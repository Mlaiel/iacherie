"""Privacy by Design Framework

Implements privacy by design principles across all new features
and system developments with automated compliance checks.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class PrivacyPrinciple(Enum):
    """Privacy by Design Principles"""
    PROACTIVE_NOT_REACTIVE = "proactive_not_reactive"
    PRIVACY_AS_DEFAULT = "privacy_as_default"
    FULL_FUNCTIONALITY = "full_functionality"
    END_TO_END_SECURITY = "end_to_end_security"
    VISIBILITY_TRANSPARENCY = "visibility_transparency"
    RESPECT_USER_PRIVACY = "respect_user_privacy"
    PRIVACY_EMBEDDED_INTO_DESIGN = "privacy_embedded_into_design"


class DataProcessingCategory(Enum):
    """Categories of data processing"""
    COLLECTION = "collection"
    STORAGE = "storage"
    PROCESSING = "processing"
    SHARING = "sharing"
    RETENTION = "retention"
    DELETION = "deletion"
    ANALYTICS = "analytics"
    PROFILING = "profiling"


class PrivacyImpactLevel(Enum):
    """Privacy impact levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class PrivacyControl:
    """Individual privacy control measure"""
    control_id: str
    name: str
    description: str
    principle: PrivacyPrinciple
    category: DataProcessingCategory
    implementation_status: str = "not_implemented"  # not_implemented, partial, implemented, verified
    technical_implementation: Optional[str] = None
    policy_implementation: Optional[str] = None
    effectiveness_score: float = 0.0
    last_assessed: Optional[datetime] = None
    required_for_compliance: bool = True


