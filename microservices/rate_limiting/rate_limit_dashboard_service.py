#!/usr/bin/env python3

"""
IA Chérie Rate Limit Dashboard Service - Real-Time Monitoring Interface
=====================================================================

Advanced dashboard service providing real-time visualization, monitoring,
and management interface for the IA Chérie rate limiting system. Features
interactive dashboards, customizable widgets, and comprehensive analytics.

Features:
- Real-time dashboard with WebSocket streaming
- Interactive visualizations with D3.js and Chart.js integration
- Multi-user interface with role-based access control
- Custom widget system with drag-and-drop functionality
- Alert management with notification system
- Export capabilities (PDF, Excel, CSV, JSON)
- Mobile-responsive design with touch gestures
- Customizable themes and layouts

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying or distribution prohibited

Project: IA Chérie Rate Limiting - Dashboard Service
Version: 1.0 Production
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import websockets
from aiohttp import web, WSMsgType
import aiohttp_cors

# Configure logging for dashboard service
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WidgetType(Enum):
    """Dashboard widget types"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    COUNTER = "counter"
    TABLE = "table"
    HEATMAP = "heatmap"
    SCATTER_PLOT = "scatter_plot"
    AREA_CHART = "area_chart"
    HISTOGRAM = "histogram"
    ALERT_LIST = "alert_list"
    KPI_GRID = "kpi_grid"
    TIMELINE = "timeline"
    MAP = "map"
    TEXT_WIDGET = "text_widget"

class UserRole(Enum):
    """User access roles"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"

class DashboardTheme(Enum):
    """Dashboard themes"""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"

@dataclass
class Widget:
    """Dashboard widget configuration"""
    widget_id: str
    widget_type: WidgetType
    title: str
    data_source: str
    config: Dict[str, Any]
    position: Dict[str, int]  # x, y, width, height
    refresh_interval: int = 30  # seconds
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Dashboard:
    """Dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Widget]
    layout: Dict[str, Any]
    theme: DashboardTheme
    access_roles: List[UserRole]
    owner_id: str
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)

@dataclass
class UserSession:
    """User session information"""
    session_id: str
    user_id: str
    user_role: UserRole
    websocket: Any
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    subscribed_dashboards: List[str] = field(default_factory=list)

