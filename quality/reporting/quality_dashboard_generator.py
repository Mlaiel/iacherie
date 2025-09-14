"""
Quality Dashboard Generator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Quality Dashboard Generator - Ainflue Quality Platform
===================================================

Enterprise-grade quality dashboard generation and visualization system.
Demonstrates Full-Stack + DevOps + Backend Senior + Data Visualization expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import base64
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import aiohttp
import aiofiles
import jinja2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from io import BytesIO
import sqlite3
from collections import defaultdict, deque
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardType(Enum):
    """Types of quality dashboards"""
    EXECUTIVE = "executive"  # High-level overview for executives
    TECHNICAL = "technical"  # Detailed technical metrics
    TEAM = "team"  # Team-focused metrics and goals
    SECURITY = "security"  # Security-focused dashboard
    PERFORMANCE = "performance"  # Performance metrics focus
    COMPLIANCE = "compliance"  # Compliance status dashboard
    REALTIME = "realtime"  # Real-time monitoring dashboard


class MetricCategory(Enum):
    """Categories of quality metrics"""
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    TESTING = "testing"
    COMPLIANCE = "compliance"
    TECHNICAL_DEBT = "technical_debt"
    MAINTAINABILITY = "maintainability"
    COVERAGE = "coverage"


class ChartType(Enum):
    """Types of charts for visualization"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TREEMAP = "treemap"
    SCATTER_PLOT = "scatter_plot"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    RADAR_CHART = "radar_chart"


@dataclass
class QualityMetric:
    """Individual quality metric data point"""
    name: str
    value: Union[float, int, str]
    category: MetricCategory
    timestamp: datetime
    unit: str = ""
    target: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    trend: str = "stable"  # "improving", "degrading", "stable"
    description: str = ""


@dataclass
class DashboardWidget:
    """Widget configuration for dashboard"""
    widget_id: str
    title: str
    chart_type: ChartType
    metrics: List[QualityMetric]
    width: int = 6  # Bootstrap grid width (1-12)
    height: int = 400  # Height in pixels
    refresh_interval: int = 300  # Refresh interval in seconds
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    dashboard_id: str
    title: str
    description: str
    dashboard_type: DashboardType
    widgets: List[DashboardWidget]
    auto_refresh: bool = True
    refresh_interval: int = 300
    theme: str = "light"  # "light", "dark"
    layout: str = "grid"  # "grid", "masonry"


