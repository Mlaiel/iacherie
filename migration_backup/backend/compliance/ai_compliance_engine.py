"""
🤖 AI Compliance Engine - Enhanced Implementation
Advanced AI compliance system for responsible AI deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import numpy as np
from abc import ABC, abstractmethod


class AIComplianceStandard(str, Enum):
    """AI compliance standards and frameworks"""
    EU_AI_ACT = "eu_ai_act"
    IEEE_2857 = "ieee_2857"
    ISO_23053 = "iso_23053"
    NIST_AI_RMF = "nist_ai_rmf"
    GDPR_AI = "gdpr_ai"
    ALGORITHMIC_ACCOUNTABILITY = "algorithmic_accountability"
    FAIRNESS_INDICATORS = "fairness_indicators"
    EXPLAINABLE_AI = "explainable_ai"
    AI_ETHICS = "ai_ethics"


class AIRiskLevel(str, Enum):
    """AI system risk classification"""
    MINIMAL = "minimal"
    LIMITED = "limited"
    HIGH = "high"
    UNACCEPTABLE = "unacceptable"


class AIBiasType(str, Enum):
    """Types of AI bias to detect and mitigate"""
    DEMOGRAPHIC = "demographic"
    HISTORICAL = "historical"
    REPRESENTATION = "representation"
    MEASUREMENT = "measurement"
    AGGREGATION = "aggregation"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"


class AIModel(BaseModel):
    """AI model metadata for compliance tracking"""
    model_id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")
    model_type: str = Field(..., description="Type of AI model")
    purpose: str = Field(..., description="Model purpose and use case")
    training_data_info: Dict[str, Any] = Field(..., description="Training data metadata")
    deployment_date: datetime = Field(..., description="Model deployment date")
    last_evaluation: Optional[datetime] = Field(None, description="Last evaluation date")
    risk_level: AIRiskLevel = Field(..., description="Assessed risk level")
    fairness_metrics: Dict[str, float] = Field(default_factory=dict)
    explainability_score: Optional[float] = Field(None, ge=0, le=1)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    compliance_certifications: List[str] = Field(default_factory=list)


class AIComplianceViolation(BaseModel):
    """AI-specific compliance violation"""
    violation_id: str = Field(..., description="Unique violation identifier")
    model_id: str = Field(..., description="Associated model identifier")
    standard: AIComplianceStandard = Field(..., description="Violated standard")
    violation_type: str = Field(..., description="Type of violation")
    severity: str = Field(..., description="Violation severity")
    description: str = Field(..., description="Violation description")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    bias_metrics: Optional[Dict[str, float]] = Field(None, description="Bias measurement results")
    fairness_impact: Optional[Dict[str, Any]] = Field(None, description="Impact on fairness")
    remediation_required: bool = Field(..., description="Whether remediation is required")
    remediation_steps: List[str] = Field(default_factory=list)
    regulatory_risk: str = Field(default="medium", description="Regulatory risk level")


class BiasDetectionResult(BaseModel):
    """Bias detection analysis result"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    model_id: str = Field(..., description="Analyzed model identifier")
    bias_type: AIBiasType = Field(..., description="Type of bias analyzed")
    detected_bias: bool = Field(..., description="Whether bias was detected")
    bias_score: float = Field(..., ge=0, le=1, description="Bias severity score")
    affected_groups: List[str] = Field(default_factory=list, description="Groups affected by bias")
    statistical_evidence: Dict[str, Any] = Field(default_factory=dict)
    confidence_level: float = Field(..., ge=0, le=1, description="Detection confidence")
    recommendations: List[str] = Field(default_factory=list)
    mitigation_strategies: List[str] = Field(default_factory=list)


class ExplainabilityAssessment(BaseModel):
    """AI model explainability assessment"""
    assessment_id: str = Field(..., description="Unique assessment identifier")
    model_id: str = Field(..., description="Assessed model identifier")
    explainability_score: float = Field(..., ge=0, le=1, description="Overall explainability score")
    interpretation_methods: List[str] = Field(default_factory=list)
    local_explanations: bool = Field(..., description="Provides local explanations")
    global_explanations: bool = Field(..., description="Provides global explanations")
    feature_importance: Dict[str, float] = Field(default_factory=dict)
    decision_transparency: float = Field(..., ge=0, le=1)
    stakeholder_understanding: Dict[str, float] = Field(default_factory=dict)
    regulatory_compliance: Dict[str, bool] = Field(default_factory=dict)


class AIEthicsFramework:
    """AI ethics framework implementation"""
    
    def __init__(self):
        self.ethical_principles = [
            "Human-centered AI design",
            "Fairness and non-discrimination",
            "Transparency and explainability",
            "Accountability and responsibility",
            "Privacy and data protection",
            "Robustness and safety",
            "Human oversight and control"
        ]
    
    async def assess_ethical_compliance(self, model: AIModel) -> Dict[str, Any]:
        """Assess model against ethical principles"""
        
        assessment = {
            "model_id": model.model_id,
            "assessment_date": datetime.utcnow(),
            "ethical_scores": {},
            "violations": [],
            "recommendations": []
        }
        
        # Human-centered design assessment
        human_centered_score = await self._assess_human_centered_design(model)
        assessment["ethical_scores"]["human_centered"] = human_centered_score
        
        # Fairness assessment
        fairness_score = await self._assess_fairness(model)
        assessment["ethical_scores"]["fairness"] = fairness_score
        
        # Transparency assessment
        transparency_score = await self._assess_transparency(model)
        assessment["ethical_scores"]["transparency"] = transparency_score
        
        # Overall ethical score
        assessment["overall_score"] = np.mean(list(assessment["ethical_scores"].values()))
        
        return assessment
    
    async def _assess_human_centered_design(self, model: AIModel) -> float:
        """Assess human-centered design principles"""
        score = 0.8  # Base score
        
        # Check if model has human oversight mechanisms
        if "human_oversight" in model.purpose.lower():
            score += 0.1
        
        # Check if model supports human decision-making
        if "decision_support" in model.purpose.lower():
            score += 0.1
        
        return min(score, 1.0)
    
    async def _assess_fairness(self, model: AIModel) -> float:
        """Assess fairness and non-discrimination"""
        if not model.fairness_metrics:
            return 0.3  # Low score if no fairness metrics
        
        # Calculate fairness score based on metrics
        fairness_values = list(model.fairness_metrics.values())
        if fairness_values:
            return np.mean(fairness_values)
        
        return 0.5  # Default score
    
    async def _assess_transparency(self, model: AIModel) -> float:
        """Assess transparency and explainability"""
        if model.explainability_score:
            return model.explainability_score
        
        return 0.4  # Low score if no explainability assessment


