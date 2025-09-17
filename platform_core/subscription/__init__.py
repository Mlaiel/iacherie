"""🚀 Platform Core Subscription Management - IA Influencer Agent Platform Enterprise
================================================================================
Module: backend/platform_core/subscription/
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE GESTION D'ABONNEMENTS ENTERPRISE
Gestion complète des plans et abonnements avec intelligence artificielle
- Plans tarifaires dynamiques et personnalisés
- Limites et quotas en temps réel
- Upgrades/downgrades automatiques et intelligents
- Analytics d'utilisation et recommandations IA
"""

from .plan_manager import PlanManager, SubscriptionPlan, PlanFeature
from .subscription_manager import SubscriptionManager, Subscription, SubscriptionStatus
from .quota_manager import QuotaManager, ResourceQuota, UsageTracker
from .upgrade_manager import UpgradeManager, UpgradeStrategy, UpgradeRecommendation
from .usage_analytics import UsageAnalytics, UsageReport, PredictiveAnalytics
from .pricing_intelligence_engine import PricingIntelligenceEngine, pricing_intelligence_engine
from .churn_prediction_system import ChurnPredictionSystem, churn_prediction_system
from .creator_tier_manager import CreatorTierManager, creator_tier_manager
from .subscription_automation_engine import SubscriptionAutomationEngine, subscription_automation_engine
# from .plan_optimizer import PlanOptimizer, OptimizationStrategy, PlanRecommendation

__all__ = [
    "PlanManager",
    "SubscriptionPlan", 
    "PlanFeature",
    "SubscriptionManager",
    "Subscription",
    "SubscriptionStatus",
    "QuotaManager",
    "ResourceQuota",
    "UsageTracker",
    "UpgradeManager",
    "UpgradeStrategy",
    "UpgradeRecommendation",
    "UsageAnalytics",
    "UsageReport", 
    "PredictiveAnalytics",
    "PricingIntelligenceEngine",
    "pricing_intelligence_engine",
    "ChurnPredictionSystem",
    "churn_prediction_system",
    "CreatorTierManager",
    "creator_tier_manager",
    "SubscriptionAutomationEngine",
    "subscription_automation_engine",
    # "PlanOptimizer",
    # "OptimizationStrategy",
    # "PlanRecommendation"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
