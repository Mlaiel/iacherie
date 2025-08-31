"""Compliance Configuration Module
===============================

Advanced compliance and regulatory configuration for IA Influencer Agent platform.
Provides comprehensive compliance frameworks, data protection, and regulatory
adherence configurations for global content creator operations.

Business Logic Integration:
- GDPR/CCPA compliance for creator data protection
- Copyright and DMCA compliance for content protection
- Financial compliance for revenue operations
- Platform-specific compliance requirements

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"                    # General Data Protection Regulation (EU)
    CCPA = "ccpa"                    # California Consumer Privacy Act (US)
    PIPEDA = "pipeda"                # Personal Information Protection (Canada)
    LGPD = "lgpd"                    # Lei Geral de Proteção de Dados (Brazil)
    PDPA_SINGAPORE = "pdpa_sg"       # Personal Data Protection Act (Singapore)
    SOX = "sox"                      # Sarbanes-Oxley Act (US Financial)
    PCI_DSS = "pci_dss"             # Payment Card Industry Data Security
    ISO27001 = "iso27001"            # Information Security Management
    NIST = "nist"                    # NIST Cybersecurity Framework
    COPPA = "coppa"                  # Children's Online Privacy Protection (US)


class DataCategory(Enum):
    """Categories of data for compliance purposes."""
    PERSONAL_DATA = "personal_data"
    SENSITIVE_DATA = "sensitive_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    CONTENT_DATA = "content_data"
    METADATA = "metadata"
    ANALYTICS_DATA = "analytics_data"
    COMMUNICATION_DATA = "communication_data"


class LegalBasis(Enum):
    """Legal basis for data processing under GDPR."""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataSubjectRight(Enum):
    """Data subject rights under privacy regulations."""
    ACCESS = "access"                # Right to access personal data
    RECTIFICATION = "rectification"  # Right to correct inaccurate data
    ERASURE = "erasure"             # Right to be forgotten
    PORTABILITY = "portability"     # Right to data portability
    RESTRICTION = "restriction"     # Right to restrict processing
    OBJECTION = "objection"         # Right to object to processing
    WITHDRAW_CONSENT = "withdraw_consent"  # Right to withdraw consent


@dataclass
class GDPRConfig:
    """GDPR (General Data Protection Regulation) configuration."""
    
    # Compliance settings
    gdpr_compliance_enabled: bool = True
    data_protection_officer_contact: str = "dpo@ia-influencer.com"
    representative_contact: str = "legal@ia-influencer.com"
    
    # Legal basis mapping
    legal_basis_mapping: Dict[str, LegalBasis] = field(default_factory=lambda: {
        "user_registration": LegalBasis.CONTRACT,
        "content_processing": LegalBasis.CONTRACT,
        "analytics": LegalBasis.LEGITIMATE_INTERESTS,
        "marketing": LegalBasis.CONSENT,
        "platform_integration": LegalBasis.CONTRACT,
        "revenue_processing": LegalBasis.CONTRACT,
        "security_monitoring": LegalBasis.LEGITIMATE_INTERESTS
    })
    
    # Data categories and retention
    data_retention_periods: Dict[DataCategory, int] = field(default_factory=lambda: {
        DataCategory.PERSONAL_DATA: 1095,      # 3 years
        DataCategory.SENSITIVE_DATA: 730,      # 2 years
        DataCategory.FINANCIAL_DATA: 2555,     # 7 years
        DataCategory.CONTENT_DATA: 2190,       # 6 years
        DataCategory.ANALYTICS_DATA: 730,      # 2 years
        DataCategory.COMMUNICATION_DATA: 365   # 1 year
    })
    
    # Consent management
    consent_management: Dict[str, Any] = field(default_factory=lambda: {
        "explicit_consent_required": True,
        "granular_consent": True,
        "consent_withdrawal_mechanism": True,
        "consent_tracking": True,
        "consent_version_control": True,
        "cookie_consent": True,
        "marketing_consent_separate": True
    })
    
    # Data subject rights
    data_subject_rights: Dict[DataSubjectRight, Dict[str, Any]] = field(default_factory=lambda: {
        DataSubjectRight.ACCESS: {
            "enabled": True,
            "response_time_days": 30,
            "automated_response": True,
            "format": "machine_readable"
        },
        DataSubjectRight.RECTIFICATION: {
            "enabled": True,
            "response_time_days": 30,
            "automated_correction": False,
            "verification_required": True
        },
        DataSubjectRight.ERASURE: {
            "enabled": True,
            "response_time_days": 30,
            "automated_deletion": True,
            "backup_deletion": True,
            "exceptions_check": True
        },
        DataSubjectRight.PORTABILITY: {
            "enabled": True,
            "response_time_days": 30,
            "format": "json",
            "encryption": True
        }
    })
    
    # Data transfers
    international_transfers: Dict[str, Any] = field(default_factory=lambda: {
        "adequacy_decisions": ["UK", "Switzerland", "Japan"],
        "standard_contractual_clauses": True,
        "binding_corporate_rules": False,
        "transfer_logging": True,
        "impact_assessment_required": True
    })
    
    # Breach notification
    breach_notification: Dict[str, Any] = field(default_factory=lambda: {
        "authority_notification_hours": 72,
        "data_subject_notification_required": True,
        "high_risk_threshold": "significant_harm",
        "automated_detection": True,
        "incident_response_plan": True
    })


@dataclass
class CCPAConfig:
    """CCPA (California Consumer Privacy Act) configuration."""
    
    # Compliance settings
    ccpa_compliance_enabled: bool = True
    business_threshold_met: bool = True  # $25M+ revenue or 50K+ consumers
    
    # Consumer rights
    consumer_rights: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "right_to_know": {
            "enabled": True,
            "response_time_days": 45,
            "categories_disclosed": True,
            "sources_disclosed": True,
            "purposes_disclosed": True
        },
        "right_to_delete": {
            "enabled": True,
            "response_time_days": 45,
            "exceptions_applied": True,
            "verification_required": True
        },
        "right_to_opt_out": {
            "enabled": True,
            "do_not_sell_link": True,
            "global_privacy_control": True,
            "third_party_disclosure": True
        },
        "right_to_non_discrimination": {
            "enabled": True,
            "no_denial_of_service": True,
            "no_different_pricing": True,
            "incentive_programs_allowed": True
        }
    })
    
    # Personal information categories
    personal_info_categories: List[str] = field(default_factory=lambda: [
        "identifiers",
        "commercial_information",
        "internet_activity",
        "geolocation_data",
        "audio_visual_data",
        "professional_information",
        "inferences"
    ])
    
    # Business purposes
    business_purposes: List[str] = field(default_factory=lambda: [
        "service_provision",
        "security_monitoring",
        "quality_assurance",
        "research_development",
        "platform_improvement",
        "legal_compliance"
    ])


@dataclass
class CopyrightComplianceConfig:
    """Copyright and intellectual property compliance configuration."""
    
    # DMCA compliance
    dmca_compliance: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "designated_agent_contact": "dmca@ia-influencer.com",
        "takedown_processing_hours": 24,
        "counter_notification_supported": True,
        "repeat_infringer_policy": True,
        "safe_harbor_provisions": True
    })
    
    # Content identification
    content_identification: Dict[str, Any] = field(default_factory=lambda: {
        "audio_fingerprinting": True,
        "video_fingerprinting": True,
        "image_fingerprinting": True,
        "text_similarity_detection": True,
        "metadata_analysis": True,
        "automated_blocking": True
    })
    
    # Rights management
    rights_management: Dict[str, Any] = field(default_factory=lambda: {
        "creative_commons_support": True,
        "licensing_verification": True,
        "fair_use_analysis": True,
        "attribution_tracking": True,
        "license_compliance_monitoring": True
    })
    
    # Platform compliance
    platform_copyright_policies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "youtube": {
            "content_id_integration": True,
            "copyright_strikes_tracking": True,
            "monetization_compliance": True
        },
        "spotify": {
            "rights_holder_verification": True,
            "mechanical_licensing": True,
            "performance_rights": True
        },
        "instagram": {
            "music_licensing": True,
            "story_copyright_check": True,
            "reels_copyright_compliance": True
        }
    })


@dataclass
class FinancialComplianceConfig:
    """Financial and payment compliance configuration."""
    
    # PCI DSS compliance
    pci_dss_compliance: Dict[str, Any] = field(default_factory=lambda: {
        "compliance_level": "SAQ-A",  # Self-Assessment Questionnaire
        "secure_payment_processing": True,
        "cardholder_data_protection": True,
        "network_security": True,
        "vulnerability_management": True,
        "access_control": True,
        "monitoring_testing": True,
        "security_policies": True
    })
    
    # Anti-Money Laundering (AML)
    aml_compliance: Dict[str, Any] = field(default_factory=lambda: {
        "customer_due_diligence": True,
        "transaction_monitoring": True,
        "suspicious_activity_reporting": True,
        "sanctions_screening": True,
        "enhanced_due_diligence_threshold": 10000,  # USD
        "record_keeping_years": 5
    })
    
    # Tax compliance
    tax_compliance: Dict[str, Any] = field(default_factory=lambda: {
        "1099_reporting": True,
        "international_tax_reporting": True,
        "vat_compliance": True,
        "withholding_tax": True,
        "tax_document_generation": True,
        "jurisdiction_mapping": True
    })
    
    # Financial reporting
    financial_reporting: Dict[str, Any] = field(default_factory=lambda: {
        "sox_compliance": True,
        "audit_trails": True,
        "financial_controls": True,
        "quarterly_reporting": True,
        "management_certification": True
    })


@dataclass
class PlatformComplianceConfig:
    """Platform-specific compliance requirements."""
    
    # Platform policies
    platform_policies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "spotify": {
            "content_policy_compliance": True,
            "metadata_accuracy": True,
            "explicit_content_labeling": True,
            "territory_restrictions": True,
            "delivery_requirements": True
        },
        "youtube": {
            "community_guidelines": True,
            "advertiser_friendly_content": True,
            "copyright_compliance": True,
            "age_restriction_compliance": True,
            "monetization_policies": True
        },
        "instagram": {
            "community_standards": True,
            "commercial_content_disclosure": True,
            "brand_safety": True,
            "creator_commerce_policies": True
        },
        "tiktok": {
            "community_guidelines": True,
            "creator_fund_eligibility": True,
            "commercial_content_policies": True,
            "data_localization": True
        }
    })
    
    # Regional compliance
    regional_requirements: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "EU": {
            "gdpr_compliance": True,
            "digital_services_act": True,
            "copyright_directive": True,
            "data_localization": False
        },
        "US": {
            "ccpa_compliance": True,
            "coppa_compliance": True,
            "dmca_compliance": True,
            "state_privacy_laws": True
        },
        "China": {
            "data_localization": True,
            "content_censorship": True,
            "cybersecurity_law": True,
            "personal_information_protection": True
        }
    })


@dataclass
class DataProtectionConfig:
    """Data protection and privacy configuration."""
    
    # Privacy by design
    privacy_by_design: Dict[str, Any] = field(default_factory=lambda: {
        "data_minimization": True,
        "purpose_limitation": True,
        "storage_limitation": True,
        "accuracy_maintenance": True,
        "security_measures": True,
        "transparency": True,
        "accountability": True
    })
    
    # Data processing principles
    processing_principles: Dict[str, bool] = field(default_factory=lambda: {
        "lawfulness": True,
        "fairness": True,
        "transparency": True,
        "purpose_limitation": True,
        "data_minimization": True,
        "accuracy": True,
        "storage_limitation": True,
        "integrity_confidentiality": True,
        "accountability": True
    })
    
    # Technical measures
    technical_measures: Dict[str, Any] = field(default_factory=lambda: {
        "encryption_at_rest": True,
        "encryption_in_transit": True,
        "pseudonymization": True,
        "anonymization": True,
        "access_controls": True,
        "audit_logging": True,
        "data_loss_prevention": True
    })
    
    # Organizational measures
    organizational_measures: Dict[str, Any] = field(default_factory=lambda: {
        "privacy_policies": True,
        "staff_training": True,
        "incident_response": True,
        "vendor_management": True,
        "privacy_impact_assessments": True,
        "regular_audits": True
    })


@dataclass
class ComplianceMonitoringConfig:
    """Compliance monitoring and reporting configuration."""
    
    # Automated monitoring
    automated_monitoring: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "real_time_alerts": True,
        "compliance_dashboard": True,
        "violation_detection": True,
        "trend_analysis": True,
        "predictive_analytics": True
    })
    
    # Compliance metrics
    compliance_metrics: List[str] = field(default_factory=lambda: [
        "gdpr_request_response_time",
        "data_breach_detection_time",
        "consent_collection_rate",
        "data_retention_compliance",
        "copyright_violation_rate",
        "platform_policy_violations",
        "financial_control_effectiveness"
    ])
    
    # Reporting requirements
    reporting_requirements: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "regulatory_reports": {
            "frequency": "quarterly",
            "automated_generation": True,
            "approval_workflow": True,
            "digital_signatures": True
        },
        "internal_reports": {
            "frequency": "monthly",
            "stakeholder_distribution": True,
            "action_item_tracking": True
        },
        "audit_reports": {
            "frequency": "annual",
            "external_auditor_access": True,
            "compliance_certification": True
        }
    })
    
    # Alert configuration
    alert_configuration: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "data_breach": {
            "immediate_alert": True,
            "escalation_chain": True,
            "external_notification": True
        },
        "compliance_violation": {
            "severity_based_routing": True,
            "automatic_remediation": True,
            "management_notification": True
        },
        "regulatory_changes": {
            "monitoring_enabled": True,
            "impact_assessment": True,
            "implementation_planning": True
        }
    })


@dataclass
class ComplianceConfig:
    """Main compliance configuration container."""
    
    # Framework configurations
    gdpr: GDPRConfig = field(default_factory=GDPRConfig)
    ccpa: CCPAConfig = field(default_factory=CCPAConfig)
    copyright: CopyrightComplianceConfig = field(default_factory=CopyrightComplianceConfig)
    financial: FinancialComplianceConfig = field(default_factory=FinancialComplianceConfig)
    platform: PlatformComplianceConfig = field(default_factory=PlatformComplianceConfig)
    data_protection: DataProtectionConfig = field(default_factory=DataProtectionConfig)
    monitoring: ComplianceMonitoringConfig = field(default_factory=ComplianceMonitoringConfig)
    
    # Global compliance settings
    enabled_frameworks: Set[ComplianceFramework] = field(default_factory=lambda: {
        ComplianceFramework.GDPR,
        ComplianceFramework.CCPA,
        ComplianceFramework.PCI_DSS,
        ComplianceFramework.ISO27001
    })
    
    # Compliance officer contacts
    compliance_contacts: Dict[str, str] = field(default_factory=lambda: {
        "data_protection_officer": "dpo@ia-influencer.com",
        "compliance_officer": "compliance@ia-influencer.com",
        "legal_counsel": "legal@ia-influencer.com",
        "security_officer": "ciso@ia-influencer.com"
    })
    
    # Regional applicability
    regional_compliance: Dict[str, List[ComplianceFramework]] = field(default_factory=lambda: {
        "EU": [ComplianceFramework.GDPR, ComplianceFramework.ISO27001],
        "US": [ComplianceFramework.CCPA, ComplianceFramework.SOX, ComplianceFramework.PCI_DSS],
        "CA": [ComplianceFramework.PIPEDA],
        "BR": [ComplianceFramework.LGPD],
        "SG": [ComplianceFramework.PDPA_SINGAPORE]
    })
    
    # Implementation timeline
    implementation_timeline: Dict[ComplianceFramework, str] = field(default_factory=lambda: {
        ComplianceFramework.GDPR: "implemented",
        ComplianceFramework.CCPA: "implemented", 
        ComplianceFramework.PCI_DSS: "in_progress",
        ComplianceFramework.ISO27001: "planned",
        ComplianceFramework.SOX: "planned"
    })
    
    # Compliance validation
    validation_schedule: Dict[str, str] = field(default_factory=lambda: {
        "internal_audit": "quarterly",
        "external_audit": "annually",
        "penetration_testing": "bi_annually",
        "compliance_review": "monthly"
    })


# Default configuration instance
compliance_config = ComplianceConfig()


def get_compliance_config() -> ComplianceConfig:
    """Get the compliance configuration instance."""
    return compliance_config


def get_applicable_frameworks(region: str) -> List[ComplianceFramework]:
    """Get applicable compliance frameworks for a specific region."""
    config = get_compliance_config()
    return config.regional_compliance.get(region, [])


def is_framework_enabled(framework: ComplianceFramework) -> bool:
    """Check if a compliance framework is enabled."""
    config = get_compliance_config()
    return framework in config.enabled_frameworks


def get_data_retention_period(data_category: DataCategory) -> int:
    """Get data retention period for a specific data category under GDPR."""
    config = get_compliance_config()
    return config.gdpr.data_retention_periods.get(data_category, 365)


def validate_compliance_config(config: ComplianceConfig) -> bool:
    """Validate compliance configuration settings."""
    # Validate enabled frameworks
    for framework in config.enabled_frameworks:
        if not isinstance(framework, ComplianceFramework):
            raise ValueError(f"Invalid compliance framework: {framework}")
    
    # Validate contact information
    for contact_type, email in config.compliance_contacts.items():
        if not email or "@" not in email:
            raise ValueError(f"Invalid email for {contact_type}: {email}")
    
    # Validate GDPR retention periods
    for period in config.gdpr.data_retention_periods.values():
        if period <= 0:
            raise ValueError(f"Retention period must be positive: {period}")
    
    return True
