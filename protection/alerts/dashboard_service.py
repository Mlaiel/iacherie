"""📊 Alert Dashboard Service
========================

Real-time dashboard service for alert visualization, monitoring, and management.
Provides WebSocket connections, real-time updates, and interactive analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import pandas as pd

from ..models.alert_models import Alert, AlertSeverity, AlertType, AlertStatus
from ..models.dashboard_models import (
    DashboardWidget, DashboardLayout, UserPreferences,
    AlertMetrics, PlatformMetrics, TimeSeriesData
)
from ...core.database import get_async_session
from ...core.cache import CacheManager

logger = logging.getLogger(__name__)

class WidgetType(str, Enum):
    """
Dashboard widget types."""

    ALERT_COUNT = "alert_count"
    SEVERITY_DISTRIBUTION = "severity_distribution"
    PLATFORM_BREAKDOWN = "platform_breakdown"
    TIMELINE_CHART = "timeline_chart"
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    TOP_VIOLATIONS = "top_violations"
    GEOGRAPHICAL_MAP = "geographical_map"
    REAL_TIME_FEED = "real_time_feed"
    ESCALATION_FUNNEL = "escalation_funnel"

class UpdateType(str, Enum):
    """Real-time update types."""

    NEW_ALERT = "new_alert"
    ALERT_UPDATE = "alert_update"
    ALERT_RESOLVED = "alert_resolved"
    METRICS_UPDATE = "metrics_update"
    SYSTEM_STATUS = "system_status"

@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    max_connections: int = 1000
    update_interval_seconds: int = 5
    metrics_retention_hours: int = 24
    real_time_alerts_limit: int = 100
    cache_ttl_seconds: int = 300

@dataclass
class ConnectionInfo:
    """
WebSocket connection information."""
    websocket: WebSocket
    user_id: str
    connection_id: str
    subscribed_widgets: Set[str] = field(default_factory=set)
    last_activity: datetime = field(default_factory=datetime.utcnow)

class WebSocketManager:
    """
Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, ConnectionInfo] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self._connection_lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """
Connect a new WebSocket client."""
        await websocket.accept()
        
        connection_id = str(uuid4())
        connection_info = ConnectionInfo(
            websocket=websocket,
            user_id=user_id,
            connection_id=connection_id
        )
        
        async with self._connection_lock:
            self.active_connections[connection_id] = connection_info
            
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        logger.info("WebSocket connected: %s for user %s", connection_id, user_id)
        return connection_id
    
    async def disconnect(self, connection_id: str) -> None:
        """Disconnect a WebSocket client."""
        async with self._connection_lock:
            if connection_id in self.active_connections:
                connection_info = self.active_connections[connection_id]
                user_id = connection_info.user_id
                
                # Remove from active connections
                del self.active_connections[connection_id]
                
                # Remove from user connections
                if user_id in self.user_connections:
                    self.user_connections[user_id].discard(connection_id)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]
                
                logger.info("WebSocket disconnected: %s", connection_id)
    
    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            try:
                connection_info = self.active_connections[connection_id]
                await connection_info.websocket.send_text(json.dumps(message))
                connection_info.last_activity = datetime.utcnow()
            except Exception as e:
                logger.error("Failed to send message to %s: %s", connection_id, str(e))
                await self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> None:
        """Send message to all connections of a user."""
        if user_id in self.user_connections:
            connection_ids = list(self.user_connections[user_id])
            for connection_id in connection_ids:
                await self.send_personal_message(connection_id, message)
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
Broadcast message to all connections."""
        connection_ids = list(self.active_connections.keys())
        for connection_id in connection_ids:
            await self.send_personal_message(connection_id, message)
    
    async def subscribe_to_widget(self, connection_id: str, widget_id: str) -> None:
        """
Subscribe connection to widget updates."""
        if connection_id in self.active_connections:
            self.active_connections[connection_id].subscribed_widgets.add(widget_id)
    
    async def unsubscribe_from_widget(self, connection_id: str, widget_id: str) -> None:
        """
