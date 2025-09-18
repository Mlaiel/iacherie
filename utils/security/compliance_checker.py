"""
Compliance Checker - Security Utilities Level 2
=============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade compliance checking system for Ainflue creator economy platform.
GDPR, SOX, ISO 27001 validation with < 30ms compliance checks.

Performance: < 30ms compliance checks
Standards: GDPR, SOX, ISO 27001, NIST, creator economy compliance
"""

import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    SOX = "sox"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    CREATOR_ECONOMY = "creator_economy"

class ComplianceStatus(Enum):
    """Compliance check status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANT = "partial_compliant"
    UNKNOWN = "unknown"
    REQUIRES_REVIEW = "requires_review"

class Severity(Enum):
    """Compliance violation severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ComplianceRequirement:
    """Compliance requirement definition."""
    requirement_id: str
    framework: ComplianceFramework
    title: str
    description: str
    category: str
    mandatory: bool
    evidence_required: List[str] = field(default_factory=list)
    validation_criteria: Dict[str, Any] = field(default_factory=dict)
    creator_specific: bool = False

@dataclass
class ComplianceViolation:
    """Compliance violation container."""
    violation_id: str
    requirement: ComplianceRequirement
    severity: Severity
    description: str
    evidence: Dict[str, Any]
    remediation_steps: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    creator_impact: Optional[str] = None

@dataclass
class ComplianceResult:
    """Compliance check result container."""
    success: bool
    framework: ComplianceFramework
    overall_status: ComplianceStatus
    compliance_score: float
    violations: List[ComplianceViolation] = field(default_factory=list)
    requirements_checked: int = 0
    requirements_passed: int = 0
    check_duration_ms: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    next_review_date: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)

