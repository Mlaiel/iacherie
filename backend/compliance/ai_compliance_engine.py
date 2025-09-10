"""
AI Compliance Engine - AI Ethics and Algorithmic Compliance Management

Comprehensive AI compliance system for algorithmic fairness, bias detection,
ethical AI governance, model transparency, and AI regulatory compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Proprietary software
"""

import asyncio
import json
import logging
import math
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

import aioredis
import numpy as np
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Float, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class AIComplianceFramework(Enum):
    """AI compliance frameworks and standards"""
    EU_AI_ACT = "eu_ai_act"
    IEEE_2857 = "ieee_2857"  # Privacy Engineering
    ISO_23053 = "iso_23053"  # Framework for AI risk management
    ISO_23894 = "iso_23894"  # AI risk management
    NIST_AI_RMF = "nist_ai_rmf"  # NIST AI Risk Management Framework
    UNESCO_AI_ETHICS = "unesco_ai_ethics"
    OECD_AI_PRINCIPLES = "oecd_ai_principles"
    GDPR_AUTOMATED_DECISIONS = "gdpr_automated_decisions"
    ALGORITHMIC_ACCOUNTABILITY_ACT = "algorithmic_accountability_act"
    PARTNERSHIP_AI_TENETS = "partnership_ai_tenets"


class AIRiskCategory(Enum):
    """AI risk categories according to EU AI Act"""
    UNACCEPTABLE_RISK = "unacceptable_risk"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"


class BiasType(Enum):
    """Types of AI bias"""
    SELECTION_BIAS = "selection_bias"
    CONFIRMATION_BIAS = "confirmation_bias"
    ALGORITHMIC_BIAS = "algorithmic_bias"
    DEMOGRAPHIC_BIAS = "demographic_bias"
    REPRESENTATION_BIAS = "representation_bias"
    MEASUREMENT_BIAS = "measurement_bias"
    HISTORICAL_BIAS = "historical_bias"
    EVALUATION_BIAS = "evaluation_bias"


class FairnessMetric(Enum):
    """AI fairness metrics"""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"
    COUNTERFACTUAL_FAIRNESS = "counterfactual_fairness"
    TREATMENT_EQUALITY = "treatment_equality"


class ExplainabilityLevel(Enum):
    """AI explainability levels"""
    FULLY_EXPLAINABLE = "fully_explainable"
    PARTIALLY_EXPLAINABLE = "partially_explainable"
    BLACK_BOX_WITH_EXPLANATIONS = "black_box_with_explanations"
    BLACK_BOX_NO_EXPLANATIONS = "black_box_no_explanations"


class AISystemType(Enum):
    """Types of AI systems"""
    RECOMMENDATION_SYSTEM = "recommendation_system"
    CONTENT_MODERATION = "content_moderation"
    BIOMETRIC_IDENTIFICATION = "biometric_identification"
    EMOTION_RECOGNITION = "emotion_recognition"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    AUTOMATED_DECISION_MAKING = "automated_decision_making"
    NATURAL_LANGUAGE_PROCESSING = "natural_language_processing"
    COMPUTER_VISION = "computer_vision"
    GENERATIVE_AI = "generative_ai"


@dataclass
class AISystemProfile:
    """AI system compliance profile"""
    system_id: str
    system_name: str
    system_type: AISystemType
    risk_category: AIRiskCategory
    purpose_description: str
    target_users: List[str]
    deployment_context: str
    data_sources: List[str]
    protected_characteristics: List[str]
    potential_harms: List[str]
    mitigation_measures: List[str]
    compliance_frameworks: List[AIComplianceFramework]
    last_assessment: datetime
    next_review: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BiasAssessment:
    """AI bias assessment result"""
    assessment_id: str
    system_id: str
    bias_types_detected: List[BiasType]
    affected_groups: List[str]
    bias_severity: str
    detection_method: str
    statistical_evidence: Dict[str, float]
    remediation_recommendations: List[str]
    assessment_date: datetime
    assessor: str
    confidence_level: float


@dataclass
class FairnessEvaluation:
    """AI fairness evaluation result"""
    evaluation_id: str
    system_id: str
    fairness_metrics: Dict[FairnessMetric, float]
    protected_attributes: List[str]
    fairness_thresholds: Dict[str, float]
    compliance_status: str
    disparate_impact_ratio: float
    equalized_odds_difference: float
    calibration_scores: Dict[str, float]
    recommendations: List[str]
    evaluation_date: datetime


@dataclass
class ExplainabilityAssessment:
    """AI explainability assessment"""
    assessment_id: str
    system_id: str
    explainability_level: ExplainabilityLevel
    explanation_methods: List[str]
    target_audience: List[str]
    explanation_quality_score: float
    comprehensibility_rating: float
    actionability_rating: float
    explanation_coverage: float
    improvement_recommendations: List[str]
    assessment_date: datetime


@dataclass
class EthicalRiskAssessment:
    """Comprehensive ethical risk assessment"""
    assessment_id: str
    system_id: str
    ethical_principles_evaluated: List[str]
    risk_factors: Dict[str, float]
    stakeholder_impact_analysis: Dict[str, str]
    ethical_compliance_score: float
    risk_mitigation_plan: List[str]
    ethical_review_board_approval: bool
    assessment_date: datetime
    next_review_date: datetime


