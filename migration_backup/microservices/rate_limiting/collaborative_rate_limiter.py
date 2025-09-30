"""
Collaborative Rate Limiter Enterprise - Ainflue
===============================================
Rate Limiter pour collaboration créateurs et gamification.
Shared quotas + collaboration bonuses + gamification rewards.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import statistics

from .distributed_rate_limiter import (
    DistributedRateLimiter, RateLimitConfig, RateLimitResult, 
    RateLimitAlgorithm, RateLimitStatus
)

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Types de collaboration"""
    JOINT_PROJECT = "joint_project"
    GUEST_FEATURE = "guest_feature"
    REMIX = "remix"
    COVER = "cover"
    DUET = "duet"
    COMPILATION = "compilation"
    LIVE_COLLABORATION = "live_collaboration"
    CROSS_PROMOTION = "cross_promotion"

class TeamRole(Enum):
    """Rôles dans équipe"""
    LEADER = "leader"
    MEMBER = "member"
    GUEST = "guest"
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    VIEWER = "viewer"

class AchievementType(Enum):
    """Types d'achievements gamification"""
    UPLOAD_MILESTONE = "upload_milestone"
    COLLABORATION_COUNT = "collaboration_count"
    ENGAGEMENT_RATE = "engagement_rate"
    QUALITY_SCORE = "quality_score"
    CONSISTENCY = "consistency"
    INNOVATION = "innovation"
    COMMUNITY_SUPPORT = "community_support"
    MENTOR = "mentor"

class BonusType(Enum):
    """Types de bonus"""
    RATE_LIMIT_INCREASE = "rate_limit_increase"
    PROCESSING_PRIORITY = "processing_priority"
    STORAGE_BONUS = "storage_bonus"
    BANDWIDTH_BONUS = "bandwidth_bonus"
    FEATURE_ACCESS = "feature_access"
    COST_REDUCTION = "cost_reduction"

@dataclass
class CollaborationTeam:
    """Équipe collaboration"""
    team_id: str
    team_name: str
    leader_id: str
    members: List[str]
    shared_quota: int
    used_quota: int = 0
    collaboration_type: CollaborationType = CollaborationType.JOINT_PROJECT
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    team_settings: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def remaining_quota(self) -> int:
        return max(0, self.shared_quota - self.used_quota)
    
    @property
    def quota_utilization(self) -> float:
        if self.shared_quota <= 0:
            return 0.0
        return min(100.0, (self.used_quota / self.shared_quota) * 100)
    
    @property
    def is_active(self) -> bool:
        return self.expires_at is None or datetime.now() < self.expires_at

@dataclass
class UserAchievement:
    """Achievement utilisateur"""
    achievement_id: str
    user_id: str
    achievement_type: AchievementType
    level: int
    earned_at: datetime
    description: str
    bonus_granted: List[BonusType]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GamificationBonus:
    """Bonus gamification"""
    bonus_id: str
    user_id: str
    bonus_type: BonusType
    multiplier: float
    expires_at: datetime
    source_achievement: str
    active: bool = True
    
    @property
    def is_valid(self) -> bool:
        return self.active and datetime.now() < self.expires_at

@dataclass
class CollabRequest:
    """Request collaboration"""
    requester_id: str
    team_id: Optional[str] = None
    collaboration_type: CollaborationType = CollaborationType.JOINT_PROJECT
    requested_quota: int = 1
    priority: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CollabLimitResult:
    """Résultat rate limiting collaboratif"""
    allowed: bool
    individual_quota_used: int
    shared_quota_used: int
    collaboration_bonus_applied: float
    gamification_bonus_applied: float
    team_contribution: Dict[str, int]
    rate_limit_result: RateLimitResult
    achievements_earned: List[UserAchievement] = field(default_factory=list)
    bonuses_applied: List[GamificationBonus] = field(default_factory=list)
    team_status: Optional[Dict[str, Any]] = None
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BonusAllocation:
    """Allocation bonus"""
    allocation_id: str
    user_id: str
    bonus_type: BonusType
    amount: float
    duration_hours: int
    conditions: List[str]
    auto_renew: bool = False

