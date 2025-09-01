"""Capacity Planning and Cost Optimization System
Automated capacity planning with predictive analytics and cost optimization recommendations
"""

import asyncio
import json
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import math

# Import monitoring systems
from ..health.health_checks import SystemMetrics
from ..sla_monitoring.sla_tracker import sla_tracker

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources for capacity planning"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    COMPUTE_INSTANCES = "compute_instances"
    LOAD_BALANCERS = "load_balancers"


class PredictionModel(Enum):
    """Prediction models for capacity planning"""
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    MACHINE_LEARNING = "machine_learning"


class OptimizationStrategy(Enum):
    """Cost optimization strategies"""
    RIGHT_SIZING = "right_sizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    AUTO_SCALING = "auto_scaling"
    SCHEDULING = "scheduling"
    STORAGE_OPTIMIZATION = "storage_optimization"


@dataclass
class ResourceMetric:
    """Resource utilization metric"""
    timestamp: datetime
    resource_type: ResourceType
    current_usage: float
    capacity: float
    utilization_percent: float
    cost_per_hour: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapacityPrediction:
    """Capacity prediction result"""
    resource_type: ResourceType
    prediction_date: datetime
    predicted_usage: float
    predicted_utilization_percent: float
    confidence_interval: Tuple[float, float]
    recommended_capacity: float
    current_capacity: float
    scaling_required: bool
    model_used: PredictionModel
    accuracy_score: float = 0.0


@dataclass
class CostOptimizationRecommendation:
    """Cost optimization recommendation"""
    strategy: OptimizationStrategy
    resource_type: ResourceType
    current_cost_monthly: float
    optimized_cost_monthly: float
    savings_monthly: float
    savings_percentage: float
    implementation_effort: str  # "low", "medium", "high"
    risk_level: str  # "low", "medium", "high"
    description: str
    implementation_steps: List[str] = field(default_factory=list)
    roi_months: int = 1  # Return on investment timeline


@dataclass
class CapacityPlanningReport:
    """Comprehensive capacity planning report"""
    timestamp: datetime
    planning_horizon_days: int
    resource_predictions: List[CapacityPrediction]
    cost_optimizations: List[CostOptimizationRecommendation]
    current_total_cost_monthly: float
    optimized_total_cost_monthly: float
    total_potential_savings_monthly: float
    capacity_alerts: List[str]
    recommendations_summary: Dict[str, Any]


