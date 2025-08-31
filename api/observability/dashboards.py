"""Enterprise Dashboard System

Real-time dashboards for observability, monitoring, and analytics visualization
in the IA Influencer content protection platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + Security

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, copying, or implementation without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum
import logging


class DashboardType(Enum):
    """Dashboard types for different observability views."""
    METRICS = "metrics"
    HEALTH = "health"
    ALERTS = "alerts"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"
    CONTENT = "content"


class RefreshInterval(Enum):
    """Dashboard refresh intervals."""
    REAL_TIME = 1  # 1 second
    FAST = 5  # 5 seconds
    NORMAL = 30  # 30 seconds
    SLOW = 300  # 5 minutes


@dataclass
class DashboardWidget:
    """Dashboard widget definition."""
    id: str
    title: str
    type: str  # chart, metric, table, status, etc.
    data_source: str
    refresh_interval: RefreshInterval
    size: str  # small, medium, large, full
    position: Dict[str, int]  # x, y coordinates
    config: Dict[str, Any] = None
    enabled: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['refresh_interval'] = self.refresh_interval.value
        return data


@dataclass
class Dashboard:
    """Dashboard configuration."""
    id: str
    name: str
    description: str
    dashboard_type: DashboardType
    widgets: List[DashboardWidget]
    layout: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    public: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['dashboard_type'] = self.dashboard_type.value
        data['widgets'] = [w.to_dict() for w in self.widgets]
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


class MetricsDashboard:
    """Real-time metrics dashboard for system and business metrics."""
    
    def __init__(self, metrics_collector, performance_monitor):
        self.metrics_collector = metrics_collector
        self.performance_monitor = performance_monitor
        self.dashboard_id = "metrics_main"
        
        # Initialize dashboard configuration
        self.dashboard = self._create_metrics_dashboard()
    
    def _create_metrics_dashboard(self) -> Dashboard:
        """Create the main metrics dashboard."""
        widgets = [
            # System Metrics Row
            DashboardWidget(
                id="cpu_usage",
                title="CPU Usage",
                type="gauge",
                data_source="system.cpu_percent",
                refresh_interval=RefreshInterval.FAST,
                size="small",
                position={"x": 0, "y": 0},
                config={
                    "max_value": 100,
                    "unit": "%",
                    "thresholds": {"warning": 80, "critical": 95}
                }
            ),
            DashboardWidget(
                id="memory_usage",
                title="Memory Usage",
                type="gauge",
                data_source="system.memory_percent",
                refresh_interval=RefreshInterval.FAST,
                size="small",
                position={"x": 1, "y": 0},
                config={
                    "max_value": 100,
                    "unit": "%",
                    "thresholds": {"warning": 80, "critical": 95}
                }
            ),
            DashboardWidget(
                id="disk_usage",
                title="Disk Usage",
                type="gauge",
                data_source="system.disk_percent",
                refresh_interval=RefreshInterval.NORMAL,
                size="small",
                position={"x": 2, "y": 0},
                config={
                    "max_value": 100,
                    "unit": "%",
                    "thresholds": {"warning": 85, "critical": 95}
                }
            ),
            
            # Content Processing Metrics Row
            DashboardWidget(
                id="content_uploads",
                title="Content Uploads/Hour",
                type="counter",
                data_source="content.uploads_hourly",
                refresh_interval=RefreshInterval.NORMAL,
                size="medium",
                position={"x": 0, "y": 1},
                config={
                    "format": "number",
                    "trend": True
                }
            ),
            DashboardWidget(
                id="upload_success_rate",
                title="Upload Success Rate",
                type="percentage",
                data_source="content.upload_success_rate",
                refresh_interval=RefreshInterval.NORMAL,
                size="medium",
                position={"x": 1, "y": 1},
                config={
                    "target": 99.5,
                    "format": "percentage"
                }
            ),
            
            # Processing Time Trends
            DashboardWidget(
                id="processing_times_chart",
                title="Processing Times (Last 24h)",
                type="line_chart",
                data_source="processing.times_trend",
                refresh_interval=RefreshInterval.NORMAL,
                size="large",
                position={"x": 0, "y": 2},
                config={
                    "metrics": ["upload", "ai_processing", "protection_scan"],
                    "time_range": "24h",
                    "unit": "ms"
                }
            ),
            
            # Content by Type
            DashboardWidget(
                id="content_by_type",
                title="Content Distribution",
                type="pie_chart",
                data_source="content.by_type",
                refresh_interval=RefreshInterval.SLOW,
                size="medium",
                position={"x": 2, "y": 1},
                config={
                    "categories": ["audio", "video", "image", "text"]
                }
            ),
            
            # Recent Activity
            DashboardWidget(
                id="recent_activity",
                title="Recent Activity",
                type="activity_feed",
                data_source="activity.recent",
                refresh_interval=RefreshInterval.FAST,
                size="medium",
                position={"x": 2, "y": 2},
                config={
                    "limit": 10,
                    "show_timestamps": True
                }
            )
        ]
        
        return Dashboard(
            id=self.dashboard_id,
            name="System Metrics Dashboard",
            description="Real-time system and content processing metrics",
            dashboard_type=DashboardType.METRICS,
            widgets=widgets,
            layout={"columns": 3, "rows": 3},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            public=True
        )
    
    async def get_dashboard_data(self) -> Dict:
        """Get all data for the metrics dashboard."""
        data = {}
        
        # Get system metrics
        system_metrics = self.metrics_collector.get_system_metrics()
        data.update({
            "system.cpu_percent": system_metrics.get("cpu_usage_percent", 0),
            "system.memory_percent": system_metrics.get("memory_usage_mb", 0),
            "system.disk_percent": system_metrics.get("disk_usage_percent", 0)
        })
        
        # Get content metrics
        content_metrics = self.metrics_collector.get_content_metrics()
        data.update({
            "content.uploads_hourly": content_metrics.get("uploads_total", 0),
            "content.upload_success_rate": self._calculate_success_rate(),
            "content.by_type": content_metrics.get("uploads_by_type", {})
        })
        
        # Get processing times trend
        data["processing.times_trend"] = await self._get_processing_times_trend()
        
        # Get recent activity
        data["activity.recent"] = await self._get_recent_activity()
        
        return {
            "dashboard": self.dashboard.to_dict(),
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate upload success rate."""
        # Mock calculation - in reality would use actual metrics
        success_count = self.metrics_collector.counters.get("content.uploads.success", 0)
        total_count = self.metrics_collector.counters.get("content.uploads.total", 1)
        return (success_count / total_count) * 100 if total_count > 0 else 100.0
    
    async def _get_processing_times_trend(self) -> Dict:
        """Get processing times trend data."""
        # Mock trend data - in reality would query time series data
        now = datetime.utcnow()
        hours = [(now - timedelta(hours=i)).isoformat() for i in range(23, -1, -1)]
        
        return {
            "timestamps": hours,
            "series": {
                "upload": [2500 + i * 50 for i in range(24)],
                "ai_processing": [15000 + i * 200 for i in range(24)],
                "protection_scan": [8000 + i * 100 for i in range(24)]
            }
        }
    
    async def _get_recent_activity(self) -> List[Dict]:
        """Get recent activity feed."""
        # Mock activity data
        activities = [
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                "type": "upload",
                "description": f"Content uploaded by user_{i}",
                "status": "success"
            }
            for i in range(10)
        ]
        return activities


