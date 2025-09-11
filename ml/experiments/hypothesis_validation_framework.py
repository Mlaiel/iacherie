#!/usr/bin/env python3
"""
🔬 Hypothesis Validation Framework - Statistical ML Research Infrastructure

Advanced statistical framework for ML experiment hypothesis validation with rigorous
statistical testing, Bayesian analysis, and creator-specific experimental design.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

Architecture Integration:
- Integrates with ExperimentTrackingSystem for rigorous A/B testing
- Provides statistical validation for model performance claims
- Supports Bayesian hypothesis testing for creator-specific metrics
- Automated statistical reporting with confidence intervals
- Multi-armed bandit testing for revenue optimization
"""

import asyncio
import logging
import time
import warnings
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, kruskal, friedmanchisquare
from scipy.special import betaln
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class HypothesisType(Enum):
    """Types of hypotheses."""
    ONE_SAMPLE = "one_sample"
    TWO_SAMPLE = "two_sample"
    PAIRED = "paired"
    MULTI_SAMPLE = "multi_sample"
    PROPORTION = "proportion"
    CORRELATION = "correlation"
    REGRESSION = "regression"
    BAYESIAN = "bayesian"


class StatisticalTest(Enum):
    """Statistical test types."""
    T_TEST = "t_test"
    WELCH_T_TEST = "welch_t_test"
    MANN_WHITNEY = "mann_whitney"
    WILCOXON = "wilcoxon"
    KRUSKAL_WALLIS = "kruskal_wallis"
    FRIEDMAN = "friedman"
    CHI_SQUARE = "chi_square"
    FISHER_EXACT = "fisher_exact"
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    BOOTSTRAP = "bootstrap"
    PERMUTATION = "permutation"
    BAYESIAN_T_TEST = "bayesian_t_test"


class EffectSizeMetric(Enum):
    """Effect size metrics."""
    COHENS_D = "cohens_d"
    GLASS_DELTA = "glass_delta"
    HEDGES_G = "hedges_g"
    CORRELATION_R = "correlation_r"
    ETA_SQUARED = "eta_squared"
    OMEGA_SQUARED = "omega_squared"
    CRAMER_V = "cramer_v"


@dataclass
class HypothesisDefinition:
    """Definition of a statistical hypothesis."""
    hypothesis_id: str
    name: str
    description: str
    hypothesis_type: HypothesisType
    null_hypothesis: str
    alternative_hypothesis: str
    
    # Statistical parameters
    alpha: float = 0.05
    power: float = 0.8
    effect_size: Optional[float] = None
    alternative: str = "two-sided"  # "two-sided", "greater", "less"
    
    # Creator-specific context
    creator_type: Optional[str] = None
    content_type: Optional[str] = None
    business_metric: Optional[str] = None
    
    # Experimental design
    minimum_sample_size: Optional[int] = None
    maximum_duration_days: Optional[int] = None
    stratification_variables: List[str] = field(default_factory=list)


@dataclass
class StatisticalResult:
    """Results of statistical test."""
    test_statistic: float
    p_value: float
    confidence_interval: Tuple[float, float]
    effect_size: Optional[float] = None
    effect_size_ci: Optional[Tuple[float, float]] = None
    power: Optional[float] = None
    
    # Test-specific results
    degrees_of_freedom: Optional[float] = None
    critical_value: Optional[float] = None
    
    # Interpretation
    is_significant: bool = False
    practical_significance: Optional[bool] = None
    interpretation: str = ""


@dataclass
class BayesianResult:
    """Results of Bayesian analysis."""
    bayes_factor: float
    posterior_mean: float
    posterior_std: float
    credible_interval: Tuple[float, float]
    probability_of_direction: float
    probability_of_effect: float
    
    # Evidence interpretation
    evidence_strength: str = ""
    interpretation: str = ""


@dataclass
class ExperimentValidation:
    """Complete experiment validation results."""
    experiment_id: str
    hypothesis: HypothesisDefinition
    statistical_result: StatisticalResult
    bayesian_result: Optional[BayesianResult] = None
    
    # Data quality checks
    data_quality_score: float = 0.0
    outlier_percentage: float = 0.0
    missing_data_percentage: float = 0.0
    
    # Sample size analysis
    achieved_sample_size: int = 0
    recommended_sample_size: int = 0
    power_analysis: Dict[str, float] = field(default_factory=dict)
    
    # Business impact
    business_significance: Optional[Dict[str, Any]] = None
    roi_estimate: Optional[float] = None
    confidence_in_results: float = 0.0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