class AchievementEngine:
    """Moteur achievements gamification"""
    
    def __init__(self):
        self.user_stats = defaultdict(lambda: {
            "uploads_count": 0,
            "collaborations_count": 0,
            "total_engagement": 0,
            "quality_scores": [],
            "consistency_streak": 0,
            "mentor_sessions": 0
        })
        self.user_achievements = defaultdict(list)
        self.achievement_definitions = self._load_achievement_definitions()
        self.logger = logging.getLogger(__name__)
    
    def _load_achievement_definitions(self) -> Dict[AchievementType, Dict[str, Any]]:
        """Chargement définitions achievements"""
        return {
            AchievementType.UPLOAD_MILESTONE: {
                "levels": {
                    1: {"threshold": 10, "bonus": 1.2},
                    2: {"threshold": 50, "bonus": 1.4},
                    3: {"threshold": 100, "bonus": 1.6},
                    4: {"threshold": 500, "bonus": 1.8},
                    5: {"threshold": 1000, "bonus": 2.0}
                },
                "bonus_types": [BonusType.RATE_LIMIT_INCREASE, BonusType.STORAGE_BONUS]
            },
            AchievementType.COLLABORATION_COUNT: {
                "levels": {
                    1: {"threshold": 5, "bonus": 1.3},
                    2: {"threshold": 20, "bonus": 1.5},
                    3: {"threshold": 50, "bonus": 1.7},
                    4: {"threshold": 100, "bonus": 2.0}
                },
                "bonus_types": [BonusType.RATE_LIMIT_INCREASE, BonusType.PROCESSING_PRIORITY]
            },
            AchievementType.ENGAGEMENT_RATE: {
                "levels": {
                    1: {"threshold": 10, "bonus": 1.2},  # 10% avg engagement
                    2: {"threshold": 25, "bonus": 1.4},  # 25% avg engagement
                    3: {"threshold": 50, "bonus": 1.6},  # 50% avg engagement
                    4: {"threshold": 75, "bonus": 1.8}   # 75% avg engagement
                },
                "bonus_types": [BonusType.BANDWIDTH_BONUS, BonusType.FEATURE_ACCESS]
            },
            AchievementType.QUALITY_SCORE: {
                "levels": {
                    1: {"threshold": 70, "bonus": 1.2},  # 70% quality score
                    2: {"threshold": 80, "bonus": 1.4},
                    3: {"threshold": 90, "bonus": 1.6},
                    4: {"threshold": 95, "bonus": 1.8}
                },
                "bonus_types": [BonusType.PROCESSING_PRIORITY, BonusType.COST_REDUCTION]
            },
            AchievementType.CONSISTENCY: {
                "levels": {
                    1: {"threshold": 7, "bonus": 1.2},   # 7 days streak
                    2: {"threshold": 30, "bonus": 1.4},  # 30 days streak
                    3: {"threshold": 90, "bonus": 1.6},  # 90 days streak
                    4: {"threshold": 365, "bonus": 1.8}  # 365 days streak
                },
                "bonus_types": [BonusType.RATE_LIMIT_INCREASE, BonusType.STORAGE_BONUS]
            },
            AchievementType.MENTOR: {
                "levels": {
                    1: {"threshold": 5, "bonus": 1.5},   # 5 mentoring sessions
                    2: {"threshold": 20, "bonus": 1.7},
                    3: {"threshold": 50, "bonus": 2.0},
                    4: {"threshold": 100, "bonus": 2.5}
                },
                "bonus_types": [BonusType.RATE_LIMIT_INCREASE, BonusType.FEATURE_ACCESS]
            }
        }
    
    async def check_achievements(self, user_id: str, action_data: Dict[str, Any]) -> List[UserAchievement]:
        """Vérification achievements"""
        earned_achievements = []
        
        try:
            # Update user stats
            await self._update_user_stats(user_id, action_data)
            
            # Check chaque type achievement
            for achievement_type, definition in self.achievement_definitions.items():
                achievement = await self._check_specific_achievement(
                    user_id, achievement_type, definition
                )
                if achievement:
                    earned_achievements.append(achievement)
            
            return earned_achievements
            
        except Exception as e:
            self.logger.error(f"Achievement check failed for {user_id}: {e}")
            return []
    
    async def _update_user_stats(self, user_id: str, action_data: Dict[str, Any]):
        """Update statistiques utilisateur"""
        stats = self.user_stats[user_id]
        
        # Update selon type action
        action_type = action_data.get("action_type", "")
        
        if action_type == "upload":
            stats["uploads_count"] += 1
            
        elif action_type == "collaboration":
            stats["collaborations_count"] += 1
            
        elif action_type == "engagement":
            engagement_rate = action_data.get("engagement_rate", 0)
            stats["total_engagement"] += engagement_rate
            
        elif action_type == "quality_score":
            quality_score = action_data.get("quality_score", 0)
            stats["quality_scores"].append(quality_score)
            
        elif action_type == "daily_activity":
            stats["consistency_streak"] += 1
            
        elif action_type == "mentoring":
            stats["mentor_sessions"] += 1
    
    async def _check_specific_achievement(self, user_id: str, achievement_type: AchievementType,
                                        definition: Dict[str, Any]) -> Optional[UserAchievement]:
        """Vérification achievement spécifique"""
        stats = self.user_stats[user_id]
        current_achievements = [a for a in self.user_achievements[user_id] 
                              if a.achievement_type == achievement_type]
        current_level = max([a.level for a in current_achievements] + [0])
        
        # Détermination valeur actuelle selon type
        if achievement_type == AchievementType.UPLOAD_MILESTONE:
            current_value = stats["uploads_count"]
        elif achievement_type == AchievementType.COLLABORATION_COUNT:
            current_value = stats["collaborations_count"]
        elif achievement_type == AchievementType.ENGAGEMENT_RATE:
            current_value = stats["total_engagement"] / max(1, stats["uploads_count"])
        elif achievement_type == AchievementType.QUALITY_SCORE:
            current_value = statistics.mean(stats["quality_scores"]) if stats["quality_scores"] else 0
        elif achievement_type == AchievementType.CONSISTENCY:
            current_value = stats["consistency_streak"]
        elif achievement_type == AchievementType.MENTOR:
            current_value = stats["mentor_sessions"]
        else:
            return None
        
        # Vérification niveau suivant
        levels = definition["levels"]
        next_level = current_level + 1
        
        if next_level in levels:
            threshold = levels[next_level]["threshold"]
            
            if current_value >= threshold:
                # Achievement earned!
                bonus_multiplier = levels[next_level]["bonus"]
                bonus_types = definition["bonus_types"]
                
                achievement = UserAchievement(
                    achievement_id=str(uuid.uuid4()),
                    user_id=user_id,
                    achievement_type=achievement_type,
                    level=next_level,
                    earned_at=datetime.now(),
                    description=f"{achievement_type.value} level {next_level} achieved",
                    bonus_granted=bonus_types,
                    metadata={
                        "threshold": threshold,
                        "current_value": current_value,
                        "bonus_multiplier": bonus_multiplier
                    }
                )
                
                self.user_achievements[user_id].append(achievement)
                return achievement
        
        return None

