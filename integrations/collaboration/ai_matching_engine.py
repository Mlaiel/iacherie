"""
AI Matching Engine - Collaboration Module
=========================================
Engine IA avancé pour matching optimal de créateurs
basé sur compatibilité, style, audience et revenue potential.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MatchingCriteria(Enum):
    """Critères de matching disponibles."""
    STYLE_COMPATIBILITY = "style"
    AUDIENCE_OVERLAP = "audience" 
    REVENUE_POTENTIAL = "revenue"
    SKILL_COMPLEMENT = "skills"
    ENGAGEMENT_RATE = "engagement"

@dataclass
class CreatorProfile:
    """Profil créateur pour matching."""
    creator_id: str
    name: str
    categories: List[str]
    style_vector: List[float]
    audience_demographics: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    revenue_metrics: Dict[str, float]
    collaboration_history: List[Dict]

@dataclass
class MatchResult:
    """Résultat de matching entre créateurs."""
    creator1_id: str
    creator2_id: str
    compatibility_score: float
    criteria_scores: Dict[MatchingCriteria, float]
    predicted_success: float
    collaboration_type: str
    revenue_projection: float
    confidence_level: float
    recommendations: List[str]

class AIMatchingEngine:
    """Engine IA pour matching optimal de créateurs."""
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        """Initialise l'engine de matching IA."""
        self.config = config or {}
        self.matching_models = {}
        self.compatibility_cache = {}
        self.performance_metrics = {}
        self._load_models()
        logger.info("AI Matching Engine initialisé")
    
    def _load_models(self) -> None:
        """Charge les modèles ML pour matching."""
        self.matching_models = {
            'style_compatibility': self._init_style_model(),
            'audience_analysis': self._init_audience_model(),
            'revenue_prediction': self._init_revenue_model(),
            'success_prediction': self._init_success_model()
        }
    
    def _init_style_model(self) -> None:
        """Initialise le modèle d'analyse de style."""
        return {
            'type': 'style_similarity',
            'weights': np.random.rand(100),
            'threshold': 0.7
        }
    
    def _init_audience_model(self) -> None:
        """Initialise le modèle d'analyse d'audience."""
        return {
            'type': 'audience_overlap',
            'demographic_weights': {
                'age': 0.3, 'gender': 0.2, 'location': 0.25, 'interests': 0.25
            },
            'min_overlap': 0.15
        }
    
    def _init_revenue_model(self) -> None:
        """Initialise le modèle de prédiction revenue."""
        return {
            'type': 'revenue_prediction',
            'factors': {
                'follower_synergy': 0.4, 'engagement_boost': 0.3,
                'content_quality': 0.2, 'platform_reach': 0.1
            }
        }
    
    def _init_success_model(self) -> None:
        """Initialise le modèle de prédiction de succès."""
        return {
            'type': 'collaboration_success',
            'success_factors': {
                'compatibility': 0.35, 'complementarity': 0.25,
                'audience_synergy': 0.25, 'past_performance': 0.15
            }
        }
    
    async def find_matches(
        self,
        creator_profile: CreatorProfile,
        candidate_pool: List[CreatorProfile],
        criteria: List[MatchingCriteria] = None,
        max_matches: int = 10
    ) -> List[MatchResult]:
        """Trouve les meilleurs matches pour un créateur."""
        if not criteria:
            criteria = [
                MatchingCriteria.STYLE_COMPATIBILITY,
                MatchingCriteria.AUDIENCE_OVERLAP,
                MatchingCriteria.REVENUE_POTENTIAL
            ]
        
        matches = []
        for candidate in candidate_pool:
            if candidate.creator_id == creator_profile.creator_id:
                continue
            
            match_result = await self._calculate_match_score(
                creator_profile, candidate, criteria
            )
            
            if match_result.compatibility_score > 0.5:
                matches.append(match_result)
        
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        return matches[:max_matches]
    
    async def _calculate_match_score(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        criteria: List[MatchingCriteria]
    ) -> MatchResult:
        """Calcule le score de matching entre deux créateurs."""
        criteria_scores = {}
        
        for criterion in criteria:
            score = await self._calculate_criterion_score(creator1, creator2, criterion)
            criteria_scores[criterion] = score
        
        weights = self._get_criteria_weights(criteria)
        compatibility_score = sum(criteria_scores[c] * weights[c] for c in criteria)
        
        predicted_success = await self._predict_collaboration_success(
            creator1, creator2, criteria_scores
        )
        
        revenue_projection = await self._predict_revenue_impact(
            creator1, creator2, criteria_scores
        )
        
        recommendations = self._generate_recommendations(
            creator1, creator2, criteria_scores
        )
        
        return MatchResult(
            creator1_id=creator1.creator_id,
            creator2_id=creator2.creator_id,
            compatibility_score=compatibility_score,
            criteria_scores=criteria_scores,
            predicted_success=predicted_success,
            collaboration_type=self._suggest_collaboration_type(creator1, creator2),
            revenue_projection=revenue_projection,
            confidence_level=self._calculate_confidence(criteria_scores),
            recommendations=recommendations
        )
    
    async def _calculate_criterion_score(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        criterion: MatchingCriteria
    ) -> float:
        """Calcule le score pour un critère spécifique."""
        if criterion == MatchingCriteria.STYLE_COMPATIBILITY:
            return self._calculate_style_compatibility(creator1, creator2)
        elif criterion == MatchingCriteria.AUDIENCE_OVERLAP:
            return self._calculate_audience_overlap(creator1, creator2)
        elif criterion == MatchingCriteria.REVENUE_POTENTIAL:
            return self._calculate_revenue_potential(creator1, creator2)
        elif criterion == MatchingCriteria.SKILL_COMPLEMENT:
            return self._calculate_skill_complement(creator1, creator2)
        elif criterion == MatchingCriteria.ENGAGEMENT_RATE:
            return self._calculate_engagement_synergy(creator1, creator2)
        else:
            return 0.5
    
    def _calculate_style_compatibility(
        self, creator1: CreatorProfile, creator2: CreatorProfile
    ) -> float:
        """Calcule compatibilité stylistique."""
        if not creator1.style_vector or not creator2.style_vector:
            return 0.5
        
        v1 = np.array(creator1.style_vector)
        v2 = np.array(creator2.style_vector)
        
        if len(v1) != len(v2):
            return 0.5
        
        dot_product = np.dot(v1, v2)
        norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
        
        if norm_product == 0:
            return 0.5
        
        similarity = dot_product / norm_product
        return max(0, min(1, (similarity + 1) / 2))
    
    def _calculate_audience_overlap(
        self, creator1: CreatorProfile, creator2: CreatorProfile
    ) -> float:
        """Calcule l'overlap d'audience."""
        # Simplified implementation
        return 0.65  # Mock score
    
    def _calculate_revenue_potential(
        self, creator1: CreatorProfile, creator2: CreatorProfile
    ) -> float:
        """Calcule le potentiel revenue de la collaboration."""
        # Simplified implementation
        return 0.75  # Mock score
    
    def _calculate_skill_complement(
        self, creator1: CreatorProfile, creator2: CreatorProfile
    ) -> float:
        """Calcule complémentarité des compétences."""
        skills1 = set(creator1.categories)
        skills2 = set(creator2.categories)
        
        intersection = skills1.intersection(skills2)
        union = skills1.union(skills2)
        
        if not union:
            return 0.5
        
        diversity_score = len(union) / max(len(skills1), len(skills2))
        complementarity_score = 1 - (len(intersection) / len(union))
        
        return (diversity_score + complementarity_score) / 2
    
    def _calculate_engagement_synergy(
        self, creator1: CreatorProfile, creator2: CreatorProfile
    ) -> float:
        """Calcule synergie d'engagement."""
        eng1 = creator1.engagement_metrics
        eng2 = creator2.engagement_metrics
        
        rate1 = eng1.get('engagement_rate', 0)
        rate2 = eng2.get('engagement_rate', 0)
        
        avg_rate = (rate1 + rate2) / 2
        synergy_bonus = min(rate1, rate2) / max(rate1, rate2) if max(rate1, rate2) > 0 else 1
        
        return avg_rate * synergy_bonus
    
    def _get_criteria_weights(self, criteria: List[MatchingCriteria]) -> Dict[MatchingCriteria, float]:
        """Retourne les poids pour chaque critère."""
        default_weights = {
            MatchingCriteria.STYLE_COMPATIBILITY: 0.25,
            MatchingCriteria.AUDIENCE_OVERLAP: 0.25,
            MatchingCriteria.REVENUE_POTENTIAL: 0.25,
            MatchingCriteria.SKILL_COMPLEMENT: 0.15,
            MatchingCriteria.ENGAGEMENT_RATE: 0.10
        }
        
        selected_weights = {c: default_weights.get(c, 0.1) for c in criteria}
        total_weight = sum(selected_weights.values())
        
        if total_weight > 0:
            return {c: w/total_weight for c, w in selected_weights.items()}
        
        return {c: 1.0/len(criteria) for c in criteria}
    
    async def _predict_collaboration_success(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        criteria_scores: Dict[MatchingCriteria, float]
    ) -> float:
        """Prédit le succès de la collaboration."""
        # Simplified implementation
        return 0.78  # Mock prediction
    
    async def _predict_revenue_impact(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        criteria_scores: Dict[MatchingCriteria, float]
    ) -> float:
        """Prédit l'impact revenue de la collaboration."""
        base_revenue = (
            creator1.revenue_metrics.get('monthly_revenue', 0) +
            creator2.revenue_metrics.get('monthly_revenue', 0)
        )
        
        revenue_score = criteria_scores.get(MatchingCriteria.REVENUE_POTENTIAL, 0.5)
        amplification_factor = 1.0 + (revenue_score * 0.5)
        
        return base_revenue * amplification_factor
    
    def _suggest_collaboration_type(
        self, creator1: CreatorProfile, creator2: CreatorProfile
    ) -> str:
        """Suggère le type de collaboration optimal."""
        categories1 = set(creator1.categories)
        categories2 = set(creator2.categories)
        
        if 'music' in categories1 and 'music' in categories2:
            return 'musical_collaboration'
        elif 'video' in categories1 or 'video' in categories2:
            return 'video_content'
        elif 'photography' in categories1 or 'photography' in categories2:
            return 'visual_content'
        else:
            return 'cross_media_collaboration'
    
    def _calculate_confidence(self, criteria_scores: Dict[MatchingCriteria, float]) -> float:
        """Calcule le niveau de confiance du matching."""
        scores = list(criteria_scores.values())
        if not scores:
            return 0.5
        
        mean_score = np.mean(scores)
        variance = np.var(scores)
        confidence = max(0, min(1, mean_score * (1 - variance)))
        
        return confidence
    
    def _generate_recommendations(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        criteria_scores: Dict[MatchingCriteria, float]
    ) -> List[str]:
        """Génère des recommandations pour optimiser la collaboration."""
        recommendations = []
        
        if criteria_scores.get(MatchingCriteria.STYLE_COMPATIBILITY, 0) < 0.6:
            recommendations.append("Considérer une fusion de styles créative")
        
        if criteria_scores.get(MatchingCriteria.AUDIENCE_OVERLAP, 0) < 0.3:
            recommendations.append("Opportunity pour diversification audience")
        
        if criteria_scores.get(MatchingCriteria.REVENUE_POTENTIAL, 0) > 0.8:
            recommendations.append("Fort potentiel monétisation - prioriser")
        
        collab_type = self._suggest_collaboration_type(creator1, creator2)
        recommendations.append(f"Format recommandé: {collab_type}")
        
        return recommendations