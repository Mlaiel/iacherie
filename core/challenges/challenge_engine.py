"""🎯 Challenge Engine Core - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/core/challenges/challenge_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Challenge Engine - Production-Ready
Responsibility: Core challenge creation, lifecycle, and management engine
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Challenge Creation → User Registration → Progress Tracking → Milestone Validation → 
Completion Assessment → Reward Distribution → Community Engagement

CHALLENGE ENGINE ARCHITECTURE:
Challenge Factory → Lifecycle Manager → Progress Tracker → 
Validation Engine → Reward Calculator → Analytics Collector
"""from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import logging
import asyncio
import uuid
from abc import ABC, abstractmethod

class ChallengeType(Enum):
    """Types of challenges available in the platform"""    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"
    COMMUNITY = "community"
    PERSONAL = "personal"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"

class ChallengeCategory(Enum):
    """Challenge categories based on content type and activity"""    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    ENGAGEMENT = "engagement"
    TECHNICAL_SKILL = "technical_skill"
    CREATIVE_SKILL = "creative_skill"
    REVENUE_GENERATION = "revenue_generation"
    COMMUNITY_BUILDING = "community_building"
    QUALITY_IMPROVEMENT = "quality_improvement"
    INNOVATION = "innovation"
    LEARNING = "learning"

class ChallengeStatus(Enum):
    """Challenge lifecycle status"""    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class ChallengeDifficulty(IntEnum):
    """Challenge difficulty levels (1-10)"""    BEGINNER = 1
    EASY = 2
    NOVICE = 3
    INTERMEDIATE = 4
    MODERATE = 5
    CHALLENGING = 6
    ADVANCED = 7
    EXPERT = 8
    MASTER = 9
    LEGENDARY = 10

class ChallengeVisibility(Enum):
    """Challenge visibility levels"""    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"
    TIER_RESTRICTED = "tier_restricted"
    VIP_ONLY = "vip_only"

@dataclass
class ChallengeRequirement:
    """Individual challenge requirement specification"""    requirement_id: str
    name: str
    description: str
    metric_type: str  # e.g., "upload_count", "quality_score", "views", "revenue"
    target_value: Union[int, float, Decimal]
    measurement_unit: str
    validation_function: Optional[str] = None
    weight: float = 1.0
    is_mandatory: bool = True
    time_bound: bool = False
    deadline: Optional[datetime] = None

@dataclass
class ChallengeReward:
    """Challenge reward specification"""    reward_id: str
    reward_type: str  # "virtual_currency", "real_money", "badge", "feature_unlock"
    reward_value: Union[int, float, Decimal, str]
    reward_description: str
    rarity_level: str = "common"  # "common", "rare", "epic", "legendary"
    is_tradeable: bool = False
    expiry_date: Optional[datetime] = None
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChallengeMilestone:
    """Challenge milestone for progressive rewards"""    milestone_id: str
    milestone_name: str
    progress_percentage: float  # 0.0 to 100.0
    reward: Optional[ChallengeReward] = None
    description: str = ""
    celebration_message: str = ""

@dataclass
class ChallengeConfiguration:
    """Complete challenge configuration"""    challenge_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    category: ChallengeCategory
    difficulty: ChallengeDifficulty
    visibility: ChallengeVisibility
    
    # Requirements and validation
    requirements: List[ChallengeRequirement]
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    start_date: datetime
    end_date: datetime
    duration_days: int = 0
    time_zone: str = "UTC"
    
    # Participation
    max_participants: Optional[int] = None
    min_participants: int = 1
    allow_teams: bool = False
    max_team_size: int = 1
    
    # Rewards and progression
    completion_rewards: List[ChallengeReward] = field(default_factory=list)
    milestones: List[ChallengeMilestone] = field(default_factory=list)
    participation_reward: Optional[ChallengeReward] = None
    
    # Gamification
    experience_points: int = 0
    skill_points: Dict[str, int] = field(default_factory=dict)
    achievement_unlock: List[str] = field(default_factory=list)
    
    # Social and community
    is_featured: bool = False
    allow_sharing: bool = True
    leaderboard_enabled: bool = True
    community_discussion: bool = True
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    creator_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"

