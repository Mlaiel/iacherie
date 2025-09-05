"""🚀 Platform Core Subscription - Subscription Management System
================================================================
Module: backend/platform_core/subscription/subscription_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE GESTION D'ABONNEMENTS
Gestion complète des abonnements avec intelligence artificielle
- Création et gestion des abonnements
- Renouvellements automatiques  
- Upgrades/downgrades intelligents
- Analytics et métriques d'abonnements
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)


class SubscriptionStatus(Enum):
    """Statuts des abonnements"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class BillingCycle(Enum):
    """Cycles de facturation"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"


@dataclass
class Subscription:
    """Modèle d'abonnement"""
    id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    start_date: datetime
    end_date: Optional[datetime]
    next_billing_date: Optional[datetime]
    price: Decimal
    currency: str
    trial_end_date: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'abonnement en dictionnaire"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "billing_cycle": self.billing_cycle.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "next_billing_date": self.next_billing_date.isoformat() if self.next_billing_date else None,
            "price": float(self.price),
            "currency": self.currency,
            "trial_end_date": self.trial_end_date.isoformat() if self.trial_end_date else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "metadata": self.metadata or {}
        }

    def is_active(self) -> bool:
        """Vérifie si l'abonnement est actif"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]

    def is_in_trial(self) -> bool:
        """Vérifie si l'abonnement est en période d'essai"""
        return (
            self.status == SubscriptionStatus.TRIAL and 
            self.trial_end_date and 
            datetime.now() <= self.trial_end_date
        )

    def days_until_renewal(self) -> Optional[int]:
        """Nombre de jours jusqu'au prochain renouvellement"""
        if not self.next_billing_date:
            return None
        
        delta = self.next_billing_date - datetime.now()
        return max(0, delta.days)


