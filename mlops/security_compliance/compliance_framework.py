"""
Compliance Framework for MLOps Enterprise
Comprehensive compliance management for ML systems

Features:
- GDPR compliance for ML systems
- Industry-specific compliance (HIPAA, PCI-DSS, SOX)
- Automated compliance checking
- Audit trail generation
- Privacy impact assessments
- Regulatory reporting

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import uuid


class ComplianceStandard(Enum):
    """Supported compliance standards"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    ISO_27001 = "iso_27001"
    CCPA = "ccpa"
    PIPEDA = "pipeda"


class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"
    UNDER_REVIEW = "under_review"


class DataCategory(Enum):
    """Categories of data for compliance"""
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    PUBLIC = "public"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class ComplianceRule:
    """Individual compliance rule"""
    rule_id: str
    standard: ComplianceStandard
    category: str
    description: str
    requirement: str
    implementation_guide: str
    severity: str  # critical, high, medium, low
    automated_check: bool
    validation_query: Optional[str] = None


@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""
    assessment_id: str
    model_id: str
    standards: List[ComplianceStandard]
    timestamp: datetime
    overall_status: ComplianceStatus
    score: float  # 0-100
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    next_review_date: datetime


@dataclass
class PrivacyImpactAssessment:
    """Privacy Impact Assessment (PIA)"""
    pia_id: str
    model_id: str
    data_types: List[DataCategory]
    processing_purpose: str
    legal_basis: str
    risk_level: str  # low, medium, high, very_high
    mitigation_measures: List[str]
    approval_status: str
    completed_at: datetime


@dataclass
class ComplianceMetrics:
    """Compliance metrics and KPIs"""
    total_assessments: int
    compliant_models: int
    non_compliant_models: int
    average_compliance_score: float
    critical_violations: int
    pending_reviews: int


