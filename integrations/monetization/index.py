"""
Monetization - Ainflue Integrations
===================================
Point d'entrée principal pour monétisation enterprise.
Orchestration pricing, revenue optimization et analytics.

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

# Configuration logique métier Ainflue
MONETIZATION_CONFIG = {
    'pricing_models': ['freemium', 'subscription', 'pay_per_use', 'tiered', 'dynamic'],
    'revenue_streams': ['subscriptions', 'commissions', 'ads', 'premium_features', 'partnerships'],
    'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CNY', 'BTC', 'ETH'],
    'payment_processors': ['stripe', 'paypal', 'square', 'adyen', 'braintree'],
    'platforms_monetization': 65,
    'tax_jurisdictions': ['us', 'eu', 'uk', 'ca', 'au', 'global'],
    'pricing_factors': ['demand', 'competition', 'value', 'market', 'user_behavior'],
    'optimization_algorithms': ['ml_pricing', 'ab_testing', 'cohort_analysis', 'elasticity']
}

def get_monetization_manager():
    """Factory pour créer le gestionnaire principal de monétisation."""
    return {
        'pricing': IntelligentPricingEngine(),
        'revenue': RevenueOptimization(),
        'subscriptions': SubscriptionManager(),
        'dynamic': DynamicPricing(),
        'currency': MultiCurrencyManager(),
        'analytics': RevenueAnalytics(),
        'advisor': AIMonetizationAdvisor(),
        'global': GlobalMonetization()
    }