class QualityDashboardGenerator:
    """
    Enterprise quality dashboard generator
    
    Demonstrates expertise in:
    - Full-Stack: Frontend dashboard generation with interactive visualizations
    - DevOps: Real-time monitoring dashboards and alerting
    - Backend Senior: Data aggregation and API integration
    - Data Visualization: Advanced charts and business intelligence
    """
    
    def __init__(self, data_source_path -> None: Optional[str] = None) -> None:
        self.data_source_path = data_source_path
        self.metric_store = {}
        self.dashboard_configs = {}
        self.template_env = None
        
        # Initialize directories
        self.dashboards_dir = Path("reports/dashboards")
        self.templates_dir = Path("templates/dashboards")
        self.static_dir = Path("static/dashboards")
        
        for directory in [self.dashboards_dir, self.templates_dir, self.static_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize template environment
        self._setup_template_environment()
        
        # Create default dashboard templates
        asyncio.create_task(self._create_default_templates())
        
        logger.info("QualityDashboardGenerator initialized")
    
    def _setup_template_environment(self) -> None:
        """Setup Jinja2 template environment (Full-Stack expertise)"""
        loader = jinja2.FileSystemLoader(str(self.templates_dir))
        self.template_env = jinja2.Environment(
            loader=loader,
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.template_env.filters['format_number'] = self._format_number
        self.template_env.filters['format_percentage'] = self._format_percentage
        self.template_env.filters['format_duration'] = self._format_duration
        self.template_env.filters['trend_icon'] = self._trend_icon
        self.template_env.filters['status_color'] = self._status_color
    
    def _format_number(self, value: Union[float, int]) -> str:
        """Format number for display"""
        if isinstance(value, (int, float)):
            if value >= 1000000:
                return f"{value/1000000:.1f}M"
            elif value >= 1000:
                return f"{value/1000:.1f}K"
            else:
                return f"{value:.1f}"
        return str(value)
    
    def _format_percentage(self, value: Union[float, int]) -> str:
        """Format percentage for display"""
        return f"{value:.1f}%" if isinstance(value, (int, float)) else str(value)
    
    def _format_duration(self, seconds: Union[float, int]) -> str:
        """Format duration for display"""
        if seconds >= 3600:
            return f"{seconds/3600:.1f}h"
        elif seconds >= 60:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds:.1f}s"
    
    def _trend_icon(self, trend: str) -> str:
        """Get trend icon"""
        icons = {
            "improving": "📈",
            "degrading": "📉",
            "stable": "➡️"
        }
        return icons.get(trend, "➡️")
    
    def _status_color(self, value: float, warning: float = None, critical: float = None) -> str:
        """Get status color based on thresholds"""
        if critical and value <= critical:
            return "danger"
        elif warning and value <= warning:
            return "warning"
        else:
            return "success"
    
    async def _create_default_templates(self) -> None:
        """Create default dashboard templates (Full-Stack expertise)"""
        # Main dashboard template
        main_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ dashboard.title }} - Ainflue Quality Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2c3e50;
        }
        .metric-label {
            color: #7f8c8d;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        .trend-positive { color: #27ae60; }
        .trend-negative { color: #e74c3c; }
        .trend-stable { color: #f39c12; }
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-success { background-color: #27ae60; }
        .status-warning { background-color: #f39c12; }
        .status-danger { background-color: #e74c3c; }
        .sidebar {
            background: #2c3e50;
            min-height: 100vh;
            padding: 2rem 1rem;
        }
        .sidebar h5 {
            color: white;
            margin-bottom: 1rem;
        }
        .nav-link {
            color: #bdc3c7;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            border-radius: 5px;
            transition: all 0.2s;
        }
        .nav-link:hover, .nav-link.active {
            background: #34495e;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar">
                <h5><i class="fas fa-chart-line"></i> Quality Dashboard</h5>
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link active" href="#overview">
                            <i class="fas fa-tachometer-alt"></i> Overview
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#code-quality">
                            <i class="fas fa-code"></i> Code Quality
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#security">
                            <i class="fas fa-shield-alt"></i> Security
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#performance">
                            <i class="fas fa-rocket"></i> Performance
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#testing">
                            <i class="fas fa-vial"></i> Testing
                        </a>
                    </li>
                </ul>
            </nav>
            
            <main class="col-md-10">
                <div class="dashboard-header">
                    <div class="container">
                        <h1>{{ dashboard.title }}</h1>
                        <p class="mb-0">{{ dashboard.description }}</p>
                        <small>Last updated: {{ timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</small>
                    </div>
                </div>
                
                <div class="container">
                    {{ content }}
                </div>
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh functionality
        {% if dashboard.auto_refresh %}
        setTimeout(function() {
            location.reload();
        }, {{ dashboard.refresh_interval * 1000 }});
        {% endif %}
        
        // Chart update functionality
        function updateCharts() {
            // This would be connected to a real-time data source
            console.log('Updating charts...');
        }
        
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    </script>
</body>
</html>
        """
        
        await self._save_template("dashboard_main.html", main_template)
        
        # Widget templates
        metric_card_template = """
<div class="col-md-{{ widget.width }}">
    <div class="metric-card">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="metric-label">{{ widget.title }}</h6>
            <span class="trend-{{ metric.trend }}">{{ metric.trend | trend_icon }}</span>
        </div>
        <div class="metric-value">{{ metric.value | format_number }}</div>
        {% if metric.target %}
        <div class="mt-2">
            <small class="text-muted">Target: {{ metric.target | format_number }}</small>
        </div>
        {% endif %}
    </div>
</div>
        """
        
        await self._save_template("metric_card.html", metric_card_template)
        
        logger.info("Default dashboard templates created")
    
    async def _save_template(self, filename -> None: str, content -> None: str) -> None:
        """Save template to file"""
        template_path = self.templates_dir / filename
        async with aiofiles.open(template_path, 'w') as f:
            await f.write(content)
    
    async def collect_metrics(self, sources: List[str] = None) -> Dict[str, List[QualityMetric]]:
        """
        Collect quality metrics from various sources
        
        Backend expertise: Data aggregation from multiple sources
        DevOps expertise: Integration with monitoring systems
        """
        logger.info("Collecting quality metrics from sources")
        
        metrics = {category.value: [] for category in MetricCategory}
        
        # Collect from different sources
        if not sources:
            sources = ["code_analysis", "test_results", "security_scan", "performance_monitoring"]
        
        for source in sources:
            try:
                source_metrics = await self._collect_from_source(source)
                for metric in source_metrics:
                    metrics[metric.category.value].append(metric)
            except Exception as e:
                logger.warning(f"Failed to collect from source {source}: {e}")
        
        # Store metrics for later use
        self.metric_store.update(metrics)
        
        logger.info(f"Collected {sum(len(m) for m in metrics.values())} metrics")
        return metrics
    
    async def _collect_from_source(self, source: str) -> List[QualityMetric]:
        """Collect metrics from specific source"""
        metrics = []
        
        if source == "code_analysis":
            metrics.extend(await self._collect_code_metrics())
        elif source == "test_results":
            metrics.extend(await self._collect_test_metrics())
        elif source == "security_scan":
            metrics.extend(await self._collect_security_metrics())
        elif source == "performance_monitoring":
            metrics.extend(await self._collect_performance_metrics())
        
        return metrics
    
    async def _collect_code_metrics(self) -> List[QualityMetric]:
        """Collect code quality metrics (Backend expertise)"""
        metrics = []
        
        # Simulate or collect real code metrics
        # In a real implementation, this would integrate with tools like SonarQube, CodeClimate, etc.
        
        metrics.append(QualityMetric(
            name="Code Coverage",
            value=85.2,
            category=MetricCategory.CODE_QUALITY,
            timestamp=datetime.now(),
            unit="%",
            target=90.0,
            threshold_warning=70.0,
            threshold_critical=50.0,
            trend="improving",
            description="Percentage of code covered by automated tests"
        ))
        
        metrics.append(QualityMetric(
            name="Cyclomatic Complexity",
            value=8.5,
            category=MetricCategory.CODE_QUALITY,
            timestamp=datetime.now(),
            unit="avg",
            target=5.0,
            threshold_warning=10.0,
            threshold_critical=15.0,
            trend="stable",
            description="Average cyclomatic complexity across codebase"
        ))
        
        metrics.append(QualityMetric(
            name="Technical Debt",
            value=42.5,
            category=MetricCategory.TECHNICAL_DEBT,
            timestamp=datetime.now(),
            unit="hours",
            target=20.0,
            threshold_warning=50.0,
            threshold_critical=100.0,
            trend="degrading",
            description="Estimated hours to resolve technical debt"
        ))
        
        metrics.append(QualityMetric(
            name="Maintainability Index",
            value=76.8,
            category=MetricCategory.MAINTAINABILITY,
            timestamp=datetime.now(),
            unit="score",
            target=80.0,
            threshold_warning=60.0,
            threshold_critical=40.0,
            trend="improving",
            description="Overall maintainability score (0-100)"
        ))
        
        return metrics
    
    async def _collect_test_metrics(self) -> List[QualityMetric]:
        """Collect testing metrics (DevOps + Backend expertise)"""
        metrics = []
        
        metrics.append(QualityMetric(
            name="Test Pass Rate",
            value=94.7,
            category=MetricCategory.TESTING,
            timestamp=datetime.now(),
            unit="%",
            target=95.0,
            threshold_warning=90.0,
            threshold_critical=80.0,
            trend="stable",
            description="Percentage of tests passing in latest run"
        ))
        
        metrics.append(QualityMetric(
            name="Test Execution Time",
            value=245,
            category=MetricCategory.TESTING,
            timestamp=datetime.now(),
            unit="seconds",
            target=180,
            threshold_warning=300,
            threshold_critical=600,
            trend="degrading",
            description="Time taken to execute full test suite"
        ))
        
        metrics.append(QualityMetric(
            name="Flaky Tests",
            value=3,
            category=MetricCategory.TESTING,
            timestamp=datetime.now(),
            unit="count",
            target=0,
            threshold_warning=5,
            threshold_critical=10,
            trend="improving",
            description="Number of tests with inconsistent results"
        ))
        
        return metrics
    
    async def _collect_security_metrics(self) -> List[QualityMetric]:
        """Collect security metrics (Security expertise)"""
        metrics = []
        
        metrics.append(QualityMetric(
            name="Security Score",
            value=88.2,
            category=MetricCategory.SECURITY,
            timestamp=datetime.now(),
            unit="score",
            target=95.0,
            threshold_warning=80.0,
            threshold_critical=70.0,
            trend="improving",
            description="Overall security posture score"
        ))
        
        metrics.append(QualityMetric(
            name="Critical Vulnerabilities",
            value=0,
            category=MetricCategory.SECURITY,
            timestamp=datetime.now(),
            unit="count",
            target=0,
            threshold_warning=1,
            threshold_critical=3,
            trend="stable",
            description="Number of critical security vulnerabilities"
        ))
        
        metrics.append(QualityMetric(
            name="Dependency Vulnerabilities",
            value=2,
            category=MetricCategory.SECURITY,
            timestamp=datetime.now(),
            unit="count",
            target=0,
            threshold_warning=5,
            threshold_critical=10,
            trend="improving",
            description="Vulnerabilities in third-party dependencies"
        ))
        
        return metrics
    
    async def _collect_performance_metrics(self) -> List[QualityMetric]:
        """Collect performance metrics (DevOps + Performance expertise)"""
        metrics = []
        
        metrics.append(QualityMetric(
            name="Response Time",
            value=124,
            category=MetricCategory.PERFORMANCE,
            timestamp=datetime.now(),
            unit="ms",
            target=100,
            threshold_warning=200,
            threshold_critical=500,
            trend="stable",
            description="Average API response time"
        ))
        
        metrics.append(QualityMetric(
            name="Throughput",
            value=1250,
            category=MetricCategory.PERFORMANCE,
            timestamp=datetime.now(),
            unit="req/min",
            target=1000,
            threshold_warning=800,
            threshold_critical=500,
            trend="improving",
            description="Requests processed per minute"
        ))
        
        metrics.append(QualityMetric(
            name="Error Rate",
            value=0.8,
            category=MetricCategory.PERFORMANCE,
            timestamp=datetime.now(),
            unit="%",
            target=0.5,
            threshold_warning=2.0,
            threshold_critical=5.0,
            trend="stable",
            description="Percentage of failed requests"
        ))
        
        return metrics
    
    async def generate_dashboard(self, dashboard_type: DashboardType = DashboardType.EXECUTIVE) -> str:
        """
        Generate comprehensive quality dashboard
        
        Full-Stack expertise: Interactive dashboard generation
        Data Visualization expertise: Advanced charts and insights
        """
        logger.info(f"Generating {dashboard_type.value} dashboard")
        
        # Collect latest metrics
        metrics = await self.collect_metrics()
        
        # Create dashboard configuration
        config = await self._create_dashboard_config(dashboard_type, metrics)
        
        # Generate charts
        charts = await self._generate_charts(config)
        
        # Render dashboard HTML
        dashboard_html = await self._render_dashboard(config, charts, metrics)
        
        # Save dashboard
        dashboard_path = await self._save_dashboard(dashboard_html, dashboard_type.value)
        
        logger.info(f"Dashboard generated: {dashboard_path}")
        return dashboard_path
    
    async def _create_dashboard_config(self, dashboard_type: DashboardType, 
                                     metrics: Dict[str, List[QualityMetric]]) -> DashboardConfig:
        """Create dashboard configuration based on type"""
        
        if dashboard_type == DashboardType.EXECUTIVE:
            return DashboardConfig(
                dashboard_id="executive_dashboard",
                title="Executive Quality Dashboard",
                description="High-level quality metrics and KPIs for executive oversight",
                dashboard_type=dashboard_type,
                widgets=[
                    DashboardWidget(
                        widget_id="overall_score",
                        title="Overall Quality Score",
                        chart_type=ChartType.GAUGE,
                        metrics=self._get_metrics_by_category(metrics, [MetricCategory.CODE_QUALITY]),
                        width=6
                    ),
                    DashboardWidget(
                        widget_id="security_status",
                        title="Security Status",
                        chart_type=ChartType.GAUGE,
                        metrics=self._get_metrics_by_category(metrics, [MetricCategory.SECURITY]),
                        width=6
                    ),
                    DashboardWidget(
                        widget_id="quality_trends",
                        title="Quality Trends",
                        chart_type=ChartType.LINE_CHART,
                        metrics=self._get_metrics_by_category(metrics, [MetricCategory.CODE_QUALITY]),
                        width=12
                    )
                ]
            )
        
        elif dashboard_type == DashboardType.TECHNICAL:
            return DashboardConfig(
                dashboard_id="technical_dashboard",
                title="Technical Quality Dashboard",
                description="Detailed technical metrics for development teams",
                dashboard_type=dashboard_type,
                widgets=[
                    DashboardWidget(
                        widget_id="code_coverage",
                        title="Code Coverage",
                        chart_type=ChartType.BAR_CHART,
                        metrics=self._get_metrics_by_category(metrics, [MetricCategory.COVERAGE]),
                        width=6
                    ),
                    DashboardWidget(
                        widget_id="technical_debt",
                        title="Technical Debt",
                        chart_type=ChartType.TREEMAP,
                        metrics=self._get_metrics_by_category(metrics, [MetricCategory.TECHNICAL_DEBT]),
                        width=6
                    ),
                    DashboardWidget(
                        widget_id="complexity_heatmap",
                        title="Complexity Heatmap",
                        chart_type=ChartType.HEATMAP,
                        metrics=self._get_metrics_by_category(metrics, [MetricCategory.CODE_QUALITY]),
                        width=12
                    )
                ]
            )
        
        # Default configuration
        return DashboardConfig(
            dashboard_id=f"{dashboard_type.value}_dashboard",
            title=f"{dashboard_type.value.title()} Quality Dashboard",
            description=f"Quality dashboard for {dashboard_type.value} view",
            dashboard_type=dashboard_type,
            widgets=[]
        )
    
    def _get_metrics_by_category(self, metrics: Dict[str, List[QualityMetric]], 
                                categories: List[MetricCategory]) -> List[QualityMetric]:
        """Get metrics filtered by categories"""
        result = []
        for category in categories:
            result.extend(metrics.get(category.value, []))
        return result
    
    async def _generate_charts(self, config: DashboardConfig) -> Dict[str, str]:
        """
        Generate interactive charts using Plotly
        
        Data Visualization expertise: Advanced charting and visualization
        """
        charts = {}
        
        for widget in config.widgets:
            try:
                if widget.chart_type == ChartType.GAUGE:
                    chart_html = await self._create_gauge_chart(widget)
                elif widget.chart_type == ChartType.LINE_CHART:
                    chart_html = await self._create_line_chart(widget)
                elif widget.chart_type == ChartType.BAR_CHART:
                    chart_html = await self._create_bar_chart(widget)
                elif widget.chart_type == ChartType.PIE_CHART:
                    chart_html = await self._create_pie_chart(widget)
                elif widget.chart_type == ChartType.HEATMAP:
                    chart_html = await self._create_heatmap(widget)
                elif widget.chart_type == ChartType.TREEMAP:
                    chart_html = await self._create_treemap(widget)
                else:
                    chart_html = await self._create_default_chart(widget)
                
                charts[widget.widget_id] = chart_html
                
            except Exception as e:
                logger.error(f"Failed to generate chart for widget {widget.widget_id}: {e}")
                charts[widget.widget_id] = f"<div class='alert alert-danger'>Error generating chart: {e}</div>"
        
        return charts
    
    async def _create_gauge_chart(self, widget: DashboardWidget) -> str:
        """Create gauge chart for metrics (Data Visualization expertise)"""
        if not widget.metrics:
            return "<div class='alert alert-warning'>No data available</div>"
        
        metric = widget.metrics[0]  # Use first metric for gauge
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=metric.value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': metric.name},
            delta={'reference': metric.target if metric.target else metric.value * 0.8},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, metric.threshold_critical or 40], 'color': "lightgray"},
                    {'range': [metric.threshold_critical or 40, metric.threshold_warning or 70], 'color': "yellow"},
                    {'range': [metric.threshold_warning or 70, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': metric.target or 90
                }
            }
        ))
        
        fig.update_layout(
            height=widget.height,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    async def _create_line_chart(self, widget: DashboardWidget) -> str:
        """Create line chart for trend analysis (Data Visualization expertise)"""
        if not widget.metrics:
            return "<div class='alert alert-warning'>No data available</div>"
        
        # Generate sample trend data (in real implementation, this would come from historical data)
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        
        fig = go.Figure()
        
        for metric in widget.metrics[:5]:  # Limit to 5 metrics for readability
            # Generate sample trend data
            base_value = metric.value
            trend_data = np.random.normal(base_value, base_value * 0.1, len(dates))
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=trend_data,
                mode='lines+markers',
                name=metric.name,
                line=dict(width=2),
                marker=dict(size=4)
            ))
        
        fig.update_layout(
            title=widget.title,
            xaxis_title="Date",
            yaxis_title="Value",
            height=widget.height,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    async def _create_bar_chart(self, widget: DashboardWidget) -> str:
        """Create bar chart for metric comparison (Data Visualization expertise)"""
        if not widget.metrics:
            return "<div class='alert alert-warning'>No data available</div>"
        
        metric_names = [m.name for m in widget.metrics]
        metric_values = [m.value for m in widget.metrics]
        
        # Color bars based on performance against targets
        colors = []
        for metric in widget.metrics:
            if metric.target:
                if metric.value >= metric.target:
                    colors.append('green')
                elif metric.threshold_warning and metric.value >= metric.threshold_warning:
                    colors.append('orange')
                else:
                    colors.append('red')
            else:
                colors.append('blue')
        
        fig = go.Figure(data=[
            go.Bar(
                x=metric_names,
                y=metric_values,
                marker_color=colors,
                text=[f"{v:.1f}" for v in metric_values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title=widget.title,
            xaxis_title="Metrics",
            yaxis_title="Value",
            height=widget.height,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    async def _create_pie_chart(self, widget: DashboardWidget) -> str:
        """Create pie chart for distribution visualization"""
        if not widget.metrics:
            return "<div class='alert alert-warning'>No data available</div>"
        
        labels = [m.name for m in widget.metrics]
        values = [m.value for m in widget.metrics]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title=widget.title,
            height=widget.height,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    async def _create_heatmap(self, widget: DashboardWidget) -> str:
        """Create heatmap for correlation analysis"""
        if len(widget.metrics) < 4:
            return "<div class='alert alert-warning'>Insufficient data for heatmap</div>"
        
        # Generate sample correlation matrix
        metric_names = [m.name for m in widget.metrics[:10]]
        correlation_matrix = np.random.rand(len(metric_names), len(metric_names))
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=metric_names,
            y=metric_names,
            colorscale='RdYlGn',
            zmid=0
        ))
        
        fig.update_layout(
            title=widget.title,
            height=widget.height,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    async def _create_treemap(self, widget: DashboardWidget) -> str:
        """Create treemap for hierarchical data visualization"""
        if not widget.metrics:
            return "<div class='alert alert-warning'>No data available</div>"
        
        labels = [m.name for m in widget.metrics]
        values = [abs(m.value) for m in widget.metrics]  # Use absolute values
        parents = [""] * len(labels)  # Root level items
        
        fig = go.Figure(go.Treemap(
            labels=labels,
            values=values,
            parents=parents,
            textinfo="label+value",
            maxdepth=2
        ))
        
        fig.update_layout(
            title=widget.title,
            height=widget.height,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    async def _create_default_chart(self, widget: DashboardWidget) -> str:
        """Create default chart when specific type is not implemented"""
        return f"""
        <div class="alert alert-info">
            <h5>{widget.title}</h5>
            <p>Chart type {widget.chart_type.value} not yet implemented.</p>
            <ul>
                {' '.join([f"<li>{m.name}: {m.value} {m.unit}</li>" for m in widget.metrics[:5]])}
            </ul>
        </div>
        """
    
    async def _render_dashboard(self, config: DashboardConfig, charts: Dict[str, str], 
                              metrics: Dict[str, List[QualityMetric]]) -> str:
        """
        Render final dashboard HTML
        
        Full-Stack expertise: Template rendering and responsive design
        """
        # Create content sections
        content_sections = []
        
        # Overview section with key metrics
        overview_metrics = []
        for category, metric_list in metrics.items():
            if metric_list:
                overview_metrics.extend(metric_list[:2])  # Top 2 metrics per category
        
        content_sections.append(self._create_overview_section(overview_metrics))
        
        # Widget sections
        for widget in config.widgets:
            chart_html = charts.get(widget.widget_id, "Chart not available")
            section_html = f"""
            <div class="chart-container">
                <h4>{widget.title}</h4>
                {chart_html}
            </div>
            """
            content_sections.append(section_html)
        
        # Summary statistics
        content_sections.append(self._create_summary_section(metrics))
        
        # Combine all content
        content = "\n".join(content_sections)
        
        # Render main template
        try:
            template = self.template_env.get_template("dashboard_main.html")
            dashboard_html = template.render(
                dashboard=config,
                content=content,
                timestamp=datetime.now(),
                metrics=metrics
            )
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            # Fallback to simple HTML
            dashboard_html = self._create_fallback_dashboard(config, content)
        
        return dashboard_html
    
    def _create_overview_section(self, metrics: List[QualityMetric]) -> str:
        """Create overview section with key metrics cards"""
        cards_html = []
        
        for metric in metrics[:8]:  # Show top 8 metrics
            status_class = self._get_status_class(metric)
            trend_class = f"trend-{metric.trend.replace('improving', 'positive').replace('degrading', 'negative')}"
            
            card_html = f"""
            <div class="col-md-3 mb-3">
                <div class="metric-card">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="metric-label">{metric.name}</h6>
                        <span class="{trend_class}">{self._trend_icon(metric.trend)}</span>
                    </div>
                    <div class="metric-value {status_class}">{self._format_metric_value(metric)}</div>
                    {f'<small class="text-muted">Target: {metric.target}</small>' if metric.target else ''}
                </div>
            </div>
            """
            cards_html.append(card_html)
        
        return f"""
        <section id="overview">
            <h3>Quality Overview</h3>
            <div class="row">
                {''.join(cards_html)}
            </div>
        </section>
        """
    
    def _create_summary_section(self, metrics: Dict[str, List[QualityMetric]]) -> str:
        """Create summary statistics section"""
        total_metrics = sum(len(metric_list) for metric_list in metrics.values())
        
        # Calculate summary stats
        all_metrics = []
        for metric_list in metrics.values():
            all_metrics.extend(metric_list)
        
        improving_count = len([m for m in all_metrics if m.trend == "improving"])
        degrading_count = len([m for m in all_metrics if m.trend == "degrading"])
        stable_count = len([m for m in all_metrics if m.trend == "stable"])
        
        return f"""
        <section id="summary" class="mt-5">
            <h3>Summary Statistics</h3>
            <div class="row">
                <div class="col-md-3">
                    <div class="metric-card text-center">
                        <div class="metric-value">{total_metrics}</div>
                        <div class="metric-label">Total Metrics</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card text-center">
                        <div class="metric-value trend-positive">{improving_count}</div>
                        <div class="metric-label">Improving</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card text-center">
                        <div class="metric-value trend-negative">{degrading_count}</div>
                        <div class="metric-label">Degrading</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card text-center">
                        <div class="metric-value trend-stable">{stable_count}</div>
                        <div class="metric-label">Stable</div>
                    </div>
                </div>
            </div>
        </section>
        """
    
    def _get_status_class(self, metric: QualityMetric) -> str:
        """Get CSS class based on metric status"""
        if metric.threshold_critical and metric.value <= metric.threshold_critical:
            return "text-danger"
        elif metric.threshold_warning and metric.value <= metric.threshold_warning:
            return "text-warning"
        else:
            return "text-success"
    
    def _format_metric_value(self, metric: QualityMetric) -> str:
        """Format metric value for display"""
        if metric.unit == "%":
            return f"{metric.value:.1f}%"
        elif metric.unit in ["seconds", "ms"]:
            return self._format_duration(metric.value)
        else:
            return f"{self._format_number(metric.value)} {metric.unit}"
    
    def _create_fallback_dashboard(self, config: DashboardConfig, content: str) -> str:
        """Create fallback dashboard when template rendering fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{config.title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <div class="container mt-4">
                <h1>{config.title}</h1>
                <p>{config.description}</p>
                {content}
            </div>
        </body>
        </html>
        """
    
    async def _save_dashboard(self, dashboard_html: str, dashboard_type: str) -> str:
        """Save dashboard HTML to file (Backend expertise)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dashboard_type}_dashboard_{timestamp}.html"
        filepath = self.dashboards_dir / filename
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(dashboard_html)
        
        # Also save as latest
        latest_filename = f"{dashboard_type}_dashboard_latest.html"
        latest_filepath = self.dashboards_dir / latest_filename
        
        async with aiofiles.open(latest_filepath, 'w') as f:
            await f.write(dashboard_html)
        
        return str(filepath)
    
    async def generate_real_time_dashboard(self) -> str:
        """Generate real-time monitoring dashboard (DevOps expertise)"""
        logger.info("Generating real-time monitoring dashboard")
        
        # This would integrate with real-time monitoring systems like Grafana, Prometheus, etc.
        realtime_config = DashboardConfig(
            dashboard_id="realtime_dashboard",
            title="Real-Time Quality Monitoring",
            description="Live monitoring of quality metrics and system health",
            dashboard_type=DashboardType.REALTIME,
            auto_refresh=True,
            refresh_interval=30,  # 30 seconds
            widgets=[]
        )
        
        # Collect real-time metrics
        metrics = await self.collect_metrics()
        
        # Generate with real-time features
        charts = await self._generate_charts(realtime_config)
        dashboard_html = await self._render_dashboard(realtime_config, charts, metrics)
        
        # Add real-time JavaScript
        dashboard_html = self._add_realtime_features(dashboard_html)
        
        return await self._save_dashboard(dashboard_html, "realtime")
    
    def _add_realtime_features(self, dashboard_html: str) -> str:
        """Add real-time update features to dashboard"""
        realtime_script = """
        <script>
        // Real-time update functionality
        class RealtimeDashboard {
            constructor() {
                this.updateInterval = 30000; // 30 seconds
                this.startUpdates();
            }
            
            startUpdates() {
                setInterval(() => {
                    this.updateMetrics();
                }, this.updateInterval);
            }
            
            async updateMetrics() {
                try {
                    // In a real implementation, this would fetch from an API
                    console.log('Updating real-time metrics...');
                    
                    // Update metric cards
                    document.querySelectorAll('.metric-value').forEach(element => {
                        // Simulate metric updates
                        const currentValue = parseFloat(element.textContent);
                        if (!isNaN(currentValue)) {
                            const variation = (Math.random() - 0.5) * 0.1; // ±5% variation
                            const newValue = currentValue * (1 + variation);
                            element.textContent = newValue.toFixed(1);
                        }
                    });
                    
                    // Update timestamp
                    const timestampElement = document.querySelector('.last-updated');
                    if (timestampElement) {
                        timestampElement.textContent = `Last updated: ${new Date().toLocaleString()}`;
                    }
                    
                } catch (error) {
                    console.error('Failed to update metrics:', error);
                }
            }
        }
        
        // Initialize real-time dashboard
        document.addEventListener('DOMContentLoaded', function() {
            new RealtimeDashboard();
        });
        </script>
        """
        
        # Insert before closing body tag
        return dashboard_html.replace('</body>', realtime_script + '</body>')


# Global instance
quality_dashboard_generator = QualityDashboardGenerator()


async def generate_executive_dashboard() -> str:
    """Quick executive dashboard generation"""
    return await quality_dashboard_generator.generate_dashboard(DashboardType.EXECUTIVE)


async def generate_technical_dashboard() -> str:
    """Quick technical dashboard generation"""
    return await quality_dashboard_generator.generate_dashboard(DashboardType.TECHNICAL)


async def generate_security_dashboard() -> str:
    """Quick security dashboard generation"""
    return await quality_dashboard_generator.generate_dashboard(DashboardType.SECURITY)


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        # Generate executive dashboard
        dashboard_path = await generate_executive_dashboard()
        print(f"Executive dashboard generated: {dashboard_path}")
        
        # Generate technical dashboard
        tech_dashboard = await generate_technical_dashboard()
        print(f"Technical dashboard generated: {tech_dashboard}")
        
        # Generate real-time dashboard
        realtime_dashboard = await quality_dashboard_generator.generate_real_time_dashboard()
        print(f"Real-time dashboard generated: {realtime_dashboard}")
    
    asyncio.run(main())