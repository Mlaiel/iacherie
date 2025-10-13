"""💰 Revenue Management System
==============================

Enterprise revenue management system for creator monetization,
revenue splits, analytics, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Existing modules
from .revenue_split_calculator import RevenueSplitCalculator
from .creator_revenue_manager import CreatorRevenueManager
from .monetization_optimizer import MonetizationOptimizer
from .revenue_analytics_engine import RevenueAnalyticsEngine
from .payout_orchestrator import PayoutOrchestrator
from .commission_calculator import CommissionCalculator
from .royalty_distribution_engine import RoyaltyDistributionEngine

# New Phase 1 modules - Core Revenue Systems
from .subscription_revenue_manager import SubscriptionRevenueManager
from .performance_incentive_engine import PerformanceIncentiveEngine
from .tax_withholding_calculator import TaxWithholdingCalculator
from .revenue_forecasting_engine import RevenueForecastingEngine

# New Phase 2 modules - Advanced Revenue Systems
from .marketplace_revenue_manager import MarketplaceRevenueManager
from .collaboration_revenue_splitter import CollaborationRevenueSplitter

# New Phase 3 modules - Enterprise Features (December 2025)
from .tiered_pricing_calculator import TieredPricingCalculator
from .revenue_recovery_manager import RevenueRecoveryManager
from .multi_currency_revenue_manager import MultiCurrencyRevenueManager
from .revenue_compliance_validator import RevenueComplianceValidator

__all__ = [
    # Existing modules
    "RevenueSplitCalculator",
    "CreatorRevenueManager", 
    "MonetizationOptimizer",
    "RevenueAnalyticsEngine",
    "PayoutOrchestrator",
    "CommissionCalculator",
    "RoyaltyDistributionEngine",
    
    # Phase 1 - Core Revenue Modules
    "SubscriptionRevenueManager",
    "PerformanceIncentiveEngine", 
    "TaxWithholdingCalculator",
    "RevenueForecastingEngine",
    
    # Phase 2 - Advanced Revenue Systems
    "MarketplaceRevenueManager",
    "CollaborationRevenueSplitter",
    
    # Phase 3 - Enterprise Features (December 2025)
    "TieredPricingCalculator",
    "RevenueRecoveryManager", 
    "MultiCurrencyRevenueManager",
    "RevenueComplianceValidator"
]