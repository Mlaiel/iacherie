"""Subscription Management Database Models and Operations

Gestion complète des abonnements avec support multi-tiers,
facturation automatisée et analytics de revenue.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Monetization Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Decimal
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum as PyEnum
import logging
import uuid
from decimal import Decimal as DecimalType

logger = logging.getLogger(__name__)

Base = declarative_base()


class SubscriptionTier(PyEnum):
    """
Niveaux d'abonnement disponibles."""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"
    CREATOR_PRO = "creator_pro"


class SubscriptionStatus(PyEnum):
    """Statuts possibles des abonnements."""

    ACTIVE = "active"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    GRACE_PERIOD = "grace_period"


class BillingCycle(PyEnum):
    """Cycles de facturation disponibles."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class PaymentStatus(PyEnum):
    """Statuts des paiements."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class SubscriptionPlan(Base):
    """
    Plans d'abonnement avec fonctionnalités et limites.
    """
    __tablename__ = "subscription_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Informations du plan
    name = Column(String(100), nullable=False)
    tier = Column(Enum(SubscriptionTier), nullable=False)
    description = Column(Text)
    
    # Tarification
    price_monthly = Column(Decimal(10, 2), nullable=False)
    price_quarterly = Column(Decimal(10, 2))
    price_yearly = Column(Decimal(10, 2))
    currency = Column(String(3), default="EUR")
    
    # Limites et fonctionnalités
    max_uploads_per_month = Column(Integer)
    max_storage_gb = Column(Integer)
    max_ai_requests_per_month = Column(Integer)
    max_collaborations = Column(Integer)
    max_platforms = Column(Integer)
    
    # Fonctionnalités incluses
    features = Column(JSON)  # Liste des fonctionnalités
    ai_features_enabled = Column(Boolean, default=True)
    protection_features_enabled = Column(Boolean, default=True)
    analytics_level = Column(String(50))  # "basic", "advanced", "enterprise"
    priority_support = Column(Boolean, default=False)
    
    # Configuration
    trial_days = Column(Integer, default=0)
    grace_period_days = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    subscriptions = relationship("UserSubscription", back_populates="plan")

    def __repr__(self):
        return f"<SubscriptionPlan({self.name}, {self.tier.value})>"
    
    def get_price_for_cycle(self, cycle: BillingCycle) -> DecimalType:
        """Retourne le prix pour un cycle de facturation donné."""
        if cycle == BillingCycle.MONTHLY:
            return self.price_monthly
        elif cycle == BillingCycle.QUARTERLY:
            return self.price_quarterly or (self.price_monthly * 3 * DecimalType('0.9'))  # 10% discount
        elif cycle == BillingCycle.YEARLY:
            return self.price_yearly or (self.price_monthly * 12 * DecimalType('0.8'))  # 20% discount
        else:
            return self.price_monthly