class AISystemRecord(Base):
    """Database model for AI systems"""
    __tablename__ = "ai_systems"
    
    system_id = Column(String, primary_key=True)
    system_name = Column(String, nullable=False)
    system_type = Column(String, nullable=False)
    risk_category = Column(String, nullable=False)
    purpose_description = Column(Text)
    target_users = Column(JSON, default=[])
    deployment_context = Column(Text)
    data_sources = Column(JSON, default=[])
    protected_characteristics = Column(JSON, default=[])
    potential_harms = Column(JSON, default=[])
    mitigation_measures = Column(JSON, default=[])
    compliance_frameworks = Column(JSON, default=[])
    last_assessment = Column(DateTime)
    next_review = Column(DateTime)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BiasAssessmentRecord(Base):
    """Database model for bias assessments"""
    __tablename__ = "bias_assessments"
    
    assessment_id = Column(String, primary_key=True)
    system_id = Column(String, nullable=False)
    bias_types_detected = Column(JSON, default=[])
    affected_groups = Column(JSON, default=[])
    bias_severity = Column(String)
    detection_method = Column(String)
    statistical_evidence = Column(JSON, default={})
    remediation_recommendations = Column(JSON, default=[])
    assessment_date = Column(DateTime, nullable=False)
    assessor = Column(String)
    confidence_level = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class FairnessEvaluationRecord(Base):
    """Database model for fairness evaluations"""
    __tablename__ = "fairness_evaluations"
    
    evaluation_id = Column(String, primary_key=True)
    system_id = Column(String, nullable=False)
    fairness_metrics = Column(JSON, default={})
    protected_attributes = Column(JSON, default=[])
    fairness_thresholds = Column(JSON, default={})
    compliance_status = Column(String)
    disparate_impact_ratio = Column(Float)
    equalized_odds_difference = Column(Float)
    calibration_scores = Column(JSON, default={})
    recommendations = Column(JSON, default=[])
    evaluation_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExplainabilityAssessmentRecord(Base):
    """Database model for explainability assessments"""
    __tablename__ = "explainability_assessments"
    
    assessment_id = Column(String, primary_key=True)
    system_id = Column(String, nullable=False)
    explainability_level = Column(String)
    explanation_methods = Column(JSON, default=[])
    target_audience = Column(JSON, default=[])
    explanation_quality_score = Column(Float)
    comprehensibility_rating = Column(Float)
    actionability_rating = Column(Float)
    explanation_coverage = Column(Float)
    improvement_recommendations = Column(JSON, default=[])
    assessment_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class EthicalRiskAssessmentRecord(Base):
    """Database model for ethical risk assessments"""
    __tablename__ = "ethical_risk_assessments"
    
    assessment_id = Column(String, primary_key=True)
    system_id = Column(String, nullable=False)
    ethical_principles_evaluated = Column(JSON, default=[])
    risk_factors = Column(JSON, default={})
    stakeholder_impact_analysis = Column(JSON, default={})
    ethical_compliance_score = Column(Float)
    risk_mitigation_plan = Column(JSON, default=[])
    ethical_review_board_approval = Column(Boolean, default=False)
    assessment_date = Column(DateTime, nullable=False)
    next_review_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class BiasDetector:
    """AI bias detection and assessment"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def detect_bias(self, 
                         system_id: str,
                         model_predictions: List[Dict[str, Any]],
                         protected_attributes: List[str]) -> BiasAssessment:
        """Detect bias in AI system predictions"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Analyze predictions for bias patterns
            bias_analysis = await self._analyze_prediction_bias(model_predictions, protected_attributes)
            
            # Detect specific bias types
            detected_bias_types = await self._identify_bias_types(bias_analysis)
            
            # Assess bias severity
            bias_severity = await self._assess_bias_severity(bias_analysis)
            
            # Generate remediation recommendations
            recommendations = await self._generate_bias_remediation(detected_bias_types, bias_analysis)
            
            assessment = BiasAssessment(
                assessment_id=assessment_id,
                system_id=system_id,
                bias_types_detected=detected_bias_types,
                affected_groups=bias_analysis.get("affected_groups", []),
                bias_severity=bias_severity,
                detection_method="statistical_analysis",
                statistical_evidence=bias_analysis.get("statistical_evidence", {}),
                remediation_recommendations=recommendations,
                assessment_date=datetime.utcnow(),
                assessor="ai_compliance_engine",
                confidence_level=bias_analysis.get("confidence", 0.8)
            )
            
            # Cache assessment
            await self.redis.setex(f"bias_assessment:{assessment_id}", 3600 * 24,
                                  json.dumps(assessment.__dict__, default=str))
            
            return assessment
            
        except Exception as e:
            logger.error(f"Bias detection failed: {str(e)}")
            raise
    
    async def _analyze_prediction_bias(self, 
                                     predictions: List[Dict[str, Any]],
                                     protected_attributes: List[str]) -> Dict[str, Any]:
        """Analyze predictions for bias patterns"""
        analysis = {
            "statistical_evidence": {},
            "affected_groups": [],
            "confidence": 0.0
        }
        
        if not predictions or not protected_attributes:
            return analysis
        
        # Group predictions by protected attributes
        groups = defaultdict(list)
        for pred in predictions:
            for attr in protected_attributes:
                if attr in pred:
                    groups[f"{attr}_{pred[attr]}"].append(pred)
        
        # Calculate statistical measures
        group_stats = {}
        for group_name, group_preds in groups.items():
            if len(group_preds) > 0:
                # Calculate positive prediction rate
                positive_rate = sum(1 for p in group_preds if p.get("prediction", 0) > 0.5) / len(group_preds)
                
                # Calculate average prediction score
                avg_score = statistics.mean([p.get("prediction", 0) for p in group_preds])
                
                group_stats[group_name] = {
                    "positive_rate": positive_rate,
                    "average_score": avg_score,
                    "sample_size": len(group_preds)
                }
        
        # Calculate disparate impact
        if len(group_stats) >= 2:
            rates = [stats["positive_rate"] for stats in group_stats.values()]
            min_rate = min(rates)
            max_rate = max(rates)
            
            disparate_impact = min_rate / max_rate if max_rate > 0 else 0
            analysis["statistical_evidence"]["disparate_impact_ratio"] = disparate_impact
            
            # Standard deviation of rates
            rate_std = statistics.stdev(rates) if len(rates) > 1 else 0
            analysis["statistical_evidence"]["rate_variation"] = rate_std
            
            # Identify affected groups
            if disparate_impact < 0.8:  # 80% rule
                affected_groups = [group for group, stats in group_stats.items() 
                                 if stats["positive_rate"] < max_rate * 0.9]
                analysis["affected_groups"] = affected_groups
            
            # Calculate confidence based on sample sizes and effect size
            min_sample = min([stats["sample_size"] for stats in group_stats.values()])
            confidence = min(0.95, 0.5 + min_sample / 200)  # Simple confidence estimation
            analysis["confidence"] = confidence
        
        analysis["group_statistics"] = group_stats
        return analysis
    
    async def _identify_bias_types(self, bias_analysis: Dict[str, Any]) -> List[BiasType]:
        """Identify specific types of bias"""
        detected_types = []
        
        evidence = bias_analysis.get("statistical_evidence", {})
        
        # Demographic bias
        if evidence.get("disparate_impact_ratio", 1.0) < 0.8:
            detected_types.append(BiasType.DEMOGRAPHIC_BIAS)
        
        # Algorithmic bias
        if evidence.get("rate_variation", 0) > 0.1:
            detected_types.append(BiasType.ALGORITHMIC_BIAS)
        
        # Selection bias (inferred from sample size disparities)
        group_stats = bias_analysis.get("group_statistics", {})
        if group_stats:
            sample_sizes = [stats["sample_size"] for stats in group_stats.values()]
            if len(sample_sizes) > 1:
                size_ratio = min(sample_sizes) / max(sample_sizes)
                if size_ratio < 0.5:
                    detected_types.append(BiasType.SELECTION_BIAS)
        
        return detected_types
    
    async def _assess_bias_severity(self, bias_analysis: Dict[str, Any]) -> str:
        """Assess the severity of detected bias"""
        evidence = bias_analysis.get("statistical_evidence", {})
        
        disparate_impact = evidence.get("disparate_impact_ratio", 1.0)
        rate_variation = evidence.get("rate_variation", 0)
        
        # Severity assessment based on statistical measures
        if disparate_impact < 0.5 or rate_variation > 0.3:
            return "critical"
        elif disparate_impact < 0.7 or rate_variation > 0.2:
            return "high"
        elif disparate_impact < 0.8 or rate_variation > 0.1:
            return "medium"
        else:
            return "low"
    
    async def _generate_bias_remediation(self, 
                                       bias_types: List[BiasType],
                                       bias_analysis: Dict[str, Any]) -> List[str]:
        """Generate bias remediation recommendations"""
        recommendations = []
        
        # General recommendations
        if bias_types:
            recommendations.append("Conduct comprehensive bias audit of training data")
            recommendations.append("Implement bias testing in model development pipeline")
            recommendations.append("Establish bias monitoring in production")
        
        # Specific recommendations per bias type
        if BiasType.DEMOGRAPHIC_BIAS in bias_types:
            recommendations.extend([
                "Re-balance training data across demographic groups",
                "Implement fairness constraints in model training",
                "Apply post-processing bias mitigation techniques"
            ])
        
        if BiasType.SELECTION_BIAS in bias_types:
            recommendations.extend([
                "Review data collection methodology",
                "Implement stratified sampling strategies",
                "Address underrepresented group coverage"
            ])
        
        if BiasType.ALGORITHMIC_BIAS in bias_types:
            recommendations.extend([
                "Review feature selection and engineering processes",
                "Implement algorithmic fairness constraints",
                "Consider alternative modeling approaches"
            ])
        
        return recommendations


