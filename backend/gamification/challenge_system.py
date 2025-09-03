"""Advanced Challenge System - Dynamic Challenge Management Engine
================================================================

Sophisticated challenge creation and management system providing dynamic
challenge generation, progress tracking, competitive events, and
comprehensive challenge analytics for content creators.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/challenge_system.py
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
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import random
from statistics import mean

logger = logging.getLogger(__name__)


class ChallengeType(str, Enum):
    """Types of challenges."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    CREATIVE = "creative"
    SKILL_BASED = "skill_based"


class ChallengeDifficulty(str, Enum):
    """Challenge difficulty levels."""
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"


class ChallengeStatus(str, Enum):
    """Challenge status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ParticipationStatus(str, Enum):
    """User participation status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class ChallengeRequirement:
    """Individual challenge requirement."""
    id: str
    description: str
    metric_key: str
    target_value: Union[int, float]
    comparison_type: str = "greater_equal"  # greater_equal, equal, less_equal
    weight: float = 1.0
    is_optional: bool = False


@dataclass
class ChallengeReward:
    """Challenge reward definition."""
    reward_type: str
    amount: Union[int, float, Decimal]
    currency: str = "CREDITS"
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Challenge:
    """Complete challenge definition."""
    id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    requirements: List[ChallengeRequirement]
    rewards: List[ChallengeReward]
    status: ChallengeStatus
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int] = None
    current_participants: int = 0
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


@dataclass
class ChallengeParticipation:
    """User challenge participation tracking."""
    id: str
    user_id: str
    challenge_id: str
    status: ParticipationStatus
    progress_data: Dict[str, Union[int, float]]
    completion_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChallengeTemplate:
    """Template for generating challenges."""
    id: str
    name: str
    title_template: str
    description_template: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    requirement_templates: List[Dict[str, Any]]
    reward_templates: List[Dict[str, Any]]
    duration_days: int
    tags: List[str] = field(default_factory=list)