class UserSubscription(Base):
    """
    Abonnements utilisateur avec gestion complète du cycle de vie.
    """
    __tablename__ = "user_subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String, ForeignKey("subscription_plans.id"), nullable=False)
    
    # État de l'abonnement
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.PENDING)
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY)
    
    # Dates importantes
    started_at = Column(DateTime, nullable=False)
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)
    cancelled_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Facturation
    amount = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    tax_rate = Column(Decimal(5, 4), default=0.0000)
    discount_percent = Column(Decimal(5, 2), default=0.00)
    
    # Informations de paiement
    payment_method_id = Column(String(255))
    payment_provider = Column(String(50))  # "stripe", "paypal", "wise"
    external_subscription_id = Column(String(255))  # ID chez le provider
    
    # Usage et limites
    uploads_used_current_period = Column(Integer, default=0)
    storage_used_gb = Column(Decimal(10, 2), default=0.00)
    ai_requests_used_current_period = Column(Integer, default=0)
    
    # Configuration
    auto_renewal = Column(Boolean, default=True)
    upgrade_at_period_end = Column(Boolean, default=False)
    downgrade_at_period_end = Column(Boolean, default=False)
    next_plan_id = Column(String, ForeignKey("subscription_plans.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions", foreign_keys=[plan_id])
    next_plan = relationship("SubscriptionPlan", foreign_keys=[next_plan_id])
    payments = relationship("SubscriptionPayment", back_populates="subscription")
    usage_logs = relationship("SubscriptionUsage", back_populates="subscription")

    def __repr__(self):
        return f"<UserSubscription({self.user_id}, {self.plan.name if self.plan else 'Unknown'})>"
    
    @property
    def is_trial(self) -> bool:
        """Vérifie si l'abonnement est en période d'essai."""
        if not self.trial_end:
            return False
        return datetime.utcnow() <= self.trial_end
    
    @property
    def is_active(self) -> bool:
        """
Vérifie si l'abonnement est actif."""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]
    
    @property
    def days_until_renewal(self) -> int:
        """
Retourne le nombre de jours jusqu'au renouvellement."""
        if not self.current_period_end:
            return 0
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    def can_use_feature(self, feature_name: str) -> bool:
        """
Vérifie si l'utilisateur peut utiliser une fonctionnalité."""
        if not self.is_active or not self.plan:
            return False
        
        features = self.plan.features or []
        return feature_name in features
    
    def get_usage_percentage(self, usage_type: str) -> float:
        """
Retourne le pourcentage d'utilisation d'une limite."""
        if not self.plan:
            return 0.0
        
        if usage_type == "uploads":
            max_uploads = self.plan.max_uploads_per_month
            if not max_uploads or max_uploads == -1:  # -1 = illimité
                return 0.0
            return (self.uploads_used_current_period / max_uploads) * 100
        
        elif usage_type == "storage":
            max_storage = self.plan.max_storage_gb
            if not max_storage or max_storage == -1:
                return 0.0
            return (float(self.storage_used_gb) / max_storage) * 100
        
        elif usage_type == "ai_requests":
            max_requests = self.plan.max_ai_requests_per_month
            if not max_requests or max_requests == -1:
                return 0.0
            return (self.ai_requests_used_current_period / max_requests) * 100
        
        return 0.0


class SubscriptionPayment(Base):
    """
    Historique des paiements d'abonnements.
    """
    __tablename__ = "subscription_payments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("user_subscriptions.id"), nullable=False)
    
    # Informations de paiement
    amount = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    tax_amount = Column(Decimal(10, 2), default=0.00)
    discount_amount = Column(Decimal(10, 2), default=0.00)
    total_amount = Column(Decimal(10, 2), nullable=False)
    
    # Provider et statut
    payment_provider = Column(String(50), nullable=False)
    payment_method = Column(String(50))  # "card", "paypal", "bank_transfer"
    external_payment_id = Column(String(255))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Période couverte
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Informations de facturation
    invoice_number = Column(String(100))
    invoice_url = Column(String(500))
    receipt_url = Column(String(500))
    
    # Métadonnées
    payment_metadata = Column(JSON)
    failure_reason = Column(Text)
    refund_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    failed_at = Column(DateTime)
    refunded_at = Column(DateTime)
    
    # Relations
    subscription = relationship("UserSubscription", back_populates="payments")

    def __repr__(self):
        return f"<SubscriptionPayment({self.amount} {self.currency}, {self.status.value})>"


class SubscriptionUsage(Base):
    """
    Suivi de l'utilisation des fonctionnalités par abonnement.
    """
    __tablename__ = "subscription_usage"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("user_subscriptions.id"), nullable=False)
    
    # Période de mesure
    usage_date = Column(DateTime, nullable=False)
    usage_period = Column(String(20))  # "daily", "monthly"
    
    # Métriques d'utilisation
    uploads_count = Column(Integer, default=0)
    storage_used_gb = Column(Decimal(10, 2), default=0.00)
    ai_requests_count = Column(Integer, default=0)
    api_calls_count = Column(Integer, default=0)
    collaborations_count = Column(Integer, default=0)
    
    # Utilisation par fonctionnalité
    feature_usage = Column(JSON)  # {"fingerprinting": 50, "analytics": 120}
    platform_usage = Column(JSON)  # {"youtube": 10, "spotify": 5}
    
    # Métriques de performance
    processing_time_total_seconds = Column(Integer, default=0)
    bandwidth_used_mb = Column(Decimal(10, 2), default=0.00)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    subscription = relationship("UserSubscription", back_populates="usage_logs")

    def __repr__(self):
        return f"<SubscriptionUsage({self.usage_date}, {self.uploads_count} uploads)>"


