#!/usr/bin/env python3
"""🧠 Redis Behavior Analysis Orchestrator - Advanced User & System Behavior Intelligence
=========================================================================================
Expert: LEAD DEV IA + ML ENGINEER + DATA SCIENTIST + BACKEND SENIOR
Technologies: Behavior Analysis + Machine Learning + Pattern Recognition + Predictive Analytics
Architecture: Level 3 - Behavioral Intelligence Layer
Date: 2025-01-14

Ultra-advanced behavior analysis system with AI-powered user pattern recognition,
system behavior prediction, engagement optimization and creator economy intelligence.
=========================================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
=========================================================================================
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import time
import numpy as np
from datetime import datetime, timedelta
import json
import math
import statistics
from collections import deque, defaultdict
import redis
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, silhouette_score
import pandas as pd

logger = logging.getLogger(__name__)

class BehaviorType(Enum):
    """Types de comportements analysés"""
    USER_INTERACTION = "user_interaction"
    CREATOR_WORKFLOW = "creator_workflow"
    CONTENT_CONSUMPTION = "content_consumption"
    COLLABORATION_PATTERN = "collaboration_pattern"
    MONETIZATION_BEHAVIOR = "monetization_behavior"
    ENGAGEMENT_PATTERN = "engagement_pattern"
    SYSTEM_USAGE = "system_usage"
    PERFORMANCE_PATTERN = "performance_pattern"

class BehaviorCategory(Enum):
    """Catégories de comportements"""
    NORMAL = "normal"
    ANOMALOUS = "anomalous"
    TRENDING = "trending"
    SEASONAL = "seasonal"
    VIRAL = "viral"
    DECLINING = "declining"
    PREDICTABLE = "predictable"
    CHAOTIC = "chaotic"

class UserPersona(Enum):
    """Personas d'utilisateurs identifiés"""
    CASUAL_CREATOR = "casual_creator"
    PROFESSIONAL_CREATOR = "professional_creator"
    COLLABORATOR = "collaborator"
    CONSUMER = "consumer"
    POWER_USER = "power_user"
    ENTERPRISE_USER = "enterprise_user"
    INFLUENCER = "influencer"
    BRAND_MANAGER = "brand_manager"

class EngagementLevel(Enum):
    """Niveaux d'engagement"""
    VERY_HIGH = "very_high"     # > 90%
    HIGH = "high"               # 70-90%
    MEDIUM = "medium"           # 40-70%
    LOW = "low"                 # 20-40%
    VERY_LOW = "very_low"       # < 20%

class BehaviorTrend(Enum):
    """Tendances comportementales"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    CYCLICAL = "cyclical"
    EXPONENTIAL = "exponential"

@dataclass
class BehaviorConfig:
    """Configuration d'analyse comportementale"""
    # Fenêtres d'analyse
    analysis_window: int = 3600          # Fenêtre analyse (1h)
    historical_depth: int = 2592000      # Profondeur historique (30 jours)
    pattern_discovery_window: int = 604800 # Fenêtre découverte patterns (7 jours)
    
    # Seuils de détection
    anomaly_threshold: float = 2.5       # Seuil anomalie (écarts-types)
    trend_significance: float = 0.1      # Seuil significance tendance
    clustering_min_samples: int = 10     # Échantillons minimum clustering
    
    # Paramètres ML
    model_retrain_interval: int = 86400  # Interval re-entraînement (24h)
    feature_importance_threshold: float = 0.05 # Seuil importance features
    prediction_confidence_min: float = 0.7     # Confiance minimum prédiction
    
    # Métriques comportementales
    tracked_behaviors: List[BehaviorType] = field(default_factory=lambda: [
        BehaviorType.USER_INTERACTION,
        BehaviorType.CREATOR_WORKFLOW,
        BehaviorType.CONTENT_CONSUMPTION,
        BehaviorType.COLLABORATION_PATTERN,
        BehaviorType.MONETIZATION_BEHAVIOR,
        BehaviorType.ENGAGEMENT_PATTERN
    ])
    
    # Optimisations spécialisées
    creator_economy_focus: bool = True
    real_time_analysis: bool = True
    predictive_modeling: bool = True
    persona_identification: bool = True

