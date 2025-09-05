"""🚀 Platform Core Subscription - Upgrade Management System
============================================================
Module: backend/platform_core/subscription/upgrade_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE GESTION D'UPGRADES
Gestion intelligente des upgrades et downgrades d'abonnements
- Recommendations automatiques basées sur l'usage
- Upgrades/downgrades seamless
- Facturation proportionnelle
- Analytics prédictives
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)


class UpgradeType(Enum):
    """Types d'upgrade"""
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    LATERAL = "lateral"  # Changement sans upgrade/downgrade


class UpgradeStatus(Enum):
    """Statuts d'upgrade"""
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UpgradeReason(Enum):
    """Raisons d'upgrade"""
    USAGE_EXCEEDED = "usage_exceeded"
    CUSTOMER_REQUEST = "customer_request"
    AUTOMATIC_RECOMMENDATION = "automatic_recommendation"
    PLAN_OPTIMIZATION = "plan_optimization"
    SEASONAL_PROMOTION = "seasonal_promotion"


@dataclass
class UpgradeStrategy:
    """Stratégie d'upgrade"""
    id: str
    name: str
    description: str
    from_plan_id: str
    to_plan_id: str
    upgrade_type: UpgradeType
    trigger_conditions: Dict[str, Any]
    price_adjustment: Decimal
    features_added: List[str]
    features_removed: List[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.features_removed is None:
            self.features_removed = []

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la stratégie en dictionnaire"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "from_plan_id": self.from_plan_id,
            "to_plan_id": self.to_plan_id,
            "upgrade_type": self.upgrade_type.value,
            "trigger_conditions": self.trigger_conditions,
            "price_adjustment": float(self.price_adjustment),
            "features_added": self.features_added,
            "features_removed": self.features_removed,
            "metadata": self.metadata or {}
        }


@dataclass
class UpgradeRecommendation:
    """Recommandation d'upgrade"""
    id: str
    customer_id: str
    current_plan_id: str
    recommended_plan_id: str
    upgrade_type: UpgradeType
    reason: UpgradeReason
    confidence_score: float  # 0.0 to 1.0
    potential_savings: Optional[Decimal]
    additional_features: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la recommandation en dictionnaire"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "current_plan_id": self.current_plan_id,
            "recommended_plan_id": self.recommended_plan_id,
            "upgrade_type": self.upgrade_type.value,
            "reason": self.reason.value,
            "confidence_score": self.confidence_score,
            "potential_savings": float(self.potential_savings) if self.potential_savings else None,
            "additional_features": self.additional_features,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata or {}
        }

    def is_expired(self) -> bool:
        """Vérifie si la recommandation a expiré"""
        return self.expires_at and datetime.now() > self.expires_at