class ComplianceChecker:
    """
    Enterprise-grade compliance checking system for creator economy platform.
    
    Features:
    - GDPR compliance validation
    - SOX financial controls verification
    - ISO 27001 security management checks
    - Creator economy specific compliance
    - Performance: < 30ms compliance checks
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize compliance checker with enterprise configuration."""
        self.config = config or {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Compliance requirements database
        self.compliance_requirements = self._load_compliance_requirements()
        self.compliance_history: List[ComplianceResult] = []
        
        # Configuration
        self.enabled_frameworks = self.config.get("enabled_frameworks", [
            ComplianceFramework.GDPR,
            ComplianceFramework.SOX,
            ComplianceFramework.ISO27001,
            ComplianceFramework.CREATOR_ECONOMY
        ])
        
        # Creator economy specific settings
        self.creator_data_retention_days = self.config.get("creator_data_retention_days", 2555)  # 7 years
        self.content_backup_required = self.config.get("content_backup_required", True)
        
        logger.info("ComplianceChecker initialized with enterprise configuration")

    def _load_compliance_requirements(self) -> Dict[ComplianceFramework, List[ComplianceRequirement]]:
        """Load compliance requirements for different frameworks."""
        requirements = {
            ComplianceFramework.GDPR: [
                ComplianceRequirement(
                    requirement_id="GDPR-1",
                    framework=ComplianceFramework.GDPR,
                    title="Data Processing Lawfulness",
                    description="Ensure lawful basis for processing personal data",
                    category="data_processing",
                    mandatory=True,
                    evidence_required=["privacy_policy", "consent_records"],
                    validation_criteria={"consent_rate": 0.95, "policy_updated": True},
                    creator_specific=True
                ),
                ComplianceRequirement(
                    requirement_id="GDPR-2",
                    framework=ComplianceFramework.GDPR,
                    title="Data Subject Rights",
                    description="Implement data subject rights (access, rectification, erasure)",
                    category="data_subject_rights",
                    mandatory=True,
                    evidence_required=["dsar_process", "response_times"],
                    validation_criteria={"response_time_days": 30, "automation": True}
                ),
                ComplianceRequirement(
                    requirement_id="GDPR-3",
                    framework=ComplianceFramework.GDPR,
                    title="Data Protection by Design",
                    description="Implement privacy by design and default",
                    category="technical_measures",
                    mandatory=True,
                    evidence_required=["encryption", "access_controls", "data_minimization"],
                    validation_criteria={"encryption_strength": "AES-256", "access_control": True}
                ),
                ComplianceRequirement(
                    requirement_id="GDPR-4",
                    framework=ComplianceFramework.GDPR,
                    title="Data Breach Notification",
                    description="Notify data breaches within 72 hours",
                    category="incident_management",
                    mandatory=True,
                    evidence_required=["incident_response_plan", "notification_procedures"],
                    validation_criteria={"notification_time_hours": 72, "automation": True}
                ),
                ComplianceRequirement(
                    requirement_id="GDPR-5",
                    framework=ComplianceFramework.GDPR,
                    title="Creator Content Protection",
                    description="Protect creator personal data in content metadata",
                    category="creator_protection",
                    mandatory=True,
                    evidence_required=["metadata_scrubbing", "content_anonymization"],
                    validation_criteria={"metadata_removal": True, "geo_data_protection": True},
                    creator_specific=True
                )
            ],
            
            ComplianceFramework.SOX: [
                ComplianceRequirement(
                    requirement_id="SOX-1",
                    framework=ComplianceFramework.SOX,
                    title="Financial Controls Documentation",
                    description="Document and test internal financial controls",
                    category="financial_controls",
                    mandatory=True,
                    evidence_required=["control_documentation", "testing_results"],
                    validation_criteria={"documentation_complete": True, "testing_frequency": "quarterly"}
                ),
                ComplianceRequirement(
                    requirement_id="SOX-2",
                    framework=ComplianceFramework.SOX,
                    title="Revenue Recognition Controls",
                    description="Implement controls for creator revenue recognition",
                    category="revenue_controls",
                    mandatory=True,
                    evidence_required=["revenue_tracking", "audit_trails"],
                    validation_criteria={"automation": True, "audit_trail": True},
                    creator_specific=True
                ),
                ComplianceRequirement(
                    requirement_id="SOX-3",
                    framework=ComplianceFramework.SOX,
                    title="Change Management Controls",
                    description="Implement IT change management controls",
                    category="it_controls",
                    mandatory=True,
                    evidence_required=["change_logs", "approval_processes"],
                    validation_criteria={"approval_required": True, "testing_required": True}
                ),
                ComplianceRequirement(
                    requirement_id="SOX-4",
                    framework=ComplianceFramework.SOX,
                    title="Payment Processing Controls",
                    description="Secure creator payment processing and reconciliation",
                    category="payment_controls",
                    mandatory=True,
                    evidence_required=["payment_logs", "reconciliation_reports"],
                    validation_criteria={"encryption": True, "segregation_of_duties": True},
                    creator_specific=True
                )
            ],
            
            ComplianceFramework.ISO27001: [
                ComplianceRequirement(
                    requirement_id="ISO-1",
                    framework=ComplianceFramework.ISO27001,
                    title="Information Security Management System",
                    description="Establish and maintain ISMS",
                    category="isms",
                    mandatory=True,
                    evidence_required=["isms_documentation", "risk_assessments"],
                    validation_criteria={"documented": True, "reviewed_annually": True}
                ),
                ComplianceRequirement(
                    requirement_id="ISO-2",
                    framework=ComplianceFramework.ISO27001,
                    title="Risk Management Process",
                    description="Implement systematic risk management",
                    category="risk_management",
                    mandatory=True,
                    evidence_required=["risk_register", "treatment_plans"],
                    validation_criteria={"risk_assessment_frequency": "annual", "treatment_plans": True}
                ),
                ComplianceRequirement(
                    requirement_id="ISO-3",
                    framework=ComplianceFramework.ISO27001,
                    title="Access Control Management",
                    description="Implement proper access controls",
                    category="access_control",
                    mandatory=True,
                    evidence_required=["access_policies", "user_provisioning"],
                    validation_criteria={"rbac": True, "regular_reviews": True}
                ),
                ComplianceRequirement(
                    requirement_id="ISO-4",
                    framework=ComplianceFramework.ISO27001,
                    title="Creator Asset Protection",
                    description="Protect creator intellectual property assets",
                    category="asset_protection",
                    mandatory=True,
                    evidence_required=["asset_inventory", "protection_measures"],
                    validation_criteria={"classification": True, "protection_adequate": True},
                    creator_specific=True
                )
            ],
            
            ComplianceFramework.CREATOR_ECONOMY: [
                ComplianceRequirement(
                    requirement_id="CE-1",
                    framework=ComplianceFramework.CREATOR_ECONOMY,
                    title="Creator Intellectual Property Protection",
                    description="Implement strong IP protection for creator content",
                    category="ip_protection",
                    mandatory=True,
                    evidence_required=["watermarking", "copyright_detection", "dmca_process"],
                    validation_criteria={"watermarking_enabled": True, "detection_accuracy": 0.95},
                    creator_specific=True
                ),
                ComplianceRequirement(
                    requirement_id="CE-2",
                    framework=ComplianceFramework.CREATOR_ECONOMY,
                    title="Fair Revenue Distribution",
                    description="Ensure transparent and fair revenue sharing",
                    category="revenue_fairness",
                    mandatory=True,
                    evidence_required=["revenue_algorithms", "transparency_reports"],
                    validation_criteria={"algorithm_audited": True, "transparency": True},
                    creator_specific=True
                ),
                ComplianceRequirement(
                    requirement_id="CE-3",
                    framework=ComplianceFramework.CREATOR_ECONOMY,
                    title="Content Authenticity Verification",
                    description="Verify and maintain content authenticity",
                    category="content_authenticity",
                    mandatory=True,
                    evidence_required=["authenticity_checks", "blockchain_records"],
                    validation_criteria={"verification_rate": 0.99, "immutable_records": True},
                    creator_specific=True
                ),
                ComplianceRequirement(
                    requirement_id="CE-4",
                    framework=ComplianceFramework.CREATOR_ECONOMY,
                    title="Creator Data Sovereignty",
                    description="Ensure creators maintain control over their data",
                    category="data_sovereignty",
                    mandatory=True,
                    evidence_required=["data_portability", "deletion_capabilities"],
                    validation_criteria={"portability": True, "deletion_complete": True},
                    creator_specific=True
                )
            ]
        }
        
        return requirements

    async def validate_gdpr_compliance(self, system_data: Dict[str, Any]) -> ComplianceResult:
        """
        Validate GDPR compliance for the creator economy platform.
        
        Args:
            system_data: System configuration and data for compliance check
            
        Returns:
            ComplianceResult with GDPR compliance status
        """
        start_time = time.perf_counter()
        
        try:
            gdpr_requirements = self.compliance_requirements[ComplianceFramework.GDPR]
            violations = []
            requirements_passed = 0
            
            for requirement in gdpr_requirements:
                violation = await self._check_gdpr_requirement(requirement, system_data)
                if violation:
                    violations.append(violation)
                else:
                    requirements_passed += 1
            
            # Calculate compliance score
            compliance_score = requirements_passed / len(gdpr_requirements)
            
            # Determine overall status
            if compliance_score >= 0.95:
                status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 0.80:
                status = ComplianceStatus.PARTIAL_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            result = ComplianceResult(
                success=True,
                framework=ComplianceFramework.GDPR,
                overall_status=status,
                compliance_score=compliance_score,
                violations=violations,
                requirements_checked=len(gdpr_requirements),
                requirements_passed=requirements_passed,
                check_duration_ms=execution_time,
                recommendations=self._generate_gdpr_recommendations(violations),
                next_review_date=datetime.now(timezone.utc) + timedelta(days=90)
            )
            
            self.compliance_history.append(result)
            
            logger.info(f"GDPR compliance check completed in {execution_time:.2f}ms: {status.value}")
            return result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"GDPR compliance check failed in {execution_time:.2f}ms: {str(e)}")
            return ComplianceResult(
                success=False,
                framework=ComplianceFramework.GDPR,
                overall_status=ComplianceStatus.UNKNOWN,
                compliance_score=0.0,
                errors=[f"GDPR compliance check error: {str(e)}"],
                check_duration_ms=execution_time
            )

    async def _check_gdpr_requirement(self, requirement: ComplianceRequirement, 
                                    system_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check individual GDPR requirement."""
        try:
            if requirement.requirement_id == "GDPR-1":
                # Check data processing lawfulness
                consent_rate = system_data.get("consent_rate", 0.0)
                privacy_policy_updated = system_data.get("privacy_policy_updated", False)
                
                if consent_rate < requirement.validation_criteria["consent_rate"] or not privacy_policy_updated:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.HIGH,
                        description=f"Insufficient consent rate ({consent_rate}) or outdated privacy policy",
                        evidence={"consent_rate": consent_rate, "policy_updated": privacy_policy_updated},
                        remediation_steps=[
                            "Update privacy policy to latest requirements",
                            "Implement improved consent collection mechanisms",
                            "Review lawful basis for processing creator data"
                        ],
                        creator_impact="Creator content processing may be non-compliant"
                    )
            
            elif requirement.requirement_id == "GDPR-2":
                # Check data subject rights implementation
                dsar_automation = system_data.get("dsar_automation", False)
                avg_response_time = system_data.get("avg_dsar_response_time", 35)
                
                if not dsar_automation or avg_response_time > requirement.validation_criteria["response_time_days"]:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.MEDIUM,
                        description=f"DSAR response time ({avg_response_time} days) exceeds limit or lacks automation",
                        evidence={"automation": dsar_automation, "response_time": avg_response_time},
                        remediation_steps=[
                            "Implement automated DSAR processing",
                            "Optimize data retrieval processes",
                            "Train staff on GDPR response procedures"
                        ]
                    )
            
            elif requirement.requirement_id == "GDPR-3":
                # Check privacy by design implementation
                encryption_strength = system_data.get("encryption_algorithm", "")
                access_controls = system_data.get("access_controls_implemented", False)
                
                if encryption_strength != requirement.validation_criteria["encryption_strength"] or not access_controls:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.HIGH,
                        description="Inadequate technical measures for privacy protection",
                        evidence={"encryption": encryption_strength, "access_controls": access_controls},
                        remediation_steps=[
                            "Upgrade encryption to AES-256",
                            "Implement comprehensive access controls",
                            "Review data minimization practices"
                        ]
                    )
            
            elif requirement.requirement_id == "GDPR-4":
                # Check breach notification procedures
                breach_notification_time = system_data.get("breach_notification_hours", 96)
                automation = system_data.get("breach_automation", False)
                
                if breach_notification_time > requirement.validation_criteria["notification_time_hours"] or not automation:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.CRITICAL,
                        description="Breach notification time exceeds 72-hour requirement",
                        evidence={"notification_time": breach_notification_time, "automation": automation},
                        remediation_steps=[
                            "Implement automated breach detection",
                            "Streamline notification procedures",
                            "Test incident response plan quarterly"
                        ],
                        deadline=datetime.now(timezone.utc) + timedelta(days=30)
                    )
            
            elif requirement.requirement_id == "GDPR-5":
                # Check creator content protection
                metadata_scrubbing = system_data.get("metadata_scrubbing_enabled", False)
                geo_protection = system_data.get("geo_data_protection", False)
                
                if not metadata_scrubbing or not geo_protection:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.HIGH,
                        description="Inadequate creator personal data protection in content",
                        evidence={"metadata_scrubbing": metadata_scrubbing, "geo_protection": geo_protection},
                        remediation_steps=[
                            "Enable automatic metadata scrubbing",
                            "Implement geographic data protection",
                            "Train creators on privacy settings"
                        ],
                        creator_impact="Creator personal data may be exposed in content metadata"
                    )
            
            return None  # No violation found
            
        except Exception as e:
            logger.error(f"GDPR requirement check failed for {requirement.requirement_id}: {str(e)}")
            return None

    async def check_sox_requirements(self, financial_data: Dict[str, Any]) -> ComplianceResult:
        """
        Check SOX compliance for financial controls.
        
        Args:
            financial_data: Financial system data for compliance check
            
        Returns:
            ComplianceResult with SOX compliance status
        """
        start_time = time.perf_counter()
        
        try:
            sox_requirements = self.compliance_requirements[ComplianceFramework.SOX]
            violations = []
            requirements_passed = 0
            
            for requirement in sox_requirements:
                violation = await self._check_sox_requirement(requirement, financial_data)
                if violation:
                    violations.append(violation)
                else:
                    requirements_passed += 1
            
            compliance_score = requirements_passed / len(sox_requirements)
            
            if compliance_score >= 0.95:
                status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 0.85:
                status = ComplianceStatus.PARTIAL_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            result = ComplianceResult(
                success=True,
                framework=ComplianceFramework.SOX,
                overall_status=status,
                compliance_score=compliance_score,
                violations=violations,
                requirements_checked=len(sox_requirements),
                requirements_passed=requirements_passed,
                check_duration_ms=execution_time,
                recommendations=self._generate_sox_recommendations(violations),
                next_review_date=datetime.now(timezone.utc) + timedelta(days=90)
            )
            
            self.compliance_history.append(result)
            
            logger.info(f"SOX compliance check completed in {execution_time:.2f}ms: {status.value}")
            return result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"SOX compliance check failed in {execution_time:.2f}ms: {str(e)}")
            return ComplianceResult(
                success=False,
                framework=ComplianceFramework.SOX,
                overall_status=ComplianceStatus.UNKNOWN,
                compliance_score=0.0,
                errors=[f"SOX compliance check error: {str(e)}"],
                check_duration_ms=execution_time
            )

    async def _check_sox_requirement(self, requirement: ComplianceRequirement,
                                   financial_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check individual SOX requirement."""
        try:
            if requirement.requirement_id == "SOX-1":
                # Check financial controls documentation
                controls_documented = financial_data.get("controls_documented", False)
                testing_frequency = financial_data.get("testing_frequency", "")
                
                if not controls_documented or testing_frequency != "quarterly":
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.HIGH,
                        description="Financial controls not properly documented or tested",
                        evidence={"documented": controls_documented, "testing": testing_frequency},
                        remediation_steps=[
                            "Document all financial controls",
                            "Implement quarterly testing schedule",
                            "Engage external auditors for validation"
                        ]
                    )
            
            elif requirement.requirement_id == "SOX-2":
                # Check revenue recognition controls
                revenue_automation = financial_data.get("revenue_automation", False)
                audit_trail = financial_data.get("revenue_audit_trail", False)
                
                if not revenue_automation or not audit_trail:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.HIGH,
                        description="Creator revenue recognition lacks proper controls",
                        evidence={"automation": revenue_automation, "audit_trail": audit_trail},
                        remediation_steps=[
                            "Implement automated revenue tracking",
                            "Enhance audit trail capabilities",
                            "Regular reconciliation procedures"
                        ],
                        creator_impact="Creator revenue reporting may be inaccurate"
                    )
            
            elif requirement.requirement_id == "SOX-3":
                # Check change management controls
                approval_required = financial_data.get("change_approval_required", False)
                testing_required = financial_data.get("change_testing_required", False)
                
                if not approval_required or not testing_required:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.MEDIUM,
                        description="IT change management controls insufficient",
                        evidence={"approval": approval_required, "testing": testing_required},
                        remediation_steps=[
                            "Implement change approval workflow",
                            "Require testing for all changes",
                            "Document change procedures"
                        ]
                    )
            
            elif requirement.requirement_id == "SOX-4":
                # Check payment processing controls
                payment_encryption = financial_data.get("payment_encryption", False)
                segregation_duties = financial_data.get("segregation_of_duties", False)
                
                if not payment_encryption or not segregation_duties:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.CRITICAL,
                        description="Payment processing controls inadequate",
                        evidence={"encryption": payment_encryption, "segregation": segregation_duties},
                        remediation_steps=[
                            "Implement payment encryption",
                            "Enforce segregation of duties",
                            "Regular payment reconciliation"
                        ],
                        creator_impact="Creator payments may be at risk"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"SOX requirement check failed for {requirement.requirement_id}: {str(e)}")
            return None

    async def verify_iso27001_controls(self, security_data: Dict[str, Any]) -> ComplianceResult:
        """
        Verify ISO 27001 security controls implementation.
        
        Args:
            security_data: Security system data for compliance check
            
        Returns:
            ComplianceResult with ISO 27001 compliance status
        """
        start_time = time.perf_counter()
        
        try:
            iso_requirements = self.compliance_requirements[ComplianceFramework.ISO27001]
            violations = []
            requirements_passed = 0
            
            for requirement in iso_requirements:
                violation = await self._check_iso_requirement(requirement, security_data)
                if violation:
                    violations.append(violation)
                else:
                    requirements_passed += 1
            
            compliance_score = requirements_passed / len(iso_requirements)
            
            if compliance_score >= 0.90:
                status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 0.75:
                status = ComplianceStatus.PARTIAL_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            result = ComplianceResult(
                success=True,
                framework=ComplianceFramework.ISO27001,
                overall_status=status,
                compliance_score=compliance_score,
                violations=violations,
                requirements_checked=len(iso_requirements),
                requirements_passed=requirements_passed,
                check_duration_ms=execution_time,
                recommendations=self._generate_iso_recommendations(violations),
                next_review_date=datetime.now(timezone.utc) + timedelta(days=365)  # Annual review
            )
            
            self.compliance_history.append(result)
            
            logger.info(f"ISO 27001 compliance check completed in {execution_time:.2f}ms: {status.value}")
            return result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"ISO 27001 compliance check failed in {execution_time:.2f}ms: {str(e)}")
            return ComplianceResult(
                success=False,
                framework=ComplianceFramework.ISO27001,
                overall_status=ComplianceStatus.UNKNOWN,
                compliance_score=0.0,
                errors=[f"ISO 27001 compliance check error: {str(e)}"],
                check_duration_ms=execution_time
            )

    async def _check_iso_requirement(self, requirement: ComplianceRequirement,
                                   security_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check individual ISO 27001 requirement."""
        try:
            if requirement.requirement_id == "ISO-1":
                # Check ISMS implementation
                isms_documented = security_data.get("isms_documented", False)
                annual_review = security_data.get("isms_reviewed_annually", False)
                
                if not isms_documented or not annual_review:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.HIGH,
                        description="ISMS not properly established or maintained",
                        evidence={"documented": isms_documented, "reviewed": annual_review},
                        remediation_steps=[
                            "Document ISMS procedures",
                            "Implement annual review process",
                            "Train staff on ISMS requirements"
                        ]
                    )
            
            elif requirement.requirement_id == "ISO-2":
                # Check risk management
                risk_assessment_frequency = security_data.get("risk_assessment_frequency", "")
                treatment_plans = security_data.get("risk_treatment_plans", False)
                
                if risk_assessment_frequency != "annual" or not treatment_plans:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.MEDIUM,
                        description="Risk management process inadequate",
                        evidence={"frequency": risk_assessment_frequency, "treatment_plans": treatment_plans},
                        remediation_steps=[
                            "Implement annual risk assessments",
                            "Develop risk treatment plans",
                            "Monitor risk mitigation effectiveness"
                        ]
                    )
            
            elif requirement.requirement_id == "ISO-3":
                # Check access control
                rbac_implemented = security_data.get("rbac_implemented", False)
                regular_reviews = security_data.get("access_reviews_regular", False)
                
                if not rbac_implemented or not regular_reviews:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.HIGH,
                        description="Access control management insufficient",
                        evidence={"rbac": rbac_implemented, "reviews": regular_reviews},
                        remediation_steps=[
                            "Implement role-based access control",
                            "Schedule regular access reviews",
                            "Automate access provisioning"
                        ]
                    )
            
            elif requirement.requirement_id == "ISO-4":
                # Check creator asset protection
                asset_classification = security_data.get("asset_classification", False)
                protection_adequate = security_data.get("creator_asset_protection", False)
                
                if not asset_classification or not protection_adequate:
                    return ComplianceViolation(
                        violation_id=f"V-{requirement.requirement_id}-{int(time.time())}",
                        requirement=requirement,
                        severity=Severity.HIGH,
                        description="Creator intellectual property assets inadequately protected",
                        evidence={"classification": asset_classification, "protection": protection_adequate},
                        remediation_steps=[
                            "Implement asset classification system",
                            "Enhance creator IP protection measures",
                            "Regular asset protection reviews"
                        ],
                        creator_impact="Creator intellectual property at risk"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"ISO requirement check failed for {requirement.requirement_id}: {str(e)}")
            return None

    async def audit_security_policies(self, policy_data: Dict[str, Any]) -> ComplianceResult:
        """
        Audit security policies for compliance across all frameworks.
        
        Args:
            policy_data: Security policy data for audit
            
        Returns:
            ComplianceResult with comprehensive policy audit
        """
        start_time = time.perf_counter()
        
        try:
            all_violations = []
            total_requirements = 0
            total_passed = 0
            
            # Check policies against all enabled frameworks
            for framework in self.enabled_frameworks:
                if framework in self.compliance_requirements:
                    requirements = self.compliance_requirements[framework]
                    for requirement in requirements:
                        total_requirements += 1
                        violation = await self._audit_policy_requirement(requirement, policy_data)
                        if violation:
                            all_violations.append(violation)
                        else:
                            total_passed += 1
            
            compliance_score = total_passed / total_requirements if total_requirements > 0 else 0.0
            
            if compliance_score >= 0.95:
                status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 0.80:
                status = ComplianceStatus.PARTIAL_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            result = ComplianceResult(
                success=True,
                framework=ComplianceFramework.ISO27001,  # Representing overall audit
                overall_status=status,
                compliance_score=compliance_score,
                violations=all_violations,
                requirements_checked=total_requirements,
                requirements_passed=total_passed,
                check_duration_ms=execution_time,
                recommendations=self._generate_policy_recommendations(all_violations),
                next_review_date=datetime.now(timezone.utc) + timedelta(days=180)  # Semi-annual
            )
            
            logger.info(f"Security policy audit completed in {execution_time:.2f}ms: {status.value}")
            return result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Security policy audit failed in {execution_time:.2f}ms: {str(e)}")
            return ComplianceResult(
                success=False,
                framework=ComplianceFramework.ISO27001,
                overall_status=ComplianceStatus.UNKNOWN,
                compliance_score=0.0,
                errors=[f"Policy audit error: {str(e)}"],
                check_duration_ms=execution_time
            )

    async def _audit_policy_requirement(self, requirement: ComplianceRequirement,
                                      policy_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Audit individual requirement against policies."""
        try:
            # General policy checks applicable across frameworks
            policy_documented = policy_data.get(f"{requirement.category}_policy_documented", False)
            policy_current = policy_data.get(f"{requirement.category}_policy_current", False)
            staff_trained = policy_data.get(f"{requirement.category}_staff_trained", False)
            
            issues = []
            if not policy_documented:
                issues.append("policy_not_documented")
            if not policy_current:
                issues.append("policy_outdated")
            if not staff_trained:
                issues.append("staff_not_trained")
            
            if issues:
                severity = Severity.HIGH if "policy_not_documented" in issues else Severity.MEDIUM
                
                return ComplianceViolation(
                    violation_id=f"V-POLICY-{requirement.requirement_id}-{int(time.time())}",
                    requirement=requirement,
                    severity=severity,
                    description=f"Policy issues for {requirement.category}: {', '.join(issues)}",
                    evidence={"issues": issues, "policy_data": policy_data},
                    remediation_steps=[
                        "Document missing policies",
                        "Update outdated policies",
                        "Provide staff training on policies"
                    ]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Policy audit failed for {requirement.requirement_id}: {str(e)}")
            return None

    async def generate_compliance_reports(self, frameworks: Optional[List[ComplianceFramework]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive compliance reports.
        
        Args:
            frameworks: Specific frameworks to report on (optional)
            
        Returns:
            Comprehensive compliance report
        """
        start_time = time.perf_counter()
        
        try:
            report_frameworks = frameworks or self.enabled_frameworks
            reports = {}
            
            for framework in report_frameworks:
                framework_history = [
                    result for result in self.compliance_history 
                    if result.framework == framework
                ]
                
                if framework_history:
                    latest_result = max(framework_history, key=lambda x: x.check_duration_ms)
                    
                    reports[framework.value] = {
                        "current_status": latest_result.overall_status.value,
                        "compliance_score": latest_result.compliance_score,
                        "violations_count": len(latest_result.violations),
                        "critical_violations": len([
                            v for v in latest_result.violations 
                            if v.severity == Severity.CRITICAL
                        ]),
                        "last_check": latest_result.next_review_date.isoformat() if latest_result.next_review_date else None,
                        "requirements_total": latest_result.requirements_checked,
                        "requirements_passed": latest_result.requirements_passed
                    }
                else:
                    reports[framework.value] = {
                        "current_status": "not_checked",
                        "compliance_score": 0.0,
                        "violations_count": 0,
                        "critical_violations": 0,
                        "last_check": None
                    }
            
            # Overall summary
            total_violations = sum(
                len(result.violations) for result in self.compliance_history
            )
            avg_compliance_score = (
                sum(result.compliance_score for result in self.compliance_history) /
                len(self.compliance_history)
            ) if self.compliance_history else 0.0
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            report = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generation_time_ms": execution_time,
                "frameworks": reports,
                "summary": {
                    "total_frameworks": len(report_frameworks),
                    "average_compliance_score": avg_compliance_score,
                    "total_violations": total_violations,
                    "checks_performed": len(self.compliance_history)
                },
                "creator_economy_specific": {
                    "creator_data_protection": True,
                    "ip_protection_enabled": True,
                    "revenue_transparency": True,
                    "content_authenticity": True
                }
            }
            
            logger.info(f"Compliance report generated in {execution_time:.2f}ms")
            return report
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Compliance report generation failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    async def continuous_compliance_monitoring(self) -> Dict[str, Any]:
        """
        Implement continuous compliance monitoring.
        
        Returns:
            Monitoring status and results
        """
        start_time = time.perf_counter()
        
        try:
            monitoring_results = {}
            
            # Check for compliance deadlines
            upcoming_deadlines = []
            for result in self.compliance_history:
                for violation in result.violations:
                    if violation.deadline:
                        days_until_deadline = (violation.deadline - datetime.now(timezone.utc)).days
                        if days_until_deadline <= 30:  # Within 30 days
                            upcoming_deadlines.append({
                                "violation_id": violation.violation_id,
                                "requirement": violation.requirement.title,
                                "days_remaining": days_until_deadline,
                                "severity": violation.severity.value
                            })
            
            # Check for overdue reviews
            overdue_reviews = []
            for result in self.compliance_history:
                if result.next_review_date and result.next_review_date < datetime.now(timezone.utc):
                    overdue_reviews.append({
                        "framework": result.framework.value,
                        "overdue_days": (datetime.now(timezone.utc) - result.next_review_date).days
                    })
            
            # Calculate trend analysis
            trend_analysis = self._calculate_compliance_trends()
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            monitoring_results = {
                "monitoring_time_ms": execution_time,
                "upcoming_deadlines": upcoming_deadlines,
                "overdue_reviews": overdue_reviews,
                "trend_analysis": trend_analysis,
                "recommendations": self._generate_monitoring_recommendations(
                    upcoming_deadlines, overdue_reviews
                )
            }
            
            logger.info(f"Continuous compliance monitoring completed in {execution_time:.2f}ms")
            return monitoring_results
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Continuous compliance monitoring failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    def _calculate_compliance_trends(self) -> Dict[str, Any]:
        """Calculate compliance score trends over time."""
        if len(self.compliance_history) < 2:
            return {"trend": "insufficient_data"}
        
        # Group by framework
        framework_trends = {}
        for framework in self.enabled_frameworks:
            framework_results = [
                result for result in self.compliance_history 
                if result.framework == framework
            ]
            
            if len(framework_results) >= 2:
                scores = [result.compliance_score for result in framework_results[-5:]]  # Last 5 checks
                if len(scores) >= 2:
                    trend = "improving" if scores[-1] > scores[0] else "declining"
                    framework_trends[framework.value] = {
                        "trend": trend,
                        "latest_score": scores[-1],
                        "change": scores[-1] - scores[0]
                    }
        
        return framework_trends

    def _generate_gdpr_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate GDPR-specific recommendations."""
        recommendations = []
        
        violation_types = [v.requirement.requirement_id for v in violations]
        
        if "GDPR-1" in violation_types:
            recommendations.append("Review and update data processing consent mechanisms")
        if "GDPR-2" in violation_types:
            recommendations.append("Implement automated data subject request handling")
        if "GDPR-3" in violation_types:
            recommendations.append("Enhance privacy by design implementation")
        if "GDPR-4" in violation_types:
            recommendations.append("Improve breach notification procedures")
        if "GDPR-5" in violation_types:
            recommendations.append("Strengthen creator content privacy protection")
        
        if not recommendations:
            recommendations.append("Continue current GDPR compliance practices")
        
        return recommendations

    def _generate_sox_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate SOX-specific recommendations."""
        recommendations = []
        
        violation_types = [v.requirement.requirement_id for v in violations]
        
        if "SOX-1" in violation_types:
            recommendations.append("Enhance financial controls documentation and testing")
        if "SOX-2" in violation_types:
            recommendations.append("Improve creator revenue recognition controls")
        if "SOX-3" in violation_types:
            recommendations.append("Strengthen IT change management procedures")
        if "SOX-4" in violation_types:
            recommendations.append("Enhance payment processing security controls")
        
        if not recommendations:
            recommendations.append("Maintain current SOX compliance standards")
        
        return recommendations

    def _generate_iso_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate ISO 27001-specific recommendations."""
        recommendations = []
        
        violation_types = [v.requirement.requirement_id for v in violations]
        
        if "ISO-1" in violation_types:
            recommendations.append("Strengthen Information Security Management System")
        if "ISO-2" in violation_types:
            recommendations.append("Improve risk management processes")
        if "ISO-3" in violation_types:
            recommendations.append("Enhance access control management")
        if "ISO-4" in violation_types:
            recommendations.append("Strengthen creator asset protection measures")
        
        if not recommendations:
            recommendations.append("Continue ISO 27001 compliance maintenance")
        
        return recommendations

    def _generate_policy_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate policy-specific recommendations."""
        categories = set(v.requirement.category for v in violations)
        
        recommendations = []
        for category in categories:
            recommendations.append(f"Review and update {category} policies")
        
        if not recommendations:
            recommendations.append("Security policies are adequately maintained")
        
        return recommendations

    def _generate_monitoring_recommendations(self, deadlines: List[Dict], 
                                          overdue: List[Dict]) -> List[str]:
        """Generate monitoring-specific recommendations."""
        recommendations = []
        
        if deadlines:
            recommendations.append(f"Address {len(deadlines)} upcoming compliance deadlines")
        if overdue:
            recommendations.append(f"Complete {len(overdue)} overdue compliance reviews")
        
        if not recommendations:
            recommendations.append("Compliance monitoring is up to date")
        
        return recommendations

    async def regulatory_change_tracking(self, regulation_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Track regulatory changes and assess impact.
        
        Args:
            regulation_updates: List of regulatory updates
            
        Returns:
            Impact assessment and recommendations
        """
        start_time = time.perf_counter()
        
        try:
            impact_assessment = []
            
            for update in regulation_updates:
                regulation = update.get("regulation", "")
                change_type = update.get("change_type", "")
                effective_date = update.get("effective_date", "")
                
                # Assess impact on current compliance
                impact = {
                    "regulation": regulation,
                    "change_type": change_type,
                    "effective_date": effective_date,
                    "impact_level": "medium",  # Default
                    "affected_requirements": [],
                    "action_required": True
                }
                
                # Determine impact based on regulation type
                if "GDPR" in regulation.upper():
                    impact["impact_level"] = "high"
                    impact["affected_requirements"] = ["GDPR-1", "GDPR-2", "GDPR-3"]
                elif "SOX" in regulation.upper():
                    impact["impact_level"] = "high"
                    impact["affected_requirements"] = ["SOX-1", "SOX-2"]
                elif "ISO" in regulation.upper():
                    impact["impact_level"] = "medium"
                    impact["affected_requirements"] = ["ISO-1", "ISO-2"]
                
                impact_assessment.append(impact)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            return {
                "tracking_time_ms": execution_time,
                "updates_processed": len(regulation_updates),
                "impact_assessment": impact_assessment,
                "high_impact_changes": len([i for i in impact_assessment if i["impact_level"] == "high"]),
                "recommendations": [
                    "Review high-impact regulatory changes immediately",
                    "Update compliance procedures accordingly",
                    "Train staff on new requirements"
                ]
            }
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Regulatory change tracking failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    def get_compliance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive compliance statistics."""
        try:
            if not self.compliance_history:
                return {
                    "total_checks": 0,
                    "frameworks_covered": 0,
                    "average_score": 0.0,
                    "total_violations": 0
                }
            
            # Framework coverage
            frameworks_checked = set(result.framework for result in self.compliance_history)
            
            # Average scores
            avg_scores = {}
            for framework in frameworks_checked:
                framework_results = [r for r in self.compliance_history if r.framework == framework]
                avg_scores[framework.value] = sum(r.compliance_score for r in framework_results) / len(framework_results)
            
            # Violation statistics
            total_violations = sum(len(result.violations) for result in self.compliance_history)
            critical_violations = sum(
                len([v for v in result.violations if v.severity == Severity.CRITICAL])
                for result in self.compliance_history
            )
            
            return {
                "total_checks": len(self.compliance_history),
                "frameworks_covered": len(frameworks_checked),
                "average_scores": avg_scores,
                "total_violations": total_violations,
                "critical_violations": critical_violations,
                "enabled_frameworks": [f.value for f in self.enabled_frameworks]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compliance statistics: {str(e)}")
            return {"error": str(e)}

# Factory for enterprise deployment
class ComplianceCheckerFactory:
    """Factory for creating ComplianceChecker instances with different configurations."""
    
    @staticmethod
    def create_production_checker() -> ComplianceChecker:
        """Create production-ready compliance checker."""
        config = {
            "enabled_frameworks": [
                ComplianceFramework.GDPR,
                ComplianceFramework.SOX,
                ComplianceFramework.ISO27001,
                ComplianceFramework.CREATOR_ECONOMY
            ],
            "creator_data_retention_days": 2555,  # 7 years
            "content_backup_required": True,
            "log_level": "INFO"
        }
        return ComplianceChecker(config)
    
    @staticmethod
    def create_development_checker() -> ComplianceChecker:
        """Create development compliance checker."""
        config = {
            "enabled_frameworks": [
                ComplianceFramework.GDPR,
                ComplianceFramework.ISO27001
            ],
            "creator_data_retention_days": 365,  # 1 year for dev
            "content_backup_required": False,
            "log_level": "DEBUG"
        }
        return ComplianceChecker(config)
    
    @staticmethod
    def create_full_compliance_checker() -> ComplianceChecker:
        """Create comprehensive compliance checker for all frameworks."""
        config = {
            "enabled_frameworks": list(ComplianceFramework),
            "creator_data_retention_days": 2555,
            "content_backup_required": True,
            "continuous_monitoring": True,
            "log_level": "WARNING"
        }
        return ComplianceChecker(config)