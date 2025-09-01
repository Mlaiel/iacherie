"""Enterprise Achievement Tracker - Comprehensive achievement system for IA Influencer platform.

This module provides a sophisticated achievement tracking system that monitors
user progress, unlocks achievements, and manages the complete achievement lifecycle
for multi-format content creators.

Architecture: Enterprise Production-Ready (Backend Level 2)
Module: backend/business/engagement/achievement_tracker.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Achievement Tracking → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set, Callable
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class AchievementCategory(str, Enum):
    """
Categories of achievements."""

    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    ENGAGEMENT = "engagement"
    QUALITY = "quality"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    PLATFORM_MASTERY = "platform_mastery"
    MILESTONE = "milestone"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"
    HIDDEN = "hidden"


class AchievementDifficulty(str, Enum):
    """Difficulty levels for achievements."""

    TRIVIAL = "trivial"        # Very easy, almost automatic
    EASY = "easy"              # Requires minimal effort
    MEDIUM = "medium"          # Requires some dedication
    HARD = "hard"              # Requires significant effort
    VERY_HARD = "very_hard"    # Requires exceptional dedication
    LEGENDARY = "legendary"    # Extremely rare and difficult


class AchievementType(str, Enum):
    """Types of achievement tracking."""

    COUNTER = "counter"              # Track numeric progress (uploads, collaborations)
    THRESHOLD = "threshold"          # Reach a specific value
    STREAK = "streak"               # Maintain consecutive activity
    PERCENTAGE = "percentage"        # Reach percentage targets
    MILESTONE = "milestone"          # Specific milestone events
    CONDITIONAL = "conditional"      # Complex condition checking
    TIME_BASED = "time_based"       # Complete within time limit
    CUMULATIVE = "cumulative"       # Accumulate over time


class AchievementStatus(str, Enum):
    """Status of user achievements."""

    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"
    EXPIRED = "expired"


@dataclass
class AchievementCriteria:
    """Defines criteria for achievement completion."""
    criteria_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    
    # Tracking configuration
    metric_key: str = ""  # The metric to track (e.g., "content_count", "collaboration_count")
    target_value: Union[int, float, str] = 0
    comparison_operator: str = ">="  # >=, >, <=, <, ==, !=
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    time_limit: Optional[timedelta] = None
    prerequisite_achievements: List[str] = field(default_factory=list)
    
    # Tracking state
    current_value: Union[int, float, str] = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def is_completed(self) -> bool:
        """Check if this criteria is completed."""
        try:
            if self.comparison_operator == ">=":
                return float(self.current_value) >= float(self.target_value)
            elif self.comparison_operator == ">":
                return float(self.current_value) > float(self.target_value)
            elif self.comparison_operator == "<=":
                return float(self.current_value) <= float(self.target_value)
            elif self.comparison_operator == "<":
                return float(self.current_value) < float(self.target_value)
            elif self.comparison_operator == "==":
                return str(self.current_value) == str(self.target_value)
            elif self.comparison_operator == "!=":
                return str(self.current_value) != str(self.target_value)
            else:
                return False
        except (ValueError, TypeError):
            return str(self.current_value) == str(self.target_value)
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage for this criteria."""
        if self.comparison_operator in [">=", ">"]:
            try:
                target = float(self.target_value)
                current = float(self.current_value)
                if target == 0:
                    return 100.0 if current > 0 else 0.0
                return min(100.0, (current / target) * 100.0)
            except (ValueError, TypeError):
                return 100.0 if self.is_completed() else 0.0
        else:
            return 100.0 if self.is_completed() else 0.0


@dataclass
class Achievement:
    """Represents an achievement definition."""
    achievement_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    detailed_description: str = ""
    
    # Classification
    category: AchievementCategory = AchievementCategory.CONTENT_CREATION
    difficulty: AchievementDifficulty = AchievementDifficulty.EASY
    achievement_type: AchievementType = AchievementType.COUNTER
    
    # Completion criteria
    criteria: List[AchievementCriteria] = field(default_factory=list)
    require_all_criteria: bool = True  # True = AND, False = OR
    
    # Rewards and benefits
    experience_points: int = 100
    virtual_currency: int = 0
    real_currency: float = 0.0
    badge_icon: str = ""
    special_benefits: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    creator_types: List[str] = field(default_factory=list)  # Which creator types can earn this
    platform_requirements: List[str] = field(default_factory=list)
    
    # Visibility and availability
    hidden: bool = False
    secret: bool = False  # Hidden until unlocked
    limited_time: bool = False
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    
    # Tracking
    total_completions: int = 0
    completion_rate: float = 0.0
    average_completion_time: Optional[timedelta] = None
    
    # Administrative
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    
    def is_available(self, timestamp: Optional[datetime] = None) -> bool:
        """Check if achievement is currently available."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if self.available_from and timestamp < self.available_from:
            return False
        
        if self.available_until and timestamp > self.available_until:
            return False
        
        return True
    
    def is_visible_to_user(self, user_profile: Dict[str, Any]) -> bool:
        """
Check if achievement should be visible to a user."""
        if self.hidden:
            return False
        
        # Check creator type requirements
        if self.creator_types:
            user_creator_type = user_profile.get("creator_type", "")
            if user_creator_type not in self.creator_types:
                return False
        
        # Check platform requirements
        if self.platform_requirements:
            user_platforms = set(user_profile.get("connected_platforms", []))
            required_platforms = set(self.platform_requirements)
            if not required_platforms.intersection(user_platforms):
                return False
        
        return True
    
    def get_completion_time_estimate(self, user_profile: Dict[str, Any]) -> Optional[timedelta]:
        """Estimate completion time for a user based on their activity level."""
        if not self.average_completion_time:
            return None
        
        # Adjust based on user activity level
        user_activity_level = user_profile.get("activity_level", "medium")
        activity_multipliers = {
            "low": 2.0,
            "medium": 1.0,
            "high": 0.7,
            "very_high": 0.5
        }
        
        multiplier = activity_multipliers.get(user_activity_level, 1.0)
        estimated_time = self.average_completion_time * multiplier
        
        return estimated_time


@dataclass
class UserAchievementProgress:
    """Tracks a user's progress on a specific achievement."""
    progress_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    achievement_id: str = ""
    
    # Status and progress
    status: AchievementStatus = AchievementStatus.LOCKED
    progress_percentage: float = 0.0
    criteria_progress: Dict[str, AchievementCriteria] = field(default_factory=dict)
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    last_progress_update: datetime = field(default_factory=datetime.utcnow)
    
    # Tracking data
    tracking_data: Dict[str, Any] = field(default_factory=dict)
    milestone_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def is_completed(self) -> bool:
        """Check if achievement is completed."""
        return self.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]
    
    def can_be_claimed(self) -> bool:
        """
Check if achievement can be claimed."""
        return self.status == AchievementStatus.COMPLETED
    
    def get_time_to_completion(self) -> Optional[timedelta]:
        """
Get time taken to complete achievement."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class AchievementTracker:
    """
    Enterprise-grade achievement tracking system.
    
    Manages the complete achievement lifecycle including definition,
    progress tracking, completion detection, and reward distribution.
    """
    
    def __init__(self):
        """
