"""🎯 Challenge Repository - IA Influencer Agent Platform Enterprise
=================================================================
Module: backend/database/gamification/challenge_repository.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Challenge Repository - Production-Ready
Responsibility: Challenge lifecycle management and competition data persistence
===============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Challenge Creation → User Participation → Progress Tracking → 
Competition Management → Reward Distribution → Community Engagement

CHALLENGE REPOSITORY ARCHITECTURE:
Challenge Lifecycle → Participation Management → Progress Analytics → 
Competition Engine → Reward Calculation → Performance Optimization
"""
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import asyncio
import hashlib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal

from ...data_management.repositories.base_repository import BaseRepository, OperationType

class ChallengeType(Enum):
    """Challenge duration types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    COMMUNITY = "community"
    SPECIAL_EVENT = "special_event"

class ChallengeCategory(Enum):
    """Challenge content categories"""
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    ENGAGEMENT = "engagement"
    QUALITY = "quality"
    CONSISTENCY = "consistency"
    INNOVATION = "innovation"
    COMMUNITY_BUILDING = "community_building"
    SKILL_DEVELOPMENT = "skill_development"

class ChallengeStatus(Enum):
    """Challenge lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class ParticipationStatus(Enum):
    """User participation status"""
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"

@dataclass
class Challenge:
    """Challenge data structure"""
    challenge_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    category: ChallengeCategory
    status: ChallengeStatus
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int]
    min_participants: int
    entry_requirements: Dict[str, Any]
    difficulty_level: int  # 1-10
    created_by: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

@dataclass
class ChallengeParticipation:
    """User challenge participation"""
    participation_id: str
    user_id: str
    challenge_id: str
    status: ParticipationStatus
    registration_date: datetime
    start_date: Optional[datetime]
    completion_date: Optional[datetime]
    current_progress: Dict[str, Any]
    progress_percentage: float
    score: Optional[float]
    rank: Optional[int]
    rewards_earned: Dict[str, Any]
    submission_data: Dict[str, Any]
    metadata: Dict[str, Any]

