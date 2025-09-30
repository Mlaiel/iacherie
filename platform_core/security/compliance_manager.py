#!/usr/bin/env python3
"""
Compliance Manager - Enterprise GDPR/SOC2/ISO27001 Compliance System
Automated compliance monitoring and audit trail management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided

This module provides comprehensive compliance management including:
- GDPR compliance automation with data subject rights
- SOC2 controls monitoring and evidence collection
- ISO27001 framework implementation and auditing
- Automated compliance reporting and documentation
- Data protection impact assessments (DPIA)
"""

import asyncio
import hashlib
import json
import logging
import secrets
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceStandard(Enum):
    """Compliance standard enumeration"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    SOX = "sox"


class ComplianceStatus(Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"


class DataSubjectRightType(Enum):
    """GDPR data subject rights enumeration"""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    AUTOMATED_DECISION_MAKING = "automated_decision_making"


class AuditType(Enum):
    """Audit type enumeration"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    REGULATORY = "regulatory"
    SELF_ASSESSMENT = "self_assessment"


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceRequirement:
    """Compliance requirement definition"""
    requirement_id: str
    standard: ComplianceStandard
    title: str
    description: str
    control_reference: str
    category: str
    mandatory: bool = True
    evidence_required: List[str] = field(default_factory=list)
    testing_frequency: str = "annual"  # daily, weekly, monthly, quarterly, annual
    responsible_role: str = ""
    status: ComplianceStatus = ComplianceStatus.UNDER_REVIEW
    last_assessment: Optional[datetime] = None
    next_assessment: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataSubjectRequest:
    """GDPR data subject request"""
    request_id: str
    data_subject_id: str
    request_type: DataSubjectRightType
    request_details: str
    requestor_identity_verified: bool = False
    received_at: datetime = field(default_factory=datetime.utcnow)
    response_due_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    status: str = "pending"  # pending, in_progress, completed, rejected
    response_provided: Optional[str] = None
    response_date: Optional[datetime] = None
    handled_by: Optional[str] = None
    evidence_collected: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditTrailEntry:
    """Audit trail entry"""
    entry_id: str
    timestamp: datetime
    user_id: Optional[str]
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str = ""
    user_agent: str = ""
    outcome: str = "success"
    compliance_relevance: List[ComplianceStandard] = field(default_factory=list)
    retention_period_days: int = 2555  # 7 years default
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceEvidence:
    """Compliance evidence document"""
    evidence_id: str
    requirement_id: str
    evidence_type: str  # document, log, screenshot, configuration
    title: str
    description: str
    file_path: Optional[str] = None
    content_hash: Optional[str] = None
    collected_by: str = ""
    collected_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataProtectionImpactAssessment:
    """GDPR Data Protection Impact Assessment"""
    dpia_id: str
    project_name: str
    project_description: str
    data_controller: str
    data_processor: Optional[str] = None
    personal_data_types: List[str] = field(default_factory=list)
    special_categories: List[str] = field(default_factory=list)
    processing_purposes: List[str] = field(default_factory=list)
    legal_basis: List[str] = field(default_factory=list)
    data_subjects: List[str] = field(default_factory=list)
    risks_identified: List[Dict[str, Any]] = field(default_factory=list)
    mitigation_measures: List[Dict[str, Any]] = field(default_factory=list)
    risk_assessment: RiskLevel = RiskLevel.MEDIUM
    consultation_required: bool = False
    dpo_consulted: bool = False
    supervisory_authority_consulted: bool = False
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "draft"  # draft, under_review, approved, rejected


