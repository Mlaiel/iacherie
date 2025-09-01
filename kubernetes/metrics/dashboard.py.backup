"""IA Influencer Agent - Metrics Dashboard Engine
Enterprise-grade real-time dashboard with advanced visualization and business intelligence

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Real-time interactive dashboards with sub-second updates
- Advanced business intelligence with predictive analytics
- Multi-tenant dashboard isolation with security
- Customizable widgets with drag-and-drop interface
- Advanced data visualization with ML insights
- Export capabilities (PDF, Excel, PNG, JSON)
- Mobile-responsive design with offline caching
- Advanced filtering and correlation analysis
"""
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from pathlib import Path
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import plotly.figure_factory as ff

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager
from backend.utils.security import SecurityManager
from backend.models.dashboard import DashboardModel, WidgetModel
from backend.deployment.metrics.metrics_collector import MetricsCollector
from backend.deployment.metrics.performance_analytics import PerformanceAnalytics
from backend.deployment.metrics.alert_manager import AlertManager
from .config import get_metrics_config, MetricsConfiguration

logger = get_logger(__name__)
settings = get_settings()


class ChartType(Enum):
    """Enhanced chart types with business intelligence features"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    STAT = "stat"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    VIOLIN_PLOT = "violin_plot"
    SUNBURST = "sunburst"
    TREEMAP = "treemap"
    WATERFALL = "waterfall"
    FUNNEL = "funnel"
    SANKEY = "sankey"
    RADAR = "radar"
    CANDLESTICK = "candlestick"
    BUBBLE = "bubble"
    CORRELATION_MATRIX = "correlation_matrix"
    FORECASTING = "forecasting"
    ANOMALY_DETECTION = "anomaly_detection"
    BUSINESS_INSIGHTS = "business_insights"


class TimeRange(Enum):
    """Time range options for dashboard data"""
    LAST_5M = "5m"
    LAST_15M = "15m"
    LAST_1H = "1h"
    LAST_6H = "6h"
    LAST_24H = "24h"
    LAST_7D = "7d"
    LAST_30D = "30d"
    LAST_90D = "90d"
    CUSTOM = "custom"


class RefreshInterval(Enum):
    """Dashboard refresh intervals"""
    REALTIME = 1      # 1 second
    FAST = 5          # 5 seconds
    NORMAL = 30       # 30 seconds
    SLOW = 60         # 1 minute
    MANUAL = 0        # Manual refresh only


class AggregationType(Enum):
    """Data aggregation types"""
    NONE = "none"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    P95 = "p95"
    P99 = "p99"
    STDDEV = "stddev"
    RATE = "rate"
    INCREASE = "increase"


class DashboardLayout(Enum):
    """Dashboard layout types"""
    GRID = "grid"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    CUSTOM = "custom"
    MASONRY = "masonry"
    TABS = "tabs"
    SPLIT_SCREEN = "split_screen"


class ExportFormat(Enum):
    """Export format options"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    PNG = "png"
    JSON = "json"
    HTML = "html"
    POWERPOINT = "powerpoint"


@dataclass
class ChartConfiguration:
    """Enhanced chart configuration with business intelligence"""
    title: str
    chart_type: ChartType
    data_source: str
    time_range: TimeRange
    refresh_interval: RefreshInterval
    aggregation: AggregationType = AggregationType.AVG
    filters: Dict[str, Any] = field(default_factory=dict)
    styling: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    ml_insights_enabled: bool = False
    real_time_enabled: bool = True
    export_enabled: bool = True
    drill_down_enabled: bool = False
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    height: int = 400
    width: Optional[int] = None
    show_legend: bool = True
    show_grid: bool = True
    tenant_filter: Optional[str] = None
    labels_filter: Optional[Dict[str, str]] = None
    color_scheme: str = "plotly"
    interactive_features: List[str] = field(default_factory=list)


@dataclass
class DashboardLayout:
    """Dashboard layout configuration"""
    rows: int
    columns: int
    grid_size: Tuple[int, int] = (1200, 800)
    responsive: bool = True
    theme: str = "light"
    background_color: str = "#ffffff"
    text_color: str = "#333333"
    accent_color: str = "#007bff"
    layout_type: DashboardLayout = DashboardLayout.GRID


