"""📊 Profiling Analytics Engine
==============================

Advanced profiling analytics and machine learning engine for the Ainflue Creator Economy platform.
Aggregates profiling data, provides predictive insights, and optimizes system performance automatically.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import numpy as np

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class AnalyticsMetricType(Enum):
    """Types of analytics metrics"""
    PERFORMANCE_TREND = "performance_trend"
    BOTTLENECK_FREQUENCY = "bottleneck_frequency"
    OPTIMIZATION_IMPACT = "optimization_impact"
    USER_EXPERIENCE_SCORE = "user_experience_score"
    SYSTEM_EFFICIENCY = "system_efficiency"
    COST_OPTIMIZATION = "cost_optimization"
    PREDICTIVE_SCALING = "predictive_scaling"
    ANOMALY_DETECTION = "anomaly_detection"


class PredictionType(Enum):
    """Types of predictions"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    CAPACITY_EXHAUSTION = "capacity_exhaustion"
    BOTTLENECK_OCCURRENCE = "bottleneck_occurrence"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"
    USER_CHURN_RISK = "user_churn_risk"
    COST_SPIKE = "cost_spike"
    SECURITY_INCIDENT = "security_incident"


class OptimizationCategory(Enum):
    """Categories of optimizations"""
    PERFORMANCE = "performance"
    COST = "cost"
    RELIABILITY = "reliability"
    SECURITY = "security"
    USER_EXPERIENCE = "user_experience"
    SCALABILITY = "scalability"


@dataclass
class ProfilingDataPoint:
    """Aggregated profiling data point"""
    timestamp: datetime
    component: str
    metric_type: str
    value: float
    unit: str
    
    # Context
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality indicators
    confidence: float = 1.0  # 0-1
    sample_size: int = 1