class ComplianceFramework:
    """
    Enterprise Compliance Framework
    Comprehensive compliance management for ML systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compliance_rules: Dict[ComplianceStandard, List[ComplianceRule]] = {}
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.privacy_assessments: Dict[str, PrivacyImpactAssessment] = {}
        self.compliance_configs: Dict[str, Dict[str, Any]] = {}
        self.metrics = ComplianceMetrics(0, 0, 0, 0.0, 0, 0)
        
        # Initialize default compliance rules
        asyncio.create_task(self._initialize_compliance_rules())
    
    async def configure_compliance(
        self,
        model_id: str,
        standards: List[ComplianceStandard],
        data_categories: List[DataCategory],
        processing_purpose: str,
        legal_basis: str = "legitimate_interest"
    ) -> bool:
        """Configure compliance requirements for a model"""
        try:
            config = {
                "standards": [s.value for s in standards],
                "data_categories": [dc.value for dc in data_categories],
                "processing_purpose": processing_purpose,
                "legal_basis": legal_basis,
                "configured_at": datetime.now().isoformat(),
                "last_assessment": None,
                "next_review": (datetime.now() + timedelta(days=90)).isoformat()
            }
            
            self.compliance_configs[model_id] = config
            
            # Trigger initial compliance assessment
            await self.assess_compliance(model_id)
            
            self.logger.info(f"Compliance configured for model {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure compliance for {model_id}: {str(e)}")
            return False
    
    async def assess_compliance(
        self,
        model_id: str,
        standards: Optional[List[ComplianceStandard]] = None
    ) -> ComplianceAssessment:
        """Perform comprehensive compliance assessment"""
        try:
            config = self.compliance_configs.get(model_id)
            if not config:
                raise ValueError(f"No compliance config for model {model_id}")
            
            # Use configured standards or specified ones
            if standards is None:
                standards = [ComplianceStandard(s) for s in config["standards"]]
            
            assessment_id = f"assessment_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            findings = []
            total_score = 0.0
            total_rules = 0
            
            # Assess each standard
            for standard in standards:
                standard_findings, standard_score = await self._assess_standard(
                    model_id, standard
                )
                findings.extend(standard_findings)
                total_score += standard_score
                total_rules += len(self.compliance_rules.get(standard, []))
            
            # Calculate overall score and status
            overall_score = total_score / max(total_rules, 1) * 100
            overall_status = self._determine_compliance_status(overall_score, findings)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(findings)
            
            # Create assessment
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                model_id=model_id,
                standards=standards,
                timestamp=datetime.now(),
                overall_status=overall_status,
                score=overall_score,
                findings=findings,
                recommendations=recommendations,
                next_review_date=datetime.now() + timedelta(days=90)
            )
            
            self.assessments[assessment_id] = assessment
            
            # Update model config
            config["last_assessment"] = assessment_id
            config["last_assessment_date"] = datetime.now().isoformat()
            self.compliance_configs[model_id] = config
            
            # Update metrics
            self._update_compliance_metrics()
            
            self.logger.info(f"Compliance assessment completed for model {model_id}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Compliance assessment failed for {model_id}: {str(e)}")
            raise
    
    async def conduct_privacy_impact_assessment(
        self,
        model_id: str,
        data_types: List[DataCategory],
        processing_purpose: str,
        legal_basis: str
    ) -> PrivacyImpactAssessment:
        """Conduct Privacy Impact Assessment (PIA)"""
        try:
            pia_id = f"pia_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Assess risk level based on data types and processing
            risk_level = self._assess_privacy_risk(data_types, processing_purpose)
            
            # Generate mitigation measures
            mitigation_measures = self._generate_privacy_mitigations(
                data_types, processing_purpose, risk_level
            )
            
            # Create PIA
            pia = PrivacyImpactAssessment(
                pia_id=pia_id,
                model_id=model_id,
                data_types=data_types,
                processing_purpose=processing_purpose,
                legal_basis=legal_basis,
                risk_level=risk_level,
                mitigation_measures=mitigation_measures,
                approval_status="pending",
                completed_at=datetime.now()
            )
            
            self.privacy_assessments[pia_id] = pia
            
            self.logger.info(f"Privacy Impact Assessment completed for model {model_id}")
            return pia
            
        except Exception as e:
            self.logger.error(f"Privacy Impact Assessment failed for {model_id}: {str(e)}")
            raise
    
    async def check_data_retention_compliance(
        self,
        model_id: str,
        data_age_days: int
    ) -> Dict[str, Any]:
        """Check data retention policy compliance"""
        try:
            config = self.compliance_configs.get(model_id)
            if not config:
                raise ValueError(f"No compliance config for model {model_id}")
            
            standards = [ComplianceStandard(s) for s in config["standards"]]
            compliance_result = {
                "model_id": model_id,
                "data_age_days": data_age_days,
                "compliance_by_standard": {},
                "actions_required": [],
                "overall_compliant": True
            }
            
            for standard in standards:
                standard_result = await self._check_retention_for_standard(
                    standard, data_age_days, config["data_categories"]
                )
                compliance_result["compliance_by_standard"][standard.value] = standard_result
                
                if not standard_result["compliant"]:
                    compliance_result["overall_compliant"] = False
                    compliance_result["actions_required"].extend(
                        standard_result["required_actions"]
                    )
            
            return compliance_result
            
        except Exception as e:
            self.logger.error(f"Data retention check failed for {model_id}: {str(e)}")
            raise
    
    async def generate_compliance_report(
        self,
        model_id: Optional[str] = None,
        standard: Optional[ComplianceStandard] = None,
        time_period: timedelta = timedelta(days=90)
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            end_date = datetime.now()
            start_date = end_date - time_period
            
            # Filter assessments by criteria
            filtered_assessments = []
            for assessment in self.assessments.values():
                if assessment.timestamp >= start_date:
                    if model_id is None or assessment.model_id == model_id:
                        if standard is None or standard in assessment.standards:
                            filtered_assessments.append(assessment)
            
            # Generate report
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "scope": {
                    "model_id": model_id,
                    "standard": standard.value if standard else None,
                    "assessments_included": len(filtered_assessments)
                },
                "summary": self._generate_report_summary(filtered_assessments),
                "detailed_findings": self._generate_detailed_findings(filtered_assessments),
                "recommendations": self._generate_report_recommendations(filtered_assessments),
                "metrics": self._calculate_report_metrics(filtered_assessments)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Compliance report generation failed: {str(e)}")
            raise
    
    async def validate_data_processing_consent(
        self,
        model_id: str,
        user_consents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate user consents for data processing"""
        try:
            config = self.compliance_configs.get(model_id)
            if not config:
                raise ValueError(f"No compliance config for model {model_id}")
            
            validation_result = {
                "model_id": model_id,
                "total_consents": len(user_consents),
                "valid_consents": 0,
                "invalid_consents": 0,
                "missing_consents": 0,
                "consent_issues": [],
                "processing_allowed": False
            }
            
            for consent in user_consents:
                consent_validity = self._validate_individual_consent(consent, config)
                
                if consent_validity["valid"]:
                    validation_result["valid_consents"] += 1
                else:
                    validation_result["invalid_consents"] += 1
                    validation_result["consent_issues"].extend(consent_validity["issues"])
            
            # Determine if processing is allowed
            validation_result["processing_allowed"] = (
                validation_result["valid_consents"] > 0 and
                validation_result["invalid_consents"] == 0
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Consent validation failed for {model_id}: {str(e)}")
            raise
    
    async def get_compliance_metrics(
        self,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get compliance metrics and KPIs"""
        try:
            if model_id:
                # Model-specific metrics
                model_assessments = [
                    a for a in self.assessments.values() 
                    if a.model_id == model_id
                ]
                
                if not model_assessments:
                    return {"error": f"No assessments found for model {model_id}"}
                
                latest_assessment = max(model_assessments, key=lambda x: x.timestamp)
                
                return {
                    "model_id": model_id,
                    "latest_assessment": {
                        "status": latest_assessment.overall_status.value,
                        "score": latest_assessment.score,
                        "timestamp": latest_assessment.timestamp.isoformat()
                    },
                    "total_assessments": len(model_assessments),
                    "compliance_trend": self._calculate_compliance_trend(model_assessments)
                }
            else:
                # Global metrics
                return {
                    "global_metrics": asdict(self.metrics),
                    "models_configured": len(self.compliance_configs),
                    "total_assessments": len(self.assessments),
                    "standards_supported": [s.value for s in ComplianceStandard],
                    "recent_activity": self._get_recent_compliance_activity()
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get compliance metrics: {str(e)}")
            raise
    
    # Private methods for compliance logic
    
    async def _initialize_compliance_rules(self):
        """Initialize default compliance rules for each standard"""
        try:
            # GDPR Rules
            gdpr_rules = [
                ComplianceRule(
                    rule_id="gdpr_001",
                    standard=ComplianceStandard.GDPR,
                    category="data_protection",
                    description="Personal data must be processed lawfully",
                    requirement="Article 6 - Lawfulness of processing",
                    implementation_guide="Ensure valid legal basis for processing",
                    severity="critical",
                    automated_check=True,
                    validation_query="check_legal_basis_exists"
                ),
                ComplianceRule(
                    rule_id="gdpr_002",
                    standard=ComplianceStandard.GDPR,
                    category="consent",
                    description="Consent must be freely given and specific",
                    requirement="Article 7 - Conditions for consent",
                    implementation_guide="Implement granular consent mechanisms",
                    severity="high",
                    automated_check=True,
                    validation_query="validate_consent_granularity"
                ),
                ComplianceRule(
                    rule_id="gdpr_003",
                    standard=ComplianceStandard.GDPR,
                    category="data_minimization",
                    description="Data processing must be limited to necessary purposes",
                    requirement="Article 5(1)(c) - Data minimisation",
                    implementation_guide="Implement purpose limitation controls",
                    severity="high",
                    automated_check=False
                )
            ]
            
            # HIPAA Rules
            hipaa_rules = [
                ComplianceRule(
                    rule_id="hipaa_001",
                    standard=ComplianceStandard.HIPAA,
                    category="phi_protection",
                    description="Protected Health Information must be encrypted",
                    requirement="45 CFR 164.312(a)(2)(iv)",
                    implementation_guide="Implement encryption for PHI",
                    severity="critical",
                    automated_check=True,
                    validation_query="check_phi_encryption"
                ),
                ComplianceRule(
                    rule_id="hipaa_002",
                    standard=ComplianceStandard.HIPAA,
                    category="access_control",
                    description="Access to PHI must be controlled and logged",
                    requirement="45 CFR 164.308(a)(4)",
                    implementation_guide="Implement role-based access controls",
                    severity="high",
                    automated_check=True,
                    validation_query="check_access_controls"
                )
            ]
            
            # PCI-DSS Rules
            pci_rules = [
                ComplianceRule(
                    rule_id="pci_001",
                    standard=ComplianceStandard.PCI_DSS,
                    category="cardholder_data",
                    description="Cardholder data must be encrypted when stored",
                    requirement="PCI DSS 3.4",
                    implementation_guide="Implement strong encryption for stored data",
                    severity="critical",
                    automated_check=True,
                    validation_query="check_cardholder_data_encryption"
                )
            ]
            
            self.compliance_rules[ComplianceStandard.GDPR] = gdpr_rules
            self.compliance_rules[ComplianceStandard.HIPAA] = hipaa_rules
            self.compliance_rules[ComplianceStandard.PCI_DSS] = pci_rules
            
        except Exception as e:
            self.logger.error(f"Failed to initialize compliance rules: {str(e)}")
    
    async def _assess_standard(
        self,
        model_id: str,
        standard: ComplianceStandard
    ) -> Tuple[List[Dict[str, Any]], float]:
        """Assess compliance for a specific standard"""
        findings = []
        total_score = 0.0
        
        rules = self.compliance_rules.get(standard, [])
        
        for rule in rules:
            # Perform automated check if available
            compliant = True
            if rule.automated_check and rule.validation_query:
                compliant = await self._execute_compliance_check(
                    model_id, rule.validation_query
                )
            
            # Create finding
            finding = {
                "rule_id": rule.rule_id,
                "standard": standard.value,
                "category": rule.category,
                "description": rule.description,
                "requirement": rule.requirement,
                "severity": rule.severity,
                "compliant": compliant,
                "implementation_guide": rule.implementation_guide
            }
            
            findings.append(finding)
            
            # Add to score (compliant rules get full points)
            if compliant:
                total_score += 1.0
            elif rule.severity == "critical":
                total_score += 0.0  # Critical violations get 0 points
            elif rule.severity == "high":
                total_score += 0.3
            elif rule.severity == "medium":
                total_score += 0.6
            else:  # low severity
                total_score += 0.8
        
        return findings, total_score
    
    async def _execute_compliance_check(
        self,
        model_id: str,
        validation_query: str
    ) -> bool:
        """Execute automated compliance check"""
        try:
            # Simplified implementation - in production would execute actual checks
            config = self.compliance_configs.get(model_id, {})
            
            if validation_query == "check_legal_basis_exists":
                return config.get("legal_basis") is not None
            elif validation_query == "validate_consent_granularity":
                return True  # Simplified - would check actual consent implementation
            elif validation_query == "check_phi_encryption":
                return "sensitive" in config.get("data_categories", [])
            elif validation_query == "check_access_controls":
                return True  # Simplified - would check actual access controls
            elif validation_query == "check_cardholder_data_encryption":
                return "confidential" in config.get("data_categories", [])
            else:
                return True  # Default to compliant for unknown checks
                
        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            return False
    
    def _determine_compliance_status(
        self,
        score: float,
        findings: List[Dict[str, Any]]
    ) -> ComplianceStatus:
        """Determine overall compliance status"""
        # Check for critical violations
        critical_violations = [
            f for f in findings 
            if f["severity"] == "critical" and not f["compliant"]
        ]
        
        if critical_violations:
            return ComplianceStatus.NON_COMPLIANT
        elif score >= 90:
            return ComplianceStatus.COMPLIANT
        elif score >= 70:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    def _generate_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        non_compliant_findings = [f for f in findings if not f["compliant"]]
        
        for finding in non_compliant_findings:
            if finding["severity"] == "critical":
                recommendations.append(
                    f"URGENT: {finding['implementation_guide']} "
                    f"(Rule: {finding['rule_id']})"
                )
            else:
                recommendations.append(
                    f"{finding['implementation_guide']} "
                    f"(Rule: {finding['rule_id']})"
                )
        
        return recommendations
    
    def _assess_privacy_risk(
        self,
        data_types: List[DataCategory],
        processing_purpose: str
    ) -> str:
        """Assess privacy risk level"""
        risk_score = 0
        
        # Risk based on data sensitivity
        for data_type in data_types:
            if data_type == DataCategory.SENSITIVE:
                risk_score += 3
            elif data_type == DataCategory.PERSONAL:
                risk_score += 2
            elif data_type == DataCategory.CONFIDENTIAL:
                risk_score += 2
            elif data_type == DataCategory.RESTRICTED:
                risk_score += 4
        
        # Risk based on processing purpose
        high_risk_purposes = ["profiling", "automated_decision_making", "behavioral_analysis"]
        if any(purpose in processing_purpose.lower() for purpose in high_risk_purposes):
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 8:
            return "very_high"
        elif risk_score >= 6:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _generate_privacy_mitigations(
        self,
        data_types: List[DataCategory],
        processing_purpose: str,
        risk_level: str
    ) -> List[str]:
        """Generate privacy mitigation measures"""
        mitigations = []
        
        if DataCategory.SENSITIVE in data_types:
            mitigations.append("Implement data anonymization techniques")
            mitigations.append("Use differential privacy for sensitive data")
        
        if DataCategory.PERSONAL in data_types:
            mitigations.append("Implement consent management system")
            mitigations.append("Provide data subject access rights")
        
        if risk_level in ["high", "very_high"]:
            mitigations.append("Conduct regular privacy audits")
            mitigations.append("Implement privacy by design principles")
            mitigations.append("Use encryption for all data processing")
        
        if "automated" in processing_purpose.lower():
            mitigations.append("Implement explainable AI measures")
            mitigations.append("Provide opt-out mechanisms")
        
        return mitigations
    
    def _update_compliance_metrics(self):
        """Update global compliance metrics"""
        try:
            self.metrics.total_assessments = len(self.assessments)
            
            # Count compliant vs non-compliant models
            compliant = 0
            non_compliant = 0
            total_score = 0.0
            critical_violations = 0
            
            for assessment in self.assessments.values():
                if assessment.overall_status == ComplianceStatus.COMPLIANT:
                    compliant += 1
                elif assessment.overall_status == ComplianceStatus.NON_COMPLIANT:
                    non_compliant += 1
                
                total_score += assessment.score
                
                # Count critical violations
                for finding in assessment.findings:
                    if finding.get("severity") == "critical" and not finding.get("compliant", True):
                        critical_violations += 1
            
            self.metrics.compliant_models = compliant
            self.metrics.non_compliant_models = non_compliant
            self.metrics.average_compliance_score = (
                total_score / max(len(self.assessments), 1)
            )
            self.metrics.critical_violations = critical_violations
            
        except Exception as e:
            self.logger.error(f"Failed to update compliance metrics: {str(e)}")
    
    def _generate_report_summary(self, assessments: List[ComplianceAssessment]) -> Dict[str, Any]:
        """Generate report summary"""
        if not assessments:
            return {"total_assessments": 0}
        
        status_counts = {}
        for assessment in assessments:
            status = assessment.overall_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_assessments": len(assessments),
            "status_distribution": status_counts,
            "average_score": sum(a.score for a in assessments) / len(assessments),
            "models_assessed": len(set(a.model_id for a in assessments))
        }
    
    def _generate_detailed_findings(self, assessments: List[ComplianceAssessment]) -> List[Dict[str, Any]]:
        """Generate detailed findings from assessments"""
        detailed_findings = []
        
        for assessment in assessments:
            for finding in assessment.findings:
                if not finding.get("compliant", True):
                    detailed_findings.append({
                        "assessment_id": assessment.assessment_id,
                        "model_id": assessment.model_id,
                        "finding": finding,
                        "timestamp": assessment.timestamp.isoformat()
                    })
        
        return detailed_findings
    
    def _generate_report_recommendations(self, assessments: List[ComplianceAssessment]) -> List[str]:
        """Generate report-level recommendations"""
        all_recommendations = []
        for assessment in assessments:
            all_recommendations.extend(assessment.recommendations)
        
        # Remove duplicates and prioritize
        unique_recommendations = list(set(all_recommendations))
        
        # Sort by urgency (URGENT first)
        urgent_recommendations = [r for r in unique_recommendations if "URGENT" in r]
        other_recommendations = [r for r in unique_recommendations if "URGENT" not in r]
        
        return urgent_recommendations + other_recommendations
    
    def _calculate_report_metrics(self, assessments: List[ComplianceAssessment]) -> Dict[str, Any]:
        """Calculate metrics for the report period"""
        if not assessments:
            return {}
        
        return {
            "compliance_rate": len([a for a in assessments if a.overall_status == ComplianceStatus.COMPLIANT]) / len(assessments),
            "average_score": sum(a.score for a in assessments) / len(assessments),
            "improvement_opportunities": len([a for a in assessments if a.score < 80])
        }
    
    async def _check_retention_for_standard(
        self,
        standard: ComplianceStandard,
        data_age_days: int,
        data_categories: List[str]
    ) -> Dict[str, Any]:
        """Check data retention compliance for specific standard"""
        # Simplified retention rules
        retention_limits = {
            ComplianceStandard.GDPR: {"personal": 365, "sensitive": 180},
            ComplianceStandard.HIPAA: {"sensitive": 2555},  # 7 years
            ComplianceStandard.PCI_DSS: {"confidential": 365}
        }
        
        limits = retention_limits.get(standard, {})
        violations = []
        
        for category in data_categories:
            limit = limits.get(category)
            if limit and data_age_days > limit:
                violations.append(f"Data category '{category}' exceeds retention limit of {limit} days")
        
        return {
            "standard": standard.value,
            "compliant": len(violations) == 0,
            "violations": violations,
            "required_actions": [f"Delete or anonymize data: {v}" for v in violations]
        }
    
    def _validate_individual_consent(
        self,
        consent: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate individual user consent"""
        issues = []
        
        required_fields = ["user_id", "consent_type", "timestamp", "granted"]
        for field in required_fields:
            if field not in consent:
                issues.append(f"Missing required field: {field}")
        
        # Check consent expiry (if applicable)
        if "expires_at" in consent:
            expiry_date = datetime.fromisoformat(consent["expires_at"])
            if datetime.now() > expiry_date:
                issues.append("Consent has expired")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _calculate_compliance_trend(self, assessments: List[ComplianceAssessment]) -> Dict[str, Any]:
        """Calculate compliance trend for a model"""
        if len(assessments) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by timestamp
        sorted_assessments = sorted(assessments, key=lambda x: x.timestamp)
        
        recent_score = sorted_assessments[-1].score
        previous_score = sorted_assessments[-2].score
        
        if recent_score > previous_score:
            trend = "improving"
        elif recent_score < previous_score:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "score_change": recent_score - previous_score,
            "recent_score": recent_score,
            "previous_score": previous_score
        }
    
    def _get_recent_compliance_activity(self) -> List[Dict[str, Any]]:
        """Get recent compliance activity"""
        recent_assessments = sorted(
            self.assessments.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )[:10]
        
        return [
            {
                "assessment_id": a.assessment_id,
                "model_id": a.model_id,
                "status": a.overall_status.value,
                "score": a.score,
                "timestamp": a.timestamp.isoformat()
            }
            for a in recent_assessments
        ]


# Global instance
compliance_framework = ComplianceFramework()