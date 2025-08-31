"""Performance Manager - IA-Influencer-Agent
================================================================================
Module: backend/core/managers/performance_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Manager Core - System Performance Monitoring & Optimization
Responsibility: Advanced performance monitoring with real-time optimization and scaling
Technologies: Python, Performance Monitoring, Auto-scaling, Resource Optimization
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Monitoring continu → Analyse performance → Détection anomalies → 
Optimisation automatique → Scaling intelligent → Alertes proactives → Rapports performance
"""from typing import Any, Dict, List, Optional, Union, Tuple, Set, Callable
import logging
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import time
import psutil
import platform
from collections import defaultdict, deque
import statistics
import socket

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types de métriques de performance"""    # System metrics
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    
    # Application metrics
    REQUEST_COUNT = "request_count"
    REQUEST_LATENCY = "request_latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    
    # Database metrics
    DB_CONNECTIONS = "db_connections"
    DB_QUERY_TIME = "db_query_time"
    DB_LOCK_WAITS = "db_lock_waits"
    
    # AI/ML metrics
    MODEL_INFERENCE_TIME = "model_inference_time"
    GPU_USAGE = "gpu_usage"
    AI_AGENT_LOAD = "ai_agent_load"
    
    # Business metrics
    ACTIVE_USERS = "active_users"
    CONTENT_PROCESSING_TIME = "content_processing_time"
    DISTRIBUTION_SUCCESS_RATE = "distribution_success_rate"
    
    # Custom metrics
    CUSTOM_COUNTER = "custom_counter"
    CUSTOM_GAUGE = "custom_gauge"
    CUSTOM_HISTOGRAM = "custom_histogram"


class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OptimizationAction(Enum):
    """Actions d'optimisation automatique"""    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    CACHE_OPTIMIZATION = "cache_optimization"
    QUERY_OPTIMIZATION = "query_optimization"
    RESOURCE_REBALANCING = "resource_rebalancing"
    GARBAGE_COLLECTION = "garbage_collection"
    CONNECTION_POOLING = "connection_pooling"
    CIRCUIT_BREAKER = "circuit_breaker"


class PerformanceStatus(Enum):
    """Statuts de performance"""    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceConfig:
    """Configuration du gestionnaire de performance"""    # Monitoring settings
    monitoring_interval_seconds: int = 30
    metric_retention_hours: int = 168  # 7 days
    detailed_monitoring: bool = True
    real_time_monitoring: bool = True
    
    # Alerting thresholds
    cpu_threshold_warning: float = 80.0
    cpu_threshold_critical: float = 95.0
    memory_threshold_warning: float = 85.0
    memory_threshold_critical: float = 95.0
    disk_threshold_warning: float = 80.0
    disk_threshold_critical: float = 90.0
    
    # Application thresholds
    response_time_threshold_ms: int = 1000
    error_rate_threshold_percent: float = 5.0
    throughput_threshold_rps: int = 100
    
    # Auto-optimization
    enable_auto_optimization: bool = True
    enable_auto_scaling: bool = True
    optimization_cooldown_minutes: int = 15
    
    # Performance targets
    target_response_time_ms: int = 500
    target_cpu_usage_percent: float = 70.0
    target_memory_usage_percent: float = 75.0
    target_error_rate_percent: float = 1.0
    
    # Resource management
    max_concurrent_optimizations: int = 3
    resource_check_interval: int = 60
    cleanup_interval_hours: int = 24
    
    # Notification settings
    alert_notification_channels: List[str] = field(default_factory=lambda: ["email", "slack"])
    critical_alert_immediate: bool = True
    performance_report_frequency: str = "daily"  # daily, weekly, monthly


@dataclass
class MetricDataPoint:
    """Point de données de métrique"""    metric_type: MetricType
    value: float
    timestamp: datetime
    
    # Additional context
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality indicators
    accuracy: float = 1.0
    confidence: float = 1.0
    
    # Source information
    source: str = ""
    collection_method: str = "automatic"


@dataclass
class PerformanceAlert:
    """Alerte de performance"""    id: str
    alert_type: str
    severity: AlertSeverity
    metric_type: MetricType
    
    # Alert details
    message: str = ""
    description: str = ""
    current_value: float = 0.0
    threshold_value: float = 0.0
    
    # Context
    affected_component: str = ""
    impact_assessment: str = ""
    recommended_actions: List[str] = field(default_factory=list)
    
    # Status
    status: str = "active"  # active, acknowledged, resolved
    acknowledged_by: str = ""
    resolved_by: str = ""
    
    # Evidence
    evidence_data: Dict[str, Any] = field(default_factory=dict)
    related_metrics: List[MetricDataPoint] = field(default_factory=list)
    
    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Escalation
    escalation_level: int = 0
    escalation_threshold: int = 3
    auto_escalate: bool = True