@dataclass
class PerformanceTrend:
    """Performance trend analysis"""
    trend_id: str
    component: str
    metric_type: str
    
    # Trend characteristics
    direction: str  # "improving", "degrading", "stable"
    strength: float  # 0-1
    confidence: float  # 0-1
    
    # Time series data
    data_points: List[ProfilingDataPoint]
    trend_line: List[float]
    
    # Statistical analysis
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    
    # Predictions
    predicted_values: List[float]
    prediction_horizon_hours: int = 24
    
    # Seasonality
    has_seasonality: bool = False
    seasonal_pattern: Optional[List[float]] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Prediction:
    """Performance prediction"""
    prediction_id: str
    prediction_type: PredictionType
    component: str
    
    # Prediction details
    predicted_event: str
    probability: float  # 0-1
    confidence: float  # 0-1
    time_to_event_hours: float
    
    # Impact analysis
    severity: str  # "low", "medium", "high", "critical"
    business_impact: str
    technical_impact: str
    user_impact: str
    
    # Supporting data
    historical_patterns: List[str]
    contributing_factors: List[str]
    
    # Recommendations
    preventive_actions: List[str]
    mitigation_strategies: List[str]
    monitoring_suggestions: List[str]
    
    # Model information
    model_name: str
    model_accuracy: float
    features_used: List[str]
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptimizationRecommendation:
    """ML-powered optimization recommendation"""
    recommendation_id: str
    category: OptimizationCategory
    component: str
    
    # Recommendation details
    title: str
    description: str
    priority: str  # "low", "medium", "high", "critical"
    
    # Implementation
    implementation_steps: List[str]
    estimated_effort_hours: float
    required_resources: List[str]
    
    # Expected benefits
    performance_improvement: Dict[str, float]
    cost_savings_usd: Optional[float] = None
    reliability_improvement: Optional[float] = None
    user_experience_improvement: Optional[float] = None
    
    # Risk analysis
    implementation_risk: str  # "low", "medium", "high"
    rollback_plan: List[str]
    testing_requirements: List[str]
    
    # ML insights
    confidence_score: float  # 0-1
    similar_cases: List[str]
    success_probability: float  # 0-1
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    anomaly_id: str
    component: str
    metric_type: str
    
    # Anomaly characteristics
    anomaly_type: str  # "spike", "drop", "drift", "oscillation"
    severity: float  # 0-1
    deviation_from_normal: float
    
    # Data points
    anomalous_values: List[float]
    normal_range: Tuple[float, float]
    timestamps: List[datetime]
    
    # Root cause analysis
    potential_causes: List[str]
    correlated_anomalies: List[str]
    
    # Impact assessment
    business_impact_score: float  # 0-1
    user_impact_score: float  # 0-1
    system_impact_score: float  # 0-1
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ProfilingAnalyticsEngine:
    """Advanced profiling analytics and ML engine"""
    
    def __init__(self,
                 aggregation_interval_minutes: int = 5,
                 trend_analysis_window_hours: int = 24,
                 prediction_horizon_hours: int = 24,
                 enable_ml_predictions: bool = True,
                 enable_anomaly_detection: bool = True,
                 max_data_points: int = 100000):
        """
        Initialize profiling analytics engine
        
        Args:
            aggregation_interval_minutes: Data aggregation interval
            trend_analysis_window_hours: Window for trend analysis
            prediction_horizon_hours: Prediction time horizon
            enable_ml_predictions: Enable ML-based predictions
            enable_anomaly_detection: Enable anomaly detection
            max_data_points: Maximum data points to store
        """
        self.aggregation_interval = aggregation_interval_minutes
        self.trend_analysis_window = trend_analysis_window_hours
        self.prediction_horizon = prediction_horizon_hours
        self.enable_ml_predictions = enable_ml_predictions
        self.enable_anomaly_detection = enable_anomaly_detection
        self.max_data_points = max_data_points
        
        # Data storage
        self.profiling_data: deque = deque(maxlen=max_data_points)
        self.aggregated_data: Dict[str, List[ProfilingDataPoint]] = defaultdict(list)
        
        # Analysis results
        self.performance_trends: Dict[str, PerformanceTrend] = {}
        self.predictions: List[Prediction] = []
        self.optimization_recommendations: List[OptimizationRecommendation] = []
        self.detected_anomalies: List[AnomalyDetection] = []
        
        # ML models (simplified placeholders)
        self.ml_models: Dict[str, Any] = {}
        self.model_accuracies: Dict[str, float] = {}
        
        # Analytics state
        self.is_analyzing = False
        self.analysis_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("ProfilingAnalyticsEngine initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'analytics_data_points': Gauge(
                'ainflue_analytics_data_points_total',
                'Total data points in analytics engine',
                ['component', 'metric_type']
            ),
            'analytics_trends': Gauge(
                'ainflue_analytics_trends_active',
                'Number of active performance trends',
                ['component', 'direction']
            ),
            'analytics_predictions': Gauge(
                'ainflue_analytics_predictions_active',
                'Number of active predictions',
                ['prediction_type', 'severity']
            ),
            'analytics_recommendations': Gauge(
                'ainflue_analytics_recommendations_active',
                'Number of active optimization recommendations',
                ['category', 'priority']
            ),
            'analytics_anomalies': Counter(
                'ainflue_analytics_anomalies_detected_total',
                'Total anomalies detected',
                ['component', 'anomaly_type']
            ),
            'analytics_model_accuracy': Gauge(
                'ainflue_analytics_model_accuracy',
                'ML model accuracy scores',
                ['model_name']
            )
        }
    
    async def start_analytics(self):
        """Start analytics processing"""
        if self.is_analyzing:
            logger.warning("Analytics already running")
            return
        
        self.is_analyzing = True
        self.analysis_task = asyncio.create_task(self._analytics_loop())
        
        # Initialize ML models
        if self.enable_ml_predictions:
            await self._initialize_ml_models()
        
        logger.info("Profiling analytics started")
    
    async def stop_analytics(self):
        """Stop analytics processing"""
        if not self.is_analyzing:
            return
        
        self.is_analyzing = False
        
        if self.analysis_task:
            self.analysis_task.cancel()
            try:
                await self.analysis_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Profiling analytics stopped")
    
    async def add_profiling_data(self, data_points: List[ProfilingDataPoint]):
        """Add profiling data points for analysis"""
        with self._lock:
            for data_point in data_points:
                self.profiling_data.append(data_point)
                
                # Add to aggregated data by component and metric
                key = f"{data_point.component}_{data_point.metric_type}"
                self.aggregated_data[key].append(data_point)
                
                # Keep aggregated data within limits
                if len(self.aggregated_data[key]) > 1000:
                    self.aggregated_data[key] = self.aggregated_data[key][-1000:]
        
        # Update Prometheus metrics
        for data_point in data_points:
            self.prometheus_metrics['analytics_data_points'].labels(
                component=data_point.component,
                metric_type=data_point.metric_type
            ).inc()
    
    async def _analytics_loop(self):
        """Background analytics processing loop"""
        while self.is_analyzing:
            try:
                # Perform trend analysis
                await self._analyze_trends()
                
                # Generate predictions
                if self.enable_ml_predictions:
                    await self._generate_predictions()
                
                # Detect anomalies
                if self.enable_anomaly_detection:
                    await self._detect_anomalies()
                
                # Generate optimization recommendations
                await self._generate_optimization_recommendations()
                
                # Clean up old data
                await self._cleanup_old_analytics_data()
                
                # Sleep for aggregation interval
                await asyncio.sleep(self.aggregation_interval * 60)
                
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _analyze_trends(self):
        """Analyze performance trends"""
        try:
            current_time = datetime.utcnow()
            
            for key, data_points in self.aggregated_data.items():
                if len(data_points) < 10:  # Need enough data points
                    continue
                
                component, metric_type = key.split('_', 1)
                
                # Filter recent data
                cutoff_time = current_time - timedelta(hours=self.trend_analysis_window)
                recent_points = [dp for dp in data_points if dp.timestamp > cutoff_time]
                
                if len(recent_points) < 5:
                    continue
                
                # Calculate trend
                trend = await self._calculate_trend(component, metric_type, recent_points)
                
                if trend:
                    self.performance_trends[key] = trend
                    
                    # Update Prometheus metrics
                    self.prometheus_metrics['analytics_trends'].labels(
                        component=component,
                        direction=trend.direction
                    ).set(1.0)
        
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
    
    async def _calculate_trend(self, component: str, metric_type: str, data_points: List[ProfilingDataPoint]) -> Optional[PerformanceTrend]:
        """Calculate trend for a metric"""
        try:
            # Extract values and timestamps
            values = [dp.value for dp in data_points]
            timestamps = [dp.timestamp for dp in data_points]
            
            # Convert timestamps to numeric values for regression
            base_time = timestamps[0]
            x_vals = [(ts - base_time).total_seconds() / 3600 for ts in timestamps]  # Hours
            y_vals = values
            
            # Simple linear regression
            if len(x_vals) < 2:
                return None
            
            # Calculate trend line
            x_mean = np.mean(x_vals)
            y_mean = np.mean(y_vals)
            
            numerator = np.sum((np.array(x_vals) - x_mean) * (np.array(y_vals) - y_mean))
            denominator = np.sum((np.array(x_vals) - x_mean) ** 2)
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            intercept = y_mean - slope * x_mean
            
            # Generate trend line
            trend_line = [slope * x + intercept for x in x_vals]
            
            # Determine trend direction and strength
            if abs(slope) < 0.01:
                direction = "stable"
                strength = 0.0
            elif slope > 0:
                direction = "degrading" if metric_type in ["response_time", "error_rate", "memory_usage"] else "improving"
                strength = min(1.0, abs(slope) / np.std(y_vals))
            else:
                direction = "improving" if metric_type in ["response_time", "error_rate", "memory_usage"] else "degrading"
                strength = min(1.0, abs(slope) / np.std(y_vals))
            
            # Generate predictions
            predicted_values = []
            for future_hour in range(1, self.prediction_horizon + 1):
                future_x = x_vals[-1] + future_hour
                predicted_value = slope * future_x + intercept
                predicted_values.append(predicted_value)
            
            # Calculate statistics
            mean_val = np.mean(y_vals)
            std_dev = np.std(y_vals)
            min_val = np.min(y_vals)
            max_val = np.max(y_vals)
            
            # Create trend object
            trend = PerformanceTrend(
                trend_id=f"trend_{component}_{metric_type}_{int(time.time())}",
                component=component,
                metric_type=metric_type,
                direction=direction,
                strength=strength,
                confidence=min(1.0, len(data_points) / 50.0),  # More data = higher confidence
                data_points=data_points,
                trend_line=trend_line,
                mean=mean_val,
                std_dev=std_dev,
                min_value=min_val,
                max_value=max_val,
                predicted_values=predicted_values,
                prediction_horizon_hours=self.prediction_horizon
            )
            
            return trend
            
        except Exception as e:
            logger.error(f"Error calculating trend for {component}_{metric_type}: {e}")
            return None
    
    async def _generate_predictions(self):
        """Generate ML-based predictions"""
        try:
            # Generate predictions based on trends
            for trend in self.performance_trends.values():
                if trend.direction == "degrading" and trend.strength > 0.5:
                    # Predict performance degradation
                    prediction = await self._create_performance_degradation_prediction(trend)
                    if prediction:
                        self.predictions.append(prediction)
                        
                        # Update Prometheus metrics
                        self.prometheus_metrics['analytics_predictions'].labels(
                            prediction_type=prediction.prediction_type.value,
                            severity=prediction.severity
                        ).set(1.0)
            
            # Generate capacity predictions
            await self._generate_capacity_predictions()
            
            # Generate cost predictions
            await self._generate_cost_predictions()
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
    
    async def _create_performance_degradation_prediction(self, trend: PerformanceTrend) -> Optional[Prediction]:
        """Create performance degradation prediction"""
        try:
            # Calculate when threshold might be breached
            threshold_multiplier = 1.5  # 50% increase from current mean
            threshold_value = trend.mean * threshold_multiplier
            
            # Find when predicted values exceed threshold
            time_to_threshold = None
            for hour, predicted_value in enumerate(trend.predicted_values):
                if predicted_value > threshold_value:
                    time_to_threshold = hour + 1
                    break
            
            if time_to_threshold is None:
                return None
            
            # Calculate probability based on trend strength and confidence
            probability = min(0.95, trend.strength * trend.confidence)
            
            prediction = Prediction(
                prediction_id=f"pred_degradation_{int(time.time())}",
                prediction_type=PredictionType.PERFORMANCE_DEGRADATION,
                component=trend.component,
                predicted_event=f"{trend.metric_type} will exceed threshold in {time_to_threshold} hours",
                probability=probability,
                confidence=trend.confidence,
                time_to_event_hours=time_to_threshold,
                severity="high" if time_to_threshold < 6 else "medium",
                business_impact="Service performance degradation affecting user experience",
                technical_impact=f"Increasing {trend.metric_type} affecting system performance",
                user_impact="Slower response times and potential service interruptions",
                historical_patterns=[f"Similar degradation pattern observed in {trend.direction} trend"],
                contributing_factors=["Increasing system load", "Resource constraints", "Code inefficiencies"],
                preventive_actions=[
                    "Monitor resource utilization closely",
                    "Implement auto-scaling if not already active",
                    "Review recent code deployments",
                    "Check for memory leaks or resource leaks"
                ],
                mitigation_strategies=[
                    "Scale up resources preemptively",
                    "Implement circuit breakers",
                    "Optimize critical code paths",
                    "Enable request throttling"
                ],
                monitoring_suggestions=[
                    f"Set up alerts for {trend.metric_type} > {threshold_value:.2f}",
                    "Monitor correlated metrics",
                    "Track resource utilization trends"
                ],
                model_name="trend_analysis",
                model_accuracy=0.75,  # Simplified
                features_used=[trend.metric_type, "trend_direction", "trend_strength"]
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error creating performance degradation prediction: {e}")
            return None
    
    async def _generate_capacity_predictions(self):
        """Generate capacity exhaustion predictions"""
        try:
            # Look for memory and CPU trends
            for key, trend in self.performance_trends.items():
                if "memory" in trend.metric_type.lower() or "cpu" in trend.metric_type.lower():
                    if trend.direction == "degrading" and trend.strength > 0.3:
                        # Predict capacity exhaustion
                        max_capacity = 100.0 if "percent" in trend.metric_type else 1000.0  # Simplified
                        
                        # Find when capacity might be exhausted
                        time_to_exhaustion = None
                        for hour, predicted_value in enumerate(trend.predicted_values):
                            if predicted_value > max_capacity * 0.9:  # 90% capacity
                                time_to_exhaustion = hour + 1
                                break
                        
                        if time_to_exhaustion and time_to_exhaustion < 48:  # Within 48 hours
                            prediction = Prediction(
                                prediction_id=f"pred_capacity_{int(time.time())}",
                                prediction_type=PredictionType.CAPACITY_EXHAUSTION,
                                component=trend.component,
                                predicted_event=f"Capacity exhaustion in {time_to_exhaustion} hours",
                                probability=min(0.9, trend.strength * trend.confidence),
                                confidence=trend.confidence,
                                time_to_event_hours=time_to_exhaustion,
                                severity="critical" if time_to_exhaustion < 12 else "high",
                                business_impact="System capacity exhaustion leading to service unavailability",
                                technical_impact="Resource exhaustion affecting all system components",
                                user_impact="Service outages and complete service unavailability",
                                historical_patterns=[f"Capacity trend indicates exhaustion"],
                                contributing_factors=["Increasing resource demand", "Lack of auto-scaling"],
                                preventive_actions=[
                                    "Implement immediate scaling",
                                    "Review resource allocation",
                                    "Enable auto-scaling policies"
                                ],
                                mitigation_strategies=[
                                    "Emergency capacity increase",
                                    "Load shedding implementation",
                                    "Service degradation protocols"
                                ],
                                monitoring_suggestions=[
                                    "Set up critical capacity alerts",
                                    "Monitor scaling events",
                                    "Track capacity utilization"
                                ],
                                model_name="capacity_analysis",
                                model_accuracy=0.80,
                                features_used=["resource_utilization", "trend_direction", "growth_rate"]
                            )
                            
                            self.predictions.append(prediction)
        
        except Exception as e:
            logger.error(f"Error generating capacity predictions: {e}")
    
    async def _generate_cost_predictions(self):
        """Generate cost spike predictions"""
        try:
            # Simplified cost prediction based on resource usage trends
            high_usage_components = []
            
            for key, trend in self.performance_trends.items():
                if trend.direction == "degrading" and trend.strength > 0.4:
                    if any(metric in trend.metric_type.lower() for metric in ["cpu", "memory", "network", "storage"]):
                        high_usage_components.append(trend.component)
            
            if len(high_usage_components) > 2:  # Multiple components showing high usage
                prediction = Prediction(
                    prediction_id=f"pred_cost_{int(time.time())}",
                    prediction_type=PredictionType.COST_SPIKE,
                    component="infrastructure",
                    predicted_event="Potential cost spike due to increased resource usage",
                    probability=0.7,
                    confidence=0.6,
                    time_to_event_hours=24,
                    severity="medium",
                    business_impact="Increased infrastructure costs affecting budget",
                    technical_impact="Higher resource consumption across multiple components",
                    user_impact="Minimal direct impact if performance maintained",
                    historical_patterns=["Multiple components showing increased usage"],
                    contributing_factors=["Increased user activity", "Inefficient resource usage"],
                    preventive_actions=[
                        "Review cost optimization opportunities",
                        "Implement cost monitoring alerts",
                        "Optimize resource allocation"
                    ],
                    mitigation_strategies=[
                        "Implement cost controls",
                        "Optimize resource usage",
                        "Consider reserved instances"
                    ],
                    monitoring_suggestions=[
                        "Set up cost alerts",
                        "Monitor resource efficiency",
                        "Track cost per user metrics"
                    ],
                    model_name="cost_analysis",
                    model_accuracy=0.65,
                    features_used=["resource_usage", "user_activity", "cost_trends"]
                )
                
                self.predictions.append(prediction)
        
        except Exception as e:
            logger.error(f"Error generating cost predictions: {e}")
    
    async def _detect_anomalies(self):
        """Detect anomalies in profiling data"""
        try:
            for key, data_points in self.aggregated_data.items():
                if len(data_points) < 20:  # Need enough data for anomaly detection
                    continue
                
                component, metric_type = key.split('_', 1)
                
                # Get recent values
                recent_points = data_points[-50:]  # Last 50 points
                values = [dp.value for dp in recent_points]
                
                # Simple anomaly detection using statistical methods
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                # Detect outliers (values beyond 3 standard deviations)
                anomalous_indices = []
                for i, value in enumerate(values):
                    if abs(value - mean_val) > 3 * std_val:
                        anomalous_indices.append(i)
                
                if anomalous_indices:
                    # Create anomaly detection result
                    anomalous_values = [values[i] for i in anomalous_indices]
                    anomalous_timestamps = [recent_points[i].timestamp for i in anomalous_indices]
                    
                    # Determine anomaly type
                    if all(v > mean_val + 2 * std_val for v in anomalous_values):
                        anomaly_type = "spike"
                    elif all(v < mean_val - 2 * std_val for v in anomalous_values):
                        anomaly_type = "drop"
                    else:
                        anomaly_type = "oscillation"
                    
                    anomaly = AnomalyDetection(
                        anomaly_id=f"anomaly_{component}_{metric_type}_{int(time.time())}",
                        component=component,
                        metric_type=metric_type,
                        anomaly_type=anomaly_type,
                        severity=min(1.0, max(anomalous_values) / mean_val) if mean_val > 0 else 0.5,
                        deviation_from_normal=np.mean([abs(v - mean_val) / std_val for v in anomalous_values]),
                        anomalous_values=anomalous_values,
                        normal_range=(mean_val - 2 * std_val, mean_val + 2 * std_val),
                        timestamps=anomalous_timestamps,
                        potential_causes=[
                            "Sudden traffic spike",
                            "System malfunction",
                            "External dependency issue",
                            "Configuration change"
                        ],
                        correlated_anomalies=[],  # Would be calculated
                        business_impact_score=0.7,  # Simplified
                        user_impact_score=0.6,
                        system_impact_score=0.8
                    )
                    
                    self.detected_anomalies.append(anomaly)
                    
                    # Update Prometheus metrics
                    self.prometheus_metrics['analytics_anomalies'].labels(
                        component=component,
                        anomaly_type=anomaly_type
                    ).inc()
                    
                    logger.warning(f"Anomaly detected in {component}_{metric_type}: {anomaly_type}")
        
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
    
    async def _generate_optimization_recommendations(self):
        """Generate ML-powered optimization recommendations"""
        try:
            # Analyze trends and anomalies to generate recommendations
            for trend in self.performance_trends.values():
                if trend.direction == "degrading":
                    recommendations = await self._create_optimization_recommendations_for_trend(trend)
                    self.optimization_recommendations.extend(recommendations)
            
            # Generate recommendations based on anomalies
            for anomaly in self.detected_anomalies[-10:]:  # Recent anomalies
                recommendations = await self._create_optimization_recommendations_for_anomaly(anomaly)
                self.optimization_recommendations.extend(recommendations)
            
            # Update Prometheus metrics
            for rec in self.optimization_recommendations[-10:]:  # Recent recommendations
                self.prometheus_metrics['analytics_recommendations'].labels(
                    category=rec.category.value,
                    priority=rec.priority
                ).set(1.0)
        
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
    
    async def _create_optimization_recommendations_for_trend(self, trend: PerformanceTrend) -> List[OptimizationRecommendation]:
        """Create optimization recommendations based on trend"""
        recommendations = []
        
        try:
            if "response_time" in trend.metric_type.lower():
                rec = OptimizationRecommendation(
                    recommendation_id=f"opt_response_{int(time.time())}",
                    category=OptimizationCategory.PERFORMANCE,
                    component=trend.component,
                    title="Optimize Response Time Performance",
                    description=f"Response time showing degrading trend with {trend.strength:.1f} strength",
                    priority="high" if trend.strength > 0.7 else "medium",
                    implementation_steps=[
                        "Analyze slow queries and optimize database performance",
                        "Implement response caching for frequently accessed data",
                        "Optimize critical code paths and algorithms",
                        "Consider horizontal scaling if load is the issue"
                    ],
                    estimated_effort_hours=16.0,
                    required_resources=["backend_developer", "dba", "devops_engineer"],
                    performance_improvement={
                        "response_time_reduction_percent": 30.0,
                        "throughput_increase_percent": 20.0
                    },
                    implementation_risk="medium",
                    rollback_plan=[
                        "Revert code changes if performance degrades",
                        "Disable caching if issues occur",
                        "Scale back if scaling causes problems"
                    ],
                    testing_requirements=[
                        "Load testing with realistic traffic",
                        "Performance benchmarking",
                        "Rollback testing"
                    ],
                    confidence_score=0.8,
                    similar_cases=["Previous response time optimization in Q3"],
                    success_probability=0.75
                )
                recommendations.append(rec)
            
            elif "memory" in trend.metric_type.lower():
                rec = OptimizationRecommendation(
                    recommendation_id=f"opt_memory_{int(time.time())}",
                    category=OptimizationCategory.PERFORMANCE,
                    component=trend.component,
                    title="Optimize Memory Usage",
                    description=f"Memory usage showing concerning trend with {trend.strength:.1f} strength",
                    priority="high" if trend.strength > 0.6 else "medium",
                    implementation_steps=[
                        "Conduct memory profiling to identify leaks",
                        "Optimize object lifecycle management",
                        "Implement memory pooling for frequently used objects",
                        "Review and optimize caching strategies"
                    ],
                    estimated_effort_hours=12.0,
                    required_resources=["backend_developer", "performance_engineer"],
                    performance_improvement={
                        "memory_usage_reduction_percent": 25.0,
                        "gc_pressure_reduction_percent": 40.0
                    },
                    implementation_risk="low",
                    rollback_plan=[
                        "Revert memory optimization changes",
                        "Restore previous object pooling settings"
                    ],
                    testing_requirements=[
                        "Memory leak testing",
                        "Stress testing under load",
                        "Long-running stability tests"
                    ],
                    confidence_score=0.85,
                    similar_cases=["Memory optimization project last quarter"],
                    success_probability=0.8
                )
                recommendations.append(rec)
        
        except Exception as e:
            logger.error(f"Error creating trend-based recommendations: {e}")
        
        return recommendations
    
    async def _create_optimization_recommendations_for_anomaly(self, anomaly: AnomalyDetection) -> List[OptimizationRecommendation]:
        """Create optimization recommendations based on anomaly"""
        recommendations = []
        
        try:
            if anomaly.anomaly_type == "spike":
                rec = OptimizationRecommendation(
                    recommendation_id=f"opt_spike_{int(time.time())}",
                    category=OptimizationCategory.RELIABILITY,
                    component=anomaly.component,
                    title="Implement Spike Protection",
                    description=f"Recurring spikes detected in {anomaly.metric_type}",
                    priority="medium",
                    implementation_steps=[
                        "Implement rate limiting to prevent spikes",
                        "Add circuit breakers for fault tolerance",
                        "Set up auto-scaling triggers",
                        "Implement request queuing for load management"
                    ],
                    estimated_effort_hours=8.0,
                    required_resources=["backend_developer", "devops_engineer"],
                    performance_improvement={
                        "spike_reduction_percent": 60.0,
                        "stability_improvement_percent": 40.0
                    },
                    reliability_improvement=0.3,
                    implementation_risk="low",
                    rollback_plan=[
                        "Disable rate limiting if issues occur",
                        "Bypass circuit breakers if needed"
                    ],
                    testing_requirements=[
                        "Spike simulation testing",
                        "Circuit breaker testing",
                        "Rate limiting validation"
                    ],
                    confidence_score=0.7,
                    similar_cases=["Spike protection implemented for API gateway"],
                    success_probability=0.8
                )
                recommendations.append(rec)
        
        except Exception as e:
            logger.error(f"Error creating anomaly-based recommendations: {e}")
        
        return recommendations
    
    async def _initialize_ml_models(self):
        """Initialize ML models for predictions"""
        try:
            # Placeholder for ML model initialization
            # In a real implementation, this would load trained models
            
            self.ml_models = {
                "performance_degradation": {"type": "regression", "accuracy": 0.75},
                "capacity_prediction": {"type": "time_series", "accuracy": 0.80},
                "anomaly_detection": {"type": "isolation_forest", "accuracy": 0.70},
                "cost_prediction": {"type": "regression", "accuracy": 0.65}
            }
            
            # Update model accuracy metrics
            for model_name, model_info in self.ml_models.items():
                self.prometheus_metrics['analytics_model_accuracy'].labels(
                    model_name=model_name
                ).set(model_info["accuracy"])
            
            logger.info("ML models initialized for analytics engine")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    async def _cleanup_old_analytics_data(self):
        """Clean up old analytics data"""
        cutoff_time = datetime.utcnow() - timedelta(days=7)  # Keep 7 days of data
        
        # Clean up old predictions
        self.predictions = [p for p in self.predictions if p.timestamp > cutoff_time]
        
        # Clean up old recommendations  
        self.optimization_recommendations = [r for r in self.optimization_recommendations if r.timestamp > cutoff_time]
        
        # Clean up old anomalies
        self.detected_anomalies = [a for a in self.detected_anomalies if a.timestamp > cutoff_time]
    
    def get_analytics_report(self) -> Dict[str, Any]:
        """Get comprehensive analytics report"""
        try:
            return {
                "summary": {
                    "total_data_points": len(self.profiling_data),
                    "active_trends": len(self.performance_trends),
                    "active_predictions": len([p for p in self.predictions if p.timestamp > datetime.utcnow() - timedelta(hours=24)]),
                    "active_recommendations": len([r for r in self.optimization_recommendations if r.timestamp > datetime.utcnow() - timedelta(hours=24)]),
                    "recent_anomalies": len([a for a in self.detected_anomalies if a.timestamp > datetime.utcnow() - timedelta(hours=24)])
                },
                "performance_trends": [
                    {
                        "id": trend.trend_id,
                        "component": trend.component,
                        "metric_type": trend.metric_type,
                        "direction": trend.direction,
                        "strength": trend.strength,
                        "confidence": trend.confidence,
                        "mean": trend.mean,
                        "predicted_values": trend.predicted_values[:5]  # Next 5 hours
                    }
                    for trend in self.performance_trends.values()
                ],
                "predictions": [
                    {
                        "id": pred.prediction_id,
                        "type": pred.prediction_type.value,
                        "component": pred.component,
                        "event": pred.predicted_event,
                        "probability": pred.probability,
                        "time_to_event_hours": pred.time_to_event_hours,
                        "severity": pred.severity,
                        "preventive_actions": pred.preventive_actions
                    }
                    for pred in self.predictions[-10:]  # Last 10 predictions
                ],
                "optimization_recommendations": [
                    {
                        "id": rec.recommendation_id,
                        "category": rec.category.value,
                        "component": rec.component,
                        "title": rec.title,
                        "priority": rec.priority,
                        "estimated_effort_hours": rec.estimated_effort_hours,
                        "performance_improvement": rec.performance_improvement,
                        "confidence_score": rec.confidence_score
                    }
                    for rec in self.optimization_recommendations[-10:]  # Last 10 recommendations
                ],
                "recent_anomalies": [
                    {
                        "id": anomaly.anomaly_id,
                        "component": anomaly.component,
                        "metric_type": anomaly.metric_type,
                        "type": anomaly.anomaly_type,
                        "severity": anomaly.severity,
                        "deviation": anomaly.deviation_from_normal,
                        "potential_causes": anomaly.potential_causes
                    }
                    for anomaly in self.detected_anomalies[-10:]  # Last 10 anomalies
                ],
                "model_performance": {
                    model_name: {
                        "accuracy": model_info["accuracy"],
                        "type": model_info["type"]
                    }
                    for model_name, model_info in self.ml_models.items()
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {"error": str(e)}


def create_profiling_analytics_engine(
    aggregation_interval_minutes: int = 5,
    trend_analysis_window_hours: int = 24,
    prediction_horizon_hours: int = 24,
    enable_ml_predictions: bool = True,
    enable_anomaly_detection: bool = True,
    start_analytics: bool = False
) -> ProfilingAnalyticsEngine:
    """
    Factory function to create profiling analytics engine
    
    Args:
        aggregation_interval_minutes: Data aggregation interval
        trend_analysis_window_hours: Window for trend analysis
        prediction_horizon_hours: Prediction time horizon
        enable_ml_predictions: Enable ML-based predictions
        enable_anomaly_detection: Enable anomaly detection
        start_analytics: Start analytics immediately
    
    Returns:
        ProfilingAnalyticsEngine: Configured analytics engine instance
    """
    engine = ProfilingAnalyticsEngine(
        aggregation_interval_minutes=aggregation_interval_minutes,
        trend_analysis_window_hours=trend_analysis_window_hours,
        prediction_horizon_hours=prediction_horizon_hours,
        enable_ml_predictions=enable_ml_predictions,
        enable_anomaly_detection=enable_anomaly_detection
    )
    
    if start_analytics:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(engine.start_analytics())
        except RuntimeError:
            logger.warning("No event loop running, analytics will need to be started manually")
    
    return engine


# Example usage for Creator Economy platform
async def example_profiling_analytics():
    """Example of profiling analytics for Creator Economy"""
    engine = create_profiling_analytics_engine(
        aggregation_interval_minutes=1,  # Fast for demo
        enable_ml_predictions=True,
        enable_anomaly_detection=True,
        start_analytics=True
    )
    
    # Simulate profiling data
    for i in range(50):
        # Create varying data points to simulate trends and anomalies
        base_response_time = 100 + i * 2  # Gradual increase (degrading trend)
        
        # Add some noise and occasional spikes
        if i % 15 == 0:  # Spike every 15 iterations
            response_time = base_response_time * 3
        else:
            response_time = base_response_time + np.random.normal(0, 10)
        
        data_points = [
            ProfilingDataPoint(
                timestamp=datetime.utcnow() - timedelta(minutes=50-i),
                component="creator_dashboard",
                metric_type="response_time",
                value=response_time,
                unit="ms",
                confidence=0.9
            ),
            ProfilingDataPoint(
                timestamp=datetime.utcnow() - timedelta(minutes=50-i),
                component="content_processor",
                metric_type="memory_usage",
                value=60 + i * 0.5,  # Gradual memory increase
                unit="percent",
                confidence=0.95
            )
        ]
        
        await engine.add_profiling_data(data_points)
    
    # Wait for analytics processing
    await asyncio.sleep(5)
    
    # Get analytics report
    report = engine.get_analytics_report()
    
    print("Profiling Analytics Report:")
    print(f"- Total data points: {report['summary']['total_data_points']}")
    print(f"- Active trends: {report['summary']['active_trends']}")
    print(f"- Active predictions: {report['summary']['active_predictions']}")
    print(f"- Optimization recommendations: {report['summary']['active_recommendations']}")
    print(f"- Recent anomalies: {report['summary']['recent_anomalies']}")
    
    print("\nPerformance Trends:")
    for trend in report['performance_trends']:
        print(f"- {trend['component']} {trend['metric_type']}: {trend['direction']} (strength: {trend['strength']:.2f})")
    
    print("\nPredictions:")
    for pred in report['predictions']:
        print(f"- {pred['type']}: {pred['event']} (probability: {pred['probability']:.2f})")
    
    print("\nOptimization Recommendations:")
    for rec in report['optimization_recommendations']:
        print(f"- {rec['title']} ({rec['priority']} priority)")
        print(f"  Expected improvement: {rec['performance_improvement']}")
    
    print("\nRecent Anomalies:")
    for anomaly in report['recent_anomalies']:
        print(f"- {anomaly['component']} {anomaly['metric_type']}: {anomaly['type']} (severity: {anomaly['severity']:.2f})")
    
    await engine.stop_analytics()


if __name__ == "__main__":
    asyncio.run(example_profiling_analytics())