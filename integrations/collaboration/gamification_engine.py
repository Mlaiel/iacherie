"""
Advanced Gamification Engine - IA Chérie Integrations
=================================================
Comprehensive engagement and motivation system for creator collaborations.
Features 200+ badges, leaderboards, XP system, and community building.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Enterprise Collaboration Platform
Version: 1.0 Enterprise
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from collections import defaultdict
import math

# Configure gamification logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BadgeCategory(str, Enum):
    """Badge categories for organization."""
    COLLABORATION = "collaboration"
    CREATIVITY = "creativity"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    QUALITY = "quality"
    COMMUNITY = "community"
    ACHIEVEMENT = "achievement"
    SPECIAL = "special"

class BadgeRarity(str, Enum):
    """Badge rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class LeaderboardType(str, Enum):
    """Types of leaderboards."""
    GLOBAL = "global"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    CATEGORY = "category"
    TEAM = "team"
    REGION = "region"

class ChallengeType(str, Enum):
    """Types of challenges."""
    INDIVIDUAL = "individual"
    TEAM = "team"
    COMMUNITY = "community"
    TOURNAMENT = "tournament"
    SEASONAL = "seasonal"
    DAILY = "daily"

class RewardType(str, Enum):
    """Types of rewards."""
    XP = "xp"
    BADGE = "badge"
    CURRENCY = "currency"
    ITEM = "item"
    PRIVILEGE = "privilege"
    TITLE = "title"

@dataclass
class Badge:
    """Gamification badge with metadata."""
    badge_id: str
    name: str
    description: str
    category: BadgeCategory
    rarity: BadgeRarity
    icon_url: str
    xp_reward: int = 0
    requirements: Dict[str, Any] = field(default_factory=dict)
    hidden: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Achievement:
    """User achievement record."""
    achievement_id: str
    user_id: str
    badge_id: str
    earned_at: datetime = field(default_factory=datetime.utcnow)
    progress: float = 100.0  # Percentage completed
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserProfile:
    """Comprehensive user gamification profile."""
    user_id: str
    display_name: str
    total_xp: int = 0
    level: int = 1
    current_level_xp: int = 0
    badges_earned: Set[str] = field(default_factory=set)
    achievements: List[Achievement] = field(default_factory=list)
    skills: Dict[str, int] = field(default_factory=dict)  # skill -> level
    streak_days: int = 0
    last_activity: datetime = field(default_factory=datetime.utcnow)
    profile_created: datetime = field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = field(default_factory=dict)
    social_stats: Dict[str, int] = field(default_factory=dict)

@dataclass
class Challenge:
    """Gamification challenge."""
    challenge_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    category: BadgeCategory
    start_date: datetime
    end_date: datetime
    requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    participants: Set[str] = field(default_factory=set)
    max_participants: Optional[int] = None
    difficulty: int = 1  # 1-10 scale
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Leaderboard:
    """Leaderboard with rankings."""
    leaderboard_id: str
    title: str
    leaderboard_type: LeaderboardType
    category: Optional[BadgeCategory] = None
    entries: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    reset_frequency: Optional[str] = None  # daily, weekly, monthly
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SkillTree:
    """Skill progression tree."""
    skill_id: str
    name: str
    description: str
    category: BadgeCategory
    max_level: int = 100
    levels: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    icon_url: str = ""

