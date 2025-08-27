"""
IA Influencer Agent - Real-Time Monitoring System
===============================================

Advanced real-time monitoring system for fingerprinting and content protection.
Provides millisecond-level detection, streaming analytics, and instant violation alerts.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import uuid
import weakref
from collections import deque, defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import aioredis
import websockets
from aiohttp import web, WSMsgType
import psutil
import pandas as pd

# Internal imports
from .config import FingerprintingSystemConfig
from .fingerprint_manager import FingerprintManager, FingerprintResult
from .vector_matcher import VectorMatcher, MatchResult
from .metadata import ContentMetadata
from .surveillance_integration import SurveillanceIntegrationManager, SurveillanceEvent

logger = logging.getLogger(__name__)


class MonitoringMode(Enum):
    """Real-time monitoring modes"""
    PASSIVE = "passive"  # Monitor only
    ACTIVE = "active"    # Monitor and respond
    AGGRESSIVE = "aggressive"  # Proactive monitoring with prediction
    STEALTH = "stealth"  # Low-profile monitoring


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Types of monitoring metrics"""
    FINGERPRINT_CREATED = "fingerprint_created"
    SIMILARITY_MATCH = "similarity_match"
    VIOLATION_DETECTED = "violation_detected"
    PERFORMANCE_METRIC = "performance_metric"
    SYSTEM_HEALTH = "system_health"
    PLATFORM_SCAN = "platform_scan"
    USER_ACTIVITY = "user_activity"


@dataclass
class RealTimeMetric:
    """Real-time monitoring metric"""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: MetricType = MetricType.SYSTEM_HEALTH
    value: float = 0.0
    unit: str = ""
    source: str = "unknown"
    fingerprint_id: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)


@dataclass
class AlertEvent:
    """Real-time alert event"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: AlertLevel = AlertLevel.INFO
    title: str = ""
    message: str = ""
    source: str = "monitoring_system"
    fingerprint_id: Optional[str] = None
    content_id: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class MonitoringSubscription:
    """Real-time monitoring subscription"""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""
    websocket: Optional[Any] = None
    metric_filters: List[MetricType] = field(default_factory=list)
    alert_filters: List[AlertLevel] = field(default_factory=list)
    fingerprint_filters: List[str] = field(default_factory=list)
    update_frequency: float = 1.0  # seconds
    last_update: datetime = field(default_factory=datetime.utcnow)
    active: bool = True


@dataclass
class StreamingWindow:
    """Sliding window for streaming analytics"""
    window_size: int = 100
    time_window: int = 60  # seconds
    values: deque = field(default_factory=deque)
    timestamps: deque = field(default_factory=deque)
    
    def add_value(self, value: float, timestamp: Optional[datetime] = None):
        """Add value to streaming window"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        self.values.append(value)
        self.timestamps.append(timestamp)
        
        # Remove old values based on time window
        cutoff_time = timestamp - timedelta(seconds=self.time_window)
        while self.timestamps and self.timestamps[0] < cutoff_time:
            self.timestamps.popleft()
            self.values.popleft()
        
        # Remove old values based on size window
        while len(self.values) > self.window_size:
            self.timestamps.popleft()
            self.values.popleft()
    
    def get_statistics(self) -> Dict[str, float]:
        """Get window statistics"""
        if not self.values:
            return {}
        
        values_array = np.array(list(self.values))
        return {
            'count': len(self.values),
            'mean': float(np.mean(values_array)),
            'median': float(np.median(values_array)),
            'std': float(np.std(values_array)),
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'sum': float(np.sum(values_array)),
            'rate_per_minute': len(self.values) / (self.time_window / 60.0)
        }


