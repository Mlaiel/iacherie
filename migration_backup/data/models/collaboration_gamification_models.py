"""Collaboration Gamification Models
==================================

Advanced collaboration and gamification models for IA Influencer Agent platform.
Comprehensive creator collaboration system with gamification elements,
achievement tracking, and competitive leaderboards.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• Creator collaboration matching & management
• Comprehensive gamification system
• Achievement & badge tracking
• Competitive leaderboards & ranking
• Reward distribution & optimization
• Social features & community building
• Collaboration analytics & insights
• Cross-platform collaboration support
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date
from enum import Enum
import uuid
from typing import Optional, Dict, Any, List

# Import base from enterprise content models
from .enterprise_content_models import Base

# ============================================================================
# ENUMS - Collaboration System
# ============================================================================

class CollaborationType(Enum):
    """Types of creator collaborations"""
    MUSIC = "music"
    VIDEO = "video"
    PHOTO = "photo"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    BLOG_POST = "blog_post"
    SOCIAL_CAMPAIGN = "social_campaign"
    BRAND_PARTNERSHIP = "brand_partnership"
    CROSS_PLATFORM = "cross_platform"
    EDUCATIONAL = "educational"
    CHARITY = "charity"
    COMPETITION = "competition"
    REMIX = "remix"
    COVER = "cover"
    DUET = "duet"


class CollaborationStatus(Enum):
    """Status of collaboration projects"""
    PROPOSED = "proposed"
    PENDING_APPROVAL = "pending_approval"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"


class CollaborationRole(Enum):
    """Roles in collaboration projects"""
    INITIATOR = "initiator"
    COLLABORATOR = "collaborator"
    FEATURED_ARTIST = "featured_artist"
    PRODUCER = "producer"
    SONGWRITER = "songwriter"
    VOCALIST = "vocalist"
    INSTRUMENTALIST = "instrumentalist"
    VIDEO_CREATOR = "video_creator"
    PHOTOGRAPHER = "photographer"
    EDITOR = "editor"
    MANAGER = "manager"
    CONSULTANT = "consultant"
    REVIEWER = "reviewer"


# ============================================================================
# ENUMS - Gamification System
# ============================================================================

class GamificationElement(Enum):
    """Types of gamification elements"""
    POINTS = "points"
    BADGES = "badges"
    LEVELS = "levels"
    ACHIEVEMENTS = "achievements"
    LEADERBOARDS = "leaderboards"
    CHALLENGES = "challenges"
    QUESTS = "quests"
    REWARDS = "rewards"
    STREAKS = "streaks"
    MILESTONES = "milestones"
    COMPETITIONS = "competitions"
    RANKINGS = "rankings"
    PROGRESS_BARS = "progress_bars"
    UNLOCKABLES = "unlockables"


class AchievementType(Enum):
    """Types of achievements users can earn"""
    UPLOAD = "upload"
    VIEWS = "views"
    COLLABORATION = "collaboration"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    QUALITY = "quality"
    CONSISTENCY = "consistency"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    LEARNING = "learning"
    MILESTONE = "milestone"
    SPECIAL_EVENT = "special_event"
    PLATFORM_SPECIFIC = "platform_specific"
    SOCIAL_IMPACT = "social_impact"
    TECHNICAL = "technical"


class AchievementDifficulty(Enum):
    """Difficulty levels for achievements"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class LeaderboardCategory(Enum):
    """Categories for leaderboards"""
    GLOBAL = "global"
    REGIONAL = "regional"
    GENRE = "genre"
    PLATFORM = "platform"
    COLLABORATION = "collaboration"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    GROWTH = "growth"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    ALL_TIME = "all_time"


class RewardType(Enum):
    """Types of rewards in the system"""
    POINTS = "points"
    PREMIUM_FEATURES = "premium_features"
    REVENUE_SHARE = "revenue_share"
    PLATFORM_PROMOTION = "platform_promotion"
    EXCLUSIVE_ACCESS = "exclusive_access"
    MERCHANDISE = "merchandise"
    CONSULTATION = "consultation"
    COLLABORATION_OPPORTUNITY = "collaboration_opportunity"
    RECOGNITION_BADGE = "recognition_badge"
    SPOTLIGHT_FEATURE = "spotlight_feature"
    MONETIZATION_BOOST = "monetization_boost"
    PRIORITY_SUPPORT = "priority_support"


