"""⚖️ Legal & Licensing Configuration Manager - IA-Influencer-Agent
===============================================================
Project Creator & Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
         Microservices Architect + Audio Engineer + DevOps Engineer + IA Prompt Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise-grade legal and licensing configuration management system.
===============================================================
"""
from typing import Dict, Any, Optional, List, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import logging
from pathlib import Path
import json
import yaml
from decimal import Decimal

# Initialize logger
logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """Types of licenses"""
    COPYRIGHT = "copyright"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC_LICENSE = "sync_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    MASTER_LICENSE = "master_license"
    PUBLISHING_LICENSE = "publishing_license"
    DISTRIBUTION_LICENSE = "distribution_license"
    COMMERCIAL_LICENSE = "commercial_license"
    EDITORIAL_LICENSE = "editorial_license"
    EDUCATIONAL_LICENSE = "educational_license"
    CUSTOM_LICENSE = "custom_license"

class LegalJurisdiction(Enum):
    """Legal jurisdictions"""
    UNITED_STATES = "united_states"
    EUROPEAN_UNION = "european_union"
    GERMANY = "germany"
    UNITED_KINGDOM = "united_kingdom"
    FRANCE = "france"
    CANADA = "canada"
    AUSTRALIA = "australia"
    JAPAN = "japan"
    SOUTH_KOREA = "south_korea"
    CHINA = "china"
    INDIA = "india"
    BRAZIL = "brazil"
    MEXICO = "mexico"
    INTERNATIONAL = "international"

class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    LGPD = "lgpd"
    DMCA = "dmca"
    COPPA = "coppa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC_2 = "soc_2"
    COPYRIGHTS_DIRECTIVE = "copyrights_directive"

class ContractType(Enum):
    """Contract types"""
    ARTIST_AGREEMENT = "artist_agreement"
    DISTRIBUTION_AGREEMENT = "distribution_agreement"
    LICENSING_AGREEMENT = "licensing_agreement"
    COLLABORATION_AGREEMENT = "collaboration_agreement"
    WORK_FOR_HIRE = "work_for_hire"
    PUBLISHING_AGREEMENT = "publishing_agreement"
    SYNC_AGREEMENT = "sync_agreement"
    ENDORSEMENT_AGREEMENT = "endorsement_agreement"
    SPONSORSHIP_AGREEMENT = "sponsorship_agreement"
    SERVICE_AGREEMENT = "service_agreement"
    NDA = "nda"
    PRIVACY_POLICY = "privacy_policy"
    TERMS_OF_SERVICE = "terms_of_service"

