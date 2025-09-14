"""
Viral Intelligence Engine - Intelligence artificielle pour optimisation virale
Auteur: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Production

Moteur d'IA pour prédiction et optimisation de la viralité du contenu.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter, deque
import hashlib
import math

class ViralityStage(Enum):
    """Stades de viralité du contenu."""
    DORMANT = "dormant"
    EMERGING = "emerging"
    ACCELERATING = "accelerating"
    VIRAL = "viral"
    PEAK = "peak"
    DECLINING = "declining"
    LEGACY = "legacy"

class ViralTrigger(Enum):
    """Déclencheurs de viralité identifiés."""
    EMOTIONAL_RESONANCE = "emotional_resonance"
    TRENDING_TOPIC = "trending_topic"
    CELEBRITY_INTERACTION = "celebrity_interaction"
    ALGORITHM_BOOST = "algorithm_boost"
    ORGANIC_SHARING = "organic_sharing"
    MEDIA_PICKUP = "media_pickup"
    COMMUNITY_AMPLIFICATION = "community_amplification"

@dataclass
class ViralPrediction:
    """Prédiction de viralité pour un contenu."""
    content_id: str
    viral_potential: float
    predicted_peak_time: datetime
    predicted_peak_reach: int
    viral_triggers: List[ViralTrigger]
    viral_stage: ViralityStage
    amplification_factors: Dict[str, float]
    risk_factors: List[str]
    optimization_recommendations: List[str]
    confidence_score: float
    predicted_lifecycle: Dict[str, Any]

class TrendPredictor:
    """Prédicteur de tendances et patterns viraux."""
    
    def __init__(self):
        self.trend_patterns = defaultdict(list)
        self.viral_markers = {}
        self.trend_velocity_tracker = defaultdict(deque)
        self.hashtag_momentum = defaultdict(list)
        self.viral_content_database = {}
        self.logger = logging.getLogger("TrendPredictor")
        
        self._initialize_viral_markers()
    
    def _initialize_viral_markers(self):
        """Initialise les marqueurs de viralité."""
        self.viral_markers = {
            'engagement_acceleration': {
                'threshold': 0.5,  # 50% d'augmentation par heure
                'weight': 0.25,
                'description': 'Accélération rapide de l\'engagement'
            },
            'sharing_velocity': {
                'threshold': 0.3,  # 30% de shares vs vues
                'weight': 0.3,
                'description': 'Vitesse de partage élevée'
            },
            'cross_platform_spread': {
                'threshold': 3,  # Présent sur 3+ plateformes
                'weight': 0.2,
                'description': 'Propagation cross-platform'
            },
            'influencer_adoption': {
                'threshold': 0.1,  # 10% d\'influenceurs adoptent
                'weight': 0.25,
                'description': 'Adoption par les influenceurs'
            },
            'trend_alignment': {
                'threshold': 0.7,  # Alignement à 70% avec trends
                'weight': 0.15,
                'description': 'Alignement avec tendances actuelles'
            },
            'emotional_intensity': {
                'threshold': 0.8,  # Score émotionnel élevé
                'weight': 0.2,
                'description': 'Intensité émotionnelle forte'
            }
        }
        
        self.logger.info(f"Initialized {len(self.viral_markers)} viral markers")
    
    async def predict_viral_potential(self, content_data: Dict[str, Any], 
                                    real_time_metrics: Optional[Dict[str, Any]] = None) -> float:
        """Prédit le potentiel viral d'un contenu."""
        try:
            viral_score_components = []
            
            # Analyse des marqueurs viraux
            for marker_name, marker_config in self.viral_markers.items():
                marker_score = await self._evaluate_viral_marker(
                    marker_name, marker_config, content_data, real_time_metrics
                )
                weighted_score = marker_score * marker_config['weight']
                viral_score_components.append(weighted_score)
            
            # Score viral brut
            raw_viral_score = sum(viral_score_components)
            
            # Ajustements contextuels
            context_multiplier = await self._calculate_context_multiplier(content_data)
            timing_multiplier = await self._calculate_timing_multiplier(content_data)
            platform_multiplier = await self._calculate_platform_multiplier(content_data)
            
            # Score viral final
            viral_potential = raw_viral_score * context_multiplier * timing_multiplier * platform_multiplier
            viral_potential = min(viral_potential, 1.0)  # Normalisation
            
            # Enregistrement pour apprentissage
            await self._record_viral_prediction(content_data, viral_potential)
            
            return viral_potential
            
        except Exception as e:
            self.logger.error(f"Error predicting viral potential: {str(e)}")
            return 0.3  # Score par défaut conservateur
    
    async def _evaluate_viral_marker(self, marker_name: str, marker_config: Dict[str, Any],
                                   content_data: Dict[str, Any], 
                                   real_time_metrics: Optional[Dict[str, Any]]) -> float:
        """Évalue un marqueur viral spécifique."""
        try:
            if marker_name == 'engagement_acceleration':
                return await self._evaluate_engagement_acceleration(content_data, real_time_metrics)
            elif marker_name == 'sharing_velocity':
                return await self._evaluate_sharing_velocity(content_data, real_time_metrics)
            elif marker_name == 'cross_platform_spread':
                return await self._evaluate_cross_platform_spread(content_data)
            elif marker_name == 'influencer_adoption':
                return await self._evaluate_influencer_adoption(content_data, real_time_metrics)
            elif marker_name == 'trend_alignment':
                return await self._evaluate_trend_alignment(content_data)
            elif marker_name == 'emotional_intensity':
                return await self._evaluate_emotional_intensity(content_data)
            else:
                return 0.5  # Score par défaut
                
        except Exception as e:
            self.logger.error(f"Error evaluating viral marker {marker_name}: {str(e)}")
            return 0.0
    
    async def _evaluate_engagement_acceleration(self, content_data: Dict[str, Any], 
                                              real_time_metrics: Optional[Dict[str, Any]]) -> float:
        """Évalue l'accélération de l'engagement."""
        if not real_time_metrics:
            return 0.5
        
        engagement_history = real_time_metrics.get('engagement_timeline', [])
        
        if len(engagement_history) < 3:
            return 0.5
        
        # Calcul de l'accélération
        recent_growth = []
        for i in range(1, len(engagement_history)):
            if engagement_history[i-1] > 0:
                growth_rate = (engagement_history[i] - engagement_history[i-1]) / engagement_history[i-1]
                recent_growth.append(growth_rate)
        
        if not recent_growth:
            return 0.5
        
        avg_acceleration = np.mean(recent_growth[-3:])  # 3 dernières mesures
        
        # Normalisation et score
        threshold = self.viral_markers['engagement_acceleration']['threshold']
        acceleration_score = min(avg_acceleration / threshold, 1.0) if avg_acceleration > 0 else 0.0
        
        return acceleration_score
    
    async def _evaluate_sharing_velocity(self, content_data: Dict[str, Any], 
                                       real_time_metrics: Optional[Dict[str, Any]]) -> float:
        """Évalue la vitesse de partage."""
        if not real_time_metrics:
            # Estimation basée sur le type de contenu
            content_type = content_data.get('content_type', 'text')
            sharing_base_rates = {
                'video': 0.6,
                'image': 0.4,
                'text': 0.3,
                'audio': 0.5,
                'carousel': 0.5
            }
            return sharing_base_rates.get(content_type, 0.4)
        
        shares = real_time_metrics.get('shares', 0)
        views = real_time_metrics.get('views', 1)
        
        sharing_rate = shares / views
        threshold = self.viral_markers['sharing_velocity']['threshold']
        
        sharing_score = min(sharing_rate / threshold, 1.0)
        return sharing_score
    
    async def _evaluate_cross_platform_spread(self, content_data: Dict[str, Any]) -> float:
        """Évalue la propagation cross-platform."""
        target_platforms = content_data.get('target_platforms', [])
        platform_count = len(target_platforms)
        
        threshold = self.viral_markers['cross_platform_spread']['threshold']
        
        # Score basé sur le nombre de plateformes
        platform_score = min(platform_count / threshold, 1.0)
        
        # Bonus pour la diversité des types de plateformes
        platform_types = set()
        for platform in target_platforms:
            if platform in ['instagram', 'tiktok', 'facebook', 'twitter']:
                platform_types.add('social')
            elif platform in ['youtube', 'vimeo', 'twitch']:
                platform_types.add('video')
            elif platform in ['spotify', 'apple_music', 'soundcloud']:
                platform_types.add('audio')
            elif platform in ['patreon', 'onlyfans', 'ko_fi']:
                platform_types.add('creator_economy')
        
        diversity_bonus = len(platform_types) * 0.1
        
        return min(platform_score + diversity_bonus, 1.0)
    
    async def _evaluate_influencer_adoption(self, content_data: Dict[str, Any], 
                                          real_time_metrics: Optional[Dict[str, Any]]) -> float:
        """Évalue l'adoption par les influenceurs."""
        if not real_time_metrics:
            # Estimation basée sur le créateur
            creator_influence = content_data.get('creator_influence_score', 0.3)
            return creator_influence
        
        influencer_shares = real_time_metrics.get('influencer_shares', 0)
        total_shares = real_time_metrics.get('total_shares', 1)
        
        if total_shares == 0:
            return 0.0
        
        influencer_adoption_rate = influencer_shares / total_shares
        threshold = self.viral_markers['influencer_adoption']['threshold']
        
        adoption_score = min(influencer_adoption_rate / threshold, 1.0)
        return adoption_score
    
    async def _evaluate_trend_alignment(self, content_data: Dict[str, Any]) -> float:
        """Évalue l'alignement avec les tendances actuelles."""
        content_tags = content_data.get('hashtags', [])
        content_topics = content_data.get('topics', [])
        
        # Récupération des tendances actuelles (simulation)
        current_trends = await self._get_current_trends()
        
        if not current_trends:
            return 0.5
        
        # Calcul de l'alignement
        trend_matches = 0
        total_trends = len(current_trends)
        
        for trend in current_trends:
            trend_lower = trend.lower()
            # Vérification dans les hashtags
            for tag in content_tags:
                if trend_lower in tag.lower():
                    trend_matches += 1
                    break
            # Vérification dans les topics
            for topic in content_topics:
                if trend_lower in topic.lower():
                    trend_matches += 1
                    break
        
        alignment_score = trend_matches / total_trends if total_trends > 0 else 0.0
        return min(alignment_score, 1.0)
    
    async def _evaluate_emotional_intensity(self, content_data: Dict[str, Any]) -> float:
        """Évalue l'intensité émotionnelle du contenu."""
        # Score de sentiment
        sentiment_score = content_data.get('sentiment_score', 0.0)
        emotional_intensity = abs(sentiment_score)  # Intensité = valeur absolue
        
        # Facteurs émotionnels additionnels
        emotional_keywords = content_data.get('emotional_keywords', [])
        emotion_boost = min(len(emotional_keywords) / 10, 0.3)  # Max 30% bonus
        
        # Score final d'intensité émotionnelle
        final_intensity = emotional_intensity + emotion_boost
        
        return min(final_intensity, 1.0)
    
    async def _calculate_context_multiplier(self, content_data: Dict[str, Any]) -> float:
        """Calcule le multiplicateur contextuel."""
        context_factors = []
        
        # Facteur de créateur
        creator_followers = content_data.get('creator_followers', 1000)
        creator_factor = min(math.log10(creator_followers) / 6, 1.2)  # Max 20% bonus
        context_factors.append(creator_factor)
        
        # Facteur de qualité
        content_quality = content_data.get('content_quality_score', 0.7)
        context_factors.append(content_quality)
        
        # Facteur de timing (événements spéciaux)
        is_special_event = content_data.get('is_special_event', False)
        event_factor = 1.3 if is_special_event else 1.0
        context_factors.append(event_factor)
        
        return np.mean(context_factors)
    
    async def _calculate_timing_multiplier(self, content_data: Dict[str, Any]) -> float:
        """Calcule le multiplicateur de timing."""
        current_time = datetime.now()
        
        # Facteurs de timing
        timing_factors = []
        
        # Heure de la journée
        hour = current_time.hour
        if hour in [8, 12, 17, 20]:  # Heures de pointe
            timing_factors.append(1.2)
        elif hour in [6, 7, 9, 10, 11, 13, 14, 15, 16, 18, 19, 21, 22]:
            timing_factors.append(1.0)
        else:
            timing_factors.append(0.8)
        
        # Jour de la semaine
        weekday = current_time.weekday()
        if weekday < 5:  # Lundi-Vendredi
            timing_factors.append(1.1)
        else:  # Weekend
            timing_factors.append(0.9)
        
        # Saisonnalité
        month = current_time.month
        if month in [11, 12, 1]:  # Période de fêtes
            timing_factors.append(1.15)
        elif month in [6, 7, 8]:  # Été
            timing_factors.append(1.05)
        else:
            timing_factors.append(1.0)
        
        return np.mean(timing_factors)
    
    async def _calculate_platform_multiplier(self, content_data: Dict[str, Any]) -> float:
        """Calcule le multiplicateur de plateforme."""
        target_platforms = content_data.get('target_platforms', [])
        
        # Facteurs viraux par plateforme
        platform_viral_factors = {
            'tiktok': 1.3,
            'twitter': 1.2,
            'instagram': 1.1,
            'youtube': 1.0,
            'facebook': 0.9,
            'linkedin': 0.7,
            'reddit': 1.25,
            'discord': 1.15
        }
        
        if not target_platforms:
            return 1.0
        
        platform_scores = []
        for platform in target_platforms:
            factor = platform_viral_factors.get(platform, 1.0)
            platform_scores.append(factor)
        
        return np.mean(platform_scores)
    
    async def _get_current_trends(self) -> List[str]:
        """Récupère les tendances actuelles (simulation)."""
        # Simulation de tendances actuelles
        current_trends = [
            'ai', 'sustainability', 'mental_health', 'creator_economy',
            'remote_work', 'blockchain', 'wellness', 'education',
            'gaming', 'music', 'art', 'technology', 'food', 'travel'
        ]
        
        # Retourne un sous-ensemble aléatoire pour simulation
        import random
        return random.sample(current_trends, k=min(8, len(current_trends)))
    
    async def _record_viral_prediction(self, content_data: Dict[str, Any], viral_potential: float):
        """Enregistre la prédiction pour améliorer le modèle."""
        content_id = content_data.get('content_id', 'unknown')
        
        self.viral_content_database[content_id] = {
            'predicted_viral_potential': viral_potential,
            'prediction_timestamp': datetime.now(),
            'content_features': content_data.copy()
        }
    
    async def analyze_trend_velocity(self, trend_topic: str, 
                                   data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse la vélocité d'une tendance."""
        try:
            if len(data_points) < 2:
                return {'velocity': 0.0, 'stage': 'insufficient_data'}
            
            # Calcul de la vélocité
            timestamps = [point['timestamp'] for point in data_points]
            mentions = [point['mention_count'] for point in data_points]
            
            # Calcul de la dérivée (changement de mentions)
            velocities = []
            for i in range(1, len(mentions)):
                time_diff = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # heures
                mention_diff = mentions[i] - mentions[i-1]
                if time_diff > 0:
                    velocity = mention_diff / time_diff
                    velocities.append(velocity)
            
            if not velocities:
                return {'velocity': 0.0, 'stage': 'no_change'}
            
            avg_velocity = np.mean(velocities)
            recent_velocity = np.mean(velocities[-3:]) if len(velocities) >= 3 else avg_velocity
            
            # Classification du stade de tendance
            stage = await self._classify_trend_stage(avg_velocity, recent_velocity, mentions)
            
            # Prédiction de pic
            predicted_peak = await self._predict_trend_peak(trend_topic, velocities, mentions)
            
            return {
                'trend_topic': trend_topic,
                'average_velocity': avg_velocity,
                'recent_velocity': recent_velocity,
                'trend_stage': stage,
                'predicted_peak': predicted_peak,
                'momentum_score': min(recent_velocity / 100, 1.0),  # Normalisation
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend velocity for {trend_topic}: {str(e)}")
            return {'error': str(e)}
    
    async def _classify_trend_stage(self, avg_velocity: float, recent_velocity: float, 
                                  mentions: List[int]) -> str:
        """Classifie le stade d'une tendance."""
        current_mentions = mentions[-1] if mentions else 0
        peak_mentions = max(mentions) if mentions else 0
        
        # Classification basée sur la vélocité et le volume
        if recent_velocity > avg_velocity * 2 and recent_velocity > 50:
            return 'accelerating'
        elif recent_velocity > 100 and current_mentions > peak_mentions * 0.8:
            return 'viral'
        elif recent_velocity < 0 and current_mentions < peak_mentions * 0.6:
            return 'declining'
        elif recent_velocity > 0 and recent_velocity < 20:
            return 'emerging'
        elif current_mentions > peak_mentions * 0.9:
            return 'peak'
        else:
            return 'stable'
    
    async def _predict_trend_peak(self, trend_topic: str, velocities: List[float], 
                                mentions: List[int]) -> Dict[str, Any]:
        """Prédit le pic d'une tendance."""
        if len(velocities) < 3:
            return {'predicted_time': None, 'confidence': 0.0}
        
        # Analyse de la tendance de vélocité
        velocity_trend = np.polyfit(range(len(velocities)), velocities, 1)[0]
        
        # Prédiction simple basée sur la tendance
        if velocity_trend > 0:
            # Tendance croissante - pic dans le futur
            hours_to_peak = abs(velocities[-1] / velocity_trend) if velocity_trend != 0 else 24
            hours_to_peak = min(hours_to_peak, 168)  # Max 1 semaine
            predicted_time = datetime.now() + timedelta(hours=hours_to_peak)
            confidence = 0.7
        elif velocity_trend < 0:
            # Tendance décroissante - pic probablement passé
            predicted_time = datetime.now() - timedelta(hours=12)
            confidence = 0.5
        else:
            # Tendance stable
            predicted_time = datetime.now() + timedelta(hours=24)
            confidence = 0.3
        
        return {
            'predicted_time': predicted_time.isoformat(),
            'confidence': confidence,
            'reasoning': f"Velocity trend: {velocity_trend:.2f}"
        }

class ViralIntelligenceEngine:
    """Moteur d'intelligence virale pour optimisation de contenu viral."""
    
    def __init__(self):
        self.trend_predictor = TrendPredictor()
        self.viral_patterns = defaultdict(list)
        self.content_lifecycle_tracker = {}
        self.viral_amplifiers = {}
        self.real_time_viral_monitor = {}
        self.logger = logging.getLogger("ViralIntelligenceEngine")
        
        self._initialize_viral_amplifiers()
    
    def _initialize_viral_amplifiers(self):
        """Initialise les amplificateurs viraux."""
        self.viral_amplifiers = {
            'hashtag_optimization': {
                'trending_hashtags': 0.3,
                'niche_hashtags': 0.2,
                'branded_hashtags': 0.1,
                'community_hashtags': 0.25
            },
            'timing_optimization': {
                'peak_hours': 0.4,
                'timezone_optimization': 0.3,
                'event_timing': 0.3
            },
            'content_optimization': {
                'emotional_hooks': 0.35,
                'visual_appeal': 0.3,
                'storytelling': 0.25,
                'call_to_action': 0.1
            },
            'network_effects': {
                'influencer_seeding': 0.4,
                'community_engagement': 0.3,
                'cross_platform_sync': 0.3
            },
            'algorithmic_optimization': {
                'engagement_velocity': 0.4,
                'completion_rate': 0.3,
                'sharing_rate': 0.3
            }
        }
        
        self.logger.info(f"Initialized {len(self.viral_amplifiers)} viral amplification strategies")
    
    async def analyze_viral_potential(self, content_id: str, content_data: Dict[str, Any], 
                                    real_time_metrics: Optional[Dict[str, Any]] = None) -> ViralPrediction:
        """Analyse complète du potentiel viral d'un contenu."""
        try:
            self.logger.info(f"Analyzing viral potential for content {content_id}")
            
            # Prédiction de base
            viral_potential = await self.trend_predictor.predict_viral_potential(content_data, real_time_metrics)
            
            # Classification du stade viral
            viral_stage = await self._determine_viral_stage(content_data, real_time_metrics, viral_potential)
            
            # Identification des déclencheurs viraux
            viral_triggers = await self._identify_viral_triggers(content_data, real_time_metrics)
            
            # Calcul des facteurs d'amplification
            amplification_factors = await self._calculate_amplification_factors(content_data)
            
            # Identification des facteurs de risque
            risk_factors = await self._identify_risk_factors(content_data, viral_potential)
            
            # Prédiction de timing de pic
            predicted_peak_time = await self._predict_peak_timing(content_data, viral_potential)
            
            # Prédiction de portée de pic
            predicted_peak_reach = await self._predict_peak_reach(content_data, viral_potential)
            
            # Génération de recommandations
            optimization_recommendations = await self._generate_viral_optimization_recommendations(
                content_data, viral_potential, amplification_factors
            )
            
            # Calcul de confiance
            confidence_score = await self._calculate_viral_confidence(content_data, real_time_metrics)
            
            # Prédiction du cycle de vie
            predicted_lifecycle = await self._predict_viral_lifecycle(content_data, viral_potential)
            
            prediction = ViralPrediction(
                content_id=content_id,
                viral_potential=viral_potential,
                predicted_peak_time=predicted_peak_time,
                predicted_peak_reach=predicted_peak_reach,
                viral_triggers=viral_triggers,
                viral_stage=viral_stage,
                amplification_factors=amplification_factors,
                risk_factors=risk_factors,
                optimization_recommendations=optimization_recommendations,
                confidence_score=confidence_score,
                predicted_lifecycle=predicted_lifecycle
            )
            
            # Enregistrement pour suivi
            self.content_lifecycle_tracker[content_id] = {
                'prediction': prediction,
                'created_at': datetime.now(),
                'real_time_data': []
            }
            
            self.logger.info(f"Viral analysis completed for {content_id}")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error analyzing viral potential: {str(e)}")
            raise
    
    async def _determine_viral_stage(self, content_data: Dict[str, Any], 
                                   real_time_metrics: Optional[Dict[str, Any]], 
                                   viral_potential: float) -> ViralityStage:
        """Détermine le stade viral actuel du contenu."""
        if not real_time_metrics:
            # Sans métriques temps réel, base sur le potentiel
            if viral_potential > 0.8:
                return ViralityStage.EMERGING
            else:
                return ViralityStage.DORMANT
        
        views = real_time_metrics.get('views', 0)
        engagement_rate = real_time_metrics.get('engagement_rate', 0)
        sharing_rate = real_time_metrics.get('sharing_rate', 0)
        growth_rate = real_time_metrics.get('growth_rate', 0)
        
        # Classification basée sur les métriques
        if views > 1000000 and engagement_rate > 0.1 and sharing_rate > 0.3:
            return ViralityStage.VIRAL
        elif views > 500000 and growth_rate > 2.0:
            return ViralityStage.ACCELERATING
        elif views > 100000 and engagement_rate > 0.05:
            return ViralityStage.EMERGING
        elif views > 10000000 and growth_rate < 0.5:
            return ViralityStage.PEAK
        elif growth_rate < -0.2:
            return ViralityStage.DECLINING
        else:
            return ViralityStage.DORMANT
    
    async def _identify_viral_triggers(self, content_data: Dict[str, Any], 
                                     real_time_metrics: Optional[Dict[str, Any]]) -> List[ViralTrigger]:
        """Identifie les déclencheurs viraux actifs."""
        triggers = []
        
        # Vérification de la résonance émotionnelle
        sentiment_intensity = abs(content_data.get('sentiment_score', 0))
        if sentiment_intensity > 0.7:
            triggers.append(ViralTrigger.EMOTIONAL_RESONANCE)
        
        # Vérification de l'alignement avec les tendances
        hashtags = content_data.get('hashtags', [])
        trending_hashtags = content_data.get('trending_hashtags', [])
        
        hashtag_overlap = len(set(hashtags).intersection(set(trending_hashtags)))
        if hashtag_overlap > 0:
            triggers.append(ViralTrigger.TRENDING_TOPIC)
        
        # Vérification de l'interaction de célébrités (simulation)
        if real_time_metrics:
            celebrity_interactions = real_time_metrics.get('celebrity_interactions', 0)
            if celebrity_interactions > 0:
                triggers.append(ViralTrigger.CELEBRITY_INTERACTION)
            
            # Vérification du boost algorithmique
            algorithm_boost_score = real_time_metrics.get('algorithm_boost_score', 0)
            if algorithm_boost_score > 0.7:
                triggers.append(ViralTrigger.ALGORITHM_BOOST)
            
            # Vérification du partage organique
            organic_share_ratio = real_time_metrics.get('organic_share_ratio', 0.5)
            if organic_share_ratio > 0.8:
                triggers.append(ViralTrigger.ORGANIC_SHARING)
        
        # Vérification de la couverture médiatique
        media_mentions = content_data.get('media_mentions', 0)
        if media_mentions > 0:
            triggers.append(ViralTrigger.MEDIA_PICKUP)
        
        # Vérification de l'amplification communautaire
        community_shares = content_data.get('community_shares', 0)
        total_shares = content_data.get('total_shares', 1)
        
        if community_shares / total_shares > 0.3:
            triggers.append(ViralTrigger.COMMUNITY_AMPLIFICATION)
        
        return triggers
    
    async def _calculate_amplification_factors(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Calcule les facteurs d'amplification disponibles."""
        amplification_scores = {}
        
        for amplifier_category, factors in self.viral_amplifiers.items():
            category_score = 0
            
            if amplifier_category == 'hashtag_optimization':
                hashtag_count = len(content_data.get('hashtags', []))
                trending_hashtag_count = len(content_data.get('trending_hashtags', []))
                
                category_score = (
                    (hashtag_count / 10) * factors['niche_hashtags'] +
                    (trending_hashtag_count / 5) * factors['trending_hashtags']
                )
            
            elif amplifier_category == 'timing_optimization':
                is_peak_time = content_data.get('is_peak_time', False)
                is_special_event = content_data.get('is_special_event', False)
                
                if is_peak_time:
                    category_score += factors['peak_hours']
                if is_special_event:
                    category_score += factors['event_timing']
                
                category_score += factors['timezone_optimization'] * 0.5  # Score par défaut
            
            elif amplifier_category == 'content_optimization':
                emotional_score = abs(content_data.get('sentiment_score', 0))
                visual_quality = content_data.get('visual_quality_score', 0.7)
                has_cta = content_data.get('has_call_to_action', False)
                
                category_score = (
                    emotional_score * factors['emotional_hooks'] +
                    visual_quality * factors['visual_appeal'] +
                    (1.0 if has_cta else 0.0) * factors['call_to_action']
                )
            
            elif amplifier_category == 'network_effects':
                creator_influence = content_data.get('creator_influence_score', 0.3)
                community_size = content_data.get('community_size', 0)
                platform_count = len(content_data.get('target_platforms', []))
                
                category_score = (
                    creator_influence * factors['influencer_seeding'] +
                    min(community_size / 10000, 1.0) * factors['community_engagement'] +
                    min(platform_count / 8, 1.0) * factors['cross_platform_sync']
                )
            
            elif amplifier_category == 'algorithmic_optimization':
                content_quality = content_data.get('content_quality_score', 0.7)
                estimated_completion = content_data.get('estimated_completion_rate', 0.6)
                estimated_sharing = content_data.get('estimated_sharing_rate', 0.1)
                
                category_score = (
                    content_quality * factors['engagement_velocity'] +
                    estimated_completion * factors['completion_rate'] +
                    estimated_sharing * factors['sharing_rate']
                )
            
            amplification_scores[amplifier_category] = min(category_score, 1.0)
        
        return amplification_scores
    
    async def _identify_risk_factors(self, content_data: Dict[str, Any], 
                                   viral_potential: float) -> List[str]:
        """Identifie les facteurs de risque pour la viralité."""
        risk_factors = []
        
        # Risque de contenu inapproprié
        content_safety_score = content_data.get('content_safety_score', 0.8)
        if content_safety_score < 0.7:
            risk_factors.append("Contenu potentiellement inapproprié")
        
        # Risque de saturation de hashtags
        hashtag_count = len(content_data.get('hashtags', []))
        if hashtag_count > 15:
            risk_factors.append("Trop de hashtags - risque de spam")
        
        # Risque de timing sous-optimal
        is_peak_time = content_data.get('is_peak_time', True)
        if not is_peak_time:
            risk_factors.append("Timing de publication non optimal")
        
        # Risque de qualité insuffisante
        content_quality = content_data.get('content_quality_score', 0.7)
        if content_quality < 0.6:
            risk_factors.append("Qualité de contenu insuffisante")
        
        # Risque de sur-promotion
        promotional_content_ratio = content_data.get('promotional_ratio', 0.2)
        if promotional_content_ratio > 0.5:
            risk_factors.append("Contenu trop promotionnel")
        
        # Risque de faible engagement initial
        estimated_initial_engagement = content_data.get('estimated_initial_engagement', 0.03)
        if estimated_initial_engagement < 0.02:
            risk_factors.append("Engagement initial prédit faible")
        
        # Risque de concurrence élevée
        content_competition_score = content_data.get('competition_score', 0.5)
        if content_competition_score > 0.8:
            risk_factors.append("Concurrence élevée sur le sujet")
        
        return risk_factors
    
    async def _predict_peak_timing(self, content_data: Dict[str, Any], 
                                 viral_potential: float) -> datetime:
        """Prédit le timing du pic viral."""
        current_time = datetime.now()
        
        # Facteurs influençant le timing de pic
        content_type = content_data.get('content_type', 'text')
        platform_count = len(content_data.get('target_platforms', []))
        creator_influence = content_data.get('creator_influence_score', 0.3)
        
        # Estimation de base selon le type de contenu
        base_hours_to_peak = {
            'video': 6,
            'image': 4,
            'text': 3,
            'audio': 8,
            'carousel': 5
        }
        
        hours_to_peak = base_hours_to_peak.get(content_type, 4)
        
        # Ajustements basés sur le potentiel viral
        if viral_potential > 0.8:
            hours_to_peak *= 0.7  # Pic plus rapide pour contenu très viral
        elif viral_potential < 0.3:
            hours_to_peak *= 1.5  # Pic plus lent pour contenu moins viral
        
        # Ajustements basés sur l'influence du créateur
        if creator_influence > 0.7:
            hours_to_peak *= 0.8  # Créateurs influents atteignent le pic plus vite
        
        # Ajustements basés sur la distribution multi-plateforme
        if platform_count > 5:
            hours_to_peak *= 1.2  # Plus de plateformes = propagation plus lente mais plus durable
        
        # Ajout de variabilité réaliste
        import random
        variation = random.uniform(0.8, 1.2)
        hours_to_peak *= variation
        
        predicted_peak_time = current_time + timedelta(hours=hours_to_peak)
        return predicted_peak_time
    
    async def _predict_peak_reach(self, content_data: Dict[str, Any], viral_potential: float) -> int:
        """Prédit la portée maximale du contenu."""
        # Base de followers du créateur
        creator_followers = content_data.get('creator_followers', 1000)
        
        # Facteur de viralité
        viral_multiplier = 1 + (viral_potential * 50)  # Jusqu'à 51x pour contenu très viral
        
        # Facteur de plateforme
        platform_count = len(content_data.get('target_platforms', []))
        platform_multiplier = 1 + (platform_count * 0.5)
        
        # Facteur de qualité
        content_quality = content_data.get('content_quality_score', 0.7)
        quality_multiplier = 0.5 + content_quality
        
        # Facteur de tendance
        trend_alignment = content_data.get('trend_alignment_score', 0.5)
        trend_multiplier = 1 + (trend_alignment * 0.5)
        
        # Calcul de la portée prédite
        predicted_reach = int(
            creator_followers * viral_multiplier * platform_multiplier * 
            quality_multiplier * trend_multiplier
        )
        
        # Limites réalistes
        predicted_reach = min(predicted_reach, 100000000)  # Max 100M
        predicted_reach = max(predicted_reach, creator_followers)  # Min followers existants
        
        return predicted_reach
    
    async def _generate_viral_optimization_recommendations(self, content_data: Dict[str, Any],
                                                         viral_potential: float,
                                                         amplification_factors: Dict[str, float]) -> List[str]:
        """Génère des recommandations pour optimiser la viralité."""
        recommendations = []
        
        # Recommandations basées sur le potentiel viral
        if viral_potential < 0.5:
            recommendations.append("Augmenter l'impact émotionnel du contenu")
            recommendations.append("Aligner avec les tendances actuelles")
        elif viral_potential > 0.8:
            recommendations.append("Préparer une stratégie de gestion de l'afflux massif")
            recommendations.append("Optimiser pour la durabilité de l'engagement")
        
        # Recommandations basées sur les facteurs d'amplification
        for factor_category, score in amplification_factors.items():
            if score < 0.5:
                if factor_category == 'hashtag_optimization':
                    recommendations.append("Ajouter des hashtags trending pertinents")
                elif factor_category == 'timing_optimization':
                    recommendations.append("Reprogrammer aux heures de pointe")
                elif factor_category == 'content_optimization':
                    recommendations.append("Améliorer les hooks émotionnels")
                elif factor_category == 'network_effects':
                    recommendations.append("Engager les influenceurs et communautés")
                elif factor_category == 'algorithmic_optimization':
                    recommendations.append("Optimiser pour l'engagement des premières heures")
        
        # Recommandations spécifiques au contenu
        content_type = content_data.get('content_type', 'text')
        if content_type == 'video':
            recommendations.append("Optimiser les 3 premières secondes")
            recommendations.append("Ajouter des sous-titres pour l'accessibilité")
        elif content_type == 'image':
            recommendations.append("Optimiser la qualité visuelle")
            recommendations.append("Ajouter des éléments textuels accrocheurs")
        
        # Recommandations de timing
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 23:
            recommendations.append("Attendre une heure plus favorable (6h-23h)")
        
        return recommendations[:8]  # Limite à 8 recommandations
    
    async def _calculate_viral_confidence(self, content_data: Dict[str, Any], 
                                        real_time_metrics: Optional[Dict[str, Any]]) -> float:
        """Calcule la confiance dans la prédiction virale."""
        confidence_factors = []
        
        # Facteur de données historiques
        creator_track_record = content_data.get('creator_viral_history_score', 0.5)
        confidence_factors.append(creator_track_record)
        
        # Facteur de données temps réel
        if real_time_metrics:
            data_completeness = len(real_time_metrics) / 10  # Suppose 10 métriques idéales
            confidence_factors.append(min(data_completeness, 1.0))
        else:
            confidence_factors.append(0.4)  # Confiance réduite sans données temps réel
        
        # Facteur de qualité du contenu
        content_quality = content_data.get('content_quality_score', 0.7)
        confidence_factors.append(content_quality)
        
        # Facteur de complétude des métadonnées
        required_fields = ['content_type', 'hashtags', 'sentiment_score', 'target_platforms']
        completeness = sum(1 for field in required_fields if field in content_data) / len(required_fields)
        confidence_factors.append(completeness)
        
        return np.mean(confidence_factors)
    
    async def _predict_viral_lifecycle(self, content_data: Dict[str, Any], 
                                     viral_potential: float) -> Dict[str, Any]:
        """Prédit le cycle de vie viral du contenu."""
        current_time = datetime.now()
        
        # Phases du cycle de vie viral
        lifecycle_phases = {}
        
        # Phase d'émergence (0-6h)
        emergence_end = current_time + timedelta(hours=6)
        lifecycle_phases['emergence'] = {
            'start_time': current_time.isoformat(),
            'end_time': emergence_end.isoformat(),
            'expected_reach_percentage': 10,
            'key_activities': ['Engagement initial', 'Partage par early adopters']
        }
        
        # Phase d'accélération (6-24h)
        acceleration_end = current_time + timedelta(hours=24)
        lifecycle_phases['acceleration'] = {
            'start_time': emergence_end.isoformat(),
            'end_time': acceleration_end.isoformat(),
            'expected_reach_percentage': 60,
            'key_activities': ['Amplification algorithmique', 'Partage viral']
        }
        
        # Phase de pic (24-48h)
        peak_duration = 24 if viral_potential > 0.7 else 12
        peak_end = acceleration_end + timedelta(hours=peak_duration)
        lifecycle_phases['peak'] = {
            'start_time': acceleration_end.isoformat(),
            'end_time': peak_end.isoformat(),
            'expected_reach_percentage': 100,
            'key_activities': ['Pic d\'engagement', 'Couverture médiatique potentielle']
        }
        
        # Phase de déclin (48h+)
        decline_end = peak_end + timedelta(days=3)
        lifecycle_phases['decline'] = {
            'start_time': peak_end.isoformat(),
            'end_time': decline_end.isoformat(),
            'expected_reach_percentage': 20,
            'key_activities': ['Engagement résiduel', 'Partage delayed']
        }
        
        # Phase legacy (après déclin)
        lifecycle_phases['legacy'] = {
            'start_time': decline_end.isoformat(),
            'end_time': None,
            'expected_reach_percentage': 5,
            'key_activities': ['Découverte organique', 'Référencement long terme']
        }
        
        return {
            'lifecycle_phases': lifecycle_phases,
            'total_predicted_duration_hours': 168,  # 1 semaine
            'peak_phase_duration_hours': peak_duration,
            'viral_sustainability_score': viral_potential * 0.8  # Potentiel de durabilité
        }
    
    async def monitor_viral_performance(self, content_id: str, 
                                      real_time_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Monitore la performance virale en temps réel."""
        try:
            if content_id not in self.content_lifecycle_tracker:
                return {'error': 'Content not found in tracking system'}
            
            tracking_data = self.content_lifecycle_tracker[content_id]
            original_prediction = tracking_data['prediction']
            
            # Mise à jour des données temps réel
            tracking_data['real_time_data'].append({
                'timestamp': datetime.now(),
                'metrics': real_time_metrics.copy()
            })
            
            # Analyse de l'écart entre prédiction et réalité
            performance_analysis = await self._analyze_prediction_accuracy(
                original_prediction, real_time_metrics
            )
            
            # Mise à jour du stade viral
            current_stage = await self._determine_viral_stage(
                {}, real_time_metrics, original_prediction.viral_potential
            )
            
            # Détection d'alertes
            alerts = await self._generate_viral_alerts(content_id, real_time_metrics, original_prediction)
            
            # Recommandations d'ajustement
            adjustment_recommendations = await self._generate_real_time_adjustments(
                real_time_metrics, original_prediction
            )
            
            return {
                'content_id': content_id,
                'current_viral_stage': current_stage.value,
                'performance_vs_prediction': performance_analysis,
                'viral_alerts': alerts,
                'adjustment_recommendations': adjustment_recommendations,
                'monitoring_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring viral performance: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_prediction_accuracy(self, original_prediction: ViralPrediction,
                                         real_time_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse la précision de la prédiction originale."""
        current_reach = real_time_metrics.get('reach', 0)
        current_engagement = real_time_metrics.get('engagement_rate', 0)
        
        # Comparaison avec les prédictions
        predicted_reach = original_prediction.predicted_peak_reach
        predicted_viral_potential = original_prediction.viral_potential
        
        # Calcul des écarts
        reach_accuracy = 1.0 - abs(current_reach - predicted_reach) / max(predicted_reach, 1)
        reach_accuracy = max(0, reach_accuracy)
        
        # Estimation de l'engagement prédit (simulation)
        predicted_engagement = predicted_viral_potential * 0.1  # Estimation simple
        engagement_accuracy = 1.0 - abs(current_engagement - predicted_engagement) / max(predicted_engagement, 0.01)
        engagement_accuracy = max(0, engagement_accuracy)
        
        overall_accuracy = (reach_accuracy + engagement_accuracy) / 2
        
        return {
            'overall_accuracy': overall_accuracy,
            'reach_accuracy': reach_accuracy,
            'engagement_accuracy': engagement_accuracy,
            'predicted_vs_actual': {
                'reach': {'predicted': predicted_reach, 'actual': current_reach},
                'engagement': {'predicted': predicted_engagement, 'actual': current_engagement}
            }
        }
    
    async def _generate_viral_alerts(self, content_id: str, real_time_metrics: Dict[str, Any],
                                   original_prediction: ViralPrediction) -> List[Dict[str, Any]]:
        """Génère des alertes basées sur la performance virale."""
        alerts = []
        
        current_reach = real_time_metrics.get('reach', 0)
        engagement_rate = real_time_metrics.get('engagement_rate', 0)
        sharing_rate = real_time_metrics.get('sharing_rate', 0)
        
        # Alerte performance exceptionnelle
        if current_reach > original_prediction.predicted_peak_reach * 1.5:
            alerts.append({
                'type': 'exceptional_performance',
                'priority': 'high',
                'message': f"Performance dépassant les prédictions de 50%+",
                'action_required': 'Préparer scaling infrastructure'
            })
        
        # Alerte début de viralité
        if engagement_rate > 0.08 and sharing_rate > 0.2:
            alerts.append({
                'type': 'viral_emergence',
                'priority': 'medium',
                'message': "Signes de début de viralité détectés",
                'action_required': 'Surveiller et amplifier'
            })
        
        # Alerte performance sous-optimale
        predicted_engagement = original_prediction.viral_potential * 0.1
        if engagement_rate < predicted_engagement * 0.5:
            alerts.append({
                'type': 'underperformance',
                'priority': 'medium',
                'message': "Performance en dessous des prédictions",
                'action_required': 'Réviser stratégie de distribution'
            })
        
        # Alerte pic potentiel
        time_since_publication = datetime.now() - datetime.fromisoformat(
            original_prediction.predicted_peak_time.replace('Z', '+00:00')
        )
        
        if abs(time_since_publication.total_seconds()) < 3600:  # Dans l'heure du pic prédit
            alerts.append({
                'type': 'peak_window',
                'priority': 'high',
                'message': "Approche de la fenêtre de pic prédite",
                'action_required': 'Maximiser amplification'
            })
        
        return alerts
    
    async def _generate_real_time_adjustments(self, real_time_metrics: Dict[str, Any],
                                            original_prediction: ViralPrediction) -> List[str]:
        """Génère des recommandations d'ajustement en temps réel."""
        adjustments = []
        
        engagement_rate = real_time_metrics.get('engagement_rate', 0)
        sharing_rate = real_time_metrics.get('sharing_rate', 0)
        completion_rate = real_time_metrics.get('completion_rate', 0.7)
        
        # Ajustements basés sur l'engagement
        if engagement_rate < 0.02:
            adjustments.append("Booster avec engagement payant initial")
            adjustments.append("Réviser le hook d'ouverture")
        elif engagement_rate > 0.08:
            adjustments.append("Préparer contenu de suivi pour capitaliser")
            adjustments.append("Augmenter fréquence de monitoring")
        
        # Ajustements basés sur le partage
        if sharing_rate < 0.05:
            adjustments.append("Ajouter call-to-action pour le partage")
            adjustments.append("Optimiser pour la découvrabilité")
        elif sharing_rate > 0.3:
            adjustments.append("Surveiller la qualité des partages")
            adjustments.append("Préparer gestion de crise si nécessaire")
        
        # Ajustements basés sur la completion
        if completion_rate < 0.5:
            adjustments.append("Analyser les points de drop-off")
            adjustments.append("Optimiser la rétention du contenu")
        
        # Ajustements temporels
        current_hour = datetime.now().hour
        if current_hour in [2, 3, 4, 5]:
            adjustments.append("Considérer re-boost aux heures de pointe")
        
        return adjustments[:5]  # Limite à 5 ajustements prioritaires
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du moteur d'intelligence virale."""
        total_predictions = len(self.content_lifecycle_tracker)
        
        if total_predictions > 0:
            avg_viral_potential = np.mean([
                tracking['prediction'].viral_potential 
                for tracking in self.content_lifecycle_tracker.values()
            ])
            
            stage_distribution = Counter([
                tracking['prediction'].viral_stage.value 
                for tracking in self.content_lifecycle_tracker.values()
            ])
        else:
            avg_viral_potential = 0.0
            stage_distribution = {}
        
        return {
            'total_predictions': total_predictions,
            'average_viral_potential': avg_viral_potential,
            'viral_stage_distribution': dict(stage_distribution),
            'viral_markers_count': len(self.trend_predictor.viral_markers),
            'amplification_strategies': len(self.viral_amplifiers),
            'engine_status': 'operational'
        }