# ============================================================================
# COLLABORATION MODELS
# ============================================================================

class CollaborationModel(Base):
    """
    Enterprise collaboration model for creator partnership management.
    Comprehensive collaboration system with role management and progress tracking.
    """
    __tablename__ = 'collaborations'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Collaboration details
    collaboration_type = Column(SQLEnum(CollaborationType), nullable=False, index=True)
    status = Column(SQLEnum(CollaborationStatus), nullable=False, default=CollaborationStatus.PROPOSED, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Project details
    project_scope = Column(Text)
    expected_deliverables = Column(JSONB, default=list)
    timeline_weeks = Column(Integer)
    budget_range = Column(String(100))
    revenue_split = Column(JSONB, default=dict)  # {"user_id": percentage}
    
    # Collaboration participants
    participants = Column(JSONB, default=list)  # List of participant user IDs
    participant_roles = Column(JSONB, default=dict)  # {"user_id": "role"}
    max_participants = Column(Integer, default=10)
    current_participant_count = Column(Integer, default=1)
    
    # Requirements & Criteria
    skill_requirements = Column(JSONB, default=list)
    experience_level_required = Column(String(50))
    equipment_requirements = Column(JSONB, default=list)
    location_requirements = Column(String(200))
    language_requirements = Column(JSONB, default=list)
    
    # Matching & Discovery
    tags = Column(JSONB, default=list)
    categories = Column(JSONB, default=list)
    target_audience = Column(JSONB, default=list)
    genre = Column(String(100))
    style = Column(String(100))
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    milestones = Column(JSONB, default=list)
    completed_milestones = Column(Integer, default=0)
    current_phase = Column(String(100))
    phase_deadline = Column(DateTime(timezone=True))
    
    # Content & Results
    content_ids = Column(JSONB, default=list)  # IDs of created content
    final_content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'))
    preview_urls = Column(JSONB, default=list)
    work_in_progress_urls = Column(JSONB, default=list)
    
    # Performance metrics
    total_views = Column(Integer, default=0)
    total_engagement = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    success_score = Column(Float, default=0.0)  # 0-1 success rating
    participant_satisfaction = Column(Float, default=0.0)
    
    # Communication & Coordination
    communication_platform = Column(String(100))  # "discord", "slack", "teams"
    project_channel_id = Column(String(200))
    meeting_schedule = Column(JSONB, default=dict)
    last_activity = Column(DateTime(timezone=True))
    communication_frequency = Column(String(50), default="daily")
    
    # Legal & Rights
    agreement_signed = Column(Boolean, default=False)
    copyright_ownership = Column(String(200), default="shared")
    licensing_terms = Column(Text)
    usage_rights = Column(JSONB, default=dict)
    dispute_resolution = Column(String(200))
    
    # Feedback & Reviews
    feedback_enabled = Column(Boolean, default=True)
    peer_reviews = Column(JSONB, default=list)
    quality_ratings = Column(JSONB, default=dict)
    improvement_suggestions = Column(JSONB, default=list)
    lessons_learned = Column(Text)
    
    # Discovery & Promotion
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    promotion_budget = Column(Float, default=0.0)
    marketing_strategy = Column(JSONB, default=dict)
    social_media_handles = Column(JSONB, default=dict)
    
    # Analytics & Insights
    application_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    collaboration_score = Column(Float, default=0.0)  # Algorithm-calculated score
    market_potential = Column(Float, default=0.0)
    
    # AI recommendations
    ai_match_score = Column(Float, default=0.0)
    ai_recommendations = Column(JSONB, default=list)
    ai_optimization_applied = Column(Boolean, default=False)
    ai_insights = Column(JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    start_date = Column(DateTime(timezone=True))
    target_completion_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    initiator = relationship("UserModel", foreign_keys=[initiator_id], backref="initiated_collaborations")
    final_content = relationship("ContentModel", foreign_keys=[final_content_id], backref="source_collaboration")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_collaboration_type_status', 'collaboration_type', 'status'),
        Index('idx_collaboration_initiator_created', 'initiator_id', 'created_at'),
        Index('idx_collaboration_featured_active', 'is_featured', 'is_active'),
        Index('idx_collaboration_progress_deadline', 'progress_percentage', 'target_completion_date'),
    )
    
    def __repr__(self):
        return f"<CollaborationModel(id={self.id}, type={self.collaboration_type.value}, status={self.status.value})>"


# ============================================================================
# GAMIFICATION MODELS
# ============================================================================

class GamificationModel(Base):
    """
    Enterprise gamification model for user engagement and motivation.
    Comprehensive point system with tracking and analytics.
    """
    __tablename__ = 'gamification'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Point system
    total_points = Column(Integer, default=0, index=True)
    points_this_week = Column(Integer, default=0)
    points_this_month = Column(Integer, default=0)
    points_this_year = Column(Integer, default=0)
    lifetime_points = Column(Integer, default=0)
    
    # Level system
    current_level = Column(Integer, default=1, index=True)
    level_name = Column(String(100), default="Beginner")
    points_for_current_level = Column(Integer, default=0)
    points_for_next_level = Column(Integer, default=100)
    level_progress_percentage = Column(Float, default=0.0)
    
    # Streak tracking
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    streak_type = Column(String(50))  # "daily_upload", "weekly_goal", etc.
    last_streak_activity = Column(DateTime(timezone=True))
    
    # Achievement tracking
    total_achievements = Column(Integer, default=0)
    achievements_this_month = Column(Integer, default=0)
    rare_achievements = Column(Integer, default=0)
    achievement_points = Column(Integer, default=0)
    
    # Badge collection
    total_badges = Column(Integer, default=0)
    bronze_badges = Column(Integer, default=0)
    silver_badges = Column(Integer, default=0)
    gold_badges = Column(Integer, default=0)
    platinum_badges = Column(Integer, default=0)
    diamond_badges = Column(Integer, default=0)
    legendary_badges = Column(Integer, default=0)
    
    # Competition & Rankings
    global_rank = Column(Integer, index=True)
    regional_rank = Column(Integer)
    genre_rank = Column(Integer)
    collaboration_rank = Column(Integer)
    monthly_rank = Column(Integer)
    weekly_rank = Column(Integer)
    
    # Activity metrics
    daily_activity_score = Column(Float, default=0.0)
    weekly_activity_score = Column(Float, default=0.0)
    monthly_activity_score = Column(Float, default=0.0)
    engagement_multiplier = Column(Float, default=1.0)
    quality_bonus = Column(Float, default=1.0)
    
    # Rewards & Benefits
    total_rewards_earned = Column(Integer, default=0)
    rewards_this_month = Column(Integer, default=0)
    reward_points_balance = Column(Integer, default=0)
    premium_benefits_unlocked = Column(JSONB, default=list)
    exclusive_features_unlocked = Column(JSONB, default=list)
    
    # Challenge participation
    active_challenges = Column(Integer, default=0)
    completed_challenges = Column(Integer, default=0)
    challenge_success_rate = Column(Float, default=0.0)
    challenge_points_earned = Column(Integer, default=0)
    
    # Social gamification
    referral_points = Column(Integer, default=0)
    collaboration_bonus = Column(Integer, default=0)
    community_contribution_score = Column(Float, default=0.0)
    mentorship_points = Column(Integer, default=0)
    helping_others_score = Column(Float, default=0.0)
    
    # Seasonal & Special events
    seasonal_points = Column(Integer, default=0)
    event_participation_count = Column(Integer, default=0)
    special_event_achievements = Column(Integer, default=0)
    holiday_bonus_points = Column(Integer, default=0)
    
    # Performance bonuses
    consistency_bonus = Column(Float, default=1.0)
    innovation_bonus = Column(Float, default=1.0)
    quality_bonus_multiplier = Column(Float, default=1.0)
    speed_bonus = Column(Float, default=1.0)
    collaboration_bonus_multiplier = Column(Float, default=1.0)
    
    # Analytics & Insights
    engagement_trend = Column(String(20), default="stable")  # "increasing", "decreasing", "stable"
    performance_trend = Column(String(20), default="stable")
    growth_rate = Column(Float, default=0.0)
    predicted_next_level_date = Column(DateTime(timezone=True))
    motivation_score = Column(Float, default=0.5)  # 0-1 motivation level
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_activity_date = Column(DateTime(timezone=True))
    level_achieved_date = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True)
    is_leaderboard_visible = Column(Boolean, default=True)
    is_achievement_notifications_enabled = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    user = relationship("UserModel", backref="gamification_profile")
    achievements = relationship("AchievementModel", back_populates="user_gamification", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_gamification_user_points', 'user_id', 'total_points'),
        Index('idx_gamification_level_rank', 'current_level', 'global_rank'),
        Index('idx_gamification_active_updated', 'is_active', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<GamificationModel(id={self.id}, user_id={self.user_id}, level={self.current_level}, points={self.total_points})>"


class AchievementModel(Base):
    """
    Achievement tracking model for individual achievement records.
    Detailed achievement system with progress tracking and rewards.
    """
    __tablename__ = 'achievements'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    gamification_id = Column(UUID(as_uuid=True), ForeignKey('gamification.id'), nullable=False, index=True)
    
    # Achievement details
    achievement_type = Column(SQLEnum(AchievementType), nullable=False, index=True)
    difficulty = Column(SQLEnum(AchievementDifficulty), nullable=False, index=True)
    achievement_name = Column(String(200), nullable=False)
    achievement_description = Column(Text)
    
    # Achievement configuration
    achievement_key = Column(String(100), nullable=False, index=True)  # Unique identifier
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    icon_url = Column(String(500))
    badge_image_url = Column(String(500))
    
    # Progress tracking
    target_value = Column(Float, nullable=False)  # Target to achieve
    current_value = Column(Float, default=0.0)  # Current progress
    progress_percentage = Column(Float, default=0.0)  # 0-100
    is_completed = Column(Boolean, default=False, index=True)
    completion_date = Column(DateTime(timezone=True))
    
    # Reward information
    points_reward = Column(Integer, default=0)
    badge_reward = Column(String(100))
    special_reward = Column(String(200))
    reward_claimed = Column(Boolean, default=False)
    reward_claim_date = Column(DateTime(timezone=True))
    
    # Achievement rarity & Statistics
    rarity_score = Column(Float, default=0.5)  # 0-1, how rare the achievement is
    global_completion_rate = Column(Float, default=0.0)  # % of users who completed
    estimated_difficulty = Column(Float, default=0.5)  # AI-estimated difficulty
    time_to_complete_days = Column(Integer)  # Average time to complete
    
    # Context & Conditions
    unlock_conditions = Column(JSONB, default=dict)  # Conditions to unlock
    prerequisite_achievements = Column(JSONB, default=list)  # Required achievements
    context_data = Column(JSONB, default=dict)  # Context when achieved
    achievement_method = Column(String(200))  # How it was achieved
    
    # Social features
    is_shareable = Column(Boolean, default=True)
    shared_count = Column(Integer, default=0)
    likes_received = Column(Integer, default=0)
    comments_received = Column(Integer, default=0)
    social_impact_score = Column(Float, default=0.0)
    
    # Verification & Validation
    verification_required = Column(Boolean, default=False)
    verification_status = Column(String(50), default="auto_verified")
    verification_evidence = Column(JSONB, default=dict)
    verified_by = Column(String(200))
    verification_date = Column(DateTime(timezone=True))
    
    # Temporal information
    is_time_limited = Column(Boolean, default=False)
    available_from = Column(DateTime(timezone=True))
    available_until = Column(DateTime(timezone=True))
    seasonal_event = Column(String(100))
    special_occasion = Column(String(100))
    
    # Performance impact
    skill_improvement = Column(JSONB, default=dict)  # Skills improved by this achievement
    platform_benefits = Column(JSONB, default=list)  # Platform benefits unlocked
    collaboration_benefits = Column(JSONB, default=list)  # Collaboration benefits
    monetization_benefits = Column(JSONB, default=list)  # Monetization benefits
    
    # Analytics
    attempt_count = Column(Integer, default=0)  # Times user attempted
    help_requests = Column(Integer, default=0)  # Times user requested help
    hints_used = Column(Integer, default=0)  # Hints used
    community_support_received = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    first_progress_at = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)  # Hidden until unlocked
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    user = relationship("UserModel", backref="achievements")
    user_gamification = relationship("GamificationModel", back_populates="achievements")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_achievement_user_type', 'user_id', 'achievement_type'),
        Index('idx_achievement_completed_difficulty', 'is_completed', 'difficulty'),
        Index('idx_achievement_key_category', 'achievement_key', 'category'),
        Index('idx_achievement_rarity_featured', 'rarity_score', 'is_featured'),
    )
    
    def __repr__(self):
        return f"<AchievementModel(id={self.id}, name='{self.achievement_name}', completed={self.is_completed})>"