class BiasDetectionEngine:
    """Advanced bias detection and mitigation engine"""
    
    def __init__(self):
        self.detection_methods = {
            AIBiasType.DEMOGRAPHIC: self._detect_demographic_bias,
            AIBiasType.HISTORICAL: self._detect_historical_bias,
            AIBiasType.REPRESENTATION: self._detect_representation_bias,
            AIBiasType.MEASUREMENT: self._detect_measurement_bias,
        }
    
    async def comprehensive_bias_analysis(
        self,
        model: AIModel,
        test_data: Dict[str, Any],
        protected_attributes: List[str]
    ) -> List[BiasDetectionResult]:
        """Perform comprehensive bias analysis"""
        
        results = []
        
        for bias_type, detection_method in self.detection_methods.items():
            try:
                result = await detection_method(model, test_data, protected_attributes)
                results.append(result)
            except Exception as e:
                # Log error and continue with other tests
                continue
        
        return results
    
    async def _detect_demographic_bias(
        self,
        model: AIModel,
        test_data: Dict[str, Any],
        protected_attributes: List[str]
    ) -> BiasDetectionResult:
        """Detect demographic bias in model predictions"""
        
        # Simulate bias detection (in real implementation, this would use actual ML libraries)
        bias_detected = False
        bias_score = 0.0
        affected_groups = []
        
        # Example: Check prediction disparities across demographic groups
        for attribute in protected_attributes:
            if attribute in test_data:
                # Calculate statistical parity difference
                group_predictions = test_data.get(f"{attribute}_predictions", {})
                if len(group_predictions) > 1:
                    prediction_rates = list(group_predictions.values())
                    max_diff = max(prediction_rates) - min(prediction_rates)
                    
                    if max_diff > 0.1:  # 10% threshold
                        bias_detected = True
                        bias_score = max(bias_score, max_diff)
                        affected_groups.append(attribute)
        
        return BiasDetectionResult(
            analysis_id=f"DEMO_BIAS_{model.model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            model_id=model.model_id,
            bias_type=AIBiasType.DEMOGRAPHIC,
            detected_bias=bias_detected,
            bias_score=bias_score,
            affected_groups=affected_groups,
            statistical_evidence={"statistical_parity_difference": bias_score},
            confidence_level=0.85,
            recommendations=[
                "Review training data for demographic balance",
                "Implement fairness constraints during training",
                "Regular bias monitoring in production"
            ] if bias_detected else ["Continue regular bias monitoring"],
            mitigation_strategies=[
                "Data augmentation for underrepresented groups",
                "Algorithmic debiasing techniques",
                "Post-processing calibration"
            ] if bias_detected else []
        )
    
    async def _detect_historical_bias(
        self,
        model: AIModel,
        test_data: Dict[str, Any],
        protected_attributes: List[str]
    ) -> BiasDetectionResult:
        """Detect historical bias in training data"""
        
        # Check training data metadata for historical bias indicators
        training_info = model.training_data_info
        bias_detected = False
        bias_score = 0.0
        
        # Check data time period
        data_period = training_info.get("time_period", "")
        if "historical" in data_period.lower() or "past" in data_period.lower():
            bias_detected = True
            bias_score = 0.6
        
        return BiasDetectionResult(
            analysis_id=f"HIST_BIAS_{model.model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            model_id=model.model_id,
            bias_type=AIBiasType.HISTORICAL,
            detected_bias=bias_detected,
            bias_score=bias_score,
            affected_groups=[],
            statistical_evidence={"historical_data_indicators": data_period},
            confidence_level=0.75,
            recommendations=[
                "Review historical context of training data",
                "Update training data with recent examples",
                "Apply temporal bias correction techniques"
            ] if bias_detected else ["Monitor for temporal drift"],
            mitigation_strategies=[
                "Data refresh with current examples",
                "Temporal reweighting",
                "Continuous learning approaches"
            ] if bias_detected else []
        )
    
    async def _detect_representation_bias(
        self,
        model: AIModel,
        test_data: Dict[str, Any],
        protected_attributes: List[str]
    ) -> BiasDetectionResult:
        """Detect representation bias in training data"""
        
        training_info = model.training_data_info
        bias_detected = False
        bias_score = 0.0
        affected_groups = []
        
        # Check data representation balance
        group_representation = training_info.get("group_representation", {})
        if group_representation:
            representation_values = list(group_representation.values())
            if representation_values:
                min_repr = min(representation_values)
                max_repr = max(representation_values)
                imbalance_ratio = min_repr / max_repr if max_repr > 0 else 0
                
                if imbalance_ratio < 0.3:  # Significant underrepresentation
                    bias_detected = True
                    bias_score = 1 - imbalance_ratio
                    affected_groups = [k for k, v in group_representation.items() if v == min_repr]
        
        return BiasDetectionResult(
            analysis_id=f"REPR_BIAS_{model.model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            model_id=model.model_id,
            bias_type=AIBiasType.REPRESENTATION,
            detected_bias=bias_detected,
            bias_score=bias_score,
            affected_groups=affected_groups,
            statistical_evidence={"group_representation": group_representation},
            confidence_level=0.90,
            recommendations=[
                "Balance training data representation",
                "Collect additional data for underrepresented groups",
                "Apply sampling techniques to balance groups"
            ] if bias_detected else ["Maintain balanced representation"],
            mitigation_strategies=[
                "Stratified sampling",
                "Synthetic data generation",
                "Transfer learning from related domains"
            ] if bias_detected else []
        )
    
    async def _detect_measurement_bias(
        self,
        model: AIModel,
        test_data: Dict[str, Any],
        protected_attributes: List[str]
    ) -> BiasDetectionResult:
        """Detect measurement bias in data collection"""
        
        # Analyze data collection methodology
        training_info = model.training_data_info
        collection_method = training_info.get("collection_method", "")
        
        bias_detected = False
        bias_score = 0.0
        
        # Check for problematic collection methods
        problematic_methods = ["self-reported", "single-source", "convenience-sample"]
        if any(method in collection_method.lower() for method in problematic_methods):
            bias_detected = True
            bias_score = 0.5
        
        return BiasDetectionResult(
            analysis_id=f"MEAS_BIAS_{model.model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            model_id=model.model_id,
            bias_type=AIBiasType.MEASUREMENT,
            detected_bias=bias_detected,
            bias_score=bias_score,
            affected_groups=[],
            statistical_evidence={"collection_method": collection_method},
            confidence_level=0.70,
            recommendations=[
                "Review data collection methodology",
                "Implement multiple measurement approaches",
                "Validate measurements across different contexts"
            ] if bias_detected else ["Continue current measurement practices"],
            mitigation_strategies=[
                "Multi-source data collection",
                "Measurement error modeling",
                "Cross-validation with external datasets"
            ] if bias_detected else []
        )


