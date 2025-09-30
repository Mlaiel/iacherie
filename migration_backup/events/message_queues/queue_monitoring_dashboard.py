"""Queue Monitoring Dashboard Module

Comprehensive monitoring dashboard with real-time metrics and alerting
for the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Queue Monitoring Dashboard architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
from collections import defaultdict, deque
import statistics

from ..core.exceptions import MessageQueueError
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class DashboardWidget(Enum):
    """Dashboard widget types"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    TABLE = "table"
    HEATMAP = "heatmap"
    ALERT_LIST = "alert_list"
    STATUS_GRID = "status_grid"


@dataclass
class MetricDefinition:
    """Definition of a monitored metric"""
    metric_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    metric_type: MetricType = MetricType.GAUGE
    unit: str = ""
    
    # Collection settings
    collection_interval: float = 10.0  # seconds
    retention_period: int = 86400      # 24 hours in seconds
    aggregation_functions: List[str] = field(default_factory=lambda: ["avg", "min", "max"])
    
    # Alert thresholds
    warning_threshold: Optional[float] = None
    error_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    
    # Business context
    business_category: str = "general"
    tags: Dict[str, str] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class Alert:
    """Monitoring alert"""
    alert_id: str = field(default_factory=lambda: str(uuid4()))
    metric_id: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str = ""
    description: str = ""
    current_value: float = 0.0
    threshold_value: float = 0.0
    
    # Timing
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    
    # Context
    business_context: Dict[str, Any] = field(default_factory=dict)
    affected_services: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    is_acknowledged: bool = False
    resolution_notes: str = ""


