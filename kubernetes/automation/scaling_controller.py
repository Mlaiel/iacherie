"""
Scaling Controller - Deployment Automation

Advanced auto-scaling management system for the IA Influencer Agent platform,
providing intelligent resource scaling, load-based adjustments, and
predictive scaling capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import math
import statistics
from collections import defaultdict, deque

from ..core.base import BaseComponent
from ..kubernetes.deployment_manager import DeploymentManager
from ..monitoring.metrics_collector import MetricsCollector
from ..infrastructure.resource_manager import ResourceManager
from ..ai.prediction_engine import PredictionEngine


class ScalingDirection(Enum):
    """Scaling direction"""
    UP = "up"
    DOWN = "down"
    MAINTAIN = "maintain"


class ScalingTriggerType(Enum):
    """Scaling trigger types"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    QUEUE_LENGTH = "queue_length"
    RESPONSE_TIME = "response_time"
    CUSTOM_METRIC = "custom_metric"
    SCHEDULE = "schedule"
    PREDICTIVE = "predictive"


class ScalingStrategy(Enum):
    """Scaling strategies"""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"
    SCHEDULED = "scheduled"


@dataclass
class ScalingMetric:
    """Scaling metric definition"""
    name: str
    type: ScalingTriggerType
    target_value: float
    tolerance: float = 0.1  # 10% tolerance
    weight: float = 1.0  # Metric weight in decision making
    min_samples: int = 3  # Minimum samples before scaling
    cooldown_seconds: int = 300  # 5 minutes cooldown
    scale_up_threshold: Optional[float] = None
    scale_down_threshold: Optional[float] = None


@dataclass
class ScalingPolicy:
    """Scaling policy configuration"""
    service_name: str
    min_replicas: int = 1
    max_replicas: int = 20
    target_cpu_utilization: float = 70.0
    target_memory_utilization: float = 80.0
    scale_up_cooldown: int = 300  # 5 minutes
    scale_down_cooldown: int = 600  # 10 minutes
    scale_up_factor: float = 1.5  # Scale up by 50%
    scale_down_factor: float = 0.8  # Scale down by 20%
    metrics: List[ScalingMetric] = field(default_factory=list)
    strategy: ScalingStrategy = ScalingStrategy.REACTIVE
    enabled: bool = True


@dataclass
class ScalingEvent:
    """Scaling event record"""
    event_id: str
    service_name: str
    timestamp: datetime
    direction: ScalingDirection
    from_replicas: int
    to_replicas: int
    trigger_metrics: Dict[str, float]
    trigger_type: ScalingTriggerType
    strategy_used: ScalingStrategy
    execution_time: float
    success: bool
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourcePrediction:
    """Resource prediction data"""
    service_name: str
    predicted_load: float
    confidence: float
    time_horizon: int  # Minutes into future
    recommended_replicas: int
    prediction_timestamp: datetime
    factors: Dict[str, Any] = field(default_factory=dict)


