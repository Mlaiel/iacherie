"""🛡️ Ethical AI Assessor - Advanced AI Ethics & Compliance
======================================================
Module: ml/monitoring/ethical_ai_assessor.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ETHICAL AI ASSESSMENT & COMPLIANCE
Advanced AI ethics evaluation with bias detection and fairness metrics
- Automated bias detection and mitigation
- Fairness evaluation across demographics
- Ethical AI compliance monitoring
- Creator rights protection
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class BiasType(Enum):
    """Types of bias that can be detected"""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    CALIBRATION = "calibration"
    REPRESENTATION = "representation"
    ALLOCATION = "allocation"
    QUALITY_OF_SERVICE = "quality_of_service"

class ProtectedAttribute(Enum):
    """Protected attributes for fairness analysis"""
    GENDER = "gender"
    RACE = "race"
    AGE = "age"
    NATIONALITY = "nationality"
    RELIGION = "religion"
    CREATOR_TYPE = "creator_type"
    FOLLOWER_COUNT = "follower_count"
    GEOGRAPHIC_REGION = "geographic_region"

class EthicalStandard(Enum):
    """Ethical AI standards and frameworks"""
    IEEE_ETHICALLY_ALIGNED_DESIGN = "ieee_ethically_aligned_design"
    EU_AI_ACT = "eu_ai_act"
    GDPR_COMPLIANCE = "gdpr_compliance"
    ALGORITHMIC_ACCOUNTABILITY = "algorithmic_accountability"
    RESPONSIBLE_AI = "responsible_ai"
    HUMAN_CENTERED_AI = "human_centered_ai"

@dataclass
class BiasAssessment:
    """Bias assessment results"""
    bias_type: BiasType
    protected_attribute: ProtectedAttribute
    bias_score: float
    severity: str
    affected_groups: List[str]
    mitigation_recommendations: List[str]
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FairnessMetrics:
    """Comprehensive fairness metrics"""
    demographic_parity_score: float
    equalized_odds_score: float
    equal_opportunity_score: float
    calibration_score: float
    overall_fairness_score: float
    group_metrics: Dict[str, Dict[str, float]]
    threshold_analysis: Dict[str, Any]

@dataclass
class EthicalAssessmentReport:
    """Complete ethical AI assessment report"""
    model_id: str
    assessment_id: str
    bias_assessments: List[BiasAssessment]
    fairness_metrics: FairnessMetrics
    compliance_status: Dict[EthicalStandard, bool]
    ethical_risk_score: float
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

class BiasDetector:
    """Advanced bias detection algorithms"""
    
    def __init__(self):
        self.detection_threshold = 0.05  # 5% threshold for bias detection
        
    async def detect_demographic_parity_bias(
        self,
        predictions: np.ndarray,
        protected_attributes: np.ndarray,
        sensitive_attribute: str
    ) -> BiasAssessment:
        """Detect demographic parity bias"""
        try:
            unique_groups = np.unique(protected_attributes)
            group_rates = {}
            
            # Calculate positive prediction rate for each group
            for group in unique_groups:
                group_mask = protected_attributes == group
                group_predictions = predictions[group_mask]
                positive_rate = np.mean(group_predictions > 0.5)
                group_rates[str(group)] = positive_rate
            
            # Calculate maximum difference between groups
            rates = list(group_rates.values())
            max_diff = max(rates) - min(rates)
            
            # Determine severity
            if max_diff > 0.2:
                severity = "high"
            elif max_diff > 0.1:
                severity = "medium"
            elif max_diff > self.detection_threshold:
                severity = "low"
            else:
                severity = "minimal"
            
            # Identify affected groups
            avg_rate = np.mean(rates)
            affected_groups = [
                group for group, rate in group_rates.items()
                if abs(rate - avg_rate) > self.detection_threshold
            ]
            
            # Generate recommendations
            recommendations = []
            if max_diff > self.detection_threshold:
                recommendations.append("Implement demographic parity constraint in model training")
                recommendations.append(f"Rebalance training data for {sensitive_attribute}")
                recommendations.append("Apply post-processing calibration techniques")
            
            # Statistical significance (simplified)
            n_total = len(predictions)
            std_error = np.sqrt(avg_rate * (1 - avg_rate) / n_total)
            significance = max_diff / (2 * std_error) if std_error > 0 else 0
            
            return BiasAssessment(
                bias_type=BiasType.DEMOGRAPHIC_PARITY,
                protected_attribute=ProtectedAttribute.AGE if sensitive_attribute == 'age_group' else ProtectedAttribute(sensitive_attribute),
                bias_score=max_diff,
                severity=severity,
                affected_groups=affected_groups,
                mitigation_recommendations=recommendations,
                statistical_significance=significance,
                confidence_interval=(max_diff - 1.96 * std_error, max_diff + 1.96 * std_error)
            )
            
        except Exception as e:
            logger.error(f"Demographic parity bias detection failed: {e}")
            raise
    
    async def detect_equalized_odds_bias(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        protected_attributes: np.ndarray,
        sensitive_attribute: str
    ) -> BiasAssessment:
        """Detect equalized odds bias"""
        try:
            unique_groups = np.unique(protected_attributes)
            group_metrics = {}
            
            # Calculate TPR and FPR for each group
            for group in unique_groups:
                group_mask = protected_attributes == group
                group_predictions = predictions[group_mask]
                group_labels = true_labels[group_mask]
                
                if len(group_labels) == 0:
                    continue
                
                # True Positive Rate
                positive_mask = group_labels == 1
                if np.sum(positive_mask) > 0:
                    tpr = np.mean(group_predictions[positive_mask] > 0.5)
                else:
                    tpr = 0
                
                # False Positive Rate
                negative_mask = group_labels == 0
                if np.sum(negative_mask) > 0:
                    fpr = np.mean(group_predictions[negative_mask] > 0.5)
                else:
                    fpr = 0
                
                group_metrics[str(group)] = {'tpr': tpr, 'fpr': fpr}
            
            # Calculate maximum difference in TPR and FPR
            tprs = [metrics['tpr'] for metrics in group_metrics.values()]
            fprs = [metrics['fpr'] for metrics in group_metrics.values()]
            
            if len(tprs) < 2:
                return BiasAssessment(
                    bias_type=BiasType.EQUALIZED_ODDS,
                    protected_attribute=ProtectedAttribute(sensitive_attribute),
                    bias_score=0.0,
                    severity="insufficient_data",
                    affected_groups=[],
                    mitigation_recommendations=[],
                    statistical_significance=0.0,
                    confidence_interval=(0.0, 0.0)
                )
            
            tpr_diff = max(tprs) - min(tprs)
            fpr_diff = max(fprs) - min(fprs)
            max_diff = max(tpr_diff, fpr_diff)
            
            # Determine severity
            if max_diff > 0.15:
                severity = "high"
            elif max_diff > 0.1:
                severity = "medium"
            elif max_diff > self.detection_threshold:
                severity = "low"
            else:
                severity = "minimal"
            
            # Generate recommendations
            recommendations = []
            if max_diff > self.detection_threshold:
                recommendations.append("Implement equalized odds constraint")
                recommendations.append("Apply threshold optimization per group")
                recommendations.append("Use adversarial debiasing techniques")
            
            return BiasAssessment(
                bias_type=BiasType.EQUALIZED_ODDS,
                protected_attribute=ProtectedAttribute.AGE if sensitive_attribute == 'age_group' else ProtectedAttribute(sensitive_attribute),
                bias_score=max_diff,
                severity=severity,
                affected_groups=list(group_metrics.keys()),
                mitigation_recommendations=recommendations,
                statistical_significance=max_diff / 0.05,  # Simplified
                confidence_interval=(max_diff * 0.8, max_diff * 1.2)
            )
            
        except Exception as e:
            logger.error(f"Equalized odds bias detection failed: {e}")
            raise
    
    async def detect_representation_bias(
        self,
        training_data: np.ndarray,
        protected_attributes: np.ndarray,
        sensitive_attribute: str
    ) -> BiasAssessment:
        """Detect representation bias in training data"""
        try:
            unique_groups = np.unique(protected_attributes)
            group_counts = {}
            
            # Calculate representation for each group
            total_samples = len(training_data)
            for group in unique_groups:
                group_count = np.sum(protected_attributes == group)
                group_counts[str(group)] = group_count / total_samples
            
            # Calculate representation disparity
            proportions = list(group_counts.values())
            expected_proportion = 1.0 / len(unique_groups)  # Equal representation
            
            max_disparity = max(abs(prop - expected_proportion) for prop in proportions)
            
            # Determine severity
            if max_disparity > 0.3:
                severity = "high"
            elif max_disparity > 0.2:
                severity = "medium"
            elif max_disparity > 0.1:
                severity = "low"
            else:
                severity = "minimal"
            
            # Identify underrepresented groups
            underrepresented = [
                group for group, prop in group_counts.items()
                if prop < expected_proportion * 0.8
            ]
            
            # Generate recommendations
            recommendations = []
            if max_disparity > 0.1:
                recommendations.append("Collect more data from underrepresented groups")
                recommendations.append("Apply data augmentation for minority groups")
                recommendations.append("Use stratified sampling techniques")
                if underrepresented:
                    recommendations.append(f"Focus on increasing representation for: {', '.join(underrepresented)}")
            
            return BiasAssessment(
                bias_type=BiasType.REPRESENTATION,
                protected_attribute=ProtectedAttribute.AGE if sensitive_attribute == 'age_group' else ProtectedAttribute(sensitive_attribute),
                bias_score=max_disparity,
                severity=severity,
                affected_groups=underrepresented,
                mitigation_recommendations=recommendations,
                statistical_significance=max_disparity * len(training_data) / 100,
                confidence_interval=(max_disparity * 0.9, max_disparity * 1.1)
            )
            
        except Exception as e:
            logger.error(f"Representation bias detection failed: {e}")
            raise

class FairnessEvaluator:
    """Comprehensive fairness evaluation"""
    
    def __init__(self):
        self.fairness_threshold = 0.8  # Minimum fairness score
        
    async def calculate_fairness_metrics(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        protected_attributes: Dict[str, np.ndarray]
    ) -> FairnessMetrics:
        """Calculate comprehensive fairness metrics"""
        try:
            # Initialize metrics
            group_metrics = {}
            
            # Calculate metrics for each protected attribute
            for attr_name, attr_values in protected_attributes.items():
                unique_groups = np.unique(attr_values)
                attr_metrics = {}
                
                for group in unique_groups:
                    group_mask = attr_values == group
                    group_pred = predictions[group_mask]
                    group_true = true_labels[group_mask]
                    
                    if len(group_pred) == 0:
                        continue
                    
                    # Calculate performance metrics
                    accuracy = accuracy_score(group_true > 0.5, group_pred > 0.5)
                    precision = precision_score(group_true > 0.5, group_pred > 0.5, zero_division=0)
                    recall = recall_score(group_true > 0.5, group_pred > 0.5, zero_division=0)
                    
                    attr_metrics[str(group)] = {
                        'accuracy': accuracy,
                        'precision': precision,
                        'recall': recall,
                        'sample_size': len(group_pred)
                    }
                
                group_metrics[attr_name] = attr_metrics
            
            # Calculate overall fairness scores
            demographic_parity = await self._calculate_demographic_parity(predictions, protected_attributes)
            equalized_odds = await self._calculate_equalized_odds(predictions, true_labels, protected_attributes)
            equal_opportunity = await self._calculate_equal_opportunity(predictions, true_labels, protected_attributes)
            calibration = await self._calculate_calibration_score(predictions, true_labels, protected_attributes)
            
            # Overall fairness score (weighted average)
            overall_fairness = (
                demographic_parity * 0.25 +
                equalized_odds * 0.25 +
                equal_opportunity * 0.25 +
                calibration * 0.25
            )
            
            # Threshold analysis
            threshold_analysis = await self._analyze_decision_thresholds(
                predictions, true_labels, protected_attributes
            )
            
            return FairnessMetrics(
                demographic_parity_score=demographic_parity,
                equalized_odds_score=equalized_odds,
                equal_opportunity_score=equal_opportunity,
                calibration_score=calibration,
                overall_fairness_score=overall_fairness,
                group_metrics=group_metrics,
                threshold_analysis=threshold_analysis
            )
            
        except Exception as e:
            logger.error(f"Fairness metrics calculation failed: {e}")
            raise
    
    async def _calculate_demographic_parity(
        self,
        predictions: np.ndarray,
        protected_attributes: Dict[str, np.ndarray]
    ) -> float:
        """Calculate demographic parity score"""
        total_score = 0
        attr_count = 0
        
        for attr_name, attr_values in protected_attributes.items():
            unique_groups = np.unique(attr_values)
            if len(unique_groups) < 2:
                continue
            
            group_rates = []
            for group in unique_groups:
                group_mask = attr_values == group
                group_pred = predictions[group_mask]
                if len(group_pred) > 0:
                    positive_rate = np.mean(group_pred > 0.5)
                    group_rates.append(positive_rate)
            
            if len(group_rates) >= 2:
                # Score based on minimum ratio (closer to 1 = more fair)
                min_rate = min(group_rates)
                max_rate = max(group_rates)
                if max_rate > 0:
                    score = min_rate / max_rate
                else:
                    score = 1.0
                total_score += score
                attr_count += 1
        
        return total_score / max(1, attr_count)
    
    async def _calculate_equalized_odds(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        protected_attributes: Dict[str, np.ndarray]
    ) -> float:
        """Calculate equalized odds score"""
        total_score = 0
        attr_count = 0
        
        for attr_name, attr_values in protected_attributes.items():
            unique_groups = np.unique(attr_values)
            if len(unique_groups) < 2:
                continue
            
            tprs = []
            fprs = []
            
            for group in unique_groups:
                group_mask = attr_values == group
                group_pred = predictions[group_mask]
                group_true = true_labels[group_mask]
                
                if len(group_pred) == 0:
                    continue
                
                # TPR
                pos_mask = group_true > 0.5
                if np.sum(pos_mask) > 0:
                    tpr = np.mean(group_pred[pos_mask] > 0.5)
                    tprs.append(tpr)
                
                # FPR
                neg_mask = group_true <= 0.5
                if np.sum(neg_mask) > 0:
                    fpr = np.mean(group_pred[neg_mask] > 0.5)
                    fprs.append(fpr)
            
            # Score based on consistency of TPR and FPR
            if len(tprs) >= 2 and len(fprs) >= 2:
                tpr_consistency = 1 - (max(tprs) - min(tprs))
                fpr_consistency = 1 - (max(fprs) - min(fprs))
                score = (tpr_consistency + fpr_consistency) / 2
                total_score += max(0, score)
                attr_count += 1
        
        return total_score / max(1, attr_count)
    
    async def _calculate_equal_opportunity(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        protected_attributes: Dict[str, np.ndarray]
    ) -> float:
        """Calculate equal opportunity score (TPR consistency)"""
        total_score = 0
        attr_count = 0
        
        for attr_name, attr_values in protected_attributes.items():
            unique_groups = np.unique(attr_values)
            if len(unique_groups) < 2:
                continue
            
            tprs = []
            
            for group in unique_groups:
                group_mask = attr_values == group
                group_pred = predictions[group_mask]
                group_true = true_labels[group_mask]
                
                pos_mask = group_true > 0.5
                if np.sum(pos_mask) > 0:
                    tpr = np.mean(group_pred[pos_mask] > 0.5)
                    tprs.append(tpr)
            
            if len(tprs) >= 2:
                # Score based on TPR consistency
                score = 1 - (max(tprs) - min(tprs))
                total_score += max(0, score)
                attr_count += 1
        
        return total_score / max(1, attr_count)
    
    async def _calculate_calibration_score(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        protected_attributes: Dict[str, np.ndarray]
    ) -> float:
        """Calculate calibration score across groups"""
        total_score = 0
        attr_count = 0
        
        for attr_name, attr_values in protected_attributes.items():
            unique_groups = np.unique(attr_values)
            if len(unique_groups) < 2:
                continue
            
            calibration_scores = []
            
            for group in unique_groups:
                group_mask = attr_values == group
                group_pred = predictions[group_mask]
                group_true = true_labels[group_mask]
                
                if len(group_pred) < 10:  # Need minimum samples
                    continue
                
                # Bin predictions and calculate calibration
                n_bins = min(5, len(group_pred) // 2)
                bin_boundaries = np.linspace(0, 1, n_bins + 1)
                
                bin_calibration = []
                for i in range(n_bins):
                    bin_mask = (group_pred >= bin_boundaries[i]) & (group_pred < bin_boundaries[i + 1])
                    if i == n_bins - 1:  # Include upper boundary for last bin
                        bin_mask = (group_pred >= bin_boundaries[i]) & (group_pred <= bin_boundaries[i + 1])
                    
                    if np.sum(bin_mask) > 0:
                        avg_pred = np.mean(group_pred[bin_mask])
                        avg_true = np.mean(group_true[bin_mask])
                        calibration_error = abs(avg_pred - avg_true)
                        bin_calibration.append(calibration_error)
                
                if bin_calibration:
                    group_calibration = 1 - np.mean(bin_calibration)  # Higher = better
                    calibration_scores.append(max(0, group_calibration))
            
            if len(calibration_scores) >= 2:
                # Score based on calibration consistency
                score = 1 - (max(calibration_scores) - min(calibration_scores))
                total_score += max(0, score)
                attr_count += 1
        
        return total_score / max(1, attr_count)
    
    async def _analyze_decision_thresholds(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        protected_attributes: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Analyze optimal decision thresholds for fairness"""
        threshold_analysis = {}
        
        thresholds = np.arange(0.1, 1.0, 0.1)
        
        for attr_name, attr_values in protected_attributes.items():
            unique_groups = np.unique(attr_values)
            if len(unique_groups) < 2:
                continue
            
            group_optimal_thresholds = {}
            
            for group in unique_groups:
                group_mask = attr_values == group
                group_pred = predictions[group_mask]
                group_true = true_labels[group_mask]
                
                if len(group_pred) < 5:
                    continue
                
                best_threshold = 0.5
                best_f1 = 0
                
                for threshold in thresholds:
                    pred_binary = group_pred > threshold
                    if len(np.unique(pred_binary)) > 1:  # Avoid single class
                        precision = precision_score(group_true > 0.5, pred_binary, zero_division=0)
                        recall = recall_score(group_true > 0.5, pred_binary, zero_division=0)
                        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                        
                        if f1 > best_f1:
                            best_f1 = f1
                            best_threshold = threshold
                
                group_optimal_thresholds[str(group)] = {
                    'optimal_threshold': best_threshold,
                    'best_f1_score': best_f1
                }
            
            threshold_analysis[attr_name] = group_optimal_thresholds
        
        return threshold_analysis