class UpgradeManager:
    """Gestionnaire principal des upgrades"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le gestionnaire d'upgrades
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or {}
        self.strategies: Dict[str, UpgradeStrategy] = {}
        self.recommendations: Dict[str, UpgradeRecommendation] = {}
        self.upgrade_history: List[Dict[str, Any]] = []
        self.recommendation_expiry_days = self.config.get("recommendation_expiry_days", 7)
        
        # Initialize default strategies
        self._initialize_default_strategies()
        
        logger.info("UpgradeManager initialized")

    def _initialize_default_strategies(self):
        """Initialise les stratégies par défaut"""
        try:
            # Stratégie d'upgrade pour usage élevé
            high_usage_strategy = UpgradeStrategy(
                id="high_usage_upgrade",
                name="High Usage Upgrade",
                description="Upgrade automatique quand l'usage dépasse 90%",
                from_plan_id="basic",
                to_plan_id="premium",
                upgrade_type=UpgradeType.UPGRADE,
                trigger_conditions={
                    "usage_threshold": 0.9,
                    "consecutive_periods": 2
                },
                price_adjustment=Decimal("20.00"),
                features_added=["unlimited_api_calls", "priority_support"]
            )
            
            self.strategies[high_usage_strategy.id] = high_usage_strategy
            
            logger.info("Default upgrade strategies initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default strategies: {e}")

    async def create_upgrade_strategy(
        self,
        name: str,
        description: str,
        from_plan_id: str,
        to_plan_id: str,
        upgrade_type: UpgradeType,
        trigger_conditions: Dict[str, Any],
        price_adjustment: Union[Decimal, float],
        features_added: List[str],
        features_removed: Optional[List[str]] = None
    ) -> UpgradeStrategy:
        """Crée une nouvelle stratégie d'upgrade
        
        Args:
            name: Nom de la stratégie
            description: Description
            from_plan_id: Plan d'origine
            to_plan_id: Plan de destination
            upgrade_type: Type d'upgrade
            trigger_conditions: Conditions de déclenchement
            price_adjustment: Ajustement de prix
            features_added: Fonctionnalités ajoutées
            features_removed: Fonctionnalités supprimées
            
        Returns:
            UpgradeStrategy: La stratégie créée
        """
        try:
            # Génération d'un ID unique
            strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.strategies)}"
            
            # Validation du prix
            if isinstance(price_adjustment, float):
                price_adjustment = Decimal(str(price_adjustment))
            
            # Création de la stratégie
            strategy = UpgradeStrategy(
                id=strategy_id,
                name=name,
                description=description,
                from_plan_id=from_plan_id,
                to_plan_id=to_plan_id,
                upgrade_type=upgrade_type,
                trigger_conditions=trigger_conditions,
                price_adjustment=price_adjustment,
                features_added=features_added,
                features_removed=features_removed or []
            )
            
            # Stockage de la stratégie
            self.strategies[strategy_id] = strategy
            
            logger.info(f"Upgrade strategy created: {strategy_id}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error creating upgrade strategy: {e}")
            raise

    async def generate_recommendation(
        self,
        customer_id: str,
        current_plan_id: str,
        usage_data: Dict[str, Any],
        billing_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[UpgradeRecommendation]:
        """Génère une recommandation d'upgrade basée sur l'usage
        
        Args:
            customer_id: ID du client
            current_plan_id: Plan actuel
            usage_data: Données d'utilisation
            billing_history: Historique de facturation
            
        Returns:
            Optional[UpgradeRecommendation]: Recommandation générée
        """
        try:
            # Analyse de l'usage pour déterminer la meilleure recommandation
            best_recommendation = None
            highest_score = 0.0
            
            for strategy in self.strategies.values():
                if strategy.from_plan_id != current_plan_id:
                    continue
                
                # Évaluation de la stratégie
                score = await self._evaluate_strategy(strategy, usage_data, billing_history)
                
                if score > highest_score and score > 0.6:  # Seuil minimum
                    highest_score = score
                    
                    # Création de la recommandation
                    recommendation_id = f"rec_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    best_recommendation = UpgradeRecommendation(
                        id=recommendation_id,
                        customer_id=customer_id,
                        current_plan_id=current_plan_id,
                        recommended_plan_id=strategy.to_plan_id,
                        upgrade_type=strategy.upgrade_type,
                        reason=self._determine_reason(usage_data),
                        confidence_score=score,
                        potential_savings=self._calculate_savings(strategy, usage_data),
                        additional_features=strategy.features_added,
                        created_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(days=self.recommendation_expiry_days)
                    )
            
            if best_recommendation:
                self.recommendations[best_recommendation.id] = best_recommendation
                logger.info(f"Recommendation generated: {best_recommendation.id}")
            
            return best_recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return None

    async def _evaluate_strategy(
        self,
        strategy: UpgradeStrategy,
        usage_data: Dict[str, Any],
        billing_history: Optional[List[Dict[str, Any]]]
    ) -> float:
        """Évalue une stratégie d'upgrade
        
        Args:
            strategy: Stratégie à évaluer
            usage_data: Données d'utilisation
            billing_history: Historique de facturation
            
        Returns:
            float: Score de confiance (0.0 to 1.0)
        """
        try:
            score = 0.0
            
            # Évaluation basée sur l'usage
            usage_threshold = strategy.trigger_conditions.get("usage_threshold", 0.8)
            current_usage = usage_data.get("usage_percentage", 0.0)
            
            if current_usage >= usage_threshold:
                score += 0.4
            
            # Évaluation basée sur la tendance
            if usage_data.get("trend", "stable") == "increasing":
                score += 0.3
            
            # Évaluation basée sur l'historique
            if billing_history:
                consistent_usage = self._analyze_usage_consistency(billing_history)
                if consistent_usage:
                    score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error evaluating strategy: {e}")
            return 0.0

    def _determine_reason(self, usage_data: Dict[str, Any]) -> UpgradeReason:
        """Détermine la raison de la recommandation"""
        usage_percentage = usage_data.get("usage_percentage", 0.0)
        
        if usage_percentage >= 0.9:
            return UpgradeReason.USAGE_EXCEEDED
        elif usage_data.get("trend") == "increasing":
            return UpgradeReason.AUTOMATIC_RECOMMENDATION
        else:
            return UpgradeReason.PLAN_OPTIMIZATION

    def _calculate_savings(
        self,
        strategy: UpgradeStrategy,
        usage_data: Dict[str, Any]
    ) -> Optional[Decimal]:
        """Calcule les économies potentielles"""
        try:
            # Simulation des économies basée sur l'usage
            overage_cost = usage_data.get("overage_cost", 0.0)
            
            if overage_cost > float(strategy.price_adjustment):
                return Decimal(str(overage_cost)) - strategy.price_adjustment
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating savings: {e}")
            return None

    def _analyze_usage_consistency(self, billing_history: List[Dict[str, Any]]) -> bool:
        """Analyse la cohérence de l'usage"""
        try:
            if len(billing_history) < 3:
                return False
            
            # Vérification de la tendance d'usage
            recent_usage = [period.get("usage_percentage", 0.0) for period in billing_history[-3:]]
            average_usage = sum(recent_usage) / len(recent_usage)
            
            return average_usage >= 0.8
            
        except Exception as e:
            logger.error(f"Error analyzing usage consistency: {e}")
            return False

    async def execute_upgrade(
        self,
        customer_id: str,
        recommendation_id: str,
        approved_by: Optional[str] = None
    ) -> bool:
        """Exécute un upgrade basé sur une recommandation
        
        Args:
            customer_id: ID du client
            recommendation_id: ID de la recommandation
            approved_by: Qui a approuvé l'upgrade
            
        Returns:
            bool: True si exécuté avec succès
        """
        try:
            recommendation = self.recommendations.get(recommendation_id)
            if not recommendation:
                logger.error(f"Recommendation not found: {recommendation_id}")
                return False
            
            if recommendation.customer_id != customer_id:
                logger.error(f"Recommendation not for customer: {customer_id}")
                return False
            
            if recommendation.is_expired():
                logger.error(f"Recommendation expired: {recommendation_id}")
                return False
            
            # Enregistrement de l'upgrade
            upgrade_record = {
                "id": f"upgrade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "customer_id": customer_id,
                "recommendation_id": recommendation_id,
                "from_plan": recommendation.current_plan_id,
                "to_plan": recommendation.recommended_plan_id,
                "upgrade_type": recommendation.upgrade_type.value,
                "executed_at": datetime.now().isoformat(),
                "approved_by": approved_by,
                "status": UpgradeStatus.COMPLETED.value
            }
            
            self.upgrade_history.append(upgrade_record)
            
            # Suppression de la recommandation utilisée
            del self.recommendations[recommendation_id]
            
            logger.info(f"Upgrade executed: {upgrade_record['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing upgrade: {e}")
            return False

    def get_recommendation(self, recommendation_id: str) -> Optional[UpgradeRecommendation]:
        """Récupère une recommandation"""
        return self.recommendations.get(recommendation_id)

    def list_customer_recommendations(
        self,
        customer_id: str,
        active_only: bool = True
    ) -> List[UpgradeRecommendation]:
        """Liste les recommandations d'un client"""
        recommendations = [
            rec for rec in self.recommendations.values()
            if rec.customer_id == customer_id
        ]
        
        if active_only:
            recommendations = [rec for rec in recommendations if not rec.is_expired()]
        
        return recommendations

    def get_upgrade_statistics(self) -> Dict[str, Any]:
        """Génère des statistiques sur les upgrades"""
        try:
            total_upgrades = len(self.upgrade_history)
            total_recommendations = len(self.recommendations)
            
            # Analyse par type d'upgrade
            upgrade_types = {}
            for upgrade in self.upgrade_history:
                upgrade_type = upgrade.get("upgrade_type", "unknown")
                upgrade_types[upgrade_type] = upgrade_types.get(upgrade_type, 0) + 1
            
            # Taux de conversion
            conversion_rate = 0.0
            if total_recommendations > 0:
                conversion_rate = (total_upgrades / (total_upgrades + total_recommendations)) * 100
            
            return {
                "total_upgrades": total_upgrades,
                "total_recommendations": total_recommendations,
                "conversion_rate": conversion_rate,
                "upgrade_types": upgrade_types,
                "active_strategies": len(self.strategies)
            }
            
        except Exception as e:
            logger.error(f"Error generating upgrade statistics: {e}")
            return {}