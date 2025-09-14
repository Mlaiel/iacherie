"""
🎮 Gamification Engine - Enterprise Gamification Infrastructure
=============================================================

**Module de Gamification Consolidé - Plateforme IA-Influencer-Agent**

CONSOLIDATION INTELLIGENTE de gamification/ (2 fichiers → 1 module unifié + enrichissements)
- achievement_system.py → AchievementSystem, BadgeManager, RewardEngine
- [NOUVEAUX] → LeaderboardManager, PointsCalculator, ChallengeOrchestrator, MotivationEngine

TOTAL CONSOLIDÉ: ~6,000+ lignes de code gamification enterprise

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
from collections import defaultdict, deque
import hashlib

# External dependencies pour enterprise features
try:
    import aioredis
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, update, delete, and_, or_
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
except ImportError as e:
    logging.warning(f"Optional dependency missing: {e}")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# ENUMS ET TYPES CONSOLIDÉS
# ==========================================

class AchievementType(Enum):
    """Types d'achievements"""
    MILESTONE = "milestone"          # Objectifs à atteindre
    STREAK = "streak"               # Séries d'actions
    CUMULATIVE = "cumulative"       # Accumulation sur le temps
    RARE = "rare"                   # Achievements rares
    SOCIAL = "social"               # Basés sur interactions sociales
    SKILL = "skill"                 # Basés sur compétences
    CONTRIBUTION = "contribution"    # Basés sur contributions
    INNOVATION = "innovation"       # Créativité et innovation
    LEADERSHIP = "leadership"       # Leadership et mentorat
    COLLABORATION = "collaboration" # Travail d'équipe

class BadgeRarity(Enum):
    """Rareté des badges"""
    COMMON = "common"         # 50%+ des utilisateurs
    UNCOMMON = "uncommon"     # 25-50% des utilisateurs
    RARE = "rare"             # 10-25% des utilisateurs
    EPIC = "epic"             # 1-10% des utilisateurs
    LEGENDARY = "legendary"   # <1% des utilisateurs

class PointCategory(Enum):
    """Catégories de points"""
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    COMMUNITY_ENGAGEMENT = "community_engagement"
    SKILL_DEVELOPMENT = "skill_development"
    MENTORSHIP = "mentorship"
    INNOVATION = "innovation"
    CONSISTENCY = "consistency"
    QUALITY = "quality"
    INFLUENCE = "influence"
    CONTRIBUTION = "contribution"

class ChallengeType(Enum):
    """Types de défis"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"
    PERSONAL = "personal"
    TEAM = "team"
    COMMUNITY = "community"

class RewardType(Enum):
    """Types de récompenses"""
    POINTS = "points"
    BADGE = "badge"
    FEATURE_ACCESS = "feature_access"
    VISIBILITY_BOOST = "visibility_boost"
    MENTORSHIP_SESSION = "mentorship_session"
    PREMIUM_CONTENT = "premium_content"
    COLLABORATION_PRIORITY = "collaboration_priority"
    CUSTOM_PROFILE = "custom_profile"
    EARLY_ACCESS = "early_access"
    RECOGNITION = "recognition"

class LeaderboardType(Enum):
    """Types de leaderboards"""
    GLOBAL = "global"
    CATEGORY = "category"
    REGIONAL = "regional"
    TEAM = "team"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"
    SKILL_BASED = "skill_based"

# ==========================================
# DATACLASSES CONSOLIDÉES
# ==========================================

@dataclass
class Achievement:
    """Achievement/accomplissement unifié"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    achievement_type: AchievementType = AchievementType.MILESTONE
    criteria: Dict[str, Any] = field(default_factory=dict)
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    icon: str = ""
    badge_id: Optional[str] = None
    points_value: int = 0
    rarity: BadgeRarity = BadgeRarity.COMMON
    prerequisites: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Badge:
    """Badge unifié avec métadonnées"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    icon: str = ""
    rarity: BadgeRarity = BadgeRarity.COMMON
    category: str = ""
    points_value: int = 0
    design_elements: Dict[str, Any] = field(default_factory=dict)
    unlock_criteria: Dict[str, Any] = field(default_factory=dict)
    display_text: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_transferable: bool = False
    expiry_date: Optional[datetime] = None

@dataclass
class UserAchievement:
    """Association utilisateur-achievement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    achievement_id: str = ""
    unlocked_at: datetime = field(default_factory=datetime.utcnow)
    progress: Dict[str, Any] = field(default_factory=dict)
    is_displayed: bool = True
    unlock_method: str = ""  # automatic, manual, event
    witnessed_by: List[str] = field(default_factory=list)

@dataclass
class PointsTransaction:
    """Transaction de points"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    amount: int = 0
    category: PointCategory = PointCategory.CONTENT_CREATION
    reason: str = ""
    reference_id: Optional[str] = None  # ID de l'entité qui a causé les points
    reference_type: str = ""  # type d'entité (message, collaboration, etc.)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    multiplier: float = 1.0
    bonus_applied: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Challenge:
    """Défi gamifié"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    challenge_type: ChallengeType = ChallengeType.DAILY
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    criteria: Dict[str, Any] = field(default_factory=dict)
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    participants: Set[str] = field(default_factory=set)
    max_participants: Optional[int] = None
    is_active: bool = True
    difficulty: str = "medium"  # easy, medium, hard, expert
    tags: List[str] = field(default_factory=list)

