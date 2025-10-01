"""
⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️

Capacity Planning Analyzer Enterprise
Intelligent capacity planning and forecasting for Creator Economy platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import time
import json
import logging
import statistics
import math
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import deque, defaultdict, Counter
import threading
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

# ML and forecasting imports
try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.metrics import mean_squared_error, r2_score
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    from scipy import stats
    import scipy.optimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Prometheus metrics
from prometheus_client import Gauge, Counter, Histogram

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    WORKERS = "workers"

class GrowthPattern(Enum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    SEASONAL = "seasonal"
    POLYNOMIAL = "polynomial"
    CUSTOM = "custom"

class ScalingRecommendation(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    OPTIMIZE = "optimize"
    MAINTAIN = "maintain"

@dataclass
class CapacityMetrics:
    """Capacity utilization metrics"""
    timestamp: datetime
    resource_type: ResourceType
    resource_name: str
    current_utilization: float  # 0.0 to 1.0
    peak_utilization: float
    average_utilization: float
    capacity_limit: float
    available_capacity: float
    growth_rate: Optional[float] = None
    seasonal_factor: Optional[float] = None

@dataclass
class GrowthForecast:
    """Resource growth forecast"""
    resource_type: ResourceType
    resource_name: str
    forecast_horizon_days: int
    growth_pattern: GrowthPattern
    projected_utilization: List[float]
    confidence_intervals: List[Tuple[float, float]]
    capacity_exhaustion_date: Optional[datetime]
    required_scaling_actions: List[ScalingRecommendation]
    cost_projections: Dict[str, float]
    model_accuracy: float

@dataclass
class ScalingPlan:
    """Resource scaling plan"""
    plan_id: str
    resource_type: ResourceType
    resource_name: str
    current_capacity: float
    recommended_capacity: float
    scaling_action: ScalingRecommendation
    urgency_level: str  # low, medium, high, critical
    implementation_timeline: str
    estimated_cost: float
    cost_savings: Optional[float]
    business_justification: str
    technical_requirements: List[str]
    risk_assessment: Dict[str, str]
    success_metrics: List[str]

@dataclass
class CreatorWorkloadPattern:
    """Creator workload pattern analysis"""
    creator_segment: str  # individual, small_team, enterprise
    avg_content_volume: float
    peak_processing_hours: List[int]
    seasonal_patterns: Dict[str, float]
    resource_consumption: Dict[ResourceType, float]
    growth_trajectory: float

class CapacityPlanningAnalyzer:
    """
    Enterprise Capacity Planning Analyzer
    AI-powered capacity forecasting and optimization for Creator Economy platform
    Predicts resource needs and provides intelligent scaling recommendations
    """
    
    def __init__(self,
                 forecasting_horizon_days: int = 90,
                 analysis_interval: int = 3600,  # 1 hour
                 enable_ml_forecasting: bool = True,
                 enable_cost_optimization: bool = True,
                 confidence_level: float = 0.95):
        
        self.forecasting_horizon_days = forecasting_horizon_days
        self.analysis_interval = analysis_interval
        self.enable_ml_forecasting = enable_ml_forecasting and SKLEARN_AVAILABLE
        self.enable_cost_optimization = enable_cost_optimization
        self.confidence_level = confidence_level
        
        # Data storage
        self.capacity_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.growth_forecasts: Dict[str, GrowthForecast] = {}
        self.scaling_plans: Dict[str, ScalingPlan] = {}
        self.creator_workload_patterns: Dict[str, CreatorWorkloadPattern] = {}
        
        # Forecasting models
        self.forecasting_models: Dict[str, Any] = {}
        self.model_accuracy_scores: Dict[str, float] = {}
        
        # Analysis state
        self.analysis_active = False
        self.analysis_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        # Capacity thresholds
        self.capacity_thresholds = {
            ResourceType.CPU: {'warning': 0.7, 'critical': 0.85, 'maximum': 0.95},
            ResourceType.MEMORY: {'warning': 0.75, 'critical': 0.9, 'maximum': 0.98},
            ResourceType.STORAGE: {'warning': 0.8, 'critical': 0.9, 'maximum': 0.95},
            ResourceType.NETWORK: {'warning': 0.6, 'critical': 0.8, 'maximum': 0.9},
            ResourceType.DATABASE: {'warning': 0.7, 'critical': 0.85, 'maximum': 0.95},
            ResourceType.CACHE: {'warning': 0.8, 'critical': 0.9, 'maximum': 0.95},
            ResourceType.QUEUE: {'warning': 0.7, 'critical': 0.85, 'maximum': 0.95},
            ResourceType.WORKERS: {'warning': 0.8, 'critical': 0.9, 'maximum': 0.95}
        }
        
        # Cost models (simplified)
        self.cost_models = {
            ResourceType.CPU: {'base_cost_per_core': 50, 'scaling_factor': 1.2},
            ResourceType.MEMORY: {'base_cost_per_gb': 10, 'scaling_factor': 1.1},
            ResourceType.STORAGE: {'base_cost_per_gb': 0.1, 'scaling_factor': 1.05},
            ResourceType.NETWORK: {'base_cost_per_gbps': 100, 'scaling_factor': 1.15},
            ResourceType.DATABASE: {'base_cost_per_connection': 5, 'scaling_factor': 1.3},
        }
        
        # Initialize Prometheus metrics
        self._init_prometheus_metrics()
        
        # Initialize Creator Economy patterns
        self._init_creator_patterns()
        
        logger.info("CapacityPlanningAnalyzer initialized")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.capacity_utilization = Gauge(
            'capacity_utilization_ratio',
            'Resource capacity utilization ratio',
            ['resource_type', 'resource_name']
        )
        
        self.capacity_forecast = Gauge(
            'capacity_forecast_utilization',
            'Forecasted capacity utilization',
            ['resource_type', 'resource_name', 'forecast_days']
        )
        
        self.capacity_exhaustion_days = Gauge(
            'capacity_exhaustion_days',
            'Days until capacity exhaustion',
            ['resource_type', 'resource_name']
        )
        
        self.scaling_recommendations_total = Counter(
            'scaling_recommendations_total',
            'Total scaling recommendations generated',
            ['resource_type', 'scaling_action', 'urgency']
        )
        
        self.capacity_planning_accuracy = Gauge(
            'capacity_planning_model_accuracy',
            'Capacity planning model accuracy score',
            ['resource_type', 'model_type']
        )
        
        self.cost_projections = Gauge(
            'capacity_cost_projections_usd',
            'Projected capacity costs in USD',
            ['resource_type', 'projection_period']
        )
    
    def _init_creator_patterns(self):
        """Initialize Creator Economy workload patterns"""
        # Define typical creator workload patterns
        self.creator_workload_patterns = {
            'individual_creator': CreatorWorkloadPattern(
                creator_segment='individual',
                avg_content_volume=10.0,  # items per day
                peak_processing_hours=[18, 19, 20, 21],  # Evening hours
                seasonal_patterns={'summer': 1.2, 'winter': 0.8, 'holidays': 1.5},
                resource_consumption={
                    ResourceType.CPU: 0.3,
                    ResourceType.MEMORY: 0.4,
                    ResourceType.STORAGE: 0.2,
                    ResourceType.NETWORK: 0.25
                },
                growth_trajectory=0.15  # 15% monthly growth
            ),
            'small_team': CreatorWorkloadPattern(
                creator_segment='small_team',
                avg_content_volume=50.0,
                peak_processing_hours=[9, 10, 14, 15, 20, 21],
                seasonal_patterns={'summer': 1.1, 'winter': 0.9, 'holidays': 1.3},
                resource_consumption={
                    ResourceType.CPU: 0.5,
                    ResourceType.MEMORY: 0.6,
                    ResourceType.STORAGE: 0.4,
                    ResourceType.NETWORK: 0.45
                },
                growth_trajectory=0.25  # 25% monthly growth
            ),
            'enterprise_creator': CreatorWorkloadPattern(
                creator_segment='enterprise',
                avg_content_volume=200.0,
                peak_processing_hours=[8, 9, 10, 13, 14, 15, 16],
                seasonal_patterns={'summer': 1.05, 'winter': 0.95, 'holidays': 1.2},
                resource_consumption={
                    ResourceType.CPU: 0.8,
                    ResourceType.MEMORY: 0.85,
                    ResourceType.STORAGE: 0.7,
                    ResourceType.NETWORK: 0.75
                },
                growth_trajectory=0.35  # 35% monthly growth
            )
        }
    
    async def start_analysis(self):
        """Start capacity planning analysis"""
        if self.analysis_active:
            logger.warning("Capacity planning analysis already active")
            return
        
        self.analysis_active = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        logger.info("Capacity planning analysis started")
    
    async def stop_analysis(self):
        """Stop capacity planning analysis"""
        self.analysis_active = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=30)
        
        logger.info("Capacity planning analysis stopped")
    
    def _analysis_loop(self):
        """Main capacity planning analysis loop"""
        while self.analysis_active:
            try:
                # Analyze current capacity utilization
                self._analyze_current_capacity()
                
                # Generate growth forecasts
                self._generate_growth_forecasts()
                
                # Create scaling plans
                self._create_scaling_plans()
                
                # Analyze creator workload patterns
                self._analyze_creator_workloads()
                
                # Update Prometheus metrics
                self._update_prometheus_metrics()
                
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Error in capacity planning analysis loop: {e}")
                time.sleep(self.analysis_interval)
    
    def ingest_capacity_metric(self,
                             resource_type: ResourceType,
                             resource_name: str,
                             current_utilization: float,
                             capacity_limit: float,
                             metadata: Optional[Dict[str, Any]] = None):
        """Ingest capacity utilization metric"""
        
        # Calculate derived metrics
        available_capacity = capacity_limit - (current_utilization * capacity_limit)
        
        # Get historical data for peak and average calculation
        metric_key = f"{resource_type.value}_{resource_name}"
        historical_data = list(self.capacity_metrics[metric_key])
        
        if historical_data:
            recent_utilizations = [m.current_utilization for m in historical_data[-24:]]  # Last 24 points
            peak_utilization = max(recent_utilizations + [current_utilization])
            average_utilization = statistics.mean(recent_utilizations + [current_utilization])
        else:
            peak_utilization = current_utilization
            average_utilization = current_utilization
        
        # Create capacity metrics
        metrics = CapacityMetrics(
            timestamp=datetime.utcnow(),
            resource_type=resource_type,
            resource_name=resource_name,
            current_utilization=current_utilization,
            peak_utilization=peak_utilization,
            average_utilization=average_utilization,
            capacity_limit=capacity_limit,
            available_capacity=available_capacity,
            growth_rate=self._calculate_growth_rate(metric_key),
            seasonal_factor=self._calculate_seasonal_factor(resource_type, resource_name)
        )
        
        # Store metrics
        self.capacity_metrics[metric_key].append(metrics)
        
        # Update Prometheus metrics
        self.capacity_utilization.labels(
            resource_type=resource_type.value,
            resource_name=resource_name
        ).set(current_utilization)
    
    def _calculate_growth_rate(self, metric_key: str) -> Optional[float]:
        """Calculate growth rate for resource utilization"""
        if metric_key not in self.capacity_metrics:
            return None
        
        historical_data = list(self.capacity_metrics[metric_key])
        if len(historical_data) < 10:  # Need sufficient data
            return None
        
        try:
            # Calculate growth rate over last week (168 hours at hourly intervals)
            recent_data = historical_data[-168:] if len(historical_data) >= 168 else historical_data
            
            if len(recent_data) < 2:
                return None
            
            # Simple linear growth rate calculation
            values = [m.current_utilization for m in recent_data]
            x = list(range(len(values)))
            
            if SCIPY_AVAILABLE:
                slope, _, _, _, _ = stats.linregress(x, values)
                # Convert to percentage growth per day
                growth_rate = slope * 24  # 24 hours per day
                return growth_rate
            else:
                # Simple growth calculation
                if len(values) >= 2:
                    return (values[-1] - values[0]) / len(values) * 24
        
        except Exception as e:
            logger.error(f"Error calculating growth rate for {metric_key}: {e}")
        
        return None
    
    def _calculate_seasonal_factor(self, resource_type: ResourceType, resource_name: str) -> Optional[float]:
        """Calculate seasonal adjustment factor"""
        current_time = datetime.utcnow()
        current_hour = current_time.hour
        current_month = current_time.month
        
        # Determine seasonal patterns based on Creator Economy workflows
        seasonal_factor = 1.0
        
        # Daily patterns
        peak_hours = [9, 10, 14, 15, 20, 21]  # General peak hours
        if current_hour in peak_hours:
            seasonal_factor *= 1.2
        elif current_hour in [2, 3, 4, 5]:  # Night hours
            seasonal_factor *= 0.6
        
        # Monthly patterns
        if current_month in [6, 7, 8]:  # Summer
            seasonal_factor *= 1.1
        elif current_month in [11, 12, 1]:  # Holiday season
            seasonal_factor *= 1.3
        elif current_month in [1, 2]:  # Post-holiday
            seasonal_factor *= 0.8
        
        return seasonal_factor
    
    def _analyze_current_capacity(self):
        """Analyze current capacity utilization across all resources"""
        for metric_key, metrics_history in self.capacity_metrics.items():
            if not metrics_history:
                continue
            
            latest_metrics = metrics_history[-1]
            
            # Check capacity thresholds
            resource_type = latest_metrics.resource_type
            thresholds = self.capacity_thresholds.get(resource_type, {})
            
            current_utilization = latest_metrics.current_utilization
            
            if current_utilization >= thresholds.get('critical', 0.9):
                logger.warning(f"Critical capacity utilization: {metric_key} at {current_utilization:.2%}")
            elif current_utilization >= thresholds.get('warning', 0.8):
                logger.info(f"Warning capacity utilization: {metric_key} at {current_utilization:.2%}")
    
    def _generate_growth_forecasts(self):
        """Generate growth forecasts for all resources"""
        for metric_key, metrics_history in self.capacity_metrics.items():
            if len(metrics_history) < 50:  # Need sufficient data for forecasting
                continue
            
            try:
                latest_metrics = metrics_history[-1]
                forecast = self._create_resource_forecast(
                    latest_metrics.resource_type,
                    latest_metrics.resource_name,
                    list(metrics_history)
                )
                
                if forecast:
                    self.growth_forecasts[metric_key] = forecast
                    
                    # Update Prometheus metrics
                    if forecast.projected_utilization:
                        for i, projected in enumerate([7, 30, 90]):  # 7, 30, 90 day forecasts
                            if i < len(forecast.projected_utilization):
                                self.capacity_forecast.labels(
                                    resource_type=forecast.resource_type.value,
                                    resource_name=forecast.resource_name,
                                    forecast_days=str(projected)
                                ).set(forecast.projected_utilization[i])
                    
                    if forecast.capacity_exhaustion_date:
                        days_to_exhaustion = (forecast.capacity_exhaustion_date - datetime.utcnow()).days
                        self.capacity_exhaustion_days.labels(
                            resource_type=forecast.resource_type.value,
                            resource_name=forecast.resource_name
                        ).set(max(days_to_exhaustion, 0))
            
            except Exception as e:
                logger.error(f"Error generating forecast for {metric_key}: {e}")
    
    def _create_resource_forecast(self,
                                resource_type: ResourceType,
                                resource_name: str,
                                metrics_history: List[CapacityMetrics]) -> Optional[GrowthForecast]:
        """Create growth forecast for a specific resource"""
        
        if not self.enable_ml_forecasting or len(metrics_history) < 30:
            return None
        
        try:
            # Prepare data for forecasting
            timestamps = [m.timestamp for m in metrics_history]
            utilizations = [m.current_utilization for m in metrics_history]
            
            # Determine growth pattern
            growth_pattern = self._identify_growth_pattern(utilizations)
            
            # Generate forecast based on pattern
            if growth_pattern == GrowthPattern.LINEAR:
                forecast_data = self._linear_forecast(timestamps, utilizations)
            elif growth_pattern == GrowthPattern.EXPONENTIAL:
                forecast_data = self._exponential_forecast(timestamps, utilizations)
            elif growth_pattern == GrowthPattern.SEASONAL:
                forecast_data = self._seasonal_forecast(timestamps, utilizations)
            else:
                forecast_data = self._polynomial_forecast(timestamps, utilizations)
            
            if not forecast_data:
                return None
            
            projected_utilization, confidence_intervals, model_accuracy = forecast_data
            
            # Calculate capacity exhaustion date
            exhaustion_date = self._calculate_exhaustion_date(
                timestamps, projected_utilization, 
                self.capacity_thresholds[resource_type]['maximum']
            )
            
            # Generate scaling recommendations
            scaling_actions = self._generate_scaling_recommendations(
                resource_type, projected_utilization, exhaustion_date
            )
            
            # Calculate cost projections
            cost_projections = self._calculate_cost_projections(
                resource_type, metrics_history[-1].capacity_limit, projected_utilization
            )
            
            return GrowthForecast(
                resource_type=resource_type,
                resource_name=resource_name,
                forecast_horizon_days=self.forecasting_horizon_days,
                growth_pattern=growth_pattern,
                projected_utilization=projected_utilization,
                confidence_intervals=confidence_intervals,
                capacity_exhaustion_date=exhaustion_date,
                required_scaling_actions=scaling_actions,
                cost_projections=cost_projections,
                model_accuracy=model_accuracy
            )
        
        except Exception as e:
            logger.error(f"Error creating forecast for {resource_name}: {e}")
            return None
    
    def _identify_growth_pattern(self, utilizations: List[float]) -> GrowthPattern:
        """Identify the growth pattern in utilization data"""
        if len(utilizations) < 10:
            return GrowthPattern.LINEAR
        
        try:
            # Test for different patterns
            x = np.array(range(len(utilizations)))
            y = np.array(utilizations)
            
            # Linear regression
            linear_model = LinearRegression().fit(x.reshape(-1, 1), y)
            linear_score = linear_model.score(x.reshape(-1, 1), y)
            
            # Polynomial regression (degree 2)
            poly_features = PolynomialFeatures(degree=2)
            x_poly = poly_features.fit_transform(x.reshape(-1, 1))
            poly_model = LinearRegression().fit(x_poly, y)
            poly_score = poly_model.score(x_poly, y)
            
            # Simple pattern detection
            if poly_score > linear_score + 0.1:
                return GrowthPattern.POLYNOMIAL
            elif linear_score > 0.8:
                return GrowthPattern.LINEAR
            else:
                # Check for seasonality (simplified)
                if len(utilizations) >= 24:  # At least 24 hours of data
                    hourly_avg = []
                    for hour in range(24):
                        hour_values = [utilizations[i] for i in range(hour, len(utilizations), 24)]
                        if hour_values:
                            hourly_avg.append(statistics.mean(hour_values))
                    
                    if hourly_avg and statistics.stdev(hourly_avg) > 0.1:
                        return GrowthPattern.SEASONAL
                
                return GrowthPattern.LINEAR
        
        except Exception:
            return GrowthPattern.LINEAR
    
    def _linear_forecast(self, timestamps: List[datetime], utilizations: List[float]) -> Optional[Tuple[List[float], List[Tuple[float, float]], float]]:
        """Generate linear forecast"""
        if not SKLEARN_AVAILABLE:
            return None
        
        try:
            # Convert timestamps to numeric values (hours since start)
            start_time = timestamps[0]
            x = np.array([(ts - start_time).total_seconds() / 3600 for ts in timestamps])
            y = np.array(utilizations)
            
            # Fit linear model
            model = LinearRegression()
            model.fit(x.reshape(-1, 1), y)
            
            # Generate forecast points
            forecast_hours = np.arange(x[-1], x[-1] + self.forecasting_horizon_days * 24, 24)
            projected_utilization = model.predict(forecast_hours.reshape(-1, 1))
            
            # Calculate confidence intervals (simplified)
            y_pred = model.predict(x.reshape(-1, 1))
            mse = mean_squared_error(y, y_pred)
            std_error = math.sqrt(mse)
            
            confidence_intervals = [
                (max(0, proj - 1.96 * std_error), min(1, proj + 1.96 * std_error))
                for proj in projected_utilization
            ]
            
            # Model accuracy
            accuracy = model.score(x.reshape(-1, 1), y)
            
            return projected_utilization.tolist(), confidence_intervals, accuracy
        
        except Exception as e:
            logger.error(f"Error in linear forecast: {e}")
            return None
    
    def _exponential_forecast(self, timestamps: List[datetime], utilizations: List[float]) -> Optional[Tuple[List[float], List[Tuple[float, float]], float]]:
        """Generate exponential forecast"""
        # Simplified exponential forecasting
        try:
            if len(utilizations) < 5:
                return None
            
            # Calculate growth rate
            recent_values = utilizations[-10:]
            if recent_values[0] > 0:
                growth_rate = (recent_values[-1] / recent_values[0]) ** (1/len(recent_values)) - 1
            else:
                growth_rate = 0.1  # Default 10% growth
            
            # Project future values
            current_value = utilizations[-1]
            projected_utilization = []
            
            for day in range(self.forecasting_horizon_days):
                projected_value = current_value * ((1 + growth_rate) ** day)
                projected_utilization.append(min(projected_value, 1.0))  # Cap at 100%
            
            # Simple confidence intervals
            confidence_intervals = [
                (max(0, proj * 0.8), min(1, proj * 1.2))
                for proj in projected_utilization
            ]
            
            # Simplified accuracy calculation
            accuracy = 0.7  # Default accuracy for exponential model
            
            return projected_utilization, confidence_intervals, accuracy
        
        except Exception as e:
            logger.error(f"Error in exponential forecast: {e}")
            return None
    
    def _seasonal_forecast(self, timestamps: List[datetime], utilizations: List[float]) -> Optional[Tuple[List[float], List[Tuple[float, float]], float]]:
        """Generate seasonal forecast"""
        # Simplified seasonal forecasting
        try:
            if len(utilizations) < 48:  # Need at least 2 days of hourly data
                return None
            
            # Calculate hourly averages
            hourly_patterns = defaultdict(list)
            for i, (ts, util) in enumerate(zip(timestamps, utilizations)):
                hourly_patterns[ts.hour].append(util)
            
            hourly_averages = {
                hour: statistics.mean(values)
                for hour, values in hourly_patterns.items()
            }
            
            # Generate forecast
            projected_utilization = []
            current_time = timestamps[-1]
            
            for day in range(self.forecasting_horizon_days):
                future_time = current_time + timedelta(days=day)
                hour_avg = hourly_averages.get(future_time.hour, utilizations[-1])
                
                # Apply trend
                trend_factor = 1 + (day * 0.001)  # 0.1% daily growth
                projected_value = hour_avg * trend_factor
                projected_utilization.append(min(projected_value, 1.0))
            
            # Confidence intervals
            confidence_intervals = [
                (max(0, proj * 0.9), min(1, proj * 1.1))
                for proj in projected_utilization
            ]
            
            accuracy = 0.8  # Good accuracy for seasonal patterns
            
            return projected_utilization, confidence_intervals, accuracy
        
        except Exception as e:
            logger.error(f"Error in seasonal forecast: {e}")
            return None
    
    def _polynomial_forecast(self, timestamps: List[datetime], utilizations: List[float]) -> Optional[Tuple[List[float], List[Tuple[float, float]], float]]:
        """Generate polynomial forecast"""
        if not SKLEARN_AVAILABLE:
            return None
        
        try:
            # Convert timestamps to numeric values
            start_time = timestamps[0]
            x = np.array([(ts - start_time).total_seconds() / 3600 for ts in timestamps])
            y = np.array(utilizations)
            
            # Fit polynomial model (degree 2)
            poly_features = PolynomialFeatures(degree=2)
            x_poly = poly_features.fit_transform(x.reshape(-1, 1))
            model = LinearRegression()
            model.fit(x_poly, y)
            
            # Generate forecast
            forecast_hours = np.arange(x[-1], x[-1] + self.forecasting_horizon_days * 24, 24)
            forecast_poly = poly_features.transform(forecast_hours.reshape(-1, 1))
            projected_utilization = model.predict(forecast_poly)
            
            # Ensure values are in valid range
            projected_utilization = np.clip(projected_utilization, 0, 1)
            
            # Calculate confidence intervals
            y_pred = model.predict(x_poly)
            mse = mean_squared_error(y, y_pred)
            std_error = math.sqrt(mse)
            
            confidence_intervals = [
                (max(0, proj - 1.96 * std_error), min(1, proj + 1.96 * std_error))
                for proj in projected_utilization
            ]
            
            # Model accuracy
            accuracy = model.score(x_poly, y)
            
            return projected_utilization.tolist(), confidence_intervals, accuracy
        
        except Exception as e:
            logger.error(f"Error in polynomial forecast: {e}")
            return None
    
    def _calculate_exhaustion_date(self,
                                 timestamps: List[datetime],
                                 projected_utilization: List[float],
                                 threshold: float) -> Optional[datetime]:
        """Calculate when capacity will be exhausted"""
        try:
            for i, utilization in enumerate(projected_utilization):
                if utilization >= threshold:
                    # Capacity will be exhausted on this day
                    exhaustion_date = timestamps[-1] + timedelta(days=i)
                    return exhaustion_date
            
            return None  # Capacity not exhausted within forecast period
        
        except Exception:
            return None
    
    def _generate_scaling_recommendations(self,
                                        resource_type: ResourceType,
                                        projected_utilization: List[float],
                                        exhaustion_date: Optional[datetime]) -> List[ScalingRecommendation]:
        """Generate scaling recommendations based on forecast"""
        recommendations = []
        
        if not projected_utilization:
            return recommendations
        
        # Check near-term projections (next 7 days)
        near_term = projected_utilization[:7] if len(projected_utilization) >= 7 else projected_utilization
        max_near_term = max(near_term) if near_term else 0
        
        thresholds = self.capacity_thresholds.get(resource_type, {})
        warning_threshold = thresholds.get('warning', 0.8)
        critical_threshold = thresholds.get('critical', 0.9)
        
        if max_near_term >= critical_threshold:
            recommendations.append(ScalingRecommendation.SCALE_UP)
        elif max_near_term >= warning_threshold:
            recommendations.append(ScalingRecommendation.SCALE_OUT)
        
        # Check if resource is consistently under-utilized
        if all(util < 0.3 for util in near_term):
            recommendations.append(ScalingRecommendation.SCALE_DOWN)
        
        # Check for optimization opportunities
        if max_near_term > warning_threshold and any(util < 0.5 for util in near_term):
            recommendations.append(ScalingRecommendation.OPTIMIZE)
        
        # Emergency scaling if exhaustion is imminent
        if exhaustion_date and (exhaustion_date - datetime.utcnow()).days <= 7:
            recommendations.insert(0, ScalingRecommendation.SCALE_UP)
        
        return recommendations if recommendations else [ScalingRecommendation.MAINTAIN]
    
    def _calculate_cost_projections(self,
                                  resource_type: ResourceType,
                                  current_capacity: float,
                                  projected_utilization: List[float]) -> Dict[str, float]:
        """Calculate cost projections for scaling scenarios"""
        cost_model = self.cost_models.get(resource_type, {})
        base_cost = cost_model.get('base_cost_per_core', 50)
        scaling_factor = cost_model.get('scaling_factor', 1.2)
        
        projections = {}
        
        try:
            # Current cost
            current_cost = current_capacity * base_cost
            projections['current_monthly'] = current_cost * 30
            
            # Projected costs based on utilization
            if projected_utilization:
                # 30-day projection
                avg_30_day = statistics.mean(projected_utilization[:30]) if len(projected_utilization) >= 30 else statistics.mean(projected_utilization)
                required_capacity_30 = current_capacity * avg_30_day / 0.8  # Target 80% utilization
                projections['projected_30_day'] = required_capacity_30 * base_cost * scaling_factor
                
                # 90-day projection
                if len(projected_utilization) >= 90:
                    avg_90_day = statistics.mean(projected_utilization[:90])
                    required_capacity_90 = current_capacity * avg_90_day / 0.8
                    projections['projected_90_day'] = required_capacity_90 * base_cost * scaling_factor
                
                # Cost savings from optimization
                if avg_30_day < 0.5:  # Under-utilized
                    optimized_capacity = current_capacity * 0.7  # 30% reduction
                    projections['optimization_savings'] = (current_cost - optimized_capacity * base_cost) * 30
        
        except Exception as e:
            logger.error(f"Error calculating cost projections: {e}")
        
        return projections
    
    def _create_scaling_plans(self):
        """Create detailed scaling plans based on forecasts"""
        for resource_key, forecast in self.growth_forecasts.items():
            try:
                # Get current capacity metrics
                if resource_key not in self.capacity_metrics or not self.capacity_metrics[resource_key]:
                    continue
                
                current_metrics = self.capacity_metrics[resource_key][-1]
                
                # Determine if scaling plan is needed
                scaling_actions = forecast.required_scaling_actions
                if ScalingRecommendation.MAINTAIN in scaling_actions:
                    continue
                
                # Create scaling plan
                plan_id = f"plan_{resource_key}_{int(time.time())}"
                
                primary_action = scaling_actions[0] if scaling_actions else ScalingRecommendation.MAINTAIN
                
                # Calculate recommended capacity
                if primary_action == ScalingRecommendation.SCALE_UP:
                    recommended_capacity = current_metrics.capacity_limit * 1.5
                    urgency = "high" if forecast.capacity_exhaustion_date and \
                             (forecast.capacity_exhaustion_date - datetime.utcnow()).days <= 7 else "medium"
                elif primary_action == ScalingRecommendation.SCALE_OUT:
                    recommended_capacity = current_metrics.capacity_limit * 1.2
                    urgency = "medium"
                elif primary_action == ScalingRecommendation.SCALE_DOWN:
                    recommended_capacity = current_metrics.capacity_limit * 0.7
                    urgency = "low"
                else:
                    recommended_capacity = current_metrics.capacity_limit
                    urgency = "low"
                
                # Calculate costs
                cost_projections = forecast.cost_projections
                estimated_cost = cost_projections.get('projected_30_day', 0) - cost_projections.get('current_monthly', 0)
                cost_savings = cost_projections.get('optimization_savings', 0) if primary_action == ScalingRecommendation.SCALE_DOWN else None
                
                scaling_plan = ScalingPlan(
                    plan_id=plan_id,
                    resource_type=forecast.resource_type,
                    resource_name=forecast.resource_name,
                    current_capacity=current_metrics.capacity_limit,
                    recommended_capacity=recommended_capacity,
                    scaling_action=primary_action,
                    urgency_level=urgency,
                    implementation_timeline=self._calculate_implementation_timeline(primary_action, urgency),
                    estimated_cost=estimated_cost,
                    cost_savings=cost_savings,
                    business_justification=self._generate_business_justification(forecast, primary_action),
                    technical_requirements=self._generate_technical_requirements(forecast.resource_type, primary_action),
                    risk_assessment=self._assess_scaling_risks(forecast, primary_action),
                    success_metrics=self._define_success_metrics(forecast.resource_type, primary_action)
                )
                
                self.scaling_plans[plan_id] = scaling_plan
                
                # Update Prometheus metrics
                self.scaling_recommendations_total.labels(
                    resource_type=forecast.resource_type.value,
                    scaling_action=primary_action.value,
                    urgency=urgency
                ).inc()
            
            except Exception as e:
                logger.error(f"Error creating scaling plan for {resource_key}: {e}")
    
    def _calculate_implementation_timeline(self, action: ScalingRecommendation, urgency: str) -> str:
        """Calculate implementation timeline for scaling action"""
        if urgency == "critical":
            return "Immediate (within 24 hours)"
        elif urgency == "high":
            return "Within 1 week"
        elif urgency == "medium":
            return "Within 2-4 weeks"
        else:
            return "Within 1-3 months"
    
    def _generate_business_justification(self, forecast: GrowthForecast, action: ScalingRecommendation) -> str:
        """Generate business justification for scaling action"""
        if action == ScalingRecommendation.SCALE_UP:
            return f"Prevent capacity exhaustion projected for {forecast.capacity_exhaustion_date}. " \
                   f"Ensure continued creator platform performance and user experience."
        elif action == ScalingRecommendation.SCALE_OUT:
            return "Distribute load to improve performance and resilience. " \
                   "Support growing creator base and content processing demands."
        elif action == ScalingRecommendation.SCALE_DOWN:
            return f"Optimize costs by reducing over-provisioned resources. " \
                   f"Projected savings: ${forecast.cost_projections.get('optimization_savings', 0):.2f}/month"
        elif action == ScalingRecommendation.OPTIMIZE:
            return "Improve resource efficiency without capacity changes. " \
                   "Enhance performance through configuration optimization."
        else:
            return "Maintain current capacity levels. Resource utilization within acceptable ranges."
    
    def _generate_technical_requirements(self, resource_type: ResourceType, action: ScalingRecommendation) -> List[str]:
        """Generate technical requirements for scaling action"""
        requirements = []
        
        if action in [ScalingRecommendation.SCALE_UP, ScalingRecommendation.SCALE_OUT]:
            requirements.extend([
                "Infrastructure provisioning approval",
                "Load balancer configuration updates",
                "Monitoring system updates",
                "Deployment pipeline modifications"
            ])
            
            if resource_type == ResourceType.DATABASE:
                requirements.extend([
                    "Database replica setup",
                    "Connection pool configuration",
                    "Query optimization review"
                ])
            elif resource_type == ResourceType.CPU:
                requirements.extend([
                    "Container orchestration updates",
                    "Auto-scaling policy adjustments",
                    "Performance baseline establishment"
                ])
        
        elif action == ScalingRecommendation.SCALE_DOWN:
            requirements.extend([
                "Gradual capacity reduction plan",
                "Performance monitoring during reduction",
                "Rollback procedures preparation"
            ])
        
        return requirements
    
    def _assess_scaling_risks(self, forecast: GrowthForecast, action: ScalingRecommendation) -> Dict[str, str]:
        """Assess risks associated with scaling action"""
        risks = {}
        
        if action == ScalingRecommendation.SCALE_UP:
            risks.update({
                "cost_risk": "High - Significant cost increase",
                "implementation_risk": "Medium - Complex infrastructure changes",
                "performance_risk": "Low - Improved performance expected"
            })
        elif action == ScalingRecommendation.SCALE_DOWN:
            risks.update({
                "cost_risk": "Low - Cost reduction",
                "implementation_risk": "Medium - Careful capacity reduction needed",
                "performance_risk": "Medium - Potential performance impact"
            })
        elif action == ScalingRecommendation.OPTIMIZE:
            risks.update({
                "cost_risk": "Low - No significant cost impact",
                "implementation_risk": "Low - Configuration changes only",
                "performance_risk": "Low - Performance improvement expected"
            })
        
        # Add forecast-specific risks
        if forecast.model_accuracy < 0.8:
            risks["forecast_risk"] = "Medium - Lower forecast accuracy"
        
        return risks
    
    def _define_success_metrics(self, resource_type: ResourceType, action: ScalingRecommendation) -> List[str]:
        """Define success metrics for scaling action"""
        metrics = [
            "Resource utilization within target range (70-85%)",
            "No capacity-related performance degradation",
            "Cost efficiency maintained or improved"
        ]
        
        if resource_type == ResourceType.CPU:
            metrics.extend([
                "API response times within SLA",
                "Content processing times improved",
                "Creator workflow performance maintained"
            ])
        elif resource_type == ResourceType.MEMORY:
            metrics.extend([
                "Memory leak incidents reduced",
                "Garbage collection overhead minimized",
                "Application stability improved"
            ])
        elif resource_type == ResourceType.DATABASE:
            metrics.extend([
                "Query response times improved",
                "Connection pool efficiency optimized",
                "Database deadlocks reduced"
            ])
        
        return metrics
    
    def _analyze_creator_workloads(self):
        """Analyze Creator Economy specific workload patterns"""
        # This would analyze creator-specific metrics and update workload patterns
        # For now, we'll use the pre-defined patterns and update them based on actual data
        
        for pattern_name, pattern in self.creator_workload_patterns.items():
            # Update patterns based on actual resource consumption data
            # This is a simplified implementation
            pass
    
    def _update_prometheus_metrics(self):
        """Update Prometheus metrics"""
        # Update capacity planning model accuracy
        for resource_key, forecast in self.growth_forecasts.items():
            self.capacity_planning_accuracy.labels(
                resource_type=forecast.resource_type.value,
                model_type=forecast.growth_pattern.value
            ).set(forecast.model_accuracy)
        
        # Update cost projections
        total_current_cost = 0
        total_projected_cost = 0
        
        for forecast in self.growth_forecasts.values():
            current_cost = forecast.cost_projections.get('current_monthly', 0)
            projected_cost = forecast.cost_projections.get('projected_30_day', 0)
            
            total_current_cost += current_cost
            total_projected_cost += projected_cost
            
            self.cost_projections.labels(
                resource_type=forecast.resource_type.value,
                projection_period='30_day'
            ).set(projected_cost)
        
        # Update overall cost projection
        self.cost_projections.labels(
            resource_type='total',
            projection_period='30_day'
        ).set(total_projected_cost)
    
    async def get_capacity_summary(self) -> Dict[str, Any]:
        """Get comprehensive capacity planning summary"""
        current_time = datetime.utcnow()
        
        # Aggregate current utilization
        current_utilization = {}
        for resource_type in ResourceType:
            type_metrics = []
            for metrics_history in self.capacity_metrics.values():
                if metrics_history and metrics_history[-1].resource_type == resource_type:
                    type_metrics.append(metrics_history[-1].current_utilization)
            
            if type_metrics:
                current_utilization[resource_type.value] = {
                    'average': statistics.mean(type_metrics),
                    'maximum': max(type_metrics),
                    'resource_count': len(type_metrics)
                }
        
        # Forecast summary
        forecast_summary = {}
        for resource_key, forecast in self.growth_forecasts.items():
            forecast_summary[resource_key] = {
                'growth_pattern': forecast.growth_pattern.value,
                'model_accuracy': forecast.model_accuracy,
                'capacity_exhaustion_days': (forecast.capacity_exhaustion_date - current_time).days 
                                          if forecast.capacity_exhaustion_date else None,
                'scaling_actions': [action.value for action in forecast.required_scaling_actions]
            }
        
        # Scaling plans summary
        scaling_plans_summary = {}
        for plan_id, plan in self.scaling_plans.items():
            scaling_plans_summary[plan_id] = {
                'resource_type': plan.resource_type.value,
                'resource_name': plan.resource_name,
                'scaling_action': plan.scaling_action.value,
                'urgency': plan.urgency_level,
                'estimated_cost': plan.estimated_cost,
                'implementation_timeline': plan.implementation_timeline
            }
        
        return {
            'summary_timestamp': current_time.isoformat(),
            'current_utilization': current_utilization,
            'forecasts': forecast_summary,
            'scaling_plans': scaling_plans_summary,
            'total_resources_monitored': len(self.capacity_metrics),
            'creator_workload_patterns': {
                name: {
                    'segment': pattern.creator_segment,
                    'growth_trajectory': pattern.growth_trajectory,
                    'avg_content_volume': pattern.avg_content_volume
                }
                for name, pattern in self.creator_workload_patterns.items()
            }
        }
    
    async def get_scaling_recommendations(self, urgency_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get scaling recommendations with optional urgency filter"""
        recommendations = []
        
        for plan_id, plan in self.scaling_plans.items():
            if urgency_filter and plan.urgency_level != urgency_filter:
                continue
            
            recommendations.append({
                'plan_id': plan_id,
                'resource_type': plan.resource_type.value,
                'resource_name': plan.resource_name,
                'current_capacity': plan.current_capacity,
                'recommended_capacity': plan.recommended_capacity,
                'scaling_action': plan.scaling_action.value,
                'urgency_level': plan.urgency_level,
                'estimated_cost': plan.estimated_cost,
                'cost_savings': plan.cost_savings,
                'business_justification': plan.business_justification,
                'implementation_timeline': plan.implementation_timeline,
                'success_metrics': plan.success_metrics
            })
        
        # Sort by urgency and estimated impact
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: (urgency_order.get(x['urgency_level'], 4), -abs(x['estimated_cost'])))
        
        return recommendations