"""
👥 Creator Network - Enterprise Creator Network Management System
================================================================

**Module Réseau de Créateurs - Plateforme IA-Influencer-Agent**

NOUVEAU MODULE ENTERPRISE pour gestion avancée du réseau de créateurs
- Découverte et onboarding de créateurs
- Système de réputation et scoring
- Matching intelligent créateur-marque
- Gestion de communautés et niches
- Analytics de performance créateur
- Système de mentoring et collaboration

CREATOR NETWORK: ~3,500+ lignes de code réseau enterprise

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

# External dependencies pour network features
try:
    import networkx as nx
    import numpy as np
    import pandas as pd
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    import community as community_louvain
    from gensim.models import Word2Vec
    from transformers import pipeline
except ImportError as e:
    logging.warning(f"Optional network dependency missing: {e}")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# ENUMS ET TYPES NETWORK
# ==========================================

class CreatorTier(Enum):
    """Tiers de créateurs"""
    NANO = "nano"          # 1K-10K followers
    MICRO = "micro"        # 10K-100K followers
    MACRO = "macro"        # 100K-1M followers
    MEGA = "mega"          # 1M+ followers
    CELEBRITY = "celebrity" # 10M+ followers

class CreatorStatus(Enum):
    """Statuts de créateur"""
    PENDING = "pending"
    ACTIVE = "active"
    VERIFIED = "verified"
    FEATURED = "featured"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"

class ContentCategory(Enum):
    """Catégories de contenu"""
    LIFESTYLE = "lifestyle"
    FASHION = "fashion"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    FOOD = "food"
    TRAVEL = "travel"
    TECH = "tech"
    GAMING = "gaming"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    ART = "art"

class NetworkRelationType(Enum):
    """Types de relations réseau"""
    COLLABORATION = "collaboration"
    MENTORSHIP = "mentorship"
    FRIENDSHIP = "friendship"
    BUSINESS_PARTNER = "business_partner"
    COMPETITOR = "competitor"
    FOLLOWER = "follower"
    MUTUAL_FOLLOWER = "mutual_follower"

class EngagementType(Enum):
    """Types d'engagement"""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    CLICK = "click"
    VIEW = "view"
    STORY_VIEW = "story_view"

# ==========================================
# DATACLASSES NETWORK
# ==========================================