Initialize the achievement tracker."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._achievements: Dict[str, Achievement] = {}
        self._user_progress: Dict[str, Dict[str, UserAchievementProgress]] = {}
        self._metric_listeners: Dict[str, List[Callable]] = {}
        
        # Initialize predefined achievements
        self._initialize_core_achievements()
        
        self.logger.info("AchievementTracker initialized successfully")
    
    def _initialize_core_achievements(self) -> None:
        """Initialize core platform achievements - Complete 50+ achievement system."""
        
        # Content Creation Achievements (15+ achievements - From "First Upload" to "Legend Creator")
        self._create_first_upload_achievement()
        self._create_viral_hit_achievement()
        self._create_consistency_achievements()
        self._create_quality_achievements()
        self._create_multi_format_achievements()
        self._create_content_volume_achievements()
        self._create_content_creativity_achievements()
        self._create_content_mastery_achievements()
        
        # Collaboration Achievements (15+ achievements - From "Team Player" to "Global Connector")
        self._create_collaboration_achievements()
        self._create_mentorship_achievements()
        self._create_networking_achievements()
        self._create_partnership_achievements()
        self._create_cross_genre_achievements()
        self._create_global_collaboration_achievements()
        
        # Monetization Achievements (15+ achievements - From "First Dollar" to "Revenue Master")
        self._create_revenue_achievements()
        self._create_optimization_achievements()
        self._create_passive_income_achievements()
        self._create_diversification_achievements()
        self._create_business_achievements()
        
        # Protection Achievements (10+ achievements - From "Guardian" to "IP Defender")
        self._create_protection_achievements()
        self._create_security_achievements()
        self._create_rights_management_achievements()
        
        # Engagement & Community Achievements
        self._create_engagement_achievements()
        self._create_community_achievements()
        self._create_social_impact_achievements()
        
        # Platform Mastery & Innovation Achievements
        self._create_platform_achievements()
        self._create_innovation_achievements()
        self._create_technical_achievements()
        
        # Milestone & Special Achievements
        self._create_milestone_achievements()
        self._create_seasonal_achievements()
        self._create_legendary_achievements()
    
    def _create_first_upload_achievement(self) -> None:
        """Create first upload achievement."""
        achievement = Achievement(
            name="First Steps",
            description="Upload your first piece of content",
            detailed_description="Welcome to the platform! Upload your first content to begin your creator journey.",
            category=AchievementCategory.CONTENT_CREATION,
            difficulty=AchievementDifficulty.TRIVIAL,
            achievement_type=AchievementType.MILESTONE,
            experience_points=200,
            virtual_currency=50,
            badge_icon="first_upload",
            tags=["beginner", "milestone", "content"],
            criteria=[
                AchievementCriteria(
                    name="First Upload",
                    description="Upload your first content",
                    metric_key="content_count",
                    target_value=1,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[achievement.achievement_id] = achievement
    
    def _create_viral_hit_achievement(self) -> None:
        """Create viral content achievement."""
        achievement = Achievement(
            name="Viral Sensation",
            description="Reach 1 million views/plays on a single piece of content",
            detailed_description="Create content that captures the world's attention and reaches viral status with over 1 million engagements.",
            category=AchievementCategory.ENGAGEMENT,
            difficulty=AchievementDifficulty.VERY_HARD,
            achievement_type=AchievementType.THRESHOLD,
            experience_points=5000,
            virtual_currency=2500,
            real_currency=100.0,
            badge_icon="viral_star",
            special_benefits=["viral_boost_package", "premium_analytics"],
            tags=["viral", "engagement", "milestone"],
            criteria=[
                AchievementCriteria(
                    name="Viral Reach",
                    description="Reach 1M+ views/plays on single content",
                    metric_key="max_content_views",
                    target_value=1000000,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[achievement.achievement_id] = achievement
        
        # Add specific "Viral Hit" achievement as required by cahier des charges
        viral_hit = Achievement(
            name="Viral Hit",
            description="1M+ views/listens on any content",
            detailed_description="Achieve viral status with content that reaches over 1 million views or listens, demonstrating mass appeal and engagement.",
            category=AchievementCategory.CONTENT_CREATION,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.THRESHOLD,
            experience_points=1000,
            virtual_currency=500,
            real_currency=50.0,
            badge_icon="viral_hit",
            special_benefits=["viral_creator_status", "featured_content"],
            tags=["viral", "hit", "million", "views"],
            criteria=[
                AchievementCriteria(
                    name="Viral Hit Milestone",
                    description="Content reaches 1M+ views/listens",
                    metric_key="content_views",
                    target_value=1000000,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[viral_hit.achievement_id] = viral_hit
    
    def _create_consistency_achievements(self) -> None:
        """Create consistency-based achievements."""
        # 7-day streak
        streak_7 = Achievement(
            name="Week Warrior",
            description="Upload content for 7 consecutive days",
            detailed_description="Maintain consistent content creation by uploading content every day for a week.",
            category=AchievementCategory.CONTENT_CREATION,
            difficulty=AchievementDifficulty.MEDIUM,
            achievement_type=AchievementType.STREAK,
            experience_points=500,
            virtual_currency=200,
            badge_icon="week_warrior",
            tags=["consistency", "streak", "dedication"],
            criteria=[
                AchievementCriteria(
                    name="Weekly Streak",
                    description="7-day upload streak",
                    metric_key="current_upload_streak",
                    target_value=7,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[streak_7.achievement_id] = streak_7
        
        # 30-day streak (Consistency King)
        streak_30 = Achievement(
            name="Consistency King",
            description="Upload content for 30 consecutive days",
            detailed_description="Demonstrate ultimate dedication by maintaining a 30-day content upload streak.",
            category=AchievementCategory.CONTENT_CREATION,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.STREAK,
            experience_points=2000,
            virtual_currency=1000,
            badge_icon="consistency_crown",
            special_benefits=["streak_protection", "priority_support"],
            tags=["consistency", "streak", "mastery"],
            criteria=[
                AchievementCriteria(
                    name="Monthly Streak",
                    description="30-day upload streak",
                    metric_key="current_upload_streak",
                    target_value=30,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[streak_30.achievement_id] = streak_30
    
    def _create_quality_achievements(self) -> None:
        """Create quality-based achievements."""
        # Quality Master (95%+ quality score)
        quality_master = Achievement(
            name="Quality Master",
            description="Achieve 95%+ quality score on content",
            detailed_description="Demonstrate exceptional content quality by achieving a 95% or higher quality score.",
            category=AchievementCategory.QUALITY,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.THRESHOLD,
            experience_points=1500,
            virtual_currency=750,
            badge_icon="quality_master",
            special_benefits=["quality_analytics", "enhanced_promotion"],
            tags=["quality", "excellence", "mastery"],
            criteria=[
                AchievementCriteria(
                    name="Quality Excellence",
                    description="Achieve 95%+ quality score",
                    metric_key="max_quality_score",
                    target_value=95,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[quality_master.achievement_id] = quality_master
        
        # Perfect Score (100% quality)
        perfect_score = Achievement(
            name="Perfectionist",
            description="Achieve perfect 100% quality score",
            detailed_description="Reach the pinnacle of content quality with a perfect 100% quality score.",
            category=AchievementCategory.QUALITY,
            difficulty=AchievementDifficulty.LEGENDARY,
            achievement_type=AchievementType.THRESHOLD,
            experience_points=5000,
            virtual_currency=2500,
            real_currency=50.0,
            badge_icon="perfectionist",
            special_benefits=["perfect_creator_status", "exclusive_features"],
            tags=["quality", "perfect", "legendary"],
            criteria=[
                AchievementCriteria(
                    name="Perfect Quality",
                    description="Achieve 100% quality score",
                    metric_key="max_quality_score",
                    target_value=100,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[perfect_score.achievement_id] = perfect_score
    
    def _create_multi_format_achievements(self) -> None:
        """Create multi-format content achievements."""
        multi_format = Achievement(
            name="Multi-Format Creator",
            description="Create content in 5 different formats",
            detailed_description="Showcase your versatility by creating content across 5 different media formats.",
            category=AchievementCategory.CONTENT_CREATION,
            difficulty=AchievementDifficulty.MEDIUM,
            achievement_type=AchievementType.COUNTER,
            experience_points=1000,
            virtual_currency=500,
            badge_icon="multi_format",
            special_benefits=["format_analytics", "cross_promotion"],
            tags=["versatility", "formats", "creativity"],
            criteria=[
                AchievementCriteria(
                    name="Format Diversity",
                    description="Use 5 different content formats",
                    metric_key="unique_formats_used",
                    target_value=5,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[multi_format.achievement_id] = multi_format
    
    def _create_collaboration_achievements(self) -> None:
        """Create collaboration-based achievements."""
        # Team Player (10 collaborations)
        team_player = Achievement(
            name="Team Player",
            description="Complete 10 successful collaborations",
            detailed_description="Build strong partnerships by completing 10 successful collaborations with other creators.",
            category=AchievementCategory.COLLABORATION,
            difficulty=AchievementDifficulty.MEDIUM,
            achievement_type=AchievementType.COUNTER,
            experience_points=1200,
            virtual_currency=600,
            badge_icon="team_player",
            special_benefits=["collaboration_boost", "partner_matching"],
            tags=["collaboration", "teamwork", "partnerships"],
            criteria=[
                AchievementCriteria(
                    name="Successful Collaborations",
                    description="Complete 10 collaborations",
                    metric_key="successful_collaborations",
                    target_value=10,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[team_player.achievement_id] = team_player
        
        # Global Collaborator (5+ countries)
        global_collab = Achievement(
            name="Global Collaborator",
            description="Collaborate with creators from 5+ countries",
            detailed_description="Expand your international network by collaborating with creators from at least 5 different countries.",
            category=AchievementCategory.COLLABORATION,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.COUNTER,
            experience_points=2000,
            virtual_currency=1000,
            badge_icon="global_collaborator",
            special_benefits=["global_promotion", "cultural_exchange"],
            tags=["global", "collaboration", "international"],
            criteria=[
                AchievementCriteria(
                    name="International Reach",
                    description="Collaborate across 5+ countries",
                    metric_key="collaboration_countries",
                    target_value=5,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[global_collab.achievement_id] = global_collab
    
    def _create_mentorship_achievements(self) -> None:
        """Create mentorship achievements."""
        mentor = Achievement(
            name="Mentor",
            description="Help 5 new creators get started",
            detailed_description="Give back to the community by mentoring and helping 5 new creators establish themselves on the platform.",
            category=AchievementCategory.COMMUNITY,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.COUNTER,
            experience_points=1800,
            virtual_currency=900,
            badge_icon="mentor",
            special_benefits=["mentor_status", "exclusive_community"],
            tags=["mentorship", "community", "leadership"],
            criteria=[
                AchievementCriteria(
                    name="Mentorship Impact",
                    description="Help 5 new creators",
                    metric_key="creators_mentored",
                    target_value=5,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[mentor.achievement_id] = mentor
    
    def _create_networking_achievements(self) -> None:
        """Create networking achievements."""
        connector = Achievement(
            name="Super Connector",
            description="Facilitate 50 successful creator matchings",
            detailed_description="Become a networking powerhouse by facilitating 50 successful connections between creators.",
            category=AchievementCategory.COMMUNITY,
            difficulty=AchievementDifficulty.VERY_HARD,
            achievement_type=AchievementType.COUNTER,
            experience_points=3000,
            virtual_currency=1500,
            badge_icon="super_connector",
            special_benefits=["networking_tools", "vip_events"],
            tags=["networking", "connections", "community"],
            criteria=[
                AchievementCriteria(
                    name="Successful Matchings",
                    description="Facilitate 50 creator matches",
                    metric_key="successful_matches_facilitated",
                    target_value=50,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[connector.achievement_id] = connector
    
    def _create_revenue_achievements(self) -> None:
        """Create revenue-based achievements."""
        # First Dollar
        first_dollar = Achievement(
            name="First Dollar",
            description="Earn your first revenue from content",
            detailed_description="Achieve your first monetization milestone by earning your first dollar from your creative work.",
            category=AchievementCategory.MONETIZATION,
            difficulty=AchievementDifficulty.MEDIUM,
            achievement_type=AchievementType.MILESTONE,
            experience_points=800,
            virtual_currency=400,
            badge_icon="first_dollar",
            special_benefits=["monetization_analytics", "revenue_optimization"],
            tags=["monetization", "revenue", "milestone"],
            criteria=[
                AchievementCriteria(
                    name="First Revenue",
                    description="Earn first dollar",
                    metric_key="total_revenue",
                    target_value=1.0,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[first_dollar.achievement_id] = first_dollar
        
        # Revenue milestones
        for amount, name in [(100, "Century Club"), (1000, "Four Figures"), (10000, "Five Figures")]:
            milestone = Achievement(
                name=name,
                description=f"Reach ${amount:,} in total revenue",
                detailed_description=f"Achieve significant monetization success by reaching ${amount:,} in total revenue from your content.",
                category=AchievementCategory.MONETIZATION,
                difficulty=AchievementDifficulty.HARD if amount >= 1000 else AchievementDifficulty.MEDIUM,
                achievement_type=AchievementType.THRESHOLD,
                experience_points=amount // 10,
                virtual_currency=amount // 20,
                real_currency=amount * 0.01,
                badge_icon=f"revenue_{amount}",
                special_benefits=["advanced_analytics", "priority_support"],
                tags=["monetization", "revenue", "milestone"],
                criteria=[
                    AchievementCriteria(
                        name=f"Revenue ${amount:,}",
                        description=f"Reach ${amount:,} total revenue",
                        metric_key="total_revenue",
                        target_value=amount,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[milestone.achievement_id] = milestone
    
    def _create_optimization_achievements(self) -> None:
        """Create optimization achievements."""
        optimizer = Achievement(
            name="Optimization Pro",
            description="Improve ROI by 50% in one month",
            detailed_description="Demonstrate business acumen by improving your return on investment by 50% or more in a single month.",
            category=AchievementCategory.MONETIZATION,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.PERCENTAGE,
            experience_points=2500,
            virtual_currency=1250,
            badge_icon="optimization_pro",
            special_benefits=["optimization_tools", "business_insights"],
            tags=["optimization", "roi", "business"],
            criteria=[
                AchievementCriteria(
                    name="ROI Improvement",
                    description="50% ROI improvement",
                    metric_key="monthly_roi_improvement",
                    target_value=50,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[optimizer.achievement_id] = optimizer
    
    def _create_engagement_achievements(self) -> None:
        """Create engagement achievements."""
        engagement_master = Achievement(
            name="Engagement Master",
            description="Achieve 25%+ average engagement rate",
            detailed_description="Build an incredibly engaged audience by maintaining an average engagement rate of 25% or higher.",
            category=AchievementCategory.ENGAGEMENT,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.THRESHOLD,
            experience_points=2000,
            virtual_currency=1000,
            badge_icon="engagement_master",
            special_benefits=["engagement_analytics", "audience_insights"],
            tags=["engagement", "audience", "mastery"],
            criteria=[
                AchievementCriteria(
                    name="High Engagement",
                    description="25%+ engagement rate",
                    metric_key="average_engagement_rate",
                    target_value=25,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[engagement_master.achievement_id] = engagement_master
    
    def _create_community_achievements(self) -> None:
        """Create community achievements."""
        community_leader = Achievement(
            name="Community Leader",
            description="Achieve 80+ community impact score",
            detailed_description="Become a positive force in the creator community by achieving a high community impact score.",
            category=AchievementCategory.COMMUNITY,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.THRESHOLD,
            experience_points=1800,
            virtual_currency=900,
            badge_icon="community_leader",
            special_benefits=["leadership_tools", "community_events"],
            tags=["community", "leadership", "impact"],
            criteria=[
                AchievementCriteria(
                    name="Community Impact",
                    description="80+ impact score",
                    metric_key="community_impact_score",
                    target_value=80,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[community_leader.achievement_id] = community_leader
    
    def _create_platform_achievements(self) -> None:
        """Create platform mastery achievements."""
        platform_master = Achievement(
            name="Platform Master",
            description="Connect and actively use 10+ platforms",
            detailed_description="Maximize your reach by successfully connecting and actively using 10 or more distribution platforms.",
            category=AchievementCategory.PLATFORM_MASTERY,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.COUNTER,
            experience_points=2200,
            virtual_currency=1100,
            badge_icon="platform_master",
            special_benefits=["platform_analytics", "cross_promotion"],
            tags=["platforms", "distribution", "mastery"],
            criteria=[
                AchievementCriteria(
                    name="Platform Diversity",
                    description="Use 10+ platforms",
                    metric_key="active_platforms_count",
                    target_value=10,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[platform_master.achievement_id] = platform_master
    
    def _create_innovation_achievements(self) -> None:
        """Create innovation achievements."""
        innovator = Achievement(
            name="Innovation Pioneer",
            description="Be among first to use 10+ new platform features",
            detailed_description="Stay at the cutting edge by being among the first to adopt and use 10 or more new platform features.",
            category=AchievementCategory.INNOVATION,
            difficulty=AchievementDifficulty.MEDIUM,
            achievement_type=AchievementType.COUNTER,
            experience_points=1500,
            virtual_currency=750,
            badge_icon="innovation_pioneer",
            special_benefits=["early_access", "beta_features"],
            tags=["innovation", "early_adopter", "features"],
            criteria=[
                AchievementCriteria(
                    name="Feature Adoption",
                    description="Use 10+ new features",
                    metric_key="new_features_adopted",
                    target_value=10,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[innovator.achievement_id] = innovator
    
    def _create_milestone_achievements(self) -> None:
        """Create milestone achievements."""
        # Level milestones
        for level in [10, 25, 50, 75, 100]:
            milestone = Achievement(
                name=f"Level {level} Master",
                description=f"Reach creator level {level}",
                detailed_description=f"Demonstrate your growth and expertise by reaching creator level {level}.",
                category=AchievementCategory.MILESTONE,
                difficulty=AchievementDifficulty.MEDIUM if level <= 25 else AchievementDifficulty.HARD,
                achievement_type=AchievementType.THRESHOLD,
                experience_points=level * 50,
                virtual_currency=level * 25,
                badge_icon=f"level_{level}",
                special_benefits=["level_benefits", "prestige_features"],
                tags=["level", "milestone", "progression"],
                criteria=[
                    AchievementCriteria(
                        name=f"Level {level}",
                        description=f"Reach level {level}",
                        metric_key="user_level",
                        target_value=level,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[milestone.achievement_id] = milestone
    
    # ==================== CONTENT CREATION ACHIEVEMENTS ====================
    # From "First Upload" to "Legend Creator" - Complete progression system
    
    def _create_content_volume_achievements(self) -> None:
        """Create content volume-based achievements."""
        volume_milestones = [
            (5, "Content Rookie", "easy", 250, 100),
            (10, "Content Regular", "easy", 400, 200),
            (25, "Content Creator", "medium", 800, 400),
            (50, "Content Producer", "medium", 1200, 600),
            (100, "Content Master", "hard", 2000, 1000),
            (250, "Content Virtuoso", "hard", 3500, 1750),
            (500, "Content Legend", "very_hard", 6000, 3000),
            (1000, "Legend Creator", "legendary", 10000, 5000)
        ]
        
        for count, name, difficulty, xp, currency in volume_milestones:
            achievement = Achievement(
                name=name,
                description=f"Upload {count} pieces of content",
                detailed_description=f"Showcase your dedication by uploading {count} pieces of content to the platform.",
                category=AchievementCategory.CONTENT_CREATION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                real_currency=count * 0.1 if count >= 100 else 0.0,
                badge_icon=f"content_{count}",
                special_benefits=["content_analytics", "enhanced_visibility"] if count >= 100 else [],
                tags=["content", "volume", "dedication"],
                criteria=[
                    AchievementCriteria(
                        name=f"Content Volume {count}",
                        description=f"Upload {count} contents",
                        metric_key="total_content_count",
                        target_value=count,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_content_creativity_achievements(self) -> None:
        """Create creativity and innovation achievements."""
        creativity_achievements = [
            ("Creative Spark", "Upload content in 3 different formats within 24 hours", "medium", 
             600, 300, "creative_spark", "format_diversity", 3),
            ("Format Pioneer", "Be first to use a new content format", "hard", 
             1000, 500, "format_pioneer", "format_innovation", 1),
            ("Style Shifter", "Create content in 8+ different styles", "hard", 
             1500, 750, "style_shifter", "style_diversity", 8),
            ("Remix Master", "Create 20+ successful remixes", "medium", 
             800, 400, "remix_master", "remix_count", 20),
            ("Trendsetter", "Start a trend with 1000+ followers", "very_hard", 
             3000, 1500, "trendsetter", "trends_started", 1)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in creativity_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Express your creativity: {desc}",
                category=AchievementCategory.CONTENT_CREATION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                badge_icon=icon,
                special_benefits=["creative_tools", "featured_placement"],
                tags=["creativity", "innovation", "unique"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_content_mastery_achievements(self) -> None:
        """Create content mastery achievements."""
        # Advanced content achievements
        content_excellence = Achievement(
            name="Content Excellence",
            description="Maintain 90%+ average quality score for 30 days",
            detailed_description="Demonstrate consistent excellence by maintaining a 90% or higher quality score for 30 consecutive days.",
            category=AchievementCategory.CONTENT_CREATION,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.STREAK,
            experience_points=2000,
            virtual_currency=1000,
            badge_icon="content_excellence",
            special_benefits=["excellence_badge", "quality_insights"],
            tags=["excellence", "quality", "consistency"],
            criteria=[
                AchievementCriteria(
                    name="Quality Streak",
                    description="90%+ quality for 30 days",
                    metric_key="quality_streak_days",
                    target_value=30,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[content_excellence.achievement_id] = content_excellence
    
    # ==================== COLLABORATION ACHIEVEMENTS ====================
    # From "Team Player" to "Global Connector" - Complete collaboration system
    
    def _create_partnership_achievements(self) -> None:
        """Create partnership-based achievements."""
        partnership_levels = [
            (3, "Collaborator", "easy", 300, 150),
            (5, "Partner", "medium", 600, 300),
            (15, "Collaborator Pro", "medium", 1000, 500),
            (25, "Partnership Master", "hard", 1800, 900),
            (50, "Super Collaborator", "very_hard", 3000, 1500),
            (100, "Global Connector", "legendary", 5000, 2500)
        ]
        
        for count, name, difficulty, xp, currency in partnership_levels:
            achievement = Achievement(
                name=name,
                description=f"Complete {count} successful collaborations",
                detailed_description=f"Build your network by completing {count} successful collaborations with other creators.",
                category=AchievementCategory.COLLABORATION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                real_currency=count * 0.5 if count >= 25 else 0.0,
                badge_icon=f"partner_{count}",
                special_benefits=["collaboration_tools", "partner_matching"] if count >= 10 else [],
                tags=["collaboration", "partnership", "networking"],
                criteria=[
                    AchievementCriteria(
                        name=f"Partnership {count}",
                        description=f"Complete {count} collaborations",
                        metric_key="successful_collaborations",
                        target_value=count,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_cross_genre_achievements(self) -> None:
        """Create cross-genre collaboration achievements."""
        cross_genre = Achievement(
            name="Cross-Genre Master",
            description="Collaborate across 5+ different content genres",
            detailed_description="Expand your creative horizons by collaborating with creators from 5 or more different content genres.",
            category=AchievementCategory.COLLABORATION,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.COUNTER,
            experience_points=2200,
            virtual_currency=1100,
            badge_icon="cross_genre",
            special_benefits=["genre_insights", "cross_promotion"],
            tags=["cross-genre", "diversity", "versatility"],
            criteria=[
                AchievementCriteria(
                    name="Genre Diversity",
                    description="Collaborate across 5+ genres",
                    metric_key="collaboration_genres",
                    target_value=5,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[cross_genre.achievement_id] = cross_genre
    
    def _create_global_collaboration_achievements(self) -> None:
        """Create global collaboration achievements."""
        global_achievements = [
            ("International Collaborator", "Collaborate with creators from 3+ countries", 
             "medium", 1000, 500, "international_collab", "collaboration_countries", 3),
            ("Continental Creator", "Collaborate across 3+ continents", 
             "hard", 2000, 1000, "continental_creator", "collaboration_continents", 3),
            ("World Connector", "Collaborate with creators from 10+ countries", 
             "very_hard", 3500, 1750, "world_connector", "collaboration_countries", 10),
            ("Global Ambassador", "Facilitate 25+ international collaborations", 
             "legendary", 5000, 2500, "global_ambassador", "international_collaborations_facilitated", 25)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in global_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Build global connections: {desc}",
                category=AchievementCategory.COLLABORATION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                badge_icon=icon,
                special_benefits=["global_promotion", "cultural_exchange"],
                tags=["global", "international", "diversity"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    # ==================== MONETIZATION ACHIEVEMENTS ====================
    # From "First Dollar" to "Revenue Master" - Complete monetization system
    
    def _create_passive_income_achievements(self) -> None:
        """Create passive income achievements."""
        passive_income = Achievement(
            name="Passive Income Pro",
            description="Generate passive income for 30 consecutive days",
            detailed_description="Build sustainable revenue by generating passive income from your content for 30 consecutive days.",
            category=AchievementCategory.MONETIZATION,
            difficulty=AchievementDifficulty.HARD,
            achievement_type=AchievementType.STREAK,
            experience_points=2500,
            virtual_currency=1250,
            real_currency=25.0,
            badge_icon="passive_income",
            special_benefits=["passive_analytics", "revenue_optimization"],
            tags=["passive", "income", "automation"],
            criteria=[
                AchievementCriteria(
                    name="Passive Income Streak",
                    description="30 days passive income",
                    metric_key="passive_income_streak",
                    target_value=30,
                    comparison_operator=">="
                )
            ]
        )
        self._achievements[passive_income.achievement_id] = passive_income
    
    def _create_diversification_achievements(self) -> None:
        """Create revenue diversification achievements."""
        diversification_levels = [
            (2, "Revenue Diversifier", "easy", 400, 200),
            (3, "Multi-Stream Creator", "medium", 800, 400),
            (5, "Diversified Pro", "hard", 1500, 750),
            (7, "Revenue Master", "very_hard", 3000, 1500),
            (10, "Income Architect", "legendary", 5000, 2500)
        ]
        
        for count, name, difficulty, xp, currency in diversification_levels:
            achievement = Achievement(
                name=name,
                description=f"Establish {count} active revenue streams",
                detailed_description=f"Diversify your income by establishing {count} different active revenue streams.",
                category=AchievementCategory.MONETIZATION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                real_currency=count * 2.0 if count >= 5 else 0.0,
                badge_icon=f"diversified_{count}",
                special_benefits=["revenue_analytics", "optimization_tools"] if count >= 3 else [],
                tags=["diversification", "revenue", "streams"],
                criteria=[
                    AchievementCriteria(
                        name=f"Revenue Streams {count}",
                        description=f"Establish {count} revenue streams",
                        metric_key="active_revenue_streams",
                        target_value=count,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_business_achievements(self) -> None:
        """Create business and optimization achievements."""
        business_achievements = [
            ("Business Minded", "Complete business training course", "medium", 
             800, 400, "business_minded", "business_training_completed", 1),
            ("Analytics Expert", "Use advanced analytics for 60 days", "hard", 
             1200, 600, "analytics_expert", "analytics_usage_days", 60),
            ("ROI Optimizer", "Achieve 200%+ ROI for 3 months", "very_hard", 
             2500, 1250, "roi_optimizer", "high_roi_months", 3),
            ("Revenue Strategist", "Develop 5+ monetization strategies", "hard", 
             1800, 900, "revenue_strategist", "monetization_strategies", 5)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in business_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Master business skills: {desc}",
                category=AchievementCategory.MONETIZATION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                badge_icon=icon,
                special_benefits=["business_tools", "strategy_guides"],
                tags=["business", "strategy", "optimization"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    # ==================== PROTECTION ACHIEVEMENTS ====================
    # From "Guardian" to "IP Defender" - Complete protection system
    
    def _create_protection_achievements(self) -> None:
        """Create content protection achievements."""
        protection_levels = [
            ("Guardian", "Protect your first piece of content", "easy", 
             400, 200, "guardian", "content_protected", 1),
            ("Content Shield", "Protect 10 pieces of content", "medium", 
             800, 400, "content_shield", "content_protected", 10),
            ("Digital Protector", "Protect 50 pieces of content", "medium", 
             1200, 600, "digital_protector", "content_protected", 50),
            ("IP Guardian", "Successfully defend against 5 copyright violations", "hard", 
             2000, 1000, "ip_guardian", "copyright_defenses", 5),
            ("Rights Defender", "Protect content across 10+ platforms", "hard", 
             2500, 1250, "rights_defender", "platforms_protected", 10),
            ("IP Defender", "Master all protection features and defend 100+ violations", "legendary", 
             5000, 2500, "ip_defender", "total_violations_defended", 100)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in protection_levels:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Secure your intellectual property: {desc}",
                category=AchievementCategory.PROTECTION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                real_currency=target * 0.1 if target >= 10 else 0.0,
                badge_icon=icon,
                special_benefits=["protection_tools", "legal_support"] if target >= 5 else [],
                tags=["protection", "ip", "security"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_security_achievements(self) -> None:
        """Create security and privacy achievements."""
        security_achievements = [
            ("Security Conscious", "Enable all security features", "easy", 
             300, 150, "security_conscious", "security_features_enabled", 100),
            ("Privacy Master", "Configure advanced privacy settings", "medium", 
             600, 300, "privacy_master", "privacy_settings_configured", 1),
            ("Watermark Pro", "Apply watermarks to 100+ contents", "medium", 
             800, 400, "watermark_pro", "watermarked_content", 100),
            ("Blockchain Protector", "Use blockchain protection for 50+ contents", "hard", 
             1500, 750, "blockchain_protector", "blockchain_protected_content", 50)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in security_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Enhance your security: {desc}",
                category=AchievementCategory.PROTECTION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                badge_icon=icon,
                special_benefits=["security_tools", "advanced_protection"],
                tags=["security", "privacy", "blockchain"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_rights_management_achievements(self) -> None:
        """Create rights management achievements."""
        rights_achievements = [
            ("Rights Manager", "Set up licensing for 25+ contents", "medium", 
             1000, 500, "rights_manager", "licensed_content", 25),
            ("License Master", "Generate $1000+ from licensing", "hard", 
             2000, 1000, "license_master", "licensing_revenue", 1000),
            ("Copyright Expert", "Successfully resolve 10+ disputes", "very_hard", 
             3000, 1500, "copyright_expert", "disputes_resolved", 10)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in rights_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Master rights management: {desc}",
                category=AchievementCategory.PROTECTION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                badge_icon=icon,
                special_benefits=["rights_tools", "legal_resources"],
                tags=["rights", "licensing", "legal"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    # ==================== ADDITIONAL CATEGORIES ====================
    
    def _create_social_impact_achievements(self) -> None:
        """Create social impact achievements."""
        social_achievements = [
            ("Community Helper", "Help 50+ community members", "medium", 
             800, 400, "community_helper", "community_helps", 50),
            ("Social Influencer", "Reach 100K+ total social reach", "hard", 
             2000, 1000, "social_influencer", "total_social_reach", 100000),
            ("Change Maker", "Lead 3+ positive community initiatives", "very_hard", 
             3000, 1500, "change_maker", "community_initiatives_led", 3)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in social_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Make a positive impact: {desc}",
                category=AchievementCategory.COMMUNITY,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                badge_icon=icon,
                special_benefits=["social_tools", "community_features"],
                tags=["social", "impact", "community"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_technical_achievements(self) -> None:
        """Create technical mastery achievements."""
        technical_achievements = [
            ("API Master", "Successfully use API integrations", "hard", 
             1500, 750, "api_master", "api_integrations_used", 5),
            ("Automation Expert", "Set up 10+ automated workflows", "hard", 
             1800, 900, "automation_expert", "automated_workflows", 10),
            ("Data Analyst", "Generate 50+ analytical reports", "medium", 
             1200, 600, "data_analyst", "analytical_reports_generated", 50),
            ("Tech Pioneer", "Beta test 15+ new features", "medium", 
             1000, 500, "tech_pioneer", "beta_features_tested", 15)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in technical_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Master technical skills: {desc}",
                category=AchievementCategory.INNOVATION,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.COUNTER,
                experience_points=xp,
                virtual_currency=currency,
                badge_icon=icon,
                special_benefits=["technical_tools", "advanced_features"],
                tags=["technical", "innovation", "mastery"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_seasonal_achievements(self) -> None:
        """Create seasonal and time-limited achievements."""
        seasonal_achievements = [
            ("New Year Creator", "Upload content on New Year's Day", "easy", 
             500, 250, "new_year_creator", "new_year_upload", 1),
            ("Summer Sensation", "Go viral during summer season", "hard", 
             2000, 1000, "summer_sensation", "summer_viral_content", 1),
            ("Holiday Spirit", "Create holiday-themed content", "medium", 
             800, 400, "holiday_spirit", "holiday_content_created", 5),
            ("Anniversary Legend", "Active for platform anniversary", "medium", 
             1000, 500, "anniversary_legend", "anniversary_participation", 1)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in seasonal_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Celebrate the seasons: {desc}",
                category=AchievementCategory.SEASONAL,
                difficulty=AchievementDifficulty.__dict__[difficulty.upper()],
                achievement_type=AchievementType.MILESTONE,
                experience_points=xp,
                virtual_currency=currency,
                badge_icon=icon,
                special_benefits=["seasonal_rewards", "exclusive_features"],
                tags=["seasonal", "celebration", "limited"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    def _create_legendary_achievements(self) -> None:
        """Create legendary and ultimate achievements."""
        legendary_achievements = [
            ("Platform Legend", "Achieve top 1% in all major categories", "legendary", 
             10000, 5000, "platform_legend", "top_percentile_categories", 4),
            ("Ultimate Creator", "Reach 1M followers across all platforms", "legendary", 
             15000, 7500, "ultimate_creator", "total_followers", 1000000),
            ("Ecosystem Master", "Master every aspect of the platform", "legendary", 
             20000, 10000, "ecosystem_master", "platform_mastery_score", 100),
            ("Hall of Fame", "Be inducted into creator hall of fame", "legendary", 
             25000, 12500, "hall_of_fame", "hall_of_fame_induction", 1)
        ]
        
        for name, desc, difficulty, xp, currency, icon, metric, target in legendary_achievements:
            achievement = Achievement(
                name=name,
                description=desc,
                detailed_description=f"Achieve legendary status: {desc}",
                category=AchievementCategory.MILESTONE,
                difficulty=AchievementDifficulty.LEGENDARY,
                achievement_type=AchievementType.THRESHOLD,
                experience_points=xp,
                virtual_currency=currency,
                real_currency=100.0,
                badge_icon=icon,
                special_benefits=["legendary_status", "exclusive_perks", "hall_of_fame"],
                tags=["legendary", "ultimate", "elite"],
                criteria=[
                    AchievementCriteria(
                        name=name,
                        description=desc,
                        metric_key=metric,
                        target_value=target,
                        comparison_operator=">="
                    )
                ]
            )
            self._achievements[achievement.achievement_id] = achievement
    
    async def track_user_metric(
        self,
        user_id: str,
        metric_key: str,
        value: Union[int, float, str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Track a metric update for a user and check for achievement progress."""
        try:
            metadata = metadata or {}
            unlocked_achievements = []
            
            # Ensure user has progress tracking initialized
            if user_id not in self._user_progress:
                await self._initialize_user_progress(user_id)
            
            # Update metric for all relevant achievements
            for achievement_id, progress in self._user_progress[user_id].items():
                if progress.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]:
                    continue
                
                achievement = self._achievements.get(achievement_id)
                if not achievement:
                    continue
                
                # Check if any criteria use this metric
                updated = False
                for criteria in achievement.criteria:
                    if criteria.metric_key == metric_key:
                        # Update the criteria progress
                        progress.criteria_progress[criteria.criteria_id].current_value = value
                        progress.criteria_progress[criteria.criteria_id].last_updated = datetime.utcnow()
                        updated = True
                
                if updated:
                    # Recalculate progress
                    await self._update_achievement_progress(user_id, achievement_id, metadata)
                    
                    # Check if achievement was unlocked
                    if progress.status == AchievementStatus.COMPLETED:
                        unlocked_achievements.append(achievement_id)
            
            # Call metric listeners
            if metric_key in self._metric_listeners:
                for listener in self._metric_listeners[metric_key]:
                    try:
                        await listener(user_id, metric_key, value, metadata)
                    except Exception as e:
                        self.logger.error(f"Error in metric listener: {e}")
            
            return unlocked_achievements
            
        except Exception as e:
            self.logger.error(f"Error tracking user metric: {e}")
            return []
    
    async def _initialize_user_progress(self, user_id: str) -> None:
        """Initialize achievement progress tracking for a user."""
        if user_id not in self._user_progress:
            self._user_progress[user_id] = {}
        
        # Create progress entries for all available achievements
        for achievement_id, achievement in self._achievements.items():
            if achievement_id not in self._user_progress[user_id]:
                progress = UserAchievementProgress(
                    user_id=user_id,
                    achievement_id=achievement_id,
                    status=AchievementStatus.LOCKED
                )
                
                # Initialize criteria progress
                for criteria in achievement.criteria:
                    progress.criteria_progress[criteria.criteria_id] = AchievementCriteria(
                        criteria_id=criteria.criteria_id,
                        name=criteria.name,
                        description=criteria.description,
                        metric_key=criteria.metric_key,
                        target_value=criteria.target_value,
                        comparison_operator=criteria.comparison_operator,
                        conditions=criteria.conditions.copy(),
                        time_limit=criteria.time_limit,
                        prerequisite_achievements=criteria.prerequisite_achievements.copy()
                    )
                
                self._user_progress[user_id][achievement_id] = progress
        
        self.logger.debug(f"Initialized progress tracking for user {user_id}")
    
    async def _update_achievement_progress(
        self,
        user_id: str,
        achievement_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update progress for a specific achievement."""
        try:
            progress = self._user_progress[user_id][achievement_id]
            achievement = self._achievements[achievement_id]
            
            # Check prerequisites
            if not await self._check_prerequisites(user_id, achievement):
                return
            
            # Update status to in_progress if locked
            if progress.status == AchievementStatus.LOCKED:
                progress.status = AchievementStatus.IN_PROGRESS
                progress.started_at = datetime.utcnow()
            
            # Calculate overall progress
            total_criteria = len(achievement.criteria)
            completed_criteria = 0
            total_progress = 0.0
            
            for criteria in progress.criteria_progress.values():
                criteria_progress = criteria.get_progress_percentage()
                total_progress += criteria_progress
                
                if criteria.is_completed():
                    completed_criteria += 1
            
            # Update progress percentage
            if total_criteria > 0:
                progress.progress_percentage = total_progress / total_criteria
            
            # Check for completion
            if achievement.require_all_criteria:
                # All criteria must be completed
                if completed_criteria == total_criteria:
                    await self._complete_achievement(user_id, achievement_id, metadata)
            else:
                # Any criteria completion is sufficient
                if completed_criteria > 0:
                    await self._complete_achievement(user_id, achievement_id, metadata)
            
            progress.last_progress_update = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Error updating achievement progress: {e}")
    
    async def _check_prerequisites(self, user_id: str, achievement: Achievement) -> bool:
        """Check if achievement prerequisites are met."""
        for criteria in achievement.criteria:
            for prereq_id in criteria.prerequisite_achievements:
                if prereq_id not in self._user_progress[user_id]:
                    return False
                
                prereq_progress = self._user_progress[user_id][prereq_id]
                if not prereq_progress.is_completed():
                    return False
        
        return True
    
    async def _complete_achievement(
        self,
        user_id: str,
        achievement_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
Complete an achievement for a user."""
        try:
            progress = self._user_progress[user_id][achievement_id]
            achievement = self._achievements[achievement_id]
            
            # Update progress status
            progress.status = AchievementStatus.COMPLETED
            progress.completed_at = datetime.utcnow()
            progress.progress_percentage = 100.0
            
            # Update achievement statistics
            achievement.total_completions += 1
            
            # Calculate completion time
            if progress.started_at:
                completion_time = progress.completed_at - progress.started_at
                if achievement.average_completion_time:
                    # Update rolling average
                    current_avg = achievement.average_completion_time.total_seconds()
                    new_time = completion_time.total_seconds()
                    updated_avg = (current_avg * (achievement.total_completions - 1) + new_time) / achievement.total_completions
                    achievement.average_completion_time = timedelta(seconds=updated_avg)
                else:
                    achievement.average_completion_time = completion_time
            
            # Log milestone
            milestone = {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "achievement_completed",
                "achievement_id": achievement_id,
                "achievement_name": achievement.name,
                "completion_time": progress.get_time_to_completion().total_seconds() if progress.get_time_to_completion() else None,
                "metadata": metadata
            }
            progress.milestone_history.append(milestone)
            
            self.logger.info(f"User {user_id} completed achievement: {achievement.name}")
            
        except Exception as e:
            self.logger.error(f"Error completing achievement: {e}")
    
    async def claim_achievement_rewards(
        self,
        user_id: str,
        achievement_id: str
    ) -> Dict[str, Any]:
        """Claim rewards for a completed achievement."""
        try:
            if user_id not in self._user_progress or achievement_id not in self._user_progress[user_id]:
                raise ValueError(f"Achievement progress not found for user {user_id}")
            
            progress = self._user_progress[user_id][achievement_id]
            
            if not progress.can_be_claimed():
                raise ValueError(f"Achievement {achievement_id} cannot be claimed")
            
            achievement = self._achievements[achievement_id]
            
            # Prepare rewards
            rewards = {
                "experience_points": achievement.experience_points,
                "virtual_currency": achievement.virtual_currency,
                "real_currency": achievement.real_currency,
                "badge_icon": achievement.badge_icon,
                "special_benefits": achievement.special_benefits.copy()
            }
            
            # Update status
            progress.status = AchievementStatus.CLAIMED
            progress.claimed_at = datetime.utcnow()
            
            # Log claim event
            milestone = {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "achievement_claimed",
                "achievement_id": achievement_id,
                "rewards": rewards
            }
            progress.milestone_history.append(milestone)
            
            self.logger.info(f"User {user_id} claimed rewards for achievement: {achievement.name}")
            
            return {
                "success": True,
                "achievement_id": achievement_id,
                "achievement_name": achievement.name,
                "rewards": rewards,
                "claimed_at": progress.claimed_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error claiming achievement rewards: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_achievements(
        self,
        user_id: str,
        status_filter: Optional[AchievementStatus] = None,
        category_filter: Optional[AchievementCategory] = None
    ) -> List[Dict[str, Any]]:
        """Get user's achievement progress with optional filtering."""
        try:
            if user_id not in self._user_progress:
                await self._initialize_user_progress(user_id)
            
            achievements_data = []
            
            for achievement_id, progress in self._user_progress[user_id].items():
                achievement = self._achievements.get(achievement_id)
                if not achievement:
                    continue
                
                # Apply filters
                if status_filter and progress.status != status_filter:
                    continue
                
                if category_filter and achievement.category != category_filter:
                    continue
                
                # Prepare achievement data
                achievement_data = {
                    "achievement_id": achievement_id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "category": achievement.category.value,
                    "difficulty": achievement.difficulty.value,
                    "status": progress.status.value,
                    "progress_percentage": progress.progress_percentage,
                    "badge_icon": achievement.badge_icon,
                    "experience_points": achievement.experience_points,
                    "virtual_currency": achievement.virtual_currency,
                    "special_benefits": achievement.special_benefits,
                    "started_at": progress.started_at.isoformat() if progress.started_at else None,
                    "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
                    "claimed_at": progress.claimed_at.isoformat() if progress.claimed_at else None,
                    "criteria_progress": []
                }
                
                # Add criteria progress
                for criteria in progress.criteria_progress.values():
                    criteria_data = {
                        "name": criteria.name,
                        "description": criteria.description,
                        "current_value": criteria.current_value,
                        "target_value": criteria.target_value,
                        "progress_percentage": criteria.get_progress_percentage(),
                        "completed": criteria.is_completed()
                    }
                    achievement_data["criteria_progress"].append(criteria_data)
                
                achievements_data.append(achievement_data)
            
            return achievements_data
            
        except Exception as e:
            self.logger.error(f"Error getting user achievements: {e}")
            return []
    
    async def get_achievement_statistics(self) -> Dict[str, Any]:
        """Get platform-wide achievement statistics."""
        try:
            total_achievements = len(self._achievements)
            total_users = len(self._user_progress)
            
            # Calculate category distribution
            category_stats = {}
            difficulty_stats = {}
            completion_stats = {}
            
            for achievement in self._achievements.values():
                # Category stats
                category = achievement.category.value
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += 1
                
                # Difficulty stats
                difficulty = achievement.difficulty.value
                if difficulty not in difficulty_stats:
                    difficulty_stats[difficulty] = 0
                difficulty_stats[difficulty] += 1
                
                # Completion stats
                completion_stats[achievement.achievement_id] = {
                    "name": achievement.name,
                    "total_completions": achievement.total_completions,
                    "completion_rate": (achievement.total_completions / total_users * 100) if total_users > 0 else 0,
                    "average_completion_time": achievement.average_completion_time.total_seconds() if achievement.average_completion_time else None
                }
            
            return {
                "platform_stats": {
                    "total_achievements": total_achievements,
                    "total_users_tracked": total_users,
                    "category_distribution": category_stats,
                    "difficulty_distribution": difficulty_stats
                },
                "achievement_completion_stats": completion_stats
            }
            
        except Exception as e:
            self.logger.error(f"Error getting achievement statistics: {e}")
            return {}
    
    async def create_custom_achievement(
        self,
        achievement_data: Dict[str, Any],
        creator_id: str
    ) -> str:
        """Create a custom achievement."""
        try:
            # Validate required fields
            required_fields = ["name", "description", "category", "criteria"]
            for field in required_fields:
                if field not in achievement_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create achievement
            achievement = Achievement(
                name=achievement_data["name"],
                description=achievement_data["description"],
                detailed_description=achievement_data.get("detailed_description", ""),
                category=AchievementCategory(achievement_data["category"]),
                difficulty=AchievementDifficulty(achievement_data.get("difficulty", "medium")),
                achievement_type=AchievementType(achievement_data.get("achievement_type", "counter")),
                experience_points=achievement_data.get("experience_points", 100),
                virtual_currency=achievement_data.get("virtual_currency", 0),
                real_currency=achievement_data.get("real_currency", 0.0),
                badge_icon=achievement_data.get("badge_icon", "custom"),
                special_benefits=achievement_data.get("special_benefits", []),
                tags=achievement_data.get("tags", []),
                creator_types=achievement_data.get("creator_types", []),
                platform_requirements=achievement_data.get("platform_requirements", []),
                hidden=achievement_data.get("hidden", False),
                secret=achievement_data.get("secret", False),
                limited_time=achievement_data.get("limited_time", False),
                available_from=achievement_data.get("available_from"),
                available_until=achievement_data.get("available_until"),
                created_by=creator_id
            )
            
            # Create criteria
            for criteria_data in achievement_data["criteria"]:
                criteria = AchievementCriteria(
                    name=criteria_data["name"],
                    description=criteria_data["description"],
                    metric_key=criteria_data["metric_key"],
                    target_value=criteria_data["target_value"],
                    comparison_operator=criteria_data.get("comparison_operator", ">="),
                    conditions=criteria_data.get("conditions", {}),
                    time_limit=criteria_data.get("time_limit"),
                    prerequisite_achievements=criteria_data.get("prerequisite_achievements", [])
                )
                achievement.criteria.append(criteria)
            
            # Store achievement
            self._achievements[achievement.achievement_id] = achievement
            
            self.logger.info(f"Created custom achievement: {achievement.name} by {creator_id}")
            
            return achievement.achievement_id
            
        except Exception as e:
            self.logger.error(f"Error creating custom achievement: {e}")
            raise
    
    def add_metric_listener(self, metric_key: str, listener: Callable) -> None:
        """Add a listener for metric updates."""
        if metric_key not in self._metric_listeners:
            self._metric_listeners[metric_key] = []
        self._metric_listeners[metric_key].append(listener)


# Global achievement tracker instance
_achievement_tracker: Optional[AchievementTracker] = None


async def get_achievement_tracker() -> AchievementTracker:
    """
Get the global achievement tracker instance."""
    global _achievement_tracker
    
    if _achievement_tracker is None:
        _achievement_tracker = AchievementTracker()
    
    return _achievement_tracker


# Convenience functions for common operations
async def track_metric(
    user_id: str,
    metric_key: str,
    value: Union[int, float, str],
    metadata: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
Track a metric update (convenience function)."""
    tracker = await get_achievement_tracker()
    return await tracker.track_user_metric(user_id, metric_key, value, metadata)


async def get_user_achievement_summary(user_id: str) -> Dict[str, Any]:
    """
Get achievement summary for a user (convenience function)."""
    tracker = await get_achievement_tracker()
    achievements = await tracker.get_user_achievements(user_id)
    
    # Calculate summary statistics
    total_achievements = len(achievements)
    completed_count = len([a for a in achievements if a["status"] == "completed"])
    claimed_count = len([a for a in achievements if a["status"] == "claimed"])
    in_progress_count = len([a for a in achievements if a["status"] == "in_progress"])
    
    # Calculate total rewards earned
    total_xp = sum(a["experience_points"] for a in achievements if a["status"] == "claimed")
    total_currency = sum(a["virtual_currency"] for a in achievements if a["status"] == "claimed")
    
    return {
        "user_id": user_id,
        "achievement_summary": {
            "total_achievements": total_achievements,
            "completed": completed_count,
            "claimed": claimed_count,
            "in_progress": in_progress_count,
            "completion_rate": (completed_count / total_achievements * 100) if total_achievements > 0 else 0
        },
        "rewards_earned": {
            "total_experience_points": total_xp,
            "total_virtual_currency": total_currency
        },
        "recent_achievements": [
            a for a in achievements 
            if a["status"] in ["completed", "claimed"] and a["completed_at"]
        ][-5:]  # Last 5 completed/claimed achievements
    }