@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    standard: ComplianceStandard
    report_type: str  # assessment, audit, monitoring
    reporting_period_start: datetime
    reporting_period_end: datetime
    overall_status: ComplianceStatus
    requirements_assessed: int = 0
    requirements_compliant: int = 0
    requirements_non_compliant: int = 0
    critical_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evidence_reviewed: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceManager:
    """
    Enterprise Compliance Manager
    
    Provides comprehensive compliance management for GDPR, SOC2, ISO27001,
    and other regulatory frameworks with automated monitoring, audit trails,
    and evidence collection specifically designed for creator economy platforms.
    """

    def __init__(self):
        # Compliance requirements by standard
        self.compliance_requirements: Dict[str, ComplianceRequirement] = {}
        
        # Data subject requests (GDPR)
        self.data_subject_requests: Dict[str, DataSubjectRequest] = {}
        
        # Audit trail storage
        self.audit_trail: List[AuditTrailEntry] = []
        
        # Evidence collection
        self.compliance_evidence: Dict[str, ComplianceEvidence] = {}
        
        # DPIA registry
        self.dpia_registry: Dict[str, DataProtectionImpactAssessment] = {}
        
        # Compliance reports
        self.compliance_reports: Dict[str, ComplianceReport] = {}
        
        # Configuration
        self.data_retention_policies: Dict[str, int] = {
            "audit_logs": 2555,  # 7 years in days
            "personal_data": 1095,  # 3 years
            "financial_records": 2555,  # 7 years
            "marketing_data": 365,  # 1 year
            "system_logs": 90  # 3 months
        }
        
        # Monitoring and alerting
        self.compliance_monitors: Dict[str, Dict[str, Any]] = {}
        self.alert_thresholds: Dict[str, float] = {
            "gdpr_response_overdue": 0.8,  # 80% of response time
            "audit_trail_gaps": 0.01,  # 1% missing entries
            "evidence_expiry": 0.9  # 90% of retention period
        }
        
        # Initialize compliance frameworks
        self._initialize_compliance_requirements()
        self._initialize_monitoring_rules()
        
        logger.info("Compliance Manager initialized with enterprise frameworks")

    def _initialize_compliance_requirements(self) -> None:
        """Initialize compliance requirements for supported standards"""
        try:
            # GDPR Requirements
            gdpr_requirements = [
                ComplianceRequirement(
                    requirement_id="gdpr_lawful_basis",
                    standard=ComplianceStandard.GDPR,
                    title="Lawful Basis for Processing",
                    description="Establish and document lawful basis for all personal data processing",
                    control_reference="Article 6",
                    category="Legal Basis",
                    evidence_required=["privacy_policy", "consent_records", "legitimate_interest_assessment"],
                    responsible_role="DPO"
                ),
                
                ComplianceRequirement(
                    requirement_id="gdpr_data_subject_rights",
                    standard=ComplianceStandard.GDPR,
                    title="Data Subject Rights",
                    description="Implement processes for handling data subject rights requests",
                    control_reference="Articles 15-22",
                    category="Data Subject Rights",
                    evidence_required=["request_handling_procedures", "response_templates", "request_logs"],
                    responsible_role="DPO"
                ),
                
                ComplianceRequirement(
                    requirement_id="gdpr_data_protection_by_design",
                    standard=ComplianceStandard.GDPR,
                    title="Data Protection by Design and Default",
                    description="Implement data protection principles in system design",
                    control_reference="Article 25",
                    category="Technical Measures",
                    evidence_required=["system_design_docs", "privacy_impact_assessments", "code_reviews"],
                    responsible_role="CTO"
                ),
                
                ComplianceRequirement(
                    requirement_id="gdpr_breach_notification",
                    standard=ComplianceStandard.GDPR,
                    title="Personal Data Breach Notification",
                    description="Implement breach detection and notification procedures",
                    control_reference="Articles 33-34",
                    category="Incident Response",
                    evidence_required=["breach_procedures", "notification_templates", "incident_logs"],
                    responsible_role="CISO"
                )
            ]
            
            # SOC2 Requirements
            soc2_requirements = [
                ComplianceRequirement(
                    requirement_id="soc2_access_controls",
                    standard=ComplianceStandard.SOC2,
                    title="Logical and Physical Access Controls",
                    description="Implement comprehensive access controls",
                    control_reference="CC6.1",
                    category="Common Criteria",
                    evidence_required=["access_control_matrix", "user_access_reviews", "authentication_logs"],
                    responsible_role="CISO"
                ),
                
                ComplianceRequirement(
                    requirement_id="soc2_system_monitoring",
                    standard=ComplianceStandard.SOC2,
                    title="System Monitoring",
                    description="Implement continuous monitoring of system operations",
                    control_reference="CC7.1",
                    category="System Operations",
                    evidence_required=["monitoring_procedures", "alert_configurations", "monitoring_logs"],
                    responsible_role="Operations Manager"
                ),
                
                ComplianceRequirement(
                    requirement_id="soc2_change_management",
                    standard=ComplianceStandard.SOC2,
                    title="Change Management",
                    description="Implement formal change management processes",
                    control_reference="CC8.1",
                    category="Change Management",
                    evidence_required=["change_procedures", "approval_workflows", "change_logs"],
                    responsible_role="CTO"
                )
            ]
            
            # ISO27001 Requirements
            iso27001_requirements = [
                ComplianceRequirement(
                    requirement_id="iso27001_risk_management",
                    standard=ComplianceStandard.ISO27001,
                    title="Information Security Risk Management",
                    description="Establish and maintain information security risk management",
                    control_reference="A.12.6",
                    category="Risk Management",
                    evidence_required=["risk_register", "risk_assessments", "treatment_plans"],
                    responsible_role="Risk Manager"
                ),
                
                ComplianceRequirement(
                    requirement_id="iso27001_incident_management",
                    standard=ComplianceStandard.ISO27001,
                    title="Information Security Incident Management",
                    description="Implement incident management procedures",
                    control_reference="A.16.1",
                    category="Incident Management",
                    evidence_required=["incident_procedures", "incident_reports", "lessons_learned"],
                    responsible_role="CISO"
                )
            ]
            
            # Store all requirements
            all_requirements = gdpr_requirements + soc2_requirements + iso27001_requirements
            for req in all_requirements:
                self.compliance_requirements[req.requirement_id] = req
            
            logger.info(f"Initialized {len(all_requirements)} compliance requirements")
            
        except Exception as e:
            logger.error(f"Failed to initialize compliance requirements: {e}")

    def _initialize_monitoring_rules(self) -> None:
        """Initialize automated compliance monitoring rules"""
        try:
            self.compliance_monitors = {
                "gdpr_consent_tracking": {
                    "description": "Monitor consent collection and withdrawal",
                    "frequency": "real_time",
                    "enabled": True,
                    "alert_conditions": ["consent_withdrawal_delay", "missing_consent_records"]
                },
                
                "data_retention_compliance": {
                    "description": "Monitor data retention policy compliance",
                    "frequency": "daily",
                    "enabled": True,
                    "alert_conditions": ["retention_period_exceeded", "deletion_failures"]
                },
                
                "access_control_review": {
                    "description": "Monitor user access reviews and certifications",
                    "frequency": "weekly",
                    "enabled": True,
                    "alert_conditions": ["overdue_access_reviews", "excessive_privileges"]
                },
                
                "audit_trail_integrity": {
                    "description": "Monitor audit trail completeness and integrity",
                    "frequency": "continuous",
                    "enabled": True,
                    "alert_conditions": ["missing_audit_entries", "audit_log_tampering"]
                }
            }
            
            logger.info(f"Initialized {len(self.compliance_monitors)} monitoring rules")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring rules: {e}")

    async def handle_data_subject_request(self, request: DataSubjectRequest) -> str:
        """Handle GDPR data subject rights request"""
        try:
            # Generate unique request ID
            if not request.request_id:
                request.request_id = f"dsr_{uuid.uuid4().hex[:8]}"
            
            # Validate request
            if not await self._validate_data_subject_request(request):
                raise ValueError("Invalid data subject request")
            
            # Store request
            self.data_subject_requests[request.request_id] = request
            
            # Log audit trail
            await self._log_audit_event(
                action="data_subject_request_received",
                resource=f"dsr:{request.request_id}",
                details={
                    "request_type": request.request_type.value,
                    "data_subject_id": request.data_subject_id,
                    "due_date": request.response_due_date.isoformat()
                },
                compliance_relevance=[ComplianceStandard.GDPR]
            )
            
            # Trigger automated processing if applicable
            if request.request_type == DataSubjectRightType.ACCESS:
                await self._process_data_access_request(request)
            elif request.request_type == DataSubjectRightType.ERASURE:
                await self._process_data_erasure_request(request)
            elif request.request_type == DataSubjectRightType.PORTABILITY:
                await self._process_data_portability_request(request)
            
            logger.info(f"Data subject request {request.request_id} processed")
            return request.request_id
            
        except Exception as e:
            logger.error(f"Failed to handle data subject request: {e}")
            raise

    async def create_dpia(self, dpia: DataProtectionImpactAssessment) -> str:
        """Create Data Protection Impact Assessment"""
        try:
            if not dpia.dpia_id:
                dpia.dpia_id = f"dpia_{uuid.uuid4().hex[:8]}"
            
            # Perform automated risk assessment
            dpia.risk_assessment = await self._assess_data_processing_risk(dpia)
            
            # Determine if consultation is required
            if dpia.risk_assessment in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                dpia.consultation_required = True
            
            # Store DPIA
            self.dpia_registry[dpia.dpia_id] = dpia
            
            # Log audit trail
            await self._log_audit_event(
                action="dpia_created",
                resource=f"dpia:{dpia.dpia_id}",
                details={
                    "project_name": dpia.project_name,
                    "risk_level": dpia.risk_assessment.value,
                    "consultation_required": dpia.consultation_required
                },
                compliance_relevance=[ComplianceStandard.GDPR]
            )
            
            logger.info(f"DPIA {dpia.dpia_id} created with risk level: {dpia.risk_assessment.value}")
            return dpia.dpia_id
            
        except Exception as e:
            logger.error(f"Failed to create DPIA: {e}")
            raise

    async def collect_compliance_evidence(self, evidence: ComplianceEvidence) -> str:
        """Collect and store compliance evidence"""
        try:
            if not evidence.evidence_id:
                evidence.evidence_id = f"evidence_{uuid.uuid4().hex[:8]}"
            
            # Calculate content hash for integrity
            if evidence.file_path and not evidence.content_hash:
                evidence.content_hash = await self._calculate_file_hash(evidence.file_path)
            
            # Store evidence
            self.compliance_evidence[evidence.evidence_id] = evidence
            
            # Update requirement status if evidence is complete
            requirement = self.compliance_requirements.get(evidence.requirement_id)
            if requirement:
                await self._update_requirement_status(requirement, evidence)
            
            # Log audit trail
            await self._log_audit_event(
                action="compliance_evidence_collected",
                resource=f"evidence:{evidence.evidence_id}",
                details={
                    "requirement_id": evidence.requirement_id,
                    "evidence_type": evidence.evidence_type,
                    "title": evidence.title
                },
                compliance_relevance=[requirement.standard] if requirement else []
            )
            
            logger.info(f"Compliance evidence {evidence.evidence_id} collected")
            return evidence.evidence_id
            
        except Exception as e:
            logger.error(f"Failed to collect compliance evidence: {e}")
            raise

    async def generate_compliance_report(self, standard: ComplianceStandard,
                                       period_start: datetime,
                                       period_end: datetime) -> ComplianceReport:
        """Generate compliance assessment report"""
        try:
            report_id = f"report_{standard.value}_{int(period_start.timestamp())}"
            
            # Get requirements for this standard
            standard_requirements = [
                req for req in self.compliance_requirements.values()
                if req.standard == standard
            ]
            
            # Assess compliance status
            compliant_count = 0
            non_compliant_count = 0
            critical_findings = []
            recommendations = []
            
            for req in standard_requirements:
                if req.status == ComplianceStatus.COMPLIANT:
                    compliant_count += 1
                elif req.status == ComplianceStatus.NON_COMPLIANT:
                    non_compliant_count += 1
                    if req.mandatory:
                        critical_findings.append(f"Non-compliant mandatory requirement: {req.title}")
                        recommendations.append(f"Immediate remediation required for {req.requirement_id}")
            
            # Determine overall status
            compliance_rate = compliant_count / len(standard_requirements) if standard_requirements else 0
            if compliance_rate >= 0.95:
                overall_status = ComplianceStatus.COMPLIANT
            elif compliance_rate >= 0.8:
                overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                overall_status = ComplianceStatus.NON_COMPLIANT
            
            # Create report
            report = ComplianceReport(
                report_id=report_id,
                standard=standard,
                report_type="assessment",
                reporting_period_start=period_start,
                reporting_period_end=period_end,
                overall_status=overall_status,
                requirements_assessed=len(standard_requirements),
                requirements_compliant=compliant_count,
                requirements_non_compliant=non_compliant_count,
                critical_findings=critical_findings,
                recommendations=recommendations,
                evidence_reviewed=[e.evidence_id for e in self.compliance_evidence.values()
                                 if any(req.requirement_id == e.requirement_id 
                                       for req in standard_requirements)]
            )
            
            # Store report
            self.compliance_reports[report_id] = report
            
            # Log audit trail
            await self._log_audit_event(
                action="compliance_report_generated",
                resource=f"report:{report_id}",
                details={
                    "standard": standard.value,
                    "overall_status": overall_status.value,
                    "compliance_rate": compliance_rate
                },
                compliance_relevance=[standard]
            )
            
            logger.info(f"Compliance report {report_id} generated for {standard.value}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise

    async def monitor_compliance(self) -> Dict[str, Any]:
        """Run automated compliance monitoring"""
        try:
            monitoring_results = {}
            current_time = datetime.utcnow()
            
            # Check GDPR response times
            overdue_requests = [
                req for req in self.data_subject_requests.values()
                if (req.status in ["pending", "in_progress"] and 
                    current_time > req.response_due_date)
            ]
            
            monitoring_results["gdpr_overdue_requests"] = len(overdue_requests)
            
            # Check data retention compliance
            retention_violations = await self._check_data_retention_compliance()
            monitoring_results["retention_violations"] = len(retention_violations)
            
            # Check evidence expiry
            expiring_evidence = [
                evidence for evidence in self.compliance_evidence.values()
                if (evidence.expires_at and 
                    evidence.expires_at <= current_time + timedelta(days=30))
            ]
            monitoring_results["expiring_evidence"] = len(expiring_evidence)
            
            # Check audit trail gaps
            audit_gaps = await self._check_audit_trail_gaps()
            monitoring_results["audit_trail_gaps"] = len(audit_gaps)
            
            # Generate alerts for critical issues
            alerts = []
            if overdue_requests:
                alerts.append(f"{len(overdue_requests)} GDPR requests overdue")
            if retention_violations:
                alerts.append(f"{len(retention_violations)} data retention violations")
            
            monitoring_results["alerts"] = alerts
            monitoring_results["monitoring_timestamp"] = current_time.isoformat()
            
            return monitoring_results
            
        except Exception as e:
            logger.error(f"Failed to monitor compliance: {e}")
            return {"error": str(e)}

    # Private helper methods
    
    async def _validate_data_subject_request(self, request: DataSubjectRequest) -> bool:
        """Validate data subject request"""
        try:
            # Check required fields
            if not request.data_subject_id or not request.request_type:
                return False
            
            # Identity verification required for sensitive requests
            if request.request_type in [DataSubjectRightType.ERASURE, DataSubjectRightType.PORTABILITY]:
                if not request.requestor_identity_verified:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate data subject request: {e}")
            return False

    async def _process_data_access_request(self, request: DataSubjectRequest) -> None:
        """Process data access request automatically"""
        try:
            # This would integrate with data stores to collect user data
            # For now, we'll simulate the process
            
            request.status = "in_progress"
            request.evidence_collected.append("personal_data_export")
            request.evidence_collected.append("processing_activities_log")
            
            # In real implementation, collect actual data from all systems
            logger.info(f"Processing data access request for {request.data_subject_id}")
            
        except Exception as e:
            logger.error(f"Failed to process data access request: {e}")

    async def _process_data_erasure_request(self, request: DataSubjectRequest) -> None:
        """Process data erasure request"""
        try:
            # Check for legal obligations to retain data
            retention_check = await self._check_legal_retention_requirements(request.data_subject_id)
            
            if retention_check["can_erase"]:
                request.status = "in_progress"
                request.evidence_collected.append("erasure_verification")
                # In real implementation, trigger data deletion across all systems
            else:
                request.status = "rejected"
                request.response_provided = f"Cannot erase due to: {retention_check['reason']}"
            
            logger.info(f"Processing data erasure request for {request.data_subject_id}")
            
        except Exception as e:
            logger.error(f"Failed to process data erasure request: {e}")

    async def _process_data_portability_request(self, request: DataSubjectRequest) -> None:
        """Process data portability request"""
        try:
            request.status = "in_progress"
            request.evidence_collected.append("structured_data_export")
            # In real implementation, generate structured data export
            
            logger.info(f"Processing data portability request for {request.data_subject_id}")
            
        except Exception as e:
            logger.error(f"Failed to process data portability request: {e}")

    async def _assess_data_processing_risk(self, dpia: DataProtectionImpactAssessment) -> RiskLevel:
        """Assess risk level for data processing activity"""
        try:
            risk_factors = 0
            
            # Special category data increases risk
            if dpia.special_categories:
                risk_factors += 2
            
            # Large scale processing increases risk
            if "large_scale" in dpia.processing_purposes:
                risk_factors += 1
            
            # Automated decision making increases risk
            if "automated_decision_making" in dpia.processing_purposes:
                risk_factors += 2
            
            # Data subject vulnerability increases risk
            if any(subject in ["children", "employees", "vulnerable_groups"] for subject in dpia.data_subjects):
                risk_factors += 1
            
            # Determine risk level
            if risk_factors >= 4:
                return RiskLevel.CRITICAL
            elif risk_factors >= 3:
                return RiskLevel.HIGH
            elif risk_factors >= 1:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
                
        except Exception as e:
            logger.error(f"Failed to assess data processing risk: {e}")
            return RiskLevel.MEDIUM

    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for integrity verification"""
        try:
            # In real implementation, read and hash the actual file
            # For now, return a placeholder hash
            return hashlib.sha256(file_path.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return ""

    async def _update_requirement_status(self, requirement: ComplianceRequirement,
                                       evidence: ComplianceEvidence) -> None:
        """Update requirement status based on evidence"""
        try:
            # Check if all required evidence is collected
            collected_evidence_types = [
                e.evidence_type for e in self.compliance_evidence.values()
                if e.requirement_id == requirement.requirement_id
            ]
            
            missing_evidence = set(requirement.evidence_required) - set(collected_evidence_types)
            
            if not missing_evidence:
                requirement.status = ComplianceStatus.COMPLIANT
                requirement.last_assessment = datetime.utcnow()
            else:
                requirement.status = ComplianceStatus.PARTIALLY_COMPLIANT
            
        except Exception as e:
            logger.error(f"Failed to update requirement status: {e}")

    async def _check_data_retention_compliance(self) -> List[Dict[str, Any]]:
        """Check for data retention policy violations"""
        try:
            violations = []
            current_time = datetime.utcnow()
            
            # Check audit trail retention
            for entry in self.audit_trail:
                retention_days = self.data_retention_policies.get(
                    entry.details.get("data_type", "system_logs"), 
                    self.data_retention_policies["system_logs"]
                )
                
                if current_time > entry.timestamp + timedelta(days=retention_days):
                    violations.append({
                        "type": "retention_exceeded",
                        "entry_id": entry.entry_id,
                        "age_days": (current_time - entry.timestamp).days,
                        "retention_limit": retention_days
                    })
            
            return violations
            
        except Exception as e:
            logger.error(f"Failed to check data retention compliance: {e}")
            return []

    async def _check_audit_trail_gaps(self) -> List[Dict[str, Any]]:
        """Check for gaps in audit trail"""
        try:
            gaps = []
            
            # Sort audit entries by timestamp
            sorted_entries = sorted(self.audit_trail, key=lambda x: x.timestamp)
            
            # Check for unusual gaps (more than 1 hour between entries)
            for i in range(1, len(sorted_entries)):
                time_gap = sorted_entries[i].timestamp - sorted_entries[i-1].timestamp
                if time_gap > timedelta(hours=1):
                    gaps.append({
                        "start_time": sorted_entries[i-1].timestamp.isoformat(),
                        "end_time": sorted_entries[i].timestamp.isoformat(),
                        "gap_duration_hours": time_gap.total_seconds() / 3600
                    })
            
            return gaps
            
        except Exception as e:
            logger.error(f"Failed to check audit trail gaps: {e}")
            return []

    async def _check_legal_retention_requirements(self, user_id: str) -> Dict[str, Any]:
        """Check if data must be retained for legal reasons"""
        try:
            # In real implementation, check against legal hold policies
            # For now, return a simple check
            return {
                "can_erase": True,
                "reason": None
            }
            
        except Exception as e:
            logger.error(f"Failed to check legal retention requirements: {e}")
            return {"can_erase": False, "reason": "Error checking requirements"}

    async def _log_audit_event(self, action: str, resource: str, details: Dict[str, Any],
                             user_id: str = None, compliance_relevance: List[ComplianceStandard] = None) -> None:
        """Log audit trail event"""
        try:
            entry = AuditTrailEntry(
                entry_id=secrets.token_urlsafe(16),
                timestamp=datetime.utcnow(),
                user_id=user_id,
                action=action,
                resource=resource,
                details=details,
                compliance_relevance=compliance_relevance or []
            )
            
            self.audit_trail.append(entry)
            
            # Maintain audit trail size limit
            if len(self.audit_trail) > 100000:
                self.audit_trail = self.audit_trail[-50000:]  # Keep most recent 50k entries
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    async def get_compliance_statistics(self) -> Dict[str, Any]:
        """Get compliance management statistics"""
        try:
            current_time = datetime.utcnow()
            
            # Count requirements by status
            status_counts = defaultdict(int)
            for req in self.compliance_requirements.values():
                status_counts[req.status.value] += 1
            
            # Count data subject requests by status
            dsr_status_counts = defaultdict(int)
            for req in self.data_subject_requests.values():
                dsr_status_counts[req.status] += 1
            
            # Count overdue requests
            overdue_requests = len([
                req for req in self.data_subject_requests.values()
                if (req.status in ["pending", "in_progress"] and 
                    current_time > req.response_due_date)
            ])
            
            return {
                "total_requirements": len(self.compliance_requirements),
                "requirements_by_status": dict(status_counts),
                "requirements_by_standard": {
                    standard.value: len([req for req in self.compliance_requirements.values() 
                                       if req.standard == standard])
                    for standard in ComplianceStandard
                },
                "total_data_subject_requests": len(self.data_subject_requests),
                "dsr_by_status": dict(dsr_status_counts),
                "overdue_dsr_requests": overdue_requests,
                "total_evidence_collected": len(self.compliance_evidence),
                "total_dpias": len(self.dpia_registry),
                "audit_trail_entries": len(self.audit_trail),
                "compliance_reports_generated": len(self.compliance_reports),
                "monitoring_rules_active": len([m for m in self.compliance_monitors.values() if m["enabled"]]),
                "timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get compliance statistics: {e}")
            return {"error": str(e)}


# Factory function for easier instantiation
def create_compliance_manager() -> ComplianceManager:
    """Factory function to create a Compliance Manager"""
    return ComplianceManager()


# Example usage and testing
async def main():
    """Example usage of Compliance Manager"""
    compliance_manager = create_compliance_manager()
    
    # Test data subject request
    dsr = DataSubjectRequest(
        request_id="",
        data_subject_id="user_123",
        request_type=DataSubjectRightType.ACCESS,
        request_details="User requesting access to all personal data",
        requestor_identity_verified=True
    )
    
    request_id = await compliance_manager.handle_data_subject_request(dsr)
    print(f"Data subject request processed: {request_id}")
    
    # Test DPIA creation
    dpia = DataProtectionImpactAssessment(
        dpia_id="",
        project_name="AI Content Analysis",
        project_description="Implementing AI-based content analysis for creators",
        data_controller="IA Chérie Platform",
        personal_data_types=["user_content", "behavioral_data"],
        processing_purposes=["content_analysis", "recommendation_engine"],
        legal_basis=["legitimate_interest"],
        data_subjects=["content_creators", "platform_users"]
    )
    
    dpia_id = await compliance_manager.create_dpia(dpia)
    print(f"DPIA created: {dpia_id}")
    
    # Generate compliance report
    report = await compliance_manager.generate_compliance_report(
        standard=ComplianceStandard.GDPR,
        period_start=datetime.utcnow() - timedelta(days=90),
        period_end=datetime.utcnow()
    )
    print(f"Compliance report generated: {report.report_id}")
    
    # Get statistics
    stats = await compliance_manager.get_compliance_statistics()
    print(f"Compliance Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())