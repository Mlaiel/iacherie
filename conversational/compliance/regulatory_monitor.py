"""Regulatory Monitor - Advanced Regulatory Compliance Monitoring System

This module provides comprehensive regulatory compliance monitoring for conversational AI,
including real-time regulatory updates, compliance requirement tracking, and policy change notifications.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum

from ..core.database import DatabaseManager
from ..core.cache import CacheManager
from ..integrations.regulatory_apis import RegulatoryAPIClient


class RegulatoryFramework(Enum):
    """Major regulatory frameworks"""    GDPR = "gdpr"
    CCPA = "ccpa"
    COPPA = "coppa"
    AI_ACT_EU = "ai_act_eu"
    DIGITAL_SERVICES_ACT = "digital_services_act"
    ONLINE_SAFETY_ACT_UK = "online_safety_act_uk"
    FTC_ACT = "ftc_act"
    PIPL_CHINA = "pipl_china"
    LGPD_BRAZIL = "lgpd_brazil"
    PIPEDA_CANADA = "pipeda_canada"


class ComplianceStatus(Enum):
    """Compliance status levels"""    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    UNDER_REVIEW = "under_review"
    NOT_APPLICABLE = "not_applicable"


class RegulatoryRequirementType(Enum):
    """Types of regulatory requirements"""    DATA_PROTECTION = "data_protection"
    CONTENT_MODERATION = "content_moderation"
    TRANSPARENCY = "transparency"
    ALGORITHMIC_ACCOUNTABILITY = "algorithmic_accountability"
    RISK_ASSESSMENT = "risk_assessment"
    AUDIT_REQUIREMENTS = "audit_requirements"
    NOTIFICATION_OBLIGATIONS = "notification_obligations"
    USER_RIGHTS = "user_rights"


class Jurisdiction(Enum):
    """Regulatory jurisdictions"""    EU = "eu"
    US = "us"
    UK = "uk"
    CANADA = "canada"
    AUSTRALIA = "australia"
    GERMANY = "germany"
    FRANCE = "france"
    CALIFORNIA = "california"
    CHINA = "china"
    BRAZIL = "brazil"
    GLOBAL = "global"


@dataclass
class RegulatoryRequirement:
    """Regulatory requirement structure"""    requirement_id: str
    framework: RegulatoryFramework
    jurisdiction: Jurisdiction
    requirement_type: RegulatoryRequirementType
    title: str
    description: str
    compliance_criteria: List[str]
    assessment_methods: List[str]
    penalties: Dict[str, Any]
    effective_date: datetime
    review_frequency: int  # days
    last_updated: datetime
    source_reference: str


@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""    requirement_id: str
    status: ComplianceStatus
    compliance_score: float
    findings: List[str]
    evidence: List[str]
    gaps: List[str]
    remediation_actions: List[str]
    next_review_date: datetime
    assessor: str
    assessment_date: datetime


@dataclass
class RegulatoryUpdate:
    """Regulatory update notification"""    update_id: str
    framework: RegulatoryFramework
    jurisdiction: Jurisdiction
    update_type: str
    title: str
    description: str
    impact_level: str
    effective_date: datetime
    action_required: bool
    deadline: Optional[datetime]
    source_url: str


@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""    report_id: str
    reporting_period: Tuple[datetime, datetime]
    overall_compliance_score: float
    framework_compliance: Dict[RegulatoryFramework, ComplianceStatus]
    requirements_assessed: List[ComplianceAssessment]
    identified_risks: List[Dict[str, Any]]
    remediation_plan: List[Dict[str, Any]]
    next_assessment_date: datetime
    generated_by: str
    generated_at: datetime


class RegulatoryMonitor:
    """    Advanced regulatory compliance monitoring system.
    
    Provides comprehensive regulatory compliance monitoring including real-time updates,
    requirement tracking, automated assessments, and compliance reporting.
    """    
    def __init__(
        self,
        db_manager: DatabaseManager,
        cache_manager: CacheManager,
        regulatory_api_client: Optional[RegulatoryAPIClient] = None
    ):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.regulatory_api_client = regulatory_api_client or RegulatoryAPIClient()
        self.logger = logging.getLogger(__name__)
        
        # Regulatory configuration
        self.monitored_frameworks = self._load_monitored_frameworks()
        self.compliance_requirements = {}
        self.assessment_schedule = {}
        
        # Compliance tracking
        self.active_assessments = {}
        self.compliance_cache = {}
        
        # Initialize regulatory data
        asyncio.create_task(self._initialize_regulatory_data())
        
        self.logger.info("RegulatoryMonitor initialized with compliance monitoring systems")
    
    def _load_monitored_frameworks(self) -> Dict[Jurisdiction, List[RegulatoryFramework]]:
        """Load monitored regulatory frameworks by jurisdiction"""        return {
            Jurisdiction.EU: [
                RegulatoryFramework.GDPR,
                RegulatoryFramework.AI_ACT_EU,
                RegulatoryFramework.DIGITAL_SERVICES_ACT
            ],
            Jurisdiction.US: [
                RegulatoryFramework.CCPA,
                RegulatoryFramework.COPPA,
                RegulatoryFramework.FTC_ACT
            ],
            Jurisdiction.UK: [
                RegulatoryFramework.GDPR,  # UK GDPR
                RegulatoryFramework.ONLINE_SAFETY_ACT_UK
            ],
            Jurisdiction.CANADA: [
                RegulatoryFramework.PIPEDA_CANADA
            ],
            Jurisdiction.CHINA: [
                RegulatoryFramework.PIPL_CHINA
            ],
            Jurisdiction.BRAZIL: [
                RegulatoryFramework.LGPD_BRAZIL
            ],
            Jurisdiction.CALIFORNIA: [
                RegulatoryFramework.CCPA
            ]
        }
    
    async def _initialize_regulatory_data(self) -> None:
        """Initialize regulatory requirements and assessment data"""        try:
            # Load regulatory requirements from database
            requirements_data = await self.db_manager.fetch_all(
                "SELECT * FROM regulatory_requirements WHERE active = true"
            )
            
            for req_data in requirements_data:
                requirement = RegulatoryRequirement(
                    requirement_id=req_data["requirement_id"],
                    framework=RegulatoryFramework(req_data["framework"]),
                    jurisdiction=Jurisdiction(req_data["jurisdiction"]),
                    requirement_type=RegulatoryRequirementType(req_data["requirement_type"]),
                    title=req_data["title"],
                    description=req_data["description"],
                    compliance_criteria=req_data["compliance_criteria"],
                    assessment_methods=req_data["assessment_methods"],
                    penalties=req_data["penalties"],
                    effective_date=req_data["effective_date"],
                    review_frequency=req_data["review_frequency"],
                    last_updated=req_data["last_updated"],
                    source_reference=req_data["source_reference"]
                )
                
                self.compliance_requirements[req_data["requirement_id"]] = requirement
            
            # Load assessment schedule
            await self._load_assessment_schedule()
            
            self.logger.info(f"Initialized {len(self.compliance_requirements)} regulatory requirements")
            
        except Exception as e:
            self.logger.error(f"Error initializing regulatory data: {str(e)}")
    
    async def _load_assessment_schedule(self) -> None:
        """Load compliance assessment schedule"""        try:
            schedule_data = await self.db_manager.fetch_all(
                """                SELECT requirement_id, next_assessment_date, frequency_days
                FROM compliance_assessment_schedule
                WHERE next_assessment_date >= $1
                """,
                datetime.now()
            )
            
            for schedule_item in schedule_data:
                self.assessment_schedule[schedule_item["requirement_id"]] = {
                    "next_assessment": schedule_item["next_assessment_date"],
                    "frequency": schedule_item["frequency_days"]
                }
                
        except Exception as e:
            self.logger.error(f"Error loading assessment schedule: {str(e)}")
    
    async def validate_regulatory_compliance(
        self,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """        Validate regulatory compliance for conversational interactions.
        
        Args:
            conversation_data: Full conversation context
            user_input: User's input text
            ai_response: AI's generated response
            
        Returns:
            Dict containing regulatory compliance assessment
        """        try:
            self.logger.debug("Starting regulatory compliance validation")
            
            # Determine applicable jurisdictions
            applicable_jurisdictions = self._determine_applicable_jurisdictions(conversation_data)
            
            # Get applicable regulatory frameworks
            applicable_frameworks = []
            for jurisdiction in applicable_jurisdictions:
                frameworks = self.monitored_frameworks.get(jurisdiction, [])
                applicable_frameworks.extend(frameworks)
            
            # Remove duplicates
            applicable_frameworks = list(set(applicable_frameworks))
            
            # Perform compliance checks for each framework
            compliance_results = {}
            overall_compliant = True
            
            for framework in applicable_frameworks:
                framework_result = await self._assess_framework_compliance(
                    framework, conversation_data, user_input, ai_response
                )
                compliance_results[framework.value] = framework_result
                
                if not framework_result.get("compliant", True):
                    overall_compliant = False
            
            # Generate recommendations
            recommendations = self._generate_regulatory_recommendations(compliance_results)
            
            # Check for pending regulatory updates
            pending_updates = await self._check_pending_updates(applicable_frameworks)
            
            return {
                "compliant": overall_compliant,
                "applicable_jurisdictions": [j.value for j in applicable_jurisdictions],
                "framework_compliance": compliance_results,
                "recommendations": recommendations,
                "pending_updates": pending_updates,
                "assessment_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in regulatory compliance validation: {str(e)}")
            return {
                "compliant": False,
                "error": str(e),
                "recommendations": ["Manual regulatory review required due to validation error"]
            }
    
    def _determine_applicable_jurisdictions(self, conversation_data: Dict[str, Any]) -> List[Jurisdiction]:
        """Determine applicable jurisdictions based on conversation context"""        jurisdictions = []
        
        # Check user location
        user_location = conversation_data.get("user_location", {})
        user_country = user_location.get("country", "").upper()
        
        # Map countries to jurisdictions
        country_jurisdiction_map = {
            "US": Jurisdiction.US,
            "CA": Jurisdiction.CANADA,
            "UK": Jurisdiction.UK,
            "GB": Jurisdiction.UK,
            "DE": Jurisdiction.GERMANY,
            "FR": Jurisdiction.FRANCE,
            "AU": Jurisdiction.AUSTRALIA,
            "CN": Jurisdiction.CHINA,
            "BR": Jurisdiction.BRAZIL
        }
        
        # EU countries
        eu_countries = {
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE",
            "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT",
            "RO", "SK", "SI", "ES", "SE"
        }
        
        if user_country in eu_countries:
            jurisdictions.append(Jurisdiction.EU)
            if user_country in country_jurisdiction_map:
                jurisdictions.append(country_jurisdiction_map[user_country])
        elif user_country in country_jurisdiction_map:
            jurisdictions.append(country_jurisdiction_map[user_country])
        
        # Check for California-specific rules
        user_state = user_location.get("state", "").upper()
        if user_country == "US" and user_state == "CA":
            jurisdictions.append(Jurisdiction.CALIFORNIA)
        
        # Default to US if no specific jurisdiction determined
        if not jurisdictions:
            jurisdictions.append(Jurisdiction.US)
        
        return jurisdictions
    
    async def _assess_framework_compliance(
        self,
        framework: RegulatoryFramework,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Assess compliance with specific regulatory framework"""        try:
            framework_requirements = [
                req for req in self.compliance_requirements.values()
                if req.framework == framework
            ]
            
            compliance_checks = []
            violations = []
            warnings = []
            
            for requirement in framework_requirements:
                check_result = await self._check_requirement_compliance(
                    requirement, conversation_data, user_input, ai_response
                )
                compliance_checks.append(check_result)
                
                if not check_result["compliant"]:
                    violations.append({
                        "requirement_id": requirement.requirement_id,
                        "title": requirement.title,
                        "description": check_result.get("violation_description", ""),
                        "severity": check_result.get("severity", "medium")
                    })
                
                if check_result.get("warnings"):
                    warnings.extend(check_result["warnings"])
            
            # Calculate overall compliance score
            total_checks = len(compliance_checks)
            compliant_checks = sum(1 for check in compliance_checks if check["compliant"])
            compliance_score = compliant_checks / total_checks if total_checks > 0 else 1.0
            
            return {
                "framework": framework.value,
                "compliant": compliance_score >= 0.8,  # 80% threshold
                "compliance_score": compliance_score,
                "violations": violations,
                "warnings": warnings,
                "requirements_checked": total_checks,
                "compliant_requirements": compliant_checks
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing {framework.value} compliance: {str(e)}")
            return {
                "framework": framework.value,
                "compliant": False,
                "error": str(e)
            }
    
    async def _check_requirement_compliance(
        self,
        requirement: RegulatoryRequirement,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Check compliance with specific regulatory requirement"""        try:
            # Implement specific compliance checks based on requirement type
            if requirement.requirement_type == RegulatoryRequirementType.DATA_PROTECTION:
                return await self._check_data_protection_compliance(
                    requirement, conversation_data, user_input, ai_response
                )
            
            elif requirement.requirement_type == RegulatoryRequirementType.CONTENT_MODERATION:
                return await self._check_content_moderation_compliance(
                    requirement, conversation_data, user_input, ai_response
                )
            
            elif requirement.requirement_type == RegulatoryRequirementType.TRANSPARENCY:
                return await self._check_transparency_compliance(
                    requirement, conversation_data, user_input, ai_response
                )
            
            elif requirement.requirement_type == RegulatoryRequirementType.ALGORITHMIC_ACCOUNTABILITY:
                return await self._check_algorithmic_accountability_compliance(
                    requirement, conversation_data, user_input, ai_response
                )
            
            elif requirement.requirement_type == RegulatoryRequirementType.USER_RIGHTS:
                return await self._check_user_rights_compliance(
                    requirement, conversation_data, user_input, ai_response
                )
            
            else:
                # Generic compliance check
                return await self._check_generic_compliance(
                    requirement, conversation_data, user_input, ai_response
                )
                
        except Exception as e:
            self.logger.error(f"Error checking requirement {requirement.requirement_id}: {str(e)}")
            return {
                "compliant": False,
                "error": str(e),
                "requirement_id": requirement.requirement_id
            }
    
    async def _check_data_protection_compliance(
        self,
        requirement: RegulatoryRequirement,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Check data protection compliance (GDPR, CCPA, etc.)"""        # Check for personal data processing
        has_personal_data = conversation_data.get("has_personal_data", False)
        user_consent = conversation_data.get("user_consent", {})
        
        violations = []
        warnings = []
        
        if has_personal_data:
            # Check consent requirements
            if requirement.framework == RegulatoryFramework.GDPR:
                required_consents = ["data_processing", "analytics"]
                for consent_type in required_consents:
                    if not user_consent.get(consent_type, False):
                        violations.append(f"Missing consent for {consent_type}")
            
            # Check data minimization
            if len(user_input + ai_response) > 1000:  # Arbitrary threshold
                warnings.append("Consider data minimization principles")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "requirement_id": requirement.requirement_id
        }
    
    async def _check_content_moderation_compliance(
        self,
        requirement: RegulatoryRequirement,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Check content moderation compliance (DSA, Online Safety Act, etc.)"""        content_safety_score = conversation_data.get("content_safety_score", 1.0)
        content_violations = conversation_data.get("content_violations", [])
        
        violations = []
        warnings = []
        
        # Check content safety thresholds
        if requirement.framework == RegulatoryFramework.DIGITAL_SERVICES_ACT:
            if content_safety_score < 0.7:
                violations.append("Content safety score below DSA requirements")
            
            if content_violations:
                violations.append(f"Content violations detected: {len(content_violations)}")
        
        elif requirement.framework == RegulatoryFramework.ONLINE_SAFETY_ACT_UK:
            illegal_content_categories = ["terrorism", "child_abuse", "hate_speech"]
            for violation in content_violations:
                if violation.get("category") in illegal_content_categories:
                    violations.append(f"Illegal content detected: {violation.get('category')}")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "requirement_id": requirement.requirement_id
        }
    
    async def _check_transparency_compliance(
        self,
        requirement: RegulatoryRequirement,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Check transparency compliance (AI Act, FTC requirements, etc.)"""        ai_disclosure_provided = conversation_data.get("ai_disclosure_provided", False)
        algorithmic_explanation = conversation_data.get("algorithmic_explanation", False)
        
        violations = []
        warnings = []
        
        if requirement.framework == RegulatoryFramework.AI_ACT_EU:
            # Check AI system disclosure
            if not ai_disclosure_provided:
                violations.append("AI system disclosure not provided to user")
            
            # Check for high-risk AI system requirements
            if conversation_data.get("ai_risk_level") == "high":
                if not algorithmic_explanation:
                    violations.append("Algorithmic explanation required for high-risk AI system")
        
        elif requirement.framework == RegulatoryFramework.FTC_ACT:
            # Check for deceptive practices
            if "human" in ai_response.lower() and not ai_disclosure_provided:
                warnings.append("Consider adding AI disclosure to prevent deception")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "requirement_id": requirement.requirement_id
        }
    
    async def _check_algorithmic_accountability_compliance(
        self,
        requirement: RegulatoryRequirement,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Check algorithmic accountability compliance"""        bias_assessment_conducted = conversation_data.get("bias_assessment_conducted", False)
        fairness_metrics_available = conversation_data.get("fairness_metrics_available", False)
        
        violations = []
        warnings = []
        
        if requirement.framework == RegulatoryFramework.AI_ACT_EU:
            if not bias_assessment_conducted:
                warnings.append("Regular bias assessment recommended")
            
            if not fairness_metrics_available:
                warnings.append("Fairness metrics should be available for algorithmic accountability")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "requirement_id": requirement.requirement_id
        }
    
    async def _check_user_rights_compliance(
        self,
        requirement: RegulatoryRequirement,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Check user rights compliance"""        user_rights_info_provided = conversation_data.get("user_rights_info_provided", False)
        data_subject_request_mechanism = conversation_data.get("data_subject_request_mechanism", False)
        
        violations = []
        warnings = []
        
        if requirement.framework in [RegulatoryFramework.GDPR, RegulatoryFramework.CCPA]:
            if not user_rights_info_provided:
                warnings.append("User rights information should be easily accessible")
            
            if not data_subject_request_mechanism:
                violations.append("Data subject request mechanism not available")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "requirement_id": requirement.requirement_id
        }
    
    async def _check_generic_compliance(
        self,
        requirement: RegulatoryRequirement,
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Generic compliance check for unspecified requirement types"""        # Basic compliance check - assume compliant unless specific violations found
        return {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "requirement_id": requirement.requirement_id,
            "note": "Generic compliance check - manual review may be required"
        }
    
    def _generate_regulatory_recommendations(
        self,
        compliance_results: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate regulatory compliance recommendations"""        recommendations = []
        
        for framework, result in compliance_results.items():
            if not result.get("compliant", True):
                recommendations.append(f"Address {framework} compliance violations")
                
                violations = result.get("violations", [])
                for violation in violations:
                    recommendations.append(f"- {violation.get('title', 'Unknown')}")
            
            warnings = result.get("warnings", [])
            for warning in warnings:
                recommendations.append(f"Consider: {warning}")
        
        if not recommendations:
            recommendations.append("Continue monitoring for regulatory updates")
        
        return recommendations
    
    async def _check_pending_updates(
        self,
        frameworks: List[RegulatoryFramework]
    ) -> List[Dict[str, Any]]:
        """Check for pending regulatory updates"""        pending_updates = []
        
        try:
            # Query recent regulatory updates
            updates_query = """                SELECT * FROM regulatory_updates 
                WHERE framework = ANY($1) 
                AND effective_date > $2 
                AND action_required = true
                ORDER BY effective_date ASC
            """            
            framework_values = [f.value for f in frameworks]
            updates_data = await self.db_manager.fetch_all(
                updates_query,
                framework_values,
                datetime.now()
            )
            
            for update_data in updates_data:
                pending_updates.append({
                    "update_id": update_data["update_id"],
                    "framework": update_data["framework"],
                    "title": update_data["title"],
                    "effective_date": update_data["effective_date"].isoformat(),
                    "action_required": update_data["action_required"],
                    "deadline": update_data["deadline"].isoformat() if update_data["deadline"] else None
                })
                
        except Exception as e:
            self.logger.error(f"Error checking pending updates: {str(e)}")
        
        return pending_updates
    
    async def conduct_compliance_assessment(
        self,
        requirement_id: str,
        assessor: str
    ) -> ComplianceAssessment:
        """Conduct comprehensive compliance assessment for specific requirement"""        try:
            requirement = self.compliance_requirements.get(requirement_id)
            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")
            
            # Gather evidence and conduct assessment
            evidence = await self._gather_compliance_evidence(requirement)
            assessment_result = await self._perform_assessment(requirement, evidence)
            
            # Create assessment record
            assessment = ComplianceAssessment(
                requirement_id=requirement_id,
                status=assessment_result["status"],
                compliance_score=assessment_result["score"],
                findings=assessment_result["findings"],
                evidence=evidence,
                gaps=assessment_result["gaps"],
                remediation_actions=assessment_result["remediation_actions"],
                next_review_date=datetime.now() + timedelta(days=requirement.review_frequency),
                assessor=assessor,
                assessment_date=datetime.now()
            )
            
            # Store assessment
            await self._store_compliance_assessment(assessment)
            
            # Update assessment schedule
            await self._update_assessment_schedule(requirement_id, assessment.next_review_date)
            
            self.logger.info(f"Compliance assessment completed for {requirement_id}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error conducting compliance assessment: {str(e)}")
            raise
    
    async def _gather_compliance_evidence(self, requirement: RegulatoryRequirement) -> List[str]:
        """Gather evidence for compliance assessment"""        evidence = []
        
        try:
            # Query relevant system data based on requirement type
            if requirement.requirement_type == RegulatoryRequirementType.DATA_PROTECTION:
                # Gather data protection evidence
                consent_data = await self.db_manager.fetch_all(
                    "SELECT COUNT(*) as consent_count FROM user_consents WHERE status = 'granted'"
                )
                evidence.append(f"Active user consents: {consent_data[0]['consent_count']}")
                
            elif requirement.requirement_type == RegulatoryRequirementType.CONTENT_MODERATION:
                # Gather content moderation evidence
                moderation_data = await self.db_manager.fetch_all(
                    """                    SELECT COUNT(*) as total_assessments, 
                           AVG(safety_score) as avg_safety_score
                    FROM content_safety_assessments 
                    WHERE created_at >= $1
                    """,
                    datetime.now() - timedelta(days=30)
                )
                evidence.append(f"Content assessments (30d): {moderation_data[0]['total_assessments']}")
                evidence.append(f"Average safety score: {moderation_data[0]['avg_safety_score']:.2f}")
            
            # Add configuration evidence
            evidence.append(f"System configuration documented: {datetime.now().isoformat()}")
            
        except Exception as e:
            self.logger.error(f"Error gathering evidence: {str(e)}")
            evidence.append(f"Evidence gathering error: {str(e)}")
        
        return evidence
    
    async def _perform_assessment(
        self,
        requirement: RegulatoryRequirement,
        evidence: List[str]
    ) -> Dict[str, Any]:
        """Perform compliance assessment based on evidence"""        findings = []
        gaps = []
        remediation_actions = []
        
        # Evaluate evidence against compliance criteria
        compliance_score = 0.0
        total_criteria = len(requirement.compliance_criteria)
        
        for criterion in requirement.compliance_criteria:
            # Simple keyword matching for evidence evaluation
            criterion_met = any(keyword in " ".join(evidence).lower() 
                              for keyword in criterion.lower().split())
            
            if criterion_met:
                compliance_score += 1.0
                findings.append(f"Criterion met: {criterion}")
            else:
                gaps.append(f"Gap identified: {criterion}")
                remediation_actions.append(f"Address: {criterion}")
        
        # Normalize score
        compliance_score = compliance_score / total_criteria if total_criteria > 0 else 1.0
        
        # Determine status
        if compliance_score >= 0.9:
            status = ComplianceStatus.COMPLIANT
        elif compliance_score >= 0.7:
            status = ComplianceStatus.PARTIAL_COMPLIANCE
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        return {
            "status": status,
            "score": compliance_score,
            "findings": findings,
            "gaps": gaps,
            "remediation_actions": remediation_actions
        }
    
    async def _store_compliance_assessment(self, assessment: ComplianceAssessment) -> None:
        """Store compliance assessment results"""        try:
            query = """                INSERT INTO compliance_assessments 
                (requirement_id, status, compliance_score, findings, evidence,
                 gaps, remediation_actions, next_review_date, assessor, assessment_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """            
            await self.db_manager.execute(
                query,
                assessment.requirement_id,
                assessment.status.value,
                assessment.compliance_score,
                assessment.findings,
                assessment.evidence,
                assessment.gaps,
                assessment.remediation_actions,
                assessment.next_review_date,
                assessment.assessor,
                assessment.assessment_date
            )
            
        except Exception as e:
            self.logger.error(f"Error storing compliance assessment: {str(e)}")
    
    async def _update_assessment_schedule(
        self,
        requirement_id: str,
        next_review_date: datetime
    ) -> None:
        """Update compliance assessment schedule"""        try:
            await self.db_manager.execute(
                """                UPDATE compliance_assessment_schedule 
                SET next_assessment_date = $1, last_updated = $2
                WHERE requirement_id = $3
                """,
                next_review_date,
                datetime.now(),
                requirement_id
            )
            
            # Update internal schedule
            if requirement_id in self.assessment_schedule:
                self.assessment_schedule[requirement_id]["next_assessment"] = next_review_date
                
        except Exception as e:
            self.logger.error(f"Error updating assessment schedule: {str(e)}")
    
    async def generate_compliance_report(
        self,
        reporting_period: Tuple[datetime, datetime],
        generated_by: str
    ) -> ComplianceReport:
        """Generate comprehensive compliance report"""        try:
            start_date, end_date = reporting_period
            
            # Gather assessments for reporting period
            assessments_data = await self.db_manager.fetch_all(
                """                SELECT * FROM compliance_assessments 
                WHERE assessment_date BETWEEN $1 AND $2
                ORDER BY assessment_date DESC
                """,
                start_date,
                end_date
            )
            
            # Convert to assessment objects
            assessments = []
            framework_compliance = {}
            total_score = 0.0
            
            for assess_data in assessments_data:
                requirement = self.compliance_requirements.get(assess_data["requirement_id"])
                if requirement:
                    assessment = ComplianceAssessment(
                        requirement_id=assess_data["requirement_id"],
                        status=ComplianceStatus(assess_data["status"]),
                        compliance_score=assess_data["compliance_score"],
                        findings=assess_data["findings"],
                        evidence=assess_data["evidence"],
                        gaps=assess_data["gaps"],
                        remediation_actions=assess_data["remediation_actions"],
                        next_review_date=assess_data["next_review_date"],
                        assessor=assess_data["assessor"],
                        assessment_date=assess_data["assessment_date"]
                    )
                    
                    assessments.append(assessment)
                    total_score += assessment.compliance_score
                    
                    # Track framework compliance
                    framework = requirement.framework
                    if framework not in framework_compliance:
                        framework_compliance[framework] = []
                    framework_compliance[framework].append(assessment.status)
            
            # Calculate overall compliance score
            overall_score = total_score / len(assessments) if assessments else 1.0
            
            # Determine framework compliance status
            for framework, statuses in framework_compliance.items():
                if all(status == ComplianceStatus.COMPLIANT for status in statuses):
                    framework_compliance[framework] = ComplianceStatus.COMPLIANT
                elif any(status == ComplianceStatus.NON_COMPLIANT for status in statuses):
                    framework_compliance[framework] = ComplianceStatus.NON_COMPLIANT
                else:
                    framework_compliance[framework] = ComplianceStatus.PARTIAL_COMPLIANCE
            
            # Identify risks and create remediation plan
            identified_risks = []
            remediation_plan = []
            
            for assessment in assessments:
                if assessment.status == ComplianceStatus.NON_COMPLIANT:
                    identified_risks.append({
                        "requirement_id": assessment.requirement_id,
                        "risk_level": "high",
                        "description": f"Non-compliant with {assessment.requirement_id}"
                    })
                    
                    for action in assessment.remediation_actions:
                        remediation_plan.append({
                            "action": action,
                            "priority": "high",
                            "deadline": assessment.next_review_date
                        })
            
            # Create report
            report = ComplianceReport(
                report_id=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                reporting_period=reporting_period,
                overall_compliance_score=overall_score,
                framework_compliance=framework_compliance,
                requirements_assessed=assessments,
                identified_risks=identified_risks,
                remediation_plan=remediation_plan,
                next_assessment_date=min(assess.next_review_date for assess in assessments) if assessments else datetime.now() + timedelta(days=90),
                generated_by=generated_by,
                generated_at=datetime.now()
            )
            
            # Store report
            await self._store_compliance_report(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {str(e)}")
            raise
    
    async def _store_compliance_report(self, report: ComplianceReport) -> None:
        """Store compliance report"""        try:
            query = """                INSERT INTO compliance_reports 
                (report_id, reporting_period_start, reporting_period_end, 
                 overall_compliance_score, framework_compliance, requirements_count,
                 risks_count, generated_by, generated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """            
            await self.db_manager.execute(
                query,
                report.report_id,
                report.reporting_period[0],
                report.reporting_period[1],
                report.overall_compliance_score,
                {k.value: v.value for k, v in report.framework_compliance.items()},
                len(report.requirements_assessed),
                len(report.identified_risks),
                report.generated_by,
                report.generated_at
            )
            
        except Exception as e:
            self.logger.error(f"Error storing compliance report: {str(e)}")
    
    async def add_regulatory_requirement(self, requirement: RegulatoryRequirement) -> None:
        """Add new regulatory requirement"""        try:
            query = """                INSERT INTO regulatory_requirements 
                (requirement_id, framework, jurisdiction, requirement_type, title,
                 description, compliance_criteria, assessment_methods, penalties,
                 effective_date, review_frequency, source_reference, active)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """            
            await self.db_manager.execute(
                query,
                requirement.requirement_id,
                requirement.framework.value,
                requirement.jurisdiction.value,
                requirement.requirement_type.value,
                requirement.title,
                requirement.description,
                requirement.compliance_criteria,
                requirement.assessment_methods,
                requirement.penalties,
                requirement.effective_date,
                requirement.review_frequency,
                requirement.source_reference,
                True
            )
            
            # Add to internal tracking
            self.compliance_requirements[requirement.requirement_id] = requirement
            
            # Schedule assessment
            next_assessment = datetime.now() + timedelta(days=30)  # Initial assessment in 30 days
            await self._schedule_assessment(requirement.requirement_id, next_assessment)
            
            self.logger.info(f"Added regulatory requirement: {requirement.requirement_id}")
            
        except Exception as e:
            self.logger.error(f"Error adding regulatory requirement: {str(e)}")
    
    async def _schedule_assessment(
        self,
        requirement_id: str,
        assessment_date: datetime
    ) -> None:
        """Schedule compliance assessment"""        try:
            await self.db_manager.execute(
                """                INSERT INTO compliance_assessment_schedule 
                (requirement_id, next_assessment_date, frequency_days, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (requirement_id) DO UPDATE SET
                next_assessment_date = $2, frequency_days = $3, updated_at = $4
                """,
                requirement_id,
                assessment_date,
                30,  # Default frequency
                datetime.now()
            )
            
            # Update internal schedule
            self.assessment_schedule[requirement_id] = {
                "next_assessment": assessment_date,
                "frequency": 30
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling assessment: {str(e)}")
    
    async def get_compliance_dashboard_data(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""        try:
            # Overall compliance metrics
            recent_assessments = await self.db_manager.fetch_all(
                """                SELECT status, COUNT(*) as count, AVG(compliance_score) as avg_score
                FROM compliance_assessments 
                WHERE assessment_date >= $1
                GROUP BY status
                """,
                datetime.now() - timedelta(days=30)
            )
            
            # Framework compliance distribution
            framework_stats = {}
            for framework in RegulatoryFramework:
                framework_requirements = [
                    req for req in self.compliance_requirements.values()
                    if req.framework == framework
                ]
                framework_stats[framework.value] = len(framework_requirements)
            
            # Upcoming assessments
            upcoming_assessments = []
            for req_id, schedule in self.assessment_schedule.items():
                if schedule["next_assessment"] <= datetime.now() + timedelta(days=7):
                    upcoming_assessments.append({
                        "requirement_id": req_id,
                        "next_assessment": schedule["next_assessment"].isoformat(),
                        "overdue": schedule["next_assessment"] < datetime.now()
                    })
            
            return {
                "recent_assessments": {
                    stat["status"]: {
                        "count": stat["count"],
                        "avg_score": stat["avg_score"]
                    }
                    for stat in recent_assessments
                },
                "framework_distribution": framework_stats,
                "upcoming_assessments": upcoming_assessments,
                "total_requirements": len(self.compliance_requirements),
                "monitored_frameworks": len(set(req.framework for req in self.compliance_requirements.values())),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {str(e)}")
            return {}
    
    def get_supported_frameworks(self) -> List[str]:
        """Get list of supported regulatory frameworks"""        return [framework.value for framework in RegulatoryFramework]
    
    def get_monitored_jurisdictions(self) -> List[str]:
        """Get list of monitored jurisdictions"""        return [jurisdiction.value for jurisdiction in self.monitored_frameworks.keys()]
