"""Compliance Configuration Module
===============================

Enterprise compliance management for legal, regulatory, and industry standards.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""from enum import Enum
from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


class ComplianceStandard(str, Enum):
    """Supported compliance standards and regulations."""    GDPR = "gdpr"  # General Data Protection Regulation (EU)
    CCPA = "ccpa"  # California Consumer Privacy Act (US)
    PIPEDA = "pipeda"  # Personal Information Protection and Electronic Documents Act (Canada)
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados (Brazil)
    SOC2 = "soc2"  # Service Organization Control 2
    ISO27001 = "iso27001"  # Information Security Management
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    COPPA = "coppa"  # Children's Online Privacy Protection Act
    DMCA = "dmca"  # Digital Millennium Copyright Act
    CAN_SPAM = "can_spam"  # Controlling the Assault of Non-Solicited Pornography And Marketing
    TCPA = "tcpa"  # Telephone Consumer Protection Act


class DataCategory(str, Enum):
    """Categories of data for compliance classification."""    PERSONAL_IDENTIFIABLE = "personal_identifiable"
    SENSITIVE_PERSONAL = "sensitive_personal"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    BEHAVIORAL = "behavioral"
    CONTENT_METADATA = "content_metadata"
    USAGE_ANALYTICS = "usage_analytics"
    COMMUNICATION = "communication"
    LOCATION = "location"


class ProcessingPurpose(str, Enum):
    """Legitimate purposes for data processing."""    SERVICE_PROVISION = "service_provision"
    CONTRACT_PERFORMANCE = "contract_performance"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"
    CONSENT = "consent"
    VITAL_INTEREST = "vital_interest"
    SECURITY = "security"
    FRAUD_PREVENTION = "fraud_prevention"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    RESEARCH = "research"


class RetentionPeriod(str, Enum):
    """Data retention periods."""    SESSION = "session"
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    MONTHS_6 = "6_months"
    YEAR_1 = "1_year"
    YEARS_2 = "2_years"
    YEARS_5 = "5_years"
    YEARS_7 = "7_years"
    YEARS_10 = "10_years"
    INDEFINITE = "indefinite"


@dataclass
class DataProcessingRecord:
    """Record of data processing activities."""    data_category: DataCategory
    processing_purpose: ProcessingPurpose
    legal_basis: str
    retention_period: RetentionPeriod
    data_subjects: List[str]
    recipients: List[str]
    transfer_countries: List[str]
    security_measures: List[str]
    automated_decision_making: bool
    data_sources: List[str]


@dataclass
class ConsentRecord:
    """User consent tracking record."""    user_id: str
    consent_type: str
    granted: bool
    timestamp: datetime
    version: str
    withdrawal_method: Optional[str] = None
    expiry_date: Optional[datetime] = None
    renewal_required: bool = False


@dataclass
class CompliancePolicy:
    """Compliance policy definition."""    policy_id: str
    standard: ComplianceStandard
    title: str
    description: str
    requirements: List[str]
    controls: List[str]
    monitoring_frequency: str
    review_cycle_months: int
    responsible_team: str
    compliance_score_weight: float


class ComplianceConfig:
    """Enterprise compliance management configuration."""    # Regional compliance requirements
    REGIONAL_COMPLIANCE = {
        "european_union": {
            "primary_standards": [ComplianceStandard.GDPR, ComplianceStandard.ISO27001],
            "data_residency_required": True,
            "consent_management_required": True,
            "data_protection_officer_required": True,
            "privacy_by_design_required": True,
            "breach_notification_hours": 72,
            "subject_rights": [
                "access", "rectification", "erasure", "portability",
                "restriction", "objection", "automated_decision_opt_out"
            ],
            "lawful_basis_documentation": True,
            "privacy_impact_assessment": True
        },
        "united_states": {
            "primary_standards": [
                ComplianceStandard.CCPA, ComplianceStandard.SOC2, 
                ComplianceStandard.COPPA, ComplianceStandard.CAN_SPAM
            ],
            "state_specific_laws": ["ccpa", "illinois_biometric", "new_york_shield"],
            "sector_specific": ["hipaa", "pci_dss", "ferpa"],
            "data_residency_preferred": True,
            "consent_management_required": False,
            "opt_out_mechanisms": True,
            "breach_notification_days": 30
        },
        "canada": {
            "primary_standards": [ComplianceStandard.PIPEDA],
            "provincial_laws": ["quebec_law_25", "bc_pipa"],
            "data_residency_required": True,
            "consent_management_required": True,
            "breach_notification_hours": 72,
            "privacy_commissioner_oversight": True
        },
        "asia_pacific": {
            "country_specific": {
                "singapore": ["pdpa"],
                "australia": ["privacy_act"],
                "japan": ["appi"],
                "south_korea": ["pipa"]
            },
            "cross_border_transfer_restrictions": True,
            "local_representative_required": False
        }
    }

    # Data processing compliance matrix
    DATA_PROCESSING_COMPLIANCE = {
        DataCategory.PERSONAL_IDENTIFIABLE: {
            "gdpr_requirements": {
                "lawful_basis": "required",
                "consent_granular": True,
                "purpose_limitation": True,
                "data_minimization": True,
                "retention_limits": True,
                "subject_rights": "full"
            },
            "ccpa_requirements": {
                "notice_at_collection": True,
                "opt_out_right": True,
                "deletion_right": True,
                "non_discrimination": True
            },
            "security_requirements": {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "access_controls": "strict",
                "audit_logging": "comprehensive"
            },
            "retention_guidelines": {
                "default_period": RetentionPeriod.YEARS_2,
                "active_user_extension": RetentionPeriod.YEARS_5,
                "legal_hold_capability": True,
                "auto_deletion": True
            }
        },
        DataCategory.SENSITIVE_PERSONAL: {
            "gdpr_requirements": {
                "explicit_consent": True,
                "special_category_protection": True,
                "dpia_required": True,
                "enhanced_security": True
            },
            "processing_restrictions": {
                "automated_decisions": "prohibited_without_consent",
                "profiling": "explicit_consent_required",
                "third_party_sharing": "restricted"
            },
            "retention_guidelines": {
                "default_period": RetentionPeriod.YEAR_1,
                "justification_required": True,
                "regular_review": "quarterly"
            }
        },
        DataCategory.FINANCIAL: {
            "pci_dss_requirements": {
                "secure_storage": True,
                "encrypted_transmission": True,
                "access_restriction": True,
                "regular_testing": True
            },
            "retention_requirements": {
                "transaction_data": RetentionPeriod.YEARS_7,
                "audit_logs": RetentionPeriod.YEARS_10,
                "cardholder_data": "minimal_retention"
            }
        },
        DataCategory.CONTENT_METADATA: {
            "copyright_compliance": {
                "dmca_compliance": True,
                "attribution_requirements": True,
                "takedown_procedures": True,
                "counter_notification": True
            },
            "retention_guidelines": {
                "original_content": RetentionPeriod.YEARS_5,
                "derivative_works": RetentionPeriod.YEARS_2,
                "deleted_content_recovery": RetentionPeriod.DAYS_90
            }
        }
    }

    # Compliance policies and procedures
    COMPLIANCE_POLICIES = {
        "privacy_policy": CompliancePolicy(
            policy_id="PRIV-001",
            standard=ComplianceStandard.GDPR,
            title="Privacy and Data Protection Policy",
            description="Comprehensive privacy policy covering data collection, processing, and user rights",
            requirements=[
                "Clear and transparent privacy notice",
                "Lawful basis for processing documented",
                "Data subject rights procedures",
                "Breach response procedures",
                "International transfer safeguards"
            ],
            controls=[
                "Privacy notice review and updates",
                "Consent management system",
                "Data subject request handling",
                "Privacy impact assessments",
                "Staff privacy training"
            ],
            monitoring_frequency="monthly",
            review_cycle_months=6,
            responsible_team="privacy_team",
            compliance_score_weight=0.25
        ),
        "data_security": CompliancePolicy(
            policy_id="SEC-001",
            standard=ComplianceStandard.SOC2,
            title="Data Security and Access Control Policy",
            description="Information security controls and access management procedures",
            requirements=[
                "Risk-based security controls",
                "Access control and authentication",
                "Data encryption requirements",
                "Security monitoring and logging",
                "Incident response procedures"
            ],
            controls=[
                "Multi-factor authentication",
                "Role-based access controls",
                "Security awareness training",
                "Vulnerability assessments",
                "Security incident monitoring"
            ],
            monitoring_frequency="continuous",
            review_cycle_months=12,
            responsible_team="security_team",
            compliance_score_weight=0.30
        ),
        "content_protection": CompliancePolicy(
            policy_id="COPY-001",
            standard=ComplianceStandard.DMCA,
            title="Copyright and Content Protection Policy",
            description="Procedures for copyright protection and DMCA compliance",
            requirements=[
                "Copyright infringement detection",
                "DMCA takedown procedures",
                "Counter-notification process",
                "Repeat infringer policy",
                "Content licensing management"
            ],
            controls=[
                "Automated content scanning",
                "Takedown request processing",
                "Copyright owner verification",
                "Content restoration procedures",
                "Legal compliance monitoring"
            ],
            monitoring_frequency="daily",
            review_cycle_months=6,
            responsible_team="legal_team",
            compliance_score_weight=0.20
        )
    }

    # Consent management configuration
    CONSENT_MANAGEMENT = {
        "consent_types": {
            "essential": {
                "required": True,
                "description": "Essential services and basic functionality",
                "legal_basis": "contract_performance",
                "withdrawal_allowed": False,
                "granular_control": False
            },
            "analytics": {
                "required": False,
                "description": "Usage analytics and performance monitoring",
                "legal_basis": "legitimate_interest",
                "withdrawal_allowed": True,
                "granular_control": True,
                "default_state": "opt_in"
            },
            "marketing": {
                "required": False,
                "description": "Marketing communications and promotional content",
                "legal_basis": "consent",
                "withdrawal_allowed": True,
                "granular_control": True,
                "default_state": "opt_out",
                "renewal_period_months": 24
            },
            "personalization": {
                "required": False,
                "description": "Personalized content and recommendations",
                "legal_basis": "consent",
                "withdrawal_allowed": True,
                "granular_control": True,
                "default_state": "opt_in"
            },
            "third_party_sharing": {
                "required": False,
                "description": "Sharing data with trusted partners",
                "legal_basis": "consent",
                "withdrawal_allowed": True,
                "granular_control": True,
                "default_state": "opt_out",
                "partner_disclosure_required": True
            }
        },
        "consent_collection": {
            "methods": ["checkbox", "toggle", "signature", "voice", "click_wrap"],
            "evidence_retention": True,
            "version_tracking": True,
            "timestamp_required": True,
            "ip_address_logging": True,
            "consent_proof_duration": RetentionPeriod.YEARS_7
        },
        "withdrawal_mechanisms": {
            "self_service_portal": True,
            "email_request": True,
            "support_ticket": True,
            "automated_processing": True,
            "confirmation_required": False,
            "processing_time_hours": 24
        }
    }

    # Subject rights management
    SUBJECT_RIGHTS = {
        "right_of_access": {
            "response_time_days": 30,
            "identity_verification": "required",
            "data_format": ["pdf", "json", "csv"],
            "fee_applicable": False,
            "exemptions": ["legal_proceedings", "national_security"],
            "automation_level": "semi_automated"
        },
        "right_to_rectification": {
            "response_time_days": 30,
            "verification_process": "identity_and_accuracy",
            "third_party_notification": "required",
            "audit_trail": "required",
            "automated_processing": True
        },
        "right_to_erasure": {
            "response_time_days": 30,
            "verification_process": "enhanced_verification",
            "exceptions": ["legal_retention", "freedom_of_expression"],
            "third_party_notification": "required",
            "backup_erasure": "required",
            "confirmation_provided": True
        },
        "right_to_portability": {
            "response_time_days": 30,
            "data_formats": ["json", "csv", "xml"],
            "direct_transfer": "where_technically_feasible",
            "scope_limitations": "automated_processing_only",
            "identity_verification": "required"
        },
        "right_to_restriction": {
            "response_time_days": 30,
            "processing_halt": "immediate",
            "storage_only": True,
            "third_party_notification": "required",
            "lifting_conditions": "documented"
        },
        "right_to_object": {
            "response_time_days": 30,
            "legitimate_interest_override": "possible",
            "marketing_opt_out": "immediate",
            "profiling_opt_out": "honored",
            "notification_requirements": "automated_systems"
        }
    }

    # Audit and monitoring requirements
    AUDIT_REQUIREMENTS = {
        "audit_frequency": {
            ComplianceStandard.GDPR: "annual",
            ComplianceStandard.SOC2: "annual",
            ComplianceStandard.ISO27001: "annual",
            ComplianceStandard.PCI_DSS: "quarterly"
        },
        "internal_audits": {
            "frequency": "quarterly",
            "scope": "risk_based",
            "documentation": "required",
            "remediation_tracking": True,
            "executive_reporting": True
        },
        "external_audits": {
            "frequency": "annual",
            "auditor_qualification": "certified_professional",
            "scope": "comprehensive",
            "report_sharing": "stakeholders_only",
            "remediation_timeline": "90_days"
        },
        "compliance_monitoring": {
            "automated_controls": True,
            "real_time_alerts": True,
            "dashboard_reporting": True,
            "trend_analysis": True,
            "exception_reporting": True
        }
    }

    # Breach response procedures
    BREACH_RESPONSE = {
        "detection_methods": [
            "automated_monitoring",
            "user_reports",
            "security_tools",
            "audit_findings",
            "third_party_notifications"
        ],
        "assessment_timeline": {
            "initial_assessment_hours": 1,
            "detailed_assessment_hours": 24,
            "final_assessment_hours": 72
        },
        "notification_requirements": {
            ComplianceStandard.GDPR: {
                "authority_notification_hours": 72,
                "individual_notification_required": "high_risk",
                "documentation_required": True
            },
            ComplianceStandard.CCPA: {
                "authority_notification_days": 30,
                "individual_notification_required": "always",
                "website_posting_required": True
            }
        },
        "response_team": {
            "incident_commander": "privacy_officer",
            "technical_lead": "security_team",
            "legal_counsel": "legal_team",
            "communications": "pr_team",
            "business_continuity": "operations_team"
        },
        "recovery_procedures": {
            "containment_priority": "immediate",
            "forensic_analysis": "preserve_evidence",
            "system_restoration": "security_verified",
            "lessons_learned": "documented"
        }
    }

    @classmethod
    def get_regional_requirements(cls, region: str) -> Dict[str, Any]:
        """Get compliance requirements for a specific region."""        return cls.REGIONAL_COMPLIANCE.get(region, {})

    @classmethod
    def get_data_category_requirements(cls, category: DataCategory) -> Dict[str, Any]:
        """Get compliance requirements for a specific data category."""        return cls.DATA_PROCESSING_COMPLIANCE.get(category, {})

    @classmethod
    def validate_processing_lawfulness(cls, category: DataCategory, purpose: ProcessingPurpose, 
                                     region: str) -> Dict[str, bool]:
        """Validate if data processing is lawful under applicable regulations."""        validation_results = {}
        
        regional_reqs = cls.get_regional_requirements(region)
        category_reqs = cls.get_data_category_requirements(category)
        
        # GDPR validation
        if ComplianceStandard.GDPR in regional_reqs.get("primary_standards", []):
            gdpr_reqs = category_reqs.get("gdpr_requirements", {})
            validation_results["gdpr_compliant"] = cls._validate_gdpr_processing(purpose, gdpr_reqs)
        
        # CCPA validation
        if ComplianceStandard.CCPA in regional_reqs.get("primary_standards", []):
            ccpa_reqs = category_reqs.get("ccpa_requirements", {})
            validation_results["ccpa_compliant"] = cls._validate_ccpa_processing(purpose, ccpa_reqs)
        
        return validation_results

    @classmethod
    def _validate_gdpr_processing(cls, purpose: ProcessingPurpose, requirements: Dict[str, Any]) -> bool:
        """Validate GDPR compliance for data processing."""        # Simplified validation logic
        lawful_basis_required = requirements.get("lawful_basis") == "required"
        
        # Check if purpose aligns with lawful bases
        lawful_purposes = [
            ProcessingPurpose.CONTRACT_PERFORMANCE,
            ProcessingPurpose.LEGAL_OBLIGATION,
            ProcessingPurpose.LEGITIMATE_INTEREST,
            ProcessingPurpose.CONSENT
        ]
        
        return purpose in lawful_purposes and (not lawful_basis_required or True)

    @classmethod
    def _validate_ccpa_processing(cls, purpose: ProcessingPurpose, requirements: Dict[str, Any]) -> bool:
        """Validate CCPA compliance for data processing."""        # Simplified validation logic
        notice_required = requirements.get("notice_at_collection", False)
        
        # CCPA allows most business purposes with proper notice
        business_purposes = [
            ProcessingPurpose.SERVICE_PROVISION,
            ProcessingPurpose.SECURITY,
            ProcessingPurpose.FRAUD_PREVENTION,
            ProcessingPurpose.ANALYTICS
        ]
        
        return purpose in business_purposes and (not notice_required or True)

    @classmethod
    def get_retention_period_days(cls, retention_period: RetentionPeriod) -> int:
        """Convert retention period enum to days."""        period_mapping = {
            RetentionPeriod.SESSION: 1,
            RetentionPeriod.DAYS_30: 30,
            RetentionPeriod.DAYS_90: 90,
            RetentionPeriod.MONTHS_6: 180,
            RetentionPeriod.YEAR_1: 365,
            RetentionPeriod.YEARS_2: 730,
            RetentionPeriod.YEARS_5: 1825,
            RetentionPeriod.YEARS_7: 2555,
            RetentionPeriod.YEARS_10: 3650,
            RetentionPeriod.INDEFINITE: -1
        }
        return period_mapping.get(retention_period, 365)

    @classmethod
    def calculate_compliance_score(cls, assessment_results: Dict[str, Any]) -> float:
        """Calculate overall compliance score based on policy assessments."""        total_weight = sum(policy.compliance_score_weight for policy in cls.COMPLIANCE_POLICIES.values())
        weighted_score = 0.0
        
        for policy_id, policy in cls.COMPLIANCE_POLICIES.items():
            policy_score = assessment_results.get(policy_id, {}).get("score", 0.0)
            weighted_score += policy_score * policy.compliance_score_weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0

    @classmethod
    def get_subject_rights_procedures(cls, right_type: str) -> Dict[str, Any]:
        """Get procedures for handling specific subject rights requests."""        return cls.SUBJECT_RIGHTS.get(right_type, {})

    @classmethod
    def is_consent_required(cls, data_category: DataCategory, processing_purpose: ProcessingPurpose, 
                          region: str) -> bool:
        """Determine if explicit consent is required for data processing."""        regional_reqs = cls.get_regional_requirements(region)
        category_reqs = cls.get_data_category_requirements(data_category)
        
        # Check for explicit consent requirements
        if data_category == DataCategory.SENSITIVE_PERSONAL:
            return True
        
        if processing_purpose == ProcessingPurpose.MARKETING:
            return True
        
        # Regional specific requirements
        if region == "european_union" and regional_reqs.get("consent_management_required"):
            gdpr_reqs = category_reqs.get("gdpr_requirements", {})
            return gdpr_reqs.get("consent_granular", False)
        
        return False
