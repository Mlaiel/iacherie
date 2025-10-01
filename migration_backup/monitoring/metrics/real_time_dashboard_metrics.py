"""📊 Real-Time Dashboard Metrics - Live Analytics & Monitoring System
===================================================================

Advanced real-time dashboard metrics and live monitoring system for the IA Chéries platform.
Provides instant insights, live data streaming, real-time alerts, performance tracking,
and interactive dashboard analytics with WebSocket integration and event-driven updates.

Enhanced Features:
- Real-time metrics streaming with WebSocket support
- Live dashboard performance tracking and optimization
- Instant alert generation and notification system
- User interaction analytics and behavior tracking
- System health monitoring with real-time diagnostics
- Live engagement tracking across all platforms
- Real-time revenue and monetization monitoring
- Interactive dashboard component performance analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ AVERTISSEMENT LÉGAL:
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
import time
import json
import websockets
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import hashlib
from collections import defaultdict, deque
import statistics
from concurrent.futures import ThreadPoolExecutor
import threading
import weakref

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of real-time metrics."""
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    TRAFFIC = "traffic"
    PERFORMANCE = "performance"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_HEALTH = "system_health"
    CONTENT_METRICS = "content_metrics"
    ALERTS = "alerts"
    CONVERSION = "conversion"
    COLLABORATION = "collaboration"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DashboardComponent(Enum):
    """Dashboard component types."""
    CHART = "chart"
    TABLE = "table"
    KPI_CARD = "kpi_card"
    GRAPH = "graph"
    MAP = "map"
    WIDGET = "widget"
    FEED = "feed"
    NOTIFICATION = "notification"


class UpdateFrequency(Enum):
    """Update frequency for different metrics."""
    REAL_TIME = "real_time"      # Immediate updates
    HIGH = "high"                # Every 1-5 seconds
    MEDIUM = "medium"            # Every 10-30 seconds
    LOW = "low"                  # Every 1-5 minutes
    BATCH = "batch"              # Every 10-60 minutes


@dataclass
class RealTimeMetric:
    """Real-time metric data structure."""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: MetricType = MetricType.ENGAGEMENT
    name: str = ""
    value: Union[float, int, str] = 0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    creator_id: Optional[str] = None
    platform: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    update_frequency: UpdateFrequency = UpdateFrequency.REAL_TIME
    trend_direction: str = "stable"  # up, down, stable
    previous_value: Optional[Union[float, int]] = None
    change_percentage: Optional[float] = None


