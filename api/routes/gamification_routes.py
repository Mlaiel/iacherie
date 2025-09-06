"""
Gamification Routes - Enterprise Gaming & Rewards System API
Advanced gamification with points, badges, leaderboards, achievements, and NFT rewards.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import asyncio

# Enterprise Security
security = HTTPBearer()

router = APIRouter(
    prefix="/gamification",
    tags=["gamification"],
    responses={404: {"description": "Not found"}}
)

# ========================================
# ENUMS & CONSTANTS
# ========================================

class AchievementType(str, Enum):
    CONTENT_MILESTONE = "content_milestone"
    REVENUE_MILESTONE = "revenue_milestone"
    ENGAGEMENT_MILESTONE = "engagement_milestone"
    COLLABORATION_MILESTONE = "collaboration_milestone"
    PROTECTION_MILESTONE = "protection_milestone"
    PLATFORM_MILESTONE = "platform_milestone"
    COMMUNITY_MILESTONE = "community_milestone"
    STREAK_MILESTONE = "streak_milestone"

class BadgeRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class LeaderboardType(str, Enum):
    POINTS = "points"
    REVENUE = "revenue"
    CONTENT_QUALITY = "content_quality"
    COLLABORATION_RATING = "collaboration_rating"
    PROTECTION_SCORE = "protection_score"
    ENGAGEMENT_RATE = "engagement_rate"
    PLATFORM_REACH = "platform_reach"

class ChallengeType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"
    COMMUNITY = "community"

class ChallengeStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class RewardType(str, Enum):
    POINTS = "points"
    BADGE = "badge"
    NFT = "nft"
    PREMIUM_FEATURES = "premium_features"
    STORAGE_BOOST = "storage_boost"
    API_QUOTA_BOOST = "api_quota_boost"
    EXCLUSIVE_ACCESS = "exclusive_access"
    MONETARY = "monetary"

class TierLevel(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"

# ========================================
# PYDANTIC MODELS
# ========================================

class GamificationProfile(BaseModel):
    user_id: str
    total_points: int = Field(default=0, ge=0)
    level: int = Field(default=1, ge=1)
    tier: TierLevel = Field(default=TierLevel.BRONZE)
    experience_points: int = Field(default=0, ge=0)
    next_level_points: int = Field(default=100, ge=0)
    badges_earned: List[str] = Field(default_factory=list)
    achievements_unlocked: List[str] = Field(default_factory=list)
    current_streak: int = Field(default=0, ge=0)
    longest_streak: int = Field(default=0, ge=0)
    leaderboard_rank: Dict[LeaderboardType, int] = Field(default_factory=dict)
    nft_rewards: List[str] = Field(default_factory=list)
    premium_benefits: List[str] = Field(default_factory=list)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Achievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    achievement_type: AchievementType
    criteria: Dict[str, Any] = Field(..., description="Achievement criteria")
    points_reward: int = Field(..., ge=0)
    badge_id: Optional[str] = None
    rarity: BadgeRarity = Field(default=BadgeRarity.COMMON)
    icon_url: Optional[str] = None
    is_secret: bool = Field(default=False)
    prerequisites: List[str] = Field(default_factory=list, description="Required achievements")
    progress_trackable: bool = Field(default=True)
    max_progress: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Badge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    rarity: BadgeRarity
    icon_url: str = Field(..., description="Badge icon URL")
    nft_metadata: Optional[Dict[str, Any]] = None
    points_value: int = Field(..., ge=0)
    unlock_criteria: Dict[str, Any] = Field(default_factory=dict)
    earned_count: int = Field(default=0, ge=0, description="Total times earned")
    is_limited_edition: bool = Field(default=False)
    max_supply: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserBadge(BaseModel):
    user_id: str
    badge_id: str
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    achievement_id: Optional[str] = None
    nft_token_id: Optional[str] = None
    is_featured: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    rank: int = Field(..., ge=1)
    score: Union[int, float, Decimal]
    tier: TierLevel
    badges_count: int = Field(default=0, ge=0)
    achievements_count: int = Field(default=0, ge=0)
    change_from_previous: Optional[int] = None  # +/- rank change
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Challenge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    challenge_type: ChallengeType
    difficulty: int = Field(..., ge=1, le=5, description="Difficulty level 1-5")
    objective: Dict[str, Any] = Field(..., description="Challenge objective")
    rewards: List[Dict[str, Any]] = Field(..., description="Completion rewards")
    start_date: datetime
    end_date: datetime
    participants_count: int = Field(default=0, ge=0)
    completion_count: int = Field(default=0, ge=0)
    max_participants: Optional[int] = None
    is_public: bool = Field(default=True)
    prerequisites: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserChallenge(BaseModel):
    user_id: str
    challenge_id: str
    status: ChallengeStatus = Field(default=ChallengeStatus.ACTIVE)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    current_value: int = Field(default=0, ge=0)
    target_value: int = Field(..., ge=1)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    rewards_claimed: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Reward(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    reward_type: RewardType
    value: Union[int, float, str] = Field(..., description="Reward value")
    cost_points: int = Field(..., ge=0, description="Points cost")
    rarity: BadgeRarity = Field(default=BadgeRarity.COMMON)
    icon_url: Optional[str] = None
    is_limited: bool = Field(default=False)
    stock_available: Optional[int] = None
    stock_total: Optional[int] = None
    expiration_date: Optional[datetime] = None
    requirements: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserReward(BaseModel):
    user_id: str
    reward_id: str
    claimed_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PointsTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: int = Field(..., description="Points amount (positive for earn, negative for spend)")
    source: str = Field(..., description="Source of points transaction")
    description: str = Field(..., max_length=200)
    reference_id: Optional[str] = None  # Achievement, challenge, etc.
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GameAction(BaseModel):
    action_type: str = Field(..., description="Type of action performed")
    action_data: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[str] = None

# ========================================
# DEPENDENCY FUNCTIONS
# ========================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Extract user information from JWT token"""
    return {
        "id": "user_123",
        "email": "creator@example.com",
        "name": "Demo Creator",
        "username": "demo_creator"
    }

