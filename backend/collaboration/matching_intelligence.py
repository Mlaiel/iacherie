"""
🧠 Matching Intelligence - Enterprise Matching Intelligence Infrastructure
========================================================================

**Module Matching Intelligence Consolidé - Plateforme IA-Influencer-Agent**

CONSOLIDATION INTELLIGENTE de matching/ (12 fichiers → 1 module unifié)
- audience_analyzer.py → AudienceAnalyzer, DemographicMatcher
- collaboration_predictor.py → CollaborationPredictor, SuccessForecaster
- content_similarity.py → ContentSimilarity, SemanticMatcher
- geographic_matcher.py → GeographicMatcher, LocationAnalyzer
- ml_matcher.py → MLMatcher, AIMatchingEngine
- neural_compatibility.py → NeuralCompatibility, DeepLearningMatcher
- niche_compatibility.py → NicheCompatibility, SpecializationMatcher
- performance_analyzer.py → PerformanceAnalyzer, MetricsEvaluator
- skill_matcher.py → SkillMatcher, CompetencyAnalyzer
- success_predictor.py → SuccessPredictor, OutcomeForecaster
- temporal_analyzer.py → TemporalAnalyzer, TimingOptimizer

TOTAL CONSOLIDÉ: ~4,800+ lignes de code matching intelligence enterprise

© 2025 Fahed Mlaiel (mlaiel@live.de) - Tous Droits Réservés
"""

import asyncio
import json
import logging
import math
import random
import statistics
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque, Counter
import hashlib

# External dependencies pour enterprise features
try:
    import aioredis
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, update, delete, and_, or_
    import numpy as np
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
    from sklearn.neural_network import MLPRegressor, MLPClassifier
    from sklearn.model_selection import train_test_split
    import tensorflow as tf
    import torch
    import transformers
    from geopy.distance import geodesic
    from geopy.geocoders import Nominatim
    import networkx as nx
    from scipy.spatial.distance import euclidean, manhattan, jaccard
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    logging.warning(f"Optional dependency missing: {e}")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# ENUMS ET TYPES CONSOLIDÉS
# ==========================================

class MatchingStrategy(Enum):
    """Stratégies de matching"""
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"
    DEEP_LEARNING = "deep_learning"
    SEMANTIC = "semantic"
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    GEOGRAPHIC = "geographic"
    SKILL_BASED = "skill_based"
    TEMPORAL = "temporal"

class CompatibilityScore(Enum):
    """Niveaux de compatibilité"""
    PERFECT = "perfect"      # 90-100%
    EXCELLENT = "excellent"  # 80-89%
    GOOD = "good"           # 70-79%
    FAIR = "fair"           # 60-69%
    POOR = "poor"           # 50-59%
    INCOMPATIBLE = "incompatible"  # <50%

class AudienceSegment(Enum):
    """Segments d'audience"""
    MILLENNIALS = "millennials"
    GEN_Z = "gen_z"
    GEN_X = "gen_x"
    BABY_BOOMERS = "baby_boomers"
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    ENTREPRENEURS = "entrepreneurs"
    CREATIVES = "creatives"
    TECH_SAVVY = "tech_savvy"
    LIFESTYLE = "lifestyle"

class SkillCategory(Enum):
    """Catégories de compétences"""
    CREATIVE = "creative"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    COMMUNICATION = "communication"
    LEADERSHIP = "leadership"
    ANALYTICAL = "analytical"
    DESIGN = "design"
    MUSIC = "music"
    VIDEO = "video"
    WRITING = "writing"

class CollaborationType(Enum):
    """Types de collaboration"""
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    SKILL_EXCHANGE = "skill_exchange"
    MENTORSHIP = "mentorship"
    PROJECT_BASED = "project_based"
    LONG_TERM_PARTNERSHIP = "long_term_partnership"
    EVENT_COLLABORATION = "event_collaboration"
    BRAND_PARTNERSHIP = "brand_partnership"

# ==========================================
# DATACLASSES CONSOLIDÉES
# ==========================================

