"""
Billing Config module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Billing Configuration Module
import asyncio

======================================

Enterprise-grade billing configuration for the Ainflue platform.
Handles subscription billing, usage-based billing, invoicing, tax calculations,
automated billing processes, and comprehensive billing analytics.

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

class BillingType(str, Enum):
    """Billing types"""
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    ONE_TIME = "one_time"
    TIERED = "tiered"
    HYBRID = "hybrid"

class BillingCycle(str, Enum):
    """Billing cycles"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class TaxCalculationMethod(str, Enum):
    """Tax calculation methods"""
    INCLUSIVE = "inclusive"
    EXCLUSIVE = "exclusive"
    AUTOMATIC = "automatic"
    MANUAL = "manual"

class CurrencyCode(str, Enum):
    """Supported currency codes"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    BTC = "BTC"
    ETH = "ETH"

@dataclass
class SubscriptionBillingConfig:
    """Subscription billing configuration"""
    enable_subscription_billing: bool = True
    default_billing_cycle: BillingCycle = BillingCycle.MONTHLY
    proration_enabled: bool = True
    grace_period_days: int = 3
    
    # Subscription tiers
    subscription_tiers: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "tier_id": "basic",
            "name": "Basic Plan",
            "price": Decimal("9.99"),
            "currency": "USD",
            "billing_cycle": "monthly",
            "features": ["basic_analytics", "standard_support"],
            "trial_days": 7
        },
        {
            "tier_id": "professional",
            "name": "Professional Plan",
            "price": Decimal("29.99"),
            "currency": "USD",
            "billing_cycle": "monthly",
            "features": ["advanced_analytics", "priority_support", "collaboration_tools"],
            "trial_days": 14
        },
        {
            "tier_id": "enterprise",
            "name": "Enterprise Plan",
            "price": Decimal("99.99"),
            "currency": "USD",
            "billing_cycle": "monthly",
            "features": ["full_analytics", "dedicated_support", "white_label", "api_access"],
            "trial_days": 30
        }
    ])
    
    # Trial and freemium
    free_trial_enabled: bool = True
    freemium_tier_enabled: bool = True
    freemium_limits: Dict[str, Any] = field(default_factory=lambda: {
        "monthly_uploads": 10,
        "storage_gb": 1,
        "analytics_days": 7,
        "collaboration_projects": 1
    })
    
    # Billing automation
    auto_renewal_enabled: bool = True
    failed_payment_retries: int = 3
    retry_intervals_days: List[int] = field(default_factory=lambda: [1, 3, 7])
    dunning_process_enabled: bool = True
    
    def get_config(self) -> Dict[str, Any]:
        """Get subscription billing configuration"""
        return {
            "enable_subscription_billing": self.enable_subscription_billing,
            "default_billing_cycle": self.default_billing_cycle.value,
            "proration_enabled": self.proration_enabled,
            "grace_period_days": self.grace_period_days,
            "subscription_tiers": [
                {
                    **tier,
                    "price": float(tier["price"])
                } for tier in self.subscription_tiers
            ],
            "trial_freemium": {
                "free_trial_enabled": self.free_trial_enabled,
                "freemium_tier_enabled": self.freemium_tier_enabled,
                "freemium_limits": self.freemium_limits
            },
            "automation": {
                "auto_renewal_enabled": self.auto_renewal_enabled,
                "failed_payment_retries": self.failed_payment_retries,
                "retry_intervals_days": self.retry_intervals_days,
                "dunning_process_enabled": self.dunning_process_enabled
            }
        }

@dataclass
class UsageBasedBillingConfig:
    """Usage-based billing configuration"""
    enable_usage_billing: bool = True
    usage_metrics: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "metric_name": "api_calls",
            "unit": "call",
            "price_per_unit": Decimal("0.01"),
            "included_quantity": 1000,
            "overage_price": Decimal("0.02")
        },
        {
            "metric_name": "storage",
            "unit": "gb",
            "price_per_unit": Decimal("0.10"),
            "included_quantity": 10,
            "overage_price": Decimal("0.15")
        },
        {
            "metric_name": "bandwidth",
            "unit": "gb",
            "price_per_unit": Decimal("0.05"),
            "included_quantity": 100,
            "overage_price": Decimal("0.08")
        },
        {
            "metric_name": "ai_processing",
            "unit": "minute",
            "price_per_unit": Decimal("0.25"),
            "included_quantity": 60,
            "overage_price": Decimal("0.30")
        }
    ])
    
    # Billing aggregation
    usage_aggregation_period: str = "monthly"
    real_time_usage_tracking: bool = True
    usage_alerts_enabled: bool = True
    usage_caps_enabled: bool = True
    
    # Pricing tiers for usage
    tiered_pricing_enabled: bool = True
    usage_tiers: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "tier": 1,
            "min_quantity": 0,
            "max_quantity": 1000,
            "price_per_unit": Decimal("0.01")
        },
        {
            "tier": 2,
            "min_quantity": 1001,
            "max_quantity": 10000,
            "price_per_unit": Decimal("0.008")
        },
        {
            "tier": 3,
            "min_quantity": 10001,
            "max_quantity": None,
            "price_per_unit": Decimal("0.005")
        }
    ])
    
    def get_config(self) -> Dict[str, Any]:
        """Get usage-based billing configuration"""
        return {
            "enable_usage_billing": self.enable_usage_billing,
            "usage_metrics": [
                {
                    **metric,
                    "price_per_unit": float(metric["price_per_unit"]),
                    "overage_price": float(metric["overage_price"])
                } for metric in self.usage_metrics
            ],
            "aggregation": {
                "usage_aggregation_period": self.usage_aggregation_period,
                "real_time_usage_tracking": self.real_time_usage_tracking,
                "usage_alerts_enabled": self.usage_alerts_enabled,
                "usage_caps_enabled": self.usage_caps_enabled
            },
            "tiered_pricing": {
                "tiered_pricing_enabled": self.tiered_pricing_enabled,
                "usage_tiers": [
                    {
                        **tier,
                        "price_per_unit": float(tier["price_per_unit"])
                    } for tier in self.usage_tiers
                ]
            }
        }

@dataclass
class InvoicingConfig:
    """Invoicing configuration"""
    enable_automated_invoicing: bool = True
    invoice_numbering_format: str = "INV-{year}-{month:02d}-{sequence:06d}"
    invoice_due_days: int = 30
    
    # Invoice content
    company_info: Dict[str, str] = field(default_factory=lambda: {
        "name": "Ainflue Platform",
        "address": "123 Innovation Street, Tech City, TC 12345",
        "tax_id": "TAX-123456789",
        "email": "billing@ainflue.com",
        "phone": "+1-555-0123"
    })
    
    invoice_line_items: List[str] = field(default_factory=lambda: [
        "subscription_fees", "usage_charges", "setup_fees", 
        "support_fees", "overage_charges", "taxes"
    ])
    
    # Invoice delivery
    invoice_delivery_methods: List[str] = field(default_factory=lambda: [
        "email", "api_webhook", "postal_mail"
    ])
    default_delivery_method: str = "email"
    
    # Payment terms
    payment_terms: Dict[str, Any] = field(default_factory=lambda: {
        "net_30": {"days": 30, "discount_percentage": 0},
        "net_15": {"days": 15, "discount_percentage": 2},
        "immediate": {"days": 0, "discount_percentage": 5}
    })
    
    # Late fees
    late_fees_enabled: bool = True
    late_fee_percentage: float = 1.5  # 1.5% per month
    late_fee_grace_period_days: int = 5
    
    def get_config(self) -> Dict[str, Any]:
        """Get invoicing configuration"""
        return {
            "automation": {
                "enable_automated_invoicing": self.enable_automated_invoicing,
                "invoice_numbering_format": self.invoice_numbering_format,
                "invoice_due_days": self.invoice_due_days
            },
            "content": {
                "company_info": self.company_info,
                "invoice_line_items": self.invoice_line_items
            },
            "delivery": {
                "invoice_delivery_methods": self.invoice_delivery_methods,
                "default_delivery_method": self.default_delivery_method
            },
            "payment_terms": self.payment_terms,
            "late_fees": {
                "late_fees_enabled": self.late_fees_enabled,
                "late_fee_percentage": self.late_fee_percentage,
                "late_fee_grace_period_days": self.late_fee_grace_period_days
            }
        }

@dataclass
class TaxConfig:
    """Tax calculation configuration"""
    enable_tax_calculation: bool = True
    tax_calculation_method: TaxCalculationMethod = TaxCalculationMethod.AUTOMATIC
    tax_inclusive_pricing: bool = False
    
    # Tax providers
    tax_providers: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "avalara",
            "enabled": True,
            "priority": 1,
            "supported_regions": ["US", "CA", "EU"]
        },
        {
            "name": "taxjar",
            "enabled": True,
            "priority": 2,
            "supported_regions": ["US"]
        }
    ])
    
    # Tax rates (fallback)
    default_tax_rates: Dict[str, float] = field(default_factory=lambda: {
        "US": 0.08,     # 8% average US sales tax
        "CA": 0.13,     # 13% HST
        "GB": 0.20,     # 20% VAT
        "DE": 0.19,     # 19% VAT
        "FR": 0.20,     # 20% VAT
        "AU": 0.10,     # 10% GST
        "JP": 0.10      # 10% consumption tax
    })
    
    # Tax exemptions
    tax_exemptions_enabled: bool = True
    exempt_entity_types: List[str] = field(default_factory=lambda: [
        "non_profit", "government", "educational", "religious"
    ])
    
    # Digital services tax
    digital_services_tax_enabled: bool = True
    dst_threshold_revenue: int = 750000  # €750k threshold
    dst_rate: float = 0.03  # 3% digital services tax
    
    def get_config(self) -> Dict[str, Any]:
        """Get tax configuration"""
        return {
            "calculation": {
                "enable_tax_calculation": self.enable_tax_calculation,
                "tax_calculation_method": self.tax_calculation_method.value,
                "tax_inclusive_pricing": self.tax_inclusive_pricing
            },
            "providers": self.tax_providers,
            "rates": {
                "default_tax_rates": self.default_tax_rates
            },
            "exemptions": {
                "tax_exemptions_enabled": self.tax_exemptions_enabled,
                "exempt_entity_types": self.exempt_entity_types
            },
            "digital_services_tax": {
                "digital_services_tax_enabled": self.digital_services_tax_enabled,
                "dst_threshold_revenue": self.dst_threshold_revenue,
                "dst_rate": self.dst_rate
            }
        }

@dataclass
class BillingAnalyticsConfig:
    """Billing analytics configuration"""
    enable_billing_analytics: bool = True
    real_time_revenue_tracking: bool = True
    
    # Key metrics
    tracked_metrics: List[str] = field(default_factory=lambda: [
        "monthly_recurring_revenue", "annual_recurring_revenue",
        "average_revenue_per_user", "customer_lifetime_value",
        "churn_rate", "revenue_retention", "net_revenue_retention",
        "billing_efficiency", "collection_rate", "days_sales_outstanding"
    ])
    
    # Revenue recognition
    revenue_recognition_method: str = "accrual"  # accrual, cash
    deferred_revenue_tracking: bool = True
    
    # Reporting
    automated_reports: List[str] = field(default_factory=lambda: [
        "daily_revenue_summary", "weekly_billing_report",
        "monthly_financial_statement", "quarterly_business_review"
    ])
    
    report_recipients: List[str] = field(default_factory=lambda: [
        "finance@ainflue.com", "ceo@ainflue.com", "cfo@ainflue.com"
    ])
    
    # Alerts
    billing_alerts: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "failed_payments_spike",
            "threshold": 0.05,  # 5% failed payment rate
            "severity": "high"
        },
        {
            "name": "revenue_drop",
            "threshold": -0.10,  # 10% revenue drop
            "severity": "critical"
        },
        {
            "name": "churn_increase",
            "threshold": 0.02,  # 2% churn rate increase
            "severity": "medium"
        }
    ])
    
    def get_config(self) -> Dict[str, Any]:
        """Get billing analytics configuration"""
        return {
            "analytics": {
                "enable_billing_analytics": self.enable_billing_analytics,
                "real_time_revenue_tracking": self.real_time_revenue_tracking,
                "tracked_metrics": self.tracked_metrics
            },
            "revenue_recognition": {
                "revenue_recognition_method": self.revenue_recognition_method,
                "deferred_revenue_tracking": self.deferred_revenue_tracking
            },
            "reporting": {
                "automated_reports": self.automated_reports,
                "report_recipients": self.report_recipients
            },
            "alerts": {
                "billing_alerts": self.billing_alerts
            }
        }

class BillingConfiguration:
    """Main billing configuration manager"""
    
    def __init__(self, billing_type -> None: BillingType = BillingType.HYBRID) -> None:
        """Initialize billing configuration"""
        self.billing_type = billing_type
        
        # Billing components
        self.subscription_config = SubscriptionBillingConfig()
        self.usage_config = UsageBasedBillingConfig()
        self.invoicing_config = InvoicingConfig()
        self.tax_config = TaxConfig()
        self.analytics_config = BillingAnalyticsConfig()
        
        # Global billing settings
        self.supported_currencies = [currency for currency in CurrencyCode]
        self.default_currency = CurrencyCode.USD
        self.multi_currency_enabled = True
        
        # Payment integration
        self.payment_processors = [
            "stripe", "paypal", "square", "adyen", "braintree"
        ]
        self.default_payment_processor = "stripe"
        
        # Compliance
        self.pci_compliance_enabled = True
        self.gdpr_compliance_enabled = True
        self.sox_compliance_enabled = True
        
        self._configure_for_billing_type()
    
    def _configure_for_billing_type(self) -> None:
        """Configure based on billing type"""
        if self.billing_type == BillingType.SUBSCRIPTION:
            self.subscription_config.enable_subscription_billing = True
            self.usage_config.enable_usage_billing = False
            
        elif self.billing_type == BillingType.USAGE_BASED:
            self.subscription_config.enable_subscription_billing = False
            self.usage_config.enable_usage_billing = True
            
        elif self.billing_type == BillingType.HYBRID:
            self.subscription_config.enable_subscription_billing = True
            self.usage_config.enable_usage_billing = True
    
    def calculate_bill_amount(self, 
                            customer_data: Dict[str, Any],
                            usage_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate bill amount for a customer"""
        total_amount = Decimal("0.00")
        line_items = []
        
        # Subscription charges
        if self.subscription_config.enable_subscription_billing:
            subscription_tier = customer_data.get("subscription_tier")
            if subscription_tier:
                for tier in self.subscription_config.subscription_tiers:
                    if tier["tier_id"] == subscription_tier:
                        total_amount += tier["price"]
                        line_items.append({
                            "description": f"{tier['name']} Subscription",
                            "amount": float(tier["price"]),
                            "type": "subscription"
                        })
                        break
        
        # Usage charges
        if self.usage_config.enable_usage_billing and usage_data:
            for metric in self.usage_config.usage_metrics:
                metric_name = metric["metric_name"]
                if metric_name in usage_data:
                    usage_quantity = usage_data[metric_name]
                    included_quantity = metric["included_quantity"]
                    
                    if usage_quantity > included_quantity:
                        overage_quantity = usage_quantity - included_quantity
                        overage_amount = overage_quantity * metric["overage_price"]
                        total_amount += overage_amount
                        
                        line_items.append({
                            "description": f"{metric_name.replace('_', ' ').title()} Overage",
                            "quantity": overage_quantity,
                            "unit_price": float(metric["overage_price"]),
                            "amount": float(overage_amount),
                            "type": "usage"
                        })
        
        # Calculate taxes
        tax_amount = Decimal("0.00")
        if self.tax_config.enable_tax_calculation:
            country_code = customer_data.get("country", "US")
            tax_rate = self.tax_config.default_tax_rates.get(country_code, 0.0)
            tax_amount = total_amount * Decimal(str(tax_rate))
            
            line_items.append({
                "description": f"Tax ({tax_rate * 100:.1f}%)",
                "amount": float(tax_amount),
                "type": "tax"
            })
        
        return {
            "subtotal": float(total_amount),
            "tax_amount": float(tax_amount),
            "total_amount": float(total_amount + tax_amount),
            "currency": self.default_currency.value,
            "line_items": line_items
        }
    
    def get_billing_cycle_config(self, cycle: BillingCycle) -> Dict[str, Any]:
        """Get configuration for specific billing cycle"""
        cycle_configs = {
            BillingCycle.MONTHLY: {
                "interval": 1,
                "interval_unit": "month",
                "proration_enabled": True,
                "grace_period_days": 3
            },
            BillingCycle.YEARLY: {
                "interval": 1,
                "interval_unit": "year",
                "proration_enabled": False,
                "grace_period_days": 7,
                "discount_percentage": 10  # 10% annual discount
            },
            BillingCycle.QUARTERLY: {
                "interval": 3,
                "interval_unit": "month",
                "proration_enabled": True,
                "grace_period_days": 5
            }
        }
        
        return cycle_configs.get(cycle, cycle_configs[BillingCycle.MONTHLY])
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete billing configuration"""
        return {
            "billing_type": self.billing_type.value,
            "subscription": self.subscription_config.get_config(),
            "usage_based": self.usage_config.get_config(),
            "invoicing": self.invoicing_config.get_config(),
            "tax": self.tax_config.get_config(),
            "analytics": self.analytics_config.get_config(),
            "global_settings": {
                "supported_currencies": [currency.value for currency in self.supported_currencies],
                "default_currency": self.default_currency.value,
                "multi_currency_enabled": self.multi_currency_enabled,
                "payment_processors": self.payment_processors,
                "default_payment_processor": self.default_payment_processor
            },
            "compliance": {
                "pci_compliance_enabled": self.pci_compliance_enabled,
                "gdpr_compliance_enabled": self.gdpr_compliance_enabled,
                "sox_compliance_enabled": self.sox_compliance_enabled
            }
        }
    
    async def process_billing_cycle(self, customer_id: str) -> Dict[str, Any]:
        """Process billing cycle for a customer"""
        # This would implement the actual billing cycle processing
        # Including charge calculation, invoice generation, payment processing
        return {
            "customer_id": customer_id,
            "billing_date": datetime.now().isoformat(),
            "status": "processed",
            "invoice_generated": True,
            "payment_attempted": True
        }

# Global billing configuration instance
billing_config = BillingConfiguration()

# Export main classes
__all__ = [
    "BillingConfiguration",
    "BillingType",
    "BillingCycle",
    "TaxCalculationMethod",
    "CurrencyCode",
    "SubscriptionBillingConfig",
    "UsageBasedBillingConfig",
    "InvoicingConfig",
    "TaxConfig",
    "BillingAnalyticsConfig",
    "billing_config"
]
