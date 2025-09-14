"""
Dashboard Generator
==================

Advanced dashboard generation engine for Ainflue Distribution Platform.
Creates dynamic, interactive dashboards for monitoring and analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from jinja2 import Template, Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Available chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    METRIC = "metric"
    HISTOGRAM = "histogram"
    BOX = "box"
    AREA = "area"
    FUNNEL = "funnel"

class DashboardTheme(Enum):
    """Dashboard themes"""
    LIGHT = "light"
    DARK = "dark"
    COLORFUL = "colorful"
    MINIMAL = "minimal"
    CORPORATE = "corporate"

class RefreshRate(Enum):
    """Dashboard refresh rates"""
    REAL_TIME = 5  # 5 seconds
    FAST = 30  # 30 seconds
    NORMAL = 60  # 1 minute
    SLOW = 300  # 5 minutes
    HOURLY = 3600  # 1 hour

@dataclass
class MetricConfig:
    """Configuration for a single metric"""
    metric_id: str
    name: str
    description: str
    data_source: str
    query: str
    chart_type: str
    aggregation: str = "sum"
    time_range: str = "24h"
    refresh_rate: int = 60
    thresholds: Dict[str, float] = field(default_factory=dict)
    formatting: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChartConfig:
    """Configuration for a chart widget"""
    chart_id: str
    title: str
    chart_type: str
    data_source: str
    metrics: List[str]
    time_range: str = "24h"
    refresh_rate: int = 60
    width: int = 6  # Bootstrap grid width (1-12)
    height: int = 400  # Height in pixels
    position: Dict[str, int] = field(default_factory=dict)  # row, col
    styling: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DashboardConfig:
    """Configuration for a complete dashboard"""
    dashboard_id: str
    name: str
    description: str
    theme: str = "light"
    refresh_rate: int = 60
    auto_refresh: bool = True
    charts: List[ChartConfig] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    is_public: bool = False

class DashboardGenerator:
    """
    Advanced Dashboard Generator
    
    Provides comprehensive dashboard creation including:
    - Dynamic chart generation
    - Real-time data updates
    - Interactive filtering
    - Multiple themes and layouts
    - Export capabilities
    - Alert integration
    """
    
    def __init__(self, data_sources -> None: Dict[str, Any] = None) -> None:
        """
        Initialize dashboard generator
        
        Args:
            data_sources: Dictionary of available data sources
        """
        self.data_sources = data_sources or {}
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.templates_dir = "templates/dashboards"
        self.output_dir = "dashboards/generated"
        self._ensure_directories()
        
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def register_data_source(self, name: str, source_config: Dict[str, Any]) -> bool:
        """
        Register a data source
        
        Args:
            name: Data source name
            source_config: Data source configuration
            
        Returns:
            bool: Success status
        """
        try:
            required_fields = ['type', 'connection']
            if not all(field in source_config for field in required_fields):
                logger.error(f"Data source config missing required fields: {required_fields}")
                return False
            
            self.data_sources[name] = source_config
            logger.info(f"Registered data source: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering data source: {str(e)}")
            return False
    
    def create_dashboard(self, config: DashboardConfig) -> bool:
        """
        Create a new dashboard
        
        Args:
            config: Dashboard configuration
            
        Returns:
            bool: Success status
        """
        try:
            if not config.dashboard_id or not config.name:
                logger.error("Dashboard ID and name are required")
                return False
            
            # Validate charts
            for chart in config.charts:
                if not self._validate_chart_config(chart):
                    logger.error(f"Invalid chart configuration: {chart.chart_id}")
                    return False
            
            self.dashboards[config.dashboard_id] = config
            logger.info(f"Created dashboard: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return False
    
    def _validate_chart_config(self, chart: ChartConfig) -> bool:
        """Validate chart configuration"""
        if not chart.chart_id or not chart.title:
            return False
        
        if chart.chart_type not in [ct.value for ct in ChartType]:
            return False
        
        if chart.data_source not in self.data_sources:
            logger.warning(f"Data source not found: {chart.data_source}")
        
        return True
    
    async def generate_dashboard_html(self, dashboard_id: str, 
                                    output_file: str = None) -> str:
        """
        Generate HTML dashboard
        
        Args:
            dashboard_id: Dashboard ID
            output_file: Optional output file path
            
        Returns:
            str: Generated HTML or file path
        """
        try:
            if dashboard_id not in self.dashboards:
                logger.error(f"Dashboard not found: {dashboard_id}")
                return ""
            
            dashboard = self.dashboards[dashboard_id]
            
            # Generate chart data
            charts_data = []
            for chart in dashboard.charts:
                chart_data = await self._generate_chart_data(chart)
                charts_data.append(chart_data)
            
            # Generate HTML
            html_content = self._render_dashboard_template(dashboard, charts_data)
            
            # Save to file if specified
            if output_file:
                output_path = os.path.join(self.output_dir, output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Generated dashboard HTML: {output_path}")
                return output_path
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating dashboard HTML: {str(e)}")
            return ""
    
    async def _generate_chart_data(self, chart: ChartConfig) -> Dict[str, Any]:
        """Generate data for a specific chart"""
        try:
            # Simulate data retrieval (in real implementation, query actual data sources)
            data = await self._fetch_data_from_source(chart.data_source, chart.metrics)
            
            # Create chart based on type
            chart_html = ""
            chart_config = {}
            
            if chart.chart_type == ChartType.LINE.value:
                chart_html, chart_config = self._create_line_chart(chart, data)
            elif chart.chart_type == ChartType.BAR.value:
                chart_html, chart_config = self._create_bar_chart(chart, data)
            elif chart.chart_type == ChartType.PIE.value:
                chart_html, chart_config = self._create_pie_chart(chart, data)
            elif chart.chart_type == ChartType.GAUGE.value:
                chart_html, chart_config = self._create_gauge_chart(chart, data)
            elif chart.chart_type == ChartType.TABLE.value:
                chart_html, chart_config = self._create_table_chart(chart, data)
            elif chart.chart_type == ChartType.METRIC.value:
                chart_html, chart_config = self._create_metric_display(chart, data)
            else:
                chart_html = f"<div>Chart type {chart.chart_type} not implemented</div>"
            
            return {
                "chart_id": chart.chart_id,
                "title": chart.title,
                "html": chart_html,
                "config": chart_config,
                "width": chart.width,
                "height": chart.height,
                "position": chart.position
            }
            
        except Exception as e:
            logger.error(f"Error generating chart data: {str(e)}")
            return {
                "chart_id": chart.chart_id,
                "title": chart.title,
                "html": f"<div>Error loading chart: {str(e)}</div>",
                "config": {},
                "width": chart.width,
                "height": chart.height,
                "position": chart.position
            }
    
    async def _fetch_data_from_source(self, source_name: str, 
                                    metrics: List[str]) -> pd.DataFrame:
        """Fetch data from specified source"""
        # Simulate data fetching - in real implementation, connect to actual data sources
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Generate sample data
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), 
                            end=datetime.now(), freq='H')
        
        data = {'timestamp': dates}
        for metric in metrics:
            if metric == "engagement_rate":
                data[metric] = np.random.uniform(0.01, 0.08, len(dates))
            elif metric == "reach":
                data[metric] = np.random.randint(1000, 50000, len(dates))
            elif metric == "impressions":
                data[metric] = np.random.randint(5000, 100000, len(dates))
            elif metric == "clicks":
                data[metric] = np.random.randint(50, 2000, len(dates))
            elif metric == "conversions":
                data[metric] = np.random.randint(5, 100, len(dates))
            else:
                data[metric] = np.random.uniform(0, 100, len(dates))
        
        return pd.DataFrame(data)
    
    def _create_line_chart(self, chart: ChartConfig, 
                          data: pd.DataFrame) -> tuple[str, Dict]:
        """Create line chart"""
        fig = go.Figure()
        
        for metric in chart.metrics:
            if metric in data.columns:
                fig.add_trace(go.Scatter(
                    x=data['timestamp'],
                    y=data[metric],
                    mode='lines+markers',
                    name=metric.replace('_', ' ').title(),
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title=chart.title,
            xaxis_title="Time",
            yaxis_title="Value",
            height=chart.height,
            template="plotly_white"
        )
        
        chart_html = fig.to_html(include_plotlyjs=False, div_id=chart.chart_id)
        chart_config = {
            "type": "line",
            "data_points": len(data),
            "metrics": chart.metrics
        }
        
        return chart_html, chart_config
    
    def _create_bar_chart(self, chart: ChartConfig, 
                         data: pd.DataFrame) -> tuple[str, Dict]:
        """Create bar chart"""
        # Aggregate data for bar chart
        latest_data = data.tail(24).groupby(data['timestamp'].dt.hour).mean()
        
        fig = go.Figure()
        
        for metric in chart.metrics:
            if metric in latest_data.columns:
                fig.add_trace(go.Bar(
                    x=latest_data.index,
                    y=latest_data[metric],
                    name=metric.replace('_', ' ').title()
                ))
        
        fig.update_layout(
            title=chart.title,
            xaxis_title="Hour",
            yaxis_title="Value",
            height=chart.height,
            template="plotly_white"
        )
        
        chart_html = fig.to_html(include_plotlyjs=False, div_id=chart.chart_id)
        chart_config = {
            "type": "bar",
            "data_points": len(latest_data),
            "metrics": chart.metrics
        }
        
        return chart_html, chart_config
    
    def _create_pie_chart(self, chart: ChartConfig, 
                         data: pd.DataFrame) -> tuple[str, Dict]:
        """Create pie chart"""
        # Use latest values for pie chart
        latest_values = data[chart.metrics].iloc[-1] if len(data) > 0 else {}
        
        fig = go.Figure(data=[go.Pie(
            labels=[metric.replace('_', ' ').title() for metric in chart.metrics],
            values=[latest_values.get(metric, 0) for metric in chart.metrics],
            hole=0.3
        )])
        
        fig.update_layout(
            title=chart.title,
            height=chart.height,
            template="plotly_white"
        )
        
        chart_html = fig.to_html(include_plotlyjs=False, div_id=chart.chart_id)
        chart_config = {
            "type": "pie",
            "metrics": chart.metrics,
            "total_value": sum(latest_values.get(metric, 0) for metric in chart.metrics)
        }
        
        return chart_html, chart_config
    
    def _create_gauge_chart(self, chart: ChartConfig, 
                           data: pd.DataFrame) -> tuple[str, Dict]:
        """Create gauge chart"""
        # Use the first metric for gauge
        metric = chart.metrics[0] if chart.metrics else "value"
        current_value = data[metric].iloc[-1] if len(data) > 0 and metric in data.columns else 0
        max_value = data[metric].max() if len(data) > 0 and metric in data.columns else 100
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"{metric.replace('_', ' ').title()}"},
            delta={'reference': max_value * 0.8},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': "lightgray"},
                    {'range': [max_value * 0.5, max_value * 0.8], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(
            title=chart.title,
            height=chart.height,
            template="plotly_white"
        )
        
        chart_html = fig.to_html(include_plotlyjs=False, div_id=chart.chart_id)
        chart_config = {
            "type": "gauge",
            "current_value": current_value,
            "max_value": max_value
        }
        
        return chart_html, chart_config
    
    def _create_table_chart(self, chart: ChartConfig, 
                           data: pd.DataFrame) -> tuple[str, Dict]:
        """Create table chart"""
        # Show latest 20 rows
        table_data = data.tail(20)[['timestamp'] + chart.metrics]
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[col.replace('_', ' ').title() for col in table_data.columns],
                fill_color='paleturquoise',
                align='left'
            ),
            cells=dict(
                values=[table_data[col] for col in table_data.columns],
                fill_color='lavender',
                align='left'
            )
        )])
        
        fig.update_layout(
            title=chart.title,
            height=chart.height
        )
        
        chart_html = fig.to_html(include_plotlyjs=False, div_id=chart.chart_id)
        chart_config = {
            "type": "table",
            "rows": len(table_data),
            "columns": len(table_data.columns)
        }
        
        return chart_html, chart_config
    
    def _create_metric_display(self, chart: ChartConfig, 
                              data: pd.DataFrame) -> tuple[str, Dict]:
        """Create metric display (KPI card)"""
        metric = chart.metrics[0] if chart.metrics else "value"
        
        if len(data) > 0 and metric in data.columns:
            current_value = data[metric].iloc[-1]
            previous_value = data[metric].iloc[-2] if len(data) > 1 else current_value
            change = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
        else:
            current_value = 0
            change = 0
        
        # Create HTML for metric card
        change_color = "green" if change >= 0 else "red"
        change_icon = "↑" if change >= 0 else "↓"
        
        metric_html = f"""
        <div class="metric-card" style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; height: {chart.height}px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">{chart.title}</h4>
            <div style="font-size: 2.5em; font-weight: bold; color: #2c3e50; margin: 10px 0;">
                {current_value:.2f}
            </div>
            <div style="color: {change_color}; font-size: 1.2em;">
                {change_icon} {abs(change):.1f}%
            </div>
            <div style="color: #7f8c8d; font-size: 0.9em; margin-top: 5px;">
                vs previous period
            </div>
        </div>
        """
        
        chart_config = {
            "type": "metric",
            "current_value": current_value,
            "change_percent": change
        }
        
        return metric_html, chart_config
    
    def _render_dashboard_template(self, dashboard: DashboardConfig, 
                                 charts_data: List[Dict]) -> str:
        """Render dashboard template"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ dashboard.name }} - Ainflue Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
        }
        .chart-container {
            margin-bottom: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-card {
            height: 100%;
        }
        .dashboard-footer {
            margin-top: 40px;
            padding: 20px 0;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }
    </style>
</head>
<body style="background-color: #f8f9fa;">
    <div class="dashboard-header">
        <div class="container">
            <h1>{{ dashboard.name }}</h1>
            <p class="lead">{{ dashboard.description }}</p>
            <small>Last updated: {{ last_updated }}</small>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            {% for chart in charts_data %}
            <div class="col-md-{{ chart.width }} mb-4">
                <div class="chart-container">
                    <h5>{{ chart.title }}</h5>
                    {{ chart.html|safe }}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="dashboard-footer">
        <div class="container">
            <p>Generated by Ainflue Distribution Platform | Auto-refresh: {{ dashboard.refresh_rate }}s</p>
        </div>
    </div>
    
    {% if dashboard.auto_refresh %}
    <script>
        // Auto-refresh dashboard
        setTimeout(function() {
            location.reload();
        }, {{ dashboard.refresh_rate * 1000 }});
    </script>
    {% endif %}
</body>
</html>
        """
        
        template = Template(template_content)
        return template.render(
            dashboard=dashboard,
            charts_data=charts_data,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    async def export_dashboard_data(self, dashboard_id: str, 
                                  format: str = "json") -> str:
        """
        Export dashboard data
        
        Args:
            dashboard_id: Dashboard ID
            format: Export format (json, csv, excel)
            
        Returns:
            str: Export file path
        """
        try:
            if dashboard_id not in self.dashboards:
                logger.error(f"Dashboard not found: {dashboard_id}")
                return ""
            
            dashboard = self.dashboards[dashboard_id]
            export_data = {
                "dashboard": {
                    "id": dashboard.dashboard_id,
                    "name": dashboard.name,
                    "description": dashboard.description,
                    "exported_at": datetime.now().isoformat()
                },
                "charts": []
            }
            
            # Collect data from all charts
            for chart in dashboard.charts:
                data = await self._fetch_data_from_source(chart.data_source, chart.metrics)
                chart_export = {
                    "chart_id": chart.chart_id,
                    "title": chart.title,
                    "type": chart.chart_type,
                    "metrics": chart.metrics,
                    "data": data.to_dict('records') if not data.empty else []
                }
                export_data["charts"].append(chart_export)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == "json":
                filename = f"{dashboard_id}_export_{timestamp}.json"
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
            
            elif format == "csv":
                # Export each chart as separate CSV
                filename = f"{dashboard_id}_export_{timestamp}.zip"
                filepath = os.path.join(self.output_dir, filename)
                # Implementation would create ZIP with multiple CSV files
                
            logger.info(f"Exported dashboard data: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {str(e)}")
            return ""
    
    def update_dashboard(self, dashboard_id: str, 
                        updates: Dict[str, Any]) -> bool:
        """
        Update dashboard configuration
        
        Args:
            dashboard_id: Dashboard ID
            updates: Configuration updates
            
        Returns:
            bool: Success status
        """
        try:
            if dashboard_id not in self.dashboards:
                logger.error(f"Dashboard not found: {dashboard_id}")
                return False
            
            dashboard = self.dashboards[dashboard_id]
            
            # Update allowed fields
            allowed_updates = ['name', 'description', 'theme', 'refresh_rate', 'auto_refresh']
            for field, value in updates.items():
                if field in allowed_updates:
                    setattr(dashboard, field, value)
            
            dashboard.last_updated = datetime.now()
            
            logger.info(f"Updated dashboard: {dashboard_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {str(e)}")
            return False
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete dashboard
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            bool: Success status
        """
        try:
            if dashboard_id in self.dashboards:
                del self.dashboards[dashboard_id]
                logger.info(f"Deleted dashboard: {dashboard_id}")
                return True
            else:
                logger.warning(f"Dashboard not found: {dashboard_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting dashboard: {str(e)}")
            return False
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """
        List all dashboards
        
        Returns:
            List[Dict[str, Any]]: Dashboard summaries
        """
        try:
            dashboards_list = []
            
            for dashboard_id, dashboard in self.dashboards.items():
                summary = {
                    "id": dashboard_id,
                    "name": dashboard.name,
                    "description": dashboard.description,
                    "theme": dashboard.theme,
                    "charts_count": len(dashboard.charts),
                    "created_date": dashboard.created_date.isoformat(),
                    "last_updated": dashboard.last_updated.isoformat(),
                    "is_public": dashboard.is_public
                }
                dashboards_list.append(summary)
            
            return dashboards_list
            
        except Exception as e:
            logger.error(f"Error listing dashboards: {str(e)}")
            return []

# Usage example
async def main() -> None:
    """Example usage of DashboardGenerator"""
    # Initialize dashboard generator
    generator = DashboardGenerator()
    
    # Register data source
    generator.register_data_source("analytics", {
        "type": "database",
        "connection": "postgresql://localhost/analytics"
    })
    
    # Create chart configurations
    engagement_chart = ChartConfig(
        chart_id="engagement_trend",
        title="Engagement Rate Trend",
        chart_type="line",
        data_source="analytics",
        metrics=["engagement_rate"],
        width=6,
        height=400
    )
    
    reach_chart = ChartConfig(
        chart_id="reach_metrics",
        title="Reach Metrics",
        chart_type="bar",
        data_source="analytics",
        metrics=["reach", "impressions"],
        width=6,
        height=400
    )
    
    kpi_chart = ChartConfig(
        chart_id="conversion_kpi",
        title="Conversions",
        chart_type="metric",
        data_source="analytics",
        metrics=["conversions"],
        width=3,
        height=200
    )
    
    # Create dashboard
    dashboard_config = DashboardConfig(
        dashboard_id="main_analytics",
        name="Main Analytics Dashboard",
        description="Overview of key performance metrics",
        theme="light",
        charts=[engagement_chart, reach_chart, kpi_chart]
    )
    
    generator.create_dashboard(dashboard_config)
    
    # Generate HTML dashboard
    html_file = await generator.generate_dashboard_html(
        "main_analytics", 
        "main_analytics.html"
    )
    print(f"Generated dashboard: {html_file}")
    
    # Export data
    export_file = await generator.export_dashboard_data("main_analytics", "json")
    print(f"Exported data: {export_file}")

if __name__ == "__main__":
    asyncio.run(main())