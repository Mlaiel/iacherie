"""🚀 Platform Core Subscription - Quota Management System
==========================================================
Module: backend/platform_core/subscription/quota_manager.py  
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE GESTION DES QUOTAS
Gestion intelligente des quotas et limites d'utilisation
- Quotas par ressource et par période
- Surveillance en temps réel
- Alertes automatiques
- Analytics d'utilisation avancées
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types de ressources avec quotas"""
    API_CALLS = "api_calls"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    USERS = "users"
    PROJECTS = "projects"
    AI_GENERATIONS = "ai_generations"
    CONTENT_PIECES = "content_pieces"
    SOCIAL_POSTS = "social_posts"


class QuotaPeriod(Enum):
    """Périodes de quota"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class QuotaStatus(Enum):
    """Statuts de quota"""
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    WARNING = "warning"
    SUSPENDED = "suspended"


@dataclass
class ResourceQuota:
    """Modèle de quota de ressource"""
    id: str
    customer_id: str
    resource_type: ResourceType
    limit: int
    used: int
    period: QuotaPeriod
    reset_date: datetime
    status: QuotaStatus
    warning_threshold: int = 80  # Percentage
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le quota en dictionnaire"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "resource_type": self.resource_type.value,
            "limit": self.limit,
            "used": self.used,
            "period": self.period.value,
            "reset_date": self.reset_date.isoformat(),
            "status": self.status.value,
            "warning_threshold": self.warning_threshold,
            "usage_percentage": self.get_usage_percentage(),
            "remaining": self.get_remaining(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata or {}
        }

    def get_usage_percentage(self) -> float:
        """Calcule le pourcentage d'utilisation"""
        if self.limit == 0:
            return 0.0
        return (self.used / self.limit) * 100

    def get_remaining(self) -> int:
        """Calcule la quantité restante"""
        return max(0, self.limit - self.used)

    def is_exceeded(self) -> bool:
        """Vérifie si le quota est dépassé"""
        return self.used >= self.limit

    def is_warning(self) -> bool:
        """Vérifie si le quota est en alerte"""
        return self.get_usage_percentage() >= self.warning_threshold

    def days_until_reset(self) -> int:
        """Nombre de jours jusqu'au reset"""
        delta = self.reset_date - datetime.now()
        return max(0, delta.days)