class ExplainabilityEngine:
    """AI explainability and interpretability engine"""
    
    def __init__(self):
        self.explanation_methods = [
            "SHAP (SHapley Additive exPlanations)",
            "LIME (Local Interpretable Model-agnostic Explanations)",
            "Integrated Gradients",
            "Attention Mechanisms",
            "Rule-based Explanations"
        ]
    
    async def assess_model_explainability(self, model: AIModel) -> ExplainabilityAssessment:
        """Assess model explainability capabilities"""
        
        # Determine available explanation methods based on model type
        available_methods = await self._determine_explanation_methods(model)
        
        # Calculate explainability scores
        local_explanations = await self._assess_local_explanations(model)
        global_explanations = await self._assess_global_explanations(model)
        decision_transparency = await self._assess_decision_transparency(model)
        
        # Overall explainability score
        overall_score = np.mean([
            0.4 * local_explanations,
            0.3 * global_explanations,
            0.3 * decision_transparency
        ])
        
        return ExplainabilityAssessment(
            assessment_id=f"EXPLAIN_{model.model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            model_id=model.model_id,
            explainability_score=overall_score,
            interpretation_methods=available_methods,
            local_explanations=local_explanations > 0.7,
            global_explanations=global_explanations > 0.7,
            feature_importance=await self._calculate_feature_importance(model),
            decision_transparency=decision_transparency,
            stakeholder_understanding={
                "technical_users": overall_score,
                "business_users": overall_score * 0.8,
                "end_users": overall_score * 0.6
            },
            regulatory_compliance={
                "eu_ai_act": overall_score > 0.8,
                "gdpr_explainability": overall_score > 0.7,
                "algorithmic_accountability": overall_score > 0.75
            }
        )
    
    async def _determine_explanation_methods(self, model: AIModel) -> List[str]:
        """Determine applicable explanation methods for model type"""
        
        methods = []
        model_type = model.model_type.lower()
        
        if "neural" in model_type or "deep" in model_type:
            methods.extend(["SHAP", "Integrated Gradients", "LIME"])
        
        if "tree" in model_type or "forest" in model_type:
            methods.extend(["SHAP", "Feature Importance", "Rule Extraction"])
        
        if "linear" in model_type:
            methods.extend(["Coefficient Analysis", "LIME"])
        
        if "attention" in model_type or "transformer" in model_type:
            methods.extend(["Attention Visualization", "SHAP"])
        
        return methods
    
    async def _assess_local_explanations(self, model: AIModel) -> float:
        """Assess local explanation capabilities"""
        if model.explainability_score:
            return model.explainability_score
        
        # Default assessment based on model type
        model_type = model.model_type.lower()
        if "linear" in model_type:
            return 0.9
        elif "tree" in model_type:
            return 0.8
        elif "neural" in model_type:
            return 0.6
        else:
            return 0.5
    
    async def _assess_global_explanations(self, model: AIModel) -> float:
        """Assess global explanation capabilities"""
        model_type = model.model_type.lower()
        if "linear" in model_type or "tree" in model_type:
            return 0.8
        elif "neural" in model_type and "simple" in model_type:
            return 0.6
        else:
            return 0.4
    
    async def _assess_decision_transparency(self, model: AIModel) -> float:
        """Assess decision-making transparency"""
        # Based on model complexity and available documentation
        if model.purpose and len(model.purpose) > 50:  # Well-documented purpose
            return 0.8
        else:
            return 0.6
    
    async def _calculate_feature_importance(self, model: AIModel) -> Dict[str, float]:
        """Calculate feature importance (simulated)"""
        # In real implementation, this would calculate actual feature importance
        return {
            "feature_1": 0.25,
            "feature_2": 0.20,
            "feature_3": 0.15,
            "feature_4": 0.12,
            "feature_5": 0.10,
            "others": 0.18
        }


