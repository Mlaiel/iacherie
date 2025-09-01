"""Queue Performance Optimizer - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/queue_performance_optimizer.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Performance Optimization Engine - ML-Powered Queue Tuning
Responsibility: Autonomous performance optimization for crawler queue systems
Technologies: Machine Learning, Performance Analytics, Predictive Optimization
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Performance analysis → Bottleneck detection → ML optimization → Strategy adjustment →
Resource allocation → Predictive scaling → Performance validation → Continuous learning
"""

from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import numpy as np
from collections import defaultdict, deque
import time
import heapq
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """
Performance optimization strategies"""

    THROUGHPUT_MAXIMIZATION = "throughput_maximization"
    LATENCY_MINIMIZATION = "latency_minimization"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    BALANCED_PERFORMANCE = "balanced_performance"
    COST_OPTIMIZATION = "cost_optimization"
    ENERGY_EFFICIENCY = "energy_efficiency"


class OptimizationScope(Enum):
    """Optimization scope levels"""

    QUEUE_LEVEL = "queue_level"
    WORKER_LEVEL = "worker_level"
    SYSTEM_LEVEL = "system_level"
    PLATFORM_LEVEL = "platform_level"
    GLOBAL_LEVEL = "global_level"


class OptimizationTechnique(Enum):
    """Available optimization techniques"""

    DYNAMIC_SCALING = "dynamic_scaling"
    LOAD_REBALANCING = "load_rebalancing"
    PRIORITY_ADJUSTMENT = "priority_adjustment"
    RESOURCE_REALLOCATION = "resource_reallocation"
    CACHING_OPTIMIZATION = "caching_optimization"
    BATCHING_OPTIMIZATION = "batching_optimization"
    ROUTING_OPTIMIZATION = "routing_optimization"
    PREDICTIVE_PREALLOCATION = "predictive_preallocation"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_name: str
    current_value: float
    target_value: float
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    trend_direction: str = "stable"  # increasing, decreasing, stable, volatile
    importance_weight: float = 1.0
    measurement_timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationOpportunity:
    """Optimization opportunity identification"""
    opportunity_id: str
    scope: OptimizationScope
    technique: OptimizationTechnique
    potential_improvement: float
    confidence_score: float
    estimated_impact: Dict[str, float]
    implementation_complexity: str  # low, medium, high
    resource_requirements: Dict[str, Union[int, float]]
    prerequisites: List[str]
    risks: List[str]
    recommended_timeline: timedelta
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationPlan:
    """
Comprehensive optimization plan"""
    plan_id: str
    strategy: OptimizationStrategy
    opportunities: List[OptimizationOpportunity]
    execution_phases: List[Dict[str, Any]]
    expected_outcomes: Dict[str, float]
    success_criteria: Dict[str, float]
    rollback_plan: Dict[str, Any]
    monitoring_requirements: List[str]
    estimated_duration: timedelta
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """
Optimization execution result"""
    result_id: str
    plan_id: str
    execution_status: str  # success, partial, failed
    implemented_techniques: List[OptimizationTechnique]
    performance_improvements: Dict[str, float]
    actual_vs_expected: Dict[str, Tuple[float, float]]
    side_effects: List[Dict[str, Any]]
    lessons_learned: List[str]
    recommendations: List[str]
    execution_duration: timedelta
    completed_at: datetime = field(default_factory=datetime.now)


