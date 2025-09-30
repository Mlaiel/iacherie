"""
Intelligent Pricing Engine
Moteur de tarification intelligent pour Ainfluencer Platform

Ce module fournit des fonctionnalités avancées de tarification dynamique et intelligente.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio

# Configuration du logger
logger = logging.getLogger(__name__)

class PricingStrategy(Enum):
    """Stratégies de tarification disponibles"""
    DYNAMIC = "dynamic"
    FIXED = "fixed"
    COMPETITIVE = "competitive"
    VALUE_BASED = "value_based"
    PENETRATION = "penetration"
    PREMIUM = "premium"

class MarketCondition(Enum):
    """Conditions de marché"""
    HIGH_DEMAND = "high_demand"
    LOW_DEMAND = "low_demand"
    NORMAL = "normal"
    VOLATILE = "volatile"

@dataclass
class PricingRule:
    """Règle de tarification"""
    name: str
    strategy: PricingStrategy
    min_price: float = 0.0
    max_price: float = 1000000.0
    markup_percentage: float = 0.0
    discount_percentage: float = 0.0
    conditions: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

@dataclass
class PricingRecommendation:
    """Recommandation de prix"""
    product_id: str
    recommended_price: float
    confidence_score: float
    strategy_used: PricingStrategy
    market_condition: MarketCondition
    factors: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)

class IntelligentPricingEngine:
    """Moteur de tarification intelligent principal"""
    
    def __init__(self):
        """Initialise le moteur de tarification"""
        self.pricing_rules: List[PricingRule] = []
        self.market_data: Dict[str, Any] = {}
        self.pricing_history: Dict[str, List[Dict]] = {}
        logger.info("Intelligent Pricing Engine initialized")
    
    async def calculate_optimal_price(
        self, 
        product_id: str,
        base_price: float,
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> PricingRecommendation:
        """
        Calcule le prix optimal pour un produit
        
        Args:
            product_id: Identifiant du produit
            base_price: Prix de base
            market_conditions: Conditions de marché actuelles
            
        Returns:
            PricingRecommendation: Recommandation de prix optimisée
        """
        
        # Analyse des conditions de marché
        market_condition = await self._analyze_market_conditions(market_conditions or {})
        
        # Sélection de la stratégie optimale
        strategy = await self._select_optimal_strategy(product_id, market_condition)
        
        # Calcul du prix recommandé
        recommended_price = await self._calculate_price(base_price, strategy, market_condition)
        
        # Calcul du score de confiance
        confidence_score = await self._calculate_confidence_score(
            product_id, recommended_price, strategy
        )
        
        recommendation = PricingRecommendation(
            product_id=product_id,
            recommended_price=recommended_price,
            confidence_score=confidence_score,
            strategy_used=strategy,
            market_condition=market_condition,
            factors={
                "base_price": base_price,
                "market_demand": market_conditions.get("demand", 1.0) if market_conditions else 1.0,
                "competitor_prices": market_conditions.get("competitor_avg", base_price) if market_conditions else base_price,
                "seasonality": market_conditions.get("seasonality", 1.0) if market_conditions else 1.0
            }
        )
        
        # Stockage dans l'historique
        if product_id not in self.pricing_history:
            self.pricing_history[product_id] = []
        
        self.pricing_history[product_id].append({
            "timestamp": datetime.now(),
            "recommended_price": recommended_price,
            "strategy": strategy.value,
            "confidence": confidence_score
        })
        
        logger.info(f"Price calculated for {product_id}: {recommended_price} ({strategy.value})")
        
        return recommendation
    
    async def _analyze_market_conditions(self, conditions: Dict[str, Any]) -> MarketCondition:
        """Analyse les conditions de marché"""
        demand = conditions.get("demand", 1.0)
        volatility = conditions.get("volatility", 0.1)
        
        if demand > 1.5:
            return MarketCondition.HIGH_DEMAND
        elif demand < 0.7:
            return MarketCondition.LOW_DEMAND
        elif volatility > 0.3:
            return MarketCondition.VOLATILE
        else:
            return MarketCondition.NORMAL
    
    async def _select_optimal_strategy(
        self, 
        product_id: str, 
        market_condition: MarketCondition
    ) -> PricingStrategy:
        """Sélectionne la stratégie de tarification optimale"""
        
        # Stratégies par conditions de marché
        strategy_map = {
            MarketCondition.HIGH_DEMAND: PricingStrategy.PREMIUM,
            MarketCondition.LOW_DEMAND: PricingStrategy.PENETRATION,
            MarketCondition.VOLATILE: PricingStrategy.DYNAMIC,
            MarketCondition.NORMAL: PricingStrategy.VALUE_BASED
        }
        
        return strategy_map.get(market_condition, PricingStrategy.DYNAMIC)
    
    async def _calculate_price(
        self, 
        base_price: float, 
        strategy: PricingStrategy,
        market_condition: MarketCondition
    ) -> float:
        """Calcule le prix selon la stratégie"""
        
        multipliers = {
            PricingStrategy.PREMIUM: {
                MarketCondition.HIGH_DEMAND: 1.3,
                MarketCondition.NORMAL: 1.2,
                MarketCondition.LOW_DEMAND: 1.1,
                MarketCondition.VOLATILE: 1.15
            },
            PricingStrategy.PENETRATION: {
                MarketCondition.HIGH_DEMAND: 0.9,
                MarketCondition.NORMAL: 0.8,
                MarketCondition.LOW_DEMAND: 0.7,
                MarketCondition.VOLATILE: 0.85
            },
            PricingStrategy.DYNAMIC: {
                MarketCondition.HIGH_DEMAND: 1.25,
                MarketCondition.NORMAL: 1.0,
                MarketCondition.LOW_DEMAND: 0.85,
                MarketCondition.VOLATILE: 1.0
            },
            PricingStrategy.VALUE_BASED: {
                MarketCondition.HIGH_DEMAND: 1.15,
                MarketCondition.NORMAL: 1.0,
                MarketCondition.LOW_DEMAND: 0.95,
                MarketCondition.VOLATILE: 1.05
            }
        }
        
        # Valeur par défaut si stratégie/condition non trouvée
        default_multipliers = {
            MarketCondition.HIGH_DEMAND: 1.1,
            MarketCondition.NORMAL: 1.0,
            MarketCondition.LOW_DEMAND: 0.9,
            MarketCondition.VOLATILE: 1.0
        }
        
        multiplier = multipliers.get(strategy, default_multipliers).get(market_condition, 1.0)
        
        return round(base_price * multiplier, 2)
    
    async def _calculate_confidence_score(
        self, 
        product_id: str, 
        price: float, 
        strategy: PricingStrategy
    ) -> float:
        """Calcule le score de confiance de la recommandation"""
        
        # Score de base selon la stratégie
        base_scores = {
            PricingStrategy.PREMIUM: 0.85,
            PricingStrategy.PENETRATION: 0.75,
            PricingStrategy.DYNAMIC: 0.90,
            PricingStrategy.VALUE_BASED: 0.80,
            PricingStrategy.COMPETITIVE: 0.70,
            PricingStrategy.FIXED: 0.60
        }
        
        base_score = base_scores.get(strategy, 0.70)
        
        # Ajustements selon l'historique
        if product_id in self.pricing_history:
            history_count = len(self.pricing_history[product_id])
            history_bonus = min(history_count * 0.02, 0.15)  # Max 15% bonus
            base_score += history_bonus
        
        return min(base_score, 0.95)  # Maximum 95%
    
    async def add_pricing_rule(self, rule: PricingRule):
        """Ajoute une règle de tarification"""
        self.pricing_rules.append(rule)
        logger.info(f"Pricing rule added: {rule.name}")
    
    async def get_pricing_history(self, product_id: str) -> List[Dict]:
        """Récupère l'historique de tarification d'un produit"""
        return self.pricing_history.get(product_id, [])
    
    async def update_market_data(self, data: Dict[str, Any]):
        """Met à jour les données de marché"""
        self.market_data.update(data)
        logger.info("Market data updated")

# Instance globale du moteur de tarification
intelligent_pricing_engine = IntelligentPricingEngine()

# Fonctions utilitaires pour compatibilité
async def calculate_dynamic_price(product_id: str, base_price: float) -> float:
    """Calcule un prix dynamique pour un produit"""
    recommendation = await intelligent_pricing_engine.calculate_optimal_price(
        product_id, base_price
    )
    return recommendation.recommended_price

async def get_price_recommendation(
    product_id: str, 
    base_price: float,
    market_data: Optional[Dict[str, Any]] = None
) -> PricingRecommendation:
    """Obtient une recommandation de prix complète"""
    return await intelligent_pricing_engine.calculate_optimal_price(
        product_id, base_price, market_data
    )

# Exports principaux
__all__ = [
    'IntelligentPricingEngine',
    'PricingRule',
    'PricingRecommendation', 
    'PricingStrategy',
    'MarketCondition',
    'intelligent_pricing_engine',
    'calculate_dynamic_price',
    'get_price_recommendation'
]

logger.info("Intelligent Pricing Engine module loaded successfully")