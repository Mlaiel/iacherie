"""
Monetization Module - Ainflue Integrations
==========================================
Module de monétisation enterprise avec pricing intelligent,
optimisation revenue et analytics business avancés.

Support pour:
- Pricing dynamique et intelligent
- Optimisation revenue multi-plateformes  
- Gestion abonnements et paiements
- Analytics ROI et performance
- Multi-devises et compliance fiscale

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

from .intelligent_pricing_engine import IntelligentPricingEngine
from .revenue_optimization import RevenueOptimization
from .subscription_manager import SubscriptionManager
from .dynamic_pricing import DynamicPricing
from .multi_currency_manager import MultiCurrencyManager
from .revenue_analytics import RevenueAnalytics
from .ai_monetization_advisor import AIMonetizationAdvisor
from .global_monetization import GlobalMonetization

__all__ = [
    'IntelligentPricingEngine',
    'RevenueOptimization',
    'SubscriptionManager', 
    'DynamicPricing',
    'MultiCurrencyManager',
    'RevenueAnalytics',
    'AIMonetizationAdvisor',
    'GlobalMonetization'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Monetization enterprise - Pricing intelligent et revenue optimization"