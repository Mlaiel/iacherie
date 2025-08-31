"""Experience Optimizer
===================

Industrial-grade experience optimization engine for IA Influencer Agent.
Optimizes user experience through A/B testing, multivariate testing, 
real-time adaptation, and continuous improvement algorithms.

Business Logic:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → AI rights protection → Professional SEO → Collaboration matching → Multi-platform distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

WARNING: Any attempt to steal, copy, or use the concept, idea, or code without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from scipy import stats
import json
from uuid import uuid4

from ..core.base_service import BaseService
from ..core.exceptions import ExperienceOptimizationError, ValidationError
from ..database.mongodb import MongoDBHandler
from ..cache.redis_cache import RedisCache
from ..ml.optimization_models import BayesianOptimizationModel, BanditModel
from ..analytics.metrics_calculator import MetricsCalculator
from ..analytics.experiment_analyzer import ExperimentAnalyzer

logger = logging.getLogger(__name__)


class ExperimentType(str, Enum):
    """Types of optimization experiments"""
    AB_TEST = "ab_test"
    MULTIVARIATE_TEST = "multivariate_test"
    BANDIT_OPTIMIZATION = "bandit_optimization"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    PERSONALIZED_EXPERIMENT = "personalized_experiment"
    REAL_TIME_ADAPTATION = "real_time_adaptation"


class OptimizationMetric(str, Enum):
    """Metrics for optimization"""
    ENGAGEMENT_RATE = "engagement_rate"
    CONVERSION_RATE = "conversion_rate"
    SESSION_DURATION = "session_duration"
    USER_SATISFACTION = "user_satisfaction"
    RETENTION_RATE = "retention_rate"
    CONTENT_CREATION_RATE = "content_creation_rate"
    COLLABORATION_RATE = "collaboration_rate"
    REVENUE_PER_USER = "revenue_per_user"
    FEATURE_ADOPTION = "feature_adoption"
    ERROR_RATE = "error_rate"


class ExperimentStatus(str, Enum):
    """Experiment status values"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ANALYZING = "analyzing"


class OptimizationScope(str, Enum):
    """Scope of optimization"""
    UI_LAYOUT = "ui_layout"
    CONTENT_RECOMMENDATION = "content_recommendation"
    FEATURE_CONFIGURATION = "feature_configuration"
    INTERACTION_FLOW = "interaction_flow"
    NOTIFICATION_STRATEGY = "notification_strategy"
    ONBOARDING_PROCESS = "onboarding_process"
    MONETIZATION_STRATEGY = "monetization_strategy"
    COLLABORATION_MATCHING = "collaboration_matching"


@dataclass
class ExperimentVariant:
    """Experiment variant configuration"""
    variant_id: str
    variant_name: str
    variant_config: Dict[str, Any]
    traffic_allocation: float  # 0.0 to 1.0
    is_control: bool = False
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentConfig:
    """Experiment configuration"""
    experiment_id: str
    experiment_name: str
    experiment_type: ExperimentType
    optimization_scope: OptimizationScope
    primary_metric: OptimizationMetric
    secondary_metrics: List[OptimizationMetric]
    variants: List[ExperimentVariant]
    target_audience: Dict[str, Any]
    duration_days: int
    min_sample_size: int
    significance_threshold: float = 0.05
    power_threshold: float = 0.8
    expected_effect_size: float = 0.05
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """Experiment result data"""
    experiment_id: str
    variant_id: str
    metric: OptimizationMetric
    value: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    statistical_significance: bool
    p_value: float
    effect_size: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    recommendation_id: str
    experiment_id: str
    recommended_variant: str
    confidence: float
    expected_improvement: float
    risk_assessment: Dict[str, Any]
    implementation_priority: str  # high, medium, low
    reasoning: str
    supporting_data: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.now)


