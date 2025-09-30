"""
Viral Prediction Engine - Distribution Module
============================================
Prediction viral enterprise avec machine learning
et viral content amplification strategies.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
import numpy as np
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)

class ViralStage(Enum):
    """Stades viralité."""
    DORMANT = "dormant"
    EMERGING = "emerging"
    ACCELERATING = "accelerating"
    VIRAL = "viral"
    PEAK = "peak"
    DECLINING = "declining"

class ViralFactor(Enum):
    """Facteurs viralité."""
    CONTENT_QUALITY = "content_quality"
    TIMING = "timing"
    AUDIENCE_RELEVANCE = "audience_relevance"
    EMOTIONAL_TRIGGER = "emotional_trigger"
    SOCIAL_PROOF = "social_proof"
    TRENDING_TOPIC = "trending_topic"
    INFLUENCER_AMPLIFICATION = "influencer_amplification"
    ALGORITHM_BOOST = "algorithm_boost"

class TrendingCategory(Enum):
    """Catégories trending."""
    TECHNOLOGY = "technology"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    EDUCATION = "education"
    BUSINESS = "business"
    SPORTS = "sports"
    MUSIC = "music"

@dataclass
class ViralMetrics:
    """Métriques viralité."""
    viral_coefficient: float
    growth_rate: float
    acceleration: float
    share_velocity: float
    engagement_velocity: float
    reach_expansion_rate: float
    cross_platform_amplification: float

@dataclass
class ViralPrediction:
    """Prédiction viralité."""
    content_id: str
    predicted_viral_score: float
    viral_probability: float
    predicted_peak_time: datetime
    predicted_reach: int
    key_viral_factors: List[ViralFactor]
    recommended_amplification_strategy: str
    confidence_level: float
    platform_viral_scores: Dict[str, float]

@dataclass
class TrendingTopic:
    """Topic trending."""
    topic_id: str
    topic_name: str
    category: TrendingCategory
    trending_score: float
    growth_velocity: float
    predicted_duration: timedelta
    related_keywords: List[str]
    optimal_platforms: List[str]
    audience_segments: List[str]

@dataclass
class ViralContentPattern:
    """Pattern contenu viral."""
    pattern_id: str
    pattern_name: str
    content_characteristics: Dict[str, Any]
    viral_factors: List[ViralFactor]
    success_probability: float
    optimal_timing: Dict[str, Any]
    target_platforms: List[str]
    amplification_strategies: List[str]

@dataclass
class InfluencerCollaborationScore:
    """Score collaboration influenceur."""
    influencer_id: str
    collaboration_score: float
    audience_overlap: float
    amplification_potential: float
    engagement_boost_factor: float
    recommended_collaboration_type: str
    optimal_timing: datetime

class ViralPredictionEngine:
    """Prediction viral enterprise avec machine learning."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ml_models = {}
        self.trending_tracker = TrendingTopicTracker()
        self.timing_optimizer = ViralTimingOptimizer()
        self.hashtag_optimizer = HashtagOptimizer()
        self.influencer_analyzer = InfluencerCollaborationAnalyzer()
        self.amplification_engine = ViralAmplificationEngine()
        self.pattern_detector = ViralPatternDetector()
        
    async def viral_potential_scoring_ml(
        self,
        content_data: Dict[str, Any],
        creator_profile: Dict[str, Any],
        target_platforms: List[str]
    ) -> ViralPrediction:
        """Scoring ML potentiel viral avec prédictions détaillées."""
        try:
            content_id = content_data.get('content_id', str(hash(str(content_data))))
            
            # Extraction features pour ML
            content_features = await self._extract_content_features(content_data)
            creator_features = await self._extract_creator_features(creator_profile)
            platform_features = await self._extract_platform_features(target_platforms)
            temporal_features = await self._extract_temporal_features()
            
            # Combinaison features
            combined_features = {
                **content_features,
                **creator_features,
                **platform_features,
                **temporal_features
            }
            
            # Prédiction ML viralité globale
            global_viral_score = await self._predict_viral_score(combined_features)
            
            # Prédictions spécifiques par plateforme
            platform_scores = {}
            for platform in target_platforms:
                platform_specific_features = await self._extract_platform_specific_features(
                    combined_features, platform
                )
                platform_scores[platform] = await self._predict_platform_viral_score(
                    platform_specific_features, platform
                )
            
            # Identification facteurs clés
            key_factors = await self._identify_key_viral_factors(
                combined_features, global_viral_score
            )
            
            # Prédiction timing peak
            predicted_peak = await self._predict_viral_peak_timing(
                combined_features, target_platforms
            )
            
            # Estimation reach viral
            predicted_reach = await self._estimate_viral_reach(
                global_viral_score, creator_features, platform_scores
            )
            
            # Stratégie amplification recommandée
            amplification_strategy = await self._recommend_amplification_strategy(
                global_viral_score, key_factors, target_platforms
            )
            
            # Calcul confiance
            confidence = await self._calculate_prediction_confidence(
                combined_features, global_viral_score, platform_scores
            )
            
            return ViralPrediction(
                content_id=content_id,
                predicted_viral_score=global_viral_score,
                viral_probability=min(global_viral_score * 0.8, 1.0),
                predicted_peak_time=predicted_peak,
                predicted_reach=predicted_reach,
                key_viral_factors=key_factors,
                recommended_amplification_strategy=amplification_strategy,
                confidence_level=confidence,
                platform_viral_scores=platform_scores
            )
            
        except Exception as e:
            self.logger.error(f"Viral potential scoring error: {e}")
            return ViralPrediction("", 0.0, 0.0, datetime.now(), 0, [], "", 0.0, {})
    
    async def trending_topic_integration(
        self,
        content_categories: List[str],
        target_regions: List[str] = None
    ) -> List[TrendingTopic]:
        """Intégration trending topics avec opportunités viralité."""
        try:
            target_regions = target_regions or ['global']
            trending_topics = []
            
            for category in content_categories:
                category_enum = TrendingCategory(category.lower())
                
                # Récupération topics trending par catégorie/région
                regional_topics = await self.trending_tracker.get_trending_topics(
                    category_enum, target_regions
                )
                
                for topic_data in regional_topics:
                    # Analyse croissance et vélocité
                    growth_analysis = await self.trending_tracker.analyze_topic_growth(
                        topic_data
                    )
                    
                    # Prédiction durée trend
                    duration_prediction = await self.trending_tracker.predict_trend_duration(
                        topic_data, growth_analysis
                    )
                    
                    # Identification plateformes optimales
                    optimal_platforms = await self._identify_optimal_platforms_for_topic(
                        topic_data, category_enum
                    )
                    
                    # Identification segments audience cibles
                    target_segments = await self._identify_target_segments_for_topic(
                        topic_data, category_enum
                    )
                    
                    trending_topic = TrendingTopic(
                        topic_id=topic_data.get('topic_id'),
                        topic_name=topic_data.get('name'),
                        category=category_enum,
                        trending_score=topic_data.get('trending_score', 0.0),
                        growth_velocity=growth_analysis.get('velocity', 0.0),
                        predicted_duration=duration_prediction,
                        related_keywords=topic_data.get('keywords', []),
                        optimal_platforms=optimal_platforms,
                        audience_segments=target_segments
                    )
                    
                    trending_topics.append(trending_topic)
                    
            # Tri par score trending
            trending_topics.sort(key=lambda x: x.trending_score, reverse=True)
            
            return trending_topics
            
        except Exception as e:
            self.logger.error(f"Trending topic integration error: {e}")
            return []
    
    async def viral_timing_optimization(
        self,
        content_data: Dict[str, Any],
        target_platforms: List[str],
        trending_topics: List[TrendingTopic] = None
    ) -> Dict[str, datetime]:
        """Optimisation timing viral par plateforme."""
        try:
            optimal_timings = {}
            
            for platform in target_platforms:
                # Analyse fenêtres optimales plateforme
                platform_windows = await self.timing_optimizer.get_platform_optimal_windows(
                    platform
                )
                
                # Analyse activité audience
                audience_activity = await self.timing_optimizer.analyze_audience_activity_patterns(
                    platform, content_data.get('target_audience', {})
                )
                
                # Intégration trending topics si disponibles
                trending_boost_windows = []
                if trending_topics:
                    trending_boost_windows = await self.timing_optimizer.identify_trending_boost_windows(
                        trending_topics, platform
                    )
                
                # Évitement saturation contenu
                content_saturation = await self.timing_optimizer.analyze_content_saturation(
                    platform, content_data.get('category', '')
                )
                
                # Calcul timing optimal
                optimal_timing = await self.timing_optimizer.calculate_optimal_timing(
                    platform_windows,
                    audience_activity,
                    trending_boost_windows,
                    content_saturation
                )
                
                optimal_timings[platform] = optimal_timing
                
            return optimal_timings
            
        except Exception as e:
            self.logger.error(f"Viral timing optimization error: {e}")
            return {}
    
    async def hashtag_optimization_ai(
        self,
        content_data: Dict[str, Any],
        target_platforms: List[str],
        trending_topics: List[TrendingTopic] = None
    ) -> Dict[str, List[str]]:
        """Optimisation IA hashtags pour viralité."""
        try:
            platform_hashtags = {}
            
            # Extraction contexte contenu
            content_context = await self._extract_content_context(content_data)
            
            for platform in target_platforms:
                # Hashtags trending plateforme
                trending_hashtags = await self.hashtag_optimizer.get_trending_hashtags(
                    platform, content_context.get('category')
                )
                
                # Hashtags basés sur contenu
                content_hashtags = await self.hashtag_optimizer.generate_content_hashtags(
                    content_data, platform
                )
                
                # Hashtags trending topics
                topic_hashtags = []
                if trending_topics:
                    topic_hashtags = await self.hashtag_optimizer.extract_topic_hashtags(
                        trending_topics, platform
                    )
                
                # Hashtags communauté/niche
                niche_hashtags = await self.hashtag_optimizer.get_niche_hashtags(
                    content_context.get('niche', ''), platform
                )
                
                # Optimisation mix hashtags
                optimized_hashtags = await self.hashtag_optimizer.optimize_hashtag_mix(
                    trending_hashtags,
                    content_hashtags,
                    topic_hashtags,
                    niche_hashtags,
                    platform
                )
                
                platform_hashtags[platform] = optimized_hashtags
                
            return platform_hashtags
            
        except Exception as e:
            self.logger.error(f"Hashtag optimization error: {e}")
            return {}
    
    async def influencer_collaboration_scoring(
        self,
        creator_profile: Dict[str, Any],
        potential_collaborators: List[Dict[str, Any]],
        content_context: Dict[str, Any]
    ) -> List[InfluencerCollaborationScore]:
        """Scoring collaborations influenceurs pour amplification viral."""
        try:
            collaboration_scores = []
            
            for collaborator in potential_collaborators:
                # Analyse overlap audience
                audience_overlap = await self.influencer_analyzer.calculate_audience_overlap(
                    creator_profile.get('audience', {}),
                    collaborator.get('audience', {})
                )
                
                # Potentiel amplification
                amplification_potential = await self.influencer_analyzer.calculate_amplification_potential(
                    creator_profile,
                    collaborator,
                    content_context
                )
                
                # Facteur boost engagement
                engagement_boost = await self.influencer_analyzer.estimate_engagement_boost(
                    creator_profile.get('engagement_metrics', {}),
                    collaborator.get('engagement_metrics', {}),
                    audience_overlap
                )
                
                # Score collaboration global
                collaboration_score = await self.influencer_analyzer.calculate_collaboration_score(
                    audience_overlap,
                    amplification_potential,
                    engagement_boost,
                    content_context
                )
                
                # Type collaboration recommandé
                collaboration_type = await self._recommend_collaboration_type(
                    collaboration_score, audience_overlap, amplification_potential
                )
                
                # Timing optimal collaboration
                optimal_timing = await self._optimize_collaboration_timing(
                    creator_profile, collaborator, content_context
                )
                
                score_obj = InfluencerCollaborationScore(
                    influencer_id=collaborator.get('influencer_id'),
                    collaboration_score=collaboration_score,
                    audience_overlap=audience_overlap,
                    amplification_potential=amplification_potential,
                    engagement_boost_factor=engagement_boost,
                    recommended_collaboration_type=collaboration_type,
                    optimal_timing=optimal_timing
                )
                
                collaboration_scores.append(score_obj)
                
            # Tri par score collaboration
            collaboration_scores.sort(key=lambda x: x.collaboration_score, reverse=True)
            
            return collaboration_scores
            
        except Exception as e:
            self.logger.error(f"Influencer collaboration scoring error: {e}")
            return []
    
    async def viral_content_amplification(
        self,
        viral_prediction: ViralPrediction,
        amplification_budget: float,
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """Amplification contenu viral avec stratégies optimisées."""
        try:
            # Stratégie amplification basée sur prédiction
            base_strategy = viral_prediction.recommended_amplification_strategy
            
            # Répartition budget par plateforme
            budget_allocation = await self.amplification_engine.allocate_budget(
                amplification_budget,
                viral_prediction.platform_viral_scores,
                target_platforms
            )
            
            # Stratégies amplification par plateforme
            platform_strategies = {}
            for platform in target_platforms:
                platform_budget = budget_allocation.get(platform, 0)
                platform_viral_score = viral_prediction.platform_viral_scores.get(platform, 0)
                
                strategy = await self.amplification_engine.create_platform_strategy(
                    platform,
                    platform_budget,
                    platform_viral_score,
                    viral_prediction.key_viral_factors
                )
                
                platform_strategies[platform] = strategy
            
            # Timing amplification
            amplification_timeline = await self.amplification_engine.create_amplification_timeline(
                viral_prediction.predicted_peak_time,
                platform_strategies
            )
            
            # KPIs amplification
            expected_kpis = await self.amplification_engine.predict_amplification_kpis(
                viral_prediction,
                platform_strategies,
                amplification_budget
            )
            
            return {
                'amplification_strategy': base_strategy,
                'budget_allocation': budget_allocation,
                'platform_strategies': platform_strategies,
                'amplification_timeline': amplification_timeline,
                'expected_kpis': expected_kpis,
                'roi_prediction': await self._predict_amplification_roi(
                    amplification_budget, expected_kpis
                )
            }
            
        except Exception as e:
            self.logger.error(f"Viral content amplification error: {e}")
            return {}
    
    async def _extract_content_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extraction features contenu."""
        return {
            'content_type': content_data.get('type', 'video'),
            'duration': content_data.get('duration', 0),
            'quality_score': content_data.get('quality_score', 0.5),
            'emotional_intensity': content_data.get('emotional_intensity', 0.5),
            'novelty_score': content_data.get('novelty_score', 0.5),
            'production_value': content_data.get('production_value', 0.5),
            'hook_strength': content_data.get('hook_strength', 0.5),
            'call_to_action_presence': 1 if content_data.get('has_cta') else 0,
            'trending_elements': len(content_data.get('trending_elements', [])),
            'visual_appeal_score': content_data.get('visual_appeal', 0.5)
        }
    
    async def _extract_creator_features(self, creator_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extraction features créateur."""
        return {
            'follower_count': creator_profile.get('followers', 0),
            'engagement_rate': creator_profile.get('avg_engagement_rate', 0.03),
            'content_consistency': creator_profile.get('consistency_score', 0.5),
            'audience_loyalty': creator_profile.get('loyalty_score', 0.5),
            'viral_history': creator_profile.get('viral_content_count', 0),
            'platform_authority': creator_profile.get('authority_score', 0.5),
            'cross_platform_presence': len(creator_profile.get('platforms', [])),
            'brand_strength': creator_profile.get('brand_score', 0.5)
        }
    
    async def _predict_viral_score(self, features: Dict[str, Any]) -> float:
        """Prédiction score viral ML."""
        # Simulation modèle ML - en production, utiliser modèle entraîné
        base_score = 0.1
        
        # Pondération features
        weights = {
            'quality_score': 0.2,
            'emotional_intensity': 0.15,
            'novelty_score': 0.15,
            'engagement_rate': 0.2,
            'viral_history': 0.1,
            'trending_elements': 0.1,
            'hook_strength': 0.1
        }
        
        weighted_score = 0
        for feature, weight in weights.items():
            feature_value = features.get(feature, 0)
            weighted_score += feature_value * weight
        
        viral_score = base_score + weighted_score
        return min(viral_score, 1.0)

class TrendingTopicTracker:
    """Tracker topics trending."""
    
    async def get_trending_topics(
        self,
        category: TrendingCategory,
        regions: List[str]
    ) -> List[Dict[str, Any]]:
        """Récupération topics trending."""
        # Simulation données trending
        topics = []
        
        topic_templates = {
            TrendingCategory.TECHNOLOGY: ['AI', 'Blockchain', 'VR', 'IoT'],
            TrendingCategory.ENTERTAINMENT: ['Movie', 'TV Show', 'Gaming', 'Music'],
            TrendingCategory.NEWS: ['Politics', 'Economics', 'Science', 'Health']
        }
        
        template_topics = topic_templates.get(category, ['General'])
        
        for i, topic_name in enumerate(template_topics):
            topic = {
                'topic_id': f"{category.value}_{i}",
                'name': f"{topic_name} Trend",
                'trending_score': 0.6 + (hash(topic_name) % 40) / 100,
                'keywords': [topic_name.lower(), f"{topic_name}_trend", "viral"]
            }
            topics.append(topic)
        
        return topics

class ViralTimingOptimizer:
    """Optimiseur timing viral."""
    
    async def get_platform_optimal_windows(self, platform: str) -> List[tuple[int, int]]:
        """Fenêtres optimales plateforme."""
        platform_windows = {
            'instagram': [(8, 10), (14, 16), (19, 21)],
            'tiktok': [(6, 9), (12, 15), (19, 23)],
            'youtube': [(14, 16), (20, 22)],
            'twitter': [(8, 10), (12, 14), (17, 19)],
            'facebook': [(9, 11), (15, 17), (20, 22)]
        }
        
        return platform_windows.get(platform, [(12, 14), (18, 20)])

class HashtagOptimizer:
    """Optimiseur hashtags."""
    
    async def get_trending_hashtags(self, platform: str, category: str) -> List[str]:
        """Hashtags trending plateforme."""
        base_hashtags = {
            'instagram': ['#viral', '#trending', '#explore', '#fyp'],
            'tiktok': ['#fyp', '#viral', '#trending', '#foryou'],
            'twitter': ['#trending', '#viral', '#breaking'],
            'youtube': ['#viral', '#trending', '#youtube']
        }
        
        return base_hashtags.get(platform, ['#viral', '#trending'])
    
    async def optimize_hashtag_mix(
        self,
        trending: List[str],
        content: List[str],
        topic: List[str],
        niche: List[str],
        platform: str
    ) -> List[str]:
        """Optimisation mix hashtags."""
        # Limites par plateforme
        limits = {
            'instagram': 30,
            'tiktok': 100,
            'twitter': 2,
            'youtube': 15
        }
        
        limit = limits.get(platform, 10)
        
        # Mix optimal: 30% trending, 40% content, 20% topic, 10% niche
        optimized = (
            trending[:max(1, int(limit * 0.3))] +
            content[:max(1, int(limit * 0.4))] +
            topic[:max(1, int(limit * 0.2))] +
            niche[:max(1, int(limit * 0.1))]
        )
        
        return optimized[:limit]

class InfluencerCollaborationAnalyzer:
    """Analyseur collaborations influenceurs."""
    
    async def calculate_audience_overlap(
        self,
        creator_audience: Dict[str, Any],
        collaborator_audience: Dict[str, Any]
    ) -> float:
        """Calcul overlap audience."""
        # Simulation calcul overlap
        creator_size = creator_audience.get('size', 1000)
        collaborator_size = collaborator_audience.get('size', 1000)
        
        # Estimation overlap basée sur démographiques similaires
        overlap_percentage = 0.1 + (hash(str(creator_audience)) % 30) / 100
        return min(overlap_percentage, 0.5)

class ViralAmplificationEngine:
    """Engine amplification viral."""
    
    async def allocate_budget(
        self,
        total_budget: float,
        platform_scores: Dict[str, float],
        platforms: List[str]
    ) -> Dict[str, float]:
        """Répartition budget par plateforme."""
        if not platform_scores:
            equal_share = total_budget / len(platforms)
            return {platform: equal_share for platform in platforms}
        
        total_score = sum(platform_scores.values())
        if total_score == 0:
            equal_share = total_budget / len(platforms)
            return {platform: equal_share for platform in platforms}
        
        allocation = {}
        for platform in platforms:
            score = platform_scores.get(platform, 0)
            allocation[platform] = (score / total_score) * total_budget
        
        return allocation

class ViralPatternDetector:
    """Détecteur patterns viraux."""
    
    async def detect_viral_patterns(
        self,
        historical_viral_content: List[Dict[str, Any]]
    ) -> List[ViralContentPattern]:
        """Détection patterns contenu viral."""
        patterns = []
        
        # Pattern contenu court et accrocheur
        short_content_pattern = ViralContentPattern(
            pattern_id="short_engaging",
            pattern_name="Short Engaging Content",
            content_characteristics={
                'duration_range': (15, 60),
                'hook_timing': 'first_3_seconds',
                'emotional_intensity': 'high'
            },
            viral_factors=[ViralFactor.EMOTIONAL_TRIGGER, ViralFactor.TIMING],
            success_probability=0.75,
            optimal_timing={'hour_range': (19, 22)},
            target_platforms=['tiktok', 'instagram', 'youtube_shorts'],
            amplification_strategies=['hashtag_optimization', 'timing_optimization']
        )
        patterns.append(short_content_pattern)
        
        return patterns