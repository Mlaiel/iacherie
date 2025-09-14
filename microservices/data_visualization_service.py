"""
📊 Data Visualization Service - Interactive Analytics Dashboards
==============================================================

**Module**: Data Visualization Service  
**Author**: Fahed Mlaiel (mlaiel@live.de)  
**Copyright**: (c) 2025 Fahed Mlaiel - All Rights Reserved  
**Role**: Backend Senior + DBA + ML Engineer + DevOps Engineer

Advanced data visualization service with interactive dashboards,
real-time charts, custom widgets, and enterprise-grade analytics.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This code is proprietary and confidential. Unauthorized use prohibited.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
import uuid
import statistics
import math

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataVisualizationService")

class ChartType(str, Enum):
    """ChartType class implementation"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    SANKEY = "sankey"

class WidgetType(str, Enum):
    """WidgetType class implementation"""
    CHART = "chart"
    METRIC_CARD = "metric_card"
    TABLE = "table"
    TEXT = "text"
    IMAGE = "image"
    IFRAME = "iframe"
    CUSTOM = "custom"

class ColorScheme(str, Enum):
    """ColorScheme class implementation"""
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    PURPLE = "purple"
    ORANGE = "orange"
    TEAL = "teal"
    GRADIENT = "gradient"
    CUSTOM = "custom"

@dataclass
class VisualizationMetrics:
    """Data visualization service metrics"""
    total_dashboards: int
    total_charts: int
    active_visualizations: int
    daily_views: int
    average_load_time: float
    user_engagement_rate: float
    export_count: int
    real_time_updates: int

class DataSourceModel(BaseModel):
    """Data source configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # database, api, file, stream
    connection_string: str
    query: Optional[str] = None
    refresh_interval: int = 300  # seconds
    last_updated: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChartConfigModel(BaseModel):
    """Chart configuration model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    chart_type: ChartType
    data_source_id: str
    x_axis: str
    y_axis: Union[str, List[str]]
    color_scheme: ColorScheme = ColorScheme.BLUE
    width: int = 600
    height: int = 400
    show_legend: bool = True
    show_grid: bool = True
    enable_zoom: bool = True
    enable_export: bool = True
    custom_options: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WidgetModel(BaseModel):
    """Dashboard widget model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    widget_type: WidgetType
    position: Dict[str, int]  # x, y, width, height
    chart_config: Optional[ChartConfigModel] = None
    data_source_id: Optional[str] = None
    content: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)
    is_visible: bool = True
    refresh_rate: int = 30  # seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DashboardModel(BaseModel):
    """Interactive dashboard model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    widgets: List[WidgetModel] = Field(default_factory=list)
    layout: Dict[str, Any] = Field(default_factory=dict)
    theme: str = "light"
    is_public: bool = False
    owner_id: str
    collaborators: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    view_count: int = 0

