"""🎮 Gamification Storage Engine - Enterprise Grade
==================================================
Expert: BACKEND SENIOR + ML ENGINEER + IA PROMPT ENGINEER + GAMIFICATION
Technologies: Achievement System + Leaderboards + Rewards + AI Personalization
Architecture: Level 2 - Storage Layer - Creator Economy
Date: 2025-01-14

Enterprise storage solution for gamification with achievement tracking,
leaderboards, reward systems and AI-driven personalized experiences.
==================================================
"""

import asyncio
import logging
import time
import hashlib
import json
import uuid
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

# Optional imports with fallbacks
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Types d'achievements"""
    CONTENT_CREATION = "content_creation"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    COLLABORATION = "collaboration"
    LEARNING = "learning"
    COMMUNITY = "community"
    INNOVATION = "innovation"
    MILESTONE = "milestone"

class AchievementDifficulty(Enum):
    """Difficultés achievements"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"

class RewardType(Enum):
    """Types de récompenses"""
    POINTS = "points"
    BADGE = "badge"
    TITLE = "title"
    PREMIUM_ACCESS = "premium_access"
    CREDITS = "credits"
    FEATURE_UNLOCK = "feature_unlock"
    EXCLUSIVE_CONTENT = "exclusive_content"
    COLLABORATION_BOOST = "collaboration_boost"

class LeaderboardPeriod(Enum):
    """Périodes leaderboard"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"