@dataclass
class FeaturePrivacyAssessment:
    """Privacy assessment for a new feature"""
    assessment_id: str
    feature_name: str
    feature_description: str
    impact_level: PrivacyImpactLevel
    data_categories: List[str] = field(default_factory=list)
    processing_purposes: List[str] = field(default_factory=list)
    legal_basis: List[str] = field(default_factory=list)
    privacy_controls: List[PrivacyControl] = field(default_factory=list)
    residual_risks: List[str] = field(default_factory=list)
    mitigation_measures: List[str] = field(default_factory=list)
    approval_status: str = "pending"  # pending, approved, rejected, conditional
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class PrivacyByDesignFramework:
    """
    Privacy by Design Framework
    
    Implements automated privacy controls and assessments for all
    new features and system changes to ensure privacy compliance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.privacy_controls: Dict[str, PrivacyControl] = {}
        self.feature_assessments: Dict[str, FeaturePrivacyAssessment] = {}
        
        # Initialize default privacy controls
        self._initialize_privacy_controls()
        
        # Audit trail
        self.audit_log: List[Dict[str, Any]] = []
        
        # Metrics
        self.metrics = {
            "total_assessments": 0,
            "approved_features": 0,
            "privacy_controls_implemented": 0,
            "average_assessment_time": 0.0,
            "compliance_score": 100.0
        }
    
    def _initialize_privacy_controls(self):
        """Initialize default privacy controls based on privacy principles"""
        
        # Proactive controls
        proactive_controls = [
            PrivacyControl(
                control_id="pbdd_data_minimization",
                name="Data Minimization",
                description="Collect and process only data necessary for specified purposes",
                principle=PrivacyPrinciple.PROACTIVE_NOT_REACTIVE,
                category=DataProcessingCategory.COLLECTION,
                technical_implementation="Automated field validation and purpose-based collection",
                required_for_compliance=True
            ),
            PrivacyControl(
                control_id="pbdd_purpose_limitation",
                name="Purpose Limitation",
                description="Use data only for explicitly stated purposes",
                principle=PrivacyPrinciple.PROACTIVE_NOT_REACTIVE,
                category=DataProcessingCategory.PROCESSING,
                technical_implementation="Purpose-based access controls and processing flags",
                required_for_compliance=True
            )
        ]
        
        # Privacy as default controls
        default_controls = [
            PrivacyControl(
                control_id="pbdd_default_privacy_settings",
                name="Default Privacy Settings",
                description="Set most privacy-protective settings as default",
                principle=PrivacyPrinciple.PRIVACY_AS_DEFAULT,
                category=DataProcessingCategory.COLLECTION,
                technical_implementation="Default opt-out for non-essential data processing",
                required_for_compliance=True
            ),
            PrivacyControl(
                control_id="pbdd_consent_granularity",
                name="Granular Consent Management",
                description="Provide granular consent options for different purposes",
                principle=PrivacyPrinciple.PRIVACY_AS_DEFAULT,
                category=DataProcessingCategory.COLLECTION,
                technical_implementation="Purpose-specific consent interfaces",
                required_for_compliance=True
            )
        ]
        
        # Security controls
        security_controls = [
            PrivacyControl(
                control_id="pbdd_encryption_at_rest",
                name="Encryption at Rest",
                description="Encrypt all personal data in storage",
                principle=PrivacyPrinciple.END_TO_END_SECURITY,
                category=DataProcessingCategory.STORAGE,
                technical_implementation="AES-256 encryption for all PII fields",
                required_for_compliance=True
            ),
            PrivacyControl(
                control_id="pbdd_encryption_in_transit",
                name="Encryption in Transit",
                description="Encrypt all personal data during transmission",
                principle=PrivacyPrinciple.END_TO_END_SECURITY,
                category=DataProcessingCategory.PROCESSING,
                technical_implementation="TLS 1.3 for all data transmission",
                required_for_compliance=True
            )
        ]
        
        # Transparency controls
        transparency_controls = [
            PrivacyControl(
                control_id="pbdd_privacy_notices",
                name="Clear Privacy Notices",
                description="Provide clear, understandable privacy information",
                principle=PrivacyPrinciple.VISIBILITY_TRANSPARENCY,
                category=DataProcessingCategory.COLLECTION,
                policy_implementation="Layered privacy notices with plain language",
                required_for_compliance=True
            ),
            PrivacyControl(
                control_id="pbdd_data_subject_rights",
                name="Data Subject Rights Portal",
                description="Provide easy access to data subject rights",
                principle=PrivacyPrinciple.RESPECT_USER_PRIVACY,
                category=DataProcessingCategory.PROCESSING,
                technical_implementation="Self-service portal for rights requests",
                required_for_compliance=True
            )
        ]
        
        # Retention controls
        retention_controls = [
            PrivacyControl(
                control_id="pbdd_automated_deletion",
                name="Automated Data Deletion",
                description="Automatically delete data when retention period expires",
                principle=PrivacyPrinciple.PROACTIVE_NOT_REACTIVE,
                category=DataProcessingCategory.DELETION,
                technical_implementation="Scheduled deletion jobs based on retention policies",
                required_for_compliance=True
            ),
            PrivacyControl(
                control_id="pbdd_retention_classification",
                name="Data Retention Classification",
                description="Classify data based on retention requirements",
                principle=PrivacyPrinciple.PRIVACY_EMBEDDED_INTO_DESIGN,
                category=DataProcessingCategory.RETENTION,
                technical_implementation="Automated data classification and tagging",
                required_for_compliance=True
            )
        ]
        
        # Combine all controls
        all_controls = (proactive_controls + default_controls + security_controls + 
                       transparency_controls + retention_controls)
        
        for control in all_controls:
            self.privacy_controls[control.control_id] = control
    
    async def assess_new_feature(
        self,
        feature_name: str,
        feature_description: str,
        data_processing_details: Dict[str, Any],
        developer_team: str = "",
        **kwargs
    ) -> str:
        """
        Assess privacy implications of a new feature
        
        Args:
            feature_name: Name of the new feature
            feature_description: Detailed description of the feature
            data_processing_details: Details about data processing activities
            developer_team: Team developing the feature
            **kwargs: Additional parameters
            
        Returns:
            str: Assessment ID
        """
        try:
            assessment_id = str(uuid.uuid4())
            
            # Extract data processing information
            data_categories = data_processing_details.get("data_categories", [])
            processing_purposes = data_processing_details.get("processing_purposes", [])
            legal_basis = data_processing_details.get("legal_basis", [])
            third_party_sharing = data_processing_details.get("third_party_sharing", False)
            automated_decision_making = data_processing_details.get("automated_decision_making", False)
            
            # Assess privacy impact level
            impact_level = await self._assess_privacy_impact_level(
                data_categories, processing_purposes, third_party_sharing, automated_decision_making
            )
            
            # Determine required privacy controls
            required_controls = await self._determine_required_controls(
                data_categories, processing_purposes, impact_level
            )
            
            # Create assessment
            assessment = FeaturePrivacyAssessment(
                assessment_id=assessment_id,
                feature_name=feature_name,
                feature_description=feature_description,
                impact_level=impact_level,
                data_categories=data_categories,
                processing_purposes=processing_purposes,
                legal_basis=legal_basis,
                privacy_controls=required_controls
            )
            
            # Perform detailed privacy analysis
            await self._perform_privacy_analysis(assessment, data_processing_details)
            
            # Store assessment
            self.feature_assessments[assessment_id] = assessment
            
            # Log assessment creation
            await self._log_audit_event({
                "event_type": "privacy_assessment_created",
                "assessment_id": assessment_id,
                "feature_name": feature_name,
                "impact_level": impact_level.value,
                "required_controls": len(required_controls),
                "developer_team": developer_team,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Determine if manual review is required
            if impact_level in [PrivacyImpactLevel.HIGH, PrivacyImpactLevel.VERY_HIGH]:
                await self._request_manual_privacy_review(assessment)
            else:
                # Automated approval for low-impact features
                await self._automated_approval_check(assessment)
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Privacy assessment created for feature '{feature_name}': {assessment_id}")
            return assessment_id
            
        except Exception as e:
            self.logger.error(f"Error assessing new feature: {e}")
            raise
    
    async def _assess_privacy_impact_level(
        self,
        data_categories: List[str],
        processing_purposes: List[str],
        third_party_sharing: bool,
        automated_decision_making: bool
    ) -> PrivacyImpactLevel:
        """Assess privacy impact level of the feature"""
        
        # High-risk data categories
        high_risk_categories = {
            "sensitive_personal_data", "health_data", "financial_data", 
            "biometric_data", "genetic_data", "location_data", "children_data"
        }
        
        # High-risk processing purposes
        high_risk_purposes = {
            "profiling", "automated_decision_making", "behavioral_analysis",
            "credit_scoring", "health_assessment"
        }
        
        # Calculate risk score
        risk_score = 0
        
        # Data category risk
        if any(cat in high_risk_categories for cat in data_categories):
            risk_score += 40
        elif any("personal" in cat.lower() for cat in data_categories):
            risk_score += 20
        
        # Processing purpose risk
        if any(purpose in high_risk_purposes for purpose in processing_purposes):
            risk_score += 30
        elif automated_decision_making:
            risk_score += 25
        
        # Third-party sharing risk
        if third_party_sharing:
            risk_score += 20
        
        # Large-scale processing
        if "large_scale" in processing_purposes:
            risk_score += 15
        
        # Determine impact level
        if risk_score >= 80:
            return PrivacyImpactLevel.VERY_HIGH
        elif risk_score >= 60:
            return PrivacyImpactLevel.HIGH
        elif risk_score >= 30:
            return PrivacyImpactLevel.MEDIUM
        else:
            return PrivacyImpactLevel.LOW
    
    async def _determine_required_controls(
        self,
        data_categories: List[str],
        processing_purposes: List[str],
        impact_level: PrivacyImpactLevel
    ) -> List[PrivacyControl]:
        """Determine required privacy controls for the feature"""
        
        required_controls = []
        
        # Base controls for all features
        base_control_ids = [
            "pbdd_data_minimization",
            "pbdd_purpose_limitation",
            "pbdd_default_privacy_settings"
        ]
        
        # Security controls for features processing personal data
        if any("personal" in cat.lower() for cat in data_categories):
            base_control_ids.extend([
                "pbdd_encryption_at_rest",
                "pbdd_encryption_in_transit"
            ])
        
        # Transparency controls for all features
        base_control_ids.extend([
            "pbdd_privacy_notices",
            "pbdd_data_subject_rights"
        ])
        
        # Additional controls for high-impact features
        if impact_level in [PrivacyImpactLevel.HIGH, PrivacyImpactLevel.VERY_HIGH]:
            base_control_ids.extend([
                "pbdd_automated_deletion",
                "pbdd_retention_classification"
            ])
        
        # Get control objects
        for control_id in base_control_ids:
            if control_id in self.privacy_controls:
                required_controls.append(self.privacy_controls[control_id])
        
        return required_controls
    
    async def _perform_privacy_analysis(
        self,
        assessment: FeaturePrivacyAssessment,
        data_processing_details: Dict[str, Any]
    ):
        """Perform detailed privacy analysis"""
        
        # Analyze data flows
        data_flows = data_processing_details.get("data_flows", [])
        await self._analyze_data_flows(assessment, data_flows)
        
        # Check for privacy risks
        await self._identify_privacy_risks(assessment, data_processing_details)
        
        # Recommend mitigation measures
        await self._recommend_mitigation_measures(assessment)
        
        # Validate legal basis
        await self._validate_legal_basis(assessment)
    
    async def _analyze_data_flows(self, assessment: FeaturePrivacyAssessment, data_flows: List[Dict[str, Any]]):
        """Analyze data flows for privacy implications"""
        
        risks = []
        
        for flow in data_flows:
            source = flow.get("source", "")
            destination = flow.get("destination", "")
            data_types = flow.get("data_types", [])
            
            # Check for cross-border transfers
            if flow.get("cross_border", False):
                risks.append(f"Cross-border data transfer: {source} -> {destination}")
            
            # Check for third-party sharing
            if "third_party" in destination.lower():
                risks.append(f"Third-party data sharing: {destination}")
            
            # Check for sensitive data in transit
            sensitive_data = ["health", "financial", "biometric", "sensitive"]
            if any(sensitive in " ".join(data_types).lower() for sensitive in sensitive_data):
                risks.append(f"Sensitive data transmission: {' '.join(data_types)}")
        
        assessment.residual_risks.extend(risks)
    
    async def _identify_privacy_risks(self, assessment: FeaturePrivacyAssessment, details: Dict[str, Any]):
        """Identify specific privacy risks"""
        
        risks = []
        
        # Automated decision-making risks
        if details.get("automated_decision_making", False):
            risks.append("Automated decision-making affecting individuals")
        
        # Profiling risks
        if "profiling" in assessment.processing_purposes:
            risks.append("Systematic profiling of individuals")
        
        # Large-scale processing risks
        if details.get("large_scale", False):
            risks.append("Large-scale processing of personal data")
        
        # Children's data risks
        if "children" in " ".join(assessment.data_categories).lower():
            risks.append("Processing of children's personal data")
        
        # Sensitive data risks
        sensitive_categories = ["health", "biometric", "genetic", "racial", "political", "religious"]
        if any(cat in " ".join(assessment.data_categories).lower() for cat in sensitive_categories):
            risks.append("Processing of sensitive personal data categories")
        
        assessment.residual_risks.extend(risks)
    
    async def _recommend_mitigation_measures(self, assessment: FeaturePrivacyAssessment):
        """Recommend privacy risk mitigation measures"""
        
        measures = []
        
        for risk in assessment.residual_risks:
            if "cross-border" in risk.lower():
                measures.append("Implement appropriate safeguards for international transfers")
            elif "third-party" in risk.lower():
                measures.append("Establish data processing agreements with third parties")
            elif "automated decision" in risk.lower():
                measures.append("Provide meaningful information about automated decision-making")
            elif "profiling" in risk.lower():
                measures.append("Implement profiling safeguards and opt-out mechanisms")
            elif "sensitive" in risk.lower():
                measures.append("Implement additional security measures for sensitive data")
            elif "children" in risk.lower():
                measures.append("Implement age verification and parental consent mechanisms")
        
        # General mitigation measures
        if assessment.impact_level in [PrivacyImpactLevel.HIGH, PrivacyImpactLevel.VERY_HIGH]:
            measures.extend([
                "Conduct regular privacy impact assessments",
                "Implement privacy monitoring and auditing",
                "Provide comprehensive privacy training to development team"
            ])
        
        assessment.mitigation_measures = list(set(measures))  # Remove duplicates
    
    async def _validate_legal_basis(self, assessment: FeaturePrivacyAssessment):
        """Validate legal basis for data processing"""
        
        if not assessment.legal_basis:
            assessment.residual_risks.append("No legal basis specified for data processing")
            assessment.mitigation_measures.append("Identify and document appropriate legal basis")
        
        # Check for consent requirements
        if "consent" in assessment.legal_basis:
            assessment.mitigation_measures.append("Implement granular consent management")
        
        # Check for legitimate interests
        if "legitimate_interests" in assessment.legal_basis:
            assessment.mitigation_measures.append("Conduct legitimate interests assessment")
    
    async def _automated_approval_check(self, assessment: FeaturePrivacyAssessment):
        """Perform automated approval check for low-risk features"""
        
        # Check if all required controls are implemented
        all_implemented = all(
            control.implementation_status == "implemented" 
            for control in assessment.privacy_controls
        )
        
        # Check if there are high-risk issues
        high_risk_indicators = [
            "sensitive", "children", "automated decision", "large-scale", "cross-border"
        ]
        
        has_high_risk = any(
            any(indicator in risk.lower() for indicator in high_risk_indicators)
            for risk in assessment.residual_risks
        )
        
        # Automated approval conditions
        if (assessment.impact_level == PrivacyImpactLevel.LOW and 
            not has_high_risk and 
            assessment.legal_basis):
            
            assessment.approval_status = "approved"
            assessment.approved_by = "automated_system"
            assessment.approval_date = datetime.utcnow()
            
            await self._log_audit_event({
                "event_type": "automated_privacy_approval",
                "assessment_id": assessment.assessment_id,
                "feature_name": assessment.feature_name,
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            assessment.approval_status = "pending"
            await self._request_manual_privacy_review(assessment)
    
    async def _request_manual_privacy_review(self, assessment: FeaturePrivacyAssessment):
        """Request manual privacy review for high-risk features"""
        
        await self._log_audit_event({
            "event_type": "manual_privacy_review_requested",
            "assessment_id": assessment.assessment_id,
            "feature_name": assessment.feature_name,
            "impact_level": assessment.impact_level.value,
            "risk_count": len(assessment.residual_risks),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # In a real implementation, this would notify privacy team
        self.logger.info(f"Manual privacy review requested for feature: {assessment.feature_name}")
    
    async def approve_feature(
        self,
        assessment_id: str,
        approver: str,
        conditions: Optional[List[str]] = None,
        comments: Optional[str] = None
    ) -> bool:
        """
        Approve a feature after privacy assessment
        
        Args:
            assessment_id: Assessment identifier
            approver: Person approving the feature
            conditions: Any conditions for approval
            comments: Approval comments
            
        Returns:
            bool: Success status
        """
        try:
            assessment = self.feature_assessments.get(assessment_id)
            if not assessment:
                return False
            
            assessment.approval_status = "conditional" if conditions else "approved"
            assessment.approved_by = approver
            assessment.approval_date = datetime.utcnow()
            
            if conditions:
                assessment.mitigation_measures.extend(conditions)
            
            if comments:
                assessment.metadata = assessment.metadata or {}
                assessment.metadata["approval_comments"] = comments
            
            await self._log_audit_event({
                "event_type": "feature_privacy_approved",
                "assessment_id": assessment_id,
                "feature_name": assessment.feature_name,
                "approved_by": approver,
                "conditional": bool(conditions),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Feature approved: {assessment.feature_name} by {approver}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error approving feature: {e}")
            return False
    
    async def get_feature_privacy_status(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get privacy status of a feature assessment"""
        assessment = self.feature_assessments.get(assessment_id)
        if not assessment:
            return None
        
        # Calculate control implementation progress
        total_controls = len(assessment.privacy_controls)
        implemented_controls = len([
            c for c in assessment.privacy_controls 
            if c.implementation_status == "implemented"
        ])
        
        return {
            "assessment_id": assessment_id,
            "feature_name": assessment.feature_name,
            "approval_status": assessment.approval_status,
            "impact_level": assessment.impact_level.value,
            "privacy_controls": {
                "total": total_controls,
                "implemented": implemented_controls,
                "completion_rate": (implemented_controls / total_controls * 100) if total_controls > 0 else 100
            },
            "risks_identified": len(assessment.residual_risks),
            "mitigation_measures": len(assessment.mitigation_measures),
            "approved_by": assessment.approved_by,
            "approval_date": assessment.approval_date.isoformat() if assessment.approval_date else None,
            "created_at": assessment.created_at.isoformat(),
            "requires_manual_review": assessment.impact_level in [PrivacyImpactLevel.HIGH, PrivacyImpactLevel.VERY_HIGH]
        }
    
    async def generate_privacy_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate privacy by design compliance report"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter assessments by date range
            filtered_assessments = [
                assessment for assessment in self.feature_assessments.values()
                if start_date <= assessment.created_at <= end_date
            ]
            
            # Calculate metrics
            total_assessments = len(filtered_assessments)
            approved_features = len([a for a in filtered_assessments if a.approval_status == "approved"])
            
            # Control implementation rate
            total_controls = sum(len(a.privacy_controls) for a in filtered_assessments)
            implemented_controls = sum(
                len([c for c in a.privacy_controls if c.implementation_status == "implemented"])
                for a in filtered_assessments
            )
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_privacy_assessments": total_assessments,
                    "approved_features": approved_features,
                    "approval_rate": (approved_features / total_assessments * 100) if total_assessments > 0 else 100,
                    "privacy_controls_implementation_rate": (implemented_controls / total_controls * 100) if total_controls > 0 else 100
                },
                "by_impact_level": {
                    level.value: len([a for a in filtered_assessments if a.impact_level == level])
                    for level in PrivacyImpactLevel
                },
                "by_approval_status": {
                    status: len([a for a in filtered_assessments if a.approval_status == status])
                    for status in ["pending", "approved", "rejected", "conditional"]
                },
                "privacy_principles_coverage": self._calculate_principle_coverage(),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating privacy compliance report: {e}")
            return {"error": str(e)}
    
    def _calculate_principle_coverage(self) -> Dict[str, float]:
        """Calculate coverage of privacy principles across controls"""
        principle_coverage = {}
        
        for principle in PrivacyPrinciple:
            principle_controls = [
                control for control in self.privacy_controls.values()
                if control.principle == principle
            ]
            
            if principle_controls:
                implemented = len([
                    control for control in principle_controls
                    if control.implementation_status == "implemented"
                ])
                coverage = (implemented / len(principle_controls)) * 100
            else:
                coverage = 0.0
            
            principle_coverage[principle.value] = coverage
        
        return principle_coverage
    
    async def _log_audit_event(self, event: Dict[str, Any]):
        """Log audit event"""
        event["id"] = str(uuid.uuid4())
        event["logged_at"] = datetime.utcnow().isoformat()
        self.audit_log.append(event)
    
    def _update_metrics(self):
        """Update privacy by design metrics"""
        total_assessments = len(self.feature_assessments)
        approved_features = len([
            a for a in self.feature_assessments.values() 
            if a.approval_status == "approved"
        ])
        
        total_controls = len(self.privacy_controls)
        implemented_controls = len([
            c for c in self.privacy_controls.values()
            if c.implementation_status == "implemented"
        ])
        
        self.metrics.update({
            "total_assessments": total_assessments,
            "approved_features": approved_features,
            "privacy_controls_implemented": implemented_controls,
            "compliance_score": (implemented_controls / total_controls * 100) if total_controls > 0 else 100
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get privacy by design metrics"""
        return self.metrics.copy()