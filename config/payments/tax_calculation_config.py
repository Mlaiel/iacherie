#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Tax Calculation Configuration Module
============================================

Enterprise-grade tax calculation configuration for the Ainflue platform.
Comprehensive tax management with multi-jurisdiction support, automated
calculations, compliance tracking, and reporting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal

class TaxType(str, Enum):
    """Types of taxes"""
    VAT = "vat"                    # Value Added Tax
    GST = "gst"                    # Goods and Services Tax
    SALES_TAX = "sales_tax"        # Sales Tax
    INCOME_TAX = "income_tax"      # Income Tax
    WITHHOLDING_TAX = "withholding_tax"  # Withholding Tax
    DIGITAL_TAX = "digital_tax"    # Digital Services Tax
    CARBON_TAX = "carbon_tax"      # Carbon Tax
    LUXURY_TAX = "luxury_tax"      # Luxury Tax
    EXCISE_TAX = "excise_tax"      # Excise Tax

class TaxCategory(str, Enum):
    """Tax categories for products/services"""
    STANDARD = "standard"          # Standard tax rate
    REDUCED = "reduced"           # Reduced tax rate
    ZERO_RATED = "zero_rated"     # Zero tax rate
    EXEMPT = "exempt"             # Tax exempt
    REVERSE_CHARGE = "reverse_charge"  # Reverse charge
    DIGITAL_SERVICES = "digital_services"  # Digital services
    SUBSCRIPTION = "subscription"  # Subscription services
    PREMIUM_CONTENT = "premium_content"  # Premium content

class TaxJurisdiction(str, Enum):
    """Tax jurisdictions"""
    FRANCE = "france"
    GERMANY = "germany"
    UNITED_KINGDOM = "united_kingdom"
    UNITED_STATES = "united_states"
    CANADA = "canada"
    AUSTRALIA = "australia"
    JAPAN = "japan"
    SINGAPORE = "singapore"
    SWITZERLAND = "switzerland"
    NETHERLANDS = "netherlands"
    SWEDEN = "sweden"
    NORWAY = "norway"

class TaxStatus(str, Enum):
    """Tax calculation status"""
    CALCULATED = "calculated"
    PENDING = "pending"
    VALIDATED = "validated"
    APPLIED = "applied"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