@dataclass  
class UsageTracker:
    """Tracker d'utilisation des ressources"""
    customer_id: str
    resource_type: ResourceType
    amount: int
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le tracker en dictionnaire"""
        return {
            "customer_id": self.customer_id,
            "resource_type": self.resource_type.value,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


class QuotaManager:
    """Gestionnaire principal des quotas"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le gestionnaire de quotas
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or {}
        self.quotas: Dict[str, ResourceQuota] = {}
        self.usage_history: List[UsageTracker] = []
        self.warning_callbacks: List[callable] = []
        self.exceeded_callbacks: List[callable] = []
        
        logger.info("QuotaManager initialized")

    async def create_quota(
        self,
        customer_id: str,
        resource_type: ResourceType,
        limit: int,
        period: QuotaPeriod,
        warning_threshold: int = 80
    ) -> ResourceQuota:
        """Crée un nouveau quota
        
        Args:
            customer_id: ID du client
            resource_type: Type de ressource
            limit: Limite du quota
            period: Période du quota
            warning_threshold: Seuil d'alerte en pourcentage
            
        Returns:
            ResourceQuota: Le quota créé
        """
        try:
            # Génération d'un ID unique
            quota_id = f"quota_{customer_id}_{resource_type.value}_{period.value}"
            
            # Calcul de la date de reset
            reset_date = self._calculate_reset_date(period)
            
            # Création du quota
            quota = ResourceQuota(
                id=quota_id,
                customer_id=customer_id,
                resource_type=resource_type,
                limit=limit,
                used=0,
                period=period,
                reset_date=reset_date,
                status=QuotaStatus.ACTIVE,
                warning_threshold=warning_threshold
            )
            
            # Stockage du quota
            self.quotas[quota_id] = quota
            
            logger.info(f"Quota created: {quota_id}")
            return quota
            
        except Exception as e:
            logger.error(f"Error creating quota: {e}")
            raise

    async def use_resource(
        self,
        customer_id: str,
        resource_type: ResourceType,
        amount: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Utilise une ressource et met à jour le quota
        
        Args:
            customer_id: ID du client
            resource_type: Type de ressource
            amount: Quantité utilisée
            metadata: Métadonnées additionnelles
            
        Returns:
            bool: True si l'utilisation est autorisée
        """
        try:
            # Recherche du quota correspondant
            quota = self._find_quota(customer_id, resource_type)
            if not quota:
                logger.warning(f"No quota found for {customer_id} - {resource_type.value}")
                return True  # Autoriser si pas de quota défini
            
            # Vérification de la limite
            if quota.used + amount > quota.limit:
                quota.status = QuotaStatus.EXCEEDED
                await self._trigger_exceeded_callbacks(quota)
                logger.warning(f"Quota exceeded for {customer_id} - {resource_type.value}")
                return False
            
            # Mise à jour de l'utilisation
            quota.used += amount
            
            # Vérification du seuil d'alerte
            if quota.is_warning() and quota.status != QuotaStatus.WARNING:
                quota.status = QuotaStatus.WARNING
                await self._trigger_warning_callbacks(quota)
            
            # Enregistrement de l'utilisation
            usage = UsageTracker(
                customer_id=customer_id,
                resource_type=resource_type,
                amount=amount,
                timestamp=datetime.now(),
                metadata=metadata
            )
            self.usage_history.append(usage)
            
            logger.debug(f"Resource used: {customer_id} - {resource_type.value} - {amount}")
            return True
            
        except Exception as e:
            logger.error(f"Error using resource: {e}")
            return False

    async def reset_quota(self, quota_id: str) -> bool:
        """Remet à zéro un quota
        
        Args:
            quota_id: ID du quota
            
        Returns:
            bool: True si reset avec succès
        """
        try:
            quota = self.quotas.get(quota_id)
            if not quota:
                logger.error(f"Quota not found: {quota_id}")
                return False
            
            # Reset des valeurs
            quota.used = 0
            quota.status = QuotaStatus.ACTIVE
            quota.reset_date = self._calculate_reset_date(quota.period)
            
            logger.info(f"Quota reset: {quota_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting quota: {e}")
            return False

    async def update_quota_limit(self, quota_id: str, new_limit: int) -> bool:
        """Met à jour la limite d'un quota
        
        Args:
            quota_id: ID du quota
            new_limit: Nouvelle limite
            
        Returns:
            bool: True si mis à jour avec succès
        """
        try:
            quota = self.quotas.get(quota_id)
            if not quota:
                logger.error(f"Quota not found: {quota_id}")
                return False
            
            old_limit = quota.limit
            quota.limit = new_limit
            
            # Réévaluation du statut
            if quota.is_exceeded():
                quota.status = QuotaStatus.EXCEEDED
            elif quota.is_warning():
                quota.status = QuotaStatus.WARNING
            else:
                quota.status = QuotaStatus.ACTIVE
            
            logger.info(f"Quota limit updated: {quota_id} ({old_limit} -> {new_limit})")
            return True
            
        except Exception as e:
            logger.error(f"Error updating quota limit: {e}")
            return False

    def _find_quota(
        self,
        customer_id: str,
        resource_type: ResourceType
    ) -> Optional[ResourceQuota]:
        """Trouve un quota pour un client et une ressource
        
        Args:
            customer_id: ID du client
            resource_type: Type de ressource
            
        Returns:
            Optional[ResourceQuota]: Le quota trouvé
        """
        for quota in self.quotas.values():
            if (quota.customer_id == customer_id and 
                quota.resource_type == resource_type):
                return quota
        return None

    def _calculate_reset_date(self, period: QuotaPeriod) -> datetime:
        """Calcule la date de reset d'un quota
        
        Args:
            period: Période du quota
            
        Returns:
            datetime: Date de reset
        """
        now = datetime.now()
        
        if period == QuotaPeriod.HOURLY:
            return now + timedelta(hours=1)
        elif period == QuotaPeriod.DAILY:
            return now + timedelta(days=1)
        elif period == QuotaPeriod.WEEKLY:
            return now + timedelta(weeks=1)
        elif period == QuotaPeriod.MONTHLY:
            return now + timedelta(days=30)
        elif period == QuotaPeriod.YEARLY:
            return now + timedelta(days=365)
        else:
            return now + timedelta(days=1)  # Default to daily

    async def _trigger_warning_callbacks(self, quota: ResourceQuota):
        """Déclenche les callbacks d'alerte"""
        for callback in self.warning_callbacks:
            try:
                await callback(quota)
            except Exception as e:
                logger.error(f"Error in warning callback: {e}")

    async def _trigger_exceeded_callbacks(self, quota: ResourceQuota):
        """Déclenche les callbacks de dépassement"""
        for callback in self.exceeded_callbacks:
            try:
                await callback(quota)
            except Exception as e:
                logger.error(f"Error in exceeded callback: {e}")

    def add_warning_callback(self, callback: callable):
        """Ajoute un callback d'alerte"""
        self.warning_callbacks.append(callback)

    def add_exceeded_callback(self, callback: callable):
        """Ajoute un callback de dépassement"""
        self.exceeded_callbacks.append(callback)

    def get_quota(self, quota_id: str) -> Optional[ResourceQuota]:
        """Récupère un quota"""
        return self.quotas.get(quota_id)

    def list_customer_quotas(self, customer_id: str) -> List[ResourceQuota]:
        """Liste les quotas d'un client"""
        return [
            quota for quota in self.quotas.values()
            if quota.customer_id == customer_id
        ]

    def get_usage_statistics(
        self,
        customer_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Génère des statistiques d'utilisation
        
        Args:
            customer_id: Filtrer par client
            resource_type: Filtrer par type de ressource
            days: Nombre de jours à analyser
            
        Returns:
            Dict[str, Any]: Statistiques d'utilisation
        """
        try:
            # Filtrage des données
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_usage = [
                usage for usage in self.usage_history
                if usage.timestamp >= cutoff_date
            ]
            
            if customer_id:
                filtered_usage = [
                    usage for usage in filtered_usage
                    if usage.customer_id == customer_id
                ]
            
            if resource_type:
                filtered_usage = [
                    usage for usage in filtered_usage
                    if usage.resource_type == resource_type
                ]
            
            # Calcul des statistiques
            total_usage = sum(usage.amount for usage in filtered_usage)
            unique_customers = len(set(usage.customer_id for usage in filtered_usage))
            
            # Usage par type de ressource
            usage_by_type = {}
            for usage in filtered_usage:
                resource = usage.resource_type.value
                usage_by_type[resource] = usage_by_type.get(resource, 0) + usage.amount
            
            return {
                "period_days": days,
                "total_usage": total_usage,
                "unique_customers": unique_customers,
                "usage_by_resource_type": usage_by_type,
                "total_records": len(filtered_usage)
            }
            
        except Exception as e:
            logger.error(f"Error generating usage statistics: {e}")
            return {}