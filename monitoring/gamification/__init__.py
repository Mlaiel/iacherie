"""
Ainflue Platform - Gamification Monitoring Module
================================================

Enterprise-grade monitoring for gamification engagement optimization,
achievement tracking, social proof automation, and retention analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GamificationModules(Enum):
    """Available gamification monitoring modules."""
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"
    ACHIEVEMENT_TRACKING = "achievement_tracking"
    SOCIAL_PROOF_AUTOMATION = "social_proof_automation"
    LEADERBOARD_PERFORMANCE = "leaderboard_performance"
    CHALLENGE_COMPLETION = "challenge_completion"
    REWARD_DISTRIBUTION = "reward_distribution"
    USER_JOURNEY_GAMIFICATION = "user_journey_gamification"
    RETENTION_OPTIMIZATION = "retention_optimization"
    VIRAL_MECHANICS = "viral_mechanics"
    MILESTONE_CELEBRATION = "milestone_celebration"
    COMPETITION_ENGAGEMENT = "competition_engagement"
    GAMIFICATION_INTELLIGENCE = "gamification_intelligence"

class EngagementMechanic(Enum):
    """Types of engagement mechanics."""
    POINTS = "points"
    BADGES = "badges"
    LEVELS = "levels"
    STREAKS = "streaks"
    CHALLENGES = "challenges"
    COMPETITIONS = "competitions"
    SOCIAL_SHARING = "social_sharing"
    COLLABORATIONS = "collaborations"
    MILESTONES = "milestones"
    REWARDS = "rewards"

class UserSegment(Enum):
    """User segments for gamification."""
    NEW_USER = "new_user"
    CASUAL_USER = "casual_user"
    ENGAGED_USER = "engaged_user"
    POWER_USER = "power_user"
    CREATOR = "creator"
    INFLUENCER = "influencer"
    ENTERPRISE = "enterprise"

@dataclass
class GamificationConfig:
    """Configuration for gamification monitoring."""
    enabled_modules: List[GamificationModules]
    engagement_mechanics: List[EngagementMechanic]
    user_segments: List[UserSegment]
    real_time_tracking: bool = True
    social_proof_enabled: bool = True
    viral_mechanics_enabled: bool = True
    reward_automation: bool = True
    competition_enabled: bool = True
    retention_optimization: bool = True
    milestone_celebrations: bool = True

@dataclass
class UserEngagement:
    """User engagement data for gamification."""
    user_id: str
    segment: UserSegment
    points: int
    level: int
    badges: List[str]
    current_streak: int
    achievements: List[str]
    challenges_completed: int
    social_shares: int
    collaboration_count: int
    last_activity: datetime
    engagement_score: float

@dataclass
class GamificationMetrics:
    """Metrics for gamification monitoring."""
    total_users: int = 0
    engaged_users: int = 0
    average_engagement_score: float = 0.0
    retention_rate_day_1: float = 0.0
    retention_rate_day_7: float = 0.0
    retention_rate_day_30: float = 0.0
    viral_coefficient: float = 0.0
    average_session_duration: float = 0.0
    daily_active_users: int = 0
    monthly_active_users: int = 0

class GamificationOrchestrator:
    """
    Main orchestrator for gamification monitoring system.
    
    Coordinates engagement optimization, achievement tracking, social proof automation,
    and retention analytics for enterprise creator platform gamification.
    """
    
    def __init__(self, config -> None: GamificationConfig) -> None:
        """Initialize gamification monitoring orchestrator."""
        self.config = config
        self.modules = {}
        self.user_data: Dict[str, UserEngagement] = {}
        self.engagement_events = []
        self.metrics = GamificationMetrics()
        self.leaderboards = {}
        self.active_challenges = {}
        self.social_proof_data = {}
        self.start_time = datetime.now()
        
        logger.info("Initializing Gamification Monitoring Orchestrator")
        self._initialize_modules()
        self._setup_gamification_systems()
    
    def _initialize_modules(self) -> None:
        """Initialize enabled gamification modules."""
        for module in self.config.enabled_modules:
            try:
                module_instance = self._create_gamification_module(module)
                self.modules[module.value] = module_instance
                logger.info(f"Initialized gamification module: {module.value}")
            except Exception as e:
                logger.error(f"Failed to initialize module {module.value}: {e}")
    
    def _create_gamification_module(self, module -> None: GamificationModules) -> None:
        """Create instance of specific gamification monitoring module."""
        return {
            "name": module.value,
            "status": "active",
            "users_engaged": 0,
            "events_processed": 0,
            "optimization_score": 0.85,
            "retention_impact": 0.12,
            "last_update": datetime.now()
        }
    
    def _setup_gamification_systems(self) -> None:
        """Setup core gamification systems."""
        # Initialize leaderboards
        self.leaderboards = {
            "weekly_points": [],
            "monthly_creators": [],
            "collaboration_champions": [],
            "social_influence": []
        }
        
        # Setup challenge system
        self.active_challenges = {
            "daily_upload": {"participants": 0, "completion_rate": 0.0},
            "collaboration_week": {"participants": 0, "completion_rate": 0.0},
            "viral_content": {"participants": 0, "completion_rate": 0.0}
        }
    
    def track_user_engagement(
        self,
        user_id: str,
        action: str,
        value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track user engagement event for gamification."""
        if user_id not in self.user_data:
            self._initialize_user_gamification(user_id)
        
        user = self.user_data[user_id]
        
        # Process engagement action
        engagement_result = self._process_engagement_action(user, action, value, metadata)
        
        # Update user data
        self._update_user_progression(user, engagement_result)
        
        # Check for achievements
        achievements = self._check_achievements(user, action)
        
        # Update social proof
        if self.config.social_proof_enabled:
            self._update_social_proof(user, action, achievements)
        
        # Process viral mechanics
        if self.config.viral_mechanics_enabled:
            viral_impact = self._process_viral_mechanics(user, action, metadata)
        else:
            viral_impact = {}
        
        # Store engagement event
        engagement_event = {
            "user_id": user_id,
            "action": action,
            "value": value,
            "timestamp": datetime.now(),
            "metadata": metadata or {},
            "result": engagement_result
        }
        self.engagement_events.append(engagement_event)
        
        # Update metrics
        self._update_gamification_metrics()
        
        result = {
            "user_id": user_id,
            "engagement_result": engagement_result,
            "new_achievements": achievements,
            "viral_impact": viral_impact,
            "current_level": user.level,
            "current_points": user.points,
            "engagement_score": user.engagement_score
        }
        
        logger.info(f"Tracked engagement for user {user_id}: {action}")
        return result
    
    def _initialize_user_gamification(self, user_id -> None: str) -> None:
        """Initialize gamification data for new user."""
        user_segment = self._determine_user_segment(user_id)
        
        self.user_data[user_id] = UserEngagement(
            user_id=user_id,
            segment=user_segment,
            points=0,
            level=1,
            badges=[],
            current_streak=0,
            achievements=["welcome_user"],
            challenges_completed=0,
            social_shares=0,
            collaboration_count=0,
            last_activity=datetime.now(),
            engagement_score=0.1  # Starting score
        )
        
        logger.info(f"Initialized gamification for user {user_id} as {user_segment.value}")
    
    def _determine_user_segment(self, user_id: str) -> UserSegment:
        """Determine user segment for gamification customization."""
        # Simplified segmentation logic
        # In practice, this would analyze user behavior and history
        return UserSegment.NEW_USER
    
    def _process_engagement_action(
        self, 
        user: UserEngagement, 
        action: str, 
        value: Optional[float],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process specific engagement action and calculate rewards."""
        action_rewards = {
            "content_upload": {"points": 50, "streak_eligible": True},
            "collaboration_join": {"points": 100, "streak_eligible": False},
            "social_share": {"points": 25, "streak_eligible": False},
            "comment_received": {"points": 10, "streak_eligible": False},
            "follower_gained": {"points": 15, "streak_eligible": False},
            "challenge_complete": {"points": 200, "streak_eligible": False},
            "milestone_reached": {"points": 500, "streak_eligible": False},
            "content_viral": {"points": 1000, "streak_eligible": False}
        }
        
        reward_config = action_rewards.get(action, {"points": 5, "streak_eligible": False})
        base_points = reward_config["points"]
        
        # Apply multipliers based on user segment
        segment_multipliers = {
            UserSegment.NEW_USER: 1.5,  # Boost for new users
            UserSegment.CASUAL_USER: 1.0,
            UserSegment.ENGAGED_USER: 1.2,
            UserSegment.POWER_USER: 1.0,
            UserSegment.CREATOR: 1.3,
            UserSegment.INFLUENCER: 1.1
        }
        
        multiplier = segment_multipliers.get(user.segment, 1.0)
        
        # Apply streak bonus
        streak_bonus = 1.0
        if reward_config["streak_eligible"] and user.current_streak > 0:
            streak_bonus = 1.0 + (user.current_streak * 0.1)  # 10% per streak day
        
        # Calculate final points
        final_points = int(base_points * multiplier * streak_bonus)
        
        return {
            "action": action,
            "base_points": base_points,
            "multiplier": multiplier,
            "streak_bonus": streak_bonus,
            "final_points": final_points,
            "level_up": False,  # Will be calculated in update function
            "badges_earned": []
        }
    
    def _update_user_progression(self, user -> None: UserEngagement, engagement_result -> None: Dict[str, Any]) -> None:
        """Update user progression based on engagement."""
        # Add points
        user.points += engagement_result["final_points"]
        
        # Check for level up
        new_level = self._calculate_level_from_points(user.points)
        if new_level > user.level:
            user.level = new_level
            engagement_result["level_up"] = True
            logger.info(f"User {user.user_id} leveled up to level {new_level}")
        
        # Update streak for streak-eligible actions
        action = engagement_result["action"]
        if action in ["content_upload", "daily_login"]:
            if self._is_consecutive_day(user.last_activity):
                user.current_streak += 1
            else:
                user.current_streak = 1
        
        # Update last activity
        user.last_activity = datetime.now()
        
        # Update engagement score
        user.engagement_score = self._calculate_engagement_score(user)
    
    def _calculate_level_from_points(self, points: int) -> int:
        """Calculate user level based on points."""
        # Exponential leveling system
        if points < 100:
            return 1
        elif points < 300:
            return 2
        elif points < 600:
            return 3
        elif points < 1000:
            return 4
        elif points < 1500:
            return 5
        else:
            # Level = sqrt(points/100) for higher levels
            import math
            return min(50, int(math.sqrt(points / 100)))
    
    def _is_consecutive_day(self, last_activity: datetime) -> bool:
        """Check if current activity is consecutive day."""
        yesterday = datetime.now() - timedelta(days=1)
        return last_activity.date() >= yesterday.date()
    
    def _calculate_engagement_score(self, user: UserEngagement) -> float:
        """Calculate overall engagement score for user."""
        # Weighted score based on different activities
        base_score = min(1.0, user.points / 10000)  # Points contribution (max 1.0)
        level_bonus = user.level * 0.02  # Level contribution
        badge_bonus = len(user.badges) * 0.01  # Badge contribution
        streak_bonus = min(0.2, user.current_streak * 0.02)  # Streak contribution (max 0.2)
        social_bonus = min(0.1, user.social_shares * 0.01)  # Social contribution (max 0.1)
        collab_bonus = min(0.15, user.collaboration_count * 0.03)  # Collaboration contribution (max 0.15)
        
        total_score = base_score + level_bonus + badge_bonus + streak_bonus + social_bonus + collab_bonus
        return min(1.0, total_score)
    
    def _check_achievements(self, user: UserEngagement, action: str) -> List[str]:
        """Check for new achievements based on user action."""
        new_achievements = []
        
        achievement_criteria = {
            "first_upload": lambda u: "content_upload" in action and u.points >= 50,
            "collaboration_master": lambda u: u.collaboration_count >= 10,
            "social_butterfly": lambda u: u.social_shares >= 50,
            "streak_warrior": lambda u: u.current_streak >= 7,
            "level_10": lambda u: u.level >= 10,
            "point_millionaire": lambda u: u.points >= 1000000,
            "badge_collector": lambda u: len(u.badges) >= 20
        }
        
        for achievement_id, criteria in achievement_criteria.items():
            if achievement_id not in user.achievements and criteria(user):
                new_achievements.append(achievement_id)
                user.achievements.append(achievement_id)
                
                # Award achievement badge
                if achievement_id not in user.badges:
                    user.badges.append(achievement_id)
        
        return new_achievements
    
    def _update_social_proof(self, user -> None: UserEngagement, action -> None: str, achievements -> None: List[str]) -> None:
        """Update social proof data for the user."""
        if user.user_id not in self.social_proof_data:
            self.social_proof_data[user.user_id] = {
                "recent_achievements": [],
                "activity_feed": [],
                "influence_score": 0.0
            }
        
        social_data = self.social_proof_data[user.user_id]
        
        # Add achievements to recent list
        for achievement in achievements:
            social_data["recent_achievements"].append({
                "achievement": achievement,
                "timestamp": datetime.now(),
                "level": user.level,
                "points": user.points
            })
        
        # Add to activity feed
        social_data["activity_feed"].append({
            "action": action,
            "timestamp": datetime.now(),
            "result": f"Level {user.level} • {user.points} points"
        })
        
        # Update influence score
        social_data["influence_score"] = self._calculate_influence_score(user)
        
        # Keep only recent data (last 50 items)
        social_data["recent_achievements"] = social_data["recent_achievements"][-50:]
        social_data["activity_feed"] = social_data["activity_feed"][-50:]
    
    def _calculate_influence_score(self, user: UserEngagement) -> float:
        """Calculate user influence score for social proof."""
        # Base influence from engagement score
        base_influence = user.engagement_score * 0.5
        
        # Collaboration influence
        collab_influence = min(0.3, user.collaboration_count / 50 * 0.3)
        
        # Social sharing influence
        social_influence = min(0.2, user.social_shares / 100 * 0.2)
        
        return base_influence + collab_influence + social_influence
    
    def _process_viral_mechanics(
        self, 
        user: UserEngagement, 
        action: str, 
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process viral mechanics for user action."""
        viral_impact = {
            "shares_generated": 0,
            "referrals_created": 0,
            "viral_coefficient": 0.0
        }
        
        # Actions that trigger viral mechanics
        viral_actions = {
            "content_viral": {"share_multiplier": 3.0, "referral_bonus": 0.5},
            "achievement_unlock": {"share_multiplier": 1.5, "referral_bonus": 0.2},
            "collaboration_complete": {"share_multiplier": 2.0, "referral_bonus": 0.3},
            "milestone_reached": {"share_multiplier": 2.5, "referral_bonus": 0.4}
        }
        
        if action in viral_actions:
            viral_config = viral_actions[action]
            
            # Calculate viral shares
            base_shares = max(1, int(user.engagement_score * 10))
            viral_impact["shares_generated"] = int(base_shares * viral_config["share_multiplier"])
            
            # Calculate referrals
            viral_impact["referrals_created"] = int(viral_config["referral_bonus"] * user.level)
            
            # Calculate viral coefficient
            viral_impact["viral_coefficient"] = min(1.0, viral_impact["shares_generated"] / 100)
        
        return viral_impact
    
    def _update_gamification_metrics(self) -> None:
        """Update overall gamification metrics."""
        if not self.user_data:
            return
        
        # Basic metrics
        self.metrics.total_users = len(self.user_data)
        
        # Engagement metrics
        engaged_threshold = 0.3
        engaged_users = [u for u in self.user_data.values() if u.engagement_score >= engaged_threshold]
        self.metrics.engaged_users = len(engaged_users)
        
        if self.user_data:
            self.metrics.average_engagement_score = sum(u.engagement_score for u in self.user_data.values()) / len(self.user_data)
        
        # Activity metrics
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        self.metrics.daily_active_users = len([
            u for u in self.user_data.values() 
            if u.last_activity >= day_ago
        ])
        
        self.metrics.monthly_active_users = len([
            u for u in self.user_data.values() 
            if u.last_activity >= month_ago
        ])
        
        # Simplified retention calculation
        if self.metrics.total_users > 0:
            self.metrics.retention_rate_day_1 = self.metrics.daily_active_users / self.metrics.total_users
            weekly_active = len([u for u in self.user_data.values() if u.last_activity >= week_ago])
            self.metrics.retention_rate_day_7 = weekly_active / self.metrics.total_users
            self.metrics.retention_rate_day_30 = self.metrics.monthly_active_users / self.metrics.total_users
    
    def get_gamification_status(self) -> Dict[str, Any]:
        """Get overall gamification system status."""
        return {
            "system_status": "active",
            "total_users": self.metrics.total_users,
            "engaged_users": self.metrics.engaged_users,
            "engagement_rate": round(self.metrics.engaged_users / max(1, self.metrics.total_users), 3),
            "average_engagement_score": round(self.metrics.average_engagement_score, 3),
            "daily_active_users": self.metrics.daily_active_users,
            "monthly_active_users": self.metrics.monthly_active_users,
            "retention_day_1": round(self.metrics.retention_rate_day_1, 3),
            "retention_day_7": round(self.metrics.retention_rate_day_7, 3),
            "retention_day_30": round(self.metrics.retention_rate_day_30, 3),
            "active_challenges": len(self.active_challenges),
            "total_engagement_events": len(self.engagement_events),
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_user_gamification_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get gamification data for specific user."""
        if user_id not in self.user_data:
            return None
        
        user = self.user_data[user_id]
        social_data = self.social_proof_data.get(user_id, {})
        
        return {
            "user_id": user_id,
            "segment": user.segment.value,
            "level": user.level,
            "points": user.points,
            "engagement_score": round(user.engagement_score, 3),
            "current_streak": user.current_streak,
            "badges": user.badges,
            "achievements": user.achievements,
            "statistics": {
                "challenges_completed": user.challenges_completed,
                "social_shares": user.social_shares,
                "collaboration_count": user.collaboration_count
            },
            "social_proof": {
                "recent_achievements": social_data.get("recent_achievements", [])[-5:],
                "influence_score": round(social_data.get("influence_score", 0.0), 3)
            },
            "last_activity": user.last_activity.isoformat()
        }

def create_enterprise_config() -> GamificationConfig:
    """Create enterprise-level configuration for gamification monitoring."""
    return GamificationConfig(
        enabled_modules=[
            GamificationModules.ENGAGEMENT_OPTIMIZATION,
            GamificationModules.ACHIEVEMENT_TRACKING,
            GamificationModules.SOCIAL_PROOF_AUTOMATION,
            GamificationModules.LEADERBOARD_PERFORMANCE,
            GamificationModules.CHALLENGE_COMPLETION,
            GamificationModules.REWARD_DISTRIBUTION,
            GamificationModules.USER_JOURNEY_GAMIFICATION,
            GamificationModules.RETENTION_OPTIMIZATION,
            GamificationModules.VIRAL_MECHANICS,
            GamificationModules.MILESTONE_CELEBRATION,
            GamificationModules.COMPETITION_ENGAGEMENT,
            GamificationModules.GAMIFICATION_INTELLIGENCE
        ],
        engagement_mechanics=[
            EngagementMechanic.POINTS,
            EngagementMechanic.BADGES,
            EngagementMechanic.LEVELS,
            EngagementMechanic.STREAKS,
            EngagementMechanic.CHALLENGES,
            EngagementMechanic.COMPETITIONS,
            EngagementMechanic.SOCIAL_SHARING,
            EngagementMechanic.COLLABORATIONS,
            EngagementMechanic.MILESTONES,
            EngagementMechanic.REWARDS
        ],
        user_segments=[
            UserSegment.NEW_USER,
            UserSegment.CASUAL_USER,
            UserSegment.ENGAGED_USER,
            UserSegment.POWER_USER,
            UserSegment.CREATOR,
            UserSegment.INFLUENCER,
            UserSegment.ENTERPRISE
        ],
        real_time_tracking=True,
        social_proof_enabled=True,
        viral_mechanics_enabled=True,
        reward_automation=True,
        competition_enabled=True,
        retention_optimization=True,
        milestone_celebrations=True
    )

# Initialize default orchestrator
enterprise_config = create_enterprise_config()
gamification_monitoring = GamificationOrchestrator(enterprise_config)

# Export main components
__all__ = [
    'GamificationOrchestrator',
    'GamificationConfig',
    'GamificationModules',
    'EngagementMechanic',
    'UserSegment',
    'UserEngagement',
    'create_enterprise_config',
    'gamification_monitoring'
]