class ExperienceOptimizer(BaseService):
    """
    Advanced experience optimization engine with ML-powered experimentation
    """
    
    def __init__(
        self,
        mongodb_handler: MongoDBHandler,
        redis_cache: RedisCache,
        bayesian_model: BayesianOptimizationModel,
        bandit_model: BanditModel,
        metrics_calculator: MetricsCalculator,
        experiment_analyzer: ExperimentAnalyzer
    ):
        super().__init__()
        self.mongodb = mongodb_handler
        self.redis_cache = redis_cache
        self.bayesian_model = bayesian_model
        self.bandit_model = bandit_model
        self.metrics_calculator = metrics_calculator
        self.experiment_analyzer = experiment_analyzer
        
        # Configuration
        self.cache_ttl = 1800  # 30 minutes
        self.min_daily_users = 100
        self.max_concurrent_experiments = 10
        self.statistical_power = 0.8
        self.significance_level = 0.05
        
        # Experiment state
        self._active_experiments = {}
        self._experiment_assignments = {}
        self._optimization_history = {}
        
        logger.info("ExperienceOptimizer initialized successfully")

    async def initialize(self) -> None:
        """Initialize experience optimizer"""
        try:
            # Initialize ML models
            await self.bayesian_model.initialize()
            await self.bandit_model.initialize()
            await self.experiment_analyzer.initialize()
            
            # Load active experiments
            await self._load_active_experiments()
            
            # Initialize optimization history
            await self._load_optimization_history()
            
            logger.info("ExperienceOptimizer initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize ExperienceOptimizer: {e}")
            raise ExperienceOptimizationError(f"Initialization failed: {e}")

    async def create_experiment(
        self,
        experiment_config: ExperimentConfig
    ) -> str:
        """
        Create new optimization experiment
        
        Args:
            experiment_config: Experiment configuration
            
        Returns:
            Experiment ID
        """
        try:
            # Validate experiment config
            await self._validate_experiment_config(experiment_config)
            
            # Check for conflicts with existing experiments
            conflicts = await self._check_experiment_conflicts(experiment_config)
            if conflicts:
                raise ValidationError(f"Experiment conflicts detected: {conflicts}")
            
            # Calculate required sample size
            required_sample_size = await self._calculate_sample_size(experiment_config)
            if required_sample_size > experiment_config.min_sample_size:
                logger.warning(
                    f"Recommended sample size ({required_sample_size}) is larger than "
                    f"configured minimum ({experiment_config.min_sample_size})"
                )
            
            # Store experiment configuration
            experiment_data = {
                "experiment_id": experiment_config.experiment_id,
                "config": experiment_config.__dict__,
                "status": ExperimentStatus.DRAFT.value,
                "created_at": datetime.now().isoformat(),
                "required_sample_size": required_sample_size
            }
            
            await self.mongodb.insert_one("optimization_experiments", experiment_data)
            
            # Initialize experiment tracking
            await self._initialize_experiment_tracking(experiment_config)
            
            logger.info(f"Experiment created: {experiment_config.experiment_id}")
            return experiment_config.experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            raise ExperienceOptimizationError(f"Experiment creation failed: {e}")

    async def start_experiment(
        self,
        experiment_id: str,
        force_start: bool = False
    ) -> bool:
        """
        Start optimization experiment
        
        Args:
            experiment_id: Experiment identifier
            force_start: Force start even if conditions are not met
            
        Returns:
            Success status
        """
        try:
            # Get experiment configuration
            experiment_data = await self.mongodb.find_one(
                "optimization_experiments", {"experiment_id": experiment_id}
            )
            
            if not experiment_data:
                raise ValidationError(f"Experiment not found: {experiment_id}")
            
            # Check pre-start conditions
            if not force_start:
                conditions_met = await self._check_start_conditions(experiment_data)
                if not conditions_met["can_start"]:
                    raise ValidationError(f"Start conditions not met: {conditions_met['reasons']}")
            
            # Update experiment status
            await self.mongodb.update_one(
                "optimization_experiments",
                {"experiment_id": experiment_id},
                {
                    "$set": {
                        "status": ExperimentStatus.RUNNING.value,
                        "started_at": datetime.now().isoformat()
                    }
                }
            )
            
            # Add to active experiments
            self._active_experiments[experiment_id] = experiment_data
            
            # Initialize real-time tracking
            await self._start_experiment_tracking(experiment_id)
            
            # Setup automated analysis
            await self._setup_automated_analysis(experiment_id)
            
            logger.info(f"Experiment started: {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start experiment: {e}")
            return False

    async def assign_user_to_experiment(
        self,
        user_id: str,
        experiment_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Assign user to experiment variant
        
        Args:
            user_id: User identifier
            experiment_id: Experiment identifier
            context: Additional context for assignment
            
        Returns:
            Assigned variant ID or None if not eligible
        """
        try:
            # Check if experiment is active
            if experiment_id not in self._active_experiments:
                return None
            
            experiment_data = self._active_experiments[experiment_id]
            experiment_config = ExperimentConfig(**experiment_data["config"])
            
            # Check user eligibility
            eligible = await self._check_user_eligibility(
                user_id, experiment_config, context
            )
            if not eligible:
                return None
            
            # Check if user already assigned
            cache_key = f"experiment_assignment:{experiment_id}:{user_id}"
            existing_assignment = await self.redis_cache.get(cache_key)
            if existing_assignment:
                return existing_assignment
            
            # Assign user to variant
            assigned_variant = await self._assign_user_to_variant(
                user_id, experiment_config, context
            )
            
            # Store assignment
            assignment_data = {
                "user_id": user_id,
                "experiment_id": experiment_id,
                "variant_id": assigned_variant,
                "assigned_at": datetime.now().isoformat(),
                "context": context or {}
            }
            
            await self.mongodb.insert_one("experiment_assignments", assignment_data)
            
            # Cache assignment
            await self.redis_cache.setex(cache_key, 86400, assigned_variant)  # 24 hours
            
            # Update assignment tracking
            self._experiment_assignments.setdefault(experiment_id, {})[user_id] = assigned_variant
            
            logger.debug(f"User {user_id} assigned to variant {assigned_variant} in experiment {experiment_id}")
            return assigned_variant
            
        except Exception as e:
            logger.error(f"Failed to assign user to experiment: {e}")
            return None

    async def track_experiment_event(
        self,
        user_id: str,
        experiment_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """
        Track experiment event for analysis
        
        Args:
            user_id: User identifier
            experiment_id: Experiment identifier
            event_type: Type of event
            event_data: Event data
            
        Returns:
            Success status
        """
        try:
            # Get user's variant assignment
            variant_id = await self._get_user_variant(user_id, experiment_id)
            if not variant_id:
                return False
            
            # Track event
            event_record = {
                "user_id": user_id,
                "experiment_id": experiment_id,
                "variant_id": variant_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.mongodb.insert_one("experiment_events", event_record)
            
            # Update real-time metrics
            await self._update_real_time_metrics(experiment_id, variant_id, event_type, event_data)
            
            # Check for early stopping conditions
            await self._check_early_stopping(experiment_id)
            
            logger.debug(f"Experiment event tracked: {experiment_id}, {event_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track experiment event: {e}")
            return False

    async def analyze_experiment(
        self,
        experiment_id: str,
        force_analysis: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze experiment results
        
        Args:
            experiment_id: Experiment identifier
            force_analysis: Force analysis even if criteria not met
            
        Returns:
            Experiment analysis results
        """
        try:
            # Get experiment data
            experiment_data = await self.mongodb.find_one(
                "optimization_experiments", {"experiment_id": experiment_id}
            )
            
            if not experiment_data:
                raise ValidationError(f"Experiment not found: {experiment_id}")
            
            experiment_config = ExperimentConfig(**experiment_data["config"])
            
            # Check analysis readiness
            if not force_analysis:
                ready = await self._check_analysis_readiness(experiment_id, experiment_config)
                if not ready["is_ready"]:
                    return {"error": f"Analysis not ready: {ready['reasons']}"}
            
            # Collect experiment data
            experiment_events = await self._collect_experiment_data(experiment_id)
            
            # Calculate metrics for each variant
            variant_results = {}
            for variant in experiment_config.variants:
                variant_data = [
                    event for event in experiment_events 
                    if event["variant_id"] == variant.variant_id
                ]
                
                variant_metrics = await self._calculate_variant_metrics(
                    variant_data, experiment_config
                )
                variant_results[variant.variant_id] = variant_metrics
            
            # Perform statistical analysis
            statistical_analysis = await self._perform_statistical_analysis(
                variant_results, experiment_config
            )
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                variant_results, statistical_analysis, experiment_config
            )
            
            # Compile analysis results
            analysis_result = {
                "experiment_id": experiment_id,
                "experiment_name": experiment_config.experiment_name,
                "experiment_type": experiment_config.experiment_type.value,
                "status": experiment_data["status"],
                "duration_days": (datetime.now() - datetime.fromisoformat(experiment_data["created_at"])).days,
                "total_participants": len(set(event["user_id"] for event in experiment_events)),
                "variant_results": variant_results,
                "statistical_analysis": statistical_analysis,
                "recommendations": [rec.__dict__ for rec in recommendations],
                "analysis_confidence": await self._calculate_analysis_confidence(
                    variant_results, statistical_analysis
                ),
                "generated_at": datetime.now().isoformat()
            }
            
            # Store analysis results
            await self.mongodb.insert_one("experiment_analyses", analysis_result)
            
            logger.info(f"Experiment analysis completed: {experiment_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze experiment: {e}")
            return {"error": f"Experiment analysis failed: {e}"}

    async def get_optimization_recommendations(
        self,
        scope: OptimizationScope,
        user_segment: Optional[Dict[str, Any]] = None,
        time_horizon: int = 30  # days
    ) -> List[OptimizationRecommendation]:
        """
        Get optimization recommendations for specific scope
        
        Args:
            scope: Optimization scope
            user_segment: Target user segment
            time_horizon: Time horizon for recommendations
            
        Returns:
            List of optimization recommendations
        """
        try:
            # Analyze historical optimization data
            historical_data = await self._analyze_historical_optimizations(
                scope, user_segment, time_horizon
            )
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(
                scope, historical_data
            )
            
            # Generate recommendations
            recommendations = []
            for opportunity in opportunities:
                recommendation = await self._generate_opportunity_recommendation(
                    opportunity, scope, historical_data
                )
                if recommendation:
                    recommendations.append(recommendation)
            
            # Prioritize recommendations
            prioritized_recommendations = await self._prioritize_recommendations(
                recommendations, scope
            )
            
            logger.info(f"Generated {len(prioritized_recommendations)} optimization recommendations for {scope.value}")
            return prioritized_recommendations
            
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return []

    # Private helper methods
    
    async def _validate_experiment_config(self, config: ExperimentConfig) -> None:
        """Validate experiment configuration"""
        if not config.experiment_id:
            raise ValidationError("Experiment ID is required")
        
        if not config.variants or len(config.variants) < 2:
            raise ValidationError("At least 2 variants are required")
        
        # Check traffic allocation
        total_allocation = sum(variant.traffic_allocation for variant in config.variants)
        if abs(total_allocation - 1.0) > 0.01:  # Allow small floating point errors
            raise ValidationError(f"Total traffic allocation must equal 1.0, got {total_allocation}")
        
        # Check control variant
        control_variants = [v for v in config.variants if v.is_control]
        if len(control_variants) != 1:
            raise ValidationError("Exactly one control variant is required")
        
        if config.duration_days <= 0:
            raise ValidationError("Duration must be positive")
        
        if config.min_sample_size <= 0:
            raise ValidationError("Minimum sample size must be positive")

    async def _calculate_sample_size(self, config: ExperimentConfig) -> int:
        """Calculate required sample size for experiment"""
        try:
            # Use statistical power analysis
            effect_size = config.expected_effect_size
            alpha = config.significance_threshold
            power = config.power_threshold
            
            # Calculate sample size per variant
            sample_size_per_variant = await self._power_analysis_sample_size(
                effect_size, alpha, power
            )
            
            # Total sample size
            total_sample_size = sample_size_per_variant * len(config.variants)
            
            return int(total_sample_size)
            
        except Exception as e:
            logger.error(f"Failed to calculate sample size: {e}")
            return config.min_sample_size

    async def _assign_user_to_variant(
        self,
        user_id: str,
        config: ExperimentConfig,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Assign user to experiment variant"""
        try:
            # Use consistent hashing for assignment
            hash_input = f"{config.experiment_id}:{user_id}"
            hash_value = hash(hash_input) % 10000
            normalized_hash = hash_value / 10000.0
            
            # Assign based on traffic allocation
            cumulative_allocation = 0.0
            for variant in config.variants:
                cumulative_allocation += variant.traffic_allocation
                if normalized_hash <= cumulative_allocation:
                    return variant.variant_id
            
            # Fallback to last variant
            return config.variants[-1].variant_id
            
        except Exception as e:
            logger.error(f"Failed to assign user to variant: {e}")
            return config.variants[0].variant_id  # Fallback to first variant

    async def _calculate_variant_metrics(
        self,
        variant_data: List[Dict[str, Any]],
        config: ExperimentConfig
    ) -> Dict[str, Any]:
        """Calculate metrics for experiment variant"""
        try:
            if not variant_data:
                return {}
            
            metrics = {}
            
            # Calculate primary metric
            primary_values = await self._extract_metric_values(
                variant_data, config.primary_metric
            )
            
            if primary_values:
                metrics[config.primary_metric.value] = {
                    "mean": np.mean(primary_values),
                    "std": np.std(primary_values),
                    "count": len(primary_values),
                    "confidence_interval": await self._calculate_confidence_interval(primary_values)
                }
            
            # Calculate secondary metrics
            for metric in config.secondary_metrics:
                metric_values = await self._extract_metric_values(variant_data, metric)
                
                if metric_values:
                    metrics[metric.value] = {
                        "mean": np.mean(metric_values),
                        "std": np.std(metric_values),
                        "count": len(metric_values),
                        "confidence_interval": await self._calculate_confidence_interval(metric_values)
                    }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate variant metrics: {e}")
            return {}

    async def _perform_statistical_analysis(
        self,
        variant_results: Dict[str, Dict[str, Any]],
        config: ExperimentConfig
    ) -> Dict[str, Any]:
        """Perform statistical analysis of experiment results"""
        try:
            analysis = {}
            
            # Get control variant results
            control_variant = next(v for v in config.variants if v.is_control)
            control_results = variant_results.get(control_variant.variant_id, {})
            
            # Analyze each treatment variant against control
            for variant in config.variants:
                if variant.is_control:
                    continue
                
                variant_results_data = variant_results.get(variant.variant_id, {})
                variant_analysis = {}
                
                # Analyze primary metric
                primary_metric = config.primary_metric.value
                if primary_metric in control_results and primary_metric in variant_results_data:
                    
                    control_values = await self._get_raw_values_for_metric(
                        control_variant.variant_id, config.primary_metric
                    )
                    treatment_values = await self._get_raw_values_for_metric(
                        variant.variant_id, config.primary_metric
                    )
                    
                    # Perform t-test
                    if control_values and treatment_values:
                        t_stat, p_value = stats.ttest_ind(control_values, treatment_values)
                        
                        # Calculate effect size (Cohen's d)
                        pooled_std = np.sqrt(
                            ((len(control_values) - 1) * np.var(control_values, ddof=1) +
                             (len(treatment_values) - 1) * np.var(treatment_values, ddof=1)) /
                            (len(control_values) + len(treatment_values) - 2)
                        )
                        
                        effect_size = (np.mean(treatment_values) - np.mean(control_values)) / pooled_std
                        
                        variant_analysis[primary_metric] = {
                            "t_statistic": float(t_stat),
                            "p_value": float(p_value),
                            "effect_size": float(effect_size),
                            "significant": p_value < config.significance_threshold,
                            "control_mean": float(np.mean(control_values)),
                            "treatment_mean": float(np.mean(treatment_values)),
                            "relative_improvement": float(
                                (np.mean(treatment_values) - np.mean(control_values)) / 
                                np.mean(control_values) if np.mean(control_values) != 0 else 0
                            )
                        }
                
                analysis[variant.variant_id] = variant_analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to perform statistical analysis: {e}")
            return {}


# Factory functions and utilities

def create_experience_optimizer(
    mongodb_handler: MongoDBHandler,
    redis_cache: RedisCache,
    bayesian_model: BayesianOptimizationModel,
    bandit_model: BanditModel,
    metrics_calculator: MetricsCalculator,
    experiment_analyzer: ExperimentAnalyzer
) -> ExperienceOptimizer:
    """Create experience optimizer instance"""
    return ExperienceOptimizer(
        mongodb_handler=mongodb_handler,
        redis_cache=redis_cache,
        bayesian_model=bayesian_model,
        bandit_model=bandit_model,
        metrics_calculator=metrics_calculator,
        experiment_analyzer=experiment_analyzer
    )


def validate_experiment_config(config: ExperimentConfig) -> bool:
    """Validate experiment configuration"""
    if not config.experiment_id or not isinstance(config.experiment_id, str):
        return False
    
    if not config.variants or len(config.variants) < 2:
        return False
    
    total_allocation = sum(variant.traffic_allocation for variant in config.variants)
    if abs(total_allocation - 1.0) > 0.01:
        return False
    
    control_variants = [v for v in config.variants if v.is_control]
    if len(control_variants) != 1:
        return False
    
    return True
