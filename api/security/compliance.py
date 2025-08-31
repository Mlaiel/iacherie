"""Compliance and Regulatory Module
Enterprise compliance management and regulatory framework for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform

Team Specialties:
- Lead AI Developer: Advanced machine learning and neural networks
- Senior Backend Developer: Enterprise-grade Python architecture
- ML Engineer: Deep learning and content analysis algorithms  
- Database Administrator: High-performance data management
- Security Expert: Cybersecurity and content protection
- Microservices Architect: Scalable distributed systems
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: CI/CD and cloud infrastructure deployment
- AI Prompt Engineer: LLM integration and optimization

⚠️  COPYRIGHT NOTICE - STRICTLY PROTECTED ⚠️
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
ANY UNAUTHORIZED USE, REPRODUCTION, DISTRIBUTION, OR THEFT OF THIS CODE
OR CONCEPT WITHOUT EXPLICIT WRITTEN PERMISSION IS STRICTLY FORBIDDEN.

Violators will face:
- Legal action under German and international copyright laws
- Criminal charges for intellectual property theft
- Financial penalties and damages claims
- Immediate cease and desist enforcement

Contact: mlaiel@live.de for any authorization requests.
"""import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import asyncio

from ..core.config import get_settings
from ..utils.cache import CacheManager
from ..utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ComplianceStandard(Enum):
    """Supported compliance standards"""    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    COPPA = "coppa"  # Children's Online Privacy Protection Act
    SOX = "sox"  # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    ISO27001 = "iso27001"  # Information Security Management
    SOC2 = "soc2"  # Service Organization Control 2
    DMCA = "dmca"  # Digital Millennium Copyright Act
    COPYRIGHT_EU = "copyright_eu"  # EU Copyright Directive


class ComplianceStatus(Enum):
    """Compliance status levels"""    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial_compliance"
    PENDING_REVIEW = "pending_review"
    UNDER_AUDIT = "under_audit"
    REMEDIATION_REQUIRED = "remediation_required"


class RiskLevel(Enum):
    """Risk assessment levels"""    NEGLIGIBLE = "negligible"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DataCategory(Enum):
    """Data categories for compliance"""    PERSONAL_DATA = "personal_data"
    SENSITIVE_DATA = "sensitive_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    CONTENT_DATA = "content_data"
    METADATA = "metadata"
    ANALYTICS_DATA = "analytics_data"


@dataclass
class ComplianceRule:
    """Individual compliance rule"""    rule_id: str = field(default_factory=lambda: secrets.token_hex(8))
    standard: ComplianceStandard = ComplianceStandard.GDPR
    rule_name: str = ""
    description: str = ""
    
    # Implementation details
    requirements: List[str] = field(default_factory=list)
    controls: List[str] = field(default_factory=list)
    data_categories: List[DataCategory] = field(default_factory=list)
    
    # Status and assessment
    status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    risk_level: RiskLevel = RiskLevel.MODERATE
    last_assessment: Optional[datetime] = None
    next_review: Optional[datetime] = None
    
    # Evidence and documentation
    evidence: Dict[str, Any] = field(default_factory=dict)
    documentation: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            "rule_id": self.rule_id,
            "standard": self.standard.value,
            "rule_name": self.rule_name,
            "description": self.description,
            "requirements": self.requirements,
            "controls": self.controls,
            "data_categories": [dc.value for dc in self.data_categories],
            "status": self.status.value,
            "risk_level": self.risk_level.value,
            "last_assessment": self.last_assessment.isoformat() if self.last_assessment else None,
            "next_review": self.next_review.isoformat() if self.next_review else None,
            "evidence": self.evidence,
            "documentation": self.documentation
        }


