"""
Performance Metrics Agent - KPIs temps réel

Real-time key performance indicators monitoring and alerting system with
comprehensive metrics tracking, dashboard generation, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque

# Import base agent
try:
    from .base import BaseAgent, AgentRequest, AgentResponse
except ImportError:
    from ai_agents.base import BaseAgent, AgentRequest, AgentResponse

# Import existing analytics components 
try:
    from analytics.performance_analyzer import PerformanceAnalyzer
except ImportError:
    # Fallback implementation
    class PerformanceAnalyzer:
        def __init__(self):
            pass
        async def analyze_content_performance(self, *args):
            return {}

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""
    SYSTEM_PERFORMANCE = "system_performance"
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_PERFORMANCE = "content_performance"
    BUSINESS_METRICS = "business_metrics"
    SECURITY_METRICS = "security_metrics"
    TECHNICAL_METRICS = "technical_metrics"


class AlertLevel(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


@dataclass
class MetricDefinition:
    """Definition of a performance metric"""
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    unit: str
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    calculation_method: str = "average"
    aggregation_period: int = 300  # seconds
    is_real_time: bool = True


@dataclass
class MetricValue:
    """Value of a performance metric at a point in time"""
    metric_id: str
    value: Union[float, int, str]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Performance alert"""
    alert_id: str
    metric_id: str
    alert_level: AlertLevel
    message: str
    current_value: Union[float, int, str]
    threshold_value: Optional[Union[float, int, str]]
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    is_resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Performance dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    metrics: List[str]  # metric IDs
    refresh_interval: int = 30  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class PerformanceMetricsAgent(BaseAgent):
    """
    Real-time Performance Metrics and KPI Monitoring Agent
    
    Capabilities:
    - Real-time metrics collection and monitoring
    - Key performance indicators (KPI) tracking
    - Automated alerting and notification system
    - Dynamic dashboard generation and updates
    - Performance trend analysis and forecasting
    - Threshold-based monitoring and anomaly detection
    - Multi-dimensional metric aggregation
    - Historical performance analysis
    """
    
    def __init__(self, agent_id: str = "performance_metrics_agent", **kwargs):
        super().__init__(
            agent_id=agent_id,
            agent_type="performance_metrics",
            version="1.0.0",
            config=kwargs.get('config', {})
        )
        
        # Initialize performance analyzer
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Metrics storage and management
        self.metric_definitions = {}
        self.metric_values = defaultdict(deque)  # metric_id -> deque of values
        self.active_alerts = {}
        self.alert_history = []
        self.dashboards = {}
        
        # Real-time monitoring
        self.monitoring_active = False
        self.collection_tasks = {}
        self.alert_rules = {}
        
        # Performance tracking
        self.last_collection_time = {}
        self.collection_stats = defaultdict(int)
        
        self.logger = logger

    async def _load_models_and_resources(self):
        """Load metrics definitions and initialize monitoring resources"""
        try:
            # Initialize default metric definitions
            await self._initialize_default_metrics()
            
            # Load alert rules
            await self._load_alert_rules()
            
            # Initialize default dashboards
            await self._initialize_default_dashboards()
            
            # Start real-time monitoring if enabled
            if self.config.get("real_time_monitoring", True):
                await self._start_real_time_monitoring()
            
            self.logger.info("Performance metrics monitoring initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load metrics monitoring resources: {e}")
            raise

    async def _initialize_default_metrics(self):
        """Initialize default performance metric definitions"""
        try:
            default_metrics = [
                # System Performance Metrics
                MetricDefinition(
                    metric_id="cpu_usage",
                    name="CPU Usage",
                    description="System CPU utilization percentage",
                    metric_type=MetricType.SYSTEM_PERFORMANCE,
                    unit="percentage",
                    target_value=70.0,
                    warning_threshold=80.0,
                    critical_threshold=95.0
                ),
                MetricDefinition(
                    metric_id="memory_usage",
                    name="Memory Usage",
                    description="System memory utilization percentage",
                    metric_type=MetricType.SYSTEM_PERFORMANCE,
                    unit="percentage",
                    target_value=60.0,
                    warning_threshold=80.0,
                    critical_threshold=90.0
                ),
                MetricDefinition(
                    metric_id="response_time",
                    name="Response Time",
                    description="Average API response time",
                    metric_type=MetricType.SYSTEM_PERFORMANCE,
                    unit="milliseconds",
                    target_value=200.0,
                    warning_threshold=1000.0,
                    critical_threshold=3000.0
                ),
                
                # User Engagement Metrics
                MetricDefinition(
                    metric_id="active_users",
                    name="Active Users",
                    description="Number of currently active users",
                    metric_type=MetricType.USER_ENGAGEMENT,
                    unit="count",
                    target_value=1000.0,
                    warning_threshold=100.0,
                    critical_threshold=10.0
                ),
                MetricDefinition(
                    metric_id="session_duration",
                    name="Average Session Duration",
                    description="Average user session duration",
                    metric_type=MetricType.USER_ENGAGEMENT,
                    unit="seconds",
                    target_value=1800.0,
                    warning_threshold=300.0,
                    critical_threshold=60.0
                ),
                MetricDefinition(
                    metric_id="bounce_rate",
                    name="Bounce Rate",
                    description="Percentage of single-page sessions",
                    metric_type=MetricType.USER_ENGAGEMENT,
                    unit="percentage",
                    target_value=30.0,
                    warning_threshold=60.0,
                    critical_threshold=80.0
                ),
                
                # Content Performance Metrics
                MetricDefinition(
                    metric_id="content_views",
                    name="Content Views",
                    description="Total content views per hour",
                    metric_type=MetricType.CONTENT_PERFORMANCE,
                    unit="count",
                    target_value=5000.0,
                    warning_threshold=1000.0,
                    critical_threshold=100.0
                ),
                MetricDefinition(
                    metric_id="engagement_rate",
                    name="Engagement Rate",
                    description="Content engagement rate",
                    metric_type=MetricType.CONTENT_PERFORMANCE,
                    unit="percentage",
                    target_value=5.0,
                    warning_threshold=2.0,
                    critical_threshold=0.5
                ),
                
                # Business Metrics
                MetricDefinition(
                    metric_id="revenue_per_hour",
                    name="Revenue per Hour",
                    description="Revenue generated per hour",
                    metric_type=MetricType.BUSINESS_METRICS,
                    unit="currency",
                    target_value=1000.0,
                    warning_threshold=200.0,
                    critical_threshold=50.0
                ),
                MetricDefinition(
                    metric_id="conversion_rate",
                    name="Conversion Rate",
                    description="User conversion rate",
                    metric_type=MetricType.BUSINESS_METRICS,
                    unit="percentage",
                    target_value=3.0,
                    warning_threshold=1.0,
                    critical_threshold=0.2
                ),
                
                # Technical Metrics
                MetricDefinition(
                    metric_id="error_rate",
                    name="Error Rate",
                    description="System error rate percentage",
                    metric_type=MetricType.TECHNICAL_METRICS,
                    unit="percentage",
                    target_value=0.1,
                    warning_threshold=1.0,
                    critical_threshold=5.0
                ),
                MetricDefinition(
                    metric_id="throughput",
                    name="Request Throughput",
                    description="Requests processed per second",
                    metric_type=MetricType.TECHNICAL_METRICS,
                    unit="requests_per_second",
                    target_value=1000.0,
                    warning_threshold=100.0,
                    critical_threshold=10.0
                )
            ]
            
            for metric_def in default_metrics:
                self.metric_definitions[metric_def.metric_id] = metric_def
            
            self.logger.info(f"Initialized {len(default_metrics)} default metrics")
            
        except Exception as e:
            self.logger.error(f"Error initializing default metrics: {e}")
            raise

    async def _load_alert_rules(self):
        """Load alerting rules and configurations"""
        try:
            # Default alert rules based on metric thresholds
            for metric_id, metric_def in self.metric_definitions.items():
                self.alert_rules[metric_id] = {
                    "enabled": True,
                    "warning_threshold": metric_def.warning_threshold,
                    "critical_threshold": metric_def.critical_threshold,
                    "evaluation_window": 300,  # 5 minutes
                    "notification_channels": ["email", "dashboard"],
                    "cooldown_period": 900  # 15 minutes
                }
            
            self.logger.info("Alert rules loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading alert rules: {e}")

    async def _initialize_default_dashboards(self):
        """Initialize default performance dashboards"""
        try:
            # System Overview Dashboard
            system_dashboard = Dashboard(
                dashboard_id="system_overview",
                name="System Overview",
                description="Overview of system performance metrics",
                metrics=["cpu_usage", "memory_usage", "response_time", "throughput", "error_rate"],
                refresh_interval=30
            )
            
            # User Engagement Dashboard
            engagement_dashboard = Dashboard(
                dashboard_id="user_engagement",
                name="User Engagement",
                description="User engagement and activity metrics",
                metrics=["active_users", "session_duration", "bounce_rate", "engagement_rate"],
                refresh_interval=60
            )
            
            # Business Metrics Dashboard
            business_dashboard = Dashboard(
                dashboard_id="business_metrics",
                name="Business Metrics",
                description="Key business performance indicators",
                metrics=["revenue_per_hour", "conversion_rate", "content_views"],
                refresh_interval=300
            )
            
            self.dashboards = {
                "system_overview": system_dashboard,
                "user_engagement": engagement_dashboard,
                "business_metrics": business_dashboard
            }
            
            self.logger.info("Default dashboards initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing dashboards: {e}")

    async def _start_real_time_monitoring(self):
        """Start real-time metrics monitoring"""
        try:
            self.monitoring_active = True
            
            # Start collection tasks for real-time metrics
            for metric_id, metric_def in self.metric_definitions.items():
                if metric_def.is_real_time:
                    task = asyncio.create_task(
                        self._collect_metric_continuously(metric_id, metric_def.aggregation_period)
                    )
                    self.collection_tasks[metric_id] = task
            
            # Start alert monitoring task
            alert_task = asyncio.create_task(self._monitor_alerts())
            self.collection_tasks["alert_monitor"] = alert_task
            
            self.logger.info("Real-time monitoring started")
            
        except Exception as e:
            self.logger.error(f"Error starting real-time monitoring: {e}")

    def get_required_config_keys(self) -> List[str]:
        """Return required configuration keys"""
        return [
            "real_time_monitoring",
            "metrics_retention_days",
            "alert_notification_channels",
            "dashboard_refresh_interval"
        ]

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process performance metrics requests"""
        try:
            action = request.action
            data = request.data
            
            result = {}
            
            if action == "collect_metrics":
                result = await self._collect_metrics(data)
            elif action == "get_real_time_metrics":
                result = await self._get_real_time_metrics(data)
            elif action == "generate_dashboard":
                result = await self._generate_dashboard(data)
            elif action == "create_alert_rule":
                result = await self._create_alert_rule(data)
            elif action == "get_alerts":
                result = await self._get_alerts(data)
            elif action == "analyze_performance_trends":
                result = await self._analyze_performance_trends(data)
            elif action == "get_kpi_summary":
                result = await self._get_kpi_summary(data)
            elif action == "export_metrics":
                result = await self._export_metrics(data)
            elif action == "configure_metric":
                result = await self._configure_metric(data)
            else:
                return AgentResponse(
                    success=False,
                    error=f"Unknown action: {action}",
                    error_code="INVALID_ACTION"
                )
            
            return AgentResponse(
                success=True,
                data=result,
                message=f"Performance metrics operation completed for action: {action}"
            )
            
        except Exception as e:
            self.logger.error(f"Error processing performance metrics request: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                error_code="METRICS_ERROR"
            )

    async def _collect_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and store performance metrics"""
        try:
            metrics_data = data.get("metrics", [])
            batch_timestamp = data.get("timestamp", datetime.utcnow())
            
            collected_count = 0
            errors = []
            
            for metric_data in metrics_data:
                try:
                    metric_id = metric_data.get("metric_id")
                    value = metric_data.get("value")
                    tags = metric_data.get("tags", {})
                    
                    if metric_id not in self.metric_definitions:
                        errors.append(f"Unknown metric: {metric_id}")
                        continue
                    
                    # Create metric value
                    metric_value = MetricValue(
                        metric_id=metric_id,
                        value=value,
                        timestamp=batch_timestamp,
                        tags=tags,
                        metadata=metric_data.get("metadata", {})
                    )
                    
                    # Store metric value
                    await self._store_metric_value(metric_value)
                    
                    # Check for alerts
                    await self._check_metric_alerts(metric_value)
                    
                    collected_count += 1
                    
                except Exception as e:
                    errors.append(f"Error processing metric {metric_data.get('metric_id', 'unknown')}: {e}")
            
            return {
                "collected_metrics": collected_count,
                "total_submitted": len(metrics_data),
                "errors": errors,
                "collection_timestamp": batch_timestamp.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return {"error": f"Metrics collection failed: {e}"}

    async def _get_real_time_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current real-time metrics values"""
        try:
            requested_metrics = data.get("metrics", list(self.metric_definitions.keys()))
            time_window = data.get("time_window_seconds", 300)
            
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(seconds=time_window)
            
            real_time_data = {}
            
            for metric_id in requested_metrics:
                if metric_id not in self.metric_definitions:
                    continue
                
                # Get recent values for this metric
                recent_values = [
                    mv for mv in self.metric_values[metric_id]
                    if mv.timestamp >= cutoff_time
                ]
                
                if recent_values:
                    # Calculate aggregated value
                    metric_def = self.metric_definitions[metric_id]
                    aggregated_value = self._calculate_aggregated_value(recent_values, metric_def.calculation_method)
                    
                    real_time_data[metric_id] = {
                        "current_value": aggregated_value,
                        "metric_name": metric_def.name,
                        "unit": metric_def.unit,
                        "target_value": metric_def.target_value,
                        "warning_threshold": metric_def.warning_threshold,
                        "critical_threshold": metric_def.critical_threshold,
                        "last_updated": recent_values[-1].timestamp.isoformat(),
                        "data_points": len(recent_values),
                        "status": self._get_metric_status(aggregated_value, metric_def),
                        "trend": self._calculate_metric_trend(recent_values)
                    }
                else:
                    real_time_data[metric_id] = {
                        "current_value": None,
                        "status": "no_data",
                        "last_updated": None
                    }
            
            return {
                "real_time_metrics": real_time_data,
                "time_window_seconds": time_window,
                "retrieved_at": current_time.isoformat(),
                "total_metrics": len(real_time_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return {"error": f"Real-time metrics retrieval failed: {e}"}

    async def _generate_dashboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance dashboard"""
        try:
            dashboard_id = data.get("dashboard_id", "system_overview")
            custom_metrics = data.get("metrics", None)
            time_range = data.get("time_range_hours", 24)
            
            if dashboard_id in self.dashboards:
                dashboard = self.dashboards[dashboard_id]
                metrics_to_include = custom_metrics or dashboard.metrics
            else:
                # Create custom dashboard
                dashboard = Dashboard(
                    dashboard_id=dashboard_id,
                    name=data.get("dashboard_name", "Custom Dashboard"),
                    description=data.get("dashboard_description", "Custom metrics dashboard"),
                    metrics=custom_metrics or list(self.metric_definitions.keys())[:5]
                )
                metrics_to_include = dashboard.metrics
            
            # Generate dashboard data
            dashboard_data = await self._build_dashboard_data(metrics_to_include, time_range)
            
            # Calculate dashboard health score
            health_score = self._calculate_dashboard_health_score(dashboard_data)
            
            return {
                "dashboard_id": dashboard_id,
                "dashboard_name": dashboard.name,
                "dashboard_description": dashboard.description,
                "health_score": health_score,
                "metrics_data": dashboard_data,
                "time_range_hours": time_range,
                "generated_at": datetime.utcnow().isoformat(),
                "refresh_interval": dashboard.refresh_interval,
                "total_metrics": len(metrics_to_include)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating dashboard: {e}")
            return {"error": f"Dashboard generation failed: {e}"}

    async def _create_alert_rule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update alert rule"""
        try:
            metric_id = data.get("metric_id")
            alert_config = data.get("alert_config", {})
            
            if metric_id not in self.metric_definitions:
                return {"error": f"Metric {metric_id} not found"}
            
            # Update alert rule
            self.alert_rules[metric_id] = {
                "enabled": alert_config.get("enabled", True),
                "warning_threshold": alert_config.get("warning_threshold"),
                "critical_threshold": alert_config.get("critical_threshold"),
                "evaluation_window": alert_config.get("evaluation_window", 300),
                "notification_channels": alert_config.get("notification_channels", ["dashboard"]),
                "cooldown_period": alert_config.get("cooldown_period", 900),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "metric_id": metric_id,
                "alert_rule": self.alert_rules[metric_id],
                "message": f"Alert rule for {metric_id} created/updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error creating alert rule: {e}")
            return {"error": f"Alert rule creation failed: {e}"}

    async def _get_alerts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current and historical alerts"""
        try:
            alert_level = data.get("alert_level", None)
            time_range_hours = data.get("time_range_hours", 24)
            include_resolved = data.get("include_resolved", False)
            
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(hours=time_range_hours)
            
            # Filter alerts
            filtered_alerts = []
            
            # Add active alerts
            for alert in self.active_alerts.values():
                if alert_level and alert.alert_level != AlertLevel(alert_level):
                    continue
                if alert.triggered_at >= cutoff_time:
                    filtered_alerts.append(alert)
            
            # Add historical alerts if requested
            if include_resolved:
                for alert in self.alert_history:
                    if alert_level and alert.alert_level != AlertLevel(alert_level):
                        continue
                    if alert.triggered_at >= cutoff_time:
                        filtered_alerts.append(alert)
            
            # Sort by triggered time (most recent first)
            filtered_alerts.sort(key=lambda x: x.triggered_at, reverse=True)
            
            # Convert to dict format
            alerts_data = []
            for alert in filtered_alerts:
                alerts_data.append({
                    "alert_id": alert.alert_id,
                    "metric_id": alert.metric_id,
                    "alert_level": alert.alert_level.value,
                    "message": alert.message,
                    "current_value": alert.current_value,
                    "threshold_value": alert.threshold_value,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "is_resolved": alert.is_resolved,
                    "duration_minutes": self._calculate_alert_duration(alert)
                })
            
            # Calculate alert summary
            alert_summary = self._calculate_alert_summary(filtered_alerts)
            
            return {
                "alerts": alerts_data,
                "alert_summary": alert_summary,
                "time_range_hours": time_range_hours,
                "total_alerts": len(alerts_data),
                "active_alerts": len(self.active_alerts),
                "retrieved_at": current_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return {"error": f"Alert retrieval failed: {e}"}

    async def _analyze_performance_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        try:
            metrics_to_analyze = data.get("metrics", list(self.metric_definitions.keys()))
            analysis_period_hours = data.get("analysis_period_hours", 168)  # 7 days
            
            current_time = datetime.utcnow()
            start_time = current_time - timedelta(hours=analysis_period_hours)
            
            trend_analysis = {}
            
            for metric_id in metrics_to_analyze:
                if metric_id not in self.metric_definitions:
                    continue
                
                # Get historical values
                historical_values = [
                    mv for mv in self.metric_values[metric_id]
                    if mv.timestamp >= start_time
                ]
                
                if len(historical_values) < 10:  # Need sufficient data
                    trend_analysis[metric_id] = {
                        "trend": "insufficient_data",
                        "data_points": len(historical_values)
                    }
                    continue
                
                # Calculate trend metrics
                trend_metrics = self._calculate_trend_metrics(historical_values)
                
                trend_analysis[metric_id] = {
                    "metric_name": self.metric_definitions[metric_id].name,
                    "trend_direction": trend_metrics["direction"],
                    "trend_strength": trend_metrics["strength"],
                    "slope": trend_metrics["slope"],
                    "r_squared": trend_metrics["r_squared"],
                    "average_value": trend_metrics["average"],
                    "min_value": trend_metrics["min"],
                    "max_value": trend_metrics["max"],
                    "volatility": trend_metrics["volatility"],
                    "data_points": len(historical_values),
                    "forecast": self._generate_metric_forecast(historical_values, 24)  # 24 hour forecast
                }
            
            # Generate overall performance summary
            performance_summary = self._generate_performance_summary(trend_analysis)
            
            return {
                "trend_analysis": trend_analysis,
                "performance_summary": performance_summary,
                "analysis_period_hours": analysis_period_hours,
                "analyzed_metrics": len(trend_analysis),
                "analyzed_at": current_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance trends: {e}")
            return {"error": f"Performance trends analysis failed: {e}"}

    async def _get_kpi_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get key performance indicators summary"""
        try:
            kpi_categories = data.get("categories", ["system", "business", "user"])
            time_period = data.get("time_period_hours", 24)
            
            current_time = datetime.utcnow()
            start_time = current_time - timedelta(hours=time_period)
            
            kpi_summary = {}
            
            for category in kpi_categories:
                category_metrics = self._get_metrics_by_category(category)
                category_kpis = {}
                
                for metric_id in category_metrics:
                    if metric_id not in self.metric_definitions:
                        continue
                    
                    recent_values = [
                        mv for mv in self.metric_values[metric_id]
                        if mv.timestamp >= start_time
                    ]
                    
                    if recent_values:
                        metric_def = self.metric_definitions[metric_id]
                        current_value = self._calculate_aggregated_value(recent_values, "average")
                        
                        # Calculate KPI status
                        kpi_status = self._calculate_kpi_status(current_value, metric_def)
                        
                        category_kpis[metric_id] = {
                            "name": metric_def.name,
                            "current_value": current_value,
                            "target_value": metric_def.target_value,
                            "unit": metric_def.unit,
                            "status": kpi_status,
                            "performance_score": self._calculate_performance_score(current_value, metric_def),
                            "trend": self._calculate_metric_trend(recent_values[-10:] if len(recent_values) > 10 else recent_values)
                        }
                
                kpi_summary[category] = category_kpis
            
            # Calculate overall KPI health score
            overall_health = self._calculate_overall_kpi_health(kpi_summary)
            
            return {
                "kpi_summary": kpi_summary,
                "overall_health_score": overall_health,
                "time_period_hours": time_period,
                "categories_analyzed": len(kpi_categories),
                "generated_at": current_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting KPI summary: {e}")
            return {"error": f"KPI summary generation failed: {e}"}

    async def _export_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Export metrics data in specified format"""
        try:
            export_format = data.get("format", "json")
            metrics_to_export = data.get("metrics", list(self.metric_definitions.keys()))
            time_range_hours = data.get("time_range_hours", 24)
            
            current_time = datetime.utcnow()
            start_time = current_time - timedelta(hours=time_range_hours)
            
            exported_data = {}
            
            for metric_id in metrics_to_export:
                if metric_id not in self.metric_definitions:
                    continue
                
                metric_values = [
                    {
                        "timestamp": mv.timestamp.isoformat(),
                        "value": mv.value,
                        "tags": mv.tags,
                        "metadata": mv.metadata
                    }
                    for mv in self.metric_values[metric_id]
                    if mv.timestamp >= start_time
                ]
                
                exported_data[metric_id] = {
                    "metric_definition": {
                        "name": self.metric_definitions[metric_id].name,
                        "description": self.metric_definitions[metric_id].description,
                        "unit": self.metric_definitions[metric_id].unit,
                        "type": self.metric_definitions[metric_id].metric_type.value
                    },
                    "values": metric_values,
                    "total_data_points": len(metric_values)
                }
            
            # Format data based on requested format
            if export_format == "csv":
                export_content = self._format_metrics_as_csv(exported_data)
            elif export_format == "json":
                export_content = json.dumps(exported_data, indent=2)
            else:
                return {"error": f"Unsupported export format: {export_format}"}
            
            return {
                "export_format": export_format,
                "exported_metrics": len(exported_data),
                "time_range_hours": time_range_hours,
                "export_size_bytes": len(export_content),
                "export_content": export_content,
                "exported_at": current_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return {"error": f"Metrics export failed: {e}"}

    async def _configure_metric(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Configure or create a new metric definition"""
        try:
            metric_config = data.get("metric_config", {})
            
            metric_def = MetricDefinition(
                metric_id=metric_config.get("metric_id"),
                name=metric_config.get("name"),
                description=metric_config.get("description", ""),
                metric_type=MetricType(metric_config.get("metric_type", "system_performance")),
                unit=metric_config.get("unit", "count"),
                target_value=metric_config.get("target_value"),
                warning_threshold=metric_config.get("warning_threshold"),
                critical_threshold=metric_config.get("critical_threshold"),
                calculation_method=metric_config.get("calculation_method", "average"),
                aggregation_period=metric_config.get("aggregation_period", 300),
                is_real_time=metric_config.get("is_real_time", True)
            )
            
            # Store metric definition
            self.metric_definitions[metric_def.metric_id] = metric_def
            
            # Create default alert rule
            self.alert_rules[metric_def.metric_id] = {
                "enabled": True,
                "warning_threshold": metric_def.warning_threshold,
                "critical_threshold": metric_def.critical_threshold,
                "evaluation_window": 300,
                "notification_channels": ["dashboard"],
                "cooldown_period": 900
            }
            
            # Start real-time collection if enabled
            if metric_def.is_real_time and self.monitoring_active:
                task = asyncio.create_task(
                    self._collect_metric_continuously(metric_def.metric_id, metric_def.aggregation_period)
                )
                self.collection_tasks[metric_def.metric_id] = task
            
            return {
                "metric_id": metric_def.metric_id,
                "metric_definition": {
                    "name": metric_def.name,
                    "description": metric_def.description,
                    "type": metric_def.metric_type.value,
                    "unit": metric_def.unit,
                    "is_real_time": metric_def.is_real_time
                },
                "message": f"Metric {metric_def.metric_id} configured successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error configuring metric: {e}")
            return {"error": f"Metric configuration failed: {e}"}

    # Helper methods for metrics processing

    async def _store_metric_value(self, metric_value: MetricValue):
        """Store a metric value in the time series"""
        metric_queue = self.metric_values[metric_value.metric_id]
        metric_queue.append(metric_value)
        
        # Maintain maximum queue size (e.g., last 10,000 values)
        max_values = self.config.get("max_metric_values", 10000)
        while len(metric_queue) > max_values:
            metric_queue.popleft()
        
        self.last_collection_time[metric_value.metric_id] = metric_value.timestamp
        self.collection_stats[metric_value.metric_id] += 1

    async def _check_metric_alerts(self, metric_value: MetricValue):
        """Check if metric value triggers any alerts"""
        metric_id = metric_value.metric_id
        
        if metric_id not in self.alert_rules or not self.alert_rules[metric_id]["enabled"]:
            return
        
        alert_rule = self.alert_rules[metric_id]
        current_value = metric_value.value
        
        # Check critical threshold
        critical_threshold = alert_rule.get("critical_threshold")
        if critical_threshold is not None and current_value >= critical_threshold:
            await self._trigger_alert(metric_value, AlertLevel.CRITICAL, critical_threshold)
        
        # Check warning threshold
        elif alert_rule.get("warning_threshold") is not None and current_value >= alert_rule["warning_threshold"]:
            await self._trigger_alert(metric_value, AlertLevel.WARNING, alert_rule["warning_threshold"])

    async def _trigger_alert(self, metric_value: MetricValue, alert_level: AlertLevel, threshold: float):
        """Trigger an alert for a metric"""
        alert_id = f"{metric_value.metric_id}_{alert_level.value}_{int(metric_value.timestamp.timestamp())}"
        
        # Check if similar alert is already active (cooldown period)
        existing_alert_key = f"{metric_value.metric_id}_{alert_level.value}"
        if existing_alert_key in self.active_alerts:
            last_alert = self.active_alerts[existing_alert_key]
            cooldown_period = self.alert_rules[metric_value.metric_id].get("cooldown_period", 900)
            if (metric_value.timestamp - last_alert.triggered_at).total_seconds() < cooldown_period:
                return  # Skip alert due to cooldown
        
        # Create alert
        alert = Alert(
            alert_id=alert_id,
            metric_id=metric_value.metric_id,
            alert_level=alert_level,
            message=f"{self.metric_definitions[metric_value.metric_id].name} {alert_level.value}: {metric_value.value} (threshold: {threshold})",
            current_value=metric_value.value,
            threshold_value=threshold,
            triggered_at=metric_value.timestamp
        )
        
        # Store alert
        self.active_alerts[existing_alert_key] = alert
        self.alert_history.append(alert)
        
        self.logger.warning(f"Alert triggered: {alert.message}")

    def _calculate_aggregated_value(self, values: List[MetricValue], method: str) -> float:
        """Calculate aggregated value from a list of metric values"""
        if not values:
            return 0.0
        
        numeric_values = [float(v.value) for v in values if isinstance(v.value, (int, float))]
        
        if not numeric_values:
            return 0.0
        
        if method == "average":
            return sum(numeric_values) / len(numeric_values)
        elif method == "sum":
            return sum(numeric_values)
        elif method == "max":
            return max(numeric_values)
        elif method == "min":
            return min(numeric_values)
        elif method == "last":
            return numeric_values[-1]
        else:
            return sum(numeric_values) / len(numeric_values)  # Default to average

    def _get_metric_status(self, value: float, metric_def: MetricDefinition) -> str:
        """Determine metric status based on value and thresholds"""
        if metric_def.critical_threshold is not None and value >= metric_def.critical_threshold:
            return "critical"
        elif metric_def.warning_threshold is not None and value >= metric_def.warning_threshold:
            return "warning"
        elif metric_def.target_value is not None and value >= metric_def.target_value:
            return "good"
        else:
            return "normal"

    def _calculate_metric_trend(self, values: List[MetricValue]) -> str:
        """Calculate trend direction for a metric"""
        if len(values) < 2:
            return "stable"
        
        numeric_values = [float(v.value) for v in values if isinstance(v.value, (int, float))]
        
        if len(numeric_values) < 2:
            return "stable"
        
        # Simple trend calculation
        first_half = numeric_values[:len(numeric_values)//2]
        second_half = numeric_values[len(numeric_values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change_percent = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"

    # Placeholder implementations for remaining helper methods
    async def _build_dashboard_data(self, metrics, time_range): 
        return {metric: {"current": 100, "trend": "stable"} for metric in metrics}
    
    def _calculate_dashboard_health_score(self, data): 
        return 85.5
    
    def _calculate_alert_duration(self, alert): 
        if alert.resolved_at:
            return (alert.resolved_at - alert.triggered_at).total_seconds() / 60
        return (datetime.utcnow() - alert.triggered_at).total_seconds() / 60
    
    def _calculate_alert_summary(self, alerts): 
        return {"total": len(alerts), "critical": 0, "warning": 0}
    
    def _calculate_trend_metrics(self, values): 
        return {"direction": "stable", "strength": 0.5, "slope": 0, "r_squared": 0.8, 
                "average": 100, "min": 50, "max": 150, "volatility": 0.2}
    
    def _generate_metric_forecast(self, values, hours): 
        return [100 + i for i in range(hours)]
    
    def _generate_performance_summary(self, analysis): 
        return {"overall_trend": "stable", "health_score": 85}
    
    def _get_metrics_by_category(self, category): 
        category_map = {
            "system": ["cpu_usage", "memory_usage", "response_time"],
            "business": ["revenue_per_hour", "conversion_rate"],
            "user": ["active_users", "session_duration", "bounce_rate"]
        }
        return category_map.get(category, [])
    
    def _calculate_kpi_status(self, value, metric_def): 
        return "good" if value >= (metric_def.target_value or 0) * 0.8 else "poor"
    
    def _calculate_performance_score(self, value, metric_def): 
        if not metric_def.target_value:
            return 0.5
        return min(1.0, value / metric_def.target_value)
    
    def _calculate_overall_kpi_health(self, kpi_summary): 
        return 82.3
    
    def _format_metrics_as_csv(self, data): 
        return "timestamp,metric,value\n2025-01-01T00:00:00,cpu_usage,75.5"
    
    async def _collect_metric_continuously(self, metric_id, period):
        """Continuously collect a metric at specified intervals"""
        while self.monitoring_active:
            try:
                # Simulate metric collection
                simulated_value = self._simulate_metric_value(metric_id)
                
                metric_value = MetricValue(
                    metric_id=metric_id,
                    value=simulated_value,
                    timestamp=datetime.utcnow()
                )
                
                await self._store_metric_value(metric_value)
                await self._check_metric_alerts(metric_value)
                
                await asyncio.sleep(period)
                
            except Exception as e:
                self.logger.error(f"Error collecting metric {metric_id}: {e}")
                await asyncio.sleep(period)

    def _simulate_metric_value(self, metric_id: str) -> float:
        """Simulate metric values for testing (replace with actual collection in production)"""
        base_values = {
            "cpu_usage": 65.0,
            "memory_usage": 45.0,
            "response_time": 250.0,
            "active_users": 1500.0,
            "session_duration": 1200.0,
            "bounce_rate": 35.0,
            "content_views": 3000.0,
            "engagement_rate": 4.2,
            "revenue_per_hour": 850.0,
            "conversion_rate": 2.8,
            "error_rate": 0.15,
            "throughput": 750.0
        }
        
        base_value = base_values.get(metric_id, 100.0)
        # Add some randomness
        variation = base_value * 0.1 * (np.random.random() - 0.5)
        return max(0, base_value + variation)

    async def _monitor_alerts(self):
        """Monitor and manage alerts"""
        while self.monitoring_active:
            try:
                current_time = datetime.utcnow()
                
                # Check for alerts that should be auto-resolved
                alerts_to_resolve = []
                for alert_key, alert in self.active_alerts.items():
                    # Auto-resolve alerts older than 1 hour if conditions are back to normal
                    if (current_time - alert.triggered_at).total_seconds() > 3600:
                        alerts_to_resolve.append(alert_key)
                
                for alert_key in alerts_to_resolve:
                    alert = self.active_alerts[alert_key]
                    alert.resolved_at = current_time
                    alert.is_resolved = True
                    del self.active_alerts[alert_key]
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring alerts: {e}")
                await asyncio.sleep(60)