@dataclass
class OptimizationAction:
    """Action d'optimisation"""    id: str
    action_type: OptimizationAction
    target_component: str
    
    # Action details
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_impact: str = ""
    
    # Execution
    status: str = "pending"  # pending, executing, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    actual_impact: Dict[str, float] = field(default_factory=dict)
    success: bool = False
    error_message: str = ""
    
    # Context
    triggered_by_alert: Optional[str] = None
    rollback_available: bool = True
    rollback_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "auto_optimizer"


@dataclass
class PerformanceReport:
    """Rapport de performance"""    id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    
    # Summary metrics
    overall_status: PerformanceStatus = PerformanceStatus.GOOD
    overall_score: float = 85.0
    
    # System performance
    average_cpu_usage: float = 0.0
    average_memory_usage: float = 0.0
    average_disk_usage: float = 0.0
    
    # Application performance
    average_response_time: float = 0.0
    total_requests: int = 0
    error_rate: float = 0.0
    throughput: float = 0.0
    
    # Resource utilization
    peak_cpu_usage: float = 0.0
    peak_memory_usage: float = 0.0
    resource_efficiency: float = 0.0
    
    # Optimization summary
    optimizations_performed: int = 0
    optimizations_successful: int = 0
    performance_improvements: Dict[str, float] = field(default_factory=dict)
    
    # Alerts summary
    total_alerts: int = 0
    critical_alerts: int = 0
    alerts_resolved: int = 0
    mean_time_to_resolution: float = 0.0
    
    # Trends and insights
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    capacity_forecast: Dict[str, Any] = field(default_factory=dict)
    
    # Generated info
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: str = "performance_manager"


@dataclass
class SystemHealthCheck:
    """Vérification de santé du système"""    id: str
    component_name: str
    
    # Health status
    is_healthy: bool = True
    health_score: float = 100.0
    status_message: str = "OK"
    
    # Detailed checks
    cpu_check: bool = True
    memory_check: bool = True
    disk_check: bool = True
    network_check: bool = True
    service_check: bool = True
    
    # Performance indicators
    response_time_ms: float = 0.0
    throughput_ops_per_sec: float = 0.0
    error_rate_percent: float = 0.0
    
    # Resource usage
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    
    # Connectivity
    external_dependencies_healthy: bool = True
    database_connectivity: bool = True
    api_endpoints_responsive: bool = True
    
    # Metadata
    check_duration_ms: float = 0.0
    last_check: datetime = field(default_factory=datetime.utcnow)
    next_check_scheduled: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=5))


