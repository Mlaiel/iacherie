"""
Intelligent Scheduler - Distribution Module
==========================================
Scheduling intelligent avec algorithmes ML pour timing optimal
et analyse audience overlap prevention.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class TimingStrategy(Enum):
    """Stratégies de timing pour optimisation."""
    ML_OPTIMAL = "ml_optimal"
    AUDIENCE_BASED = "audience_based"
    PLATFORM_ALGORITHM = "platform_algorithm"
    GLOBAL_TIMEZONE = "global_timezone"
    COMPETITOR_AVOIDANCE = "competitor_avoidance"

@dataclass
class AudienceData:
    """Données audience pour optimisation timing."""
    timezone_distribution: Dict[str, float]
    engagement_patterns: Dict[str, float]
    peak_activity_hours: List[int]
    platform_preferences: Dict[str, float]
    demographic_breakdown: Dict[str, Any]

@dataclass
class PlatformAlgorithmData:
    """Données algorithmes plateforme."""
    platform_name: str
    optimal_posting_times: List[datetime]
    algorithm_preferences: Dict[str, Any]
    content_saturation_periods: List[tuple[datetime, datetime]]
    engagement_boost_windows: List[tuple[datetime, datetime]]

@dataclass
class SchedulingResult:
    """Résultat optimisation scheduling."""
    platform: str
    optimal_time: datetime
    confidence_score: float
    strategy_used: TimingStrategy
    audience_overlap_risk: float
    expected_engagement: float
    reasoning: str

class IntelligentScheduler:
    """Scheduling intelligent avec algorithmes ML pour timing optimal."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ml_models = {}
        self.platform_algorithms = {}
        self.audience_data_cache = {}
        self.competitor_activity_tracker = CompetitorActivityTracker()
        
    async def ml_powered_timing_prediction(
        self,
        content_type: str,
        target_platforms: List[str],
        audience_data: AudienceData,
        historical_performance: Dict[str, Any]
    ) -> Dict[str, SchedulingResult]:
        """Prédiction timing optimal avec ML."""
        try:
            results = {}
            
            for platform in target_platforms:
                # Extract features pour ML model
                features = self._extract_timing_features(
                    content_type, platform, audience_data, historical_performance
                )
                
                # ML prediction
                model = await self._get_ml_model(platform)
                prediction = await self._predict_optimal_timing(model, features)
                
                # Calcul confidence score
                confidence = await self._calculate_confidence_score(
                    prediction, features, platform
                )
                
                results[platform] = SchedulingResult(
                    platform=platform,
                    optimal_time=prediction['optimal_time'],
                    confidence_score=confidence,
                    strategy_used=TimingStrategy.ML_OPTIMAL,
                    audience_overlap_risk=prediction['overlap_risk'],
                    expected_engagement=prediction['expected_engagement'],
                    reasoning=f"ML model prediction based on {len(features)} features"
                )
                
            return results
            
        except Exception as e:
            self.logger.error(f"ML timing prediction error: {e}")
            return await self._fallback_timing_strategy(target_platforms, audience_data)
    
    async def audience_overlap_analysis(
        self,
        scheduled_posts: Dict[str, datetime],
        audience_data: AudienceData
    ) -> Dict[str, float]:
        """Analyse overlap audience entre plateformes."""
        try:
            overlap_scores = {}
            
            for platform1, time1 in scheduled_posts.items():
                overlap_scores[platform1] = 0.0
                
                for platform2, time2 in scheduled_posts.items():
                    if platform1 != platform2:
                        # Calcul overlap temporel
                        time_diff = abs((time1 - time2).total_seconds() / 3600)
                        
                        # Overlap audience entre plateformes
                        audience_overlap = self._calculate_audience_overlap(
                            platform1, platform2, audience_data
                        )
                        
                        # Score impact overlap
                        if time_diff <= 2:  # Moins de 2h d'écart
                            overlap_penalty = audience_overlap * (2 - time_diff) / 2
                            overlap_scores[platform1] += overlap_penalty
                
            return overlap_scores
            
        except Exception as e:
            self.logger.error(f"Audience overlap analysis error: {e}")
            return {platform: 0.0 for platform in scheduled_posts.keys()}
    
    async def platform_algorithm_adaptation(
        self,
        target_platforms: List[str],
        content_metadata: Dict[str, Any]
    ) -> Dict[str, PlatformAlgorithmData]:
        """Adaptation aux algorithmes natifs des plateformes."""
        try:
            algorithm_data = {}
            
            for platform in target_platforms:
                # Récupération données algorithme plateforme
                algo_config = await self._get_platform_algorithm_config(platform)
                
                # Analyse saturation contenu
                saturation_periods = await self._analyze_content_saturation(
                    platform, content_metadata
                )
                
                # Fenêtres boost engagement
                boost_windows = await self._identify_engagement_boost_windows(
                    platform, algo_config
                )
                
                # Optimisation timing selon algorithme
                optimal_times = await self._optimize_for_platform_algorithm(
                    platform, algo_config, saturation_periods
                )
                
                algorithm_data[platform] = PlatformAlgorithmData(
                    platform_name=platform,
                    optimal_posting_times=optimal_times,
                    algorithm_preferences=algo_config,
                    content_saturation_periods=saturation_periods,
                    engagement_boost_windows=boost_windows
                )
                
            return algorithm_data
            
        except Exception as e:
            self.logger.error(f"Platform algorithm adaptation error: {e}")
            return {}
    
    async def timezone_optimization_global(
        self,
        target_regions: List[str],
        audience_data: AudienceData
    ) -> Dict[str, datetime]:
        """Optimisation globale fuseaux horaires."""
        try:
            optimal_times = {}
            
            # Analyse distribution timezone audience
            timezone_weights = audience_data.timezone_distribution
            
            for region in target_regions:
                # Calcul timing optimal par région
                region_timezones = await self._get_region_timezones(region)
                
                # Pondération audience par timezone
                weighted_optimal_time = await self._calculate_weighted_optimal_time(
                    region_timezones, timezone_weights, audience_data.peak_activity_hours
                )
                
                # Ajustement selon patterns locaux
                localized_time = await self._apply_local_adjustments(
                    weighted_optimal_time, region
                )
                
                optimal_times[region] = localized_time
                
            return optimal_times
            
        except Exception as e:
            self.logger.error(f"Timezone optimization error: {e}")
            return {}
    
    async def seasonal_trend_analysis(
        self,
        content_category: str,
        target_date_range: tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Analyse tendances saisonnières."""
        try:
            trends = {
                'seasonal_multipliers': {},
                'trending_topics': [],
                'optimal_periods': [],
                'avoid_periods': []
            }
            
            start_date, end_date = target_date_range
            
            # Analyse tendances historiques
            historical_data = await self._get_historical_seasonal_data(
                content_category, start_date, end_date
            )
            
            # Calcul multiplicateurs saisonniers
            trends['seasonal_multipliers'] = await self._calculate_seasonal_multipliers(
                historical_data, content_category
            )
            
            # Identification trending topics
            trends['trending_topics'] = await self._identify_trending_topics(
                content_category, start_date, end_date
            )
            
            # Périodes optimales et à éviter
            trends['optimal_periods'] = await self._identify_optimal_periods(
                historical_data, trends['seasonal_multipliers']
            )
            trends['avoid_periods'] = await self._identify_avoid_periods(
                historical_data, trends['seasonal_multipliers']
            )
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Seasonal trend analysis error: {e}")
            return {'seasonal_multipliers': {}, 'trending_topics': [], 'optimal_periods': [], 'avoid_periods': []}
    
    async def competitor_timing_avoidance(
        self,
        content_niche: str,
        target_platforms: List[str],
        competitor_ids: List[str]
    ) -> Dict[str, List[datetime]]:
        """Évitement timing concurrents."""
        try:
            avoidance_windows = {}
            
            for platform in target_platforms:
                # Récupération activité concurrents
                competitor_activity = await self.competitor_activity_tracker.get_competitor_schedule(
                    competitor_ids, platform, content_niche
                )
                
                # Identification fenêtres à éviter
                avoid_windows = await self._identify_competitor_clash_windows(
                    competitor_activity, platform
                )
                
                # Génération créneaux alternatifs
                alternative_slots = await self._generate_alternative_time_slots(
                    avoid_windows, platform
                )
                
                avoidance_windows[platform] = alternative_slots
                
            return avoidance_windows
            
        except Exception as e:
            self.logger.error(f"Competitor timing avoidance error: {e}")
            return {platform: [] for platform in target_platforms}
    
    def _extract_timing_features(
        self,
        content_type: str,
        platform: str,
        audience_data: AudienceData,
        historical_performance: Dict[str, Any]
    ) -> np.ndarray:
        """Extract features pour ML model."""
        features = []
        
        # Content type encoding
        content_type_map = {'video': 1, 'image': 2, 'text': 3, 'audio': 4}
        features.append(content_type_map.get(content_type, 0))
        
        # Platform encoding
        platform_map = {'instagram': 1, 'tiktok': 2, 'youtube': 3, 'facebook': 4, 'twitter': 5}
        features.append(platform_map.get(platform, 0))
        
        # Audience features
        features.extend([
            len(audience_data.timezone_distribution),
            np.mean(list(audience_data.engagement_patterns.values())),
            len(audience_data.peak_activity_hours)
        ])
        
        # Historical performance features
        features.extend([
            historical_performance.get('avg_engagement', 0),
            historical_performance.get('best_hour', 12),
            historical_performance.get('consistency_score', 0)
        ])
        
        return np.array(features)
    
    async def _get_ml_model(self, platform: str):
        """Récupération model ML pour plateforme."""
        if platform not in self.ml_models:
            # Simulation modèle ML - en production, charger modèle réel
            self.ml_models[platform] = {
                'weights': np.random.random((10, 1)),
                'bias': np.random.random(),
                'platform': platform
            }
        return self.ml_models[platform]
    
    async def _predict_optimal_timing(self, model: Dict, features: np.ndarray) -> Dict[str, Any]:
        """Prédiction timing avec modèle ML."""
        # Simulation prédiction ML
        score = np.dot(features[:len(model['weights'])], model['weights'].flatten()) + model['bias']
        
        # Conversion score en heure optimale
        optimal_hour = int(abs(score) % 24)
        optimal_time = datetime.now().replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
        
        return {
            'optimal_time': optimal_time,
            'overlap_risk': min(abs(score) * 0.1, 1.0),
            'expected_engagement': min(abs(score) * 0.05, 1.0)
        }
    
    async def _calculate_confidence_score(
        self,
        prediction: Dict[str, Any],
        features: np.ndarray,
        platform: str
    ) -> float:
        """Calcul score de confiance."""
        base_confidence = 0.7
        
        # Ajustement selon données disponibles
        feature_quality = min(len(features) / 10.0, 1.0)
        
        # Ajustement selon historique plateforme
        platform_reliability = 0.8  # En production, basé sur historique réel
        
        return min(base_confidence * feature_quality * platform_reliability, 1.0)
    
    def _calculate_audience_overlap(
        self,
        platform1: str,
        platform2: str,
        audience_data: AudienceData
    ) -> float:
        """Calcul overlap audience entre plateformes."""
        # Simulation overlap basé sur préférences plateforme
        platform_prefs = audience_data.platform_preferences
        
        p1_score = platform_prefs.get(platform1, 0.5)
        p2_score = platform_prefs.get(platform2, 0.5)
        
        # Overlap estimé
        overlap = min(p1_score, p2_score) / max(p1_score, p2_score, 0.1)
        return overlap
    
    async def _fallback_timing_strategy(
        self,
        target_platforms: List[str],
        audience_data: AudienceData
    ) -> Dict[str, SchedulingResult]:
        """Stratégie fallback en cas d'erreur ML."""
        results = {}
        
        for platform in target_platforms:
            # Timing basé sur peak activity hours
            peak_hour = audience_data.peak_activity_hours[0] if audience_data.peak_activity_hours else 12
            optimal_time = datetime.now().replace(hour=peak_hour, minute=0, second=0, microsecond=0)
            
            results[platform] = SchedulingResult(
                platform=platform,
                optimal_time=optimal_time,
                confidence_score=0.6,
                strategy_used=TimingStrategy.AUDIENCE_BASED,
                audience_overlap_risk=0.3,
                expected_engagement=0.5,
                reasoning="Fallback strategy based on peak activity hours"
            )
            
        return results

class CompetitorActivityTracker:
    """Tracker activité concurrents."""
    
    def __init__(self):
        self.activity_cache = defaultdict(list)
    
    async def get_competitor_schedule(
        self,
        competitor_ids: List[str],
        platform: str,
        niche: str
    ) -> List[Dict[str, Any]]:
        """Récupération planning concurrents."""
        # Simulation données concurrents
        activities = []
        
        for competitor_id in competitor_ids:
            # En production, récupérer données réelles via APIs
            activity = {
                'competitor_id': competitor_id,
                'platform': platform,
                'scheduled_times': [
                    datetime.now() + timedelta(hours=i) for i in range(1, 25, 3)
                ],
                'content_frequency': 3,
                'engagement_peak_hours': [9, 14, 20]
            }
            activities.append(activity)
            
        return activities