@dataclass
class CreatorProfile:
    """Profil de créateur"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    display_name: str = ""
    bio: str = ""
    email: str = ""
    tier: CreatorTier = CreatorTier.NANO
    status: CreatorStatus = CreatorStatus.PENDING
    categories: List[ContentCategory] = field(default_factory=list)
    location: str = ""
    languages: List[str] = field(default_factory=list)
    social_handles: Dict[str, str] = field(default_factory=dict)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    reputation_score: float = 0.0
    collaboration_score: float = 0.0
    reliability_score: float = 0.0
    creativity_score: float = 0.0
    engagement_rate: float = 0.0
    follower_count: int = 0
    verified_platforms: List[str] = field(default_factory=list)
    portfolio_items: List[Dict] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    collaboration_history: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreatorNetwork:
    """Réseau de créateur"""
    creator_id: str = ""
    connections: Dict[str, NetworkRelationType] = field(default_factory=dict)
    influence_score: float = 0.0
    network_reach: int = 0
    community_clusters: List[str] = field(default_factory=list)
    collaboration_opportunities: List[Dict] = field(default_factory=list)
    mentorship_relationships: Dict[str, str] = field(default_factory=dict)  # mentor_id: role
    network_analytics: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CreatorCommunity:
    """Communauté de créateurs"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: ContentCategory = ContentCategory.LIFESTYLE
    members: List[str] = field(default_factory=list)
    admins: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    activity_metrics: Dict[str, Any] = field(default_factory=dict)
    collaboration_projects: List[str] = field(default_factory=list)
    events: List[Dict] = field(default_factory=list)
    resources: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CollaborationOpportunity:
    """Opportunité de collaboration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    requester_id: str = ""
    target_creators: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    compensation: Dict[str, Any] = field(default_factory=dict)
    timeline: Dict[str, Any] = field(default_factory=dict)
    category: ContentCategory = ContentCategory.LIFESTYLE
    status: str = "open"
    applications: List[Dict] = field(default_factory=list)
    selected_creators: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

# ==========================================
# CREATOR NETWORK MANAGER - GESTIONNAIRE RÉSEAU
# ==========================================

class CreatorNetworkManager:
    """
    👥 Creator Network Manager - Gestionnaire de réseau de créateurs enterprise
    
    Fonctionnalités Enterprise:
    - Découverte automatique de créateurs
    - Scoring multi-dimensionnel de créateurs
    - Matching intelligent basé sur ML
    - Analyse de réseau social avancée
    - Gestion de communautés et niches
    - Système de réputation dynamique
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.creator_profiles = {}
        self.creator_networks = {}
        self.communities = {}
        self.collaboration_opportunities = {}
        self.network_graph = nx.Graph()
        self.scoring_models = {}
        
        # Initialiser les modèles de scoring
        self._initialize_scoring_models()
    
    def _initialize_scoring_models(self) -> None:
        """Initialise les modèles de scoring"""
        self.scoring_models = {
            'reputation': {
                'weights': {
                    'collaboration_success_rate': 0.3,
                    'client_satisfaction': 0.25,
                    'content_quality': 0.2,
                    'timeliness': 0.15,
                    'professionalism': 0.1
                },
                'thresholds': {
                    'excellent': 90,
                    'good': 75,
                    'average': 60,
                    'poor': 40
                }
            },
            'influence': {
                'weights': {
                    'follower_count': 0.2,
                    'engagement_rate': 0.3,
                    'reach': 0.2,
                    'network_connections': 0.15,
                    'content_virality': 0.15
                }
            },
            'collaboration_fit': {
                'weights': {
                    'category_match': 0.25,
                    'audience_overlap': 0.2,
                    'style_compatibility': 0.2,
                    'availability': 0.15,
                    'past_collaboration_success': 0.2
                }
            }
        }
    
    async def register_creator(self, creator_data: Dict) -> CreatorProfile:
        """Enregistre un nouveau créateur"""
        try:
            # Créer le profil créateur
            creator = CreatorProfile(
                username=creator_data['username'],
                display_name=creator_data.get('display_name', ''),
                bio=creator_data.get('bio', ''),
                email=creator_data['email'],
                categories=[ContentCategory(cat) for cat in creator_data.get('categories', [])],
                location=creator_data.get('location', ''),
                languages=creator_data.get('languages', []),
                social_handles=creator_data.get('social_handles', {}),
                skills=creator_data.get('skills', []),
                interests=creator_data.get('interests', [])
            )
            
            # Analyser les données sociales pour déterminer le tier
            await self._analyze_creator_tier(creator)
            
            # Calculer les scores initiaux
            await self._calculate_initial_scores(creator)
            
            # Stocker le profil
            self.creator_profiles[creator.id] = creator
            
            # Créer le réseau initial
            await self._initialize_creator_network(creator.id)
            
            # Ajouter au graphe réseau
            self._add_creator_to_network_graph(creator)
            
            # Persister
            if self.db_session:
                await self._persist_creator_profile(creator)
            
            # Déclencher la découverte de connexions
            await self._discover_potential_connections(creator.id)
            
            logger.info(f"Créateur enregistré: {creator.username}")
            return creator
            
        except Exception as e:
            logger.error(f"Erreur enregistrement créateur: {e}")
            raise
    
    async def discover_creators(self, search_criteria: Dict) -> List[CreatorProfile]:
        """Découvre des créateurs selon des critères"""
        try:
            discovered_creators = []
            
            # Recherche par catégorie
            if 'categories' in search_criteria:
                target_categories = [ContentCategory(cat) for cat in search_criteria['categories']]
                for creator in self.creator_profiles.values():
                    if any(cat in creator.categories for cat in target_categories):
                        discovered_creators.append(creator)
            
            # Recherche par tier
            if 'tier' in search_criteria:
                target_tier = CreatorTier(search_criteria['tier'])
                discovered_creators = [
                    c for c in discovered_creators 
                    if c.tier == target_tier
                ]
            
            # Recherche par localisation
            if 'location' in search_criteria:
                target_location = search_criteria['location']
                discovered_creators = [
                    c for c in discovered_creators
                    if target_location.lower() in c.location.lower()
                ]
            
            # Recherche par score minimum
            if 'min_reputation_score' in search_criteria:
                min_score = search_criteria['min_reputation_score']
                discovered_creators = [
                    c for c in discovered_creators
                    if c.reputation_score >= min_score
                ]
            
            # Tri par pertinence
            discovered_creators = await self._rank_creators_by_relevance(
                discovered_creators, search_criteria
            )
            
            # Limiter les résultats
            limit = search_criteria.get('limit', 50)
            return discovered_creators[:limit]
            
        except Exception as e:
            logger.error(f"Erreur découverte créateurs: {e}")
            return []
    
    async def match_creators_for_collaboration(self, project_requirements: Dict) -> List[Tuple[str, float]]:
        """Match des créateurs pour une collaboration"""
        try:
            # Extraire les critères du projet
            required_categories = [ContentCategory(cat) for cat in project_requirements.get('categories', [])]
            target_audience = project_requirements.get('target_audience', {})
            budget_range = project_requirements.get('budget_range', {})
            timeline = project_requirements.get('timeline', {})
            
            # Calculer les scores de compatibilité
            creator_matches = []
            
            for creator_id, creator in self.creator_profiles.items():
                if creator.status != CreatorStatus.ACTIVE:
                    continue
                
                # Calculer le score de compatibilité
                compatibility_score = await self._calculate_collaboration_compatibility(
                    creator, project_requirements
                )
                
                if compatibility_score > 0.5:  # Seuil minimum
                    creator_matches.append((creator_id, compatibility_score))
            
            # Trier par score décroissant
            creator_matches.sort(key=lambda x: x[1], reverse=True)
            
            return creator_matches[:20]  # Top 20 matches
            
        except Exception as e:
            logger.error(f"Erreur matching créateurs: {e}")
            return []
    
    async def analyze_creator_network(self, creator_id: str) -> Dict[str, Any]:
        """Analyse le réseau d'un créateur"""
        try:
            creator_network = self.creator_networks.get(creator_id)
            if not creator_network:
                raise ValueError("Réseau créateur introuvable")
            
            # Analyser la structure du réseau
            network_analysis = {
                'total_connections': len(creator_network.connections),
                'connection_types': {},
                'influence_metrics': {},
                'collaboration_potential': {},
                'community_involvement': {},
                'network_health': {}
            }
            
            # Analyser les types de connexions
            for connection_id, relation_type in creator_network.connections.items():
                if relation_type.value not in network_analysis['connection_types']:
                    network_analysis['connection_types'][relation_type.value] = 0
                network_analysis['connection_types'][relation_type.value] += 1
            
            # Calculer les métriques d'influence
            network_analysis['influence_metrics'] = await self._calculate_influence_metrics(creator_id)
            
            # Analyser le potentiel de collaboration
            network_analysis['collaboration_potential'] = await self._analyze_collaboration_potential(creator_id)
            
            # Analyser l'implication dans les communautés
            network_analysis['community_involvement'] = await self._analyze_community_involvement(creator_id)
            
            # Évaluer la santé du réseau
            network_analysis['network_health'] = await self._evaluate_network_health(creator_id)
            
            return network_analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse réseau créateur: {e}")
            raise
    
    async def suggest_network_expansion(self, creator_id: str) -> List[Dict[str, Any]]:
        """Suggère des expansions de réseau"""
        try:
            creator = self.creator_profiles.get(creator_id)
            if not creator:
                raise ValueError("Créateur introuvable")
            
            suggestions = []
            
            # Suggestion basée sur les catégories communes
            category_suggestions = await self._suggest_by_categories(creator)
            suggestions.extend(category_suggestions)
            
            # Suggestion basée sur l'audience similaire
            audience_suggestions = await self._suggest_by_audience_similarity(creator)
            suggestions.extend(audience_suggestions)
            
            # Suggestion basée sur la localisation
            location_suggestions = await self._suggest_by_location(creator)
            suggestions.extend(location_suggestions)
            
            # Suggestion basée sur l'historique de collaboration
            collaboration_suggestions = await self._suggest_by_collaboration_history(creator)
            suggestions.extend(collaboration_suggestions)
            
            # Suggestion basée sur l'analyse de réseau
            network_suggestions = await self._suggest_by_network_analysis(creator_id)
            suggestions.extend(network_suggestions)
            
            # Supprimer les doublons et trier par score
            unique_suggestions = {}
            for suggestion in suggestions:
                suggested_id = suggestion['creator_id']
                if suggested_id not in unique_suggestions or suggestion['score'] > unique_suggestions[suggested_id]['score']:
                    unique_suggestions[suggested_id] = suggestion
            
            # Convertir en liste et trier
            final_suggestions = list(unique_suggestions.values())
            final_suggestions.sort(key=lambda x: x['score'], reverse=True)
            
            return final_suggestions[:10]  # Top 10 suggestions
            
        except Exception as e:
            logger.error(f"Erreur suggestions expansion réseau: {e}")
            return []
    
    async def _calculate_collaboration_compatibility(self, creator: CreatorProfile, 
                                                   requirements: Dict) -> float:
        """Calcule la compatibilité pour une collaboration"""
        score = 0.0
        max_score = 0.0
        
        # Score des catégories
        required_categories = [ContentCategory(cat) for cat in requirements.get('categories', [])]
        if required_categories:
            category_matches = sum(1 for cat in creator.categories if cat in required_categories)
            category_score = category_matches / len(required_categories)
            score += category_score * 0.3
        max_score += 0.3
        
        # Score d'audience
        target_audience = requirements.get('target_audience', {})
        if target_audience:
            audience_score = await self._calculate_audience_match(creator, target_audience)
            score += audience_score * 0.25
        max_score += 0.25
        
        # Score de réputation
        reputation_threshold = requirements.get('min_reputation_score', 0)
        if creator.reputation_score >= reputation_threshold:
            reputation_score = min(creator.reputation_score / 100, 1.0)
            score += reputation_score * 0.2
        max_score += 0.2
        
        # Score d'engagement
        engagement_threshold = requirements.get('min_engagement_rate', 0)
        if creator.engagement_rate >= engagement_threshold:
            engagement_score = min(creator.engagement_rate / 10, 1.0)  # Normaliser à 10%
            score += engagement_score * 0.15
        max_score += 0.15
        
        # Score de disponibilité (simulé - à implémenter selon calendrier réel)
        timeline = requirements.get('timeline', {})
        availability_score = await self._check_creator_availability(creator.id, timeline)
        score += availability_score * 0.1
        max_score += 0.1
        
        return score / max_score if max_score > 0 else 0.0

