"""🎮 Gamification & Engagement Database Module - Advanced User Engagement System
==================================================================================
Module: backend/database/gamification_engagement.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Consolidated Gamification & Engagement Database - Ultra Enterprise Production-Ready
Responsibility: Advanced gamification, achievements, challenges, rewards, social interactions, and loyalty programs
====================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This consolidated module provides comprehensive database schemas and operations for:
- Advanced gamification system with multi-tier achievements
- Dynamic challenges and competitions for creators
- Automated reward distribution and loyalty programs
- Social interactions and community engagement
- Real-time leaderboards and ranking systems
- Behavioral analytics and engagement optimization

BUSINESS LOGIC INTEGRATION:
User Activity → Gamification Rules → Achievement Unlock → Reward Distribution → Social Sharing → Engagement Loop
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid
import logging

logger = logging.getLogger(__name__)

# Create independent declarative base to avoid conflicts
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# ================================
# ENUMERATIONS
# ================================

class AchievementType(Enum):
    """Achievement types and categories."""
    MILESTONE = "milestone"
    PROGRESSION = "progression"
    SOCIAL = "social"
    CREATIVE = "creative"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    ENGAGEMENT = "engagement"
    SPECIAL_EVENT = "special_event"
    SEASONAL = "seasonal"
    EXCLUSIVE = "exclusive"


class AchievementRarity(Enum):
    """Achievement rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class ChallengeType(Enum):
    """Challenge and competition types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    COMMUNITY = "community"
    SOLO = "solo"
    TEAM = "team"
    TOURNAMENT = "tournament"
    SPECIAL_EVENT = "special_event"


class ChallengeStatus(Enum):
    """Challenge participation status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CLAIMED = "claimed"


class RewardType(Enum):
    """Reward types for achievements and challenges."""
    POINTS = "points"
    BADGES = "badges"
    CURRENCY = "currency"
    PREMIUM_TIME = "premium_time"
    FEATURES = "features"
    DISCOUNTS = "discounts"
    EXCLUSIVE_CONTENT = "exclusive_content"
    MERCHANDISE = "merchandise"
    EXPERIENCE_BOOST = "experience_boost"
    PRIORITY_SUPPORT = "priority_support"


class InteractionType(Enum):
    """Social interaction types."""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    FOLLOW = "follow"
    COLLABORATE = "collaborate"
    MENTION = "mention"
    TAG = "tag"
    REMIX = "remix"
    FEATURE = "feature"
    SUPPORT = "support"


class LeaderboardType(Enum):
    """Leaderboard categories."""
    OVERALL_POINTS = "overall_points"
    MONTHLY_REVENUE = "monthly_revenue"
    COLLABORATIONS = "collaborations"
    CONTENT_CREATED = "content_created"
    SOCIAL_ENGAGEMENT = "social_engagement"
    CHALLENGE_WINS = "challenge_wins"
    STREAK_DAYS = "streak_days"
    SKILL_LEVEL = "skill_level"


# ================================
# GAMIFICATION CORE SCHEMAS
# ================================

