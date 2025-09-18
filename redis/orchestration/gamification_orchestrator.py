#!/usr/bin/env python3
"""🎮 Gamification Orchestrator - Advanced Creator Engagement Gaming Platform
================================================================
Expert: GAME DESIGNER + PSYCHOLOGY EXPERT + BACKEND SENIOR + CREATOR ECONOMY SPECIALIST
Technologies: Gamification Systems + Behavioral Psychology + Reward Mechanics + Social Dynamics
Architecture: Level 3 - Engagement Intelligence Layer
Date: 2025-01-25

Ultra-advanced gamification orchestration for creator economy with psychological engagement,
achievement systems, competitive mechanics and social interaction optimization.
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
================================================================
"""

import asyncio
import logging
import json
import time
import math
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis as redis_client
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import statistics
from collections import defaultdict, deque
import random

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Types d'achievements"""
    CONTENT_CREATION = "content_creation"
    ENGAGEMENT = "engagement"
    COLLABORATION = "collaboration"
    LEARNING = "learning"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"
    SOCIAL = "social"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    SPECIAL_EVENT = "special_event"

class BadgeRarity(Enum):
    """Rareté des badges"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class ChallengeType(Enum):
    """Types de défis"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    COMMUNITY = "community"
    PERSONAL = "personal"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"

class RewardType(Enum):
    """Types de récompenses"""
    POINTS = "points"
    BADGES = "badges"
    ACHIEVEMENTS = "achievements"
    VIRTUAL_CURRENCY = "virtual_currency"
    REAL_CURRENCY = "real_currency"
    FEATURES_UNLOCK = "features_unlock"
    COSMETIC = "cosmetic"
    STATUS = "status"
    EXCLUSIVE_ACCESS = "exclusive_access"
    PHYSICAL_REWARD = "physical_reward"

class EngagementTrigger(Enum):
    """Déclencheurs d'engagement"""
    CONTENT_UPLOAD = "content_upload"
    FIRST_VIEW = "first_view"
    VIRAL_CONTENT = "viral_content"
    COLLABORATION_START = "collaboration_start"
    SKILL_IMPROVEMENT = "skill_improvement"
    CONSISTENCY_STREAK = "consistency_streak"
    COMMUNITY_INTERACTION = "community_interaction"
    GOAL_ACHIEVEMENT = "goal_achievement"
    LEVEL_UP = "level_up"
    MILESTONE_REACHED = "milestone_reached"

@dataclass
class GamificationProfile:
    """Profil de gamification d'un utilisateur"""
    user_id: str
    total_points: int = 0
    level: int = 1
    experience_points: int = 0
    streak_days: int = 0
    achievements_unlocked: List[str] = field(default_factory=list)
    badges_earned: List[str] = field(default_factory=list)
    challenges_completed: List[str] = field(default_factory=list)
    leaderboard_position: int = 0
    reputation_score: float = 0.0
    engagement_score: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    preferences: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Achievement:
    """Achievement système"""
    achievement_id: str
    name: str
    description: str
    achievement_type: AchievementType
    points_reward: int
    badge_id: Optional[str] = None
    rarity: BadgeRarity = BadgeRarity.COMMON
    requirements: Dict[str, Any] = field(default_factory=dict)
    unlock_conditions: List[Dict[str, Any]] = field(default_factory=list)
    hidden: bool = False
    repeatable: bool = False
    category: str = "general"
    icon_url: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Badge:
    """Badge système"""
    badge_id: str
    name: str
    description: str
    category: str
    rarity: BadgeRarity
    icon_url: str
    color_scheme: Dict[str, str] = field(default_factory=dict)
    unlock_requirements: Dict[str, Any] = field(default_factory=dict)
    holders_count: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Challenge:
    """Défi gamifié"""
    challenge_id: str
    name: str
    description: str
    challenge_type: ChallengeType
    difficulty: int  # 1-10
    points_reward: int
    additional_rewards: List[Dict[str, Any]] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    participants: Set[str] = field(default_factory=set)
    completions: Dict[str, datetime] = field(default_factory=dict)
    is_active: bool = True
    category: str = "general"

@dataclass
class Leaderboard:
    """Classement"""
    leaderboard_id: str
    name: str
    description: str
    category: str
    ranking_metric: str  # points, level, achievements, etc.
    time_period: str  # daily, weekly, monthly, all_time
    rankings: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class Reward:
    """Récompense"""
    reward_id: str
    name: str
    description: str
    reward_type: RewardType
    value: Union[int, float, str]
    cost_points: int
    availability: int = -1  # -1 = unlimited
    claimed_count: int = 0
    requirements: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    is_active: bool = True

