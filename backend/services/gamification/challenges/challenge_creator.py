"""Challenge Creator - Dynamic Challenge Creation and Management
===========================================================

Advanced challenge creation system providing dynamic challenge generation,
template management, challenge customization, and comprehensive challenge
lifecycle management for content creator engagement.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification/challenges/challenge_creator.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA

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
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import random

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
    SKILL_BASED = "skill_based"
    MILESTONE = "milestone"
    COMMUNITY = "community"


class ChallengeDifficulty(str, Enum):
    """Challenge difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"


class ChallengeStatus(str, Enum):
    """Challenge status states."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ParticipationStatus(str, Enum):
    """User participation status in challenges."""
    NOT_JOINED = "not_joined"
    JOINED = "joined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class ChallengeReward:
    """Challenge completion reward."""
    id: str
    reward_type: str  # points, currency, badge, etc.
    value: Union[float, int, str, Dict[str, Any]]
    description: str
    rarity: str = "common"
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChallengeRequirement:
    """Challenge completion requirement."""
    id: str
    name: str
    description: str
    metric_key: str
    target_value: Union[float, int]
    comparison_operator: str = ">="  # >=, >, ==, <, <=
    weight: float = 1.0  # For multi-requirement challenges
    is_optional: bool = False


@dataclass
class ChallengeTemplate:
    """Template for generating challenges."""
    id: str
    name: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    requirements_templates: List[Dict[str, Any]]
    rewards_templates: List[Dict[str, Any]]
    duration_hours: int = 24
    max_participants: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    generation_rules: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class Challenge:
    """Individual challenge instance."""
    id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    status: ChallengeStatus
    requirements: List[ChallengeRequirement]
    rewards: List[ChallengeReward]
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int] = None
    current_participants: int = 0
    completion_count: int = 0
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    creator_id: Optional[str] = None
    template_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChallengeParticipation:
    """User participation in a challenge."""
    id: str
    user_id: str
    challenge_id: str
    status: ParticipationStatus
    joined_at: datetime
    completed_at: Optional[datetime] = None
    progress_data: Dict[str, Any] = field(default_factory=dict)
    completion_percentage: float = 0.0
    rewards_claimed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChallengeCreator:
    """
    Advanced challenge creation and management system.
    
    Provides dynamic challenge generation, template management,
    challenge customization, and comprehensive lifecycle management.
    """
    
    def __init__(self):
        """Initialize the challenge creator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Challenge templates and instances
        self.challenge_templates: Dict[str, ChallengeTemplate] = {}
        self.challenges: Dict[str, Challenge] = {}
        
        # User participation tracking
        self.participations: Dict[str, List[ChallengeParticipation]] = {}
        
        # Challenge generation and management
        self.active_challenges: Dict[str, Challenge] = {}
        self.completed_challenges: List[Challenge] = []
        
        # Statistics and analytics
        self.challenge_statistics: Dict[str, Any] = {}
        
        self.logger.info("ChallengeCreator initialized")
    
    async def initialize(self) -> bool:
        """Initialize the challenge creator with default templates."""
        try:
            # Load default challenge templates
            await self._load_default_templates()
            
            # Start background tasks
            asyncio.create_task(self._generate_daily_challenges())
            asyncio.create_task(self._update_challenge_status())
            asyncio.create_task(self._cleanup_expired_challenges())
            
            self.initialized = True
            self.logger.info(f"✅ ChallengeCreator initialized with {len(self.challenge_templates)} templates")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize ChallengeCreator: {e}")
            return False
    
    async def _load_default_templates(self):
        """Load default challenge templates."""
        default_templates = [
            # Daily Challenges
            ChallengeTemplate(
                id="daily_content_upload",
                name="Daily Creator",
                description="Upload {target} pieces of content today",
                challenge_type=ChallengeType.DAILY,
                difficulty=ChallengeDifficulty.BEGINNER,
                requirements_templates=[
                    {
                        "metric_key": "daily_uploads",
                        "target_value_range": [1, 3],
                        "description": "Upload content pieces"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [50, 150],
                        "description": "Daily challenge points"
                    },
                    {
                        "reward_type": "streak_bonus",
                        "value": 1.1,
                        "description": "Streak multiplier bonus"
                    }
                ],
                duration_hours=24,
                tags=["daily", "content", "beginner"]
            ),
            ChallengeTemplate(
                id="daily_engagement",
                name="Engagement Master",
                description="Achieve {target}% engagement rate on your content today",
                challenge_type=ChallengeType.DAILY,
                difficulty=ChallengeDifficulty.INTERMEDIATE,
                requirements_templates=[
                    {
                        "metric_key": "daily_engagement_rate",
                        "target_value_range": [0.1, 0.25],
                        "description": "Average engagement rate"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [100, 300],
                        "description": "Engagement bonus points"
                    },
                    {
                        "reward_type": "visibility_boost",
                        "value": {"multiplier": 1.2, "duration": 24},
                        "description": "24-hour visibility boost"
                    }
                ],
                duration_hours=24,
                tags=["daily", "engagement", "intermediate"]
            ),
            
            # Weekly Challenges
            ChallengeTemplate(
                id="weekly_collaboration",
                name="Collaboration Champion",
                description="Complete {target} successful collaborations this week",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.INTERMEDIATE,
                requirements_templates=[
                    {
                        "metric_key": "weekly_collaborations",
                        "target_value_range": [2, 5],
                        "description": "Successful collaborations"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [500, 1000],
                        "description": "Collaboration mastery points"
                    },
                    {
                        "reward_type": "collaboration_boost",
                        "value": {"multiplier": 1.5, "duration": 7},
                        "description": "Week-long collaboration boost"
                    },
                    {
                        "reward_type": "badge",
                        "value": "collaboration_champion",
                        "description": "Collaboration Champion badge"
                    }
                ],
                duration_hours=168,  # 7 days
                tags=["weekly", "collaboration", "intermediate"]
            ),
            ChallengeTemplate(
                id="weekly_quality",
                name="Quality Pursuit",
                description="Maintain {target}% average quality score this week",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.ADVANCED,
                requirements_templates=[
                    {
                        "metric_key": "weekly_avg_quality",
                        "target_value_range": [0.75, 0.9],
                        "description": "Average content quality"
                    },
                    {
                        "metric_key": "weekly_uploads",
                        "target_value_range": [5, 10],
                        "description": "Minimum content uploads"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [750, 1500],
                        "description": "Quality achievement points"
                    },
                    {
                        "reward_type": "premium_access",
                        "value": {"duration": 7, "features": ["advanced_analytics"]},
                        "description": "Premium analytics access"
                    }
                ],
                duration_hours=168,
                tags=["weekly", "quality", "advanced"]
            ),
            
            # Monthly Challenges
            ChallengeTemplate(
                id="monthly_growth",
                name="Growth Accelerator",
                description="Achieve {target}% follower growth this month",
                challenge_type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.ADVANCED,
                requirements_templates=[
                    {
                        "metric_key": "monthly_follower_growth",
                        "target_value_range": [0.1, 0.3],
                        "description": "Follower growth percentage"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [2000, 4000],
                        "description": "Growth achievement points"
                    },
                    {
                        "reward_type": "revenue_boost",
                        "value": {"percentage": 0.05, "duration": 30},
                        "description": "5% revenue boost for 30 days"
                    },
                    {
                        "reward_type": "feature_unlock",
                        "value": "premium_analytics",
                        "description": "Permanent premium analytics access"
                    }
                ],
                duration_hours=720,  # 30 days
                tags=["monthly", "growth", "advanced"]
            ),
            
            # Skill-based Challenges
            ChallengeTemplate(
                id="skill_video_mastery",
                name="Video Production Master",
                description="Create {target} high-quality videos with advanced techniques",
                challenge_type=ChallengeType.SKILL_BASED,
                difficulty=ChallengeDifficulty.EXPERT,
                requirements_templates=[
                    {
                        "metric_key": "advanced_video_count",
                        "target_value_range": [3, 7],
                        "description": "Advanced video productions"
                    },
                    {
                        "metric_key": "video_quality_score",
                        "target_value_range": [0.85, 0.95],
                        "description": "Minimum quality threshold"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [1500, 3000],
                        "description": "Video mastery points"
                    },
                    {
                        "reward_type": "certification",
                        "value": "video_production_expert",
                        "description": "Video Production Expert certification"
                    },
                    {
                        "reward_type": "exclusive_access",
                        "value": "master_class_video",
                        "description": "Exclusive video masterclass access"
                    }
                ],
                duration_hours=336,  # 14 days
                prerequisites=["intermediate_video_challenge"],
                tags=["skill", "video", "expert"]
            ),
            
            # Collaborative Challenges
            ChallengeTemplate(
                id="community_project",
                name="Community Builder",
                description="Participate in {target} community projects this month",
                challenge_type=ChallengeType.COLLABORATIVE,
                difficulty=ChallengeDifficulty.INTERMEDIATE,
                requirements_templates=[
                    {
                        "metric_key": "community_projects",
                        "target_value_range": [2, 5],
                        "description": "Community project participations"
                    },
                    {
                        "metric_key": "project_contribution_score",
                        "target_value_range": [0.7, 1.0],
                        "description": "Contribution quality score"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [800, 1600],
                        "description": "Community contribution points"
                    },
                    {
                        "reward_type": "community_badge",
                        "value": "community_champion",
                        "description": "Community Champion badge"
                    },
                    {
                        "reward_type": "special_access",
                        "value": "community_leader_forum",
                        "description": "Community leader forum access"
                    }
                ],
                duration_hours=720,  # 30 days
                max_participants=50,
                tags=["collaborative", "community", "intermediate"]
            ),
            
            # Competitive Challenges
            ChallengeTemplate(
                id="content_race",
                name="Content Creation Race",
                description="Be among top {target} creators in content volume this week",
                challenge_type=ChallengeType.COMPETITIVE,
                difficulty=ChallengeDifficulty.ADVANCED,
                requirements_templates=[
                    {
                        "metric_key": "leaderboard_position",
                        "target_value_range": [1, 10],
                        "description": "Top leaderboard position",
                        "comparison_operator": "<="
                    },
                    {
                        "metric_key": "weekly_content_count",
                        "target_value_range": [10, 20],
                        "description": "Minimum content threshold"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [1000, 2500],
                        "description": "Competition achievement points"
                    },
                    {
                        "reward_type": "trophy",
                        "value": "content_race_winner",
                        "description": "Content Race trophy"
                    },
                    {
                        "reward_type": "featured_placement",
                        "value": {"duration": 7, "prominence": "high"},
                        "description": "Featured creator placement"
                    }
                ],
                duration_hours=168,  # 7 days
                max_participants=100,
                tags=["competitive", "content", "advanced"]
            ),
            
            # Special Event Challenges
            ChallengeTemplate(
                id="seasonal_winter",
                name="Winter Creator Festival",
                description="Create {target} winter-themed content pieces",
                challenge_type=ChallengeType.SEASONAL,
                difficulty=ChallengeDifficulty.BEGINNER,
                requirements_templates=[
                    {
                        "metric_key": "winter_themed_content",
                        "target_value_range": [3, 8],
                        "description": "Winter-themed content pieces"
                    },
                    {
                        "metric_key": "seasonal_engagement",
                        "target_value_range": [0.15, 0.25],
                        "description": "Seasonal content engagement"
                    }
                ],
                rewards_templates=[
                    {
                        "reward_type": "points",
                        "value_range": [300, 800],
                        "description": "Seasonal festival points"
                    },
                    {
                        "reward_type": "seasonal_badge",
                        "value": "winter_creator_2025",
                        "description": "Winter Creator 2025 badge"
                    },
                    {
                        "reward_type": "limited_item",
                        "value": "winter_profile_frame",
                        "description": "Limited winter profile frame"
                    }
                ],
                duration_hours=720,  # 30 days
                tags=["seasonal", "winter", "event", "beginner"]
            )
        ]
        
        for template in default_templates:
            self.challenge_templates[template.id] = template
        
        self.logger.info(f"Loaded {len(default_templates)} default challenge templates")
    
    async def create_challenge_from_template(
        self,
        template_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Optional[Challenge]:
        """Create a challenge instance from a template."""
        try:
            if template_id not in self.challenge_templates:
                self.logger.error(f"Template {template_id} not found")
                return None
            
            template = self.challenge_templates[template_id]
            if not template.is_active:
                self.logger.warning(f"Template {template_id} is not active")
                return None
            
            # Generate challenge requirements
            requirements = []
            for req_template in template.requirements_templates:
                requirement = await self._generate_requirement_from_template(req_template)
                if requirement:
                    requirements.append(requirement)
            
            # Generate challenge rewards
            rewards = []
            for reward_template in template.rewards_templates:
                reward = await self._generate_reward_from_template(reward_template)
                if reward:
                    rewards.append(reward)
            
            # Apply customizations
            if customizations:
                requirements = self._apply_requirement_customizations(requirements, customizations)
                rewards = self._apply_reward_customizations(rewards, customizations)
            
            # Create challenge instance
            challenge_id = str(uuid4())
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(hours=template.duration_hours)
            
            # Generate dynamic title and description
            title, description = self._generate_challenge_text(template, requirements)
            
            challenge = Challenge(
                id=challenge_id,
                title=title,
                description=description,
                challenge_type=template.challenge_type,
                difficulty=template.difficulty,
                status=ChallengeStatus.ACTIVE,
                requirements=requirements,
                rewards=rewards,
                start_date=start_date,
                end_date=end_date,
                max_participants=template.max_participants,
                tags=template.tags.copy(),
                prerequisites=template.prerequisites.copy(),
                template_id=template_id,
                metadata={
                    "generated_at": datetime.utcnow(),
                    "template_version": "1.0",
                    "customizations": customizations or {}
                }
            )
            
            # Store challenge
            self.challenges[challenge_id] = challenge
            self.active_challenges[challenge_id] = challenge
            
            self.logger.info(f"Created challenge: {title} (ID: {challenge_id})")
            
            return challenge
            
        except Exception as e:
            self.logger.error(f"Error creating challenge from template: {e}")
            return None
    
    async def _generate_requirement_from_template(
        self,
        req_template: Dict[str, Any]
    ) -> Optional[ChallengeRequirement]:
        """Generate a requirement from template configuration."""
        try:
            # Generate target value from range
            target_range = req_template.get("target_value_range", [1, 1])
            if isinstance(target_range, list) and len(target_range) == 2:
                target_value = random.uniform(target_range[0], target_range[1])
                # Round based on type
                if req_template.get("metric_key", "").endswith("_count"):
                    target_value = int(target_value)
            else:
                target_value = target_range
            
            requirement = ChallengeRequirement(
                id=str(uuid4()),
                name=req_template.get("name", "Challenge Requirement"),
                description=req_template.get("description", "Complete this requirement"),
                metric_key=req_template["metric_key"],
                target_value=target_value,
                comparison_operator=req_template.get("comparison_operator", ">="),
                weight=req_template.get("weight", 1.0),
                is_optional=req_template.get("is_optional", False)
            )
            
            return requirement
            
        except Exception as e:
            self.logger.error(f"Error generating requirement from template: {e}")
            return None
    
    async def _generate_reward_from_template(
        self,
        reward_template: Dict[str, Any]
    ) -> Optional[ChallengeReward]:
        """Generate a reward from template configuration."""
        try:
            # Generate reward value
            value = reward_template.get("value")
            value_range = reward_template.get("value_range")
            
            if value_range and isinstance(value_range, list) and len(value_range) == 2:
                if reward_template["reward_type"] == "points":
                    value = random.randint(value_range[0], value_range[1])
                else:
                    value = random.uniform(value_range[0], value_range[1])
            
            reward = ChallengeReward(
                id=str(uuid4()),
                reward_type=reward_template["reward_type"],
                value=value,
                description=reward_template.get("description", "Challenge reward"),
                rarity=reward_template.get("rarity", "common"),
                conditions=reward_template.get("conditions", {})
            )
            
            return reward
            
        except Exception as e:
            self.logger.error(f"Error generating reward from template: {e}")
            return None
    
    def _apply_requirement_customizations(
        self,
        requirements: List[ChallengeRequirement],
        customizations: Dict[str, Any]
    ) -> List[ChallengeRequirement]:
        """Apply customizations to generated requirements."""
        try:
            req_customizations = customizations.get("requirements", {})
            
            for requirement in requirements:
                if requirement.metric_key in req_customizations:
                    custom = req_customizations[requirement.metric_key]
                    
                    if "target_value" in custom:
                        requirement.target_value = custom["target_value"]
                    if "comparison_operator" in custom:
                        requirement.comparison_operator = custom["comparison_operator"]
                    if "weight" in custom:
                        requirement.weight = custom["weight"]
            
            return requirements
            
        except Exception as e:
            self.logger.error(f"Error applying requirement customizations: {e}")
            return requirements
    
    def _apply_reward_customizations(
        self,
        rewards: List[ChallengeReward],
        customizations: Dict[str, Any]
    ) -> List[ChallengeReward]:
        """Apply customizations to generated rewards."""
        try:
            reward_customizations = customizations.get("rewards", {})
            
            # Apply multipliers
            if "point_multiplier" in reward_customizations:
                multiplier = reward_customizations["point_multiplier"]
                for reward in rewards:
                    if reward.reward_type == "points" and isinstance(reward.value, (int, float)):
                        reward.value = int(reward.value * multiplier)
            
            # Add bonus rewards
            if "bonus_rewards" in reward_customizations:
                for bonus_reward_data in reward_customizations["bonus_rewards"]:
                    bonus_reward = ChallengeReward(
                        id=str(uuid4()),
                        reward_type=bonus_reward_data["reward_type"],
                        value=bonus_reward_data["value"],
                        description=bonus_reward_data.get("description", "Bonus reward"),
                        rarity=bonus_reward_data.get("rarity", "uncommon")
                    )
                    rewards.append(bonus_reward)
            
            return rewards
            
        except Exception as e:
            self.logger.error(f"Error applying reward customizations: {e}")
            return rewards
    
    def _generate_challenge_text(
        self,
        template: ChallengeTemplate,
        requirements: List[ChallengeRequirement]
    ) -> Tuple[str, str]:
        """Generate dynamic title and description for challenge."""
        try:
            title = template.name
            description = template.description
            
            # Replace placeholders with actual values
            for requirement in requirements:
                target_placeholder = "{target}"
                if target_placeholder in description:
                    if isinstance(requirement.target_value, int):
                        target_str = str(requirement.target_value)
                    elif isinstance(requirement.target_value, float):
                        if requirement.target_value < 1:
                            target_str = f"{requirement.target_value:.1%}"
                        else:
                            target_str = f"{requirement.target_value:.1f}"
                    else:
                        target_str = str(requirement.target_value)
                    
                    description = description.replace(target_placeholder, target_str)
                    break
            
            return title, description
            
        except Exception as e:
            self.logger.error(f"Error generating challenge text: {e}")
            return template.name, template.description
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> Dict[str, Any]:
        """Allow user to join a challenge."""
        try:
            if challenge_id not in self.challenges:
                return {"success": False, "error": "Challenge not found"}
            
            challenge = self.challenges[challenge_id]
            
            # Check if challenge is active and not expired
            if challenge.status != ChallengeStatus.ACTIVE:
                return {"success": False, "error": "Challenge is not active"}
            
            if datetime.utcnow() > challenge.end_date:
                return {"success": False, "error": "Challenge has expired"}
            
            # Check participant limit
            if (challenge.max_participants and 
                challenge.current_participants >= challenge.max_participants):
                return {"success": False, "error": "Challenge is full"}
            
            # Check if user already joined
            if user_id in self.participations:
                for participation in self.participations[user_id]:
                    if participation.challenge_id == challenge_id:
                        return {"success": False, "error": "Already joined this challenge"}
            
            # Check prerequisites
            if challenge.prerequisites:
                if not await self._check_prerequisites(user_id, challenge.prerequisites):
                    return {"success": False, "error": "Prerequisites not met"}
            
            # Create participation record
            participation = ChallengeParticipation(
                id=str(uuid4()),
                user_id=user_id,
                challenge_id=challenge_id,
                status=ParticipationStatus.JOINED,
                joined_at=datetime.utcnow()
            )
            
            # Add to user's participations
            if user_id not in self.participations:
                self.participations[user_id] = []
            self.participations[user_id].append(participation)
            
            # Update challenge participant count
            challenge.current_participants += 1
            
            self.logger.info(f"User {user_id} joined challenge {challenge.title}")
            
            return {
                "success": True,
                "participation_id": participation.id,
                "challenge": {
                    "id": challenge.id,
                    "title": challenge.title,
                    "description": challenge.description,
                    "end_date": challenge.end_date,
                    "requirements": [
                        {
                            "name": req.name,
                            "description": req.description,
                            "target_value": req.target_value,
                            "metric_key": req.metric_key
                        } for req in challenge.requirements
                    ],
                    "rewards": [
                        {
                            "type": reward.reward_type,
                            "value": reward.value,
                            "description": reward.description
                        } for reward in challenge.rewards
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error joining challenge: {e}")
            return {"success": False, "error": str(e)}
    
    async def _check_prerequisites(self, user_id: str, prerequisites: List[str]) -> bool:
        """Check if user meets challenge prerequisites."""
        try:
            # This would integrate with achievement system, tier system, etc.
            # For now, we'll implement basic logic
            
            for prerequisite in prerequisites:
                # Check if user has completed prerequisite challenge
                if prerequisite.endswith("_challenge"):
                    completed = False
                    if user_id in self.participations:
                        for participation in self.participations[user_id]:
                            if (participation.status == ParticipationStatus.COMPLETED and
                                self.challenges.get(participation.challenge_id, {}).get("template_id") == prerequisite):
                                completed = True
                                break
                    
                    if not completed:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking prerequisites: {e}")
            return False
    
    async def update_progress(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user progress on active challenges."""
        try:
            if user_id not in self.participations:
                return {"progress": [], "completed": []}
            
            progress_updates = []
            completed_challenges = []
            
            # Get user's active participations
            active_participations = [
                p for p in self.participations[user_id]
                if p.status in [ParticipationStatus.JOINED, ParticipationStatus.IN_PROGRESS]
            ]
            
            for participation in active_participations:
                challenge = self.challenges.get(participation.challenge_id)
                if not challenge or challenge.status != ChallengeStatus.ACTIVE:
                    continue
                
                # Update progress based on action
                progress_updated = await self._update_participation_progress(
                    participation, challenge, action_type, action_data
                )
                
                if progress_updated:
                    progress_updates.append({
                        "challenge_id": challenge.id,
                        "challenge_title": challenge.title,
                        "progress_percentage": participation.completion_percentage,
                        "requirements_met": self._get_requirements_status(participation, challenge)
                    })
                    
                    # Check if challenge is completed
                    if participation.completion_percentage >= 100.0:
                        participation.status = ParticipationStatus.COMPLETED
                        participation.completed_at = datetime.utcnow()
                        
                        # Award rewards
                        await self._award_challenge_rewards(user_id, challenge)
                        
                        completed_challenges.append({
                            "challenge_id": challenge.id,
                            "challenge_title": challenge.title,
                            "rewards": [
                                {
                                    "type": reward.reward_type,
                                    "value": reward.value,
                                    "description": reward.description
                                } for reward in challenge.rewards
                            ]
                        })
                        
                        # Update challenge completion count
                        challenge.completion_count += 1
                        
                        self.logger.info(f"User {user_id} completed challenge {challenge.title}")
            
            return {
                "progress": progress_updates,
                "completed": completed_challenges
            }
            
        except Exception as e:
            self.logger.error(f"Error updating challenge progress: {e}")
            return {"progress": [], "error": str(e)}
    
    async def _update_participation_progress(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> bool:
        """Update progress for a specific participation."""
        try:
            progress_updated = False
            
            for requirement in challenge.requirements:
                metric_key = requirement.metric_key
                
                # Map action types to metrics
                metric_updates = self._get_metric_updates(action_type, action_data)
                
                if metric_key in metric_updates:
                    # Update metric value
                    current_value = participation.progress_data.get(metric_key, 0)
                    new_value = metric_updates[metric_key]
                    
                    # Apply update based on metric type
                    if metric_key.endswith("_count") or metric_key.endswith("_uploads"):
                        participation.progress_data[metric_key] = current_value + new_value
                    elif metric_key.endswith("_rate") or metric_key.endswith("_score"):
                        # Calculate average for rates and scores
                        update_count = participation.progress_data.get(f"{metric_key}_updates", 0)
                        if update_count == 0:
                            participation.progress_data[metric_key] = new_value
                        else:
                            participation.progress_data[metric_key] = (
                                (current_value * update_count + new_value) / (update_count + 1)
                            )
                        participation.progress_data[f"{metric_key}_updates"] = update_count + 1
                    else:
                        participation.progress_data[metric_key] = max(current_value, new_value)
                    
                    progress_updated = True
            
            if progress_updated:
                # Update participation status
                if participation.status == ParticipationStatus.JOINED:
                    participation.status = ParticipationStatus.IN_PROGRESS
                
                # Calculate overall completion percentage
                participation.completion_percentage = self._calculate_completion_percentage(
                    participation, challenge
                )
            
            return progress_updated
            
        except Exception as e:
            self.logger.error(f"Error updating participation progress: {e}")
            return False
    
    def _get_metric_updates(self, action_type: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map action types to metric updates."""
        updates = {}
        
        if action_type == "content_upload":
            updates["daily_uploads"] = 1
            updates["weekly_uploads"] = 1
            updates["weekly_content_count"] = 1
            
            # Check for themed content
            if action_data.get("theme") == "winter":
                updates["winter_themed_content"] = 1
            
            # Quality score
            if "quality_score" in action_data:
                updates["daily_quality_score"] = action_data["quality_score"]
                updates["weekly_avg_quality"] = action_data["quality_score"]
                updates["video_quality_score"] = action_data["quality_score"]
        
        elif action_type == "collaboration_success":
            updates["weekly_collaborations"] = 1
            updates["collaborations"] = 1
        
        elif action_type == "engagement_update":
            if "engagement_rate" in action_data:
                updates["daily_engagement_rate"] = action_data["engagement_rate"]
                updates["seasonal_engagement"] = action_data["engagement_rate"]
        
        elif action_type == "follower_gained":
            # Calculate growth rate (would need baseline data)
            updates["monthly_follower_growth"] = action_data.get("growth_rate", 0.01)
        
        elif action_type == "community_contribution":
            updates["community_projects"] = 1
            updates["project_contribution_score"] = action_data.get("contribution_score", 0.8)
        
        elif action_type == "leaderboard_update":
            if "position" in action_data:
                updates["leaderboard_position"] = action_data["position"]
        
        return updates
    
    def _calculate_completion_percentage(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> float:
        """Calculate overall completion percentage for a challenge."""
        try:
            total_weight = sum(req.weight for req in challenge.requirements if not req.is_optional)
            if total_weight == 0:
                return 0.0
            
            weighted_completion = 0.0
            
            for requirement in challenge.requirements:
                if requirement.is_optional:
                    continue
                
                current_value = participation.progress_data.get(requirement.metric_key, 0)
                target_value = requirement.target_value
                
                # Calculate requirement completion
                if requirement.comparison_operator == ">=":
                    req_completion = min(1.0, current_value / target_value)
                elif requirement.comparison_operator == "<=":
                    req_completion = 1.0 if current_value <= target_value else 0.0
                elif requirement.comparison_operator == "==":
                    req_completion = 1.0 if abs(current_value - target_value) < 0.01 else 0.0
                else:
                    req_completion = min(1.0, current_value / target_value)
                
                weighted_completion += req_completion * requirement.weight
            
            return (weighted_completion / total_weight) * 100.0
            
        except Exception as e:
            self.logger.error(f"Error calculating completion percentage: {e}")
            return 0.0
    
    def _get_requirements_status(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> List[Dict[str, Any]]:
        """Get detailed status of each requirement."""
        requirements_status = []
        
        for requirement in challenge.requirements:
            current_value = participation.progress_data.get(requirement.metric_key, 0)
            target_value = requirement.target_value
            
            is_met = False
            if requirement.comparison_operator == ">=":
                is_met = current_value >= target_value
            elif requirement.comparison_operator == "<=":
                is_met = current_value <= target_value
            elif requirement.comparison_operator == "==":
                is_met = abs(current_value - target_value) < 0.01
            
            requirements_status.append({
                "name": requirement.name,
                "current_value": current_value,
                "target_value": target_value,
                "is_met": is_met,
                "is_optional": requirement.is_optional,
                "progress_percentage": min(100.0, (current_value / target_value) * 100.0) if target_value > 0 else 0.0
            })
        
        return requirements_status
    
    async def _award_challenge_rewards(self, user_id: str, challenge: Challenge):
        """Award rewards for challenge completion."""
        try:
            # This would integrate with reward distribution system
            self.logger.info(f"Awarding {len(challenge.rewards)} rewards to user {user_id} for completing challenge {challenge.title}")
            
            # For now, just log the rewards
            for reward in challenge.rewards:
                self.logger.info(f"Reward: {reward.reward_type} - {reward.value} ({reward.description})")
            
        except Exception as e:
            self.logger.error(f"Error awarding challenge rewards: {e}")
    
    async def get_user_challenges(self, user_id: str) -> Dict[str, Any]:
        """Get user's challenge information."""
        try:
            user_participations = self.participations.get(user_id, [])
            
            # Categorize challenges
            active_challenges = []
            completed_challenges = []
            available_challenges = []
            
            # Process user's participations
            for participation in user_participations:
                challenge = self.challenges.get(participation.challenge_id)
                if not challenge:
                    continue
                
                challenge_info = {
                    "id": challenge.id,
                    "title": challenge.title,
                    "description": challenge.description,
                    "type": challenge.challenge_type.value,
                    "difficulty": challenge.difficulty.value,
                    "end_date": challenge.end_date,
                    "participation": {
                        "status": participation.status.value,
                        "progress": participation.completion_percentage,
                        "joined_at": participation.joined_at,
                        "completed_at": participation.completed_at
                    },
                    "requirements": self._get_requirements_status(participation, challenge),
                    "rewards": [
                        {
                            "type": reward.reward_type,
                            "value": reward.value,
                            "description": reward.description
                        } for reward in challenge.rewards
                    ]
                }
                
                if participation.status == ParticipationStatus.COMPLETED:
                    completed_challenges.append(challenge_info)
                else:
                    active_challenges.append(challenge_info)
            
            # Find available challenges (not yet joined)
            joined_challenge_ids = {p.challenge_id for p in user_participations}
            for challenge in self.active_challenges.values():
                if (challenge.id not in joined_challenge_ids and
                    challenge.status == ChallengeStatus.ACTIVE and
                    datetime.utcnow() < challenge.end_date):
                    
                    # Check prerequisites
                    can_join = True
                    if challenge.prerequisites:
                        can_join = await self._check_prerequisites(user_id, challenge.prerequisites)
                    
                    if can_join:
                        available_challenges.append({
                            "id": challenge.id,
                            "title": challenge.title,
                            "description": challenge.description,
                            "type": challenge.challenge_type.value,
                            "difficulty": challenge.difficulty.value,
                            "end_date": challenge.end_date,
                            "participants": challenge.current_participants,
                            "max_participants": challenge.max_participants,
                            "requirements": [
                                {
                                    "name": req.name,
                                    "description": req.description,
                                    "target_value": req.target_value
                                } for req in challenge.requirements
                            ],
                            "rewards": [
                                {
                                    "type": reward.reward_type,
                                    "value": reward.value,
                                    "description": reward.description
                                } for reward in challenge.rewards
                            ]
                        })
            
            return {
                "user_id": user_id,
                "active": active_challenges,
                "completed": completed_challenges,
                "available": available_challenges,
                "statistics": {
                    "total_completed": len(completed_challenges),
                    "total_active": len(active_challenges),
                    "completion_rate": (
                        len(completed_challenges) / len(user_participations) * 100
                    ) if user_participations else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user challenges: {e}")
            return {}
    
    async def _generate_daily_challenges(self):
        """Background task to generate daily challenges."""
        while True:
            try:
                await asyncio.sleep(86400)  # Wait 24 hours
                
                # Generate daily challenges
                daily_templates = [
                    template for template in self.challenge_templates.values()
                    if template.challenge_type == ChallengeType.DAILY and template.is_active
                ]
                
                for template in daily_templates:
                    # Generate challenge with some variation
                    challenge = await self.create_challenge_from_template(template.id)
                    if challenge:
                        self.logger.info(f"Generated daily challenge: {challenge.title}")
                
            except Exception as e:
                self.logger.error(f"Error in daily challenge generation: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _update_challenge_status(self):
        """Background task to update challenge statuses."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = datetime.utcnow()
                
                # Check for expired challenges
                expired_challenges = []
                for challenge_id, challenge in self.active_challenges.items():
                    if current_time > challenge.end_date and challenge.status == ChallengeStatus.ACTIVE:
                        challenge.status = ChallengeStatus.EXPIRED
                        expired_challenges.append(challenge_id)
                
                # Move expired challenges
                for challenge_id in expired_challenges:
                    challenge = self.active_challenges.pop(challenge_id)
                    self.completed_challenges.append(challenge)
                
                if expired_challenges:
                    self.logger.info(f"Expired {len(expired_challenges)} challenges")
                
            except Exception as e:
                self.logger.error(f"Error updating challenge status: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
    
    async def _cleanup_expired_challenges(self):
        """Background task to cleanup old challenge data."""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                
                # Keep completed challenges for 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                old_challenges = [
                    challenge for challenge in self.completed_challenges
                    if challenge.end_date < cutoff_date
                ]
                
                # Remove old challenges
                for challenge in old_challenges:
                    self.completed_challenges.remove(challenge)
                    if challenge.id in self.challenges:
                        del self.challenges[challenge.id]
                
                if old_challenges:
                    self.logger.info(f"Cleaned up {len(old_challenges)} old challenges")
                
            except Exception as e:
                self.logger.error(f"Error in challenge cleanup: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour