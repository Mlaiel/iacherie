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

from .plan_manager import PlanManager, SubscriptionPlan, PlanFeature, plan_manager
from .subscription_manager import SubscriptionManager, Subscription, SubscriptionStatus, subscription_manager
from .quota_manager import QuotaManager, ResourceQuota, UsageTracker
from .upgrade_manager import UpgradeManager, UpgradeStrategy, UpgradeRecommendation
from .usage_analytics import UsageAnalytics, UsageReport, PredictiveAnalytics
from .pricing_intelligence_engine import PricingIntelligenceEngine, pricing_intelligence_engine
from .churn_prediction_system import ChurnPredictionSystem, churn_prediction_system
from .creator_tier_manager import CreatorTierManager, creator_tier_manager
from .subscription_automation_engine import SubscriptionAutomationEngine, subscription_automation_engine
from .subscription_lifecycle_manager import SubscriptionLifecycleManager, subscription_lifecycle_manager
from .revenue_optimization_engine import RevenueOptimizationEngine, revenue_optimization_engine
# Import nouveaux modules
from .plan_recommendation_system import PlanRecommendationSystem, plan_recommendation_system
from .usage_forecasting_engine import UsageForecastingEngine, usage_forecasting_engine
from .subscription_metrics_collector import SubscriptionMetricsCollector, subscription_metrics_collector
from .feature_flag_manager import FeatureFlagManager, feature_flag_manager
from .trial_optimization_system import TrialOptimizationSystem, trial_optimization_system
from .subscription_fraud_detector import SubscriptionFraudDetector, subscription_fraud_detector

__all__ = [
    "PlanManager",
    "plan_manager",
    "SubscriptionPlan", 
    "PlanFeature",
    "SubscriptionManager",
    "subscription_manager",
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
    "SubscriptionLifecycleManager",
    "subscription_lifecycle_manager",
    "RevenueOptimizationEngine",
    "revenue_optimization_engine",
    "PlanRecommendationSystem",
    "plan_recommendation_system",
    "UsageForecastingEngine",
    "usage_forecasting_engine",
    "SubscriptionMetricsCollector",
    "subscription_metrics_collector",
    "FeatureFlagManager",
    "feature_flag_manager",
    "TrialOptimizationSystem",
    "trial_optimization_system",
    "SubscriptionFraudDetector",
    "subscription_fraud_detector"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
