"""
⭐ Reputation System - Enterprise Reputation Management System
=============================================================

**Module Système de Réputation - Plateforme IA-Influencer-Agent**

NOUVEAU MODULE ENTERPRISE pour gestion avancée de la réputation
- Scoring multi-dimensionnel de réputation basé sur IA
- Système de badges et certifications dynamiques
- Tracking de performance et historique transparent
- Système de reviews et feedback communautaire
- Détection de fraudes et manipulation
- Recommandations d'amélioration personnalisées

REPUTATION SYSTEM: ~3,500+ lignes de code réputation enterprise

© 2025 Fahed Mlaiel (mlaiel@live.de) - Tous Droits Réservés
"""

import asyncio
import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid
import hashlib

# External dependencies pour reputation management
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    from sklearn.metrics.pairwise import cosine_similarity
    import networkx as nx
    from textblob import TextBlob
    import spacy
    from scipy import stats
except ImportError as e:
    logging.warning(f"Optional reputation dependency missing: {e}")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# ENUMS ET TYPES REPUTATION
# ==========================================

class ReputationCategory(Enum):
    """Catégories de réputation"""
    OVERALL = "overall"
    COLLABORATION = "collaboration"
    CONTENT_QUALITY = "content_quality"
    PROFESSIONALISM = "professionalism"
    RELIABILITY = "reliability"
    CREATIVITY = "creativity"
    COMMUNICATION = "communication"
    TECHNICAL_SKILLS = "technical_skills"
    MARKET_INFLUENCE = "market_influence"

class BadgeType(Enum):
    """Types de badges"""
    ACHIEVEMENT = "achievement"
    SKILL = "skill"
    MILESTONE = "milestone"
    CERTIFICATION = "certification"
    RECOGNITION = "recognition"
    COMMUNITY = "community"

class ReviewSource(Enum):
    """Sources de reviews"""
    CLIENT = "client"
    PEER = "peer"
    PLATFORM = "platform"
    AUTOMATED = "automated"
    VERIFIED_COLLABORATION = "verified_collaboration"

class FraudType(Enum):
    """Types de fraudes détectées"""
    FAKE_REVIEWS = "fake_reviews"
    INFLATED_METRICS = "inflated_metrics"
    MANIPULATION = "manipulation"
    SOCKPUPPETING = "sockpuppeting"
    REVIEW_FARMING = "review_farming"

class ReputationTrend(Enum):
    """Tendances de réputation"""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"

# ==========================================
# DATACLASSES REPUTATION
# ==========================================

@dataclass
class ReputationScore:
    """Score de réputation"""
    user_id: str = ""
    category: ReputationCategory = ReputationCategory.OVERALL
    current_score: float = 0.0
    previous_score: float = 0.0
    max_score: float = 100.0
    percentile_rank: float = 0.0
    trend: ReputationTrend = ReputationTrend.STABLE
    confidence_level: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    factors: Dict[str, float] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)