@dataclass
class ComplianceAudit:
    """Compliance audit record"""    audit_id: str = field(default_factory=lambda: secrets.token_hex(12))
    audit_type: str = "internal"
    standard: ComplianceStandard = ComplianceStandard.GDPR
    
    # Audit details
    audit_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    auditor: str = ""
    scope: List[str] = field(default_factory=list)
    
    # Results
    overall_status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    total_rules_checked: int = 0
    compliant_rules: int = 0
    non_compliant_rules: int = 0
    
    # Findings
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timeline
    completed_at: Optional[datetime] = None
    report_generated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            "audit_id": self.audit_id,
            "audit_type": self.audit_type,
            "standard": self.standard.value,
            "audit_date": self.audit_date.isoformat(),
            "auditor": self.auditor,
            "scope": self.scope,
            "overall_status": self.overall_status.value,
            "total_rules_checked": self.total_rules_checked,
            "compliant_rules": self.compliant_rules,
            "non_compliant_rules": self.non_compliant_rules,
            "compliance_rate": (self.compliant_rules / self.total_rules_checked * 100) if self.total_rules_checked > 0 else 0,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "action_items": self.action_items,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "report_generated_at": self.report_generated_at.isoformat() if self.report_generated_at else None
        }


@dataclass
class DataProcessingActivity:
    """Data processing activity for compliance tracking"""    activity_id: str = field(default_factory=lambda: secrets.token_hex(10))
    activity_name: str = ""
    description: str = ""
    
    # Data details
    data_categories: List[DataCategory] = field(default_factory=list)
    data_subjects: List[str] = field(default_factory=list)  # Types of people
    purposes: List[str] = field(default_factory=list)
    legal_basis: List[str] = field(default_factory=list)
    
    # Processing details
    controllers: List[str] = field(default_factory=list)
    processors: List[str] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    transfers: List[str] = field(default_factory=list)  # International transfers
    
    # Retention and security
    retention_period: Optional[str] = None
    security_measures: List[str] = field(default_factory=list)
    
    # Compliance status
    compliance_status: Dict[str, ComplianceStatus] = field(default_factory=dict)
    risk_assessment: Dict[str, RiskLevel] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceManager:
    """Enterprise compliance and regulatory management system"""    
    def __init__(self):
        self.cache = CacheManager()
        self.rules: Dict[str, ComplianceRule] = {}
        self.audits: Dict[str, ComplianceAudit] = {}
        self.activities: Dict[str, DataProcessingActivity] = {}
        self._setup_compliance_framework()
    
    def _setup_compliance_framework(self):
        """Initialize compliance framework with standard rules"""        # GDPR Rules
        self._setup_gdpr_rules()
        
        # CCPA Rules
        self._setup_ccpa_rules()
        
        # DMCA Rules
        self._setup_dmca_rules()
        
        # ISO 27001 Rules
        self._setup_iso27001_rules()
    
    def _setup_gdpr_rules(self):
        """Setup GDPR compliance rules"""        gdpr_rules = [
            {
                "rule_name": "Right to Information",
                "description": "Users must be informed about data collection and processing",
                "requirements": [
                    "Provide clear privacy policy",
                    "Explain data collection purposes",
                    "Identify legal basis for processing",
                    "Specify retention periods"
                ],
                "controls": [
                    "privacy_policy_display",
                    "consent_management",
                    "data_mapping"
                ],
                "data_categories": [DataCategory.PERSONAL_DATA, DataCategory.CONTENT_DATA]
            },
            {
                "rule_name": "Right to Access",
                "description": "Users can request access to their personal data",
                "requirements": [
                    "Provide data export functionality",
                    "Respond within 30 days",
                    "Verify identity before providing access"
                ],
                "controls": [
                    "data_export_api",
                    "identity_verification",
                    "access_logging"
                ],
                "data_categories": [DataCategory.PERSONAL_DATA, DataCategory.ANALYTICS_DATA]
            },
            {
                "rule_name": "Right to Erasure",
                "description": "Users can request deletion of their personal data",
                "requirements": [
                    "Implement secure deletion",
                    "Remove all copies and backups",
                    "Notify third parties of deletion requests"
                ],
                "controls": [
                    "secure_deletion_process",
                    "backup_management",
                    "third_party_notification"
                ],
                "data_categories": [DataCategory.PERSONAL_DATA]
            },
            {
                "rule_name": "Data Protection by Design",
                "description": "Privacy considerations built into system design",
                "requirements": [
                    "Privacy impact assessments",
                    "Data minimization principles",
                    "Purpose limitation"
                ],
                "controls": [
                    "privacy_impact_assessment",
                    "data_minimization_controls",
                    "purpose_validation"
                ],
                "data_categories": [dc for dc in DataCategory]
            }
        ]
        
        for rule_data in gdpr_rules:
            rule = ComplianceRule(
                standard=ComplianceStandard.GDPR,
                rule_name=rule_data["rule_name"],
                description=rule_data["description"],
                requirements=rule_data["requirements"],
                controls=rule_data["controls"],
                data_categories=[DataCategory(dc) for dc in rule_data["data_categories"]]
            )
            self.rules[rule.rule_id] = rule
    
    def _setup_ccpa_rules(self):
        """Setup CCPA compliance rules"""        ccpa_rules = [
            {
                "rule_name": "Right to Know",
                "description": "Consumers have right to know about personal information collection",
                "requirements": [
                    "Disclose categories of personal information",
                    "Identify sources of information",
                    "Explain business purposes"
                ],
                "controls": [
                    "privacy_notice",
                    "data_inventory",
                    "purpose_documentation"
                ],
                "data_categories": [DataCategory.PERSONAL_DATA]
            },
            {
                "rule_name": "Right to Delete",
                "description": "Consumers can request deletion of personal information",
                "requirements": [
                    "Verify consumer identity",
                    "Delete personal information",
                    "Direct service providers to delete"
                ],
                "controls": [
                    "identity_verification",
                    "deletion_process",
                    "vendor_management"
                ],
                "data_categories": [DataCategory.PERSONAL_DATA]
            }
        ]
        
        for rule_data in ccpa_rules:
            rule = ComplianceRule(
                standard=ComplianceStandard.CCPA,
                rule_name=rule_data["rule_name"],
                description=rule_data["description"],
                requirements=rule_data["requirements"],
                controls=rule_data["controls"],
                data_categories=[DataCategory.PERSONAL_DATA]
            )
            self.rules[rule.rule_id] = rule
    
    def _setup_dmca_rules(self):
        """Setup DMCA compliance rules"""        dmca_rules = [
            {
                "rule_name": "Notice and Takedown",
                "description": "Process for handling copyright takedown notices",
                "requirements": [
                    "Designate DMCA agent",
                    "Implement takedown process",
                    "Provide counter-notification process"
                ],
                "controls": [
                    "dmca_agent_registration",
                    "takedown_automation",
                    "counter_notice_handling"
                ],
                "data_categories": [DataCategory.CONTENT_DATA]
            },
            {
                "rule_name": "Safe Harbor Provisions",
                "description": "Qualify for DMCA safe harbor protections",
                "requirements": [
                    "Implement repeat infringer policy",
                    "Remove infringing content expeditiously",
                    "No actual knowledge of infringement"
                ],
                "controls": [
                    "repeat_infringer_tracking",
                    "content_monitoring",
                    "automated_removal"
                ],
                "data_categories": [DataCategory.CONTENT_DATA]
            }
        ]
        
        for rule_data in dmca_rules:
            rule = ComplianceRule(
                standard=ComplianceStandard.DMCA,
                rule_name=rule_data["rule_name"],
                description=rule_data["description"],
                requirements=rule_data["requirements"],
                controls=rule_data["controls"],
                data_categories=[DataCategory.CONTENT_DATA]
            )
            self.rules[rule.rule_id] = rule
    
    def _setup_iso27001_rules(self):
        """Setup ISO 27001 compliance rules"""        iso_rules = [
            {
                "rule_name": "Information Security Policy",
                "description": "Establish and maintain information security policy",
                "requirements": [
                    "Document security policy",
                    "Management approval",
                    "Regular review and updates"
                ],
                "controls": [
                    "policy_documentation",
                    "management_approval",
                    "policy_review_process"
                ],
                "data_categories": [dc for dc in DataCategory]
            },
            {
                "rule_name": "Risk Management",
                "description": "Identify and assess information security risks",
                "requirements": [
                    "Risk identification process",
                    "Risk assessment methodology",
                    "Risk treatment plans"
                ],
                "controls": [
                    "risk_register",
                    "risk_assessment_tools",
                    "treatment_tracking"
                ],
                "data_categories": [dc for dc in DataCategory]
            }
        ]
        
        for rule_data in iso_rules:
            rule = ComplianceRule(
                standard=ComplianceStandard.ISO27001,
                rule_name=rule_data["rule_name"],
                description=rule_data["description"],
                requirements=rule_data["requirements"],
                controls=rule_data["controls"],
                data_categories=[dc for dc in DataCategory]
            )
            self.rules[rule.rule_id] = rule
    
    async def assess_compliance(
        self,
        standard: ComplianceStandard,
        scope: Optional[List[str]] = None
    ) -> ComplianceAudit:
        """Perform comprehensive compliance assessment"""        try:
            # Create audit record
            audit = ComplianceAudit(
                audit_type="automated_assessment",
                standard=standard,
                auditor="system_automated",
                scope=scope or ["full_system"]
            )
            
            # Filter rules for the standard
            standard_rules = [
                rule for rule in self.rules.values()
                if rule.standard == standard
            ]
            
            audit.total_rules_checked = len(standard_rules)
            
            # Assess each rule
            for rule in standard_rules:
                assessment_result = await self._assess_rule_compliance(rule)
                
                if assessment_result["status"] == ComplianceStatus.COMPLIANT:
                    audit.compliant_rules += 1
                else:
                    audit.non_compliant_rules += 1
                    
                    # Add finding
                    finding = {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.rule_name,
                        "status": assessment_result["status"].value,
                        "risk_level": assessment_result["risk_level"].value,
                        "issues": assessment_result["issues"],
                        "recommendations": assessment_result["recommendations"]
                    }
                    audit.findings.append(finding)
            
            # Determine overall status
            compliance_rate = audit.compliant_rules / audit.total_rules_checked if audit.total_rules_checked > 0 else 0
            
            if compliance_rate >= 0.95:
                audit.overall_status = ComplianceStatus.COMPLIANT
            elif compliance_rate >= 0.80:
                audit.overall_status = ComplianceStatus.PARTIAL
            else:
                audit.overall_status = ComplianceStatus.NON_COMPLIANT
            
            # Generate recommendations
            audit.recommendations = self._generate_compliance_recommendations(audit)
            
            # Generate action items
            audit.action_items = self._generate_action_items(audit)
            
            # Complete audit
            audit.completed_at = datetime.now(timezone.utc)
            audit.report_generated_at = datetime.now(timezone.utc)
            
            # Store audit
            self.audits[audit.audit_id] = audit
            await self.cache.set(
                f"compliance_audit:{audit.audit_id}",
                audit.to_dict(),
                ttl=86400 * 30  # 30 days
            )
            
            logger.info(f"Compliance assessment completed: {audit.audit_id}")
            return audit
            
        except Exception as e:
            logger.error(f"Error assessing compliance: {str(e)}")
            raise
    
    async def _assess_rule_compliance(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Assess compliance for individual rule"""        try:
            assessment = {
                "status": ComplianceStatus.PENDING_REVIEW,
                "risk_level": RiskLevel.MODERATE,
                "issues": [],
                "recommendations": []
            }
            
            # Check each control
            compliant_controls = 0
            total_controls = len(rule.controls)
            
            for control in rule.controls:
                control_status = await self._check_control_implementation(control, rule)
                if control_status:
                    compliant_controls += 1
                else:
                    assessment["issues"].append(f"Control not implemented: {control}")
            
            # Determine status based on control implementation
            if total_controls == 0:
                assessment["status"] = ComplianceStatus.PENDING_REVIEW
            elif compliant_controls == total_controls:
                assessment["status"] = ComplianceStatus.COMPLIANT
                assessment["risk_level"] = RiskLevel.LOW
            elif compliant_controls >= total_controls * 0.7:
                assessment["status"] = ComplianceStatus.PARTIAL
                assessment["risk_level"] = RiskLevel.MODERATE
            else:
                assessment["status"] = ComplianceStatus.NON_COMPLIANT
                assessment["risk_level"] = RiskLevel.HIGH
            
            # Generate recommendations
            if assessment["status"] != ComplianceStatus.COMPLIANT:
                assessment["recommendations"] = [
                    f"Implement missing control: {control}"
                    for control in rule.controls
                    if not await self._check_control_implementation(control, rule)
                ]
            
            # Update rule status
            rule.status = assessment["status"]
            rule.risk_level = assessment["risk_level"]
            rule.last_assessment = datetime.now(timezone.utc)
            rule.next_review = datetime.now(timezone.utc) + timedelta(days=90)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing rule compliance: {str(e)}")
            return {
                "status": ComplianceStatus.PENDING_REVIEW,
                "risk_level": RiskLevel.HIGH,
                "issues": [f"Assessment error: {str(e)}"],
                "recommendations": ["Manual review required"]
            }
    
    async def _check_control_implementation(
        self,
        control: str,
        rule: ComplianceRule
    ) -> bool:
        """Check if a specific control is implemented"""        try:
            # This is a simplified implementation
            # In production, this would check actual system configurations
            
            implemented_controls = {
                "privacy_policy_display": True,
                "consent_management": True,
                "data_mapping": False,  # Example of missing control
                "data_export_api": True,
                "identity_verification": True,
                "access_logging": True,
                "secure_deletion_process": False,  # Example of missing control
                "backup_management": True,
                "third_party_notification": False,
                "privacy_impact_assessment": True,
                "data_minimization_controls": True,
                "purpose_validation": True,
                "dmca_agent_registration": True,
                "takedown_automation": True,
                "counter_notice_handling": False,
                "repeat_infringer_tracking": True,
                "content_monitoring": True,
                "automated_removal": True,
                "policy_documentation": True,
                "management_approval": True,
                "policy_review_process": True,
                "risk_register": False,
                "risk_assessment_tools": True,
                "treatment_tracking": False
            }
            
            return implemented_controls.get(control, False)
            
        except Exception as e:
            logger.error(f"Error checking control implementation: {str(e)}")
            return False
    
    def _generate_compliance_recommendations(self, audit: ComplianceAudit) -> List[str]:
        """Generate compliance recommendations based on audit results"""        recommendations = []
        
        try:
            compliance_rate = audit.compliant_rules / audit.total_rules_checked if audit.total_rules_checked > 0 else 0
            
            # General recommendations based on compliance rate
            if compliance_rate < 0.5:
                recommendations.append("Critical compliance gaps identified - immediate action required")
                recommendations.append("Consider engaging external compliance consultant")
                recommendations.append("Implement comprehensive compliance program")
            
            elif compliance_rate < 0.8:
                recommendations.append("Moderate compliance improvements needed")
                recommendations.append("Prioritize high-risk compliance gaps")
                recommendations.append("Establish regular compliance monitoring")
            
            else:
                recommendations.append("Good compliance posture - focus on continuous improvement")
                recommendations.append("Implement automated compliance monitoring")
            
            # Specific recommendations based on findings
            high_risk_findings = [f for f in audit.findings if f.get("risk_level") == "high"]
            if high_risk_findings:
                recommendations.append(f"Address {len(high_risk_findings)} high-risk compliance issues immediately")
            
            # Standard-specific recommendations
            if audit.standard == ComplianceStandard.GDPR:
                recommendations.append("Ensure all data processing activities are documented")
                recommendations.append("Implement privacy by design principles")
            
            elif audit.standard == ComplianceStandard.DMCA:
                recommendations.append("Register DMCA agent with copyright office")
                recommendations.append("Implement automated content monitoring")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Error generating recommendations - manual review required"]
    
    def _generate_action_items(self, audit: ComplianceAudit) -> List[Dict[str, Any]]:
        """Generate action items based on audit findings"""        action_items = []
        
        try:
            for finding in audit.findings:
                if finding.get("status") in ["non_compliant", "partial_compliance"]:
                    # Determine priority based on risk level
                    risk_level = finding.get("risk_level", "moderate")
                    if risk_level in ["critical", "high"]:
                        priority = "high"
                        due_days = 30
                    elif risk_level == "moderate":
                        priority = "medium"
                        due_days = 60
                    else:
                        priority = "low"
                        due_days = 90
                    
                    action_item = {
                        "action_id": secrets.token_hex(6),
                        "rule_id": finding["rule_id"],
                        "rule_name": finding["rule_name"],
                        "description": f"Address compliance gap in {finding['rule_name']}",
                        "priority": priority,
                        "assigned_to": "compliance_team",
                        "due_date": (datetime.now(timezone.utc) + timedelta(days=due_days)).isoformat(),
                        "status": "open",
                        "recommendations": finding.get("recommendations", [])
                    }
                    action_items.append(action_item)
            
            return action_items
            
        except Exception as e:
            logger.error(f"Error generating action items: {str(e)}")
            return []
    
    async def register_data_processing_activity(
        self,
        activity_name: str,
        description: str,
        data_categories: List[DataCategory],
        purposes: List[str],
        legal_basis: List[str]
    ) -> DataProcessingActivity:
        """Register new data processing activity"""        try:
            activity = DataProcessingActivity(
                activity_name=activity_name,
                description=description,
                data_categories=data_categories,
                purposes=purposes,
                legal_basis=legal_basis
            )
            
            # Assess compliance for each relevant standard
            for standard in [ComplianceStandard.GDPR, ComplianceStandard.CCPA]:
                activity.compliance_status[standard.value] = await self._assess_activity_compliance(
                    activity, standard
                )
                activity.risk_assessment[standard.value] = await self._assess_activity_risk(
                    activity, standard
                )
            
            # Store activity
            self.activities[activity.activity_id] = activity
            await self.cache.set(
                f"processing_activity:{activity.activity_id}",
                activity.__dict__,
                ttl=86400 * 30
            )
            
            logger.info(f"Data processing activity registered: {activity.activity_id}")
            return activity
            
        except Exception as e:
            logger.error(f"Error registering data processing activity: {str(e)}")
            raise
    
    async def _assess_activity_compliance(
        self,
        activity: DataProcessingActivity,
        standard: ComplianceStandard
    ) -> ComplianceStatus:
        """Assess compliance status for data processing activity"""        try:
            # Simplified compliance assessment
            compliance_score = 0
            total_checks = 0
            
            # Check legal basis
            if activity.legal_basis:
                compliance_score += 1
            total_checks += 1
            
            # Check purpose limitation
            if activity.purposes and len(activity.purposes) <= 3:  # Not too many purposes
                compliance_score += 1
            total_checks += 1
            
            # Check data minimization
            if len(activity.data_categories) <= 3:  # Limited data categories
                compliance_score += 1
            total_checks += 1
            
            # Determine status
            compliance_rate = compliance_score / total_checks if total_checks > 0 else 0
            
            if compliance_rate >= 0.9:
                return ComplianceStatus.COMPLIANT
            elif compliance_rate >= 0.7:
                return ComplianceStatus.PARTIAL
            else:
                return ComplianceStatus.NON_COMPLIANT
                
        except Exception as e:
            logger.error(f"Error assessing activity compliance: {str(e)}")
            return ComplianceStatus.PENDING_REVIEW
    
    async def _assess_activity_risk(
        self,
        activity: DataProcessingActivity,
        standard: ComplianceStandard
    ) -> RiskLevel:
        """Assess risk level for data processing activity"""        try:
            risk_score = 0
            
            # High-risk data categories
            high_risk_categories = [
                DataCategory.SENSITIVE_DATA,
                DataCategory.BIOMETRIC_DATA,
                DataCategory.HEALTH_DATA,
                DataCategory.FINANCIAL_DATA
            ]
            
            for category in activity.data_categories:
                if category in high_risk_categories:
                    risk_score += 2
                else:
                    risk_score += 1
            
            # International transfers increase risk
            if activity.transfers:
                risk_score += len(activity.transfers)
            
            # Determine risk level
            if risk_score >= 10:
                return RiskLevel.CRITICAL
            elif risk_score >= 7:
                return RiskLevel.HIGH
            elif risk_score >= 4:
                return RiskLevel.MODERATE
            elif risk_score >= 2:
                return RiskLevel.LOW
            else:
                return RiskLevel.NEGLIGIBLE
                
        except Exception as e:
            logger.error(f"Error assessing activity risk: {str(e)}")
            return RiskLevel.MODERATE
    
    async def generate_compliance_report(
        self,
        standards: Optional[List[ComplianceStandard]] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""        try:
            standards = standards or [
                ComplianceStandard.GDPR,
                ComplianceStandard.CCPA,
                ComplianceStandard.DMCA,
                ComplianceStandard.ISO27001
            ]
            
            report = {
                "report_id": secrets.token_hex(12),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "period_days": period_days,
                "standards_assessed": [s.value for s in standards],
                "overall_compliance": {},
                "by_standard": {},
                "risk_summary": {},
                "action_items": [],
                "recommendations": []
            }
            
            # Assess each standard
            total_compliant = 0
            total_rules = 0
            
            for standard in standards:
                standard_rules = [r for r in self.rules.values() if r.standard == standard]
                compliant_rules = [r for r in standard_rules if r.status == ComplianceStatus.COMPLIANT]
                
                standard_compliance = len(compliant_rules) / len(standard_rules) if standard_rules else 0
                
                report["by_standard"][standard.value] = {
                    "compliance_rate": standard_compliance,
                    "total_rules": len(standard_rules),
                    "compliant_rules": len(compliant_rules),
                    "non_compliant_rules": len(standard_rules) - len(compliant_rules),
                    "high_risk_rules": len([r for r in standard_rules if r.risk_level == RiskLevel.HIGH])
                }
                
                total_compliant += len(compliant_rules)
                total_rules += len(standard_rules)
            
            # Overall compliance
            overall_rate = total_compliant / total_rules if total_rules > 0 else 0
            report["overall_compliance"] = {
                "compliance_rate": overall_rate,
                "status": "compliant" if overall_rate >= 0.95 else "partial" if overall_rate >= 0.8 else "non_compliant",
                "total_rules": total_rules,
                "compliant_rules": total_compliant
            }
            
            # Risk summary
            risk_counts = {}
            for risk_level in RiskLevel:
                count = len([r for r in self.rules.values() if r.risk_level == risk_level])
                risk_counts[risk_level.value] = count
            
            report["risk_summary"] = risk_counts
            
            # Recent action items
            recent_audits = [
                audit for audit in self.audits.values()
                if audit.audit_date >= datetime.now(timezone.utc) - timedelta(days=period_days)
            ]
            
            for audit in recent_audits:
                report["action_items"].extend(audit.action_items)
            
            # Generate recommendations
            if overall_rate < 0.8:
                report["recommendations"].extend([
                    "Immediate compliance improvement program required",
                    "Conduct comprehensive risk assessment",
                    "Implement automated compliance monitoring"
                ])
            else:
                report["recommendations"].extend([
                    "Maintain current compliance posture",
                    "Regular compliance monitoring recommended",
                    "Consider third-party compliance validation"
                ])
            
            logger.info(f"Compliance report generated: {report['report_id']}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            raise


# Global compliance manager
compliance_manager = ComplianceManager()

# Export functions for easy import
async def assess_regulatory_compliance(
    standard: ComplianceStandard,
    scope: Optional[List[str]] = None
) -> ComplianceAudit:
    """Assess compliance with regulatory standard"""    return await compliance_manager.assess_compliance(standard, scope)

async def register_processing_activity(
    name: str,
    description: str,
    data_categories: List[DataCategory],
    purposes: List[str],
    legal_basis: List[str]
) -> DataProcessingActivity:
    """Register data processing activity"""    return await compliance_manager.register_data_processing_activity(
        name, description, data_categories, purposes, legal_basis
    )

async def generate_regulatory_report(
    standards: Optional[List[ComplianceStandard]] = None,
    period_days: int = 30
) -> Dict[str, Any]:
    """Generate compliance report"""    return await compliance_manager.generate_compliance_report(standards, period_days)
