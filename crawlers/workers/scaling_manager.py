"""Scaling Manager - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/scaling_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Scaling Manager - Intelligent Auto-Scaling Engine
Responsibility: Dynamic worker pool scaling based on intelligent load analysis
Technologies: ML-based Scaling, Predictive Analytics, Resource Optimization
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Load monitoring → Trend analysis → Resource prediction → 
Scaling decision → Worker allocation → Performance validation → Optimization
"""
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
import statistics
import math
from collections import defaultdict, deque

from .worker_pool import PoolConfig, PoolMetrics
from ...ai.ml.prediction_engine import PredictionEngine
from ...ai.ml.time_series_predictor import TimeSeriesPredictor
from ...monitoring.performance_monitor import PerformanceMonitor
from ...utils.math_utils import MathUtils

logger = logging.getLogger(__name__)


class ScalingDirection(Enum):
    """Scaling directions"""    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"


class ScalingReason(Enum):
    """Reasons for scaling decisions"""    HIGH_LOAD = "high_load"
    LOW_LOAD = "low_load"
    QUEUE_BUILDUP = "queue_buildup"
    RESPONSE_TIME_DEGRADATION = "response_time_degradation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PREDICTIVE_SCALING = "predictive_scaling"
    COST_OPTIMIZATION = "cost_optimization"
    MAINTENANCE = "maintenance"


class ScalingTrigger(Enum):
    """Scaling trigger types"""    THRESHOLD = "threshold"
    TREND = "trend"
    PREDICTIVE = "predictive"
    MANUAL = "manual"
    SCHEDULE = "schedule"


@dataclass
class ScalingRule:
    """Scaling rule definition"""    rule_id: str
    metric_name: str
    threshold_up: float
    threshold_down: float
    duration_seconds: int
    scale_up_count: int
    scale_down_count: int
    cooldown_seconds: int
    enabled: bool = True
    weight: float = 1.0


@dataclass
class ScalingAction:
    """Scaling action definition"""    should_scale: bool
    direction: ScalingDirection
    target_workers: int
    confidence: float
    reason: ScalingReason
    trigger: ScalingTrigger
    estimated_cost_impact: float
    estimated_performance_impact: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingHistory:
    """Scaling action history"""    timestamp: datetime
    action: ScalingAction
    previous_workers: int
    new_workers: int
    success: bool
    actual_performance_impact: Optional[float] = None
    duration_seconds: Optional[float] = None


@dataclass
class LoadPrediction:
    """Load prediction result"""    predicted_load: float
    confidence: float
    time_horizon: int  # seconds
    contributing_factors: List[str] = field(default_factory=list)


