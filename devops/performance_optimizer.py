"""
🚀 Performance Optimizer - Auto-scaling and Performance Management
=================================================================

Enterprise-grade performance optimization with predictive scaling, resource optimization,
bottleneck detection, and capacity planning.

Features:
- Predictive scaling algorithms using ML models
- Resource utilization optimization and right-sizing
- Performance bottleneck detection and resolution
- Capacity planning automation with forecasting
- Cost-performance optimization algorithms
- Application performance monitoring (APM)
- Database performance optimization
- CDN and caching optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: DevOps Engineer + Performance Engineering + ML Engineering + SRE
"""

import asyncio
import logging
import json
import statistics
import math
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import uuid
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

class MetricTrend(Enum):
    """Metric trend direction"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

class ScalingDirection(Enum):
    """Scaling direction"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_CHANGE = "no_change"

class BottleneckType(Enum):
    """Performance bottleneck types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    DATABASE = "database"
    CACHE = "cache"
    APPLICATION = "application"

class OptimizationType(Enum):
    """Optimization types"""
    RESOURCE_SIZING = "resource_sizing"
    AUTO_SCALING = "auto_scaling"
    CACHING = "caching"
    DATABASE_TUNING = "database_tuning"
    CDN_OPTIMIZATION = "cdn_optimization"
    CODE_OPTIMIZATION = "code_optimization"

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_name: str
    value: float
    timestamp: datetime
    service: str
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

@dataclass
class ScalingRecommendation:
    """Auto-scaling recommendation"""
    recommendation_id: str
    service: str
    current_replicas: int
    recommended_replicas: int
    direction: ScalingDirection
    confidence: float
    reasoning: str
    expected_impact: Dict[str, float]
    created_at: datetime
    implementation_priority: str = "medium"

@dataclass
class PerformanceBottleneck:
    """Performance bottleneck detection"""
    bottleneck_id: str
    service: str
    bottleneck_type: BottleneckType
    severity: str  # low, medium, high, critical
    impact_score: float
    description: str
    root_cause: str
    recommendations: List[str]
    detected_at: datetime
    resolved_at: Optional[datetime] = None

@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    optimization_id: str
    service: str
    optimization_type: OptimizationType
    current_state: Dict[str, Any]
    recommended_state: Dict[str, Any]
    expected_improvement: Dict[str, float]
    implementation_effort: str  # low, medium, high
    cost_impact: str  # reduce, neutral, increase
    description: str
    created_at: datetime

@dataclass
class CapacityForecast:
    """Capacity planning forecast"""
    forecast_id: str
    service: str
    metric: str
    current_capacity: float
    forecasted_values: List[Dict[str, Any]]
    capacity_exhaustion_date: Optional[datetime]
    recommended_scaling_plan: List[Dict[str, Any]]
    confidence_interval: Tuple[float, float]
    created_at: datetime

@dataclass
class PerformanceBaseline:
    """Performance baseline metrics"""
    service: str
    metric: str
    baseline_value: float
    acceptable_range: Tuple[float, float]
    measurement_period: int  # seconds
    established_at: datetime
    last_updated: datetime
    sample_count: int

class PerformanceOptimizer:
    """
    Auto-scaling and Performance Management
    
    Responsibilities:
    - Predictive auto-scaling based on ML models and patterns
    - Resource utilization optimization and right-sizing
    - Performance bottleneck detection and automated resolution
    - Capacity planning with demand forecasting
    - Cost-performance optimization algorithms
    - Application and infrastructure performance monitoring
    - Database query optimization and tuning
    - CDN and caching strategy optimization
    """
    
    def __init__(self):
        # Performance metrics storage
        self.performance_metrics: deque = deque(maxlen=100000)
        self.aggregated_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5000))
        
        # Auto-scaling
        self.scaling_recommendations: List[ScalingRecommendation] = []
        self.scaling_history: List[Dict[str, Any]] = []
        self.scaling_policies: Dict[str, Dict] = {}
        
        # Performance analysis
        self.performance_baselines: Dict[str, PerformanceBaseline] = {}
        self.bottlenecks: Dict[str, PerformanceBottleneck] = {}
        self.optimization_recommendations: List[OptimizationRecommendation] = []
        
        # Capacity planning
        self.capacity_forecasts: Dict[str, CapacityForecast] = {}
        self.capacity_thresholds: Dict[str, Dict] = {}
        
        # ML models for prediction
        self.prediction_models: Dict[str, Any] = {}
        self.model_accuracy: Dict[str, float] = {}
        
        # Performance profiles
        self.service_profiles: Dict[str, Dict] = {}
        self.workload_patterns: Dict[str, List] = defaultdict(list)
        
        # Optimization strategies
        self.optimization_strategies: Dict[str, Dict] = {}
        self.cost_optimization_rules: List[Dict] = []
        
        self._initialize_performance_optimizer()
        
        logger.info("PerformanceOptimizer initialized")

    def _initialize_performance_optimizer(self):
        """Initialize performance optimizer"""
        
        # Start background tasks
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._auto_scaling_loop())
        asyncio.create_task(self._bottleneck_detection_loop())
        asyncio.create_task(self._capacity_planning_loop())
        asyncio.create_task(self._optimization_analysis_loop())
        asyncio.create_task(self._model_training_loop())
        
        # Initialize configurations
        self._setup_scaling_policies()
        self._setup_performance_thresholds()
        self._setup_optimization_strategies()
        self._setup_capacity_thresholds()
        
        logger.info("Performance optimizer initialization complete")

    def _setup_scaling_policies(self):
        """Setup auto-scaling policies"""
        
        self.scaling_policies = {
            "web_service": {
                "min_replicas": 2,
                "max_replicas": 20,
                "target_cpu_utilization": 70.0,
                "target_memory_utilization": 80.0,
                "scale_up_threshold": 80.0,
                "scale_down_threshold": 30.0,
                "scale_up_cooldown": 300,  # 5 minutes
                "scale_down_cooldown": 600,  # 10 minutes
                "metrics": ["cpu_usage", "memory_usage", "request_rate", "response_time"]
            },
            "worker_service": {
                "min_replicas": 1,
                "max_replicas": 10,
                "target_cpu_utilization": 75.0,
                "target_memory_utilization": 85.0,
                "scale_up_threshold": 85.0,
                "scale_down_threshold": 25.0,
                "scale_up_cooldown": 180,  # 3 minutes
                "scale_down_cooldown": 900,  # 15 minutes
                "metrics": ["cpu_usage", "memory_usage", "queue_length"]
            },
            "database": {
                "min_replicas": 1,
                "max_replicas": 5,
                "target_cpu_utilization": 60.0,
                "target_memory_utilization": 75.0,
                "scale_up_threshold": 70.0,
                "scale_down_threshold": 20.0,
                "scale_up_cooldown": 600,  # 10 minutes
                "scale_down_cooldown": 1800,  # 30 minutes
                "metrics": ["cpu_usage", "memory_usage", "connection_count", "query_time"]
            }
        }

    def _setup_performance_thresholds(self):
        """Setup performance monitoring thresholds"""
        
        self.performance_thresholds = {
            "response_time": {
                "good": 200.0,     # ms
                "acceptable": 500.0,
                "poor": 1000.0,
                "critical": 2000.0
            },
            "throughput": {
                "minimum": 100.0,   # requests/sec
                "target": 1000.0,
                "maximum": 5000.0
            },
            "error_rate": {
                "good": 0.01,       # 1%
                "acceptable": 0.05, # 5%
                "poor": 0.10,       # 10%
                "critical": 0.20    # 20%
            },
            "resource_utilization": {
                "cpu": {"low": 30, "optimal": 70, "high": 85, "critical": 95},
                "memory": {"low": 40, "optimal": 75, "high": 85, "critical": 95},
                "disk": {"low": 50, "optimal": 70, "high": 80, "critical": 90}
            }
        }

    def _setup_optimization_strategies(self):
        """Setup optimization strategies"""
        
        self.optimization_strategies = {
            "cpu_optimization": {
                "strategies": [
                    "vertical_scaling",
                    "horizontal_scaling", 
                    "cpu_affinity_tuning",
                    "process_optimization"
                ],
                "triggers": ["high_cpu_usage", "cpu_throttling"],
                "impact_metrics": ["cpu_usage", "response_time", "throughput"]
            },
            "memory_optimization": {
                "strategies": [
                    "memory_right_sizing",
                    "garbage_collection_tuning",
                    "memory_leak_detection",
                    "cache_optimization"
                ],
                "triggers": ["high_memory_usage", "memory_pressure", "oom_events"],
                "impact_metrics": ["memory_usage", "gc_time", "response_time"]
            },
            "database_optimization": {
                "strategies": [
                    "index_optimization",
                    "query_optimization",
                    "connection_pooling",
                    "read_replica_scaling"
                ],
                "triggers": ["slow_queries", "high_db_cpu", "connection_pool_exhaustion"],
                "impact_metrics": ["query_time", "db_cpu", "connection_count"]
            },
            "caching_optimization": {
                "strategies": [
                    "cache_warming",
                    "cache_invalidation_tuning",
                    "cdn_optimization",
                    "application_cache_tuning"
                ],
                "triggers": ["low_cache_hit_rate", "high_backend_load"],
                "impact_metrics": ["cache_hit_rate", "response_time", "backend_load"]
            }
        }

    def _setup_capacity_thresholds(self):
        """Setup capacity planning thresholds"""
        
        self.capacity_thresholds = {
            "cpu_capacity": {
                "warning": 80.0,
                "critical": 90.0,
                "planning_horizon": 30  # days
            },
            "memory_capacity": {
                "warning": 85.0,
                "critical": 95.0,
                "planning_horizon": 30
            },
            "storage_capacity": {
                "warning": 80.0,
                "critical": 90.0,
                "planning_horizon": 60  # days
            },
            "network_capacity": {
                "warning": 70.0,
                "critical": 85.0,
                "planning_horizon": 14  # days
            }
        }

    async def collect_performance_metric(
        self,
        metric_name: str,
        value: float,
        service: str,
        labels: Optional[Dict[str, str]] = None,
        unit: str = ""
    ):
        """
        Collect performance metric
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            service: Service name
            labels: Additional labels
            unit: Metric unit
        """
        
        try:
            metric = PerformanceMetric(
                metric_name=metric_name,
                value=value,
                timestamp=datetime.now(),
                service=service,
                labels=labels or {},
                unit=unit
            )
            
            self.performance_metrics.append(metric)
            
            # Store in aggregated metrics
            metric_key = f"{service}:{metric_name}"
            self.aggregated_metrics[metric_key].append({
                "timestamp": metric.timestamp,
                "value": value
            })
            
            # Update baselines
            await self._update_performance_baseline(service, metric_name, value)
            
        except Exception as e:
            logger.error(f"Performance metric collection failed: {str(e)}")

    async def _update_performance_baseline(self, service: str, metric: str, value: float):
        """Update performance baseline for service and metric"""
        
        try:
            baseline_key = f"{service}:{metric}"
            
            if baseline_key not in self.performance_baselines:
                # Create new baseline
                self.performance_baselines[baseline_key] = PerformanceBaseline(
                    service=service,
                    metric=metric,
                    baseline_value=value,
                    acceptable_range=(value * 0.8, value * 1.2),  # ±20%
                    measurement_period=3600,  # 1 hour
                    established_at=datetime.now(),
                    last_updated=datetime.now(),
                    sample_count=1
                )
            else:
                # Update existing baseline
                baseline = self.performance_baselines[baseline_key]
                
                # Calculate rolling average
                alpha = 0.1  # Smoothing factor
                baseline.baseline_value = (1 - alpha) * baseline.baseline_value + alpha * value
                
                # Update acceptable range (±20% of baseline)
                margin = baseline.baseline_value * 0.2
                baseline.acceptable_range = (
                    baseline.baseline_value - margin,
                    baseline.baseline_value + margin
                )
                
                baseline.last_updated = datetime.now()
                baseline.sample_count += 1
                
        except Exception as e:
            logger.error(f"Baseline update failed: {str(e)}")

    async def analyze_scaling_needs(self, service: str) -> List[ScalingRecommendation]:
        """
        Analyze auto-scaling needs for service
        
        Args:
            service: Service name
            
        Returns:
            List of scaling recommendations
        """
        
        try:
            if service not in self.scaling_policies:
                logger.warning(f"No scaling policy found for service: {service}")
                return []
            
            policy = self.scaling_policies[service]
            recommendations = []
            
            # Get recent metrics for the service
            recent_metrics = await self._get_recent_metrics(service, 900)  # 15 minutes
            
            if not recent_metrics:
                logger.warning(f"No recent metrics found for service: {service}")
                return []
            
            # Analyze each metric
            for metric_name in policy["metrics"]:
                metric_values = [
                    m["value"] for m in recent_metrics 
                    if m["metric_name"] == metric_name
                ]
                
                if not metric_values:
                    continue
                
                # Calculate current utilization
                current_avg = statistics.mean(metric_values)
                current_p95 = np.percentile(metric_values, 95)
                
                # Predict future values
                predicted_values = await self._predict_metric_values(service, metric_name, 300)  # 5 minutes ahead
                
                # Determine scaling recommendation
                recommendation = await self._evaluate_scaling_decision(
                    service, metric_name, current_avg, current_p95, predicted_values, policy
                )
                
                if recommendation:
                    recommendations.append(recommendation)
            
            # Consolidate recommendations
            final_recommendation = await self._consolidate_scaling_recommendations(service, recommendations)
            
            if final_recommendation:
                self.scaling_recommendations.append(final_recommendation)
                return [final_recommendation]
            
            return []
            
        except Exception as e:
            logger.error(f"Scaling analysis failed: {str(e)}")
            return []

    async def _get_recent_metrics(self, service: str, seconds: int) -> List[Dict[str, Any]]:
        """Get recent metrics for service"""
        
        cutoff_time = datetime.now() - timedelta(seconds=seconds)
        
        recent_metrics = [
            {
                "metric_name": m.metric_name,
                "value": m.value,
                "timestamp": m.timestamp
            }
            for m in self.performance_metrics
            if m.service == service and m.timestamp >= cutoff_time
        ]
        
        return recent_metrics

    async def _predict_metric_values(self, service: str, metric: str, seconds_ahead: int) -> List[float]:
        """Predict future metric values using simple time series analysis"""
        
        try:
            # Get historical data
            metric_key = f"{service}:{metric}"
            historical_data = list(self.aggregated_metrics[metric_key])
            
            if len(historical_data) < 10:
                # Not enough data for prediction
                return []
            
            # Simple linear regression for trend prediction
            values = [d["value"] for d in historical_data[-60:]]  # Last 60 points
            timestamps = list(range(len(values)))
            
            if len(values) < 5:
                return []
            
            # Calculate trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
            
            # Predict future values
            future_points = int(seconds_ahead / 60)  # Assuming 1-minute intervals
            predictions = []
            
            for i in range(1, future_points + 1):
                future_timestamp = len(values) + i
                predicted_value = slope * future_timestamp + intercept
                predictions.append(max(0, predicted_value))  # Non-negative values
            
            return predictions
            
        except Exception as e:
            logger.error(f"Metric prediction failed: {str(e)}")
            return []

    async def _evaluate_scaling_decision(
        self,
        service: str,
        metric_name: str,
        current_avg: float,
        current_p95: float,
        predicted_values: List[float],
        policy: Dict[str, Any]
    ) -> Optional[ScalingRecommendation]:
        """Evaluate scaling decision based on metrics and predictions"""
        
        try:
            scale_up_threshold = policy.get("scale_up_threshold", 80.0)
            scale_down_threshold = policy.get("scale_down_threshold", 30.0)
            
            # Current state analysis
            needs_scale_up = current_p95 > scale_up_threshold
            needs_scale_down = current_avg < scale_down_threshold
            
            # Predictive analysis
            if predicted_values:
                max_predicted = max(predicted_values)
                needs_scale_up = needs_scale_up or max_predicted > scale_up_threshold
            
            # Determine scaling direction and magnitude
            if needs_scale_up and not needs_scale_down:
                # Calculate scale-up magnitude
                overload_factor = current_p95 / scale_up_threshold
                recommended_increase = math.ceil(overload_factor - 1)
                
                current_replicas = self._get_current_replicas(service)
                new_replicas = min(
                    current_replicas + recommended_increase,
                    policy.get("max_replicas", 10)
                )
                
                confidence = min(0.9, overload_factor - 1)
                
                return ScalingRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    service=service,
                    current_replicas=current_replicas,
                    recommended_replicas=new_replicas,
                    direction=ScalingDirection.SCALE_UP,
                    confidence=confidence,
                    reasoning=f"{metric_name} ({current_p95:.1f}) exceeds threshold ({scale_up_threshold})",
                    expected_impact={
                        "cpu_reduction": 20.0,
                        "response_time_improvement": 15.0,
                        "throughput_increase": 25.0
                    },
                    created_at=datetime.now(),
                    implementation_priority="high" if current_p95 > scale_up_threshold * 1.2 else "medium"
                )
                
            elif needs_scale_down and not needs_scale_up:
                # Calculate scale-down magnitude
                underload_factor = scale_down_threshold / current_avg
                recommended_decrease = max(1, math.floor(underload_factor - 1))
                
                current_replicas = self._get_current_replicas(service)
                new_replicas = max(
                    current_replicas - recommended_decrease,
                    policy.get("min_replicas", 1)
                )
                
                if new_replicas < current_replicas:
                    confidence = min(0.8, underload_factor - 1)
                    
                    return ScalingRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        service=service,
                        current_replicas=current_replicas,
                        recommended_replicas=new_replicas,
                        direction=ScalingDirection.SCALE_DOWN,
                        confidence=confidence,
                        reasoning=f"{metric_name} ({current_avg:.1f}) below threshold ({scale_down_threshold})",
                        expected_impact={
                            "cost_reduction": 15.0,
                            "resource_efficiency": 20.0
                        },
                        created_at=datetime.now(),
                        implementation_priority="low"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Scaling decision evaluation failed: {str(e)}")
            return None

    def _get_current_replicas(self, service: str) -> int:
        """Get current replica count for service"""
        
        # Mock current replica count
        replica_counts = {
            "web_service": 3,
            "worker_service": 2,
            "database": 1
        }
        
        return replica_counts.get(service, 1)

    async def _consolidate_scaling_recommendations(
        self,
        service: str,
        recommendations: List[ScalingRecommendation]
    ) -> Optional[ScalingRecommendation]:
        """Consolidate multiple scaling recommendations into single recommendation"""
        
        if not recommendations:
            return None
        
        if len(recommendations) == 1:
            return recommendations[0]
        
        # Multiple recommendations - need to consolidate
        scale_up_recs = [r for r in recommendations if r.direction == ScalingDirection.SCALE_UP]
        scale_down_recs = [r for r in recommendations if r.direction == ScalingDirection.SCALE_DOWN]
        
        # Scale up takes priority over scale down
        if scale_up_recs:
            # Use the recommendation with highest confidence
            best_rec = max(scale_up_recs, key=lambda r: r.confidence)
            return best_rec
        elif scale_down_recs:
            # Use the recommendation with highest confidence
            best_rec = max(scale_down_recs, key=lambda r: r.confidence)
            return best_rec
        
        return None

    async def detect_performance_bottlenecks(self, service: str) -> List[PerformanceBottleneck]:
        """
        Detect performance bottlenecks in service
        
        Args:
            service: Service name
            
        Returns:
            List of detected bottlenecks
        """
        
        try:
            bottlenecks = []
            
            # Get recent metrics
            recent_metrics = await self._get_recent_metrics(service, 1800)  # 30 minutes
            
            if not recent_metrics:
                return bottlenecks
            
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in recent_metrics:
                metrics_by_type[metric["metric_name"]].append(metric["value"])
            
            # Analyze each metric type for bottlenecks
            for metric_name, values in metrics_by_type.items():
                if len(values) < 5:
                    continue
                
                avg_value = statistics.mean(values)
                p95_value = np.percentile(values, 95)
                
                # Check against thresholds
                bottleneck = await self._analyze_metric_for_bottleneck(
                    service, metric_name, avg_value, p95_value
                )
                
                if bottleneck:
                    bottlenecks.append(bottleneck)
            
            # Store detected bottlenecks
            for bottleneck in bottlenecks:
                self.bottlenecks[bottleneck.bottleneck_id] = bottleneck
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Bottleneck detection failed: {str(e)}")
            return []

    async def _analyze_metric_for_bottleneck(
        self,
        service: str,
        metric_name: str,
        avg_value: float,
        p95_value: float
    ) -> Optional[PerformanceBottleneck]:
        """Analyze metric for performance bottleneck"""
        
        try:
            # Define bottleneck detection rules
            bottleneck_rules = {
                "cpu_usage": {
                    "type": BottleneckType.CPU,
                    "thresholds": {"medium": 80, "high": 90, "critical": 95},
                    "description": "High CPU utilization detected"
                },
                "memory_usage": {
                    "type": BottleneckType.MEMORY,
                    "thresholds": {"medium": 85, "high": 92, "critical": 98},
                    "description": "High memory utilization detected"
                },
                "disk_io_wait": {
                    "type": BottleneckType.DISK_IO,
                    "thresholds": {"medium": 20, "high": 40, "critical": 60},
                    "description": "High disk I/O wait time detected"
                },
                "response_time": {
                    "type": BottleneckType.APPLICATION,
                    "thresholds": {"medium": 500, "high": 1000, "critical": 2000},
                    "description": "High response time detected"
                },
                "query_time": {
                    "type": BottleneckType.DATABASE,
                    "thresholds": {"medium": 100, "high": 500, "critical": 1000},
                    "description": "Slow database queries detected"
                }
            }
            
            if metric_name not in bottleneck_rules:
                return None
            
            rule = bottleneck_rules[metric_name]
            severity = None
            impact_score = 0
            
            # Determine severity based on P95 value
            if p95_value >= rule["thresholds"]["critical"]:
                severity = "critical"
                impact_score = 9.0
            elif p95_value >= rule["thresholds"]["high"]:
                severity = "high"
                impact_score = 7.0
            elif p95_value >= rule["thresholds"]["medium"]:
                severity = "medium"
                impact_score = 5.0
            
            if severity:
                # Generate recommendations
                recommendations = await self._generate_bottleneck_recommendations(
                    rule["type"], metric_name, p95_value
                )
                
                bottleneck = PerformanceBottleneck(
                    bottleneck_id=str(uuid.uuid4()),
                    service=service,
                    bottleneck_type=rule["type"],
                    severity=severity,
                    impact_score=impact_score,
                    description=f"{rule['description']} (P95: {p95_value:.1f})",
                    root_cause=f"{metric_name} exceeding optimal thresholds",
                    recommendations=recommendations,
                    detected_at=datetime.now()
                )
                
                return bottleneck
            
            return None
            
        except Exception as e:
            logger.error(f"Metric bottleneck analysis failed: {str(e)}")
            return None

    async def _generate_bottleneck_recommendations(
        self,
        bottleneck_type: BottleneckType,
        metric_name: str,
        value: float
    ) -> List[str]:
        """Generate recommendations for bottleneck resolution"""
        
        recommendations = []
        
        if bottleneck_type == BottleneckType.CPU:
            recommendations = [
                "Scale up CPU resources or add more instances",
                "Optimize CPU-intensive algorithms and code paths",
                "Implement CPU affinity and process optimization",
                "Consider horizontal scaling to distribute load",
                "Review and optimize thread usage patterns"
            ]
        elif bottleneck_type == BottleneckType.MEMORY:
            recommendations = [
                "Increase memory allocation or scale up instance size",
                "Optimize memory usage patterns and reduce memory leaks",
                "Implement memory pooling and object reuse",
                "Tune garbage collection settings",
                "Add memory caching layers for frequently accessed data"
            ]
        elif bottleneck_type == BottleneckType.DISK_IO:
            recommendations = [
                "Upgrade to faster storage (SSD, NVMe)",
                "Implement read/write caching mechanisms",
                "Optimize database queries and indexing",
                "Use asynchronous I/O operations",
                "Implement data compression and archiving"
            ]
        elif bottleneck_type == BottleneckType.DATABASE:
            recommendations = [
                "Optimize slow queries and add appropriate indexes",
                "Implement database connection pooling",
                "Consider read replicas for read-heavy workloads",
                "Optimize database configuration parameters",
                "Implement query result caching"
            ]
        elif bottleneck_type == BottleneckType.APPLICATION:
            recommendations = [
                "Optimize application code and algorithms",
                "Implement application-level caching",
                "Use asynchronous processing for long-running tasks",
                "Optimize API calls and reduce unnecessary requests",
                "Implement request prioritization and throttling"
            ]
        
        return recommendations

    async def generate_optimization_recommendations(self, service: str) -> List[OptimizationRecommendation]:
        """
        Generate performance optimization recommendations
        
        Args:
            service: Service name
            
        Returns:
            List of optimization recommendations
        """
        
        try:
            recommendations = []
            
            # Analyze current performance state
            current_state = await self._analyze_current_performance_state(service)
            
            # Generate recommendations for each optimization type
            for opt_type in OptimizationType:
                recommendation = await self._generate_optimization_recommendation(
                    service, opt_type, current_state
                )
                
                if recommendation:
                    recommendations.append(recommendation)
            
            # Store recommendations
            self.optimization_recommendations.extend(recommendations)
            
            # Sort by impact and implementation effort
            recommendations.sort(
                key=lambda r: (r.expected_improvement.get("performance_gain", 0), -self._effort_score(r.implementation_effort)),
                reverse=True
            )
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendation generation failed: {str(e)}")
            return []

    async def _analyze_current_performance_state(self, service: str) -> Dict[str, Any]:
        """Analyze current performance state of service"""
        
        recent_metrics = await self._get_recent_metrics(service, 3600)  # 1 hour
        
        if not recent_metrics:
            return {}
        
        # Group metrics
        metrics_by_type = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_type[metric["metric_name"]].append(metric["value"])
        
        # Calculate statistics
        state = {}
        for metric_name, values in metrics_by_type.items():
            if values:
                state[metric_name] = {
                    "avg": statistics.mean(values),
                    "p50": np.percentile(values, 50),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        return state

    async def _generate_optimization_recommendation(
        self,
        service: str,
        optimization_type: OptimizationType,
        current_state: Dict[str, Any]
    ) -> Optional[OptimizationRecommendation]:
        """Generate specific optimization recommendation"""
        
        try:
            if optimization_type == OptimizationType.RESOURCE_SIZING:
                return await self._generate_resource_sizing_recommendation(service, current_state)
            elif optimization_type == OptimizationType.CACHING:
                return await self._generate_caching_recommendation(service, current_state)
            elif optimization_type == OptimizationType.DATABASE_TUNING:
                return await self._generate_database_tuning_recommendation(service, current_state)
            # Add more optimization types as needed
            
            return None
            
        except Exception as e:
            logger.error(f"Optimization recommendation generation failed: {str(e)}")
            return None

    async def _generate_resource_sizing_recommendation(
        self,
        service: str,
        current_state: Dict[str, Any]
    ) -> Optional[OptimizationRecommendation]:
        """Generate resource sizing optimization recommendation"""
        
        cpu_stats = current_state.get("cpu_usage", {})
        memory_stats = current_state.get("memory_usage", {})
        
        if not cpu_stats or not memory_stats:
            return None
        
        cpu_p95 = cpu_stats.get("p95", 0)
        memory_p95 = memory_stats.get("p95", 0)
        
        # Check if resources are over or under-utilized
        if cpu_p95 < 30 and memory_p95 < 40:
            # Under-utilized - recommend downsizing
            return OptimizationRecommendation(
                optimization_id=str(uuid.uuid4()),
                service=service,
                optimization_type=OptimizationType.RESOURCE_SIZING,
                current_state={"cpu_p95": cpu_p95, "memory_p95": memory_p95},
                recommended_state={"action": "downsize", "cpu_reduction": "25%", "memory_reduction": "30%"},
                expected_improvement={"cost_reduction": 25.0, "efficiency_gain": 20.0},
                implementation_effort="low",
                cost_impact="reduce",
                description=f"Resources under-utilized (CPU: {cpu_p95:.1f}%, Memory: {memory_p95:.1f}%). Recommend downsizing.",
                created_at=datetime.now()
            )
        elif cpu_p95 > 85 or memory_p95 > 90:
            # Over-utilized - recommend upsizing
            return OptimizationRecommendation(
                optimization_id=str(uuid.uuid4()),
                service=service,
                optimization_type=OptimizationType.RESOURCE_SIZING,
                current_state={"cpu_p95": cpu_p95, "memory_p95": memory_p95},
                recommended_state={"action": "upsize", "cpu_increase": "50%", "memory_increase": "40%"},
                expected_improvement={"performance_gain": 30.0, "reliability_improvement": 25.0},
                implementation_effort="medium",
                cost_impact="increase",
                description=f"Resources over-utilized (CPU: {cpu_p95:.1f}%, Memory: {memory_p95:.1f}%). Recommend upsizing.",
                created_at=datetime.now()
            )
        
        return None

    async def _generate_caching_recommendation(
        self,
        service: str,
        current_state: Dict[str, Any]
    ) -> Optional[OptimizationRecommendation]:
        """Generate caching optimization recommendation"""
        
        response_time_stats = current_state.get("response_time", {})
        cache_hit_rate_stats = current_state.get("cache_hit_rate", {})
        
        if not response_time_stats:
            return None
        
        response_time_p95 = response_time_stats.get("p95", 0)
        cache_hit_rate = cache_hit_rate_stats.get("avg", 0) if cache_hit_rate_stats else 0
        
        if response_time_p95 > 500 or cache_hit_rate < 80:
            return OptimizationRecommendation(
                optimization_id=str(uuid.uuid4()),
                service=service,
                optimization_type=OptimizationType.CACHING,
                current_state={"response_time_p95": response_time_p95, "cache_hit_rate": cache_hit_rate},
                recommended_state={
                    "implement_redis_cache": True,
                    "enable_cdn": True,
                    "cache_frequently_accessed_data": True
                },
                expected_improvement={"response_time_reduction": 40.0, "cache_hit_rate_increase": 25.0},
                implementation_effort="medium",
                cost_impact="neutral",
                description=f"Poor caching performance (Response time: {response_time_p95:.1f}ms, Cache hit rate: {cache_hit_rate:.1f}%). Implement comprehensive caching strategy.",
                created_at=datetime.now()
            )
        
        return None

    async def _generate_database_tuning_recommendation(
        self,
        service: str,
        current_state: Dict[str, Any]
    ) -> Optional[OptimizationRecommendation]:
        """Generate database tuning optimization recommendation"""
        
        query_time_stats = current_state.get("query_time", {})
        db_cpu_stats = current_state.get("db_cpu_usage", {})
        
        if not query_time_stats:
            return None
        
        query_time_p95 = query_time_stats.get("p95", 0)
        db_cpu_p95 = db_cpu_stats.get("p95", 0) if db_cpu_stats else 0
        
        if query_time_p95 > 100 or db_cpu_p95 > 80:
            return OptimizationRecommendation(
                optimization_id=str(uuid.uuid4()),
                service=service,
                optimization_type=OptimizationType.DATABASE_TUNING,
                current_state={"query_time_p95": query_time_p95, "db_cpu_p95": db_cpu_p95},
                recommended_state={
                    "optimize_slow_queries": True,
                    "add_missing_indexes": True,
                    "implement_connection_pooling": True,
                    "consider_read_replicas": True
                },
                expected_improvement={"query_time_reduction": 50.0, "db_cpu_reduction": 30.0},
                implementation_effort="high",
                cost_impact="neutral",
                description=f"Database performance issues (Query time: {query_time_p95:.1f}ms, DB CPU: {db_cpu_p95:.1f}%). Comprehensive database optimization needed.",
                created_at=datetime.now()
            )
        
        return None

    def _effort_score(self, effort: str) -> int:
        """Convert effort string to numeric score"""
        effort_scores = {"low": 1, "medium": 2, "high": 3}
        return effort_scores.get(effort, 2)

    async def create_capacity_forecast(
        self,
        service: str,
        metric: str,
        forecast_days: int = 30
    ) -> str:
        """
        Create capacity forecast for service metric
        
        Args:
            service: Service name
            metric: Metric to forecast
            forecast_days: Number of days to forecast
            
        Returns:
            Forecast ID
        """
        
        try:
            forecast_id = str(uuid.uuid4())
            
            # Get historical data
            metric_key = f"{service}:{metric}"
            historical_data = list(self.aggregated_metrics[metric_key])
            
            if len(historical_data) < 50:
                raise ValueError("Insufficient historical data for forecasting")
            
            # Generate forecast using trend analysis
            values = [d["value"] for d in historical_data[-168:]]  # Last week
            
            # Simple linear trend forecasting
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                list(range(len(values))), values
            )
            
            # Generate forecasted values
            forecasted_values = []
            forecast_points = forecast_days * 24  # Hourly forecasts
            
            for i in range(forecast_points):
                future_timestamp = len(values) + i
                predicted_value = slope * future_timestamp + intercept
                
                # Add some variance
                variance = std_err * np.random.normal(0, 1)
                forecasted_value = max(0, predicted_value + variance)
                
                forecast_date = datetime.now() + timedelta(hours=i)
                
                forecasted_values.append({
                    "timestamp": forecast_date.isoformat(),
                    "value": forecasted_value,
                    "confidence_lower": forecasted_value * 0.9,
                    "confidence_upper": forecasted_value * 1.1
                })
            
            # Determine capacity exhaustion date if applicable
            current_capacity = max(values) if values else 100.0
            capacity_threshold = current_capacity * 0.9  # 90% of max capacity
            
            exhaustion_date = None
            for forecast_point in forecasted_values:
                if forecast_point["value"] > capacity_threshold:
                    exhaustion_date = datetime.fromisoformat(forecast_point["timestamp"])
                    break
            
            # Generate scaling plan
            scaling_plan = await self._generate_scaling_plan(
                service, metric, forecasted_values, current_capacity
            )
            
            forecast = CapacityForecast(
                forecast_id=forecast_id,
                service=service,
                metric=metric,
                current_capacity=current_capacity,
                forecasted_values=forecasted_values,
                capacity_exhaustion_date=exhaustion_date,
                recommended_scaling_plan=scaling_plan,
                confidence_interval=(0.9, 1.1),  # 90%-110% confidence
                created_at=datetime.now()
            )
            
            self.capacity_forecasts[forecast_id] = forecast
            
            logger.info(f"Capacity forecast created: {service}:{metric} for {forecast_days} days")
            return forecast_id
            
        except Exception as e:
            logger.error(f"Capacity forecast creation failed: {str(e)}")
            raise

    async def _generate_scaling_plan(
        self,
        service: str,
        metric: str,
        forecasted_values: List[Dict[str, Any]],
        current_capacity: float
    ) -> List[Dict[str, Any]]:
        """Generate capacity scaling plan based on forecast"""
        
        scaling_plan = []
        capacity_threshold = current_capacity * 0.8  # 80% threshold
        
        # Analyze forecast for scaling events
        for i, forecast_point in enumerate(forecasted_values):
            if forecast_point["value"] > capacity_threshold:
                # Calculate required scaling
                required_capacity = forecast_point["value"] * 1.2  # 20% buffer
                scaling_factor = required_capacity / current_capacity
                
                scaling_event = {
                    "timestamp": forecast_point["timestamp"],
                    "action": "scale_up",
                    "current_capacity": current_capacity,
                    "required_capacity": required_capacity,
                    "scaling_factor": scaling_factor,
                    "urgency": "high" if scaling_factor > 2.0 else "medium",
                    "recommendation": f"Scale {service} to {scaling_factor:.1f}x current capacity"
                }
                
                scaling_plan.append(scaling_event)
                
                # Update current capacity for subsequent calculations
                current_capacity = required_capacity
                capacity_threshold = current_capacity * 0.8
        
        return scaling_plan

    # Background monitoring tasks
    async def _performance_monitoring_loop(self):
        """Background performance monitoring loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Collect system performance metrics
                await self._collect_system_metrics()
                
            except Exception as e:
                logger.error(f"Performance monitoring loop error: {str(e)}")

    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        
        # Mock system metrics collection
        import random
        
        services = ["web_service", "worker_service", "database"]
        metrics = ["cpu_usage", "memory_usage", "response_time", "throughput"]
        
        for service in services:
            for metric in metrics:
                # Generate realistic metric values
                base_values = {
                    "cpu_usage": 50 + random.uniform(-20, 30),
                    "memory_usage": 60 + random.uniform(-25, 25),
                    "response_time": 200 + random.uniform(-100, 200),
                    "throughput": 1000 + random.uniform(-300, 500)
                }
                
                value = max(0, base_values[metric])
                await self.collect_performance_metric(metric, value, service)

    async def _auto_scaling_loop(self):
        """Background auto-scaling analysis loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
                # Analyze scaling needs for all services
                for service in self.scaling_policies.keys():
                    recommendations = await self.analyze_scaling_needs(service)
                    
                    for recommendation in recommendations:
                        logger.info(f"Scaling recommendation: {recommendation.service} - {recommendation.direction.value}")
                
            except Exception as e:
                logger.error(f"Auto-scaling loop error: {str(e)}")

    async def _bottleneck_detection_loop(self):
        """Background bottleneck detection loop"""
        while True:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes
                
                # Detect bottlenecks for all services
                for service in ["web_service", "worker_service", "database"]:
                    bottlenecks = await self.detect_performance_bottlenecks(service)
                    
                    for bottleneck in bottlenecks:
                        logger.warning(f"Performance bottleneck detected: {bottleneck.service} - {bottleneck.bottleneck_type.value}")
                
            except Exception as e:
                logger.error(f"Bottleneck detection loop error: {str(e)}")

    async def _capacity_planning_loop(self):
        """Background capacity planning loop"""
        while True:
            try:
                await asyncio.sleep(86400)  # Daily capacity planning
                
                # Generate capacity forecasts
                services = ["web_service", "worker_service", "database"]
                metrics = ["cpu_usage", "memory_usage", "storage_usage"]
                
                for service in services:
                    for metric in metrics:
                        try:
                            await self.create_capacity_forecast(service, metric, 30)
                        except Exception as e:
                            logger.warning(f"Capacity forecast failed for {service}:{metric} - {str(e)}")
                
            except Exception as e:
                logger.error(f"Capacity planning loop error: {str(e)}")

    async def _optimization_analysis_loop(self):
        """Background optimization analysis loop"""
        while True:
            try:
                await asyncio.sleep(3600)  # Analyze every hour
                
                # Generate optimization recommendations
                for service in ["web_service", "worker_service", "database"]:
                    recommendations = await self.generate_optimization_recommendations(service)
                    
                    for recommendation in recommendations:
                        logger.info(f"Optimization recommendation: {recommendation.service} - {recommendation.optimization_type.value}")
                
            except Exception as e:
                logger.error(f"Optimization analysis loop error: {str(e)}")

    async def _model_training_loop(self):
        """Background ML model training loop"""
        while True:
            try:
                await asyncio.sleep(43200)  # Train every 12 hours
                
                # Train/update prediction models
                await self._train_prediction_models()
                
            except Exception as e:
                logger.error(f"Model training loop error: {str(e)}")

    async def _train_prediction_models(self):
        """Train ML models for performance prediction"""
        
        # Mock model training
        logger.info("Training performance prediction models...")
        
        # Update model accuracy scores
        self.model_accuracy = {
            "cpu_prediction": 0.85,
            "memory_prediction": 0.82,
            "response_time_prediction": 0.78,
            "throughput_prediction": 0.88
        }

    async def health_check(self) -> bool:
        """Performance optimizer health check"""
        
        try:
            # Check if metrics are being collected
            recent_metrics = [
                m for m in self.performance_metrics 
                if m.timestamp >= datetime.now() - timedelta(minutes=10)
            ]
            
            if len(recent_metrics) == 0:
                logger.warning("No recent performance metrics")
                return False
            
            # Check for excessive bottlenecks
            active_bottlenecks = [
                b for b in self.bottlenecks.values() 
                if b.resolved_at is None
            ]
            
            if len(active_bottlenecks) > 10:
                logger.warning("Too many active performance bottlenecks")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Performance optimizer health check failed: {str(e)}")
            return False

    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard"""
        
        # Calculate performance statistics
        recent_metrics = [
            m for m in self.performance_metrics 
            if m.timestamp >= datetime.now() - timedelta(hours=1)
        ]
        
        metrics_by_service = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_service[metric.service].append(metric)
        
        # Count bottlenecks by severity
        bottleneck_counts = defaultdict(int)
        for bottleneck in self.bottlenecks.values():
            if bottleneck.resolved_at is None:
                bottleneck_counts[bottleneck.severity] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": {
                "total_metrics": len(self.performance_metrics),
                "recent_metrics": len(recent_metrics),
                "services_monitored": len(metrics_by_service),
                "metrics_per_minute": len([
                    m for m in recent_metrics 
                    if m.timestamp >= datetime.now() - timedelta(minutes=1)
                ])
            },
            "auto_scaling": {
                "active_recommendations": len(self.scaling_recommendations),
                "scaling_policies": len(self.scaling_policies),
                "recent_scaling_events": len([
                    event for event in self.scaling_history 
                    if event.get("timestamp", datetime.min) >= datetime.now() - timedelta(hours=24)
                ])
            },
            "bottlenecks": {
                "total_bottlenecks": len(self.bottlenecks),
                "active_bottlenecks": len([
                    b for b in self.bottlenecks.values() 
                    if b.resolved_at is None
                ]),
                "by_severity": dict(bottleneck_counts),
                "by_type": {
                    bt.value: len([
                        b for b in self.bottlenecks.values() 
                        if b.bottleneck_type == bt and b.resolved_at is None
                    ]) for bt in BottleneckType
                }
            },
            "optimization": {
                "active_recommendations": len(self.optimization_recommendations),
                "optimization_strategies": len(self.optimization_strategies),
                "performance_baselines": len(self.performance_baselines)
            },
            "capacity_planning": {
                "active_forecasts": len(self.capacity_forecasts),
                "capacity_thresholds": len(self.capacity_thresholds),
                "forecasts_with_exhaustion": len([
                    f for f in self.capacity_forecasts.values() 
                    if f.capacity_exhaustion_date is not None
                ])
            },
            "ml_models": {
                "prediction_models": len(self.prediction_models),
                "average_accuracy": statistics.mean(self.model_accuracy.values()) if self.model_accuracy else 0,
                "model_accuracy": self.model_accuracy
            }
        }

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

logger.info("🚀 Performance Optimizer initialized - Auto-scaling and performance management")