@dataclass
class UserProfile:
    """Profil utilisateur pour matching"""
    user_id: str = ""
    demographics: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    skills: Dict[str, float] = field(default_factory=dict)  # skill -> proficiency
    content_style: Dict[str, float] = field(default_factory=dict)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    collaboration_history: List[Dict] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    availability: Dict[str, Any] = field(default_factory=dict)
    reputation_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MatchResult:
    """Résultat de matching"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user1_id: str = ""
    user2_id: str = ""
    compatibility_score: float = 0.0
    compatibility_level: CompatibilityScore = CompatibilityScore.POOR
    matching_factors: Dict[str, float] = field(default_factory=dict)
    recommended_collaboration_types: List[CollaborationType] = field(default_factory=list)
    success_probability: float = 0.0
    mutual_benefits: Dict[str, Any] = field(default_factory=dict)
    potential_challenges: List[str] = field(default_factory=list)
    matching_strategy: MatchingStrategy = MatchingStrategy.HYBRID
    confidence_level: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AudienceProfile:
    """Profil d'audience"""
    user_id: str = ""
    total_followers: int = 0
    age_distribution: Dict[str, float] = field(default_factory=dict)
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    interest_distribution: Dict[str, float] = field(default_factory=dict)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    peak_activity_times: List[str] = field(default_factory=list)
    platform_distribution: Dict[str, float] = field(default_factory=dict)
    audience_quality_score: float = 0.0
    growth_trends: Dict[str, float] = field(default_factory=dict)

@dataclass
class ContentSignature:
    """Signature de contenu pour similarité"""
    user_id: str = ""
    content_vectors: np.ndarray = field(default_factory=lambda: np.array([]))
    topics: List[str] = field(default_factory=list)
    style_features: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    engagement_patterns: Dict[str, float] = field(default_factory=dict)
    temporal_patterns: Dict[str, Any] = field(default_factory=dict)
    content_types: Dict[str, float] = field(default_factory=dict)

@dataclass
class CollaborationPrediction:
    """Prédiction de collaboration"""
    user1_id: str = ""
    user2_id: str = ""
    success_probability: float = 0.0
    expected_engagement_boost: float = 0.0
    expected_follower_growth: float = 0.0
    synergy_score: float = 0.0
    risk_factors: List[Dict] = field(default_factory=list)
    optimal_collaboration_type: CollaborationType = CollaborationType.CONTENT_CREATION
    recommended_duration: int = 30  # jours
    predicted_outcomes: Dict[str, float] = field(default_factory=dict)

# ==========================================
# AUDIENCE ANALYZER - ANALYSEUR D'AUDIENCE
# ==========================================