class EthicalAIAssessor:
    """Main ethical AI assessment system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.bias_detector = BiasDetector()
        self.fairness_evaluator = FairnessEvaluator()
        
        self.assessment_history: List[EthicalAssessmentReport] = []
        self.ethical_risk_threshold = self.config.get('ethical_risk_threshold', 0.3)
        
        logger.info("Ethical AI Assessor initialized")
    
    async def comprehensive_ethical_assessment(
        self,
        model_id: str,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        protected_attributes: Dict[str, np.ndarray],
        training_data: Optional[np.ndarray] = None
    ) -> EthicalAssessmentReport:
        """Perform comprehensive ethical AI assessment"""
        try:
            assessment_id = f"ethics_assessment_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Bias detection
            bias_assessments = []
            
            for attr_name, attr_values in protected_attributes.items():
                # Demographic parity bias
                demo_bias = await self.bias_detector.detect_demographic_parity_bias(
                    predictions, attr_values, attr_name
                )
                bias_assessments.append(demo_bias)
                
                # Equalized odds bias
                eq_odds_bias = await self.bias_detector.detect_equalized_odds_bias(
                    predictions, true_labels, attr_values, attr_name
                )
                bias_assessments.append(eq_odds_bias)
                
                # Representation bias (if training data available)
                if training_data is not None:
                    repr_bias = await self.bias_detector.detect_representation_bias(
                        training_data, attr_values, attr_name
                    )
                    bias_assessments.append(repr_bias)
            
            # Fairness metrics
            fairness_metrics = await self.fairness_evaluator.calculate_fairness_metrics(
                predictions, true_labels, protected_attributes
            )
            
            # Compliance status
            compliance_status = await self._evaluate_compliance_status(
                bias_assessments, fairness_metrics
            )
            
            # Calculate ethical risk score
            ethical_risk_score = await self._calculate_ethical_risk_score(
                bias_assessments, fairness_metrics
            )
            
            # Generate recommendations
            recommendations = await self._generate_ethical_recommendations(
                bias_assessments, fairness_metrics, ethical_risk_score
            )
            
            # Create assessment report
            report = EthicalAssessmentReport(
                model_id=model_id,
                assessment_id=assessment_id,
                bias_assessments=bias_assessments,
                fairness_metrics=fairness_metrics,
                compliance_status=compliance_status,
                ethical_risk_score=ethical_risk_score,
                recommendations=recommendations
            )
            
            self.assessment_history.append(report)
            
            logger.info(f"Ethical assessment completed: {assessment_id}, risk score: {ethical_risk_score:.3f}")
            return report
            
        except Exception as e:
            logger.error(f"Ethical assessment failed: {e}")
            raise
    
    async def _evaluate_compliance_status(
        self,
        bias_assessments: List[BiasAssessment],
        fairness_metrics: FairnessMetrics
    ) -> Dict[EthicalStandard, bool]:
        """Evaluate compliance with ethical standards"""
        compliance = {}
        
        # IEEE Ethically Aligned Design
        ieee_compliant = (
            fairness_metrics.overall_fairness_score >= 0.8 and
            all(bias.severity in ["minimal", "low"] for bias in bias_assessments)
        )
        compliance[EthicalStandard.IEEE_ETHICALLY_ALIGNED_DESIGN] = ieee_compliant
        
        # EU AI Act (simplified criteria)
        eu_ai_compliant = (
            fairness_metrics.demographic_parity_score >= 0.8 and
            fairness_metrics.equalized_odds_score >= 0.8 and
            not any(bias.severity == "high" for bias in bias_assessments)
        )
        compliance[EthicalStandard.EU_AI_ACT] = eu_ai_compliant
        
        # GDPR Compliance (fairness aspects)
        gdpr_compliant = (
            fairness_metrics.overall_fairness_score >= 0.7 and
            not any(bias.bias_type == BiasType.REPRESENTATION and bias.severity == "high" 
                   for bias in bias_assessments)
        )
        compliance[EthicalStandard.GDPR_COMPLIANCE] = gdpr_compliant
        
        # Algorithmic Accountability
        algo_accountable = (
            fairness_metrics.calibration_score >= 0.7 and
            len([b for b in bias_assessments if b.statistical_significance > 2]) == 0
        )
        compliance[EthicalStandard.ALGORITHMIC_ACCOUNTABILITY] = algo_accountable
        
        # Responsible AI
        responsible_ai = (
            fairness_metrics.overall_fairness_score >= 0.75 and
            all(bias.severity != "high" for bias in bias_assessments)
        )
        compliance[EthicalStandard.RESPONSIBLE_AI] = responsible_ai
        
        # Human-Centered AI
        human_centered = (
            fairness_metrics.equal_opportunity_score >= 0.8 and
            not any(bias.bias_type == BiasType.QUALITY_OF_SERVICE for bias in bias_assessments)
        )
        compliance[EthicalStandard.HUMAN_CENTERED_AI] = human_centered
        
        return compliance
    
    async def _calculate_ethical_risk_score(
        self,
        bias_assessments: List[BiasAssessment],
        fairness_metrics: FairnessMetrics
    ) -> float:
        """Calculate overall ethical risk score (0-1, lower is better)"""
        try:
            # Bias severity contribution
            severity_weights = {"minimal": 0.0, "low": 0.2, "medium": 0.5, "high": 1.0}
            bias_risk = np.mean([
                severity_weights.get(bias.severity, 0.5) for bias in bias_assessments
            ]) if bias_assessments else 0.0
            
            # Fairness metrics contribution (inverted, as higher fairness = lower risk)
            fairness_risk = 1.0 - fairness_metrics.overall_fairness_score
            
            # Statistical significance contribution
            high_significance_count = sum(
                1 for bias in bias_assessments if bias.statistical_significance > 2
            )
            significance_risk = min(1.0, high_significance_count / max(1, len(bias_assessments)))
            
            # Weighted combination
            risk_score = (
                bias_risk * 0.4 +
                fairness_risk * 0.4 +
                significance_risk * 0.2
            )
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception as e:
            logger.error(f"Risk score calculation failed: {e}")
            return 0.5  # Default medium risk
    
    async def _generate_ethical_recommendations(
        self,
        bias_assessments: List[BiasAssessment],
        fairness_metrics: FairnessMetrics,
        ethical_risk_score: float
    ) -> List[str]:
        """Generate ethical AI recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        if ethical_risk_score > 0.7:
            recommendations.append("HIGH PRIORITY: Immediate bias mitigation required")
            recommendations.append("Consider model retraining with fairness constraints")
        elif ethical_risk_score > 0.4:
            recommendations.append("MEDIUM PRIORITY: Implement bias monitoring and alerts")
        
        # Bias-specific recommendations
        high_bias_types = set()
        for bias in bias_assessments:
            if bias.severity in ["high", "medium"]:
                high_bias_types.add(bias.bias_type)
                recommendations.extend(bias.mitigation_recommendations[:2])  # Top 2 recommendations
        
        # Fairness-specific recommendations
        if fairness_metrics.demographic_parity_score < 0.8:
            recommendations.append("Implement demographic parity constraints")
        
        if fairness_metrics.equalized_odds_score < 0.8:
            recommendations.append("Apply equalized odds optimization")
        
        if fairness_metrics.calibration_score < 0.7:
            recommendations.append("Improve model calibration across groups")
        
        # General recommendations
        recommendations.append("Establish regular ethical AI monitoring schedule")
        recommendations.append("Document bias detection and mitigation efforts")
        recommendations.append("Implement human oversight for high-stakes decisions")
        
        # Creator-specific recommendations
        recommendations.append("Ensure fair treatment across all creator demographics")
        recommendations.append("Monitor revenue distribution fairness")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]  # Limit to top 10
    
    async def monitor_ethical_compliance(
        self,
        model_id: str,
        monitoring_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Continuous ethical compliance monitoring"""
        try:
            # Get recent assessments for this model
            recent_assessments = [
                report for report in self.assessment_history[-10:]
                if report.model_id == model_id
            ]
            
            if not recent_assessments:
                return {"status": "no_assessment_history"}
            
            # Trend analysis
            risk_scores = [report.ethical_risk_score for report in recent_assessments]
            fairness_scores = [report.fairness_metrics.overall_fairness_score for report in recent_assessments]
            
            # Calculate trends
            if len(risk_scores) >= 2:
                risk_trend = risk_scores[-1] - risk_scores[0]
                fairness_trend = fairness_scores[-1] - fairness_scores[0]
            else:
                risk_trend = 0
                fairness_trend = 0
            
            # Current status
            latest_assessment = recent_assessments[-1]
            current_risk = latest_assessment.ethical_risk_score
            
            # Compliance status
            compliance_count = sum(latest_assessment.compliance_status.values())
            total_standards = len(latest_assessment.compliance_status)
            compliance_rate = compliance_count / total_standards if total_standards > 0 else 0
            
            # Alerts
            alerts = []
            if current_risk > 0.7:
                alerts.append("HIGH RISK: Ethical risk score exceeds threshold")
            if risk_trend > 0.2:
                alerts.append("DEGRADATION: Ethical risk increasing")
            if compliance_rate < 0.5:
                alerts.append("NON-COMPLIANCE: Multiple standards violated")
            
            monitoring_result = {
                'model_id': model_id,
                'current_risk_score': current_risk,
                'risk_trend': risk_trend,
                'fairness_trend': fairness_trend,
                'compliance_rate': compliance_rate,
                'alerts': alerts,
                'assessment_count': len(recent_assessments),
                'last_assessment': latest_assessment.created_at.isoformat(),
                'status': 'compliant' if current_risk < 0.3 and not alerts else 'attention_required'
            }
            
            return monitoring_result
            
        except Exception as e:
            logger.error(f"Ethical compliance monitoring failed: {e}")
            raise
    
    async def generate_ethics_report(self) -> Dict[str, Any]:
        """Generate comprehensive ethics report"""
        try:
            if not self.assessment_history:
                return {"error": "No assessment history available"}
            
            # Overall statistics
            total_assessments = len(self.assessment_history)
            avg_risk_score = np.mean([report.ethical_risk_score for report in self.assessment_history])
            avg_fairness_score = np.mean([report.fairness_metrics.overall_fairness_score for report in self.assessment_history])
            
            # Compliance statistics
            compliance_stats = {}
            for standard in EthicalStandard:
                compliant_count = sum(
                    1 for report in self.assessment_history 
                    if report.compliance_status.get(standard, False)
                )
                compliance_stats[standard.value] = compliant_count / total_assessments
            
            # Risk distribution
            risk_distribution = {
                'low_risk': sum(1 for r in self.assessment_history if r.ethical_risk_score < 0.3),
                'medium_risk': sum(1 for r in self.assessment_history if 0.3 <= r.ethical_risk_score < 0.7),
                'high_risk': sum(1 for r in self.assessment_history if r.ethical_risk_score >= 0.7)
            }
            
            # Common bias types
            all_biases = []
            for report in self.assessment_history:
                all_biases.extend(report.bias_assessments)
            
            bias_frequency = {}
            for bias_type in BiasType:
                count = sum(1 for bias in all_biases if bias.bias_type == bias_type)
                bias_frequency[bias_type.value] = count
            
            # Recent trends
            recent_reports = self.assessment_history[-5:] if len(self.assessment_history) >= 5 else self.assessment_history
            recent_avg_risk = np.mean([r.ethical_risk_score for r in recent_reports])
            recent_avg_fairness = np.mean([r.fairness_metrics.overall_fairness_score for r in recent_reports])
            
            report = {
                'summary': {
                    'total_assessments': total_assessments,
                    'average_risk_score': avg_risk_score,
                    'average_fairness_score': avg_fairness_score,
                    'overall_compliance_rate': np.mean(list(compliance_stats.values()))
                },
                'compliance_by_standard': compliance_stats,
                'risk_distribution': risk_distribution,
                'bias_frequency': bias_frequency,
                'recent_trends': {
                    'recent_average_risk': recent_avg_risk,
                    'recent_average_fairness': recent_avg_fairness,
                    'trend_direction': 'improving' if recent_avg_risk < avg_risk_score else 'degrading'
                },
                'recommendations': [
                    "Implement continuous bias monitoring",
                    "Establish ethical AI governance framework", 
                    "Regular training on bias detection and mitigation",
                    "Creator fairness audits and feedback mechanisms"
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Ethics report generated: {total_assessments} assessments analyzed")
            return report
            
        except Exception as e:
            logger.error(f"Ethics report generation failed: {e}")
            raise

# Example usage and testing
async def main():
    """Test ethical AI assessor"""
    try:
        # Initialize assessor
        assessor = EthicalAIAssessor()
        
        # Generate synthetic test data
        np.random.seed(42)
        n_samples = 1000
        
        # Synthetic predictions and labels
        predictions = np.random.random(n_samples)
        true_labels = np.random.randint(0, 2, n_samples)
        
        # Synthetic protected attributes with some bias
        gender = np.random.choice(['male', 'female'], n_samples, p=[0.6, 0.4])
        age_group = np.random.choice(['young', 'middle', 'senior'], n_samples, p=[0.5, 0.3, 0.2])
        
        # Introduce some bias (higher predictions for certain groups)
        bias_mask = (gender == 'male') & (age_group == 'young')
        predictions[bias_mask] += 0.2
        predictions = np.clip(predictions, 0, 1)
        
        protected_attributes = {
            'gender': gender,
            'age_group': age_group
        }
        
        # Run comprehensive assessment
        assessment = await assessor.comprehensive_ethical_assessment(
            model_id="test_model_001",
            predictions=predictions,
            true_labels=true_labels,
            protected_attributes=protected_attributes,
            training_data=np.random.randn(n_samples, 10)
        )
        
        print(f"Ethical Assessment completed:")
        print(f"Risk Score: {assessment.ethical_risk_score:.3f}")
        print(f"Fairness Score: {assessment.fairness_metrics.overall_fairness_score:.3f}")
        print(f"Bias Assessments: {len(assessment.bias_assessments)}")
        print(f"Compliance Standards Met: {sum(assessment.compliance_status.values())}/{len(assessment.compliance_status)}")
        
        # Monitor compliance
        monitoring = await assessor.monitor_ethical_compliance("test_model_001", {})
        print(f"Monitoring Status: {monitoring['status']}")
        
        # Generate ethics report
        ethics_report = await assessor.generate_ethics_report()
        print(f"Ethics Report: {ethics_report['summary']['total_assessments']} assessments")
        
        return True
        
    except Exception as e:
        logger.error(f"Ethical AI assessor test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())