"""
💰 BUSINESS MODELS INDEX - ENTERPRISE GRADE
==========================================

Point d'entrée central pour tous les modèles Business Enterprise
Support complet: Revenue, Licensing, Payments, Subscriptions, Marketplace

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Architecture: Enterprise Business Models with advanced monetization patterns
"""

from .revenue_model import RevenueModel
from .licensing_model import LicensingModel
from .payment_model import PaymentModel
from .subscription_model import SubscriptionModel
from .marketplace_model import MarketplaceModel
from .pricing_model import PricingModel
from .premium_features_model import PremiumFeaturesModel
from .monetization_strategy_model import MonetizationStrategyModel
from .billing_model import BillingModel
from .payout_model import PayoutModel
from .financial_analytics_model import FinancialAnalyticsModel
from .recurring_revenue_model import RecurringRevenueModel
from .promotional_model import PromotionalModel
from .roi_tracking_model import ROITrackingModel

# Enterprise Business Models Collection
__all__ = [
    # Core Revenue Models
    'RevenueModel',
    'PaymentModel',
    'BillingModel',
    'PayoutModel',
    
    # Licensing & Rights
    'LicensingModel',
    'PremiumFeaturesModel',
    'MonetizationStrategyModel',
    
    # Subscription & Marketplace
    'SubscriptionModel',
    'MarketplaceModel',
    'PricingModel',
    'RecurringRevenueModel',
    
    # Analytics & Optimization
    'FinancialAnalyticsModel',
    'PromotionalModel',
    'ROITrackingModel',
]

# Enterprise Business Registry
BUSINESS_MODELS_REGISTRY = {
    'revenue': {
        'revenue': RevenueModel,
        'recurring': RecurringRevenueModel,
        'payment': PaymentModel,
        'billing': BillingModel,
        'payout': PayoutModel,
    },
    'licensing': {
        'licensing': LicensingModel,
        'premium': PremiumFeaturesModel,
        'strategy': MonetizationStrategyModel,
    },
    'marketplace': {
        'marketplace': MarketplaceModel,
        'subscription': SubscriptionModel,
        'pricing': PricingModel,
    },
    'analytics': {
        'financial': FinancialAnalyticsModel,
        'promotional': PromotionalModel,
        'roi': ROITrackingModel,
    }
}

def get_business_model(category: str, model_type: str):
    """
    Récupère un modèle Business Enterprise par catégorie et type
    
    Args:
        category: revenue, licensing, marketplace, analytics
        model_type: Type spécifique de modèle business
        
    Returns:
        Classe du modèle Business Enterprise correspondant
    """
    return BUSINESS_MODELS_REGISTRY.get(category, {}).get(model_type)

def list_available_business_models():
    """Liste tous les modèles Business Enterprise disponibles"""
    return BUSINESS_MODELS_REGISTRY

# Business Models Enterprise Stats
BUSINESS_MODELS_STATS = {
    'total_models': 14,
    'categories': 4,
    'revenue_models': 5,
    'licensing_models': 3,
    'marketplace_models': 3,
    'analytics_models': 3,
    'enterprise_ready': True,
    'monetization_complete': True,
    'multi_currency_support': True,
    'subscription_ready': True
}