class PsychologyEngine:
    """Moteur psychologique d'engagement"""
    
    def __init__(self):
        self.engagement_patterns = {
            "achiever": {"points": 1.2, "badges": 1.5, "leaderboards": 1.3},
            "explorer": {"achievements": 1.4, "content_discovery": 1.3, "variety": 1.2},
            "socializer": {"collaboration": 1.5, "community": 1.4, "social_rewards": 1.3},
            "competitor": {"leaderboards": 1.6, "challenges": 1.4, "status": 1.3}
        }
        
        self.motivation_triggers = {
            "autonomy": ["choice_rewards", "customization", "self_direction"],
            "mastery": ["skill_progression", "learning_paths", "improvement_tracking"],
            "purpose": ["community_impact", "meaningful_goals", "social_contribution"]
        }
    
    async def analyze_user_psychology(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyser le profil psychologique d'un utilisateur"""
        try:
            # Analyze user behavior patterns
            behavior_scores = {
                "achiever": 0.0,
                "explorer": 0.0,
                "socializer": 0.0,
                "competitor": 0.0
            }
            
            # Achiever signals
            if activity_data.get("achievements_focus", 0) > 0.7:
                behavior_scores["achiever"] += 0.3
            if activity_data.get("completion_rate", 0) > 0.8:
                behavior_scores["achiever"] += 0.2
            if activity_data.get("points_focus", 0) > 0.6:
                behavior_scores["achiever"] += 0.2
            
            # Explorer signals
            if activity_data.get("feature_exploration", 0) > 0.7:
                behavior_scores["explorer"] += 0.3
            if activity_data.get("content_variety", 0) > 0.6:
                behavior_scores["explorer"] += 0.2
            if activity_data.get("experimental_behavior", 0) > 0.5:
                behavior_scores["explorer"] += 0.2
            
            # Socializer signals
            if activity_data.get("collaboration_frequency", 0) > 0.6:
                behavior_scores["socializer"] += 0.3
            if activity_data.get("community_interaction", 0) > 0.7:
                behavior_scores["socializer"] += 0.2
            if activity_data.get("sharing_behavior", 0) > 0.5:
                behavior_scores["socializer"] += 0.2
            
            # Competitor signals
            if activity_data.get("leaderboard_focus", 0) > 0.7:
                behavior_scores["competitor"] += 0.3
            if activity_data.get("challenge_participation", 0) > 0.6:
                behavior_scores["competitor"] += 0.2
            if activity_data.get("ranking_improvement", 0) > 0.5:
                behavior_scores["competitor"] += 0.2
            
            # Normalize scores
            total_score = sum(behavior_scores.values())
            if total_score > 0:
                behavior_scores = {k: v / total_score for k, v in behavior_scores.items()}
            
            logger.info(f"Psychology analysis completed for user {user_id}")
            return behavior_scores
            
        except Exception as e:
            logger.error(f"Error analyzing user psychology: {e}")
            return {"achiever": 0.25, "explorer": 0.25, "socializer": 0.25, "competitor": 0.25}
    
    async def calculate_motivation_score(self, user_id: str, recent_activities: List[Dict[str, Any]]) -> float:
        """Calculer le score de motivation"""
        try:
            if not recent_activities:
                return 0.5  # Neutral score
            
            # Analyze recent engagement patterns
            engagement_indicators = {
                "frequency": len(recent_activities) / 30,  # Activities per day over 30 days
                "consistency": self._calculate_consistency(recent_activities),
                "progress": self._calculate_progress_trend(recent_activities),
                "social_engagement": self._calculate_social_engagement(recent_activities)
            }
            
            # Weight factors
            weights = {
                "frequency": 0.25,
                "consistency": 0.3,
                "progress": 0.25,
                "social_engagement": 0.2
            }
            
            # Calculate weighted score
            motivation_score = sum(
                engagement_indicators.get(factor, 0) * weight 
                for factor, weight in weights.items()
            )
            
            # Normalize to 0-1 range
            motivation_score = max(0.0, min(1.0, motivation_score))
            
            return motivation_score
            
        except Exception as e:
            logger.error(f"Error calculating motivation score: {e}")
            return 0.5
    
    def _calculate_consistency(self, activities: List[Dict[str, Any]]) -> float:
        """Calculer la consistance d'activité"""
        if len(activities) < 7:
            return 0.5
        
        # Group activities by day
        daily_activities = defaultdict(int)
        for activity in activities:
            day = activity.get("timestamp", datetime.now()).date()
            daily_activities[day] += 1
        
        # Calculate coefficient of variation (lower = more consistent)
        daily_counts = list(daily_activities.values())
        if len(daily_counts) < 2:
            return 0.5
        
        mean_activities = statistics.mean(daily_counts)
        std_activities = statistics.stdev(daily_counts)
        
        if mean_activities == 0:
            return 0.0
        
        cv = std_activities / mean_activities
        consistency_score = max(0.0, 1.0 - cv)  # Lower CV = higher consistency
        
        return consistency_score
    
    def _calculate_progress_trend(self, activities: List[Dict[str, Any]]) -> float:
        """Calculer la tendance de progression"""
        if len(activities) < 5:
            return 0.5
        
        # Sort activities by timestamp
        sorted_activities = sorted(activities, key=lambda x: x.get("timestamp", datetime.now()))
        
        # Calculate progress indicators over time
        progress_values = []
        for activity in sorted_activities:
            progress_value = activity.get("points_earned", 0) + activity.get("achievements_unlocked", 0) * 10
            progress_values.append(progress_value)
        
        # Calculate trend using simple linear regression slope
        if len(progress_values) < 2:
            return 0.5
        
        x_values = list(range(len(progress_values)))
        n = len(progress_values)
        
        sum_x = sum(x_values)
        sum_y = sum(progress_values)
        sum_xy = sum(x * y for x, y in zip(x_values, progress_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.5
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Normalize slope to 0-1 range (positive slope = improvement)
        progress_score = max(0.0, min(1.0, (slope + 10) / 20))  # Assuming slope range -10 to +10
        
        return progress_score
    
    def _calculate_social_engagement(self, activities: List[Dict[str, Any]]) -> float:
        """Calculer l'engagement social"""
        social_activities = [
            activity for activity in activities 
            if activity.get("type") in ["collaboration", "community_interaction", "sharing", "mentoring"]
        ]
        
        if not activities:
            return 0.0
        
        social_ratio = len(social_activities) / len(activities)
        return min(1.0, social_ratio * 2)  # Double weight for social activities

class AchievementEngine:
    """Moteur d'achievements"""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.achievement_checkers: Dict[str, Callable] = {}
        self._initialize_default_achievements()
    
    def _initialize_default_achievements(self):
        """Initialiser les achievements par défaut"""
        default_achievements = [
            {
                "achievement_id": "first_content",
                "name": "Premier Contenu",
                "description": "Publiez votre premier contenu",
                "achievement_type": AchievementType.CONTENT_CREATION,
                "points_reward": 100,
                "requirements": {"content_count": 1},
                "rarity": BadgeRarity.COMMON
            },
            {
                "achievement_id": "viral_creator",
                "name": "Créateur Viral",
                "description": "Atteignez 10,000 vues sur un contenu",
                "achievement_type": AchievementType.ENGAGEMENT,
                "points_reward": 1000,
                "requirements": {"single_content_views": 10000},
                "rarity": BadgeRarity.RARE
            },
            {
                "achievement_id": "collaboration_master",
                "name": "Maître de la Collaboration",
                "description": "Participez à 5 collaborations différentes",
                "achievement_type": AchievementType.COLLABORATION,
                "points_reward": 500,
                "requirements": {"collaborations_count": 5},
                "rarity": BadgeRarity.UNCOMMON
            },
            {
                "achievement_id": "consistency_champion",
                "name": "Champion de la Consistance",
                "description": "Publiez du contenu 30 jours d'affilée",
                "achievement_type": AchievementType.CONSISTENCY,
                "points_reward": 2000,
                "requirements": {"consecutive_days": 30},
                "rarity": BadgeRarity.EPIC
            },
            {
                "achievement_id": "community_builder",
                "name": "Bâtisseur de Communauté",
                "description": "Aidez 100 autres créateurs",
                "achievement_type": AchievementType.COMMUNITY,
                "points_reward": 1500,
                "requirements": {"help_count": 100},
                "rarity": BadgeRarity.RARE
            }
        ]
        
        for ach_data in default_achievements:
            achievement = Achievement(**ach_data)
            self.achievements[achievement.achievement_id] = achievement
    
    async def check_achievements(self, user_id: str, activity_data: Dict[str, Any]) -> List[str]:
        """Vérifier les achievements débloqués"""
        try:
            unlocked_achievements = []
            
            for achievement_id, achievement in self.achievements.items():
                if await self._check_achievement_unlock(user_id, achievement, activity_data):
                    unlocked_achievements.append(achievement_id)
            
            logger.info(f"Checked achievements for user {user_id}: {len(unlocked_achievements)} unlocked")
            return unlocked_achievements
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []
    
    async def _check_achievement_unlock(self, user_id: str, achievement: Achievement, activity_data: Dict[str, Any]) -> bool:
        """Vérifier si un achievement est débloqué"""
        try:
            # Check if already unlocked (if not repeatable)
            user_achievements = activity_data.get("achievements_unlocked", [])
            if not achievement.repeatable and achievement.achievement_id in user_achievements:
                return False
            
            # Check requirements
            for req_key, req_value in achievement.requirements.items():
                user_value = activity_data.get(req_key, 0)
                
                if isinstance(req_value, (int, float)):
                    if user_value < req_value:
                        return False
                elif isinstance(req_value, str):
                    if str(user_value) != req_value:
                        return False
                elif isinstance(req_value, list):
                    if user_value not in req_value:
                        return False
            
            # Check unlock conditions (more complex logic)
            for condition in achievement.unlock_conditions:
                if not await self._evaluate_unlock_condition(user_id, condition, activity_data):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking achievement unlock: {e}")
            return False
    
    async def _evaluate_unlock_condition(self, user_id: str, condition: Dict[str, Any], activity_data: Dict[str, Any]) -> bool:
        """Évaluer une condition de déverrouillage"""
        condition_type = condition.get("type", "simple")
        
        if condition_type == "simple":
            key = condition.get("key")
            operator = condition.get("operator", ">=")
            value = condition.get("value")
            
            user_value = activity_data.get(key, 0)
            
            if operator == ">=":
                return user_value >= value
            elif operator == ">":
                return user_value > value
            elif operator == "<=":
                return user_value <= value
            elif operator == "<":
                return user_value < value
            elif operator == "==":
                return user_value == value
            elif operator == "!=":
                return user_value != value
        
        elif condition_type == "time_based":
            # Check if condition is met within timeframe
            timeframe = condition.get("timeframe_days", 30)
            cutoff_date = datetime.now() - timedelta(days=timeframe)
            
            recent_data = {
                k: v for k, v in activity_data.items() 
                if isinstance(v, datetime) and v >= cutoff_date
            }
            
            return len(recent_data) >= condition.get("min_occurrences", 1)
        
        return False

class ChallengeEngine:
    """Moteur de défis"""
    
    def __init__(self):
        self.active_challenges: Dict[str, Challenge] = {}
        self.challenge_templates = self._create_challenge_templates()
    
    def _create_challenge_templates(self) -> List[Dict[str, Any]]:
        """Créer des templates de défis"""
        return [
            {
                "name": "Défi Créativité Quotidienne",
                "description": "Publiez du contenu créatif pendant 7 jours consécutifs",
                "challenge_type": ChallengeType.WEEKLY,
                "difficulty": 3,
                "points_reward": 500,
                "requirements": {"consecutive_posts": 7, "creativity_score": 0.7}
            },
            {
                "name": "Marathon de Collaboration",
                "description": "Collaborez avec 3 créateurs différents cette semaine",
                "challenge_type": ChallengeType.WEEKLY,
                "difficulty": 5,
                "points_reward": 750,
                "requirements": {"unique_collaborators": 3}
            },
            {
                "name": "Maître de l'Engagement",
                "description": "Obtenez un taux d'engagement de 10% aujourd'hui",
                "challenge_type": ChallengeType.DAILY,
                "difficulty": 6,
                "points_reward": 200,
                "requirements": {"engagement_rate": 0.1}
            },
            {
                "name": "Innovateur du Mois",
                "description": "Essayez 5 nouveaux formats de contenu ce mois",
                "challenge_type": ChallengeType.MONTHLY,
                "difficulty": 7,
                "points_reward": 1500,
                "requirements": {"new_formats": 5}
            }
        ]
    
    async def generate_personalized_challenges(self, user_id: str, psychology_profile: Dict[str, float]) -> List[Challenge]:
        """Générer des défis personnalisés"""
        try:
            personalized_challenges = []
            
            # Get dominant psychology type
            dominant_type = max(psychology_profile, key=psychology_profile.get)
            
            # Select appropriate challenge templates
            selected_templates = self._select_templates_for_psychology(dominant_type)
            
            for template in selected_templates[:3]:  # Limit to 3 challenges
                challenge_id = str(uuid.uuid4())
                
                # Customize challenge based on psychology
                customized_template = self._customize_challenge_for_user(template, psychology_profile)
                
                challenge = Challenge(
                    challenge_id=challenge_id,
                    name=customized_template["name"],
                    description=customized_template["description"],
                    challenge_type=customized_template["challenge_type"],
                    difficulty=customized_template["difficulty"],
                    points_reward=customized_template["points_reward"],
                    requirements=customized_template["requirements"],
                    start_date=datetime.now(),
                    end_date=self._calculate_end_date(customized_template["challenge_type"])
                )
                
                personalized_challenges.append(challenge)
                self.active_challenges[challenge_id] = challenge
            
            logger.info(f"Generated {len(personalized_challenges)} personalized challenges for user {user_id}")
            return personalized_challenges
            
        except Exception as e:
            logger.error(f"Error generating personalized challenges: {e}")
            return []
    
    def _select_templates_for_psychology(self, psychology_type: str) -> List[Dict[str, Any]]:
        """Sélectionner les templates selon le profil psychologique"""
        if psychology_type == "achiever":
            # Focus on completion and points
            return [t for t in self.challenge_templates if t["points_reward"] >= 500]
        elif psychology_type == "explorer":
            # Focus on variety and experimentation
            return [t for t in self.challenge_templates if "new" in t["name"].lower() or "different" in t["description"].lower()]
        elif psychology_type == "socializer":
            # Focus on collaboration and community
            return [t for t in self.challenge_templates if "collaboration" in t["description"].lower() or "community" in t["description"].lower()]
        elif psychology_type == "competitor":
            # Focus on competitive and ranking challenges
            return [t for t in self.challenge_templates if t["difficulty"] >= 5]
        else:
            return self.challenge_templates
    
    def _customize_challenge_for_user(self, template: Dict[str, Any], psychology_profile: Dict[str, float]) -> Dict[str, Any]:
        """Personnaliser un défi pour l'utilisateur"""
        customized = template.copy()
        
        # Adjust difficulty based on competitive score
        competitive_score = psychology_profile.get("competitor", 0.25)
        if competitive_score > 0.7:
            customized["difficulty"] = min(10, customized["difficulty"] + 1)
            customized["points_reward"] = int(customized["points_reward"] * 1.2)
        elif competitive_score < 0.3:
            customized["difficulty"] = max(1, customized["difficulty"] - 1)
        
        # Adjust social requirements based on socializer score
        socializer_score = psychology_profile.get("socializer", 0.25)
        if socializer_score > 0.6 and "collaborators" in customized["requirements"]:
            customized["requirements"]["collaborators"] = max(1, customized["requirements"]["collaborators"] - 1)
        
        return customized
    
    def _calculate_end_date(self, challenge_type: ChallengeType) -> datetime:
        """Calculer la date de fin selon le type de défi"""
        now = datetime.now()
        
        if challenge_type == ChallengeType.DAILY:
            return now.replace(hour=23, minute=59, second=59) 
        elif challenge_type == ChallengeType.WEEKLY:
            days_until_sunday = (6 - now.weekday()) % 7
            if days_until_sunday == 0:  # Today is Sunday
                days_until_sunday = 7
            return now + timedelta(days=days_until_sunday)
        elif challenge_type == ChallengeType.MONTHLY:
            # End of current month
            next_month = now.replace(day=28) + timedelta(days=4)
            return next_month - timedelta(days=next_month.day)
        elif challenge_type == ChallengeType.SEASONAL:
            return now + timedelta(days=90)
        else:
            return now + timedelta(days=7)  # Default to weekly
    
    async def check_challenge_completion(self, user_id: str, challenge_id: str, activity_data: Dict[str, Any]) -> bool:
        """Vérifier la completion d'un défi"""
        try:
            if challenge_id not in self.active_challenges:
                return False
            
            challenge = self.active_challenges[challenge_id]
            
            # Check if challenge is still active
            if not challenge.is_active or datetime.now() > challenge.end_date:
                return False
            
            # Check if user has already completed
            if user_id in challenge.completions:
                return False
            
            # Check requirements
            for req_key, req_value in challenge.requirements.items():
                user_value = activity_data.get(req_key, 0)
                
                if isinstance(req_value, (int, float)):
                    if user_value < req_value:
                        return False
                elif isinstance(req_value, str):
                    if str(user_value) != req_value:
                        return False
            
            # Mark as completed
            challenge.completions[user_id] = datetime.now()
            
            logger.info(f"Challenge {challenge_id} completed by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error checking challenge completion: {e}")
            return False

class RewardSystem:
    """Système de récompenses"""
    
    def __init__(self):
        self.available_rewards: Dict[str, Reward] = {}
        self.user_redemptions: Dict[str, List[str]] = defaultdict(list)
        self._initialize_default_rewards()
    
    def _initialize_default_rewards(self):
        """Initialiser les récompenses par défaut"""
        default_rewards = [
            {
                "reward_id": "profile_badge",
                "name": "Badge Profil Premium",
                "description": "Badge spécial affiché sur votre profil",
                "reward_type": RewardType.COSMETIC,
                "value": "premium_badge",
                "cost_points": 1000
            },
            {
                "reward_id": "feature_unlock",
                "name": "Fonctionnalité Premium",
                "description": "Déverrouillage d'une fonctionnalité avancée",
                "reward_type": RewardType.FEATURES_UNLOCK,
                "value": "advanced_analytics",
                "cost_points": 2500
            },
            {
                "reward_id": "virtual_currency",
                "name": "Crédits Plateforme",
                "description": "Crédits utilisables sur la plateforme",
                "reward_type": RewardType.VIRTUAL_CURRENCY,
                "value": 100,
                "cost_points": 500
            },
            {
                "reward_id": "exclusive_access",
                "name": "Accès Beta",
                "description": "Accès anticipé aux nouvelles fonctionnalités",
                "reward_type": RewardType.EXCLUSIVE_ACCESS,
                "value": "beta_access",
                "cost_points": 5000,
                "availability": 50
            }
        ]
        
        for reward_data in default_rewards:
            reward = Reward(**reward_data)
            self.available_rewards[reward.reward_id] = reward
    
    async def redeem_reward(self, user_id: str, reward_id: str, user_points: int) -> Dict[str, Any]:
        """Échanger des points contre une récompense"""
        try:
            if reward_id not in self.available_rewards:
                return {"success": False, "error": "Reward not found"}
            
            reward = self.available_rewards[reward_id]
            
            # Check if reward is available
            if not reward.is_active:
                return {"success": False, "error": "Reward not available"}
            
            if reward.expires_at and datetime.now() > reward.expires_at:
                return {"success": False, "error": "Reward expired"}
            
            if reward.availability != -1 and reward.claimed_count >= reward.availability:
                return {"success": False, "error": "Reward out of stock"}
            
            # Check if user has enough points
            if user_points < reward.cost_points:
                return {"success": False, "error": "Insufficient points"}
            
            # Check requirements
            if reward.requirements:
                # This would check additional requirements like level, achievements, etc.
                pass
            
            # Process redemption
            reward.claimed_count += 1
            self.user_redemptions[user_id].append(reward_id)
            
            redemption_result = {
                "success": True,
                "reward": {
                    "id": reward.reward_id,
                    "name": reward.name,
                    "type": reward.reward_type.value,
                    "value": reward.value
                },
                "points_deducted": reward.cost_points,
                "redemption_time": datetime.now().isoformat()
            }
            
            logger.info(f"Reward {reward_id} redeemed by user {user_id}")
            return redemption_result
            
        except Exception as e:
            logger.error(f"Error redeeming reward: {e}")
            return {"success": False, "error": str(e)}

class GamificationOrchestrator:
    """🎮 Orchestrateur de Gamification Enterprise pour Creators"""
    
    def __init__(self, redis_client: redis_client.Redis):
        self.redis_client = redis_client
        self.user_profiles: Dict[str, GamificationProfile] = {}
        self.psychology_engine = PsychologyEngine()
        self.achievement_engine = AchievementEngine()
        self.challenge_engine = ChallengeEngine()
        self.reward_system = RewardSystem()
        self.leaderboards: Dict[str, Leaderboard] = {}
        
        # Initialize default leaderboards
        self._initialize_leaderboards()
        
        logger.info("🎮 Gamification Orchestrator initialized")
    
    def _initialize_leaderboards(self):
        """Initialiser les leaderboards par défaut"""
        default_leaderboards = [
            {
                "leaderboard_id": "points_weekly",
                "name": "Top Points - Semaine",
                "description": "Classement des points cette semaine",
                "category": "points",
                "ranking_metric": "weekly_points",
                "time_period": "weekly"
            },
            {
                "leaderboard_id": "engagement_monthly",
                "name": "Top Engagement - Mois",
                "description": "Classement d'engagement ce mois",
                "category": "engagement",
                "ranking_metric": "monthly_engagement",
                "time_period": "monthly"
            },
            {
                "leaderboard_id": "achievements_all_time",
                "name": "Maîtres des Achievements",
                "description": "Plus grand nombre d'achievements débloqués",
                "category": "achievements",
                "ranking_metric": "total_achievements",
                "time_period": "all_time"
            }
        ]
        
        for lb_data in default_leaderboards:
            leaderboard = Leaderboard(**lb_data)
            self.leaderboards[leaderboard.leaderboard_id] = leaderboard
    
    async def initialize_user_profile(self, user_id: str, initial_data: Dict[str, Any] = None) -> GamificationProfile:
        """Initialiser le profil de gamification d'un utilisateur"""
        try:
            if user_id in self.user_profiles:
                return self.user_profiles[user_id]
            
            profile = GamificationProfile(
                user_id=user_id,
                preferences=initial_data or {},
                statistics={"content_created": 0, "collaborations": 0, "engagement_total": 0}
            )
            
            self.user_profiles[user_id] = profile
            
            # Store in Redis
            await self.redis_client.hset(
                f"gamification:profile:{user_id}",
                mapping={
                    "total_points": str(profile.total_points),
                    "level": str(profile.level),
                    "experience_points": str(profile.experience_points),
                    "streak_days": str(profile.streak_days),
                    "created_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Gamification profile initialized for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error initializing user profile: {e}")
            return None
    
    async def process_user_activity(self, user_id: str, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traiter une activité utilisateur et déclencher les mécanismes de gamification"""
        try:
            # Ensure user profile exists
            if user_id not in self.user_profiles:
                await self.initialize_user_profile(user_id)
            
            profile = self.user_profiles[user_id]
            
            # Update profile statistics
            await self._update_profile_statistics(profile, activity_type, activity_data)
            
            # Calculate points for activity
            points_earned = await self._calculate_activity_points(activity_type, activity_data, profile)
            
            # Update profile
            profile.total_points += points_earned
            profile.experience_points += points_earned
            profile.last_activity = datetime.now()
            
            # Check for level up
            level_up = await self._check_level_up(profile)
            
            # Update streak
            await self._update_streak(profile, activity_type)
            
            # Check achievements
            unlocked_achievements = await self.achievement_engine.check_achievements(
                user_id, {**activity_data, **profile.statistics}
            )
            
            # Add achievements to profile
            for achievement_id in unlocked_achievements:
                if achievement_id not in profile.achievements_unlocked:
                    profile.achievements_unlocked.append(achievement_id)
                    achievement = self.achievement_engine.achievements.get(achievement_id)
                    if achievement:
                        profile.total_points += achievement.points_reward
            
            # Check active challenges
            completed_challenges = await self._check_active_challenges(user_id, activity_data)
            
            # Update leaderboards
            await self._update_leaderboards(user_id, profile)
            
            # Generate psychology-based recommendations
            psychology_profile = await self.psychology_engine.analyze_user_psychology(
                user_id, {**activity_data, **profile.statistics}
            )
            
            # Calculate engagement triggers
            triggers = await self._identify_engagement_triggers(activity_type, activity_data, profile)
            
            # Prepare response
            response = {
                "user_id": user_id,
                "activity_processed": activity_type,
                "points_earned": points_earned,
                "total_points": profile.total_points,
                "level": profile.level,
                "level_up": level_up,
                "experience_points": profile.experience_points,
                "streak_days": profile.streak_days,
                "unlocked_achievements": unlocked_achievements,
                "completed_challenges": completed_challenges,
                "psychology_profile": psychology_profile,
                "engagement_triggers": triggers,
                "next_level_progress": await self._calculate_level_progress(profile),
                "recommendations": await self._generate_recommendations(user_id, psychology_profile)
            }
            
            # Store updated profile
            await self._store_profile_update(user_id, profile)
            
            logger.info(f"Activity processed for user {user_id}: {points_earned} points earned")
            return response
            
        except Exception as e:
            logger.error(f"Error processing user activity: {e}")
            return {"error": str(e)}
    
    async def _update_profile_statistics(self, profile: GamificationProfile, activity_type: str, activity_data: Dict[str, Any]):
        """Mettre à jour les statistiques du profil"""
        if activity_type == "content_creation":
            profile.statistics["content_created"] = profile.statistics.get("content_created", 0) + 1
            profile.statistics["total_views"] = profile.statistics.get("total_views", 0) + activity_data.get("views", 0)
        
        elif activity_type == "collaboration":
            profile.statistics["collaborations"] = profile.statistics.get("collaborations", 0) + 1
        
        elif activity_type == "engagement":
            profile.statistics["engagement_total"] = profile.statistics.get("engagement_total", 0) + activity_data.get("engagement_count", 0)
        
        elif activity_type == "learning":
            profile.statistics["courses_completed"] = profile.statistics.get("courses_completed", 0) + 1
        
        # Update last activity timestamp
        profile.last_activity = datetime.now()
    
    async def _calculate_activity_points(self, activity_type: str, activity_data: Dict[str, Any], profile: GamificationProfile) -> int:
        """Calculer les points pour une activité"""
        base_points = {
            "content_creation": 50,
            "collaboration": 100,
            "engagement": 10,
            "learning": 75,
            "community_help": 25,
            "challenge_completion": 200,
            "achievement_unlock": 150
        }
        
        points = base_points.get(activity_type, 10)
        
        # Apply multipliers based on quality and performance
        if activity_type == "content_creation":
            views = activity_data.get("views", 0)
            if views > 10000:
                points *= 3
            elif views > 1000:
                points *= 2
            
            engagement_rate = activity_data.get("engagement_rate", 0)
            if engagement_rate > 0.1:  # 10% engagement rate
                points = int(points * 1.5)
        
        # Level-based bonus
        level_bonus = profile.level * 2
        points += level_bonus
        
        # Streak bonus
        if profile.streak_days > 7:
            streak_multiplier = 1 + (profile.streak_days / 100)  # 1% bonus per streak day
            points = int(points * streak_multiplier)
        
        return max(1, points)  # Minimum 1 point
    
    async def _check_level_up(self, profile: GamificationProfile) -> bool:
        """Vérifier et traiter les montées de niveau"""
        # Calculate required XP for next level (exponential growth)
        required_xp = 100 * (profile.level ** 1.5)
        
        if profile.experience_points >= required_xp:
            profile.level += 1
            profile.experience_points -= int(required_xp)
            
            # Level up bonus
            bonus_points = profile.level * 100
            profile.total_points += bonus_points
            
            logger.info(f"User {profile.user_id} leveled up to level {profile.level}")
            return True
        
        return False
    
    async def _update_streak(self, profile: GamificationProfile, activity_type: str):
        """Mettre à jour la streak d'activité"""
        today = datetime.now().date()
        last_activity_date = profile.last_activity.date()
        
        if activity_type in ["content_creation", "collaboration", "learning"]:
            if last_activity_date == today:
                # Same day, no streak change
                pass
            elif last_activity_date == today - timedelta(days=1):
                # Consecutive day, increment streak
                profile.streak_days += 1
            else:
                # Streak broken, reset
                profile.streak_days = 1
    
    async def _check_active_challenges(self, user_id: str, activity_data: Dict[str, Any]) -> List[str]:
        """Vérifier les défis actifs"""
        completed_challenges = []
        
        for challenge_id, challenge in self.challenge_engine.active_challenges.items():
            if user_id in challenge.participants:
                is_completed = await self.challenge_engine.check_challenge_completion(
                    user_id, challenge_id, activity_data
                )
                if is_completed:
                    completed_challenges.append(challenge_id)
        
        return completed_challenges
    
    async def _update_leaderboards(self, user_id: str, profile: GamificationProfile):
        """Mettre à jour les leaderboards"""
        for leaderboard_id, leaderboard in self.leaderboards.items():
            if leaderboard.ranking_metric == "total_points":
                # Update user position in points leaderboard
                user_entry = {
                    "user_id": user_id,
                    "score": profile.total_points,
                    "level": profile.level,
                    "achievements": len(profile.achievements_unlocked)
                }
                
                # Remove existing entry
                leaderboard.rankings = [r for r in leaderboard.rankings if r["user_id"] != user_id]
                
                # Add new entry and sort
                leaderboard.rankings.append(user_entry)
                leaderboard.rankings.sort(key=lambda x: x["score"], reverse=True)
                
                # Keep only top 100
                leaderboard.rankings = leaderboard.rankings[:100]
                
                # Update user's leaderboard position
                for i, entry in enumerate(leaderboard.rankings):
                    if entry["user_id"] == user_id:
                        profile.leaderboard_position = i + 1
                        break
    
    async def _identify_engagement_triggers(self, activity_type: str, activity_data: Dict[str, Any], profile: GamificationProfile) -> List[str]:
        """Identifier les déclencheurs d'engagement"""
        triggers = []
        
        if activity_type == "content_creation":
            if activity_data.get("views", 0) > 1000:
                triggers.append(EngagementTrigger.VIRAL_CONTENT.value)
            
            if profile.statistics.get("content_created", 0) == 1:
                triggers.append(EngagementTrigger.FIRST_VIEW.value)
        
        if activity_type == "collaboration":
            triggers.append(EngagementTrigger.COLLABORATION_START.value)
        
        if profile.streak_days > 0 and profile.streak_days % 7 == 0:
            triggers.append(EngagementTrigger.CONSISTENCY_STREAK.value)
        
        if len(profile.achievements_unlocked) > 0:
            triggers.append(EngagementTrigger.GOAL_ACHIEVEMENT.value)
        
        return triggers
    
    async def _calculate_level_progress(self, profile: GamificationProfile) -> Dict[str, Any]:
        """Calculer le progrès vers le niveau suivant"""
        required_xp = 100 * (profile.level ** 1.5)
        progress_percentage = (profile.experience_points / required_xp) * 100
        
        return {
            "current_level": profile.level,
            "next_level": profile.level + 1,
            "current_xp": profile.experience_points,
            "required_xp": int(required_xp),
            "progress_percentage": min(100, round(progress_percentage, 2)),
            "xp_remaining": max(0, int(required_xp) - profile.experience_points)
        }
    
    async def _generate_recommendations(self, user_id: str, psychology_profile: Dict[str, float]) -> List[str]:
        """Générer des recommandations personnalisées"""
        recommendations = []
        
        dominant_type = max(psychology_profile, key=psychology_profile.get)
        
        if dominant_type == "achiever":
            recommendations.extend([
                "Complétez vos défis actifs pour maximiser vos points",
                "Vérifiez les achievements disponibles - vous êtes proche de plusieurs déverrouillages",
                "Participez aux challenges hebdomadaires pour des récompenses bonus"
            ])
        
        elif dominant_type == "explorer":
            recommendations.extend([
                "Essayez de nouveaux formats de contenu pour débloquer des achievements",
                "Explorez les fonctionnalités beta disponibles dans la boutique de récompenses",
                "Participez à des collaborations avec des créateurs de différents domaines"
            ])
        
        elif dominant_type == "socializer":
            recommendations.extend([
                "Rejoignez des défis communautaires pour rencontrer d'autres créateurs",
                "Aidez d'autres créateurs pour débloquer l'achievement 'Community Builder'",
                "Participez aux discussions dans les forums pour gagner des points sociaux"
            ])
        
        elif dominant_type == "competitor":
            recommendations.extend([
                "Vérifiez votre position dans les leaderboards - vous pouvez grimper!",
                "Participez aux défis de difficulté élevée pour plus de points",
                "Défiez d'autres créateurs dans des compétitions créatives"
            ])
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    async def _store_profile_update(self, user_id: str, profile: GamificationProfile):
        """Stocker la mise à jour du profil"""
        await self.redis_client.hset(
            f"gamification:profile:{user_id}",
            mapping={
                "total_points": str(profile.total_points),
                "level": str(profile.level),
                "experience_points": str(profile.experience_points),
                "streak_days": str(profile.streak_days),
                "achievements_count": str(len(profile.achievements_unlocked)),
                "leaderboard_position": str(profile.leaderboard_position),
                "last_activity": profile.last_activity.isoformat(),
                "statistics": json.dumps(profile.statistics)
            }
        )
    
    async def get_user_gamification_status(self, user_id: str) -> Dict[str, Any]:
        """Obtenir le statut de gamification d'un utilisateur"""
        try:
            if user_id not in self.user_profiles:
                await self.initialize_user_profile(user_id)
            
            profile = self.user_profiles[user_id]
            
            # Get psychology analysis
            psychology_profile = await self.psychology_engine.analyze_user_psychology(
                user_id, profile.statistics
            )
            
            # Get available challenges
            available_challenges = await self.challenge_engine.generate_personalized_challenges(
                user_id, psychology_profile
            )
            
            # Get level progress
            level_progress = await self._calculate_level_progress(profile)
            
            # Get available rewards
            affordable_rewards = [
                reward for reward in self.reward_system.available_rewards.values()
                if reward.cost_points <= profile.total_points and reward.is_active
            ]
            
            status = {
                "user_id": user_id,
                "profile": {
                    "total_points": profile.total_points,
                    "level": profile.level,
                    "experience_points": profile.experience_points,
                    "streak_days": profile.streak_days,
                    "achievements_unlocked": len(profile.achievements_unlocked),
                    "leaderboard_position": profile.leaderboard_position,
                    "engagement_score": profile.engagement_score,
                    "reputation_score": profile.reputation_score
                },
                "level_progress": level_progress,
                "psychology_profile": psychology_profile,
                "available_challenges": [
                    {
                        "challenge_id": c.challenge_id,
                        "name": c.name,
                        "description": c.description,
                        "difficulty": c.difficulty,
                        "points_reward": c.points_reward,
                        "end_date": c.end_date.isoformat()
                    } for c in available_challenges
                ],
                "affordable_rewards": [
                    {
                        "reward_id": r.reward_id,
                        "name": r.name,
                        "description": r.description,
                        "cost_points": r.cost_points,
                        "type": r.reward_type.value
                    } for r in affordable_rewards[:10]  # Limit to 10
                ],
                "recent_achievements": profile.achievements_unlocked[-5:],  # Last 5 achievements
                "statistics": profile.statistics,
                "recommendations": await self._generate_recommendations(user_id, psychology_profile)
            }
            
            logger.info(f"Gamification status retrieved for user {user_id}")
            return status
            
        except Exception as e:
            logger.error(f"Error getting gamification status: {e}")
            return {"error": str(e)}
    
    async def redeem_reward(self, user_id: str, reward_id: str) -> Dict[str, Any]:
        """Échanger des points contre une récompense"""
        try:
            if user_id not in self.user_profiles:
                return {"success": False, "error": "User profile not found"}
            
            profile = self.user_profiles[user_id]
            
            # Attempt redemption
            redemption_result = await self.reward_system.redeem_reward(
                user_id, reward_id, profile.total_points
            )
            
            if redemption_result.get("success"):
                # Deduct points from profile
                profile.total_points -= redemption_result["points_deducted"]
                
                # Store updated profile
                await self._store_profile_update(user_id, profile)
                
                logger.info(f"Reward {reward_id} redeemed by user {user_id}")
            
            return redemption_result
            
        except Exception as e:
            logger.error(f"Error redeeming reward: {e}")
            return {"success": False, "error": str(e)}

# Export
__all__ = [
    'GamificationOrchestrator',
    'AchievementType',
    'BadgeRarity',
    'ChallengeType',
    'RewardType',
    'EngagementTrigger',
    'GamificationProfile',
    'Achievement',
    'Badge',
    'Challenge',
    'Leaderboard',
    'Reward'
]