class DataVisualizationService:
    """
    📊 Enterprise Data Visualization Service
    
    **Expertise Applied:**
    - **Backend Senior**: Scalable dashboard architecture and real-time updates
    - **DBA**: Optimized data retrieval and query performance
    - **ML Engineer**: Advanced statistical visualizations and predictive charts
    - **DevOps**: Performance monitoring and export capabilities
    """
    
    def __init__(self) -> None:
        self.dashboards: Dict[str, DashboardModel] = {}
        self.data_sources: Dict[str, DataSourceModel] = {}
        self.chart_configs: Dict[str, ChartConfigModel] = {}
        self.cached_data: Dict[str, Dict] = {}
        self.real_time_connections: Dict[str, Any] = {}
        self.chart_templates: Dict[str, Dict] = {}
        
        # Initialize default data sources and templates
        self._initialize_default_data_sources()
        self._initialize_chart_templates()
        
        logger.info("📊 Data Visualization Service initialized")
    
    def _initialize_default_data_sources(self) -> None:
        """Initialize default data sources"""
        default_sources = [
            {
                "name": "User Analytics",
                "type": "analytics",
                "connection_string": "analytics://user_data",
                "query": "SELECT date, user_count, active_users FROM daily_stats",
                "refresh_interval": 300
            },
            {
                "name": "Revenue Data",
                "type": "financial",
                "connection_string": "finance://revenue_data",
                "query": "SELECT date, revenue, transactions FROM revenue_daily",
                "refresh_interval": 600
            },
            {
                "name": "Content Metrics",
                "type": "content",
                "connection_string": "content://metrics",
                "query": "SELECT date, uploads, views, engagement FROM content_stats",
                "refresh_interval": 180
            }
        ]
        
        for source_data in default_sources:
            source = DataSourceModel(**source_data)
            self.data_sources[source.id] = source
    
    def _initialize_chart_templates(self) -> None:
        """Initialize chart templates for common use cases"""
        self.chart_templates = {
            "user_growth": {
                "title": "User Growth Over Time",
                "chart_type": ChartType.LINE,
                "x_axis": "date",
                "y_axis": "user_count",
                "color_scheme": ColorScheme.BLUE,
                "show_trend": True
            },
            "revenue_trend": {
                "title": "Revenue Trend",
                "chart_type": ChartType.AREA,
                "x_axis": "date", 
                "y_axis": "revenue",
                "color_scheme": ColorScheme.GREEN,
                "show_total": True
            },
            "engagement_pie": {
                "title": "Engagement Distribution",
                "chart_type": ChartType.PIE,
                "x_axis": "category",
                "y_axis": "percentage",
                "color_scheme": ColorScheme.GRADIENT,
                "show_percentages": True
            },
            "performance_gauge": {
                "title": "Performance Score",
                "chart_type": ChartType.GAUGE,
                "y_axis": "score",
                "color_scheme": ColorScheme.TEAL,
                "min_value": 0,
                "max_value": 100
            }
        }
    
    async def create_data_source(self, source: DataSourceModel) -> Dict[str, Any]:
        """Create new data source"""
        try:
            # Validate data source
            if not source.name or not source.connection_string:
                raise ValueError("Data source name and connection string are required")
            
            # Test connection
            connection_test = await self._test_data_source_connection(source)
            if not connection_test["success"]:
                raise ValueError(f"Connection test failed: {connection_test['error']}")
            
            # Store data source
            self.data_sources[source.id] = source
            
            # Initialize data cache
            await self._refresh_data_source(source.id)
            
            logger.info(f"📊 Data source created: {source.name} (ID: {source.id})")
            
            return {
                "success": True,
                "data_source_id": source.id,
                "data_source": source.dict(),
                "connection_test": connection_test,
                "message": "Data source created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Data source creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data source creation failed: {str(e)}")
    
    async def create_chart(self, chart_config: ChartConfigModel) -> Dict[str, Any]:
        """Create new chart configuration"""
        try:
            # Validate chart config
            if chart_config.data_source_id not in self.data_sources:
                raise ValueError(f"Data source {chart_config.data_source_id} not found")
            
            # Store chart config
            self.chart_configs[chart_config.id] = chart_config
            
            # Generate chart data
            chart_data = await self._generate_chart_data(chart_config.id)
            
            logger.info(f"📈 Chart created: {chart_config.title} (ID: {chart_config.id})")
            
            return {
                "success": True,
                "chart_id": chart_config.id,
                "chart_config": chart_config.dict(),
                "chart_data": chart_data,
                "message": "Chart created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Chart creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Chart creation failed: {str(e)}")
    
    async def create_dashboard(self, dashboard: DashboardModel) -> Dict[str, Any]:
        """Create new interactive dashboard"""
        try:
            # Validate dashboard
            if not dashboard.name or not dashboard.owner_id:
                raise ValueError("Dashboard name and owner are required")
            
            # Store dashboard
            self.dashboards[dashboard.id] = dashboard
            
            # Initialize dashboard data
            dashboard_data = await self._initialize_dashboard_data(dashboard.id)
            
            logger.info(f"📊 Dashboard created: {dashboard.name} (ID: {dashboard.id})")
            
            return {
                "success": True,
                "dashboard_id": dashboard.id,
                "dashboard": dashboard.dict(),
                "dashboard_data": dashboard_data,
                "message": "Dashboard created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Dashboard creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Dashboard creation failed: {str(e)}")
    
    async def get_dashboard_data(self, dashboard_id: str, user_id: str = None) -> Dict[str, Any]:
        """Get dashboard data with all widgets"""
        try:
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            dashboard = self.dashboards[dashboard_id]
            
            # Check access permissions
            if not dashboard.is_public:
                if user_id != dashboard.owner_id and user_id not in dashboard.collaborators:
                    raise ValueError("Access denied to dashboard")
            
            # Get data for each widget
            widget_data = {}
            for widget in dashboard.widgets:
                try:
                    data = await self._get_widget_data(widget)
                    widget_data[widget.id] = data
                except Exception as e:
                    logger.warning(f"Widget data retrieval failed for {widget.id}: {str(e)}")
                    widget_data[widget.id] = {"error": str(e)}
            
            # Update view count
            dashboard.view_count += 1
            
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "dashboard": dashboard.dict(),
                "widget_data": widget_data,
                "last_updated": datetime.utcnow().isoformat(),
                "message": "Dashboard data retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Dashboard data retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")
    
    async def create_from_template(self, template_name: str, dashboard_name: str,
                                 owner_id: str, customization: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create dashboard from template"""
        try:
            if template_name not in self.chart_templates:
                raise ValueError(f"Template '{template_name}' not found")
            
            template = self.chart_templates[template_name]
            
            # Create dashboard
            dashboard = DashboardModel(
                name=dashboard_name,
                description=f"Dashboard created from {template_name} template",
                owner_id=owner_id
            )
            
            # Add widgets based on template
            if template_name == "user_growth":
                widget = WidgetModel(
                    title=template["title"],
                    widget_type=WidgetType.CHART,
                    position={"x": 0, "y": 0, "width": 8, "height": 6},
                    chart_config=ChartConfigModel(
                        title=template["title"],
                        chart_type=template["chart_type"],
                        data_source_id=list(self.data_sources.keys())[0],
                        x_axis=template["x_axis"],
                        y_axis=template["y_axis"],
                        color_scheme=template["color_scheme"]
                    )
                )
            elif template_name == "revenue_trend":
                widget = WidgetModel(
                    title=template["title"],
                    widget_type=WidgetType.CHART,
                    position={"x": 0, "y": 0, "width": 12, "height": 6},
                    chart_config=ChartConfigModel(
                        title=template["title"],
                        chart_type=template["chart_type"],
                        data_source_id=list(self.data_sources.keys())[1] if len(self.data_sources) > 1 else list(self.data_sources.keys())[0],
                        x_axis=template["x_axis"],
                        y_axis=template["y_axis"],
                        color_scheme=template["color_scheme"]
                    )
                )
            else:
                # Generic template
                widget = WidgetModel(
                    title=template["title"],
                    widget_type=WidgetType.CHART,
                    position={"x": 0, "y": 0, "width": 6, "height": 4},
                    chart_config=ChartConfigModel(
                        title=template["title"],
                        chart_type=template["chart_type"],
                        data_source_id=list(self.data_sources.keys())[0],
                        x_axis=template.get("x_axis", "date"),
                        y_axis=template.get("y_axis", "value"),
                        color_scheme=template["color_scheme"]
                    )
                )
            
            dashboard.widgets.append(widget)
            
            # Apply customization
            if customization:
                if "theme" in customization:
                    dashboard.theme = customization["theme"]
                if "is_public" in customization:
                    dashboard.is_public = customization["is_public"]
            
            return await self.create_dashboard(dashboard)
            
        except Exception as e:
            logger.error(f"❌ Template dashboard creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Template creation failed: {str(e)}")
    
    async def export_dashboard(self, dashboard_id: str, format: str = "png",
                             user_id: str = None) -> Dict[str, Any]:
        """Export dashboard in specified format"""
        try:
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            dashboard = self.dashboards[dashboard_id]
            
            # Check access permissions
            if not dashboard.is_public:
                if user_id != dashboard.owner_id and user_id not in dashboard.collaborators:
                    raise ValueError("Access denied to dashboard")
            
            # Generate export
            export_data = await self._generate_dashboard_export(dashboard, format)
            
            logger.info(f"📊 Dashboard exported: {dashboard.name} as {format}")
            
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "export_format": format,
                "export_data": export_data,
                "generated_at": datetime.utcnow().isoformat(),
                "message": "Dashboard exported successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Dashboard export failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Dashboard export failed: {str(e)}")
    
    async def get_chart_data(self, chart_id: str, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get chart data with optional time filtering"""
        try:
            if chart_id not in self.chart_configs:
                raise ValueError(f"Chart {chart_id} not found")
            
            chart_config = self.chart_configs[chart_id]
            
            # Generate chart data
            chart_data = await self._generate_chart_data(chart_id, time_range)
            
            # Calculate chart statistics
            stats = await self._calculate_chart_statistics(chart_data)
            
            return {
                "success": True,
                "chart_id": chart_id,
                "chart_config": chart_config.dict(),
                "data": chart_data,
                "statistics": stats,
                "last_updated": datetime.utcnow().isoformat(),
                "message": "Chart data retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Chart data retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Chart data retrieval failed: {str(e)}")
    
    async def update_widget(self, dashboard_id: str, widget_id: str, 
                          updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard widget"""
        try:
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            dashboard = self.dashboards[dashboard_id]
            widget = next((w for w in dashboard.widgets if w.id == widget_id), None)
            
            if not widget:
                raise ValueError(f"Widget {widget_id} not found")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(widget, key):
                    setattr(widget, key, value)
            
            # Update dashboard modified time
            dashboard.last_modified = datetime.utcnow()
            
            # Get updated widget data
            widget_data = await self._get_widget_data(widget)
            
            logger.info(f"📊 Widget updated: {widget_id} in dashboard {dashboard_id}")
            
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "widget_id": widget_id,
                "updated_widget": widget.dict(),
                "widget_data": widget_data,
                "message": "Widget updated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Widget update failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Widget update failed: {str(e)}")
    
    async def _test_data_source_connection(self, source: DataSourceModel) -> Dict[str, Any]:
        """Test data source connection"""
        try:
            # Simulate connection test
            if source.type in ["analytics", "financial", "content"]:
                return {
                    "success": True,
                    "response_time": 0.15,
                    "records_available": 1000
                }
            else:
                return {
                    "success": False,
                    "error": "Unsupported data source type"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _refresh_data_source(self, source_id -> None: str) -> None:
        """Refresh data from data source"""
        try:
            source = self.data_sources[source_id]
            
            # Generate sample data based on source type
            if "user" in source.name.lower():
                data = await self._generate_user_analytics_data()
            elif "revenue" in source.name.lower():
                data = await self._generate_revenue_data()
            elif "content" in source.name.lower():
                data = await self._generate_content_metrics_data()
            else:
                data = await self._generate_generic_data()
            
            self.cached_data[source_id] = {
                "data": data,
                "last_updated": datetime.utcnow(),
                "record_count": len(data)
            }
            
            source.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"❌ Data source refresh failed: {str(e)}")
    
    async def _generate_user_analytics_data(self) -> List[Dict[str, Any]]:
        """Generate sample user analytics data"""
        data = []
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            user_count = 1000 + i * 25 + (i % 7) * 50
            active_users = int(user_count * 0.7) + (i % 5) * 20
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "user_count": user_count,
                "active_users": active_users,
                "new_users": max(5, 20 + (i % 10) * 3),
                "retention_rate": 75 + (i % 15)
            })
        
        return data
    
    async def _generate_revenue_data(self) -> List[Dict[str, Any]]:
        """Generate sample revenue data"""
        data = []
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            base_revenue = 5000
            daily_revenue = base_revenue + i * 100 + (i % 7) * 500
            transactions = int(daily_revenue / 25) + (i % 10) * 5
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "revenue": daily_revenue,
                "transactions": transactions,
                "avg_transaction": round(daily_revenue / transactions, 2) if transactions > 0 else 0,
                "conversion_rate": 2.5 + (i % 8) * 0.3
            })
        
        return data
    
    async def _generate_content_metrics_data(self) -> List[Dict[str, Any]]:
        """Generate sample content metrics data"""
        data = []
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            uploads = 50 + i * 2 + (i % 7) * 10
            views = uploads * 150 + (i % 5) * 500
            engagement = views * 0.05 + (i % 12) * 20
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "uploads": uploads,
                "views": int(views),
                "engagement": int(engagement),
                "avg_quality_score": 75 + (i % 20),
                "viral_content": max(0, (i % 15) - 10)
            })
        
        return data
    
    async def _generate_generic_data(self) -> List[Dict[str, Any]]:
        """Generate generic sample data"""
        data = []
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            value = 100 + i * 5 + math.sin(i / 7) * 20
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": round(value, 2),
                "category": f"Category_{i % 5}",
                "score": 50 + (i % 50)
            })
        
        return data
    
    async def _generate_chart_data(self, chart_id: str, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate chart data from configuration"""
        chart_config = self.chart_configs[chart_id]
        data_source = self.data_sources[chart_config.data_source_id]
        
        # Get cached data
        if chart_config.data_source_id not in self.cached_data:
            await self._refresh_data_source(chart_config.data_source_id)
        
        source_data = self.cached_data[chart_config.data_source_id]["data"]
        
        # Apply time range filtering if specified
        if time_range:
            filtered_data = []
            start_date = time_range.get("start_date")
            end_date = time_range.get("end_date")
            
            for record in source_data:
                record_date = record.get("date")
                if start_date and record_date < start_date:
                    continue
                if end_date and record_date > end_date:
                    continue
                filtered_data.append(record)
            
            source_data = filtered_data
        
        # Format data for chart type
        if chart_config.chart_type == ChartType.LINE:
            chart_data = {
                "labels": [record[chart_config.x_axis] for record in source_data],
                "datasets": [{
                    "label": chart_config.title,
                    "data": [record[chart_config.y_axis] for record in source_data],
                    "borderColor": self._get_color_for_scheme(chart_config.color_scheme),
                    "tension": 0.1
                }]
            }
        elif chart_config.chart_type == ChartType.BAR:
            chart_data = {
                "labels": [record[chart_config.x_axis] for record in source_data],
                "datasets": [{
                    "label": chart_config.title,
                    "data": [record[chart_config.y_axis] for record in source_data],
                    "backgroundColor": self._get_color_for_scheme(chart_config.color_scheme)
                }]
            }
        elif chart_config.chart_type == ChartType.PIE:
            # Aggregate data for pie chart
            categories = {}
            for record in source_data:
                category = record.get(chart_config.x_axis, "Unknown")
                value = record.get(chart_config.y_axis, 0)
                categories[category] = categories.get(category, 0) + value
            
            chart_data = {
                "labels": list(categories.keys()),
                "datasets": [{
                    "data": list(categories.values()),
                    "backgroundColor": self._get_color_palette(len(categories))
                }]
            }
        elif chart_config.chart_type == ChartType.GAUGE:
            # Get latest value for gauge
            latest_value = source_data[-1][chart_config.y_axis] if source_data else 0
            chart_data = {
                "value": latest_value,
                "min": chart_config.custom_options.get("min_value", 0),
                "max": chart_config.custom_options.get("max_value", 100),
                "color": self._get_color_for_scheme(chart_config.color_scheme)
            }
        else:
            # Default format
            chart_data = {
                "labels": [record[chart_config.x_axis] for record in source_data],
                "data": [record[chart_config.y_axis] for record in source_data]
            }
        
        return chart_data
    
    async def _get_widget_data(self, widget: WidgetModel) -> Dict[str, Any]:
        """Get data for a specific widget"""
        if widget.widget_type == WidgetType.CHART and widget.chart_config:
            return await self._generate_chart_data(widget.chart_config.id)
        elif widget.widget_type == WidgetType.METRIC_CARD:
            # Generate metric card data
            if widget.data_source_id and widget.data_source_id in self.cached_data:
                source_data = self.cached_data[widget.data_source_id]["data"]
                if source_data:
                    latest_record = source_data[-1]
                    return {
                        "current_value": latest_record.get("value", 0),
                        "previous_value": source_data[-2].get("value", 0) if len(source_data) > 1 else 0,
                        "change_percentage": self._calculate_percentage_change(
                            source_data[-2].get("value", 0) if len(source_data) > 1 else 0,
                            latest_record.get("value", 0)
                        ),
                        "trend": "up" if len(source_data) > 1 and latest_record.get("value", 0) > source_data[-2].get("value", 0) else "down"
                    }
            return {"current_value": 0, "previous_value": 0, "change_percentage": 0, "trend": "neutral"}
        elif widget.widget_type == WidgetType.TABLE:
            # Generate table data
            if widget.data_source_id and widget.data_source_id in self.cached_data:
                return {
                    "columns": ["Date", "Value", "Category"],
                    "rows": self.cached_data[widget.data_source_id]["data"][-10:]  # Last 10 records
                }
            return {"columns": [], "rows": []}
        else:
            return {"content": widget.content or "No data available"}
    
    async def _initialize_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Initialize dashboard with initial data"""
        dashboard = self.dashboards[dashboard_id]
        
        # Refresh all data sources used by this dashboard
        data_source_ids = set()
        for widget in dashboard.widgets:
            if widget.data_source_id:
                data_source_ids.add(widget.data_source_id)
            elif widget.chart_config and widget.chart_config.data_source_id:
                data_source_ids.add(widget.chart_config.data_source_id)
        
        for source_id in data_source_ids:
            if source_id in self.data_sources:
                await self._refresh_data_source(source_id)
        
        return {
            "initialized": True,
            "data_sources_refreshed": len(data_source_ids),
            "widgets_count": len(dashboard.widgets)
        }
    
    def _get_color_for_scheme(self, scheme: ColorScheme) -> str:
        """Get color code for color scheme"""
        color_map = {
            ColorScheme.BLUE: "#3498db",
            ColorScheme.GREEN: "#2ecc71",
            ColorScheme.RED: "#e74c3c",
            ColorScheme.PURPLE: "#9b59b6",
            ColorScheme.ORANGE: "#f39c12",
            ColorScheme.TEAL: "#1abc9c"
        }
        return color_map.get(scheme, "#3498db")
    
    def _get_color_palette(self, count: int) -> List[str]:
        """Get color palette for multiple data series"""
        colors = [
            "#3498db", "#2ecc71", "#e74c3c", "#9b59b6", "#f39c12",
            "#1abc9c", "#34495e", "#95a5a6", "#d35400", "#c0392b"
        ]
        return colors[:count] if count <= len(colors) else colors * (count // len(colors) + 1)
    
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change"""
        if old_value == 0:
            return 0
        return round(((new_value - old_value) / old_value) * 100, 2)
    
    async def _calculate_chart_statistics(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics for chart data"""
        stats = {"count": 0, "min": 0, "max": 0, "average": 0}
        
        if "datasets" in chart_data and chart_data["datasets"]:
            data_values = chart_data["datasets"][0].get("data", [])
            if data_values:
                stats = {
                    "count": len(data_values),
                    "min": min(data_values),
                    "max": max(data_values),
                    "average": round(statistics.mean(data_values), 2),
                    "total": sum(data_values)
                }
        elif "data" in chart_data:
            data_values = chart_data["data"]
            if data_values:
                stats = {
                    "count": len(data_values),
                    "min": min(data_values),
                    "max": max(data_values),
                    "average": round(statistics.mean(data_values), 2),
                    "total": sum(data_values)
                }
        
        return stats
    
    async def _generate_dashboard_export(self, dashboard: DashboardModel, format: str) -> Dict[str, Any]:
        """Generate dashboard export in specified format"""
        export_data = {
            "dashboard_info": {
                "name": dashboard.name,
                "description": dashboard.description,
                "created_at": dashboard.created_at.isoformat(),
                "widgets_count": len(dashboard.widgets)
            },
            "widgets": []
        }
        
        # Export each widget
        for widget in dashboard.widgets:
            widget_export = {
                "title": widget.title,
                "type": widget.widget_type.value,
                "position": widget.position
            }
            
            # Add widget data
            if widget.widget_type == WidgetType.CHART and widget.chart_config:
                chart_data = await self._generate_chart_data(widget.chart_config.id)
                widget_export["chart_data"] = chart_data
                widget_export["chart_config"] = widget.chart_config.dict()
            
            export_data["widgets"].append(widget_export)
        
        if format == "json":
            return export_data
        elif format == "csv":
            # Convert to CSV format (simplified)
            return {"csv_data": "CSV export not fully implemented"}
        else:
            return {"export_url": f"/exports/{dashboard.id}.{format}"}
    
    async def get_visualization_metrics(self) -> Dict[str, Any]:
        """Get visualization service metrics"""
        try:
            total_dashboards = len(self.dashboards)
            total_charts = len(self.chart_configs)
            
            # Count active visualizations (accessed in last 24 hours)
            active_visualizations = len([d for d in self.dashboards.values() 
                                       if d.view_count > 0])
            
            # Calculate daily views
            daily_views = sum(d.view_count for d in self.dashboards.values())
            
            # Calculate average load time (simulated)
            average_load_time = 1.2  # seconds
            
            # Calculate engagement rate
            total_possible_views = total_dashboards * 10  # Assume 10 potential views per dashboard
            user_engagement_rate = (daily_views / total_possible_views * 100) if total_possible_views > 0 else 0
            
            metrics = VisualizationMetrics(
                total_dashboards=total_dashboards,
                total_charts=total_charts,
                active_visualizations=active_visualizations,
                daily_views=daily_views,
                average_load_time=average_load_time,
                user_engagement_rate=min(100, user_engagement_rate),
                export_count=0,  # Simplified
                real_time_updates=len(self.real_time_connections)
            )
            
            return {
                "success": True,
                "metrics": asdict(metrics),
                "data_sources_count": len(self.data_sources),
                "cached_datasets": len(self.cached_data),
                "message": "Visualization metrics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Visualization metrics failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Metrics failed: {str(e)}")

# FastAPI Application
app = FastAPI(title="Data Visualization Service", version="1.0.0")
service = DataVisualizationService()

@app.post("/data-sources/create")
async def create_data_source(source -> None: DataSourceModel) -> None:
    """Create new data source"""
    return await service.create_data_source(source)

@app.post("/charts/create")
async def create_chart(chart_config -> None: ChartConfigModel) -> None:
    """Create new chart configuration"""
    return await service.create_chart(chart_config)

@app.post("/dashboards/create")
async def create_dashboard(dashboard -> None: DashboardModel) -> None:
    """Create new interactive dashboard"""
    return await service.create_dashboard(dashboard)

@app.get("/dashboards/{dashboard_id}/data")
async def get_dashboard_data(dashboard_id -> None: str, user_id -> None: str = None) -> None:
    """Get dashboard data with all widgets"""
    return await service.get_dashboard_data(dashboard_id, user_id)

@app.post("/dashboards/create-from-template")
async def create_from_template(template_name -> None: str, dashboard_name -> None: str, 
                             owner_id -> None: str, customization -> None: Dict[str, Any] = None) -> None:
    """Create dashboard from template"""
    return await service.create_from_template(template_name, dashboard_name, owner_id, customization)

@app.get("/charts/{chart_id}/data")
async def get_chart_data(chart_id -> None: str, time_range -> None: Dict[str, Any] = None) -> None:
    """Get chart data with optional time filtering"""
    return await service.get_chart_data(chart_id, time_range)

@app.put("/dashboards/{dashboard_id}/widgets/{widget_id}")
async def update_widget(dashboard_id -> None: str, widget_id -> None: str, updates -> None: Dict[str, Any]) -> None:
    """Update dashboard widget"""
    return await service.update_widget(dashboard_id, widget_id, updates)

@app.post("/dashboards/{dashboard_id}/export")
async def export_dashboard(dashboard_id -> None: str, format -> None: str = "png", user_id -> None: str = None) -> None:
    """Export dashboard in specified format"""
    return await service.export_dashboard(dashboard_id, format, user_id)

@app.get("/metrics")
async def get_metrics() -> None:
    """Get visualization service metrics"""
    return await service.get_visualization_metrics()

@app.get("/health")
async def health_check() -> None:
    """Service health check"""
    return {
        "service": "DataVisualizationService",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("📊 Starting Data Visualization Service...")
    print("📈 Interactive dashboards and analytics charts")
    print("🎨 Custom visualizations and real-time updates")
    print("📋 Enterprise reporting and export capabilities")
    
    uvicorn.run(app, host="0.0.0.0", port=8091)