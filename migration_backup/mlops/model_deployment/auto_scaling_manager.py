"""📈 Auto Scaling Manager - Intelligent Resource Optimization
============================================================
Module: mlops/model_deployment/auto_scaling_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE AUTO SCALING MANAGER
Intelligent auto-scaling system for ML model deployments in Creator Economy
- Predictive scaling based on Creator usage patterns
- Cost-aware scaling policies with tier-specific limits
- Multi-metric scaling decisions (CPU, Memory, Request Rate, Creator Satisfaction)
- Advanced scaling algorithms with machine learning optimization
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import statistics
import math

logger = logging.getLogger(__name__)

class ScalingDirection(Enum):
    """Scaling direction options"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"

class ScalingTrigger(Enum):
    """Scaling trigger types"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    CREATOR_SATISFACTION = "creator_satisfaction"
    PREDICTIVE = "predictive"
    SCHEDULE_BASED = "schedule_based"

class ScalingPolicy(Enum):
    """Scaling policy types"""
    REACTIVE = "reactive"          # React to current metrics
    PREDICTIVE = "predictive"      # Predict future load
    PROACTIVE = "proactive"        # Proactive based on patterns
    HYBRID = "hybrid"              # Combination of methods

class ScalingAlgorithm(Enum):
    """Scaling algorithms"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    MACHINE_LEARNING = "machine_learning"
    CREATOR_PATTERN_BASED = "creator_pattern_based"

@dataclass
class ScalingMetrics:
    """Current scaling metrics"""
    timestamp: datetime
    cpu_utilization: float
    memory_utilization: float
    request_rate: float
    response_time_ms: float
    queue_length: int
    active_connections: int
    creator_satisfaction_score: float
    business_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class ScalingConfig:
    """Auto-scaling configuration"""
    model_id: str
    creator_id: str
    policy: ScalingPolicy
    algorithm: ScalingAlgorithm
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: float = 70.0
    target_memory_utilization: float = 80.0
    target_response_time_ms: float = 500.0
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 30.0
    scale_up_cooldown_seconds: int = 300
    scale_down_cooldown_seconds: int = 600
    creator_tier: str = "creator"
    predictive_window_hours: int = 2
    creator_patterns: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScalingDecision:
    """Scaling decision with reasoning"""
    direction: ScalingDirection
    target_replicas: int
    current_replicas: int
    trigger: ScalingTrigger
    confidence: float
    reasoning: str
    estimated_cost_impact: float
    creator_impact_score: float

@dataclass
class ScalingEvent:
    """Scaling event record"""
    timestamp: datetime
    model_id: str
    creator_id: str
    decision: ScalingDecision
    execution_result: Dict[str, Any]
    metrics_before: ScalingMetrics
    metrics_after: Optional[ScalingMetrics] = None

