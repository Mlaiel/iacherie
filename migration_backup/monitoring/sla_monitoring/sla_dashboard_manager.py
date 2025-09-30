"""SLA Dashboard Manager System
Real-time SLA dashboard management and visualization for Creator Economy Platform

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle exclusive
"""

import asyncio
import logging
import statistics
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import deque, defaultdict
from enum import Enum

class DashboardType(Enum):
    """Types of SLA dashboards"""
    REAL_TIME = "real_time"
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    MOBILE = "mobile"
    CUSTOM = "custom"

class VisualizationType(Enum):
    """Types of visualizations"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    HEATMAP = "heatmap"
    TABLE = "table"
    METRIC_CARD = "metric_card"
    ALERT_LIST = "alert_list"
    TREND_INDICATOR = "trend_indicator"

class RefreshRate(Enum):
    """Dashboard refresh rates"""
    REAL_TIME = "real_time"  # 1-5 seconds
    FAST = "fast"           # 30 seconds
    NORMAL = "normal"       # 1 minute
    SLOW = "slow"          # 5 minutes
    MANUAL = "manual"       # On demand

@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    title: str
    visualization_type: VisualizationType
    data_source: str
    metrics: List[str]
    time_range: str
    refresh_rate: RefreshRate
    position: Dict[str, int]  # x, y, width, height
    configuration: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Dashboard:
    """Dashboard configuration"""
    dashboard_id: str
    name: str
    dashboard_type: DashboardType
    description: str
    widgets: List[DashboardWidget]
    layout: Dict[str, Any]
    access_permissions: List[str]
    refresh_rate: RefreshRate
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class SLADashboardManager:
    """
    Enterprise SLA Dashboard Manager
    Real-time dashboard management and custom visualization system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dashboards: Dict[str, Dashboard] = {}
        self.dashboard_data_cache: Dict[str, Dict[str, Any]] = {}
        self.active_subscriptions: Dict[str, List[str]] = {}  # dashboard_id -> user_ids
        self.widget_templates: Dict[str, DashboardWidget] = {}
        self.dashboard_metrics: deque = deque(maxlen=10000)
        self.monitoring_active = False
        
        # Initialize default dashboard templates
        self._initialize_dashboard_templates()
        
    def _initialize_dashboard_templates(self):
        """Initialize default dashboard templates"""
        # Executive Dashboard Template
        executive_widgets = [
            DashboardWidget(
                widget_id="exec_overall_compliance",
                title="Overall SLA Compliance",
                visualization_type=VisualizationType.GAUGE,
                data_source="sla_tracker",
                metrics=["overall_compliance_percentage"],
                time_range="24h",
                refresh_rate=RefreshRate.NORMAL,
                position={"x": 0, "y": 0, "width": 6, "height": 4},
                configuration={
                    "min_value": 0,
                    "max_value": 100,
                    "thresholds": [
                        {"value": 95, "color": "green"},
                        {"value": 90, "color": "yellow"},
                        {"value": 0, "color": "red"}
                    ]
                }
            ),
            DashboardWidget(
                widget_id="exec_violations_summary",
                title="SLA Violations Summary",
                visualization_type=VisualizationType.BAR_CHART,
                data_source="all_sla_systems",
                metrics=["critical_violations", "warnings"],
                time_range="7d",
                refresh_rate=RefreshRate.NORMAL,
                position={"x": 6, "y": 0, "width": 6, "height": 4}
            ),
            DashboardWidget(
                widget_id="exec_system_health",
                title="System Health Overview",
                visualization_type=VisualizationType.HEATMAP,
                data_source="all_sla_systems",
                metrics=["uptime_percentage", "response_time", "error_rate"],
                time_range="24h",
                refresh_rate=RefreshRate.FAST,
                position={"x": 0, "y": 4, "width": 12, "height": 4}
            )
        ]
        
        # Dashboard sera créé de manière asynchrone lors du premier accès
        self._dashboard_configs = {
            "executive_overview": {
                "title": "Executive SLA Overview",
                "dashboard_type": DashboardType.EXECUTIVE,
                "description": "High-level SLA compliance and system health overview for executives",
                "widgets": executive_widgets,
                "permissions": ["executives", "management"]
            }
        }
        
        # Operational Dashboard Template
        operational_widgets = [
            DashboardWidget(
                widget_id="ops_api_performance",
                title="API Performance Metrics",
                visualization_type=VisualizationType.LINE_CHART,
                data_source="api_performance_sla",
                metrics=["response_time_p95", "throughput_rps", "error_rate"],
                time_range="4h",
                refresh_rate=RefreshRate.FAST,
                position={"x": 0, "y": 0, "width": 8, "height": 4}
            ),
            DashboardWidget(
                widget_id="ops_active_alerts",
                title="Active SLA Alerts",
                visualization_type=VisualizationType.ALERT_LIST,
                data_source="all_sla_systems",
                metrics=["active_alerts"],
                time_range="1h",
                refresh_rate=RefreshRate.REAL_TIME,
                position={"x": 8, "y": 0, "width": 4, "height": 8}
            ),
            DashboardWidget(
                widget_id="ops_infrastructure_health",
                title="Infrastructure Health",
                visualization_type=VisualizationType.METRIC_CARD,
                data_source="infrastructure_health_sla",
                metrics=["system_uptime", "database_performance", "cache_hit_ratio"],
                time_range="1h",
                refresh_rate=RefreshRate.FAST,
                position={"x": 0, "y": 4, "width": 8, "height": 4}
            )
        ]
        
        self._dashboard_configs["operational_monitoring"] = {
            "title": "Operational SLA Monitoring", 
            "dashboard_type": DashboardType.OPERATIONAL,
            "description": "Real-time operational metrics and alerting dashboard",
            "widgets": operational_widgets,
            "permissions": ["operations", "engineering", "devops"]
        }
        
    async def create_dashboard(self, dashboard_id: str, name: str, 
                             dashboard_type: DashboardType, description: str,
                             widgets: List[DashboardWidget],
                             access_permissions: List[str]) -> Dashboard:
        """Create a new SLA dashboard"""
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            name=name,
            dashboard_type=dashboard_type,
            description=description,
            widgets=widgets,
            layout={"grid_size": 12, "row_height": 100},
            access_permissions=access_permissions,
            refresh_rate=RefreshRate.NORMAL,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.dashboards[dashboard_id] = dashboard
        
        # Initialize data cache for dashboard
        self.dashboard_data_cache[dashboard_id] = {}
        
        self.logger.info(f"Dashboard created: {dashboard_id} ({dashboard_type.value})")
        
        return dashboard
        
    async def update_dashboard(self, dashboard_id: str, 
                             updates: Dict[str, Any]) -> Dashboard:
        """Update existing dashboard configuration"""
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        dashboard = self.dashboards[dashboard_id]
        
        # Update dashboard properties
        for key, value in updates.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
        
        dashboard.updated_at = datetime.now()
        
        # Clear cache to force refresh
        self.dashboard_data_cache[dashboard_id] = {}
        
        self.logger.info(f"Dashboard updated: {dashboard_id}")
        
        return dashboard
        
    async def add_widget(self, dashboard_id: str, widget: DashboardWidget) -> bool:
        """Add widget to existing dashboard"""
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        dashboard = self.dashboards[dashboard_id]
        
        # Check for duplicate widget IDs
        existing_ids = {w.widget_id for w in dashboard.widgets}
        if widget.widget_id in existing_ids:
            raise ValueError(f"Widget ID already exists: {widget.widget_id}")
        
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.now()
        
        self.logger.info(f"Widget added to dashboard {dashboard_id}: {widget.widget_id}")
        
        return True
        
    async def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove widget from dashboard"""
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        dashboard = self.dashboards[dashboard_id]
        
        # Find and remove widget
        original_count = len(dashboard.widgets)
        dashboard.widgets = [w for w in dashboard.widgets if w.widget_id != widget_id]
        
        if len(dashboard.widgets) == original_count:
            raise ValueError(f"Widget not found: {widget_id}")
        
        dashboard.updated_at = datetime.now()
        
        self.logger.info(f"Widget removed from dashboard {dashboard_id}: {widget_id}")
        
        return True
        
    async def get_dashboard_data(self, dashboard_id: str, 
                               force_refresh: bool = False) -> Dict[str, Any]:
        """Get dashboard data with all widget data"""
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        dashboard = self.dashboards[dashboard_id]
        
        # Check cache unless force refresh
        if not force_refresh and dashboard_id in self.dashboard_data_cache:
            cached_data = self.dashboard_data_cache[dashboard_id]
            cache_age = datetime.now() - cached_data.get('last_updated', datetime.min)
            
            # Use cache if less than refresh interval
            refresh_seconds = self._get_refresh_seconds(dashboard.refresh_rate)
            if cache_age.total_seconds() < refresh_seconds:
                return cached_data
        
        # Collect data for all widgets
        dashboard_data = {
            "dashboard_id": dashboard_id,
            "name": dashboard.name,
            "dashboard_type": dashboard.dashboard_type.value,
            "last_updated": datetime.now(),
            "widgets": {}
        }
        
        for widget in dashboard.widgets:
            widget_data = await self._get_widget_data(widget)
            dashboard_data["widgets"][widget.widget_id] = widget_data
        
        # Cache the data
        self.dashboard_data_cache[dashboard_id] = dashboard_data
        
        return dashboard_data
        
    async def _get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for a specific widget"""
        widget_data = {
            "widget_id": widget.widget_id,
            "title": widget.title,
            "visualization_type": widget.visualization_type.value,
            "last_updated": datetime.now().isoformat(),
            "data": {},
            "status": "success"
        }
        
        try:
            # Simulate data collection based on data source
            if widget.data_source == "sla_tracker":
                widget_data["data"] = await self._get_sla_tracker_data(widget.metrics)
            elif widget.data_source == "api_performance_sla":
                widget_data["data"] = await self._get_api_performance_data(widget.metrics)
            elif widget.data_source == "all_sla_systems":
                widget_data["data"] = await self._get_all_systems_data(widget.metrics)
            elif widget.data_source == "infrastructure_health_sla":
                widget_data["data"] = await self._get_infrastructure_data(widget.metrics)
            else:
                widget_data["data"] = await self._get_generic_data(widget.metrics)
                
        except Exception as e:
            widget_data["status"] = "error"
            widget_data["error"] = str(e)
            self.logger.error(f"Error getting widget data for {widget.widget_id}: {e}")
        
        return widget_data
        
    async def _get_sla_tracker_data(self, metrics: List[str]) -> Dict[str, Any]:
        """Get SLA tracker data"""
        # Simulated SLA tracker data
        data = {
            "overall_compliance_percentage": 97.5,
            "uptime_hours_24h": 23.8,
            "violations_count": 2,
            "warnings_count": 5
        }
        
        return {metric: data.get(metric, 0) for metric in metrics}
        
    async def _get_api_performance_data(self, metrics: List[str]) -> Dict[str, Any]:
        """Get API performance data"""
        # Simulated API performance data with time series
        timestamp_base = datetime.now() - timedelta(hours=4)
        time_series = []
        
        for i in range(0, 240, 5):  # Every 5 minutes for 4 hours
            timestamp = timestamp_base + timedelta(minutes=i)
            time_series.append({
                "timestamp": timestamp.isoformat(),
                "response_time_p95": 150 + (i % 50) + (10 if i > 120 else 0),  # Simulate variation
                "throughput_rps": 11000 + (i % 1000) - (500 if i > 180 else 0),
                "error_rate": 0.1 + (i % 10) * 0.01
            })
        
        return {
            "time_series": time_series,
            "current_values": {
                "response_time_p95": time_series[-1]["response_time_p95"],
                "throughput_rps": time_series[-1]["throughput_rps"],
                "error_rate": time_series[-1]["error_rate"]
            }
        }
        
    async def _get_all_systems_data(self, metrics: List[str]) -> Dict[str, Any]:
        """Get data from all SLA systems"""
        systems_data = {
            "api_performance": {"compliance": True, "violations": 0, "warnings": 1},
            "creator_experience": {"compliance": True, "violations": 0, "warnings": 2},
            "revenue_monetization": {"compliance": True, "violations": 0, "warnings": 0},
            "content_processing": {"compliance": False, "violations": 1, "warnings": 3},
            "security_compliance": {"compliance": True, "violations": 0, "warnings": 1},
            "infrastructure_health": {"compliance": True, "violations": 0, "warnings": 1}
        }
        
        # Generate aggregated metrics
        total_violations = sum(s["violations"] for s in systems_data.values())
        total_warnings = sum(s["warnings"] for s in systems_data.values())
        compliant_systems = sum(1 for s in systems_data.values() if s["compliance"])
        
        if "active_alerts" in metrics:
            alerts = [
                {
                    "id": "alert_001",
                    "system": "content_processing",
                    "level": "CRITICAL",
                    "message": "AI analysis time exceeding SLA threshold",
                    "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()
                },
                {
                    "id": "alert_002",
                    "system": "api_performance",
                    "level": "WARNING",
                    "message": "Response time approaching threshold",
                    "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()
                }
            ]
            
            return {
                "active_alerts": alerts,
                "systems_data": systems_data,
                "summary": {
                    "total_violations": total_violations,
                    "total_warnings": total_warnings,
                    "compliant_systems": compliant_systems,
                    "total_systems": len(systems_data)
                }
            }
        
        return {
            "critical_violations": total_violations,
            "warnings": total_warnings,
            "systems_compliance": (compliant_systems / len(systems_data)) * 100
        }
        
    async def _get_infrastructure_data(self, metrics: List[str]) -> Dict[str, Any]:
        """Get infrastructure health data"""
        data = {
            "system_uptime": 99.95,
            "database_performance": 85.2,  # Query response time
            "cache_hit_ratio": 94.8,
            "storage_usage": 78.5,
            "network_latency": 25.3
        }
        
        return {metric: data.get(metric, 0) for metric in metrics}
        
    async def _get_generic_data(self, metrics: List[str]) -> Dict[str, Any]:
        """Get generic data for custom metrics"""
        # Generate sample data
        import random
        
        data = {}
        for metric in metrics:
            # Generate realistic sample data based on metric name
            if "percentage" in metric or "ratio" in metric:
                data[metric] = random.uniform(85, 99)
            elif "time" in metric:
                data[metric] = random.uniform(50, 200)
            elif "count" in metric:
                data[metric] = random.randint(0, 100)
            else:
                data[metric] = random.uniform(0, 1000)
        
        return data
        
    def _get_refresh_seconds(self, refresh_rate: RefreshRate) -> int:
        """Get refresh interval in seconds"""
        refresh_map = {
            RefreshRate.REAL_TIME: 5,
            RefreshRate.FAST: 30,
            RefreshRate.NORMAL: 60,
            RefreshRate.SLOW: 300,
            RefreshRate.MANUAL: 3600  # 1 hour for manual refresh
        }
        return refresh_map.get(refresh_rate, 60)
        
    async def subscribe_to_dashboard(self, dashboard_id: str, user_id: str) -> bool:
        """Subscribe user to dashboard updates"""
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        if dashboard_id not in self.active_subscriptions:
            self.active_subscriptions[dashboard_id] = []
        
        if user_id not in self.active_subscriptions[dashboard_id]:
            self.active_subscriptions[dashboard_id].append(user_id)
        
        self.logger.info(f"User {user_id} subscribed to dashboard {dashboard_id}")
        
        return True
        
    async def unsubscribe_from_dashboard(self, dashboard_id: str, user_id: str) -> bool:
        """Unsubscribe user from dashboard updates"""
        if dashboard_id in self.active_subscriptions:
            if user_id in self.active_subscriptions[dashboard_id]:
                self.active_subscriptions[dashboard_id].remove(user_id)
                
                # Clean up empty subscription lists
                if not self.active_subscriptions[dashboard_id]:
                    del self.active_subscriptions[dashboard_id]
        
        self.logger.info(f"User {user_id} unsubscribed from dashboard {dashboard_id}")
        
        return True
        
    async def get_dashboard_list(self, user_permissions: List[str] = None) -> List[Dict[str, Any]]:
        """Get list of available dashboards for user"""
        dashboard_list = []
        
        for dashboard_id, dashboard in self.dashboards.items():
            # Check user permissions
            if user_permissions:
                has_access = any(
                    perm in dashboard.access_permissions 
                    for perm in user_permissions
                )
                if not has_access:
                    continue
            
            dashboard_info = {
                "dashboard_id": dashboard_id,
                "name": dashboard.name,
                "dashboard_type": dashboard.dashboard_type.value,
                "description": dashboard.description,
                "widget_count": len(dashboard.widgets),
                "last_updated": dashboard.updated_at.isoformat(),
                "refresh_rate": dashboard.refresh_rate.value
            }
            
            dashboard_list.append(dashboard_info)
        
        return dashboard_list
        
    async def export_dashboard_config(self, dashboard_id: str) -> Dict[str, Any]:
        """Export dashboard configuration for backup/sharing"""
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        dashboard = self.dashboards[dashboard_id]
        
        # Convert dashboard to exportable format
        config = {
            "dashboard_id": dashboard.dashboard_id,
            "name": dashboard.name,
            "dashboard_type": dashboard.dashboard_type.value,
            "description": dashboard.description,
            "layout": dashboard.layout,
            "refresh_rate": dashboard.refresh_rate.value,
            "widgets": []
        }
        
        for widget in dashboard.widgets:
            widget_config = {
                "widget_id": widget.widget_id,
                "title": widget.title,
                "visualization_type": widget.visualization_type.value,
                "data_source": widget.data_source,
                "metrics": widget.metrics,
                "time_range": widget.time_range,
                "refresh_rate": widget.refresh_rate.value,
                "position": widget.position,
                "configuration": widget.configuration,
                "filters": widget.filters
            }
            config["widgets"].append(widget_config)
        
        return config
        
    async def import_dashboard_config(self, config: Dict[str, Any], 
                                    new_dashboard_id: str = None) -> str:
        """Import dashboard configuration"""
        dashboard_id = new_dashboard_id or config["dashboard_id"]
        
        # Create widgets
        widgets = []
        for widget_config in config["widgets"]:
            widget = DashboardWidget(
                widget_id=widget_config["widget_id"],
                title=widget_config["title"],
                visualization_type=VisualizationType(widget_config["visualization_type"]),
                data_source=widget_config["data_source"],
                metrics=widget_config["metrics"],
                time_range=widget_config["time_range"],
                refresh_rate=RefreshRate(widget_config["refresh_rate"]),
                position=widget_config["position"],
                configuration=widget_config.get("configuration", {}),
                filters=widget_config.get("filters", {})
            )
            widgets.append(widget)
        
        # Create dashboard
        dashboard = await self.create_dashboard(
            dashboard_id=dashboard_id,
            name=config["name"],
            dashboard_type=DashboardType(config["dashboard_type"]),
            description=config["description"],
            widgets=widgets,
            access_permissions=["all"]  # Default permissions
        )
        
        self.logger.info(f"Dashboard imported: {dashboard_id}")
        
        return dashboard_id
        
    async def get_dashboard_analytics(self, dashboard_id: str, 
                                    days: int = 7) -> Dict[str, Any]:
        """Get dashboard usage analytics"""
        # This would typically pull from actual analytics data
        # For now, returning simulated analytics
        
        analytics = {
            "dashboard_id": dashboard_id,
            "period_days": days,
            "usage_metrics": {
                "total_views": 245,
                "unique_users": 18,
                "avg_session_duration_minutes": 12.5,
                "peak_usage_hour": 14,  # 2 PM
                "most_viewed_widget": "exec_overall_compliance"
            },
            "performance_metrics": {
                "avg_load_time_ms": 850,
                "cache_hit_rate": 78.5,
                "error_rate": 0.2
            },
            "user_engagement": {
                "widget_interactions": 156,
                "filter_changes": 23,
                "export_requests": 8
            }
        }
        
        return analytics

# Global SLA dashboard manager instance
sla_dashboard_manager = SLADashboardManager()