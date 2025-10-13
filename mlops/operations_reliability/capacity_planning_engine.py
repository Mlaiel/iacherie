"""
🛡️ MLOps Operations & Reliability - Capacity Planning Engine
=============================================================

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Enterprise capacity planning engine for Creator Economy predictive scaling.
Combining expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json
import math


class ResourceType(Enum):
    """Resource types for capacity planning"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage" 
    NETWORK = "network"
    GPU = "gpu"
    DATABASE = "database"
    CACHE = "cache"


class CreatorTier(Enum):
    """Creator tier classifications"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class PredictionModel(Enum):
    """Prediction model types"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    ARIMA = "arima"


@dataclass
class CapacityMetrics:
    """Capacity metrics data structure"""
    timestamp: datetime
    resource_type: ResourceType
    current_usage: float
    max_capacity: float
    utilization_percentage: float
    creator_tier: CreatorTier
    geographic_region: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """Capacity prediction result"""
    resource_type: ResourceType
    predicted_usage: float
    confidence_interval: Tuple[float, float]
    prediction_horizon: timedelta
    model_accuracy: float
    recommended_capacity: float
    cost_impact: float
    risk_assessment: str


@dataclass
class ScalingRecommendation:
    """Scaling recommendation data"""
    resource_type: ResourceType
    current_capacity: float
    recommended_capacity: float
    scaling_factor: float
    timeline: timedelta
    cost_estimate: float
    performance_impact: str
    business_justification: str


