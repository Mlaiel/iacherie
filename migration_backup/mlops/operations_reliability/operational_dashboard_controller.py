"""
🛡️ MLOps Operations & Reliability - Operational Dashboard Controller
=====================================================================

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Enterprise operational dashboard controller for Creator Economy executive reporting.
Combining expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics


class DashboardType(Enum):
    """Dashboard types"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    CREATOR_FOCUSED = "creator_focused"
    FINANCIAL = "financial"


class MetricSeverity(Enum):
    """Metric severity levels"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DashboardUpdateFrequency(Enum):
    """Dashboard update frequencies"""
    REAL_TIME = "real_time"      # < 1 minute
    NEAR_REAL_TIME = "near_real_time"  # 1-5 minutes  
    PERIODIC = "periodic"        # 5-30 minutes
    HOURLY = "hourly"           # 1 hour
    DAILY = "daily"             # 24 hours


@dataclass
class DashboardMetric:
    """Dashboard metric definition"""
    metric_id: str
    name: str
    description: str
    current_value: float
    target_value: Optional[float]
    unit: str
    severity: MetricSeverity
    trend: str  # "up", "down", "stable"
    change_percentage: float
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    title: str
    widget_type: str  # "metric", "chart", "table", "alert", "status"
    metrics: List[str]  # Metric IDs
    position: Dict[str, int]  # {"x": 0, "y": 0, "width": 4, "height": 2}
    refresh_interval: timedelta
    visible: bool = True
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Dashboard definition"""
    dashboard_id: str
    name: str
    description: str
    dashboard_type: DashboardType
    widgets: List[DashboardWidget]
    access_roles: List[str]
    update_frequency: DashboardUpdateFrequency
    auto_refresh: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class AlertSummary:
    """Alert summary for dashboard"""
    total_alerts: int
    critical_alerts: int
    warning_alerts: int
    resolved_in_last_hour: int
    average_resolution_time: timedelta
    top_alert_sources: List[Dict[str, Any]]


