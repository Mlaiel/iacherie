"""
⚡ Live Creator Analytics - Analytics Créateur Temps Réel
========================================================

Analytics créateur temps réel ultra-avancées pour surveillance instantanée
de l'engagement, audience et performance multi-plateforme.

Fonctionnalités:
- Real-time creator engagement tracking
- Live audience analytics et démographiques  
- Instant content performance metrics
- Creator journey live monitoring
- Multi-platform sync analytics
- Predictive audience growth analysis

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from collections import deque, defaultdict
import statistics
import math
import numpy as np
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EngagementType(Enum):
    """Types d'engagement créateur"""
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CLICKS = "clicks"
    DOWNLOADS = "downloads"
    PURCHASES = "purchases"
    COLLABORATIONS = "collaborations"
    FOLLOW = "follow"


class PlatformType(Enum):
    """Types de plateformes"""
    AINFLUE = "ainflue"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    ONLYFANS = "onlyfans"


class AudienceSegment(Enum):
    """Segments d'audience"""
    GEN_Z = "gen_z"
    MILLENNIALS = "millennials"
    GEN_X = "gen_x"
    BOOMERS = "boomers"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CREATORS = "creators"
    BRANDS = "brands"


@dataclass
class CreatorMetrics:
    """Métriques créateur temps réel"""
    creator_id: str
    timestamp: datetime
    platform: PlatformType
    engagement_rate: float
    audience_size: int
    revenue_24h: float
    content_count: int
    collaboration_score: float
    viral_potential: float
    audience_growth_rate: float
    geographic_reach: Dict[str, int] = field(default_factory=dict)
    demographic_breakdown: Dict[str, float] = field(default_factory=dict)
    engagement_breakdown: Dict[EngagementType, int] = field(default_factory=dict)


@dataclass
class AudienceInsight:
    """Insight audience temps réel"""
    segment: AudienceSegment
    size: int
    growth_rate: float
    engagement_level: float
    conversion_rate: float
    lifetime_value: float
    geographic_distribution: Dict[str, float]
    behavior_patterns: Dict[str, Any]
    prediction_confidence: float


@dataclass
class ContentPerformance:
    """Performance contenu temps réel"""
    content_id: str
    creator_id: str
    platform: PlatformType
    publish_time: datetime
    current_views: int
    engagement_score: float
    viral_velocity: float
    predicted_peak: datetime
    monetization_potential: float
    audience_sentiment: float
    share_velocity: float
    comment_sentiment: float


@dataclass
class CreatorJourney:
    """Parcours créateur temps réel"""
    creator_id: str
    stage: str
    milestone_progress: float
    next_milestone: str
    growth_trajectory: str
    blockers: List[str]
    opportunities: List[str]
    recommended_actions: List[str]
    success_probability: float


