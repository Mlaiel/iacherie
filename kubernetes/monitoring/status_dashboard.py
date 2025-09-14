"""Status Dashboard for IA Influencer Agent Platform
================================================

Industrial-grade real-time monitoring dashboard with AI-powered insights,
business intelligence visualization, and comprehensive system observability
for content protection, revenue tracking, and platform operations.

Features:
    - Real-time system health visualization with WebSocket updates
- AI-powered performance insights and predictive analytics
- Content protection metrics and violation tracking
- Revenue analytics and monetization dashboards
- User engagement and collaboration metrics
- Multi-tenant monitoring with privacy controls
- Interactive drill-down capabilities and custom views
- Mobile-responsive design with dark/light themes

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use, distribution, or modification prohibited
"""
import asyncio
import json
import logging
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import aioredis
from aiohttp import web, WSMsgType
import aiohttp_cors
from jinja2 import Environment, BaseLoader, FileSystemLoader
import base64
import hashlib

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Enhanced component status levels with business impact"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"
    CRITICAL = "critical"
    WARNING = "warning"


class BusinessDomain(Enum):
    """Business domain categories for dashboard organization"""
    CONTENT_PROTECTION = "content_protection"
    AI_FINGERPRINTING = "ai_fingerprinting"
    REVENUE_TRACKING = "revenue_tracking"
    USER_ENGAGEMENT = "user_engagement"
    PLATFORM_INTEGRATION = "platform_integration"
    SYSTEM_INFRASTRUCTURE = "system_infrastructure"
    SECURITY = "security"
    COLLABORATION = "collaboration"


@dataclass
class SystemComponent:
    """Enhanced system component with business context"""
    name: str
    description: str
    category: str
    domain: BusinessDomain
    status: ComponentStatus = ComponentStatus.OPERATIONAL
    last_updated: datetime = field(default_factory=datetime.utcnow)
    uptime_percentage: float = 100.0
    response_time: Optional[float] = None
    error_rate: float = 0.0
    business_impact: str = "medium"  # low, medium, high, critical
    sla_target: float = 99.9
    current_sla: float = 100.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    health_score: float = 1.0  # 0.0 to 1.0