class LegalDocumentStatus(Enum):
    """Legal document status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    DISPUTED = "disputed"
    ARCHIVED = "archived"

@dataclass
class LicenseConfiguration:
    """License configuration"""
    license_type: LicenseType
    enabled: bool = True
    
    # Basic license information
    license_name: str = ""
    license_description: str = ""
    license_version: str = "1.0"
    license_url: Optional[str] = None
    
    # Rights and permissions
    commercial_use_allowed: bool = True
    modification_allowed: bool = True
    distribution_allowed: bool = True
    private_use_allowed: bool = True
    patent_use_allowed: bool = False
    
    # Obligations
    include_copyright: bool = True
    include_license: bool = True
    state_changes: bool = False
    disclose_source: bool = False
    same_license: bool = False
    
    # Restrictions
    liability_limitation: bool = True
    warranty_disclaimer: bool = True
    trademark_use_restriction: bool = True
    hold_harmless: bool = True
    
    # Territory and duration
    territorial_scope: List[LegalJurisdiction] = field(default_factory=lambda: [LegalJurisdiction.INTERNATIONAL])
    duration_years: Optional[int] = None
    renewable: bool = True
    auto_renewal: bool = False
    
    # Financial terms
    licensing_fee: Optional[Decimal] = None
    royalty_percentage: Optional[float] = None
    minimum_guarantee: Optional[Decimal] = None
    advance_payment: Optional[Decimal] = None
    payment_schedule: str = "monthly"
    
    # Usage restrictions
    max_copies: Optional[int] = None
    max_users: Optional[int] = None
    geographical_restrictions: List[str] = field(default_factory=list)
    industry_restrictions: List[str] = field(default_factory=list)
    
    # Quality and standards
    quality_standards: List[str] = field(default_factory=list)
    technical_requirements: Dict[str, Any] = field(default_factory=dict)
    delivery_format: List[str] = field(default_factory=list)
    
    # Attribution requirements
    attribution_required: bool = True
    attribution_format: str = "© {year} {creator_name}"
    credit_placement: str = "visible"
    logo_placement_required: bool = False
    
    # Audit and compliance
    audit_rights: bool = True
    reporting_requirements: List[str] = field(default_factory=list)
    compliance_verification: bool = True
    
    # Termination
    termination_notice_days: int = 30
    termination_for_cause: bool = True
    post_termination_obligations: List[str] = field(default_factory=list)

@dataclass
class DMCAConfiguration:
    """DMCA takedown configuration"""
    enabled: bool = True
    
    # Contact information
    designated_agent_name: str = "Fahed Mlaiel"
    designated_agent_email: str = "mlaiel@live.de"
    designated_agent_phone: Optional[str] = None
    designated_agent_address: str = ""
    
    # Processing settings
    auto_processing: bool = True
    human_review_required: bool = True
    processing_time_hours: int = 24
    response_time_hours: int = 12
    
    # Notice requirements
    require_sworn_statement: bool = True
    require_signature: bool = True
    require_contact_info: bool = True
    require_good_faith_belief: bool = True
    require_authorization: bool = True
    
    # Validation settings
    validate_copyright_ownership: bool = True
    validate_infringement_claim: bool = True
    validate_contact_information: bool = True
    verify_identity: bool = True
    
    # Counter-notice handling
    counter_notice_enabled: bool = True
    counter_notice_period_days: int = 10
    reinstatement_period_days: int = 14
    legal_action_period_days: int = 10
    
    # Documentation
    maintain_records: bool = True
    record_retention_years: int = 3
    privacy_protection: bool = True
    transparency_reporting: bool = True
    
    # Templates and automation
    notice_templates: Dict[str, str] = field(default_factory=dict)
    response_templates: Dict[str, str] = field(default_factory=dict)
    automated_acknowledgment: bool = True
    status_tracking: bool = True

@dataclass
class ComplianceConfiguration:
    """Compliance configuration"""
    enabled: bool = True
    
    # Frameworks
    active_frameworks: List[ComplianceFramework] = field(default_factory=lambda: [
        ComplianceFramework.GDPR, ComplianceFramework.CCPA, ComplianceFramework.DMCA
    ])
    
    # Data protection
    data_protection_enabled: bool = True
    data_minimization: bool = True
    purpose_limitation: bool = True
    data_retention_policy: bool = True
    right_to_erasure: bool = True
    data_portability: bool = True
    
    # Consent management
    explicit_consent_required: bool = True
    consent_withdrawal: bool = True
    consent_documentation: bool = True
    age_verification: bool = True
    parental_consent: bool = True
    
    # Privacy rights
    privacy_by_design: bool = True
    privacy_impact_assessment: bool = True
    data_breach_notification: bool = True
    privacy_officer_required: bool = True
    
    # Security requirements
    encryption_required: bool = True
    access_controls: bool = True
    audit_logging: bool = True
    incident_response: bool = True
    vulnerability_management: bool = True
    
    # Reporting and notifications
    regulatory_reporting: bool = True
    breach_notification_hours: int = 72
    individual_notification_required: bool = True
    transparency_reports: bool = True
    
    # Training and awareness
    staff_training_required: bool = True
    training_frequency_months: int = 12
    compliance_monitoring: bool = True
    risk_assessment: bool = True

@dataclass
class ContractManagementConfig:
    """Contract management configuration"""
    enabled: bool = True
    
    # Contract lifecycle
    automated_generation: bool = True
    digital_signatures: bool = True
    approval_workflow: bool = True
    version_control: bool = True
    expiration_tracking: bool = True
    
    # Templates and standardization
    standardized_templates: bool = True
    clause_library: bool = True
    template_versioning: bool = True
    localization_support: bool = True
    
    # Review and approval
    legal_review_required: bool = True
    multi_level_approval: bool = True
    risk_assessment: bool = True
    compliance_check: bool = True
    
    # Notifications and alerts
    renewal_notifications: bool = True
    expiration_alerts: bool = True
    milestone_reminders: bool = True
    obligation_tracking: bool = True
    
    # Integration
    crm_integration: bool = True
    financial_system_integration: bool = True
    document_management_integration: bool = True
    
    # Analytics and reporting
    contract_analytics: bool = True
    performance_metrics: bool = True
    compliance_reporting: bool = True
    risk_analytics: bool = True
    
    # Security and access
    role_based_access: bool = True
    encryption_at_rest: bool = True
    audit_trail: bool = True
    secure_sharing: bool = True

@dataclass
class IntellectualPropertyConfig:
    """Intellectual property configuration"""
    enabled: bool = True
    
    # IP types
    copyright_protection: bool = True
    trademark_protection: bool = True
    patent_protection: bool = False
    trade_secret_protection: bool = True
    
    # Registration and filing
    automated_registration: bool = True
    priority_filing: bool = True
    international_filing: bool = True
    maintenance_tracking: bool = True
    
    # Portfolio management
    ip_portfolio_tracking: bool = True
    valuation_tracking: bool = True
    licensing_opportunity_identification: bool = True
    infringement_monitoring: bool = True
    
    # Enforcement
    automated_enforcement: bool = True
    cease_and_desist_automation: bool = True
    litigation_support: bool = True
    settlement_tracking: bool = True
    
    # Due diligence
    freedom_to_operate_analysis: bool = True
    prior_art_searching: bool = True
    clearance_procedures: bool = True
    
    # Collaboration and licensing
    licensing_program: bool = True
    cross_licensing: bool = True
    patent_pooling: bool = False
    open_source_compliance: bool = True

@dataclass
class LegalLicensingConfiguration:
    """Master legal and licensing configuration"""
    # Core configurations
    license_configs: Dict[LicenseType, LicenseConfiguration] = field(default_factory=dict)
    dmca_config: DMCAConfiguration = field(default_factory=DMCAConfiguration)
    compliance_config: ComplianceConfiguration = field(default_factory=ComplianceConfiguration)
    contract_management_config: ContractManagementConfig = field(default_factory=ContractManagementConfig)
    ip_config: IntellectualPropertyConfig = field(default_factory=IntellectualPropertyConfig)
    
    # Global legal settings
    primary_jurisdiction: LegalJurisdiction = LegalJurisdiction.GERMANY
    legal_entity_name: str = "Fahed Mlaiel"
    legal_entity_type: str = "Individual"
    business_registration_number: Optional[str] = None
    tax_identification_number: Optional[str] = None
    
    # Legal representation
    law_firm_name: Optional[str] = None
    primary_attorney: Optional[str] = None
    attorney_contact_email: Optional[str] = None
    attorney_contact_phone: Optional[str] = None
    
    # Default terms and conditions
    default_license_terms: Dict[str, Any] = field(default_factory=dict)
    standard_payment_terms: str = "Net 30"
    default_warranty_period_days: int = 90
    limitation_of_liability: bool = True
    
    # Risk management
    insurance_required: bool = True
    indemnification_required: bool = True
    dispute_resolution_method: str = "arbitration"
    governing_law: LegalJurisdiction = LegalJurisdiction.GERMANY
    
    # Documentation and record keeping
    document_retention_years: int = 7
    legal_document_encryption: bool = True
    backup_legal_documents: bool = True
    version_control_legal_docs: bool = True
    
    # Monitoring and compliance
    legal_monitoring_enabled: bool = True
    regulatory_change_tracking: bool = True
    compliance_audits: bool = True
    legal_risk_assessment: bool = True
    
    # Notifications and alerts
    legal_alert_enabled: bool = True
    contract_expiration_alerts: bool = True
    compliance_deadline_alerts: bool = True
    legal_news_monitoring: bool = True
    
    # Integration settings
    legal_system_integration: bool = True
    case_management_integration: bool = True
    billing_system_integration: bool = True
    
    # Metadata
    version: str = "2.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "Fahed Mlaiel"
    contact_email: str = "mlaiel@live.de"

class LegalLicensingConfigManager:
    """
    Enterprise-grade legal and licensing configuration manager.
    
    Manages comprehensive configuration for licensing, DMCA, compliance,
    contract management, and intellectual property protection.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize legal licensing configuration manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration path
        self.config_path = config_path or os.getenv(
            "LEGAL_CONFIG_PATH",
            "/app/config/legal_licensing.yaml"
        )
        
        # Initialize default configuration
        self._config = LegalLicensingConfiguration()
        
        # Initialize default license configurations
        self._initialize_default_licenses()
        
        # Configuration state
        self.initialized = False
        self.last_updated = datetime.now()
        self.validation_errors = []
        
        # Load configuration from file if exists
        self._load_configuration()
        
        self.logger.info("Legal licensing configuration manager initialized")
    
    def _initialize_default_licenses(self) -> None:
        """Initialize default license configurations"""
        default_licenses = {
            LicenseType.COPYRIGHT: LicenseConfiguration(
                license_type=LicenseType.COPYRIGHT,
                license_name="Standard Copyright License",
                commercial_use_allowed=True,
                modification_allowed=False,
                distribution_allowed=True,
                include_copyright=True,
                attribution_required=True
            ),
            LicenseType.CREATIVE_COMMONS: LicenseConfiguration(
                license_type=LicenseType.CREATIVE_COMMONS,
                license_name="Creative Commons Attribution",
                commercial_use_allowed=True,
                modification_allowed=True,
                distribution_allowed=True,
                include_copyright=True,
                attribution_required=True,
                same_license=True
            ),
            LicenseType.EXCLUSIVE: LicenseConfiguration(
                license_type=LicenseType.EXCLUSIVE,
                license_name="Exclusive Commercial License",
                commercial_use_allowed=True,
                modification_allowed=True,
                distribution_allowed=True,
                licensing_fee=Decimal("1000.00"),
                royalty_percentage=10.0
            )
        }
        
        for license_type, config in default_licenses.items():
            self._config.license_configs[license_type] = config
    
    def _load_configuration(self) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Update configuration with loaded data
                self._update_config_from_dict(config_data)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                self.logger.info("No configuration file found, using defaults")
                return False
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in config_data.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self._config.updated_at = datetime.now()
        self.last_updated = datetime.now()
    
    def add_license_configuration(self, license_type: LicenseType, config: LicenseConfiguration) -> bool:
        """Add license configuration"""
        try:
            self._config.license_configs[license_type] = config
            self._config.updated_at = datetime.now()
            self.last_updated = datetime.now()
            self.logger.info(f"License configuration {license_type.value} added")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add license configuration: {e}")
            return False
    
    def get_license_configuration(self, license_type: LicenseType) -> Optional[LicenseConfiguration]:
        """Get license configuration"""
        return self._config.license_configs.get(license_type)
    
    def get_available_licenses(self) -> List[LicenseType]:
        """Get list of available license types"""
        return [
            license_type for license_type, config in self._config.license_configs.items()
            if config.enabled
        ]
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        try:
            # Validate license configurations
            for license_type, config in self._config.license_configs.items():
                if config.enabled and not config.license_name:
                    errors.append(f"License {license_type.value} requires a name")
                
                if config.royalty_percentage and (config.royalty_percentage < 0 or config.royalty_percentage > 100):
                    errors.append(f"License {license_type.value} royalty percentage must be between 0 and 100")
            
            # Validate DMCA configuration
            dmca_config = self._config.dmca_config
            if dmca_config.enabled and not dmca_config.designated_agent_email:
                errors.append("DMCA designated agent email is required")
            
            # Validate compliance configuration
            compliance_config = self._config.compliance_config
            if compliance_config.enabled and not compliance_config.active_frameworks:
                errors.append("At least one compliance framework must be selected")
            
            # Validate global settings
            if not self._config.legal_entity_name:
                errors.append("Legal entity name is required")
            
            self.validation_errors = errors
            
            if not errors:
                self.logger.info("Configuration validation passed")
            else:
                self.logger.warning(f"Configuration validation failed with {len(errors)} errors")
            
            return errors
        
        except Exception as e:
            error_msg = f"Configuration validation error: {e}"
            self.logger.error(error_msg)
            return [error_msg]
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration status and metadata"""
        return {
            "initialized": self.initialized,
            "last_updated": self.last_updated,
            "config_path": self.config_path,
            "validation_errors": self.validation_errors,
            "version": self._config.version,
            "created_by": self._config.created_by,
            "contact_email": self._config.contact_email,
            "primary_jurisdiction": self._config.primary_jurisdiction.value,
            "legal_entity_name": self._config.legal_entity_name,
            "available_licenses": len(self.get_available_licenses()),
            "total_licenses": len(self._config.license_configs),
            "features_enabled": {
                "dmca_processing": self._config.dmca_config.enabled,
                "compliance_monitoring": self._config.compliance_config.enabled,
                "contract_management": self._config.contract_management_config.enabled,
                "ip_protection": self._config.ip_config.enabled,
                "legal_monitoring": self._config.legal_monitoring_enabled,
                "legal_alerts": self._config.legal_alert_enabled
            }
        }

# Global instance
legal_licensing_config_manager = LegalLicensingConfigManager()

# Export public API
__all__ = [
    "LegalLicensingConfigManager",
    "LegalLicensingConfiguration",
    "LicenseConfiguration",
    "DMCAConfiguration",
    "ComplianceConfiguration",
    "ContractManagementConfig",
    "IntellectualPropertyConfig",
    "LicenseType",
    "LegalJurisdiction",
    "ComplianceFramework",
    "ContractType",
    "LegalDocumentStatus",
    "legal_licensing_config_manager"
]
