"""
Regulatory Compliance Configuration Module
==========================================

Professional regulatory compliance configuration for financial services and content monetization.
Comprehensive compliance management for global regulations, data protection, and financial standards.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + FinTech Expert

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    # Financial Services
    PCI_DSS = "pci_dss"
    SOX = "sox"  # Sarbanes-Oxley
    MiFID_II = "mifid_ii"  # EU Markets in Financial Instruments Directive
    PSD2 = "psd2"  # EU Payment Services Directive
    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    
    # Anti-Money Laundering
    AML = "aml"
    KYC = "kyc"
    CDD = "cdd"  # Customer Due Diligence
    
    # International Sanctions
    OFAC = "ofac"  # Office of Foreign Assets Control
    EU_SANCTIONS = "eu_sanctions"
    UN_SANCTIONS = "un_sanctions"
    
    # Content & Copyright
    DMCA = "dmca"
    COPYRIGHT_DIRECTIVE = "copyright_directive"  # EU Copyright Directive
    SAFE_HARBOR = "safe_harbor"
    
    # Industry Standards
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"
    NIST = "nist"


class JurisdictionCode(str, Enum):
    """Legal jurisdictions for compliance."""
    # Major Markets
    UNITED_STATES = "US"
    EUROPEAN_UNION = "EU"
    GERMANY = "DE"
    UNITED_KINGDOM = "GB"
    FRANCE = "FR"
    ITALY = "IT"
    SPAIN = "ES"
    NETHERLANDS = "NL"
    CANADA = "CA"
    AUSTRALIA = "AU"
    JAPAN = "JP"
    SINGAPORE = "SG"
    SWITZERLAND = "CH"
    
    # Emerging Markets
    BRAZIL = "BR"
    INDIA = "IN"
    CHINA = "CN"
    SOUTH_KOREA = "KR"
    MEXICO = "MX"


class ComplianceRisk(str, Enum):
    """Compliance risk levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataClassification(str, Enum):
    """Data classification levels for compliance."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement configuration."""
    requirement_id: str
    framework: ComplianceFramework
    jurisdiction: JurisdictionCode
    title: str
    description: str
    mandatory: bool = True
    risk_level: ComplianceRisk = ComplianceRisk.MEDIUM
    
    # Implementation Details
    implementation_deadline: Optional[datetime] = None
    responsible_team: str = ""
    implementation_status: str = "not_started"  # not_started, in_progress, completed, failed
    last_assessment_date: Optional[datetime] = None
    next_assessment_date: Optional[datetime] = None
    
    # Evidence and Documentation
    documentation_required: bool = True
    audit_trail_required: bool = True
    evidence_retention_years: int = 7
    
    # Monitoring and Reporting
    continuous_monitoring: bool = False
    reporting_frequency: str = "quarterly"  # daily, weekly, monthly, quarterly, annually
    automated_reporting: bool = False
    
    # Penalties and Consequences
    penalty_amount_eur: Optional[Decimal] = None
    business_impact: str = "medium"  # low, medium, high, critical
    regulatory_action_risk: bool = False


@dataclass
class DataProtectionPolicy:
    """Data protection and privacy policy configuration."""
    policy_name: str
    applicable_frameworks: List[ComplianceFramework] = field(default_factory=list)
    
    # Data Collection
    consent_required: bool = True
    explicit_consent: bool = True
    consent_withdrawal: bool = True
    purpose_limitation: bool = True
    data_minimization: bool = True
    
    # Data Processing
    lawful_basis_required: bool = True
    processing_purposes: List[str] = field(default_factory=list)
    automated_decision_making: bool = False
    profiling_enabled: bool = False
    
    # Data Subject Rights
    right_to_access: bool = True
    right_to_rectification: bool = True
    right_to_erasure: bool = True
    right_to_portability: bool = True
    right_to_object: bool = True
    right_to_restrict: bool = True
    
    # Data Security
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    pseudonymization: bool = False
    anonymization: bool = False
    access_controls: bool = True
    audit_logging: bool = True
    
    # Data Retention
    retention_periods: Dict[DataClassification, int] = field(default_factory=dict)
    automatic_deletion: bool = True
    retention_schedule: bool = True
    
    # International Transfers
    adequacy_decisions: List[str] = field(default_factory=list)
    standard_contractual_clauses: bool = False
    binding_corporate_rules: bool = False
    
    # Breach Management
    breach_detection: bool = True
    breach_notification_hours: int = 72
    authority_notification: bool = True
    data_subject_notification: bool = True


