"""📈 Auto-Scaling Manager - Intelligent ML Infrastructure Scaling
================================================================
Module: ml/deployment/auto_scaling_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

📈 INTELLIGENT AUTO-SCALING
ML-aware auto-scaling with predictive analytics and cost optimization
- Predictive scaling based on historical patterns
- Multi-dimensional scaling metrics (CPU, GPU, memory, inference latency)
- Cost-aware scaling with budget constraints
- Creator workload pattern analysis
- Real-time performance optimization
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
from collections import deque, defaultdict
import math

logger = logging.getLogger(__name__)

class ScalingTrigger(Enum):
    """Auto-scaling trigger types"""
    CPU_UTILIZATION = "cpu_utilization"
    GPU_UTILIZATION = "gpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    INFERENCE_LATENCY = "inference_latency"
    QUEUE_LENGTH = "queue_length"
    REQUEST_RATE = "request_rate"
    ERROR_RATE = "error_rate"
    COST_OPTIMIZATION = "cost_optimization"
    PREDICTIVE = "predictive"
    CREATOR_DEMAND = "creator_demand"

class ScalingDirection(Enum):
    """Scaling direction"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    NO_ACTION = "no_action"

class ScalingPolicy(Enum):
    """Scaling policy types"""
    REACTIVE = "reactive"        # React to current metrics
    PREDICTIVE = "predictive"    # Predict future demand
    HYBRID = "hybrid"           # Combine reactive and predictive
    COST_OPTIMIZED = "cost_optimized"  # Minimize costs
    PERFORMANCE_FIRST = "performance_first"  # Prioritize performance

class ResourceType(Enum):
    """Resource types for scaling"""
    CPU = "cpu"
    GPU = "gpu" 
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    INSTANCES = "instances"

@dataclass
class ScalingMetric:
    """Individual scaling metric"""
    name: str
    value: float
    threshold_min: float
    threshold_max: float
    weight: float = 1.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ScalingRule:
    """Auto-scaling rule definition"""
    rule_id: str
    name: str
    trigger: ScalingTrigger
    metric_name: str
    threshold_up: float
    threshold_down: float
    scale_up_amount: int
    scale_down_amount: int
    cooldown_period: int  # seconds
    min_instances: int = 1
    max_instances: int = 100
    enabled: bool = True
    weight: float = 1.0
    conditions: List[str] = field(default_factory=list)
    
@dataclass
class PredictiveModel:
    """Predictive scaling model"""
    model_type: str = "linear_regression"
    lookback_window: int = 168  # hours (7 days)
    prediction_horizon: int = 24  # hours
    accuracy_score: float = 0.0
    last_trained: Optional[datetime] = None
    features: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScalingAction:
    """Scaling action record"""
    action_id: str
    timestamp: datetime
    trigger: ScalingTrigger
    direction: ScalingDirection
    resource_type: ResourceType
    current_capacity: int
    target_capacity: int
    reason: str
    success: bool = False
    execution_time: float = 0.0  # seconds
    cost_impact: float = 0.0  # USD
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkloadPattern:
    """Creator workload pattern analysis"""
    creator_type: str
    peak_hours: List[int] = field(default_factory=list)
    peak_days: List[int] = field(default_factory=list)  # 0=Monday
    seasonal_factors: Dict[str, float] = field(default_factory=dict)
    demand_volatility: float = 0.0
    growth_trend: float = 0.0
    typical_duration: int = 0  # minutes
    resource_intensity: Dict[ResourceType, float] = field(default_factory=dict)