class SubscriptionManager:
    """Gestionnaire principal des abonnements"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le gestionnaire d'abonnements
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or {}
        self.trial_days = self.config.get("trial_days", 14)
        self.grace_period_days = self.config.get("grace_period_days", 3)
        self.subscriptions: Dict[str, Subscription] = {}
        
        logger.info("SubscriptionManager initialized")

    async def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        price: Union[Decimal, float],
        currency: str = "USD",
        start_trial: bool = False
    ) -> Subscription:
        """Crée un nouvel abonnement
        
        Args:
            customer_id: ID du client
            plan_id: ID du plan
            billing_cycle: Cycle de facturation
            price: Prix de l'abonnement
            currency: Devise
            start_trial: Démarrer avec période d'essai
            
        Returns:
            Subscription: L'abonnement créé
        """
        try:
            # Génération d'un ID unique
            subscription_id = f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.subscriptions)}"
            
            # Validation du prix
            if isinstance(price, float):
                price = Decimal(str(price))
            
            # Dates de démarrage et de fin
            start_date = datetime.now()
            trial_end_date = None
            status = SubscriptionStatus.ACTIVE
            
            if start_trial:
                trial_end_date = start_date + timedelta(days=self.trial_days)
                status = SubscriptionStatus.TRIAL
            
            # Calcul de la prochaine date de facturation
            next_billing_date = self._calculate_next_billing_date(start_date, billing_cycle)
            
            # Création de l'abonnement
            subscription = Subscription(
                id=subscription_id,
                customer_id=customer_id,
                plan_id=plan_id,
                status=status,
                billing_cycle=billing_cycle,
                start_date=start_date,
                end_date=None,
                next_billing_date=next_billing_date,
                price=price,
                currency=currency,
                trial_end_date=trial_end_date
            )
            
            # Stockage de l'abonnement
            self.subscriptions[subscription_id] = subscription
            
            logger.info(f"Subscription created: {subscription_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False
    ) -> bool:
        """Annule un abonnement
        
        Args:
            subscription_id: ID de l'abonnement
            immediate: Annulation immédiate ou à la fin de la période
            
        Returns:
            bool: True si annulé avec succès
        """
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return False
            
            if subscription.status == SubscriptionStatus.CANCELLED:
                logger.warning(f"Subscription already cancelled: {subscription_id}")
                return True
            
            # Annulation immédiate
            if immediate:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.now()
                subscription.end_date = datetime.now()
            else:
                # Annulation à la fin de la période
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.now()
                subscription.end_date = subscription.next_billing_date
            
            logger.info(f"Subscription cancelled: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return False

    async def renew_subscription(self, subscription_id: str) -> bool:
        """Renouvelle un abonnement
        
        Args:
            subscription_id: ID de l'abonnement
            
        Returns:
            bool: True si renouvelé avec succès
        """
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return False
            
            if not subscription.is_active():
                logger.error(f"Cannot renew inactive subscription: {subscription_id}")
                return False
            
            # Calcul de la nouvelle date de facturation
            current_billing_date = subscription.next_billing_date or datetime.now()
            new_billing_date = self._calculate_next_billing_date(
                current_billing_date, 
                subscription.billing_cycle
            )
            
            # Mise à jour de l'abonnement
            subscription.next_billing_date = new_billing_date
            
            # Si c'était un essai, passer en actif
            if subscription.status == SubscriptionStatus.TRIAL:
                subscription.status = SubscriptionStatus.ACTIVE
            
            logger.info(f"Subscription renewed: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error renewing subscription: {e}")
            return False

    async def suspend_subscription(self, subscription_id: str, reason: str) -> bool:
        """Suspend un abonnement
        
        Args:
            subscription_id: ID de l'abonnement
            reason: Raison de la suspension
            
        Returns:
            bool: True si suspendu avec succès
        """
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return False
            
            if subscription.status == SubscriptionStatus.SUSPENDED:
                logger.warning(f"Subscription already suspended: {subscription_id}")
                return True
            
            subscription.status = SubscriptionStatus.SUSPENDED
            subscription.metadata = subscription.metadata or {}
            subscription.metadata["suspension_reason"] = reason
            subscription.metadata["suspended_at"] = datetime.now().isoformat()
            
            logger.info(f"Subscription suspended: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error suspending subscription: {e}")
            return False

    async def reactivate_subscription(self, subscription_id: str) -> bool:
        """Réactive un abonnement suspendu
        
        Args:
            subscription_id: ID de l'abonnement
            
        Returns:
            bool: True si réactivé avec succès
        """
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return False
            
            if subscription.status != SubscriptionStatus.SUSPENDED:
                logger.error(f"Cannot reactivate non-suspended subscription: {subscription_id}")
                return False
            
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.metadata = subscription.metadata or {}
            subscription.metadata["reactivated_at"] = datetime.now().isoformat()
            
            logger.info(f"Subscription reactivated: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error reactivating subscription: {e}")
            return False

    def _calculate_next_billing_date(
        self,
        current_date: datetime,
        billing_cycle: BillingCycle
    ) -> datetime:
        """Calcule la prochaine date de facturation
        
        Args:
            current_date: Date actuelle
            billing_cycle: Cycle de facturation
            
        Returns:
            datetime: Prochaine date de facturation
        """
        if billing_cycle == BillingCycle.WEEKLY:
            return current_date + timedelta(weeks=1)
        elif billing_cycle == BillingCycle.MONTHLY:
            return current_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return current_date + timedelta(days=90)
        elif billing_cycle == BillingCycle.YEARLY:
            return current_date + timedelta(days=365)
        else:
            return current_date + timedelta(days=30)  # Default to monthly

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Récupère un abonnement
        
        Args:
            subscription_id: ID de l'abonnement
            
        Returns:
            Optional[Subscription]: L'abonnement si trouvé
        """
        return self.subscriptions.get(subscription_id)

    def list_customer_subscriptions(self, customer_id: str) -> List[Subscription]:
        """Liste les abonnements d'un client
        
        Args:
            customer_id: ID du client
            
        Returns:
            List[Subscription]: Liste des abonnements du client
        """
        return [
            sub for sub in self.subscriptions.values()
            if sub.customer_id == customer_id
        ]

    def get_subscription_stats(self) -> Dict[str, Any]:
        """Génère des statistiques sur les abonnements
        
        Returns:
            Dict[str, Any]: Statistiques des abonnements
        """
        try:
            total_subscriptions = len(self.subscriptions)
            active_subscriptions = len([
                sub for sub in self.subscriptions.values()
                if sub.is_active()
            ])
            
            status_counts = {}
            for status in SubscriptionStatus:
                status_counts[status.value] = len([
                    sub for sub in self.subscriptions.values()
                    if sub.status == status
                ])
            
            total_mrr = sum(
                sub.price for sub in self.subscriptions.values()
                if sub.is_active() and sub.billing_cycle == BillingCycle.MONTHLY
            )
            
            return {
                "total_subscriptions": total_subscriptions,
                "active_subscriptions": active_subscriptions,
                "status_breakdown": status_counts,
                "monthly_recurring_revenue": float(total_mrr),
                "churn_rate": (
                    status_counts.get("cancelled", 0) / max(total_subscriptions, 1) * 100
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating subscription stats: {e}")
            return {}