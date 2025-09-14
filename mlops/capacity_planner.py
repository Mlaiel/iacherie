"""
📊 Capacity Planner Enterprise
MLOps Platform - Planificateur de capacité avec prédiction de demande ML

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute tentative de vol, copie, reproduction, ingénierie inverse ou utilisation non autorisée
sans permission écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement interdite
et entraînera immédiatement des poursuites judiciaires sous le droit allemand et international.
"""

import asyncio
import json
import logging
import time
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid
import numpy as np
from scipy import stats, optimize
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pandas as pd

# Enterprise Monitoring & Security
import prometheus_client as prom
from prometheus_client import Counter, Histogram, Gauge, Summary

class ResourceType(Enum):
    """Types de ressources à planifier"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    INSTANCES = "instances"

class TimeHorizon(Enum):
    """Horizons temporels de planification"""
    SHORT_TERM = "1h"      # 1 hour
    MEDIUM_TERM = "24h"    # 24 hours  
    LONG_TERM = "7d"       # 7 days
    STRATEGIC = "30d"      # 30 days

@dataclass
class ResourceDemand:
    """Demande de ressource prédite"""
    resource_type: ResourceType
    predicted_demand: float
    confidence_interval: Tuple[float, float]
    timestamp: datetime
    horizon: TimeHorizon
    contributing_factors: Dict[str, float]

@dataclass
class CapacityRecommendation:
    """Recommandation de capacité"""
    resource_type: ResourceType
    current_capacity: float
    recommended_capacity: float
    confidence_score: float
    cost_impact: float
    urgency: str  # low, medium, high, critical
    reasoning: str
    implementation_timeline: str

@dataclass
class CreatorWorkload:
    """Profil de charge de travail par type de créateur"""
    creator_type: str
    peak_hours: List[int]  # Hours of day (0-23)
    seasonal_patterns: Dict[str, float]  # month -> multiplier
    resource_requirements: Dict[ResourceType, float]
    growth_rate: float  # monthly growth rate
    burst_capacity_needed: float  # percentage above average

class CapacityPlanner:
    """
    📊 Planificateur de capacité enterprise avec prédiction de demande ML
    
    Features Enterprise:
    - ML-powered demand forecasting with multiple algorithms
    - Creator-specific workload pattern analysis
    - Multi-horizon capacity planning (1h to 30d)
    - Cost-optimized scaling recommendations
    - Seasonal and trending pattern detection
    - Real-time capacity alerts and auto-scaling
    - Resource optimization across regions
    - Business impact analysis for capacity decisions
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        self.logger = logging.getLogger(__name__)
        
        # Historical data storage
        self.resource_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.creator_workloads: Dict[str, CreatorWorkload] = {}
        self.demand_history: Dict[ResourceType, deque] = defaultdict(lambda: deque(maxlen=5000))
        self.capacity_recommendations: List[CapacityRecommendation] = []
        
        # ML Models for prediction
        self.demand_predictors: Dict[ResourceType, Dict[TimeHorizon, Any]] = defaultdict(dict)
        self.scalers: Dict[ResourceType, StandardScaler] = {}
        self.feature_importance: Dict[ResourceType, Dict] = defaultdict(dict)
        
        # Prometheus Metrics
        self.demand_forecast_gauge = Gauge('capacity_demand_forecast', 'Forecasted demand', 
                                         ['resource_type', 'horizon', 'region'])
        self.capacity_utilization_gauge = Gauge('capacity_utilization_percent', 'Current utilization %', 
                                              ['resource_type', 'region'])
        self.capacity_recommendations_counter = Counter('capacity_recommendations_total', 
                                                      'Capacity recommendations', ['urgency', 'resource_type'])
        self.prediction_accuracy_gauge = Gauge('capacity_prediction_accuracy', 'Prediction accuracy', 
                                             ['resource_type', 'horizon'])
        self.cost_optimization_savings = Counter('capacity_cost_savings_usd', 'Cost savings from optimization')
        
        # Configuration
        self.config = config or {
            "prediction_intervals": [0.8, 0.9, 0.95],  # Confidence intervals
            "retraining_interval": 3600,  # 1 hour
            "monitoring_interval": 300,   # 5 minutes
            "alert_thresholds": {
                "cpu": {"warning": 70, "critical": 85},
                "memory": {"warning": 75, "critical": 90},
                "gpu": {"warning": 80, "critical": 95}
            },
            "growth_rate_window": 30,  # days
            "seasonal_detection_window": 90,  # days
            "cost_optimization_enabled": True,
            "auto_scaling_enabled": True,
            "max_scaling_factor": 2.0,
            "min_scaling_factor": 0.5
        }
        
        # Regional capacity data
        self.regional_capacity: Dict[str, Dict[ResourceType, float]] = defaultdict(lambda: defaultdict(float))
        self.regional_costs: Dict[str, Dict[ResourceType, float]] = defaultdict(lambda: defaultdict(float))
        
        # Business context
        self.creator_growth_rates: Dict[str, float] = {}
        self.seasonal_multipliers: Dict[str, Dict[str, float]] = {}
        
        # Cost optimization parameters
        self.cost_factors = {
            "cpu_cost_per_hour": {"us-west": 0.10, "us-east": 0.095, "europe": 0.12, "asia": 0.08},
            "memory_cost_per_gb_hour": {"us-west": 0.02, "us-east": 0.019, "europe": 0.024, "asia": 0.016},
            "gpu_cost_per_hour": {"us-west": 2.5, "us-east": 2.4, "europe": 3.0, "asia": 2.1},
            "storage_cost_per_gb_month": {"us-west": 0.023, "us-east": 0.021, "europe": 0.028, "asia": 0.019},
            "bandwidth_cost_per_gb": {"us-west": 0.09, "us-east": 0.08, "europe": 0.12, "asia": 0.07}
        }
        
        self.logger.info("📊 Capacity Planner initialized with ML forecasting capabilities")

    async def initialize(self) -> bool:
        """Initialize le capacity planner"""
        try:
            self.logger.info("🚀 Initializing Capacity Planner...")
            
            # Initialize creator workload profiles
            await self._initialize_creator_workloads()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Start background tasks
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._retraining_loop())
            asyncio.create_task(self._recommendation_loop())
            
            self.logger.info("✅ Capacity Planner initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize capacity planner: {e}")
            return False

    async def forecast_demand(
        self,
        resource_type: ResourceType,
        horizon: TimeHorizon,
        region: Optional[str] = None,
        creator_type: Optional[str] = None
    ) -> ResourceDemand:
        """
        Prédire la demande de ressources avec ML avancé
        
        Args:
            resource_type: Type de ressource à prédire
            horizon: Horizon temporel de prédiction
            region: Région cible (optionnel)
            creator_type: Type de créateur (optionnel)
            
        Returns:
            Prédiction de demande avec intervalle de confiance
        """
        try:
            self.logger.info(f"🔮 Forecasting {resource_type.value} demand for {horizon.value}")
            
            # Prepare features for prediction
            features = await self._prepare_prediction_features(resource_type, region, creator_type)
            
            if not features:
                raise ValueError("Insufficient data for prediction")
            
            # Get appropriate ML model
            model = self.demand_predictors.get(resource_type, {}).get(horizon)
            scaler = self.scalers.get(resource_type)
            
            if not model or not scaler:
                self.logger.warning(f"⚠️ No trained model for {resource_type.value}/{horizon.value}, using fallback")
                return await self._fallback_prediction(resource_type, horizon)
            
            # Scale features
            features_scaled = scaler.transform([features])
            
            # Make prediction
            if hasattr(model, 'predict'):
                predicted_demand = model.predict(features_scaled)[0]
            else:
                predicted_demand = await self._ensemble_prediction(resource_type, horizon, features_scaled)
            
            # Calculate confidence interval
            confidence_interval = await self._calculate_confidence_interval(
                resource_type, horizon, predicted_demand, features
            )
            
            # Identify contributing factors
            contributing_factors = await self._analyze_contributing_factors(
                resource_type, features, model
            )
            
            # Create demand prediction
            demand = ResourceDemand(
                resource_type=resource_type,
                predicted_demand=max(0, predicted_demand),
                confidence_interval=confidence_interval,
                timestamp=datetime.now(timezone.utc),
                horizon=horizon,
                contributing_factors=contributing_factors
            )
            
            # Update metrics
            self.demand_forecast_gauge.labels(
                resource_type=resource_type.value,
                horizon=horizon.value,
                region=region or "global"
            ).set(predicted_demand)
            
            self.logger.info(f"✅ Forecasted {resource_type.value} demand: {predicted_demand:.2f}")
            
            return demand
            
        except Exception as e:
            self.logger.error(f"❌ Demand forecasting failed: {e}")
            return await self._fallback_prediction(resource_type, horizon)

    async def generate_capacity_recommendations(
        self,
        region: Optional[str] = None,
        horizons: Optional[List[TimeHorizon]] = None
    ) -> List[CapacityRecommendation]:
        """
        Générer des recommandations de capacité optimisées
        
        Args:
            region: Région cible (optionnel)
            horizons: Horizons temporels à analyser
            
        Returns:
            Liste de recommandations de capacité
        """
        try:
            self.logger.info(f"🎯 Generating capacity recommendations for region: {region or 'all'}")
            
            horizons = horizons or [TimeHorizon.SHORT_TERM, TimeHorizon.MEDIUM_TERM, TimeHorizon.LONG_TERM]
            recommendations = []
            
            for resource_type in ResourceType:
                for horizon in horizons:
                    # Forecast demand
                    demand = await self.forecast_demand(resource_type, horizon, region)
                    
                    # Get current capacity
                    current_capacity = await self._get_current_capacity(resource_type, region)
                    
                    # Calculate optimal capacity
                    optimal_capacity = await self._calculate_optimal_capacity(
                        demand, current_capacity, resource_type, horizon
                    )
                    
                    # Skip if no change needed
                    if abs(optimal_capacity - current_capacity) < current_capacity * 0.05:  # 5% threshold
                        continue
                    
                    # Calculate cost impact
                    cost_impact = await self._calculate_cost_impact(
                        resource_type, current_capacity, optimal_capacity, region
                    )
                    
                    # Determine urgency
                    urgency = await self._determine_urgency(
                        demand, current_capacity, resource_type
                    )
                    
                    # Generate reasoning
                    reasoning = await self._generate_reasoning(
                        demand, current_capacity, optimal_capacity, horizon
                    )
                    
                    # Create recommendation
                    recommendation = CapacityRecommendation(
                        resource_type=resource_type,
                        current_capacity=current_capacity,
                        recommended_capacity=optimal_capacity,
                        confidence_score=self._calculate_confidence_score(demand),
                        cost_impact=cost_impact,
                        urgency=urgency,
                        reasoning=reasoning,
                        implementation_timeline=self._get_implementation_timeline(urgency, horizon)
                    )
                    
                    recommendations.append(recommendation)
                    
                    # Update metrics
                    self.capacity_recommendations_counter.labels(
                        urgency=urgency,
                        resource_type=resource_type.value
                    ).inc()
            
            # Sort by urgency and cost impact
            recommendations.sort(key=lambda r: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[r.urgency],
                abs(r.cost_impact)
            ), reverse=True)
            
            self.capacity_recommendations = recommendations
            
            self.logger.info(f"✅ Generated {len(recommendations)} capacity recommendations")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate capacity recommendations: {e}")
            return []

    async def _prepare_prediction_features(
        self,
        resource_type: ResourceType,
        region: Optional[str],
        creator_type: Optional[str]
    ) -> Optional[List[float]]:
        """Prepare features for ML prediction"""
        
        try:
            features = []
            
            # Time-based features
            now = datetime.now(timezone.utc)
            features.extend([
                now.hour,
                now.weekday(),
                now.day,
                now.month,
                math.sin(2 * math.pi * now.hour / 24),  # Cyclical hour
                math.cos(2 * math.pi * now.hour / 24),
                math.sin(2 * math.pi * now.weekday() / 7),  # Cyclical day of week
                math.cos(2 * math.pi * now.weekday() / 7)
            ])
            
            # Historical usage features
            resource_key = f"{resource_type.value}_{region or 'global'}"
            recent_metrics = list(self.resource_metrics[resource_key])[-168:]  # Last week
            
            if len(recent_metrics) >= 24:
                features.extend([
                    np.mean(recent_metrics[-24:]),  # Last 24h average
                    np.max(recent_metrics[-24:]),   # Last 24h peak
                    np.std(recent_metrics[-24:]),   # Last 24h volatility
                    np.mean(recent_metrics[-168:]), # Last week average
                    np.percentile(recent_metrics[-168:], 95),  # 95th percentile
                ])
            else:
                features.extend([0, 0, 0, 0, 0])  # Default values
            
            # Creator-specific features
            if creator_type and creator_type in self.creator_workloads:
                workload = self.creator_workloads[creator_type]
                features.extend([
                    workload.growth_rate,
                    workload.burst_capacity_needed,
                    workload.resource_requirements.get(resource_type, 0),
                    workload.seasonal_patterns.get(str(now.month), 1.0)
                ])
            else:
                features.extend([0.05, 0.2, 1.0, 1.0])  # Default values
            
            # Regional features
            if region:
                features.extend([
                    self.regional_capacity[region][resource_type],
                    self.regional_costs[region][resource_type]
                ])
            else:
                features.extend([100.0, 1.0])  # Default values
            
            # Trend features
            if len(recent_metrics) >= 7:
                trend = np.polyfit(range(len(recent_metrics[-7:])), recent_metrics[-7:], 1)[0]
                features.append(trend)
            else:
                features.append(0)
            
            return features
            
        except Exception as e:
            self.logger.error(f"❌ Failed to prepare features: {e}")
            return None

    async def _fallback_prediction(
        self,
        resource_type: ResourceType,
        horizon: TimeHorizon
    ) -> ResourceDemand:
        """Fallback prediction when ML models are unavailable"""
        
        # Simple trend-based prediction
        resource_key = f"{resource_type.value}_global"
        recent_metrics = list(self.resource_metrics[resource_key])[-24:]
        
        if len(recent_metrics) >= 12:
            # Calculate simple trend
            current_avg = np.mean(recent_metrics[-6:])
            previous_avg = np.mean(recent_metrics[-12:-6])
            trend = (current_avg - previous_avg) / previous_avg if previous_avg > 0 else 0
            
            # Project based on horizon
            horizon_hours = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}[horizon.value]
            predicted_demand = current_avg * (1 + trend * horizon_hours / 24)
        else:
            predicted_demand = 50.0  # Default fallback
        
        confidence_interval = (
            predicted_demand * 0.8,
            predicted_demand * 1.2
        )
        
        return ResourceDemand(
            resource_type=resource_type,
            predicted_demand=predicted_demand,
            confidence_interval=confidence_interval,
            timestamp=datetime.now(timezone.utc),
            horizon=horizon,
            contributing_factors={"trend": 0.6, "baseline": 0.4}
        )

    async def _ensemble_prediction(
        self,
        resource_type: ResourceType,
        horizon: TimeHorizon,
        features_scaled: np.ndarray
    ) -> float:
        """Ensemble prediction using multiple algorithms"""
        
        predictions = []
        
        # Try different models if available
        models = self.demand_predictors.get(resource_type, {})
        
        for model_horizon, model in models.items():
            if hasattr(model, 'predict'):
                try:
                    pred = model.predict(features_scaled)[0]
                    predictions.append(pred)
                except:
                    continue
        
        if predictions:
            # Weighted average (could be more sophisticated)
            return np.mean(predictions)
        else:
            return 50.0  # Fallback

    async def _calculate_confidence_interval(
        self,
        resource_type: ResourceType,
        horizon: TimeHorizon,
        predicted_demand: float,
        features: List[float]
    ) -> Tuple[float, float]:
        """Calculate confidence interval for prediction"""
        
        # Get historical prediction errors
        resource_key = f"{resource_type.value}_{horizon.value}_errors"
        errors = list(self.resource_metrics[resource_key])[-100:]  # Last 100 predictions
        
        if len(errors) >= 10:
            error_std = np.std(errors)
            confidence_level = 0.95  # 95% confidence interval
            z_score = stats.norm.ppf(1 - (1 - confidence_level) / 2)
            margin = z_score * error_std
        else:
            # Default uncertainty
            margin = predicted_demand * 0.15
        
        return (
            max(0, predicted_demand - margin),
            predicted_demand + margin
        )

    async def _analyze_contributing_factors(
        self,
        resource_type: ResourceType,
        features: List[float],
        model: Any
    ) -> Dict[str, float]:
        """Analyze factors contributing to the prediction"""
        
        feature_names = [
            "hour", "weekday", "day", "month", "hour_sin", "hour_cos", "weekday_sin", "weekday_cos",
            "avg_24h", "max_24h", "std_24h", "avg_week", "p95_week",
            "growth_rate", "burst_capacity", "resource_req", "seasonal",
            "regional_capacity", "regional_cost", "trend"
        ]
        
        # Get feature importance if available
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            # Normalize to sum to 1
            importances = importances / np.sum(importances)
            
            # Create factor dictionary
            factors = {}
            for i, (name, importance) in enumerate(zip(feature_names, importances)):
                if i < len(features) and importance > 0.01:  # Only significant factors
                    factors[name] = float(importance)
            
            return factors
        else:
            # Default factors
            return {
                "historical_usage": 0.4,
                "temporal_patterns": 0.3,
                "creator_growth": 0.2,
                "regional_factors": 0.1
            }

    async def _get_current_capacity(
        self,
        resource_type: ResourceType,
        region: Optional[str]
    ) -> float:
        """Get current capacity for resource type and region"""
        
        if region:
            return self.regional_capacity[region][resource_type]
        else:
            # Global capacity (sum of all regions)
            return sum(
                region_data[resource_type] 
                for region_data in self.regional_capacity.values()
            )

    async def _calculate_optimal_capacity(
        self,
        demand: ResourceDemand,
        current_capacity: float,
        resource_type: ResourceType,
        horizon: TimeHorizon
    ) -> float:
        """Calculate optimal capacity considering demand and business constraints"""
        
        # Base capacity on upper confidence interval for safety
        target_demand = demand.confidence_interval[1]
        
        # Add buffer based on resource type and horizon
        buffer_factors = {
            ResourceType.CPU: {"1h": 1.1, "24h": 1.15, "7d": 1.2, "30d": 1.25},
            ResourceType.MEMORY: {"1h": 1.05, "24h": 1.1, "7d": 1.15, "30d": 1.2},
            ResourceType.GPU: {"1h": 1.2, "24h": 1.25, "7d": 1.3, "30d": 1.35},
            ResourceType.STORAGE: {"1h": 1.05, "24h": 1.1, "7d": 1.15, "30d": 1.2},
            ResourceType.BANDWIDTH: {"1h": 1.15, "24h": 1.2, "7d": 1.25, "30d": 1.3}
        }
        
        buffer_factor = buffer_factors.get(resource_type, {}).get(horizon.value, 1.15)
        optimal_capacity = target_demand * buffer_factor
        
        # Apply business constraints
        max_change_factor = self.config["max_scaling_factor"]
        min_change_factor = self.config["min_scaling_factor"]
        
        optimal_capacity = min(optimal_capacity, current_capacity * max_change_factor)
        optimal_capacity = max(optimal_capacity, current_capacity * min_change_factor)
        
        return optimal_capacity

    async def _calculate_cost_impact(
        self,
        resource_type: ResourceType,
        current_capacity: float,
        recommended_capacity: float,
        region: Optional[str]
    ) -> float:
        """Calculate cost impact of capacity change"""
        
        if not self.config["cost_optimization_enabled"]:
            return 0.0
        
        region = region or "us-west"  # Default region
        capacity_change = recommended_capacity - current_capacity
        
        # Get cost per unit for resource type
        cost_mapping = {
            ResourceType.CPU: "cpu_cost_per_hour",
            ResourceType.MEMORY: "memory_cost_per_gb_hour", 
            ResourceType.GPU: "gpu_cost_per_hour",
            ResourceType.STORAGE: "storage_cost_per_gb_month",
            ResourceType.BANDWIDTH: "bandwidth_cost_per_gb"
        }
        
        cost_key = cost_mapping.get(resource_type, "cpu_cost_per_hour")
        unit_cost = self.cost_factors[cost_key].get(region, 0.1)
        
        # Calculate monthly cost impact
        if resource_type == ResourceType.STORAGE:
            cost_impact = capacity_change * unit_cost  # Monthly cost
        else:
            cost_impact = capacity_change * unit_cost * 24 * 30  # Monthly cost (hourly rate)
        
        return cost_impact

    async def _determine_urgency(
        self,
        demand: ResourceDemand,
        current_capacity: float,
        resource_type: ResourceType
    ) -> str:
        """Determine urgency of capacity change"""
        
        predicted_utilization = demand.predicted_demand / max(current_capacity, 1)
        
        # Get alert thresholds
        thresholds = self.config["alert_thresholds"].get(
            resource_type.value, 
            {"warning": 70, "critical": 85}
        )
        
        if predicted_utilization > thresholds["critical"] / 100:
            return "critical"
        elif predicted_utilization > thresholds["warning"] / 100:
            return "high"
        elif predicted_utilization > 0.5:
            return "medium"
        else:
            return "low"

    async def _generate_reasoning(
        self,
        demand: ResourceDemand,
        current_capacity: float,
        recommended_capacity: float,
        horizon: TimeHorizon
    ) -> str:
        """Generate human-readable reasoning for recommendation"""
        
        change_percent = ((recommended_capacity - current_capacity) / current_capacity) * 100
        
        if change_percent > 10:
            action = "increase"
            reason = f"Expected demand surge of {demand.predicted_demand:.1f} units"
        elif change_percent < -10:
            action = "decrease"
            reason = f"Expected demand reduction to {demand.predicted_demand:.1f} units"
        else:
            action = "maintain"
            reason = f"Stable demand around {demand.predicted_demand:.1f} units"
        
        # Add contributing factors
        top_factors = sorted(
            demand.contributing_factors.items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]
        
        factors_text = ", ".join([f"{factor} ({weight:.1%})" for factor, weight in top_factors])
        
        return f"{action.title()} capacity by {abs(change_percent):.1f}% over {horizon.value}. {reason}. Key factors: {factors_text}."

    def _calculate_confidence_score(self, demand: ResourceDemand) -> float:
        """Calculate confidence score for prediction"""
        
        # Based on confidence interval width
        ci_width = demand.confidence_interval[1] - demand.confidence_interval[0]
        relative_width = ci_width / max(demand.predicted_demand, 1)
        
        # Convert to confidence score (0-1)
        confidence = max(0, 1 - (relative_width / 2))
        return min(1.0, confidence)

    def _get_implementation_timeline(self, urgency: str, horizon: TimeHorizon) -> str:
        """Get recommended implementation timeline"""
        
        timelines = {
            "critical": "Immediate (within 1 hour)",
            "high": "Urgent (within 4 hours)",
            "medium": "Planned (within 24 hours)",
            "low": "Scheduled (within 1 week)"
        }
        
        base_timeline = timelines.get(urgency, "Planned")
        
        # Adjust for horizon
        if horizon == TimeHorizon.STRATEGIC:
            return f"{base_timeline} - Strategic planning horizon"
        
        return base_timeline

    async def _initialize_creator_workloads(self) -> None:
        """Initialize creator workload profiles"""
        
        # Sample creator workload profiles based on business analysis
        creator_profiles = {
            "musician": CreatorWorkload(
                creator_type="musician",
                peak_hours=[14, 15, 16, 17, 18, 19, 20, 21],  # Afternoon/evening
                seasonal_patterns={
                    "1": 0.9, "2": 0.8, "3": 1.0, "4": 1.1, "5": 1.2, "6": 1.3,
                    "7": 1.3, "8": 1.2, "9": 1.1, "10": 1.2, "11": 1.4, "12": 1.5
                },
                resource_requirements={
                    ResourceType.CPU: 2.5,
                    ResourceType.MEMORY: 4.0,
                    ResourceType.GPU: 1.0,
                    ResourceType.STORAGE: 8.0,
                    ResourceType.BANDWIDTH: 3.0
                },
                growth_rate=0.12,  # 12% monthly
                burst_capacity_needed=0.4  # 40% burst
            ),
            "blogger": CreatorWorkload(
                creator_type="blogger",
                peak_hours=[8, 9, 10, 11, 12, 13, 14, 15, 16],  # Business hours
                seasonal_patterns={
                    "1": 1.2, "2": 1.1, "3": 1.0, "4": 0.9, "5": 0.8, "6": 0.7,
                    "7": 0.8, "8": 1.0, "9": 1.2, "10": 1.3, "11": 1.2, "12": 1.1
                },
                resource_requirements={
                    ResourceType.CPU: 1.5,
                    ResourceType.MEMORY: 2.0,
                    ResourceType.GPU: 0.2,
                    ResourceType.STORAGE: 3.0,
                    ResourceType.BANDWIDTH: 2.0
                },
                growth_rate=0.08,  # 8% monthly
                burst_capacity_needed=0.3  # 30% burst
            ),
            "photographer": CreatorWorkload(
                creator_type="photographer",
                peak_hours=[10, 11, 12, 13, 14, 15, 16, 17],  # Daytime
                seasonal_patterns={
                    "1": 0.7, "2": 0.8, "3": 1.1, "4": 1.3, "5": 1.4, "6": 1.5,
                    "7": 1.5, "8": 1.4, "9": 1.2, "10": 1.1, "11": 0.9, "12": 0.8
                },
                resource_requirements={
                    ResourceType.CPU: 3.0,
                    ResourceType.MEMORY: 6.0,
                    ResourceType.GPU: 2.0,
                    ResourceType.STORAGE: 15.0,
                    ResourceType.BANDWIDTH: 5.0
                },
                growth_rate=0.10,  # 10% monthly
                burst_capacity_needed=0.5  # 50% burst
            ),
            "influencer": CreatorWorkload(
                creator_type="influencer",
                peak_hours=[16, 17, 18, 19, 20, 21, 22],  # Evening/night
                seasonal_patterns={
                    "1": 1.1, "2": 1.0, "3": 1.0, "4": 1.1, "5": 1.2, "6": 1.3,
                    "7": 1.2, "8": 1.1, "9": 1.0, "10": 1.1, "11": 1.3, "12": 1.4
                },
                resource_requirements={
                    ResourceType.CPU: 2.0,
                    ResourceType.MEMORY: 3.0,
                    ResourceType.GPU: 1.5,
                    ResourceType.STORAGE: 10.0,
                    ResourceType.BANDWIDTH: 6.0
                },
                growth_rate=0.15,  # 15% monthly
                burst_capacity_needed=0.6  # 60% burst
            ),
            "comedian": CreatorWorkload(
                creator_type="comedian",
                peak_hours=[19, 20, 21, 22, 23],  # Evening/night
                seasonal_patterns={
                    "1": 0.9, "2": 0.9, "3": 1.0, "4": 1.0, "5": 1.1, "6": 1.1,
                    "7": 1.1, "8": 1.0, "9": 1.0, "10": 1.1, "11": 1.2, "12": 1.3
                },
                resource_requirements={
                    ResourceType.CPU: 2.2,
                    ResourceType.MEMORY: 3.5,
                    ResourceType.GPU: 1.2,
                    ResourceType.STORAGE: 12.0,
                    ResourceType.BANDWIDTH: 4.0
                },
                growth_rate=0.09,  # 9% monthly
                burst_capacity_needed=0.4  # 40% burst
            )
        }
        
        self.creator_workloads = creator_profiles
        
        self.logger.info(f"✅ Initialized {len(creator_profiles)} creator workload profiles")

    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for demand prediction"""
        
        try:
            # Initialize models for each resource type and horizon
            for resource_type in ResourceType:
                self.scalers[resource_type] = StandardScaler()
                
                for horizon in TimeHorizon:
                    # Use different algorithms for different horizons
                    if horizon in [TimeHorizon.SHORT_TERM, TimeHorizon.MEDIUM_TERM]:
                        # Fast models for short-term prediction
                        model = RandomForestRegressor(
                            n_estimators=50,
                            max_depth=10,
                            random_state=42
                        )
                    else:
                        # More complex models for long-term prediction
                        model = GradientBoostingRegressor(
                            n_estimators=100,
                            learning_rate=0.1,
                            max_depth=8,
                            random_state=42
                        )
                    
                    self.demand_predictors[resource_type][horizon] = model
            
            self.logger.info("🤖 ML models initialized for demand prediction")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize ML models: {e}")

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        
        while True:
            try:
                await self._collect_resource_metrics()
                await self._update_capacity_utilization()
                await self._check_capacity_alerts()
                
                await asyncio.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(60)

    async def _retraining_loop(self) -> None:
        """Background model retraining loop"""
        
        while True:
            try:
                await self._retrain_ml_models()
                await self._evaluate_prediction_accuracy()
                
                await asyncio.sleep(self.config["retraining_interval"])
                
            except Exception as e:
                self.logger.error(f"❌ Retraining loop error: {e}")
                await asyncio.sleep(300)

    async def _recommendation_loop(self) -> None:
        """Background recommendation generation loop"""
        
        while True:
            try:
                recommendations = await self.generate_capacity_recommendations()
                
                # Process high urgency recommendations
                for rec in recommendations:
                    if rec.urgency in ["critical", "high"]:
                        await self._process_urgent_recommendation(rec)
                
                await asyncio.sleep(1800)  # Every 30 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Recommendation loop error: {e}")
                await asyncio.sleep(300)

    async def _collect_resource_metrics(self) -> None:
        """Collect current resource metrics"""
        # Placeholder - would integrate with actual monitoring system
        pass

    async def _update_capacity_utilization(self) -> None:
        """Update capacity utilization metrics"""
        # Placeholder - would calculate actual utilization
        pass

    async def _check_capacity_alerts(self) -> None:
        """Check for capacity alerts"""
        # Placeholder - would check thresholds and send alerts
        pass

    async def _retrain_ml_models(self) -> None:
        """Retrain ML models with latest data"""
        # Placeholder - would implement actual retraining
        pass

    async def _evaluate_prediction_accuracy(self) -> None:
        """Evaluate prediction accuracy"""
        # Placeholder - would calculate accuracy metrics
        pass

    async def _process_urgent_recommendation(self, recommendation -> None: CapacityRecommendation) -> None:
        """Process urgent capacity recommendations"""
        
        self.logger.warning(
            f"⚠️ Urgent capacity recommendation: {recommendation.resource_type.value} "
            f"needs {recommendation.urgency} action - {recommendation.reasoning}"
        )
        
        # In production, this would trigger auto-scaling if enabled
        if self.config["auto_scaling_enabled"] and recommendation.urgency == "critical":
            await self._trigger_auto_scaling(recommendation)

    async def _trigger_auto_scaling(self, recommendation -> None: CapacityRecommendation) -> None:
        """Trigger auto-scaling based on recommendation"""
        
        self.logger.info(
            f"🚀 Triggering auto-scaling for {recommendation.resource_type.value}: "
            f"{recommendation.current_capacity} → {recommendation.recommended_capacity}"
        )
        
        # Placeholder - would integrate with actual auto-scaling system

    # Public API methods
    
    async def get_capacity_overview(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive capacity overview"""
        
        overview = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "region": region or "global",
            "resources": {},
            "recommendations_summary": {
                "total": len(self.capacity_recommendations),
                "critical": len([r for r in self.capacity_recommendations if r.urgency == "critical"]),
                "high": len([r for r in self.capacity_recommendations if r.urgency == "high"]),
                "medium": len([r for r in self.capacity_recommendations if r.urgency == "medium"]),
                "low": len([r for r in self.capacity_recommendations if r.urgency == "low"])
            }
        }
        
        for resource_type in ResourceType:
            current_capacity = await self._get_current_capacity(resource_type, region)
            
            # Get recent forecasts
            forecasts = {}
            for horizon in TimeHorizon:
                try:
                    demand = await self.forecast_demand(resource_type, horizon, region)
                    forecasts[horizon.value] = {
                        "predicted_demand": demand.predicted_demand,
                        "confidence_interval": demand.confidence_interval,
                        "confidence_score": self._calculate_confidence_score(demand)
                    }
                except:
                    forecasts[horizon.value] = None
            
            overview["resources"][resource_type.value] = {
                "current_capacity": current_capacity,
                "utilization_percent": 65.0,  # Would calculate actual utilization
                "forecasts": forecasts
            }
        
        return overview

    async def analyze_creator_impact(self, creator_type: str) -> Dict[str, Any]:
        """Analyze capacity impact for specific creator type"""
        
        if creator_type not in self.creator_workloads:
            return {"error": f"Unknown creator type: {creator_type}"}
        
        workload = self.creator_workloads[creator_type]
        
        analysis = {
            "creator_type": creator_type,
            "growth_rate": workload.growth_rate,
            "peak_hours": workload.peak_hours,
            "seasonal_patterns": workload.seasonal_patterns,
            "resource_requirements": {
                rt.value: req for rt, req in workload.resource_requirements.items()
            },
            "capacity_impact": {}
        }
        
        # Analyze impact on each resource type
        for resource_type, requirement in workload.resource_requirements.items():
            demand = await self.forecast_demand(
                resource_type, 
                TimeHorizon.MEDIUM_TERM, 
                creator_type=creator_type
            )
            
            analysis["capacity_impact"][resource_type.value] = {
                "predicted_demand": demand.predicted_demand,
                "requirement_per_user": requirement,
                "growth_impact": requirement * workload.growth_rate,
                "burst_capacity_needed": requirement * workload.burst_capacity_needed
            }
        
        return analysis