class HypothesisValidationFramework:
    """
    Advanced statistical framework for ML experiment validation.
    
    Features:
    - Rigorous statistical hypothesis testing
    - Bayesian analysis with evidence quantification
    - Power analysis and sample size calculation
    - Effect size estimation with confidence intervals
    - Creator-specific experimental design
    - Automated statistical reporting
    - Business impact assessment
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the hypothesis validation framework."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Validation tracking
        self.hypotheses: Dict[str, HypothesisDefinition] = {}
        self.validations: Dict[str, ExperimentValidation] = {}
        self.validation_history: List[Dict[str, Any]] = []
        
        # Statistical configuration
        self.default_alpha = self.config.get("default_alpha", 0.05)
        self.default_power = self.config.get("default_power", 0.8)
        self.bootstrap_iterations = self.config.get("bootstrap_iterations", 10000)
        self.bayesian_samples = self.config.get("bayesian_samples", 10000)
        
        # Creator-specific configurations
        self.creator_configurations = self._initialize_creator_configurations()
        
        # Effect size interpretation thresholds
        self.effect_size_thresholds = {
            "small": 0.2,
            "medium": 0.5,
            "large": 0.8
        }
        
        self.logger.info("Hypothesis Validation Framework initialized")
    
    def _initialize_creator_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize creator-specific statistical configurations."""
        return {
            "musician": {
                "primary_metrics": ["engagement_rate", "listening_time", "revenue_per_track"],
                "typical_effect_sizes": {"engagement_rate": 0.15, "revenue": 0.25},
                "seasonal_adjustment": True,
                "minimum_sample_size": 1000,
                "recommended_test_duration": 14  # days
            },
            "blogger": {
                "primary_metrics": ["page_views", "time_on_page", "conversion_rate"],
                "typical_effect_sizes": {"page_views": 0.10, "conversion": 0.20},
                "seasonal_adjustment": False,
                "minimum_sample_size": 2000,
                "recommended_test_duration": 21
            },
            "photographer": {
                "primary_metrics": ["image_views", "purchase_rate", "aesthetic_score"],
                "typical_effect_sizes": {"views": 0.12, "purchases": 0.30},
                "seasonal_adjustment": True,
                "minimum_sample_size": 800,
                "recommended_test_duration": 10
            },
            "influencer": {
                "primary_metrics": ["follower_growth", "engagement_rate", "brand_partnerships"],
                "typical_effect_sizes": {"growth": 0.18, "engagement": 0.22},
                "seasonal_adjustment": True,
                "minimum_sample_size": 1500,
                "recommended_test_duration": 28
            }
        }
    
    async def define_hypothesis(self, hypothesis: HypothesisDefinition) -> str:
        """Define a new hypothesis for validation."""
        try:
            # Validate hypothesis definition
            if not await self._validate_hypothesis_definition(hypothesis):
                raise ValueError("Invalid hypothesis definition")
            
            # Apply creator-specific optimizations
            if hypothesis.creator_type:
                hypothesis = await self._optimize_for_creator_type(hypothesis)
            
            # Calculate recommended sample size
            if not hypothesis.minimum_sample_size:
                hypothesis.minimum_sample_size = await self._calculate_sample_size(hypothesis)
            
            # Store hypothesis
            self.hypotheses[hypothesis.hypothesis_id] = hypothesis
            
            self.logger.info(f"Hypothesis '{hypothesis.name}' defined with ID: {hypothesis.hypothesis_id}")
            
            return hypothesis.hypothesis_id
            
        except Exception as e:
            self.logger.error(f"Failed to define hypothesis: {e}")
            raise
    
    async def _validate_hypothesis_definition(self, hypothesis: HypothesisDefinition) -> bool:
        """Validate hypothesis definition."""
        try:
            # Check required fields
            if not all([
                hypothesis.hypothesis_id,
                hypothesis.name,
                hypothesis.null_hypothesis,
                hypothesis.alternative_hypothesis
            ]):
                return False
            
            # Check alpha value
            if not 0 < hypothesis.alpha < 1:
                return False
            
            # Check power value
            if not 0 < hypothesis.power < 1:
                return False
            
            # Check effect size if provided
            if hypothesis.effect_size is not None and hypothesis.effect_size <= 0:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Hypothesis validation failed: {e}")
            return False
    
    async def _optimize_for_creator_type(self, hypothesis: HypothesisDefinition) -> HypothesisDefinition:
        """Optimize hypothesis for specific creator type."""
        try:
            creator_type = hypothesis.creator_type
            if creator_type not in self.creator_configurations:
                return hypothesis
            
            config = self.creator_configurations[creator_type]
            
            # Apply creator-specific configurations
            if not hypothesis.minimum_sample_size:
                hypothesis.minimum_sample_size = config["minimum_sample_size"]
            
            if not hypothesis.maximum_duration_days:
                hypothesis.maximum_duration_days = config["recommended_test_duration"]
            
            # Set effect size if not specified
            if not hypothesis.effect_size and hypothesis.business_metric in config["typical_effect_sizes"]:
                hypothesis.effect_size = config["typical_effect_sizes"][hypothesis.business_metric]
            
            # Add stratification variables for creator type
            if "user_segment" not in hypothesis.stratification_variables:
                hypothesis.stratification_variables.append("user_segment")
            
            return hypothesis
            
        except Exception as e:
            self.logger.error(f"Creator type optimization failed: {e}")
            return hypothesis
    
    async def _calculate_sample_size(self, hypothesis: HypothesisDefinition) -> int:
        """Calculate required sample size for hypothesis test."""
        try:
            alpha = hypothesis.alpha
            power = hypothesis.power
            effect_size = hypothesis.effect_size or 0.5  # Default medium effect
            
            # Sample size calculation based on hypothesis type
            if hypothesis.hypothesis_type == HypothesisType.TWO_SAMPLE:
                # Two-sample t-test sample size
                z_alpha = stats.norm.ppf(1 - alpha/2)
                z_beta = stats.norm.ppf(power)
                
                sample_size = 2 * ((z_alpha + z_beta) / effect_size) ** 2
                
            elif hypothesis.hypothesis_type == HypothesisType.PROPORTION:
                # Proportion test sample size
                p1 = 0.5  # Baseline proportion (estimated)
                p2 = p1 + effect_size
                
                p_pooled = (p1 + p2) / 2
                z_alpha = stats.norm.ppf(1 - alpha/2)
                z_beta = stats.norm.ppf(power)
                
                sample_size = (
                    (z_alpha * np.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                     z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
                ) / (p1 - p2) ** 2
                
            else:
                # Default conservative estimate
                sample_size = 1000
            
            # Apply safety margin
            sample_size = int(sample_size * 1.2)  # 20% safety margin
            
            # Apply creator-specific minimums
            if hypothesis.creator_type in self.creator_configurations:
                min_size = self.creator_configurations[hypothesis.creator_type]["minimum_sample_size"]
                sample_size = max(sample_size, min_size)
            
            return max(sample_size, 100)  # Absolute minimum
            
        except Exception as e:
            self.logger.error(f"Sample size calculation failed: {e}")
            return 1000  # Fallback
    
    async def validate_experiment(self,
                                experiment_id: str,
                                hypothesis_id: str,
                                data: Dict[str, Any],
                                include_bayesian: bool = True) -> ExperimentValidation:
        """Validate experiment results against hypothesis."""
        try:
            if hypothesis_id not in self.hypotheses:
                raise ValueError(f"Hypothesis {hypothesis_id} not found")
            
            hypothesis = self.hypotheses[hypothesis_id]
            
            self.logger.info(f"Validating experiment {experiment_id} against hypothesis {hypothesis_id}")
            
            # Data quality assessment
            data_quality = await self._assess_data_quality(data)
            
            # Extract experimental data
            experimental_data = await self._extract_experimental_data(data, hypothesis)
            
            # Perform statistical tests
            statistical_result = await self._perform_statistical_test(experimental_data, hypothesis)
            
            # Bayesian analysis if requested
            bayesian_result = None
            if include_bayesian:
                bayesian_result = await self._perform_bayesian_analysis(experimental_data, hypothesis)
            
            # Power analysis
            power_analysis = await self._perform_power_analysis(experimental_data, hypothesis)
            
            # Business impact assessment
            business_impact = await self._assess_business_impact(experimental_data, hypothesis)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                statistical_result, bayesian_result, hypothesis, experimental_data
            )
            
            # Create validation result
            validation = ExperimentValidation(
                experiment_id=experiment_id,
                hypothesis=hypothesis,
                statistical_result=statistical_result,
                bayesian_result=bayesian_result,
                data_quality_score=data_quality["quality_score"],
                outlier_percentage=data_quality["outlier_percentage"],
                missing_data_percentage=data_quality["missing_percentage"],
                achieved_sample_size=len(experimental_data.get("control", [])) + len(experimental_data.get("treatment", [])),
                recommended_sample_size=hypothesis.minimum_sample_size or 1000,
                power_analysis=power_analysis,
                business_significance=business_impact,
                recommendations=recommendations["statistical"],
                next_steps=recommendations["next_steps"]
            )
            
            # Calculate confidence in results
            validation.confidence_in_results = await self._calculate_confidence_score(validation)
            
            # Store validation
            self.validations[experiment_id] = validation
            
            # Update history
            self.validation_history.append({
                "experiment_id": experiment_id,
                "hypothesis_id": hypothesis_id,
                "timestamp": time.time(),
                "result": "significant" if statistical_result.is_significant else "not_significant",
                "p_value": statistical_result.p_value,
                "effect_size": statistical_result.effect_size,
                "confidence_score": validation.confidence_in_results
            })
            
            self.logger.info(f"Experiment validation completed for {experiment_id}")
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Experiment validation failed: {e}")
            raise
    
    async def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Assess quality of experimental data."""
        try:
            total_points = 0
            missing_count = 0
            outlier_count = 0
            
            # Check all data arrays
            for key, values in data.items():
                if isinstance(values, (list, np.ndarray)):
                    values = np.array(values)
                    total_points += len(values)
                    
                    # Missing data
                    missing_count += np.isnan(values).sum()
                    
                    # Outliers (using IQR method)
                    if len(values) > 4:
                        q1, q3 = np.percentile(values[~np.isnan(values)], [25, 75])
                        iqr = q3 - q1
                        outlier_threshold = 1.5 * iqr
                        outliers = (values < (q1 - outlier_threshold)) | (values > (q3 + outlier_threshold))
                        outlier_count += outliers.sum()
            
            missing_percentage = (missing_count / max(total_points, 1)) * 100
            outlier_percentage = (outlier_count / max(total_points, 1)) * 100
            
            # Quality score calculation
            quality_score = 1.0
            quality_score -= min(missing_percentage / 100, 0.5)  # Penalize missing data
            quality_score -= min(outlier_percentage / 200, 0.3)   # Penalize outliers less
            
            return {
                "quality_score": max(quality_score, 0.0),
                "missing_percentage": missing_percentage,
                "outlier_percentage": outlier_percentage
            }
            
        except Exception as e:
            self.logger.error(f"Data quality assessment failed: {e}")
            return {"quality_score": 0.5, "missing_percentage": 0, "outlier_percentage": 0}
    
    async def _extract_experimental_data(self, 
                                       data: Dict[str, Any], 
                                       hypothesis: HypothesisDefinition) -> Dict[str, np.ndarray]:
        """Extract and clean experimental data."""
        try:
            experimental_data = {}
            
            # Extract control and treatment groups
            if "control" in data and "treatment" in data:
                experimental_data["control"] = np.array(data["control"])
                experimental_data["treatment"] = np.array(data["treatment"])
            
            # Extract paired data if applicable
            elif "before" in data and "after" in data:
                experimental_data["before"] = np.array(data["before"])
                experimental_data["after"] = np.array(data["after"])
            
            # Extract single sample data
            elif "sample" in data:
                experimental_data["sample"] = np.array(data["sample"])
                if "population_mean" in data:
                    experimental_data["population_mean"] = data["population_mean"]
            
            # Handle multiple groups
            else:
                for key, values in data.items():
                    if isinstance(values, (list, np.ndarray)):
                        experimental_data[key] = np.array(values)
            
            # Clean data (remove NaN values)
            for key in experimental_data:
                if isinstance(experimental_data[key], np.ndarray):
                    experimental_data[key] = experimental_data[key][~np.isnan(experimental_data[key])]
            
            return experimental_data
            
        except Exception as e:
            self.logger.error(f"Data extraction failed: {e}")
            return {}
    
    async def _perform_statistical_test(self, 
                                      data: Dict[str, np.ndarray], 
                                      hypothesis: HypothesisDefinition) -> StatisticalResult:
        """Perform appropriate statistical test."""
        try:
            test_type = self._determine_test_type(data, hypothesis)
            
            if test_type == StatisticalTest.T_TEST:
                return await self._perform_t_test(data, hypothesis)
            elif test_type == StatisticalTest.MANN_WHITNEY:
                return await self._perform_mann_whitney_test(data, hypothesis)
            elif test_type == StatisticalTest.WILCOXON:
                return await self._perform_wilcoxon_test(data, hypothesis)
            elif test_type == StatisticalTest.CHI_SQUARE:
                return await self._perform_chi_square_test(data, hypothesis)
            elif test_type == StatisticalTest.BOOTSTRAP:
                return await self._perform_bootstrap_test(data, hypothesis)
            else:
                # Fallback to t-test
                return await self._perform_t_test(data, hypothesis)
                
        except Exception as e:
            self.logger.error(f"Statistical test failed: {e}")
            raise
    
    def _determine_test_type(self, 
                           data: Dict[str, np.ndarray], 
                           hypothesis: HypothesisDefinition) -> StatisticalTest:
        """Determine appropriate statistical test."""
        try:
            # Check data structure
            if "control" in data and "treatment" in data:
                # Two-sample test
                control = data["control"]
                treatment = data["treatment"]
                
                # Check normality and sample size
                if len(control) < 30 or len(treatment) < 30:
                    return StatisticalTest.MANN_WHITNEY
                
                # Check for normality (simplified)
                if self._check_normality(control) and self._check_normality(treatment):
                    return StatisticalTest.T_TEST
                else:
                    return StatisticalTest.MANN_WHITNEY
            
            elif "before" in data and "after" in data:
                # Paired test
                return StatisticalTest.WILCOXON
            
            elif hypothesis.hypothesis_type == HypothesisType.PROPORTION:
                return StatisticalTest.CHI_SQUARE
            
            else:
                return StatisticalTest.BOOTSTRAP
                
        except Exception as e:
            self.logger.error(f"Test type determination failed: {e}")
            return StatisticalTest.T_TEST
    
    def _check_normality(self, data: np.ndarray, alpha: float = 0.05) -> bool:
        """Check if data follows normal distribution."""
        try:
            if len(data) < 8:
                return False  # Too small for reliable test
            
            # Use Shapiro-Wilk test for small samples
            if len(data) <= 50:
                _, p_value = stats.shapiro(data)
            else:
                # Use D'Agostino-Pearson test for larger samples
                _, p_value = stats.normaltest(data)
            
            return p_value > alpha
            
        except Exception:
            return False
    
    async def _perform_t_test(self, 
                            data: Dict[str, np.ndarray], 
                            hypothesis: HypothesisDefinition) -> StatisticalResult:
        """Perform t-test."""
        try:
            if "control" in data and "treatment" in data:
                # Two-sample t-test
                control = data["control"]
                treatment = data["treatment"]
                
                # Perform Welch's t-test (unequal variances)
                t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)
                
                # Calculate effect size (Cohen's d)
                pooled_std = np.sqrt(((len(control) - 1) * np.var(control, ddof=1) + 
                                    (len(treatment) - 1) * np.var(treatment, ddof=1)) / 
                                   (len(control) + len(treatment) - 2))
                
                cohens_d = (np.mean(treatment) - np.mean(control)) / pooled_std
                
                # Degrees of freedom for Welch's t-test
                s1, s2 = np.var(control, ddof=1), np.var(treatment, ddof=1)
                n1, n2 = len(control), len(treatment)
                
                df = (s1/n1 + s2/n2)**2 / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))
                
                # Confidence interval for mean difference
                se_diff = np.sqrt(s1/n1 + s2/n2)
                t_crit = stats.t.ppf(1 - hypothesis.alpha/2, df)
                mean_diff = np.mean(treatment) - np.mean(control)
                ci_lower = mean_diff - t_crit * se_diff
                ci_upper = mean_diff + t_crit * se_diff
                
            else:
                # One-sample t-test
                sample = data["sample"]
                pop_mean = data.get("population_mean", 0)
                
                t_stat, p_value = stats.ttest_1samp(sample, pop_mean)
                cohens_d = (np.mean(sample) - pop_mean) / np.std(sample, ddof=1)
                
                df = len(sample) - 1
                se = np.std(sample, ddof=1) / np.sqrt(len(sample))
                t_crit = stats.t.ppf(1 - hypothesis.alpha/2, df)
                mean_diff = np.mean(sample) - pop_mean
                ci_lower = mean_diff - t_crit * se
                ci_upper = mean_diff + t_crit * se
            
            # Interpret results
            is_significant = p_value < hypothesis.alpha
            interpretation = self._interpret_result(p_value, cohens_d, hypothesis.alpha)
            
            return StatisticalResult(
                test_statistic=t_stat,
                p_value=p_value,
                confidence_interval=(ci_lower, ci_upper),
                effect_size=cohens_d,
                degrees_of_freedom=df,
                is_significant=is_significant,
                interpretation=interpretation
            )
            
        except Exception as e:
            self.logger.error(f"T-test failed: {e}")
            raise
    
    async def _perform_mann_whitney_test(self, 
                                       data: Dict[str, np.ndarray], 
                                       hypothesis: HypothesisDefinition) -> StatisticalResult:
        """Perform Mann-Whitney U test."""
        try:
            control = data["control"]
            treatment = data["treatment"]
            
            # Perform test
            u_stat, p_value = mannwhitneyu(treatment, control, alternative=hypothesis.alternative)
            
            # Calculate effect size (rank biserial correlation)
            n1, n2 = len(control), len(treatment)
            effect_size = 1 - (2 * u_stat) / (n1 * n2)
            
            # Bootstrap confidence interval for median difference
            n_bootstrap = 1000
            bootstrap_diffs = []
            
            for _ in range(n_bootstrap):
                boot_control = np.random.choice(control, size=len(control), replace=True)
                boot_treatment = np.random.choice(treatment, size=len(treatment), replace=True)
                bootstrap_diffs.append(np.median(boot_treatment) - np.median(boot_control))
            
            ci_lower, ci_upper = np.percentile(bootstrap_diffs, 
                                             [100 * hypothesis.alpha/2, 100 * (1 - hypothesis.alpha/2)])
            
            is_significant = p_value < hypothesis.alpha
            interpretation = self._interpret_result(p_value, effect_size, hypothesis.alpha)
            
            return StatisticalResult(
                test_statistic=u_stat,
                p_value=p_value,
                confidence_interval=(ci_lower, ci_upper),
                effect_size=effect_size,
                is_significant=is_significant,
                interpretation=interpretation
            )
            
        except Exception as e:
            self.logger.error(f"Mann-Whitney test failed: {e}")
            raise
    
    async def _perform_wilcoxon_test(self, 
                                   data: Dict[str, np.ndarray], 
                                   hypothesis: HypothesisDefinition) -> StatisticalResult:
        """Perform Wilcoxon signed-rank test."""
        try:
            before = data["before"]
            after = data["after"]
            
            # Ensure paired data
            min_len = min(len(before), len(after))
            before = before[:min_len]
            after = after[:min_len]
            
            # Perform test
            w_stat, p_value = stats.wilcoxon(after, before, alternative=hypothesis.alternative)
            
            # Effect size (matched-pairs rank biserial correlation)
            differences = after - before
            non_zero_diffs = differences[differences != 0]
            
            if len(non_zero_diffs) > 0:
                effect_size = w_stat / (len(non_zero_diffs) * (len(non_zero_diffs) + 1) / 2)
            else:
                effect_size = 0
            
            # Confidence interval for median difference
            median_diff = np.median(differences)
            ci_lower, ci_upper = self._wilcoxon_ci(differences, hypothesis.alpha)
            
            is_significant = p_value < hypothesis.alpha
            interpretation = self._interpret_result(p_value, effect_size, hypothesis.alpha)
            
            return StatisticalResult(
                test_statistic=w_stat,
                p_value=p_value,
                confidence_interval=(ci_lower, ci_upper),
                effect_size=effect_size,
                is_significant=is_significant,
                interpretation=interpretation
            )
            
        except Exception as e:
            self.logger.error(f"Wilcoxon test failed: {e}")
            raise
    
    def _wilcoxon_ci(self, differences: np.ndarray, alpha: float) -> Tuple[float, float]:
        """Calculate confidence interval for Wilcoxon test."""
        try:
            # Bootstrap approach for CI
            n_bootstrap = 1000
            bootstrap_medians = []
            
            for _ in range(n_bootstrap):
                boot_sample = np.random.choice(differences, size=len(differences), replace=True)
                bootstrap_medians.append(np.median(boot_sample))
            
            ci_lower, ci_upper = np.percentile(bootstrap_medians, 
                                             [100 * alpha/2, 100 * (1 - alpha/2)])
            
            return ci_lower, ci_upper
            
        except Exception:
            return 0.0, 0.0
    
    async def _perform_chi_square_test(self, 
                                     data: Dict[str, np.ndarray], 
                                     hypothesis: HypothesisDefinition) -> StatisticalResult:
        """Perform chi-square test for proportions."""
        try:
            # Assume data contains contingency table
            if "contingency_table" in data:
                contingency = data["contingency_table"]
            else:
                # Create contingency table from success counts
                control_success = data.get("control_success", [])
                control_total = data.get("control_total", [])
                treatment_success = data.get("treatment_success", [])
                treatment_total = data.get("treatment_total", [])
                
                contingency = np.array([
                    [sum(control_success), sum(control_total) - sum(control_success)],
                    [sum(treatment_success), sum(treatment_total) - sum(treatment_success)]
                ])
            
            # Perform chi-square test
            chi2_stat, p_value, dof, expected = chi2_contingency(contingency)
            
            # Calculate effect size (Cramer's V)
            n = contingency.sum()
            cramer_v = np.sqrt(chi2_stat / (n * (min(contingency.shape) - 1)))
            
            # Calculate confidence interval for proportion difference
            p1 = contingency[0, 0] / contingency[0].sum()
            p2 = contingency[1, 0] / contingency[1].sum()
            prop_diff = p2 - p1
            
            # Standard error for proportion difference
            n1, n2 = contingency[0].sum(), contingency[1].sum()
            se_diff = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
            
            z_crit = stats.norm.ppf(1 - hypothesis.alpha/2)
            ci_lower = prop_diff - z_crit * se_diff
            ci_upper = prop_diff + z_crit * se_diff
            
            is_significant = p_value < hypothesis.alpha
            interpretation = self._interpret_result(p_value, cramer_v, hypothesis.alpha)
            
            return StatisticalResult(
                test_statistic=chi2_stat,
                p_value=p_value,
                confidence_interval=(ci_lower, ci_upper),
                effect_size=cramer_v,
                degrees_of_freedom=dof,
                is_significant=is_significant,
                interpretation=interpretation
            )
            
        except Exception as e:
            self.logger.error(f"Chi-square test failed: {e}")
            raise
    
    async def _perform_bootstrap_test(self, 
                                    data: Dict[str, np.ndarray], 
                                    hypothesis: HypothesisDefinition) -> StatisticalResult:
        """Perform bootstrap hypothesis test."""
        try:
            control = data.get("control", np.array([]))
            treatment = data.get("treatment", np.array([]))
            
            if len(control) == 0 or len(treatment) == 0:
                raise ValueError("Bootstrap test requires control and treatment groups")
            
            # Observed difference
            observed_diff = np.mean(treatment) - np.mean(control)
            
            # Bootstrap under null hypothesis
            combined = np.concatenate([control, treatment])
            n_control, n_treatment = len(control), len(treatment)
            
            bootstrap_diffs = []
            for _ in range(self.bootstrap_iterations):
                # Resample under null hypothesis
                bootstrap_sample = np.random.choice(combined, size=len(combined), replace=True)
                boot_control = bootstrap_sample[:n_control]
                boot_treatment = bootstrap_sample[n_control:]
                
                bootstrap_diffs.append(np.mean(boot_treatment) - np.mean(boot_control))
            
            bootstrap_diffs = np.array(bootstrap_diffs)
            
            # Calculate p-value
            if hypothesis.alternative == "two-sided":
                p_value = np.mean(np.abs(bootstrap_diffs) >= np.abs(observed_diff))
            elif hypothesis.alternative == "greater":
                p_value = np.mean(bootstrap_diffs >= observed_diff)
            else:  # "less"
                p_value = np.mean(bootstrap_diffs <= observed_diff)
            
            # Effect size (standardized mean difference)
            pooled_std = np.sqrt((np.var(control, ddof=1) + np.var(treatment, ddof=1)) / 2)
            effect_size = observed_diff / pooled_std if pooled_std > 0 else 0
            
            # Confidence interval
            ci_lower, ci_upper = np.percentile(bootstrap_diffs, 
                                             [100 * hypothesis.alpha/2, 100 * (1 - hypothesis.alpha/2)])
            
            is_significant = p_value < hypothesis.alpha
            interpretation = self._interpret_result(p_value, effect_size, hypothesis.alpha)
            
            return StatisticalResult(
                test_statistic=observed_diff,
                p_value=p_value,
                confidence_interval=(ci_lower, ci_upper),
                effect_size=effect_size,
                is_significant=is_significant,
                interpretation=interpretation
            )
            
        except Exception as e:
            self.logger.error(f"Bootstrap test failed: {e}")
            raise
    
    def _interpret_result(self, p_value: float, effect_size: float, alpha: float) -> str:
        """Interpret statistical test results."""
        try:
            interpretation = []
            
            # Statistical significance
            if p_value < alpha:
                interpretation.append(f"Statistically significant (p = {p_value:.4f} < α = {alpha})")
            else:
                interpretation.append(f"Not statistically significant (p = {p_value:.4f} ≥ α = {alpha})")
            
            # Effect size interpretation
            abs_effect = abs(effect_size)
            if abs_effect < self.effect_size_thresholds["small"]:
                effect_desc = "negligible"
            elif abs_effect < self.effect_size_thresholds["medium"]:
                effect_desc = "small"
            elif abs_effect < self.effect_size_thresholds["large"]:
                effect_desc = "medium"
            else:
                effect_desc = "large"
            
            interpretation.append(f"Effect size: {effect_desc} (|d| = {abs_effect:.3f})")
            
            return "; ".join(interpretation)
            
        except Exception as e:
            self.logger.error(f"Result interpretation failed: {e}")
            return "Unable to interpret results"
    
    async def _perform_bayesian_analysis(self, 
                                       data: Dict[str, np.ndarray], 
                                       hypothesis: HypothesisDefinition) -> BayesianResult:
        """Perform Bayesian analysis."""
        try:
            if "control" not in data or "treatment" not in data:
                return None
            
            control = data["control"]
            treatment = data["treatment"]
            
            # Bayesian t-test using default priors
            mean_diff = np.mean(treatment) - np.mean(control)
            
            # Simulate posterior using normal approximation
            n1, n2 = len(control), len(treatment)
            s1, s2 = np.var(control, ddof=1), np.var(treatment, ddof=1)
            
            # Posterior parameters
            se_diff = np.sqrt(s1/n1 + s2/n2)
            
            # Generate posterior samples
            posterior_samples = np.random.normal(mean_diff, se_diff, self.bayesian_samples)
            
            # Calculate Bayesian metrics
            posterior_mean = np.mean(posterior_samples)
            posterior_std = np.std(posterior_samples)
            
            # Credible interval
            credible_level = 1 - hypothesis.alpha
            ci_lower, ci_upper = np.percentile(posterior_samples, 
                                             [100 * hypothesis.alpha/2, 100 * (1 - hypothesis.alpha/2)])
            
            # Probability of direction (P(effect > 0))
            prob_direction = np.mean(posterior_samples > 0)
            
            # Probability of practical effect (P(|effect| > small_effect))
            small_effect = self.effect_size_thresholds["small"]
            prob_effect = np.mean(np.abs(posterior_samples) > small_effect)
            
            # Approximate Bayes Factor (BF10)
            # Using Savage-Dickey density ratio approximation
            prior_density = stats.norm.pdf(0, 0, 1)  # Prior at null
            posterior_density = stats.norm.pdf(0, posterior_mean, posterior_std)  # Posterior at null
            
            bayes_factor = prior_density / max(posterior_density, 1e-10)
            
            # Interpret evidence strength
            evidence_strength = self._interpret_bayes_factor(bayes_factor)
            
            interpretation = f"Evidence {evidence_strength} for alternative hypothesis (BF₁₀ = {bayes_factor:.2f})"
            
            return BayesianResult(
                bayes_factor=bayes_factor,
                posterior_mean=posterior_mean,
                posterior_std=posterior_std,
                credible_interval=(ci_lower, ci_upper),
                probability_of_direction=prob_direction,
                probability_of_effect=prob_effect,
                evidence_strength=evidence_strength,
                interpretation=interpretation
            )
            
        except Exception as e:
            self.logger.error(f"Bayesian analysis failed: {e}")
            return None
    
    def _interpret_bayes_factor(self, bf: float) -> str:
        """Interpret Bayes factor strength."""
        if bf < 1:
            return "against"
        elif bf < 3:
            return "anecdotal"
        elif bf < 10:
            return "moderate"
        elif bf < 30:
            return "strong"
        elif bf < 100:
            return "very strong"
        else:
            return "extreme"
    
    async def _perform_power_analysis(self, 
                                    data: Dict[str, np.ndarray], 
                                    hypothesis: HypothesisDefinition) -> Dict[str, float]:
        """Perform power analysis."""
        try:
            power_analysis = {}
            
            if "control" in data and "treatment" in data:
                control = data["control"]
                treatment = data["treatment"]
                
                # Observed effect size
                pooled_std = np.sqrt((np.var(control, ddof=1) + np.var(treatment, ddof=1)) / 2)
                observed_effect = abs(np.mean(treatment) - np.mean(control)) / pooled_std
                
                # Current power
                n1, n2 = len(control), len(treatment)
                current_power = self._calculate_power(observed_effect, n1, n2, hypothesis.alpha)
                
                # Minimum detectable effect
                mde = self._calculate_mde(n1, n2, hypothesis.alpha, hypothesis.power)
                
                power_analysis = {
                    "observed_effect_size": observed_effect,
                    "current_power": current_power,
                    "minimum_detectable_effect": mde,
                    "recommended_sample_size": hypothesis.minimum_sample_size or 1000
                }
            
            return power_analysis
            
        except Exception as e:
            self.logger.error(f"Power analysis failed: {e}")
            return {}
    
    def _calculate_power(self, effect_size: float, n1: int, n2: int, alpha: float) -> float:
        """Calculate statistical power."""
        try:
            # Approximate power calculation for two-sample t-test
            z_alpha = stats.norm.ppf(1 - alpha/2)
            delta = effect_size * np.sqrt(n1 * n2 / (n1 + n2))
            
            power = 1 - stats.norm.cdf(z_alpha - delta)
            return min(max(power, 0), 1)
            
        except Exception:
            return 0.5
    
    def _calculate_mde(self, n1: int, n2: int, alpha: float, power: float) -> float:
        """Calculate minimum detectable effect."""
        try:
            z_alpha = stats.norm.ppf(1 - alpha/2)
            z_beta = stats.norm.ppf(power)
            
            mde = (z_alpha + z_beta) / np.sqrt(n1 * n2 / (n1 + n2))
            return mde
            
        except Exception:
            return 0.5
    
    async def _assess_business_impact(self, 
                                    data: Dict[str, np.ndarray], 
                                    hypothesis: HypothesisDefinition) -> Dict[str, Any]:
        """Assess business impact of results."""
        try:
            business_impact = {}
            
            if "control" in data and "treatment" in data and hypothesis.business_metric:
                control = data["control"]
                treatment = data["treatment"]
                
                # Calculate improvement
                control_mean = np.mean(control)
                treatment_mean = np.mean(treatment)
                
                if control_mean != 0:
                    relative_improvement = (treatment_mean - control_mean) / control_mean
                    absolute_improvement = treatment_mean - control_mean
                    
                    business_impact = {
                        "metric": hypothesis.business_metric,
                        "control_baseline": control_mean,
                        "treatment_value": treatment_mean,
                        "absolute_improvement": absolute_improvement,
                        "relative_improvement": relative_improvement,
                        "improvement_percentage": relative_improvement * 100
                    }
                    
                    # Creator-specific impact assessment
                    if hypothesis.creator_type in self.creator_configurations:
                        config = self.creator_configurations[hypothesis.creator_type]
                        typical_effect = config.get("typical_effect_sizes", {}).get(hypothesis.business_metric, 0.1)
                        
                        business_impact["vs_typical_effect"] = abs(relative_improvement) / typical_effect
                        business_impact["is_practically_significant"] = abs(relative_improvement) > typical_effect * 0.5
            
            return business_impact
            
        except Exception as e:
            self.logger.error(f"Business impact assessment failed: {e}")
            return {}
    
    async def _generate_recommendations(self, 
                                      statistical_result: StatisticalResult,
                                      bayesian_result: Optional[BayesianResult],
                                      hypothesis: HypothesisDefinition,
                                      data: Dict[str, np.ndarray]) -> Dict[str, List[str]]:
        """Generate recommendations based on results."""
        try:
            recommendations = {
                "statistical": [],
                "next_steps": []
            }
            
            # Statistical recommendations
            if statistical_result.is_significant:
                recommendations["statistical"].append(
                    f"Reject null hypothesis: Evidence supports {hypothesis.alternative_hypothesis}"
                )
                
                if statistical_result.effect_size and abs(statistical_result.effect_size) > self.effect_size_thresholds["medium"]:
                    recommendations["statistical"].append(
                        "Effect size indicates practical significance beyond statistical significance"
                    )
                else:
                    recommendations["statistical"].append(
                        "Consider whether observed effect is practically meaningful"
                    )
            else:
                recommendations["statistical"].append(
                    f"Fail to reject null hypothesis: Insufficient evidence for {hypothesis.alternative_hypothesis}"
                )
                
                # Power analysis recommendations
                sample_sizes = [len(arr) for arr in data.values() if isinstance(arr, np.ndarray)]
                if sample_sizes and min(sample_sizes) < hypothesis.minimum_sample_size:
                    recommendations["statistical"].append(
                        f"Consider increasing sample size (current: {min(sample_sizes)}, recommended: {hypothesis.minimum_sample_size})"
                    )
            
            # Bayesian recommendations
            if bayesian_result:
                if bayesian_result.bayes_factor > 3:
                    recommendations["statistical"].append(
                        f"Bayesian analysis provides {bayesian_result.evidence_strength} evidence (BF₁₀ = {bayesian_result.bayes_factor:.2f})"
                    )
                elif bayesian_result.bayes_factor < 1/3:
                    recommendations["statistical"].append(
                        f"Bayesian analysis supports null hypothesis (BF₁₀ = {bayesian_result.bayes_factor:.2f})"
                    )
                else:
                    recommendations["statistical"].append(
                        "Bayesian analysis is inconclusive - consider collecting more data"
                    )
            
            # Next steps
            if statistical_result.is_significant:
                recommendations["next_steps"].extend([
                    "Implement the change in production",
                    "Monitor long-term effects with continuous A/B testing",
                    "Consider expanding test to other creator segments"
                ])
            else:
                recommendations["next_steps"].extend([
                    "Consider alternative implementations or features",
                    "Analyze subgroup effects for specific creator types",
                    "Design follow-up experiments with higher power"
                ])
            
            # Creator-specific recommendations
            if hypothesis.creator_type:
                config = self.creator_configurations.get(hypothesis.creator_type, {})
                if config.get("seasonal_adjustment"):
                    recommendations["next_steps"].append(
                        "Consider seasonal effects in result interpretation"
                    )
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return {"statistical": [], "next_steps": []}
    
    async def _calculate_confidence_score(self, validation: ExperimentValidation) -> float:
        """Calculate overall confidence score in results."""
        try:
            confidence_factors = []
            
            # Statistical significance
            if validation.statistical_result.is_significant:
                sig_score = max(0, 1 - validation.statistical_result.p_value / validation.hypothesis.alpha)
            else:
                sig_score = 0
            confidence_factors.append(("significance", sig_score, 0.3))
            
            # Effect size
            if validation.statistical_result.effect_size:
                effect_score = min(1, abs(validation.statistical_result.effect_size) / self.effect_size_thresholds["large"])
            else:
                effect_score = 0
            confidence_factors.append(("effect_size", effect_score, 0.2))
            
            # Sample size adequacy
            sample_ratio = validation.achieved_sample_size / validation.recommended_sample_size
            sample_score = min(1, sample_ratio)
            confidence_factors.append(("sample_size", sample_score, 0.2))
            
            # Data quality
            confidence_factors.append(("data_quality", validation.data_quality_score, 0.15))
            
            # Bayesian evidence
            if validation.bayesian_result:
                if validation.bayesian_result.bayes_factor > 1:
                    bayes_score = min(1, np.log10(validation.bayesian_result.bayes_factor) / 2)
                else:
                    bayes_score = 0
            else:
                bayes_score = 0.5
            confidence_factors.append(("bayesian", bayes_score, 0.15))
            
            # Calculate weighted confidence score
            total_score = sum(score * weight for _, score, weight in confidence_factors)
            
            return max(0, min(1, total_score))
            
        except Exception as e:
            self.logger.error(f"Confidence score calculation failed: {e}")
            return 0.5
    
    async def get_validation_summary(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive validation summary."""
        try:
            if experiment_id not in self.validations:
                return None
            
            validation = self.validations[experiment_id]
            
            summary = {
                "experiment_id": experiment_id,
                "hypothesis": {
                    "name": validation.hypothesis.name,
                    "type": validation.hypothesis.hypothesis_type.value,
                    "creator_type": validation.hypothesis.creator_type,
                    "business_metric": validation.hypothesis.business_metric
                },
                "statistical_results": {
                    "is_significant": validation.statistical_result.is_significant,
                    "p_value": validation.statistical_result.p_value,
                    "effect_size": validation.statistical_result.effect_size,
                    "confidence_interval": validation.statistical_result.confidence_interval,
                    "interpretation": validation.statistical_result.interpretation
                },
                "data_quality": {
                    "quality_score": validation.data_quality_score,
                    "sample_size": validation.achieved_sample_size,
                    "outlier_percentage": validation.outlier_percentage,
                    "missing_data_percentage": validation.missing_data_percentage
                },
                "confidence_score": validation.confidence_in_results,
                "recommendations": validation.recommendations,
                "next_steps": validation.next_steps
            }
            
            # Add Bayesian results if available
            if validation.bayesian_result:
                summary["bayesian_results"] = {
                    "bayes_factor": validation.bayesian_result.bayes_factor,
                    "evidence_strength": validation.bayesian_result.evidence_strength,
                    "credible_interval": validation.bayesian_result.credible_interval,
                    "probability_of_effect": validation.bayesian_result.probability_of_effect
                }
            
            # Add business impact if available
            if validation.business_significance:
                summary["business_impact"] = validation.business_significance
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get validation summary: {e}")
            return None
    
    async def generate_statistical_report(self, experiment_id: str) -> str:
        """Generate comprehensive statistical report."""
        try:
            validation = self.validations.get(experiment_id)
            if not validation:
                return "Validation not found"
            
            report = []
            
            # Header
            report.append("=" * 80)
            report.append("STATISTICAL VALIDATION REPORT")
            report.append("=" * 80)
            report.append(f"Experiment ID: {experiment_id}")
            report.append(f"Hypothesis: {validation.hypothesis.name}")
            report.append(f"Creator Type: {validation.hypothesis.creator_type or 'General'}")
            report.append("")
            
            # Hypothesis
            report.append("HYPOTHESIS")
            report.append("-" * 40)
            report.append(f"H₀: {validation.hypothesis.null_hypothesis}")
            report.append(f"H₁: {validation.hypothesis.alternative_hypothesis}")
            report.append(f"Significance Level: α = {validation.hypothesis.alpha}")
            report.append("")
            
            # Statistical Results
            report.append("STATISTICAL ANALYSIS")
            report.append("-" * 40)
            result = validation.statistical_result
            report.append(f"Test Statistic: {result.test_statistic:.4f}")
            report.append(f"P-value: {result.p_value:.6f}")
            report.append(f"Effect Size: {result.effect_size:.4f}" if result.effect_size else "Effect Size: Not calculated")
            report.append(f"Confidence Interval: ({result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f})")
            report.append(f"Result: {'SIGNIFICANT' if result.is_significant else 'NOT SIGNIFICANT'}")
            report.append(f"Interpretation: {result.interpretation}")
            report.append("")
            
            # Bayesian Results
            if validation.bayesian_result:
                report.append("BAYESIAN ANALYSIS")
                report.append("-" * 40)
                bayes = validation.bayesian_result
                report.append(f"Bayes Factor (BF₁₀): {bayes.bayes_factor:.2f}")
                report.append(f"Evidence Strength: {bayes.evidence_strength}")
                report.append(f"Posterior Mean: {bayes.posterior_mean:.4f}")
                report.append(f"Credible Interval: ({bayes.credible_interval[0]:.4f}, {bayes.credible_interval[1]:.4f})")
                report.append(f"P(Direction): {bayes.probability_of_direction:.3f}")
                report.append(f"P(Effect): {bayes.probability_of_effect:.3f}")
                report.append("")
            
            # Data Quality
            report.append("DATA QUALITY ASSESSMENT")
            report.append("-" * 40)
            report.append(f"Quality Score: {validation.data_quality_score:.2f}/1.00")
            report.append(f"Sample Size: {validation.achieved_sample_size}")
            report.append(f"Recommended Size: {validation.recommended_sample_size}")
            report.append(f"Outliers: {validation.outlier_percentage:.1f}%")
            report.append(f"Missing Data: {validation.missing_data_percentage:.1f}%")
            report.append("")
            
            # Business Impact
            if validation.business_significance:
                report.append("BUSINESS IMPACT")
                report.append("-" * 40)
                impact = validation.business_significance
                if "improvement_percentage" in impact:
                    report.append(f"Improvement: {impact['improvement_percentage']:.1f}%")
                if "is_practically_significant" in impact:
                    report.append(f"Practically Significant: {'Yes' if impact['is_practically_significant'] else 'No'}")
                report.append("")
            
            # Confidence Score
            report.append("CONFIDENCE ASSESSMENT")
            report.append("-" * 40)
            report.append(f"Overall Confidence: {validation.confidence_in_results:.2f}/1.00")
            confidence_level = "High" if validation.confidence_in_results > 0.7 else "Medium" if validation.confidence_in_results > 0.4 else "Low"
            report.append(f"Confidence Level: {confidence_level}")
            report.append("")
            
            # Recommendations
            report.append("RECOMMENDATIONS")
            report.append("-" * 40)
            for i, rec in enumerate(validation.recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
            
            # Next Steps
            report.append("NEXT STEPS")
            report.append("-" * 40)
            for i, step in enumerate(validation.next_steps, 1):
                report.append(f"{i}. {step}")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return f"Error generating report: {e}"