@dataclass
class FinancialCompliancePolicy:
    """Financial services compliance policy configuration."""
    policy_name: str
    applicable_frameworks: List[ComplianceFramework] = field(default_factory=list)
    
    # Anti-Money Laundering (AML)
    customer_screening: bool = True
    transaction_monitoring: bool = True
    suspicious_activity_reporting: bool = True
    sanctions_screening: bool = True
    pep_screening: bool = True  # Politically Exposed Persons
    
    # Know Your Customer (KYC)
    identity_verification: bool = True
    address_verification: bool = True
    document_verification: bool = True
    biometric_verification: bool = False
    ongoing_monitoring: bool = True
    
    # Customer Due Diligence (CDD)
    simplified_due_diligence: bool = True
    standard_due_diligence: bool = True
    enhanced_due_diligence: bool = True
    
    # Transaction Limits and Monitoring
    daily_transaction_limits: Dict[str, Decimal] = field(default_factory=dict)
    monthly_limits: Dict[str, Decimal] = field(default_factory=dict)
    annual_limits: Dict[str, Decimal] = field(default_factory=dict)
    velocity_monitoring: bool = True
    pattern_analysis: bool = True
    
    # Reporting Requirements
    ctr_threshold: Decimal = Decimal("10000.00")  # Currency Transaction Report
    sar_required: bool = True  # Suspicious Activity Report
    regulatory_reporting: bool = True
    audit_trail: bool = True
    
    # Record Keeping
    transaction_records_years: int = 7
    customer_records_years: int = 7
    compliance_records_years: int = 10
    automated_record_keeping: bool = True


