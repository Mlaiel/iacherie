"""Complete Monetization Module
============================

Industrial-grade comprehensive monetization system with automated revenue sharing,
real-time financial dashboard, accounting export, and tax compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

# Core new modules - our main implementation
from .automated_revenue_sharing import (
    AutomatedRevenueSharingEngine,
    get_revenue_sharing_engine,
    register_content_revenue_sharing,
    distribute_content_revenue
)
from .realtime_financial_dashboard import (
    RealTimeFinancialDashboard,
    get_financial_dashboard,
    update_revenue_metric,
    update_expense_metric,
    track_transaction_volume
)
from .accounting_export_compliance import (
    AccountingExportCompliance,
    get_accounting_export,
    record_revenue_transaction,
    export_tax_report,
    TaxJurisdiction,
    ExportFormat
)

# Try to import existing modules with error handling
try:
    from .licensing_manager import LicensingManager
except ImportError:
    LicensingManager = None

try:
    from .royalty_engine import RoyaltyEngine
except ImportError:
    RoyaltyEngine = None

try:
    from .revenue_calculator import RevenueCalculator
except ImportError:
    RevenueCalculator = None

try:
    from .payment_processor import PaymentProcessor
except ImportError:
    PaymentProcessor = None

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # New core modules - always available
    "AutomatedRevenueSharingEngine",
    "get_revenue_sharing_engine", 
    "register_content_revenue_sharing",
    "distribute_content_revenue",
    "RealTimeFinancialDashboard",
    "get_financial_dashboard",
    "update_revenue_metric",
    "update_expense_metric", 
    "track_transaction_volume",
    "AccountingExportCompliance",
    "get_accounting_export",
    "record_revenue_transaction",
    "export_tax_report",
    "TaxJurisdiction",
    "ExportFormat",
]

# Add existing modules if they imported successfully
if LicensingManager:
    __all__.append("LicensingManager")
if RoyaltyEngine:
    __all__.append("RoyaltyEngine")
if RevenueCalculator:
    __all__.append("RevenueCalculator")
if PaymentProcessor:
    __all__.append("PaymentProcessor")

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
