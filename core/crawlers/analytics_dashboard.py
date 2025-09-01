"""Advanced Analytics Dashboard - Ultra-Advanced Implementation
AI-Powered Analytics and Real-Time Dashboard System

This module provides comprehensive analytics dashboard with real-time visualizations,
advanced metrics, AI-powered insights, and interactive reporting capabilities.
"""

import asyncio
import aiohttp
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import hashlib
import uuid
import statistics
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import threading
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import sqlite3
import redis
from sqlalchemy import create_engine, text

from .base import BaseCrawler
from ..utils.rate_limiter import RateLimiter
from ..utils.cache import CacheManager
from ..utils.encryption import ContentEncryption

logger = logging.getLogger(__name__)


class ChartType(str, Enum):
    """
Types of charts"""

    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    GAUGE_CHART = "gauge_chart"
    TREEMAP = "treemap"
    SANKEY_DIAGRAM = "sankey_diagram"
    FUNNEL_CHART = "funnel_chart"
    WATERFALL_CHART = "waterfall_chart"


class MetricCategory(str, Enum):
    """Metric categories"""

    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    CONTENT = "content"
    AUDIENCE = "audience"
    REVENUE = "revenue"
    GROWTH = "growth"
    QUALITY = "quality"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"


class DashboardTheme(str, Enum):
    """Dashboard themes"""

    LIGHT = "light"
    DARK = "dark"
    CORPORATE = "corporate"
    MODERN = "modern"
    MINIMAL = "minimal"


class VisualizationType(str, Enum):
    """Visualization types"""

    REAL_TIME = "real_time"
    HISTORICAL = "historical"
    COMPARATIVE = "comparative"
    PREDICTIVE = "predictive"
    INTERACTIVE = "interactive"
    STATIC = "static"


class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    widget_id: str
    widget_type: str
    title: str
    description: str = ""
    
    # Chart configuration
    chart_type: ChartType
    metric_category: MetricCategory
    data_source: str
    
    # Layout
    position: Dict[str, int] = Field(default_factory=dict)  # x, y, width, height
    size: str = "medium"  # "small", "medium", "large", "extra_large"
    
    # Data configuration
    metrics: List[str] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)
    time_range: str = "24h"  # "1h", "24h", "7d", "30d", "90d", "1y"
    
    # Visualization settings
    visualization_type: VisualizationType = VisualizationType.REAL_TIME
    update_interval: int = 30  # seconds
    auto_refresh: bool = True
    
    # Styling
    theme: DashboardTheme = DashboardTheme.MODERN
    color_scheme: List[str] = Field(default_factory=list)
    
    # Interactions
    interactive: bool = True
    drill_down_enabled: bool = False
    export_enabled: bool = True
    
    # Alerts
    alert_enabled: bool = False
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: str = "system"
    tags: List[str] = Field(default_factory=list)


class DashboardLayout(BaseModel):
    """Dashboard layout configuration"""
    layout_id: str
    name: str
    description: str = ""
    
    # Layout properties
    grid_columns: int = 12
    grid_rows: int = 20
    responsive: bool = True
    
    # Widgets
    widgets: List[DashboardWidget] = Field(default_factory=list)
    
    # Theme and styling
    theme: DashboardTheme = DashboardTheme.MODERN
    background_color: str = "#ffffff"
    primary_color: str = "#007bff"
    
    # Access control
    public: bool = False
    allowed_users: List[str] = Field(default_factory=list)
    allowed_roles: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: str = "system"
    version: str = "1.0"


class AnalyticsMetric(BaseModel):
    """Analytics metric definition"""
    metric_id: str
    name: str
    description: str
    category: MetricCategory
    
    # Calculation
    calculation_method: str = "sum"  # "sum", "avg", "count", "min", "max", "custom"
    source_table: str
    source_column: str
    
    # Filters and grouping
    default_filters: Dict[str, Any] = Field(default_factory=dict)
    groupby_fields: List[str] = Field(default_factory=list)
    
    # Formatting
    data_type: str = "number"  # "number", "percentage", "currency", "duration"
    format_string: str = "{:.2f}"
    unit: str = ""
    
    # Aggregation levels
    time_aggregation: List[str] = Field(default_factory=lambda: ["hour", "day", "week", "month"])
    
    # Metadata
    created_at: datetime
    active: bool = True
    tags: List[str] = Field(default_factory=list)


class AnalyticsReport(BaseModel):
    """Analytics report"""
    report_id: str
    name: str
    description: str = ""
    
    # Report configuration
    report_type: str = "scheduled"  # "scheduled", "on_demand", "alert_based"
    schedule: str = "daily"  # "hourly", "daily", "weekly", "monthly"
    
    # Content
    metrics: List[str] = Field(default_factory=list)
    charts: List[str] = Field(default_factory=list)
    time_range: str = "7d"
    
    # Format and delivery
    output_format: str = "pdf"  # "pdf", "html", "json", "csv"
    delivery_method: str = "email"  # "email", "slack", "webhook"
    recipients: List[str] = Field(default_factory=list)
    
    # Generation
    template: str = "standard"
    include_insights: bool = True
    include_recommendations: bool = True
    
    # Status
    last_generated: Optional[datetime] = None
    next_generation: Optional[datetime] = None
    status: str = "active"  # "active", "paused", "error"
    
    # Metadata
    created_at: datetime
    created_by: str = "system"


