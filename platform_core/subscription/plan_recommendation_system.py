"""🚀 Platform Core Subscription - Plan Recommendation System
================================================================
Module: backend/platform_core/subscription/plan_recommendation_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 SYSTÈME DE RECOMMANDATION PLANS IA
Plan recommendation engine avec machine learning avancé
- Algorithmes ML personnalisés pour recommandations optimales
- Analyse comportementale et patterns d'usage
- A/B testing automatique des recommandations
- Intelligence prédictive pour upgrade paths optimaux
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import logging
import asyncio
import json
from decimal import Decimal
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types de recommandations de plans"""
    INITIAL_PLAN = "initial_plan"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    LATERAL_MOVE = "lateral_move"
    TRIAL_TO_PAID = "trial_to_paid"
    RETENTION_OFFER = "retention_offer"


class RecommendationConfidence(Enum):
    """Niveaux de confiance des recommandations"""
    HIGH = "high"  # >80%
    MEDIUM = "medium"  # 60-80%
    LOW = "low"  # 40-60%
    VERY_LOW = "very_low"  # <40%


@dataclass
class CreatorProfile:
    """Profil complet d'un créateur pour recommandations"""
    creator_id: str
    creator_type: str  # musician, blogger, photographer, etc.
    usage_patterns: Dict[str, Any]
    current_plan: Optional[str]
    subscription_history: List[Dict[str, Any]]
    engagement_metrics: Dict[str, float]
    collaboration_activity: Dict[str, Any]
    content_stats: Dict[str, Any]
    revenue_metrics: Dict[str, float]
    behavioral_segments: List[str]


@dataclass
class PlanRecommendation:
    """Recommandation de plan intelligent"""
    recommended_plan_id: str
    recommendation_type: RecommendationType
    confidence_score: float
    confidence_level: RecommendationConfidence
    reasoning: List[str]
    expected_benefits: List[str]
    financial_impact: Dict[str, Decimal]
    success_probability: float
    personalization_factors: List[str]
    timing_recommendation: str
    a_b_test_group: Optional[str]


@dataclass
class RecommendationContext:
    """Contexte pour les recommandations"""
    timestamp: datetime
    trigger_event: str
    business_objectives: List[str]
    market_conditions: Dict[str, Any]
    seasonal_factors: Dict[str, Any]
    competitive_landscape: Dict[str, Any]