class WorkerScalingManager:
    """    Intelligent scaling manager for dynamic worker pool optimization
    
    Features:
    - Multi-metric scaling analysis
    - Predictive load forecasting
    - Cost-aware scaling decisions
    - Performance impact assessment
    - Automatic rule learning
    - Cooldown management
    """
    def __init__(self, config: PoolConfig):
        self.config = config
        
        # Scaling configuration
        self.min_workers = config.min_workers
        self.max_workers = config.max_workers
        self.scaling_threshold = config.scaling_threshold
        self.scale_down_threshold = config.scale_down_threshold
        self.cooldown_period = 300  # 5 minutes default
        
        # Scaling rules
        self.scaling_rules: Dict[str, ScalingRule] = {}
        self.last_scaling_action: Optional[datetime] = None
        self.scaling_history: deque = deque(maxlen=1000)
        
        # Load tracking
        self.load_history: deque = deque(maxlen=1000)
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=200))
        
        # Components
        self.prediction_engine = PredictionEngine()
        self.time_series_predictor = TimeSeriesPredictor()
        self.performance_monitor = PerformanceMonitor()
        self.math_utils = MathUtils()
        
        # Scaling intelligence
        self.adaptive_thresholds = True
        self.predictive_scaling = True
        self.cost_optimization = True
        
        # Performance tracking
        self.scaling_effectiveness = {
            'successful_scale_ups': 0,
            'failed_scale_ups': 0,
            'successful_scale_downs': 0,
            'failed_scale_downs': 0,
            'average_prediction_accuracy': 0.0
        }
        
        # Initialize default rules
        self._initialize_default_rules()

    async def initialize(self) -> None:
        """Initialize the scaling manager"""        try:
            logger.info("🚀 Initializing scaling manager")
            
            # Initialize prediction engines
            await self.prediction_engine.initialize()
            await self.time_series_predictor.initialize()
            
            logger.info("✅ Scaling manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize scaling manager: {e}")
            raise

    async def analyze_scaling_need(
        self, 
        current_load: float, 
        metrics: PoolMetrics, 
        current_workers: int
    ) -> ScalingAction:
        """Analyze if scaling is needed"""        try:
            # Record current metrics
            await self._record_metrics(current_load, metrics)
            
            # Check cooldown period
            if await self._is_in_cooldown():
                return ScalingAction(
                    should_scale=False,
                    direction=ScalingDirection.MAINTAIN,
                    target_workers=current_workers,
                    confidence=1.0,
                    reason=ScalingReason.MAINTENANCE,
                    trigger=ScalingTrigger.THRESHOLD,
                    estimated_cost_impact=0.0,
                    estimated_performance_impact=0.0
                )
            
            # Collect scaling signals
            scaling_signals = await self._collect_scaling_signals(current_load, metrics, current_workers)
            
            # Analyze signals and make decision
            scaling_decision = await self._make_scaling_decision(scaling_signals, current_workers)
            
            # Validate decision
            validated_decision = await self._validate_scaling_decision(scaling_decision, current_workers)
            
            logger.info(f"📊 Scaling analysis: {validated_decision.direction.value} to {validated_decision.target_workers} workers (confidence: {validated_decision.confidence:.2f})")
            
            return validated_decision
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze scaling need: {e}")
            return ScalingAction(
                should_scale=False,
                direction=ScalingDirection.MAINTAIN,
                target_workers=current_workers,
                confidence=0.0,
                reason=ScalingReason.MAINTENANCE,
                trigger=ScalingTrigger.THRESHOLD,
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0
            )

    async def record_scaling_result(
        self, 
        action: ScalingAction, 
        previous_workers: int, 
        new_workers: int, 
        success: bool
    ) -> None:
        """Record scaling action result"""        try:
            # Create history record
            history = ScalingHistory(
                timestamp=datetime.utcnow(),
                action=action,
                previous_workers=previous_workers,
                new_workers=new_workers,
                success=success
            )
            
            self.scaling_history.append(history)
            self.last_scaling_action = datetime.utcnow()
            
            # Update effectiveness metrics
            if success:
                if action.direction == ScalingDirection.SCALE_UP:
                    self.scaling_effectiveness['successful_scale_ups'] += 1
                elif action.direction == ScalingDirection.SCALE_DOWN:
                    self.scaling_effectiveness['successful_scale_downs'] += 1
            else:
                if action.direction == ScalingDirection.SCALE_UP:
                    self.scaling_effectiveness['failed_scale_ups'] += 1
                elif action.direction == ScalingDirection.SCALE_DOWN:
                    self.scaling_effectiveness['failed_scale_downs'] += 1
            
            # Learn from the action
            if self.adaptive_thresholds:
                await self._learn_from_scaling_action(history)
            
            logger.info(f"📈 Scaling result recorded: {action.direction.value} {'succeeded' if success else 'failed'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record scaling result: {e}")

    async def get_scaling_recommendations(self, current_workers: int) -> Dict[str, Any]:
        """Get scaling recommendations and insights"""        try:
            # Predict future load
            load_prediction = await self._predict_future_load()
            
            # Calculate optimal worker count
            optimal_workers = await self._calculate_optimal_workers(load_prediction)
            
            # Analyze cost implications
            cost_analysis = await self._analyze_cost_implications(current_workers, optimal_workers)
            
            # Generate recommendations
            recommendations = {
                'current_workers': current_workers,
                'optimal_workers': optimal_workers,
                'predicted_load': {
                    'next_hour': load_prediction.predicted_load,
                    'confidence': load_prediction.confidence,
                    'factors': load_prediction.contributing_factors
                },
                'cost_analysis': cost_analysis,
                'scaling_history': {
                    'recent_actions': len([h for h in self.scaling_history if h.timestamp > datetime.utcnow() - timedelta(hours=24)]),
                    'success_rate': await self._calculate_success_rate(),
                    'effectiveness': self.scaling_effectiveness
                },
                'rules_status': {
                    'active_rules': len([r for r in self.scaling_rules.values() if r.enabled]),
                    'total_rules': len(self.scaling_rules),
                    'adaptive_thresholds': self.adaptive_thresholds
                }
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to get scaling recommendations: {e}")
            return {}

    def _initialize_default_rules(self) -> None:
        """Initialize default scaling rules"""        try:
            # CPU-based scaling
            self.scaling_rules['cpu_load'] = ScalingRule(
                rule_id='cpu_load',
                metric_name='cpu_utilization',
                threshold_up=0.8,
                threshold_down=0.3,
                duration_seconds=180,
                scale_up_count=2,
                scale_down_count=1,
                cooldown_seconds=300,
                weight=1.0
            )
            
            # Memory-based scaling
            self.scaling_rules['memory_load'] = ScalingRule(
                rule_id='memory_load',
                metric_name='memory_utilization',
                threshold_up=0.85,
                threshold_down=0.25,
                duration_seconds=240,
                scale_up_count=1,
                scale_down_count=1,
                cooldown_seconds=300,
                weight=0.8
            )
            
            # Queue-based scaling
            self.scaling_rules['queue_size'] = ScalingRule(
                rule_id='queue_size',
                metric_name='queue_size',
                threshold_up=10,
                threshold_down=2,
                duration_seconds=120,
                scale_up_count=3,
                scale_down_count=1,
                cooldown_seconds=180,
                weight=1.2
            )
            
            # Response time-based scaling
            self.scaling_rules['response_time'] = ScalingRule(
                rule_id='response_time',
                metric_name='average_response_time',
                threshold_up=300,  # 5 minutes
                threshold_down=60,  # 1 minute
                duration_seconds=300,
                scale_up_count=2,
                scale_down_count=1,
                cooldown_seconds=240,
                weight=0.9
            )
            
            logger.info("✅ Default scaling rules initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize default rules: {e}")

    async def _record_metrics(self, current_load: float, metrics: PoolMetrics) -> None:
        """Record current metrics for analysis"""        try:
            timestamp = datetime.utcnow()
            
            # Record load history
            self.load_history.append({
                'timestamp': timestamp,
                'load': current_load,
                'workers': metrics.total_workers,
                'queue_size': metrics.queue_size,
                'utilization': metrics.resource_utilization
            })
            
            # Record individual metrics
            self.metric_history['cpu_utilization'].append(metrics.resource_utilization)
            self.metric_history['memory_utilization'].append(metrics.resource_utilization * 0.8)  # Estimate
            self.metric_history['queue_size'].append(metrics.queue_size)
            self.metric_history['response_time'].append(metrics.average_response_time)
            self.metric_history['throughput'].append(metrics.throughput_per_second)
            
        except Exception as e:
            logger.error(f"❌ Failed to record metrics: {e}")

    async def _is_in_cooldown(self) -> bool:
        """Check if scaling is in cooldown period"""        try:
            if not self.last_scaling_action:
                return False
            
            elapsed = (datetime.utcnow() - self.last_scaling_action).total_seconds()
            return elapsed < self.cooldown_period
            
        except Exception as e:
            logger.error(f"❌ Failed to check cooldown: {e}")
            return False

    async def _collect_scaling_signals(
        self, 
        current_load: float, 
        metrics: PoolMetrics, 
        current_workers: int
    ) -> Dict[str, Any]:
        """Collect signals for scaling decision"""        try:
            signals = {
                'threshold_signals': {},
                'trend_signals': {},
                'predictive_signals': {},
                'cost_signals': {}
            }
            
            # Threshold-based signals
            for rule_id, rule in self.scaling_rules.items():
                if not rule.enabled:
                    continue
                
                metric_value = await self._get_metric_value(rule.metric_name, metrics)
                
                # Check thresholds
                if metric_value > rule.threshold_up:
                    signals['threshold_signals'][rule_id] = {
                        'direction': ScalingDirection.SCALE_UP,
                        'strength': (metric_value - rule.threshold_up) / rule.threshold_up,
                        'weight': rule.weight,
                        'scale_count': rule.scale_up_count
                    }
                elif metric_value < rule.threshold_down:
                    signals['threshold_signals'][rule_id] = {
                        'direction': ScalingDirection.SCALE_DOWN,
                        'strength': (rule.threshold_down - metric_value) / rule.threshold_down,
                        'weight': rule.weight,
                        'scale_count': rule.scale_down_count
                    }
            
            # Trend-based signals
            signals['trend_signals'] = await self._analyze_metric_trends()
            
            # Predictive signals
            if self.predictive_scaling:
                signals['predictive_signals'] = await self._generate_predictive_signals()
            
            # Cost optimization signals
            if self.cost_optimization:
                signals['cost_signals'] = await self._analyze_cost_efficiency(current_workers)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Failed to collect scaling signals: {e}")
            return {}

    async def _get_metric_value(self, metric_name: str, metrics: PoolMetrics) -> float:
        """Get metric value from pool metrics"""        try:
            metric_mapping = {
                'cpu_utilization': metrics.resource_utilization,
                'memory_utilization': metrics.resource_utilization * 0.8,  # Estimate
                'queue_size': metrics.queue_size,
                'average_response_time': metrics.average_response_time,
                'throughput': metrics.throughput_per_second,
                'error_rate': (metrics.failed_tasks / max(1, metrics.total_tasks_processed)) * 100
            }
            
            return metric_mapping.get(metric_name, 0.0)
            
        except Exception as e:
            logger.error(f"❌ Failed to get metric value for {metric_name}: {e}")
            return 0.0

    async def _analyze_metric_trends(self) -> Dict[str, Any]:
        """Analyze metric trends for scaling signals"""        try:
            trends = {}
            
            for metric_name, history in self.metric_history.items():
                if len(history) < 10:
                    continue
                
                # Calculate trend
                recent_values = list(history)[-10:]
                trend_slope = await self._calculate_trend_slope(recent_values)
                
                # Determine trend strength
                if abs(trend_slope) > 0.1:  # Significant trend
                    if trend_slope > 0:
                        direction = ScalingDirection.SCALE_UP
                    else:
                        direction = ScalingDirection.SCALE_DOWN
                    
                    trends[metric_name] = {
                        'direction': direction,
                        'strength': abs(trend_slope),
                        'confidence': min(1.0, abs(trend_slope) * 2)
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze metric trends: {e}")
            return {}

    async def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression"""        try:
            if len(values) < 2:
                return 0.0
            
            n = len(values)
            x = list(range(n))
            y = values
            
            # Simple linear regression
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate trend slope: {e}")
            return 0.0

    async def _generate_predictive_signals(self) -> Dict[str, Any]:
        """Generate predictive scaling signals"""        try:
            if len(self.load_history) < 20:
                return {}
            
            # Predict load for next periods
            load_values = [h['load'] for h in list(self.load_history)[-50:]]
            
            # Short-term prediction (15 minutes)
            short_term_prediction = await self.time_series_predictor.predict(
                load_values, 
                horizon=3,  # 3 data points ahead
                confidence_level=0.8
            )
            
            # Medium-term prediction (1 hour)
            medium_term_prediction = await self.time_series_predictor.predict(
                load_values,
                horizon=12,  # 12 data points ahead
                confidence_level=0.7
            )
            
            signals = {}
            
            # Analyze predictions
            current_load = load_values[-1] if load_values else 0.0
            
            if short_term_prediction and short_term_prediction['predicted_values']:
                predicted_load = short_term_prediction['predicted_values'][-1]
                confidence = short_term_prediction['confidence']
                
                load_change = (predicted_load - current_load) / max(0.1, current_load)
                
                if abs(load_change) > 0.2 and confidence > 0.6:  # Significant change
                    direction = ScalingDirection.SCALE_UP if load_change > 0 else ScalingDirection.SCALE_DOWN
                    
                    signals['short_term'] = {
                        'direction': direction,
                        'strength': abs(load_change),
                        'confidence': confidence,
                        'predicted_load': predicted_load,
                        'horizon': '15_minutes'
                    }
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Failed to generate predictive signals: {e}")
            return {}

    async def _analyze_cost_efficiency(self, current_workers: int) -> Dict[str, Any]:
        """Analyze cost efficiency for scaling"""        try:
            # Calculate current cost efficiency
            if len(self.load_history) < 5:
                return {}
            
            recent_loads = [h['load'] for h in list(self.load_history)[-10:]]
            avg_load = statistics.mean(recent_loads)
            
            # Cost per worker (estimated)
            cost_per_worker_hour = 5.0  # $5/hour estimate
            
            # Calculate efficiency metrics
            utilization_efficiency = avg_load
            worker_efficiency = utilization_efficiency / current_workers if current_workers > 0 else 0
            
            signals = {}
            
            # Suggest scale down if over-provisioned
            if worker_efficiency < 0.3 and current_workers > self.min_workers:
                signals['cost_optimization'] = {
                    'direction': ScalingDirection.SCALE_DOWN,
                    'strength': 1.0 - worker_efficiency,
                    'estimated_savings': cost_per_worker_hour * (current_workers - max(self.min_workers, current_workers - 1)),
                    'reason': 'over_provisioned'
                }
            
            # Suggest scale up if under-provisioned but cost-effective
            elif worker_efficiency > 0.9 and avg_load > 0.8:
                additional_capacity_value = avg_load * 10  # $10 value per load unit
                additional_cost = cost_per_worker_hour
                
                if additional_capacity_value > additional_cost * 2:  # 2x ROI threshold
                    signals['capacity_expansion'] = {
                        'direction': ScalingDirection.SCALE_UP,
                        'strength': worker_efficiency - 0.8,
                        'roi_estimate': additional_capacity_value / additional_cost,
                        'reason': 'cost_effective_expansion'
                    }
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze cost efficiency: {e}")
            return {}

    async def _make_scaling_decision(self, signals: Dict[str, Any], current_workers: int) -> ScalingAction:
        """Make scaling decision based on collected signals"""        try:
            # Weight and combine signals
            scale_up_score = 0.0
            scale_down_score = 0.0
            confidence_scores = []
            reasons = []
            
            # Process threshold signals
            for signal_id, signal in signals.get('threshold_signals', {}).items():
                weight = signal['weight']
                strength = signal['strength']
                
                if signal['direction'] == ScalingDirection.SCALE_UP:
                    scale_up_score += strength * weight
                    reasons.append(f"threshold_{signal_id}")
                else:
                    scale_down_score += strength * weight
                    reasons.append(f"threshold_{signal_id}")
                
                confidence_scores.append(min(1.0, strength))
            
            # Process trend signals
            for signal_id, signal in signals.get('trend_signals', {}).items():
                strength = signal['strength'] * 0.5  # Trend signals have less weight
                confidence = signal['confidence']
                
                if signal['direction'] == ScalingDirection.SCALE_UP:
                    scale_up_score += strength
                else:
                    scale_down_score += strength
                
                confidence_scores.append(confidence)
                reasons.append(f"trend_{signal_id}")
            
            # Process predictive signals
            for signal_id, signal in signals.get('predictive_signals', {}).items():
                strength = signal['strength'] * signal['confidence'] * 0.3  # Predictive signals discounted
                
                if signal['direction'] == ScalingDirection.SCALE_UP:
                    scale_up_score += strength
                    reasons.append(ScalingReason.PREDICTIVE_SCALING)
                else:
                    scale_down_score += strength
                    reasons.append(ScalingReason.PREDICTIVE_SCALING)
                
                confidence_scores.append(signal['confidence'])
            
            # Process cost signals
            for signal_id, signal in signals.get('cost_signals', {}).items():
                strength = signal['strength'] * 0.4  # Cost signals moderate weight
                
                if signal['direction'] == ScalingDirection.SCALE_UP:
                    scale_up_score += strength
                    reasons.append(ScalingReason.COST_OPTIMIZATION)
                else:
                    scale_down_score += strength
                    reasons.append(ScalingReason.COST_OPTIMIZATION)
                
                confidence_scores.append(0.8)  # Moderate confidence for cost signals
            
            # Make decision
            net_score = scale_up_score - scale_down_score
            decision_threshold = 0.5
            
            if abs(net_score) < decision_threshold:
                # No clear signal, maintain current state
                return ScalingAction(
                    should_scale=False,
                    direction=ScalingDirection.MAINTAIN,
                    target_workers=current_workers,
                    confidence=0.8,
                    reason=ScalingReason.MAINTENANCE,
                    trigger=ScalingTrigger.THRESHOLD,
                    estimated_cost_impact=0.0,
                    estimated_performance_impact=0.0
                )
            
            # Determine scaling direction and magnitude
            if net_score > decision_threshold:
                direction = ScalingDirection.SCALE_UP
                primary_reason = ScalingReason.HIGH_LOAD
                scale_count = min(3, max(1, int(net_score)))  # Scale 1-3 workers
            else:
                direction = ScalingDirection.SCALE_DOWN
                primary_reason = ScalingReason.LOW_LOAD
                scale_count = min(2, max(1, int(abs(net_score))))  # Scale down 1-2 workers
            
            # Calculate target workers
            if direction == ScalingDirection.SCALE_UP:
                target_workers = min(self.max_workers, current_workers + scale_count)
            else:
                target_workers = max(self.min_workers, current_workers - scale_count)
            
            # Calculate confidence
            overall_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.5
            
            # Estimate impacts
            cost_impact = await self._estimate_cost_impact(current_workers, target_workers)
            performance_impact = await self._estimate_performance_impact(current_workers, target_workers)
            
            return ScalingAction(
                should_scale=target_workers != current_workers,
                direction=direction,
                target_workers=target_workers,
                confidence=overall_confidence,
                reason=primary_reason,
                trigger=ScalingTrigger.THRESHOLD,
                estimated_cost_impact=cost_impact,
                estimated_performance_impact=performance_impact,
                metadata={
                    'scale_up_score': scale_up_score,
                    'scale_down_score': scale_down_score,
                    'net_score': net_score,
                    'contributing_reasons': reasons[:5]  # Top 5 reasons
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to make scaling decision: {e}")
            return ScalingAction(
                should_scale=False,
                direction=ScalingDirection.MAINTAIN,
                target_workers=current_workers,
                confidence=0.0,
                reason=ScalingReason.MAINTENANCE,
                trigger=ScalingTrigger.THRESHOLD,
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0
            )

    async def _validate_scaling_decision(self, decision: ScalingAction, current_workers: int) -> ScalingAction:
        """Validate and potentially modify scaling decision"""        try:
            # Boundary checks
            if decision.target_workers < self.min_workers:
                decision.target_workers = self.min_workers
                decision.confidence *= 0.8
            elif decision.target_workers > self.max_workers:
                decision.target_workers = self.max_workers
                decision.confidence *= 0.8
            
            # Safety checks
            worker_change = abs(decision.target_workers - current_workers)
            
            # Limit aggressive scaling
            if worker_change > 5:
                if decision.direction == ScalingDirection.SCALE_UP:
                    decision.target_workers = current_workers + 3
                else:
                    decision.target_workers = current_workers - 2
                decision.confidence *= 0.7
                
                logger.warning(f"⚠️ Limiting aggressive scaling: {worker_change} → {abs(decision.target_workers - current_workers)} workers")
            
            # Check if scaling is actually needed
            if decision.target_workers == current_workers:
                decision.should_scale = False
                decision.direction = ScalingDirection.MAINTAIN
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Failed to validate scaling decision: {e}")
            return decision

    async def _predict_future_load(self) -> LoadPrediction:
        """Predict future load"""        try:
            if len(self.load_history) < 10:
                return LoadPrediction(
                    predicted_load=0.5,
                    confidence=0.3,
                    time_horizon=3600,
                    contributing_factors=['insufficient_data']
                )
            
            # Extract load values
            load_values = [h['load'] for h in list(self.load_history)[-30:]]
            
            # Use time series prediction
            prediction = await self.time_series_predictor.predict(
                load_values,
                horizon=12,  # 1 hour ahead (assuming 5-minute intervals)
                confidence_level=0.8
            )
            
            if prediction and prediction['predicted_values']:
                predicted_load = prediction['predicted_values'][-1]
                confidence = prediction['confidence']
                
                # Identify contributing factors
                factors = []
                if confidence > 0.8:
                    factors.append('strong_historical_pattern')
                if len(load_values) > 20:
                    factors.append('sufficient_data')
                
                return LoadPrediction(
                    predicted_load=predicted_load,
                    confidence=confidence,
                    time_horizon=3600,
                    contributing_factors=factors
                )
            
            # Fallback to simple average
            avg_load = statistics.mean(load_values)
            return LoadPrediction(
                predicted_load=avg_load,
                confidence=0.6,
                time_horizon=3600,
                contributing_factors=['simple_average']
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to predict future load: {e}")
            return LoadPrediction(
                predicted_load=0.5,
                confidence=0.3,
                time_horizon=3600,
                contributing_factors=['prediction_error']
            )

    async def _calculate_optimal_workers(self, load_prediction: LoadPrediction) -> int:
        """Calculate optimal number of workers"""        try:
            predicted_load = load_prediction.predicted_load
            
            # Simple calculation: workers needed for predicted load
            # Assuming each worker can handle ~0.2 load units efficiently
            base_workers = math.ceil(predicted_load / 0.2)
            
            # Add buffer based on confidence
            confidence_buffer = 1 if load_prediction.confidence < 0.7 else 0
            
            # Apply min/max constraints
            optimal = max(self.min_workers, min(self.max_workers, base_workers + confidence_buffer))
            
            return optimal
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate optimal workers: {e}")
            return self.min_workers

    async def _analyze_cost_implications(self, current_workers: int, optimal_workers: int) -> Dict[str, Any]:
        """Analyze cost implications of scaling"""        try:
            cost_per_worker_hour = 5.0  # Estimated cost
            
            worker_diff = optimal_workers - current_workers
            hourly_cost_change = worker_diff * cost_per_worker_hour
            daily_cost_change = hourly_cost_change * 24
            monthly_cost_change = daily_cost_change * 30
            
            return {
                'current_workers': current_workers,
                'optimal_workers': optimal_workers,
                'worker_difference': worker_diff,
                'cost_change': {
                    'hourly': hourly_cost_change,
                    'daily': daily_cost_change,
                    'monthly': monthly_cost_change
                },
                'cost_efficiency': {
                    'current_efficiency': await self._calculate_current_efficiency(),
                    'projected_efficiency': await self._calculate_projected_efficiency(optimal_workers)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze cost implications: {e}")
            return {}

    async def _calculate_current_efficiency(self) -> float:
        """Calculate current cost efficiency"""        try:
            if not self.load_history:
                return 0.5
            
            recent_loads = [h['load'] for h in list(self.load_history)[-10:]]
            recent_workers = [h['workers'] for h in list(self.load_history)[-10:]]
            
            if not recent_loads or not recent_workers:
                return 0.5
            
            avg_load = statistics.mean(recent_loads)
            avg_workers = statistics.mean(recent_workers)
            
            efficiency = avg_load / max(1, avg_workers)
            return min(1.0, efficiency)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate current efficiency: {e}")
            return 0.5

    async def _calculate_projected_efficiency(self, projected_workers: int) -> float:
        """Calculate projected efficiency with new worker count"""        try:
            if not self.load_history:
                return 0.5
            
            recent_loads = [h['load'] for h in list(self.load_history)[-10:]]
            if not recent_loads:
                return 0.5
            
            avg_load = statistics.mean(recent_loads)
            efficiency = avg_load / max(1, projected_workers)
            
            return min(1.0, efficiency)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate projected efficiency: {e}")
            return 0.5

    async def _calculate_success_rate(self) -> float:
        """Calculate scaling action success rate"""        try:
            if not self.scaling_history:
                return 0.0
            
            total_actions = len(self.scaling_history)
            successful_actions = sum(1 for h in self.scaling_history if h.success)
            
            return successful_actions / total_actions
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate success rate: {e}")
            return 0.0

    async def _estimate_cost_impact(self, current_workers: int, target_workers: int) -> float:
        """Estimate cost impact of scaling"""        try:
            worker_diff = target_workers - current_workers
            cost_per_worker_hour = 5.0
            
            return worker_diff * cost_per_worker_hour
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate cost impact: {e}")
            return 0.0

    async def _estimate_performance_impact(self, current_workers: int, target_workers: int) -> float:
        """Estimate performance impact of scaling"""        try:
            if target_workers > current_workers:
                # Scaling up should improve performance
                improvement_ratio = target_workers / max(1, current_workers)
                return min(0.5, (improvement_ratio - 1) * 0.3)  # Up to 50% improvement
            elif target_workers < current_workers:
                # Scaling down might degrade performance
                degradation_ratio = current_workers / max(1, target_workers)
                return -min(0.3, (degradation_ratio - 1) * 0.2)  # Up to 30% degradation
            else:
                return 0.0
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate performance impact: {e}")
            return 0.0

    async def _learn_from_scaling_action(self, history: ScalingHistory) -> None:
        """Learn from scaling action to improve future decisions"""        try:
            # This would implement machine learning to adapt thresholds
            # and improve scaling decisions based on historical outcomes
            
            if history.success:
                # Reinforce successful decisions
                logger.debug(f"🎯 Learning from successful scaling action: {history.action.direction.value}")
            else:
                # Learn from failures
                logger.debug(f"📚 Learning from failed scaling action: {history.action.direction.value}")
                
                # Adjust relevant thresholds (simplified approach)
                if history.action.trigger == ScalingTrigger.THRESHOLD:
                    # Make thresholds slightly more conservative
                    for rule in self.scaling_rules.values():
                        if history.action.direction == ScalingDirection.SCALE_UP:
                            rule.threshold_up *= 1.05  # Increase threshold by 5%
                        else:
                            rule.threshold_down *= 0.95  # Decrease threshold by 5%
            
        except Exception as e:
            logger.error(f"❌ Failed to learn from scaling action: {e}")
