"""
🛡️ MLOps Operations & Reliability - Auto Scaling Intelligence
==============================================================

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

Enterprise auto-scaling intelligence for Creator Economy predictive scaling.
Combining expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
import numpy as np
from collections import defaultdict, deque
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd


class ScalingDirection(Enum):
    """Scaling direction"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    MAINTAIN = "maintain"


class ScalingTrigger(Enum):
    """Scaling trigger types"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    CUSTOM_METRIC = "custom_metric"
    PREDICTIVE = "predictive"
    CREATOR_ACTIVITY = "creator_activity"


class CreatorTier(Enum):
    """Creator tier for scaling decisions"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class ScalingPolicy(Enum):
    """Scaling policy types"""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"
    CREATOR_AWARE = "creator_aware"


class ResourceType(Enum):
    """Resource types for scaling"""
    CPU = "cpu"
    MEMORY = "memory"
    INSTANCES = "instances"
    CONTAINERS = "containers"
    STORAGE = "storage"
    NETWORK_BANDWIDTH = "network_bandwidth"


@dataclass
class ScalingMetric:
    """Scaling metric data point"""
    metric_name: str
    value: float
    timestamp: datetime
    service_id: str
    resource_type: ResourceType
    creator_tier: Optional[CreatorTier] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingRule:
    """Auto-scaling rule configuration"""
    rule_id: str
    name: str
    service_id: str
    trigger: ScalingTrigger
    direction: ScalingDirection
    threshold: float
    scaling_policy: ScalingPolicy
    min_instances: int
    max_instances: int
    cooldown_period: timedelta
    creator_impact_weight: float = 1.0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingDecision:
    """Auto-scaling decision"""
    decision_id: str
    service_id: str
    direction: ScalingDirection
    current_instances: int
    target_instances: int
    trigger_metric: str
    trigger_value: float
    confidence_score: float
    creator_impact_estimate: float
    cost_impact: float
    decision_time: datetime
    execution_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionModel:
    """Predictive scaling model"""
    model_id: str
    service_id: str
    model_type: str
    features: List[str]
    accuracy: float
    trained_at: datetime
    prediction_horizon: timedelta
    model_object: Any = None


@dataclass
class CreatorActivityPattern:
    """Creator activity pattern for scaling"""
    pattern_id: str
    creator_tier: CreatorTier
    activity_type: str  # video_upload, live_stream, batch_processing
    peak_hours: List[int]
    scaling_multiplier: float
    resource_requirements: Dict[ResourceType, float]


