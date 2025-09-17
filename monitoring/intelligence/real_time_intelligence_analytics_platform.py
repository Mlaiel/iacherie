"""Real-Time Intelligence Analytics Platform
========================================

Enterprise-grade Real-Time Intelligence Analytics system providing comprehensive
real-time monitoring, intelligent analytics, and advanced performance tracking
for the Ainflue Creator Economy. Implements sophisticated real-time algorithms,
streaming analytics, and intelligent event processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team technical training included
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import threading
from contextlib import asynccontextmanager

# Optional imports for enhanced functionality
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Mock numpy for basic operations
    np = type('MockNumpy', (), {
        'random': type('MockRandom', (), {
            'rand': lambda: __import__('random').random(),
            'choice': lambda x: __import__('random').choice(x),
            'normal': lambda mu, sigma: mu + sigma * (__import__('random').random() - 0.5) * 2,
            'mean': lambda x: sum(x) / len(x) if x else 0,
            'std': lambda x: (sum((i - sum(x)/len(x))**2 for i in x) / len(x))**0.5 if x else 0
        })(),
        'array': lambda x: list(x) if hasattr(x, '__iter__') else [x],
        'percentile': lambda x, p: sorted(x)[int(len(x) * p / 100)] if x else 0
    })()

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types of real-time events"""
    CONTENT_PUBLISHED = "content_published"
    ENGAGEMENT_RECEIVED = "engagement_received"
    FOLLOWER_GAINED = "follower_gained"
    REVENUE_GENERATED = "revenue_generated"
    COLLABORATION_STARTED = "collaboration_started"
    TIER_CHANGED = "tier_changed"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    CONTENT_VIRAL = "content_viral"
    PLATFORM_CONNECTED = "platform_connected"
    ALERT_TRIGGERED = "alert_triggered"

class MetricType(Enum):
    """Types of real-time metrics"""
    ENGAGEMENT_RATE = "engagement_rate"
    FOLLOWER_GROWTH = "follower_growth"
    CONTENT_PERFORMANCE = "content_performance"
    REVENUE_RATE = "revenue_rate"
    PLATFORM_ACTIVITY = "platform_activity"
    AUDIENCE_ACTIVITY = "audience_activity"
    COLLABORATION_RATE = "collaboration_rate"
    TIER_PROGRESSION = "tier_progression"
    SYSTEM_PERFORMANCE = "system_performance"
    ANOMALY_DETECTION = "anomaly_detection"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AnalyticsScope(Enum):
    """Analytics scope levels"""
    CREATOR = "creator"
    PLATFORM = "platform"
    GLOBAL = "global"
    CAMPAIGN = "campaign"
    COLLABORATION = "collaboration"

@dataclass
class RealTimeEvent:
    """Real-time event data structure"""
    event_id: str
    event_type: EventType
    creator_id: str
    timestamp: datetime
    platform_id: Optional[str] = None
    content_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    processing_time: Optional[float] = None

@dataclass
class RealTimeMetric:
    """Real-time metric data structure"""
    metric_id: str
    metric_type: MetricType
    scope: AnalyticsScope
    scope_id: str  # creator_id, platform_id, etc.
    value: float
    timestamp: datetime
    window_size: int = 60  # seconds
    aggregation_type: str = "average"  # average, sum, count, max, min
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RealTimeAlert:
    """Real-time alert data structure"""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    scope: AnalyticsScope
    scope_id: str
    message: str
    timestamp: datetime
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    auto_resolved: bool = False
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsDashboard:
    """Real-time analytics dashboard data"""
    dashboard_id: str
    name: str
    scope: AnalyticsScope
    scope_id: str
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    auto_refresh_interval: int = 30  # seconds
    is_active: bool = True
    subscribers: List[str] = field(default_factory=list)  # WebSocket connection IDs
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class StreamingWindow:
    """Streaming analytics window"""
    window_id: str
    metric_type: MetricType
    window_size: int  # seconds
    slide_interval: int  # seconds
    aggregation_func: str
    data_points: deque = field(default_factory=deque)
    current_value: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceSnapshot:
    """Real-time performance snapshot"""
    snapshot_id: str
    scope: AnalyticsScope
    scope_id: str
    timestamp: datetime
    metrics: Dict[str, float] = field(default_factory=dict)
    trends: Dict[str, str] = field(default_factory=dict)  # "increasing", "decreasing", "stable"
    anomalies: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    performance_score: float = 0.0

