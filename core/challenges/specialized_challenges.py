"""🎯 Specialized Challenge Types - Monthly Creative, Technical & Global Competitions

This module implements the specific challenge types required:
- Monthly Creative Challenges with rewards
- Technical Challenges (SEO, revenue optimization)
- Global Competitions for special events

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)


class SpecializedChallengeType(Enum):
    """
Specialized challenge types for the platform requirements"""

    MONTHLY_CREATIVE = "monthly_creative"
    TECHNICAL_SEO = "technical_seo"
    TECHNICAL_REVENUE = "technical_revenue"
    GLOBAL_COMPETITION = "global_competition"
    SPECIAL_EVENT = "special_event"


class ChallengeRewardType(Enum):
    """Types of rewards for challenges"""

    POINTS = "points"
    BADGE = "badge"
    CASH_PRIZE = "cash_prize"
    FEATURE_UNLOCK = "feature_unlock"
    PREMIUM_EXTENSION = "premium_extension"
    COLLABORATION_OPPORTUNITY = "collaboration_opportunity"
    PLATFORM_BOOST = "platform_boost"


@dataclass
class SpecializedReward:
    """Specialized reward configuration"""
    reward_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reward_type: ChallengeRewardType = ChallengeRewardType.POINTS
    value: Union[int, Decimal, str] = 0
    currency: str = "USD"
    description: str = ""
    conditions: Dict[str, Any] = field(default_factory=dict)
    expiry_date: Optional[datetime] = None
    tier_requirements: List[str] = field(default_factory=list)


@dataclass
class MonthlyCreativeChallenge:
    """Monthly creative challenge with comprehensive reward system"""
    challenge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    theme: str = ""  # Monthly theme (e.g., "Winter Creativity", "AI Innovation")
    
    # Challenge specifics
    content_requirements: Dict[str, Any] = field(default_factory=dict)
    creative_constraints: List[str] = field(default_factory=list)
    inspiration_sources: List[str] = field(default_factory=list)
    
    # Timing
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))
    submission_deadline: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=28))
    
    # Rewards
    grand_prize: SpecializedReward = field(default_factory=SpecializedReward)
    runner_up_prizes: List[SpecializedReward] = field(default_factory=list)
    participation_rewards: List[SpecializedReward] = field(default_factory=list)
    milestone_rewards: Dict[str, SpecializedReward] = field(default_factory=dict)
    
    # Community features
    community_voting_enabled: bool = True
    expert_judging_enabled: bool = True
    peer_collaboration_allowed: bool = True
    
    # Analytics
    participants: List[str] = field(default_factory=list)
    submissions: List[Dict[str, Any]] = field(default_factory=list)
    voting_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class TechnicalChallenge:
    """Technical challenges for SEO and revenue optimization"""
    challenge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    technical_focus: str = ""  # "seo", "revenue_optimization", "analytics"
    
    # Technical requirements
    target_metrics: Dict[str, Union[int, float, Decimal]] = field(default_factory=dict)
    measurement_period: int = 30  # days
    baseline_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # SEO specific
    seo_targets: Dict[str, Any] = field(default_factory=lambda: {
        "ranking_improvement": 0,
        "organic_traffic_increase": 0,
        "keyword_optimization_count": 0,
        "content_quality_score": 0
    })
    
    # Revenue specific  
    revenue_targets: Dict[str, Any] = field(default_factory=lambda: {
        "revenue_increase_percentage": 0,
        "new_revenue_streams": 0,
        "monetization_optimization": 0,
        "conversion_rate_improvement": 0
    })
    
    # Validation
    automated_tracking: bool = True
    manual_verification: bool = False
    third_party_validation: bool = False
    
    # Rewards
    achievement_rewards: List[SpecializedReward] = field(default_factory=list)
    progressive_rewards: Dict[str, SpecializedReward] = field(default_factory=dict)
    
    # Timing
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))


@dataclass
class GlobalCompetition:
    """Global competitions for special events"""
    competition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    event_type: str = ""  # "seasonal", "milestone", "partnership", "anniversary"
    
    # Global scope
    participating_regions: List[str] = field(default_factory=list)
    language_support: List[str] = field(default_factory=list)
    timezone_considerations: Dict[str, Any] = field(default_factory=dict)
    
    # Competition structure
    phases: List[Dict[str, Any]] = field(default_factory=list)
    elimination_rounds: bool = False
    team_competition: bool = False
    individual_competition: bool = True
    
    # Special event features
    live_streaming: bool = False
    real_time_leaderboard: bool = True
    social_media_integration: bool = True
    influencer_partnerships: bool = False
    
    # Massive reward pool
    total_prize_pool: Decimal = Decimal('0')
    prize_distribution: Dict[str, SpecializedReward] = field(default_factory=dict)
    special_recognitions: List[SpecializedReward] = field(default_factory=list)
    
    # Event timing
    registration_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    registration_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7))
    competition_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=14))
    competition_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=44))
    
    # Global analytics
    regional_participation: Dict[str, int] = field(default_factory=dict)
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)


class SpecializedChallengeManager:
    """Manager for specialized challenge types"""
    
    def __init__(self):
        self.monthly_challenges: Dict[str, MonthlyCreativeChallenge] = {}
        self.technical_challenges: Dict[str, TechnicalChallenge] = {}
        self.global_competitions: Dict[str, GlobalCompetition] = {}
        self.active_events: Dict[str, Any] = {}
        
        logger.info("SpecializedChallengeManager initialized")
    
    async def create_monthly_creative_challenge(
        self,
        title: str,
        theme: str,
        description: str = "",
        **kwargs
    ) -> MonthlyCreativeChallenge:
        """Create a new monthly creative challenge"""
        
        challenge = MonthlyCreativeChallenge(
            title=title,
            description=description,
            theme=theme,
            **kwargs
        )
        
        # Set up default rewards
        challenge.grand_prize = SpecializedReward(
            reward_type=ChallengeRewardType.CASH_PRIZE,
            value=Decimal('500'),
            description="Monthly Creative Challenge Grand Prize"
        )
        
        challenge.runner_up_prizes = [
            SpecializedReward(
                reward_type=ChallengeRewardType.CASH_PRIZE,
                value=Decimal('200'),
                description="Second Place Prize"
            ),
            SpecializedReward(
                reward_type=ChallengeRewardType.CASH_PRIZE,
                value=Decimal('100'),
                description="Third Place Prize"
            )
        ]
        
        challenge.participation_rewards = [
            SpecializedReward(
                reward_type=ChallengeRewardType.POINTS,
                value=100,
                description="Participation Points"
            ),
            SpecializedReward(
                reward_type=ChallengeRewardType.BADGE,
                value="monthly_creative_participant",
                description="Monthly Creative Participant Badge"
            )
        ]
        
        self.monthly_challenges[challenge.challenge_id] = challenge
        logger.info(f"Created monthly creative challenge: {title}")
        
        return challenge
    
    async def create_seo_challenge(
        self,
        title: str,
        description: str = "",
        target_improvement: float = 20.0,
        **kwargs
    ) -> TechnicalChallenge:
        """Create a new SEO optimization challenge"""
        
        challenge = TechnicalChallenge(
            title=title,
            description=description,
            technical_focus="seo",
            **kwargs
        )
        
        # Set SEO-specific targets
        challenge.seo_targets.update({
            "ranking_improvement": target_improvement,
            "organic_traffic_increase": target_improvement * 1.5,
            "keyword_optimization_count": 10,
            "content_quality_score": 85
        })
        
        # Set up SEO challenge rewards
        challenge.achievement_rewards = [
            SpecializedReward(
                reward_type=ChallengeRewardType.POINTS,
                value=500,
                description="SEO Master Achievement"
            ),
            SpecializedReward(
                reward_type=ChallengeRewardType.BADGE,
                value="seo_optimizer",
                description="SEO Optimizer Badge"
            ),
            SpecializedReward(
                reward_type=ChallengeRewardType.FEATURE_UNLOCK,
                value="advanced_seo_tools",
                description="Unlock Advanced SEO Tools"
            )
        ]
        
        self.technical_challenges[challenge.challenge_id] = challenge
        logger.info(f"Created SEO challenge: {title}")
        
        return challenge
    
    async def create_revenue_challenge(
        self,
        title: str,
        description: str = "",
        target_increase: float = 50.0,
        **kwargs
    ) -> TechnicalChallenge:
        """Create a new revenue optimization challenge"""
        
        challenge = TechnicalChallenge(
            title=title,
            description=description,
            technical_focus="revenue_optimization",
            **kwargs
        )
        
        # Set revenue-specific targets
        challenge.revenue_targets.update({
            "revenue_increase_percentage": target_increase,
            "new_revenue_streams": 2,
            "monetization_optimization": 25.0,
            "conversion_rate_improvement": 15.0
        })
        
        # Set up revenue challenge rewards
        challenge.achievement_rewards = [
            SpecializedReward(
                reward_type=ChallengeRewardType.CASH_PRIZE,
                value=Decimal('300'),
                description="Revenue Optimization Achievement Prize"
            ),
            SpecializedReward(
                reward_type=ChallengeRewardType.BADGE,
                value="revenue_optimizer",
                description="Revenue Optimizer Badge"
            ),
            SpecializedReward(
                reward_type=ChallengeRewardType.PLATFORM_BOOST,
                value="revenue_multiplier_1.2x",
                description="1.2x Revenue Multiplier for 30 days"
            )
        ]
        
        self.technical_challenges[challenge.challenge_id] = challenge
        logger.info(f"Created revenue challenge: {title}")
        
        return challenge
    
    async def create_global_competition(
        self,
        title: str,
        event_type: str,
        description: str = "",
        prize_pool: Union[int, Decimal] = Decimal('10000'),
        **kwargs
    ) -> GlobalCompetition:
        """Create a new global competition"""
        
        competition = GlobalCompetition(
            title=title,
            description=description,
            event_type=event_type,
            total_prize_pool=Decimal(str(prize_pool)),
            **kwargs
        )
        
        # Set up global competition structure
        competition.participating_regions = [
            "North America", "Europe", "Asia-Pacific", "Latin America", 
            "Middle East", "Africa", "Oceania"
        ]
        
        competition.language_support = [
            "en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko", "ar"
        ]
        
        # Set up massive prize distribution
        total_pool = competition.total_prize_pool
        competition.prize_distribution = {
            "first_place": SpecializedReward(
                reward_type=ChallengeRewardType.CASH_PRIZE,
                value=total_pool * Decimal('0.3'),
                description="Global Competition Grand Champion"
            ),
            "second_place": SpecializedReward(
                reward_type=ChallengeRewardType.CASH_PRIZE,
                value=total_pool * Decimal('0.2'),
                description="Global Competition Runner-up"
            ),
            "third_place": SpecializedReward(
                reward_type=ChallengeRewardType.CASH_PRIZE,
                value=total_pool * Decimal('0.1'),
                description="Global Competition Third Place"
            ),
            "regional_winners": SpecializedReward(
                reward_type=ChallengeRewardType.CASH_PRIZE,
                value=total_pool * Decimal('0.25') / 7,  # Divided among 7 regions
                description="Regional Champion Prize"
            ),
            "participation_pool": SpecializedReward(
                reward_type=ChallengeRewardType.POINTS,
                value=1000,
                description="Global Competition Participation Reward"
            )
        }
        
        self.global_competitions[competition.competition_id] = competition
        logger.info(f"Created global competition: {title}")
        
        return competition
    
    async def get_active_monthly_challenges(self) -> List[MonthlyCreativeChallenge]:
        """Get all active monthly creative challenges"""
        now = datetime.now(timezone.utc)
        active = []
        
        for challenge in self.monthly_challenges.values():
            if challenge.start_date <= now <= challenge.end_date:
                active.append(challenge)
        
        return active
    
    async def get_active_technical_challenges(self) -> List[TechnicalChallenge]:
        """