class LiveCreatorAnalytics:
    """
    Analytics créateur temps réel ultra-avancées
    
    Surveillance instantanée de l'engagement, audience et performance
    multi-plateforme avec intelligence prédictive et insights actionables.
    """
    
    def __init__(self, 
                 buffer_size: int = 10000,
                 analytics_window: int = 300,
                 prediction_horizon: int = 3600):
        """
        Initialise analytics créateur temps réel
        
        Args:
            buffer_size: Taille buffer métriques
            analytics_window: Fenêtre analyse en secondes  
            prediction_horizon: Horizon prédiction en secondes
        """
        self.buffer_size = buffer_size
        self.analytics_window = analytics_window
        self.prediction_horizon = prediction_horizon
        
        # Buffers métriques temps réel
        self.creator_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=buffer_size)
        )
        self.audience_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=buffer_size)
        )
        self.content_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=buffer_size)
        )
        
        # Analytics état
        self.active_creators: Set[str] = set()
        self.trending_creators: Dict[str, float] = {}
        self.audience_insights: Dict[str, List[AudienceInsight]] = {}
        self.journey_tracking: Dict[str, CreatorJourney] = {}
        
        # ML Models (simulation pour démo)
        self.engagement_predictor = self._init_engagement_predictor()
        self.growth_predictor = self._init_growth_predictor()
        self.viral_predictor = self._init_viral_predictor()
        
        logger.info("LiveCreatorAnalytics initialisé avec succès")
    
    def _init_engagement_predictor(self):
        """Initialise prédicteur engagement"""
        # Simulation ML model - en production utiliser TensorFlow/PyTorch
        return {
            'model_type': 'engagement_lstm',
            'accuracy': 0.89,
            'last_trained': datetime.now(),
            'features': ['views', 'likes', 'shares', 'time_of_day', 'platform']
        }
    
    def _init_growth_predictor(self):
        """Initialise prédicteur croissance"""
        return {
            'model_type': 'growth_transformer',
            'accuracy': 0.92,
            'last_trained': datetime.now(),
            'features': ['historical_growth', 'content_quality', 'engagement_rate']
        }
    
    def _init_viral_predictor(self):
        """Initialise prédicteur viral"""
        return {
            'model_type': 'viral_cnn',
            'accuracy': 0.85,
            'last_trained': datetime.now(),
            'features': ['share_velocity', 'comment_sentiment', 'platform_algorithm']
        }
    
    async def track_creator_activity(self, 
                                   creator_id: str,
                                   platform: PlatformType,
                                   activity_data: Dict[str, Any]) -> CreatorMetrics:
        """
        Track activité créateur temps réel
        
        Args:
            creator_id: ID créateur
            platform: Plateforme
            activity_data: Données activité
            
        Returns:
            CreatorMetrics: Métriques calculées
        """
        try:
            # Calcul métriques engagement
            engagement_rate = await self._calculate_engagement_rate(
                creator_id, activity_data
            )
            
            # Analyse audience
            audience_size = activity_data.get('followers', 0)
            audience_growth = await self._calculate_audience_growth(
                creator_id, audience_size
            )
            
            # Revenue tracking
            revenue_24h = await self._calculate_daily_revenue(
                creator_id, activity_data
            )
            
            # Score collaboration
            collaboration_score = await self._calculate_collaboration_score(
                creator_id, activity_data
            )
            
            # Potentiel viral
            viral_potential = await self._predict_viral_potential(
                creator_id, activity_data
            )
            
            # Création métriques
            metrics = CreatorMetrics(
                creator_id=creator_id,
                timestamp=datetime.now(),
                platform=platform,
                engagement_rate=engagement_rate,
                audience_size=audience_size,
                revenue_24h=revenue_24h,
                content_count=activity_data.get('content_count', 0),
                collaboration_score=collaboration_score,
                viral_potential=viral_potential,
                audience_growth_rate=audience_growth,
                geographic_reach=activity_data.get('geographic_reach', {}),
                demographic_breakdown=activity_data.get('demographics', {}),
                engagement_breakdown=self._parse_engagement_data(activity_data)
            )
            
            # Stockage dans buffer
            self.creator_metrics[creator_id].append(metrics)
            self.active_creators.add(creator_id)
            
            # Mise à jour journey
            await self._update_creator_journey(creator_id, metrics)
            
            logger.info(f"Métriques créateur trackées: {creator_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur track creator activity: {e}")
            raise
    
    async def analyze_audience_insights(self, 
                                      creator_id: str) -> List[AudienceInsight]:
        """
        Analyse insights audience temps réel
        
        Args:
            creator_id: ID créateur
            
        Returns:
            List[AudienceInsight]: Insights audience
        """
        try:
            insights = []
            
            # Récupération métriques récentes
            recent_metrics = list(self.creator_metrics[creator_id])[-100:]
            if not recent_metrics:
                return insights
            
            # Analyse par segment
            for segment in AudienceSegment:
                insight = await self._analyze_audience_segment(
                    creator_id, segment, recent_metrics
                )
                if insight:
                    insights.append(insight)
            
            # Stockage insights
            self.audience_insights[creator_id] = insights
            
            logger.info(f"Insights audience analysés: {creator_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Erreur analyse audience insights: {e}")
            return []
    
    async def track_content_performance(self, 
                                      content_id: str,
                                      creator_id: str,
                                      platform: PlatformType,
                                      performance_data: Dict[str, Any]) -> ContentPerformance:
        """
        Track performance contenu temps réel
        
        Args:
            content_id: ID contenu
            creator_id: ID créateur
            platform: Plateforme
            performance_data: Données performance
            
        Returns:
            ContentPerformance: Performance calculée
        """
        try:
            # Calcul vitesse viral
            viral_velocity = await self._calculate_viral_velocity(
                content_id, performance_data
            )
            
            # Prédiction pic
            predicted_peak = await self._predict_performance_peak(
                content_id, performance_data
            )
            
            # Potentiel monétisation
            monetization_potential = await self._calculate_monetization_potential(
                content_id, creator_id, performance_data
            )
            
            # Sentiment analysis
            audience_sentiment = await self._analyze_content_sentiment(
                content_id, performance_data
            )
            
            # Création performance object
            performance = ContentPerformance(
                content_id=content_id,
                creator_id=creator_id,
                platform=platform,
                publish_time=performance_data.get(
                    'publish_time', datetime.now()
                ),
                current_views=performance_data.get('views', 0),
                engagement_score=performance_data.get('engagement_score', 0.0),
                viral_velocity=viral_velocity,
                predicted_peak=predicted_peak,
                monetization_potential=monetization_potential,
                audience_sentiment=audience_sentiment,
                share_velocity=performance_data.get('share_velocity', 0.0),
                comment_sentiment=performance_data.get('comment_sentiment', 0.0)
            )
            
            # Stockage métriques contenu
            self.content_metrics[content_id].append(performance)
            
            logger.info(f"Performance contenu trackée: {content_id}")
            return performance
            
        except Exception as e:
            logger.error(f"Erreur track content performance: {e}")
            raise
    
    async def get_creator_journey(self, creator_id: str) -> Optional[CreatorJourney]:
        """
        Récupère parcours créateur temps réel
        
        Args:
            creator_id: ID créateur
            
        Returns:
            Optional[CreatorJourney]: Parcours si disponible
        """
        return self.journey_tracking.get(creator_id)
    
    async def get_trending_creators(self, 
                                  platform: Optional[PlatformType] = None,
                                  limit: int = 50) -> Dict[str, float]:
        """
        Récupère créateurs trending temps réel
        
        Args:
            platform: Plateforme spécifique (optionnel)
            limit: Nombre maximum résultats
            
        Returns:
            Dict[str, float]: Créateurs et scores trending
        """
        try:
            # Calcul scores trending
            trending_scores = {}
            
            for creator_id in self.active_creators:
                score = await self._calculate_trending_score(creator_id, platform)
                if score > 0:
                    trending_scores[creator_id] = score
            
            # Tri par score
            sorted_trending = dict(
                sorted(trending_scores.items(), 
                      key=lambda x: x[1], reverse=True)[:limit]
            )
            
            self.trending_creators = sorted_trending
            
            logger.info(f"Trending creators calculés: {len(sorted_trending)}")
            return sorted_trending
            
        except Exception as e:
            logger.error(f"Erreur get trending creators: {e}")
            return {}
    
    async def predict_creator_growth(self, 
                                   creator_id: str,
                                   horizon_days: int = 30) -> Dict[str, Any]:
        """
        Prédit croissance créateur
        
        Args:
            creator_id: ID créateur
            horizon_days: Horizon prédiction en jours
            
        Returns:
            Dict[str, Any]: Prédictions croissance
        """
        try:
            # Récupération historique
            metrics_history = list(self.creator_metrics[creator_id])[-1000:]
            if len(metrics_history) < 10:
                return {'error': 'Données insuffisantes pour prédiction'}
            
            # Calcul tendances
            audience_trend = self._calculate_growth_trend(
                [m.audience_size for m in metrics_history]
            )
            engagement_trend = self._calculate_growth_trend(
                [m.engagement_rate for m in metrics_history]
            )
            revenue_trend = self._calculate_growth_trend(
                [m.revenue_24h for m in metrics_history]
            )
            
            # Prédictions ML (simulation)
            predicted_audience = await self._predict_audience_growth(
                creator_id, horizon_days
            )
            predicted_revenue = await self._predict_revenue_growth(
                creator_id, horizon_days
            )
            
            return {
                'creator_id': creator_id,
                'prediction_horizon_days': horizon_days,
                'current_audience': metrics_history[-1].audience_size,
                'predicted_audience': predicted_audience,
                'audience_growth_rate': audience_trend,
                'current_engagement': metrics_history[-1].engagement_rate,
                'engagement_trend': engagement_trend,
                'current_revenue_24h': metrics_history[-1].revenue_24h,
                'predicted_revenue_30d': predicted_revenue,
                'revenue_trend': revenue_trend,
                'confidence_score': 0.85,
                'risk_factors': await self._identify_growth_risks(creator_id),
                'growth_opportunities': await self._identify_growth_opportunities(creator_id)
            }
            
        except Exception as e:
            logger.error(f"Erreur predict creator growth: {e}")
            return {'error': str(e)}
    
    # Méthodes privées d'aide
    
    async def _calculate_engagement_rate(self, 
                                       creator_id: str, 
                                       activity_data: Dict[str, Any]) -> float:
        """Calcule taux engagement"""
        try:
            total_interactions = (
                activity_data.get('likes', 0) +
                activity_data.get('comments', 0) +
                activity_data.get('shares', 0)
            )
            followers = activity_data.get('followers', 1)
            return min(total_interactions / followers * 100, 100.0)
        except:
            return 0.0
    
    async def _calculate_audience_growth(self, 
                                       creator_id: str, 
                                       current_size: int) -> float:
        """Calcule croissance audience"""
        try:
            history = list(self.creator_metrics[creator_id])
            if len(history) < 2:
                return 0.0
            
            previous_size = history[-1].audience_size
            if previous_size == 0:
                return 0.0
            
            return ((current_size - previous_size) / previous_size) * 100
        except:
            return 0.0
    
    async def _calculate_daily_revenue(self, 
                                     creator_id: str, 
                                     activity_data: Dict[str, Any]) -> float:
        """Calcule revenue 24h"""
        # Simulation - en production intégration payment systems
        base_revenue = activity_data.get('revenue', 0.0)
        engagement_multiplier = 1 + (activity_data.get('engagement_rate', 0) / 100)
        return base_revenue * engagement_multiplier
    
    async def _calculate_collaboration_score(self, 
                                           creator_id: str, 
                                           activity_data: Dict[str, Any]) -> float:
        """Calcule score collaboration"""
        # Facteurs: engagement, audience, brand safety, historique
        factors = {
            'engagement': activity_data.get('engagement_rate', 0) / 100,
            'audience_size': min(activity_data.get('followers', 0) / 100000, 1),
            'brand_safety': activity_data.get('brand_safety_score', 0.8),
            'collaboration_history': activity_data.get('past_collaborations', 0) / 10
        }
        
        weights = [0.3, 0.25, 0.25, 0.2]
        score = sum(v * w for v, w in zip(factors.values(), weights))
        return min(score * 100, 100.0)
    
    async def _predict_viral_potential(self, 
                                     creator_id: str, 
                                     activity_data: Dict[str, Any]) -> float:
        """Prédit potentiel viral"""
        # Facteurs viral: engagement velocity, share rate, timing, trend alignment
        velocity = activity_data.get('engagement_velocity', 0)
        share_rate = activity_data.get('share_rate', 0)
        timing_score = activity_data.get('optimal_timing_score', 0.5)
        trend_alignment = activity_data.get('trend_alignment', 0.5)
        
        viral_score = (velocity * 0.4 + share_rate * 0.3 + 
                      timing_score * 0.15 + trend_alignment * 0.15)
        
        return min(viral_score * 100, 100.0)
    
    def _parse_engagement_data(self, activity_data: Dict[str, Any]) -> Dict[EngagementType, int]:
        """Parse données engagement"""
        engagement = {}
        for engagement_type in EngagementType:
            key = engagement_type.value
            engagement[engagement_type] = activity_data.get(key, 0)
        return engagement
    
    async def _update_creator_journey(self, 
                                    creator_id: str, 
                                    metrics: CreatorMetrics):
        """Met à jour parcours créateur"""
        # Logique simplifiée - en production utiliser ML sophistiqué
        current_stage = self._determine_creator_stage(metrics)
        
        journey = CreatorJourney(
            creator_id=creator_id,
            stage=current_stage,
            milestone_progress=self._calculate_milestone_progress(metrics),
            next_milestone=self._get_next_milestone(current_stage),
            growth_trajectory=self._assess_growth_trajectory(creator_id),
            blockers=await self._identify_blockers(creator_id),
            opportunities=await self._identify_opportunities(creator_id),
            recommended_actions=await self._get_recommended_actions(creator_id),
            success_probability=self._calculate_success_probability(metrics)
        )
        
        self.journey_tracking[creator_id] = journey
    
    def _determine_creator_stage(self, metrics: CreatorMetrics) -> str:
        """Détermine stage créateur"""
        if metrics.audience_size < 1000:
            return "emerging"
        elif metrics.audience_size < 10000:
            return "growing"
        elif metrics.audience_size < 100000:
            return "established"
        elif metrics.audience_size < 1000000:
            return "influential"
        else:
            return "celebrity"
    
    def _calculate_milestone_progress(self, metrics: CreatorMetrics) -> float:
        """Calcule progrès milestone"""
        stage_thresholds = {
            "emerging": 1000,
            "growing": 10000,
            "established": 100000,
            "influential": 1000000
        }
        
        current_stage = self._determine_creator_stage(metrics)
        if current_stage == "celebrity":
            return 100.0
        
        threshold = stage_thresholds.get(current_stage, 1000)
        return (metrics.audience_size / threshold) * 100
    
    def _get_next_milestone(self, current_stage: str) -> str:
        """Récupère prochaine milestone"""
        milestones = {
            "emerging": "1K followers",
            "growing": "10K followers", 
            "established": "100K followers",
            "influential": "1M followers",
            "celebrity": "Maintain position"
        }
        return milestones.get(current_stage, "Unknown")
    
    # Méthodes utilitaires additionnelles
    
    async def _analyze_audience_segment(self, 
                                      creator_id: str,
                                      segment: AudienceSegment,
                                      metrics: List[CreatorMetrics]) -> Optional[AudienceInsight]:
        """Analyse segment audience spécifique"""
        # Simulation analyse segment
        if not metrics:
            return None
        
        # Calcul métriques segment (simulation)
        segment_size = int(metrics[-1].audience_size * 0.2)  # 20% par segment
        growth_rate = statistics.mean([m.audience_growth_rate for m in metrics[-10:]])
        engagement_level = statistics.mean([m.engagement_rate for m in metrics[-10:]])
        
        return AudienceInsight(
            segment=segment,
            size=segment_size,
            growth_rate=growth_rate,
            engagement_level=engagement_level,
            conversion_rate=0.05,  # 5% simulation
            lifetime_value=150.0,  # $150 simulation
            geographic_distribution={'US': 0.4, 'EU': 0.3, 'ASIA': 0.3},
            behavior_patterns={'peak_activity': '20:00', 'preferred_content': 'video'},
            prediction_confidence=0.8
        )
    
    async def _calculate_viral_velocity(self, 
                                      content_id: str,
                                      performance_data: Dict[str, Any]) -> float:
        """Calcule vitesse viral contenu"""
        views = performance_data.get('views', 0)
        shares = performance_data.get('shares', 0)
        time_since_publish = performance_data.get('hours_since_publish', 1)
        
        velocity = (views + shares * 10) / time_since_publish
        return min(velocity / 1000, 100.0)  # Normalisation
    
    async def _predict_performance_peak(self, 
                                      content_id: str,
                                      performance_data: Dict[str, Any]) -> datetime:
        """Prédit pic performance contenu"""
        # Simulation - en production utiliser ML time series
        publish_time = performance_data.get('publish_time', datetime.now())
        viral_velocity = await self._calculate_viral_velocity(content_id, performance_data)
        
        # Prédiction basée sur velocity
        if viral_velocity > 50:
            peak_hours = 2  # Contenu viral rapide
        elif viral_velocity > 20:
            peak_hours = 8  # Croissance normale
        else:
            peak_hours = 24  # Croissance lente
        
        return publish_time + timedelta(hours=peak_hours)
    
    async def _calculate_monetization_potential(self, 
                                              content_id: str,
                                              creator_id: str,
                                              performance_data: Dict[str, Any]) -> float:
        """Calcule potentiel monétisation"""
        engagement_score = performance_data.get('engagement_score', 0)
        views = performance_data.get('views', 0)
        audience_sentiment = performance_data.get('audience_sentiment', 0.5)
        
        # Facteurs monétisation
        monetization_score = (
            engagement_score * 0.4 +
            min(views / 10000, 10) * 0.3 +  # Normalisation vues
            audience_sentiment * 0.3
        )
        
        return min(monetization_score * 10, 100.0)
    
    async def _analyze_content_sentiment(self, 
                                       content_id: str,
                                       performance_data: Dict[str, Any]) -> float:
        """Analyse sentiment audience contenu"""
        # Simulation NLP sentiment analysis
        positive_reactions = performance_data.get('likes', 0)
        negative_reactions = performance_data.get('dislikes', 0)
        comments_sentiment = performance_data.get('comments_sentiment', 0.5)
        
        if positive_reactions + negative_reactions == 0:
            return 0.5
        
        reaction_sentiment = positive_reactions / (positive_reactions + negative_reactions)
        overall_sentiment = (reaction_sentiment + comments_sentiment) / 2
        
        return overall_sentiment
    
    async def _calculate_trending_score(self, 
                                      creator_id: str,
                                      platform: Optional[PlatformType] = None) -> float:
        """Calcule score trending créateur"""
        try:
            metrics = list(self.creator_metrics[creator_id])[-24:]  # 24h
            if not metrics:
                return 0.0
            
            # Filtrage plateforme si spécifiée
            if platform:
                metrics = [m for m in metrics if m.platform == platform]
                if not metrics:
                    return 0.0
            
            # Calcul facteurs trending
            avg_engagement = statistics.mean([m.engagement_rate for m in metrics])
            avg_growth = statistics.mean([m.audience_growth_rate for m in metrics])
            avg_viral = statistics.mean([m.viral_potential for m in metrics])
            
            # Score composite
            trending_score = (
                avg_engagement * 0.4 +
                avg_growth * 0.3 +
                avg_viral * 0.3
            )
            
            return trending_score
            
        except Exception as e:
            logger.error(f"Erreur calcul trending score: {e}")
            return 0.0
    
    def _calculate_growth_trend(self, values: List[float]) -> float:
        """Calcule tendance croissance"""
        if len(values) < 2:
            return 0.0
        
        # Régression linéaire simple
        n = len(values)
        x = list(range(n))
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    async def _predict_audience_growth(self, 
                                     creator_id: str, 
                                     horizon_days: int) -> int:
        """Prédit croissance audience"""
        try:
            metrics = list(self.creator_metrics[creator_id])[-100:]
            if not metrics:
                return 0
            
            current_size = metrics[-1].audience_size
            growth_rates = [m.audience_growth_rate for m in metrics[-30:]]
            avg_growth_rate = statistics.mean(growth_rates) if growth_rates else 0
            
            # Prédiction simple avec facteur décroissance
            daily_growth_rate = avg_growth_rate / 100 / 30  # Conversion mensuel -> quotidien
            decay_factor = 0.95  # Décroissance temporelle
            
            predicted_size = current_size
            for day in range(horizon_days):
                daily_rate = daily_growth_rate * (decay_factor ** day)
                predicted_size += predicted_size * daily_rate
            
            return int(predicted_size)
            
        except Exception as e:
            logger.error(f"Erreur predict audience growth: {e}")
            return 0
    
    async def _predict_revenue_growth(self, 
                                    creator_id: str, 
                                    horizon_days: int) -> float:
        """Prédit croissance revenue"""
        try:
            metrics = list(self.creator_metrics[creator_id])[-30:]
            if not metrics:
                return 0.0
            
            daily_revenues = [m.revenue_24h for m in metrics]
            avg_daily_revenue = statistics.mean(daily_revenues)
            revenue_trend = self._calculate_growth_trend(daily_revenues)
            
            # Prédiction revenue 30 jours
            predicted_30d_revenue = avg_daily_revenue * horizon_days
            trend_adjustment = revenue_trend * horizon_days * avg_daily_revenue
            
            return max(predicted_30d_revenue + trend_adjustment, 0.0)
            
        except Exception as e:
            logger.error(f"Erreur predict revenue growth: {e}")
            return 0.0
    
    async def _identify_growth_risks(self, creator_id: str) -> List[str]:
        """Identifie risques croissance"""
        risks = []
        
        try:
            metrics = list(self.creator_metrics[creator_id])[-30:]
            if not metrics:
                return risks
            
            # Analyse tendances
            engagement_trend = self._calculate_growth_trend([m.engagement_rate for m in metrics])
            growth_trend = self._calculate_growth_trend([m.audience_growth_rate for m in metrics])
            
            if engagement_trend < -0.1:
                risks.append("Declining engagement rate")
            if growth_trend < -0.05:
                risks.append("Slowing audience growth")
            if metrics[-1].collaboration_score < 50:
                risks.append("Low collaboration potential")
            if statistics.mean([m.viral_potential for m in metrics[-7:]]) < 20:
                risks.append("Limited viral reach")
                
        except Exception as e:
            logger.error(f"Erreur identify growth risks: {e}")
        
        return risks
    
    async def _identify_growth_opportunities(self, creator_id: str) -> List[str]:
        """Identifie opportunités croissance"""
        opportunities = []
        
        try:
            metrics = list(self.creator_metrics[creator_id])[-30:]
            if not metrics:
                return opportunities
            
            latest = metrics[-1]
            
            if latest.viral_potential > 70:
                opportunities.append("High viral potential - increase posting frequency")
            if latest.collaboration_score > 80:
                opportunities.append("Strong collaboration profile - seek brand partnerships")
            if latest.engagement_rate > 15:
                opportunities.append("High engagement - consider premium content")
            
            # Analyse audience segments
            audience_insights = self.audience_insights.get(creator_id, [])
            for insight in audience_insights:
                if insight.conversion_rate > 0.1:
                    opportunities.append(f"High converting {insight.segment.value} segment")
                    
        except Exception as e:
            logger.error(f"Erreur identify growth opportunities: {e}")
        
        return opportunities
    
    def _assess_growth_trajectory(self, creator_id: str) -> str:
        """Évalue trajectoire croissance"""
        try:
            metrics = list(self.creator_metrics[creator_id])[-30:]
            if len(metrics) < 10:
                return "insufficient_data"
            
            growth_rates = [m.audience_growth_rate for m in metrics]
            avg_growth = statistics.mean(growth_rates)
            
            if avg_growth > 5:
                return "exponential"
            elif avg_growth > 2:
                return "strong"
            elif avg_growth > 0:
                return "steady"
            elif avg_growth > -2:
                return "declining"
            else:
                return "critical"
                
        except Exception as e:
            logger.error(f"Erreur assess growth trajectory: {e}")
            return "unknown"
    
    async def _identify_blockers(self, creator_id: str) -> List[str]:
        """Identifie blockers créateur"""
        # Simulation - en production analyse plus sophistiquée
        return ["Limited content variety", "Inconsistent posting schedule"]
    
    async def _identify_opportunities(self, creator_id: str) -> List[str]:
        """Identifie opportunités créateur"""
        # Simulation - en production ML recommendations
        return ["Cross-platform expansion", "Collaboration with trending creators"]
    
    async def _get_recommended_actions(self, creator_id: str) -> List[str]:
        """Récupère actions recommandées"""
        # Simulation - en production AI-powered recommendations
        return ["Increase posting frequency", "Engage more with audience comments"]
    
    def _calculate_success_probability(self, metrics: CreatorMetrics) -> float:
        """Calcule probabilité succès"""
        factors = [
            metrics.engagement_rate / 100,
            metrics.collaboration_score / 100,
            metrics.viral_potential / 100,
            min(metrics.audience_growth_rate / 10, 1.0)
        ]
        
        return statistics.mean(factors)


# Factory function pour faciliter l'import
def create_live_creator_analytics(**kwargs) -> LiveCreatorAnalytics:
    """
    Factory function pour créer instance LiveCreatorAnalytics
    
    Returns:
        LiveCreatorAnalytics: Instance configurée
    """
    return LiveCreatorAnalytics(**kwargs)


# Export pour utilisation externe
__all__ = [
    'LiveCreatorAnalytics',
    'CreatorMetrics',
    'AudienceInsight', 
    'ContentPerformance',
    'CreatorJourney',
    'EngagementType',
    'PlatformType', 
    'AudienceSegment',
    'create_live_creator_analytics'
]