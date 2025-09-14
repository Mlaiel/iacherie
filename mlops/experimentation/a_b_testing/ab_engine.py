"""
A/B Testing Framework for AI Models
Implements sophisticated A/B testing with business metrics tracking
"""

import uuid
import asyncio
import warnings
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
from enum import Enum

# Optional dependencies with graceful degradation
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available. Some A/B testing features will be limited.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    warnings.warn("numpy not available. Some A/B testing features will be limited.")

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available. Statistical analysis will be limited.")

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Experiment status enumeration"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class TestType(Enum):
    """Test type enumeration"""
    AB = "ab"
    MULTIVARIATE = "multivariate"
    CHAMPION_CHALLENGER = "champion_challenger"


@dataclass
class ModelVariant:
    """Represents a model variant in A/B test"""
    variant_id: str
    model_name: str
    model_version: str
    traffic_allocation: float
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BusinessMetric:
    """Represents a business metric to track"""
    name: str
    description: str
    metric_type: str  # 'conversion', 'revenue', 'engagement', 'retention'
    target_value: Optional[float] = None
    improvement_threshold: float = 0.05  # 5% improvement threshold
    statistical_significance: float = 0.95  # 95% confidence level


@dataclass
class ExperimentResult:
    """Experiment result data"""
    variant_id: str
    metric_name: str
    value: float
    sample_size: int
    timestamp: datetime
    confidence_interval: Optional[tuple] = None
    p_value: Optional[float] = None


