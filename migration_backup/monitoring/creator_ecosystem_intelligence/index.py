"""
🎨 Creator Ecosystem Intelligence - Intelligence Créateurs
=========================================================

Module intelligence spécialisé pour l'écosystème créateurs Ainflue.
Surveillance, analyse et optimisation des collaborations créatives.

Fonctionnalités:
- Profiling créateurs multi-format (Musicien/Blogueur/Photographe/Influenceur/Comédien)
- Matching collaboration IA avec scoring compatibilité
- Prédiction succès collaboration ML
- Analytics performance créateurs
- Optimisation engagement audience
- Détection talents émergents

© 2025 Fahed Mlaiel - Architecture Monitoring Propriétaire Ultra-Avancée
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import random
import math


class CreatorType(Enum):
    """Types de créateurs Ainflue"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"


@dataclass
class CreatorProfile:
    """Profil créateur enterprise"""
    creator_id: str
    creator_type: CreatorType
    name: str
    skill_level: float  # 0.0 - 1.0
    engagement_rate: float
    follower_count: int
    collaboration_history: List[str]
    revenue_performance: Dict[str, float]
    content_quality_score: float
    audience_demographics: Dict[str, Any]
    platform_presence: Dict[str, bool]
    preferred_collaboration_types: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreatorMetrics:
    """Métriques performance créateur"""
    creator_id: str
    upload_frequency: float
    engagement_trend: float
    revenue_trend: float
    collaboration_success_rate: float
    content_virality_score: float
    audience_growth_rate: float
    platform_optimization_score: float
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationMatch:
    """Match collaboration entre créateurs"""
    match_id: str
    creator1_id: str
    creator2_id: str
    compatibility_score: float
    success_prediction: float
    estimated_revenue_boost: float
    collaboration_type: str
    match_reasons: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