@dataclass
class DashboardWidget:
    """Enhanced dashboard widget with business intelligence"""
    id: str
    title: str
    chart_config: ChartConfiguration
    position: Dict[str, int]  # x, y, width, height
    tenant_id: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    business_priority: str = "normal"  # low, normal, high, critical
    cost_center: Optional[str] = None
    data_retention_days: int = 90
    cache_enabled: bool = True
    notifications_enabled: bool = False


@dataclass
class DashboardConfig:
    """Comprehensive dashboard configuration"""
    id: str
    title: str
    description: str
    layout: DashboardLayout
    widgets: List[DashboardWidget]
    tenant_id: Optional[str] = None
    owner_id: str = ""
    shared_with: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    auto_refresh: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    business_category: str = "operational"  # operational, strategic, executive
    compliance_level: str = "standard"  # standard, sensitive, confidential
    refresh_interval: int = 30
    is_public: bool = False
    version: str = "1.0.0"
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None


class MetricsDashboard:
    """
    Enterprise metrics dashboard with advanced visualization and BI
    
    Features:
    - Real-time interactive dashboards with WebSocket updates
    - Advanced business intelligence with predictive analytics
    - Multi-tenant security with granular permissions
    - Customizable drag-and-drop interface
    - Export capabilities with multiple formats
    - Mobile-responsive design with offline support
    - Advanced filtering and correlation analysis
    - ML-powered insights and recommendations
    - Advanced charting with 20+ chart types
    - Business intelligence and forecasting
    - Anomaly detection with automated alerts
    - Performance optimization with caching
    - Multi-language support and accessibility
    """
    
    def __init__(self, config: Optional[MetricsConfiguration] = None):
        self.config = config or get_metrics_config()
        self.logger = logger
        
        # Enhanced components
        self.redis_manager = RedisManager()
        self.security_manager = SecurityManager()
        
        # Dashboard management
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.active_connections: Dict[str, List[Any]] = {}  # WebSocket connections
        self.widget_cache: Dict[str, Any] = {}
        
        # Real-time updates
        self._update_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        
        # Business intelligence
        self.bi_engine = self._initialize_bi_engine()
        self.chart_templates = self._initialize_chart_templates()
        
        # Performance optimization
        self.data_cache: Dict[str, Any] = {}
        self.cache_ttl = 30  # seconds
        
        # Visualization engines
        self.plot_engine = self._initialize_plot_engine()
        self.export_engine = self._initialize_export_engine()
        
        # ML models for insights
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.clustering_model = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        
        # Business intelligence metrics
        self.business_metrics = {
            "revenue_per_user": 0,
            "customer_acquisition_cost": 0,
            "customer_lifetime_value": 0,
            "churn_rate": 0,
            "engagement_score": 0
        }
        
        # Dashboard components
        self.metrics_collector = MetricsCollector()
        self.performance_analytics = PerformanceAnalytics()
        self.alert_manager = AlertManager()
        
        # Initialize default dashboards
        self._initialize_default_dashboards()
    
    async def start(self) -> None:
        """Start dashboard engine with real-time capabilities"""
        try:
            if self._running:
                self.logger.warning("Dashboard engine already running")
                return
            
            self._running = True
            
            # Initialize security
            await self.security_manager.initialize()
            
            # Start real-time update tasks
            self._update_tasks["real_time_updater"] = asyncio.create_task(
                self._real_time_update_loop()
            )
            
            self._update_tasks["cache_manager"] = asyncio.create_task(
                self._cache_management_loop()
            )
            
            self._update_tasks["bi_analyzer"] = asyncio.create_task(
                self._business_intelligence_loop()
            )
            
            self._update_tasks["anomaly_detector"] = asyncio.create_task(
                self._anomaly_detection_loop()
            )
            
            self.logger.info("Advanced Metrics Dashboard Engine started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting dashboard engine: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop dashboard engine gracefully"""
        try:
            self._running = False
            
            # Stop all update tasks
            for task_name, task in self._update_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Close active WebSocket connections
            for dashboard_id, connections in self.active_connections.items():
                for connection in connections:
                    try:
                        await connection.close()
                    except Exception as e:
                        self.logger.error(f"Error closing connection: {e}")
            
            # Save dashboard configurations
            await self._save_dashboard_configurations()
            
            self.logger.info("Metrics Dashboard Engine stopped gracefully")
            
        except Exception as e:
            self.logger.error(f"Error stopping dashboard engine: {e}")
    
    async def create_dashboard(
        self,
        title: str,
        description: str,
        layout: DashboardLayout,
        widgets: List[DashboardWidget],
        tenant_id: Optional[str] = None,
        owner_id: str = "",
        business_category: str = "operational"
    ) -> str:
        """Create new comprehensive dashboard"""
        try:
            # Generate unique dashboard ID
            dashboard_id = str(uuid.uuid4())
            
            # Validate dashboard configuration
            await self._validate_dashboard_config(widgets, tenant_id)
            
            # Apply security policies
            await self._apply_dashboard_security(widgets, tenant_id, owner_id)
            
            # Create dashboard configuration
            dashboard_config = DashboardConfig(
                id=dashboard_id,
                title=title,
                description=description,
                layout=layout,
                widgets=widgets,
                tenant_id=tenant_id,
                owner_id=owner_id,
                business_category=business_category
            )
            
            # Store dashboard
            self.dashboards[dashboard_id] = dashboard_config
            
            # Cache dashboard for performance
            await self._cache_dashboard_config(dashboard_id, dashboard_config)
            
            # Initialize real-time updates if needed
            if any(w.chart_config.real_time_enabled for w in widgets):
                await self._initialize_real_time_updates(dashboard_id)
            
            self.logger.info(f"Dashboard created: {title} (ID: {dashboard_id})")
            return dashboard_id
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            raise
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[DashboardConfig]:
        """Get dashboard configuration with enhanced caching"""
        try:
            if dashboard_id in self.dashboards:
                return self.dashboards[dashboard_id]
            
            # Try to load from Redis
            config = await self._load_dashboard_config(dashboard_id)
            if config:
                self.dashboards[dashboard_id] = config
                return config
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard: {e}")
            return None
    
    async def get_dashboard_data(
        self,
        dashboard_id: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        real_time: bool = False
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data with business intelligence"""
        try:
            dashboard_config = await self.get_dashboard(dashboard_id)
            if not dashboard_config:
                return {"error": "Dashboard not found"}
            
            # Validate access permissions
            if not await self._validate_dashboard_access(dashboard_config, tenant_id, user_id):
                return {"error": "Access denied"}
            
            # Get widget data with caching
            widget_data = {}
            for widget in dashboard_config.widgets:
                try:
                    # Check cache first
                    cache_key = f"widget:{widget.id}:{tenant_id}"
                    cached_data = await self._get_cached_widget_data(cache_key)
                    
                    if cached_data and not real_time:
                        widget_data[widget.id] = cached_data
                    else:
                        # Generate fresh data
                        data = await self._generate_widget_data(widget, tenant_id)
                        
                        # Add ML insights if enabled
                        if widget.chart_config.ml_insights_enabled:
                            data["ml_insights"] = await self._generate_ml_insights(widget, data)
                        
                        # Add business context
                        data["business_context"] = await self._add_business_context(widget, data)
                        
                        # Add anomaly detection
                        data["anomalies"] = await self._detect_anomalies_in_data(data)
                        
                        widget_data[widget.id] = data
                        
                        # Cache the data
                        await self._cache_widget_data(cache_key, data)
                        
                except Exception as e:
                    self.logger.error(f"Error getting data for widget {widget.id}: {e}")
                    widget_data[widget.id] = {"error": str(e)}
            
            # Generate dashboard-level insights
            dashboard_insights = await self._generate_dashboard_insights(
                dashboard_config, widget_data
            )
            
            # Add business metrics
            business_metrics = await self._calculate_business_metrics(widget_data, tenant_id)
            
            return {
                "dashboard_id": dashboard_id,
                "title": dashboard_config.title,
                "description": dashboard_config.description,
                "layout": dashboard_config.layout,
                "widgets": widget_data,
                "insights": dashboard_insights,
                "business_metrics": business_metrics,
                "last_updated": datetime.utcnow().isoformat(),
                "real_time_enabled": real_time,
                "business_category": dashboard_config.business_category,
                "performance_score": await self._calculate_dashboard_performance_score(widget_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e)}
    
    async def render_dashboard(
        self,
        dashboard_id: str,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """Render complete dashboard with all charts"""
        try:
            config = await self.get_dashboard(dashboard_id)
            if not config:
                raise ValueError(f"Dashboard not found: {dashboard_id}")
            
            dashboard_data = {
                "id": dashboard_id,
                "title": config.title,
                "description": config.description,
                "layout": config.layout.layout_type.value if hasattr(config.layout, 'layout_type') else config.layout,
                "refresh_interval": config.refresh_interval,
                "tenant_id": config.tenant_id,
                "charts": [],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "chart_count": len(config.widgets),
                    "version": config.version,
                    "business_category": config.business_category
                }
            }
            
            # Render each widget
            for i, widget in enumerate(config.widgets):
                try:
                    # Use provided time range or widget default
                    widget_time_range = time_range or widget.chart_config.time_range.value
                    
                    chart_data = await self.render_chart(
                        widget.chart_config,
                        widget_time_range,
                        f"chart_{i}"
                    )
                    
                    # Add widget-specific metadata
                    chart_data["widget_metadata"] = {
                        "business_priority": widget.business_priority,
                        "cost_center": widget.cost_center,
                        "tags": widget.tags,
                        "permissions": widget.permissions
                    }
                    
                    dashboard_data["charts"].append(chart_data)
                    
                except Exception as e:
                    self.logger.error(f"Error rendering widget {i}: {e}")
                    # Add error placeholder
                    dashboard_data["charts"].append({
                        "id": f"chart_{i}",
                        "title": widget.chart_config.title,
                        "error": str(e),
                        "chart_type": widget.chart_config.chart_type.value
                    })
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error rendering dashboard: {e}")
            raise
    
    async def render_chart(
        self,
        config: ChartConfiguration,
        time_range: str,
        chart_id: str
    ) -> Dict[str, Any]:
        """Render individual chart with advanced features"""
        try:
            # Get metrics data
            metrics_data = await self._get_chart_metrics_data(config, time_range)
            
            # Generate chart based on type
            if config.chart_type == ChartType.LINE:
                chart_figure = await self._create_line_chart(metrics_data, config)
            elif config.chart_type == ChartType.BAR:
                chart_figure = await self._create_bar_chart(metrics_data, config)
            elif config.chart_type == ChartType.SCATTER:
                chart_figure = await self._create_scatter_chart(metrics_data, config)
            elif config.chart_type == ChartType.HISTOGRAM:
                chart_figure = await self._create_histogram_chart(metrics_data, config)
            elif config.chart_type == ChartType.HEATMAP:
                chart_figure = await self._create_heatmap_chart(metrics_data, config)
            elif config.chart_type == ChartType.GAUGE:
                chart_figure = await self._create_gauge_chart(metrics_data, config)
            elif config.chart_type == ChartType.PIE:
                chart_figure = await self._create_pie_chart(metrics_data, config)
            elif config.chart_type == ChartType.TABLE:
                chart_figure = await self._create_table_chart(metrics_data, config)
            elif config.chart_type == ChartType.CORRELATION_MATRIX:
                chart_figure = await self._create_correlation_matrix(metrics_data, config)
            elif config.chart_type == ChartType.FORECASTING:
                chart_figure = await self._create_forecasting_chart(metrics_data, config)
            elif config.chart_type == ChartType.ANOMALY_DETECTION:
                chart_figure = await self._create_anomaly_detection_chart(metrics_data, config)
            elif config.chart_type == ChartType.BUSINESS_INSIGHTS:
                chart_figure = await self._create_business_insights_chart(metrics_data, config)
            else:
                chart_figure = await self._create_line_chart(metrics_data, config)
            
            # Convert to JSON
            chart_json = chart_figure.to_json() if hasattr(chart_figure, 'to_json') else json.dumps(chart_figure)
            
            # Add ML insights if enabled
            ml_insights = {}
            if config.ml_insights_enabled:
                ml_insights = await self._generate_chart_ml_insights(config, metrics_data)
            
            return {
                "id": chart_id,
                "title": config.title,
                "chart_type": config.chart_type.value,
                "data_source": config.data_source,
                "time_range": time_range,
                "data": chart_json,
                "ml_insights": ml_insights,
                "config": {
                    "height": config.height,
                    "width": config.width,
                    "show_legend": config.show_legend,
                    "show_grid": config.show_grid,
                    "color_scheme": config.color_scheme,
                    "interactive_features": config.interactive_features
                },
                "business_context": config.business_context,
                "alerts": await self._check_chart_alerts(metrics_data, config.alert_thresholds),
                "metadata": {
                    "data_points": len(metrics_data) if isinstance(metrics_data, list) else 0,
                    "generated_at": datetime.utcnow().isoformat(),
                    "aggregation": config.aggregation.value,
                    "real_time_enabled": config.real_time_enabled
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error rendering chart: {e}")
            raise
    
    async def create_dashboard(
        self,
        config: DashboardConfig,
        dashboard_id: Optional[str] = None
    ) -> str:
        """Create new dashboard"""
        try:
            if not dashboard_id:
                dashboard_id = f"dashboard_{len(self.dashboards)}_{int(datetime.utcnow().timestamp())}"
            
            self.dashboards[dashboard_id] = config
            
            # Store in Redis
            await self._store_dashboard_config(dashboard_id, config)
            
            self.logger.info(f"Dashboard created: {config.title} ({dashboard_id})")
            return dashboard_id
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            raise
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[DashboardConfig]:
        """Get dashboard configuration"""
        try:
            if dashboard_id in self.dashboards:
                return self.dashboards[dashboard_id]
            
            # Try to load from Redis
            config = await self._load_dashboard_config(dashboard_id)
            if config:
                self.dashboards[dashboard_id] = config
                return config
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard: {e}")
            return None
    
    async def render_dashboard(
        self,
        dashboard_id: str,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """Render complete dashboard with all charts"""
        try:
            config = await self.get_dashboard(dashboard_id)
            if not config:
                raise ValueError(f"Dashboard not found: {dashboard_id}")
            
            dashboard_data = {
                "id": dashboard_id,
                "title": config.title,
                "description": config.description,
                "layout": config.layout.value,
                "refresh_interval": config.refresh_interval,
                "tenant_id": config.tenant_id,
                "charts": [],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "chart_count": len(config.charts)
                }
            }
            
            # Render each chart
            for i, chart_config in enumerate(config.charts):
                try:
                    # Use provided time range or chart default
                    chart_time_range = time_range or chart_config.time_range
                    
                    chart_data = await self.render_chart(
                        chart_config,
                        chart_time_range,
                        f"chart_{i}"
                    )
                    
                    dashboard_data["charts"].append(chart_data)
                    
                except Exception as e:
                    self.logger.error(f"Error rendering chart {i}: {e}")
                    # Add error placeholder
                    dashboard_data["charts"].append({
                        "id": f"chart_{i}",
                        "title": chart_config.title,
                        "error": str(e),
                        "chart_type": chart_config.chart_type.value
                    })
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error rendering dashboard: {e}")
            raise
    
    async def render_chart(
        self,
        config: ChartConfig,
        time_range: str,
        chart_id: str
    ) -> Dict[str, Any]:
        """Render individual chart"""
        try:
            # Get metrics data
            metrics_data = await self._get_chart_metrics_data(config, time_range)
            
            # Generate chart based on type
            if config.chart_type == ChartType.LINE:
                chart_figure = self._create_line_chart(metrics_data, config)
            elif config.chart_type == ChartType.BAR:
                chart_figure = self._create_bar_chart(metrics_data, config)
            elif config.chart_type == ChartType.SCATTER:
                chart_figure = self._create_scatter_chart(metrics_data, config)
            elif config.chart_type == ChartType.HISTOGRAM:
                chart_figure = self._create_histogram_chart(metrics_data, config)
            elif config.chart_type == ChartType.HEATMAP:
                chart_figure = self._create_heatmap_chart(metrics_data, config)
            elif config.chart_type == ChartType.GAUGE:
                chart_figure = self._create_gauge_chart(metrics_data, config)
            elif config.chart_type == ChartType.PIE:
                chart_figure = self._create_pie_chart(metrics_data, config)
            elif config.chart_type == ChartType.TABLE:
                chart_figure = self._create_table_chart(metrics_data, config)
            else:
                raise ValueError(f"Unsupported chart type: {config.chart_type}")
            
            # Convert to JSON
            chart_json = chart_figure.to_json() if hasattr(chart_figure, 'to_json') else json.dumps(chart_figure)
            
            return {
                "id": chart_id,
                "title": config.title,
                "chart_type": config.chart_type.value,
                "metric_name": config.metric_name,
                "time_range": time_range,
                "data": chart_json,
                "config": {
                    "height": config.height,
                    "width": config.width,
                    "show_legend": config.show_legend,
                    "show_grid": config.show_grid
                },
                "metadata": {
                    "data_points": len(metrics_data) if isinstance(metrics_data, list) else 0,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error rendering chart: {e}")
            raise
    
    async def get_real_time_data(
        self,
        metric_name: str,
        tenant_id: Optional[str] = None,
        time_range: str = "5m"
    ) -> Dict[str, Any]:
        """Get real-time metrics data for live updates"""
        try:
            # Parse time range
            minutes = int(time_range.replace('m', '').replace('h', '')) 
            if 'h' in time_range:
                minutes *= 60
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=minutes)
            
            # Get data from Redis
            data_points = []
            current_time = start_time
            
            while current_time <= end_time:
                timestamp_key = current_time.strftime("%Y%m%d%H%M")
                
                if tenant_id:
                    key = f"metrics:tenant:{tenant_id}:{metric_name}:{timestamp_key}"
                else:
                    key = f"metrics:global:{metric_name}:{timestamp_key}"
                
                data = await self.redis_manager.lrange(key, 0, -1)
                
                for item in data:
                    try:
                        metric_data = json.loads(item)
                        timestamp = datetime.fromisoformat(metric_data["timestamp"])
                        
                        if start_time <= timestamp <= end_time:
                            data_points.append({
                                "timestamp": timestamp.isoformat(),
                                "value": metric_data["value"],
                                "labels": metric_data.get("labels", {}),
                                "metadata": metric_data.get("metadata", {})
                            })
                    except Exception as e:
                        self.logger.error(f"Error parsing metric data: {e}")
                
                current_time += timedelta(minutes=1)
            
            # Sort by timestamp
            data_points.sort(key=lambda x: x["timestamp"])
            
            return {
                "metric_name": metric_name,
                "tenant_id": tenant_id,
                "time_range": time_range,
                "data_points": data_points,
                "metadata": {
                    "count": len(data_points),
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time data: {e}")
            return {}
    
    async def get_alert_dashboard_data(
        self,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get alert dashboard data"""
        try:
            # Get active alerts
            if tenant_id:
                alerts = await self.alert_manager.get_tenant_alerts(tenant_id)
            else:
                # Get all alerts (admin view)
                alerts = []  # Implementation would aggregate all tenant alerts
            
            # Get alert metrics
            alert_metrics = await self.alert_manager.get_alert_metrics(tenant_id)
            
            # Prepare dashboard data
            alert_dashboard = {
                "tenant_id": tenant_id,
                "active_alerts": [
                    {
                        "id": alert.id,
                        "rule_name": alert.rule_name,
                        "severity": alert.severity.value,
                        "state": alert.state.value,
                        "triggered_at": alert.triggered_at.isoformat(),
                        "metric_value": alert.metric_value,
                        "context": alert.context
                    }
                    for alert in alerts if alert.state.value in ["firing", "pending"]
                ],
                "alert_metrics": alert_metrics,
                "summary": {
                    "total_active_alerts": len([a for a in alerts if a.state.value in ["firing", "pending"]]),
                    "critical_alerts": len([a for a in alerts if a.severity.value == "critical" and a.state.value == "firing"]),
                    "warning_alerts": len([a for a in alerts if a.severity.value == "warning" and a.state.value == "firing"])
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return alert_dashboard
            
        except Exception as e:
            self.logger.error(f"Error getting alert dashboard data: {e}")
            return {}
    
    async def export_dashboard(
        self,
        dashboard_id: str,
        export_format: str = "json",
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export dashboard data"""
        try:
            dashboard_data = await self.render_dashboard(dashboard_id, time_range)
            
            if export_format == "json":
                return dashboard_data
            elif export_format == "csv":
                return self._export_dashboard_csv(dashboard_data)
            elif export_format == "pdf":
                return self._export_dashboard_pdf(dashboard_data)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
                
        except Exception as e:
            self.logger.error(f"Error exporting dashboard: {e}")
            raise
    
    def _create_line_chart(self, data: List[Dict], config: ChartConfig) -> go.Figure:
        """Create line chart"""
        try:
            df = pd.DataFrame(data)
            
            if df.empty:
                return self._create_empty_chart(config.title)
            
            fig = go.Figure()
            
            # Group by labels if present
            if 'labels' in df.columns and any(df['labels']):
                unique_labels = df['labels'].apply(lambda x: str(x)).unique()
                for label in unique_labels:
                    label_data = df[df['labels'].apply(lambda x: str(x)) == label]
                    fig.add_trace(go.Scatter(
                        x=label_data['timestamp'],
                        y=label_data['value'],
                        mode='lines+markers',
                        name=label,
                        line=dict(width=2)
                    ))
            else:
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['value'],
                    mode='lines+markers',
                    name=config.metric_name,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title="Time",
                yaxis_title="Value",
                height=config.height,
                showlegend=config.show_legend,
                template="plotly_white"
            )
            
            if config.show_grid:
                fig.update_xaxes(showgrid=True)
                fig.update_yaxes(showgrid=True)
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating line chart: {e}")
            return self._create_empty_chart(config.title)
    
    def _create_bar_chart(self, data: List[Dict], config: ChartConfig) -> go.Figure:
        """Create bar chart"""
        try:
            df = pd.DataFrame(data)
            
            if df.empty:
                return self._create_empty_chart(config.title)
            
            # Aggregate data for bar chart
            if 'labels' in df.columns:
                # Group by labels
                aggregated = df.groupby('labels')['value'].agg(config.aggregation).reset_index()
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=[str(label) for label in aggregated['labels']],
                        y=aggregated['value'],
                        name=config.metric_name
                    )
                ])
            else:
                # Simple time-based bars
                df['time_bucket'] = pd.to_datetime(df['timestamp']).dt.floor('5T')  # 5 minute buckets
                aggregated = df.groupby('time_bucket')['value'].agg(config.aggregation).reset_index()
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=aggregated['time_bucket'],
                        y=aggregated['value'],
                        name=config.metric_name
                    )
                ])
            
            fig.update_layout(
                title=config.title,
                xaxis_title="Category",
                yaxis_title="Value",
                height=config.height,
                showlegend=config.show_legend,
                template="plotly_white"
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating bar chart: {e}")
            return self._create_empty_chart(config.title)
    
    def _create_gauge_chart(self, data: List[Dict], config: ChartConfig) -> go.Figure:
        """Create gauge chart"""
        try:
            if not data:
                current_value = 0
            else:
                # Use latest value
                current_value = data[-1]['value']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=current_value,
                title={'text': config.title},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=config.height)
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating gauge chart: {e}")
            return self._create_empty_chart(config.title)
    
    def _create_pie_chart(self, data: List[Dict], config: ChartConfig) -> go.Figure:
        """Create pie chart"""
        try:
            df = pd.DataFrame(data)
            
            if df.empty:
                return self._create_empty_chart(config.title)
            
            # Aggregate by labels
            if 'labels' in df.columns:
                aggregated = df.groupby('labels')['value'].sum().reset_index()
                
                fig = go.Figure(data=[go.Pie(
                    labels=[str(label) for label in aggregated['labels']],
                    values=aggregated['value'],
                    hole=.3
                )])
            else:
                # Default pie chart
                return self._create_empty_chart(config.title)
            
            fig.update_layout(
                title=config.title,
                height=config.height,
                showlegend=config.show_legend
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating pie chart: {e}")
            return self._create_empty_chart(config.title)
    
    def _create_table_chart(self, data: List[Dict], config: ChartConfig) -> Dict[str, Any]:
        """Create table chart"""
        try:
            df = pd.DataFrame(data)
            
            if df.empty:
                return {
                    "type": "table",
                    "title": config.title,
                    "headers": [],
                    "rows": [],
                    "message": "No data available"
                }
            
            # Format data for table
            table_data = {
                "type": "table",
                "title": config.title,
                "headers": list(df.columns),
                "rows": df.values.tolist(),
                "row_count": len(df)
            }
            
            return table_data
            
        except Exception as e:
            self.logger.error(f"Error creating table chart: {e}")
            return {
                "type": "table",
                "title": config.title,
                "headers": [],
                "rows": [],
                "error": str(e)
            }
    
    def _create_empty_chart(self, title: str) -> go.Figure:
        """Create empty chart placeholder"""
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            template="plotly_white",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        return fig
    
    async def _get_chart_metrics_data(
        self,
        config: ChartConfig,
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Get metrics data for chart"""
        try:
            return await self.get_real_time_data(
                config.metric_name,
                config.tenant_filter,
                time_range
            ).get("data_points", [])
            
        except Exception as e:
            self.logger.error(f"Error getting chart metrics data: {e}")
            return []
    
    async def _store_dashboard_config(
        self,
        dashboard_id: str,
        config: DashboardConfig
    ) -> None:
        """Store dashboard configuration in Redis"""
        try:
            config_data = {
                "title": config.title,
                "description": config.description,
                "layout": config.layout.value,
                "charts": [
                    {
                        "title": chart.title,
                        "chart_type": chart.chart_type.value,
                        "metric_name": chart.metric_name,
                        "time_range": chart.time_range,
                        "refresh_interval": chart.refresh_interval,
                        "tenant_filter": chart.tenant_filter,
                        "labels_filter": chart.labels_filter,
                        "aggregation": chart.aggregation,
                        "show_legend": chart.show_legend,
                        "show_grid": chart.show_grid,
                        "height": chart.height,
                        "width": chart.width
                    }
                    for chart in config.charts
                ],
                "refresh_interval": config.refresh_interval,
                "tenant_id": config.tenant_id,
                "is_public": config.is_public,
                "created_by": config.created_by,
                "tags": config.tags,
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.redis_manager.set_json(
                f"dashboard_config:{dashboard_id}",
                config_data,
                expire=86400  # 24 hours
            )
            
        except Exception as e:
            self.logger.error(f"Error storing dashboard config: {e}")
    
    async def _load_dashboard_config(self, dashboard_id: str) -> Optional[DashboardConfig]:
        """Load dashboard configuration from Redis"""
        try:
            config_data = await self.redis_manager.get_json(f"dashboard_config:{dashboard_id}")
            
            if not config_data:
                return None
            
            # Reconstruct config object
            charts = [
                ChartConfig(
                    title=chart_data["title"],
                    chart_type=ChartType(chart_data["chart_type"]),
                    metric_name=chart_data["metric_name"],
                    time_range=chart_data.get("time_range", "1h"),
                    refresh_interval=chart_data.get("refresh_interval", 30),
                    tenant_filter=chart_data.get("tenant_filter"),
                    labels_filter=chart_data.get("labels_filter"),
                    aggregation=chart_data.get("aggregation", "avg"),
                    show_legend=chart_data.get("show_legend", True),
                    show_grid=chart_data.get("show_grid", True),
                    height=chart_data.get("height", 400),
                    width=chart_data.get("width")
                )
                for chart_data in config_data.get("charts", [])
            ]
            
            config = DashboardConfig(
                title=config_data["title"],
                description=config_data["description"],
                layout=DashboardLayout(config_data.get("layout", "grid")),
                charts=charts,
                refresh_interval=config_data.get("refresh_interval", 30),
                tenant_id=config_data.get("tenant_id"),
                is_public=config_data.get("is_public", False),
                created_by=config_data.get("created_by"),
                tags=config_data.get("tags", [])
            )
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading dashboard config: {e}")
            return None
    
    def _initialize_default_dashboards(self) -> None:
        """Initialize default dashboards"""
        # Application Overview Dashboard
        app_overview = DashboardConfig(
            title="Application Overview",
            description="High-level application performance metrics",
            layout=DashboardLayout.GRID,
            charts=[
                ChartConfig(
                    title="HTTP Request Rate",
                    chart_type=ChartType.LINE,
                    metric_name="http_requests_total",
                    time_range="1h"
                ),
                ChartConfig(
                    title="Response Time",
                    chart_type=ChartType.LINE,
                    metric_name="http_request_duration_seconds",
                    time_range="1h"
                ),
                ChartConfig(
                    title="Error Rate",
                    chart_type=ChartType.GAUGE,
                    metric_name="http_errors_total",
                    time_range="1h"
                ),
                ChartConfig(
                    title="Active Users",
                    chart_type=ChartType.BAR,
                    metric_name="active_users_current",
                    time_range="24h"
                )
            ],
            tags=["default", "application", "overview"]
        )
        
        self.dashboards["app_overview"] = app_overview
        
        # Infrastructure Dashboard
        infra_dashboard = DashboardConfig(
            title="Infrastructure Monitoring",
            description="System resources and infrastructure metrics",
            layout=DashboardLayout.GRID,
            charts=[
                ChartConfig(
                    title="CPU Usage",
                    chart_type=ChartType.LINE,
                    metric_name="system_cpu_percent",
                    time_range="1h"
                ),
                ChartConfig(
                    title="Memory Usage",
                    chart_type=ChartType.LINE,
                    metric_name="system_memory_bytes",
                    time_range="1h"
                ),
                ChartConfig(
                    title="Database Connections",
                    chart_type=ChartType.GAUGE,
                    metric_name="database_connections_active",
                    time_range="1h"
                ),
                ChartConfig(
                    title="Cache Hit Rate",
                    chart_type=ChartType.GAUGE,
                    metric_name="cache_hit_rate",
                    time_range="1h"
                )
            ],
            tags=["default", "infrastructure", "monitoring"]
        )
        
        self.dashboards["infrastructure"] = infra_dashboard