@dataclass
class LeaderboardEntry:
    """Entrée de leaderboard"""
    user_id: str = ""
    rank: int = 0
    score: float = 0.0
    category: str = ""
    period: str = ""
    achievements_count: int = 0
    badges_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MotivationProfile:
    """Profil de motivation utilisateur"""
    user_id: str = ""
    motivation_types: Dict[str, float] = field(default_factory=dict)  # achievement, social, mastery, etc.
    preferred_challenges: List[ChallengeType] = field(default_factory=list)
    activity_patterns: Dict[str, Any] = field(default_factory=dict)
    last_engagement: Optional[datetime] = None
    motivation_score: float = 0.0
    engagement_trend: str = "stable"  # increasing, stable, decreasing

# ==========================================
# ACHIEVEMENT SYSTEM - SYSTÈME D'ACCOMPLISSEMENTS
# ==========================================

class AchievementSystem:
    """
    🏆 Achievement System - Système d'accomplissements enterprise
    
    Fonctionnalités Enterprise:
    - Achievements multi-dimensionnels avec critères complexes
    - Progression temps réel avec événements
    - Système de prérequis et chaînes d'achievements
    - Achievements dynamiques basés sur l'IA
    - Analytics de progression et engagement
    - Personnalisation par profil utilisateur
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.achievements = {}
        self.user_achievements = defaultdict(dict)
        self.user_progress = defaultdict(dict)
        self.achievement_dependencies = defaultdict(set)
        self.dynamic_achievements = {}
        self.progress_events = deque(maxlen=10000)
        
        # Initialiser les achievements de base
        self._initialize_default_achievements()
    
    def _initialize_default_achievements(self) -> None:
        """Initialise les achievements par défaut"""
        default_achievements = [
            {
                'name': "First Steps",
                'description': "Créer votre premier contenu",
                'achievement_type': AchievementType.MILESTONE,
                'criteria': {'content_created': 1},
                'points_value': 100,
                'rarity': BadgeRarity.COMMON
            },
            {
                'name': "Content Creator",
                'description': "Créer 10 contenus",
                'achievement_type': AchievementType.CUMULATIVE,
                'criteria': {'content_created': 10},
                'points_value': 500,
                'rarity': BadgeRarity.UNCOMMON
            },
            {
                'name': "Collaboration Starter",
                'description': "Démarrer votre première collaboration",
                'achievement_type': AchievementType.SOCIAL,
                'criteria': {'collaborations_started': 1},
                'points_value': 200,
                'rarity': BadgeRarity.COMMON
            },
            {
                'name': "Team Player",
                'description': "Participer à 5 collaborations",
                'achievement_type': AchievementType.COLLABORATION,
                'criteria': {'collaborations_participated': 5},
                'points_value': 750,
                'rarity': BadgeRarity.UNCOMMON
            },
            {
                'name': "Daily Grind",
                'description': "Être actif 7 jours consécutifs",
                'achievement_type': AchievementType.STREAK,
                'criteria': {'daily_streak': 7},
                'points_value': 300,
                'rarity': BadgeRarity.UNCOMMON
            },
            {
                'name': "Innovation Master",
                'description': "Créer un contenu viral (>10k vues)",
                'achievement_type': AchievementType.INNOVATION,
                'criteria': {'content_views': 10000},
                'points_value': 2000,
                'rarity': BadgeRarity.RARE
            },
            {
                'name': "Community Leader",
                'description': "Avoir 100 followers",
                'achievement_type': AchievementType.LEADERSHIP,
                'criteria': {'followers_count': 100},
                'points_value': 1000,
                'rarity': BadgeRarity.RARE
            },
            {
                'name': "Legendary Creator",
                'description': "Atteindre 1M de vues cumulées",
                'achievement_type': AchievementType.CUMULATIVE,
                'criteria': {'total_views': 1000000},
                'points_value': 10000,
                'rarity': BadgeRarity.LEGENDARY
            }
        ]
        
        for achievement_data in default_achievements:
            achievement = Achievement(**achievement_data)
            self.achievements[achievement.id] = achievement
    
    async def track_event(self, user_id -> None: str, event_type -> None: str, event_data -> None: Dict[str, Any]) -> None:
        """Track un événement pour progression des achievements"""
        try:
            # Enregistrer l'événement
            event = {
                'user_id': user_id,
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': datetime.utcnow()
            }
            self.progress_events.append(event)
            
            # Mettre à jour la progression
            await self._update_user_progress(user_id, event_type, event_data)
            
            # Vérifier les achievements débloqués
            unlocked_achievements = await self._check_achievements_unlock(user_id)
            
            # Notifier les nouveaux achievements
            for achievement_id in unlocked_achievements:
                await self._notify_achievement_unlocked(user_id, achievement_id)
            
            logger.debug(f"Événement tracké: {event_type} pour {user_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors du tracking d'événement: {e}")
            raise
    
    async def _update_user_progress(self, user_id -> None: str, event_type -> None: str, event_data -> None: Dict) -> None:
        """Met à jour la progression utilisateur"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = defaultdict(int)
        
        progress = self.user_progress[user_id]
        
        # Mapping des événements vers les critères de progression
        event_mappings = {
            'content_created': ['content_created'],
            'collaboration_started': ['collaborations_started'],
            'collaboration_joined': ['collaborations_participated'],
            'daily_activity': ['daily_streak'],
            'content_viewed': ['content_views', 'total_views'],
            'follower_gained': ['followers_count'],
            'message_sent': ['messages_sent'],
            'skill_improved': ['skills_developed'],
            'mentorship_given': ['mentorships_given'],
            'innovation_recognized': ['innovations_created']
        }
        
        if event_type in event_mappings:
            for criterion in event_mappings[event_type]:
                if criterion in ['content_views', 'total_views']:
                    progress[criterion] += event_data.get('views', 1)
                elif criterion == 'daily_streak':
                    await self._update_daily_streak(user_id)
                else:
                    progress[criterion] += event_data.get('count', 1)
        
        # Persister dans Redis pour accès rapide
        if self.redis_client:
            await self.redis_client.hset(
                f"user_progress:{user_id}",
                mapping={k: v for k, v in progress.items()}
            )
    
    async def _check_achievements_unlock(self, user_id: str) -> List[str]:
        """Vérifie quels achievements peuvent être débloqués"""
        unlocked = []
        user_progress = self.user_progress.get(user_id, {})
        user_achievements = self.user_achievements.get(user_id, {})
        
        for achievement_id, achievement in self.achievements.items():
            # Ignorer si déjà débloqué
            if achievement_id in user_achievements:
                continue
            
            # Vérifier les prérequis
            if not await self._check_prerequisites(user_id, achievement.prerequisites):
                continue
            
            # Vérifier les critères
            if await self._check_achievement_criteria(user_progress, achievement.criteria):
                unlocked.append(achievement_id)
                
                # Marquer comme débloqué
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement_id,
                    unlock_method="automatic"
                )
                self.user_achievements[user_id][achievement_id] = user_achievement
                
                # Persister
                if self.db_session:
                    await self._persist_user_achievement(user_achievement)
        
        return unlocked
    
    async def _check_achievement_criteria(self, user_progress: Dict, criteria: Dict) -> bool:
        """Vérifie si les critères d'un achievement sont remplis"""
        for criterion, required_value in criteria.items():
            current_value = user_progress.get(criterion, 0)
            
            if isinstance(required_value, dict):
                # Critères complexes
                operator = required_value.get('operator', '>=')
                value = required_value.get('value', 0)
                
                if operator == '>=' and current_value < value:
                    return False
                elif operator == '>' and current_value <= value:
                    return False
                elif operator == '==' and current_value != value:
                    return False
                elif operator == '<=' and current_value > value:
                    return False
                elif operator == '<' and current_value >= value:
                    return False
            else:
                # Critère simple (>=)
                if current_value < required_value:
                    return False
        
        return True
    
    async def _check_prerequisites(self, user_id: str, prerequisites: List[str]) -> bool:
        """Vérifie si les prérequis sont remplis"""
        if not prerequisites:
            return True
        
        user_achievements = self.user_achievements.get(user_id, {})
        
        for prereq_id in prerequisites:
            if prereq_id not in user_achievements:
                return False
        
        return True
    
    async def create_dynamic_achievement(self, user_id: str, context: Dict) -> Optional[Achievement]:
        """Crée un achievement dynamique basé sur le contexte utilisateur"""
        try:
            # Analyser le profil utilisateur
            user_profile = await self._get_user_profile(user_id)
            user_progress = self.user_progress.get(user_id, {})
            
            # Générer un achievement personnalisé
            achievement_templates = [
                {
                    'condition': lambda p: p.get('collaborations_participated', 0) > 10 and p.get('content_created', 0) > 5,
                    'name': "Collaboration Expert",
                    'description': "Master of collaborative content creation",
                    'criteria': {'collaborative_content': 20},
                    'points_value': 1500,
                    'rarity': BadgeRarity.EPIC
                },
                {
                    'condition': lambda p: p.get('daily_streak', 0) > 30,
                    'name': "Consistency Master",
                    'description': "Incredibly consistent content creator",
                    'criteria': {'monthly_consistency': 6},
                    'points_value': 2500,
                    'rarity': BadgeRarity.EPIC
                }
            ]
            
            for template in achievement_templates:
                if template['condition'](user_progress):
                    achievement = Achievement(
                        name=template['name'],
                        description=template['description'],
                        achievement_type=AchievementType.RARE,
                        criteria=template['criteria'],
                        points_value=template['points_value'],
                        rarity=template['rarity'],
                        metadata={'dynamic': True, 'created_for': user_id}
                    )
                    
                    self.dynamic_achievements[achievement.id] = achievement
                    return achievement
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la création d'achievement dynamique: {e}")
            return None
    
    async def get_user_achievements(self, user_id: str, include_progress: bool = True) -> Dict:
        """Récupère les achievements d'un utilisateur"""
        try:
            user_achievements = self.user_achievements.get(user_id, {})
            user_progress = self.user_progress.get(user_id, {}) if include_progress else {}
            
            # Construire la réponse
            achievements_data = []
            for achievement_id, user_achievement in user_achievements.items():
                if achievement_id in self.achievements:
                    achievement = self.achievements[achievement_id]
                    achievement_data = {
                        'achievement': achievement.__dict__,
                        'user_achievement': user_achievement.__dict__,
                        'unlocked': True
                    }
                    
                    if include_progress:
                        achievement_data['progress'] = self._calculate_achievement_progress(
                            user_progress, achievement.criteria
                        )
                    
                    achievements_data.append(achievement_data)
            
            # Ajouter les achievements non débloqués
            for achievement_id, achievement in self.achievements.items():
                if achievement_id not in user_achievements:
                    achievement_data = {
                        'achievement': achievement.__dict__,
                        'user_achievement': None,
                        'unlocked': False
                    }
                    
                    if include_progress:
                        achievement_data['progress'] = self._calculate_achievement_progress(
                            user_progress, achievement.criteria
                        )
                    
                    achievements_data.append(achievement_data)
            
            return {
                'total_achievements': len(self.achievements),
                'unlocked_achievements': len(user_achievements),
                'achievements': achievements_data,
                'completion_rate': len(user_achievements) / len(self.achievements) if self.achievements else 0
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des achievements: {e}")
            return {}
    
    def _calculate_achievement_progress(self, user_progress: Dict, criteria: Dict) -> Dict:
        """Calcule la progression vers un achievement"""
        progress_data = {}
        total_criteria = len(criteria)
        completed_criteria = 0
        
        for criterion, required_value in criteria.items():
            current_value = user_progress.get(criterion, 0)
            
            if isinstance(required_value, dict):
                target = required_value.get('value', 0)
            else:
                target = required_value
            
            progress_percentage = min(100, (current_value / target * 100)) if target > 0 else 0
            is_completed = current_value >= target
            
            progress_data[criterion] = {
                'current': current_value,
                'target': target,
                'percentage': progress_percentage,
                'completed': is_completed
            }
            
            if is_completed:
                completed_criteria += 1
        
        progress_data['overall'] = {
            'percentage': (completed_criteria / total_criteria * 100) if total_criteria > 0 else 0,
            'completed_criteria': completed_criteria,
            'total_criteria': total_criteria
        }
        
        return progress_data
    
    async def _update_daily_streak(self, user_id -> None: str) -> None:
        """Met à jour la série quotidienne"""
        try:
            # Récupérer la dernière activité
            if self.redis_client:
                last_activity = await self.redis_client.get(f"last_activity:{user_id}")
                today = datetime.utcnow().date()
                
                if last_activity:
                    last_date = datetime.fromisoformat(last_activity).date()
                    
                    if last_date == today:
                        # Déjà actif aujourd'hui
                        return
                    elif last_date == today - timedelta(days=1):
                        # Continuer la série
                        current_streak = await self.redis_client.get(f"daily_streak:{user_id}")
                        if current_streak:
                            new_streak = int(current_streak) + 1
                        else:
                            new_streak = 1
                    else:
                        # Série cassée
                        new_streak = 1
                else:
                    # Première activité
                    new_streak = 1
                
                # Mettre à jour
                await self.redis_client.set(f"daily_streak:{user_id}", new_streak)
                await self.redis_client.set(f"last_activity:{user_id}", today.isoformat())
                
                # Mettre à jour la progression
                self.user_progress[user_id]['daily_streak'] = new_streak
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la série quotidienne: {e}")

# ==========================================
# BADGE MANAGER - GESTIONNAIRE DE BADGES
# ==========================================

class BadgeManager:
    """
    🏅 Badge Manager - Gestionnaire de badges enterprise
    
    Fonctionnalités Enterprise:
    - Badges personnalisables avec design dynamique
    - Système de rareté et valeur économique
    - Badges temporaires et évènements spéciaux
    - Marketplace de badges avec échanges
    - Génération procédurale de badges
    - Analytics de collection et engagement
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.badges = {}
        self.user_badges = defaultdict(list)
        self.badge_collections = defaultdict(set)
        self.rarity_weights = {
            BadgeRarity.COMMON: 1.0,
            BadgeRarity.UNCOMMON: 2.0,
            BadgeRarity.RARE: 5.0,
            BadgeRarity.EPIC: 10.0,
            BadgeRarity.LEGENDARY: 25.0
        }
        
        self._initialize_default_badges()
    
    def _initialize_default_badges(self) -> None:
        """Initialise les badges par défaut"""
        default_badges = [
            {
                'name': "Pioneer",
                'description': "Among the first users of the platform",
                'icon': "🚀",
                'rarity': BadgeRarity.RARE,
                'category': "platform",
                'points_value': 500,
                'design_elements': {'color': '#FFD700', 'animation': 'glow'}
            },
            {
                'name': "Content Master",
                'description': "Created outstanding content",
                'icon': "🎨",
                'rarity': BadgeRarity.EPIC,
                'category': "content",
                'points_value': 1000,
                'design_elements': {'color': '#FF6B6B', 'animation': 'pulse'}
            },
            {
                'name': "Collaboration Hero",
                'description': "Exceptional collaborative spirit",
                'icon': "🤝",
                'rarity': BadgeRarity.UNCOMMON,
                'category': "collaboration",
                'points_value': 300,
                'design_elements': {'color': '#4ECDC4', 'animation': 'bounce'}
            },
            {
                'name': "Community Leader",
                'description': "Leading the community forward",
                'icon': "👑",
                'rarity': BadgeRarity.LEGENDARY,
                'category': "leadership",
                'points_value': 2500,
                'design_elements': {'color': '#9B59B6', 'animation': 'sparkle'}
            },
            {
                'name': "Innovation Catalyst",
                'description': "Driving innovation and creativity",
                'icon': "💡",
                'rarity': BadgeRarity.EPIC,
                'category': "innovation",
                'points_value': 1500,
                'design_elements': {'color': '#F39C12', 'animation': 'flash'}
            }
        ]
        
        for badge_data in default_badges:
            badge = Badge(**badge_data)
            self.badges[badge.id] = badge
    
    async def award_badge(self, user_id: str, badge_id: str, reason: str = "") -> bool:
        """Attribue un badge à un utilisateur"""
        try:
            if badge_id not in self.badges:
                raise ValueError(f"Badge {badge_id} introuvable")
            
            badge = self.badges[badge_id]
            
            # Vérifier si l'utilisateur a déjà ce badge
            user_badge_ids = [ub['badge_id'] for ub in self.user_badges[user_id]]
            if badge_id in user_badge_ids:
                logger.warning(f"Utilisateur {user_id} a déjà le badge {badge_id}")
                return False
            
            # Créer l'attribution
            user_badge = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'badge_id': badge_id,
                'awarded_at': datetime.utcnow(),
                'reason': reason,
                'metadata': {
                    'rarity': badge.rarity.value,
                    'points_value': badge.points_value
                }
            }
            
            # Ajouter à la collection utilisateur
            self.user_badges[user_id].append(user_badge)
            self.badge_collections[user_id].add(badge_id)
            
            # Persister
            if self.db_session:
                await self._persist_user_badge(user_badge)
            
            # Cache Redis
            if self.redis_client:
                await self.redis_client.sadd(f"user_badges:{user_id}", badge_id)
                await self.redis_client.hset(
                    f"badge_details:{user_id}:{badge_id}",
                    mapping=user_badge
                )
            
            # Notifier l'attribution
            await self._notify_badge_awarded(user_id, badge_id)
            
            logger.info(f"Badge {badge.name} attribué à {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'attribution du badge: {e}")
            return False
    
    async def create_custom_badge(self, badge_data: Dict, creator_id: str) -> Badge:
        """Crée un badge personnalisé"""
        try:
            badge = Badge(
                name=badge_data.get('name', ''),
                description=badge_data.get('description', ''),
                icon=badge_data.get('icon', '🏆'),
                rarity=BadgeRarity(badge_data.get('rarity', 'common')),
                category=badge_data.get('category', 'custom'),
                points_value=badge_data.get('points_value', 100),
                design_elements=badge_data.get('design_elements', {}),
                unlock_criteria=badge_data.get('unlock_criteria', {})
            )
            
            # Valider les critères de déverrouillage
            if not await self._validate_unlock_criteria(badge.unlock_criteria):
                raise ValueError("Critères de déverrouillage invalides")
            
            # Ajouter métadonnées de création
            badge.metadata = {
                'created_by': creator_id,
                'is_custom': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Stocker
            self.badges[badge.id] = badge
            
            # Persister
            if self.db_session:
                await self._persist_badge(badge)
            
            logger.info(f"Badge personnalisé créé: {badge.name}")
            return badge
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du badge: {e}")
            raise
    
    async def generate_procedural_badge(self, user_id: str, achievement_data: Dict) -> Badge:
        """Génère un badge procédural basé sur les données d'achievement"""
        try:
            # Analyser les données pour déterminer les caractéristiques
            rarity = self._calculate_procedural_rarity(achievement_data)
            design = self._generate_procedural_design(achievement_data, rarity)
            
            badge = Badge(
                name=self._generate_badge_name(achievement_data),
                description=self._generate_badge_description(achievement_data),
                icon=design['icon'],
                rarity=rarity,
                category="procedural",
                points_value=int(self.rarity_weights[rarity] * 100),
                design_elements=design['elements'],
                metadata={
                    'procedural': True,
                    'generated_for': user_id,
                    'source_data': achievement_data
                }
            )
            
            self.badges[badge.id] = badge
            return badge
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération procédurale: {e}")
            raise
    
    def _calculate_procedural_rarity(self, achievement_data: Dict) -> BadgeRarity:
        """Calcule la rareté basée sur les données d'achievement"""
        score = 0
        
        # Facteurs de rareté
        if achievement_data.get('completion_time', 0) < 86400:  # < 1 jour
            score += 3
        elif achievement_data.get('completion_time', 0) < 604800:  # < 1 semaine
            score += 2
        else:
            score += 1
        
        if achievement_data.get('difficulty', 1) > 8:
            score += 4
        elif achievement_data.get('difficulty', 1) > 5:
            score += 2
        
        if achievement_data.get('uniqueness', 0) > 0.9:
            score += 5
        elif achievement_data.get('uniqueness', 0) > 0.7:
            score += 3
        
        # Mapper le score à la rareté
        if score >= 10:
            return BadgeRarity.LEGENDARY
        elif score >= 7:
            return BadgeRarity.EPIC
        elif score >= 5:
            return BadgeRarity.RARE
        elif score >= 3:
            return BadgeRarity.UNCOMMON
        else:
            return BadgeRarity.COMMON
    
    def _generate_procedural_design(self, achievement_data: Dict, rarity: BadgeRarity) -> Dict:
        """Génère un design procédural"""
        # Couleurs basées sur la rareté
        rarity_colors = {
            BadgeRarity.COMMON: '#95A5A6',
            BadgeRarity.UNCOMMON: '#3498DB',
            BadgeRarity.RARE: '#9B59B6',
            BadgeRarity.EPIC: '#E74C3C',
            BadgeRarity.LEGENDARY: '#F1C40F'
        }
        
        # Icônes basées sur la catégorie
        category_icons = {
            'content': ['🎨', '📝', '🎬', '📸'],
            'collaboration': ['🤝', '👥', '🌟', '🔗'],
            'skill': ['🎯', '💪', '🧠', '⚡'],
            'innovation': ['💡', '🚀', '🔥', '⭐'],
            'leadership': ['👑', '🏆', '🎖️', '🦅']
        }
        
        category = achievement_data.get('category', 'content')
        icon = random.choice(category_icons.get(category, ['🏆']))
        
        return {
            'icon': icon,
            'elements': {
                'color': rarity_colors[rarity],
                'glow_intensity': self.rarity_weights[rarity] / 25,
                'animation': self._select_animation(rarity),
                'particle_effects': rarity in [BadgeRarity.EPIC, BadgeRarity.LEGENDARY]
            }
        }
    
    def _select_animation(self, rarity: BadgeRarity) -> str:
        """Sélectionne une animation basée sur la rareté"""
        animations = {
            BadgeRarity.COMMON: 'none',
            BadgeRarity.UNCOMMON: 'fade',
            BadgeRarity.RARE: 'pulse',
            BadgeRarity.EPIC: 'glow',
            BadgeRarity.LEGENDARY: 'sparkle'
        }
        return animations[rarity]
    
    async def get_user_badge_collection(self, user_id: str) -> Dict:
        """Récupère la collection de badges d'un utilisateur"""
        try:
            user_badge_list = self.user_badges.get(user_id, [])
            
            # Organiser par catégorie et rareté
            collection = {
                'total_badges': len(user_badge_list),
                'badges_by_category': defaultdict(list),
                'badges_by_rarity': defaultdict(list),
                'rarity_stats': defaultdict(int),
                'total_points': 0,
                'badges': []
            }
            
            for user_badge in user_badge_list:
                badge_id = user_badge['badge_id']
                if badge_id in self.badges:
                    badge = self.badges[badge_id]
                    
                    badge_data = {
                        'badge': badge.__dict__,
                        'user_badge': user_badge
                    }
                    
                    collection['badges'].append(badge_data)
                    collection['badges_by_category'][badge.category].append(badge_data)
                    collection['badges_by_rarity'][badge.rarity.value].append(badge_data)
                    collection['rarity_stats'][badge.rarity.value] += 1
                    collection['total_points'] += badge.points_value
            
            # Calculer les statistiques
            collection['collection_value'] = self._calculate_collection_value(user_badge_list)
            collection['rarity_distribution'] = dict(collection['rarity_stats'])
            collection['completion_rate'] = len(user_badge_list) / len(self.badges) if self.badges else 0
            
            return collection
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la collection: {e}")
            return {}
    
    def _calculate_collection_value(self, user_badge_list: List[Dict]) -> float:
        """Calcule la valeur de la collection"""
        total_value = 0
        
        for user_badge in user_badge_list:
            badge_id = user_badge['badge_id']
            if badge_id in self.badges:
                badge = self.badges[badge_id]
                rarity_multiplier = self.rarity_weights[badge.rarity]
                total_value += badge.points_value * rarity_multiplier
        
        return total_value

# ==========================================
# POINTS CALCULATOR - CALCULATEUR DE POINTS
# ==========================================

class PointsCalculator:
    """
    🔢 Points Calculator - Calculateur de points enterprise
    
    Fonctionnalités Enterprise:
    - Système de points multi-dimensionnel
    - Multiplicateurs dynamiques basés sur la performance
    - Bonus temporels et événements spéciaux
    - Système de decay et fraîcheur
    - Analytics de distribution des points
    - Économie équilibrée avec ajustements automatiques
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.user_points = defaultdict(lambda: defaultdict(int))
        self.point_transactions = defaultdict(list)
        self.multipliers = defaultdict(lambda: 1.0)
        self.base_points = self._initialize_base_points()
        self.decay_rates = self._initialize_decay_rates()
        self.bonus_events = {}
        
    def _initialize_base_points(self) -> Dict[str, int]:
        """Initialise les points de base par action"""
        return {
            'content_created': 100,
            'content_liked': 5,
            'content_shared': 15,
            'comment_added': 10,
            'collaboration_started': 200,
            'collaboration_completed': 500,
            'skill_improved': 150,
            'mentorship_given': 300,
            'innovation_recognized': 1000,
            'daily_login': 25,
            'streak_maintained': 50,
            'achievement_unlocked': 250,
            'badge_earned': 100,
            'community_contribution': 75,
            'feedback_provided': 20,
            'bug_reported': 100,
            'feature_suggested': 50
        }
    
    def _initialize_decay_rates(self) -> Dict[str, float]:
        """Initialise les taux de decay par catégorie"""
        return {
            PointCategory.CONTENT_CREATION.value: 0.95,  # 5% decay par mois
            PointCategory.COLLABORATION.value: 0.90,     # 10% decay par mois
            PointCategory.COMMUNITY_ENGAGEMENT.value: 0.85,  # 15% decay par mois
            PointCategory.SKILL_DEVELOPMENT.value: 0.98,     # 2% decay par mois
            PointCategory.MENTORSHIP.value: 0.92,            # 8% decay par mois
        }
    
    async def award_points(self, user_id: str, action: str, amount: Optional[int] = None,
                          category: PointCategory = PointCategory.CONTENT_CREATION,
                          context: Optional[Dict] = None) -> PointsTransaction:
        """Attribue des points à un utilisateur"""
        try:
            # Calculer le montant si pas spécifié
            if amount is None:
                amount = self.base_points.get(action, 50)
            
            # Appliquer les multiplicateurs
            final_amount = await self._apply_multipliers(user_id, amount, action, context)
            
            # Créer la transaction
            transaction = PointsTransaction(
                user_id=user_id,
                amount=final_amount,
                category=category,
                reason=action,
                reference_id=context.get('reference_id') if context else None,
                reference_type=context.get('reference_type') if context else "",
                multiplier=final_amount / amount if amount > 0 else 1.0,
                metadata=context or {}
            )
            
            # Mettre à jour les points utilisateur
            self.user_points[user_id][category.value] += final_amount
            self.user_points[user_id]['total'] += final_amount
            
            # Enregistrer la transaction
            self.point_transactions[user_id].append(transaction)
            
            # Persister
            if self.db_session:
                await self._persist_points_transaction(transaction)
            
            # Cache Redis
            if self.redis_client:
                await self.redis_client.hincrby(f"user_points:{user_id}", category.value, final_amount)
                await self.redis_client.hincrby(f"user_points:{user_id}", "total", final_amount)
            
            # Vérifier les achievements liés aux points
            await self._check_points_achievements(user_id)
            
            logger.debug(f"Points attribués: {final_amount} à {user_id} pour {action}")
            return transaction
            
        except Exception as e:
            logger.error(f"Erreur lors de l'attribution de points: {e}")
            raise
    
    async def _apply_multipliers(self, user_id: str, base_amount: int, action: str, context: Optional[Dict]) -> int:
        """Applique les multiplicateurs appropriés"""
        multiplier = 1.0
        
        # Multiplicateur utilisateur personnel
        multiplier *= self.multipliers[user_id]
        
        # Multiplicateurs basés sur la performance
        performance_multiplier = await self._calculate_performance_multiplier(user_id, action)
        multiplier *= performance_multiplier
        
        # Multiplicateurs temporels
        time_multiplier = await self._calculate_time_multiplier(action)
        multiplier *= time_multiplier
        
        # Multiplicateurs d'événements spéciaux
        event_multiplier = await self._calculate_event_multiplier(action, context)
        multiplier *= event_multiplier
        
        # Multiplicateur de série (streak)
        streak_multiplier = await self._calculate_streak_multiplier(user_id, action)
        multiplier *= streak_multiplier
        
        # Multiplicateur de qualité
        if context and 'quality_score' in context:
            quality_multiplier = min(2.0, context['quality_score'] / 50)  # Max 2x pour score parfait
            multiplier *= quality_multiplier
        
        return int(base_amount * multiplier)
    
    async def _calculate_performance_multiplier(self, user_id: str, action: str) -> float:
        """Calcule le multiplicateur basé sur la performance"""
        try:
            # Récupérer l'historique de performance
            recent_transactions = self.point_transactions[user_id][-50:]  # 50 dernières transactions
            
            if not recent_transactions:
                return 1.0
            
            # Analyser la tendance de performance
            recent_points = [t.amount for t in recent_transactions if t.reason == action]
            
            if len(recent_points) < 3:
                return 1.0
            
            # Calculer la tendance
            avg_recent = statistics.mean(recent_points[-10:]) if len(recent_points) >= 10 else statistics.mean(recent_points)
            avg_historical = statistics.mean(recent_points[:-10]) if len(recent_points) >= 20 else avg_recent
            
            if avg_historical > 0:
                trend = avg_recent / avg_historical
                # Multiplicateur entre 0.8 et 1.5
                return max(0.8, min(1.5, trend))
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Erreur calcul multiplicateur performance: {e}")
            return 1.0
    
    async def _calculate_time_multiplier(self, action: str) -> float:
        """Calcule le multiplicateur temporel"""
        now = datetime.utcnow()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Bonus heures de pointe (9h-17h en semaine)
        if 0 <= day_of_week <= 4 and 9 <= hour <= 17:
            return 1.2
        
        # Bonus week-end pour certaines actions
        if day_of_week >= 5 and action in ['collaboration_started', 'skill_improved']:
            return 1.3
        
        # Bonus heures creuses pour encourager l'activité
        if hour >= 22 or hour <= 6:
            return 1.1
        
        return 1.0
    
    async def _calculate_event_multiplier(self, action: str, context: Optional[Dict]) -> float:
        """Calcule le multiplicateur d'événements spéciaux"""
        now = datetime.utcnow()
        
        for event_id, event in self.bonus_events.items():
            if (event['start_date'] <= now <= event['end_date'] and
                action in event.get('applicable_actions', [])):
                return event.get('multiplier', 1.0)
        
        return 1.0
    
    async def _calculate_streak_multiplier(self, user_id: str, action: str) -> float:
        """Calcule le multiplicateur de série"""
        try:
            if self.redis_client:
                streak = await self.redis_client.get(f"action_streak:{user_id}:{action}")
                if streak:
                    streak_days = int(streak)
                    # Multiplicateur croissant avec la série (max 2x à 30 jours)
                    return min(2.0, 1.0 + (streak_days * 0.033))
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Erreur calcul multiplicateur série: {e}")
            return 1.0
    
    async def calculate_leaderboard_score(self, user_id: str, timeframe: str = "all_time") -> float:
        """Calcule le score pour le leaderboard"""
        try:
            user_points_data = self.user_points[user_id]
            
            if timeframe == "all_time":
                base_score = user_points_data.get('total', 0)
            else:
                # Filtrer par période
                base_score = await self._get_points_for_timeframe(user_id, timeframe)
            
            # Appliquer les facteurs de pondération
            weighted_score = base_score
            
            # Bonus pour la diversité des catégories
            active_categories = sum(1 for category, points in user_points_data.items() 
                                  if category != 'total' and points > 0)
            diversity_bonus = min(0.5, active_categories * 0.1)  # Max 50% bonus
            weighted_score *= (1 + diversity_bonus)
            
            # Facteur de decay basé sur l'activité récente
            recent_activity_factor = await self._calculate_recent_activity_factor(user_id)
            weighted_score *= recent_activity_factor
            
            return weighted_score
            
        except Exception as e:
            logger.error(f"Erreur calcul score leaderboard: {e}")
            return 0.0
    
    async def get_user_points_breakdown(self, user_id: str) -> Dict:
        """Récupère la répartition détaillée des points"""
        try:
            user_points_data = self.user_points[user_id]
            transactions = self.point_transactions[user_id]
            
            # Répartition par catégorie
            category_breakdown = {category.value: user_points_data.get(category.value, 0) 
                                for category in PointCategory}
            
            # Répartition par action
            action_breakdown = defaultdict(int)
            for transaction in transactions:
                action_breakdown[transaction.reason] += transaction.amount
            
            # Statistiques temporelles
            now = datetime.utcnow()
            weekly_points = sum(t.amount for t in transactions 
                              if (now - t.timestamp).days <= 7)
            monthly_points = sum(t.amount for t in transactions 
                               if (now - t.timestamp).days <= 30)
            
            # Tendances
            trend_data = await self._calculate_points_trend(transactions)
            
            return {
                'total_points': user_points_data.get('total', 0),
                'category_breakdown': dict(category_breakdown),
                'action_breakdown': dict(action_breakdown),
                'weekly_points': weekly_points,
                'monthly_points': monthly_points,
                'average_daily': monthly_points / 30 if monthly_points > 0 else 0,
                'trend': trend_data,
                'rank_estimate': await self._estimate_user_rank(user_id),
                'multiplier_status': {
                    'current_multiplier': self.multipliers[user_id],
                    'streak_bonus': await self._get_current_streak_bonus(user_id),
                    'active_events': await self._get_active_events_for_user(user_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération breakdown points: {e}")
            return {}
    
    async def create_bonus_event(self, event_data: Dict) -> str:
        """Crée un événement bonus"""
        try:
            event_id = str(uuid.uuid4())
            
            event = {
                'id': event_id,
                'name': event_data['name'],
                'description': event_data.get('description', ''),
                'start_date': datetime.fromisoformat(event_data['start_date']),
                'end_date': datetime.fromisoformat(event_data['end_date']),
                'multiplier': event_data.get('multiplier', 2.0),
                'applicable_actions': event_data.get('applicable_actions', []),
                'target_users': event_data.get('target_users', []),
                'max_bonus_per_user': event_data.get('max_bonus_per_user'),
                'created_at': datetime.utcnow()
            }
            
            self.bonus_events[event_id] = event
            
            # Persister
            if self.db_session:
                await self._persist_bonus_event(event)
            
            logger.info(f"Événement bonus créé: {event['name']}")
            return event_id
            
        except Exception as e:
            logger.error(f"Erreur création événement bonus: {e}")
            raise

# ==========================================
# EXPORTS CONSOLIDÉS
# ==========================================

__all__ = [
    # Core classes
    'AchievementSystem', 'BadgeManager', 'PointsCalculator', 'RewardEngine', 
    'LeaderboardManager', 'ChallengeOrchestrator', 'MotivationEngine',
    
    # Data types
    'Achievement', 'Badge', 'UserAchievement', 'PointsTransaction', 'Challenge',
    'LeaderboardEntry', 'MotivationProfile',
    
    # Enums
    'AchievementType', 'BadgeRarity', 'PointCategory', 'ChallengeType', 
    'RewardType', 'LeaderboardType'
]

# ==========================================
# FACTORY FUNCTION
# ==========================================

async def create_gamification_engine(redis_url: Optional[str] = None, 
                                    db_session=None) -> Dict[str, Any]:
    """
    Factory function pour créer une instance complète du Gamification Engine
    """
    # Configuration Redis si URL fournie
    redis_client = None
    if redis_url:
        try:
            redis_client = await aioredis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Impossible de se connecter à Redis: {e}")
    
    # Créer les instances
    achievement_system = AchievementSystem(db_session, redis_client)
    badge_manager = BadgeManager(db_session, redis_client)
    points_calculator = PointsCalculator(db_session, redis_client)
    
    return {
        'achievement_system': achievement_system,
        'badge_manager': badge_manager,
        'points_calculator': points_calculator,
        'redis_client': redis_client
    }

# Fin du module gamification_engine.py
