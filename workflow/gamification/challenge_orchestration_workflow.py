"""Challenge Orchestration Workflow

AI-powered challenge creation and management workflow for gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class ChallengeType(Enum):
    """Types of challenges"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    COMMUNITY = "community"
    PERSONAL = "personal"


@dataclass
class Challenge:
    """Challenge definition"""
    challenge_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    target_metric: str
    target_value: float
    reward_points: int
    reward_items: List[str]
    start_date: datetime
    end_date: datetime
    difficulty: str = "medium"  # easy, medium, hard
    is_active: bool = True
    participant_count: int = 0


@dataclass
class ChallengeProgress:
    """User's progress on a challenge"""
    user_id: str
    challenge_id: str
    current_progress: float
    target_progress: float
    completion_percentage: float
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ChallengeOrchestrationWorkflow:
    """AI-powered challenge orchestration workflow"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.active_challenges: Dict[str, Challenge] = {}
        self.user_progress: Dict[str, List[ChallengeProgress]] = {}
        
    async def create_challenge(
        self,
        title: str,
        description: str,
        challenge_type: ChallengeType,
        target_metric: str,
        target_value: float,
        reward_points: int,
        duration_days: int = 7,
        difficulty: str = "medium"
    ) -> Challenge:
        """
        Create a new challenge
        
        Args:
            title: Challenge title
            description: Challenge description
            challenge_type: Type of challenge
            target_metric: Metric to track (e.g., 'posts_created', 'likes_received')
            target_value: Target value to achieve
            reward_points: Points awarded for completion
            duration_days: Challenge duration in days
            difficulty: Challenge difficulty level
            
        Returns:
            Challenge object
        """
        try:
            start_time = datetime.utcnow()
            challenge_id = f"challenge_{int(start_time.timestamp())}"
            
            logger.info(f"Creating challenge: {title}")
            
            # Calculate end date
            end_date = start_time + timedelta(days=duration_days)
            
            # Determine reward items based on difficulty
            reward_items = await self._get_reward_items(difficulty, challenge_type)
            
            challenge = Challenge(
                challenge_id=challenge_id,
                title=title,
                description=description,
                challenge_type=challenge_type,
                target_metric=target_metric,
                target_value=target_value,
                reward_points=reward_points,
                reward_items=reward_items,
                start_date=start_time,
                end_date=end_date,
                difficulty=difficulty
            )
            
            # Store challenge
            self.active_challenges[challenge_id] = challenge
            
            # Record metrics
            await self.metrics_collector.record_metric("challenges_created", 1)
            
            logger.info(f"Challenge created: {challenge_id}")
            return challenge
            
        except Exception as e:
            logger.error(f"Challenge creation failed: {e}")
            raise WorkflowError(f"Challenge creation failed: {e}")
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> ChallengeProgress:
        """
        User joins a challenge
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            
        Returns:
            ChallengeProgress object
        """
        try:
            if challenge_id not in self.active_challenges:
                raise WorkflowError(f"Challenge {challenge_id} not found")
            
            challenge = self.active_challenges[challenge_id]
            
            # Check if challenge is still active
            now = datetime.utcnow()
            if now > challenge.end_date:
                raise WorkflowError("Challenge has ended")
            
            # Check if user already joined
            user_progresses = self.user_progress.get(user_id, [])
            for progress in user_progresses:
                if progress.challenge_id == challenge_id:
                    return progress  # Already joined
            
            # Create progress tracker
            progress = ChallengeProgress(
                user_id=user_id,
                challenge_id=challenge_id,
                current_progress=0.0,
                target_progress=challenge.target_value,
                completion_percentage=0.0
            )
            
            # Store progress
            if user_id not in self.user_progress:
                self.user_progress[user_id] = []
            self.user_progress[user_id].append(progress)
            
            # Update participant count
            challenge.participant_count += 1
            
            logger.info(f"User {user_id} joined challenge {challenge_id}")
            return progress
            
        except Exception as e:
            logger.error(f"Failed to join challenge: {e}")
            raise WorkflowError(f"Failed to join challenge: {e}")
    
    async def update_challenge_progress(
        self,
        user_id: str,
        metric_updates: Dict[str, float]
    ) -> List[ChallengeProgress]:
        """
        Update user's progress on challenges based on actions
        
        Args:
            user_id: User identifier
            metric_updates: Dictionary of metric_name -> value_change
            
        Returns:
            List of updated ChallengeProgress objects
        """
        try:
            updated_progresses = []
            
            if user_id not in self.user_progress:
                return updated_progresses
            
            for progress in self.user_progress[user_id]:
                if progress.is_completed:
                    continue  # Skip completed challenges
                
                challenge = self.active_challenges.get(progress.challenge_id)
                if not challenge or not challenge.is_active:
                    continue
                
                # Check if this update affects this challenge
                if challenge.target_metric in metric_updates:
                    progress.current_progress += metric_updates[challenge.target_metric]
                    progress.completion_percentage = min(
                        (progress.current_progress / progress.target_progress) * 100, 100
                    )
                    progress.last_updated = datetime.utcnow()
                    
                    # Check for completion
                    if progress.current_progress >= progress.target_progress and not progress.is_completed:
                        progress.is_completed = True
                        progress.completed_at = datetime.utcnow()
                        await self._reward_user(user_id, challenge)
                        logger.info(f"User {user_id} completed challenge {challenge.challenge_id}")
                    
                    updated_progresses.append(progress)
            
            return updated_progresses
            
        except Exception as e:
            logger.error(f"Failed to update challenge progress: {e}")
            raise WorkflowError(f"Failed to update challenge progress: {e}")
    
    async def get_user_challenges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all challenges for a user with progress"""
        
        user_progresses = self.user_progress.get(user_id, [])
        challenges_data = []
        
        for progress in user_progresses:
            challenge = self.active_challenges.get(progress.challenge_id)
            if challenge:
                challenge_data = {
                    "challenge": challenge,
                    "progress": progress,
                    "time_remaining": max(0, (challenge.end_date - datetime.utcnow()).total_seconds()),
                    "status": "completed" if progress.is_completed else "active" if challenge.is_active else "expired"
                }
                challenges_data.append(challenge_data)
        
        return challenges_data
    
    async def get_available_challenges(self, user_id: str = None) -> List[Challenge]:
        """Get all available challenges (optionally filtered for user)"""
        
        now = datetime.utcnow()
        available_challenges = []
        
        for challenge in self.active_challenges.values():
            if challenge.is_active and challenge.start_date <= now <= challenge.end_date:
                # Check if user has already joined (if user_id provided)
                if user_id:
                    user_progresses = self.user_progress.get(user_id, [])
                    already_joined = any(p.challenge_id == challenge.challenge_id for p in user_progresses)
                    if already_joined:
                        continue
                
                available_challenges.append(challenge)
        
        return available_challenges
    
    async def generate_personalized_challenges(self, user_id: str, user_stats: Dict[str, Any]) -> List[Challenge]:
        """Generate AI-powered personalized challenges for user"""
        
        personalized_challenges = []
        
        # Analyze user behavior patterns
        engagement_level = user_stats.get("engagement_level", "medium")
        preferred_content_types = user_stats.get("preferred_content_types", ["general"])
        skill_level = user_stats.get("skill_level", "intermediate")
        
        # Generate challenges based on patterns
        if engagement_level == "high":
            # Create more challenging goals
            challenge = await self.create_challenge(
                title="Content Creation Master",
                description="Create 20 high-quality posts this week",
                challenge_type=ChallengeType.WEEKLY,
                target_metric="posts_created",
                target_value=20,
                reward_points=500,
                difficulty="hard"
            )
            personalized_challenges.append(challenge)
        
        elif engagement_level == "low":
            # Create easier, motivational challenges
            challenge = await self.create_challenge(
                title="First Steps",
                description="Create 3 posts this week to get started",
                challenge_type=ChallengeType.WEEKLY,
                target_metric="posts_created",
                target_value=3,
                reward_points=100,
                difficulty="easy"
            )
            personalized_challenges.append(challenge)
        
        # Add social challenges
        social_challenge = await self.create_challenge(
            title="Community Engagement",
            description="Receive 50 likes from the community",
            challenge_type=ChallengeType.WEEKLY,
            target_metric="likes_received",
            target_value=50,
            reward_points=200,
            difficulty="medium"
        )
        personalized_challenges.append(social_challenge)
        
        return personalized_challenges
    
    async def get_challenge_leaderboard(self, challenge_id: str) -> List[Dict[str, Any]]:
        """Get leaderboard for a specific challenge"""
        
        if challenge_id not in self.active_challenges:
            return []
        
        # Collect all participants and their progress
        participants = []
        for user_id, progresses in self.user_progress.items():
            for progress in progresses:
                if progress.challenge_id == challenge_id:
                    participants.append({
                        "user_id": user_id,
                        "progress": progress.current_progress,
                        "completion_percentage": progress.completion_percentage,
                        "is_completed": progress.is_completed,
                        "completed_at": progress.completed_at
                    })
        
        # Sort by progress (completed first, then by progress amount)
        participants.sort(
            key=lambda x: (not x["is_completed"], -x["progress"])
        )
        
        # Add ranks
        for i, participant in enumerate(participants):
            participant["rank"] = i + 1
        
        return participants
    
    async def _get_reward_items(self, difficulty: str, challenge_type: ChallengeType) -> List[str]:
        """Get reward items based on difficulty and type"""
        
        base_rewards = {
            "easy": ["Bronze Badge", "10 Bonus Credits"],
            "medium": ["Silver Badge", "25 Bonus Credits", "Feature Highlight"],
            "hard": ["Gold Badge", "50 Bonus Credits", "Premium Feature Access", "Special Recognition"]
        }
        
        type_rewards = {
            ChallengeType.DAILY: ["Daily Streak Bonus"],
            ChallengeType.WEEKLY: ["Weekly Champion Badge"],
            ChallengeType.MONTHLY: ["Monthly Master Title"],
            ChallengeType.SEASONAL: ["Seasonal Trophy", "Exclusive Theme"],
            ChallengeType.COMMUNITY: ["Community Star Badge", "Social Boost"],
            ChallengeType.PERSONAL: ["Personal Achievement Badge"]
        }
        
        rewards = base_rewards.get(difficulty, base_rewards["medium"])
        rewards.extend(type_rewards.get(challenge_type, []))
        
        return rewards
    
    async def _reward_user(self, user_id: str, challenge: Challenge):
        """Award rewards to user for completing challenge"""
        
        # In real implementation, this would:
        # 1. Add points to user's account
        # 2. Grant badge/items to user inventory
        # 3. Send notification
        # 4. Update user statistics
        
        logger.info(f"Rewarding user {user_id} for completing challenge {challenge.challenge_id}")
        logger.info(f"Points awarded: {challenge.reward_points}")
        logger.info(f"Items awarded: {challenge.reward_items}")
        
        # Record metrics
        await self.metrics_collector.record_metric("challenges_completed", 1)
        await self.metrics_collector.record_metric("challenge_points_awarded", challenge.reward_points)
    
    async def expire_challenges(self):
        """Mark expired challenges as inactive"""
        
        now = datetime.utcnow()
        expired_count = 0
        
        for challenge in self.active_challenges.values():
            if challenge.is_active and now > challenge.end_date:
                challenge.is_active = False
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Expired {expired_count} challenges")
            await self.metrics_collector.record_metric("challenges_expired", expired_count)
    
    async def get_challenge_analytics(self, challenge_id: str) -> Dict[str, Any]:
        """Get analytics for a specific challenge"""
        
        if challenge_id not in self.active_challenges:
            return {"error": "Challenge not found"}
        
        challenge = self.active_challenges[challenge_id]
        
        # Collect participant data
        participants = []
        for user_progresses in self.user_progress.values():
            for progress in user_progresses:
                if progress.challenge_id == challenge_id:
                    participants.append(progress)
        
        if not participants:
            return {"participants": 0, "completion_rate": 0}
        
        completed_count = sum(1 for p in participants if p.is_completed)
        completion_rate = completed_count / len(participants)
        
        avg_progress = sum(p.completion_percentage for p in participants) / len(participants)
        
        analytics = {
            "challenge_info": {
                "title": challenge.title,
                "type": challenge.challenge_type.value,
                "difficulty": challenge.difficulty,
                "target_value": challenge.target_value
            },
            "participation": {
                "total_participants": len(participants),
                "completed_participants": completed_count,
                "completion_rate": round(completion_rate * 100, 2),
                "average_progress": round(avg_progress, 2)
            },
            "engagement": {
                "days_active": (datetime.utcnow() - challenge.start_date).days,
                "daily_participation": len(participants) / max(1, (datetime.utcnow() - challenge.start_date).days)
            }
        }
        
        return analytics