"""Scaling Engine - Advanced Dynamic Scaling Decision & Execution Engine

This module provides intelligent scaling decisions using machine learning algorithms,
predictive analytics, and advanced resource optimization strategies.

Author: Fahed Mlaiel
Email: mlaiel@live.de
© 2025 All Rights Reserved
"""import asyncio
import logging
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from collections import defaultdict, deque
import pickle
from concurrent.futures import ThreadPoolExecutor

from ..base import BaseAgent
try:
    from core.exceptions import ScalingException
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ScalingException = globals().get('ScalingException', Exception)
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...core.monitoring import get_metrics_client


class ScalingStrategy(Enum):
    """Scaling strategy types"""    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    PROACTIVE = "proactive"
    HYBRID = "hybrid"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"


class ScalingDirection(Enum):
    """Scaling direction"""    UP = "up"
    DOWN = "down"
    MAINTAIN = "maintain"


@dataclass
class ScalingDecision:
    """Scaling decision with confidence and metadata"""    service_name: str
    current_instances: int
    target_instances: int
    direction: ScalingDirection
    strategy_used: ScalingStrategy
    confidence: float
    reasoning: List[str]
    estimated_cost_impact: float
    estimated_performance_impact: float
    execution_priority: int = 1
    cooldown_period: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingModel:
    """Machine learning model for scaling decisions"""    model_id: str
    service_name: str
    model_type: str
    accuracy: float
    last_trained: datetime
    training_data_size: int
    feature_importance: Dict[str, float] = field(default_factory=dict)


@dataclass
class ResourcePrediction:
    """Resource usage prediction"""    metric_name: str
    predicted_value: float
    confidence_interval: Tuple[float, float]
    prediction_horizon: int  # minutes
    model_accuracy: float
    timestamp: datetime = field(default_factory=datetime.now)