Unsubscribe connection from widget updates."""
        if connection_id in self.active_connections:
            self.active_connections[connection_id].subscribed_widgets.discard(widget_id)
    
    async def send_widget_update(self, widget_id: str, data: Dict[str, Any]) -> None:
        """
Send update to all connections subscribed to a widget."""
        message = {
            "type": "widget_update",
            "widget_id": widget_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for connection_info in self.active_connections.values():
            if widget_id in connection_info.subscribed_widgets:
                await self.send_personal_message(connection_info.connection_id, message)
    
    async def cleanup_stale_connections(self) -> None:
        """Clean up stale connections."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        stale_connections = []
        
        for connection_id, connection_info in self.active_connections.items():
            if connection_info.last_activity < cutoff_time:
                stale_connections.append(connection_id)
        
        for connection_id in stale_connections:
            await self.disconnect(connection_id)
        
        if stale_connections:
            logger.info("Cleaned up %d stale connections", len(stale_connections))

class MetricsCalculator:
    """Calculates dashboard metrics and analytics."""
    
    def __init__(self, cache_manager: CacheManager):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def get_alert_metrics(
        self,
        user_id: Optional[str] = None,
        time_range: timedelta = timedelta(hours=24)
    ) -> AlertMetrics:
        """
Calculate alert metrics."""
        try:
            cache_key = f"alert_metrics:{user_id or 'all'}:{time_range.total_seconds()}"
            cached_metrics = await self.cache_manager.get(cache_key)
            
            if cached_metrics:
                return AlertMetrics(**cached_metrics)
            
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            async with get_async_session() as session:
                # Base query
                query = select(Alert).where(Alert.created_at.between(start_time, end_time))
                
                if user_id:
                    query = query.where(Alert.user_id == user_id)
                
                result = await session.execute(query)
                alerts = list(result.scalars().all())
                
                # Calculate metrics
                total_alerts = len(alerts)
                resolved_alerts = sum(1 for a in alerts if a.status == AlertStatus.RESOLVED)
                pending_alerts = sum(1 for a in alerts if a.status == AlertStatus.PENDING)
                escalated_alerts = sum(1 for a in alerts if a.status == AlertStatus.ESCALATED)
                
                # Severity distribution
                severity_counts = {}
                for alert in alerts:
                    severity = alert.severity.value
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Platform distribution
                platform_counts = {}
                for alert in alerts:
                    platform = alert.platform
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                # Response time calculation
                response_times = []
                for alert in alerts:
                    if alert.resolved_at and alert.created_at:
                        response_time = (alert.resolved_at - alert.created_at).total_seconds()
                        response_times.append(response_time)
                
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                
                metrics = AlertMetrics(
                    total_alerts=total_alerts,
                    resolved_alerts=resolved_alerts,
                    pending_alerts=pending_alerts,
                    escalated_alerts=escalated_alerts,
                    resolution_rate=resolved_alerts / total_alerts if total_alerts > 0 else 0,
                    average_response_time=avg_response_time,
                    severity_distribution=severity_counts,
                    platform_distribution=platform_counts,
                    time_range_hours=time_range.total_seconds() / 3600,
                    calculated_at=datetime.utcnow()
                )
                
                # Cache metrics
                await self.cache_manager.set(cache_key, metrics.dict(), ttl=300)
                
                return metrics
                
        except Exception as e:
            logger.error("Failed to calculate alert metrics: %s", str(e))
            return AlertMetrics()
    
    async def get_platform_metrics(
        self,
        user_id: Optional[str] = None,
        time_range: timedelta = timedelta(hours=24)
    ) -> List[PlatformMetrics]:
        """Calculate platform-specific metrics."""
        try:
            cache_key = f"platform_metrics:{user_id or 'all'}:{time_range.total_seconds()}"
            cached_metrics = await self.cache_manager.get(cache_key)
            
            if cached_metrics:
                return [PlatformMetrics(**m) for m in cached_metrics]
            
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            async with get_async_session() as session:
                # Query alerts grouped by platform
                query = select(
                    Alert.platform,
                    func.count(Alert.id).label('total_alerts'),
                    func.count(Alert.id).filter(Alert.status == AlertStatus.RESOLVED).label('resolved'),
                    func.avg(Alert.confidence_score).label('avg_confidence')
                ).where(
                    Alert.created_at.between(start_time, end_time)
                ).group_by(Alert.platform)
                
                if user_id:
                    query = query.where(Alert.user_id == user_id)
                
                result = await session.execute(query)
                platform_data = result.fetchall()
                
                metrics_list = []
                for row in platform_data:
                    platform_metrics = PlatformMetrics(
                        platform=row.platform,
                        total_alerts=row.total_alerts,
                        resolved_alerts=row.resolved or 0,
                        resolution_rate=(row.resolved or 0) / row.total_alerts if row.total_alerts > 0 else 0,
                        average_confidence=float(row.avg_confidence or 0),
                        calculated_at=datetime.utcnow()
                    )
                    metrics_list.append(platform_metrics)
                
                # Cache metrics
                metrics_data = [m.dict() for m in metrics_list]
                await self.cache_manager.set(cache_key, metrics_data, ttl=300)
                
                return metrics_list
                
        except Exception as e:
            logger.error("Failed to calculate platform metrics: %s", str(e))
            return []
    
    async def get_timeline_data(
        self,
        user_id: Optional[str] = None,
        time_range: timedelta = timedelta(hours=24),
        interval_minutes: int = 60
    ) -> TimeSeriesData:
        """Get timeline data for charts."""
        try:
            cache_key = f"timeline_data:{user_id or 'all'}:{time_range.total_seconds()}:{interval_minutes}"
            cached_data = await self.cache_manager.get(cache_key)
            
            if cached_data:
                return TimeSeriesData(**cached_data)
            
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            # Generate time intervals
            intervals = []
            current_time = start_time
            while current_time < end_time:
                intervals.append(current_time)
                current_time += timedelta(minutes=interval_minutes)
            
            async with get_async_session() as session:
                # Query alerts
                query = select(Alert).where(Alert.created_at.between(start_time, end_time))
                
                if user_id:
                    query = query.where(Alert.user_id == user_id)
                
                result = await session.execute(query)
                alerts = list(result.scalars().all())
                
                # Group alerts by time intervals
                data_points = []
                labels = []
                
                for i, interval_start in enumerate(intervals):
                    interval_end = interval_start + timedelta(minutes=interval_minutes)
                    
                    # Count alerts in this interval
                    interval_alerts = [
                        a for a in alerts
                        if interval_start <= a.created_at < interval_end
                    ]
                    
                    data_points.append(len(interval_alerts))
                    labels.append(interval_start.strftime("%H:%M"))
                
                timeline_data = TimeSeriesData(
                    labels=labels,
                    data_points=data_points,
                    start_time=start_time,
                    end_time=end_time,
                    interval_minutes=interval_minutes,
                    total_data_points=len(data_points)
                )
                
                # Cache data
                await self.cache_manager.set(cache_key, timeline_data.dict(), ttl=300)
                
                return timeline_data
                
        except Exception as e:
            logger.error("Failed to get timeline data: %s", str(e))
            return TimeSeriesData()

