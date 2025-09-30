"""🔒 Compliance Analytics - Enterprise Regulatory Intelligence Engine
===================================================================

Advanced compliance monitoring and regulatory analytics for Creator Economy Platform.
GDPR, PCI DSS, SOX compliance tracking with real-time violation detection.

Performance Targets: < 100ms compliance checks
Enterprise regulatory compliance with automated reporting and audit trails.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from decimal import Decimal
from collections import defaultdict, deque
import hashlib
import uuid
import structlog

logger = structlog.get_logger(__name__)

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"                    # General Data Protection Regulation
    CCPA = "ccpa"                    # California Consumer Privacy Act
    PCI_DSS = "pci_dss"              # Payment Card Industry Data Security Standard
    SOX = "sox"                      # Sarbanes-Oxley Act
    HIPAA = "hipaa"                  # Health Insurance Portability and Accountability Act
    ISO_27001 = "iso_27001"          # Information Security Management
    SOC_2 = "soc_2"                  # Service Organization Control 2
    PSD2 = "psd2"                    # Payment Services Directive 2
    AML = "aml"                      # Anti-Money Laundering
    KYC = "kyc"                      # Know Your Customer

class ViolationType(Enum):
    """Types of compliance violations"""
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_RETENTION = "data_retention"
    CONSENT_VIOLATION = "consent_violation"
    ENCRYPTION_FAILURE = "encryption_failure"
    AUDIT_TRAIL_MISSING = "audit_trail_missing"
    FINANCIAL_REPORTING = "financial_reporting"
    TRANSACTION_MONITORING = "transaction_monitoring"
    IDENTITY_VERIFICATION = "identity_verification"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"

class RiskLevel(Enum):
    """Risk assessment levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    framework: ComplianceFramework
    violation_type: ViolationType
    severity: RiskLevel
    description: str
    detected_at: datetime
    affected_entities: List[str]
    remediation_actions: List[str]
    deadline: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ComplianceRequirement:
    """Compliance requirement definition"""
    requirement_id: str
    framework: ComplianceFramework
    title: str
    description: str
    mandatory: bool
    controls: List[str]
    validation_rules: List[str]
    frequency: str  # "daily", "weekly", "monthly", "quarterly", "annually"
    last_checked: Optional[datetime] = None
    status: ComplianceStatus = ComplianceStatus.UNDER_REVIEW

@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    result: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""
    report_id: str
    framework: ComplianceFramework
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    overall_status: ComplianceStatus
    compliance_score: float
    violations: List[ComplianceViolation]
    requirements_status: Dict[str, ComplianceStatus]
    risk_assessment: Dict[RiskLevel, int]
    recommendations: List[str]
    next_review_date: datetime

