#!/usr/bin/env python3
"""
IA Chéries Platform - Real-Time Monitoring Dispatcher
================================================

Enterprise-grade real-time monitoring dispatcher for Creator Economy platform.
Processes real-time data streams, monitors creator activity live, dispatches instant alerts,
streams performance metrics, and coordinates live dashboard data.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import uuid

# Optional websockets import
try:
    import websockets
except ImportError:
    websockets = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Real-time event types"""
    CREATOR_ACTIVITY = "creator_activity"
    CONTENT_UPLOAD = "content_upload"
    ENGAGEMENT_SPIKE = "engagement_spike"
    REVENUE_EVENT = "revenue_event"
    COLLABORATION_UPDATE = "collaboration_update"
    ALERT_TRIGGER = "alert_trigger"
    SYSTEM_PERFORMANCE = "system_performance"
    USER_INTERACTION = "user_interaction"

class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class StreamType(Enum):
    """Data stream types"""
    METRICS_STREAM = "metrics_stream"
    ACTIVITY_STREAM = "activity_stream"
    ALERT_STREAM = "alert_stream"
    DASHBOARD_STREAM = "dashboard_stream"
    ANALYTICS_STREAM = "analytics_stream"

@dataclass
class RealTimeEvent:
    """Real-time event data structure"""
    event_id: str
    event_type: EventType
    creator_id: Optional[str]
    content_id: Optional[str]
    timestamp: datetime
    data: Dict[str, Any]
    priority: AlertPriority = AlertPriority.INFO
    processed: bool = False
    processing_latency_ms: Optional[float] = None