class AutoScalingManager:
    """📈 Intelligent Auto-Scaling Manager for ML Infrastructure
    
    **BACKEND SENIOR + DEVOPS EXPERT IMPLEMENTATION**
    - Predictive scaling with ML-powered demand forecasting
    - Multi-dimensional resource optimization (CPU/GPU/Memory)
    - Cost-aware scaling with budget constraints
    - Creator workload pattern analysis
    - Real-time performance monitoring and optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize auto-scaling manager"""
        self.config = config or {}
        
        # Core configuration
        self.scaling_policy = ScalingPolicy(self.config.get("scaling_policy", "hybrid"))
        self.evaluation_interval = self.config.get("evaluation_interval", 60)  # seconds
        self.max_scale_per_hour = self.config.get("max_scale_per_hour", 10)
        self.cost_budget_hourly = self.config.get("cost_budget_hourly", 1000.0)  # USD
        
        # Data storage
        self.scaling_rules: Dict[str, ScalingRule] = {}
        self.metrics_history: deque = deque(maxlen=1000)
        self.scaling_history: List[ScalingAction] = []
        self.workload_patterns: Dict[str, WorkloadPattern] = {}
        self.predictive_models: Dict[str, PredictiveModel] = {}
        
        # State tracking
        self.current_capacity: Dict[ResourceType, int] = {
            ResourceType.INSTANCES: 1,
            ResourceType.CPU: 4,
            ResourceType.GPU: 0,
            ResourceType.MEMORY: 8192  # MB
        }
        self.last_scaling_action = datetime.utcnow()
        self.cost_tracking: Dict[str, float] = defaultdict(float)
        
        # Initialize default scaling rules
        self._initialize_default_rules()
        
        logger.info("📈 Auto-Scaling Manager initialized with intelligent ML scaling")

    def _initialize_default_rules(self):
        """Initialize default scaling rules"""
        
        # CPU-based scaling
        self.scaling_rules["cpu_scale"] = ScalingRule(
            rule_id="cpu_scale",
            name="CPU Utilization Scaling",
            trigger=ScalingTrigger.CPU_UTILIZATION,
            metric_name="cpu_percent",
            threshold_up=70.0,
            threshold_down=30.0,
            scale_up_amount=2,
            scale_down_amount=1,
            cooldown_period=300,  # 5 minutes
            max_instances=20
        )
        
        # GPU-based scaling for ML workloads
        self.scaling_rules["gpu_scale"] = ScalingRule(
            rule_id="gpu_scale",
            name="GPU Utilization Scaling",
            trigger=ScalingTrigger.GPU_UTILIZATION,
            metric_name="gpu_percent",
            threshold_up=80.0,
            threshold_down=20.0,
            scale_up_amount=1,
            scale_down_amount=1,
            cooldown_period=600,  # 10 minutes (GPU warmup time)
            max_instances=10,
            weight=1.5  # Higher weight for GPU scaling
        )
        
        # Inference latency scaling
        self.scaling_rules["latency_scale"] = ScalingRule(
            rule_id="latency_scale",
            name="Inference Latency Scaling",
            trigger=ScalingTrigger.INFERENCE_LATENCY,
            metric_name="inference_latency_p95",
            threshold_up=200.0,  # 200ms
            threshold_down=50.0,  # 50ms
            scale_up_amount=2,
            scale_down_amount=1,
            cooldown_period=180,  # 3 minutes
            max_instances=50,
            weight=2.0  # High priority for latency
        )
        
        # Queue length scaling
        self.scaling_rules["queue_scale"] = ScalingRule(
            rule_id="queue_scale",
            name="Request Queue Scaling",
            trigger=ScalingTrigger.QUEUE_LENGTH,
            metric_name="queue_length",
            threshold_up=10.0,
            threshold_down=2.0,
            scale_up_amount=3,
            scale_down_amount=1,
            cooldown_period=120,  # 2 minutes
            max_instances=30
        )
        
        # Predictive scaling
        self.scaling_rules["predictive_scale"] = ScalingRule(
            rule_id="predictive_scale",
            name="Predictive Demand Scaling",
            trigger=ScalingTrigger.PREDICTIVE,
            metric_name="predicted_demand",
            threshold_up=1.2,  # 20% increase predicted
            threshold_down=0.8,  # 20% decrease predicted
            scale_up_amount=2,
            scale_down_amount=1,
            cooldown_period=900,  # 15 minutes
            max_instances=40
        )

    async def evaluate_scaling(self, current_metrics: Dict[str, float]) -> List[ScalingAction]:
        """🔍 Evaluate current metrics and determine scaling actions"""
        try:
            scaling_actions = []
            
            # Store metrics for historical analysis
            metric_entry = {
                "timestamp": datetime.utcnow(),
                "metrics": current_metrics.copy()
            }
            self.metrics_history.append(metric_entry)
            
            # Check cooldown period
            time_since_last_action = (datetime.utcnow() - self.last_scaling_action).total_seconds()
            min_cooldown = min(rule.cooldown_period for rule in self.scaling_rules.values() if rule.enabled)
            
            if time_since_last_action < min_cooldown:
                logger.debug(f"📈 Scaling in cooldown period: {time_since_last_action:.0f}s < {min_cooldown}s")
                return scaling_actions
            
            # Analyze workload patterns
            await self._analyze_workload_patterns(current_metrics)
            
            # Generate predictive metrics if enabled
            if self.scaling_policy in [ScalingPolicy.PREDICTIVE, ScalingPolicy.HYBRID]:
                predicted_metrics = await self._generate_predictions()
                current_metrics.update(predicted_metrics)
            
            # Evaluate each scaling rule
            for rule in self.scaling_rules.values():
                if not rule.enabled:
                    continue
                
                action = await self._evaluate_rule(rule, current_metrics)
                if action:
                    scaling_actions.append(action)
            
            # Apply scaling policy logic
            final_actions = await self._apply_scaling_policy(scaling_actions, current_metrics)
            
            # Execute scaling actions
            for action in final_actions:
                success = await self._execute_scaling_action(action)
                action.success = success
                self.scaling_history.append(action)
                
                if success:
                    self.last_scaling_action = datetime.utcnow()
            
            # Cost optimization check
            await self._optimize_costs(current_metrics)
            
            return final_actions
            
        except Exception as e:
            logger.error(f"📈 Scaling evaluation failed: {str(e)}")
            return []

    async def _evaluate_rule(self, rule: ScalingRule, metrics: Dict[str, float]) -> Optional[ScalingAction]:
        """Evaluate individual scaling rule"""
        
        if rule.metric_name not in metrics:
            return None
        
        metric_value = metrics[rule.metric_name]
        current_instances = self.current_capacity[ResourceType.INSTANCES]
        
        # Determine scaling direction
        direction = ScalingDirection.NO_ACTION
        target_capacity = current_instances
        
        if metric_value > rule.threshold_up and current_instances < rule.max_instances:
            direction = ScalingDirection.SCALE_OUT
            target_capacity = min(current_instances + rule.scale_up_amount, rule.max_instances)
        elif metric_value < rule.threshold_down and current_instances > rule.min_instances:
            direction = ScalingDirection.SCALE_IN
            target_capacity = max(current_instances - rule.scale_down_amount, rule.min_instances)
        
        if direction == ScalingDirection.NO_ACTION:
            return None
        
        # Create scaling action
        return ScalingAction(
            action_id=f"action_{rule.rule_id}_{int(datetime.utcnow().timestamp())}",
            timestamp=datetime.utcnow(),
            trigger=rule.trigger,
            direction=direction,
            resource_type=ResourceType.INSTANCES,
            current_capacity=current_instances,
            target_capacity=target_capacity,
            reason=f"{rule.name}: {rule.metric_name}={metric_value:.2f} (threshold: {rule.threshold_up if direction == ScalingDirection.SCALE_OUT else rule.threshold_down})",
            metadata={
                "rule_id": rule.rule_id,
                "metric_value": metric_value,
                "rule_weight": rule.weight
            }
        )

    async def _apply_scaling_policy(self, actions: List[ScalingAction], 
                                  metrics: Dict[str, float]) -> List[ScalingAction]:
        """Apply scaling policy to resolve conflicts and optimize actions"""
        
        if not actions:
            return []
        
        if self.scaling_policy == ScalingPolicy.REACTIVE:
            # Only use reactive actions, prioritize by weight
            reactive_actions = [a for a in actions if a.trigger != ScalingTrigger.PREDICTIVE]
            return self._prioritize_actions(reactive_actions)
        
        elif self.scaling_policy == ScalingPolicy.PREDICTIVE:
            # Prioritize predictive actions
            predictive_actions = [a for a in actions if a.trigger == ScalingTrigger.PREDICTIVE]
            if predictive_actions:
                return self._prioritize_actions(predictive_actions)
            return self._prioritize_actions(actions[:1])  # Fallback to one reactive action
        
        elif self.scaling_policy == ScalingPolicy.HYBRID:
            # Combine reactive and predictive with weighted scoring
            return self._hybrid_action_selection(actions, metrics)
        
        elif self.scaling_policy == ScalingPolicy.COST_OPTIMIZED:
            # Select actions that minimize cost while meeting performance
            return self._cost_optimized_selection(actions, metrics)
        
        elif self.scaling_policy == ScalingPolicy.PERFORMANCE_FIRST:
            # Prioritize performance over cost
            performance_actions = [
                a for a in actions 
                if a.trigger in [ScalingTrigger.INFERENCE_LATENCY, ScalingTrigger.QUEUE_LENGTH]
            ]
            return self._prioritize_actions(performance_actions or actions)
        
        return self._prioritize_actions(actions)

    def _prioritize_actions(self, actions: List[ScalingAction]) -> List[ScalingAction]:
        """Prioritize actions by weight and impact"""
        if not actions:
            return []
        
        # Sort by rule weight (from metadata) and impact
        prioritized = sorted(actions, key=lambda a: (
            a.metadata.get("rule_weight", 1.0),
            abs(a.target_capacity - a.current_capacity)
        ), reverse=True)
        
        # Return top action to avoid conflicts
        return prioritized[:1]

    async def _hybrid_action_selection(self, actions: List[ScalingAction], 
                                     metrics: Dict[str, float]) -> List[ScalingAction]:
        """Hybrid action selection combining reactive and predictive"""
        
        # Separate reactive and predictive actions
        reactive = [a for a in actions if a.trigger != ScalingTrigger.PREDICTIVE]
        predictive = [a for a in actions if a.trigger == ScalingTrigger.PREDICTIVE]
        
        # Calculate urgency scores
        reactive_urgency = self._calculate_urgency_score(reactive, metrics)
        predictive_confidence = self._calculate_prediction_confidence()
        
        # Decision logic
        if reactive_urgency > 0.8:  # High urgency, act reactively
            return self._prioritize_actions(reactive)
        elif predictive_confidence > 0.7 and predictive:  # Good prediction confidence
            return self._prioritize_actions(predictive)
        else:
            return self._prioritize_actions(reactive[:1])  # Conservative reactive action

    def _calculate_urgency_score(self, actions: List[ScalingAction], metrics: Dict[str, float]) -> float:
        """Calculate urgency score for reactive actions"""
        if not actions:
            return 0.0
        
        urgency_scores = []
        
        for action in actions:
            rule_id = action.metadata.get("rule_id", "")
            rule = self.scaling_rules.get(rule_id)
            
            if rule and rule.metric_name in metrics:
                metric_value = metrics[rule.metric_name]
                
                if action.direction == ScalingDirection.SCALE_OUT:
                    # Urgency increases as we exceed threshold
                    urgency = (metric_value - rule.threshold_up) / rule.threshold_up
                else:
                    # Urgency for scale down is lower
                    urgency = (rule.threshold_down - metric_value) / rule.threshold_down * 0.5
                
                urgency_scores.append(max(0, urgency))
        
        return max(urgency_scores) if urgency_scores else 0.0

    def _calculate_prediction_confidence(self) -> float:
        """Calculate confidence in predictive models"""
        if not self.predictive_models:
            return 0.0
        
        confidences = [model.accuracy_score for model in self.predictive_models.values()]
        return statistics.mean(confidences) if confidences else 0.0

    async def _cost_optimized_selection(self, actions: List[ScalingAction], 
                                      metrics: Dict[str, float]) -> List[ScalingAction]:
        """Select actions optimized for cost"""
        
        if not actions:
            return []
        
        # Calculate cost impact for each action
        for action in actions:
            cost_impact = await self._calculate_cost_impact(action)
            action.cost_impact = cost_impact
        
        # Filter actions that exceed budget
        budget_remaining = self._get_remaining_budget()
        affordable_actions = [a for a in actions if a.cost_impact <= budget_remaining]
        
        if not affordable_actions:
            logger.warning("📈 No affordable scaling actions available")
            return []
        
        # Select action with best performance/cost ratio
        best_action = min(affordable_actions, key=lambda a: a.cost_impact)
        return [best_action]

    async def _calculate_cost_impact(self, action: ScalingAction) -> float:
        """Calculate cost impact of scaling action"""
        
        # Base cost per instance per hour (example rates)
        cost_rates = {
            ResourceType.INSTANCES: 0.10,  # $0.10/hour per CPU instance
            ResourceType.GPU: 2.50,       # $2.50/hour per GPU
            ResourceType.MEMORY: 0.01     # $0.01/hour per GB
        }
        
        capacity_change = action.target_capacity - action.current_capacity
        base_rate = cost_rates.get(action.resource_type, 0.10)
        
        # Calculate hourly cost impact
        hourly_impact = capacity_change * base_rate
        
        # Factor in typical usage duration
        avg_duration = self._get_average_scaling_duration(action.trigger)
        
        return hourly_impact * (avg_duration / 3600)  # Convert to total cost

    def _get_average_scaling_duration(self, trigger: ScalingTrigger) -> float:
        """Get average duration for scaling trigger in seconds"""
        
        # Analyze historical data for this trigger
        trigger_actions = [a for a in self.scaling_history if a.trigger == trigger]
        
        if len(trigger_actions) < 2:
            # Default durations by trigger type
            defaults = {
                ScalingTrigger.CPU_UTILIZATION: 1800,     # 30 minutes
                ScalingTrigger.GPU_UTILIZATION: 3600,     # 1 hour
                ScalingTrigger.INFERENCE_LATENCY: 900,    # 15 minutes
                ScalingTrigger.QUEUE_LENGTH: 600,         # 10 minutes
                ScalingTrigger.PREDICTIVE: 7200           # 2 hours
            }
            return defaults.get(trigger, 1800)
        
        # Calculate average from history
        durations = []
        for i in range(1, len(trigger_actions)):
            if trigger_actions[i].direction != trigger_actions[i-1].direction:
                duration = (trigger_actions[i].timestamp - trigger_actions[i-1].timestamp).total_seconds()
                durations.append(duration)
        
        return statistics.mean(durations) if durations else 1800

    def _get_remaining_budget(self) -> float:
        """Get remaining hourly budget"""
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        hour_key = current_hour.isoformat()
        
        spent_this_hour = self.cost_tracking.get(hour_key, 0.0)
        return max(0, self.cost_budget_hourly - spent_this_hour)

    async def _execute_scaling_action(self, action: ScalingAction) -> bool:
        """Execute scaling action"""
        try:
            execution_start = datetime.utcnow()
            
            logger.info(f"📈 Executing scaling action: {action.direction.value}")
            logger.info(f"   Resource: {action.resource_type.value}")
            logger.info(f"   Capacity: {action.current_capacity} → {action.target_capacity}")
            logger.info(f"   Reason: {action.reason}")
            
            # Simulate scaling execution (in production, integrate with orchestrator)
            await asyncio.sleep(1)  # Simulate execution time
            
            # Update current capacity
            self.current_capacity[action.resource_type] = action.target_capacity
            
            # Track cost
            cost_impact = action.cost_impact
            if cost_impact > 0:
                current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
                hour_key = current_hour.isoformat()
                self.cost_tracking[hour_key] += cost_impact
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - execution_start).total_seconds()
            action.execution_time = execution_time
            
            logger.info(f"✅ Scaling action completed in {execution_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"📈 Scaling action failed: {str(e)}")
            return False

    async def _analyze_workload_patterns(self, metrics: Dict[str, float]):
        """Analyze and update workload patterns"""
        
        current_time = datetime.utcnow()
        hour = current_time.hour
        weekday = current_time.weekday()
        
        # Detect creator-specific patterns
        creator_types = ["musician", "blogger", "photographer", "influencer"]
        
        for creator_type in creator_types:
            if creator_type not in self.workload_patterns:
                self.workload_patterns[creator_type] = WorkloadPattern(creator_type=creator_type)
            
            pattern = self.workload_patterns[creator_type]
            
            # Update peak hours detection
            demand_indicator = metrics.get(f"{creator_type}_demand", metrics.get("request_rate", 0))
            
            if demand_indicator > 0:
                # Simple peak detection (could be enhanced with ML)
                avg_demand = sum(metrics.get(f"{ct}_demand", 0) for ct in creator_types) / len(creator_types)
                
                if demand_indicator > avg_demand * 1.5:  # 50% above average
                    if hour not in pattern.peak_hours:
                        pattern.peak_hours.append(hour)
                    
                    if weekday not in pattern.peak_days:
                        pattern.peak_days.append(weekday)
                
                # Update resource intensity
                for resource in ResourceType:
                    resource_metric = metrics.get(f"{resource.value}_utilization", 0)
                    if resource not in pattern.resource_intensity:
                        pattern.resource_intensity[resource] = resource_metric
                    else:
                        # Exponential moving average
                        alpha = 0.1
                        pattern.resource_intensity[resource] = (
                            alpha * resource_metric + 
                            (1 - alpha) * pattern.resource_intensity[resource]
                        )

    async def _generate_predictions(self) -> Dict[str, float]:
        """Generate predictive metrics using ML models"""
        
        try:
            predictions = {}
            
            # Simple time-series prediction (can be enhanced with advanced ML)
            if len(self.metrics_history) >= 24:  # Need at least 24 data points
                
                # Extract recent metrics for prediction
                recent_metrics = list(self.metrics_history)[-24:]
                
                # Predict demand for next hour
                demand_values = [m["metrics"].get("request_rate", 0) for m in recent_metrics]
                
                if demand_values:
                    # Simple linear trend prediction
                    x = np.arange(len(demand_values))
                    y = np.array(demand_values)
                    
                    if len(y) > 1 and np.std(y) > 0:
                        # Linear regression
                        slope, intercept = np.polyfit(x, y, 1)
                        next_hour_pred = slope * len(y) + intercept
                        
                        # Apply seasonal adjustments
                        seasonal_factor = self._get_seasonal_factor()
                        next_hour_pred *= seasonal_factor
                        
                        # Calculate predicted demand ratio
                        current_demand = demand_values[-1] if demand_values else 1
                        demand_ratio = next_hour_pred / max(current_demand, 1)
                        
                        predictions["predicted_demand"] = demand_ratio
                        
                        # Predict resource utilization
                        cpu_values = [m["metrics"].get("cpu_percent", 0) for m in recent_metrics]
                        if cpu_values:
                            cpu_slope, cpu_intercept = np.polyfit(x, np.array(cpu_values), 1)
                            predictions["predicted_cpu"] = cpu_slope * len(y) + cpu_intercept
                        
                        logger.debug(f"📈 Generated predictions: demand_ratio={demand_ratio:.3f}")
            
            return predictions
            
        except Exception as e:
            logger.warning(f"📈 Prediction generation failed: {str(e)}")
            return {}

    def _get_seasonal_factor(self) -> float:
        """Get seasonal adjustment factor"""
        
        current_time = datetime.utcnow()
        hour = current_time.hour
        weekday = current_time.weekday()
        
        # Simple seasonal factors (can be learned from data)
        hour_factors = {
            # Morning rush
            8: 1.2, 9: 1.3, 10: 1.2,
            # Lunch time
            12: 1.1, 13: 1.1,
            # Evening peak
            18: 1.4, 19: 1.5, 20: 1.4, 21: 1.3,
            # Late night low
            23: 0.7, 0: 0.6, 1: 0.5, 2: 0.5, 3: 0.5, 4: 0.6, 5: 0.7
        }
        
        weekday_factors = {
            0: 1.0,   # Monday
            1: 1.1,   # Tuesday
            2: 1.1,   # Wednesday  
            3: 1.2,   # Thursday
            4: 1.3,   # Friday
            5: 0.8,   # Saturday
            6: 0.7    # Sunday
        }
        
        hour_factor = hour_factors.get(hour, 1.0)
        weekday_factor = weekday_factors.get(weekday, 1.0)
        
        return hour_factor * weekday_factor

    async def _optimize_costs(self, metrics: Dict[str, float]):
        """Perform cost optimization analysis"""
        
        # Check if we're exceeding budget
        remaining_budget = self._get_remaining_budget()
        
        if remaining_budget < self.cost_budget_hourly * 0.1:  # Less than 10% budget remaining
            logger.warning(f"📈 Budget nearly exhausted: ${remaining_budget:.2f} remaining")
            
            # Suggest cost-saving actions
            suggestions = await self._generate_cost_saving_suggestions(metrics)
            
            for suggestion in suggestions:
                logger.info(f"💰 Cost optimization suggestion: {suggestion}")

    async def _generate_cost_saving_suggestions(self, metrics: Dict[str, float]) -> List[str]:
        """Generate cost-saving suggestions"""
        
        suggestions = []
        current_instances = self.current_capacity[ResourceType.INSTANCES]
        
        # Check for over-provisioning
        cpu_utilization = metrics.get("cpu_percent", 0)
        if cpu_utilization < 20 and current_instances > 1:
            suggestions.append(f"Consider scaling down: CPU utilization is only {cpu_utilization:.1f}%")
        
        # Check for GPU under-utilization
        gpu_utilization = metrics.get("gpu_percent", 0)
        gpu_instances = self.current_capacity.get(ResourceType.GPU, 0)
        if gpu_utilization < 30 and gpu_instances > 0:
            suggestions.append(f"GPU under-utilized at {gpu_utilization:.1f}% - consider CPU-only instances for current workload")
        
        # Check queue length
        queue_length = metrics.get("queue_length", 0)
        if queue_length == 0 and current_instances > 2:
            suggestions.append("No queued requests - consider reducing instance count")
        
        return suggestions

    async def get_scaling_dashboard(self) -> Dict[str, Any]:
        """📊 Generate scaling dashboard metrics"""
        
        # Current status
        current_status = {
            "current_capacity": dict(self.current_capacity),
            "active_rules": len([r for r in self.scaling_rules.values() if r.enabled]),
            "scaling_policy": self.scaling_policy.value,
            "last_action": self.last_scaling_action.isoformat() if self.last_scaling_action else None
        }
        
        # Historical metrics
        if self.scaling_history:
            recent_actions = [a for a in self.scaling_history 
                            if datetime.utcnow() - a.timestamp < timedelta(hours=24)]
            
            historical_metrics = {
                "total_scaling_actions": len(self.scaling_history),
                "actions_last_24h": len(recent_actions),
                "success_rate": sum(a.success for a in self.scaling_history) / len(self.scaling_history),
                "avg_execution_time": statistics.mean(a.execution_time for a in self.scaling_history if a.execution_time > 0),
                "scaling_triggers": {
                    trigger.value: len([a for a in recent_actions if a.trigger == trigger])
                    for trigger in ScalingTrigger
                }
            }
        else:
            historical_metrics = {
                "total_scaling_actions": 0,
                "actions_last_24h": 0,
                "success_rate": 1.0,
                "avg_execution_time": 0.0,
                "scaling_triggers": {}
            }
        
        # Cost analysis
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        hour_key = current_hour.isoformat()
        
        cost_analysis = {
            "hourly_budget": self.cost_budget_hourly,
            "spent_current_hour": self.cost_tracking.get(hour_key, 0.0),
            "remaining_budget": self._get_remaining_budget(),
            "total_cost_24h": sum(
                cost for timestamp, cost in self.cost_tracking.items()
                if datetime.fromisoformat(timestamp) > datetime.utcnow() - timedelta(hours=24)
            )
        }
        
        # Workload patterns
        pattern_summary = {}
        for creator_type, pattern in self.workload_patterns.items():
            pattern_summary[creator_type] = {
                "peak_hours": pattern.peak_hours,
                "peak_days": pattern.peak_days,
                "demand_volatility": pattern.demand_volatility,
                "primary_resources": [
                    resource.value for resource, intensity in pattern.resource_intensity.items()
                    if intensity > 0.5
                ]
            }
        
        return {
            "current_status": current_status,
            "historical_metrics": historical_metrics,
            "cost_analysis": cost_analysis,
            "workload_patterns": pattern_summary,
            "predictive_models": {
                name: {
                    "type": model.model_type,
                    "accuracy": model.accuracy_score,
                    "last_trained": model.last_trained.isoformat() if model.last_trained else None
                }
                for name, model in self.predictive_models.items()
            }
        }

    async def add_scaling_rule(self, rule: ScalingRule):
        """Add custom scaling rule"""
        self.scaling_rules[rule.rule_id] = rule
        logger.info(f"📈 Added scaling rule: {rule.name}")

    async def update_scaling_policy(self, policy: ScalingPolicy):
        """Update scaling policy"""
        old_policy = self.scaling_policy
        self.scaling_policy = policy
        logger.info(f"📈 Updated scaling policy: {old_policy.value} → {policy.value}")

    def __repr__(self) -> str:
        return f"AutoScalingManager(policy={self.scaling_policy.value}, rules={len(self.scaling_rules)}, instances={self.current_capacity[ResourceType.INSTANCES]})"

# 📈 BACKEND SENIOR + DEVOPS EXPERT - Intelligent Auto-Scaling Complete
# Predictive scaling, cost optimization, and creator workload pattern analysis