@dataclass
class BehaviorPattern:
    """Pattern comportemental identifié"""
    pattern_id: str = ""
    behavior_type: BehaviorType = BehaviorType.USER_INTERACTION
    category: BehaviorCategory = BehaviorCategory.NORMAL
    confidence: float = 0.0
    frequency: float = 0.0
    intensity: float = 0.0
    duration: float = 0.0
    users_affected: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Détails du pattern
    description: str = ""
    triggers: List[str] = field(default_factory=list)
    consequences: List[str] = field(default_factory=list)
    correlations: Dict[str, float] = field(default_factory=dict)
    
    # Métriques business
    revenue_impact: float = 0.0
    engagement_impact: float = 0.0
    performance_impact: float = 0.0
    creator_satisfaction_impact: float = 0.0

@dataclass
class UserBehaviorProfile:
    """Profil comportemental utilisateur"""
    user_id: str = ""
    persona: UserPersona = UserPersona.CASUAL_CREATOR
    engagement_level: EngagementLevel = EngagementLevel.MEDIUM
    behavior_score: float = 0.0
    
    # Patterns d'activité
    activity_patterns: Dict[str, Any] = field(default_factory=dict)
    peak_hours: List[int] = field(default_factory=list)
    preferred_content_types: List[str] = field(default_factory=list)
    collaboration_frequency: float = 0.0
    monetization_activity: float = 0.0
    
    # Métriques historiques
    session_duration_avg: float = 0.0
    content_creation_rate: float = 0.0
    interaction_rate: float = 0.0
    retention_probability: float = 0.0
    
    # Prédictions
    predicted_churn_risk: float = 0.0
    predicted_upgrade_likelihood: float = 0.0
    predicted_collaboration_interest: float = 0.0
    
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    profile_updated: datetime = field(default_factory=datetime.now)

@dataclass
class BehaviorInsight:
    """Insight comportemental actionnable"""
    insight_id: str = ""
    title: str = ""
    description: str = ""
    category: str = ""
    confidence: float = 0.0
    impact_score: float = 0.0
    
    # Recommandations
    recommendations: List[str] = field(default_factory=list)
    expected_improvement: float = 0.0
    implementation_effort: str = "medium"
    
    # Métriques affectées
    affected_metrics: List[str] = field(default_factory=list)
    potential_revenue_impact: float = 0.0
    potential_engagement_lift: float = 0.0
    
    # Contexte
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    related_patterns: List[str] = field(default_factory=list)
    
    timestamp: datetime = field(default_factory=datetime.now)

