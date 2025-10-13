"""
Audience Intelligence Engine - Intelligence artificielle pour analyse d'audience
Auteur: Fahed Mlaiel (mlaiel@live.de)  
Version: 1.0 Production

Moteur d'IA pour profilage avancé d'audience et prédiction comportementale.
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
from collections import defaultdict, Counter
import hashlib

class AudienceSegment(Enum):
    """Segments d'audience principaux."""
    CREATOR = "creator"
    CONSUMER = "consumer"
    INFLUENCER = "influencer"
    BRAND = "brand"
    COMMUNITY = "community"

class BehaviorPattern(Enum):
    """Patterns comportementaux identifiés."""
    EARLY_ADOPTER = "early_adopter"
    TRENDSETTER = "trendsetter"
    FOLLOWER = "follower"
    LURKER = "lurker"
    ACTIVIST = "activist"
    CASUAL = "casual"

@dataclass
class AudienceProfile:
    """Profil d'audience détaillé."""
    audience_id: str
    segment: AudienceSegment
    behavior_pattern: BehaviorPattern
    demographics: Dict[str, Any]
    interests: List[str]
    platform_preferences: Dict[str, float]
    engagement_patterns: Dict[str, Any]
    content_preferences: Dict[str, float]
    optimal_timing: List[str]
    influence_score: float
    loyalty_score: float
    conversion_likelihood: float
    created_at: datetime
    last_updated: datetime