class HealthDashboard:
    """System health and service status dashboard."""
    
    def __init__(self, health_checker, system_monitor):
        self.health_checker = health_checker
        self.system_monitor = system_monitor
        self.dashboard_id = "health_main"
        
        self.dashboard = self._create_health_dashboard()
    
    def _create_health_dashboard(self) -> Dashboard:
        """Create the health monitoring dashboard."""
        widgets = [
            # Overall Health Status
            DashboardWidget(
                id="overall_health",
                title="Overall System Health",
                type="status_indicator",
                data_source="health.overall_status",
                refresh_interval=RefreshInterval.FAST,
                size="large",
                position={"x": 0, "y": 0},
                config={
                    "status_colors": {
                        "healthy": "#28a745",
                        "degraded": "#ffc107",
                        "unhealthy": "#dc3545"
                    }
                }
            ),
            
            # Service Health Grid
            DashboardWidget(
                id="service_health_grid",
                title="Service Health Status",
                type="service_grid",
                data_source="health.services",
                refresh_interval=RefreshInterval.FAST,
                size="large",
                position={"x": 1, "y": 0},
                config={
                    "services": [
                        "database", "redis", "storage", "ai_processing", 
                        "content_upload", "protection_scan"
                    ]
                }
            ),
            
            # Response Time Chart
            DashboardWidget(
                id="response_times",
                title="Service Response Times",
                type="bar_chart",
                data_source="health.response_times",
                refresh_interval=RefreshInterval.NORMAL,
                size="medium",
                position={"x": 0, "y": 1},
                config={
                    "unit": "ms",
                    "threshold": 5000
                }
            ),
            
            # Resource Utilization
            DashboardWidget(
                id="resource_utilization",
                title="Resource Utilization",
                type="stacked_bar",
                data_source="health.resources",
                refresh_interval=RefreshInterval.NORMAL,
                size="medium",
                position={"x": 1, "y": 1},
                config={
                    "resources": ["cpu", "memory", "disk"],
                    "unit": "%"
                }
            ),
            
            # Health Check History
            DashboardWidget(
                id="health_history",
                title="Health Check Results (24h)",
                type="timeline",
                data_source="health.check_history",
                refresh_interval=RefreshInterval.NORMAL,
                size="full",
                position={"x": 0, "y": 2},
                config={
                    "time_range": "24h",
                    "show_failures_only": False
                }
            )
        ]
        
        return Dashboard(
            id=self.dashboard_id,
            name="System Health Dashboard",
            description="Comprehensive system health and service monitoring",
            dashboard_type=DashboardType.HEALTH,
            widgets=widgets,
            layout={"columns": 2, "rows": 3},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            public=True
        )
    
    async def get_dashboard_data(self) -> Dict:
        """Get all data for the health dashboard."""
        # Run health checks
        health_results = await self.health_checker.run_all_checks()
        
        # Get system metrics
        system_health = self.health_checker.get_system_health()
        
        data = {
            "health.overall_status": health_results.get("overall_status", "unknown"),
            "health.services": self._format_service_health(health_results.get("checks", {})),
            "health.response_times": self._extract_response_times(health_results.get("checks", {})),
            "health.resources": system_health,
            "health.check_history": await self._get_health_history()
        }
        
        return {
            "dashboard": self.dashboard.to_dict(),
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _format_service_health(self, health_checks: Dict) -> List[Dict]:
        """Format service health data for grid display."""
        services = []
        
        for service_name, check_result in health_checks.items():
            services.append({
                "name": service_name,
                "status": check_result.get("status", "unknown"),
                "response_time": check_result.get("response_time_ms", 0),
                "last_check": check_result.get("timestamp", ""),
                "critical": check_result.get("critical", False)
            })
        
        return services
    
    def _extract_response_times(self, health_checks: Dict) -> Dict:
        """Extract response times for chart display."""
        response_times = {}
        
        for service_name, check_result in health_checks.items():
            response_times[service_name] = check_result.get("response_time_ms", 0)
        
        return response_times
    
    async def _get_health_history(self) -> List[Dict]:
        """Get health check history for timeline."""
        # Mock history data - in reality would query stored health check results
        history = []
        now = datetime.utcnow()
        
        for i in range(48):  # Last 48 hours
            timestamp = now - timedelta(hours=i)
            history.append({
                "timestamp": timestamp.isoformat(),
                "overall_status": "healthy" if i % 10 != 0 else "degraded",
                "failed_checks": [] if i % 10 != 0 else ["database"],
                "total_checks": 6
            })
        
        return list(reversed(history))


class AlertDashboard:
    """Alert monitoring and management dashboard."""
    
    def __init__(self, alert_manager):
        self.alert_manager = alert_manager
        self.dashboard_id = "alerts_main"
        
        self.dashboard = self._create_alert_dashboard()
    
    def _create_alert_dashboard(self) -> Dashboard:
        """Create the alert monitoring dashboard."""
        widgets = [
            # Alert Summary
            DashboardWidget(
                id="alert_summary",
                title="Alert Summary",
                type="metric_cards",
                data_source="alerts.summary",
                refresh_interval=RefreshInterval.FAST,
                size="large",
                position={"x": 0, "y": 0},
                config={
                    "metrics": [
                        "total_active", "critical", "warning", "info"
                    ]
                }
            ),
            
            # Active Alerts Table
            DashboardWidget(
                id="active_alerts",
                title="Active Alerts",
                type="table",
                data_source="alerts.active",
                refresh_interval=RefreshInterval.FAST,
                size="full",
                position={"x": 0, "y": 1},
                config={
                    "columns": [
                        "severity", "rule_name", "message", 
                        "triggered_at", "actions"
                    ],
                    "sortable": True,
                    "filterable": True
                }
            ),
            
            # Alert Trend Chart
            DashboardWidget(
                id="alert_trends",
                title="Alert Trends (24h)",
                type="area_chart",
                data_source="alerts.trends",
                refresh_interval=RefreshInterval.NORMAL,
                size="medium",
                position={"x": 1, "y": 0},
                config={
                    "time_range": "24h",
                    "stack_by": "severity"
                }
            ),
            
            # Top Alert Rules
            DashboardWidget(
                id="top_alert_rules",
                title="Most Triggered Rules",
                type="horizontal_bar",
                data_source="alerts.top_rules",
                refresh_interval=RefreshInterval.SLOW,
                size="medium",
                position={"x": 2, "y": 0},
                config={
                    "limit": 10
                }
            )
        ]
        
        return Dashboard(
            id=self.dashboard_id,
            name="Alert Management Dashboard",
            description="Real-time alert monitoring and management",
            dashboard_type=DashboardType.ALERTS,
            widgets=widgets,
            layout={"columns": 3, "rows": 2},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            public=True
        )
    
    async def get_dashboard_data(self) -> Dict:
        """Get all data for the alert dashboard."""
        # Get alert summary
        alert_summary = self.alert_manager.get_alert_summary()
        
        # Get active alerts
        active_alerts = self.alert_manager.get_active_alerts()
        
        data = {
            "alerts.summary": alert_summary,
            "alerts.active": [alert.to_dict() for alert in active_alerts],
            "alerts.trends": await self._get_alert_trends(),
            "alerts.top_rules": await self._get_top_alert_rules()
        }
        
        return {
            "dashboard": self.dashboard.to_dict(),
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_alert_trends(self) -> Dict:
        """Get alert trends over time."""
        # Mock trend data
        now = datetime.utcnow()
        hours = [(now - timedelta(hours=i)).isoformat() for i in range(23, -1, -1)]
        
        return {
            "timestamps": hours,
            "series": {
                "critical": [i % 3 for i in range(24)],
                "warning": [i % 5 for i in range(24)],
                "info": [i % 7 for i in range(24)]
            }
        }
    
    async def _get_top_alert_rules(self) -> List[Dict]:
        """Get most frequently triggered alert rules."""
        # Mock data - in reality would query alert history
        return [
            {"rule_name": "cpu_usage_high", "trigger_count": 15},
            {"rule_name": "memory_usage_high", "trigger_count": 12},
            {"rule_name": "upload_failure_rate", "trigger_count": 8},
            {"rule_name": "ai_processing_slow", "trigger_count": 6},
            {"rule_name": "disk_space_low", "trigger_count": 4}
        ]


class DashboardManager:
    """Manages multiple dashboards and provides unified access."""
    
    def __init__(self, 
                 metrics_collector=None,
                 health_checker=None,
                 system_monitor=None,
                 performance_monitor=None,
                 alert_manager=None):
        
        self.dashboards = {}
        
        # Initialize available dashboards
        if metrics_collector and performance_monitor:
            self.dashboards["metrics"] = MetricsDashboard(metrics_collector, performance_monitor)
        
        if health_checker and system_monitor:
            self.dashboards["health"] = HealthDashboard(health_checker, system_monitor)
        
        if alert_manager:
            self.dashboards["alerts"] = AlertDashboard(alert_manager)
        
        # Dashboard registry
        self.dashboard_registry = {}
        for name, dashboard_obj in self.dashboards.items():
            self.dashboard_registry[dashboard_obj.dashboard.id] = {
                "name": name,
                "dashboard": dashboard_obj.dashboard,
                "instance": dashboard_obj
            }
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dict]:
        """Get dashboard configuration and data."""
        if dashboard_id not in self.dashboard_registry:
            return None
        
        dashboard_info = self.dashboard_registry[dashboard_id]
        dashboard_instance = dashboard_info["instance"]
        
        return await dashboard_instance.get_dashboard_data()
    
    def list_dashboards(self) -> List[Dict]:
        """List all available dashboards."""
        return [
            {
                "id": info["dashboard"].id,
                "name": info["dashboard"].name,
                "description": info["dashboard"].description,
                "type": info["dashboard"].dashboard_type.value,
                "public": info["dashboard"].public,
                "widget_count": len(info["dashboard"].widgets)
            }
            for info in self.dashboard_registry.values()
        ]
    
    async def get_dashboard_widget_data(self, dashboard_id: str, widget_id: str) -> Optional[Dict]:
        """Get data for a specific widget."""
        if dashboard_id not in self.dashboard_registry:
            return None
        
        dashboard_data = await self.get_dashboard(dashboard_id)
        if not dashboard_data:
            return None
        
        # Find widget configuration
        widget_config = None
        for widget in dashboard_data["dashboard"]["widgets"]:
            if widget["id"] == widget_id:
                widget_config = widget
                break
        
        if not widget_config:
            return None
        
        # Get widget data
        data_source = widget_config["data_source"]
        widget_data = dashboard_data["data"].get(data_source)
        
        return {
            "widget": widget_config,
            "data": widget_data,
            "timestamp": dashboard_data["timestamp"]
        }
    
    def get_dashboard_config(self, dashboard_id: str) -> Optional[Dict]:
        """Get dashboard configuration only (no data)."""
        if dashboard_id not in self.dashboard_registry:
            return None
        
        return self.dashboard_registry[dashboard_id]["dashboard"].to_dict()
    
    async def refresh_all_dashboards(self) -> Dict[str, Dict]:
        """Refresh data for all dashboards."""
        refreshed_data = {}
        
        for dashboard_id in self.dashboard_registry:
            try:
                dashboard_data = await self.get_dashboard(dashboard_id)
                refreshed_data[dashboard_id] = dashboard_data
            except Exception as e:
                logging.error(f"Failed to refresh dashboard {dashboard_id}: {e}")
                refreshed_data[dashboard_id] = {"error": str(e)}
        
        return refreshed_data