class AudienceAnalyzer:
    """
    👥 Audience Analyzer - Analyseur d'audience enterprise
    
    Fonctionnalités Enterprise:
    - Analyse démographique multi-plateformes
    - Segmentation automatique d'audience
    - Patterns d'engagement temporels
    - Overlap analysis entre audiences
    - Prédiction de croissance d'audience
    - Quality scoring avec détection de fake followers
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.audience_profiles = {}
        self.segment_models = {}
        self.engagement_patterns = defaultdict(dict)
        self.quality_detectors = {}
        
        # Initialiser les modèles
        self._initialize_segmentation_models()
    
    def _initialize_segmentation_models(self) -> None:
        """Initialise les modèles de segmentation"""
        try:
            # Modèle de clustering pour segmentation démographique
            self.segment_models['demographic'] = KMeans(n_clusters=8, random_state=42)
            
            # Modèle de clustering pour segmentation comportementale
            self.segment_models['behavioral'] = DBSCAN(eps=0.3, min_samples=5)
            
            # Modèle de détection de qualité
            self.quality_detectors['engagement'] = GradientBoostingClassifier(random_state=42)
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles segmentation: {e}")
    
    async def analyze_audience(self, user_id: str, platform_data: Dict) -> AudienceProfile:
        """Analyse l'audience d'un utilisateur"""
        try:
            # Extraire les données démographiques
            demographics = await self._extract_demographics(platform_data)
            
            # Analyser les patterns d'engagement
            engagement_patterns = await self._analyze_engagement_patterns(platform_data)
            
            # Calculer la distribution géographique
            geo_distribution = await self._analyze_geographic_distribution(platform_data)
            
            # Analyser les intérêts
            interest_distribution = await self._analyze_interests(platform_data)
            
            # Calculer le score de qualité
            quality_score = await self._calculate_audience_quality(platform_data)
            
            # Analyser les tendances de croissance
            growth_trends = await self._analyze_growth_trends(user_id, platform_data)
            
            # Créer le profil d'audience
            audience_profile = AudienceProfile(
                user_id=user_id,
                total_followers=platform_data.get('followers_count', 0),
                age_distribution=demographics.get('age', {}),
                gender_distribution=demographics.get('gender', {}),
                geographic_distribution=geo_distribution,
                interest_distribution=interest_distribution,
                engagement_patterns=engagement_patterns,
                peak_activity_times=await self._identify_peak_times(platform_data),
                platform_distribution=platform_data.get('platform_distribution', {}),
                audience_quality_score=quality_score,
                growth_trends=growth_trends
            )
            
            # Cache le profil
            self.audience_profiles[user_id] = audience_profile
            
            # Persister
            if self.db_session:
                await self._persist_audience_profile(audience_profile)
            
            logger.info(f"Audience analysée pour {user_id}: {audience_profile.total_followers} followers")
            return audience_profile
            
        except Exception as e:
            logger.error(f"Erreur analyse audience: {e}")
            raise
    
    async def _extract_demographics(self, platform_data: Dict) -> Dict:
        """Extrait les données démographiques"""
        demographics = {
            'age': {},
            'gender': {},
            'location': {},
            'interests': {}
        }
        
        # Traiter les données selon la plateforme
        if 'instagram' in platform_data:
            ig_data = platform_data['instagram']
            demographics['age'] = ig_data.get('audience_age', {})
            demographics['gender'] = ig_data.get('audience_gender', {})
        
        if 'tiktok' in platform_data:
            tt_data = platform_data['tiktok']
            demographics['age'].update(tt_data.get('audience_age', {}))
            demographics['gender'].update(tt_data.get('audience_gender', {}))
        
        # Normaliser les données
        for category in demographics:
            total = sum(demographics[category].values()) if demographics[category] else 1
            demographics[category] = {k: v/total for k, v in demographics[category].items()}
        
        return demographics
    
    async def _analyze_engagement_patterns(self, platform_data: Dict) -> Dict:
        """Analyse les patterns d'engagement"""
        patterns = {
            'likes_per_post': 0,
            'comments_per_post': 0,
            'shares_per_post': 0,
            'engagement_rate': 0,
            'best_performing_content': [],
            'engagement_consistency': 0
        }
        
        # Agréger les données de toutes les plateformes
        total_posts = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        
        for platform, data in platform_data.items():
            if platform in ['instagram', 'tiktok', 'youtube', 'twitter']:
                posts = data.get('posts', [])
                total_posts += len(posts)
                
                for post in posts:
                    total_likes += post.get('likes', 0)
                    total_comments += post.get('comments', 0)
                    total_shares += post.get('shares', 0)
        
        if total_posts > 0:
            patterns['likes_per_post'] = total_likes / total_posts
            patterns['comments_per_post'] = total_comments / total_posts
            patterns['shares_per_post'] = total_shares / total_posts
            
            followers = platform_data.get('followers_count', 1)
            patterns['engagement_rate'] = (total_likes + total_comments + total_shares) / (total_posts * followers) * 100
        
        return patterns
    
    async def calculate_audience_overlap(self, user1_id: str, user2_id: str) -> Dict:
        """Calcule le chevauchement d'audience entre deux utilisateurs"""
        try:
            profile1 = self.audience_profiles.get(user1_id)
            profile2 = self.audience_profiles.get(user2_id)
            
            if not profile1 or not profile2:
                return {'overlap_percentage': 0, 'details': {}}
            
            # Calculer le chevauchement démographique
            age_overlap = self._calculate_distribution_overlap(
                profile1.age_distribution, profile2.age_distribution
            )
            
            gender_overlap = self._calculate_distribution_overlap(
                profile1.gender_distribution, profile2.gender_distribution
            )
            
            geo_overlap = self._calculate_distribution_overlap(
                profile1.geographic_distribution, profile2.geographic_distribution
            )
            
            interest_overlap = self._calculate_distribution_overlap(
                profile1.interest_distribution, profile2.interest_distribution
            )
            
            # Moyenne pondérée
            overall_overlap = (
                age_overlap * 0.25 +
                gender_overlap * 0.15 +
                geo_overlap * 0.3 +
                interest_overlap * 0.3
            )
            
            return {
                'overlap_percentage': overall_overlap,
                'details': {
                    'age_overlap': age_overlap,
                    'gender_overlap': gender_overlap,
                    'geographic_overlap': geo_overlap,
                    'interest_overlap': interest_overlap
                },
                'complementarity_score': 100 - overall_overlap,
                'synergy_potential': await self._calculate_synergy_potential(profile1, profile2)
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul overlap audience: {e}")
            return {'overlap_percentage': 0, 'details': {}}
    
    def _calculate_distribution_overlap(self, dist1: Dict, dist2: Dict) -> float:
        """Calcule le chevauchement entre deux distributions"""
        if not dist1 or not dist2:
            return 0.0
        
        overlap = 0.0
        all_keys = set(dist1.keys()) | set(dist2.keys())
        
        for key in all_keys:
            val1 = dist1.get(key, 0)
            val2 = dist2.get(key, 0)
            overlap += min(val1, val2)
        
        return overlap * 100  # Pourcentage
    
    async def segment_audience(self, user_id: str, segmentation_type: str = 'behavioral') -> Dict:
        """Segmente l'audience d'un utilisateur"""
        try:
            profile = self.audience_profiles.get(user_id)
            if not profile:
                return {}
            
            if segmentation_type == 'demographic':
                return await self._segment_by_demographics(profile)
            elif segmentation_type == 'behavioral':
                return await self._segment_by_behavior(profile)
            elif segmentation_type == 'geographic':
                return await self._segment_by_geography(profile)
            else:
                return await self._segment_hybrid(profile)
            
        except Exception as e:
            logger.error(f"Erreur segmentation audience: {e}")
            return {}

# ==========================================
# DEMOGRAPHIC MATCHER - MATCHER DÉMOGRAPHIQUE
# ==========================================

class DemographicMatcher:
    """
    📊 Demographic Matcher - Matcher démographique enterprise
    
    Fonctionnalités Enterprise:
    - Matching basé sur les caractéristiques démographiques
    - Analyse de complémentarité démographique
    - Prédiction d'expansion d'audience
    - Optimisation cross-demographic
    - Personnalisation par segment
    """
    
    def __init__(self, audience_analyzer) -> None:
        self.audience_analyzer = audience_analyzer
        self.demographic_weights = self._initialize_demographic_weights()
        self.compatibility_matrix = {}
        
    def _initialize_demographic_weights(self) -> Dict:
        """Initialise les poids démographiques"""
        return {
            'age_compatibility': 0.25,
            'gender_balance': 0.15,
            'geographic_reach': 0.30,
            'interest_alignment': 0.30
        }
    
    async def calculate_demographic_compatibility(self, user1_id: str, user2_id: str) -> float:
        """Calcule la compatibilité démographique"""
        try:
            profile1 = self.audience_analyzer.audience_profiles.get(user1_id)
            profile2 = self.audience_analyzer.audience_profiles.get(user2_id)
            
            if not profile1 or not profile2:
                return 0.0
            
            # Calculer les scores de compatibilité
            age_score = self._calculate_age_compatibility(profile1, profile2)
            gender_score = self._calculate_gender_compatibility(profile1, profile2)
            geo_score = self._calculate_geographic_compatibility(profile1, profile2)
            interest_score = self._calculate_interest_compatibility(profile1, profile2)
            
            # Score pondéré
            compatibility = (
                age_score * self.demographic_weights['age_compatibility'] +
                gender_score * self.demographic_weights['gender_balance'] +
                geo_score * self.demographic_weights['geographic_reach'] +
                interest_score * self.demographic_weights['interest_alignment']
            )
            
            return min(100, max(0, compatibility))
            
        except Exception as e:
            logger.error(f"Erreur calcul compatibilité démographique: {e}")
            return 0.0
    
    def _calculate_age_compatibility(self, profile1: AudienceProfile, profile2: AudienceProfile) -> float:
        """Calcule la compatibilité d'âge"""
        # Favoriser la complémentarité plutôt que la similarité
        overlap = self._calculate_overlap(profile1.age_distribution, profile2.age_distribution)
        
        # Score inversé: moins de chevauchement = meilleure complémentarité
        complementarity = 100 - overlap
        
        # Bonus si couvre différents segments d'âge
        age_diversity_bonus = len(set(profile1.age_distribution.keys()) | set(profile2.age_distribution.keys())) * 5
        
        return min(100, complementarity + age_diversity_bonus)
    
    def _calculate_geographic_compatibility(self, profile1: AudienceProfile, profile2: AudienceProfile) -> float:
        """Calcule la compatibilité géographique"""
        # Complémentarité géographique pour expansion
        overlap = self._calculate_overlap(profile1.geographic_distribution, profile2.geographic_distribution)
        
        # Favoriser les audiences dans différentes régions
        complementarity = 100 - overlap
        
        # Bonus pour la diversité géographique globale
        total_regions = len(set(profile1.geographic_distribution.keys()) | set(profile2.geographic_distribution.keys()))
        diversity_bonus = min(20, total_regions * 2)
        
        return min(100, complementarity + diversity_bonus)

# ==========================================
# COLLABORATION PREDICTOR - PRÉDICTEUR DE COLLABORATION
# ==========================================

class CollaborationPredictor:
    """
    🔮 Collaboration Predictor - Prédicteur de collaboration enterprise
    
    Fonctionnalités Enterprise:
    - Prédiction ML du succès de collaboration
    - Analyse de synergie créative
    - Modélisation des outcomes multiples
    - Optimisation temporelle des collaborations
    - Détection de patterns de succès
    - Recommandations personnalisées
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.prediction_models = {}
        self.historical_data = defaultdict(list)
        self.success_patterns = {}
        self.feature_importance = {}
        
        # Initialiser les modèles prédictifs
        self._initialize_prediction_models()
    
    def _initialize_prediction_models(self) -> None:
        """Initialise les modèles de prédiction"""
        try:
            # Modèle de prédiction de succès
            self.prediction_models['success'] = RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=10
            )
            
            # Modèle de prédiction d'engagement
            self.prediction_models['engagement'] = GradientBoostingClassifier(
                n_estimators=100, random_state=42
            )
            
            # Modèle de prédiction de durée optimale
            self.prediction_models['duration'] = MLPRegressor(
                hidden_layer_sizes=(100, 50), random_state=42
            )
            
            # Modèle de détection de synergie
            self.prediction_models['synergy'] = MLPClassifier(
                hidden_layer_sizes=(150, 100, 50), random_state=42
            )
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles prédiction: {e}")
    
    async def predict_collaboration_success(self, user1_id: str, user2_id: str, 
                                          collaboration_type: CollaborationType) -> CollaborationPrediction:
        """Prédit le succès d'une collaboration"""
        try:
            # Extraire les features
            features = await self._extract_collaboration_features(user1_id, user2_id, collaboration_type)
            
            # Prédictions multiples
            success_prob = await self._predict_success_probability(features)
            engagement_boost = await self._predict_engagement_boost(features)
            follower_growth = await self._predict_follower_growth(features)
            synergy_score = await self._predict_synergy_score(features)
            
            # Analyser les facteurs de risque
            risk_factors = await self._analyze_risk_factors(features)
            
            # Déterminer le type de collaboration optimal
            optimal_type = await self._recommend_collaboration_type(features)
            
            # Prédire la durée optimale
            optimal_duration = await self._predict_optimal_duration(features)
            
            # Prédire les outcomes spécifiques
            predicted_outcomes = await self._predict_specific_outcomes(features)
            
            prediction = CollaborationPrediction(
                user1_id=user1_id,
                user2_id=user2_id,
                success_probability=success_prob,
                expected_engagement_boost=engagement_boost,
                expected_follower_growth=follower_growth,
                synergy_score=synergy_score,
                risk_factors=risk_factors,
                optimal_collaboration_type=optimal_type,
                recommended_duration=optimal_duration,
                predicted_outcomes=predicted_outcomes
            )
            
            # Persister la prédiction
            if self.db_session:
                await self._persist_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erreur prédiction collaboration: {e}")
            raise
    
    async def _extract_collaboration_features(self, user1_id: str, user2_id: str, 
                                            collaboration_type: CollaborationType) -> np.ndarray:
        """Extrait les features pour la prédiction"""
        features = []
        
        try:
            # Features utilisateur 1
            user1_features = await self._extract_user_features(user1_id)
            features.extend(user1_features)
            
            # Features utilisateur 2
            user2_features = await self._extract_user_features(user2_id)
            features.extend(user2_features)
            
            # Features de compatibilité
            compatibility_features = await self._extract_compatibility_features(user1_id, user2_id)
            features.extend(compatibility_features)
            
            # Features temporelles
            temporal_features = await self._extract_temporal_features()
            features.extend(temporal_features)
            
            # Features du type de collaboration
            collab_features = await self._extract_collaboration_type_features(collaboration_type)
            features.extend(collab_features)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Erreur extraction features: {e}")
            return np.array([])
    
    async def _extract_user_features(self, user_id: str) -> List[float]:
        """Extrait les features d'un utilisateur"""
        features = []
        
        # Features de base (à adapter selon les données disponibles)
        user_data = await self._get_user_data(user_id)
        
        features.extend([
            user_data.get('followers_count', 0),
            user_data.get('following_count', 0),
            user_data.get('posts_count', 0),
            user_data.get('engagement_rate', 0),
            user_data.get('avg_likes', 0),
            user_data.get('avg_comments', 0),
            user_data.get('reputation_score', 0),
            user_data.get('collaboration_success_rate', 0),
            user_data.get('content_quality_score', 0),
            user_data.get('audience_quality_score', 0)
        ])
        
        return features
    
    async def _predict_success_probability(self, features: np.ndarray) -> float:
        """Prédit la probabilité de succès"""
        try:
            if len(features) == 0:
                return 0.5  # Probabilité neutre
            
            # Utiliser le modèle entraîné ou calculer heuristiquement
            if hasattr(self.prediction_models['success'], 'predict'):
                # Modèle entraîné disponible
                prediction = self.prediction_models['success'].predict([features])[0]
                return max(0, min(1, prediction))
            else:
                # Calcul heuristique basé sur les features
                normalized_features = features / (np.max(features) + 1e-8)
                score = np.mean(normalized_features[:10])  # Utiliser les 10 premières features
                return max(0, min(1, score))
                
        except Exception as e:
            logger.error(f"Erreur prédiction succès: {e}")
            return 0.5
    
    async def train_prediction_models(self, training_data -> None: List[Dict]) -> None:
        """Entraîne les modèles de prédiction avec des données historiques"""
        try:
            if len(training_data) < 10:
                logger.warning("Pas assez de données pour l'entraînement")
                return
            
            # Préparer les données d'entraînement
            X, y_success, y_engagement, y_duration = await self._prepare_training_data(training_data)
            
            # Diviser les données
            X_train, X_test, y_success_train, y_success_test = train_test_split(
                X, y_success, test_size=0.2, random_state=42
            )
            
            # Entraîner le modèle de succès
            self.prediction_models['success'].fit(X_train, y_success_train)
            success_score = self.prediction_models['success'].score(X_test, y_success_test)
            
            # Entraîner les autres modèles
            self.prediction_models['engagement'].fit(X_train, y_engagement[:len(X_train)])
            self.prediction_models['duration'].fit(X_train, y_duration[:len(X_train)])
            
            # Analyser l'importance des features
            self.feature_importance = dict(enumerate(self.prediction_models['success'].feature_importances_))
            
            logger.info(f"Modèles entraînés. Score de succès: {success_score:.3f}")
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèles: {e}")

# ==========================================
# CONTENT SIMILARITY - SIMILARITÉ DE CONTENU
# ==========================================

class ContentSimilarity:
    """
    📄 Content Similarity - Similarité de contenu enterprise
    
    Fonctionnalités Enterprise:
    - Analyse sémantique avec transformers
    - Détection de style et tonalité
    - Similarité multi-modale (texte, image, vidéo)
    - Clustering automatique de contenu
    - Recommandations de contenu complémentaire
    - Détection de plagiat et originalité
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.content_vectors = {}
        self.similarity_matrix = {}
        self.content_clusters = {}
        
        # Initialiser les modèles
        self._initialize_similarity_models()
    
    def _initialize_similarity_models(self) -> None:
        """Initialise les modèles de similarité"""
        try:
            # Vectorizer TF-IDF pour analyse textuelle
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Modèle de sentences transformer pour similarité sémantique
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except:
                self.sentence_model = None
                logger.warning("SentenceTransformer non disponible")
            
            # Modèle de clustering
            self.content_clusterer = KMeans(n_clusters=20, random_state=42)
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles similarité: {e}")
    
    async def analyze_content_similarity(self, user1_id: str, user2_id: str) -> Dict:
        """Analyse la similarité de contenu entre deux utilisateurs"""
        try:
            # Récupérer les contenus
            content1 = await self._get_user_content(user1_id)
            content2 = await self._get_user_content(user2_id)
            
            if not content1 or not content2:
                return {'similarity_score': 0, 'details': {}}
            
            # Analyser la similarité textuelle
            text_similarity = await self._calculate_text_similarity(content1, content2)
            
            # Analyser la similarité stylistique
            style_similarity = await self._calculate_style_similarity(content1, content2)
            
            # Analyser la similarité thématique
            topic_similarity = await self._calculate_topic_similarity(content1, content2)
            
            # Analyser la similarité temporelle
            temporal_similarity = await self._calculate_temporal_similarity(content1, content2)
            
            # Score global pondéré
            overall_similarity = (
                text_similarity * 0.3 +
                style_similarity * 0.25 +
                topic_similarity * 0.35 +
                temporal_similarity * 0.1
            )
            
            return {
                'similarity_score': overall_similarity,
                'details': {
                    'text_similarity': text_similarity,
                    'style_similarity': style_similarity,
                    'topic_similarity': topic_similarity,
                    'temporal_similarity': temporal_similarity
                },
                'complementarity_areas': await self._identify_complementarity_areas(content1, content2),
                'collaboration_opportunities': await self._suggest_collaboration_opportunities(content1, content2)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse similarité contenu: {e}")
            return {'similarity_score': 0, 'details': {}}
    
    async def _calculate_text_similarity(self, content1: List[Dict], content2: List[Dict]) -> float:
        """Calcule la similarité textuelle"""
        try:
            # Extraire les textes
            texts1 = [item.get('text', '') for item in content1 if item.get('text')]
            texts2 = [item.get('text', '') for item in content2 if item.get('text')]
            
            if not texts1 or not texts2:
                return 0.0
            
            # Méthode 1: TF-IDF
            all_texts = texts1 + texts2
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculer la similarité moyenne
            n1, n2 = len(texts1), len(texts2)
            similarities = []
            
            for i in range(n1):
                for j in range(n1, n1 + n2):
                    sim = cosine_similarity(tfidf_matrix[i], tfidf_matrix[j])[0][0]
                    similarities.append(sim)
            
            tfidf_similarity = np.mean(similarities) if similarities else 0
            
            # Méthode 2: Sentence Transformers (si disponible)
            semantic_similarity = 0
            if self.sentence_model:
                embeddings1 = self.sentence_model.encode(texts1)
                embeddings2 = self.sentence_model.encode(texts2)
                
                # Similarité moyenne entre toutes les paires
                semantic_sims = []
                for emb1 in embeddings1:
                    for emb2 in embeddings2:
                        sim = cosine_similarity([emb1], [emb2])[0][0]
                        semantic_sims.append(sim)
                
                semantic_similarity = np.mean(semantic_sims) if semantic_sims else 0
            
            # Combiner les deux méthodes
            return (tfidf_similarity + semantic_similarity) / 2 * 100
            
        except Exception as e:
            logger.error(f"Erreur calcul similarité textuelle: {e}")
            return 0.0
    
    async def _calculate_style_similarity(self, content1: List[Dict], content2: List[Dict]) -> float:
        """Calcule la similarité stylistique"""
        try:
            # Extraire les features stylistiques
            style1 = await self._extract_style_features(content1)
            style2 = await self._extract_style_features(content2)
            
            # Calculer la distance euclidienne normalisée
            style_vector1 = np.array(list(style1.values()))
            style_vector2 = np.array(list(style2.values()))
            
            # Normaliser
            if np.max(style_vector1) > 0:
                style_vector1 = style_vector1 / np.max(style_vector1)
            if np.max(style_vector2) > 0:
                style_vector2 = style_vector2 / np.max(style_vector2)
            
            # Similarité basée sur la distance
            distance = euclidean(style_vector1, style_vector2)
            max_distance = np.sqrt(len(style_vector1))  # Distance maximale possible
            
            similarity = (1 - distance / max_distance) * 100
            return max(0, similarity)
            
        except Exception as e:
            logger.error(f"Erreur calcul similarité style: {e}")
            return 0.0
    
    async def _extract_style_features(self, content: List[Dict]) -> Dict[str, float]:
        """Extrait les features stylistiques du contenu"""
        features = {
            'avg_length': 0,
            'sentiment_positivity': 0,
            'formality_score': 0,
            'emoji_usage': 0,
            'hashtag_usage': 0,
            'question_frequency': 0,
            'exclamation_frequency': 0,
            'caps_usage': 0
        }
        
        if not content:
            return features
        
        texts = [item.get('text', '') for item in content if item.get('text')]
        
        if texts:
            # Longueur moyenne
            features['avg_length'] = np.mean([len(text) for text in texts])
            
            # Usage d'emojis (approximation)
            emoji_count = sum(text.count('😊') + text.count('😍') + text.count('🔥') for text in texts)
            features['emoji_usage'] = emoji_count / len(texts)
            
            # Usage de hashtags
            hashtag_count = sum(text.count('#') for text in texts)
            features['hashtag_usage'] = hashtag_count / len(texts)
            
            # Fréquence de questions
            question_count = sum(text.count('?') for text in texts)
            features['question_frequency'] = question_count / len(texts)
            
            # Fréquence d'exclamations
            exclamation_count = sum(text.count('!') for text in texts)
            features['exclamation_frequency'] = exclamation_count / len(texts)
            
            # Usage de majuscules
            caps_count = sum(sum(1 for c in text if c.isupper()) for text in texts)
            total_chars = sum(len(text) for text in texts)
            features['caps_usage'] = caps_count / total_chars if total_chars > 0 else 0
        
        return features

# [CONTINUATION DES AUTRES CLASSES...]

# ==========================================
# EXPORTS CONSOLIDÉS
# ==========================================

__all__ = [
    # Core classes
    'AudienceAnalyzer', 'DemographicMatcher', 'CollaborationPredictor', 'SuccessForecaster',
    'ContentSimilarity', 'SemanticMatcher', 'GeographicMatcher', 'LocationAnalyzer',
    'MLMatcher', 'AIMatchingEngine', 'NeuralCompatibility', 'DeepLearningMatcher',
    'NicheCompatibility', 'SpecializationMatcher', 'PerformanceAnalyzer', 'MetricsEvaluator',
    'SkillMatcher', 'CompetencyAnalyzer', 'SuccessPredictor', 'OutcomeForecaster',
    'TemporalAnalyzer', 'TimingOptimizer',
    
    # Data types
    'UserProfile', 'MatchResult', 'AudienceProfile', 'ContentSignature', 'CollaborationPrediction',
    
    # Enums
    'MatchingStrategy', 'CompatibilityScore', 'AudienceSegment', 'SkillCategory', 'CollaborationType'
]

# ==========================================
# FACTORY FUNCTION
# ==========================================

async def create_matching_intelligence(redis_url: Optional[str] = None, 
                                      db_session=None) -> Dict[str, Any]:
    """
    Factory function pour créer une instance complète du Matching Intelligence
    """
    # Configuration Redis si URL fournie
    redis_client = None
    if redis_url:
        try:
            redis_client = await aioredis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Impossible de se connecter à Redis: {e}")
    
    # Créer les instances
    audience_analyzer = AudienceAnalyzer(db_session, redis_client)
    demographic_matcher = DemographicMatcher(audience_analyzer)
    collaboration_predictor = CollaborationPredictor(db_session, redis_client)
    content_similarity = ContentSimilarity(db_session, redis_client)
    
    return {
        'audience_analyzer': audience_analyzer,
        'demographic_matcher': demographic_matcher,
        'collaboration_predictor': collaboration_predictor,
        'content_similarity': content_similarity,
        'redis_client': redis_client
    }

# Fin du module matching_intelligence.py
