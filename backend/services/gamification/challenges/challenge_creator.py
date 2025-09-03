"""Challenge Creator - Création challenges
======================================

Challenge creation and management system for generating dynamic challenges,
managing challenge templates, and coordinating challenge lifecycles.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import random


class ChallengeType(str, Enum):
    """Types of challenges available."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    COMMUNITY = "community"
    PERSONAL = "personal"
    COLLABORATION = "collaboration"
    MILESTONE = "milestone"


class ChallengeDifficulty(str, Enum):
    """Challenge difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    LEGENDARY = "legendary"


class ChallengeStatus(str, Enum):
    """Challenge lifecycle status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ParticipationStatus(str, Enum):
    """User participation status in challenges."""
    NOT_JOINED = "not_joined"
    JOINED = "joined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class ChallengeRequirement:
    """Challenge requirement definition."""
    metric: str
    target_value: Union[int, float]
    operator: str = "greater_equal"  # greater_equal, less_equal, equal
    description: str = ""
    weight: float = 1.0


@dataclass
class ChallengeReward:
    """Challenge reward definition."""
    reward_type: str
    amount: Union[int, float]
    currency: str = "credits"
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
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None


@dataclass
class ChallengeParticipation:
    """User participation in a challenge."""
    id: str
    user_id: str
    challenge_id: str
    status: ParticipationStatus
    progress_data: Dict[str, Union[int, float]]
    completion_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
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
    variables: Dict[str, Any] = field(default_factory=dict)


