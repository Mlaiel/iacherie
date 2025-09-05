"""Revenue Management Module - IA Influencer Agent Platform
========================================================

Enterprise-grade revenue optimization, calculation, and management system
for content creators and influencer monetization workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Architecture: 12-module revenue optimization suite
"""

from .optimization_engine import RevenueOptimizationEngine
from .attribution_tracker import RevenueAttributionTracker
from .forecasting_model import RevenueForecaster
from .sharing_calculator import RevenueSharingCalculator
from .performance_analyzer import RevenuePerformanceAnalyzer
from .tax_calculator import TaxCalculationEngine
from .commission_manager import CommissionManager
from .pricing_optimizer import PricingOptimizer
from .subscription_handler import SubscriptionHandler
from .cryptocurrency_processor import CryptocurrencyProcessor
from .escrow_manager import EscrowManager

__all__ = [
    'RevenueOptimizationEngine',
    'RevenueAttributionTracker', 
    'RevenueForecaster',
    'RevenueSharingCalculator',
    'RevenuePerformanceAnalyzer',
    'TaxCalculationEngine',
    'CommissionManager',
    'PricingOptimizer',
    'SubscriptionHandler',
    'CryptocurrencyProcessor',
    'EscrowManager'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"