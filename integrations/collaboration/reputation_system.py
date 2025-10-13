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
    
    def _initialize_creator_reputation(self, creator_id: str) -> None:
        """Initialize reputation for new creator."""
        self.creator_reputations[creator_id] = CreatorReputation(
            creator_id=creator_id,
            overall_score=0.5,  # Start with neutral score
            scores_by_category={},
            total_collaborations=0,
            success_rate=0.0,
            trust_level="new"
        )
    
    def _calculate_confidence(self, creator_id: str, category: ReputationCategory) -> float:
        """Calculate confidence score based on data volume."""
        reputation = self.creator_reputations.get(creator_id)
        if not reputation:
            return 0.1
        
        # Base confidence on total collaborations
        collaborations = reputation.total_collaborations
        if collaborations == 0:
            return 0.1
        elif collaborations < 5:
            return 0.3
        elif collaborations < 15:
            return 0.6
        elif collaborations < 50:
            return 0.8
        else:
            return 0.95
    
    async def _recalculate_overall_score(self, creator_id: str) -> None:
        """Recalculate overall reputation score."""
        reputation = self.creator_reputations[creator_id]
        
        if not reputation.scores_by_category:
            reputation.overall_score = 0.5
            return
        
        # Weighted average of category scores
        category_weights = {
            ReputationCategory.COLLABORATION_QUALITY: 0.3,
            ReputationCategory.RELIABILITY: 0.25,
            ReputationCategory.CREATIVITY: 0.2,
            ReputationCategory.COMMUNICATION: 0.15,
            ReputationCategory.TECHNICAL_SKILLS: 0.1
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for category, score_obj in reputation.scores_by_category.items():
            weight = category_weights.get(category, 0.1)
            weighted_sum += score_obj.score * weight * score_obj.confidence
            total_weight += weight * score_obj.confidence
        
        if total_weight > 0:
            reputation.overall_score = weighted_sum / total_weight
        
        # Update trust level based on overall score and confidence
        avg_confidence = statistics.mean([s.confidence for s in reputation.scores_by_category.values()])
        
        if reputation.overall_score >= 0.9 and avg_confidence >= 0.8:
            reputation.trust_level = "exceptional"
        elif reputation.overall_score >= 0.8 and avg_confidence >= 0.6:
            reputation.trust_level = "high"
        elif reputation.overall_score >= 0.6 and avg_confidence >= 0.4:
            reputation.trust_level = "good"
        elif reputation.overall_score >= 0.4:
            reputation.trust_level = "average"
        else:
            reputation.trust_level = "low"
    
    async def get_reputation(self, creator_id: str) -> Optional[CreatorReputation]:
        """Get creator reputation."""
        return self.creator_reputations.get(creator_id)
    
    async def compare_creators(self, creator_ids: List[str]) -> Dict[str, Any]:
        """Compare reputation scores between creators."""
        reputations = {}
        for creator_id in creator_ids:
            rep = await self.get_reputation(creator_id)
            if rep:
                reputations[creator_id] = {
                    'overall_score': rep.overall_score,
                    'trust_level': rep.trust_level,
                    'total_collaborations': rep.total_collaborations,
                    'success_rate': rep.success_rate
                }
        
        # Sort by overall score
        sorted_creators = sorted(
            reputations.items(),
            key=lambda x: x[1]['overall_score'],
            reverse=True
        )
        
        return {
            'rankings': sorted_creators,
            'best_creator': sorted_creators[0] if sorted_creators else None,
            'comparison_timestamp': datetime.now().isoformat()
        }
    
    async def get_top_creators(
        self,
        limit: int = 10,
        category: Optional[ReputationCategory] = None,
        min_collaborations: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top creators by reputation."""
        eligible_creators = []
        
        for creator_id, reputation in self.creator_reputations.items():
            if reputation.total_collaborations >= min_collaborations:
                score = reputation.overall_score
                
                if category and category in reputation.scores_by_category:
                    score = reputation.scores_by_category[category].score
                
                eligible_creators.append({
                    'creator_id': creator_id,
                    'score': score,
                    'trust_level': reputation.trust_level,
                    'collaborations': reputation.total_collaborations,
                    'success_rate': reputation.success_rate
                })
        
        # Sort and limit
        eligible_creators.sort(key=lambda x: x['score'], reverse=True)
        return eligible_creators[:limit]
    
    async def calculate_collaboration_risk(
        self,
        creator_ids: List[str]
    ) -> Dict[str, Any]:
        """Calculate risk assessment for collaboration."""
        risks = []
        total_risk_score = 0.0
        
        for creator_id in creator_ids:
            reputation = await self.get_reputation(creator_id)
            if not reputation:
                risks.append({
                    'creator_id': creator_id,
                    'risk_level': 'high',
                    'reason': 'No reputation data'
                })
                total_risk_score += 0.8
                continue
            
            # Calculate individual risk
            risk_score = 1.0 - reputation.overall_score
            
            # Adjust for collaboration history
            if reputation.total_collaborations < 3:
                risk_score += 0.2
            
            # Adjust for success rate
            if reputation.success_rate < 0.7:
                risk_score += 0.1
            
            risk_level = "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high"
            
            risks.append({
                'creator_id': creator_id,
                'risk_score': min(1.0, risk_score),
                'risk_level': risk_level,
                'total_collaborations': reputation.total_collaborations,
                'success_rate': reputation.success_rate
            })
            
            total_risk_score += min(1.0, risk_score)
        
        avg_risk = total_risk_score / len(creator_ids) if creator_ids else 0
        overall_risk = "low" if avg_risk < 0.3 else "medium" if avg_risk < 0.6 else "high"
        
        return {
            'individual_risks': risks,
            'overall_risk_score': avg_risk,
            'overall_risk_level': overall_risk,
            'recommendation': self._get_risk_recommendation(overall_risk),
            'assessment_timestamp': datetime.now().isoformat()
        }
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level."""
        recommendations = {
            'low': 'Collaboration recommended. Creators have proven track records.',
            'medium': 'Collaboration acceptable with monitoring. Consider milestone-based payments.',
            'high': 'Collaboration not recommended without additional safeguards or experienced supervision.'
        }
        return recommendations.get(risk_level, 'Unable to assess risk.')
    
    async def track_collaboration_outcome(
        self,
        collaboration_id: str,
        creator_ids: List[str],
        success: bool,
        performance_metrics: Dict[str, Any]
    ) -> bool:
        """Track collaboration outcome and update reputations."""
        for creator_id in creator_ids:
            if creator_id not in self.creator_reputations:
                self._initialize_creator_reputation(creator_id)
            
            reputation = self.creator_reputations[creator_id]
            reputation.total_collaborations += 1
            
            # Update success rate
            if success:
                current_successes = reputation.success_rate * (reputation.total_collaborations - 1)
                reputation.success_rate = (current_successes + 1) / reputation.total_collaborations
            else:
                current_successes = reputation.success_rate * (reputation.total_collaborations - 1)
                reputation.success_rate = current_successes / reputation.total_collaborations
            
            # Update category scores based on performance metrics
            for category in ReputationCategory:
                metric_key = f"{category.value}_score"
                if metric_key in performance_metrics:
                    await self.update_reputation(
                        creator_id,
                        category,
                        performance_metrics[metric_key]
                    )
        
        logger.info(f"Collaboration outcome tracked: {collaboration_id} - Success: {success}")
        return True