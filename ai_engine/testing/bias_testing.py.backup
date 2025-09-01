"""Bias Testing and Fairness Validation Module

This module provides comprehensive bias testing and fairness validation
for AI/ML models to ensure equitable treatment across different groups.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score
from scipy import stats
import json
import uuid

logger = logging.getLogger(__name__)


class FairnessMetric(str, Enum):
    """Fairness metrics enumeration"""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"


class BiasType(str, Enum):
    """Types of bias to detect"""
    DEMOGRAPHIC = "demographic"
    REPRESENTATION = "representation"
    MEASUREMENT = "measurement"
    AGGREGATION = "aggregation"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"


class FairnessThreshold(str, Enum):
    """Fairness thresholds for different environments"""
    STRICT = "0.95"      # 95% fairness threshold
    MODERATE = "0.90"    # 90% fairness threshold
    LENIENT = "0.85"     # 85% fairness threshold


@dataclass
class BiasMetrics:
    """Comprehensive bias and fairness metrics"""
    demographic_parity: float
    equalized_odds: float
    equal_opportunity: float
    calibration_score: float
    disparate_impact: float
    statistical_parity: float
    group_accuracy_differences: Dict[str, float]
    confusion_matrices: Dict[str, np.ndarray]
    fairness_score: float
    bias_detected: bool
    affected_groups: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FairnessTest:
    """Single fairness test configuration and results"""
    test_id: str
    test_name: str
    metric_type: FairnessMetric
    threshold: float
    result: float
    passed: bool
    details: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BiasValidationResult:
    """Complete bias validation result"""
    model_id: str
    validation_id: str
    metrics: BiasMetrics
    individual_tests: List[FairnessTest]
    overall_fairness_score: float
    bias_detected: bool
    critical_issues: List[str]
    recommendations: List[str]
    validation_duration: float
    dataset_info: Dict[str, Any]


class FairnessValidator:
    """Comprehensive fairness and bias validator for AI/ML models"""
    
    def __init__(self, fairness_threshold: float = 0.90):
        """
        Initialize the fairness validator.
        
        Args:
            fairness_threshold: Minimum fairness score threshold (default: 0.90)
        """
        self.fairness_threshold = fairness_threshold
        self.validation_history = {}
        self.logger = logging.getLogger(__name__)
        
    async def validate_model_fairness(
        self,
        model_id: str,
        predictions: np.ndarray,
        ground_truth: np.ndarray,
        sensitive_attributes: Dict[str, np.ndarray],
        model_probabilities: Optional[np.ndarray] = None,
        dataset_info: Optional[Dict[str, Any]] = None
    ) -> BiasValidationResult:
        """
        Comprehensive fairness validation of AI/ML model.
        
        Args:
            model_id: Unique model identifier
            predictions: Model predictions
            ground_truth: Ground truth labels
            sensitive_attributes: Dictionary of sensitive attributes (e.g., {'gender': array, 'race': array})
            model_probabilities: Model prediction probabilities
            dataset_info: Information about the dataset
            
        Returns:
            BiasValidationResult: Comprehensive bias validation result
        """
        start_time = datetime.utcnow()
        validation_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Starting fairness validation for model {model_id}")
            
            # Validate inputs
            self._validate_inputs(predictions, ground_truth, sensitive_attributes)
            
            # Calculate comprehensive bias metrics
            metrics = await self._calculate_bias_metrics(
                predictions, ground_truth, sensitive_attributes, model_probabilities
            )
            
            # Run individual fairness tests
            individual_tests = await self._run_fairness_tests(
                predictions, ground_truth, sensitive_attributes, model_probabilities
            )
            
            # Calculate overall fairness score
            overall_score = self._calculate_overall_fairness_score(metrics, individual_tests)
            
            # Determine if bias is detected
            bias_detected = overall_score < self.fairness_threshold
            
            # Generate critical issues and recommendations
            critical_issues = self._identify_critical_issues(metrics, individual_tests)
            recommendations = self._generate_bias_recommendations(metrics, individual_tests)
            
            # Calculate validation duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Create validation result
            result = BiasValidationResult(
                model_id=model_id,
                validation_id=validation_id,
                metrics=metrics,
                individual_tests=individual_tests,
                overall_fairness_score=overall_score,
                bias_detected=bias_detected,
                critical_issues=critical_issues,
                recommendations=recommendations,
                validation_duration=duration,
                dataset_info=dataset_info or {}
            )
            
            # Store validation history
            if model_id not in self.validation_history:
                self.validation_history[model_id] = []
            self.validation_history[model_id].append(result)
            
            self.logger.info(
                f"Fairness validation completed for model {model_id}: "
                f"Overall Score={overall_score:.4f}, Bias Detected={bias_detected}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Fairness validation failed for model {model_id}: {str(e)}")
            raise
    
    def _validate_inputs(
        self,
        predictions: np.ndarray,
        ground_truth: np.ndarray,
        sensitive_attributes: Dict[str, np.ndarray]
    ):
        """Validate input data for fairness testing"""
        if len(predictions) != len(ground_truth):
            raise ValueError("Predictions and ground truth must have same length")
        
        for attr_name, attr_values in sensitive_attributes.items():
            if len(attr_values) != len(predictions):
                raise ValueError(f"Sensitive attribute '{attr_name}' must have same length as predictions")
    
    async def _calculate_bias_metrics(
        self,
        predictions: np.ndarray,
        ground_truth: np.ndarray,
        sensitive_attributes: Dict[str, np.ndarray],
        model_probabilities: Optional[np.ndarray] = None
    ) -> BiasMetrics:
        """Calculate comprehensive bias and fairness metrics"""
        
        # Initialize results storage
        group_accuracy_differences = {}
        confusion_matrices = {}
        
        # Calculate metrics for each sensitive attribute
        demographic_parity_scores = []
        equalized_odds_scores = []
        equal_opportunity_scores = []
        
        for attr_name, attr_values in sensitive_attributes.items():
            unique_groups = np.unique(attr_values)
            
            if len(unique_groups) < 2:
                continue
            
            # Calculate group-specific metrics
            group_accuracies = {}
            group_cms = {}
            
            for group in unique_groups:
                group_mask = attr_values == group
                group_pred = predictions[group_mask]
                group_true = ground_truth[group_mask]
                
                if len(group_pred) > 0:
                    group_acc = accuracy_score(group_true, group_pred)
                    group_accuracies[str(group)] = group_acc
                    group_cms[str(group)] = confusion_matrix(group_true, group_pred)
            
            group_accuracy_differences[attr_name] = group_accuracies
            confusion_matrices[attr_name] = group_cms
            
            # Demographic Parity (Statistical Parity)
            dp_score = self._calculate_demographic_parity(predictions, attr_values)
            demographic_parity_scores.append(dp_score)
            
            # Equalized Odds
            eo_score = self._calculate_equalized_odds(predictions, ground_truth, attr_values)
            equalized_odds_scores.append(eo_score)
            
            # Equal Opportunity
            eop_score = self._calculate_equal_opportunity(predictions, ground_truth, attr_values)
            equal_opportunity_scores.append(eop_score)
        
        # Aggregate scores across all attributes
        demographic_parity = np.mean(demographic_parity_scores) if demographic_parity_scores else 1.0
        equalized_odds = np.mean(equalized_odds_scores) if equalized_odds_scores else 1.0
        equal_opportunity = np.mean(equal_opportunity_scores) if equal_opportunity_scores else 1.0
        
        # Calibration score (if probabilities available)
        calibration_score = 1.0
        if model_probabilities is not None:
            calibration_score = self._calculate_calibration_score(
                model_probabilities, ground_truth, sensitive_attributes
            )
        
        # Disparate Impact
        disparate_impact = self._calculate_disparate_impact(predictions, sensitive_attributes)
        
        # Statistical Parity
        statistical_parity = demographic_parity  # Same as demographic parity
        
        # Overall fairness score
        fairness_score = np.mean([
            demographic_parity, equalized_odds, equal_opportunity, calibration_score
        ])
        
        # Detect bias
        bias_detected = fairness_score < self.fairness_threshold
        
        # Identify affected groups
        affected_groups = []
        for attr_name, group_accs in group_accuracy_differences.items():
            if len(group_accs) > 1:
                acc_values = list(group_accs.values())
                if max(acc_values) - min(acc_values) > 0.1:  # 10% difference threshold
                    affected_groups.append(attr_name)
        
        return BiasMetrics(
            demographic_parity=demographic_parity,
            equalized_odds=equalized_odds,
            equal_opportunity=equal_opportunity,
            calibration_score=calibration_score,
            disparate_impact=disparate_impact,
            statistical_parity=statistical_parity,
            group_accuracy_differences=group_accuracy_differences,
            confusion_matrices=confusion_matrices,
            fairness_score=fairness_score,
            bias_detected=bias_detected,
            affected_groups=affected_groups
        )
    
    def _calculate_demographic_parity(self, predictions: np.ndarray, sensitive_attr: np.ndarray) -> float:
        """Calculate demographic parity (statistical parity)"""
        unique_groups = np.unique(sensitive_attr)
        if len(unique_groups) < 2:
            return 1.0
        
        positive_rates = []
        for group in unique_groups:
            group_mask = sensitive_attr == group
            if np.sum(group_mask) > 0:
                positive_rate = np.mean(predictions[group_mask])
                positive_rates.append(positive_rate)
        
        if len(positive_rates) < 2:
            return 1.0
        
        # Return the ratio of min to max positive rate
        return min(positive_rates) / max(positive_rates) if max(positive_rates) > 0 else 1.0
    
    def _calculate_equalized_odds(
        self, predictions: np.ndarray, ground_truth: np.ndarray, sensitive_attr: np.ndarray
    ) -> float:
        """Calculate equalized odds fairness metric"""
        unique_groups = np.unique(sensitive_attr)
        if len(unique_groups) < 2:
            return 1.0
        
        tpr_scores = []  # True Positive Rates
        fpr_scores = []  # False Positive Rates
        
        for group in unique_groups:
            group_mask = sensitive_attr == group
            group_pred = predictions[group_mask]
            group_true = ground_truth[group_mask]
            
            if len(group_pred) > 0:
                # Calculate TPR and FPR
                cm = confusion_matrix(group_true, group_pred)
                if cm.shape == (2, 2):
                    tn, fp, fn, tp = cm.ravel()
                    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                    tpr_scores.append(tpr)
                    fpr_scores.append(fpr)
        
        if len(tpr_scores) < 2:
            return 1.0
        
        # Calculate difference in TPR and FPR between groups
        tpr_diff = max(tpr_scores) - min(tpr_scores)
        fpr_diff = max(fpr_scores) - min(fpr_scores)
        
        # Return fairness score (1 - average difference)
        return 1.0 - (tpr_diff + fpr_diff) / 2
    
    def _calculate_equal_opportunity(
        self, predictions: np.ndarray, ground_truth: np.ndarray, sensitive_attr: np.ndarray
    ) -> float:
        """Calculate equal opportunity fairness metric"""
        unique_groups = np.unique(sensitive_attr)
        if len(unique_groups) < 2:
            return 1.0
        
        tpr_scores = []
        
        for group in unique_groups:
            group_mask = sensitive_attr == group
            group_pred = predictions[group_mask]
            group_true = ground_truth[group_mask]
            
            if len(group_pred) > 0:
                # Calculate TPR for positive class
                positive_mask = group_true == 1
                if np.sum(positive_mask) > 0:
                    tpr = np.mean(group_pred[positive_mask] == 1)
                    tpr_scores.append(tpr)
        
        if len(tpr_scores) < 2:
            return 1.0
        
        # Return ratio of min to max TPR
        return min(tpr_scores) / max(tpr_scores) if max(tpr_scores) > 0 else 1.0
    
    def _calculate_calibration_score(
        self, probabilities: np.ndarray, ground_truth: np.ndarray, sensitive_attributes: Dict[str, np.ndarray]
    ) -> float:
        """Calculate calibration fairness score"""
        # Simplified calibration check - in practice, you'd use more sophisticated methods
        calibration_scores = []
        
        for attr_name, attr_values in sensitive_attributes.items():
            unique_groups = np.unique(attr_values)
            
            for group in unique_groups:
                group_mask = attr_values == group
                group_probs = probabilities[group_mask]
                group_true = ground_truth[group_mask]
                
                if len(group_probs) > 10:  # Minimum sample size
                    # Calculate calibration error (simplified)
                    bin_boundaries = np.linspace(0, 1, 11)
                    bin_lowers = bin_boundaries[:-1]
                    bin_uppers = bin_boundaries[1:]
                    
                    ece = 0  # Expected Calibration Error
                    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
                        in_bin = (group_probs > bin_lower) & (group_probs <= bin_upper)
                        prop_in_bin = in_bin.mean()
                        
                        if prop_in_bin > 0:
                            accuracy_in_bin = group_true[in_bin].mean()
                            avg_confidence_in_bin = group_probs[in_bin].mean()
                            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
                    
                    calibration_scores.append(1.0 - ece)  # Convert to fairness score
        
        return np.mean(calibration_scores) if calibration_scores else 1.0
    
    def _calculate_disparate_impact(self, predictions: np.ndarray, sensitive_attributes: Dict[str, np.ndarray]) -> float:
        """Calculate disparate impact ratio"""
        disparate_impacts = []
        
        for attr_name, attr_values in sensitive_attributes.items():
            unique_groups = np.unique(attr_values)
            if len(unique_groups) < 2:
                continue
            
            positive_rates = []
            for group in unique_groups:
                group_mask = attr_values == group
                if np.sum(group_mask) > 0:
                    positive_rate = np.mean(predictions[group_mask])
                    positive_rates.append(positive_rate)
            
            if len(positive_rates) >= 2:
                # Calculate disparate impact as min/max ratio
                di_ratio = min(positive_rates) / max(positive_rates) if max(positive_rates) > 0 else 1.0
                disparate_impacts.append(di_ratio)
        
        return np.mean(disparate_impacts) if disparate_impacts else 1.0
    
    async def _run_fairness_tests(
        self,
        predictions: np.ndarray,
        ground_truth: np.ndarray,
        sensitive_attributes: Dict[str, np.ndarray],
        model_probabilities: Optional[np.ndarray] = None
    ) -> List[FairnessTest]:
        """Run individual fairness tests"""
        tests = []
        
        # Demographic Parity Test
        for attr_name, attr_values in sensitive_attributes.items():
            dp_score = self._calculate_demographic_parity(predictions, attr_values)
            test = FairnessTest(
                test_id=str(uuid.uuid4()),
                test_name=f"Demographic Parity - {attr_name}",
                metric_type=FairnessMetric.DEMOGRAPHIC_PARITY,
                threshold=self.fairness_threshold,
                result=dp_score,
                passed=dp_score >= self.fairness_threshold,
                details={"attribute": attr_name, "score": dp_score}
            )
            tests.append(test)
        
        # Equalized Odds Test
        for attr_name, attr_values in sensitive_attributes.items():
            eo_score = self._calculate_equalized_odds(predictions, ground_truth, attr_values)
            test = FairnessTest(
                test_id=str(uuid.uuid4()),
                test_name=f"Equalized Odds - {attr_name}",
                metric_type=FairnessMetric.EQUALIZED_ODDS,
                threshold=self.fairness_threshold,
                result=eo_score,
                passed=eo_score >= self.fairness_threshold,
                details={"attribute": attr_name, "score": eo_score}
            )
            tests.append(test)
        
        return tests
    
    def _calculate_overall_fairness_score(self, metrics: BiasMetrics, tests: List[FairnessTest]) -> float:
        """Calculate overall fairness score"""
        # Weight different components
        metric_score = metrics.fairness_score * 0.6
        test_score = np.mean([test.result for test in tests]) * 0.4 if tests else 0
        
        return metric_score + test_score
    
    def _identify_critical_issues(self, metrics: BiasMetrics, tests: List[FairnessTest]) -> List[str]:
        """Identify critical fairness issues"""
        issues = []
        
        if metrics.bias_detected:
            issues.append("Overall bias detected in model predictions")
        
        if metrics.demographic_parity < 0.8:
            issues.append("Critical demographic parity violation detected")
        
        if metrics.equalized_odds < 0.8:
            issues.append("Critical equalized odds violation detected")
        
        failed_tests = [test for test in tests if not test.passed]
        if len(failed_tests) > len(tests) / 2:
            issues.append("Majority of fairness tests failed")
        
        return issues
    
    def _generate_bias_recommendations(self, metrics: BiasMetrics, tests: List[FairnessTest]) -> List[str]:
        """Generate recommendations for bias mitigation"""
        recommendations = []
        
        if metrics.bias_detected:
            recommendations.append("Consider implementing bias mitigation techniques")
            recommendations.append("Review training data for representation balance")
        
        if metrics.demographic_parity < self.fairness_threshold:
            recommendations.append("Improve demographic parity through data rebalancing or algorithmic adjustments")
        
        if metrics.equalized_odds < self.fairness_threshold:
            recommendations.append("Address equalized odds violations through post-processing techniques")
        
        if len(metrics.affected_groups) > 0:
            recommendations.append(f"Pay special attention to affected groups: {', '.join(metrics.affected_groups)}")
        
        return recommendations
    
    def get_fairness_history(self, model_id: str) -> List[BiasValidationResult]:
        """Get fairness validation history for a model"""
        return self.validation_history.get(model_id, [])
    
    async def continuous_fairness_monitoring(
        self,
        model_id: str,
        monitoring_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Setup continuous fairness monitoring"""
        config = {
            "model_id": model_id,
            "fairness_threshold": monitoring_config.get("threshold", self.fairness_threshold),
            "monitoring_frequency": monitoring_config.get("frequency", "daily"),
            "alert_on_violations": monitoring_config.get("alerts", True),
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Continuous fairness monitoring setup for model {model_id}")
        return config