class DataVisualization(BaseModel):
    """Data visualization configuration"""
    visualization_id: str
    name: str
    description: str = ""
    
    # Chart configuration
    chart_type: ChartType
    data_query: str
    
    # Styling
    title: str
    subtitle: str = ""
    x_axis_title: str = ""
    y_axis_title: str = ""
    
    # Colors and themes
    color_palette: List[str] = Field(default_factory=list)
    theme: DashboardTheme = DashboardTheme.MODERN
    
    # Interactions
    interactive: bool = True
    zoom_enabled: bool = True
    pan_enabled: bool = True
    hover_enabled: bool = True
    
    # Annotations
    annotations: List[Dict[str, Any]] = Field(default_factory=list)
    watermark: str = ""
    
    # Export options
    export_formats: List[str] = Field(default_factory=lambda: ["png", "svg", "pdf"])
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    tags: List[str] = Field(default_factory=list)


class DashboardInsight(BaseModel):
    """AI-generated dashboard insight"""
    insight_id: str
    title: str
    description: str
    category: str = "general"
    
    # Insight type
    insight_type: str = "trend"  # "trend", "anomaly", "correlation", "prediction"
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str = "info"  # "info", "warning", "critical"
    
    # Related data
    metrics_involved: List[str] = Field(default_factory=list)
    time_period: str
    
    # Evidence
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    chart_references: List[str] = Field(default_factory=list)
    
    # Actions
    recommended_actions: List[str] = Field(default_factory=list)
    impact_assessment: str = ""
    
    # Status
    status: str = "new"  # "new", "reviewed", "acted_upon", "dismissed"
    created_at: datetime
    expires_at: Optional[datetime] = None


