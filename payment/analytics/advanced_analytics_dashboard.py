"""🏗️ Advanced Payment Analytics Dashboard
==========================================

Enterprise-grade payment analytics dashboard with real-time monitoring,
performance metrics, advanced visualizations, and comprehensive reporting.

Features:
- Real-time payment monitoring
- Advanced analytics and KPIs
- Interactive dashboards
- Performance optimization insights
- Executive reporting
- Custom alert management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from decimal import Decimal
import numpy as np
import pandas as pd
from pathlib import Path
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import websockets
import json

logger = logging.getLogger(__name__)

Base = declarative_base()


class DashboardType(Enum):
    """Types of dashboards"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CUSTOM = "custom"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TimeRange(Enum):
    """Time range options"""
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"
    QUARTER = "3m"
    YEAR = "1y"
    CUSTOM = "custom"


@dataclass
class DashboardMetric:
    """Dashboard metric definition"""
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    unit: str
    query: str  # SQL query or aggregation function
    refresh_interval: timedelta
    is_active: bool = True
    dashboard_types: List[DashboardType] = field(default_factory=list)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    name: str
    widget_type: str  # chart, table, kpi, gauge, etc.
    metrics: List[str]  # List of metric IDs
    configuration: Dict[str, Any]
    position: Dict[str, int]  # x, y, width, height
    is_visible: bool = True


@dataclass
class Dashboard:
    """Dashboard definition"""
    dashboard_id: str
    name: str
    description: str
    dashboard_type: DashboardType
    widgets: List[DashboardWidget]
    layout: Dict[str, Any]
    permissions: List[str]  # User roles that can access
    is_public: bool = False
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alert:
    """Dashboard alert"""
    alert_id: str
    metric_id: str
    name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    message: str
    is_active: bool = True
    notification_channels: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MetricValue:
    """Metric value with timestamp"""
    metric_id: str
    value: Union[float, int, str]
    timestamp: datetime
    dimensions: Dict[str, Any] = field(default_factory=dict)


