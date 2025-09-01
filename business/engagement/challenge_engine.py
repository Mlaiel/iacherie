"""Enterprise Challenge Engine - Advanced creative challenge system for IA Influencer platform.

This module provides a comprehensive challenge management system that creates
engaging creative challenges, competitions, and collaborative events for
multi-format content creators.

Architecture: Enterprise Production-Ready (Backend Level 2)
Module: backend/business/engagement/challenge_engine.py
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
Challenge Participation → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import random

logger = logging.getLogger(__name__)


class ChallengeType(str, Enum):
    """
Types of challenges available in the system."""

    CREATIVE = "creative"
    TECHNICAL = "technical"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    EDUCATIONAL = "educational"
    COMMUNITY = "community"
    SEASONAL = "seasonal"
    MILESTONE = "milestone"
    # Specialized challenge types for requirements
    MONTHLY_CREATIVE = "monthly_creative"
    TECHNICAL_SEO = "technical_seo"
    TECHNICAL_REVENUE = "technical_revenue"
    GLOBAL_COMPETITION = "global_competition"
    SPECIAL_EVENT = "special_event"


class ChallengeDifficulty(str, Enum):
    """Difficulty levels for challenges."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class ChallengeStatus(str, Enum):
    """Status of a challenge."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ParticipationStatus(str, Enum):
    """Status of user participation in a challenge."""

    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    FAILED = "failed"
    DISQUALIFIED = "disqualified"


class ContentFormat(str, Enum):
    """Content formats for challenges."""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    MIXED_MEDIA = "mixed_media"


@dataclass
class ChallengeReward:
    """Represents rewards for challenge completion."""
    reward_id: str = field(default_factory=lambda: str(uuid4()))
    reward_type: str = "points"  # points, badge, currency, premium_feature, etc.
    value: Union[int, str, Dict[str, Any]] = 0
    description: str = ""
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    unlock_conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChallengeCriteria:
    """Evaluation criteria for challenges."""
    criterion_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    weight: float = 1.0  # Weighting for this criterion in overall score
    max_score: int = 100
    auto_evaluate: bool = False  # Whether this can be automatically evaluated
    evaluation_method: str = "manual"  # manual, ai_analysis, metric_based


@dataclass
class Challenge:
    """Represents a challenge in the system."""
    challenge_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    challenge_type: ChallengeType = ChallengeType.CREATIVE
    difficulty: ChallengeDifficulty = ChallengeDifficulty.BEGINNER
    status: ChallengeStatus = ChallengeStatus.DRAFT
    
    # Content requirements
    content_formats: List[ContentFormat] = field(default_factory=list)
    content_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = None
    
    # Participation
    max_participants: Optional[int] = None
    min_participants: int = 1
    team_challenge: bool = False
    max_team_size: int = 1
    
    # Evaluation
    evaluation_criteria: List[ChallengeCriteria] = field(default_factory=list)
    auto_evaluation: bool = False
    community_voting: bool = False
    expert_review: bool = False
    
    # Rewards
    completion_rewards: List[ChallengeReward] = field(default_factory=list)
    ranking_rewards: Dict[str, List[ChallengeReward]] = field(default_factory=dict)  # position -> rewards
    participation_rewards: List[ChallengeReward] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    creator_types: List[str] = field(default_factory=list)  # Which creator types can participate
    skill_requirements: List[str] = field(default_factory=list)
    platform_requirements: List[str] = field(default_factory=list)
    
    # Stats
    participant_count: int = 0
    submission_count: int = 0
    completion_rate: float = 0.0
    average_rating: float = 0.0
    
    # Administrative
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_active(self) -> bool:
        """Check if the challenge is currently active."""
        if self.status != ChallengeStatus.ACTIVE:
            return False
        
        now = datetime.utcnow()
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def can_register(self) -> bool:
        """