class TeamManager:
    """Gestionnaire équipes collaboration"""
    
    def __init__(self):
        self.teams = {}  # team_id -> CollaborationTeam
        self.user_teams = defaultdict(list)  # user_id -> [team_ids]
        self.team_history = defaultdict(lambda: deque(maxlen=100))
        self.logger = logging.getLogger(__name__)
    
    async def create_team(self, leader_id: str, team_name: str, 
                         collaboration_type: CollaborationType,
                         initial_quota: int = 1000) -> str:
        """Création équipe collaboration"""
        try:
            team_id = str(uuid.uuid4())
            
            # Calcul quota basé sur type collaboration
            quota_multipliers = {
                CollaborationType.JOINT_PROJECT: 2.0,
                CollaborationType.LIVE_COLLABORATION: 3.0,
                CollaborationType.COMPILATION: 1.5,
                CollaborationType.GUEST_FEATURE: 1.2
            }
            
            multiplier = quota_multipliers.get(collaboration_type, 1.0)
            shared_quota = int(initial_quota * multiplier)
            
            # Calcul expiration
            expiration_hours = {
                CollaborationType.LIVE_COLLABORATION: 24,
                CollaborationType.GUEST_FEATURE: 168,  # 1 week
                CollaborationType.JOINT_PROJECT: 720,  # 30 days
                CollaborationType.COMPILATION: 336     # 2 weeks
            }
            
            expires_at = datetime.now() + timedelta(
                hours=expiration_hours.get(collaboration_type, 168)
            )
            
            team = CollaborationTeam(
                team_id=team_id,
                team_name=team_name,
                leader_id=leader_id,
                members=[leader_id],
                shared_quota=shared_quota,
                collaboration_type=collaboration_type,
                expires_at=expires_at,
                team_settings={
                    "auto_renew": False,
                    "max_members": 10,
                    "require_approval": True
                }
            )
            
            self.teams[team_id] = team
            self.user_teams[leader_id].append(team_id)
            
            self.logger.info(f"Team created: {team_id} by {leader_id}")
            return team_id
            
        except Exception as e:
            self.logger.error(f"Team creation failed: {e}")
            raise
    
    async def add_team_member(self, team_id: str, user_id: str, role: TeamRole = TeamRole.MEMBER) -> bool:
        """Ajout membre équipe"""
        try:
            team = self.teams.get(team_id)
            if not team:
                return False
            
            if user_id in team.members:
                return True  # Already member
            
            # Vérification limite membres
            max_members = team.team_settings.get("max_members", 10)
            if len(team.members) >= max_members:
                return False
            
            # Ajout membre
            team.members.append(user_id)
            self.user_teams[user_id].append(team_id)
            
            # Bonus quota pour nouveau membre
            bonus_quota = team.shared_quota // 10  # 10% bonus per new member
            team.shared_quota += bonus_quota
            
            self.logger.info(f"User {user_id} added to team {team_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Add team member failed: {e}")
            return False
    
    async def consume_team_quota(self, team_id: str, amount: int) -> bool:
        """Consommation quota équipe"""
        team = self.teams.get(team_id)
        if not team or not team.is_active:
            return False
        
        if team.remaining_quota >= amount:
            team.used_quota += amount
            return True
        
        return False
    
    async def get_team_contribution(self, team_id: str) -> Dict[str, int]:
        """Contribution chaque membre équipe"""
        # Simulation - dans une vraie implémentation, tracker contributions réelles
        team = self.teams.get(team_id)
        if not team:
            return {}
        
        # Distribution égale pour simplification
        total_used = team.used_quota
        members_count = len(team.members)
        avg_contribution = total_used // max(1, members_count)
        
        return {member_id: avg_contribution for member_id in team.members}