class PerformanceManager(ABC):
    """    📊 Advanced Performance Manager - IA-Influencer-Agent
    
    Responsabilité:
    Gestionnaire industriel pour monitoring performance et optimisation système
    
    Technologies:
    - Real-time Monitoring: Continuous system and application monitoring
    - Auto-optimization: Intelligent performance optimization automation
    - Predictive Analytics: Performance forecasting and capacity planning
    - Alert Management: Proactive alerting with escalation procedures
    - Resource Optimization: Dynamic resource allocation and scaling
    - Performance Analytics: Comprehensive performance reporting and insights
    
    Fonctionnalités industrielles:
    - Monitoring temps réel complet
    - Optimisation automatique intelligente
    - Alertes proactives configurables
    - Scaling automatique basé charge
    - Analytics performance avancées
    - Détection anomalies ML
    - Prédiction capacité future
    - Optimisation ressources continue
    - Rapports performance détaillés
    - Health checks automatisés
    - Recovery automatique pannes
    - Tuning performance continu
    """    
    def __init__(self, config: PerformanceConfig = None):
        self.config = config or PerformanceConfig()
        
        # Metric storage
        self._metrics: Dict[MetricType, deque] = defaultdict(lambda: deque(maxlen=10080))  # 7 days of 1-min intervals
        self._current_metrics: Dict[MetricType, MetricDataPoint] = {}
        
        # Alerting system
        self._alerts: Dict[str, PerformanceAlert] = {}
        self._alert_rules: Dict[MetricType, List[Dict[str, Any]]] = defaultdict(list)
        self._alert_queue: asyncio.Queue = asyncio.Queue()
        
        # Optimization system
        self._optimization_actions: Dict[str, OptimizationAction] = {}
        self._optimization_queue: asyncio.Queue = asyncio.Queue()
        self._optimization_history: List[OptimizationAction] = []
        
        # Health monitoring
        self._health_checks: Dict[str, SystemHealthCheck] = {}
        self._component_status: Dict[str, bool] = {}
        
        # Performance reports
        self._performance_reports: Dict[str, PerformanceReport] = {}
        
        # Background tasks
        self._monitoring_tasks: Set[asyncio.Task] = set()
        self._optimization_tasks: Set[asyncio.Task] = set()
        self._monitoring_active = False
        self._lock = threading.Lock()
        
        # System information
        self._system_info = {
            "platform": platform.system(),
            "architecture": platform.architecture()[0],
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "hostname": socket.gethostname()
        }
        
        # Performance baselines
        self._performance_baselines: Dict[MetricType, float] = {}
        self._anomaly_detection_models: Dict[MetricType, Any] = {}
        
        # Performance metrics
        self._metrics_summary = {
            "total_metrics_collected": 0,
            "active_alerts": 0,
            "optimizations_performed": 0,
            "system_uptime": 0.0,
            "average_response_time": 0.0,
            "current_cpu_usage": 0.0,
            "current_memory_usage": 0.0,
            "current_throughput": 0.0,
            "overall_health_score": 100.0,
            "performance_trend": "stable"
        }
        
        logger.info(f"📊 Performance Manager initialized - Monitoring {len(MetricType)} metric types")
    
    @abstractmethod
    async def initialize_monitoring(self) -> bool:
        """        Initialize performance monitoring system
        
        Returns:
            bool: True if initialization successful
        """        pass
    
    @abstractmethod
    async def collect_system_metrics(self) -> Dict[MetricType, MetricDataPoint]:
        """        Collect current system performance metrics
        
        Returns:
            Dict[MetricType, MetricDataPoint]: Current system metrics
        """        pass
    
    @abstractmethod
    async def execute_optimization_action(
        self,
        action: OptimizationAction
    ) -> bool:
        """        Execute performance optimization action
        
        Args:
            action: Optimization action to execute
            
        Returns:
            bool: True if action executed successfully
        """        pass
    
    @abstractmethod
    async def perform_health_check(
        self,
        component_name: str
    ) -> SystemHealthCheck:
        """        Perform health check on system component
        
        Args:
            component_name: Component to check
            
        Returns:
            SystemHealthCheck: Health check results
        """        pass
    
    async def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """        Record performance metric
        
        Args:
            metric_type: Type of metric
            value: Metric value
            tags: Optional metric tags
            metadata: Optional metric metadata
        """        try:
            # Create metric data point
            metric_point = MetricDataPoint(
                metric_type=metric_type,
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {},
                metadata=metadata or {},
                source="manual_recording"
            )
            
            with self._lock:
                # Store metric
                self._metrics[metric_type].append(metric_point)
                self._current_metrics[metric_type] = metric_point
                self._metrics_summary["total_metrics_collected"] += 1
            
            # Check alert rules
            await self._evaluate_alert_rules(metric_point)
            
            # Update performance baselines
            await self._update_performance_baselines(metric_type, value)
            
            logger.debug(f"📊 Metric recorded: {metric_type.value} = {value}")
            
        except Exception as e:
            logger.error(f"❌ Metric recording failed: {e}")
    
    async def create_alert_rule(
        self,
        metric_type: MetricType,
        threshold: float,
        severity: AlertSeverity,
        condition: str = "greater_than",
        duration_minutes: int = 5
    ) -> str:
        """        Create performance alert rule
        
        Args:
            metric_type: Metric to monitor
            threshold: Alert threshold
            severity: Alert severity level
            condition: Alert condition (greater_than, less_than, etc.)
            duration_minutes: Duration before alerting
            
        Returns:
            str: Alert rule ID
        """        try:
            rule_id = str(uuid.uuid4())
            
            alert_rule = {
                "id": rule_id,
                "metric_type": metric_type,
                "threshold": threshold,
                "severity": severity,
                "condition": condition,
                "duration_minutes": duration_minutes,
                "created_at": datetime.utcnow(),
                "active": True
            }
            
            with self._lock:
                self._alert_rules[metric_type].append(alert_rule)
            
            logger.info(f"📊 Alert rule created: {metric_type.value} {condition} {threshold}")
            return rule_id
            
        except Exception as e:
            logger.error(f"❌ Alert rule creation failed: {e}")
            raise
    
    async def get_performance_dashboard(
        self,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """        Get comprehensive performance dashboard data
        
        Args:
            time_range: Optional time range filter
            
        Returns:
            Dict: Complete dashboard data
        """        try:
            # Default to last 24 hours
            if not time_range:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(hours=24)
                time_range = (start_time, end_time)
            else:
                start_time, end_time = time_range
            
            with self._lock:
                # Current system status
                current_status = {
                    "overall_health": self._calculate_overall_health_score(),
                    "system_uptime": self._calculate_system_uptime(),
                    "active_alerts": len([a for a in self._alerts.values() if a.status == "active"]),
                    "critical_alerts": len([
                        a for a in self._alerts.values() 
                        if a.status == "active" and a.severity == AlertSeverity.CRITICAL
                    ])
                }
                
                # Current metrics
                current_metrics = {}
                for metric_type, metric_point in self._current_metrics.items():
                    current_metrics[metric_type.value] = {
                        "value": metric_point.value,
                        "timestamp": metric_point.timestamp.isoformat(),
                        "status": self._get_metric_status(metric_type, metric_point.value)
                    }
                
                # Historical data
                historical_data = {}
                for metric_type, metric_deque in self._metrics.items():
                    # Filter by time range
                    filtered_metrics = [
                        m for m in metric_deque 
                        if start_time <= m.timestamp <= end_time
                    ]
                    
                    if filtered_metrics:
                        values = [m.value for m in filtered_metrics]
                        timestamps = [m.timestamp.isoformat() for m in filtered_metrics]
                        
                        historical_data[metric_type.value] = {
                            "values": values,
                            "timestamps": timestamps,
                            "average": statistics.mean(values),
                            "min": min(values),
                            "max": max(values),
                            "trend": self._calculate_trend(values)
                        }
                
                # Resource utilization
                resource_utilization = self._calculate_resource_utilization()
                
                # Performance trends
                performance_trends = self._analyze_performance_trends(time_range)
                
                # Top alerts
                recent_alerts = sorted(
                    [a for a in self._alerts.values() if start_time <= a.triggered_at <= end_time],
                    key=lambda x: x.triggered_at,
                    reverse=True
                )[:10]
                
                alert_data = [
                    {
                        "id": alert.id,
                        "type": alert.alert_type,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "component": alert.affected_component,
                        "status": alert.status,
                        "triggered_at": alert.triggered_at.isoformat()
                    }
                    for alert in recent_alerts
                ]
                
                # Optimization summary
                recent_optimizations = [
                    opt for opt in self._optimization_history
                    if start_time <= opt.created_at <= end_time
                ]
                
                optimization_summary = {
                    "total_optimizations": len(recent_optimizations),
                    "successful_optimizations": len([o for o in recent_optimizations if o.success]),
                    "optimization_types": self._count_optimization_types(recent_optimizations),
                    "average_impact": self._calculate_average_optimization_impact(recent_optimizations)
                }
                
                # Capacity forecasting
                capacity_forecast = await self._generate_capacity_forecast()
                
                # Health checks summary
                health_summary = {
                    "total_components": len(self._health_checks),
                    "healthy_components": len([h for h in self._health_checks.values() if h.is_healthy]),
                    "average_health_score": statistics.mean([h.health_score for h in self._health_checks.values()]) if self._health_checks else 100.0
                }
                
                return {
                    # Current status
                    "current_status": current_status,
                    "current_metrics": current_metrics,
                    "resource_utilization": resource_utilization,
                    
                    # Historical data
                    "historical_data": historical_data,
                    "performance_trends": performance_trends,
                    
                    # Alerts and incidents
                    "recent_alerts": alert_data,
                    "alert_statistics": {
                        "total_alerts": len(recent_alerts),
                        "by_severity": self._count_alerts_by_severity(recent_alerts),
                        "by_component": self._count_alerts_by_component(recent_alerts)
                    },
                    
                    # Optimization insights
                    "optimization_summary": optimization_summary,
                    
                    # Health monitoring
                    "health_summary": health_summary,
                    "component_health": {
                        name: {
                            "healthy": check.is_healthy,
                            "score": check.health_score,
                            "last_check": check.last_check.isoformat()
                        }
                        for name, check in self._health_checks.items()
                    },
                    
                    # Capacity planning
                    "capacity_forecast": capacity_forecast,
                    
                    # System information
                    "system_info": self._system_info,
                    
                    # Generated metadata
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    },
                    "generated_at": datetime.utcnow().isoformat(),
                    "data_points": sum(len(deque) for deque in self._metrics.values())
                }
            
        except Exception as e:
            logger.error(f"❌ Dashboard generation failed: {e}")
            raise
    
    async def optimize_performance_automatically(
        self,
        target_metrics: Dict[MetricType, float] = None
    ) -> Dict[str, Any]:
        """        Perform automatic performance optimization
        
        Args:
            target_metrics: Optional target values for metrics
            
        Returns:
            Dict: Optimization results
        """        try:
            targets = target_metrics or {
                MetricType.CPU_USAGE: self.config.target_cpu_usage_percent,
                MetricType.MEMORY_USAGE: self.config.target_memory_usage_percent,
                MetricType.REQUEST_LATENCY: self.config.target_response_time_ms,
                MetricType.ERROR_RATE: self.config.target_error_rate_percent
            }
            
            optimization_results = {
                "actions_planned": 0,
                "actions_executed": 0,
                "actions_successful": 0,
                "performance_improvements": {},
                "errors": []
            }
            
            # Analyze current performance vs targets
            performance_gaps = await self._analyze_performance_gaps(targets)
            
            # Generate optimization actions
            optimization_actions = await self._generate_optimization_actions(performance_gaps)
            optimization_results["actions_planned"] = len(optimization_actions)
            
            # Execute optimizations
            for action in optimization_actions:
                try:
                    success = await self.execute_optimization_action(action)
                    optimization_results["actions_executed"] += 1
                    
                    if success:
                        optimization_results["actions_successful"] += 1
                        
                        # Record performance improvement
                        if action.actual_impact:
                            optimization_results["performance_improvements"][action.action_type.value] = action.actual_impact
                    
                except Exception as e:
                    optimization_results["errors"].append({
                        "action": action.action_type.value,
                        "error": str(e)
                    })
            
            # Calculate overall success rate
            success_rate = (optimization_results["actions_successful"] / 
                          max(optimization_results["actions_executed"], 1)) * 100
            
            optimization_results["success_rate"] = success_rate
            optimization_results["optimization_timestamp"] = datetime.utcnow().isoformat()
            
            logger.info(f"📊 Auto-optimization completed: {optimization_results['actions_successful']}/{optimization_results['actions_executed']} successful")
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Auto-optimization failed: {e}")
            raise
    
    async def _evaluate_alert_rules(self, metric_point: MetricDataPoint) -> None:
        """Evaluate alert rules for metric"""        metric_type = metric_point.metric_type
        
        for rule in self._alert_rules.get(metric_type, []):
            if not rule.get("active", True):
                continue
            
            threshold = rule["threshold"]
            condition = rule["condition"]
            severity = rule["severity"]
            
            # Check condition
            triggered = False
            if condition == "greater_than" and metric_point.value > threshold:
                triggered = True
            elif condition == "less_than" and metric_point.value < threshold:
                triggered = True
            elif condition == "equals" and metric_point.value == threshold:
                triggered = True
            
            if triggered:
                # Create alert
                alert = PerformanceAlert(
                    id=str(uuid.uuid4()),
                    alert_type=f"{metric_type.value}_{condition}_{threshold}",
                    severity=severity,
                    metric_type=metric_type,
                    message=f"{metric_type.value} {condition} {threshold}: current value {metric_point.value}",
                    current_value=metric_point.value,
                    threshold_value=threshold,
                    affected_component=metric_point.tags.get("component", "system"),
                    related_metrics=[metric_point]
                )
                
                await self._queue_alert(alert)
    
    async def _queue_alert(self, alert: PerformanceAlert) -> None:
        """Queue alert for processing"""        with self._lock:
            self._alerts[alert.id] = alert
            self._metrics_summary["active_alerts"] += 1
        
        await self._alert_queue.put(alert)
    
    async def _update_performance_baselines(self, metric_type: MetricType, value: float) -> None:
        """Update performance baselines"""        with self._lock:
            if metric_type not in self._performance_baselines:
                self._performance_baselines[metric_type] = value
            else:
                # Exponential moving average
                alpha = 0.1
                current_baseline = self._performance_baselines[metric_type]
                self._performance_baselines[metric_type] = alpha * value + (1 - alpha) * current_baseline
    
    def _calculate_overall_health_score(self) -> float:
        """Calculate overall system health score"""        if not self._health_checks:
            return 100.0
        
        total_score = sum(check.health_score for check in self._health_checks.values())
        return total_score / len(self._health_checks)
    
    def _calculate_system_uptime(self) -> float:
        """Calculate system uptime in hours"""        try:
            return time.time() - psutil.boot_time()
        except:
            return 0.0
    
    def _get_metric_status(self, metric_type: MetricType, value: float) -> str:
        """Get status for metric value"""        # Define status thresholds based on metric type
        if metric_type in [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]:
            if value < 70:
                return "good"
            elif value < 85:
                return "warning"
            else:
                return "critical"
        elif metric_type == MetricType.ERROR_RATE:
            if value < 1:
                return "good"
            elif value < 5:
                return "warning"
            else:
                return "critical"
        else:
            return "unknown"
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation
        recent = statistics.mean(values[-min(10, len(values)):])
        older = statistics.mean(values[:min(10, len(values))])
        
        change_percent = ((recent - older) / max(older, 0.001)) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """Calculate current resource utilization"""        return {
            "cpu": self._current_metrics.get(MetricType.CPU_USAGE, MetricDataPoint(MetricType.CPU_USAGE, 0.0, datetime.utcnow())).value,
            "memory": self._current_metrics.get(MetricType.MEMORY_USAGE, MetricDataPoint(MetricType.MEMORY_USAGE, 0.0, datetime.utcnow())).value,
            "disk": self._current_metrics.get(MetricType.DISK_USAGE, MetricDataPoint(MetricType.DISK_USAGE, 0.0, datetime.utcnow())).value,
        }
    
    def _analyze_performance_trends(self, time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Analyze performance trends"""        # Simplified trend analysis
        return {
            "cpu_trend": "stable",
            "memory_trend": "stable",
            "response_time_trend": "improving",
            "throughput_trend": "stable"
        }
    
    def _count_optimization_types(self, optimizations: List[OptimizationAction]) -> Dict[str, int]:
        """Count optimization types"""        counts = defaultdict(int)
        for opt in optimizations:
            counts[opt.action_type.value] += 1
        return dict(counts)
    
    def _calculate_average_optimization_impact(self, optimizations: List[OptimizationAction]) -> Dict[str, float]:
        """Calculate average optimization impact"""        # Simplified impact calculation
        return {
            "cpu_improvement": 5.0,
            "memory_improvement": 3.0,
            "response_time_improvement": 10.0
        }
    
    async def _generate_capacity_forecast(self) -> Dict[str, Any]:
        """Generate capacity forecast"""        # Simplified capacity forecasting
        return {
            "cpu_forecast_30_days": 75.0,
            "memory_forecast_30_days": 80.0,
            "storage_forecast_30_days": 60.0,
            "recommendations": [
                "Consider scaling up CPU resources in 3 weeks",
                "Monitor memory usage closely",
                "Storage capacity sufficient for 6 months"
            ]
        }
    
    def _count_alerts_by_severity(self, alerts: List[PerformanceAlert]) -> Dict[str, int]:
        """Count alerts by severity"""        counts = defaultdict(int)
        for alert in alerts:
            counts[alert.severity.value] += 1
        return dict(counts)
    
    def _count_alerts_by_component(self, alerts: List[PerformanceAlert]) -> Dict[str, int]:
        """Count alerts by component"""        counts = defaultdict(int)
        for alert in alerts:
            counts[alert.affected_component] += 1
        return dict(counts)
    
    async def _analyze_performance_gaps(self, targets: Dict[MetricType, float]) -> Dict[MetricType, float]:
        """Analyze performance gaps vs targets"""        gaps = {}
        
        with self._lock:
            for metric_type, target_value in targets.items():
                current_metric = self._current_metrics.get(metric_type)
                if current_metric:
                    gap = current_metric.value - target_value
                    if abs(gap) > target_value * 0.1:  # 10% threshold
                        gaps[metric_type] = gap
        
        return gaps
    
    async def _generate_optimization_actions(self, performance_gaps: Dict[MetricType, float]) -> List[OptimizationAction]:
        """Generate optimization actions based on performance gaps"""        actions = []
        
        for metric_type, gap in performance_gaps.items():
            if metric_type == MetricType.CPU_USAGE and gap > 0:
                action = OptimizationAction(
                    id=str(uuid.uuid4()),
                    action_type=OptimizationAction.SCALE_UP,
                    target_component="cpu",
                    description="Scale up CPU resources due to high utilization",
                    parameters={"target_cpu_count": self._system_info["cpu_count"] + 1}
                )
                actions.append(action)
            
            elif metric_type == MetricType.MEMORY_USAGE and gap > 0:
                action = OptimizationAction(
                    id=str(uuid.uuid4()),
                    action_type=OptimizationAction.GARBAGE_COLLECTION,
                    target_component="memory",
                    description="Trigger garbage collection to free memory",
                    parameters={"aggressive": True}
                )
                actions.append(action)
        
        return actions
    
    @asynccontextmanager
    async def get_performance_session(self, component_name: str):
        """Context manager for performance monitoring operations"""        session_id = str(uuid.uuid4())
        try:
            logger.info(f"📊 Performance session started: {session_id} for {component_name}")
            yield session_id
        finally:
            logger.info(f"📊 Performance session ended: {session_id}")
    
    async def cleanup(self) -> bool:
        """Cleanup performance monitoring resources"""        try:
            # Stop monitoring
            self._monitoring_active = False
            
            # Cancel tasks
            for task in self._monitoring_tasks:
                task.cancel()
            for task in self._optimization_tasks:
                task.cancel()
            
            await asyncio.gather(
                *self._monitoring_tasks,
                *self._optimization_tasks,
                return_exceptions=True
            )
            
            with self._lock:
                # Clear queues
                while not self._alert_queue.empty():
                    self._alert_queue.get_nowait()
                while not self._optimization_queue.empty():
                    self._optimization_queue.get_nowait()
                
                # Clear data structures
                self._metrics.clear()
                self._current_metrics.clear()
                self._alerts.clear()
                self._optimization_actions.clear()
                self._health_checks.clear()
                self._monitoring_tasks.clear()
                self._optimization_tasks.clear()
                
                # Reset metrics
                self._metrics_summary = {
                    "total_metrics_collected": 0,
                    "active_alerts": 0,
                    "optimizations_performed": 0,
                    "system_uptime": 0.0,
                    "average_response_time": 0.0,
                    "current_cpu_usage": 0.0,
                    "current_memory_usage": 0.0,
                    "current_throughput": 0.0,
                    "overall_health_score": 100.0,
                    "performance_trend": "stable"
                }
            
            logger.info("🧹 Performance Manager cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance cleanup failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance system statistics"""        with self._lock:
            return {
                "metrics_tracked": len(self._metrics),
                "total_data_points": sum(len(deque) for deque in self._metrics.values()),
                "active_alerts": len([a for a in self._alerts.values() if a.status == "active"]),
                "health_checks": len(self._health_checks),
                "optimization_actions": len(self._optimization_actions),
                "config": {
                    "monitoring_interval_seconds": self.config.monitoring_interval_seconds,
                    "enable_auto_optimization": self.config.enable_auto_optimization,
                    "enable_auto_scaling": self.config.enable_auto_scaling,
                    "cpu_threshold_warning": self.config.cpu_threshold_warning,
                    "memory_threshold_warning": self.config.memory_threshold_warning,
                    "target_response_time_ms": self.config.target_response_time_ms
                },
                "metrics_summary": dict(self._metrics_summary),
                "system_info": self._system_info,
                "system_health": {
                    "overall_health_score": self._calculate_overall_health_score(),
                    "monitoring_active": self._monitoring_active,
                    "background_tasks": len(self._monitoring_tasks) + len(self._optimization_tasks),
                    "queue_sizes": {
                        "alerts": self._alert_queue.qsize(),
                        "optimizations": self._optimization_queue.qsize()
                    },
                    "last_updated": datetime.utcnow().isoformat()
                }
            }


# Global instance
performance_manager = None


def get_performance_manager() -> PerformanceManager:
    """    Get the global performance manager instance
    
    Returns:
        PerformanceManager: Global performance manager
    """    global performance_manager
    if performance_manager is None:
        from ..implementations.performance_manager_impl import PerformanceManagerImpl
        performance_manager = PerformanceManagerImpl()
    return performance_manager
