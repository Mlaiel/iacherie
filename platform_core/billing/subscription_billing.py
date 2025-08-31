"""
 Subscription Billing - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/platform_core/billing/subscription_billing.py
Author: Fahed Mlaiel (mlaiel@live.de)
===============================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

 SYSTÈME D'ABONNEMENTS ET FACTURATION RÉCURRENTE
Gestion complète des abonnements SaaS avec billing automatique
- Plans tarifaires flexibles et modulaires
- Prorata automatique et changements de plan
- Usage-based billing et facturation à l'usage
- Gestion des essais gratuits et coupons
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import calendar

# Configuration
logger = logging.getLogger(__name__)

class BillingPeriod(Enum):
    """Périodes de facturation"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class SubscriptionStatus(Enum):
    """États des abonnements"""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    PAUSED = "paused"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"

class PricingModel(Enum):
    """Modèles de tarification"""
    FLAT_RATE = "flat_rate"
    PER_UNIT = "per_unit"
    TIERED = "tiered"
    VOLUME = "volume"
    PACKAGE = "package"
    USAGE_BASED = "usage_based"

class ProrationPolicy(Enum):
    """Politiques de prorata"""
    IMMEDIATE = "immediate"
    END_OF_PERIOD = "end_of_period"
    CREATE_CREDIT = "create_credit"
    NO_PRORATION = "no_proration"

@dataclass
class PricingTier:
    """Niveau de tarification"""
    tier_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    min_quantity: int = 0
    max_quantity: Optional[int] = None
    unit_price: Decimal = Decimal("0.0")
    flat_fee: Decimal = Decimal("0.0")
    
    def calculate_cost(self, quantity: int) -> Decimal:
        """Calcule le coût pour une quantité donnée"""
        if self.max_quantity and quantity > self.max_quantity:
            quantity = self.max_quantity
        if quantity < self.min_quantity:
            return Decimal("0.0")
            
        effective_quantity = max(0, quantity - self.min_quantity)
        return self.flat_fee + (effective_quantity * self.unit_price)

@dataclass
class SubscriptionFeature:
    """Fonctionnalité d'abonnement"""
    feature_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    feature_type: str = "boolean"  # boolean, numeric, text
    default_value: Any = None
    limits: Dict[str, Any] = field(default_factory=dict)
    
    # Facturation à l'usage
    is_metered: bool = False
    unit_price: Decimal = Decimal("0.0")
    included_units: int = 0
    overage_price: Decimal = Decimal("0.0")