class LeaderboardModel(Base):
    """
    Leaderboard model for competitive rankings and recognition.
    Multi-category leaderboards with time-based rankings.
    """
    __tablename__ = 'leaderboards'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Leaderboard classification
    category = Column(SQLEnum(LeaderboardCategory), nullable=False, index=True)
    leaderboard_name = Column(String(200), nullable=False)
    ranking_metric = Column(String(100), nullable=False)  # What is being ranked
    
    # Ranking information
    current_rank = Column(Integer, nullable=False, index=True)
    previous_rank = Column(Integer)
    best_rank = Column(Integer)
    rank_change = Column(Integer, default=0)  # +/- change from previous period
    ranking_score = Column(Float, nullable=False)  # Score used for ranking
    
    # Time period
    period_type = Column(String(20), nullable=False)  # "weekly", "monthly", "annual", etc.
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    is_current_period = Column(Boolean, default=True, index=True)
    
    # Context & Filters
    region = Column(String(10))  # ISO country code
    genre = Column(String(100))
    platform = Column(String(100))
    age_group = Column(String(20))
    user_tier = Column(String(50))
    
    # Performance metrics
    percentile = Column(Float)  # 0-100 percentile
    z_score = Column(Float)  # Standard deviations from mean
    total_participants = Column(Integer)
    active_participants = Column(Integer)
    competition_level = Column(String(20), default="medium")  # how competitive
    
    # Achievement & Recognition
    position_badge = Column(String(100))  # "top_1", "top_10", "top_100"
    special_recognition = Column(String(200))
    featured_achievement = Column(Boolean, default=False)
    hall_of_fame = Column(Boolean, default=False)
    
    # Rewards & Benefits
    reward_earned = Column(String(200))
    reward_type = Column(SQLEnum(RewardType))
    reward_value = Column(Float)
    reward_claimed = Column(Boolean, default=False)
    reward_expiry = Column(DateTime(timezone=True))
    
    # Social features
    is_public = Column(Boolean, default=True)
    celebration_shared = Column(Boolean, default=False)
    community_congratulations = Column(Integer, default=0)
    social_mentions = Column(Integer, default=0)
    
    # Historical tracking
    rank_history = Column(JSONB, default=list)  # Historical rank data
    score_history = Column(JSONB, default=list)  # Historical score data
    trend_direction = Column(String(20))  # "rising", "falling", "stable"
    momentum_score = Column(Float, default=0.0)  # Rate of change
    
    # Competition analysis
    gap_to_higher_rank = Column(Float)  # Points/score gap to next rank
    gap_from_lower_rank = Column(Float)  # Points/score gap from lower rank
    improvement_needed = Column(Float)  # Estimated improvement needed to rank up
    probability_rank_up = Column(Float)  # AI-predicted probability
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    rank_achieved_at = Column(DateTime(timezone=True))
    
    # System flags
    is_verified = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    user = relationship("UserModel", backref="leaderboard_entries")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_leaderboard_category_rank', 'category', 'current_rank'),
        Index('idx_leaderboard_user_period', 'user_id', 'period_type'),
        Index('idx_leaderboard_current_score', 'is_current_period', 'ranking_score'),
        Index('idx_leaderboard_region_genre', 'region', 'genre'),
    )
    
    def __repr__(self):
        return f"<LeaderboardModel(id={self.id}, category={self.category.value}, rank={self.current_rank})>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_collaboration_example(initiator_id: str, 
                                collaboration_type: CollaborationType = CollaborationType.MUSIC) -> CollaborationModel:
    """Create example collaboration for testing and development"""
    return CollaborationModel(
        initiator_id=initiator_id,
        collaboration_type=collaboration_type,
        title=f"Sample {collaboration_type.value.title()} Collaboration",
        description="This is a sample collaboration for testing purposes",
        timeline_weeks=4,
        max_participants=3,
        skill_requirements=["beginner", "intermediate"],
        tags=["sample", "test", collaboration_type.value]
    )


