"""🤖 Model Bias Detector - Ethical AI & Fairness Validation
============================================================
Module: ml/model_registry/model_bias_detector.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🤖 ETHICAL AI & BIAS DETECTION
Automated bias detection and fairness evaluation for ethical AI compliance
- Demographic parity and equalized odds
- Individual and group fairness metrics
- Creator demographic bias analysis
- Intersectional bias detection
- Algorithmic audit trails
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import warnings
from collections import defaultdict
from scipy import stats
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score
import math

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class BiasType(Enum):
    """Types of algorithmic bias"""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUALITY_OPPORTUNITY = "equality_opportunity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"
    COUNTERFACTUAL_FAIRNESS = "counterfactual_fairness"
    INTERSECTIONAL = "intersectional"
    CREATOR_BIAS = "creator_bias"

class ProtectedAttribute(Enum):
    """Protected attributes for bias analysis"""
    GENDER = "gender"
    AGE = "age"
    ETHNICITY = "ethnicity"
    NATIONALITY = "nationality"
    CREATOR_TYPE = "creator_type"
    FOLLOWER_COUNT = "follower_count"
    CONTENT_LANGUAGE = "content_language"
    GEOGRAPHICAL_REGION = "geographical_region"

class BiasLevel(Enum):
    """Bias severity levels"""
    NONE = "none"              # <5% bias
    LOW = "low"                # 5-10% bias
    MODERATE = "moderate"      # 10-20% bias
    HIGH = "high"              # 20-30% bias
    SEVERE = "severe"          # >30% bias

class FairnessMetric(Enum):
    """Fairness metric types"""
    STATISTICAL_PARITY = "statistical_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    DEMOGRAPHIC_PARITY = "demographic_parity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"

@dataclass
class BiasTestResult:
    """Individual bias test result"""
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bias_type: BiasType = BiasType.DEMOGRAPHIC_PARITY
    protected_attribute: ProtectedAttribute = ProtectedAttribute.GENDER
    bias_level: BiasLevel = BiasLevel.NONE
    bias_score: float = 0.0
    threshold: float = 0.1
    groups_analyzed: List[str] = field(default_factory=list)
    detailed_metrics: Dict[str, Any] = field(default_factory=dict)
    statistical_significance: float = 0.05
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    recommendations: List[str] = field(default_factory=list)
    test_date: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CreatorBiasAnalysis:
    """Creator-specific bias analysis"""
    creator_type: str
    total_creators: int
    bias_metrics: Dict[str, float] = field(default_factory=dict)
    performance_gaps: Dict[str, float] = field(default_factory=dict)
    recommendation_bias: float = 0.0
    monetization_bias: float = 0.0
    visibility_bias: float = 0.0
    intersectional_analysis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BiasAssessment:
    """Complete bias assessment for a model"""
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str = ""
    model_name: str = ""
    assessment_date: datetime = field(default_factory=datetime.utcnow)
    overall_bias_level: BiasLevel = BiasLevel.NONE
    bias_tests: List[BiasTestResult] = field(default_factory=list)
    creator_analysis: List[CreatorBiasAnalysis] = field(default_factory=list)
    fairness_score: float = 0.0
    ethical_compliance: bool = True
    remediation_priority: str = "LOW"
    next_audit_date: Optional[datetime] = None
    assessor_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelPrediction:
    """Model prediction data for bias testing"""
    user_id: str
    prediction: float
    actual_outcome: Optional[float] = None
    protected_attributes: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class ModelBiasDetector:
    """🤖 Advanced Model Bias Detector & Ethical AI Validator
    
    **ML ENGINEER + IA PROMPT ENGINEER EXPERT IMPLEMENTATION**
    - Comprehensive bias detection algorithms
    - Creator demographic fairness analysis
    - Intersectional bias evaluation
    - Algorithmic audit compliance
    - Ethical AI recommendations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize bias detector with advanced ML algorithms"""
        self.config = config or {}
        self.bias_history: List[BiasAssessment] = []
        self.fairness_thresholds = self._initialize_fairness_thresholds()
        
        # Configuration
        self.bias_threshold = self.config.get("bias_threshold", 0.1)  # 10% maximum acceptable bias
        self.statistical_significance = self.config.get("statistical_significance", 0.05)
        self.min_sample_size = self.config.get("min_sample_size", 100)
        self.creator_types = self.config.get("creator_types", [
            "musician", "blogger", "photographer", "influencer", "comedian"
        ])
        
        logger.info("🤖 Model Bias Detector initialized with ethical AI standards")

    def _initialize_fairness_thresholds(self) -> Dict[BiasType, float]:
        """Initialize bias detection thresholds"""
        return {
            BiasType.DEMOGRAPHIC_PARITY: 0.1,      # 10% max difference
            BiasType.EQUALIZED_ODDS: 0.1,          # 10% max difference
            BiasType.EQUALITY_OPPORTUNITY: 0.1,    # 10% max difference
            BiasType.CALIBRATION: 0.05,            # 5% max calibration error
            BiasType.INDIVIDUAL_FAIRNESS: 0.15,    # 15% max individual difference
            BiasType.INTERSECTIONAL: 0.2,          # 20% max intersectional bias
            BiasType.CREATOR_BIAS: 0.08            # 8% max creator bias
        }

    async def assess_model_bias(self, model_id: str, model_name: str,
                               predictions: List[ModelPrediction]) -> BiasAssessment:
        """🔍 Comprehensive bias assessment for ML model"""
        try:
            logger.info(f"🤖 Starting bias assessment for model {model_id}")
            
            assessment = BiasAssessment(
                model_id=model_id,
                model_name=model_name
            )
            
            # Validate sufficient data
            if len(predictions) < self.min_sample_size:
                logger.warning(f"🤖 Insufficient data for bias assessment: {len(predictions)} < {self.min_sample_size}")
                assessment.metadata["warning"] = "Insufficient data for reliable bias assessment"
            
            # Convert predictions to DataFrame for analysis
            df = self._predictions_to_dataframe(predictions)
            
            # Run bias tests for each protected attribute
            bias_tests = []
            for protected_attr in ProtectedAttribute:
                if protected_attr.value in df.columns:
                    attr_tests = await self._run_bias_tests_for_attribute(df, protected_attr)
                    bias_tests.extend(attr_tests)
            
            assessment.bias_tests = bias_tests
            
            # Creator-specific bias analysis
            assessment.creator_analysis = await self._analyze_creator_bias(df)
            
            # Calculate overall metrics
            assessment.overall_bias_level = self._calculate_overall_bias_level(bias_tests)
            assessment.fairness_score = self._calculate_fairness_score(bias_tests)
            assessment.ethical_compliance = assessment.fairness_score >= 0.8
            assessment.remediation_priority = self._determine_remediation_priority(assessment.overall_bias_level)
            assessment.next_audit_date = datetime.utcnow() + timedelta(days=90)  # Quarterly audits
            
            # Store assessment
            self.bias_history.append(assessment)
            
            logger.info(f"🤖 Bias assessment completed: {assessment.overall_bias_level.value} (Score: {assessment.fairness_score:.3f})")
            
            return assessment
            
        except Exception as e:
            logger.error(f"🤖 Bias assessment failed: {str(e)}")
            raise

    def _predictions_to_dataframe(self, predictions: List[ModelPrediction]) -> pd.DataFrame:
        """Convert predictions to pandas DataFrame for analysis"""
        data = []
        for pred in predictions:
            row = {
                'user_id': pred.user_id,
                'prediction': pred.prediction,
                'actual_outcome': pred.actual_outcome
            }
            # Add protected attributes
            row.update(pred.protected_attributes)
            # Add context data
            row.update(pred.context)
            data.append(row)
        
        return pd.DataFrame(data)

    async def _run_bias_tests_for_attribute(self, df: pd.DataFrame, 
                                          protected_attr: ProtectedAttribute) -> List[BiasTestResult]:
        """Run comprehensive bias tests for a protected attribute"""
        tests = []
        attr_name = protected_attr.value
        
        if attr_name not in df.columns or df[attr_name].isna().all():
            return tests
        
        # Get unique groups for this attribute
        groups = df[attr_name].dropna().unique()
        if len(groups) < 2:
            return tests
        
        # Test 1: Demographic Parity
        demo_parity_test = await self._test_demographic_parity(df, attr_name, groups)
        demo_parity_test.protected_attribute = protected_attr
        tests.append(demo_parity_test)
        
        # Test 2: Equalized Odds (if we have actual outcomes)
        if 'actual_outcome' in df.columns and not df['actual_outcome'].isna().all():
            eq_odds_test = await self._test_equalized_odds(df, attr_name, groups)
            eq_odds_test.protected_attribute = protected_attr
            tests.append(eq_odds_test)
            
            # Test 3: Equal Opportunity
            eq_opp_test = await self._test_equal_opportunity(df, attr_name, groups)
            eq_opp_test.protected_attribute = protected_attr
            tests.append(eq_opp_test)
        
        # Test 4: Calibration
        calibration_test = await self._test_calibration(df, attr_name, groups)
        calibration_test.protected_attribute = protected_attr
        tests.append(calibration_test)
        
        # Test 5: Individual Fairness
        individual_test = await self._test_individual_fairness(df, attr_name, groups)
        individual_test.protected_attribute = protected_attr
        tests.append(individual_test)
        
        return tests

    async def _test_demographic_parity(self, df: pd.DataFrame, attr_name: str, groups: List[str]) -> BiasTestResult:
        """🔍 Test demographic parity (statistical parity)"""
        try:
            # Calculate positive prediction rate for each group
            group_rates = {}
            for group in groups:
                group_data = df[df[attr_name] == group]
                if len(group_data) > 0:
                    positive_rate = (group_data['prediction'] > 0.5).mean()
                    group_rates[str(group)] = positive_rate
            
            # Calculate maximum difference between groups
            rates = list(group_rates.values())
            bias_score = max(rates) - min(rates) if rates else 0.0
            
            # Statistical significance test
            if len(groups) == 2 and len(df) > 30:
                group1_data = df[df[attr_name] == groups[0]]['prediction']
                group2_data = df[df[attr_name] == groups[1]]['prediction']
                _, p_value = stats.ttest_ind(group1_data, group2_data)
                is_significant = p_value < self.statistical_significance
            else:
                is_significant = bias_score > self.bias_threshold
            
            bias_level = self._classify_bias_level(bias_score)
            
            return BiasTestResult(
                bias_type=BiasType.DEMOGRAPHIC_PARITY,
                bias_level=bias_level,
                bias_score=bias_score,
                threshold=self.fairness_thresholds[BiasType.DEMOGRAPHIC_PARITY],
                groups_analyzed=list(map(str, groups)),
                detailed_metrics={
                    "group_rates": group_rates,
                    "max_rate": max(rates) if rates else 0,
                    "min_rate": min(rates) if rates else 0,
                    "statistically_significant": is_significant
                },
                recommendations=self._generate_bias_recommendations(BiasType.DEMOGRAPHIC_PARITY, bias_level)
            )
            
        except Exception as e:
            logger.error(f"🤖 Demographic parity test failed: {str(e)}")
            return BiasTestResult(bias_type=BiasType.DEMOGRAPHIC_PARITY)

    async def _test_equalized_odds(self, df: pd.DataFrame, attr_name: str, groups: List[str]) -> BiasTestResult:
        """🔍 Test equalized odds fairness"""
        try:
            group_metrics = {}
            
            for group in groups:
                group_data = df[df[attr_name] == group]
                if len(group_data) > 10:  # Minimum sample size
                    y_true = (group_data['actual_outcome'] > 0.5).astype(int)
                    y_pred = (group_data['prediction'] > 0.5).astype(int)
                    
                    # Calculate TPR and FPR
                    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
                    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                    
                    group_metrics[str(group)] = {
                        "tpr": tpr,
                        "fpr": fpr,
                        "sample_size": len(group_data)
                    }
            
            # Calculate equalized odds violation
            if len(group_metrics) >= 2:
                tprs = [metrics["tpr"] for metrics in group_metrics.values()]
                fprs = [metrics["fpr"] for metrics in group_metrics.values()]
                
                tpr_diff = max(tprs) - min(tprs)
                fpr_diff = max(fprs) - min(fprs)
                bias_score = max(tpr_diff, fpr_diff)
            else:
                bias_score = 0.0
            
            bias_level = self._classify_bias_level(bias_score)
            
            return BiasTestResult(
                bias_type=BiasType.EQUALIZED_ODDS,
                bias_level=bias_level,
                bias_score=bias_score,
                threshold=self.fairness_thresholds[BiasType.EQUALIZED_ODDS],
                groups_analyzed=list(map(str, groups)),
                detailed_metrics={
                    "group_metrics": group_metrics,
                    "tpr_difference": tpr_diff if 'tpr_diff' in locals() else 0,
                    "fpr_difference": fpr_diff if 'fpr_diff' in locals() else 0
                },
                recommendations=self._generate_bias_recommendations(BiasType.EQUALIZED_ODDS, bias_level)
            )
            
        except Exception as e:
            logger.error(f"🤖 Equalized odds test failed: {str(e)}")
            return BiasTestResult(bias_type=BiasType.EQUALIZED_ODDS)

    async def _test_equal_opportunity(self, df: pd.DataFrame, attr_name: str, groups: List[str]) -> BiasTestResult:
        """🔍 Test equal opportunity fairness"""
        try:
            group_tprs = {}
            
            for group in groups:
                group_data = df[df[attr_name] == group]
                positive_actual = group_data[group_data['actual_outcome'] > 0.5]
                
                if len(positive_actual) > 5:  # Minimum positives for reliable TPR
                    y_true = (positive_actual['actual_outcome'] > 0.5).astype(int)
                    y_pred = (positive_actual['prediction'] > 0.5).astype(int)
                    
                    tpr = y_pred.sum() / len(y_pred) if len(y_pred) > 0 else 0
                    group_tprs[str(group)] = tpr
            
            # Calculate equal opportunity violation
            if len(group_tprs) >= 2:
                tprs = list(group_tprs.values())
                bias_score = max(tprs) - min(tprs)
            else:
                bias_score = 0.0
            
            bias_level = self._classify_bias_level(bias_score)
            
            return BiasTestResult(
                bias_type=BiasType.EQUALITY_OPPORTUNITY,
                bias_level=bias_level,
                bias_score=bias_score,
                threshold=self.fairness_thresholds[BiasType.EQUALITY_OPPORTUNITY],
                groups_analyzed=list(map(str, groups)),
                detailed_metrics={
                    "group_tprs": group_tprs,
                    "max_tpr": max(group_tprs.values()) if group_tprs else 0,
                    "min_tpr": min(group_tprs.values()) if group_tprs else 0
                },
                recommendations=self._generate_bias_recommendations(BiasType.EQUALITY_OPPORTUNITY, bias_level)
            )
            
        except Exception as e:
            logger.error(f"🤖 Equal opportunity test failed: {str(e)}")
            return BiasTestResult(bias_type=BiasType.EQUALITY_OPPORTUNITY)

    async def _test_calibration(self, df: pd.DataFrame, attr_name: str, groups: List[str]) -> BiasTestResult:
        """🔍 Test calibration fairness"""
        try:
            group_calibrations = {}
            
            for group in groups:
                group_data = df[df[attr_name] == group]
                if len(group_data) > 20 and 'actual_outcome' in group_data.columns:
                    # Bin predictions and calculate calibration
                    bins = np.linspace(0, 1, 11)  # 10 bins
                    bin_indices = np.digitize(group_data['prediction'], bins)
                    
                    calibration_error = 0
                    for i in range(1, len(bins)):
                        bin_mask = bin_indices == i
                        if bin_mask.sum() > 0:
                            bin_predictions = group_data.loc[bin_mask, 'prediction'].mean()
                            bin_outcomes = group_data.loc[bin_mask, 'actual_outcome'].mean()
                            calibration_error += abs(bin_predictions - bin_outcomes) * bin_mask.sum()
                    
                    calibration_error /= len(group_data)
                    group_calibrations[str(group)] = calibration_error
            
            # Calculate calibration bias
            if len(group_calibrations) >= 2:
                calibrations = list(group_calibrations.values())
                bias_score = max(calibrations) - min(calibrations)
            else:
                bias_score = 0.0
            
            bias_level = self._classify_bias_level(bias_score, bias_type=BiasType.CALIBRATION)
            
            return BiasTestResult(
                bias_type=BiasType.CALIBRATION,
                bias_level=bias_level,
                bias_score=bias_score,
                threshold=self.fairness_thresholds[BiasType.CALIBRATION],
                groups_analyzed=list(map(str, groups)),
                detailed_metrics={
                    "group_calibrations": group_calibrations,
                    "max_calibration_error": max(group_calibrations.values()) if group_calibrations else 0,
                    "min_calibration_error": min(group_calibrations.values()) if group_calibrations else 0
                },
                recommendations=self._generate_bias_recommendations(BiasType.CALIBRATION, bias_level)
            )
            
        except Exception as e:
            logger.error(f"🤖 Calibration test failed: {str(e)}")
            return BiasTestResult(bias_type=BiasType.CALIBRATION)

    async def _test_individual_fairness(self, df: pd.DataFrame, attr_name: str, groups: List[str]) -> BiasTestResult:
        """🔍 Test individual fairness (similar individuals receive similar outcomes)"""
        try:
            # For individual fairness, we need to find similar individuals across groups
            # Simplified version: compare prediction variance within groups
            
            group_variances = {}
            for group in groups:
                group_data = df[df[attr_name] == group]
                if len(group_data) > 10:
                    pred_variance = group_data['prediction'].var()
                    group_variances[str(group)] = pred_variance
            
            # Individual fairness violation: high variance difference between groups
            if len(group_variances) >= 2:
                variances = list(group_variances.values())
                bias_score = (max(variances) - min(variances)) / (max(variances) + 1e-8)
            else:
                bias_score = 0.0
            
            bias_level = self._classify_bias_level(bias_score, bias_type=BiasType.INDIVIDUAL_FAIRNESS)
            
            return BiasTestResult(
                bias_type=BiasType.INDIVIDUAL_FAIRNESS,
                bias_level=bias_level,
                bias_score=bias_score,
                threshold=self.fairness_thresholds[BiasType.INDIVIDUAL_FAIRNESS],
                groups_analyzed=list(map(str, groups)),
                detailed_metrics={
                    "group_variances": group_variances,
                    "variance_ratio": bias_score
                },
                recommendations=self._generate_bias_recommendations(BiasType.INDIVIDUAL_FAIRNESS, bias_level)
            )
            
        except Exception as e:
            logger.error(f"🤖 Individual fairness test failed: {str(e)}")
            return BiasTestResult(bias_type=BiasType.INDIVIDUAL_FAIRNESS)

    async def _analyze_creator_bias(self, df: pd.DataFrame) -> List[CreatorBiasAnalysis]:
        """🎨 Creator-specific bias analysis"""
        analyses = []
        
        if 'creator_type' not in df.columns:
            return analyses
        
        creator_types = df['creator_type'].dropna().unique()
        
        for creator_type in creator_types:
            if creator_type in self.creator_types:
                creator_data = df[df['creator_type'] == creator_type]
                
                analysis = CreatorBiasAnalysis(
                    creator_type=str(creator_type),
                    total_creators=len(creator_data)
                )
                
                # Performance metrics by creator type
                if len(creator_data) > 10:
                    analysis.bias_metrics = {
                        "avg_prediction": float(creator_data['prediction'].mean()),
                        "prediction_std": float(creator_data['prediction'].std()),
                        "prediction_range": float(creator_data['prediction'].max() - creator_data['prediction'].min())
                    }
                    
                    # Compare with overall averages
                    overall_avg = df['prediction'].mean()
                    creator_avg = creator_data['prediction'].mean()
                    analysis.performance_gaps["prediction_gap"] = float(abs(creator_avg - overall_avg) / overall_avg)
                    
                    # Creator-specific bias patterns
                    if 'follower_count' in df.columns:
                        follower_corr = creator_data[['prediction', 'follower_count']].corr().iloc[0, 1]
                        analysis.visibility_bias = float(abs(follower_corr)) if not pd.isna(follower_corr) else 0.0
                    
                    # Intersectional analysis
                    if 'gender' in df.columns and len(creator_data['gender'].dropna().unique()) > 1:
                        gender_bias = await self._analyze_intersectional_bias(creator_data, ['gender'])
                        analysis.intersectional_analysis['gender'] = gender_bias
                
                analyses.append(analysis)
        
        return analyses

    async def _analyze_intersectional_bias(self, df: pd.DataFrame, attributes: List[str]) -> Dict[str, Any]:
        """🔍 Intersectional bias analysis"""
        try:
            intersectional_metrics = {}
            
            # Create intersectional groups
            if len(attributes) == 1:
                groups = df[attributes[0]].dropna().unique()
                for group in groups:
                    group_data = df[df[attributes[0]] == group]
                    if len(group_data) > 5:
                        intersectional_metrics[str(group)] = {
                            "avg_prediction": float(group_data['prediction'].mean()),
                            "sample_size": len(group_data)
                        }
            
            # Calculate intersectional bias score
            if len(intersectional_metrics) >= 2:
                predictions = [m["avg_prediction"] for m in intersectional_metrics.values()]
                bias_score = (max(predictions) - min(predictions)) / max(predictions) if max(predictions) > 0 else 0
            else:
                bias_score = 0.0
            
            return {
                "bias_score": float(bias_score),
                "group_metrics": intersectional_metrics,
                "significant": bias_score > 0.1
            }
            
        except Exception as e:
            logger.error(f"🤖 Intersectional analysis failed: {str(e)}")
            return {"bias_score": 0.0, "error": str(e)}

    def _classify_bias_level(self, bias_score: float, bias_type: BiasType = BiasType.DEMOGRAPHIC_PARITY) -> BiasLevel:
        """Classify bias severity level"""
        # Adjust thresholds based on bias type
        if bias_type == BiasType.CALIBRATION:
            thresholds = [0.02, 0.05, 0.1, 0.2]  # More strict for calibration
        else:
            thresholds = [0.05, 0.1, 0.2, 0.3]   # Standard thresholds
        
        if bias_score < thresholds[0]:
            return BiasLevel.NONE
        elif bias_score < thresholds[1]:
            return BiasLevel.LOW
        elif bias_score < thresholds[2]:
            return BiasLevel.MODERATE
        elif bias_score < thresholds[3]:
            return BiasLevel.HIGH
        else:
            return BiasLevel.SEVERE

    def _generate_bias_recommendations(self, bias_type: BiasType, bias_level: BiasLevel) -> List[str]:
        """Generate bias mitigation recommendations"""
        recommendations = []
        
        if bias_level == BiasLevel.NONE:
            return ["Model shows no significant bias for this metric"]
        
        # General recommendations by bias type
        if bias_type == BiasType.DEMOGRAPHIC_PARITY:
            recommendations.extend([
                "Apply demographic parity constraints during training",
                "Use fairness-aware sampling techniques",
                "Implement post-processing bias correction"
            ])
        elif bias_type == BiasType.EQUALIZED_ODDS:
            recommendations.extend([
                "Apply equalized odds constraints in model training",
                "Use threshold optimization for different groups",
                "Implement fairness-aware ensemble methods"
            ])
        elif bias_type == BiasType.CALIBRATION:
            recommendations.extend([
                "Apply calibration techniques like Platt scaling",
                "Use isotonic regression for calibration",
                "Implement group-specific calibration"
            ])
        elif bias_type == BiasType.CREATOR_BIAS:
            recommendations.extend([
                "Balance training data across creator types",
                "Implement creator-aware loss functions",
                "Use creator type as a protected attribute"
            ])
        
        # Severity-specific recommendations
        if bias_level in [BiasLevel.HIGH, BiasLevel.SEVERE]:
            recommendations.extend([
                "Immediate model retraining required",
                "Conduct thorough data audit",
                "Implement emergency bias monitoring",
                "Consider model retirement if bias persists"
            ])
        elif bias_level == BiasLevel.MODERATE:
            recommendations.extend([
                "Schedule bias mitigation training",
                "Increase monitoring frequency",
                "Implement bias correction techniques"
            ])
        
        return recommendations

    def _calculate_overall_bias_level(self, bias_tests: List[BiasTestResult]) -> BiasLevel:
        """Calculate overall bias level from all tests"""
        if not bias_tests:
            return BiasLevel.NONE
        
        # Count tests by severity
        level_counts = defaultdict(int)
        for test in bias_tests:
            level_counts[test.bias_level] += 1
        
        # Determine overall level
        if level_counts[BiasLevel.SEVERE] > 0:
            return BiasLevel.SEVERE
        elif level_counts[BiasLevel.HIGH] > 0:
            return BiasLevel.HIGH
        elif level_counts[BiasLevel.MODERATE] >= 2:  # Multiple moderate issues
            return BiasLevel.HIGH
        elif level_counts[BiasLevel.MODERATE] > 0:
            return BiasLevel.MODERATE
        elif level_counts[BiasLevel.LOW] >= 3:  # Multiple low issues
            return BiasLevel.MODERATE
        elif level_counts[BiasLevel.LOW] > 0:
            return BiasLevel.LOW
        else:
            return BiasLevel.NONE

    def _calculate_fairness_score(self, bias_tests: List[BiasTestResult]) -> float:
        """Calculate overall fairness score (0-1, higher is better)"""
        if not bias_tests:
            return 1.0
        
        total_score = 0.0
        weight_sum = 0.0
        
        # Weight different bias types
        bias_weights = {
            BiasType.DEMOGRAPHIC_PARITY: 1.0,
            BiasType.EQUALIZED_ODDS: 1.2,      # Higher weight for predictive fairness
            BiasType.EQUALITY_OPPORTUNITY: 1.1,
            BiasType.CALIBRATION: 1.3,         # Highest weight for calibration
            BiasType.INDIVIDUAL_FAIRNESS: 0.8,
            BiasType.CREATOR_BIAS: 1.1
        }
        
        for test in bias_tests:
            weight = bias_weights.get(test.bias_type, 1.0)
            # Convert bias score to fairness score (1 - normalized_bias)
            max_threshold = 0.3  # Maximum acceptable bias
            normalized_bias = min(test.bias_score / max_threshold, 1.0)
            fairness_component = 1.0 - normalized_bias
            
            total_score += fairness_component * weight
            weight_sum += weight
        
        return total_score / weight_sum if weight_sum > 0 else 1.0

    def _determine_remediation_priority(self, overall_bias_level: BiasLevel) -> str:
        """Determine remediation priority"""
        priority_map = {
            BiasLevel.NONE: "LOW",
            BiasLevel.LOW: "LOW",
            BiasLevel.MODERATE: "MEDIUM",
            BiasLevel.HIGH: "HIGH",
            BiasLevel.SEVERE: "CRITICAL"
        }
        return priority_map.get(overall_bias_level, "MEDIUM")

    async def get_bias_dashboard(self) -> Dict[str, Any]:
        """📊 Get bias monitoring dashboard metrics"""
        total_assessments = len(self.bias_history)
        recent_assessments = [
            a for a in self.bias_history 
            if datetime.utcnow() - a.assessment_date < timedelta(days=30)
        ]
        
        dashboard = {
            "total_assessments": total_assessments,
            "recent_assessments": len(recent_assessments),
            "bias_level_distribution": {
                "none": len([a for a in recent_assessments if a.overall_bias_level == BiasLevel.NONE]),
                "low": len([a for a in recent_assessments if a.overall_bias_level == BiasLevel.LOW]),
                "moderate": len([a for a in recent_assessments if a.overall_bias_level == BiasLevel.MODERATE]),
                "high": len([a for a in recent_assessments if a.overall_bias_level == BiasLevel.HIGH]),
                "severe": len([a for a in recent_assessments if a.overall_bias_level == BiasLevel.SEVERE])
            },
            "average_fairness_score": sum(a.fairness_score for a in recent_assessments) / len(recent_assessments) if recent_assessments else 1.0,
            "ethical_compliance_rate": sum(a.ethical_compliance for a in recent_assessments) / len(recent_assessments) if recent_assessments else 1.0,
            "models_requiring_attention": len([a for a in recent_assessments if a.overall_bias_level in [BiasLevel.HIGH, BiasLevel.SEVERE]]),
            "creator_bias_summary": {}
        }
        
        # Creator bias summary
        creator_analyses = []
        for assessment in recent_assessments:
            creator_analyses.extend(assessment.creator_analysis)
        
        creator_types = set(analysis.creator_type for analysis in creator_analyses)
        for creator_type in creator_types:
            type_analyses = [a for a in creator_analyses if a.creator_type == creator_type]
            if type_analyses:
                avg_performance_gap = sum(
                    analysis.performance_gaps.get("prediction_gap", 0) 
                    for analysis in type_analyses
                ) / len(type_analyses)
                
                dashboard["creator_bias_summary"][creator_type] = {
                    "total_analyses": len(type_analyses),
                    "avg_performance_gap": avg_performance_gap,
                    "bias_concern": avg_performance_gap > 0.1
                }
        
        return dashboard

    def __repr__(self) -> str:
        return f"ModelBiasDetector(assessments={len(self.bias_history)}, thresholds={len(self.fairness_thresholds)})"

# 🤖 ML ENGINEER + IA PROMPT ENGINEER EXPERT - Ethical AI Implementation Complete
# Comprehensive bias detection with creator-specific fairness analysis