class AutoScalingIntelligence:
    """
    Enterprise auto-scaling intelligence for Creator Economy predictive scaling.
    
    Provides intelligent auto-scaling decisions based on predictive models,
    creator activity patterns, and cost optimization.
    """
    
    def __init__(self):
        """Initialize auto-scaling intelligence"""
        self.logger = logging.getLogger(__name__)
        self.scaling_rules = {}
        self.metrics_history = defaultdict(deque)
        self.scaling_decisions = []
        self.prediction_models = {}
        self.creator_patterns = {}
        self.active_cooldowns = {}
        
        # Default scaling thresholds
        self.default_thresholds = {
            ScalingTrigger.CPU_UTILIZATION: {'scale_up': 75.0, 'scale_down': 25.0},
            ScalingTrigger.MEMORY_UTILIZATION: {'scale_up': 80.0, 'scale_down': 30.0},
            ScalingTrigger.REQUEST_RATE: {'scale_up': 1000.0, 'scale_down': 100.0},
            ScalingTrigger.RESPONSE_TIME: {'scale_up': 2000.0, 'scale_down': 500.0},
            ScalingTrigger.QUEUE_LENGTH: {'scale_up': 50.0, 'scale_down': 5.0}
        }
        
        # Initialize creator activity patterns
        self._setup_creator_patterns()
        
        self.logger.info("AutoScalingIntelligence initialized")
    
    def _setup_creator_patterns(self):
        """Setup default creator activity patterns"""
        patterns = [
            CreatorActivityPattern(
                pattern_id="video_creator_peak",
                creator_tier=CreatorTier.PROFESSIONAL,
                activity_type="video_processing",
                peak_hours=[18, 19, 20, 21, 22],
                scaling_multiplier=2.5,
                resource_requirements={
                    ResourceType.CPU: 3.0,
                    ResourceType.MEMORY: 2.0,
                    ResourceType.STORAGE: 4.0
                }
            ),
            CreatorActivityPattern(
                pattern_id="live_streaming_burst",
                creator_tier=CreatorTier.ENTERPRISE,
                activity_type="live_streaming",
                peak_hours=[19, 20, 21],
                scaling_multiplier=4.0,
                resource_requirements={
                    ResourceType.CPU: 5.0,
                    ResourceType.MEMORY: 3.0,
                    ResourceType.NETWORK_BANDWIDTH: 6.0
                }
            ),
            CreatorActivityPattern(
                pattern_id="batch_processing_night",
                creator_tier=CreatorTier.PREMIUM,
                activity_type="batch_processing",
                peak_hours=[2, 3, 4, 5],
                scaling_multiplier=3.0,
                resource_requirements={
                    ResourceType.CPU: 4.0,
                    ResourceType.MEMORY: 4.0,
                    ResourceType.INSTANCES: 2.0
                }
            )
        ]
        
        for pattern in patterns:
            self.creator_patterns[pattern.pattern_id] = pattern
    
    async def collect_scaling_metrics(
        self,
        service_id: str,
        metrics: List[ScalingMetric]
    ) -> bool:
        """
        Collect scaling metrics for analysis
        
        Args:
            service_id: Service identifier
            metrics: List of scaling metrics
            
        Returns:
            True if metrics collected successfully
        """
        try:
            for metric in metrics:
                key = f"{service_id}_{metric.metric_name}"
                self.metrics_history[key].append(metric)
                
                # Keep only last 1000 metrics per key
                if len(self.metrics_history[key]) > 1000:
                    self.metrics_history[key].popleft()
            
            # Evaluate scaling decisions
            await self._evaluate_scaling_decisions(service_id, metrics)
            
            self.logger.debug(f"Collected {len(metrics)} scaling metrics for {service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error collecting scaling metrics: {str(e)}")
            raise
    
    async def create_scaling_rule(
        self,
        rule: ScalingRule
    ) -> bool:
        """
        Create an auto-scaling rule
        
        Args:
            rule: Scaling rule configuration
            
        Returns:
            True if rule created successfully
        """
        try:
            # Validate rule
            if rule.min_instances >= rule.max_instances:
                raise ValueError("min_instances must be less than max_instances")
            
            if rule.min_instances < 1:
                raise ValueError("min_instances must be at least 1")
            
            # Store rule
            self.scaling_rules[rule.rule_id] = rule
            
            self.logger.info(f"Created scaling rule: {rule.rule_id} for service {rule.service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating scaling rule: {str(e)}")
            raise
    
    async def _evaluate_scaling_decisions(
        self,
        service_id: str,
        metrics: List[ScalingMetric]
    ):
        """Evaluate if scaling decisions should be made"""
        # Get applicable scaling rules
        service_rules = [
            rule for rule in self.scaling_rules.values()
            if rule.service_id == service_id and rule.enabled
        ]
        
        for rule in service_rules:
            # Check cooldown period
            if self._is_in_cooldown(rule.rule_id):
                continue
            
            # Evaluate rule condition
            decision = await self._evaluate_scaling_rule(rule, metrics)
            
            if decision:
                # Execute scaling decision
                await self._execute_scaling_decision(decision)
    
    def _is_in_cooldown(self, rule_id: str) -> bool:
        """Check if rule is in cooldown period"""
        if rule_id not in self.active_cooldowns:
            return False
        
        cooldown_end = self.active_cooldowns[rule_id]
        return datetime.now() < cooldown_end
    
    async def _evaluate_scaling_rule(
        self,
        rule: ScalingRule,
        metrics: List[ScalingMetric]
    ) -> Optional[ScalingDecision]:
        """Evaluate a scaling rule against current metrics"""
        try:
            # Find relevant metrics for this rule
            relevant_metrics = [
                m for m in metrics
                if self._is_metric_relevant_to_trigger(m, rule.trigger)
            ]
            
            if not relevant_metrics:
                return None
            
            # Get current metric value
            current_value = statistics.mean([m.value for m in relevant_metrics])
            
            # Determine if scaling is needed
            scaling_needed = self._should_scale(rule, current_value)
            
            if not scaling_needed:
                return None
            
            # Get current instance count (simulated)
            current_instances = await self._get_current_instance_count(rule.service_id)
            
            # Calculate target instances
            target_instances = await self._calculate_target_instances(
                rule, current_instances, current_value, relevant_metrics
            )
            
            # Ensure within bounds
            target_instances = max(rule.min_instances, min(rule.max_instances, target_instances))
            
            if target_instances == current_instances:
                return None
            
            # Determine scaling direction
            if target_instances > current_instances:
                direction = ScalingDirection.SCALE_OUT
            else:
                direction = ScalingDirection.SCALE_IN
            
            # Calculate confidence and impact
            confidence_score = await self._calculate_confidence_score(rule, current_value, relevant_metrics)
            creator_impact = await self._estimate_creator_impact(rule, direction, target_instances - current_instances)
            cost_impact = await self._estimate_cost_impact(rule, target_instances - current_instances)
            
            # Create scaling decision
            decision = ScalingDecision(
                decision_id=f"scale_{int(time.time())}_{rule.rule_id}",
                service_id=rule.service_id,
                direction=direction,
                current_instances=current_instances,
                target_instances=target_instances,
                trigger_metric=rule.trigger.value,
                trigger_value=current_value,
                confidence_score=confidence_score,
                creator_impact_estimate=creator_impact,
                cost_impact=cost_impact,
                decision_time=datetime.now(),
                metadata={
                    'rule_id': rule.rule_id,
                    'threshold': rule.threshold,
                    'policy': rule.scaling_policy.value
                }
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error evaluating scaling rule {rule.rule_id}: {str(e)}")
            return None
    
    def _is_metric_relevant_to_trigger(
        self,
        metric: ScalingMetric,
        trigger: ScalingTrigger
    ) -> bool:
        """Check if metric is relevant to scaling trigger"""
        trigger_mapping = {
            ScalingTrigger.CPU_UTILIZATION: ['cpu_usage', 'cpu_utilization'],
            ScalingTrigger.MEMORY_UTILIZATION: ['memory_usage', 'memory_utilization'],
            ScalingTrigger.REQUEST_RATE: ['requests_per_second', 'request_rate'],
            ScalingTrigger.RESPONSE_TIME: ['response_time', 'latency'],
            ScalingTrigger.QUEUE_LENGTH: ['queue_length', 'queue_size'],
            ScalingTrigger.CREATOR_ACTIVITY: ['creator_activity', 'active_creators']
        }
        
        relevant_names = trigger_mapping.get(trigger, [])
        return any(name in metric.metric_name.lower() for name in relevant_names)
    
    def _should_scale(self, rule: ScalingRule, current_value: float) -> bool:
        """Determine if scaling should occur based on rule and current value"""
        if rule.direction == ScalingDirection.SCALE_OUT:
            return current_value > rule.threshold
        elif rule.direction == ScalingDirection.SCALE_IN:
            return current_value < rule.threshold
        else:
            # For bidirectional rules, use default thresholds
            thresholds = self.default_thresholds.get(rule.trigger, {'scale_up': 75.0, 'scale_down': 25.0})
            return current_value > thresholds['scale_up'] or current_value < thresholds['scale_down']
    
    async def _get_current_instance_count(self, service_id: str) -> int:
        """Get current instance count for service (simulated)"""
        # In real implementation, would query container orchestrator
        return np.random.randint(2, 10)  # Simulate current instances
    
    async def _calculate_target_instances(
        self,
        rule: ScalingRule,
        current_instances: int,
        current_value: float,
        metrics: List[ScalingMetric]
    ) -> int:
        """Calculate target number of instances"""
        if rule.scaling_policy == ScalingPolicy.PREDICTIVE:
            return await self._calculate_predictive_target(rule, current_instances, metrics)
        elif rule.scaling_policy == ScalingPolicy.CREATOR_AWARE:
            return await self._calculate_creator_aware_target(rule, current_instances, current_value)
        else:
            return await self._calculate_reactive_target(rule, current_instances, current_value)
    
    async def _calculate_reactive_target(
        self,
        rule: ScalingRule,
        current_instances: int,
        current_value: float
    ) -> int:
        """Calculate target instances using reactive scaling"""
        # Simple threshold-based scaling
        if rule.direction == ScalingDirection.SCALE_OUT or current_value > rule.threshold:
            # Scale up by 1-3 instances based on urgency
            urgency = min(3, max(1, int((current_value / rule.threshold) - 1) + 1))
            return current_instances + urgency
        else:
            # Scale down by 1 instance
            return max(rule.min_instances, current_instances - 1)
    
    async def _calculate_predictive_target(
        self,
        rule: ScalingRule,
        current_instances: int,
        metrics: List[ScalingMetric]
    ) -> int:
        """Calculate target instances using predictive scaling"""
        try:
            # Get prediction model for this service
            model = self.prediction_models.get(rule.service_id)
            
            if not model:
                # Fall back to reactive scaling
                return await self._calculate_reactive_target(rule, current_instances, metrics[0].value if metrics else 0)
            
            # Prepare features for prediction
            features = await self._prepare_prediction_features(rule.service_id, metrics)
            
            if not features:
                return current_instances
            
            # Make prediction
            predicted_load = model.model_object.predict([features])[0]
            
            # Calculate required instances based on predicted load
            load_per_instance = 100.0  # Assume each instance can handle 100 units
            required_instances = math.ceil(predicted_load / load_per_instance)
            
            # Add buffer for safety
            buffer_factor = 1.2
            target_instances = int(required_instances * buffer_factor)
            
            return max(rule.min_instances, min(rule.max_instances, target_instances))
            
        except Exception as e:
            self.logger.error(f"Error in predictive scaling: {str(e)}")
            # Fall back to reactive scaling
            return await self._calculate_reactive_target(rule, current_instances, metrics[0].value if metrics else 0)
    
    async def _calculate_creator_aware_target(
        self,
        rule: ScalingRule,
        current_instances: int,
        current_value: float
    ) -> int:
        """Calculate target instances considering creator activity patterns"""
        current_hour = datetime.now().hour
        base_target = await self._calculate_reactive_target(rule, current_instances, current_value)
        
        # Check for matching creator patterns
        scaling_multiplier = 1.0
        
        for pattern in self.creator_patterns.values():
            if current_hour in pattern.peak_hours:
                scaling_multiplier = max(scaling_multiplier, pattern.scaling_multiplier)
        
        # Apply creator-aware scaling
        creator_aware_target = int(base_target * scaling_multiplier)
        
        return max(rule.min_instances, min(rule.max_instances, creator_aware_target))
    
    async def _prepare_prediction_features(
        self,
        service_id: str,
        metrics: List[ScalingMetric]
    ) -> Optional[List[float]]:
        """Prepare features for predictive model"""
        try:
            features = []
            
            # Time-based features
            now = datetime.now()
            features.extend([
                now.hour,
                now.weekday(),
                now.month,
                1 if 18 <= now.hour <= 22 else 0,  # Peak hours
                1 if now.weekday() >= 5 else 0      # Weekend
            ])
            
            # Metric-based features
            if metrics:
                cpu_metrics = [m.value for m in metrics if 'cpu' in m.metric_name.lower()]
                memory_metrics = [m.value for m in metrics if 'memory' in m.metric_name.lower()]
                request_metrics = [m.value for m in metrics if 'request' in m.metric_name.lower()]
                
                features.extend([
                    statistics.mean(cpu_metrics) if cpu_metrics else 0,
                    statistics.mean(memory_metrics) if memory_metrics else 0,
                    statistics.mean(request_metrics) if request_metrics else 0
                ])
            else:
                features.extend([0, 0, 0])
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error preparing prediction features: {str(e)}")
            return None
    
    async def _calculate_confidence_score(
        self,
        rule: ScalingRule,
        current_value: float,
        metrics: List[ScalingMetric]
    ) -> float:
        """Calculate confidence score for scaling decision"""
        # Base confidence on how far the metric is from threshold
        threshold_distance = abs(current_value - rule.threshold) / rule.threshold
        base_confidence = min(1.0, threshold_distance)
        
        # Adjust based on metric stability
        if len(metrics) > 1:
            values = [m.value for m in metrics]
            stability = 1.0 - (statistics.stdev(values) / statistics.mean(values)) if statistics.mean(values) > 0 else 0
            base_confidence *= max(0.5, stability)
        
        # Adjust based on scaling policy
        if rule.scaling_policy == ScalingPolicy.PREDICTIVE:
            model = self.prediction_models.get(rule.service_id)
            if model:
                base_confidence *= model.accuracy
        
        return max(0.1, min(1.0, base_confidence))
    
    async def _estimate_creator_impact(
        self,
        rule: ScalingRule,
        direction: ScalingDirection,
        instance_change: int
    ) -> float:
        """Estimate creator impact of scaling decision"""
        # Base impact on scaling direction
        if direction == ScalingDirection.SCALE_OUT:
            # Scaling out generally improves creator experience
            base_impact = -abs(instance_change) * 2.0  # Negative = positive impact
        else:
            # Scaling in might degrade creator experience
            base_impact = abs(instance_change) * 3.0   # Positive = negative impact
        
        # Apply creator impact weight from rule
        weighted_impact = base_impact * rule.creator_impact_weight
        
        # Consider current time and creator patterns
        current_hour = datetime.now().hour
        is_peak_time = any(
            current_hour in pattern.peak_hours
            for pattern in self.creator_patterns.values()
        )
        
        if is_peak_time:
            weighted_impact *= 1.5  # Higher impact during peak times
        
        return max(-100, min(100, weighted_impact))
    
    async def _estimate_cost_impact(
        self,
        rule: ScalingRule,
        instance_change: int
    ) -> float:
        """Estimate cost impact of scaling decision"""
        # Cost per instance per hour (simplified)
        cost_per_instance_hour = 0.10  # $0.10 per instance per hour
        
        # Calculate hourly cost change
        hourly_cost_change = instance_change * cost_per_instance_hour
        
        # Estimate daily cost impact
        daily_cost_impact = hourly_cost_change * 24
        
        return daily_cost_impact
    
    async def _execute_scaling_decision(self, decision: ScalingDecision):
        """Execute a scaling decision"""
        try:
            self.logger.info(f"Executing scaling decision {decision.decision_id}: "
                           f"{decision.current_instances} -> {decision.target_instances} instances")
            
            # Simulate scaling execution
            await asyncio.sleep(2)  # Simulate scaling time
            
            # Update decision with execution time
            decision.execution_time = datetime.now()
            
            # Store decision in history
            self.scaling_decisions.append(decision)
            
            # Set cooldown period
            rule = next(
                (r for r in self.scaling_rules.values() if r.rule_id == decision.metadata.get('rule_id')),
                None
            )
            
            if rule:
                cooldown_end = datetime.now() + rule.cooldown_period
                self.active_cooldowns[rule.rule_id] = cooldown_end
            
            self.logger.info(f"Scaling decision {decision.decision_id} executed successfully")
            
        except Exception as e:
            self.logger.error(f"Error executing scaling decision {decision.decision_id}: {str(e)}")
            raise
    
    async def train_predictive_model(
        self,
        service_id: str,
        training_data: List[Dict[str, Any]],
        model_type: str = "random_forest"
    ) -> PredictionModel:
        """
        Train a predictive scaling model
        
        Args:
            service_id: Service to train model for
            training_data: Historical data for training
            model_type: Type of model to train
            
        Returns:
            Trained prediction model
        """
        try:
            # Prepare training data
            df = pd.DataFrame(training_data)
            
            # Feature engineering
            features = ['hour', 'day_of_week', 'month', 'is_peak', 'is_weekend',
                       'cpu_usage', 'memory_usage', 'request_rate']
            
            X = df[features]
            y = df['load']  # Target variable
            
            # Train model
            if model_type == "random_forest":
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                model = LinearRegression()
                scaler = StandardScaler()
                X = scaler.fit_transform(X)
            
            model.fit(X, y)
            
            # Calculate accuracy
            accuracy = model.score(X, y)
            
            # Create prediction model
            prediction_model = PredictionModel(
                model_id=f"model_{service_id}_{int(time.time())}",
                service_id=service_id,
                model_type=model_type,
                features=features,
                accuracy=accuracy,
                trained_at=datetime.now(),
                prediction_horizon=timedelta(minutes=30),
                model_object=model
            )
            
            # Store model
            self.prediction_models[service_id] = prediction_model
            
            self.logger.info(f"Trained predictive model for {service_id} with accuracy: {accuracy:.3f}")
            return prediction_model
            
        except Exception as e:
            self.logger.error(f"Error training predictive model: {str(e)}")
            raise
    
    async def get_scaling_recommendations(
        self,
        service_id: str,
        time_horizon: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get scaling recommendations for a service
        
        Args:
            service_id: Service to analyze
            time_horizon: Time horizon for recommendations
            
        Returns:
            List of scaling recommendations
        """
        try:
            recommendations = []
            
            # Get recent metrics
            recent_metrics = await self._get_recent_metrics(service_id, timedelta(minutes=30))
            
            if not recent_metrics:
                return recommendations
            
            # Analyze current performance
            current_analysis = await self._analyze_current_performance(service_id, recent_metrics)
            
            # Generate recommendations based on analysis
            if current_analysis['avg_cpu'] > 80:
                recommendations.append({
                    'type': 'scale_out',
                    'reason': f"High CPU utilization ({current_analysis['avg_cpu']:.1f}%)",
                    'urgency': 'high',
                    'recommended_instances': current_analysis['current_instances'] + 2,
                    'expected_improvement': '25-35% CPU reduction'
                })
            
            if current_analysis['avg_memory'] > 85:
                recommendations.append({
                    'type': 'scale_out',
                    'reason': f"High memory utilization ({current_analysis['avg_memory']:.1f}%)",
                    'urgency': 'critical',
                    'recommended_instances': current_analysis['current_instances'] + 1,
                    'expected_improvement': '20-30% memory reduction'
                })
            
            if current_analysis['avg_response_time'] > 2000:
                recommendations.append({
                    'type': 'scale_out',
                    'reason': f"High response time ({current_analysis['avg_response_time']:.0f}ms)",
                    'urgency': 'high',
                    'recommended_instances': current_analysis['current_instances'] + 3,
                    'expected_improvement': '40-50% response time improvement'
                })
            
            # Check for over-provisioning
            if (current_analysis['avg_cpu'] < 30 and 
                current_analysis['avg_memory'] < 40 and 
                current_analysis['current_instances'] > 2):
                recommendations.append({
                    'type': 'scale_in',
                    'reason': 'Low resource utilization - cost optimization opportunity',
                    'urgency': 'low',
                    'recommended_instances': max(2, current_analysis['current_instances'] - 1),
                    'expected_savings': f"${(current_analysis['current_instances'] - 2) * 2.4:.2f}/day"
                })
            
            # Predictive recommendations
            if service_id in self.prediction_models:
                predictive_rec = await self._generate_predictive_recommendations(service_id, time_horizon)
                recommendations.extend(predictive_rec)
            
            self.logger.info(f"Generated {len(recommendations)} scaling recommendations for {service_id}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting scaling recommendations: {str(e)}")
            raise
    
    async def _get_recent_metrics(
        self,
        service_id: str,
        time_window: timedelta
    ) -> List[ScalingMetric]:
        """Get recent metrics for a service"""
        cutoff_time = datetime.now() - time_window
        recent_metrics = []
        
        for key, metrics in self.metrics_history.items():
            if service_id in key:
                for metric in metrics:
                    if metric.timestamp >= cutoff_time:
                        recent_metrics.append(metric)
        
        return recent_metrics
    
    async def _analyze_current_performance(
        self,
        service_id: str,
        metrics: List[ScalingMetric]
    ) -> Dict[str, Any]:
        """Analyze current performance metrics"""
        analysis = {
            'service_id': service_id,
            'current_instances': await self._get_current_instance_count(service_id),
            'metric_count': len(metrics)
        }
        
        # Analyze by metric type
        cpu_values = [m.value for m in metrics if 'cpu' in m.metric_name.lower()]
        memory_values = [m.value for m in metrics if 'memory' in m.metric_name.lower()]
        response_values = [m.value for m in metrics if 'response' in m.metric_name.lower()]
        request_values = [m.value for m in metrics if 'request' in m.metric_name.lower()]
        
        analysis.update({
            'avg_cpu': statistics.mean(cpu_values) if cpu_values else 0,
            'max_cpu': max(cpu_values) if cpu_values else 0,
            'avg_memory': statistics.mean(memory_values) if memory_values else 0,
            'max_memory': max(memory_values) if memory_values else 0,
            'avg_response_time': statistics.mean(response_values) if response_values else 0,
            'p95_response_time': np.percentile(response_values, 95) if len(response_values) > 1 else (response_values[0] if response_values else 0),
            'avg_request_rate': statistics.mean(request_values) if request_values else 0
        })
        
        return analysis
    
    async def _generate_predictive_recommendations(
        self,
        service_id: str,
        time_horizon: timedelta
    ) -> List[Dict[str, Any]]:
        """Generate predictive scaling recommendations"""
        recommendations = []
        
        try:
            model = self.prediction_models[service_id]
            
            # Generate predictions for time horizon
            predictions = []
            current_time = datetime.now()
            
            while current_time < datetime.now() + time_horizon:
                features = [
                    current_time.hour,
                    current_time.weekday(),
                    current_time.month,
                    1 if 18 <= current_time.hour <= 22 else 0,
                    1 if current_time.weekday() >= 5 else 0,
                    50, 60, 100  # Example current metrics
                ]
                
                predicted_load = model.model_object.predict([features])[0]
                predictions.append(predicted_load)
                
                current_time += timedelta(minutes=15)
            
            # Analyze predictions
            max_predicted_load = max(predictions)
            avg_predicted_load = statistics.mean(predictions)
            
            current_instances = await self._get_current_instance_count(service_id)
            current_capacity = current_instances * 100  # Assume 100 units per instance
            
            if max_predicted_load > current_capacity * 0.8:
                recommendations.append({
                    'type': 'predictive_scale_out',
                    'reason': f"Predicted load spike ({max_predicted_load:.0f} units) exceeds 80% capacity",
                    'urgency': 'medium',
                    'recommended_instances': math.ceil(max_predicted_load / 80),  # 80% target utilization
                    'when': 'within next hour',
                    'confidence': model.accuracy
                })
            
        except Exception as e:
            self.logger.error(f"Error generating predictive recommendations: {str(e)}")
        
        return recommendations
    
    def get_scaling_history(
        self,
        service_id: Optional[str] = None,
        time_range: timedelta = timedelta(days=1)
    ) -> List[Dict[str, Any]]:
        """Get scaling decision history"""
        cutoff_time = datetime.now() - time_range
        
        history = [
            {
                'decision_id': decision.decision_id,
                'service_id': decision.service_id,
                'direction': decision.direction.value,
                'current_instances': decision.current_instances,
                'target_instances': decision.target_instances,
                'trigger_metric': decision.trigger_metric,
                'trigger_value': decision.trigger_value,
                'confidence_score': decision.confidence_score,
                'creator_impact_estimate': decision.creator_impact_estimate,
                'cost_impact': decision.cost_impact,
                'decision_time': decision.decision_time.isoformat(),
                'execution_time': decision.execution_time.isoformat() if decision.execution_time else None
            }
            for decision in self.scaling_decisions
            if decision.decision_time >= cutoff_time and (service_id is None or decision.service_id == service_id)
        ]
        
        return history
    
    def get_intelligence_status(self) -> Dict[str, Any]:
        """Get auto-scaling intelligence status"""
        return {
            'intelligence_name': 'AutoScalingIntelligence',
            'version': '1.0.0',
            'status': 'active',
            'scaling_rules': len(self.scaling_rules),
            'prediction_models': len(self.prediction_models),
            'creator_patterns': len(self.creator_patterns),
            'scaling_decisions_total': len(self.scaling_decisions),
            'active_cooldowns': len(self.active_cooldowns),
            'supported_triggers': [trigger.value for trigger in ScalingTrigger],
            'supported_policies': [policy.value for policy in ScalingPolicy]
        }


# Export main classes and enums
__all__ = [
    'AutoScalingIntelligence',
    'ScalingDirection',
    'ScalingTrigger',
    'CreatorTier',
    'ScalingPolicy',
    'ResourceType',
    'ScalingMetric',
    'ScalingRule',
    'ScalingDecision',
    'PredictionModel',
    'CreatorActivityPattern'
]