class FairnessEvaluator:
    """AI fairness evaluation and metrics calculation"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def evaluate_fairness(self, 
                              system_id: str,
                              predictions: List[Dict[str, Any]],
                              ground_truth: List[Dict[str, Any]],
                              protected_attributes: List[str]) -> FairnessEvaluation:
        """Evaluate AI system fairness using multiple metrics"""
        try:
            evaluation_id = str(uuid.uuid4())
            
            # Calculate fairness metrics
            fairness_metrics = await self._calculate_fairness_metrics(
                predictions, ground_truth, protected_attributes
            )
            
            # Assess compliance status
            compliance_status = await self._assess_fairness_compliance(fairness_metrics)
            
            # Generate recommendations
            recommendations = await self._generate_fairness_recommendations(fairness_metrics, compliance_status)
            
            evaluation = FairnessEvaluation(
                evaluation_id=evaluation_id,
                system_id=system_id,
                fairness_metrics=fairness_metrics,
                protected_attributes=protected_attributes,
                fairness_thresholds={"disparate_impact": 0.8, "equalized_odds": 0.1},
                compliance_status=compliance_status,
                disparate_impact_ratio=fairness_metrics.get(FairnessMetric.DEMOGRAPHIC_PARITY, 0.0),
                equalized_odds_difference=fairness_metrics.get(FairnessMetric.EQUALIZED_ODDS, 0.0),
                calibration_scores={"overall": fairness_metrics.get(FairnessMetric.CALIBRATION, 0.0)},
                recommendations=recommendations,
                evaluation_date=datetime.utcnow()
            )
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Fairness evaluation failed: {str(e)}")
            raise
    
    async def _calculate_fairness_metrics(self, 
                                        predictions: List[Dict[str, Any]],
                                        ground_truth: List[Dict[str, Any]],
                                        protected_attributes: List[str]) -> Dict[FairnessMetric, float]:
        """Calculate various fairness metrics"""
        metrics = {}
        
        if not predictions or not ground_truth or not protected_attributes:
            return metrics
        
        # Align predictions and ground truth
        aligned_data = []
        for i, (pred, truth) in enumerate(zip(predictions, ground_truth)):
            aligned_data.append({
                "prediction": pred.get("prediction", 0),
                "ground_truth": truth.get("label", 0),
                "protected_attr": {attr: pred.get(attr) for attr in protected_attributes}
            })
        
        # Group by protected attributes
        groups = defaultdict(list)
        for data in aligned_data:
            for attr in protected_attributes:
                attr_value = data["protected_attr"].get(attr)
                if attr_value is not None:
                    groups[f"{attr}_{attr_value}"].append(data)
        
        if len(groups) < 2:
            return metrics
        
        # Calculate Demographic Parity
        group_positive_rates = {}
        for group_name, group_data in groups.items():
            positive_rate = sum(1 for d in group_data if d["prediction"] > 0.5) / len(group_data)
            group_positive_rates[group_name] = positive_rate
        
        if group_positive_rates:
            rates = list(group_positive_rates.values())
            metrics[FairnessMetric.DEMOGRAPHIC_PARITY] = min(rates) / max(rates) if max(rates) > 0 else 0
        
        # Calculate Equalized Odds
        group_tpr = {}  # True Positive Rate
        group_fpr = {}  # False Positive Rate
        
        for group_name, group_data in groups.items():
            tp = sum(1 for d in group_data if d["prediction"] > 0.5 and d["ground_truth"] == 1)
            fn = sum(1 for d in group_data if d["prediction"] <= 0.5 and d["ground_truth"] == 1)
            fp = sum(1 for d in group_data if d["prediction"] > 0.5 and d["ground_truth"] == 0)
            tn = sum(1 for d in group_data if d["prediction"] <= 0.5 and d["ground_truth"] == 0)
            
            tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            
            group_tpr[group_name] = tpr
            group_fpr[group_name] = fpr
        
        if len(group_tpr) >= 2:
            tpr_values = list(group_tpr.values())
            fpr_values = list(group_fpr.values())
            
            tpr_diff = max(tpr_values) - min(tpr_values)
            fpr_diff = max(fpr_values) - min(fpr_values)
            
            metrics[FairnessMetric.EQUALIZED_ODDS] = max(tpr_diff, fpr_diff)
        
        # Calculate Equal Opportunity (TPR difference)
        if len(group_tpr) >= 2:
            tpr_values = list(group_tpr.values())
            metrics[FairnessMetric.EQUAL_OPPORTUNITY] = max(tpr_values) - min(tpr_values)
        
        # Calculate Calibration
        group_calibration = {}
        for group_name, group_data in groups.items():
            if len(group_data) > 0:
                predicted_probs = [d["prediction"] for d in group_data]
                actual_outcomes = [d["ground_truth"] for d in group_data]
                
                # Simple calibration measure
                avg_prediction = statistics.mean(predicted_probs)
                avg_outcome = statistics.mean(actual_outcomes)
                calibration_error = abs(avg_prediction - avg_outcome)
                
                group_calibration[group_name] = calibration_error
        
        if group_calibration:
            metrics[FairnessMetric.CALIBRATION] = statistics.mean(group_calibration.values())
        
        return metrics
    
    async def _assess_fairness_compliance(self, fairness_metrics: Dict[FairnessMetric, float]) -> str:
        """Assess overall fairness compliance status"""
        compliance_issues = []
        
        # Check demographic parity
        demo_parity = fairness_metrics.get(FairnessMetric.DEMOGRAPHIC_PARITY, 1.0)
        if demo_parity < 0.8:
            compliance_issues.append("demographic_parity_violation")
        
        # Check equalized odds
        eq_odds = fairness_metrics.get(FairnessMetric.EQUALIZED_ODDS, 0.0)
        if eq_odds > 0.1:
            compliance_issues.append("equalized_odds_violation")
        
        # Check calibration
        calibration = fairness_metrics.get(FairnessMetric.CALIBRATION, 0.0)
        if calibration > 0.1:
            compliance_issues.append("calibration_violation")
        
        # Determine overall status
        if not compliance_issues:
            return "compliant"
        elif len(compliance_issues) == 1:
            return "partially_compliant"
        else:
            return "non_compliant"
    
    async def _generate_fairness_recommendations(self, 
                                               fairness_metrics: Dict[FairnessMetric, float],
                                               compliance_status: str) -> List[str]:
        """Generate fairness improvement recommendations"""
        recommendations = []
        
        # Demographic parity recommendations
        demo_parity = fairness_metrics.get(FairnessMetric.DEMOGRAPHIC_PARITY, 1.0)
        if demo_parity < 0.8:
            recommendations.extend([
                "Implement demographic parity constraints during training",
                "Re-balance training data across protected groups",
                "Apply post-processing fairness techniques"
            ])
        
        # Equalized odds recommendations
        eq_odds = fairness_metrics.get(FairnessMetric.EQUALIZED_ODDS, 0.0)
        if eq_odds > 0.1:
            recommendations.extend([
                "Optimize for equalized odds fairness metric",
                "Implement threshold optimization per group",
                "Review feature importance across protected groups"
            ])
        
        # Calibration recommendations
        calibration = fairness_metrics.get(FairnessMetric.CALIBRATION, 0.0)
        if calibration > 0.1:
            recommendations.extend([
                "Implement calibration techniques for each group",
                "Apply Platt scaling or isotonic regression",
                "Review probability threshold settings"
            ])
        
        # General recommendations
        if compliance_status != "compliant":
            recommendations.extend([
                "Establish continuous fairness monitoring",
                "Implement fairness-aware machine learning techniques",
                "Conduct regular fairness audits",
                "Engage with affected communities for feedback"
            ])
        
        return recommendations


class ExplainabilityAnalyzer:
    """AI explainability and interpretability analysis"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def assess_explainability(self, 
                                  system_id: str,
                                  model_info: Dict[str, Any],
                                  target_audience: List[str]) -> ExplainabilityAssessment:
        """Assess AI system explainability"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Determine explainability level
            explainability_level = await self._determine_explainability_level(model_info)
            
            # Identify available explanation methods
            explanation_methods = await self._identify_explanation_methods(model_info, explainability_level)
            
            # Assess explanation quality
            quality_assessment = await self._assess_explanation_quality(
                explanation_methods, target_audience, model_info
            )
            
            # Generate improvement recommendations
            recommendations = await self._generate_explainability_recommendations(
                explainability_level, quality_assessment, target_audience
            )
            
            assessment = ExplainabilityAssessment(
                assessment_id=assessment_id,
                system_id=system_id,
                explainability_level=explainability_level,
                explanation_methods=explanation_methods,
                target_audience=target_audience,
                explanation_quality_score=quality_assessment["quality_score"],
                comprehensibility_rating=quality_assessment["comprehensibility"],
                actionability_rating=quality_assessment["actionability"],
                explanation_coverage=quality_assessment["coverage"],
                improvement_recommendations=recommendations,
                assessment_date=datetime.utcnow()
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Explainability assessment failed: {str(e)}")
            raise
    
    async def _determine_explainability_level(self, model_info: Dict[str, Any]) -> ExplainabilityLevel:
        """Determine the explainability level of the AI system"""
        model_type = model_info.get("type", "unknown")
        complexity = model_info.get("complexity", "unknown")
        
        # Rule-based or simple models
        if model_type in ["linear_regression", "logistic_regression", "decision_tree", "rule_based"]:
            return ExplainabilityLevel.FULLY_EXPLAINABLE
        
        # Moderately complex models
        elif model_type in ["random_forest", "gradient_boosting", "naive_bayes"]:
            return ExplainabilityLevel.PARTIALLY_EXPLAINABLE
        
        # Complex models with explanation capabilities
        elif model_type in ["neural_network", "deep_learning"] and model_info.get("has_explanations", False):
            return ExplainabilityLevel.BLACK_BOX_WITH_EXPLANATIONS
        
        # Complex models without explanations
        else:
            return ExplainabilityLevel.BLACK_BOX_NO_EXPLANATIONS
    
    async def _identify_explanation_methods(self, 
                                          model_info: Dict[str, Any],
                                          explainability_level: ExplainabilityLevel) -> List[str]:
        """Identify available explanation methods"""
        methods = []
        
        model_type = model_info.get("type", "unknown")
        
        # Intrinsic methods for interpretable models
        if explainability_level == ExplainabilityLevel.FULLY_EXPLAINABLE:
            if model_type in ["linear_regression", "logistic_regression"]:
                methods.extend(["coefficient_analysis", "feature_importance"])
            elif model_type == "decision_tree":
                methods.extend(["tree_visualization", "rule_extraction"])
            elif model_type == "rule_based":
                methods.extend(["rule_inspection", "decision_path_tracing"])
        
        # Post-hoc methods for complex models
        elif explainability_level in [ExplainabilityLevel.PARTIALLY_EXPLAINABLE, 
                                    ExplainabilityLevel.BLACK_BOX_WITH_EXPLANATIONS]:
            methods.extend([
                "feature_importance_global",
                "permutation_importance",
                "partial_dependence_plots"
            ])
            
            # Model-specific methods
            if model_type in ["random_forest", "gradient_boosting"]:
                methods.append("tree_based_feature_importance")
            
            # Add advanced explanation methods
            methods.extend([
                "lime_explanations",
                "shap_values",
                "counterfactual_explanations",
                "anchor_explanations"
            ])
        
        # Limited methods for black box models
        elif explainability_level == ExplainabilityLevel.BLACK_BOX_NO_EXPLANATIONS:
            methods.extend([
                "input_output_analysis",
                "sensitivity_analysis",
                "surrogate_model_explanations"
            ])
        
        return methods
    
    async def _assess_explanation_quality(self, 
                                        explanation_methods: List[str],
                                        target_audience: List[str],
                                        model_info: Dict[str, Any]) -> Dict[str, float]:
        """Assess the quality of available explanations"""
        quality_assessment = {
            "quality_score": 0.0,
            "comprehensibility": 0.0,
            "actionability": 0.0,
            "coverage": 0.0
        }
        
        if not explanation_methods:
            return quality_assessment
        
        # Base quality score on number and sophistication of methods
        method_scores = {
            "coefficient_analysis": 0.9,
            "feature_importance": 0.8,
            "tree_visualization": 0.9,
            "rule_extraction": 0.9,
            "shap_values": 0.8,
            "lime_explanations": 0.7,
            "counterfactual_explanations": 0.8,
            "partial_dependence_plots": 0.7,
            "sensitivity_analysis": 0.6,
            "surrogate_model_explanations": 0.6
        }
        
        method_quality = [method_scores.get(method, 0.5) for method in explanation_methods]
        quality_assessment["quality_score"] = statistics.mean(method_quality) if method_quality else 0.0
        
        # Assess comprehensibility based on target audience
        if "end_users" in target_audience:
            # Need simpler explanations for end users
            simple_methods = ["rule_extraction", "feature_importance", "counterfactual_explanations"]
            simple_score = sum(1 for method in explanation_methods if method in simple_methods)
            quality_assessment["comprehensibility"] = min(1.0, simple_score / 3)
        else:
            # Technical audience can handle more complex explanations
            quality_assessment["comprehensibility"] = min(1.0, len(explanation_methods) / 5)
        
        # Assess actionability
        actionable_methods = ["counterfactual_explanations", "feature_importance", "rule_extraction"]
        actionable_score = sum(1 for method in explanation_methods if method in actionable_methods)
        quality_assessment["actionability"] = min(1.0, actionable_score / 3)
        
        # Assess coverage
        coverage_types = ["global", "local", "counterfactual", "feature_based"]
        coverage_count = 0
        
        if any("global" in method or "importance" in method for method in explanation_methods):
            coverage_count += 1
        if any("local" in method or "lime" in method or "shap" in method for method in explanation_methods):
            coverage_count += 1
        if any("counterfactual" in method for method in explanation_methods):
            coverage_count += 1
        if any("feature" in method for method in explanation_methods):
            coverage_count += 1
        
        quality_assessment["coverage"] = coverage_count / len(coverage_types)
        
        return quality_assessment
    
    async def _generate_explainability_recommendations(self, 
                                                     explainability_level: ExplainabilityLevel,
                                                     quality_assessment: Dict[str, float],
                                                     target_audience: List[str]) -> List[str]:
        """Generate explainability improvement recommendations"""
        recommendations = []
        
        # Level-based recommendations
        if explainability_level == ExplainabilityLevel.BLACK_BOX_NO_EXPLANATIONS:
            recommendations.extend([
                "Implement post-hoc explanation methods (SHAP, LIME)",
                "Consider switching to more interpretable models if possible",
                "Develop surrogate interpretable models",
                "Create user-friendly explanation interfaces"
            ])
        
        elif explainability_level == ExplainabilityLevel.BLACK_BOX_WITH_EXPLANATIONS:
            recommendations.extend([
                "Improve explanation quality and coverage",
                "Implement multiple explanation methods for robustness",
                "Validate explanations with domain experts"
            ])
        
        # Quality-based recommendations
        if quality_assessment["comprehensibility"] < 0.7:
            recommendations.append("Simplify explanations for target audience")
            if "end_users" in target_audience:
                recommendations.append("Develop natural language explanations")
        
        if quality_assessment["actionability"] < 0.7:
            recommendations.extend([
                "Implement counterfactual explanations",
                "Provide actionable insights and recommendations",
                "Show feature importance rankings"
            ])
        
        if quality_assessment["coverage"] < 0.7:
            recommendations.extend([
                "Implement both global and local explanations",
                "Add feature-based explanation methods",
                "Develop explanation dashboards"
            ])
        
        # Audience-specific recommendations
        if "regulators" in target_audience:
            recommendations.extend([
                "Provide audit trail for all decisions",
                "Document explanation methodology",
                "Ensure regulatory compliance for explanations"
            ])
        
        if "data_subjects" in target_audience:
            recommendations.extend([
                "Implement right to explanation features",
                "Create user-friendly explanation interfaces",
                "Provide recourse mechanisms based on explanations"
            ])
        
        return recommendations


class EthicalRiskAnalyzer:
    """Comprehensive ethical risk analysis for AI systems"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
    async def conduct_ethical_risk_assessment(self, 
                                            system_id: str,
                                            system_profile: AISystemProfile) -> EthicalRiskAssessment:
        """Conduct comprehensive ethical risk assessment"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Define ethical principles to evaluate
            ethical_principles = [
                "human_autonomy",
                "prevention_of_harm",
                "fairness",
                "explicability",
                "transparency",
                "accountability",
                "privacy",
                "human_dignity",
                "non_discrimination",
                "children_protection"
            ]
            
            # Assess risks for each principle
            risk_factors = await self._assess_ethical_risks(system_profile, ethical_principles)
            
            # Analyze stakeholder impact
            stakeholder_impact = await self._analyze_stakeholder_impact(system_profile, risk_factors)
            
            # Calculate overall ethical compliance score
            compliance_score = await self._calculate_ethical_compliance_score(risk_factors)
            
            # Generate risk mitigation plan
            mitigation_plan = await self._generate_risk_mitigation_plan(risk_factors, stakeholder_impact)
            
            # Determine if ethical review board approval is needed
            needs_approval = await self._assess_ethical_review_requirement(system_profile, risk_factors)
            
            assessment = EthicalRiskAssessment(
                assessment_id=assessment_id,
                system_id=system_id,
                ethical_principles_evaluated=ethical_principles,
                risk_factors=risk_factors,
                stakeholder_impact_analysis=stakeholder_impact,
                ethical_compliance_score=compliance_score,
                risk_mitigation_plan=mitigation_plan,
                ethical_review_board_approval=needs_approval,
                assessment_date=datetime.utcnow(),
                next_review_date=datetime.utcnow() + timedelta(days=180)
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Ethical risk assessment failed: {str(e)}")
            raise
    
    async def _assess_ethical_risks(self, 
                                  system_profile: AISystemProfile,
                                  ethical_principles: List[str]) -> Dict[str, float]:
        """Assess risks for each ethical principle"""
        risk_factors = {}
        
        for principle in ethical_principles:
            risk_score = await self._calculate_principle_risk(principle, system_profile)
            risk_factors[principle] = risk_score
        
        return risk_factors
    
    async def _calculate_principle_risk(self, 
                                      principle: str,
                                      system_profile: AISystemProfile) -> float:
        """Calculate risk score for a specific ethical principle"""
        risk_score = 0.0
        
        if principle == "human_autonomy":
            # Higher risk for automated decision-making systems
            if system_profile.system_type == AISystemType.AUTOMATED_DECISION_MAKING:
                risk_score += 0.4
            if "high_stakes_decisions" in system_profile.potential_harms:
                risk_score += 0.3
            if system_profile.risk_category == AIRiskCategory.HIGH_RISK:
                risk_score += 0.3
        
        elif principle == "prevention_of_harm":
            # Risk based on potential harms and risk category
            harm_count = len(system_profile.potential_harms)
            risk_score += min(0.5, harm_count * 0.1)
            
            if system_profile.risk_category == AIRiskCategory.UNACCEPTABLE_RISK:
                risk_score += 0.5
            elif system_profile.risk_category == AIRiskCategory.HIGH_RISK:
                risk_score += 0.3
        
        elif principle == "fairness":
            # Higher risk for systems affecting protected characteristics
            if system_profile.protected_characteristics:
                risk_score += min(0.4, len(system_profile.protected_characteristics) * 0.1)
            if "discrimination" in system_profile.potential_harms:
                risk_score += 0.3
            if system_profile.system_type in [AISystemType.BIOMETRIC_IDENTIFICATION, 
                                            AISystemType.EMOTION_RECOGNITION]:
                risk_score += 0.3
        
        elif principle == "explicability":
            # Risk based on system complexity and stakes
            if system_profile.system_type in [AISystemType.AUTOMATED_DECISION_MAKING,
                                            AISystemType.BIOMETRIC_IDENTIFICATION]:
                risk_score += 0.4
            if "lack_of_transparency" in system_profile.potential_harms:
                risk_score += 0.3
            if system_profile.risk_category == AIRiskCategory.HIGH_RISK:
                risk_score += 0.3
        
        elif principle == "privacy":
            # Risk based on data types and processing
            sensitive_data_types = ["biometric", "health", "financial", "personal"]
            data_risk = sum(0.1 for data_type in system_profile.data_sources 
                          if any(sensitive in data_type.lower() for sensitive in sensitive_data_types))
            risk_score += min(0.5, data_risk)
            
            if system_profile.system_type in [AISystemType.BIOMETRIC_IDENTIFICATION,
                                            AISystemType.EMOTION_RECOGNITION]:
                risk_score += 0.3
        
        elif principle == "children_protection":
            # Higher risk for systems targeting or affecting children
            if "children" in system_profile.target_users:
                risk_score += 0.5
            if "minors" in system_profile.target_users:
                risk_score += 0.4
            if "educational" in system_profile.deployment_context.lower():
                risk_score += 0.2
        
        # Cap risk score at 1.0
        return min(1.0, risk_score)
    
    async def _analyze_stakeholder_impact(self, 
                                        system_profile: AISystemProfile,
                                        risk_factors: Dict[str, float]) -> Dict[str, str]:
        """Analyze impact on different stakeholder groups"""
        stakeholder_impact = {}
        
        # End users impact
        user_risk = statistics.mean([
            risk_factors.get("human_autonomy", 0),
            risk_factors.get("prevention_of_harm", 0),
            risk_factors.get("fairness", 0)
        ])
        
        if user_risk > 0.7:
            stakeholder_impact["end_users"] = "high_negative_impact"
        elif user_risk > 0.4:
            stakeholder_impact["end_users"] = "moderate_negative_impact"
        else:
            stakeholder_impact["end_users"] = "low_impact"
        
        # Protected groups impact
        if system_profile.protected_characteristics:
            protected_risk = risk_factors.get("fairness", 0) + risk_factors.get("non_discrimination", 0)
            if protected_risk > 0.6:
                stakeholder_impact["protected_groups"] = "high_discrimination_risk"
            elif protected_risk > 0.3:
                stakeholder_impact["protected_groups"] = "moderate_discrimination_risk"
            else:
                stakeholder_impact["protected_groups"] = "low_discrimination_risk"
        
        # Children impact
        if "children" in system_profile.target_users:
            children_risk = risk_factors.get("children_protection", 0)
            if children_risk > 0.5:
                stakeholder_impact["children"] = "high_protection_concern"
            elif children_risk > 0.3:
                stakeholder_impact["children"] = "moderate_protection_concern"
            else:
                stakeholder_impact["children"] = "adequate_protection"
        
        # Society impact
        society_risk = statistics.mean([
            risk_factors.get("transparency", 0),
            risk_factors.get("accountability", 0),
            risk_factors.get("human_dignity", 0)
        ])
        
        if society_risk > 0.6:
            stakeholder_impact["society"] = "significant_societal_concern"
        elif society_risk > 0.3:
            stakeholder_impact["society"] = "moderate_societal_impact"
        else:
            stakeholder_impact["society"] = "minimal_societal_impact"
        
        return stakeholder_impact
    
    async def _calculate_ethical_compliance_score(self, risk_factors: Dict[str, float]) -> float:
        """Calculate overall ethical compliance score"""
        if not risk_factors:
            return 0.5
        
        # Weight critical principles more heavily
        weights = {
            "human_autonomy": 1.2,
            "prevention_of_harm": 1.5,
            "fairness": 1.3,
            "children_protection": 1.4,
            "privacy": 1.1,
            "explicability": 1.0,
            "transparency": 1.0,
            "accountability": 1.0,
            "human_dignity": 1.1,
            "non_discrimination": 1.3
        }
        
        weighted_risks = []
        for principle, risk in risk_factors.items():
            weight = weights.get(principle, 1.0)
            weighted_risks.append(risk * weight)
        
        avg_weighted_risk = statistics.mean(weighted_risks)
        
        # Convert risk to compliance score (inverse relationship)
        compliance_score = 1.0 - avg_weighted_risk
        
        return max(0.0, min(1.0, compliance_score))
    
    async def _generate_risk_mitigation_plan(self, 
                                           risk_factors: Dict[str, float],
                                           stakeholder_impact: Dict[str, str]) -> List[str]:
        """Generate risk mitigation plan"""
        mitigation_plan = []
        
        # High-risk principle mitigation
        high_risk_principles = [principle for principle, risk in risk_factors.items() if risk > 0.6]
        
        for principle in high_risk_principles:
            if principle == "human_autonomy":
                mitigation_plan.extend([
                    "Implement human oversight mechanisms",
                    "Provide opt-out options for automated decisions",
                    "Establish human review processes for high-stakes decisions"
                ])
            
            elif principle == "prevention_of_harm":
                mitigation_plan.extend([
                    "Implement comprehensive safety testing",
                    "Establish monitoring systems for harmful outcomes",
                    "Create incident response procedures"
                ])
            
            elif principle == "fairness":
                mitigation_plan.extend([
                    "Implement bias testing and mitigation",
                    "Conduct fairness audits across protected groups",
                    "Establish fairness metrics and thresholds"
                ])
            
            elif principle == "children_protection":
                mitigation_plan.extend([
                    "Implement additional safeguards for minors",
                    "Conduct child impact assessments",
                    "Establish parental consent mechanisms"
                ])
        
        # Stakeholder-specific mitigation
        if "high_negative_impact" in stakeholder_impact.values():
            mitigation_plan.extend([
                "Engage with affected stakeholder groups",
                "Implement stakeholder feedback mechanisms",
                "Conduct regular impact assessments"
            ])
        
        # General mitigation measures
        mitigation_plan.extend([
            "Establish AI ethics committee oversight",
            "Implement continuous monitoring and auditing",
            "Provide regular ethics training for development teams",
            "Document all ethical considerations and decisions"
        ])
        
        return mitigation_plan
    
    async def _assess_ethical_review_requirement(self, 
                                               system_profile: AISystemProfile,
                                               risk_factors: Dict[str, float]) -> bool:
        """Assess if ethical review board approval is required"""
        # High-risk categories always require approval
        if system_profile.risk_category in [AIRiskCategory.HIGH_RISK, AIRiskCategory.UNACCEPTABLE_RISK]:
            return True
        
        # High ethical risk scores require approval
        high_risk_count = sum(1 for risk in risk_factors.values() if risk > 0.7)
        if high_risk_count >= 2:
            return True
        
        # Sensitive system types require approval
        sensitive_types = [
            AISystemType.BIOMETRIC_IDENTIFICATION,
            AISystemType.EMOTION_RECOGNITION,
            AISystemType.AUTOMATED_DECISION_MAKING
        ]
        if system_profile.system_type in sensitive_types:
            return True
        
        # Systems affecting children require approval
        if "children" in system_profile.target_users:
            return True
        
        return False


# Main AI Compliance Engine
class AIComplianceEngine:
    """Main AI compliance and ethics management engine"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
        # Initialize components
        self.bias_detector = BiasDetector(redis_client)
        self.fairness_evaluator = FairnessEvaluator(redis_client)
        self.explainability_analyzer = ExplainabilityAnalyzer(redis_client)
        self.ethical_risk_analyzer = EthicalRiskAnalyzer(db_session, redis_client)
        
    async def conduct_comprehensive_ai_compliance_assessment(self, 
                                                           system_profile: AISystemProfile,
                                                           model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive AI compliance assessment"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Conduct bias assessment
            bias_assessment = None
            if "predictions" in model_data and "protected_attributes" in model_data:
                bias_assessment = await self.bias_detector.detect_bias(
                    system_profile.system_id,
                    model_data["predictions"],
                    model_data["protected_attributes"]
                )
            
            # Conduct fairness evaluation
            fairness_evaluation = None
            if ("predictions" in model_data and "ground_truth" in model_data and 
                "protected_attributes" in model_data):
                fairness_evaluation = await self.fairness_evaluator.evaluate_fairness(
                    system_profile.system_id,
                    model_data["predictions"],
                    model_data["ground_truth"],
                    model_data["protected_attributes"]
                )
            
            # Conduct explainability assessment
            explainability_assessment = await self.explainability_analyzer.assess_explainability(
                system_profile.system_id,
                model_data.get("model_info", {}),
                model_data.get("target_audience", ["end_users"])
            )
            
            # Conduct ethical risk assessment
            ethical_risk_assessment = await self.ethical_risk_analyzer.conduct_ethical_risk_assessment(
                system_profile.system_id,
                system_profile
            )
            
            # Calculate overall compliance score
            overall_compliance = await self._calculate_overall_compliance_score(
                bias_assessment, fairness_evaluation, explainability_assessment, ethical_risk_assessment
            )
            
            # Generate compliance recommendations
            recommendations = await self._generate_compliance_recommendations(
                bias_assessment, fairness_evaluation, explainability_assessment, ethical_risk_assessment
            )
            
            # Determine compliance status
            compliance_status = await self._determine_compliance_status(overall_compliance, ethical_risk_assessment)
            
            comprehensive_assessment = {
                "assessment_id": assessment_id,
                "system_profile": system_profile.__dict__,
                "bias_assessment": bias_assessment.__dict__ if bias_assessment else None,
                "fairness_evaluation": fairness_evaluation.__dict__ if fairness_evaluation else None,
                "explainability_assessment": explainability_assessment.__dict__,
                "ethical_risk_assessment": ethical_risk_assessment.__dict__,
                "overall_compliance_score": overall_compliance,
                "compliance_status": compliance_status,
                "recommendations": recommendations,
                "assessment_date": datetime.utcnow().isoformat(),
                "next_review_date": (datetime.utcnow() + timedelta(days=180)).isoformat()
            }
            
            # Cache assessment
            await self.redis.setex(f"ai_compliance_assessment:{assessment_id}", 3600 * 24 * 7,
                                  json.dumps(comprehensive_assessment, default=str))
            
            return comprehensive_assessment
            
        except Exception as e:
            logger.error(f"AI compliance assessment failed: {str(e)}")
            raise
    
    async def _calculate_overall_compliance_score(self, 
                                                bias_assessment: Optional[BiasAssessment],
                                                fairness_evaluation: Optional[FairnessEvaluation],
                                                explainability_assessment: ExplainabilityAssessment,
                                                ethical_risk_assessment: EthicalRiskAssessment) -> float:
        """Calculate overall AI compliance score"""
        scores = []
        weights = []
        
        # Bias score (if available)
        if bias_assessment:
            bias_score = 1.0 - (0.2 if bias_assessment.bias_severity == "critical" else
                               0.15 if bias_assessment.bias_severity == "high" else
                               0.1 if bias_assessment.bias_severity == "medium" else 0.05)
            scores.append(bias_score)
            weights.append(0.25)
        
        # Fairness score (if available)
        if fairness_evaluation:
            fairness_score = 1.0 if fairness_evaluation.compliance_status == "compliant" else \
                           0.7 if fairness_evaluation.compliance_status == "partially_compliant" else 0.4
            scores.append(fairness_score)
            weights.append(0.25)
        
        # Explainability score
        explainability_score = explainability_assessment.explanation_quality_score
        scores.append(explainability_score)
        weights.append(0.25)
        
        # Ethical compliance score
        ethical_score = ethical_risk_assessment.ethical_compliance_score
        scores.append(ethical_score)
        weights.append(0.25)
        
        # Calculate weighted average
        if scores and weights:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            weighted_score = sum(score * weight for score, weight in zip(scores, normalized_weights))
            return max(0.0, min(1.0, weighted_score))
        
        return 0.5
    
    async def _generate_compliance_recommendations(self, 
                                                 bias_assessment: Optional[BiasAssessment],
                                                 fairness_evaluation: Optional[FairnessEvaluation],
                                                 explainability_assessment: ExplainabilityAssessment,
                                                 ethical_risk_assessment: EthicalRiskAssessment) -> List[str]:
        """Generate comprehensive compliance recommendations"""
        recommendations = []
        
        # Bias recommendations
        if bias_assessment and bias_assessment.remediation_recommendations:
            recommendations.extend(bias_assessment.remediation_recommendations)
        
        # Fairness recommendations
        if fairness_evaluation and fairness_evaluation.recommendations:
            recommendations.extend(fairness_evaluation.recommendations)
        
        # Explainability recommendations
        if explainability_assessment.improvement_recommendations:
            recommendations.extend(explainability_assessment.improvement_recommendations)
        
        # Ethical risk recommendations
        if ethical_risk_assessment.risk_mitigation_plan:
            recommendations.extend(ethical_risk_assessment.risk_mitigation_plan)
        
        # Overall AI compliance recommendations
        recommendations.extend([
            "Establish AI governance framework",
            "Implement continuous AI monitoring and auditing",
            "Provide AI ethics training for development teams",
            "Create AI incident response procedures",
            "Establish stakeholder feedback mechanisms"
        ])
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return unique_recommendations
    
    async def _determine_compliance_status(self, 
                                         overall_score: float,
                                         ethical_assessment: EthicalRiskAssessment) -> str:
        """Determine overall compliance status"""
        if ethical_assessment.ethical_review_board_approval and overall_score >= 0.8:
            return "fully_compliant"
        elif overall_score >= 0.7:
            return "largely_compliant"
        elif overall_score >= 0.5:
            return "partially_compliant"
        else:
            return "non_compliant"


# Export main classes
__all__ = [
    "AIComplianceEngine",
    "BiasDetector",
    "FairnessEvaluator",
    "ExplainabilityAnalyzer",
    "EthicalRiskAnalyzer",
    "AIComplianceFramework",
    "AIRiskCategory",
    "BiasType",
    "FairnessMetric",
    "ExplainabilityLevel",
    "AISystemType",
    "AISystemProfile",
    "BiasAssessment",
    "FairnessEvaluation",
    "ExplainabilityAssessment",
    "EthicalRiskAssessment"
]
