"""Vendor Risk Assessment for Third Parties

Implements comprehensive vendor risk assessment for GDPR compliance,
data processing agreements, and third-party risk management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class VendorCategory(Enum):
    """Categories of vendors"""
    DATA_PROCESSOR = "data_processor"
    DATA_CONTROLLER = "data_controller"
    JOINT_CONTROLLER = "joint_controller"
    SUB_PROCESSOR = "sub_processor"
    CLOUD_PROVIDER = "cloud_provider"
    ANALYTICS_PROVIDER = "analytics_provider"
    MARKETING_PROVIDER = "marketing_provider"
    PAYMENT_PROCESSOR = "payment_processor"
    SUPPORT_PROVIDER = "support_provider"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssessmentStatus(Enum):
    """Status of vendor assessment"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REMEDIATION = "requires_remediation"


@dataclass
class SecurityControl:
    """Individual security control assessment"""
    control_id: str
    name: str
    description: str
    implemented: bool = False
    evidence_provided: bool = False
    assessment_notes: str = ""
    risk_score: float = 0.0
    required_for_approval: bool = True


@dataclass
class ComplianceFramework:
    """Compliance framework assessment"""
    framework_name: str
    certified: bool = False
    certification_details: str = ""
    compliance_score: float = 0.0
    gaps_identified: List[str] = field(default_factory=list)
    remediation_plan: List[str] = field(default_factory=list)


@dataclass
class DataProcessingDetails:
    """Details about vendor data processing"""
    data_categories: List[str] = field(default_factory=list)
    processing_purposes: List[str] = field(default_factory=list)
    data_subjects: List[str] = field(default_factory=list)
    retention_periods: Dict[str, str] = field(default_factory=dict)
    cross_border_transfers: bool = False
    transfer_countries: List[str] = field(default_factory=list)
    transfer_safeguards: List[str] = field(default_factory=list)
    sub_processors: List[str] = field(default_factory=list)