class ChallengeStatus(Enum):
    """États défis"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    PAUSED = "paused"

@dataclass
class GamificationConfig:
    """Configuration moteur gamification"""
    redis_url: str = "redis://localhost:6379"
    max_pool_size: int = 25
    achievement_ttl: int = 86400 * 365  # 1 an
    leaderboard_ttl: int = 86400 * 30   # 30 jours
    enable_ai_personalization: bool = True
    enable_dynamic_challenges: bool = True
    max_active_challenges: int = 20
    point_decay_rate: float = 0.95  # Décroissance points mensuelle
    streak_bonus_multiplier: float = 1.5
    collaboration_bonus: float = 1.2

@dataclass
class Achievement:
    """Achievement utilisateur"""
    achievement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    description: str = ""
    achievement_type: AchievementType = AchievementType.CONTENT_CREATION
    difficulty: AchievementDifficulty = AchievementDifficulty.BRONZE
    icon_url: str = ""
    criteria: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0
    completed: bool = False
    completed_at: Optional[datetime] = None
    points_awarded: int = 0
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    streak_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class UserGamificationProfile:
    """Profil gamification utilisateur"""
    user_id: str
    username: str = ""
    total_points: int = 0
    level: int = 1
    experience: int = 0
    next_level_xp: int = 100
    achievements_unlocked: List[str] = field(default_factory=list)
    badges: List[Dict[str, Any]] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    active_title: str = ""
    streak_data: Dict[str, Any] = field(default_factory=dict)
    leaderboard_positions: Dict[str, int] = field(default_factory=dict)
    personal_challenges: List[str] = field(default_factory=list)
    collaboration_stats: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)

@dataclass
class Challenge:
    """Défi gamification"""
    challenge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    challenge_type: AchievementType = AchievementType.CONTENT_CREATION
    difficulty: AchievementDifficulty = AchievementDifficulty.BRONZE
    objectives: List[Dict[str, Any]] = field(default_factory=list)
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    participants: Set[str] = field(default_factory=set)
    max_participants: int = 1000
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    status: ChallengeStatus = ChallengeStatus.ACTIVE
    leaderboard: List[Dict[str, Any]] = field(default_factory=list)
    ai_personalized: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LeaderboardEntry:
    """Entrée leaderboard"""
    user_id: str
    username: str = ""
    score: Union[int, float] = 0
    rank: int = 0
    change_from_previous: int = 0
    achievements_count: int = 0
    level: int = 1
    streak: int = 0
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class GamificationStorageEngine:
    """Moteur stockage gamification enterprise"""
    
    def __init__(self, config: GamificationConfig):
        self.config = config
        self.redis_pool = None
        self.user_profiles = {}
        self.achievements_cache = {}
        self.challenges_cache = {}
        self.leaderboards_cache = {}
        self.achievement_processor = asyncio.Queue()
        
        # Métriques de performance
        self.metrics = {
            'total_users': 0,
            'total_achievements': 0,
            'active_challenges': 0,
            'total_points_awarded': 0,
            'avg_user_level': 0.0,
            'engagement_rate': 0.0
        }
        
        logger.info("GamificationStorageEngine initialisé")
    
    async def initialize(self):
        """Initialisation connexions Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis non disponible - mode dégradé")
            return
        
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.max_pool_size,
                retry_on_timeout=True
            )
            
            # Test connexion
            async with redis.Redis(connection_pool=self.redis_pool) as r:
                await r.ping()
            
            # Démarrage processus gamification
            asyncio.create_task(self._achievement_processor_worker())
            
            if self.config.enable_dynamic_challenges:
                asyncio.create_task(self._dynamic_challenge_creator())
            
            asyncio.create_task(self._leaderboard_updater())
            
            logger.info("Connexion Redis établie pour la gamification")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Redis gamification: {e}")
            self.redis_pool = None
    
    async def create_user_profile(self, user_id: str, user_data: Dict[str, Any]) -> UserGamificationProfile:
        """Création profil gamification utilisateur"""
        try:
            # Création profil
            profile = UserGamificationProfile(
                user_id=user_id,
                username=user_data.get('username', ''),
                preferences=user_data.get('preferences', {})
            )
            
            # Configuration initiale basée sur préférences
            if self.config.enable_ai_personalization:
                await self._personalize_initial_setup(profile, user_data)
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_user_profile_to_redis(profile)
            
            # Cache local
            self.user_profiles[user_id] = profile
            
            # Attribution achievements de base
            await self._award_welcome_achievements(user_id)
            
            # Mise à jour métriques
            self.metrics['total_users'] += 1
            
            logger.info(f"Profil gamification créé: {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Erreur création profil gamification {user_id}: {e}")
            raise
    
    async def award_achievement(self, user_id: str, achievement_data: Dict[str, Any]) -> str:
        """Attribution achievement"""
        try:
            # Création achievement
            achievement = Achievement(
                user_id=user_id,
                title=achievement_data['title'],
                description=achievement_data.get('description', ''),
                achievement_type=AchievementType(achievement_data.get('type', AchievementType.CONTENT_CREATION.value)),
                difficulty=AchievementDifficulty(achievement_data.get('difficulty', AchievementDifficulty.BRONZE.value)),
                criteria=achievement_data.get('criteria', {}),
                points_awarded=achievement_data.get('points', self._calculate_points_by_difficulty(
                    AchievementDifficulty(achievement_data.get('difficulty', AchievementDifficulty.BRONZE.value))
                )),
                rewards=achievement_data.get('rewards', [])
            )
            
            # Vérification si déjà obtenu
            if await self._has_achievement(user_id, achievement.title):
                logger.info(f"Achievement déjà obtenu: {achievement.title} par {user_id}")
                return ""
            
            # Marquer comme complété
            achievement.completed = True
            achievement.completed_at = datetime.now()
            achievement.progress = 1.0
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_achievement_to_redis(achievement)
            
            # Cache local
            self.achievements_cache[achievement.achievement_id] = achievement
            
            # Mise à jour profil utilisateur
            await self._update_user_profile_with_achievement(user_id, achievement)
            
            # Ajout à la queue de traitement
            await self.achievement_processor.put({
                'action': 'process_achievement',
                'achievement_id': achievement.achievement_id,
                'user_id': user_id
            })
            
            # Mise à jour métriques
            self.metrics['total_achievements'] += 1
            self.metrics['total_points_awarded'] += achievement.points_awarded
            
            logger.info(f"Achievement attribué: {achievement.title} à {user_id} ({achievement.points_awarded} points)")
            return achievement.achievement_id
            
        except Exception as e:
            logger.error(f"Erreur attribution achievement {user_id}: {e}")
            raise
    
    async def update_user_progress(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mise à jour progression utilisateur"""
        try:
            progress_updates = {
                'points_gained': 0,
                'level_up': False,
                'new_achievements': [],
                'streak_updates': {},
                'challenges_completed': []
            }
            
            # Récupération profil
            profile = await self._get_user_profile(user_id)
            if not profile:
                return progress_updates
            
            # Calcul points d'activité
            activity_points = await self._calculate_activity_points(activity_data)
            
            # Application multiplicateurs
            final_points = await self._apply_multipliers(user_id, activity_points, activity_data)
            
            # Mise à jour profil
            profile.total_points += final_points
            profile.experience += final_points
            profile.last_active = datetime.now()
            
            progress_updates['points_gained'] = final_points
            
            # Vérification level up
            if profile.experience >= profile.next_level_xp:
                await self._level_up_user(profile)
                progress_updates['level_up'] = True
            
            # Mise à jour streaks
            streak_updates = await self._update_user_streaks(profile, activity_data)
            progress_updates['streak_updates'] = streak_updates
            
            # Vérification nouveaux achievements
            new_achievements = await self._check_achievement_triggers(user_id, activity_data, profile)
            progress_updates['new_achievements'] = new_achievements
            
            # Vérification challenges
            completed_challenges = await self._check_challenge_completion(user_id, activity_data)
            progress_updates['challenges_completed'] = completed_challenges
            
            # Sauvegarde profil
            if self.redis_pool:
                await self._store_user_profile_to_redis(profile)
            
            self.user_profiles[user_id] = profile
            
            return progress_updates
            
        except Exception as e:
            logger.error(f"Erreur mise à jour progression {user_id}: {e}")
            return {'error': str(e)}
    
    async def create_challenge(self, challenge_data: Dict[str, Any]) -> str:
        """Création défi"""
        try:
            # Création challenge
            challenge = Challenge(
                title=challenge_data['title'],
                description=challenge_data.get('description', ''),
                challenge_type=AchievementType(challenge_data.get('type', AchievementType.CONTENT_CREATION.value)),
                difficulty=AchievementDifficulty(challenge_data.get('difficulty', AchievementDifficulty.BRONZE.value)),
                objectives=challenge_data.get('objectives', []),
                rewards=challenge_data.get('rewards', []),
                max_participants=challenge_data.get('max_participants', 1000),
                end_date=datetime.fromisoformat(challenge_data['end_date']) if 'end_date' in challenge_data else datetime.now() + timedelta(days=7),
                ai_personalized=challenge_data.get('ai_personalized', False)
            )
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_challenge_to_redis(challenge)
            
            # Cache local
            self.challenges_cache[challenge.challenge_id] = challenge
            
            # Notification utilisateurs intéressés
            if self.config.enable_ai_personalization:
                await self._notify_relevant_users(challenge)
            
            # Mise à jour métriques
            self.metrics['active_challenges'] += 1
            
            logger.info(f"Challenge créé: {challenge.title} ({challenge.challenge_id})")
            return challenge.challenge_id
            
        except Exception as e:
            logger.error(f"Erreur création challenge: {e}")
            raise
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Inscription à un défi"""
        try:
            challenge = await self._get_challenge(challenge_id)
            if not challenge:
                return False
            
            # Vérifications
            if challenge.status != ChallengeStatus.ACTIVE:
                return False
            
            if len(challenge.participants) >= challenge.max_participants:
                return False
            
            if user_id in challenge.participants:
                return True  # Déjà inscrit
            
            # Ajout participant
            challenge.participants.add(user_id)
            
            # Mise à jour profil utilisateur
            profile = await self._get_user_profile(user_id)
            if profile:
                profile.personal_challenges.append(challenge_id)
                
                if self.redis_pool:
                    await self._store_user_profile_to_redis(profile)
                
                self.user_profiles[user_id] = profile
            
            # Sauvegarde challenge
            if self.redis_pool:
                await self._store_challenge_to_redis(challenge)
            
            self.challenges_cache[challenge_id] = challenge
            
            logger.info(f"Utilisateur {user_id} rejoint challenge {challenge_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur inscription challenge {challenge_id}: {e}")
            return False
    
    async def get_leaderboard(self, period: LeaderboardPeriod, 
                             category: Optional[AchievementType] = None,
                             limit: int = 100) -> List[LeaderboardEntry]:
        """Récupération leaderboard"""
        try:
            # Clé cache
            cache_key = f"{period.value}_{category.value if category else 'all'}_{limit}"
            
            # Vérification cache
            if cache_key in self.leaderboards_cache:
                cached_data = self.leaderboards_cache[cache_key]
                if (datetime.now() - cached_data['cached_at']).seconds < 300:  # 5 min cache
                    return cached_data['leaderboard']
            
            # Calcul période
            period_start, period_end = self._calculate_period_dates(period)
            
            # Récupération données utilisateurs
            user_scores = await self._calculate_leaderboard_scores(
                period_start, period_end, category
            )
            
            # Tri et classement
            sorted_users = sorted(user_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            
            leaderboard = []
            for rank, (user_id, user_data) in enumerate(sorted_users[:limit], 1):
                entry = LeaderboardEntry(
                    user_id=user_id,
                    username=user_data.get('username', ''),
                    score=user_data['score'],
                    rank=rank,
                    achievements_count=user_data.get('achievements_count', 0),
                    level=user_data.get('level', 1),
                    streak=user_data.get('streak', 0),
                    last_activity=user_data.get('last_activity', datetime.now())
                )
                leaderboard.append(entry)
            
            # Mise en cache
            self.leaderboards_cache[cache_key] = {
                'leaderboard': leaderboard,
                'cached_at': datetime.now()
            }
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Erreur récupération leaderboard: {e}")
            return []
    
    async def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """Récupération achievements utilisateur"""
        try:
            achievements = []
            
            if self.redis_pool:
                async with redis.Redis(connection_pool=self.redis_pool) as r:
                    # Récupération achievements utilisateur
                    achievement_keys = await r.keys(f"gamification:achievement:{user_id}:*")
                    
                    for key in achievement_keys:
                        achievement_json = await r.get(key)
                        if achievement_json:
                            data = json.loads(achievement_json)
                            achievement = self._dict_to_achievement(data)
                            achievements.append(achievement)
            
            # Tri par date de completion
            achievements.sort(key=lambda a: a.completed_at or datetime.min, reverse=True)
            
            return achievements
            
        except Exception as e:
            logger.error(f"Erreur récupération achievements {user_id}: {e}")
            return []
    
    async def get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Recommandations personnalisées"""
        try:
            recommendations = {
                'next_achievements': [],
                'suggested_challenges': [],
                'engagement_tips': [],
                'collaboration_opportunities': []
            }
            
            # Récupération profil
            profile = await self._get_user_profile(user_id)
            if not profile:
                return recommendations
            
            # Analyse patterns utilisateur
            user_patterns = await self._analyze_user_patterns(user_id)
            
            # Achievements recommandés
            recommendations['next_achievements'] = await self._recommend_next_achievements(
                profile, user_patterns
            )
            
            # Challenges suggérés
            recommendations['suggested_challenges'] = await self._suggest_challenges(
                profile, user_patterns
            )
            
            # Tips engagement
            recommendations['engagement_tips'] = await self._generate_engagement_tips(
                profile, user_patterns
            )
            
            # Opportunités collaboration
            recommendations['collaboration_opportunities'] = await self._find_collaboration_opportunities(
                user_id, profile
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur recommandations {user_id}: {e}")
            return {'error': str(e)}
    
    def _calculate_points_by_difficulty(self, difficulty: AchievementDifficulty) -> int:
        """Calcul points par difficulté"""
        difficulty_points = {
            AchievementDifficulty.BRONZE: 10,
            AchievementDifficulty.SILVER: 25,
            AchievementDifficulty.GOLD: 50,
            AchievementDifficulty.PLATINUM: 100,
            AchievementDifficulty.DIAMOND: 250,
            AchievementDifficulty.LEGENDARY: 500
        }
        
        return difficulty_points.get(difficulty, 10)
    
    async def _personalize_initial_setup(self, profile: UserGamificationProfile, 
                                       user_data: Dict[str, Any]):
        """Personnalisation configuration initiale"""
        # Configuration basée sur intérêts
        interests = user_data.get('interests', [])
        
        if 'content_creation' in interests:
            profile.preferences['focus_content'] = True
        if 'collaboration' in interests:
            profile.preferences['focus_collaboration'] = True
        if 'monetization' in interests:
            profile.preferences['focus_revenue'] = True
    
    async def _award_welcome_achievements(self, user_id: str):
        """Attribution achievements de bienvenue"""
        welcome_achievements = [
            {
                'title': '🎉 Bienvenue dans la communauté !',
                'description': 'Premier pas dans l\'aventure créative',
                'type': AchievementType.MILESTONE.value,
                'difficulty': AchievementDifficulty.BRONZE.value,
                'points': 10
            },
            {
                'title': '👤 Profil complété',
                'description': 'Configuration du profil terminée',
                'type': AchievementType.MILESTONE.value,
                'difficulty': AchievementDifficulty.BRONZE.value,
                'points': 15
            }
        ]
        
        for achievement_data in welcome_achievements:
            await self.award_achievement(user_id, achievement_data)
    
    async def _has_achievement(self, user_id: str, title: str) -> bool:
        """Vérification possession achievement"""
        if not self.redis_pool:
            return False
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            achievement_keys = await r.keys(f"gamification:achievement:{user_id}:*")
            
            for key in achievement_keys:
                achievement_json = await r.get(key)
                if achievement_json:
                    data = json.loads(achievement_json)
                    if data.get('title') == title:
                        return True
        
        return False
    
    async def _update_user_profile_with_achievement(self, user_id: str, achievement: Achievement):
        """Mise à jour profil avec achievement"""
        profile = await self._get_user_profile(user_id)
        if profile:
            profile.achievements_unlocked.append(achievement.achievement_id)
            profile.total_points += achievement.points_awarded
            profile.experience += achievement.points_awarded
            
            # Ajout badge si applicable
            if achievement.rewards:
                for reward in achievement.rewards:
                    if reward.get('type') == RewardType.BADGE.value:
                        profile.badges.append(reward)
                    elif reward.get('type') == RewardType.TITLE.value:
                        profile.titles.append(reward.get('value', ''))
            
            # Sauvegarde
            if self.redis_pool:
                await self._store_user_profile_to_redis(profile)
            
            self.user_profiles[user_id] = profile
    
    async def _calculate_activity_points(self, activity_data: Dict[str, Any]) -> int:
        """Calcul points d'activité"""
        base_points = 0
        activity_type = activity_data.get('type', '')
        
        # Points par type d'activité
        activity_points = {
            'content_created': 20,
            'content_published': 15,
            'comment_received': 2,
            'like_received': 1,
            'share_received': 5,
            'collaboration_started': 25,
            'collaboration_completed': 50,
            'revenue_milestone': 100
        }
        
        base_points = activity_points.get(activity_type, 1)
        
        # Multiplicateurs basés sur qualité/impact
        quality_multiplier = activity_data.get('quality_score', 1.0)
        impact_multiplier = activity_data.get('impact_score', 1.0)
        
        return int(base_points * quality_multiplier * impact_multiplier)
    
    async def _apply_multipliers(self, user_id: str, base_points: int, 
                               activity_data: Dict[str, Any]) -> int:
        """Application multiplicateurs"""
        profile = await self._get_user_profile(user_id)
        if not profile:
            return base_points
        
        multiplier = 1.0
        
        # Bonus streak
        if profile.streak_data.get('current_streak', 0) > 0:
            streak_bonus = min(profile.streak_data['current_streak'] * 0.1, 1.0)
            multiplier += streak_bonus
        
        # Bonus collaboration
        if activity_data.get('is_collaboration', False):
            multiplier *= self.config.collaboration_bonus
        
        # Bonus niveau
        level_bonus = profile.level * 0.05
        multiplier += level_bonus
        
        return int(base_points * multiplier)
    
    async def _level_up_user(self, profile: UserGamificationProfile):
        """Level up utilisateur"""
        old_level = profile.level
        profile.level += 1
        profile.experience = 0
        profile.next_level_xp = int(profile.next_level_xp * 1.5)  # Progression exponentielle
        
        # Attribution achievement level up
        await self.award_achievement(profile.user_id, {
            'title': f'🆙 Niveau {profile.level} atteint !',
            'description': f'Progression du niveau {old_level} au niveau {profile.level}',
            'type': AchievementType.MILESTONE.value,
            'difficulty': AchievementDifficulty.SILVER.value,
            'points': profile.level * 10
        })
    
    async def _update_user_streaks(self, profile: UserGamificationProfile, 
                                  activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mise à jour streaks utilisateur"""
        today = datetime.now().date()
        last_activity_date = profile.last_active.date()
        
        streak_updates = {}
        
        # Streak quotidien
        if 'daily_streak' not in profile.streak_data:
            profile.streak_data['daily_streak'] = {'count': 0, 'last_date': None}
        
        daily_streak = profile.streak_data['daily_streak']
        
        if last_activity_date == today - timedelta(days=1):
            # Continuation streak
            daily_streak['count'] += 1
            streak_updates['daily_streak_continued'] = daily_streak['count']
        elif last_activity_date < today - timedelta(days=1):
            # Streak cassé
            if daily_streak['count'] > 0:
                streak_updates['daily_streak_broken'] = daily_streak['count']
            daily_streak['count'] = 1
        elif last_activity_date == today:
            # Même jour, pas de changement
            pass
        else:
            # Premier jour
            daily_streak['count'] = 1
        
        daily_streak['last_date'] = today.isoformat()
        
        return streak_updates
    
    async def _check_achievement_triggers(self, user_id: str, activity_data: Dict[str, Any],
                                         profile: UserGamificationProfile) -> List[str]:
        """Vérification déclencheurs achievements"""
        new_achievements = []
        
        # Triggers basés sur activité
        activity_type = activity_data.get('type', '')
        
        # Achievement premiers contenus
        if activity_type == 'content_created':
            content_count = activity_data.get('total_content_count', 1)
            
            if content_count == 1:
                achievement_id = await self.award_achievement(user_id, {
                    'title': '🎬 Premier contenu créé !',
                    'description': 'Félicitations pour votre première création',
                    'type': AchievementType.CONTENT_CREATION.value,
                    'difficulty': AchievementDifficulty.BRONZE.value
                })
                if achievement_id:
                    new_achievements.append(achievement_id)
            
            elif content_count == 10:
                achievement_id = await self.award_achievement(user_id, {
                    'title': '🏆 Créateur prolifique',
                    'description': '10 contenus créés avec succès',
                    'type': AchievementType.CONTENT_CREATION.value,
                    'difficulty': AchievementDifficulty.SILVER.value
                })
                if achievement_id:
                    new_achievements.append(achievement_id)
        
        # Achievement streaks
        daily_streak = profile.streak_data.get('daily_streak', {}).get('count', 0)
        if daily_streak == 7:
            achievement_id = await self.award_achievement(user_id, {
                'title': '🔥 Streak de 7 jours !',
                'description': 'Activité quotidienne pendant une semaine',
                'type': AchievementType.ENGAGEMENT.value,
                'difficulty': AchievementDifficulty.GOLD.value
            })
            if achievement_id:
                new_achievements.append(achievement_id)
        
        return new_achievements
    
    async def _check_challenge_completion(self, user_id: str, 
                                         activity_data: Dict[str, Any]) -> List[str]:
        """Vérification completion challenges"""
        completed_challenges = []
        
        profile = await self._get_user_profile(user_id)
        if not profile:
            return completed_challenges
        
        for challenge_id in profile.personal_challenges:
            challenge = await self._get_challenge(challenge_id)
            if challenge and challenge.status == ChallengeStatus.ACTIVE:
                
                # Vérification objectifs
                completion_progress = await self._check_challenge_objectives(
                    user_id, challenge, activity_data
                )
                
                if completion_progress >= 1.0:  # 100% complété
                    # Marquer challenge comme complété pour cet utilisateur
                    await self._complete_user_challenge(user_id, challenge_id)
                    completed_challenges.append(challenge_id)
        
        return completed_challenges
    
    async def _check_challenge_objectives(self, user_id: str, challenge: Challenge,
                                         activity_data: Dict[str, Any]) -> float:
        """Vérification objectifs challenge"""
        # Simulation simple (à implémenter selon logique métier)
        if challenge.challenge_type == AchievementType.CONTENT_CREATION:
            if activity_data.get('type') == 'content_created':
                return 1.0  # Objectif atteint
        
        return 0.0  # Pas encore atteint
    
    async def _complete_user_challenge(self, user_id: str, challenge_id: str):
        """Completion challenge utilisateur"""
        challenge = await self._get_challenge(challenge_id)
        if challenge:
            # Attribution récompenses
            for reward in challenge.rewards:
                if reward.get('type') == RewardType.POINTS.value:
                    profile = await self._get_user_profile(user_id)
                    if profile:
                        profile.total_points += reward.get('value', 0)
                        
                        if self.redis_pool:
                            await self._store_user_profile_to_redis(profile)
                        
                        self.user_profiles[user_id] = profile
    
    def _calculate_period_dates(self, period: LeaderboardPeriod) -> Tuple[datetime, datetime]:
        """Calcul dates période leaderboard"""
        now = datetime.now()
        
        if period == LeaderboardPeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == LeaderboardPeriod.WEEKLY:
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif period == LeaderboardPeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        else:  # ALL_TIME
            start = datetime(2020, 1, 1)  # Date arbitraire début
            end = now + timedelta(days=1)
        
        return start, end
    
    async def _calculate_leaderboard_scores(self, start_date: datetime, end_date: datetime,
                                          category: Optional[AchievementType]) -> Dict[str, Dict[str, Any]]:
        """Calcul scores leaderboard"""
        user_scores = {}
        
        # Récupération données utilisateurs
        for user_id, profile in self.user_profiles.items():
            score = profile.total_points
            
            # Filtrage par catégorie si spécifié
            if category:
                # Score spécifique à la catégorie (à implémenter)
                score = await self._calculate_category_score(user_id, category, start_date, end_date)
            
            user_scores[user_id] = {
                'score': score,
                'username': profile.username,
                'achievements_count': len(profile.achievements_unlocked),
                'level': profile.level,
                'streak': profile.streak_data.get('daily_streak', {}).get('count', 0),
                'last_activity': profile.last_active
            }
        
        return user_scores
    
    async def _calculate_category_score(self, user_id: str, category: AchievementType,
                                       start_date: datetime, end_date: datetime) -> int:
        """Calcul score par catégorie"""
        # Récupération achievements de la catégorie
        user_achievements = await self.get_user_achievements(user_id)
        
        category_score = 0
        for achievement in user_achievements:
            if (achievement.achievement_type == category and
                achievement.completed_at and
                start_date <= achievement.completed_at <= end_date):
                category_score += achievement.points_awarded
        
        return category_score
    
    async def _store_user_profile_to_redis(self, profile: UserGamificationProfile):
        """Stockage profil utilisateur Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            profile_key = f"gamification:profile:{profile.user_id}"
            profile_data = {
                'user_id': profile.user_id,
                'username': profile.username,
                'total_points': profile.total_points,
                'level': profile.level,
                'experience': profile.experience,
                'next_level_xp': profile.next_level_xp,
                'achievements_unlocked': profile.achievements_unlocked,
                'badges': profile.badges,
                'titles': profile.titles,
                'active_title': profile.active_title,
                'streak_data': profile.streak_data,
                'leaderboard_positions': profile.leaderboard_positions,
                'personal_challenges': profile.personal_challenges,
                'collaboration_stats': profile.collaboration_stats,
                'preferences': profile.preferences,
                'created_at': profile.created_at.isoformat(),
                'last_active': profile.last_active.isoformat()
            }
            
            await r.setex(profile_key, self.config.achievement_ttl, json.dumps(profile_data))
    
    async def _store_achievement_to_redis(self, achievement: Achievement):
        """Stockage achievement Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            achievement_key = f"gamification:achievement:{achievement.user_id}:{achievement.achievement_id}"
            achievement_data = {
                'achievement_id': achievement.achievement_id,
                'user_id': achievement.user_id,
                'title': achievement.title,
                'description': achievement.description,
                'achievement_type': achievement.achievement_type.value,
                'difficulty': achievement.difficulty.value,
                'icon_url': achievement.icon_url,
                'criteria': achievement.criteria,
                'progress': achievement.progress,
                'completed': achievement.completed,
                'completed_at': achievement.completed_at.isoformat() if achievement.completed_at else None,
                'points_awarded': achievement.points_awarded,
                'rewards': achievement.rewards,
                'streak_count': achievement.streak_count,
                'metadata': achievement.metadata,
                'created_at': achievement.created_at.isoformat()
            }
            
            await r.setex(achievement_key, self.config.achievement_ttl, json.dumps(achievement_data))
    
    async def _store_challenge_to_redis(self, challenge: Challenge):
        """Stockage challenge Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            challenge_key = f"gamification:challenge:{challenge.challenge_id}"
            challenge_data = {
                'challenge_id': challenge.challenge_id,
                'title': challenge.title,
                'description': challenge.description,
                'challenge_type': challenge.challenge_type.value,
                'difficulty': challenge.difficulty.value,
                'objectives': challenge.objectives,
                'rewards': challenge.rewards,
                'participants': list(challenge.participants),
                'max_participants': challenge.max_participants,
                'start_date': challenge.start_date.isoformat(),
                'end_date': challenge.end_date.isoformat(),
                'status': challenge.status.value,
                'leaderboard': challenge.leaderboard,
                'ai_personalized': challenge.ai_personalized,
                'metadata': challenge.metadata
            }
            
            await r.setex(challenge_key, self.config.leaderboard_ttl, json.dumps(challenge_data))
    
    async def _get_user_profile(self, user_id: str) -> Optional[UserGamificationProfile]:
        """Récupération profil utilisateur"""
        # Cache local d'abord
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Redis ensuite
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            profile_key = f"gamification:profile:{user_id}"
            profile_json = await r.get(profile_key)
            
            if not profile_json:
                return None
            
            data = json.loads(profile_json)
            profile = UserGamificationProfile(
                user_id=data['user_id'],
                username=data['username'],
                total_points=data['total_points'],
                level=data['level'],
                experience=data['experience'],
                next_level_xp=data['next_level_xp'],
                achievements_unlocked=data['achievements_unlocked'],
                badges=data['badges'],
                titles=data['titles'],
                active_title=data['active_title'],
                streak_data=data['streak_data'],
                leaderboard_positions=data['leaderboard_positions'],
                personal_challenges=data['personal_challenges'],
                collaboration_stats=data['collaboration_stats'],
                preferences=data['preferences'],
                created_at=datetime.fromisoformat(data['created_at']),
                last_active=datetime.fromisoformat(data['last_active'])
            )
            
            # Mise en cache
            self.user_profiles[user_id] = profile
            return profile
    
    async def _get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        """Récupération challenge"""
        # Cache local d'abord
        if challenge_id in self.challenges_cache:
            return self.challenges_cache[challenge_id]
        
        # Redis ensuite
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            challenge_key = f"gamification:challenge:{challenge_id}"
            challenge_json = await r.get(challenge_key)
            
            if not challenge_json:
                return None
            
            data = json.loads(challenge_json)
            challenge = Challenge(
                challenge_id=data['challenge_id'],
                title=data['title'],
                description=data['description'],
                challenge_type=AchievementType(data['challenge_type']),
                difficulty=AchievementDifficulty(data['difficulty']),
                objectives=data['objectives'],
                rewards=data['rewards'],
                participants=set(data['participants']),
                max_participants=data['max_participants'],
                start_date=datetime.fromisoformat(data['start_date']),
                end_date=datetime.fromisoformat(data['end_date']),
                status=ChallengeStatus(data['status']),
                leaderboard=data['leaderboard'],
                ai_personalized=data['ai_personalized'],
                metadata=data['metadata']
            )
            
            # Mise en cache
            self.challenges_cache[challenge_id] = challenge
            return challenge
    
    def _dict_to_achievement(self, data: Dict[str, Any]) -> Achievement:
        """Conversion dictionnaire vers achievement"""
        return Achievement(
            achievement_id=data['achievement_id'],
            user_id=data['user_id'],
            title=data['title'],
            description=data['description'],
            achievement_type=AchievementType(data['achievement_type']),
            difficulty=AchievementDifficulty(data['difficulty']),
            icon_url=data['icon_url'],
            criteria=data['criteria'],
            progress=data['progress'],
            completed=data['completed'],
            completed_at=datetime.fromisoformat(data['completed_at']) if data['completed_at'] else None,
            points_awarded=data['points_awarded'],
            rewards=data['rewards'],
            streak_count=data['streak_count'],
            metadata=data['metadata'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    # Méthodes d'IA et recommandations (placeholders)
    async def _analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyse patterns utilisateur"""
        return {
            'preferred_content_types': ['video', 'image'],
            'activity_hours': [18, 19, 20],
            'engagement_style': 'collaborative',
            'motivation_drivers': ['achievement', 'social']
        }
    
    async def _recommend_next_achievements(self, profile: UserGamificationProfile,
                                         patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommandation achievements suivants"""
        recommendations = []
        
        # Basé sur le niveau
        if profile.level < 5:
            recommendations.append({
                'title': '🎯 Créateur régulier',
                'description': 'Créer 5 contenus en une semaine',
                'difficulty': 'bronze',
                'estimated_points': 50
            })
        
        # Basé sur les préférences
        if profile.preferences.get('focus_collaboration'):
            recommendations.append({
                'title': '🤝 Collaborateur expert',
                'description': 'Participer à 3 projets collaboratifs',
                'difficulty': 'silver',
                'estimated_points': 75
            })
        
        return recommendations
    
    async def _suggest_challenges(self, profile: UserGamificationProfile,
                                patterns: Dict[str, Any]) -> List[str]:
        """Suggestion challenges"""
        # Récupération challenges actifs compatibles
        active_challenges = []
        
        for challenge in self.challenges_cache.values():
            if (challenge.status == ChallengeStatus.ACTIVE and
                profile.user_id not in challenge.participants):
                
                # Filtrage par préférences
                if self._is_challenge_compatible(challenge, profile, patterns):
                    active_challenges.append(challenge.challenge_id)
        
        return active_challenges[:5]  # Top 5
    
    def _is_challenge_compatible(self, challenge: Challenge, 
                               profile: UserGamificationProfile,
                               patterns: Dict[str, Any]) -> bool:
        """Vérification compatibilité challenge"""
        # Niveau approprié
        difficulty_levels = {
            AchievementDifficulty.BRONZE: [1, 2, 3],
            AchievementDifficulty.SILVER: [3, 4, 5, 6],
            AchievementDifficulty.GOLD: [5, 6, 7, 8],
            AchievementDifficulty.PLATINUM: [7, 8, 9, 10]
        }
        
        if profile.level not in difficulty_levels.get(challenge.difficulty, []):
            return False
        
        # Type compatible avec préférences
        if challenge.challenge_type == AchievementType.CONTENT_CREATION:
            return profile.preferences.get('focus_content', True)
        elif challenge.challenge_type == AchievementType.COLLABORATION:
            return profile.preferences.get('focus_collaboration', True)
        
        return True
    
    async def _generate_engagement_tips(self, profile: UserGamificationProfile,
                                       patterns: Dict[str, Any]) -> List[str]:
        """Génération tips engagement"""
        tips = []
        
        # Basé sur niveau
        if profile.level < 3:
            tips.append("💡 Complétez votre profil pour débloquer plus d'achievements")
        
        # Basé sur streaks
        if profile.streak_data.get('daily_streak', {}).get('count', 0) == 0:
            tips.append("🔥 Démarrez un streak quotidien pour gagner des bonus points")
        
        # Conseils généraux
        tips.extend([
            "🎯 Participez aux challenges pour accélérer votre progression",
            "🤝 Collaborez avec d'autres créateurs pour des bonus multiplicateurs",
            "📈 Publiez régulièrement pour maintenir votre engagement"
        ])
        
        return tips
    
    async def _find_collaboration_opportunities(self, user_id: str,
                                              profile: UserGamificationProfile) -> List[Dict[str, Any]]:
        """Recherche opportunités collaboration"""
        opportunities = []
        
        # Recherche utilisateurs compatibles
        for other_user_id, other_profile in self.user_profiles.items():
            if (other_user_id != user_id and 
                abs(other_profile.level - profile.level) <= 2):  # Niveaux similaires
                
                opportunities.append({
                    'user_id': other_user_id,
                    'username': other_profile.username,
                    'level': other_profile.level,
                    'compatibility_score': 0.8,  # Score simulé
                    'suggested_project': 'Création contenu collaboratif'
                })
        
        return opportunities[:3]  # Top 3
    
    async def _notify_relevant_users(self, challenge: Challenge):
        """Notification utilisateurs intéressés"""
        # Identification utilisateurs cibles
        target_users = []
        
        for user_id, profile in self.user_profiles.items():
            if self._is_challenge_compatible(challenge, profile, {}):
                target_users.append(user_id)
        
        # Notification (placeholder)
        logger.info(f"Challenge {challenge.title} notifié à {len(target_users)} utilisateurs")
    
    async def _achievement_processor_worker(self):
        """Worker traitement achievements"""
        while True:
            try:
                task = await self.achievement_processor.get()
                
                if task['action'] == 'process_achievement':
                    achievement_id = task['achievement_id']
                    user_id = task['user_id']
                    
                    # Traitement post-attribution
                    await self._post_process_achievement(achievement_id, user_id)
                
            except Exception as e:
                logger.error(f"Erreur achievement processor: {e}")
                await asyncio.sleep(1)
    
    async def _post_process_achievement(self, achievement_id: str, user_id: str):
        """Post-traitement achievement"""
        # Vérification achievements en cascade
        await self._check_cascade_achievements(user_id)
        
        # Mise à jour leaderboards
        await self._update_user_leaderboard_positions(user_id)
    
    async def _check_cascade_achievements(self, user_id: str):
        """Vérification achievements en cascade"""
        profile = await self._get_user_profile(user_id)
        if not profile:
            return
        
        # Achievement collectionneur
        if len(profile.achievements_unlocked) >= 10:
            await self.award_achievement(user_id, {
                'title': '🏆 Collectionneur d\'achievements',
                'description': '10 achievements débloqués',
                'type': AchievementType.MILESTONE.value,
                'difficulty': AchievementDifficulty.GOLD.value
            })
    
    async def _update_user_leaderboard_positions(self, user_id: str):
        """Mise à jour positions leaderboard"""
        # Mise à jour positions dans différents leaderboards
        for period in [LeaderboardPeriod.WEEKLY, LeaderboardPeriod.MONTHLY]:
            leaderboard = await self.get_leaderboard(period, limit=1000)
            
            # Recherche position utilisateur
            for entry in leaderboard:
                if entry.user_id == user_id:
                    profile = await self._get_user_profile(user_id)
                    if profile:
                        profile.leaderboard_positions[period.value] = entry.rank
                        
                        if self.redis_pool:
                            await self._store_user_profile_to_redis(profile)
                        
                        self.user_profiles[user_id] = profile
                    break
    
    async def _dynamic_challenge_creator(self):
        """Créateur challenges dynamiques"""
        while True:
            try:
                await asyncio.sleep(3600)  # Toutes les heures
                
                # Vérification besoin nouveaux challenges
                active_count = len([c for c in self.challenges_cache.values() 
                                  if c.status == ChallengeStatus.ACTIVE])
                
                if active_count < self.config.max_active_challenges:
                    await self._create_dynamic_challenge()
                
            except Exception as e:
                logger.error(f"Erreur dynamic challenge creator: {e}")
                await asyncio.sleep(3600)
    
    async def _create_dynamic_challenge(self):
        """Création challenge dynamique"""
        # Challenge basé sur patterns communauté
        challenge_data = {
            'title': f'🎯 Défi créatif - {datetime.now().strftime("%B %Y")}',
            'description': 'Challenge dynamique adapté à la communauté',
            'type': AchievementType.CONTENT_CREATION.value,
            'difficulty': AchievementDifficulty.SILVER.value,
            'objectives': [
                {'type': 'create_content', 'target': 3, 'timeframe': 7}
            ],
            'rewards': [
                {'type': RewardType.POINTS.value, 'value': 100},
                {'type': RewardType.BADGE.value, 'value': 'Créateur du mois'}
            ],
            'end_date': (datetime.now() + timedelta(days=14)).isoformat(),
            'ai_personalized': True
        }
        
        await self.create_challenge(challenge_data)
    
    async def _leaderboard_updater(self):
        """Mise à jour leaderboards périodique"""
        while True:
            try:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
                # Invalidation cache leaderboards
                self.leaderboards_cache.clear()
                
                # Mise à jour métriques
                if self.user_profiles:
                    avg_level = sum(p.level for p in self.user_profiles.values()) / len(self.user_profiles)
                    self.metrics['avg_user_level'] = avg_level
                
            except Exception as e:
                logger.error(f"Erreur leaderboard updater: {e}")
                await asyncio.sleep(300)
    
    async def get_gamification_statistics(self) -> Dict[str, Any]:
        """Statistiques gamification globales"""
        try:
            stats = self.metrics.copy()
            
            stats['total_users'] = len(self.user_profiles)
            stats['active_challenges'] = len([c for c in self.challenges_cache.values() 
                                            if c.status == ChallengeStatus.ACTIVE])
            
            # Statistiques engagement
            if self.user_profiles:
                recent_activity = len([
                    p for p in self.user_profiles.values()
                    if (datetime.now() - p.last_active).days <= 7
                ])
                stats['engagement_rate'] = recent_activity / len(self.user_profiles)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques gamification: {e}")
            return self.metrics

# Factory function
def create_gamification_storage_engine(
    redis_url: str = "redis://localhost:6379",
    **kwargs
) -> GamificationStorageEngine:
    """Factory pour création moteur stockage gamification"""
    config = GamificationConfig(redis_url=redis_url, **kwargs)
    return GamificationStorageEngine(config)

# Export classes principales
__all__ = [
    'GamificationStorageEngine',
    'GamificationConfig',
    'Achievement',
    'UserGamificationProfile',
    'Challenge',
    'LeaderboardEntry',
    'AchievementType',
    'AchievementDifficulty',
    'RewardType',
    'LeaderboardPeriod',
    'ChallengeStatus',
    'create_gamification_storage_engine'
]