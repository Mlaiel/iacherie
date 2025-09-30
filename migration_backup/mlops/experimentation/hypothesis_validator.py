"""
Hypothesis Validator
Statistical hypothesis testing and validation for ML experiments

This module provides:
- Hypothesis formulation and testing
- Statistical significance validation
- Multiple testing corrections
- Sequential testing capabilities
- Business significance evaluation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from scipy.stats import norm
import math

logger = logging.getLogger(__name__)

class HypothesisType(Enum):
    SUPERIORITY = "superiority"  # H1: treatment > control
    NON_INFERIORITY = "non_inferiority"  # H1: treatment >= control - margin
    EQUIVALENCE = "equivalence"  # H1: |treatment - control| <= margin
    TWO_SIDED = "two_sided"  # H1: treatment != control

@dataclass
class Hypothesis:
    """Hypothesis definition"""
    name: str
    type: HypothesisType
    primary_metric: str
    null_hypothesis: str
    alternative_hypothesis: str
    margin: Optional[float] = None  # For non-inferiority and equivalence tests
    alpha: float = 0.05
    power: float = 0.8
    minimum_effect_size: Optional[float] = None

@dataclass
class ValidationResult:
    """Hypothesis validation result"""
    hypothesis: Hypothesis
    is_valid: bool
    p_value: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    statistical_power: float
    business_significance: bool
    recommendation: str
    details: Dict[str, Any]

class HypothesisValidator:
    """
    Advanced hypothesis validation for ML experiments
    Handles multiple testing scenarios and business significance
    """
    
    def __init__(self):
        self.active_hypotheses: Dict[str, Hypothesis] = {}
        self.validation_history: List[ValidationResult] = []
        
    async def formulate_hypothesis(
        self,
        name: str,
        hypothesis_type: HypothesisType,
        primary_metric: str,
        expected_improvement: float,
        alpha: float = 0.05,
        power: float = 0.8,
        margin: Optional[float] = None
    ) -> Hypothesis:
        """
        Formulate statistical hypothesis for experiment
        
        Args:
            name: Hypothesis identifier
            hypothesis_type: Type of hypothesis test
            primary_metric: Primary metric to evaluate
            expected_improvement: Expected improvement magnitude
            alpha: Type I error rate
            power: Statistical power requirement
            margin: Margin for non-inferiority/equivalence tests
            
        Returns:
            hypothesis: Formulated hypothesis object
        """
        try:
            # Generate hypothesis statements
            null_hypothesis, alternative_hypothesis = self._generate_hypothesis_statements(
                hypothesis_type, primary_metric, margin
            )
            
            hypothesis = Hypothesis(
                name=name,
                type=hypothesis_type,
                primary_metric=primary_metric,
                null_hypothesis=null_hypothesis,
                alternative_hypothesis=alternative_hypothesis,
                margin=margin,
                alpha=alpha,
                power=power,
                minimum_effect_size=expected_improvement
            )
            
            self.active_hypotheses[name] = hypothesis
            
            logger.info(f"Formulated hypothesis '{name}': {alternative_hypothesis}")
            return hypothesis
            
        except Exception as e:
            logger.error(f"Failed to formulate hypothesis: {e}")
            raise
    
    async def test_significance(
        self,
        control_metrics: Dict[str, Any],
        treatment_metrics: Dict[str, Any],
        hypothesis_name: Optional[str] = None,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Test statistical significance of experimental results
        
        Args:
            control_metrics: Control group metrics
            treatment_metrics: Treatment group metrics
            hypothesis_name: Specific hypothesis to test
            confidence_level: Confidence level for intervals
            
        Returns:
            significance_results: Comprehensive significance analysis
        """
        try:
            alpha = 1 - confidence_level
            
            # Extract primary metric values
            control_value = control_metrics.get("primary_metric", 0)
            treatment_value = treatment_metrics.get("primary_metric", 0)
            
            control_n = control_metrics.get("sample_size", 1)
            treatment_n = treatment_metrics.get("sample_size", 1)
            
            control_std = control_metrics.get("std", 1)
            treatment_std = treatment_metrics.get("std", 1)
            
            # Calculate observed difference
            observed_difference = treatment_value - control_value
            
            # Calculate standard error
            pooled_variance = (
                (control_n - 1) * control_std**2 + 
                (treatment_n - 1) * treatment_std**2
            ) / (control_n + treatment_n - 2)
            
            standard_error = math.sqrt(
                pooled_variance * (1/control_n + 1/treatment_n)
            )
            
            # Calculate test statistic
            if standard_error > 0:
                t_statistic = observed_difference / standard_error
            else:
                t_statistic = 0
            
            # Degrees of freedom
            df = control_n + treatment_n - 2
            
            # Calculate p-value (two-tailed)
            from scipy.stats import t as t_dist
            p_value = 2 * (1 - t_dist.cdf(abs(t_statistic), df))
            
            # Confidence interval
            t_critical = t_dist.ppf(1 - alpha/2, df)
            margin_error = t_critical * standard_error
            
            ci_lower = observed_difference - margin_error
            ci_upper = observed_difference + margin_error
            
            # Effect size (Cohen's d)
            pooled_std = math.sqrt(pooled_variance)
            effect_size = observed_difference / pooled_std if pooled_std > 0 else 0
            
            # Statistical significance
            is_significant = p_value < alpha
            
            # Business significance evaluation
            business_significant = await self._evaluate_business_significance(
                observed_difference, effect_size, control_metrics, treatment_metrics
            )
            
            # Generate recommendation
            recommendation = self._generate_significance_recommendation(
                is_significant, business_significant, effect_size, p_value
            )
            
            return {
                "is_significant": is_significant,
                "p_value": p_value,
                "confidence_interval": (ci_lower, ci_upper),
                "effect_size": effect_size,
                "observed_difference": observed_difference,
                "standard_error": standard_error,
                "t_statistic": t_statistic,
                "degrees_of_freedom": df,
                "business_significant": business_significant,
                "recommendation": recommendation,
                "alpha": alpha,
                "confidence_level": confidence_level
            }
            
        except Exception as e:
            logger.error(f"Failed to test significance: {e}")
            raise
    
    async def validate_hypothesis(
        self,
        hypothesis_name: str,
        control_metrics: Dict[str, Any],
        treatment_metrics: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate specific hypothesis against experimental data
        
        Args:
            hypothesis_name: Hypothesis to validate
            control_metrics: Control group metrics
            treatment_metrics: Treatment group metrics
            
        Returns:
            validation_result: Comprehensive validation result
        """
        try:
            if hypothesis_name not in self.active_hypotheses:
                raise ValueError(f"Hypothesis '{hypothesis_name}' not found")
            
            hypothesis = self.active_hypotheses[hypothesis_name]
            
            # Get significance test results
            significance_results = await self.test_significance(
                control_metrics, treatment_metrics, hypothesis_name, 
                confidence_level=1-hypothesis.alpha
            )
            
            # Hypothesis-specific validation
            is_valid = await self._validate_hypothesis_specific(
                hypothesis, significance_results, control_metrics, treatment_metrics
            )
            
            # Calculate statistical power (post-hoc)
            statistical_power = await self._calculate_achieved_power(
                hypothesis, significance_results, control_metrics, treatment_metrics
            )
            
            # Business significance
            business_significance = significance_results["business_significant"]
            
            # Generate detailed recommendation
            recommendation = await self._generate_detailed_recommendation(
                hypothesis, is_valid, significance_results, business_significance
            )
            
            validation_result = ValidationResult(
                hypothesis=hypothesis,
                is_valid=is_valid,
                p_value=significance_results["p_value"],
                confidence_interval=significance_results["confidence_interval"],
                effect_size=significance_results["effect_size"],
                statistical_power=statistical_power,
                business_significance=business_significance,
                recommendation=recommendation,
                details=significance_results
            )
            
            self.validation_history.append(validation_result)
            
            logger.info(f"Validated hypothesis '{hypothesis_name}': {recommendation}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate hypothesis: {e}")
            raise
    
    async def correct_multiple_testing(
        self,
        p_values: List[float],
        method: str = "bonferroni"
    ) -> List[float]:
        """
        Apply multiple testing correction
        
        Args:
            p_values: List of p-values to correct
            method: Correction method ("bonferroni", "holm", "benjamini_hochberg")
            
        Returns:
            corrected_p_values: Corrected p-values
        """
        try:
            n_tests = len(p_values)
            
            if method == "bonferroni":
                # Bonferroni correction
                corrected = [min(1.0, p * n_tests) for p in p_values]
                
            elif method == "holm":
                # Holm-Bonferroni method
                sorted_indices = sorted(range(n_tests), key=lambda i: p_values[i])
                corrected = [0] * n_tests
                
                for rank, idx in enumerate(sorted_indices):
                    corrected[idx] = min(1.0, p_values[idx] * (n_tests - rank))
                    
            elif method == "benjamini_hochberg":
                # Benjamini-Hochberg (FDR) method
                sorted_indices = sorted(range(n_tests), key=lambda i: p_values[i])
                corrected = [0] * n_tests
                
                for rank, idx in enumerate(sorted_indices):
                    corrected[idx] = min(1.0, p_values[idx] * n_tests / (rank + 1))
                    
            else:
                raise ValueError(f"Unknown correction method: {method}")
            
            logger.info(f"Applied {method} correction to {n_tests} tests")
            return corrected
            
        except Exception as e:
            logger.error(f"Failed to correct for multiple testing: {e}")
            raise
    
    async def sequential_testing(
        self,
        hypothesis_name: str,
        control_metrics: Dict[str, Any],
        treatment_metrics: Dict[str, Any],
        alpha_spending_function: str = "obrien_fleming"
    ) -> Dict[str, Any]:
        """
        Perform sequential hypothesis testing with alpha spending
        
        Args:
            hypothesis_name: Hypothesis to test
            control_metrics: Control group metrics
            treatment_metrics: Treatment group metrics
            alpha_spending_function: Alpha spending function to use
            
        Returns:
            sequential_result: Sequential testing results
        """
        try:
            if hypothesis_name not in self.active_hypotheses:
                raise ValueError(f"Hypothesis '{hypothesis_name}' not found")
            
            hypothesis = self.active_hypotheses[hypothesis_name]
            
            # Calculate current information fraction
            current_n = control_metrics.get("sample_size", 0) + treatment_metrics.get("sample_size", 0)
            planned_n = control_metrics.get("planned_sample_size", current_n)
            information_fraction = current_n / planned_n if planned_n > 0 else 1.0
            
            # Calculate alpha spending
            alpha_spent = await self._calculate_alpha_spending(
                information_fraction, hypothesis.alpha, alpha_spending_function
            )
            
            # Adjusted significance level for this interim analysis
            adjusted_alpha = alpha_spent
            
            # Perform significance test with adjusted alpha
            significance_results = await self.test_significance(
                control_metrics, treatment_metrics, hypothesis_name,
                confidence_level=1-adjusted_alpha
            )
            
            # Sequential decision
            decision = self._make_sequential_decision(
                significance_results, adjusted_alpha, information_fraction
            )
            
            return {
                "information_fraction": information_fraction,
                "alpha_spent": alpha_spent,
                "adjusted_alpha": adjusted_alpha,
                "significance_results": significance_results,
                "decision": decision,
                "continue_experiment": decision == "continue"
            }
            
        except Exception as e:
            logger.error(f"Failed to perform sequential testing: {e}")
            raise
    
    def _generate_hypothesis_statements(
        self,
        hypothesis_type: HypothesisType,
        metric: str,
        margin: Optional[float] = None
    ) -> Tuple[str, str]:
        """Generate null and alternative hypothesis statements"""
        
        if hypothesis_type == HypothesisType.SUPERIORITY:
            null = f"H0: {metric}_treatment <= {metric}_control"
            alternative = f"H1: {metric}_treatment > {metric}_control"
            
        elif hypothesis_type == HypothesisType.NON_INFERIORITY:
            margin_str = f"{margin}" if margin else "margin"
            null = f"H0: {metric}_treatment < {metric}_control - {margin_str}"
            alternative = f"H1: {metric}_treatment >= {metric}_control - {margin_str}"
            
        elif hypothesis_type == HypothesisType.EQUIVALENCE:
            margin_str = f"{margin}" if margin else "margin"
            null = f"H0: |{metric}_treatment - {metric}_control| > {margin_str}"
            alternative = f"H1: |{metric}_treatment - {metric}_control| <= {margin_str}"
            
        else:  # TWO_SIDED
            null = f"H0: {metric}_treatment = {metric}_control"
            alternative = f"H1: {metric}_treatment != {metric}_control"
        
        return null, alternative
    
    async def _evaluate_business_significance(
        self,
        observed_difference: float,
        effect_size: float,
        control_metrics: Dict[str, Any],
        treatment_metrics: Dict[str, Any]
    ) -> bool:
        """Evaluate business/practical significance"""
        
        # Business significance thresholds
        min_improvement_threshold = 0.02  # 2% minimum improvement
        min_effect_size_threshold = 0.2   # Small effect size minimum
        
        # Check absolute improvement
        relative_improvement = abs(observed_difference) / abs(control_metrics.get("primary_metric", 1))
        
        # Check effect size
        meaningful_effect = abs(effect_size) >= min_effect_size_threshold
        meaningful_improvement = relative_improvement >= min_improvement_threshold
        
        return meaningful_effect and meaningful_improvement
    
    def _generate_significance_recommendation(
        self,
        is_significant: bool,
        business_significant: bool,
        effect_size: float,
        p_value: float
    ) -> str:
        """Generate recommendation based on significance results"""
        
        if is_significant and business_significant:
            return f"DEPLOY: Statistically significant (p={p_value:.4f}) with meaningful business impact (d={effect_size:.3f})"
        elif is_significant and not business_significant:
            return f"MONITOR: Statistically significant (p={p_value:.4f}) but small practical effect (d={effect_size:.3f})"
        elif not is_significant and business_significant:
            return f"CONTINUE: Large effect observed (d={effect_size:.3f}) but not statistically significant (p={p_value:.4f})"
        else:
            return f"NO CHANGE: Neither statistically nor practically significant (p={p_value:.4f}, d={effect_size:.3f})"
    
    async def _validate_hypothesis_specific(
        self,
        hypothesis: Hypothesis,
        significance_results: Dict[str, Any],
        control_metrics: Dict[str, Any],
        treatment_metrics: Dict[str, Any]
    ) -> bool:
        """Validate hypothesis based on its specific type"""
        
        observed_diff = significance_results["observed_difference"]
        ci_lower, ci_upper = significance_results["confidence_interval"]
        
        if hypothesis.type == HypothesisType.SUPERIORITY:
            # Treatment must be significantly better
            return significance_results["is_significant"] and observed_diff > 0
            
        elif hypothesis.type == HypothesisType.NON_INFERIORITY:
            # Treatment must not be worse than control by more than margin
            margin = hypothesis.margin or 0
            return ci_lower >= -margin
            
        elif hypothesis.type == HypothesisType.EQUIVALENCE:
            # Difference must be within equivalence margin
            margin = hypothesis.margin or 0
            return ci_lower >= -margin and ci_upper <= margin
            
        else:  # TWO_SIDED
            return significance_results["is_significant"]
    
    async def _calculate_achieved_power(
        self,
        hypothesis: Hypothesis,
        significance_results: Dict[str, Any],
        control_metrics: Dict[str, Any],
        treatment_metrics: Dict[str, Any]
    ) -> float:
        """Calculate achieved statistical power"""
        
        effect_size = significance_results["effect_size"]
        n1 = control_metrics.get("sample_size", 1)
        n2 = treatment_metrics.get("sample_size", 1)
        alpha = hypothesis.alpha
        
        # Calculate noncentrality parameter
        n_harmonic = 2 / (1/n1 + 1/n2)
        ncp = effect_size * math.sqrt(n_harmonic / 2)
        
        # Power calculation (approximate)
        from scipy.stats import norm
        z_alpha = norm.ppf(1 - alpha/2)
        power = 1 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)
        
        return max(0, min(1, power))
    
    async def _generate_detailed_recommendation(
        self,
        hypothesis: Hypothesis,
        is_valid: bool,
        significance_results: Dict[str, Any],
        business_significance: bool
    ) -> str:
        """Generate detailed recommendation for hypothesis validation"""
        
        base_rec = self._generate_significance_recommendation(
            is_valid, business_significance,
            significance_results["effect_size"],
            significance_results["p_value"]
        )
        
        # Add hypothesis-specific context
        hypothesis_context = f" (Testing {hypothesis.type.value} hypothesis: {hypothesis.alternative_hypothesis})"
        
        return base_rec + hypothesis_context
    
    async def _calculate_alpha_spending(
        self,
        information_fraction: float,
        total_alpha: float,
        spending_function: str
    ) -> float:
        """Calculate alpha spending for sequential testing"""
        
        t = information_fraction
        
        if spending_function == "obrien_fleming":
            # O'Brien-Fleming spending function
            if t <= 0:
                return 0
            elif t >= 1:
                return total_alpha
            else:
                from scipy.stats import norm
                z_alpha = norm.ppf(1 - total_alpha/2)
                alpha_spent = 2 * (1 - norm.cdf(z_alpha / math.sqrt(t)))
                
        elif spending_function == "pocock":
            # Pocock spending function
            alpha_spent = total_alpha * math.log(1 + (math.e - 1) * t)
            
        else:
            # Linear spending (default)
            alpha_spent = total_alpha * t
        
        return min(alpha_spent, total_alpha)
    
    def _make_sequential_decision(
        self,
        significance_results: Dict[str, Any],
        adjusted_alpha: float,
        information_fraction: float
    ) -> str:
        """Make decision for sequential testing"""
        
        is_significant = significance_results["p_value"] < adjusted_alpha
        
        if is_significant:
            if significance_results["observed_difference"] > 0:
                return "stop_efficacy"  # Stop for efficacy
            else:
                return "stop_futility"  # Stop for futility
        elif information_fraction >= 1.0:
            return "stop_final"  # Final analysis
        else:
            return "continue"  # Continue experiment