class BehaviorPredictor:
    """Prédicteur de comportement d'audience basé sur l'IA."""
    
    def __init__(self):
        self.behavior_models = {}
        self.engagement_patterns = defaultdict(list)
        self.conversion_data = defaultdict(list)
        self.logger = logging.getLogger("BehaviorPredictor")
        
        self._initialize_behavior_models()
    
    def _initialize_behavior_models(self):
        """Initialise les modèles de prédiction comportementale."""
        self.logger.info("Initializing audience behavior prediction models...")
        
        # Modèles par type de comportement
        self.behavior_models = {
            BehaviorPattern.EARLY_ADOPTER: {
                'engagement_threshold': 0.08,
                'content_novelty_preference': 0.9,
                'platform_adoption_speed': 0.9,
                'sharing_propensity': 0.8,
                'conversion_rate': 0.15
            },
            BehaviorPattern.TRENDSETTER: {
                'engagement_threshold': 0.12,
                'content_novelty_preference': 0.95,
                'platform_adoption_speed': 0.95,
                'sharing_propensity': 0.9,
                'conversion_rate': 0.2
            },
            BehaviorPattern.FOLLOWER: {
                'engagement_threshold': 0.04,
                'content_novelty_preference': 0.3,
                'platform_adoption_speed': 0.4,
                'sharing_propensity': 0.5,
                'conversion_rate': 0.08
            },
            BehaviorPattern.LURKER: {
                'engagement_threshold': 0.01,
                'content_novelty_preference': 0.6,
                'platform_adoption_speed': 0.2,
                'sharing_propensity': 0.1,
                'conversion_rate': 0.03
            },
            BehaviorPattern.ACTIVIST: {
                'engagement_threshold': 0.15,
                'content_novelty_preference': 0.7,
                'platform_adoption_speed': 0.6,
                'sharing_propensity': 0.95,
                'conversion_rate': 0.25
            },
            BehaviorPattern.CASUAL: {
                'engagement_threshold': 0.03,
                'content_novelty_preference': 0.5,
                'platform_adoption_speed': 0.3,
                'sharing_propensity': 0.3,
                'conversion_rate': 0.05
            }
        }
        
        self.logger.info(f"Initialized {len(self.behavior_models)} behavior prediction models")
    
    async def predict_engagement_behavior(self, audience_data: Dict[str, Any], 
                                        content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prédit le comportement d'engagement pour une audience donnée."""
        try:
            # Classification du pattern comportemental
            behavior_pattern = await self._classify_behavior_pattern(audience_data)
            
            # Modèle correspondant
            model = self.behavior_models.get(behavior_pattern, self.behavior_models[BehaviorPattern.CASUAL])
            
            # Prédiction d'engagement
            base_engagement = model['engagement_threshold']
            
            # Facteurs d'ajustement
            content_novelty = content_data.get('novelty_score', 0.5)
            novelty_bonus = content_novelty * model['content_novelty_preference'] * 0.3
            
            platform_match = audience_data.get('platform_affinity', 0.7)
            platform_bonus = platform_match * 0.2
            
            timing_score = await self._calculate_timing_score(audience_data, content_data)
            timing_bonus = timing_score * 0.1
            
            # Engagement prédit
            predicted_engagement = base_engagement + novelty_bonus + platform_bonus + timing_bonus
            predicted_engagement = min(predicted_engagement, 1.0)
            
            # Prédiction de partage
            sharing_probability = model['sharing_propensity'] * content_novelty
            
            # Prédiction de conversion
            conversion_probability = model['conversion_rate'] * platform_match
            
            return {
                'behavior_pattern': behavior_pattern.value,
                'predicted_engagement_rate': predicted_engagement,
                'sharing_probability': sharing_probability,
                'conversion_probability': conversion_probability,
                'engagement_confidence': await self._calculate_prediction_confidence(audience_data),
                'behavioral_insights': await self._generate_behavioral_insights(behavior_pattern, model),
                'optimization_recommendations': await self._generate_optimization_recommendations(
                    behavior_pattern, model, content_data
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting engagement behavior: {str(e)}")
            return self._get_default_behavior_prediction()
    
    async def _classify_behavior_pattern(self, audience_data: Dict[str, Any]) -> BehaviorPattern:
        """Classifie le pattern comportemental d'une audience."""
        try:
            # Métriques clés pour la classification
            engagement_rate = audience_data.get('avg_engagement_rate', 0.03)
            content_sharing_rate = audience_data.get('sharing_rate', 0.1)
            platform_diversity = audience_data.get('platform_count', 3)
            content_creation_rate = audience_data.get('creation_rate', 0.0)
            early_adoption_score = audience_data.get('early_adoption_score', 0.5)
            
            # Score de classification
            scores = {}
            
            # Early Adopter
            scores[BehaviorPattern.EARLY_ADOPTER] = (
                (early_adoption_score * 0.4) +
                (min(platform_diversity / 8, 1.0) * 0.3) +
                (min(engagement_rate / 0.08, 1.0) * 0.3)
            )
            
            # Trendsetter
            scores[BehaviorPattern.TRENDSETTER] = (
                (content_creation_rate * 0.4) +
                (min(content_sharing_rate / 0.5, 1.0) * 0.3) +
                (min(engagement_rate / 0.12, 1.0) * 0.3)
            )
            
            # Activist
            scores[BehaviorPattern.ACTIVIST] = (
                (min(content_sharing_rate / 0.8, 1.0) * 0.5) +
                (min(engagement_rate / 0.15, 1.0) * 0.3) +
                (audience_data.get('cause_engagement', 0.0) * 0.2)
            )
            
            # Lurker
            scores[BehaviorPattern.LURKER] = (
                (1.0 - min(engagement_rate / 0.02, 1.0)) * 0.4 +
                (1.0 - min(content_sharing_rate / 0.05, 1.0)) * 0.3 +
                (audience_data.get('viewing_time', 0.5) * 0.3)
            )
            
            # Follower
            scores[BehaviorPattern.FOLLOWER] = (
                (1.0 - early_adoption_score) * 0.4 +
                (min(engagement_rate / 0.04, 1.0) * 0.3) +
                (audience_data.get('trend_following_score', 0.7) * 0.3)
            )
            
            # Casual
            scores[BehaviorPattern.CASUAL] = 0.5  # Score de base
            
            # Retourne le pattern avec le score le plus élevé
            best_pattern = max(scores.items(), key=lambda x: x[1])
            
            # Seuil minimum pour éviter les faux positifs
            if best_pattern[1] < 0.4:
                return BehaviorPattern.CASUAL
            
            return best_pattern[0]
            
        except Exception as e:
            self.logger.error(f"Error classifying behavior pattern: {str(e)}")
            return BehaviorPattern.CASUAL
    
    async def _calculate_timing_score(self, audience_data: Dict[str, Any], 
                                    content_data: Dict[str, Any]) -> float:
        """Calcule le score de timing optimal pour l'audience."""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            current_day = current_time.weekday()
            
            # Heures préférées de l'audience
            preferred_hours = audience_data.get('preferred_hours', [8, 12, 17, 20])
            
            # Score horaire
            hour_score = 1.0 if current_hour in preferred_hours else 0.6
            
            # Score de jour de semaine
            preferred_days = audience_data.get('preferred_days', [0, 1, 2, 3, 4])  # Lun-Ven
            day_score = 1.0 if current_day in preferred_days else 0.7
            
            # Score de saisonnalité
            seasonal_score = audience_data.get('seasonal_activity', {}).get(str(current_time.month), 0.8)
            
            # Score composite
            timing_score = (hour_score * 0.5 + day_score * 0.3 + seasonal_score * 0.2)
            
            return timing_score
            
        except Exception as e:
            self.logger.error(f"Error calculating timing score: {str(e)}")
            return 0.7
    
    async def _calculate_prediction_confidence(self, audience_data: Dict[str, Any]) -> float:
        """Calcule la confiance dans la prédiction."""
        confidence_factors = []
        
        # Facteur de données historiques
        data_points = audience_data.get('historical_data_points', 0)
        data_confidence = min(data_points / 100, 1.0)  # 100+ points = confiance max
        confidence_factors.append(data_confidence)
        
        # Facteur de cohérence comportementale
        behavior_consistency = audience_data.get('behavior_consistency_score', 0.7)
        confidence_factors.append(behavior_consistency)
        
        # Facteur de récence des données
        last_activity = audience_data.get('last_activity_days_ago', 30)
        recency_confidence = max(0.3, 1.0 - (last_activity / 90))  # Décroissance sur 90 jours
        confidence_factors.append(recency_confidence)
        
        return np.mean(confidence_factors)
    
    async def _generate_behavioral_insights(self, behavior_pattern: BehaviorPattern, 
                                          model: Dict[str, Any]) -> List[str]:
        """Génère des insights comportementaux."""
        insights = []
        
        if behavior_pattern == BehaviorPattern.EARLY_ADOPTER:
            insights.extend([
                "Audience très réactive aux nouveautés",
                "Préfère le contenu exclusif et avant-première",
                "Forte propension au partage de découvertes"
            ])
        elif behavior_pattern == BehaviorPattern.TRENDSETTER:
            insights.extend([
                "Audience créatrice de tendances",
                "Influence élevée sur leur réseau",
                "Recherche constamment l'originalité"
            ])
        elif behavior_pattern == BehaviorPattern.ACTIVIST:
            insights.extend([
                "Engagement très élevé sur les causes",
                "Partage massif de contenu aligné avec leurs valeurs",
                "Potentiel viral important pour le bon contenu"
            ])
        elif behavior_pattern == BehaviorPattern.LURKER:
            insights.extend([
                "Consomme beaucoup mais interagit peu",
                "Nécessite des incitations spéciales pour l'engagement",
                "Audience fidèle mais silencieuse"
            ])
        elif behavior_pattern == BehaviorPattern.FOLLOWER:
            insights.extend([
                "Suit les tendances établies",
                "Engagement modéré mais prévisible",
                "Répond bien aux preuves sociales"
            ])
        else:  # CASUAL
            insights.extend([
                "Engagement variable selon l'intérêt",
                "Sensible à la qualité du contenu",
                "Timing crucial pour l'engagement"
            ])
        
        return insights
    
    async def _generate_optimization_recommendations(self, behavior_pattern: BehaviorPattern,
                                                   model: Dict[str, Any], 
                                                   content_data: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'optimisation."""
        recommendations = []
        
        if behavior_pattern == BehaviorPattern.EARLY_ADOPTER:
            recommendations.extend([
                "Mettre en avant la nouveauté et l'exclusivité",
                "Inclure des éléments 'première mondiale' ou 'avant-première'",
                "Faciliter le partage pour amplification"
            ])
        elif behavior_pattern == BehaviorPattern.TRENDSETTER:
            recommendations.extend([
                "Créer du contenu original et unique",
                "Inclure des éléments personnalisables",
                "Optimiser pour la créativité et l'expression personnelle"
            ])
        elif behavior_pattern == BehaviorPattern.ACTIVIST:
            recommendations.extend([
                "Aligner le contenu avec des causes importantes",
                "Inclure des appels à l'action clairs",
                "Faciliter le partage avec message personnel"
            ])
        elif behavior_pattern == BehaviorPattern.LURKER:
            recommendations.extend([
                "Créer des incitations subtiles à l'interaction",
                "Proposer des interactions à faible effort (like, save)",
                "Utiliser des questions ouvertes simples"
            ])
        elif behavior_pattern == BehaviorPattern.FOLLOWER:
            recommendations.extend([
                "Inclure des preuves sociales (témoignages, stats)",
                "Suivre les formats de contenu populaires",
                "Optimiser le timing selon les heures de pointe"
            ])
        else:  # CASUAL
            recommendations.extend([
                "Maximiser la qualité et la valeur du contenu",
                "Optimiser les 3 premières secondes",
                "Utiliser des hooks émotionnels forts"
            ])
        
        return recommendations
    
    def _get_default_behavior_prediction(self) -> Dict[str, Any]:
        """Retourne une prédiction par défaut."""
        return {
            'behavior_pattern': BehaviorPattern.CASUAL.value,
            'predicted_engagement_rate': 0.03,
            'sharing_probability': 0.1,
            'conversion_probability': 0.05,
            'engagement_confidence': 0.5,
            'behavioral_insights': ["Données insuffisantes pour analyse approfondie"],
            'optimization_recommendations': ["Améliorer la collecte de données d'audience"]
        }

class AudienceIntelligenceEngine:
    """Moteur d'intelligence d'audience pour analyse comportementale avancée."""
    
    def __init__(self):
        self.behavior_predictor = BehaviorPredictor()
        self.audience_profiles = {}
        self.segment_analytics = defaultdict(list)
        self.lookalike_models = {}
        self.real_time_behavior_tracking = defaultdict(list)
        self.logger = logging.getLogger("AudienceIntelligenceEngine")
        
        self._initialize_segmentation_models()
    
    def _initialize_segmentation_models(self):
        """Initialise les modèles de segmentation d'audience."""
        self.logger.info("Initializing audience segmentation models...")
        
        # Modèles de segmentation par type d'audience
        self.segmentation_models = {
            AudienceSegment.CREATOR: {
                'content_creation_rate': 0.8,
                'follower_growth_rate': 0.6,
                'engagement_with_creators': 0.9,
                'tool_usage_frequency': 0.7,
                'monetization_activity': 0.5
            },
            AudienceSegment.CONSUMER: {
                'content_consumption_rate': 0.9,
                'purchase_behavior': 0.7,
                'brand_loyalty': 0.6,
                'price_sensitivity': 0.8,
                'recommendation_following': 0.8
            },
            AudienceSegment.INFLUENCER: {
                'follower_count': 0.9,
                'engagement_rate': 0.8,
                'brand_collaboration_rate': 0.7,
                'content_consistency': 0.8,
                'audience_growth_rate': 0.7
            },
            AudienceSegment.BRAND: {
                'business_content_ratio': 0.9,
                'promotional_activity': 0.8,
                'customer_service_engagement': 0.7,
                'marketing_budget_indicators': 0.6,
                'b2b_interactions': 0.8
            },
            AudienceSegment.COMMUNITY: {
                'group_participation': 0.9,
                'community_content_sharing': 0.8,
                'event_attendance': 0.7,
                'member_helping_behavior': 0.8,
                'long_term_engagement': 0.9
            }
        }
        
        self.logger.info(f"Initialized segmentation models for {len(self.segmentation_models)} audience types")
    
    async def analyze_audience_profile(self, audience_id: str, audience_data: Dict[str, Any]) -> AudienceProfile:
        """Analyse complète du profil d'audience."""
        try:
            self.logger.info(f"Analyzing audience profile for {audience_id}")
            
            # Classification de segment
            audience_segment = await self._classify_audience_segment(audience_data)
            
            # Prédiction comportementale
            behavior_prediction = await self.behavior_predictor.predict_engagement_behavior(
                audience_data, {}
            )
            behavior_pattern = BehaviorPattern(behavior_prediction['behavior_pattern'])
            
            # Analyse démographique
            demographics = await self._analyze_demographics(audience_data)
            
            # Extraction d'intérêts
            interests = await self._extract_interests(audience_data)
            
            # Préférences de plateforme
            platform_preferences = await self._analyze_platform_preferences(audience_data)
            
            # Patterns d'engagement
            engagement_patterns = await self._analyze_engagement_patterns(audience_data)
            
            # Préférences de contenu
            content_preferences = await self._analyze_content_preferences(audience_data)
            
            # Timing optimal
            optimal_timing = await self._calculate_optimal_timing(audience_data)
            
            # Scores avancés
            influence_score = await self._calculate_influence_score(audience_data)
            loyalty_score = await self._calculate_loyalty_score(audience_data)
            conversion_likelihood = await self._calculate_conversion_likelihood(audience_data)
            
            # Création du profil
            profile = AudienceProfile(
                audience_id=audience_id,
                segment=audience_segment,
                behavior_pattern=behavior_pattern,
                demographics=demographics,
                interests=interests,
                platform_preferences=platform_preferences,
                engagement_patterns=engagement_patterns,
                content_preferences=content_preferences,
                optimal_timing=optimal_timing,
                influence_score=influence_score,
                loyalty_score=loyalty_score,
                conversion_likelihood=conversion_likelihood,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            # Mise en cache
            self.audience_profiles[audience_id] = profile
            
            # Mise à jour des analytics de segment
            self.segment_analytics[audience_segment].append({
                'profile_id': audience_id,
                'analysis_date': datetime.now(),
                'key_metrics': {
                    'influence_score': influence_score,
                    'loyalty_score': loyalty_score,
                    'conversion_likelihood': conversion_likelihood
                }
            })
            
            self.logger.info(f"Audience profile analysis completed for {audience_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error analyzing audience profile: {str(e)}")
            raise
    
    async def _classify_audience_segment(self, audience_data: Dict[str, Any]) -> AudienceSegment:
        """Classifie le segment d'audience."""
        try:
            scores = {}
            
            for segment, model in self.segmentation_models.items():
                score = 0
                total_weight = 0
                
                for feature, weight in model.items():
                    if feature in audience_data:
                        # Normalisation de la valeur
                        raw_value = audience_data[feature]
                        if isinstance(raw_value, (int, float)):
                            normalized_value = min(raw_value, 1.0)
                        elif isinstance(raw_value, bool):
                            normalized_value = 1.0 if raw_value else 0.0
                        else:
                            normalized_value = 0.5
                        
                        score += normalized_value * weight
                        total_weight += weight
                
                if total_weight > 0:
                    scores[segment] = score / total_weight
                else:
                    scores[segment] = 0.0
            
            # Retourne le segment avec le score le plus élevé
            best_segment = max(scores.items(), key=lambda x: x[1])
            
            # Seuil minimum pour éviter les classifications erronées
            if best_segment[1] < 0.3:
                return AudienceSegment.CONSUMER  # Segment par défaut
            
            return best_segment[0]
            
        except Exception as e:
            self.logger.error(f"Error classifying audience segment: {str(e)}")
            return AudienceSegment.CONSUMER
    
    async def _analyze_demographics(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les données démographiques."""
        demographics = {}
        
        # Extraction des données démographiques disponibles
        demo_fields = ['age', 'age_range', 'gender', 'location', 'country', 'language', 'timezone']
        
        for field in demo_fields:
            if field in audience_data:
                demographics[field] = audience_data[field]
        
        # Analyse des patterns géographiques
        if 'country' in demographics:
            demographics['market_tier'] = await self._classify_market_tier(demographics['country'])
        
        # Analyse temporelle
        if 'timezone' in demographics:
            demographics['optimal_hours_local'] = await self._calculate_local_optimal_hours(
                demographics['timezone']
            )
        
        return demographics
    
    async def _extract_interests(self, audience_data: Dict[str, Any]) -> List[str]:
        """Extrait les intérêts de l'audience."""
        interests = []
        
        # Sources d'intérêts
        interest_sources = [
            'topics_followed', 'hashtags_used', 'content_categories',
            'brand_interactions', 'event_attendance', 'purchase_categories'
        ]
        
        for source in interest_sources:
            if source in audience_data:
                source_interests = audience_data[source]
                if isinstance(source_interests, list):
                    interests.extend(source_interests)
                elif isinstance(source_interests, str):
                    interests.append(source_interests)
        
        # Déduplication et priorisation
        interest_counts = Counter(interests)
        top_interests = [interest for interest, count in interest_counts.most_common(20)]
        
        return top_interests
    
    async def _analyze_platform_preferences(self, audience_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyse les préférences de plateforme."""
        platform_preferences = {}
        
        # Données d'usage par plateforme
        platform_usage = audience_data.get('platform_usage', {})
        
        for platform, usage_data in platform_usage.items():
            # Calcul du score de préférence basé sur l'usage
            time_spent = usage_data.get('time_spent_hours', 0)
            engagement_rate = usage_data.get('engagement_rate', 0)
            frequency = usage_data.get('sessions_per_week', 0)
            
            # Score composite normalisé
            preference_score = (
                min(time_spent / 10, 1.0) * 0.4 +
                min(engagement_rate / 0.1, 1.0) * 0.4 +
                min(frequency / 20, 1.0) * 0.2
            )
            
            platform_preferences[platform] = preference_score
        
        return platform_preferences
    
    async def _analyze_engagement_patterns(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les patterns d'engagement."""
        patterns = {}
        
        # Patterns temporels
        hourly_activity = audience_data.get('hourly_activity', {})
        if hourly_activity:
            peak_hours = [hour for hour, activity in hourly_activity.items() 
                         if activity > np.mean(list(hourly_activity.values()))]
            patterns['peak_hours'] = peak_hours
        
        # Patterns de contenu
        content_engagement = audience_data.get('content_type_engagement', {})
        if content_engagement:
            preferred_content = max(content_engagement.items(), key=lambda x: x[1])
            patterns['preferred_content_type'] = preferred_content[0]
        
        # Patterns d'interaction
        interaction_types = audience_data.get('interaction_distribution', {})
        if interaction_types:
            dominant_interaction = max(interaction_types.items(), key=lambda x: x[1])
            patterns['dominant_interaction'] = dominant_interaction[0]
        
        # Fréquence d'engagement
        patterns['engagement_frequency'] = audience_data.get('avg_engagements_per_week', 0)
        
        # Consistance d'engagement
        engagement_history = audience_data.get('engagement_history', [])
        if len(engagement_history) > 1:
            patterns['engagement_consistency'] = 1.0 - np.std(engagement_history) / np.mean(engagement_history)
        else:
            patterns['engagement_consistency'] = 0.5
        
        return patterns
    
    async def _analyze_content_preferences(self, audience_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyse les préférences de contenu."""
        preferences = {}
        
        # Types de contenu
        content_types = ['text', 'image', 'video', 'audio', 'carousel', 'story', 'live']
        
        for content_type in content_types:
            engagement_key = f'{content_type}_engagement_rate'
            if engagement_key in audience_data:
                preferences[content_type] = audience_data[engagement_key]
            else:
                # Valeur par défaut basée sur des moyennes générales
                default_prefs = {
                    'video': 0.8, 'image': 0.6, 'carousel': 0.7,
                    'story': 0.5, 'text': 0.4, 'audio': 0.5, 'live': 0.9
                }
                preferences[content_type] = default_prefs.get(content_type, 0.5)
        
        # Normalisation
        max_pref = max(preferences.values())
        if max_pref > 0:
            preferences = {k: v/max_pref for k, v in preferences.items()}
        
        return preferences
    
    async def _calculate_optimal_timing(self, audience_data: Dict[str, Any]) -> List[str]:
        """Calcule le timing optimal pour l'audience."""
        optimal_times = []
        
        # Analyse de l'activité horaire
        hourly_activity = audience_data.get('hourly_activity', {})
        
        if hourly_activity:
            # Trouve les heures avec l'activité la plus élevée
            sorted_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)
            top_hours = [hour for hour, activity in sorted_hours[:4]]
            optimal_times.extend([f"{hour}:00" for hour in top_hours])
        else:
            # Heures par défaut basées sur des patterns généraux
            optimal_times = ["08:00", "12:00", "17:00", "20:00"]
        
        return optimal_times
    
    async def _calculate_influence_score(self, audience_data: Dict[str, Any]) -> float:
        """Calcule le score d'influence de l'audience."""
        influence_factors = []
        
        # Facteurs d'influence
        follower_count = audience_data.get('follower_count', 0)
        if follower_count > 0:
            # Score logarithmique pour les followers
            follower_score = min(np.log10(follower_count) / 6, 1.0)  # Max à 1M followers
            influence_factors.append(follower_score)
        
        # Taux d'engagement
        engagement_rate = audience_data.get('avg_engagement_rate', 0)
        engagement_score = min(engagement_rate / 0.1, 1.0)  # Max à 10%
        influence_factors.append(engagement_score)
        
        # Taux de partage
        sharing_rate = audience_data.get('sharing_rate', 0)
        sharing_score = min(sharing_rate / 0.3, 1.0)  # Max à 30%
        influence_factors.append(sharing_score)
        
        # Diversité de plateforme
        platform_count = len(audience_data.get('platform_usage', {}))
        platform_score = min(platform_count / 8, 1.0)  # Max à 8 plateformes
        influence_factors.append(platform_score)
        
        if influence_factors:
            return np.mean(influence_factors)
        else:
            return 0.3  # Score par défaut
    
    async def _calculate_loyalty_score(self, audience_data: Dict[str, Any]) -> float:
        """Calcule le score de fidélité de l'audience."""
        loyalty_factors = []
        
        # Ancienneté
        account_age_days = audience_data.get('account_age_days', 30)
        age_score = min(account_age_days / 365, 1.0)  # Max à 1 an
        loyalty_factors.append(age_score)
        
        # Consistance d'engagement
        engagement_consistency = audience_data.get('engagement_consistency', 0.5)
        loyalty_factors.append(engagement_consistency)
        
        # Fréquence d'activité
        activity_frequency = audience_data.get('activity_frequency_score', 0.5)
        loyalty_factors.append(activity_frequency)
        
        # Fidélité aux créateurs
        creator_loyalty = audience_data.get('creator_loyalty_score', 0.5)
        loyalty_factors.append(creator_loyalty)
        
        return np.mean(loyalty_factors)
    
    async def _calculate_conversion_likelihood(self, audience_data: Dict[str, Any]) -> float:
        """Calcule la probabilité de conversion."""
        conversion_factors = []
        
        # Historique d'achat
        purchase_history = audience_data.get('purchase_count', 0)
        if purchase_history > 0:
            purchase_score = min(purchase_history / 10, 1.0)
            conversion_factors.append(purchase_score)
        
        # Engagement avec contenu commercial
        commercial_engagement = audience_data.get('commercial_content_engagement', 0)
        conversion_factors.append(commercial_engagement)
        
        # Clics sur liens
        click_through_rate = audience_data.get('click_through_rate', 0)
        ctr_score = min(click_through_rate / 0.05, 1.0)  # Max à 5%
        conversion_factors.append(ctr_score)
        
        # Score de revenu (si disponible)
        revenue_score = audience_data.get('revenue_potential_score', 0.3)
        conversion_factors.append(revenue_score)
        
        if conversion_factors:
            return np.mean(conversion_factors)
        else:
            return 0.2  # Score par défaut conservateur
    
    async def _classify_market_tier(self, country: str) -> str:
        """Classifie le tier de marché par pays."""
        tier_1_countries = [
            'US', 'UK', 'DE', 'FR', 'CA', 'AU', 'JP', 'NL', 'SE', 'CH', 'NO', 'DK'
        ]
        tier_2_countries = [
            'ES', 'IT', 'BR', 'MX', 'KR', 'SG', 'HK', 'BE', 'AT', 'IE', 'FI', 'NZ'
        ]
        
        if country in tier_1_countries:
            return 'tier_1'
        elif country in tier_2_countries:
            return 'tier_2'
        else:
            return 'tier_3'
    
    async def _calculate_local_optimal_hours(self, timezone: str) -> List[str]:
        """Calcule les heures optimales en heure locale."""
        # Heures optimales UTC
        utc_optimal_hours = [8, 12, 17, 20]
        
        # Simulation de conversion timezone (simplifiée)
        # En réalité, utiliserait pytz ou similar
        timezone_offset = 0  # Simplification
        
        local_optimal_hours = [(hour + timezone_offset) % 24 for hour in utc_optimal_hours]
        
        return [f"{hour:02d}:00" for hour in local_optimal_hours]
    
    async def find_lookalike_audiences(self, reference_audience_id: str, 
                                     similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Trouve des audiences similaires à une audience de référence."""
        try:
            if reference_audience_id not in self.audience_profiles:
                raise ValueError(f"Reference audience {reference_audience_id} not found")
            
            reference_profile = self.audience_profiles[reference_audience_id]
            lookalike_audiences = []
            
            for audience_id, profile in self.audience_profiles.items():
                if audience_id == reference_audience_id:
                    continue
                
                # Calcul de similarité
                similarity_score = await self._calculate_audience_similarity(reference_profile, profile)
                
                if similarity_score >= similarity_threshold:
                    lookalike_audiences.append({
                        'audience_id': audience_id,
                        'similarity_score': similarity_score,
                        'shared_characteristics': await self._identify_shared_characteristics(
                            reference_profile, profile
                        ),
                        'profile': profile
                    })
            
            # Tri par score de similarité
            lookalike_audiences.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return lookalike_audiences[:10]  # Top 10 audiences similaires
            
        except Exception as e:
            self.logger.error(f"Error finding lookalike audiences: {str(e)}")
            return []
    
    async def _calculate_audience_similarity(self, profile1: AudienceProfile, 
                                          profile2: AudienceProfile) -> float:
        """Calcule la similarité entre deux profils d'audience."""
        similarity_factors = []
        
        # Similarité de segment
        segment_similarity = 1.0 if profile1.segment == profile2.segment else 0.3
        similarity_factors.append(segment_similarity * 0.25)
        
        # Similarité de pattern comportemental
        behavior_similarity = 1.0 if profile1.behavior_pattern == profile2.behavior_pattern else 0.4
        similarity_factors.append(behavior_similarity * 0.25)
        
        # Similarité d'intérêts
        common_interests = set(profile1.interests).intersection(set(profile2.interests))
        total_interests = set(profile1.interests).union(set(profile2.interests))
        interest_similarity = len(common_interests) / len(total_interests) if total_interests else 0
        similarity_factors.append(interest_similarity * 0.2)
        
        # Similarité de préférences de plateforme
        platform_similarity = await self._calculate_platform_preference_similarity(
            profile1.platform_preferences, profile2.platform_preferences
        )
        similarity_factors.append(platform_similarity * 0.15)
        
        # Similarité démographique
        demo_similarity = await self._calculate_demographic_similarity(
            profile1.demographics, profile2.demographics
        )
        similarity_factors.append(demo_similarity * 0.15)
        
        return sum(similarity_factors)
    
    async def _calculate_platform_preference_similarity(self, prefs1: Dict[str, float], 
                                                      prefs2: Dict[str, float]) -> float:
        """Calcule la similarité des préférences de plateforme."""
        common_platforms = set(prefs1.keys()).intersection(set(prefs2.keys()))
        
        if not common_platforms:
            return 0.0
        
        similarities = []
        for platform in common_platforms:
            # Similarité basée sur la différence absolue
            diff = abs(prefs1[platform] - prefs2[platform])
            similarity = 1.0 - diff
            similarities.append(similarity)
        
        return np.mean(similarities)
    
    async def _calculate_demographic_similarity(self, demo1: Dict[str, Any], 
                                              demo2: Dict[str, Any]) -> float:
        """Calcule la similarité démographique."""
        demo_similarities = []
        
        # Comparaison des champs démographiques
        comparable_fields = ['age_range', 'country', 'language', 'market_tier']
        
        for field in comparable_fields:
            if field in demo1 and field in demo2:
                if demo1[field] == demo2[field]:
                    demo_similarities.append(1.0)
                else:
                    demo_similarities.append(0.0)
        
        return np.mean(demo_similarities) if demo_similarities else 0.5
    
    async def _identify_shared_characteristics(self, profile1: AudienceProfile, 
                                             profile2: AudienceProfile) -> List[str]:
        """Identifie les caractéristiques partagées entre deux profils."""
        shared_characteristics = []
        
        # Caractéristiques communes
        if profile1.segment == profile2.segment:
            shared_characteristics.append(f"Même segment: {profile1.segment.value}")
        
        if profile1.behavior_pattern == profile2.behavior_pattern:
            shared_characteristics.append(f"Même pattern comportemental: {profile1.behavior_pattern.value}")
        
        # Intérêts communs
        common_interests = set(profile1.interests).intersection(set(profile2.interests))
        if common_interests:
            shared_characteristics.append(f"Intérêts communs: {', '.join(list(common_interests)[:3])}")
        
        # Plateformes préférées communes
        top_platforms_1 = sorted(profile1.platform_preferences.items(), key=lambda x: x[1], reverse=True)[:3]
        top_platforms_2 = sorted(profile2.platform_preferences.items(), key=lambda x: x[1], reverse=True)[:3]
        
        common_platforms = set([p[0] for p in top_platforms_1]).intersection(
            set([p[0] for p in top_platforms_2])
        )
        
        if common_platforms:
            shared_characteristics.append(f"Plateformes préférées communes: {', '.join(common_platforms)}")
        
        return shared_characteristics
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du moteur d'intelligence d'audience."""
        segment_counts = defaultdict(int)
        behavior_counts = defaultdict(int)
        
        for profile in self.audience_profiles.values():
            segment_counts[profile.segment.value] += 1
            behavior_counts[profile.behavior_pattern.value] += 1
        
        return {
            'total_profiles': len(self.audience_profiles),
            'segment_distribution': dict(segment_counts),
            'behavior_distribution': dict(behavior_counts),
            'segmentation_models': len(self.segmentation_models),
            'behavior_models': len(self.behavior_predictor.behavior_models),
            'average_influence_score': np.mean([p.influence_score for p in self.audience_profiles.values()]) 
                                     if self.audience_profiles else 0,
            'average_loyalty_score': np.mean([p.loyalty_score for p in self.audience_profiles.values()]) 
                                   if self.audience_profiles else 0,
            'engine_status': 'operational'
        }