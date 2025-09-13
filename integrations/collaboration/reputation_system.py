"""
Reputation System - Collaboration Module
=======================================
Système de réputation basé sur performance collaborative.
Scoring créateurs, feedback et trust metrics.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class ReputationCategory(Enum):
    """Catégories de réputation."""
    COLLABORATION_QUALITY = "collaboration_quality"
    RELIABILITY = "reliability"
    CREATIVITY = "creativity"
    COMMUNICATION = "communication"
    TECHNICAL_SKILLS = "technical_skills"

@dataclass
class ReputationScore:
    """Score de réputation."""
    category: ReputationCategory
    score: float  # 0.0 - 1.0
    confidence: float
    last_updated: datetime

@dataclass
class CreatorReputation:
    """Réputation globale d'un créateur."""
    creator_id: str
    overall_score: float
    scores_by_category: Dict[ReputationCategory, ReputationScore]
    total_collaborations: int
    success_rate: float
    trust_level: str

class ReputationSystem:
    """Système de réputation pour créateurs."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialise le système de réputation."""
        self.config = config or {}
        self.creator_reputations: Dict[str, CreatorReputation] = {}
        self.feedback_history: Dict[str, List[Dict]] = {}
        logger.info("Reputation System initialisé")
    
    async def update_reputation(
        self,
        creator_id: str,
        category: ReputationCategory,
        performance_score: float,
        collaboration_context: Dict[str, Any] = None
    ) -> bool:
        """Met à jour la réputation d'un créateur."""
        if creator_id not in self.creator_reputations:
            self._initialize_creator_reputation(creator_id)
        
        reputation = self.creator_reputations[creator_id]
        
        # Calculer nouveau score avec pondération historique
        current_score = reputation.scores_by_category.get(category)
        if current_score:
            # Moyenne pondérée avec historique
            weight_new = 0.3  # 30% nouveau score, 70% historique
            new_score_value = (performance_score * weight_new + 
                             current_score.score * (1 - weight_new))
        else:
            new_score_value = performance_score
        
        # Mettre à jour score catégorie
        reputation.scores_by_category[category] = ReputationScore(
            category=category,
            score=max(0.0, min(1.0, new_score_value)),
            confidence=self._calculate_confidence(creator_id, category),
            last_updated=datetime.now()
        )
        
        # Recalculer score global
        await self._recalculate_overall_score(creator_id)
        
        logger.info(f"Réputation mise à jour: {creator_id} - {category.value} = {new_score_value:.2f}")
        return True