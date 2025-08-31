"""Licensing Configuration Module
=============================

Professional licensing configuration for automated content licensing and revenue management.
Supports multiple license types, automated negotiations, and royalty tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from datetime import datetime, timedelta
from decimal import Decimal


class LicenseType(str, Enum):
    """Types of content licenses."""    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    CREATIVE_COMMONS = "creative_commons"
    PUBLIC_DOMAIN = "public_domain"
    CUSTOM = "custom"


class UsageType(str, Enum):
    """Types of content usage."""    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    SYNCHRONIZATION = "synchronization"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    DISTRIBUTION = "distribution"


class LicenseStatus(str, Enum):
    """Status of license agreements."""    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    UNDER_NEGOTIATION = "under_negotiation"
    REJECTED = "rejected"


class PricingModel(str, Enum):
    """Pricing models for licenses."""    FLAT_FEE = "flat_fee"
    ROYALTY_PERCENTAGE = "royalty_percentage"
    REVENUE_SHARE = "revenue_share"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    TIERED = "tiered"
    HYBRID = "hybrid"


class Territory(str, Enum):
    """Territorial coverage for licenses."""    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    COUNTRY_SPECIFIC = "country_specific"


@dataclass
class LicenseTerms:
    """License terms and conditions."""    license_type: LicenseType
    usage_types: List[UsageType]
    territory: Territory
    duration_months: Optional[int] = None  # None = perpetual
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    renewable: bool = True
    transferable: bool = False
    sublicensable: bool = False
    attribution_required: bool = True
    modifications_allowed: bool = False
    commercial_use_allowed: bool = True
    exclusivity_period_days: Optional[int] = None
    usage_limitations: Dict[str, Any] = field(default_factory=dict)
    quality_requirements: Dict[str, str] = field(default_factory=dict)


@dataclass
class PricingStructure:
    """Pricing structure for licenses."""    pricing_model: PricingModel
    base_price: Decimal = Decimal('0.00')
    currency: str = "USD"
    royalty_percentage: Optional[float] = None
    revenue_share_percentage: Optional[float] = None
    minimum_guarantee: Optional[Decimal] = None
    advance_payment: Optional[Decimal] = None
    payment_schedule: str = "monthly"  # monthly, quarterly, annually, one_time
    late_payment_fee_percentage: float = 1.5
    payment_terms_days: int = 30
    tiered_rates: List[Dict[str, Any]] = field(default_factory=list)
    volume_discounts: Dict[str, float] = field(default_factory=dict)
    seasonal_adjustments: Dict[str, float] = field(default_factory=dict)


@dataclass
class AutomatedNegotiationConfig:
    """Configuration for automated license negotiations."""    enable_auto_negotiation: bool = True
    min_acceptable_price: Decimal = Decimal('1.00')
    max_discount_percentage: float = 20.0
    negotiation_rounds_limit: int = 5
    auto_accept_threshold: Decimal = Decimal('100.00')
    counter_offer_strategy: str = "gradual_decrease"  # fixed_rate, gradual_decrease, market_based
    negotiation_timeout_hours: int = 72
    human_intervention_threshold: Decimal = Decimal('1000.00')
    bulk_discount_enabled: bool = True
    loyalty_discount_enabled: bool = True
    seasonal_pricing_enabled: bool = True
    market_rate_adjustment: bool = True
    competitive_analysis_enabled: bool = True


@dataclass
class RoyaltyTrackingConfig:
    """Configuration for royalty tracking and distribution."""    enable_royalty_tracking: bool = True
    tracking_granularity: str = "transaction"  # transaction, daily, monthly
    real_time_tracking: bool = True
    automated_reporting: bool = True
    reporting_frequency: str = "monthly"
    minimum_payout_threshold: Decimal = Decimal('10.00')
    payout_schedule: str = "monthly"  # weekly, monthly, quarterly
    payout_method: str = "bank_transfer"  # bank_transfer, paypal, crypto
    tax_handling: bool = True
    currency_conversion: bool = True
    foreign_exchange_provider: str = "xe"
    withholding_tax_countries: List[str] = field(default_factory=list)
    audit_trail_enabled: bool = True
    dispute_resolution_enabled: bool = True


@dataclass
class ComplianceConfig:
    """Legal compliance configuration for licensing."""    jurisdiction: str = "EU"
    regulatory_compliance: List[str] = field(default_factory=lambda: [
        "GDPR", "DMCA", "EU_Copyright_Directive"
    ])
    contract_language: str = "en"
    legal_review_required: bool = True
    digital_signature_required: bool = True
    notarization_required: bool = False
    witness_requirement: int = 0
    cooling_off_period_days: int = 14
    force_majeure_clauses: bool = True
    dispute_resolution_method: str = "arbitration"  # arbitration, mediation, court
    governing_law: str = "German Law"
    venue_jurisdiction: str = "Berlin, Germany"


@dataclass
class IntegrationConfig:
    """Integration configuration with external systems."""    enable_crm_integration: bool = True
    crm_system: str = "salesforce"
    enable_accounting_integration: bool = True
    accounting_system: str = "quickbooks"
    enable_payment_gateway: bool = True
    payment_gateways: List[str] = field(default_factory=lambda: [
        "stripe", "paypal", "wise"
    ])
    enable_blockchain_tracking: bool = False
    blockchain_network: str = "ethereum"
    smart_contracts_enabled: bool = False
    api_rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "requests_per_minute": 100,
        "requests_per_hour": 1000
    })
    webhook_endpoints: List[str] = field(default_factory=list)
    data_synchronization_interval: int = 300  # seconds


class LicensingConfig:
    """    Professional licensing configuration manager.
    Provides industrial-grade configuration for automated content licensing.
    """    
    def __init__(self):
        # General licensing settings
        self.enable_licensing_system: bool = True
        self.auto_licensing_enabled: bool = True
        self.manual_approval_required: bool = True
        self.default_license_type: LicenseType = LicenseType.NON_EXCLUSIVE
        self.license_approval_threshold: Decimal = Decimal('500.00')
        
        # Configuration components
        self.automated_negotiation = AutomatedNegotiationConfig()
        self.royalty_tracking = RoyaltyTrackingConfig()
        self.compliance = ComplianceConfig()
        self.integration = IntegrationConfig()
        
        # Default license templates
        self.license_templates: Dict[str, Dict[str, Any]] = {}
        self.pricing_templates: Dict[str, PricingStructure] = {}
        
        # Content categories and their licensing rules
        self.content_category_rules: Dict[str, Dict[str, Any]] = {}
        
        # Performance settings
        self.max_concurrent_negotiations: int = 100
        self.processing_timeout_minutes: int = 30
        self.batch_processing_enabled: bool = True
        self.batch_size: int = 50
        
        # Initialize default configurations
        self._initialize_license_templates()
        self._initialize_pricing_templates()
        self._initialize_content_rules()
        
        # Load environment configurations
        self._load_from_environment()
    
    def _initialize_license_templates(self) -> None:
        """Initialize default license templates."""        # Standard non-exclusive license
        self.license_templates["standard_non_exclusive"] = {
            "license_type": LicenseType.NON_EXCLUSIVE,
            "usage_types": [UsageType.COMMERCIAL, UsageType.STREAMING],
            "territory": Territory.WORLDWIDE,
            "duration_months": 12,
            "renewable": True,
            "transferable": False,
            "attribution_required": True,
            "modifications_allowed": False,
            "commercial_use_allowed": True
        }
        
        # Exclusive license template
        self.license_templates["exclusive_premium"] = {
            "license_type": LicenseType.EXCLUSIVE,
            "usage_types": [UsageType.COMMERCIAL, UsageType.BROADCAST, UsageType.STREAMING],
            "territory": Territory.WORLDWIDE,
            "duration_months": 24,
            "renewable": True,
            "transferable": True,
            "attribution_required": True,
            "modifications_allowed": True,
            "commercial_use_allowed": True,
            "exclusivity_period_days": 30
        }
        
        # Royalty-free template
        self.license_templates["royalty_free"] = {
            "license_type": LicenseType.ROYALTY_FREE,
            "usage_types": [UsageType.COMMERCIAL, UsageType.EDITORIAL],
            "territory": Territory.WORLDWIDE,
            "duration_months": None,  # Perpetual
            "renewable": False,
            "transferable": True,
            "attribution_required": False,
            "modifications_allowed": True,
            "commercial_use_allowed": True
        }
    
    def _initialize_pricing_templates(self) -> None:
        """Initialize default pricing templates."""        # Standard royalty pricing
        self.pricing_templates["standard_royalty"] = PricingStructure(
            pricing_model=PricingModel.ROYALTY_PERCENTAGE,
            base_price=Decimal('0.00'),
            royalty_percentage=10.0,
            minimum_guarantee=Decimal('50.00'),
            payment_schedule="monthly",
            payment_terms_days=30
        )
        
        # Flat fee pricing
        self.pricing_templates["flat_fee_basic"] = PricingStructure(
            pricing_model=PricingModel.FLAT_FEE,
            base_price=Decimal('100.00'),
            payment_schedule="one_time",
            payment_terms_days=14
        )
        
        # Premium exclusive pricing
        self.pricing_templates["exclusive_premium"] = PricingStructure(
            pricing_model=PricingModel.HYBRID,
            base_price=Decimal('500.00'),
            royalty_percentage=15.0,
            minimum_guarantee=Decimal('1000.00'),
            advance_payment=Decimal('500.00'),
            payment_schedule="quarterly"
        )
    
    def _initialize_content_rules(self) -> None:
        """Initialize content-specific licensing rules."""        # Music content rules
        self.content_category_rules["music"] = {
            "default_license_type": LicenseType.RIGHTS_MANAGED,
            "allowed_usage_types": [
                UsageType.COMMERCIAL, UsageType.STREAMING, 
                UsageType.SYNCHRONIZATION, UsageType.PERFORMANCE
            ],
            "min_price": Decimal('25.00'),
            "max_discount": 15.0,
            "attribution_required": True,
            "auto_approval_threshold": Decimal('200.00')
        }
        
        # Video content rules
        self.content_category_rules["video"] = {
            "default_license_type": LicenseType.NON_EXCLUSIVE,
            "allowed_usage_types": [
                UsageType.COMMERCIAL, UsageType.BROADCAST, 
                UsageType.STREAMING, UsageType.EDITORIAL
            ],
            "min_price": Decimal('50.00'),
            "max_discount": 20.0,
            "attribution_required": True,
            "auto_approval_threshold": Decimal('300.00')
        }
        
        # Image content rules
        self.content_category_rules["image"] = {
            "default_license_type": LicenseType.ROYALTY_FREE,
            "allowed_usage_types": [
                UsageType.COMMERCIAL, UsageType.EDITORIAL, 
                UsageType.EDUCATIONAL
            ],
            "min_price": Decimal('10.00'),
            "max_discount": 25.0,
            "attribution_required": False,
            "auto_approval_threshold": Decimal('100.00')
        }
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""        # General settings
        self.enable_licensing_system = os.getenv("LICENSING_ENABLED", "true").lower() == "true"
        self.auto_licensing_enabled = os.getenv("LICENSING_AUTO_ENABLED", "true").lower() == "true"
        self.manual_approval_required = os.getenv("LICENSING_MANUAL_APPROVAL", "true").lower() == "true"
        
        threshold_str = os.getenv("LICENSING_APPROVAL_THRESHOLD", "500.00")
        self.license_approval_threshold = Decimal(threshold_str)
        
        # Performance settings
        self.max_concurrent_negotiations = int(os.getenv("LICENSING_MAX_CONCURRENT", "100"))
        self.processing_timeout_minutes = int(os.getenv("LICENSING_TIMEOUT_MINUTES", "30"))
        self.batch_size = int(os.getenv("LICENSING_BATCH_SIZE", "50"))
        
        # Automated negotiation settings
        min_price_str = os.getenv("LICENSING_MIN_PRICE", "1.00")
        self.automated_negotiation.min_acceptable_price = Decimal(min_price_str)
        
        self.automated_negotiation.max_discount_percentage = float(
            os.getenv("LICENSING_MAX_DISCOUNT", "20.0")
        )
        
        # Royalty tracking settings
        payout_threshold_str = os.getenv("LICENSING_MIN_PAYOUT", "10.00")
        self.royalty_tracking.minimum_payout_threshold = Decimal(payout_threshold_str)
        
        self.royalty_tracking.payout_schedule = os.getenv("LICENSING_PAYOUT_SCHEDULE", "monthly")
        
        # Compliance settings
        self.compliance.jurisdiction = os.getenv("LICENSING_JURISDICTION", "EU")
        self.compliance.contract_language = os.getenv("LICENSING_CONTRACT_LANGUAGE", "en")
        
        # Integration settings
        self.integration.crm_system = os.getenv("LICENSING_CRM_SYSTEM", "salesforce")
        self.integration.accounting_system = os.getenv("LICENSING_ACCOUNTING_SYSTEM", "quickbooks")
    
    def create_license_terms(self, template_name: str, **overrides) -> LicenseTerms:
        """Create license terms from template with optional overrides."""        if template_name not in self.license_templates:
            raise ValueError(f"License template not found: {template_name}")
        
        template = self.license_templates[template_name].copy()
        template.update(overrides)
        
        return LicenseTerms(**template)
    
    def create_pricing_structure(self, template_name: str, **overrides) -> PricingStructure:
        """Create pricing structure from template with optional overrides."""        if template_name not in self.pricing_templates:
            raise ValueError(f"Pricing template not found: {template_name}")
        
        template = self.pricing_templates[template_name]
        pricing_dict = template.__dict__.copy()
        pricing_dict.update(overrides)
        
        return PricingStructure(**pricing_dict)
    
    def get_content_rules(self, content_category: str) -> Dict[str, Any]:
        """Get licensing rules for specific content category."""        return self.content_category_rules.get(content_category, {
            "default_license_type": self.default_license_type,
            "allowed_usage_types": [UsageType.COMMERCIAL],
            "min_price": Decimal('10.00'),
            "max_discount": 10.0,
            "attribution_required": True,
            "auto_approval_threshold": Decimal('100.00')
        })
    
    def should_auto_approve(self, license_value: Decimal, content_category: str) -> bool:
        """Determine if license should be automatically approved."""        if not self.auto_licensing_enabled:
            return False
        
        content_rules = self.get_content_rules(content_category)
        auto_approval_threshold = content_rules.get(
            "auto_approval_threshold", 
            self.license_approval_threshold
        )
        
        return license_value <= auto_approval_threshold
    
    def calculate_license_price(self, content_category: str, usage_types: List[UsageType],
                              territory: Territory, duration_months: Optional[int] = None) -> Decimal:
        """Calculate license price based on parameters."""        content_rules = self.get_content_rules(content_category)
        base_price = content_rules.get("min_price", Decimal('10.00'))
        
        # Usage type multipliers
        usage_multipliers = {
            UsageType.COMMERCIAL: 1.5,
            UsageType.BROADCAST: 2.0,
            UsageType.STREAMING: 1.2,
            UsageType.SYNCHRONIZATION: 2.5,
            UsageType.EXCLUSIVE: 3.0
        }
        
        # Territory multipliers
        territory_multipliers = {
            Territory.WORLDWIDE: 2.0,
            Territory.NORTH_AMERICA: 1.5,
            Territory.EUROPE: 1.3,
            Territory.ASIA_PACIFIC: 1.2,
            Territory.COUNTRY_SPECIFIC: 0.8
        }
        
        # Calculate price
        price = base_price
        
        # Apply usage type multipliers
        max_usage_multiplier = max(
            [usage_multipliers.get(usage, 1.0) for usage in usage_types]
        )
        price *= Decimal(str(max_usage_multiplier))
        
        # Apply territory multiplier
        territory_multiplier = territory_multipliers.get(territory, 1.0)
        price *= Decimal(str(territory_multiplier))
        
        # Apply duration multiplier if specified
        if duration_months:
            if duration_months <= 12:
                duration_multiplier = 1.0
            elif duration_months <= 24:
                duration_multiplier = 1.8
            else:
                duration_multiplier = 2.5
            price *= Decimal(str(duration_multiplier))
        
        return price.quantize(Decimal('0.01'))
    
    def generate_counter_offer(self, original_price: Decimal, 
                             current_round: int) -> Decimal:
        """Generate counter offer in automated negotiation."""        strategy = self.automated_negotiation.counter_offer_strategy
        max_discount = self.automated_negotiation.max_discount_percentage / 100
        max_rounds = self.automated_negotiation.negotiation_rounds_limit
        
        if strategy == "fixed_rate":
            discount = max_discount * 0.5  # Fixed 50% of max discount
        elif strategy == "gradual_decrease":
            # Gradually increase discount with each round
            discount = (max_discount * current_round) / max_rounds
        else:  # market_based
            # Simple market-based adjustment (could be enhanced with real market data)
            discount = max_discount * 0.7
        
        counter_price = original_price * (Decimal('1.0') - Decimal(str(discount)))
        return counter_price.quantize(Decimal('0.01'))
    
    def validate_license_terms(self, terms: LicenseTerms) -> List[str]:
        """Validate license terms and return any issues."""        issues = []
        
        # Validate dates
        if terms.end_date and terms.end_date <= terms.start_date:
            issues.append("End date must be after start date")
        
        if terms.duration_months and terms.duration_months <= 0:
            issues.append("Duration must be positive")
        
        # Validate exclusivity
        if terms.license_type == LicenseType.EXCLUSIVE:
            if not terms.exclusivity_period_days:
                issues.append("Exclusive licenses must specify exclusivity period")
        
        # Validate usage types
        if not terms.usage_types:
            issues.append("At least one usage type must be specified")
        
        # Validate territory
        if terms.territory == Territory.COUNTRY_SPECIFIC:
            if "countries" not in terms.usage_limitations:
                issues.append("Country-specific territory must specify countries")
        
        return issues
    
    def validate_pricing_structure(self, pricing: PricingStructure) -> List[str]:
        """Validate pricing structure and return any issues."""        issues = []
        
        # Validate base price
        if pricing.base_price < 0:
            issues.append("Base price cannot be negative")
        
        # Validate royalty percentage
        if (pricing.pricing_model in [PricingModel.ROYALTY_PERCENTAGE, PricingModel.HYBRID] and
            pricing.royalty_percentage is not None):
            if not 0 <= pricing.royalty_percentage <= 100:
                issues.append("Royalty percentage must be between 0 and 100")
        
        # Validate revenue share percentage
        if pricing.revenue_share_percentage is not None:
            if not 0 <= pricing.revenue_share_percentage <= 100:
                issues.append("Revenue share percentage must be between 0 and 100")
        
        # Validate minimum guarantee
        if pricing.minimum_guarantee and pricing.minimum_guarantee < 0:
            issues.append("Minimum guarantee cannot be negative")
        
        # Validate payment terms
        if pricing.payment_terms_days <= 0:
            issues.append("Payment terms must be positive")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""        return {
            "enable_licensing_system": self.enable_licensing_system,
            "auto_licensing_enabled": self.auto_licensing_enabled,
            "manual_approval_required": self.manual_approval_required,
            "default_license_type": self.default_license_type,
            "license_approval_threshold": str(self.license_approval_threshold),
            "max_concurrent_negotiations": self.max_concurrent_negotiations,
            "processing_timeout_minutes": self.processing_timeout_minutes,
            "batch_processing_enabled": self.batch_processing_enabled,
            "batch_size": self.batch_size,
            "automated_negotiation": self.automated_negotiation.__dict__,
            "royalty_tracking": self.royalty_tracking.__dict__,
            "compliance": self.compliance.__dict__,
            "integration": self.integration.__dict__,
            "license_templates": self.license_templates,
            "content_category_rules": {
                k: {**v, "min_price": str(v["min_price"]), 
                    "auto_approval_threshold": str(v["auto_approval_threshold"])}
                for k, v in self.content_category_rules.items()
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'LicensingConfig':
        """Create configuration from dictionary."""        config = cls()
        
        # Load basic settings
        basic_fields = [
            "enable_licensing_system", "auto_licensing_enabled",
            "manual_approval_required", "max_concurrent_negotiations",
            "processing_timeout_minutes", "batch_processing_enabled", "batch_size"
        ]
        
        for field in basic_fields:
            if field in config_dict:
                setattr(config, field, config_dict[field])
        
        if "default_license_type" in config_dict:
            config.default_license_type = LicenseType(config_dict["default_license_type"])
        
        if "license_approval_threshold" in config_dict:
            config.license_approval_threshold = Decimal(config_dict["license_approval_threshold"])
        
        # Load component configurations
        component_map = {
            "automated_negotiation": config.automated_negotiation,
            "royalty_tracking": config.royalty_tracking,
            "compliance": config.compliance,
            "integration": config.integration
        }
        
        for key, component in component_map.items():
            if key in config_dict:
                for attr_key, attr_value in config_dict[key].items():
                    # Handle Decimal conversions
                    if attr_key in ["min_acceptable_price", "minimum_payout_threshold"] and isinstance(attr_value, str):
                        attr_value = Decimal(attr_value)
                    setattr(component, attr_key, attr_value)
        
        # Load templates and rules
        if "license_templates" in config_dict:
            config.license_templates = config_dict["license_templates"]
        
        if "content_category_rules" in config_dict:
            config.content_category_rules = {}
            for category, rules in config_dict["content_category_rules"].items():
                converted_rules = rules.copy()
                converted_rules["min_price"] = Decimal(rules["min_price"])
                converted_rules["auto_approval_threshold"] = Decimal(rules["auto_approval_threshold"])
                config.content_category_rules[category] = converted_rules
        
        return config
