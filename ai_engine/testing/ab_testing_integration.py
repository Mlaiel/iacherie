"""A/B Testing Integration for ML Models

This module integrates with the existing A/B testing framework to provide
comprehensive experimentation capabilities for ML model validation and
continuous improvement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from scipy import stats
import json
import uuid

# Import existing A/B testing framework
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from conversational.response_generation.response_analytics import ABTestingFramework, MetricType
except ImportError:
    # Fallback definitions if import fails
    class MetricType(Enum):
        ENGAGEMENT = "engagement"
        SATISFACTION = "satisfaction"
        EFFECTIVENESS = "effectiveness"
        ACCURACY = "accuracy"
        PERFORMANCE = "performance"

logger = logging.getLogger(__name__)


class ExperimentType(str, Enum):
    """Types of ML experiments"""
    MODEL_COMPARISON = "model_comparison"
    FEATURE_TESTING = "feature_testing"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    ALGORITHM_SELECTION = "algorithm_selection"
    PREPROCESSING_OPTIMIZATION = "preprocessing_optimization"
    ARCHITECTURE_TESTING = "architecture_testing"


class ExperimentStatus(str, Enum):
    """Experiment status enumeration"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"


class StatisticalSignificance(str, Enum):
    """Statistical significance levels"""
    HIGH = "high"        # p < 0.01
    MODERATE = "moderate"  # p < 0.05
    LOW = "low"          # p < 0.1
    NONE = "none"        # p >= 0.1


@dataclass
class ExperimentConfig:
    """Configuration for ML experiments"""
    experiment_name: str
    experiment_type: ExperimentType
    primary_metric: MetricType
    secondary_metrics: List[MetricType]
    variants: List[Dict[str, Any]]
    traffic_allocation: Dict[str, float]
    duration: timedelta
    min_sample_size: int
    confidence_level: float
    statistical_power: float
    early_stopping_enabled: bool
    success_criteria: Dict[str, Any]


@dataclass
class VariantResult:
    """Results for a single experiment variant"""
    variant_id: str
    variant_name: str
    sample_size: int
    metrics: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]
    statistical_significance: Dict[str, StatisticalSignificance]
    performance_data: Dict[str, Any]


@dataclass
class ExperimentResults:
    """Complete experiment results"""
    experiment_id: str
    experiment_name: str
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration: timedelta
    variant_results: List[VariantResult]
    winner: Optional[str]
    statistical_summary: Dict[str, Any]
    business_impact: Dict[str, Any]
    recommendations: List[str]
    next_steps: List[str]