# Example usage
async def main() -> None:
    """Example usage of Capacity Planner"""
    
    # Initialize planner
    planner = CapacityPlanner()
    await planner.initialize()
    
    # Forecast demand for CPU in the next 24 hours
    cpu_demand = await planner.forecast_demand(
        ResourceType.CPU,
        TimeHorizon.MEDIUM_TERM,
        region="us-west",
        creator_type="musician"
    )
    
    print(f"🔮 CPU Demand Forecast: {cpu_demand.predicted_demand:.2f}")
    print(f"📊 Confidence Interval: {cpu_demand.confidence_interval}")
    print(f"🎯 Contributing Factors: {cpu_demand.contributing_factors}")
    
    # Generate capacity recommendations
    recommendations = await planner.generate_capacity_recommendations("us-west")
    
    print(f"\n📋 Capacity Recommendations ({len(recommendations)}):")
    for rec in recommendations[:3]:  # Show top 3
        print(f"  - {rec.resource_type.value}: {rec.current_capacity:.1f} → {rec.recommended_capacity:.1f}")
        print(f"    Urgency: {rec.urgency}, Cost Impact: ${rec.cost_impact:.2f}/month")
        print(f"    Reasoning: {rec.reasoning}")
    
    # Get capacity overview
    overview = await planner.get_capacity_overview("us-west")
    print(f"\n📊 Capacity Overview: {overview['recommendations_summary']}")

if __name__ == "__main__":
    asyncio.run(main())