@dataclass
class StatusIncident:
    """Enhanced status incident with resolution tracking"""
    id: str
    title: str
    description: str
    status: str  # investigating, identified, monitoring, resolved
    impact: str  # none, minor, major, critical
    components: List[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    updates: List[Dict[str, Any]] = field(default_factory=list)
    root_cause: Optional[str] = None
    resolution_time: Optional[int] = None  # minutes
    affected_users: int = 0
    business_impact_score: float = 0.0
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    id: str
    title: str
    type: str  # metric, chart, table, status, custom
    position: Tuple[int, int]  # (row, column)
    size: Tuple[int, int]  # (width, height)
    data_source: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    refresh_interval: int = 30  # seconds
    enabled: bool = True


@dataclass
class BusinessMetricSummary:
    """Business metrics summary for dashboard"""
    domain: BusinessDomain
    kpis: Dict[str, float]
    trends: Dict[str, str]  # increasing, decreasing, stable
    alerts: List[str]
    health_score: float
    last_updated: datetime


class DashboardTemplates:
    """Dashboard HTML templates"""
    
    @staticmethod
    def get_main_template() -> str:
        """Get main dashboard template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA Influencer Agent - Monitoring Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #2563eb;
            --success-color: #059669;
            --warning-color: #d97706;
            --danger-color: #dc2626;
            --dark-bg: #1f2937;
            --card-bg: #ffffff;
            --text-primary: #111827;
            --border-color: #e5e7eb;
        }
        
        [data-theme="dark"] {
            --card-bg: #374151;
            --text-primary: #f9fafb;
            --border-color: #4b5563;
            background-color: var(--dark-bg);
            color: var(--text-primary);
        }
        
        .status-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .status-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-operational { background-color: var(--success-color); }
        .status-degraded { background-color: var(--warning-color); }
        .status-critical { background-color: var(--danger-color); }
        .status-maintenance { background-color: #6b7280; }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .trend-up { color: var(--success-color); }
        .trend-down { color: var(--danger-color); }
        .trend-stable { color: #6b7280; }
        
        .sidebar {
            width: 250px;
            height: 100vh;
            background: var(--card-bg);
            border-right: 1px solid var(--border-color);
            position: fixed;
            left: 0;
            top: 0;
            z-index: 1000;
            padding: 1rem;
        }
        
        .main-content {
            margin-left: 250px;
            padding: 2rem;
            min-height: 100vh;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin: 1rem 0;
        }
        
        .widget-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .sidebar.show {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="d-flex align-items-center mb-4">
            <i class="fas fa-chart-line text-primary me-2"></i>
            <h5 class="mb-0">IA Influencer</h5>
        </div>
        
        <nav class="nav flex-column">
            <a class="nav-link active" href="#overview" data-section="overview">
                <i class="fas fa-tachometer-alt me-2"></i>Overview
            </a>
            <a class="nav-link" href="#content-protection" data-section="content-protection">
                <i class="fas fa-shield-alt me-2"></i>Content Protection
            </a>
            <a class="nav-link" href="#revenue" data-section="revenue">
                <i class="fas fa-chart-pie me-2"></i>Revenue Analytics
            </a>
            <a class="nav-link" href="#users" data-section="users">
                <i class="fas fa-users me-2"></i>User Engagement
            </a>
            <a class="nav-link" href="#performance" data-section="performance">
                <i class="fas fa-rocket me-2"></i>Performance
            </a>
            <a class="nav-link" href="#security" data-section="security">
                <i class="fas fa-lock me-2"></i>Security
            </a>
            <a class="nav-link" href="#incidents" data-section="incidents">
                <i class="fas fa-exclamation-triangle me-2"></i>Incidents
            </a>
        </nav>
        
        <div class="mt-auto pt-4">
            <button class="btn btn-outline-primary btn-sm w-100" onclick="toggleTheme()">
                <i class="fas fa-moon me-1"></i>Toggle Theme
            </button>
        </div>
    </div>
    
    <div class="main-content">
        <header class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1>Monitoring Dashboard</h1>
                <p class="text-muted mb-0">Real-time system health and business metrics</p>
            </div>
            <div class="d-flex align-items-center">
                <span class="badge bg-success me-2">
                    <i class="fas fa-circle me-1"></i>All Systems Operational
                </span>
                <span id="last-update" class="text-muted small"></span>
            </div>
        </header>
        
        <div id="dashboard-content">
            <!-- Dynamic content will be loaded here -->
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // WebSocket connection for real-time updates
        let ws;
        let currentSection = 'overview';
        
        function initWebSocket() {
            const wsUrl = `ws://${window.location.host}/ws/dashboard`;
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('Dashboard WebSocket connected');
                updateConnectionStatus(true);
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketUpdate(data);
            };
            
            ws.onclose = function() {
                console.log('Dashboard WebSocket disconnected');
                updateConnectionStatus(false);
                // Reconnect after 5 seconds
                setTimeout(initWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                updateConnectionStatus(false);
            };
        }
        
        function handleWebSocketUpdate(data) {
            switch(data.type) {
                case 'metrics_update':
                    updateMetrics(data.payload);
                    break;
                case 'component_status':
                    updateComponentStatus(data.payload);
                    break;
                case 'alert':
                    showAlert(data.payload);
                    break;
                case 'incident_update':
                    updateIncidents(data.payload);
                    break;
            }
            updateLastUpdateTime();
        }
        
        function updateConnectionStatus(connected) {
            const statusBadge = document.querySelector('.badge');
            if (connected) {
                statusBadge.className = 'badge bg-success me-2';
                statusBadge.innerHTML = '<i class="fas fa-circle me-1"></i>All Systems Operational';
            } else {
                statusBadge.className = 'badge bg-warning me-2';
                statusBadge.innerHTML = '<i class="fas fa-exclamation-circle me-1"></i>Connection Issues';
            }
        }
        
        function updateLastUpdateTime() {
            const now = new Date();
            document.getElementById('last-update').textContent = 
                `Last updated: ${now.toLocaleTimeString()}`;
        }
        
        function loadSection(section) {
            currentSection = section;
            fetch(`/api/dashboard/${section}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('dashboard-content').innerHTML = data.html;
                    if (data.scripts) {
                        eval(data.scripts);
                    }
                })
                .catch(error => {
                    console.error('Error loading section:', error);
                });
        }
        
        function toggleTheme() {
            const body = document.body;
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('dashboard-theme', newTheme);
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            // Load saved theme
            const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
            document.body.setAttribute('data-theme', savedTheme);
            
            // Setup navigation
            document.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const section = this.getAttribute('data-section');
                    
                    // Update active nav
                    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Load section content
                    loadSection(section);
                });
            });
            
            // Initialize WebSocket
            initWebSocket();
            
            // Load initial section
            loadSection('overview');
            
            // Update time initially
            updateLastUpdateTime();
        });
    </script>
</body>
</html>
        '''
    
    @staticmethod
    def get_overview_template() -> str:
        """Get overview section template"""
        return '''
        <div class="row">
            <div class="col-md-3">
                <div class="status-card">
                    <div class="d-flex align-items-center justify-content-between">
                        <div>
                            <div class="metric-value text-primary" id="active-users">{{ active_users }}</div>
                            <div class="metric-label">Active Users</div>
                        </div>
                        <i class="fas fa-users fa-2x text-primary opacity-25"></i>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="status-card">
                    <div class="d-flex align-items-center justify-content-between">
                        <div>
                            <div class="metric-value text-success" id="daily-revenue"># [EMOJI_REMOVED]{{ daily_revenue }}</div>
                            <div class="metric-label">Daily Revenue</div>
                        </div>
                        <i class="fas fa-euro-sign fa-2x text-success opacity-25"></i>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="status-card">
                    <div class="d-flex align-items-center justify-content-between">
                        <div>
                            <div class="metric-value text-info" id="fingerprints-today">{{ fingerprints_today }}</div>
                            <div class="metric-label">Fingerprints Today</div>
                        </div>
                        <i class="fas fa-fingerprint fa-2x text-info opacity-25"></i>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="status-card">
                    <div class="d-flex align-items-center justify-content-between">
                        <div>
                            <div class="metric-value text-warning" id="protection-alerts">{{ protection_alerts }}</div>
                            <div class="metric-label">Protection Alerts</div>
                        </div>
                        <i class="fas fa-shield-alt fa-2x text-warning opacity-25"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-8">
                <div class="status-card">
                    <h5>System Health Overview</h5>
                    <div class="chart-container">
                        <canvas id="healthChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="status-card">
                    <h5>Component Status</h5>
                    <div id="component-list">
                        {% for component in components %}
                        <div class="d-flex align-items-center justify-content-between mb-2">
                            <div class="d-flex align-items-center">
                                <span class="status-indicator status-{{ component.status }}"></span>
                                <span>{{ component.name }}</span>
                            </div>
                            <small class="text-muted">{{ component.uptime }}%</small>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
        '''


class StatusDashboard:
    """
    Industrial-grade real-time monitoring dashboard with AI-powered insights,
    business intelligence visualization, and comprehensive system observability.
    """
    
    def __init__(
        self,
        redis_client -> None: Optional[aioredis.Redis] = None,
        metrics_collector=None,
        health_monitor=None,
        alert_manager=None,
        performance_tracker=None,
        business_metrics=None,
        port -> None: int = 8080,
        enable_auth -> None: bool = True
    ) -> None:
        self.redis_client = redis_client
        self.metrics_collector = metrics_collector
        self.health_monitor = health_monitor
        self.alert_manager = alert_manager
        self.performance_tracker = performance_tracker
        self.business_metrics = business_metrics
        self.port = port
        self.enable_auth = enable_auth
        
        # Web application
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        
        # WebSocket connections
        self.websocket_connections: List[web.WebSocketResponse] = []
        
        # System components
        self.components: Dict[str, SystemComponent] = {}
        self.incidents: Dict[str, StatusIncident] = {}
        self.widgets: Dict[str, DashboardWidget] = {}
        
        # Dashboard state
        self._dashboard_running = False
    
    def _initialize_default_components(self) -> None:
        """Initialize default system components"""
        components_config = [
            {
                "name": "Core API Gateway",
                "description": "Main API gateway handling all external requests",
                "category": "api",
                "domain": BusinessDomain.SYSTEM_INFRASTRUCTURE,
                "business_impact": "critical",
                "sla_target": 99.95,
                "dependencies": ["database", "redis", "ai_engine"]
            },
            {
                "name": "AI Fingerprinting Engine",
                "description": "Advanced AI system for content fingerprinting and matching",
                "category": "ai",
                "domain": BusinessDomain.AI_FINGERPRINTING,
                "business_impact": "high",
                "sla_target": 99.9,
                "dependencies": ["ml_models", "gpu_cluster"]
            },
            {
                "name": "Content Protection Service",
                "description": "Real-time content protection and violation detection",
                "category": "protection",
                "domain": BusinessDomain.CONTENT_PROTECTION,
                "business_impact": "high",
                "sla_target": 99.8,
                "dependencies": ["ai_engine", "database"]
            },
            {
                "name": "Revenue Tracking System",
                "description": "Real-time revenue analytics and monetization tracking",
                "category": "business",
                "domain": BusinessDomain.REVENUE_TRACKING,
                "business_impact": "critical",
                "sla_target": 99.99,
                "dependencies": ["database", "payment_gateways"]
            },
            {
                "name": "User Engagement Analytics",
                "description": "User behavior analysis and engagement metrics",
                "category": "analytics",
                "domain": BusinessDomain.USER_ENGAGEMENT,
                "business_impact": "medium",
                "sla_target": 99.5,
                "dependencies": ["database", "analytics_engine"]
            },
            {
                "name": "Multi-Platform Integration Hub",
                "description": "Integration with Spotify, YouTube, TikTok, Instagram",
                "category": "integration",
                "domain": BusinessDomain.PLATFORM_INTEGRATION,
                "business_impact": "high",
                "sla_target": 99.7,
                "dependencies": ["api_gateway", "oauth_service"]
            },
            {
                "name": "Collaboration Engine",
                "description": "Real-time collaboration features and workspace management",
                "category": "collaboration",
                "domain": BusinessDomain.COLLABORATION,
                "business_impact": "medium",
                "sla_target": 99.5,
                "dependencies": ["websocket_service", "database"]
            },
            {
                "name": "Security & Authentication",
                "description": "Multi-factor authentication and security monitoring",
                "category": "security",
                "domain": BusinessDomain.SECURITY,
                "business_impact": "critical",
                "sla_target": 99.99,
                "dependencies": ["vault", "identity_provider"]
            }
        ]
        
        for config in components_config:
            component = SystemComponent(
                name=config["name"],
                description=config["description"],
                category=config["category"],
                domain=config["domain"],
                business_impact=config["business_impact"],
                sla_target=config["sla_target"],
                dependencies=config.get("dependencies", [])
            )
            self.components[component.name.lower().replace(" ", "_")] = component
    
    def _initialize_default_widgets(self) -> None:
        """Initialize default dashboard widgets"""
        widgets_config = [
            {
                "id": "overview_metrics",
                "title": "Key Performance Indicators",
                "type": "metric",
                "position": (0, 0),
                "size": (12, 3),
                "data_source": "business_metrics",
                "configuration": {
                    "metrics": ["active_users", "daily_revenue", "fingerprints_today", "protection_alerts"],
                    "real_time": True
                }
            },
            {
                "id": "system_health",
                "title": "System Health Overview",
                "type": "chart",
                "position": (1, 0),
                "size": (8, 4),
                "data_source": "health_monitor",
                "configuration": {
                    "chart_type": "line",
                    "metrics": ["cpu_usage", "memory_usage", "disk_usage", "network_io"],
                    "time_range": "1h"
                }
            },
            {
                "id": "component_status",
                "title": "Component Status",
                "type": "status",
                "position": (1, 8),
                "size": (4, 4),
                "data_source": "components",
                "configuration": {
                    "show_uptime": True,
                    "show_response_time": True,
                    "group_by": "domain"
                }
            },
            {
                "id": "revenue_chart",
                "title": "Revenue Analytics",
                "type": "chart",
                "position": (2, 0),
                "size": (6, 3),
                "data_source": "revenue_metrics",
                "configuration": {
                    "chart_type": "area",
                    "metrics": ["daily_revenue", "monthly_recurring", "new_subscriptions"],
                    "time_range": "30d"
                }
            },
            {
                "id": "content_protection",
                "title": "Content Protection Metrics",
                "type": "chart",
                "position": (2, 6),
                "size": (6, 3),
                "data_source": "protection_metrics",
                "configuration": {
                    "chart_type": "bar",
                    "metrics": ["violations_detected", "fingerprints_matched", "false_positives"],
                    "time_range": "24h"
                }
            },
            {
                "id": "active_incidents",
                "title": "Active Incidents",
                "type": "table",
                "position": (3, 0),
                "size": (12, 2),
                "data_source": "incidents",
                "configuration": {
                    "filters": {"status": ["investigating", "identified", "monitoring"]},
                    "sort_by": "created_at",
                    "show_updates": True
                }
            }
        ]
        
        for config in widgets_config:
            widget = DashboardWidget(
                id=config["id"],
                title=config["title"],
                type=config["type"],
                position=config["position"],
                size=config["size"],
                data_source=config["data_source"],
                configuration=config.get("configuration", {}),
                permissions=config.get("permissions", ["read"]),
                refresh_interval=config.get("refresh_interval", 30)
            )
            self.widgets[widget.id] = widget
    
    def setup_routes(self) -> None:
        """Setup web application routes"""
        # Dashboard routes
        self.app.router.add_get('/', self.serve_dashboard)
        self.app.router.add_get('/dashboard', self.serve_dashboard)
        self.app.router.add_get('/dashboard/{section}', self.serve_dashboard_section)
        
        # API routes
        self.app.router.add_get('/api/status', self.get_system_status)
        self.app.router.add_get('/api/components', self.get_components)
        self.app.router.add_get('/api/components/{component_id}', self.get_component_details)
        self.app.router.add_get('/api/incidents', self.get_incidents)
        self.app.router.add_post('/api/incidents', self.create_incident)
        self.app.router.add_patch('/api/incidents/{incident_id}', self.update_incident)
        self.app.router.add_get('/api/metrics', self.get_metrics)
        self.app.router.add_get('/api/metrics/{domain}', self.get_domain_metrics)
        self.app.router.add_get('/api/dashboard/{section}', self.get_dashboard_section_data)
        
        # Widget routes
        self.app.router.add_get('/api/widgets', self.get_widgets)
        self.app.router.add_post('/api/widgets', self.create_widget)
        self.app.router.add_patch('/api/widgets/{widget_id}', self.update_widget)
        self.app.router.add_delete('/api/widgets/{widget_id}', self.delete_widget)
        
        # WebSocket route
        self.app.router.add_get('/ws/dashboard', self.websocket_handler)
        
        # Static files
        self.app.router.add_static('/', path='static', name='static')
    
    def setup_cors(self) -> None:
        """Setup CORS for cross-origin requests"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def serve_dashboard(self, request: web.Request) -> web.Response:
        """Serve main dashboard page"""
        try:
            # Get current system status
            system_status = await self.get_system_overview()
            
            # Render main template
            html_content = self.templates.get_main_template()
            
            return web.Response(
                text=html_content,
                content_type='text/html',
                headers={'Cache-Control': 'no-cache'}
            )
            
        except Exception as e:
            logger.error(f"Error serving dashboard: {e}")
            return web.Response(
                text=f"Dashboard error: {str(e)}",
                status=500
            )
    
    async def serve_dashboard_section(self, request: web.Request) -> web.Response:
        """Serve specific dashboard section"""
        section = request.match_info.get('section', 'overview')
        
        try:
            # Get section-specific data
            section_data = await self.get_section_data(section)
            
            # Render section template
            html_content = await self.render_section_template(section, section_data)
            
            return web.Response(
                text=html_content,
                content_type='text/html'
            )
            
        except Exception as e:
            logger.error(f"Error serving dashboard section {section}: {e}")
            return web.Response(
                text=f"Section error: {str(e)}",
                status=500
            )
    
    async def get_system_status(self, request: web.Request) -> web.Response:
        """Get overall system status"""
        try:
            status_data = await self.get_system_overview()
            return web.json_response(status_data)
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def get_components(self, request: web.Request) -> web.Response:
        """Get all system components"""
        try:
            # Update component statuses
            await self.update_component_statuses()
            
            components_data = [
                {
                    "id": comp_id,
                    **asdict(component)
                }
                for comp_id, component in self.components.items()
            ]
            
            return web.json_response(components_data)
            
        except Exception as e:
            logger.error(f"Error getting components: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def get_component_details(self, request: web.Request) -> web.Response:
        """Get detailed information about a specific component"""
        component_id = request.match_info.get('component_id')
        
        try:
            if component_id not in self.components:
                return web.json_response(
                    {"error": "Component not found"},
                    status=404
                )
            
            component = self.components[component_id]
            
            # Get additional metrics for this component
            component_metrics = await self.get_component_metrics(component_id)
            
            # Get component history
            component_history = await self.get_component_history(component_id)
            
            return web.json_response({
                "component": asdict(component),
                "metrics": component_metrics,
                "history": component_history
            })
            
        except Exception as e:
            logger.error(f"Error getting component details for {component_id}: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def get_incidents(self, request: web.Request) -> web.Response:
        """Get all incidents with filtering"""
        try:
            # Get query parameters
            status_filter = request.query.get('status')
            impact_filter = request.query.get('impact')
            limit = int(request.query.get('limit', 50))
            offset = int(request.query.get('offset', 0))
            
            # Filter incidents
            filtered_incidents = []
            for incident in self.incidents.values():
                if status_filter and incident.status != status_filter:
                    continue
                if impact_filter and incident.impact != impact_filter:
                    continue
                filtered_incidents.append(incident)
            
            # Sort by creation date (newest first)
            filtered_incidents.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            paginated_incidents = filtered_incidents[offset:offset + limit]
            
            incidents_data = [asdict(incident) for incident in paginated_incidents]
            
            return web.json_response({
                "incidents": incidents_data,
                "total": len(filtered_incidents),
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"Error getting incidents: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
        self._update_task: Optional[asyncio.Task] = None
        
        # Templates
        self.template_env = Environment(loader=BaseLoader())
        
        # Register default components
        self._register_default_components()
        
    def _register_default_components(self) -> None:
        """Register default system components"""
        
        # Core platform components
        self.register_component(SystemComponent(
            name="api_gateway",
            description="Main API Gateway",
            category="core"
        ))
        
        self.register_component(SystemComponent(
            name="database",
            description="PostgreSQL Database",
            category="core"
        ))
        
        self.register_component(SystemComponent(
            name="redis_cache",
            description="Redis Cache System",
            category="core"
        ))
        
        self.register_component(SystemComponent(
            name="message_queue",
            description="Celery Message Queue",
            category="core"
        ))
        
        # AI/ML components
        self.register_component(SystemComponent(
            name="fingerprint_engine",
            description="AI Fingerprinting Engine",
            category="ai"
        ))
        
        self.register_component(SystemComponent(
            name="content_protection",
            description="Content Protection Service",
            category="ai"
        ))
        
        self.register_component(SystemComponent(
            name="ml_models",
            description="Machine Learning Models",
            category="ai"
        ))
        
        # Business components
        self.register_component(SystemComponent(
            name="revenue_tracking",
            description="Revenue Tracking System",
            category="business"
        ))
        
        self.register_component(SystemComponent(
            name="payment_processing",
            description="Payment Processing",
            category="business"
        ))
        
        self.register_component(SystemComponent(
            name="user_management",
            description="User Management Service",
            category="business"
        ))
        
        # External services
        self.register_component(SystemComponent(
            name="spotify_api",
            description="Spotify API Integration",
            category="external"
        ))
        
        self.register_component(SystemComponent(
            name="youtube_api",
            description="YouTube API Integration",
            category="external"
        ))
        
        self.register_component(SystemComponent(
            name="storage_service",
            description="S3 Storage Service",
            category="external"
        ))
        
    def setup_routes(self) -> None:
        """Setup web routes"""
        # CORS setup
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # API routes
        self.app.router.add_get('/', self.dashboard_home)
        self.app.router.add_get('/api/status', self.api_status)
        self.app.router.add_get('/api/components', self.api_components)
        self.app.router.add_get('/api/incidents', self.api_incidents)
        self.app.router.add_get('/api/metrics', self.api_metrics)
        self.app.router.add_get('/api/health', self.api_health)
        self.app.router.add_get('/api/performance', self.api_performance)
        self.app.router.add_get('/api/business', self.api_business_metrics)
        
        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Static routes for dashboard assets
        self.app.router.add_get('/dashboard.js', self.dashboard_js)
        self.app.router.add_get('/dashboard.css', self.dashboard_css)
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
            
    async def start_dashboard(self) -> None:
        """Start the status dashboard"""
        if self._dashboard_running:
            logger.warning("Status dashboard already running")
            return
            
        self._dashboard_running = True
        
        # Start update task
        self._update_task = asyncio.create_task(self._update_loop())
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"Status dashboard started on port {self.port}")
        
    async def stop_dashboard(self) -> None:
        """Stop the status dashboard"""
        self._dashboard_running = False
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
                
        # Close WebSocket connections
        for ws in self.websocket_connections:
            if not ws.closed:
                await ws.close()
                
        logger.info("Status dashboard stopped")
        
    async def _update_loop(self) -> None:
        """Main update loop for dashboard data"""
        while self._dashboard_running:
            try:
                await self._update_component_status()
                await self._broadcast_updates()
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                await asyncio.sleep(5)
                
    async def _update_component_status(self) -> None:
        """Update status of all components"""
        if self.health_monitor:
            health_results = self.health_monitor.get_detailed_results()
            
            for component_name, component in self.components.items():
                # Map component to health check
                health_key = self._map_component_to_health_check(component_name)
                
                if health_key in health_results:
                    health_result = health_results[health_key]
                    
                    # Update component status
                    if health_result['status'] == 'healthy':
                        component.status = ComponentStatus.OPERATIONAL
                    elif health_result['status'] == 'warning':
                        component.status = ComponentStatus.DEGRADED
                    else:
                        component.status = ComponentStatus.PARTIAL_OUTAGE
                        
                    component.response_time = health_result.get('response_time', 0)
                    component.last_updated = datetime.utcnow()
                    
        # Update performance metrics
        if self.performance_tracker:
            perf_summary = self.performance_tracker.get_performance_summary()
            
            for component_name, component in self.components.items():
                if component.category == "core":
                    # Update based on performance metrics
                    resource_info = perf_summary.get('resources', {})
                    
                    if component_name == "database":
                        # Update database component based on DB performance
                        operations = perf_summary.get('operations', {})
                        db_ops = {k: v for k, v in operations.items() if 'database' in k.lower()}
                        
                        if db_ops:
                            avg_response = sum(op['avg_time'] for op in db_ops.values()) / len(db_ops)
                            component.response_time = avg_response
                            
                            if avg_response > 5000:  # >5s
                                component.status = ComponentStatus.DEGRADED
                                
    def _map_component_to_health_check(self, component_name: str) -> str:
        """Map component name to health check name"""
        mapping = {
            "database": "database_connection",
            "redis_cache": "redis_connection",
            "api_gateway": "api_endpoints",
            "fingerprint_engine": "fingerprint_service",
            "content_protection": "protection_alerts"
        }
        
        return mapping.get(component_name, component_name)
        
    async def _broadcast_updates(self) -> None:
        """Broadcast updates to all WebSocket connections"""
        if not self.websocket_connections:
            return
            
        try:
            # Prepare update data
            update_data = {
                "type": "status_update",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    name: {
                        "status": comp.status.value,
                        "uptime": comp.uptime_percentage,
                        "response_time": comp.response_time,
                        "error_rate": comp.error_rate,
                        "last_updated": comp.last_updated.isoformat()
                    }
                    for name, comp in self.components.items()
                }
            }
            
            # Add metrics if available
            if self.metrics_collector:
                current_metrics = self.metrics_collector.get_current_metrics()
                update_data["metrics"] = current_metrics
                
            message = json.dumps(update_data)
            
            # Send to all connected clients
            disconnected = []
            for ws in self.websocket_connections:
                try:
                    if ws.closed:
                        disconnected.append(ws)
                    else:
                        await ws.send_str(message)
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {e}")
                    disconnected.append(ws)
                    
            # Remove disconnected clients
            for ws in disconnected:
                self.websocket_connections.remove(ws)
                
        except Exception as e:
            logger.error(f"Error broadcasting updates: {e}")
            
    # Web handlers
    async def dashboard_home(self, request) -> None:
        """Dashboard home page"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>IA Influencer Agent - Status Dashboard</title>
            <link rel="stylesheet" href="/dashboard.css">
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <div id="dashboard">
                <header>
                    <h1># [EMOJI_REMOVED] IA Influencer Agent Platform</h1>
                    <div class="status-indicator" id="overall-status">
                        <span class="status-dot operational"></span>
                        <span>All Systems Operational</span>
                    </div>
                </header>
                
                <div class="dashboard-content">
                    <div class="components-section">
                        <h2>System Components</h2>
                        <div id="components-grid" class="components-grid">
                            <!-- Components will be loaded here -->
                        </div>
                    </div>
                    
                    <div class="metrics-section">
                        <h2>Real-time Metrics</h2>
                        <div id="metrics-grid" class="metrics-grid">
                            <!-- Metrics will be loaded here -->
                        </div>
                    </div>
                    
                    <div class="incidents-section">
                        <h2>Recent Incidents</h2>
                        <div id="incidents-list">
                            <!-- Incidents will be loaded here -->
                        </div>
                    </div>
                </div>
                
                <footer>
                    <p># [EMOJI_REMOVED] 2025 Fahed Mlaiel - IA Influencer Agent Platform</p>
                    <p><strong># [EMOJI_REMOVED] Proprietary System - Unauthorized access prohibited</strong></p>
                </footer>
            </div>
            
            <script src="/dashboard.js"></script>
        </body>
        </html>
        """
        
        return web.Response(text=html_template, content_type='text/html')
        
    async def dashboard_css(self, request) -> None:
        """Dashboard CSS styles"""
        css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        #dashboard {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2rem;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: bold;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .status-dot.operational { background: #27ae60; }
        .status-dot.degraded { background: #f39c12; }
        .status-dot.partial_outage { background: #e74c3c; }
        .status-dot.major_outage { background: #c0392b; }
        .status-dot.maintenance { background: #3498db; }
        
        .dashboard-content {
            display: grid;
            gap: 20px;
        }
        
        .components-section, .metrics-section, .incidents-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        
        .components-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .component-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            transition: transform 0.2s;
        }
        
        .component-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .component-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .component-name {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .component-metrics {
            font-size: 0.9em;
            color: #666;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .metric-card {
            text-align: center;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #f8f9fa;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #3498db;
        }
        
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        
        .incident-item {
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin-bottom: 10px;
            background: #fff5f5;
            border-radius: 0 8px 8px 0;
        }
        
        .incident-title {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .incident-meta {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        footer {
            text-align: center;
            margin-top: 30px;
            color: rgba(255, 255, 255, 0.8);
        }
        
        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .connected {
            background: #27ae60;
            color: white;
        }
        
        .disconnected {
            background: #e74c3c;
            color: white;
        }
        
        @media (max-width: 768px) {
            .components-grid {
                grid-template-columns: 1fr;
            }
            
            header {
                flex-direction: column;
                gap: 10px;
                text-align: center;
            }
        }
        """
        
        return web.Response(text=css, content_type='text/css')
        
    async def dashboard_js(self, request) -> None:
        """Dashboard JavaScript"""
        js = """
        class StatusDashboard {
            constructor() {
                this.ws = null;
                this.reconnectInterval = 5000;
                this.init();
            }
            
            init() {
                this.connectWebSocket();
                this.loadInitialData();
                this.setupReconnection();
            }
            
            connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.updateConnectionStatus(true);
                };
                
                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handleUpdate(data);
                };
                
                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.updateConnectionStatus(false);
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.updateConnectionStatus(false);
                };
            }
            
            setupReconnection() {
                setInterval(() => {
                    if (this.ws.readyState === WebSocket.CLOSED) {
                        this.connectWebSocket();
                    }
                }, this.reconnectInterval);
            }
            
            updateConnectionStatus(connected) {
                let statusEl = document.getElementById('connection-status');
                if (!statusEl) {
                    statusEl = document.createElement('div');
                    statusEl.id = 'connection-status';
                    statusEl.className = 'connection-status';
                    document.body.appendChild(statusEl);
                }
                
                statusEl.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
                statusEl.textContent = connected ? '# [EMOJI_REMOVED] Connected' : '# [EMOJI_REMOVED] Disconnected';
            }
            
            async loadInitialData() {
                try {
                    const [components, metrics, incidents] = await Promise.all([
                        fetch('/api/components').then(r => r.json()),
                        fetch('/api/metrics').then(r => r.json()),
                        fetch('/api/incidents').then(r => r.json())
                    ]);
                    
                    this.renderComponents(components);
                    this.renderMetrics(metrics);
                    this.renderIncidents(incidents);
                    
                } catch (error) {
                    console.error('Error loading initial data:', error);
                }
            }
            
            handleUpdate(data) {
                if (data.type === 'status_update') {
                    this.updateComponents(data.components);
                    if (data.metrics) {
                        this.updateMetrics(data.metrics);
                    }
                }
            }
            
            renderComponents(components) {
                const grid = document.getElementById('components-grid');
                grid.innerHTML = '';
                
                Object.entries(components).forEach(([name, component]) => {
                    const card = this.createComponentCard(name, component);
                    grid.appendChild(card);
                });
                
                this.updateOverallStatus(components);
            }
            
            createComponentCard(name, component) {
                const card = document.createElement('div');
                card.className = 'component-card';
                card.id = `component-${name}`;
                
                const statusDot = `<span class="status-dot ${component.status}"></span>`;
                const responseTime = component.response_time ? 
                    `${Math.round(component.response_time)}ms` : 'N/A';
                
                card.innerHTML = `
                    <div class="component-header">
                        <span class="component-name">${this.formatName(name)}</span>
                        ${statusDot}
                    </div>
                    <div class="component-description">${component.description}</div>
                    <div class="component-metrics">
                        <div>Uptime: ${component.uptime.toFixed(2)}%</div>
                        <div>Response: ${responseTime}</div>
                        <div>Error Rate: ${(component.error_rate * 100).toFixed(2)}%</div>
                    </div>
                `;
                
                return card;
            }
            
            updateComponents(components) {
                Object.entries(components).forEach(([name, component]) => {
                    const card = document.getElementById(`component-${name}`);
                    if (card) {
                        const statusDot = card.querySelector('.status-dot');
                        if (statusDot) {
                            statusDot.className = `status-dot ${component.status}`;
                        }
                        
                        const metrics = card.querySelector('.component-metrics');
                        if (metrics) {
                            const responseTime = component.response_time ? 
                                `${Math.round(component.response_time)}ms` : 'N/A';
                            
                            metrics.innerHTML = `
                                <div>Uptime: ${component.uptime.toFixed(2)}%</div>
                                <div>Response: ${responseTime}</div>
                                <div>Error Rate: ${(component.error_rate * 100).toFixed(2)}%</div>
                            `;
                        }
                    }
                });
                
                this.updateOverallStatus(components);
            }
            
            updateOverallStatus(components) {
                const statuses = Object.values(components).map(c => c.status);
                const overallStatus = document.getElementById('overall-status');
                
                let status = 'operational';
                let text = 'All Systems Operational';
                
                if (statuses.includes('major_outage')) {
                    status = 'major_outage';
                    text = 'Major Service Outage';
                } else if (statuses.includes('partial_outage')) {
                    status = 'partial_outage';
                    text = 'Partial Service Outage';
                } else if (statuses.includes('degraded')) {
                    status = 'degraded';
                    text = 'Some Services Degraded';
                } else if (statuses.includes('maintenance')) {
                    status = 'maintenance';
                    text = 'Maintenance In Progress';
                }
                
                const statusDot = overallStatus.querySelector('.status-dot');
                statusDot.className = `status-dot ${status}`;
                overallStatus.querySelector('span:last-child').textContent = text;
            }
            
            renderMetrics(metrics) {
                const grid = document.getElementById('metrics-grid');
                grid.innerHTML = '';
                
                const metricCards = [
                    { label: 'Active Users', value: metrics.active_users || 0, format: 'number' },
                    { label: 'API Requests/min', value: metrics.api_requests_per_minute || 0, format: 'number' },
                    { label: 'Response Time', value: metrics.avg_response_time || 0, format: 'time' },
                    { label: 'Error Rate', value: metrics.error_rate || 0, format: 'percentage' },
                    { label: 'CPU Usage', value: metrics.cpu_usage || 0, format: 'percentage' },
                    { label: 'Memory Usage', value: metrics.memory_usage || 0, format: 'percentage' }
                ];
                
                metricCards.forEach(metric => {
                    const card = this.createMetricCard(metric);
                    grid.appendChild(card);
                });
            }
            
            createMetricCard(metric) {
                const card = document.createElement('div');
                card.className = 'metric-card';
                
                let value = metric.value;
                switch (metric.format) {
                    case 'time':
                        value = `${Math.round(value)}ms`;
                        break;
                    case 'percentage':
                        value = `${Math.round(value)}%`;
                        break;
                    case 'number':
                        value = Math.round(value).toLocaleString();
                        break;
                }
                
                card.innerHTML = `
                    <div class="metric-value">${value}</div>
                    <div class="metric-label">${metric.label}</div>
                `;
                
                return card;
            }
            
            updateMetrics(metrics) {
                // Update metrics if needed
                this.renderMetrics(metrics);
            }
            
            renderIncidents(incidents) {
                const list = document.getElementById('incidents-list');
                
                if (incidents.length === 0) {
                    list.innerHTML = '<p>No recent incidents</p>';
                    return;
                }
                
                list.innerHTML = '';
                incidents.forEach(incident => {
                    const item = this.createIncidentItem(incident);
                    list.appendChild(item);
                });
            }
            
            createIncidentItem(incident) {
                const item = document.createElement('div');
                item.className = 'incident-item';
                
                const date = new Date(incident.created_at).toLocaleString();
                
                item.innerHTML = `
                    <div class="incident-title">${incident.title}</div>
                    <div class="incident-meta">
                        ${incident.status.toUpperCase()} - ${incident.impact.toUpperCase()} - ${date}
                    </div>
                    <div class="incident-description">${incident.description}</div>
                `;
                
                return item;
            }
            
            formatName(name) {
                return name.split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ');
            }
        }
        
        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new StatusDashboard();
        });
        """
        
        return web.Response(text=js, content_type='application/javascript')
        
    async def websocket_handler(self, request) -> None:
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.append(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    # Handle incoming WebSocket messages if needed
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)
                
        return ws
        
    async def api_status(self, request) -> None:
        """API endpoint for overall status"""
        overall_status = self._calculate_overall_status()
        
        return web.json_response({
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "components_count": len(self.components),
            "incidents_count": len([i for i in self.incidents.values() if i.status != "resolved"])
        })
        
    async def api_components(self, request) -> None:
        """API endpoint for components status"""
        components_data = {}
        
        for name, component in self.components.items():
            components_data[name] = {
                "name": component.name,
                "description": component.description,
                "category": component.category,
                "status": component.status.value,
                "uptime": component.uptime_percentage,
                "response_time": component.response_time,
                "error_rate": component.error_rate,
                "last_updated": component.last_updated.isoformat()
            }
            
        return web.json_response(components_data)
        
    async def api_incidents(self, request) -> None:
        """API endpoint for incidents"""
        incidents_data = []
        
        for incident in self.incidents.values():
            incidents_data.append({
                "id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "status": incident.status,
                "impact": incident.impact,
                "components": incident.components,
                "created_at": incident.created_at.isoformat(),
                "updated_at": incident.updated_at.isoformat(),
                "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None
            })
            
        # Sort by creation date (newest first)
        incidents_data.sort(key=lambda x: x['created_at'], reverse=True)
        
        return web.json_response(incidents_data[:10])  # Return last 10 incidents
        
    async def api_metrics(self, request) -> None:
        """API endpoint for metrics"""
        metrics_data = {}
        
        if self.metrics_collector:
            current_metrics = self.metrics_collector.get_current_metrics()
            
            # Extract key metrics for dashboard
            metrics_data.update({
                "cpu_usage": current_metrics.get("system.cpu.usage", {}).get("value", 0),
                "memory_usage": current_metrics.get("system.memory.usage", {}).get("value", 0),
                "active_users": 150,  # This would come from business metrics
                "api_requests_per_minute": 245,  # This would be calculated
                "avg_response_time": 125,  # This would come from performance tracker
                "error_rate": 0.5  # This would be calculated
            })
            
        return web.json_response(metrics_data)
        
    async def api_health(self, request) -> None:
        """API endpoint for health status"""
        if self.health_monitor:
            health_summary = self.health_monitor.get_health_summary()
            detailed_results = self.health_monitor.get_detailed_results()
            
            return web.json_response({
                "summary": health_summary,
                "details": detailed_results
            })
        else:
            return web.json_response({"error": "Health monitor not available"})
            
    async def api_performance(self, request) -> None:
        """API endpoint for performance metrics"""
        if self.performance_tracker:
            performance_summary = self.performance_tracker.get_performance_summary()
            return web.json_response(performance_summary)
        else:
            return web.json_response({"error": "Performance tracker not available"})
            
    async def api_business_metrics(self, request) -> None:
        """API endpoint for business metrics"""
        if self.business_metrics:
            business_kpis = await self.business_metrics.get_business_kpis()
            return web.json_response(business_kpis)
        else:
            return web.json_response({"error": "Business metrics not available"})
            
    # Utility methods
    def register_component(self, component -> None: SystemComponent) -> None:
        """Register a system component"""
        self.components[component.name] = component
        logger.info(f"Registered component: {component.name}")
        
    def update_component_status(self, name -> None: str, status -> None: ComponentStatus, **kwargs) -> None:
        """Update component status"""
        if name in self.components:
            component = self.components[name]
            component.status = status
            component.last_updated = datetime.utcnow()
            
            # Update optional fields
            for key, value in kwargs.items():
                if hasattr(component, key):
                    setattr(component, key, value)
                    
            logger.info(f"Updated component {name} status to {status.value}")
            
    
    async def get_section_data(self, section: str) -> Dict[str, Any]:
        """Get data for a specific dashboard section"""
        try:
            if section == "overview":
                return await self.get_overview_data()
            elif section == "content-protection":
                return await self.get_content_protection_data()
            elif section == "revenue":
                return await self.get_revenue_data()
            elif section == "users":
                return await self.get_user_engagement_data()
            elif section == "performance":
                return await self.get_performance_data()
            elif section == "security":
                return await self.get_security_data()
            elif section == "incidents":
                return await self.get_incidents_data()
            else:
                return {"error": f"Unknown section: {section}"}
                
        except Exception as e:
            logger.error(f"Error getting section data for {section}: {e}")
            return {"error": str(e)}
    
    async def get_overview_data(self) -> Dict[str, Any]:
        """Get overview dashboard data"""
        system_overview = await self.get_system_overview()
        
        # Get key metrics
        active_users = await self._get_metric_value("daily_active_users", 0)
        daily_revenue = await self._get_metric_value("daily_revenue", 0.0)
        fingerprints_today = await self._get_metric_value("fingerprints_processed_today", 0)
        protection_alerts = len([
            comp for comp in self.components.values()
            if comp.domain == BusinessDomain.CONTENT_PROTECTION and comp.alerts
        ])
        
        # Get component status list
        components = [
            {
                "name": comp.name,
                "status": comp.status.value,
                "uptime": comp.uptime_percentage
            }
            for comp in self.components.values()
        ]
        
        return {
            "active_users": active_users,
            "daily_revenue": f"{daily_revenue:.2f}",
            "fingerprints_today": fingerprints_today,
            "protection_alerts": protection_alerts,
            "components": components,
            "system_overview": system_overview
        }
    
    async def get_content_protection_data(self) -> Dict[str, Any]:
        """Get content protection dashboard data"""
        metrics = await self.get_cached_business_metrics(BusinessDomain.CONTENT_PROTECTION)
        
        return {
            "metrics": asdict(metrics),
            "components": [
                asdict(comp) for comp in self.components.values()
                if comp.domain == BusinessDomain.CONTENT_PROTECTION
            ]
        }
    
    async def get_revenue_data(self) -> Dict[str, Any]:
        """Get revenue dashboard data"""
        metrics = await self.get_cached_business_metrics(BusinessDomain.REVENUE_TRACKING)
        
        return {
            "metrics": asdict(metrics),
            "components": [
                asdict(comp) for comp in self.components.values()
                if comp.domain == BusinessDomain.REVENUE_TRACKING
            ]
        }
    
    async def get_user_engagement_data(self) -> Dict[str, Any]:
        """Get user engagement dashboard data"""
        metrics = await self.get_cached_business_metrics(BusinessDomain.USER_ENGAGEMENT)
        
        return {
            "metrics": asdict(metrics),
            "components": [
                asdict(comp) for comp in self.components.values()
                if comp.domain == BusinessDomain.USER_ENGAGEMENT
            ]
        }
    
    async def get_performance_data(self) -> Dict[str, Any]:
        """Get performance dashboard data"""
        performance_metrics = {}
        
        if self.performance_tracker:
            performance_metrics = await self.performance_tracker.get_system_performance_summary()
        
        return {
            "performance_metrics": performance_metrics,
            "components": [
                asdict(comp) for comp in self.components.values()
                if comp.domain == BusinessDomain.SYSTEM_INFRASTRUCTURE
            ]
        }
    
    async def get_security_data(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        metrics = await self.get_cached_business_metrics(BusinessDomain.SECURITY)
        
        return {
            "metrics": asdict(metrics),
            "components": [
                asdict(comp) for comp in self.components.values()
                if comp.domain == BusinessDomain.SECURITY
            ]
        }
    
    async def get_incidents_data(self) -> Dict[str, Any]:
        """Get incidents dashboard data"""
        active_incidents = [
            asdict(incident) for incident in self.incidents.values()
            if incident.status not in ["resolved", "closed"]
        ]
        
        recent_incidents = sorted(
            [asdict(incident) for incident in self.incidents.values()],
            key=lambda x: x["created_at"],
            reverse=True
        )[:10]
        
        return {
            "active_incidents": active_incidents,
            "recent_incidents": recent_incidents,
            "incident_stats": {
                "total": len(self.incidents),
                "active": len(active_incidents),
                "resolved_today": len([
                    inc for inc in self.incidents.values()
                    if inc.resolved_at and inc.resolved_at.date() == datetime.utcnow().date()
                ])
            }
        }
    
    async def render_section_template(self, section: str, data: Dict[str, Any]) -> str:
        """Render HTML template for a section"""
        try:
            if section == "overview":
                return self.templates.get_overview_template().format(**data)
            else:
                # For now, return a basic template
                return f'''
                <div class="section-content">
                    <h2>{section.replace("-", " ").title()}</h2>
                    <div class="widget-grid">
                        <div class="status-card">
                            <h5>Section Data</h5>
                            <pre>{json.dumps(data, indent=2, default=str)}</pre>
                        </div>
                    </div>
                </div>
                '''
                
        except Exception as e:
            logger.error(f"Error rendering template for {section}: {e}")
            return f"<div class='alert alert-danger'>Error rendering {section}: {str(e)}</div>"
    
    async def get_section_scripts(self, section: str) -> str:
        """Get JavaScript code for a section"""
        if section == "overview":
            return '''
            // Initialize overview charts
            const ctx = document.getElementById('healthChart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['1h ago', '45m ago', '30m ago', '15m ago', 'Now'],
                        datasets: [{
                            label: 'System Health',
                            data: [98, 97, 99, 98, 99],
                            borderColor: 'rgb(37, 99, 235)',
                            backgroundColor: 'rgba(37, 99, 235, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }
            '''
        return ""
    
    async def get_component_metrics(self, component_id: str) -> Dict[str, Any]:
        """Get detailed metrics for a component"""
        if self.performance_tracker:
            return await self.performance_tracker.get_component_performance(component_id)
        return {}
    
    async def get_component_history(self, component_id: str) -> List[Dict[str, Any]]:
        """Get historical data for a component"""
        # This would typically fetch from a time series database
        return []
    
    async def get_performance_metrics(self, time_range: str) -> Dict[str, Any]:
        """Get system performance metrics"""
        if self.performance_tracker:
            return await self.performance_tracker.get_system_performance_summary()
        return {}
    
    async def get_health_metrics(self, time_range: str) -> Dict[str, Any]:
        """Get system health metrics"""
        if self.health_monitor:
            return await self.health_monitor.get_health_summary()
        return {}
    
    async def start_dashboard(self) -> None:
        """Start the status dashboard"""
        try:
            if self._dashboard_running:
                logger.warning("Dashboard is already running")
                return
            
            self._dashboard_running = True
            
            # Start background update task
            self._update_task = asyncio.create_task(self._update_loop())
            
            # Start web server
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', self.port)
            await site.start()
            
            logger.info(f"Status dashboard started on port {self.port}")
            
        except Exception as e:
            logger.error(f"Error starting dashboard: {e}")
            self._dashboard_running = False
            raise
    
    async def stop_dashboard(self) -> None:
        """Stop the status dashboard"""
        try:
            self._dashboard_running = False
            
            # Cancel update task
            if self._update_task:
                self._update_task.cancel()
                try:
                    await self._update_task
                except asyncio.CancelledError:
                    pass
            
            # Close WebSocket connections
            for ws in self.websocket_connections:
                await ws.close()
            self.websocket_connections.clear()
            
            logger.info("Status dashboard stopped")
            
        except Exception as e:
            logger.error(f"Error stopping dashboard: {e}")
    
    async def _update_loop(self) -> None:
        """Background update loop for real-time data"""
        try:
            while self._dashboard_running:
                # Update component statuses
                await self.update_component_statuses()
                
                # Broadcast updates to WebSocket clients
                if self.websocket_connections:
                    update_data = {
                        "type": "status_update",
                        "payload": {
                            "components": {
                                comp_id: asdict(comp) 
                                for comp_id, comp in self.components.items()
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    await self.broadcast_to_websockets(update_data)
                
                # Wait before next update
                await asyncio.sleep(30)  # Update every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("Dashboard update loop cancelled")
        except Exception as e:
            logger.error(f"Error in dashboard update loop: {e}")
    
    def create_incident(
        self,
        title: str,
        description: str,
        impact: str,
        components: List[str]
    ) -> str:
        """Create a new incident"""
        incident_id = f"incident_{int(datetime.utcnow().timestamp())}"
        
        incident = StatusIncident(
            id=incident_id,
            title=title,
            description=description,
            status="investigating",
            impact=impact,
            components=components,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.incidents[incident_id] = incident
        logger.info(f"Created incident: {incident_id}")
        
        return incident_id
        
    def update_incident(self, incident_id -> None: str, status -> None: str, update_message -> None: str) -> None:
        """Update an incident"""
        if incident_id in self.incidents:
            incident = self.incidents[incident_id]
            incident.status = status
            incident.updated_at = datetime.utcnow()
            
            if status == "resolved":
                incident.resolved_at = datetime.utcnow()
                
            incident.updates.append({
                "timestamp": datetime.utcnow().isoformat(),
                "message": update_message,
                "status": status
            })
            
            logger.info(f"Updated incident {incident_id}: {status}")
            
    def _calculate_overall_status(self) -> ComponentStatus:
        """Calculate overall system status"""
        if not self.components:
            return ComponentStatus.OPERATIONAL
            
        if ComponentStatus.MAJOR_OUTAGE in statuses:
            return ComponentStatus.MAJOR_OUTAGE
        elif ComponentStatus.PARTIAL_OUTAGE in statuses:
            return ComponentStatus.PARTIAL_OUTAGE
        elif ComponentStatus.DEGRADED in statuses:
            return ComponentStatus.DEGRADED
        elif ComponentStatus.MAINTENANCE in statuses:
            return ComponentStatus.MAINTENANCE
        else:
            return ComponentStatus.OPERATIONAL


# Example usage
async def create_status_dashboard_example() -> None:
    """Example of creating and running a status dashboard"""
    import aioredis
    
    # Initialize Redis client
    redis_client = await aioredis.create_redis_pool('redis://localhost:6379')
    
    # Create dashboard
    dashboard = StatusDashboard(
        redis_client=redis_client,
        port=8080,
        enable_auth=False  # Disable for development
    )
    
    # Add some example incidents
    dashboard.create_incident(
        title="API Gateway Latency Issues",
        description="Increased response times observed on the main API gateway",
        impact="minor",
        components=["core_api_gateway"]
    )
    
    # Start dashboard
    await dashboard.start_dashboard()
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await dashboard.stop_dashboard()
    finally:
        redis_client.close()


if __name__ == "__main__":
    # Run the example
    asyncio.run(create_status_dashboard_example())
        
        if ComponentStatus.MAJOR_OUTAGE in statuses:
            return ComponentStatus.MAJOR_OUTAGE
        elif ComponentStatus.PARTIAL_OUTAGE in statuses:
            return ComponentStatus.PARTIAL_OUTAGE
        elif ComponentStatus.DEGRADED in statuses:
            return ComponentStatus.DEGRADED
        elif ComponentStatus.MAINTENANCE in statuses:
            return ComponentStatus.MAINTENANCE
        else:
            return ComponentStatus.OPERATIONAL

# File has syntax issues - needs manual review