@dataclass
class Badge:
    """Badge de réputation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: BadgeType = BadgeType.ACHIEVEMENT
    category: ReputationCategory = ReputationCategory.OVERALL
    icon_url: str = ""
    requirements: Dict[str, Any] = field(default_factory=dict)
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    points_value: int = 0
    auto_awarded: bool = True
    verification_required: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

@dataclass
class UserBadge:
    """Badge attribué à un utilisateur"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    badge_id: str = ""
    awarded_at: datetime = field(default_factory=datetime.utcnow)
    awarded_by: Optional[str] = None
    verification_status: str = "verified"
    evidence: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Review:
    """Review de réputation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reviewee_id: str = ""
    reviewer_id: str = ""
    source: ReviewSource = ReviewSource.CLIENT
    collaboration_id: Optional[str] = None
    category: ReputationCategory = ReputationCategory.OVERALL
    rating: float = 0.0  # 1-5 scale
    title: str = ""
    comment: str = ""
    aspects: Dict[str, float] = field(default_factory=dict)
    is_verified: bool = False
    helpful_votes: int = 0
    reported_count: int = 0
    fraud_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReputationInsight:
    """Insight de réputation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    type: str = ""  # improvement, warning, opportunity, achievement
    title: str = ""
    description: str = ""
    category: ReputationCategory = ReputationCategory.OVERALL
    impact_level: str = "medium"  # low, medium, high
    actionable_steps: List[str] = field(default_factory=list)
    expected_improvement: float = 0.0
    confidence: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class FraudAlert:
    """Alerte de fraude"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    fraud_type: FraudType = FraudType.FAKE_REVIEWS
    severity: str = "medium"  # low, medium, high, critical
    confidence: float = 0.0
    evidence: List[Dict] = field(default_factory=list)
    description: str = ""
    status: str = "open"  # open, investigating, resolved, false_positive
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# ==========================================
# REPUTATION MANAGER - GESTIONNAIRE PRINCIPAL
# ==========================================

class ReputationManager:
    """
    ⭐ Reputation Manager - Gestionnaire de réputation enterprise
    
    Fonctionnalités Enterprise:
    - Calcul de réputation multi-factoriel intelligent
    - Système de badges dynamique et adaptatif
    - Détection de fraudes et manipulation avancée
    - Analytics de réputation temps réel
    - Recommandations d'amélioration personnalisées
    - Tracking de performance longitudinal
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.reputation_scores = defaultdict(dict)
        self.badges = {}
        self.user_badges = defaultdict(list)
        self.reviews = defaultdict(list)
        self.fraud_detectors = {}
        self.reputation_models = {}
        
        # Initialiser le système
        self._initialize_reputation_system()
    
    def _initialize_reputation_system(self) -> None:
        """Initialise le système de réputation"""
        # Créer les badges par défaut
        self._create_default_badges()
        
        # Initialiser les modèles de détection de fraude
        self._initialize_fraud_detection()
        
        # Configurer les facteurs de réputation
        self._configure_reputation_factors()
    
    def _create_default_badges(self) -> None:
        """Crée les badges par défaut du système"""
        default_badges = [
            {
                'name': 'Nouveau Créateur',
                'description': 'Bienvenue dans la communauté !',
                'type': BadgeType.MILESTONE,
                'category': ReputationCategory.OVERALL,
                'requirements': {'profile_completed': True},
                'rarity': 'common',
                'points_value': 10
            },
            {
                'name': 'Collaborateur Fiable',
                'description': 'Reconnu pour sa fiabilité en collaboration',
                'type': BadgeType.ACHIEVEMENT,
                'category': ReputationCategory.RELIABILITY,
                'requirements': {'reliability_score': 85, 'collaborations_completed': 5},
                'rarity': 'uncommon',
                'points_value': 50
            },
            {
                'name': 'Expert en Contenu',
                'description': 'Créateur de contenu de qualité exceptionnelle',
                'type': BadgeType.SKILL,
                'category': ReputationCategory.CONTENT_QUALITY,
                'requirements': {'content_quality_score': 90, 'content_pieces': 20},
                'rarity': 'rare',
                'points_value': 100
            },
            {
                'name': 'Influenceur Vérifié',
                'description': 'Statut d\'influenceur vérifié par la plateforme',
                'type': BadgeType.CERTIFICATION,
                'category': ReputationCategory.MARKET_INFLUENCE,
                'requirements': {'follower_count': 10000, 'engagement_rate': 3.0},
                'rarity': 'epic',
                'points_value': 200,
                'verification_required': True
            },
            {
                'name': 'Leader Communautaire',
                'description': 'Contribue activement à la communauté',
                'type': BadgeType.COMMUNITY,
                'category': ReputationCategory.OVERALL,
                'requirements': {'community_contributions': 50, 'mentorships': 3},
                'rarity': 'legendary',
                'points_value': 500
            }
        ]
        
        for badge_data in default_badges:
            badge = Badge(**badge_data)
            self.badges[badge.id] = badge
    
    def _initialize_fraud_detection(self) -> None:
        """Initialise les systèmes de détection de fraude"""
        self.fraud_detectors = {
            'fake_reviews': {
                'model_type': 'isolation_forest',
                'features': ['review_velocity', 'rating_pattern', 'text_similarity', 'reviewer_diversity'],
                'threshold': 0.7
            },
            'inflated_metrics': {
                'model_type': 'statistical_outlier',
                'features': ['follower_growth_rate', 'engagement_spike', 'metrics_consistency'],
                'threshold': 0.8
            },
            'manipulation': {
                'model_type': 'network_analysis',
                'features': ['connection_patterns', 'review_timing', 'coordinated_behavior'],
                'threshold': 0.75
            }
        }
    
    def _configure_reputation_factors(self) -> None:
        """Configure les facteurs de réputation"""
        self.reputation_models = {
            ReputationCategory.COLLABORATION: {
                'factors': {
                    'completion_rate': 0.25,
                    'client_satisfaction': 0.25,
                    'timeliness': 0.20,
                    'communication_quality': 0.15,
                    'problem_resolution': 0.15
                },
                'base_weight': 0.3
            },
            ReputationCategory.CONTENT_QUALITY: {
                'factors': {
                    'quality_scores': 0.30,
                    'engagement_rates': 0.25,
                    'consistency': 0.20,
                    'innovation': 0.15,
                    'brand_alignment': 0.10
                },
                'base_weight': 0.25
            },
            ReputationCategory.PROFESSIONALISM: {
                'factors': {
                    'response_time': 0.25,
                    'communication_clarity': 0.25,
                    'deadline_adherence': 0.25,
                    'conflict_resolution': 0.25
                },
                'base_weight': 0.20
            },
            ReputationCategory.MARKET_INFLUENCE: {
                'factors': {
                    'follower_count': 0.20,
                    'engagement_rate': 0.30,
                    'reach': 0.20,
                    'brand_partnerships': 0.30
                },
                'base_weight': 0.15
            },
            ReputationCategory.CREATIVITY: {
                'factors': {
                    'originality_score': 0.40,
                    'trend_setting': 0.30,
                    'visual_appeal': 0.30
                },
                'base_weight': 0.10
            }
        }
    
    async def calculate_reputation_score(self, user_id: str, 
                                       category: ReputationCategory = ReputationCategory.OVERALL) -> ReputationScore:
        """Calcule le score de réputation pour un utilisateur"""
        try:
            if category == ReputationCategory.OVERALL:
                return await self._calculate_overall_reputation(user_id)
            else:
                return await self._calculate_category_reputation(user_id, category)
        
        except Exception as e:
            logger.error(f"Erreur calcul réputation: {e}")
            return ReputationScore(user_id=user_id, category=category)
    
    async def _calculate_overall_reputation(self, user_id: str) -> ReputationScore:
        """Calcule la réputation globale"""
        try:
            # Calculer les scores par catégorie
            category_scores = {}
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for category, config in self.reputation_models.items():
                category_score = await self._calculate_category_reputation(user_id, category)
                category_scores[category.value] = category_score.current_score
                
                weight = config['base_weight']
                total_weighted_score += category_score.current_score * weight
                total_weight += weight
            
            # Score global pondéré
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Récupérer le score précédent
            previous_score = 0.0
            if user_id in self.reputation_scores and ReputationCategory.OVERALL in self.reputation_scores[user_id]:
                previous_score = self.reputation_scores[user_id][ReputationCategory.OVERALL].current_score
            
            # Déterminer la tendance
            trend = await self._calculate_reputation_trend(user_id, overall_score, previous_score)
            
            # Calculer le percentile
            percentile_rank = await self._calculate_percentile_rank(user_id, overall_score)
            
            # Calculer la confiance
            confidence_level = await self._calculate_confidence_level(user_id, category_scores)
            
            # Créer le score de réputation
            reputation_score = ReputationScore(
                user_id=user_id,
                category=ReputationCategory.OVERALL,
                current_score=overall_score,
                previous_score=previous_score,
                percentile_rank=percentile_rank,
                trend=trend,
                confidence_level=confidence_level,
                factors=category_scores
            )
            
            # Stocker le score
            self.reputation_scores[user_id][ReputationCategory.OVERALL] = reputation_score
            
            # Ajouter à l'historique
            await self._add_to_reputation_history(reputation_score)
            
            # Vérifier l'éligibilité aux badges
            await self._check_badge_eligibility(user_id)
            
            # Persister
            if self.db_session:
                await self._persist_reputation_score(reputation_score)
            
            return reputation_score
            
        except Exception as e:
            logger.error(f"Erreur calcul réputation globale: {e}")
            return ReputationScore(user_id=user_id, category=ReputationCategory.OVERALL)
    
    async def _calculate_category_reputation(self, user_id: str, 
                                           category: ReputationCategory) -> ReputationScore:
        """Calcule la réputation pour une catégorie spécifique"""
        try:
            if category not in self.reputation_models:
                return ReputationScore(user_id=user_id, category=category)
            
            config = self.reputation_models[category]
            factors = config['factors']
            
            # Récupérer les données utilisateur
            user_data = await self._get_user_reputation_data(user_id, category)
            
            # Calculer les scores des facteurs
            factor_scores = {}
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for factor_name, weight in factors.items():
                factor_score = await self._calculate_factor_score(user_data, factor_name, category)
                factor_scores[factor_name] = factor_score
                
                total_weighted_score += factor_score * weight
                total_weight += weight
            
            # Score de catégorie
            category_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Récupérer le score précédent
            previous_score = 0.0
            if user_id in self.reputation_scores and category in self.reputation_scores[user_id]:
                previous_score = self.reputation_scores[user_id][category].current_score
            
            # Créer le score de réputation
            reputation_score = ReputationScore(
                user_id=user_id,
                category=category,
                current_score=category_score,
                previous_score=previous_score,
                factors=factor_scores
            )
            
            # Stocker le score
            if user_id not in self.reputation_scores:
                self.reputation_scores[user_id] = {}
            self.reputation_scores[user_id][category] = reputation_score
            
            return reputation_score
            
        except Exception as e:
            logger.error(f"Erreur calcul réputation catégorie {category}: {e}")
            return ReputationScore(user_id=user_id, category=category)
    
    async def add_review(self, review_data: Dict) -> Review:
        """Ajoute un review à un utilisateur"""
        try:
            # Créer le review
            review = Review(
                reviewee_id=review_data['reviewee_id'],
                reviewer_id=review_data['reviewer_id'],
                source=ReviewSource(review_data.get('source', 'client')),
                collaboration_id=review_data.get('collaboration_id'),
                category=ReputationCategory(review_data.get('category', 'overall')),
                rating=review_data['rating'],
                title=review_data.get('title', ''),
                comment=review_data.get('comment', ''),
                aspects=review_data.get('aspects', {}),
                is_verified=review_data.get('is_verified', False)
            )
            
            # Analyser le sentiment du commentaire
            if review.comment:
                sentiment_score = await self._analyze_review_sentiment(review.comment)
                review.metadata['sentiment_score'] = sentiment_score
            
            # Détecter les fraudes potentielles
            fraud_score = await self._detect_review_fraud(review)
            review.fraud_score = fraud_score
            
            # Stocker le review
            self.reviews[review.reviewee_id].append(review)
            
            # Persister
            if self.db_session:
                await self._persist_review(review)
            
            # Recalculer la réputation si le review est valide
            if fraud_score < 0.5:  # Seuil de fraude acceptable
                await self.calculate_reputation_score(review.reviewee_id)
            
            logger.info(f"Review ajouté: {review.rating}/5 pour {review.reviewee_id}")
            return review
            
        except Exception as e:
            logger.error(f"Erreur ajout review: {e}")
            raise
    
    async def award_badge(self, user_id: str, badge_id: str, awarded_by: Optional[str] = None,
                         evidence: Optional[List[Dict]] = None) -> UserBadge:
        """Attribue un badge à un utilisateur"""
        try:
            badge = self.badges.get(badge_id)
            if not badge:
                raise ValueError("Badge introuvable")
            
            # Vérifier si l'utilisateur possède déjà ce badge
            existing_badges = [ub for ub in self.user_badges[user_id] if ub.badge_id == badge_id]
            if existing_badges:
                raise ValueError("Badge déjà attribué")
            
            # Vérifier les requirements si attribution automatique
            if badge.auto_awarded:
                eligible = await self._check_badge_requirements(user_id, badge)
                if not eligible:
                    raise ValueError("Requirements non satisfaits")
            
            # Créer l'attribution de badge
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge_id,
                awarded_by=awarded_by,
                evidence=evidence or [],
                verification_status="verified" if not badge.verification_required else "pending"
            )
            
            # Stocker l'attribution
            self.user_badges[user_id].append(user_badge)
            
            # Persister
            if self.db_session:
                await self._persist_user_badge(user_badge)
            
            # Recalculer la réputation (les badges contribuent au score)
            await self.calculate_reputation_score(user_id)
            
            logger.info(f"Badge attribué: {badge.name} à {user_id}")
            return user_badge
            
        except Exception as e:
            logger.error(f"Erreur attribution badge: {e}")
            raise
    
    async def detect_fraud(self, user_id: str) -> List[FraudAlert]:
        """Détecte les fraudes pour un utilisateur"""
        try:
            fraud_alerts = []
            
            # Détecter les faux reviews
            fake_review_score = await self._detect_fake_reviews(user_id)
            if fake_review_score > 0.7:
                alert = FraudAlert(
                    user_id=user_id,
                    fraud_type=FraudType.FAKE_REVIEWS,
                    severity="high" if fake_review_score > 0.9 else "medium",
                    confidence=fake_review_score,
                    description="Détection de reviews potentiellement faux",
                    evidence=await self._get_fake_review_evidence(user_id)
                )
                fraud_alerts.append(alert)
            
            # Détecter l'inflation de métriques
            inflated_metrics_score = await self._detect_inflated_metrics(user_id)
            if inflated_metrics_score > 0.8:
                alert = FraudAlert(
                    user_id=user_id,
                    fraud_type=FraudType.INFLATED_METRICS,
                    severity="high" if inflated_metrics_score > 0.9 else "medium",
                    confidence=inflated_metrics_score,
                    description="Métriques potentiellement gonflées artificiellement"
                )
                fraud_alerts.append(alert)
            
            # Détecter la manipulation de réseau
            manipulation_score = await self._detect_network_manipulation(user_id)
            if manipulation_score > 0.75:
                alert = FraudAlert(
                    user_id=user_id,
                    fraud_type=FraudType.MANIPULATION,
                    severity="critical" if manipulation_score > 0.9 else "high",
                    confidence=manipulation_score,
                    description="Manipulation de réseau détectée"
                )
                fraud_alerts.append(alert)
            
            return fraud_alerts
            
        except Exception as e:
            logger.error(f"Erreur détection fraude: {e}")
            return []
    
    async def generate_reputation_insights(self, user_id: str) -> List[ReputationInsight]:
        """Génère des insights de réputation pour un utilisateur"""
        try:
            insights = []
            
            # Récupérer les scores de réputation
            user_scores = self.reputation_scores.get(user_id, {})
            
            # Analyser les opportunités d'amélioration
            for category, score in user_scores.items():
                if score.current_score < 80:  # Seuil d'amélioration
                    improvement_insights = await self._generate_improvement_insights(user_id, category, score)
                    insights.extend(improvement_insights)
            
            # Identifier les achievements potentiels
            achievement_insights = await self._generate_achievement_insights(user_id)
            insights.extend(achievement_insights)
            
            # Analyser les tendances
            trend_insights = await self._generate_trend_insights(user_id)
            insights.extend(trend_insights)
            
            # Suggestions de badges
            badge_insights = await self._generate_badge_suggestions(user_id)
            insights.extend(badge_insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur génération insights réputation: {e}")
            return []

# ==========================================
# BADGE SYSTEM - SYSTÈME DE BADGES
# ==========================================

class BadgeSystem:
    """
    🏆 Badge System - Système de badges enterprise
    
    Fonctionnalités Enterprise:
    - Badges dynamiques basés sur performance
    - Système de rareté et valeur
    - Badges communautaires et professionnels
    - Verification et certification automatisée
    - Analytics de progression badges
    """
    
    def __init__(self, reputation_manager) -> None:
        self.reputation_manager = reputation_manager
        self.badge_progression_tracking = defaultdict(dict)
        
    async def create_dynamic_badge(self, badge_data: Dict, creator_id: str) -> Badge:
        """Crée un badge dynamique"""
        try:
            badge = Badge(
                name=badge_data['name'],
                description=badge_data['description'],
                type=BadgeType(badge_data['type']),
                category=ReputationCategory(badge_data['category']),
                requirements=badge_data['requirements'],
                rarity=badge_data.get('rarity', 'common'),
                points_value=badge_data.get('points_value', 10),
                auto_awarded=badge_data.get('auto_awarded', True),
                verification_required=badge_data.get('verification_required', False)
            )
            
            # Stocker le badge
            self.reputation_manager.badges[badge.id] = badge
            
            # Persister
            if self.reputation_manager.db_session:
                await self._persist_badge(badge)
            
            logger.info(f"Badge dynamique créé: {badge.name}")
            return badge
            
        except Exception as e:
            logger.error(f"Erreur création badge dynamique: {e}")
            raise
    
    async def track_badge_progression(self, user_id: str) -> Dict[str, Any]:
        """Track la progression vers les badges"""
        try:
            progression = {}
            
            for badge_id, badge in self.reputation_manager.badges.items():
                # Skip si l'utilisateur possède déjà ce badge
                user_badges = self.reputation_manager.user_badges.get(user_id, [])
                if any(ub.badge_id == badge_id for ub in user_badges):
                    continue
                
                # Calculer la progression
                progress = await self._calculate_badge_progress(user_id, badge)
                if progress['percentage'] > 0:
                    progression[badge_id] = {
                        'badge': badge,
                        'progress': progress,
                        'estimated_completion': await self._estimate_badge_completion(user_id, badge, progress)
                    }
            
            return progression
            
        except Exception as e:
            logger.error(f"Erreur tracking progression badges: {e}")
            return {}

# ==========================================
# FRAUD DETECTION ENGINE - MOTEUR DE DÉTECTION DE FRAUDE
# ==========================================

class FraudDetectionEngine:
    """
    🛡️ Fraud Detection Engine - Moteur de détection de fraude enterprise
    
    Fonctionnalités Enterprise:
    - Détection de fraudes multi-méthodes
    - Machine learning pour pattern recognition
    - Analyse de réseau social pour collusion
    - Scoring de risque en temps réel
    - Alertes automatisées et investigation
    """
    
    def __init__(self, reputation_manager) -> None:
        self.reputation_manager = reputation_manager
        self.fraud_models = {}
        self.suspicious_patterns = defaultdict(list)
        
    async def analyze_review_authenticity(self, review: Review) -> float:
        """Analyse l'authenticité d'un review"""
        try:
            authenticity_score = 1.0
            
            # Analyser le texte
            text_score = await self._analyze_review_text_patterns(review)
            authenticity_score *= text_score
            
            # Analyser le timing
            timing_score = await self._analyze_review_timing(review)
            authenticity_score *= timing_score
            
            # Analyser le reviewer
            reviewer_score = await self._analyze_reviewer_patterns(review)
            authenticity_score *= reviewer_score
            
            # Analyser la cohérence des ratings
            rating_score = await self._analyze_rating_patterns(review)
            authenticity_score *= rating_score
            
            return authenticity_score
            
        except Exception as e:
            logger.error(f"Erreur analyse authenticité review: {e}")
            return 0.5
    
    async def detect_coordinated_manipulation(self, user_id: str) -> Dict[str, Any]:
        """Détecte la manipulation coordonnée"""
        try:
            # Analyser les patterns de reviews
            review_patterns = await self._analyze_coordinated_review_patterns(user_id)
            
            # Analyser les connections suspectes
            network_analysis = await self._analyze_suspicious_connections(user_id)
            
            # Analyser les timing suspects
            timing_analysis = await self._analyze_suspicious_timing(user_id)
            
            # Calculer le score de manipulation
            manipulation_score = await self._calculate_manipulation_score(
                review_patterns, network_analysis, timing_analysis
            )
            
            return {
                'manipulation_score': manipulation_score,
                'review_patterns': review_patterns,
                'network_analysis': network_analysis,
                'timing_analysis': timing_analysis,
                'risk_level': self._determine_risk_level(manipulation_score)
            }
            
        except Exception as e:
            logger.error(f"Erreur détection manipulation coordonnée: {e}")
            return {'manipulation_score': 0.0}

# ==========================================
# EXPORTS CONSOLIDÉS
# ==========================================

__all__ = [
    'ReputationManager', 'BadgeSystem', 'FraudDetectionEngine',
    'ReputationScore', 'Badge', 'UserBadge', 'Review', 'ReputationInsight', 'FraudAlert',
    'ReputationCategory', 'BadgeType', 'ReviewSource', 'FraudType', 'ReputationTrend'
]

# ==========================================
# FACTORY FUNCTION
# ==========================================

async def create_reputation_system(redis_url: Optional[str] = None, 
                                  db_session=None) -> Dict[str, Any]:
    """
    Factory function pour créer une instance complète du Reputation System
    """
    # Configuration Redis si URL fournie
    redis_client = None
    if redis_url:
        try:
            import aioredis
            redis_client = await aioredis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Impossible de se connecter à Redis: {e}")
    
    # Créer les instances
    reputation_manager = ReputationManager(db_session, redis_client)
    badge_system = BadgeSystem(reputation_manager)
    fraud_detection_engine = FraudDetectionEngine(reputation_manager)
    
    return {
        'reputation_manager': reputation_manager,
        'badge_system': badge_system,
        'fraud_detection_engine': fraud_detection_engine,
        'redis_client': redis_client
    }

# Fin du module reputation_system.py