class AIComplianceOrchestrator:
    """Central orchestrator for AI compliance management"""
    
    def __init__(self):
        self.ethics_framework = AIEthicsFramework()
        self.bias_detector = BiasDetectionEngine()
        self.explainability_engine = ExplainabilityEngine()
        self.compliance_history: List[Dict[str, Any]] = []
    
    async def comprehensive_ai_compliance_assessment(
        self,
        model: AIModel,
        test_data: Optional[Dict[str, Any]] = None,
        protected_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive AI compliance assessment"""
        
        assessment_results = {
            "model_id": model.model_id,
            "assessment_date": datetime.utcnow(),
            "overall_compliance_score": 0.0,
            "risk_level": model.risk_level,
            "violations": [],
            "recommendations": [],
            "detailed_assessments": {}
        }
        
        # Ethics assessment
        ethics_assessment = await self.ethics_framework.assess_ethical_compliance(model)
        assessment_results["detailed_assessments"]["ethics"] = ethics_assessment
        
        # Bias detection
        if test_data and protected_attributes:
            bias_results = await self.bias_detector.comprehensive_bias_analysis(
                model, test_data, protected_attributes
            )
            assessment_results["detailed_assessments"]["bias_detection"] = bias_results
            
            # Check for bias violations
            for bias_result in bias_results:
                if bias_result.detected_bias and bias_result.bias_score > 0.3:
                    violation = AIComplianceViolation(
                        violation_id=f"BIAS_VIOLATION_{model.model_id}_{bias_result.bias_type}",
                        model_id=model.model_id,
                        standard=AIComplianceStandard.FAIRNESS_INDICATORS,
                        violation_type=f"bias_{bias_result.bias_type}",
                        severity="high" if bias_result.bias_score > 0.5 else "medium",
                        description=f"Detected {bias_result.bias_type} bias with score {bias_result.bias_score}",
                        bias_metrics={"bias_score": bias_result.bias_score},
                        remediation_required=True,
                        remediation_steps=bias_result.mitigation_strategies
                    )
                    assessment_results["violations"].append(violation)
        
        # Explainability assessment
        explainability_assessment = await self.explainability_engine.assess_model_explainability(model)
        assessment_results["detailed_assessments"]["explainability"] = explainability_assessment
        
        # Check for explainability violations
        if explainability_assessment.explainability_score < 0.7:
            violation = AIComplianceViolation(
                violation_id=f"EXPLAIN_VIOLATION_{model.model_id}",
                model_id=model.model_id,
                standard=AIComplianceStandard.EXPLAINABLE_AI,
                violation_type="insufficient_explainability",
                severity="high" if explainability_assessment.explainability_score < 0.5 else "medium",
                description=f"Insufficient explainability score: {explainability_assessment.explainability_score}",
                remediation_required=True,
                remediation_steps=[
                    "Implement SHAP explanations",
                    "Add feature importance analysis",
                    "Provide decision reasoning"
                ]
            )
            assessment_results["violations"].append(violation)
        
        # Calculate overall compliance score
        assessment_results["overall_compliance_score"] = await self._calculate_overall_compliance_score(
            assessment_results
        )
        
        # Generate recommendations
        assessment_results["recommendations"] = await self._generate_ai_recommendations(
            assessment_results
        )
        
        # Store in history
        self.compliance_history.append(assessment_results)
        
        return assessment_results
    
    async def _calculate_overall_compliance_score(self, assessment_results: Dict[str, Any]) -> float:
        """Calculate overall AI compliance score"""
        
        scores = []
        
        # Ethics score
        if "ethics" in assessment_results["detailed_assessments"]:
            ethics_score = assessment_results["detailed_assessments"]["ethics"].get("overall_score", 0)
            scores.append(ethics_score * 0.4)  # 40% weight
        
        # Explainability score
        if "explainability" in assessment_results["detailed_assessments"]:
            explain_score = assessment_results["detailed_assessments"]["explainability"].explainability_score
            scores.append(explain_score * 0.3)  # 30% weight
        
        # Bias score (inverse - higher bias = lower compliance)
        if "bias_detection" in assessment_results["detailed_assessments"]:
            bias_results = assessment_results["detailed_assessments"]["bias_detection"]
            avg_bias_score = np.mean([1 - result.bias_score for result in bias_results])
            scores.append(avg_bias_score * 0.3)  # 30% weight
        
        # Penalty for violations
        violation_penalty = len(assessment_results["violations"]) * 0.1
        
        overall_score = np.mean(scores) if scores else 0.5
        overall_score = max(0, overall_score - violation_penalty)
        
        return round(overall_score, 3)
    
    async def _generate_ai_recommendations(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Generate AI compliance recommendations"""
        
        recommendations = []
        
        # Based on overall score
        overall_score = assessment_results["overall_compliance_score"]
        if overall_score < 0.6:
            recommendations.append("URGENT: Comprehensive AI compliance review required")
        elif overall_score < 0.8:
            recommendations.append("Improve AI compliance measures")
        
        # Based on violations
        violations = assessment_results["violations"]
        if violations:
            recommendations.append(f"Address {len(violations)} identified compliance violations")
            
            bias_violations = [v for v in violations if "bias" in v.violation_type]
            if bias_violations:
                recommendations.append("Implement bias detection and mitigation strategies")
            
            explain_violations = [v for v in violations if "explain" in v.violation_type]
            if explain_violations:
                recommendations.append("Enhance model explainability and transparency")
        
        # General recommendations
        recommendations.extend([
            "Regular AI compliance monitoring and assessment",
            "Implement continuous bias monitoring in production",
            "Establish AI ethics review board",
            "Provide AI ethics training for development teams"
        ])
        
        return recommendations
    
    async def monitor_production_compliance(self, model_ids: List[str]) -> Dict[str, Any]:
        """Monitor AI compliance in production"""
        
        monitoring_results = {
            "monitoring_date": datetime.utcnow(),
            "models_monitored": len(model_ids),
            "compliance_alerts": [],
            "performance_drift": {},
            "bias_drift": {},
            "recommendations": []
        }
        
        # This would implement real-time monitoring
        # For now, return monitoring framework structure
        
        return monitoring_results
    
    def get_ai_compliance_dashboard(self) -> Dict[str, Any]:
        """Generate AI compliance dashboard"""
        
        if not self.compliance_history:
            return {"message": "No AI compliance assessments available"}
        
        recent_assessments = sorted(
            self.compliance_history, 
            key=lambda x: x["assessment_date"], 
            reverse=True
        )[:10]
        
        dashboard = {
            "total_assessments": len(self.compliance_history),
            "average_compliance_score": np.mean([
                a["overall_compliance_score"] for a in self.compliance_history
            ]),
            "recent_assessments": recent_assessments,
            "high_risk_models": [
                a for a in recent_assessments 
                if a["overall_compliance_score"] < 0.6
            ],
            "compliance_trends": self._calculate_ai_compliance_trends(),
            "violation_summary": self._summarize_violations()
        }
        
        return dashboard
    
    def _calculate_ai_compliance_trends(self) -> Dict[str, Any]:
        """Calculate AI compliance trends"""
        
        if len(self.compliance_history) < 2:
            return {"message": "Insufficient data for trend analysis"}
        
        # Calculate monthly trends
        monthly_scores = {}
        for assessment in self.compliance_history:
            month_key = assessment["assessment_date"].strftime("%Y-%m")
            if month_key not in monthly_scores:
                monthly_scores[month_key] = []
            monthly_scores[month_key].append(assessment["overall_compliance_score"])
        
        trends = {
            "monthly_averages": {
                month: np.mean(scores) 
                for month, scores in monthly_scores.items()
            },
            "improvement_trend": "positive" if self.compliance_history[-1]["overall_compliance_score"] > self.compliance_history[0]["overall_compliance_score"] else "negative"
        }
        
        return trends
    
    def _summarize_violations(self) -> Dict[str, Any]:
        """Summarize AI compliance violations"""
        
        all_violations = []
        for assessment in self.compliance_history:
            all_violations.extend(assessment["violations"])
        
        if not all_violations:
            return {"message": "No violations recorded"}
        
        violation_types = {}
        severity_counts = {}
        
        for violation in all_violations:
            vtype = violation.violation_type
            severity = violation.severity
            
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_violations": len(all_violations),
            "by_type": violation_types,
            "by_severity": severity_counts,
            "most_common_type": max(violation_types.items(), key=lambda x: x[1])[0] if violation_types else None
        }


# Export classes for external use
__all__ = [
    'AIComplianceStandard',
    'AIRiskLevel',
    'AIBiasType',
    'AIModel',
    'AIComplianceViolation',
    'BiasDetectionResult',
    'ExplainabilityAssessment',
    'AIEthicsFramework',
    'BiasDetectionEngine',
    'ExplainabilityEngine',
    'AIComplianceOrchestrator'
]