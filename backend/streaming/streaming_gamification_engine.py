"""Streaming Gamification Engine - Live Engagement and Achievement System
======================================================================

Enterprise-grade streaming gamification engine providing real-time engagement
mechanics, achievement systems, interactive challenges, leaderboards, and
comprehensive audience interaction optimization for streaming platforms.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/streaming/streaming_gamification_engine.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

BUSINESS LOGIC INTEGRATION:
Engagement Tracking → Achievement Processing → Challenge Management → Reward Distribution → Analytics
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()
logger = logging.getLogger(__name__)


class EngagementType(str, Enum):
    """Types of audience engagement."""
    CHAT_MESSAGE = "chat_message"
    REACTION = "reaction"
    DONATION = "donation"
    SUPER_CHAT = "super_chat"
    SUBSCRIPTION = "subscription"
    SHARE = "share"
    LIKE = "like"
    FOLLOW = "follow"
    POLL_VOTE = "poll_vote"
    CHALLENGE_PARTICIPATION = "challenge_participation"


class AchievementType(str, Enum):
    """Types of achievements."""
    MILESTONE = "milestone"
    STREAK = "streak"
    FIRST_TIME = "first_time"
    COMMUNITY = "community"
    CREATOR_SPECIFIC = "creator_specific"
    PLATFORM_WIDE = "platform_wide"
    SPECIAL_EVENT = "special_event"
    SEASONAL = "seasonal"


class ChallengeType(str, Enum):
    """Types of interactive challenges."""
    DONATION_GOAL = "donation_goal"
    VIEWER_COUNT = "viewer_count"
    ENGAGEMENT_TARGET = "engagement_target"
    COMMUNITY_CHALLENGE = "community_challenge"
    TRIVIA_QUIZ = "trivia_quiz"
    PREDICTION_GAME = "prediction_game"
    CREATIVE_CONTEST = "creative_contest"
    INTERACTIVE_POLL = "interactive_poll"


class RewardType(str, Enum):
    """Types of rewards."""
    VIRTUAL_BADGE = "virtual_badge"
    EXCLUSIVE_CONTENT = "exclusive_content"
    DISCOUNT_COUPON = "discount_coupon"
    MERCHANDISE = "merchandise"
    PREMIUM_ACCESS = "premium_access"
    CREATOR_INTERACTION = "creator_interaction"
    PLATFORM_CURRENCY = "platform_currency"
    REAL_MONEY = "real_money"


class BadgeRarity(str, Enum):
    """Badge rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class LeaderboardType(str, Enum):
    """Leaderboard categories."""
    TOP_SUPPORTERS = "top_supporters"
    MOST_ENGAGED = "most_engaged"
    ACHIEVEMENT_HUNTERS = "achievement_hunters"
    CHALLENGE_CHAMPIONS = "challenge_champions"
    WEEKLY_CHAMPIONS = "weekly_champions"
    MONTHLY_LEGENDS = "monthly_legends"
    ALL_TIME_HEROES = "all_time_heroes"


@dataclass
class GamificationConfig:
    """Configuration for streaming gamification."""
    enabled_engagement_types: List[EngagementType]
    achievement_system_enabled: bool = True
    challenges_enabled: bool = True
    leaderboards_enabled: bool = True
    real_time_rewards: bool = True
    badge_system_enabled: bool = True
    point_system_enabled: bool = True
    streak_tracking_enabled: bool = True
    community_challenges_enabled: bool = True
    milestone_celebrations: bool = True
    engagement_multipliers: Dict[str, float] = field(default_factory=dict)
    reward_distribution_settings: Dict[str, Any] = field(default_factory=dict)
    leaderboard_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngagementEvent:
    """Audience engagement event."""
    event_id: str
    session_id: str
    user_id: str
    engagement_type: EngagementType
    event_data: Dict[str, Any]
    engagement_value: float
    points_awarded: int
    timestamp: datetime
    platform: str
    context: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False


@dataclass
class Achievement:
    """Achievement definition."""
    achievement_id: str
    title: str
    description: str
    achievement_type: AchievementType
    criteria: Dict[str, Any]
    reward: Dict[str, Any]
    badge_design: Optional[str] = None
    rarity: BadgeRarity = BadgeRarity.COMMON
    points_value: int = 100
    is_active: bool = True
    unlock_conditions: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserAchievement:
    """User's achieved achievement record."""
    record_id: str
    user_id: str
    achievement_id: str
    session_id: Optional[str] = None
    unlocked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    progress_data: Dict[str, Any] = field(default_factory=dict)
    reward_claimed: bool = False
    reward_claim_date: Optional[datetime] = None