class CreatorEcosystemIntelligence:
    """Intelligence écosystème créateurs Ainflue"""
    
    def __init__(self, config):
        self.config = config
        self.logger = self._setup_logging()
        
        # Data stores
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.creator_metrics: Dict[str, CreatorMetrics] = {}
        self.collaboration_matches: List[CollaborationMatch] = []
        self.collaboration_history: Dict[str, List[Dict]] = {}
        
        # Analytics
        self.performance_trends: Dict[str, List[float]] = {}
        self.collaboration_success_tracking: Dict[str, float] = {}
        
        # ML Models (simplified placeholders)
        self.compatibility_model_weights = {
            'skill_complement': 0.25,
            'audience_overlap': 0.30,
            'collaboration_history': 0.20,
            'revenue_similarity': 0.25
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("creator_intelligence")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation intelligence créateurs"""
        self.logger.info("🎨 Initialisation Creator Ecosystem Intelligence...")
        
        # Load sample data for demonstration
        await self._load_sample_creators()
        
        self.logger.info(f"✅ Intelligence créateurs initialisée - {len(self.creator_profiles)} créateurs")
    
    async def _load_sample_creators(self):
        """Chargement créateurs exemples pour démonstration"""
        sample_creators = [
            {
                'creator_id': 'musician_001',
                'type': CreatorType.MUSICIAN,
                'name': 'Alex Harmony',
                'skill_level': 0.85,
                'engagement_rate': 0.12,
                'follower_count': 25000,
                'content_quality_score': 0.90
            },
            {
                'creator_id': 'blogger_001',
                'type': CreatorType.BLOGGER,
                'name': 'Sophie Words',
                'skill_level': 0.78,
                'engagement_rate': 0.08,
                'follower_count': 15000,
                'content_quality_score': 0.82
            },
            {
                'creator_id': 'photographer_001',
                'type': CreatorType.PHOTOGRAPHER,
                'name': 'Marco Lens',
                'skill_level': 0.92,
                'engagement_rate': 0.15,
                'follower_count': 35000,
                'content_quality_score': 0.95
            },
            {
                'creator_id': 'influencer_001',
                'type': CreatorType.INFLUENCER,
                'name': 'Emma Social',
                'skill_level': 0.75,
                'engagement_rate': 0.18,
                'follower_count': 50000,
                'content_quality_score': 0.80
            },
            {
                'creator_id': 'comedian_001',
                'type': CreatorType.COMEDIAN,
                'name': 'Carlos Humor',
                'skill_level': 0.88,
                'engagement_rate': 0.22,
                'follower_count': 30000,
                'content_quality_score': 0.87
            }
        ]
        
        for creator_data in sample_creators:
            profile = CreatorProfile(
                creator_id=creator_data['creator_id'],
                creator_type=creator_data['type'],
                name=creator_data['name'],
                skill_level=creator_data['skill_level'],
                engagement_rate=creator_data['engagement_rate'],
                follower_count=creator_data['follower_count'],
                collaboration_history=[],
                revenue_performance={
                    'monthly_average': random.randint(500, 5000),
                    'growth_rate': random.uniform(0.05, 0.25)
                },
                content_quality_score=creator_data['content_quality_score'],
                audience_demographics={
                    'age_distribution': {'18-24': 0.3, '25-34': 0.4, '35-44': 0.2, '45+': 0.1},
                    'geographic_distribution': {'EU': 0.6, 'US': 0.3, 'Other': 0.1},
                    'interests': {'music': 0.7, 'lifestyle': 0.5, 'tech': 0.3}
                },
                platform_presence={
                    'youtube': True,
                    'instagram': True,
                    'tiktok': True,
                    'spotify': creator_data['type'] == CreatorType.MUSICIAN
                },
                preferred_collaboration_types=['cross_promotion', 'joint_content', 'event_collaboration']
            )
            
            self.creator_profiles[creator_data['creator_id']] = profile
            
            # Generate metrics
            metrics = CreatorMetrics(
                creator_id=creator_data['creator_id'],
                upload_frequency=random.uniform(0.5, 3.0),  # posts per day
                engagement_trend=random.uniform(-0.1, 0.2),
                revenue_trend=random.uniform(-0.05, 0.15),
                collaboration_success_rate=random.uniform(0.6, 0.95),
                content_virality_score=random.uniform(0.3, 0.9),
                audience_growth_rate=random.uniform(0.02, 0.12),
                platform_optimization_score=random.uniform(0.7, 0.95)
            )
            
            self.creator_metrics[creator_data['creator_id']] = metrics
    
    async def analyze_creator_compatibility(self, creator1_id: str, creator2_id: str) -> float:
        """Analyse compatibilité entre créateurs"""
        
        profile1 = self.creator_profiles.get(creator1_id)
        profile2 = self.creator_profiles.get(creator2_id)
        
        if not profile1 or not profile2:
            return 0.0
        
        # 1. Complémentarité des compétences (différence optimale)
        skill_diff = abs(profile1.skill_level - profile2.skill_level)
        skill_complement_score = 1.0 - min(skill_diff, 0.5) / 0.5  # Optimal difference: 0.2-0.3
        
        # 2. Audience overlap optimal (ni trop, ni trop peu)
        audience_overlap = self._calculate_audience_overlap(profile1, profile2)
        optimal_overlap = 0.3  # 30% optimal
        overlap_score = 1.0 - abs(audience_overlap - optimal_overlap) * 2
        overlap_score = max(0.0, min(1.0, overlap_score))
        
        # 3. Historique collaboration
        collaboration_history_score = self._analyze_collaboration_history(creator1_id, creator2_id)
        
        # 4. Similarité revenue (créateurs de niveau similaire)
        revenue_similarity = self._calculate_revenue_similarity(profile1, profile2)
        
        # Score compatibilité pondéré
        compatibility_score = (
            skill_complement_score * self.compatibility_model_weights['skill_complement'] +
            overlap_score * self.compatibility_model_weights['audience_overlap'] +
            collaboration_history_score * self.compatibility_model_weights['collaboration_history'] +
            revenue_similarity * self.compatibility_model_weights['revenue_similarity']
        )
        
        return min(compatibility_score, 1.0)
    
    def _calculate_audience_overlap(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calcul chevauchement audience"""
        demo1 = profile1.audience_demographics
        demo2 = profile2.audience_demographics
        
        # Analyse âge
        age_overlap = self._calculate_demographic_overlap(
            demo1.get('age_distribution', {}),
            demo2.get('age_distribution', {})
        )
        
        # Analyse géographique
        geo_overlap = self._calculate_demographic_overlap(
            demo1.get('geographic_distribution', {}),
            demo2.get('geographic_distribution', {})
        )
        
        # Analyse intérêts
        interests_overlap = self._calculate_demographic_overlap(
            demo1.get('interests', {}),
            demo2.get('interests', {})
        )
        
        # Score moyen pondéré
        return (age_overlap * 0.4 + geo_overlap * 0.3 + interests_overlap * 0.3)
    
    def _calculate_demographic_overlap(self, dist1: Dict[str, float], dist2: Dict[str, float]) -> float:
        """Calcul overlap entre deux distributions"""
        overlap = 0.0
        all_keys = set(dist1.keys()) | set(dist2.keys())
        
        for key in all_keys:
            val1 = dist1.get(key, 0.0)
            val2 = dist2.get(key, 0.0)
            overlap += min(val1, val2)
        
        return overlap
    
    def _analyze_collaboration_history(self, creator1_id: str, creator2_id: str) -> float:
        """Analyse historique collaboration"""
        # Check previous collaborations
        history1 = self.collaboration_history.get(creator1_id, [])
        history2 = self.collaboration_history.get(creator2_id, [])
        
        # Check if they collaborated before
        previous_collab = any(
            collab.get('partner_id') == creator2_id for collab in history1
        )
        
        if previous_collab:
            # Get previous success rate
            prev_success = next(
                (collab.get('success_rate', 0.0) for collab in history1 
                 if collab.get('partner_id') == creator2_id), 0.0
            )
            return prev_success
        
        # No previous collaboration - use average success rates
        avg_success1 = sum(collab.get('success_rate', 0.0) for collab in history1) / max(len(history1), 1)
        avg_success2 = sum(collab.get('success_rate', 0.0) for collab in history2) / max(len(history2), 1)
        
        return (avg_success1 + avg_success2) / 2 if history1 or history2 else 0.5
    
    def _calculate_revenue_similarity(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calcul similarité revenus"""
        revenue1 = profile1.revenue_performance.get('monthly_average', 0)
        revenue2 = profile2.revenue_performance.get('monthly_average', 0)
        
        if revenue1 == 0 or revenue2 == 0:
            return 0.0
        
        # Similarity based on revenue ratio (closer to 1.0 = more similar)
        ratio = min(revenue1, revenue2) / max(revenue1, revenue2)
        return ratio
    
    async def predict_collaboration_success(self, collaboration_data: Dict) -> float:
        """Prédiction succès collaboration"""
        creator1_id = collaboration_data.get('creator1_id')
        creator2_id = collaboration_data.get('creator2_id')
        compatibility_score = collaboration_data.get('compatibility_score', 0.0)
        
        if not creator1_id or not creator2_id:
            return 0.5
        
        # Get creator metrics
        metrics1 = self.creator_metrics.get(creator1_id)
        metrics2 = self.creator_metrics.get(creator2_id)
        
        if not metrics1 or not metrics2:
            return compatibility_score * 0.8  # Fallback to compatibility
        
        # Success prediction factors
        engagement_factor = (metrics1.engagement_trend + metrics2.engagement_trend) / 2
        growth_factor = (metrics1.audience_growth_rate + metrics2.audience_growth_rate) / 2
        quality_factor = (metrics1.content_virality_score + metrics2.content_virality_score) / 2
        
        # Base prediction on compatibility
        success_prediction = compatibility_score
        
        # Adjust based on trends and performance
        success_prediction += engagement_factor * 0.1
        success_prediction += growth_factor * 0.15
        success_prediction += quality_factor * 0.1
        
        # Apply collaboration history
        avg_success_rate = (metrics1.collaboration_success_rate + metrics2.collaboration_success_rate) / 2
        success_prediction = (success_prediction + avg_success_rate) / 2
        
        return min(success_prediction, 1.0)
    
    async def recommend_optimal_collaborations(self, creator_id: str, limit: int = 5) -> List[CollaborationMatch]:
        """Recommandation collaborations optimales"""
        
        recommendations = []
        creator_profile = self.creator_profiles.get(creator_id)
        
        if not creator_profile:
            return recommendations
        
        # Analyse tous les créateurs potentiels
        for potential_partner_id, partner_profile in self.creator_profiles.items():
            if potential_partner_id == creator_id:
                continue
            
            # Score compatibilité
            compatibility = await self.analyze_creator_compatibility(creator_id, potential_partner_id)
            
            # Prédiction succès
            collaboration_data = {
                'creator1_id': creator_id,
                'creator2_id': potential_partner_id,
                'compatibility_score': compatibility
            }
            success_prediction = await self.predict_collaboration_success(collaboration_data)
            
            # Estimation boost revenus
            revenue_boost = self._estimate_revenue_boost(creator_profile, partner_profile, compatibility)
            
            # Type collaboration suggéré
            collaboration_type = self._suggest_collaboration_type(creator_profile, partner_profile)
            
            # Raisons du match
            match_reasons = self._generate_match_reasons(creator_profile, partner_profile, compatibility)
            
            # Création match
            match = CollaborationMatch(
                match_id=str(uuid.uuid4()),
                creator1_id=creator_id,
                creator2_id=potential_partner_id,
                compatibility_score=compatibility,
                success_prediction=success_prediction,
                estimated_revenue_boost=revenue_boost,
                collaboration_type=collaboration_type,
                match_reasons=match_reasons
            )
            
            recommendations.append(match)
        
        # Tri par score global (compatibilité + prédiction succès)
        recommendations.sort(
            key=lambda x: (x.compatibility_score * 0.6 + x.success_prediction * 0.4), 
            reverse=True
        )
        
        return recommendations[:limit]
    
    def _estimate_revenue_boost(self, profile1: CreatorProfile, profile2: CreatorProfile, compatibility: float) -> float:
        """Estimation boost revenus collaboration"""
        base_revenue1 = profile1.revenue_performance.get('monthly_average', 1000)
        base_revenue2 = profile2.revenue_performance.get('monthly_average', 1000)
        
        # Combined audience potential
        combined_reach = profile1.follower_count + profile2.follower_count
        
        # Boost factor based on compatibility and reach
        boost_factor = compatibility * 0.3 + (combined_reach / 100000) * 0.1
        boost_factor = min(boost_factor, 0.5)  # Max 50% boost
        
        estimated_boost = (base_revenue1 + base_revenue2) * boost_factor
        return round(estimated_boost, 2)
    
    def _suggest_collaboration_type(self, profile1: CreatorProfile, profile2: CreatorProfile) -> str:
        """Suggestion type collaboration"""
        type_combinations = {
            (CreatorType.MUSICIAN, CreatorType.BLOGGER): "music_review_series",
            (CreatorType.MUSICIAN, CreatorType.PHOTOGRAPHER): "music_video_collaboration",
            (CreatorType.MUSICIAN, CreatorType.INFLUENCER): "music_promotion_campaign",
            (CreatorType.MUSICIAN, CreatorType.COMEDIAN): "musical_comedy_content",
            (CreatorType.BLOGGER, CreatorType.PHOTOGRAPHER): "visual_storytelling_series",
            (CreatorType.BLOGGER, CreatorType.INFLUENCER): "lifestyle_content_series",
            (CreatorType.BLOGGER, CreatorType.COMEDIAN): "humorous_lifestyle_content",
            (CreatorType.PHOTOGRAPHER, CreatorType.INFLUENCER): "visual_brand_campaign",
            (CreatorType.PHOTOGRAPHER, CreatorType.COMEDIAN): "comedy_photo_series",
            (CreatorType.INFLUENCER, CreatorType.COMEDIAN): "comedy_lifestyle_content"
        }
        
        # Sort by enum value instead of enum object
        type_key = tuple(sorted([profile1.creator_type.value, profile2.creator_type.value]))
        
        # Check all combinations with enum values
        for (type1, type2), collab_type in type_combinations.items():
            if tuple(sorted([type1.value, type2.value])) == type_key:
                return collab_type
                
        return "cross_promotion_campaign"
    
    def _generate_match_reasons(self, profile1: CreatorProfile, profile2: CreatorProfile, compatibility: float) -> List[str]:
        """Génération raisons du match"""
        reasons = []
        
        if compatibility > 0.8:
            reasons.append("Excellent compatibility score")
        
        # Skill complementarity
        skill_diff = abs(profile1.skill_level - profile2.skill_level)
        if 0.1 <= skill_diff <= 0.3:
            reasons.append("Complementary skill levels")
        
        # Audience analysis
        overlap = self._calculate_audience_overlap(profile1, profile2)
        if 0.2 <= overlap <= 0.4:
            reasons.append("Optimal audience overlap")
        
        # Platform synergy
        common_platforms = set(
            [p for p, present in profile1.platform_presence.items() if present]
        ).intersection(
            [p for p, present in profile2.platform_presence.items() if present]
        )
        if len(common_platforms) >= 2:
            reasons.append(f"Strong platform synergy ({len(common_platforms)} platforms)")
        
        # Growth potential
        metrics1 = self.creator_metrics.get(profile1.creator_id)
        metrics2 = self.creator_metrics.get(profile2.creator_id)
        if metrics1 and metrics2:
            avg_growth = (metrics1.audience_growth_rate + metrics2.audience_growth_rate) / 2
            if avg_growth > 0.08:
                reasons.append("High growth potential")
        
        return reasons[:3]  # Limit to top 3 reasons
    
    async def track_creator_performance(self, creator_id: str, performance_data: Dict):
        """Tracking performance créateur"""
        metrics = self.creator_metrics.get(creator_id)
        if not metrics:
            return
        
        # Update metrics based on new data
        if 'engagement_rate' in performance_data:
            metrics.engagement_trend = performance_data['engagement_rate'] - metrics.engagement_trend
        
        if 'revenue' in performance_data:
            current_revenue = self.creator_profiles[creator_id].revenue_performance.get('monthly_average', 0)
            metrics.revenue_trend = (performance_data['revenue'] - current_revenue) / current_revenue if current_revenue > 0 else 0
        
        metrics.calculated_at = datetime.utcnow()
        
        self.logger.info(f"Performance updated for creator {creator_id}")
    
    async def track_collaboration_outcome(self, collaboration_id: str, outcome_data: Dict):
        """Tracking résultat collaboration"""
        success_rate = outcome_data.get('success_rate', 0.0)
        creator1_id = outcome_data.get('creator1_id')
        creator2_id = outcome_data.get('creator2_id')
        
        # Store collaboration outcome
        self.collaboration_success_tracking[collaboration_id] = success_rate
        
        # Update collaboration history
        if creator1_id:
            if creator1_id not in self.collaboration_history:
                self.collaboration_history[creator1_id] = []
            self.collaboration_history[creator1_id].append({
                'collaboration_id': collaboration_id,
                'partner_id': creator2_id,
                'success_rate': success_rate,
                'date': datetime.utcnow().isoformat()
            })
        
        self.logger.info(f"Collaboration outcome tracked: {collaboration_id} - Success: {success_rate}")
    
    async def get_creator_insights(self, creator_id: str) -> Dict[str, Any]:
        """Insights détaillés créateur"""
        profile = self.creator_profiles.get(creator_id)
        metrics = self.creator_metrics.get(creator_id)
        
        if not profile or not metrics:
            return {}
        
        # Generate recommendations
        recommendations = await self.recommend_optimal_collaborations(creator_id, 3)
        
        return {
            'creator_profile': {
                'id': profile.creator_id,
                'name': profile.name,
                'type': profile.creator_type.value,
                'skill_level': profile.skill_level,
                'follower_count': profile.follower_count,
                'content_quality': profile.content_quality_score
            },
            'performance_metrics': {
                'engagement_trend': metrics.engagement_trend,
                'revenue_trend': metrics.revenue_trend,
                'collaboration_success_rate': metrics.collaboration_success_rate,
                'virality_score': metrics.content_virality_score,
                'growth_rate': metrics.audience_growth_rate
            },
            'collaboration_recommendations': [
                {
                    'partner_id': rec.creator2_id,
                    'partner_name': self.creator_profiles[rec.creator2_id].name,
                    'compatibility': rec.compatibility_score,
                    'success_prediction': rec.success_prediction,
                    'revenue_boost': rec.estimated_revenue_boost,
                    'collaboration_type': rec.collaboration_type,
                    'reasons': rec.match_reasons
                }
                for rec in recommendations
            ],
            'optimization_suggestions': await self._generate_optimization_suggestions(creator_id)
        }
    
    async def _generate_optimization_suggestions(self, creator_id: str) -> List[str]:
        """Génération suggestions optimisation"""
        metrics = self.creator_metrics.get(creator_id)
        if not metrics:
            return []
        
        suggestions = []
        
        if metrics.engagement_trend < 0:
            suggestions.append("Focus on improving content engagement through interactive elements")
        
        if metrics.audience_growth_rate < 0.05:
            suggestions.append("Increase posting frequency and cross-platform promotion")
        
        if metrics.collaboration_success_rate < 0.7:
            suggestions.append("Choose collaboration partners more strategically")
        
        if metrics.platform_optimization_score < 0.8:
            suggestions.append("Optimize content format for each platform's algorithm")
        
        return suggestions
    
    async def get_ecosystem_overview(self) -> Dict[str, Any]:
        """Vue d'ensemble écosystème créateurs"""
        total_creators = len(self.creator_profiles)
        
        # Creator type distribution
        type_distribution = {}
        for profile in self.creator_profiles.values():
            creator_type = profile.creator_type.value
            type_distribution[creator_type] = type_distribution.get(creator_type, 0) + 1
        
        # Average metrics
        all_metrics = list(self.creator_metrics.values())
        avg_engagement = sum(m.engagement_trend for m in all_metrics) / len(all_metrics) if all_metrics else 0
        avg_growth = sum(m.audience_growth_rate for m in all_metrics) / len(all_metrics) if all_metrics else 0
        
        return {
            'total_creators': total_creators,
            'creator_types': type_distribution,
            'ecosystem_health': {
                'avg_engagement_trend': avg_engagement,
                'avg_growth_rate': avg_growth,
                'collaboration_matches_today': len([m for m in self.collaboration_matches if 
                                                   (datetime.utcnow() - m.created_at).days == 0])
            },
            'top_performers': await self._get_top_performers(5),
            'collaboration_opportunities': len(await self.recommend_optimal_collaborations('musician_001', 10))
        }
    
    async def _get_top_performers(self, limit: int) -> List[Dict[str, Any]]:
        """Top performers écosystème"""
        performers = []
        
        for creator_id, metrics in self.creator_metrics.items():
            profile = self.creator_profiles.get(creator_id)
            if profile:
                # Performance score composite
                performance_score = (
                    metrics.engagement_trend * 0.3 +
                    metrics.revenue_trend * 0.3 +
                    metrics.audience_growth_rate * 0.2 +
                    metrics.content_virality_score * 0.2
                )
                
                performers.append({
                    'creator_id': creator_id,
                    'name': profile.name,
                    'type': profile.creator_type.value,
                    'performance_score': performance_score,
                    'follower_count': profile.follower_count
                })
        
        performers.sort(key=lambda x: x['performance_score'], reverse=True)
        return performers[:limit]
    
    async def shutdown(self):
        """Arrêt propre module"""
        self.logger.info("⏹️ Arrêt Creator Ecosystem Intelligence...")
        
        # Clear data
        self.creator_profiles.clear()
        self.creator_metrics.clear()
        self.collaboration_matches.clear()
        
        self.logger.info("✅ Creator Intelligence arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_creator_intelligence():
        class MockConfig:
            debug = True
        
        intelligence = CreatorEcosystemIntelligence(MockConfig())
        await intelligence.initialize()
        
        # Test compatibility analysis
        compatibility = await intelligence.analyze_creator_compatibility('musician_001', 'photographer_001')
        print(f"Compatibility score: {compatibility}")
        
        # Test recommendations
        recommendations = await intelligence.recommend_optimal_collaborations('musician_001', 3)
        print(f"Recommendations: {len(recommendations)}")
        
        # Test ecosystem overview
        overview = await intelligence.get_ecosystem_overview()
        print("Ecosystem overview:", json.dumps(overview, indent=2, default=str))
        
        await intelligence.shutdown()
    
    asyncio.run(test_creator_intelligence())