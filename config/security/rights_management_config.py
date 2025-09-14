"""
Rights Management Configuration - Enterprise Configuration Management
Enterprise configuration for rights management and legal compliance business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
    """Config: class implementation"""
            env_prefix = ""
            case_sensitive = False
            extra = "allow"
    
    def Field(**kwargs) -> None:
        return kwargs.get('default_factory', kwargs.get('default'))()
    
    def validator(field_name) -> None:
        def decorator(func) -> None:
            return func
        return decorator


class LicensingType(str, Enum):
    """Content licensing types"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    CUSTOM = "custom"
    COMMERCIAL = "commercial"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"


class UsageRight(str, Enum):
    """Content usage rights"""
    DISPLAY = "display"
    DISTRIBUTION = "distribution"
    MODIFICATION = "modification"
    COMMERCIAL_USE = "commercial_use"
    RESALE = "resale"
    SUBLICENSING = "sublicensing"
    DERIVATIVE_WORKS = "derivative_works"
    PUBLIC_PERFORMANCE = "public_performance"


class ComplianceFramework(str, Enum):
    """Legal compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    DMCA = "dmca"
    INTERNATIONAL_COPYRIGHT = "international_copyright"
    CREATIVE_COMMONS = "creative_commons"
    FAIR_USE = "fair_use"
    SAFE_HARBOR = "safe_harbor"
    BLOCKCHAIN_RIGHTS = "blockchain_rights"


class ContractType(str, Enum):
    """Contract types for rights management"""
    LICENSING_AGREEMENT = "licensing_agreement"
    DISTRIBUTION_AGREEMENT = "distribution_agreement"
    COLLABORATION_AGREEMENT = "collaboration_agreement"
    ROYALTY_AGREEMENT = "royalty_agreement"
    EXCLUSIVE_RIGHTS = "exclusive_rights"
    WORK_FOR_HIRE = "work_for_hire"
    REVENUE_SHARING = "revenue_sharing"
    SMART_CONTRACT = "smart_contract"


class EnforcementAction(str, Enum):
    """Rights enforcement actions"""
    TAKEDOWN_NOTICE = "takedown_notice"
    CEASE_DESIST = "cease_desist"
    DMCA_FILING = "dmca_filing"
    LITIGATION = "litigation"
    ARBITRATION = "arbitration"
    MEDIATION = "mediation"
    AUTOMATED_BLOCKING = "automated_blocking"
    REVENUE_CLAIM = "revenue_claim"


@dataclass
class LicenseConfiguration:
    """License configuration specification"""
    license_type: LicensingType
    usage_rights: List[UsageRight]
    restrictions: List[str]
    duration_months: Optional[int]
    territory: List[str]
    revenue_share_percentage: float
    exclusive: bool
    transferable: bool
    renewable: bool


@dataclass
class ComplianceConfiguration:
    """Legal compliance configuration"""
    framework: ComplianceFramework
    requirements: List[str]
    monitoring_enabled: bool
    auto_compliance: bool
    audit_trail: bool
    notification_settings: Dict[str, Any]


@dataclass
class ContractConfiguration:
    """Contract management configuration"""
    contract_type: ContractType
    automated_generation: bool
    blockchain_enabled: bool
    smart_contract_address: Optional[str]
    signature_required: bool
    escrow_enabled: bool
    milestone_payments: bool


@dataclass
class EnforcementConfiguration:
    """Rights enforcement configuration"""
    action_type: EnforcementAction
    automated: bool
    escalation_timeline: List[int]  # Days for escalation
    legal_team_notification: bool
    success_tracking: bool
    cost_tracking: bool


class RightsManagementSettings(BaseSettings):
    """Rights management configuration settings"""
    
    # License Management Configuration
    licensing_types: Dict[str, LicenseConfiguration] = Field(
        default_factory=lambda: {
            "exclusive": LicenseConfiguration(
                license_type=LicensingType.EXCLUSIVE,
                usage_rights=[UsageRight.DISPLAY, UsageRight.DISTRIBUTION, 
                            UsageRight.COMMERCIAL_USE, UsageRight.DERIVATIVE_WORKS],
                restrictions=["territory_limited", "time_limited"],
                duration_months=24,
                territory=["worldwide"],
                revenue_share_percentage=20.0,
                exclusive=True,
                transferable=False,
                renewable=True
            ),
            "non_exclusive": LicenseConfiguration(
                license_type=LicensingType.NON_EXCLUSIVE,
                usage_rights=[UsageRight.DISPLAY, UsageRight.DISTRIBUTION],
                restrictions=["commercial_use_limited"],
                duration_months=12,
                territory=["specific_regions"],
                revenue_share_percentage=10.0,
                exclusive=False,
                transferable=True,
                renewable=True
            ),
            "royalty_free": LicenseConfiguration(
                license_type=LicensingType.ROYALTY_FREE,
                usage_rights=[UsageRight.DISPLAY, UsageRight.MODIFICATION],
                restrictions=["attribution_required"],
                duration_months=None,  # Perpetual
                territory=["worldwide"],
                revenue_share_percentage=0.0,
                exclusive=False,
                transferable=True,
                renewable=False
            ),
            "creative_commons": LicenseConfiguration(
                license_type=LicensingType.CREATIVE_COMMONS,
                usage_rights=[UsageRight.DISPLAY, UsageRight.DISTRIBUTION, 
                            UsageRight.MODIFICATION, UsageRight.DERIVATIVE_WORKS],
                restrictions=["attribution_required", "share_alike"],
                duration_months=None,  # Perpetual
                territory=["worldwide"],
                revenue_share_percentage=0.0,
                exclusive=False,
                transferable=True,
                renewable=False
            )
        }
    )
    
    # Legal Compliance Configuration
    compliance_frameworks: Dict[str, ComplianceConfiguration] = Field(
        default_factory=lambda: {
            "gdpr": ComplianceConfiguration(
                framework=ComplianceFramework.GDPR,
                requirements=[
                    "data_consent", "right_to_deletion", "data_portability",
                    "privacy_by_design", "data_protection_officer"
                ],
                monitoring_enabled=True,
                auto_compliance=True,
                audit_trail=True,
                notification_settings={
                    "breach_notification": True,
                    "consent_renewal": True,
                    "data_request_alerts": True
                }
            ),
            "ccpa": ComplianceConfiguration(
                framework=ComplianceFramework.CCPA,
                requirements=[
                    "consumer_rights", "opt_out_option", "data_disclosure",
                    "non_discrimination", "verification_process"
                ],
                monitoring_enabled=True,
                auto_compliance=True,
                audit_trail=True,
                notification_settings={
                    "consumer_request_alerts": True,
                    "opt_out_notifications": True
                }
            ),
            "dmca": ComplianceConfiguration(
                framework=ComplianceFramework.DMCA,
                requirements=[
                    "takedown_procedure", "counter_notification",
                    "repeat_infringer_policy", "safe_harbor_compliance"
                ],
                monitoring_enabled=True,
                auto_compliance=True,
                audit_trail=True,
                notification_settings={
                    "takedown_alerts": True,
                    "counter_claim_alerts": True
                }
            ),
            "international_copyright": ComplianceConfiguration(
                framework=ComplianceFramework.INTERNATIONAL_COPYRIGHT,
                requirements=[
                    "berne_convention", "trips_agreement", "wipo_treaties",
                    "national_copyright_laws", "moral_rights"
                ],
                monitoring_enabled=True,
                auto_compliance=False,  # Requires manual review
                audit_trail=True,
                notification_settings={
                    "infringement_alerts": True,
                    "registration_reminders": True
                }
            )
        }
    )
    
    # Contract Management Configuration
    contract_management: Dict[str, ContractConfiguration] = Field(
        default_factory=lambda: {
            "licensing_agreement": ContractConfiguration(
                contract_type=ContractType.LICENSING_AGREEMENT,
                automated_generation=True,
                blockchain_enabled=True,
                smart_contract_address=None,
                signature_required=True,
                escrow_enabled=True,
                milestone_payments=False
            ),
            "distribution_agreement": ContractConfiguration(
                contract_type=ContractType.DISTRIBUTION_AGREEMENT,
                automated_generation=True,
                blockchain_enabled=True,
                smart_contract_address=None,
                signature_required=True,
                escrow_enabled=False,
                milestone_payments=True
            ),
            "collaboration_agreement": ContractConfiguration(
                contract_type=ContractType.COLLABORATION_AGREEMENT,
                automated_generation=False,  # Requires custom terms
                blockchain_enabled=True,
                smart_contract_address=None,
                signature_required=True,
                escrow_enabled=True,
                milestone_payments=True
            ),
            "revenue_sharing": ContractConfiguration(
                contract_type=ContractType.REVENUE_SHARING,
                automated_generation=True,
                blockchain_enabled=True,
                smart_contract_address=None,
                signature_required=True,
                escrow_enabled=True,
                milestone_payments=False
            )
        }
    )
    
    # Rights Enforcement Configuration
    enforcement_actions: Dict[str, EnforcementConfiguration] = Field(
        default_factory=lambda: {
            "takedown_notice": EnforcementConfiguration(
                action_type=EnforcementAction.TAKEDOWN_NOTICE,
                automated=True,
                escalation_timeline=[1, 7, 14],  # Days
                legal_team_notification=False,
                success_tracking=True,
                cost_tracking=False
            ),
            "dmca_filing": EnforcementConfiguration(
                action_type=EnforcementAction.DMCA_FILING,
                automated=True,
                escalation_timeline=[3, 10, 21],
                legal_team_notification=True,
                success_tracking=True,
                cost_tracking=True
            ),
            "cease_desist": EnforcementConfiguration(
                action_type=EnforcementAction.CEASE_DESIST,
                automated=False,  # Requires legal review
                escalation_timeline=[7, 21, 60],
                legal_team_notification=True,
                success_tracking=True,
                cost_tracking=True
            ),
            "litigation": EnforcementConfiguration(
                action_type=EnforcementAction.LITIGATION,
                automated=False,  # Always requires legal team
                escalation_timeline=[30, 90, 180],
                legal_team_notification=True,
                success_tracking=True,
                cost_tracking=True
            )
        }
    )
    
    # Usage Tracking Configuration
    usage_tracking: Dict[str, Any] = Field(
        default_factory=lambda: {
            "real_time_monitoring": True,
            "usage_analytics": True,
            "revenue_tracking": True,
            "geographic_tracking": True,
            "platform_tracking": True,
            "user_behavior_tracking": True,
            "compliance_monitoring": True,
            "anomaly_detection": True
        }
    )
    
    # Revenue Distribution Configuration
    revenue_distribution: Dict[str, Any] = Field(
        default_factory=lambda: {
            "automated_distribution": True,
            "blockchain_based": True,
            "real_time_settlements": True,
            "multi_currency_support": True,
            "tax_compliance": True,
            "dispute_resolution": True,
            "escrow_services": True,
            "transparent_reporting": True
        }
    )
    
    # Blockchain Integration Settings
    blockchain_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "smart_contracts": True,
            "nft_rights_management": True,
            "immutable_records": True,
            "decentralized_storage": True,
            "consensus_mechanism": "proof_of_stake",
            "gas_optimization": True,
            "cross_chain_compatibility": True
        }
    )
    
    # Legal Integration Settings
    legal_integration: Dict[str, Any] = Field(
        default_factory=lambda: {
            "legal_database_access": True,
            "automated_legal_research": True,
            "jurisdiction_analysis": True,
            "precedent_tracking": True,
            "legal_document_generation": True,
            "compliance_automation": True,
            "risk_assessment": True,
            "legal_cost_tracking": True
        }
    )
    
    # Performance and Security Settings
    performance_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "high_availability": True,
            "load_balancing": True,
            "auto_scaling": True,
            "caching_enabled": True,
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "access_control": "rbac",
            "audit_logging": True
        }
    )
    
    class Config:
    """Config: class implementation"""
        env_prefix = "RIGHTS_MANAGEMENT_"
        case_sensitive = False
        extra = "allow"
    
    def get_license_configuration(self, license_type: str) -> Optional[LicenseConfiguration]:
        """Get license configuration by type"""
        return self.licensing_types.get(license_type)
    
    def get_compliance_requirements(self, framework: str) -> List[str]:
        """Get compliance requirements for a framework"""
        config = self.compliance_frameworks.get(framework)
        return config.requirements if config else []
    
    def get_contract_configuration(self, contract_type: str) -> Optional[ContractConfiguration]:
        """Get contract configuration by type"""
        return self.contract_management.get(contract_type)
    
    def get_enforcement_configuration(self, action_type: str) -> Optional[EnforcementConfiguration]:
        """Get enforcement configuration by action type"""
        return self.enforcement_actions.get(action_type)
    
    def is_license_exclusive(self, license_type: str) -> bool:
        """Check if license type is exclusive"""
        config = self.get_license_configuration(license_type)
        return config.exclusive if config else False
    
    def get_revenue_share_percentage(self, license_type: str) -> float:
        """Get revenue share percentage for license type"""
        config = self.get_license_configuration(license_type)
        return config.revenue_share_percentage if config else 0.0
    
    def is_compliance_automated(self, framework: str) -> bool:
        """Check if compliance framework is automated"""
        config = self.compliance_frameworks.get(framework)
        return config.auto_compliance if config else False
    
    def is_contract_blockchain_enabled(self, contract_type: str) -> bool:
        """Check if contract type supports blockchain"""
        config = self.get_contract_configuration(contract_type)
        return config.blockchain_enabled if config else False
    
    def is_enforcement_automated(self, action_type: str) -> bool:
        """Check if enforcement action is automated"""
        config = self.get_enforcement_configuration(action_type)
        return config.automated if config else False
    
    def get_escalation_timeline(self, action_type: str) -> List[int]:
        """Get escalation timeline for enforcement action"""
        config = self.get_enforcement_configuration(action_type)
        return config.escalation_timeline if config else []
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete rights management configuration"""
        errors = []
        
        # Validate licensing configurations
        for license_type, config in self.licensing_types.items():
            if not config.usage_rights:
                errors.append(f"License type '{license_type}' has no usage rights defined")
            if config.revenue_share_percentage < 0 or config.revenue_share_percentage > 100:
                errors.append(f"License type '{license_type}' has invalid revenue share percentage")
        
        # Validate compliance configurations
        for framework, config in self.compliance_frameworks.items():
            if not config.requirements:
                errors.append(f"Compliance framework '{framework}' has no requirements defined")
        
        # Validate contract configurations
        for contract_type, config in self.contract_management.items():
            if config.blockchain_enabled and not self.blockchain_settings["enabled"]:
                errors.append(f"Contract type '{contract_type}' requires blockchain but blockchain is disabled")
        
        # Validate enforcement configurations
        for action_type, config in self.enforcement_actions.items():
            if not config.escalation_timeline:
                errors.append(f"Enforcement action '{action_type}' has no escalation timeline")
        
        return errors


# Global rights management settings instance
rights_management_settings = RightsManagementSettings()

__all__ = [
    "RightsManagementSettings",
    "rights_management_settings",
    "LicensingType",
    "UsageRight",
    "ComplianceFramework",
    "ContractType",
    "EnforcementAction",
    "LicenseConfiguration",
    "ComplianceConfiguration",
    "ContractConfiguration",
    "EnforcementConfiguration"
]