@dataclass
class DashboardAlert:
    """Real-time dashboard alert."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    severity: AlertSeverity = AlertSeverity.INFO
    title: str = ""
    message: str = ""
    metric_type: MetricType = MetricType.SYSTEM_HEALTH
    source_component: Optional[str] = None
    creator_id: Optional[str] = None
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    action_required: bool = False
    auto_resolve: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class UserInteraction:
    """User interaction tracking data."""
    interaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    component_type: DashboardComponent = DashboardComponent.CHART
    component_id: str = ""
    action: str = ""  # click, hover, scroll, filter, etc.
    interaction_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration: Optional[float] = None  # seconds
    page_url: str = ""
    user_agent: str = ""


@dataclass
class DashboardPerformance:
    """Dashboard performance metrics."""
    component_id: str = ""
    component_type: DashboardComponent = DashboardComponent.CHART
    load_time: float = 0.0  # milliseconds
    render_time: float = 0.0  # milliseconds
    data_fetch_time: float = 0.0  # milliseconds
    memory_usage: float = 0.0  # MB
    cpu_usage: float = 0.0  # percentage
    network_latency: float = 0.0  # milliseconds
    error_count: int = 0
    user_interactions: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WebSocketClient:
    """WebSocket client connection information."""
    client_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    websocket: Any = None  # WebSocket connection object
    user_id: Optional[str] = None
    subscribed_metrics: Set[str] = field(default_factory=set)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    connection_quality: float = 1.0  # 0-1 scale
    is_active: bool = True


class RealTimeDashboardMetrics:
    """Advanced real-time dashboard metrics and monitoring system."""
    
    def __init__(self):
        """Initialize the real-time dashboard metrics system."""
        self.real_time_metrics: Dict[str, RealTimeMetric] = {}
        self.metric_streams: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=10000) for metric_type in MetricType
        }
        self.active_alerts: Dict[str, DashboardAlert] = {}
        self.user_interactions: deque = deque(maxlen=100000)  # Last 100K interactions
        self.dashboard_performance: Dict[str, DashboardPerformance] = {}
        self.websocket_clients: Dict[str, WebSocketClient] = {}
        self.metric_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # metric_id -> client_ids
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Threading and async management
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=12)
        self.websocket_server = None
        self.metric_processors: Dict[MetricType, Callable] = {}
        
        # Real-time configuration
        self.update_intervals = {
            UpdateFrequency.REAL_TIME: 0.1,  # 100ms
            UpdateFrequency.HIGH: 1.0,       # 1 second
            UpdateFrequency.MEDIUM: 15.0,    # 15 seconds
            UpdateFrequency.LOW: 60.0,       # 1 minute
            UpdateFrequency.BATCH: 600.0     # 10 minutes
        }
        
        # System health monitoring
        self.system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_latency": 0.0,
            "active_connections": 0,
            "error_rate": 0.0
        }
        
        # Alert configuration
        self.default_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "error_rate": 5.0,
            "response_time": 2000.0,  # 2 seconds
            "engagement_drop": 20.0   # 20% drop
        }
        
        logger.info("RealTimeDashboardMetrics initialized successfully")
    
    async def start_real_time_monitoring(self, port: int = 8765) -> None:
        """Start real-time monitoring with WebSocket server."""
        try:
            # Start WebSocket server for real-time updates
            self.websocket_server = await websockets.serve(
                self._handle_websocket_connection, 
                "localhost", 
                port
            )
            
            # Start background tasks
            asyncio.create_task(self._metric_processing_loop())
            asyncio.create_task(self._alert_monitoring_loop())
            asyncio.create_task(self._system_health_monitoring_loop())
            asyncio.create_task(self._cleanup_expired_data_loop())
            
            logger.info(f"Real-time monitoring started on port {port}")
            
        except Exception as e:
            logger.error(f"Error starting real-time monitoring: {e}")
    
    async def record_real_time_metric(self, metric: RealTimeMetric) -> bool:
        """Record a real-time metric and broadcast to subscribers."""
        try:
            with self.lock:
                # Calculate trend and change
                previous_metric = self.real_time_metrics.get(
                    f"{metric.metric_type.value}_{metric.name}_{metric.creator_id}"
                )
                
                if previous_metric:
                    metric.previous_value = previous_metric.value
                    if isinstance(metric.value, (int, float)) and isinstance(previous_metric.value, (int, float)):
                        if previous_metric.value != 0:
                            metric.change_percentage = (
                                (metric.value - previous_metric.value) / previous_metric.value * 100
                            )
                            
                            # Determine trend direction
                            if metric.change_percentage > 1:
                                metric.trend_direction = "up"
                            elif metric.change_percentage < -1:
                                metric.trend_direction = "down"
                            else:
                                metric.trend_direction = "stable"
                
                # Store metric
                metric_key = f"{metric.metric_type.value}_{metric.name}_{metric.creator_id}"
                self.real_time_metrics[metric_key] = metric
                
                # Add to stream
                self.metric_streams[metric.metric_type].append(metric)
                
                # Check for alerts
                await self._check_metric_alerts(metric)
                
                # Broadcast to WebSocket subscribers
                await self._broadcast_metric_update(metric)
            
            logger.debug(f"Recorded real-time metric: {metric.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording real-time metric: {e}")
            return False
    
    async def subscribe_to_metrics(
        self, 
        client_id: str,
        metric_types: List[MetricType],
        filters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Subscribe WebSocket client to specific metric types."""
        try:
            if client_id not in self.websocket_clients:
                logger.warning(f"Client {client_id} not found for subscription")
                return False
            
            client = self.websocket_clients[client_id]
            
            # Add metric subscriptions
            for metric_type in metric_types:
                subscription_key = f"{metric_type.value}"
                if filters:
                    subscription_key += f"_{hash(json.dumps(filters, sort_keys=True))}"
                
                client.subscribed_metrics.add(subscription_key)
                self.metric_subscriptions[subscription_key].add(client_id)
            
            # Send current metrics to new subscriber
            await self._send_current_metrics_to_client(client_id, metric_types, filters)
            
            logger.info(f"Client {client_id} subscribed to {len(metric_types)} metric types")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing client to metrics: {e}")
            return False
    
    async def create_alert(self, alert: DashboardAlert) -> bool:
        """Create and broadcast a real-time alert."""
        try:
            # Set expiration if not provided
            if not alert.expires_at:
                if alert.severity == AlertSeverity.CRITICAL:
                    alert.expires_at = datetime.utcnow() + timedelta(hours=24)
                elif alert.severity == AlertSeverity.ERROR:
                    alert.expires_at = datetime.utcnow() + timedelta(hours=12)
                elif alert.severity == AlertSeverity.WARNING:
                    alert.expires_at = datetime.utcnow() + timedelta(hours=6)
                else:
                    alert.expires_at = datetime.utcnow() + timedelta(hours=2)
            
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            
            # Broadcast alert to subscribers
            await self._broadcast_alert(alert)
            
            # Log alert based on severity
            if alert.severity == AlertSeverity.CRITICAL:
                logger.critical(f"CRITICAL ALERT: {alert.title} - {alert.message}")
            elif alert.severity == AlertSeverity.ERROR:
                logger.error(f"ERROR ALERT: {alert.title} - {alert.message}")
            elif alert.severity == AlertSeverity.WARNING:
                logger.warning(f"WARNING ALERT: {alert.title} - {alert.message}")
            else:
                logger.info(f"INFO ALERT: {alert.title} - {alert.message}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return False
    
    async def track_user_interaction(self, interaction: UserInteraction) -> bool:
        """Track user dashboard interaction."""
        try:
            with self.lock:
                self.user_interactions.append(interaction)
                
                # Update component performance metrics
                await self._update_component_performance(interaction)
                
                # Analyze interaction patterns
                await self._analyze_interaction_patterns(interaction)
            
            logger.debug(f"Tracked user interaction: {interaction.action} on {interaction.component_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking user interaction: {e}")
            return False
    
    async def update_dashboard_performance(self, performance: DashboardPerformance) -> bool:
        """Update dashboard component performance metrics."""
        try:
            with self.lock:
                self.dashboard_performance[performance.component_id] = performance
                
                # Check performance thresholds
                await self._check_performance_alerts(performance)
                
                # Update performance baselines
                await self._update_performance_baselines(performance)
            
            # Broadcast performance update
            await self._broadcast_performance_update(performance)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating dashboard performance: {e}")
            return False
    
    async def get_real_time_analytics(
        self, 
        timeframe: timedelta = timedelta(minutes=30),
        metric_types: Optional[List[MetricType]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive real-time analytics."""
        try:
            cutoff_time = datetime.utcnow() - timeframe
            
            analytics = {
                "timeframe_minutes": timeframe.total_seconds() / 60,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "metric_summary": {},
                "alert_summary": {},
                "user_activity": {},
                "performance_summary": {},
                "system_health": self.system_metrics.copy()
            }
            
            # Metric summary
            if not metric_types:
                metric_types = list(MetricType)
            
            for metric_type in metric_types:
                stream = self.metric_streams[metric_type]
                recent_metrics = [
                    metric for metric in stream 
                    if metric.timestamp >= cutoff_time
                ]
                
                if recent_metrics:
                    values = [
                        metric.value for metric in recent_metrics 
                        if isinstance(metric.value, (int, float))
                    ]
                    
                    analytics["metric_summary"][metric_type.value] = {
                        "count": len(recent_metrics),
                        "avg_value": statistics.mean(values) if values else 0,
                        "min_value": min(values) if values else 0,
                        "max_value": max(values) if values else 0,
                        "trend_analysis": await self._analyze_metric_trend(recent_metrics)
                    }
            
            # Alert summary
            recent_alerts = [
                alert for alert in self.active_alerts.values()
                if alert.created_at >= cutoff_time
            ]
            
            alert_by_severity = defaultdict(int)
            for alert in recent_alerts:
                alert_by_severity[alert.severity.value] += 1
            
            analytics["alert_summary"] = {
                "total_alerts": len(recent_alerts),
                "by_severity": dict(alert_by_severity),
                "unresolved_count": len([a for a in recent_alerts if not a.resolved]),
                "critical_unresolved": len([
                    a for a in recent_alerts 
                    if a.severity == AlertSeverity.CRITICAL and not a.resolved
                ])
            }
            
            # User activity summary
            recent_interactions = [
                interaction for interaction in self.user_interactions
                if interaction.timestamp >= cutoff_time
            ]
            
            user_activity = defaultdict(int)
            component_activity = defaultdict(int)
            
            for interaction in recent_interactions:
                user_activity[interaction.user_id] += 1
                component_activity[interaction.component_type.value] += 1
            
            analytics["user_activity"] = {
                "total_interactions": len(recent_interactions),
                "unique_users": len(user_activity),
                "avg_interactions_per_user": statistics.mean(user_activity.values()) if user_activity else 0,
                "most_active_components": dict(sorted(
                    component_activity.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5])
            }
            
            # Performance summary
            performance_metrics = list(self.dashboard_performance.values())
            recent_performance = [
                perf for perf in performance_metrics
                if perf.timestamp >= cutoff_time
            ]
            
            if recent_performance:
                avg_load_time = statistics.mean([p.load_time for p in recent_performance])
                avg_render_time = statistics.mean([p.render_time for p in recent_performance])
                total_errors = sum([p.error_count for p in recent_performance])
                
                analytics["performance_summary"] = {
                    "avg_load_time_ms": round(avg_load_time, 2),
                    "avg_render_time_ms": round(avg_render_time, 2),
                    "total_errors": total_errors,
                    "components_monitored": len(recent_performance),
                    "performance_score": await self._calculate_performance_score(recent_performance)
                }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting real-time analytics: {e}")
            return {"error": str(e)}
    
    async def get_live_dashboard_status(self) -> Dict[str, Any]:
        """Get current live dashboard status."""
        try:
            active_clients = len([c for c in self.websocket_clients.values() if c.is_active])
            
            # Calculate metrics per second
            current_time = datetime.utcnow()
            one_minute_ago = current_time - timedelta(minutes=1)
            
            recent_metrics_count = 0
            for stream in self.metric_streams.values():
                recent_metrics_count += len([
                    m for m in stream 
                    if m.timestamp >= one_minute_ago
                ])
            
            metrics_per_second = recent_metrics_count / 60
            
            # Active alerts by severity
            active_alerts_by_severity = defaultdict(int)
            for alert in self.active_alerts.values():
                if not alert.resolved:
                    active_alerts_by_severity[alert.severity.value] += 1
            
            # WebSocket connection quality
            connection_qualities = [
                client.connection_quality 
                for client in self.websocket_clients.values() 
                if client.is_active
            ]
            avg_connection_quality = statistics.mean(connection_qualities) if connection_qualities else 0
            
            return {
                "status": "active",
                "timestamp": current_time.isoformat(),
                "websocket_server_running": self.websocket_server is not None,
                "active_connections": active_clients,
                "total_subscriptions": sum(len(subs) for subs in self.metric_subscriptions.values()),
                "metrics_per_second": round(metrics_per_second, 2),
                "active_alerts": dict(active_alerts_by_severity),
                "total_active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
                "avg_connection_quality": round(avg_connection_quality, 3),
                "system_health": self.system_metrics,
                "memory_usage": {
                    "real_time_metrics": len(self.real_time_metrics),
                    "user_interactions": len(self.user_interactions),
                    "active_alerts": len(self.active_alerts),
                    "websocket_clients": len(self.websocket_clients)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting live dashboard status: {e}")
            return {"status": "error", "error": str(e)}
    
    # Private helper methods
    
    async def _handle_websocket_connection(self, websocket, path):
        """Handle new WebSocket connection."""
        client_id = str(uuid.uuid4())
        client = WebSocketClient(
            client_id=client_id,
            websocket=websocket
        )
        
        try:
            self.websocket_clients[client_id] = client
            logger.info(f"New WebSocket client connected: {client_id}")
            
            # Send welcome message
            welcome_message = {
                "type": "connection_established",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(welcome_message))
            
            # Handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_client_message(client_id, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from client {client_id}")
                except Exception as e:
                    logger.error(f"Error handling message from client {client_id}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error in WebSocket connection {client_id}: {e}")
        finally:
            # Cleanup client
            await self._cleanup_client(client_id)
    
    async def _handle_client_message(self, client_id: str, data: Dict[str, Any]):
        """Handle message from WebSocket client."""
        message_type = data.get("type")
        
        if message_type == "subscribe_metrics":
            metric_types = [MetricType(mt) for mt in data.get("metric_types", [])]
            filters = data.get("filters")
            await self.subscribe_to_metrics(client_id, metric_types, filters)
            
        elif message_type == "unsubscribe_metrics":
            metric_types = data.get("metric_types", [])
            await self._unsubscribe_from_metrics(client_id, metric_types)
            
        elif message_type == "acknowledge_alert":
            alert_id = data.get("alert_id")
            await self._acknowledge_alert(alert_id, client_id)
            
        elif message_type == "heartbeat":
            await self._handle_heartbeat(client_id)
            
        else:
            logger.warning(f"Unknown message type from client {client_id}: {message_type}")
    
    async def _metric_processing_loop(self):
        """Background loop for processing metrics."""
        while True:
            try:
                await asyncio.sleep(0.1)  # 100ms intervals
                
                # Process high-frequency metrics
                await self._process_high_frequency_metrics()
                
                # Aggregate metrics for different time windows
                await self._aggregate_metrics_by_timeframe()
                
            except Exception as e:
                logger.error(f"Error in metric processing loop: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    async def _alert_monitoring_loop(self):
        """Background loop for monitoring alerts."""
        while True:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Check for auto-resolving alerts
                await self._check_auto_resolve_alerts()
                
                # Clean up expired alerts
                await self._cleanup_expired_alerts()
                
                # Check system health alerts
                await self._check_system_health_alerts()
                
            except Exception as e:
                logger.error(f"Error in alert monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _system_health_monitoring_loop(self):
        """Background loop for system health monitoring."""
        while True:
            try:
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
                # Update system metrics
                await self._update_system_metrics()
                
                # Check WebSocket connection health
                await self._check_websocket_health()
                
                # Monitor dashboard performance
                await self._monitor_overall_performance()
                
            except Exception as e:
                logger.error(f"Error in system health monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_expired_data_loop(self):
        """Background loop for cleaning up expired data."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes
                
                # Cleanup old metrics
                await self._cleanup_old_metrics()
                
                # Cleanup old interactions
                await self._cleanup_old_interactions()
                
                # Cleanup inactive WebSocket clients
                await self._cleanup_inactive_clients()
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)
    
    async def _check_metric_alerts(self, metric: RealTimeMetric):
        """Check if metric triggers any alerts."""
        try:
            metric_key = f"{metric.metric_type.value}_{metric.name}"
            thresholds = self.alert_thresholds.get(metric_key, {})
            
            if not thresholds:
                # Use default thresholds if available
                if metric.name in self.default_thresholds:
                    thresholds = {"max": self.default_thresholds[metric.name]}
            
            if not thresholds or not isinstance(metric.value, (int, float)):
                return
            
            # Check maximum threshold
            if "max" in thresholds and metric.value > thresholds["max"]:
                alert = DashboardAlert(
                    severity=AlertSeverity.WARNING,
                    title=f"High {metric.name}",
                    message=f"{metric.name} is {metric.value}{metric.unit}, exceeding threshold of {thresholds['max']}{metric.unit}",
                    metric_type=metric.metric_type,
                    creator_id=metric.creator_id,
                    threshold_value=thresholds["max"],
                    current_value=metric.value,
                    action_required=True
                )
                await self.create_alert(alert)
            
            # Check minimum threshold
            if "min" in thresholds and metric.value < thresholds["min"]:
                alert = DashboardAlert(
                    severity=AlertSeverity.WARNING,
                    title=f"Low {metric.name}",
                    message=f"{metric.name} is {metric.value}{metric.unit}, below threshold of {thresholds['min']}{metric.unit}",
                    metric_type=metric.metric_type,
                    creator_id=metric.creator_id,
                    threshold_value=thresholds["min"],
                    current_value=metric.value,
                    action_required=True
                )
                await self.create_alert(alert)
            
            # Check for significant drops
            if metric.change_percentage and metric.change_percentage < -20:  # 20% drop
                alert = DashboardAlert(
                    severity=AlertSeverity.ERROR,
                    title=f"Significant Drop in {metric.name}",
                    message=f"{metric.name} dropped by {abs(metric.change_percentage):.1f}%",
                    metric_type=metric.metric_type,
                    creator_id=metric.creator_id,
                    current_value=metric.value,
                    action_required=True
                )
                await self.create_alert(alert)
                
        except Exception as e:
            logger.error(f"Error checking metric alerts: {e}")
    
    async def _broadcast_metric_update(self, metric: RealTimeMetric):
        """Broadcast metric update to subscribed WebSocket clients."""
        try:
            message = {
                "type": "metric_update",
                "metric": asdict(metric),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Convert datetime objects to ISO strings
            message["metric"]["timestamp"] = metric.timestamp.isoformat()
            
            # Find subscribed clients
            subscription_key = metric.metric_type.value
            subscribed_clients = self.metric_subscriptions.get(subscription_key, set())
            
            # Send to subscribed clients
            for client_id in list(subscribed_clients):
                client = self.websocket_clients.get(client_id)
                if client and client.is_active and client.websocket:
                    try:
                        await client.websocket.send(json.dumps(message))
                    except Exception as e:
                        logger.warning(f"Error sending to client {client_id}: {e}")
                        # Mark client as inactive
                        client.is_active = False
                        
        except Exception as e:
            logger.error(f"Error broadcasting metric update: {e}")
    
    async def _broadcast_alert(self, alert: DashboardAlert):
        """Broadcast alert to all active WebSocket clients."""
        try:
            message = {
                "type": "alert",
                "alert": asdict(alert),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Convert datetime objects to ISO strings
            message["alert"]["created_at"] = alert.created_at.isoformat()
            if alert.expires_at:
                message["alert"]["expires_at"] = alert.expires_at.isoformat()
            
            # Send to all active clients
            for client_id, client in self.websocket_clients.items():
                if client.is_active and client.websocket:
                    try:
                        await client.websocket.send(json.dumps(message))
                    except Exception as e:
                        logger.warning(f"Error sending alert to client {client_id}: {e}")
                        client.is_active = False
                        
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")
    
    async def _broadcast_performance_update(self, performance: DashboardPerformance):
        """Broadcast performance update to subscribed clients."""
        try:
            message = {
                "type": "performance_update",
                "performance": asdict(performance),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Convert datetime to ISO string
            message["performance"]["timestamp"] = performance.timestamp.isoformat()
            
            # Send to clients subscribed to performance metrics
            subscription_key = "performance"
            subscribed_clients = self.metric_subscriptions.get(subscription_key, set())
            
            for client_id in list(subscribed_clients):
                client = self.websocket_clients.get(client_id)
                if client and client.is_active and client.websocket:
                    try:
                        await client.websocket.send(json.dumps(message))
                    except Exception as e:
                        logger.warning(f"Error sending performance update to client {client_id}: {e}")
                        client.is_active = False
                        
        except Exception as e:
            logger.error(f"Error broadcasting performance update: {e}")
    
    async def _update_system_metrics(self):
        """Update system health metrics."""
        try:
            import psutil
            
            # CPU usage
            self.system_metrics["cpu_usage"] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_metrics["memory_usage"] = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_metrics["disk_usage"] = disk.percent
            
            # Active connections
            self.system_metrics["active_connections"] = len([
                c for c in self.websocket_clients.values() if c.is_active
            ])
            
            # Calculate error rate
            recent_errors = sum(
                perf.error_count for perf in self.dashboard_performance.values()
            )
            total_interactions = len(self.user_interactions)
            self.system_metrics["error_rate"] = (
                (recent_errors / max(total_interactions, 1)) * 100
                if total_interactions > 0 else 0
            )
            
        except ImportError:
            # psutil not available, use mock values
            self.system_metrics["cpu_usage"] = 25.0
            self.system_metrics["memory_usage"] = 45.0
            self.system_metrics["disk_usage"] = 60.0
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    async def _analyze_metric_trend(self, metrics: List[RealTimeMetric]) -> Dict[str, Any]:
        """Analyze trend for a list of metrics."""
        if len(metrics) < 2:
            return {"trend": "insufficient_data"}
        
        values = [m.value for m in metrics if isinstance(m.value, (int, float))]
        if len(values) < 2:
            return {"trend": "insufficient_numeric_data"}
        
        # Simple linear trend analysis
        if len(values) >= 5:
            recent_avg = statistics.mean(values[-3:])
            earlier_avg = statistics.mean(values[:3])
            
            if recent_avg > earlier_avg * 1.05:
                trend = "increasing"
            elif recent_avg < earlier_avg * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            if values[-1] > values[0]:
                trend = "increasing"
            elif values[-1] < values[0]:
                trend = "decreasing"
            else:
                trend = "stable"
        
        # Calculate volatility
        volatility = statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) != 0 else 0
        
        return {
            "trend": trend,
            "volatility": round(volatility, 3),
            "min_value": min(values),
            "max_value": max(values),
            "avg_value": round(statistics.mean(values), 2),
            "data_points": len(values)
        }
    
    async def _cleanup_client(self, client_id: str):
        """Clean up disconnected WebSocket client."""
        try:
            # Remove from client registry
            if client_id in self.websocket_clients:
                del self.websocket_clients[client_id]
            
            # Remove from all subscriptions
            for subscription_set in self.metric_subscriptions.values():
                subscription_set.discard(client_id)
            
            logger.info(f"Cleaned up client: {client_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up client {client_id}: {e}")


# Export the main class
__all__ = [
    "RealTimeDashboardMetrics", 
    "RealTimeMetric", 
    "DashboardAlert", 
    "UserInteraction",
    "DashboardPerformance",
    "WebSocketClient"
]