class ChallengeSystem:
    """
    Advanced challenge management system providing dynamic challenge
    creation, progress tracking, and comprehensive challenge analytics.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the challenge system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.active_challenges: Dict[str, Challenge] = {}
        self.user_participations: Dict[str, List[ChallengeParticipation]] = {}
        self.challenge_templates = self._initialize_challenge_templates()
        
        self.logger.info("ChallengeSystem initialized")
    
    def _initialize_challenge_templates(self) -> Dict[str, ChallengeTemplate]:
        """Initialize default challenge templates."""
        templates = {}
        
        # Daily challenges
        templates["daily_upload"] = ChallengeTemplate(
            id="daily_upload",
            name="Daily Content Upload",
            title_template="Daily Creator",
            description_template="Upload {count} pieces of content today",
            challenge_type=ChallengeType.DAILY,
            difficulty=ChallengeDifficulty.EASY,
            requirement_templates=[
                {
                    "metric_key": "daily_uploads",
                    "target_value": 1,
                    "description": "Upload content"
                }
            ],
            reward_templates=[
                {
                    "reward_type": "currency",
                    "amount": 50,
                    "currency": "CREDITS",
                    "description": "Daily upload bonus"
                }
            ],
            duration_days=1,
            tags=["daily", "content", "consistency"]
        )
        
        templates["daily_engagement"] = ChallengeTemplate(
            id="daily_engagement",
            name="Daily Engagement",
            title_template="Engagement Master",
            description_template="Achieve {rate}% engagement rate today",
            challenge_type=ChallengeType.DAILY,
            difficulty=ChallengeDifficulty.MEDIUM,
            requirement_templates=[
                {
                    "metric_key": "daily_engagement_rate",
                    "target_value": 15.0,
                    "description": "Achieve high engagement"
                }
            ],
            reward_templates=[
                {
                    "reward_type": "currency",
                    "amount": 100,
                    "currency": "CREDITS",
                    "description": "Engagement achievement bonus"
                }
            ],
            duration_days=1,
            tags=["daily", "engagement", "interaction"]
        )
        
        # Weekly challenges
        templates["weekly_consistency"] = ChallengeTemplate(
            id="weekly_consistency",
            name="Weekly Consistency",
            title_template="Consistent Creator",
            description_template="Upload content for {days} consecutive days",
            challenge_type=ChallengeType.WEEKLY,
            difficulty=ChallengeDifficulty.MEDIUM,
            requirement_templates=[
                {
                    "metric_key": "consecutive_upload_days",
                    "target_value": 5,
                    "description": "Upload for 5 consecutive days"
                }
            ],
            reward_templates=[
                {
                    "reward_type": "currency",
                    "amount": 500,
                    "currency": "CREDITS",
                    "description": "Consistency master bonus"
                }
            ],
            duration_days=7,
            tags=["weekly", "consistency", "dedication"]
        )
        
        templates["weekly_collaboration"] = ChallengeTemplate(
            id="weekly_collaboration",
            name="Weekly Collaboration",
            title_template="Team Player",
            description_template="Complete {count} collaborations this week",
            challenge_type=ChallengeType.WEEKLY,
            difficulty=ChallengeDifficulty.HARD,
            requirement_templates=[
                {
                    "metric_key": "weekly_collaborations",
                    "target_value": 3,
                    "description": "Complete 3 collaborations"
                }
            ],
            reward_templates=[
                {
                    "reward_type": "currency",
                    "amount": 300,
                    "currency": "COLLABORATION_COINS",
                    "description": "Collaboration champion bonus"
                }
            ],
            duration_days=7,
            tags=["weekly", "collaboration", "teamwork"]
        )
        
        # Monthly challenges
        templates["monthly_revenue"] = ChallengeTemplate(
            id="monthly_revenue",
            name="Monthly Revenue Goal",
            title_template="Revenue Champion",
            description_template="Generate ${amount} in revenue this month",
            challenge_type=ChallengeType.MONTHLY,
            difficulty=ChallengeDifficulty.EXPERT,
            requirement_templates=[
                {
                    "metric_key": "monthly_revenue",
                    "target_value": 500,
                    "description": "Generate $500 in revenue"
                }
            ],
            reward_templates=[
                {
                    "reward_type": "currency",
                    "amount": 2000,
                    "currency": "PREMIUM_POINTS",
                    "description": "Revenue achievement bonus"
                }
            ],
            duration_days=30,
            tags=["monthly", "revenue", "monetization"]
        )
        
        # Creative challenges
        templates["creative_diversity"] = ChallengeTemplate(
            id="creative_diversity",
            name="Creative Diversity",
            title_template="Multi-Platform Creator",
            description_template="Upload content to {count} different platforms",
            challenge_type=ChallengeType.CREATIVE,
            difficulty=ChallengeDifficulty.MEDIUM,
            requirement_templates=[
                {
                    "metric_key": "platforms_used",
                    "target_value": 5,
                    "description": "Use 5 different platforms"
                }
            ],
            reward_templates=[
                {
                    "reward_type": "currency",
                    "amount": 750,
                    "currency": "CREDITS",
                    "description": "Platform diversity bonus"
                }
            ],
            duration_days=14,
            tags=["creative", "diversity", "platforms"]
        )
        
        # Skill-based challenges
        templates["quality_master"] = ChallengeTemplate(
            id="quality_master",
            name="Quality Master",
            title_template="Quality Excellence",
            description_template="Achieve average quality score of {score}/10",
            challenge_type=ChallengeType.SKILL_BASED,
            difficulty=ChallengeDifficulty.HARD,
            requirement_templates=[
                {
                    "metric_key": "average_quality_score",
                    "target_value": 8.5,
                    "description": "Achieve high quality average"
                },
                {
                    "metric_key": "min_uploads_for_average",
                    "target_value": 10,
                    "description": "Minimum uploads required"
                }
            ],
            reward_templates=[
                {
                    "reward_type": "currency",
                    "amount": 150,
                    "currency": "QUALITY_CRYSTALS",
                    "description": "Quality excellence bonus"
                }
            ],
            duration_days=21,
            tags=["skill", "quality", "excellence"]
        )
        
        return templates
    
    async def create_challenge_from_template(
        self,
        template_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Optional[Challenge]:
        """Create a new challenge from a template."""
        try:
            if template_id not in self.challenge_templates:
                self.logger.error(f"Template not found: {template_id}")
                return None
            
            template = self.challenge_templates[template_id]
            customizations = customizations or {}
            
            # Generate challenge ID
            challenge_id = str(uuid4())
            
            # Build requirements from template
            requirements = []
            for i, req_template in enumerate(template.requirement_templates):
                requirement = ChallengeRequirement(
                    id=f"{challenge_id}_req_{i}",
                    description=req_template["description"],
                    metric_key=req_template["metric_key"],
                    target_value=req_template["target_value"],
                    comparison_type=req_template.get("comparison_type", "greater_equal"),
                    weight=req_template.get("weight", 1.0),
                    is_optional=req_template.get("is_optional", False)
                )
                requirements.append(requirement)
            
            # Build rewards from template
            rewards = []
            for reward_template in template.reward_templates:
                reward = ChallengeReward(
                    reward_type=reward_template["reward_type"],
                    amount=reward_template["amount"],
                    currency=reward_template.get("currency", "CREDITS"),
                    description=reward_template["description"]
                )
                rewards.append(reward)
            
            # Calculate dates
            start_date = customizations.get("start_date", datetime.utcnow())
            end_date = customizations.get("end_date", start_date + timedelta(days=template.duration_days))
            
            # Create challenge
            challenge = Challenge(
                id=challenge_id,
                title=customizations.get("title", template.title_template),
                description=customizations.get("description", template.description_template),
                challenge_type=template.challenge_type,
                difficulty=template.difficulty,
                requirements=requirements,
                rewards=rewards,
                status=ChallengeStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                max_participants=customizations.get("max_participants"),
                tags=template.tags.copy(),
                metadata=customizations.get("metadata", {})
            )
            
            # Store challenge
            self.active_challenges[challenge_id] = challenge
            
            self.logger.info(f"✅ Challenge created from template {template_id}: {challenge.title}")
            
            return challenge
            
        except Exception as e:
            self.logger.error(f"Error creating challenge from template: {e}")
            return None
    
    async def create_custom_challenge(
        self,
        title: str,
        description: str,
        challenge_type: ChallengeType,
        difficulty: ChallengeDifficulty,
        requirements: List[Dict[str, Any]],
        rewards: List[Dict[str, Any]],
        duration_days: int,
        created_by: Optional[str] = None,
        **kwargs
    ) -> Optional[Challenge]:
        """Create a custom challenge."""
        try:
            challenge_id = str(uuid4())
            
            # Build requirements
            challenge_requirements = []
            for i, req_data in enumerate(requirements):
                requirement = ChallengeRequirement(
                    id=f"{challenge_id}_req_{i}",
                    description=req_data["description"],
                    metric_key=req_data["metric_key"],
                    target_value=req_data["target_value"],
                    comparison_type=req_data.get("comparison_type", "greater_equal"),
                    weight=req_data.get("weight", 1.0),
                    is_optional=req_data.get("is_optional", False)
                )
                challenge_requirements.append(requirement)
            
            # Build rewards
            challenge_rewards = []
            for reward_data in rewards:
                reward = ChallengeReward(
                    reward_type=reward_data["reward_type"],
                    amount=reward_data["amount"],
                    currency=reward_data.get("currency", "CREDITS"),
                    description=reward_data["description"],
                    metadata=reward_data.get("metadata", {})
                )
                challenge_rewards.append(reward)
            
            # Calculate dates
            start_date = kwargs.get("start_date", datetime.utcnow())
            end_date = kwargs.get("end_date", start_date + timedelta(days=duration_days))
            
            # Create challenge
            challenge = Challenge(
                id=challenge_id,
                title=title,
                description=description,
                challenge_type=challenge_type,
                difficulty=difficulty,
                requirements=challenge_requirements,
                rewards=challenge_rewards,
                status=ChallengeStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                max_participants=kwargs.get("max_participants"),
                tags=kwargs.get("tags", []),
                prerequisites=kwargs.get("prerequisites", []),
                metadata=kwargs.get("metadata", {}),
                created_by=created_by
            )
            
            # Store challenge
            self.active_challenges[challenge_id] = challenge
            
            self.logger.info(f"✅ Custom challenge created: {challenge.title}")
            
            return challenge
            
        except Exception as e:
            self.logger.error(f"Error creating custom challenge: {e}")
            return None
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Join a user to a challenge."""
        try:
            if challenge_id not in self.active_challenges:
                self.logger.error(f"Challenge not found: {challenge_id}")
                return False
            
            challenge = self.active_challenges[challenge_id]
            
            # Check if challenge is active
            if challenge.status != ChallengeStatus.ACTIVE:
                self.logger.error(f"Challenge not active: {challenge_id}")
                return False
            
            # Check if challenge has started
            if datetime.utcnow() < challenge.start_date:
                self.logger.error(f"Challenge not started yet: {challenge_id}")
                return False
            
            # Check if challenge has ended
            if datetime.utcnow() > challenge.end_date:
                self.logger.error(f"Challenge has ended: {challenge_id}")
                return False
            
            # Check participant limit
            if (challenge.max_participants and 
                challenge.current_participants >= challenge.max_participants):
                self.logger.error(f"Challenge is full: {challenge_id}")
                return False
            
            # Check if user already joined
            if user_id in self.user_participations:
                existing_participation = next(
                    (p for p in self.user_participations[user_id] 
                     if p.challenge_id == challenge_id), None
                )
                if existing_participation:
                    self.logger.warning(f"User already joined challenge: {user_id} - {challenge_id}")
                    return False
            
            # Check prerequisites
            if challenge.prerequisites:
                if not await self._check_user_prerequisites(user_id, challenge.prerequisites):
                    self.logger.error(f"User doesn't meet prerequisites: {user_id}")
                    return False
            
            # Create participation
            participation = ChallengeParticipation(
                id=str(uuid4()),
                user_id=user_id,
                challenge_id=challenge_id,
                status=ParticipationStatus.IN_PROGRESS,
                progress_data={},
                completion_percentage=0.0,
                started_at=datetime.utcnow()
            )
            
            # Store participation
            if user_id not in self.user_participations:
                self.user_participations[user_id] = []
            
            self.user_participations[user_id].append(participation)
            
            # Update challenge participant count
            challenge.current_participants += 1
            
            self.logger.info(f"✅ User joined challenge: {user_id} - {challenge.title}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error joining challenge: {e}")
            return False
    
    async def update_user_progress(
        self,
        user_id: str,
        metric_key: str,
        value: Union[int, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Update user progress for all relevant challenges.
        
        Returns:
            List of completed challenge IDs
        """
        try:
            completed_challenges = []
            
            if user_id not in self.user_participations:
                return completed_challenges
            
            for participation in self.user_participations[user_id]:
                if participation.status != ParticipationStatus.IN_PROGRESS:
                    continue
                
                if participation.challenge_id not in self.active_challenges:
                    continue
                
                challenge = self.active_challenges[participation.challenge_id]
                
                # Check if challenge uses this metric
                relevant_requirements = [
                    req for req in challenge.requirements 
                    if req.metric_key == metric_key
                ]
                
                if not relevant_requirements:
                    continue
                
                # Update progress data
                participation.progress_data[metric_key] = value
                participation.last_updated = datetime.utcnow()
                
                # Check if challenge is completed
                if await self._check_challenge_completion(participation, challenge):
                    participation.status = ParticipationStatus.COMPLETED
                    participation.completed_at = datetime.utcnow()
                    completed_challenges.append(challenge.id)
                    
                    # Award challenge rewards
                    await self._award_challenge_rewards(user_id, challenge)
                    
                    self.logger.info(f"🏆 Challenge completed: {user_id} - {challenge.title}")
                else:
                    # Update progress percentage
                    participation.completion_percentage = await self._calculate_challenge_progress(
                        participation, challenge
                    )
            
            return completed_challenges
            
        except Exception as e:
            self.logger.error(f"Error updating user progress: {e}")
            return []
    
    async def _check_user_prerequisites(
        self,
        user_id: str,
        prerequisites: List[str]
    ) -> bool:
        """Check if user meets challenge prerequisites."""
        try:
            # In a real implementation, this would check user achievements,
            # completed challenges, tier level, etc.
            return True
        except Exception as e:
            self.logger.error(f"Error checking prerequisites: {e}")
            return False
    
    async def _check_challenge_completion(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> bool:
        """Check if challenge is completed by user."""
        try:
            required_count = 0
            completed_count = 0
            
            for requirement in challenge.requirements:
                if requirement.is_optional:
                    continue
                
                required_count += 1
                user_value = participation.progress_data.get(requirement.metric_key, 0)
                
                if requirement.comparison_type == "greater_equal":
                    if user_value >= requirement.target_value:
                        completed_count += 1
                elif requirement.comparison_type == "equal":
                    if user_value == requirement.target_value:
                        completed_count += 1
                elif requirement.comparison_type == "less_equal":
                    if user_value <= requirement.target_value:
                        completed_count += 1
            
            return completed_count >= required_count
            
        except Exception as e:
            self.logger.error(f"Error checking challenge completion: {e}")
            return False
    
    async def _calculate_challenge_progress(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> float:
        """Calculate challenge completion percentage."""
        try:
            total_requirements = len([r for r in challenge.requirements if not r.is_optional])
            
            if total_requirements == 0:
                return 100.0
            
            requirement_percentages = []
            
            for requirement in challenge.requirements:
                if requirement.is_optional:
                    continue
                
                user_value = participation.progress_data.get(requirement.metric_key, 0)
                target_value = requirement.target_value
                
                if requirement.comparison_type == "greater_equal":
                    if user_value >= target_value:
                        requirement_percentages.append(100.0)
                    else:
                        percentage = min(100.0, (user_value / target_value) * 100.0)
                        requirement_percentages.append(percentage)
                elif requirement.comparison_type == "equal":
                    if user_value == target_value:
                        requirement_percentages.append(100.0)
                    else:
                        requirement_percentages.append(0.0)
                elif requirement.comparison_type == "less_equal":
                    if user_value <= target_value:
                        requirement_percentages.append(100.0)
                    else:
                        requirement_percentages.append(0.0)
            
            # Weighted average based on requirement weights
            if requirement_percentages:
                total_weight = sum(r.weight for r in challenge.requirements if not r.is_optional)
                weighted_sum = sum(
                    p * challenge.requirements[i].weight 
                    for i, p in enumerate(requirement_percentages)
                )
                return weighted_sum / total_weight if total_weight > 0 else 0.0
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating challenge progress: {e}")
            return 0.0
    
    async def _award_challenge_rewards(
        self,
        user_id: str,
        challenge: Challenge
    ) -> bool:
        """Award rewards for challenge completion."""
        try:
            # In a real implementation, this would integrate with the rewards system
            for reward in challenge.rewards:
                self.logger.info(f"💰 Awarded {reward.amount} {reward.currency} to {user_id}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error awarding challenge rewards: {e}")
            return False
    
    async def get_active_challenges(
        self,
        challenge_type: Optional[ChallengeType] = None,
        difficulty: Optional[ChallengeDifficulty] = None,
        tags: Optional[List[str]] = None
    ) -> List[Challenge]:
        """Get active challenges with optional filtering."""
        try:
            challenges = []
            
            for challenge in self.active_challenges.values():
                if challenge.status != ChallengeStatus.ACTIVE:
                    continue
                
                if datetime.utcnow() > challenge.end_date:
                    continue
                
                # Apply filters
                if challenge_type and challenge.challenge_type != challenge_type:
                    continue
                
                if difficulty and challenge.difficulty != difficulty:
                    continue
                
                if tags and not any(tag in challenge.tags for tag in tags):
                    continue
                
                challenges.append(challenge)
            
            # Sort by start date
            challenges.sort(key=lambda c: c.start_date)
            
            return challenges
            
        except Exception as e:
            self.logger.error(f"Error getting active challenges: {e}")
            return []
    
    async def get_user_challenges(
        self,
        user_id: str,
        status: Optional[ParticipationStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get user's challenge participations."""
        try:
            if user_id not in self.user_participations:
                return []
            
            user_challenges = []
            
            for participation in self.user_participations[user_id]:
                if status and participation.status != status:
                    continue
                
                if participation.challenge_id not in self.active_challenges:
                    continue
                
                challenge = self.active_challenges[participation.challenge_id]
                
                user_challenges.append({
                    "challenge": challenge,
                    "participation": participation
                })
            
            return user_challenges
            
        except Exception as e:
            self.logger.error(f"Error getting user challenges: {e}")
            return []
    
    async def get_challenge_leaderboard(
        self,
        challenge_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get leaderboard for a specific challenge."""
        try:
            if challenge_id not in self.active_challenges:
                return []
            
            leaderboard = []
            
            for user_id, participations in self.user_participations.items():
                user_participation = next(
                    (p for p in participations if p.challenge_id == challenge_id), None
                )
                
                if user_participation:
                    leaderboard.append({
                        "user_id": user_id,
                        "status": user_participation.status,
                        "completion_percentage": user_participation.completion_percentage,
                        "completed_at": user_participation.completed_at,
                        "started_at": user_participation.started_at
                    })
            
            # Sort by completion status and percentage
            leaderboard.sort(
                key=lambda x: (
                    x["status"] == ParticipationStatus.COMPLETED,
                    x["completion_percentage"],
                    -(x["completed_at"] or datetime.max).timestamp()
                ),
                reverse=True
            )
            
            return leaderboard[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting challenge leaderboard: {e}")
            return []
    
    async def generate_daily_challenges(self) -> List[Challenge]:
        """Generate daily challenges automatically."""
        try:
            daily_templates = [
                template for template in self.challenge_templates.values()
                if template.challenge_type == ChallengeType.DAILY
            ]
            
            generated_challenges = []
            
            # Generate 2-3 daily challenges
            num_challenges = min(3, len(daily_templates))
            selected_templates = random.sample(daily_templates, num_challenges)
            
            for template in selected_templates:
                challenge = await self.create_challenge_from_template(template.id)
                if challenge:
                    generated_challenges.append(challenge)
            
            self.logger.info(f"✅ Generated {len(generated_challenges)} daily challenges")
            
            return generated_challenges
            
        except Exception as e:
            self.logger.error(f"Error generating daily challenges: {e}")
            return []
    
    async def cleanup_expired_challenges(self) -> int:
        """Clean up expired challenges."""
        try:
            expired_count = 0
            current_time = datetime.utcnow()
            
            for challenge_id, challenge in list(self.active_challenges.items()):
                if current_time > challenge.end_date and challenge.status == ChallengeStatus.ACTIVE:
                    challenge.status = ChallengeStatus.EXPIRED
                    expired_count += 1
                    
                    # Update any in-progress participations
                    for user_participations in self.user_participations.values():
                        for participation in user_participations:
                            if (participation.challenge_id == challenge_id and 
                                participation.status == ParticipationStatus.IN_PROGRESS):
                                participation.status = ParticipationStatus.FAILED
            
            self.logger.info(f"🧹 Cleaned up {expired_count} expired challenges")
            
            return expired_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired challenges: {e}")
            return 0


# Global challenge system instance
_challenge_system: Optional[ChallengeSystem] = None


async def get_challenge_system() -> ChallengeSystem:
    """Get global challenge system instance."""
    global _challenge_system
    
    if _challenge_system is None:
        _challenge_system = ChallengeSystem()
    
    return _challenge_system


async def create_challenge_from_template(
    template_id: str,
    customizations: Optional[Dict[str, Any]] = None
) -> Optional[Challenge]:
    """Convenience function to create challenge from template."""
    system = await get_challenge_system()
    return await system.create_challenge_from_template(template_id, customizations)


async def join_challenge(user_id: str, challenge_id: str) -> bool:
    """Convenience function to join a challenge."""
    system = await get_challenge_system()
    return await system.join_challenge(user_id, challenge_id)