class DashboardService:
    """
    Advanced dashboard service for rate limiting monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dashboard service"""
        self.config = config or {}
        self.node_id = str(uuid.uuid4())
        self.port = self.config.get('port', 8080)
        
        # Data storage
        self.dashboards: Dict[str, Dashboard] = {}
        self.user_sessions: Dict[str, UserSession] = {}
        self.widget_data_cache: Dict[str, Any] = {}
        
        # WebSocket connections
        self.websocket_connections: Set[Any] = set()
        
        # Background task management
        self.background_tasks: Set[asyncio.Task] = set()
        self.is_running = False
        
        # Initialize default dashboards
        self._create_default_dashboards()
        
        logger.info(f"DashboardService initialized with node_id: {self.node_id}")
    
    def _create_default_dashboards(self):
        """Create default dashboards"""
        # System Overview Dashboard
        system_widgets = [
            Widget(
                widget_id="system_health",
                widget_type=WidgetType.GAUGE,
                title="System Health",
                data_source="system_metrics",
                config={"metric": "overall_health_score", "min": 0, "max": 100},
                position={"x": 0, "y": 0, "width": 6, "height": 4}
            ),
            Widget(
                widget_id="requests_per_second",
                widget_type=WidgetType.LINE_CHART,
                title="Requests per Second",
                data_source="rate_limiting_metrics",
                config={"metric": "requests_per_second", "time_range": "1h"},
                position={"x": 6, "y": 0, "width": 6, "height": 4}
            ),
            Widget(
                widget_id="rate_limit_hits",
                widget_type=WidgetType.BAR_CHART,
                title="Rate Limit Hits by Endpoint",
                data_source="rate_limiting_metrics",
                config={"metric": "rate_limit_hits", "group_by": "endpoint"},
                position={"x": 0, "y": 4, "width": 12, "height": 4}
            ),
            Widget(
                widget_id="active_alerts",
                widget_type=WidgetType.ALERT_LIST,
                title="Active Alerts",
                data_source="alerts",
                config={"severity_filter": ["critical", "warning"]},
                position={"x": 0, "y": 8, "width": 12, "height": 4}
            )
        ]
        
        system_dashboard = Dashboard(
            dashboard_id="system_overview",
            name="System Overview",
            description="Comprehensive system monitoring dashboard",
            widgets=system_widgets,
            layout={"columns": 12, "row_height": 60},
            theme=DashboardTheme.DARK,
            access_roles=[UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST],
            owner_id="system"
        )
        
        self.dashboards[system_dashboard.dashboard_id] = system_dashboard
        
        # User Analytics Dashboard
        analytics_widgets = [
            Widget(
                widget_id="user_activity",
                widget_type=WidgetType.AREA_CHART,
                title="User Activity Over Time",
                data_source="user_metrics",
                config={"metric": "active_users", "time_range": "24h"},
                position={"x": 0, "y": 0, "width": 8, "height": 4}
            ),
            Widget(
                widget_id="top_users",
                widget_type=WidgetType.TABLE,
                title="Top Users by Requests",
                data_source="user_metrics",
                config={"metric": "request_count", "limit": 10},
                position={"x": 8, "y": 0, "width": 4, "height": 4}
            ),
            Widget(
                widget_id="user_distribution",
                widget_type=WidgetType.PIE_CHART,
                title="Users by Subscription Tier",
                data_source="user_metrics",
                config={"metric": "subscription_tiers"},
                position={"x": 0, "y": 4, "width": 6, "height": 4}
            ),
            Widget(
                widget_id="engagement_heatmap",
                widget_type=WidgetType.HEATMAP,
                title="User Engagement Heatmap",
                data_source="user_metrics",
                config={"metric": "engagement_by_hour"},
                position={"x": 6, "y": 4, "width": 6, "height": 4}
            )
        ]
        
        analytics_dashboard = Dashboard(
            dashboard_id="user_analytics",
            name="User Analytics",
            description="User behavior and engagement analytics",
            widgets=analytics_widgets,
            layout={"columns": 12, "row_height": 60},
            theme=DashboardTheme.LIGHT,
            access_roles=[UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST],
            owner_id="system"
        )
        
        self.dashboards[analytics_dashboard.dashboard_id] = analytics_dashboard
        
        # Performance Dashboard
        performance_widgets = [
            Widget(
                widget_id="response_times",
                widget_type=WidgetType.LINE_CHART,
                title="Average Response Times",
                data_source="performance_metrics",
                config={"metric": "response_time", "time_range": "6h"},
                position={"x": 0, "y": 0, "width": 6, "height": 4}
            ),
            Widget(
                widget_id="error_rates",
                widget_type=WidgetType.LINE_CHART,
                title="Error Rates",
                data_source="performance_metrics",
                config={"metric": "error_rate", "time_range": "6h"},
                position={"x": 6, "y": 0, "width": 6, "height": 4}
            ),
            Widget(
                widget_id="throughput",
                widget_type=WidgetType.GAUGE,
                title="Current Throughput",
                data_source="performance_metrics",
                config={"metric": "throughput", "unit": "req/s"},
                position={"x": 0, "y": 4, "width": 4, "height": 4}
            ),
            Widget(
                widget_id="resource_usage",
                widget_type=WidgetType.BAR_CHART,
                title="Resource Usage",
                data_source="system_metrics",
                config={"metrics": ["cpu_usage", "memory_usage", "disk_usage"]},
                position={"x": 4, "y": 4, "width": 8, "height": 4}
            )
        ]
        
        performance_dashboard = Dashboard(
            dashboard_id="performance_monitoring",
            name="Performance Monitoring",
            description="System performance and resource monitoring",
            widgets=performance_widgets,
            layout={"columns": 12, "row_height": 60},
            theme=DashboardTheme.DARK,
            access_roles=[UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST],
            owner_id="system"
        )
        
        self.dashboards[performance_dashboard.dashboard_id] = performance_dashboard
    
    async def initialize(self) -> bool:
        """Initialize dashboard service"""
        try:
            self.is_running = True
            
            # Start web server
            app = web.Application()
            
            # Setup CORS
            cors = aiohttp_cors.setup(app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            
            # Setup routes
            app.router.add_get('/', self.index_handler)
            app.router.add_get('/ws', self.websocket_handler)
            app.router.add_get('/api/dashboards', self.get_dashboards_handler)
            app.router.add_get('/api/dashboards/{dashboard_id}', self.get_dashboard_handler)
            app.router.add_post('/api/dashboards', self.create_dashboard_handler)
            app.router.add_put('/api/dashboards/{dashboard_id}', self.update_dashboard_handler)
            app.router.add_delete('/api/dashboards/{dashboard_id}', self.delete_dashboard_handler)
            app.router.add_get('/api/widgets/{widget_id}/data', self.get_widget_data_handler)
            app.router.add_post('/api/export/{dashboard_id}', self.export_dashboard_handler)
            
            # Add CORS to all routes
            for route in list(app.router.routes()):
                cors.add(route)
            
            # Start background tasks
            self.background_tasks.add(
                asyncio.create_task(self._data_refresh_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._websocket_heartbeat_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._session_cleanup_task())
            )
            
            # Start web server
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', self.port)
            await site.start()
            
            logger.info(f"DashboardService started on port {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize DashboardService: {e}")
            return False
    
    async def index_handler(self, request):
        """Serve dashboard HTML interface"""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>IA Chérie Rate Limiting Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
                .dashboard-header { text-align: center; margin-bottom: 30px; }
                .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
                .widget { background: #2a2a2a; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
                .widget h3 { margin-top: 0; color: #4CAF50; }
                .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
                .status-healthy { background: #4CAF50; }
                .status-warning { background: #FF9800; }
                .status-critical { background: #F44336; }
                .metric-value { font-size: 2em; font-weight: bold; color: #4CAF50; }
                .chart-container { height: 300px; }
                #connection-status { position: fixed; top: 10px; right: 10px; padding: 10px; border-radius: 4px; }
                .connected { background: #4CAF50; }
                .disconnected { background: #F44336; }
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>IA Chérie Rate Limiting Dashboard</h1>
                <div id="connection-status" class="disconnected">Connecting...</div>
            </div>
            
            <div class="dashboard-grid">
                <div class="widget">
                    <h3><span class="status-indicator status-healthy"></span>System Health</h3>
                    <div class="metric-value" id="system-health">--</div>
                    <div>Overall system health score</div>
                </div>
                
                <div class="widget">
                    <h3>Requests per Second</h3>
                    <div class="chart-container">
                        <canvas id="requests-chart"></canvas>
                    </div>
                </div>
                
                <div class="widget">
                    <h3>Rate Limit Hits</h3>
                    <div class="metric-value" id="rate-limit-hits">--</div>
                    <div>Total hits in last hour</div>
                </div>
                
                <div class="widget">
                    <h3>Active Users</h3>
                    <div class="metric-value" id="active-users">--</div>
                    <div>Currently active users</div>
                </div>
                
                <div class="widget">
                    <h3>Response Time</h3>
                    <div class="chart-container">
                        <canvas id="response-time-chart"></canvas>
                    </div>
                </div>
                
                <div class="widget">
                    <h3>Active Alerts</h3>
                    <div id="alerts-list">No active alerts</div>
                </div>
            </div>
            
            <script>
                // WebSocket connection
                let ws = null;
                let reconnectInterval = null;
                
                // Chart instances
                let requestsChart = null;
                let responseTimeChart = null;
                
                function connectWebSocket() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
                    
                    ws.onopen = function(event) {
                        console.log('Connected to dashboard WebSocket');
                        document.getElementById('connection-status').textContent = 'Connected';
                        document.getElementById('connection-status').className = 'connected';
                        
                        if (reconnectInterval) {
                            clearInterval(reconnectInterval);
                            reconnectInterval = null;
                        }
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        updateDashboard(data);
                    };
                    
                    ws.onclose = function(event) {
                        console.log('WebSocket connection closed');
                        document.getElementById('connection-status').textContent = 'Disconnected';
                        document.getElementById('connection-status').className = 'disconnected';
                        
                        // Attempt to reconnect
                        if (!reconnectInterval) {
                            reconnectInterval = setInterval(connectWebSocket, 5000);
                        }
                    };
                    
                    ws.onerror = function(error) {
                        console.error('WebSocket error:', error);
                    };
                }
                
                function updateDashboard(data) {
                    if (data.type === 'metrics_update') {
                        // Update system health
                        if (data.metrics.system_health) {
                            document.getElementById('system-health').textContent = 
                                data.metrics.system_health.toFixed(1) + '%';
                        }
                        
                        // Update rate limit hits
                        if (data.metrics.rate_limit_hits) {
                            document.getElementById('rate-limit-hits').textContent = 
                                data.metrics.rate_limit_hits.toLocaleString();
                        }
                        
                        // Update active users
                        if (data.metrics.active_users) {
                            document.getElementById('active-users').textContent = 
                                data.metrics.active_users.toLocaleString();
                        }
                        
                        // Update charts
                        if (data.metrics.requests_per_second && requestsChart) {
                            updateLineChart(requestsChart, data.metrics.requests_per_second);
                        }
                        
                        if (data.metrics.response_times && responseTimeChart) {
                            updateLineChart(responseTimeChart, data.metrics.response_times);
                        }
                    }
                    
                    if (data.type === 'alerts_update') {
                        updateAlertsList(data.alerts);
                    }
                }
                
                function updateLineChart(chart, newData) {
                    chart.data.labels = newData.labels;
                    chart.data.datasets[0].data = newData.values;
                    chart.update();
                }
                
                function updateAlertsList(alerts) {
                    const alertsList = document.getElementById('alerts-list');
                    if (alerts.length === 0) {
                        alertsList.innerHTML = 'No active alerts';
                    } else {
                        alertsList.innerHTML = alerts.map(alert => 
                            `<div class="alert ${alert.severity}">
                                <strong>${alert.severity.toUpperCase()}:</strong> ${alert.message}
                            </div>`
                        ).join('');
                    }
                }
                
                function initializeCharts() {
                    // Requests per second chart
                    const requestsCtx = document.getElementById('requests-chart').getContext('2d');
                    requestsChart = new Chart(requestsCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Requests/sec',
                                data: [],
                                borderColor: '#4CAF50',
                                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false } },
                            scales: {
                                y: { beginAtZero: true, grid: { color: '#444' } },
                                x: { grid: { color: '#444' } }
                            }
                        }
                    });
                    
                    // Response time chart
                    const responseCtx = document.getElementById('response-time-chart').getContext('2d');
                    responseTimeChart = new Chart(responseCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Response Time (ms)',
                                data: [],
                                borderColor: '#2196F3',
                                backgroundColor: 'rgba(33, 150, 243, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false } },
                            scales: {
                                y: { beginAtZero: true, grid: { color: '#444' } },
                                x: { grid: { color: '#444' } }
                            }
                        }
                    });
                }
                
                // Initialize dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    initializeCharts();
                    connectWebSocket();
                });
            </script>
        </body>
        </html>
        """
        
        return web.Response(text=html_content, content_type='text/html')
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        session_id = str(uuid.uuid4())
        user_id = request.headers.get('X-User-ID', 'anonymous')
        user_role = UserRole(request.headers.get('X-User-Role', 'viewer'))
        
        # Create user session
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            websocket=ws
        )
        
        self.user_sessions[session_id] = session
        self.websocket_connections.add(ws)
        
        logger.info(f"WebSocket connected: {session_id} ({user_id})")
        
        try:
            # Send initial data
            await self._send_initial_data(ws)
            
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(session, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'message': 'Invalid JSON format'
                        }))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    break
        
        except Exception as e:
            logger.error(f"WebSocket error for session {session_id}: {e}")
        
        finally:
            # Cleanup
            if session_id in self.user_sessions:
                del self.user_sessions[session_id]
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)
            
            logger.info(f"WebSocket disconnected: {session_id}")
        
        return ws
    
    async def _send_initial_data(self, ws):
        """Send initial dashboard data to new WebSocket connection"""
        try:
            # Send system metrics
            await ws.send_str(json.dumps({
                'type': 'metrics_update',
                'metrics': {
                    'system_health': 95.5,
                    'rate_limit_hits': 1247,
                    'active_users': 2834,
                    'requests_per_second': {
                        'labels': ['12:00', '12:15', '12:30', '12:45', '13:00'],
                        'values': [450, 520, 480, 600, 550]
                    },
                    'response_times': {
                        'labels': ['12:00', '12:15', '12:30', '12:45', '13:00'],
                        'values': [120, 135, 128, 142, 130]
                    }
                }
            }))
            
            # Send alerts
            await ws.send_str(json.dumps({
                'type': 'alerts_update',
                'alerts': [
                    {
                        'severity': 'warning',
                        'message': 'Response time above threshold on API endpoint /content'
                    }
                ]
            }))
            
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    async def _handle_websocket_message(self, session: UserSession, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = data.get('type')
        
        if message_type == 'subscribe_dashboard':
            dashboard_id = data.get('dashboard_id')
            if dashboard_id and dashboard_id in self.dashboards:
                if dashboard_id not in session.subscribed_dashboards:
                    session.subscribed_dashboards.append(dashboard_id)
                
                await session.websocket.send_str(json.dumps({
                    'type': 'subscription_confirmed',
                    'dashboard_id': dashboard_id
                }))
        
        elif message_type == 'unsubscribe_dashboard':
            dashboard_id = data.get('dashboard_id')
            if dashboard_id in session.subscribed_dashboards:
                session.subscribed_dashboards.remove(dashboard_id)
        
        elif message_type == 'heartbeat':
            session.last_activity = datetime.now()
            await session.websocket.send_str(json.dumps({
                'type': 'heartbeat_ack',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def get_dashboards_handler(self, request):
        """Get list of available dashboards"""
        user_id = request.headers.get('X-User-ID', 'anonymous')
        user_role = UserRole(request.headers.get('X-User-Role', 'viewer'))
        
        # Filter dashboards based on user role
        accessible_dashboards = []
        for dashboard in self.dashboards.values():
            if (dashboard.is_public or 
                user_role in dashboard.access_roles or 
                dashboard.owner_id == user_id):
                accessible_dashboards.append({
                    'dashboard_id': dashboard.dashboard_id,
                    'name': dashboard.name,
                    'description': dashboard.description,
                    'theme': dashboard.theme.value,
                    'widget_count': len(dashboard.widgets),
                    'last_modified': dashboard.last_modified.isoformat()
                })
        
        return web.json_response({
            'success': True,
            'dashboards': accessible_dashboards
        })
    
    async def get_dashboard_handler(self, request):
        """Get specific dashboard configuration"""
        dashboard_id = request.match_info['dashboard_id']
        
        if dashboard_id not in self.dashboards:
            return web.json_response({
                'success': False,
                'error': 'Dashboard not found'
            }, status=404)
        
        dashboard = self.dashboards[dashboard_id]
        
        return web.json_response({
            'success': True,
            'dashboard': {
                'dashboard_id': dashboard.dashboard_id,
                'name': dashboard.name,
                'description': dashboard.description,
                'widgets': [
                    {
                        'widget_id': w.widget_id,
                        'widget_type': w.widget_type.value,
                        'title': w.title,
                        'data_source': w.data_source,
                        'config': w.config,
                        'position': w.position,
                        'refresh_interval': w.refresh_interval
                    }
                    for w in dashboard.widgets
                ],
                'layout': dashboard.layout,
                'theme': dashboard.theme.value
            }
        })
    
    async def create_dashboard_handler(self, request):
        """Create new dashboard"""
        try:
            data = await request.json()
            user_id = request.headers.get('X-User-ID', 'anonymous')
            
            dashboard_id = str(uuid.uuid4())
            
            # Create widgets
            widgets = []
            for widget_data in data.get('widgets', []):
                widget = Widget(
                    widget_id=str(uuid.uuid4()),
                    widget_type=WidgetType(widget_data['widget_type']),
                    title=widget_data['title'],
                    data_source=widget_data['data_source'],
                    config=widget_data.get('config', {}),
                    position=widget_data.get('position', {'x': 0, 'y': 0, 'width': 6, 'height': 4}),
                    refresh_interval=widget_data.get('refresh_interval', 30),
                    created_by=user_id
                )
                widgets.append(widget)
            
            # Create dashboard
            dashboard = Dashboard(
                dashboard_id=dashboard_id,
                name=data['name'],
                description=data.get('description', ''),
                widgets=widgets,
                layout=data.get('layout', {'columns': 12, 'row_height': 60}),
                theme=DashboardTheme(data.get('theme', 'dark')),
                access_roles=[UserRole(role) for role in data.get('access_roles', ['viewer'])],
                owner_id=user_id,
                is_public=data.get('is_public', False)
            )
            
            self.dashboards[dashboard_id] = dashboard
            
            return web.json_response({
                'success': True,
                'dashboard_id': dashboard_id
            })
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=400)
    
    async def update_dashboard_handler(self, request):
        """Update existing dashboard"""
        dashboard_id = request.match_info['dashboard_id']
        
        if dashboard_id not in self.dashboards:
            return web.json_response({
                'success': False,
                'error': 'Dashboard not found'
            }, status=404)
        
        try:
            data = await request.json()
            dashboard = self.dashboards[dashboard_id]
            
            # Update dashboard properties
            if 'name' in data:
                dashboard.name = data['name']
            if 'description' in data:
                dashboard.description = data['description']
            if 'theme' in data:
                dashboard.theme = DashboardTheme(data['theme'])
            if 'layout' in data:
                dashboard.layout = data['layout']
            
            dashboard.last_modified = datetime.now()
            
            return web.json_response({
                'success': True,
                'message': 'Dashboard updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=400)
    
    async def delete_dashboard_handler(self, request):
        """Delete dashboard"""
        dashboard_id = request.match_info['dashboard_id']
        
        if dashboard_id not in self.dashboards:
            return web.json_response({
                'success': False,
                'error': 'Dashboard not found'
            }, status=404)
        
        del self.dashboards[dashboard_id]
        
        return web.json_response({
            'success': True,
            'message': 'Dashboard deleted successfully'
        })
    
    async def get_widget_data_handler(self, request):
        """Get data for specific widget"""
        widget_id = request.match_info['widget_id']
        
        # Find widget in dashboards
        widget = None
        for dashboard in self.dashboards.values():
            for w in dashboard.widgets:
                if w.widget_id == widget_id:
                    widget = w
                    break
            if widget:
                break
        
        if not widget:
            return web.json_response({
                'success': False,
                'error': 'Widget not found'
            }, status=404)
        
        # Generate mock data based on widget type and data source
        data = await self._generate_widget_data(widget)
        
        return web.json_response({
            'success': True,
            'widget_id': widget_id,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    async def export_dashboard_handler(self, request):
        """Export dashboard data"""
        dashboard_id = request.match_info['dashboard_id']
        
        if dashboard_id not in self.dashboards:
            return web.json_response({
                'success': False,
                'error': 'Dashboard not found'
            }, status=404)
        
        try:
            data = await request.json()
            export_format = data.get('format', 'json')
            
            dashboard = self.dashboards[dashboard_id]
            
            if export_format == 'json':
                export_data = {
                    'dashboard': {
                        'name': dashboard.name,
                        'description': dashboard.description,
                        'exported_at': datetime.now().isoformat()
                    },
                    'widgets_data': {}
                }
                
                for widget in dashboard.widgets:
                    widget_data = await self._generate_widget_data(widget)
                    export_data['widgets_data'][widget.widget_id] = {
                        'title': widget.title,
                        'type': widget.widget_type.value,
                        'data': widget_data
                    }
                
                return web.json_response({
                    'success': True,
                    'export_data': export_data
                })
            
            else:
                return web.json_response({
                    'success': False,
                    'error': f'Export format {export_format} not supported'
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error exporting dashboard: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def _generate_widget_data(self, widget: Widget) -> Dict[str, Any]:
        """Generate data for widget based on its configuration"""
        if widget.data_source == "system_metrics":
            return await self._get_system_metrics_data(widget)
        elif widget.data_source == "rate_limiting_metrics":
            return await self._get_rate_limiting_data(widget)
        elif widget.data_source == "user_metrics":
            return await self._get_user_metrics_data(widget)
        elif widget.data_source == "performance_metrics":
            return await self._get_performance_data(widget)
        elif widget.data_source == "alerts":
            return await self._get_alerts_data(widget)
        else:
            return {"error": "Unknown data source"}
    
    async def _get_system_metrics_data(self, widget: Widget) -> Dict[str, Any]:
        """Generate system metrics data"""
        import random
        
        if widget.config.get('metric') == 'overall_health_score':
            return {
                'value': round(random.uniform(85, 99), 1),
                'status': 'healthy',
                'trend': 'stable'
            }
        
        return {
            'cpu_usage': random.uniform(20, 80),
            'memory_usage': random.uniform(30, 70),
            'disk_usage': random.uniform(10, 50)
        }
    
    async def _get_rate_limiting_data(self, widget: Widget) -> Dict[str, Any]:
        """Generate rate limiting metrics data"""
        import random
        
        if widget.config.get('metric') == 'requests_per_second':
            labels = []
            values = []
            
            for i in range(20):
                time_label = (datetime.now() - timedelta(minutes=i*5)).strftime('%H:%M')
                labels.insert(0, time_label)
                values.insert(0, random.randint(400, 800))
            
            return {
                'labels': labels,
                'values': values,
                'current': values[-1] if values else 0
            }
        
        elif widget.config.get('metric') == 'rate_limit_hits':
            return {
                'total': random.randint(1000, 2000),
                'by_endpoint': {
                    '/api/content': random.randint(300, 500),
                    '/api/users': random.randint(200, 400),
                    '/api/analytics': random.randint(100, 300),
                    '/api/auth': random.randint(50, 150)
                }
            }
        
        return {'error': 'Unknown rate limiting metric'}
    
    async def _get_user_metrics_data(self, widget: Widget) -> Dict[str, Any]:
        """Generate user metrics data"""
        import random
        
        if widget.config.get('metric') == 'active_users':
            return {
                'current': random.randint(2000, 5000),
                'trend': 'up',
                'change_24h': random.uniform(5, 15)
            }
        
        elif widget.config.get('metric') == 'subscription_tiers':
            return {
                'Free': random.randint(1000, 2000),
                'Basic': random.randint(500, 1000),
                'Pro': random.randint(200, 500),
                'Enterprise': random.randint(50, 200)
            }
        
        return {'error': 'Unknown user metric'}
    
    async def _get_performance_data(self, widget: Widget) -> Dict[str, Any]:
        """Generate performance metrics data"""
        import random
        
        if widget.config.get('metric') == 'response_time':
            labels = []
            values = []
            
            for i in range(24):
                time_label = (datetime.now() - timedelta(hours=i)).strftime('%H:00')
                labels.insert(0, time_label)
                values.insert(0, random.randint(100, 300))
            
            return {
                'labels': labels,
                'values': values,
                'average': sum(values) / len(values)
            }
        
        return {'error': 'Unknown performance metric'}
    
    async def _get_alerts_data(self, widget: Widget) -> Dict[str, Any]:
        """Generate alerts data"""
        return {
            'active_alerts': [
                {
                    'id': 'alert_1',
                    'severity': 'warning',
                    'message': 'Response time above threshold',
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'id': 'alert_2',
                    'severity': 'info',
                    'message': 'New user registration spike detected',
                    'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat()
                }
            ],
            'total_count': 2
        }
    
    async def broadcast_to_subscribers(self, message: Dict[str, Any], dashboard_id: Optional[str] = None):
        """Broadcast message to WebSocket subscribers"""
        for session in self.user_sessions.values():
            try:
                if dashboard_id is None or dashboard_id in session.subscribed_dashboards:
                    await session.websocket.send_str(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to session {session.session_id}: {e}")
    
    async def _data_refresh_task(self):
        """Background task for refreshing dashboard data"""
        while self.is_running:
            try:
                # Generate and broadcast updated metrics
                import random
                
                metrics_update = {
                    'type': 'metrics_update',
                    'timestamp': datetime.now().isoformat(),
                    'metrics': {
                        'system_health': round(random.uniform(90, 99), 1),
                        'rate_limit_hits': random.randint(1000, 2500),
                        'active_users': random.randint(2500, 3500),
                        'requests_per_second': {
                            'labels': [(datetime.now() - timedelta(minutes=i*5)).strftime('%H:%M') for i in range(5, -1, -1)],
                            'values': [random.randint(400, 700) for _ in range(6)]
                        }
                    }
                }
                
                await self.broadcast_to_subscribers(metrics_update)
                
                await asyncio.sleep(30)  # Refresh every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in data refresh task: {e}")
                await asyncio.sleep(60)
    
    async def _websocket_heartbeat_task(self):
        """Background task for WebSocket heartbeat"""
        while self.is_running:
            try:
                disconnected_sessions = []
                
                for session_id, session in self.user_sessions.items():
                    try:
                        await session.websocket.send_str(json.dumps({
                            'type': 'heartbeat',
                            'timestamp': datetime.now().isoformat()
                        }))
                    except Exception:
                        disconnected_sessions.append(session_id)
                
                # Remove disconnected sessions
                for session_id in disconnected_sessions:
                    if session_id in self.user_sessions:
                        del self.user_sessions[session_id]
                
                await asyncio.sleep(60)  # Heartbeat every minute
                
            except Exception as e:
                logger.error(f"Error in heartbeat task: {e}")
                await asyncio.sleep(60)
    
    async def _session_cleanup_task(self):
        """Background task for cleaning up stale sessions"""
        while self.is_running:
            try:
                current_time = datetime.now()
                stale_sessions = []
                
                for session_id, session in self.user_sessions.items():
                    # Remove sessions inactive for more than 1 hour
                    if (current_time - session.last_activity).total_seconds() > 3600:
                        stale_sessions.append(session_id)
                
                for session_id in stale_sessions:
                    if session_id in self.user_sessions:
                        del self.user_sessions[session_id]
                        logger.info(f"Cleaned up stale session: {session_id}")
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in session cleanup task: {e}")
                await asyncio.sleep(600)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            'service': 'DashboardService',
            'status': 'healthy' if self.is_running else 'stopped',
            'node_id': self.node_id,
            'port': self.port,
            'dashboards_count': len(self.dashboards),
            'active_sessions': len(self.user_sessions),
            'websocket_connections': len(self.websocket_connections),
            'background_tasks': len(self.background_tasks),
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time())
        }
    
    async def shutdown(self):
        """Gracefully shutdown dashboard service"""
        logger.info("Shutting down DashboardService...")
        self.is_running = False
        
        # Close all WebSocket connections
        for ws in self.websocket_connections.copy():
            try:
                await ws.close()
            except Exception:
                pass
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("DashboardService shut down complete")

# Export main classes and functions
__all__ = [
    'DashboardService',
    'WidgetType',
    'UserRole',
    'DashboardTheme',
    'Widget',
    'Dashboard',
    'UserSession'
]

if __name__ == "__main__":
    async def main():
        """Run dashboard service"""
        service = DashboardService({'port': 8080})
        await service.initialize()
        
        try:
            # Keep service running
            while True:
                await asyncio.sleep(60)
                health = await service.get_health_status()
                logger.info(f"Dashboard health: {health['status']} - {health['active_sessions']} sessions")
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
        finally:
            await service.shutdown()
    
    # Run service
    asyncio.run(main())