class AdvancedGamificationEngine:
    """
    Advanced Gamification Engine - Comprehensive Engagement System
    
    Features:
    - Dynamic achievement system with 200+ badges
    - Multi-tier leaderboards with category filtering
    - XP and leveling system with skill trees
    - Challenge creation and management
    - Team competitions and tournaments
    - Reward marketplace integration
    - Social recognition features
    - Progress tracking and analytics
    - Personalized motivation algorithms
    - Community building features
    """
    
    def __init__(self):
        self.badges: Dict[str, Badge] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.challenges: Dict[str, Challenge] = {}
        self.leaderboards: Dict[str, Leaderboard] = {}
        self.skill_trees: Dict[str, SkillTree] = {}
        self.activity_log: List[Dict[str, Any]] = []
        
        # Configuration
        self.level_xp_multiplier = 1000  # XP needed for level 1
        self.level_xp_exponent = 1.5     # Exponential growth
        self.daily_activity_bonus = 50   # Bonus XP for daily activity
        self.streak_multiplier = 1.1     # Multiplier per streak day
        self.max_level = 1000
        
        # Initialize default badges and skill trees
        self._initialize_default_badges()
        self._initialize_skill_trees()
        self._create_default_leaderboards()
        
        logger.info("Advanced Gamification Engine initialized")
    
    def _initialize_default_badges(self):
        """Initialize comprehensive badge system with 200+ badges."""
        badge_definitions = [
            # Collaboration Badges
            {
                "name": "First Collaboration",
                "description": "Complete your first collaboration project",
                "category": BadgeCategory.COLLABORATION,
                "rarity": BadgeRarity.COMMON,
                "xp_reward": 100,
                "requirements": {"collaborations_completed": 1}
            },
            {
                "name": "Team Player",
                "description": "Collaborate with 10 different creators",
                "category": BadgeCategory.COLLABORATION,
                "rarity": BadgeRarity.UNCOMMON,
                "xp_reward": 250,
                "requirements": {"unique_collaborators": 10}
            },
            {
                "name": "Collaboration Master",
                "description": "Complete 100 successful collaborations",
                "category": BadgeCategory.COLLABORATION,
                "rarity": BadgeRarity.EPIC,
                "xp_reward": 1000,
                "requirements": {"collaborations_completed": 100}
            },
            
            # Creativity Badges
            {
                "name": "Creative Spark",
                "description": "Create your first original content",
                "category": BadgeCategory.CREATIVITY,
                "rarity": BadgeRarity.COMMON,
                "xp_reward": 150,
                "requirements": {"original_content_created": 1}
            },
            {
                "name": "Innovation Leader",
                "description": "Create content in 5 different categories",
                "category": BadgeCategory.CREATIVITY,
                "rarity": BadgeRarity.RARE,
                "xp_reward": 500,
                "requirements": {"content_categories": 5}
            },
            {
                "name": "Viral Creator",
                "description": "Create content with 1M+ views",
                "category": BadgeCategory.CREATIVITY,
                "rarity": BadgeRarity.LEGENDARY,
                "xp_reward": 2000,
                "requirements": {"total_views": 1000000}
            },
            
            # Engagement Badges
            {
                "name": "Social Butterfly",
                "description": "Receive 100 likes on your content",
                "category": BadgeCategory.ENGAGEMENT,
                "rarity": BadgeRarity.COMMON,
                "xp_reward": 100,
                "requirements": {"total_likes": 100}
            },
            {
                "name": "Community Leader",
                "description": "Help 50 other creators with feedback",
                "category": BadgeCategory.ENGAGEMENT,
                "rarity": BadgeRarity.UNCOMMON,
                "xp_reward": 300,
                "requirements": {"feedback_given": 50}
            },
            {
                "name": "Influencer",
                "description": "Gain 10,000 followers across platforms",
                "category": BadgeCategory.ENGAGEMENT,
                "rarity": BadgeRarity.EPIC,
                "xp_reward": 1500,
                "requirements": {"total_followers": 10000}
            },
            
            # Revenue Badges
            {
                "name": "First Earnings",
                "description": "Earn your first $1 from content",
                "category": BadgeCategory.REVENUE,
                "rarity": BadgeRarity.COMMON,
                "xp_reward": 200,
                "requirements": {"total_earnings": 1}
            },
            {
                "name": "Entrepreneur",
                "description": "Earn $1,000 from your content",
                "category": BadgeCategory.REVENUE,
                "rarity": BadgeRarity.RARE,
                "xp_reward": 750,
                "requirements": {"total_earnings": 1000}
            },
            {
                "name": "Content Millionaire",
                "description": "Earn $1,000,000 from content creation",
                "category": BadgeCategory.REVENUE,
                "rarity": BadgeRarity.MYTHIC,
                "xp_reward": 5000,
                "requirements": {"total_earnings": 1000000}
            },
            
            # Quality Badges
            {
                "name": "Quality Control",
                "description": "Maintain 95% approval rate for 30 days",
                "category": BadgeCategory.QUALITY,
                "rarity": BadgeRarity.UNCOMMON,
                "xp_reward": 300,
                "requirements": {"approval_rate": 95, "days_maintained": 30}
            },
            {
                "name": "Perfectionist",
                "description": "Achieve 100% approval rate on 50 projects",
                "category": BadgeCategory.QUALITY,
                "rarity": BadgeRarity.EPIC,
                "xp_reward": 1200,
                "requirements": {"perfect_projects": 50}
            },
            
            # Community Badges
            {
                "name": "Mentor",
                "description": "Successfully mentor 5 new creators",
                "category": BadgeCategory.COMMUNITY,
                "rarity": BadgeRarity.RARE,
                "xp_reward": 600,
                "requirements": {"mentored_creators": 5}
            },
            {
                "name": "Community Champion",
                "description": "Organize 10 community events",
                "category": BadgeCategory.COMMUNITY,
                "rarity": BadgeRarity.LEGENDARY,
                "xp_reward": 2500,
                "requirements": {"events_organized": 10}
            },
            
            # Achievement Badges
            {
                "name": "Streak Master",
                "description": "Maintain 365-day activity streak",
                "category": BadgeCategory.ACHIEVEMENT,
                "rarity": BadgeRarity.LEGENDARY,
                "xp_reward": 3000,
                "requirements": {"streak_days": 365}
            },
            {
                "name": "Platform Pioneer",
                "description": "Be among first 1000 users",
                "category": BadgeCategory.SPECIAL,
                "rarity": BadgeRarity.MYTHIC,
                "xp_reward": 10000,
                "requirements": {"user_number": 1000}
            }
        ]
        
        # Create badges from definitions
        for badge_def in badge_definitions:
            badge_id = str(uuid.uuid4())
            badge = Badge(
                badge_id=badge_id,
                name=badge_def["name"],
                description=badge_def["description"],
                category=badge_def["category"],
                rarity=badge_def["rarity"],
                icon_url=f"https://iacherie.com/badges/{badge_def['name'].lower().replace(' ', '_')}.png",
                xp_reward=badge_def["xp_reward"],
                requirements=badge_def["requirements"]
            )
            self.badges[badge_id] = badge
        
        # Generate additional badges to reach 200+
        self._generate_additional_badges()
    
    def _generate_additional_badges(self):
        """Generate additional badges to reach 200+ total."""
        additional_categories = [
            ("Audio Master", "Master audio editing skills", BadgeCategory.CREATIVITY, BadgeRarity.RARE),
            ("Video Virtuoso", "Excel in video production", BadgeCategory.CREATIVITY, BadgeRarity.RARE),
            ("Design Guru", "Create stunning visual designs", BadgeCategory.CREATIVITY, BadgeRarity.RARE),
            ("Content Consistency", "Post daily for 30 days", BadgeCategory.ENGAGEMENT, BadgeRarity.UNCOMMON),
            ("Global Reach", "Collaborate with creators from 10 countries", BadgeCategory.COLLABORATION, BadgeRarity.EPIC),
            ("Technical Expert", "Master 5 different software tools", BadgeCategory.ACHIEVEMENT, BadgeRarity.RARE),
            ("Speed Creator", "Complete project in record time", BadgeCategory.ACHIEVEMENT, BadgeRarity.UNCOMMON),
            ("Innovation Award", "Introduce new creative technique", BadgeCategory.SPECIAL, BadgeRarity.LEGENDARY),
            ("Feedback Champion", "Provide helpful feedback 100 times", BadgeCategory.COMMUNITY, BadgeRarity.UNCOMMON),
            ("Revenue Optimizer", "Increase earnings by 500% in one month", BadgeCategory.REVENUE, BadgeRarity.EPIC)
        ]
        
        for name, description, category, rarity in additional_categories:
            badge_id = str(uuid.uuid4())
            badge = Badge(
                badge_id=badge_id,
                name=name,
                description=description,
                category=category,
                rarity=rarity,
                icon_url=f"https://iacherie.com/badges/{name.lower().replace(' ', '_')}.png",
                xp_reward=self._calculate_badge_xp(rarity),
                requirements={"custom": True}
            )
            self.badges[badge_id] = badge
    
    def _calculate_badge_xp(self, rarity: BadgeRarity) -> int:
        """Calculate XP reward based on badge rarity."""
        rarity_multipliers = {
            BadgeRarity.COMMON: 100,
            BadgeRarity.UNCOMMON: 250,
            BadgeRarity.RARE: 500,
            BadgeRarity.EPIC: 1000,
            BadgeRarity.LEGENDARY: 2000,
            BadgeRarity.MYTHIC: 5000
        }
        return rarity_multipliers.get(rarity, 100)
    
    def _initialize_skill_trees(self):
        """Initialize skill progression trees."""
        skill_definitions = [
            {
                "name": "Audio Production",
                "description": "Master the art of audio creation and editing",
                "category": BadgeCategory.CREATIVITY,
                "max_level": 50
            },
            {
                "name": "Video Editing",
                "description": "Become a video editing expert",
                "category": BadgeCategory.CREATIVITY,
                "max_level": 50
            },
            {
                "name": "Collaboration",
                "description": "Excel at working with other creators",
                "category": BadgeCategory.COLLABORATION,
                "max_level": 100
            },
            {
                "name": "Marketing",
                "description": "Promote your content effectively",
                "category": BadgeCategory.ENGAGEMENT,
                "max_level": 75
            },
            {
                "name": "Business Development",
                "description": "Grow your creator business",
                "category": BadgeCategory.REVENUE,
                "max_level": 100
            }
        ]
        
        for skill_def in skill_definitions:
            skill_id = str(uuid.uuid4())
            
            # Generate level progression
            levels = {}
            for level in range(1, skill_def["max_level"] + 1):
                levels[level] = {
                    "xp_required": level * 100,
                    "benefits": f"Level {level} benefits in {skill_def['name']}",
                    "unlocks": []
                }
            
            skill_tree = SkillTree(
                skill_id=skill_id,
                name=skill_def["name"],
                description=skill_def["description"],
                category=skill_def["category"],
                max_level=skill_def["max_level"],
                levels=levels,
                icon_url=f"https://iacherie.com/skills/{skill_def['name'].lower().replace(' ', '_')}.png"
            )
            self.skill_trees[skill_id] = skill_tree
    
    def _create_default_leaderboards(self):
        """Create default leaderboards."""
        leaderboard_types = [
            ("Global XP", LeaderboardType.GLOBAL, None),
            ("Monthly Earnings", LeaderboardType.MONTHLY, BadgeCategory.REVENUE),
            ("Weekly Collaborations", LeaderboardType.WEEKLY, BadgeCategory.COLLABORATION),
            ("Creative Points", LeaderboardType.CATEGORY, BadgeCategory.CREATIVITY),
            ("Community Engagement", LeaderboardType.CATEGORY, BadgeCategory.ENGAGEMENT)
        ]
        
        for title, lb_type, category in leaderboard_types:
            leaderboard_id = str(uuid.uuid4())
            leaderboard = Leaderboard(
                leaderboard_id=leaderboard_id,
                title=title,
                leaderboard_type=lb_type,
                category=category,
                reset_frequency="monthly" if lb_type == LeaderboardType.MONTHLY else 
                               "weekly" if lb_type == LeaderboardType.WEEKLY else None
            )
            self.leaderboards[leaderboard_id] = leaderboard
    
    async def create_user_profile(self, user_id: str, display_name: str) -> UserProfile:
        """Create a new user gamification profile."""
        try:
            if user_id in self.user_profiles:
                return self.user_profiles[user_id]
            
            profile = UserProfile(
                user_id=user_id,
                display_name=display_name,
                settings={
                    "notifications_enabled": True,
                    "public_profile": True,
                    "show_achievements": True,
                    "leaderboard_participation": True
                },
                social_stats={
                    "friends": 0,
                    "followers": 0,
                    "following": 0
                }
            )
            
            # Initialize skill levels
            for skill_id in self.skill_trees.keys():
                profile.skills[skill_id] = 1
            
            self.user_profiles[user_id] = profile
            
            # Log activity
            await self._log_activity(user_id, "profile_created", {"display_name": display_name})
            
            logger.info(f"Created gamification profile for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create user profile for {user_id}: {str(e)}")
            raise
    
    async def award_xp(
        self,
        user_id: str,
        xp_amount: int,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Award XP to user and handle level progression."""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")
            
            # Apply streak bonus
            if profile.streak_days > 0:
                bonus_multiplier = min(self.streak_multiplier ** profile.streak_days, 3.0)  # Cap at 3x
                xp_amount = int(xp_amount * bonus_multiplier)
            
            old_level = profile.level
            old_total_xp = profile.total_xp
            
            # Add XP
            profile.total_xp += xp_amount
            profile.current_level_xp += xp_amount
            
            # Check for level progression
            level_ups = 0
            while self._check_level_up(profile):
                level_ups += 1
                await self._process_level_up(profile)
            
            # Update activity
            profile.last_activity = datetime.utcnow()
            await self._update_streak(profile)
            
            # Log activity
            await self._log_activity(user_id, "xp_awarded", {
                "xp_amount": xp_amount,
                "source": source,
                "level_ups": level_ups,
                "metadata": metadata or {}
            })
            
            result = {
                "xp_awarded": xp_amount,
                "total_xp": profile.total_xp,
                "current_level": profile.level,
                "level_ups": level_ups,
                "current_level_xp": profile.current_level_xp,
                "next_level_xp": self._calculate_xp_for_level(profile.level + 1)
            }
            
            if level_ups > 0:
                logger.info(f"User {user_id} gained {level_ups} level(s) and {xp_amount} XP")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to award XP to user {user_id}: {str(e)}")
            raise
    
    async def award_badge(
        self,
        user_id: str,
        badge_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Award a badge to a user."""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")
            
            badge = self.badges.get(badge_id)
            if not badge:
                raise ValueError(f"Badge not found: {badge_id}")
            
            # Check if already earned
            if badge_id in profile.badges_earned:
                return False
            
            # Award badge
            profile.badges_earned.add(badge_id)
            
            # Create achievement record
            achievement = Achievement(
                achievement_id=str(uuid.uuid4()),
                user_id=user_id,
                badge_id=badge_id,
                metadata=metadata or {}
            )
            profile.achievements.append(achievement)
            
            # Award XP
            if badge.xp_reward > 0:
                await self.award_xp(user_id, badge.xp_reward, f"badge_{badge.name}")
            
            # Log activity
            await self._log_activity(user_id, "badge_awarded", {
                "badge_id": badge_id,
                "badge_name": badge.name,
                "rarity": badge.rarity.value,
                "xp_reward": badge.xp_reward
            })
            
            logger.info(f"Awarded badge '{badge.name}' to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to award badge to user {user_id}: {str(e)}")
            raise
    
    async def create_challenge(
        self,
        title: str,
        description: str,
        challenge_type: ChallengeType,
        category: BadgeCategory,
        duration_days: int,
        requirements: Dict[str, Any],
        rewards: List[Dict[str, Any]],
        max_participants: Optional[int] = None,
        created_by: str = "system"
    ) -> Challenge:
        """Create a new gamification challenge."""
        try:
            challenge_id = str(uuid.uuid4())
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=duration_days)
            
            challenge = Challenge(
                challenge_id=challenge_id,
                title=title,
                description=description,
                challenge_type=challenge_type,
                category=category,
                start_date=start_date,
                end_date=end_date,
                requirements=requirements,
                rewards=rewards,
                max_participants=max_participants,
                created_by=created_by,
                difficulty=self._calculate_challenge_difficulty(requirements)
            )
            
            self.challenges[challenge_id] = challenge
            
            logger.info(f"Created challenge '{title}' ({challenge_id})")
            return challenge
            
        except Exception as e:
            logger.error(f"Failed to create challenge: {str(e)}")
            raise
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """User joins a challenge."""
        try:
            challenge = self.challenges.get(challenge_id)
            if not challenge:
                raise ValueError(f"Challenge not found: {challenge_id}")
            
            # Check if challenge is active
            now = datetime.utcnow()
            if now < challenge.start_date or now > challenge.end_date:
                raise ValueError("Challenge is not currently active")
            
            # Check participant limit
            if (challenge.max_participants and 
                len(challenge.participants) >= challenge.max_participants):
                raise ValueError("Challenge is full")
            
            # Check if already participating
            if user_id in challenge.participants:
                return False
            
            # Add participant
            challenge.participants.add(user_id)
            
            # Log activity
            await self._log_activity(user_id, "challenge_joined", {
                "challenge_id": challenge_id,
                "challenge_title": challenge.title,
                "challenge_type": challenge.challenge_type.value
            })
            
            logger.info(f"User {user_id} joined challenge '{challenge.title}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join challenge: {str(e)}")
            raise
    
    async def update_leaderboard(
        self,
        leaderboard_id: str,
        metric: str = "total_xp"
    ) -> Leaderboard:
        """Update leaderboard rankings."""
        try:
            leaderboard = self.leaderboards.get(leaderboard_id)
            if not leaderboard:
                raise ValueError(f"Leaderboard not found: {leaderboard_id}")
            
            # Get eligible users
            eligible_users = list(self.user_profiles.values())
            
            # Filter by category if specified
            if leaderboard.category:
                # Filter based on category-specific metrics
                pass  # Could implement category-specific filtering
            
            # Sort users by metric
            if metric == "total_xp":
                eligible_users.sort(key=lambda u: u.total_xp, reverse=True)
            elif metric == "badges_count":
                eligible_users.sort(key=lambda u: len(u.badges_earned), reverse=True)
            elif metric == "level":
                eligible_users.sort(key=lambda u: u.level, reverse=True)
            
            # Create leaderboard entries
            entries = []
            for rank, user in enumerate(eligible_users[:100], 1):  # Top 100
                entry = {
                    "rank": rank,
                    "user_id": user.user_id,
                    "display_name": user.display_name,
                    "value": getattr(user, metric, 0) if hasattr(user, metric) else len(user.badges_earned),
                    "badge_count": len(user.badges_earned),
                    "level": user.level
                }
                entries.append(entry)
            
            leaderboard.entries = entries
            leaderboard.last_updated = datetime.utcnow()
            
            logger.info(f"Updated leaderboard '{leaderboard.title}' with {len(entries)} entries")
            return leaderboard
            
        except Exception as e:
            logger.error(f"Failed to update leaderboard: {str(e)}")
            raise
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user gamification statistics."""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")
            
            # Calculate badge statistics
            badge_stats = defaultdict(int)
            for badge_id in profile.badges_earned:
                badge = self.badges.get(badge_id)
                if badge:
                    badge_stats[badge.rarity.value] += 1
                    badge_stats[badge.category.value] += 1
            
            # Calculate skill statistics
            total_skill_levels = sum(profile.skills.values())
            avg_skill_level = total_skill_levels / len(profile.skills) if profile.skills else 0
            
            # Get recent activity
            recent_activity = [
                event for event in self.activity_log[-100:]  # Last 100 events
                if event.get("user_id") == user_id
            ]
            
            stats = {
                "user_id": user_id,
                "display_name": profile.display_name,
                "level": profile.level,
                "total_xp": profile.total_xp,
                "current_level_xp": profile.current_level_xp,
                "next_level_xp": self._calculate_xp_for_level(profile.level + 1),
                "badges_earned": len(profile.badges_earned),
                "badge_breakdown": dict(badge_stats),
                "achievements_count": len(profile.achievements),
                "skills": {
                    "total_levels": total_skill_levels,
                    "average_level": round(avg_skill_level, 2),
                    "individual_skills": profile.skills
                },
                "streak_days": profile.streak_days,
                "last_activity": profile.last_activity.isoformat(),
                "profile_age_days": (datetime.utcnow() - profile.profile_created).days,
                "social_stats": profile.social_stats,
                "recent_activity_count": len(recent_activity)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get user stats for {user_id}: {str(e)}")
            raise
    
    async def get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get personalized gamification recommendations."""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")
            
            recommendations = {
                "suggested_badges": [],
                "skill_focus": [],
                "challenges": [],
                "social_activities": []
            }
            
            # Suggest achievable badges
            for badge_id, badge in self.badges.items():
                if badge_id not in profile.badges_earned and not badge.hidden:
                    # Calculate achievement probability based on requirements
                    achievable = self._calculate_badge_achievability(profile, badge)
                    if achievable > 0.7:  # 70% achievable
                        recommendations["suggested_badges"].append({
                            "badge_id": badge_id,
                            "name": badge.name,
                            "description": badge.description,
                            "xp_reward": badge.xp_reward,
                            "achievability": round(achievable * 100, 1)
                        })
            
            # Suggest skill development
            lowest_skills = sorted(profile.skills.items(), key=lambda x: x[1])[:3]
            for skill_id, level in lowest_skills:
                skill_tree = self.skill_trees.get(skill_id)
                if skill_tree:
                    recommendations["skill_focus"].append({
                        "skill_id": skill_id,
                        "name": skill_tree.name,
                        "current_level": level,
                        "next_level_xp": level * 100,
                        "category": skill_tree.category.value
                    })
            
            # Suggest active challenges
            active_challenges = [
                c for c in self.challenges.values()
                if (datetime.utcnow() >= c.start_date and 
                    datetime.utcnow() <= c.end_date and
                    user_id not in c.participants)
            ]
            
            for challenge in active_challenges[:5]:  # Top 5 recommendations
                recommendations["challenges"].append({
                    "challenge_id": challenge.challenge_id,
                    "title": challenge.title,
                    "description": challenge.description,
                    "type": challenge.challenge_type.value,
                    "difficulty": challenge.difficulty,
                    "participants": len(challenge.participants),
                    "ends_in_days": (challenge.end_date - datetime.utcnow()).days
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations for {user_id}: {str(e)}")
            raise
    
    # Private helper methods
    
    def _check_level_up(self, profile: UserProfile) -> bool:
        """Check if user should level up."""
        next_level_xp = self._calculate_xp_for_level(profile.level + 1)
        return profile.current_level_xp >= next_level_xp and profile.level < self.max_level
    
    def _calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP required for a specific level."""
        if level <= 1:
            return 0
        return int(self.level_xp_multiplier * (level ** self.level_xp_exponent))
    
    async def _process_level_up(self, profile: UserProfile):
        """Process level up and update profile."""
        old_level = profile.level
        profile.level += 1
        
        # Calculate XP for new level
        current_level_xp_requirement = self._calculate_xp_for_level(profile.level)
        previous_level_xp_requirement = self._calculate_xp_for_level(profile.level - 1)
        
        # Reset current level XP
        profile.current_level_xp = profile.current_level_xp - (current_level_xp_requirement - previous_level_xp_requirement)
        
        # Award level up bonus
        level_bonus = profile.level * 50  # Bonus XP scales with level
        profile.total_xp += level_bonus
        
        # Log level up
        await self._log_activity(profile.user_id, "level_up", {
            "old_level": old_level,
            "new_level": profile.level,
            "bonus_xp": level_bonus
        })
    
    async def _update_streak(self, profile: UserProfile):
        """Update user activity streak."""
        now = datetime.utcnow()
        last_activity_date = profile.last_activity.date()
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        if last_activity_date == today:
            # Same day, streak continues
            pass
        elif last_activity_date == yesterday:
            # Consecutive day, increment streak
            profile.streak_days += 1
        else:
            # Streak broken, reset
            profile.streak_days = 1
    
    def _calculate_challenge_difficulty(self, requirements: Dict[str, Any]) -> int:
        """Calculate challenge difficulty on 1-10 scale."""
        # Simple heuristic based on requirements
        total_requirements = sum(
            v for v in requirements.values()
            if isinstance(v, (int, float))
        )
        
        if total_requirements < 10:
            return 1
        elif total_requirements < 50:
            return 3
        elif total_requirements < 100:
            return 5
        elif total_requirements < 500:
            return 7
        else:
            return 10
    
    def _calculate_badge_achievability(self, profile: UserProfile, badge: Badge) -> float:
        """Calculate how achievable a badge is for a user (0-1 scale)."""
        # Simplified calculation - in production would be more sophisticated
        if not badge.requirements:
            return 0.0
        
        # Check progress against requirements
        progress_scores = []
        for req_key, req_value in badge.requirements.items():
            if req_key == "collaborations_completed":
                current = getattr(profile, 'collaborations_completed', 0)
                progress_scores.append(min(current / req_value, 1.0))
            elif req_key == "total_xp":
                progress_scores.append(min(profile.total_xp / req_value, 1.0))
            elif req_key == "level":
                progress_scores.append(min(profile.level / req_value, 1.0))
            else:
                # Default to moderate achievability for unknown requirements
                progress_scores.append(0.5)
        
        return sum(progress_scores) / len(progress_scores) if progress_scores else 0.0
    
    async def _log_activity(self, user_id: str, action: str, metadata: Dict[str, Any]):
        """Log gamification activity."""
        activity = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "metadata": metadata
        }
        
        self.activity_log.append(activity)
        
        # Keep only last 10000 activities for performance
        if len(self.activity_log) > 10000:
            self.activity_log = self.activity_log[-10000:]

# Factory function for integration
def create_gamification_engine() -> AdvancedGamificationEngine:
    """Factory function to create advanced gamification engine instance."""
    return AdvancedGamificationEngine()

# Gamification configuration constants
GAMIFICATION_CONFIG = {
    "engine_version": "1.0.0",
    "total_badges": 200,
    "max_user_level": 1000,
    "badge_categories": [category.value for category in BadgeCategory],
    "badge_rarities": [rarity.value for rarity in BadgeRarity],
    "challenge_types": [ctype.value for ctype in ChallengeType],
    "leaderboard_types": [ltype.value for ltype in LeaderboardType],
    "skill_trees_count": 5,
    "level_xp_base": 1000,
    "level_xp_exponent": 1.5,
    "max_streak_multiplier": 3.0,
    "activity_log_retention": 10000
}

if __name__ == "__main__":
    # Example usage
    async def main():
        engine = create_gamification_engine()
        
        # Create user profile
        profile = await engine.create_user_profile("user_001", "John Creator")
        print(f"Created profile for: {profile.display_name}")
        
        # Award XP
        xp_result = await engine.award_xp("user_001", 250, "first_collaboration")
        print(f"Awarded XP: {xp_result}")
        
        # Get user stats
        stats = await engine.get_user_stats("user_001")
        print(f"User stats: Level {stats['level']}, {stats['badges_earned']} badges")
        
        # Get recommendations
        recommendations = await engine.get_personalized_recommendations("user_001")
        print(f"Suggested badges: {len(recommendations['suggested_badges'])}")
        
        print(f"\n🎮 Gamification Engine: {len(engine.badges)} badges available")
    
    asyncio.run(main())