@dataclass
class Challenge:
    """Interactive challenge definition."""
    challenge_id: str
    session_id: str
    creator_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    target_value: Union[int, float]
    start_time: datetime
    current_progress: Union[int, float] = 0
    end_time: Optional[datetime] = None
    is_active: bool = True
    participants: List[str] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    rules: Dict[str, Any] = field(default_factory=dict)
    progress_tracking: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeaderboardEntry:
    """Leaderboard entry."""
    user_id: str
    username: str
    score: Union[int, float]
    rank: int
    badges_earned: int = 0
    achievements_unlocked: int = 0
    engagement_level: str = "bronze"
    avatar_url: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Leaderboard:
    """Leaderboard for different categories."""
    leaderboard_id: str
    leaderboard_type: LeaderboardType
    session_id: Optional[str] = None
    creator_id: Optional[str] = None
    timeframe: str = "weekly"  # daily, weekly, monthly, all_time
    entries: List[LeaderboardEntry] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GamificationAnalytics:
    """Gamification performance analytics."""
    analytics_id: str
    session_id: str
    timeframe: str
    total_engagement_events: int
    engagement_by_type: Dict[EngagementType, int]
    achievements_unlocked: int
    challenges_completed: int
    points_distributed: int
    rewards_claimed: int
    user_participation_rate: float
    engagement_increase: float
    top_performers: List[Dict[str, Any]] = field(default_factory=list)
    engagement_trends: Dict[str, Any] = field(default_factory=dict)
    effectiveness_metrics: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class GamificationRecord(Base):
    """Database model for gamification events."""
    __tablename__ = "streaming_gamification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    engagement_type = Column(String(30), nullable=False)
    event_data = Column(JSON, nullable=False)
    engagement_value = Column(Float, default=0.0)
    points_awarded = Column(Integer, default=0)
    platform = Column(String(30))
    context_data = Column(JSON)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class AchievementRecord(Base):
    """Database model for achievements."""
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    achievement_type = Column(String(30), nullable=False)
    criteria = Column(JSON, nullable=False)
    reward = Column(JSON)
    badge_design = Column(String(500))
    rarity = Column(String(20), default="common")
    points_value = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    unlock_conditions = Column(JSON)
    prerequisites = Column(JSON)
    achievement_meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class UserAchievementRecord(Base):
    """Database model for user achievements."""
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False, index=True)
    achievement_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    unlocked_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    progress_data = Column(JSON)
    reward_claimed = Column(Boolean, default=False)
    reward_claim_date = Column(DateTime(timezone=True))


