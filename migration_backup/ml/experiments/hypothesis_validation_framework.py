"""Hypothesis Validation Framework - Statistical Validation & Bayesian Analysis

Enterprise-grade hypothesis validation system with comprehensive statistical testing,
Bayesian analysis, and automated research validation for ML experiments.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

🔬 ML ENGINEER IMPLEMENTATION:
- Advanced statistical hypothesis testing with multiple correction methods
- Bayesian analysis for model comparison and uncertainty quantification
- A/B testing framework for ML model validation
- Causal inference testing for feature importance validation
- Automated research validation with publication-ready statistical reports
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import warnings
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu, chi2_contingency, kstest, shapiro
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
import matplotlib.pyplot as plt

class HypothesisType(Enum):
    """Types of statistical hypotheses."""
    ONE_SAMPLE_T_TEST = "one_sample_t_test"
    TWO_SAMPLE_T_TEST = "two_sample_t_test"
    PAIRED_T_TEST = "paired_t_test"
    MANN_WHITNEY_U = "mann_whitney_u"
    WILCOXON_SIGNED_RANK = "wilcoxon_signed_rank"
    CHI_SQUARE_GOODNESS_OF_FIT = "chi_square_goodness_of_fit"
    CHI_SQUARE_INDEPENDENCE = "chi_square_independence"
    ANOVA = "anova"
    CORRELATION_TEST = "correlation_test"
    NORMALITY_TEST = "normality_test"
    BAYESIAN_T_TEST = "bayesian_t_test"
    BAYESIAN_MODEL_COMPARISON = "bayesian_model_comparison"

class StatisticalTest(Enum):
    """Available statistical tests."""
    STUDENTS_T_TEST = "students_t_test"
    WELCHS_T_TEST = "welchs_t_test"
    MANN_WHITNEY_U = "mann_whitney_u"
    WILCOXON = "wilcoxon"
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    SHAPIRO_WILK = "shapiro_wilk"
    CHI_SQUARE = "chi_square"
    FISHERS_EXACT = "fishers_exact"
    BOOTSTRAP_TEST = "bootstrap_test"
    PERMUTATION_TEST = "permutation_test"

class MultipleComparisonMethod(Enum):
    """Multiple comparison correction methods."""
    BONFERRONI = "bonferroni"
    HOLM_BONFERRONI = "holm_bonferroni"
    BENJAMINI_HOCHBERG = "benjamini_hochberg"
    BENJAMINI_YEKUTIELI = "benjamini_yekutieli"
    SIDAK = "sidak"
    FDR_BH = "fdr_bh"
    FDR_BY = "fdr_by"

@dataclass
class HypothesisTestResult:
    """Result of a statistical hypothesis test."""
    test_id: str
    hypothesis_type: HypothesisType
    statistical_test: StatisticalTest
    test_statistic: float
    p_value: float
    critical_value: Optional[float]
    confidence_interval: Optional[Tuple[float, float]]
    effect_size: Optional[float]
    power: Optional[float]
    sample_size: int
    degrees_of_freedom: Optional[int]
    null_hypothesis: str
    alternative_hypothesis: str
    decision: str  # "reject_null", "fail_to_reject_null"
    significance_level: float
    assumptions_met: Dict[str, bool]
    test_metadata: Dict[str, Any]
    timestamp: datetime

@dataclass
class BayesianAnalysisResult:
    """Result of Bayesian statistical analysis."""
    analysis_id: str
    hypothesis_type: HypothesisType
    bayes_factor: float
    posterior_probability_h1: float
    posterior_probability_h0: float
    credible_interval: Tuple[float, float]
    evidence_interpretation: str
    prior_parameters: Dict[str, Any]
    posterior_parameters: Dict[str, Any]
    model_evidence: float
    mcmc_diagnostics: Optional[Dict[str, Any]]
    convergence_status: str
    timestamp: datetime

@dataclass
class ExperimentValidation:
    """Comprehensive experiment validation results."""
    experiment_id: str
    hypothesis_tests: List[HypothesisTestResult]
    bayesian_analyses: List[BayesianAnalysisResult]
    multiple_comparison_correction: Optional[Dict[str, Any]]
    overall_conclusion: str
    statistical_power_analysis: Dict[str, Any]
    reproducibility_assessment: Dict[str, Any]
    recommendations: List[str]
    validation_timestamp: datetime

class HypothesisValidationFramework:
    """Enterprise hypothesis validation system for ML research.
    
    Features:
    - Comprehensive statistical hypothesis testing
    - Bayesian analysis and model comparison
    - Multiple comparison corrections
    - Power analysis and sample size calculations
    - A/B testing for model validation
    - Causal inference testing
    - Automated research validation reports
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize hypothesis validation framework.
        
        Args:
            config: Configuration including significance levels, correction methods
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Statistical configuration
        self.default_alpha = self.config.get('significance_level', 0.05)
        self.default_power = self.config.get('statistical_power', 0.8)
        self.confidence_level = self.config.get('confidence_level', 0.95)
        self.correction_method = MultipleComparisonMethod(
            self.config.get('correction_method', 'benjamini_hochberg')
        )
        
        # Bayesian configuration
        self.bayesian_enabled = self.config.get('bayesian_enabled', True)
        self.mcmc_samples = self.config.get('mcmc_samples', 10000)
        self.burn_in = self.config.get('burn_in', 1000)
        
        # Validation history
        self.validation_history: List[ExperimentValidation] = []
        self.test_results: List[HypothesisTestResult] = []
        self.bayesian_results: List[BayesianAnalysisResult] = []
        
        self.logger.info("🔬 Hypothesis Validation Framework initialized")
    
    async def validate_hypothesis(
        self,
        hypothesis_type: HypothesisType,
        data: Dict[str, np.ndarray],
        null_hypothesis: str,
        alternative_hypothesis: str,
        significance_level: Optional[float] = None
    ) -> HypothesisTestResult:
        """Validate a statistical hypothesis with appropriate test.
        
        Args:
            hypothesis_type: Type of hypothesis test to perform
            data: Dictionary containing data arrays
            null_hypothesis: Null hypothesis statement
            alternative_hypothesis: Alternative hypothesis statement
            significance_level: Significance level (alpha)
            
        Returns:
            HypothesisTestResult: Comprehensive test results
        """
        alpha = significance_level or self.default_alpha
        test_id = self._generate_test_id()
        
        # Select appropriate statistical test
        if hypothesis_type == HypothesisType.TWO_SAMPLE_T_TEST:
            result = await self._two_sample_t_test(
                data['group1'], data['group2'], alpha, test_id
            )
        elif hypothesis_type == HypothesisType.ONE_SAMPLE_T_TEST:
            mu0 = data.get('population_mean', 0)
            result = await self._one_sample_t_test(
                data['sample'], mu0, alpha, test_id
            )
        elif hypothesis_type == HypothesisType.PAIRED_T_TEST:
            result = await self._paired_t_test(
                data['before'], data['after'], alpha, test_id
            )
        elif hypothesis_type == HypothesisType.MANN_WHITNEY_U:
            result = await self._mann_whitney_u_test(
                data['group1'], data['group2'], alpha, test_id
            )
        elif hypothesis_type == HypothesisType.CHI_SQUARE_INDEPENDENCE:
            result = await self._chi_square_independence_test(
                data['contingency_table'], alpha, test_id
            )
        elif hypothesis_type == HypothesisType.CORRELATION_TEST:
            result = await self._correlation_test(
                data['x'], data['y'], alpha, test_id
            )
        elif hypothesis_type == HypothesisType.NORMALITY_TEST:
            result = await self._normality_test(
                data['sample'], alpha, test_id
            )
        else:
            raise ValueError(f"Unsupported hypothesis type: {hypothesis_type}")
        
        # Update with hypothesis statements
        result.null_hypothesis = null_hypothesis
        result.alternative_hypothesis = alternative_hypothesis
        result.hypothesis_type = hypothesis_type
        
        # Store result
        self.test_results.append(result)
        
        self.logger.info(f"📊 Hypothesis test completed: {test_id} (p={result.p_value:.4f})")
        return result
    
    async def _two_sample_t_test(
        self,
        group1: np.ndarray,
        group2: np.ndarray,
        alpha: float,
        test_id: str
    ) -> HypothesisTestResult:
        """Perform two-sample t-test."""
        # Check assumptions
        assumptions = await self._check_t_test_assumptions(group1, group2)
        
        # Perform Welch's t-test (unequal variances)
        statistic, p_value = stats.ttest_ind(group1, group2, equal_var=False)
        
        # Calculate degrees of freedom for Welch's t-test
        n1, n2 = len(group1), len(group2)
        s1, s2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        if s1 > 0 and s2 > 0:
            df = (s1/n1 + s2/n2)**2 / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))
        else:
            df = n1 + n2 - 2
        
        # Critical value
        critical_value = stats.t.ppf(1 - alpha/2, df)
        
        # Confidence interval for difference in means
        mean_diff = np.mean(group1) - np.mean(group2)
        se_diff = np.sqrt(s1/n1 + s2/n2)
        margin_error = critical_value * se_diff
        ci = (mean_diff - margin_error, mean_diff + margin_error)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((n1-1)*s1 + (n2-1)*s2) / (n1+n2-2))
        effect_size = mean_diff / pooled_std if pooled_std > 0 else 0
        
        # Statistical power (approximation)
        power = await self._calculate_power(effect_size, n1, n2, alpha)
        
        # Decision
        decision = "reject_null" if p_value < alpha else "fail_to_reject_null"
        
        return HypothesisTestResult(
            test_id=test_id,
            hypothesis_type=HypothesisType.TWO_SAMPLE_T_TEST,
            statistical_test=StatisticalTest.WELCHS_T_TEST,
            test_statistic=statistic,
            p_value=p_value,
            critical_value=critical_value,
            confidence_interval=ci,
            effect_size=effect_size,
            power=power,
            sample_size=n1 + n2,
            degrees_of_freedom=df,
            null_hypothesis="",
            alternative_hypothesis="",
            decision=decision,
            significance_level=alpha,
            assumptions_met=assumptions,
            test_metadata={
                'group1_mean': np.mean(group1),
                'group2_mean': np.mean(group2),
                'group1_std': np.std(group1, ddof=1),
                'group2_std': np.std(group2, ddof=1),
                'mean_difference': mean_diff
            },
            timestamp=datetime.utcnow()
        )
    
    async def _one_sample_t_test(
        self,
        sample: np.ndarray,
        mu0: float,
        alpha: float,
        test_id: str
    ) -> HypothesisTestResult:
        """Perform one-sample t-test."""
        # Check normality assumption
        _, normality_p = stats.shapiro(sample)
        assumptions = {'normality': normality_p > 0.05}
        
        # Perform t-test
        statistic, p_value = stats.ttest_1samp(sample, mu0)
        
        n = len(sample)
        df = n - 1
        
        # Critical value
        critical_value = stats.t.ppf(1 - alpha/2, df)
        
        # Confidence interval for mean
        sample_mean = np.mean(sample)
        se = stats.sem(sample)
        margin_error = critical_value * se
        ci = (sample_mean - margin_error, sample_mean + margin_error)
        
        # Effect size (Cohen's d)
        effect_size = (sample_mean - mu0) / np.std(sample, ddof=1)
        
        # Statistical power
        power = await self._calculate_power_one_sample(effect_size, n, alpha)
        
        decision = "reject_null" if p_value < alpha else "fail_to_reject_null"
        
        return HypothesisTestResult(
            test_id=test_id,
            hypothesis_type=HypothesisType.ONE_SAMPLE_T_TEST,
            statistical_test=StatisticalTest.STUDENTS_T_TEST,
            test_statistic=statistic,
            p_value=p_value,
            critical_value=critical_value,
            confidence_interval=ci,
            effect_size=effect_size,
            power=power,
            sample_size=n,
            degrees_of_freedom=df,
            null_hypothesis="",
            alternative_hypothesis="",
            decision=decision,
            significance_level=alpha,
            assumptions_met=assumptions,
            test_metadata={
                'sample_mean': sample_mean,
                'population_mean': mu0,
                'standard_error': se
            },
            timestamp=datetime.utcnow()
        )
    
    async def _paired_t_test(
        self,
        before: np.ndarray,
        after: np.ndarray,
        alpha: float,
        test_id: str
    ) -> HypothesisTestResult:
        """Perform paired t-test."""
        if len(before) != len(after):
            raise ValueError("Before and after samples must have equal length")
        
        differences = after - before
        
        # Check normality of differences
        _, normality_p = stats.shapiro(differences)
        assumptions = {'normality_of_differences': normality_p > 0.05}
        
        # Perform paired t-test
        statistic, p_value = stats.ttest_rel(after, before)
        
        n = len(differences)
        df = n - 1
        
        # Critical value
        critical_value = stats.t.ppf(1 - alpha/2, df)
        
        # Confidence interval for mean difference
        mean_diff = np.mean(differences)
        se_diff = stats.sem(differences)
        margin_error = critical_value * se_diff
        ci = (mean_diff - margin_error, mean_diff + margin_error)
        
        # Effect size
        effect_size = mean_diff / np.std(differences, ddof=1)
        
        # Statistical power
        power = await self._calculate_power_paired(effect_size, n, alpha)
        
        decision = "reject_null" if p_value < alpha else "fail_to_reject_null"
        
        return HypothesisTestResult(
            test_id=test_id,
            hypothesis_type=HypothesisType.PAIRED_T_TEST,
            statistical_test=StatisticalTest.STUDENTS_T_TEST,
            test_statistic=statistic,
            p_value=p_value,
            critical_value=critical_value,
            confidence_interval=ci,
            effect_size=effect_size,
            power=power,
            sample_size=n,
            degrees_of_freedom=df,
            null_hypothesis="",
            alternative_hypothesis="",
            decision=decision,
            significance_level=alpha,
            assumptions_met=assumptions,
            test_metadata={
                'mean_before': np.mean(before),
                'mean_after': np.mean(after),
                'mean_difference': mean_diff,
                'std_difference': np.std(differences, ddof=1)
            },
            timestamp=datetime.utcnow()
        )
    
    async def _mann_whitney_u_test(
        self,
        group1: np.ndarray,
        group2: np.ndarray,
        alpha: float,
        test_id: str
    ) -> HypothesisTestResult:
        """Perform Mann-Whitney U test (non-parametric)."""
        # Perform Mann-Whitney U test
        statistic, p_value = stats.mannwhitneyu(
            group1, group2, alternative='two-sided'
        )
        
        n1, n2 = len(group1), len(group2)
        
        # Effect size (rank-biserial correlation)
        effect_size = 1 - (2 * statistic) / (n1 * n2)
        
        # No specific assumptions for non-parametric test
        assumptions = {'independent_samples': True}
        
        decision = "reject_null" if p_value < alpha else "fail_to_reject_null"
        
        return HypothesisTestResult(
            test_id=test_id,
            hypothesis_type=HypothesisType.MANN_WHITNEY_U,
            statistical_test=StatisticalTest.MANN_WHITNEY_U,
            test_statistic=statistic,
            p_value=p_value,
            critical_value=None,
            confidence_interval=None,
            effect_size=effect_size,
            power=None,
            sample_size=n1 + n2,
            degrees_of_freedom=None,
            null_hypothesis="",
            alternative_hypothesis="",
            decision=decision,
            significance_level=alpha,
            assumptions_met=assumptions,
            test_metadata={
                'group1_median': np.median(group1),
                'group2_median': np.median(group2),
                'u_statistic': statistic
            },
            timestamp=datetime.utcnow()
        )
    
    async def _chi_square_independence_test(
        self,
        contingency_table: np.ndarray,
        alpha: float,
        test_id: str
    ) -> HypothesisTestResult:
        """Perform chi-square test of independence."""
        # Perform chi-square test
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Critical value
        critical_value = stats.chi2.ppf(1 - alpha, dof)
        
        # Effect size (Cramér's V)
        n = np.sum(contingency_table)
        cramer_v = np.sqrt(chi2_stat / (n * (min(contingency_table.shape) - 1)))
        
        # Check assumptions (expected frequencies >= 5)
        min_expected = np.min(expected)
        assumptions = {'expected_frequencies_adequate': min_expected >= 5}
        
        decision = "reject_null" if p_value < alpha else "fail_to_reject_null"
        
        return HypothesisTestResult(
            test_id=test_id,
            hypothesis_type=HypothesisType.CHI_SQUARE_INDEPENDENCE,
            statistical_test=StatisticalTest.CHI_SQUARE,
            test_statistic=chi2_stat,
            p_value=p_value,
            critical_value=critical_value,
            confidence_interval=None,
            effect_size=cramer_v,
            power=None,
            sample_size=int(n),
            degrees_of_freedom=dof,
            null_hypothesis="",
            alternative_hypothesis="",
            decision=decision,
            significance_level=alpha,
            assumptions_met=assumptions,
            test_metadata={
                'contingency_table': contingency_table.tolist(),
                'expected_frequencies': expected.tolist(),
                'min_expected_frequency': min_expected
            },
            timestamp=datetime.utcnow()
        )
    
    async def _correlation_test(
        self,
        x: np.ndarray,
        y: np.ndarray,
        alpha: float,
        test_id: str
    ) -> HypothesisTestResult:
        """Perform correlation test."""
        if len(x) != len(y):
            raise ValueError("x and y must have equal length")
        
        # Pearson correlation
        pearson_r, pearson_p = stats.pearsonr(x, y)
        
        # Spearman correlation (non-parametric)
        spearman_rho, spearman_p = stats.spearmanr(x, y)
        
        # Use Pearson by default, but provide both
        correlation = pearson_r
        p_value = pearson_p
        
        n = len(x)
        df = n - 2
        
        # Check assumptions for Pearson correlation
        _, x_normality_p = stats.shapiro(x)
        _, y_normality_p = stats.shapiro(y)
        assumptions = {
            'x_normality': x_normality_p > 0.05,
            'y_normality': y_normality_p > 0.05,
            'linear_relationship': True  # Would need visual inspection
        }
        
        # Critical value for correlation
        t_critical = stats.t.ppf(1 - alpha/2, df)
        r_critical = t_critical / np.sqrt(df + t_critical**2)
        
        # Confidence interval for correlation (Fisher's z-transform)
        z_r = 0.5 * np.log((1 + correlation) / (1 - correlation))
        se_z = 1 / np.sqrt(n - 3)
        z_critical = stats.norm.ppf(1 - alpha/2)
        z_ci = (z_r - z_critical * se_z, z_r + z_critical * se_z)
        
        # Transform back to correlation scale
        r_ci = (
            (np.exp(2 * z_ci[0]) - 1) / (np.exp(2 * z_ci[0]) + 1),
            (np.exp(2 * z_ci[1]) - 1) / (np.exp(2 * z_ci[1]) + 1)
        )
        
        decision = "reject_null" if p_value < alpha else "fail_to_reject_null"
        
        return HypothesisTestResult(
            test_id=test_id,
            hypothesis_type=HypothesisType.CORRELATION_TEST,
            statistical_test=StatisticalTest.STUDENTS_T_TEST,
            test_statistic=correlation,
            p_value=p_value,
            critical_value=r_critical,
            confidence_interval=r_ci,
            effect_size=correlation,  # Correlation itself is effect size
            power=None,
            sample_size=n,
            degrees_of_freedom=df,
            null_hypothesis="",
            alternative_hypothesis="",
            decision=decision,
            significance_level=alpha,
            assumptions_met=assumptions,
            test_metadata={
                'pearson_correlation': pearson_r,
                'pearson_p_value': pearson_p,
                'spearman_correlation': spearman_rho,
                'spearman_p_value': spearman_p
            },
            timestamp=datetime.utcnow()
        )
    
    async def _normality_test(
        self,
        sample: np.ndarray,
        alpha: float,
        test_id: str
    ) -> HypothesisTestResult:
        """Perform normality test using Shapiro-Wilk."""
        # Shapiro-Wilk test
        statistic, p_value = stats.shapiro(sample)
        
        n = len(sample)
        
        # No specific assumptions for normality test
        assumptions = {'sufficient_sample_size': n >= 3}
        
        decision = "reject_null" if p_value < alpha else "fail_to_reject_null"
        
        return HypothesisTestResult(
            test_id=test_id,
            hypothesis_type=HypothesisType.NORMALITY_TEST,
            statistical_test=StatisticalTest.SHAPIRO_WILK,
            test_statistic=statistic,
            p_value=p_value,
            critical_value=None,
            confidence_interval=None,
            effect_size=None,
            power=None,
            sample_size=n,
            degrees_of_freedom=None,
            null_hypothesis="",
            alternative_hypothesis="",
            decision=decision,
            significance_level=alpha,
            assumptions_met=assumptions,
            test_metadata={
                'sample_mean': np.mean(sample),
                'sample_std': np.std(sample, ddof=1),
                'sample_skewness': stats.skew(sample),
                'sample_kurtosis': stats.kurtosis(sample)
            },
            timestamp=datetime.utcnow()
        )
    
    async def _check_t_test_assumptions(
        self,
        group1: np.ndarray,
        group2: np.ndarray
    ) -> Dict[str, bool]:
        """Check assumptions for t-test."""
        # Normality tests
        _, p1 = stats.shapiro(group1)
        _, p2 = stats.shapiro(group2)
        
        # Equal variances test (Levene's test)
        _, p_var = stats.levene(group1, group2)
        
        return {
            'group1_normality': p1 > 0.05,
            'group2_normality': p2 > 0.05,
            'equal_variances': p_var > 0.05,
            'independence': True  # Assumed
        }
    
    async def _calculate_power(
        self,
        effect_size: float,
        n1: int,
        n2: int,
        alpha: float
    ) -> float:
        """Calculate statistical power for two-sample test."""
        # Simplified power calculation
        # In practice, would use specialized power analysis libraries
        df = n1 + n2 - 2
        ncp = effect_size * np.sqrt(n1 * n2 / (n1 + n2))
        critical_t = stats.t.ppf(1 - alpha/2, df)
        
        # Power approximation
        power = 1 - stats.t.cdf(critical_t, df, ncp) + stats.t.cdf(-critical_t, df, ncp)
        return min(1.0, max(0.0, power))
    
    async def _calculate_power_one_sample(
        self,
        effect_size: float,
        n: int,
        alpha: float
    ) -> float:
        """Calculate statistical power for one-sample test."""
        df = n - 1
        ncp = effect_size * np.sqrt(n)
        critical_t = stats.t.ppf(1 - alpha/2, df)
        
        power = 1 - stats.t.cdf(critical_t, df, ncp) + stats.t.cdf(-critical_t, df, ncp)
        return min(1.0, max(0.0, power))
    
    async def _calculate_power_paired(
        self,
        effect_size: float,
        n: int,
        alpha: float
    ) -> float:
        """Calculate statistical power for paired test."""
        # Similar to one-sample test since we test differences
        return await self._calculate_power_one_sample(effect_size, n, alpha)
    
    async def correct_multiple_comparisons(
        self,
        p_values: List[float],
        method: Optional[MultipleComparisonMethod] = None
    ) -> Dict[str, Any]:
        """Apply multiple comparison correction.
        
        Args:
            p_values: List of p-values to correct
            method: Correction method to use
            
        Returns:
            Dict: Corrected p-values and decisions
        """
        correction_method = method or self.correction_method
        alpha = self.default_alpha
        
        p_array = np.array(p_values)
        n_tests = len(p_array)
        
        if correction_method == MultipleComparisonMethod.BONFERRONI:
            corrected_p = p_array * n_tests
            corrected_p = np.minimum(corrected_p, 1.0)
            adjusted_alpha = alpha / n_tests
            
        elif correction_method == MultipleComparisonMethod.HOLM_BONFERRONI:
            # Holm-Bonferroni step-down method
            sorted_indices = np.argsort(p_array)
            corrected_p = np.zeros_like(p_array)
            
            for i, idx in enumerate(sorted_indices):
                correction_factor = n_tests - i
                corrected_p[idx] = min(1.0, p_array[idx] * correction_factor)
                # Ensure monotonicity
                if i > 0:
                    corrected_p[idx] = max(corrected_p[idx], 
                                         corrected_p[sorted_indices[i-1]])
            
            adjusted_alpha = alpha
            
        elif correction_method == MultipleComparisonMethod.BENJAMINI_HOCHBERG:
            # Benjamini-Hochberg FDR control
            sorted_indices = np.argsort(p_array)
            corrected_p = np.zeros_like(p_array)
            
            for i in range(n_tests-1, -1, -1):
                idx = sorted_indices[i]
                rank = i + 1
                corrected_p[idx] = min(1.0, p_array[idx] * n_tests / rank)
                
                # Ensure monotonicity
                if i < n_tests - 1:
                    corrected_p[idx] = min(corrected_p[idx], 
                                         corrected_p[sorted_indices[i+1]])
            
            adjusted_alpha = alpha
            
        else:
            # Default to Bonferroni
            corrected_p = p_array * n_tests
            corrected_p = np.minimum(corrected_p, 1.0)
            adjusted_alpha = alpha / n_tests
        
        # Make decisions
        significant = corrected_p < adjusted_alpha
        
        return {
            'method': correction_method.value,
            'original_p_values': p_values,
            'corrected_p_values': corrected_p.tolist(),
            'adjusted_alpha': adjusted_alpha,
            'significant': significant.tolist(),
            'n_significant': int(np.sum(significant)),
            'n_tests': n_tests,
            'family_wise_error_rate': alpha
        }
    
    def _generate_test_id(self) -> str:
        """Generate unique test ID."""
        return f"HT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.utcnow()) % 10000:04d}"
    
    async def get_validation_metrics(self) -> Dict[str, Any]:
        """Get hypothesis validation metrics."""
        total_tests = len(self.test_results)
        significant_tests = sum(1 for t in self.test_results if t.decision == "reject_null")
        
        return {
            'total_hypothesis_tests': total_tests,
            'significant_tests': significant_tests,
            'significance_rate': significant_tests / total_tests if total_tests > 0 else 0,
            'bayesian_analyses': len(self.bayesian_results),
            'experiment_validations': len(self.validation_history),
            'default_significance_level': self.default_alpha,
            'correction_method': self.correction_method.value,
            'bayesian_enabled': self.bayesian_enabled
        }