class MLPerformancePredictor:
    """
Machine learning performance prediction engine"""
    
    def __init__(self):
        self.models = {}
        self.training_data = defaultdict(list)
        self.prediction_cache = {}
        self.model_accuracy = {}
        
    async def predict_performance_impact(
        self,
        optimization_technique: OptimizationTechnique,
        current_metrics: Dict[str, float],
        proposed_changes: Dict[str, Any]
    ) -> Dict[str, float]:
        """
Predict performance impact of optimization"""
        
        # Generate prediction key
        prediction_key = self._generate_prediction_key(
            optimization_technique, current_metrics, proposed_changes
        )
        
        # Check cache first
        if prediction_key in self.prediction_cache:
            cached_result = self.prediction_cache[prediction_key]
            if datetime.now() - cached_result['timestamp'] < timedelta(minutes=30):
                return cached_result['prediction']
        
        # Generate ML prediction
        prediction = await self._generate_ml_prediction(
            optimization_technique, current_metrics, proposed_changes
        )
        
        # Cache result
        self.prediction_cache[prediction_key] = {
            'prediction': prediction,
            'timestamp': datetime.now()
        }
        
        return prediction
    
    async def _generate_ml_prediction(
        self,
        technique: OptimizationTechnique,
        metrics: Dict[str, float],
        changes: Dict[str, Any]
    ) -> Dict[str, float]:
        """
Generate ML-based performance prediction"""
        
        # Feature engineering
        features = self._extract_features(metrics, changes)
        
        # Model selection based on technique
        model_key = f"{technique.value}_predictor"
        
        if model_key not in self.models:
            # Initialize model if not exists
            self.models[model_key] = await self._initialize_model(technique)
        
        # Generate prediction
        prediction = await self._predict_with_model(
            self.models[model_key], features
        )
        
        return prediction
    
    def _extract_features(
        self,
        metrics: Dict[str, float],
        changes: Dict[str, Any]
    ) -> np.ndarray:
        """Extract ML features from metrics and changes"""
        
        features = []
        
        # Current performance features
        features.extend([
            metrics.get('throughput', 0.0),
            metrics.get('latency', 0.0),
            metrics.get('error_rate', 0.0),
            metrics.get('resource_utilization', 0.0),
            metrics.get('queue_size', 0.0),
            metrics.get('worker_count', 0.0)
        ])
        
        # Change magnitude features
        features.extend([
            changes.get('scaling_factor', 1.0),
            changes.get('resource_adjustment', 0.0),
            changes.get('priority_adjustment', 0.0),
            len(changes.get('affected_components', []))
        ])
        
        # Time-based features
        now = datetime.now()
        features.extend([
            now.hour,
            now.weekday(),
            (now.timestamp() % 86400) / 86400  # Time of day normalized
        ])
        
        return np.array(features)
    
    async def _initialize_model(self, technique: OptimizationTechnique):
        """
Initialize ML model for specific optimization technique"""
        
        # Placeholder for actual ML model initialization
        # In production, this would load pre-trained models or initialize new ones
        return {
            'technique': technique,
            'model_type': 'gradient_boosting',
            'features_count': 13,
            'initialized_at': datetime.now()
        }
    
    async def _predict_with_model(
        self,
        model: Dict[str, Any],
        features: np.ndarray
    ) -> Dict[str, float]:
        """
Generate prediction using model"""
        
        # Placeholder for actual ML prediction
        # In production, this would use trained models
        
        base_improvement = np.random.uniform(0.05, 0.25)  # 5-25% improvement
        
        return {
            'throughput_improvement': base_improvement * np.random.uniform(0.8, 1.2),
            'latency_reduction': base_improvement * np.random.uniform(0.6, 1.0),
            'resource_efficiency': base_improvement * np.random.uniform(0.7, 1.1),
            'error_rate_reduction': base_improvement * np.random.uniform(0.5, 0.9),
            'confidence_score': np.random.uniform(0.7, 0.95)
        }
    
    def _generate_prediction_key(
        self,
        technique: OptimizationTechnique,
        metrics: Dict[str, float],
        changes: Dict[str, Any]
    ) -> str:
        """
Generate cache key for prediction"""
        
        key_data = {
            'technique': technique.value,
            'metrics_hash': hashlib.md5(
                json.dumps(metrics, sort_keys=True).encode()
            ).hexdigest()[:8],
            'changes_hash': hashlib.md5(
                json.dumps(changes, sort_keys=True, default=str).encode()
            ).hexdigest()[:8]
        }
        
        return f"pred_{key_data['technique']}_{key_data['metrics_hash']}_{key_data['changes_hash']}"