class AdvancedAnalyticsDashboard(BaseCrawler):
    """
    Ultra-Advanced Analytics Dashboard
    
    Provides comprehensive analytics dashboard with real-time visualizations,
    AI-powered insights, interactive reporting, and advanced data exploration.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Dashboard configuration
        self.dashboard_enabled = config.get('dashboard_enabled', True)
        self.real_time_updates = config.get('real_time_updates', True)
        self.ai_insights_enabled = config.get('ai_insights_enabled', True)
        self.auto_report_generation = config.get('auto_report_generation', True)
        
        # Server configuration
        self.dashboard_host = config.get('dashboard_host', '0.0.0.0')
        self.dashboard_port = config.get('dashboard_port', 8050)
        self.external_access = config.get('external_access', False)
        
        # Data sources
        self.primary_database = config.get('primary_database', 'sqlite:///analytics.db')
        self.redis_host = config.get('redis_host', 'localhost')
        self.redis_port = config.get('redis_port', 6379)
        self.redis_db = config.get('redis_db', 0)
        
        # Storage
        self.dashboard_layouts = {}
        self.analytics_metrics = {}
        self.active_reports = {}
        self.visualizations = {}
        self.dashboard_insights = deque(maxlen=1000)
        
        # Cache for dashboard data
        self.data_cache = {}
        self.cache_ttl = config.get('cache_ttl', 300)  # 5 minutes
        
        # Real-time data
        self.real_time_data = defaultdict(deque)
        self.max_real_time_points = config.get('max_real_time_points', 1000)
        
        # AI service endpoints
        self.insights_endpoint = config.get('insights_endpoint')
        self.recommendation_endpoint = config.get('recommendation_endpoint')
        self.anomaly_detection_endpoint = config.get('anomaly_detection_endpoint')
        
        # Dashboard themes and styling
        self.available_themes = {
            DashboardTheme.LIGHT: {
                'background': '#ffffff',
                'paper': '#f8f9fa',
                'text': '#212529',
                'primary': '#007bff'
            },
            DashboardTheme.DARK: {
                'background': '#1a1a1a',
                'paper': '#2d2d2d',
                'text': '#ffffff',
                'primary': '#0d6efd'
            },
            DashboardTheme.CORPORATE: {
                'background': '#f5f5f5',
                'paper': '#ffffff',
                'text': '#333333',
                'primary': '#004085'
            }
        }
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.get('requests_per_minute', 300),
            requests_per_hour=config.get('requests_per_hour', 10000),
            burst_limit=config.get('burst_limit', 100)
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=self.cache_ttl,
            max_cache_size=config.get('max_cache_size', 50000)
        )
        
        # Content encryption
        self.content_encryption = ContentEncryption()
        
        # Database connections
        self.db_engine = None
        self.redis_client = None
        
        # Dash application
        self.dash_app = None
        self.dashboard_server = None
        
        # Update tasks
        self.update_tasks = []
        self.dashboard_active = False
        
        # Predefined metric categories
        self.metric_definitions = self._initialize_metric_definitions()
        
        # Chart templates
        self.chart_templates = self._initialize_chart_templates()
        
        logger.info("Advanced Analytics Dashboard initialized with AI-powered insights")

    async def initialize_dashboard(self):
        """Initialize dashboard components"""
        try:
            # Initialize database connections
            await self._initialize_database()
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Create default metrics
            await self._create_default_metrics()
            
            # Create default dashboard layouts
            await self._create_default_layouts()
            
            # Initialize Dash application
            await self._initialize_dash_app()
            
            logger.info("Analytics dashboard initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing dashboard: {str(e)}")

    async def start_dashboard_server(self):
        """Start dashboard server"""
        try:
            if not self.dashboard_enabled:
                return
            
            self.dashboard_active = True
            
            # Start update tasks
            real_time_task = asyncio.create_task(self._real_time_update_loop())
            insights_task = asyncio.create_task(self._insights_generation_loop())
            report_task = asyncio.create_task(self._report_generation_loop())
            
            self.update_tasks = [real_time_task, insights_task, report_task]
            
            # Start Dash server in thread
            if self.dash_app:
                dashboard_thread = threading.Thread(
                    target=self._run_dash_server,
                    daemon=True
                )
                dashboard_thread.start()
            
            logger.info(f"Dashboard server started on http://{self.dashboard_host}:{self.dashboard_port}")
            
        except Exception as e:
            logger.error(f"Error starting dashboard server: {str(e)}")

    async def stop_dashboard_server(self):
        """Stop dashboard server"""
        try:
            self.dashboard_active = False
            
            # Cancel update tasks
            for task in self.update_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.update_tasks, return_exceptions=True)
            self.update_tasks = []
            
            logger.info("Dashboard server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping dashboard server: {str(e)}")

    async def create_dashboard_layout(
        self,
        name: str,
        description: str = "",
        widgets: List[Dict[str, Any]] = None
    ) -> DashboardLayout:
        """
        Create new dashboard layout
        
        Args:
            name: Layout name
            description: Layout description
            widgets: Widget configurations
            
        Returns:
            DashboardLayout: Created dashboard layout
        """
        try:
            layout_id = str(uuid.uuid4())
            
            # Create widgets
            dashboard_widgets = []
            if widgets:
                for widget_config in widgets:
                    widget = DashboardWidget(
                        widget_id=str(uuid.uuid4()),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        **widget_config
                    )
                    dashboard_widgets.append(widget)
            
            # Create layout
            layout = DashboardLayout(
                layout_id=layout_id,
                name=name,
                description=description,
                widgets=dashboard_widgets,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store layout
            self.dashboard_layouts[layout_id] = layout
            
            # Cache layout data
            await self.cache_manager.set(
                f"dashboard_layout:{layout_id}",
                layout.dict(),
                ttl=self.cache_ttl * 10  # Longer TTL for layouts
            )
            
            logger.info(f"Created dashboard layout: {name}")
            return layout
            
        except Exception as e:
            logger.error(f"Error creating dashboard layout: {str(e)}")
            return None

    async def add_widget_to_layout(
        self,
        layout_id: str,
        widget_config: Dict[str, Any]
    ) -> DashboardWidget:
        """
        Add widget to dashboard layout
        
        Args:
            layout_id: Target layout ID
            widget_config: Widget configuration
            
        Returns:
            DashboardWidget: Created widget
        """
        try:
            if layout_id not in self.dashboard_layouts:
                raise ValueError(f"Layout {layout_id} not found")
            
            layout = self.dashboard_layouts[layout_id]
            
            # Create widget
            widget = DashboardWidget(
                widget_id=str(uuid.uuid4()),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                **widget_config
            )
            
            # Add to layout
            layout.widgets.append(widget)
            layout.updated_at = datetime.utcnow()
            
            # Update cache
            await self.cache_manager.set(
                f"dashboard_layout:{layout_id}",
                layout.dict(),
                ttl=self.cache_ttl * 10
            )
            
            logger.info(f"Added widget {widget.title} to layout {layout.name}")
            return widget
            
        except Exception as e:
            logger.error(f"Error adding widget to layout: {str(e)}")
            return None

    async def generate_chart(
        self,
        chart_type: ChartType,
        data_query: str,
        chart_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate chart visualization
        
        Args:
            chart_type: Type of chart to generate
            data_query: SQL query or data source
            chart_config: Chart configuration options
            
        Returns:
            Dict[str, Any]: Chart configuration and data
        """
        try:
            config = chart_config or {}
            
            # Execute data query
            data = await self._execute_data_query(data_query)
            
            if not data:
                return {'error': 'No data returned from query'}
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(data)
            
            # Generate chart based on type
            chart_figure = None
            
            if chart_type == ChartType.LINE_CHART:
                chart_figure = self._create_line_chart(df, config)
            elif chart_type == ChartType.BAR_CHART:
                chart_figure = self._create_bar_chart(df, config)
            elif chart_type == ChartType.PIE_CHART:
                chart_figure = self._create_pie_chart(df, config)
            elif chart_type == ChartType.SCATTER_PLOT:
                chart_figure = self._create_scatter_plot(df, config)
            elif chart_type == ChartType.HEATMAP:
                chart_figure = self._create_heatmap(df, config)
            elif chart_type == ChartType.HISTOGRAM:
                chart_figure = self._create_histogram(df, config)
            elif chart_type == ChartType.BOX_PLOT:
                chart_figure = self._create_box_plot(df, config)
            elif chart_type == ChartType.GAUGE_CHART:
                chart_figure = self._create_gauge_chart(df, config)
            else:
                return {'error': f'Unsupported chart type: {chart_type}'}
            
            if chart_figure:
                # Apply theme
                theme = config.get('theme', DashboardTheme.MODERN)
                chart_figure = self._apply_chart_theme(chart_figure, theme)
                
                return {
                    'figure': chart_figure,
                    'data_points': len(data),
                    'generated_at': datetime.utcnow().isoformat(),
                    'chart_type': chart_type.value
                }
            
            return {'error': 'Failed to generate chart'}
            
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            return {'error': str(e)}

    async def get_analytics_data(
        self,
        metrics: List[str],
        time_range: str = "24h",
        filters: Dict[str, Any] = None,
        groupby: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics data for specified metrics
        
        Args:
            metrics: List of metric names
            time_range: Time range for data
            filters: Additional filters
            groupby: Fields to group by
            
        Returns:
            Dict[str, Any]: Analytics data
        """
        try:
            filters = filters or {}
            groupby = groupby or []
            
            # Parse time range
            time_filter = self._parse_time_range(time_range)
            
            analytics_data = {}
            
            for metric_name in metrics:
                if metric_name not in self.analytics_metrics:
                    continue
                
                metric_def = self.analytics_metrics[metric_name]
                
                # Build query
                query = self._build_metric_query(metric_def, time_filter, filters, groupby)
                
                # Execute query
                data = await self._execute_data_query(query)
                
                # Process data
                processed_data = self._process_metric_data(data, metric_def)
                
                analytics_data[metric_name] = processed_data
            
            # Add metadata
            analytics_data['_metadata'] = {
                'time_range': time_range,
                'filters': filters,
                'groupby': groupby,
                'generated_at': datetime.utcnow().isoformat(),
                'data_points': sum(len(data.get('values', [])) for data in analytics_data.values() if isinstance(data, dict))
            }
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return {'error': str(e)}

    async def generate_ai_insights(
        self,
        data: Dict[str, Any],
        insight_types: List[str] = None
    ) -> List[DashboardInsight]:
        """
        Generate AI-powered insights from data
        
        Args:
            data: Analytics data
            insight_types: Types of insights to generate
            
        Returns:
            List[DashboardInsight]: Generated insights
        """
        try:
            if not self.ai_insights_enabled or not self.insights_endpoint:
                return []
            
            insight_types = insight_types or ['trend', 'anomaly', 'correlation']
            
            # Prepare data for AI analysis
            ai_request = {
                'data': data,
                'insight_types': insight_types,
                'context': {
                    'dashboard_name': 'main_dashboard',
                    'time_period': data.get('_metadata', {}).get('time_range', '24h')
                }
            }
            
            insights = []
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.insights_endpoint,
                    json=ai_request,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        ai_insights = await response.json()
                        
                        for insight_data in ai_insights.get('insights', []):
                            insight = DashboardInsight(
                                insight_id=str(uuid.uuid4()),
                                created_at=datetime.utcnow(),
                                **insight_data
                            )
                            insights.append(insight)
                            
                            # Store insight
                            self.dashboard_insights.append(insight)
            
            # Generate local insights as fallback
            if not insights:
                insights = await self._generate_local_insights(data)
            
            logger.info(f"Generated {len(insights)} AI insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return []

    async def create_analytics_report(
        self,
        name: str,
        metrics: List[str],
        time_range: str = "7d",
        report_config: Dict[str, Any] = None
    ) -> AnalyticsReport:
        """
        Create analytics report
        
        Args:
            name: Report name
            metrics: Metrics to include
            time_range: Time range for report
            report_config: Additional report configuration
            
        Returns:
            AnalyticsReport: Created report
        """
        try:
            config = report_config or {}
            
            report = AnalyticsReport(
                report_id=str(uuid.uuid4()),
                name=name,
                metrics=metrics,
                time_range=time_range,
                created_at=datetime.utcnow(),
                **config
            )
            
            # Store report
            self.active_reports[report.report_id] = report
            
            # Generate initial report
            if config.get('generate_immediately', True):
                await self._generate_report(report)
            
            logger.info(f"Created analytics report: {name}")
            return report
            
        except Exception as e:
            logger.error(f"Error creating analytics report: {str(e)}")
            return None

    async def export_dashboard_data(
        self,
        layout_id: str,
        export_format: str = "json",
        include_data: bool = True
    ) -> Dict[str, Any]:
        """
        Export dashboard data
        
        Args:
            layout_id: Dashboard layout ID
            export_format: Export format
            include_data: Whether to include actual data
            
        Returns:
            Dict[str, Any]: Exported dashboard data
        """
        try:
            if layout_id not in self.dashboard_layouts:
                return {'error': f'Layout {layout_id} not found'}
            
            layout = self.dashboard_layouts[layout_id]
            export_data = {
                'layout': layout.dict(),
                'export_timestamp': datetime.utcnow().isoformat(),
                'export_format': export_format
            }
            
            if include_data:
                # Get data for all widgets
                widget_data = {}
                for widget in layout.widgets:
                    if widget.metrics:
                        data = await self.get_analytics_data(
                            metrics=widget.metrics,
                            time_range=widget.time_range,
                            filters=widget.filters
                        )
                        widget_data[widget.widget_id] = data
                
                export_data['widget_data'] = widget_data
            
            # Format according to export format
            if export_format.lower() == 'csv':
                # Convert to CSV format
                export_data = self._convert_to_csv(export_data)
            elif export_format.lower() == 'pdf':
                # Generate PDF report
                export_data = await self._generate_pdf_export(export_data)
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {str(e)}")
            return {'error': str(e)}

    # Database and data management methods
    
    async def _initialize_database(self):
        """Initialize database connection"""
        try:
            from sqlalchemy import create_engine
            self.db_engine = create_engine(self.primary_database)
            
            # Create tables if they don't exist
            await self._create_database_tables()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")

    async def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio as aioredis
            self.redis_client = aioredis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            
            logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            logger.warning(f"Redis not available: {str(e)}")
            self.redis_client = None

    async def _create_database_tables(self):
        """Create necessary database tables"""
        try:
            create_tables_sql = """
            CREATE TABLE IF NOT EXISTS analytics_metrics (
                metric_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                data_type VARCHAR(50),
                calculation_method VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS dashboard_layouts (
                layout_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                config JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS analytics_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id VARCHAR(255),
                timestamp TIMESTAMP,
                value REAL,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            with self.db_engine.connect() as conn:
                for statement in create_tables_sql.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                conn.commit()
            
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")

    async def _execute_data_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute data query"""
        try:
            # Check cache first
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cached_result = await self.cache_manager.get(f"query:{query_hash}")
            
            if cached_result:
                return cached_result
            
            # Execute query
            with self.db_engine.connect() as conn:
                result = conn.execute(text(query))
                data = [dict(row._mapping) for row in result]
            
            # Cache result
            await self.cache_manager.set(
                f"query:{query_hash}",
                data,
                ttl=self.cache_ttl
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Error executing data query: {str(e)}")
            return []

    # Chart generation methods
    
    def _create_line_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create line chart"""
        fig = go.Figure()
        
        x_col = config.get('x_column', df.columns[0])
        y_cols = config.get('y_columns', [df.columns[1]] if len(df.columns) > 1 else [])
        
        for y_col in y_cols:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='lines+markers',
                name=y_col,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title=config.get('title', 'Line Chart'),
            xaxis_title=config.get('x_axis_title', x_col),
            yaxis_title=config.get('y_axis_title', 'Value'),
            hovermode='x unified'
        )
        
        return fig

    def _create_bar_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create bar chart"""
        fig = go.Figure()
        
        x_col = config.get('x_column', df.columns[0])
        y_col = config.get('y_column', df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=y_col
        ))
        
        fig.update_layout(
            title=config.get('title', 'Bar Chart'),
            xaxis_title=config.get('x_axis_title', x_col),
            yaxis_title=config.get('y_axis_title', y_col)
        )
        
        return fig

    def _create_pie_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create pie chart"""
        fig = go.Figure()
        
        labels_col = config.get('labels_column', df.columns[0])
        values_col = config.get('values_column', df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        fig.add_trace(go.Pie(
            labels=df[labels_col],
            values=df[values_col],
            textinfo='label+percent',
            textposition='inside'
        ))
        
        fig.update_layout(
            title=config.get('title', 'Pie Chart')
        )
        
        return fig

    def _create_scatter_plot(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create scatter plot"""
        fig = go.Figure()
        
        x_col = config.get('x_column', df.columns[0])
        y_col = config.get('y_column', df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='markers',
            marker=dict(
                size=config.get('marker_size', 8),
                opacity=0.7
            )
        ))
        
        fig.update_layout(
            title=config.get('title', 'Scatter Plot'),
            xaxis_title=config.get('x_axis_title', x_col),
            yaxis_title=config.get('y_axis_title', y_col)
        )
        
        return fig

    def _create_heatmap(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create heatmap"""
        fig = go.Figure()
        
        # Create correlation matrix if not specified
        if 'z_values' not in config:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                correlation_matrix = df[numeric_cols].corr()
                z_values = correlation_matrix.values
                x_labels = correlation_matrix.columns.tolist()
                y_labels = correlation_matrix.index.tolist()
            else:
                return go.Figure()  # Return empty figure
        else:
            z_values = config['z_values']
            x_labels = config.get('x_labels', [])
            y_labels = config.get('y_labels', [])
        
        fig.add_trace(go.Heatmap(
            z=z_values,
            x=x_labels,
            y=y_labels,
            colorscale='RdBu',
            zmid=0
        ))
        
        fig.update_layout(
            title=config.get('title', 'Heatmap')
        )
        
        return fig

    def _create_histogram(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create histogram"""
        fig = go.Figure()
        
        column = config.get('column', df.columns[0])
        
        fig.add_trace(go.Histogram(
            x=df[column],
            nbinsx=config.get('bins', 30),
            name=column
        ))
        
        fig.update_layout(
            title=config.get('title', 'Histogram'),
            xaxis_title=config.get('x_axis_title', column),
            yaxis_title='Frequency'
        )
        
        return fig

    def _create_box_plot(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create box plot"""
        fig = go.Figure()
        
        y_col = config.get('y_column', df.columns[0])
        
        if 'x_column' in config:
            # Grouped box plot
            x_col = config['x_column']
            for group in df[x_col].unique():
                group_data = df[df[x_col] == group]
                fig.add_trace(go.Box(
                    y=group_data[y_col],
                    name=str(group)
                ))
        else:
            # Single box plot
            fig.add_trace(go.Box(
                y=df[y_col],
                name=y_col
            ))
        
        fig.update_layout(
            title=config.get('title', 'Box Plot'),
            yaxis_title=config.get('y_axis_title', y_col)
        )
        
        return fig

    def _create_gauge_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create gauge chart"""
        fig = go.Figure()
        
        value = config.get('value', df.iloc[0, 0] if not df.empty else 0)
        max_value = config.get('max_value', 100)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': config.get('title', 'Gauge Chart')},
            delta={'reference': config.get('reference', 0)},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': config.get('bar_color', 'darkblue')},
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': 'lightgray'},
                    {'range': [max_value * 0.5, max_value * 0.8], 'color': 'gray'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': config.get('threshold', max_value * 0.9)
                }
            }
        ))
        
        return fig

    def _apply_chart_theme(self, figure: go.Figure, theme: DashboardTheme) -> go.Figure:
        """Apply theme to chart"""
        theme_config = self.available_themes.get(theme, self.available_themes[DashboardTheme.MODERN])
        
        figure.update_layout(
            paper_bgcolor=theme_config['paper'],
            plot_bgcolor=theme_config['background'],
            font=dict(color=theme_config['text']),
            colorway=[theme_config['primary']]
        )
        
        return figure

    # Data processing and utility methods
    
    def _parse_time_range(self, time_range: str) -> Dict[str, Any]:
        """
Parse time range string into filter conditions"""
        now = datetime.utcnow()
        
        if time_range == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range == "24h":
            start_time = now - timedelta(days=1)
        elif time_range == "7d":
            start_time = now - timedelta(days=7)
        elif time_range == "30d":
            start_time = now - timedelta(days=30)
        elif time_range == "90d":
            start_time = now - timedelta(days=90)
        elif time_range == "1y":
            start_time = now - timedelta(days=365)
        else:
            start_time = now - timedelta(days=1)  # Default to 24h
        
        return {
            'start_time': start_time,
            'end_time': now
        }

    def _build_metric_query(
        self,
        metric_def: AnalyticsMetric,
        time_filter: Dict[str, Any],
        filters: Dict[str, Any],
        groupby: List[str]
    ) -> str:
        """Build SQL query for metric"""
        # Simplified query building
        query = f"SELECT {metric_def.source_column} FROM {metric_def.source_table}"
        
        # Add time filter
        query += f" WHERE timestamp >= '{time_filter['start_time']}'"
        query += f" AND timestamp <= '{time_filter['end_time']}'"
        
        # Add additional filters
        for field, value in filters.items():
            query += f" AND {field} = '{value}'"
        
        # Add groupby
        if groupby:
            query += f" GROUP BY {', '.join(groupby)}"
        
        # Add ordering
        query += " ORDER BY timestamp DESC"
        
        return query

    def _process_metric_data(self, data: List[Dict[str, Any]], metric_def: AnalyticsMetric) -> Dict[str, Any]:
        """Process metric data according to definition"""
        if not data:
            return {'values': [], 'total': 0, 'average': 0}
        
        values = [row.get(metric_def.source_column, 0) for row in data]
        
        processed = {
            'values': values,
            'total': sum(values),
            'average': sum(values) / len(values) if values else 0,
            'count': len(values),
            'min': min(values) if values else 0,
            'max': max(values) if values else 0
        }
        
        # Apply formatting
        if metric_def.data_type == 'percentage':
            processed['formatted_values'] = [f"{v:.1f}%" for v in values]
        elif metric_def.data_type == 'currency':
            processed['formatted_values'] = [f"${v:.2f}" for v in values]
        else:
            processed['formatted_values'] = [metric_def.format_string.format(v) for v in values]
        
        return processed

    # Real-time update methods
    
    async def _real_time_update_loop(self):
        """Real-time data update loop"""
        while self.dashboard_active:
            try:
                # Update real-time data for all active widgets
                for layout in self.dashboard_layouts.values():
                    for widget in layout.widgets:
                        if widget.auto_refresh and widget.visualization_type == VisualizationType.REAL_TIME:
                            await self._update_widget_data(widget)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in real-time update loop: {str(e)}")
                await asyncio.sleep(30)

    async def _insights_generation_loop(self):
        """AI insights generation loop"""
        while self.dashboard_active:
            try:
                if self.ai_insights_enabled:
                    # Generate insights for main dashboard
                    main_data = await self.get_analytics_data(
                        metrics=list(self.analytics_metrics.keys())[:10],  # First 10 metrics
                        time_range="24h"
                    )
                    
                    if main_data:
                        await self.generate_ai_insights(main_data)
                
                await asyncio.sleep(3600)  # Generate insights every hour
                
            except Exception as e:
                logger.error(f"Error in insights generation loop: {str(e)}")
                await asyncio.sleep(3600)

    async def _report_generation_loop(self):
        """Automated report generation loop"""
        while self.dashboard_active:
            try:
                if self.auto_report_generation:
                    for report in self.active_reports.values():
                        if report.status == 'active' and report.report_type == 'scheduled':
                            # Check if report is due
                            if await self._is_report_due(report):
                                await self._generate_report(report)
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Error in report generation loop: {str(e)}")
                await asyncio.sleep(1800)

    # Initialization helper methods
    
    def _initialize_metric_definitions(self) -> Dict[str, AnalyticsMetric]:
        """Initialize predefined metric definitions"""
        metrics = {}
        
        # Performance metrics
        metrics['page_views'] = AnalyticsMetric(
            metric_id="page_views",
            name="Page Views",
            description="Total number of page views",
            category=MetricCategory.ENGAGEMENT,
            calculation_method="count",
            source_table="analytics_events",
            source_column="event_id",
            data_type="number",
            created_at=datetime.utcnow()
        )
        
        metrics['unique_visitors'] = AnalyticsMetric(
            metric_id="unique_visitors",
            name="Unique Visitors",
            description="Number of unique visitors",
            category=MetricCategory.AUDIENCE,
            calculation_method="count_distinct",
            source_table="analytics_events",
            source_column="user_id",
            data_type="number",
            created_at=datetime.utcnow()
        )
        
        return metrics

    def _initialize_chart_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize chart templates"""
        return {
            'performance_overview': {
                'chart_type': ChartType.LINE_CHART,
                'title': 'Performance Overview',
                'metrics': ['response_time', 'throughput', 'error_rate']
            },
            'engagement_summary': {
                'chart_type': ChartType.BAR_CHART,
                'title': 'Engagement Summary',
                'metrics': ['page_views', 'unique_visitors', 'session_duration']
            },
            'traffic_distribution': {
                'chart_type': ChartType.PIE_CHART,
                'title': 'Traffic Distribution',
                'metrics': ['traffic_source']
            }
        }

    async def _create_default_metrics(self):
        """
Create default analytics metrics"""
        for metric_id, metric in self.metric_definitions.items():
            self.analytics_metrics[metric_id] = metric

    async def _create_default_layouts(self):
        """
Create default dashboard layouts"""
        # Main dashboard layout
        main_widgets = [
            {
                'widget_type': 'chart',
                'title': 'Performance Overview',
                'chart_type': ChartType.LINE_CHART,
                'metric_category': MetricCategory.PERFORMANCE,
                'data_source': 'analytics_data',
                'metrics': ['cpu_usage', 'memory_usage'],
                'time_range': '24h',
                'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4}
            },
            {
                'widget_type': 'metric',
                'title': 'Total Page Views',
                'chart_type': ChartType.GAUGE_CHART,
                'metric_category': MetricCategory.ENGAGEMENT,
                'data_source': 'analytics_data',
                'metrics': ['page_views'],
                'time_range': '24h',
                'position': {'x': 6, 'y': 0, 'width': 3, 'height': 2}
            }
        ]
        
        await self.create_dashboard_layout(
            name="Main Dashboard",
            description="Primary analytics dashboard with key metrics",
            widgets=main_widgets
        )

    def _initialize_dash_app(self):
        """Initialize Dash application"""
        try:
            self.dash_app = dash.Dash(__name__)
            
            # Define layout
            self.dash_app.layout = html.Div([
                html.H1("Analytics Dashboard", style={'textAlign': 'center'}),
                html.Div(id='dashboard-content'),
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,  # Update every 30 seconds
                    n_intervals=0
                )
            ])
            
            # Define callbacks
            @self.dash_app.callback(
                Output('dashboard-content', 'children'),
                [Input('interval-component', 'n_intervals')]
            )
            def update_dashboard(n):
                return self._generate_dashboard_layout()
            
        except Exception as e:
            logger.error(f"Error initializing Dash app: {str(e)}")

    def _run_dash_server(self):
        """Run Dash server"""
        try:
            if self.dash_app:
                self.dash_app.run_server(
                    host=self.dashboard_host,
                    port=self.dashboard_port,
                    debug=False
                )
        except Exception as e:
            logger.error(f"Error running Dash server: {str(e)}")

    def _generate_dashboard_layout(self):
        """Generate dashboard layout for Dash"""
        try:
            # Get main dashboard layout
            main_layout = None
            for layout in self.dashboard_layouts.values():
                if layout.name == "Main Dashboard":
                    main_layout = layout
                    break
            
            if not main_layout:
                return html.Div("No dashboard layout found")
            
            # Generate widgets
            dashboard_components = []
            for widget in main_layout.widgets:
                component = self._create_dash_component(widget)
                if component:
                    dashboard_components.append(component)
            
            return html.Div(dashboard_components)
            
        except Exception as e:
            logger.error(f"Error generating dashboard layout: {str(e)}")
            return html.Div(f"Error: {str(e)}")

    def _create_dash_component(self, widget: DashboardWidget):
        """Create Dash component for widget"""
        try:
            if widget.chart_type == ChartType.GAUGE_CHART:
                # Simple metric display
                return html.Div([
                    html.H3(widget.title),
                    html.H2("Loading...", id=f"metric-{widget.widget_id}")
                ], style={'textAlign': 'center', 'padding': '20px'})
            else:
                # Chart component
                return html.Div([
                    html.H3(widget.title),
                    dcc.Graph(id=f"chart-{widget.widget_id}")
                ], style={'padding': '20px'})
                
        except Exception as e:
            logger.error(f"Error creating Dash component: {str(e)}")
            return html.Div(f"Error creating component: {str(e)}")

    # Helper methods for advanced features
    
    async def _update_widget_data(self, widget: DashboardWidget):
        """Update data for a specific widget"""
        try:
            if widget.metrics:
                data = await self.get_analytics_data(
                    metrics=widget.metrics,
                    time_range=widget.time_range,
                    filters=widget.filters
                )
                
                # Store in real-time data
                self.real_time_data[widget.widget_id].append({
                    'timestamp': datetime.utcnow(),
                    'data': data
                })
                
                # Limit data points
                while len(self.real_time_data[widget.widget_id]) > self.max_real_time_points:
                    self.real_time_data[widget.widget_id].popleft()
                    
        except Exception as e:
            logger.error(f"Error updating widget data: {str(e)}")

    async def _generate_local_insights(self, data: Dict[str, Any]) -> List[DashboardInsight]:
        """Generate local insights without AI service"""
        insights = []
        
        try:
            # Simple trend analysis
            for metric_name, metric_data in data.items():
                if metric_name.startswith('_') or not isinstance(metric_data, dict):
                    continue
                
                values = metric_data.get('values', [])
                if len(values) > 10:
                    # Calculate trend
                    recent_avg = sum(values[-5:]) / 5
                    older_avg = sum(values[-10:-5]) / 5
                    
                    if recent_avg > older_avg * 1.1:  # 10% increase
                        insight = DashboardInsight(
                            insight_id=str(uuid.uuid4()),
                            title=f"{metric_name} Trending Up",
                            description=f"{metric_name} has increased by {((recent_avg - older_avg) / older_avg * 100):.1f}%",
                            insight_type="trend",
                            confidence=0.8,
                            metrics_involved=[metric_name],
                            time_period="recent",
                            created_at=datetime.utcnow()
                        )
                        insights.append(insight)
            
        except Exception as e:
            logger.error(f"Error generating local insights: {str(e)}")
        
        return insights

    async def _is_report_due(self, report: AnalyticsReport) -> bool:
        """Check if report generation is due"""
        if not report.next_generation:
            return True
        
        return datetime.utcnow() >= report.next_generation

    async def _generate_report(self, report: AnalyticsReport):
        """
Generate analytics report"""
        try:
            # Get data for report
            data = await self.get_analytics_data(
                metrics=report.metrics,
                time_range=report.time_range
            )
            
            # Generate report content
            report_content = {
                'report_id': report.report_id,
                'name': report.name,
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': report.time_range,
                'data': data
            }
            
            # Add insights if enabled
            if report.include_insights:
                insights = await self.generate_ai_insights(data)
                report_content['insights'] = [insight.dict() for insight in insights]
            
            # Store generated report
            await self.cache_manager.set(
                f"report:{report.report_id}",
                report_content,
                ttl=self.cache_ttl * 100  # Long TTL for reports
            )
            
            # Update report status
            report.last_generated = datetime.utcnow()
            if report.schedule == 'daily':
                report.next_generation = datetime.utcnow() + timedelta(days=1)
            elif report.schedule == 'weekly':
                report.next_generation = datetime.utcnow() + timedelta(weeks=1)
            elif report.schedule == 'monthly':
                report.next_generation = datetime.utcnow() + timedelta(days=30)
            
            logger.info(f"Generated report: {report.name}")
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")

    def _convert_to_csv(self, export_data: Dict[str, Any]) -> str:
        """Convert export data to CSV format"""
        # Simplified CSV conversion
        return "CSV export not yet implemented"

    async def _generate_pdf_export(self, export_data: Dict[str, Any]) -> bytes:
        """Generate PDF export"""
        # Simplified PDF generation
        return b"PDF export not yet implemented"

    async def close(self):
        """Close dashboard and cleanup resources"""
        try:
            await self.stop_dashboard_server()
            await self.cache_manager.close()
            
            if self.redis_client:
                await self.redis_client.close()
            
            await super().close()
            logger.info("Advanced Analytics Dashboard closed successfully")
        except Exception as e:
            logger.error(f"Error closing analytics dashboard: {str(e)}")