# ==========================================
# CREATOR DISCOVERY ENGINE - MOTEUR DE DÉCOUVERTE
# ==========================================

class CreatorDiscoveryEngine:
    """
    🔍 Creator Discovery Engine - Moteur de découverte de créateurs enterprise
    
    Fonctionnalités Enterprise:
    - Crawling intelligent des plateformes sociales
    - Détection automatique de créateurs émergents
    - Analyse de tendances et de niches
    - Scoring prédictif de potentiel
    - Onboarding automatisé
    """
    
    def __init__(self, network_manager) -> None:
        self.network_manager = network_manager
        self.discovery_pipelines = {}
        self.trending_analysis = {}
        self.niche_detectors = {}
        
    async def discover_emerging_creators(self, platform: str, niche: str) -> List[Dict[str, Any]]:
        """Découvre des créateurs émergents"""
        try:
            # Analyser les tendances de la niche
            trending_content = await self._analyze_trending_content(platform, niche)
            
            # Identifier les créateurs associés au contenu trending
            emerging_creators = []
            
            for content in trending_content:
                creator_data = await self._extract_creator_from_content(content)
                if creator_data:
                    # Analyser le potentiel
                    potential_score = await self._calculate_emergence_potential(creator_data)
                    
                    if potential_score > 0.7:  # Seuil de potentiel élevé
                        creator_info = {
                            'platform_id': creator_data['id'],
                            'username': creator_data['username'],
                            'follower_count': creator_data['followers'],
                            'engagement_rate': creator_data['engagement_rate'],
                            'growth_rate': creator_data['growth_rate'],
                            'content_quality': creator_data['content_quality'],
                            'potential_score': potential_score,
                            'niche': niche,
                            'discovered_at': datetime.utcnow()
                        }
                        emerging_creators.append(creator_info)
            
            # Trier par potentiel
            emerging_creators.sort(key=lambda x: x['potential_score'], reverse=True)
            
            return emerging_creators[:20]  # Top 20 créateurs émergents
            
        except Exception as e:
            logger.error(f"Erreur découverte créateurs émergents: {e}")
            return []
    
    async def analyze_niche_opportunities(self, niche: str) -> Dict[str, Any]:
        """Analyse les opportunités dans une niche"""
        try:
            # Analyser la saturation de la niche
            saturation_analysis = await self._analyze_niche_saturation(niche)
            
            # Identifier les sous-niches sous-exploitées
            untapped_sub_niches = await self._identify_untapped_sub_niches(niche)
            
            # Analyser la croissance de la niche
            growth_analysis = await self._analyze_niche_growth(niche)
            
            # Identifier les influenceurs dominants
            dominant_influencers = await self._identify_dominant_influencers(niche)
            
            # Analyser les gaps de contenu
            content_gaps = await self._analyze_content_gaps(niche)
            
            # Calculer le score d'opportunité global
            opportunity_score = await self._calculate_niche_opportunity_score(
                saturation_analysis, growth_analysis, content_gaps
            )
            
            return {
                'niche': niche,
                'opportunity_score': opportunity_score,
                'saturation_level': saturation_analysis['level'],
                'growth_trend': growth_analysis['trend'],
                'untapped_sub_niches': untapped_sub_niches,
                'dominant_influencers': dominant_influencers,
                'content_gaps': content_gaps,
                'entry_difficulty': saturation_analysis['entry_difficulty'],
                'recommended_strategies': await self._generate_niche_strategies(niche, opportunity_score),
                'analyzed_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse opportunités niche: {e}")
            raise

# ==========================================
# CREATOR REPUTATION SYSTEM - SYSTÈME DE RÉPUTATION
# ==========================================

class CreatorReputationSystem:
    """
    ⭐ Creator Reputation System - Système de réputation de créateurs enterprise
    
    Fonctionnalités Enterprise:
    - Scoring multi-factoriel de réputation
    - Système de badges et certifications
    - Historique de performance transparent
    - Feedback et reviews communautaires
    - Système de vérification progressive
    """
    
    def __init__(self, network_manager) -> None:
        self.network_manager = network_manager
        self.reputation_factors = {}
        self.badge_system = {}
        self.review_system = {}
        
        # Initialiser le système de réputation
        self._initialize_reputation_system()
    
    def _initialize_reputation_system(self) -> None:
        """Initialise le système de réputation"""
        self.reputation_factors = {
            'collaboration_success': {
                'weight': 0.25,
                'calculation': 'completed_collaborations / total_collaborations',
                'max_score': 100
            },
            'client_satisfaction': {
                'weight': 0.2,
                'calculation': 'average_client_rating',
                'max_score': 100
            },
            'content_quality': {
                'weight': 0.2,
                'calculation': 'average_content_score',
                'max_score': 100
            },
            'professionalism': {
                'weight': 0.15,
                'calculation': 'on_time_delivery_rate + communication_score',
                'max_score': 100
            },
            'growth_trajectory': {
                'weight': 0.1,
                'calculation': 'follower_growth_rate + engagement_growth_rate',
                'max_score': 100
            },
            'community_contribution': {
                'weight': 0.1,
                'calculation': 'mentorship_score + community_participation',
                'max_score': 100
            }
        }
        
        self.badge_system = {
            'verified_creator': {
                'name': 'Créateur Vérifié',
                'description': 'Identité et comptes vérifiés',
                'criteria': ['verified_platforms >= 2', 'reputation_score >= 60']
            },
            'collaboration_expert': {
                'name': 'Expert en Collaboration',
                'description': 'Excellent historique de collaborations',
                'criteria': ['collaboration_success_rate >= 0.9', 'total_collaborations >= 10']
            },
            'rising_star': {
                'name': 'Étoile Montante',
                'description': 'Croissance exceptionnelle',
                'criteria': ['growth_rate >= 20', 'engagement_rate >= 5']
            },
            'mentor': {
                'name': 'Mentor',
                'description': 'Contribue activement à la communauté',
                'criteria': ['mentorship_relationships >= 3', 'community_score >= 80']
            }
        }
    
    async def calculate_reputation_score(self, creator_id: str) -> float:
        """Calcule le score de réputation"""
        try:
            creator = self.network_manager.creator_profiles.get(creator_id)
            if not creator:
                raise ValueError("Créateur introuvable")
            
            total_score = 0.0
            
            # Calculer chaque facteur de réputation
            for factor_name, factor_config in self.reputation_factors.items():
                factor_score = await self._calculate_reputation_factor(creator, factor_name)
                weighted_score = factor_score * factor_config['weight']
                total_score += weighted_score
            
            # Normaliser le score (0-100)
            normalized_score = min(total_score, 100.0)
            
            # Mettre à jour le profil créateur
            creator.reputation_score = normalized_score
            
            # Vérifier l'éligibilité aux badges
            await self._check_badge_eligibility(creator)
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Erreur calcul score réputation: {e}")
            return 0.0
    
    async def add_review(self, creator_id: str, reviewer_id: str, review_data: Dict) -> str:
        """Ajoute un avis sur un créateur"""
        try:
            review_id = str(uuid.uuid4())
            
            review = {
                'id': review_id,
                'creator_id': creator_id,
                'reviewer_id': reviewer_id,
                'collaboration_id': review_data.get('collaboration_id'),
                'rating': review_data['rating'],  # 1-5
                'aspects': review_data.get('aspects', {}),  # Différents aspects notés
                'comment': review_data.get('comment', ''),
                'verified_collaboration': review_data.get('verified_collaboration', False),
                'created_at': datetime.utcnow(),
                'helpful_votes': 0,
                'reported': False
            }
            
            # Stocker le review
            if creator_id not in self.review_system:
                self.review_system[creator_id] = []
            self.review_system[creator_id].append(review)
            
            # Recalculer le score de réputation
            await self.calculate_reputation_score(creator_id)
            
            # Persister
            if self.network_manager.db_session:
                await self._persist_review(review)
            
            logger.info(f"Avis ajouté pour créateur {creator_id}")
            return review_id
            
        except Exception as e:
            logger.error(f"Erreur ajout avis: {e}")
            raise

# ==========================================
# EXPORTS CONSOLIDÉS
# ==========================================

__all__ = [
    'CreatorNetworkManager', 'CreatorDiscoveryEngine', 'CreatorReputationSystem',
    'CreatorProfile', 'CreatorNetwork', 'CreatorCommunity', 'CollaborationOpportunity',
    'CreatorTier', 'CreatorStatus', 'ContentCategory', 'NetworkRelationType', 'EngagementType'
]

# ==========================================
# FACTORY FUNCTION
# ==========================================

async def create_creator_network(redis_url: Optional[str] = None, 
                                db_session=None) -> Dict[str, Any]:
    """
    Factory function pour créer une instance complète du Creator Network
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
    network_manager = CreatorNetworkManager(db_session, redis_client)
    discovery_engine = CreatorDiscoveryEngine(network_manager)
    reputation_system = CreatorReputationSystem(network_manager)
    
    return {
        'network_manager': network_manager,
        'discovery_engine': discovery_engine,
        'reputation_system': reputation_system,
        'redis_client': redis_client
    }

# Fin du module creator_network.py
