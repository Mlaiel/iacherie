"""
Model Comparison Analyzer - Comprehensive Model Comparison with Statistical Significance
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade model comparison and analysis with statistical significance testing,
performance benchmarking, and comprehensive evaluation metrics for creator domains.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
from scipy import stats
from itertools import combinations
import uuid

@dataclass
class ModelMetrics:
    """Comprehensive model performance metrics."""
    model_id: str
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    latency_ms: float
    throughput_rps: float
    memory_usage_mb: float
    inference_cost: float
    training_time_hours: float
    model_size_mb: float
    confidence_score: float
    domain_specific_metrics: Dict[str, float]
    evaluation_timestamp: datetime

@dataclass
class ComparisonResult:
    """Statistical comparison result between models."""
    comparison_id: str
    model_a: str
    model_b: str
    metric_comparisons: Dict[str, Dict[str, Any]]
    statistical_significance: Dict[str, bool]
    effect_sizes: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]
    practical_significance: Dict[str, bool]
    overall_winner: Optional[str]
    recommendation: str
    comparison_timestamp: datetime

@dataclass
class BenchmarkSuite:
    """Benchmark test suite for model evaluation."""
    suite_id: str
    suite_name: str
    domain: str  # "musician", "blogger", "photographer", "influencer"
    test_datasets: List[Dict[str, Any]]
    evaluation_metrics: List[str]
    performance_requirements: Dict[str, float]
    test_scenarios: List[Dict[str, Any]]
    created_at: datetime

class ModelComparisonAnalyzer:
    """
    Advanced model comparison analyzer with statistical rigor.
    
    Features:
    - Statistical significance testing with multiple comparison correction
    - Effect size calculation and practical significance assessment
    - Comprehensive performance benchmarking
    - Creator-domain specific evaluation metrics
    - A/B testing framework integration
    - Multi-dimensional model comparison (accuracy, latency, cost)
    - Confidence interval estimation
    - Performance regression detection
    """
    
    def __init__(self, comparison_cache_dir: str = "comparison_cache/"):
        self.logger = logging.getLogger(__name__)
        self.comparison_cache_dir = Path(comparison_cache_dir)
        self.comparison_cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Model metrics storage
        self.model_metrics = {}
        self.comparison_history = []
        self.benchmark_suites = {}
        
        # Statistical testing configuration
        self.significance_level = 0.05
        self.multiple_comparison_correction = "holm"  # "holm", "bonferroni", "fdr"
        self.min_sample_size = 30
        self.bootstrap_iterations = 1000
        
        # Domain-specific evaluation frameworks
        self.domain_evaluation_frameworks = {
            "musician": {
                "primary_metrics": ["genre_accuracy", "tempo_detection", "mood_classification"],
                "performance_metrics": ["latency_ms", "throughput_rps"],
                "business_metrics": ["user_engagement", "recommendation_ctr", "retention_rate"],
                "quality_thresholds": {
                    "genre_accuracy": 0.90,
                    "tempo_detection": 0.85,
                    "mood_classification": 0.80,
                    "latency_ms": 150.0,
                    "user_engagement": 0.75
                }
            },
            "blogger": {
                "primary_metrics": ["topic_classification", "sentiment_accuracy", "readability_score"],
                "performance_metrics": ["processing_speed", "memory_efficiency"],
                "business_metrics": ["content_engagement", "seo_improvement", "click_through_rate"],
                "quality_thresholds": {
                    "topic_classification": 0.92,
                    "sentiment_accuracy": 0.88,
                    "readability_score": 0.80,
                    "processing_speed": 100.0,
                    "content_engagement": 0.70
                }
            },
            "photographer": {
                "primary_metrics": ["aesthetic_score", "composition_analysis", "style_detection"],
                "performance_metrics": ["image_processing_time", "gpu_utilization"],
                "business_metrics": ["portfolio_performance", "client_satisfaction", "sales_conversion"],
                "quality_thresholds": {
                    "aesthetic_score": 0.85,
                    "composition_analysis": 0.80,
                    "style_detection": 0.88,
                    "image_processing_time": 500.0,
                    "portfolio_performance": 0.75
                }
            },
            "influencer": {
                "primary_metrics": ["engagement_prediction", "viral_potential", "brand_alignment"],
                "performance_metrics": ["multimodal_processing", "scalability"],
                "business_metrics": ["follower_growth", "conversion_rate", "brand_partnerships"],
                "quality_thresholds": {
                    "engagement_prediction": 0.80,
                    "viral_potential": 0.75,
                    "brand_alignment": 0.85,
                    "multimodal_processing": 200.0,
                    "follower_growth": 0.70
                }
            }
        }
        
        # Effect size interpretation
        self.effect_size_interpretation = {
            "small": (0.0, 0.2),
            "medium": (0.2, 0.5),
            "large": (0.5, 0.8),
            "very_large": (0.8, float('inf'))
        }
        
    async def evaluate_model(
        self,
        model_id: str,
        model_version: str,
        evaluation_data: Dict[str, Any],
        benchmark_suite_id: Optional[str] = None,
        domain: str = "general"
    ) -> ModelMetrics:
        """Evaluate a model comprehensively."""
        try:
            # Run benchmark suite if specified
            if benchmark_suite_id and benchmark_suite_id in self.benchmark_suites:
                benchmark_results = await self._run_benchmark_suite(
                    model_id, model_version, benchmark_suite_id, evaluation_data
                )
            else:
                benchmark_results = await self._run_standard_evaluation(
                    model_id, model_version, evaluation_data, domain
                )
            
            # Extract core metrics
            core_metrics = await self._extract_core_metrics(benchmark_results)
            
            # Calculate domain-specific metrics
            domain_metrics = await self._calculate_domain_metrics(
                benchmark_results, domain
            )
            
            # Measure performance characteristics
            performance_metrics = await self._measure_performance_characteristics(
                model_id, model_version, evaluation_data
            )
            
            # Create comprehensive metrics object
            model_metrics = ModelMetrics(
                model_id=model_id,
                model_version=model_version,
                accuracy=core_metrics.get("accuracy", 0.0),
                precision=core_metrics.get("precision", 0.0),
                recall=core_metrics.get("recall", 0.0),
                f1_score=core_metrics.get("f1_score", 0.0),
                auc_roc=core_metrics.get("auc_roc", 0.0),
                latency_ms=performance_metrics.get("latency_ms", 0.0),
                throughput_rps=performance_metrics.get("throughput_rps", 0.0),
                memory_usage_mb=performance_metrics.get("memory_usage_mb", 0.0),
                inference_cost=performance_metrics.get("inference_cost", 0.0),
                training_time_hours=performance_metrics.get("training_time_hours", 0.0),
                model_size_mb=performance_metrics.get("model_size_mb", 0.0),
                confidence_score=core_metrics.get("confidence_score", 0.0),
                domain_specific_metrics=domain_metrics,
                evaluation_timestamp=datetime.now()
            )
            
            # Store metrics
            metrics_key = f"{model_id}_{model_version}"
            self.model_metrics[metrics_key] = model_metrics
            
            # Save metrics to cache
            await self._save_model_metrics(model_metrics)
            
            self.logger.info(f"Model evaluation completed: {model_id} v{model_version} "
                           f"(accuracy: {model_metrics.accuracy:.3f})")
            
            return model_metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            raise
    
    async def compare_models(
        self,
        model_ids: List[str],
        comparison_metrics: List[str] = None,
        statistical_tests: List[str] = None,
        domain: str = "general"
    ) -> List[ComparisonResult]:
        """Compare multiple models with statistical significance testing."""
        try:
            if len(model_ids) < 2:
                raise ValueError("At least 2 models required for comparison")
            
            # Get model metrics
            model_metrics_list = []
            for model_id in model_ids:
                metrics = await self._get_latest_model_metrics(model_id)
                if metrics:
                    model_metrics_list.append(metrics)
                else:
                    self.logger.warning(f"No metrics found for model: {model_id}")
            
            if len(model_metrics_list) < 2:
                raise ValueError("Insufficient model metrics for comparison")
            
            # Default comparison metrics
            if comparison_metrics is None:
                comparison_metrics = ["accuracy", "f1_score", "latency_ms", "memory_usage_mb"]
            
            # Default statistical tests
            if statistical_tests is None:
                statistical_tests = ["t_test", "mann_whitney", "bootstrap"]
            
            # Perform pairwise comparisons
            comparison_results = []
            
            for model_a, model_b in combinations(model_metrics_list, 2):
                comparison = await self._perform_pairwise_comparison(
                    model_a, model_b, comparison_metrics, statistical_tests, domain
                )
                comparison_results.append(comparison)
            
            # Apply multiple comparison correction
            corrected_results = await self._apply_multiple_comparison_correction(
                comparison_results
            )
            
            # Store comparison results
            self.comparison_history.extend(corrected_results)
            
            # Save comparison results
            for result in corrected_results:
                await self._save_comparison_result(result)
            
            self.logger.info(f"Model comparison completed: {len(corrected_results)} pairwise comparisons")
            return corrected_results
            
        except Exception as e:
            self.logger.error(f"Error comparing models: {e}")
            raise
    
    async def run_ab_test_analysis(
        self,
        model_a_id: str,
        model_b_id: str,
        test_data: Dict[str, Any],
        test_duration_days: int = 14,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """Run A/B test analysis between two models."""
        try:
            # Simulate A/B test data collection
            ab_test_data = await self._simulate_ab_test_data(
                model_a_id, model_b_id, test_data, test_duration_days
            )
            
            # Calculate conversion rates and metrics
            model_a_metrics = await self._calculate_ab_test_metrics(
                ab_test_data["model_a_data"]
            )
            model_b_metrics = await self._calculate_ab_test_metrics(
                ab_test_data["model_b_data"]
            )
            
            # Perform statistical tests
            statistical_results = await self._perform_ab_test_statistics(
                ab_test_data, confidence_level
            )
            
            # Calculate practical significance
            practical_significance = await self._assess_practical_significance(
                model_a_metrics, model_b_metrics, ab_test_data["domain"]
            )
            
            # Power analysis
            power_analysis = await self._perform_power_analysis(
                ab_test_data, statistical_results
            )
            
            # Generate recommendations
            recommendations = await self._generate_ab_test_recommendations(
                model_a_metrics, model_b_metrics, statistical_results, practical_significance
            )
            
            ab_test_result = {
                "test_id": f"ab_test_{model_a_id}_vs_{model_b_id}_{int(time.time())}",
                "model_a": {
                    "model_id": model_a_id,
                    "metrics": model_a_metrics,
                    "sample_size": len(ab_test_data["model_a_data"])
                },
                "model_b": {
                    "model_id": model_b_id,
                    "metrics": model_b_metrics,
                    "sample_size": len(ab_test_data["model_b_data"])
                },
                "statistical_results": statistical_results,
                "practical_significance": practical_significance,
                "power_analysis": power_analysis,
                "recommendations": recommendations,
                "test_duration_days": test_duration_days,
                "confidence_level": confidence_level,
                "test_completion_date": datetime.now().isoformat()
            }
            
            # Save A/B test results
            await self._save_ab_test_results(ab_test_result)
            
            self.logger.info(f"A/B test analysis completed: {model_a_id} vs {model_b_id}")
            return ab_test_result
            
        except Exception as e:
            self.logger.error(f"Error in A/B test analysis: {e}")
            raise
    
    async def create_benchmark_suite(
        self,
        suite_name: str,
        domain: str,
        test_specifications: Dict[str, Any]
    ) -> BenchmarkSuite:
        """Create a comprehensive benchmark suite for model evaluation."""
        try:
            suite_id = f"benchmark_{domain}_{int(time.time())}"
            
            # Generate test datasets
            test_datasets = await self._generate_test_datasets(domain, test_specifications)
            
            # Define evaluation metrics
            domain_framework = self.domain_evaluation_frameworks.get(domain, {})
            evaluation_metrics = (
                domain_framework.get("primary_metrics", []) +
                domain_framework.get("performance_metrics", []) +
                domain_framework.get("business_metrics", [])
            )
            
            # Set performance requirements
            performance_requirements = domain_framework.get("quality_thresholds", {})
            
            # Create test scenarios
            test_scenarios = await self._create_test_scenarios(domain, test_specifications)
            
            benchmark_suite = BenchmarkSuite(
                suite_id=suite_id,
                suite_name=suite_name,
                domain=domain,
                test_datasets=test_datasets,
                evaluation_metrics=evaluation_metrics,
                performance_requirements=performance_requirements,
                test_scenarios=test_scenarios,
                created_at=datetime.now()
            )
            
            # Store benchmark suite
            self.benchmark_suites[suite_id] = benchmark_suite
            
            # Save benchmark suite
            await self._save_benchmark_suite(benchmark_suite)
            
            self.logger.info(f"Benchmark suite created: {suite_id} for {domain}")
            return benchmark_suite
            
        except Exception as e:
            self.logger.error(f"Error creating benchmark suite: {e}")
            raise
    
    async def _perform_pairwise_comparison(
        self,
        model_a: ModelMetrics,
        model_b: ModelMetrics,
        comparison_metrics: List[str],
        statistical_tests: List[str],
        domain: str
    ) -> ComparisonResult:
        """Perform statistical comparison between two models."""
        try:
            comparison_id = f"comp_{model_a.model_id}_vs_{model_b.model_id}_{int(time.time())}"
            
            metric_comparisons = {}
            statistical_significance = {}
            effect_sizes = {}
            confidence_intervals = {}
            practical_significance = {}
            
            for metric in comparison_metrics:
                # Get metric values
                value_a = getattr(model_a, metric, model_a.domain_specific_metrics.get(metric, 0.0))
                value_b = getattr(model_b, metric, model_b.domain_specific_metrics.get(metric, 0.0))
                
                # Generate sample data for statistical testing (mock implementation)
                samples_a = np.random.normal(value_a, value_a * 0.1, self.min_sample_size)
                samples_b = np.random.normal(value_b, value_b * 0.1, self.min_sample_size)
                
                # Perform statistical tests
                test_results = {}
                
                if "t_test" in statistical_tests:
                    t_stat, p_value = stats.ttest_ind(samples_a, samples_b)
                    test_results["t_test"] = {"statistic": t_stat, "p_value": p_value}
                
                if "mann_whitney" in statistical_tests:
                    u_stat, p_value = stats.mannwhitneyu(samples_a, samples_b, alternative='two-sided')
                    test_results["mann_whitney"] = {"statistic": u_stat, "p_value": p_value}
                
                if "bootstrap" in statistical_tests:
                    bootstrap_result = await self._bootstrap_comparison(samples_a, samples_b)
                    test_results["bootstrap"] = bootstrap_result
                
                metric_comparisons[metric] = {
                    "model_a_value": value_a,
                    "model_b_value": value_b,
                    "difference": value_b - value_a,
                    "percent_change": ((value_b - value_a) / value_a * 100) if value_a != 0 else 0,
                    "statistical_tests": test_results
                }
                
                # Determine statistical significance (using t-test p-value)
                p_value = test_results.get("t_test", {}).get("p_value", 1.0)
                statistical_significance[metric] = p_value < self.significance_level
                
                # Calculate effect size (Cohen's d)
                pooled_std = np.sqrt((np.var(samples_a) + np.var(samples_b)) / 2)
                effect_size = (np.mean(samples_b) - np.mean(samples_a)) / pooled_std if pooled_std > 0 else 0
                effect_sizes[metric] = effect_size
                
                # Calculate confidence interval for difference
                diff = np.mean(samples_b) - np.mean(samples_a)
                se_diff = np.sqrt(np.var(samples_a)/len(samples_a) + np.var(samples_b)/len(samples_b))
                margin_of_error = stats.t.ppf(0.975, len(samples_a) + len(samples_b) - 2) * se_diff
                confidence_intervals[metric] = (diff - margin_of_error, diff + margin_of_error)
                
                # Assess practical significance
                practical_significance[metric] = await self._assess_practical_significance_metric(
                    metric, value_a, value_b, domain
                )
            
            # Determine overall winner
            overall_winner = await self._determine_overall_winner(
                model_a, model_b, metric_comparisons, domain
            )
            
            # Generate recommendation
            recommendation = await self._generate_comparison_recommendation(
                model_a, model_b, metric_comparisons, statistical_significance, 
                practical_significance, overall_winner
            )
            
            return ComparisonResult(
                comparison_id=comparison_id,
                model_a=f"{model_a.model_id}_{model_a.model_version}",
                model_b=f"{model_b.model_id}_{model_b.model_version}",
                metric_comparisons=metric_comparisons,
                statistical_significance=statistical_significance,
                effect_sizes=effect_sizes,
                confidence_intervals=confidence_intervals,
                practical_significance=practical_significance,
                overall_winner=overall_winner,
                recommendation=recommendation,
                comparison_timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in pairwise comparison: {e}")
            raise
    
    async def _bootstrap_comparison(
        self, 
        samples_a: np.ndarray, 
        samples_b: np.ndarray
    ) -> Dict[str, Any]:
        """Perform bootstrap comparison between two samples."""
        try:
            bootstrap_diffs = []
            
            for _ in range(self.bootstrap_iterations):
                # Bootstrap resample
                resample_a = np.random.choice(samples_a, size=len(samples_a), replace=True)
                resample_b = np.random.choice(samples_b, size=len(samples_b), replace=True)
                
                # Calculate difference in means
                diff = np.mean(resample_b) - np.mean(resample_a)
                bootstrap_diffs.append(diff)
            
            bootstrap_diffs = np.array(bootstrap_diffs)
            
            # Calculate confidence interval
            ci_lower = np.percentile(bootstrap_diffs, 2.5)
            ci_upper = np.percentile(bootstrap_diffs, 97.5)
            
            # Calculate p-value (proportion of bootstrap samples with difference <= 0)
            p_value = np.mean(bootstrap_diffs <= 0) * 2  # Two-tailed test
            
            return {
                "mean_difference": np.mean(bootstrap_diffs),
                "confidence_interval": (ci_lower, ci_upper),
                "p_value": min(p_value, 1.0),
                "bootstrap_iterations": self.bootstrap_iterations
            }
            
        except Exception as e:
            self.logger.error(f"Error in bootstrap comparison: {e}")
            return {}
    
    async def _run_standard_evaluation(
        self,
        model_id: str,
        model_version: str,
        evaluation_data: Dict[str, Any],
        domain: str
    ) -> Dict[str, Any]:
        """Run standard model evaluation."""
        # Simulate evaluation process
        await asyncio.sleep(0.1)
        
        # Mock evaluation results
        base_accuracy = 0.8 + np.random.uniform(-0.1, 0.1)
        
        return {
            "accuracy": base_accuracy,
            "precision": base_accuracy + np.random.uniform(-0.05, 0.05),
            "recall": base_accuracy + np.random.uniform(-0.05, 0.05),
            "f1_score": base_accuracy + np.random.uniform(-0.03, 0.03),
            "auc_roc": base_accuracy + np.random.uniform(0.0, 0.1),
            "confidence_score": np.random.uniform(0.7, 0.95),
            "evaluation_samples": evaluation_data.get("sample_count", 1000),
            "domain": domain
        }

# Example usage and testing
async def main():
    """Example usage of ModelComparisonAnalyzer."""
    analyzer = ModelComparisonAnalyzer()
    
    # Create benchmark suite for musicians
    benchmark_suite = await analyzer.create_benchmark_suite(
        "Musician AI Benchmark v1.0",
        "musician",
        {
            "test_types": ["genre_classification", "tempo_detection", "mood_analysis"],
            "dataset_sizes": {"train": 10000, "test": 2000, "validation": 1000},
            "evaluation_criteria": ["accuracy", "latency", "user_satisfaction"]
        }
    )
    
    print(f"Benchmark suite created: {benchmark_suite.suite_id}")
    
    # Evaluate multiple models
    model_ids = ["musician-classifier-v1", "musician-classifier-v2", "musician-classifier-v3"]
    evaluation_data = {"sample_count": 2000, "domain": "musician"}
    
    model_metrics = []
    for i, model_id in enumerate(model_ids):
        metrics = await analyzer.evaluate_model(
            model_id, f"v{i+1}.0", evaluation_data, benchmark_suite.suite_id, "musician"
        )
        model_metrics.append(metrics)
        print(f"Evaluated {model_id}: accuracy={metrics.accuracy:.3f}, latency={metrics.latency_ms:.1f}ms")
    
    # Compare models
    comparison_results = await analyzer.compare_models(
        model_ids, 
        ["accuracy", "f1_score", "latency_ms"],
        ["t_test", "bootstrap"],
        "musician"
    )
    
    print(f"\nModel comparison results ({len(comparison_results)} comparisons):")
    for result in comparison_results:
        print(f"- {result.model_a} vs {result.model_b}")
        print(f"  Winner: {result.overall_winner}")
        print(f"  Recommendation: {result.recommendation}")
        
        # Show significant differences
        significant_metrics = [
            metric for metric, is_sig in result.statistical_significance.items() if is_sig
        ]
        if significant_metrics:
            print(f"  Significant differences in: {', '.join(significant_metrics)}")
        print()
    
    # Run A/B test
    ab_result = await analyzer.run_ab_test_analysis(
        model_ids[0], model_ids[1], 
        {"domain": "musician", "user_segments": ["new_users", "premium_users"]},
        test_duration_days=7
    )
    
    print(f"A/B test completed: {ab_result['test_id']}")
    print(f"Winner: {ab_result['recommendations']['recommended_model']}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())