class AdvancedPaymentAnalyticsDashboard:
    """Enterprise payment analytics dashboard system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.db_session: Optional[AsyncSession] = None
        
        # Dashboard storage
        self.dashboards: Dict[str, Dashboard] = {}
        self.metrics: Dict[str, DashboardMetric] = {}
        self.alerts: Dict[str, Alert] = {}
        
        # Real-time data
        self.metric_cache: Dict[str, List[MetricValue]] = {}
        self.active_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Analytics settings
        self.data_retention = timedelta(days=config.get('data_retention_days', 90))
        self.real_time_update_interval = timedelta(seconds=config.get('update_interval_seconds', 5))
        self.max_cache_size = config.get('max_cache_size', 10000)
        
        # Background tasks
        self.metrics_collector_task: Optional[asyncio.Task] = None
        self.alert_monitor_task: Optional[asyncio.Task] = None
        self.data_cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize the analytics dashboard system"""
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 6),
                decode_responses=True
            )
            
            # Initialize database connection
            db_config = self.config.get('database', {})
            db_url = f"postgresql+asyncpg://{db_config.get('user')}:{db_config.get('password')}@{db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}"
            engine = create_async_engine(db_url)
            async_session = sessionmaker(engine, class_=AsyncSession)
            self.db_session = async_session()
            
            # Load existing configurations
            await self._load_dashboards()
            await self._load_metrics()
            await self._load_alerts()
            
            # Create default dashboards and metrics
            await self._create_default_configurations()
            
            # Start background tasks
            self.metrics_collector_task = asyncio.create_task(self._collect_metrics_periodically())
            self.alert_monitor_task = asyncio.create_task(self._monitor_alerts_periodically())
            self.data_cleanup_task = asyncio.create_task(self._cleanup_old_data_periodically())
            
            logger.info("Advanced payment analytics dashboard initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics dashboard: {e}")
            raise
    
    async def get_dashboard_data(
        self,
        dashboard_id: str,
        time_range: TimeRange,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                raise ValueError(f"Dashboard not found: {dashboard_id}")
            
            # Calculate time range
            if time_range == TimeRange.CUSTOM:
                if not start_time or not end_time:
                    raise ValueError("Custom time range requires start_time and end_time")
            else:
                end_time = datetime.utcnow()
                start_time = self._calculate_start_time(time_range, end_time)
            
            # Collect data for all dashboard widgets
            dashboard_data = {
                'dashboard_id': dashboard_id,
                'dashboard_name': dashboard.name,
                'dashboard_type': dashboard.dashboard_type.value,
                'time_range': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'range_type': time_range.value
                },
                'widgets': {}
            }
            
            # Process each widget
            for widget in dashboard.widgets:
                if not widget.is_visible:
                    continue
                
                widget_data = await self._get_widget_data(widget, start_time, end_time)
                dashboard_data['widgets'][widget.widget_id] = widget_data
            
            # Add summary statistics
            dashboard_data['summary'] = await self._generate_dashboard_summary(dashboard, start_time, end_time)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    async def get_real_time_metrics(
        self,
        metric_ids: List[str],
        last_update: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get real-time metrics updates"""
        try:
            real_time_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': {}
            }
            
            for metric_id in metric_ids:
                if metric_id not in self.metrics:
                    continue
                
                # Get latest metric values
                metric_values = await self._get_latest_metric_values(metric_id, last_update)
                
                if metric_values:
                    real_time_data['metrics'][metric_id] = {
                        'values': [
                            {
                                'value': val.value,
                                'timestamp': val.timestamp.isoformat(),
                                'dimensions': val.dimensions
                            }
                            for val in metric_values
                        ],
                        'metric_info': {
                            'name': self.metrics[metric_id].name,
                            'type': self.metrics[metric_id].metric_type.value,
                            'unit': self.metrics[metric_id].unit
                        }
                    }
            
            return real_time_data
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {'timestamp': datetime.utcnow().isoformat(), 'metrics': {}}
    
    async def create_custom_dashboard(
        self,
        dashboard_config: Dict[str, Any],
        user_id: str
    ) -> str:
        """Create a custom dashboard"""
        try:
            dashboard_id = f"dashboard_{uuid.uuid4().hex[:8]}"
            
            # Create widgets
            widgets = []
            for widget_config in dashboard_config.get('widgets', []):
                widget = DashboardWidget(
                    widget_id=f"widget_{uuid.uuid4().hex[:8]}",
                    name=widget_config['name'],
                    widget_type=widget_config['type'],
                    metrics=widget_config.get('metrics', []),
                    configuration=widget_config.get('configuration', {}),
                    position=widget_config.get('position', {'x': 0, 'y': 0, 'width': 6, 'height': 4})
                )
                widgets.append(widget)
            
            # Create dashboard
            dashboard = Dashboard(
                dashboard_id=dashboard_id,
                name=dashboard_config['name'],
                description=dashboard_config.get('description', ''),
                dashboard_type=DashboardType(dashboard_config.get('type', 'custom')),
                widgets=widgets,
                layout=dashboard_config.get('layout', {}),
                permissions=dashboard_config.get('permissions', []),
                is_public=dashboard_config.get('is_public', False),
                created_by=user_id
            )
            
            # Store dashboard
            self.dashboards[dashboard_id] = dashboard
            await self._store_dashboard(dashboard)
            
            logger.info(f"Created custom dashboard: {dashboard.name}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create custom dashboard: {e}")
            raise
    
    async def generate_chart(
        self,
        chart_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate interactive chart using Plotly"""
        try:
            chart_type = chart_config['type']
            metric_ids = chart_config['metrics']
            time_range = chart_config.get('time_range', TimeRange.DAY)
            
            # Get data for metrics
            chart_data = {}
            for metric_id in metric_ids:
                if metric_id in self.metrics:
                    values = await self._get_metric_time_series(metric_id, time_range)
                    chart_data[metric_id] = values
            
            # Create chart based on type
            if chart_type == 'line':
                fig = self._create_line_chart(chart_data, chart_config)
            elif chart_type == 'bar':
                fig = self._create_bar_chart(chart_data, chart_config)
            elif chart_type == 'pie':
                fig = self._create_pie_chart(chart_data, chart_config)
            elif chart_type == 'gauge':
                fig = self._create_gauge_chart(chart_data, chart_config)
            elif chart_type == 'heatmap':
                fig = self._create_heatmap_chart(chart_data, chart_config)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            # Convert to JSON for frontend
            chart_json = fig.to_json()
            
            return {
                'chart_id': chart_config.get('chart_id', str(uuid.uuid4())),
                'chart_type': chart_type,
                'chart_data': json.loads(chart_json),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate chart: {e}")
            raise
    
    async def create_alert(self, alert_config: Dict[str, Any]) -> str:
        """Create a new alert"""
        try:
            alert = Alert(
                alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                metric_id=alert_config['metric_id'],
                name=alert_config['name'],
                condition=alert_config['condition'],
                threshold=alert_config['threshold'],
                severity=AlertSeverity(alert_config['severity']),
                message=alert_config['message'],
                notification_channels=alert_config.get('notification_channels', [])
            )
            
            # Validate metric exists
            if alert.metric_id not in self.metrics:
                raise ValueError(f"Metric not found: {alert.metric_id}")
            
            # Store alert
            self.alerts[alert.alert_id] = alert
            await self._store_alert(alert)
            
            logger.info(f"Created alert: {alert.name}")
            return alert.alert_id
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise
    
    async def get_payment_performance_insights(
        self,
        time_range: TimeRange
    ) -> Dict[str, Any]:
        """Generate comprehensive payment performance insights"""
        try:
            end_time = datetime.utcnow()
            start_time = self._calculate_start_time(time_range, end_time)
            
            # Calculate key performance indicators
            insights = {
                'time_period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'range': time_range.value
                },
                'payment_volume': await self._calculate_payment_volume(start_time, end_time),
                'success_metrics': await self._calculate_success_metrics(start_time, end_time),
                'provider_performance': await self._analyze_provider_performance(start_time, end_time),
                'revenue_analysis': await self._analyze_revenue_metrics(start_time, end_time),
                'fraud_metrics': await self._calculate_fraud_metrics(start_time, end_time),
                'performance_trends': await self._analyze_performance_trends(start_time, end_time),
                'optimization_recommendations': await self._generate_optimization_recommendations(start_time, end_time)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate performance insights: {e}")
            return {}
    
    async def _get_widget_data(
        self,
        widget: DashboardWidget,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get data for a specific widget"""
        try:
            widget_data = {
                'widget_id': widget.widget_id,
                'widget_name': widget.name,
                'widget_type': widget.widget_type,
                'configuration': widget.configuration,
                'data': {}
            }
            
            # Get data for each metric in the widget
            for metric_id in widget.metrics:
                if metric_id in self.metrics:
                    metric_data = await self._get_metric_data_for_period(metric_id, start_time, end_time)
                    widget_data['data'][metric_id] = metric_data
            
            # Apply widget-specific transformations
            if widget.widget_type == 'kpi':
                widget_data['data'] = await self._transform_kpi_data(widget_data['data'])
            elif widget.widget_type == 'chart':
                widget_data['data'] = await self._transform_chart_data(widget_data['data'], widget.configuration)
            elif widget.widget_type == 'table':
                widget_data['data'] = await self._transform_table_data(widget_data['data'])
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Failed to get widget data: {e}")
            return {'widget_id': widget.widget_id, 'error': str(e)}
    
    def _create_line_chart(self, data: Dict[str, List], config: Dict[str, Any]) -> go.Figure:
        """Create line chart"""
        fig = go.Figure()
        
        for metric_id, values in data.items():
            if metric_id in self.metrics:
                metric = self.metrics[metric_id]
                
                timestamps = [val['timestamp'] for val in values]
                metric_values = [val['value'] for val in values]
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=metric_values,
                    mode='lines+markers',
                    name=metric.name,
                    hovertemplate=f'{metric.name}: %{{y}} {metric.unit}<br>Time: %{{x}}<extra></extra>'
                ))
        
        fig.update_layout(
            title=config.get('title', 'Payment Metrics'),
            xaxis_title='Time',
            yaxis_title='Value',
            hovermode='x unified'
        )
        
        return fig
    
    def _create_bar_chart(self, data: Dict[str, List], config: Dict[str, Any]) -> go.Figure:
        """Create bar chart"""
        fig = go.Figure()
        
        # Implementation for bar chart
        return fig
    
    def _create_pie_chart(self, data: Dict[str, List], config: Dict[str, Any]) -> go.Figure:
        """Create pie chart"""
        fig = go.Figure()
        
        # Implementation for pie chart
        return fig
    
    def _create_gauge_chart(self, data: Dict[str, List], config: Dict[str, Any]) -> go.Figure:
        """Create gauge chart"""
        fig = go.Figure()
        
        # Implementation for gauge chart
        return fig
    
    def _create_heatmap_chart(self, data: Dict[str, List], config: Dict[str, Any]) -> go.Figure:
        """Create heatmap chart"""
        fig = go.Figure()
        
        # Implementation for heatmap chart
        return fig
    
    def _calculate_start_time(self, time_range: TimeRange, end_time: datetime) -> datetime:
        """Calculate start time based on time range"""
        if time_range == TimeRange.HOUR:
            return end_time - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            return end_time - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            return end_time - timedelta(weeks=1)
        elif time_range == TimeRange.MONTH:
            return end_time - timedelta(days=30)
        elif time_range == TimeRange.QUARTER:
            return end_time - timedelta(days=90)
        elif time_range == TimeRange.YEAR:
            return end_time - timedelta(days=365)
        else:
            return end_time - timedelta(days=1)  # Default to 1 day
    
    async def _collect_metrics_periodically(self):
        """Periodically collect metrics"""
        while True:
            try:
                await asyncio.sleep(self.real_time_update_interval.total_seconds())
                
                # Collect all active metrics
                for metric in self.metrics.values():
                    if metric.is_active:
                        try:
                            value = await self._execute_metric_query(metric)
                            await self._store_metric_value(metric.metric_id, value)
                        except Exception as e:
                            logger.error(f"Failed to collect metric {metric.metric_id}: {e}")
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
    
    async def _monitor_alerts_periodically(self):
        """Periodically monitor alerts"""
        while True:
            try:
                await asyncio.sleep(60)  # Check alerts every minute
                
                for alert in self.alerts.values():
                    if alert.is_active:
                        await self._check_alert_condition(alert)
                
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
    
    async def _cleanup_old_data_periodically(self):
        """Periodically clean up old data"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                
                cutoff_time = datetime.utcnow() - self.data_retention
                await self._cleanup_metric_data(cutoff_time)
                
            except Exception as e:
                logger.error(f"Error in data cleanup: {e}")
    
    # Placeholder methods for additional functionality
    async def _load_dashboards(self):
        """Load dashboards from storage"""
        pass
    
    async def _load_metrics(self):
        """Load metrics from storage"""
        pass
    
    async def _load_alerts(self):
        """Load alerts from storage"""
        pass
    
    async def _create_default_configurations(self):
        """Create default dashboards and metrics"""
        pass
    
    async def _get_latest_metric_values(self, metric_id: str, last_update: Optional[datetime]) -> List[MetricValue]:
        """Get latest metric values"""
        return []
    
    async def _get_metric_time_series(self, metric_id: str, time_range: TimeRange) -> List[Dict[str, Any]]:
        """Get metric time series data"""
        return []
    
    async def _get_metric_data_for_period(self, metric_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get metric data for specific period"""
        return {}
    
    async def _generate_dashboard_summary(self, dashboard: Dashboard, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate dashboard summary"""
        return {}
    
    async def _transform_kpi_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data for KPI widget"""
        return data
    
    async def _transform_chart_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data for chart widget"""
        return data
    
    async def _transform_table_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data for table widget"""
        return data
    
    async def _store_dashboard(self, dashboard: Dashboard):
        """Store dashboard configuration"""
        pass
    
    async def _store_alert(self, alert: Alert):
        """Store alert configuration"""
        pass
    
    async def _execute_metric_query(self, metric: DashboardMetric) -> float:
        """Execute metric query and return value"""
        return 0.0
    
    async def _store_metric_value(self, metric_id: str, value: float):
        """Store metric value"""
        pass
    
    async def _check_alert_condition(self, alert: Alert):
        """Check alert condition and trigger if necessary"""
        pass
    
    async def _cleanup_metric_data(self, cutoff_time: datetime):
        """Clean up old metric data"""
        pass
    
    async def _calculate_payment_volume(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate payment volume metrics"""
        return {}
    
    async def _calculate_success_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate success rate metrics"""
        return {}
    
    async def _analyze_provider_performance(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Analyze payment provider performance"""
        return {}
    
    async def _analyze_revenue_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Analyze revenue metrics"""
        return {}
    
    async def _calculate_fraud_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate fraud detection metrics"""
        return {}
    
    async def _analyze_performance_trends(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Analyze performance trends"""
        return {}
    
    async def _generate_optimization_recommendations(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        return []
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard system metrics"""
        return {
            "total_dashboards": len(self.dashboards),
            "total_metrics": len(self.metrics),
            "active_metrics": len([m for m in self.metrics.values() if m.is_active]),
            "total_alerts": len(self.alerts),
            "active_alerts": len([a for a in self.alerts.values() if a.is_active]),
            "active_connections": len(self.active_connections),
            "cache_size": sum(len(values) for values in self.metric_cache.values()),
            "update_interval_seconds": int(self.real_time_update_interval.total_seconds()),
            "data_retention_days": self.data_retention.days
        }