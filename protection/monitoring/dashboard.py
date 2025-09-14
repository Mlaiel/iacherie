"""📈 Monitoring Dashboard Controller
=================================

Advanced dashboard controller for real-time monitoring visualization.
Provides API endpoints for dashboard components and real-time data feeds.

Technical Specifications:
- Real-time WebSocket data streaming
- RESTful API for dashboard components
- Customizable dashboard widgets
- Performance metrics visualization
- Interactive analytics interface

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.
Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum

# Optional websockets import with fallback
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None

# Optional FastAPI imports with fallbacks
try:
    from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
    from fastapi.responses import StreamingResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Simple fallback classes
    class APIRouter:
    """APIRouter: class implementation"""
        def __init__(self, *args, **kwargs) -> None:
            self.prefix = kwargs.get('prefix', '')
            self.tags = kwargs.get('tags', [])
        def get(self, path) -> None: 
            def decorator(func) -> None: return func
            return decorator
        def post(self, path) -> None:
            def decorator(func) -> None: return func
            return decorator
        def put(self, path) -> None:
            def decorator(func) -> None: return func
            return decorator
        def delete(self, path) -> None:
            def decorator(func) -> None: return func
            return decorator
        def websocket(self, path) -> None:
            def decorator(func) -> None: return func
            return decorator
    class HTTPException(Exception): 
    """HTTPException class implementation"""
        def __init__(self, *args, **kwargs) -> None:
            super().__init__()
    class WebSocket: pass
    class WebSocketDisconnect(Exception): pass
    def Depends(*args, **kwargs) -> None: return None
    class StreamingResponse: pass

# Optional pydantic import with fallback
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    class BaseModel:
    """BaseModel: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
    def Field(*args, **kwargs) -> None:
        return None

# Optional SQLAlchemy import with fallback
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    AsyncSession = None

from .realtime_monitor import RealTimeMonitor, MonitoringPriority, ThreatLevel
from .analytics import MonitoringAnalytics, AnalyticsTimeRange, AnalyticsReport
from .performance_optimizer import PerformanceOptimizer, OptimizationTarget

logger = logging.getLogger(__name__)

class DashboardWidgetType(str, Enum):
    """
Types of dashboard widgets."""

    METRICS_CHART = "metrics_chart"
    THREAT_MAP = "threat_map"
    PLATFORM_STATUS = "platform_status"
    PERFORMANCE_GAUGE = "performance_gauge"
    VIOLATION_FEED = "violation_feed"
    ANALYTICS_TABLE = "analytics_table"
    SYSTEM_HEALTH = "system_health"
    REVENUE_TRACKER = "revenue_tracker"
    ALERT_CENTER = "alert_center"
    OPTIMIZATION_PANEL = "optimization_panel"

class DashboardLayout(str, Enum):
    """Dashboard layout types."""

    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    SECURITY = "security"
    ANALYTICS = "analytics"
    CUSTOM = "custom"

class TimeRange(str, Enum):
    """Time range options for dashboard data."""

    LAST_HOUR = "1h"
    LAST_6_HOURS = "6h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    CUSTOM = "custom"

class DashboardWidget(BaseModel):
    """Dashboard widget configuration."""
    widget_id: str
    widget_type: DashboardWidgetType
    title: str
    position: Dict[str, int] = Field(default_factory=dict)  # x, y, width, height
    config: Dict[str, Any] = Field(default_factory=dict)
    data_source: str = ""
    refresh_interval: int = Field(default=30, ge=5, le=300)  # seconds
    visible: bool = True
    user_permissions: List[str] = Field(default_factory=list)

class DashboardConfig(BaseModel):
    """Dashboard configuration."""
    dashboard_id: str
    user_id: int
    layout_type: DashboardLayout
    widgets: List[DashboardWidget]
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RealtimeData(BaseModel):
    """
Real-time dashboard data structure."""
    timestamp: datetime
    widget_id: str
    data_type: str
    data: Dict[str, Any]
    user_id: Optional[int] = None

class DashboardMetrics(BaseModel):
    """
Dashboard metrics summary."""
    total_violations: int = 0
    active_sessions: int = 0
    threat_level_distribution: Dict[str, int] = Field(default_factory=dict)
    platform_coverage: Dict[str, int] = Field(default_factory=dict)
    system_health_score: float = 100.0
    response_time_avg: float = 0.0
    detection_rate: float = 0.0
    false_positive_rate: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ConnectionManager:
    """
Manage WebSocket connections for real-time updates."""
    
    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, List[str]] = {}
        self.connection_subscriptions: Dict[str, List[str]] = {}
    
    async def connect(self, websocket -> None: WebSocket, connection_id -> None: str, user_id -> None: int) -> None:
        """
Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        logger.info(f"WebSocket connection established: {connection_id} for user {user_id}")
    
    def disconnect(self, connection_id -> None: str, user_id -> None: int) -> None:
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id] = [
                conn_id for conn_id in self.user_connections[user_id] 
                if conn_id != connection_id
            ]
            
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        if connection_id in self.connection_subscriptions:
            del self.connection_subscriptions[connection_id]
        
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def send_personal_message(self, message -> None: dict, connection_id -> None: str) -> None:
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                # Remove broken connection
                for user_id, conn_ids in self.user_connections.items():
                    if connection_id in conn_ids:
                        self.disconnect(connection_id, user_id)
                        break
    
    async def send_user_message(self, message -> None: dict, user_id -> None: int) -> None:
        """Send message to all connections for a user."""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message -> None: dict) -> None:
        """
Broadcast message to all connections."""
        for connection_id in self.active_connections:
            await self.send_personal_message(message, connection_id)
    
    def subscribe_to_data(self, connection_id -> None: str, data_types -> None: List[str]) -> None:
        """
Subscribe connection to specific data types."""
        self.connection_subscriptions[connection_id] = data_types
    
    async def send_to_subscribers(self, data_type -> None: str, message -> None: dict) -> None:
        """