class RealTimeMonitor:
    """Advanced real-time monitoring system"""
    
    def __init__(self, config: FingerprintingSystemConfig):
        self.config = config
        self.mode = MonitoringMode.ACTIVE
        self.running = False
        
        # Data storage
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.alerts_buffer: deque = deque(maxlen=1000)
        self.subscriptions: Dict[str, MonitoringSubscription] = {}
        
        # Streaming analytics
        self.streaming_windows: Dict[str, StreamingWindow] = {}
        self.alert_thresholds: Dict[MetricType, Dict[str, float]] = {}
        
        # Real-time connections
        self.websocket_server: Optional[Any] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Background tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Performance tracking
        self.start_time = datetime.utcnow()
        self.total_metrics_processed = 0
        self.total_alerts_generated = 0
        
        # Initialize streaming windows
        self._initialize_streaming_windows()
        
        # Setup alert thresholds
        self._setup_alert_thresholds()
        
        logger.info("Real-time monitor initialized")
    
    def _initialize_streaming_windows(self):
        """Initialize streaming analytics windows"""
        window_configs = {
            'fingerprint_rate': StreamingWindow(window_size=100, time_window=300),  # 5 minutes
            'similarity_scores': StreamingWindow(window_size=200, time_window=600),  # 10 minutes
            'violation_rate': StreamingWindow(window_size=50, time_window=3600),   # 1 hour
            'system_cpu': StreamingWindow(window_size=60, time_window=120),        # 2 minutes
            'system_memory': StreamingWindow(window_size=60, time_window=120),     # 2 minutes
            'response_times': StreamingWindow(window_size=100, time_window=300),   # 5 minutes
        }
        
        for name, window in window_configs.items():
            self.streaming_windows[name] = window
    
    def _setup_alert_thresholds(self):
        """Setup alert thresholds for different metrics"""
        self.alert_thresholds = {
            MetricType.SIMILARITY_MATCH: {
                'warning': 0.8,
                'critical': 0.9,
                'emergency': 0.95
            },
            MetricType.VIOLATION_DETECTED: {
                'warning': 1.0,  # Any violation is a warning
                'critical': 3.0,  # 3 violations in window
                'emergency': 5.0  # 5 violations in window
            },
            MetricType.PERFORMANCE_METRIC: {
                'warning': 2.0,   # 2 second response time
                'critical': 5.0,  # 5 second response time
                'emergency': 10.0 # 10 second response time
            },
            MetricType.SYSTEM_HEALTH: {
                'warning': 80.0,  # 80% resource usage
                'critical': 90.0, # 90% resource usage
                'emergency': 95.0 # 95% resource usage
            }
        }
    
    async def start(self):
        """Start real-time monitoring system"""
        if self.running:
            logger.warning("Real-time monitor already running")
            return
        
        try:
            # Initialize Redis connection
            self.redis_client = await aioredis.from_url(
                self.config.redis_url if hasattr(self.config, 'redis_url') 
                else "redis://localhost:6379",
                decode_responses=True
            )
            
            # Start WebSocket server
            await self._start_websocket_server()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            self.running = True
            self.start_time = datetime.utcnow()
            
            logger.info("Real-time monitoring system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start real-time monitor: {str(e)}")
            raise
    
    async def stop(self):
        """Stop real-time monitoring system"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            if not task.done():
                task.cancel()
        
        # Close WebSocket server
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Real-time monitoring system stopped")
    
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        async def handle_websocket(websocket, path):
            client_id = str(uuid.uuid4())
            logger.info(f"WebSocket client connected: {client_id}")
            
            try:
                subscription = MonitoringSubscription(
                    client_id=client_id,
                    websocket=websocket,
                    metric_filters=[],  # All metrics by default
                    alert_filters=[AlertLevel.WARNING, AlertLevel.CRITICAL, AlertLevel.EMERGENCY]
                )
                
                self.subscriptions[subscription.subscription_id] = subscription
                
                # Send initial connection message
                await websocket.send(json.dumps({
                    'type': 'connection',
                    'subscription_id': subscription.subscription_id,
                    'client_id': client_id,
                    'timestamp': datetime.utcnow().isoformat()
                }))
                
                # Handle incoming messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self._handle_websocket_message(subscription, data)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from client {client_id}")
                    except Exception as e:
                        logger.error(f"Error handling WebSocket message: {str(e)}")
                        
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"WebSocket client disconnected: {client_id}")
            except Exception as e:
                logger.error(f"WebSocket error for client {client_id}: {str(e)}")
            finally:
                # Clean up subscription
                subscription_to_remove = None
                for sub_id, sub in self.subscriptions.items():
                    if sub.client_id == client_id:
                        subscription_to_remove = sub_id
                        break
                
                if subscription_to_remove:
                    del self.subscriptions[subscription_to_remove]
        
        # Start WebSocket server
        self.websocket_server = await websockets.serve(
            handle_websocket,
            "localhost",
            8765,
            ping_interval=30,
            ping_timeout=10
        )
        
        logger.info("WebSocket server started on ws://localhost:8765")
    
    async def _handle_websocket_message(
        self, 
        subscription: MonitoringSubscription, 
        message: Dict[str, Any]
    ):
        """Handle incoming WebSocket message"""
        message_type = message.get('type')
        
        if message_type == 'subscribe':
            # Update subscription filters
            if 'metric_filters' in message:
                subscription.metric_filters = [
                    MetricType(filter_type) for filter_type in message['metric_filters']
                ]
            
            if 'alert_filters' in message:
                subscription.alert_filters = [
                    AlertLevel(level) for level in message['alert_filters']
                ]
            
            if 'fingerprint_filters' in message:
                subscription.fingerprint_filters = message['fingerprint_filters']
            
            if 'update_frequency' in message:
                subscription.update_frequency = float(message['update_frequency'])
            
            logger.debug(f"Updated subscription filters for {subscription.client_id}")
            
        elif message_type == 'get_status':
            # Send current system status
            status = await self.get_system_status()
            await subscription.websocket.send(json.dumps({
                'type': 'status_response',
                'data': status,
                'timestamp': datetime.utcnow().isoformat()
            }))
            
        elif message_type == 'acknowledge_alert':
            # Acknowledge alert
            alert_id = message.get('alert_id')
            if alert_id:
                await self._acknowledge_alert(alert_id)
    
    async def _start_monitoring_tasks(self):
        """Start background monitoring tasks"""
        # System metrics monitoring
        async def monitor_system_metrics():
            while self.running:
                try:
                    await self._collect_system_metrics()
                    await asyncio.sleep(5)  # 5 second intervals
                except Exception as e:
                    logger.error(f"System metrics monitoring error: {str(e)}")
                    await asyncio.sleep(10)
        
        # Alert processing
        async def process_alerts():
            while self.running:
                try:
                    await self._process_pending_alerts()
                    await asyncio.sleep(1)  # 1 second intervals
                except Exception as e:
                    logger.error(f"Alert processing error: {str(e)}")
                    await asyncio.sleep(5)
        
        # WebSocket updates
        async def send_websocket_updates():
            while self.running:
                try:
                    await self._send_websocket_updates()
                    await asyncio.sleep(1)  # 1 second intervals
                except Exception as e:
                    logger.error(f"WebSocket updates error: {str(e)}")
                    await asyncio.sleep(5)
        
        # Data cleanup
        async def cleanup_old_data():
            while self.running:
                try:
                    await self._cleanup_old_data()
                    await asyncio.sleep(300)  # 5 minute intervals
                except Exception as e:
                    logger.error(f"Data cleanup error: {str(e)}")
                    await asyncio.sleep(600)  # Wait longer on error
        
        # Start all tasks
        tasks = [
            monitor_system_metrics(),
            process_alerts(),
            send_websocket_updates(),
            cleanup_old_data()
        ]
        
        for task_coro in tasks:
            task = asyncio.create_task(task_coro)
            self.monitoring_tasks.append(task)
    
    async def record_metric(self, metric: RealTimeMetric):
        """Record a real-time metric"""
        try:
            # Add to buffer
            self.metrics_buffer.append(metric)
            self.total_metrics_processed += 1
            
            # Update streaming windows
            await self._update_streaming_windows(metric)
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
            # Store in Redis for persistence
            if self.redis_client:
                await self.redis_client.lpush(
                    "realtime_metrics",
                    json.dumps({
                        'metric_id': metric.metric_id,
                        'metric_type': metric.metric_type.value,
                        'value': metric.value,
                        'unit': metric.unit,
                        'source': metric.source,
                        'fingerprint_id': metric.fingerprint_id,
                        'content_id': metric.content_id,
                        'metadata': metric.metadata,
                        'timestamp': metric.timestamp.isoformat(),
                        'tags': metric.tags
                    })
                )
                
                # Trim list to prevent unlimited growth
                await self.redis_client.ltrim("realtime_metrics", 0, 9999)
            
            logger.debug(f"Recorded metric: {metric.metric_type.value} = {metric.value}")
            
        except Exception as e:
            logger.error(f"Failed to record metric: {str(e)}")
    
    async def generate_alert(self, alert: AlertEvent):
        """Generate a real-time alert"""
        try:
            # Add to buffer
            self.alerts_buffer.append(alert)
            self.total_alerts_generated += 1
            
            # Store in Redis
            if self.redis_client:
                await self.redis_client.lpush(
                    "realtime_alerts",
                    json.dumps({
                        'alert_id': alert.alert_id,
                        'level': alert.level.value,
                        'title': alert.title,
                        'message': alert.message,
                        'source': alert.source,
                        'fingerprint_id': alert.fingerprint_id,
                        'content_id': alert.content_id,
                        'evidence': alert.evidence,
                        'suggested_actions': alert.suggested_actions,
                        'timestamp': alert.timestamp.isoformat(),
                        'acknowledged': alert.acknowledged,
                        'resolved': alert.resolved
                    })
                )
                
                # Trim list
                await self.redis_client.ltrim("realtime_alerts", 0, 999)
            
            logger.info(f"Generated {alert.level.value} alert: {alert.title}")
            
            # Send to surveillance integration if available
            try:
                from .surveillance_integration import send_surveillance_message, SurveillanceEvent
                await send_surveillance_message(
                    SurveillanceEvent.VIOLATION_SUSPECTED,
                    fingerprint_id=alert.fingerprint_id,
                    content_id=alert.content_id,
                    payload={
                        'alert_id': alert.alert_id,
                        'level': alert.level.value,
                        'title': alert.title,
                        'message': alert.message,
                        'evidence': alert.evidence
                    },
                    priority=10 if alert.level == AlertLevel.EMERGENCY else 5
                )
            except Exception as e:
                logger.debug(f"Could not send to surveillance integration: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to generate alert: {str(e)}")
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric(RealTimeMetric(
                metric_type=MetricType.SYSTEM_HEALTH,
                value=cpu_percent,
                unit="percent",
                source="system_cpu",
                metadata={'resource': 'cpu'}
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.record_metric(RealTimeMetric(
                metric_type=MetricType.SYSTEM_HEALTH,
                value=memory.percent,
                unit="percent",
                source="system_memory",
                metadata={'resource': 'memory', 'available': memory.available}
            ))
            
            # Disk usage
            disk = psutil.disk_usage('/')
            await self.record_metric(RealTimeMetric(
                metric_type=MetricType.SYSTEM_HEALTH,
                value=(disk.used / disk.total) * 100,
                unit="percent",
                source="system_disk",
                metadata={'resource': 'disk', 'free': disk.free}
            ))
            
            # Network I/O
            network = psutil.net_io_counters()
            await self.record_metric(RealTimeMetric(
                metric_type=MetricType.SYSTEM_HEALTH,
                value=network.bytes_sent + network.bytes_recv,
                unit="bytes",
                source="system_network",
                metadata={'bytes_sent': network.bytes_sent, 'bytes_recv': network.bytes_recv}
            ))
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
    
    async def _update_streaming_windows(self, metric: RealTimeMetric):
        """Update streaming analytics windows"""
        try:
            # Map metrics to windows
            if metric.metric_type == MetricType.FINGERPRINT_CREATED:
                self.streaming_windows['fingerprint_rate'].add_value(1.0, metric.timestamp)
            
            elif metric.metric_type == MetricType.SIMILARITY_MATCH:
                self.streaming_windows['similarity_scores'].add_value(metric.value, metric.timestamp)
            
            elif metric.metric_type == MetricType.VIOLATION_DETECTED:
                self.streaming_windows['violation_rate'].add_value(1.0, metric.timestamp)
            
            elif metric.metric_type == MetricType.PERFORMANCE_METRIC:
                self.streaming_windows['response_times'].add_value(metric.value, metric.timestamp)
            
            elif metric.metric_type == MetricType.SYSTEM_HEALTH:
                if metric.source == "system_cpu":
                    self.streaming_windows['system_cpu'].add_value(metric.value, metric.timestamp)
                elif metric.source == "system_memory":
                    self.streaming_windows['system_memory'].add_value(metric.value, metric.timestamp)
            
        except Exception as e:
            logger.error(f"Failed to update streaming windows: {str(e)}")
    
    async def _check_metric_alerts(self, metric: RealTimeMetric):
        """Check if metric triggers any alerts"""
        try:
            thresholds = self.alert_thresholds.get(metric.metric_type, {})
            
            if not thresholds:
                return
            
            # Check emergency threshold
            if 'emergency' in thresholds and metric.value >= thresholds['emergency']:
                await self.generate_alert(AlertEvent(
                    level=AlertLevel.EMERGENCY,
                    title=f"Emergency: {metric.metric_type.value}",
                    message=f"Metric {metric.metric_type.value} reached emergency level: {metric.value} {metric.unit}",
                    source=metric.source,
                    fingerprint_id=metric.fingerprint_id,
                    content_id=metric.content_id,
                    evidence={'metric_value': metric.value, 'threshold': thresholds['emergency']},
                    suggested_actions=["Immediate investigation required", "Check system resources", "Review recent changes"]
                ))
            
            # Check critical threshold
            elif 'critical' in thresholds and metric.value >= thresholds['critical']:
                await self.generate_alert(AlertEvent(
                    level=AlertLevel.CRITICAL,
                    title=f"Critical: {metric.metric_type.value}",
                    message=f"Metric {metric.metric_type.value} reached critical level: {metric.value} {metric.unit}",
                    source=metric.source,
                    fingerprint_id=metric.fingerprint_id,
                    content_id=metric.content_id,
                    evidence={'metric_value': metric.value, 'threshold': thresholds['critical']},
                    suggested_actions=["Investigation required", "Monitor closely", "Consider scaling resources"]
                ))
            
            # Check warning threshold
            elif 'warning' in thresholds and metric.value >= thresholds['warning']:
                await self.generate_alert(AlertEvent(
                    level=AlertLevel.WARNING,
                    title=f"Warning: {metric.metric_type.value}",
                    message=f"Metric {metric.metric_type.value} reached warning level: {metric.value} {metric.unit}",
                    source=metric.source,
                    fingerprint_id=metric.fingerprint_id,
                    content_id=metric.content_id,
                    evidence={'metric_value': metric.value, 'threshold': thresholds['warning']},
                    suggested_actions=["Monitor situation", "Check trends", "Review performance"]
                ))
            
        except Exception as e:
            logger.error(f"Failed to check metric alerts: {str(e)}")
    
    async def _process_pending_alerts(self):
        """Process pending alerts and handle escalation"""
        try:
            current_time = datetime.utcnow()
            
            # Check for unacknowledged critical/emergency alerts
            for alert in list(self.alerts_buffer):
                if (alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY] and
                    not alert.acknowledged and
                    current_time - alert.timestamp > timedelta(minutes=5)):
                    
                    # Escalate unacknowledged critical alerts
                    await self._escalate_alert(alert)
                
                # Auto-resolve old info/warning alerts
                elif (alert.level in [AlertLevel.INFO, AlertLevel.WARNING] and
                      current_time - alert.timestamp > timedelta(hours=1)):
                    alert.resolved = True
            
        except Exception as e:
            logger.error(f"Failed to process pending alerts: {str(e)}")
    
    async def _escalate_alert(self, alert: AlertEvent):
        """Escalate unacknowledged alert"""
        try:
            escalated_alert = AlertEvent(
                level=AlertLevel.EMERGENCY,
                title=f"ESCALATED: {alert.title}",
                message=f"Alert escalated due to no acknowledgment: {alert.message}",
                source=f"escalation_{alert.source}",
                fingerprint_id=alert.fingerprint_id,
                content_id=alert.content_id,
                evidence={**alert.evidence, 'original_alert_id': alert.alert_id},
                suggested_actions=["IMMEDIATE ACTION REQUIRED"] + alert.suggested_actions
            )
            
            await self.generate_alert(escalated_alert)
            logger.warning(f"Alert escalated: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to escalate alert: {str(e)}")
    
    async def _send_websocket_updates(self):
        """Send real-time updates to WebSocket clients"""
        try:
            if not self.subscriptions:
                return
            
            current_time = datetime.utcnow()
            
            # Get recent metrics and alerts
            recent_metrics = [
                metric for metric in list(self.metrics_buffer)
                if current_time - metric.timestamp < timedelta(seconds=5)
            ]
            
            recent_alerts = [
                alert for alert in list(self.alerts_buffer)
                if current_time - alert.timestamp < timedelta(seconds=30)
            ]
            
            # Send to each subscription
            disconnected_subscriptions = []
            
            for subscription in self.subscriptions.values():
                try:
                    if (current_time - subscription.last_update).total_seconds() < subscription.update_frequency:
                        continue
                    
                    # Filter metrics
                    filtered_metrics = []
                    for metric in recent_metrics:
                        if (not subscription.metric_filters or 
                            metric.metric_type in subscription.metric_filters):
                            if (not subscription.fingerprint_filters or
                                metric.fingerprint_id in subscription.fingerprint_filters):
                                filtered_metrics.append({
                                    'metric_id': metric.metric_id,
                                    'metric_type': metric.metric_type.value,
                                    'value': metric.value,
                                    'unit': metric.unit,
                                    'source': metric.source,
                                    'fingerprint_id': metric.fingerprint_id,
                                    'content_id': metric.content_id,
                                    'timestamp': metric.timestamp.isoformat()
                                })
                    
                    # Filter alerts
                    filtered_alerts = []
                    for alert in recent_alerts:
                        if (not subscription.alert_filters or 
                            alert.level in subscription.alert_filters):
                            if (not subscription.fingerprint_filters or
                                alert.fingerprint_id in subscription.fingerprint_filters):
                                filtered_alerts.append({
                                    'alert_id': alert.alert_id,
                                    'level': alert.level.value,
                                    'title': alert.title,
                                    'message': alert.message,
                                    'fingerprint_id': alert.fingerprint_id,
                                    'content_id': alert.content_id,
                                    'timestamp': alert.timestamp.isoformat(),
                                    'acknowledged': alert.acknowledged,
                                    'resolved': alert.resolved
                                })
                    
                    # Send update if there's data or it's time for a heartbeat
                    if (filtered_metrics or filtered_alerts or 
                        (current_time - subscription.last_update).total_seconds() > 30):
                        
                        update_message = {
                            'type': 'realtime_update',
                            'metrics': filtered_metrics,
                            'alerts': filtered_alerts,
                            'timestamp': current_time.isoformat()
                        }
                        
                        await subscription.websocket.send(json.dumps(update_message))
                        subscription.last_update = current_time
                
                except websockets.exceptions.ConnectionClosed:
                    disconnected_subscriptions.append(subscription.subscription_id)
                except Exception as e:
                    logger.error(f"WebSocket update error for {subscription.client_id}: {str(e)}")
                    disconnected_subscriptions.append(subscription.subscription_id)
            
            # Clean up disconnected subscriptions
            for subscription_id in disconnected_subscriptions:
                if subscription_id in self.subscriptions:
                    del self.subscriptions[subscription_id]
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket updates: {str(e)}")
    
    async def _cleanup_old_data(self):
        """Clean up old metrics and alerts"""
        try:
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(hours=24)
            
            # Clean metrics buffer
            self.metrics_buffer = deque([
                metric for metric in self.metrics_buffer
                if metric.timestamp > cutoff_time
            ], maxlen=10000)
            
            # Clean alerts buffer
            self.alerts_buffer = deque([
                alert for alert in self.alerts_buffer
                if alert.timestamp > cutoff_time
            ], maxlen=1000)
            
            logger.debug("Cleaned up old monitoring data")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {str(e)}")
    
    async def _acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        try:
            for alert in self.alerts_buffer:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    logger.info(f"Alert acknowledged: {alert_id}")
                    break
            
            # Update in Redis
            if self.redis_client:
                # This would require a more sophisticated Redis data structure
                # for efficient updates in a production system
                pass
                
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {str(e)}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system monitoring status"""
        try:
            current_time = datetime.utcnow()
            uptime = (current_time - self.start_time).total_seconds()
            
            # Get streaming statistics
            streaming_stats = {}
            for name, window in self.streaming_windows.items():
                streaming_stats[name] = window.get_statistics()
            
            # Count recent alerts by level
            recent_alerts = [
                alert for alert in self.alerts_buffer
                if current_time - alert.timestamp < timedelta(hours=1)
            ]
            
            alert_counts = defaultdict(int)
            for alert in recent_alerts:
                alert_counts[alert.level.value] += 1
            
            return {
                'status': 'running' if self.running else 'stopped',
                'uptime_seconds': uptime,
                'mode': self.mode.value,
                'metrics_processed': self.total_metrics_processed,
                'alerts_generated': self.total_alerts_generated,
                'active_subscriptions': len(self.subscriptions),
                'metrics_buffer_size': len(self.metrics_buffer),
                'alerts_buffer_size': len(self.alerts_buffer),
                'streaming_statistics': streaming_stats,
                'recent_alert_counts': dict(alert_counts),
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
            return {'error': str(e)}
    
    def set_mode(self, mode: MonitoringMode):
        """Set monitoring mode"""
        self.mode = mode
        logger.info(f"Monitoring mode set to: {mode.value}")
    
    def get_recent_metrics(
        self, 
        metric_type: Optional[MetricType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent metrics"""
        metrics = list(self.metrics_buffer)
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        # Sort by timestamp and limit
        metrics.sort(key=lambda x: x.timestamp, reverse=True)
        metrics = metrics[:limit]
        
        return [
            {
                'metric_id': m.metric_id,
                'metric_type': m.metric_type.value,
                'value': m.value,
                'unit': m.unit,
                'source': m.source,
                'fingerprint_id': m.fingerprint_id,
                'content_id': m.content_id,
                'metadata': m.metadata,
                'timestamp': m.timestamp.isoformat(),
                'tags': m.tags
            }
            for m in metrics
        ]
    
    def get_recent_alerts(
        self, 
        level: Optional[AlertLevel] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        alerts = list(self.alerts_buffer)
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        # Sort by timestamp and limit
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        alerts = alerts[:limit]
        
        return [
            {
                'alert_id': a.alert_id,
                'level': a.level.value,
                'title': a.title,
                'message': a.message,
                'source': a.source,
                'fingerprint_id': a.fingerprint_id,
                'content_id': a.content_id,
                'evidence': a.evidence,
                'suggested_actions': a.suggested_actions,
                'timestamp': a.timestamp.isoformat(),
                'acknowledged': a.acknowledged,
                'resolved': a.resolved
            }
            for a in alerts
        ]


# Global real-time monitor instance
_realtime_monitor: Optional[RealTimeMonitor] = None


def get_realtime_monitor(config: Optional[FingerprintingSystemConfig] = None) -> RealTimeMonitor:
    """Get or create real-time monitor instance"""
    global _realtime_monitor
    
    if _realtime_monitor is None:
        if config is None:
            from .config import get_config
            config = get_config()
        _realtime_monitor = RealTimeMonitor(config)
    
    return _realtime_monitor


def reset_realtime_monitor():
    """Reset real-time monitor (for testing)"""
    global _realtime_monitor
    if _realtime_monitor:
        asyncio.create_task(_realtime_monitor.stop())
    _realtime_monitor = None


# Convenience functions
async def record_fingerprint_metric(fingerprint_id: str, metric_type: MetricType, value: float, **kwargs):
    """Record fingerprint-related metric"""
    monitor = get_realtime_monitor()
    
    metric = RealTimeMetric(
        metric_type=metric_type,
        value=value,
        fingerprint_id=fingerprint_id,
        source=kwargs.get('source', 'fingerprinting_system'),
        unit=kwargs.get('unit', ''),
        metadata=kwargs.get('metadata', {}),
        tags=kwargs.get('tags', [])
    )
    
    await monitor.record_metric(metric)


async def record_performance_metric(operation: str, duration: float, **kwargs):
    """Record performance metric"""
    monitor = get_realtime_monitor()
    
    metric = RealTimeMetric(
        metric_type=MetricType.PERFORMANCE_METRIC,
        value=duration,
        unit="seconds",
        source=f"performance_{operation}",
        metadata={'operation': operation, **kwargs.get('metadata', {})},
        tags=kwargs.get('tags', [])
    )
    
    await monitor.record_metric(metric)


async def generate_violation_alert(
    fingerprint_id: str, 
    content_id: str, 
    similarity_score: float,
    evidence: Dict[str, Any],
    **kwargs
):
    """Generate violation alert"""
    monitor = get_realtime_monitor()
    
    # Determine alert level based on similarity score
    if similarity_score >= 0.95:
        level = AlertLevel.EMERGENCY
    elif similarity_score >= 0.9:
        level = AlertLevel.CRITICAL
    elif similarity_score >= 0.8:
        level = AlertLevel.WARNING
    else:
        level = AlertLevel.INFO
    
    alert = AlertEvent(
        level=level,
        title=f"Content Violation Detected ({similarity_score:.1%} similarity)",
        message=f"Potential copyright violation detected for content {content_id}",
        source="violation_detector",
        fingerprint_id=fingerprint_id,
        content_id=content_id,
        evidence=evidence,
        suggested_actions=[
            "Review detected content",
            "Verify ownership claims",
            "Consider legal action if confirmed",
            "Update monitoring parameters"
        ]
    )
    
    await monitor.generate_alert(alert)