class RegulatoryComplianceConfig:
    """
    Professional regulatory compliance configuration.
    Comprehensive compliance management for global regulations and standards.
    """
    
    def __init__(self):
        """Initialize regulatory compliance configuration."""
        
        # Database Configuration
        self.COMPLIANCE_DB_URL = os.getenv(
            "COMPLIANCE_DB_URL",
            "postgresql://user:pass@localhost:5432/compliance_db"
        )
        
        # Document Management System
        self.DOCUMENT_STORAGE_URL = os.getenv("COMPLIANCE_DOCS_URL", "s3://compliance-documents/")
        self.AUDIT_TRAIL_STORAGE = os.getenv("AUDIT_STORAGE_URL", "s3://audit-trails/")
        
        # General Configuration
        self.ENABLE_COMPLIANCE_MONITORING = True
        self.ENABLE_AUTOMATED_REPORTING = True
        self.ENABLE_REAL_TIME_ALERTS = True
        self.ENABLE_AUDIT_LOGGING = True
        
        # Compliance Requirements
        self.COMPLIANCE_REQUIREMENTS = self._initialize_compliance_requirements()
        
        # Data Protection Policies
        self.DATA_PROTECTION_POLICIES = self._initialize_data_protection_policies()
        
        # Financial Compliance Policies
        self.FINANCIAL_COMPLIANCE_POLICIES = self._initialize_financial_policies()
        
        # Jurisdictional Configuration
        self.JURISDICTIONAL_CONFIG = self._initialize_jurisdictional_config()
        
        # Risk Management
        self.RISK_MANAGEMENT_CONFIG = {
            "risk_assessment_frequency": "quarterly",
            "automated_risk_scoring": True,
            "risk_threshold_alerts": True,
            "mitigation_tracking": True,
            "board_reporting": True,
            "third_party_risk_assessment": True
        }
        
        # Audit and Assessment
        self.AUDIT_CONFIG = {
            "internal_audit_enabled": True,
            "external_audit_required": True,
            "continuous_auditing": True,
            "audit_scheduling": "risk_based",
            "audit_trail_immutable": True,
            "audit_evidence_retention_years": 10
        }
        
        # Training and Awareness
        self.TRAINING_CONFIG = {
            "mandatory_compliance_training": True,
            "training_frequency": "annual",
            "role_based_training": True,
            "compliance_certification": True,
            "awareness_campaigns": True,
            "training_effectiveness_tracking": True
        }
        
        # Incident Management
        self.INCIDENT_CONFIG = {
            "incident_reporting_system": True,
            "automated_incident_detection": True,
            "incident_classification": True,
            "escalation_procedures": True,
            "regulatory_notification": True,
            "incident_investigation": True,
            "lessons_learned": True
        }
        
        # Technology and Infrastructure
        self.TECHNOLOGY_CONFIG = {
            "compliance_management_platform": True,
            "regulatory_change_management": True,
            "policy_management_system": True,
            "workflow_automation": True,
            "dashboard_reporting": True,
            "api_integrations": True
        }
    
    def _initialize_compliance_requirements(self) -> List[ComplianceRequirement]:
        """Initialize comprehensive compliance requirements."""



        return [
            # PCI DSS Requirements
            ComplianceRequirement(
                requirement_id="PCI_DSS_001",
                framework=ComplianceFramework.PCI_DSS,
                jurisdiction=JurisdictionCode.UNITED_STATES,
                title="Install and maintain network security controls",
                description="Implement and maintain network security controls to protect cardholder data",
                risk_level=ComplianceRisk.CRITICAL,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=True,
                penalty_amount_eur=Decimal("500000.00")
            ),
            
            ComplianceRequirement(
                requirement_id="PCI_DSS_002",
                framework=ComplianceFramework.PCI_DSS,
                jurisdiction=JurisdictionCode.UNITED_STATES,
                title="Apply secure configurations to all system components",
                description="Remove vendor-supplied defaults and other security parameters",
                risk_level=ComplianceRisk.HIGH,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=True
            ),
            
            # GDPR Requirements
            ComplianceRequirement(
                requirement_id="GDPR_001",
                framework=ComplianceFramework.GDPR,
                jurisdiction=JurisdictionCode.EUROPEAN_UNION,
                title="Lawful basis for processing personal data",
                description="Establish and document lawful basis for all personal data processing",
                risk_level=ComplianceRisk.CRITICAL,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=False,
                penalty_amount_eur=Decimal("20000000.00")  # 4% of annual turnover or €20M
            ),
            
            ComplianceRequirement(
                requirement_id="GDPR_002",
                framework=ComplianceFramework.GDPR,
                jurisdiction=JurisdictionCode.EUROPEAN_UNION,
                title="Data subject rights implementation",
                description="Implement procedures for data subject rights (access, rectification, erasure, etc.)",
                risk_level=ComplianceRisk.HIGH,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=True
            ),
            
            # AML/KYC Requirements
            ComplianceRequirement(
                requirement_id="AML_001",
                framework=ComplianceFramework.AML,
                jurisdiction=JurisdictionCode.GERMANY,
                title="Customer Due Diligence (CDD)",
                description="Implement risk-based customer due diligence procedures",
                risk_level=ComplianceRisk.CRITICAL,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=True
            ),
            
            ComplianceRequirement(
                requirement_id="AML_002",
                framework=ComplianceFramework.AML,
                jurisdiction=JurisdictionCode.GERMANY,
                title="Transaction Monitoring",
                description="Monitor transactions for suspicious activity and money laundering patterns",
                risk_level=ComplianceRisk.HIGH,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=True
            ),
            
            # OFAC Sanctions
            ComplianceRequirement(
                requirement_id="OFAC_001",
                framework=ComplianceFramework.OFAC,
                jurisdiction=JurisdictionCode.UNITED_STATES,
                title="Sanctions Screening",
                description="Screen customers and transactions against OFAC sanctions lists",
                risk_level=ComplianceRisk.CRITICAL,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=True
            ),
            
            # Copyright Compliance
            ComplianceRequirement(
                requirement_id="DMCA_001",
                framework=ComplianceFramework.DMCA,
                jurisdiction=JurisdictionCode.UNITED_STATES,
                title="DMCA Safe Harbor Compliance",
                description="Implement DMCA takedown procedures and safe harbor provisions",
                risk_level=ComplianceRisk.MEDIUM,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=False
            ),
            
            # PSD2 Requirements
            ComplianceRequirement(
                requirement_id="PSD2_001",
                framework=ComplianceFramework.PSD2,
                jurisdiction=JurisdictionCode.EUROPEAN_UNION,
                title="Strong Customer Authentication (SCA)",
                description="Implement strong customer authentication for electronic payments",
                risk_level=ComplianceRisk.HIGH,
                implementation_status="completed",
                continuous_monitoring=True,
                automated_reporting=True
            )
        ]
    
    def _initialize_data_protection_policies(self) -> List[DataProtectionPolicy]:
        """Initialize data protection policies."""



        return [
            DataProtectionPolicy(
                policy_name="GDPR Data Protection Policy",
                applicable_frameworks=[ComplianceFramework.GDPR],
                consent_required=True,
                explicit_consent=True,
                consent_withdrawal=True,
                purpose_limitation=True,
                data_minimization=True,
                lawful_basis_required=True,
                processing_purposes=["service_provision", "analytics", "marketing", "legal_compliance"],
                automated_decision_making=False,
                profiling_enabled=True,
                right_to_access=True,
                right_to_rectification=True,
                right_to_erasure=True,
                right_to_portability=True,
                right_to_object=True,
                right_to_restrict=True,
                encryption_at_rest=True,
                encryption_in_transit=True,
                pseudonymization=True,
                anonymization=False,
                access_controls=True,
                audit_logging=True,
                retention_periods={
                    DataClassification.PUBLIC: 365,  # 1 year
                    DataClassification.INTERNAL: 2555,  # 7 years
                    DataClassification.CONFIDENTIAL: 2555,  # 7 years
                    DataClassification.RESTRICTED: 3650  # 10 years
                },
                automatic_deletion=True,
                retention_schedule=True,
                adequacy_decisions=["US", "CA", "CH", "GB"],
                standard_contractual_clauses=True,
                binding_corporate_rules=False,
                breach_detection=True,
                breach_notification_hours=72,
                authority_notification=True,
                data_subject_notification=True
            ),
            
            DataProtectionPolicy(
                policy_name="CCPA Privacy Policy",
                applicable_frameworks=[ComplianceFramework.CCPA],
                consent_required=True,
                explicit_consent=False,  # Opt-out model for CCPA
                consent_withdrawal=True,
                purpose_limitation=True,
                data_minimization=True,
                processing_purposes=["business_purposes", "commercial_purposes"],
                right_to_access=True,
                right_to_erasure=True,  # Right to delete
                right_to_portability=True,
                right_to_object=True,  # Right to opt-out of sale
                encryption_at_rest=True,
                encryption_in_transit=True,
                access_controls=True,
                audit_logging=True,
                breach_detection=True,
                breach_notification_hours=72
            )
        ]
    
    def _initialize_financial_policies(self) -> List[FinancialCompliancePolicy]:
        """Initialize financial compliance policies."""



        return [
            FinancialCompliancePolicy(
                policy_name="German AML/KYC Policy",
                applicable_frameworks=[ComplianceFramework.AML, ComplianceFramework.KYC],
                customer_screening=True,
                transaction_monitoring=True,
                suspicious_activity_reporting=True,
                sanctions_screening=True,
                pep_screening=True,
                identity_verification=True,
                address_verification=True,
                document_verification=True,
                biometric_verification=False,
                ongoing_monitoring=True,
                simplified_due_diligence=True,
                standard_due_diligence=True,
                enhanced_due_diligence=True,
                daily_transaction_limits={
                    "EUR": Decimal("15000.00"),
                    "USD": Decimal("15000.00")
                },
                monthly_limits={
                    "EUR": Decimal("100000.00"),
                    "USD": Decimal("100000.00")
                },
                annual_limits={
                    "EUR": Decimal("1000000.00"),
                    "USD": Decimal("1000000.00")
                },
                velocity_monitoring=True,
                pattern_analysis=True,
                ctr_threshold=Decimal("10000.00"),
                sar_required=True,
                regulatory_reporting=True,
                audit_trail=True,
                transaction_records_years=7,
                customer_records_years=7,
                compliance_records_years=10,
                automated_record_keeping=True
            ),
            
            FinancialCompliancePolicy(
                policy_name="US Financial Compliance Policy",
                applicable_frameworks=[ComplianceFramework.AML, ComplianceFramework.OFAC],
                customer_screening=True,
                transaction_monitoring=True,
                suspicious_activity_reporting=True,
                sanctions_screening=True,
                pep_screening=True,
                identity_verification=True,
                address_verification=True,
                document_verification=True,
                ongoing_monitoring=True,
                enhanced_due_diligence=True,
                daily_transaction_limits={
                    "USD": Decimal("10000.00")
                },
                ctr_threshold=Decimal("10000.00"),
                sar_required=True,
                regulatory_reporting=True,
                audit_trail=True,
                transaction_records_years=5,
                customer_records_years=5,
                compliance_records_years=7
            )
        ]
    
    def _initialize_jurisdictional_config(self) -> Dict[JurisdictionCode, Dict[str, Any]]:
        """Initialize jurisdictional compliance configuration."""



        return {
            JurisdictionCode.GERMANY: {
                "primary_regulator": "BaFin",
                "data_protection_authority": "BfDI",
                "applicable_frameworks": [
                    ComplianceFramework.GDPR,
                    ComplianceFramework.PCI_DSS,
                    ComplianceFramework.AML,
                    ComplianceFramework.MiFID_II,
                    ComplianceFramework.PSD2
                ],
                "data_localization_required": False,
                "cross_border_restrictions": False,
                "mandatory_breach_notification": True,
                "breach_notification_hours": 72,
                "representative_required": False,
                "local_banking_license": False
            },
            
            JurisdictionCode.UNITED_STATES: {
                "primary_regulator": "Federal Reserve",
                "data_protection_authority": "FTC",
                "applicable_frameworks": [
                    ComplianceFramework.PCI_DSS,
                    ComplianceFramework.OFAC,
                    ComplianceFramework.AML,
                    ComplianceFramework.DMCA,
                    ComplianceFramework.SOX
                ],
                "data_localization_required": False,
                "cross_border_restrictions": True,
                "mandatory_breach_notification": True,
                "breach_notification_hours": 72,
                "representative_required": False,
                "local_banking_license": True
            },
            
            JurisdictionCode.EUROPEAN_UNION: {
                "primary_regulator": "ECB",
                "data_protection_authority": "EDPB",
                "applicable_frameworks": [
                    ComplianceFramework.GDPR,
                    ComplianceFramework.PCI_DSS,
                    ComplianceFramework.PSD2,
                    ComplianceFramework.MiFID_II,
                    ComplianceFramework.COPYRIGHT_DIRECTIVE
                ],
                "data_localization_required": False,
                "cross_border_restrictions": False,
                "mandatory_breach_notification": True,
                "breach_notification_hours": 72,
                "representative_required": True,
                "local_banking_license": False
            }
        }
    
    def get_compliance_requirement(self, requirement_id: str) -> Optional[ComplianceRequirement]:
        """Get compliance requirement by ID."""



        return next((req for req in self.COMPLIANCE_REQUIREMENTS if req.requirement_id == requirement_id), None)
    
    def get_requirements_by_framework(self, framework: ComplianceFramework) -> List[ComplianceRequirement]:
        """Get all requirements for a specific compliance framework."""



        return [req for req in self.COMPLIANCE_REQUIREMENTS if req.framework == framework]
    
    def get_requirements_by_jurisdiction(self, jurisdiction: JurisdictionCode) -> List[ComplianceRequirement]:
        """Get all requirements for a specific jurisdiction."""



        return [req for req in self.COMPLIANCE_REQUIREMENTS if req.jurisdiction == jurisdiction]
    
    def get_critical_requirements(self) -> List[ComplianceRequirement]:
        """Get all critical compliance requirements."""



        return [req for req in self.COMPLIANCE_REQUIREMENTS if req.risk_level == ComplianceRisk.CRITICAL]
    
    def get_data_protection_policy(self, policy_name: str) -> Optional[DataProtectionPolicy]:
        """Get data protection policy by name."""



        return next((policy for policy in self.DATA_PROTECTION_POLICIES if policy.policy_name == policy_name), None)
    
    def get_financial_policy(self, policy_name: str) -> Optional[FinancialCompliancePolicy]:
        """Get financial compliance policy by name."""



        return next((policy for policy in self.FINANCIAL_COMPLIANCE_POLICIES if policy.policy_name == policy_name), None)
    
    def get_applicable_frameworks(self, jurisdiction: JurisdictionCode) -> List[ComplianceFramework]:
        """Get applicable compliance frameworks for a jurisdiction."""
        config = self.JURISDICTIONAL_CONFIG.get(jurisdiction)
        return config.get("applicable_frameworks", []) if config else []
    
    def assess_compliance_risk(self, jurisdiction: JurisdictionCode) -> Dict[str, Any]:
        """Assess compliance risk for a specific jurisdiction."""
        requirements = self.get_requirements_by_jurisdiction(jurisdiction)
        
        risk_assessment = {
            "jurisdiction": jurisdiction.value,
            "total_requirements": len(requirements),
            "critical_requirements": len([req for req in requirements if req.risk_level == ComplianceRisk.CRITICAL]),
            "completed_requirements": len([req for req in requirements if req.implementation_status == "completed"]),
            "pending_requirements": len([req for req in requirements if req.implementation_status in ["not_started", "in_progress"]]),
            "overall_risk_level": ComplianceRisk.LOW.value,
            "estimated_penalties": sum(req.penalty_amount_eur or Decimal("0") for req in requirements),
            "next_assessment_due": None,
            "recommendations": []
        }
        
        # Calculate overall risk level
        critical_pending = len([req for req in requirements 
                               if req.risk_level == ComplianceRisk.CRITICAL and req.implementation_status != "completed"])
        
        if critical_pending > 0:
            risk_assessment["overall_risk_level"] = ComplianceRisk.CRITICAL.value
        elif len([req for req in requirements if req.risk_level == ComplianceRisk.HIGH and req.implementation_status != "completed"]) > 2:
            risk_assessment["overall_risk_level"] = ComplianceRisk.HIGH.value
        elif risk_assessment["pending_requirements"] > 5:
            risk_assessment["overall_risk_level"] = ComplianceRisk.MEDIUM.value
        
        return risk_assessment
    
    def generate_compliance_report(self, jurisdiction: Optional[JurisdictionCode] = None) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        if jurisdiction:
            requirements = self.get_requirements_by_jurisdiction(jurisdiction)
        else:
            requirements = self.COMPLIANCE_REQUIREMENTS
        
        report = {
            "report_date": datetime.now().isoformat(),
            "scope": jurisdiction.value if jurisdiction else "global",
            "summary": {
                "total_requirements": len(requirements),
                "completed": len([req for req in requirements if req.implementation_status == "completed"]),
                "in_progress": len([req for req in requirements if req.implementation_status == "in_progress"]),
                "not_started": len([req for req in requirements if req.implementation_status == "not_started"]),
                "failed": len([req for req in requirements if req.implementation_status == "failed"])
            },
            "risk_breakdown": {
                "critical": len([req for req in requirements if req.risk_level == ComplianceRisk.CRITICAL]),
                "high": len([req for req in requirements if req.risk_level == ComplianceRisk.HIGH]),
                "medium": len([req for req in requirements if req.risk_level == ComplianceRisk.MEDIUM]),
                "low": len([req for req in requirements if req.risk_level == ComplianceRisk.LOW])
            },
            "framework_coverage": {},
            "compliance_score": 0,
            "recommendations": [],
            "next_actions": []
        }
        
        # Calculate compliance score
        completed_critical = len([req for req in requirements 
                                if req.risk_level == ComplianceRisk.CRITICAL and req.implementation_status == "completed"])
        total_critical = len([req for req in requirements if req.risk_level == ComplianceRisk.CRITICAL])
        
        if total_critical > 0:
            critical_score = (completed_critical / total_critical) * 100
        else:
            critical_score = 100
        
        overall_completion = (report["summary"]["completed"] / len(requirements)) * 100 if requirements else 100
        
        # Weighted score (critical requirements have higher weight)
        report["compliance_score"] = round((critical_score * 0.7) + (overall_completion * 0.3), 2)
        
        return report


# Global configuration instance
regulatory_compliance_config = RegulatoryComplianceConfig()