Check if new participants can register."""
        if not self.is_active():
            return False
        
        if self.max_participants and self.participant_count >= self.max_participants:
            return False
        
        return True
    
    def get_time_remaining(self) -> Optional[timedelta]:
        """
Get time remaining in the challenge."""
        if not self.end_date:
            return None
        
        now = datetime.utcnow()
        if now >= self.end_date:
            return timedelta(0)
        
        return self.end_date - now


@dataclass
class ChallengeParticipation:
    """
Represents a user's participation in a challenge."""
    participation_id: str = field(default_factory=lambda: str(uuid4()))
    challenge_id: str = ""
    user_id: str = ""
    team_id: Optional[str] = None
    status: ParticipationStatus = ParticipationStatus.REGISTERED
    
    # Progress
    progress_percentage: float = 0.0
    milestones_completed: List[str] = field(default_factory=list)
    
    # Submission
    submission_id: Optional[str] = None
    submission_data: Dict[str, Any] = field(default_factory=dict)
    submission_date: Optional[datetime] = None
    
    # Evaluation
    scores: Dict[str, float] = field(default_factory=dict)  # criterion_id -> score
    total_score: float = 0.0
    ranking_position: Optional[int] = None
    
    # Rewards
    rewards_earned: List[ChallengeReward] = field(default_factory=list)
    rewards_claimed: List[str] = field(default_factory=list)
    
    # Metadata
    registered_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def is_completed(self) -> bool:
        """Check if participation is completed."""
        return self.status in [ParticipationStatus.COMPLETED, ParticipationStatus.SUBMITTED]
    
    def can_submit(self) -> bool:
        """
Check if user can submit for this challenge."""
        return self.status in [ParticipationStatus.REGISTERED, ParticipationStatus.IN_PROGRESS]