@dataclass
class SubscriptionPlan:
    """Plan d'abonnement"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Tarification
    pricing_model: PricingModel = PricingModel.FLAT_RATE
    base_price: Decimal = Decimal("0.0")
    setup_fee: Decimal = Decimal("0.0")
    currency: str = "USD"
    
    # Période de facturation
    billing_period: BillingPeriod = BillingPeriod.MONTHLY
    billing_period_count: int = 1  # ex: tous les 3 mois
    
    # Tarification par niveaux
    pricing_tiers: List[PricingTier] = field(default_factory=list)
    
    # Fonctionnalités incluses
    features: List[SubscriptionFeature] = field(default_factory=list)
    feature_limits: Dict[str, Any] = field(default_factory=dict)
    
    # Essai gratuit
    trial_period_days: int = 0
    
    # Métadonnées
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_price(self, quantity: int = 1, usage_data: Optional[Dict[str, int]] = None) -> Decimal:
        """Calcule le prix selon le modèle tarifaire"""
        if self.pricing_model == PricingModel.FLAT_RATE:
            return self.base_price
            
        elif self.pricing_model == PricingModel.PER_UNIT:
            return self.base_price * Decimal(str(quantity))
            
        elif self.pricing_model == PricingModel.TIERED:
            total = Decimal("0.0")
            remaining_quantity = quantity
            
            for tier in sorted(self.pricing_tiers, key=lambda t: t.min_quantity):
                if remaining_quantity <= 0:
                    break
                    
                tier_quantity = remaining_quantity
                if tier.max_quantity:
                    tier_quantity = min(tier_quantity, tier.max_quantity - tier.min_quantity)
                    
                total += tier.calculate_cost(tier_quantity)
                remaining_quantity -= tier_quantity
                
            return total
            
        elif self.pricing_model == PricingModel.VOLUME:
            # Toute la quantité au prix du niveau applicable
            applicable_tier = None
            for tier in sorted(self.pricing_tiers, key=lambda t: t.min_quantity, reverse=True):
                if quantity >= tier.min_quantity:
                    applicable_tier = tier
                    break
                    
            if applicable_tier:
                return applicable_tier.unit_price * Decimal(str(quantity)) + applicable_tier.flat_fee
            return self.base_price
            
        elif self.pricing_model == PricingModel.USAGE_BASED:
            total = self.base_price  # Prix de base
            
            if usage_data:
                for feature in self.features:
                    if feature.is_metered and feature.name in usage_data:
                        usage = usage_data[feature.name]
                        overage = max(0, usage - feature.included_units)
                        total += overage * feature.overage_price
                        
            return total
            
        return self.base_price

@dataclass
class Subscription:
    """Abonnement client"""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    plan_id: str = ""
    
    # État
    status: SubscriptionStatus = SubscriptionStatus.TRIAL
    current_period_start: datetime = field(default_factory=datetime.utcnow)
    current_period_end: datetime = field(default_factory=datetime.utcnow)
    
    # Essai gratuit
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    
    # Facturation
    quantity: int = 1
    unit_amount: Decimal = Decimal("0.0")
    
    # Dates importantes
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Configuration
    proration_behavior: ProrationPolicy = ProrationPolicy.IMMEDIATE
    collection_method: str = "charge_automatically"  # ou "send_invoice"
    
    # Coupons et remises
    coupon_id: Optional[str] = None
    discount_percentage: Decimal = Decimal("0.0")
    discount_amount: Decimal = Decimal("0.0")
    
    # Données d'utilisation
    usage_data: Dict[str, int] = field(default_factory=dict)
    
    # Métadonnées
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Vérifie si l'abonnement est actif"""



        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]
        
    @property
    def is_in_trial(self) -> bool:
        """Vérifie si l'abonnement est en période d'essai"""
        if not self.trial_end:
            return False
        return self.status == SubscriptionStatus.TRIAL and datetime.utcnow() <= self.trial_end
        
    @property
    def days_until_renewal(self) -> int:
        """Nombre de jours avant le renouvellement"""
        if self.current_period_end:
            delta = self.current_period_end - datetime.utcnow()
            return max(0, delta.days)
        return 0

@dataclass
class BillingCycle:
    """Cycle de facturation"""
    cycle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subscription_id: str = ""
    
    # Période
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    
    # Montants
    subtotal: Decimal = Decimal("0.0")
    tax_amount: Decimal = Decimal("0.0")
    discount_amount: Decimal = Decimal("0.0")
    total_amount: Decimal = Decimal("0.0")
    
    # État
    status: str = "draft"  # draft, finalized, paid
    invoice_id: Optional[str] = None
    
    # Données d'utilisation pour cette période
    usage_records: List[Dict[str, Any]] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)

