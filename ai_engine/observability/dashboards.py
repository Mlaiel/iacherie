"""Interactive Dashboard System

Advanced dashboard system for the IA Influencer platform providing
interactive visualizations, real-time data display, and customizable monitoring views.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""import asyncio
import json
import time
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import statistics
import logging

logger = logging.getLogger(__name__)


class DashboardType(Enum):
    """Dashboard types"""    OVERVIEW = "overview"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    AI_MODELS = "ai_models"
    CONTENT_PROTECTION = "content_protection"
    USER_ANALYTICS = "user_analytics"
    SYSTEM_HEALTH = "system_health"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


class WidgetType(Enum):
    """Widget types for dashboards"""    METRIC = "metric"                    # Single metric display
    GAUGE = "gauge"                      # Circular gauge
    CHART = "chart"                      # Line/bar/pie chart
    TABLE = "table"                      # Data table
    MAP = "map"                          # Geographic map
    HEATMAP = "heatmap"                  # Heat map visualization
    ALERT_PANEL = "alert_panel"          # Alert status panel
    TEXT = "text"                        # Text/markdown content
    IFRAME = "iframe"                    # Embedded content
    STATUS_INDICATOR = "status_indicator" # Status lights
    PROGRESS_BAR = "progress_bar"        # Progress visualization
    LOG_VIEWER = "log_viewer"            # Log display
    CUSTOM = "custom"                    # Custom widget


class ChartType(Enum):
    """Chart visualization types"""    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    CANDLESTICK = "candlestick"
    TREEMAP = "treemap"
    FUNNEL = "funnel"


class RefreshInterval(Enum):
    """Dashboard refresh intervals"""    REAL_TIME = 1        # 1 second
    FAST = 5             # 5 seconds
    NORMAL = 30          # 30 seconds
    SLOW = 300           # 5 minutes
    MANUAL = 0           # Manual refresh only


@dataclass
class WidgetConfig:
    """Widget configuration"""    widget_id: str
    title: str
    widget_type: WidgetType
    position: Dict[str, int]           # x, y, width, height
    data_source: str
    query: str
    chart_type: Optional[ChartType] = None
    options: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: RefreshInterval = RefreshInterval.NORMAL
    thresholds: Dict[str, float] = field(default_factory=dict)
    format_settings: Dict[str, Any] = field(default_factory=dict)
    is_visible: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'widget_id': self.widget_id,
            'title': self.title,
            'widget_type': self.widget_type.value,
            'position': self.position,
            'data_source': self.data_source,
            'query': self.query,
            'chart_type': self.chart_type.value if self.chart_type else None,
            'options': self.options,
            'refresh_interval': self.refresh_interval.value,
            'thresholds': self.thresholds,
            'format_settings': self.format_settings,
            'is_visible': self.is_visible,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class Dashboard:
    """Dashboard definition"""    dashboard_id: str
    name: str
    description: str
    dashboard_type: DashboardType
    widgets: List[WidgetConfig] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    is_public: bool = False
    is_default: bool = False
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'dashboard_id': self.dashboard_id,
            'name': self.name,
            'description': self.description,
            'dashboard_type': self.dashboard_type.value,
            'widgets': [w.to_dict() for w in self.widgets],
            'layout': self.layout,
            'permissions': self.permissions,
            'tags': self.tags,
            'is_public': self.is_public,
            'is_default': self.is_default,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class WidgetData:
    """Widget data response"""    widget_id: str
    data: Any
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'widget_id': self.widget_id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'error': self.error
        }


class DataProvider:
    """    Base class for dashboard data providers
    
    Data providers fetch and format data for dashboard widgets
    """    
    def __init__(self, provider_name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize data provider"""        self.provider_name = provider_name
        self.config = config or {}
        
    async def fetch_data(self, query: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """Fetch data based on query - base implementation"""        try:
            # Basic implementation that returns simulated data
            logger.info(f"Fetching data for query: {query}")
            
            options = options or {}
            
            # Return sample data structure based on query type
            if "metrics" in query.lower():
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "values": [
                        {"name": "cpu_usage", "value": 45.2},
                        {"name": "memory_usage", "value": 67.8},
                        {"name": "disk_usage", "value": 34.1}
                    ],
                    "query": query,
                    "provider": self.provider_name
                }
            elif "logs" in query.lower():
                return {
                    "total_count": 1250,
                    "logs": [
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "level": "INFO",
                            "message": "Sample log entry",
                            "source": "application"
                        }
                    ],
                    "query": query
                }
            else:
                # Generic data structure
                return {
                    "data": [1, 2, 3, 4, 5],
                    "labels": ["A", "B", "C", "D", "E"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "query": query,
                    "provider": self.provider_name
                }
                
        except Exception as e:
            logger.error(f"Error fetching data for query '{query}': {str(e)}")
            return {
                "error": str(e),
                "query": query,
                "provider": self.provider_name
            }
    
    async def validate_query(self, query: str) -> bool:
        """Validate query syntax"""        return True  # Default implementation allows all queries
    
    def format_data(self, raw_data: Any, widget_type: WidgetType) -> Any:
        """Format data for specific widget type"""        return raw_data  # Default implementation returns raw data


class MetricsDataProvider(DataProvider):
    """Data provider for metrics data"""    
    def __init__(self, metrics_collector, config: Optional[Dict[str, Any]] = None):
        """Initialize metrics data provider"""        super().__init__("metrics", config)
        self.metrics_collector = metrics_collector
    
    async def fetch_data(self, query: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """Fetch metrics data"""        try:
            # Parse query to extract metric name and aggregation
            parts = query.split()
            metric_name = parts[0]
            
            aggregation = "current"
            if len(parts) > 1:
                aggregation = parts[1]
            
            timeframe = options.get('timeframe', '1h') if options else '1h'
            
            # Get data from metrics collector
            if aggregation == "current":
                data = await self._get_current_metric(metric_name)
            elif aggregation == "history":
                data = await self._get_metric_history(metric_name, timeframe)
            elif aggregation == "avg":
                data = await self._get_metric_average(metric_name, timeframe)
            else:
                data = await self._get_current_metric(metric_name)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch metrics data for query '{query}': {str(e)}")
            return None
    
    async def _get_current_metric(self, metric_name: str) -> Dict[str, Any]:
        """Get current metric value"""        try:
            # Simulate getting current metric value
            current_value = getattr(self.metrics_collector, 'get_current_value', lambda x: 0)(metric_name)
            
            return {
                'metric_name': metric_name,
                'value': current_value,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get current metric {metric_name}: {str(e)}")
            return {'metric_name': metric_name, 'value': 0, 'timestamp': datetime.now(timezone.utc).isoformat()}
    
    async def _get_metric_history(self, metric_name: str, timeframe: str) -> List[Dict[str, Any]]:
        """Get metric history"""        try:
            # Simulate historical data generation
            data_points = []
            now = datetime.now(timezone.utc)
            
            # Parse timeframe (simplified)
            if timeframe.endswith('h'):
                hours = int(timeframe[:-1])
                points = min(hours * 6, 100)  # 6 points per hour, max 100
                interval = timedelta(hours=hours) / points
            else:
                points = 50
                interval = timedelta(hours=1) / points
            
            # Generate sample data points
            for i in range(points):
                timestamp = now - (interval * (points - i))
                value = 50 + (i % 20) + (i // 10) * 5  # Sample trending data
                
                data_points.append({
                    'timestamp': timestamp.isoformat(),
                    'value': value
                })
            
            return data_points
            
        except Exception as e:
            logger.error(f"Failed to get metric history for {metric_name}: {str(e)}")
            return []
    
    async def _get_metric_average(self, metric_name: str, timeframe: str) -> Dict[str, Any]:
        """Get metric average over timeframe"""        try:
            history = await self._get_metric_history(metric_name, timeframe)
            
            if not history:
                return {'metric_name': metric_name, 'average': 0}
            
            values = [point['value'] for point in history]
            average = sum(values) / len(values)
            
            return {
                'metric_name': metric_name,
                'average': average,
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
            
        except Exception as e:
            logger.error(f"Failed to get metric average for {metric_name}: {str(e)}")
            return {'metric_name': metric_name, 'average': 0}


class AlertsDataProvider(DataProvider):
    """Data provider for alerts data"""    
    def __init__(self, alert_manager, config: Optional[Dict[str, Any]] = None):
        """Initialize alerts data provider"""        super().__init__("alerts", config)
        self.alert_manager = alert_manager
    
    async def fetch_data(self, query: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """Fetch alerts data"""        try:
            if query == "active":
                return await self._get_active_alerts(options)
            elif query == "recent":
                return await self._get_recent_alerts(options)
            elif query == "summary":
                return await self._get_alerts_summary(options)
            else:
                return await self._get_active_alerts(options)
            
        except Exception as e:
            logger.error(f"Failed to fetch alerts data for query '{query}': {str(e)}")
            return []
    
    async def _get_active_alerts(self, options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get active alerts"""        try:
            filters = options.get('filters', {}) if options else {}
            alerts = self.alert_manager.get_active_alerts(filters)
            
            return [alert.to_dict() for alert in alerts]
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {str(e)}")
            return []
    
    async def _get_recent_alerts(self, options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get recent alerts"""        try:
            limit = options.get('limit', 50) if options else 50
            
            # Get from alert history (simplified)
            recent_alerts = self.alert_manager.alert_history[-limit:] if hasattr(self.alert_manager, 'alert_history') else []
            
            return [alert.to_dict() for alert in recent_alerts]
            
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {str(e)}")
            return []
    
    async def _get_alerts_summary(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get alerts summary"""        try:
            active_alerts = self.alert_manager.get_active_alerts()
            
            summary = {
                'total_active': len(active_alerts),
                'by_severity': {},
                'by_category': {},
                'oldest_alert': None,
                'newest_alert': None
            }
            
            if active_alerts:
                # Group by severity
                for alert in active_alerts:
                    severity = alert.severity.value
                    summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
                    
                    category = alert.category.value
                    summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
                
                # Find oldest and newest
                sorted_alerts = sorted(active_alerts, key=lambda a: a.triggered_at)
                summary['oldest_alert'] = sorted_alerts[0].to_dict()
                summary['newest_alert'] = sorted_alerts[-1].to_dict()
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get alerts summary: {str(e)}")
            return {'total_active': 0, 'by_severity': {}, 'by_category': {}}


class SystemDataProvider(DataProvider):
    """Data provider for system information"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize system data provider"""        super().__init__("system", config)
    
    async def fetch_data(self, query: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """Fetch system data"""        try:
            if query == "health":
                return await self._get_system_health()
            elif query == "resources":
                return await self._get_resource_usage()
            elif query == "services":
                return await self._get_service_status()
            else:
                return await self._get_system_health()
            
        except Exception as e:
            logger.error(f"Failed to fetch system data for query '{query}': {str(e)}")
            return {}
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health information"""        try:
            # Simulate system health data
            health = {
                'status': 'healthy',
                'uptime': 3600 * 24 * 5,  # 5 days in seconds
                'version': '2.1.0',
                'environment': 'production',
                'components': {
                    'database': {'status': 'healthy', 'response_time': 15},
                    'cache': {'status': 'healthy', 'response_time': 2},
                    'storage': {'status': 'healthy', 'free_space': 85.5},
                    'ai_models': {'status': 'healthy', 'active_models': 12}
                },
                'last_check': datetime.now(timezone.utc).isoformat()
            }
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get system health: {str(e)}")
            return {'status': 'unknown'}
    
    async def _get_resource_usage(self) -> Dict[str, Any]:
        """Get resource usage information"""        try:
            # Simulate resource usage data
            resources = {
                'cpu': {
                    'current': 45.2,
                    'average': 42.1,
                    'max': 78.9
                },
                'memory': {
                    'used': 6.2,
                    'total': 16.0,
                    'percentage': 38.75
                },
                'disk': {
                    'used': 425.6,
                    'total': 1024.0,
                    'percentage': 41.6
                },
                'network': {
                    'inbound_mbps': 125.4,
                    'outbound_mbps': 89.2
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return resources
            
        except Exception as e:
            logger.error(f"Failed to get resource usage: {str(e)}")
            return {}
    
    async def _get_service_status(self) -> List[Dict[str, Any]]:
        """Get service status information"""        try:
            # Simulate service status data
            services = [
                {'name': 'API Gateway', 'status': 'running', 'uptime': 3600 * 48},
                {'name': 'Content Processing', 'status': 'running', 'uptime': 3600 * 72},
                {'name': 'AI Model Server', 'status': 'running', 'uptime': 3600 * 24},
                {'name': 'Database', 'status': 'running', 'uptime': 3600 * 168},
                {'name': 'Cache Server', 'status': 'running', 'uptime': 3600 * 96},
                {'name': 'Background Jobs', 'status': 'running', 'uptime': 3600 * 12}
            ]
            
            return services
            
        except Exception as e:
            logger.error(f"Failed to get service status: {str(e)}")
            return []


class DashboardEngine:
    """    Main dashboard engine managing dashboards, widgets, and data
    
    Features:
    - Dashboard management
    - Widget data fetching
    - Real-time updates
    - Custom dashboard creation
    - Permission management
    - Caching and optimization
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dashboard engine"""        self.config = config or {}
        
        # Dashboard storage
        self.dashboards: Dict[str, Dashboard] = {}
        self.data_providers: Dict[str, DataProvider] = {}
        
        # Real-time updates
        self.update_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.update_task = None
        
        # Caching
        self.widget_cache: Dict[str, WidgetData] = {}
        self.cache_ttl = self.config.get('cache_ttl', 30)  # seconds
        
        # Performance tracking
        self.performance_stats = {
            'dashboard_views': defaultdict(int),
            'widget_renders': defaultdict(int),
            'data_fetch_times': defaultdict(list)
        }
    
    def register_data_provider(self, provider: DataProvider):
        """Register a data provider"""        try:
            self.data_providers[provider.provider_name] = provider
            logger.info(f"Registered data provider: {provider.provider_name}")
            
        except Exception as e:
            logger.error(f"Failed to register data provider: {str(e)}")
    
    def create_dashboard(self, dashboard: Dashboard) -> bool:
        """Create a new dashboard"""        try:
            # Validate dashboard
            if not dashboard.dashboard_id or not dashboard.name:
                logger.error("Dashboard must have ID and name")
                return False
            
            # Check for duplicates
            if dashboard.dashboard_id in self.dashboards:
                logger.error(f"Dashboard with ID '{dashboard.dashboard_id}' already exists")
                return False
            
            # Validate widgets
            for widget in dashboard.widgets:
                if not self._validate_widget(widget):
                    logger.error(f"Invalid widget configuration: {widget.widget_id}")
                    return False
            
            # Store dashboard
            self.dashboards[dashboard.dashboard_id] = dashboard
            logger.info(f"Created dashboard: {dashboard.name} ({dashboard.dashboard_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {str(e)}")
            return False
    
    def _validate_widget(self, widget: WidgetConfig) -> bool:
        """Validate widget configuration"""        try:
            # Check required fields
            if not widget.widget_id or not widget.title or not widget.data_source:
                return False
            
            # Check data source exists
            if widget.data_source not in self.data_providers:
                logger.warning(f"Data provider '{widget.data_source}' not found for widget {widget.widget_id}")
                return False
            
            # Validate position
            required_pos_fields = ['x', 'y', 'width', 'height']
            if not all(field in widget.position for field in required_pos_fields):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate widget: {str(e)}")
            return False
    
    def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing dashboard"""        try:
            if dashboard_id not in self.dashboards:
                logger.error(f"Dashboard not found: {dashboard_id}")
                return False
            
            dashboard = self.dashboards[dashboard_id]
            
            # Update allowed fields
            allowed_updates = ['name', 'description', 'widgets', 'layout', 'permissions', 'tags', 'is_public']
            
            for field, value in updates.items():
                if field in allowed_updates:
                    setattr(dashboard, field, value)
            
            dashboard.updated_at = datetime.now(timezone.utc)
            
            # Invalidate cache for this dashboard
            self._invalidate_dashboard_cache(dashboard_id)
            
            logger.info(f"Updated dashboard: {dashboard_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update dashboard {dashboard_id}: {str(e)}")
            return False
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete dashboard"""        try:
            if dashboard_id not in self.dashboards:
                logger.error(f"Dashboard not found: {dashboard_id}")
                return False
            
            del self.dashboards[dashboard_id]
            
            # Clean up cache
            self._invalidate_dashboard_cache(dashboard_id)
            
            logger.info(f"Deleted dashboard: {dashboard_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete dashboard {dashboard_id}: {str(e)}")
            return False
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID"""        return self.dashboards.get(dashboard_id)
    
    def list_dashboards(self, filters: Optional[Dict[str, Any]] = None) -> List[Dashboard]:
        """List dashboards with optional filtering"""        try:
            dashboards = list(self.dashboards.values())
            
            if not filters:
                return dashboards
            
            # Apply filters
            filtered_dashboards = []
            for dashboard in dashboards:
                include = True
                
                if 'type' in filters and dashboard.dashboard_type.value != filters['type']:
                    include = False
                
                if 'tags' in filters:
                    required_tags = filters['tags'] if isinstance(filters['tags'], list) else [filters['tags']]
                    if not any(tag in dashboard.tags for tag in required_tags):
                        include = False
                
                if 'public_only' in filters and filters['public_only'] and not dashboard.is_public:
                    include = False
                
                if include:
                    filtered_dashboards.append(dashboard)
            
            return filtered_dashboards
            
        except Exception as e:
            logger.error(f"Failed to list dashboards: {str(e)}")
            return []
    
    async def get_widget_data(self, widget: WidgetConfig, force_refresh: bool = False) -> WidgetData:
        """Get data for a specific widget"""        try:
            # Check cache first
            cache_key = f"{widget.widget_id}_{hash(widget.query)}"
            
            if not force_refresh and cache_key in self.widget_cache:
                cached_data = self.widget_cache[cache_key]
                cache_age = (datetime.now(timezone.utc) - cached_data.timestamp).total_seconds()
                
                if cache_age < self.cache_ttl:
                    return cached_data
            
            # Fetch fresh data
            start_time = time.time()
            
            data_provider = self.data_providers.get(widget.data_source)
            if not data_provider:
                return WidgetData(
                    widget_id=widget.widget_id,
                    data=None,
                    timestamp=datetime.now(timezone.utc),
                    error=f"Data provider '{widget.data_source}' not found"
                )
            
            # Fetch raw data
            raw_data = await data_provider.fetch_data(widget.query, widget.options)
            
            # Format data for widget type
            formatted_data = data_provider.format_data(raw_data, widget.widget_type)
            
            # Create widget data response
            widget_data = WidgetData(
                widget_id=widget.widget_id,
                data=formatted_data,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'fetch_time_ms': (time.time() - start_time) * 1000,
                    'data_source': widget.data_source,
                    'cache_key': cache_key
                }
            )
            
            # Cache the result
            self.widget_cache[cache_key] = widget_data
            
            # Update performance stats
            self.performance_stats['widget_renders'][widget.widget_id] += 1
            self.performance_stats['data_fetch_times'][widget.data_source].append(time.time() - start_time)
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Failed to get widget data for {widget.widget_id}: {str(e)}")
            return WidgetData(
                widget_id=widget.widget_id,
                data=None,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    async def get_dashboard_data(self, dashboard_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Get complete dashboard data"""        try:
            dashboard = self.get_dashboard(dashboard_id)
            
            if not dashboard:
                return {'error': f'Dashboard not found: {dashboard_id}'}
            
            # Track dashboard view
            self.performance_stats['dashboard_views'][dashboard_id] += 1
            
            # Get data for all widgets
            widget_data = {}
            widget_tasks = []
            
            for widget in dashboard.widgets:
                if widget.is_visible:
                    task = self.get_widget_data(widget, force_refresh)
                    widget_tasks.append((widget.widget_id, task))
            
            # Execute widget data fetches concurrently
            for widget_id, task in widget_tasks:
                try:
                    data = await task
                    widget_data[widget_id] = data.to_dict()
                except Exception as e:
                    logger.error(f"Failed to get data for widget {widget_id}: {str(e)}")
                    widget_data[widget_id] = {
                        'widget_id': widget_id,
                        'data': None,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'error': str(e)
                    }
            
            return {
                'dashboard': dashboard.to_dict(),
                'widget_data': widget_data,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'performance': {
                    'total_widgets': len(widget_data),
                    'widgets_with_data': sum(1 for w in widget_data.values() if w.get('data') is not None),
                    'widgets_with_errors': sum(1 for w in widget_data.values() if w.get('error') is not None)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data for {dashboard_id}: {str(e)}")
            return {'error': str(e)}
    
    def _invalidate_dashboard_cache(self, dashboard_id: str):
        """Invalidate cache for a dashboard"""        try:
            dashboard = self.get_dashboard(dashboard_id)
            if not dashboard:
                return
            
            # Remove cached data for all widgets in this dashboard
            widget_ids = [widget.widget_id for widget in dashboard.widgets]
            
            cache_keys_to_remove = []
            for cache_key in self.widget_cache:
                for widget_id in widget_ids:
                    if cache_key.startswith(f"{widget_id}_"):
                        cache_keys_to_remove.append(cache_key)
                        break
            
            for cache_key in cache_keys_to_remove:
                del self.widget_cache[cache_key]
            
            logger.info(f"Invalidated cache for dashboard {dashboard_id}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache for dashboard {dashboard_id}: {str(e)}")
    
    async def start_real_time_updates(self):
        """Start real-time dashboard updates"""        try:
            logger.info("Starting real-time dashboard updates")
            self.update_task = asyncio.create_task(self._update_loop())
            
        except Exception as e:
            logger.error(f"Failed to start real-time updates: {str(e)}")
    
    async def stop_real_time_updates(self):
        """Stop real-time dashboard updates"""        try:
            logger.info("Stopping real-time dashboard updates")
            
            if self.update_task:
                self.update_task.cancel()
                try:
                    await self.update_task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            logger.error(f"Failed to stop real-time updates: {str(e)}")
    
    async def _update_loop(self):
        """Real-time update loop"""        while True:
            try:
                # Update widgets that need real-time refresh
                await self._update_real_time_widgets()
                
                # Clean up old cache entries
                await self._cleanup_cache()
                
                # Wait before next update
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in update loop: {str(e)}")
                await asyncio.sleep(5)
    
    async def _update_real_time_widgets(self):
        """Update widgets that need real-time refresh"""        try:
            current_time = datetime.now(timezone.utc)
            widgets_to_update = []
            
            # Find widgets that need updating
            for dashboard in self.dashboards.values():
                for widget in dashboard.widgets:
                    if (widget.is_visible and 
                        widget.refresh_interval in [RefreshInterval.REAL_TIME, RefreshInterval.FAST]):
                        
                        # Check if it's time to update
                        cache_key = f"{widget.widget_id}_{hash(widget.query)}"
                        
                        if cache_key in self.widget_cache:
                            last_update = self.widget_cache[cache_key].timestamp
                            age = (current_time - last_update).total_seconds()
                            
                            if age >= widget.refresh_interval.value:
                                widgets_to_update.append(widget)
                        else:
                            widgets_to_update.append(widget)
            
            # Update widgets
            update_tasks = []
            for widget in widgets_to_update[:20]:  # Limit concurrent updates
                task = self.get_widget_data(widget, force_refresh=True)
                update_tasks.append(task)
            
            if update_tasks:
                await asyncio.gather(*update_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Failed to update real-time widgets: {str(e)}")
    
    async def _cleanup_cache(self):
        """Clean up old cache entries"""        try:
            current_time = datetime.now(timezone.utc)
            max_cache_age = self.cache_ttl * 3  # Keep cache 3x longer than TTL
            
            expired_keys = []
            for cache_key, widget_data in self.widget_cache.items():
                age = (current_time - widget_data.timestamp).total_seconds()
                if age > max_cache_age:
                    expired_keys.append(cache_key)
            
            for key in expired_keys:
                del self.widget_cache[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {str(e)}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get dashboard performance statistics"""        try:
            stats = {
                'dashboard_views': dict(self.performance_stats['dashboard_views']),
                'widget_renders': dict(self.performance_stats['widget_renders']),
                'data_providers': {},
                'cache_stats': {
                    'total_entries': len(self.widget_cache),
                    'cache_hit_rate': 0.0
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Calculate average fetch times by data provider
            for provider, times in self.performance_stats['data_fetch_times'].items():
                if times:
                    stats['data_providers'][provider] = {
                        'avg_fetch_time_ms': (sum(times) / len(times)) * 1000,
                        'min_fetch_time_ms': min(times) * 1000,
                        'max_fetch_time_ms': max(times) * 1000,
                        'total_requests': len(times)
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {str(e)}")
            return {}


# Pre-defined dashboard templates
class DashboardTemplates:
    """Pre-defined dashboard templates for common use cases"""    
    @staticmethod
    def create_overview_dashboard() -> Dashboard:
        """Create system overview dashboard"""        widgets = [
            WidgetConfig(
                widget_id="system_health",
                title="System Health",
                widget_type=WidgetType.STATUS_INDICATOR,
                position={'x': 0, 'y': 0, 'width': 3, 'height': 2},
                data_source="system",
                query="health",
                refresh_interval=RefreshInterval.NORMAL
            ),
            WidgetConfig(
                widget_id="active_alerts",
                title="Active Alerts",
                widget_type=WidgetType.METRIC,
                position={'x': 3, 'y': 0, 'width': 3, 'height': 2},
                data_source="alerts",
                query="summary",
                refresh_interval=RefreshInterval.FAST
            ),
            WidgetConfig(
                widget_id="resource_usage",
                title="Resource Usage",
                widget_type=WidgetType.GAUGE,
                position={'x': 6, 'y': 0, 'width': 6, 'height': 4},
                data_source="system",
                query="resources",
                refresh_interval=RefreshInterval.NORMAL
            ),
            WidgetConfig(
                widget_id="recent_alerts",
                title="Recent Alerts",
                widget_type=WidgetType.TABLE,
                position={'x': 0, 'y': 2, 'width': 6, 'height': 4},
                data_source="alerts",
                query="recent",
                options={'limit': 10},
                refresh_interval=RefreshInterval.FAST
            )
        ]
        
        return Dashboard(
            dashboard_id="system_overview",
            name="System Overview",
            description="High-level system status and health monitoring",
            dashboard_type=DashboardType.OVERVIEW,
            widgets=widgets,
            is_default=True
        )
    
    @staticmethod
    def create_performance_dashboard() -> Dashboard:
        """Create performance monitoring dashboard"""        widgets = [
            WidgetConfig(
                widget_id="response_time_chart",
                title="API Response Time",
                widget_type=WidgetType.CHART,
                chart_type=ChartType.LINE,
                position={'x': 0, 'y': 0, 'width': 6, 'height': 4},
                data_source="metrics",
                query="api_response_time history",
                options={'timeframe': '1h'},
                refresh_interval=RefreshInterval.NORMAL
            ),
            WidgetConfig(
                widget_id="throughput_chart",
                title="Request Throughput",
                widget_type=WidgetType.CHART,
                chart_type=ChartType.BAR,
                position={'x': 6, 'y': 0, 'width': 6, 'height': 4},
                data_source="metrics",
                query="request_count history",
                options={'timeframe': '1h'},
                refresh_interval=RefreshInterval.NORMAL
            ),
            WidgetConfig(
                widget_id="error_rate",
                title="Error Rate",
                widget_type=WidgetType.GAUGE,
                position={'x': 0, 'y': 4, 'width': 4, 'height': 3},
                data_source="metrics",
                query="error_rate current",
                thresholds={'warning': 1.0, 'critical': 5.0},
                refresh_interval=RefreshInterval.FAST
            ),
            WidgetConfig(
                widget_id="active_users",
                title="Active Users",
                widget_type=WidgetType.METRIC,
                position={'x': 4, 'y': 4, 'width': 4, 'height': 3},
                data_source="metrics",
                query="active_users current",
                refresh_interval=RefreshInterval.NORMAL
            ),
            WidgetConfig(
                widget_id="database_performance",
                title="Database Performance",
                widget_type=WidgetType.CHART,
                chart_type=ChartType.AREA,
                position={'x': 8, 'y': 4, 'width': 4, 'height': 3},
                data_source="metrics",
                query="db_query_time history",
                options={'timeframe': '2h'},
                refresh_interval=RefreshInterval.NORMAL
            )
        ]
        
        return Dashboard(
            dashboard_id="performance_monitoring",
            name="Performance Monitoring",
            description="Application and system performance metrics",
            dashboard_type=DashboardType.PERFORMANCE,
            widgets=widgets
        )
    
    @staticmethod
    def create_business_dashboard() -> Dashboard:
        """Create business metrics dashboard"""        widgets = [
            WidgetConfig(
                widget_id="revenue_chart",
                title="Revenue Trend",
                widget_type=WidgetType.CHART,
                chart_type=ChartType.LINE,
                position={'x': 0, 'y': 0, 'width': 8, 'height': 4},
                data_source="metrics",
                query="revenue history",
                options={'timeframe': '7d'},
                refresh_interval=RefreshInterval.SLOW
            ),
            WidgetConfig(
                widget_id="user_registrations",
                title="New User Registrations",
                widget_type=WidgetType.CHART,
                chart_type=ChartType.BAR,
                position={'x': 8, 'y': 0, 'width': 4, 'height': 4},
                data_source="metrics",
                query="user_registrations history",
                options={'timeframe': '7d'},
                refresh_interval=RefreshInterval.SLOW
            ),
            WidgetConfig(
                widget_id="content_uploads",
                title="Content Uploads Today",
                widget_type=WidgetType.METRIC,
                position={'x': 0, 'y': 4, 'width': 3, 'height': 2},
                data_source="metrics",
                query="content_uploads current",
                refresh_interval=RefreshInterval.NORMAL
            ),
            WidgetConfig(
                widget_id="protection_requests",
                title="Protection Requests",
                widget_type=WidgetType.METRIC,
                position={'x': 3, 'y': 4, 'width': 3, 'height': 2},
                data_source="metrics",
                query="protection_requests current",
                refresh_interval=RefreshInterval.NORMAL
            ),
            WidgetConfig(
                widget_id="collaboration_matches",
                title="Collaboration Matches",
                widget_type=WidgetType.METRIC,
                position={'x': 6, 'y': 4, 'width': 3, 'height': 2},
                data_source="metrics",
                query="collaboration_matches current",
                refresh_interval=RefreshInterval.NORMAL
            ),
            WidgetConfig(
                widget_id="platform_distribution",
                title="Content Distribution by Platform",
                widget_type=WidgetType.CHART,
                chart_type=ChartType.PIE,
                position={'x': 9, 'y': 4, 'width': 3, 'height': 2},
                data_source="metrics",
                query="platform_distribution current",
                refresh_interval=RefreshInterval.SLOW
            )
        ]
        
        return Dashboard(
            dashboard_id="business_metrics",
            name="Business Metrics",
            description="Key business performance indicators and metrics",
            dashboard_type=DashboardType.BUSINESS,
            widgets=widgets
        )