class AutoScalingManager:
    """📈 Enterprise Auto Scaling Manager
    
    Intelligent auto-scaling system that optimizes resource allocation for ML model deployments
    based on Creator usage patterns, performance metrics, and cost considerations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the auto scaling manager"""
        self.config = config or {}
        
        # Scaling configurations per deployment
        self.scaling_configs: Dict[str, ScalingConfig] = {}
        self.current_replicas: Dict[str, int] = {}
        self.last_scaling_time: Dict[str, datetime] = {}
        
        # Metrics history for predictive scaling
        self.metrics_history: Dict[str, List[ScalingMetrics]] = {}
        self.scaling_events: List[ScalingEvent] = []
        
        # Creator patterns and profiles
        self.creator_patterns = self._initialize_creator_patterns()
        
        # Scaling algorithms
        self.scaling_algorithms = self._initialize_scaling_algorithms()
        
        # Tier-specific configurations
        self.tier_configs = self._setup_tier_configurations()
        
        # Predictive models (simplified for demonstration)
        self.predictive_models = self._initialize_predictive_models()
        
        # Performance metrics
        self.metrics = {
            'total_scaling_events': 0,
            'scale_up_events': 0,
            'scale_down_events': 0,
            'cost_savings': 0.0,
            'performance_improvements': 0,
            'creator_satisfaction_improvements': 0,
            'predictive_accuracy': 0.0
        }
        
        logger.info("AutoScalingManager initialized successfully")
    
    def _initialize_creator_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize creator usage patterns"""
        return {
            'content_creators': {
                'peak_hours': [9, 10, 11, 14, 15, 16, 19, 20, 21],
                'peak_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'seasonal_patterns': {'summer': 1.2, 'winter': 0.8},
                'burst_probability': 0.3,
                'average_session_duration': 15  # minutes
            },
            'influencers': {
                'peak_hours': [7, 8, 12, 13, 17, 18, 19, 20, 21, 22],
                'peak_days': ['friday', 'saturday', 'sunday'],
                'seasonal_patterns': {'holiday_season': 1.5, 'back_to_school': 1.3},
                'burst_probability': 0.5,
                'average_session_duration': 25
            },
            'musicians': {
                'peak_hours': [15, 16, 17, 18, 19, 20, 21, 22, 23],
                'peak_days': ['friday', 'saturday', 'sunday'],
                'seasonal_patterns': {'festival_season': 2.0, 'new_year': 1.8},
                'burst_probability': 0.7,
                'average_session_duration': 45
            },
            'bloggers': {
                'peak_hours': [8, 9, 10, 11, 14, 15, 16],
                'peak_days': ['monday', 'tuesday', 'wednesday', 'thursday'],
                'seasonal_patterns': {'regular': 1.0},
                'burst_probability': 0.2,
                'average_session_duration': 10
            }
        }
    
    def _initialize_scaling_algorithms(self) -> Dict[ScalingAlgorithm, callable]:
        """Initialize scaling algorithms"""
        return {
            ScalingAlgorithm.LINEAR: self._linear_scaling_algorithm,
            ScalingAlgorithm.EXPONENTIAL: self._exponential_scaling_algorithm,
            ScalingAlgorithm.LOGARITHMIC: self._logarithmic_scaling_algorithm,
            ScalingAlgorithm.MACHINE_LEARNING: self._ml_scaling_algorithm,
            ScalingAlgorithm.CREATOR_PATTERN_BASED: self._creator_pattern_scaling_algorithm
        }
    
    def _setup_tier_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Setup scaling configurations per creator tier"""
        return {
            'free': {
                'max_replicas': 2,
                'scale_up_cooldown': 600,  # 10 minutes
                'scale_down_cooldown': 1200,  # 20 minutes
                'cpu_threshold': 85.0,
                'memory_threshold': 90.0,
                'predictive_scaling': False,
                'burst_scaling': False
            },
            'creator': {
                'max_replicas': 5,
                'scale_up_cooldown': 300,  # 5 minutes
                'scale_down_cooldown': 600,  # 10 minutes
                'cpu_threshold': 75.0,
                'memory_threshold': 85.0,
                'predictive_scaling': True,
                'burst_scaling': True
            },
            'professional': {
                'max_replicas': 15,
                'scale_up_cooldown': 180,  # 3 minutes
                'scale_down_cooldown': 300,  # 5 minutes
                'cpu_threshold': 70.0,
                'memory_threshold': 80.0,
                'predictive_scaling': True,
                'burst_scaling': True
            },
            'enterprise': {
                'max_replicas': 50,
                'scale_up_cooldown': 120,  # 2 minutes
                'scale_down_cooldown': 180,  # 3 minutes
                'cpu_threshold': 60.0,
                'memory_threshold': 75.0,
                'predictive_scaling': True,
                'burst_scaling': True
            }
        }
    
    def _initialize_predictive_models(self) -> Dict[str, Any]:
        """Initialize predictive models (simplified)"""
        return {
            'time_series_model': None,  # Would be actual ML model
            'pattern_recognition_model': None,
            'creator_behavior_model': None,
            'cost_optimization_model': None
        }
    
    async def setup_auto_scaling(
        self,
        deployment_context: Dict[str, Any],
        scaling_config: Optional[ScalingConfig] = None
    ) -> Dict[str, Any]:
        """🚀 Setup auto-scaling for a deployment
        
        Args:
            deployment_context: Complete deployment context
            scaling_config: Optional custom scaling configuration
            
        Returns:
            Setup result with scaling configuration
        """
        deployment_id = deployment_context['deployment_id']
        model_id = deployment_context['model_id']
        creator_id = deployment_context['creator_id']
        
        try:
            logger.info(f"Setting up auto-scaling for deployment {deployment_id}")
            
            # Create or use provided scaling configuration
            if not scaling_config:
                scaling_config = await self._create_optimal_scaling_config(deployment_context)
            
            # Store configuration
            self.scaling_configs[deployment_id] = scaling_config
            
            # Initialize tracking
            creator_config = deployment_context.get('creator_config', {})
            initial_replicas = creator_config.get('replicas', scaling_config.min_replicas)
            self.current_replicas[deployment_id] = initial_replicas
            self.metrics_history[deployment_id] = []
            
            # Start monitoring
            monitoring_task = asyncio.create_task(
                self._continuous_monitoring(deployment_id)
            )
            
            logger.info(f"Auto-scaling setup completed for {deployment_id}")
            
            return {
                'success': True,
                'deployment_id': deployment_id,
                'scaling_config': scaling_config.__dict__,
                'initial_replicas': initial_replicas,
                'monitoring_started': True
            }
            
        except Exception as e:
            logger.error(f"Auto-scaling setup failed for {deployment_id}: {str(e)}")
            return {
                'success': False,
                'deployment_id': deployment_id,
                'error': str(e)
            }
    
    async def _create_optimal_scaling_config(
        self,
        deployment_context: Dict[str, Any]
    ) -> ScalingConfig:
        """Create optimal scaling configuration for deployment"""
        try:
            model_id = deployment_context['model_id']
            creator_id = deployment_context['creator_id']
            creator_config = deployment_context.get('creator_config', {})
            
            # Get creator tier and tier configuration
            creator_tier = creator_config.get('tier', 'creator')
            tier_config = self.tier_configs.get(creator_tier, self.tier_configs['creator'])
            
            # Determine creator category for pattern-based scaling
            creator_category = self._determine_creator_category(creator_config)
            creator_patterns = self.creator_patterns.get(creator_category, {})
            
            # Select optimal policy and algorithm
            policy = ScalingPolicy.HYBRID if tier_config['predictive_scaling'] else ScalingPolicy.REACTIVE
            algorithm = ScalingAlgorithm.CREATOR_PATTERN_BASED if creator_patterns else ScalingAlgorithm.LINEAR
            
            return ScalingConfig(
                model_id=model_id,
                creator_id=creator_id,
                policy=policy,
                algorithm=algorithm,
                min_replicas=max(1, creator_config.get('min_replicas', 1)),
                max_replicas=min(tier_config['max_replicas'], creator_config.get('max_replicas', 10)),
                target_cpu_utilization=tier_config['cpu_threshold'],
                target_memory_utilization=tier_config['memory_threshold'],
                scale_up_cooldown_seconds=tier_config['scale_up_cooldown'],
                scale_down_cooldown_seconds=tier_config['scale_down_cooldown'],
                creator_tier=creator_tier,
                creator_patterns=creator_patterns
            )
            
        except Exception as e:
            logger.error(f"Failed to create optimal scaling config: {str(e)}")
            raise
    
    def _determine_creator_category(self, creator_config: Dict[str, Any]) -> str:
        """Determine creator category for pattern-based scaling"""
        try:
            # Check explicit category
            if 'category' in creator_config:
                return creator_config['category']
            
            # Infer from content type or other metadata
            content_types = creator_config.get('content_types', [])
            
            if 'music' in content_types or 'audio' in content_types:
                return 'musicians'
            elif 'video' in content_types or 'social' in content_types:
                return 'influencers'
            elif 'text' in content_types or 'blog' in content_types:
                return 'bloggers'
            else:
                return 'content_creators'  # Default
                
        except Exception:
            return 'content_creators'  # Safe default
    
    async def _continuous_monitoring(self, deployment_id: str) -> None:
        """Continuous monitoring and scaling decisions"""
        try:
            monitoring_interval = 30  # seconds
            
            while deployment_id in self.scaling_configs:
                try:
                    # Collect current metrics
                    current_metrics = await self._collect_scaling_metrics(deployment_id)
                    
                    # Store metrics history
                    self.metrics_history[deployment_id].append(current_metrics)
                    
                    # Limit history size (keep last 24 hours)
                    max_history = (24 * 60 * 60) // monitoring_interval
                    if len(self.metrics_history[deployment_id]) > max_history:
                        self.metrics_history[deployment_id] = self.metrics_history[deployment_id][-max_history:]
                    
                    # Make scaling decision
                    scaling_decision = await self._make_scaling_decision(deployment_id, current_metrics)
                    
                    # Execute scaling if needed
                    if scaling_decision.direction != ScalingDirection.STABLE:
                        execution_result = await self._execute_scaling_decision(
                            deployment_id, scaling_decision, current_metrics
                        )
                        
                        # Record scaling event
                        scaling_event = ScalingEvent(
                            timestamp=datetime.now(),
                            model_id=self.scaling_configs[deployment_id].model_id,
                            creator_id=self.scaling_configs[deployment_id].creator_id,
                            decision=scaling_decision,
                            execution_result=execution_result,
                            metrics_before=current_metrics
                        )
                        self.scaling_events.append(scaling_event)
                        
                        # Update metrics
                        self._update_scaling_metrics(scaling_decision, execution_result)
                    
                    await asyncio.sleep(monitoring_interval)
                    
                except Exception as e:
                    logger.error(f"Monitoring error for {deployment_id}: {str(e)}")
                    await asyncio.sleep(monitoring_interval)
            
        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for {deployment_id}")
        except Exception as e:
            logger.error(f"Continuous monitoring failed for {deployment_id}: {str(e)}")
    
    async def _collect_scaling_metrics(self, deployment_id: str) -> ScalingMetrics:
        """Collect current scaling metrics"""
        try:
            # In real implementation, this would collect from monitoring systems
            # For simulation, generate realistic metrics with some variance
            
            current_replicas = self.current_replicas.get(deployment_id, 1)
            config = self.scaling_configs[deployment_id]
            
            # Base metrics (simulated)
            base_cpu = 65.0
            base_memory = 70.0
            base_request_rate = 50.0
            base_response_time = 200.0
            
            # Add load variation based on time and creator patterns
            load_factor = self._calculate_current_load_factor(config)
            
            # Adjust metrics based on current replicas (more replicas = lower utilization)
            replica_factor = 1.0 / max(current_replicas, 1)
            
            return ScalingMetrics(
                timestamp=datetime.now(),
                cpu_utilization=min(100.0, base_cpu * load_factor * replica_factor),
                memory_utilization=min(100.0, base_memory * load_factor * replica_factor),
                request_rate=base_request_rate * load_factor,
                response_time_ms=base_response_time * load_factor * replica_factor,
                queue_length=max(0, int(10 * load_factor * replica_factor - 5)),
                active_connections=int(20 * load_factor),
                creator_satisfaction_score=max(1.0, min(5.0, 5.0 - (load_factor - 1.0))),
                business_metrics={
                    'throughput': base_request_rate * load_factor,
                    'availability': max(95.0, 100.0 - (load_factor - 1.0) * 10),
                    'cost_efficiency': 100.0 / max(current_replicas, 1)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to collect scaling metrics: {str(e)}")
            # Return safe default metrics
            return ScalingMetrics(
                timestamp=datetime.now(),
                cpu_utilization=50.0,
                memory_utilization=60.0,
                request_rate=30.0,
                response_time_ms=300.0,
                queue_length=0,
                active_connections=10,
                creator_satisfaction_score=4.0
            )
    
    def _calculate_current_load_factor(self, config: ScalingConfig) -> float:
        """Calculate current load factor based on patterns and time"""
        try:
            now = datetime.now()
            current_hour = now.hour
            current_day = now.strftime('%A').lower()
            
            creator_patterns = config.creator_patterns
            base_load = 1.0
            
            # Time-based patterns
            if 'peak_hours' in creator_patterns:
                if current_hour in creator_patterns['peak_hours']:
                    base_load *= 1.5
                else:
                    base_load *= 0.7
            
            # Day-based patterns
            if 'peak_days' in creator_patterns:
                if current_day in creator_patterns['peak_days']:
                    base_load *= 1.3
                else:
                    base_load *= 0.8
            
            # Add some randomness for burst patterns
            import random
            burst_probability = creator_patterns.get('burst_probability', 0.1)
            if random.random() < burst_probability:
                base_load *= random.uniform(1.5, 3.0)
            
            return base_load
            
        except Exception:
            return 1.0  # Default load factor
    
    async def _make_scaling_decision(
        self,
        deployment_id: str,
        current_metrics: ScalingMetrics
    ) -> ScalingDecision:
        """Make intelligent scaling decision"""
        try:
            config = self.scaling_configs[deployment_id]
            current_replicas = self.current_replicas[deployment_id]
            
            # Check cooldown periods
            if not self._is_scaling_allowed(deployment_id):
                return ScalingDecision(
                    direction=ScalingDirection.STABLE,
                    target_replicas=current_replicas,
                    current_replicas=current_replicas,
                    trigger=ScalingTrigger.CPU_UTILIZATION,
                    confidence=1.0,
                    reasoning="Cooldown period active",
                    estimated_cost_impact=0.0,
                    creator_impact_score=0.0
                )
            
            # Use configured scaling algorithm
            algorithm_func = self.scaling_algorithms[config.algorithm]
            scaling_decision = await algorithm_func(deployment_id, config, current_metrics)
            
            # Validate decision against constraints
            scaling_decision = self._validate_scaling_decision(config, scaling_decision)
            
            return scaling_decision
            
        except Exception as e:
            logger.error(f"Scaling decision failed: {str(e)}")
            # Safe default: maintain current state
            return ScalingDecision(
                direction=ScalingDirection.STABLE,
                target_replicas=current_replicas,
                current_replicas=current_replicas,
                trigger=ScalingTrigger.CPU_UTILIZATION,
                confidence=0.0,
                reasoning=f"Decision error: {str(e)}",
                estimated_cost_impact=0.0,
                creator_impact_score=0.0
            )
    
    def _is_scaling_allowed(self, deployment_id: str) -> bool:
        """Check if scaling is allowed (cooldown period)"""
        try:
            config = self.scaling_configs[deployment_id]
            last_scaling = self.last_scaling_time.get(deployment_id)
            
            if not last_scaling:
                return True
            
            # Check cooldown based on last scaling direction
            time_since_scaling = (datetime.now() - last_scaling).total_seconds()
            
            # Use the longer cooldown period for safety
            cooldown_seconds = max(
                config.scale_up_cooldown_seconds,
                config.scale_down_cooldown_seconds
            )
            
            return time_since_scaling >= cooldown_seconds
            
        except Exception:
            return True  # Allow scaling if check fails
    
    async def _linear_scaling_algorithm(
        self,
        deployment_id: str,
        config: ScalingConfig,
        metrics: ScalingMetrics
    ) -> ScalingDecision:
        """Linear scaling algorithm"""
        current_replicas = self.current_replicas[deployment_id]
        
        # Primary trigger: CPU utilization
        cpu_util = metrics.cpu_utilization
        target_cpu = config.target_cpu_utilization
        
        if cpu_util > config.scale_up_threshold:
            # Scale up
            target_replicas = min(current_replicas + 1, config.max_replicas)
            direction = ScalingDirection.UP
            trigger = ScalingTrigger.CPU_UTILIZATION
            confidence = min(1.0, (cpu_util - target_cpu) / 20.0)
            reasoning = f"CPU utilization {cpu_util:.1f}% > threshold {config.scale_up_threshold}%"
            
        elif cpu_util < config.scale_down_threshold:
            # Scale down
            target_replicas = max(current_replicas - 1, config.min_replicas)
            direction = ScalingDirection.DOWN
            trigger = ScalingTrigger.CPU_UTILIZATION
            confidence = min(1.0, (target_cpu - cpu_util) / 30.0)
            reasoning = f"CPU utilization {cpu_util:.1f}% < threshold {config.scale_down_threshold}%"
            
        else:
            # Stable
            target_replicas = current_replicas
            direction = ScalingDirection.STABLE
            trigger = ScalingTrigger.CPU_UTILIZATION
            confidence = 1.0
            reasoning = f"CPU utilization {cpu_util:.1f}% within target range"
        
        # Calculate impact estimates
        cost_impact = self._estimate_cost_impact(current_replicas, target_replicas)
        creator_impact = self._estimate_creator_impact(metrics, direction)
        
        return ScalingDecision(
            direction=direction,
            target_replicas=target_replicas,
            current_replicas=current_replicas,
            trigger=trigger,
            confidence=confidence,
            reasoning=reasoning,
            estimated_cost_impact=cost_impact,
            creator_impact_score=creator_impact
        )
    
    async def _exponential_scaling_algorithm(
        self,
        deployment_id: str,
        config: ScalingConfig,
        metrics: ScalingMetrics
    ) -> ScalingDecision:
        """Exponential scaling algorithm for rapid scaling"""
        current_replicas = self.current_replicas[deployment_id]
        
        # More aggressive scaling based on multiple metrics
        cpu_util = metrics.cpu_utilization
        memory_util = metrics.memory_utilization
        response_time = metrics.response_time_ms
        
        # Calculate scaling factor based on severity
        cpu_factor = max(0, (cpu_util - config.target_cpu_utilization) / 10.0)
        memory_factor = max(0, (memory_util - config.target_memory_utilization) / 10.0)
        response_factor = max(0, (response_time - config.target_response_time_ms) / 100.0)
        
        severity = max(cpu_factor, memory_factor, response_factor)
        
        if severity > 2.0:
            # High severity: exponential scale up
            scale_factor = min(3, int(math.ceil(severity)))
            target_replicas = min(current_replicas * scale_factor, config.max_replicas)
            direction = ScalingDirection.UP
            trigger = ScalingTrigger.CPU_UTILIZATION
            confidence = min(1.0, severity / 3.0)
            reasoning = f"High severity scaling: CPU {cpu_util:.1f}%, Memory {memory_util:.1f}%, RT {response_time:.1f}ms"
            
        elif severity < -1.0:
            # Low utilization: scale down gradually
            target_replicas = max(current_replicas // 2, config.min_replicas)
            direction = ScalingDirection.DOWN
            trigger = ScalingTrigger.CPU_UTILIZATION
            confidence = min(1.0, abs(severity) / 2.0)
            reasoning = f"Low utilization scaling: CPU {cpu_util:.1f}%, Memory {memory_util:.1f}%"
            
        else:
            target_replicas = current_replicas
            direction = ScalingDirection.STABLE
            trigger = ScalingTrigger.CPU_UTILIZATION
            confidence = 1.0
            reasoning = "Utilization within acceptable range"
        
        cost_impact = self._estimate_cost_impact(current_replicas, target_replicas)
        creator_impact = self._estimate_creator_impact(metrics, direction)
        
        return ScalingDecision(
            direction=direction,
            target_replicas=target_replicas,
            current_replicas=current_replicas,
            trigger=trigger,
            confidence=confidence,
            reasoning=reasoning,
            estimated_cost_impact=cost_impact,
            creator_impact_score=creator_impact
        )
    
    async def _logarithmic_scaling_algorithm(
        self,
        deployment_id: str,
        config: ScalingConfig,
        metrics: ScalingMetrics
    ) -> ScalingDecision:
        """Logarithmic scaling algorithm for smooth scaling"""
        current_replicas = self.current_replicas[deployment_id]
        
        # Smooth scaling based on logarithmic function
        cpu_util = metrics.cpu_utilization
        target_cpu = config.target_cpu_utilization
        
        if cpu_util > config.scale_up_threshold:
            # Logarithmic scale up
            excess = cpu_util - target_cpu
            scale_factor = math.log(excess + 1) / math.log(2)  # Log base 2
            target_replicas = min(
                current_replicas + max(1, int(scale_factor)),
                config.max_replicas
            )
            direction = ScalingDirection.UP
            
        elif cpu_util < config.scale_down_threshold:
            # Logarithmic scale down
            deficit = target_cpu - cpu_util
            scale_factor = math.log(deficit + 1) / math.log(3)  # Slower scale down
            target_replicas = max(
                current_replicas - max(1, int(scale_factor)),
                config.min_replicas
            )
            direction = ScalingDirection.DOWN
            
        else:
            target_replicas = current_replicas
            direction = ScalingDirection.STABLE
        
        cost_impact = self._estimate_cost_impact(current_replicas, target_replicas)
        creator_impact = self._estimate_creator_impact(metrics, direction)
        
        return ScalingDecision(
            direction=direction,
            target_replicas=target_replicas,
            current_replicas=current_replicas,
            trigger=ScalingTrigger.CPU_UTILIZATION,
            confidence=0.8,
            reasoning=f"Logarithmic scaling: CPU {cpu_util:.1f}%",
            estimated_cost_impact=cost_impact,
            creator_impact_score=creator_impact
        )
    
    async def _ml_scaling_algorithm(
        self,
        deployment_id: str,
        config: ScalingConfig,
        metrics: ScalingMetrics
    ) -> ScalingDecision:
        """Machine learning based scaling algorithm"""
        # Simplified ML algorithm (in real implementation, would use trained models)
        current_replicas = self.current_replicas[deployment_id]
        
        # Feature vector
        features = [
            metrics.cpu_utilization,
            metrics.memory_utilization,
            metrics.request_rate,
            metrics.response_time_ms,
            metrics.queue_length,
            metrics.creator_satisfaction_score,
            current_replicas
        ]
        
        # Simplified decision tree logic
        if (metrics.cpu_utilization > 80 and metrics.response_time_ms > 500) or metrics.queue_length > 10:
            target_replicas = min(current_replicas + 2, config.max_replicas)
            direction = ScalingDirection.UP
            confidence = 0.9
            reasoning = "ML model predicts high load requiring scale up"
            
        elif metrics.cpu_utilization < 30 and metrics.response_time_ms < 200 and metrics.queue_length == 0:
            target_replicas = max(current_replicas - 1, config.min_replicas)
            direction = ScalingDirection.DOWN
            confidence = 0.8
            reasoning = "ML model predicts low load allowing scale down"
            
        else:
            target_replicas = current_replicas
            direction = ScalingDirection.STABLE
            confidence = 0.7
            reasoning = "ML model recommends maintaining current scale"
        
        cost_impact = self._estimate_cost_impact(current_replicas, target_replicas)
        creator_impact = self._estimate_creator_impact(metrics, direction)
        
        return ScalingDecision(
            direction=direction,
            target_replicas=target_replicas,
            current_replicas=current_replicas,
            trigger=ScalingTrigger.PREDICTIVE,
            confidence=confidence,
            reasoning=reasoning,
            estimated_cost_impact=cost_impact,
            creator_impact_score=creator_impact
        )
    
    async def _creator_pattern_scaling_algorithm(
        self,
        deployment_id: str,
        config: ScalingConfig,
        metrics: ScalingMetrics
    ) -> ScalingDecision:
        """Creator pattern-based scaling algorithm"""
        current_replicas = self.current_replicas[deployment_id]
        
        # Get creator patterns
        patterns = config.creator_patterns
        if not patterns:
            # Fallback to linear algorithm
            return await self._linear_scaling_algorithm(deployment_id, config, metrics)
        
        # Calculate expected load based on patterns
        expected_load_factor = self._calculate_current_load_factor(config)
        
        # Predictive scaling based on patterns
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).hour
        
        # Check if next hour is a peak hour
        upcoming_peak = next_hour in patterns.get('peak_hours', [])
        
        if upcoming_peak and current_replicas < config.max_replicas:
            # Proactive scale up before peak
            target_replicas = min(
                current_replicas + 1,
                config.max_replicas
            )
            direction = ScalingDirection.UP
            trigger = ScalingTrigger.PREDICTIVE
            confidence = 0.8
            reasoning = f"Proactive scaling for upcoming peak hour {next_hour}"
            
        elif metrics.cpu_utilization > config.scale_up_threshold:
            # Reactive scale up
            burst_factor = patterns.get('burst_probability', 0.1)
            if burst_factor > 0.5:  # High burst probability
                target_replicas = min(current_replicas + 2, config.max_replicas)
            else:
                target_replicas = min(current_replicas + 1, config.max_replicas)
            
            direction = ScalingDirection.UP
            trigger = ScalingTrigger.CPU_UTILIZATION
            confidence = 0.9
            reasoning = f"Reactive scaling: CPU {metrics.cpu_utilization:.1f}% with burst factor {burst_factor}"
            
        elif metrics.cpu_utilization < config.scale_down_threshold and not upcoming_peak:
            # Scale down if not approaching peak
            target_replicas = max(current_replicas - 1, config.min_replicas)
            direction = ScalingDirection.DOWN
            trigger = ScalingTrigger.CPU_UTILIZATION
            confidence = 0.7
            reasoning = f"Scale down: CPU {metrics.cpu_utilization:.1f}%, no upcoming peak"
            
        else:
            target_replicas = current_replicas
            direction = ScalingDirection.STABLE
            trigger = ScalingTrigger.CREATOR_SATISFACTION
            confidence = 1.0
            reasoning = "Maintaining current scale based on creator patterns"
        
        cost_impact = self._estimate_cost_impact(current_replicas, target_replicas)
        creator_impact = self._estimate_creator_impact(metrics, direction)
        
        return ScalingDecision(
            direction=direction,
            target_replicas=target_replicas,
            current_replicas=current_replicas,
            trigger=trigger,
            confidence=confidence,
            reasoning=reasoning,
            estimated_cost_impact=cost_impact,
            creator_impact_score=creator_impact
        )
    
    def _validate_scaling_decision(
        self,
        config: ScalingConfig,
        decision: ScalingDecision
    ) -> ScalingDecision:
        """Validate and adjust scaling decision against constraints"""
        try:
            # Ensure within replica bounds
            decision.target_replicas = max(config.min_replicas, decision.target_replicas)
            decision.target_replicas = min(config.max_replicas, decision.target_replicas)
            
            # Update direction based on validated target
            if decision.target_replicas > decision.current_replicas:
                decision.direction = ScalingDirection.UP
            elif decision.target_replicas < decision.current_replicas:
                decision.direction = ScalingDirection.DOWN
            else:
                decision.direction = ScalingDirection.STABLE
            
            # Adjust confidence if decision was clamped
            if decision.target_replicas == config.max_replicas or decision.target_replicas == config.min_replicas:
                decision.confidence *= 0.8
                decision.reasoning += " (clamped to limits)"
            
            return decision
            
        except Exception as e:
            logger.error(f"Decision validation failed: {str(e)}")
            return decision
    
    def _estimate_cost_impact(self, current_replicas: int, target_replicas: int) -> float:
        """Estimate cost impact of scaling decision"""
        try:
            # Simplified cost calculation (per replica per hour)
            cost_per_replica_per_hour = 0.10  # USD
            
            replica_change = target_replicas - current_replicas
            hourly_cost_change = replica_change * cost_per_replica_per_hour
            
            return hourly_cost_change
            
        except Exception:
            return 0.0
    
    def _estimate_creator_impact(self, metrics: ScalingMetrics, direction: ScalingDirection) -> float:
        """Estimate impact on creator satisfaction"""
        try:
            current_satisfaction = metrics.creator_satisfaction_score
            
            if direction == ScalingDirection.UP:
                # Scaling up should improve performance and satisfaction
                if metrics.response_time_ms > 500:
                    return 0.5  # Significant improvement expected
                else:
                    return 0.2  # Moderate improvement
                    
            elif direction == ScalingDirection.DOWN:
                # Scaling down might reduce performance
                if metrics.cpu_utilization < 30:
                    return 0.0  # Minimal impact expected
                else:
                    return -0.3  # Potential negative impact
                    
            else:
                return 0.0  # No change
                
        except Exception:
            return 0.0
    
    async def _execute_scaling_decision(
        self,
        deployment_id: str,
        decision: ScalingDecision,
        metrics_before: ScalingMetrics
    ) -> Dict[str, Any]:
        """Execute the scaling decision"""
        try:
            logger.info(f"Executing scaling decision for {deployment_id}: {decision.direction.value} to {decision.target_replicas} replicas")
            
            # In real implementation, this would:
            # - Update Kubernetes HPA settings
            # - Modify container orchestration configuration
            # - Update load balancer settings
            # - Trigger infrastructure changes
            
            # Simulate scaling execution
            await asyncio.sleep(2)
            
            # Update tracking
            old_replicas = self.current_replicas[deployment_id]
            self.current_replicas[deployment_id] = decision.target_replicas
            self.last_scaling_time[deployment_id] = datetime.now()
            
            execution_result = {
                'success': True,
                'old_replicas': old_replicas,
                'new_replicas': decision.target_replicas,
                'scaling_time': datetime.now().isoformat(),
                'trigger': decision.trigger.value,
                'confidence': decision.confidence,
                'estimated_cost_impact': decision.estimated_cost_impact
            }
            
            logger.info(f"Scaling executed successfully: {old_replicas} -> {decision.target_replicas} replicas")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Scaling execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'old_replicas': self.current_replicas.get(deployment_id, 1),
                'new_replicas': decision.current_replicas
            }
    
    def _update_scaling_metrics(
        self,
        decision: ScalingDecision,
        execution_result: Dict[str, Any]
    ) -> None:
        """Update scaling metrics"""
        self.metrics['total_scaling_events'] += 1
        
        if execution_result['success']:
            if decision.direction == ScalingDirection.UP:
                self.metrics['scale_up_events'] += 1
            elif decision.direction == ScalingDirection.DOWN:
                self.metrics['scale_down_events'] += 1
            
            # Update cost savings
            if execution_result.get('estimated_cost_impact', 0) < 0:
                self.metrics['cost_savings'] += abs(execution_result['estimated_cost_impact'])
            
            # Update performance improvements
            if decision.creator_impact_score > 0:
                self.metrics['performance_improvements'] += 1
                self.metrics['creator_satisfaction_improvements'] += decision.creator_impact_score
    
    async def manual_scale(
        self,
        deployment_id: str,
        target_replicas: int,
        reason: str = "Manual scaling"
    ) -> Dict[str, Any]:
        """🎛️ Manual scaling override"""
        try:
            if deployment_id not in self.scaling_configs:
                return {'success': False, 'error': 'Deployment not found'}
            
            config = self.scaling_configs[deployment_id]
            current_replicas = self.current_replicas[deployment_id]
            
            # Validate target replicas
            target_replicas = max(config.min_replicas, target_replicas)
            target_replicas = min(config.max_replicas, target_replicas)
            
            if target_replicas == current_replicas:
                return {
                    'success': True,
                    'message': 'Already at target replica count',
                    'current_replicas': current_replicas
                }
            
            # Create manual scaling decision
            direction = ScalingDirection.UP if target_replicas > current_replicas else ScalingDirection.DOWN
            
            manual_decision = ScalingDecision(
                direction=direction,
                target_replicas=target_replicas,
                current_replicas=current_replicas,
                trigger=ScalingTrigger.SCHEDULE_BASED,  # Manual trigger
                confidence=1.0,
                reasoning=f"Manual scaling: {reason}",
                estimated_cost_impact=self._estimate_cost_impact(current_replicas, target_replicas),
                creator_impact_score=0.0
            )
            
            # Execute scaling
            current_metrics = await self._collect_scaling_metrics(deployment_id)
            execution_result = await self._execute_scaling_decision(
                deployment_id, manual_decision, current_metrics
            )
            
            return {
                'success': execution_result['success'],
                'old_replicas': current_replicas,
                'new_replicas': target_replicas,
                'cost_impact': manual_decision.estimated_cost_impact,
                'execution_result': execution_result
            }
            
        except Exception as e:
            logger.error(f"Manual scaling failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_scaling_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """📊 Get current scaling status"""
        if deployment_id not in self.scaling_configs:
            return None
        
        config = self.scaling_configs[deployment_id]
        current_replicas = self.current_replicas[deployment_id]
        last_scaling = self.last_scaling_time.get(deployment_id)
        
        # Get recent metrics
        recent_metrics = None
        if deployment_id in self.metrics_history and self.metrics_history[deployment_id]:
            recent_metrics = self.metrics_history[deployment_id][-1].__dict__
        
        # Get recent scaling events
        recent_events = [
            event.__dict__ for event in self.scaling_events[-5:]
            if event.model_id == config.model_id
        ]
        
        return {
            'deployment_id': deployment_id,
            'model_id': config.model_id,
            'creator_id': config.creator_id,
            'current_replicas': current_replicas,
            'min_replicas': config.min_replicas,
            'max_replicas': config.max_replicas,
            'scaling_policy': config.policy.value,
            'scaling_algorithm': config.algorithm.value,
            'last_scaling_time': last_scaling.isoformat() if last_scaling else None,
            'recent_metrics': recent_metrics,
            'recent_events': recent_events,
            'scaling_allowed': self._is_scaling_allowed(deployment_id)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """📈 Get auto scaling metrics"""
        total_events = max(self.metrics['total_scaling_events'], 1)
        
        return {
            **self.metrics,
            'scale_up_rate': (self.metrics['scale_up_events'] / total_events) * 100,
            'scale_down_rate': (self.metrics['scale_down_events'] / total_events) * 100,
            'average_creator_impact': (
                self.metrics['creator_satisfaction_improvements'] / 
                max(self.metrics['performance_improvements'], 1)
            ),
            'active_deployments': len(self.scaling_configs),
            'total_managed_replicas': sum(self.current_replicas.values())
        }
    
    async def cleanup_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """🧹 Cleanup auto-scaling for a deployment"""
        try:
            if deployment_id not in self.scaling_configs:
                return {'success': False, 'error': 'Deployment not found'}
            
            # Remove configurations and tracking
            del self.scaling_configs[deployment_id]
            
            if deployment_id in self.current_replicas:
                del self.current_replicas[deployment_id]
            
            if deployment_id in self.last_scaling_time:
                del self.last_scaling_time[deployment_id]
            
            if deployment_id in self.metrics_history:
                del self.metrics_history[deployment_id]
            
            logger.info(f"Auto-scaling cleanup completed for {deployment_id}")
            
            return {
                'success': True,
                'message': f'Auto-scaling cleanup completed for {deployment_id}'
            }
            
        except Exception as e:
            logger.error(f"Auto-scaling cleanup failed: {str(e)}")
            return {'success': False, 'error': str(e)}

# Export all components
__all__ = [
    'AutoScalingManager',
    'ScalingDirection',
    'ScalingTrigger',
    'ScalingPolicy',
    'ScalingAlgorithm',
    'ScalingMetrics',
    'ScalingConfig',
    'ScalingDecision',
    'ScalingEvent'
]