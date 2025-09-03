"""Complete Monetization Engine Module  
=====================================

Comprehensive monetization platform with multi-currency payments, subscription management,
automated billing, financial analytics, cryptocurrency support, and tax compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

# Core monetization modules
from .licensing_manager import LicensingManager
from .royalty_engine import RoyaltyEngine
from .usage_tracker import UsageTracker
from .contract_generator import ContractGenerator
from .rights_validator import RightsValidator
from .payment_processor import PaymentProcessor
from .revenue_calculator import RevenueCalculator

# Enhanced monetization modules
from .billing_engine import BillingEngine, BillingPlan, Subscription, BillingCycle, PlanTier
from .financial_dashboard import FinancialDashboard, financial_dashboard, RevenueType, MetricPeriod
from .crypto_gateway import CryptoPaymentGateway, CryptoCurrency, PaymentRequest, crypto_gateway
from .tax_compliance import TaxComplianceEngine, TaxJurisdiction, TaxCalculation, tax_engine
from .subscription_manager import SubscriptionManager, CustomerSegment, subscription_manager

# Convenience imports
from .financial_dashboard import track_revenue_event, get_dashboard_data
from .crypto_gateway import create_crypto_payment, get_crypto_rates
from .tax_compliance import calculate_transaction_tax, export_financial_data
from .subscription_manager import create_trial_subscription, upgrade_subscription

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core modules
    "LicensingManager",
    "RoyaltyEngine", 
    "UsageTracker",
    "ContractGenerator",
    "RightsValidator",
    "PaymentProcessor",
    "RevenueCalculator",
    
    # Enhanced modules
    "BillingEngine",
    "FinancialDashboard",
    "CryptoPaymentGateway", 
    "TaxComplianceEngine",
    "SubscriptionManager",
    
    # Data classes
    "BillingPlan",
    "Subscription",
    "PaymentRequest",
    "TaxCalculation",
    
    # Enums
    "BillingCycle",
    "PlanTier",
    "RevenueType",
    "MetricPeriod",
    "CryptoCurrency",
    "TaxJurisdiction",
    "CustomerSegment",
    
    # Global instances
    "financial_dashboard",
    "crypto_gateway", 
    "tax_engine",
    "subscription_manager",
    
    # Convenience functions
    "track_revenue_event",
    "get_dashboard_data",
    "create_crypto_payment",
    "get_crypto_rates",
    "calculate_transaction_tax",
    "export_financial_data",
    "create_trial_subscription",
    "upgrade_subscription",
]

# Licensing configuration
LICENSING_CONFIG = {
    "licensing_tiers": {
        "basic": {
            "price": 10.0,
            "duration_days": 30,
            "usage_limits": {"downloads": 100, "streams": 1000},
            "commercial_use": False
        },
        "standard": {
            "price": 50.0,
            "duration_days": 90,
            "usage_limits": {"downloads": 500, "streams": 10000},
            "commercial_use": True
        },
        "premium": {
            "price": 200.0,
            "duration_days": 365,
            "usage_limits": {"downloads": 2000, "streams": 50000},
            "commercial_use": True,
            "exclusive": True
        }
    },
    "royalty_rates": {
        "streaming": 0.004,  # per stream
        "download": 0.1,     # per download
        "sync": 0.15,        # sync licensing
        "commercial": 0.25   # commercial usage
    },
    "auto_licensing": {
        "enabled": True,
        "approval_threshold": 100.0,  # Auto-approve under this amount
        "payment_terms": "net_30",
        "default_territory": "worldwide"
    }
}

# Global licensing manager instance
_licensing_manager = None

def get_licensing_manager():
    """Get global licensing manager instance."""
    global _licensing_manager
    if _licensing_manager is None:
        _licensing_manager = LicensingManager()
    return _licensing_manager

async def create_license(content_id: int, licensee_id: int, license_type: str, terms: dict):
    """
Create new content license."""
    manager = get_licensing_manager()
    return await manager.create_license(content_id, licensee_id, license_type, terms)

async def track_usage(license_id: int, usage_type: str, usage_data: dict):
    """
Track license usage."""
    manager = get_licensing_manager()
    return await manager.track_usage(license_id, usage_type, usage_data)

async def calculate_royalties(license_id: int, period_start: str, period_end: str):
    """
Calculate royalties for license period."""
    manager = get_licensing_manager()
    return await manager.calculate_royalties(license_id, period_start, period_end)
