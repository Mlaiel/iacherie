"""License Management Configuration Module
=====================================

Professional licensing and rights management configuration for content monetization.
Handles automated licensing, royalty distribution, and intellectual property management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + FinTech Expert

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class LicenseType(str, Enum):
    """Content license types."""    SYNC_RIGHTS = "sync_rights"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    MASTER_USE = "master_use"
    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    PUBLIC_DISPLAY = "public_display"
    ADAPTATION = "adaptation"
    COMMERCIAL_USE = "commercial_use"
    EDITORIAL_USE = "editorial_use"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"


class LicenseScope(str, Enum):
    """License scope and territory."""    WORLDWIDE = "worldwide"
    REGIONAL = "regional"
    NATIONAL = "national"
    LOCAL = "local"
    DIGITAL_ONLY = "digital_only"
    BROADCAST = "broadcast"
    THEATRICAL = "theatrical"
    STREAMING = "streaming"
    SOCIAL_MEDIA = "social_media"


class RoyaltyType(str, Enum):
    """Royalty distribution types."""    PERFORMANCE_ROYALTY = "performance_royalty"
    MECHANICAL_ROYALTY = "mechanical_royalty"
    SYNC_ROYALTY = "sync_royalty"
    NEIGHBORING_RIGHTS = "neighboring_rights"
    DIGITAL_ROYALTY = "digital_royalty"
    BROADCAST_ROYALTY = "broadcast_royalty"
    PRINT_ROYALTY = "print_royalty"


class LicenseStatus(str, Enum):
    """License agreement status."""    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    RENEWED = "renewed"


class RightsOrganization(str, Enum):
    """Rights management organizations."""    GEMA = "gema"  # Germany
    BMI = "bmi"  # USA
    ASCAP = "ascap"  # USA
    SESAC = "sesac"  # USA
    PRS = "prs"  # UK
    SACEM = "sacem"  # France
    SIAE = "siae"  # Italy
    SGAE = "sgae"  # Spain
    STIM = "stim"  # Sweden
    TEOSTO = "teosto"  # Finland


@dataclass
class RoyaltySplit:
    """Royalty split configuration for stakeholders."""    stakeholder_id: str
    stakeholder_name: str
    role: str  # writer, composer, publisher, performer, producer
    percentage: Decimal
    territory: LicenseScope = LicenseScope.WORLDWIDE
    royalty_types: List[RoyaltyType] = field(default_factory=list)
    minimum_threshold: Decimal = Decimal("1.00")
    payment_method: str = "bank_transfer"


@dataclass
class LicenseTerms:
    """License agreement terms and conditions."""    license_type: LicenseType
    scope: LicenseScope
    territory: List[str]  # Country codes
    duration_months: int
    usage_limits: Dict[str, int] = field(default_factory=dict)  # max_plays, max_downloads, etc.
    exclusivity: bool = False
    sublicensing_allowed: bool = False
    attribution_required: bool = True
    commercial_use_allowed: bool = True
    modifications_allowed: bool = False
    resale_allowed: bool = False


@dataclass
class LicensingRate:
    """Licensing rate configuration."""    license_type: LicenseType
    base_rate: Decimal
    currency: str = "EUR"
    rate_type: str = "fixed"  # fixed, percentage, per_use, per_stream
    minimum_fee: Decimal = Decimal("0.00")
    maximum_fee: Optional[Decimal] = None
    bulk_discount_tiers: Dict[int, Decimal] = field(default_factory=dict)  # quantity -> discount_percentage
    territory_multipliers: Dict[str, Decimal] = field(default_factory=dict)  # country_code -> multiplier
    seasonal_adjustments: Dict[str, Decimal] = field(default_factory=dict)  # season -> multiplier


@dataclass
class ContentRightsMetadata:
    """Content rights and ownership metadata."""    content_id: str
    title: str
    creators: List[Dict[str, Any]]  # name, role, percentage, PRO membership
    publishers: List[Dict[str, Any]]  # name, percentage, territory
    record_label: Optional[str] = None
    isrc: Optional[str] = None  # International Standard Recording Code
    iswc: Optional[str] = None  # International Standard Musical Work Code
    copyright_year: Optional[int] = None
    original_release_date: Optional[datetime] = None
    rights_clearance_status: str = "pending"
    contains_samples: bool = False
    sample_clearances: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LicenseAgreement:
    """Complete license agreement configuration."""    agreement_id: str
    content_metadata: ContentRightsMetadata
    licensee_id: str
    licensee_name: str
    licensor_id: str
    licensor_name: str
    license_terms: LicenseTerms
    licensing_rate: LicensingRate
    royalty_splits: List[RoyaltySplit]
    
    # Agreement Details
    effective_date: datetime
    expiration_date: datetime
    auto_renewal: bool = False
    renewal_terms: Optional[Dict[str, Any]] = None
    termination_notice_days: int = 30
    
    # Financial Terms
    advance_payment: Decimal = Decimal("0.00")
    minimum_guarantee: Decimal = Decimal("0.00")
    royalty_payment_frequency: str = "quarterly"  # monthly, quarterly, annually
    payment_terms_days: int = 30
    
    # Status and Tracking
    status: LicenseStatus = LicenseStatus.DRAFT
    approval_workflow: List[Dict[str, Any]] = field(default_factory=list)
    usage_tracking_enabled: bool = True
    reporting_required: bool = True
    reporting_frequency: str = "quarterly"
    
    # Legal and Compliance
    governing_law: str = "DE"  # Country code
    dispute_resolution: str = "arbitration"
    warranties: List[str] = field(default_factory=list)
    indemnifications: List[str] = field(default_factory=list)
    force_majeure_clause: bool = True


class LicenseManagementConfig:
    """    Professional license management configuration.
    Handles automated licensing, rights clearance, and royalty distribution.
    """    
    def __init__(self):
        """Initialize license management configuration."""        
        # Database Configuration
        self.LICENSING_DB_URL = os.getenv(
            "LICENSING_DB_URL",
            "postgresql://user:pass@localhost:5432/licensing_db"
        )
        
        # Blockchain Configuration for Rights Management
        self.BLOCKCHAIN_CONFIG = {
            "enabled": True,
            "network": "ethereum",
            "smart_contract_address": os.getenv("RIGHTS_CONTRACT_ADDRESS"),
            "gas_price_gwei": 20,
            "confirmation_blocks": 3,
            "ipfs_gateway": "https://gateway.pinata.cloud/ipfs/"
        }
        
        # Rights Organizations Integration
        self.PRO_INTEGRATIONS = self._initialize_pro_integrations()
        
        # Default Licensing Rates
        self.DEFAULT_LICENSING_RATES = self._initialize_default_rates()
        
        # Automated Licensing Configuration
        self.AUTOMATION_CONFIG = {
            "enable_auto_licensing": True,
            "auto_approve_threshold": Decimal("100.00"),
            "require_manual_review": ["sync_rights", "exclusive", "master_use"],
            "blacklisted_territories": ["CU", "IR", "KP", "SY"],  # Sanctioned countries
            "whitelisted_licensees": [],
            "preferred_partners": []
        }
        
        # Royalty Distribution Configuration
        self.ROYALTY_CONFIG = {
            "enable_auto_distribution": True,
            "distribution_frequency": "monthly",
            "minimum_distribution_amount": Decimal("10.00"),
            "reserve_percentage": Decimal("15.0"),  # Reserve for disputes/adjustments
            "currency_conversion_enabled": True,
            "tax_withholding_enabled": True,
            "default_withholding_rate": Decimal("30.0")  # For non-treaty countries
        }
        
        # Usage Tracking Configuration
        self.USAGE_TRACKING_CONFIG = {
            "enable_fingerprinting": True,
            "track_streaming_platforms": True,
            "track_broadcast_usage": True,
            "track_sync_usage": True,
            "track_social_media": True,
            "real_time_monitoring": True,
            "usage_reporting_api_enabled": True
        }
        
        # Legal Compliance Configuration
        self.COMPLIANCE_CONFIG = {
            "gdpr_compliance": True,
            "ccpa_compliance": True,
            "dmca_compliance": True,
            "copyright_registration": True,
            "international_treaties": ["berne", "rome", "geneva", "trips"],
            "mandatory_disclosures": True,
            "audit_trail_required": True
        }
        
        # Performance and Scaling
        self.PERFORMANCE_CONFIG = {
            "max_concurrent_agreements": 10000,
            "agreement_processing_timeout": 300,  # seconds
            "royalty_calculation_batch_size": 5000,
            "enable_caching": True,
            "cache_ttl_hours": 6,
            "enable_rate_limiting": True,
            "rate_limit_per_minute": 1000
        }
        
        # Security Configuration
        self.SECURITY_CONFIG = {
            "encrypt_agreements": True,
            "digital_signatures_required": True,
            "multi_factor_auth_required": True,
            "ip_whitelisting_enabled": True,
            "activity_logging_enabled": True,
            "fraud_detection_enabled": True,
            "anomaly_detection_threshold": Decimal("10000.00")
        }
    
    def _initialize_pro_integrations(self) -> Dict[RightsOrganization, Dict[str, Any]]:
        """Initialize Performing Rights Organizations integrations."""        return {
            RightsOrganization.GEMA: {
                "name": "GEMA",
                "country": "DE",
                "api_endpoint": "https://online.gema.de/werke/api/",
                "authentication_type": "oauth2",
                "supports_repertoire_search": True,
                "supports_usage_reporting": True,
                "supports_royalty_distribution": True,
                "member_verification_enabled": True
            },
            RightsOrganization.BMI: {
                "name": "BMI",
                "country": "US",
                "api_endpoint": "https://repertoire.bmi.com/api/",
                "authentication_type": "api_key",
                "supports_repertoire_search": True,
                "supports_usage_reporting": True,
                "supports_royalty_distribution": False,
                "member_verification_enabled": True
            },
            RightsOrganization.ASCAP: {
                "name": "ASCAP",
                "country": "US",
                "api_endpoint": "https://www.ascap.com/repertory/api/",
                "authentication_type": "oauth2",
                "supports_repertoire_search": True,
                "supports_usage_reporting": True,
                "supports_royalty_distribution": False,
                "member_verification_enabled": True
            },
            RightsOrganization.PRS: {
                "name": "PRS for Music",
                "country": "GB",
                "api_endpoint": "https://online.prsformusic.com/api/",
                "authentication_type": "oauth2",
                "supports_repertoire_search": True,
                "supports_usage_reporting": True,
                "supports_royalty_distribution": True,
                "member_verification_enabled": True
            },
            RightsOrganization.SACEM: {
                "name": "SACEM",
                "country": "FR",
                "api_endpoint": "https://repertoire.sacem.fr/api/",
                "authentication_type": "oauth2",
                "supports_repertoire_search": True,
                "supports_usage_reporting": True,
                "supports_royalty_distribution": True,
                "member_verification_enabled": True
            }
        }
    
    def _initialize_default_rates(self) -> Dict[LicenseType, LicensingRate]:
        """Initialize default licensing rates."""        return {
            LicenseType.SYNC_RIGHTS: LicensingRate(
                license_type=LicenseType.SYNC_RIGHTS,
                base_rate=Decimal("500.00"),
                rate_type="fixed",
                minimum_fee=Decimal("100.00"),
                territory_multipliers={
                    "US": Decimal("1.5"),
                    "GB": Decimal("1.2"),
                    "DE": Decimal("1.0"),
                    "FR": Decimal("1.1"),
                    "JP": Decimal("1.3")
                }
            ),
            LicenseType.MECHANICAL: LicensingRate(
                license_type=LicenseType.MECHANICAL,
                base_rate=Decimal("0.091"),  # USD per copy (US statutory rate)
                rate_type="per_use",
                minimum_fee=Decimal("0.01"),
                bulk_discount_tiers={
                    1000: Decimal("5.0"),
                    10000: Decimal("10.0"),
                    100000: Decimal("15.0")
                }
            ),
            LicenseType.PERFORMANCE: LicensingRate(
                license_type=LicenseType.PERFORMANCE,
                base_rate=Decimal("0.0024"),  # Per stream/play
                rate_type="per_use",
                minimum_fee=Decimal("0.001"),
                territory_multipliers={
                    "US": Decimal("1.0"),
                    "GB": Decimal("0.8"),
                    "DE": Decimal("0.9"),
                    "IN": Decimal("0.3"),
                    "BR": Decimal("0.4")
                }
            ),
            LicenseType.MASTER_USE: LicensingRate(
                license_type=LicenseType.MASTER_USE,
                base_rate=Decimal("1000.00"),
                rate_type="fixed",
                minimum_fee=Decimal("250.00"),
                maximum_fee=Decimal("25000.00")
            ),
            LicenseType.COMMERCIAL_USE: LicensingRate(
                license_type=LicenseType.COMMERCIAL_USE,
                base_rate=Decimal("15.0"),  # Percentage of advertising budget
                rate_type="percentage",
                minimum_fee=Decimal("500.00"),
                seasonal_adjustments={
                    "holiday": Decimal("1.5"),
                    "summer": Decimal("1.2"),
                    "back_to_school": Decimal("1.3")
                }
            ),
            LicenseType.ROYALTY_FREE: LicensingRate(
                license_type=LicenseType.ROYALTY_FREE,
                base_rate=Decimal("50.00"),
                rate_type="fixed",
                minimum_fee=Decimal("10.00"),
                maximum_fee=Decimal("500.00")
            )
        }
    
    def get_pro_integration(self, organization: RightsOrganization) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific PRO integration."""        return self.PRO_INTEGRATIONS.get(organization)
    
    def get_default_rate(self, license_type: LicenseType) -> Optional[LicensingRate]:
        """Get default licensing rate for a license type."""        return self.DEFAULT_LICENSING_RATES.get(license_type)
    
    def calculate_license_fee(
        self,
        license_type: LicenseType,
        usage_data: Dict[str, Any],
        territory: str = "DE",
        custom_rates: Optional[LicensingRate] = None
    ) -> Decimal:
        """Calculate license fee based on usage data and rates."""        
        rate_config = custom_rates or self.get_default_rate(license_type)
        if not rate_config:
            return Decimal("0.00")
        
        base_fee = rate_config.base_rate
        
        # Apply territory multiplier
        territory_multiplier = rate_config.territory_multipliers.get(territory, Decimal("1.0"))
        base_fee *= territory_multiplier
        
        # Calculate based on rate type
        if rate_config.rate_type == "fixed":
            total_fee = base_fee
        elif rate_config.rate_type == "per_use":
            usage_count = usage_data.get("usage_count", 1)
            total_fee = base_fee * Decimal(str(usage_count))
        elif rate_config.rate_type == "percentage":
            base_amount = Decimal(str(usage_data.get("base_amount", 0)))
            total_fee = base_amount * (base_fee / Decimal("100"))
        else:
            total_fee = base_fee
        
        # Apply bulk discounts
        if rate_config.bulk_discount_tiers and "quantity" in usage_data:
            quantity = usage_data["quantity"]
            applicable_discount = Decimal("0.0")
            for tier_quantity, discount_percentage in sorted(rate_config.bulk_discount_tiers.items()):
                if quantity >= tier_quantity:
                    applicable_discount = discount_percentage
            
            if applicable_discount > Decimal("0.0"):
                discount_amount = total_fee * (applicable_discount / Decimal("100"))
                total_fee -= discount_amount
        
        # Apply seasonal adjustments
        if rate_config.seasonal_adjustments and "season" in usage_data:
            season = usage_data["season"]
            seasonal_multiplier = rate_config.seasonal_adjustments.get(season, Decimal("1.0"))
            total_fee *= seasonal_multiplier
        
        # Apply minimum and maximum constraints
        if total_fee < rate_config.minimum_fee:
            total_fee = rate_config.minimum_fee
        
        if rate_config.maximum_fee and total_fee > rate_config.maximum_fee:
            total_fee = rate_config.maximum_fee
        
        return total_fee.quantize(Decimal("0.01"))  # Round to 2 decimal places
    
    def validate_license_agreement(self, agreement: LicenseAgreement) -> Dict[str, Any]:
        """Validate a license agreement for completeness and compliance."""        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "compliance_checks": []
        }
        
        # Required fields validation
        if not agreement.content_metadata.title:
            validation_result["errors"].append("Content title is required")
            validation_result["valid"] = False
        
        if not agreement.licensee_name or not agreement.licensor_name:
            validation_result["errors"].append("Licensee and licensor names are required")
            validation_result["valid"] = False
        
        if not agreement.royalty_splits:
            validation_result["errors"].append("Royalty splits must be defined")
            validation_result["valid"] = False
        
        # Royalty splits validation
        total_percentage = sum(split.percentage for split in agreement.royalty_splits)
        if abs(total_percentage - Decimal("100.0")) > Decimal("0.01"):
            validation_result["errors"].append(f"Royalty splits must total 100%, got {total_percentage}%")
            validation_result["valid"] = False
        
        # Territory validation
        if not agreement.license_terms.territory:
            validation_result["warnings"].append("No territories specified, defaulting to worldwide")
        
        # Compliance checks
        if agreement.license_terms.territory and any(
            country in self.AUTOMATION_CONFIG["blacklisted_territories"] 
            for country in agreement.license_terms.territory
        ):
            validation_result["compliance_checks"].append("Agreement includes sanctioned territories")
        
        # Date validation
        if agreement.effective_date >= agreement.expiration_date:
            validation_result["errors"].append("Effective date must be before expiration date")
            validation_result["valid"] = False
        
        # Duration validation
        duration_days = (agreement.expiration_date - agreement.effective_date).days
        if duration_days > 365 * 10:  # 10 years max
            validation_result["warnings"].append("Agreement duration exceeds 10 years")
        
        return validation_result
    
    def get_automated_licensing_eligibility(self, agreement: LicenseAgreement) -> Dict[str, Any]:
        """Determine if an agreement is eligible for automated processing."""        
        eligibility = {
            "eligible": True,
            "reasons": [],
            "manual_review_required": False,
            "auto_approval_eligible": False
        }
        
        # Check if license type requires manual review
        if agreement.license_terms.license_type.value in self.AUTOMATION_CONFIG["require_manual_review"]:
            eligibility["eligible"] = False
            eligibility["manual_review_required"] = True
            eligibility["reasons"].append(f"License type {agreement.license_terms.license_type.value} requires manual review")
        
        # Check licensing fee threshold
        estimated_fee = self.calculate_license_fee(
            agreement.license_terms.license_type,
            {"usage_count": 1000, "base_amount": 10000},  # Estimated usage
            agreement.license_terms.territory[0] if agreement.license_terms.territory else "DE"
        )
        
        if estimated_fee > self.AUTOMATION_CONFIG["auto_approve_threshold"]:
            eligibility["eligible"] = False
            eligibility["manual_review_required"] = True
            eligibility["reasons"].append(f"Estimated fee {estimated_fee} exceeds auto-approval threshold")
        else:
            eligibility["auto_approval_eligible"] = True
        
        # Check blacklisted territories
        if agreement.license_terms.territory and any(
            country in self.AUTOMATION_CONFIG["blacklisted_territories"]
            for country in agreement.license_terms.territory
        ):
            eligibility["eligible"] = False
            eligibility["reasons"].append("Agreement includes blacklisted territories")
        
        # Check licensee status
        if agreement.licensee_id in self.AUTOMATION_CONFIG.get("whitelisted_licensees", []):
            eligibility["auto_approval_eligible"] = True
            eligibility["reasons"].append("Licensee is whitelisted for auto-approval")
        
        return eligibility


# Global configuration instance
license_management_config = LicenseManagementConfig()