class ChallengeEngine:
    """Core challenge engine for creating and managing challenges"""    
    def __init__(self, 
                 challenge_repository=None,
                 user_service=None,
                 analytics_service=None,
                 notification_service=None,
                 reward_service=None,
                 validation_service=None,
                 gamification_service=None):
        """Initialize challenge engine with dependencies"""        self.challenge_repository = challenge_repository
        self.user_service = user_service
        self.analytics_service = analytics_service
        self.notification_service = notification_service
        self.reward_service = reward_service
        self.validation_service = validation_service
        self.gamification_service = gamification_service
        
        self.logger = logging.getLogger(__name__)
        
        # Challenge type configurations
        self._challenge_type_configs = {
            ChallengeType.DAILY: {
                "default_duration": 1,
                "max_duration": 1,
                "experience_multiplier": 1.0,
                "max_participants": 10000
            },
            ChallengeType.WEEKLY: {
                "default_duration": 7,
                "max_duration": 7,
                "experience_multiplier": 2.5,
                "max_participants": 5000
            },
            ChallengeType.MONTHLY: {
                "default_duration": 30,
                "max_duration": 31,
                "experience_multiplier": 8.0,
                "max_participants": 2000
            },
            ChallengeType.SEASONAL: {
                "default_duration": 90,
                "max_duration": 120,
                "experience_multiplier": 20.0,
                "max_participants": 1000
            },
            ChallengeType.SPECIAL_EVENT: {
                "default_duration": 14,
                "max_duration": 30,
                "experience_multiplier": 25.0,
                "max_participants": 500
            }
        }
        
        # Difficulty multipliers for rewards and experience
        self._difficulty_multipliers = {
            ChallengeDifficulty.BEGINNER: 1.0,
            ChallengeDifficulty.EASY: 1.2,
            ChallengeDifficulty.NOVICE: 1.5,
            ChallengeDifficulty.INTERMEDIATE: 1.8,
            ChallengeDifficulty.MODERATE: 2.2,
            ChallengeDifficulty.CHALLENGING: 2.7,
            ChallengeDifficulty.ADVANCED: 3.3,
            ChallengeDifficulty.EXPERT: 4.0,
            ChallengeDifficulty.MASTER: 5.0,
            ChallengeDifficulty.LEGENDARY: 6.5
        }
    
    async def create_challenge(self, config: ChallengeConfiguration) -> Dict[str, Any]:
        """Create a new challenge with comprehensive validation"""        try:
            # Validate challenge configuration
            validation_result = await self._validate_challenge_config(config)
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error": "Invalid challenge configuration",
                    "validation_errors": validation_result["errors"]
                }
            
            # Generate unique challenge ID if not provided
            if not config.challenge_id:
                config.challenge_id = f"ch_{uuid.uuid4().hex[:12]}"
            
            # Apply challenge type defaults
            config = self._apply_challenge_type_defaults(config)
            
            # Calculate experience points and rewards
            config = self._calculate_challenge_rewards(config)
            
            # Set initial status
            status = ChallengeStatus.DRAFT if not config.creator_id else ChallengeStatus.PENDING_APPROVAL
            
            # Create challenge record
            challenge_data = {
                "challenge_id": config.challenge_id,
                "configuration": config.__dict__,
                "status": status.value,
                "participants_count": 0,
                "completion_count": 0,
                "creation_timestamp": datetime.now(timezone.utc),
                "metrics": {
                    "views": 0,
                    "shares": 0,
                    "completion_rate": 0.0,
                    "average_score": 0.0
                }
            }
            
            # Save to repository
            challenge = await self.challenge_repository.create_challenge(challenge_data)
            
            # Track analytics
            if self.analytics_service:
                await self.analytics_service.track_event(
                    "challenge_created",
                    {
                        "challenge_id": config.challenge_id,
                        "challenge_type": config.challenge_type.value,
                        "category": config.category.value,
                        "difficulty": config.difficulty.value,
                        "creator_id": config.creator_id
                    }
                )
            
            self.logger.info(f"Challenge created successfully: {config.challenge_id}")
            
            return {
                "success": True,
                "challenge_id": config.challenge_id,
                "challenge": challenge,
                "status": status.value,
                "estimated_participants": self._estimate_participants(config)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create challenge: {str(e)}")
            return {
                "success": False,
                "error": f"Challenge creation failed: {str(e)}"
            }
    
    async def register_user_for_challenge(self, 
                                        challenge_id: str, 
                                        user_id: str,
                                        team_id: Optional[str] = None) -> Dict[str, Any]:
        """Register user for challenge participation"""        try:
            # Get challenge configuration
            challenge = await self.challenge_repository.get_challenge(challenge_id)
            if not challenge:
                return {"success": False, "error": "Challenge not found"}
            
            config = ChallengeConfiguration(**challenge["configuration"])
            
            # Validate registration eligibility
            eligibility = await self._check_registration_eligibility(
                challenge_id, user_id, config
            )
            
            if not eligibility["eligible"]:
                return {
                    "success": False,
                    "error": "Registration not allowed",
                    "reason": eligibility["reason"]
                }
            
            # Create participation record
            participation_data = {
                "participation_id": f"{user_id}_{challenge_id}",
                "challenge_id": challenge_id,
                "user_id": user_id,
                "team_id": team_id,
                "registration_date": datetime.now(timezone.utc),
                "status": "registered",
                "progress": {},
                "milestones_achieved": [],
                "current_score": 0.0,
                "completion_percentage": 0.0
            }
            
            # Register in repository
            participation = await self.challenge_repository.register_user_for_challenge(
                user_id, challenge_id, participation_data
            )
            
            # Send notification
            if self.notification_service:
                await self.notification_service.send_notification(
                    user_id,
                    "challenge_registration_success",
                    {
                        "challenge_title": config.title,
                        "challenge_id": challenge_id,
                        "start_date": config.start_date.isoformat()
                    }
                )
            
            # Track analytics
            if self.analytics_service:
                await self.analytics_service.track_event(
                    "challenge_registration",
                    {
                        "challenge_id": challenge_id,
                        "user_id": user_id,
                        "challenge_type": config.challenge_type.value,
                        "difficulty": config.difficulty.value
                    }
                )
            
            return {
                "success": True,
                "participation": participation,
                "challenge_starts": config.start_date,
                "requirements_summary": self._get_requirements_summary(config)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to register user for challenge: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_user_progress(self, 
                                 challenge_id: str, 
                                 user_id: str,
                                 progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user progress on challenge"""        try:
            # Get current participation
            participation = await self.challenge_repository.get_user_participation(
                challenge_id, user_id
            )
            
            if not participation:
                return {"success": False, "error": "Participation not found"}
            
            # Get challenge configuration
            challenge = await self.challenge_repository.get_challenge(challenge_id)
            config = ChallengeConfiguration(**challenge["configuration"])
            
            # Validate and process progress update
            progress_result = await self._process_progress_update(
                config, participation, progress_data
            )
            
            if not progress_result["valid"]:
                return {
                    "success": False,
                    "error": "Invalid progress data",
                    "details": progress_result["errors"]
                }
            
            # Update participation record
            updated_participation = await self.challenge_repository.update_user_progress(
                challenge_id, user_id, progress_result["updated_progress"]
            )
            
            # Check for milestone achievements
            milestone_results = await self._check_milestone_achievements(
                config, updated_participation
            )
            
            # Check for challenge completion
            completion_result = await self._check_challenge_completion(
                config, updated_participation
            )
            
            # Process rewards if applicable
            rewards_granted = []
            if milestone_results["milestones_achieved"]:
                rewards_granted.extend(
                    await self._grant_milestone_rewards(
                        user_id, milestone_results["milestones_achieved"]
                    )
                )
            
            if completion_result["completed"]:
                completion_rewards = await self._grant_completion_rewards(
                    user_id, config, completion_result
                )
                rewards_granted.extend(completion_rewards)
            
            # Send notifications
            if self.notification_service:
                await self._send_progress_notifications(
                    user_id, config, milestone_results, completion_result
                )
            
            return {
                "success": True,
                "participation": updated_participation,
                "milestones_achieved": milestone_results["milestones_achieved"],
                "completed": completion_result["completed"],
                "rewards_granted": rewards_granted,
                "next_milestone": milestone_results.get("next_milestone")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update user progress: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_active_challenges(self, 
                                  user_id: Optional[str] = None,
                                  category: Optional[ChallengeCategory] = None,
                                  difficulty: Optional[ChallengeDifficulty] = None) -> List[Dict[str, Any]]:
        """Get list of active challenges with optional filtering"""        try:
            # Build filter criteria
            filters = {"status": ChallengeStatus.ACTIVE.value}
            
            if category:
                filters["category"] = category.value
            
            if difficulty:
                filters["difficulty"] = difficulty.value
            
            # Get challenges from repository
            challenges = await self.challenge_repository.get_challenges_by_filter(filters)
            
            # Enrich with user-specific data if user_id provided
            if user_id:
                challenges = await self._enrich_challenges_for_user(challenges, user_id)
            
            # Sort by relevance and engagement
            challenges = self._sort_challenges_by_relevance(challenges, user_id)
            
            return challenges
            
        except Exception as e:
            self.logger.error(f"Failed to get active challenges: {str(e)}")
            return []
    
    async def get_challenge_leaderboard(self, 
                                      challenge_id: str,
                                      limit: int = 100) -> Dict[str, Any]:
        """Get challenge leaderboard with rankings"""        try:
            # Get challenge configuration
            challenge = await self.challenge_repository.get_challenge(challenge_id)
            if not challenge:
                return {"success": False, "error": "Challenge not found"}
            
            config = ChallengeConfiguration(**challenge["configuration"])
            
            # Get all participations for this challenge
            participations = await self.challenge_repository.get_challenge_participations(
                challenge_id, include_completed=True
            )
            
            # Calculate scores and rankings
            leaderboard = await self._calculate_leaderboard_rankings(
                config, participations, limit
            )
            
            return {
                "success": True,
                "challenge_id": challenge_id,
                "challenge_title": config.title,
                "leaderboard": leaderboard,
                "total_participants": len(participations),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get challenge leaderboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Private helper methods
    
    async def _validate_challenge_config(self, config: ChallengeConfiguration) -> Dict[str, Any]:
        """Validate challenge configuration"""        errors = []
        
        # Basic validation
        if not config.title or len(config.title.strip()) < 3:
            errors.append("Challenge title must be at least 3 characters")
        
        if not config.description or len(config.description.strip()) < 10:
            errors.append("Challenge description must be at least 10 characters")
        
        if not config.requirements:
            errors.append("Challenge must have at least one requirement")
        
        # Date validation
        if config.start_date >= config.end_date:
            errors.append("End date must be after start date")
        
        if config.start_date < datetime.now(timezone.utc) - timedelta(minutes=5):
            errors.append("Start date cannot be in the past")
        
        # Participant validation
        if config.max_participants and config.max_participants < config.min_participants:
            errors.append("Maximum participants cannot be less than minimum")
        
        # Requirement validation
        for req in config.requirements:
            if req.target_value <= 0:
                errors.append(f"Requirement '{req.name}' must have positive target value")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def _apply_challenge_type_defaults(self, config: ChallengeConfiguration) -> ChallengeConfiguration:
        """Apply default settings based on challenge type"""        type_config = self._challenge_type_configs.get(config.challenge_type, {})
        
        # Set default duration if not specified
        if config.duration_days == 0:
            config.duration_days = type_config.get("default_duration", 7)
        
        # Adjust max participants based on type
        if not config.max_participants:
            config.max_participants = type_config.get("max_participants", 1000)
        
        return config
    
    def _calculate_challenge_rewards(self, config: ChallengeConfiguration) -> ChallengeConfiguration:
        """Calculate experience points and rewards based on difficulty and type"""        type_config = self._challenge_type_configs.get(config.challenge_type, {})
        type_multiplier = type_config.get("experience_multiplier", 1.0)
        difficulty_multiplier = self._difficulty_multipliers.get(config.difficulty, 1.0)
        
        # Calculate base experience points
        base_exp = 100 * config.duration_days
        config.experience_points = int(base_exp * type_multiplier * difficulty_multiplier)
        
        # Enhance rewards based on difficulty
        for reward in config.completion_rewards:
            if reward.reward_type == "virtual_currency":
                original_value = float(reward.reward_value)
                reward.reward_value = int(original_value * difficulty_multiplier)
        
        return config
    
    async def _check_registration_eligibility(self, 
                                            challenge_id: str, 
                                            user_id: str,
                                            config: ChallengeConfiguration) -> Dict[str, Any]:
        """Check if user is eligible to register for challenge"""        # Check if challenge is active for registration
        if datetime.now(timezone.utc) > config.start_date:
            return {"eligible": False, "reason": "Challenge has already started"}
        
        # Check if user is already registered
        existing_participation = await self.challenge_repository.get_user_participation(
            challenge_id, user_id
        )
        
        if existing_participation:
            return {"eligible": False, "reason": "User already registered"}
        
        # Check participant limits
        current_participants = await self.challenge_repository.get_participants_count(
            challenge_id
        )
        
        if config.max_participants and current_participants >= config.max_participants:
            return {"eligible": False, "reason": "Challenge is at maximum capacity"}
        
        # Check user tier restrictions (if applicable)
        if config.visibility == ChallengeVisibility.TIER_RESTRICTED:
            user_tier = await self._get_user_tier(user_id)
            if not self._check_tier_eligibility(user_tier, config):
                return {"eligible": False, "reason": "User tier not eligible"}
        
        return {"eligible": True}
    
    def _get_requirements_summary(self, config: ChallengeConfiguration) -> List[Dict[str, Any]]:
        """Get summarized requirements for user display"""        return [
            {
                "name": req.name,
                "description": req.description,
                "target": req.target_value,
                "unit": req.measurement_unit,
                "is_mandatory": req.is_mandatory
            }
            for req in config.requirements
        ]
    
    async def _process_progress_update(self, 
                                     config: ChallengeConfiguration,
                                     participation: Dict[str, Any],
                                     progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate progress update"""        try:
            current_progress = participation.get("progress", {})
            updated_progress = current_progress.copy()
            
            # Validate each progress metric
            for metric, value in progress_data.items():
                # Find corresponding requirement
                requirement = next(
                    (req for req in config.requirements if req.metric_type == metric),
                    None
                )
                
                if not requirement:
                    continue
                
                # Validate value type and range
                if not isinstance(value, (int, float)) or value < 0:
                    return {"valid": False, "errors": [f"Invalid value for {metric}"]}
                
                # Update progress (accumulative for most metrics)
                if metric in ["upload_count", "collaboration_count", "views"]:
                    updated_progress[metric] = updated_progress.get(metric, 0) + value
                else:
                    updated_progress[metric] = max(updated_progress.get(metric, 0), value)
            
            # Calculate overall completion percentage
            completion_percentage = self._calculate_completion_percentage(
                config, updated_progress
            )
            
            return {
                "valid": True,
                "updated_progress": {
                    **updated_progress,
                    "completion_percentage": completion_percentage,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}
    
    def _calculate_completion_percentage(self, 
                                       config: ChallengeConfiguration,
                                       progress: Dict[str, Any]) -> float:
        """Calculate overall completion percentage"""        total_weight = sum(req.weight for req in config.requirements)
        weighted_completion = 0.0
        
        for requirement in config.requirements:
            current_value = progress.get(requirement.metric_type, 0)
            requirement_completion = min(
                current_value / requirement.target_value, 1.0
            )
            weighted_completion += requirement_completion * requirement.weight
        
        return round((weighted_completion / total_weight) * 100, 2)
    
    async def _check_milestone_achievements(self, 
                                          config: ChallengeConfiguration,
                                          participation: Dict[str, Any]) -> Dict[str, Any]:
        """Check for milestone achievements"""        current_percentage = participation.get("completion_percentage", 0.0)
        achieved_milestones = participation.get("milestones_achieved", [])
        
        new_milestones = []
        next_milestone = None
        
        for milestone in sorted(config.milestones, key=lambda m: m.progress_percentage):
            if (milestone.progress_percentage <= current_percentage and 
                milestone.milestone_id not in achieved_milestones):
                new_milestones.append(milestone)
            elif milestone.progress_percentage > current_percentage and not next_milestone:
                next_milestone = milestone
                break
        
        return {
            "milestones_achieved": new_milestones,
            "next_milestone": next_milestone
        }
    
    async def _check_challenge_completion(self, 
                                        config: ChallengeConfiguration,
                                        participation: Dict[str, Any]) -> Dict[str, Any]:
        """Check if challenge is completed"""        completion_percentage = participation.get("completion_percentage", 0.0)
        progress = participation.get("progress", {})
        
        # Check if all mandatory requirements are met
        all_mandatory_met = True
        completion_details = {}
        
        for requirement in config.requirements:
            if requirement.is_mandatory:
                current_value = progress.get(requirement.metric_type, 0)
                requirement_met = current_value >= requirement.target_value
                completion_details[requirement.metric_type] = {
                    "required": requirement.target_value,
                    "achieved": current_value,
                    "met": requirement_met
                }
                
                if not requirement_met:
                    all_mandatory_met = False
        
        completed = all_mandatory_met and completion_percentage >= 100.0
        
        return {
            "completed": completed,
            "completion_percentage": completion_percentage,
            "requirements_status": completion_details,
            "completion_timestamp": datetime.now(timezone.utc).isoformat() if completed else None
        }
    
    async def _grant_milestone_rewards(self, 
                                     user_id: str,
                                     milestones: List[ChallengeMilestone]) -> List[Dict[str, Any]]:
        """Grant rewards for achieved milestones"""        granted_rewards = []
        
        for milestone in milestones:
            if milestone.reward and self.reward_service:
                try:
                    reward_result = await self.reward_service.grant_reward(
                        user_id, milestone.reward.__dict__
                    )
                    granted_rewards.append({
                        "milestone_id": milestone.milestone_id,
                        "reward": milestone.reward.__dict__,
                        "grant_result": reward_result
                    })
                except Exception as e:
                    self.logger.error(f"Failed to grant milestone reward: {str(e)}")
        
        return granted_rewards
    
    async def _grant_completion_rewards(self, 
                                      user_id: str,
                                      config: ChallengeConfiguration,
                                      completion_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Grant rewards for challenge completion"""        granted_rewards = []
        
        # Grant completion rewards
        for reward in config.completion_rewards:
            if self.reward_service:
                try:
                    reward_result = await self.reward_service.grant_reward(
                        user_id, reward.__dict__
                    )
                    granted_rewards.append({
                        "reward_type": "completion",
                        "reward": reward.__dict__,
                        "grant_result": reward_result
                    })
                except Exception as e:
                    self.logger.error(f"Failed to grant completion reward: {str(e)}")
        
        # Grant experience points
        if config.experience_points > 0 and self.gamification_service:
            try:
                exp_result = await self.gamification_service.add_experience_points(
                    user_id, config.experience_points
                )
                granted_rewards.append({
                    "reward_type": "experience_points",
                    "amount": config.experience_points,
                    "result": exp_result
                })
            except Exception as e:
                self.logger.error(f"Failed to grant experience points: {str(e)}")
        
        return granted_rewards
    
    def _estimate_participants(self, config: ChallengeConfiguration) -> int:
        """Estimate expected number of participants"""        base_estimate = {
            ChallengeType.DAILY: 1000,
            ChallengeType.WEEKLY: 500,
            ChallengeType.MONTHLY: 200,
            ChallengeType.SEASONAL: 100,
            ChallengeType.SPECIAL_EVENT: 150
        }.get(config.challenge_type, 100)
        
        # Adjust based on difficulty
        difficulty_factor = {
            ChallengeDifficulty.BEGINNER: 1.5,
            ChallengeDifficulty.EASY: 1.3,
            ChallengeDifficulty.NOVICE: 1.1,
            ChallengeDifficulty.INTERMEDIATE: 1.0,
            ChallengeDifficulty.MODERATE: 0.8,
            ChallengeDifficulty.CHALLENGING: 0.6,
            ChallengeDifficulty.ADVANCED: 0.4,
            ChallengeDifficulty.EXPERT: 0.2,
            ChallengeDifficulty.MASTER: 0.1,
            ChallengeDifficulty.LEGENDARY: 0.05
        }.get(config.difficulty, 1.0)
        
        estimated = int(base_estimate * difficulty_factor)
        
        # Cap at max_participants if specified
        if config.max_participants:
            estimated = min(estimated, config.max_participants)
        
        return estimated
    
    async def _enrich_challenges_for_user(self, 
                                        challenges: List[Dict[str, Any]],
                                        user_id: str) -> List[Dict[str, Any]]:
        """Enrich challenges with user-specific data"""        enriched = []
        
        for challenge in challenges:
            challenge_id = challenge["challenge_id"]
            
            # Check if user is participating
            participation = await self.challenge_repository.get_user_participation(
                challenge_id, user_id
            )
            
            challenge["user_participation"] = participation
            challenge["is_participating"] = participation is not None
            
            if participation:
                challenge["user_progress"] = participation.get("completion_percentage", 0.0)
                challenge["user_rank"] = await self._get_user_rank_in_challenge(
                    challenge_id, user_id
                )
            
            enriched.append(challenge)
        
        return enriched
    
    def _sort_challenges_by_relevance(self, 
                                    challenges: List[Dict[str, Any]],
                                    user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Sort challenges by relevance and engagement"""        def relevance_score(challenge):
            score = 0
            
            # Prioritize challenges user is participating in
            if challenge.get("is_participating"):
                score += 1000
            
            # Prioritize featured challenges
            config = challenge.get("configuration", {})
            if config.get("is_featured"):
                score += 500
            
            # Factor in participant count (popular challenges)
            participants = challenge.get("participants_count", 0)
            score += min(participants / 10, 100)
            
            # Factor in recency
            created_at = challenge.get("creation_timestamp")
            if created_at:
                days_old = (datetime.now(timezone.utc) - created_at).days
                score += max(50 - days_old, 0)
            
            return score
        
        return sorted(challenges, key=relevance_score, reverse=True)
    
    async def _calculate_leaderboard_rankings(self, 
                                            config: ChallengeConfiguration,
                                            participations: List[Dict[str, Any]],
                                            limit: int) -> List[Dict[str, Any]]:
        """Calculate leaderboard rankings for challenge"""        scored_participants = []
        
        for participation in participations:
            score = self._calculate_participant_score(config, participation)
            
            scored_participants.append({
                "user_id": participation["user_id"],
                "score": score,
                "completion_percentage": participation.get("completion_percentage", 0.0),
                "milestones_achieved": len(participation.get("milestones_achieved", [])),
                "registration_date": participation.get("registration_date"),
                "status": participation.get("status")
            })
        
        # Sort by score (descending) and registration date (ascending for ties)
        leaderboard = sorted(
            scored_participants,
            key=lambda p: (-p["score"], p.get("registration_date", datetime.max))
        )
        
        # Add rankings
        for i, participant in enumerate(leaderboard[:limit]):
            participant["rank"] = i + 1
        
        return leaderboard[:limit]
    
    def _calculate_participant_score(self, 
                                   config: ChallengeConfiguration,
                                   participation: Dict[str, Any]) -> float:
        """Calculate score for participant in challenge"""        base_score = participation.get("completion_percentage", 0.0)
        
        # Bonus for milestones
        milestones_bonus = len(participation.get("milestones_achieved", [])) * 10
        
        # Time bonus (earlier completion gets bonus)
        completion_date = participation.get("completion_date")
        time_bonus = 0
        
        if completion_date and completion_date < config.end_date:
            days_early = (config.end_date - completion_date).days
            time_bonus = min(days_early * 2, 20)
        
        return base_score + milestones_bonus + time_bonus
    
    async def _send_progress_notifications(self, 
                                         user_id: str,
                                         config: ChallengeConfiguration,
                                         milestone_results: Dict[str, Any],
                                         completion_result: Dict[str, Any]):
        """Send appropriate notifications for progress updates"""        if not self.notification_service:
            return
        
        # Milestone achievement notifications
        for milestone in milestone_results.get("milestones_achieved", []):
            await self.notification_service.send_notification(
                user_id,
                "challenge_milestone_achieved",
                {
                    "challenge_title": config.title,
                    "milestone_name": milestone.milestone_name,
                    "celebration_message": milestone.celebration_message
                }
            )
        
        # Challenge completion notification
        if completion_result["completed"]:
            await self.notification_service.send_notification(
                user_id,
                "challenge_completed",
                {
                    "challenge_title": config.title,
                    "completion_percentage": completion_result["completion_percentage"],
                    "completion_timestamp": completion_result["completion_timestamp"]
                }
            )
    
    async def _get_user_tier(self, user_id: str) -> str:
        """Get user tier from user service"""        if self.user_service:
            try:
                user_data = await self.user_service.get_user_profile(user_id)
                return user_data.get("tier", "basic")
            except Exception:
                return "basic"
        return "basic"
    
    def _check_tier_eligibility(self, user_tier: str, config: ChallengeConfiguration) -> bool:
        """Check if user tier is eligible for challenge"""        # Simplified tier checking - would implement proper business logic
        tier_hierarchy = ["basic", "premium", "pro", "vip", "elite"]
        required_tier_index = tier_hierarchy.index("premium")  # Default requirement
        user_tier_index = tier_hierarchy.index(user_tier) if user_tier in tier_hierarchy else 0
        
        return user_tier_index >= required_tier_index
    
    async def _get_user_rank_in_challenge(self, challenge_id: str, user_id: str) -> Optional[int]:
        """Get user's current rank in challenge"""        try:
            leaderboard_result = await self.get_challenge_leaderboard(challenge_id, limit=1000)
            if leaderboard_result["success"]:
                for entry in leaderboard_result["leaderboard"]:
                    if entry["user_id"] == user_id:
                        return entry["rank"]
            return None
        except Exception:
            return None