class RedisBehaviorAnalysisOrchestrator:
    """🧠 Orchestrateur d'analyse comportementale Redis ultra-avancé"""
    
    def __init__(self, config: BehaviorConfig = None):
        """Initialisation orchestrateur comportemental"""
        self.config = config or BehaviorConfig()
        self.redis_client = None
        self.is_running = False
        
        # Composants ML
        self.behavior_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.clustering_model = KMeans(n_clusters=8, random_state=42)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        
        # Storage interne
        self.behavior_patterns = {}
        self.user_profiles = {}
        self.insights_generated = {}
        self.model_performance = {}
        
        # Métriques en temps réel
        self.realtime_metrics = defaultdict(deque)
        self.behavior_counters = defaultdict(int)
        self.trend_analysis = {}
        
        # Système de cache intelligent
        self.pattern_cache = {}
        self.prediction_cache = {}
        self.insight_cache = {}
        
        logger.info("🧠 Orchestrateur d'analyse comportementale initialisé")

    async def start(self, redis_connection=None):
        """Démarrer l'orchestrateur comportemental"""
        try:
            self.redis_client = redis_connection or redis.Redis(decode_responses=True)
            self.is_running = True
            
            # Démarrer les analyses en arrière-plan
            analysis_tasks = [
                self._run_realtime_analysis(),
                self._run_pattern_discovery(),
                self._run_user_profiling(),
                self._run_insight_generation(),
                self._run_model_maintenance()
            ]
            
            await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            logger.info("🧠 Orchestrateur comportemental démarré avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage orchestrateur: {e}")
            raise

    async def stop(self):
        """Arrêter l'orchestrateur"""
        self.is_running = False
        logger.info("🧠 Orchestrateur comportemental arrêté")

    async def analyze_user_behavior(self, user_id: str, session_data: Dict[str, Any]) -> UserBehaviorProfile:
        """Analyser le comportement d'un utilisateur"""
        try:
            # Charger le profil existant ou créer nouveau
            profile = self.user_profiles.get(user_id, UserBehaviorProfile(user_id=user_id))
            
            # Extraire features comportementales
            features = await self._extract_behavioral_features(session_data)
            
            # Classifier le comportement
            behavior_category = await self._classify_behavior(features)
            
            # Identifier la persona
            persona = await self._identify_persona(user_id, features)
            
            # Calculer l'engagement
            engagement_level = await self._calculate_engagement_level(features)
            
            # Mettre à jour le profil
            profile.persona = persona
            profile.engagement_level = engagement_level
            profile.behavior_score = await self._calculate_behavior_score(features)
            profile.last_activity = datetime.now()
            profile.profile_updated = datetime.now()
            
            # Prédictions
            profile.predicted_churn_risk = await self._predict_churn_risk(user_id, features)
            profile.predicted_upgrade_likelihood = await self._predict_upgrade_likelihood(features)
            
            # Sauvegarder
            self.user_profiles[user_id] = profile
            await self._persist_user_profile(profile)
            
            logger.info(f"🧠 Comportement analysé pour utilisateur {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse comportement utilisateur {user_id}: {e}")
            return UserBehaviorProfile(user_id=user_id)

    async def discover_patterns(self, behavior_type: BehaviorType, time_window: int = None) -> List[BehaviorPattern]:
        """Découvrir des patterns comportementaux"""
        try:
            window = time_window or self.config.pattern_discovery_window
            end_time = datetime.now()
            start_time = end_time - timedelta(seconds=window)
            
            # Récupérer les données comportementales
            data = await self._get_behavior_data(behavior_type, start_time, end_time)
            
            if not data:
                return []
            
            # Préparation des données
            features_df = await self._prepare_pattern_data(data)
            
            # Clustering pour identifier patterns
            clusters = await self._perform_clustering(features_df)
            
            # Analyser chaque cluster comme pattern potentiel
            patterns = []
            for cluster_id, cluster_data in clusters.items():
                pattern = await self._analyze_cluster_pattern(
                    cluster_id, cluster_data, behavior_type
                )
                if pattern.confidence > 0.5:  # Seuil de confiance
                    patterns.append(pattern)
            
            # Trier par confiance
            patterns.sort(key=lambda p: p.confidence, reverse=True)
            
            # Sauvegarder patterns
            for pattern in patterns:
                self.behavior_patterns[pattern.pattern_id] = pattern
                await self._persist_pattern(pattern)
            
            logger.info(f"🧠 {len(patterns)} patterns découverts pour {behavior_type.value}")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur découverte patterns: {e}")
            return []

    async def generate_behavioral_insights(self, context: str = "global") -> List[BehaviorInsight]:
        """Générer des insights comportementaux actionnables"""
        try:
            insights = []
            
            # Analyser les tendances globales
            global_insights = await self._analyze_global_trends()
            insights.extend(global_insights)
            
            # Analyser les patterns d'engagement
            engagement_insights = await self._analyze_engagement_patterns()
            insights.extend(engagement_insights)
            
            # Analyser les comportements de monétisation
            monetization_insights = await self._analyze_monetization_behaviors()
            insights.extend(monetization_insights)
            
            # Analyser les patterns de collaboration
            collaboration_insights = await self._analyze_collaboration_patterns()
            insights.extend(collaboration_insights)
            
            # Analyser les anomalies comportementales
            anomaly_insights = await self._analyze_behavioral_anomalies()
            insights.extend(anomaly_insights)
            
            # Filtrer et prioriser insights
            insights = await self._prioritize_insights(insights)
            
            # Sauvegarder insights
            for insight in insights:
                self.insights_generated[insight.insight_id] = insight
                await self._persist_insight(insight)
            
            logger.info(f"🧠 {len(insights)} insights générés pour contexte {context}")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Erreur génération insights: {e}")
            return []

    async def predict_user_behavior(self, user_id: str, prediction_horizon: int = 3600) -> Dict[str, Any]:
        """Prédire le comportement futur d'un utilisateur"""
        try:
            # Charger profil utilisateur
            profile = self.user_profiles.get(user_id)
            if not profile:
                profile = await self._load_user_profile(user_id)
            
            if not profile:
                return {"error": "Profil utilisateur non trouvé"}
            
            # Récupérer historique comportemental
            historical_data = await self._get_user_behavior_history(user_id)
            
            # Extraire features prédictives
            features = await self._extract_predictive_features(profile, historical_data)
            
            # Prédictions spécifiques
            predictions = {
                "next_session_probability": await self._predict_next_session(features),
                "content_creation_likelihood": await self._predict_content_creation(features),
                "collaboration_interest": await self._predict_collaboration_interest(features),
                "monetization_potential": await self._predict_monetization_potential(features),
                "engagement_level": await self._predict_engagement_level(features),
                "platform_retention": await self._predict_retention(features),
                "upgrade_likelihood": await self._predict_upgrade_likelihood(features),
                "peak_activity_times": await self._predict_peak_times(features)
            }
            
            # Confiance globale prédiction
            predictions["overall_confidence"] = np.mean([
                pred for pred in predictions.values() 
                if isinstance(pred, (int, float))
            ])
            
            # Recommandations basées prédictions
            predictions["recommendations"] = await self._generate_user_recommendations(
                profile, predictions
            )
            
            # Cache prédiction
            cache_key = f"prediction:{user_id}:{prediction_horizon}"
            self.prediction_cache[cache_key] = {
                "predictions": predictions,
                "timestamp": datetime.now(),
                "expires": datetime.now() + timedelta(seconds=prediction_horizon)
            }
            
            logger.info(f"🧠 Prédictions générées pour utilisateur {user_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction comportement {user_id}: {e}")
            return {"error": str(e)}

    async def optimize_creator_experience(self, creator_id: str) -> Dict[str, Any]:
        """Optimiser l'expérience d'un créateur"""
        try:
            # Analyser comportement créateur
            creator_profile = await self.analyze_user_behavior(creator_id, {})
            
            # Identifier patterns d'activité
            activity_patterns = await self._analyze_creator_activity_patterns(creator_id)
            
            # Analyser performance contenu
            content_performance = await self._analyze_creator_content_performance(creator_id)
            
            # Analyser collaborations
            collaboration_analysis = await self._analyze_creator_collaborations(creator_id)
            
            # Analyser monétisation
            monetization_analysis = await self._analyze_creator_monetization(creator_id)
            
            # Générer recommandations personnalisées
            optimization_recommendations = {
                "content_strategy": await self._recommend_content_strategy(
                    creator_profile, content_performance
                ),
                "posting_schedule": await self._recommend_posting_schedule(
                    activity_patterns
                ),
                "collaboration_opportunities": await self._recommend_collaborations(
                    collaboration_analysis
                ),
                "monetization_strategies": await self._recommend_monetization(
                    monetization_analysis
                ),
                "audience_engagement": await self._recommend_engagement_tactics(
                    creator_profile
                ),
                "platform_optimization": await self._recommend_platform_optimizations(
                    creator_id
                )
            }
            
            # Score d'optimisation global
            optimization_score = await self._calculate_optimization_score(
                creator_profile, optimization_recommendations
            )
            
            result = {
                "creator_id": creator_id,
                "optimization_score": optimization_score,
                "current_performance": {
                    "engagement_level": creator_profile.engagement_level.value,
                    "behavior_score": creator_profile.behavior_score,
                    "monetization_activity": creator_profile.monetization_activity
                },
                "recommendations": optimization_recommendations,
                "estimated_improvement": await self._estimate_improvement_potential(
                    creator_profile, optimization_recommendations
                ),
                "implementation_priority": await self._prioritize_recommendations(
                    optimization_recommendations
                )
            }
            
            logger.info(f"🧠 Optimisation générée pour créateur {creator_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation créateur {creator_id}: {e}")
            return {"error": str(e)}

    async def get_behavior_analytics(self, analytics_type: str = "comprehensive") -> Dict[str, Any]:
        """Récupérer les analytics comportementales"""
        try:
            analytics = {}
            
            if analytics_type in ["comprehensive", "users"]:
                analytics["user_analytics"] = {
                    "total_users": len(self.user_profiles),
                    "persona_distribution": await self._get_persona_distribution(),
                    "engagement_distribution": await self._get_engagement_distribution(),
                    "behavior_score_stats": await self._get_behavior_score_stats(),
                    "churn_risk_analysis": await self._get_churn_risk_analysis(),
                    "retention_analytics": await self._get_retention_analytics()
                }
            
            if analytics_type in ["comprehensive", "patterns"]:
                analytics["pattern_analytics"] = {
                    "total_patterns": len(self.behavior_patterns),
                    "pattern_categories": await self._get_pattern_category_stats(),
                    "pattern_confidence_stats": await self._get_pattern_confidence_stats(),
                    "trending_patterns": await self._get_trending_patterns(),
                    "pattern_impact_analysis": await self._get_pattern_impact_analysis()
                }
            
            if analytics_type in ["comprehensive", "insights"]:
                analytics["insight_analytics"] = {
                    "total_insights": len(self.insights_generated),
                    "insight_categories": await self._get_insight_category_stats(),
                    "actionable_insights": await self._get_actionable_insights_count(),
                    "implementation_status": await self._get_implementation_status(),
                    "impact_metrics": await self._get_insight_impact_metrics()
                }
            
            if analytics_type in ["comprehensive", "performance"]:
                analytics["performance_analytics"] = {
                    "model_performance": self.model_performance,
                    "prediction_accuracy": await self._get_prediction_accuracy_stats(),
                    "processing_metrics": await self._get_processing_metrics(),
                    "system_health": await self._get_system_health_metrics()
                }
            
            analytics["generated_at"] = datetime.now().isoformat()
            analytics["analytics_type"] = analytics_type
            
            logger.info(f"🧠 Analytics comportementales générées: {analytics_type}")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Erreur génération analytics: {e}")
            return {"error": str(e)}

    # ================== MÉTHODES PRIVÉES ==================

    async def _run_realtime_analysis(self):
        """Analyse comportementale temps réel"""
        while self.is_running:
            try:
                # Traitement données temps réel
                await self._process_realtime_data()
                await asyncio.sleep(1)  # 1 seconde
            except Exception as e:
                logger.error(f"❌ Erreur analyse temps réel: {e}")
                await asyncio.sleep(5)

    async def _run_pattern_discovery(self):
        """Découverte patterns en arrière-plan"""
        while self.is_running:
            try:
                # Découverte patterns toutes les 5 minutes
                for behavior_type in self.config.tracked_behaviors:
                    await self.discover_patterns(behavior_type)
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"❌ Erreur découverte patterns: {e}")
                await asyncio.sleep(60)

    async def _run_user_profiling(self):
        """Profilage utilisateurs en arrière-plan"""
        while self.is_running:
            try:
                # Mise à jour profils utilisateurs
                await self._update_user_profiles()
                await asyncio.sleep(600)  # 10 minutes
            except Exception as e:
                logger.error(f"❌ Erreur profilage utilisateurs: {e}")
                await asyncio.sleep(120)

    async def _run_insight_generation(self):
        """Génération insights en arrière-plan"""
        while self.is_running:
            try:
                # Génération insights toutes les 30 minutes
                await self.generate_behavioral_insights()
                await asyncio.sleep(1800)  # 30 minutes
            except Exception as e:
                logger.error(f"❌ Erreur génération insights: {e}")
                await asyncio.sleep(300)

    async def _run_model_maintenance(self):
        """Maintenance modèles ML"""
        while self.is_running:
            try:
                # Re-entraînement modèles
                await self._retrain_models()
                await asyncio.sleep(self.config.model_retrain_interval)
            except Exception as e:
                logger.error(f"❌ Erreur maintenance modèles: {e}")
                await asyncio.sleep(3600)

    async def _extract_behavioral_features(self, session_data: Dict[str, Any]) -> np.ndarray:
        """Extraire features comportementales"""
        features = []
        
        # Features de session
        features.extend([
            session_data.get("duration", 0),
            session_data.get("page_views", 0),
            session_data.get("clicks", 0),
            session_data.get("scroll_depth", 0),
            session_data.get("time_on_page_avg", 0)
        ])
        
        # Features d'interaction
        features.extend([
            session_data.get("likes_given", 0),
            session_data.get("comments_made", 0),
            session_data.get("shares_made", 0),
            session_data.get("content_created", 0),
            session_data.get("collaborations_initiated", 0)
        ])
        
        # Features temporelles
        now = datetime.now()
        features.extend([
            now.hour,
            now.weekday(),
            session_data.get("time_since_last_session", 0)
        ])
        
        return np.array(features)

    async def _classify_behavior(self, features: np.ndarray) -> BehaviorCategory:
        """Classifier le comportement"""
        try:
            # Normalisation
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Prédiction
            prediction = self.behavior_classifier.predict(features_scaled)[0]
            
            # Mapping vers BehaviorCategory
            category_map = {
                0: BehaviorCategory.NORMAL,
                1: BehaviorCategory.ANOMALOUS,
                2: BehaviorCategory.TRENDING,
                3: BehaviorCategory.VIRAL
            }
            
            return category_map.get(prediction, BehaviorCategory.NORMAL)
            
        except Exception as e:
            logger.error(f"❌ Erreur classification comportement: {e}")
            return BehaviorCategory.NORMAL

    async def _identify_persona(self, user_id: str, features: np.ndarray) -> UserPersona:
        """Identifier la persona utilisateur"""
        try:
            # Logique d'identification persona basée sur features
            content_creation = features[8] if len(features) > 8 else 0
            collaboration_activity = features[9] if len(features) > 9 else 0
            session_duration = features[0] if len(features) > 0 else 0
            
            if content_creation > 5:
                if collaboration_activity > 3:
                    return UserPersona.PROFESSIONAL_CREATOR
                else:
                    return UserPersona.CASUAL_CREATOR
            elif collaboration_activity > 2:
                return UserPersona.COLLABORATOR
            elif session_duration > 1800:  # 30 minutes
                return UserPersona.POWER_USER
            else:
                return UserPersona.CONSUMER
                
        except Exception as e:
            logger.error(f"❌ Erreur identification persona: {e}")
            return UserPersona.CASUAL_CREATOR

    async def _calculate_engagement_level(self, features: np.ndarray) -> EngagementLevel:
        """Calculer le niveau d'engagement"""
        try:
            # Score d'engagement basé sur features
            engagement_score = 0
            
            if len(features) > 10:
                # Pondération des features d'engagement
                engagement_score += features[1] * 0.1  # page_views
                engagement_score += features[5] * 2    # likes_given
                engagement_score += features[6] * 3    # comments_made
                engagement_score += features[7] * 1.5  # shares_made
                engagement_score += features[8] * 5    # content_created
            
            # Mapping vers EngagementLevel
            if engagement_score > 50:
                return EngagementLevel.VERY_HIGH
            elif engagement_score > 30:
                return EngagementLevel.HIGH
            elif engagement_score > 15:
                return EngagementLevel.MEDIUM
            elif engagement_score > 5:
                return EngagementLevel.LOW
            else:
                return EngagementLevel.VERY_LOW
                
        except Exception as e:
            logger.error(f"❌ Erreur calcul engagement: {e}")
            return EngagementLevel.MEDIUM

    async def _calculate_behavior_score(self, features: np.ndarray) -> float:
        """Calculer score comportemental global"""
        try:
            if len(features) == 0:
                return 0.0
            
            # Normalisation et pondération
            normalized_features = (features - np.mean(features)) / (np.std(features) + 1e-8)
            weights = np.array([1, 1.5, 2, 1, 1.2, 3, 2.5, 2, 4, 3, 1, 1, 0.5])
            
            if len(normalized_features) >= len(weights):
                weighted_score = np.sum(normalized_features[:len(weights)] * weights)
                return max(0, min(100, weighted_score * 10 + 50))
            else:
                return 50.0  # Score neutre par défaut
                
        except Exception as e:
            logger.error(f"❌ Erreur calcul score comportement: {e}")
            return 50.0

    async def _predict_churn_risk(self, user_id: str, features: np.ndarray) -> float:
        """Prédire le risque de churn"""
        try:
            # Récupérer historique utilisateur
            profile = self.user_profiles.get(user_id)
            if not profile:
                return 0.5  # Risque neutre
            
            # Facteurs de risque
            time_since_last_activity = (datetime.now() - profile.last_activity).days
            engagement_decline = 1.0 - (profile.engagement_level.value == "very_low")
            
            # Calcul risque churn
            churn_risk = 0.0
            churn_risk += min(0.4, time_since_last_activity * 0.05)
            churn_risk += engagement_decline * 0.3
            churn_risk += (1.0 - profile.behavior_score / 100) * 0.3
            
            return min(1.0, max(0.0, churn_risk))
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction churn: {e}")
            return 0.5

    async def _predict_upgrade_likelihood(self, features: np.ndarray) -> float:
        """Prédire la probabilité d'upgrade"""
        try:
            # Facteurs d'upgrade
            content_creation = features[8] if len(features) > 8 else 0
            collaboration_activity = features[9] if len(features) > 9 else 0
            session_duration = features[0] if len(features) > 0 else 0
            
            # Score d'upgrade
            upgrade_score = 0.0
            upgrade_score += min(0.4, content_creation * 0.1)
            upgrade_score += min(0.3, collaboration_activity * 0.15)
            upgrade_score += min(0.3, session_duration / 3600 * 0.2)
            
            return min(1.0, max(0.0, upgrade_score))
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction upgrade: {e}")
            return 0.2

    # ================== MÉTHODES DE PERSISTENCE ==================

    async def _persist_user_profile(self, profile: UserBehaviorProfile):
        """Persister profil utilisateur"""
        try:
            if self.redis_client:
                key = f"behavior:profile:{profile.user_id}"
                data = {
                    "persona": profile.persona.value,
                    "engagement_level": profile.engagement_level.value,
                    "behavior_score": profile.behavior_score,
                    "last_activity": profile.last_activity.isoformat(),
                    "predicted_churn_risk": profile.predicted_churn_risk,
                    "predicted_upgrade_likelihood": profile.predicted_upgrade_likelihood
                }
                await self.redis_client.hset(key, mapping=data)
                await self.redis_client.expire(key, 2592000)  # 30 jours
        except Exception as e:
            logger.error(f"❌ Erreur persistence profil: {e}")

    async def _persist_pattern(self, pattern: BehaviorPattern):
        """Persister pattern comportemental"""
        try:
            if self.redis_client:
                key = f"behavior:pattern:{pattern.pattern_id}"
                data = {
                    "behavior_type": pattern.behavior_type.value,
                    "category": pattern.category.value,
                    "confidence": pattern.confidence,
                    "frequency": pattern.frequency,
                    "timestamp": pattern.timestamp.isoformat(),
                    "description": pattern.description
                }
                await self.redis_client.hset(key, mapping=data)
                await self.redis_client.expire(key, 604800)  # 7 jours
        except Exception as e:
            logger.error(f"❌ Erreur persistence pattern: {e}")

    async def _persist_insight(self, insight: BehaviorInsight):
        """Persister insight comportemental"""
        try:
            if self.redis_client:
                key = f"behavior:insight:{insight.insight_id}"
                data = {
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "impact_score": insight.impact_score,
                    "timestamp": insight.timestamp.isoformat(),
                    "recommendations": json.dumps(insight.recommendations)
                }
                await self.redis_client.hset(key, mapping=data)
                await self.redis_client.expire(key, 2592000)  # 30 jours
        except Exception as e:
            logger.error(f"❌ Erreur persistence insight: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Récupérer métriques de l'orchestrateur"""
        return {
            "orchestrator_type": "behavior_analysis",
            "status": "running" if self.is_running else "stopped",
            "user_profiles_count": len(self.user_profiles),
            "behavior_patterns_count": len(self.behavior_patterns),
            "insights_generated_count": len(self.insights_generated),
            "cache_sizes": {
                "pattern_cache": len(self.pattern_cache),
                "prediction_cache": len(self.prediction_cache),
                "insight_cache": len(self.insight_cache)
            },
            "model_status": {
                "behavior_classifier": "trained" if hasattr(self.behavior_classifier, "feature_importances_") else "untrained",
                "anomaly_detector": "trained" if hasattr(self.anomaly_detector, "decision_function") else "untrained",
                "clustering_model": "trained" if hasattr(self.clustering_model, "cluster_centers_") else "untrained"
            }
        }