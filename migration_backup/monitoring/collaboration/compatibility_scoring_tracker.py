"""
Ainflue Platform - Compatibility Scoring Tracker
=================================================

Advanced compatibility scoring system for measuring and tracking creator
compatibility across multiple dimensions with ML-powered insights and
real-time scoring optimization for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque
import json
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd

logger = logging.getLogger(__name__)

class CompatibilityDimension(Enum):
    """Dimensions for compatibility scoring."""
    CREATIVE_STYLE = "creative_style"
    TECHNICAL_SKILLS = "technical_skills"
    WORK_SCHEDULE = "work_schedule"
    COMMUNICATION_STYLE = "communication_style"
    AUDIENCE_DEMOGRAPHICS = "audience_demographics"
    CONTENT_THEMES = "content_themes"
    COLLABORATION_HISTORY = "collaboration_history"
    PERSONALITY_TRAITS = "personality_traits"
    PRODUCTION_QUALITY = "production_quality"
    COMMERCIAL_ALIGNMENT = "commercial_alignment"
    CULTURAL_FIT = "cultural_fit"
    GEOGRAPHICAL_PROXIMITY = "geographical_proximity"

class ScoreCategory(Enum):
    """Score categories for compatibility."""
    EXCELLENT = "excellent"          # 90-100%
    VERY_GOOD = "very_good"         # 80-89%
    GOOD = "good"                   # 70-79%
    MODERATE = "moderate"           # 60-69%
    LOW = "low"                     # 40-59%
    VERY_LOW = "very_low"           # 0-39%

@dataclass
class CompatibilityVector:
    """Compatibility vector for a creator."""
    creator_id: str
    creative_style_vector: np.ndarray
    technical_skills_vector: np.ndarray
    schedule_vector: np.ndarray
    communication_vector: np.ndarray
    audience_vector: np.ndarray
    content_themes_vector: np.ndarray
    personality_vector: np.ndarray
    quality_vector: np.ndarray
    commercial_vector: np.ndarray
    cultural_vector: np.ndarray
    geographical_vector: np.ndarray
    last_updated: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0

@dataclass
class CompatibilityScore:
    """Individual compatibility score."""
    creator_a_id: str
    creator_b_id: str
    dimension: CompatibilityDimension
    score: float
    confidence: float
    calculation_method: str
    factors: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OverallCompatibility:
    """Overall compatibility assessment."""
    creator_a_id: str
    creator_b_id: str
    overall_score: float
    category: ScoreCategory
    dimension_scores: Dict[CompatibilityDimension, float]
    confidence_interval: Tuple[float, float]
    key_strengths: List[str]
    potential_challenges: List[str]
    recommendations: List[str]
    collaboration_potential: float
    risk_factors: List[str]
    success_probability: float
    timestamp: datetime = field(default_factory=datetime.now)

class CompatibilityScoringTracker:
    """
    Advanced compatibility scoring tracker for creator matching.
    
    Features:
    - Multi-dimensional compatibility analysis
    - ML-powered scoring algorithms
    - Real-time score tracking and updates
    - Confidence interval calculations
    - Historical compatibility trends
    - Collaborative filtering integration
    - Personalized scoring weights
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.compatibility_scores: Dict[str, CompatibilityScore] = {}
        self.creator_vectors: Dict[str, CompatibilityVector] = {}
        self.overall_compatibilities: Dict[str, OverallCompatibility] = {}
        self.scoring_history: defaultdict = defaultdict(deque)
        self.dimension_weights: Dict[CompatibilityDimension, float] = {}
        self.ml_models: Dict[str, Any] = {}
        self.scaler = StandardScaler()
        self.kmeans_clusterer = KMeans(n_clusters=10, random_state=42)
        self.pca_reducer = PCA(n_components=50)
        
        # Initialize dimension weights
        self._initialize_dimension_weights()
        
        # ML models initialization
        self._initialize_ml_models()
        
        # Performance metrics
        self.metrics = {
            'total_scores_calculated': 0,
            'average_calculation_time': 0.0,
            'score_accuracy': 0.0,
            'prediction_confidence': 0.0,
            'successful_matches': 0,
            'failed_matches': 0
        }
        
        logger.info("CompatibilityScoringTracker initialized")

    def _initialize_dimension_weights(self):
        """Initialize dimension weights based on importance."""
        self.dimension_weights = {
            CompatibilityDimension.CREATIVE_STYLE: 0.15,
            CompatibilityDimension.TECHNICAL_SKILLS: 0.12,
            CompatibilityDimension.WORK_SCHEDULE: 0.10,
            CompatibilityDimension.COMMUNICATION_STYLE: 0.13,
            CompatibilityDimension.AUDIENCE_DEMOGRAPHICS: 0.11,
            CompatibilityDimension.CONTENT_THEMES: 0.14,
            CompatibilityDimension.COLLABORATION_HISTORY: 0.08,
            CompatibilityDimension.PERSONALITY_TRAITS: 0.09,
            CompatibilityDimension.PRODUCTION_QUALITY: 0.05,
            CompatibilityDimension.COMMERCIAL_ALIGNMENT: 0.02,
            CompatibilityDimension.CULTURAL_FIT: 0.01,
            CompatibilityDimension.GEOGRAPHICAL_PROXIMITY: 0.00
        }

    def _initialize_ml_models(self):
        """Initialize ML models for compatibility scoring."""
        try:
            # Placeholder for actual ML model loading
            self.ml_models = {
                'compatibility_predictor': None,
                'success_predictor': None,
                'risk_assessor': None,
                'recommendation_engine': None
            }
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")

    async def calculate_compatibility_score(
        self,
        creator_a_id: str,
        creator_b_id: str,
        dimension: CompatibilityDimension,
        data_a: Dict[str, Any],
        data_b: Dict[str, Any]
    ) -> CompatibilityScore:
        """Calculate compatibility score for specific dimension."""
        try:
            start_time = datetime.now()
            
            # Extract relevant features for the dimension
            features_a = self._extract_dimension_features(data_a, dimension)
            features_b = self._extract_dimension_features(data_b, dimension)
            
            # Calculate similarity score
            score = self._calculate_similarity_score(features_a, features_b, dimension)
            
            # Calculate confidence
            confidence = self._calculate_confidence(features_a, features_b, dimension)
            
            # Determine calculation method
            method = self._get_calculation_method(dimension)
            
            # Extract contributing factors
            factors = self._analyze_contributing_factors(features_a, features_b, dimension)
            
            compatibility_score = CompatibilityScore(
                creator_a_id=creator_a_id,
                creator_b_id=creator_b_id,
                dimension=dimension,
                score=score,
                confidence=confidence,
                calculation_method=method,
                factors=factors
            )
            
            # Store score
            score_key = f"{creator_a_id}_{creator_b_id}_{dimension.value}"
            self.compatibility_scores[score_key] = compatibility_score
            
            # Update history
            self.scoring_history[score_key].append({
                'score': score,
                'confidence': confidence,
                'timestamp': datetime.now()
            })
            
            # Update metrics
            calculation_time = (datetime.now() - start_time).total_seconds()
            self._update_calculation_metrics(calculation_time)
            
            logger.info(f"Calculated compatibility score: {score:.3f} for {dimension.value}")
            return compatibility_score
            
        except Exception as e:
            logger.error(f"Error calculating compatibility score: {e}")
            raise

    def _extract_dimension_features(
        self,
        creator_data: Dict[str, Any],
        dimension: CompatibilityDimension
    ) -> np.ndarray:
        """Extract features for specific compatibility dimension."""
        try:
            if dimension == CompatibilityDimension.CREATIVE_STYLE:
                return self._extract_creative_style_features(creator_data)
            elif dimension == CompatibilityDimension.TECHNICAL_SKILLS:
                return self._extract_technical_skills_features(creator_data)
            elif dimension == CompatibilityDimension.WORK_SCHEDULE:
                return self._extract_schedule_features(creator_data)
            elif dimension == CompatibilityDimension.COMMUNICATION_STYLE:
                return self._extract_communication_features(creator_data)
            elif dimension == CompatibilityDimension.AUDIENCE_DEMOGRAPHICS:
                return self._extract_audience_features(creator_data)
            elif dimension == CompatibilityDimension.CONTENT_THEMES:
                return self._extract_content_themes_features(creator_data)
            elif dimension == CompatibilityDimension.COLLABORATION_HISTORY:
                return self._extract_collaboration_history_features(creator_data)
            elif dimension == CompatibilityDimension.PERSONALITY_TRAITS:
                return self._extract_personality_features(creator_data)
            elif dimension == CompatibilityDimension.PRODUCTION_QUALITY:
                return self._extract_quality_features(creator_data)
            elif dimension == CompatibilityDimension.COMMERCIAL_ALIGNMENT:
                return self._extract_commercial_features(creator_data)
            elif dimension == CompatibilityDimension.CULTURAL_FIT:
                return self._extract_cultural_features(creator_data)
            elif dimension == CompatibilityDimension.GEOGRAPHICAL_PROXIMITY:
                return self._extract_geographical_features(creator_data)
            else:
                return np.zeros(10)  # Default feature vector
                
        except Exception as e:
            logger.error(f"Error extracting features for {dimension}: {e}")
            return np.zeros(10)

    def _extract_creative_style_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract creative style features."""
        features = []
        
        # Visual style preferences
        visual_style = data.get('visual_style', {})
        features.extend([
            visual_style.get('minimalism_score', 0.5),
            visual_style.get('color_vibrancy', 0.5),
            visual_style.get('composition_complexity', 0.5),
            visual_style.get('artistic_influence', 0.5)
        ])
        
        # Content style metrics
        content_style = data.get('content_style', {})
        features.extend([
            content_style.get('narrative_complexity', 0.5),
            content_style.get('humor_quotient', 0.5),
            content_style.get('emotional_intensity', 0.5),
            content_style.get('educational_component', 0.5)
        ])
        
        # Production approach
        production = data.get('production_approach', {})
        features.extend([
            production.get('planning_detail', 0.5),
            production.get('improvisation_tendency', 0.5)
        ])
        
        return np.array(features)

    def _extract_technical_skills_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract technical skills features."""
        features = []
        
        skills = data.get('technical_skills', {})
        features.extend([
            skills.get('video_editing_proficiency', 0.0),
            skills.get('audio_editing_proficiency', 0.0),
            skills.get('photography_skills', 0.0),
            skills.get('graphic_design_skills', 0.0),
            skills.get('animation_skills', 0.0),
            skills.get('streaming_technology', 0.0),
            skills.get('social_media_management', 0.0),
            skills.get('seo_optimization', 0.0),
            skills.get('analytics_interpretation', 0.0),
            skills.get('equipment_proficiency', 0.0)
        ])
        
        return np.array(features)

    def _extract_schedule_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract work schedule features."""
        features = []
        
        schedule = data.get('work_schedule', {})
        features.extend([
            schedule.get('hours_per_week', 20) / 40,  # Normalized
            schedule.get('flexibility_score', 0.5),
            schedule.get('timezone_offset', 0) / 24,  # Normalized
            schedule.get('weekend_availability', 0.5),
            schedule.get('evening_availability', 0.5),
            schedule.get('morning_availability', 0.5),
            schedule.get('deadline_adherence', 0.5),
            schedule.get('project_duration_preference', 0.5),
            schedule.get('collaboration_frequency_preference', 0.5),
            schedule.get('response_time_expectation', 0.5)
        ])
        
        return np.array(features)

    def _extract_communication_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract communication style features."""
        features = []
        
        comm = data.get('communication_style', {})
        features.extend([
            comm.get('formal_informal_ratio', 0.5),
            comm.get('detail_level_preference', 0.5),
            comm.get('feedback_directness', 0.5),
            comm.get('meeting_preference', 0.5),
            comm.get('written_vs_verbal', 0.5),
            comm.get('brainstorming_style', 0.5),
            comm.get('conflict_resolution_approach', 0.5),
            comm.get('decision_making_style', 0.5),
            comm.get('cultural_sensitivity', 0.5),
            comm.get('language_proficiency', 0.5)
        ])
        
        return np.array(features)

    def _extract_audience_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract audience demographics features."""
        features = []
        
        audience = data.get('audience_demographics', {})
        features.extend([
            audience.get('age_group_primary', 0.5),
            audience.get('gender_distribution', 0.5),
            audience.get('geographic_concentration', 0.5),
            audience.get('income_level', 0.5),
            audience.get('education_level', 0.5),
            audience.get('interests_diversity', 0.5),
            audience.get('engagement_level', 0.5),
            audience.get('platform_preference', 0.5),
            audience.get('content_consumption_habits', 0.5),
            audience.get('brand_loyalty', 0.5)
        ])
        
        return np.array(features)

    def _extract_content_themes_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract content themes features."""
        features = []
        
        themes = data.get('content_themes', {})
        features.extend([
            themes.get('entertainment_focus', 0.0),
            themes.get('educational_focus', 0.0),
            themes.get('lifestyle_focus', 0.0),
            themes.get('technology_focus', 0.0),
            themes.get('art_culture_focus', 0.0),
            themes.get('business_focus', 0.0),
            themes.get('health_wellness_focus', 0.0),
            themes.get('travel_focus', 0.0),
            themes.get('food_focus', 0.0),
            themes.get('music_focus', 0.0)
        ])
        
        return np.array(features)

    def _extract_collaboration_history_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract collaboration history features."""
        features = []
        
        history = data.get('collaboration_history', {})
        features.extend([
            min(history.get('total_collaborations', 0) / 50, 1.0),
            history.get('success_rate', 0.0),
            history.get('repeat_collaborations_ratio', 0.0),
            history.get('project_completion_rate', 0.0),
            history.get('average_collaboration_duration', 0.5),
            history.get('feedback_score', 0.5),
            history.get('reliability_score', 0.5),
            history.get('creativity_contribution', 0.5),
            history.get('technical_contribution', 0.5),
            history.get('leadership_tendency', 0.5)
        ])
        
        return np.array(features)

    def _extract_personality_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract personality traits features."""
        features = []
        
        personality = data.get('personality_traits', {})
        features.extend([
            personality.get('openness_to_experience', 0.5),
            personality.get('conscientiousness', 0.5),
            personality.get('extraversion', 0.5),
            personality.get('agreeableness', 0.5),
            personality.get('neuroticism', 0.5),
            personality.get('risk_tolerance', 0.5),
            personality.get('perfectionism', 0.5),
            personality.get('adaptability', 0.5),
            personality.get('leadership_style', 0.5),
            personality.get('stress_management', 0.5)
        ])
        
        return np.array(features)

    def _extract_quality_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract production quality features."""
        features = []
        
        quality = data.get('production_quality', {})
        features.extend([
            quality.get('video_quality_score', 0.5),
            quality.get('audio_quality_score', 0.5),
            quality.get('editing_sophistication', 0.5),
            quality.get('visual_aesthetics', 0.5),
            quality.get('content_structure', 0.5),
            quality.get('technical_innovation', 0.5),
            quality.get('consistency_score', 0.5),
            quality.get('equipment_quality', 0.5),
            quality.get('post_production_skills', 0.5),
            quality.get('attention_to_detail', 0.5)
        ])
        
        return np.array(features)

    def _extract_commercial_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract commercial alignment features."""
        features = []
        
        commercial = data.get('commercial_alignment', {})
        features.extend([
            commercial.get('monetization_focus', 0.5),
            commercial.get('brand_partnership_openness', 0.5),
            commercial.get('pricing_strategy', 0.5),
            commercial.get('business_acumen', 0.5),
            commercial.get('market_understanding', 0.5),
            commercial.get('growth_ambition', 0.5),
            commercial.get('revenue_diversification', 0.5),
            commercial.get('professional_network', 0.5),
            commercial.get('industry_connections', 0.5),
            commercial.get('investment_readiness', 0.5)
        ])
        
        return np.array(features)

    def _extract_cultural_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract cultural fit features."""
        features = []
        
        cultural = data.get('cultural_fit', {})
        features.extend([
            cultural.get('cultural_background', 0.5),
            cultural.get('language_skills', 0.5),
            cultural.get('cultural_sensitivity', 0.5),
            cultural.get('international_experience', 0.5),
            cultural.get('diversity_appreciation', 0.5),
            cultural.get('cross_cultural_communication', 0.5),
            cultural.get('global_mindset', 0.5),
            cultural.get('local_market_understanding', 0.5),
            cultural.get('cultural_adaptation', 0.5),
            cultural.get('inclusive_content_creation', 0.5)
        ])
        
        return np.array(features)

    def _extract_geographical_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract geographical proximity features."""
        features = []
        
        geo = data.get('geographical_info', {})
        features.extend([
            geo.get('latitude', 0.0) / 90,  # Normalized
            geo.get('longitude', 0.0) / 180,  # Normalized
            geo.get('timezone_offset', 0) / 24,  # Normalized
            geo.get('urban_rural_score', 0.5),
            geo.get('cost_of_living_index', 0.5),
            geo.get('internet_infrastructure', 0.5),
            geo.get('local_creator_scene', 0.5),
            geo.get('travel_accessibility', 0.5),
            geo.get('legal_framework', 0.5),
            geo.get('market_size', 0.5)
        ])
        
        return np.array(features)

    def _calculate_similarity_score(
        self,
        features_a: np.ndarray,
        features_b: np.ndarray,
        dimension: CompatibilityDimension
    ) -> float:
        """Calculate similarity score between two feature vectors."""
        try:
            # Handle empty or mismatched vectors
            if len(features_a) == 0 or len(features_b) == 0:
                return 0.0
            
            if len(features_a) != len(features_b):
                min_len = min(len(features_a), len(features_b))
                features_a = features_a[:min_len]
                features_b = features_b[:min_len]
            
            # Calculate different similarity metrics
            cosine_sim = self._cosine_similarity(features_a, features_b)
            euclidean_sim = self._euclidean_similarity(features_a, features_b)
            pearson_sim = self._pearson_similarity(features_a, features_b)
            
            # Weighted combination based on dimension
            if dimension in [CompatibilityDimension.CREATIVE_STYLE, CompatibilityDimension.CONTENT_THEMES]:
                # For creative dimensions, cosine similarity is most important
                score = 0.5 * cosine_sim + 0.3 * pearson_sim + 0.2 * euclidean_sim
            elif dimension in [CompatibilityDimension.TECHNICAL_SKILLS, CompatibilityDimension.PRODUCTION_QUALITY]:
                # For technical dimensions, euclidean similarity is key
                score = 0.5 * euclidean_sim + 0.3 * cosine_sim + 0.2 * pearson_sim
            else:
                # Balanced approach for other dimensions
                score = 0.4 * cosine_sim + 0.3 * euclidean_sim + 0.3 * pearson_sim
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating similarity score: {e}")
            return 0.0

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity."""
        try:
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
        except:
            return 0.0

    def _euclidean_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate euclidean similarity (inverted distance)."""
        try:
            distance = np.linalg.norm(a - b)
            max_distance = np.sqrt(len(a) * 2)  # Maximum possible distance
            return 1.0 - (distance / max_distance)
        except:
            return 0.0

    def _pearson_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate Pearson correlation coefficient."""
        try:
            correlation = np.corrcoef(a, b)[0, 1]
            if np.isnan(correlation):
                return 0.0
            return (correlation + 1) / 2  # Normalize to 0-1 range
        except:
            return 0.0

    def _calculate_confidence(
        self,
        features_a: np.ndarray,
        features_b: np.ndarray,
        dimension: CompatibilityDimension
    ) -> float:
        """Calculate confidence in the compatibility score."""
        try:
            # Base confidence on data quality and completeness
            completeness_a = np.mean(features_a > 0)
            completeness_b = np.mean(features_b > 0)
            data_completeness = (completeness_a + completeness_b) / 2
            
            # Variance in features (more variance = less confidence)
            variance_a = np.var(features_a)
            variance_b = np.var(features_b)
            variance_factor = 1.0 - min(variance_a + variance_b, 1.0)
            
            # Historical accuracy for this dimension
            historical_accuracy = self._get_historical_accuracy(dimension)
            
            # Combined confidence
            confidence = (
                0.4 * data_completeness +
                0.3 * variance_factor +
                0.3 * historical_accuracy
            )
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5

    def _get_historical_accuracy(self, dimension: CompatibilityDimension) -> float:
        """Get historical accuracy for dimension."""
        # Placeholder - would use actual historical data
        accuracy_map = {
            CompatibilityDimension.CREATIVE_STYLE: 0.85,
            CompatibilityDimension.TECHNICAL_SKILLS: 0.90,
            CompatibilityDimension.WORK_SCHEDULE: 0.80,
            CompatibilityDimension.COMMUNICATION_STYLE: 0.75,
            CompatibilityDimension.AUDIENCE_DEMOGRAPHICS: 0.88,
            CompatibilityDimension.CONTENT_THEMES: 0.82,
            CompatibilityDimension.COLLABORATION_HISTORY: 0.92,
            CompatibilityDimension.PERSONALITY_TRAITS: 0.70,
            CompatibilityDimension.PRODUCTION_QUALITY: 0.87,
            CompatibilityDimension.COMMERCIAL_ALIGNMENT: 0.78,
            CompatibilityDimension.CULTURAL_FIT: 0.65,
            CompatibilityDimension.GEOGRAPHICAL_PROXIMITY: 0.95
        }
        return accuracy_map.get(dimension, 0.75)

    def _get_calculation_method(self, dimension: CompatibilityDimension) -> str:
        """Get calculation method used for dimension."""
        method_map = {
            CompatibilityDimension.CREATIVE_STYLE: "hybrid_cosine_pearson",
            CompatibilityDimension.TECHNICAL_SKILLS: "euclidean_weighted",
            CompatibilityDimension.WORK_SCHEDULE: "temporal_overlap_analysis",
            CompatibilityDimension.COMMUNICATION_STYLE: "nlp_similarity_matrix",
            CompatibilityDimension.AUDIENCE_DEMOGRAPHICS: "demographic_clustering",
            CompatibilityDimension.CONTENT_THEMES: "semantic_similarity",
            CompatibilityDimension.COLLABORATION_HISTORY: "collaborative_filtering",
            CompatibilityDimension.PERSONALITY_TRAITS: "big_five_analysis",
            CompatibilityDimension.PRODUCTION_QUALITY: "quality_metric_comparison",
            CompatibilityDimension.COMMERCIAL_ALIGNMENT: "business_goal_alignment",
            CompatibilityDimension.CULTURAL_FIT: "cultural_distance_metric",
            CompatibilityDimension.GEOGRAPHICAL_PROXIMITY: "haversine_distance"
        }
        return method_map.get(dimension, "general_similarity")

    def _analyze_contributing_factors(
        self,
        features_a: np.ndarray,
        features_b: np.ndarray,
        dimension: CompatibilityDimension
    ) -> Dict[str, Any]:
        """Analyze factors contributing to compatibility score."""
        factors = {}
        
        try:
            # Feature similarity analysis
            feature_similarities = []
            for i in range(len(features_a)):
                if len(features_b) > i:
                    sim = 1.0 - abs(features_a[i] - features_b[i])
                    feature_similarities.append(sim)
            
            factors['feature_similarities'] = feature_similarities
            factors['top_matching_features'] = sorted(
                enumerate(feature_similarities),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            factors['divergent_features'] = sorted(
                enumerate(feature_similarities),
                key=lambda x: x[1]
            )[:3]
            
            # Statistical analysis
            factors['mean_similarity'] = np.mean(feature_similarities) if feature_similarities else 0.0
            factors['std_similarity'] = np.std(feature_similarities) if feature_similarities else 0.0
            factors['consistency_score'] = 1.0 - factors['std_similarity']
            
        except Exception as e:
            logger.error(f"Error analyzing contributing factors: {e}")
        
        return factors

    async def calculate_overall_compatibility(
        self,
        creator_a_id: str,
        creator_b_id: str,
        creator_a_data: Dict[str, Any],
        creator_b_data: Dict[str, Any]
    ) -> OverallCompatibility:
        """Calculate overall compatibility between two creators."""
        try:
            dimension_scores = {}
            total_weighted_score = 0.0
            total_weight = 0.0
            
            # Calculate scores for all dimensions
            for dimension in CompatibilityDimension:
                score_obj = await self.calculate_compatibility_score(
                    creator_a_id, creator_b_id, dimension,
                    creator_a_data, creator_b_data
                )
                
                dimension_scores[dimension] = score_obj.score
                weight = self.dimension_weights.get(dimension, 0.0)
                total_weighted_score += score_obj.score * weight
                total_weight += weight
            
            # Calculate overall score
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Determine category
            category = self._determine_score_category(overall_score)
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(dimension_scores)
            
            # Generate insights
            key_strengths = self._identify_key_strengths(dimension_scores)
            potential_challenges = self._identify_potential_challenges(dimension_scores)
            recommendations = self._generate_recommendations(dimension_scores, creator_a_data, creator_b_data)
            
            # Calculate collaboration potential and success probability
            collaboration_potential = self._calculate_collaboration_potential(dimension_scores)
            risk_factors = self._identify_risk_factors(dimension_scores)
            success_probability = self._calculate_success_probability(dimension_scores, creator_a_data, creator_b_data)
            
            overall_compatibility = OverallCompatibility(
                creator_a_id=creator_a_id,
                creator_b_id=creator_b_id,
                overall_score=overall_score,
                category=category,
                dimension_scores=dimension_scores,
                confidence_interval=confidence_interval,
                key_strengths=key_strengths,
                potential_challenges=potential_challenges,
                recommendations=recommendations,
                collaboration_potential=collaboration_potential,
                risk_factors=risk_factors,
                success_probability=success_probability
            )
            
            # Store overall compatibility
            compatibility_key = f"{creator_a_id}_{creator_b_id}"
            self.overall_compatibilities[compatibility_key] = overall_compatibility
            
            logger.info(f"Calculated overall compatibility: {overall_score:.3f} ({category.value})")
            return overall_compatibility
            
        except Exception as e:
            logger.error(f"Error calculating overall compatibility: {e}")
            raise

    def _determine_score_category(self, score: float) -> ScoreCategory:
        """Determine score category based on score value."""
        if score >= 0.90:
            return ScoreCategory.EXCELLENT
        elif score >= 0.80:
            return ScoreCategory.VERY_GOOD
        elif score >= 0.70:
            return ScoreCategory.GOOD
        elif score >= 0.60:
            return ScoreCategory.MODERATE
        elif score >= 0.40:
            return ScoreCategory.LOW
        else:
            return ScoreCategory.VERY_LOW

    def _calculate_confidence_interval(self, dimension_scores: Dict[CompatibilityDimension, float]) -> Tuple[float, float]:
        """Calculate confidence interval for overall score."""
        scores = list(dimension_scores.values())
        if not scores:
            return (0.0, 0.0)
        
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        # 95% confidence interval
        margin = 1.96 * std_score / np.sqrt(len(scores))
        return (max(0.0, mean_score - margin), min(1.0, mean_score + margin))

    def _identify_key_strengths(self, dimension_scores: Dict[CompatibilityDimension, float]) -> List[str]:
        """Identify key compatibility strengths."""
        strengths = []
        
        # Sort dimensions by score
        sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
        
        for dimension, score in sorted_dimensions[:3]:
            if score >= 0.75:
                strength_descriptions = {
                    CompatibilityDimension.CREATIVE_STYLE: "Highly compatible creative approaches and artistic vision",
                    CompatibilityDimension.TECHNICAL_SKILLS: "Complementary technical expertise and skill sets",
                    CompatibilityDimension.WORK_SCHEDULE: "Excellent schedule alignment and availability overlap",
                    CompatibilityDimension.COMMUNICATION_STYLE: "Compatible communication preferences and styles",
                    CompatibilityDimension.AUDIENCE_DEMOGRAPHICS: "Strong audience overlap and cross-pollination potential",
                    CompatibilityDimension.CONTENT_THEMES: "Synergistic content themes and topic alignment",
                    CompatibilityDimension.COLLABORATION_HISTORY: "Proven track record of successful partnerships",
                    CompatibilityDimension.PERSONALITY_TRAITS: "Complementary personality traits and working styles",
                    CompatibilityDimension.PRODUCTION_QUALITY: "Matched production standards and quality expectations",
                    CompatibilityDimension.COMMERCIAL_ALIGNMENT: "Aligned business goals and monetization strategies",
                    CompatibilityDimension.CULTURAL_FIT: "Strong cultural compatibility and understanding",
                    CompatibilityDimension.GEOGRAPHICAL_PROXIMITY: "Favorable geographical location for collaboration"
                }
                strengths.append(strength_descriptions.get(dimension, f"Strong {dimension.value} compatibility"))
        
        return strengths

    def _identify_potential_challenges(self, dimension_scores: Dict[CompatibilityDimension, float]) -> List[str]:
        """Identify potential collaboration challenges."""
        challenges = []
        
        # Sort dimensions by score (lowest first)
        sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1])
        
        for dimension, score in sorted_dimensions[:3]:
            if score <= 0.50:
                challenge_descriptions = {
                    CompatibilityDimension.CREATIVE_STYLE: "Divergent creative approaches may require alignment",
                    CompatibilityDimension.TECHNICAL_SKILLS: "Technical skill gaps may need bridging",
                    CompatibilityDimension.WORK_SCHEDULE: "Schedule conflicts may impact collaboration timing",
                    CompatibilityDimension.COMMUNICATION_STYLE: "Communication style differences need attention",
                    CompatibilityDimension.AUDIENCE_DEMOGRAPHICS: "Limited audience overlap reduces cross-promotion value",
                    CompatibilityDimension.CONTENT_THEMES: "Content theme misalignment requires creative integration",
                    CompatibilityDimension.COLLABORATION_HISTORY: "Limited collaboration experience may slow initial phase",
                    CompatibilityDimension.PERSONALITY_TRAITS: "Personality differences require careful management",
                    CompatibilityDimension.PRODUCTION_QUALITY: "Production quality standards need alignment",
                    CompatibilityDimension.COMMERCIAL_ALIGNMENT: "Business goal differences require negotiation",
                    CompatibilityDimension.CULTURAL_FIT: "Cultural differences need consideration and respect",
                    CompatibilityDimension.GEOGRAPHICAL_PROXIMITY: "Distance may complicate logistics and coordination"
                }
                challenges.append(challenge_descriptions.get(dimension, f"Challenges in {dimension.value} alignment"))
        
        return challenges

    def _generate_recommendations(
        self,
        dimension_scores: Dict[CompatibilityDimension, float],
        creator_a_data: Dict[str, Any],
        creator_b_data: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for successful collaboration."""
        recommendations = []
        
        # Analyze dimension scores and provide specific recommendations
        for dimension, score in dimension_scores.items():
            if score <= 0.60:  # Low compatibility requires specific recommendations
                if dimension == CompatibilityDimension.COMMUNICATION_STYLE:
                    recommendations.append("Establish clear communication protocols and preferred channels")
                elif dimension == CompatibilityDimension.WORK_SCHEDULE:
                    recommendations.append("Create shared calendar and define core collaboration hours")
                elif dimension == CompatibilityDimension.CREATIVE_STYLE:
                    recommendations.append("Conduct creative alignment sessions and style harmonization")
                elif dimension == CompatibilityDimension.TECHNICAL_SKILLS:
                    recommendations.append("Provide cross-training or skill-sharing sessions")
        
        # General recommendations based on overall compatibility
        overall_score = np.mean(list(dimension_scores.values()))
        if overall_score >= 0.80:
            recommendations.append("Excellent compatibility - proceed with confidence")
        elif overall_score >= 0.60:
            recommendations.append("Good foundation - address specific challenges proactively")
        else:
            recommendations.append("Consider alternative partners or extensive preparation")
        
        return recommendations[:5]  # Limit to top 5 recommendations

    def _calculate_collaboration_potential(self, dimension_scores: Dict[CompatibilityDimension, float]) -> float:
        """Calculate overall collaboration potential."""
        # Weight key dimensions more heavily for collaboration potential
        key_weights = {
            CompatibilityDimension.CREATIVE_STYLE: 0.25,
            CompatibilityDimension.COMMUNICATION_STYLE: 0.20,
            CompatibilityDimension.WORK_SCHEDULE: 0.15,
            CompatibilityDimension.COLLABORATION_HISTORY: 0.15,
            CompatibilityDimension.PERSONALITY_TRAITS: 0.10,
            CompatibilityDimension.TECHNICAL_SKILLS: 0.15
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for dimension, weight in key_weights.items():
            if dimension in dimension_scores:
                weighted_score += dimension_scores[dimension] * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _identify_risk_factors(self, dimension_scores: Dict[CompatibilityDimension, float]) -> List[str]:
        """Identify risk factors for collaboration."""
        risk_factors = []
        
        # High-risk dimensions
        high_risk_threshold = 0.40
        critical_dimensions = [
            CompatibilityDimension.COMMUNICATION_STYLE,
            CompatibilityDimension.WORK_SCHEDULE,
            CompatibilityDimension.COLLABORATION_HISTORY,
            CompatibilityDimension.PERSONALITY_TRAITS
        ]
        
        for dimension in critical_dimensions:
            if dimension in dimension_scores and dimension_scores[dimension] <= high_risk_threshold:
                risk_map = {
                    CompatibilityDimension.COMMUNICATION_STYLE: "Communication breakdown risk",
                    CompatibilityDimension.WORK_SCHEDULE: "Scheduling conflict risk",
                    CompatibilityDimension.COLLABORATION_HISTORY: "Inexperience risk",
                    CompatibilityDimension.PERSONALITY_TRAITS: "Personality conflict risk"
                }
                risk_factors.append(risk_map.get(dimension, f"{dimension.value} risk"))
        
        return risk_factors

    def _calculate_success_probability(
        self,
        dimension_scores: Dict[CompatibilityDimension, float],
        creator_a_data: Dict[str, Any],
        creator_b_data: Dict[str, Any]
    ) -> float:
        """Calculate probability of collaboration success."""
        # Base probability on dimension scores
        base_probability = np.mean(list(dimension_scores.values()))
        
        # Adjust based on historical data
        history_a = creator_a_data.get('collaboration_history', {})
        history_b = creator_b_data.get('collaboration_history', {})
        
        success_rate_a = history_a.get('success_rate', 0.5)
        success_rate_b = history_b.get('success_rate', 0.5)
        historical_factor = (success_rate_a + success_rate_b) / 2
        
        # Combine base probability with historical factor
        success_probability = 0.7 * base_probability + 0.3 * historical_factor
        
        return max(0.0, min(1.0, success_probability))

    def _update_calculation_metrics(self, calculation_time: float):
        """Update performance metrics."""
        self.metrics['total_scores_calculated'] += 1
        
        # Update average calculation time
        current_avg = self.metrics['average_calculation_time']
        total_calcs = self.metrics['total_scores_calculated']
        new_avg = ((current_avg * (total_calcs - 1)) + calculation_time) / total_calcs
        self.metrics['average_calculation_time'] = new_avg

    async def get_compatibility_trends(
        self,
        creator_a_id: str,
        creator_b_id: str,
        dimension: Optional[CompatibilityDimension] = None
    ) -> Dict[str, Any]:
        """Get compatibility trends over time."""
        try:
            if dimension:
                score_key = f"{creator_a_id}_{creator_b_id}_{dimension.value}"
                history = list(self.scoring_history.get(score_key, []))
            else:
                # Aggregate trends across all dimensions
                history = []
                for dim in CompatibilityDimension:
                    score_key = f"{creator_a_id}_{creator_b_id}_{dim.value}"
                    dim_history = list(self.scoring_history.get(score_key, []))
                    history.extend(dim_history)
                
                # Sort by timestamp
                history.sort(key=lambda x: x['timestamp'])
            
            if not history:
                return {'trend': 'no_data', 'data_points': 0}
            
            # Analyze trends
            scores = [point['score'] for point in history]
            timestamps = [point['timestamp'] for point in history]
            
            trend_analysis = {
                'data_points': len(history),
                'score_range': (min(scores), max(scores)),
                'latest_score': scores[-1],
                'score_variance': np.var(scores),
                'trend_direction': self._calculate_trend_direction(scores),
                'stability': self._calculate_stability(scores),
                'improvement_rate': self._calculate_improvement_rate(scores, timestamps)
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error getting compatibility trends: {e}")
            return {'error': str(e)}

    def _calculate_trend_direction(self, scores: List[float]) -> str:
        """Calculate overall trend direction."""
        if len(scores) < 2:
            return 'insufficient_data'
        
        # Simple linear trend
        recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
        early_avg = np.mean(scores[:3]) if len(scores) >= 3 else scores[0]
        
        if recent_avg > early_avg + 0.05:
            return 'improving'
        elif recent_avg < early_avg - 0.05:
            return 'declining'
        else:
            return 'stable'

    def _calculate_stability(self, scores: List[float]) -> float:
        """Calculate score stability (inverse of variance)."""
        if len(scores) < 2:
            return 1.0
        
        variance = np.var(scores)
        stability = 1.0 / (1.0 + variance)
        return stability

    def _calculate_improvement_rate(self, scores: List[float], timestamps: List[datetime]) -> float:
        """Calculate rate of improvement per day."""
        if len(scores) < 2:
            return 0.0
        
        # Calculate slope of improvement over time
        time_diffs = [(timestamps[i] - timestamps[0]).days for i in range(len(timestamps))]
        
        if max(time_diffs) == 0:
            return 0.0
        
        # Simple linear regression slope
        n = len(scores)
        sum_xy = sum(time_diffs[i] * scores[i] for i in range(n))
        sum_x = sum(time_diffs)
        sum_y = sum(scores)
        sum_x2 = sum(x**2 for x in time_diffs)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        return slope

    async def update_dimension_weights(self, new_weights: Dict[CompatibilityDimension, float]):
        """Update dimension weights for compatibility calculation."""
        try:
            # Validate weights sum to 1.0
            total_weight = sum(new_weights.values())
            if abs(total_weight - 1.0) > 0.01:
                logger.warning(f"Weights sum to {total_weight}, normalizing")
                normalized_weights = {dim: weight/total_weight for dim, weight in new_weights.items()}
                self.dimension_weights.update(normalized_weights)
            else:
                self.dimension_weights.update(new_weights)
            
            logger.info("Dimension weights updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating dimension weights: {e}")
            raise

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get tracker performance metrics."""
        try:
            return {
                'total_scores_calculated': self.metrics['total_scores_calculated'],
                'average_calculation_time': self.metrics['average_calculation_time'],
                'score_accuracy': self.metrics['score_accuracy'],
                'prediction_confidence': self.metrics['prediction_confidence'],
                'successful_matches': self.metrics['successful_matches'],
                'failed_matches': self.metrics['failed_matches'],
                'success_rate': (
                    self.metrics['successful_matches'] / 
                    (self.metrics['successful_matches'] + self.metrics['failed_matches'])
                    if (self.metrics['successful_matches'] + self.metrics['failed_matches']) > 0 else 0.0
                ),
                'total_compatibilities_tracked': len(self.overall_compatibilities),
                'dimension_weights': self.dimension_weights
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {'error': str(e)}

    async def export_compatibility_data(self, format: str = 'json') -> str:
        """Export compatibility data for analysis."""
        try:
            data = {
                'compatibility_scores': {
                    key: {
                        'creator_a_id': score.creator_a_id,
                        'creator_b_id': score.creator_b_id,
                        'dimension': score.dimension.value,
                        'score': score.score,
                        'confidence': score.confidence,
                        'timestamp': score.timestamp.isoformat()
                    }
                    for key, score in self.compatibility_scores.items()
                },
                'overall_compatibilities': {
                    key: {
                        'creator_a_id': comp.creator_a_id,
                        'creator_b_id': comp.creator_b_id,
                        'overall_score': comp.overall_score,
                        'category': comp.category.value,
                        'dimension_scores': {dim.value: score for dim, score in comp.dimension_scores.items()},
                        'success_probability': comp.success_probability,
                        'timestamp': comp.timestamp.isoformat()
                    }
                    for key, comp in self.overall_compatibilities.items()
                }
            }
            
            if format == 'json':
                return json.dumps(data, indent=2)
            elif format == 'pickle':
                return pickle.dumps(data)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting compatibility data: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    async def test_compatibility_scoring():
        """Test compatibility scoring functionality."""
        tracker = CompatibilityScoringTracker()
        
        # Sample creator data
        creator_a_data = {
            'creative_style': {
                'minimalism_score': 0.8,
                'color_vibrancy': 0.6,
                'composition_complexity': 0.7,
                'artistic_influence': 0.5
            },
            'technical_skills': {
                'video_editing_proficiency': 0.9,
                'audio_editing_proficiency': 0.7,
                'photography_skills': 0.8
            },
            'collaboration_history': {
                'total_collaborations': 15,
                'success_rate': 0.87
            }
        }
        
        creator_b_data = {
            'creative_style': {
                'minimalism_score': 0.7,
                'color_vibrancy': 0.8,
                'composition_complexity': 0.6,
                'artistic_influence': 0.6
            },
            'technical_skills': {
                'video_editing_proficiency': 0.8,
                'audio_editing_proficiency': 0.9,
                'photography_skills': 0.7
            },
            'collaboration_history': {
                'total_collaborations': 22,
                'success_rate': 0.91
            }
        }
        
        # Test compatibility scoring
        try:
            # Calculate overall compatibility
            compatibility = await tracker.calculate_overall_compatibility(
                "creator_001", "creator_002", creator_a_data, creator_b_data
            )
            
            print(f"Overall Compatibility Score: {compatibility.overall_score:.3f}")
            print(f"Category: {compatibility.category.value}")
            print(f"Success Probability: {compatibility.success_probability:.3f}")
            print("\nKey Strengths:")
            for strength in compatibility.key_strengths:
                print(f"  - {strength}")
            
            print("\nRecommendations:")
            for rec in compatibility.recommendations:
                print(f"  - {rec}")
            
            # Get performance metrics
            metrics = await tracker.get_performance_metrics()
            print(f"\nPerformance Metrics: {metrics}")
            
        except Exception as e:
            print(f"Error in test: {e}")
    
    # Run test
    asyncio.run(test_compatibility_scoring())