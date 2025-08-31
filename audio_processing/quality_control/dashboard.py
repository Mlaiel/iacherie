"""📊 Quality Control Dashboard - Real-time Quality Management Interface

Advanced dashboard system for real-time monitoring, management, and visualization
of audio quality control operations with comprehensive analytics and reporting.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from pathlib import Path
import uuid

from .controller import QualityController
from .monitor import QualityMonitor, QualityAlert
from .metrics import QualityReport, QualityMetrics
from .standards import QualityProfile
from .compliance import ComplianceReport, PlatformComplianceManager
from .gates import QualityGate, QualityGateResult
from .optimization import QualityOptimizer, OptimizationResult

logger = logging.getLogger(__name__)


class DashboardMetricType(Enum):
    """Dashboard metric types"""
    QUALITY_SCORE = "quality_score"
    PROCESSING_TIME = "processing_time"
    SUCCESS_RATE = "success_rate"
    ALERT_COUNT = "alert_count"
    COMPLIANCE_RATE = "compliance_rate"
    OPTIMIZATION_IMPROVEMENT = "optimization_improvement"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"


class TimeRange(Enum):
    """Time range options for analytics"""
    LAST_HOUR = "1h"
    LAST_6_HOURS = "6h"
    LAST_24_HOURS = "24h"
    LAST_WEEK = "7d"
    LAST_MONTH = "30d"
    CUSTOM = "custom"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    title: str
    type: str  # "chart", "metric", "table", "alert", "status"
    metric_type: Optional[DashboardMetricType] = None
    time_range: TimeRange = TimeRange.LAST_24_HOURS
    refresh_interval: int = 60  # seconds
    position: Dict[str, int] = field(default_factory=dict)  # {"x": 0, "y": 0, "w": 4, "h": 3}
    config: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class DashboardData:
    """Complete dashboard data structure"""
    timestamp: datetime
    summary_metrics: Dict[str, Any]
    quality_trends: Dict[str, List[Dict[str, Any]]]
    active_alerts: List[QualityAlert]
    recent_reports: List[Dict[str, Any]]
    compliance_status: Dict[str, Any]
    system_health: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class RealTimeDashboard:
    """
    📊 Real-time Quality Control Dashboard
    
    Comprehensive dashboard for monitoring and managing audio quality control:
    - Real-time quality metrics visualization
    - Alert management and notification system
    - Compliance tracking across platforms
    - Performance analytics and reporting
    - Interactive quality control management
    """
    def __init__(
        self,
        quality_controller: QualityController,
        quality_monitor: QualityMonitor,
        compliance_manager: PlatformComplianceManager,
        quality_optimizer: QualityOptimizer
    ):
        self.controller = quality_controller
        self.monitor = quality_monitor
        self.compliance_manager = compliance_manager
        self.optimizer = quality_optimizer
        
        self.dashboard_id = str(uuid.uuid4())
        self.widgets: Dict[str, DashboardWidget] = {}
        self.dashboard_history: List[DashboardData] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Data caching for performance
        self.data_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_ttl = 30  # seconds
        
        # Initialize default widgets
        self._initialize_default_widgets()
        
        logger.info(f"RealTimeDashboard initialized with ID: {self.dashboard_id}")

    def _initialize_default_widgets(self):
        """Initialize default dashboard widgets"""
        
        # Quality Score Overview
        self.widgets["quality_overview"] = DashboardWidget(
            widget_id="quality_overview",
            title="Quality Score Overview",
            type="metric",
            metric_type=DashboardMetricType.QUALITY_SCORE,
            time_range=TimeRange.LAST_24_HOURS,
            position={"x": 0, "y": 0, "w": 6, "h": 3},
            config={
                "show_trend": True,
                "color_coding": True,
                "threshold_lines": True
            }
        )
        
        # Active Alerts
        self.widgets["active_alerts"] = DashboardWidget(
            widget_id="active_alerts",
            title="Active Quality Alerts",
            type="alert",
            position={"x": 6, "y": 0, "w": 6, "h": 3},
            config={
                "show_severity": True,
                "auto_refresh": True,
                "max_displayed": 10
            }
        )
        
        # Processing Performance
        self.widgets["processing_performance"] = DashboardWidget(
            widget_id="processing_performance",
            title="Processing Performance",
            type="chart",
            metric_type=DashboardMetricType.PROCESSING_TIME,
            time_range=TimeRange.LAST_6_HOURS,
            position={"x": 0, "y": 3, "w": 8, "h": 4},
            config={
                "chart_type": "line",
                "show_average": True,
                "show_percentiles": [50, 95, 99]
            }
        )
        
        # Compliance Status
        self.widgets["compliance_status"] = DashboardWidget(
            widget_id="compliance_status",
            title="Platform Compliance",
            type="status",
            metric_type=DashboardMetricType.COMPLIANCE_RATE,
            position={"x": 8, "y": 3, "w": 4, "h": 4},
            config={
                "platforms": ["spotify", "youtube", "tiktok", "apple_music"],
                "show_details": True
            }
        )
        
        # Recent Quality Reports
        self.widgets["recent_reports"] = DashboardWidget(
            widget_id="recent_reports",
            title="Recent Quality Reports",
            type="table",
            position={"x": 0, "y": 7, "w": 12, "h": 5},
            config={
                "columns": ["timestamp", "file", "quality_score", "status", "issues"],
                "max_rows": 20,
                "sortable": True,
                "filterable": True
            }
        )

    async def get_dashboard_data(
        self,
        time_range: TimeRange = TimeRange.LAST_24_HOURS,
        custom_start: Optional[datetime] = None,
        custom_end: Optional[datetime] = None
    ) -> DashboardData:
        """Get complete dashboard data"""
        
        cache_key = f"dashboard_data_{time_range.value}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            logger.debug("Returning cached dashboard data")
            return self.data_cache[cache_key]
        
        start_time = datetime.now()
        
        # Determine time range
        end_time = custom_end or datetime.now()
        if custom_start:
            start_time = custom_start
        else:
            delta_map = {
                TimeRange.LAST_HOUR: timedelta(hours=1),
                TimeRange.LAST_6_HOURS: timedelta(hours=6),
                TimeRange.LAST_24_HOURS: timedelta(hours=24),
                TimeRange.LAST_WEEK: timedelta(days=7),
                TimeRange.LAST_MONTH: timedelta(days=30)
            }
            start_time = end_time - delta_map.get(time_range, timedelta(hours=24))
        
        # Gather data from all components
        summary_metrics = await self._get_summary_metrics(start_time, end_time)
        quality_trends = await self._get_quality_trends(start_time, end_time)
        active_alerts = await self._get_active_alerts()
        recent_reports = await self._get_recent_reports(start_time, end_time)
        compliance_status = await self._get_compliance_status(start_time, end_time)
        system_health = await self._get_system_health()
        performance_metrics = await self._get_performance_metrics(start_time, end_time)
        
        dashboard_data = DashboardData(
            timestamp=datetime.now(),
            summary_metrics=summary_metrics,
            quality_trends=quality_trends,
            active_alerts=active_alerts,
            recent_reports=recent_reports,
            compliance_status=compliance_status,
            system_health=system_health,
            performance_metrics=performance_metrics
        )
        
        # Cache the data
        self.data_cache[cache_key] = dashboard_data
        self.cache_timestamps[cache_key] = datetime.now()
        
        return dashboard_data

    async def _get_summary_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get summary metrics for the dashboard"""
        
        # Get quality statistics from controller
        controller_stats = self.controller.get_processing_statistics()
        
        # Get monitoring statistics
        monitor_stats = self.monitor.get_monitoring_statistics()
        
        # Get optimization statistics
        optimizer_stats = self.optimizer.get_optimization_statistics()
        
        # Get compliance statistics
        compliance_stats = self.compliance_manager.get_compliance_statistics(hours=24)
        
        summary = {
            "total_processed": controller_stats.get("total_processed", 0),
            "average_quality_score": controller_stats.get("average_quality_score", 0.0),
            "success_rate": controller_stats.get("success_rate", 0.0),
            "total_alerts": monitor_stats.get("total_alerts", 0),
            "active_alerts": monitor_stats.get("active_alerts", 0),
            "average_processing_time": controller_stats.get("average_processing_time", 0.0),
            "compliance_rate": compliance_stats.get("compliance_rate", 0.0),
            "optimization_improvement": optimizer_stats.get("average_improvement", 0.0),
            "error_rate": 1.0 - controller_stats.get("success_rate", 1.0),
            "throughput": controller_stats.get("files_per_hour", 0.0),
            "system_uptime": (datetime.now() - start_time).total_seconds() / 3600  # hours
        }
        
        return summary

    async def _get_quality_trends(self, start_time: datetime, end_time: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """Get quality trends data"""
        
        trends = {
            "quality_scores": [],
            "processing_times": [],
            "success_rates": [],
            "alert_counts": [],
            "compliance_rates": []
        }
        
        # Get historical data from controller
        processing_history = self.controller.get_processing_history(
            hours=int((end_time - start_time).total_seconds() / 3600)
        )
        
        # Process into hourly buckets
        hour_buckets = {}
        for record in processing_history:
            hour_key = record.get('timestamp', datetime.now()).replace(minute=0, second=0, microsecond=0)
            if hour_key not in hour_buckets:
                hour_buckets[hour_key] = {
                    'quality_scores': [],
                    'processing_times': [],
                    'successes': 0,
                    'total': 0
                }
            
            bucket = hour_buckets[hour_key]
            bucket['total'] += 1
            
            if record.get('success', False):
                bucket['successes'] += 1
                if 'quality_score' in record:
                    bucket['quality_scores'].append(record['quality_score'])
                if 'processing_time' in record:
                    bucket['processing_times'].append(record['processing_time'])
        
        # Convert to trend data
        for hour, data in sorted(hour_buckets.items()):
            timestamp = hour.isoformat()
            
            # Quality scores trend
            if data['quality_scores']:
                trends["quality_scores"].append({
                    "timestamp": timestamp,
                    "value": statistics.mean(data['quality_scores']),
                    "count": len(data['quality_scores'])
                })
            
            # Processing times trend
            if data['processing_times']:
                trends["processing_times"].append({
                    "timestamp": timestamp,
                    "value": statistics.mean(data['processing_times']),
                    "min": min(data['processing_times']),
                    "max": max(data['processing_times']),
                    "count": len(data['processing_times'])
                })
            
            # Success rates trend
            if data['total'] > 0:
                trends["success_rates"].append({
                    "timestamp": timestamp,
                    "value": data['successes'] / data['total'],
                    "successful": data['successes'],
                    "total": data['total']
                })
        
        return trends

    async def _get_active_alerts(self) -> List[QualityAlert]:
        """Get active quality alerts"""
        return self.monitor.get_active_alerts()

    async def _get_recent_reports(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get recent quality reports"""
        
        # Get quality reports from controller history
        processing_history = self.controller.get_processing_history(
            hours=int((end_time - start_time).total_seconds() / 3600)
        )
        
        recent_reports = []
        
        for record in processing_history[-50:]:  # Last 50 records
            report = {
                "timestamp": record.get('timestamp', datetime.now()).isoformat(),
                "file": record.get('file_path', 'Unknown'),
                "quality_score": record.get('quality_score', 0.0),
                "status": "Success" if record.get('success', False) else "Failed",
                "processing_time": record.get('processing_time', 0.0),
                "issues": record.get('issues', []),
                "profile": record.get('quality_profile', 'Unknown')
            }
            recent_reports.append(report)
        
        return recent_reports

    async def _get_compliance_status(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get compliance status across platforms"""
        
        platforms = self.compliance_manager.get_supported_platforms()
        compliance_status = {}
        
        for platform in platforms:
            platform_stats = self.compliance_manager.get_compliance_statistics(
                platform=platform,
                hours=int((end_time - start_time).total_seconds() / 3600)
            )
            
            if not platform_stats.get('no_data', False):
                compliance_status[platform] = {
                    "compliance_rate": platform_stats.get('compliance_rate', 0.0),
                    "total_checks": platform_stats.get('total_checks', 0),
                    "violations": platform_stats.get('total_violations', 0),
                    "warnings": platform_stats.get('total_warnings', 0),
                    "average_score": platform_stats.get('average_score', 0.0)
                }
            else:
                compliance_status[platform] = {
                    "compliance_rate": 0.0,
                    "total_checks": 0,
                    "violations": 0,
                    "warnings": 0,
                    "average_score": 0.0
                }
        
        # Overall compliance
        if compliance_status:
            total_checks = sum(p["total_checks"] for p in compliance_status.values())
            if total_checks > 0:
                overall_compliance = sum(
                    p["compliance_rate"] * p["total_checks"] 
                    for p in compliance_status.values()
                ) / total_checks
            else:
                overall_compliance = 0.0
            
            compliance_status["overall"] = {
                "compliance_rate": overall_compliance,
                "total_checks": total_checks,
                "violations": sum(p["violations"] for p in compliance_status.values()),
                "warnings": sum(p["warnings"] for p in compliance_status.values())
            }
        
        return compliance_status

    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        
        # Controller health
        controller_stats = self.controller.get_processing_statistics()
        controller_health = "healthy" if controller_stats.get("success_rate", 0) > 0.95 else "degraded"
        
        # Monitor health
        monitor_stats = self.monitor.get_monitoring_statistics()
        active_alerts = monitor_stats.get("active_alerts", 0)
        monitor_health = "healthy" if active_alerts < 5 else "degraded"
        
        # Overall system health
        overall_health = "healthy" if controller_health == "healthy" and monitor_health == "healthy" else "degraded"
        
        return {
            "overall": overall_health,
            "controller": controller_health,
            "monitor": monitor_health,
            "optimizer": "healthy",  # Assuming optimizer is always healthy
            "compliance_manager": "healthy",  # Assuming compliance manager is always healthy
            "uptime": (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)).total_seconds(),
            "last_check": datetime.now().isoformat()
        }

    async def _get_performance_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get performance metrics"""
        
        controller_stats = self.controller.get_processing_statistics()
        optimizer_stats = self.optimizer.get_optimization_statistics()
        
        return {
            "average_processing_time": controller_stats.get("average_processing_time", 0.0),
            "throughput": controller_stats.get("files_per_hour", 0.0),
            "optimization_time": optimizer_stats.get("average_processing_time", 0.0),
            "success_rate": controller_stats.get("success_rate", 0.0),
            "error_rate": 1.0 - controller_stats.get("success_rate", 1.0),
            "memory_usage": 0.0,  # Would need actual memory monitoring
            "cpu_usage": 0.0,     # Would need actual CPU monitoring
            "disk_usage": 0.0     # Would need actual disk monitoring
        }

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache_timestamps:
            return False
        
        return (datetime.now() - self.cache_timestamps[cache_key]).total_seconds() < self.cache_ttl

    async def get_widget_data(self, widget_id: str) -> Dict[str, Any]:
        """Get data for a specific widget"""
        
        if widget_id not in self.widgets:
            return {"error": "Widget not found"}
        
        widget = self.widgets[widget_id]
        cache_key = f"widget_{widget_id}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.data_cache[cache_key]
        
        # Generate widget data based on type
        if widget.type == "metric":
            widget_data = await self._get_metric_widget_data(widget)
        elif widget.type == "chart":
            widget_data = await self._get_chart_widget_data(widget)
        elif widget.type == "table":
            widget_data = await self._get_table_widget_data(widget)
        elif widget.type == "alert":
            widget_data = await self._get_alert_widget_data(widget)
        elif widget.type == "status":
            widget_data = await self._get_status_widget_data(widget)
        else:
            widget_data = {"error": "Unknown widget type"}
        
        # Cache the data
        self.data_cache[cache_key] = widget_data
        self.cache_timestamps[cache_key] = datetime.now()
        
        return widget_data

    async def _get_metric_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for metric widget"""
        
        dashboard_data = await self.get_dashboard_data(widget.time_range)
        
        if widget.metric_type == DashboardMetricType.QUALITY_SCORE:
            current_value = dashboard_data.summary_metrics.get("average_quality_score", 0.0)
            trend_data = dashboard_data.quality_trends.get("quality_scores", [])
        elif widget.metric_type == DashboardMetricType.SUCCESS_RATE:
            current_value = dashboard_data.summary_metrics.get("success_rate", 0.0)
            trend_data = dashboard_data.quality_trends.get("success_rates", [])
        elif widget.metric_type == DashboardMetricType.PROCESSING_TIME:
            current_value = dashboard_data.summary_metrics.get("average_processing_time", 0.0)
            trend_data = dashboard_data.quality_trends.get("processing_times", [])
        else:
            current_value = 0.0
            trend_data = []
        
        return {
            "current_value": current_value,
            "trend_data": trend_data[-24:],  # Last 24 data points
            "change_percent": self._calculate_trend_change(trend_data),
            "status": self._get_metric_status(current_value, widget.metric_type)
        }

    async def _get_chart_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for chart widget"""
        
        dashboard_data = await self.get_dashboard_data(widget.time_range)
        
        chart_type = widget.config.get("chart_type", "line")
        
        if widget.metric_type == DashboardMetricType.PROCESSING_TIME:
            data = dashboard_data.quality_trends.get("processing_times", [])
        elif widget.metric_type == DashboardMetricType.QUALITY_SCORE:
            data = dashboard_data.quality_trends.get("quality_scores", [])
        else:
            data = []
        
        return {
            "chart_type": chart_type,
            "data": data,
            "config": widget.config
        }

    async def _get_table_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for table widget"""
        
        dashboard_data = await self.get_dashboard_data(widget.time_range)
        
        columns = widget.config.get("columns", [])
        max_rows = widget.config.get("max_rows", 20)
        
        rows = dashboard_data.recent_reports[:max_rows]
        
        return {
            "columns": columns,
            "rows": rows,
            "total_count": len(dashboard_data.recent_reports),
            "config": widget.config
        }

    async def _get_alert_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for alert widget"""
        
        active_alerts = await self._get_active_alerts()
        max_displayed = widget.config.get("max_displayed", 10)
        
        # Sort by severity and timestamp
        sorted_alerts = sorted(
            active_alerts,
            key=lambda a: (a.severity.value, a.timestamp),
            reverse=True
        )
        
        return {
            "alerts": [asdict(alert) for alert in sorted_alerts[:max_displayed]],
            "total_count": len(active_alerts),
            "critical_count": len([a for a in active_alerts if a.severity.value == "critical"]),
            "warning_count": len([a for a in active_alerts if a.severity.value == "warning"])
        }

    async def _get_status_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for status widget"""
        
        if widget.metric_type == DashboardMetricType.COMPLIANCE_RATE:
            dashboard_data = await self.get_dashboard_data(widget.time_range)
            platforms = widget.config.get("platforms", [])
            
            status_data = {}
            for platform in platforms:
                platform_data = dashboard_data.compliance_status.get(platform, {})
                status_data[platform] = {
                    "compliance_rate": platform_data.get("compliance_rate", 0.0),
                    "status": "good" if platform_data.get("compliance_rate", 0.0) > 0.8 else "warning",
                    "violations": platform_data.get("violations", 0),
                    "checks": platform_data.get("total_checks", 0)
                }
            
            return {
                "platforms": status_data,
                "overall_status": dashboard_data.compliance_status.get("overall", {})
            }
        else:
            return {"error": "Unsupported metric type for status widget"}

    def _calculate_trend_change(self, trend_data: List[Dict[str, Any]]) -> float:
        """Calculate trend change percentage"""
        
        if len(trend_data) < 2:
            return 0.0
        
        recent_values = [d["value"] for d in trend_data[-5:]]  # Last 5 values
        older_values = [d["value"] for d in trend_data[-10:-5]]  # Previous 5 values
        
        if not recent_values or not older_values:
            return 0.0
        
        recent_avg = statistics.mean(recent_values)
        older_avg = statistics.mean(older_values)
        
        if older_avg == 0:
            return 0.0
        
        return ((recent_avg - older_avg) / older_avg) * 100

    def _get_metric_status(self, value: float, metric_type: DashboardMetricType) -> str:
        """Get status for metric value"""
        
        thresholds = {
            DashboardMetricType.QUALITY_SCORE: {"good": 0.8, "warning": 0.6},
            DashboardMetricType.SUCCESS_RATE: {"good": 0.95, "warning": 0.85},
            DashboardMetricType.COMPLIANCE_RATE: {"good": 0.9, "warning": 0.75},
            DashboardMetricType.ERROR_RATE: {"good": 0.05, "warning": 0.15}  # Inverted (lower is better)
        }
        
        if metric_type not in thresholds:
            return "unknown"
        
        threshold = thresholds[metric_type]
        
        # For error rate, lower is better
        if metric_type == DashboardMetricType.ERROR_RATE:
            if value <= threshold["good"]:
                return "good"
            elif value <= threshold["warning"]:
                return "warning"
            else:
                return "critical"
        else:
            # For other metrics, higher is better
            if value >= threshold["good"]:
                return "good"
            elif value >= threshold["warning"]:
                return "warning"
            else:
                return "critical"

    def add_widget(self, widget: DashboardWidget):
        """Add custom widget to dashboard"""
        self.widgets[widget.widget_id] = widget
        logger.info(f"Added widget {widget.widget_id} to dashboard")

    def remove_widget(self, widget_id: str):
        """Remove widget from dashboard"""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            # Clear cache
            cache_key = f"widget_{widget_id}"
            if cache_key in self.data_cache:
                del self.data_cache[cache_key]
                del self.cache_timestamps[cache_key]
            logger.info(f"Removed widget {widget_id} from dashboard")

    def update_widget_config(self, widget_id: str, config: Dict[str, Any]):
        """Update widget configuration"""
        if widget_id in self.widgets:
            self.widgets[widget_id].config.update(config)
            # Clear cache to force refresh
            cache_key = f"widget_{widget_id}"
            if cache_key in self.data_cache:
                del self.data_cache[cache_key]
                del self.cache_timestamps[cache_key]
            logger.info(f"Updated configuration for widget {widget_id}")

    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get complete dashboard configuration"""
        return {
            "dashboard_id": self.dashboard_id,
            "widgets": {wid: asdict(widget) for wid, widget in self.widgets.items()},
            "cache_ttl": self.cache_ttl,
            "active_sessions": len(self.active_sessions)
        }

    def start_session(self, session_id: str, user_info: Dict[str, Any] = None) -> str:
        """Start dashboard session"""
        session_id = session_id or str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            "started_at": datetime.now(),
            "user_info": user_info or {},
            "last_activity": datetime.now(),
            "widgets_accessed": [],
            "data_requests": 0
        }
        
        logger.info(f"Started dashboard session: {session_id}")
        return session_id

    def end_session(self, session_id: str):
        """End dashboard session"""
        if session_id in self.active_sessions:
            session_duration = (datetime.now() - self.active_sessions[session_id]["started_at"]).total_seconds()
            logger.info(f"Ended dashboard session {session_id} after {session_duration:.1f} seconds")
            del self.active_sessions[session_id]

    def clear_cache(self):
        """Clear all cached data"""
        self.data_cache.clear()
        self.cache_timestamps.clear()
        logger.info("Cleared dashboard cache")

    async def export_dashboard_data(
        self,
        format: str = "json",
        time_range: TimeRange = TimeRange.LAST_24_HOURS
    ) -> str:
        """Export dashboard data"""
        
        dashboard_data = await self.get_dashboard_data(time_range)
        
        if format.lower() == "json":
            # Convert to JSON-serializable format
            export_data = {
                "dashboard_id": self.dashboard_id,
                "exported_at": datetime.now().isoformat(),
                "time_range": time_range.value,
                "data": asdict(dashboard_data)
            }
            
            return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        
        else:
            return f"Unsupported export format: {format}"

    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Get dashboard usage statistics"""
        
        active_sessions_count = len(self.active_sessions)
        total_widgets = len(self.widgets)
        cache_entries = len(self.data_cache)
        
        # Session statistics
        if self.active_sessions:
            session_durations = [
                (datetime.now() - session["started_at"]).total_seconds()
                for session in self.active_sessions.values()
            ]
            avg_session_duration = statistics.mean(session_durations)
        else:
            avg_session_duration = 0.0
        
        return {
            "active_sessions": active_sessions_count,
            "total_widgets": total_widgets,
            "cache_entries": cache_entries,
            "cache_ttl": self.cache_ttl,
            "average_session_duration": avg_session_duration,
            "dashboard_uptime": (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)).total_seconds(),
            "data_points_cached": sum(1 for key in self.data_cache.keys() if key.startswith("widget_"))
        }
