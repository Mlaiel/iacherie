"""📊 Capacity Planning System - Enterprise ML Infrastructure
============================================================
Module: ml/deployment/capacity_planning_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ML INFRASTRUCTURE CAPACITY PLANNING SYSTEM
ML infrastructure capacity planning with predictive scaling
- Demand forecasting and capacity planning
- Creator growth prediction and resource planning
- Cost optimization with future demand
- Multi-dimensional scaling strategies
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from statistics import mean, median

logger = logging.getLogger(__name__)


class CapacityMetric(Enum):
    """Capacity planning metrics"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    GPU_UTILIZATION = "gpu_utilization"
    STORAGE_UTILIZATION = "storage_utilization"
    NETWORK_THROUGHPUT = "network_throughput"
    REQUEST_VOLUME = "request_volume"
    CREATOR_COUNT = "creator_count"
    INFERENCE_LATENCY = "inference_latency"


class ForecastHorizon(Enum):
    """Forecast time horizons"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ScalingDirection(Enum):
    """Scaling directions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    MAINTAIN = "maintain"


class CreatorSegment(Enum):
    """Creator segments for demand modeling"""
    EMERGING = "emerging"
    ESTABLISHED = "established"
    VIRAL = "viral"
    ENTERPRISE = "enterprise"


@dataclass
class CapacityDataPoint:
    """Single capacity measurement"""
    timestamp: datetime
    metric: CapacityMetric
    value: float
    creator_type: Optional[str] = None
    region: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DemandForecast:
    """Demand forecast result"""
    metric: CapacityMetric
    horizon: ForecastHorizon
    forecast_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    trend_direction: str
    seasonality_detected: bool
    accuracy_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CapacityRecommendation:
    """Capacity planning recommendation"""
    recommendation_id: str
    target_metric: CapacityMetric
    scaling_direction: ScalingDirection
    recommended_capacity: float
    current_capacity: float
    expected_cost_impact: float
    priority: int
    reasoning: str
    implementation_timeline: str
    risk_assessment: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorGrowthModel:
    """Creator growth model"""
    creator_type: str
    segment: CreatorSegment
    growth_rate: float
    churn_rate: float
    resource_intensity: float
    predicted_count: List[int]
    confidence_level: float