# ========================================
# GAMIFICATION PROFILE
# ========================================

@router.get("/profile", response_model=GamificationProfile)
async def get_gamification_profile(
    current_user: Dict = Depends(get_current_user)
):
    """Get user's gamification profile"""
    
    return GamificationProfile(
        user_id=current_user["id"],
        total_points=15750,
        level=12,
        tier=TierLevel.GOLD,
        experience_points=1250,
        next_level_points=2000,
        badges_earned=["content_creator", "collaborator", "protector", "early_adopter"],
        achievements_unlocked=["first_upload", "100_uploads", "viral_content", "collaboration_master"],
        current_streak=23,
        longest_streak=45,
        leaderboard_rank={
            LeaderboardType.POINTS: 47,
            LeaderboardType.REVENUE: 23,
            LeaderboardType.CONTENT_QUALITY: 15
        },
        nft_rewards=["rare_creator_badge_001", "legendary_collaborator_nft"],
        premium_benefits=["extended_storage", "priority_support", "advanced_analytics"]
    )

@router.post("/action")
async def process_game_action(
    action: GameAction,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Process a gamification action and update user progress"""
    
    # Schedule background processing
    background_tasks.add_task(process_gamification_action, current_user["id"], action)
    
    # Immediate response with potential rewards
    points_earned = calculate_points_for_action(action.action_type)
    
    return {
        "action_processed": True,
        "action_type": action.action_type,
        "points_earned": points_earned,
        "new_achievements": [],  # Will be updated by background task
        "new_badges": [],       # Will be updated by background task
        "level_up": False,      # Will be updated by background task
        "processed_at": datetime.utcnow()
    }

# ========================================
# ACHIEVEMENTS
# ========================================

@router.get("/achievements", response_model=List[Achievement])
async def get_achievements(
    achievement_type: Optional[AchievementType] = Query(None),
    rarity: Optional[BadgeRarity] = Query(None),
    earned_only: bool = Query(False, description="Show only earned achievements"),
    include_secret: bool = Query(False, description="Include secret achievements"),
    current_user: Dict = Depends(get_current_user)
):
    """Get available achievements"""
    
    # Mock achievements data
    achievements = [
        Achievement(
            id="ach_first_upload",
            name="First Steps",
            description="Upload your first piece of content",
            achievement_type=AchievementType.CONTENT_MILESTONE,
            criteria={"content_uploads": 1},
            points_reward=100,
            badge_id="badge_newcomer",
            rarity=BadgeRarity.COMMON,
            icon_url="https://cdn.ainflue.com/achievements/first_upload.png"
        ),
        Achievement(
            id="ach_100_uploads",
            name="Content Creator",
            description="Upload 100 pieces of content",
            achievement_type=AchievementType.CONTENT_MILESTONE,
            criteria={"content_uploads": 100},
            points_reward=1000,
            badge_id="badge_creator",
            rarity=BadgeRarity.UNCOMMON,
            icon_url="https://cdn.ainflue.com/achievements/100_uploads.png"
        ),
        Achievement(
            id="ach_revenue_10k",
            name="Revenue Milestone",
            description="Earn $10,000 in total revenue",
            achievement_type=AchievementType.REVENUE_MILESTONE,
            criteria={"total_revenue": 10000},
            points_reward=2500,
            badge_id="badge_earner",
            rarity=BadgeRarity.RARE,
            icon_url="https://cdn.ainflue.com/achievements/revenue_10k.png"
        ),
        Achievement(
            id="ach_collaboration_master",
            name="Collaboration Master",
            description="Complete 25 successful collaborations",
            achievement_type=AchievementType.COLLABORATION_MILESTONE,
            criteria={"successful_collaborations": 25},
            points_reward=1500,
            badge_id="badge_collaborator",
            rarity=BadgeRarity.EPIC,
            icon_url="https://cdn.ainflue.com/achievements/collab_master.png"
        ),
        Achievement(
            id="ach_protection_hero",
            name="Protection Hero",
            description="Successfully protect content from 100 violations",
            achievement_type=AchievementType.PROTECTION_MILESTONE,
            criteria={"violations_prevented": 100},
            points_reward=2000,
            badge_id="badge_protector",
            rarity=BadgeRarity.LEGENDARY,
            icon_url="https://cdn.ainflue.com/achievements/protection_hero.png",
            is_secret=True
        )
    ]
    
    # Apply filters
    if achievement_type:
        achievements = [a for a in achievements if a.achievement_type == achievement_type]
    if rarity:
        achievements = [a for a in achievements if a.rarity == rarity]
    if not include_secret:
        achievements = [a for a in achievements if not a.is_secret]
    
    return achievements

@router.get("/achievements/{achievement_id}", response_model=Achievement)
async def get_achievement_details(
    achievement_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get detailed information about specific achievement"""
    
    # Mock achievement details
    achievement = Achievement(
        id=achievement_id,
        name="Viral Content Creator",
        description="Create content that reaches 1 million views",
        achievement_type=AchievementType.ENGAGEMENT_MILESTONE,
        criteria={"content_views": 1000000},
        points_reward=5000,
        badge_id="badge_viral",
        rarity=BadgeRarity.LEGENDARY,
        icon_url="https://cdn.ainflue.com/achievements/viral_creator.png",
        progress_trackable=True,
        max_progress=1000000
    )
    
    return achievement

@router.get("/achievements/{achievement_id}/progress")
async def get_achievement_progress(
    achievement_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get user's progress towards specific achievement"""
    
    # Mock progress data
    return {
        "achievement_id": achievement_id,
        "user_id": current_user["id"],
        "current_progress": 750000,
        "target_progress": 1000000,
        "percentage": 75.0,
        "is_completed": False,
        "estimated_completion": datetime.utcnow() + timedelta(days=30),
        "last_updated": datetime.utcnow()
    }

# ========================================
# BADGES & REWARDS
# ========================================

@router.get("/badges", response_model=List[Badge])
async def get_badges(
    rarity: Optional[BadgeRarity] = Query(None),
    earned_only: bool = Query(False),
    current_user: Dict = Depends(get_current_user)
):
    """Get available badges"""
    
    badges = [
        Badge(
            id="badge_newcomer",
            name="Newcomer",
            description="Welcome to the Ainflue platform!",
            rarity=BadgeRarity.COMMON,
            icon_url="https://cdn.ainflue.com/badges/newcomer.png",
            points_value=100,
            earned_count=15420
        ),
        Badge(
            id="badge_creator",
            name="Content Creator",
            description="Dedicated content creator with 100+ uploads",
            rarity=BadgeRarity.UNCOMMON,
            icon_url="https://cdn.ainflue.com/badges/creator.png",
            points_value=500,
            earned_count=2850
        ),
        Badge(
            id="badge_collaborator",
            name="Master Collaborator",
            description="Expert at creator collaborations",
            rarity=BadgeRarity.EPIC,
            icon_url="https://cdn.ainflue.com/badges/collaborator.png",
            points_value=1500,
            earned_count=156,
            nft_metadata={"contract": "0x...", "collection": "Ainflue Badges"}
        ),
        Badge(
            id="badge_protector",
            name="Content Protector",
            description="Guardian of intellectual property",
            rarity=BadgeRarity.LEGENDARY,
            icon_url="https://cdn.ainflue.com/badges/protector.png",
            points_value=2500,
            earned_count=23,
            is_limited_edition=True,
            max_supply=100,
            nft_metadata={"contract": "0x...", "collection": "Ainflue Elite"}
        )
    ]
    
    if rarity:
        badges = [b for b in badges if b.rarity == rarity]
    
    return badges

@router.get("/badges/earned", response_model=List[UserBadge])
async def get_user_badges(
    current_user: Dict = Depends(get_current_user)
):
    """Get user's earned badges"""
    
    return [
        UserBadge(
            user_id=current_user["id"],
            badge_id="badge_newcomer",
            earned_at=datetime.utcnow() - timedelta(days=30),
            achievement_id="ach_first_upload",
            is_featured=True
        ),
        UserBadge(
            user_id=current_user["id"],
            badge_id="badge_creator",
            earned_at=datetime.utcnow() - timedelta(days=15),
            achievement_id="ach_100_uploads",
            nft_token_id="nft_creator_001"
        )
    ]

@router.post("/badges/{badge_id}/feature")
async def feature_badge(
    badge_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Feature a badge on user profile"""
    
    # In production, update database
    return {
        "message": f"Badge {badge_id} is now featured on your profile",
        "badge_id": badge_id,
        "featured_at": datetime.utcnow()
    }

# ========================================
# LEADERBOARDS
# ========================================

@router.get("/leaderboards/{leaderboard_type}", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    leaderboard_type: LeaderboardType,
    time_period: str = Query("all_time", pattern="^(daily|weekly|monthly|all_time)$"),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """Get leaderboard rankings"""
    
    # Mock leaderboard data
    entries = []
    for i in range(limit):
        rank = i + 1
        if leaderboard_type == LeaderboardType.POINTS:
            score = 25000 - (i * 150)
        elif leaderboard_type == LeaderboardType.REVENUE:
            score = Decimal(str(50000 - (i * 500)))
        else:
            score = 95.5 - (i * 0.1)
        
        entries.append(LeaderboardEntry(
            user_id=f"user_{i+1:03d}",
            username=f"Creator{i+1}",
            avatar_url=f"https://avatars.ainflue.com/user_{i+1}.jpg",
            rank=rank,
            score=score,
            tier=TierLevel.GOLD if rank <= 10 else TierLevel.SILVER if rank <= 50 else TierLevel.BRONZE,
            badges_count=8 - (i // 10),
            achievements_count=15 - (i // 5),
            change_from_previous=1 if i % 3 == 0 else -1 if i % 3 == 1 else 0
        ))
    
    return entries

@router.get("/leaderboards/{leaderboard_type}/rank")
async def get_user_rank(
    leaderboard_type: LeaderboardType,
    time_period: str = Query("all_time", pattern="^(daily|weekly|monthly|all_time)$"),
    current_user: Dict = Depends(get_current_user)
):
    """Get current user's rank in leaderboard"""
    
    return {
        "leaderboard_type": leaderboard_type,
        "time_period": time_period,
        "user_id": current_user["id"],
        "current_rank": 47,
        "total_participants": 2847,
        "percentile": 98.3,
        "score": 18450,
        "change_from_yesterday": 2,
        "next_rank_gap": 150,
        "tier": TierLevel.GOLD
    }

# ========================================
# CHALLENGES
# ========================================

@router.get("/challenges", response_model=List[Challenge])
async def get_challenges(
    challenge_type: Optional[ChallengeType] = Query(None),
    active_only: bool = Query(True),
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    current_user: Dict = Depends(get_current_user)
):
    """Get available challenges"""
    
    challenges = [
        Challenge(
            id="challenge_daily_upload",
            name="Daily Content Creator",
            description="Upload at least one piece of content every day for 7 days",
            challenge_type=ChallengeType.WEEKLY,
            difficulty=2,
            objective={"daily_uploads": 1, "days": 7},
            rewards=[
                {"type": "points", "value": 500},
                {"type": "badge", "value": "streak_keeper"}
            ],
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
            participants_count=1250,
            completion_count=234,
            created_by="system"
        ),
        Challenge(
            id="challenge_collaboration_month",
            name="Collaboration Champion",
            description="Complete 5 successful collaborations this month",
            challenge_type=ChallengeType.MONTHLY,
            difficulty=4,
            objective={"successful_collaborations": 5},
            rewards=[
                {"type": "points", "value": 2000},
                {"type": "nft", "value": "collaboration_champion_nft"},
                {"type": "premium_features", "value": "30_day_boost"}
            ],
            start_date=datetime.utcnow().replace(day=1),
            end_date=datetime.utcnow().replace(day=28),
            participants_count=456,
            completion_count=23,
            created_by="system"
        ),
        Challenge(
            id="challenge_protection_hero",
            name="Content Protection Hero",
            description="Successfully prevent 10 content violations",
            challenge_type=ChallengeType.SPECIAL_EVENT,
            difficulty=5,
            objective={"violations_prevented": 10},
            rewards=[
                {"type": "points", "value": 3000},
                {"type": "badge", "value": "protection_hero"},
                {"type": "monetary", "value": 100}
            ],
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            participants_count=89,
            completion_count=3,
            max_participants=100,
            created_by="system"
        )
    ]
    
    # Apply filters
    if challenge_type:
        challenges = [c for c in challenges if c.challenge_type == challenge_type]
    if difficulty:
        challenges = [c for c in challenges if c.difficulty == difficulty]
    if active_only:
        now = datetime.utcnow()
        challenges = [c for c in challenges if c.start_date <= now <= c.end_date]
    
    return challenges

@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: str,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Join a challenge"""
    
    # Schedule background task to initialize challenge progress
    background_tasks.add_task(initialize_user_challenge, current_user["id"], challenge_id)
    
    return {
        "message": f"Successfully joined challenge {challenge_id}",
        "challenge_id": challenge_id,
        "user_id": current_user["id"],
        "joined_at": datetime.utcnow(),
        "progress": 0.0
    }

@router.get("/challenges/active", response_model=List[UserChallenge])
async def get_user_challenges(
    current_user: Dict = Depends(get_current_user)
):
    """Get user's active challenges"""
    
    return [
        UserChallenge(
            user_id=current_user["id"],
            challenge_id="challenge_daily_upload",
            status=ChallengeStatus.ACTIVE,
            progress=71.4,
            current_value=5,
            target_value=7,
            started_at=datetime.utcnow() - timedelta(days=5)
        ),
        UserChallenge(
            user_id=current_user["id"],
            challenge_id="challenge_collaboration_month",
            status=ChallengeStatus.ACTIVE,
            progress=60.0,
            current_value=3,
            target_value=5,
            started_at=datetime.utcnow() - timedelta(days=15)
        )
    ]

@router.get("/challenges/{challenge_id}/progress")
async def get_challenge_progress(
    challenge_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get detailed challenge progress"""
    
    return {
        "challenge_id": challenge_id,
        "user_id": current_user["id"],
        "status": ChallengeStatus.ACTIVE,
        "progress_percentage": 75.0,
        "current_value": 3,
        "target_value": 4,
        "time_remaining": "5 days, 12 hours",
        "daily_progress": [
            {"date": "2025-01-01", "value": 1},
            {"date": "2025-01-02", "value": 1},
            {"date": "2025-01-03", "value": 1}
        ],
        "rewards_pending": [
            {"type": "points", "value": 1500},
            {"type": "badge", "value": "weekly_warrior"}
        ]
    }

# ========================================
# REWARDS STORE
# ========================================

@router.get("/rewards", response_model=List[Reward])
async def get_rewards_store(
    reward_type: Optional[RewardType] = Query(None),
    max_cost: Optional[int] = Query(None, ge=0),
    available_only: bool = Query(True),
    current_user: Dict = Depends(get_current_user)
):
    """Get available rewards in the store"""
    
    rewards = [
        Reward(
            id="reward_storage_boost",
            name="Storage Boost (10GB)",
            description="Increase your storage quota by 10GB for 30 days",
            reward_type=RewardType.STORAGE_BOOST,
            value="10GB_30days",
            cost_points=1000,
            rarity=BadgeRarity.COMMON,
            icon_url="https://cdn.ainflue.com/rewards/storage_boost.png",
            stock_available=50,
            stock_total=100
        ),
        Reward(
            id="reward_api_boost",
            name="API Quota Boost",
            description="Double your API quota for 7 days",
            reward_type=RewardType.API_QUOTA_BOOST,
            value="double_7days",
            cost_points=750,
            rarity=BadgeRarity.UNCOMMON,
            icon_url="https://cdn.ainflue.com/rewards/api_boost.png"
        ),
        Reward(
            id="reward_premium_month",
            name="Premium Features (1 Month)",
            description="Access to all premium features for 30 days",
            reward_type=RewardType.PREMIUM_FEATURES,
            value="premium_30days",
            cost_points=5000,
            rarity=BadgeRarity.RARE,
            icon_url="https://cdn.ainflue.com/rewards/premium.png",
            stock_available=10,
            stock_total=20,
            expiration_date=datetime.utcnow() + timedelta(days=30)
        ),
        Reward(
            id="reward_exclusive_nft",
            name="Exclusive Creator NFT",
            description="Limited edition NFT for top creators",
            reward_type=RewardType.NFT,
            value="exclusive_creator_001",
            cost_points=10000,
            rarity=BadgeRarity.LEGENDARY,
            icon_url="https://cdn.ainflue.com/nfts/exclusive_creator.png",
            is_limited=True,
            stock_available=2,
            stock_total=10
        )
    ]
    
    # Apply filters
    if reward_type:
        rewards = [r for r in rewards if r.reward_type == reward_type]
    if max_cost:
        rewards = [r for r in rewards if r.cost_points <= max_cost]
    if available_only:
        rewards = [r for r in rewards if not r.stock_available or r.stock_available > 0]
    
    return rewards

@router.post("/rewards/{reward_id}/claim")
async def claim_reward(
    reward_id: str,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Claim a reward from the store"""
    
    # In production, verify user has enough points and deduct them
    user_points = 15750  # Mock user points
    reward_cost = 1000   # Mock reward cost
    
    if user_points < reward_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points"
        )
    
    # Schedule background processing
    background_tasks.add_task(process_reward_claim, current_user["id"], reward_id)
    
    return {
        "message": f"Reward {reward_id} claimed successfully",
        "reward_id": reward_id,
        "points_spent": reward_cost,
        "remaining_points": user_points - reward_cost,
        "claimed_at": datetime.utcnow()
    }

@router.get("/rewards/claimed", response_model=List[UserReward])
async def get_claimed_rewards(
    active_only: bool = Query(True),
    current_user: Dict = Depends(get_current_user)
):
    """Get user's claimed rewards"""
    
    rewards = [
        UserReward(
            user_id=current_user["id"],
            reward_id="reward_storage_boost",
            claimed_at=datetime.utcnow() - timedelta(days=5),
            expires_at=datetime.utcnow() + timedelta(days=25),
            is_active=True
        ),
        UserReward(
            user_id=current_user["id"],
            reward_id="reward_api_boost",
            claimed_at=datetime.utcnow() - timedelta(days=10),
            expires_at=datetime.utcnow() - timedelta(days=3),
            is_active=False
        )
    ]
    
    if active_only:
        rewards = [r for r in rewards if r.is_active]
    
    return rewards

# ========================================
# POINTS & TRANSACTIONS
# ========================================

@router.get("/points/balance")
async def get_points_balance(
    current_user: Dict = Depends(get_current_user)
):
    """Get user's current points balance"""
    
    return {
        "user_id": current_user["id"],
        "total_points": 15750,
        "points_earned_today": 150,
        "points_earned_this_week": 850,
        "points_earned_this_month": 3450,
        "lifetime_points_earned": 28750,
        "lifetime_points_spent": 13000,
        "pending_points": 250,
        "next_tier_points": 20000,
        "points_to_next_tier": 4250
    }

@router.get("/points/transactions", response_model=List[PointsTransaction])
async def get_points_transactions(
    limit: int = Query(50, ge=1, le=100),
    transaction_type: Optional[str] = Query(None, pattern="^(earned|spent)$"),
    current_user: Dict = Depends(get_current_user)
):
    """Get user's points transaction history"""
    
    transactions = [
        PointsTransaction(
            user_id=current_user["id"],
            amount=500,
            source="achievement_unlock",
            description="Unlocked 'Content Creator' achievement",
            reference_id="ach_100_uploads",
            metadata={"achievement_name": "Content Creator"}
        ),
        PointsTransaction(
            user_id=current_user["id"],
            amount=-1000,
            source="reward_claim",
            description="Claimed Storage Boost reward",
            reference_id="reward_storage_boost"
        ),
        PointsTransaction(
            user_id=current_user["id"],
            amount=250,
            source="daily_activity",
            description="Daily activity bonus",
            metadata={"streak_day": 23}
        ),
        PointsTransaction(
            user_id=current_user["id"],
            amount=750,
            source="challenge_completion",
            description="Completed 'Weekly Upload Challenge'",
            reference_id="challenge_weekly_upload"
        )
    ]
    
    if transaction_type:
        if transaction_type == "earned":
            transactions = [t for t in transactions if t.amount > 0]
        else:  # spent
            transactions = [t for t in transactions if t.amount < 0]
    
    return transactions[:limit]

# ========================================
# BACKGROUND TASKS
# ========================================

async def process_gamification_action(user_id: str, action: GameAction):
    """Process gamification action in background"""
    await asyncio.sleep(2)
    print(f"Processed gamification action {action.action_type} for user {user_id}")

async def initialize_user_challenge(user_id: str, challenge_id: str):
    """Initialize user challenge progress"""
    await asyncio.sleep(1)
    print(f"Initialized challenge {challenge_id} for user {user_id}")

async def process_reward_claim(user_id: str, reward_id: str):
    """Process reward claim"""
    await asyncio.sleep(3)
    print(f"Processed reward claim {reward_id} for user {user_id}")

def calculate_points_for_action(action_type: str) -> int:
    """Calculate points for specific action"""
    point_values = {
        "content_upload": 50,
        "content_view": 1,
        "content_like": 2,
        "content_share": 5,
        "collaboration_start": 100,
        "collaboration_complete": 500,
        "violation_prevented": 150,
        "daily_login": 10,
        "profile_complete": 25
    }
    return point_values.get(action_type, 10)

__all__ = ["router"]