class CapacityPlanningEngine:
    """
    Enterprise capacity planning engine for Creator Economy predictive scaling.
    
    Provides intelligent capacity forecasting, resource optimization,
    and predictive scaling recommendations for creator workloads.
    """
    
    def __init__(self):
        """Initialize capacity planning engine"""
        self.logger = logging.getLogger(__name__)
        self.prediction_models = {}
        self.historical_data = {}
        self.scaling_policies = {}
        self.cost_models = {}
        self.performance_thresholds = {
            ResourceType.CPU: 80.0,
            ResourceType.MEMORY: 85.0,
            ResourceType.STORAGE: 90.0,
            ResourceType.NETWORK: 75.0,
            ResourceType.GPU: 85.0,
            ResourceType.DATABASE: 80.0,
            ResourceType.CACHE: 70.0
        }
        
        self.logger.info("CapacityPlanningEngine initialized")
    
    async def collect_capacity_metrics(
        self,
        resource_type: ResourceType,
        time_range: timedelta = timedelta(days=30)
    ) -> List[CapacityMetrics]:
        """
        Collect historical capacity metrics for analysis
        
        Args:
            resource_type: Type of resource to analyze
            time_range: Historical data time range
            
        Returns:
            List of capacity metrics
        """
        try:
            # Simulate collecting metrics from monitoring systems
            end_time = datetime.now()
            start_time = end_time - time_range
            
            metrics = []
            current_time = start_time
            
            while current_time <= end_time:
                # Simulate realistic usage patterns
                base_usage = self._simulate_creator_usage_pattern(
                    current_time, resource_type
                )
                
                for tier in CreatorTier:
                    for region in ["us-east-1", "eu-west-1", "ap-southeast-1"]:
                        metric = CapacityMetrics(
                            timestamp=current_time,
                            resource_type=resource_type,
                            current_usage=base_usage * self._get_tier_multiplier(tier),
                            max_capacity=1000.0,  # Base capacity
                            utilization_percentage=(base_usage * self._get_tier_multiplier(tier)) / 10.0,
                            creator_tier=tier,
                            geographic_region=region,
                            metadata={
                                "active_creators": np.random.randint(100, 1000),
                                "peak_hour": self._is_peak_hour(current_time),
                                "seasonal_factor": self._get_seasonal_factor(current_time)
                            }
                        )
                        metrics.append(metric)
                
                current_time += timedelta(hours=1)
            
            self.historical_data[resource_type] = metrics
            self.logger.info(f"Collected {len(metrics)} capacity metrics for {resource_type.value}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting capacity metrics: {str(e)}")
            raise
    
    def _simulate_creator_usage_pattern(
        self, 
        timestamp: datetime, 
        resource_type: ResourceType
    ) -> float:
        """Simulate realistic creator usage patterns"""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Base pattern with daily cycles
        base_usage = 50 + 30 * math.sin(2 * math.pi * hour / 24)
        
        # Weekend boost for creators
        if day_of_week >= 5:  # Weekend
            base_usage *= 1.4
        
        # Peak hours for different content types
        if resource_type == ResourceType.GPU and 18 <= hour <= 22:
            base_usage *= 1.8  # Video processing peak
        elif resource_type == ResourceType.STORAGE and 20 <= hour <= 23:
            base_usage *= 1.5  # Content upload peak
        
        return max(10, base_usage + np.random.normal(0, 5))
    
    def _get_tier_multiplier(self, tier: CreatorTier) -> float:
        """Get resource multiplier for creator tier"""
        multipliers = {
            CreatorTier.STARTER: 1.0,
            CreatorTier.PROFESSIONAL: 2.5,
            CreatorTier.ENTERPRISE: 5.0,
            CreatorTier.PREMIUM: 8.0
        }
        return multipliers.get(tier, 1.0)
    
    def _is_peak_hour(self, timestamp: datetime) -> bool:
        """Check if timestamp is during peak hours"""
        return 18 <= timestamp.hour <= 22
    
    def _get_seasonal_factor(self, timestamp: datetime) -> float:
        """Get seasonal factor for capacity planning"""
        month = timestamp.month
        # Higher usage during holiday seasons
        if month in [11, 12, 1]:  # Holiday season
            return 1.3
        elif month in [6, 7, 8]:  # Summer boost
            return 1.2
        return 1.0
    
    async def train_prediction_models(
        self,
        resource_type: ResourceType,
        model_type: PredictionModel = PredictionModel.RANDOM_FOREST
    ) -> Dict[str, Any]:
        """
        Train prediction models for capacity forecasting
        
        Args:
            resource_type: Resource type to train model for
            model_type: Type of prediction model to use
            
        Returns:
            Model training results
        """
        try:
            if resource_type not in self.historical_data:
                await self.collect_capacity_metrics(resource_type)
            
            # Prepare training data
            metrics = self.historical_data[resource_type]
            df = pd.DataFrame([
                {
                    'timestamp': m.timestamp,
                    'usage': m.current_usage,
                    'utilization': m.utilization_percentage,
                    'hour': m.timestamp.hour,
                    'day_of_week': m.timestamp.weekday(),
                    'month': m.timestamp.month,
                    'is_peak': self._is_peak_hour(m.timestamp),
                    'seasonal_factor': self._get_seasonal_factor(m.timestamp),
                    'tier_multiplier': self._get_tier_multiplier(m.creator_tier)
                }
                for m in metrics
            ])
            
            # Feature engineering
            features = ['hour', 'day_of_week', 'month', 'is_peak', 
                       'seasonal_factor', 'tier_multiplier']
            X = df[features]
            y = df['usage']
            
            # Train model based on type
            if model_type == PredictionModel.RANDOM_FOREST:
                model = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    max_depth=10
                )
            else:  # Default to linear regression
                model = LinearRegression()
                scaler = StandardScaler()
                X = scaler.fit_transform(X)
            
            model.fit(X, y)
            
            # Calculate model accuracy
            train_score = model.score(X, y)
            
            self.prediction_models[resource_type] = {
                'model': model,
                'scaler': scaler if model_type == PredictionModel.LINEAR_REGRESSION else None,
                'features': features,
                'accuracy': train_score,
                'trained_at': datetime.now()
            }
            
            result = {
                'resource_type': resource_type.value,
                'model_type': model_type.value,
                'accuracy': train_score,
                'features_count': len(features),
                'training_samples': len(df)
            }
            
            self.logger.info(f"Trained {model_type.value} model for {resource_type.value} "
                           f"with accuracy: {train_score:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error training prediction model: {str(e)}")
            raise
    
    async def predict_capacity_demand(
        self,
        resource_type: ResourceType,
        prediction_horizon: timedelta = timedelta(days=7),
        creator_tier: Optional[CreatorTier] = None
    ) -> List[PredictionResult]:
        """
        Predict future capacity demand
        
        Args:
            resource_type: Resource type to predict
            prediction_horizon: How far ahead to predict
            creator_tier: Specific creator tier to predict for
            
        Returns:
            List of prediction results
        """
        try:
            if resource_type not in self.prediction_models:
                await self.train_prediction_models(resource_type)
            
            model_info = self.prediction_models[resource_type]
            model = model_info['model']
            scaler = model_info.get('scaler')
            features = model_info['features']
            
            predictions = []
            current_time = datetime.now()
            end_time = current_time + prediction_horizon
            
            while current_time <= end_time:
                # Prepare prediction features
                feature_data = {
                    'hour': current_time.hour,
                    'day_of_week': current_time.weekday(),
                    'month': current_time.month,
                    'is_peak': self._is_peak_hour(current_time),
                    'seasonal_factor': self._get_seasonal_factor(current_time),
                    'tier_multiplier': self._get_tier_multiplier(
                        creator_tier or CreatorTier.PROFESSIONAL
                    )
                }
                
                X_pred = np.array([[feature_data[f] for f in features]])
                
                if scaler:
                    X_pred = scaler.transform(X_pred)
                
                # Make prediction
                predicted_usage = model.predict(X_pred)[0]
                
                # Calculate confidence interval (simplified)
                confidence_range = predicted_usage * 0.15  # ±15%
                confidence_interval = (
                    predicted_usage - confidence_range,
                    predicted_usage + confidence_range
                )
                
                # Calculate recommended capacity with buffer
                recommended_capacity = predicted_usage * 1.2  # 20% buffer
                
                # Estimate cost impact
                cost_impact = self._estimate_cost_impact(
                    resource_type, recommended_capacity
                )
                
                # Risk assessment
                utilization = predicted_usage / recommended_capacity * 100
                if utilization > 85:
                    risk = "HIGH"
                elif utilization > 70:
                    risk = "MEDIUM"
                else:
                    risk = "LOW"
                
                prediction = PredictionResult(
                    resource_type=resource_type,
                    predicted_usage=predicted_usage,
                    confidence_interval=confidence_interval,
                    prediction_horizon=current_time - datetime.now(),
                    model_accuracy=model_info['accuracy'],
                    recommended_capacity=recommended_capacity,
                    cost_impact=cost_impact,
                    risk_assessment=risk
                )
                
                predictions.append(prediction)
                current_time += timedelta(hours=1)
            
            self.logger.info(f"Generated {len(predictions)} capacity predictions for "
                           f"{resource_type.value}")
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting capacity demand: {str(e)}")
            raise
    
    def _estimate_cost_impact(
        self,
        resource_type: ResourceType,
        capacity: float
    ) -> float:
        """Estimate cost impact of capacity allocation"""
        # Simplified cost model ($/hour)
        cost_per_unit = {
            ResourceType.CPU: 0.05,
            ResourceType.MEMORY: 0.01,
            ResourceType.STORAGE: 0.001,
            ResourceType.NETWORK: 0.02,
            ResourceType.GPU: 0.50,
            ResourceType.DATABASE: 0.15,
            ResourceType.CACHE: 0.08
        }
        
        return capacity * cost_per_unit.get(resource_type, 0.05)
    
    async def generate_scaling_recommendations(
        self,
        resource_type: ResourceType,
        current_capacity: float,
        prediction_horizon: timedelta = timedelta(days=30)
    ) -> List[ScalingRecommendation]:
        """
        Generate intelligent scaling recommendations
        
        Args:
            resource_type: Resource type to generate recommendations for
            current_capacity: Current resource capacity
            prediction_horizon: Time horizon for recommendations
            
        Returns:
            List of scaling recommendations
        """
        try:
            # Get capacity predictions
            predictions = await self.predict_capacity_demand(
                resource_type, prediction_horizon
            )
            
            # Analyze peak demand
            peak_demand = max(p.predicted_usage for p in predictions)
            avg_demand = sum(p.predicted_usage for p in predictions) / len(predictions)
            
            recommendations = []
            
            # Immediate scaling recommendation
            if peak_demand > current_capacity * 0.8:  # 80% threshold
                immediate_scaling = ScalingRecommendation(
                    resource_type=resource_type,
                    current_capacity=current_capacity,
                    recommended_capacity=peak_demand * 1.2,  # 20% buffer
                    scaling_factor=(peak_demand * 1.2) / current_capacity,
                    timeline=timedelta(hours=1),
                    cost_estimate=self._estimate_cost_impact(
                        resource_type, peak_demand * 1.2 - current_capacity
                    ),
                    performance_impact="Prevents resource exhaustion",
                    business_justification="Creator experience protection during peak usage"
                )
                recommendations.append(immediate_scaling)
            
            # Long-term capacity planning
            growth_rate = self._calculate_growth_rate(predictions)
            if growth_rate > 0.1:  # 10% growth
                future_capacity = current_capacity * (1 + growth_rate)
                
                longterm_scaling = ScalingRecommendation(
                    resource_type=resource_type,
                    current_capacity=current_capacity,
                    recommended_capacity=future_capacity,
                    scaling_factor=1 + growth_rate,
                    timeline=timedelta(weeks=2),
                    cost_estimate=self._estimate_cost_impact(
                        resource_type, future_capacity - current_capacity
                    ),
                    performance_impact="Supports projected growth",
                    business_justification=f"Handles {growth_rate*100:.1f}% projected growth"
                )
                recommendations.append(longterm_scaling)
            
            # Cost optimization recommendation
            if avg_demand < current_capacity * 0.5:  # Under-utilized
                optimization_rec = ScalingRecommendation(
                    resource_type=resource_type,
                    current_capacity=current_capacity,
                    recommended_capacity=avg_demand * 1.3,  # 30% buffer
                    scaling_factor=(avg_demand * 1.3) / current_capacity,
                    timeline=timedelta(days=1),
                    cost_estimate=-self._estimate_cost_impact(
                        resource_type, current_capacity - (avg_demand * 1.3)
                    ),
                    performance_impact="Maintains performance with cost savings",
                    business_justification="Resource optimization opportunity"
                )
                recommendations.append(optimization_rec)
            
            self.logger.info(f"Generated {len(recommendations)} scaling recommendations "
                           f"for {resource_type.value}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating scaling recommendations: {str(e)}")
            raise
    
    def _calculate_growth_rate(self, predictions: List[PredictionResult]) -> float:
        """Calculate growth rate from predictions"""
        if len(predictions) < 2:
            return 0.0
        
        early_avg = sum(p.predicted_usage for p in predictions[:len(predictions)//3]) / (len(predictions)//3)
        late_avg = sum(p.predicted_usage for p in predictions[-len(predictions)//3:]) / (len(predictions)//3)
        
        if early_avg == 0:
            return 0.0
        
        return (late_avg - early_avg) / early_avg
    
    async def optimize_resource_allocation(
        self,
        resources: Dict[ResourceType, float],
        budget_constraint: Optional[float] = None
    ) -> Dict[ResourceType, float]:
        """
        Optimize resource allocation across resource types
        
        Args:
            resources: Current resource allocations
            budget_constraint: Optional budget limit
            
        Returns:
            Optimized resource allocation
        """
        try:
            optimized_allocation = {}
            total_cost = 0.0
            
            for resource_type, current_allocation in resources.items():
                # Get scaling recommendations
                recommendations = await self.generate_scaling_recommendations(
                    resource_type, current_allocation
                )
                
                if recommendations:
                    # Choose the most cost-effective recommendation
                    best_rec = min(recommendations, key=lambda r: r.cost_estimate)
                    optimized_allocation[resource_type] = best_rec.recommended_capacity
                    total_cost += max(0, best_rec.cost_estimate)
                else:
                    optimized_allocation[resource_type] = current_allocation
            
            # Apply budget constraint if specified
            if budget_constraint and total_cost > budget_constraint:
                # Scale down proportionally
                scale_factor = budget_constraint / total_cost
                for resource_type in optimized_allocation:
                    optimized_allocation[resource_type] *= scale_factor
            
            self.logger.info(f"Optimized resource allocation with total cost: ${total_cost:.2f}")
            return optimized_allocation
            
        except Exception as e:
            self.logger.error(f"Error optimizing resource allocation: {str(e)}")
            raise
    
    async def generate_capacity_report(
        self,
        resource_types: List[ResourceType],
        report_period: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive capacity planning report
        
        Args:
            resource_types: List of resource types to include
            report_period: Reporting period
            
        Returns:
            Comprehensive capacity report
        """
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'report_period': str(report_period),
                'resource_analysis': {},
                'summary': {},
                'recommendations': []
            }
            
            total_cost_impact = 0.0
            high_risk_resources = []
            
            for resource_type in resource_types:
                # Get predictions and recommendations
                predictions = await self.predict_capacity_demand(resource_type, report_period)
                recommendations = await self.generate_scaling_recommendations(
                    resource_type, 1000.0  # Assume current capacity
                )
                
                # Analyze predictions
                peak_usage = max(p.predicted_usage for p in predictions)
                avg_usage = sum(p.predicted_usage for p in predictions) / len(predictions)
                high_risk_periods = len([p for p in predictions if p.risk_assessment == "HIGH"])
                
                resource_analysis = {
                    'peak_predicted_usage': peak_usage,
                    'average_predicted_usage': avg_usage,
                    'high_risk_periods': high_risk_periods,
                    'model_accuracy': predictions[0].model_accuracy if predictions else 0.0,
                    'predictions_count': len(predictions),
                    'scaling_recommendations': len(recommendations)
                }
                
                report['resource_analysis'][resource_type.value] = resource_analysis
                
                # Update summary
                if recommendations:
                    total_cost_impact += sum(r.cost_estimate for r in recommendations)
                
                if high_risk_periods > len(predictions) * 0.1:  # >10% high risk
                    high_risk_resources.append(resource_type.value)
            
            # Generate summary
            report['summary'] = {
                'total_resources_analyzed': len(resource_types),
                'total_cost_impact': total_cost_impact,
                'high_risk_resources': high_risk_resources,
                'optimization_opportunities': len([r for r in resource_types 
                                                  if any(rec.cost_estimate < 0 
                                                        for rec in await self.generate_scaling_recommendations(r, 1000.0))])
            }
            
            self.logger.info(f"Generated capacity planning report for {len(resource_types)} resources")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating capacity report: {str(e)}")
            raise
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get engine status and metrics"""
        return {
            'engine_name': 'CapacityPlanningEngine',
            'version': '1.0.0',
            'status': 'active',
            'trained_models': len(self.prediction_models),
            'supported_resources': [rt.value for rt in ResourceType],
            'prediction_accuracy': {
                rt.value: info['accuracy'] 
                for rt, info in self.prediction_models.items()
            },
            'last_training': {
                rt.value: info['trained_at'].isoformat()
                for rt, info in self.prediction_models.items()
            }
        }


# Export main classes and enums
__all__ = [
    'CapacityPlanningEngine',
    'ResourceType',
    'CreatorTier', 
    'PredictionModel',
    'CapacityMetrics',
    'PredictionResult',
    'ScalingRecommendation'
]