class RealTimeIntelligenceAnalyticsPlatform:
    """Enterprise Real-Time Intelligence Analytics Platform
    
    Provides comprehensive real-time analytics with intelligent monitoring,
    streaming processing, and advanced real-time insights for Creator Economy.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Real-Time Intelligence Analytics Platform
        
        Args:
            config: Configuration dictionary for analytics settings
        """
        self.config = config or {}
        self.event_stream = deque()
        self.metric_streams = defaultdict(deque)
        self.active_alerts = {}
        self.dashboards = {}
        self.streaming_windows = {}
        self.performance_snapshots = defaultdict(list)
        self.websocket_connections = {}
        self.alert_rules = {}
        self.anomaly_detectors = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Real-time processing settings
        self.processing_settings = {
            "max_events_per_second": 1000,
            "metric_retention_hours": 24,
            "alert_retention_days": 7,
            "websocket_heartbeat_interval": 30,
            "anomaly_detection_window": 300,  # 5 minutes
            "performance_snapshot_interval": 60,  # 1 minute
            "batch_processing_size": 100
        }
        
        # Threading for real-time processing
        self._processing_lock = threading.Lock()
        self._shutdown_event = threading.Event()
        
        # Initialize default alert rules
        self._initialize_default_alert_rules()
        
        # Start background processing tasks
        asyncio.create_task(self._event_processor())
        asyncio.create_task(self._metric_aggregator())
        asyncio.create_task(self._alert_monitor())
        asyncio.create_task(self._websocket_heartbeat())
        asyncio.create_task(self._performance_snapshot_generator())
        
        logger.info("Real-Time Intelligence Analytics Platform initialized successfully")
    
    def _initialize_default_alert_rules(self):
        """Initialize default alert rules for the system"""
        default_rules = [
            {
                "rule_id": "engagement_drop",
                "metric_type": MetricType.ENGAGEMENT_RATE,
                "condition": "below",
                "threshold": 0.02,
                "severity": AlertSeverity.WARNING,
                "window_minutes": 15,
                "description": "Engagement rate dropped below 2%"
            },
            {
                "rule_id": "follower_spike",
                "metric_type": MetricType.FOLLOWER_GROWTH,
                "condition": "above",
                "threshold": 100,
                "severity": AlertSeverity.INFO,
                "window_minutes": 5,
                "description": "Rapid follower growth detected"
            },
            {
                "rule_id": "revenue_surge",
                "metric_type": MetricType.REVENUE_RATE,
                "condition": "above",
                "threshold": 1000,
                "severity": AlertSeverity.INFO,
                "window_minutes": 10,
                "description": "High revenue generation detected"
            },
            {
                "rule_id": "system_overload",
                "metric_type": MetricType.SYSTEM_PERFORMANCE,
                "condition": "below",
                "threshold": 0.7,
                "severity": AlertSeverity.CRITICAL,
                "window_minutes": 1,
                "description": "System performance degraded"
            }
        ]
        
        for rule in default_rules:
            self.alert_rules[rule["rule_id"]] = rule
    
    async def ingest_event(self, event: RealTimeEvent) -> bool:
        """Ingest a real-time event into the analytics platform
        
        Args:
            event: Real-time event to process
            
        Returns:
            Success status of event ingestion
        """
        try:
            # Rate limiting check
            if len(self.event_stream) >= self.processing_settings["max_events_per_second"]:
                logger.warning("Event ingestion rate limit exceeded")
                return False
            
            # Add to event stream
            with self._processing_lock:
                self.event_stream.append(event)
            
            # Trigger immediate processing for critical events
            if event.event_type in [EventType.ALERT_TRIGGERED, EventType.CONTENT_VIRAL]:
                await self._process_single_event(event)
            
            logger.debug(f"Event ingested: {event.event_type.value} for creator {event.creator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting event: {str(e)}")
            return False
    
    async def publish_metric(self, metric: RealTimeMetric) -> bool:
        """Publish a real-time metric
        
        Args:
            metric: Real-time metric to publish
            
        Returns:
            Success status of metric publication
        """
        try:
            # Add to metric stream
            metric_key = f"{metric.scope.value}_{metric.scope_id}_{metric.metric_type.value}"
            
            with self._processing_lock:
                self.metric_streams[metric_key].append(metric)
                
                # Maintain retention limit
                retention_limit = self.processing_settings["metric_retention_hours"] * 3600  # to seconds
                cutoff_time = datetime.now() - timedelta(seconds=retention_limit)
                
                while (self.metric_streams[metric_key] and 
                       self.metric_streams[metric_key][0].timestamp < cutoff_time):
                    self.metric_streams[metric_key].popleft()
            
            # Update streaming windows
            await self._update_streaming_windows(metric)
            
            # Check alert rules
            await self._check_alert_rules(metric)
            
            # Broadcast to subscribers
            await self._broadcast_metric_update(metric)
            
            logger.debug(f"Metric published: {metric.metric_type.value} for {metric.scope.value} {metric.scope_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing metric: {str(e)}")
            return False
    
    async def _event_processor(self):
        """Background task to process real-time events"""
        while not self._shutdown_event.is_set():
            try:
                events_to_process = []
                
                # Collect events for batch processing
                with self._processing_lock:
                    batch_size = min(
                        len(self.event_stream), 
                        self.processing_settings["batch_processing_size"]
                    )
                    
                    for _ in range(batch_size):
                        if self.event_stream:
                            events_to_process.append(self.event_stream.popleft())
                
                # Process events
                if events_to_process:
                    await asyncio.gather(*[
                        self._process_single_event(event) 
                        for event in events_to_process
                    ], return_exceptions=True)
                
                await asyncio.sleep(0.1)  # Small delay to prevent CPU overload
                
            except Exception as e:
                logger.error(f"Error in event processor: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_single_event(self, event: RealTimeEvent):
        """Process a single real-time event"""
        try:
            start_time = time.time()
            
            # Extract metrics from event
            await self._extract_metrics_from_event(event)
            
            # Update dashboards
            await self._update_relevant_dashboards(event)
            
            # Anomaly detection
            await self._detect_anomalies(event)
            
            # Mark as processed
            event.processed = True
            event.processing_time = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {str(e)}")
    
    async def _extract_metrics_from_event(self, event: RealTimeEvent):
        """Extract metrics from a real-time event"""
        try:
            timestamp = event.timestamp
            
            # Extract different metrics based on event type
            if event.event_type == EventType.ENGAGEMENT_RECEIVED:
                engagement_rate = event.data.get("engagement_rate", 0.0)
                metric = RealTimeMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.ENGAGEMENT_RATE,
                    scope=AnalyticsScope.CREATOR,
                    scope_id=event.creator_id,
                    value=engagement_rate,
                    timestamp=timestamp
                )
                await self.publish_metric(metric)
                
            elif event.event_type == EventType.FOLLOWER_GAINED:
                follower_count = event.data.get("new_followers", 1)
                metric = RealTimeMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.FOLLOWER_GROWTH,
                    scope=AnalyticsScope.CREATOR,
                    scope_id=event.creator_id,
                    value=follower_count,
                    timestamp=timestamp
                )
                await self.publish_metric(metric)
                
            elif event.event_type == EventType.REVENUE_GENERATED:
                revenue_amount = event.data.get("amount", 0.0)
                metric = RealTimeMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.REVENUE_RATE,
                    scope=AnalyticsScope.CREATOR,
                    scope_id=event.creator_id,
                    value=revenue_amount,
                    timestamp=timestamp
                )
                await self.publish_metric(metric)
                
            elif event.event_type == EventType.CONTENT_PUBLISHED:
                performance_score = event.data.get("performance_score", 0.5)
                metric = RealTimeMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.CONTENT_PERFORMANCE,
                    scope=AnalyticsScope.CREATOR,
                    scope_id=event.creator_id,
                    value=performance_score,
                    timestamp=timestamp
                )
                await self.publish_metric(metric)
                
                # Platform activity metric
                if event.platform_id:
                    platform_metric = RealTimeMetric(
                        metric_id=str(uuid.uuid4()),
                        metric_type=MetricType.PLATFORM_ACTIVITY,
                        scope=AnalyticsScope.PLATFORM,
                        scope_id=event.platform_id,
                        value=1.0,  # Activity count
                        timestamp=timestamp,
                        aggregation_type="sum"
                    )
                    await self.publish_metric(platform_metric)
            
        except Exception as e:
            logger.error(f"Error extracting metrics from event: {str(e)}")
    
    async def _update_streaming_windows(self, metric: RealTimeMetric):
        """Update streaming analytics windows with new metric"""
        try:
            window_key = f"{metric.scope.value}_{metric.scope_id}_{metric.metric_type.value}"
            
            if window_key not in self.streaming_windows:
                self.streaming_windows[window_key] = StreamingWindow(
                    window_id=window_key,
                    metric_type=metric.metric_type,
                    window_size=300,  # 5 minutes default
                    slide_interval=30,  # 30 seconds slide
                    aggregation_func=metric.aggregation_type,
                    data_points=deque()
                )
            
            window = self.streaming_windows[window_key]
            
            # Add new data point
            window.data_points.append((metric.timestamp, metric.value))
            
            # Remove old data points outside window
            cutoff_time = datetime.now() - timedelta(seconds=window.window_size)
            while (window.data_points and 
                   window.data_points[0][0] < cutoff_time):
                window.data_points.popleft()
            
            # Calculate current aggregated value
            if window.data_points:
                values = [point[1] for point in window.data_points]
                
                if window.aggregation_func == "average":
                    window.current_value = np.mean(values) if NUMPY_AVAILABLE else sum(values) / len(values)
                elif window.aggregation_func == "sum":
                    window.current_value = sum(values)
                elif window.aggregation_func == "count":
                    window.current_value = len(values)
                elif window.aggregation_func == "max":
                    window.current_value = max(values)
                elif window.aggregation_func == "min":
                    window.current_value = min(values)
                else:
                    window.current_value = values[-1]  # Latest value
            
            window.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating streaming windows: {str(e)}")
    
    async def _check_alert_rules(self, metric: RealTimeMetric):
        """Check alert rules against new metric"""
        try:
            for rule_id, rule in self.alert_rules.items():
                if rule["metric_type"] != metric.metric_type:
                    continue
                
                threshold = rule["threshold"]
                condition = rule["condition"]
                
                should_alert = False
                
                if condition == "above" and metric.value > threshold:
                    should_alert = True
                elif condition == "below" and metric.value < threshold:
                    should_alert = True
                elif condition == "equals" and abs(metric.value - threshold) < 0.001:
                    should_alert = True
                
                if should_alert:
                    alert = RealTimeAlert(
                        alert_id=str(uuid.uuid4()),
                        alert_type=rule_id,
                        severity=AlertSeverity(rule["severity"]),
                        scope=metric.scope,
                        scope_id=metric.scope_id,
                        message=rule["description"],
                        timestamp=datetime.now(),
                        threshold_value=threshold,
                        current_value=metric.value
                    )
                    
                    await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking alert rules: {str(e)}")
    
    async def _trigger_alert(self, alert: RealTimeAlert):
        """Trigger a real-time alert"""
        try:
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            
            # Clean old alerts
            retention_days = self.processing_settings["alert_retention_days"]
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            alerts_to_remove = [
                alert_id for alert_id, stored_alert in self.active_alerts.items()
                if stored_alert.timestamp < cutoff_time
            ]
            
            for alert_id in alerts_to_remove:
                del self.active_alerts[alert_id]
            
            # Broadcast alert
            await self._broadcast_alert(alert)
            
            logger.warning(f"Alert triggered: {alert.alert_type} ({alert.severity.value}) for {alert.scope.value} {alert.scope_id}")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {str(e)}")
    
    async def _update_relevant_dashboards(self, event: RealTimeEvent):
        """Update dashboards that are relevant to the event"""
        try:
            for dashboard in self.dashboards.values():
                if not dashboard.is_active:
                    continue
                
                # Check if dashboard is relevant to event
                is_relevant = False
                
                if dashboard.scope == AnalyticsScope.CREATOR and dashboard.scope_id == event.creator_id:
                    is_relevant = True
                elif dashboard.scope == AnalyticsScope.PLATFORM and dashboard.scope_id == event.platform_id:
                    is_relevant = True
                elif dashboard.scope == AnalyticsScope.GLOBAL:
                    is_relevant = True
                
                if is_relevant:
                    dashboard.last_updated = datetime.now()
                    await self._broadcast_dashboard_update(dashboard)
            
        except Exception as e:
            logger.error(f"Error updating dashboards: {str(e)}")
    
    async def _detect_anomalies(self, event: RealTimeEvent):
        """Detect anomalies in real-time events"""
        try:
            # Simple anomaly detection based on statistical thresholds
            # In production, this would use more sophisticated ML models
            
            if event.event_type == EventType.ENGAGEMENT_RECEIVED:
                engagement_rate = event.data.get("engagement_rate", 0.0)
                
                # Get historical engagement rates for this creator
                metric_key = f"creator_{event.creator_id}_engagement_rate"
                if metric_key in self.metric_streams:
                    recent_metrics = list(self.metric_streams[metric_key])[-100:]  # Last 100 metrics
                    
                    if len(recent_metrics) >= 10:
                        values = [m.value for m in recent_metrics]
                        mean_val = np.mean(values) if NUMPY_AVAILABLE else sum(values) / len(values)
                        std_val = np.std(values) if NUMPY_AVAILABLE else 0
                        
                        # Check if current value is an outlier (> 3 standard deviations)
                        if std_val > 0 and abs(engagement_rate - mean_val) > 3 * std_val:
                            await self._trigger_anomaly_alert(event, "engagement_rate_anomaly", engagement_rate, mean_val)
            
            elif event.event_type == EventType.FOLLOWER_GAINED:
                new_followers = event.data.get("new_followers", 1)
                
                # Detect unusual follower spikes
                if new_followers > 1000:  # Threshold for spike detection
                    await self._trigger_anomaly_alert(event, "follower_spike", new_followers, 0)
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
    
    async def _trigger_anomaly_alert(self, event: RealTimeEvent, anomaly_type: str, current_value: float, expected_value: float):
        """Trigger an anomaly alert"""
        try:
            alert = RealTimeAlert(
                alert_id=str(uuid.uuid4()),
                alert_type=f"anomaly_{anomaly_type}",
                severity=AlertSeverity.WARNING,
                scope=AnalyticsScope.CREATOR,
                scope_id=event.creator_id,
                message=f"Anomaly detected: {anomaly_type} - expected {expected_value:.2f}, got {current_value:.2f}",
                timestamp=datetime.now(),
                threshold_value=expected_value,
                current_value=current_value
            )
            
            await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error triggering anomaly alert: {str(e)}")
    
    async def _metric_aggregator(self):
        """Background task to aggregate metrics"""
        while not self._shutdown_event.is_set():
            try:
                # Aggregate metrics for different time windows
                await self._aggregate_metrics_by_window()
                await asyncio.sleep(30)  # Aggregate every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in metric aggregator: {str(e)}")
                await asyncio.sleep(60)
    
    async def _aggregate_metrics_by_window(self):
        """Aggregate metrics by different time windows"""
        try:
            windows = [60, 300, 900, 3600]  # 1min, 5min, 15min, 1hour
            
            for window_seconds in windows:
                cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
                
                # Group metrics by scope and type
                aggregated_metrics = defaultdict(list)
                
                for metric_key, metric_stream in self.metric_streams.items():
                    recent_metrics = [
                        m for m in metric_stream 
                        if m.timestamp >= cutoff_time
                    ]
                    
                    if recent_metrics:
                        # Calculate aggregated values
                        values = [m.value for m in recent_metrics]
                        
                        aggregated_data = {
                            "count": len(values),
                            "sum": sum(values),
                            "average": np.mean(values) if NUMPY_AVAILABLE else sum(values) / len(values),
                            "min": min(values),
                            "max": max(values),
                            "latest": values[-1],
                            "window_seconds": window_seconds
                        }
                        
                        aggregated_metrics[metric_key].append(aggregated_data)
                
                # Store aggregated metrics for dashboard consumption
                # This would typically be stored in a time-series database
                
        except Exception as e:
            logger.error(f"Error aggregating metrics: {str(e)}")
    
    async def _alert_monitor(self):
        """Background task to monitor and manage alerts"""
        while not self._shutdown_event.is_set():
            try:
                # Auto-resolve alerts that no longer meet conditions
                await self._auto_resolve_alerts()
                
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in alert monitor: {str(e)}")
                await asyncio.sleep(300)
    
    async def _auto_resolve_alerts(self):
        """Auto-resolve alerts that no longer meet trigger conditions"""
        try:
            for alert_id, alert in list(self.active_alerts.items()):
                if alert.auto_resolved or alert.acknowledged:
                    continue
                
                # Check if alert condition is still met
                should_resolve = await self._should_auto_resolve_alert(alert)
                
                if should_resolve:
                    alert.auto_resolved = True
                    await self._broadcast_alert_resolution(alert)
                    logger.info(f"Auto-resolved alert: {alert.alert_type}")
            
        except Exception as e:
            logger.error(f"Error auto-resolving alerts: {str(e)}")
    
    async def _should_auto_resolve_alert(self, alert: RealTimeAlert) -> bool:
        """Check if an alert should be auto-resolved"""
        try:
            # Get recent metrics for the alert scope
            metric_key = f"{alert.scope.value}_{alert.scope_id}_{alert.alert_type}"
            
            if metric_key in self.streaming_windows:
                window = self.streaming_windows[metric_key]
                current_value = window.current_value
                
                if current_value is not None and alert.threshold_value is not None:
                    # Check if condition is no longer met
                    rule = self.alert_rules.get(alert.alert_type)
                    if rule:
                        condition = rule["condition"]
                        threshold = alert.threshold_value
                        
                        if condition == "above" and current_value <= threshold:
                            return True
                        elif condition == "below" and current_value >= threshold:
                            return True
                        elif condition == "equals" and abs(current_value - threshold) >= 0.001:
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert resolution: {str(e)}")
            return False
    
    async def _cleanup_old_alerts(self):
        """Clean up old alerts"""
        try:
            retention_days = self.processing_settings["alert_retention_days"]
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            alerts_to_remove = [
                alert_id for alert_id, alert in self.active_alerts.items()
                if alert.timestamp < cutoff_time
            ]
            
            for alert_id in alerts_to_remove:
                del self.active_alerts[alert_id]
            
            if alerts_to_remove:
                logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")
            
        except Exception as e:
            logger.error(f"Error cleaning up alerts: {str(e)}")
    
    async def _websocket_heartbeat(self):
        """Send heartbeat to WebSocket connections"""
        if not WEBSOCKETS_AVAILABLE:
            return
            
        while not self._shutdown_event.is_set():
            try:
                # Send heartbeat to all active connections
                heartbeat_message = {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "server_status": "healthy"
                }
                
                await self._broadcast_to_all_connections(heartbeat_message)
                
                await asyncio.sleep(self.processing_settings["websocket_heartbeat_interval"])
                
            except Exception as e:
                logger.error(f"Error in websocket heartbeat: {str(e)}")
                await asyncio.sleep(60)
    
    async def _performance_snapshot_generator(self):
        """Generate performance snapshots periodically"""
        while not self._shutdown_event.is_set():
            try:
                await self._generate_performance_snapshots()
                await asyncio.sleep(self.processing_settings["performance_snapshot_interval"])
                
            except Exception as e:
                logger.error(f"Error generating performance snapshots: {str(e)}")
                await asyncio.sleep(300)
    
    async def _generate_performance_snapshots(self):
        """Generate performance snapshots for all scopes"""
        try:
            # Generate snapshots for different scopes
            scopes_to_snapshot = set()
            
            # Collect all unique scopes from streaming windows
            for window_key, window in self.streaming_windows.items():
                scope_parts = window_key.split('_')
                if len(scope_parts) >= 3:
                    scope = scope_parts[0]
                    scope_id = scope_parts[1]
                    scopes_to_snapshot.add((scope, scope_id))
            
            # Generate snapshots
            for scope_str, scope_id in scopes_to_snapshot:
                try:
                    scope = AnalyticsScope(scope_str)
                    snapshot = await self._create_performance_snapshot(scope, scope_id)
                    
                    if snapshot:
                        # Store snapshot
                        snapshot_key = f"{scope.value}_{scope_id}"
                        self.performance_snapshots[snapshot_key].append(snapshot)
                        
                        # Keep only recent snapshots (last 24 hours)
                        cutoff_time = datetime.now() - timedelta(hours=24)
                        self.performance_snapshots[snapshot_key] = [
                            s for s in self.performance_snapshots[snapshot_key]
                            if s.timestamp >= cutoff_time
                        ]
                        
                except ValueError:
                    # Invalid scope value
                    continue
            
        except Exception as e:
            logger.error(f"Error generating performance snapshots: {str(e)}")
    
    async def _create_performance_snapshot(self, scope: AnalyticsScope, scope_id: str) -> Optional[PerformanceSnapshot]:
        """Create a performance snapshot for a specific scope"""
        try:
            metrics = {}
            trends = {}
            anomalies = []
            active_alerts = []
            
            # Collect metrics for this scope
            for window_key, window in self.streaming_windows.items():
                if window_key.startswith(f"{scope.value}_{scope_id}_"):
                    metric_type = window.metric_type.value
                    metrics[metric_type] = window.current_value or 0.0
                    
                    # Determine trend (simplified)
                    if len(window.data_points) >= 2:
                        recent_values = [point[1] for point in list(window.data_points)[-10:]]
                        first_half = recent_values[:len(recent_values)//2]
                        second_half = recent_values[len(recent_values)//2:]
                        
                        if first_half and second_half:
                            first_avg = sum(first_half) / len(first_half)
                            second_avg = sum(second_half) / len(second_half)
                            
                            if second_avg > first_avg * 1.1:
                                trends[metric_type] = "increasing"
                            elif second_avg < first_avg * 0.9:
                                trends[metric_type] = "decreasing"
                            else:
                                trends[metric_type] = "stable"
            
            # Find alerts for this scope
            for alert in self.active_alerts.values():
                if alert.scope == scope and alert.scope_id == scope_id and not alert.auto_resolved:
                    active_alerts.append(alert.alert_id)
            
            # Calculate performance score
            performance_score = await self._calculate_performance_score(scope, scope_id, metrics, trends, active_alerts)
            
            snapshot = PerformanceSnapshot(
                snapshot_id=str(uuid.uuid4()),
                scope=scope,
                scope_id=scope_id,
                timestamp=datetime.now(),
                metrics=metrics,
                trends=trends,
                anomalies=anomalies,
                alerts=active_alerts,
                performance_score=performance_score
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error creating performance snapshot: {str(e)}")
            return None
    
    async def _calculate_performance_score(
        self, 
        scope: AnalyticsScope, 
        scope_id: str, 
        metrics: Dict[str, float],
        trends: Dict[str, str],
        active_alerts: List[str]
    ) -> float:
        """Calculate performance score based on metrics and trends"""
        try:
            base_score = 50.0  # Base score
            
            # Positive metrics
            if "engagement_rate" in metrics:
                engagement_score = min(30, metrics["engagement_rate"] * 1000)  # Scale up
                base_score += engagement_score
            
            if "follower_growth" in metrics:
                growth_score = min(20, metrics["follower_growth"] / 10)
                base_score += growth_score
            
            # Trend bonuses
            positive_trends = len([t for t in trends.values() if t == "increasing"])
            negative_trends = len([t for t in trends.values() if t == "decreasing"])
            
            base_score += positive_trends * 5
            base_score -= negative_trends * 3
            
            # Alert penalties
            critical_alerts = len([a for a in active_alerts if "critical" in a.lower()])
            warning_alerts = len([a for a in active_alerts if "warning" in a.lower()])
            
            base_score -= critical_alerts * 15
            base_score -= warning_alerts * 5
            
            # Normalize to 0-100 scale
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 50.0
    
    async def _broadcast_metric_update(self, metric: RealTimeMetric):
        """Broadcast metric update to subscribers"""
        try:
            message = {
                "type": "metric_update",
                "metric": {
                    "metric_type": metric.metric_type.value,
                    "scope": metric.scope.value,
                    "scope_id": metric.scope_id,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat()
                }
            }
            
            await self._broadcast_to_relevant_connections(message, metric.scope, metric.scope_id)
            
        except Exception as e:
            logger.error(f"Error broadcasting metric update: {str(e)}")
    
    async def _broadcast_alert(self, alert: RealTimeAlert):
        """Broadcast alert to subscribers"""
        try:
            message = {
                "type": "alert",
                "alert": {
                    "alert_id": alert.alert_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity.value,
                    "scope": alert.scope.value,
                    "scope_id": alert.scope_id,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "current_value": alert.current_value,
                    "threshold_value": alert.threshold_value
                }
            }
            
            await self._broadcast_to_relevant_connections(message, alert.scope, alert.scope_id)
            
        except Exception as e:
            logger.error(f"Error broadcasting alert: {str(e)}")
    
    async def _broadcast_alert_resolution(self, alert: RealTimeAlert):
        """Broadcast alert resolution to subscribers"""
        try:
            message = {
                "type": "alert_resolved",
                "alert_id": alert.alert_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await self._broadcast_to_relevant_connections(message, alert.scope, alert.scope_id)
            
        except Exception as e:
            logger.error(f"Error broadcasting alert resolution: {str(e)}")
    
    async def _broadcast_dashboard_update(self, dashboard: AnalyticsDashboard):
        """Broadcast dashboard update to subscribers"""
        try:
            message = {
                "type": "dashboard_update",
                "dashboard_id": dashboard.dashboard_id,
                "last_updated": dashboard.last_updated.isoformat()
            }
            
            # Broadcast to dashboard subscribers
            for subscriber_id in dashboard.subscribers:
                if subscriber_id in self.websocket_connections:
                    # In a real implementation, send via WebSocket
                    pass
            
        except Exception as e:
            logger.error(f"Error broadcasting dashboard update: {str(e)}")
    
    async def _broadcast_to_relevant_connections(self, message: Dict[str, Any], scope: AnalyticsScope, scope_id: str):
        """Broadcast message to relevant WebSocket connections"""
        try:
            # In a real implementation, this would send via WebSocket to connections
            # that are subscribed to the specific scope and scope_id
            pass
            
        except Exception as e:
            logger.error(f"Error broadcasting to connections: {str(e)}")
    
    async def _broadcast_to_all_connections(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket connections"""
        try:
            # In a real implementation, this would send via WebSocket to all connections
            pass
            
        except Exception as e:
            logger.error(f"Error broadcasting to all connections: {str(e)}")
    
    async def get_real_time_metrics(
        self, 
        scope: AnalyticsScope, 
        scope_id: str,
        metric_types: Optional[List[MetricType]] = None,
        window_seconds: int = 300
    ) -> Dict[str, Any]:
        """Get real-time metrics for a specific scope
        
        Args:
            scope: Analytics scope
            scope_id: Scope identifier
            metric_types: Optional list of metric types to filter
            window_seconds: Time window for metrics
            
        Returns:
            Real-time metrics data
        """
        try:
            cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
            metrics_data = {}
            
            # Filter metric types
            target_metric_types = metric_types or list(MetricType)
            
            for metric_type in target_metric_types:
                metric_key = f"{scope.value}_{scope_id}_{metric_type.value}"
                
                if metric_key in self.streaming_windows:
                    window = self.streaming_windows[metric_key]
                    
                    # Get data points within window
                    recent_points = [
                        {"timestamp": point[0].isoformat(), "value": point[1]}
                        for point in window.data_points
                        if point[0] >= cutoff_time
                    ]
                    
                    metrics_data[metric_type.value] = {
                        "current_value": window.current_value,
                        "data_points": recent_points,
                        "aggregation_type": window.aggregation_func,
                        "last_updated": window.last_updated.isoformat()
                    }
            
            return {
                "scope": scope.value,
                "scope_id": scope_id,
                "window_seconds": window_seconds,
                "metrics": metrics_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {str(e)}")
            return {}
    
    async def get_active_alerts(
        self, 
        scope: Optional[AnalyticsScope] = None,
        scope_id: Optional[str] = None,
        severity: Optional[AlertSeverity] = None
    ) -> List[Dict[str, Any]]:
        """Get active alerts with optional filtering
        
        Args:
            scope: Optional scope filter
            scope_id: Optional scope ID filter
            severity: Optional severity filter
            
        Returns:
            List of active alerts
        """
        try:
            alerts = []
            
            for alert in self.active_alerts.values():
                if alert.auto_resolved or alert.acknowledged:
                    continue
                
                # Apply filters
                if scope and alert.scope != scope:
                    continue
                if scope_id and alert.scope_id != scope_id:
                    continue
                if severity and alert.severity != severity:
                    continue
                
                alerts.append({
                    "alert_id": alert.alert_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity.value,
                    "scope": alert.scope.value,
                    "scope_id": alert.scope_id,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "current_value": alert.current_value,
                    "threshold_value": alert.threshold_value,
                    "auto_resolved": alert.auto_resolved,
                    "acknowledged": alert.acknowledged
                })
            
            # Sort by severity and timestamp
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.ERROR: 1,
                AlertSeverity.WARNING: 2,
                AlertSeverity.INFO: 3
            }
            
            alerts.sort(key=lambda x: (
                severity_order.get(AlertSeverity(x["severity"]), 4),
                x["timestamp"]
            ), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {str(e)}")
            return []
    
    async def get_performance_snapshot(self, scope: AnalyticsScope, scope_id: str) -> Optional[Dict[str, Any]]:
        """Get latest performance snapshot for a scope
        
        Args:
            scope: Analytics scope
            scope_id: Scope identifier
            
        Returns:
            Performance snapshot data
        """
        try:
            snapshot_key = f"{scope.value}_{scope_id}"
            
            if snapshot_key in self.performance_snapshots:
                snapshots = self.performance_snapshots[snapshot_key]
                
                if snapshots:
                    # Get latest snapshot
                    latest_snapshot = max(snapshots, key=lambda s: s.timestamp)
                    
                    return {
                        "snapshot_id": latest_snapshot.snapshot_id,
                        "scope": latest_snapshot.scope.value,
                        "scope_id": latest_snapshot.scope_id,
                        "timestamp": latest_snapshot.timestamp.isoformat(),
                        "metrics": latest_snapshot.metrics,
                        "trends": latest_snapshot.trends,
                        "anomalies": latest_snapshot.anomalies,
                        "alerts": latest_snapshot.alerts,
                        "performance_score": latest_snapshot.performance_score
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting performance snapshot: {str(e)}")
            return None
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and performance metrics
        
        Returns:
            System health information
        """
        try:
            # Calculate processing statistics
            total_events = len(self.event_stream)
            total_metrics = sum(len(stream) for stream in self.metric_streams.values())
            active_alerts_count = len([a for a in self.active_alerts.values() if not a.auto_resolved])
            
            # System performance metrics
            event_processing_rate = 0  # Would be calculated from actual processing
            metric_ingestion_rate = 0  # Would be calculated from actual ingestion
            
            return {
                "system_status": "operational",
                "event_processing": {
                    "events_in_queue": total_events,
                    "processing_rate_per_second": event_processing_rate,
                    "max_events_per_second": self.processing_settings["max_events_per_second"]
                },
                "metric_processing": {
                    "total_metric_streams": len(self.metric_streams),
                    "total_metrics": total_metrics,
                    "ingestion_rate_per_second": metric_ingestion_rate,
                    "streaming_windows_active": len(self.streaming_windows)
                },
                "alerting": {
                    "active_alerts": active_alerts_count,
                    "total_alerts": len(self.active_alerts),
                    "alert_rules": len(self.alert_rules),
                    "auto_resolution_enabled": True
                },
                "dashboards": {
                    "total_dashboards": len(self.dashboards),
                    "active_dashboards": len([d for d in self.dashboards.values() if d.is_active]),
                    "websocket_connections": len(self.websocket_connections)
                },
                "performance": {
                    "performance_snapshots": sum(len(snapshots) for snapshots in self.performance_snapshots.values()),
                    "anomaly_detectors": len(self.anomaly_detectors),
                    "system_uptime": "operational"
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def shutdown(self):
        """Shutdown the analytics platform"""
        self._shutdown_event.set()
        self.executor.shutdown(wait=True)
        logger.info("Real-Time Intelligence Analytics Platform shutdown completed")

# Export main class and types
__all__ = [
    'RealTimeIntelligenceAnalyticsPlatform',
    'EventType',
    'MetricType',
    'AlertSeverity',
    'AnalyticsScope',
    'RealTimeEvent',
    'RealTimeMetric',
    'RealTimeAlert',
    'AnalyticsDashboard',
    'StreamingWindow',
    'PerformanceSnapshot'
]