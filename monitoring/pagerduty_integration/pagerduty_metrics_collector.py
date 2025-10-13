"""
PagerDuty Metrics Collector for IA Chérie Platform
Advanced metrics harvesting and analytics for incident management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib

try:
    import requests
    import prometheus_client
    METRICS_DEPENDENCIES_AVAILABLE = True
except ImportError:
    METRICS_DEPENDENCIES_AVAILABLE = False
    requests = None
    prometheus_client = None

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of PagerDuty metrics"""
    INCIDENT_VOLUME = "incident_volume"
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"
    ESCALATION_RATE = "escalation_rate"
    SLA_COMPLIANCE = "sla_compliance"
    TEAM_PERFORMANCE = "team_performance"
    ALERT_FATIGUE = "alert_fatigue"
    BUSINESS_IMPACT = "business_impact"
    COST_ANALYSIS = "cost_analysis"
    AVAILABILITY = "availability"


class MetricGranularity(Enum):
    """Metric collection granularity"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class MetricStatus(Enum):
    """Metric collection status"""
    COLLECTING = "collecting"
    COMPLETED = "completed"
    FAILED = "failed"
    STALE = "stale"


@dataclass
class MetricDefinition:
    """Metric definition and configuration"""
    metric_id: str
    metric_name: str
    metric_type: MetricType
    description: str
    unit: str
    collection_interval: int  # seconds
    retention_days: int
    aggregation_methods: List[str]
    labels: List[str]
    thresholds: Dict[str, float]
    business_context: str
    creator_economy_relevance: str


@dataclass
class MetricDataPoint:
    """Individual metric data point"""
    metric_id: str
    timestamp: datetime
    value: float
    labels: Dict[str, str]
    metadata: Dict[str, Any]
    source: str
    granularity: MetricGranularity


@dataclass
class MetricSeries:
    """Time series of metric data"""
    series_id: str
    metric_definition: MetricDefinition
    data_points: List[MetricDataPoint]
    start_time: datetime
    end_time: datetime
    aggregated_values: Dict[str, float]
    status: MetricStatus
    last_updated: datetime


@dataclass
class TeamPerformanceMetrics:
    """Team performance metrics"""
    team_id: str
    team_name: str
    period_start: datetime
    period_end: datetime
    incidents_handled: int
    average_response_time: float
    average_resolution_time: float
    escalation_rate: float
    sla_compliance_rate: float
    burnout_risk_score: float
    efficiency_score: float
    alert_fatigue_level: str
    specializations: List[str]
    workload_distribution: Dict[str, float]


@dataclass
class BusinessImpactMetrics:
    """Business impact metrics for Creator Economy"""
    metric_id: str
    period_start: datetime
    period_end: datetime
    total_creators_affected: int
    total_brands_affected: int
    estimated_revenue_loss: float
    creator_satisfaction_impact: float
    brand_trust_impact: float
    platform_reputation_score: float
    competitive_advantage_loss: float
    regulatory_compliance_risk: float
    creator_churn_risk: float
    brand_partnership_risk: float


@dataclass
class AlertFatigueAnalysis:
    """Alert fatigue analysis"""
    analysis_id: str
    team_id: str
    period_start: datetime
    period_end: datetime
    total_alerts: int
    actionable_alerts: int
    false_positive_rate: float
    alert_density_per_hour: float
    peak_alert_periods: List[Dict[str, Any]]
    fatigue_indicators: Dict[str, float]
    recommendations: List[str]
    severity_distribution: Dict[str, int]
    response_time_degradation: float


class PagerDutyMetricsCollector:
    """
    Advanced PagerDuty metrics collection and analytics
    Provides comprehensive incident management analytics for Creator Economy
    """
    
    def __init__(self, pagerduty_client=None, prometheus_gateway_url: str = None):
        """Initialize PagerDuty metrics collector"""
        self.pagerduty_client = pagerduty_client
        self.prometheus_gateway_url = prometheus_gateway_url
        self.metric_definitions = {}
        self.metric_series = {}
        self.team_metrics = {}
        self.collection_tasks = {}
        
        # Initialize metric definitions
        self._initialize_metric_definitions()
        
        # Prometheus metrics (if available)
        self.prometheus_metrics = {}
        if METRICS_DEPENDENCIES_AVAILABLE:
            self._initialize_prometheus_metrics()
        
        # Configuration
        self.config = {
            "collection_enabled": True,
            "prometheus_export": True,
            "retention_days": 90,
            "aggregation_interval": 300,  # 5 minutes
            "team_analysis_interval": 3600,  # 1 hour
            "business_impact_interval": 1800,  # 30 minutes
            "alert_fatigue_threshold": 50,  # alerts per hour
            "auto_optimization": True
        }
        
        logger.info("PagerDuty Metrics Collector initialized")
    
    def _initialize_metric_definitions(self):
        """Initialize Creator Economy specific metric definitions"""
        
        # Incident Volume Metrics
        self.metric_definitions["incident_volume"] = MetricDefinition(
            metric_id="incident_volume",
            metric_name="Incident Volume",
            metric_type=MetricType.INCIDENT_VOLUME,
            description="Number of incidents over time",
            unit="count",
            collection_interval=300,  # 5 minutes
            retention_days=90,
            aggregation_methods=["sum", "avg", "max"],
            labels=["severity", "service", "team", "creator_impact"],
            thresholds={"warning": 10.0, "critical": 20.0},
            business_context="Platform stability and reliability",
            creator_economy_relevance="Direct impact on creator productivity and earnings"
        )
        
        # Response Time Metrics
        self.metric_definitions["response_time"] = MetricDefinition(
            metric_id="response_time",
            metric_name="Incident Response Time",
            metric_type=MetricType.RESPONSE_TIME,
            description="Time from incident detection to first response",
            unit="seconds",
            collection_interval=60,
            retention_days=90,
            aggregation_methods=["avg", "p50", "p95", "p99"],
            labels=["severity", "team", "escalation_level"],
            thresholds={"p1": 300.0, "p2": 900.0, "p3": 1800.0},
            business_context="Service level agreement compliance",
            creator_economy_relevance="Faster response = less creator disruption"
        )
        
        # Resolution Time Metrics
        self.metric_definitions["resolution_time"] = MetricDefinition(
            metric_id="resolution_time",
            metric_name="Incident Resolution Time",
            metric_type=MetricType.RESOLUTION_TIME,
            description="Time from incident detection to resolution",
            unit="seconds",
            collection_interval=60,
            retention_days=90,
            aggregation_methods=["avg", "p50", "p95", "p99"],
            labels=["severity", "service", "root_cause"],
            thresholds={"p1": 3600.0, "p2": 14400.0, "p3": 86400.0},
            business_context="Operational efficiency and customer satisfaction",
            creator_economy_relevance="Shorter downtime = maintained creator revenue"
        )
        
        # SLA Compliance Metrics
        self.metric_definitions["sla_compliance"] = MetricDefinition(
            metric_id="sla_compliance",
            metric_name="SLA Compliance Rate",
            metric_type=MetricType.SLA_COMPLIANCE,
            description="Percentage of incidents meeting SLA targets",
            unit="percentage",
            collection_interval=3600,  # 1 hour
            retention_days=365,  # Keep longer for trend analysis
            aggregation_methods=["avg", "min", "max"],
            labels=["severity", "service", "team"],
            thresholds={"warning": 95.0, "critical": 90.0},
            business_context="Service quality and contract compliance",
            creator_economy_relevance="Consistent service quality builds creator trust"
        )
        
        # Team Performance Metrics
        self.metric_definitions["team_performance"] = MetricDefinition(
            metric_id="team_performance",
            metric_name="Team Performance Score",
            metric_type=MetricType.TEAM_PERFORMANCE,
            description="Composite team performance score",
            unit="score",
            collection_interval=3600,
            retention_days=90,
            aggregation_methods=["avg", "trend"],
            labels=["team", "skill_area", "shift"],
            thresholds={"excellent": 90.0, "good": 75.0, "needs_improvement": 60.0},
            business_context="Team productivity and skill development",
            creator_economy_relevance="High-performing teams = reliable creator platform"
        )
        
        # Alert Fatigue Metrics
        self.metric_definitions["alert_fatigue"] = MetricDefinition(
            metric_id="alert_fatigue",
            metric_name="Alert Fatigue Index",
            metric_type=MetricType.ALERT_FATIGUE,
            description="Measure of alert fatigue impact on team",
            unit="index",
            collection_interval=1800,  # 30 minutes
            retention_days=60,
            aggregation_methods=["avg", "max", "trend"],
            labels=["team", "alert_source", "time_of_day"],
            thresholds={"low": 30.0, "medium": 60.0, "high": 80.0},
            business_context="Team sustainability and alert quality",
            creator_economy_relevance="Focused alerts = faster creator issue resolution"
        )
        
        # Business Impact Metrics
        self.metric_definitions["business_impact"] = MetricDefinition(
            metric_id="business_impact",
            metric_name="Business Impact Score",
            metric_type=MetricType.BUSINESS_IMPACT,
            description="Financial and strategic impact of incidents",
            unit="dollars",
            collection_interval=1800,
            retention_days=365,
            aggregation_methods=["sum", "avg", "max"],
            labels=["impact_type", "creator_segment", "brand_tier"],
            thresholds={"minor": 1000.0, "major": 10000.0, "critical": 50000.0},
            business_context="ROI of incident management investment",
            creator_economy_relevance="Direct correlation to creator and brand revenue"
        )
        
        # Availability Metrics
        self.metric_definitions["availability"] = MetricDefinition(
            metric_id="availability",
            metric_name="Service Availability",
            metric_type=MetricType.AVAILABILITY,
            description="Service uptime percentage",
            unit="percentage",
            collection_interval=300,
            retention_days=365,
            aggregation_methods=["avg", "min"],
            labels=["service", "region", "user_type"],
            thresholds={"target": 99.9, "warning": 99.5, "critical": 99.0},
            business_context="Platform reliability and user experience",
            creator_economy_relevance="High availability = creator earning potential"
        )
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        if not METRICS_DEPENDENCIES_AVAILABLE:
            return
        
        try:
            # Counter metrics
            self.prometheus_metrics["incidents_total"] = prometheus_client.Counter(
                "pagerduty_incidents_total",
                "Total number of incidents",
                ["severity", "service", "team"]
            )
            
            # Histogram metrics
            self.prometheus_metrics["response_time"] = prometheus_client.Histogram(
                "pagerduty_response_time_seconds",
                "Incident response time",
                ["severity", "team"],
                buckets=[30, 60, 300, 900, 1800, 3600, 7200]
            )
            
            self.prometheus_metrics["resolution_time"] = prometheus_client.Histogram(
                "pagerduty_resolution_time_seconds", 
                "Incident resolution time",
                ["severity", "service"],
                buckets=[300, 900, 1800, 3600, 7200, 14400, 86400]
            )
            
            # Gauge metrics
            self.prometheus_metrics["sla_compliance"] = prometheus_client.Gauge(
                "pagerduty_sla_compliance_rate",
                "SLA compliance rate",
                ["severity", "team"]
            )
            
            self.prometheus_metrics["team_performance"] = prometheus_client.Gauge(
                "pagerduty_team_performance_score",
                "Team performance score",
                ["team", "metric_type"]
            )
            
            self.prometheus_metrics["alert_fatigue"] = prometheus_client.Gauge(
                "pagerduty_alert_fatigue_index",
                "Alert fatigue index",
                ["team"]
            )
            
            self.prometheus_metrics["business_impact"] = prometheus_client.Gauge(
                "pagerduty_business_impact_dollars",
                "Business impact in dollars",
                ["impact_type", "creator_segment"]
            )
            
            logger.info("Prometheus metrics initialized")
            
        except Exception as e:
            logger.error(f"Prometheus metrics initialization failed: {e}")
    
    async def start_metric_collection(self):
        """Start all metric collection tasks"""
        try:
            if not self.config["collection_enabled"]:
                logger.info("Metric collection disabled")
                return
            
            # Start collection tasks for each metric
            for metric_id, definition in self.metric_definitions.items():
                task = asyncio.create_task(
                    self._collect_metric_continuously(metric_id, definition)
                )
                self.collection_tasks[metric_id] = task
                logger.info(f"Started collection for metric: {metric_id}")
            
            # Start team analysis task
            team_task = asyncio.create_task(self._analyze_team_performance_continuously())
            self.collection_tasks["team_analysis"] = team_task
            
            # Start business impact analysis
            business_task = asyncio.create_task(self._analyze_business_impact_continuously())
            self.collection_tasks["business_analysis"] = business_task
            
            # Start alert fatigue analysis
            fatigue_task = asyncio.create_task(self._analyze_alert_fatigue_continuously())
            self.collection_tasks["fatigue_analysis"] = fatigue_task
            
            logger.info("All metric collection tasks started")
            
        except Exception as e:
            logger.error(f"Metric collection start failed: {e}")
    
    async def _collect_metric_continuously(self, metric_id: str, definition: MetricDefinition):
        """Continuously collect specific metric"""
        try:
            while True:
                await self._collect_single_metric(metric_id, definition)
                await asyncio.sleep(definition.collection_interval)
                
        except asyncio.CancelledError:
            logger.info(f"Metric collection cancelled for {metric_id}")
        except Exception as e:
            logger.error(f"Continuous metric collection failed for {metric_id}: {e}")
    
    async def _collect_single_metric(self, metric_id: str, definition: MetricDefinition):
        """Collect single metric data point"""
        try:
            # Collect based on metric type
            if definition.metric_type == MetricType.INCIDENT_VOLUME:
                data_points = await self._collect_incident_volume()
            elif definition.metric_type == MetricType.RESPONSE_TIME:
                data_points = await self._collect_response_times()
            elif definition.metric_type == MetricType.RESOLUTION_TIME:
                data_points = await self._collect_resolution_times()
            elif definition.metric_type == MetricType.SLA_COMPLIANCE:
                data_points = await self._collect_sla_compliance()
            elif definition.metric_type == MetricType.AVAILABILITY:
                data_points = await self._collect_availability_metrics()
            else:
                logger.warning(f"Unknown metric type: {definition.metric_type}")
                return
            
            # Store data points
            if metric_id not in self.metric_series:
                self.metric_series[metric_id] = MetricSeries(
                    series_id=str(uuid.uuid4()),
                    metric_definition=definition,
                    data_points=[],
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow(),
                    aggregated_values={},
                    status=MetricStatus.COLLECTING,
                    last_updated=datetime.utcnow()
                )
            
            series = self.metric_series[metric_id]
            series.data_points.extend(data_points)
            series.end_time = datetime.utcnow()
            series.last_updated = datetime.utcnow()
            
            # Trim old data points
            await self._trim_old_data_points(series, definition.retention_days)
            
            # Update aggregated values
            await self._update_aggregated_values(series, definition)
            
            # Export to Prometheus
            if self.config["prometheus_export"] and METRICS_DEPENDENCIES_AVAILABLE:
                await self._export_to_prometheus(metric_id, data_points)
            
            logger.debug(f"Collected {len(data_points)} data points for {metric_id}")
            
        except Exception as e:
            logger.error(f"Single metric collection failed for {metric_id}: {e}")
    
    async def _collect_incident_volume(self) -> List[MetricDataPoint]:
        """Collect incident volume metrics"""
        try:
            data_points = []
            
            # Mock incident data - in real implementation, query PagerDuty API
            incident_counts = {
                ("p1", "creator-api"): 2,
                ("p2", "content-processor"): 5,
                ("p3", "analytics"): 8,
                ("p4", "notifications"): 12
            }
            
            for (severity, service), count in incident_counts.items():
                data_point = MetricDataPoint(
                    metric_id="incident_volume",
                    timestamp=datetime.utcnow(),
                    value=float(count),
                    labels={
                        "severity": severity,
                        "service": service,
                        "team": self._get_team_for_service(service),
                        "creator_impact": self._assess_creator_impact(service, severity)
                    },
                    metadata={"collection_method": "api_query"},
                    source="pagerduty_api",
                    granularity=MetricGranularity.MINUTE
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Incident volume collection failed: {e}")
            return []
    
    async def _collect_response_times(self) -> List[MetricDataPoint]:
        """Collect response time metrics"""
        try:
            data_points = []
            
            # Mock response time data
            response_times = {
                ("p1", "sre-team"): 180.0,     # 3 minutes
                ("p2", "backend-team"): 720.0,  # 12 minutes
                ("p3", "support-team"): 1440.0, # 24 minutes
                ("p4", "support-team"): 2880.0  # 48 minutes
            }
            
            for (severity, team), time_seconds in response_times.items():
                data_point = MetricDataPoint(
                    metric_id="response_time",
                    timestamp=datetime.utcnow(),
                    value=time_seconds,
                    labels={
                        "severity": severity,
                        "team": team,
                        "escalation_level": "1" if time_seconds < 600 else "2"
                    },
                    metadata={"measurement_method": "timestamp_diff"},
                    source="pagerduty_api",
                    granularity=MetricGranularity.MINUTE
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Response time collection failed: {e}")
            return []
    
    async def _collect_resolution_times(self) -> List[MetricDataPoint]:
        """Collect resolution time metrics"""
        try:
            data_points = []
            
            # Mock resolution time data
            resolution_times = {
                ("p1", "creator-api", "infrastructure"): 2400.0,    # 40 minutes
                ("p2", "content-processor", "application"): 7200.0, # 2 hours
                ("p3", "analytics", "database"): 18000.0,          # 5 hours
                ("p4", "notifications", "configuration"): 43200.0   # 12 hours
            }
            
            for (severity, service, root_cause), time_seconds in resolution_times.items():
                data_point = MetricDataPoint(
                    metric_id="resolution_time",
                    timestamp=datetime.utcnow(),
                    value=time_seconds,
                    labels={
                        "severity": severity,
                        "service": service,
                        "root_cause": root_cause
                    },
                    metadata={"resolution_method": "automated" if time_seconds < 3600 else "manual"},
                    source="pagerduty_api",
                    granularity=MetricGranularity.MINUTE
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Resolution time collection failed: {e}")
            return []
    
    async def _collect_sla_compliance(self) -> List[MetricDataPoint]:
        """Collect SLA compliance metrics"""
        try:
            data_points = []
            
            # Mock SLA compliance data
            sla_rates = {
                ("p1", "sre-team"): 95.5,
                ("p2", "backend-team"): 98.2,
                ("p3", "support-team"): 99.1,
                ("p4", "support-team"): 99.8
            }
            
            for (severity, team), compliance_rate in sla_rates.items():
                data_point = MetricDataPoint(
                    metric_id="sla_compliance",
                    timestamp=datetime.utcnow(),
                    value=compliance_rate,
                    labels={
                        "severity": severity,
                        "team": team,
                        "period": "daily"
                    },
                    metadata={"calculation_method": "rolling_average"},
                    source="internal_calculation",
                    granularity=MetricGranularity.HOUR
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"SLA compliance collection failed: {e}")
            return []
    
    async def _collect_availability_metrics(self) -> List[MetricDataPoint]:
        """Collect service availability metrics"""
        try:
            data_points = []
            
            # Mock availability data for Creator Economy services
            availability_data = {
                ("creator-api", "us-east", "creators"): 99.95,
                ("content-processor", "us-east", "creators"): 99.92,
                ("brand-dashboard", "us-east", "brands"): 99.98,
                ("analytics", "global", "all"): 99.85,
                ("payment-processor", "global", "all"): 99.99
            }
            
            for (service, region, user_type), availability in availability_data.items():
                data_point = MetricDataPoint(
                    metric_id="availability",
                    timestamp=datetime.utcnow(),
                    value=availability,
                    labels={
                        "service": service,
                        "region": region,
                        "user_type": user_type
                    },
                    metadata={"measurement_window": "5_minutes"},
                    source="monitoring_system",
                    granularity=MetricGranularity.MINUTE
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Availability metrics collection failed: {e}")
            return []
    
    def _get_team_for_service(self, service: str) -> str:
        """Get responsible team for service"""
        team_mapping = {
            "creator-api": "backend-team",
            "content-processor": "ml-team",
            "brand-dashboard": "frontend-team",
            "analytics": "data-team",
            "payment-processor": "fintech-team",
            "notifications": "platform-team"
        }
        return team_mapping.get(service, "platform-team")
    
    def _assess_creator_impact(self, service: str, severity: str) -> str:
        """Assess impact on creator community"""
        high_impact_services = ["creator-api", "content-processor", "payment-processor"]
        
        if service in high_impact_services:
            if severity in ["p1", "p2"]:
                return "high"
            else:
                return "medium"
        else:
            if severity in ["p1", "p2"]:
                return "medium"
            else:
                return "low"
    
    async def _trim_old_data_points(self, series: MetricSeries, retention_days: int):
        """Remove data points older than retention period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=retention_days)
            series.data_points = [
                dp for dp in series.data_points 
                if dp.timestamp > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Data trimming failed: {e}")
    
    async def _update_aggregated_values(self, series: MetricSeries, definition: MetricDefinition):
        """Update aggregated values for metric series"""
        try:
            if not series.data_points:
                return
            
            values = [dp.value for dp in series.data_points]
            
            for method in definition.aggregation_methods:
                if method == "sum":
                    series.aggregated_values["sum"] = sum(values)
                elif method == "avg":
                    series.aggregated_values["avg"] = sum(values) / len(values)
                elif method == "max":
                    series.aggregated_values["max"] = max(values)
                elif method == "min":
                    series.aggregated_values["min"] = min(values)
                elif method == "p50":
                    sorted_values = sorted(values)
                    series.aggregated_values["p50"] = sorted_values[len(sorted_values) // 2]
                elif method == "p95":
                    sorted_values = sorted(values)
                    series.aggregated_values["p95"] = sorted_values[int(len(sorted_values) * 0.95)]
                elif method == "p99":
                    sorted_values = sorted(values)
                    series.aggregated_values["p99"] = sorted_values[int(len(sorted_values) * 0.99)]
            
        except Exception as e:
            logger.error(f"Aggregated values update failed: {e}")
    
    async def _export_to_prometheus(self, metric_id: str, data_points: List[MetricDataPoint]):
        """Export metrics to Prometheus"""
        try:
            if not METRICS_DEPENDENCIES_AVAILABLE:
                return
            
            for dp in data_points:
                if metric_id == "incident_volume" and "incidents_total" in self.prometheus_metrics:
                    self.prometheus_metrics["incidents_total"].labels(
                        severity=dp.labels.get("severity", "unknown"),
                        service=dp.labels.get("service", "unknown"),
                        team=dp.labels.get("team", "unknown")
                    ).inc(dp.value)
                
                elif metric_id == "response_time" and "response_time" in self.prometheus_metrics:
                    self.prometheus_metrics["response_time"].labels(
                        severity=dp.labels.get("severity", "unknown"),
                        team=dp.labels.get("team", "unknown")
                    ).observe(dp.value)
                
                elif metric_id == "resolution_time" and "resolution_time" in self.prometheus_metrics:
                    self.prometheus_metrics["resolution_time"].labels(
                        severity=dp.labels.get("severity", "unknown"),
                        service=dp.labels.get("service", "unknown")
                    ).observe(dp.value)
                
                elif metric_id == "sla_compliance" and "sla_compliance" in self.prometheus_metrics:
                    self.prometheus_metrics["sla_compliance"].labels(
                        severity=dp.labels.get("severity", "unknown"),
                        team=dp.labels.get("team", "unknown")
                    ).set(dp.value)
            
        except Exception as e:
            logger.error(f"Prometheus export failed: {e}")
    
    async def _analyze_team_performance_continuously(self):
        """Continuously analyze team performance"""
        try:
            while True:
                await self._analyze_team_performance()
                await asyncio.sleep(self.config["team_analysis_interval"])
                
        except asyncio.CancelledError:
            logger.info("Team performance analysis cancelled")
        except Exception as e:
            logger.error(f"Continuous team performance analysis failed: {e}")
    
    async def _analyze_team_performance(self):
        """Analyze team performance metrics"""
        try:
            teams = ["sre-team", "backend-team", "frontend-team", "data-team", "platform-team"]
            
            for team in teams:
                metrics = await self._calculate_team_metrics(team)
                self.team_metrics[team] = metrics
                
                # Export team performance to Prometheus
                if (self.config["prometheus_export"] and 
                    METRICS_DEPENDENCIES_AVAILABLE and 
                    "team_performance" in self.prometheus_metrics):
                    
                    self.prometheus_metrics["team_performance"].labels(
                        team=team,
                        metric_type="efficiency"
                    ).set(metrics.efficiency_score)
                    
                    self.prometheus_metrics["team_performance"].labels(
                        team=team,
                        metric_type="sla_compliance"
                    ).set(metrics.sla_compliance_rate)
            
            logger.info("Team performance analysis completed")
            
        except Exception as e:
            logger.error(f"Team performance analysis failed: {e}")
    
    async def _calculate_team_metrics(self, team_id: str) -> TeamPerformanceMetrics:
        """Calculate metrics for specific team"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)  # Last 24 hours
            
            # Mock team metrics calculation
            # In real implementation, aggregate from actual incident data
            
            base_performance = {
                "sre-team": {"incidents": 8, "response": 240, "resolution": 3600, "escalation": 0.1},
                "backend-team": {"incidents": 12, "response": 480, "resolution": 7200, "escalation": 0.15},
                "frontend-team": {"incidents": 6, "response": 600, "resolution": 5400, "escalation": 0.05},
                "data-team": {"incidents": 4, "response": 900, "resolution": 10800, "escalation": 0.08},
                "platform-team": {"incidents": 10, "response": 720, "resolution": 9000, "escalation": 0.12}
            }
            
            team_data = base_performance.get(team_id, base_performance["platform-team"])
            
            # Calculate efficiency score (composite metric)
            response_score = max(0, 100 - (team_data["response"] / 300) * 20)  # 300s baseline
            resolution_score = max(0, 100 - (team_data["resolution"] / 3600) * 10)  # 1h baseline
            escalation_score = max(0, 100 - (team_data["escalation"] * 200))  # 0.1 baseline
            
            efficiency_score = (response_score + resolution_score + escalation_score) / 3
            
            # Calculate burnout risk based on workload
            incidents_per_day = team_data["incidents"]
            burnout_risk = min(100, max(0, (incidents_per_day - 5) * 10))  # 5 incidents baseline
            
            # SLA compliance (mock)
            sla_compliance = max(95.0, 100.0 - team_data["escalation"] * 50)
            
            # Alert fatigue level
            alert_fatigue_level = "low"
            if incidents_per_day > 15:
                alert_fatigue_level = "high"
            elif incidents_per_day > 10:
                alert_fatigue_level = "medium"
            
            return TeamPerformanceMetrics(
                team_id=team_id,
                team_name=team_id.replace("-", " ").title(),
                period_start=start_time,
                period_end=end_time,
                incidents_handled=team_data["incidents"],
                average_response_time=team_data["response"],
                average_resolution_time=team_data["resolution"],
                escalation_rate=team_data["escalation"],
                sla_compliance_rate=sla_compliance,
                burnout_risk_score=burnout_risk,
                efficiency_score=efficiency_score,
                alert_fatigue_level=alert_fatigue_level,
                specializations=self._get_team_specializations(team_id),
                workload_distribution={"on_call": 0.3, "development": 0.5, "incidents": 0.2}
            )
            
        except Exception as e:
            logger.error(f"Team metrics calculation failed for {team_id}: {e}")
            return TeamPerformanceMetrics(
                team_id=team_id,
                team_name=team_id,
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow(),
                incidents_handled=0,
                average_response_time=0.0,
                average_resolution_time=0.0,
                escalation_rate=0.0,
                sla_compliance_rate=0.0,
                burnout_risk_score=0.0,
                efficiency_score=0.0,
                alert_fatigue_level="unknown",
                specializations=[],
                workload_distribution={}
            )
    
    def _get_team_specializations(self, team_id: str) -> List[str]:
        """Get team specializations"""
        specializations = {
            "sre-team": ["infrastructure", "monitoring", "performance", "automation"],
            "backend-team": ["apis", "databases", "microservices", "integration"],
            "frontend-team": ["ui", "ux", "web", "mobile"],
            "data-team": ["analytics", "ml", "etl", "reporting"],
            "platform-team": ["deployment", "security", "compliance", "operations"]
        }
        return specializations.get(team_id, [])
    
    async def _analyze_business_impact_continuously(self):
        """Continuously analyze business impact"""
        try:
            while True:
                await self._analyze_business_impact()
                await asyncio.sleep(self.config["business_impact_interval"])
                
        except asyncio.CancelledError:
            logger.info("Business impact analysis cancelled")
        except Exception as e:
            logger.error(f"Continuous business impact analysis failed: {e}")
    
    async def _analyze_business_impact(self):
        """Analyze business impact of incidents"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)  # Last hour
            
            # Calculate Creator Economy specific impacts
            impact_metrics = BusinessImpactMetrics(
                metric_id=str(uuid.uuid4()),
                period_start=start_time,
                period_end=end_time,
                total_creators_affected=await self._calculate_affected_creators(),
                total_brands_affected=await self._calculate_affected_brands(),
                estimated_revenue_loss=await self._calculate_revenue_impact(),
                creator_satisfaction_impact=await self._calculate_satisfaction_impact(),
                brand_trust_impact=await self._calculate_brand_trust_impact(),
                platform_reputation_score=await self._calculate_reputation_score(),
                competitive_advantage_loss=await self._calculate_competitive_loss(),
                regulatory_compliance_risk=await self._calculate_compliance_risk(),
                creator_churn_risk=await self._calculate_churn_risk(),
                brand_partnership_risk=await self._calculate_partnership_risk()
            )
            
            # Export to Prometheus
            if (self.config["prometheus_export"] and 
                METRICS_DEPENDENCIES_AVAILABLE and 
                "business_impact" in self.prometheus_metrics):
                
                self.prometheus_metrics["business_impact"].labels(
                    impact_type="revenue_loss",
                    creator_segment="all"
                ).set(impact_metrics.estimated_revenue_loss)
                
                self.prometheus_metrics["business_impact"].labels(
                    impact_type="reputation",
                    creator_segment="all"
                ).set(impact_metrics.platform_reputation_score)
            
            logger.info(f"Business impact analysis completed: ${impact_metrics.estimated_revenue_loss:.2f} revenue impact")
            
        except Exception as e:
            logger.error(f"Business impact analysis failed: {e}")
    
    async def _calculate_affected_creators(self) -> int:
        """Calculate number of affected creators"""
        # Mock calculation based on incident data
        return 1250  # Example: 1,250 creators affected
    
    async def _calculate_affected_brands(self) -> int:
        """Calculate number of affected brands"""
        return 85  # Example: 85 brands affected
    
    async def _calculate_revenue_impact(self) -> float:
        """Calculate estimated revenue impact"""
        # Mock calculation: creator earnings loss + platform fees loss
        creator_loss = 1250 * 50.0  # $50 avg per creator per hour
        platform_loss = creator_loss * 0.15  # 15% platform fee
        return creator_loss + platform_loss
    
    async def _calculate_satisfaction_impact(self) -> float:
        """Calculate creator satisfaction impact"""
        return 7.5  # Scale of 1-10, 7.5 = moderate impact
    
    async def _calculate_brand_trust_impact(self) -> float:
        """Calculate brand trust impact"""
        return 6.8  # Scale of 1-10, 6.8 = moderate-high impact
    
    async def _calculate_reputation_score(self) -> float:
        """Calculate platform reputation score"""
        return 85.2  # Scale of 0-100, 85.2 = good reputation
    
    async def _calculate_competitive_loss(self) -> float:
        """Calculate competitive advantage loss"""
        return 2.5  # Scale of 1-10, 2.5 = low competitive loss
    
    async def _calculate_compliance_risk(self) -> float:
        """Calculate regulatory compliance risk"""
        return 1.8  # Scale of 1-10, 1.8 = low compliance risk
    
    async def _calculate_churn_risk(self) -> float:
        """Calculate creator churn risk"""
        return 3.2  # Scale of 1-10, 3.2 = low-medium churn risk
    
    async def _calculate_partnership_risk(self) -> float:
        """Calculate brand partnership risk"""
        return 2.9  # Scale of 1-10, 2.9 = low partnership risk
    
    async def _analyze_alert_fatigue_continuously(self):
        """Continuously analyze alert fatigue"""
        try:
            while True:
                await self._analyze_alert_fatigue()
                await asyncio.sleep(self.config["team_analysis_interval"])
                
        except asyncio.CancelledError:
            logger.info("Alert fatigue analysis cancelled")
        except Exception as e:
            logger.error(f"Continuous alert fatigue analysis failed: {e}")
    
    async def _analyze_alert_fatigue(self):
        """Analyze alert fatigue for teams"""
        try:
            teams = ["sre-team", "backend-team", "frontend-team", "data-team", "platform-team"]
            
            for team in teams:
                fatigue_analysis = await self._calculate_alert_fatigue(team)
                
                # Export to Prometheus
                if (self.config["prometheus_export"] and 
                    METRICS_DEPENDENCIES_AVAILABLE and 
                    "alert_fatigue" in self.prometheus_metrics):
                    
                    fatigue_index = (fatigue_analysis.false_positive_rate * 50 + 
                                   min(fatigue_analysis.alert_density_per_hour, 100) * 0.5)
                    
                    self.prometheus_metrics["alert_fatigue"].labels(team=team).set(fatigue_index)
            
            logger.info("Alert fatigue analysis completed")
            
        except Exception as e:
            logger.error(f"Alert fatigue analysis failed: {e}")
    
    async def _calculate_alert_fatigue(self, team_id: str) -> AlertFatigueAnalysis:
        """Calculate alert fatigue analysis for team"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            # Mock alert fatigue data
            alert_data = {
                "sre-team": {"total": 120, "actionable": 96, "density": 5.0},
                "backend-team": {"total": 85, "actionable": 78, "density": 3.5},
                "frontend-team": {"total": 45, "actionable": 43, "density": 1.9},
                "data-team": {"total": 30, "actionable": 28, "density": 1.25},
                "platform-team": {"total": 65, "actionable": 58, "density": 2.7}
            }
            
            team_data = alert_data.get(team_id, alert_data["platform-team"])
            
            false_positive_rate = 1.0 - (team_data["actionable"] / team_data["total"])
            
            # Generate recommendations based on analysis
            recommendations = []
            if false_positive_rate > 0.2:
                recommendations.append("Review alert thresholds to reduce false positives")
            if team_data["density"] > 4.0:
                recommendations.append("Implement alert grouping and deduplication")
            if team_data["total"] > 100:
                recommendations.append("Consider alert prioritization system")
            
            return AlertFatigueAnalysis(
                analysis_id=str(uuid.uuid4()),
                team_id=team_id,
                period_start=start_time,
                period_end=end_time,
                total_alerts=team_data["total"],
                actionable_alerts=team_data["actionable"],
                false_positive_rate=false_positive_rate,
                alert_density_per_hour=team_data["density"],
                peak_alert_periods=[
                    {"start": "09:00", "end": "11:00", "count": 25},
                    {"start": "14:00", "end": "16:00", "count": 22}
                ],
                fatigue_indicators={
                    "response_time_degradation": 15.5 if false_positive_rate > 0.15 else 5.2,
                    "escalation_rate_increase": 8.3 if team_data["density"] > 3.0 else 2.1,
                    "team_satisfaction_score": 6.5 if false_positive_rate > 0.2 else 8.2
                },
                recommendations=recommendations,
                severity_distribution={"p1": 5, "p2": 15, "p3": 35, "p4": 45},
                response_time_degradation=15.5 if false_positive_rate > 0.15 else 5.2
            )
            
        except Exception as e:
            logger.error(f"Alert fatigue calculation failed for {team_id}: {e}")
            return AlertFatigueAnalysis(
                analysis_id=str(uuid.uuid4()),
                team_id=team_id,
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow(),
                total_alerts=0,
                actionable_alerts=0,
                false_positive_rate=0.0,
                alert_density_per_hour=0.0,
                peak_alert_periods=[],
                fatigue_indicators={},
                recommendations=[],
                severity_distribution={},
                response_time_degradation=0.0
            )
    
    async def get_metrics_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive metrics dashboard"""
        try:
            dashboard = {
                "summary": {
                    "total_metrics_collected": len(self.metric_series),
                    "active_collection_tasks": len([t for t in self.collection_tasks.values() if not t.done()]),
                    "data_points_today": await self._count_todays_data_points(),
                    "prometheus_integration": self.config["prometheus_export"] and METRICS_DEPENDENCIES_AVAILABLE
                },
                "incident_metrics": {
                    "volume_trend": "stable",  # Mock trend
                    "avg_response_time": "4.2 minutes",
                    "avg_resolution_time": "2.1 hours",
                    "sla_compliance": "97.8%"
                },
                "team_performance": {
                    team_id: {
                        "efficiency_score": metrics.efficiency_score,
                        "sla_compliance": metrics.sla_compliance_rate,
                        "burnout_risk": metrics.burnout_risk_score,
                        "alert_fatigue": metrics.alert_fatigue_level
                    }
                    for team_id, metrics in self.team_metrics.items()
                },
                "business_impact": {
                    "estimated_hourly_revenue_impact": "$73,500",
                    "creators_affected_24h": "2,450",
                    "brands_affected_24h": "165",
                    "platform_reputation_score": "87.3/100"
                },
                "collection_status": {
                    metric_id: {
                        "status": series.status.value,
                        "last_updated": series.last_updated.isoformat(),
                        "data_points": len(series.data_points)
                    }
                    for metric_id, series in self.metric_series.items()
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return {}
    
    async def _count_todays_data_points(self) -> int:
        """Count data points collected today"""
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            total_count = 0
            
            for series in self.metric_series.values():
                today_points = [
                    dp for dp in series.data_points 
                    if dp.timestamp >= today_start
                ]
                total_count += len(today_points)
            
            return total_count
            
        except Exception as e:
            logger.error(f"Data point counting failed: {e}")
            return 0
    
    async def stop_metric_collection(self):
        """Stop all metric collection tasks"""
        try:
            for task_name, task in self.collection_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                logger.info(f"Stopped collection task: {task_name}")
            
            self.collection_tasks.clear()
            logger.info("All metric collection tasks stopped")
            
        except Exception as e:
            logger.error(f"Metric collection stop failed: {e}")


# Global PagerDuty metrics collector instance
_pagerduty_metrics_collector = None


def get_pagerduty_metrics_collector(pagerduty_client=None, 
                                  prometheus_gateway_url: str = None) -> PagerDutyMetricsCollector:
    """Get PagerDuty metrics collector instance"""
    global _pagerduty_metrics_collector
    if _pagerduty_metrics_collector is None:
        _pagerduty_metrics_collector = PagerDutyMetricsCollector(pagerduty_client, prometheus_gateway_url)
    return _pagerduty_metrics_collector


def create_pagerduty_metrics_collector(pagerduty_client=None,
                                     prometheus_gateway_url: str = None) -> PagerDutyMetricsCollector:
    """Create new PagerDuty metrics collector instance"""
    return PagerDutyMetricsCollector(pagerduty_client, prometheus_gateway_url)


# Export main classes and functions
__all__ = [
    'PagerDutyMetricsCollector',
    'MetricDefinition',
    'MetricDataPoint',
    'MetricSeries',
    'TeamPerformanceMetrics',
    'BusinessImpactMetrics',
    'AlertFatigueAnalysis',
    'MetricType',
    'MetricGranularity',
    'MetricStatus',
    'get_pagerduty_metrics_collector',
    'create_pagerduty_metrics_collector'
]