class ChallengeCreator:
    """
    Advanced challenge creation system providing dynamic challenge generation,
    template management, and intelligent challenge recommendation.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the challenge creator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.active_challenges: Dict[str, Challenge] = {}
        self.challenge_templates: Dict[str, ChallengeTemplate] = {}
        self.user_participations: Dict[str, List[ChallengeParticipation]] = {}
        
        # Initialize system
        self._initialize_challenge_templates()
        
        self.logger.info("ChallengeCreator initialized")
    
    def _initialize_challenge_templates(self):
        """Initialize default challenge templates."""
        try:
            # Daily upload challenge
            self.challenge_templates["daily_upload"] = ChallengeTemplate(
                id="daily_upload",
                name="Daily Content Upload",
                title_template="Daily Creator Challenge",
                description_template="Upload {count} pieces of content today",
                challenge_type=ChallengeType.DAILY,
                difficulty=ChallengeDifficulty.EASY,
                requirement_templates=[
                    {
                        "metric": "uploads_today",
                        "target_value": 1,
                        "operator": "greater_equal",
                        "description": "Upload content today"
                    }
                ],
                reward_templates=[
                    {
                        "reward_type": "points",
                        "amount": 50,
                        "currency": "xp",
                        "description": "Daily upload bonus"
                    }
                ],
                duration_days=1,
                tags=["daily", "upload", "consistency"]
            )
            
            # Weekly collaboration challenge
            self.challenge_templates["weekly_collaboration"] = ChallengeTemplate(
                id="weekly_collaboration",
                name="Weekly Collaboration",
                title_template="Team Player Challenge",
                description_template="Complete {count} collaborations this week",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.MEDIUM,
                requirement_templates=[
                    {
                        "metric": "collaborations_week",
                        "target_value": 3,
                        "operator": "greater_equal",
                        "description": "Complete collaborations"
                    }
                ],
                reward_templates=[
                    {
                        "reward_type": "currency",
                        "amount": 200,
                        "currency": "collaboration_coins",
                        "description": "Collaboration master reward"
                    }
                ],
                duration_days=7,
                tags=["weekly", "collaboration", "teamwork"]
            )
            
            # Monthly growth challenge
            self.challenge_templates["monthly_growth"] = ChallengeTemplate(
                id="monthly_growth",
                name="Monthly Growth Challenge",
                title_template="Growth Master",
                description_template="Gain {count} new followers this month",
                challenge_type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.HARD,
                requirement_templates=[
                    {
                        "metric": "follower_growth_month",
                        "target_value": 100,
                        "operator": "greater_equal",
                        "description": "Gain new followers"
                    }
                ],
                reward_templates=[
                    {
                        "reward_type": "currency",
                        "amount": 1000,
                        "currency": "credits",
                        "description": "Growth achievement reward"
                    },
                    {
                        "reward_type": "badge",
                        "amount": 1,
                        "currency": "growth_master",
                        "description": "Growth master badge"
                    }
                ],
                duration_days=30,
                tags=["monthly", "growth", "followers"]
            )
            
            # Quality content challenge
            self.challenge_templates["quality_content"] = ChallengeTemplate(
                id="quality_content",
                name="Quality Content Challenge",
                title_template="Quality Creator",
                description_template="Create {count} high-quality content pieces",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.MEDIUM,
                requirement_templates=[
                    {
                        "metric": "high_quality_uploads",
                        "target_value": 5,
                        "operator": "greater_equal",
                        "description": "Upload high-quality content"
                    }
                ],
                reward_templates=[
                    {
                        "reward_type": "currency",
                        "amount": 300,
                        "currency": "quality_crystals",
                        "description": "Quality content reward"
                    }
                ],
                duration_days=7,
                tags=["quality", "content", "creation"],
                variables={"quality_threshold": 0.8}
            )
            
            # Viral content challenge
            self.challenge_templates["viral_content"] = ChallengeTemplate(
                id="viral_content",
                name="Viral Content Challenge",
                title_template="Go Viral",
                description_template="Create content that reaches {count}+ views",
                challenge_type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.EXPERT,
                requirement_templates=[
                    {
                        "metric": "max_content_views",
                        "target_value": 100000,
                        "operator": "greater_equal",
                        "description": "Achieve viral views"
                    }
                ],
                reward_templates=[
                    {
                        "reward_type": "currency",
                        "amount": 2500,
                        "currency": "credits",
                        "description": "Viral content achievement"
                    },
                    {
                        "reward_type": "badge",
                        "amount": 1,
                        "currency": "viral_master",
                        "description": "Viral master badge"
                    }
                ],
                duration_days=30,
                tags=["viral", "views", "engagement"]
            )
            
            # Community engagement challenge
            self.challenge_templates["community_engagement"] = ChallengeTemplate(
                id="community_engagement",
                name="Community Engagement Challenge",
                title_template="Community Builder",
                description_template="Engage with {count} other creators",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.EASY,
                requirement_templates=[
                    {
                        "metric": "creator_interactions",
                        "target_value": 10,
                        "operator": "greater_equal",
                        "description": "Interact with other creators"
                    }
                ],
                reward_templates=[
                    {
                        "reward_type": "currency",
                        "amount": 150,
                        "currency": "credits",
                        "description": "Community engagement reward"
                    }
                ],
                duration_days=7,
                tags=["community", "engagement", "social"]
            )
            
            self.logger.info(f"Initialized {len(self.challenge_templates)} challenge templates")
            
        except Exception as e:
            self.logger.error(f"Error initializing challenge templates: {e}")
    
    async def create_challenge_from_template(
        self,
        template_id: str,
        customizations: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None
    ) -> Optional[str]:
        """Create a challenge from a template."""
        try:
            template = self.challenge_templates.get(template_id)
            if not template:
                self.logger.warning(f"Template {template_id} not found")
                return None
            
            # Set start and end dates
            if not start_date:
                start_date = datetime.now(timezone.utc)
            end_date = start_date + timedelta(days=template.duration_days)
            
            # Apply customizations
            custom_vars = customizations or {}
            variables = {**template.variables, **custom_vars}
            
            # Generate challenge ID
            challenge_id = f"{template_id}_{int(start_date.timestamp())}"
            
            # Create requirements from template
            requirements = []
            for req_template in template.requirement_templates:
                target_value = req_template["target_value"]
                
                # Apply variable substitutions
                if "target_value_var" in req_template and req_template["target_value_var"] in variables:
                    target_value = variables[req_template["target_value_var"]]
                
                requirement = ChallengeRequirement(
                    metric=req_template["metric"],
                    target_value=target_value,
                    operator=req_template.get("operator", "greater_equal"),
                    description=req_template.get("description", ""),
                    weight=req_template.get("weight", 1.0)
                )
                requirements.append(requirement)
            
            # Create rewards from template
            rewards = []
            for reward_template in template.reward_templates:
                amount = reward_template["amount"]
                
                # Apply variable substitutions for rewards
                if "amount_var" in reward_template and reward_template["amount_var"] in variables:
                    amount = variables[reward_template["amount_var"]]
                
                reward = ChallengeReward(
                    reward_type=reward_template["reward_type"],
                    amount=amount,
                    currency=reward_template.get("currency", "credits"),
                    description=reward_template.get("description", ""),
                    metadata=reward_template.get("metadata", {})
                )
                rewards.append(reward)
            
            # Format title and description with variables
            title = template.title_template.format(**variables, **custom_vars)
            description = template.description_template.format(**variables, **custom_vars)
            
            # Create challenge
            challenge = Challenge(
                id=challenge_id,
                title=title,
                description=description,
                challenge_type=template.challenge_type,
                difficulty=template.difficulty,
                requirements=requirements,
                rewards=rewards,
                status=ChallengeStatus.SCHEDULED,
                start_date=start_date,
                end_date=end_date,
                tags=template.tags.copy(),
                metadata={"template_id": template_id, "variables": variables}
            )
            
            # Store challenge
            self.active_challenges[challenge_id] = challenge
            
            self.logger.info(f"Created challenge '{title}' from template {template_id}")
            return challenge_id
            
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
        start_date: Optional[datetime] = None,
        max_participants: Optional[int] = None,
        tags: Optional[List[str]] = None,
        prerequisites: Optional[List[str]] = None
    ) -> Optional[str]:
        """Create a custom challenge."""
        try:
            # Generate challenge ID
            challenge_id = str(uuid.uuid4())
            
            # Set dates
            if not start_date:
                start_date = datetime.now(timezone.utc)
            end_date = start_date + timedelta(days=duration_days)
            
            # Create requirements
            challenge_requirements = []
            for req_data in requirements:
                requirement = ChallengeRequirement(
                    metric=req_data["metric"],
                    target_value=req_data["target_value"],
                    operator=req_data.get("operator", "greater_equal"),
                    description=req_data.get("description", ""),
                    weight=req_data.get("weight", 1.0)
                )
                challenge_requirements.append(requirement)
            
            # Create rewards
            challenge_rewards = []
            for reward_data in rewards:
                reward = ChallengeReward(
                    reward_type=reward_data["reward_type"],
                    amount=reward_data["amount"],
                    currency=reward_data.get("currency", "credits"),
                    description=reward_data.get("description", ""),
                    metadata=reward_data.get("metadata", {})
                )
                challenge_rewards.append(reward)
            
            # Create challenge
            challenge = Challenge(
                id=challenge_id,
                title=title,
                description=description,
                challenge_type=challenge_type,
                difficulty=difficulty,
                requirements=challenge_requirements,
                rewards=challenge_rewards,
                status=ChallengeStatus.SCHEDULED,
                start_date=start_date,
                end_date=end_date,
                max_participants=max_participants,
                tags=tags or [],
                prerequisites=prerequisites or [],
                metadata={"custom": True}
            )
            
            # Store challenge
            self.active_challenges[challenge_id] = challenge
            
            self.logger.info(f"Created custom challenge '{title}'")
            return challenge_id
            
        except Exception as e:
            self.logger.error(f"Error creating custom challenge: {e}")
            return None
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Join a user to a challenge."""
        try:
            challenge = self.active_challenges.get(challenge_id)
            if not challenge:
                self.logger.warning(f"Challenge {challenge_id} not found")
                return False
            
            # Check if challenge is active
            now = datetime.now(timezone.utc)
            if challenge.status != ChallengeStatus.ACTIVE or now < challenge.start_date or now > challenge.end_date:
                self.logger.warning(f"Challenge {challenge_id} is not active")
                return False
            
            # Check if user already joined
            user_participations = self.user_participations.get(user_id, [])
            existing = next((p for p in user_participations if p.challenge_id == challenge_id), None)
            if existing:
                self.logger.warning(f"User {user_id} already joined challenge {challenge_id}")
                return False
            
            # Check participant limit
            if challenge.max_participants and challenge.current_participants >= challenge.max_participants:
                self.logger.warning(f"Challenge {challenge_id} is full")
                return False
            
            # Check prerequisites (simplified)
            if challenge.prerequisites:
                # In a real implementation, would check user's completed challenges/achievements
                pass
            
            # Create participation
            participation = ChallengeParticipation(
                id=f"{user_id}_{challenge_id}",
                user_id=user_id,
                challenge_id=challenge_id,
                status=ParticipationStatus.JOINED,
                progress_data={req.metric: 0 for req in challenge.requirements},
                completion_percentage=0.0,
                started_at=now
            )
            
            # Add to user participations
            if user_id not in self.user_participations:
                self.user_participations[user_id] = []
            self.user_participations[user_id].append(participation)
            
            # Update challenge participant count
            challenge.current_participants += 1
            
            self.logger.info(f"User {user_id} joined challenge '{challenge.title}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error joining challenge: {e}")
            return False
    
    async def update_user_progress(
        self,
        user_id: str,
        challenge_id: str,
        metric_updates: Dict[str, Union[int, float]]
    ) -> Dict[str, Any]:
        """Update user's progress in a challenge."""
        try:
            # Find user participation
            user_participations = self.user_participations.get(user_id, [])
            participation = next((p for p in user_participations if p.challenge_id == challenge_id), None)
            
            if not participation:
                return {"error": "Participation not found"}
            
            if participation.status not in [ParticipationStatus.JOINED, ParticipationStatus.IN_PROGRESS]:
                return {"error": "Challenge not in progress"}
            
            # Update progress data
            for metric, value in metric_updates.items():
                if metric in participation.progress_data:
                    participation.progress_data[metric] = max(participation.progress_data[metric], value)
            
            # Calculate completion percentage
            challenge = self.active_challenges.get(challenge_id)
            if challenge:
                completion_percentage = await self._calculate_completion_percentage(participation, challenge)
                participation.completion_percentage = completion_percentage
                participation.status = ParticipationStatus.IN_PROGRESS
                participation.last_updated = datetime.now(timezone.utc)
                
                # Check if challenge is completed
                if completion_percentage >= 100.0:
                    participation.status = ParticipationStatus.COMPLETED
                    participation.completed_at = datetime.now(timezone.utc)
                    
                    # Award rewards
                    await self._award_challenge_rewards(user_id, challenge)
                    
                    self.logger.info(f"🎉 User {user_id} completed challenge '{challenge.title}'")
                    
                    return {
                        "status": "completed",
                        "completion_percentage": completion_percentage,
                        "rewards": [
                            {
                                "type": reward.reward_type,
                                "amount": reward.amount,
                                "currency": reward.currency,
                                "description": reward.description
                            }
                            for reward in challenge.rewards
                        ]
                    }
                
                return {
                    "status": "in_progress",
                    "completion_percentage": completion_percentage,
                    "progress": participation.progress_data
                }
            
            return {"error": "Challenge not found"}
            
        except Exception as e:
            self.logger.error(f"Error updating user progress: {e}")
            return {"error": "Failed to update progress"}
    
    async def _calculate_completion_percentage(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> float:
        """Calculate completion percentage for a challenge."""
        try:
            if not challenge.requirements:
                return 100.0
            
            total_weight = sum(req.weight for req in challenge.requirements)
            if total_weight == 0:
                return 100.0
            
            completed_weight = 0.0
            
            for requirement in challenge.requirements:
                current_value = participation.progress_data.get(requirement.metric, 0)
                
                if requirement.operator == "greater_equal":
                    progress_ratio = min(current_value / requirement.target_value, 1.0)
                elif requirement.operator == "less_equal":
                    progress_ratio = 1.0 if current_value <= requirement.target_value else 0.0
                elif requirement.operator == "equal":
                    progress_ratio = 1.0 if current_value == requirement.target_value else 0.0
                else:
                    progress_ratio = 0.0
                
                completed_weight += progress_ratio * requirement.weight
            
            return (completed_weight / total_weight) * 100.0
            
        except Exception as e:
            self.logger.error(f"Error calculating completion percentage: {e}")
            return 0.0
    
    async def _award_challenge_rewards(self, user_id: str, challenge: Challenge):
        """Award rewards for challenge completion."""
        try:
            from ..rewards.reward_distributor import get_reward_distributor
            reward_distributor = get_reward_distributor()
            
            for reward in challenge.rewards:
                await reward_distributor.distribute_reward(
                    user_id=user_id,
                    reward_type=reward.reward_type,
                    name=f"Challenge Reward: {challenge.title}",
                    description=reward.description,
                    value=reward.amount,
                    currency_type=reward.currency,
                    trigger_source_id=challenge.id,
                    metadata={"challenge_id": challenge.id}
                )
            
        except Exception as e:
            self.logger.error(f"Error awarding challenge rewards: {e}")
    
    async def get_active_challenges(
        self,
        challenge_type: Optional[ChallengeType] = None,
        difficulty: Optional[ChallengeDifficulty] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get active challenges with optional filtering."""
        try:
            now = datetime.now(timezone.utc)
            active_challenges = []
            
            for challenge in self.active_challenges.values():
                # Check if challenge is currently active
                if (challenge.status == ChallengeStatus.ACTIVE and 
                    challenge.start_date <= now <= challenge.end_date):
                    
                    # Apply filters
                    if challenge_type and challenge.challenge_type != challenge_type:
                        continue
                    if difficulty and challenge.difficulty != difficulty:
                        continue
                    if tags and not any(tag in challenge.tags for tag in tags):
                        continue
                    
                    active_challenges.append({
                        "id": challenge.id,
                        "title": challenge.title,
                        "description": challenge.description,
                        "challenge_type": challenge.challenge_type,
                        "difficulty": challenge.difficulty,
                        "start_date": challenge.start_date.isoformat(),
                        "end_date": challenge.end_date.isoformat(),
                        "current_participants": challenge.current_participants,
                        "max_participants": challenge.max_participants,
                        "tags": challenge.tags,
                        "requirements": [
                            {
                                "metric": req.metric,
                                "target_value": req.target_value,
                                "operator": req.operator,
                                "description": req.description
                            }
                            for req in challenge.requirements
                        ],
                        "rewards": [
                            {
                                "reward_type": reward.reward_type,
                                "amount": reward.amount,
                                "currency": reward.currency,
                                "description": reward.description
                            }
                            for reward in challenge.rewards
                        ]
                    })
            
            return active_challenges
            
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
            user_participations = self.user_participations.get(user_id, [])
            
            if status:
                user_participations = [p for p in user_participations if p.status == status]
            
            result = []
            for participation in user_participations:
                challenge = self.active_challenges.get(participation.challenge_id)
                if challenge:
                    result.append({
                        "participation_id": participation.id,
                        "challenge_id": challenge.id,
                        "challenge_title": challenge.title,
                        "challenge_description": challenge.description,
                        "challenge_type": challenge.challenge_type,
                        "difficulty": challenge.difficulty,
                        "status": participation.status,
                        "completion_percentage": participation.completion_percentage,
                        "progress_data": participation.progress_data,
                        "started_at": participation.started_at.isoformat(),
                        "completed_at": participation.completed_at.isoformat() if participation.completed_at else None,
                        "end_date": challenge.end_date.isoformat()
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting user challenges: {e}")
            return []
    
    async def process_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process a user action and update relevant challenge progress."""
        results = []
        
        try:
            # Map action types to metrics
            metric_mapping = {
                "content_upload": "uploads_today",
                "collaboration_complete": "collaborations_week",
                "follower_gain": "follower_growth_month",
                "high_quality_upload": "high_quality_uploads",
                "content_view": "max_content_views",
                "creator_interaction": "creator_interactions"
            }
            
            metric = metric_mapping.get(action_type)
            if not metric:
                return results
            
            # Get user's active challenges
            user_participations = self.user_participations.get(user_id, [])
            active_participations = [
                p for p in user_participations 
                if p.status in [ParticipationStatus.JOINED, ParticipationStatus.IN_PROGRESS]
            ]
            
            # Update progress for relevant challenges
            for participation in active_participations:
                challenge = self.active_challenges.get(participation.challenge_id)
                if challenge and any(req.metric == metric for req in challenge.requirements):
                    # Calculate new metric value
                    new_value = action_data.get("count", 1)
                    if action_type == "content_view":
                        new_value = action_data.get("view_count", 0)
                    elif action_type == "follower_gain":
                        new_value = action_data.get("total_followers", 0)
                    
                    # Update progress
                    progress_result = await self.update_user_progress(
                        user_id, challenge.id, {metric: new_value}
                    )
                    
                    if progress_result.get("status") == "completed":
                        results.append({
                            "type": "challenge_completed",
                            "challenge_id": challenge.id,
                            "challenge_title": challenge.title,
                            "rewards": progress_result.get("rewards", [])
                        })
                    elif progress_result.get("status") == "in_progress":
                        results.append({
                            "type": "challenge_progress",
                            "challenge_id": challenge.id,
                            "challenge_title": challenge.title,
                            "completion_percentage": progress_result.get("completion_percentage", 0)
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing action for challenges: {e}")
            return []
    
    async def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user's challenge summary."""
        try:
            user_participations = self.user_participations.get(user_id, [])
            
            summary = {
                "total_challenges": len(user_participations),
                "completed_challenges": len([p for p in user_participations if p.status == ParticipationStatus.COMPLETED]),
                "active_challenges": len([p for p in user_participations if p.status in [ParticipationStatus.JOINED, ParticipationStatus.IN_PROGRESS]]),
                "failed_challenges": len([p for p in user_participations if p.status == ParticipationStatus.FAILED]),
                "recent_completions": [],
                "active_progress": []
            }
            
            # Recent completions
            completed = [p for p in user_participations if p.status == ParticipationStatus.COMPLETED and p.completed_at]
            completed.sort(key=lambda x: x.completed_at, reverse=True)
            
            for participation in completed[:5]:
                challenge = self.active_challenges.get(participation.challenge_id)
                if challenge:
                    summary["recent_completions"].append({
                        "challenge_id": challenge.id,
                        "title": challenge.title,
                        "completed_at": participation.completed_at.isoformat(),
                        "difficulty": challenge.difficulty
                    })
            
            # Active progress
            active = [p for p in user_participations if p.status in [ParticipationStatus.JOINED, ParticipationStatus.IN_PROGRESS]]
            
            for participation in active:
                challenge = self.active_challenges.get(participation.challenge_id)
                if challenge:
                    summary["active_progress"].append({
                        "challenge_id": challenge.id,
                        "title": challenge.title,
                        "completion_percentage": participation.completion_percentage,
                        "end_date": challenge.end_date.isoformat()
                    })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting user challenge summary: {e}")
            return {}
    
    async def generate_daily_challenges(self) -> List[str]:
        """Generate daily challenges automatically."""
        try:
            generated_challenges = []
            
            # Generate daily upload challenge
            daily_upload_id = await self.create_challenge_from_template("daily_upload")
            if daily_upload_id:
                generated_challenges.append(daily_upload_id)
                # Activate the challenge
                challenge = self.active_challenges[daily_upload_id]
                challenge.status = ChallengeStatus.ACTIVE
            
            # Generate community engagement challenge
            community_id = await self.create_challenge_from_template("community_engagement")
            if community_id:
                generated_challenges.append(community_id)
                challenge = self.active_challenges[community_id]
                challenge.status = ChallengeStatus.ACTIVE
            
            self.logger.info(f"Generated {len(generated_challenges)} daily challenges")
            return generated_challenges
            
        except Exception as e:
            self.logger.error(f"Error generating daily challenges: {e}")
            return []


# Global instance
_challenge_creator = None

def get_challenge_creator(database_connection=None, cache_client=None) -> ChallengeCreator:
    """Get the global challenge creator instance."""
    global _challenge_creator
    if _challenge_creator is None:
        _challenge_creator = ChallengeCreator(database_connection, cache_client)
    return _challenge_creator