class ChallengeRepository(BaseRepository[Challenge]):
    """Enterprise challenge management repository"""
    
    def __init__(self, db_connection=None, cache_manager=None,
                 analytics_service=None, notification_service=None,
                 reward_service=None, gamification_service=None):
        super().__init__(db_connection, cache_manager)
        self.analytics_service = analytics_service
        self.notification_service = notification_service
        self.reward_service = reward_service
        self.gamification_service = gamification_service
        self.table_name = "challenges"
        self.participation_table = "challenge_participations"
        self.logger = logging.getLogger(__name__)
        
        # Challenge scoring weights by difficulty
        self._difficulty_multipliers = {
            1: 1.0, 2: 1.2, 3: 1.5, 4: 1.8, 5: 2.2,
            6: 2.7, 7: 3.3, 8: 4.0, 9: 5.0, 10: 6.5
        }
        
        # Type-based reward multipliers
        self._type_multipliers = {
            ChallengeType.DAILY: 1.0,
            ChallengeType.WEEKLY: 2.5,
            ChallengeType.MONTHLY: 8.0,
            ChallengeType.SEASONAL: 20.0,
            ChallengeType.COMMUNITY: 15.0,
            ChallengeType.SPECIAL_EVENT: 25.0
        }
        
        # Completion rate thresholds
        self._completion_thresholds = {
            "excellent": 0.95,
            "good": 0.80,
            "satisfactory": 0.60,
            "minimum": 0.40
        }
    
    def create_challenge(
        self,
        title: str,
        description: str,
        challenge_type: ChallengeType,
        category: ChallengeCategory,
        requirements: Dict[str, Any],
        rewards: Dict[str, Any],
        duration_days: int,
        difficulty_level: int = 5,
        max_participants: Optional[int] = None,
        min_participants: int = 1,
        entry_requirements: Optional[Dict[str, Any]] = None,
        created_by: str = "system",
        auto_start: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Challenge:
        """Create new challenge with validation"""
        try:
            # Validate inputs
            if not title or len(title) < 5:
                raise ValueError("Challenge title must be at least 5 characters")
            
            if not description or len(description) < 20:
                raise ValueError("Challenge description must be at least 20 characters")
            
            if not (1 <= difficulty_level <= 10):
                raise ValueError("Difficulty level must be between 1 and 10")
            
            if duration_days < 1:
                raise ValueError("Challenge duration must be at least 1 day")
            
            if max_participants and max_participants < min_participants:
                raise ValueError("Max participants cannot be less than min participants")
            
            challenge_id = self._generate_challenge_id(title, challenge_type)
            current_time = datetime.now(timezone.utc)
            
            # Calculate dates
            start_date = current_time if auto_start else current_time + timedelta(hours=1)
            end_date = start_date + timedelta(days=duration_days)
            
            challenge = Challenge(
                challenge_id=challenge_id,
                title=title,
                description=description,
                challenge_type=challenge_type,
                category=category,
                status=ChallengeStatus.ACTIVE if auto_start else ChallengeStatus.DRAFT,
                requirements=requirements,
                rewards=rewards,
                start_date=start_date,
                end_date=end_date,
                max_participants=max_participants,
                min_participants=min_participants,
                entry_requirements=entry_requirements or {},
                difficulty_level=difficulty_level,
                created_by=created_by,
                created_at=current_time,
                updated_at=current_time,
                metadata=metadata or {}
            )
            
            # Create challenge record
            created_challenge = self.create(challenge)
            
            # Schedule challenge activation if not auto-started
            if not auto_start:
                self._schedule_challenge_activation(challenge_id, start_date)
            
            # Track analytics
            if self.analytics_service:
                self.analytics_service.track_challenge_created(
                    challenge_id, category.value, challenge_type.value, difficulty_level
                )
            
            self.logger.info(f"Challenge created: {challenge_id} - {title}")
            return created_challenge
            
        except Exception as e:
            self.logger.error(f"Failed to create challenge: {str(e)}")
            raise
    
    def register_user_for_challenge(
        self,
        user_id: str,
        challenge_id: str,
        registration_data: Optional[Dict[str, Any]] = None
    ) -> Optional[ChallengeParticipation]:
        """Register user for challenge with validation"""
        try:
            # Get challenge details
            challenge = self.get_by_id(challenge_id)
            if not challenge:
                raise ValueError("Challenge not found")
            
            if challenge.status != ChallengeStatus.ACTIVE:
                raise ValueError("Challenge is not active for registration")
            
            # Check if already registered
            existing_participation = self.get_user_participation(user_id, challenge_id)
            if existing_participation:
                return existing_participation
            
            # Validate entry requirements
            if not self._validate_entry_requirements(user_id, challenge):
                raise ValueError("User does not meet entry requirements")
            
            # Check capacity
            if challenge.max_participants:
                current_participants = self.get_participant_count(challenge_id)
                if current_participants >= challenge.max_participants:
                    raise ValueError("Challenge is at maximum capacity")
            
            # Create participation record
            participation_id = f"{user_id}_{challenge_id}"
            current_time = datetime.now(timezone.utc)
            
            participation = ChallengeParticipation(
                participation_id=participation_id,
                user_id=user_id,
                challenge_id=challenge_id,
                status=ParticipationStatus.REGISTERED,
                registration_date=current_time,
                start_date=None,
                completion_date=None,
                current_progress={},
                progress_percentage=0.0,
                score=None,
                rank=None,
                rewards_earned={},
                submission_data=registration_data or {},
                metadata={"registration_source": "api"}
            )
            
            # Save participation
            saved_participation = self._save_participation(participation)
            
            # Send notification
            if self.notification_service:
                self.notification_service.send_challenge_registration_notification(
                    user_id, challenge
                )
            
            # Track analytics
            if self.analytics_service:
                self.analytics_service.track_challenge_registration(
                    user_id, challenge_id, challenge.category.value
                )
            
            self.logger.info(f"User registered for challenge: {user_id} -> {challenge_id}")
            return saved_participation
            
        except Exception as e:
            self.logger.error(f"Failed to register user for challenge: {str(e)}")
            return None
    
    def update_user_progress(
        self,
        user_id: str,
        challenge_id: str,
        progress_data: Dict[str, Any],
        auto_complete: bool = True
    ) -> Optional[ChallengeParticipation]:
        """Update user progress on challenge"""
        try:
            # Get participation record
            participation = self.get_user_participation(user_id, challenge_id)
            if not participation:
                return None
            
            if participation.status not in [ParticipationStatus.REGISTERED, ParticipationStatus.IN_PROGRESS]:
                return participation
            
            # Get challenge requirements
            challenge = self.get_by_id(challenge_id)
            if not challenge:
                return None
            
            # Calculate progress percentage
            progress_percentage = self._calculate_progress_percentage(
                challenge.requirements, progress_data
            )
            
            # Update participation
            current_time = datetime.now(timezone.utc)
            participation.current_progress = progress_data
            participation.progress_percentage = progress_percentage
            participation.status = ParticipationStatus.IN_PROGRESS
            participation.metadata["last_update"] = current_time.isoformat()
            
            # Check for completion
            if auto_complete and progress_percentage >= 100.0:
                participation = self._complete_user_challenge(participation, challenge)
            
            # Save updated participation
            updated_participation = self._save_participation(participation)
            
            # Track analytics
            if self.analytics_service:
                self.analytics_service.track_challenge_progress(
                    user_id, challenge_id, progress_percentage
                )
            
            return updated_participation
            
        except Exception as e:
            self.logger.error(f"Failed to update user progress: {str(e)}")
            return None
    
    def get_active_challenges(
        self,
        category: Optional[ChallengeCategory] = None,
        challenge_type: Optional[ChallengeType] = None,
        difficulty_min: Optional[int] = None,
        difficulty_max: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Challenge]:
        """Get active challenges with filtering"""
        try:
            cache_key = f"active_challenges:{category}:{challenge_type}:{difficulty_min}:{difficulty_max}:{limit}:{offset}"
            
            # Try cache first
            if self.cache_manager:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Build filters
            filters = {"status": ChallengeStatus.ACTIVE.value}
            current_time = datetime.now(timezone.utc)
            
            if category:
                filters["category"] = category.value
            if challenge_type:
                filters["challenge_type"] = challenge_type.value
            if difficulty_min:
                filters["difficulty_level_min"] = difficulty_min
            if difficulty_max:
                filters["difficulty_level_max"] = difficulty_max
            
            # Query active challenges
            challenges = self._query_challenges(filters, limit, offset)
            
            # Filter by date
            active_challenges = [
                c for c in challenges 
                if c.start_date <= current_time <= c.end_date
            ]
            
            # Cache result
            if self.cache_manager:
                self.cache_manager.set(cache_key, active_challenges, ttl=300)
            
            return active_challenges
            
        except Exception as e:
            self.logger.error(f"Failed to get active challenges: {str(e)}")
            return []
    
    def get_challenge_leaderboard(
        self,
        challenge_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get challenge leaderboard"""
        try:
            cache_key = f"challenge_leaderboard:{challenge_id}:{limit}"
            
            # Try cache first
            if self.cache_manager:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Query leaderboard data
            leaderboard = self._calculate_challenge_leaderboard(challenge_id, limit)
            
            # Cache result
            if self.cache_manager:
                self.cache_manager.set(cache_key, leaderboard, ttl=120)
            
            return leaderboard
            
        except Exception as e:
            self.logger.error(f"Failed to get challenge leaderboard: {str(e)}")
            return []
    
    def get_user_challenge_history(
        self,
        user_id: str,
        status: Optional[ParticipationStatus] = None,
        category: Optional[ChallengeCategory] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChallengeParticipation]:
        """Get user challenge participation history"""
        try:
            cache_key = f"user_challenge_history:{user_id}:{status}:{category}:{limit}:{offset}"
            
            # Try cache first
            if self.cache_manager:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Build filters
            filters = {"user_id": user_id}
            if status:
                filters["status"] = status.value
            if category:
                filters["challenge_category"] = category.value
            
            # Query participation history
            history = self._query_participations(filters, limit, offset)
            
            # Cache result
            if self.cache_manager:
                self.cache_manager.set(cache_key, history, ttl=600)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get user challenge history: {str(e)}")
            return []
    
    def get_challenge_analytics(
        self,
        challenge_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive challenge analytics"""
        try:
            cache_key = f"challenge_analytics:{challenge_id}"
            
            # Try cache first
            if self.cache_manager:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Calculate analytics
            analytics = self._calculate_challenge_analytics(challenge_id)
            
            # Cache result
            if self.cache_manager:
                self.cache_manager.set(cache_key, analytics, ttl=900)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get challenge analytics: {str(e)}")
            return {}
    
    def _generate_challenge_id(
        self,
        title: str,
        challenge_type: ChallengeType
    ) -> str:
        """Generate unique challenge ID"""
        base_string = f"{challenge_type.value}_{title.lower().replace(' ', '_')}"
        timestamp = str(int(datetime.now().timestamp()))
        return f"chal_{hashlib.md5((base_string + timestamp).encode()).hexdigest()[:12]}"
    
    def _validate_entry_requirements(
        self,
        user_id: str,
        challenge: Challenge
    ) -> bool:
        """Validate user meets challenge entry requirements"""
        try:
            entry_reqs = challenge.entry_requirements
            
            # Check minimum level requirement
            if "min_level" in entry_reqs:
                user_level = self._get_user_level(user_id)
                if user_level < entry_reqs["min_level"]:
                    return False
            
            # Check required achievements
            if "required_achievements" in entry_reqs:
                user_achievements = self._get_user_achievement_ids(user_id)
                required = set(entry_reqs["required_achievements"])
                if not required.issubset(set(user_achievements)):
                    return False
            
            # Check activity requirements
            if "min_activity_score" in entry_reqs:
                activity_score = self._get_user_activity_score(user_id)
                if activity_score < entry_reqs["min_activity_score"]:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating entry requirements: {str(e)}")
            return False
    
    def _calculate_progress_percentage(
        self,
        requirements: Dict[str, Any],
        progress_data: Dict[str, Any]
    ) -> float:
        """Calculate progress percentage based on requirements"""
        try:
            total_weight = 0
            completed_weight = 0
            
            for req_key, req_value in requirements.items():
                weight = 1.0  # Default weight
                if isinstance(req_value, dict) and "weight" in req_value:
                    weight = req_value["weight"]
                    target = req_value["target"]
                else:
                    target = req_value
                
                total_weight += weight
                
                # Calculate completion for this requirement
                current_value = progress_data.get(req_key, 0)
                if isinstance(current_value, (int, float)) and isinstance(target, (int, float)):
                    completion_ratio = min(current_value / target, 1.0)
                    completed_weight += weight * completion_ratio
                elif current_value == target:
                    completed_weight += weight
            
            return (completed_weight / total_weight * 100.0) if total_weight > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating progress percentage: {str(e)}")
            return 0.0
    
    def _complete_user_challenge(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> ChallengeParticipation:
        """Complete user challenge and calculate rewards"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Calculate completion score
            score = self._calculate_completion_score(participation, challenge)
            
            # Calculate rewards
            earned_rewards = self._calculate_challenge_rewards(challenge, score)
            
            # Update participation
            participation.status = ParticipationStatus.COMPLETED
            participation.completion_date = current_time
            participation.score = score
            participation.rewards_earned = earned_rewards
            participation.metadata["completion_time"] = current_time.isoformat()
            
            # Distribute rewards
            if self.reward_service and earned_rewards:
                self.reward_service.distribute_challenge_rewards(
                    participation.user_id, challenge.challenge_id, earned_rewards
                )
            
            # Update user experience
            if self.gamification_service and "experience_points" in earned_rewards:
                self.gamification_service.add_experience_points(
                    participation.user_id, earned_rewards["experience_points"]
                )
            
            # Send completion notification
            if self.notification_service:
                self.notification_service.send_challenge_completion_notification(
                    participation.user_id, challenge, score, earned_rewards
                )
            
            # Track analytics
            if self.analytics_service:
                self.analytics_service.track_challenge_completion(
                    participation.user_id, challenge.challenge_id, score
                )
            
            return participation
            
        except Exception as e:
            self.logger.error(f"Error completing user challenge: {str(e)}")
            return participation
    
    def _calculate_completion_score(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> float:
        """Calculate completion score based on performance"""
        base_score = participation.progress_percentage
        
        # Apply difficulty multiplier
        difficulty_multiplier = self._difficulty_multipliers.get(challenge.difficulty_level, 1.0)
        
        # Apply type multiplier
        type_multiplier = self._type_multipliers.get(challenge.challenge_type, 1.0)
        
        # Calculate time bonus (completed early gets bonus)
        time_bonus = self._calculate_time_bonus(participation, challenge)
        
        final_score = base_score * difficulty_multiplier * type_multiplier * (1 + time_bonus)
        return min(final_score, 1000.0)  # Cap at 1000 points
    
    def _calculate_time_bonus(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge
    ) -> float:
        """Calculate time-based completion bonus"""
        if not participation.completion_date:
            return 0.0
        
        total_duration = (challenge.end_date - challenge.start_date).total_seconds()
        time_taken = (participation.completion_date - challenge.start_date).total_seconds()
        
        if time_taken <= total_duration * 0.5:  # Completed in first half
            return 0.25  # 25% bonus
        elif time_taken <= total_duration * 0.75:  # Completed in first 3/4
            return 0.15  # 15% bonus
        elif time_taken <= total_duration * 0.9:  # Completed in first 90%
            return 0.05  # 5% bonus
        
        return 0.0  # No bonus
    
    def _calculate_challenge_rewards(
        self,
        challenge: Challenge,
        score: float
    ) -> Dict[str, Any]:
        """Calculate rewards based on challenge completion"""
        base_rewards = challenge.rewards.copy()
        
        # Apply score multiplier to numeric rewards
        score_multiplier = score / 100.0
        
        calculated_rewards = {}
        for reward_type, reward_value in base_rewards.items():
            if isinstance(reward_value, (int, float)):
                calculated_rewards[reward_type] = int(reward_value * score_multiplier)
            else:
                calculated_rewards[reward_type] = reward_value
        
        return calculated_rewards
    
    def _schedule_challenge_activation(self, challenge_id: str, start_date: datetime):
        """Schedule challenge activation"""
        # Implementation would schedule task for challenge activation
        pass
    
    def get_participant_count(self, challenge_id: str) -> int:
        """Get current participant count"""
        # Implementation would count participants
        return 0
    
    def get_user_participation(
        self,
        user_id: str,
        challenge_id: str
    ) -> Optional[ChallengeParticipation]:
        """Get user participation record"""
        # Implementation would query participation table
        return None
    
    def _save_participation(self, participation: ChallengeParticipation) -> ChallengeParticipation:
        """Save participation record"""
        # Implementation would save to database
        return participation
    
    def _query_challenges(
        self,
        filters: Dict[str, Any],
        limit: int,
        offset: int
    ) -> List[Challenge]:
        """Query challenges with filters"""
        # Implementation would execute filtered query
        return []
    
    def _query_participations(
        self,
        filters: Dict[str, Any],
        limit: int,
        offset: int
    ) -> List[ChallengeParticipation]:
        """Query participations with filters"""
        # Implementation would execute filtered query
        return []
    
    def _calculate_challenge_leaderboard(
        self,
        challenge_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Calculate challenge leaderboard"""
        # Implementation would calculate leaderboard
        return []
    
    def _calculate_challenge_analytics(self, challenge_id: str) -> Dict[str, Any]:
        """Calculate challenge analytics"""
        # Implementation would calculate analytics
        return {}
    
    def _get_user_level(self, user_id: str) -> int:
        """Get user level"""
        # Implementation would get user level
        return 1
    
    def _get_user_achievement_ids(self, user_id: str) -> List[str]:
        """Get user achievement IDs"""
        # Implementation would get achievement IDs
        return []
    
    def _get_user_activity_score(self, user_id: str) -> float:
        """Get user activity score"""
        # Implementation would calculate activity score
        return 0.0
    
    # BaseRepository abstract method implementations
    def create(self, entity: Challenge, **kwargs) -> Challenge:
        """Create challenge entity"""
        self._validate_entity(entity)
        # Implementation would save to database
        return entity
    
    def get_by_id(self, entity_id: str, use_cache: bool = True) -> Optional[Challenge]:
        """Get challenge by ID"""
        # Implementation would query database
        return None
    
    def update(self, entity: Challenge, **kwargs) -> Challenge:
        """Update challenge entity"""
        self._validate_entity(entity)
        # Implementation would update database
        return entity
    
    def delete(self, entity_id: str, **kwargs) -> bool:
        """Delete challenge"""
        # Implementation would delete from database
        return True
    
    def list_all(self, limit: int = 100, offset: int = 0, **filters) -> List[Challenge]:
        """List all challenges with filtering"""
        # Implementation would query with filters
        return []