class PlanRecommendationSystem:
    """🚀 Système de Recommandation Plans IA Enterprise
    
    Système ML avancé pour recommandations de plans personnalisées
    basé sur l'analyse comportementale et l'intelligence prédictive.
    """
    
    def __init__(self):
        """Initialise le système de recommandation"""
        self.ml_models = {}
        self.feature_scalers = {}
        self.cluster_models = {}
        self.recommendation_cache = {}
        self.a_b_test_groups = {}
        
        # Configuration des algorithmes ML
        self.recommendation_algorithms = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'clustering': KMeans(n_clusters=8, random_state=42)
        }
        
        # Poids des facteurs de recommandation
        self.recommendation_weights = {
            'usage_patterns': 0.3,
            'engagement_metrics': 0.25,
            'collaboration_activity': 0.2,
            'revenue_potential': 0.15,
            'behavioral_similarity': 0.1
        }
        
        logger.info("🚀 Plan Recommendation System initialized")
    
    async def get_plan_recommendations(
        self,
        creator_profile: CreatorProfile,
        context: RecommendationContext,
        max_recommendations: int = 3
    ) -> List[PlanRecommendation]:
        """Génère des recommandations de plans personnalisées"""
        try:
            # Analyse du profil créateur
            profile_features = await self._extract_profile_features(creator_profile)
            
            # Segmentation comportementale
            behavioral_segment = await self._identify_behavioral_segment(profile_features)
            
            # Génération des recommandations candidates
            candidate_plans = await self._generate_candidate_plans(
                creator_profile, behavioral_segment, context
            )
            
            # Scoring ML des recommandations
            scored_recommendations = await self._score_recommendations(
                candidate_plans, profile_features, context
            )
            
            # Sélection des meilleures recommandations
            top_recommendations = await self._select_top_recommendations(
                scored_recommendations, max_recommendations
            )
            
            # Personnalisation finale
            personalized_recommendations = await self._personalize_recommendations(
                top_recommendations, creator_profile, context
            )
            
            logger.info(f"✅ Generated {len(personalized_recommendations)} plan recommendations for creator {creator_profile.creator_id}")
            return personalized_recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating plan recommendations: {e}")
            return []
    
    async def _extract_profile_features(self, profile: CreatorProfile) -> np.ndarray:
        """Extrait les features ML du profil créateur"""
        features = []
        
        # Features d'usage
        usage = profile.usage_patterns
        features.extend([
            usage.get('monthly_uploads', 0),
            usage.get('storage_used_gb', 0),
            usage.get('bandwidth_used_gb', 0),
            usage.get('api_calls_count', 0)
        ])
        
        # Features d'engagement
        engagement = profile.engagement_metrics
        features.extend([
            engagement.get('content_views', 0),
            engagement.get('likes_count', 0),
            engagement.get('shares_count', 0),
            engagement.get('collaboration_rate', 0)
        ])
        
        # Features de revenus
        revenue = profile.revenue_metrics
        features.extend([
            revenue.get('monthly_revenue', 0),
            revenue.get('revenue_growth_rate', 0),
            revenue.get('average_content_value', 0)
        ])
        
        # Features temporelles
        features.extend([
            len(profile.subscription_history),
            (datetime.now() - datetime.fromisoformat(
                profile.subscription_history[-1]['start_date'] if profile.subscription_history else '2024-01-01'
            )).days if profile.subscription_history else 0
        ])
        
        return np.array(features).reshape(1, -1)
    
    async def _identify_behavioral_segment(self, features: np.ndarray) -> str:
        """Identifie le segment comportemental du créateur"""
        try:
            # Utilise le clustering pour identifier le segment
            if 'clustering' in self.ml_models:
                cluster_id = self.ml_models['clustering'].predict(features)[0]
            else:
                # Segmentation basique si pas de modèle entraîné
                feature_sum = np.sum(features)
                if feature_sum > 1000:
                    cluster_id = 0  # Heavy users
                elif feature_sum > 500:
                    cluster_id = 1  # Medium users
                else:
                    cluster_id = 2  # Light users
            
            segment_mapping = {
                0: "power_creator",
                1: "growing_creator", 
                2: "emerging_creator",
                3: "casual_creator",
                4: "collaborator_focused",
                5: "revenue_focused",
                6: "content_volume_focused",
                7: "engagement_focused"
            }
            
            return segment_mapping.get(cluster_id, "general_creator")
            
        except Exception as e:
            logger.error(f"❌ Error identifying behavioral segment: {e}")
            return "general_creator"
    
    async def _generate_candidate_plans(
        self,
        profile: CreatorProfile,
        segment: str,
        context: RecommendationContext
    ) -> List[Dict[str, Any]]:
        """Génère des plans candidats basés sur le profil et segment"""
        candidates = []
        
        # Plans disponibles par type de créateur
        creator_plans = {
            'musician': ['musician_hobbyist', 'musician_emerging', 'musician_professional', 'musician_star'],
            'blogger': ['blogger_personal', 'blogger_content_creator', 'blogger_influencer', 'blogger_media_company'],
            'photographer': ['photographer_amateur', 'photographer_semi_pro', 'photographer_professional', 'photographer_studio'],
            'video_creator': ['video_basic', 'video_creator', 'video_pro', 'video_enterprise'],
            'podcaster': ['podcast_starter', 'podcast_growing', 'podcast_established', 'podcast_network']
        }
        
        # Sélection des plans pertinents
        relevant_plans = creator_plans.get(profile.creator_type, ['general_basic', 'general_pro', 'general_enterprise'])
        
        # Génération des candidats avec contexte
        for plan_id in relevant_plans:
            if plan_id != profile.current_plan:  # Éviter le plan actuel
                candidates.append({
                    'plan_id': plan_id,
                    'creator_type': profile.creator_type,
                    'segment': segment,
                    'context_score': await self._calculate_context_score(plan_id, context)
                })
        
        return candidates
    
    async def _calculate_context_score(self, plan_id: str, context: RecommendationContext) -> float:
        """Calcule le score contextuel d'un plan"""
        score = 0.5  # Score de base
        
        # Facteurs saisonniers
        if 'high_season' in context.seasonal_factors:
            if 'pro' in plan_id or 'professional' in plan_id:
                score += 0.2
        
        # Conditions du marché
        if context.market_conditions.get('creator_growth_rate', 0) > 0.1:
            if 'emerging' in plan_id or 'growing' in plan_id:
                score += 0.15
        
        # Objectifs business
        if 'increase_revenue' in context.business_objectives:
            if 'enterprise' in plan_id or 'star' in plan_id:
                score += 0.1
        
        return min(score, 1.0)
    
    async def _score_recommendations(
        self,
        candidates: List[Dict[str, Any]],
        features: np.ndarray,
        context: RecommendationContext
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Score les recommandations avec ML"""
        scored_candidates = []
        
        for candidate in candidates:
            # Score ML basé sur les features
            ml_score = await self._calculate_ml_score(candidate, features)
            
            # Score contextuel
            context_score = candidate['context_score']
            
            # Score combiné
            final_score = (ml_score * 0.7) + (context_score * 0.3)
            
            scored_candidates.append((candidate, final_score))
        
        # Tri par score décroissant
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return scored_candidates
    
    async def _calculate_ml_score(self, candidate: Dict[str, Any], features: np.ndarray) -> float:
        """Calcule le score ML pour un candidat"""
        try:
            # Si modèle ML entraîné disponible
            if 'plan_recommendation' in self.ml_models:
                probability = self.ml_models['plan_recommendation'].predict_proba(features)[0]
                return max(probability)  # Score de confiance maximum
            else:
                # Scoring heuristique en l'absence de modèle entraîné
                base_score = 0.5
                
                # Bonus pour correspondance créateur/plan
                if candidate['creator_type'] in candidate['plan_id']:
                    base_score += 0.2
                
                # Bonus pour segment approprié
                segment_bonus = {
                    'power_creator': 0.3 if 'pro' in candidate['plan_id'] else 0.1,
                    'growing_creator': 0.2 if 'emerging' in candidate['plan_id'] else 0.1,
                    'emerging_creator': 0.2 if 'basic' in candidate['plan_id'] else 0.1
                }
                
                base_score += segment_bonus.get(candidate['segment'], 0.1)
                
                return min(base_score, 1.0)
                
        except Exception as e:
            logger.error(f"❌ Error calculating ML score: {e}")
            return 0.5
    
    async def _select_top_recommendations(
        self,
        scored_recommendations: List[Tuple[Dict[str, Any], float]],
        max_count: int
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Sélectionne les meilleures recommandations"""
        # Diversification des recommandations
        selected = []
        plan_types_seen = set()
        
        for candidate, score in scored_recommendations:
            if len(selected) >= max_count:
                break
            
            plan_type = candidate['plan_id'].split('_')[0]  # Extrait le type de plan
            
            # Assure la diversité des types de plans
            if plan_type not in plan_types_seen or len(selected) < max_count // 2:
                selected.append((candidate, score))
                plan_types_seen.add(plan_type)
        
        return selected
    
    async def _personalize_recommendations(
        self,
        top_recommendations: List[Tuple[Dict[str, Any], float]],
        profile: CreatorProfile,
        context: RecommendationContext
    ) -> List[PlanRecommendation]:
        """Personnalise les recommandations finales"""
        personalized = []
        
        for i, (candidate, score) in enumerate(top_recommendations):
            # Détermine le type de recommandation
            rec_type = await self._determine_recommendation_type(candidate, profile)
            
            # Calcule la confiance
            confidence_level = self._get_confidence_level(score)
            
            # Génère le raisonnement
            reasoning = await self._generate_reasoning(candidate, profile, context)
            
            # Calcule l'impact financier
            financial_impact = await self._calculate_financial_impact(candidate, profile)
            
            # Crée la recommandation
            recommendation = PlanRecommendation(
                recommended_plan_id=candidate['plan_id'],
                recommendation_type=rec_type,
                confidence_score=score,
                confidence_level=confidence_level,
                reasoning=reasoning,
                expected_benefits=await self._generate_expected_benefits(candidate, profile),
                financial_impact=financial_impact,
                success_probability=score * 0.9,  # Légèrement plus conservateur
                personalization_factors=await self._identify_personalization_factors(candidate, profile),
                timing_recommendation=await self._recommend_timing(candidate, context),
                a_b_test_group=f"recommendation_test_{i % 3}"  # A/B testing simple
            )
            
            personalized.append(recommendation)
        
        return personalized
    
    async def _determine_recommendation_type(
        self,
        candidate: Dict[str, Any],
        profile: CreatorProfile
    ) -> RecommendationType:
        """Détermine le type de recommandation"""
        if not profile.current_plan:
            return RecommendationType.INITIAL_PLAN
        
        current_tier = self._extract_tier_level(profile.current_plan)
        candidate_tier = self._extract_tier_level(candidate['plan_id'])
        
        if candidate_tier > current_tier:
            return RecommendationType.UPGRADE
        elif candidate_tier < current_tier:
            return RecommendationType.DOWNGRADE
        else:
            return RecommendationType.LATERAL_MOVE
    
    def _extract_tier_level(self, plan_id: str) -> int:
        """Extrait le niveau de tier d'un plan"""
        tier_mapping = {
            'basic': 1, 'hobbyist': 1, 'personal': 1, 'amateur': 1, 'starter': 1,
            'emerging': 2, 'growing': 2, 'content_creator': 2, 'semi_pro': 2,
            'professional': 3, 'pro': 3, 'established': 3,
            'enterprise': 4, 'star': 4, 'studio': 4, 'network': 4, 'media_company': 4
        }
        
        for tier, level in tier_mapping.items():
            if tier in plan_id.lower():
                return level
        
        return 2  # Niveau par défaut
    
    def _get_confidence_level(self, score: float) -> RecommendationConfidence:
        """Détermine le niveau de confiance"""
        if score >= 0.8:
            return RecommendationConfidence.HIGH
        elif score >= 0.6:
            return RecommendationConfidence.MEDIUM
        elif score >= 0.4:
            return RecommendationConfidence.LOW
        else:
            return RecommendationConfidence.VERY_LOW
    
    async def _generate_reasoning(
        self,
        candidate: Dict[str, Any],
        profile: CreatorProfile,
        context: RecommendationContext
    ) -> List[str]:
        """Génère le raisonnement de la recommandation"""
        reasoning = []
        
        # Analyse d'usage
        usage = profile.usage_patterns
        if usage.get('monthly_uploads', 0) > 50:
            reasoning.append("Votre volume de contenu élevé bénéficierait des fonctionnalités avancées")
        
        # Analyse d'engagement
        engagement = profile.engagement_metrics
        if engagement.get('collaboration_rate', 0) > 0.3:
            reasoning.append("Votre activité collaborative élevée justifie des outils premium")
        
        # Analyse de croissance
        if profile.revenue_metrics.get('revenue_growth_rate', 0) > 0.2:
            reasoning.append("Votre croissance rapide nécessite des ressources supplémentaires")
        
        # Contextuel
        if 'increase_revenue' in context.business_objectives:
            reasoning.append("Ce plan optimise votre potentiel de monétisation")
        
        return reasoning[:3]  # Maximum 3 raisons principales
    
    async def _generate_expected_benefits(
        self,
        candidate: Dict[str, Any],
        profile: CreatorProfile
    ) -> List[str]:
        """Génère les bénéfices attendus"""
        benefits = []
        
        plan_id = candidate['plan_id']
        
        if 'pro' in plan_id or 'professional' in plan_id:
            benefits.extend([
                "Outils de création avancés",
                "Analytics détaillées",
                "Support prioritaire",
                "Fonctionnalités de collaboration étendues"
            ])
        
        if 'enterprise' in plan_id or 'star' in plan_id:
            benefits.extend([
                "Ressources illimitées",
                "API complète",
                "Gestion d'équipe",
                "White-label options"
            ])
        
        return benefits[:4]  # Maximum 4 bénéfices
    
    async def _calculate_financial_impact(
        self,
        candidate: Dict[str, Any],
        profile: CreatorProfile
    ) -> Dict[str, Decimal]:
        """Calcule l'impact financier de la recommandation"""
        # Simulation des prix (à remplacer par données réelles)
        plan_prices = {
            'basic': Decimal('9.99'),
            'pro': Decimal('29.99'),
            'enterprise': Decimal('99.99')
        }
        
        current_cost = Decimal('0')
        if profile.current_plan:
            for tier, price in plan_prices.items():
                if tier in profile.current_plan:
                    current_cost = price
                    break
        
        new_cost = Decimal('29.99')  # Prix par défaut
        for tier, price in plan_prices.items():
            if tier in candidate['plan_id']:
                new_cost = price
                break
        
        return {
            'monthly_cost_change': new_cost - current_cost,
            'yearly_cost_change': (new_cost - current_cost) * 12,
            'estimated_roi': Decimal('150.00')  # ROI estimé en %
        }
    
    async def _identify_personalization_factors(
        self,
        candidate: Dict[str, Any],
        profile: CreatorProfile
    ) -> List[str]:
        """Identifie les facteurs de personnalisation"""
        factors = []
        
        if profile.creator_type in candidate['plan_id']:
            factors.append(f"Spécialisé pour {profile.creator_type}")
        
        if profile.collaboration_activity.get('active_collaborations', 0) > 5:
            factors.append("Optimisé pour collaboration intensive")
        
        if profile.revenue_metrics.get('monthly_revenue', 0) > 1000:
            factors.append("Adapté aux créateurs à haut revenu")
        
        return factors
    
    async def _recommend_timing(
        self,
        candidate: Dict[str, Any],
        context: RecommendationContext
    ) -> str:
        """Recommande le timing optimal"""
        # Analyse saisonnière
        if context.seasonal_factors.get('high_season'):
            return "Immédiatement - période de forte activité"
        
        # Analyse de contexte
        if 'urgent' in context.business_objectives:
            return "Dans les 7 prochains jours"
        
        return "Dans les 30 prochains jours - timing optimal"
    
    async def train_recommendation_models(self, training_data: pd.DataFrame) -> bool:
        """Entraîne les modèles ML de recommandation"""
        try:
            logger.info("🚀 Training recommendation models...")
            
            # Préparation des données
            features = training_data.drop(['plan_id', 'success'], axis=1)
            labels = training_data['success']
            
            # Normalisation
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Entraînement Random Forest
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(features_scaled, labels)
            
            # Entraînement Gradient Boosting
            gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            gb_model.fit(features_scaled, labels)
            
            # Clustering pour segmentation
            cluster_model = KMeans(n_clusters=8, random_state=42)
            cluster_model.fit(features_scaled)
            
            # Sauvegarde des modèles
            self.ml_models['random_forest'] = rf_model
            self.ml_models['gradient_boosting'] = gb_model
            self.ml_models['clustering'] = cluster_model
            self.feature_scalers['main'] = scaler
            
            logger.info("✅ Recommendation models trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error training recommendation models: {e}")
            return False
    
    async def evaluate_recommendation_performance(
        self,
        recommendations: List[PlanRecommendation],
        actual_outcomes: List[bool]
    ) -> Dict[str, float]:
        """Évalue la performance des recommandations"""
        try:
            if len(recommendations) != len(actual_outcomes):
                raise ValueError("Mismatch between recommendations and outcomes")
            
            # Calcul des métriques
            total_recommendations = len(recommendations)
            successful_recommendations = sum(actual_outcomes)
            
            accuracy = successful_recommendations / total_recommendations if total_recommendations > 0 else 0
            
            # Analyse par niveau de confiance
            confidence_performance = {}
            for confidence in RecommendationConfidence:
                conf_recs = [i for i, r in enumerate(recommendations) if r.confidence_level == confidence]
                if conf_recs:
                    conf_success = sum(actual_outcomes[i] for i in conf_recs)
                    confidence_performance[confidence.value] = conf_success / len(conf_recs)
            
            # Métriques avancées
            high_conf_recs = [r for r in recommendations if r.confidence_level == RecommendationConfidence.HIGH]
            precision_high_conf = len([r for r in high_conf_recs if actual_outcomes[recommendations.index(r)]]) / len(high_conf_recs) if high_conf_recs else 0
            
            metrics = {
                'overall_accuracy': accuracy,
                'total_recommendations': total_recommendations,
                'successful_recommendations': successful_recommendations,
                'precision_high_confidence': precision_high_conf,
                'confidence_performance': confidence_performance
            }
            
            logger.info(f"✅ Recommendation performance evaluated: {accuracy:.2%} accuracy")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error evaluating recommendation performance: {e}")
            return {}


# Instance globale
plan_recommendation_system = PlanRecommendationSystem()

# Export des classes principales
__all__ = [
    'PlanRecommendationSystem',
    'PlanRecommendation', 
    'CreatorProfile',
    'RecommendationContext',
    'RecommendationType',
    'RecommendationConfidence',
    'plan_recommendation_system'
]