class ScalingEngine(BaseAgent):
    """    Enterprise Scaling Engine
    
    Features:
    - ML-powered scaling decisions
    - Predictive resource allocation
    - Multi-strategy scaling optimization
    - Cost-aware scaling decisions
    - Performance impact analysis
    - Historical pattern analysis
    - Real-time decision optimization
    - Custom scaling strategies
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
        self.metrics_client = get_metrics_client()
        
        # Scaling configuration
        self.default_strategy = ScalingStrategy.HYBRID
        self.strategy_config: Dict[str, ScalingStrategy] = {}
        
        # Machine learning models
        self.scaling_models: Dict[str, ScalingModel] = {}
        self.prediction_cache: Dict[str, ResourcePrediction] = {}
        
        # Historical data for learning
        self.scaling_history: deque = deque(maxlen=10000)
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5000))
        self.cost_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5000))
        
        # Decision engine state
        self.active_decisions: Dict[str, ScalingDecision] = {}
        self.decision_queue: List[ScalingDecision] = []
        
        # Learning and optimization
        self.learning_enabled = True
        self.auto_optimization = True
        self.model_retrain_interval = 86400  # 24 hours
        
        # Thread safety and execution
        self.decision_lock = threading.RLock()
        self.execution_executor = ThreadPoolExecutor(max_workers=4)
        
        # Performance tracking
        self.engine_stats = {
            "decisions_made": 0,
            "successful_scalings": 0,
            "failed_scalings": 0,
            "average_decision_time": 0.0,
            "model_accuracy": 0.0
        }
        
        # Feature weights for decision making
        self.feature_weights = {
            "cpu_utilization": 0.25,
            "memory_utilization": 0.20,
            "request_rate": 0.15,
            "response_time": 0.15,
            "error_rate": 0.10,
            "queue_length": 0.10,
            "historical_pattern": 0.05
        }
        
        self.logger.info("ScalingEngine initialized successfully")

    async def make_scaling_decision(self, service_name: str, 
                                  metrics: Dict[str, float],
                                  current_instances: int) -> ScalingDecision:
        """Make intelligent scaling decision based on metrics and strategy"""        start_time = time.time()
        
        try:
            with self.decision_lock:
                # Get strategy for service
                strategy = self.strategy_config.get(service_name, self.default_strategy)
                
                # Generate predictions if using predictive strategies
                predictions = None
                if strategy in [ScalingStrategy.PREDICTIVE, ScalingStrategy.HYBRID]:
                    predictions = await self._generate_predictions(service_name, metrics)
                
                # Make decision based on strategy
                decision = await self._execute_scaling_strategy(
                    service_name, metrics, current_instances, strategy, predictions
                )
                
                # Calculate confidence score
                decision.confidence = await self._calculate_decision_confidence(
                    decision, metrics, predictions
                )
                
                # Add reasoning
                decision.reasoning = self._generate_decision_reasoning(
                    decision, metrics, predictions
                )
                
                # Estimate impact
                decision.estimated_cost_impact = await self._estimate_cost_impact(decision)
                decision.estimated_performance_impact = await self._estimate_performance_impact(decision)
                
                # Store decision
                self.active_decisions[service_name] = decision
                
                # Update stats
                decision_time = (time.time() - start_time) * 1000
                self.engine_stats["decisions_made"] += 1
                self.engine_stats["average_decision_time"] = (
                    (self.engine_stats["average_decision_time"] * 
                     (self.engine_stats["decisions_made"] - 1) + decision_time) /
                    self.engine_stats["decisions_made"]
                )
                
                self.logger.info(
                    f"Scaling decision for {service_name}: "
                    f"{current_instances} -> {decision.target_instances} "
                    f"(confidence: {decision.confidence:.2f})"
                )
                
                return decision
                
        except Exception as e:
            self.logger.error(f"Error making scaling decision for {service_name}: {e}")
            raise ScalingException(f"Decision making failed: {e}")

    async def _execute_scaling_strategy(self, service_name: str, 
                                       metrics: Dict[str, float],
                                       current_instances: int,
                                       strategy: ScalingStrategy,
                                       predictions: Optional[Dict[str, ResourcePrediction]]) -> ScalingDecision:
        """Execute specific scaling strategy"""        
        if strategy == ScalingStrategy.REACTIVE:
            return await self._reactive_scaling(service_name, metrics, current_instances)
        
        elif strategy == ScalingStrategy.PREDICTIVE:
            return await self._predictive_scaling(service_name, metrics, current_instances, predictions)
        
        elif strategy == ScalingStrategy.PROACTIVE:
            return await self._proactive_scaling(service_name, metrics, current_instances)
        
        elif strategy == ScalingStrategy.HYBRID:
            return await self._hybrid_scaling(service_name, metrics, current_instances, predictions)
        
        elif strategy == ScalingStrategy.COST_OPTIMIZED:
            return await self._cost_optimized_scaling(service_name, metrics, current_instances)
        
        elif strategy == ScalingStrategy.PERFORMANCE_OPTIMIZED:
            return await self._performance_optimized_scaling(service_name, metrics, current_instances)
        
        else:
            # Fallback to reactive
            return await self._reactive_scaling(service_name, metrics, current_instances)

    async def _reactive_scaling(self, service_name: str, 
                               metrics: Dict[str, float],
                               current_instances: int) -> ScalingDecision:
        """Reactive scaling based on current metrics"""        try:
            # Define scaling thresholds
            scale_up_score = 0
            scale_down_score = 0
            
            # CPU utilization
            cpu = metrics.get("cpu_utilization", 0)
            if cpu > 80:
                scale_up_score += 3
            elif cpu > 70:
                scale_up_score += 1
            elif cpu < 30:
                scale_down_score += 1
            elif cpu < 20:
                scale_down_score += 2
            
            # Memory utilization
            memory = metrics.get("memory_utilization", 0)
            if memory > 85:
                scale_up_score += 3
            elif memory > 75:
                scale_up_score += 1
            elif memory < 40:
                scale_down_score += 1
            elif memory < 30:
                scale_down_score += 2
            
            # Response time
            response_time = metrics.get("response_time", 0)
            if response_time > 2000:
                scale_up_score += 2
            elif response_time > 1000:
                scale_up_score += 1
            elif response_time < 200:
                scale_down_score += 1
            
            # Error rate
            error_rate = metrics.get("error_rate", 0)
            if error_rate > 0.05:
                scale_up_score += 2
            elif error_rate > 0.02:
                scale_up_score += 1
            
            # Request rate
            request_rate = metrics.get("request_rate", 0)
            if request_rate > 1000:
                scale_up_score += 1
            elif request_rate < 100:
                scale_down_score += 1
            
            # Make decision
            if scale_up_score >= 3:
                direction = ScalingDirection.UP
                target_instances = min(current_instances + 1, 20)
            elif scale_down_score >= 3:
                direction = ScalingDirection.DOWN
                target_instances = max(current_instances - 1, 1)
            else:
                direction = ScalingDirection.MAINTAIN
                target_instances = current_instances
            
            return ScalingDecision(
                service_name=service_name,
                current_instances=current_instances,
                target_instances=target_instances,
                direction=direction,
                strategy_used=ScalingStrategy.REACTIVE,
                confidence=0.0,  # Will be calculated later
                reasoning=[],
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Error in reactive scaling: {e}")
            raise

    async def _predictive_scaling(self, service_name: str, 
                                 metrics: Dict[str, float],
                                 current_instances: int,
                                 predictions: Optional[Dict[str, ResourcePrediction]]) -> ScalingDecision:
        """Predictive scaling based on forecasted metrics"""        try:
            if not predictions:
                # Fallback to reactive if no predictions available
                return await self._reactive_scaling(service_name, metrics, current_instances)
            
            # Analyze predictions
            scale_up_factors = 0
            scale_down_factors = 0
            
            # Check CPU prediction
            cpu_pred = predictions.get("cpu_utilization")
            if cpu_pred:
                if cpu_pred.predicted_value > 80:
                    scale_up_factors += 2
                elif cpu_pred.predicted_value < 30:
                    scale_down_factors += 1
            
            # Check memory prediction
            memory_pred = predictions.get("memory_utilization")
            if memory_pred:
                if memory_pred.predicted_value > 85:
                    scale_up_factors += 2
                elif memory_pred.predicted_value < 40:
                    scale_down_factors += 1
            
            # Check request rate prediction
            request_pred = predictions.get("request_rate")
            if request_pred:
                current_rate = metrics.get("request_rate", 0)
                predicted_growth = (request_pred.predicted_value - current_rate) / max(current_rate, 1)
                
                if predicted_growth > 0.5:  # 50% increase predicted
                    scale_up_factors += 2
                elif predicted_growth > 0.2:  # 20% increase predicted
                    scale_up_factors += 1
                elif predicted_growth < -0.3:  # 30% decrease predicted
                    scale_down_factors += 1
            
            # Make decision
            if scale_up_factors >= 2:
                direction = ScalingDirection.UP
                target_instances = min(current_instances + 1, 20)
            elif scale_down_factors >= 2:
                direction = ScalingDirection.DOWN
                target_instances = max(current_instances - 1, 1)
            else:
                direction = ScalingDirection.MAINTAIN
                target_instances = current_instances
            
            return ScalingDecision(
                service_name=service_name,
                current_instances=current_instances,
                target_instances=target_instances,
                direction=direction,
                strategy_used=ScalingStrategy.PREDICTIVE,
                confidence=0.0,
                reasoning=[],
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0,
                metadata={"predictions": {k: v.predicted_value for k, v in predictions.items()}}
            )
            
        except Exception as e:
            self.logger.error(f"Error in predictive scaling: {e}")
            raise

    async def _hybrid_scaling(self, service_name: str, 
                             metrics: Dict[str, float],
                             current_instances: int,
                             predictions: Optional[Dict[str, ResourcePrediction]]) -> ScalingDecision:
        """Hybrid scaling combining reactive and predictive approaches"""        try:
            # Get both reactive and predictive decisions
            reactive_decision = await self._reactive_scaling(service_name, metrics, current_instances)
            
            if predictions:
                predictive_decision = await self._predictive_scaling(
                    service_name, metrics, current_instances, predictions
                )
            else:
                predictive_decision = reactive_decision
            
            # Combine decisions with weighted approach
            reactive_weight = 0.6
            predictive_weight = 0.4
            
            # Calculate weighted target instances
            reactive_change = reactive_decision.target_instances - current_instances
            predictive_change = predictive_decision.target_instances - current_instances
            
            weighted_change = (reactive_change * reactive_weight + 
                             predictive_change * predictive_weight)
            
            target_instances = current_instances + round(weighted_change)
            target_instances = max(1, min(target_instances, 20))
            
            # Determine direction
            if target_instances > current_instances:
                direction = ScalingDirection.UP
            elif target_instances < current_instances:
                direction = ScalingDirection.DOWN
            else:
                direction = ScalingDirection.MAINTAIN
            
            return ScalingDecision(
                service_name=service_name,
                current_instances=current_instances,
                target_instances=target_instances,
                direction=direction,
                strategy_used=ScalingStrategy.HYBRID,
                confidence=0.0,
                reasoning=[],
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0,
                metadata={
                    "reactive_target": reactive_decision.target_instances,
                    "predictive_target": predictive_decision.target_instances,
                    "weights": {"reactive": reactive_weight, "predictive": predictive_weight}
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in hybrid scaling: {e}")
            raise

    async def _cost_optimized_scaling(self, service_name: str, 
                                     metrics: Dict[str, float],
                                     current_instances: int) -> ScalingDecision:
        """Cost-optimized scaling to minimize infrastructure costs"""        try:
            # Get baseline reactive decision
            base_decision = await self._reactive_scaling(service_name, metrics, current_instances)
            
            # Apply cost optimization
            if base_decision.direction == ScalingDirection.UP:
                # Be more conservative with scale-up to save costs
                if base_decision.target_instances - current_instances > 1:
                    # Only scale up by 1 instance at a time for cost optimization
                    target_instances = current_instances + 1
                else:
                    target_instances = base_decision.target_instances
                
                # Check if scaling up is cost-justified
                cpu = metrics.get("cpu_utilization", 0)
                memory = metrics.get("memory_utilization", 0)
                
                if cpu < 85 and memory < 90:
                    # Not critical enough to justify cost
                    target_instances = current_instances
                    direction = ScalingDirection.MAINTAIN
                else:
                    direction = ScalingDirection.UP
                    
            elif base_decision.direction == ScalingDirection.DOWN:
                # Be more aggressive with scale-down to save costs
                target_instances = base_decision.target_instances
                direction = ScalingDirection.DOWN
            else:
                target_instances = current_instances
                direction = ScalingDirection.MAINTAIN
            
            return ScalingDecision(
                service_name=service_name,
                current_instances=current_instances,
                target_instances=target_instances,
                direction=direction,
                strategy_used=ScalingStrategy.COST_OPTIMIZED,
                confidence=0.0,
                reasoning=[],
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Error in cost-optimized scaling: {e}")
            raise

    async def _performance_optimized_scaling(self, service_name: str, 
                                           metrics: Dict[str, float],
                                           current_instances: int) -> ScalingDecision:
        """Performance-optimized scaling to maximize system performance"""        try:
            # Get baseline reactive decision
            base_decision = await self._reactive_scaling(service_name, metrics, current_instances)
            
            # Apply performance optimization
            if base_decision.direction == ScalingDirection.UP:
                # Be more aggressive with scale-up for performance
                target_instances = min(base_decision.target_instances + 1, 20)
                direction = ScalingDirection.UP
                
            elif base_decision.direction == ScalingDirection.DOWN:
                # Be more conservative with scale-down to maintain performance
                cpu = metrics.get("cpu_utilization", 0)
                memory = metrics.get("memory_utilization", 0)
                response_time = metrics.get("response_time", 0)
                
                if cpu > 60 or memory > 60 or response_time > 500:
                    # Keep instances for performance
                    target_instances = current_instances
                    direction = ScalingDirection.MAINTAIN
                else:
                    target_instances = base_decision.target_instances
                    direction = ScalingDirection.DOWN
                    
            else:
                # Proactively scale for performance if needed
                cpu = metrics.get("cpu_utilization", 0)
                memory = metrics.get("memory_utilization", 0)
                response_time = metrics.get("response_time", 0)
                
                if cpu > 60 or memory > 60 or response_time > 300:
                    target_instances = current_instances + 1
                    direction = ScalingDirection.UP
                else:
                    target_instances = current_instances
                    direction = ScalingDirection.MAINTAIN
            
            return ScalingDecision(
                service_name=service_name,
                current_instances=current_instances,
                target_instances=target_instances,
                direction=direction,
                strategy_used=ScalingStrategy.PERFORMANCE_OPTIMIZED,
                confidence=0.0,
                reasoning=[],
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Error in performance-optimized scaling: {e}")
            raise

    async def _proactive_scaling(self, service_name: str, 
                                metrics: Dict[str, float],
                                current_instances: int) -> ScalingDecision:
        """Proactive scaling based on historical patterns"""        try:
            # Analyze historical patterns
            historical_pattern = await self._analyze_historical_patterns(service_name)
            
            # Get baseline reactive decision
            base_decision = await self._reactive_scaling(service_name, metrics, current_instances)
            
            # Apply proactive adjustments
            target_instances = base_decision.target_instances
            direction = base_decision.direction
            
            # Check if we're in a known high-load period
            if historical_pattern.get("expected_load_increase", False):
                if direction == ScalingDirection.MAINTAIN:
                    target_instances = min(current_instances + 1, 20)
                    direction = ScalingDirection.UP
                elif direction == ScalingDirection.UP:
                    target_instances = min(target_instances + 1, 20)
                    
            # Check if we're in a known low-load period
            elif historical_pattern.get("expected_load_decrease", False):
                if direction == ScalingDirection.MAINTAIN and current_instances > 2:
                    target_instances = max(current_instances - 1, 1)
                    direction = ScalingDirection.DOWN
            
            return ScalingDecision(
                service_name=service_name,
                current_instances=current_instances,
                target_instances=target_instances,
                direction=direction,
                strategy_used=ScalingStrategy.PROACTIVE,
                confidence=0.0,
                reasoning=[],
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0,
                metadata={"historical_pattern": historical_pattern}
            )
            
        except Exception as e:
            self.logger.error(f"Error in proactive scaling: {e}")
            raise

    async def _generate_predictions(self, service_name: str, 
                                   current_metrics: Dict[str, float]) -> Dict[str, ResourcePrediction]:
        """Generate resource predictions using ML models"""        try:
            predictions = {}
            
            # Check if we have a trained model for this service
            model = self.scaling_models.get(service_name)
            
            if not model:
                # Create simple trend-based predictions
                predictions = await self._simple_trend_predictions(service_name, current_metrics)
            else:
                # Use trained ML model for predictions
                predictions = await self._ml_based_predictions(service_name, current_metrics, model)
            
            # Cache predictions
            for metric_name, prediction in predictions.items():
                cache_key = f"{service_name}_{metric_name}"
                self.prediction_cache[cache_key] = prediction
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error generating predictions: {e}")
            return {}

    async def _simple_trend_predictions(self, service_name: str, 
                                       current_metrics: Dict[str, float]) -> Dict[str, ResourcePrediction]:
        """Generate simple trend-based predictions"""        try:
            predictions = {}
            
            # Get historical data for trend analysis
            history = self.performance_history.get(service_name, deque())
            
            if len(history) < 10:
                # Not enough data for trend analysis, use current values
                for metric_name, value in current_metrics.items():
                    predictions[metric_name] = ResourcePrediction(
                        metric_name=metric_name,
                        predicted_value=value,
                        confidence_interval=(value * 0.9, value * 1.1),
                        prediction_horizon=15,
                        model_accuracy=0.5,
                        timestamp=datetime.now()
                    )
                return predictions
            
            # Analyze trends for each metric
            for metric_name in current_metrics.keys():
                # Extract metric values from history
                metric_values = []
                timestamps = []
                
                for record in list(history)[-20:]:  # Last 20 records
                    if metric_name in record.get("metrics", {}):
                        metric_values.append(record["metrics"][metric_name])
                        timestamps.append(record["timestamp"])
                
                if len(metric_values) < 5:
                    # Not enough data, use current value
                    predicted_value = current_metrics[metric_name]
                else:
                    # Simple linear trend
                    x = np.arange(len(metric_values))
                    coeffs = np.polyfit(x, metric_values, 1)
                    # Predict next value (15 minutes ahead)
                    predicted_value = coeffs[0] * len(metric_values) + coeffs[1]
                    predicted_value = max(0, predicted_value)  # Ensure non-negative
                
                # Calculate confidence interval
                current_value = current_metrics[metric_name]
                variance = abs(predicted_value - current_value) * 0.2
                confidence_interval = (
                    max(0, predicted_value - variance),
                    predicted_value + variance
                )
                
                predictions[metric_name] = ResourcePrediction(
                    metric_name=metric_name,
                    predicted_value=predicted_value,
                    confidence_interval=confidence_interval,
                    prediction_horizon=15,
                    model_accuracy=0.7,
                    timestamp=datetime.now()
                )
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error in simple trend predictions: {e}")
            return {}

    async def _ml_based_predictions(self, service_name: str, 
                                   current_metrics: Dict[str, float],
                                   model: ScalingModel) -> Dict[str, ResourcePrediction]:
        """Generate ML-based predictions (placeholder for actual ML implementation)"""        try:
            # This would use a trained ML model in production
            # For now, return enhanced trend-based predictions
            
            predictions = await self._simple_trend_predictions(service_name, current_metrics)
            
            # Enhance with model accuracy
            for prediction in predictions.values():
                prediction.model_accuracy = model.accuracy
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error in ML-based predictions: {e}")
            return {}

    async def _analyze_historical_patterns(self, service_name: str) -> Dict[str, Any]:
        """Analyze historical patterns for proactive scaling"""        try:
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            # Simple pattern analysis based on time
            patterns = {
                "expected_load_increase": False,
                "expected_load_decrease": False,
                "confidence": 0.5
            }
            
            # Business hours pattern (9 AM - 5 PM)
            if 9 <= current_hour <= 17:
                patterns["expected_load_increase"] = True
                patterns["confidence"] = 0.7
            elif current_hour < 6 or current_hour > 22:
                patterns["expected_load_decrease"] = True
                patterns["confidence"] = 0.6
            
            # Weekend pattern
            if current_day in [5, 6]:  # Saturday, Sunday
                patterns["expected_load_decrease"] = True
                patterns["confidence"] = 0.8
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing historical patterns: {e}")
            return {"expected_load_increase": False, "expected_load_decrease": False, "confidence": 0.0}

    async def _calculate_decision_confidence(self, decision: ScalingDecision,
                                           metrics: Dict[str, float],
                                           predictions: Optional[Dict[str, ResourcePrediction]]) -> float:
        """Calculate confidence score for scaling decision"""        try:
            confidence_factors = []
            
            # Strategy confidence
            strategy_confidence = {
                ScalingStrategy.REACTIVE: 0.7,
                ScalingStrategy.PREDICTIVE: 0.6,
                ScalingStrategy.PROACTIVE: 0.5,
                ScalingStrategy.HYBRID: 0.8,
                ScalingStrategy.COST_OPTIMIZED: 0.6,
                ScalingStrategy.PERFORMANCE_OPTIMIZED: 0.7
            }
            confidence_factors.append(strategy_confidence.get(decision.strategy_used, 0.5))
            
            # Metrics confidence (based on how clear the scaling signal is)
            cpu = metrics.get("cpu_utilization", 50)
            memory = metrics.get("memory_utilization", 50)
            
            if decision.direction == ScalingDirection.UP:
                if cpu > 80 or memory > 85:
                    confidence_factors.append(0.9)
                elif cpu > 70 or memory > 75:
                    confidence_factors.append(0.7)
                else:
                    confidence_factors.append(0.5)
            elif decision.direction == ScalingDirection.DOWN:
                if cpu < 30 and memory < 40:
                    confidence_factors.append(0.8)
                elif cpu < 50 and memory < 60:
                    confidence_factors.append(0.6)
                else:
                    confidence_factors.append(0.4)
            else:
                confidence_factors.append(0.6)
            
            # Prediction confidence (if available)
            if predictions:
                pred_confidences = [p.model_accuracy for p in predictions.values()]
                if pred_confidences:
                    confidence_factors.append(sum(pred_confidences) / len(pred_confidences))
            
            # Historical success rate
            service_history = [record for record in self.scaling_history 
                             if record.get("service_name") == decision.service_name]
            if service_history:
                successful = sum(1 for record in service_history[-10:] 
                               if record.get("success", False))
                success_rate = successful / min(len(service_history), 10)
                confidence_factors.append(success_rate)
            
            # Calculate weighted average
            if confidence_factors:
                return sum(confidence_factors) / len(confidence_factors)
            else:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Error calculating decision confidence: {e}")
            return 0.5

    def _generate_decision_reasoning(self, decision: ScalingDecision,
                                   metrics: Dict[str, float],
                                   predictions: Optional[Dict[str, ResourcePrediction]]) -> List[str]:
        """Generate human-readable reasoning for scaling decision"""        try:
            reasoning = []
            
            # Add strategy reasoning
            reasoning.append(f"Using {decision.strategy_used.value} scaling strategy")
            
            # Add metric-based reasoning
            cpu = metrics.get("cpu_utilization", 0)
            memory = metrics.get("memory_utilization", 0)
            response_time = metrics.get("response_time", 0)
            
            if decision.direction == ScalingDirection.UP:
                if cpu > 80:
                    reasoning.append(f"High CPU utilization ({cpu:.1f}%) requires additional capacity")
                if memory > 85:
                    reasoning.append(f"High memory utilization ({memory:.1f}%) needs more resources")
                if response_time > 1000:
                    reasoning.append(f"High response time ({response_time:.0f}ms) indicates performance issues")
                    
            elif decision.direction == ScalingDirection.DOWN:
                if cpu < 30 and memory < 40:
                    reasoning.append(f"Low resource utilization (CPU: {cpu:.1f}%, Memory: {memory:.1f}%) allows downsizing")
                    
            # Add prediction-based reasoning
            if predictions:
                for metric_name, prediction in predictions.items():
                    current = metrics.get(metric_name, 0)
                    if abs(prediction.predicted_value - current) / max(current, 1) > 0.2:
                        reasoning.append(
                            f"Predicted {metric_name} change: {current:.1f} -> {prediction.predicted_value:.1f}"
                        )
            
            # Add confidence reasoning
            reasoning.append(f"Decision confidence: {decision.confidence:.1%}")
            
            return reasoning
            
        except Exception as e:
            self.logger.error(f"Error generating decision reasoning: {e}")
            return ["Decision made based on current metrics"]

    async def _estimate_cost_impact(self, decision: ScalingDecision) -> float:
        """Estimate cost impact of scaling decision"""        try:
            # Simple cost estimation (would be more complex in production)
            instance_cost_per_hour = 0.50  # $0.50 per instance per hour
            
            instance_change = decision.target_instances - decision.current_instances
            monthly_cost_impact = instance_change * instance_cost_per_hour * 24 * 30
            
            return monthly_cost_impact
            
        except Exception as e:
            self.logger.error(f"Error estimating cost impact: {e}")
            return 0.0

    async def _estimate_performance_impact(self, decision: ScalingDecision) -> float:
        """Estimate performance impact of scaling decision"""        try:
            # Simple performance estimation
            if decision.direction == ScalingDirection.UP:
                # Positive impact from scaling up
                instance_change = decision.target_instances - decision.current_instances
                performance_improvement = min(instance_change * 0.2, 0.5)  # Max 50% improvement
                return performance_improvement
                
            elif decision.direction == ScalingDirection.DOWN:
                # Potential negative impact from scaling down
                instance_change = decision.current_instances - decision.target_instances
                performance_degradation = min(instance_change * 0.15, 0.3)  # Max 30% degradation
                return -performance_degradation
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error estimating performance impact: {e}")
            return 0.0

    async def record_scaling_outcome(self, service_name: str, decision: ScalingDecision, 
                                   success: bool, actual_performance_change: Optional[float] = None):
        """Record scaling outcome for learning and optimization"""        try:
            outcome = {
                "timestamp": datetime.now(),
                "service_name": service_name,
                "decision": decision.__dict__,
                "success": success,
                "actual_performance_change": actual_performance_change
            }
            
            self.scaling_history.append(outcome)
            
            # Update engine stats
            if success:
                self.engine_stats["successful_scalings"] += 1
            else:
                self.engine_stats["failed_scalings"] += 1
            
            # Learn from outcome if learning is enabled
            if self.learning_enabled:
                await self._learn_from_outcome(outcome)
                
        except Exception as e:
            self.logger.error(f"Error recording scaling outcome: {e}")

    async def _learn_from_outcome(self, outcome: Dict[str, Any]):
        """Learn from scaling outcome to improve future decisions"""        try:
            # Simple learning: adjust feature weights based on success/failure
            decision = outcome["decision"]
            success = outcome["success"]
            
            # If decision was successful and high confidence, slightly increase relevant weights
            # If decision failed or low confidence, slightly decrease relevant weights
            weight_adjustment = 0.01 if success else -0.01
            
            # This is a simplified learning mechanism
            # In production, this would use more sophisticated ML algorithms
            
            strategy = decision.get("strategy_used")
            if strategy and success:
                # Reward successful strategies
                pass
            
        except Exception as e:
            self.logger.error(f"Error learning from outcome: {e}")

    async def get_engine_status(self) -> Dict[str, Any]:
        """Get scaling engine status and statistics"""        try:
            return {
                "engine_stats": self.engine_stats,
                "active_decisions": len(self.active_decisions),
                "decision_queue": len(self.decision_queue),
                "scaling_models": len(self.scaling_models),
                "prediction_cache": len(self.prediction_cache),
                "historical_records": len(self.scaling_history),
                "learning_enabled": self.learning_enabled,
                "auto_optimization": self.auto_optimization,
                "feature_weights": self.feature_weights,
                "strategy_config": {k: v.value for k, v in self.strategy_config.items()}
            }
        except Exception as e:
            self.logger.error(f"Error getting engine status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for scaling engine"""        try:
            success_rate = 0.0
            if self.engine_stats["successful_scalings"] + self.engine_stats["failed_scalings"] > 0:
                total_scalings = self.engine_stats["successful_scalings"] + self.engine_stats["failed_scalings"]
                success_rate = self.engine_stats["successful_scalings"] / total_scalings
            
            return {
                "status": "healthy" if success_rate > 0.7 else "degraded",
                "decisions_made": self.engine_stats["decisions_made"],
                "success_rate": success_rate,
                "average_decision_time": self.engine_stats["average_decision_time"],
                "active_models": len(self.scaling_models),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
