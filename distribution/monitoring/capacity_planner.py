"""
Capacity Planner module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Ainflue Platform - Distribution Monitoring - Capacity Planner
Advanced capacity planning and resource optimization for distribution infrastructure

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import numpy as np
from scipy import stats
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types of resources to plan for"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    API_CAPACITY = "api_capacity"
    WORKER_PROCESSES = "worker_processes"

class PlanningHorizon(Enum):
    """Planning time horizons"""
    SHORT_TERM = "short_term"      # 1-4 weeks
    MEDIUM_TERM = "medium_term"    # 1-6 months
    LONG_TERM = "long_term"        # 6-24 months

class GrowthPattern(Enum):
    """Growth pattern types"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    SEASONAL = "seasonal"
    STEP_FUNCTION = "step_function"
    PLATEAU = "plateau"

class AlertLevel(Enum):
    """Capacity alert levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class ResourceMetrics:
    """Resource usage metrics"""
    timestamp: datetime
    resource_type: ResourceType
    current_usage: float
    max_capacity: float
    utilization_percent: float
    cost_per_unit: float
    metadata: Dict[str, Any] = None

@dataclass
class CapacityPrediction:
    """Capacity prediction result"""
    resource_type: ResourceType
    current_capacity: float
    predicted_usage: Dict[str, float]  # horizon -> predicted usage
    recommended_capacity: Dict[str, float]  # horizon -> recommended capacity
    growth_rate: float
    confidence_interval: Tuple[float, float]
    growth_pattern: GrowthPattern
    cost_impact: Dict[str, float]

@dataclass
class CapacityAlert:
    """Capacity planning alert"""
    alert_id: str
    resource_type: ResourceType
    level: AlertLevel
    message: str
    current_utilization: float
    predicted_exhaustion: Optional[datetime]
    recommendations: List[str]
    created_at: datetime

@dataclass
class ScalingRecommendation:
    """Scaling recommendation"""
    resource_type: ResourceType
    action: str  # scale_up, scale_down, optimize
    timeline: str
    justification: str
    cost_impact: float
    risk_level: str
    implementation_steps: List[str]

class DistributionCapacityPlanner:
    """
    Advanced capacity planning system for distribution infrastructure
    Predicts resource needs and provides scaling recommendations
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.historical_metrics: Dict[ResourceType, List[ResourceMetrics]] = {}
        self.predictions: Dict[ResourceType, CapacityPrediction] = {}
        self.alerts: List[CapacityAlert] = []
        self.recommendations: List[ScalingRecommendation] = []
        
        # Configuration
        self.prediction_models = {}
        self.thresholds = self._load_capacity_thresholds()
        self.cost_models = self._load_cost_models()
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _load_capacity_thresholds(self) -> Dict[ResourceType, Dict[str, float]]:
        """Load capacity thresholds for different resources"""
        return {
            ResourceType.CPU: {
                'warning': 70.0,
                'critical': 85.0,
                'emergency': 95.0,
                'target_utilization': 65.0,
                'buffer_percent': 20.0
            },
            ResourceType.MEMORY: {
                'warning': 75.0,
                'critical': 90.0,
                'emergency': 98.0,
                'target_utilization': 70.0,
                'buffer_percent': 25.0
            },
            ResourceType.STORAGE: {
                'warning': 80.0,
                'critical': 90.0,
                'emergency': 95.0,
                'target_utilization': 75.0,
                'buffer_percent': 30.0
            },
            ResourceType.NETWORK: {
                'warning': 70.0,
                'critical': 85.0,
                'emergency': 95.0,
                'target_utilization': 60.0,
                'buffer_percent': 40.0
            },
            ResourceType.DATABASE: {
                'warning': 75.0,
                'critical': 85.0,
                'emergency': 95.0,
                'target_utilization': 70.0,
                'buffer_percent': 25.0
            }
        }
    
    def _load_cost_models(self) -> Dict[ResourceType, Dict[str, float]]:
        """Load cost models for different resources"""
        return {
            ResourceType.CPU: {
                'cost_per_vcpu_hour': 0.048,
                'setup_cost': 0.0,
                'scaling_cost_factor': 1.0
            },
            ResourceType.MEMORY: {
                'cost_per_gb_hour': 0.0065,
                'setup_cost': 0.0,
                'scaling_cost_factor': 1.0
            },
            ResourceType.STORAGE: {
                'cost_per_gb_month': 0.10,
                'setup_cost': 0.0,
                'scaling_cost_factor': 0.95  # Volume discounts
            },
            ResourceType.NETWORK: {
                'cost_per_gb_transfer': 0.09,
                'setup_cost': 0.0,
                'scaling_cost_factor': 0.9
            },
            ResourceType.DATABASE: {
                'cost_per_hour': 0.25,
                'setup_cost': 50.0,
                'scaling_cost_factor': 1.2  # Database scaling is more expensive
            }
        }
    
    def _initialize_sample_data(self) -> None:
        """Initialize with sample historical data for demonstration"""
        
        # Generate sample CPU usage data with growth trend
        cpu_data = []
        base_time = datetime.utcnow() - timedelta(days=90)
        
        for i in range(90):
            timestamp = base_time + timedelta(days=i)
            # Simulate growing usage with some noise
            base_usage = 45 + (i * 0.3) + np.random.normal(0, 5)
            utilization = min(max(base_usage, 20), 95)  # Clamp between 20-95%
            
            cpu_data.append(ResourceMetrics(
                timestamp=timestamp,
                resource_type=ResourceType.CPU,
                current_usage=utilization,
                max_capacity=100.0,
                utilization_percent=utilization,
                cost_per_unit=0.048,
                metadata={'instance_type': 'm5.large', 'region': 'us-east-1'}
            ))
        
        self.historical_metrics[ResourceType.CPU] = cpu_data
        
        # Generate sample memory data
        memory_data = []
        for i in range(90):
            timestamp = base_time + timedelta(days=i)
            base_usage = 55 + (i * 0.25) + np.random.normal(0, 4)
            utilization = min(max(base_usage, 30), 92)
            
            memory_data.append(ResourceMetrics(
                timestamp=timestamp,
                resource_type=ResourceType.MEMORY,
                current_usage=utilization,
                max_capacity=100.0,
                utilization_percent=utilization,
                cost_per_unit=0.0065,
                metadata={'memory_gb': 16, 'instance_type': 'm5.large'}
            ))
        
        self.historical_metrics[ResourceType.MEMORY] = memory_data
    
    async def analyze_capacity_trends(self, resource_type: ResourceType, 
                                    horizon: PlanningHorizon = PlanningHorizon.MEDIUM_TERM) -> CapacityPrediction:
        """
        Analyze capacity trends and predict future resource needs
        
        Args:
            resource_type: Type of resource to analyze
            horizon: Planning horizon
            
        Returns:
            Capacity prediction with recommendations
        """
        logger.info(f"Analyzing capacity trends for {resource_type.value}")
        
        if resource_type not in self.historical_metrics:
            raise ValueError(f"No historical data available for {resource_type.value}")
        
        metrics = self.historical_metrics[resource_type]
        
        # Prepare data for analysis
        df = pd.DataFrame([
            {
                'timestamp': m.timestamp,
                'utilization': m.utilization_percent,
                'usage': m.current_usage
            }
            for m in metrics
        ])
        
        df['days'] = (df['timestamp'] - df['timestamp'].min()).dt.days
        
        # Detect growth pattern
        growth_pattern = self._detect_growth_pattern(df)
        
        # Train prediction model
        model, confidence = self._train_prediction_model(df, growth_pattern)
        
        # Generate predictions
        predictions = self._generate_predictions(model, df, horizon)
        
        # Calculate recommended capacity
        recommendations = self._calculate_capacity_recommendations(predictions, resource_type)
        
        # Calculate cost impact
        cost_impact = self._calculate_cost_impact(resource_type, predictions)
        
        prediction = CapacityPrediction(
            resource_type=resource_type,
            current_capacity=metrics[-1].max_capacity,
            predicted_usage=predictions,
            recommended_capacity=recommendations,
            growth_rate=self._calculate_growth_rate(df),
            confidence_interval=confidence,
            growth_pattern=growth_pattern,
            cost_impact=cost_impact
        )
        
        self.predictions[resource_type] = prediction
        
        # Generate alerts if needed
        await self._check_capacity_alerts(prediction)
        
        logger.info(f"Capacity analysis completed for {resource_type.value}")
        return prediction
    
    def _detect_growth_pattern(self, df: pd.DataFrame) -> GrowthPattern:
        """Detect the growth pattern in historical data"""
        
        utilization = df['utilization'].values
        days = df['days'].values
        
        # Test for linear growth
        linear_r2 = self._test_linear_fit(days, utilization)
        
        # Test for exponential growth
        log_utilization = np.log(np.maximum(utilization, 1))  # Avoid log(0)
        exp_r2 = self._test_linear_fit(days, log_utilization)
        
        # Test for seasonal patterns
        seasonal_score = self._test_seasonal_pattern(df)
        
        # Determine pattern based on R² scores
        if seasonal_score > 0.7:
            return GrowthPattern.SEASONAL
        elif exp_r2 > linear_r2 and exp_r2 > 0.8:
            return GrowthPattern.EXPONENTIAL
        elif linear_r2 > 0.6:
            return GrowthPattern.LINEAR
        elif np.std(utilization[-14:]) < 2:  # Low variance in recent data
            return GrowthPattern.PLATEAU
        else:
            return GrowthPattern.STEP_FUNCTION
    
    def _test_linear_fit(self, x: np.ndarray, y: np.ndarray) -> float:
        """Test linear fit and return R² score"""
        try:
            model = LinearRegression()
            model.fit(x.reshape(-1, 1), y)
            y_pred = model.predict(x.reshape(-1, 1))
            return r2_score(y, y_pred)
        except:
            return 0.0
    
    def _test_seasonal_pattern(self, df: pd.DataFrame) -> float:
        """Test for seasonal patterns in the data"""
        if len(df) < 28:  # Need at least 4 weeks of data
            return 0.0
        
        # Add day of week and hour features
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['hour'] = df['timestamp'].dt.hour
        
        # Calculate variance within days vs between days
        daily_variance = df.groupby('day_of_week')['utilization'].var().mean()
        overall_variance = df['utilization'].var()
        
        if overall_variance == 0:
            return 0.0
        
        seasonal_score = min(daily_variance / overall_variance, 1.0)
        return seasonal_score
    
    def _train_prediction_model(self, df: pd.DataFrame, pattern: GrowthPattern) -> Tuple[Any, Tuple[float, float]]:
        """Train prediction model based on detected pattern"""
        
        days = df['days'].values.reshape(-1, 1)
        utilization = df['utilization'].values
        
        if pattern == GrowthPattern.LINEAR:
            model = LinearRegression()
            model.fit(days, utilization)
            
        elif pattern == GrowthPattern.EXPONENTIAL:
            # Use polynomial features for exponential-like growth
            poly_features = PolynomialFeatures(degree=2)
            days_poly = poly_features.fit_transform(days)
            
            model = LinearRegression()
            model.fit(days_poly, utilization)
            model.poly_features = poly_features
            
        else:
            # Default to linear for other patterns
            model = LinearRegression()
            model.fit(days, utilization)
        
        # Calculate confidence interval
        predictions = model.predict(days) if pattern == GrowthPattern.LINEAR else model.predict(model.poly_features.transform(days))
        mse = mean_squared_error(utilization, predictions)
        confidence_interval = (np.sqrt(mse) * -1.96, np.sqrt(mse) * 1.96)
        
        return model, confidence_interval
    
    def _generate_predictions(self, model: Any, df: pd.DataFrame, horizon: PlanningHorizon) -> Dict[str, float]:
        """Generate predictions for different time horizons"""
        
        last_day = df['days'].max()
        
        # Define prediction periods
        horizons = {
            PlanningHorizon.SHORT_TERM: [7, 14, 21, 28],  # weeks
            PlanningHorizon.MEDIUM_TERM: [30, 60, 90, 120, 180],  # days
            PlanningHorizon.LONG_TERM: [180, 365, 548, 730]  # days
        }
        
        periods = horizons[horizon]
        predictions = {}
        
        for period in periods:
            future_day = last_day + period
            
            if hasattr(model, 'poly_features'):
                # Polynomial model
                future_days_poly = model.poly_features.transform([[future_day]])
                prediction = model.predict(future_days_poly)[0]
            else:
                # Linear model
                prediction = model.predict([[future_day]])[0]
            
            # Ensure prediction is reasonable (0-100%)
            prediction = max(0, min(prediction, 100))
            
            period_name = f"{period}_days" if period > 28 else f"{period//7}_weeks"
            predictions[period_name] = prediction
        
        return predictions
    
    def _calculate_capacity_recommendations(self, predictions: Dict[str, float], 
                                          resource_type: ResourceType) -> Dict[str, float]:
        """Calculate recommended capacity based on predictions"""
        
        thresholds = self.thresholds.get(resource_type, {})
        buffer_percent = thresholds.get('buffer_percent', 20.0)
        
        recommendations = {}
        
        for period, predicted_usage in predictions.items():
            # Add buffer for safety
            recommended_capacity = predicted_usage * (1 + buffer_percent / 100)
            recommendations[period] = min(recommended_capacity, 100.0)
        
        return recommendations
    
    def _calculate_growth_rate(self, df: pd.DataFrame) -> float:
        """Calculate average growth rate"""
        if len(df) < 2:
            return 0.0
        
        utilization = df['utilization'].values
        first_half = utilization[:len(utilization)//2].mean()
        second_half = utilization[len(utilization)//2:].mean()
        
        if first_half == 0:
            return 0.0
        
        growth_rate = ((second_half - first_half) / first_half) * 100
        return growth_rate
    
    def _calculate_cost_impact(self, resource_type: ResourceType, predictions: Dict[str, float]) -> Dict[str, float]:
        """Calculate cost impact of capacity changes"""
        
        cost_model = self.cost_models.get(resource_type, {})
        cost_per_unit = cost_model.get('cost_per_vcpu_hour', 0.048)
        
        cost_impact = {}
        
        for period, predicted_usage in predictions.items():
            # Calculate additional cost for scaling
            current_usage = 50.0  # Assume current baseline
            additional_capacity = max(0, predicted_usage - current_usage)
            
            # Calculate monthly cost impact
            if 'weeks' in period:
                weeks = int(period.split('_')[0])
                monthly_cost = additional_capacity * cost_per_unit * 24 * 30 / 4 * weeks
            else:
                days = int(period.split('_')[0])
                monthly_cost = additional_capacity * cost_per_unit * 24 * (days / 30)
            
            cost_impact[period] = monthly_cost
        
        return cost_impact
    
    async def _check_capacity_alerts(self, prediction -> None: CapacityPrediction) -> None:
        """Check if capacity alerts should be generated"""
        
        resource_type = prediction.resource_type
        thresholds = self.thresholds.get(resource_type, {})
        
        # Get current and near-term predictions
        current_usage = prediction.predicted_usage.get('1_weeks', 0)
        short_term_usage = prediction.predicted_usage.get('4_weeks', 0)
        
        alerts_to_create = []
        
        # Check current utilization
        if current_usage >= thresholds.get('emergency', 95):
            alerts_to_create.append({
                'level': AlertLevel.EMERGENCY,
                'message': f'{resource_type.value} utilization at emergency level ({current_usage:.1f}%)',
                'recommendations': ['Immediate scaling required', 'Activate emergency capacity']
            })
        elif current_usage >= thresholds.get('critical', 85):
            alerts_to_create.append({
                'level': AlertLevel.CRITICAL,
                'message': f'{resource_type.value} utilization at critical level ({current_usage:.1f}%)',
                'recommendations': ['Scale up within 24 hours', 'Monitor closely']
            })
        elif current_usage >= thresholds.get('warning', 70):
            alerts_to_create.append({
                'level': AlertLevel.WARNING,
                'message': f'{resource_type.value} utilization approaching limits ({current_usage:.1f}%)',
                'recommendations': ['Plan scaling in next week', 'Review optimization opportunities']
            })
        
        # Check growth trend
        if prediction.growth_rate > 15:  # 15% growth rate
            alerts_to_create.append({
                'level': AlertLevel.WARNING,
                'message': f'{resource_type.value} showing high growth rate ({prediction.growth_rate:.1f}%)',
                'recommendations': ['Review capacity planning strategy', 'Consider auto-scaling']
            })
        
        # Create alerts
        for alert_info in alerts_to_create:
            alert = CapacityAlert(
                alert_id=f"CAP-{int(time.time() * 1000)}",
                resource_type=resource_type,
                level=alert_info['level'],
                message=alert_info['message'],
                current_utilization=current_usage,
                predicted_exhaustion=self._calculate_exhaustion_date(prediction),
                recommendations=alert_info['recommendations'],
                created_at=datetime.utcnow()
            )
            
            self.alerts.append(alert)
            logger.warning(f"Capacity alert created: {alert.message}")
    
    def _calculate_exhaustion_date(self, prediction: CapacityPrediction) -> Optional[datetime]:
        """Calculate when resource will be exhausted based on growth"""
        
        if prediction.growth_rate <= 0:
            return None
        
        # Simple linear extrapolation to 100% utilization
        current_usage = list(prediction.predicted_usage.values())[0]
        days_to_exhaustion = (100 - current_usage) / (prediction.growth_rate / 30)
        
        if days_to_exhaustion > 0 and days_to_exhaustion < 365:
            return datetime.utcnow() + timedelta(days=days_to_exhaustion)
        
        return None
    
    async def generate_scaling_recommendations(self, resource_type: ResourceType) -> List[ScalingRecommendation]:
        """Generate scaling recommendations for a resource"""
        
        if resource_type not in self.predictions:
            await self.analyze_capacity_trends(resource_type)
        
        prediction = self.predictions[resource_type]
        recommendations = []
        
        # Short-term recommendations
        short_term_usage = prediction.predicted_usage.get('4_weeks', 0)
        if short_term_usage > 80:
            recommendations.append(ScalingRecommendation(
                resource_type=resource_type,
                action='scale_up',
                timeline='immediate',
                justification=f'Predicted {short_term_usage:.1f}% utilization in 4 weeks',
                cost_impact=prediction.cost_impact.get('4_weeks', 0),
                risk_level='high',
                implementation_steps=[
                    'Review current resource allocation',
                    'Provision additional capacity',
                    'Update monitoring thresholds',
                    'Test scaled configuration'
                ]
            ))
        
        # Medium-term recommendations
        medium_term_usage = prediction.predicted_usage.get('90_days', 0)
        if medium_term_usage > 75:
            recommendations.append(ScalingRecommendation(
                resource_type=resource_type,
                action='scale_up',
                timeline='1-3 months',
                justification=f'Predicted {medium_term_usage:.1f}% utilization in 3 months',
                cost_impact=prediction.cost_impact.get('90_days', 0),
                risk_level='medium',
                implementation_steps=[
                    'Plan capacity expansion',
                    'Budget for additional resources',
                    'Evaluate optimization opportunities',
                    'Implement auto-scaling if possible'
                ]
            ))
        
        # Optimization recommendations
        if prediction.growth_rate > 10:
            recommendations.append(ScalingRecommendation(
                resource_type=resource_type,
                action='optimize',
                timeline='ongoing',
                justification=f'High growth rate ({prediction.growth_rate:.1f}%) indicates optimization potential',
                cost_impact=-prediction.cost_impact.get('30_days', 0) * 0.1,  # Assume 10% savings
                risk_level='low',
                implementation_steps=[
                    'Conduct resource utilization audit',
                    'Implement performance optimizations',
                    'Review and optimize algorithms',
                    'Consider caching strategies'
                ]
            ))
        
        self.recommendations.extend(recommendations)
        return recommendations
    
    async def get_capacity_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive capacity dashboard data"""
        
        dashboard_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'resources': {},
            'alerts': [],
            'recommendations': [],
            'cost_projections': {}
        }
        
        # Analyze all resource types
        for resource_type in ResourceType:
            if resource_type in self.historical_metrics:
                try:
                    prediction = await self.analyze_capacity_trends(resource_type)
                    
                    dashboard_data['resources'][resource_type.value] = {
                        'current_utilization': prediction.predicted_usage.get('1_weeks', 0),
                        'growth_rate': prediction.growth_rate,
                        'predictions': prediction.predicted_usage,
                        'recommendations': prediction.recommended_capacity,
                        'pattern': prediction.growth_pattern.value,
                        'confidence': prediction.confidence_interval
                    }
                    
                    # Generate recommendations
                    recommendations = await self.generate_scaling_recommendations(resource_type)
                    dashboard_data['recommendations'].extend([
                        {
                            'resource': rec.resource_type.value,
                            'action': rec.action,
                            'timeline': rec.timeline,
                            'justification': rec.justification,
                            'cost_impact': rec.cost_impact
                        }
                        for rec in recommendations
                    ])
                    
                except Exception as e:
                    logger.error(f"Error analyzing {resource_type.value}: {e}")
        
        # Add alerts
        dashboard_data['alerts'] = [
            {
                'id': alert.alert_id,
                'resource': alert.resource_type.value,
                'level': alert.level.value,
                'message': alert.message,
                'utilization': alert.current_utilization,
                'recommendations': alert.recommendations
            }
            for alert in self.alerts[-10:]  # Last 10 alerts
        ]
        
        # Calculate total cost projections
        total_cost_30d = sum(
            pred.cost_impact.get('30_days', 0) 
            for pred in self.predictions.values()
        )
        total_cost_90d = sum(
            pred.cost_impact.get('90_days', 0) 
            for pred in self.predictions.values()
        )
        
        dashboard_data['cost_projections'] = {
            '30_days': total_cost_30d,
            '90_days': total_cost_90d,
            'annual': total_cost_90d * 4
        }
        
        return dashboard_data
    
    async def simulate_scaling_scenario(self, resource_type: ResourceType, 
                                      scaling_factor: float) -> Dict[str, Any]:
        """Simulate the impact of scaling a resource by a given factor"""
        
        if resource_type not in self.predictions:
            await self.analyze_capacity_trends(resource_type)
        
        prediction = self.predictions[resource_type]
        cost_model = self.cost_models.get(resource_type, {})
        
        # Calculate impact
        current_capacity = prediction.current_capacity
        new_capacity = current_capacity * scaling_factor
        capacity_change = new_capacity - current_capacity
        
        # Cost impact
        cost_per_unit = cost_model.get('cost_per_vcpu_hour', 0.048)
        monthly_cost_change = capacity_change * cost_per_unit * 24 * 30
        
        # Utilization impact
        utilization_reduction = {}
        for period, predicted_usage in prediction.predicted_usage.items():
            new_utilization = (predicted_usage * current_capacity) / new_capacity
            utilization_reduction[period] = predicted_usage - new_utilization
        
        return {
            'resource_type': resource_type.value,
            'scaling_factor': scaling_factor,
            'capacity_change': capacity_change,
            'cost_impact': {
                'monthly': monthly_cost_change,
                'annual': monthly_cost_change * 12
            },
            'utilization_improvement': utilization_reduction,
            'risk_reduction': self._calculate_risk_reduction(utilization_reduction),
            'recommendation': 'proceed' if scaling_factor <= 2.0 else 'review_carefully'
        }
    
    def _calculate_risk_reduction(self, utilization_improvement: Dict[str, float]) -> str:
        """Calculate risk reduction from utilization improvement"""
        avg_improvement = np.mean(list(utilization_improvement.values()))
        
        if avg_improvement > 20:
            return 'high'
        elif avg_improvement > 10:
            return 'medium'
        elif avg_improvement > 5:
            return 'low'
        else:
            return 'minimal'

# Factory function
def create_capacity_planner(config: Optional[Dict] = None) -> DistributionCapacityPlanner:
    """Create capacity planner instance"""
    return DistributionCapacityPlanner(config)

# Example usage
async def main() -> None:
    """Example usage of capacity planner"""
    planner = create_capacity_planner()
    
    # Analyze CPU capacity trends
    cpu_prediction = await planner.analyze_capacity_trends(ResourceType.CPU)
    print(f"CPU Growth Rate: {cpu_prediction.growth_rate:.1f}%")
    print(f"CPU Predictions: {cpu_prediction.predicted_usage}")
    
    # Generate scaling recommendations
    recommendations = await planner.generate_scaling_recommendations(ResourceType.CPU)
    for rec in recommendations:
        print(f"Recommendation: {rec.action} - {rec.justification}")
    
    # Get dashboard data
    dashboard = await planner.get_capacity_dashboard_data()
    print(f"Total cost projection (30d): ${dashboard['cost_projections']['30_days']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())