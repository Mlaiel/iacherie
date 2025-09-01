"""Monetization and Licensing Engine Module  
=========================================

Comprehensive monetization system with advanced licensing, billing, payment processing,
fraud detection, and subscription management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

# Legacy licensing components
from .licensing_manager import LicensingManager
from .royalty_engine import RoyaltyEngine
from .usage_tracker import UsageTracker
from .contract_generator import ContractGenerator
from .rights_validator import RightsValidator
from .payment_processor import PaymentProcessor, PaymentTransaction, PaymentProvider, PaymentStatus, PaymentType

# New comprehensive billing features
from .billing_engine import (
    ComprehensiveBillingEngine,
    BillingCycle,
    InvoiceStatus,
    SubscriptionStatus,
    FraudRiskLevel,
    TaxRate,
    Invoice,
    Subscription,
    FraudAnalysis,
    RevenueRecognition
)

from .subscription_manager import (
    AdvancedSubscriptionManager,
    SubscriptionAction,
    ProrationMethod,
    SubscriptionPlan,
    SubscriptionModification
)

from .fraud_detector import (
    AdvancedFraudDetector,
    FraudSignal,
    ActionType,
    FraudRule,
    TransactionContext,
    FraudEvent
)

from .enhanced_payment_providers import (
    EnhancedMultiProviderPaymentService,
    ExtendedPaymentProvider,
    PaymentProviderConfig
)

from .billing_api import billing_router

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Legacy licensing
    "LicensingManager",
    "RoyaltyEngine",
    "UsageTracker",
    "ContractGenerator",
    "RightsValidator",
    "PaymentProcessor",
    "PaymentTransaction", 
    "PaymentProvider",
    "PaymentStatus",
    "PaymentType",
    
    # Comprehensive billing engine
    "ComprehensiveBillingEngine",
    "BillingCycle",
    "InvoiceStatus",
    "SubscriptionStatus",
    "FraudRiskLevel",
    "TaxRate",
    "Invoice",
    "Subscription",
    "FraudAnalysis",
    "RevenueRecognition",
    
    # Advanced subscription management
    "AdvancedSubscriptionManager",
    "SubscriptionAction",
    "ProrationMethod",
    "SubscriptionPlan",
    "SubscriptionModification",
    
    # Fraud detection
    "AdvancedFraudDetector",
    "FraudSignal",
    "ActionType",
    "FraudRule",
    "TransactionContext",
    "FraudEvent",
    
    # Enhanced payment providers
    "EnhancedMultiProviderPaymentService",
    "ExtendedPaymentProvider",
    "PaymentProviderConfig",
    
    # API router
    "billing_router"
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

def create_license(content_id: int, licensee_id: int, license_type: str, terms: dict):
    """
Create new content license."""
    manager = get_licensing_manager()
    return manager.create_license(content_id, licensee_id, license_type, terms)

def track_usage(license_id: int, usage_type: str, usage_data: dict):
    """
Track license usage."""
    manager = get_licensing_manager()
    return manager.track_usage(license_id, usage_type, usage_data)

def calculate_royalties(license_id: int, period_start: str, period_end: str):
    """
Calculate royalties for license period."""
    manager = get_licensing_manager()
    return manager.calculate_royalties(license_id, period_start, period_end)