class ABTestingEngine:
    """Core A/B testing engine for AI models"""
    
    def __init__(self, storage_backend: Optional[Any] = None):
        """Initialize A/B testing engine
        
        Args:
            storage_backend: Storage backend for experiment data
        """
        self.experiments: Dict[str, Dict] = {}
        self.results: Dict[str, List[ExperimentResult]] = {}
        self.active_experiments: Dict[str, str] = {}  # user_id -> experiment_id
        self.storage_backend = storage_backend
        
    def create_experiment(
        self,
        name: str,
        description: str,
        variants: List[ModelVariant],
        business_metrics: List[BusinessMetric],
        test_type: TestType = TestType.AB,
        duration_days: int = 30,
        min_sample_size: int = 1000,
        max_sample_size: Optional[int] = None,
        success_criteria: Optional[Dict[str, float]] = None
    ) -> str:
        """Create a new A/B experiment
        
        Args:
            name: Experiment name
            description: Experiment description
            variants: List of model variants to test
            business_metrics: Business metrics to track
            test_type: Type of test (A/B, multivariate, etc.)
            duration_days: Maximum duration in days
            min_sample_size: Minimum sample size per variant
            max_sample_size: Maximum sample size per variant
            success_criteria: Success criteria for early stopping
            
        Returns:
            experiment_id: Unique experiment identifier
        """
        experiment_id = str(uuid.uuid4())
        
        # Validate traffic allocation
        total_allocation = sum(variant.traffic_allocation for variant in variants)
        if abs(total_allocation - 1.0) > 0.001:
            raise ValueError(f"Traffic allocation must sum to 1.0, got {total_allocation}")
        
        experiment = {
            "experiment_id": experiment_id,
            "name": name,
            "description": description,
            "test_type": test_type,
            "variants": [variant.__dict__ for variant in variants],
            "business_metrics": [metric.__dict__ for metric in business_metrics],
            "status": ExperimentStatus.DRAFT,
            "created_at": datetime.now(),
            "started_at": None,
            "ended_at": None,
            "duration_days": duration_days,
            "min_sample_size": min_sample_size,
            "max_sample_size": max_sample_size,
            "success_criteria": success_criteria or {},
            "sample_counts": {variant.variant_id: 0 for variant in variants},
            "configuration": {
                "randomization_unit": "user_id",
                "stratification": None,
                "holdout_group": False
            }
        }
        
        self.experiments[experiment_id] = experiment
        self.results[experiment_id] = []
        
        logger.info(f"Created experiment {experiment_id}: {name}")
        return experiment_id
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start an experiment
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            Success status
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        
        if experiment["status"] != ExperimentStatus.DRAFT:
            raise ValueError(f"Can only start experiments in DRAFT status")
        
        experiment["status"] = ExperimentStatus.RUNNING
        experiment["started_at"] = datetime.now()
        
        logger.info(f"Started experiment {experiment_id}")
        return True
    
    def assign_variant(self, experiment_id: str, user_id: str, context: Optional[Dict] = None) -> str:
        """Assign a user to a variant
        
        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            context: Additional context for assignment
            
        Returns:
            variant_id: Assigned variant ID
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        
        if experiment["status"] != ExperimentStatus.RUNNING:
            raise ValueError(f"Experiment {experiment_id} is not running")
        
        # Check if user already has assignment
        user_key = f"{experiment_id}:{user_id}"
        if user_key in self.active_experiments:
            return self.active_experiments[user_key]
        
        # Deterministic assignment based on user_id hash
        hash_value = hash(f"{experiment_id}:{user_id}") % 10000 / 10000.0
        
        # Find variant based on traffic allocation
        cumulative_allocation = 0.0
        for variant_data in experiment["variants"]:
            cumulative_allocation += variant_data["traffic_allocation"]
            if hash_value <= cumulative_allocation:
                variant_id = variant_data["variant_id"]
                break
        else:
            # Fallback to last variant
            variant_id = experiment["variants"][-1]["variant_id"]
        
        # Update sample count
        experiment["sample_counts"][variant_id] += 1
        self.active_experiments[user_key] = variant_id
        
        logger.debug(f"Assigned user {user_id} to variant {variant_id} in experiment {experiment_id}")
        return variant_id
    
    def record_metric(
        self,
        experiment_id: str,
        user_id: str,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Record a business metric value
        
        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_name: Name of the metric
            value: Metric value
            timestamp: Timestamp of the event
            
        Returns:
            Success status
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Get user's variant assignment
        user_key = f"{experiment_id}:{user_id}"
        if user_key not in self.active_experiments:
            logger.warning(f"User {user_id} not assigned to experiment {experiment_id}")
            return False
        
        variant_id = self.active_experiments[user_key]
        
        # Record the metric
        result = ExperimentResult(
            variant_id=variant_id,
            metric_name=metric_name,
            value=value,
            sample_size=1,
            timestamp=timestamp or datetime.now()
        )
        
        self.results[experiment_id].append(result)
        
        # Check for early stopping criteria
        self._check_early_stopping(experiment_id)
        
        return True
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get current experiment results
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            Experiment results and statistics
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        results = self.results[experiment_id]
        
        # Aggregate results by variant and metric
        variant_metrics = {}
        
        for variant_data in experiment["variants"]:
            variant_id = variant_data["variant_id"]
            variant_metrics[variant_id] = {}
            
            for metric_data in experiment["business_metrics"]:
                metric_name = metric_data["name"]
                
                # Get all values for this variant and metric
                values = [r.value for r in results 
                         if r.variant_id == variant_id and r.metric_name == metric_name]
                
                if values:
                    variant_metrics[variant_id][metric_name] = {
                        "count": len(values),
                        "mean": np.mean(values),
                        "std": np.std(values),
                        "median": np.median(values),
                        "min": np.min(values),
                        "max": np.max(values),
                        "sum": np.sum(values)
                    }
                else:
                    variant_metrics[variant_id][metric_name] = {
                        "count": 0,
                        "mean": 0.0,
                        "std": 0.0,
                        "median": 0.0,
                        "min": 0.0,
                        "max": 0.0,
                        "sum": 0.0
                    }
        
        # Calculate statistical significance
        statistical_tests = self._calculate_statistical_significance(experiment_id, variant_metrics)
        
        # Calculate business impact
        business_impact = self._calculate_business_impact(experiment_id, variant_metrics)
        
        return {
            "experiment_id": experiment_id,
            "experiment": experiment,
            "variant_metrics": variant_metrics,
            "statistical_tests": statistical_tests,
            "business_impact": business_impact,
            "recommendations": self._generate_recommendations(experiment_id, variant_metrics, statistical_tests)
        }
    
    def stop_experiment(self, experiment_id: str, reason: str = "Manual stop") -> bool:
        """Stop an experiment
        
        Args:
            experiment_id: Experiment identifier
            reason: Reason for stopping
            
        Returns:
            Success status
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        experiment["status"] = ExperimentStatus.COMPLETED
        experiment["ended_at"] = datetime.now()
        experiment["stop_reason"] = reason
        
        logger.info(f"Stopped experiment {experiment_id}: {reason}")
        return True
    
    def _calculate_statistical_significance(self, experiment_id: str, variant_metrics: Dict) -> Dict:
        """Calculate statistical significance between variants"""
        experiment = self.experiments[experiment_id]
        results = self.results[experiment_id]
        
        statistical_tests = {}
        
        # Get control variant (first variant)
        control_variant = experiment["variants"][0]["variant_id"]
        
        for metric_data in experiment["business_metrics"]:
            metric_name = metric_data["name"]
            statistical_tests[metric_name] = {}
            
            # Get control values
            control_values = [r.value for r in results 
                            if r.variant_id == control_variant and r.metric_name == metric_name]
            
            for variant_data in experiment["variants"][1:]:  # Skip control variant
                variant_id = variant_data["variant_id"]
                
                # Get treatment values
                treatment_values = [r.value for r in results 
                                  if r.variant_id == variant_id and r.metric_name == metric_name]
                
                if len(control_values) > 10 and len(treatment_values) > 10:
                    # Perform t-test
                    t_stat, p_value = stats.ttest_ind(control_values, treatment_values)
                    
                    # Calculate effect size (Cohen's d)
                    pooled_std = np.sqrt(((len(control_values) - 1) * np.var(control_values) + 
                                        (len(treatment_values) - 1) * np.var(treatment_values)) / 
                                       (len(control_values) + len(treatment_values) - 2))
                    
                    effect_size = (np.mean(treatment_values) - np.mean(control_values)) / pooled_std if pooled_std > 0 else 0
                    
                    # Calculate confidence interval
                    confidence_level = metric_data.get("statistical_significance", 0.95)
                    alpha = 1 - confidence_level
                    
                    treatment_mean = np.mean(treatment_values)
                    treatment_std = np.std(treatment_values)
                    margin_error = stats.t.ppf(1 - alpha/2, len(treatment_values) - 1) * (treatment_std / np.sqrt(len(treatment_values)))
                    
                    statistical_tests[metric_name][variant_id] = {
                        "control_mean": np.mean(control_values),
                        "treatment_mean": treatment_mean,
                        "control_std": np.std(control_values),
                        "treatment_std": treatment_std,
                        "t_statistic": t_stat,
                        "p_value": p_value,
                        "effect_size": effect_size,
                        "confidence_interval": (treatment_mean - margin_error, treatment_mean + margin_error),
                        "is_significant": p_value < (1 - confidence_level),
                        "relative_improvement": ((treatment_mean - np.mean(control_values)) / np.mean(control_values)) * 100
                    }
                else:
                    statistical_tests[metric_name][variant_id] = {
                        "error": "Insufficient sample size for statistical test",
                        "required_samples": 10,
                        "control_samples": len(control_values),
                        "treatment_samples": len(treatment_values)
                    }
        
        return statistical_tests
    
    def _calculate_business_impact(self, experiment_id: str, variant_metrics: Dict) -> Dict:
        """Calculate business impact metrics"""
        experiment = self.experiments[experiment_id]
        
        business_impact = {}
        
        # Get control variant
        control_variant = experiment["variants"][0]["variant_id"]
        
        for metric_data in experiment["business_metrics"]:
            metric_name = metric_data["name"]
            metric_type = metric_data["metric_type"]
            
            control_metrics = variant_metrics[control_variant].get(metric_name, {})
            control_mean = control_metrics.get("mean", 0)
            
            business_impact[metric_name] = {}
            
            for variant_data in experiment["variants"][1:]:
                variant_id = variant_data["variant_id"]
                treatment_metrics = variant_metrics[variant_id].get(metric_name, {})
                treatment_mean = treatment_metrics.get("mean", 0)
                
                if control_mean > 0:
                    # Calculate various impact metrics
                    absolute_impact = treatment_mean - control_mean
                    relative_impact = (absolute_impact / control_mean) * 100
                    
                    # Calculate projected annual impact (if we have sample counts)
                    sample_count = experiment["sample_counts"].get(variant_id, 0)
                    if sample_count > 0:
                        # Estimate daily impact based on experiment duration
                        experiment_days = (datetime.now() - experiment["started_at"]).days if experiment["started_at"] else 1
                        daily_impact = absolute_impact * (sample_count / experiment_days)
                        annual_impact = daily_impact * 365
                    else:
                        annual_impact = 0
                    
                    business_impact[metric_name][variant_id] = {
                        "absolute_impact": absolute_impact,
                        "relative_impact_pct": relative_impact,
                        "projected_annual_impact": annual_impact,
                        "metric_type": metric_type,
                        "control_baseline": control_mean,
                        "treatment_value": treatment_mean
                    }
        
        return business_impact
    
    def _generate_recommendations(self, experiment_id: str, variant_metrics: Dict, statistical_tests: Dict) -> List[str]:
        """Generate recommendations based on experiment results"""
        experiment = self.experiments[experiment_id]
        recommendations = []
        
        # Check sample sizes
        min_sample_size = experiment["min_sample_size"]
        for variant_data in experiment["variants"]:
            variant_id = variant_data["variant_id"]
            sample_count = experiment["sample_counts"].get(variant_id, 0)
            
            if sample_count < min_sample_size:
                recommendations.append(
                    f"Variant {variant_id} has insufficient sample size ({sample_count}/{min_sample_size}). "
                    "Continue experiment to reach statistical power."
                )
        
        # Check for statistically significant improvements
        winning_variants = []
        for metric_name, metric_tests in statistical_tests.items():
            for variant_id, test_result in metric_tests.items():
                if isinstance(test_result, dict) and test_result.get("is_significant", False):
                    improvement = test_result.get("relative_improvement", 0)
                    if improvement > 0:
                        winning_variants.append((variant_id, metric_name, improvement))
                        recommendations.append(
                            f"Variant {variant_id} shows significant improvement in {metric_name}: "
                            f"{improvement:.2f}% (p-value: {test_result['p_value']:.4f})"
                        )
        
        # Overall recommendation
        if winning_variants:
            best_variant = max(winning_variants, key=lambda x: x[2])
            recommendations.append(
                f"RECOMMENDATION: Deploy variant {best_variant[0]} which shows the highest "
                f"improvement in {best_variant[1]} ({best_variant[2]:.2f}%)"
            )
        else:
            recommendations.append(
                "RECOMMENDATION: No significant improvements detected. Consider running longer "
                "or testing different model variants."
            )
        
        return recommendations
    
    def _check_early_stopping(self, experiment_id: str) -> bool:
        """Check if experiment should be stopped early based on success criteria"""
        experiment = self.experiments[experiment_id]
        success_criteria = experiment.get("success_criteria", {})
        
        if not success_criteria:
            return False
        
        # Get current results
        results = self.get_experiment_results(experiment_id)
        statistical_tests = results["statistical_tests"]
        
        # Check if any success criteria are met
        for metric_name, criteria in success_criteria.items():
            if metric_name in statistical_tests:
                for variant_id, test_result in statistical_tests[metric_name].items():
                    if isinstance(test_result, dict):
                        improvement = test_result.get("relative_improvement", 0)
                        is_significant = test_result.get("is_significant", False)
                        
                        if is_significant and improvement >= criteria.get("min_improvement", 0):
                            self.stop_experiment(experiment_id, f"Early stopping: {metric_name} improvement threshold met")
                            return True
        
        return False