class CapacityPlanningSystem:
    """Enterprise Capacity Planning System"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
        # Data storage
        self.capacity_data: Dict[CapacityMetric, List[CapacityDataPoint]] = {
            metric: [] for metric in CapacityMetric
        }
        self.demand_forecasts: Dict[str, DemandForecast] = {}
        self.capacity_recommendations: Dict[str, CapacityRecommendation] = {}
        self.creator_models: Dict[str, CreatorGrowthModel] = {}
        
        # Configuration
        self.forecast_accuracy_threshold = self.config.get('forecast_accuracy_threshold', 0.8)
        self.utilization_upper_threshold = self.config.get('utilization_upper_threshold', 0.8)
        self.utilization_lower_threshold = self.config.get('utilization_lower_threshold', 0.3)
        self.cost_optimization_weight = self.config.get('cost_optimization_weight', 0.7)
        
        # Creator-specific parameters
        self.creator_resource_profiles = {
            'musician': {'cpu_weight': 0.6, 'gpu_weight': 1.5, 'storage_weight': 1.2},
            'blogger': {'cpu_weight': 0.8, 'gpu_weight': 0.3, 'storage_weight': 0.7},
            'photographer': {'cpu_weight': 0.7, 'gpu_weight': 1.2, 'storage_weight': 1.5},
            'influencer': {'cpu_weight': 0.9, 'gpu_weight': 0.8, 'storage_weight': 0.9},
            'comedian': {'cpu_weight': 0.8, 'gpu_weight': 0.7, 'storage_weight': 0.8}
        }
        
        # Performance tracking
        self.planning_metrics = {
            'forecasts_generated': 0,
            'recommendations_created': 0,
            'capacity_adjustments': 0,
            'cost_savings_predicted': 0.0,
            'forecast_accuracy_avg': 0.0
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
        
        logger.info("📊 Capacity Planning System initialized")
    
    def _initialize_sample_data(self) -> None:
        """Initialize system with sample historical data"""
        try:
            # Generate sample capacity data for the last 30 days
            base_time = datetime.utcnow() - timedelta(days=30)
            
            for i in range(30 * 24):  # Hourly data for 30 days
                timestamp = base_time + timedelta(hours=i)
                
                # Simulate CPU utilization with daily pattern
                hour_of_day = timestamp.hour
                daily_pattern = 0.3 + 0.4 * np.sin((hour_of_day - 6) * np.pi / 12)
                cpu_util = max(0.1, min(0.9, daily_pattern + np.random.normal(0, 0.1)))
                
                self.capacity_data[CapacityMetric.CPU_UTILIZATION].append(
                    CapacityDataPoint(timestamp, CapacityMetric.CPU_UTILIZATION, cpu_util)
                )
                
                # Simulate memory utilization
                memory_util = max(0.2, min(0.85, cpu_util * 0.8 + np.random.normal(0, 0.05)))
                self.capacity_data[CapacityMetric.MEMORY_UTILIZATION].append(
                    CapacityDataPoint(timestamp, CapacityMetric.MEMORY_UTILIZATION, memory_util)
                )
                
                # Simulate request volume
                base_requests = 1000 + 800 * daily_pattern + np.random.normal(0, 100)
                self.capacity_data[CapacityMetric.REQUEST_VOLUME].append(
                    CapacityDataPoint(timestamp, CapacityMetric.REQUEST_VOLUME, max(0, base_requests))
                )
            
            # Initialize creator growth models
            self._initialize_creator_models()
            
        except Exception as e:
            logger.error(f"❌ Error initializing sample data: {e}")
    
    def _initialize_creator_models(self) -> None:
        """Initialize creator growth models"""
        creator_data = [
            {
                'type': 'musician',
                'segment': CreatorSegment.ESTABLISHED,
                'growth_rate': 0.15,
                'churn_rate': 0.08,
                'resource_intensity': 1.3
            },
            {
                'type': 'blogger',
                'segment': CreatorSegment.EMERGING,
                'growth_rate': 0.25,
                'churn_rate': 0.12,
                'resource_intensity': 0.8
            },
            {
                'type': 'photographer',
                'segment': CreatorSegment.ESTABLISHED,
                'growth_rate': 0.18,
                'churn_rate': 0.10,
                'resource_intensity': 1.2
            },
            {
                'type': 'influencer',
                'segment': CreatorSegment.VIRAL,
                'growth_rate': 0.35,
                'churn_rate': 0.20,
                'resource_intensity': 1.1
            }
        ]
        
        for data in creator_data:
            # Generate predicted counts for next 12 months
            current_count = 1000  # Base count
            predicted_counts = []
            
            for month in range(12):
                growth = data['growth_rate'] * (1 - month * 0.02)  # Diminishing growth
                current_count = int(current_count * (1 + growth - data['churn_rate']))
                predicted_counts.append(current_count)
            
            self.creator_models[data['type']] = CreatorGrowthModel(
                creator_type=data['type'],
                segment=data['segment'],
                growth_rate=data['growth_rate'],
                churn_rate=data['churn_rate'],
                resource_intensity=data['resource_intensity'],
                predicted_count=predicted_counts,
                confidence_level=0.75
            )
    
    async def ingest_capacity_data(
        self,
        data_points: List[CapacityDataPoint]
    ) -> bool:
        """Ingest new capacity data points"""
        try:
            for point in data_points:
                self.capacity_data[point.metric].append(point)
                
                # Keep only recent data (last 90 days)
                cutoff_time = datetime.utcnow() - timedelta(days=90)
                self.capacity_data[point.metric] = [
                    dp for dp in self.capacity_data[point.metric]
                    if dp.timestamp > cutoff_time
                ]
            
            logger.info(f"✅ Ingested {len(data_points)} capacity data points")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error ingesting capacity data: {e}")
            return False
    
    async def generate_demand_forecast(
        self,
        metric: CapacityMetric,
        horizon: ForecastHorizon,
        creator_type: Optional[str] = None
    ) -> Optional[DemandForecast]:
        """Generate demand forecast for specific metric"""
        try:
            # Get historical data
            historical_data = self.capacity_data.get(metric, [])
            
            if creator_type:
                historical_data = [
                    dp for dp in historical_data
                    if dp.creator_type == creator_type
                ]
            
            if len(historical_data) < 24:  # Need at least 24 data points
                logger.warning(f"Insufficient data for forecasting {metric.value}")
                return None
            
            # Sort by timestamp
            historical_data.sort(key=lambda x: x.timestamp)
            values = [dp.value for dp in historical_data]
            
            # Generate forecast based on horizon
            forecast_values, confidence_intervals = await self._generate_forecast(
                values, horizon
            )
            
            # Detect trend and seasonality
            trend_direction = await self._detect_trend(values)
            seasonality_detected = await self._detect_seasonality(values)
            
            # Calculate accuracy (simplified)
            accuracy_score = await self._calculate_forecast_accuracy(values, forecast_values[:len(values)//2])
            
            forecast = DemandForecast(
                metric=metric,
                horizon=horizon,
                forecast_values=forecast_values,
                confidence_intervals=confidence_intervals,
                trend_direction=trend_direction,
                seasonality_detected=seasonality_detected,
                accuracy_score=accuracy_score
            )
            
            forecast_id = f"{metric.value}_{horizon.value}_{creator_type or 'all'}"
            self.demand_forecasts[forecast_id] = forecast
            self.planning_metrics['forecasts_generated'] += 1
            
            logger.info(f"✅ Generated forecast for {metric.value} ({horizon.value})")
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Error generating forecast: {e}")
            return None
    
    async def _generate_forecast(
        self,
        values: List[float],
        horizon: ForecastHorizon
    ) -> Tuple[List[float], List[Tuple[float, float]]]:
        """Generate forecast values with confidence intervals"""
        try:
            # Determine forecast length
            forecast_length = {
                ForecastHorizon.DAILY: 7,
                ForecastHorizon.WEEKLY: 4,
                ForecastHorizon.MONTHLY: 12,
                ForecastHorizon.QUARTERLY: 4,
                ForecastHorizon.YEARLY: 2
            }.get(horizon, 7)
            
            # Simple trend-based forecast
            if len(values) < 2:
                return [values[-1]] * forecast_length, [(values[-1] * 0.9, values[-1] * 1.1)] * forecast_length
            
            # Calculate trend
            recent_values = values[-min(24, len(values)):]  # Last 24 points or all available
            trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
            
            # Generate forecast
            forecast_values = []
            confidence_intervals = []
            last_value = values[-1]
            
            for i in range(forecast_length):
                # Apply trend with damping
                damping_factor = 0.95 ** i  # Trend dampens over time
                predicted_value = last_value + trend * (i + 1) * damping_factor
                
                # Add seasonal component (simplified)
                seasonal_component = 0.05 * np.sin(2 * np.pi * i / 24)  # Daily seasonality
                predicted_value += predicted_value * seasonal_component
                
                # Ensure non-negative for utilization metrics
                predicted_value = max(0, predicted_value)
                if 'utilization' in horizon.value.lower():
                    predicted_value = min(1.0, predicted_value)
                
                forecast_values.append(predicted_value)
                
                # Calculate confidence interval (±10% with increasing uncertainty)
                uncertainty = 0.1 + 0.02 * i
                lower_bound = predicted_value * (1 - uncertainty)
                upper_bound = predicted_value * (1 + uncertainty)
                confidence_intervals.append((lower_bound, upper_bound))
            
            return forecast_values, confidence_intervals
            
        except Exception as e:
            logger.error(f"❌ Error generating forecast values: {e}")
            return [], []
    
    async def _detect_trend(self, values: List[float]) -> str:
        """Detect trend direction in time series"""
        try:
            if len(values) < 3:
                return "stable"
            
            # Linear regression slope
            n = len(values)
            x = list(range(n))
            x_mean = mean(x)
            y_mean = mean(values)
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                return "stable"
            
            slope = numerator / denominator
            
            if slope > 0.01:
                return "increasing"
            elif slope < -0.01:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"❌ Error detecting trend: {e}")
            return "unknown"
    
    async def _detect_seasonality(self, values: List[float]) -> bool:
        """Detect seasonality in time series"""
        try:
            if len(values) < 48:  # Need at least 48 points for daily seasonality
                return False
            
            # Simple autocorrelation check for 24-hour seasonality
            period = 24
            if len(values) < 2 * period:
                return False
            
            # Calculate autocorrelation at period lag
            recent_values = values[-2*period:]
            lag_values = recent_values[:-period]
            current_values = recent_values[period:]
            
            if len(lag_values) != len(current_values):
                return False
            
            # Pearson correlation coefficient
            mean_lag = mean(lag_values)
            mean_current = mean(current_values)
            
            numerator = sum((lag_values[i] - mean_lag) * (current_values[i] - mean_current) 
                          for i in range(len(lag_values)))
            
            lag_var = sum((v - mean_lag) ** 2 for v in lag_values)
            current_var = sum((v - mean_current) ** 2 for v in current_values)
            
            if lag_var == 0 or current_var == 0:
                return False
            
            correlation = numerator / (lag_var * current_var) ** 0.5
            
            return abs(correlation) > 0.3  # Threshold for seasonality
            
        except Exception as e:
            logger.error(f"❌ Error detecting seasonality: {e}")
            return False
    
    async def _calculate_forecast_accuracy(
        self,
        actual: List[float],
        predicted: List[float]
    ) -> float:
        """Calculate forecast accuracy using MAPE"""
        try:
            if len(actual) != len(predicted) or len(actual) == 0:
                return 0.0
            
            absolute_percentage_errors = []
            
            for i in range(len(actual)):
                if actual[i] != 0:
                    ape = abs((actual[i] - predicted[i]) / actual[i])
                    absolute_percentage_errors.append(ape)
            
            if not absolute_percentage_errors:
                return 0.0
            
            mape = mean(absolute_percentage_errors)
            accuracy = max(0, 1 - mape)  # Convert MAPE to accuracy
            
            return accuracy
            
        except Exception as e:
            logger.error(f"❌ Error calculating forecast accuracy: {e}")
            return 0.0
    
    async def generate_capacity_recommendations(
        self,
        forecast_horizon: ForecastHorizon = ForecastHorizon.MONTHLY
    ) -> List[CapacityRecommendation]:
        """Generate capacity planning recommendations"""
        try:
            recommendations = []
            
            # Generate forecasts for key metrics
            key_metrics = [
                CapacityMetric.CPU_UTILIZATION,
                CapacityMetric.MEMORY_UTILIZATION,
                CapacityMetric.GPU_UTILIZATION,
                CapacityMetric.REQUEST_VOLUME
            ]
            
            for metric in key_metrics:
                forecast = await self.generate_demand_forecast(metric, forecast_horizon)
                
                if forecast and forecast.accuracy_score > self.forecast_accuracy_threshold:
                    recommendation = await self._generate_metric_recommendation(forecast)
                    if recommendation:
                        recommendations.append(recommendation)
            
            # Sort by priority
            recommendations.sort(key=lambda x: x.priority, reverse=True)
            
            # Store recommendations
            for rec in recommendations:
                self.capacity_recommendations[rec.recommendation_id] = rec
            
            self.planning_metrics['recommendations_created'] += len(recommendations)
            
            logger.info(f"✅ Generated {len(recommendations)} capacity recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating capacity recommendations: {e}")
            return []
    
    async def _generate_metric_recommendation(
        self,
        forecast: DemandForecast
    ) -> Optional[CapacityRecommendation]:
        """Generate recommendation for specific metric forecast"""
        try:
            # Get current utilization
            recent_data = self.capacity_data[forecast.metric][-24:]  # Last 24 points
            if not recent_data:
                return None
            
            current_avg = mean([dp.value for dp in recent_data])
            forecast_max = max(forecast.forecast_values) if forecast.forecast_values else current_avg
            
            # Determine if action needed
            scaling_direction = ScalingDirection.MAINTAIN
            priority = 1
            reasoning = "No action required - capacity within normal range"
            
            if forecast_max > self.utilization_upper_threshold:
                scaling_direction = ScalingDirection.SCALE_UP
                priority = 5 if forecast_max > 0.9 else 3
                reasoning = f"Forecast indicates {forecast.metric.value} will exceed {self.utilization_upper_threshold*100}%"
                
            elif forecast_max < self.utilization_lower_threshold:
                scaling_direction = ScalingDirection.SCALE_DOWN
                priority = 2
                reasoning = f"Forecast indicates {forecast.metric.value} will remain below {self.utilization_lower_threshold*100}%"
            
            # Calculate recommended capacity
            recommended_capacity = current_avg
            if scaling_direction == ScalingDirection.SCALE_UP:
                recommended_capacity = forecast_max * 1.2  # 20% buffer
            elif scaling_direction == ScalingDirection.SCALE_DOWN:
                recommended_capacity = forecast_max * 1.1  # 10% buffer
            
            # Estimate cost impact
            cost_impact = await self._estimate_cost_impact(
                forecast.metric, current_avg, recommended_capacity
            )
            
            recommendation = CapacityRecommendation(
                recommendation_id=str(uuid.uuid4()),
                target_metric=forecast.metric,
                scaling_direction=scaling_direction,
                recommended_capacity=recommended_capacity,
                current_capacity=current_avg,
                expected_cost_impact=cost_impact,
                priority=priority,
                reasoning=reasoning,
                implementation_timeline=self._get_implementation_timeline(priority),
                risk_assessment=await self._assess_recommendation_risk(forecast, scaling_direction)
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Error generating metric recommendation: {e}")
            return None
    
    async def _estimate_cost_impact(
        self,
        metric: CapacityMetric,
        current_capacity: float,
        recommended_capacity: float
    ) -> float:
        """Estimate cost impact of capacity change"""
        try:
            # Simplified cost calculation
            base_cost_per_unit = {
                CapacityMetric.CPU_UTILIZATION: 0.10,  # $ per CPU hour
                CapacityMetric.MEMORY_UTILIZATION: 0.05,  # $ per GB hour
                CapacityMetric.GPU_UTILIZATION: 2.50,  # $ per GPU hour
                CapacityMetric.STORAGE_UTILIZATION: 0.02  # $ per GB hour
            }
            
            unit_cost = base_cost_per_unit.get(metric, 0.10)
            capacity_change = recommended_capacity - current_capacity
            
            # Estimate monthly cost impact
            monthly_cost_impact = capacity_change * unit_cost * 24 * 30
            
            return monthly_cost_impact
            
        except Exception as e:
            logger.error(f"❌ Error estimating cost impact: {e}")
            return 0.0
    
    def _get_implementation_timeline(self, priority: int) -> str:
        """Get implementation timeline based on priority"""
        timelines = {
            5: "Immediate (within 24 hours)",
            4: "Urgent (within 3 days)",
            3: "High (within 1 week)",
            2: "Medium (within 2 weeks)",
            1: "Low (within 1 month)"
        }
        return timelines.get(priority, "Low priority")
    
    async def _assess_recommendation_risk(
        self,
        forecast: DemandForecast,
        scaling_direction: ScalingDirection
    ) -> Dict[str, Any]:
        """Assess risk of implementing recommendation"""
        try:
            risk_level = "LOW"
            risk_factors = []
            
            # Forecast accuracy risk
            if forecast.accuracy_score < 0.8:
                risk_level = "MEDIUM"
                risk_factors.append("Forecast accuracy below 80%")
            
            # Scaling direction risk
            if scaling_direction == ScalingDirection.SCALE_DOWN:
                risk_factors.append("Resource reduction may impact performance")
                if risk_level == "LOW":
                    risk_level = "MEDIUM"
            
            # Trend uncertainty
            if forecast.trend_direction == "unknown":
                risk_factors.append("Uncertain trend direction")
            
            return {
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'mitigation_strategies': [
                    "Monitor implementation closely",
                    "Prepare rollback plan",
                    "Implement gradually"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error assessing recommendation risk: {e}")
            return {'risk_level': 'UNKNOWN', 'risk_factors': []}
    
    async def project_creator_impact(
        self,
        months_ahead: int = 12
    ) -> Dict[str, Any]:
        """Project impact of creator growth on infrastructure"""
        try:
            projections = {}
            
            for creator_type, model in self.creator_models.items():
                profile = self.creator_resource_profiles.get(creator_type, {})
                
                # Project resource requirements
                projected_resources = []
                
                for month in range(min(months_ahead, len(model.predicted_count))):
                    creator_count = model.predicted_count[month]
                    
                    # Calculate resource requirements
                    cpu_requirement = creator_count * profile.get('cpu_weight', 1.0) * model.resource_intensity
                    gpu_requirement = creator_count * profile.get('gpu_weight', 1.0) * model.resource_intensity
                    storage_requirement = creator_count * profile.get('storage_weight', 1.0) * model.resource_intensity
                    
                    projected_resources.append({
                        'month': month + 1,
                        'creator_count': creator_count,
                        'cpu_requirement': cpu_requirement,
                        'gpu_requirement': gpu_requirement,
                        'storage_requirement': storage_requirement
                    })
                
                projections[creator_type] = {
                    'growth_rate': model.growth_rate,
                    'projected_resources': projected_resources,
                    'confidence_level': model.confidence_level
                }
            
            return projections
            
        except Exception as e:
            logger.error(f"❌ Error projecting creator impact: {e}")
            return {}
    
    async def get_capacity_dashboard(self) -> Dict[str, Any]:
        """Get capacity planning dashboard data"""
        try:
            dashboard = {
                'current_utilization': {},
                'recent_forecasts': {},
                'active_recommendations': [],
                'creator_projections': {},
                'alerts': []
            }
            
            # Current utilization
            for metric in CapacityMetric:
                recent_data = self.capacity_data[metric][-24:]
                if recent_data:
                    current_avg = mean([dp.value for dp in recent_data])
                    dashboard['current_utilization'][metric.value] = {
                        'current': current_avg,
                        'threshold_upper': self.utilization_upper_threshold,
                        'threshold_lower': self.utilization_lower_threshold,
                        'status': self._get_utilization_status(current_avg)
                    }
            
            # Recent forecasts
            for forecast_id, forecast in list(self.demand_forecasts.items())[-5:]:
                dashboard['recent_forecasts'][forecast_id] = {
                    'metric': forecast.metric.value,
                    'horizon': forecast.horizon.value,
                    'trend': forecast.trend_direction,
                    'accuracy': forecast.accuracy_score,
                    'next_value': forecast.forecast_values[0] if forecast.forecast_values else None
                }
            
            # Active recommendations
            active_recs = sorted(
                self.capacity_recommendations.values(),
                key=lambda x: x.priority,
                reverse=True
            )[:10]
            
            for rec in active_recs:
                dashboard['active_recommendations'].append({
                    'id': rec.recommendation_id,
                    'metric': rec.target_metric.value,
                    'direction': rec.scaling_direction.value,
                    'priority': rec.priority,
                    'cost_impact': rec.expected_cost_impact,
                    'timeline': rec.implementation_timeline
                })
            
            # Creator projections
            dashboard['creator_projections'] = await self.project_creator_impact(6)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Error getting capacity dashboard: {e}")
            return {}
    
    def _get_utilization_status(self, utilization: float) -> str:
        """Get utilization status"""
        if utilization > self.utilization_upper_threshold:
            return "HIGH"
        elif utilization < self.utilization_lower_threshold:
            return "LOW"
        else:
            return "NORMAL"
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get capacity planning metrics"""
        return {
            **self.planning_metrics,
            'data_points_stored': sum(len(data) for data in self.capacity_data.values()),
            'active_forecasts': len(self.demand_forecasts),
            'pending_recommendations': len(self.capacity_recommendations)
        }


