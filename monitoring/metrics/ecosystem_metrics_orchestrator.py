"""🌐 Ecosystem Metrics Orchestrator - Master Analytics Coordination System
========================================================================

Advanced ecosystem metrics orchestration and cross-service correlation system for Ainflue.
Provides centralized metrics coordination, inter-service dependency tracking, global platform 
analytics, master dashboard management, and comprehensive ecosystem health monitoring.

Enhanced Features:
- Cross-service metrics correlation and analysis
- Ecosystem-wide health monitoring and optimization
- Inter-service dependency tracking and impact analysis
- Global platform analytics with real-time insights
- Master metrics dashboard orchestration
- Service mesh observability and performance tracking
- End-to-end creator journey analytics across all services
- Automated ecosystem optimization recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict, deque
import statistics
import uuid
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading
import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of services in the ecosystem."""
    CONTENT_PROCESSING = "content_processing"
    USER_MANAGEMENT = "user_management"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"
    NOTIFICATIONS = "notifications"
    STORAGE = "storage"
    SECURITY = "security"
    COLLABORATION = "collaboration"
    DISTRIBUTION = "distribution"
    PROTECTION = "protection"
    GAMIFICATION = "gamification"
    SEO = "seo"


class MetricScope(Enum):
    """Scope of metrics collection."""
    SERVICE_LEVEL = "service_level"
    CROSS_SERVICE = "cross_service"
    ECOSYSTEM_WIDE = "ecosystem_wide"
    BUSINESS_DOMAIN = "business_domain"
    CREATOR_JOURNEY = "creator_journey"


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    DOWN = "down"


