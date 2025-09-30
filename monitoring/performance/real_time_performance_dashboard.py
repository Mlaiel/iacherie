"""
⚠️ CONFIDENTIEL - IA Chérie Creator Platform ⚠️

Real-Time Performance Dashboard - Enterprise Performance Monitoring
Advanced real-time performance visualization and alerting for Creator Economy

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import json
import websockets
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import statistics
from prometheus_client import Gauge, Counter, Histogram, generate_latest
import aiohttp
from aiohttp import web, WSMsgType
import weakref
import threading
from concurrent.futures import ThreadPoolExecutor
import plotly.graph_objs as go
import plotly.utils
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class DashboardMetrics:
    """Real-time dashboard metrics"""
    metric_type: str  # cpu, memory, network, api, database
    metric_name: str
    current_value: float
    previous_value: float
    trend: str  # increasing, decreasing, stable
    threshold_status: str  # normal, warning, critical
    unit: str
    timestamp: datetime
    
@dataclass
class AlertMetrics:
    """Performance alert metrics"""
    alert_id: str
    alert_type: str  # threshold, anomaly, trend
    severity: str  # info, warning, error, critical
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    suggested_action: str
    affected_components: List[str]
    timestamp: datetime
    acknowledged: bool = False

@dataclass
class PerformanceTrendMetrics:
    """Performance trend analysis"""
    metric_name: str
    time_series: List[Tuple[datetime, float]]
    trend_direction: str  # up, down, stable
    trend_strength: float  # 0-1
    forecast_values: List[float]
    anomaly_score: float
    seasonal_pattern: bool
    timestamp: datetime

@dataclass
class WebSocketSession:
    """WebSocket session information"""
    session_id: str
    websocket: Any
    subscribed_metrics: Set[str]
    user_id: Optional[str]
    dashboard_config: Dict[str, Any]
    last_ping: datetime
    connected_at: datetime

class RealTimePerformanceDashboard:
    """
    Enterprise-grade real-time performance dashboard
    Provides WebSocket streaming, anomaly detection, and intelligent alerting
    """
    
    def __init__(self,
                 redis_url: str = "redis://localhost:6379",
                 websocket_port: int = 8765,
                 http_port: int = 8080,
                 update_interval: float = 1.0,
                 enable_anomaly_detection: bool = True,
                 enable_predictive_alerting: bool = True):
        """
        Initialize real-time performance dashboard
        
        Args:
            redis_url: Redis URL for pub/sub and caching
            websocket_port: WebSocket server port
            http_port: HTTP server port for dashboard UI
            update_interval: Metrics update interval in seconds
            enable_anomaly_detection: Enable ML-based anomaly detection
            enable_predictive_alerting: Enable predictive alerting
        """
        self.redis_url = redis_url
        self.websocket_port = websocket_port
        self.http_port = http_port
        self.update_interval = update_interval
        self.enable_anomaly_detection = enable_anomaly_detection
        self.enable_predictive_alerting = enable_predictive_alerting
        
        # Server components
        self.websocket_server = None
        self.http_server = None
        self.redis_client = None
        self.redis_subscriber = None
        
        # Dashboard state
        self.active_sessions: Dict[str, WebSocketSession] = {}
        self.metric_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_cache: deque = deque(maxlen=1000)
        self.trend_cache: Dict[str, PerformanceTrendMetrics] = {}
        
        # Real-time metrics
        self.current_metrics: Dict[str, DashboardMetrics] = {}
        self.metric_thresholds: Dict[str, Dict] = {
            'cpu_usage_percent': {'warning': 80, 'critical': 95},
            'memory_usage_percent': {'warning': 85, 'critical': 95},
            'api_response_time_ms': {'warning': 1000, 'critical': 5000},
            'database_query_time_ms': {'warning': 500, 'critical': 2000},
            'error_rate_percent': {'warning': 5, 'critical': 15}
        }
        
        # Anomaly detection
        self.anomaly_models: Dict[str, Any] = {}
        self.anomaly_baselines: Dict[str, Dict] = {}
        
        # Dashboard configuration
        self.dashboard_layouts = {
            'overview': {
                'widgets': [
                    {'type': 'gauge', 'metric': 'cpu_usage_percent', 'size': 'medium'},
                    {'type': 'gauge', 'metric': 'memory_usage_percent', 'size': 'medium'},
                    {'type': 'line_chart', 'metric': 'api_response_time_ms', 'size': 'large'},
                    {'type': 'alert_panel', 'size': 'medium'}
                ]
            },
            'infrastructure': {
                'widgets': [
                    {'type': 'heatmap', 'metric': 'server_health', 'size': 'large'},
                    {'type': 'line_chart', 'metric': 'network_latency_ms', 'size': 'medium'},
                    {'type': 'bar_chart', 'metric': 'disk_usage_percent', 'size': 'medium'}
                ]
            },
            'application': {
                'widgets': [
                    {'type': 'line_chart', 'metric': 'request_rate_rps', 'size': 'large'},
                    {'type': 'pie_chart', 'metric': 'status_code_distribution', 'size': 'medium'},
                    {'type': 'table', 'metric': 'slow_endpoints', 'size': 'large'}
                ]
            }
        }
        
        # Running state
        self.running = False
        self._background_tasks = []
    
    async def initialize(self):
        """Initialize dashboard components"""
        try:
            # Initialize Redis connection
            self.redis_client = await aioredis.from_url(self.redis_url)
            logger.info("Redis connection established")
            
            # Initialize anomaly detection models
            if self.enable_anomaly_detection:
                await self._initialize_anomaly_detection()
            
            # Setup metric subscriptions
            await self._setup_metric_subscriptions()
            
        except Exception as e:
            logger.error(f"Error initializing dashboard: {e}")
            raise
    
    async def _initialize_anomaly_detection(self):
        """Initialize anomaly detection models"""
        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler
            
            # Initialize models for different metric types
            for metric_name in self.metric_thresholds.keys():
                self.anomaly_models[metric_name] = {
                    'model': IsolationForest(contamination=0.1, random_state=42),
                    'scaler': StandardScaler(),
                    'trained': False,
                    'training_data': deque(maxlen=1000)
                }
            
            logger.info("Anomaly detection models initialized")
            
        except ImportError:
            logger.warning("Scikit-learn not available, anomaly detection disabled")
            self.enable_anomaly_detection = False
    
    async def _setup_metric_subscriptions(self):
        """Setup Redis pub/sub for metrics"""
        try:
            self.redis_subscriber = self.redis_client.pubsub()
            await self.redis_subscriber.subscribe('performance_metrics')
            logger.info("Metric subscriptions established")
        except Exception as e:
            logger.error(f"Error setting up metric subscriptions: {e}")
    
    async def start_servers(self):
        """Start WebSocket and HTTP servers"""
        if self.running:
            logger.warning("Dashboard servers already running")
            return
        
        self.running = True
        
        # Start WebSocket server
        websocket_task = asyncio.create_task(self._start_websocket_server())
        
        # Start HTTP server
        http_task = asyncio.create_task(self._start_http_server())
        
        # Start background tasks
        background_tasks = [
            self._metrics_processing_loop(),
            self._anomaly_detection_loop(),
            self._alert_processing_loop(),
            self._session_management_loop()
        ]
        
        self._background_tasks = [
            websocket_task,
            http_task
        ] + [asyncio.create_task(task) for task in background_tasks]
        
        logger.info("Dashboard servers started")
    
    async def stop_servers(self):
        """Stop all dashboard servers"""
        self.running = False
        
        # Cancel all background tasks
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket connections
        for session in list(self.active_sessions.values()):
            await session.websocket.close()
        
        # Close Redis connections
        if self.redis_subscriber:
            await self.redis_subscriber.unsubscribe()
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Dashboard servers stopped")
    
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        async def handle_websocket(websocket, path):
            session_id = f"session_{int(time.time())}_{id(websocket)}"
            
            try:
                # Register session
                session = WebSocketSession(
                    session_id=session_id,
                    websocket=websocket,
                    subscribed_metrics=set(),
                    user_id=None,
                    dashboard_config={},
                    last_ping=datetime.utcnow(),
                    connected_at=datetime.utcnow()
                )
                
                self.active_sessions[session_id] = session
                logger.info(f"WebSocket session connected: {session_id}")
                
                # Handle messages
                async for message in websocket:
                    if message.type == WSMsgType.TEXT:
                        await self._handle_websocket_message(session, json.loads(message.data))
                    elif message.type == WSMsgType.ERROR:
                        logger.error(f"WebSocket error: {websocket.exception()}")
                        break
                
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"WebSocket session disconnected: {session_id}")
            except Exception as e:
                logger.error(f"Error in WebSocket handler: {e}")
            finally:
                # Cleanup session
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
        
        # Start WebSocket server
        self.websocket_server = await websockets.serve(
            handle_websocket,
            "localhost",
            self.websocket_port
        )
        
        logger.info(f"WebSocket server started on port {self.websocket_port}")
        
        # Keep server running
        await self.websocket_server.wait_closed()
    
    async def _start_http_server(self):
        """Start HTTP server for dashboard UI"""
        app = web.Application()
        
        # Setup routes
        app.router.add_get('/', self._serve_dashboard)
        app.router.add_get('/api/metrics', self._api_get_metrics)
        app.router.add_get('/api/alerts', self._api_get_alerts)
        app.router.add_post('/api/alerts/{alert_id}/acknowledge', self._api_acknowledge_alert)
        app.router.add_get('/api/dashboard/config', self._api_get_dashboard_config)
        app.router.add_post('/api/dashboard/config', self._api_set_dashboard_config)
        app.router.add_static('/static', 'static')
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.http_port)
        await site.start()
        
        logger.info(f"HTTP server started on port {self.http_port}")
    
    async def _handle_websocket_message(self, session: WebSocketSession, message: Dict):
        """Handle WebSocket message from client"""
        try:
            msg_type = message.get('type')
            
            if msg_type == 'subscribe':
                # Subscribe to metrics
                metrics = message.get('metrics', [])
                session.subscribed_metrics.update(metrics)
                
                # Send current values
                for metric_name in metrics:
                    if metric_name in self.current_metrics:
                        await self._send_metric_update(session, metric_name)
                
            elif msg_type == 'unsubscribe':
                # Unsubscribe from metrics
                metrics = message.get('metrics', [])
                session.subscribed_metrics.difference_update(metrics)
                
            elif msg_type == 'ping':
                # Handle ping
                session.last_ping = datetime.utcnow()
                await session.websocket.send(json.dumps({'type': 'pong'}))
                
            elif msg_type == 'configure_dashboard':
                # Update dashboard configuration
                session.dashboard_config = message.get('config', {})
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _send_metric_update(self, session: WebSocketSession, metric_name: str):
        """Send metric update to WebSocket session"""
        if metric_name in self.current_metrics:
            metric = self.current_metrics[metric_name]
            
            update_message = {
                'type': 'metric_update',
                'metric_name': metric_name,
                'data': asdict(metric),
                'timestamp': metric.timestamp.isoformat()
            }
            
            try:
                await session.websocket.send(json.dumps(update_message))
            except Exception as e:
                logger.error(f"Error sending metric update: {e}")
    
    async def _broadcast_metric_update(self, metric_name: str):
        """Broadcast metric update to all subscribed sessions"""
        for session in list(self.active_sessions.values()):
            if metric_name in session.subscribed_metrics:
                await self._send_metric_update(session, metric_name)
    
    async def _broadcast_alert(self, alert: AlertMetrics):
        """Broadcast alert to all sessions"""
        alert_message = {
            'type': 'alert',
            'data': asdict(alert),
            'timestamp': alert.timestamp.isoformat()
        }
        
        for session in list(self.active_sessions.values()):
            try:
                await session.websocket.send(json.dumps(alert_message))
            except Exception as e:
                logger.error(f"Error broadcasting alert: {e}")
    
    def update_metric(self, metric_name: str, value: float, unit: str = ""):
        """Update metric value and trigger dashboard updates"""
        current_time = datetime.utcnow()
        
        # Get previous value
        previous_value = 0.0
        if metric_name in self.current_metrics:
            previous_value = self.current_metrics[metric_name].current_value
        
        # Calculate trend
        trend = "stable"
        if value > previous_value * 1.05:
            trend = "increasing"
        elif value < previous_value * 0.95:
            trend = "decreasing"
        
        # Determine threshold status
        threshold_status = self._get_threshold_status(metric_name, value)
        
        # Create metric object
        metric = DashboardMetrics(
            metric_type=self._get_metric_type(metric_name),
            metric_name=metric_name,
            current_value=value,
            previous_value=previous_value,
            trend=trend,
            threshold_status=threshold_status,
            unit=unit,
            timestamp=current_time
        )
        
        # Store metric
        self.current_metrics[metric_name] = metric
        self.metric_cache[metric_name].append((current_time, value))
        
        # Schedule broadcast (async)
        asyncio.create_task(self._broadcast_metric_update(metric_name))
        
        # Check for alerts
        asyncio.create_task(self._check_metric_alerts(metric))
        
        # Update anomaly detection
        if self.enable_anomaly_detection:
            asyncio.create_task(self._update_anomaly_detection(metric_name, value))
    
    def _get_metric_type(self, metric_name: str) -> str:
        """Determine metric type from metric name"""
        if 'cpu' in metric_name.lower():
            return 'cpu'
        elif 'memory' in metric_name.lower():
            return 'memory'
        elif 'network' in metric_name.lower() or 'latency' in metric_name.lower():
            return 'network'
        elif 'api' in metric_name.lower() or 'response' in metric_name.lower():
            return 'api'
        elif 'database' in metric_name.lower() or 'query' in metric_name.lower():
            return 'database'
        else:
            return 'custom'
    
    def _get_threshold_status(self, metric_name: str, value: float) -> str:
        """Get threshold status for metric"""
        if metric_name in self.metric_thresholds:
            thresholds = self.metric_thresholds[metric_name]
            
            if value >= thresholds.get('critical', float('inf')):
                return 'critical'
            elif value >= thresholds.get('warning', float('inf')):
                return 'warning'
        
        return 'normal'
    
    async def _check_metric_alerts(self, metric: DashboardMetrics):
        """Check metric for alert conditions"""
        alerts = []
        
        # Threshold-based alerts
        if metric.threshold_status in ['warning', 'critical']:
            alert = AlertMetrics(
                alert_id=f"threshold_{metric.metric_name}_{int(time.time())}",
                alert_type='threshold',
                severity=metric.threshold_status,
                metric_name=metric.metric_name,
                current_value=metric.current_value,
                threshold_value=self.metric_thresholds.get(metric.metric_name, {}).get(metric.threshold_status, 0),
                message=f"{metric.metric_name} is {metric.threshold_status}: {metric.current_value:.2f} {metric.unit}",
                suggested_action=self._get_suggested_action(metric),
                affected_components=self._get_affected_components(metric.metric_name),
                timestamp=datetime.utcnow()
            )
            alerts.append(alert)
        
        # Trend-based alerts
        if metric.trend == "increasing" and metric.current_value > metric.previous_value * 1.5:
            alert = AlertMetrics(
                alert_id=f"trend_{metric.metric_name}_{int(time.time())}",
                alert_type='trend',
                severity='warning',
                metric_name=metric.metric_name,
                current_value=metric.current_value,
                threshold_value=metric.previous_value,
                message=f"Rapid increase detected in {metric.metric_name}: {((metric.current_value/metric.previous_value - 1) * 100):.1f}% increase",
                suggested_action="Investigate recent changes or increased load",
                affected_components=self._get_affected_components(metric.metric_name),
                timestamp=datetime.utcnow()
            )
            alerts.append(alert)
        
        # Store and broadcast alerts
        for alert in alerts:
            self.alert_cache.append(alert)
            await self._broadcast_alert(alert)
    
    def _get_suggested_action(self, metric: DashboardMetrics) -> str:
        """Get suggested action for metric alert"""
        actions = {
            'cpu_usage_percent': 'Check for high CPU processes, consider scaling',
            'memory_usage_percent': 'Check for memory leaks, restart services if needed',
            'api_response_time_ms': 'Check database queries, optimize slow endpoints',
            'database_query_time_ms': 'Analyze slow queries, check indexes',
            'error_rate_percent': 'Check error logs, investigate failing requests'
        }
        
        return actions.get(metric.metric_name, 'Monitor metric and investigate if trend continues')
    
    def _get_affected_components(self, metric_name: str) -> List[str]:
        """Get components affected by metric"""
        component_mapping = {
            'cpu_usage_percent': ['application_server', 'background_workers'],
            'memory_usage_percent': ['application_server', 'cache_layer'],
            'api_response_time_ms': ['api_gateway', 'application_server', 'database'],
            'database_query_time_ms': ['database', 'application_server'],
            'error_rate_percent': ['application_server', 'api_gateway']
        }
        
        return component_mapping.get(metric_name, ['unknown'])
    
    async def _update_anomaly_detection(self, metric_name: str, value: float):
        """Update anomaly detection model"""
        if metric_name not in self.anomaly_models:
            return
        
        model_data = self.anomaly_models[metric_name]
        model_data['training_data'].append(value)
        
        # Train model if we have enough data
        if len(model_data['training_data']) >= 100 and not model_data['trained']:
            try:
                data = np.array(list(model_data['training_data'])).reshape(-1, 1)
                data_scaled = model_data['scaler'].fit_transform(data)
                model_data['model'].fit(data_scaled)
                model_data['trained'] = True
                logger.info(f"Anomaly detection model trained for {metric_name}")
            except Exception as e:
                logger.error(f"Error training anomaly model for {metric_name}: {e}")
        
        # Detect anomalies if model is trained
        if model_data['trained']:
            try:
                value_scaled = model_data['scaler'].transform([[value]])
                anomaly_score = model_data['model'].decision_function(value_scaled)[0]
                is_anomaly = model_data['model'].predict(value_scaled)[0] == -1
                
                if is_anomaly:
                    alert = AlertMetrics(
                        alert_id=f"anomaly_{metric_name}_{int(time.time())}",
                        alert_type='anomaly',
                        severity='warning',
                        metric_name=metric_name,
                        current_value=value,
                        threshold_value=0,
                        message=f"Anomaly detected in {metric_name}: {value:.2f} (score: {anomaly_score:.3f})",
                        suggested_action="Investigate unusual behavior pattern",
                        affected_components=self._get_affected_components(metric_name),
                        timestamp=datetime.utcnow()
                    )
                    
                    self.alert_cache.append(alert)
                    await self._broadcast_alert(alert)
                    
            except Exception as e:
                logger.error(f"Error in anomaly detection for {metric_name}: {e}")
    
    async def _serve_dashboard(self, request):
        """Serve dashboard HTML"""
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
    
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>IA Chérie Performance Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .header { background: #2c3e50; color: white; padding: 20px; margin: -20px -20px 20px -20px; }
                .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
                .widget { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric-value { font-size: 2em; font-weight: bold; }
                .metric-trend { font-size: 0.9em; margin-top: 5px; }
                .status-normal { color: #27ae60; }
                .status-warning { color: #f39c12; }
                .status-critical { color: #e74c3c; }
                .alert-panel { max-height: 300px; overflow-y: auto; }
                .alert-item { padding: 10px; margin: 5px 0; border-left: 4px solid; border-radius: 4px; }
                .alert-critical { border-color: #e74c3c; background: #fdf2f2; }
                .alert-warning { border-color: #f39c12; background: #fef9e7; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 IA Chérie Creator Platform - Performance Dashboard</h1>
                <p>Real-time performance monitoring and alerting</p>
            </div>
            
            <div class="dashboard-grid">
                <div class="widget">
                    <h3>CPU Usage</h3>
                    <div id="cpu-gauge"></div>
                </div>
                
                <div class="widget">
                    <h3>Memory Usage</h3>
                    <div id="memory-gauge"></div>
                </div>
                
                <div class="widget">
                    <h3>API Response Time</h3>
                    <div id="api-chart"></div>
                </div>
                
                <div class="widget">
                    <h3>Active Alerts</h3>
                    <div id="alerts-panel" class="alert-panel"></div>
                </div>
            </div>
            
            <script>
                // WebSocket connection
                const ws = new WebSocket('ws://localhost:8765');
                
                ws.onopen = function() {
                    console.log('Connected to dashboard');
                    ws.send(JSON.stringify({
                        type: 'subscribe',
                        metrics: ['cpu_usage_percent', 'memory_usage_percent', 'api_response_time_ms']
                    }));
                };
                
                ws.onmessage = function(event) {
                    const message = JSON.parse(event.data);
                    
                    if (message.type === 'metric_update') {
                        updateMetricWidget(message.metric_name, message.data);
                    } else if (message.type === 'alert') {
                        addAlert(message.data);
                    }
                };
                
                function updateMetricWidget(metricName, data) {
                    if (metricName === 'cpu_usage_percent') {
                        updateGauge('cpu-gauge', data.current_value, 'CPU %', data.threshold_status);
                    } else if (metricName === 'memory_usage_percent') {
                        updateGauge('memory-gauge', data.current_value, 'Memory %', data.threshold_status);
                    } else if (metricName === 'api_response_time_ms') {
                        updateChart('api-chart', data.current_value);
                    }
                }
                
                function updateGauge(elementId, value, title, status) {
                    const color = status === 'critical' ? 'red' : status === 'warning' ? 'orange' : 'green';
                    
                    const data = [{
                        type: 'indicator',
                        mode: 'gauge+number',
                        value: value,
                        title: { text: title },
                        gauge: {
                            axis: { range: [null, 100] },
                            bar: { color: color },
                            steps: [
                                { range: [0, 50], color: 'lightgray' },
                                { range: [50, 80], color: 'gray' }
                            ],
                            threshold: {
                                line: { color: 'red', width: 4 },
                                thickness: 0.75,
                                value: 90
                            }
                        }
                    }];
                    
                    Plotly.newPlot(elementId, data);
                }
                
                function updateChart(elementId, value) {
                    // This would update a time series chart
                    console.log('Updating chart:', elementId, value);
                }
                
                function addAlert(alert) {
                    const alertsPanel = document.getElementById('alerts-panel');
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert-item alert-${alert.severity}`;
                    alertDiv.innerHTML = `
                        <strong>${alert.severity.toUpperCase()}</strong>: ${alert.message}
                        <br><small>${alert.suggested_action}</small>
                        <br><em>${new Date(alert.timestamp).toLocaleString()}</em>
                    `;
                    
                    alertsPanel.insertBefore(alertDiv, alertsPanel.firstChild);
                    
                    // Keep only last 10 alerts
                    while (alertsPanel.children.length > 10) {
                        alertsPanel.removeChild(alertsPanel.lastChild);
                    }
                }
                
                // Ping every 30 seconds
                setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'ping' }));
                    }
                }, 30000);
            </script>
        </body>
        </html>
        """
    
    async def _api_get_metrics(self, request):
        """API endpoint to get current metrics"""
        metrics_data = {
            name: asdict(metric)
            for name, metric in self.current_metrics.items()
        }
        return web.json_response(metrics_data)
    
    async def _api_get_alerts(self, request):
        """API endpoint to get recent alerts"""
        alerts_data = [asdict(alert) for alert in list(self.alert_cache)[-50:]]
        return web.json_response(alerts_data)
    
    async def _api_acknowledge_alert(self, request):
        """API endpoint to acknowledge alert"""
        alert_id = request.match_info['alert_id']
        
        # Find and acknowledge alert
        for alert in self.alert_cache:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return web.json_response({'status': 'acknowledged'})
        
        return web.json_response({'error': 'Alert not found'}, status=404)
    
    async def _api_get_dashboard_config(self, request):
        """API endpoint to get dashboard configuration"""
        return web.json_response(self.dashboard_layouts)
    
    async def _api_set_dashboard_config(self, request):
        """API endpoint to set dashboard configuration"""
        config_data = await request.json()
        # Would save configuration to database or file
        return web.json_response({'status': 'saved'})
    
    async def _metrics_processing_loop(self):
        """Process incoming metrics from Redis"""
        while self.running:
            try:
                if self.redis_subscriber:
                    message = await self.redis_subscriber.get_message(timeout=1)
                    if message and message['type'] == 'message':
                        metric_data = json.loads(message['data'])
                        
                        metric_name = metric_data.get('name')
                        value = metric_data.get('value')
                        unit = metric_data.get('unit', '')
                        
                        if metric_name and value is not None:
                            self.update_metric(metric_name, value, unit)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _anomaly_detection_loop(self):
        """Anomaly detection processing loop"""
        while self.running:
            try:
                if self.enable_anomaly_detection:
                    # Process trend analysis
                    for metric_name, metric_data in self.metric_cache.items():
                        if len(metric_data) >= 50:  # Need sufficient data points
                            await self._analyze_metric_trends(metric_name, list(metric_data))
                
                await asyncio.sleep(60)  # Run every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in anomaly detection loop: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_metric_trends(self, metric_name: str, data_points: List[Tuple[datetime, float]]):
        """Analyze metric trends for predictive alerting"""
        try:
            if len(data_points) < 10:
                return
            
            values = [point[1] for point in data_points[-30:]]  # Last 30 points
            timestamps = [point[0] for point in data_points[-30:]]
            
            # Simple trend analysis
            if len(values) >= 10:
                # Calculate trend slope
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]
                
                # Determine trend direction
                trend_direction = 'up' if slope > 0 else 'down' if slope < 0 else 'stable'
                trend_strength = abs(slope) / (max(values) - min(values)) if max(values) != min(values) else 0
                
                # Simple forecast (linear extrapolation)
                forecast_points = 10
                forecast_x = np.arange(len(values), len(values) + forecast_points)
                forecast_values = [slope * x + values[-1] for x in range(forecast_points)]
                
                # Calculate anomaly score (variance from expected)
                expected_variance = np.var(values)
                recent_variance = np.var(values[-5:]) if len(values) >= 5 else 0
                anomaly_score = abs(recent_variance - expected_variance) / max(expected_variance, 0.001)
                
                trend_metrics = PerformanceTrendMetrics(
                    metric_name=metric_name,
                    time_series=list(zip(timestamps, values)),
                    trend_direction=trend_direction,
                    trend_strength=trend_strength,
                    forecast_values=forecast_values,
                    anomaly_score=anomaly_score,
                    seasonal_pattern=False,  # Would need more sophisticated analysis
                    timestamp=datetime.utcnow()
                )
                
                self.trend_cache[metric_name] = trend_metrics
                
                # Predictive alerting
                if self.enable_predictive_alerting and trend_direction == 'up' and trend_strength > 0.5:
                    # Check if forecast exceeds thresholds
                    if metric_name in self.metric_thresholds:
                        thresholds = self.metric_thresholds[metric_name]
                        max_forecast = max(forecast_values)
                        
                        if max_forecast > thresholds.get('warning', float('inf')):
                            alert = AlertMetrics(
                                alert_id=f"predictive_{metric_name}_{int(time.time())}",
                                alert_type='trend',
                                severity='info',
                                metric_name=metric_name,
                                current_value=values[-1],
                                threshold_value=thresholds.get('warning', 0),
                                message=f"Predictive alert: {metric_name} trending towards threshold violation",
                                suggested_action="Monitor closely and consider preventive action",
                                affected_components=self._get_affected_components(metric_name),
                                timestamp=datetime.utcnow()
                            )
                            
                            self.alert_cache.append(alert)
                            await self._broadcast_alert(alert)
                
        except Exception as e:
            logger.error(f"Error analyzing trends for {metric_name}: {e}")
    
    async def _alert_processing_loop(self):
        """Alert processing and notification loop"""
        while self.running:
            try:
                # Clean up old alerts
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.alert_cache = deque([
                    alert for alert in self.alert_cache
                    if alert.timestamp > cutoff_time
                ], maxlen=1000)
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}")
                await asyncio.sleep(300)
    
    async def _session_management_loop(self):
        """WebSocket session management loop"""
        while self.running:
            try:
                # Clean up stale sessions
                current_time = datetime.utcnow()
                stale_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    # Check for stale sessions (no ping in 2 minutes)
                    if (current_time - session.last_ping).total_seconds() > 120:
                        stale_sessions.append(session_id)
                
                # Remove stale sessions
                for session_id in stale_sessions:
                    if session_id in self.active_sessions:
                        try:
                            await self.active_sessions[session_id].websocket.close()
                        except:
                            pass
                        del self.active_sessions[session_id]
                        logger.info(f"Removed stale session: {session_id}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session management loop: {e}")
                await asyncio.sleep(30)