@dataclass
class VendorAssessment:
    """Comprehensive vendor risk assessment"""
    assessment_id: str
    vendor_name: str
    vendor_category: VendorCategory
    vendor_contact: str
    assessment_status: AssessmentStatus = AssessmentStatus.PENDING
    overall_risk_level: RiskLevel = RiskLevel.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    assessed_by: str = ""
    completed_at: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    
    # Data processing details
    data_processing: DataProcessingDetails = field(default_factory=DataProcessingDetails)
    
    # Security assessment
    security_controls: List[SecurityControl] = field(default_factory=list)
    security_score: float = 0.0
    
    # Compliance assessment
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    compliance_score: float = 0.0
    
    # Risk assessment
    identified_risks: List[str] = field(default_factory=list)
    mitigation_measures: List[str] = field(default_factory=list)
    residual_risks: List[str] = field(default_factory=list)
    
    # Legal assessment
    dpa_required: bool = True
    dpa_in_place: bool = False
    dpa_review_date: Optional[datetime] = None
    liability_coverage: str = ""
    insurance_details: str = ""
    
    # Assessment artifacts
    documents_reviewed: List[str] = field(default_factory=list)
    questionnaire_responses: Dict[str, Any] = field(default_factory=dict)
    audit_findings: List[str] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class VendorRiskManager:
    """
    Vendor Risk Assessment Manager
    
    Handles comprehensive vendor risk assessments including security,
    compliance, data protection, and legal requirements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.vendor_assessments: Dict[str, VendorAssessment] = {}
        self.assessment_templates: Dict[VendorCategory, Dict[str, Any]] = {}
        
        # Initialize assessment templates
        self._initialize_assessment_templates()
        
        # Audit trail
        self.audit_log: List[Dict[str, Any]] = []
        
        # Metrics
        self.metrics = {
            "total_vendors": 0,
            "approved_vendors": 0,
            "high_risk_vendors": 0,
            "overdue_reviews": 0,
            "compliance_rate": 100.0,
            "average_assessment_time": 0.0
        }
    
    def _initialize_assessment_templates(self):
        """Initialize vendor assessment templates by category"""
        
        # Data Processor Template
        data_processor_template = {
            "security_controls": [
                {
                    "control_id": "sec_encryption",
                    "name": "Data Encryption",
                    "description": "Encryption of data at rest and in transit",
                    "required_for_approval": True
                },
                {
                    "control_id": "sec_access_control",
                    "name": "Access Controls",
                    "description": "Role-based access controls and authentication",
                    "required_for_approval": True
                },
                {
                    "control_id": "sec_audit_logging",
                    "name": "Audit Logging",
                    "description": "Comprehensive audit logging and monitoring",
                    "required_for_approval": True
                },
                {
                    "control_id": "sec_incident_response",
                    "name": "Incident Response",
                    "description": "Documented incident response procedures",
                    "required_for_approval": True
                },
                {
                    "control_id": "sec_data_backup",
                    "name": "Data Backup and Recovery",
                    "description": "Regular data backup and disaster recovery",
                    "required_for_approval": False
                }
            ],
            "compliance_frameworks": [
                "ISO 27001", "SOC 2 Type II", "GDPR Compliance", "PCI DSS"
            ],
            "required_documents": [
                "Security Policy", "Privacy Policy", "Data Processing Agreement",
                "Incident Response Plan", "Business Continuity Plan"
            ]
        }
        
        # Cloud Provider Template
        cloud_provider_template = {
            "security_controls": [
                {
                    "control_id": "cloud_network_security",
                    "name": "Network Security",
                    "description": "Network segmentation and security controls",
                    "required_for_approval": True
                },
                {
                    "control_id": "cloud_data_residency",
                    "name": "Data Residency Controls",
                    "description": "Controls over data location and residency",
                    "required_for_approval": True
                },
                {
                    "control_id": "cloud_compliance_monitoring",
                    "name": "Compliance Monitoring",
                    "description": "Continuous compliance monitoring and reporting",
                    "required_for_approval": True
                }
            ],
            "compliance_frameworks": [
                "ISO 27001", "SOC 2 Type II", "GDPR Compliance", "FedRAMP", "CSA STAR"
            ],
            "required_documents": [
                "Security Whitepaper", "Compliance Attestations", "Data Processing Agreement",
                "Service Level Agreement", "Shared Responsibility Model"
            ]
        }
        
        self.assessment_templates = {
            VendorCategory.DATA_PROCESSOR: data_processor_template,
            VendorCategory.CLOUD_PROVIDER: cloud_provider_template,
            VendorCategory.ANALYTICS_PROVIDER: data_processor_template,
            VendorCategory.MARKETING_PROVIDER: data_processor_template,
            VendorCategory.PAYMENT_PROCESSOR: {
                **data_processor_template,
                "compliance_frameworks": data_processor_template["compliance_frameworks"] + ["PCI DSS Level 1"]
            }
        }
    
    async def initiate_vendor_assessment(
        self,
        vendor_name: str,
        vendor_category: VendorCategory,
        vendor_contact: str,
        assessed_by: str,
        data_processing_details: Dict[str, Any],
        **kwargs
    ) -> str:
        """
        Initiate a new vendor risk assessment
        
        Args:
            vendor_name: Name of the vendor
            vendor_category: Category of vendor
            vendor_contact: Contact information
            assessed_by: Person conducting assessment
            data_processing_details: Details about data processing
            **kwargs: Additional parameters
            
        Returns:
            str: Assessment ID
        """
        try:
            assessment_id = str(uuid.uuid4())
            
            # Create data processing details
            data_processing = DataProcessingDetails(
                data_categories=data_processing_details.get("data_categories", []),
                processing_purposes=data_processing_details.get("processing_purposes", []),
                data_subjects=data_processing_details.get("data_subjects", []),
                retention_periods=data_processing_details.get("retention_periods", {}),
                cross_border_transfers=data_processing_details.get("cross_border_transfers", False),
                transfer_countries=data_processing_details.get("transfer_countries", []),
                transfer_safeguards=data_processing_details.get("transfer_safeguards", []),
                sub_processors=data_processing_details.get("sub_processors", [])
            )
            
            # Initialize security controls from template
            security_controls = []
            template = self.assessment_templates.get(vendor_category, {})
            
            for control_data in template.get("security_controls", []):
                control = SecurityControl(
                    control_id=control_data["control_id"],
                    name=control_data["name"],
                    description=control_data["description"],
                    required_for_approval=control_data["required_for_approval"]
                )
                security_controls.append(control)
            
            # Initialize compliance frameworks
            compliance_frameworks = []
            for framework_name in template.get("compliance_frameworks", []):
                framework = ComplianceFramework(framework_name=framework_name)
                compliance_frameworks.append(framework)
            
            # Calculate next review date (annually)
            next_review = datetime.utcnow() + timedelta(days=365)
            
            # Create assessment
            assessment = VendorAssessment(
                assessment_id=assessment_id,
                vendor_name=vendor_name,
                vendor_category=vendor_category,
                vendor_contact=vendor_contact,
                assessed_by=assessed_by,
                next_review_date=next_review,
                data_processing=data_processing,
                security_controls=security_controls,
                compliance_frameworks=compliance_frameworks,
                documents_reviewed=template.get("required_documents", []),
                metadata=kwargs.get("metadata", {})
            )
            
            self.vendor_assessments[assessment_id] = assessment
            
            # Log assessment initiation
            await self._log_audit_event({
                "event_type": "vendor_assessment_initiated",
                "assessment_id": assessment_id,
                "vendor_name": vendor_name,
                "vendor_category": vendor_category.value,
                "assessed_by": assessed_by,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Start automated assessment process
            await self._start_assessment_process(assessment)
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Vendor assessment initiated: {vendor_name} ({assessment_id})")
            return assessment_id
            
        except Exception as e:
            self.logger.error(f"Error initiating vendor assessment: {e}")
            raise
    
    async def _start_assessment_process(self, assessment: VendorAssessment):
        """Start the automated assessment process"""
        try:
            assessment.assessment_status = AssessmentStatus.IN_PROGRESS
            
            # Perform initial risk assessment
            await self._perform_initial_risk_assessment(assessment)
            
            # Generate vendor questionnaire
            await self._generate_vendor_questionnaire(assessment)
            
            # Request required documents
            await self._request_vendor_documents(assessment)
            
        except Exception as e:
            self.logger.error(f"Error starting assessment process: {e}")
    
    async def _perform_initial_risk_assessment(self, assessment: VendorAssessment):
        """Perform initial risk assessment based on data processing details"""
        
        risk_score = 0
        risks = []
        
        # Data sensitivity risk
        sensitive_data = ["health", "financial", "biometric", "genetic", "sensitive"]
        if any(sensitive in " ".join(assessment.data_processing.data_categories).lower() for sensitive in sensitive_data):
            risk_score += 30
            risks.append("Processing of sensitive personal data")
        
        # Cross-border transfer risk
        if assessment.data_processing.cross_border_transfers:
            risk_score += 20
            risks.append("Cross-border data transfers")
            
            # Additional risk for non-adequate countries
            high_risk_countries = ["china", "russia", "north_korea", "iran"]
            if any(country.lower() in high_risk_countries for country in assessment.data_processing.transfer_countries):
                risk_score += 25
                risks.append("Transfers to high-risk jurisdictions")
        
        # Processing purpose risk
        high_risk_purposes = ["profiling", "automated_decision_making", "behavioral_analysis"]
        if any(purpose in assessment.data_processing.processing_purposes for purpose in high_risk_purposes):
            risk_score += 25
            risks.append("High-risk processing purposes")
        
        # Sub-processor risk
        if assessment.data_processing.sub_processors:
            risk_score += 15
            risks.append("Use of sub-processors")
        
        # Volume risk (if data subjects include large populations)
        large_scale_indicators = ["customers", "users", "employees", "members"]
        if any(indicator in " ".join(assessment.data_processing.data_subjects).lower() for indicator in large_scale_indicators):
            risk_score += 10
            risks.append("Large-scale data processing")
        
        # Determine risk level
        if risk_score >= 80:
            assessment.overall_risk_level = RiskLevel.CRITICAL
        elif risk_score >= 60:
            assessment.overall_risk_level = RiskLevel.HIGH
        elif risk_score >= 30:
            assessment.overall_risk_level = RiskLevel.MEDIUM
        else:
            assessment.overall_risk_level = RiskLevel.LOW
        
        assessment.identified_risks = risks
        
        await self._log_audit_event({
            "event_type": "initial_risk_assessment_completed",
            "assessment_id": assessment.assessment_id,
            "risk_level": assessment.overall_risk_level.value,
            "risk_score": risk_score,
            "risks_identified": len(risks),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def update_security_assessment(
        self,
        assessment_id: str,
        security_updates: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Update security control assessments
        
        Args:
            assessment_id: Assessment identifier
            security_updates: Updates for security controls
            
        Returns:
            bool: Success status
        """
        try:
            assessment = self.vendor_assessments.get(assessment_id)
            if not assessment:
                return False
            
            # Update security controls
            for control in assessment.security_controls:
                if control.control_id in security_updates:
                    update_data = security_updates[control.control_id]
                    control.implemented = update_data.get("implemented", control.implemented)
                    control.evidence_provided = update_data.get("evidence_provided", control.evidence_provided)
                    control.assessment_notes = update_data.get("assessment_notes", control.assessment_notes)
                    control.risk_score = update_data.get("risk_score", control.risk_score)
            
            # Calculate overall security score
            assessment.security_score = await self._calculate_security_score(assessment)
            
            await self._log_audit_event({
                "event_type": "security_assessment_updated",
                "assessment_id": assessment_id,
                "security_score": assessment.security_score,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating security assessment: {e}")
            return False
    
    async def update_compliance_assessment(
        self,
        assessment_id: str,
        compliance_updates: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Update compliance framework assessments
        
        Args:
            assessment_id: Assessment identifier
            compliance_updates: Updates for compliance frameworks
            
        Returns:
            bool: Success status
        """
        try:
            assessment = self.vendor_assessments.get(assessment_id)
            if not assessment:
                return False
            
            # Update compliance frameworks
            for framework in assessment.compliance_frameworks:
                if framework.framework_name in compliance_updates:
                    update_data = compliance_updates[framework.framework_name]
                    framework.certified = update_data.get("certified", framework.certified)
                    framework.certification_details = update_data.get("certification_details", framework.certification_details)
                    framework.compliance_score = update_data.get("compliance_score", framework.compliance_score)
                    framework.gaps_identified = update_data.get("gaps_identified", framework.gaps_identified)
                    framework.remediation_plan = update_data.get("remediation_plan", framework.remediation_plan)
            
            # Calculate overall compliance score
            assessment.compliance_score = await self._calculate_compliance_score(assessment)
            
            await self._log_audit_event({
                "event_type": "compliance_assessment_updated",
                "assessment_id": assessment_id,
                "compliance_score": assessment.compliance_score,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating compliance assessment: {e}")
            return False
    
    async def complete_vendor_assessment(
        self,
        assessment_id: str,
        final_decision: str,
        decision_rationale: str,
        conditions: Optional[List[str]] = None
    ) -> bool:
        """
        Complete vendor risk assessment
        
        Args:
            assessment_id: Assessment identifier
            final_decision: approved, rejected, or conditional
            decision_rationale: Rationale for decision
            conditions: Conditions for approval (if conditional)
            
        Returns:
            bool: Success status
        """
        try:
            assessment = self.vendor_assessments.get(assessment_id)
            if not assessment:
                return False
            
            # Update assessment status
            if final_decision == "approved":
                assessment.assessment_status = AssessmentStatus.APPROVED
            elif final_decision == "rejected":
                assessment.assessment_status = AssessmentStatus.REJECTED
            elif final_decision == "conditional":
                assessment.assessment_status = AssessmentStatus.REQUIRES_REMEDIATION
                if conditions:
                    assessment.mitigation_measures.extend(conditions)
            
            assessment.completed_at = datetime.utcnow()
            assessment.metadata.update({
                "final_decision": final_decision,
                "decision_rationale": decision_rationale,
                "approval_conditions": conditions or []
            })
            
            # Generate final risk assessment
            await self._generate_final_risk_assessment(assessment)
            
            # Create monitoring schedule if approved
            if assessment.assessment_status == AssessmentStatus.APPROVED:
                await self._schedule_ongoing_monitoring(assessment)
            
            await self._log_audit_event({
                "event_type": "vendor_assessment_completed",
                "assessment_id": assessment_id,
                "vendor_name": assessment.vendor_name,
                "final_decision": final_decision,
                "risk_level": assessment.overall_risk_level.value,
                "security_score": assessment.security_score,
                "compliance_score": assessment.compliance_score,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Vendor assessment completed: {assessment.vendor_name} - {final_decision}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error completing vendor assessment: {e}")
            return False
    
    async def get_vendor_assessment_status(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive vendor assessment status"""
        assessment = self.vendor_assessments.get(assessment_id)
        if not assessment:
            return None
        
        # Calculate control implementation status
        total_controls = len(assessment.security_controls)
        implemented_controls = len([c for c in assessment.security_controls if c.implemented])
        
        # Calculate compliance status
        total_frameworks = len(assessment.compliance_frameworks)
        certified_frameworks = len([f for f in assessment.compliance_frameworks if f.certified])
        
        return {
            "assessment_id": assessment_id,
            "vendor_name": assessment.vendor_name,
            "vendor_category": assessment.vendor_category.value,
            "assessment_status": assessment.assessment_status.value,
            "overall_risk_level": assessment.overall_risk_level.value,
            "security_assessment": {
                "overall_score": assessment.security_score,
                "controls_implemented": f"{implemented_controls}/{total_controls}",
                "implementation_rate": (implemented_controls / total_controls * 100) if total_controls > 0 else 100
            },
            "compliance_assessment": {
                "overall_score": assessment.compliance_score,
                "frameworks_certified": f"{certified_frameworks}/{total_frameworks}",
                "certification_rate": (certified_frameworks / total_frameworks * 100) if total_frameworks > 0 else 100
            },
            "data_processing": {
                "data_categories": len(assessment.data_processing.data_categories),
                "cross_border_transfers": assessment.data_processing.cross_border_transfers,
                "sub_processors": len(assessment.data_processing.sub_processors)
            },
            "legal_status": {
                "dpa_required": assessment.dpa_required,
                "dpa_in_place": assessment.dpa_in_place,
                "dpa_review_date": assessment.dpa_review_date.isoformat() if assessment.dpa_review_date else None
            },
            "timeline": {
                "created_at": assessment.created_at.isoformat(),
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
                "next_review_date": assessment.next_review_date.isoformat() if assessment.next_review_date else None
            },
            "risks_identified": len(assessment.identified_risks),
            "mitigation_measures": len(assessment.mitigation_measures)
        }
    
    async def generate_vendor_risk_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive vendor risk report"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=90)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter assessments by date range
            filtered_assessments = [
                assessment for assessment in self.vendor_assessments.values()
                if start_date <= assessment.created_at <= end_date
            ]
            
            # Calculate metrics
            total_vendors = len(filtered_assessments)
            approved_vendors = len([a for a in filtered_assessments if a.assessment_status == AssessmentStatus.APPROVED])
            high_risk_vendors = len([a for a in filtered_assessments if a.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
            
            # Average scores
            avg_security_score = sum(a.security_score for a in filtered_assessments) / total_vendors if total_vendors > 0 else 0
            avg_compliance_score = sum(a.compliance_score for a in filtered_assessments) / total_vendors if total_vendors > 0 else 0
            
            # Assessment times
            completed_assessments = [a for a in filtered_assessments if a.completed_at]
            avg_assessment_time = 0.0
            if completed_assessments:
                assessment_times = [
                    (a.completed_at - a.created_at).total_seconds() / 86400  # days
                    for a in completed_assessments
                ]
                avg_assessment_time = sum(assessment_times) / len(assessment_times)
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_vendor_assessments": total_vendors,
                    "approved_vendors": approved_vendors,
                    "approval_rate": (approved_vendors / total_vendors * 100) if total_vendors > 0 else 100,
                    "high_risk_vendors": high_risk_vendors,
                    "average_security_score": avg_security_score,
                    "average_compliance_score": avg_compliance_score,
                    "average_assessment_time_days": avg_assessment_time
                },
                "by_vendor_category": {
                    category.value: len([a for a in filtered_assessments if a.vendor_category == category])
                    for category in VendorCategory
                },
                "by_risk_level": {
                    level.value: len([a for a in filtered_assessments if a.overall_risk_level == level])
                    for level in RiskLevel
                },
                "by_status": {
                    status.value: len([a for a in filtered_assessments if a.assessment_status == status])
                    for status in AssessmentStatus
                },
                "overdue_reviews": self._get_overdue_reviews(),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating vendor risk report: {e}")
            return {"error": str(e)}
    
    # Helper methods (simplified implementations)
    
    async def _calculate_security_score(self, assessment: VendorAssessment) -> float:
        """Calculate overall security score"""
        if not assessment.security_controls:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for control in assessment.security_controls:
            weight = 2.0 if control.required_for_approval else 1.0
            score = 100.0 if control.implemented else (50.0 if control.evidence_provided else 0.0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _calculate_compliance_score(self, assessment: VendorAssessment) -> float:
        """Calculate overall compliance score"""
        if not assessment.compliance_frameworks:
            return 0.0
        
        total_score = sum(f.compliance_score for f in assessment.compliance_frameworks)
        return total_score / len(assessment.compliance_frameworks)
    
    async def _generate_vendor_questionnaire(self, assessment: VendorAssessment):
        """Generate vendor security questionnaire"""
        # Implementation would generate and send questionnaire
        self.logger.info(f"Vendor questionnaire generated for {assessment.vendor_name}")
    
    async def _request_vendor_documents(self, assessment: VendorAssessment):
        """Request required documents from vendor"""
        # Implementation would send document request
        self.logger.info(f"Document request sent to {assessment.vendor_name}")
    
    async def _generate_final_risk_assessment(self, assessment: VendorAssessment):
        """Generate final risk assessment summary"""
        # Combine all assessment components
        final_risks = []
        
        if assessment.security_score < 80:
            final_risks.append("Inadequate security controls")
        
        if assessment.compliance_score < 80:
            final_risks.append("Compliance framework gaps")
        
        if assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            final_risks.append("High inherent risk level")
        
        assessment.residual_risks = final_risks
    
    async def _schedule_ongoing_monitoring(self, assessment: VendorAssessment):
        """Schedule ongoing monitoring for approved vendors"""
        # Implementation would schedule periodic reviews
        self.logger.info(f"Ongoing monitoring scheduled for {assessment.vendor_name}")
    
    def _get_overdue_reviews(self) -> List[Dict[str, Any]]:
        """Get vendors with overdue reviews"""
        overdue = []
        current_time = datetime.utcnow()
        
        for assessment in self.vendor_assessments.values():
            if (assessment.assessment_status == AssessmentStatus.APPROVED and
                assessment.next_review_date and
                current_time > assessment.next_review_date):
                
                overdue.append({
                    "assessment_id": assessment.assessment_id,
                    "vendor_name": assessment.vendor_name,
                    "next_review_date": assessment.next_review_date.isoformat(),
                    "days_overdue": (current_time - assessment.next_review_date).days
                })
        
        return overdue
    
    async def _log_audit_event(self, event: Dict[str, Any]):
        """Log audit event"""
        event["id"] = str(uuid.uuid4())
        event["logged_at"] = datetime.utcnow().isoformat()
        self.audit_log.append(event)
    
    def _update_metrics(self):
        """Update vendor risk metrics"""
        total = len(self.vendor_assessments)
        approved = len([a for a in self.vendor_assessments.values() if a.assessment_status == AssessmentStatus.APPROVED])
        high_risk = len([a for a in self.vendor_assessments.values() if a.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
        overdue = len(self._get_overdue_reviews())
        
        self.metrics.update({
            "total_vendors": total,
            "approved_vendors": approved,
            "high_risk_vendors": high_risk,
            "overdue_reviews": overdue,
            "compliance_rate": (approved / total * 100) if total > 0 else 100
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get vendor risk metrics"""
        return self.metrics.copy()