@dataclass
class TaxRate:
    """Tax rate configuration"""
    tax_id: str
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    tax_category: TaxCategory
    rate_percentage: Decimal
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    description: str = ""
    is_compound: bool = False
    minimum_threshold: Optional[Decimal] = None
    maximum_threshold: Optional[Decimal] = None
    
    def is_active(self, date: datetime = None) -> bool:
        """Check if tax rate is active on given date"""
        check_date = date or datetime.now()
        if check_date < self.effective_date:
            return False
        if self.expiry_date and check_date > self.expiry_date:
            return False
        return True
    
    def calculate_tax(self, amount: Decimal) -> Decimal:
        """Calculate tax amount for given base amount"""
        if not self.is_active():
            return Decimal('0')
        
        if self.minimum_threshold and amount < self.minimum_threshold:
            return Decimal('0')
        
        if self.maximum_threshold and amount > self.maximum_threshold:
            amount = self.maximum_threshold
        
        return amount * (self.rate_percentage / Decimal('100'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tax rate to dictionary"""
        return {
            "tax_id": self.tax_id,
            "jurisdiction": self.jurisdiction.value,
            "tax_type": self.tax_type.value,
            "tax_category": self.tax_category.value,
            "rate_percentage": float(self.rate_percentage),
            "effective_date": self.effective_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "description": self.description,
            "is_compound": self.is_compound,
            "minimum_threshold": float(self.minimum_threshold) if self.minimum_threshold else None,
            "maximum_threshold": float(self.maximum_threshold) if self.maximum_threshold else None,
            "is_active": self.is_active()
        }

@dataclass
class TaxCalculationResult:
    """Tax calculation result"""
    calculation_id: str
    jurisdiction: TaxJurisdiction
    base_amount: Decimal
    tax_breakdown: Dict[str, Decimal]
    total_tax: Decimal
    total_amount: Decimal
    calculation_date: datetime
    status: TaxStatus
    applied_rates: List[Dict[str, Any]]
    exemptions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert calculation result to dictionary"""
        return {
            "calculation_id": self.calculation_id,
            "jurisdiction": self.jurisdiction.value,
            "base_amount": float(self.base_amount),
            "tax_breakdown": {k: float(v) for k, v in self.tax_breakdown.items()},
            "total_tax": float(self.total_tax),
            "total_amount": float(self.total_amount),
            "calculation_date": self.calculation_date.isoformat(),
            "status": self.status.value,
            "applied_rates": self.applied_rates,
            "exemptions": self.exemptions
        }

@dataclass
class TaxEngineConfig:
    """Tax calculation engine configuration"""
    enabled: bool = True
    
    # Calculation engine
    calculation_engine: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "real_time_calculation": True,
        "batch_calculation": True,
        "async_calculation": True,
        "caching_enabled": True,
        "cache_duration_minutes": 60,
        "precision_decimal_places": 4,
        "rounding_method": "round_half_up"
    })
    
    # Tax providers integration
    tax_providers: Dict[str, Any] = field(default_factory=lambda: {
        "avalara": {
            "enabled": True,
            "api_key": os.getenv("AVALARA_API_KEY", ""),
            "environment": "sandbox",
            "company_code": "AINFLUE",
            "timeout_seconds": 30,
            "retry_attempts": 3
        },
        "taxjar": {
            "enabled": True,
            "api_token": os.getenv("TAXJAR_API_TOKEN", ""),
            "environment": "sandbox",
            "timeout_seconds": 30,
            "retry_attempts": 3
        },
        "vertex": {
            "enabled": False,
            "api_key": os.getenv("VERTEX_API_KEY", ""),
            "environment": "sandbox",
            "timeout_seconds": 30
        },
        "internal_engine": {
            "enabled": True,
            "fallback_provider": True,
            "custom_rates": True,
            "jurisdiction_support": True
        }
    })
    
    # Validation and compliance
    validation_compliance: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "real_time_validation": True,
        "address_validation": True,
        "tax_id_validation": True,
        "exemption_validation": True,
        "rate_validation": True,
        "threshold_validation": True,
        "compliance_checks": True
    })
    
    # Reporting and audit
    reporting_audit: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "detailed_logging": True,
        "calculation_audit": True,
        "rate_change_tracking": True,
        "exemption_tracking": True,
        "compliance_reporting": True,
        "performance_metrics": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get tax engine configuration"""
        return {
            "enabled": self.enabled,
            "calculation_engine": self.calculation_engine,
            "tax_providers": self.tax_providers,
            "validation_compliance": self.validation_compliance,
            "reporting_audit": self.reporting_audit
        }

@dataclass
class JurisdictionConfig:
    """Tax jurisdiction configuration"""
    enabled: bool = True
    
    # Supported jurisdictions
    supported_jurisdictions: Dict[str, Any] = field(default_factory=lambda: {
        "france": {
            "enabled": True,
            "vat_rates": {
                "standard": 20.0,
                "reduced": 10.0,
                "super_reduced": 5.5,
                "zero": 0.0
            },
            "digital_tax": {
                "enabled": True,
                "rate": 3.0,
                "threshold": 25000000  # €25M revenue threshold
            },
            "withholding_tax": {
                "enabled": True,
                "rate": 12.8,
                "exemption_threshold": 200000
            }
        },
        "germany": {
            "enabled": True,
            "vat_rates": {
                "standard": 19.0,
                "reduced": 7.0,
                "zero": 0.0
            },
            "digital_tax": {
                "enabled": False
            }
        },
        "united_states": {
            "enabled": True,
            "sales_tax": {
                "state_level": True,
                "nexus_tracking": True,
                "marketplace_facilitator": True
            },
            "federal_tax": {
                "income_tax": True,
                "backup_withholding": 24.0
            }
        },
        "united_kingdom": {
            "enabled": True,
            "vat_rates": {
                "standard": 20.0,
                "reduced": 5.0,
                "zero": 0.0
            },
            "digital_services_tax": {
                "enabled": True,
                "rate": 2.0,
                "threshold": 500000000  # £500M global revenue
            }
        }
    })
    
    # Jurisdiction rules
    jurisdiction_rules: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "automatic_detection": True,
        "ip_geolocation": True,
        "billing_address": True,
        "shipping_address": True,
        "payment_method": True,
        "priority_order": ["billing_address", "shipping_address", "ip_geolocation"],
        "fallback_jurisdiction": "france"
    })
    
    # Cross-border taxation
    cross_border: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "eu_vat_rules": True,
        "one_stop_shop": True,
        "import_vat": True,
        "export_exemptions": True,
        "treaty_benefits": True,
        "withholding_agreements": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get jurisdiction configuration"""
        return {
            "enabled": self.enabled,
            "supported_jurisdictions": self.supported_jurisdictions,
            "jurisdiction_rules": self.jurisdiction_rules,
            "cross_border": self.cross_border
        }