@dataclass
class DashboardPanel:
    """Dashboard panel configuration"""
    panel_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    widget_type: DashboardWidget = DashboardWidget.LINE_CHART
    
    # Data configuration
    metric_ids: List[str] = field(default_factory=list)
    time_range: str = "1h"  # 1h, 6h, 24h, 7d, 30d
    refresh_interval: float = 30.0  # seconds
    
    # Display configuration
    chart_options: Dict[str, Any] = field(default_factory=dict)
    layout: Dict[str, Any] = field(default_factory=dict)
    
    # Business context
    business_category: str = "general"
    priority: int = 100
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class MetricDataPoint:
    """Single metric data point"""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    value: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """Overall system health status"""
    overall_status: str = "healthy"  # healthy, degraded, unhealthy
    queue_health: Dict[str, str] = field(default_factory=dict)
    service_health: Dict[str, str] = field(default_factory=dict)
    critical_alerts: int = 0
    warning_alerts: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AinflueBusiness:
    """Ainflue Business Monitoring Configuration"""
    
    # Core metrics definitions
    CORE_METRICS = {
        # Queue metrics
        "queue_depth": MetricDefinition(
            metric_id="queue_depth",
            name="Queue Depth",
            description="Number of messages pending in queue",
            metric_type=MetricType.GAUGE,
            unit="messages",
            collection_interval=5.0,
            warning_threshold=1000,
            error_threshold=5000,
            critical_threshold=10000,
            business_category="queue_performance"
        ),
        
        "message_throughput": MetricDefinition(
            metric_id="message_throughput",
            name="Message Throughput",
            description="Messages processed per second",
            metric_type=MetricType.COUNTER,
            unit="messages/sec",
            collection_interval=10.0,
            warning_threshold=10,  # Below 10 msg/sec
            business_category="queue_performance"
        ),
        
        "processing_latency": MetricDefinition(
            metric_id="processing_latency",
            name="Processing Latency",
            description="Average message processing time",
            metric_type=MetricType.TIMER,
            unit="milliseconds",
            collection_interval=10.0,
            warning_threshold=1000,   # 1 second
            error_threshold=5000,    # 5 seconds
            critical_threshold=10000, # 10 seconds
            business_category="performance"
        ),
        
        "error_rate": MetricDefinition(
            metric_id="error_rate",
            name="Error Rate",
            description="Percentage of failed message processing",
            metric_type=MetricType.GAUGE,
            unit="percent",
            collection_interval=10.0,
            warning_threshold=5.0,   # 5%
            error_threshold=10.0,    # 10%
            critical_threshold=25.0, # 25%
            business_category="reliability"
        ),
        
        # Business metrics
        "content_upload_rate": MetricDefinition(
            metric_id="content_upload_rate",
            name="Content Upload Rate",
            description="Content uploads per minute",
            metric_type=MetricType.COUNTER,
            unit="uploads/min",
            collection_interval=15.0,
            business_category="content_management"
        ),
        
        "ai_processing_queue": MetricDefinition(
            metric_id="ai_processing_queue",
            name="AI Processing Queue",
            description="AI analysis requests in queue",
            metric_type=MetricType.GAUGE,
            unit="requests",
            collection_interval=10.0,
            warning_threshold=100,
            error_threshold=500,
            business_category="ai_processing"
        ),
        
        "payment_processing_latency": MetricDefinition(
            metric_id="payment_processing_latency",
            name="Payment Processing Latency",
            description="Payment processing time",
            metric_type=MetricType.TIMER,
            unit="milliseconds",
            collection_interval=5.0,
            warning_threshold=3000,   # 3 seconds
            error_threshold=10000,    # 10 seconds
            critical_threshold=30000, # 30 seconds
            business_category="payments"
        ),
        
        "collaboration_matches": MetricDefinition(
            metric_id="collaboration_matches",
            name="Collaboration Matches",
            description="Successful collaboration matches per hour",
            metric_type=MetricType.COUNTER,
            unit="matches/hour",
            collection_interval=300.0,  # 5 minutes
            business_category="collaboration"
        ),
        
        # System metrics
        "circuit_breaker_open": MetricDefinition(
            metric_id="circuit_breaker_open",
            name="Open Circuit Breakers",
            description="Number of open circuit breakers",
            metric_type=MetricType.GAUGE,
            unit="count",
            collection_interval=10.0,
            warning_threshold=1,
            error_threshold=3,
            critical_threshold=5,
            business_category="reliability"
        ),
        
        "dead_letter_queue_size": MetricDefinition(
            metric_id="dead_letter_queue_size",
            name="Dead Letter Queue Size",
            description="Messages in dead letter queue",
            metric_type=MetricType.GAUGE,
            unit="messages",
            collection_interval=30.0,
            warning_threshold=10,
            error_threshold=50,
            critical_threshold=100,
            business_category="reliability"
        )
    }
    
    # Dashboard panels configuration
    DASHBOARD_PANELS = {
        # Overview dashboard
        "system_overview": [
            DashboardPanel(
                panel_id="system_health_status",
                title="System Health Overview",
                widget_type=DashboardWidget.STATUS_GRID,
                metric_ids=["queue_depth", "error_rate", "circuit_breaker_open"],
                time_range="1h",
                business_category="overview",
                priority=1
            ),
            DashboardPanel(
                panel_id="throughput_chart",
                title="Message Throughput",
                widget_type=DashboardWidget.LINE_CHART,
                metric_ids=["message_throughput"],
                time_range="6h",
                business_category="overview",
                priority=2
            ),
            DashboardPanel(
                panel_id="latency_chart",
                title="Processing Latency",
                widget_type=DashboardWidget.LINE_CHART,
                metric_ids=["processing_latency"],
                time_range="6h",
                business_category="overview",
                priority=3
            ),
            DashboardPanel(
                panel_id="active_alerts",
                title="Active Alerts",
                widget_type=DashboardWidget.ALERT_LIST,
                time_range="24h",
                business_category="overview",
                priority=4
            )
        ],
        
        # Business operations dashboard
        "business_operations": [
            DashboardPanel(
                panel_id="content_metrics",
                title="Content Operations",
                widget_type=DashboardWidget.BAR_CHART,
                metric_ids=["content_upload_rate"],
                time_range="24h",
                business_category="content_management",
                priority=1
            ),
            DashboardPanel(
                panel_id="ai_processing_metrics",
                title="AI Processing",
                widget_type=DashboardWidget.GAUGE,
                metric_ids=["ai_processing_queue"],
                time_range="1h",
                business_category="ai_processing",
                priority=2
            ),
            DashboardPanel(
                panel_id="payment_metrics",
                title="Payment Processing",
                widget_type=DashboardWidget.LINE_CHART,
                metric_ids=["payment_processing_latency"],
                time_range="6h",
                business_category="payments",
                priority=3
            ),
            DashboardPanel(
                panel_id="collaboration_metrics",
                title="Collaboration Matching",
                widget_type=DashboardWidget.PIE_CHART,
                metric_ids=["collaboration_matches"],
                time_range="24h",
                business_category="collaboration",
                priority=4
            )
        ],
        
        # Technical infrastructure dashboard
        "infrastructure": [
            DashboardPanel(
                panel_id="queue_depths",
                title="Queue Depths",
                widget_type=DashboardWidget.HEATMAP,
                metric_ids=["queue_depth"],
                time_range="6h",
                business_category="infrastructure",
                priority=1
            ),
            DashboardPanel(
                panel_id="error_rates",
                title="Error Rates",
                widget_type=DashboardWidget.LINE_CHART,
                metric_ids=["error_rate"],
                time_range="24h",
                business_category="infrastructure",
                priority=2
            ),
            DashboardPanel(
                panel_id="circuit_breakers",
                title="Circuit Breaker Status",
                widget_type=DashboardWidget.TABLE,
                metric_ids=["circuit_breaker_open"],
                time_range="1h",
                business_category="infrastructure",
                priority=3
            ),
            DashboardPanel(
                panel_id="dlq_status",
                title="Dead Letter Queues",
                widget_type=DashboardWidget.BAR_CHART,
                metric_ids=["dead_letter_queue_size"],
                time_range="24h",
                business_category="infrastructure",
                priority=4
            )
        ]
    }
    
    # Alert notification rules
    ALERT_NOTIFICATION_RULES = {
        AlertSeverity.CRITICAL: {
            "immediate_channels": ["pagerduty", "sms", "email"],
            "escalation_time": 300,  # 5 minutes
            "auto_escalate": True
        },
        AlertSeverity.ERROR: {
            "immediate_channels": ["slack", "email"],
            "escalation_time": 900,  # 15 minutes
            "auto_escalate": True
        },
        AlertSeverity.WARNING: {
            "immediate_channels": ["slack"],
            "escalation_time": 3600,  # 1 hour
            "auto_escalate": False
        },
        AlertSeverity.INFO: {
            "immediate_channels": ["slack"],
            "escalation_time": None,
            "auto_escalate": False
        }
    }
    
    # SLA thresholds
    SLA_THRESHOLDS = {
        "content_upload_processing": {
            "target_latency": 5000,    # 5 seconds
            "max_error_rate": 2.0,     # 2%
            "availability": 99.9       # 99.9%
        },
        "payment_processing": {
            "target_latency": 3000,    # 3 seconds
            "max_error_rate": 0.1,     # 0.1%
            "availability": 99.99      # 99.99%
        },
        "ai_processing": {
            "target_latency": 30000,   # 30 seconds
            "max_error_rate": 5.0,     # 5%
            "availability": 99.0       # 99%
        },
        "collaboration_matching": {
            "target_latency": 10000,   # 10 seconds
            "max_error_rate": 3.0,     # 3%
            "availability": 99.5       # 99.5%
        }
    }