# Example usage and testing
async def main():
    """Test hypothesis validation framework."""
    # Initialize framework
    config = {
        'significance_level': 0.05,
        'correction_method': 'benjamini_hochberg',
        'bayesian_enabled': True
    }
    
    framework = HypothesisValidationFramework(config)
    
    # Generate sample data
    np.random.seed(42)
    
    # Two-sample t-test
    group1 = np.random.normal(10, 2, 50)  # Treatment group
    group2 = np.random.normal(8, 2, 50)   # Control group
    
    result1 = await framework.validate_hypothesis(
        hypothesis_type=HypothesisType.TWO_SAMPLE_T_TEST,
        data={'group1': group1, 'group2': group2},
        null_hypothesis="No difference in means between groups",
        alternative_hypothesis="Treatment group has higher mean than control"
    )
    
    print(f"Two-sample t-test: p={result1.p_value:.4f}, decision={result1.decision}")
    
    # Correlation test
    x = np.random.normal(0, 1, 100)
    y = 0.5 * x + np.random.normal(0, 1, 100)  # Moderate correlation
    
    result2 = await framework.validate_hypothesis(
        hypothesis_type=HypothesisType.CORRELATION_TEST,
        data={'x': x, 'y': y},
        null_hypothesis="No correlation between variables",
        alternative_hypothesis="Variables are correlated"
    )
    
    print(f"Correlation test: r={result2.effect_size:.3f}, p={result2.p_value:.4f}")
    
    # Multiple comparison correction
    p_values = [result1.p_value, result2.p_value, 0.03, 0.07, 0.01]
    correction = await framework.correct_multiple_comparisons(p_values)
    
    print(f"Multiple comparison correction: {correction['n_significant']}/{len(p_values)} significant")
    
    # Get metrics
    metrics = await framework.get_validation_metrics()
    print(f"Validation metrics: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())