class MLExperimentFramework:
    """ML-focused experiment framework extending A/B testing capabilities"""
    
    def __init__(self, base_ab_framework: Optional[object] = None):
        """
        Initialize ML experiment framework.
        
        Args:
            base_ab_framework: Existing ABTestingFramework instance
        """
        self.base_framework = base_ab_framework or self._create_base_framework()
        self.ml_experiments = {}
        self.experiment_history = {}
        self.model_performance_cache = {}
        self.logger = logging.getLogger(__name__)
        
    def _create_base_framework(self):
        """Create base A/B testing framework if not provided"""
        try:
            from conversational.response_generation.response_analytics import ABTestingFramework
            return ABTestingFramework()
        except ImportError:
            # Return mock framework for testing
            return None
    
    async def create_ml_experiment(
        self,
        config: ExperimentConfig,
        model_variants: Dict[str, Callable],
        dataset: Dict[str, np.ndarray]
    ) -> str:
        """
        Create a new ML experiment.
        
        Args:
            config: Experiment configuration
            model_variants: Dictionary of model variants {variant_name: model_predict_func}
            dataset: Dictionary containing 'X_test', 'y_test', and optionally 'X_train', 'y_train'
            
        Returns:
            Experiment ID
        """
        try:
            experiment_id = str(uuid.uuid4())
            
            # Validate inputs
            self._validate_experiment_config(config, model_variants, dataset)
            
            # Create experiment record
            experiment = {
                "id": experiment_id,
                "config": config,
                "model_variants": model_variants,
                "dataset": dataset,
                "status": ExperimentStatus.DRAFT,
                "created_at": datetime.utcnow(),
                "results": None,
                "metrics_history": []
            }
            
            self.ml_experiments[experiment_id] = experiment
            
            # Initialize with base A/B framework if available
            if self.base_framework:
                ab_variants = [
                    {"name": name, "model": model, "allocation": config.traffic_allocation.get(name, 0)}
                    for name, model in model_variants.items()
                ]
                
                # Create corresponding A/B test
                ab_experiment_id = await self.base_framework.create_experiment(
                    experiment_name=config.experiment_name,
                    variants=ab_variants,
                    target_metric=config.primary_metric,
                    traffic_allocation=config.traffic_allocation
                )
                experiment["ab_experiment_id"] = ab_experiment_id
            
            self.logger.info(f"Created ML experiment {config.experiment_name} with ID {experiment_id}")
            return experiment_id
            
        except Exception as e:
            self.logger.error(f"Failed to create ML experiment: {str(e)}")
            raise
    
    def _validate_experiment_config(
        self,
        config: ExperimentConfig,
        model_variants: Dict[str, Callable],
        dataset: Dict[str, np.ndarray]
    ):
        """Validate experiment configuration"""
        
        # Check required dataset components
        required_keys = ['X_test', 'y_test']
        for key in required_keys:
            if key not in dataset:
                raise ValueError(f"Dataset missing required key: {key}")
        
        # Check model variants
        if len(model_variants) < 2:
            raise ValueError("At least 2 model variants required for comparison")
        
        # Check traffic allocation
        total_allocation = sum(config.traffic_allocation.values())
        if not (0.99 <= total_allocation <= 1.01):  # Allow small floating point errors
            raise ValueError("Traffic allocation must sum to 1.0")
        
        # Check variant names match
        variant_names = {variant["name"] for variant in config.variants}
        model_names = set(model_variants.keys())
        allocation_names = set(config.traffic_allocation.keys())
        
        if variant_names != model_names or variant_names != allocation_names:
            raise ValueError("Variant names must match across config, models, and allocation")
    
    async def run_experiment(
        self,
        experiment_id: str,
        evaluation_metrics: Optional[List[str]] = None
    ) -> ExperimentResults:
        """
        Run the ML experiment.
        
        Args:
            experiment_id: Experiment identifier
            evaluation_metrics: Additional metrics to evaluate
            
        Returns:
            Experiment results
        """
        try:
            if experiment_id not in self.ml_experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.ml_experiments[experiment_id]
            config = experiment["config"]
            model_variants = experiment["model_variants"]
            dataset = experiment["dataset"]
            
            # Update status
            experiment["status"] = ExperimentStatus.RUNNING
            experiment["start_time"] = datetime.utcnow()
            
            self.logger.info(f"Starting experiment {config.experiment_name}")
            
            # Run variant evaluation
            variant_results = await self._evaluate_variants(
                model_variants, dataset, config, evaluation_metrics
            )
            
            # Statistical analysis
            statistical_summary = await self._perform_statistical_analysis(
                variant_results, config
            )
            
            # Determine winner
            winner = self._determine_experiment_winner(variant_results, statistical_summary)
            
            # Business impact analysis
            business_impact = await self._analyze_business_impact(variant_results, config)
            
            # Generate recommendations
            recommendations = self._generate_experiment_recommendations(
                variant_results, statistical_summary, winner
            )
            
            # Generate next steps
            next_steps = self._generate_next_steps(variant_results, winner, config)
            
            # Create results
            end_time = datetime.utcnow()
            results = ExperimentResults(
                experiment_id=experiment_id,
                experiment_name=config.experiment_name,
                status=ExperimentStatus.COMPLETED,
                start_time=experiment["start_time"],
                end_time=end_time,
                duration=end_time - experiment["start_time"],
                variant_results=variant_results,
                winner=winner,
                statistical_summary=statistical_summary,
                business_impact=business_impact,
                recommendations=recommendations,
                next_steps=next_steps
            )
            
            # Store results
            experiment["results"] = results
            experiment["status"] = ExperimentStatus.COMPLETED
            experiment["end_time"] = end_time
            
            # Update experiment history
            if config.experiment_name not in self.experiment_history:
                self.experiment_history[config.experiment_name] = []
            self.experiment_history[config.experiment_name].append(results)
            
            self.logger.info(f"Completed experiment {config.experiment_name}, winner: {winner}")
            return results
            
        except Exception as e:
            if experiment_id in self.ml_experiments:
                self.ml_experiments[experiment_id]["status"] = ExperimentStatus.FAILED
            self.logger.error(f"Experiment {experiment_id} failed: {str(e)}")
            raise
    
    async def _evaluate_variants(
        self,
        model_variants: Dict[str, Callable],
        dataset: Dict[str, np.ndarray],
        config: ExperimentConfig,
        evaluation_metrics: Optional[List[str]] = None
    ) -> List[VariantResult]:
        """Evaluate all model variants"""
        
        X_test = dataset["X_test"]
        y_test = dataset["y_test"]
        
        variant_results = []
        
        for variant_name, model_func in model_variants.items():
            try:
                # Get predictions
                predictions = model_func(X_test)
                
                # Calculate metrics
                metrics = await self._calculate_variant_metrics(
                    predictions, y_test, config.primary_metric, config.secondary_metrics
                )
                
                # Add evaluation metrics if specified
                if evaluation_metrics:
                    eval_metrics = await self._calculate_evaluation_metrics(
                        predictions, y_test, evaluation_metrics
                    )
                    metrics.update(eval_metrics)
                
                # Calculate confidence intervals
                confidence_intervals = self._calculate_confidence_intervals(
                    predictions, y_test, metrics, config.confidence_level
                )
                
                # Calculate sample size for this variant
                sample_size = int(len(X_test) * config.traffic_allocation.get(variant_name, 0))
                
                variant_result = VariantResult(
                    variant_id=str(uuid.uuid4()),
                    variant_name=variant_name,
                    sample_size=sample_size,
                    metrics=metrics,
                    confidence_intervals=confidence_intervals,
                    statistical_significance={},  # Will be filled in statistical analysis
                    performance_data={
                        "prediction_latency": self._measure_prediction_latency(model_func, X_test[:100]),
                        "memory_usage": self._estimate_memory_usage(model_func),
                        "throughput": self._measure_throughput(model_func, X_test[:100])
                    }
                )
                
                variant_results.append(variant_result)
                
            except Exception as e:
                self.logger.error(f"Failed to evaluate variant {variant_name}: {str(e)}")
                continue
        
        return variant_results
    
    async def _calculate_variant_metrics(
        self,
        predictions: np.ndarray,
        y_true: np.ndarray,
        primary_metric: MetricType,
        secondary_metrics: List[MetricType]
    ) -> Dict[str, float]:
        """Calculate metrics for a variant"""
        
        metrics = {}
        
        # Calculate primary metric
        if primary_metric == MetricType.ACCURACY:
            metrics["accuracy"] = float(np.mean(predictions == y_true))
        elif primary_metric == MetricType.EFFECTIVENESS:
            # Custom effectiveness metric (placeholder)
            metrics["effectiveness"] = float(np.mean(predictions == y_true) * 1.1)  # Weighted accuracy
        
        # Calculate secondary metrics
        for metric in secondary_metrics:
            if metric == MetricType.ACCURACY and "accuracy" not in metrics:
                metrics["accuracy"] = float(np.mean(predictions == y_true))
            elif metric == MetricType.PERFORMANCE:
                # Performance metric (placeholder)
                metrics["performance"] = float(np.mean(predictions == y_true) * 0.95)
            elif metric == MetricType.ENGAGEMENT:
                # Simulated engagement metric
                metrics["engagement"] = float(np.random.uniform(0.7, 0.9))
        
        # Additional ML metrics
        if len(np.unique(y_true)) == 2:  # Binary classification
            from sklearn.metrics import precision_score, recall_score, f1_score
            metrics["precision"] = float(precision_score(y_true, predictions, average='binary', zero_division=0))
            metrics["recall"] = float(recall_score(y_true, predictions, average='binary', zero_division=0))
            metrics["f1_score"] = float(f1_score(y_true, predictions, average='binary', zero_division=0))
        
        return metrics
    
    async def _calculate_evaluation_metrics(
        self,
        predictions: np.ndarray,
        y_true: np.ndarray,
        evaluation_metrics: List[str]
    ) -> Dict[str, float]:
        """Calculate additional evaluation metrics"""
        
        metrics = {}
        
        for metric_name in evaluation_metrics:
            if metric_name == "mse" and len(np.unique(y_true)) > 2:
                from sklearn.metrics import mean_squared_error
                metrics["mse"] = float(mean_squared_error(y_true, predictions))
            elif metric_name == "mae" and len(np.unique(y_true)) > 2:
                from sklearn.metrics import mean_absolute_error
                metrics["mae"] = float(mean_absolute_error(y_true, predictions))
            elif metric_name == "auc" and len(np.unique(y_true)) == 2:
                # Would need prediction probabilities for real AUC
                metrics["auc"] = float(np.random.uniform(0.6, 0.9))  # Placeholder
        
        return metrics
    
    def _calculate_confidence_intervals(
        self,
        predictions: np.ndarray,
        y_true: np.ndarray,
        metrics: Dict[str, float],
        confidence_level: float
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for metrics"""
        
        confidence_intervals = {}
        alpha = 1 - confidence_level
        
        for metric_name, metric_value in metrics.items():
            if metric_name in ["accuracy", "precision", "recall", "f1_score"]:
                # Binomial confidence interval for proportion-based metrics
                n = len(predictions)
                p = metric_value
                
                # Wilson score interval
                z = stats.norm.ppf(1 - alpha/2)
                denominator = 1 + z**2/n
                centre = (p + z**2/(2*n)) / denominator
                margin = z * np.sqrt((p*(1-p) + z**2/(4*n)) / n) / denominator
                
                lower = max(0, centre - margin)
                upper = min(1, centre + margin)
                
                confidence_intervals[metric_name] = (lower, upper)
            else:
                # Simple normal approximation for other metrics
                std_error = np.std([metric_value] * len(predictions)) / np.sqrt(len(predictions))
                margin = stats.norm.ppf(1 - alpha/2) * std_error
                confidence_intervals[metric_name] = (
                    metric_value - margin,
                    metric_value + margin
                )
        
        return confidence_intervals
    
    def _measure_prediction_latency(self, model_func: Callable, X_sample: np.ndarray) -> float:
        """Measure model prediction latency"""
        import time
        
        start_time = time.time()
        _ = model_func(X_sample)
        end_time = time.time()
        
        return (end_time - start_time) * 1000  # Convert to milliseconds
    
    def _estimate_memory_usage(self, model_func: Callable) -> float:
        """Estimate model memory usage (placeholder)"""
        # In practice, this would measure actual memory usage
        return float(np.random.uniform(100, 1000))  # MB
    
    def _measure_throughput(self, model_func: Callable, X_sample: np.ndarray) -> float:
        """Measure model throughput (predictions per second)"""
        import time
        
        start_time = time.time()
        for _ in range(10):  # Multiple runs for better estimate
            _ = model_func(X_sample)
        end_time = time.time()
        
        total_predictions = 10 * len(X_sample)
        total_time = end_time - start_time
        
        return total_predictions / total_time if total_time > 0 else 0
    
    async def _perform_statistical_analysis(
        self,
        variant_results: List[VariantResult],
        config: ExperimentConfig
    ) -> Dict[str, Any]:
        """Perform statistical analysis of experiment results"""
        
        if len(variant_results) < 2:
            return {"error": "Insufficient variants for statistical analysis"}
        
        # Compare variants pairwise
        comparisons = {}
        primary_metric = config.primary_metric.value if hasattr(config.primary_metric, 'value') else str(config.primary_metric)
        
        for i, variant_a in enumerate(variant_results):
            for j, variant_b in enumerate(variant_results):
                if i >= j:
                    continue
                
                comparison_key = f"{variant_a.variant_name}_vs_{variant_b.variant_name}"
                
                # Get primary metric values
                metric_a = variant_a.metrics.get(primary_metric, 0)
                metric_b = variant_b.metrics.get(primary_metric, 0)
                
                # Perform statistical test (simplified)
                # In practice, you'd use proper statistical tests based on data distribution
                effect_size = abs(metric_a - metric_b)
                
                # Simulate p-value based on effect size and sample sizes
                min_sample_size = min(variant_a.sample_size, variant_b.sample_size)
                
                if effect_size > 0.05 and min_sample_size > 100:
                    p_value = 0.01  # Significant
                elif effect_size > 0.02 and min_sample_size > 50:
                    p_value = 0.04  # Moderately significant
                else:
                    p_value = 0.15  # Not significant
                
                # Determine significance level
                if p_value < 0.01:
                    significance = StatisticalSignificance.HIGH
                elif p_value < 0.05:
                    significance = StatisticalSignificance.MODERATE
                elif p_value < 0.1:
                    significance = StatisticalSignificance.LOW
                else:
                    significance = StatisticalSignificance.NONE
                
                comparisons[comparison_key] = {
                    "metric_difference": metric_a - metric_b,
                    "effect_size": effect_size,
                    "p_value": p_value,
                    "significance": significance,
                    "winner": variant_a.variant_name if metric_a > metric_b else variant_b.variant_name
                }
                
                # Update variant statistical significance
                variant_a.statistical_significance[variant_b.variant_name] = significance
                variant_b.statistical_significance[variant_a.variant_name] = significance
        
        return {
            "comparisons": comparisons,
            "overall_significance": self._determine_overall_significance(comparisons),
            "sample_size_adequacy": all(v.sample_size >= config.min_sample_size for v in variant_results),
            "power_analysis": self._perform_power_analysis(variant_results, config)
        }
    
    def _determine_overall_significance(self, comparisons: Dict[str, Any]) -> StatisticalSignificance:
        """Determine overall experiment significance"""
        significance_levels = [comp["significance"] for comp in comparisons.values()]
        
        if any(sig == StatisticalSignificance.HIGH for sig in significance_levels):
            return StatisticalSignificance.HIGH
        elif any(sig == StatisticalSignificance.MODERATE for sig in significance_levels):
            return StatisticalSignificance.MODERATE
        elif any(sig == StatisticalSignificance.LOW for sig in significance_levels):
            return StatisticalSignificance.LOW
        else:
            return StatisticalSignificance.NONE
    
    def _perform_power_analysis(self, variant_results: List[VariantResult], config: ExperimentConfig) -> Dict[str, Any]:
        """Perform statistical power analysis"""
        
        # Simplified power analysis
        min_sample_size = min(v.sample_size for v in variant_results)
        target_power = config.statistical_power
        
        # Estimate achieved power based on sample size and effect size
        if min_sample_size >= config.min_sample_size:
            achieved_power = min(0.95, 0.5 + (min_sample_size / config.min_sample_size) * 0.4)
        else:
            achieved_power = 0.5 * (min_sample_size / config.min_sample_size)
        
        return {
            "target_power": target_power,
            "achieved_power": achieved_power,
            "power_adequate": achieved_power >= target_power,
            "recommended_sample_size": config.min_sample_size,
            "actual_min_sample_size": min_sample_size
        }
    
    def _determine_experiment_winner(
        self,
        variant_results: List[VariantResult],
        statistical_summary: Dict[str, Any]
    ) -> Optional[str]:
        """Determine experiment winner based on results"""
        
        if not variant_results:
            return None
        
        # Find variant with best primary metric
        best_variant = max(
            variant_results,
            key=lambda v: list(v.metrics.values())[0] if v.metrics else 0
        )
        
        # Check if winner is statistically significant
        comparisons = statistical_summary.get("comparisons", {})
        
        # Count significant wins for the best variant
        significant_wins = 0
        total_comparisons = 0
        
        for comparison_key, comparison in comparisons.items():
            if best_variant.variant_name in comparison_key:
                total_comparisons += 1
                if (comparison["winner"] == best_variant.variant_name and
                    comparison["significance"] in [StatisticalSignificance.HIGH, StatisticalSignificance.MODERATE]):
                    significant_wins += 1
        
        # Require at least 50% significant wins to declare a winner
        if total_comparisons > 0 and significant_wins / total_comparisons >= 0.5:
            return best_variant.variant_name
        
        return None  # No clear winner
    
    async def _analyze_business_impact(
        self,
        variant_results: List[VariantResult],
        config: ExperimentConfig
    ) -> Dict[str, Any]:
        """Analyze business impact of experiment results"""
        
        if not variant_results:
            return {}
        
        # Get baseline (first variant) and best variant
        baseline = variant_results[0]
        best_variant = max(
            variant_results,
            key=lambda v: list(v.metrics.values())[0] if v.metrics else 0
        )
        
        primary_metric = list(baseline.metrics.keys())[0] if baseline.metrics else "accuracy"
        baseline_value = baseline.metrics.get(primary_metric, 0)
        best_value = best_variant.metrics.get(primary_metric, 0)
        
        improvement = best_value - baseline_value
        relative_improvement = (improvement / baseline_value * 100) if baseline_value > 0 else 0
        
        # Estimate business impact (simplified)
        # In practice, this would use actual business metrics and conversion rates
        estimated_impact = {
            "metric_improvement": improvement,
            "relative_improvement_percent": relative_improvement,
            "confidence_level": "medium" if abs(relative_improvement) > 5 else "low",
            "estimated_value": f"${improvement * 1000:.2f}/month" if improvement > 0 else "No significant value",
            "risk_assessment": "low" if improvement > 0 else "medium"
        }
        
        return estimated_impact
    
    def _generate_experiment_recommendations(
        self,
        variant_results: List[VariantResult],
        statistical_summary: Dict[str, Any],
        winner: Optional[str]
    ) -> List[str]:
        """Generate experiment recommendations"""
        
        recommendations = []
        
        if winner:
            recommendations.append(f"Deploy {winner} to production - clear winner identified")
            recommendations.append("Monitor performance metrics closely after deployment")
        else:
            recommendations.append("No clear winner - consider running extended experiment")
            recommendations.append("Review experiment design and success criteria")
        
        if not statistical_summary.get("sample_size_adequacy", True):
            recommendations.append("Increase sample size for more reliable results")
        
        power_analysis = statistical_summary.get("power_analysis", {})
        if not power_analysis.get("power_adequate", True):
            recommendations.append("Increase statistical power through larger sample size")
        
        # Performance-based recommendations
        performance_variants = [
            (v.variant_name, v.performance_data.get("prediction_latency", float('inf')))
            for v in variant_results
        ]
        fastest_variant = min(performance_variants, key=lambda x: x[1])
        
        if fastest_variant[1] < 100:  # Less than 100ms
            recommendations.append(f"{fastest_variant[0]} shows best latency performance")
        
        return recommendations
    
    def _generate_next_steps(
        self,
        variant_results: List[VariantResult],
        winner: Optional[str],
        config: ExperimentConfig
    ) -> List[str]:
        """Generate next steps for experiment follow-up"""
        
        next_steps = []
        
        if winner:
            next_steps.extend([
                f"Prepare {winner} for production deployment",
                "Set up monitoring dashboards for the winning variant",
                "Plan gradual rollout strategy (e.g., 10%, 50%, 100%)",
                "Schedule follow-up analysis after 30 days"
            ])
        else:
            next_steps.extend([
                "Analyze why no clear winner emerged",
                "Consider testing different variants or parameters",
                "Review experiment methodology and metrics",
                "Plan follow-up experiment with refined approach"
            ])
        
        # Type-specific next steps
        if config.experiment_type == ExperimentType.MODEL_COMPARISON:
            next_steps.append("Consider ensemble methods combining best-performing models")
        elif config.experiment_type == ExperimentType.HYPERPARAMETER_TUNING:
            next_steps.append("Explore hyperparameter space around winning configuration")
        elif config.experiment_type == ExperimentType.FEATURE_TESTING:
            next_steps.append("Analyze feature importance in winning variant")
        
        return next_steps
    
    def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get current experiment status"""
        if experiment_id not in self.ml_experiments:
            return {"error": "Experiment not found"}
        
        experiment = self.ml_experiments[experiment_id]
        config = experiment["config"]
        
        status_info = {
            "experiment_id": experiment_id,
            "name": config.experiment_name,
            "status": experiment["status"],
            "created_at": experiment["created_at"].isoformat(),
            "type": config.experiment_type,
            "variants": [v["name"] for v in config.variants],
            "primary_metric": config.primary_metric
        }
        
        if experiment["status"] == ExperimentStatus.COMPLETED and experiment.get("results"):
            results = experiment["results"]
            status_info.update({
                "winner": results.winner,
                "duration": results.duration.total_seconds(),
                "statistical_significance": results.statistical_summary.get("overall_significance")
            })
        
        return status_info
    
    def get_experiment_history(self, experiment_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get experiment history"""
        if experiment_name:
            return [
                {
                    "experiment_id": result.experiment_id,
                    "name": result.experiment_name,
                    "status": result.status,
                    "winner": result.winner,
                    "duration": result.duration.total_seconds(),
                    "end_time": result.end_time.isoformat() if result.end_time else None
                }
                for result in self.experiment_history.get(experiment_name, [])
            ]
        else:
            # Return all experiments
            all_history = []
            for exp_name, results in self.experiment_history.items():
                all_history.extend([
                    {
                        "experiment_id": result.experiment_id,
                        "name": result.experiment_name,
                        "status": result.status,
                        "winner": result.winner,
                        "duration": result.duration.total_seconds(),
                        "end_time": result.end_time.isoformat() if result.end_time else None
                    }
                    for result in results
                ])
            return all_history