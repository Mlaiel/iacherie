"""Complete Monetization Module Suite
====================================

Advanced monetization platform with comprehensive financial management,
subscription billing, payment processing, and compliance features.

Author: Fahed Mlaiel <mlaiel@live.de>
⚠️ COPYRIGHT WARNING: Proprietary code - unauthorized use prohibited.
"""

# Core monetization modules
from .licensing_manager import LicensingManager
from .royalty_engine import RoyaltyEngine
from .usage_tracker import UsageTracker
from .contract_generator import ContractGenerator
from .rights_validator import RightsValidator
from .payment_processor import PaymentProcessor
from .revenue_calculator import RevenueCalculator
from .distribution_engine import DistributionEngine
try:
    from .platform_apis import PlatformAPIManager
except ImportError:
    PlatformAPIManager = None

# Enhanced payment providers (import with error handling)
try:
    from .enhanced_payment_providers import (
        ExtendedPaymentProvider,
        MultiProviderPaymentGateway,
        CryptocurrencyProcessor,
        BankingIntegrationManager
    )
except ImportError:
    # Handle missing dependencies gracefully
    ExtendedPaymentProvider = None
    MultiProviderPaymentGateway = None
    CryptocurrencyProcessor = None
    BankingIntegrationManager = None

# Complete monetization suite - NEW MODULES
from .subscription_manager import (
    SubscriptionManager,
    SubscriptionPlan,
    Subscription,
    SubscriptionTier,
    BillingCycle,
    SubscriptionStatus
)

from .billing_engine import (
    BillingEngine,
    Invoice,
    InvoiceLineItem,
    PaymentAttempt,
    TaxRate,
    InvoiceStatus
)

from .financial_dashboard import (
    FinancialDashboard,
    FinancialMetric,
    RevenueBreakdown,
    CohortAnalysis,
    MetricType,
    TimeGranularity
)

from .accounting_compliance import (
    AccountingSystem,
    JournalEntry,
    ChartOfAccounts,
    TaxCalculation,
    FinancialReport,
    AccountingStandard
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Complete module exports
__all__ = [
    # Core licensing and rights management
    "LicensingManager",
    "RoyaltyEngine", 
    "UsageTracker",
    "ContractGenerator",
    "RightsValidator",
    
    # Payment and revenue systems
    "PaymentProcessor",
    "RevenueCalculator",
    "DistributionEngine",
    "PlatformAPIManager",
    
    # Enhanced payment providers
    "ExtendedPaymentProvider",
    "MultiProviderPaymentGateway",
    "CryptocurrencyProcessor",
    "BankingIntegrationManager",
    
    # Subscription management
    "SubscriptionManager",
    "SubscriptionPlan",
    "Subscription",
    "SubscriptionTier",
    "BillingCycle",
    "SubscriptionStatus",
    
    # Billing automation
    "BillingEngine",
    "Invoice",
    "InvoiceLineItem",
    "PaymentAttempt",
    "TaxRate",
    "InvoiceStatus",
    
    # Financial analytics
    "FinancialDashboard",
    "FinancialMetric",
    "RevenueBreakdown",
    "CohortAnalysis",
    "MetricType",
    "TimeGranularity",
    
    # Accounting and compliance
    "AccountingSystem",
    "JournalEntry",
    "ChartOfAccounts",
    "TaxCalculation",
    "FinancialReport",
    "AccountingStandard",
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