class ChallengeEngine:
    """
    Enterprise-grade challenge management system.
    
    Manages creative challenges, competitions, and collaborative events
    to drive user engagement and skill development.
    """
    
    def __init__(self):
        """
Initialize the challenge engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._challenges: Dict[str, Challenge] = {}
        self._participations: Dict[str, ChallengeParticipation] = {}
        self._challenge_templates = self._initialize_challenge_templates()
        
        self.logger.info("ChallengeEngine initialized successfully")
    
    def _initialize_challenge_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined challenge templates."""
        templates = {
            "30_day_challenge": {
                "title": "30-Day Content Creation Challenge",
                "description": "Create and upload content every day for 30 consecutive days",
                "challenge_type": ChallengeType.CREATIVE,
                "difficulty": ChallengeDifficulty.INTERMEDIATE,
                "duration_days": 30,
                "content_formats": [ContentFormat.AUDIO, ContentFormat.VIDEO, ContentFormat.IMAGE],
                "auto_evaluation": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="points",
                        value=5000,
                        description="30-Day Consistency Champion"
                    ),
                    ChallengeReward(
                        reward_type="badge",
                        value="consistency_master",
                        description="Consistency Master Badge"
                    )
                ]
            },
            
            "style_transfer": {
                "title": "Style Transfer Challenge",
                "description": "Adapt your content to match a different genre or style",
                "challenge_type": ChallengeType.CREATIVE,
                "difficulty": ChallengeDifficulty.ADVANCED,
                "duration_days": 14,
                "content_formats": [ContentFormat.AUDIO, ContentFormat.VIDEO],
                "expert_review": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="points",
                        value=2500,
                        description="Style Innovation Award"
                    )
                ]
            },
            
            "remix_battle": {
                "title": "Remix Battle Competition",
                "description": "Create the best remix of provided source material",
                "challenge_type": ChallengeType.COMPETITIVE,
                "difficulty": ChallengeDifficulty.INTERMEDIATE,
                "duration_days": 7,
                "content_formats": [ContentFormat.AUDIO],
                "community_voting": True,
                "ranking_rewards": {
                    "1": [ChallengeReward(reward_type="currency", value=1000, description="First Place Prize")],
                    "2": [ChallengeReward(reward_type="currency", value=500, description="Second Place Prize")],
                    "3": [ChallengeReward(reward_type="currency", value=250, description="Third Place Prize")]
                }
            },
            
            "collab_race": {
                "title": "Collaboration Race",
                "description": "Complete the most successful collaborations in one month",
                "challenge_type": ChallengeType.COLLABORATIVE,
                "difficulty": ChallengeDifficulty.INTERMEDIATE,
                "duration_days": 30,
                "auto_evaluation": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="badge",
                        value="collaboration_champion",
                        description="Collaboration Champion Badge"
                    )
                ]
            },
            
            "viral_challenge": {
                "title": "Viral Content Challenge",
                "description": "Be the first to reach 1 million views/plays",
                "challenge_type": ChallengeType.COMPETITIVE,
                "difficulty": ChallengeDifficulty.EXPERT,
                "duration_days": 60,
                "auto_evaluation": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="points",
                        value=10000,
                        description="Viral Sensation Achievement"
                    ),
                    ChallengeReward(
                        reward_type="premium_feature",
                        value="viral_boost_package",
                        description="Viral Boost Premium Package"
                    )
                ]
            },
            
            "seo_master": {
                "title": "SEO Mastery Challenge",
                "description": "Improve your content's search ranking by 50% in 30 days",
                "challenge_type": ChallengeType.TECHNICAL,
                "difficulty": ChallengeDifficulty.ADVANCED,
                "duration_days": 30,
                "auto_evaluation": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="badge",
                        value="seo_specialist",
                        description="SEO Specialist Badge"
                    )
                ]
            },
            
            "revenue_boost": {
                "title": "Revenue Boost Challenge",
                "description": "Increase monthly revenue by 50% compared to previous month",
                "challenge_type": ChallengeType.TECHNICAL,
                "difficulty": ChallengeDifficulty.ADVANCED,
                "duration_days": 30,
                "auto_evaluation": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="points",
                        value=7500,
                        description="Revenue Growth Achievement"
                    )
                ]
            },
            
            "global_reach": {
                "title": "Global Reach Challenge",
                "description": "Expand your audience to 10+ countries",
                "challenge_type": ChallengeType.TECHNICAL,
                "difficulty": ChallengeDifficulty.INTERMEDIATE,
                "duration_days": 45,
                "auto_evaluation": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="badge",
                        value="global_influencer",
                        description="Global Influencer Badge"
                    )
                ]
            },
            
            "quality_quest": {
                "title": "Quality Quest",
                "description": "Maintain 98%+ quality score for all content uploads",
                "challenge_type": ChallengeType.TECHNICAL,
                "difficulty": ChallengeDifficulty.EXPERT,
                "duration_days": 30,
                "auto_evaluation": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="badge",
                        value="quality_pioneer",
                        description="Quality Pioneer Badge"
                    )
                ]
            },
            
            "innovation_lab": {
                "title": "Innovation Lab Challenge",
                "description": "Use 5+ new platform features in your content",
                "challenge_type": ChallengeType.EDUCATIONAL,
                "difficulty": ChallengeDifficulty.BEGINNER,
                "duration_days": 21,
                "auto_evaluation": True,
                "completion_rewards": [
                    ChallengeReward(
                        reward_type="badge",
                        value="innovation_adopter",
                        description="Innovation Adopter Badge"
                    )
                ]
            }
        }
        
        return templates
    
    async def create_challenge(
        self,
        template_name: Optional[str] = None,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Challenge:
        """Create a new challenge from template or custom parameters."""
        try:
            if template_name and template_name in self._challenge_templates:
                # Create from template
                template = self._challenge_templates[template_name].copy()
                
                # Apply custom overrides if provided
                if custom_params:
                    template.update(custom_params)
                
                challenge = Challenge(**template)
            
            elif custom_params:
                # Create custom challenge
                challenge = Challenge(**custom_params)
            
            else:
                raise ValueError("Either template_name or custom_params must be provided")
            
            # Set timing if not provided
            if not challenge.start_date and not challenge.end_date:
                challenge.start_date = datetime.utcnow()
                if challenge.duration_days:
                    challenge.end_date = challenge.start_date + timedelta(days=challenge.duration_days)
            
            # Initialize evaluation criteria if not provided
            if not challenge.evaluation_criteria:
                challenge.evaluation_criteria = self._create_default_criteria(challenge.challenge_type)
            
            # Store the challenge
            self._challenges[challenge.challenge_id] = challenge
            
            self.logger.info(f"Created challenge: {challenge.title} (ID: {challenge.challenge_id})")
            return challenge
            
        except Exception as e:
            self.logger.error(f"Failed to create challenge: {e}")
            raise
    
    def _create_default_criteria(self, challenge_type: ChallengeType) -> List[ChallengeCriteria]:
        """Create default evaluation criteria based on challenge type."""
        criteria_by_type = {
            ChallengeType.CREATIVE: [
                ChallengeCriteria(
                    name="Creativity",
                    description="Originality and creative approach",
                    weight=0.4,
                    max_score=100
                ),
                ChallengeCriteria(
                    name="Technical Quality",
                    description="Technical execution and production quality",
                    weight=0.3,
                    max_score=100,
                    auto_evaluate=True,
                    evaluation_method="ai_analysis"
                ),
                ChallengeCriteria(
                    name="Audience Engagement",
                    description="Level of audience engagement generated",
                    weight=0.3,
                    max_score=100,
                    auto_evaluate=True,
                    evaluation_method="metric_based"
                )
            ],
            
            ChallengeType.TECHNICAL: [
                ChallengeCriteria(
                    name="Technical Achievement",
                    description="Meeting technical requirements and metrics",
                    weight=0.6,
                    max_score=100,
                    auto_evaluate=True,
                    evaluation_method="metric_based"
                ),
                ChallengeCriteria(
                    name="Implementation Quality",
                    description="Quality of technical implementation",
                    weight=0.4,
                    max_score=100,
                    auto_evaluate=True,
                    evaluation_method="ai_analysis"
                )
            ],
            
            ChallengeType.COLLABORATIVE: [
                ChallengeCriteria(
                    name="Collaboration Success",
                    description="Number and quality of successful collaborations",
                    weight=0.5,
                    max_score=100,
                    auto_evaluate=True,
                    evaluation_method="metric_based"
                ),
                ChallengeCriteria(
                    name="Team Contribution",
                    description="Individual contribution to team efforts",
                    weight=0.3,
                    max_score=100
                ),
                ChallengeCriteria(
                    name="Community Impact",
                    description="Positive impact on the community",
                    weight=0.2,
                    max_score=100
                )
            ],
            
            ChallengeType.COMPETITIVE: [
                ChallengeCriteria(
                    name="Performance",
                    description="Overall performance in the competition",
                    weight=0.7,
                    max_score=100,
                    auto_evaluate=True,
                    evaluation_method="metric_based"
                ),
                ChallengeCriteria(
                    name="Innovation",
                    description="Innovative approaches and techniques",
                    weight=0.3,
                    max_score=100
                )
            ]
        }
        
        return criteria_by_type.get(challenge_type, [
            ChallengeCriteria(
                name="Overall Quality",
                description="Overall quality of submission",
                weight=1.0,
                max_score=100
            )
        ])
    
    async def register_participant(
        self,
        challenge_id: str,
        user_id: str,
        team_id: Optional[str] = None
    ) -> ChallengeParticipation:
        """Register a user for a challenge."""
        try:
            if challenge_id not in self._challenges:
                raise ValueError(f"Challenge {challenge_id} not found")
            
            challenge = self._challenges[challenge_id]
            
            if not challenge.can_register():
                raise ValueError(f"Challenge {challenge_id} is not accepting registrations")
            
            # Check if user is already registered
            existing_participation = self._get_user_participation(challenge_id, user_id)
            if existing_participation:
                raise ValueError(f"User {user_id} already registered for challenge {challenge_id}")
            
            # Create participation record
            participation = ChallengeParticipation(
                challenge_id=challenge_id,
                user_id=user_id,
                team_id=team_id
            )
            
            # Store participation
            self._participations[participation.participation_id] = participation
            
            # Update challenge stats
            challenge.participant_count += 1
            challenge.updated_at = datetime.utcnow()
            
            self.logger.info(f"Registered user {user_id} for challenge {challenge_id}")
            return participation
            
        except Exception as e:
            self.logger.error(f"Failed to register participant: {e}")
            raise
    
    def _get_user_participation(
        self,
        challenge_id: str,
        user_id: str
    ) -> Optional[ChallengeParticipation]:
        """Get user's participation in a specific challenge."""
        for participation in self._participations.values():
            if (participation.challenge_id == challenge_id and 
                participation.user_id == user_id):
                return participation
        return None
    
    async def submit_challenge_entry(
        self,
        challenge_id: str,
        user_id: str,
        submission_data: Dict[str, Any]
    ) -> bool:
        """
Submit an entry for a challenge."""
        try:
            participation = self._get_user_participation(challenge_id, user_id)
            if not participation:
                raise ValueError(f"User {user_id} not registered for challenge {challenge_id}")
            
            if not participation.can_submit():
                raise ValueError(f"User {user_id} cannot submit for challenge {challenge_id}")
            
            challenge = self._challenges[challenge_id]
            if not challenge.is_active():
                raise ValueError(f"Challenge {challenge_id} is not active")
            
            # Update participation
            participation.submission_data = submission_data
            participation.submission_date = datetime.utcnow()
            participation.submission_id = str(uuid4())
            participation.status = ParticipationStatus.SUBMITTED
            
            if not participation.started_at:
                participation.started_at = datetime.utcnow()
            
            # Update challenge stats
            challenge.submission_count += 1
            challenge.updated_at = datetime.utcnow()
            
            # Trigger evaluation if auto-evaluation is enabled
            if challenge.auto_evaluation:
                await self._auto_evaluate_submission(challenge, participation)
            
            self.logger.info(f"Submitted entry for user {user_id} in challenge {challenge_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to submit challenge entry: {e}")
            return False
    
    async def _auto_evaluate_submission(
        self,
        challenge: Challenge,
        participation: ChallengeParticipation
    ) -> None:
        """Automatically evaluate a challenge submission."""
        try:
            total_score = 0.0
            total_weight = 0.0
            
            for criterion in challenge.evaluation_criteria:
                if criterion.auto_evaluate:
                    score = await self._evaluate_criterion(criterion, participation, challenge)
                    participation.scores[criterion.criterion_id] = score
                    total_score += score * criterion.weight
                    total_weight += criterion.weight
            
            # Calculate overall score
            if total_weight > 0:
                participation.total_score = total_score / total_weight
            
            # Check for completion
            if len(participation.scores) == len(challenge.evaluation_criteria):
                participation.status = ParticipationStatus.COMPLETED
                participation.completed_at = datetime.utcnow()
                
                # Award completion rewards
                await self._award_completion_rewards(challenge, participation)
            
            self.logger.debug(f"Auto-evaluated submission for user {participation.user_id}: score {participation.total_score}")
            
        except Exception as e:
            self.logger.error(f"Failed to auto-evaluate submission: {e}")
    
    async def _evaluate_criterion(
        self,
        criterion: ChallengeCriteria,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> float:
        """Evaluate a specific criterion for a submission."""
        try:
            if criterion.evaluation_method == "metric_based":
                return await self._evaluate_metric_based_criterion(criterion, participation, challenge)
            elif criterion.evaluation_method == "ai_analysis":
                return await self._evaluate_ai_based_criterion(criterion, participation, challenge)
            else:
                # Manual evaluation - return default score for now
                return 70.0
                
        except Exception as e:
            self.logger.error(f"Failed to evaluate criterion {criterion.name}: {e}")
            return 0.0
    
    async def _evaluate_metric_based_criterion(
        self,
        criterion: ChallengeCriteria,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> float:
        """Evaluate criterion based on metrics."""
        # This would integrate with actual metrics from the platform
        # For now, return simulated scores based on submission data
        
        submission_data = participation.submission_data
        
        if "engagement_rate" in submission_data:
            engagement_rate = submission_data["engagement_rate"]
            # Convert engagement rate to score (0-100)
            score = min(100, engagement_rate * 4)  # 25% engagement = 100 score
            return score
        
        elif "quality_score" in submission_data:
            return min(100, submission_data["quality_score"])
        
        elif "collaboration_count" in submission_data:
            collab_count = submission_data["collaboration_count"]
            # Scale collaboration count to score
            score = min(100, collab_count * 10)  # 10 collaborations = 100 score
            return score
        
        elif "revenue_improvement" in submission_data:
            improvement = submission_data["revenue_improvement"]
            # Convert percentage improvement to score
            score = min(100, improvement * 2)  # 50% improvement = 100 score
            return score
        
        # Default scoring
        return random.uniform(60, 95)
    
    async def _evaluate_ai_based_criterion(
        self,
        criterion: ChallengeCriteria,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> float:
        """Evaluate criterion using AI analysis."""
        # This would integrate with AI analysis services
        # For now, return simulated AI scores
        
        submission_data = participation.submission_data
        
        # Simulate AI evaluation based on content type and quality indicators
        base_score = 75.0
        
        if "content_url" in submission_data:
            # Simulate AI content analysis
            content_quality_factors = [
                submission_data.get("audio_quality", 0.8),
                submission_data.get("visual_quality", 0.8),
                submission_data.get("technical_quality", 0.8),
                submission_data.get("creative_score", 0.8)
            ]
            
            avg_quality = sum(content_quality_factors) / len(content_quality_factors)
            base_score = avg_quality * 100
        
        # Add some randomization to simulate AI variability
        score = base_score + random.uniform(-10, 10)
        return max(0, min(100, score))
    
    async def _award_completion_rewards(
        self,
        challenge: Challenge,
        participation: ChallengeParticipation
    ) -> None:
        """Award rewards for challenge completion."""
        try:
            # Award completion rewards
            for reward in challenge.completion_rewards:
                participation.rewards_earned.append(reward)
            
            # Check for ranking rewards (if this is a competitive challenge)
            if challenge.challenge_type == ChallengeType.COMPETITIVE:
                ranking = await self._calculate_user_ranking(challenge, participation)
                participation.ranking_position = ranking
                
                ranking_str = str(ranking)
                if ranking_str in challenge.ranking_rewards:
                    for reward in challenge.ranking_rewards[ranking_str]:
                        participation.rewards_earned.append(reward)
            
            self.logger.info(
                f"Awarded {len(participation.rewards_earned)} rewards to user "
                f"{participation.user_id} for challenge {challenge.challenge_id}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to award completion rewards: {e}")
    
    async def _calculate_user_ranking(
        self,
        challenge: Challenge,
        participation: ChallengeParticipation
    ) -> int:
        """Calculate user's ranking in a competitive challenge."""
        # Get all completed participations for this challenge
        completed_participations = [
            p for p in self._participations.values()
            if p.challenge_id == challenge.challenge_id and p.is_completed()
        ]
        
        # Sort by total score (descending)
        completed_participations.sort(key=lambda p: p.total_score, reverse=True)
        
        # Find user's position
        for i, p in enumerate(completed_participations):
            if p.participation_id == participation.participation_id:
                return i + 1
        
        return len(completed_participations) + 1
    
    async def get_active_challenges(
        self,
        user_id: Optional[str] = None,
        challenge_type: Optional[ChallengeType] = None,
        difficulty: Optional[ChallengeDifficulty] = None
    ) -> List[Challenge]:
        """
Get list of active challenges with optional filtering."""
        challenges = []
        
        for challenge in self._challenges.values():
            if not challenge.is_active():
                continue
            
            if challenge_type and challenge.challenge_type != challenge_type:
                continue
            
            if difficulty and challenge.difficulty != difficulty:
                continue
            
            # If user_id provided, check if user can participate
            if user_id:
                existing_participation = self._get_user_participation(challenge.challenge_id, user_id)
                if existing_participation and existing_participation.is_completed():
                    continue  # Skip completed challenges
            
            challenges.append(challenge)
        
        # Sort by creation date (newest first)
        challenges.sort(key=lambda c: c.created_at, reverse=True)
        
        return challenges
    
    async def get_user_challenges(
        self,
        user_id: str,
        status_filter: Optional[ParticipationStatus] = None
    ) -> List[Tuple[Challenge, ChallengeParticipation]]:
        """
Get challenges that a user is participating in."""
        user_challenges = []
        
        for participation in self._participations.values():
            if participation.user_id != user_id:
                continue
            
            if status_filter and participation.status != status_filter:
                continue
            
            challenge = self._challenges.get(participation.challenge_id)
            if challenge:
                user_challenges.append((challenge, participation))
        
        # Sort by registration date (newest first)
        user_challenges.sort(key=lambda x: x[1].registered_at, reverse=True)
        
        return user_challenges
    
    async def get_challenge_leaderboard(
        self,
        challenge_id: str,
        limit: int = 50
    ) -> List[Tuple[ChallengeParticipation, int]]:
        """
Get leaderboard for a specific challenge."""
        if challenge_id not in self._challenges:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        # Get all participations for this challenge
        participations = [
            p for p in self._participations.values()
            if p.challenge_id == challenge_id and p.is_completed()
        ]
        
        # Sort by total score (descending)
        participations.sort(key=lambda p: p.total_score, reverse=True)
        
        # Create leaderboard with rankings
        leaderboard = []
        for i, participation in enumerate(participations[:limit]):
            leaderboard.append((participation, i + 1))
        
        return leaderboard
    
    async def get_challenge_statistics(self, challenge_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a challenge."""
        if challenge_id not in self._challenges:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        challenge = self._challenges[challenge_id]
        
        # Get all participations
        participations = [
            p for p in self._participations.values()
            if p.challenge_id == challenge_id
        ]
        
        completed_participations = [p for p in participations if p.is_completed()]
        
        # Calculate statistics
        completion_rate = (len(completed_participations) / len(participations) * 100) if participations else 0
        
        average_score = 0.0
        if completed_participations:
            total_scores = [p.total_score for p in completed_participations]
            average_score = sum(total_scores) / len(total_scores)
        
        return {
            "challenge_id": challenge_id,
            "title": challenge.title,
            "status": challenge.status,
            "is_active": challenge.is_active(),
            "time_remaining": challenge.get_time_remaining().total_seconds() if challenge.get_time_remaining() else None,
            "participants": {
                "total": len(participations),
                "completed": len(completed_participations),
                "completion_rate": completion_rate
            },
            "performance": {
                "average_score": average_score,
                "submissions": challenge.submission_count
            },
            "timing": {
                "start_date": challenge.start_date.isoformat() if challenge.start_date else None,
                "end_date": challenge.end_date.isoformat() if challenge.end_date else None,
                "duration_days": challenge.duration_days
            }
        }
    
    async def update_challenge_progress(
        self,
        challenge_id: str,
        user_id: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """Update user's progress in a challenge."""
        try:
            participation = self._get_user_participation(challenge_id, user_id)
            if not participation:
                raise ValueError(f"User {user_id} not registered for challenge {challenge_id}")
            
            # Update progress
            if "progress_percentage" in progress_data:
                participation.progress_percentage = min(100, max(0, progress_data["progress_percentage"]))
            
            if "milestones_completed" in progress_data:
                new_milestones = progress_data["milestones_completed"]
                for milestone in new_milestones:
                    if milestone not in participation.milestones_completed:
                        participation.milestones_completed.append(milestone)
            
            # Update status based on progress
            if not participation.started_at and participation.progress_percentage > 0:
                participation.started_at = datetime.utcnow()
                participation.status = ParticipationStatus.IN_PROGRESS
            
            self.logger.debug(f"Updated progress for user {user_id} in challenge {challenge_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update challenge progress: {e}")
            return False
    
    async def get_recommended_challenges(
        self,
        user_id: str,
        user_profile: Dict[str, Any],
        limit: int = 10
    ) -> List[Tuple[Challenge, float]]:
        """Get personalized challenge recommendations for a user."""
        active_challenges = await self.get_active_challenges(user_id=user_id)
        
        recommendations = []
        
        for challenge in active_challenges:
            # Calculate recommendation score based on user profile
            score = await self._calculate_recommendation_score(challenge, user_profile)
            recommendations.append((challenge, score))
        
        # Sort by recommendation score (highest first)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:limit]
    
    async def _calculate_recommendation_score(
        self,
        challenge: Challenge,
        user_profile: Dict[str, Any]
    ) -> float:
        """
Calculate recommendation score for a challenge based on user profile."""
        score = 0.0
        
        # Difficulty matching
        user_level = user_profile.get("level", 1)
        difficulty_match = {
            ChallengeDifficulty.BEGINNER: (1, 10),
            ChallengeDifficulty.INTERMEDIATE: (8, 25),
            ChallengeDifficulty.ADVANCED: (20, 50),
            ChallengeDifficulty.EXPERT: (40, 75),
            ChallengeDifficulty.MASTER: (70, 100)
        }
        
        min_level, max_level = difficulty_match.get(challenge.difficulty, (1, 100))
        if min_level <= user_level <= max_level:
            score += 30.0
        elif user_level < min_level:
            score += max(0, 30.0 - (min_level - user_level) * 2)
        else:
            score += max(0, 30.0 - (user_level - max_level) * 0.5)
        
        # Content format matching
        user_formats = set(user_profile.get("content_formats", []))
        challenge_formats = set([f.value for f in challenge.content_formats])
        
        if user_formats & challenge_formats:
            score += 25.0
        
        # Creator type matching
        user_creator_type = user_profile.get("creator_type", "")
        if user_creator_type in challenge.creator_types:
            score += 20.0
        
        # Skill matching
        user_skills = set(user_profile.get("skills", []))
        challenge_skills = set(challenge.skill_requirements)
        
        skill_overlap = len(user_skills & challenge_skills)
        if skill_overlap > 0:
            score += min(15.0, skill_overlap * 3)
        
        # Challenge type preference (based on past participation)
        past_types = user_profile.get("preferred_challenge_types", [])
        if challenge.challenge_type.value in past_types:
            score += 10.0
        
        return score


# Global challenge engine instance
_challenge_engine: Optional[ChallengeEngine] = None


async def get_challenge_engine() -> ChallengeEngine:
    """Get the global challenge engine instance."""
    global _challenge_engine
    
    if _challenge_engine is None:
        _challenge_engine = ChallengeEngine()
    
    return _challenge_engine


# Convenience functions for common operations
async def create_challenge_from_template(
    template_name: str,
    custom_params: Optional[Dict[str, Any]] = None
) -> Challenge:
    """
Create a challenge from a template (convenience function)."""
    engine = await get_challenge_engine()
    return await engine.create_challenge(template_name, custom_params)


async def register_for_challenge(
    challenge_id: str,
    user_id: str,
    team_id: Optional[str] = None
) -> ChallengeParticipation:
    """
Register a user for a challenge (convenience function)."""
    engine = await get_challenge_engine()
    return await engine.register_participant(challenge_id, user_id, team_id)