class ComplianceMonitor:
    """Core compliance monitoring engine"""
    
    def __init__(self):
        self.violation_history = deque(maxlen=10000)
        self.compliance_requirements = self._initialize_requirements()
        self.active_violations = {}
        
    def _initialize_requirements(self) -> Dict[ComplianceFramework, List[ComplianceRequirement]]:
        """Initialize compliance requirements for each framework"""
        requirements = {
            ComplianceFramework.GDPR: [
                ComplianceRequirement(
                    requirement_id="gdpr_001",
                    framework=ComplianceFramework.GDPR,
                    title="Data Subject Consent",
                    description="Obtain explicit consent for data processing",
                    mandatory=True,
                    controls=["consent_management", "data_collection_logs"],
                    validation_rules=["consent_recorded", "consent_timestamp", "purpose_specified"],
                    frequency="daily"
                ),
                ComplianceRequirement(
                    requirement_id="gdpr_002",
                    framework=ComplianceFramework.GDPR,
                    title="Right to Erasure",
                    description="Process data deletion requests within 30 days",
                    mandatory=True,
                    controls=["deletion_workflow", "data_mapping"],
                    validation_rules=["deletion_completed_30_days", "confirmation_sent"],
                    frequency="weekly"
                ),
                ComplianceRequirement(
                    requirement_id="gdpr_003",
                    framework=ComplianceFramework.GDPR,
                    title="Data Breach Notification",
                    description="Report data breaches within 72 hours",
                    mandatory=True,
                    controls=["incident_response", "notification_system"],
                    validation_rules=["breach_detected", "notification_sent_72h"],
                    frequency="continuous"
                )
            ],
            ComplianceFramework.PCI_DSS: [
                ComplianceRequirement(
                    requirement_id="pci_001",
                    framework=ComplianceFramework.PCI_DSS,
                    title="Secure Network",
                    description="Install and maintain firewall configuration",
                    mandatory=True,
                    controls=["firewall_rules", "network_segmentation"],
                    validation_rules=["firewall_active", "rules_updated"],
                    frequency="daily"
                ),
                ComplianceRequirement(
                    requirement_id="pci_002",
                    framework=ComplianceFramework.PCI_DSS,
                    title="Data Encryption",
                    description="Encrypt cardholder data in transit and at rest",
                    mandatory=True,
                    controls=["encryption_at_rest", "encryption_in_transit"],
                    validation_rules=["data_encrypted", "key_management"],
                    frequency="continuous"
                ),
                ComplianceRequirement(
                    requirement_id="pci_003",
                    framework=ComplianceFramework.PCI_DSS,
                    title="Access Control",
                    description="Restrict access to cardholder data by business need",
                    mandatory=True,
                    controls=["access_controls", "user_authentication"],
                    validation_rules=["access_logged", "periodic_review"],
                    frequency="monthly"
                )
            ],
            ComplianceFramework.SOX: [
                ComplianceRequirement(
                    requirement_id="sox_001",
                    framework=ComplianceFramework.SOX,
                    title="Financial Controls",
                    description="Maintain adequate internal financial controls",
                    mandatory=True,
                    controls=["financial_reporting", "control_testing"],
                    validation_rules=["controls_documented", "testing_completed"],
                    frequency="quarterly"
                ),
                ComplianceRequirement(
                    requirement_id="sox_002",
                    framework=ComplianceFramework.SOX,
                    title="Audit Trail",
                    description="Maintain complete audit trails for financial transactions",
                    mandatory=True,
                    controls=["transaction_logging", "audit_retention"],
                    validation_rules=["trails_complete", "retention_compliant"],
                    frequency="daily"
                )
            ]
        }
        
        return requirements
    
    async def monitor_regulatory_compliance(
        self,
        framework: ComplianceFramework,
        data_sources: Dict[str, Any],
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Monitor regulatory compliance for specific framework"""
        try:
            start_time = time.perf_counter()
            
            # Get requirements for framework
            requirements = self.compliance_requirements.get(framework, [])
            
            # Check each requirement
            compliance_results = {}
            violations_detected = []
            
            for requirement in requirements:
                result = await self._check_requirement_compliance(
                    requirement, data_sources, time_window
                )
                compliance_results[requirement.requirement_id] = result
                
                if result["status"] != ComplianceStatus.COMPLIANT:
                    violation = await self._create_violation_record(
                        requirement, result, framework
                    )
                    violations_detected.append(violation)
            
            # Calculate overall compliance score
            compliance_score = await self._calculate_compliance_score(compliance_results)
            
            # Determine overall status
            overall_status = await self._determine_overall_status(compliance_results)
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                violations_detected, compliance_results
            )
            
            result = {
                "framework": framework.value,
                "monitoring_period": {
                    "start": (datetime.utcnow() - time_window).isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "overall_status": overall_status.value,
                "compliance_score": compliance_score,
                "requirements_checked": len(requirements),
                "violations_detected": len(violations_detected),
                "detailed_results": compliance_results,
                "violations": [
                    {
                        "violation_id": v.violation_id,
                        "type": v.violation_type.value,
                        "severity": v.severity.value,
                        "description": v.description
                    }
                    for v in violations_detected
                ],
                "recommendations": recommendations
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Regulatory compliance monitored",
                framework=framework.value,
                compliance_score=compliance_score,
                violations=len(violations_detected),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error monitoring regulatory compliance: {e}")
            raise
    
    async def _check_requirement_compliance(
        self,
        requirement: ComplianceRequirement,
        data_sources: Dict[str, Any],
        time_window: timedelta
    ) -> Dict[str, Any]:
        """Check compliance for a specific requirement"""
        try:
            # Simulate compliance checking based on requirement type
            if requirement.framework == ComplianceFramework.GDPR:
                return await self._check_gdpr_requirement(requirement, data_sources, time_window)
            elif requirement.framework == ComplianceFramework.PCI_DSS:
                return await self._check_pci_requirement(requirement, data_sources, time_window)
            elif requirement.framework == ComplianceFramework.SOX:
                return await self._check_sox_requirement(requirement, data_sources, time_window)
            else:
                return await self._check_generic_requirement(requirement, data_sources)
                
        except Exception as e:
            logger.error(f"Error checking requirement {requirement.requirement_id}: {e}")
            return {
                "status": ComplianceStatus.UNDER_REVIEW,
                "score": 0.0,
                "issues": [f"Error during compliance check: {str(e)}"],
                "checked_at": datetime.utcnow()
            }
    
    async def _check_gdpr_requirement(
        self,
        requirement: ComplianceRequirement,
        data_sources: Dict[str, Any],
        time_window: timedelta
    ) -> Dict[str, Any]:
        """Check GDPR-specific requirements"""
        issues = []
        score = 100.0
        
        if requirement.requirement_id == "gdpr_001":  # Data Subject Consent
            # Check consent records
            consent_data = data_sources.get("consent_records", [])
            
            if not consent_data:
                issues.append("No consent records found")
                score -= 50
            else:
                # Validate consent completeness
                for record in consent_data:
                    if not record.get("timestamp"):
                        issues.append("Consent record missing timestamp")
                        score -= 10
                    if not record.get("purpose"):
                        issues.append("Consent record missing purpose")
                        score -= 10
        
        elif requirement.requirement_id == "gdpr_002":  # Right to Erasure
            # Check deletion requests processing
            deletion_requests = data_sources.get("deletion_requests", [])
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            overdue_requests = [
                req for req in deletion_requests
                if req.get("created_at", datetime.utcnow()) < cutoff_date
                and not req.get("completed", False)
            ]
            
            if overdue_requests:
                issues.append(f"{len(overdue_requests)} deletion requests overdue")
                score -= len(overdue_requests) * 20
        
        elif requirement.requirement_id == "gdpr_003":  # Data Breach Notification
            # Check breach notification compliance
            breach_incidents = data_sources.get("breach_incidents", [])
            
            for incident in breach_incidents:
                breach_time = incident.get("detected_at", datetime.utcnow())
                notification_time = incident.get("notified_at")
                
                if notification_time:
                    time_diff = notification_time - breach_time
                    if time_diff > timedelta(hours=72):
                        issues.append(f"Breach notification delayed: {time_diff}")
                        score -= 30
                else:
                    issues.append("Breach incident without notification record")
                    score -= 50
        
        status = ComplianceStatus.COMPLIANT if score >= 95 else \
                ComplianceStatus.PARTIALLY_COMPLIANT if score >= 70 else \
                ComplianceStatus.NON_COMPLIANT
        
        return {
            "status": status,
            "score": max(0.0, score),
            "issues": issues,
            "checked_at": datetime.utcnow()
        }
    
    async def _check_pci_requirement(
        self,
        requirement: ComplianceRequirement,
        data_sources: Dict[str, Any],
        time_window: timedelta
    ) -> Dict[str, Any]:
        """Check PCI DSS-specific requirements"""
        issues = []
        score = 100.0
        
        if requirement.requirement_id == "pci_001":  # Secure Network
            # Check firewall status
            firewall_status = data_sources.get("firewall_status", {})
            
            if not firewall_status.get("active", False):
                issues.append("Firewall not active")
                score -= 50
            
            if not firewall_status.get("rules_updated_recently", False):
                issues.append("Firewall rules not recently updated")
                score -= 20
        
        elif requirement.requirement_id == "pci_002":  # Data Encryption
            # Check encryption status
            encryption_status = data_sources.get("encryption_status", {})
            
            if not encryption_status.get("data_at_rest_encrypted", False):
                issues.append("Data at rest not encrypted")
                score -= 40
            
            if not encryption_status.get("data_in_transit_encrypted", False):
                issues.append("Data in transit not encrypted")
                score -= 40
            
            if not encryption_status.get("key_management_compliant", False):
                issues.append("Key management not compliant")
                score -= 20
        
        elif requirement.requirement_id == "pci_003":  # Access Control
            # Check access control logs
            access_logs = data_sources.get("access_logs", [])
            
            recent_logs = [
                log for log in access_logs
                if log.get("timestamp", datetime.min) > datetime.utcnow() - time_window
            ]
            
            if not recent_logs:
                issues.append("No recent access logs found")
                score -= 30
            
            # Check for unauthorized access attempts
            failed_attempts = [
                log for log in recent_logs
                if log.get("result") == "failed"
            ]
            
            if len(failed_attempts) > 10:  # High number of failed attempts
                issues.append(f"High number of failed access attempts: {len(failed_attempts)}")
                score -= 20
        
        status = ComplianceStatus.COMPLIANT if score >= 95 else \
                ComplianceStatus.PARTIALLY_COMPLIANT if score >= 80 else \
                ComplianceStatus.NON_COMPLIANT
        
        return {
            "status": status,
            "score": max(0.0, score),
            "issues": issues,
            "checked_at": datetime.utcnow()
        }
    
    async def _check_sox_requirement(
        self,
        requirement: ComplianceRequirement,
        data_sources: Dict[str, Any],
        time_window: timedelta
    ) -> Dict[str, Any]:
        """Check SOX-specific requirements"""
        issues = []
        score = 100.0
        
        if requirement.requirement_id == "sox_001":  # Financial Controls
            # Check financial control documentation
            controls_status = data_sources.get("financial_controls", {})
            
            if not controls_status.get("documented", False):
                issues.append("Financial controls not properly documented")
                score -= 40
            
            if not controls_status.get("tested_quarterly", False):
                issues.append("Financial controls not tested quarterly")
                score -= 30
            
            if not controls_status.get("deficiencies_addressed", False):
                issues.append("Control deficiencies not addressed")
                score -= 30
        
        elif requirement.requirement_id == "sox_002":  # Audit Trail
            # Check audit trail completeness
            audit_data = data_sources.get("audit_trails", [])
            financial_transactions = data_sources.get("financial_transactions", [])
            
            # Check if all financial transactions have audit trails
            transactions_with_trails = set(
                trail.get("transaction_id") for trail in audit_data
            )
            
            all_transaction_ids = set(
                txn.get("transaction_id") for txn in financial_transactions
            )
            
            missing_trails = all_transaction_ids - transactions_with_trails
            if missing_trails:
                issues.append(f"{len(missing_trails)} transactions missing audit trails")
                score -= len(missing_trails) * 5  # 5 points per missing trail
            
            # Check audit trail retention
            old_cutoff = datetime.utcnow() - timedelta(days=7*365)  # 7 years
            recent_transactions = [
                txn for txn in financial_transactions
                if txn.get("timestamp", datetime.utcnow()) > old_cutoff
            ]
            
            if len(recent_transactions) != len(financial_transactions):
                issues.append("Some historical audit trails may be missing")
                score -= 10
        
        status = ComplianceStatus.COMPLIANT if score >= 95 else \
                ComplianceStatus.PARTIALLY_COMPLIANT if score >= 85 else \
                ComplianceStatus.NON_COMPLIANT
        
        return {
            "status": status,
            "score": max(0.0, score),
            "issues": issues,
            "checked_at": datetime.utcnow()
        }
    
    async def _check_generic_requirement(
        self,
        requirement: ComplianceRequirement,
        data_sources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check generic compliance requirement"""
        # Basic compliance check for unsupported frameworks
        score = 75.0  # Default partial compliance
        issues = ["Manual review required for this compliance framework"]
        
        return {
            "status": ComplianceStatus.PARTIALLY_COMPLIANT,
            "score": score,
            "issues": issues,
            "checked_at": datetime.utcnow()
        }
    
    async def _create_violation_record(
        self,
        requirement: ComplianceRequirement,
        check_result: Dict[str, Any],
        framework: ComplianceFramework
    ) -> ComplianceViolation:
        """Create violation record for non-compliant requirement"""
        violation_id = f"viol_{int(time.time())}_{requirement.requirement_id}"
        
        # Determine violation type based on requirement
        violation_type = self._map_requirement_to_violation_type(requirement)
        
        # Determine severity based on score
        score = check_result.get("score", 0)
        if score < 50:
            severity = RiskLevel.CRITICAL
        elif score < 70:
            severity = RiskLevel.HIGH
        elif score < 85:
            severity = RiskLevel.MEDIUM
        else:
            severity = RiskLevel.LOW
        
        # Generate remediation actions
        remediation_actions = await self._generate_remediation_actions(
            requirement, check_result
        )
        
        violation = ComplianceViolation(
            violation_id=violation_id,
            framework=framework,
            violation_type=violation_type,
            severity=severity,
            description=f"Non-compliance with {requirement.title}: {', '.join(check_result.get('issues', []))}",
            detected_at=datetime.utcnow(),
            affected_entities=[requirement.requirement_id],
            remediation_actions=remediation_actions,
            deadline=datetime.utcnow() + self._get_remediation_deadline(severity)
        )
        
        # Store violation
        self.active_violations[violation_id] = violation
        self.violation_history.append(violation)
        
        return violation
    
    def _map_requirement_to_violation_type(
        self,
        requirement: ComplianceRequirement
    ) -> ViolationType:
        """Map compliance requirement to violation type"""
        mapping = {
            "gdpr_001": ViolationType.CONSENT_VIOLATION,
            "gdpr_002": ViolationType.DATA_RETENTION,
            "gdpr_003": ViolationType.DATA_BREACH,
            "pci_001": ViolationType.UNAUTHORIZED_ACCESS,
            "pci_002": ViolationType.ENCRYPTION_FAILURE,
            "pci_003": ViolationType.UNAUTHORIZED_ACCESS,
            "sox_001": ViolationType.FINANCIAL_REPORTING,
            "sox_002": ViolationType.AUDIT_TRAIL_MISSING
        }
        
        return mapping.get(requirement.requirement_id, ViolationType.UNAUTHORIZED_ACCESS)
    
    async def _generate_remediation_actions(
        self,
        requirement: ComplianceRequirement,
        check_result: Dict[str, Any]
    ) -> List[str]:
        """Generate specific remediation actions"""
        actions = []
        issues = check_result.get("issues", [])
        
        # Framework-specific actions
        if requirement.framework == ComplianceFramework.GDPR:
            if any("consent" in issue.lower() for issue in issues):
                actions.extend([
                    "Implement proper consent management system",
                    "Update privacy policy and consent forms",
                    "Train staff on GDPR consent requirements"
                ])
            if any("deletion" in issue.lower() for issue in issues):
                actions.extend([
                    "Process pending deletion requests immediately",
                    "Implement automated deletion workflows",
                    "Update data retention policies"
                ])
        
        elif requirement.framework == ComplianceFramework.PCI_DSS:
            if any("firewall" in issue.lower() for issue in issues):
                actions.extend([
                    "Activate and configure firewall",
                    "Update firewall rules regularly",
                    "Implement network segmentation"
                ])
            if any("encryption" in issue.lower() for issue in issues):
                actions.extend([
                    "Implement end-to-end encryption",
                    "Update encryption algorithms",
                    "Strengthen key management practices"
                ])
        
        elif requirement.framework == ComplianceFramework.SOX:
            if any("control" in issue.lower() for issue in issues):
                actions.extend([
                    "Document all financial controls",
                    "Implement quarterly control testing",
                    "Address identified control deficiencies"
                ])
            if any("audit" in issue.lower() for issue in issues):
                actions.extend([
                    "Implement comprehensive audit logging",
                    "Ensure audit trail completeness",
                    "Update audit retention policies"
                ])
        
        # Generic actions if no specific ones identified
        if not actions:
            actions = [
                "Review and update compliance procedures",
                "Conduct staff training on compliance requirements",
                "Implement monitoring and alerting systems"
            ]
        
        return actions
    
    def _get_remediation_deadline(self, severity: RiskLevel) -> timedelta:
        """Get remediation deadline based on severity"""
        deadlines = {
            RiskLevel.CRITICAL: timedelta(days=1),
            RiskLevel.HIGH: timedelta(days=7),
            RiskLevel.MEDIUM: timedelta(days=30),
            RiskLevel.LOW: timedelta(days=90),
            RiskLevel.MINIMAL: timedelta(days=180)
        }
        
        return deadlines.get(severity, timedelta(days=30))
    
    async def _calculate_compliance_score(
        self,
        compliance_results: Dict[str, Dict[str, Any]]
    ) -> float:
        """Calculate overall compliance score"""
        if not compliance_results:
            return 0.0
        
        total_score = sum(
            result.get("score", 0) for result in compliance_results.values()
        )
        
        return total_score / len(compliance_results)
    
    async def _determine_overall_status(
        self,
        compliance_results: Dict[str, Dict[str, Any]]
    ) -> ComplianceStatus:
        """Determine overall compliance status"""
        statuses = [result.get("status") for result in compliance_results.values()]
        
        if all(status == ComplianceStatus.COMPLIANT for status in statuses):
            return ComplianceStatus.COMPLIANT
        elif any(status == ComplianceStatus.NON_COMPLIANT for status in statuses):
            return ComplianceStatus.NON_COMPLIANT
        elif any(status == ComplianceStatus.PARTIALLY_COMPLIANT for status in statuses):
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.UNDER_REVIEW
    
    async def _generate_compliance_recommendations(
        self,
        violations: List[ComplianceViolation],
        compliance_results: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        # Priority recommendations based on violations
        critical_violations = [v for v in violations if v.severity == RiskLevel.CRITICAL]
        if critical_violations:
            recommendations.append("Address critical compliance violations immediately")
        
        high_violations = [v for v in violations if v.severity == RiskLevel.HIGH]
        if high_violations:
            recommendations.append(f"Resolve {len(high_violations)} high-priority violations within 7 days")
        
        # Score-based recommendations
        avg_score = sum(
            result.get("score", 0) for result in compliance_results.values()
        ) / len(compliance_results) if compliance_results else 0
        
        if avg_score < 70:
            recommendations.extend([
                "Implement comprehensive compliance management system",
                "Conduct organization-wide compliance training",
                "Establish regular compliance monitoring procedures"
            ])
        elif avg_score < 90:
            recommendations.extend([
                "Fine-tune existing compliance procedures",
                "Implement automated compliance monitoring",
                "Regular review and update of compliance policies"
            ])
        
        return recommendations

class RegulatoryAnalyzer:
    """Advanced regulatory analysis engine"""
    
    def __init__(self):
        self.regulatory_data = {}
        self.analysis_cache = {}
        
    async def analyze_compliance_metrics(
        self,
        compliance_data: List[Dict[str, Any]],
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """Analyze compliance metrics across frameworks"""
        try:
            start_time = time.perf_counter()
            
            if not compliance_data:
                raise ValueError("No compliance data provided for analysis")
            
            # Analyze each framework
            framework_analysis = {}
            for framework in frameworks:
                framework_data = [
                    data for data in compliance_data
                    if data.get("framework") == framework.value
                ]
                
                if framework_data:
                    analysis = await self._analyze_framework_metrics(
                        framework, framework_data
                    )
                    framework_analysis[framework.value] = analysis
            
            # Cross-framework analysis
            cross_analysis = await self._perform_cross_framework_analysis(
                framework_analysis
            )
            
            # Trend analysis
            trend_analysis = await self._analyze_compliance_trends(compliance_data)
            
            # Risk assessment
            risk_assessment = await self._assess_regulatory_risks(
                framework_analysis, compliance_data
            )
            
            result = {
                "framework_analysis": framework_analysis,
                "cross_framework_analysis": cross_analysis,
                "trend_analysis": trend_analysis,
                "risk_assessment": risk_assessment,
                "overall_compliance_health": await self._calculate_compliance_health(
                    framework_analysis
                )
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Compliance metrics analyzed",
                frameworks_count=len(frameworks),
                data_points=len(compliance_data),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing compliance metrics: {e}")
            raise
    
    async def _analyze_framework_metrics(
        self,
        framework: ComplianceFramework,
        framework_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze metrics for specific compliance framework"""
        # Calculate key metrics
        total_checks = len(framework_data)
        compliant_checks = len([
            data for data in framework_data
            if data.get("status") == "compliant"
        ])
        
        compliance_rate = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Average compliance score
        scores = [data.get("score", 0) for data in framework_data if data.get("score")]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Violation analysis
        violations = [
            data for data in framework_data
            if data.get("violations_detected", 0) > 0
        ]
        
        total_violations = sum(
            data.get("violations_detected", 0) for data in framework_data
        )
        
        # Time-based analysis
        recent_data = [
            data for data in framework_data
            if data.get("timestamp", datetime.min) > datetime.utcnow() - timedelta(days=30)
        ]
        
        recent_compliance_rate = (
            len([d for d in recent_data if d.get("status") == "compliant"]) /
            len(recent_data) * 100
        ) if recent_data else 0
        
        return {
            "framework": framework.value,
            "compliance_rate": compliance_rate,
            "average_score": avg_score,
            "total_checks": total_checks,
            "total_violations": total_violations,
            "recent_compliance_rate": recent_compliance_rate,
            "trend": "improving" if recent_compliance_rate > compliance_rate else "declining" if recent_compliance_rate < compliance_rate else "stable"
        }
    
    async def _perform_cross_framework_analysis(
        self,
        framework_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform cross-framework compliance analysis"""
        if not framework_analysis:
            return {}
        
        # Compare compliance rates across frameworks
        compliance_rates = {
            framework: analysis.get("compliance_rate", 0)
            for framework, analysis in framework_analysis.items()
        }
        
        best_framework = max(compliance_rates.keys(), key=lambda k: compliance_rates[k])
        worst_framework = min(compliance_rates.keys(), key=lambda k: compliance_rates[k])
        
        # Calculate variance in compliance
        rates = list(compliance_rates.values())
        avg_rate = sum(rates) / len(rates)
        variance = sum((rate - avg_rate) ** 2 for rate in rates) / len(rates)
        
        # Identify common issues
        common_issues = await self._identify_common_compliance_issues(
            framework_analysis
        )
        
        return {
            "average_compliance_rate": avg_rate,
            "compliance_variance": variance,
            "best_performing_framework": best_framework,
            "worst_performing_framework": worst_framework,
            "frameworks_analyzed": len(framework_analysis),
            "common_issues": common_issues,
            "consistency_score": max(0, 100 - variance)  # Higher variance = lower consistency
        }
    
    async def _analyze_compliance_trends(
        self,
        compliance_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze compliance trends over time"""
        if not compliance_data:
            return {"trend": "insufficient_data"}
        
        # Sort data by timestamp
        sorted_data = sorted(
            compliance_data,
            key=lambda x: x.get("timestamp", datetime.min)
        )
        
        # Calculate monthly compliance rates
        monthly_rates = defaultdict(list)
        for data in sorted_data:
            timestamp = data.get("timestamp", datetime.utcnow())
            month_key = timestamp.strftime("%Y-%m")
            is_compliant = data.get("status") == "compliant"
            monthly_rates[month_key].append(is_compliant)
        
        # Calculate monthly averages
        monthly_averages = {
            month: sum(rates) / len(rates) * 100
            for month, rates in monthly_rates.items()
        }
        
        if len(monthly_averages) < 2:
            return {"trend": "insufficient_data_for_trend"}
        
        # Calculate trend
        months = sorted(monthly_averages.keys())
        recent_rate = monthly_averages[months[-1]]
        older_rate = monthly_averages[months[0]]
        
        trend_direction = "improving" if recent_rate > older_rate else "declining" if recent_rate < older_rate else "stable"
        trend_magnitude = abs(recent_rate - older_rate)
        
        return {
            "trend_direction": trend_direction,
            "trend_magnitude": trend_magnitude,
            "current_rate": recent_rate,
            "historical_rate": older_rate,
            "monthly_data": monthly_averages,
            "data_points": len(sorted_data)
        }
    
    async def _assess_regulatory_risks(
        self,
        framework_analysis: Dict[str, Any],
        compliance_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess regulatory compliance risks"""
        risks = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        risk_factors = []
        
        # Analyze framework-specific risks
        for framework, analysis in framework_analysis.items():
            compliance_rate = analysis.get("compliance_rate", 0)
            
            if compliance_rate < 70:
                risks["critical"] += 1
                risk_factors.append(f"Critical non-compliance in {framework}")
            elif compliance_rate < 85:
                risks["high"] += 1
                risk_factors.append(f"High compliance risk in {framework}")
            elif compliance_rate < 95:
                risks["medium"] += 1
                risk_factors.append(f"Medium compliance risk in {framework}")
            else:
                risks["low"] += 1
        
        # Calculate overall risk score
        risk_score = (
            risks["critical"] * 4 +
            risks["high"] * 3 +
            risks["medium"] * 2 +
            risks["low"] * 1
        )
        
        max_possible_risk = len(framework_analysis) * 4
        normalized_risk = (risk_score / max_possible_risk * 100) if max_possible_risk > 0 else 0
        
        # Determine risk level
        if normalized_risk > 75:
            overall_risk = "critical"
        elif normalized_risk > 50:
            overall_risk = "high"
        elif normalized_risk > 25:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        return {
            "overall_risk_level": overall_risk,
            "risk_score": normalized_risk,
            "risk_breakdown": risks,
            "risk_factors": risk_factors,
            "frameworks_at_risk": sum(risks["critical"], risks["high"])
        }
    
    async def _identify_common_compliance_issues(
        self,
        framework_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify common compliance issues across frameworks"""
        common_issues = []
        
        # Check for patterns in compliance rates
        low_compliance_frameworks = [
            framework for framework, analysis in framework_analysis.items()
            if analysis.get("compliance_rate", 0) < 80
        ]
        
        if len(low_compliance_frameworks) > 1:
            common_issues.append("Multiple frameworks showing low compliance rates")
        
        # Check for declining trends
        declining_frameworks = [
            framework for framework, analysis in framework_analysis.items()
            if analysis.get("trend") == "declining"
        ]
        
        if len(declining_frameworks) > 1:
            common_issues.append("Declining compliance trends across multiple frameworks")
        
        # Check for high violation counts
        high_violation_frameworks = [
            framework for framework, analysis in framework_analysis.items()
            if analysis.get("total_violations", 0) > 5
        ]
        
        if len(high_violation_frameworks) > 1:
            common_issues.append("High violation counts across multiple frameworks")
        
        return common_issues
    
    async def _calculate_compliance_health(
        self,
        framework_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall compliance health score"""
        if not framework_analysis:
            return {"health_score": 0, "status": "unknown"}
        
        # Calculate weighted average compliance rate
        total_weight = 0
        weighted_score = 0
        
        # Framework weights (some frameworks are more critical)
        framework_weights = {
            "gdpr": 1.5,  # Higher weight for GDPR
            "pci_dss": 1.3,  # High weight for PCI DSS
            "sox": 1.2,  # High weight for SOX
            "ccpa": 1.1,
            "hipaa": 1.0,
            "iso_27001": 0.9,
            "soc_2": 0.8,
            "psd2": 0.7,
            "aml": 0.6,
            "kyc": 0.5
        }
        
        for framework, analysis in framework_analysis.items():
            weight = framework_weights.get(framework, 1.0)
            compliance_rate = analysis.get("compliance_rate", 0)
            weighted_score += compliance_rate * weight
            total_weight += weight
        
        health_score = weighted_score / total_weight if total_weight > 0 else 0
        
        # Determine health status
        if health_score >= 95:
            status = "excellent"
        elif health_score >= 85:
            status = "good"
        elif health_score >= 70:
            status = "fair"
        elif health_score >= 50:
            status = "poor"
        else:
            status = "critical"
        
        return {
            "health_score": health_score,
            "status": status,
            "frameworks_evaluated": len(framework_analysis),
            "weighted_calculation": True
        }

class AuditManager:
    """Comprehensive audit management and trail system"""
    
    def __init__(self):
        self.audit_events = deque(maxlen=100000)  # Large audit trail
        self.audit_policies = {}
        
    async def maintain_compliance_history(
        self,
        compliance_events: List[Dict[str, Any]],
        retention_policy: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Maintain comprehensive compliance history"""
        try:
            start_time = time.perf_counter()
            
            retention_policy = retention_policy or {
                "default_retention_days": 2555,  # 7 years default
                "critical_events_retention_days": 3650,  # 10 years for critical
                "framework_specific": {
                    "sox": 2555,  # 7 years for SOX
                    "gdpr": 1095,  # 3 years for GDPR
                    "pci_dss": 365  # 1 year for PCI DSS
                }
            }
            
            # Process and categorize events
            processed_events = []
            retention_summary = defaultdict(int)
            
            for event in compliance_events:
                processed_event = await self._process_compliance_event(
                    event, retention_policy
                )
                processed_events.append(processed_event)
                
                # Update retention summary
                retention_days = processed_event.get("retention_days", 0)
                retention_summary[f"{retention_days}_days"] += 1
            
            # Store events in audit trail
            for event in processed_events:
                audit_event = AuditEvent(
                    event_id=event.get("event_id", str(uuid.uuid4())),
                    timestamp=event.get("timestamp", datetime.utcnow()),
                    user_id=event.get("user_id", "system"),
                    action=event.get("action", "compliance_check"),
                    resource=event.get("resource", "compliance_system"),
                    result=event.get("result", "completed"),
                    metadata=event
                )
                self.audit_events.append(audit_event)
            
            # Generate compliance history report
            history_report = await self._generate_history_report(processed_events)
            
            result = {
                "events_processed": len(processed_events),
                "retention_summary": dict(retention_summary),
                "retention_policy_applied": retention_policy,
                "history_report": history_report,
                "audit_trail_size": len(self.audit_events)
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Compliance history maintained",
                events_processed=len(processed_events),
                audit_trail_size=len(self.audit_events),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error maintaining compliance history: {e}")
            raise
    
    async def _process_compliance_event(
        self,
        event: Dict[str, Any],
        retention_policy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process individual compliance event"""
        # Determine retention period
        framework = event.get("framework", "default")
        event_type = event.get("type", "standard")
        
        # Get framework-specific retention
        framework_retention = retention_policy.get("framework_specific", {})
        retention_days = framework_retention.get(
            framework,
            retention_policy.get("default_retention_days", 2555)
        )
        
        # Adjust for critical events
        if event_type in ["violation", "breach", "critical"]:
            retention_days = max(
                retention_days,
                retention_policy.get("critical_events_retention_days", 3650)
            )
        
        # Add metadata
        processed_event = event.copy()
        processed_event.update({
            "retention_days": retention_days,
            "retention_until": datetime.utcnow() + timedelta(days=retention_days),
            "processed_at": datetime.utcnow(),
            "event_hash": hashlib.sha256(
                json.dumps(event, sort_keys=True).encode()
            ).hexdigest()
        })
        
        return processed_event
    
    async def _generate_history_report(
        self,
        processed_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate compliance history report"""
        if not processed_events:
            return {"status": "no_events"}
        
        # Categorize events by framework
        framework_counts = defaultdict(int)
        event_type_counts = defaultdict(int)
        
        for event in processed_events:
            framework = event.get("framework", "unknown")
            event_type = event.get("type", "unknown")
            
            framework_counts[framework] += 1
            event_type_counts[event_type] += 1
        
        # Calculate time ranges
        timestamps = [
            event.get("timestamp", datetime.utcnow())
            for event in processed_events
        ]
        
        earliest_event = min(timestamps)
        latest_event = max(timestamps)
        
        return {
            "total_events": len(processed_events),
            "framework_breakdown": dict(framework_counts),
            "event_type_breakdown": dict(event_type_counts),
            "time_range": {
                "earliest_event": earliest_event.isoformat(),
                "latest_event": latest_event.isoformat(),
                "span_days": (latest_event - earliest_event).days
            },
            "retention_summary": {
                "average_retention_days": sum(
                    event.get("retention_days", 0) for event in processed_events
                ) / len(processed_events),
                "max_retention_days": max(
                    event.get("retention_days", 0) for event in processed_events
                ),
                "min_retention_days": min(
                    event.get("retention_days", 0) for event in processed_events
                )
            }
        }

class ComplianceAnalytics:
    """Main compliance analytics orchestrator"""
    
    def __init__(self):
        self.compliance_monitor = ComplianceMonitor()
        self.regulatory_analyzer = RegulatoryAnalyzer()
        self.audit_manager = AuditManager()
        
    async def monitor_regulatory_compliance(
        self,
        framework: ComplianceFramework,
        data_sources: Dict[str, Any],
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Main entry point for regulatory compliance monitoring"""
        return await self.compliance_monitor.monitor_regulatory_compliance(
            framework, data_sources, time_window
        )
    
    async def analyze_compliance_metrics(
        self,
        compliance_data: List[Dict[str, Any]],
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """Analyze compliance metrics across frameworks"""
        return await self.regulatory_analyzer.analyze_compliance_metrics(
            compliance_data, frameworks
        )
    
    async def generate_compliance_reports(
        self,
        frameworks: List[ComplianceFramework],
        period_start: datetime,
        period_end: datetime,
        data_sources: Dict[str, Any]
    ) -> Dict[str, ComplianceReport]:
        """Generate comprehensive compliance reports"""
        try:
            start_time = time.perf_counter()
            
            reports = {}
            
            for framework in frameworks:
                # Monitor compliance for the period
                compliance_result = await self.monitor_regulatory_compliance(
                    framework, data_sources, period_end - period_start
                )
                
                # Generate report
                report = ComplianceReport(
                    report_id=f"report_{framework.value}_{int(time.time())}",
                    framework=framework,
                    generated_at=datetime.utcnow(),
                    period_start=period_start,
                    period_end=period_end,
                    overall_status=ComplianceStatus(compliance_result["overall_status"]),
                    compliance_score=compliance_result["compliance_score"],
                    violations=[],  # Would be populated from compliance_result
                    requirements_status={},  # Would be populated from detailed_results
                    risk_assessment={},  # Would be calculated
                    recommendations=compliance_result["recommendations"],
                    next_review_date=datetime.utcnow() + timedelta(days=30)
                )
                
                reports[framework.value] = report
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Compliance reports generated",
                frameworks_count=len(frameworks),
                duration_ms=duration_ms
            )
            
            return reports
            
        except Exception as e:
            logger.error(f"Error generating compliance reports: {e}")
            raise
    
    async def track_audit_requirements(
        self,
        audit_events: List[Dict[str, Any]],
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """Track audit requirements across frameworks"""
        try:
            start_time = time.perf_counter()
            
            # Maintain compliance history
            history_result = await self.audit_manager.maintain_compliance_history(
                audit_events
            )
            
            # Analyze audit coverage
            audit_coverage = await self._analyze_audit_coverage(
                audit_events, frameworks
            )
            
            # Identify audit gaps
            audit_gaps = await self._identify_audit_gaps(
                audit_events, frameworks
            )
            
            result = {
                "compliance_history": history_result,
                "audit_coverage": audit_coverage,
                "audit_gaps": audit_gaps,
                "frameworks_tracked": [f.value for f in frameworks],
                "total_audit_events": len(audit_events)
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Audit requirements tracked",
                frameworks_count=len(frameworks),
                audit_events=len(audit_events),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error tracking audit requirements: {e}")
            raise
    
    async def _analyze_audit_coverage(
        self,
        audit_events: List[Dict[str, Any]],
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """Analyze audit coverage across frameworks"""
        coverage = {}
        
        for framework in frameworks:
            framework_events = [
                event for event in audit_events
                if event.get("framework") == framework.value
            ]
            
            required_controls = self.compliance_monitor.compliance_requirements.get(
                framework, []
            )
            
            covered_controls = set(
                event.get("control_id") for event in framework_events
                if event.get("control_id")
            )
            
            total_controls = len(required_controls)
            covered_count = len(covered_controls)
            
            coverage[framework.value] = {
                "total_controls": total_controls,
                "covered_controls": covered_count,
                "coverage_percentage": (covered_count / total_controls * 100) if total_controls > 0 else 0,
                "uncovered_controls": [
                    req.requirement_id for req in required_controls
                    if req.requirement_id not in covered_controls
                ]
            }
        
        return coverage
    
    async def _identify_audit_gaps(
        self,
        audit_events: List[Dict[str, Any]],
        frameworks: List[ComplianceFramework]
    ) -> List[Dict[str, Any]]:
        """Identify gaps in audit coverage"""
        gaps = []
        
        for framework in frameworks:
            required_controls = self.compliance_monitor.compliance_requirements.get(
                framework, []
            )
            
            framework_events = [
                event for event in audit_events
                if event.get("framework") == framework.value
            ]
            
            # Check for missing controls
            audited_controls = set(
                event.get("control_id") for event in framework_events
            )
            
            for requirement in required_controls:
                if requirement.requirement_id not in audited_controls:
                    gaps.append({
                        "framework": framework.value,
                        "missing_control": requirement.requirement_id,
                        "requirement_title": requirement.title,
                        "criticality": "high" if requirement.mandatory else "medium",
                        "recommended_action": f"Implement audit for {requirement.title}"
                    })
        
        return gaps

if __name__ == "__main__":
    # Enterprise testing and validation
    async def test_compliance_analytics():
        """Test compliance analytics functionality"""
        analytics = ComplianceAnalytics()
        
        # Test data sources
        test_data_sources = {
            "consent_records": [
                {"timestamp": datetime.utcnow(), "purpose": "payment_processing"},
                {"timestamp": datetime.utcnow(), "purpose": "marketing"}
            ],
            "deletion_requests": [
                {"created_at": datetime.utcnow() - timedelta(days=10), "completed": True}
            ],
            "breach_incidents": [],
            "firewall_status": {"active": True, "rules_updated_recently": True},
            "encryption_status": {
                "data_at_rest_encrypted": True,
                "data_in_transit_encrypted": True,
                "key_management_compliant": True
            },
            "access_logs": [
                {"timestamp": datetime.utcnow(), "result": "success"},
                {"timestamp": datetime.utcnow(), "result": "failed"}
            ],
            "financial_controls": {
                "documented": True,
                "tested_quarterly": True,
                "deficiencies_addressed": True
            },
            "audit_trails": [
                {"transaction_id": "txn_001", "timestamp": datetime.utcnow()}
            ],
            "financial_transactions": [
                {"transaction_id": "txn_001", "timestamp": datetime.utcnow()}
            ]
        }
        
        # Test GDPR compliance monitoring
        print("Testing GDPR compliance monitoring...")
        gdpr_result = await analytics.monitor_regulatory_compliance(
            ComplianceFramework.GDPR, test_data_sources
        )
        print(f"GDPR compliance score: {gdpr_result['compliance_score']:.1f}")
        print(f"GDPR status: {gdpr_result['overall_status']}")
        
        # Test PCI DSS compliance monitoring
        print("\nTesting PCI DSS compliance monitoring...")
        pci_result = await analytics.monitor_regulatory_compliance(
            ComplianceFramework.PCI_DSS, test_data_sources
        )
        print(f"PCI DSS compliance score: {pci_result['compliance_score']:.1f}")
        print(f"PCI DSS status: {pci_result['overall_status']}")
        
        # Test compliance metrics analysis
        print("\nTesting compliance metrics analysis...")
        compliance_data = [
            {
                "framework": "gdpr",
                "status": "compliant",
                "score": 95,
                "timestamp": datetime.utcnow(),
                "violations_detected": 0
            },
            {
                "framework": "pci_dss",
                "status": "partially_compliant",
                "score": 85,
                "timestamp": datetime.utcnow(),
                "violations_detected": 1
            }
        ]
        
        metrics_result = await analytics.analyze_compliance_metrics(
            compliance_data, [ComplianceFramework.GDPR, ComplianceFramework.PCI_DSS]
        )
        print(f"Overall compliance health: {metrics_result['overall_compliance_health']['status']}")
        
        # Test audit tracking
        print("\nTesting audit tracking...")
        audit_events = [
            {
                "framework": "gdpr",
                "type": "compliance_check",
                "control_id": "gdpr_001",
                "timestamp": datetime.utcnow()
            },
            {
                "framework": "pci_dss",
                "type": "security_review",
                "control_id": "pci_001",
                "timestamp": datetime.utcnow()
            }
        ]
        
        audit_result = await analytics.track_audit_requirements(
            audit_events, [ComplianceFramework.GDPR, ComplianceFramework.PCI_DSS]
        )
        print(f"Audit events processed: {audit_result['total_audit_events']}")
        
        print("\nCompliance analytics tests completed successfully!")
    
    # Run tests
    asyncio.run(test_compliance_analytics())