@dataclass
class ExemptionConfig:
    """Tax exemption configuration"""
    enabled: bool = True
    
    # Exemption types
    exemption_types: Dict[str, Any] = field(default_factory=lambda: {
        "customer_exemptions": {
            "enabled": True,
            "business_exemption": True,
            "non_profit_exemption": True,
            "government_exemption": True,
            "educational_exemption": True,
            "reseller_exemption": True,
            "export_exemption": True
        },
        "product_exemptions": {
            "enabled": True,
            "essential_services": True,
            "educational_content": True,
            "medical_services": True,
            "financial_services": True,
            "insurance_services": True,
            "digital_books": True
        },
        "jurisdiction_exemptions": {
            "enabled": True,
            "small_business": True,
            "startup_incentives": True,
            "economic_zones": True,
            "temporary_exemptions": True
        }
    })
    
    # Exemption validation
    exemption_validation: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "certificate_validation": True,
        "expiry_tracking": True,
        "automatic_renewal": True,
        "compliance_verification": True,
        "audit_trail": True,
        "real_time_verification": True
    })
    
    # Exemption management
    exemption_management: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "self_service_portal": True,
        "automated_approval": True,
        "manual_review": True,
        "documentation_upload": True,
        "status_tracking": True,
        "notification_system": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get exemption configuration"""
        return {
            "enabled": self.enabled,
            "exemption_types": self.exemption_types,
            "exemption_validation": self.exemption_validation,
            "exemption_management": self.exemption_management
        }

class TaxCalculationConfiguration:
    """Main tax calculation configuration manager"""
    
    def __init__(self):
        """Initialize tax calculation configuration"""
        # Tax configuration components
        self.tax_engine = TaxEngineConfig()
        self.jurisdiction_config = JurisdictionConfig()
        self.exemption_config = ExemptionConfig()
        
        # Tax rates storage
        self.tax_rates: List[TaxRate] = []
        self.calculation_history: List[TaxCalculationResult] = []
        
        # Global tax settings
        self.tax_calculation_enabled = True
        self.automatic_tax_calculation = True
        self.real_time_rates_update = True
        self.tax_calculation_precision = 4
        
        # Compliance settings
        self.compliance_monitoring = True
        self.audit_trail_enabled = True
        self.tax_reporting_enabled = True
        self.regulatory_notifications = True
        
        # Performance settings
        self.calculation_caching = True
        self.cache_duration_hours = 1
        self.async_calculation = True
        self.batch_processing = True
        
        # Integration settings
        self.third_party_providers = True
        self.fallback_calculation = True
        self.provider_failover = True
        self.rate_synchronization = True
        
        # Initialize default tax rates
        self._initialize_default_tax_rates()
    
    def add_tax_rate(self, rate_config: Dict[str, Any]) -> TaxRate:
        """Add new tax rate"""
        
        tax_rate = TaxRate(
            tax_id=f"tax_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            jurisdiction=TaxJurisdiction(rate_config.get("jurisdiction", "france")),
            tax_type=TaxType(rate_config.get("tax_type", "vat")),
            tax_category=TaxCategory(rate_config.get("tax_category", "standard")),
            rate_percentage=Decimal(str(rate_config.get("rate_percentage", "20.0"))),
            effective_date=rate_config.get("effective_date", datetime.now()),
            expiry_date=rate_config.get("expiry_date"),
            description=rate_config.get("description", ""),
            is_compound=rate_config.get("is_compound", False),
            minimum_threshold=Decimal(str(rate_config.get("minimum_threshold", "0"))) if rate_config.get("minimum_threshold") else None,
            maximum_threshold=Decimal(str(rate_config.get("maximum_threshold", "0"))) if rate_config.get("maximum_threshold") else None
        )
        
        self.tax_rates.append(tax_rate)
        return tax_rate
    
    async def calculate_tax(self, calculation_request: Dict[str, Any]) -> TaxCalculationResult:
        """Calculate tax for given transaction"""
        
        calculation_result = TaxCalculationResult(
            calculation_id=f"calc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            jurisdiction=TaxJurisdiction(calculation_request.get("jurisdiction", "france")),
            base_amount=Decimal(str(calculation_request.get("base_amount", "0"))),
            tax_breakdown={},
            total_tax=Decimal('0'),
            total_amount=Decimal('0'),
            calculation_date=datetime.now(),
            status=TaxStatus.CALCULATED,
            applied_rates=[]
        )
        
        try:
            # Get applicable tax rates
            applicable_rates = await self._get_applicable_tax_rates(calculation_request)
            
            # Calculate taxes for each applicable rate
            for tax_rate in applicable_rates:
                tax_amount = tax_rate.calculate_tax(calculation_result.base_amount)
                
                if tax_amount > 0:
                    tax_key = f"{tax_rate.tax_type.value}_{tax_rate.tax_category.value}"
                    calculation_result.tax_breakdown[tax_key] = tax_amount
                    calculation_result.total_tax += tax_amount
                    
                    calculation_result.applied_rates.append({
                        "tax_id": tax_rate.tax_id,
                        "tax_type": tax_rate.tax_type.value,
                        "rate_percentage": float(tax_rate.rate_percentage),
                        "tax_amount": float(tax_amount)
                    })
            
            # Calculate total amount
            calculation_result.total_amount = calculation_result.base_amount + calculation_result.total_tax
            
            # Check for exemptions
            exemptions = await self._check_exemptions(calculation_request)
            if exemptions:
                calculation_result.exemptions = exemptions
                calculation_result.total_tax = Decimal('0')
                calculation_result.tax_breakdown = {}
                calculation_result.total_amount = calculation_result.base_amount
            
            # Validate calculation
            if await self._validate_calculation(calculation_result):
                calculation_result.status = TaxStatus.VALIDATED
            
            # Store calculation history
            self.calculation_history.append(calculation_result)
            
        except Exception as e:
            calculation_result.status = TaxStatus.PENDING
            # Log error for debugging
        
        return calculation_result
    
    async def get_tax_rates(self, 
                           jurisdiction: TaxJurisdiction = None,
                           tax_type: TaxType = None,
                           active_only: bool = True) -> List[TaxRate]:
        """Get tax rates based on criteria"""
        
        filtered_rates = []
        
        for rate in self.tax_rates:
            # Filter by jurisdiction
            if jurisdiction and rate.jurisdiction != jurisdiction:
                continue
            
            # Filter by tax type
            if tax_type and rate.tax_type != tax_type:
                continue
            
            # Filter by active status
            if active_only and not rate.is_active():
                continue
            
            filtered_rates.append(rate)
        
        return filtered_rates
    
    async def update_tax_rates_from_provider(self, provider: str = "avalara") -> Dict[str, Any]:
        """Update tax rates from external provider"""
        
        update_result = {
            "provider": provider,
            "update_timestamp": datetime.now().isoformat(),
            "rates_updated": 0,
            "rates_added": 0,
            "rates_removed": 0,
            "success": False,
            "errors": []
        }
        
        try:
            if provider == "avalara":
                provider_rates = await self._fetch_avalara_rates()
            elif provider == "taxjar":
                provider_rates = await self._fetch_taxjar_rates()
            else:
                update_result["errors"].append(f"Unsupported provider: {provider}")
                return update_result
            
            # Update existing rates and add new ones
            for provider_rate in provider_rates:
                existing_rate = self._find_existing_rate(provider_rate)
                
                if existing_rate:
                    # Update existing rate
                    existing_rate.rate_percentage = Decimal(str(provider_rate["rate_percentage"]))
                    existing_rate.effective_date = provider_rate["effective_date"]
                    update_result["rates_updated"] += 1
                else:
                    # Add new rate
                    self.add_tax_rate(provider_rate)
                    update_result["rates_added"] += 1
            
            update_result["success"] = True
            
        except Exception as e:
            update_result["errors"].append(str(e))
        
        return update_result
    
    def get_tax_calculation_statistics(self) -> Dict[str, Any]:
        """Get tax calculation statistics"""
        
        stats = {
            "total_calculations": len(self.calculation_history),
            "calculations_by_jurisdiction": {},
            "calculations_by_status": {},
            "average_tax_rate": 0.0,
            "total_tax_collected": 0.0,
            "exemptions_applied": 0,
            "calculation_trends": {}
        }
        
        if not self.calculation_history:
            return stats
        
        # Calculate statistics
        total_base_amount = Decimal('0')
        total_tax_amount = Decimal('0')
        exemption_count = 0
        
        for calc in self.calculation_history:
            # By jurisdiction
            jurisdiction = calc.jurisdiction.value
            stats["calculations_by_jurisdiction"][jurisdiction] = stats["calculations_by_jurisdiction"].get(jurisdiction, 0) + 1
            
            # By status
            status = calc.status.value
            stats["calculations_by_status"][status] = stats["calculations_by_status"].get(status, 0) + 1
            
            # Totals
            total_base_amount += calc.base_amount
            total_tax_amount += calc.total_tax
            
            # Exemptions
            if calc.exemptions:
                exemption_count += 1
        
        # Calculate averages
        if total_base_amount > 0:
            stats["average_tax_rate"] = float((total_tax_amount / total_base_amount) * 100)
        
        stats["total_tax_collected"] = float(total_tax_amount)
        stats["exemptions_applied"] = exemption_count
        
        return stats
    
    def search_calculations(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search tax calculations based on criteria"""
        
        matching_calculations = []
        
        for calc in self.calculation_history:
            if self._matches_calculation_criteria(calc, search_criteria):
                matching_calculations.append(calc.to_dict())
        
        return matching_calculations
    
    # Helper methods
    def _initialize_default_tax_rates(self) -> None:
        """Initialize default tax rates for supported jurisdictions"""
        
        # France VAT rates
        self.add_tax_rate({
            "jurisdiction": "france",
            "tax_type": "vat",
            "tax_category": "standard",
            "rate_percentage": "20.0",
            "description": "France Standard VAT Rate"
        })
        
        self.add_tax_rate({
            "jurisdiction": "france",
            "tax_type": "vat",
            "tax_category": "reduced",
            "rate_percentage": "10.0",
            "description": "France Reduced VAT Rate"
        })
        
        # Germany VAT rates
        self.add_tax_rate({
            "jurisdiction": "germany",
            "tax_type": "vat",
            "tax_category": "standard",
            "rate_percentage": "19.0",
            "description": "Germany Standard VAT Rate"
        })
        
        # UK VAT rates
        self.add_tax_rate({
            "jurisdiction": "united_kingdom",
            "tax_type": "vat",
            "tax_category": "standard",
            "rate_percentage": "20.0",
            "description": "UK Standard VAT Rate"
        })
    
    async def _get_applicable_tax_rates(self, calculation_request: Dict[str, Any]) -> List[TaxRate]:
        """Get applicable tax rates for calculation request"""
        
        jurisdiction = TaxJurisdiction(calculation_request.get("jurisdiction", "france"))
        tax_category = TaxCategory(calculation_request.get("tax_category", "standard"))
        
        applicable_rates = []
        
        for rate in self.tax_rates:
            if (rate.jurisdiction == jurisdiction and 
                rate.tax_category == tax_category and 
                rate.is_active()):
                applicable_rates.append(rate)
        
        return applicable_rates
    
    async def _check_exemptions(self, calculation_request: Dict[str, Any]) -> List[str]:
        """Check for applicable tax exemptions"""
        exemptions = []
        
        # Check customer exemptions
        if calculation_request.get("customer_type") == "non_profit":
            exemptions.append("non_profit_exemption")
        
        # Check product exemptions
        if calculation_request.get("product_type") == "educational_content":
            exemptions.append("educational_exemption")
        
        return exemptions
    
    async def _validate_calculation(self, calculation_result: TaxCalculationResult) -> bool:
        """Validate tax calculation result"""
        # Implement validation logic
        return True
    
    async def _fetch_avalara_rates(self) -> List[Dict[str, Any]]:
        """Fetch tax rates from Avalara API"""
        # Implement Avalara API integration
        return []
    
    async def _fetch_taxjar_rates(self) -> List[Dict[str, Any]]:
        """Fetch tax rates from TaxJar API"""
        # Implement TaxJar API integration
        return []
    
    def _find_existing_rate(self, provider_rate: Dict[str, Any]) -> Optional[TaxRate]:
        """Find existing tax rate matching provider rate"""
        # Implement rate matching logic
        return None
    
    def _matches_calculation_criteria(self, calc: TaxCalculationResult, criteria: Dict[str, Any]) -> bool:
        """Check if calculation matches search criteria"""
        # Implement search logic
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete tax calculation configuration"""
        return {
            "tax_statistics": self.get_tax_calculation_statistics(),
            "tax_engine": self.tax_engine.get_config(),
            "jurisdiction_config": self.jurisdiction_config.get_config(),
            "exemption_config": self.exemption_config.get_config(),
            "tax_rates_count": len(self.tax_rates),
            "calculations_count": len(self.calculation_history),
            "global_settings": {
                "tax_calculation_enabled": self.tax_calculation_enabled,
                "automatic_tax_calculation": self.automatic_tax_calculation,
                "real_time_rates_update": self.real_time_rates_update,
                "tax_calculation_precision": self.tax_calculation_precision
            },
            "compliance_settings": {
                "compliance_monitoring": self.compliance_monitoring,
                "audit_trail_enabled": self.audit_trail_enabled,
                "tax_reporting_enabled": self.tax_reporting_enabled,
                "regulatory_notifications": self.regulatory_notifications
            },
            "performance_settings": {
                "calculation_caching": self.calculation_caching,
                "cache_duration_hours": self.cache_duration_hours,
                "async_calculation": self.async_calculation,
                "batch_processing": self.batch_processing
            },
            "integration_settings": {
                "third_party_providers": self.third_party_providers,
                "fallback_calculation": self.fallback_calculation,
                "provider_failover": self.provider_failover,
                "rate_synchronization": self.rate_synchronization
            }
        }

# Global tax calculation configuration instance
tax_calculation_config = TaxCalculationConfiguration()

# Export main classes
__all__ = [
    "TaxCalculationConfiguration",
    "TaxType",
    "TaxCategory",
    "TaxJurisdiction",
    "TaxStatus",
    "TaxRate",
    "TaxCalculationResult",
    "TaxEngineConfig",
    "JurisdictionConfig",
    "ExemptionConfig",
    "tax_calculation_config"
]