class DashboardService:
    """
    Main dashboard service for real-time alert monitoring and analytics.
    """
    
    def __init__(
        self,
        config: DashboardConfig,
        cache_manager: CacheManager,
        redis_client: redis.Redis
    ):
        self.config = config
        self.cache_manager = cache_manager
        self.redis_client = redis_client
        
        # WebSocket management
        self.websocket_manager = WebSocketManager()
        
        # Metrics calculator
        self.metrics_calculator = MetricsCalculator(cache_manager)
        
        # Background tasks
        self._is_running = False
        self._background_tasks: List[asyncio.Task] = []
        
        logger.info("DashboardService initialized")

    async def start(self) -> None:
        """Start the dashboard service."""
        if self._is_running:
            return
            
        self._is_running = True
        
        # Start background tasks
        self._background_tasks = [
            asyncio.create_task(self._metrics_updater()),
            asyncio.create_task(self._connection_cleaner()),
            asyncio.create_task(self._alert_broadcaster())
        ]
        
        logger.info("DashboardService started")

    async def stop(self) -> None:
        """Stop the dashboard service."""
        self._is_running = False
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()
        
        logger.info("DashboardService stopped")

    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str) -> None:
        """Handle WebSocket connection lifecycle."""
        connection_id = await self.websocket_manager.connect(websocket, user_id)
        
        try:
            # Send initial data
            await self._send_initial_dashboard_data(connection_id, user_id)
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_websocket_message(connection_id, message)
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received from %s", connection_id)
                except Exception as e:
                    logger.error("WebSocket error for %s: %s", connection_id, str(e))
                    break
        
        finally:
            await self.websocket_manager.disconnect(connection_id)

    async def notify_alert_update(self, alert: Alert, update_type: UpdateType) -> None:
        """Notify all relevant connections about alert updates."""
        try:
            message = {
                "type": update_type.value,
                "alert": {
                    "id": alert.id,
                    "type": alert.type.value,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "platform": alert.platform,
                    "status": alert.status.value,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                    "updated_at": alert.updated_at.isoformat() if alert.updated_at else None
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to user's connections
            await self.websocket_manager.send_to_user(alert.user_id, message)
            
            # Update relevant widgets
            await self._update_widgets_for_alert(alert, update_type)
            
        except Exception as e:
            logger.error("Failed to notify alert update: %s", str(e))

    async def get_dashboard_layout(self, user_id: str) -> Optional[DashboardLayout]:
        """Get user's dashboard layout."""
        try:
            cache_key = f"dashboard_layout:{user_id}"
            cached_layout = await self.cache_manager.get(cache_key)
            
            if cached_layout:
                return DashboardLayout(**cached_layout)
            
            # Query database for user's layout
            async with get_async_session() as session:
                result = await session.execute(
                    select(DashboardLayout).where(DashboardLayout.user_id == user_id)
                )
                layout = result.scalar_one_or_none()
                
                if layout:
                    # Cache layout
                    await self.cache_manager.set(cache_key, layout.dict(), ttl=1800)
                
                return layout
                
        except Exception as e:
            logger.error("Failed to get dashboard layout: %s", str(e))
            return None

    async def save_dashboard_layout(self, user_id: str, layout: Dict[str, Any]) -> bool:
        """Save user's dashboard layout."""
        try:
            async with get_async_session() as session:
                # Check if layout exists
                result = await session.execute(
                    select(DashboardLayout).where(DashboardLayout.user_id == user_id)
                )
                existing_layout = result.scalar_one_or_none()
                
                if existing_layout:
                    # Update existing layout
                    existing_layout.widgets = layout.get("widgets", [])
                    existing_layout.preferences = layout.get("preferences", {})
                    existing_layout.updated_at = datetime.utcnow()
                else:
                    # Create new layout
                    new_layout = DashboardLayout(
                        id=str(uuid4()),
                        user_id=user_id,
                        widgets=layout.get("widgets", []),
                        preferences=layout.get("preferences", {}),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(new_layout)
                
                await session.commit()
                
                # Clear cache
                await self.cache_manager.delete(f"dashboard_layout:{user_id}")
                
                return True
                
        except Exception as e:
            logger.error("Failed to save dashboard layout: %s", str(e))
            return False

    async def get_widget_data(self, widget_type: WidgetType, user_id: str, **kwargs) -> Dict[str, Any]:
        """Get data for specific widget type."""
        try:
            if widget_type == WidgetType.ALERT_COUNT:
                metrics = await self.metrics_calculator.get_alert_metrics(user_id)
                return {
                    "total": metrics.total_alerts,
                    "resolved": metrics.resolved_alerts,
                    "pending": metrics.pending_alerts,
                    "escalated": metrics.escalated_alerts
                }
            
            elif widget_type == WidgetType.SEVERITY_DISTRIBUTION:
                metrics = await self.metrics_calculator.get_alert_metrics(user_id)
                return {
                    "distribution": metrics.severity_distribution,
                    "total": metrics.total_alerts
                }
            
            elif widget_type == WidgetType.PLATFORM_BREAKDOWN:
                platform_metrics = await self.metrics_calculator.get_platform_metrics(user_id)
                return {
                    "platforms": [
                        {
                            "name": pm.platform,
                            "total": pm.total_alerts,
                            "resolved": pm.resolved_alerts,
                            "resolution_rate": pm.resolution_rate
                        }
                        for pm in platform_metrics
                    ]
                }
            
            elif widget_type == WidgetType.TIMELINE_CHART:
                time_range = timedelta(hours=kwargs.get("hours", 24))
                timeline_data = await self.metrics_calculator.get_timeline_data(user_id, time_range)
                return {
                    "labels": timeline_data.labels,
                    "data": timeline_data.data_points,
                    "interval_minutes": timeline_data.interval_minutes
                }
            
            elif widget_type == WidgetType.RESPONSE_TIME:
                metrics = await self.metrics_calculator.get_alert_metrics(user_id)
                return {
                    "average_response_time": metrics.average_response_time,
                    "resolution_rate": metrics.resolution_rate
                }
            
            elif widget_type == WidgetType.REAL_TIME_FEED:
                return await self._get_real_time_alerts(user_id)
            
            else:
                return {"error": f"Unsupported widget type: {widget_type}"}
                
        except Exception as e:
            logger.error("Failed to get widget data for %s: %s", widget_type, str(e))
            return {"error": str(e)}

    async def _send_initial_dashboard_data(self, connection_id: str, user_id: str) -> None:
        """Send initial dashboard data to new connection."""
        try:
            # Get dashboard layout
            layout = await self.get_dashboard_layout(user_id)
            
            # Get metrics
            metrics = await self.metrics_calculator.get_alert_metrics(user_id)
            
            initial_data = {
                "type": "initial_data",
                "layout": layout.dict() if layout else None,
                "metrics": metrics.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.websocket_manager.send_personal_message(connection_id, initial_data)
            
        except Exception as e:
            logger.error("Failed to send initial dashboard data: %s", str(e))

    async def _handle_websocket_message(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle incoming WebSocket message."""
        try:
            message_type = message.get("type")
            
            if message_type == "subscribe_widget":
                widget_id = message.get("widget_id")
                if widget_id:
                    await self.websocket_manager.subscribe_to_widget(connection_id, widget_id)
            
            elif message_type == "unsubscribe_widget":
                widget_id = message.get("widget_id")
                if widget_id:
                    await self.websocket_manager.unsubscribe_from_widget(connection_id, widget_id)
            
            elif message_type == "request_widget_data":
                widget_type = message.get("widget_type")
                if widget_type:
                    connection_info = self.websocket_manager.active_connections.get(connection_id)
                    if connection_info:
                        widget_data = await self.get_widget_data(
                            WidgetType(widget_type),
                            connection_info.user_id,
                            **message.get("params", {})
                        )
                        
                        response = {
                            "type": "widget_data",
                            "widget_type": widget_type,
                            "data": widget_data,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        await self.websocket_manager.send_personal_message(connection_id, response)
            
        except Exception as e:
            logger.error("Failed to handle WebSocket message: %s", str(e))

    async def _metrics_updater(self) -> None:
        """Background task to update metrics."""
        while self._is_running:
            try:
                # Update metrics for all active users
                active_users = set()
                for connection_info in self.websocket_manager.active_connections.values():
                    active_users.add(connection_info.user_id)
                
                for user_id in active_users:
                    # Update user metrics
                    metrics = await self.metrics_calculator.get_alert_metrics(user_id)
                    
                    # Send to subscribed widgets
                    await self.websocket_manager.send_widget_update(
                        "alert_metrics",
                        metrics.dict()
                    )
                
                await asyncio.sleep(self.config.update_interval_seconds)
                
            except Exception as e:
                logger.error("Metrics updater error: %s", str(e))
                await asyncio.sleep(10)

    async def _connection_cleaner(self) -> None:
        """Background task to clean up stale connections."""
        while self._is_running:
            try:
                await self.websocket_manager.cleanup_stale_connections()
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error("Connection cleaner error: %s", str(e))
                await asyncio.sleep(60)

    async def _alert_broadcaster(self) -> None:
        """Background task to broadcast alert updates."""
        while self._is_running:
            try:
                # Listen for alert updates from Redis
                pubsub = self.redis_client.pubsub()
                await pubsub.subscribe("alert_updates")
                
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            alert_data = json.loads(message["data"])
                            await self._process_alert_broadcast(alert_data)
                        except Exception as e:
                            logger.error("Failed to process alert broadcast: %s", str(e))
                
            except Exception as e:
                logger.error("Alert broadcaster error: %s", str(e))
                await asyncio.sleep(10)

    async def _process_alert_broadcast(self, alert_data: Dict[str, Any]) -> None:
        """Process alert broadcast message."""
        try:
            update_type = UpdateType(alert_data.get("type", "alert_update"))
            alert_info = alert_data.get("alert", {})
            
            # Create message for WebSocket clients
            message = {
                "type": update_type.value,
                "alert": alert_info,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to relevant user connections
            user_id = alert_info.get("user_id")
            if user_id:
                await self.websocket_manager.send_to_user(user_id, message)
            
        except Exception as e:
            logger.error("Failed to process alert broadcast: %s", str(e))

    async def _update_widgets_for_alert(self, alert: Alert, update_type: UpdateType) -> None:
        """Update widgets based on alert changes."""
        try:
            # Update alert count widget
            metrics = await self.metrics_calculator.get_alert_metrics(alert.user_id)
            await self.websocket_manager.send_widget_update(
                "alert_count",
                {
                    "total": metrics.total_alerts,
                    "resolved": metrics.resolved_alerts,
                    "pending": metrics.pending_alerts
                }
            )
            
            # Update real-time feed
            real_time_data = await self._get_real_time_alerts(alert.user_id)
            await self.websocket_manager.send_widget_update(
                "real_time_feed",
                real_time_data
            )
            
        except Exception as e:
            logger.error("Failed to update widgets: %s", str(e))

    async def _get_real_time_alerts(self, user_id: str) -> Dict[str, Any]:
        """Get recent alerts for real-time feed."""
        try:
            async with get_async_session() as session:
                result = await session.execute(
                    select(Alert)
                    .where(Alert.user_id == user_id)
                    .order_by(Alert.created_at.desc())
                    .limit(self.config.real_time_alerts_limit)
                )
                
                alerts = list(result.scalars().all())
                
                return {
                    "alerts": [
                        {
                            "id": alert.id,
                            "title": alert.title,
                            "severity": alert.severity.value,
                            "platform": alert.platform,
                            "status": alert.status.value,
                            "created_at": alert.created_at.isoformat() if alert.created_at else None
                        }
                        for alert in alerts
                    ],
                    "total": len(alerts)
                }
                
        except Exception as e:
            logger.error("Failed to get real-time alerts: %s", str(e))
            return {"alerts": [], "total": 0}
