"""
Statistical Engine
Advanced statistical analysis and testing for ML experiments

This module provides:
- Statistical significance testing (t-tests, chi-square, etc.)
- Effect size calculations (Cohen's d, Glass's delta)
- Power analysis and sample size calculations
- Bayesian statistical methods
- Confidence interval calculations

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from scipy import stats
from scipy.stats import norm, chi2, t as t_dist
import math
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TestType(Enum):
    T_TEST = "t_test"
    WELCH_T_TEST = "welch_t_test"
    CHI_SQUARE = "chi_square"
    MANN_WHITNEY = "mann_whitney"
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    BAYESIAN = "bayesian"

@dataclass
class StatisticalTestResult:
    """Results from statistical significance testing"""
    test_type: TestType
    statistic: float
    p_value: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    power: float
    sample_size_a: int
    sample_size_b: int
    is_significant: bool
    alpha: float
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class EffectSizeResult:
    """Effect size calculation results"""
    cohens_d: float
    glass_delta: float
    hedge_g: float
    r_squared: float
    magnitude: str  # small, medium, large
    interpretation: str

class StatisticalEngine:
    """
    Advanced statistical analysis engine for ML experimentation
    Provides comprehensive statistical testing and analysis capabilities
    """
    
    def __init__(self):
        self.confidence_levels = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        
    async def validate_sample_size(
        self,
        metrics: Dict[str, Any],
        minimum_required: int
    ) -> bool:
        """
        Validate if sample size is adequate for statistical testing
        
        Args:
            metrics: Experimental metrics containing sample sizes
            minimum_required: Minimum sample size required
            
        Returns:
            is_valid: Whether sample size is adequate
        """
        try:
            total_samples = metrics.get("total_samples", 0)
            control_samples = metrics.get("control", {}).get("sample_size", 0)
            treatment_samples = metrics.get("treatment", {}).get("sample_size", 0)
            
            # Check individual group sizes
            min_group_size = min(control_samples, treatment_samples)
            
            # Rule of thumb: each group should have at least 30 samples
            # and total should meet minimum requirement
            return (
                min_group_size >= 30 and
                total_samples >= minimum_required and
                control_samples > 0 and
                treatment_samples > 0
            )
            
        except Exception as e:
            logger.error(f"Failed to validate sample size: {e}")
            return False
    
    async def calculate_effect_size(
        self,
        control_data: Dict[str, Any],
        treatment_data: Dict[str, Any],
        metric: str = "primary"
    ) -> EffectSizeResult:
        """
        Calculate effect size between control and treatment groups
        
        Args:
            control_data: Control group metrics
            treatment_data: Treatment group metrics
            metric: Metric to analyze
            
        Returns:
            effect_size_result: Comprehensive effect size analysis
        """
        try:
            # Extract values
            control_mean = control_data.get("mean", 0)
            control_std = control_data.get("std", 1)
            control_n = control_data.get("sample_size", 1)
            
            treatment_mean = treatment_data.get("mean", 0)
            treatment_std = treatment_data.get("std", 1)
            treatment_n = treatment_data.get("sample_size", 1)
            
            # Cohen's d
            pooled_std = math.sqrt(
                ((control_n - 1) * control_std**2 + (treatment_n - 1) * treatment_std**2) /
                (control_n + treatment_n - 2)
            )
            
            cohens_d = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0
            
            # Glass's delta (using control group std)
            glass_delta = (treatment_mean - control_mean) / control_std if control_std > 0 else 0
            
            # Hedge's g (bias-corrected Cohen's d)
            correction_factor = 1 - (3 / (4 * (control_n + treatment_n) - 9))
            hedge_g = cohens_d * correction_factor
            
            # R-squared (proportion of variance explained)
            total_n = control_n + treatment_n
            r_squared = (cohens_d**2) / (cohens_d**2 + (total_n / (control_n * treatment_n)))
            
            # Magnitude interpretation (Cohen's conventions)
            magnitude = self._interpret_effect_magnitude(abs(cohens_d))
            interpretation = self._generate_effect_interpretation(cohens_d, magnitude)
            
            return EffectSizeResult(
                cohens_d=cohens_d,
                glass_delta=glass_delta,
                hedge_g=hedge_g,
                r_squared=r_squared,
                magnitude=magnitude,
                interpretation=interpretation
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate effect size: {e}")
            raise
    
    async def perform_t_test(
        self,
        control_data: List[float],
        treatment_data: List[float],
        alpha: float = 0.05,
        equal_var: bool = True
    ) -> StatisticalTestResult:
        """
        Perform t-test for comparing two groups
        
        Args:
            control_data: Control group measurements
            treatment_data: Treatment group measurements
            alpha: Significance level
            equal_var: Assume equal variances
            
        Returns:
            test_result: T-test results
        """
        try:
            control_array = np.array(control_data)
            treatment_array = np.array(treatment_data)
            
            # Perform t-test
            if equal_var:
                statistic, p_value = stats.ttest_ind(control_array, treatment_array)
                test_type = TestType.T_TEST
            else:
                statistic, p_value = stats.ttest_ind(control_array, treatment_array, equal_var=False)
                test_type = TestType.WELCH_T_TEST
            
            # Calculate degrees of freedom
            n1, n2 = len(control_data), len(treatment_data)
            if equal_var:
                df = n1 + n2 - 2
            else:
                # Welch's formula for unequal variances
                s1, s2 = np.var(control_array, ddof=1), np.var(treatment_array, ddof=1)
                df = (s1/n1 + s2/n2)**2 / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))
            
            # Confidence interval for difference in means
            diff_mean = np.mean(treatment_array) - np.mean(control_array)
            se_diff = np.sqrt(np.var(control_array, ddof=1)/n1 + np.var(treatment_array, ddof=1)/n2)
            t_critical = t_dist.ppf(1 - alpha/2, df)
            ci_lower = diff_mean - t_critical * se_diff
            ci_upper = diff_mean + t_critical * se_diff
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt(((n1-1)*np.var(control_array, ddof=1) + (n2-1)*np.var(treatment_array, ddof=1))/(n1+n2-2))
            effect_size = diff_mean / pooled_std if pooled_std > 0 else 0
            
            # Statistical power (post-hoc)
            power = await self._calculate_post_hoc_power(effect_size, n1, n2, alpha)
            
            return StatisticalTestResult(
                test_type=test_type,
                statistic=statistic,
                p_value=p_value,
                confidence_interval=(ci_lower, ci_upper),
                effect_size=effect_size,
                power=power,
                sample_size_a=n1,
                sample_size_b=n2,
                is_significant=p_value < alpha,
                alpha=alpha,
                metadata={
                    "degrees_of_freedom": df,
                    "mean_difference": diff_mean,
                    "standard_error": se_diff
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to perform t-test: {e}")
            raise
    
    async def perform_chi_square_test(
        self,
        observed_counts: List[List[int]],
        alpha: float = 0.05
    ) -> StatisticalTestResult:
        """
        Perform chi-square test for categorical data
        
        Args:
            observed_counts: 2D array of observed frequencies
            alpha: Significance level
            
        Returns:
            test_result: Chi-square test results
        """
        try:
            observed = np.array(observed_counts)
            
            # Perform chi-square test
            statistic, p_value, dof, expected = stats.chi2_contingency(observed)
            
            # Calculate effect size (Cramér's V)
            n = np.sum(observed)
            min_dim = min(observed.shape) - 1
            cramers_v = np.sqrt(statistic / (n * min_dim)) if n > 0 and min_dim > 0 else 0
            
            # Confidence interval for chi-square statistic
            ci_lower = chi2.ppf(alpha/2, dof)
            ci_upper = chi2.ppf(1 - alpha/2, dof)
            
            # Statistical power (approximate)
            power = 1 - chi2.cdf(chi2.ppf(1-alpha, dof), dof, statistic)
            
            return StatisticalTestResult(
                test_type=TestType.CHI_SQUARE,
                statistic=statistic,
                p_value=p_value,
                confidence_interval=(ci_lower, ci_upper),
                effect_size=cramers_v,
                power=power,
                sample_size_a=int(np.sum(observed[0])),
                sample_size_b=int(np.sum(observed[1])) if observed.shape[0] > 1 else 0,
                is_significant=p_value < alpha,
                alpha=alpha,
                metadata={
                    "degrees_of_freedom": dof,
                    "expected_counts": expected.tolist(),
                    "cramers_v": cramers_v
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to perform chi-square test: {e}")
            raise
    
    async def calculate_required_sample_size(
        self,
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.8,
        alternative: str = "two-sided"
    ) -> int:
        """
        Calculate required sample size for given effect size and power
        
        Args:
            effect_size: Expected effect size (Cohen's d)
            alpha: Type I error rate
            power: Statistical power (1 - Type II error rate)
            alternative: Test alternative ("two-sided", "greater", "less")
            
        Returns:
            required_n: Required sample size per group
        """
        try:
            # Z-scores for alpha and beta
            if alternative == "two-sided":
                z_alpha = norm.ppf(1 - alpha/2)
            else:
                z_alpha = norm.ppf(1 - alpha)
                
            z_beta = norm.ppf(power)
            
            # Sample size calculation
            # n = 2 * ((z_alpha + z_beta) / effect_size)^2
            if effect_size == 0:
                return float('inf')
                
            n_per_group = 2 * ((z_alpha + z_beta) / effect_size)**2
            
            # Round up to nearest integer
            return max(1, int(np.ceil(n_per_group)))
            
        except Exception as e:
            logger.error(f"Failed to calculate sample size: {e}")
            raise
    
    async def perform_bayesian_test(
        self,
        control_data: List[float],
        treatment_data: List[float],
        prior_mean: float = 0,
        prior_std: float = 1
    ) -> Dict[str, Any]:
        """
        Perform Bayesian hypothesis testing
        
        Args:
            control_data: Control group data
            treatment_data: Treatment group data
            prior_mean: Prior mean for effect size
            prior_std: Prior standard deviation for effect size
            
        Returns:
            bayesian_result: Bayesian analysis results
        """
        try:
            control_array = np.array(control_data)
            treatment_array = np.array(treatment_data)
            
            # Calculate sample statistics
            n1, n2 = len(control_data), len(treatment_data)
            mean1, mean2 = np.mean(control_array), np.mean(treatment_array)
            var1, var2 = np.var(control_array, ddof=1), np.var(treatment_array, ddof=1)
            
            # Observed difference
            observed_diff = mean2 - mean1
            
            # Standard error of difference
            se_diff = np.sqrt(var1/n1 + var2/n2)
            
            # Bayesian updating (assuming normal likelihood)
            # Posterior mean and variance
            likelihood_precision = 1 / (se_diff**2)
            prior_precision = 1 / (prior_std**2)
            
            posterior_precision = prior_precision + likelihood_precision
            posterior_variance = 1 / posterior_precision
            posterior_std = np.sqrt(posterior_variance)
            
            posterior_mean = (
                prior_precision * prior_mean + likelihood_precision * observed_diff
            ) / posterior_precision
            
            # Credible interval (95%)
            credible_lower = posterior_mean - 1.96 * posterior_std
            credible_upper = posterior_mean + 1.96 * posterior_std
            
            # Probability that treatment is better than control
            prob_positive = 1 - norm.cdf(0, posterior_mean, posterior_std)
            
            # Bayes factor (approximate)
            # BF01 = P(data|H0) / P(data|H1)
            marginal_likelihood_h0 = norm.pdf(observed_diff, 0, se_diff)
            marginal_likelihood_h1 = norm.pdf(observed_diff, prior_mean, np.sqrt(prior_std**2 + se_diff**2))
            bayes_factor = marginal_likelihood_h0 / marginal_likelihood_h1 if marginal_likelihood_h1 > 0 else float('inf')
            
            return {
                "posterior_mean": posterior_mean,
                "posterior_std": posterior_std,
                "credible_interval": (credible_lower, credible_upper),
                "probability_positive": prob_positive,
                "bayes_factor": bayes_factor,
                "observed_difference": observed_diff,
                "evidence_strength": self._interpret_bayes_factor(bayes_factor)
            }
            
        except Exception as e:
            logger.error(f"Failed to perform Bayesian test: {e}")
            raise
    
    def _interpret_effect_magnitude(self, cohens_d: float) -> str:
        """Interpret effect size magnitude using Cohen's conventions"""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"
    
    def _generate_effect_interpretation(self, cohens_d: float, magnitude: str) -> str:
        """Generate human-readable interpretation of effect size"""
        direction = "positive" if cohens_d > 0 else "negative"
        return f"The treatment shows a {magnitude} {direction} effect compared to control (Cohen's d = {cohens_d:.3f})"
    
    async def _calculate_post_hoc_power(
        self,
        effect_size: float,
        n1: int,
        n2: int,
        alpha: float
    ) -> float:
        """Calculate post-hoc statistical power"""
        try:
            # Calculate noncentrality parameter
            n_harmonic = 2 / (1/n1 + 1/n2)  # Harmonic mean
            ncp = effect_size * np.sqrt(n_harmonic / 2)
            
            # Critical value
            df = n1 + n2 - 2
            t_critical = t_dist.ppf(1 - alpha/2, df)
            
            # Power calculation
            power = 1 - t_dist.cdf(t_critical, df, ncp) + t_dist.cdf(-t_critical, df, ncp)
            
            return max(0, min(1, power))
            
        except Exception as e:
            logger.warning(f"Could not calculate post-hoc power: {e}")
            return 0.0
    
    def _interpret_bayes_factor(self, bf: float) -> str:
        """Interpret Bayes Factor using Jeffreys' scale"""
        if bf < 1:
            inv_bf = 1 / bf
            if inv_bf < 3:
                return "weak evidence for H1"
            elif inv_bf < 10:
                return "moderate evidence for H1"
            elif inv_bf < 30:
                return "strong evidence for H1"
            elif inv_bf < 100:
                return "very strong evidence for H1"
            else:
                return "extreme evidence for H1"
        else:
            if bf < 3:
                return "weak evidence for H0"
            elif bf < 10:
                return "moderate evidence for H0"
            elif bf < 30:
                return "strong evidence for H0"
            elif bf < 100:
                return "very strong evidence for H0"
            else:
                return "extreme evidence for H0"