# Global instance
capacity_planner = CapacityPlanningSystem()


async def main() -> None:
    """Test the Capacity Planning System"""
    planner = CapacityPlanningSystem()
    
    print("📊 Testing Capacity Planning System...")
    
    # Generate forecast
    forecast = await planner.generate_demand_forecast(
        CapacityMetric.CPU_UTILIZATION,
        ForecastHorizon.WEEKLY
    )
    
    if forecast:
        print(f"✅ Generated forecast for CPU utilization")
        print(f"   Trend: {forecast.trend_direction}")
        print(f"   Seasonality: {forecast.seasonality_detected}")
        print(f"   Accuracy: {forecast.accuracy_score:.2f}")
        print(f"   Next 7 values: {[f'{v:.2f}' for v in forecast.forecast_values]}")
    
    # Generate recommendations
    recommendations = await planner.generate_capacity_recommendations()
    print(f"\n📋 Generated {len(recommendations)} recommendations:")
    
    for rec in recommendations[:3]:
        print(f"   Priority {rec.priority}: {rec.target_metric.value}")
        print(f"   Action: {rec.scaling_direction.value}")
        print(f"   Cost impact: ${rec.expected_cost_impact:.2f}/month")
        print(f"   Timeline: {rec.implementation_timeline}")
    
    # Creator impact projection
    projections = await planner.project_creator_impact(6)
    print(f"\n👥 Creator growth projections:")
    
    for creator_type, projection in projections.items():
        if projection['projected_resources']:
            month_6 = projection['projected_resources'][5]  # 6th month
            print(f"   {creator_type}: {month_6['creator_count']} creators")
            print(f"     CPU requirement: {month_6['cpu_requirement']:.1f} units")
    
    # Get dashboard
    dashboard = await planner.get_capacity_dashboard()
    print(f"\n📊 Dashboard summary:")
    print(f"   Current utilization entries: {len(dashboard['current_utilization'])}")
    print(f"   Recent forecasts: {len(dashboard['recent_forecasts'])}")
    print(f"   Active recommendations: {len(dashboard['active_recommendations'])}")
    
    # Get metrics
    metrics = await planner.get_metrics()
    print(f"\nMetrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())