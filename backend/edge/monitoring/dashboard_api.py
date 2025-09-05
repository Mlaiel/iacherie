"""Edge Dashboard API
==================

Real-time dashboard API for edge computing infrastructure,
providing REST endpoints for monitoring data visualization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

logger = logging.getLogger(__name__)


class WidgetType(str, Enum):
    """Dashboard widget types."""
    METRIC_CHART = "metric_chart"
    GAUGE = "gauge"
    TABLE = "table"
    ALERT_LIST = "alert_list"
    STATUS_GRID = "status_grid"
    TREND_CHART = "trend_chart"
    MAP = "map"
    LOG_VIEWER = "log_viewer"


class ChartType(str, Enum):
    """Chart types for widgets."""
    LINE = "line"
    BAR = "bar"
    AREA = "area"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    widget_id: str
    title: str
    widget_type: WidgetType
    chart_type: Optional[ChartType] = None
    data_source: str = ""
    refresh_interval: int = 30  # seconds
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=dict)  # x, y, width, height


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    dashboard_id: str
    name: str
    description: str
    widgets: List[DashboardWidget] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    auto_refresh: bool = True
    refresh_interval: int = 30


# Pydantic models for API requests/responses
class MetricQuery(BaseModel):
    metric_name: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    aggregation: Optional[str] = "avg"
    interval: Optional[str] = "1m"


class AlertQuery(BaseModel):
    severity: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = 100


class HealthQuery(BaseModel):
    check_id: Optional[str] = None
    status: Optional[str] = None


class DashboardResponse(BaseModel):
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    last_updated: str


class EdgeDashboardAPI:
    """Real-time dashboard API for edge computing infrastructure."""
    
    def __init__(self,
                 host: str = "0.0.0.0",
                 port: int = 8080,
                 metrics_collector=None,
                 performance_monitor=None,
                 health_checker=None,
                 alerting_system=None):
        
        self.host = host
        self.port = port
        
        # Injected dependencies
        self.metrics_collector = metrics_collector
        self.performance_monitor = performance_monitor
        self.health_checker = health_checker
        self.alerting_system = alerting_system
        
        # Dashboard storage
        self.dashboards: Dict[str, DashboardConfig] = {}
        
        # FastAPI app
        self.app = FastAPI(
            title="Edge Computing Dashboard API",
            description="Real-time monitoring and analytics API",
            version="1.0.0"
        )
        
        # Server
        self.server = None
        
        # Setup routes
        self._setup_routes()
        
        # Create default dashboard
        self._create_default_dashboard()
        
        logger.info("EdgeDashboardAPI initialized")
    
    async def start(self):
        """Start the dashboard API server."""
        try:
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            self.server = uvicorn.Server(config)
            
            logger.info(f"Starting dashboard API server on {self.host}:{self.port}")
            await self.server.serve()
            
        except Exception as e:
            logger.error(f"Failed to start dashboard API server: {e}")
    
    async def stop(self):
        """Stop the dashboard API server."""
        if self.server:
            self.server.should_exit = True
            logger.info("Dashboard API server stopped")
    
    def _setup_routes(self):
        """Setup API routes."""
        
        # Health endpoint
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        # Metrics endpoints
        @self.app.get("/api/metrics")
        async def get_metrics(
            metric_name: Optional[str] = Query(None),
            start_time: Optional[str] = Query(None),
            end_time: Optional[str] = Query(None),
            limit: Optional[int] = Query(100)
        ):
            return await self._get_metrics(metric_name, start_time, end_time, limit)
        
        @self.app.post("/api/metrics/query")
        async def query_metrics(query: MetricQuery):
            return await self._query_metrics(query)
        
        @self.app.get("/api/metrics/statistics")
        async def get_metric_statistics(
            metric_name: str = Query(...),
            time_window: Optional[str] = Query("1h")
        ):
            return await self._get_metric_statistics(metric_name, time_window)
        
        # Performance endpoints
        @self.app.get("/api/performance/summary")
        async def get_performance_summary(
            time_window: Optional[str] = Query("1h")
        ):
            return await self._get_performance_summary(time_window)
        
        @self.app.get("/api/performance/trends")
        async def get_performance_trends():
            return await self._get_performance_trends()
        
        # Health check endpoints
        @self.app.get("/api/health/status")
        async def get_health_status(query: HealthQuery = None):
            if not query:
                query = HealthQuery()
            return await self._get_health_status(query)
        
        @self.app.get("/api/health/report")
        async def get_health_report():
            return await self._get_health_report()
        
        # Alert endpoints
        @self.app.get("/api/alerts")
        async def get_alerts(query: AlertQuery = None):
            if not query:
                query = AlertQuery()
            return await self._get_alerts(query)
        
        @self.app.get("/api/alerts/statistics")
        async def get_alert_statistics():
            return await self._get_alert_statistics()
        
        @self.app.post("/api/alerts/{alert_id}/acknowledge")
        async def acknowledge_alert(
            alert_id: str = Path(...),
            acknowledged_by: str = Query(...)
        ):
            return await self._acknowledge_alert(alert_id, acknowledged_by)
        
        @self.app.post("/api/alerts/{alert_id}/resolve")
        async def resolve_alert(
            alert_id: str = Path(...),
            resolution_message: Optional[str] = Query(None)
        ):
            return await self._resolve_alert(alert_id, resolution_message)
        
        # Dashboard endpoints
        @self.app.get("/api/dashboards")
        async def get_dashboards():
            return await self._get_dashboards()
        
        @self.app.get("/api/dashboards/{dashboard_id}")
        async def get_dashboard(dashboard_id: str = Path(...)):
            return await self._get_dashboard(dashboard_id)
        
        @self.app.get("/api/dashboards/{dashboard_id}/data")
        async def get_dashboard_data(dashboard_id: str = Path(...)):
            return await self._get_dashboard_data(dashboard_id)
        
        # Real-time data endpoint
        @self.app.get("/api/realtime/overview")
        async def get_realtime_overview():
            return await self._get_realtime_overview()
    
    # API implementation methods
    
    async def _get_metrics(self, metric_name: Optional[str], start_time: Optional[str], 
                          end_time: Optional[str], limit: Optional[int]):
        """Get metrics data."""
        
        if not self.metrics_collector:
            raise HTTPException(status_code=503, detail="Metrics collector not available")
        
        try:
            # Parse time parameters
            start_dt = datetime.fromisoformat(start_time) if start_time else None
            end_dt = datetime.fromisoformat(end_time) if end_time else None
            
            # Get metrics from collector
            from .edge_metrics import MetricType
            metric_type = MetricType(metric_name) if metric_name else None
            
            metrics = await self.metrics_collector.get_metrics(
                metric_type=metric_type,
                start_time=start_dt,
                end_time=end_dt,
                limit=limit
            )
            
            # Convert to API format
            result = []
            for metric in metrics:
                result.append({
                    'metric_id': metric.metric_id,
                    'metric_type': metric.metric_type.value,
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'source': metric.source,
                    'tags': metric.tags,
                    'unit': metric.unit
                })
            
            return {'metrics': result, 'count': len(result)}
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _query_metrics(self, query: MetricQuery):
        """Query metrics with aggregation."""
        
        if not self.metrics_collector:
            raise HTTPException(status_code=503, detail="Metrics collector not available")
        
        try:
            # Parse time parameters
            start_time = datetime.fromisoformat(query.start_time) if query.start_time else datetime.now() - timedelta(hours=1)
            end_time = datetime.fromisoformat(query.end_time) if query.end_time else datetime.now()
            
            # Get aggregated metrics
            from .edge_metrics import MetricType, AggregationType
            
            metric_type = MetricType(query.metric_name)
            aggregation_type = AggregationType(query.aggregation.upper())
            
            time_window = end_time - start_time
            
            aggregations = await self.metrics_collector.get_aggregated_metrics(
                metric_type=metric_type,
                aggregation_type=aggregation_type,
                time_window=time_window
            )
            
            # Convert to API format
            result = []
            for agg in aggregations:
                result.append({
                    'metric_type': agg.metric_type.value,
                    'aggregation_type': agg.aggregation_type.value,
                    'value': agg.value,
                    'start_time': agg.start_time.isoformat(),
                    'end_time': agg.end_time.isoformat(),
                    'sample_count': agg.sample_count,
                    'source': agg.source
                })
            
            return {'aggregations': result, 'count': len(result)}
            
        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_metric_statistics(self, metric_name: str, time_window: str):
        """Get metric statistics."""
        
        if not self.metrics_collector:
            raise HTTPException(status_code=503, detail="Metrics collector not available")
        
        try:
            # Parse time window
            window_mapping = {
                '1h': timedelta(hours=1),
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30)
            }
            window = window_mapping.get(time_window, timedelta(hours=1))
            
            from .edge_metrics import MetricType
            metric_type = MetricType(metric_name)
            
            stats = await self.metrics_collector.get_metric_statistics(
                metric_type=metric_type,
                time_window=window
            )
            
            return {'metric_name': metric_name, 'time_window': time_window, 'statistics': stats}
            
        except Exception as e:
            logger.error(f"Failed to get metric statistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_performance_summary(self, time_window: str):
        """Get performance summary."""
        
        if not self.performance_monitor:
            raise HTTPException(status_code=503, detail="Performance monitor not available")
        
        try:
            # Parse time window
            window_mapping = {
                '1h': timedelta(hours=1),
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7)
            }
            window = window_mapping.get(time_window, timedelta(hours=1))
            
            summary = await self.performance_monitor.get_performance_summary(window)
            
            return {'time_window': time_window, 'summary': summary}
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_performance_trends(self):
        """Get performance trends."""
        
        if not self.performance_monitor:
            raise HTTPException(status_code=503, detail="Performance monitor not available")
        
        try:
            trends = await self.performance_monitor.get_all_trends()
            
            # Convert to API format
            result = {}
            for metric_name, trend in trends.items():
                result[metric_name] = {
                    'direction': trend.direction.value,
                    'slope': trend.slope,
                    'confidence': trend.confidence,
                    'period': str(trend.period),
                    'sample_count': trend.sample_count
                }
            
            return {'trends': result}
            
        except Exception as e:
            logger.error(f"Failed to get performance trends: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_health_status(self, query: HealthQuery):
        """Get health status."""
        
        if not self.health_checker:
            raise HTTPException(status_code=503, detail="Health checker not available")
        
        try:
            if query.check_id:
                status = await self.health_checker.get_health_status(query.check_id)
                return {'check_id': query.check_id, 'status': status.value}
            else:
                overall = await self.health_checker.get_overall_health()
                return overall
                
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_health_report(self):
        """Get health report."""
        
        if not self.health_checker:
            raise HTTPException(status_code=503, detail="Health checker not available")
        
        try:
            report = await self.health_checker.get_health_report()
            return report
            
        except Exception as e:
            logger.error(f"Failed to get health report: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_alerts(self, query: AlertQuery):
        """Get alerts."""
        
        if not self.alerting_system:
            raise HTTPException(status_code=503, detail="Alerting system not available")
        
        try:
            from .alerting_system import AlertSeverity, AlertStatus
            
            severity = AlertSeverity(query.severity) if query.severity else None
            status = AlertStatus(query.status) if query.status else None
            
            if status and status != "active":
                # Get from history
                alerts = await self.alerting_system.get_alert_history(
                    limit=query.limit,
                    status=status
                )
            else:
                # Get active alerts
                alerts = await self.alerting_system.get_active_alerts(
                    severity=severity
                )
            
            # Convert to API format
            result = []
            for alert in alerts:
                result.append({
                    'alert_id': alert.alert_id,
                    'rule_id': alert.rule_id,
                    'type': alert.alert_type.value,
                    'severity': alert.severity.value,
                    'status': alert.status.value,
                    'title': alert.title,
                    'message': alert.message,
                    'source': alert.source,
                    'timestamp': alert.timestamp.isoformat(),
                    'acknowledged_by': alert.acknowledged_by,
                    'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                    'tags': alert.tags
                })
            
            return {'alerts': result, 'count': len(result)}
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_alert_statistics(self):
        """Get alert statistics."""
        
        if not self.alerting_system:
            raise HTTPException(status_code=503, detail="Alerting system not available")
        
        try:
            stats = await self.alerting_system.get_alert_statistics()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get alert statistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert."""
        
        if not self.alerting_system:
            raise HTTPException(status_code=503, detail="Alerting system not available")
        
        try:
            success = await self.alerting_system.acknowledge_alert(alert_id, acknowledged_by)
            
            if success:
                return {'message': 'Alert acknowledged', 'alert_id': alert_id}
            else:
                raise HTTPException(status_code=404, detail="Alert not found")
                
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _resolve_alert(self, alert_id: str, resolution_message: Optional[str]):
        """Resolve an alert."""
        
        if not self.alerting_system:
            raise HTTPException(status_code=503, detail="Alerting system not available")
        
        try:
            success = await self.alerting_system.resolve_alert(alert_id, resolution_message)
            
            if success:
                return {'message': 'Alert resolved', 'alert_id': alert_id}
            else:
                raise HTTPException(status_code=404, detail="Alert not found")
                
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_dashboards(self):
        """Get all dashboards."""
        
        dashboards = []
        for dashboard_id, config in self.dashboards.items():
            dashboards.append({
                'dashboard_id': config.dashboard_id,
                'name': config.name,
                'description': config.description,
                'widget_count': len(config.widgets)
            })
        
        return {'dashboards': dashboards}
    
    async def _get_dashboard(self, dashboard_id: str):
        """Get specific dashboard configuration."""
        
        if dashboard_id not in self.dashboards:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        config = self.dashboards[dashboard_id]
        
        # Convert widgets to API format
        widgets = []
        for widget in config.widgets:
            widgets.append({
                'widget_id': widget.widget_id,
                'title': widget.title,
                'widget_type': widget.widget_type.value,
                'chart_type': widget.chart_type.value if widget.chart_type else None,
                'data_source': widget.data_source,
                'refresh_interval': widget.refresh_interval,
                'config': widget.config,
                'position': widget.position
            })
        
        return DashboardResponse(
            dashboard_id=config.dashboard_id,
            name=config.name,
            description=config.description,
            widgets=widgets,
            last_updated=datetime.now().isoformat()
        )
    
    async def _get_dashboard_data(self, dashboard_id: str):
        """Get dashboard data for all widgets."""
        
        if dashboard_id not in self.dashboards:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        config = self.dashboards[dashboard_id]
        widget_data = {}
        
        for widget in config.widgets:
            try:
                data = await self._get_widget_data(widget)
                widget_data[widget.widget_id] = data
            except Exception as e:
                logger.error(f"Failed to get data for widget {widget.widget_id}: {e}")
                widget_data[widget.widget_id] = {'error': str(e)}
        
        return {
            'dashboard_id': dashboard_id,
            'widget_data': widget_data,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _get_widget_data(self, widget: DashboardWidget):
        """Get data for a specific widget."""
        
        if widget.widget_type == WidgetType.METRIC_CHART:
            return await self._get_metric_chart_data(widget)
        elif widget.widget_type == WidgetType.GAUGE:
            return await self._get_gauge_data(widget)
        elif widget.widget_type == WidgetType.ALERT_LIST:
            return await self._get_alert_list_data(widget)
        elif widget.widget_type == WidgetType.STATUS_GRID:
            return await self._get_status_grid_data(widget)
        else:
            return {'message': f'Widget type {widget.widget_type.value} not implemented'}
    
    async def _get_metric_chart_data(self, widget: DashboardWidget):
        """Get data for metric chart widget."""
        
        if not self.metrics_collector:
            return {'error': 'Metrics collector not available'}
        
        try:
            from .edge_metrics import MetricType
            metric_type = MetricType(widget.data_source)
            
            # Get recent metrics
            metrics = await self.metrics_collector.get_metrics(
                metric_type=metric_type,
                start_time=datetime.now() - timedelta(hours=1),
                limit=100
            )
            
            # Format for chart
            data_points = []
            for metric in metrics:
                data_points.append({
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.value
                })
            
            return {
                'chart_type': widget.chart_type.value if widget.chart_type else 'line',
                'data': data_points,
                'metric_name': widget.data_source
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_gauge_data(self, widget: DashboardWidget):
        """Get data for gauge widget."""
        
        if not self.metrics_collector:
            return {'error': 'Metrics collector not available'}
        
        try:
            from .edge_metrics import MetricType
            metric_type = MetricType(widget.data_source)
            
            # Get latest metric value
            metrics = await self.metrics_collector.get_metrics(
                metric_type=metric_type,
                limit=1
            )
            
            current_value = metrics[0].value if metrics else 0
            
            return {
                'current_value': current_value,
                'min_value': widget.config.get('min_value', 0),
                'max_value': widget.config.get('max_value', 100),
                'unit': widget.config.get('unit', ''),
                'thresholds': widget.config.get('thresholds', {})
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_alert_list_data(self, widget: DashboardWidget):
        """Get data for alert list widget."""
        
        if not self.alerting_system:
            return {'error': 'Alerting system not available'}
        
        try:
            alerts = await self.alerting_system.get_active_alerts()
            
            alert_list = []
            for alert in alerts[:10]:  # Limit to 10 recent alerts
                alert_list.append({
                    'alert_id': alert.alert_id,
                    'title': alert.title,
                    'severity': alert.severity.value,
                    'timestamp': alert.timestamp.isoformat(),
                    'source': alert.source
                })
            
            return {'alerts': alert_list}
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_status_grid_data(self, widget: DashboardWidget):
        """Get data for status grid widget."""
        
        if not self.health_checker:
            return {'error': 'Health checker not available'}
        
        try:
            overall = await self.health_checker.get_overall_health()
            
            return {
                'overall_status': overall['overall_status'].value,
                'total_checks': overall['total_checks'],
                'status_counts': overall['status_counts'],
                'failed_checks': overall['failed_checks']
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_realtime_overview(self):
        """Get real-time overview data."""
        
        overview = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'unknown',
            'metrics': {},
            'alerts': {'active': 0, 'critical': 0},
            'health': {'overall': 'unknown', 'checks_passing': 0}
        }
        
        try:
            # Get current metrics
            if self.metrics_collector:
                current_metrics = await self.metrics_collector.get_current_metrics()
                overview['metrics'] = current_metrics
            
            # Get alert counts
            if self.alerting_system:
                stats = await self.alerting_system.get_alert_statistics()
                overview['alerts'] = {
                    'active': stats.get('active_alerts', 0),
                    'critical': stats.get('by_severity', {}).get('critical', 0)
                }
            
            # Get health status
            if self.health_checker:
                health = await self.health_checker.get_overall_health()
                overview['health'] = {
                    'overall': health['overall_status'].value,
                    'checks_passing': health['status_counts'].get('healthy', 0)
                }
                overview['system_status'] = health['overall_status'].value
            
        except Exception as e:
            logger.error(f"Failed to get realtime overview: {e}")
            overview['error'] = str(e)
        
        return overview
    
    def _create_default_dashboard(self):
        """Create a default dashboard."""
        
        widgets = [
            DashboardWidget(
                widget_id="cpu_chart",
                title="CPU Usage",
                widget_type=WidgetType.METRIC_CHART,
                chart_type=ChartType.LINE,
                data_source="cpu_usage",
                position={'x': 0, 'y': 0, 'width': 6, 'height': 4}
            ),
            DashboardWidget(
                widget_id="memory_gauge",
                title="Memory Usage",
                widget_type=WidgetType.GAUGE,
                data_source="memory_usage",
                config={'max_value': 100, 'unit': '%'},
                position={'x': 6, 'y': 0, 'width': 3, 'height': 4}
            ),
            DashboardWidget(
                widget_id="alerts_list",
                title="Active Alerts",
                widget_type=WidgetType.ALERT_LIST,
                position={'x': 9, 'y': 0, 'width': 3, 'height': 4}
            ),
            DashboardWidget(
                widget_id="system_status",
                title="System Health",
                widget_type=WidgetType.STATUS_GRID,
                position={'x': 0, 'y': 4, 'width': 12, 'height': 3}
            )
        ]
        
        default_dashboard = DashboardConfig(
            dashboard_id="default",
            name="Edge Computing Overview",
            description="Default dashboard showing system overview",
            widgets=widgets
        )
        
        self.dashboards["default"] = default_dashboard


def create_dashboard_api(
    host: str = "0.0.0.0",
    port: int = 8080,
    metrics_collector=None,
    performance_monitor=None,
    health_checker=None,
    alerting_system=None
) -> EdgeDashboardAPI:
    """Create and configure a dashboard API instance."""
    return EdgeDashboardAPI(
        host=host,
        port=port,
        metrics_collector=metrics_collector,
        performance_monitor=performance_monitor,
        health_checker=health_checker,
        alerting_system=alerting_system
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_dashboard_api():
        """Test the dashboard API."""
        dashboard = create_dashboard_api(port=8081)
        
        # Start the API server
        await dashboard.start()
    
    # Run test
    asyncio.run(test_dashboard_api())