class UserGamification(Base):
    """Core user gamification profile and statistics."""
    __tablename__ = 'user_gamifications'
    __table_args__ = (
        Index('idx_user_gamification_user', 'user_id'),
        Index('idx_user_gamification_level', 'current_level'),
        Index('idx_user_gamification_points', 'total_points'),
        Index('idx_user_gamification_rank', 'global_rank'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Core progression
    current_level = Column(Integer, default=1)
    current_experience = Column(BigInteger, default=0)
    experience_to_next_level = Column(BigInteger, default=100)
    total_points = Column(BigInteger, default=0)
    lifetime_points = Column(BigInteger, default=0)
    
    # Rankings
    global_rank = Column(Integer, nullable=True)
    category_ranks = Column(JSONB, default={})  # Different category rankings
    rank_history = Column(JSONB, default=[])
    
    # Streaks and consistency
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    consecutive_login_days = Column(Integer, default=0)
    
    # Achievement progress
    total_achievements_unlocked = Column(Integer, default=0)
    rare_achievements_count = Column(Integer, default=0)
    achievement_points = Column(BigInteger, default=0)
    
    # Challenge participation
    challenges_completed = Column(Integer, default=0)
    challenges_won = Column(Integer, default=0)
    challenge_points = Column(BigInteger, default=0)
    current_challenges = Column(ARRAY(UUID), default=[])
    
    # Social engagement
    social_influence_score = Column(Float, default=0.0)
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    total_likes_received = Column(BigInteger, default=0)
    total_shares_received = Column(BigInteger, default=0)
    
    # Rewards and benefits
    reward_points_balance = Column(BigInteger, default=0)
    premium_benefits_active = Column(Boolean, default=False)
    premium_expires_at = Column(DateTime(timezone=True), nullable=True)
    special_badges = Column(ARRAY(String), default=[])
    
    # Behavioral patterns
    activity_patterns = Column(JSONB, default={})
    engagement_preferences = Column(JSONB, default={})
    motivation_factors = Column(JSONB, default={})
    
    # Customization and preferences
    display_preferences = Column(JSONB, default={})
    notification_preferences = Column(JSONB, default={})
    privacy_settings = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_level_up_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    achievements = relationship("UserAchievement", back_populates="user_gamification")
    challenge_participations = relationship("ChallengeParticipation", back_populates="user_gamification")
    reward_claims = relationship("RewardClaim", back_populates="user_gamification")
    social_interactions_given = relationship("SocialInteraction", foreign_keys="SocialInteraction.user_id", back_populates="user")
    social_interactions_received = relationship("SocialInteraction", foreign_keys="SocialInteraction.target_user_id", back_populates="target_user")


# ================================
# ACHIEVEMENT SYSTEM SCHEMAS
# ================================

class Achievement(Base):
    """Achievement definitions and configurations."""
    __tablename__ = 'achievements'
    __table_args__ = (
        Index('idx_achievement_type', 'achievement_type'),
        Index('idx_achievement_rarity', 'rarity'),
        Index('idx_achievement_category', 'category'),
        Index('idx_achievement_active', 'is_active'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    detailed_description = Column(Text, nullable=True)
    
    # Classification
    achievement_type = Column(SQLEnum(AchievementType), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    rarity = Column(SQLEnum(AchievementRarity), default=AchievementRarity.COMMON)
    
    # Visual elements
    icon_url = Column(String(500), nullable=True)
    badge_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    color_scheme = Column(JSONB, default={})
    
    # Requirements and conditions
    unlock_conditions = Column(JSONB, nullable=False)
    prerequisite_achievements = Column(ARRAY(UUID), default=[])
    minimum_level_required = Column(Integer, default=1)
    time_limited = Column(Boolean, default=False)
    available_from = Column(DateTime(timezone=True), nullable=True)
    available_until = Column(DateTime(timezone=True), nullable=True)
    
    # Rewards
    reward_points = Column(Integer, default=0)
    reward_experience = Column(Integer, default=0)
    special_rewards = Column(JSONB, default=[])
    
    # Progress tracking
    is_progressive = Column(Boolean, default=False)
    progress_steps = Column(JSONB, default=[])
    max_progress = Column(Integer, default=1)
    
    # Difficulty and effort
    difficulty_level = Column(Integer, default=1)  # 1-10
    estimated_time_hours = Column(Float, nullable=True)
    skill_requirements = Column(ARRAY(String), default=[])
    
    # Metadata
    tags = Column(ARRAY(String), default=[])
    hidden_until_unlocked = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    unlock_order = Column(Integer, nullable=True)
    
    # Statistics
    total_unlocks = Column(BigInteger, default=0)
    unlock_rate_percentage = Column(Float, nullable=True)
    average_unlock_time_hours = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    """User achievement unlocks and progress tracking."""
    __tablename__ = 'user_achievements'
    __table_args__ = (
        Index('idx_user_achievement_user', 'user_gamification_id'),
        Index('idx_user_achievement_achievement', 'achievement_id'),
        Index('idx_user_achievement_unlocked', 'unlocked_at'),
        Index('idx_user_achievement_progress', 'current_progress'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_gamification_id = Column(UUID(as_uuid=True), ForeignKey('user_gamifications.id'), nullable=False)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey('achievements.id'), nullable=False)
    
    # Progress tracking
    current_progress = Column(Integer, default=0)
    max_progress = Column(Integer, default=1)
    progress_percentage = Column(Float, default=0.0)
    is_unlocked = Column(Boolean, default=False)
    
    # Progress history
    progress_history = Column(JSONB, default=[])
    milestone_checkpoints = Column(JSONB, default=[])
    
    # Unlock details
    unlock_method = Column(String(100), nullable=True)
    unlock_context = Column(JSONB, default={})
    time_to_unlock_hours = Column(Float, nullable=True)
    
    # Reward claiming
    rewards_claimed = Column(Boolean, default=False)
    rewards_claimed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Social sharing
    shared_on_social = Column(Boolean, default=False)
    shared_at = Column(DateTime(timezone=True), nullable=True)
    social_engagement_count = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user_gamification = relationship("UserGamification", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")


# ================================
# CHALLENGE SYSTEM SCHEMAS
# ================================

class Challenge(Base):
    """Challenge and competition definitions."""
    __tablename__ = 'challenges'
    __table_args__ = (
        Index('idx_challenge_type', 'challenge_type'),
        Index('idx_challenge_status', 'status'),
        Index('idx_challenge_start', 'start_date'),
        Index('idx_challenge_end', 'end_date'),
        Index('idx_challenge_difficulty', 'difficulty_level'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    detailed_rules = Column(Text, nullable=True)
    
    # Challenge classification
    challenge_type = Column(SQLEnum(ChallengeType), nullable=False)
    category = Column(String(100), nullable=False)
    difficulty_level = Column(Integer, default=1)  # 1-10
    
    # Timing
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Integer, nullable=True)
    timezone = Column(String(50), default='UTC')
    
    # Participation
    max_participants = Column(Integer, nullable=True)
    current_participants = Column(Integer, default=0)
    entry_requirements = Column(JSONB, default={})
    entry_fee = Column(Numeric(8, 2), default=0)
    
    # Challenge mechanics
    objectives = Column(JSONB, nullable=False)
    scoring_system = Column(JSONB, nullable=False)
    success_criteria = Column(JSONB, nullable=False)
    team_based = Column(Boolean, default=False)
    max_team_size = Column(Integer, default=1)
    
    # Rewards and prizes
    reward_pool = Column(JSONB, default={})
    winner_rewards = Column(JSONB, default={})
    participation_rewards = Column(JSONB, default={})
    milestone_rewards = Column(JSONB, default={})
    
    # Status and visibility
    status = Column(String(50), default='draft')  # draft, active, completed, cancelled
    is_public = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)
    
    # Visual elements
    banner_url = Column(String(500), nullable=True)
    icon_url = Column(String(500), nullable=True)
    theme_colors = Column(JSONB, default={})
    
    # Analytics
    total_participation_count = Column(BigInteger, default=0)
    completion_rate_percentage = Column(Float, nullable=True)
    average_score = Column(Float, nullable=True)
    engagement_metrics = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participations = relationship("ChallengeParticipation", back_populates="challenge")


class ChallengeParticipation(Base):
    """User participation in challenges and competitions."""
    __tablename__ = 'challenge_participations'
    __table_args__ = (
        Index('idx_challenge_participation_user', 'user_gamification_id'),
        Index('idx_challenge_participation_challenge', 'challenge_id'),
        Index('idx_challenge_participation_status', 'participation_status'),
        Index('idx_challenge_participation_score', 'current_score'),
        Index('idx_challenge_participation_rank', 'current_rank'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_gamification_id = Column(UUID(as_uuid=True), ForeignKey('user_gamifications.id'), nullable=False)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey('challenges.id'), nullable=False)
    
    # Participation details
    participation_status = Column(SQLEnum(ChallengeStatus), default=ChallengeStatus.NOT_STARTED)
    team_id = Column(UUID(as_uuid=True), nullable=True)
    team_role = Column(String(50), nullable=True)
    
    # Progress and scoring
    current_score = Column(Float, default=0.0)
    max_possible_score = Column(Float, nullable=True)
    progress_percentage = Column(Float, default=0.0)
    objectives_completed = Column(JSONB, default={})
    
    # Ranking
    current_rank = Column(Integer, nullable=True)
    best_rank = Column(Integer, nullable=True)
    rank_history = Column(JSONB, default=[])
    
    # Performance tracking
    submission_data = Column(JSONB, default={})
    performance_metrics = Column(JSONB, default={})
    completion_evidence = Column(JSONB, default={})
    
    # Timing
    time_spent_minutes = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    
    # Rewards
    rewards_earned = Column(JSONB, default={})
    rewards_claimed = Column(Boolean, default=False)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user_gamification = relationship("UserGamification", back_populates="challenge_participations")
    challenge = relationship("Challenge", back_populates="participations")


# ================================
# REWARD SYSTEM SCHEMAS
# ================================

class Reward(Base):
    """Reward definitions and configurations."""
    __tablename__ = 'rewards'
    __table_args__ = (
        Index('idx_reward_type', 'reward_type'),
        Index('idx_reward_category', 'category'),
        Index('idx_reward_cost', 'cost_points'),
        Index('idx_reward_active', 'is_active'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Classification
    reward_type = Column(SQLEnum(RewardType), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    
    # Cost and availability
    cost_points = Column(Integer, nullable=False)
    cost_currency = Column(Numeric(8, 2), nullable=True)
    currency_code = Column(String(3), nullable=True)
    
    # Reward content
    reward_data = Column(JSONB, nullable=False)
    delivery_method = Column(String(50), nullable=False)  # instant, manual, scheduled
    
    # Limitations and conditions
    max_claims_per_user = Column(Integer, nullable=True)
    total_available_quantity = Column(Integer, nullable=True)
    remaining_quantity = Column(Integer, nullable=True)
    minimum_level_required = Column(Integer, default=1)
    
    # Timing
    available_from = Column(DateTime(timezone=True), nullable=True)
    available_until = Column(DateTime(timezone=True), nullable=True)
    expiry_duration_days = Column(Integer, nullable=True)
    
    # Visual elements
    icon_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Statistics
    total_claims = Column(BigInteger, default=0)
    popularity_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claims = relationship("RewardClaim", back_populates="reward")


class RewardClaim(Base):
    """User reward claims and redemptions."""
    __tablename__ = 'reward_claims'
    __table_args__ = (
        Index('idx_reward_claim_user', 'user_gamification_id'),
        Index('idx_reward_claim_reward', 'reward_id'),
        Index('idx_reward_claim_status', 'claim_status'),
        Index('idx_reward_claim_claimed', 'claimed_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_gamification_id = Column(UUID(as_uuid=True), ForeignKey('user_gamifications.id'), nullable=False)
    reward_id = Column(UUID(as_uuid=True), ForeignKey('rewards.id'), nullable=False)
    
    # Claim details
    claim_status = Column(String(50), default='pending')  # pending, delivered, expired, cancelled
    points_spent = Column(Integer, nullable=False)
    currency_spent = Column(Numeric(8, 2), nullable=True)
    
    # Delivery
    delivery_data = Column(JSONB, default={})
    delivery_reference = Column(String(255), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage and expiry
    used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Feedback
    satisfaction_rating = Column(Float, nullable=True)  # 1.0-5.0
    feedback_text = Column(Text, nullable=True)
    
    # Timestamps
    claimed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user_gamification = relationship("UserGamification", back_populates="reward_claims")
    reward = relationship("Reward", back_populates="claims")


# ================================
# SOCIAL INTERACTION SCHEMAS
# ================================

class SocialInteraction(Base):
    """Social interactions and engagement tracking."""
    __tablename__ = 'social_interactions'
    __table_args__ = (
        Index('idx_social_interaction_user', 'user_id'),
        Index('idx_social_interaction_target', 'target_user_id'),
        Index('idx_social_interaction_type', 'interaction_type'),
        Index('idx_social_interaction_content', 'content_id'),
        Index('idx_social_interaction_created', 'created_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_gamifications.user_id'), nullable=False)
    target_user_id = Column(UUID(as_uuid=True), ForeignKey('user_gamifications.user_id'), nullable=True)
    
    # Interaction details
    interaction_type = Column(SQLEnum(InteractionType), nullable=False)
    content_id = Column(String(255), nullable=True)
    content_type = Column(String(50), nullable=True)
    
    # Interaction data
    interaction_data = Column(JSONB, default={})
    message = Column(Text, nullable=True)
    interaction_metadata = Column(JSONB, default={})
    
    # Context
    platform = Column(String(50), nullable=True)
    source = Column(String(100), nullable=True)
    context = Column(JSONB, default={})
    
    # Engagement metrics
    engagement_score = Column(Float, nullable=True)
    viral_factor = Column(Float, nullable=True)
    reach_count = Column(Integer, default=0)
    
    # Response tracking
    responses = Column(JSONB, default=[])
    response_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserGamification", foreign_keys=[user_id], back_populates="social_interactions_given")
    target_user = relationship("UserGamification", foreign_keys=[target_user_id], back_populates="social_interactions_received")


# ================================
# LEADERBOARD SCHEMAS
# ================================

class Leaderboard(Base):
    """Leaderboard configurations and rankings."""
    __tablename__ = 'leaderboards'
    __table_args__ = (
        Index('idx_leaderboard_type', 'leaderboard_type'),
        Index('idx_leaderboard_category', 'category'),
        Index('idx_leaderboard_period', 'time_period'),
        Index('idx_leaderboard_updated', 'last_updated'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Leaderboard definition
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    leaderboard_type = Column(SQLEnum(LeaderboardType), nullable=False)
    category = Column(String(100), nullable=False)
    
    # Ranking configuration
    ranking_criteria = Column(JSONB, nullable=False)
    scoring_formula = Column(Text, nullable=False)
    update_frequency = Column(String(50), default='daily')  # real_time, hourly, daily, weekly
    
    # Time period
    time_period = Column(String(50), nullable=False)  # all_time, yearly, monthly, weekly, daily
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Display settings
    max_displayed_ranks = Column(Integer, default=100)
    show_user_rank = Column(Boolean, default=True)
    show_scores = Column(Boolean, default=True)
    
    # Visibility and access
    is_public = Column(Boolean, default=True)
    access_level = Column(String(50), default='public')  # public, premium, private
    
    # Visual elements
    icon_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    theme_colors = Column(JSONB, default={})
    
    # Statistics
    total_participants = Column(Integer, default=0)
    active_participants = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rankings = relationship("LeaderboardRanking", back_populates="leaderboard")


class LeaderboardRanking(Base):
    """Individual user rankings on leaderboards."""
    __tablename__ = 'leaderboard_rankings'
    __table_args__ = (
        Index('idx_leaderboard_ranking_board', 'leaderboard_id'),
        Index('idx_leaderboard_ranking_user', 'user_id'),
        Index('idx_leaderboard_ranking_rank', 'current_rank'),
        Index('idx_leaderboard_ranking_score', 'score'),
        Index('idx_leaderboard_ranking_updated', 'last_updated'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    leaderboard_id = Column(UUID(as_uuid=True), ForeignKey('leaderboards.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Ranking details
    current_rank = Column(Integer, nullable=False)
    previous_rank = Column(Integer, nullable=True)
    best_rank = Column(Integer, nullable=True)
    rank_change = Column(Integer, default=0)
    
    # Scoring
    score = Column(Float, nullable=False)
    previous_score = Column(Float, nullable=True)
    score_change = Column(Float, default=0.0)
    
    # Additional metrics
    detailed_metrics = Column(JSONB, default={})
    performance_data = Column(JSONB, default={})
    
    # Trends
    trend_direction = Column(String(20), nullable=True)  # up, down, stable
    momentum_score = Column(Float, nullable=True)
    
    # Achievements on leaderboard
    rank_achievements = Column(ARRAY(String), default=[])
    milestone_reached = Column(JSONB, default=[])
    
    # Timestamps
    first_appeared = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leaderboard = relationship("Leaderboard", back_populates="rankings")


# ================================
# LOYALTY PROGRAM SCHEMAS
# ================================

class LoyaltyProgram(Base):
    """Loyalty programs and tier-based benefits."""
    __tablename__ = 'loyalty_programs'
    __table_args__ = (
        Index('idx_loyalty_program_user', 'user_id'),
        Index('idx_loyalty_program_tier', 'current_tier'),
        Index('idx_loyalty_program_points', 'loyalty_points'),
        Index('idx_loyalty_program_status', 'status'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Program membership
    program_name = Column(String(255), default='Ainflue Creators')
    membership_number = Column(String(100), nullable=True, unique=True)
    status = Column(String(50), default='active')  # active, inactive, suspended, terminated
    
    # Tier system
    current_tier = Column(String(50), default='Bronze')
    tier_level = Column(Integer, default=1)
    points_to_next_tier = Column(Integer, nullable=True)
    tier_benefits = Column(JSONB, default={})
    
    # Points and rewards
    loyalty_points = Column(BigInteger, default=0)
    lifetime_points_earned = Column(BigInteger, default=0)
    points_redeemed = Column(BigInteger, default=0)
    points_expired = Column(BigInteger, default=0)
    
    # Tier history
    tier_history = Column(JSONB, default=[])
    tier_upgrade_date = Column(DateTime(timezone=True), nullable=True)
    tier_downgrade_protection_until = Column(DateTime(timezone=True), nullable=True)
    
    # Benefits and perks
    active_benefits = Column(JSONB, default=[])
    exclusive_offers = Column(JSONB, default=[])
    priority_access = Column(Boolean, default=False)
    dedicated_support = Column(Boolean, default=False)
    
    # Spending and activity
    total_spending = Column(Numeric(12, 2), default=0)
    average_monthly_activity = Column(Float, nullable=True)
    last_earning_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Referrals and social
    referral_code = Column(String(50), nullable=True, unique=True)
    successful_referrals = Column(Integer, default=0)
    referral_bonus_points = Column(BigInteger, default=0)
    
    # Program metrics
    program_satisfaction_score = Column(Float, nullable=True)
    net_promoter_score = Column(Integer, nullable=True)
    
    # Special recognition
    vip_status = Column(Boolean, default=False)
    anniversary_date = Column(DateTime(timezone=True), nullable=True)
    special_recognition = Column(JSONB, default=[])
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)


# ================================
# EXPORT FUNCTIONS
# ================================

def get_gamification_engagement_models() -> None:
    """Get all gamification and engagement models."""
    return [
        UserGamification,
        Achievement,
        UserAchievement,
        Challenge,
        ChallengeParticipation,
        Reward,
        RewardClaim,
        SocialInteraction,
        Leaderboard,
        LeaderboardRanking,
        LoyaltyProgram,
    ]


def create_gamification_engagement_tables(engine) -> None:
    """Create all gamification and engagement tables."""
    try:
        Base.metadata.create_all(engine, tables=[model.__table__ for model in get_gamification_engagement_models()])
        logger.info("Successfully created gamification and engagement tables")
        return True
    except Exception as e:
        logger.error(f"Failed to create gamification and engagement tables: {str(e)}")
        return False


# Export all models and functions
__all__ = [
    # Enums
    'AchievementType', 'AchievementRarity', 'ChallengeType', 'ChallengeStatus', 
    'RewardType', 'InteractionType', 'LeaderboardType',
    
    # Models
    'UserGamification', 'Achievement', 'UserAchievement', 'Challenge', 'ChallengeParticipation',
    'Reward', 'RewardClaim', 'SocialInteraction', 'Leaderboard', 'LeaderboardRanking',
    'LoyaltyProgram',
    
    # Functions
    'get_gamification_engagement_models', 'create_gamification_engagement_tables'
]