class OperationalDashboardController:
    """
    Enterprise operational dashboard controller for Creator Economy executive reporting.
    
    Provides comprehensive operational dashboards with real-time metrics,
    executive summaries, and creator-focused business intelligence.
    """
    
    def __init__(self):
        """Initialize operational dashboard controller"""
        self.logger = logging.getLogger(__name__)
        self.dashboards = {}
        self.metrics = {}
        self.widgets = {}
        self.dashboard_data_cache = {}
        self.subscribers = {}  # WebSocket connections for real-time updates
        
        # Initialize default dashboards
        self._setup_default_dashboards()
        
        self.logger.info("OperationalDashboardController initialized")
    
    def _setup_default_dashboards(self):
        """Setup default operational dashboards"""
        # Executive Dashboard
        executive_dashboard = self._create_executive_dashboard()
        self.dashboards[executive_dashboard.dashboard_id] = executive_dashboard
        
        # Technical Operations Dashboard
        tech_ops_dashboard = self._create_technical_operations_dashboard()
        self.dashboards[tech_ops_dashboard.dashboard_id] = tech_ops_dashboard
        
        # Creator Experience Dashboard
        creator_dashboard = self._create_creator_experience_dashboard()
        self.dashboards[creator_dashboard.dashboard_id] = creator_dashboard
        
        # Financial Impact Dashboard
        financial_dashboard = self._create_financial_impact_dashboard()
        self.dashboards[financial_dashboard.dashboard_id] = financial_dashboard
    
    def _create_executive_dashboard(self) -> Dashboard:
        """Create executive dashboard"""
        widgets = [
            DashboardWidget(
                widget_id="system_health_overview",
                title="System Health Overview",
                widget_type="status",
                metrics=["overall_system_health", "creator_satisfaction", "revenue_impact"],
                position={"x": 0, "y": 0, "width": 6, "height": 3},
                refresh_interval=timedelta(minutes=5)
            ),
            DashboardWidget(
                widget_id="creator_metrics_summary",
                title="Creator Metrics Summary",
                widget_type="metric",
                metrics=["active_creators", "content_uploads", "creator_revenue"],
                position={"x": 6, "y": 0, "width": 6, "height": 3},
                refresh_interval=timedelta(minutes=10)
            ),
            DashboardWidget(
                widget_id="sla_compliance",
                title="SLA Compliance",
                widget_type="chart",
                metrics=["sla_compliance_percentage", "slo_violations", "error_budget_burn"],
                position={"x": 0, "y": 3, "width": 8, "height": 4},
                refresh_interval=timedelta(minutes=15)
            ),
            DashboardWidget(
                widget_id="incident_summary",
                title="Incident Summary",
                widget_type="alert",
                metrics=["active_incidents", "mttr", "incident_trend"],
                position={"x": 8, "y": 3, "width": 4, "height": 4},
                refresh_interval=timedelta(minutes=5)
            )
        ]
        
        return Dashboard(
            dashboard_id="executive_dashboard",
            name="Executive Operations Dashboard",
            description="High-level operational metrics for executive team",
            dashboard_type=DashboardType.EXECUTIVE,
            widgets=widgets,
            access_roles=["cto", "ceo", "vp_engineering", "head_of_operations"],
            update_frequency=DashboardUpdateFrequency.PERIODIC
        )
    
    def _create_technical_operations_dashboard(self) -> Dashboard:
        """Create technical operations dashboard"""
        widgets = [
            DashboardWidget(
                widget_id="infrastructure_metrics",
                title="Infrastructure Metrics",
                widget_type="chart",
                metrics=["cpu_utilization", "memory_usage", "network_throughput", "disk_io"],
                position={"x": 0, "y": 0, "width": 6, "height": 4},
                refresh_interval=timedelta(minutes=1)
            ),
            DashboardWidget(
                widget_id="service_performance",
                title="Service Performance",
                widget_type="table",
                metrics=["response_times", "error_rates", "throughput", "availability"],
                position={"x": 6, "y": 0, "width": 6, "height": 4},
                refresh_interval=timedelta(minutes=2)
            ),
            DashboardWidget(
                widget_id="deployment_status",
                title="Deployment Status",
                widget_type="status",
                metrics=["active_deployments", "rollback_rate", "deployment_success"],
                position={"x": 0, "y": 4, "width": 4, "height": 3},
                refresh_interval=timedelta(minutes=5)
            ),
            DashboardWidget(
                widget_id="capacity_planning",
                title="Capacity Planning",
                widget_type="chart",
                metrics=["capacity_utilization", "scaling_events", "resource_forecast"],
                position={"x": 4, "y": 4, "width": 8, "height": 3},
                refresh_interval=timedelta(minutes=10)
            )
        ]
        
        return Dashboard(
            dashboard_id="technical_operations",
            name="Technical Operations Dashboard",
            description="Detailed technical metrics for operations team",
            dashboard_type=DashboardType.TECHNICAL,
            widgets=widgets,
            access_roles=["sre", "devops", "platform_engineer", "operations_lead"],
            update_frequency=DashboardUpdateFrequency.NEAR_REAL_TIME
        )
    
    def _create_creator_experience_dashboard(self) -> Dashboard:
        """Create creator experience dashboard"""
        widgets = [
            DashboardWidget(
                widget_id="creator_satisfaction_score",
                title="Creator Satisfaction Score",
                widget_type="metric",
                metrics=["nps_score", "support_tickets", "feature_requests"],
                position={"x": 0, "y": 0, "width": 4, "height": 3},
                refresh_interval=timedelta(minutes=15)
            ),
            DashboardWidget(
                widget_id="content_performance",
                title="Content Performance",
                widget_type="chart",
                metrics=["upload_success_rate", "processing_time", "delivery_speed"],
                position={"x": 4, "y": 0, "width": 8, "height": 3},
                refresh_interval=timedelta(minutes=5)
            ),
            DashboardWidget(
                widget_id="creator_tool_usage",
                title="Creator Tool Usage",
                widget_type="table",
                metrics=["tool_adoption", "feature_usage", "api_calls"],
                position={"x": 0, "y": 3, "width": 6, "height": 4},
                refresh_interval=timedelta(minutes=10)
            ),
            DashboardWidget(
                widget_id="monetization_metrics",
                title="Monetization Metrics",
                widget_type="chart",
                metrics=["revenue_per_creator", "payout_success_rate", "subscription_growth"],
                position={"x": 6, "y": 3, "width": 6, "height": 4},
                refresh_interval=timedelta(minutes=30)
            )
        ]
        
        return Dashboard(
            dashboard_id="creator_experience",
            name="Creator Experience Dashboard",
            description="Creator-focused metrics and experience indicators",
            dashboard_type=DashboardType.CREATOR_FOCUSED,
            widgets=widgets,
            access_roles=["creator_success", "product_manager", "customer_success"],
            update_frequency=DashboardUpdateFrequency.PERIODIC
        )
    
    def _create_financial_impact_dashboard(self) -> Dashboard:
        """Create financial impact dashboard"""
        widgets = [
            DashboardWidget(
                widget_id="revenue_impact",
                title="Revenue Impact",
                widget_type="metric",
                metrics=["revenue_at_risk", "downtime_cost", "sla_penalties"],
                position={"x": 0, "y": 0, "width": 6, "height": 2},
                refresh_interval=timedelta(minutes=30)
            ),
            DashboardWidget(
                widget_id="operational_costs",
                title="Operational Costs",
                widget_type="chart",
                metrics=["infrastructure_costs", "support_costs", "incident_costs"],
                position={"x": 6, "y": 0, "width": 6, "height": 2},
                refresh_interval=timedelta(hours=1)
            ),
            DashboardWidget(
                widget_id="roi_metrics",
                title="ROI Metrics",
                widget_type="table",
                metrics=["automation_savings", "efficiency_gains", "cost_avoidance"],
                position={"x": 0, "y": 2, "width": 12, "height": 3},
                refresh_interval=timedelta(hours=1)
            )
        ]
        
        return Dashboard(
            dashboard_id="financial_impact",
            name="Financial Impact Dashboard",
            description="Financial impact and cost analysis of operations",
            dashboard_type=DashboardType.FINANCIAL,
            widgets=widgets,
            access_roles=["cfo", "finance_director", "business_operations"],
            update_frequency=DashboardUpdateFrequency.HOURLY
        )
    
    async def update_metric(
        self,
        metric_id: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Update a dashboard metric
        
        Args:
            metric_id: Metric identifier
            value: New metric value
            timestamp: Update timestamp (default: now)
            
        Returns:
            True if metric updated successfully
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Get or create metric
            if metric_id in self.metrics:
                metric = self.metrics[metric_id]
                
                # Calculate trend and change
                old_value = metric.current_value
                change = value - old_value
                change_percentage = (change / old_value * 100) if old_value != 0 else 0
                
                if change > 0:
                    trend = "up"
                elif change < 0:
                    trend = "down"
                else:
                    trend = "stable"
                
                # Update metric
                metric.current_value = value
                metric.change_percentage = change_percentage
                metric.trend = trend
                metric.last_updated = timestamp
                
                # Update severity based on thresholds
                metric.severity = self._calculate_metric_severity(metric_id, value)
                
            else:
                # Create new metric
                metric = DashboardMetric(
                    metric_id=metric_id,
                    name=self._get_metric_display_name(metric_id),
                    description=self._get_metric_description(metric_id),
                    current_value=value,
                    target_value=self._get_metric_target(metric_id),
                    unit=self._get_metric_unit(metric_id),
                    severity=self._calculate_metric_severity(metric_id, value),
                    trend="stable",
                    change_percentage=0.0,
                    last_updated=timestamp
                )
                
                self.metrics[metric_id] = metric
            
            # Trigger dashboard updates
            await self._trigger_dashboard_updates(metric_id)
            
            self.logger.debug(f"Updated metric {metric_id}: {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating metric {metric_id}: {str(e)}")
            raise
    
    def _calculate_metric_severity(self, metric_id: str, value: float) -> MetricSeverity:
        """Calculate metric severity based on value and thresholds"""
        # Define thresholds for different metrics
        thresholds = {
            "cpu_utilization": {"warning": 75.0, "critical": 90.0, "emergency": 95.0},
            "memory_usage": {"warning": 80.0, "critical": 90.0, "emergency": 95.0},
            "error_rate": {"warning": 1.0, "critical": 5.0, "emergency": 10.0},
            "response_time": {"warning": 1000.0, "critical": 2000.0, "emergency": 5000.0},
            "availability": {"warning": 99.0, "critical": 98.0, "emergency": 95.0, "inverted": True},
            "sla_compliance": {"warning": 99.0, "critical": 98.0, "emergency": 95.0, "inverted": True}
        }
        
        metric_thresholds = thresholds.get(metric_id, {"warning": 80.0, "critical": 90.0, "emergency": 95.0})
        inverted = metric_thresholds.get("inverted", False)
        
        if inverted:
            # For metrics where lower is worse (availability, SLA compliance)
            if value <= metric_thresholds["emergency"]:
                return MetricSeverity.EMERGENCY
            elif value <= metric_thresholds["critical"]:
                return MetricSeverity.CRITICAL
            elif value <= metric_thresholds["warning"]:
                return MetricSeverity.WARNING
            else:
                return MetricSeverity.NORMAL
        else:
            # For metrics where higher is worse (CPU, memory, error rate)
            if value >= metric_thresholds["emergency"]:
                return MetricSeverity.EMERGENCY
            elif value >= metric_thresholds["critical"]:
                return MetricSeverity.CRITICAL
            elif value >= metric_thresholds["warning"]:
                return MetricSeverity.WARNING
            else:
                return MetricSeverity.NORMAL
    
    def _get_metric_display_name(self, metric_id: str) -> str:
        """Get display name for metric"""
        display_names = {
            "cpu_utilization": "CPU Utilization",
            "memory_usage": "Memory Usage",
            "error_rate": "Error Rate",
            "response_time": "Response Time",
            "availability": "Service Availability",
            "sla_compliance": "SLA Compliance",
            "active_creators": "Active Creators",
            "creator_satisfaction": "Creator Satisfaction",
            "revenue_impact": "Revenue Impact",
            "mttr": "Mean Time to Resolution",
            "active_incidents": "Active Incidents"
        }
        
        return display_names.get(metric_id, metric_id.replace("_", " ").title())
    
    def _get_metric_description(self, metric_id: str) -> str:
        """Get description for metric"""
        descriptions = {
            "cpu_utilization": "Average CPU utilization across all services",
            "memory_usage": "Memory usage percentage across infrastructure",
            "error_rate": "Error rate percentage for all services",
            "response_time": "Average response time in milliseconds",
            "availability": "Overall service availability percentage",
            "sla_compliance": "SLA compliance percentage",
            "active_creators": "Number of active creators on the platform",
            "creator_satisfaction": "Creator satisfaction score (NPS)",
            "revenue_impact": "Estimated revenue impact of operational issues"
        }
        
        return descriptions.get(metric_id, f"Metric: {metric_id}")
    
    def _get_metric_target(self, metric_id: str) -> Optional[float]:
        """Get target value for metric"""
        targets = {
            "cpu_utilization": 70.0,
            "memory_usage": 75.0,
            "error_rate": 0.1,
            "response_time": 500.0,
            "availability": 99.9,
            "sla_compliance": 99.5,
            "creator_satisfaction": 8.5,
            "mttr": 30.0  # 30 minutes
        }
        
        return targets.get(metric_id)
    
    def _get_metric_unit(self, metric_id: str) -> str:
        """Get unit for metric"""
        units = {
            "cpu_utilization": "%",
            "memory_usage": "%",
            "error_rate": "%",
            "response_time": "ms",
            "availability": "%",
            "sla_compliance": "%",
            "active_creators": "count",
            "creator_satisfaction": "score",
            "revenue_impact": "$",
            "mttr": "minutes",
            "active_incidents": "count"
        }
        
        return units.get(metric_id, "")
    
    async def _trigger_dashboard_updates(self, metric_id: str):
        """Trigger updates for dashboards that use this metric"""
        affected_dashboards = []
        
        # Find dashboards that use this metric
        for dashboard in self.dashboards.values():
            for widget in dashboard.widgets:
                if metric_id in widget.metrics:
                    affected_dashboards.append(dashboard.dashboard_id)
                    break
        
        # Update dashboard data cache
        for dashboard_id in affected_dashboards:
            await self._update_dashboard_cache(dashboard_id)
            
            # Notify real-time subscribers
            if dashboard_id in self.subscribers:
                await self._notify_subscribers(dashboard_id, metric_id)
    
    async def _update_dashboard_cache(self, dashboard_id: str):
        """Update dashboard data cache"""
        if dashboard_id not in self.dashboards:
            return
        
        dashboard = self.dashboards[dashboard_id]
        dashboard_data = await self._generate_dashboard_data(dashboard)
        
        self.dashboard_data_cache[dashboard_id] = {
            'data': dashboard_data,
            'last_updated': datetime.now(),
            'dashboard_info': {
                'id': dashboard.dashboard_id,
                'name': dashboard.name,
                'type': dashboard.dashboard_type.value,
                'auto_refresh': dashboard.auto_refresh,
                'update_frequency': dashboard.update_frequency.value
            }
        }
    
    async def _generate_dashboard_data(self, dashboard: Dashboard) -> Dict[str, Any]:
        """Generate dashboard data"""
        dashboard_data = {
            'widgets': [],
            'summary': await self._generate_dashboard_summary(dashboard),
            'alerts': await self._generate_alert_summary(),
            'last_updated': datetime.now().isoformat()
        }
        
        # Generate data for each widget
        for widget in dashboard.widgets:
            widget_data = await self._generate_widget_data(widget)
            dashboard_data['widgets'].append(widget_data)
        
        return dashboard_data
    
    async def _generate_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Generate data for a widget"""
        widget_data = {
            'widget_id': widget.widget_id,
            'title': widget.title,
            'type': widget.widget_type,
            'position': widget.position,
            'metrics': [],
            'status': 'normal',
            'last_updated': datetime.now().isoformat()
        }
        
        # Collect metric data
        highest_severity = MetricSeverity.NORMAL
        
        for metric_id in widget.metrics:
            if metric_id in self.metrics:
                metric = self.metrics[metric_id]
                
                metric_data = {
                    'id': metric.metric_id,
                    'name': metric.name,
                    'value': metric.current_value,
                    'target': metric.target_value,
                    'unit': metric.unit,
                    'severity': metric.severity.value,
                    'trend': metric.trend,
                    'change_percentage': metric.change_percentage,
                    'last_updated': metric.last_updated.isoformat()
                }
                
                widget_data['metrics'].append(metric_data)
                
                # Update widget status based on highest severity
                severity_order = [MetricSeverity.NORMAL, MetricSeverity.WARNING, 
                                MetricSeverity.CRITICAL, MetricSeverity.EMERGENCY]
                if severity_order.index(metric.severity) > severity_order.index(highest_severity):
                    highest_severity = metric.severity
        
        widget_data['status'] = highest_severity.value
        
        # Generate widget-specific data based on type
        if widget.widget_type == "chart":
            widget_data['chart_data'] = await self._generate_chart_data(widget.metrics)
        elif widget.widget_type == "table":
            widget_data['table_data'] = await self._generate_table_data(widget.metrics)
        elif widget.widget_type == "status":
            widget_data['status_data'] = await self._generate_status_data(widget.metrics)
        
        return widget_data
    
    async def _generate_chart_data(self, metric_ids: List[str]) -> Dict[str, Any]:
        """Generate chart data for metrics"""
        # Simulate time series data
        time_points = []
        current_time = datetime.now()
        
        for i in range(24):  # Last 24 hours
            time_points.append(current_time - timedelta(hours=23-i))
        
        chart_data = {
            'time_series': [t.isoformat() for t in time_points],
            'datasets': []
        }
        
        for metric_id in metric_ids:
            if metric_id in self.metrics:
                metric = self.metrics[metric_id]
                
                # Generate sample data points
                data_points = []
                base_value = metric.current_value
                
                for i in range(24):
                    # Add some variation around current value
                    variation = (i - 12) * 0.1  # Slight trend
                    noise = (time.time() % (i + 1)) * 0.05  # Random-ish noise
                    value = max(0, base_value + variation + noise)
                    data_points.append(round(value, 2))
                
                dataset = {
                    'metric_id': metric_id,
                    'name': metric.name,
                    'data': data_points,
                    'unit': metric.unit,
                    'color': self._get_metric_color(metric_id)
                }
                
                chart_data['datasets'].append(dataset)
        
        return chart_data
    
    async def _generate_table_data(self, metric_ids: List[str]) -> Dict[str, Any]:
        """Generate table data for metrics"""
        table_data = {
            'headers': ['Metric', 'Current', 'Target', 'Status', 'Trend'],
            'rows': []
        }
        
        for metric_id in metric_ids:
            if metric_id in self.metrics:
                metric = self.metrics[metric_id]
                
                row = {
                    'metric': metric.name,
                    'current': f"{metric.current_value}{metric.unit}",
                    'target': f"{metric.target_value}{metric.unit}" if metric.target_value else "N/A",
                    'status': metric.severity.value,
                    'trend': f"{metric.trend} ({metric.change_percentage:+.1f}%)"
                }
                
                table_data['rows'].append(row)
        
        return table_data
    
    async def _generate_status_data(self, metric_ids: List[str]) -> Dict[str, Any]:
        """Generate status data for metrics"""
        status_data = {
            'overall_status': 'normal',
            'status_items': []
        }
        
        highest_severity = MetricSeverity.NORMAL
        
        for metric_id in metric_ids:
            if metric_id in self.metrics:
                metric = self.metrics[metric_id]
                
                status_item = {
                    'name': metric.name,
                    'status': metric.severity.value,
                    'value': f"{metric.current_value}{metric.unit}",
                    'message': self._get_status_message(metric)
                }
                
                status_data['status_items'].append(status_item)
                
                # Update overall status
                severity_order = [MetricSeverity.NORMAL, MetricSeverity.WARNING,
                                MetricSeverity.CRITICAL, MetricSeverity.EMERGENCY]
                if severity_order.index(metric.severity) > severity_order.index(highest_severity):
                    highest_severity = metric.severity
        
        status_data['overall_status'] = highest_severity.value
        
        return status_data
    
    def _get_metric_color(self, metric_id: str) -> str:
        """Get color for metric visualization"""
        colors = {
            "cpu_utilization": "#FF6B6B",
            "memory_usage": "#4ECDC4",
            "error_rate": "#FF8C42",
            "response_time": "#6BCF7F",
            "availability": "#4D96FF",
            "sla_compliance": "#9B59B6",
            "active_creators": "#1ABC9C",
            "creator_satisfaction": "#F39C12"
        }
        
        return colors.get(metric_id, "#95A5A6")
    
    def _get_status_message(self, metric: DashboardMetric) -> str:
        """Get status message for metric"""
        if metric.severity == MetricSeverity.NORMAL:
            return "Operating normally"
        elif metric.severity == MetricSeverity.WARNING:
            return f"Above warning threshold ({metric.target_value}{metric.unit})"
        elif metric.severity == MetricSeverity.CRITICAL:
            return "Critical threshold exceeded - immediate attention required"
        elif metric.severity == MetricSeverity.EMERGENCY:
            return "Emergency threshold exceeded - escalating to on-call team"
        else:
            return "Unknown status"
    
    async def _generate_dashboard_summary(self, dashboard: Dashboard) -> Dict[str, Any]:
        """Generate dashboard summary"""
        # Count metrics by severity
        severity_counts = {
            'normal': 0,
            'warning': 0,
            'critical': 0,
            'emergency': 0
        }
        
        # Get all metrics used in dashboard
        dashboard_metrics = set()
        for widget in dashboard.widgets:
            dashboard_metrics.update(widget.metrics)
        
        for metric_id in dashboard_metrics:
            if metric_id in self.metrics:
                severity = self.metrics[metric_id].severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate overall health score
        total_metrics = sum(severity_counts.values())
        if total_metrics > 0:
            health_score = (
                severity_counts['normal'] * 100 +
                severity_counts['warning'] * 75 +
                severity_counts['critical'] * 25 +
                severity_counts['emergency'] * 0
            ) / total_metrics
        else:
            health_score = 100
        
        return {
            'total_metrics': total_metrics,
            'health_score': round(health_score, 1),
            'severity_distribution': severity_counts,
            'last_updated': datetime.now().isoformat()
        }
    
    async def _generate_alert_summary(self) -> AlertSummary:
        """Generate alert summary for dashboard"""
        # Simulate alert data
        return AlertSummary(
            total_alerts=15,
            critical_alerts=2,
            warning_alerts=8,
            resolved_in_last_hour=5,
            average_resolution_time=timedelta(minutes=25),
            top_alert_sources=[
                {"source": "creator_api", "count": 5},
                {"source": "payment_system", "count": 3},
                {"source": "content_delivery", "count": 2}
            ]
        )
    
    async def _notify_subscribers(self, dashboard_id: str, metric_id: str):
        """Notify real-time subscribers of metric updates"""
        if dashboard_id in self.subscribers:
            for subscriber in self.subscribers[dashboard_id]:
                try:
                    update_message = {
                        'type': 'metric_update',
                        'dashboard_id': dashboard_id,
                        'metric_id': metric_id,
                        'metric_data': self.metrics[metric_id].__dict__ if metric_id in self.metrics else None,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # In real implementation, would send via WebSocket
                    self.logger.debug(f"Notifying subscriber of metric update: {metric_id}")
                    
                except Exception as e:
                    self.logger.error(f"Error notifying subscriber: {str(e)}")
    
    async def get_dashboard_data(
        self,
        dashboard_id: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get dashboard data
        
        Args:
            dashboard_id: Dashboard identifier
            force_refresh: Force refresh of cached data
            
        Returns:
            Dashboard data or None if not found
        """
        try:
            if dashboard_id not in self.dashboards:
                return None
            
            # Check if we need to refresh cache
            should_refresh = force_refresh
            
            if dashboard_id in self.dashboard_data_cache:
                cache_entry = self.dashboard_data_cache[dashboard_id]
                dashboard = self.dashboards[dashboard_id]
                
                # Check if cache is stale based on update frequency
                cache_age = datetime.now() - cache_entry['last_updated']
                
                if dashboard.update_frequency == DashboardUpdateFrequency.REAL_TIME:
                    should_refresh = cache_age > timedelta(minutes=1)
                elif dashboard.update_frequency == DashboardUpdateFrequency.NEAR_REAL_TIME:
                    should_refresh = cache_age > timedelta(minutes=5)
                elif dashboard.update_frequency == DashboardUpdateFrequency.PERIODIC:
                    should_refresh = cache_age > timedelta(minutes=15)
                elif dashboard.update_frequency == DashboardUpdateFrequency.HOURLY:
                    should_refresh = cache_age > timedelta(hours=1)
                elif dashboard.update_frequency == DashboardUpdateFrequency.DAILY:
                    should_refresh = cache_age > timedelta(days=1)
            else:
                should_refresh = True
            
            if should_refresh:
                await self._update_dashboard_cache(dashboard_id)
            
            return self.dashboard_data_cache.get(dashboard_id)
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {str(e)}")
            raise
    
    async def get_available_dashboards(
        self,
        user_roles: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get list of available dashboards"""
        available_dashboards = []
        
        for dashboard in self.dashboards.values():
            # Check access permissions
            if user_roles:
                has_access = any(role in dashboard.access_roles for role in user_roles)
                if not has_access:
                    continue
            
            dashboard_info = {
                'dashboard_id': dashboard.dashboard_id,
                'name': dashboard.name,
                'description': dashboard.description,
                'type': dashboard.dashboard_type.value,
                'widget_count': len(dashboard.widgets),
                'update_frequency': dashboard.update_frequency.value,
                'auto_refresh': dashboard.auto_refresh,
                'last_updated': dashboard.last_updated.isoformat()
            }
            
            available_dashboards.append(dashboard_info)
        
        return available_dashboards
    
    def get_controller_status(self) -> Dict[str, Any]:
        """Get dashboard controller status"""
        return {
            'controller_name': 'OperationalDashboardController',
            'version': '1.0.0',
            'status': 'active',
            'dashboards_count': len(self.dashboards),
            'metrics_tracked': len(self.metrics),
            'widgets_configured': sum(len(d.widgets) for d in self.dashboards.values()),
            'active_subscribers': sum(len(subs) for subs in self.subscribers.values()),
            'cache_entries': len(self.dashboard_data_cache),
            'supported_dashboard_types': [dtype.value for dtype in DashboardType],
            'supported_widget_types': ["metric", "chart", "table", "alert", "status"]
        }


# Export main classes and enums
__all__ = [
    'OperationalDashboardController',
    'DashboardType',
    'MetricSeverity',
    'DashboardUpdateFrequency',
    'DashboardMetric',
    'DashboardWidget',
    'Dashboard',
    'AlertSummary'
]