def create_achievement_example(user_id: str, gamification_id: str,
                             achievement_type: AchievementType = AchievementType.UPLOAD) -> AchievementModel:
    """Create example achievement for testing and development"""
    return AchievementModel(
        user_id=user_id,
        gamification_id=gamification_id,
        achievement_type=achievement_type,
        difficulty=AchievementDifficulty.BRONZE,
        achievement_name=f"First {achievement_type.value.title()}",
        achievement_description=f"Complete your first {achievement_type.value}",
        achievement_key=f"first_{achievement_type.value}",
        target_value=1.0,
        points_reward=100
    )


def calculate_collaboration_match_score(user_skills: List[str], required_skills: List[str],
                                      user_experience: str, required_experience: str) -> float:
    """Calculate match score between user and collaboration requirements"""
    skill_match = len(set(user_skills) & set(required_skills)) / max(len(required_skills), 1)
    
    experience_levels = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
    user_exp_level = experience_levels.get(user_experience, 1)
    req_exp_level = experience_levels.get(required_experience, 1)
    
    experience_match = 1.0 if user_exp_level >= req_exp_level else user_exp_level / req_exp_level
    
    return (skill_match * 0.7) + (experience_match * 0.3)


def calculate_gamification_level(total_points: int) -> tuple:
    """Calculate level and progress based on total points"""
    # Level progression: Level 1 = 0-99, Level 2 = 100-299, Level 3 = 300-599, etc.
    level = 1
    points_needed = 100
    cumulative_points = 0
    
    while total_points >= cumulative_points + points_needed:
        cumulative_points += points_needed
        level += 1
        points_needed = int(points_needed * 1.5)  # Exponential growth
    
    points_for_current_level = total_points - cumulative_points
    points_for_next_level = points_needed
    progress_percentage = (points_for_current_level / points_for_next_level) * 100
    
    return level, points_for_current_level, points_for_next_level, progress_percentage


def generate_achievement_key(achievement_type: AchievementType, 
                           category: str, difficulty: AchievementDifficulty) -> str:
    """Generate unique achievement key"""
    return f"{achievement_type.value}_{category}_{difficulty.value}_{uuid.uuid4().hex[:8]}"


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Models
    'CollaborationModel', 'GamificationModel', 'AchievementModel', 'LeaderboardModel',
    
    # Collaboration Enums
    'CollaborationType', 'CollaborationStatus', 'CollaborationRole',
    
    # Gamification Enums
    'GamificationElement', 'AchievementType', 'AchievementDifficulty', 'LeaderboardCategory', 'RewardType',
    
    # Utility Functions
    'create_collaboration_example', 'create_achievement_example',
    'calculate_collaboration_match_score', 'calculate_gamification_level', 'generate_achievement_key'
]