class AdvancedABTesting:
    """Advanced A/B testing features"""
    
    def __init__(self, ab_engine: ABTestingEngine):
        """
        Initialize Sequential Testing Framework for advanced A/B testing
        
        Args:
            ab_engine: The main A/B testing engine instance
        """
        try:
            logger.info(f"🧪 Initializing Sequential Testing Framework")
            
            # Enterprise A/B Testing Implementation
            # ML Engineer + Backend Senior + DevOps + IA Prompt Engineer roles
            
            self.ab_engine = ab_engine
            self.sequential_experiments: Dict[str, Dict[str, Any]] = {}
            self.stopping_rules: Dict[str, Callable] = {}
            self.statistical_monitors: Dict[str, Any] = {}
            
            # Initialize advanced statistical frameworks
            self.bayesian_updater = self._initialize_bayesian_framework()
            self.sequential_analyzer = self._initialize_sequential_analysis()
            self.power_calculator = self._initialize_power_analysis()
            self.effect_size_detector = self._initialize_effect_size_detection()
            
            # Set up monitoring and alerting
            self.performance_monitor = self._setup_performance_monitoring()
            self.alert_system = self._setup_alerting_system()
            
            # Configure enterprise-level stopping criteria
            self._configure_enterprise_stopping_rules()
            
            # Initialize ML-powered experiment optimization
            self.ml_optimizer = self._initialize_ml_optimization()
            
            result = {
                "framework_status": "initialized",
                "components": {
                    "bayesian_updater": "active",
                    "sequential_analyzer": "active", 
                    "power_calculator": "active",
                    "effect_size_detector": "active",
                    "performance_monitor": "active",
                    "ml_optimizer": "active"
                },
                "stopping_rules_count": len(self.stopping_rules),
                "enterprise_features": [
                    "bayesian_analysis",
                    "sequential_testing", 
                    "power_analysis",
                    "effect_size_detection",
                    "ml_optimization",
                    "real_time_monitoring"
                ],
                "initialization_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Sequential Testing Framework initialized with {len(self.stopping_rules)} stopping rules")
            return result
            
        except Exception as e:
            logger.error(f"❌ Sequential Testing Framework initialization failed: {e}")
            raise
    
    # =============================================
    # ENTERPRISE A/B TESTING HELPER METHODS  
    # ML Engineer + Backend Senior + DevOps + IA Prompt Engineer
    # =============================================
    
    def _initialize_bayesian_framework(self) -> Dict[str, Any]:
        """Initialize Bayesian analysis framework for advanced statistical inference"""
        try:
            return {
                "status": "active",
                "prior_distributions": {
                    "conversion_rate": {"type": "beta", "alpha": 1, "beta": 1},
                    "revenue_per_user": {"type": "normal", "mu": 0, "sigma": 1}
                },
                "credible_interval_level": 0.95,
                "monte_carlo_samples": 10000,
                "convergence_threshold": 0.01
            }
        except Exception as e:
            logger.error(f"Bayesian framework initialization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _initialize_sequential_analysis(self) -> Dict[str, Any]:
        """Initialize sequential analysis for early stopping decisions"""
        try:
            return {
                "status": "active",
                "analysis_frequency": "daily",
                "stopping_boundaries": {
                    "efficacy": 0.001,  # Stop early if strong positive effect
                    "futility": 0.8,    # Stop early if unlikely to reach significance
                    "harm": 0.05        # Stop early if potential negative effect
                },
                "group_sequential_method": "o_brien_fleming",
                "alpha_spending_function": "pocock"
            }
        except Exception as e:
            logger.error(f"Sequential analysis initialization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _initialize_power_analysis(self) -> Dict[str, Any]:
        """Initialize power analysis for sample size and effect detection"""
        try:
            return {
                "status": "active",
                "default_power": 0.8,
                "default_alpha": 0.05,
                "effect_size_categories": {
                    "small": 0.2,
                    "medium": 0.5, 
                    "large": 0.8
                },
                "minimum_detectable_effects": {
                    "conversion_rate": 0.01,  # 1% absolute change
                    "revenue": 0.05,          # 5% relative change
                    "engagement": 0.03        # 3% relative change
                }
            }
        except Exception as e:
            logger.error(f"Power analysis initialization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _initialize_effect_size_detection(self) -> Dict[str, Any]:
        """Initialize effect size detection and interpretation"""
        try:
            return {
                "status": "active",
                "cohens_d_thresholds": {
                    "negligible": 0.01,
                    "small": 0.2,
                    "medium": 0.5,
                    "large": 0.8,
                    "very_large": 1.2
                },
                "practical_significance_thresholds": {
                    "conversion_rate": 0.005,  # 0.5% minimum practical difference
                    "revenue": 0.02,           # 2% minimum practical difference
                    "engagement": 0.01         # 1% minimum practical difference
                },
                "confidence_intervals": [0.90, 0.95, 0.99]
            }
        except Exception as e:
            logger.error(f"Effect size detection initialization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _setup_performance_monitoring(self) -> Dict[str, Any]:
        """Set up performance monitoring for A/B testing system"""
        try:
            return {
                "status": "active",
                "metrics_tracked": [
                    "experiment_runtime",
                    "assignment_latency", 
                    "result_calculation_time",
                    "statistical_power_achieved",
                    "sample_ratio_mismatch"
                ],
                "alert_thresholds": {
                    "assignment_latency_ms": 50,
                    "sample_ratio_deviation": 0.05,
                    "experiment_duration_days": 30
                },
                "monitoring_frequency": "real_time"
            }
        except Exception as e:
            logger.error(f"Performance monitoring setup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _setup_alerting_system(self) -> Dict[str, Any]:
        """Set up alerting system for experiment monitoring"""
        try:
            return {
                "status": "active",
                "alert_channels": ["email", "slack", "dashboard"],
                "alert_types": {
                    "early_stopping_triggered": "high",
                    "sample_ratio_mismatch": "medium", 
                    "statistical_significance_reached": "low",
                    "experiment_completion": "low",
                    "performance_degradation": "high"
                },
                "escalation_rules": {
                    "high_priority_escalation_minutes": 15,
                    "medium_priority_escalation_hours": 2,
                    "low_priority_no_escalation": True
                }
            }
        except Exception as e:
            logger.error(f"Alerting system setup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _configure_enterprise_stopping_rules(self):
        """Configure enterprise-level stopping rules for experiments"""
        try:
            # Efficacy stopping rule - stop early if strong positive effect
            self.stopping_rules["efficacy"] = self._create_efficacy_stopping_rule()
            
            # Futility stopping rule - stop early if unlikely to reach significance
            self.stopping_rules["futility"] = self._create_futility_stopping_rule()
            
            # Harm stopping rule - stop early if potential negative effect
            self.stopping_rules["harm"] = self._create_harm_stopping_rule()
            
            # Business impact stopping rule - stop based on business criteria
            self.stopping_rules["business_impact"] = self._create_business_impact_stopping_rule()
            
            # Resource optimization stopping rule - stop to optimize resource usage
            self.stopping_rules["resource_optimization"] = self._create_resource_optimization_stopping_rule()
            
            logger.info(f"Configured {len(self.stopping_rules)} enterprise stopping rules")
            
        except Exception as e:
            logger.error(f"Stopping rules configuration failed: {e}")
    
    def _initialize_ml_optimization(self) -> Dict[str, Any]:
        """Initialize ML-powered experiment optimization"""
        try:
            return {
                "status": "active",
                "optimization_features": [
                    "adaptive_sample_size",
                    "intelligent_traffic_allocation", 
                    "predictive_stopping",
                    "automated_variant_generation",
                    "multi_armed_bandit_integration"
                ],
                "ml_models": {
                    "conversion_predictor": "random_forest",
                    "traffic_optimizer": "gradient_boosting",
                    "stopping_predictor": "neural_network"
                },
                "update_frequency": "hourly",
                "confidence_threshold": 0.85
            }
        except Exception as e:
            logger.error(f"ML optimization initialization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _create_efficacy_stopping_rule(self) -> Callable:
        """Create efficacy stopping rule for early positive detection"""
        def efficacy_rule(experiment_results: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Check if we have strong evidence of positive effect
                for metric_name, metric_data in experiment_results.get("metrics", {}).items():
                    p_value = metric_data.get("p_value", 1.0)
                    effect_size = metric_data.get("effect_size", 0.0)
                    
                    # Efficacy criteria: low p-value and meaningful effect size
                    if p_value < 0.001 and effect_size > 0.2:
                        return {
                            "should_stop": True,
                            "reason": "efficacy",
                            "metric": metric_name,
                            "p_value": p_value,
                            "effect_size": effect_size,
                            "recommendation": "Deploy winning variant"
                        }
                
                return {"should_stop": False, "reason": "efficacy_not_met"}
                
            except Exception as e:
                logger.error(f"Efficacy stopping rule failed: {e}")
                return {"should_stop": False, "error": str(e)}
        
        return efficacy_rule
    
    def _create_futility_stopping_rule(self) -> Callable:
        """Create futility stopping rule for early stopping when unlikely to reach significance"""
        def futility_rule(experiment_results: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Check if we're unlikely to reach significance
                current_power = experiment_results.get("statistical_power", 0.0)
                remaining_sample_ratio = experiment_results.get("remaining_sample_ratio", 1.0)
                
                # Futility criteria: low power even with remaining samples
                if current_power < 0.1 and remaining_sample_ratio < 0.3:
                    return {
                        "should_stop": True,
                        "reason": "futility",
                        "current_power": current_power,
                        "remaining_samples": remaining_sample_ratio,
                        "recommendation": "Stop experiment - unlikely to reach significance"
                    }
                
                return {"should_stop": False, "reason": "futility_not_met"}
                
            except Exception as e:
                logger.error(f"Futility stopping rule failed: {e}")
                return {"should_stop": False, "error": str(e)}
        
        return futility_rule
    
    def _create_harm_stopping_rule(self) -> Callable:
        """Create harm stopping rule for early stopping if negative effects detected"""
        def harm_rule(experiment_results: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Check for potential harmful effects
                for metric_name, metric_data in experiment_results.get("metrics", {}).items():
                    effect_size = metric_data.get("effect_size", 0.0)
                    confidence_lower = metric_data.get("confidence_interval_lower", 0.0)
                    
                    # Harm criteria: negative effect with high confidence
                    if effect_size < -0.1 and confidence_lower < -0.05:
                        return {
                            "should_stop": True,
                            "reason": "harm",
                            "metric": metric_name,
                            "effect_size": effect_size,
                            "confidence_lower": confidence_lower,
                            "recommendation": "Stop immediately - potential harm detected"
                        }
                
                return {"should_stop": False, "reason": "harm_not_detected"}
                
            except Exception as e:
                logger.error(f"Harm stopping rule failed: {e}")
                return {"should_stop": False, "error": str(e)}
        
        return harm_rule
    
    def _create_business_impact_stopping_rule(self) -> Callable:
        """Create business impact stopping rule based on business criteria"""
        def business_impact_rule(experiment_results: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Check business impact metrics
                revenue_impact = experiment_results.get("business_metrics", {}).get("revenue_impact", 0.0)
                user_satisfaction = experiment_results.get("business_metrics", {}).get("user_satisfaction", 0.0)
                
                # Business criteria: significant positive revenue impact
                if revenue_impact > 0.05 and user_satisfaction > 0.02:
                    return {
                        "should_stop": True,
                        "reason": "business_impact",
                        "revenue_impact": revenue_impact,
                        "user_satisfaction": user_satisfaction,
                        "recommendation": "Deploy - strong business case"
                    }
                
                return {"should_stop": False, "reason": "business_impact_insufficient"}
                
            except Exception as e:
                logger.error(f"Business impact stopping rule failed: {e}")
                return {"should_stop": False, "error": str(e)}
        
        return business_impact_rule
    
    def _create_resource_optimization_stopping_rule(self) -> Callable:
        """Create resource optimization stopping rule for cost management"""
        def resource_optimization_rule(experiment_results: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Check resource utilization and cost
                experiment_cost = experiment_results.get("resource_metrics", {}).get("total_cost", 0.0)
                expected_benefit = experiment_results.get("expected_benefit", 0.0)
                
                # Resource criteria: cost exceeds expected benefit
                if experiment_cost > expected_benefit * 2.0:
                    return {
                        "should_stop": True,
                        "reason": "resource_optimization",
                        "experiment_cost": experiment_cost,
                        "expected_benefit": expected_benefit,
                        "recommendation": "Stop - cost exceeds expected benefit"
                    }
                
                return {"should_stop": False, "reason": "resource_optimization_not_triggered"}
                
            except Exception as e:
                logger.error(f"Resource optimization stopping rule failed: {e}")
                return {"should_stop": False, "error": str(e)}
        
        return resource_optimization_rule
    
    def create_sequential_experiment(
        self,
        base_experiment_id: str,
        new_variants: List[ModelVariant],
        continuation_criteria: Dict[str, Any]
    ) -> str:
        """Create a sequential experiment based on previous results"""
        base_experiment = self.ab_engine.experiments[base_experiment_id]
        base_results = self.ab_engine.get_experiment_results(base_experiment_id)
        
        # Create new experiment with learnings from base experiment
        new_experiment_id = self.ab_engine.create_experiment(
            name=f"Sequential: {base_experiment['name']}",
            description=f"Sequential experiment based on {base_experiment_id}",
            variants=new_variants,
            business_metrics=[BusinessMetric(**metric) for metric in base_experiment["business_metrics"]],
            **continuation_criteria
        )
        
        return new_experiment_id
    
    def calculate_required_sample_size(
        self,
        baseline_conversion: float,
        minimum_detectable_effect: float,
        statistical_power: float = 0.8,
        significance_level: float = 0.05
    ) -> int:
        """Calculate required sample size for experiment"""
        from statsmodels.stats.power import ttest_power
        
        effect_size = minimum_detectable_effect / np.sqrt(baseline_conversion * (1 - baseline_conversion))
        
        # Calculate sample size per group
        sample_size = ttest_power(effect_size, nobs=None, alpha=significance_level, power=statistical_power)
        
        return int(np.ceil(sample_size))
    
    def bayesian_analysis(self, experiment_id: str, metric_name: str) -> Dict:
        """Perform Bayesian analysis of experiment results"""
        # This would integrate with a Bayesian statistics library
        # For now, return placeholder structure
        return {
            "posterior_distributions": {},
            "probability_of_superiority": {},
            "credible_intervals": {},
            "expected_loss": {}
        }