class QueueMonitoringDashboard:
    """
    Comprehensive monitoring dashboard with real-time metrics and alerting
    Provides complete visibility into Ainflue message queue operations
    """
    
    def __init__(self,
                 metrics_collector: Optional[MetricsCollector] = None,
                 encryption_manager: Optional[EncryptionManager] = None):
        self.metrics = metrics_collector
        self.encryption = encryption_manager
        
        # Monitoring configuration
        self.metric_definitions = {}  # metric_id -> MetricDefinition
        self.dashboard_panels = {}    # panel_id -> DashboardPanel
        self.metric_collectors = {}   # metric_id -> collection function
        
        # Data storage
        self.metric_data = defaultdict(deque)  # metric_id -> deque of MetricDataPoint
        self.alerts = {}              # alert_id -> Alert
        self.active_alerts = {}       # metric_id -> Alert
        
        # Monitoring tasks
        self.collection_tasks = {}    # metric_id -> asyncio.Task
        self.alert_tasks = {}         # metric_id -> asyncio.Task
        
        # Dashboard state
        self.dashboard_sessions = {}  # session_id -> dashboard config
        self.real_time_subscribers = defaultdict(list)  # metric_id -> List[callback]
        
        # System health
        self.system_health = SystemHealth()
        
        # Alert callbacks
        self.alert_callbacks = {}     # severity -> List[callback]
        
        logger.info("Initialized Queue Monitoring Dashboard")
    
    async def start(self) -> bool:
        """Start the monitoring dashboard"""
        try:
            # Load business monitoring configuration
            await self._load_business_configuration()
            
            # Start metric collection
            await self._start_metric_collection()
            
            # Start alert monitoring
            await self._start_alert_monitoring()
            
            # Start system health monitoring
            await self._start_system_health_monitoring()
            
            logger.info("Queue Monitoring Dashboard started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring dashboard: {str(e)}")
            raise MessageQueueError(f"Dashboard startup failed: {str(e)}")
    
    async def stop(self):
        """Stop the monitoring dashboard"""
        try:
            # Stop all collection tasks
            for task in self.collection_tasks.values():
                task.cancel()
            
            # Stop all alert tasks
            for task in self.alert_tasks.values():
                task.cancel()
            
            logger.info("Queue Monitoring Dashboard stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring dashboard: {str(e)}")
    
    async def register_metric(self, metric_def: MetricDefinition, collector_func: Callable) -> str:
        """Register a new metric for monitoring"""
        try:
            self.metric_definitions[metric_def.metric_id] = metric_def
            self.metric_collectors[metric_def.metric_id] = collector_func
            
            # Start collection if active
            if metric_def.is_active:
                await self._start_metric_collection_task(metric_def.metric_id)
                await self._start_metric_alert_task(metric_def.metric_id)
            
            logger.info(f"Registered metric: {metric_def.name}")
            return metric_def.metric_id
            
        except Exception as e:
            logger.error(f"Error registering metric: {str(e)}")
            raise MessageQueueError(f"Failed to register metric: {str(e)}")
    
    async def record_metric(self, metric_id: str, value: float, tags: Dict[str, str] = None) -> bool:
        """Record a metric data point"""
        try:
            if metric_id not in self.metric_definitions:
                return False
            
            data_point = MetricDataPoint(
                value=value,
                tags=tags or {}
            )
            
            # Store data point
            self.metric_data[metric_id].append(data_point)
            
            # Maintain data retention
            metric_def = self.metric_definitions[metric_id]
            retention_limit = datetime.now(timezone.utc) - timedelta(seconds=metric_def.retention_period)
            
            while (self.metric_data[metric_id] and 
                   self.metric_data[metric_id][0].timestamp < retention_limit):
                self.metric_data[metric_id].popleft()
            
            # Check for alerts
            await self._check_metric_alerts(metric_id, value)
            
            # Notify real-time subscribers
            await self._notify_real_time_subscribers(metric_id, data_point)
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording metric {metric_id}: {str(e)}")
            return False
    
    async def get_dashboard_data(self, dashboard_name: str, time_range: str = "1h") -> Dict[str, Any]:
        """Get dashboard data for rendering"""
        try:
            if dashboard_name not in AinflueBusiness.DASHBOARD_PANELS:
                return {"error": "Dashboard not found"}
            
            panels = AinflueBusiness.DASHBOARD_PANELS[dashboard_name]
            dashboard_data = {
                "dashboard_name": dashboard_name,
                "panels": [],
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "system_health": self._get_system_health_summary()
            }
            
            for panel in panels:
                if not panel.is_active:
                    continue
                
                panel_data = await self._get_panel_data(panel, time_range)
                dashboard_data["panels"].append(panel_data)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {"error": str(e)}
    
    async def get_metric_data(self, 
                            metric_id: str,
                            time_range: str = "1h",
                            aggregation: str = "avg") -> Dict[str, Any]:
        """Get metric data for specific time range"""
        try:
            if metric_id not in self.metric_definitions:
                return {"error": "Metric not found"}
            
            metric_def = self.metric_definitions[metric_id]
            
            # Calculate time range
            end_time = datetime.now(timezone.utc)
            start_time = self._parse_time_range(time_range, end_time)
            
            # Filter data points
            data_points = [
                dp for dp in self.metric_data[metric_id]
                if start_time <= dp.timestamp <= end_time
            ]
            
            if not data_points:
                return {
                    "metric_id": metric_id,
                    "metric_name": metric_def.name,
                    "data_points": [],
                    "summary": {}
                }
            
            # Aggregate data
            values = [dp.value for dp in data_points]
            summary = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "latest": values[-1] if values else 0
            }
            
            if len(values) > 1:
                summary["stddev"] = statistics.stdev(values)
            
            # Format data points for charting
            chart_data = [
                {
                    "timestamp": dp.timestamp.isoformat(),
                    "value": dp.value,
                    "tags": dp.tags
                }
                for dp in data_points
            ]
            
            return {
                "metric_id": metric_id,
                "metric_name": metric_def.name,
                "unit": metric_def.unit,
                "time_range": time_range,
                "data_points": chart_data,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error getting metric data for {metric_id}: {str(e)}")
            return {"error": str(e)}
    
    async def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """Get active alerts"""
        try:
            active_alerts = [
                alert for alert in self.alerts.values()
                if alert.is_active and alert.resolved_at is None
            ]
            
            if severity:
                active_alerts = [
                    alert for alert in active_alerts
                    if alert.severity == severity
                ]
            
            # Sort by severity and time
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.ERROR: 1,
                AlertSeverity.WARNING: 2,
                AlertSeverity.INFO: 3
            }
            
            active_alerts.sort(
                key=lambda a: (severity_order[a.severity], a.triggered_at),
                reverse=True
            )
            
            return [
                {
                    "alert_id": alert.alert_id,
                    "metric_id": alert.metric_id,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "description": alert.description,
                    "current_value": alert.current_value,
                    "threshold_value": alert.threshold_value,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "is_acknowledged": alert.is_acknowledged,
                    "business_context": alert.business_context,
                    "affected_services": alert.affected_services
                }
                for alert in active_alerts
            ]
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {str(e)}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, user_id: str, notes: str = "") -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            alert.is_acknowledged = True
            alert.acknowledged_at = datetime.now(timezone.utc)
            alert.resolution_notes = notes
            
            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {str(e)}")
            return False
    
    async def resolve_alert(self, alert_id: str, user_id: str, resolution_notes: str = "") -> bool:
        """Resolve an alert"""
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            alert.is_active = False
            alert.resolved_at = datetime.now(timezone.utc)
            alert.resolution_notes = resolution_notes
            
            # Remove from active alerts
            if alert.metric_id in self.active_alerts:
                del self.active_alerts[alert.metric_id]
            
            logger.info(f"Alert {alert_id} resolved by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {str(e)}")
            return False
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            await self._update_system_health()
            
            return {
                "overall_status": self.system_health.overall_status,
                "queue_health": self.system_health.queue_health,
                "service_health": self.system_health.service_health,
                "critical_alerts": self.system_health.critical_alerts,
                "warning_alerts": self.system_health.warning_alerts,
                "last_updated": self.system_health.last_updated.isoformat(),
                "sla_compliance": await self._calculate_sla_compliance()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {"error": str(e)}
    
    async def register_real_time_subscription(self, 
                                            metric_ids: List[str],
                                            callback: Callable,
                                            session_id: Optional[str] = None) -> str:
        """Register for real-time metric updates"""
        try:
            if not session_id:
                session_id = str(uuid4())
            
            for metric_id in metric_ids:
                self.real_time_subscribers[metric_id].append({
                    "session_id": session_id,
                    "callback": callback
                })
            
            logger.info(f"Registered real-time subscription for {len(metric_ids)} metrics")
            return session_id
            
        except Exception as e:
            logger.error(f"Error registering real-time subscription: {str(e)}")
            raise MessageQueueError(f"Failed to register subscription: {str(e)}")
    
    # Core monitoring logic
    
    async def _load_business_configuration(self):
        """Load Ainflue business monitoring configuration"""
        # Load metric definitions
        for metric_id, metric_def in AinflueBusiness.CORE_METRICS.items():
            self.metric_definitions[metric_id] = metric_def
        
        # Load dashboard panels
        for dashboard_name, panels in AinflueBusiness.DASHBOARD_PANELS.items():
            for panel in panels:
                self.dashboard_panels[panel.panel_id] = panel
        
        logger.info("Loaded business monitoring configuration")
    
    async def _start_metric_collection(self):
        """Start metric collection for all active metrics"""
        for metric_id in self.metric_definitions.keys():
            await self._start_metric_collection_task(metric_id)
    
    async def _start_metric_collection_task(self, metric_id: str):
        """Start collection task for a specific metric"""
        if metric_id in self.collection_tasks:
            return  # Already collecting
        
        metric_def = self.metric_definitions[metric_id]
        if not metric_def.is_active:
            return
        
        task = asyncio.create_task(self._metric_collection_loop(metric_id))
        self.collection_tasks[metric_id] = task
    
    async def _metric_collection_loop(self, metric_id: str):
        """Collection loop for a metric"""
        metric_def = self.metric_definitions[metric_id]
        
        while metric_id in self.metric_definitions and metric_def.is_active:
            try:
                # Collect metric if collector is available
                if metric_id in self.metric_collectors:
                    collector = self.metric_collectors[metric_id]
                    value = await collector()
                    
                    if value is not None:
                        await self.record_metric(metric_id, value)
                
                await asyncio.sleep(metric_def.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metric collection for {metric_id}: {str(e)}")
                await asyncio.sleep(60)  # Back off on error
    
    async def _start_alert_monitoring(self):
        """Start alert monitoring for all metrics"""
        for metric_id in self.metric_definitions.keys():
            await self._start_metric_alert_task(metric_id)
    
    async def _start_metric_alert_task(self, metric_id: str):
        """Start alert monitoring for a specific metric"""
        if metric_id in self.alert_tasks:
            return  # Already monitoring
        
        metric_def = self.metric_definitions[metric_id]
        if not any([metric_def.warning_threshold, metric_def.error_threshold, metric_def.critical_threshold]):
            return  # No thresholds defined
        
        task = asyncio.create_task(self._alert_monitoring_loop(metric_id))
        self.alert_tasks[metric_id] = task
    
    async def _alert_monitoring_loop(self, metric_id: str):
        """Alert monitoring loop for a metric"""
        metric_def = self.metric_definitions[metric_id]
        
        while metric_id in self.metric_definitions and metric_def.is_active:
            try:
                # Check current metric value
                if metric_id in self.metric_data and self.metric_data[metric_id]:
                    latest_value = self.metric_data[metric_id][-1].value
                    await self._check_metric_alerts(metric_id, latest_value)
                
                await asyncio.sleep(metric_def.collection_interval * 2)  # Check at 2x collection interval
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert monitoring for {metric_id}: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_metric_alerts(self, metric_id: str, current_value: float):
        """Check if metric value triggers alerts"""
        metric_def = self.metric_definitions[metric_id]
        
        # Determine alert severity
        alert_severity = None
        threshold_value = None
        
        if metric_def.critical_threshold is not None and current_value >= metric_def.critical_threshold:
            alert_severity = AlertSeverity.CRITICAL
            threshold_value = metric_def.critical_threshold
        elif metric_def.error_threshold is not None and current_value >= metric_def.error_threshold:
            alert_severity = AlertSeverity.ERROR
            threshold_value = metric_def.error_threshold
        elif metric_def.warning_threshold is not None and current_value >= metric_def.warning_threshold:
            alert_severity = AlertSeverity.WARNING
            threshold_value = metric_def.warning_threshold
        
        if alert_severity:
            # Check if alert already exists
            if metric_id in self.active_alerts:
                existing_alert = self.active_alerts[metric_id]
                
                # Update existing alert if severity increased
                if alert_severity.value < existing_alert.severity.value:  # Lower enum value = higher severity
                    existing_alert.severity = alert_severity
                    existing_alert.current_value = current_value
                    existing_alert.threshold_value = threshold_value
                
                return
            
            # Create new alert
            alert = Alert(
                metric_id=metric_id,
                severity=alert_severity,
                title=f"{metric_def.name} {alert_severity.value.title()} Alert",
                description=f"{metric_def.name} is {current_value} {metric_def.unit}, exceeding {alert_severity.value} threshold of {threshold_value} {metric_def.unit}",
                current_value=current_value,
                threshold_value=threshold_value,
                business_context={
                    "metric_name": metric_def.name,
                    "business_category": metric_def.business_category
                }
            )
            
            self.alerts[alert.alert_id] = alert
            self.active_alerts[metric_id] = alert
            
            # Send notifications
            await self._send_alert_notification(alert)
            
            logger.warning(f"Alert triggered: {alert.title}")
        
        else:
            # Check if we should resolve existing alert
            if metric_id in self.active_alerts:
                alert = self.active_alerts[metric_id]
                
                # Resolve if value is below warning threshold
                if (metric_def.warning_threshold is None or 
                    current_value < metric_def.warning_threshold):
                    
                    await self.resolve_alert(alert.alert_id, "system", "Metric value returned to normal")
    
    async def _start_system_health_monitoring(self):
        """Start system health monitoring"""
        asyncio.create_task(self._system_health_monitoring_loop())
    
    async def _system_health_monitoring_loop(self):
        """System health monitoring loop"""
        while True:
            try:
                await self._update_system_health()
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system health monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def _update_system_health(self):
        """Update overall system health"""
        # Count alerts by severity
        critical_alerts = sum(1 for alert in self.alerts.values() 
                            if alert.is_active and alert.severity == AlertSeverity.CRITICAL)
        
        warning_alerts = sum(1 for alert in self.alerts.values() 
                           if alert.is_active and alert.severity in [AlertSeverity.WARNING, AlertSeverity.ERROR])
        
        self.system_health.critical_alerts = critical_alerts
        self.system_health.warning_alerts = warning_alerts
        
        # Determine overall status
        if critical_alerts > 0:
            self.system_health.overall_status = "unhealthy"
        elif warning_alerts > 5:  # More than 5 warnings = degraded
            self.system_health.overall_status = "degraded"
        else:
            self.system_health.overall_status = "healthy"
        
        self.system_health.last_updated = datetime.now(timezone.utc)
    
    # Helper methods
    
    async def _get_panel_data(self, panel: DashboardPanel, time_range: str) -> Dict[str, Any]:
        """Get data for a dashboard panel"""
        panel_data = {
            "panel_id": panel.panel_id,
            "title": panel.title,
            "widget_type": panel.widget_type.value,
            "time_range": time_range,
            "data": []
        }
        
        if panel.widget_type == DashboardWidget.ALERT_LIST:
            # Get active alerts
            alerts = await self.get_active_alerts()
            panel_data["data"] = alerts[:10]  # Limit to 10 most recent
        
        elif panel.widget_type == DashboardWidget.STATUS_GRID:
            # Get status for each metric
            status_data = []
            for metric_id in panel.metric_ids:
                metric_data = await self.get_metric_data(metric_id, time_range)
                if "error" not in metric_data and metric_data["data_points"]:
                    latest_value = metric_data["summary"]["latest"]
                    status = self._determine_metric_status(metric_id, latest_value)
                    
                    status_data.append({
                        "metric_id": metric_id,
                        "metric_name": metric_data["metric_name"],
                        "value": latest_value,
                        "status": status,
                        "unit": metric_data["unit"]
                    })
            
            panel_data["data"] = status_data
        
        else:
            # Get metric data for charts
            for metric_id in panel.metric_ids:
                metric_data = await self.get_metric_data(metric_id, time_range)
                if "error" not in metric_data:
                    panel_data["data"].append(metric_data)
        
        return panel_data
    
    def _determine_metric_status(self, metric_id: str, value: float) -> str:
        """Determine status based on metric value and thresholds"""
        if metric_id not in self.metric_definitions:
            return "unknown"
        
        metric_def = self.metric_definitions[metric_id]
        
        if metric_def.critical_threshold is not None and value >= metric_def.critical_threshold:
            return "critical"
        elif metric_def.error_threshold is not None and value >= metric_def.error_threshold:
            return "error"
        elif metric_def.warning_threshold is not None and value >= metric_def.warning_threshold:
            return "warning"
        else:
            return "healthy"
    
    def _parse_time_range(self, time_range: str, end_time: datetime) -> datetime:
        """Parse time range string to start time"""
        if time_range == "1h":
            return end_time - timedelta(hours=1)
        elif time_range == "6h":
            return end_time - timedelta(hours=6)
        elif time_range == "24h":
            return end_time - timedelta(hours=24)
        elif time_range == "7d":
            return end_time - timedelta(days=7)
        elif time_range == "30d":
            return end_time - timedelta(days=30)
        else:
            return end_time - timedelta(hours=1)  # Default to 1 hour
    
    def _get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary for dashboard"""
        return {
            "overall_status": self.system_health.overall_status,
            "critical_alerts": self.system_health.critical_alerts,
            "warning_alerts": self.system_health.warning_alerts,
            "last_updated": self.system_health.last_updated.isoformat()
        }
    
    async def _calculate_sla_compliance(self) -> Dict[str, Any]:
        """Calculate SLA compliance for business services"""
        sla_compliance = {}
        
        for service_name, thresholds in AinflueBusiness.SLA_THRESHOLDS.items():
            # This would calculate actual SLA compliance based on metrics
            # For now, return mock data
            sla_compliance[service_name] = {
                "availability": 99.5,  # Would be calculated from uptime metrics
                "latency_compliance": 95.0,  # Would be calculated from latency metrics
                "error_rate_compliance": 98.0,  # Would be calculated from error metrics
                "overall_compliance": 97.5
            }
        
        return sla_compliance
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        notification_rules = AinflueBusiness.ALERT_NOTIFICATION_RULES.get(alert.severity, {})
        
        # Send to registered callbacks
        callbacks = self.alert_callbacks.get(alert.severity, [])
        for callback in callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error sending alert notification: {str(e)}")
    
    async def _notify_real_time_subscribers(self, metric_id: str, data_point: MetricDataPoint):
        """Notify real-time subscribers of metric updates"""
        subscribers = self.real_time_subscribers.get(metric_id, [])
        
        for subscriber in subscribers:
            try:
                callback = subscriber["callback"]
                await callback({
                    "metric_id": metric_id,
                    "timestamp": data_point.timestamp.isoformat(),
                    "value": data_point.value,
                    "tags": data_point.tags
                })
            except Exception as e:
                logger.error(f"Error notifying real-time subscriber: {str(e)}")
    
    def register_alert_callback(self, severity: AlertSeverity, callback: Callable):
        """Register callback for alert notifications"""
        if severity not in self.alert_callbacks:
            self.alert_callbacks[severity] = []
        
        self.alert_callbacks[severity].append(callback)
        logger.info(f"Registered alert callback for {severity.value}")


# Export for public API
__all__ = [
    "QueueMonitoringDashboard",
    "MetricDefinition",
    "Alert",
    "DashboardPanel",
    "MetricDataPoint",
    "SystemHealth",
    "AlertSeverity",
    "MetricType",
    "DashboardWidget",
    "AinflueBusiness"
]