class DependencyType(Enum):
    """Types of service dependencies."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    DATA_FLOW = "data_flow"
    SHARED_RESOURCE = "shared_resource"
    EVENT_DRIVEN = "event_driven"


@dataclass
class ServiceMetric:
    """Individual service metric data."""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = ""
    service_type: ServiceType = ServiceType.ANALYTICS
    metric_name: str = ""
    metric_value: Union[float, int, str] = 0
    metric_type: str = "gauge"  # gauge, counter, histogram, summary
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    scope: MetricScope = MetricScope.SERVICE_LEVEL


@dataclass
class ServiceDependency:
    """Service dependency relationship."""
    dependency_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_service: str = ""
    target_service: str = ""
    dependency_type: DependencyType = DependencyType.SYNCHRONOUS
    criticality: str = "medium"  # low, medium, high, critical
    sla_target: Optional[float] = None  # in milliseconds
    current_latency: Optional[float] = None
    success_rate: float = 100.0  # percentage
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    health_status: HealthStatus = HealthStatus.HEALTHY


@dataclass
class EcosystemHealth:
    """Overall ecosystem health assessment."""
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    overall_health_score: float = 0.0  # 0-100
    service_health_scores: Dict[str, float] = field(default_factory=dict)
    critical_issues: List[str] = field(default_factory=list)
    performance_bottlenecks: List[str] = field(default_factory=list)
    dependency_issues: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    health_trends: Dict[str, str] = field(default_factory=dict)  # improving, stable, degrading
    assessment_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreatorJourneyMetrics:
    """End-to-end creator journey metrics."""
    journey_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    journey_stage: str = ""  # onboarding, content_creation, monetization, growth
    start_timestamp: datetime = field(default_factory=datetime.utcnow)
    end_timestamp: Optional[datetime] = None
    services_involved: List[str] = field(default_factory=list)
    total_duration: Optional[timedelta] = None
    stage_durations: Dict[str, timedelta] = field(default_factory=dict)
    success_indicators: Dict[str, bool] = field(default_factory=dict)
    friction_points: List[str] = field(default_factory=list)
    conversion_funnel: Dict[str, float] = field(default_factory=dict)
    satisfaction_score: Optional[float] = None


@dataclass
class CrossServiceCorrelation:
    """Cross-service metric correlation analysis."""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_a: str = ""
    service_b: str = ""
    metric_a: str = ""
    metric_b: str = ""
    correlation_coefficient: float = 0.0  # -1 to 1
    correlation_strength: str = "weak"  # weak, moderate, strong
    causality_direction: Optional[str] = None  # a_to_b, b_to_a, bidirectional, none
    statistical_significance: float = 0.0  # p-value
    sample_size: int = 0
    analysis_period: timedelta = field(default_factory=lambda: timedelta(days=7))
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EcosystemOptimization:
    """Ecosystem optimization recommendation."""
    optimization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    category: str = ""  # performance, cost, reliability, user_experience
    priority: str = "medium"  # low, medium, high, critical
    affected_services: List[str] = field(default_factory=list)
    expected_impact: Dict[str, float] = field(default_factory=dict)
    implementation_effort: str = "medium"  # low, medium, high
    implementation_timeline: timedelta = field(default_factory=lambda: timedelta(days=14))
    prerequisites: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    confidence_score: float = 0.0  # 0-1
    created_at: datetime = field(default_factory=datetime.utcnow)


class EcosystemMetricsOrchestrator:
    """Master ecosystem metrics orchestration and correlation system."""
    
    def __init__(self):
        """Initialize the ecosystem metrics orchestrator."""
        self.service_metrics: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=10000)))
        self.service_dependencies: Dict[str, ServiceDependency] = {}
        self.ecosystem_health_history: deque = deque(maxlen=1000)
        self.creator_journeys: Dict[str, CreatorJourneyMetrics] = {}
        self.cross_service_correlations: Dict[str, CrossServiceCorrelation] = {}
        self.optimization_recommendations: Dict[str, EcosystemOptimization] = {}
        
        # Service registry and topology
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        self.service_topology: nx.DiGraph = nx.DiGraph()
        self.service_health_cache: Dict[str, Tuple[HealthStatus, datetime]] = {}
        
        # Metrics aggregation and analysis
        self.metric_aggregators: Dict[str, Callable] = {}
        self.correlation_engine_cache: Dict[str, Dict] = {}
        self.anomaly_detection_models: Dict[str, Any] = {}
        
        # Configuration
        self.health_check_interval = timedelta(minutes=5)
        self.correlation_analysis_interval = timedelta(hours=1)
        self.optimization_analysis_interval = timedelta(hours=6)
        self.metric_retention_period = timedelta(days=30)
        
        # Threading and processing
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=16)
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Service thresholds and SLAs
        self.service_slas = {
            "response_time_ms": 500,
            "availability_percentage": 99.9,
            "error_rate_percentage": 1.0,
            "throughput_rps": 1000
        }
        
        # Business domain mappings
        self.business_domains = {
            "creator_onboarding": ["user_management", "content_processing"],
            "content_lifecycle": ["content_processing", "protection", "seo", "distribution"],
            "monetization_flow": ["monetization", "analytics", "collaboration"],
            "creator_growth": ["gamification", "analytics", "notifications"]
        }
        
        logger.info("EcosystemMetricsOrchestrator initialized successfully")
    
    async def start_orchestration(self) -> None:
        """Start the ecosystem metrics orchestration."""
        try:
            # Start background monitoring tasks
            self.background_tasks.add(asyncio.create_task(self._ecosystem_health_monitoring_loop()))
            self.background_tasks.add(asyncio.create_task(self._dependency_monitoring_loop()))
            self.background_tasks.add(asyncio.create_task(self._correlation_analysis_loop()))
            self.background_tasks.add(asyncio.create_task(self._creator_journey_tracking_loop()))
            self.background_tasks.add(asyncio.create_task(self._optimization_analysis_loop()))
            self.background_tasks.add(asyncio.create_task(self._metric_cleanup_loop()))
            
            logger.info("Ecosystem metrics orchestration started successfully")
            
        except Exception as e:
            logger.error(f"Error starting ecosystem orchestration: {e}")
    
    async def register_service(
        self, 
        service_name: str,
        service_type: ServiceType,
        service_config: Dict[str, Any]
    ) -> bool:
        """Register a service in the ecosystem."""
        try:
            with self.lock:
                self.service_registry[service_name] = {
                    "service_type": service_type,
                    "config": service_config,
                    "registered_at": datetime.utcnow(),
                    "last_heartbeat": datetime.utcnow(),
                    "health_status": HealthStatus.HEALTHY,
                    "metrics_enabled": True
                }
                
                # Add to service topology
                self.service_topology.add_node(service_name, **service_config)
                
                # Initialize health cache
                self.service_health_cache[service_name] = (HealthStatus.HEALTHY, datetime.utcnow())
            
            logger.info(f"Registered service: {service_name} ({service_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering service {service_name}: {e}")
            return False
    
    async def record_service_metric(self, metric: ServiceMetric) -> bool:
        """Record a metric from a service."""
        try:
            with self.lock:
                # Validate service is registered
                if metric.service_name not in self.service_registry:
                    logger.warning(f"Metric from unregistered service: {metric.service_name}")
                    return False
                
                # Store metric in time series
                metric_key = f"{metric.metric_name}_{metric.metric_type}"
                self.service_metrics[metric.service_name][metric_key].append(metric)
                
                # Update service heartbeat
                self.service_registry[metric.service_name]["last_heartbeat"] = metric.timestamp
                
                # Trigger real-time analysis if needed
                await self._analyze_metric_anomalies(metric)
                await self._update_service_health(metric.service_name)
            
            logger.debug(f"Recorded metric: {metric.service_name}.{metric.metric_name} = {metric.metric_value}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording service metric: {e}")
            return False
    
    async def define_service_dependency(self, dependency: ServiceDependency) -> bool:
        """Define a dependency relationship between services."""
        try:
            with self.lock:
                # Store dependency
                self.service_dependencies[dependency.dependency_id] = dependency
                
                # Update service topology
                self.service_topology.add_edge(
                    dependency.source_service,
                    dependency.target_service,
                    dependency_type=dependency.dependency_type.value,
                    criticality=dependency.criticality,
                    sla_target=dependency.sla_target
                )
                
                # Initialize dependency health monitoring
                await self._initialize_dependency_monitoring(dependency)
            
            logger.info(f"Defined dependency: {dependency.source_service} -> {dependency.target_service}")
            return True
            
        except Exception as e:
            logger.error(f"Error defining service dependency: {e}")
            return False
    
    async def track_creator_journey(
        self, 
        creator_id: str,
        journey_stage: str,
        services_involved: List[str],
        success_indicators: Dict[str, bool],
        friction_points: Optional[List[str]] = None
    ) -> CreatorJourneyMetrics:
        """Track end-to-end creator journey across services."""
        try:
            journey_key = f"{creator_id}_{journey_stage}"
            
            if journey_key in self.creator_journeys:
                # Update existing journey
                journey = self.creator_journeys[journey_key]
                journey.end_timestamp = datetime.utcnow()
                journey.total_duration = journey.end_timestamp - journey.start_timestamp
                journey.success_indicators.update(success_indicators)
                if friction_points:
                    journey.friction_points.extend(friction_points)
            else:
                # Create new journey tracking
                journey = CreatorJourneyMetrics(
                    creator_id=creator_id,
                    journey_stage=journey_stage,
                    services_involved=services_involved,
                    success_indicators=success_indicators,
                    friction_points=friction_points or []
                )
                self.creator_journeys[journey_key] = journey
            
            # Analyze journey performance
            await self._analyze_journey_performance(journey)
            
            return journey
            
        except Exception as e:
            logger.error(f"Error tracking creator journey: {e}")
            return CreatorJourneyMetrics(creator_id=creator_id, journey_stage=journey_stage)
    
    async def analyze_cross_service_correlations(
        self, 
        service_pairs: Optional[List[Tuple[str, str]]] = None,
        analysis_period: timedelta = timedelta(days=7)
    ) -> List[CrossServiceCorrelation]:
        """Analyze correlations between metrics across services."""
        try:
            correlations = []
            
            # If no specific pairs provided, analyze all registered services
            if not service_pairs:
                services = list(self.service_registry.keys())
                service_pairs = [(s1, s2) for s1 in services for s2 in services if s1 != s2]
            
            for service_a, service_b in service_pairs:
                service_correlations = await self._calculate_service_correlations(
                    service_a, service_b, analysis_period
                )
                correlations.extend(service_correlations)
            
            # Store significant correlations
            for correlation in correlations:
                if abs(correlation.correlation_coefficient) > 0.5:  # Only store significant correlations
                    self.cross_service_correlations[correlation.correlation_id] = correlation
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error analyzing cross-service correlations: {e}")
            return []
    
    async def assess_ecosystem_health(self) -> EcosystemHealth:
        """Perform comprehensive ecosystem health assessment."""
        try:
            # Calculate individual service health scores
            service_health_scores = {}
            for service_name in self.service_registry.keys():
                health_score = await self._calculate_service_health_score(service_name)
                service_health_scores[service_name] = health_score
            
            # Calculate overall ecosystem health
            overall_score = statistics.mean(service_health_scores.values()) if service_health_scores else 0.0
            
            # Identify critical issues
            critical_issues = await self._identify_critical_issues()
            
            # Identify performance bottlenecks
            bottlenecks = await self._identify_performance_bottlenecks()
            
            # Analyze dependency health
            dependency_issues = await self._analyze_dependency_health()
            
            # Generate optimization opportunities
            optimizations = await self._identify_optimization_opportunities()
            
            # Analyze health trends
            health_trends = await self._analyze_health_trends()
            
            health_assessment = EcosystemHealth(
                overall_health_score=overall_score,
                service_health_scores=service_health_scores,
                critical_issues=critical_issues,
                performance_bottlenecks=bottlenecks,
                dependency_issues=dependency_issues,
                optimization_opportunities=optimizations,
                health_trends=health_trends
            )
            
            # Store health assessment
            self.ecosystem_health_history.append(health_assessment)
            
            return health_assessment
            
        except Exception as e:
            logger.error(f"Error assessing ecosystem health: {e}")
            return EcosystemHealth()
    
    async def generate_ecosystem_insights(
        self, 
        analysis_period: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Generate comprehensive ecosystem insights and analytics."""
        try:
            insights = {
                "analysis_period_days": analysis_period.days,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "ecosystem_overview": {},
                "service_performance": {},
                "creator_journey_analytics": {},
                "correlation_insights": {},
                "optimization_recommendations": {},
                "trend_analysis": {},
                "health_summary": {}
            }
            
            # Ecosystem overview
            insights["ecosystem_overview"] = {
                "total_services": len(self.service_registry),
                "active_services": len([s for s, data in self.service_registry.items() 
                                     if (datetime.utcnow() - data["last_heartbeat"]).seconds < 300]),
                "total_dependencies": len(self.service_dependencies),
                "service_types": dict(defaultdict(int)),
                "overall_health_score": (await self.assess_ecosystem_health()).overall_health_score
            }
            
            # Count services by type
            for service_data in self.service_registry.values():
                service_type = service_data["service_type"].value
                insights["ecosystem_overview"]["service_types"][service_type] += 1
            
            # Service performance analysis
            for service_name in self.service_registry.keys():
                performance_data = await self._analyze_service_performance(service_name, analysis_period)
                insights["service_performance"][service_name] = performance_data
            
            # Creator journey analytics
            journey_analytics = await self._analyze_creator_journeys(analysis_period)
            insights["creator_journey_analytics"] = journey_analytics
            
            # Correlation insights
            significant_correlations = [
                corr for corr in self.cross_service_correlations.values()
                if abs(corr.correlation_coefficient) > 0.6
            ]
            insights["correlation_insights"] = {
                "total_correlations": len(self.cross_service_correlations),
                "significant_correlations": len(significant_correlations),
                "strongest_correlations": [
                    {
                        "services": f"{corr.service_a} <-> {corr.service_b}",
                        "metrics": f"{corr.metric_a} <-> {corr.metric_b}",
                        "coefficient": corr.correlation_coefficient,
                        "strength": corr.correlation_strength
                    }
                    for corr in sorted(significant_correlations, 
                                     key=lambda x: abs(x.correlation_coefficient), 
                                     reverse=True)[:5]
                ]
            }
            
            # Optimization recommendations
            active_optimizations = [
                opt for opt in self.optimization_recommendations.values()
                if opt.created_at >= datetime.utcnow() - analysis_period
            ]
            
            insights["optimization_recommendations"] = {
                "total_recommendations": len(active_optimizations),
                "high_priority": len([opt for opt in active_optimizations if opt.priority == "high"]),
                "by_category": dict(defaultdict(int)),
                "top_recommendations": [
                    {
                        "title": opt.title,
                        "category": opt.category,
                        "priority": opt.priority,
                        "affected_services": opt.affected_services,
                        "expected_impact": opt.expected_impact
                    }
                    for opt in sorted(active_optimizations, 
                                    key=lambda x: x.confidence_score, 
                                    reverse=True)[:3]
                ]
            }
            
            # Count recommendations by category
            for opt in active_optimizations:
                insights["optimization_recommendations"]["by_category"][opt.category] += 1
            
            # Trend analysis
            insights["trend_analysis"] = await self._analyze_ecosystem_trends(analysis_period)
            
            # Health summary
            latest_health = self.ecosystem_health_history[-1] if self.ecosystem_health_history else None
            if latest_health:
                insights["health_summary"] = {
                    "overall_score": latest_health.overall_health_score,
                    "critical_issues_count": len(latest_health.critical_issues),
                    "performance_bottlenecks_count": len(latest_health.performance_bottlenecks),
                    "health_status": await self._determine_ecosystem_health_status(latest_health.overall_health_score)
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating ecosystem insights: {e}")
            return {"error": str(e)}
    
    async def get_master_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for the master ecosystem dashboard."""
        try:
            current_time = datetime.utcnow()
            
            # Real-time service status
            service_status = {}
            for service_name, service_data in self.service_registry.items():
                last_heartbeat = service_data["last_heartbeat"]
                is_healthy = (current_time - last_heartbeat).seconds < 300  # 5 minutes
                
                service_status[service_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_heartbeat": last_heartbeat.isoformat(),
                    "service_type": service_data["service_type"].value,
                    "health_score": await self._calculate_service_health_score(service_name)
                }
            
            # Dependency graph data
            dependency_graph = {
                "nodes": [
                    {"id": service, "type": data["service_type"].value}
                    for service, data in self.service_registry.items()
                ],
                "edges": [
                    {
                        "source": dep.source_service,
                        "target": dep.target_service,
                        "type": dep.dependency_type.value,
                        "health": dep.health_status.value,
                        "criticality": dep.criticality
                    }
                    for dep in self.service_dependencies.values()
                ]
            }
            
            # Key metrics summary
            key_metrics = await self._calculate_key_ecosystem_metrics()
            
            # Recent alerts and issues
            recent_issues = await self._get_recent_issues(timedelta(hours=24))
            
            # Creator journey summary
            journey_summary = await self._get_creator_journey_summary()
            
            # Performance trends
            performance_trends = await self._get_performance_trends(timedelta(hours=24))
            
            return {
                "timestamp": current_time.isoformat(),
                "service_status": service_status,
                "dependency_graph": dependency_graph,
                "key_metrics": key_metrics,
                "recent_issues": recent_issues,
                "creator_journey_summary": journey_summary,
                "performance_trends": performance_trends,
                "ecosystem_health": (await self.assess_ecosystem_health()).overall_health_score
            }
            
        except Exception as e:
            logger.error(f"Error getting master dashboard data: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _ecosystem_health_monitoring_loop(self):
        """Background loop for ecosystem health monitoring."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval.total_seconds())
                
                # Perform health assessment
                health_assessment = await self.assess_ecosystem_health()
                
                # Check for critical issues requiring immediate attention
                if health_assessment.overall_health_score < 50:
                    logger.critical(f"Ecosystem health critical: {health_assessment.overall_health_score:.1f}%")
                    await self._handle_critical_health_issues(health_assessment)
                
            except Exception as e:
                logger.error(f"Error in ecosystem health monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _dependency_monitoring_loop(self):
        """Background loop for dependency health monitoring."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                for dependency in self.service_dependencies.values():
                    await self._check_dependency_health(dependency)
                
            except Exception as e:
                logger.error(f"Error in dependency monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _correlation_analysis_loop(self):
        """Background loop for correlation analysis."""
        while True:
            try:
                await asyncio.sleep(self.correlation_analysis_interval.total_seconds())
                
                # Perform cross-service correlation analysis
                await self.analyze_cross_service_correlations()
                
            except Exception as e:
                logger.error(f"Error in correlation analysis loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    async def _creator_journey_tracking_loop(self):
        """Background loop for creator journey analysis."""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Analyze active creator journeys
                await self._analyze_active_journeys()
                
                # Clean up completed journeys
                await self._cleanup_completed_journeys()
                
            except Exception as e:
                logger.error(f"Error in creator journey tracking loop: {e}")
                await asyncio.sleep(300)
    
    async def _optimization_analysis_loop(self):
        """Background loop for optimization analysis."""
        while True:
            try:
                await asyncio.sleep(self.optimization_analysis_interval.total_seconds())
                
                # Generate optimization recommendations
                await self._generate_optimization_recommendations()
                
            except Exception as e:
                logger.error(f"Error in optimization analysis loop: {e}")
                await asyncio.sleep(21600)  # Wait 6 hours before retrying
    
    async def _metric_cleanup_loop(self):
        """Background loop for metric cleanup."""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Clean up old metrics
                await self._cleanup_old_metrics()
                
            except Exception as e:
                logger.error(f"Error in metric cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _calculate_service_health_score(self, service_name: str) -> float:
        """Calculate health score for a specific service."""
        try:
            if service_name not in self.service_registry:
                return 0.0
            
            health_components = []
            
            # Availability component
            last_heartbeat = self.service_registry[service_name]["last_heartbeat"]
            heartbeat_age = (datetime.utcnow() - last_heartbeat).total_seconds()
            availability_score = max(0, 100 - (heartbeat_age / 60))  # Degrade over 1 minute
            health_components.append(availability_score)
            
            # Performance component
            performance_metrics = self.service_metrics.get(service_name, {})
            if "response_time_gauge" in performance_metrics:
                recent_response_times = list(performance_metrics["response_time_gauge"])[-10:]
                if recent_response_times:
                    avg_response_time = statistics.mean([m.metric_value for m in recent_response_times])
                    performance_score = max(0, 100 - (avg_response_time / 10))  # Degrade after 1000ms
                    health_components.append(performance_score)
            
            # Error rate component
            if "error_rate_gauge" in performance_metrics:
                recent_error_rates = list(performance_metrics["error_rate_gauge"])[-10:]
                if recent_error_rates:
                    avg_error_rate = statistics.mean([m.metric_value for m in recent_error_rates])
                    error_score = max(0, 100 - (avg_error_rate * 10))  # Degrade with error rate
                    health_components.append(error_score)
            
            # Calculate weighted average
            return statistics.mean(health_components) if health_components else 50.0
            
        except Exception as e:
            logger.error(f"Error calculating health score for {service_name}: {e}")
            return 0.0
    
    async def _calculate_service_correlations(
        self, 
        service_a: str, 
        service_b: str, 
        analysis_period: timedelta
    ) -> List[CrossServiceCorrelation]:
        """Calculate correlations between two services."""
        correlations = []
        
        try:
            metrics_a = self.service_metrics.get(service_a, {})
            metrics_b = self.service_metrics.get(service_b, {})
            
            # Get metric names from both services
            for metric_name_a in metrics_a.keys():
                for metric_name_b in metrics_b.keys():
                    correlation = await self._calculate_metric_correlation(
                        service_a, metric_name_a, service_b, metric_name_b, analysis_period
                    )
                    
                    if correlation and abs(correlation.correlation_coefficient) > 0.3:
                        correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating correlations between {service_a} and {service_b}: {e}")
            return []
    
    async def _calculate_metric_correlation(
        self, 
        service_a: str, 
        metric_a: str, 
        service_b: str, 
        metric_b: str,
        analysis_period: timedelta
    ) -> Optional[CrossServiceCorrelation]:
        """Calculate correlation between two specific metrics."""
        try:
            cutoff_time = datetime.utcnow() - analysis_period
            
            # Get metric data
            metrics_a_data = [
                m for m in self.service_metrics[service_a][metric_a]
                if m.timestamp >= cutoff_time and isinstance(m.metric_value, (int, float))
            ]
            
            metrics_b_data = [
                m for m in self.service_metrics[service_b][metric_b]
                if m.timestamp >= cutoff_time and isinstance(m.metric_value, (int, float))
            ]
            
            if len(metrics_a_data) < 10 or len(metrics_b_data) < 10:
                return None  # Insufficient data
            
            # Align metrics by timestamp (simplified)
            values_a = [m.metric_value for m in metrics_a_data]
            values_b = [m.metric_value for m in metrics_b_data]
            
            # Take minimum length for correlation
            min_length = min(len(values_a), len(values_b))
            values_a = values_a[:min_length]
            values_b = values_b[:min_length]
            
            # Calculate correlation coefficient
            correlation_matrix = np.corrcoef(values_a, values_b)
            correlation_coefficient = correlation_matrix[0, 1] if not np.isnan(correlation_matrix[0, 1]) else 0.0
            
            # Determine correlation strength
            abs_corr = abs(correlation_coefficient)
            if abs_corr < 0.3:
                strength = "weak"
            elif abs_corr < 0.7:
                strength = "moderate"
            else:
                strength = "strong"
            
            return CrossServiceCorrelation(
                service_a=service_a,
                service_b=service_b,
                metric_a=metric_a,
                metric_b=metric_b,
                correlation_coefficient=correlation_coefficient,
                correlation_strength=strength,
                sample_size=min_length,
                analysis_period=analysis_period
            )
            
        except Exception as e:
            logger.error(f"Error calculating metric correlation: {e}")
            return None
    
    async def _analyze_journey_performance(self, journey: CreatorJourneyMetrics):
        """Analyze creator journey performance."""
        try:
            # Calculate conversion funnel
            funnel_stages = ["start", "engagement", "conversion", "completion"]
            for i, stage in enumerate(funnel_stages):
                # Simplified funnel calculation
                conversion_rate = max(0, 100 - (i * 20))  # Mock decreasing conversion
                journey.conversion_funnel[stage] = conversion_rate
            
            # Identify friction points based on service performance
            for service in journey.services_involved:
                service_health = await self._calculate_service_health_score(service)
                if service_health < 70:
                    journey.friction_points.append(f"Poor performance in {service}")
            
            # Calculate satisfaction score based on success indicators and friction
            success_rate = sum(journey.success_indicators.values()) / max(len(journey.success_indicators), 1)
            friction_penalty = len(journey.friction_points) * 0.1
            journey.satisfaction_score = max(0, (success_rate * 100) - (friction_penalty * 100))
            
        except Exception as e:
            logger.error(f"Error analyzing journey performance: {e}")
    
    async def _identify_critical_issues(self) -> List[str]:
        """Identify critical issues in the ecosystem."""
        issues = []
        
        try:
            # Check for unhealthy services
            for service_name, service_data in self.service_registry.items():
                last_heartbeat = service_data["last_heartbeat"]
                if (datetime.utcnow() - last_heartbeat).seconds > 600:  # 10 minutes
                    issues.append(f"Service {service_name} appears to be down")
            
            # Check for failing dependencies
            for dependency in self.service_dependencies.values():
                if dependency.health_status in [HealthStatus.CRITICAL, HealthStatus.DOWN]:
                    issues.append(f"Critical dependency failure: {dependency.source_service} -> {dependency.target_service}")
            
            # Check for performance degradation
            for service_name in self.service_registry.keys():
                health_score = await self._calculate_service_health_score(service_name)
                if health_score < 30:
                    issues.append(f"Service {service_name} performance critically degraded")
            
            return issues
            
        except Exception as e:
            logger.error(f"Error identifying critical issues: {e}")
            return []
    
    async def _identify_performance_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks in the ecosystem."""
        bottlenecks = []
        
        try:
            # Analyze response times across services
            for service_name, metrics in self.service_metrics.items():
                if "response_time_gauge" in metrics:
                    recent_metrics = list(metrics["response_time_gauge"])[-20:]
                    if recent_metrics:
                        avg_response_time = statistics.mean([m.metric_value for m in recent_metrics])
                        if avg_response_time > 2000:  # 2 seconds
                            bottlenecks.append(f"High response time in {service_name}: {avg_response_time:.0f}ms")
            
            # Analyze dependency chains
            for dependency in self.service_dependencies.values():
                if dependency.current_latency and dependency.current_latency > 1000:
                    bottlenecks.append(f"High latency dependency: {dependency.source_service} -> {dependency.target_service}")
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Error identifying performance bottlenecks: {e}")
            return []
    
    async def _generate_optimization_recommendations(self):
        """Generate ecosystem optimization recommendations."""
        try:
            # Performance optimizations
            await self._generate_performance_optimizations()
            
            # Resource utilization optimizations
            await self._generate_resource_optimizations()
            
            # Dependency optimizations
            await self._generate_dependency_optimizations()
            
            # Creator journey optimizations
            await self._generate_journey_optimizations()
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
    
    async def _generate_performance_optimizations(self):
        """Generate performance-related optimization recommendations."""
        for service_name, metrics in self.service_metrics.items():
            if "response_time_gauge" in metrics:
                recent_metrics = list(metrics["response_time_gauge"])[-50:]
                if recent_metrics:
                    avg_response_time = statistics.mean([m.metric_value for m in recent_metrics])
                    
                    if avg_response_time > 1000:  # 1 second
                        optimization = EcosystemOptimization(
                            title=f"Optimize Response Time for {service_name}",
                            description=f"Average response time is {avg_response_time:.0f}ms, exceeding target of 500ms",
                            category="performance",
                            priority="high" if avg_response_time > 2000 else "medium",
                            affected_services=[service_name],
                            expected_impact={"response_time_improvement": 30.0, "user_satisfaction": 15.0},
                            implementation_effort="medium",
                            implementation_timeline=timedelta(days=10),
                            success_metrics=[f"{service_name}_response_time", f"{service_name}_user_satisfaction"],
                            confidence_score=0.8
                        )
                        
                        self.optimization_recommendations[optimization.optimization_id] = optimization
    
    async def _calculate_key_ecosystem_metrics(self) -> Dict[str, Any]:
        """Calculate key metrics for the ecosystem."""
        try:
            active_services = len([
                s for s, data in self.service_registry.items()
                if (datetime.utcnow() - data["last_heartbeat"]).seconds < 300
            ])
            
            # Calculate average response time across all services
            all_response_times = []
            for service_metrics in self.service_metrics.values():
                if "response_time_gauge" in service_metrics:
                    recent_times = [m.metric_value for m in list(service_metrics["response_time_gauge"])[-10:]]
                    all_response_times.extend(recent_times)
            
            avg_response_time = statistics.mean(all_response_times) if all_response_times else 0.0
            
            # Calculate error rates
            all_error_rates = []
            for service_metrics in self.service_metrics.values():
                if "error_rate_gauge" in service_metrics:
                    recent_errors = [m.metric_value for m in list(service_metrics["error_rate_gauge"])[-10:]]
                    all_error_rates.extend(recent_errors)
            
            avg_error_rate = statistics.mean(all_error_rates) if all_error_rates else 0.0
            
            # Calculate throughput
            total_throughput = 0
            for service_metrics in self.service_metrics.values():
                if "throughput_gauge" in service_metrics:
                    recent_throughput = list(service_metrics["throughput_gauge"])[-1:]
                    if recent_throughput:
                        total_throughput += recent_throughput[0].metric_value
            
            return {
                "active_services": active_services,
                "total_services": len(self.service_registry),
                "average_response_time_ms": round(avg_response_time, 2),
                "average_error_rate_percent": round(avg_error_rate, 2),
                "total_throughput_rps": round(total_throughput, 2),
                "healthy_dependencies": len([
                    d for d in self.service_dependencies.values()
                    if d.health_status == HealthStatus.HEALTHY
                ]),
                "total_dependencies": len(self.service_dependencies)
            }
            
        except Exception as e:
            logger.error(f"Error calculating key ecosystem metrics: {e}")
            return {}


# Export the main class
__all__ = [
    "EcosystemMetricsOrchestrator", 
    "ServiceMetric", 
    "ServiceDependency", 
    "EcosystemHealth",
    "CreatorJourneyMetrics",
    "CrossServiceCorrelation",
    "EcosystemOptimization"
]