class QueuePerformanceOptimizer:
    """Enterprise-grade queue performance optimization engine"""
    
    def __init__(
        self,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED_PERFORMANCE,
        enable_ml_prediction: bool = True,
        optimization_interval_seconds: int = 300,
        max_concurrent_optimizations: int = 3
    ):
        self.optimization_strategy = optimization_strategy
        self.enable_ml_prediction = enable_ml_prediction
        self.optimization_interval = optimization_interval_seconds
        self.max_concurrent_optimizations = max_concurrent_optimizations
        
        # Performance tracking
        self.performance_history = defaultdict(deque)
        self.optimization_history = []
        self.active_optimizations = {}
        
        # ML components
        self.ml_predictor = MLPerformancePredictor() if enable_ml_prediction else None
        
        # Optimization state
        self.current_metrics = {}
        self.baseline_metrics = {}
        self.optimization_targets = {}
        
        # Control flags
        self.optimization_enabled = True
        self.continuous_optimization = False
        self.emergency_optimization_mode = False
        
        logger.info(f"QueuePerformanceOptimizer initialized with strategy: {optimization_strategy.value}")
    
    async def initialize(self, queue_manager=None, distribution_engine=None):
        """Initialize optimizer with system components"""
        
        self.queue_manager = queue_manager
        self.distribution_engine = distribution_engine
        
        # Collect baseline metrics
        await self._collect_baseline_metrics()
        
        # Set optimization targets
        await self._set_optimization_targets()
        
        logger.info("QueuePerformanceOptimizer initialized successfully")
        return True
    
    async def start_continuous_optimization(self):
        """Start continuous performance optimization"""
        
        if self.continuous_optimization:
            logger.warning("Continuous optimization already running")
            return
        
        self.continuous_optimization = True
        logger.info("Starting continuous performance optimization")
        
        # Start optimization loop
        asyncio.create_task(self._continuous_optimization_loop())
    
    async def stop_continuous_optimization(self):
        """Stop continuous performance optimization"""
        
        self.continuous_optimization = False
        logger.info("Stopping continuous performance optimization")
    
    async def analyze_performance_opportunities(
        self,
        include_ml_predictions: bool = True
    ) -> List[OptimizationOpportunity]:
        """Analyze current performance and identify optimization opportunities"""
        
        # Collect current performance metrics
        current_metrics = await self._collect_current_metrics()
        
        # Identify bottlenecks
        bottlenecks = await self._identify_bottlenecks(current_metrics)
        
        # Generate optimization opportunities
        opportunities = []
        
        for bottleneck in bottlenecks:
            opportunity = await self._generate_optimization_opportunity(
                bottleneck, current_metrics, include_ml_predictions
            )
            if opportunity:
                opportunities.append(opportunity)
        
        # Sort by potential impact
        opportunities.sort(
            key=lambda x: x.potential_improvement * x.confidence_score,
            reverse=True
        )
        
        logger.info(f"Identified {len(opportunities)} optimization opportunities")
        return opportunities
    
    async def create_optimization_plan(
        self,
        opportunities: List[OptimizationOpportunity],
        max_complexity: str = "medium",
        target_timeframe: timedelta = timedelta(hours=1)
    ) -> OptimizationPlan:
        """Create comprehensive optimization plan"""
        
        # Filter opportunities by complexity and timeframe
        suitable_opportunities = [
            opp for opp in opportunities
            if self._is_suitable_opportunity(opp, max_complexity, target_timeframe)
        ]
        
        # Create execution phases
        execution_phases = await self._create_execution_phases(suitable_opportunities)
        
        # Calculate expected outcomes
        expected_outcomes = await self._calculate_expected_outcomes(suitable_opportunities)
        
        # Define success criteria
        success_criteria = await self._define_success_criteria(expected_outcomes)
        
        # Create rollback plan
        rollback_plan = await self._create_rollback_plan(suitable_opportunities)
        
        plan = OptimizationPlan(
            plan_id=f"opt_plan_{uuid.uuid4().hex[:8]}",
            strategy=self.optimization_strategy,
            opportunities=suitable_opportunities,
            execution_phases=execution_phases,
            expected_outcomes=expected_outcomes,
            success_criteria=success_criteria,
            rollback_plan=rollback_plan,
            monitoring_requirements=self._get_monitoring_requirements(suitable_opportunities),
            estimated_duration=target_timeframe
        )
        
        logger.info(f"Created optimization plan {plan.plan_id} with {len(suitable_opportunities)} opportunities")
        return plan
    
    async def execute_optimization_plan(
        self,
        plan: OptimizationPlan,
        dry_run: bool = False
    ) -> OptimizationResult:
        """Execute optimization plan"""
        
        result_id = f"opt_result_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        if dry_run:
            logger.info(f"Executing optimization plan {plan.plan_id} in DRY RUN mode")
        else:
            logger.info(f"Executing optimization plan {plan.plan_id}")
        
        # Pre-execution snapshot
        pre_metrics = await self._collect_current_metrics()
        
        implemented_techniques = []
        performance_improvements = {}
        side_effects = []
        
        try:
            # Execute each phase
            for phase_idx, phase in enumerate(plan.execution_phases):
                logger.info(f"Executing phase {phase_idx + 1}/{len(plan.execution_phases)}: {phase['name']}")
                
                if not dry_run:
                    phase_result = await self._execute_optimization_phase(phase)
                    implemented_techniques.extend(phase_result.get('techniques', []))
                    side_effects.extend(phase_result.get('side_effects', []))
                
                # Wait between phases
                if phase.get('wait_after', 0) > 0:
                    await asyncio.sleep(phase['wait_after'])
            
            # Post-execution measurement
            if not dry_run:
                await asyncio.sleep(30)  # Allow metrics to stabilize
                post_metrics = await self._collect_current_metrics()
                performance_improvements = self._calculate_improvements(
                    pre_metrics, post_metrics
                )
            
            execution_status = "success" if not dry_run else "dry_run_success"
            
        except Exception as e:
            logger.error(f"Optimization execution failed: {e}")
            execution_status = "failed"
            
            # Attempt rollback if not dry run
            if not dry_run:
                await self._execute_rollback(plan.rollback_plan)
        
        # Create result
        result = OptimizationResult(
            result_id=result_id,
            plan_id=plan.plan_id,
            execution_status=execution_status,
            implemented_techniques=implemented_techniques,
            performance_improvements=performance_improvements,
            actual_vs_expected=self._compare_actual_vs_expected(
                performance_improvements, plan.expected_outcomes
            ),
            side_effects=side_effects,
            lessons_learned=self._extract_lessons_learned(plan, performance_improvements),
            recommendations=self._generate_future_recommendations(performance_improvements),
            execution_duration=datetime.now() - start_time
        )
        
        # Store result
        self.optimization_history.append(result)
        
        logger.info(f"Optimization execution completed: {execution_status}")
        return result
    
    async def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        
        current_metrics = await self._collect_current_metrics()
        
        return {
            'optimizer_status': {
                'optimization_enabled': self.optimization_enabled,
                'continuous_optimization': self.continuous_optimization,
                'emergency_mode': self.emergency_optimization_mode,
                'strategy': self.optimization_strategy.value,
                'active_optimizations': len(self.active_optimizations)
            },
            'performance_metrics': current_metrics,
            'baseline_comparison': self._compare_to_baseline(current_metrics),
            'optimization_history': {
                'total_optimizations': len(self.optimization_history),
                'recent_success_rate': self._calculate_recent_success_rate(),
                'average_improvement': self._calculate_average_improvement()
            },
            'recommendations': await self._get_immediate_recommendations()
        }
    
    # Private methods
    
    async def _continuous_optimization_loop(self):
        """
Continuous optimization loop"""
        
        while self.continuous_optimization:
            try:
                # Check if optimization is needed
                if await self._should_optimize():
                    opportunities = await self.analyze_performance_opportunities()
                    
                    if opportunities:
                        # Create and execute quick optimization plan
                        plan = await self.create_optimization_plan(
                            opportunities[:3],  # Top 3 opportunities
                            max_complexity="low",
                            target_timeframe=timedelta(minutes=10)
                        )
                        
                        await self.execute_optimization_plan(plan)
                
                # Wait for next optimization cycle
                await asyncio.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"Error in continuous optimization loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _collect_current_metrics(self) -> Dict[str, float]:
        """Collect current performance metrics"""
        
        metrics = {}
        
        try:
            # Queue manager metrics
            if self.queue_manager:
                queue_status = await self.queue_manager.get_queue_status()
                metrics.update({
                    'queue_size': queue_status.get('total_queued', 0),
                    'throughput': queue_status.get('throughput_per_minute', 0),
                    'average_wait_time': queue_status.get('average_wait_time', 0),
                    'error_rate': queue_status.get('error_rate', 0)
                })
            
            # Distribution engine metrics
            if self.distribution_engine:
                dist_metrics = await self.distribution_engine.get_distribution_metrics()
                metrics.update({
                    'resource_utilization': getattr(dist_metrics, 'resource_utilization_efficiency', 0),
                    'agent_efficiency': getattr(dist_metrics, 'agent_efficiency_score', 0),
                    'load_balance_score': getattr(dist_metrics, 'load_balance_score', 0)
                })
            
            # System metrics
            metrics.update({
                'timestamp': datetime.now().timestamp(),
                'worker_count': len(self.active_optimizations)
            })
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
        
        return metrics
    
    async def _collect_baseline_metrics(self):
        """Collect baseline performance metrics"""
        
        self.baseline_metrics = await self._collect_current_metrics()
        logger.info(f"Baseline metrics collected: {len(self.baseline_metrics)} metrics")
    
    async def _set_optimization_targets(self):
        """Set optimization targets based on strategy"""
        
        if self.optimization_strategy == OptimizationStrategy.THROUGHPUT_MAXIMIZATION:
            self.optimization_targets = {
                'throughput_improvement': 0.20,  # 20% improvement
                'latency_tolerance': 0.10,       # 10% latency increase acceptable
                'resource_efficiency': 0.05     # 5% efficiency improvement
            }
        elif self.optimization_strategy == OptimizationStrategy.LATENCY_MINIMIZATION:
            self.optimization_targets = {
                'latency_reduction': 0.30,       # 30% latency reduction
                'throughput_tolerance': -0.05,   # 5% throughput decrease acceptable
                'resource_efficiency': 0.10     # 10% efficiency improvement
            }
        else:  # BALANCED_PERFORMANCE
            self.optimization_targets = {
                'throughput_improvement': 0.10,  # 10% improvement
                'latency_reduction': 0.15,       # 15% reduction
                'resource_efficiency': 0.15     # 15% efficiency improvement
            }
    
    async def _identify_bottlenecks(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """
Identify performance bottlenecks"""
        
        bottlenecks = []
        
        # Queue size bottleneck
        if metrics.get('queue_size', 0) > 1000:
            bottlenecks.append({
                'type': 'queue_overflow',
                'severity': 'high',
                'metric': 'queue_size',
                'current_value': metrics['queue_size'],
                'threshold': 1000
            })
        
        # Throughput bottleneck
        if metrics.get('throughput', 0) < 100:
            bottlenecks.append({
                'type': 'low_throughput',
                'severity': 'medium',
                'metric': 'throughput',
                'current_value': metrics['throughput'],
                'threshold': 100
            })
        
        # Error rate bottleneck
        if metrics.get('error_rate', 0) > 0.05:
            bottlenecks.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'metric': 'error_rate',
                'current_value': metrics['error_rate'],
                'threshold': 0.05
            })
        
        # Resource utilization bottleneck
        if metrics.get('resource_utilization', 0) < 0.60:
            bottlenecks.append({
                'type': 'low_resource_utilization',
                'severity': 'medium',
                'metric': 'resource_utilization',
                'current_value': metrics['resource_utilization'],
                'threshold': 0.60
            })
        
        return bottlenecks
    
    async def _generate_optimization_opportunity(
        self,
        bottleneck: Dict[str, Any],
        metrics: Dict[str, float],
        include_ml_predictions: bool
    ) -> Optional[OptimizationOpportunity]:
        """
Generate optimization opportunity from bottleneck"""
        
        bottleneck_type = bottleneck['type']
        
        # Map bottleneck types to optimization techniques
        technique_mapping = {
            'queue_overflow': OptimizationTechnique.DYNAMIC_SCALING,
            'low_throughput': OptimizationTechnique.LOAD_REBALANCING,
            'high_error_rate': OptimizationTechnique.ROUTING_OPTIMIZATION,
            'low_resource_utilization': OptimizationTechnique.RESOURCE_REALLOCATION
        }
        
        technique = technique_mapping.get(bottleneck_type)
        if not technique:
            return None
        
        # Calculate potential improvement
        potential_improvement = self._calculate_potential_improvement(bottleneck)
        
        # Get ML prediction if enabled
        confidence_score = 0.7  # Default confidence
        estimated_impact = {'default': potential_improvement}
        
        if include_ml_predictions and self.ml_predictor:
            try:
                ml_prediction = await self.ml_predictor.predict_performance_impact(
                    technique, metrics, {'bottleneck': bottleneck}
                )
                confidence_score = ml_prediction.get('confidence_score', 0.7)
                estimated_impact = ml_prediction
            except Exception as e:
                logger.error(f"ML prediction failed: {e}")
        
        return OptimizationOpportunity(
            opportunity_id=f"opp_{uuid.uuid4().hex[:8]}",
            scope=OptimizationScope.QUEUE_LEVEL,
            technique=technique,
            potential_improvement=potential_improvement,
            confidence_score=confidence_score,
            estimated_impact=estimated_impact,
            implementation_complexity="medium",
            resource_requirements={'cpu': 10, 'memory': 100, 'time': 300},
            prerequisites=[],
            risks=['temporary_performance_impact'],
            recommended_timeline=timedelta(minutes=15)
        )
    
    def _calculate_potential_improvement(self, bottleneck: Dict[str, Any]) -> float:
        """Calculate potential improvement percentage"""
        
        current = bottleneck['current_value']
        threshold = bottleneck['threshold']
        
        if bottleneck['type'] in ['queue_overflow', 'high_error_rate']:
            # For negative metrics, improvement is reduction
            return min(0.5, abs(current - threshold) / current)
        else:
            # For positive metrics, improvement is increase
            return min(0.3, abs(threshold - current) / threshold)
    
    def _is_suitable_opportunity(
        self,
        opportunity: OptimizationOpportunity,
        max_complexity: str,
        target_timeframe: timedelta
    ) -> bool:
        """
Check if opportunity is suitable for current constraints"""
        
        # Complexity check
        complexity_order = ['low', 'medium', 'high']
        if complexity_order.index(opportunity.implementation_complexity) > complexity_order.index(max_complexity):
            return False
        
        # Timeframe check
        if opportunity.recommended_timeline > target_timeframe:
            return False
        
        return True
    
    async def _create_execution_phases(
        self,
        opportunities: List[OptimizationOpportunity]
    ) -> List[Dict[str, Any]]:
        """
Create execution phases for opportunities"""
        
        phases = []
        
        # Group opportunities by technique
        technique_groups = defaultdict(list)
        for opp in opportunities:
            technique_groups[opp.technique].append(opp)
        
        # Create phases
        for technique, ops in technique_groups.items():
            phase = {
                'name': f"{technique.value}_optimization",
                'technique': technique,
                'opportunities': ops,
                'estimated_duration': max(op.recommended_timeline for op in ops),
                'wait_after': 30,  # Wait 30 seconds after phase
                'validation_required': True
            }
            phases.append(phase)
        
        return phases
    
    async def _calculate_expected_outcomes(
        self,
        opportunities: List[OptimizationOpportunity]
    ) -> Dict[str, float]:
        """Calculate expected outcomes from opportunities"""
        
        outcomes = defaultdict(float)
        
        for opp in opportunities:
            for metric, improvement in opp.estimated_impact.items():
                if isinstance(improvement, (int, float)):
                    outcomes[metric] += improvement * opp.confidence_score
        
        return dict(outcomes)
    
    async def _define_success_criteria(
        self,
        expected_outcomes: Dict[str, float]
    ) -> Dict[str, float]:
        """
Define success criteria based on expected outcomes"""
        
        # Success criteria is typically 70% of expected outcomes
        return {
            metric: improvement * 0.7
            for metric, improvement in expected_outcomes.items()
        }
    
    async def _create_rollback_plan(
        self,
        opportunities: List[OptimizationOpportunity]
    ) -> Dict[str, Any]:
        """
Create rollback plan for optimization"""
        
        return {
            'rollback_enabled': True,
            'rollback_triggers': [
                'performance_degradation',
                'error_rate_increase',
                'system_instability'
            ],
            'rollback_actions': [
                'restore_original_configuration',
                'revert_scaling_changes',
                'reset_priority_settings'
            ],
            'rollback_timeout': 300  # 5 minutes
        }
    
    def _get_monitoring_requirements(
        self,
        opportunities: List[OptimizationOpportunity]
    ) -> List[str]:
        """
Get monitoring requirements for optimization"""
        
        requirements = set(['throughput', 'latency', 'error_rate'])
        
        for opp in opportunities:
            if opp.technique == OptimizationTechnique.DYNAMIC_SCALING:
                requirements.update(['worker_count', 'resource_utilization'])
            elif opp.technique == OptimizationTechnique.LOAD_REBALANCING:
                requirements.update(['load_distribution', 'queue_sizes'])
        
        return list(requirements)
    
    async def _execute_optimization_phase(self, phase: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute single optimization phase"""
        
        technique = phase['technique']
        opportunities = phase['opportunities']
        
        result = {
            'techniques': [technique],
            'side_effects': []
        }
        
        logger.info(f"Executing {technique.value} optimization")
        
        # Execute technique-specific optimization
        if technique == OptimizationTechnique.DYNAMIC_SCALING:
            await self._execute_dynamic_scaling(opportunities)
        elif technique == OptimizationTechnique.LOAD_REBALANCING:
            await self._execute_load_rebalancing(opportunities)
        elif technique == OptimizationTechnique.RESOURCE_REALLOCATION:
            await self._execute_resource_reallocation(opportunities)
        elif technique == OptimizationTechnique.ROUTING_OPTIMIZATION:
            await self._execute_routing_optimization(opportunities)
        
        return result
    
    async def _execute_dynamic_scaling(self, opportunities: List[OptimizationOpportunity]):
        """Execute dynamic scaling optimization"""
        logger.info("Executing dynamic scaling optimization")
        # Implementation placeholder
        
    async def _execute_load_rebalancing(self, opportunities: List[OptimizationOpportunity]):
        """Execute load rebalancing optimization"""
        logger.info("Executing load rebalancing optimization")
        # Implementation placeholder
        
    async def _execute_resource_reallocation(self, opportunities: List[OptimizationOpportunity]):
        """Execute resource reallocation optimization"""
        logger.info("Executing resource reallocation optimization")
        # Implementation placeholder
        
    async def _execute_routing_optimization(self, opportunities: List[OptimizationOpportunity]):
        """Execute routing optimization"""
        logger.info("Executing routing optimization")
        # Implementation placeholder
    
    def _calculate_improvements(
        self,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate performance improvements"""
        
        improvements = {}
        
        for metric in pre_metrics:
            if metric in post_metrics and metric != 'timestamp':
                pre_value = pre_metrics[metric]
                post_value = post_metrics[metric]
                
                if pre_value > 0:
                    improvement = (post_value - pre_value) / pre_value
                    improvements[metric] = improvement
        
        return improvements
    
    def _compare_actual_vs_expected(
        self,
        actual: Dict[str, float],
        expected: Dict[str, float]
    ) -> Dict[str, Tuple[float, float]]:
        """
Compare actual vs expected improvements"""
        
        comparison = {}
        
        for metric in expected:
            actual_value = actual.get(metric, 0.0)
            expected_value = expected[metric]
            comparison[metric] = (actual_value, expected_value)
        
        return comparison
    
    def _extract_lessons_learned(
        self,
        plan: OptimizationPlan,
        improvements: Dict[str, float]
    ) -> List[str]:
        """
Extract lessons learned from optimization"""
        
        lessons = []
        
        # Analyze improvement vs expectations
        for metric, improvement in improvements.items():
            expected = plan.expected_outcomes.get(metric, 0)
            if improvement > expected * 1.2:
                lessons.append(f"{metric} exceeded expectations by {((improvement/expected)-1)*100:.1f}%")
            elif improvement < expected * 0.5:
                lessons.append(f"{metric} underperformed expectations by {((expected/improvement)-1)*100:.1f}%")
        
        return lessons
    
    def _generate_future_recommendations(
        self,
        improvements: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for future optimizations"""
        
        recommendations = []
        
        # Analyze which optimizations worked best
        best_improvements = sorted(
            [(metric, improvement) for metric, improvement in improvements.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        if best_improvements:
            best_metric, best_improvement = best_improvements[0]
            recommendations.append(
                f"Focus on {best_metric} optimizations as they showed {best_improvement*100:.1f}% improvement"
            )
        
        return recommendations
    
    def _compare_to_baseline(self, current_metrics: Dict[str, float]) -> Dict[str, float]:
        """Compare current metrics to baseline"""
        
        comparison = {}
        
        for metric in self.baseline_metrics:
            if metric in current_metrics and metric != 'timestamp':
                baseline = self.baseline_metrics[metric]
                current = current_metrics[metric]
                
                if baseline > 0:
                    change = (current - baseline) / baseline
                    comparison[metric] = change
        
        return comparison
    
    def _calculate_recent_success_rate(self) -> float:
        """
Calculate recent optimization success rate"""
        
        recent_results = self.optimization_history[-10:]  # Last 10 optimizations
        if not recent_results:
            return 0.0
        
        successes = sum(1 for result in recent_results if result.execution_status == 'success')
        return successes / len(recent_results)
    
    def _calculate_average_improvement(self) -> float:
        """
Calculate average improvement from optimizations"""
        
        recent_results = self.optimization_history[-10:]
        if not recent_results:
            return 0.0
        
        total_improvement = 0.0
        count = 0
        
        for result in recent_results:
            for improvement in result.performance_improvements.values():
                if isinstance(improvement, (int, float)):
                    total_improvement += improvement
                    count += 1
        
        return total_improvement / count if count > 0 else 0.0
    
    async def _get_immediate_recommendations(self) -> List[str]:
        """
Get immediate optimization recommendations"""
        
        recommendations = []
        current_metrics = await self._collect_current_metrics()
        
        # Check for immediate concerns
        if current_metrics.get('error_rate', 0) > 0.1:
            recommendations.append("High error rate detected - consider routing optimization")
        
        if current_metrics.get('queue_size', 0) > 5000:
            recommendations.append("Queue overflow risk - consider dynamic scaling")
        
        if current_metrics.get('throughput', 0) < 50:
            recommendations.append("Low throughput detected - consider load rebalancing")
        
        return recommendations
    
    async def _should_optimize(self) -> bool:
        """Determine if optimization should be triggered"""
        
        current_metrics = await self._collect_current_metrics()
        
        # Check if any metric is significantly below target
        for metric, value in current_metrics.items():
            baseline_value = self.baseline_metrics.get(metric, 0)
            if baseline_value > 0:
                change = (value - baseline_value) / baseline_value
                if change < -0.2:  # 20% degradation
                    return True
        
        return False
    
    async def _execute_rollback(self, rollback_plan: Dict[str, Any]):
        """
Execute rollback plan"""
        
        logger.warning("Executing optimization rollback")
        
        # Placeholder for rollback implementation
        for action in rollback_plan.get('rollback_actions', []):
            logger.info(f"Executing rollback action: {action}")
            await asyncio.sleep(1)  # Simulate rollback action


# Factory function
def create_queue_performance_optimizer(
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED_PERFORMANCE,
    enable_ml_prediction: bool = True,
    optimization_interval_seconds: int = 300
) -> QueuePerformanceOptimizer:
    """Create queue performance optimizer instance"""
    
    return QueuePerformanceOptimizer(
        optimization_strategy=optimization_strategy,
        enable_ml_prediction=enable_ml_prediction,
        optimization_interval_seconds=optimization_interval_seconds
    )


# Export all classes and functions
__all__ = [
    'QueuePerformanceOptimizer',
    'MLPerformancePredictor',
    'OptimizationStrategy',
    'OptimizationScope',
    'OptimizationTechnique',
    'PerformanceMetric',
    'OptimizationOpportunity',
    'OptimizationPlan',
    'OptimizationResult',
    'create_queue_performance_optimizer'
]