class ScalingController(BaseComponent):
    """
    Enterprise-grade auto-scaling controller.
    
    Provides intelligent auto-scaling capabilities with multiple strategies,
    predictive scaling, custom metrics support, and comprehensive
    scaling event tracking and analysis.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core managers
        self.deployment_manager = DeploymentManager(config.get('kubernetes', {}))
        self.metrics_collector = MetricsCollector(config.get('metrics', {}))
        self.resource_manager = ResourceManager(config.get('resources', {}))
        self.prediction_engine = PredictionEngine(config.get('prediction', {}))
        
        # Scaling state
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
        self.scaling_events: List[ScalingEvent] = []
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.last_scaling_times: Dict[str, datetime] = {}
        self.resource_predictions: Dict[str, ResourcePrediction] = {}
        
        # Configuration
        self.scaling_enabled = config.get('scaling_enabled', True)
        self.default_check_interval = config.get('check_interval_seconds', 60)
        self.max_scaling_events_per_hour = config.get('max_scaling_events_per_hour', 10)
        self.prediction_horizon_minutes = config.get('prediction_horizon_minutes', 30)
        
        # IA Influencer Agent specific services with creator workflow patterns
        self.creator_workflow_services = {
            'ai_agent': {
                'cpu_intensive': True,
                'memory_intensive': True,
                'io_intensive': False,
                'scaling_sensitivity': 'high',
                'creator_impact': 'critical',
                'peak_patterns': ['morning_uploads', 'evening_generation']
            },
            'content_protection': {
                'cpu_intensive': True,
                'memory_intensive': False,
                'io_intensive': True,
                'scaling_sensitivity': 'medium',
                'creator_impact': 'critical',
                'peak_patterns': ['viral_content_detection', 'mass_upload_periods']
            },
            'fingerprinting': {
                'cpu_intensive': True,
                'memory_intensive': True,
                'io_intensive': True,
                'scaling_sensitivity': 'high',
                'creator_impact': 'critical',
                'peak_patterns': ['new_content_processing', 'protection_scanning']
            },
            'audio_processing': {
                'cpu_intensive': True,
                'memory_intensive': True,
                'io_intensive': False,
                'scaling_sensitivity': 'high',
                'creator_impact': 'critical',
                'peak_patterns': ['music_generation', 'audio_analysis'],
                'gpu_required': True
            },
            'monetization': {
                'cpu_intensive': False,
                'memory_intensive': False,
                'io_intensive': True,
                'scaling_sensitivity': 'low',
                'creator_impact': 'high',
                'peak_patterns': ['payment_processing', 'revenue_calculation']
            },
            'collaboration_matching': {
                'cpu_intensive': True,
                'memory_intensive': True,
                'io_intensive': False,
                'scaling_sensitivity': 'medium',
                'creator_impact': 'medium',
                'peak_patterns': ['matching_requests', 'recommendation_updates']
            },
            'revenue_analytics': {
                'cpu_intensive': True,
                'memory_intensive': True,
                'io_intensive': True,
                'scaling_sensitivity': 'medium',
                'creator_impact': 'high',
                'peak_patterns': ['report_generation', 'trend_analysis']
            },
            'seo_optimization': {
                'cpu_intensive': False,
                'memory_intensive': False,
                'io_intensive': True,
                'scaling_sensitivity': 'low',
                'creator_impact': 'medium',
                'peak_patterns': ['content_optimization', 'keyword_research']
            },
            'crawler': {
                'cpu_intensive': False,
                'memory_intensive': False,
                'io_intensive': True,
                'scaling_sensitivity': 'medium',
                'creator_impact': 'medium',
                'peak_patterns': ['platform_scanning', 'infringement_detection']
            },
            'api_gateway': {
                'cpu_intensive': False,
                'memory_intensive': False,
                'io_intensive': True,
                'scaling_sensitivity': 'high',
                'creator_impact': 'critical',
                'peak_patterns': ['creator_uploads', 'dashboard_access']
            }
        }
        
        # Creator activity patterns for predictive scaling
        self.creator_patterns = {
            'daily_peaks': {
                'morning_upload': {'start': '08:00', 'end': '10:00', 'multiplier': 2.5},
                'lunch_break': {'start': '12:00', 'end': '14:00', 'multiplier': 1.8},
                'evening_creation': {'start': '18:00', 'end': '22:00', 'multiplier': 3.2},
                'late_night': {'start': '22:00', 'end': '02:00', 'multiplier': 0.3}
            },
            'weekly_patterns': {
                'weekend_boost': {'days': ['saturday', 'sunday'], 'multiplier': 2.0},
                'monday_rush': {'days': ['monday'], 'multiplier': 1.5},
                'midweek_steady': {'days': ['tuesday', 'wednesday', 'thursday'], 'multiplier': 1.0},
                'friday_wind_down': {'days': ['friday'], 'multiplier': 0.8}
            },
            'viral_content_multipliers': {
                'trending_detection': {'multiplier': 5.0, 'duration_minutes': 60},
                'mass_protection_alert': {'multiplier': 8.0, 'duration_minutes': 120},
                'platform_surge': {'multiplier': 3.5, 'duration_minutes': 90}
            }
        }

        # Initialize default policies
        self._initialize_creator_focused_policies()

    def _initialize_default_policies(self) -> None:
        """Initialize default scaling policies for IA services"""
        
        for service_name, service_config in self.ia_services.items():
            sensitivity = service_config['scaling_sensitivity']
            
            # Adjust thresholds based on sensitivity
            if sensitivity == 'high':
                cpu_target = 60.0
                memory_target = 70.0
                scale_up_cooldown = 180  # 3 minutes
                scale_down_cooldown = 300  # 5 minutes
                max_replicas = 25
            elif sensitivity == 'medium':
                cpu_target = 70.0
                memory_target = 80.0
                scale_up_cooldown = 300  # 5 minutes
                scale_down_cooldown = 600  # 10 minutes
                max_replicas = 15
            else:  # low
                cpu_target = 80.0
                memory_target = 85.0
                scale_up_cooldown = 600  # 10 minutes
                scale_down_cooldown = 900  # 15 minutes
                max_replicas = 10
            
            # Create metrics based on service characteristics
            metrics = []
            
            # CPU metric (always included)
            metrics.append(ScalingMetric(
                name="cpu_utilization",
                type=ScalingTriggerType.CPU_UTILIZATION,
                target_value=cpu_target,
                tolerance=0.1,
                weight=2.0 if service_config['cpu_intensive'] else 1.0,
                cooldown_seconds=scale_up_cooldown
            ))
            
            # Memory metric (always included)
            metrics.append(ScalingMetric(
                name="memory_utilization",
                type=ScalingTriggerType.MEMORY_UTILIZATION,
                target_value=memory_target,
                tolerance=0.1,
                weight=2.0 if service_config['memory_intensive'] else 1.0,
                cooldown_seconds=scale_up_cooldown
            ))
            
            # Request rate for API-facing services
            if service_name in ['api_gateway', 'ai_agent']:
                metrics.append(ScalingMetric(
                    name="request_rate",
                    type=ScalingTriggerType.REQUEST_RATE,
                    target_value=100.0,  # requests per second
                    tolerance=0.2,
                    weight=1.5,
                    cooldown_seconds=scale_up_cooldown
                ))
            
            # Queue length for processing services
            if service_name in ['ai_agent', 'content_protection', 'fingerprinting']:
                metrics.append(ScalingMetric(
                    name="queue_length",
                    type=ScalingTriggerType.QUEUE_LENGTH,
                    target_value=50.0,  # items in queue
                    tolerance=0.3,
                    weight=2.0,
                    cooldown_seconds=scale_up_cooldown
                ))
            
            # Response time for user-facing services
            if service_name in ['api_gateway', 'ai_agent']:
                metrics.append(ScalingMetric(
                    name="response_time",
                    type=ScalingTriggerType.RESPONSE_TIME,
                    target_value=500.0,  # milliseconds
                    tolerance=0.2,
                    weight=1.5,
                    cooldown_seconds=scale_up_cooldown
                ))
            
            policy = ScalingPolicy(
                service_name=service_name,
                min_replicas=1,
                max_replicas=max_replicas,
                target_cpu_utilization=cpu_target,
                target_memory_utilization=memory_target,
                scale_up_cooldown=scale_up_cooldown,
                scale_down_cooldown=scale_down_cooldown,
                metrics=metrics,
                strategy=ScalingStrategy.HYBRID,
                enabled=True
            )
            
            self.scaling_policies[service_name] = policy

    async def start_scaling_controller(self, environment: str) -> None:
        """Start the scaling controller"""
        
        if not self.scaling_enabled:
            self.logger.info("Scaling controller is disabled")
            return
        
        self.logger.info("Starting scaling controller")
        
        # Start background tasks
        asyncio.create_task(self._scaling_monitor_loop(environment))
        asyncio.create_task(self._prediction_update_loop(environment))
        asyncio.create_task(self._metrics_collection_loop(environment))

    async def _scaling_monitor_loop(self, environment: str) -> None:
        """Main scaling monitor loop"""
        
        while self.scaling_enabled:
            try:
                await self._evaluate_scaling_decisions(environment)
                await asyncio.sleep(self.default_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in scaling monitor loop: {str(e)}", exc_info=True)
                await asyncio.sleep(self.default_check_interval)

    async def _prediction_update_loop(self, environment: str) -> None:
        """Update resource predictions periodically"""
        
        while self.scaling_enabled:
            try:
                await self._update_resource_predictions(environment)
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in prediction update loop: {str(e)}", exc_info=True)
                await asyncio.sleep(300)

    async def _metrics_collection_loop(self, environment: str) -> None:
        """Collect metrics for scaling decisions"""
        
        while self.scaling_enabled:
            try:
                await self._collect_scaling_metrics(environment)
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in metrics collection loop: {str(e)}", exc_info=True)
                await asyncio.sleep(30)

    async def _evaluate_scaling_decisions(self, environment: str) -> None:
        """Evaluate and execute scaling decisions for all services"""
        
        namespace = f"ia-influencer-{environment}"
        
        for service_name, policy in self.scaling_policies.items():
            if not policy.enabled:
                continue
            
            try:
                # Check if service is in cooldown
                if self._is_service_in_cooldown(service_name, policy):
                    continue
                
                # Check scaling event rate limits
                if self._exceeds_scaling_rate_limit(service_name):
                    continue
                
                # Get current metrics
                current_metrics = await self._get_current_service_metrics(
                    service_name, namespace
                )
                
                # Make scaling decision
                scaling_decision = await self._make_scaling_decision(
                    service_name, policy, current_metrics, environment
                )
                
                if scaling_decision['action'] != ScalingDirection.MAINTAIN:
                    await self._execute_scaling_action(
                        service_name, scaling_decision, namespace, environment
                    )
                
            except Exception as e:
                self.logger.error(
                    f"Error evaluating scaling for {service_name}: {str(e)}",
                    exc_info=True
                )

    async def _get_current_service_metrics(
        self,
        service_name: str,
        namespace: str
    ) -> Dict[str, float]:
        """Get current metrics for a service"""
        
        metrics = {}
        
        try:
            # CPU utilization
            cpu_metrics = await self.metrics_collector.get_cpu_utilization(
                service=service_name,
                namespace=namespace,
                time_range="5m"
            )
            if cpu_metrics:
                metrics['cpu_utilization'] = cpu_metrics['average']
            
            # Memory utilization
            memory_metrics = await self.metrics_collector.get_memory_utilization(
                service=service_name,
                namespace=namespace,
                time_range="5m"
            )
            if memory_metrics:
                metrics['memory_utilization'] = memory_metrics['average']
            
            # Request rate
            request_metrics = await self.metrics_collector.get_request_rate(
                service=service_name,
                namespace=namespace,
                time_range="5m"
            )
            if request_metrics:
                metrics['request_rate'] = request_metrics['per_second']
            
            # Queue length (for processing services)
            if service_name in ['ai_agent', 'content_protection', 'fingerprinting']:
                queue_metrics = await self.metrics_collector.get_queue_length(
                    service=service_name,
                    namespace=namespace
                )
                if queue_metrics:
                    metrics['queue_length'] = queue_metrics['current_length']
            
            # Response time
            response_metrics = await self.metrics_collector.get_response_time(
                service=service_name,
                namespace=namespace,
                time_range="5m"
            )
            if response_metrics:
                metrics['response_time'] = response_metrics['p95']
            
            # Store metrics in history
            self.metric_history[service_name].append({
                'timestamp': datetime.utcnow(),
                'metrics': metrics.copy()
            })
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics for {service_name}: {str(e)}")
        
        return metrics

    async def _make_scaling_decision(
        self,
        service_name: str,
        policy: ScalingPolicy,
        current_metrics: Dict[str, float],
        environment: str
    ) -> Dict[str, Any]:
        """Make intelligent scaling decision"""
        
        # Get current replica count
        current_replicas = await self.deployment_manager.get_replica_count(
            service_name, f"ia-influencer-{environment}"
        )
        
        decision = {
            'action': ScalingDirection.MAINTAIN,
            'target_replicas': current_replicas,
            'confidence': 0.0,
            'reasons': [],
            'strategy_used': policy.strategy,
            'trigger_metrics': current_metrics.copy()
        }
        
        if policy.strategy == ScalingStrategy.REACTIVE:
            decision = await self._reactive_scaling_decision(
                service_name, policy, current_metrics, current_replicas
            )
        elif policy.strategy == ScalingStrategy.PREDICTIVE:
            decision = await self._predictive_scaling_decision(
                service_name, policy, current_metrics, current_replicas, environment
            )
        elif policy.strategy == ScalingStrategy.HYBRID:
            # Combine reactive and predictive
            reactive_decision = await self._reactive_scaling_decision(
                service_name, policy, current_metrics, current_replicas
            )
            predictive_decision = await self._predictive_scaling_decision(
                service_name, policy, current_metrics, current_replicas, environment
            )
            
            decision = self._combine_scaling_decisions(
                reactive_decision, predictive_decision, current_replicas
            )
        elif policy.strategy == ScalingStrategy.SCHEDULED:
            decision = await self._scheduled_scaling_decision(
                service_name, policy, current_replicas
            )
        
        # Apply constraints
        decision['target_replicas'] = max(
            policy.min_replicas,
            min(policy.max_replicas, decision['target_replicas'])
        )
        
        # Determine final action
        if decision['target_replicas'] > current_replicas:
            decision['action'] = ScalingDirection.UP
        elif decision['target_replicas'] < current_replicas:
            decision['action'] = ScalingDirection.DOWN
        else:
            decision['action'] = ScalingDirection.MAINTAIN
        
        return decision

    async def _reactive_scaling_decision(
        self,
        service_name: str,
        policy: ScalingPolicy,
        current_metrics: Dict[str, float],
        current_replicas: int
    ) -> Dict[str, Any]:
        """Make reactive scaling decision based on current metrics"""
        
        decision = {
            'action': ScalingDirection.MAINTAIN,
            'target_replicas': current_replicas,
            'confidence': 0.0,
            'reasons': [],
            'strategy_used': ScalingStrategy.REACTIVE,
            'trigger_metrics': current_metrics.copy()
        }
        
        scale_up_votes = 0
        scale_down_votes = 0
        total_weight = 0
        
        for metric in policy.metrics:
            if metric.name not in current_metrics:
                continue
            
            current_value = current_metrics[metric.name]
            target_value = metric.target_value
            tolerance = metric.tolerance
            weight = metric.weight
            
            total_weight += weight
            
            # Calculate deviation from target
            if metric.type in [ScalingTriggerType.CPU_UTILIZATION, ScalingTriggerType.MEMORY_UTILIZATION]:
                # Higher values indicate need to scale up
                upper_threshold = target_value * (1 + tolerance)
                lower_threshold = target_value * (1 - tolerance)
                
                if current_value > upper_threshold:
                    scale_up_votes += weight
                    decision['reasons'].append(
                        f"{metric.name} {current_value:.1f}% > {upper_threshold:.1f}% threshold"
                    )
                elif current_value < lower_threshold:
                    scale_down_votes += weight
                    decision['reasons'].append(
                        f"{metric.name} {current_value:.1f}% < {lower_threshold:.1f}% threshold"
                    )
            
            elif metric.type == ScalingTriggerType.REQUEST_RATE:
                # Higher request rate indicates need to scale up
                upper_threshold = target_value * (1 + tolerance)
                lower_threshold = target_value * (1 - tolerance)
                
                if current_value > upper_threshold:
                    scale_up_votes += weight
                    decision['reasons'].append(
                        f"Request rate {current_value:.1f} rps > {upper_threshold:.1f} threshold"
                    )
                elif current_value < lower_threshold:
                    scale_down_votes += weight
                    decision['reasons'].append(
                        f"Request rate {current_value:.1f} rps < {lower_threshold:.1f} threshold"
                    )
            
            elif metric.type == ScalingTriggerType.QUEUE_LENGTH:
                # Higher queue length indicates need to scale up
                upper_threshold = target_value * (1 + tolerance)
                lower_threshold = target_value * (1 - tolerance)
                
                if current_value > upper_threshold:
                    scale_up_votes += weight
                    decision['reasons'].append(
                        f"Queue length {current_value:.0f} > {upper_threshold:.0f} threshold"
                    )
                elif current_value < lower_threshold:
                    scale_down_votes += weight
                    decision['reasons'].append(
                        f"Queue length {current_value:.0f} < {lower_threshold:.0f} threshold"
                    )
            
            elif metric.type == ScalingTriggerType.RESPONSE_TIME:
                # Higher response time indicates need to scale up
                upper_threshold = target_value * (1 + tolerance)
                lower_threshold = target_value * (1 - tolerance)
                
                if current_value > upper_threshold:
                    scale_up_votes += weight
                    decision['reasons'].append(
                        f"Response time {current_value:.0f}ms > {upper_threshold:.0f}ms threshold"
                    )
                elif current_value < lower_threshold:
                    scale_down_votes += weight
                    decision['reasons'].append(
                        f"Response time {current_value:.0f}ms < {lower_threshold:.0f}ms threshold"
                    )
        
        if total_weight == 0:
            return decision
        
        # Calculate scaling confidence based on voting
        scale_up_confidence = scale_up_votes / total_weight
        scale_down_confidence = scale_down_votes / total_weight
        
        # Make scaling decision
        if scale_up_confidence > 0.5:  # More than 50% of weighted votes
            # Calculate scale-up factor
            scale_factor = min(policy.scale_up_factor, 1 + scale_up_confidence)
            decision['target_replicas'] = math.ceil(current_replicas * scale_factor)
            decision['confidence'] = scale_up_confidence
            
        elif scale_down_confidence > 0.7:  # Higher threshold for scale-down
            # Calculate scale-down factor
            scale_factor = max(policy.scale_down_factor, 1 - (scale_down_confidence * 0.5))
            decision['target_replicas'] = math.floor(current_replicas * scale_factor)
            decision['confidence'] = scale_down_confidence
        
        return decision

    async def _predictive_scaling_decision(
        self,
        service_name: str,
        policy: ScalingPolicy,
        current_metrics: Dict[str, float],
        current_replicas: int,
        environment: str
    ) -> Dict[str, Any]:
        """Make predictive scaling decision based on forecasted load"""
        
        decision = {
            'action': ScalingDirection.MAINTAIN,
            'target_replicas': current_replicas,
            'confidence': 0.0,
            'reasons': [],
            'strategy_used': ScalingStrategy.PREDICTIVE,
            'trigger_metrics': current_metrics.copy()
        }
        
        # Get resource prediction
        prediction = self.resource_predictions.get(service_name)
        
        if not prediction or prediction.confidence < 0.6:
            # Low confidence prediction, fall back to current replica count
            decision['reasons'].append("Low confidence prediction, maintaining current scale")
            return decision
        
        # Use predicted load to determine required replicas
        predicted_replicas = prediction.recommended_replicas
        
        # Add predictive scaling reasons
        decision['reasons'].append(
            f"Predicted load: {prediction.predicted_load:.2f} "
            f"(confidence: {prediction.confidence:.2f})"
        )
        
        # Consider prediction time horizon
        time_to_prediction = (prediction.prediction_timestamp - datetime.utcnow()).total_seconds() / 60
        
        if time_to_prediction > self.prediction_horizon_minutes:
            # Prediction is too far in the future, scale more conservatively
            if predicted_replicas > current_replicas:
                predicted_replicas = current_replicas + max(1, (predicted_replicas - current_replicas) // 2)
            elif predicted_replicas < current_replicas:
                predicted_replicas = current_replicas - max(1, (current_replicas - predicted_replicas) // 2)
            
            decision['reasons'].append(
                f"Adjusted for prediction horizon ({time_to_prediction:.0f} min)"
            )
        
        decision['target_replicas'] = predicted_replicas
        decision['confidence'] = prediction.confidence
        
        return decision

    def _combine_scaling_decisions(
        self,
        reactive_decision: Dict[str, Any],
        predictive_decision: Dict[str, Any],
        current_replicas: int
    ) -> Dict[str, Any]:
        """Combine reactive and predictive scaling decisions"""
        
        # Weight decisions by confidence
        reactive_weight = reactive_decision['confidence']
        predictive_weight = predictive_decision['confidence']
        total_weight = reactive_weight + predictive_weight
        
        if total_weight == 0:
            return {
                'action': ScalingDirection.MAINTAIN,
                'target_replicas': current_replicas,
                'confidence': 0.0,
                'reasons': ['No confident scaling signals'],
                'strategy_used': ScalingStrategy.HYBRID,
                'trigger_metrics': reactive_decision['trigger_metrics']
            }
        
        # Weighted average of target replicas
        weighted_replicas = (
            (reactive_decision['target_replicas'] * reactive_weight) +
            (predictive_decision['target_replicas'] * predictive_weight)
        ) / total_weight
        
        combined_decision = {
            'action': ScalingDirection.MAINTAIN,
            'target_replicas': round(weighted_replicas),
            'confidence': total_weight / 2,  # Average confidence
            'reasons': reactive_decision['reasons'] + predictive_decision['reasons'],
            'strategy_used': ScalingStrategy.HYBRID,
            'trigger_metrics': reactive_decision['trigger_metrics']
        }
        
        return combined_decision

    async def _scheduled_scaling_decision(
        self,
        service_name: str,
        policy: ScalingPolicy,
        current_replicas: int
    ) -> Dict[str, Any]:
        """Make scheduled scaling decision based on time patterns"""
        
        decision = {
            'action': ScalingDirection.MAINTAIN,
            'target_replicas': current_replicas,
            'confidence': 1.0,  # High confidence for scheduled scaling
            'reasons': [],
            'strategy_used': ScalingStrategy.SCHEDULED,
            'trigger_metrics': {}
        }
        
        current_time = datetime.utcnow()
        hour = current_time.hour
        day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
        
        # Define scaling schedules for IA Influencer services
        # These are based on typical content creation and consumption patterns
        
        if service_name == 'ai_agent':
            # High usage during content creation hours (8 AM - 10 PM UTC)
            if 8 <= hour <= 22:
                target_replicas = max(3, policy.min_replicas)
                decision['reasons'].append("Peak content creation hours")
            else:
                target_replicas = policy.min_replicas
                decision['reasons'].append("Off-peak hours")
        
        elif service_name == 'content_protection':
            # Steady usage with peaks during upload times
            if 6 <= hour <= 23:  # Extended hours for global usage
                target_replicas = max(2, policy.min_replicas)
                decision['reasons'].append("Content upload hours")
            else:
                target_replicas = policy.min_replicas
                decision['reasons'].append("Low upload period")
        
        elif service_name == 'api_gateway':
            # High usage during business hours across time zones
            if 6 <= hour <= 24 or day_of_week < 5:  # Weekdays with extended hours
                target_replicas = max(2, policy.min_replicas)
                decision['reasons'].append("Business hours")
            else:
                target_replicas = policy.min_replicas
                decision['reasons'].append("Weekend low-traffic period")
        
        else:
            # Default schedule for other services
            if 8 <= hour <= 20:
                target_replicas = max(2, policy.min_replicas)
                decision['reasons'].append("Standard business hours")
            else:
                target_replicas = policy.min_replicas
                decision['reasons'].append("Off-hours")
        
        decision['target_replicas'] = target_replicas
        
        return decision

    async def _execute_scaling_action(
        self,
        service_name: str,
        scaling_decision: Dict[str, Any],
        namespace: str,
        environment: str
    ) -> None:
        """Execute the scaling action"""
        
        current_replicas = await self.deployment_manager.get_replica_count(
            service_name, namespace
        )
        target_replicas = scaling_decision['target_replicas']
        
        if current_replicas == target_replicas:
            return
        
        event_id = f"scale-{service_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        start_time = datetime.utcnow()
        
        try:
            # Execute scaling
            await self.deployment_manager.scale_deployment(
                service_name, namespace, target_replicas
            )
            
            # Wait for scaling to complete
            await self.deployment_manager.wait_for_scale_completion(
                service_name, namespace, target_replicas, timeout=300
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record scaling event
            scaling_event = ScalingEvent(
                event_id=event_id,
                service_name=service_name,
                timestamp=start_time,
                direction=scaling_decision['action'],
                from_replicas=current_replicas,
                to_replicas=target_replicas,
                trigger_metrics=scaling_decision['trigger_metrics'],
                trigger_type=self._determine_primary_trigger(scaling_decision),
                strategy_used=scaling_decision['strategy_used'],
                execution_time=execution_time,
                success=True,
                reason='; '.join(scaling_decision['reasons']),
                metadata={
                    'confidence': scaling_decision['confidence'],
                    'environment': environment
                }
            )
            
            self.scaling_events.append(scaling_event)
            self.last_scaling_times[service_name] = start_time
            
            self.logger.info(
                f"Successfully scaled {service_name} from {current_replicas} to {target_replicas} replicas"
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record failed scaling event
            scaling_event = ScalingEvent(
                event_id=event_id,
                service_name=service_name,
                timestamp=start_time,
                direction=scaling_decision['action'],
                from_replicas=current_replicas,
                to_replicas=target_replicas,
                trigger_metrics=scaling_decision['trigger_metrics'],
                trigger_type=self._determine_primary_trigger(scaling_decision),
                strategy_used=scaling_decision['strategy_used'],
                execution_time=execution_time,
                success=False,
                reason=f"Scaling failed: {str(e)}",
                metadata={
                    'confidence': scaling_decision['confidence'],
                    'environment': environment,
                    'error': str(e)
                }
            )
            
            self.scaling_events.append(scaling_event)
            
            self.logger.error(
                f"Failed to scale {service_name} from {current_replicas} to {target_replicas}: {str(e)}"
            )
            
            raise

    def _determine_primary_trigger(self, scaling_decision: Dict[str, Any]) -> ScalingTriggerType:
        """Determine the primary trigger type for scaling"""
        
        # Simple heuristic: if CPU or memory mentioned in reasons, use that
        reasons = scaling_decision.get('reasons', [])
        
        for reason in reasons:
            if 'cpu' in reason.lower():
                return ScalingTriggerType.CPU_UTILIZATION
            elif 'memory' in reason.lower():
                return ScalingTriggerType.MEMORY_UTILIZATION
            elif 'request' in reason.lower():
                return ScalingTriggerType.REQUEST_RATE
            elif 'queue' in reason.lower():
                return ScalingTriggerType.QUEUE_LENGTH
            elif 'response' in reason.lower():
                return ScalingTriggerType.RESPONSE_TIME
            elif 'predicted' in reason.lower():
                return ScalingTriggerType.PREDICTIVE
        
        return ScalingTriggerType.CPU_UTILIZATION  # Default

    def _is_service_in_cooldown(self, service_name: str, policy: ScalingPolicy) -> bool:
        """Check if service is in scaling cooldown period"""
        
        if service_name not in self.last_scaling_times:
            return False
        
        last_scaling_time = self.last_scaling_times[service_name]
        time_since_last_scaling = (datetime.utcnow() - last_scaling_time).total_seconds()
        
        # Use appropriate cooldown period
        last_event = None
        for event in reversed(self.scaling_events):
            if event.service_name == service_name:
                last_event = event
                break
        
        if last_event and last_event.direction == ScalingDirection.UP:
            cooldown_period = policy.scale_up_cooldown
        else:
            cooldown_period = policy.scale_down_cooldown
        
        return time_since_last_scaling < cooldown_period

    def _exceeds_scaling_rate_limit(self, service_name: str) -> bool:
        """Check if service exceeds scaling rate limits"""
        
        # Count scaling events in the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        recent_events = [
            event for event in self.scaling_events
            if event.service_name == service_name and event.timestamp > one_hour_ago
        ]
        
        return len(recent_events) >= self.max_scaling_events_per_hour

    async def _update_resource_predictions(self, environment: str) -> None:
        """Update resource predictions for all services"""
        
        for service_name in self.scaling_policies.keys():
            try:
                # Get historical metrics
                historical_data = self._get_historical_metrics(service_name)
                
                if len(historical_data) < 10:  # Need minimum data for prediction
                    continue
                
                # Generate prediction
                prediction = await self.prediction_engine.predict_resource_usage(
                    service_name=service_name,
                    historical_data=historical_data,
                    prediction_horizon_minutes=self.prediction_horizon_minutes
                )
                
                if prediction:
                    # Calculate recommended replicas based on prediction
                    current_replicas = await self.deployment_manager.get_replica_count(
                        service_name, f"ia-influencer-{environment}"
                    )
                    
                    recommended_replicas = self._calculate_recommended_replicas(
                        service_name, prediction, current_replicas
                    )
                    
                    resource_prediction = ResourcePrediction(
                        service_name=service_name,
                        predicted_load=prediction['predicted_load'],
                        confidence=prediction['confidence'],
                        time_horizon=self.prediction_horizon_minutes,
                        recommended_replicas=recommended_replicas,
                        prediction_timestamp=datetime.utcnow(),
                        factors=prediction.get('factors', {})
                    )
                    
                    self.resource_predictions[service_name] = resource_prediction
                
            except Exception as e:
                self.logger.error(f"Error updating prediction for {service_name}: {str(e)}")

    def _get_historical_metrics(self, service_name: str) -> List[Dict[str, Any]]:
        """Get historical metrics for a service"""
        
        if service_name not in self.metric_history:
            return []
        
        return list(self.metric_history[service_name])

    def _calculate_recommended_replicas(
        self,
        service_name: str,
        prediction: Dict[str, Any],
        current_replicas: int
    ) -> int:
        """Calculate recommended replicas based on prediction"""
        
        predicted_load = prediction['predicted_load']
        
        # Simple scaling factor calculation
        # This could be more sophisticated based on service characteristics
        
        service_config = self.ia_services.get(service_name, {})
        
        # Base load capacity per replica (adjust based on service type)
        if service_config.get('cpu_intensive', False):
            base_capacity = 0.7  # 70% load per replica for CPU-intensive services
        elif service_config.get('memory_intensive', False):
            base_capacity = 0.8  # 80% load per replica for memory-intensive services
        else:
            base_capacity = 0.85  # 85% load per replica for I/O-intensive services
        
        # Calculate required replicas
        required_replicas = math.ceil(predicted_load / base_capacity)
        
        # Apply conservative scaling (don't change too dramatically)
        max_change = max(1, current_replicas // 2)  # Change by at most 50%
        
        if required_replicas > current_replicas:
            recommended_replicas = min(required_replicas, current_replicas + max_change)
        elif required_replicas < current_replicas:
            recommended_replicas = max(required_replicas, current_replicas - max_change)
        else:
            recommended_replicas = current_replicas
        
        return recommended_replicas

    async def _collect_scaling_metrics(self, environment: str) -> None:
        """Collect metrics for all services"""
        
        namespace = f"ia-influencer-{environment}"
        
        for service_name in self.scaling_policies.keys():
            try:
                metrics = await self._get_current_service_metrics(service_name, namespace)
                # Metrics are stored in the _get_current_service_metrics method
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics for {service_name}: {str(e)}")

    async def update_scaling_policy(self, service_name: str, policy: ScalingPolicy) -> None:
        """Update scaling policy for a service"""
        
        self.scaling_policies[service_name] = policy
        self.logger.info(f"Updated scaling policy for {service_name}")

    async def get_scaling_status(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get current scaling status"""
        
        if service_name:
            services = [service_name] if service_name in self.scaling_policies else []
        else:
            services = list(self.scaling_policies.keys())
        
        status = {
            'enabled': self.scaling_enabled,
            'services': {},
            'recent_events': []
        }
        
        for svc in services:
            policy = self.scaling_policies[svc]
            
            # Get recent metrics
            recent_metrics = {}
            if svc in self.metric_history and self.metric_history[svc]:
                recent_metrics = self.metric_history[svc][-1]['metrics']
            
            # Get prediction
            prediction = self.resource_predictions.get(svc)
            
            status['services'][svc] = {
                'policy': {
                    'min_replicas': policy.min_replicas,
                    'max_replicas': policy.max_replicas,
                    'strategy': policy.strategy.value,
                    'enabled': policy.enabled
                },
                'current_metrics': recent_metrics,
                'prediction': {
                    'predicted_load': prediction.predicted_load if prediction else None,
                    'confidence': prediction.confidence if prediction else None,
                    'recommended_replicas': prediction.recommended_replicas if prediction else None
                } if prediction else None,
                'in_cooldown': self._is_service_in_cooldown(svc, policy)
            }
        
        # Get recent events (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_events = [
            {
                'event_id': event.event_id,
                'service_name': event.service_name,
                'timestamp': event.timestamp,
                'direction': event.direction.value,
                'from_replicas': event.from_replicas,
                'to_replicas': event.to_replicas,
                'success': event.success,
                'reason': event.reason
            }
            for event in self.scaling_events
            if event.timestamp > cutoff_time
        ]
        
        status['recent_events'] = sorted(recent_events, key=lambda x: x['timestamp'], reverse=True)
        
        return status

    async def get_scaling_metrics_history(
        self,
        service_name: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get scaling metrics history for a service"""
        
        if service_name not in self.metric_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            entry for entry in self.metric_history[service_name]
            if entry['timestamp'] > cutoff_time
        ]

    async def enable_scaling(self, service_name: Optional[str] = None) -> None:
        """Enable scaling for a service or globally"""
        
        if service_name:
            if service_name in self.scaling_policies:
                self.scaling_policies[service_name].enabled = True
                self.logger.info(f"Enabled scaling for {service_name}")
        else:
            self.scaling_enabled = True
            self.logger.info("Enabled global scaling")

    async def disable_scaling(self, service_name: Optional[str] = None) -> None:
        """Disable scaling for a service or globally"""
        
        if service_name:
            if service_name in self.scaling_policies:
                self.scaling_policies[service_name].enabled = False
                self.logger.info(f"Disabled scaling for {service_name}")
        else:
            self.scaling_enabled = False
            self.logger.info("Disabled global scaling")

    async def manual_scale(
        self,
        service_name: str,
        target_replicas: int,
        environment: str,
        reason: str = "Manual scaling"
    ) -> Dict[str, Any]:
        """Manually scale a service"""
        
        namespace = f"ia-influencer-{environment}"
        
        current_replicas = await self.deployment_manager.get_replica_count(
            service_name, namespace
        )
        
        if service_name in self.scaling_policies:
            policy = self.scaling_policies[service_name]
            target_replicas = max(
                policy.min_replicas,
                min(policy.max_replicas, target_replicas)
            )
        
        # Create manual scaling decision
        scaling_decision = {
            'action': ScalingDirection.UP if target_replicas > current_replicas else 
                     ScalingDirection.DOWN if target_replicas < current_replicas else 
                     ScalingDirection.MAINTAIN,
            'target_replicas': target_replicas,
            'confidence': 1.0,
            'reasons': [reason],
            'strategy_used': ScalingStrategy.REACTIVE,
            'trigger_metrics': {}
        }
        
        if scaling_decision['action'] != ScalingDirection.MAINTAIN:
            await self._execute_scaling_action(
                service_name, scaling_decision, namespace, environment
            )
        
        return {
            'service_name': service_name,
            'from_replicas': current_replicas,
            'to_replicas': target_replicas,
            'action': scaling_decision['action'].value,
            'reason': reason
        }