class ChallengeRecord(Base):
    """Database model for challenges."""
    __tablename__ = "streaming_challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    challenge_type = Column(String(30), nullable=False)
    target_value = Column(Float, nullable=False)
    current_progress = Column(Float, default=0.0)
    start_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    end_time = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    participants = Column(JSON)
    rewards = Column(JSON)
    rules = Column(JSON)
    progress_tracking = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class StreamingGamificationEngine:
    """Enterprise streaming gamification engine for audience engagement."""
    
    def __init__(self, redis_client: redis.Redis, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.is_running = False
        self.active_challenges = {}
        self.achievement_processors = {}
        self.leaderboard_managers = {}
        self.engagement_trackers = {}
        
    async def start_gamification_engine(self):
        """Start the streaming gamification engine."""
        try:
            self.is_running = True
            
            # Initialize gamification components
            await self._initialize_gamification_systems()
            
            # Load active achievements and challenges
            await self._load_active_achievements()
            await self._load_active_challenges()
            
            # Start background gamification tasks
            asyncio.create_task(self._engagement_processor())
            asyncio.create_task(self._achievement_monitor())
            asyncio.create_task(self._challenge_coordinator())
            asyncio.create_task(self._leaderboard_updater())
            asyncio.create_task(self._reward_distributor())
            
            logger.info("Streaming Gamification Engine started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start gamification engine: {e}")
            raise
    
    async def stop_gamification_engine(self):
        """Stop the streaming gamification engine."""
        try:
            self.is_running = False
            
            # Finalize active challenges
            for challenge_id in list(self.active_challenges.keys()):
                await self._finalize_challenge(challenge_id)
            
            logger.info("Streaming Gamification Engine stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop gamification engine: {e}")
    
    async def configure_session_gamification(
        self, 
        session_id: str, 
        creator_id: str,
        config: GamificationConfig
    ) -> Dict[str, Any]:
        """Configure gamification for streaming session."""
        try:
            # Validate configuration
            validation_result = await self._validate_gamification_config(config)
            if not validation_result['valid']:
                return {'success': False, 'errors': validation_result['errors']}
            
            # Setup achievement tracking
            achievement_setup = await self._setup_achievement_tracking(session_id, creator_id, config)
            
            # Initialize challenges
            challenge_setup = await self._initialize_session_challenges(session_id, creator_id, config)
            
            # Setup leaderboards
            leaderboard_setup = await self._setup_session_leaderboards(session_id, creator_id, config)
            
            # Configure engagement tracking
            engagement_setup = await self._configure_engagement_tracking(session_id, config)
            
            # Cache gamification configuration
            gamification_data = {
                'session_id': session_id,
                'creator_id': creator_id,
                'config': asdict(config),
                'achievement_setup': achievement_setup,
                'challenge_setup': challenge_setup,
                'leaderboard_setup': leaderboard_setup,
                'engagement_setup': engagement_setup,
                'configured_at': datetime.now(timezone.utc).isoformat()
            }
            
            await self.redis.setex(
                f"streaming:gamification:{session_id}",
                3600,  # 1 hour
                json.dumps(gamification_data, default=str)
            )
            
            return {
                'success': True,
                'gamification_id': str(uuid.uuid4()),
                'achievements_enabled': config.achievement_system_enabled,
                'challenges_enabled': config.challenges_enabled,
                'leaderboards_enabled': config.leaderboards_enabled,
                'engagement_types_tracked': len(config.enabled_engagement_types)
            }
            
        except Exception as e:
            logger.error(f"Failed to configure session gamification: {e}")
            return {'success': False, 'error': str(e)}
    
    async def process_engagement_event(
        self, 
        session_id: str, 
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process audience engagement event."""
        try:
            event_id = str(uuid.uuid4())
            
            # Create engagement event
            event = EngagementEvent(
                event_id=event_id,
                session_id=session_id,
                user_id=event_data['user_id'],
                engagement_type=EngagementType(event_data['type']),
                event_data=event_data.get('data', {}),
                engagement_value=event_data.get('value', 1.0),
                points_awarded=0,  # Will be calculated
                timestamp=datetime.now(timezone.utc),
                platform=event_data.get('platform', 'web'),
                context=event_data.get('context', {})
            )
            
            # Calculate points awarded
            points_awarded = await self._calculate_engagement_points(session_id, event)
            event.points_awarded = points_awarded
            
            # Save engagement event
            await self._save_engagement_event(event)
            
            # Process for achievements
            achievements_triggered = await self._check_achievement_triggers(session_id, event)
            
            # Update challenges
            challenges_updated = await self._update_challenge_progress(session_id, event)
            
            # Update leaderboards
            await self._update_leaderboards(session_id, event)
            
            # Process real-time rewards
            rewards_processed = []
            if await self._is_real_time_rewards_enabled(session_id):
                rewards_processed = await self._process_real_time_rewards(session_id, event)
            
            # Update engagement analytics
            await self._update_engagement_analytics(session_id, event)
            
            # Mark event as processed
            event.processed = True
            await self._update_engagement_event(event)
            
            return {
                'event_id': event_id,
                'points_awarded': points_awarded,
                'achievements_triggered': len(achievements_triggered),
                'challenges_updated': len(challenges_updated),
                'rewards_processed': len(rewards_processed),
                'processed_successfully': True
            }
            
        except Exception as e:
            logger.error(f"Failed to process engagement event: {e}")
            return {'processed_successfully': False, 'error': str(e)}
    
    async def create_interactive_challenge(
        self, 
        session_id: str, 
        creator_id: str,
        challenge_data: Dict[str, Any]
    ) -> Challenge:
        """Create interactive challenge for streaming session."""
        try:
            challenge_id = str(uuid.uuid4())
            
            # Validate challenge data
            validation_result = await self._validate_challenge_data(challenge_data)
            if not validation_result['valid']:
                raise ValueError(f"Invalid challenge data: {validation_result['errors']}")
            
            # Calculate end time if duration provided
            end_time = None
            if 'duration_minutes' in challenge_data:
                end_time = datetime.now(timezone.utc) + timedelta(minutes=challenge_data['duration_minutes'])
            elif 'end_time' in challenge_data:
                end_time = datetime.fromisoformat(challenge_data['end_time'])
            
            # Create challenge
            challenge = Challenge(
                challenge_id=challenge_id,
                session_id=session_id,
                creator_id=creator_id,
                title=challenge_data['title'],
                description=challenge_data.get('description', ''),
                challenge_type=ChallengeType(challenge_data['type']),
                target_value=challenge_data['target_value'],
                start_time=datetime.now(timezone.utc),
                end_time=end_time,
                rewards=challenge_data.get('rewards', {}),
                rules=challenge_data.get('rules', {}),
                progress_tracking={'tracking_method': challenge_data.get('tracking_method', 'automatic')}
            )
            
            # Save challenge to database
            await self._save_challenge(challenge)
            
            # Add to active challenges
            self.active_challenges[challenge_id] = challenge
            
            # Cache challenge data
            await self._cache_challenge_data(challenge_id, challenge)
            
            # Notify session participants
            await self._notify_challenge_created(session_id, challenge)
            
            # Start challenge monitoring
            asyncio.create_task(self._monitor_challenge_progress(challenge_id))
            
            return challenge
            
        except Exception as e:
            logger.error(f"Failed to create interactive challenge: {e}")
            raise
    
    async def manage_achievement_system(
        self, 
        session_id: str, 
        action: str,
        achievement_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Manage achievement system for session."""
        try:
            if action == "create_achievement":
                return await self._create_custom_achievement(session_id, achievement_data)
            elif action == "unlock_achievement":
                return await self._unlock_achievement(
                    achievement_data['user_id'], 
                    achievement_data['achievement_id'],
                    session_id
                )
            elif action == "check_progress":
                return await self._check_achievement_progress(
                    achievement_data['user_id'],
                    session_id
                )
            elif action == "claim_reward":
                return await self._claim_achievement_reward(
                    achievement_data['user_id'],
                    achievement_data['achievement_id']
                )
            elif action == "list_available":
                return await self._list_available_achievements(session_id)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            logger.error(f"Failed to manage achievement system: {e}")
            return {'success': False, 'error': str(e)}
    
    async def update_leaderboards(
        self, 
        session_id: str, 
        leaderboard_type: Optional[LeaderboardType] = None
    ) -> Dict[str, Any]:
        """Update leaderboards for streaming session."""
        try:
            updated_leaderboards = {}
            
            # Determine which leaderboards to update
            leaderboard_types = [leaderboard_type] if leaderboard_type else list(LeaderboardType)
            
            for lb_type in leaderboard_types:
                leaderboard = await self._generate_leaderboard(session_id, lb_type)
                
                if leaderboard:
                    # Save leaderboard
                    await self._save_leaderboard(leaderboard)
                    
                    # Cache leaderboard
                    await self._cache_leaderboard(session_id, leaderboard)
                    
                    updated_leaderboards[lb_type.value] = {
                        'entry_count': len(leaderboard.entries),
                        'last_updated': leaderboard.last_updated.isoformat(),
                        'top_performer': leaderboard.entries[0].username if leaderboard.entries else None
                    }
            
            return {
                'success': True,
                'updated_leaderboards': updated_leaderboards,
                'update_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update leaderboards: {e}")
            return {'success': False, 'error': str(e)}
    
    async def generate_gamification_analytics(
        self, 
        session_id: str, 
        timeframe: str = "session"
    ) -> GamificationAnalytics:
        """Generate comprehensive gamification analytics."""
        try:
            analytics_id = str(uuid.uuid4())
            
            # Define time range
            if timeframe == "session":
                start_time = await self._get_session_start_time(session_id)
                end_time = datetime.now(timezone.utc)
            elif timeframe == "daily":
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(days=1)
            elif timeframe == "weekly":
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(weeks=1)
            else:
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(hours=24)  # Default to 24 hours
            
            # Collect engagement data
            engagement_data = await self._collect_engagement_data(session_id, start_time, end_time)
            
            # Calculate analytics metrics
            total_events = len(engagement_data['events'])
            engagement_by_type = await self._calculate_engagement_by_type(engagement_data['events'])
            
            # Achievement metrics
            achievement_metrics = await self._calculate_achievement_metrics(session_id, start_time, end_time)
            
            # Challenge metrics
            challenge_metrics = await self._calculate_challenge_metrics(session_id, start_time, end_time)
            
            # Participation metrics
            participation_metrics = await self._calculate_participation_metrics(engagement_data)
            
            # Effectiveness metrics
            effectiveness_metrics = await self._calculate_gamification_effectiveness(
                engagement_data, achievement_metrics, challenge_metrics
            )
            
            # Top performers
            top_performers = await self._identify_top_performers(session_id, timeframe)
            
            # Engagement trends
            engagement_trends = await self._analyze_engagement_trends(engagement_data)
            
            analytics = GamificationAnalytics(
                analytics_id=analytics_id,
                session_id=session_id,
                timeframe=timeframe,
                total_engagement_events=total_events,
                engagement_by_type=engagement_by_type,
                achievements_unlocked=achievement_metrics['unlocked'],
                challenges_completed=challenge_metrics['completed'],
                points_distributed=engagement_data['total_points'],
                rewards_claimed=achievement_metrics['rewards_claimed'],
                user_participation_rate=participation_metrics['participation_rate'],
                engagement_increase=effectiveness_metrics['engagement_increase'],
                top_performers=top_performers,
                engagement_trends=engagement_trends,
                effectiveness_metrics=effectiveness_metrics
            )
            
            # Cache analytics
            await self._cache_gamification_analytics(session_id, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to generate gamification analytics: {e}")
            raise
    
    async def _initialize_gamification_systems(self):
        """Initialize gamification system components."""
        # Load default achievements
        await self._load_default_achievements()
        logger.info("Gamification systems initialized")
    
    async def _validate_gamification_config(self, config: GamificationConfig) -> Dict[str, Any]:
        """Validate gamification configuration."""
        errors = []
        
        if not config.enabled_engagement_types:
            errors.append("At least one engagement type must be enabled")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    async def _calculate_engagement_points(self, session_id: str, event: EngagementEvent) -> int:
        """Calculate points for engagement event."""
        base_points = {
            EngagementType.CHAT_MESSAGE: 1,
            EngagementType.REACTION: 2,
            EngagementType.DONATION: 10,
            EngagementType.SUPER_CHAT: 15,
            EngagementType.SUBSCRIPTION: 50,
            EngagementType.SHARE: 25,
            EngagementType.LIKE: 5,
            EngagementType.FOLLOW: 30,
            EngagementType.POLL_VOTE: 3,
            EngagementType.CHALLENGE_PARTICIPATION: 20
        }
        
        points = base_points.get(event.engagement_type, 1)
        
        # Apply value multiplier
        points = int(points * event.engagement_value)
        
        # Apply session-specific multipliers
        multiplier = await self._get_session_point_multiplier(session_id, event.engagement_type)
        points = int(points * multiplier)
        
        return max(points, 1)  # Minimum 1 point
    
    async def _check_achievement_triggers(
        self, 
        session_id: str, 
        event: EngagementEvent
    ) -> List[str]:
        """Check if event triggers any achievements."""
        triggered_achievements = []
        
        # Get user's current progress
        user_progress = await self._get_user_achievement_progress(event.user_id, session_id)
        
        # Check all active achievements
        active_achievements = await self._get_active_achievements(session_id)
        
        for achievement in active_achievements:
            if await self._check_achievement_criteria(achievement, event, user_progress):
                # Achievement triggered
                unlock_result = await self._unlock_achievement(
                    event.user_id, achievement['id'], session_id, event
                )
                if unlock_result['success']:
                    triggered_achievements.append(achievement['id'])
        
        return triggered_achievements
    
    async def _update_challenge_progress(
        self, 
        session_id: str, 
        event: EngagementEvent
    ) -> List[str]:
        """Update challenge progress based on engagement event."""
        updated_challenges = []
        
        # Get active challenges for session
        session_challenges = await self._get_active_session_challenges(session_id)
        
        for challenge in session_challenges:
            if await self._event_affects_challenge(challenge, event):
                # Update progress
                progress_update = await self._calculate_challenge_progress_update(challenge, event)
                
                if progress_update['updated']:
                    challenge['current_progress'] = progress_update['new_progress']
                    
                    # Save updated challenge
                    await self._save_challenge_progress(challenge['id'], progress_update)
                    
                    # Check if challenge completed
                    if progress_update['new_progress'] >= challenge['target_value']:
                        await self._complete_challenge(challenge['id'])
                    
                    updated_challenges.append(challenge['id'])
        
        return updated_challenges
    
    async def _generate_leaderboard(
        self, 
        session_id: str, 
        leaderboard_type: LeaderboardType
    ) -> Optional[Leaderboard]:
        """Generate leaderboard for specific type."""
        try:
            leaderboard_id = str(uuid.uuid4())
            
            # Get leaderboard data based on type
            if leaderboard_type == LeaderboardType.TOP_SUPPORTERS:
                entries = await self._get_top_supporters_leaderboard(session_id)
            elif leaderboard_type == LeaderboardType.MOST_ENGAGED:
                entries = await self._get_most_engaged_leaderboard(session_id)
            elif leaderboard_type == LeaderboardType.ACHIEVEMENT_HUNTERS:
                entries = await self._get_achievement_hunters_leaderboard(session_id)
            elif leaderboard_type == LeaderboardType.CHALLENGE_CHAMPIONS:
                entries = await self._get_challenge_champions_leaderboard(session_id)
            else:
                entries = await self._get_generic_leaderboard(session_id, leaderboard_type)
            
            if not entries:
                return None
            
            leaderboard = Leaderboard(
                leaderboard_id=leaderboard_id,
                leaderboard_type=leaderboard_type,
                session_id=session_id,
                entries=entries
            )
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Failed to generate leaderboard: {e}")
            return None
    
    # Background task methods
    async def _engagement_processor(self):
        """Background engagement event processing."""
        while self.is_running:
            try:
                # Process pending engagement events
                pending_events = await self._get_pending_engagement_events()
                
                for event in pending_events:
                    await self.process_engagement_event(event['session_id'], event['event_data'])
                
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                logger.error(f"Engagement processor error: {e}")
                await asyncio.sleep(10)
    
    async def _achievement_monitor(self):
        """Monitor achievement progress and triggers."""
        while self.is_running:
            try:
                # Monitor achievement progress for all active sessions
                active_sessions = await self.redis.keys("streaming:gamification:*")
                
                for session_key in active_sessions:
                    session_id = session_key.split(":")[-1]
                    await self._check_time_based_achievements(session_id)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Achievement monitor error: {e}")
                await asyncio.sleep(120)
    
    async def _challenge_coordinator(self):
        """Coordinate active challenges."""
        while self.is_running:
            try:
                # Check challenge timeouts and completions
                for challenge_id, challenge in list(self.active_challenges.items()):
                    await self._check_challenge_status(challenge_id, challenge)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Challenge coordinator error: {e}")
                await asyncio.sleep(60)
    
    async def _leaderboard_updater(self):
        """Update leaderboards periodically."""
        while self.is_running:
            try:
                # Update leaderboards for active sessions
                active_sessions = await self._get_active_gamification_sessions()
                
                for session_id in active_sessions:
                    await self.update_leaderboards(session_id)
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Leaderboard updater error: {e}")
                await asyncio.sleep(600)
    
    async def _reward_distributor(self):
        """Distribute rewards for achievements and challenges."""
        while self.is_running:
            try:
                # Process pending reward distributions
                await self._process_pending_rewards()
                
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                logger.error(f"Reward distributor error: {e}")
                await asyncio.sleep(120)
    
    # Utility methods (simplified implementations)
    async def _save_engagement_event(self, event: EngagementEvent):
        """Save engagement event to database."""
        try:
            record = GamificationRecord(
                id=event.event_id,
                session_id=event.session_id,
                user_id=event.user_id,
                engagement_type=event.engagement_type.value,
                event_data=event.event_data,
                engagement_value=event.engagement_value,
                points_awarded=event.points_awarded,
                platform=event.platform,
                context_data=event.context,
                processed=event.processed
            )
            
            self.db.add(record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save engagement event: {e}")
    
    async def _load_default_achievements(self):
        """Load default achievements from database."""
        try:
            # Load common achievements
            default_achievements = [
                {
                    'title': 'First Message',
                    'description': 'Send your first chat message',
                    'type': 'first_time',
                    'criteria': {'engagement_type': 'chat_message', 'count': 1},
                    'points': 10
                },
                {
                    'title': 'Supporter',
                    'description': 'Make your first donation',
                    'type': 'first_time', 
                    'criteria': {'engagement_type': 'donation', 'count': 1},
                    'points': 50
                },
                {
                    'title': 'Social Butterfly',
                    'description': 'Send 100 chat messages',
                    'type': 'milestone',
                    'criteria': {'engagement_type': 'chat_message', 'count': 100},
                    'points': 100
                }
            ]
            
            for achievement_data in default_achievements:
                await self._create_default_achievement(achievement_data)
            
        except Exception as e:
            logger.error(f"Failed to load default achievements: {e}")


def create_streaming_gamification_engine(
    redis_client: redis.Redis, 
    db_session: Session
) -> StreamingGamificationEngine:
    """Factory function to create Streaming Gamification Engine instance."""
    return StreamingGamificationEngine(redis_client, db_session)