class CollaborativeRateLimiter:
    """
    Rate Limiter pour collaboration créateurs et gamification.
    Shared quotas + collaboration bonuses + gamification rewards.
    """
    
    def __init__(self, distributed_limiter: DistributedRateLimiter):
        self.distributed_limiter = distributed_limiter
        self.achievement_engine = AchievementEngine()
        self.team_manager = TeamManager()
        
        # Bonus système
        self.active_bonuses = defaultdict(list)  # user_id -> [GamificationBonus]
        self.collaboration_multipliers = {
            CollaborationType.JOINT_PROJECT: 1.5,
            CollaborationType.LIVE_COLLABORATION: 2.0,
            CollaborationType.GUEST_FEATURE: 1.3,
            CollaborationType.REMIX: 1.2,
            CollaborationType.DUET: 1.4,
            CollaborationType.COMPILATION: 1.6
        }
        
        # Métriques collaboration
        self.collab_metrics = {
            "total_collaborative_requests": 0,
            "teams_active": 0,
            "bonuses_applied": 0,
            "achievements_earned": 0,
            "shared_quota_used": 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._background_tasks = []
        self._stop_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialisation collaborative rate limiter"""
        try:
            # Initialisation distributed limiter base
            await self.distributed_limiter.initialize()
            
            # Démarrage background tasks
            await self._start_background_tasks()
            
            self.logger.info("Collaborative rate limiter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Collaborative rate limiter initialization failed: {e}")
            return False
    
    async def manage_collaborative_limits(self, request: CollabRequest) -> CollabLimitResult:
        """Rate limiting pour collaborations avec shared quotas"""
        start_time = time.time()
        self.collab_metrics["total_collaborative_requests"] += 1
        
        try:
            # 1. Vérification équipe si spécifiée
            team_status = None
            shared_quota_used = 0
            team_contribution = {}
            
            if request.team_id:
                team = self.team_manager.teams.get(request.team_id)
                if team and team.is_active:
                    # Tentative consommation quota équipe
                    if await self.team_manager.consume_team_quota(request.team_id, request.requested_quota):
                        shared_quota_used = request.requested_quota
                        team_contribution = await self.team_manager.get_team_contribution(request.team_id)
                        self.collab_metrics["shared_quota_used"] += request.requested_quota
                        
                        team_status = {
                            "team_id": request.team_id,
                            "team_name": team.team_name,
                            "remaining_quota": team.remaining_quota,
                            "utilization": team.quota_utilization,
                            "members_count": len(team.members)
                        }
            
            # 2. Calcul bonus collaboration
            collaboration_bonus = 1.0
            if request.collaboration_type in self.collaboration_multipliers:
                collaboration_bonus = self.collaboration_multipliers[request.collaboration_type]
            
            # 3. Vérification achievements et bonus gamification
            action_data = {
                "action_type": "collaboration",
                "collaboration_type": request.collaboration_type.value,
                "team_involved": request.team_id is not None
            }
            
            achievements_earned = await self.achievement_engine.check_achievements(
                request.requester_id, action_data
            )
            
            # 4. Application bonus gamification
            gamification_bonus = await self._calculate_gamification_bonus(
                request.requester_id, achievements_earned
            )
            
            # 5. Calcul quota individuel ajusté
            individual_quota_needed = max(1, int(request.requested_quota // collaboration_bonus))
            if shared_quota_used > 0:
                individual_quota_needed = 0  # Quota équipe utilisé
            
            # 6. Vérification rate limiting distribué
            rate_limit_result = await self.distributed_limiter.check_rate_limit(
                f"collab:{request.requester_id}",
                individual_quota_needed,
                {
                    "collaboration_type": request.collaboration_type.value,
                    "team_id": request.team_id,
                    "collaboration_bonus": collaboration_bonus,
                    "gamification_bonus": gamification_bonus
                }
            )
            
            # 7. Application bonus gamification au résultat
            if gamification_bonus > 1.0 and not rate_limit_result.allowed:
                # Retry avec quota réduit grâce au bonus
                reduced_quota = max(1, int(individual_quota_needed / gamification_bonus))
                rate_limit_result = await self.distributed_limiter.check_rate_limit(
                    f"collab:{request.requester_id}",
                    reduced_quota,
                    {"gamification_bonus_applied": True}
                )
            
            # 8. Génération bonuses si achievements earned
            bonuses_applied = []
            if achievements_earned:
                bonuses_applied = await self._generate_bonuses_from_achievements(
                    request.requester_id, achievements_earned
                )
                self.collab_metrics["bonuses_applied"] += len(bonuses_applied)
                self.collab_metrics["achievements_earned"] += len(achievements_earned)
            
            # 9. Génération recommendations
            recommendations = await self._generate_collaboration_recommendations(
                request, team_status, achievements_earned
            )
            
            # 10. Construction résultat final
            result = CollabLimitResult(
                allowed=rate_limit_result.allowed or shared_quota_used > 0,
                individual_quota_used=individual_quota_needed if rate_limit_result.allowed else 0,
                shared_quota_used=shared_quota_used,
                collaboration_bonus_applied=collaboration_bonus,
                gamification_bonus_applied=gamification_bonus,
                team_contribution=team_contribution,
                rate_limit_result=rate_limit_result,
                achievements_earned=achievements_earned,
                bonuses_applied=bonuses_applied,
                team_status=team_status,
                recommendations=recommendations,
                metadata={
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "collaboration_type": request.collaboration_type.value,
                    "team_involved": request.team_id is not None,
                    "bonuses_count": len(bonuses_applied)
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Collaborative rate limiting failed for {request.requester_id}: {e}")
            return CollabLimitResult(
                allowed=False,
                individual_quota_used=0,
                shared_quota_used=0,
                collaboration_bonus_applied=1.0,
                gamification_bonus_applied=1.0,
                team_contribution={},
                rate_limit_result=RateLimitResult(
                    status=RateLimitStatus.ERROR,
                    allowed=False
                ),
                metadata={"error": str(e)}
            )
    
    async def apply_gamification_bonuses(self, user_achievements: List[UserAchievement]) -> List[BonusAllocation]:
        """Application bonus rate limiting basés sur gamification"""
        bonus_allocations = []
        
        try:
            for achievement in user_achievements:
                # Génération bonus selon achievement
                bonuses = await self._create_bonuses_for_achievement(achievement)
                bonus_allocations.extend(bonuses)
            
            return bonus_allocations
            
        except Exception as e:
            self.logger.error(f"Gamification bonus application failed: {e}")
            return []
    
    async def _calculate_gamification_bonus(self, user_id: str, 
                                         achievements_earned: List[UserAchievement]) -> float:
        """Calcul bonus gamification total"""
        base_bonus = 1.0
        
        # Bonus depuis achievements actifs
        active_bonuses = [b for b in self.active_bonuses[user_id] if b.is_valid]
        
        for bonus in active_bonuses:
            if bonus.bonus_type == BonusType.RATE_LIMIT_INCREASE:
                base_bonus *= bonus.multiplier
        
        # Bonus depuis nouveaux achievements
        for achievement in achievements_earned:
            bonus_multiplier = achievement.metadata.get("bonus_multiplier", 1.0)
            base_bonus *= bonus_multiplier
        
        return min(3.0, base_bonus)  # Cap à 3x bonus
    
    async def _generate_bonuses_from_achievements(self, user_id: str,
                                                achievements: List[UserAchievement]) -> List[GamificationBonus]:
        """Génération bonus depuis achievements"""
        bonuses = []
        
        for achievement in achievements:
            for bonus_type in achievement.bonus_granted:
                bonus = GamificationBonus(
                    bonus_id=str(uuid.uuid4()),
                    user_id=user_id,
                    bonus_type=bonus_type,
                    multiplier=achievement.metadata.get("bonus_multiplier", 1.2),
                    expires_at=datetime.now() + timedelta(days=30),
                    source_achievement=achievement.achievement_id
                )
                
                bonuses.append(bonus)
                self.active_bonuses[user_id].append(bonus)
        
        return bonuses
    
    async def _create_bonuses_for_achievement(self, achievement: UserAchievement) -> List[BonusAllocation]:
        """Création bonus pour achievement"""
        allocations = []
        
        for bonus_type in achievement.bonus_granted:
            # Détermination montant bonus
            bonus_amounts = {
                BonusType.RATE_LIMIT_INCREASE: achievement.metadata.get("bonus_multiplier", 1.2),
                BonusType.PROCESSING_PRIORITY: 1.0,  # Boolean bonus
                BonusType.STORAGE_BONUS: 1000.0,  # MB
                BonusType.BANDWIDTH_BONUS: 500.0,  # MB
                BonusType.COST_REDUCTION: 0.8     # 20% reduction
            }
            
            allocation = BonusAllocation(
                allocation_id=str(uuid.uuid4()),
                user_id=achievement.user_id,
                bonus_type=bonus_type,
                amount=bonus_amounts.get(bonus_type, 1.0),
                duration_hours=24 * 30,  # 30 days
                conditions=[f"achievement:{achievement.achievement_id}"],
                auto_renew=False
            )
            
            allocations.append(allocation)
        
        return allocations
    
    async def _generate_collaboration_recommendations(self, request: CollabRequest,
                                                    team_status: Optional[Dict[str, Any]],
                                                    achievements: List[UserAchievement]) -> List[str]:
        """Génération recommendations collaboration"""
        recommendations = []
        
        # Recommendations équipe
        if team_status:
            utilization = team_status["utilization"]
            if utilization > 80:
                recommendations.append("Team quota is running low - consider inviting more members for bonus quota")
            elif utilization < 20:
                recommendations.append("Team quota is underutilized - great opportunity for more collaboration")
        else:
            recommendations.append("Consider joining or creating a team for shared quota benefits")
        
        # Recommendations achievements
        if not achievements:
            recommendations.append("Complete more collaborations to unlock achievement bonuses")
        
        # Recommendations type collaboration
        if request.collaboration_type == CollaborationType.GUEST_FEATURE:
            recommendations.append("Guest features have lower bonuses - consider joint projects for higher multipliers")
        
        return recommendations
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        # Tâche cleanup bonuses expirés
        bonus_cleanup_task = asyncio.create_task(self._bonus_cleanup_loop())
        self._background_tasks.append(bonus_cleanup_task)
        
        # Tâche expiration équipes
        team_expiry_task = asyncio.create_task(self._team_expiry_loop())
        self._background_tasks.append(team_expiry_task)
        
        # Tâche analysis collaboration patterns
        pattern_task = asyncio.create_task(self._collaboration_pattern_analysis_loop())
        self._background_tasks.append(pattern_task)
    
    async def _bonus_cleanup_loop(self):
        """Loop cleanup bonus expirés"""
        while not self._stop_event.is_set():
            try:
                now = datetime.now()
                
                for user_id, bonuses in self.active_bonuses.items():
                    # Filtrage bonus actifs
                    active_bonuses = [b for b in bonuses if b.is_valid]
                    expired_count = len(bonuses) - len(active_bonuses)
                    
                    self.active_bonuses[user_id] = active_bonuses
                    
                    if expired_count > 0:
                        self.logger.info(f"Cleaned {expired_count} expired bonuses for user {user_id}")
                
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"Bonus cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _team_expiry_loop(self):
        """Loop expiration équipes"""
        while not self._stop_event.is_set():
            try:
                now = datetime.now()
                expired_teams = []
                
                for team_id, team in self.team_manager.teams.items():
                    if team.expires_at and now > team.expires_at:
                        expired_teams.append(team_id)
                
                # Cleanup équipes expirées
                for team_id in expired_teams:
                    team = self.team_manager.teams[team_id]
                    
                    # Retirer membres des user_teams
                    for member_id in team.members:
                        if team_id in self.team_manager.user_teams[member_id]:
                            self.team_manager.user_teams[member_id].remove(team_id)
                    
                    # Archiver équipe
                    del self.team_manager.teams[team_id]
                    self.logger.info(f"Team {team_id} expired and archived")
                
                # Update métriques
                self.collab_metrics["teams_active"] = len(self.team_manager.teams)
                
                await asyncio.sleep(1800)  # Every 30 minutes
            except Exception as e:
                self.logger.error(f"Team expiry error: {e}")
                await asyncio.sleep(600)
    
    async def _collaboration_pattern_analysis_loop(self):
        """Loop analyse patterns collaboration"""
        while not self._stop_event.is_set():
            try:
                # Analyse patterns collaboration
                await self._analyze_collaboration_effectiveness()
                
                # Optimisation bonus basés sur patterns
                await self._optimize_collaboration_bonuses()
                
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"Pattern analysis error: {e}")
                await asyncio.sleep(600)
    
    async def _analyze_collaboration_effectiveness(self):
        """Analyse efficacité collaborations"""
        # Analysis collaboration types les plus utilisés
        type_distribution = defaultdict(int)
        for team in self.team_manager.teams.values():
            type_distribution[team.collaboration_type.value] += 1
        
        self.logger.info(f"Collaboration type distribution: {dict(type_distribution)}")
    
    async def _optimize_collaboration_bonuses(self):
        """Optimisation bonus collaboration"""
        # Ajustement bonus basé sur usage
        # Implementation simplifiée - dans une vraie version, ML-based optimization
        pass
    
    async def get_collaboration_status(self, user_id: str) -> Dict[str, Any]:
        """Status collaboration utilisateur"""
        try:
            # Teams actives
            user_teams = [
                self.team_manager.teams[team_id] 
                for team_id in self.team_manager.user_teams[user_id]
                if team_id in self.team_manager.teams
            ]
            
            # Achievements
            user_achievements = self.achievement_engine.user_achievements[user_id]
            
            # Bonus actifs
            active_bonuses = [b for b in self.active_bonuses[user_id] if b.is_valid]
            
            # Stats utilisateur
            user_stats = self.achievement_engine.user_stats[user_id]
            
            return {
                "user_id": user_id,
                "active_teams": [
                    {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "role": "leader" if team.leader_id == user_id else "member",
                        "quota_remaining": team.remaining_quota,
                        "collaboration_type": team.collaboration_type.value
                    } for team in user_teams
                ],
                "achievements": [
                    {
                        "type": a.achievement_type.value,
                        "level": a.level,
                        "earned_at": a.earned_at.isoformat()
                    } for a in user_achievements[-10:]  # Last 10 achievements
                ],
                "active_bonuses": [
                    {
                        "type": b.bonus_type.value,
                        "multiplier": b.multiplier,
                        "expires_at": b.expires_at.isoformat()
                    } for b in active_bonuses
                ],
                "user_stats": user_stats,
                "global_metrics": self.collab_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}

# Factory functions
def create_team_collaboration_limiter(redis_client) -> CollaborativeRateLimiter:
    """Factory pour limiter collaboration équipe"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=100,
        burst_capacity=200,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        redis_key_prefix="team_collab_rl"
    ))
    
    return CollaborativeRateLimiter(base_limiter)

def create_gamification_limiter(redis_client) -> CollaborativeRateLimiter:
    """Factory pour limiter gamification"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=80,
        burst_capacity=160,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        redis_key_prefix="gamif_rl"
    ))
    
    return CollaborativeRateLimiter(base_limiter)

# Export classes principales
__all__ = [
    'CollaborativeRateLimiter',
    'CollabRequest',
    'CollabLimitResult',
    'CollaborationTeam',
    'UserAchievement',
    'GamificationBonus',
    'BonusAllocation',
    'CollaborationType',
    'AchievementType',
    'BonusType',
    'create_team_collaboration_limiter',
    'create_gamification_limiter'
]