Get all active technical challenges"""
        now = datetime.now(timezone.utc)
        active = []
        
        for challenge in self.technical_challenges.values():
            if challenge.start_date <= now <= challenge.end_date:
                active.append(challenge)
        
        return active
    
    async def get_active_global_competitions(self) -> List[GlobalCompetition]:
        """
Get all active global competitions"""
        now = datetime.now(timezone.utc)
        active = []
        
        for competition in self.global_competitions.values():
            if (competition.registration_start <= now <= competition.competition_end or
                competition.competition_start <= now <= competition.competition_end):
                active.append(competition)
        
        return active
    
    async def get_challenge_analytics(self) -> Dict[str, Any]:
        """
Get analytics for specialized challenges"""
        return {
            "monthly_challenges": {
                "total": len(self.monthly_challenges),
                "active": len(await self.get_active_monthly_challenges()),
                "total_participants": sum(len(c.participants) for c in self.monthly_challenges.values())
            },
            "technical_challenges": {
                "total": len(self.technical_challenges),
                "active": len(await self.get_active_technical_challenges()),
                "seo_challenges": len([c for c in self.technical_challenges.values() 
                                    if c.technical_focus == "seo"]),
                "revenue_challenges": len([c for c in self.technical_challenges.values() 
                                         if c.technical_focus == "revenue_optimization"])
            },
            "global_competitions": {
                "total": len(self.global_competitions),
                "active": len(await self.get_active_global_competitions()),
                "total_prize_pool": sum(c.total_prize_pool for c in self.global_competitions.values()),
                "regional_participation": {}
            }
        }


# Default challenge templates for immediate use
async def create_default_specialized_challenges() -> SpecializedChallengeManager:
    """Create default specialized challenges for the platform"""
    manager = SpecializedChallengeManager()
    
    # Create January 2025 Creative Challenge
    await manager.create_monthly_creative_challenge(
        title="January 2025 Creative Revolution",
        theme="New Year Innovation",
        description="Start the year with groundbreaking creative content that showcases innovation and originality",
        content_requirements={
            "min_duration": 30,  # seconds
            "formats_allowed": ["video", "audio", "image", "text"],
            "innovation_required": True
        },
        creative_constraints=[
            "Must incorporate AI tools or techniques",
            "Must be original content",
            "Must include user interaction element"
        ]
    )
    
    # Create SEO Mastery Challenge
    await manager.create_seo_challenge(
        title="SEO Mastery Challenge",
        description="Improve your content's search engine optimization and organic reach",
        target_improvement=30.0
    )
    
    # Create Revenue Boost Challenge
    await manager.create_revenue_challenge(
        title="Revenue Boost Challenge",
        description="Optimize your monetization strategy and increase earnings by 50%",
        target_increase=50.0
    )
    
    # Create Global Winter Competition
    await manager.create_global_competition(
        title="Global Winter Creative Championship 2025",
        event_type="seasonal",
        description="The ultimate global creative competition bringing together creators from around the world",
        prize_pool=Decimal('25000')
    )
    
    logger.info("Default specialized challenges created successfully")
    return manager
