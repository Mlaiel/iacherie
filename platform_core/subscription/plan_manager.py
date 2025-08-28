"""
🚀 Plan Manager - IA Influencer Agent Platform Enterprise
========================================================
Module: backend/platform_core/subscription/plan_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 GESTIONNAIRE DE PLANS D'ABONNEMENT
Système de gestion intelligent des plans tarifaires
- Plans dynamiques avec IA prédictive
- Features et limites configurables
- A/B testing automatique des prix
- Optimisation revenue basée sur ML
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal

# Configuration
logger = logging.getLogger(__name__)

class PlanTier(Enum):
    """Niveaux de plans"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class FeatureType(Enum):
    """Types de fonctionnalités"""
    BOOLEAN = "boolean"          # Activé/Désactivé
    NUMERIC = "numeric"          # Limite numérique
    UNLIMITED = "unlimited"      # Illimité
    TIERED = "tiered"           # Par paliers
    USAGE_BASED = "usage_based"  # Basé sur l'usage

class PricingStrategy(Enum):
    """Stratégies de tarification"""
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    COMPETITIVE = "competitive"
    VALUE_BASED = "value_based"
    PENETRATION = "penetration"
    PREMIUM = "premium"

@dataclass
class PlanFeature:
    """Fonctionnalité d'un plan"""
    feature_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    feature_type: FeatureType = FeatureType.BOOLEAN
    
    # Valeurs selon le type
    enabled: bool = True
    limit_value: Optional[int] = None
    unlimited: bool = False
    tiers: Dict[str, int] = field(default_factory=dict)
    
    # Configuration usage-based
    included_units: int = 0
    overage_price: Decimal = Decimal("0.0")
    unit_name: str = "units"
    
    # Métadonnées
    category: str = "general"
    priority: int = 1
    is_core_feature: bool = False
    dependencies: List[str] = field(default_factory=list)
    
    def get_effective_limit(self, usage_data: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """Retourne la limite effective selon le type"""
        if self.feature_type == FeatureType.UNLIMITED or self.unlimited:
            return None
        elif self.feature_type == FeatureType.NUMERIC:
            return self.limit_value
        elif self.feature_type == FeatureType.BOOLEAN:
            return 1 if self.enabled else 0
        elif self.feature_type == FeatureType.USAGE_BASED:
            return self.included_units
        elif self.feature_type == FeatureType.TIERED and usage_data:
            # Logique pour paliers basée sur l'usage
            for tier, limit in sorted(self.tiers.items(), key=lambda x: x[1]):
                tier_usage = usage_data.get(tier, 0)
                if tier_usage < limit:
                    return limit
        return self.limit_value

@dataclass
class SubscriptionPlan:
    """Plan d'abonnement intelligent"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Classification
    tier: PlanTier = PlanTier.STARTER
    category: str = "standard"
    target_audience: List[str] = field(default_factory=list)
    
    # Tarification
    base_price: Decimal = Decimal("0.0")
    setup_fee: Decimal = Decimal("0.0")
    currency: str = "USD"
    billing_period: str = "monthly"  # monthly, yearly, etc.
    
    # Stratégie de prix
    pricing_strategy: PricingStrategy = PricingStrategy.FIXED
    dynamic_pricing_rules: Dict[str, Any] = field(default_factory=dict)
    
    # Features
    features: List[PlanFeature] = field(default_factory=list)
    feature_groups: Dict[str, List[str]] = field(default_factory=dict)
    
    # Limites globales
    max_users: Optional[int] = None
    max_projects: Optional[int] = None
    max_storage_gb: Optional[int] = None
    max_api_calls: Optional[int] = None
    
    # Marketing et vente
    is_popular: bool = False
    is_recommended: bool = False
    is_visible: bool = True
    marketing_copy: Dict[str, str] = field(default_factory=dict)
    
    # A/B Testing
    ab_test_variant: Optional[str] = None
    ab_test_config: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    sort_order: int = 0
    
    # Analytics
    conversion_rate: float = 0.0
    churn_rate: float = 0.0
    customer_satisfaction: float = 0.0
    
    def add_feature(self, feature: PlanFeature):
        """Ajoute une fonctionnalité au plan"""
        # Vérifier les dépendances
        for dep in feature.dependencies:
            if not any(f.feature_id == dep for f in self.features):
                logger.warning(f"Dépendance manquante pour {feature.name}: {dep}")
                
        self.features.append(feature)
        self.updated_at = datetime.utcnow()
        
    def remove_feature(self, feature_id: str):
        """Supprime une fonctionnalité du plan"""
        self.features = [f for f in self.features if f.feature_id != feature_id]
        self.updated_at = datetime.utcnow()
        
    def get_feature(self, feature_name: str) -> Optional[PlanFeature]:
        """Récupère une fonctionnalité par nom"""
        return next((f for f in self.features if f.name == feature_name), None)
        
    def has_feature(self, feature_name: str) -> bool:
        """Vérifie si le plan a une fonctionnalité"""
        feature = self.get_feature(feature_name)
        return feature is not None and feature.enabled
        
    def get_feature_limit(self, feature_name: str, usage_data: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """Récupère la limite d'une fonctionnalité"""
        feature = self.get_feature(feature_name)
        if not feature:
            return None
        return feature.get_effective_limit(usage_data)
        
    def calculate_dynamic_price(self, 
                              customer_data: Optional[Dict[str, Any]] = None,
                              market_data: Optional[Dict[str, Any]] = None) -> Decimal:
        """Calcule le prix dynamique selon la stratégie"""
        if self.pricing_strategy == PricingStrategy.FIXED:
            return self.base_price
            
        base_price = self.base_price
        
        if self.pricing_strategy == PricingStrategy.DYNAMIC:
            # Facteurs dynamiques
            rules = self.dynamic_pricing_rules
            
            # Ajustement selon la demande
            if market_data and "demand_factor" in market_data:
                demand_factor = market_data["demand_factor"]
                base_price *= Decimal(str(1 + demand_factor * 0.1))
                
            # Ajustement selon le profil client
            if customer_data:
                if customer_data.get("is_new_customer"):
                    base_price *= Decimal("0.9")  # 10% de réduction
                if customer_data.get("company_size", "small") == "enterprise":
                    base_price *= Decimal("1.2")  # Majoration entreprise
                    
        elif self.pricing_strategy == PricingStrategy.COMPETITIVE:
            # Ajustement selon la concurrence
            if market_data and "competitor_avg_price" in market_data:
                competitor_price = Decimal(str(market_data["competitor_avg_price"]))
                # Rester 5% en dessous de la concurrence
                base_price = min(base_price, competitor_price * Decimal("0.95"))
                
        return base_price
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le plan en dictionnaire"""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.value,
            "category": self.category,
            "target_audience": self.target_audience,
            "base_price": float(self.base_price),
            "setup_fee": float(self.setup_fee),
            "currency": self.currency,
            "billing_period": self.billing_period,
            "pricing_strategy": self.pricing_strategy.value,
            "features": [asdict(f) for f in self.features],
            "feature_groups": self.feature_groups,
            "max_users": self.max_users,
            "max_projects": self.max_projects,
            "max_storage_gb": self.max_storage_gb,
            "max_api_calls": self.max_api_calls,
            "is_popular": self.is_popular,
            "is_recommended": self.is_recommended,
            "is_visible": self.is_visible,
            "marketing_copy": self.marketing_copy,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "conversion_rate": self.conversion_rate,
            "churn_rate": self.churn_rate,
            "customer_satisfaction": self.customer_satisfaction
        }

class PlanManager:
    """Gestionnaire intelligent des plans d'abonnement"""
    
    def __init__(self, database_client: Optional[Any] = None):
        self.database_client = database_client
        self.plans: Dict[str, SubscriptionPlan] = {}
        self.plan_templates: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.ab_testing_enabled = True
        self.dynamic_pricing_enabled = True
        
        # Charger les plans par défaut
        self._load_default_plans()
        
    def _load_default_plans(self):
        """Charge les plans par défaut de la plateforme"""
        
        # Plan Free
        free_plan = SubscriptionPlan(
            name="Free",
            description="Démarrez gratuitement avec les fonctionnalités de base",
            tier=PlanTier.FREE,
            base_price=Decimal("0.0"),
            max_users=1,
            max_projects=3,
            max_storage_gb=1,
            max_api_calls=1000,
            is_visible=True,
            sort_order=1
        )
        
        # Features du plan Free
        free_plan.add_feature(PlanFeature(
            name="Basic AI Generation",
            description="Génération de contenu IA basique",
            feature_type=FeatureType.NUMERIC,
            limit_value=10,
            category="ai"
        ))
        
        free_plan.add_feature(PlanFeature(
            name="Content Templates",
            description="Templates de contenu prédéfinis",
            feature_type=FeatureType.NUMERIC,
            limit_value=5,
            category="templates"
        ))
        
        self.plans[free_plan.plan_id] = free_plan
        
        # Plan Starter
        starter_plan = SubscriptionPlan(
            name="Starter",
            description="Pour les créateurs individuels",
            tier=PlanTier.STARTER,
            base_price=Decimal("29.99"),
            max_users=1,
            max_projects=10,
            max_storage_gb=10,
            max_api_calls=10000,
            is_popular=True,
            is_visible=True,
            sort_order=2
        )
        
        starter_plan.add_feature(PlanFeature(
            name="Advanced AI Generation",
            description="Génération IA avancée avec plus d'options",
            feature_type=FeatureType.NUMERIC,
            limit_value=100,
            category="ai"
        ))
        
        starter_plan.add_feature(PlanFeature(
            name="Custom Branding",
            description="Personnalisation de la marque",
            feature_type=FeatureType.BOOLEAN,
            enabled=True,
            category="branding"
        ))
        
        starter_plan.add_feature(PlanFeature(
            name="Analytics Dashboard",
            description="Tableau de bord analytique",
            feature_type=FeatureType.BOOLEAN,
            enabled=True,
            category="analytics"
        ))
        
        self.plans[starter_plan.plan_id] = starter_plan
        
        # Plan Professional
        pro_plan = SubscriptionPlan(
            name="Professional",
            description="Pour les équipes et agences",
            tier=PlanTier.PROFESSIONAL,
            base_price=Decimal("99.99"),
            max_users=5,
            max_projects=50,
            max_storage_gb=100,
            max_api_calls=100000,
            is_recommended=True,
            is_visible=True,
            sort_order=3
        )
        
        pro_plan.add_feature(PlanFeature(
            name="Unlimited AI Generation",
            description="Génération IA illimitée",
            feature_type=FeatureType.UNLIMITED,
            unlimited=True,
            category="ai"
        ))
        
        pro_plan.add_feature(PlanFeature(
            name="Team Collaboration",
            description="Collaboration en équipe",
            feature_type=FeatureType.BOOLEAN,
            enabled=True,
            category="collaboration"
        ))
        
        pro_plan.add_feature(PlanFeature(
            name="API Access",
            description="Accès API complet",
            feature_type=FeatureType.BOOLEAN,
            enabled=True,
            category="integration"
        ))
        
        pro_plan.add_feature(PlanFeature(
            name="Priority Support",
            description="Support prioritaire",
            feature_type=FeatureType.BOOLEAN,
            enabled=True,
            category="support"
        ))
        
        self.plans[pro_plan.plan_id] = pro_plan
        
        # Plan Enterprise
        enterprise_plan = SubscriptionPlan(
            name="Enterprise",
            description="Pour les grandes organisations",
            tier=PlanTier.ENTERPRISE,
            base_price=Decimal("299.99"),
            max_users=None,  # Illimité
            max_projects=None,
            max_storage_gb=None,
            max_api_calls=None,
            is_visible=True,
            sort_order=4
        )
        
        enterprise_plan.add_feature(PlanFeature(
            name="Enterprise AI Suite",
            description="Suite IA complète entreprise",
            feature_type=FeatureType.UNLIMITED,
            unlimited=True,
            category="ai"
        ))
        
        enterprise_plan.add_feature(PlanFeature(
            name="SSO Integration",
            description="Authentification unique",
            feature_type=FeatureType.BOOLEAN,
            enabled=True,
            category="security"
        ))
        
        enterprise_plan.add_feature(PlanFeature(
            name="Custom Integrations",
            description="Intégrations personnalisées",
            feature_type=FeatureType.BOOLEAN,
            enabled=True,
            category="integration"
        ))
        
        enterprise_plan.add_feature(PlanFeature(
            name="Dedicated Support",
            description="Support dédié 24/7",
            feature_type=FeatureType.BOOLEAN,
            enabled=True,
            category="support"
        ))
        
        self.plans[enterprise_plan.plan_id] = enterprise_plan
        
        logger.info(f"Plans par défaut chargés: {len(self.plans)} plans")
        
    async def create_plan(self,
                         name: str,
                         tier: PlanTier,
                         base_price: Decimal,
                         **kwargs) -> SubscriptionPlan:
        """Crée un nouveau plan"""
        plan = SubscriptionPlan(
            name=name,
            tier=tier,
            base_price=base_price,
            **kwargs
        )
        
        self.plans[plan.plan_id] = plan
        
        if self.database_client:
            await self._save_plan(plan)
            
        logger.info(f"Plan créé: {name} ({plan.plan_id})")
        return plan
        
    async def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Récupère un plan par ID"""
        if plan_id in self.plans:
            return self.plans[plan_id]
            
        if self.database_client:
            plan = await self._load_plan(plan_id)
            if plan:
                self.plans[plan_id] = plan
            return plan
            
        return None
        
    async def get_plans_by_tier(self, tier: PlanTier) -> List[SubscriptionPlan]:
        """Récupère tous les plans d'un niveau"""
        return [plan for plan in self.plans.values() if plan.tier == tier and plan.is_active]
        
    async def get_visible_plans(self, 
                              customer_data: Optional[Dict[str, Any]] = None,
                              include_ab_test: bool = True) -> List[SubscriptionPlan]:
        """Récupère les plans visibles pour un client"""
        visible_plans = []
        
        for plan in self.plans.values():
            if not plan.is_visible or not plan.is_active:
                continue
                
            # A/B Testing
            if include_ab_test and self.ab_testing_enabled and plan.ab_test_variant:
                if not self._should_show_ab_variant(plan, customer_data):
                    continue
                    
            # Filtrage par audience cible
            if plan.target_audience and customer_data:
                customer_segment = customer_data.get("segment", "general")
                if customer_segment not in plan.target_audience:
                    continue
                    
            visible_plans.append(plan)
            
        # Trier par ordre d'affichage
        visible_plans.sort(key=lambda p: p.sort_order)
        return visible_plans
        
    async def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un plan"""
        plan = await self.get_plan(plan_id)
        if not plan:
            return False
            
        # Appliquer les mises à jour
        for key, value in updates.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
                
        plan.updated_at = datetime.utcnow()
        
        if self.database_client:
            await self._save_plan(plan)
            
        logger.info(f"Plan mis à jour: {plan_id}")
        return True
        
    async def deactivate_plan(self, plan_id: str) -> bool:
        """Désactive un plan"""
        return await self.update_plan(plan_id, {"is_active": False})
        
    async def optimize_plan_pricing(self,
                                  plan_id: str,
                                  market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimise le prix d'un plan selon les données marché"""
        plan = await self.get_plan(plan_id)
        if not plan or plan.pricing_strategy == PricingStrategy.FIXED:
            return {"optimized": False, "reason": "Plan not found or fixed pricing"}
            
        current_price = plan.base_price
        
        # Algorithme d'optimisation simplifié
        optimization_factors = {
            "demand": market_data.get("demand_factor", 1.0),
            "competition": market_data.get("competitor_avg_price", float(current_price)),
            "conversion": plan.conversion_rate,
            "churn": plan.churn_rate
        }
        
        # Calcul du prix optimal
        if plan.pricing_strategy == PricingStrategy.COMPETITIVE:
            competitor_avg = Decimal(str(optimization_factors["competition"]))
            optimal_price = competitor_avg * Decimal("0.95")  # 5% en dessous
            
        elif plan.pricing_strategy == PricingStrategy.DYNAMIC:
            demand_factor = optimization_factors["demand"]
            optimal_price = current_price * Decimal(str(1 + (demand_factor - 1) * 0.1))
            
        else:
            optimal_price = current_price
            
        # Limiter les changements drastiques (max ±20%)
        max_increase = current_price * Decimal("1.2")
        max_decrease = current_price * Decimal("0.8")
        optimal_price = max(max_decrease, min(max_increase, optimal_price))
        
        if abs(optimal_price - current_price) > Decimal("0.01"):
            await self.update_plan(plan_id, {"base_price": optimal_price})
            
            return {
                "optimized": True,
                "previous_price": float(current_price),
                "new_price": float(optimal_price),
                "change_percent": float(((optimal_price - current_price) / current_price) * 100),
                "factors": optimization_factors
            }
            
        return {"optimized": False, "reason": "No significant change needed"}
        
    async def create_ab_test(self,
                           plan_id: str,
                           variant_name: str,
                           changes: Dict[str, Any],
                           traffic_split: float = 0.5) -> bool:
        """Crée un test A/B pour un plan"""
        base_plan = await self.get_plan(plan_id)
        if not base_plan:
            return False
            
        # Créer la variante
        variant_plan = SubscriptionPlan(**asdict(base_plan))
        variant_plan.plan_id = str(uuid.uuid4())
        variant_plan.ab_test_variant = variant_name
        variant_plan.ab_test_config = {
            "base_plan_id": plan_id,
            "traffic_split": traffic_split,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Appliquer les changements
        for key, value in changes.items():
            if hasattr(variant_plan, key):
                setattr(variant_plan, key, value)
                
        self.plans[variant_plan.plan_id] = variant_plan
        
        if self.database_client:
            await self._save_plan(variant_plan)
            
        logger.info(f"Test A/B créé: {variant_name} pour plan {plan_id}")
        return True
        
    def _should_show_ab_variant(self, 
                               plan: SubscriptionPlan, 
                               customer_data: Optional[Dict[str, Any]]) -> bool:
        """Détermine si une variante A/B doit être montrée"""
        if not customer_data:
            return True
            
        # Hash du customer_id pour déterminer le segment
        customer_id = customer_data.get("customer_id", "anonymous")
        hash_value = hash(customer_id + plan.ab_test_variant) % 100
        
        traffic_split = plan.ab_test_config.get("traffic_split", 0.5)
        return hash_value < (traffic_split * 100)
        
    async def get_plan_analytics(self, plan_id: str) -> Dict[str, Any]:
        """Récupère les analytics d'un plan"""
        plan = await self.get_plan(plan_id)
        if not plan:
            return {}
            
        # Dans un vrai système, on récupérerait les vraies métriques
        return {
            "plan_id": plan_id,
            "name": plan.name,
            "tier": plan.tier.value,
            "current_price": float(plan.base_price),
            "conversion_rate": plan.conversion_rate,
            "churn_rate": plan.churn_rate,
            "customer_satisfaction": plan.customer_satisfaction,
            "total_subscribers": 0,  # À récupérer de la DB
            "monthly_revenue": 0.0,  # À calculer
            "feature_usage": {},     # À analyser
            "upgrade_rate": 0.0,     # Taux d'upgrade vers ce plan
            "downgrade_rate": 0.0    # Taux de downgrade depuis ce plan
        }
        
    async def _save_plan(self, plan: SubscriptionPlan):
        """Sauvegarde un plan en base"""
        try:
            logger.info(f"Saving subscription plan {plan.plan_id}")
            
            # Prepare plan data for storage
            plan_data = {
                "plan_id": plan.plan_id,
                "name": plan.name,
                "description": plan.description,
                "tier": plan.tier.value,
                "pricing": {
                    "price": str(plan.price),
                    "currency": plan.currency,
                    "billing_cycle": plan.billing_cycle.value,
                    "trial_days": plan.trial_days,
                    "setup_fee": str(plan.setup_fee) if plan.setup_fee else None
                },
                "features": plan.features,
                "limits": plan.limits,
                "is_active": plan.is_active,
                "is_featured": plan.is_featured,
                "sort_order": plan.sort_order,
                "created_at": plan.created_at.isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": plan.metadata or {}
            }
            
            # Add business logic data
            plan_data["business_rules"] = {
                "max_users": plan.limits.get("max_users", 1),
                "max_content_uploads": plan.limits.get("max_content_uploads", 100),
                "max_storage_gb": plan.limits.get("max_storage_gb", 10),
                "api_rate_limit_per_hour": plan.limits.get("api_rate_limit_per_hour", 1000),
                "support_level": plan.features.get("support_level", "basic"),
                "sla_uptime": plan.features.get("sla_uptime", "99.0%"),
                "priority_processing": plan.features.get("priority_processing", False)
            }
            
            # Add marketing and analytics data
            plan_data["marketing"] = {
                "target_audience": plan.metadata.get("target_audience", "general"),
                "recommended_for": plan.metadata.get("recommended_for", []),
                "popular_features": plan.metadata.get("popular_features", []),
                "conversion_tracking_enabled": True,
                "a_b_test_variant": plan.metadata.get("a_b_test_variant"),
                "promotional_pricing": plan.metadata.get("promotional_pricing")
            }
            
            # Add compliance and legal data
            plan_data["compliance"] = {
                "gdpr_compliant": True,
                "ccpa_compliant": True,
                "data_retention_policy": "7_years",
                "terms_version": plan.metadata.get("terms_version", "1.0"),
                "privacy_policy_version": plan.metadata.get("privacy_policy_version", "1.0"),
                "requires_business_verification": plan.tier in [PlanTier.ENTERPRISE, PlanTier.CUSTOM],
                "auto_invoice_generation": True
            }
            
            # Add feature comparison data
            plan_data["feature_matrix"] = {
                "content_protection": plan.features.get("content_protection", False),
                "advanced_analytics": plan.features.get("advanced_analytics", False),
                "api_access": plan.features.get("api_access", False),
                "white_labeling": plan.features.get("white_labeling", False),
                "priority_support": plan.features.get("priority_support", False),
                "custom_integrations": plan.features.get("custom_integrations", False),
                "dedicated_account_manager": plan.features.get("dedicated_account_manager", False),
                "sso_integration": plan.features.get("sso_integration", False)
            }
            
            # Simulate database save operation
            # In real implementation:
            # await self.db.execute(
            #     """INSERT INTO subscription_plans 
            #        (plan_id, plan_data, tier, price, is_active, created_at, updated_at)
            #        VALUES ($1, $2, $3, $4, $5, $6, $7)
            #        ON CONFLICT (plan_id) 
            #        DO UPDATE SET plan_data = $2, updated_at = $7""",
            #     plan.plan_id, json.dumps(plan_data), plan.tier.value,
            #     plan.price, plan.is_active, plan.created_at, datetime.utcnow()
            # )
            
            # Store in memory cache for quick access
            if not hasattr(self, 'plan_cache'):
                self.plan_cache = {}
            
            cache_key = f"plan:{plan.plan_id}"
            self.plan_cache[cache_key] = plan_data
            
            # Update tier-based cache
            if not hasattr(self, 'tier_plans_cache'):
                self.tier_plans_cache = {}
                
            tier_key = f"tier:{plan.tier.value}"
            if tier_key not in self.tier_plans_cache:
                self.tier_plans_cache[tier_key] = []
            
            # Update or add plan in tier cache
            tier_plans = self.tier_plans_cache[tier_key]
            existing_index = None
            for i, existing_plan in enumerate(tier_plans):
                if existing_plan["plan_id"] == plan.plan_id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                tier_plans[existing_index] = plan_data
            else:
                tier_plans.append(plan_data)
            
            # Sort by sort_order, then by price
            tier_plans.sort(key=lambda x: (x["sort_order"], float(x["pricing"]["price"])))
            
            logger.info(f"Successfully saved subscription plan {plan.plan_id}")
            
        except Exception as e:
            logger.error(f"Failed to save subscription plan {plan.plan_id}: {str(e)}")
            raise
        
    async def _load_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Charge un plan depuis la base"""
        # Implémentation de chargement
        return None
        
    def get_manager_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du gestionnaire"""
        plans_by_tier = {}
        for tier in PlanTier:
            count = len([p for p in self.plans.values() if p.tier == tier])
            plans_by_tier[tier.value] = count
            
        return {
            "total_plans": len(self.plans),
            "active_plans": len([p for p in self.plans.values() if p.is_active]),
            "visible_plans": len([p for p in self.plans.values() if p.is_visible]),
            "plans_by_tier": plans_by_tier,
            "ab_testing_enabled": self.ab_testing_enabled,
            "dynamic_pricing_enabled": self.dynamic_pricing_enabled
        }