class SubscriptionRepository:
    """
    Repository pattern pour la gestion des abonnements.
    Implémentation professionnelle avec gestion des cycles de vie.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    def create_subscription(self, user_id: str, plan_id: str, 
                          billing_cycle: BillingCycle = BillingCycle.MONTHLY,
                          start_trial: bool = False) -> UserSubscription:
        """
        Crée un nouvel abonnement utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            plan_id: ID du plan d'abonnement
            billing_cycle: Cycle de facturation
            start_trial: Commencer par une période d'essai
            
        Returns:
            UserSubscription: Abonnement créé
        """
        try:
            plan = self.session.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == plan_id
            ).first()
            
            if not plan:
                raise ValueError("Plan d'abonnement non trouvé")
            
            # Calcul des dates
            start_date = datetime.utcnow()
            
            if start_trial and plan.trial_days > 0:
                trial_end = start_date + timedelta(days=plan.trial_days)
                period_end = trial_end
                status = SubscriptionStatus.TRIAL
            else:
                trial_end = None
                if billing_cycle == BillingCycle.MONTHLY:
                    period_end = start_date + timedelta(days=30)
                elif billing_cycle == BillingCycle.QUARTERLY:
                    period_end = start_date + timedelta(days=90)
                elif billing_cycle == BillingCycle.YEARLY:
                    period_end = start_date + timedelta(days=365)
                else:
                    period_end = start_date + timedelta(days=30)
                status = SubscriptionStatus.ACTIVE
            
            # Création de l'abonnement
            subscription = UserSubscription(
                user_id=user_id,
                plan_id=plan_id,
                status=status,
                billing_cycle=billing_cycle,
                started_at=start_date,
                current_period_start=start_date,
                current_period_end=period_end,
                trial_start=start_date if start_trial else None,
                trial_end=trial_end,
                amount=plan.get_price_for_cycle(billing_cycle)
            )
            
            self.session.add(subscription)
            self.session.commit()
            
            self.logger.info(f"Abonnement créé: {subscription.id}")
            return subscription
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur création abonnement: {str(e)}")
            raise
    
    def get_user_active_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Récupère l'abonnement actif d'un utilisateur."""
        return self.session.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).first()
    
    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """
        Annule un abonnement.
        
        Args:
            subscription_id: ID de l'abonnement
            immediate: Annulation immédiate ou en fin de période
            
        Returns:
            bool: True si annulé avec succès
        """
        try:
            subscription = self.session.query(UserSubscription).filter(
                UserSubscription.id == subscription_id
            ).first()
            
            if not subscription:
                return False
            
            if immediate:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.expires_at = datetime.utcnow()
            else:
                subscription.auto_renewal = False
                subscription.expires_at = subscription.current_period_end
            
            subscription.cancelled_at = datetime.utcnow()
            subscription.updated_at = datetime.utcnow()
            
            self.session.commit()
            self.logger.info(f"Abonnement annulé: {subscription_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur annulation abonnement: {str(e)}")
            return False
    
    def upgrade_subscription(self, subscription_id: str, new_plan_id: str,
                           immediate: bool = True) -> bool:
        """
        Met à niveau un abonnement vers un plan supérieur.
        
        Args:
            subscription_id: ID de l'abonnement
            new_plan_id: ID du nouveau plan
            immediate: Mise à niveau immédiate ou en fin de période
            
        Returns:
            bool: True si mis à niveau avec succès
        """
        try:
            subscription = self.session.query(UserSubscription).filter(
                UserSubscription.id == subscription_id
            ).first()
            
            if not subscription:
                return False
            
            new_plan = self.session.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == new_plan_id
            ).first()
            
            if not new_plan:
                return False
            
            if immediate:
                subscription.plan_id = new_plan_id
                subscription.amount = new_plan.get_price_for_cycle(subscription.billing_cycle)
            else:
                subscription.upgrade_at_period_end = True
                subscription.next_plan_id = new_plan_id
            
            subscription.updated_at = datetime.utcnow()
            
            self.session.commit()
            self.logger.info(f"Abonnement mis à niveau: {subscription_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à niveau abonnement: {str(e)}")
            return False
    
    def record_usage(self, subscription_id: str, usage_type: str, amount: int = 1) -> bool:
        """
        Enregistre l'utilisation d'une fonctionnalité.
        
        Args:
            subscription_id: ID de l'abonnement
            usage_type: Type d'utilisation ("uploads", "ai_requests", etc.)
            amount: Quantité utilisée
            
        Returns:
            bool: True si enregistré avec succès
        """
        try:
            subscription = self.session.query(UserSubscription).filter(
                UserSubscription.id == subscription_id
            ).first()
            
            if not subscription:
                return False
            
            # Mise à jour des compteurs
            if usage_type == "uploads":
                subscription.uploads_used_current_period += amount
            elif usage_type == "ai_requests":
                subscription.ai_requests_used_current_period += amount
            elif usage_type == "storage":
                subscription.storage_used_gb += DecimalType(str(amount))
            
            subscription.updated_at = datetime.utcnow()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur enregistrement usage: {str(e)}")
            return False
    
    def process_renewals(self) -> List[str]:
        """
        Traite les renouvellements d'abonnements qui arrivent à échéance.
        
        Returns:
            List[str]: Liste des IDs d'abonnements traités
        """
        try:
            # Abonnements arrivant à échéance dans les prochaines 24h
            cutoff_date = datetime.utcnow() + timedelta(hours=24)
            
            subscriptions_to_renew = self.session.query(UserSubscription).filter(
                UserSubscription.status == SubscriptionStatus.ACTIVE,
                UserSubscription.auto_renewal == True,
                UserSubscription.current_period_end <= cutoff_date
            ).all()
            
            processed_ids = []
            
            for subscription in subscriptions_to_renew:
                try:
                    # Calcul de la nouvelle période
                    if subscription.billing_cycle == BillingCycle.MONTHLY:
                        new_period_end = subscription.current_period_end + timedelta(days=30)
                    elif subscription.billing_cycle == BillingCycle.QUARTERLY:
                        new_period_end = subscription.current_period_end + timedelta(days=90)
                    elif subscription.billing_cycle == BillingCycle.YEARLY:
                        new_period_end = subscription.current_period_end + timedelta(days=365)
                    else:
                        new_period_end = subscription.current_period_end + timedelta(days=30)
                    
                    # Mise à jour de l'abonnement
                    subscription.current_period_start = subscription.current_period_end
                    subscription.current_period_end = new_period_end
                    subscription.uploads_used_current_period = 0
                    subscription.ai_requests_used_current_period = 0
                    subscription.updated_at = datetime.utcnow()
                    
                    # Gestion des changements de plan programmés
                    if subscription.upgrade_at_period_end and subscription.next_plan_id:
                        subscription.plan_id = subscription.next_plan_id
                        subscription.next_plan_id = None
                        subscription.upgrade_at_period_end = False
                    
                    processed_ids.append(subscription.id)
                    
                except Exception as e:
                    self.logger.error(f"Erreur renouvellement {subscription.id}: {str(e)}")
                    continue
            
            self.session.commit()
            self.logger.info(f"Renouvellements traités: {len(processed_ids)}")
            return processed_ids
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur traitement renouvellements: {str(e)}")
            return []
    
    def get_subscription_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Retourne les analytics des abonnements sur une période donnée.
        
        Args:
            period_days: Nombre de jours à analyser
            
        Returns:
            Dict[str, Any]: Analytics des abonnements
        """
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Nouvelles souscriptions
        new_subscriptions = self.session.query(UserSubscription).filter(
            UserSubscription.created_at >= start_date
        ).count()
        
        # Annulations
        cancellations = self.session.query(UserSubscription).filter(
            UserSubscription.cancelled_at >= start_date
        ).count()
        
        # Revenus
        payments = self.session.query(SubscriptionPayment).filter(
            SubscriptionPayment.processed_at >= start_date,
            SubscriptionPayment.status == PaymentStatus.COMPLETED
        ).all()
        
        total_revenue = sum(p.total_amount for p in payments)
        
        # Répartition par plan
        active_subscriptions = self.session.query(UserSubscription).filter(
            UserSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).all()
        
        plan_distribution = {}
        for sub in active_subscriptions:
            plan_name = sub.plan.name if sub.plan else "Unknown"
            plan_distribution[plan_name] = plan_distribution.get(plan_name, 0) + 1
        
        return {
            'period_days': period_days,
            'new_subscriptions': new_subscriptions,
            'cancellations': cancellations,
            'churn_rate': (cancellations / max(1, new_subscriptions)) * 100,
            'total_revenue': float(total_revenue),
            'active_subscriptions': len(active_subscriptions),
            'plan_distribution': plan_distribution,
            'last_updated': datetime.utcnow().isoformat()
        }