class CapacityPlanningOrchestrator:
    """
    Orchestrator for automated capacity planning with predictive analytics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[ResourceMetric] = []
        self.predictions_cache: Dict[str, CapacityPrediction] = {}
        self.system_metrics = SystemMetrics()
        
        # Configuration
        self.prediction_horizon_days = 30
        self.confidence_threshold = 0.8
        self.scaling_threshold_percent = 80
        
        # Cost configuration (would be loaded from cloud provider APIs)
        self.cost_config = {
            ResourceType.CPU: {"cost_per_vcpu_hour": 0.05},
            ResourceType.MEMORY: {"cost_per_gb_hour": 0.01},
            ResourceType.STORAGE: {"cost_per_gb_month": 0.10},
            ResourceType.COMPUTE_INSTANCES: {"cost_per_instance_hour": 0.50},
            ResourceType.DATABASE: {"cost_per_instance_hour": 0.30},
            ResourceType.LOAD_BALANCERS: {"cost_per_hour": 0.025}
        }
    
    async def initialize(self) -> bool:
        """Initialize capacity planning system"""
        try:
            # Start metrics collection
            asyncio.create_task(self._metrics_collection_loop())
            
            self.logger.info("Capacity planning orchestrator initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize capacity planning: {e}")
            return False
    
    async def _metrics_collection_loop(self):
        """Continuous metrics collection loop"""
        while True:
            try:
                await self._collect_current_metrics()
                await asyncio.sleep(300)  # Collect every 5 minutes
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _collect_current_metrics(self):
        """Collect current resource metrics"""
        try:
            timestamp = datetime.now()
            system_stats = self.system_metrics.get_system_stats()
            app_stats = self.system_metrics.get_application_stats()
            
            # CPU metrics
            cpu_metric = ResourceMetric(
                timestamp=timestamp,
                resource_type=ResourceType.CPU,
                current_usage=system_stats["cpu_percent"],
                capacity=100.0,
                utilization_percent=system_stats["cpu_percent"],
                cost_per_hour=self._calculate_cpu_cost(system_stats["cpu_percent"]),
                metadata={"cores": 4}  # Would be detected dynamically
            )
            self.metrics_history.append(cpu_metric)
            
            # Memory metrics
            memory_used_gb = (system_stats["memory"]["total"] - system_stats["memory"]["available"]) / (1024**3)
            memory_total_gb = system_stats["memory"]["total"] / (1024**3)
            
            memory_metric = ResourceMetric(
                timestamp=timestamp,
                resource_type=ResourceType.MEMORY,
                current_usage=memory_used_gb,
                capacity=memory_total_gb,
                utilization_percent=system_stats["memory"]["percent"],
                cost_per_hour=self._calculate_memory_cost(memory_used_gb),
                metadata={"total_gb": memory_total_gb}
            )
            self.metrics_history.append(memory_metric)
            
            # Storage metrics
            storage_used_gb = (system_stats["disk"]["total"] - system_stats["disk"]["free"]) / (1024**3)
            storage_total_gb = system_stats["disk"]["total"] / (1024**3)
            
            storage_metric = ResourceMetric(
                timestamp=timestamp,
                resource_type=ResourceType.STORAGE,
                current_usage=storage_used_gb,
                capacity=storage_total_gb,
                utilization_percent=system_stats["disk"]["percent"],
                cost_per_hour=self._calculate_storage_cost(storage_used_gb),
                metadata={"total_gb": storage_total_gb}
            )
            self.metrics_history.append(storage_metric)
            
            # Keep only recent metrics (last 7 days)
            cutoff_time = timestamp - timedelta(days=7)
            self.metrics_history = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
    
    def _calculate_cpu_cost(self, cpu_percent: float) -> float:
        """Calculate CPU cost based on usage"""
        cores = 4  # Would be detected dynamically
        cost_per_core_hour = self.cost_config[ResourceType.CPU]["cost_per_vcpu_hour"]
        return cores * cost_per_core_hour
    
    def _calculate_memory_cost(self, memory_gb: float) -> float:
        """Calculate memory cost"""
        cost_per_gb_hour = self.cost_config[ResourceType.MEMORY]["cost_per_gb_hour"]
        return memory_gb * cost_per_gb_hour
    
    def _calculate_storage_cost(self, storage_gb: float) -> float:
        """Calculate storage cost"""
        cost_per_gb_month = self.cost_config[ResourceType.STORAGE]["cost_per_gb_month"]
        return storage_gb * cost_per_gb_month / (24 * 30)  # Convert to hourly
    
    async def generate_capacity_predictions(self, resource_types: List[ResourceType] = None, 
                                          horizon_days: int = None) -> List[CapacityPrediction]:
        """Generate capacity predictions for specified resources"""
        if resource_types is None:
            resource_types = [ResourceType.CPU, ResourceType.MEMORY, ResourceType.STORAGE]
        
        if horizon_days is None:
            horizon_days = self.prediction_horizon_days
        
        predictions = []
        
        for resource_type in resource_types:
            try:
                prediction = await self._predict_resource_capacity(resource_type, horizon_days)
                if prediction:
                    predictions.append(prediction)
            except Exception as e:
                self.logger.error(f"Error predicting capacity for {resource_type}: {e}")
        
        return predictions
    
    async def _predict_resource_capacity(self, resource_type: ResourceType, 
                                       horizon_days: int) -> Optional[CapacityPrediction]:
        """Predict capacity for a specific resource type"""
        try:
            # Get historical data for the resource
            resource_metrics = [m for m in self.metrics_history if m.resource_type == resource_type]
            
            if len(resource_metrics) < 10:  # Need minimum data points
                self.logger.warning(f"Insufficient data for {resource_type} prediction")
                return None
            
            # Sort by timestamp
            resource_metrics.sort(key=lambda x: x.timestamp)
            
            # Extract utilization percentages and timestamps
            utilizations = [m.utilization_percent for m in resource_metrics]
            timestamps = [m.timestamp for m in resource_metrics]
            
            # Use linear regression for prediction (simplified)
            predicted_utilization = await self._linear_regression_predict(
                utilizations, timestamps, horizon_days
            )
            
            # Calculate recommended capacity
            current_capacity = resource_metrics[-1].capacity if resource_metrics else 100.0
            current_utilization = utilizations[-1] if utilizations else 0.0
            
            # Add safety margin
            safety_margin = 1.2  # 20% safety margin
            recommended_capacity = (predicted_utilization / 100.0) * current_capacity * safety_margin
            
            # Determine if scaling is required
            scaling_required = predicted_utilization > self.scaling_threshold_percent
            
            # Calculate confidence interval (simplified)
            confidence_range = predicted_utilization * 0.1  # ±10%
            confidence_interval = (
                max(0, predicted_utilization - confidence_range),
                min(100, predicted_utilization + confidence_range)
            )
            
            prediction = CapacityPrediction(
                resource_type=resource_type,
                prediction_date=datetime.now() + timedelta(days=horizon_days),
                predicted_usage=(predicted_utilization / 100.0) * current_capacity,
                predicted_utilization_percent=predicted_utilization,
                confidence_interval=confidence_interval,
                recommended_capacity=recommended_capacity,
                current_capacity=current_capacity,
                scaling_required=scaling_required,
                model_used=PredictionModel.LINEAR_REGRESSION,
                accuracy_score=0.85  # Would be calculated based on historical accuracy
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error in capacity prediction for {resource_type}: {e}")
            return None
    
    async def _linear_regression_predict(self, values: List[float], timestamps: List[datetime], 
                                       horizon_days: int) -> float:
        """Simple linear regression prediction"""
        if len(values) < 2:
            return values[0] if values else 0.0
        
        # Convert timestamps to numeric values (days since first timestamp)
        base_time = timestamps[0]
        x_values = [(ts - base_time).total_seconds() / (24 * 3600) for ts in timestamps]
        y_values = values
        
        # Calculate linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Predict for future date
        future_x = x_values[-1] + horizon_days
        predicted_value = slope * future_x + intercept
        
        # Ensure reasonable bounds
        return max(0.0, min(100.0, predicted_value))
    
    async def generate_cost_optimization_recommendations(self) -> List[CostOptimizationRecommendation]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        try:
            # Get current resource utilization
            recent_metrics = [m for m in self.metrics_history 
                            if m.timestamp >= datetime.now() - timedelta(hours=24)]
            
            if not recent_metrics:
                return recommendations
            
            # Group metrics by resource type
            metrics_by_type = {}
            for metric in recent_metrics:
                if metric.resource_type not in metrics_by_type:
                    metrics_by_type[metric.resource_type] = []
                metrics_by_type[metric.resource_type].append(metric)
            
            # Generate recommendations for each resource type
            for resource_type, metrics in metrics_by_type.items():
                avg_utilization = statistics.mean([m.utilization_percent for m in metrics])
                current_cost = statistics.mean([m.cost_per_hour for m in metrics]) * 24 * 30
                
                # Right-sizing recommendations
                if avg_utilization < 30:  # Under-utilized
                    savings = current_cost * 0.4  # 40% savings through right-sizing
                    recommendations.append(CostOptimizationRecommendation(
                        strategy=OptimizationStrategy.RIGHT_SIZING,
                        resource_type=resource_type,
                        current_cost_monthly=current_cost,
                        optimized_cost_monthly=current_cost - savings,
                        savings_monthly=savings,
                        savings_percentage=(savings / current_cost) * 100,
                        implementation_effort="medium",
                        risk_level="low",
                        description=f"Right-size {resource_type.value} resources - currently only {avg_utilization:.1f}% utilized",
                        implementation_steps=[
                            f"Analyze {resource_type.value} usage patterns",
                            f"Reduce {resource_type.value} allocation by 40%",
                            "Monitor performance after change",
                            "Adjust if needed"
                        ]
                    ))
                
                # Auto-scaling recommendations
                if resource_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.COMPUTE_INSTANCES]:
                    utilization_variance = statistics.variance([m.utilization_percent for m in metrics]) if len(metrics) > 1 else 0
                    
                    if utilization_variance > 400:  # High variance suggests auto-scaling benefits
                        savings = current_cost * 0.25  # 25% savings through auto-scaling
                        recommendations.append(CostOptimizationRecommendation(
                            strategy=OptimizationStrategy.AUTO_SCALING,
                            resource_type=resource_type,
                            current_cost_monthly=current_cost,
                            optimized_cost_monthly=current_cost - savings,
                            savings_monthly=savings,
                            savings_percentage=(savings / current_cost) * 100,
                            implementation_effort="high",
                            risk_level="medium",
                            description=f"Implement auto-scaling for {resource_type.value} to handle variable workloads",
                            implementation_steps=[
                                "Configure auto-scaling policies",
                                "Set up monitoring and alerts",
                                "Test scaling behavior",
                                "Optimize scaling parameters"
                            ]
                        ))
                
                # Reserved instances recommendations (for compute resources)
                if resource_type == ResourceType.COMPUTE_INSTANCES and avg_utilization > 70:
                    savings = current_cost * 0.30  # 30% savings with reserved instances
                    recommendations.append(CostOptimizationRecommendation(
                        strategy=OptimizationStrategy.RESERVED_INSTANCES,
                        resource_type=resource_type,
                        current_cost_monthly=current_cost,
                        optimized_cost_monthly=current_cost - savings,
                        savings_monthly=savings,
                        savings_percentage=(savings / current_cost) * 100,
                        implementation_effort="low",
                        risk_level="low",
                        description="Purchase reserved instances for consistent workloads",
                        implementation_steps=[
                            "Analyze usage patterns",
                            "Purchase 1-year reserved instances",
                            "Monitor usage and adjust as needed"
                        ],
                        roi_months=3
                    ))
                
                # Storage optimization
                if resource_type == ResourceType.STORAGE:
                    savings = current_cost * 0.20  # 20% savings through storage optimization
                    recommendations.append(CostOptimizationRecommendation(
                        strategy=OptimizationStrategy.STORAGE_OPTIMIZATION,
                        resource_type=resource_type,
                        current_cost_monthly=current_cost,
                        optimized_cost_monthly=current_cost - savings,
                        savings_monthly=savings,
                        savings_percentage=(savings / current_cost) * 100,
                        implementation_effort="medium",
                        risk_level="low",
                        description="Optimize storage with tiering and compression",
                        implementation_steps=[
                            "Implement data lifecycle policies",
                            "Enable compression",
                            "Move infrequent data to cheaper storage tiers",
                            "Clean up unused data"
                        ]
                    ))
            
        except Exception as e:
            self.logger.error(f"Error generating cost optimization recommendations: {e}")
        
        # Sort recommendations by savings amount
        recommendations.sort(key=lambda x: x.savings_monthly, reverse=True)
        
        return recommendations
    
    async def generate_comprehensive_report(self) -> CapacityPlanningReport:
        """Generate comprehensive capacity planning and cost optimization report"""
        try:
            # Generate predictions
            predictions = await self.generate_capacity_predictions()
            
            # Generate cost optimizations
            cost_optimizations = await self.generate_cost_optimization_recommendations()
            
            # Calculate current and optimized costs
            current_total_cost = sum(opt.current_cost_monthly for opt in cost_optimizations)
            optimized_total_cost = sum(opt.optimized_cost_monthly for opt in cost_optimizations)
            total_savings = sum(opt.savings_monthly for opt in cost_optimizations)
            
            # Generate capacity alerts
            capacity_alerts = []
            for prediction in predictions:
                if prediction.scaling_required:
                    capacity_alerts.append(
                        f"⚠️ {prediction.resource_type.value.title()} capacity scaling required - "
                        f"predicted {prediction.predicted_utilization_percent:.1f}% utilization"
                    )
                
                if prediction.predicted_utilization_percent > 95:
                    capacity_alerts.append(
                        f"🚨 Critical: {prediction.resource_type.value.title()} predicted to reach "
                        f"{prediction.predicted_utilization_percent:.1f}% utilization"
                    )
            
            # Generate recommendations summary
            optimization_by_strategy = {}
            for opt in cost_optimizations:
                strategy = opt.strategy.value
                if strategy not in optimization_by_strategy:
                    optimization_by_strategy[strategy] = {
                        "count": 0,
                        "total_savings": 0,
                        "avg_roi_months": 0
                    }
                optimization_by_strategy[strategy]["count"] += 1
                optimization_by_strategy[strategy]["total_savings"] += opt.savings_monthly
                optimization_by_strategy[strategy]["avg_roi_months"] = opt.roi_months
            
            recommendations_summary = {
                "high_impact_optimizations": len([o for o in cost_optimizations if o.savings_monthly > 1000]),
                "quick_wins": len([o for o in cost_optimizations if o.implementation_effort == "low"]),
                "optimization_strategies": optimization_by_strategy,
                "capacity_scaling_needed": len([p for p in predictions if p.scaling_required])
            }
            
            report = CapacityPlanningReport(
                timestamp=datetime.now(),
                planning_horizon_days=self.prediction_horizon_days,
                resource_predictions=predictions,
                cost_optimizations=cost_optimizations,
                current_total_cost_monthly=current_total_cost,
                optimized_total_cost_monthly=optimized_total_cost,
                total_potential_savings_monthly=total_savings,
                capacity_alerts=capacity_alerts,
                recommendations_summary=recommendations_summary
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating capacity planning report: {e}")
            raise


class CostOptimizationEngine:
    """
    Engine for continuous cost optimization monitoring and recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.capacity_planner = CapacityPlanningOrchestrator()
        self.optimization_history: List[CostOptimizationRecommendation] = []
        self.implemented_optimizations: List[Dict[str, Any]] = []
    
    async def initialize(self) -> bool:
        """Initialize cost optimization engine"""
        try:
            await self.capacity_planner.initialize()
            
            # Start continuous optimization monitoring
            asyncio.create_task(self._optimization_monitoring_loop())
            
            self.logger.info("Cost optimization engine initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize cost optimization engine: {e}")
            return False
    
    async def _optimization_monitoring_loop(self):
        """Continuous cost optimization monitoring"""
        while True:
            try:
                # Generate recommendations daily
                recommendations = await self.capacity_planner.generate_cost_optimization_recommendations()
                
                # Check for new high-impact recommendations
                high_impact_recs = [r for r in recommendations if r.savings_monthly > 500]
                
                if high_impact_recs:
                    self.logger.info(f"Found {len(high_impact_recs)} high-impact cost optimization opportunities")
                    
                    # Store recommendations
                    self.optimization_history.extend(recommendations)
                    
                    # Keep only recent history
                    cutoff_date = datetime.now() - timedelta(days=30)
                    self.optimization_history = [
                        r for r in self.optimization_history 
                        if hasattr(r, 'timestamp') and r.timestamp >= cutoff_date
                    ]
                
                # Sleep for 24 hours
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                self.logger.error(f"Error in cost optimization monitoring: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def get_optimization_dashboard(self) -> Dict[str, Any]:
        """Get cost optimization dashboard data"""
        try:
            # Get latest report
            report = await self.capacity_planner.generate_comprehensive_report()
            
            # Calculate potential ROI
            annual_savings = report.total_potential_savings_monthly * 12
            implementation_costs = len(report.cost_optimizations) * 1000  # Estimate $1000 per optimization
            
            return {
                "timestamp": datetime.now().isoformat(),
                "current_monthly_cost": report.current_total_cost_monthly,
                "optimized_monthly_cost": report.optimized_total_cost_monthly,
                "potential_monthly_savings": report.total_potential_savings_monthly,
                "potential_annual_savings": annual_savings,
                "savings_percentage": (report.total_potential_savings_monthly / 
                                     max(report.current_total_cost_monthly, 1)) * 100,
                "roi_estimate": {
                    "annual_savings": annual_savings,
                    "implementation_cost": implementation_costs,
                    "payback_months": max(1, implementation_costs / max(report.total_potential_savings_monthly, 1))
                },
                "optimization_opportunities": len(report.cost_optimizations),
                "high_impact_opportunities": len([o for o in report.cost_optimizations if o.savings_monthly > 500]),
                "quick_wins": len([o for o in report.cost_optimizations if o.implementation_effort == "low"]),
                "capacity_alerts": report.capacity_alerts,
                "top_recommendations": sorted(
                    report.cost_optimizations, 
                    key=lambda x: x.savings_monthly, 
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating optimization dashboard: {e}")
            return {"error": str(e)}


# Global instances
capacity_planning_orchestrator = CapacityPlanningOrchestrator()
cost_optimization_engine = CostOptimizationEngine()