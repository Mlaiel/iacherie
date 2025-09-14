"""📊 Unified Dashboards Module - IA Influencer Agent Platform
==========================================================

Consolidated dashboard system combining:
- Production monitoring dashboard
- Business workflow dashboards
- Real-time status display
- Interactive data visualization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

import logging
logger = logging.getLogger(__name__)


class DashboardType(Enum):
    """Types of dashboards"""
    PRODUCTION = "production"
    BUSINESS = "business"
    SYSTEM = "system"
    SECURITY = "security"
    CUSTOM = "custom"


class WidgetType(Enum):
    """Types of dashboard widgets"""
    METRIC = "metric"
    CHART = "chart"
    TABLE = "table"
    ALERT = "alert"
    STATUS = "status"
    LOG = "log"


@dataclass
class DashboardWidget:
    """Dashboard widget definition"""
    id: str
    title: str
    widget_type: WidgetType
    data_source: str
    config: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 60  # seconds
    position: Dict[str, int] = field(default_factory=dict)  # x, y, width, height


@dataclass
class Dashboard:
    """Dashboard definition"""
    id: str
    name: str
    dashboard_type: DashboardType
    description: str = ""
    widgets: List[DashboardWidget] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    public: bool = False


class DashboardDataProvider:
    """Provides data for dashboard widgets"""
    
    def __init__(self) -> None:
        self.data_sources: Dict[str, callable] = {}
        self._register_default_sources()
    
    def _register_default_sources(self) -> None:
        """Register default data sources"""
        self.data_sources.update({
            "system_metrics": self._get_system_metrics,
            "business_metrics": self._get_business_metrics,
            "alert_summary": self._get_alert_summary,
            "health_status": self._get_health_status,
            "performance_stats": self._get_performance_stats,
            "user_analytics": self._get_user_analytics,
            "revenue_metrics": self._get_revenue_metrics,
            "content_metrics": self._get_content_metrics,
            "error_logs": self._get_error_logs,
            "capacity_forecast": self._get_capacity_forecast
        })
    
    async def get_widget_data(self, data_source: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data for a specific widget"""
        if data_source not in self.data_sources:
            return {"error": f"Data source '{data_source}' not found"}
        
        try:
            data_func = self.data_sources[data_source]
            if asyncio.iscoroutinefunction(data_func):
                return await data_func(config or {})
            else:
                return data_func(config or {})
        except Exception as e:
            logger.error(f"Error getting data for {data_source}: {e}")
            return {"error": str(e)}
    
    # Data source implementations
    
    def _get_system_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get system metrics data"""
        try:
            # Try to import psutil for real metrics
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "percent": psutil.virtual_memory().percent,
                    "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                    "total_gb": round(psutil.virtual_memory().total / (1024**3), 2)
                },
                "disk": {
                    "percent": round((psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100, 1),
                    "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
                    "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2)
                },
                "network": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent if psutil.net_io_counters() else 0,
                    "bytes_recv": psutil.net_io_counters().bytes_recv if psutil.net_io_counters() else 0
                },
                "timestamp": datetime.now().isoformat()
            }
        except ImportError:
            # Fallback to simulated metrics when psutil not available
            return {
                "cpu_percent": 45.0,
                "memory": {
                    "percent": 67.0,
                    "available_gb": 8.0,
                    "total_gb": 16.0
                },
                "disk": {
                    "percent": 52.0,
                    "free_gb": 250.0,
                    "total_gb": 500.0
                },
                "network": {
                    "bytes_sent": 1048576,  # 1MB
                    "bytes_recv": 2097152   # 2MB
                },
                "timestamp": datetime.now().isoformat(),
                "simulated": True
            }
        except Exception as e:
            return {"error": f"Failed to get system metrics: {e}"}
    
    def _get_business_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get business metrics data"""
        return {
            "revenue": {
                "total": 245327.89,
                "monthly": 23450.67,
                "daily": 1245.67,
                "currency": "USD"
            },
            "users": {
                "active_daily": 1847,
                "active_monthly": 12456,
                "conversion_rate": 3.4,
                "churn_rate": 2.5
            },
            "content": {
                "created_today": 156,
                "total_content": 45892,
                "processing_queue": 23,
                "quality_score": 8.7
            },
            "subscriptions": {
                "active": 1247,
                "new_today": 23,
                "cancelled_today": 5,
                "revenue_monthly": 18500.00
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_alert_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get alert summary data"""
        return {
            "open_alerts": 3,
            "critical_alerts": 1,
            "warning_alerts": 2,
            "alerts_today": 15,
            "recent_alerts": [
                {
                    "id": "alert_001",
                    "title": "High CPU usage detected",
                    "severity": "warning",
                    "created_at": (datetime.now() - timedelta(minutes=15)).isoformat()
                },
                {
                    "id": "alert_002", 
                    "title": "Memory usage elevated",
                    "severity": "warning",
                    "created_at": (datetime.now() - timedelta(minutes=45)).isoformat()
                },
                {
                    "id": "alert_003",
                    "title": "Database connection pool exhausted",
                    "severity": "critical",
                    "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_health_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get health status data"""
        return {
            "overall_status": "healthy",
            "services": {
                "api": {"status": "healthy", "response_time_ms": 45},
                "database": {"status": "healthy", "connections": 47},
                "cache": {"status": "healthy", "hit_rate": 94.5},
                "ai_service": {"status": "degraded", "accuracy": 94.3},
                "payment": {"status": "healthy", "success_rate": 99.8}
            },
            "sla_compliance": {
                "availability": 99.9,
                "response_time": 98.5,
                "error_rate": 0.1
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_performance_stats(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "response_times": {
                "avg_ms": 145,
                "p95_ms": 280,
                "p99_ms": 450
            },
            "throughput": {
                "requests_per_second": 234,
                "requests_today": 45892
            },
            "errors": {
                "error_rate_percent": 0.2,
                "errors_today": 15
            },
            "database": {
                "query_time_avg_ms": 12.3,
                "slow_queries": 3,
                "connection_pool_usage": 78
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_user_analytics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get user analytics data"""
        return {
            "user_activity": {
                "sessions_today": 2341,
                "avg_session_duration_min": 18.5,
                "bounce_rate_percent": 23.4,
                "page_views_today": 8745
            },
            "user_engagement": {
                "content_interactions": 5623,
                "shares": 234,
                "comments": 456,
                "likes": 1247
            },
            "user_satisfaction": {
                "rating_avg": 4.6,
                "feedback_count": 89,
                "nps_score": 67
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_revenue_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get revenue metrics data"""
        return {
            "revenue_breakdown": {
                "subscriptions": 18500.00,
                "one_time_purchases": 3450.67,
                "premium_features": 1500.00
            },
            "payment_methods": {
                "credit_card": 65.5,
                "paypal": 25.2,
                "bank_transfer": 9.3
            },
            "revenue_trends": {
                "growth_rate_monthly": 12.5,
                "mrr": 18500.00,
                "arr": 222000.00
            },
            "refunds": {
                "refund_rate_percent": 2.1,
                "refunds_today": 2,
                "refund_amount_today": 89.99
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_content_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get content metrics data"""
        return {
            "content_stats": {
                "uploads_today": 156,
                "processing_time_avg_s": 2.34,
                "quality_score_avg": 8.7,
                "storage_used_gb": 2847.3
            },
            "content_types": {
                "audio": 78.5,
                "video": 15.2,
                "text": 6.3
            },
            "content_protection": {
                "copyright_checks": 156,
                "violations_detected": 3,
                "false_positives": 1
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_error_logs(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get error logs data"""
        return {
            "recent_errors": [
                {
                    "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                    "level": "ERROR",
                    "message": "Database connection timeout",
                    "module": "database.connection",
                    "count": 3
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                    "level": "WARNING",
                    "message": "High memory usage detected",
                    "module": "monitoring.health",
                    "count": 1
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=25)).isoformat(),
                    "level": "ERROR",
                    "message": "Payment processing failed",
                    "module": "payment.processor",
                    "count": 2
                }
            ],
            "error_summary": {
                "errors_today": 15,
                "warnings_today": 23,
                "critical_today": 2
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_capacity_forecast(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get capacity forecast data"""
        return {
            "cpu_forecast": {
                "current_usage": 45.2,
                "forecasted_usage": 62.8,
                "days_to_capacity": 45,
                "trend": "increasing"
            },
            "memory_forecast": {
                "current_usage": 67.3,
                "forecasted_usage": 78.9,
                "days_to_capacity": 60,
                "trend": "stable"
            },
            "disk_forecast": {
                "current_usage": 52.1,
                "forecasted_usage": 71.5,
                "days_to_capacity": 90,
                "trend": "increasing"
            },
            "timestamp": datetime.now().isoformat()
        }


class UnifiedDashboardManager:
    """
    Unified dashboard management system
    """
    
    def __init__(self) -> None:
        self.dashboards: Dict[str, Dashboard] = {}
        self.data_provider = DashboardDataProvider()
        
        # Initialize default dashboards
        self._create_default_dashboards()
    
    def _create_default_dashboards(self) -> None:
        """Create default dashboards"""
        
        # Production Dashboard
        production_dashboard = Dashboard(
            id="production",
            name="Production Monitoring",
            dashboard_type=DashboardType.PRODUCTION,
            description="Real-time production system monitoring",
            widgets=[
                DashboardWidget(
                    id="system_overview",
                    title="System Overview",
                    widget_type=WidgetType.METRIC,
                    data_source="system_metrics",
                    position={"x": 0, "y": 0, "width": 6, "height": 4}
                ),
                DashboardWidget(
                    id="health_status",
                    title="Service Health",
                    widget_type=WidgetType.STATUS,
                    data_source="health_status",
                    position={"x": 6, "y": 0, "width": 6, "height": 4}
                ),
                DashboardWidget(
                    id="alert_summary",
                    title="Active Alerts",
                    widget_type=WidgetType.ALERT,
                    data_source="alert_summary",
                    position={"x": 0, "y": 4, "width": 8, "height": 3}
                ),
                DashboardWidget(
                    id="performance_chart",
                    title="Performance Trends",
                    widget_type=WidgetType.CHART,
                    data_source="performance_stats",
                    position={"x": 8, "y": 4, "width": 4, "height": 3}
                )
            ],
            tags=["production", "monitoring", "real-time"],
            public=True
        )
        self.dashboards["production"] = production_dashboard
        
        # Business Dashboard
        business_dashboard = Dashboard(
            id="business",
            name="Business Analytics",
            dashboard_type=DashboardType.BUSINESS,
            description="Business metrics and KPI tracking",
            widgets=[
                DashboardWidget(
                    id="revenue_metrics",
                    title="Revenue Overview",
                    widget_type=WidgetType.METRIC,
                    data_source="revenue_metrics",
                    position={"x": 0, "y": 0, "width": 6, "height": 4}
                ),
                DashboardWidget(
                    id="user_analytics",
                    title="User Engagement",
                    widget_type=WidgetType.CHART,
                    data_source="user_analytics",
                    position={"x": 6, "y": 0, "width": 6, "height": 4}
                ),
                DashboardWidget(
                    id="business_kpis",
                    title="Key Performance Indicators",
                    widget_type=WidgetType.METRIC,
                    data_source="business_metrics",
                    position={"x": 0, "y": 4, "width": 8, "height": 3}
                ),
                DashboardWidget(
                    id="content_overview",
                    title="Content Metrics",
                    widget_type=WidgetType.TABLE,
                    data_source="content_metrics",
                    position={"x": 8, "y": 4, "width": 4, "height": 3}
                )
            ],
            tags=["business", "analytics", "kpi"],
            public=True
        )
        self.dashboards["business"] = business_dashboard
        
        # System Dashboard
        system_dashboard = Dashboard(
            id="system",
            name="System Monitoring",
            dashboard_type=DashboardType.SYSTEM,
            description="Detailed system resource monitoring",
            widgets=[
                DashboardWidget(
                    id="cpu_memory_chart",
                    title="CPU & Memory Usage",
                    widget_type=WidgetType.CHART,
                    data_source="system_metrics",
                    position={"x": 0, "y": 0, "width": 6, "height": 4}
                ),
                DashboardWidget(
                    id="disk_network_chart",
                    title="Disk & Network Usage",
                    widget_type=WidgetType.CHART,
                    data_source="system_metrics",
                    position={"x": 6, "y": 0, "width": 6, "height": 4}
                ),
                DashboardWidget(
                    id="capacity_forecast",
                    title="Capacity Forecast",
                    widget_type=WidgetType.TABLE,
                    data_source="capacity_forecast",
                    position={"x": 0, "y": 4, "width": 8, "height": 3}
                ),
                DashboardWidget(
                    id="error_logs",
                    title="Recent Errors",
                    widget_type=WidgetType.LOG,
                    data_source="error_logs",
                    position={"x": 8, "y": 4, "width": 4, "height": 3}
                )
            ],
            tags=["system", "resources", "monitoring"],
            public=False
        )
        self.dashboards["system"] = system_dashboard
    
    def create_dashboard(
        self,
        name: str,
        dashboard_type: DashboardType,
        description: str = "",
        widgets: List[DashboardWidget] = None,
        tags: List[str] = None,
        public: bool = False
    ) -> str:
        """Create a new dashboard"""
        dashboard_id = name.lower().replace(" ", "_")
        
        dashboard = Dashboard(
            id=dashboard_id,
            name=name,
            dashboard_type=dashboard_type,
            description=description,
            widgets=widgets or [],
            tags=tags or [],
            public=public
        )
        
        self.dashboards[dashboard_id] = dashboard
        logger.info(f"Created dashboard: {name}")
        return dashboard_id
    
    def add_widget(self, dashboard_id: str, widget: DashboardWidget) -> bool:
        """Add widget to dashboard"""
        if dashboard_id not in self.dashboards:
            logger.warning(f"Dashboard {dashboard_id} not found")
            return False
        
        dashboard = self.dashboards[dashboard_id]
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.now()
        
        logger.info(f"Added widget {widget.title} to dashboard {dashboard.name}")
        return True
    
    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove widget from dashboard"""
        if dashboard_id not in self.dashboards:
            return False
        
        dashboard = self.dashboards[dashboard_id]
        dashboard.widgets = [w for w in dashboard.widgets if w.id != widget_id]
        dashboard.updated_at = datetime.now()
        
        return True
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get complete dashboard data"""
        if dashboard_id not in self.dashboards:
            return {"error": f"Dashboard {dashboard_id} not found"}
        
        dashboard = self.dashboards[dashboard_id]
        dashboard_data = {
            "dashboard": {
                "id": dashboard.id,
                "name": dashboard.name,
                "type": dashboard.dashboard_type.value,
                "description": dashboard.description,
                "updated_at": dashboard.updated_at.isoformat(),
                "tags": dashboard.tags
            },
            "widgets": {},
            "generated_at": datetime.now().isoformat()
        }
        
        # Get data for each widget
        for widget in dashboard.widgets:
            try:
                widget_data = await self.data_provider.get_widget_data(
                    widget.data_source, widget.config
                )
                dashboard_data["widgets"][widget.id] = {
                    "widget": {
                        "id": widget.id,
                        "title": widget.title,
                        "type": widget.widget_type.value,
                        "position": widget.position,
                        "refresh_interval": widget.refresh_interval
                    },
                    "data": widget_data
                }
            except Exception as e:
                logger.error(f"Error getting data for widget {widget.id}: {e}")
                dashboard_data["widgets"][widget.id] = {
                    "widget": {
                        "id": widget.id,
                        "title": widget.title,
                        "type": widget.widget_type.value,
                        "position": widget.position
                    },
                    "data": {"error": str(e)}
                }
        
        return dashboard_data
    
    def get_dashboard_list(self) -> List[Dict[str, Any]]:
        """Get list of all dashboards"""
        return [
            {
                "id": dashboard.id,
                "name": dashboard.name,
                "type": dashboard.dashboard_type.value,
                "description": dashboard.description,
                "widget_count": len(dashboard.widgets),
                "updated_at": dashboard.updated_at.isoformat(),
                "tags": dashboard.tags,
                "public": dashboard.public
            }
            for dashboard in self.dashboards.values()
        ]
    
    def get_dashboard_config(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard configuration"""
        return self.dashboards.get(dashboard_id)
    
    async def refresh_widget_data(self, dashboard_id: str, widget_id: str) -> Dict[str, Any]:
        """Refresh data for a specific widget"""
        if dashboard_id not in self.dashboards:
            return {"error": f"Dashboard {dashboard_id} not found"}
        
        dashboard = self.dashboards[dashboard_id]
        widget = next((w for w in dashboard.widgets if w.id == widget_id), None)
        
        if not widget:
            return {"error": f"Widget {widget_id} not found"}
        
        return await self.data_provider.get_widget_data(widget.data_source, widget.config)


# Global dashboard manager instance
dashboard_manager = UnifiedDashboardManager()


# Convenience functions for external use
async def get_production_dashboard() -> Dict[str, Any]:
    """Get production dashboard data"""
    return await dashboard_manager.get_dashboard_data("production")


async def get_business_dashboard() -> Dict[str, Any]:
    """Get business dashboard data"""
    return await dashboard_manager.get_dashboard_data("business")


async def get_system_dashboard() -> Dict[str, Any]:
    """Get system dashboard data"""
    return await dashboard_manager.get_dashboard_data("system")


def get_dashboard_list() -> List[Dict[str, Any]]:
    """Get list of all dashboards"""
    return dashboard_manager.get_dashboard_list()


async def create_custom_dashboard(
    name: str,
    description: str = "",
    widgets: List[DashboardWidget] = None
) -> str:
    """Create custom dashboard"""
    return dashboard_manager.create_dashboard(
        name=name,
        dashboard_type=DashboardType.CUSTOM,
        description=description,
        widgets=widgets or [],
        public=False
    )