class SubscriptionBilling:
    """Gestionnaire de facturation d'abonnements"""
    
    def __init__(self, 
                 invoice_manager: Any,
                 payment_processor: Any,
                 database_client: Optional[Any] = None):
        self.invoice_manager = invoice_manager
        self.payment_processor = payment_processor
        self.database_client = database_client
        
        # Cache des plans
        self.plans_cache: Dict[str, SubscriptionPlan] = {}
        self.subscriptions_cache: Dict[str, Subscription] = {}
        
    async def create_plan(self, 
                         name: str,
                         base_price: Decimal,
                         billing_period: BillingPeriod = BillingPeriod.MONTHLY,
                         **kwargs) -> SubscriptionPlan:
        """Crée un nouveau plan d'abonnement"""
        plan = SubscriptionPlan(
            name=name,
            base_price=base_price,
            billing_period=billing_period,
            **kwargs
        )
        
        # Sauvegarder en base
        if self.database_client:
            await self._save_plan(plan)
            
        self.plans_cache[plan.plan_id] = plan
        
        logger.info(f"Plan créé: {name} ({plan.plan_id})")
        return plan
        
    async def subscribe_customer(self,
                               customer_id: str,
                               plan_id: str,
                               quantity: int = 1,
                               start_trial: bool = False,
                               **kwargs) -> Subscription:
        """Abonne un client à un plan"""
        plan = await self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan non trouvé: {plan_id}")
            
        # Créer l'abonnement
        subscription = Subscription(
            customer_id=customer_id,
            plan_id=plan_id,
            quantity=quantity,
            unit_amount=plan.base_price,
            **kwargs
        )
        
        # Configurer l'essai gratuit
        if start_trial and plan.trial_period_days > 0:
            subscription.status = SubscriptionStatus.TRIAL
            subscription.trial_start = datetime.utcnow()
            subscription.trial_end = datetime.utcnow() + timedelta(days=plan.trial_period_days)
            subscription.current_period_end = subscription.trial_end
        else:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.started_at = datetime.utcnow()
            subscription.current_period_end = self._calculate_next_billing_date(plan)
            
        # Sauvegarder
        if self.database_client:
            await self._save_subscription(subscription)
            
        self.subscriptions_cache[subscription.subscription_id] = subscription
        
        logger.info(f"Client {customer_id} abonné au plan {plan.name}")
        return subscription
        
    async def change_subscription_plan(self,
                                     subscription_id: str,
                                     new_plan_id: str,
                                     proration_policy: ProrationPolicy = ProrationPolicy.IMMEDIATE) -> Subscription:
        """Change le plan d'un abonnement"""
        subscription = await self.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Abonnement non trouvé: {subscription_id}")
            
        old_plan = await self.get_plan(subscription.plan_id)
        new_plan = await self.get_plan(new_plan_id)
        
        if not new_plan:
            raise ValueError(f"Nouveau plan non trouvé: {new_plan_id}")
            
        # Calculer la prorata si nécessaire
        if proration_policy == ProrationPolicy.IMMEDIATE:
            await self._handle_plan_change_proration(subscription, old_plan, new_plan)
            
        # Mettre à jour l'abonnement
        subscription.plan_id = new_plan_id
        subscription.unit_amount = new_plan.base_price
        
        if proration_policy == ProrationPolicy.END_OF_PERIOD:
            # Le changement prend effet à la fin de la période courante
            subscription.metadata["pending_plan_change"] = {
                "new_plan_id": new_plan_id,
                "effective_date": subscription.current_period_end.isoformat()
            }
        else:
            # Recalculer la période de facturation
            subscription.current_period_end = self._calculate_next_billing_date(new_plan, subscription.current_period_start)
            
        await self.update_subscription(subscription)
        
        logger.info(f"Plan changé pour abonnement {subscription_id}: {old_plan.name} -> {new_plan.name}")
        return subscription
        
    async def cancel_subscription(self,
                                subscription_id: str,
                                immediate: bool = False,
                                reason: str = "") -> Subscription:
        """Annule un abonnement"""
        subscription = await self.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Abonnement non trouvé: {subscription_id}")
            
        subscription.canceled_at = datetime.utcnow()
        subscription.metadata["cancellation_reason"] = reason
        
        if immediate:
            subscription.status = SubscriptionStatus.CANCELED
            subscription.ended_at = datetime.utcnow()
            subscription.current_period_end = datetime.utcnow()
        else:
            # Annulation à la fin de la période courante
            subscription.status = SubscriptionStatus.CANCELED
            subscription.ended_at = subscription.current_period_end
            
        await self.update_subscription(subscription)
        
        logger.info(f"Abonnement {subscription_id} annulé (immédiat: {immediate})")
        return subscription
        
    async def pause_subscription(self,
                               subscription_id: str,
                               resume_date: Optional[datetime] = None) -> Subscription:
        """Met en pause un abonnement"""
        subscription = await self.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Abonnement non trouvé: {subscription_id}")
            
        subscription.status = SubscriptionStatus.PAUSED
        if resume_date:
            subscription.metadata["resume_date"] = resume_date.isoformat()
            
        await self.update_subscription(subscription)
        
        logger.info(f"Abonnement {subscription_id} mis en pause")
        return subscription
        
    async def record_usage(self,
                          subscription_id: str,
                          feature_name: str,
                          quantity: int,
                          timestamp: Optional[datetime] = None):
        """Enregistre l'utilisation d'une fonctionnalité mesurée"""
        subscription = await self.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Abonnement non trouvé: {subscription_id}")
            
        if feature_name not in subscription.usage_data:
            subscription.usage_data[feature_name] = 0
            
        subscription.usage_data[feature_name] += quantity
        
        # Enregistrer l'historique d'utilisation
        usage_record = {
            "feature_name": feature_name,
            "quantity": quantity,
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
            "subscription_id": subscription_id
        }
        
        # Ici, on sauvegarderait l'usage record en base
        # await self._save_usage_record(usage_record)
        
        await self.update_subscription(subscription)
        
        logger.debug(f"Usage enregistré pour {subscription_id}: {feature_name} = {quantity}")
        
    async def process_recurring_billing(self) -> List[Dict[str, Any]]:
        """Traite la facturation récurrente pour tous les abonnements"""
        results = []
        
        # Récupérer les abonnements à facturer
        due_subscriptions = await self._get_subscriptions_due_for_billing()
        
        for subscription in due_subscriptions:
            try:
                result = await self._process_subscription_billing(subscription)
                results.append({
                    "subscription_id": subscription.subscription_id,
                    "status": "success",
                    "invoice_id": result.get("invoice_id"),
                    "amount": result.get("amount")
                })
            except Exception as e:
                logger.error(f"Erreur lors de la facturation de {subscription.subscription_id}: {e}")
                results.append({
                    "subscription_id": subscription.subscription_id,
                    "status": "error",
                    "error": str(e)
                })
                
        logger.info(f"Facturation récurrente traitée: {len(results)} abonnements")
        return results
        
    async def _process_subscription_billing(self, subscription: Subscription) -> Dict[str, Any]:
        """Traite la facturation d'un abonnement spécifique"""
        plan = await self.get_plan(subscription.plan_id)
        if not plan:
            raise ValueError(f"Plan non trouvé: {subscription.plan_id}")
            
        # Créer le cycle de facturation
        cycle = BillingCycle(
            subscription_id=subscription.subscription_id,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end
        )
        
        # Calculer le montant
        base_amount = plan.calculate_price(subscription.quantity, subscription.usage_data)
        
        # Appliquer les remises
        discount = Decimal("0.0")
        if subscription.discount_percentage > 0:
            discount = base_amount * (subscription.discount_percentage / Decimal("100"))
        elif subscription.discount_amount > 0:
            discount = subscription.discount_amount
            
        cycle.subtotal = base_amount
        cycle.discount_amount = discount
        cycle.total_amount = base_amount - discount
        
        # Créer la facture
        invoice = await self.invoice_manager.create_invoice(
            customer_id=subscription.customer_id,
            due_at=datetime.utcnow() + timedelta(days=30)
        )
        
        # Ajouter les lignes de facture
        invoice.add_item(
            description=f"{plan.name} - {cycle.period_start.strftime('%Y-%m-%d')} à {cycle.period_end.strftime('%Y-%m-%d')}",
            quantity=Decimal(str(subscription.quantity)),
            unit_price=plan.base_price
        )
        
        # Ajouter l'usage si applicable
        for feature_name, usage in subscription.usage_data.items():
            feature = next((f for f in plan.features if f.name == feature_name), None)
            if feature and feature.is_metered:
                overage = max(0, usage - feature.included_units)
                if overage > 0:
                    invoice.add_item(
                        description=f"Usage supplémentaire - {feature_name}",
                        quantity=Decimal(str(overage)),
                        unit_price=feature.overage_price
                    )
                    
        # Enregistrer la facture
        cycle.invoice_id = invoice.invoice_id
        cycle.status = "finalized"
        
        # Mettre à jour l'abonnement pour la prochaine période
        subscription.current_period_start = subscription.current_period_end
        subscription.current_period_end = self._calculate_next_billing_date(plan, subscription.current_period_start)
        
        # Reset de l'usage pour la nouvelle période
        subscription.usage_data = {}
        
        await self.update_subscription(subscription)
        
        return {
            "invoice_id": invoice.invoice_id,
            "amount": cycle.total_amount,
            "cycle_id": cycle.cycle_id
        }
        
    def _calculate_next_billing_date(self, plan: SubscriptionPlan, from_date: Optional[datetime] = None) -> datetime:
        """Calcule la prochaine date de facturation"""
        start_date = from_date or datetime.utcnow()
        
        if plan.billing_period == BillingPeriod.DAILY:
            return start_date + timedelta(days=plan.billing_period_count)
        elif plan.billing_period == BillingPeriod.WEEKLY:
            return start_date + timedelta(weeks=plan.billing_period_count)
        elif plan.billing_period == BillingPeriod.MONTHLY:
            # Ajouter des mois en gérant les fins de mois
            month = start_date.month
            year = start_date.year
            
            month += plan.billing_period_count
            while month > 12:
                month -= 12
                year += 1
                
            # Gérer les fins de mois (ex: 31 janvier -> 28 février)
            day = min(start_date.day, calendar.monthrange(year, month)[1])
            
            return start_date.replace(year=year, month=month, day=day)
        elif plan.billing_period == BillingPeriod.YEARLY:
            return start_date.replace(year=start_date.year + plan.billing_period_count)
        else:
            return start_date + timedelta(days=30)  # Par défaut
            
    async def _handle_plan_change_proration(self,
                                          subscription: Subscription,
                                          old_plan: SubscriptionPlan,
                                          new_plan: SubscriptionPlan):
        """Gère la prorata lors d'un changement de plan"""
        now = datetime.utcnow()
        
        # Calculer la période restante
        total_period = (subscription.current_period_end - subscription.current_period_start).total_seconds()
        remaining_period = (subscription.current_period_end - now).total_seconds()
        
        if total_period <= 0:
            return
            
        proration_factor = Decimal(str(remaining_period / total_period))
        
        # Crédit pour l'ancien plan
        old_amount = old_plan.base_price * subscription.quantity * proration_factor
        
        # Charge pour le nouveau plan
        new_amount = new_plan.base_price * subscription.quantity * proration_factor
        
        # Différence à facturer/créditer
        difference = new_amount - old_amount
        
        if difference != 0:
            # Créer une facture de prorata
            invoice = await self.invoice_manager.create_invoice(
                customer_id=subscription.customer_id,
                due_at=now + timedelta(days=1)  # Due immédiatement
            )
            
            if difference > 0:
                invoice.add_item(
                    description=f"Prorata - Upgrade vers {new_plan.name}",
                    quantity=Decimal("1"),
                    unit_price=difference
                )
            else:
                invoice.add_item(
                    description=f"Prorata - Crédit pour changement vers {new_plan.name}",
                    quantity=Decimal("1"),
                    unit_price=difference  # Négatif
                )
                
    async def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Récupère un plan par ID"""
        if plan_id in self.plans_cache:
            return self.plans_cache[plan_id]
            
        if self.database_client:
            plan = await self._load_plan(plan_id)
            if plan:
                self.plans_cache[plan_id] = plan
            return plan
            
        return None
        
    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Récupère un abonnement par ID"""
        if subscription_id in self.subscriptions_cache:
            return self.subscriptions_cache[subscription_id]
            
        if self.database_client:
            subscription = await self._load_subscription(subscription_id)
            if subscription:
                self.subscriptions_cache[subscription_id] = subscription
            return subscription
            
        return None
        
    async def update_subscription(self, subscription: Subscription):
        """Met à jour un abonnement"""
        if self.database_client:
            await self._save_subscription(subscription)
        self.subscriptions_cache[subscription.subscription_id] = subscription
        
    async def _get_subscriptions_due_for_billing(self) -> List[Subscription]:
        """Récupère les abonnements à facturer"""
        # Dans un vrai système, on ferait une requête en base
        # pour récupérer les abonnements dont current_period_end <= maintenant
        return []
        
    async def _save_plan(self, plan: SubscriptionPlan):
        """Sauvegarde un plan en base"""



        try:
            # In a real system, this would save to database
            plan_data = {
                "plan_id": plan.plan_id,
                "name": plan.name,
                "price": float(plan.price),
                "currency": plan.currency,
                "billing_interval": plan.billing_interval,
                "features": plan.features,
                "is_active": plan.is_active
            }
            
            # Simulate database save
            logger.info(f"Subscription plan saved: {plan.plan_id}")
            logger.debug(f"Plan data: {json.dumps(plan_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error saving subscription plan: {e}")
        
    async def _load_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Charge un plan depuis la base"""



        try:
            # In a real system, this would load from database
            # For now, return a default plan if the ID matches common patterns
            if plan_id in ["basic", "premium", "pro"]:
                plan_configs = {
                    "basic": {"name": "Basic Plan", "price": Decimal("9.99"), "features": ["basic_access"]},
                    "premium": {"name": "Premium Plan", "price": Decimal("19.99"), "features": ["premium_access", "analytics"]},
                    "pro": {"name": "Pro Plan", "price": Decimal("39.99"), "features": ["pro_access", "analytics", "collaboration"]}
                }
                
                config = plan_configs.get(plan_id)
                if config:
                    from .subscription_billing import SubscriptionPlan  # Local import to avoid circular import
                    return SubscriptionPlan(
                        plan_id=plan_id,
                        name=config["name"],
                        price=config["price"],
                        currency="EUR",
                        billing_interval="monthly",
                        features=config["features"],
                        is_active=True
                    )
            
            logger.debug(f"Subscription plan not found: {plan_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading subscription plan {plan_id}: {e}")
            return None
        
    async def _save_subscription(self, subscription: Subscription):
        """Sauvegarde un abonnement en base"""



        try:
            # In a real system, this would save to database
            subscription_data = {
                "subscription_id": subscription.subscription_id,
                "user_id": subscription.user_id,
                "plan_id": subscription.plan_id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start.isoformat(),
                "current_period_end": subscription.current_period_end.isoformat(),
                "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
                "created_at": subscription.created_at.isoformat()
            }
            
            # Simulate database save
            logger.info(f"Subscription saved: {subscription.subscription_id}")
            logger.debug(f"Subscription data: {json.dumps(subscription_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error saving subscription: {e}")
        
    async def _load_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Charge un abonnement depuis la base"""



        try:
            # In a real system, this would load from database
            # For now, simulate loading a subscription
            logger.debug(f"Loading subscription: {subscription_id}")
            
            # Return None to indicate subscription not found
            # In a real system, this would query the database
            return None
            
        except Exception as e:
            logger.error(f"Error loading subscription {subscription_id}: {e}")
            return None
        
    def get_billing_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de facturation"""



        return {
            "plans_cached": len(self.plans_cache),
            "subscriptions_cached": len(self.subscriptions_cache),
            "active_subscriptions": len([s for s in self.subscriptions_cache.values() if s.is_active])
        }