Send message to connections subscribed to data type."""
        for connection_id, subscriptions in self.connection_subscriptions.items():
            if data_type in subscriptions:
                await self.send_personal_message(message, connection_id)

class DashboardController:
    """
    Advanced dashboard controller for monitoring system.
    
    Provides comprehensive dashboard functionality including:
    - Real-time WebSocket data streaming
    - RESTful API for dashboard components
    - Customizable dashboard layouts and widgets
    - Interactive analytics and visualizations
    - Performance metrics and system health monitoring
    """
    
    def __init__(
        self,
        realtime_monitor -> None: RealTimeMonitor,
        analytics -> None: MonitoringAnalytics,
        performance_optimizer -> None: PerformanceOptimizer
    ) -> None:
        """
        Initialize dashboard controller.
        
        Args:
            realtime_monitor: Real-time monitoring service
            analytics: Analytics service
            performance_optimizer: Performance optimization service
        """
        self.realtime_monitor = realtime_monitor
        self.analytics = analytics
        self.performance_optimizer = performance_optimizer
        
        # Connection management
        self.connection_manager = ConnectionManager()
        
        # Dashboard state
        self._initialized = False
        self._dashboard_configs = {}
        self._widget_cache = {}
        
        # Real-time data streaming
        self._streaming_tasks = {}
        self._data_streams = {}
        
        # API router
        self.router = APIRouter(prefix="/dashboard", tags=["dashboard"])
        self._setup_routes()
        
        logger.info("Dashboard Controller initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize the dashboard controller.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Dashboard Controller...")
            
            # Load default dashboard configurations
            await self._load_default_configurations()
            
            # Start real-time data streaming
            await self._start_data_streaming()
            
            # Initialize widget cache
            await self._initialize_widget_cache()
            
            self._initialized = True
            logger.info("Dashboard Controller initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Dashboard Controller: {e}")
            return False
    
    async def get_dashboard_metrics(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics for a user.
        
        Args:
            user_id: User ID to get metrics for
            
        Returns:
            Dict containing dashboard metrics
        """
        try:
            # Get real-time metrics from analytics
            realtime_metrics = await self.analytics.get_realtime_metrics(user_id)
            
            # Get system performance metrics
            performance_metrics = await self.performance_optimizer.monitor_system_performance()
            
            # Get monitoring session status
            active_sessions = 0
            if hasattr(self.realtime_monitor, 'get_active_sessions_count'):
                active_sessions = await self.realtime_monitor.get_active_sessions_count(user_id)
            
            # Compile dashboard metrics
            dashboard_metrics = {
                'overview': {
                    'total_violations_detected': realtime_metrics.get('total_violations_detected', 0),
                    'violations_resolved': realtime_metrics.get('violations_resolved', 0),
                    'active_monitoring_sessions': realtime_metrics.get('active_monitoring_sessions', 0),
                    'system_health_score': realtime_metrics.get('system_health_score', 100.0),
                    'last_updated': datetime.utcnow().isoformat()
                },
                'performance': {
                    'average_response_time_ms': realtime_metrics.get('average_detection_time_seconds', 0) * 1000,
                    'detection_rate': realtime_metrics.get('detection_rate', 0.0),
                    'false_positive_rate': realtime_metrics.get('current_false_positive_rate', 0.0),
                    'throughput_per_minute': 0.0  # Would be calculated
                },
                'platform_distribution': realtime_metrics.get('platform_distribution', {}),
                'threat_distribution': realtime_metrics.get('threat_level_distribution', {}),
                'resource_usage': {
                    resource_type.value: {
                        'current_usage': metrics.current_usage,
                        'efficiency': metrics.efficiency,
                        'trend': metrics.trend
                    }
                    for resource_type, metrics in performance_metrics.items()
                },
                'recent_activity': await self._get_recent_activity(user_id),
                'alerts': await self._get_active_alerts(user_id),
                'insights': [
                    insight.__dict__ for insight in 
                    await self.analytics.generate_insights(user_id=user_id)
                ][:5]  # Top 5 insights
            }
            
            return dashboard_metrics
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return {}
    
    async def create_dashboard_config(
        self,
        user_id: int,
        layout_type: DashboardLayout,
        widgets: List[DashboardWidget]
    ) -> str:
        """
        Create a new dashboard configuration.
        
        Args:
            user_id: User ID
            layout_type: Dashboard layout type
            widgets: List of widgets to include
            
        Returns:
            str: Dashboard configuration ID
        """
        try:
            dashboard_id = f"dashboard_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            config = DashboardConfig(
                dashboard_id=dashboard_id,
                user_id=user_id,
                layout_type=layout_type,
                widgets=widgets
            )
            
            self._dashboard_configs[dashboard_id] = config
            
            # Initialize widgets
            for widget in widgets:
                await self._initialize_widget(widget, user_id)
            
            logger.info(f"Dashboard configuration created: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create dashboard configuration: {e}")
            raise HTTPException(status_code=500, detail="Failed to create dashboard")
    
    async def get_widget_data(
        self,
        widget_id: str,
        user_id: int,
        time_range: TimeRange = TimeRange.LAST_24_HOURS
    ) -> Dict[str, Any]:
        """
        Get data for a specific dashboard widget.
        
        Args:
            widget_id: Widget identifier
            user_id: User ID
            time_range: Time range for data
            
        Returns:
            Dict containing widget data
        """
        try:
            # Check cache first
            cache_key = f"{widget_id}_{user_id}_{time_range.value}"
            if cache_key in self._widget_cache:
                cached_data = self._widget_cache[cache_key]
                if (datetime.utcnow() - cached_data['timestamp']).seconds < 30:  # 30s cache
                    return cached_data['data']
            
            # Get widget configuration
            widget_config = await self._get_widget_config(widget_id)
            if not widget_config:
                raise HTTPException(status_code=404, detail="Widget not found")
            
            # Generate data based on widget type
            widget_data = await self._generate_widget_data(
                widget_config, user_id, time_range
            )
            
            # Cache the data
            self._widget_cache[cache_key] = {
                'data': widget_data,
                'timestamp': datetime.utcnow()
            }
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Failed to get widget data for {widget_id}: {e}")
            return {}
    
    async def update_widget_config(
        self,
        widget_id: str,
        user_id: int,
        config_updates: Dict[str, Any]
    ) -> bool:
        """
        Update widget configuration.
        
        Args:
            widget_id: Widget identifier
            user_id: User ID
            config_updates: Configuration updates
            
        Returns:
            bool: True if update successful
        """
        try:
            # Find and update widget configuration
            for dashboard_config in self._dashboard_configs.values():
                if dashboard_config.user_id == user_id:
                    for widget in dashboard_config.widgets:
                        if widget.widget_id == widget_id:
                            # Update widget configuration
                            for key, value in config_updates.items():
                                if hasattr(widget, key):
                                    setattr(widget, key, value)
                            
                            # Clear cache for this widget
                            cache_keys_to_remove = [
                                key for key in self._widget_cache.keys()
                                if key.startswith(f"{widget_id}_{user_id}")
                            ]
                            for key in cache_keys_to_remove:
                                del self._widget_cache[key]
                            
                            logger.info(f"Widget configuration updated: {widget_id}")
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update widget configuration: {e}")
            return False
    
    async def stream_realtime_data(
        self,
        websocket -> None: WebSocket,
        user_id -> None: int,
        subscriptions -> None: List[str]
    ) -> None:
        """
        Stream real-time data to WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
            subscriptions: List of data types to subscribe to
        """
        connection_id = f"conn_{user_id}_{datetime.utcnow().timestamp()}"
        
        try:
            # Establish connection
            await self.connection_manager.connect(websocket, connection_id, user_id)
            
            # Subscribe to data types
            self.connection_manager.subscribe_to_data(connection_id, subscriptions)
            
            # Send initial data
            initial_data = await self.get_dashboard_metrics(user_id)
            await self.connection_manager.send_personal_message(
                {
                    'type': 'initial_data',
                    'data': initial_data,
                    'timestamp': datetime.utcnow().isoformat()
                },
                connection_id
            )
            
            # Keep connection alive and handle messages
            while True:
                try:
                    # Wait for client messages (ping, subscription updates, etc.)
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    await self._handle_websocket_message(message, connection_id, user_id)
                    
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await self.connection_manager.send_personal_message(
                        {'type': 'ping', 'timestamp': datetime.utcnow().isoformat()},
                        connection_id
                    )
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {connection_id}: {e}")
        finally:
            self.connection_manager.disconnect(connection_id, user_id)
    
    async def export_dashboard_data(
        self,
        user_id: int,
        format_type: str = "json",
        time_range: TimeRange = TimeRange.LAST_7_DAYS
    ) -> Dict[str, Any]:
        """
        Export dashboard data in specified format.
        
        Args:
            user_id: User ID
            format_type: Export format (json, csv, excel)
            time_range: Time range for export
            
        Returns:
            Dict containing export data and metadata
        """
        try:
            # Get comprehensive dashboard data
            dashboard_data = await self.get_dashboard_metrics(user_id)
            
            # Get analytics data
            analytics_data = await self.analytics.export_analytics_data(
                export_format=format_type,
                time_range=AnalyticsTimeRange(time_range.value),
                user_id=user_id,
                include_raw_data=True
            )
            
            # Combine data
            export_data = {
                'metadata': {
                    'exported_at': datetime.utcnow().isoformat(),
                    'user_id': user_id,
                    'format': format_type,
                    'time_range': time_range.value
                },
                'dashboard_metrics': dashboard_data,
                'analytics': analytics_data,
                'configuration': {
                    'dashboards': [
                        config.dict() for config in self._dashboard_configs.values()
                        if config.user_id == user_id
                    ]
                }
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export dashboard data: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Gracefully shutdown dashboard controller."""
        logger.info("Shutting down Dashboard Controller...")
        
        # Close all WebSocket connections
        for connection_id in list(self.connection_manager.active_connections.keys()):
            try:
                websocket = self.connection_manager.active_connections[connection_id]
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket {connection_id}: {e}")
        
        # Stop streaming tasks
        for task in self._streaming_tasks.values():
            if hasattr(task, 'cancel'):
                task.cancel()
        
        # Clear caches
        self._widget_cache.clear()
        self._dashboard_configs.clear()
        
        self._initialized = False
        logger.info("Dashboard Controller shutdown complete")
    
    # Private helper methods
    
    def _setup_routes(self) -> None:
        """Set up FastAPI routes for dashboard API."""
        
        @self.router.get("/metrics/{user_id}")
        async def get_dashboard_metrics_endpoint(user_id -> None: int) -> None:
            """Get dashboard metrics for user."""
            return await self.get_dashboard_metrics(user_id)
        
        @self.router.get("/widget/{widget_id}/data")
        async def get_widget_data_endpoint(
            widget_id -> None: str,
            user_id -> None: int,
            time_range -> None: TimeRange = TimeRange.LAST_24_HOURS
        ) -> None:
            """Get data for specific widget."""
            return await self.get_widget_data(widget_id, user_id, time_range)
        
        @self.router.post("/create")
        async def create_dashboard_endpoint(
            user_id -> None: int,
            layout_type -> None: DashboardLayout,
            widgets -> None: List[DashboardWidget]
        ) -> None:
            """Create new dashboard configuration."""
            dashboard_id = await self.create_dashboard_config(user_id, layout_type, widgets)
            return {"dashboard_id": dashboard_id}
        
        @self.router.put("/widget/{widget_id}")
        async def update_widget_endpoint(
            widget_id -> None: str,
            user_id -> None: int,
            config_updates -> None: Dict[str, Any]
        ) -> None:
            """Update widget configuration."""
            success = await self.update_widget_config(widget_id, user_id, config_updates)
            return {"success": success}
        
        @self.router.get("/export/{user_id}")
        async def export_dashboard_endpoint(
            user_id -> None: int,
            format_type -> None: str = "json",
            time_range -> None: TimeRange = TimeRange.LAST_7_DAYS
        ) -> None:
            """Export dashboard data."""
            return await self.export_dashboard_data(user_id, format_type, time_range)
        
        @self.router.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket -> None: WebSocket, user_id -> None: int) -> None:
            """WebSocket endpoint for real-time data."""
            subscriptions = ["metrics", "alerts", "violations", "performance"]
            await self.stream_realtime_data(websocket, user_id, subscriptions)
    
    async def _load_default_configurations(self) -> None:
        """Load default dashboard configurations."""
        try:
            # Executive dashboard
            executive_widgets = [
                DashboardWidget(
                    widget_id="exec_metrics",
                    widget_type=DashboardWidgetType.METRICS_CHART,
                    title="Key Metrics Overview",
                    position={"x": 0, "y": 0, "width": 12, "height": 4},
                    config={"chart_type": "line", "metrics": ["violations", "detection_rate"]}
                ),
                DashboardWidget(
                    widget_id="exec_health",
                    widget_type=DashboardWidgetType.SYSTEM_HEALTH,
                    title="System Health",
                    position={"x": 0, "y": 4, "width": 6, "height": 3},
                    config={"display_type": "gauge"}
                ),
                DashboardWidget(
                    widget_id="exec_threats",
                    widget_type=DashboardWidgetType.THREAT_MAP,
                    title="Threat Distribution",
                    position={"x": 6, "y": 4, "width": 6, "height": 3},
                    config={"view_type": "pie_chart"}
                )
            ]
            
            # Technical dashboard
            technical_widgets = [
                DashboardWidget(
                    widget_id="tech_performance",
                    widget_type=DashboardWidgetType.PERFORMANCE_GAUGE,
                    title="Performance Metrics",
                    position={"x": 0, "y": 0, "width": 8, "height": 4},
                    config={"metrics": ["cpu", "memory", "disk", "network"]}
                ),
                DashboardWidget(
                    widget_id="tech_violations",
                    widget_type=DashboardWidgetType.VIOLATION_FEED,
                    title="Recent Violations",
                    position={"x": 8, "y": 0, "width": 4, "height": 4},
                    config={"max_items": 10, "auto_refresh": True}
                ),
                DashboardWidget(
                    widget_id="tech_platforms",
                    widget_type=DashboardWidgetType.PLATFORM_STATUS,
                    title="Platform Status",
                    position={"x": 0, "y": 4, "width": 12, "height": 3},
                    config={"show_details": True}
                )
            ]
            
            # Store default configurations
            self._default_configurations = {
                DashboardLayout.EXECUTIVE: executive_widgets,
                DashboardLayout.TECHNICAL: technical_widgets
            }
            
            logger.info("Default dashboard configurations loaded")
            
        except Exception as e:
            logger.error(f"Failed to load default configurations: {e}")
    
    async def _start_data_streaming(self) -> None:
        """Start background data streaming tasks."""
        try:
            # Start real-time metrics streaming
            self._streaming_tasks['metrics'] = asyncio.create_task(
                self._stream_metrics_data()
            )
            
            # Start alerts streaming
            self._streaming_tasks['alerts'] = asyncio.create_task(
                self._stream_alerts_data()
            )
            
            # Start violations streaming
            self._streaming_tasks['violations'] = asyncio.create_task(
                self._stream_violations_data()
            )
            
            logger.info("Data streaming tasks started")
            
        except Exception as e:
            logger.error(f"Failed to start data streaming: {e}")
    
    async def _initialize_widget_cache(self) -> None:
        """Initialize widget cache with default data."""
        try:
            # Pre-load common widget data
            common_widgets = ["metrics_overview", "system_health", "threat_distribution"]
            
            for widget_id in common_widgets:
                cache_key = f"{widget_id}_default_24h"
                self._widget_cache[cache_key] = {
                    'data': {},
                    'timestamp': datetime.utcnow()
                }
            
            logger.info("Widget cache initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize widget cache: {e}")
    
    async def _get_widget_config(self, widget_id: str) -> Optional[DashboardWidget]:
        """Get widget configuration by ID."""
        for dashboard_config in self._dashboard_configs.values():
            for widget in dashboard_config.widgets:
                if widget.widget_id == widget_id:
                    return widget
        return None
    
    async def _generate_widget_data(
        self,
        widget_config: DashboardWidget,
        user_id: int,
        time_range: TimeRange
    ) -> Dict[str, Any]:
        """
Generate data for a specific widget."""
        try:
            widget_type = widget_config.widget_type
            
            if widget_type == DashboardWidgetType.METRICS_CHART:
                return await self._generate_metrics_chart_data(widget_config, user_id, time_range)
            
            elif widget_type == DashboardWidgetType.THREAT_MAP:
                return await self._generate_threat_map_data(widget_config, user_id, time_range)
            
            elif widget_type == DashboardWidgetType.PLATFORM_STATUS:
                return await self._generate_platform_status_data(widget_config, user_id)
            
            elif widget_type == DashboardWidgetType.PERFORMANCE_GAUGE:
                return await self._generate_performance_gauge_data(widget_config, user_id)
            
            elif widget_type == DashboardWidgetType.VIOLATION_FEED:
                return await self._generate_violation_feed_data(widget_config, user_id, time_range)
            
            elif widget_type == DashboardWidgetType.SYSTEM_HEALTH:
                return await self._generate_system_health_data(widget_config, user_id)
            
            elif widget_type == DashboardWidgetType.ANALYTICS_TABLE:
                return await self._generate_analytics_table_data(widget_config, user_id, time_range)
            
            else:
                return {"error": f"Unsupported widget type: {widget_type}"}
                
        except Exception as e:
            logger.error(f"Failed to generate widget data: {e}")
            return {"error": str(e)}
    
    async def _generate_metrics_chart_data(
        self,
        widget_config: DashboardWidget,
        user_id: int,
        time_range: TimeRange
    ) -> Dict[str, Any]:
        """Generate metrics chart data."""
        try:
            # Get analytics time range
            analytics_time_range = AnalyticsTimeRange(time_range.value)
            
            # Get trend analysis for requested metrics
            metrics = widget_config.config.get('metrics', ['violations', 'detection_rate'])
            chart_data = {
                'labels': [],
                'datasets': []
            }
            
            for metric in metrics:
                # This would get actual historical data
                # For now, generate sample data
                data_points = [
                    {'timestamp': datetime.utcnow() - timedelta(hours=i), 'value': 50 + i * 2}
                    for i in range(24, 0, -1)
                ]
                
                chart_data['datasets'].append({
                    'label': metric.replace('_', ' ').title(),
                    'data': [point['value'] for point in data_points],
                    'borderColor': self._get_metric_color(metric),
                    'backgroundColor': self._get_metric_color(metric, alpha=0.2)
                })
            
            # Generate labels (timestamps)
            chart_data['labels'] = [
                (datetime.utcnow() - timedelta(hours=i)).strftime('%H:%M')
                for i in range(24, 0, -1)
            ]
            
            return {
                'chart_type': widget_config.config.get('chart_type', 'line'),
                'data': chart_data,
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {'beginAtZero': True}
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate metrics chart data: {e}")
            return {}
    
    async def _generate_threat_map_data(
        self,
        widget_config: DashboardWidget,
        user_id: int,
        time_range: TimeRange
    ) -> Dict[str, Any]:
        """Generate threat map data."""
        try:
            # Get threat distribution from analytics
            realtime_metrics = await self.analytics.get_realtime_metrics(user_id)
            threat_distribution = realtime_metrics.get('threat_level_distribution', {})
            
            return {
                'view_type': widget_config.config.get('view_type', 'pie_chart'),
                'data': {
                    'labels': list(threat_distribution.keys()),
                    'values': list(threat_distribution.values()),
                    'colors': [
                        '#ff4444' if level == 'critical' else
                        '#ff8800' if level == 'high' else
                        '#ffcc00' if level == 'medium' else
                        '#00cc44' for level in threat_distribution.keys()
                    ]
                },
                'total_threats': sum(threat_distribution.values()),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate threat map data: {e}")
            return {}
    
    async def _generate_platform_status_data(
        self,
        widget_config: DashboardWidget,
        user_id: int
    ) -> Dict[str, Any]:
        """Generate platform status data."""
        try:
            # Get platform analytics
            platform_analytics = await self.analytics.get_platform_analytics(
                time_range=AnalyticsTimeRange.LAST_24_HOURS,
                user_id=user_id
            )
            
            platforms = []
            for platform, data in platform_analytics.get('platform_coverage', {}).items():
                platforms.append({
                    'name': platform,
                    'status': 'active' if data.get('active_sessions', 0) > 0 else 'inactive',
                    'active_sessions': data.get('active_sessions', 0),
                    'total_scans': data.get('total_scans', 0),
                    'detection_rate': platform_analytics.get('detection_rates', {}).get(platform, 0.0),
                    'last_scan': datetime.utcnow().isoformat()  # Would be actual last scan time
                })
            
            return {
                'platforms': platforms,
                'total_platforms': len(platforms),
                'active_platforms': len([p for p in platforms if p['status'] == 'active']),
                'show_details': widget_config.config.get('show_details', False)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate platform status data: {e}")
            return {}
    
    async def _generate_performance_gauge_data(
        self,
        widget_config: DashboardWidget,
        user_id: int
    ) -> Dict[str, Any]:
        """Generate performance gauge data."""
        try:
            # Get system performance metrics
            performance_metrics = await self.performance_optimizer.monitor_system_performance()
            
            gauges = []
            requested_metrics = widget_config.config.get('metrics', ['cpu', 'memory'])
            
            for metric in requested_metrics:
                if metric in ['cpu', 'memory', 'disk', 'network']:
                    resource_type = getattr(self.performance_optimizer.ResourceType, metric.upper(), None)
                    if resource_type and resource_type in performance_metrics:
                        metrics_data = performance_metrics[resource_type]
                        gauges.append({
                            'name': metric.upper(),
                            'value': metrics_data.current_usage,
                            'max_value': 100,
                            'unit': '%',
                            'status': self._get_gauge_status(metrics_data.current_usage),
                            'trend': metrics_data.trend
                        })
            
            return {
                'gauges': gauges,
                'overall_health': await self._calculate_overall_health(performance_metrics),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance gauge data: {e}")
            return {}
    
    async def _generate_violation_feed_data(
        self,
        widget_config: DashboardWidget,
        user_id: int,
        time_range: TimeRange
    ) -> Dict[str, Any]:
        """Generate violation feed data."""
        try:
            max_items = widget_config.config.get('max_items', 10)
            
            # Get recent violations (would be from database)
            violations = [
                {
                    'id': f"violation_{i}",
                    'platform': ['youtube', 'instagram', 'tiktok'][i % 3],
                    'content_title': f"Sample Content {i}",
                    'similarity_score': 0.85 + (i * 0.02),
                    'threat_level': ['high', 'medium', 'critical'][i % 3],
                    'detected_at': datetime.utcnow() - timedelta(minutes=i * 10),
                    'status': ['pending', 'investigating', 'resolved'][i % 3]
                }
                for i in range(max_items)
            ]
            
            return {
                'violations': violations,
                'total_count': len(violations),
                'auto_refresh': widget_config.config.get('auto_refresh', True),
                'refresh_interval': widget_config.refresh_interval
            }
            
        except Exception as e:
            logger.error(f"Failed to generate violation feed data: {e}")
            return {}
    
    async def _generate_system_health_data(
        self,
        widget_config: DashboardWidget,
        user_id: int
    ) -> Dict[str, Any]:
        """Generate system health data."""
        try:
            # Get system health score from analytics
            realtime_metrics = await self.analytics.get_realtime_metrics(user_id)
            health_score = realtime_metrics.get('system_health_score', 100.0)
            
            # Get performance metrics for detailed health
            performance_metrics = await self.performance_optimizer.monitor_system_performance()
            
            health_components = []
            for resource_type, metrics in performance_metrics.items():
                health_components.append({
                    'component': resource_type.value,
                    'status': self._get_health_status(metrics.current_usage),
                    'score': max(0, 100 - metrics.current_usage),
                    'details': metrics.recommendations[:2]  # Top 2 recommendations
                })
            
            return {
                'overall_score': health_score,
                'status': self._get_health_status(100 - health_score),
                'components': health_components,
                'display_type': widget_config.config.get('display_type', 'gauge'),
                'last_checked': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate system health data: {e}")
            return {}
    
    async def _generate_analytics_table_data(
        self,
        widget_config: DashboardWidget,
        user_id: int,
        time_range: TimeRange
    ) -> Dict[str, Any]:
        """Generate analytics table data."""
        try:
            # Get platform analytics for table
            platform_analytics = await self.analytics.get_platform_analytics(
                time_range=AnalyticsTimeRange(time_range.value),
                user_id=user_id
            )
            
            table_data = []
            for platform in platform_analytics.get('platform_coverage', {}).keys():
                table_data.append({
                    'platform': platform,
                    'violations': platform_analytics.get('total_violations_by_platform', {}).get(platform, 0),
                    'detection_rate': f"{platform_analytics.get('detection_rates', {}).get(platform, 0):.1%}",
                    'false_positive_rate': f"{platform_analytics.get('false_positive_rates', {}).get(platform, 0):.1%}",
                    'avg_response_time': f"{platform_analytics.get('response_times', {}).get(platform, 0):.0f}ms",
                    'enforcement_success': f"{platform_analytics.get('enforcement_success_rates', {}).get(platform, 0):.1%}"
                })
            
            return {
                'columns': [
                    {'key': 'platform', 'title': 'Platform', 'sortable': True},
                    {'key': 'violations', 'title': 'Violations', 'sortable': True},
                    {'key': 'detection_rate', 'title': 'Detection Rate', 'sortable': True},
                    {'key': 'false_positive_rate', 'title': 'False Positive Rate', 'sortable': True},
                    {'key': 'avg_response_time', 'title': 'Avg Response Time', 'sortable': True},
                    {'key': 'enforcement_success', 'title': 'Enforcement Success', 'sortable': True}
                ],
                'data': table_data,
                'sortable': True,
                'filterable': True,
                'pagination': {
                    'page_size': widget_config.config.get('page_size', 10),
                    'current_page': 1,
                    'total_pages': 1
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate analytics table data: {e}")
            return {}
    
    def _get_metric_color(self, metric: str, alpha: float = 1.0) -> str:
        """Get color for metric visualization."""
        color_map = {
            'violations': f'rgba(255, 99, 132, {alpha})',
            'detection_rate': f'rgba(54, 162, 235, {alpha})',
            'false_positive_rate': f'rgba(255, 206, 86, {alpha})',
            'response_time': f'rgba(75, 192, 192, {alpha})',
            'throughput': f'rgba(153, 102, 255, {alpha})'
        }
        return color_map.get(metric, f'rgba(128, 128, 128, {alpha})')
    
    def _get_gauge_status(self, value: float) -> str:
        """
Get status for gauge visualization."""
        if value >= 90:
            return 'critical'
        elif value >= 75:
            return 'warning'
        elif value >= 50:
            return 'good'
        else:
            return 'excellent'
    
    def _get_health_status(self, value: float) -> str:
        """
Get health status based on value."""
        if value >= 90:
            return 'excellent'
        elif value >= 75:
            return 'good'
        elif value >= 50:
            return 'warning'
        else:
            return 'critical'
    
    async def _calculate_overall_health(self, performance_metrics: Dict) -> float:
        """
Calculate overall system health score."""
        try:
            if not performance_metrics:
                return 100.0
            
            total_score = 0.0
            count = 0
            
            for resource_type, metrics in performance_metrics.items():
                # Health is inverse of usage (lower usage = better health)
                health_score = max(0, 100 - metrics.current_usage)
                total_score += health_score
                count += 1
            
            return total_score / count if count > 0 else 100.0
            
        except Exception as e:
            logger.error(f"Failed to calculate overall health: {e}")
            return 100.0
    
    async def _get_recent_activity(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recent activity for dashboard."""
        try:
            # This would get actual recent activity from database
            activities = [
                {
                    'id': f'activity_{i}',
                    'type': ['violation_detected', 'enforcement_action', 'optimization'][i % 3],
                    'description': f'Sample activity {i}',
                    'timestamp': datetime.utcnow() - timedelta(minutes=i * 5),
                    'severity': ['low', 'medium', 'high'][i % 3]
                }
                for i in range(5)
            ]
            
            return activities
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []
    
    async def _get_active_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get active alerts for dashboard."""
        try:
            # This would get actual alerts from database
            alerts = [
                {
                    'id': f'alert_{i}',
                    'title': f'Sample Alert {i}',
                    'message': f'Alert message {i}',
                    'severity': ['low', 'medium', 'high', 'critical'][i % 4],
                    'created_at': datetime.utcnow() - timedelta(hours=i),
                    'acknowledged': i % 2 == 0
                }
                for i in range(3)
            ]
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def _handle_websocket_message(
        self,
        message -> None: str,
        connection_id -> None: str,
        user_id -> None: int
    ) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Update subscriptions
                subscriptions = data.get('subscriptions', [])
                self.connection_manager.subscribe_to_data(connection_id, subscriptions)
                
            elif message_type == 'unsubscribe':
                # Remove subscriptions
                subscriptions = data.get('subscriptions', [])
                current_subs = self.connection_manager.connection_subscriptions.get(connection_id, [])
                new_subs = [sub for sub in current_subs if sub not in subscriptions]
                self.connection_manager.subscribe_to_data(connection_id, new_subs)
                
            elif message_type == 'request_data':
                # Send specific data
                widget_id = data.get('widget_id')
                if widget_id:
                    widget_data = await self.get_widget_data(widget_id, user_id)
                    await self.connection_manager.send_personal_message(
                        {
                            'type': 'widget_data',
                            'widget_id': widget_id,
                            'data': widget_data,
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        connection_id
                    )
            
        except Exception as e:
            logger.error(f"Failed to handle WebSocket message: {e}")
    
    async def _stream_metrics_data(self) -> None:
        """Stream real-time metrics data."""
        while self._initialized:
            try:
                # Get current metrics
                for user_id in self.connection_manager.user_connections.keys():
                    metrics = await self.get_dashboard_metrics(user_id)
                    
                    message = {
                        'type': 'metrics_update',
                        'data': metrics,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    await self.connection_manager.send_to_subscribers('metrics', message)
                
                # Wait before next update
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics streaming: {e}")
                await asyncio.sleep(30)
    
    async def _stream_alerts_data(self) -> None:
        """Stream real-time alerts data."""
        while self._initialized:
            try:
                # Check for new alerts
                for user_id in self.connection_manager.user_connections.keys():
                    alerts = await self._get_active_alerts(user_id)
                    
                    message = {
                        'type': 'alerts_update',
                        'data': {'alerts': alerts},
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    await self.connection_manager.send_to_subscribers('alerts', message)
                
                await asyncio.sleep(60)  # Check alerts every minute
                
            except Exception as e:
                logger.error(f"Error in alerts streaming: {e}")
                await asyncio.sleep(60)
    
    async def _stream_violations_data(self) -> None:
        """Stream real-time violations data."""
        while self._initialized:
            try:
                # Check for new violations
                # This would integrate with real-time monitor for actual violations
                
                await asyncio.sleep(15)  # Check violations every 15 seconds
                
            except Exception as e:
                logger.error(f"Error in violations streaming: {e}")
                await asyncio.sleep(15)
    
    async def _initialize_widget(self, widget -> None: DashboardWidget, user_id -> None: int) -> None:
        """Initialize a dashboard widget."""
        try:
            # Pre-generate initial data for widget
            initial_data = await self._generate_widget_data(
                widget, user_id, TimeRange.LAST_24_HOURS
            )
            
            # Cache initial data
            cache_key = f"{widget.widget_id}_{user_id}_{TimeRange.LAST_24_HOURS.value}"
            self._widget_cache[cache_key] = {
                'data': initial_data,
                'timestamp': datetime.utcnow()
            }
            
            logger.info(f"Widget initialized: {widget.widget_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize widget {widget.widget_id}: {e}")
    SYSTEM_HEALTH = "system_health"
    OPTIMIZATION_PANEL = "optimization_panel"

class ChartType(str, Enum):
    """Chart types for visualization."""

    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"

class DashboardWidget(BaseModel):
    """Dashboard widget configuration."""
    widget_id: str
    widget_type: DashboardWidgetType
    title: str
    position: Dict[str, int] = Field(default_factory=dict)  # x, y, width, height
    config: Dict[str, Any] = Field(default_factory=dict)
    data_source: str = ""
    refresh_interval: int = 30  # seconds
    enabled: bool = True

class DashboardLayout(BaseModel):
    """Dashboard layout configuration."""
    layout_id: str
    name: str
    description: str = ""
    widgets: List[DashboardWidget] = Field(default_factory=list)
    created_by: int
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RealTimeDataPoint(BaseModel):
    """Real-time data point for dashboard."""
    timestamp: datetime
    metric_name: str
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DashboardMetrics(BaseModel):
    """
Dashboard metrics summary."""
    total_violations: int = 0
    active_monitors: int = 0
    detection_rate: float = 0.0
    false_positive_rate: float = 0.0
    system_health: float = 100.0
    response_time: float = 0.0
    threat_distribution: Dict[str, int] = Field(default_factory=dict)
    platform_status: Dict[str, str] = Field(default_factory=dict)

class WebSocketConnection:
    """
WebSocket connection manager."""
    
    def __init__(self, websocket -> None: WebSocket, user_id -> None: int) -> None:
        self.websocket = websocket
        self.user_id = user_id
        self.subscriptions: Set[str] = set()
        self.connected_at = datetime.utcnow()

class DashboardController:
    """
    Advanced dashboard controller for monitoring visualization.
    
    Features:
    - Real-time data streaming via WebSocket
    - Customizable dashboard layouts
    - Interactive widget configuration
    - Performance metrics visualization
    - Multi-user dashboard management
    """
    
    def __init__(
        self,
        realtime_monitor -> None: RealTimeMonitor,
        analytics -> None: MonitoringAnalytics,
        performance_optimizer -> None: PerformanceOptimizer
    ) -> None:
        """
Initialize dashboard controller."""
        self.realtime_monitor = realtime_monitor
        self.analytics = analytics
        self.performance_optimizer = performance_optimizer
        
        # WebSocket connections
        self._websocket_connections: Dict[str, WebSocketConnection] = {}
        
        # Dashboard layouts
        self._dashboard_layouts: Dict[str, DashboardLayout] = {}
        
        # Real-time data cache
        self._realtime_data_cache: Dict[str, List[RealTimeDataPoint]] = {}
        self._cache_max_size = 1000
        
        # Background tasks
        self._dashboard_tasks: List[asyncio.Task] = []
        self._running = False
        
        logger.info("Dashboard Controller initialized")

    async def initialize(self) -> bool:
        """Initialize the dashboard controller."""
        try:
            logger.info("Initializing Dashboard Controller...")
            
            # Load default dashboard layouts
            await self._load_default_layouts()
            
            # Start background tasks
            await self._start_dashboard_tasks()
            
            self._running = True
            logger.info("Dashboard Controller initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Dashboard Controller: {e}")
            return False

    async def get_dashboard_metrics(self, user_id: int) -> DashboardMetrics:
        """Get comprehensive dashboard metrics."""
        try:
            # Get real-time metrics
            realtime_metrics = await self.realtime_monitor.get_realtime_metrics()
            
            # Get analytics data
            analytics_report = await self.analytics.generate_analytics_report(
                AnalyticsTimeRange.LAST_24_HOURS
            )
            
            # Get performance data
            performance_metrics = await self.performance_optimizer.monitor_system_performance()
            
            # Compile dashboard metrics
            metrics = DashboardMetrics(
                total_violations=analytics_report.total_violations,
                active_monitors=len(await self.realtime_monitor.get_active_sessions()),
                detection_rate=realtime_metrics.detection_accuracy,
                false_positive_rate=realtime_metrics.violations_detected * 0.05,  # Mock calculation
                system_health=performance_metrics.get('cpu', 0).efficiency * 100,
                response_time=realtime_metrics.response_time_ms,
                threat_distribution={
                    ThreatLevel.CRITICAL.value: 5,
                    ThreatLevel.HIGH.value: 15,
                    ThreatLevel.MEDIUM.value: 30,
                    ThreatLevel.LOW.value: 50
                },
                platform_status={
                    "youtube": "active",
                    "spotify": "active", 
                    "instagram": "maintenance",
                    "tiktok": "active"
                }
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return DashboardMetrics()

    async def get_widget_data(
        self,
        widget_id: str,
        widget_type: DashboardWidgetType,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get data for a specific dashboard widget."""
        try:
            if widget_type == DashboardWidgetType.METRICS_CHART:
                return await self._get_metrics_chart_data(config)
                
            elif widget_type == DashboardWidgetType.THREAT_MAP:
                return await self._get_threat_map_data(config)
                
            elif widget_type == DashboardWidgetType.PLATFORM_STATUS:
                return await self._get_platform_status_data(config)
                
            elif widget_type == DashboardWidgetType.PERFORMANCE_GAUGE:
                return await self._get_performance_gauge_data(config)
                
            elif widget_type == DashboardWidgetType.VIOLATION_FEED:
                return await self._get_violation_feed_data(config)
                
            elif widget_type == DashboardWidgetType.ANALYTICS_TABLE:
                return await self._get_analytics_table_data(config)
                
            elif widget_type == DashboardWidgetType.SYSTEM_HEALTH:
                return await self._get_system_health_data(config)
                
            elif widget_type == DashboardWidgetType.OPTIMIZATION_PANEL:
                return await self._get_optimization_panel_data(config)
            
            else:
                return {"error": f"Unsupported widget type: {widget_type}"}
                
        except Exception as e:
            logger.error(f"Failed to get widget data for {widget_id}: {e}")
            return {"error": str(e)}

    async def create_dashboard_layout(
        self,
        layout_data: Dict[str, Any],
        user_id: int
    ) -> DashboardLayout:
        """Create a new dashboard layout."""
        try:
            layout = DashboardLayout(
                layout_id=f"layout_{user_id}_{int(datetime.utcnow().timestamp())}",
                name=layout_data.get('name', 'New Dashboard'),
                description=layout_data.get('description', ''),
                widgets=[
                    DashboardWidget(**widget) 
                    for widget in layout_data.get('widgets', [])
                ],
                created_by=user_id
            )
            
            # Store layout
            self._dashboard_layouts[layout.layout_id] = layout
            
            # Save to persistent storage (would implement database save)
            await self._save_dashboard_layout(layout)
            
            logger.info(f"Created dashboard layout: {layout.layout_id}")
            return layout
            
        except Exception as e:
            logger.error(f"Failed to create dashboard layout: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_dashboard_layout(
        self,
        layout_id: str,
        updates: Dict[str, Any],
        user_id: int
    ) -> DashboardLayout:
        """Update an existing dashboard layout."""
        try:
            if layout_id not in self._dashboard_layouts:
                raise HTTPException(status_code=404, detail="Layout not found")
            
            layout = self._dashboard_layouts[layout_id]
            
            # Verify ownership
            if layout.created_by != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(layout, key):
                    setattr(layout, key, value)
            
            # Save changes
            await self._save_dashboard_layout(layout)
            
            logger.info(f"Updated dashboard layout: {layout_id}")
            return layout
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update dashboard layout: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_dashboard_layouts(self, user_id: int) -> List[DashboardLayout]:
        """Get dashboard layouts for a user."""
        try:
            user_layouts = [
                layout for layout in self._dashboard_layouts.values()
                if layout.created_by == user_id or layout.is_default
            ]
            return user_layouts
            
        except Exception as e:
            logger.error(f"Failed to get user dashboard layouts: {e}")
            return []

    async def handle_websocket_connection(
        self,
        websocket: WebSocket,
        user_id: int
    ) -> None:
        """Handle WebSocket connection for real-time dashboard updates."""
        await websocket.accept()
        
        connection_id = f"ws_{user_id}_{int(datetime.utcnow().timestamp())}"
        connection = WebSocketConnection(websocket, user_id)
        self._websocket_connections[connection_id] = connection
        
        logger.info(f"WebSocket connected: {connection_id}")
        
        try:
            while True:
                # Receive message from client
                message = await websocket.receive_text()
                data = json.loads(message)
                
                # Handle different message types
                if data.get('type') == 'subscribe':
                    await self._handle_websocket_subscription(connection, data)
                elif data.get('type') == 'unsubscribe':
                    await self._handle_websocket_unsubscription(connection, data)
                elif data.get('type') == 'get_data':
                    await self._handle_websocket_data_request(connection, data)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {connection_id}: {e}")
        finally:
            # Clean up connection
            if connection_id in self._websocket_connections:
                del self._websocket_connections[connection_id]

    async def stream_realtime_data(
        self,
        data_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> StreamingResponse:
        """Stream real-time data for dashboard components."""
        async def generate_data() -> None:
            """
Generate streaming data."""
            try:
                while True:
                    # Get real-time data based on type
                    if data_type == "violations":
                        data = await self._get_realtime_violations(filters)
                    elif data_type == "metrics":
                        data = await self._get_realtime_metrics(filters)
                    elif data_type == "performance":
                        data = await self._get_realtime_performance(filters)
                    else:
                        data = {"error": f"Unknown data type: {data_type}"}
                    
                    # Format as server-sent events
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    # Wait before next update
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"Error streaming {data_type} data: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_data(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    async def _get_metrics_chart_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for metrics chart widget."""
        chart_type = config.get('chart_type', ChartType.LINE.value)
        metric_types = config.get('metrics', ['detection_rate'])
        time_range = config.get('time_range', '1h')
        
        # Get historical metrics data
        end_time = datetime.utcnow()
        if time_range == '1h':
            start_time = end_time - timedelta(hours=1)
        elif time_range == '6h':
            start_time = end_time - timedelta(hours=6)
        elif time_range == '24h':
            start_time = end_time - timedelta(hours=24)
        else:
            start_time = end_time - timedelta(hours=1)
        
        # Format data for chart
        chart_data = {
            'type': chart_type,
            'data': {
                'labels': [],
                'datasets': []
            },
            'options': {
                'responsive': True,
                'scales': {
                    'x': {'type': 'time'},
                    'y': {'beginAtZero': True}
                }
            }
        }
        
        # Generate time labels
        current_time = start_time
        while current_time <= end_time:
            chart_data['data']['labels'].append(current_time.isoformat())
            current_time += timedelta(minutes=5)
        
        # Add datasets for each metric
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
        for i, metric_type in enumerate(metric_types):
            # Mock data generation (would fetch real data)
            values = [
                np.random.uniform(0.8, 0.95) for _ in chart_data['data']['labels']
            ]
            
            dataset = {
                'label': metric_type.replace('_', ' ').title(),
                'data': values,
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '20',
                'tension': 0.1
            }
            chart_data['data']['datasets'].append(dataset)
        
        return chart_data

    async def _get_threat_map_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
Get data for threat map widget."""
        # Mock geographical threat data
        threat_data = {
            'type': 'geographical',
            'threats': [
                {
                    'country': 'US',
                    'threat_count': 45,
                    'threat_level': 'medium',
                    'coordinates': [39.8283, -98.5795]
                },
                {
                    'country': 'DE',
                    'threat_count': 23,
                    'threat_level': 'low',
                    'coordinates': [51.1657, 10.4515]
                },
                {
                    'country': 'CN',
                    'threat_count': 67,
                    'threat_level': 'high',
                    'coordinates': [35.8617, 104.1954]
                }
            ],
            'heatmap_data': [
                {'lat': 40.7128, 'lng': -74.0060, 'intensity': 0.8},  # New York
                {'lat': 51.5074, 'lng': -0.1278, 'intensity': 0.6},   # London
                {'lat': 35.6762, 'lng': 139.6503, 'intensity': 0.9}   # Tokyo
            ]
        }
        
        return threat_data

    async def _get_platform_status_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
Get data for platform status widget."""
        platforms = config.get('platforms', ['youtube', 'spotify', 'instagram', 'tiktok'])
        
        status_data = {
            'platforms': []
        }
        
        for platform in platforms:
            # Mock platform status
            status = {
                'name': platform,
                'status': np.random.choice(['active', 'warning', 'error'], p=[0.8, 0.15, 0.05]),
                'uptime': np.random.uniform(95, 100),
                'last_scan': (datetime.utcnow() - timedelta(minutes=np.random.randint(1, 60))).isoformat(),
                'violations_detected': np.random.randint(0, 20),
                'response_time': np.random.uniform(500, 2000)
            }
            status_data['platforms'].append(status)
        
        return status_data

    async def _get_performance_gauge_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
Get data for performance gauge widget."""
        metric_type = config.get('metric', 'system_health')
        
        # Get current performance metrics
        performance_metrics = await self.performance_optimizer.monitor_system_performance()
        
        if metric_type == 'system_health':
            value = np.mean([
                m.efficiency for m in performance_metrics.values()
            ]) * 100
        elif metric_type == 'response_time':
            value = np.random.uniform(500, 2000)
        elif metric_type == 'detection_rate':
            value = np.random.uniform(85, 98)
        else:
            value = 50
        
        gauge_data = {
            'value': value,
            'min': config.get('min', 0),
            'max': config.get('max', 100),
            'threshold': config.get('threshold', 80),
            'unit': config.get('unit', '%'),
            'status': 'good' if value >= config.get('threshold', 80) else 'warning'
        }
        
        return gauge_data

    async def _get_violation_feed_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
Get data for violation feed widget."""
        limit = config.get('limit', 10)
        
        # Mock violation feed data
        violations = []
        for i in range(limit):
            violation = {
                'id': f"violation_{i}",
                'timestamp': (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(),
                'platform': np.random.choice(['youtube', 'spotify', 'instagram', 'tiktok']),
                'threat_level': np.random.choice(['low', 'medium', 'high', 'critical']),
                'similarity_score': np.random.uniform(0.8, 0.95),
                'url': f"https://example.com/content_{i}",
                'status': np.random.choice(['pending', 'investigating', 'resolved'])
            }
            violations.append(violation)
        
        return {'violations': violations}

    async def _get_analytics_table_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for analytics table widget."""
        # Generate analytics report
        report = await self.analytics.generate_analytics_report(
            AnalyticsTimeRange.LAST_24_HOURS
        )
        
        # Format for table display
        table_data = {
            'columns': [
                {'key': 'platform', 'title': 'Platform'},
                {'key': 'detections', 'title': 'Detections'},
                {'key': 'false_positives', 'title': 'False Positives'},
                {'key': 'accuracy', 'title': 'Accuracy %'},
                {'key': 'response_time', 'title': 'Avg Response (ms)'}
            ],
            'rows': []
        }
        
        for platform_perf in report.platform_performance:
            row = {
                'platform': platform_perf.platform_name,
                'detections': platform_perf.detection_count,
                'false_positives': platform_perf.false_positive_count,
                'accuracy': f"{platform_perf.efficiency_score * 100:.1f}",
                'response_time': f"{platform_perf.average_response_time:.0f}"
            }
            table_data['rows'].append(row)
        
        return table_data

    async def _get_system_health_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for system health widget."""
        # Get current system metrics
        performance_metrics = await self.performance_optimizer.monitor_system_performance()
        
        health_data = {
            'overall_health': np.mean([m.efficiency for m in performance_metrics.values()]) * 100,
            'components': []
        }
        
        for resource_type, metrics in performance_metrics.items():
            component = {
                'name': resource_type.value.title(),
                'status': 'healthy' if metrics.current_usage < 80 else 'warning',
                'usage': metrics.current_usage,
                'trend': metrics.trend
            }
            health_data['components'].append(component)
        
        return health_data

    async def _get_optimization_panel_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
Get data for optimization panel widget."""
        # Get optimization recommendations
        recommendations = await self.performance_optimizer.generate_optimization_recommendations()
        
        panel_data = {
            'recommendations': [
                {
                    'id': rec.id,
                    'description': rec.description,
                    'priority': rec.priority,
                    'expected_improvement': f"{rec.expected_improvement * 100:.1f}%",
                    'risk_level': rec.risk_level,
                    'action': rec.action.value
                }
                for rec in recommendations[:5]  # Top 5 recommendations
            ],
            'auto_optimization_enabled': self.performance_optimizer.auto_apply_recommendations,
            'last_optimization': datetime.utcnow().isoformat()
        }
        
        return panel_data

    async def _handle_websocket_subscription(
        self,
        connection: WebSocketConnection,
        data: Dict[str, Any]
    ) -> None:
        """Handle WebSocket subscription request."""
        subscription_type = data.get('subscription_type')
        if subscription_type:
            connection.subscriptions.add(subscription_type)
            
            # Send confirmation
            response = {
                'type': 'subscription_confirmed',
                'subscription_type': subscription_type
            }
            await connection.websocket.send_text(json.dumps(response))

    async def _handle_websocket_unsubscription(
        self,
        connection: WebSocketConnection,
        data: Dict[str, Any]
    ) -> None:
        """
Handle WebSocket unsubscription request."""
        subscription_type = data.get('subscription_type')
        if subscription_type in connection.subscriptions:
            connection.subscriptions.remove(subscription_type)
            
            # Send confirmation
            response = {
                'type': 'unsubscription_confirmed',
                'subscription_type': subscription_type
            }
            await connection.websocket.send_text(json.dumps(response))

    async def _handle_websocket_data_request(
        self,
        connection: WebSocketConnection,
        data: Dict[str, Any]
    ) -> None:
        """
Handle WebSocket data request."""
        widget_type = data.get('widget_type')
        widget_config = data.get('config', {})
        
        if widget_type:
            widget_data = await self.get_widget_data(
                f"ws_{connection.user_id}",
                DashboardWidgetType(widget_type),
                widget_config
            )
            
            response = {
                'type': 'widget_data',
                'widget_type': widget_type,
                'data': widget_data
            }
            await connection.websocket.send_text(json.dumps(response))

    async def _start_dashboard_tasks(self) -> None:
        """Start background dashboard tasks."""
        # Real-time data broadcasting task
        broadcast_task = asyncio.create_task(self._realtime_broadcast_loop())
        self._dashboard_tasks.append(broadcast_task)
        
        logger.info("Started dashboard background tasks")

    async def _realtime_broadcast_loop(self) -> None:
        """Background task for broadcasting real-time data."""
        try:
            while self._running:
                # Broadcast to all connected WebSocket clients
                for connection in self._websocket_connections.values():
                    try:
                        # Send data for subscribed channels
                        for subscription in connection.subscriptions:
                            data = await self._get_subscription_data(subscription)
                            if data:
                                message = {
                                    'type': 'realtime_data',
                                    'subscription': subscription,
                                    'data': data,
                                    'timestamp': datetime.utcnow().isoformat()
                                }
                                await connection.websocket.send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"Error broadcasting to WebSocket: {e}")
                
                await asyncio.sleep(5)  # Broadcast every 5 seconds
                
        except asyncio.CancelledError:
            logger.debug("Real-time broadcast loop cancelled")

    async def _get_subscription_data(self, subscription_type: str) -> Optional[Dict[str, Any]]:
        """Get data for a subscription type."""
        try:
            if subscription_type == 'violations':
                return await self._get_realtime_violations()
            elif subscription_type == 'metrics':
                return await self._get_realtime_metrics()
            elif subscription_type == 'performance':
                return await self._get_realtime_performance()
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting subscription data for {subscription_type}: {e}")
            return None

    async def _get_realtime_violations(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get real-time violation data."""
        # Mock real-time violations
        return {
            'new_violations': np.random.randint(0, 3),
            'total_violations_today': np.random.randint(50, 200),
            'threat_level_distribution': {
                'critical': np.random.randint(0, 5),
                'high': np.random.randint(5, 15),
                'medium': np.random.randint(15, 30),
                'low': np.random.randint(30, 50)
            }
        }

    async def _get_realtime_metrics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
Get real-time metrics data."""
        metrics = await self.realtime_monitor.get_realtime_metrics()
        return {
            'detection_accuracy': metrics.detection_accuracy,
            'response_time': metrics.response_time_ms,
            'active_monitors': len(await self.realtime_monitor.get_active_sessions()),
            'system_load': np.random.uniform(0.3, 0.8)
        }

    async def _get_realtime_performance(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
Get real-time performance data."""
        performance_metrics = await self.performance_optimizer.monitor_system_performance()
        
        return {
            'cpu_usage': performance_metrics.get('cpu', type('obj', (object,), {'current_usage': 0})).current_usage,
            'memory_usage': performance_metrics.get('memory', type('obj', (object,), {'current_usage': 0})).current_usage,
            'queue_depth': performance_metrics.get('queue', type('obj', (object,), {'current_usage': 0})).current_usage,
            'overall_health': np.mean([m.efficiency for m in performance_metrics.values()]) * 100
        }

    async def _load_default_layouts(self) -> None:
        """
Load default dashboard layouts."""
        try:
            # Create default monitoring dashboard
            default_layout = DashboardLayout(
                layout_id="default_monitoring",
                name="Default Monitoring Dashboard",
                description="Default layout for content protection monitoring",
                widgets=[
                    DashboardWidget(
                        widget_id="metrics_overview",
                        widget_type=DashboardWidgetType.METRICS_CHART,
                        title="Detection Metrics",
                        position={"x": 0, "y": 0, "width": 6, "height": 4},
                        config={"chart_type": "line", "metrics": ["detection_rate", "false_positive_rate"]}
                    ),
                    DashboardWidget(
                        widget_id="threat_map",
                        widget_type=DashboardWidgetType.THREAT_MAP,
                        title="Global Threat Map",
                        position={"x": 6, "y": 0, "width": 6, "height": 4},
                        config={}
                    ),
                    DashboardWidget(
                        widget_id="platform_status",
                        widget_type=DashboardWidgetType.PLATFORM_STATUS,
                        title="Platform Status",
                        position={"x": 0, "y": 4, "width": 4, "height": 3},
                        config={"platforms": ["youtube", "spotify", "instagram", "tiktok"]}
                    ),
                    DashboardWidget(
                        widget_id="system_health",
                        widget_type=DashboardWidgetType.SYSTEM_HEALTH,
                        title="System Health",
                        position={"x": 4, "y": 4, "width": 4, "height": 3},
                        config={}
                    ),
                    DashboardWidget(
                        widget_id="violation_feed",
                        widget_type=DashboardWidgetType.VIOLATION_FEED,
                        title="Recent Violations",
                        position={"x": 8, "y": 4, "width": 4, "height": 3},
                        config={"limit": 10}
                    )
                ],
                created_by=0,  # System user
                is_default=True
            )
            
            self._dashboard_layouts[default_layout.layout_id] = default_layout
            
            logger.info("Loaded default dashboard layouts")
            
        except Exception as e:
            logger.error(f"Failed to load default layouts: {e}")

    async def _save_dashboard_layout(self, layout: DashboardLayout) -> None:
        """Save dashboard layout to persistent storage."""
        try:
            # This would save to database in real implementation
            logger.debug(f"Saved dashboard layout: {layout.layout_id}")
        except Exception as e:
            logger.error(f"Failed to save dashboard layout: {e}")

    async def shutdown(self) -> None:
        """Shutdown the dashboard controller."""
        logger.info("Shutting down Dashboard Controller...")
        
        self._running = False
        
        # Close all WebSocket connections
        for connection in self._websocket_connections.values():
            try:
                await connection.websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
        
        # Cancel dashboard tasks
        for task in self._dashboard_tasks:
            task.cancel()
        
        if self._dashboard_tasks:
            await asyncio.gather(*self._dashboard_tasks, return_exceptions=True)
        
        logger.info("Dashboard Controller shutdown complete")


# Create API router for dashboard endpoints
router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

# This would be injected as a dependency
dashboard_controller: Optional[DashboardController] = None

@router.get("/metrics")
async def get_dashboard_metrics(user_id -> None: int = 1) -> None:
    """Get comprehensive dashboard metrics."""
    if not dashboard_controller:
        raise HTTPException(status_code=503, detail="Dashboard controller not available")
    
    return await dashboard_controller.get_dashboard_metrics(user_id)

@router.get("/layouts")
async def get_dashboard_layouts(user_id -> None: int = 1) -> None:
    """Get dashboard layouts for user."""
    if not dashboard_controller:
        raise HTTPException(status_code=503, detail="Dashboard controller not available")
    
    return await dashboard_controller.get_user_dashboard_layouts(user_id)

@router.post("/layouts")
async def create_dashboard_layout(layout_data -> None: dict, user_id -> None: int = 1) -> None:
    """Create new dashboard layout."""
    if not dashboard_controller:
        raise HTTPException(status_code=503, detail="Dashboard controller not available")
    
    return await dashboard_controller.create_dashboard_layout(layout_data, user_id)

@router.get("/widget/{widget_type}")
async def get_widget_data(
    widget_type -> None: DashboardWidgetType,
    widget_id -> None: str = "default",
    config -> None: str = "{}"
) -> None:
    """Get data for dashboard widget."""
    if not dashboard_controller:
        raise HTTPException(status_code=503, detail="Dashboard controller not available")
    
    try:
        widget_config = json.loads(config)
    except json.JSONDecodeError:
        widget_config = {}
    
    return await dashboard_controller.get_widget_data(widget_id, widget_type, widget_config)

@router.websocket("/ws")
async def websocket_endpoint(websocket -> None: WebSocket, user_id -> None: int = 1) -> None:
    """WebSocket endpoint for real-time dashboard updates."""
    if not dashboard_controller:
        await websocket.close(code=1011, reason="Service unavailable")
        return
    
    await dashboard_controller.handle_websocket_connection(websocket, user_id)