@dataclass
class AlertDispatch:
    """Alert dispatch configuration and tracking"""
    alert_id: str
    alert_type: str
    priority: AlertPriority
    recipients: List[str]
    channels: List[str]
    dispatch_time: datetime
    delivery_confirmations: Dict[str, bool] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class StreamMetrics:
    """Stream performance metrics"""
    stream_type: StreamType
    messages_per_second: float
    average_latency_ms: float
    error_rate: float
    active_subscribers: int
    data_throughput_bytes: int
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class CreatorActivityEvent:
    """Creator real-time activity event"""
    creator_id: str
    activity_type: str
    content_id: Optional[str]
    platform: Optional[str]
    metrics: Dict[str, Any]
    geolocation: Optional[Dict[str, str]]
    device_info: Optional[Dict[str, str]]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class RealTimeMonitoringDispatcher:
    """
    Enterprise real-time monitoring dispatcher for Creator Economy platform.
    
    Capabilities:
    - Real-time data stream processing
    - Creator activity monitoring live
    - Instant alert dispatching
    - Performance metrics streaming
    - Live dashboard data coordination
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.event_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self.alert_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.stream_subscribers: Dict[StreamType, Set[str]] = defaultdict(set)
        self.websocket_connections: Dict[str, Any] = {}
        self.stream_metrics: Dict[StreamType, StreamMetrics] = {}
        self.processing_active = False
        
        # Initialize real-time monitoring systems
        self._initialize_event_processing()
        self._initialize_alert_dispatching()
        self._initialize_stream_management()
        self._initialize_performance_tracking()
        
        logger.info("RealTimeMonitoringDispatcher initialized successfully")
    
    def _initialize_event_processing(self):
        """Initialize real-time event processing systems."""
        self.event_processors = {
            EventType.CREATOR_ACTIVITY: self._process_creator_activity_event,
            EventType.CONTENT_UPLOAD: self._process_content_upload_event,
            EventType.ENGAGEMENT_SPIKE: self._process_engagement_spike_event,
            EventType.REVENUE_EVENT: self._process_revenue_event,
            EventType.COLLABORATION_UPDATE: self._process_collaboration_event,
            EventType.SYSTEM_PERFORMANCE: self._process_system_performance_event,
            EventType.USER_INTERACTION: self._process_user_interaction_event
        }
        
        self.event_routing_rules = {
            EventType.CREATOR_ACTIVITY: [StreamType.ACTIVITY_STREAM, StreamType.DASHBOARD_STREAM],
            EventType.ENGAGEMENT_SPIKE: [StreamType.METRICS_STREAM, StreamType.ALERT_STREAM],
            EventType.REVENUE_EVENT: [StreamType.ANALYTICS_STREAM, StreamType.DASHBOARD_STREAM],
            EventType.ALERT_TRIGGER: [StreamType.ALERT_STREAM],
            EventType.SYSTEM_PERFORMANCE: [StreamType.METRICS_STREAM]
        }
        
        self.processing_stats = {
            "events_processed": 0,
            "events_per_second": 0.0,
            "average_processing_time_ms": 0.0,
            "error_count": 0,
            "queue_depth": 0
        }
    
    def _initialize_alert_dispatching(self):
        """Initialize alert dispatching systems."""
        self.alert_channels = {
            "websocket": self._send_websocket_alert,
            "email": self._send_email_alert,
            "sms": self._send_sms_alert,
            "push": self._send_push_notification,
            "slack": self._send_slack_alert,
            "dashboard": self._send_dashboard_alert
        }
        
        self.alert_routing = {
            AlertPriority.CRITICAL: ["websocket", "email", "sms", "push", "slack"],
            AlertPriority.HIGH: ["websocket", "email", "push", "slack"],
            AlertPriority.MEDIUM: ["websocket", "push"],
            AlertPriority.LOW: ["websocket"],
            AlertPriority.INFO: ["dashboard"]
        }
        
        self.alert_throttling = {
            "max_alerts_per_minute": 60,
            "duplicate_suppression_window_minutes": 5,
            "escalation_thresholds": {
                AlertPriority.MEDIUM: {"count": 10, "window_minutes": 10},
                AlertPriority.HIGH: {"count": 5, "window_minutes": 5}
            }
        }
        
        self.recent_alerts: deque = deque(maxlen=1000)
        self.alert_counts: Dict[str, int] = defaultdict(int)
    
    def _initialize_stream_management(self):
        """Initialize data stream management."""
        self.stream_configs = {
            StreamType.METRICS_STREAM: {
                "buffer_size": 1000,
                "batch_size": 50,
                "flush_interval_ms": 1000,
                "compression": True
            },
            StreamType.ACTIVITY_STREAM: {
                "buffer_size": 2000,
                "batch_size": 100,
                "flush_interval_ms": 500,
                "compression": False
            },
            StreamType.ALERT_STREAM: {
                "buffer_size": 500,
                "batch_size": 10,
                "flush_interval_ms": 100,
                "compression": False
            },
            StreamType.DASHBOARD_STREAM: {
                "buffer_size": 1000,
                "batch_size": 20,
                "flush_interval_ms": 2000,
                "compression": True
            }
        }
        
        self.stream_buffers: Dict[StreamType, deque] = {
            stream_type: deque(maxlen=config["buffer_size"])
            for stream_type, config in self.stream_configs.items()
        }
        
        # Initialize stream metrics
        for stream_type in StreamType:
            self.stream_metrics[stream_type] = StreamMetrics(
                stream_type=stream_type,
                messages_per_second=0.0,
                average_latency_ms=0.0,
                error_rate=0.0,
                active_subscribers=0,
                data_throughput_bytes=0
            )
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking systems."""
        self.performance_thresholds = {
            "max_processing_latency_ms": 100,
            "max_queue_depth": 5000,
            "max_error_rate": 0.01,
            "min_throughput_events_per_second": 100
        }
        
        self.performance_history: deque = deque(maxlen=3600)  # 1 hour of data
        self.circuit_breakers: Dict[str, Dict] = {}
    
    async def start_processing(self):
        """Start real-time monitoring and dispatching."""
        if self.processing_active:
            logger.warning("Real-time processing already active")
            return
        
        self.processing_active = True
        logger.info("Starting real-time monitoring dispatcher...")
        
        # Start processing tasks
        tasks = [
            asyncio.create_task(self._process_event_queue()),
            asyncio.create_task(self._dispatch_alerts()),
            asyncio.create_task(self._manage_data_streams()),
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._flush_stream_buffers()),
            asyncio.create_task(self._cleanup_old_data())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in real-time processing: {e}")
            self.processing_active = False
            raise
    
    async def stop_processing(self):
        """Stop real-time monitoring and dispatching."""
        self.processing_active = False
        logger.info("Real-time monitoring dispatcher stopped")
    
    async def publish_event(self, event_data: Dict[str, Any]) -> str:
        """Publish real-time event to processing queue."""
        event_id = str(uuid.uuid4())
        
        event = RealTimeEvent(
            event_id=event_id,
            event_type=EventType(event_data.get('type', 'user_interaction')),
            creator_id=event_data.get('creator_id'),
            content_id=event_data.get('content_id'),
            timestamp=datetime.now(timezone.utc),
            data=event_data.get('data', {}),
            priority=AlertPriority(event_data.get('priority', 'info'))
        )
        
        try:
            await self.event_queue.put(event)
            logger.debug(f"Published event {event_id} to queue")
            return event_id
        except asyncio.QueueFull:
            logger.error(f"Event queue full, dropping event {event_id}")
            await self._trigger_system_alert("queue_overflow", {"event_id": event_id})
            return event_id
    
    async def dispatch_alert(self, alert_data: Dict[str, Any]) -> str:
        """Dispatch immediate alert."""
        alert_id = str(uuid.uuid4())
        
        alert = AlertDispatch(
            alert_id=alert_id,
            alert_type=alert_data.get('type', 'system_alert'),
            priority=AlertPriority(alert_data.get('priority', 'medium')),
            recipients=alert_data.get('recipients', []),
            channels=alert_data.get('channels', []),
            dispatch_time=datetime.now(timezone.utc)
        )
        
        try:
            await self.alert_queue.put(alert)
            logger.info(f"Dispatched alert {alert_id}")
            return alert_id
        except asyncio.QueueFull:
            logger.error(f"Alert queue full, dropping alert {alert_id}")
            return alert_id
    
    async def subscribe_to_stream(self, stream_type: StreamType, subscriber_id: str, websocket: Optional[Any] = None):
        """Subscribe to real-time data stream."""
        self.stream_subscribers[stream_type].add(subscriber_id)
        
        if websocket:
            self.websocket_connections[subscriber_id] = websocket
        
        # Update subscriber count in metrics
        self.stream_metrics[stream_type].active_subscribers = len(self.stream_subscribers[stream_type])
        
        logger.info(f"Subscriber {subscriber_id} subscribed to {stream_type.value}")
    
    async def unsubscribe_from_stream(self, stream_type: StreamType, subscriber_id: str):
        """Unsubscribe from real-time data stream."""
        self.stream_subscribers[stream_type].discard(subscriber_id)
        
        if subscriber_id in self.websocket_connections:
            del self.websocket_connections[subscriber_id]
        
        # Update subscriber count in metrics
        self.stream_metrics[stream_type].active_subscribers = len(self.stream_subscribers[stream_type])
        
        logger.info(f"Subscriber {subscriber_id} unsubscribed from {stream_type.value}")
    
    async def _process_event_queue(self):
        """Process events from the real-time queue."""
        while self.processing_active:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                start_time = time.time()
                
                # Process event based on type
                processor = self.event_processors.get(event.event_type)
                if processor:
                    await processor(event)
                else:
                    await self._process_generic_event(event)
                
                # Calculate processing latency
                processing_time = (time.time() - start_time) * 1000
                event.processing_latency_ms = processing_time
                event.processed = True
                
                # Route event to appropriate streams
                await self._route_event_to_streams(event)
                
                # Update processing stats
                self.processing_stats["events_processed"] += 1
                
                # Mark task as done
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self.processing_stats["error_count"] += 1
    
    async def _dispatch_alerts(self):
        """Dispatch alerts from the alert queue."""
        while self.processing_active:
            try:
                # Get alert from queue with timeout
                alert = await asyncio.wait_for(self.alert_queue.get(), timeout=1.0)
                
                # Check alert throttling
                if await self._should_throttle_alert(alert):
                    logger.info(f"Alert {alert.alert_id} throttled")
                    continue
                
                # Determine channels based on priority
                channels = alert.channels or self.alert_routing.get(alert.priority, ["websocket"])
                
                # Dispatch to each channel
                for channel in channels:
                    handler = self.alert_channels.get(channel)
                    if handler:
                        try:
                            success = await handler(alert)
                            alert.delivery_confirmations[channel] = success
                        except Exception as e:
                            logger.error(f"Failed to send alert via {channel}: {e}")
                            alert.delivery_confirmations[channel] = False
                
                # Store alert for tracking
                self.recent_alerts.append(alert)
                
                # Mark task as done
                self.alert_queue.task_done()
                
            except asyncio.TimeoutError:
                # No alerts in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error dispatching alert: {e}")
    
    async def _manage_data_streams(self):
        """Manage real-time data streams."""
        while self.processing_active:
            try:
                # Update stream metrics
                for stream_type, metrics in self.stream_metrics.items():
                    buffer = self.stream_buffers[stream_type]
                    
                    # Calculate messages per second
                    current_time = time.time()
                    recent_messages = len([msg for msg in buffer 
                                         if msg.get('timestamp', 0) > current_time - 1])
                    metrics.messages_per_second = recent_messages
                    
                    # Update last updated time
                    metrics.last_updated = datetime.now(timezone.utc)
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Error managing data streams: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_performance(self):
        """Monitor real-time processing performance."""
        while self.processing_active:
            try:
                # Calculate performance metrics
                queue_depth = self.event_queue.qsize()
                self.processing_stats["queue_depth"] = queue_depth
                
                # Check performance thresholds
                if queue_depth > self.performance_thresholds["max_queue_depth"]:
                    await self._trigger_performance_alert("high_queue_depth", queue_depth)
                
                # Calculate events per second
                current_time = time.time()
                if hasattr(self, '_last_performance_check'):
                    time_diff = current_time - self._last_performance_check
                    events_diff = self.processing_stats["events_processed"] - getattr(self, '_last_events_count', 0)
                    self.processing_stats["events_per_second"] = events_diff / time_diff if time_diff > 0 else 0
                
                self._last_performance_check = current_time
                self._last_events_count = self.processing_stats["events_processed"]
                
                # Store performance history
                performance_snapshot = {
                    "timestamp": current_time,
                    "queue_depth": queue_depth,
                    "events_per_second": self.processing_stats["events_per_second"],
                    "error_count": self.processing_stats["error_count"]
                }
                self.performance_history.append(performance_snapshot)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring performance: {e}")
                await asyncio.sleep(5)
    
    async def _flush_stream_buffers(self):
        """Flush stream buffers to subscribers."""
        while self.processing_active:
            try:
                for stream_type, buffer in self.stream_buffers.items():
                    if buffer:
                        config = self.stream_configs[stream_type]
                        
                        # Check if we should flush (buffer size or time threshold)
                        should_flush = (
                            len(buffer) >= config["batch_size"] or
                            time.time() - getattr(self, f'_last_flush_{stream_type.value}', 0) > config["flush_interval_ms"] / 1000
                        )
                        
                        if should_flush:
                            await self._flush_stream_to_subscribers(stream_type, list(buffer))
                            buffer.clear()
                            setattr(self, f'_last_flush_{stream_type.value}', time.time())
                
                await asyncio.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Error flushing stream buffers: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_old_data(self):
        """Clean up old data and connections."""
        while self.processing_active:
            try:
                # Clean up old alerts
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                self.recent_alerts = deque([
                    alert for alert in self.recent_alerts
                    if alert.dispatch_time > cutoff_time
                ], maxlen=1000)
                
                # Clean up disconnected websockets
                disconnected_connections = []
                for subscriber_id, ws in self.websocket_connections.items():
                    if ws.closed:
                        disconnected_connections.append(subscriber_id)
                
                for subscriber_id in disconnected_connections:
                    del self.websocket_connections[subscriber_id]
                    # Remove from all streams
                    for stream_type in StreamType:
                        self.stream_subscribers[stream_type].discard(subscriber_id)
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error cleaning up old data: {e}")
                await asyncio.sleep(60)
    
    async def _process_creator_activity_event(self, event: RealTimeEvent):
        """Process creator activity event."""
        activity_data = CreatorActivityEvent(
            creator_id=event.creator_id or '',
            activity_type=event.data.get('activity_type', 'unknown'),
            content_id=event.content_id,
            platform=event.data.get('platform'),
            metrics=event.data.get('metrics', {}),
            geolocation=event.data.get('geolocation'),
            device_info=event.data.get('device_info')
        )
        
        # Check for activity anomalies
        await self._check_activity_anomalies(activity_data)
        
        logger.debug(f"Processed creator activity event for {event.creator_id}")
    
    async def _process_content_upload_event(self, event: RealTimeEvent):
        """Process content upload event."""
        upload_data = event.data
        
        # Track upload metrics
        await self._track_upload_metrics(event.creator_id, upload_data)
        
        # Check for content quality issues
        if upload_data.get('quality_score', 1.0) < 0.5:
            await self._trigger_content_alert("low_quality", event)
        
        logger.debug(f"Processed content upload event: {event.content_id}")
    
    async def _process_engagement_spike_event(self, event: RealTimeEvent):
        """Process engagement spike event."""
        spike_data = event.data
        engagement_increase = spike_data.get('engagement_increase', 0)
        
        # Determine spike severity
        if engagement_increase > 1000:  # 1000% increase
            await self._trigger_engagement_alert("viral_content", event)
        elif engagement_increase > 100:  # 100% increase
            await self._trigger_engagement_alert("high_engagement", event)
        
        logger.info(f"Processed engagement spike: {engagement_increase}% increase")
    
    async def _process_revenue_event(self, event: RealTimeEvent):
        """Process revenue event."""
        revenue_data = event.data
        amount = revenue_data.get('amount', 0)
        
        # Track revenue metrics
        await self._track_revenue_metrics(event.creator_id, revenue_data)
        
        # Check for significant revenue events
        if amount > 1000:  # $1000+
            await self._trigger_revenue_alert("high_revenue", event)
        
        logger.debug(f"Processed revenue event: ${amount}")
    
    async def _process_collaboration_event(self, event: RealTimeEvent):
        """Process collaboration update event."""
        collab_data = event.data
        status = collab_data.get('status')
        
        # Track collaboration progress
        if status == 'completed':
            await self._track_collaboration_completion(event.creator_id, collab_data)
        elif status == 'failed':
            await self._trigger_collaboration_alert("collaboration_failed", event)
        
        logger.debug(f"Processed collaboration event: {status}")
    
    async def _process_system_performance_event(self, event: RealTimeEvent):
        """Process system performance event."""
        perf_data = event.data
        
        # Check performance thresholds
        cpu_usage = perf_data.get('cpu_usage', 0)
        memory_usage = perf_data.get('memory_usage', 0)
        
        if cpu_usage > 90:
            await self._trigger_system_alert("high_cpu_usage", {"usage": cpu_usage})
        
        if memory_usage > 85:
            await self._trigger_system_alert("high_memory_usage", {"usage": memory_usage})
        
        logger.debug(f"Processed system performance event")
    
    async def _process_user_interaction_event(self, event: RealTimeEvent):
        """Process user interaction event."""
        interaction_data = event.data
        
        # Track user engagement patterns
        await self._track_user_engagement(event.creator_id, interaction_data)
        
        logger.debug(f"Processed user interaction event")
    
    async def _process_generic_event(self, event: RealTimeEvent):
        """Process generic event."""
        logger.debug(f"Processed generic event: {event.event_type.value}")
    
    async def _route_event_to_streams(self, event: RealTimeEvent):
        """Route processed event to appropriate data streams."""
        target_streams = self.event_routing_rules.get(event.event_type, [])
        
        stream_message = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "creator_id": event.creator_id,
            "content_id": event.content_id,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data,
            "processing_latency_ms": event.processing_latency_ms
        }
        
        for stream_type in target_streams:
            self.stream_buffers[stream_type].append(stream_message)
    
    async def _flush_stream_to_subscribers(self, stream_type: StreamType, messages: List[Dict]):
        """Flush stream messages to subscribers."""
        if not messages or not self.stream_subscribers[stream_type]:
            return
        
        batch_message = {
            "stream_type": stream_type.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_count": len(messages),
            "messages": messages
        }
        
        # Send to websocket subscribers
        disconnected_subscribers = []
        for subscriber_id in self.stream_subscribers[stream_type]:
            websocket = self.websocket_connections.get(subscriber_id)
            if websocket and not websocket.closed:
                try:
                    await websocket.send(json.dumps(batch_message, default=str))
                except Exception as e:
                    logger.error(f"Failed to send to subscriber {subscriber_id}: {e}")
                    disconnected_subscribers.append(subscriber_id)
            else:
                disconnected_subscribers.append(subscriber_id)
        
        # Remove disconnected subscribers
        for subscriber_id in disconnected_subscribers:
            await self.unsubscribe_from_stream(stream_type, subscriber_id)
        
        # Update stream metrics
        metrics = self.stream_metrics[stream_type]
        metrics.data_throughput_bytes += len(json.dumps(batch_message, default=str))
    
    async def _should_throttle_alert(self, alert: AlertDispatch) -> bool:
        """Check if alert should be throttled."""
        current_time = datetime.now(timezone.utc)
        
        # Check overall rate limit
        recent_alerts = [a for a in self.recent_alerts 
                        if (current_time - a.dispatch_time).total_seconds() < 60]
        
        if len(recent_alerts) >= self.alert_throttling["max_alerts_per_minute"]:
            return True
        
        # Check duplicate suppression
        suppression_window = timedelta(minutes=self.alert_throttling["duplicate_suppression_window_minutes"])
        duplicate_alerts = [a for a in self.recent_alerts 
                           if a.alert_type == alert.alert_type and 
                           (current_time - a.dispatch_time) < suppression_window]
        
        if duplicate_alerts:
            return True
        
        return False
    
    async def _send_websocket_alert(self, alert: AlertDispatch) -> bool:
        """Send alert via websocket."""
        alert_message = {
            "type": "alert",
            "alert_id": alert.alert_id,
            "alert_type": alert.alert_type,
            "priority": alert.priority.value,
            "dispatch_time": alert.dispatch_time.isoformat(),
            "data": asdict(alert)
        }
        
        success_count = 0
        total_connections = len(self.websocket_connections)
        
        for subscriber_id, websocket in self.websocket_connections.items():
            if not websocket.closed:
                try:
                    await websocket.send(json.dumps(alert_message, default=str))
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send websocket alert to {subscriber_id}: {e}")
        
        return success_count > 0
    
    async def _send_email_alert(self, alert: AlertDispatch) -> bool:
        """Send alert via email (simulated)."""
        # In production, integrate with email service
        logger.info(f"Email alert sent: {alert.alert_type} (simulated)")
        return True
    
    async def _send_sms_alert(self, alert: AlertDispatch) -> bool:
        """Send alert via SMS (simulated)."""
        # In production, integrate with SMS service
        logger.info(f"SMS alert sent: {alert.alert_type} (simulated)")
        return True
    
    async def _send_push_notification(self, alert: AlertDispatch) -> bool:
        """Send push notification (simulated)."""
        # In production, integrate with push notification service
        logger.info(f"Push notification sent: {alert.alert_type} (simulated)")
        return True
    
    async def _send_slack_alert(self, alert: AlertDispatch) -> bool:
        """Send alert to Slack (simulated)."""
        # In production, integrate with Slack API
        logger.info(f"Slack alert sent: {alert.alert_type} (simulated)")
        return True
    
    async def _send_dashboard_alert(self, alert: AlertDispatch) -> bool:
        """Send alert to dashboard."""
        # Route to dashboard stream
        dashboard_message = {
            "type": "dashboard_alert",
            "alert": asdict(alert),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.stream_buffers[StreamType.DASHBOARD_STREAM].append(dashboard_message)
        return True
    
    async def _check_activity_anomalies(self, activity: CreatorActivityEvent):
        """Check for activity anomalies."""
        # Implement anomaly detection logic
        metrics = activity.metrics
        
        # Check for unusual activity patterns
        if metrics.get('requests_per_minute', 0) > 1000:
            await self._trigger_activity_alert("high_activity_rate", activity)
    
    async def _track_upload_metrics(self, creator_id: str, upload_data: Dict):
        """Track content upload metrics."""
        # Store upload metrics for analytics
        logger.debug(f"Tracked upload metrics for creator {creator_id}")
    
    async def _track_revenue_metrics(self, creator_id: str, revenue_data: Dict):
        """Track revenue metrics."""
        # Store revenue metrics for analytics
        logger.debug(f"Tracked revenue metrics for creator {creator_id}")
    
    async def _track_collaboration_completion(self, creator_id: str, collab_data: Dict):
        """Track collaboration completion."""
        # Store collaboration metrics
        logger.debug(f"Tracked collaboration completion for creator {creator_id}")
    
    async def _track_user_engagement(self, creator_id: str, interaction_data: Dict):
        """Track user engagement patterns."""
        # Store engagement metrics
        logger.debug(f"Tracked user engagement for creator {creator_id}")
    
    async def _trigger_system_alert(self, alert_type: str, data: Dict):
        """Trigger system-level alert."""
        await self.dispatch_alert({
            "type": alert_type,
            "priority": "high",
            "data": data,
            "channels": ["websocket", "email"]
        })
    
    async def _trigger_performance_alert(self, alert_type: str, metric_value: Any):
        """Trigger performance-related alert."""
        await self.dispatch_alert({
            "type": f"performance_{alert_type}",
            "priority": "medium",
            "data": {"metric_value": metric_value},
            "channels": ["websocket"]
        })
    
    async def _trigger_content_alert(self, alert_type: str, event: RealTimeEvent):
        """Trigger content-related alert."""
        await self.dispatch_alert({
            "type": f"content_{alert_type}",
            "priority": "low",
            "data": {"event": asdict(event)},
            "channels": ["dashboard"]
        })
    
    async def _trigger_engagement_alert(self, alert_type: str, event: RealTimeEvent):
        """Trigger engagement-related alert."""
        await self.dispatch_alert({
            "type": f"engagement_{alert_type}",
            "priority": "high",
            "data": {"event": asdict(event)},
            "channels": ["websocket", "push"]
        })
    
    async def _trigger_revenue_alert(self, alert_type: str, event: RealTimeEvent):
        """Trigger revenue-related alert."""
        await self.dispatch_alert({
            "type": f"revenue_{alert_type}",
            "priority": "medium",
            "data": {"event": asdict(event)},
            "channels": ["websocket", "email"]
        })
    
    async def _trigger_collaboration_alert(self, alert_type: str, event: RealTimeEvent):
        """Trigger collaboration-related alert."""
        await self.dispatch_alert({
            "type": f"collaboration_{alert_type}",
            "priority": "medium",
            "data": {"event": asdict(event)},
            "channels": ["websocket"]
        })
    
    async def _trigger_activity_alert(self, alert_type: str, activity: CreatorActivityEvent):
        """Trigger activity-related alert."""
        await self.dispatch_alert({
            "type": f"activity_{alert_type}",
            "priority": "high",
            "data": {"activity": asdict(activity)},
            "channels": ["websocket", "email"]
        })
    
    async def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data."""
        return {
            "processing_stats": self.processing_stats,
            "stream_metrics": {
                stream_type.value: asdict(metrics)
                for stream_type, metrics in self.stream_metrics.items()
            },
            "active_subscribers": sum(len(subscribers) for subscribers in self.stream_subscribers.values()),
            "alert_summary": {
                "recent_alerts_count": len(self.recent_alerts),
                "alerts_by_priority": {
                    priority.value: len([a for a in self.recent_alerts if a.priority == priority])
                    for priority in AlertPriority
                }
            },
            "performance_snapshot": list(self.performance_history)[-10:] if self.performance_history else [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on real-time monitoring systems."""
        return {
            "status": "healthy" if self.processing_active else "inactive",
            "event_queue_size": self.event_queue.qsize(),
            "alert_queue_size": self.alert_queue.qsize(),
            "active_websocket_connections": len(self.websocket_connections),
            "total_events_processed": self.processing_stats["events_processed"],
            "events_per_second": self.processing_stats["events_per_second"],
            "error_rate": self.processing_stats["error_count"] / max(1, self.processing_stats["events_processed"]),
            "last_check": datetime.now(timezone.utc).isoformat()
        }

# Global real-time monitoring instance
real_time_monitoring_dispatcher = RealTimeMonitoringDispatcher()

async def main():
    """Main function for testing real-time monitoring."""
    dispatcher = RealTimeMonitoringDispatcher()
    
    # Test event publishing
    event_data = {
        'type': 'creator_activity',
        'creator_id': 'creator_1',
        'content_id': 'content_001',
        'priority': 'medium',
        'data': {
            'activity_type': 'content_upload',
            'platform': 'youtube',
            'metrics': {
                'file_size': 1024000,
                'duration': 300,
                'quality_score': 0.85
            }
        }
    }
    
    event_id = await dispatcher.publish_event(event_data)
    print(f"Published event: {event_id}")
    
    # Test alert dispatching
    alert_data = {
        'type': 'engagement_spike',
        'priority': 'high',
        'channels': ['websocket', 'email'],
        'recipients': ['admin@ainflue.com']
    }
    
    alert_id = await dispatcher.dispatch_alert(alert_data)
    print(f"Dispatched alert: {alert_id}")
    
    # Get dashboard data
    dashboard = await dispatcher.get_real_time_dashboard_data()
    print(f"Dashboard data: {json.dumps(dashboard, indent=2, default=str)}")
    
    # Health check
    health = await dispatcher.health_check()
    print(f"Health check: {json.dumps(health, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())