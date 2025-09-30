"""
Challenge Completion Analyzer - Gamification Module
==================================================

Advanced challenge completion analysis system for tracking user progress,
completion rates, and optimizing challenge design for maximum engagement.

Features:
- Real-time challenge progress tracking
- Completion rate analysis and optimization
- Challenge difficulty adjustment
- Reward optimization based on completion data
- User engagement pattern analysis
- Challenge design recommendations

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class ChallengeType(Enum):
    """Types of challenges in the gamification system"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MILESTONE = "milestone"
    COMMUNITY = "community"
    COLLABORATION = "collaboration"
    SKILL_BUILDING = "skill_building"
    ENGAGEMENT = "engagement"

class ChallengeStatus(Enum):
    """Challenge completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    EXPIRED = "expired"

class DifficultyLevel(Enum):
    """Challenge difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

@dataclass
class Challenge:
    """Challenge definition and configuration"""
    challenge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    challenge_type: ChallengeType = ChallengeType.DAILY
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    
    # Requirements and goals
    requirements: List[str] = field(default_factory=list)
    target_metric: str = ""  # views, likes, shares, etc.
    target_value: int = 0
    completion_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Rewards and incentives
    points_reward: int = 0
    badge_reward: Optional[str] = None
    monetary_reward: float = 0.0
    special_privileges: List[str] = field(default_factory=list)
    
    # Time constraints
    duration_hours: int = 24
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Challenge analytics
    participants_count: int = 0
    completion_rate: float = 0.0
    average_completion_time: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    is_active: bool = True

@dataclass
class ChallengeProgress:
    """User progress on a specific challenge"""
    progress_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    challenge_id: str = ""
    status: ChallengeStatus = ChallengeStatus.NOT_STARTED
    
    # Progress tracking
    current_value: float = 0.0
    target_value: float = 0.0
    progress_percentage: float = 0.0
    steps_completed: List[str] = field(default_factory=list)
    milestones_reached: List[str] = field(default_factory=list)
    
    # Time tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_minutes: float = 0.0
    
    # Engagement metrics
    attempts_count: int = 0
    hints_used: int = 0
    help_requests: int = 0
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class CompletionAnalytics:
    """Analytics for challenge completion patterns"""
    challenge_id: str = ""
    analysis_period_start: datetime = field(default_factory=datetime.now)
    analysis_period_end: datetime = field(default_factory=datetime.now)
    
    # Completion statistics
    total_participants: int = 0
    completed_count: int = 0
    failed_count: int = 0
    abandoned_count: int = 0
    completion_rate: float = 0.0
    
    # Time analysis
    average_completion_time: float = 0.0
    median_completion_time: float = 0.0
    fastest_completion_time: float = 0.0
    slowest_completion_time: float = 0.0
    
    # Difficulty analysis
    perceived_difficulty: float = 0.0  # User feedback score
    actual_difficulty: float = 0.0     # Based on completion data
    difficulty_rating: DifficultyLevel = DifficultyLevel.BEGINNER
    
    # Engagement patterns
    peak_activity_hours: List[int] = field(default_factory=list)
    drop_off_points: List[str] = field(default_factory=list)
    common_failure_reasons: List[str] = field(default_factory=list)
    
    # Optimization insights
    optimization_recommendations: List[str] = field(default_factory=list)
    suggested_difficulty_adjustment: Optional[DifficultyLevel] = None
    suggested_reward_adjustment: float = 0.0

class ChallengeCompletionAnalyzer:
    """Main challenge completion analysis system"""
    
    def __init__(self):
        self.challenges: Dict[str, Challenge] = {}
        self.user_progress: Dict[str, List[ChallengeProgress]] = defaultdict(list)
        self.completion_analytics: List[CompletionAnalytics] = []
        
        # Configuration
        self.analysis_enabled = True
        self.auto_optimization = True
        self.difficulty_adjustment_threshold = 0.3  # 30% deviation from target
        
        # Initialize with sample challenges
        self._initialize_sample_challenges()
        
    def _initialize_sample_challenges(self):
        """Initialize with sample challenges for the platform"""
        sample_challenges = [
            {
                "title": "Content Creator Kickstart",
                "description": "Upload your first piece of content and get 10 engagements",
                "type": ChallengeType.MILESTONE,
                "difficulty": DifficultyLevel.BEGINNER,
                "target_metric": "engagements",
                "target_value": 10,
                "points_reward": 100,
                "duration_hours": 168  # 1 week
            },
            {
                "title": "Daily Upload Challenge",
                "description": "Upload content every day for 7 consecutive days",
                "type": ChallengeType.DAILY,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "target_metric": "consecutive_uploads",
                "target_value": 7,
                "points_reward": 500,
                "badge_reward": "Consistency Champion",
                "duration_hours": 168
            },
            {
                "title": "Viral Content Challenge",
                "description": "Create content that reaches 1000 views in 24 hours",
                "type": ChallengeType.ENGAGEMENT,
                "difficulty": DifficultyLevel.ADVANCED,
                "target_metric": "views_24h",
                "target_value": 1000,
                "points_reward": 1000,
                "monetary_reward": 10.0,
                "duration_hours": 24
            },
            {
                "title": "Collaboration Master",
                "description": "Complete 3 successful collaborations this month",
                "type": ChallengeType.COLLABORATION,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "target_metric": "collaborations",
                "target_value": 3,
                "points_reward": 750,
                "duration_hours": 720  # 1 month
            },
            {
                "title": "Community Helper",
                "description": "Help 5 other creators by commenting and sharing their content",
                "type": ChallengeType.COMMUNITY,
                "difficulty": DifficultyLevel.BEGINNER,
                "target_metric": "community_actions",
                "target_value": 5,
                "points_reward": 200,
                "duration_hours": 72  # 3 days
            }
        ]
        
        for challenge_data in sample_challenges:
            challenge = Challenge(
                title=challenge_data["title"],
                description=challenge_data["description"],
                challenge_type=challenge_data["type"],
                difficulty=challenge_data["difficulty"],
                target_metric=challenge_data["target_metric"],
                target_value=challenge_data["target_value"],
                points_reward=challenge_data["points_reward"],
                badge_reward=challenge_data.get("badge_reward"),
                monetary_reward=challenge_data.get("monetary_reward", 0.0),
                duration_hours=challenge_data["duration_hours"]
            )
            
            challenge.end_time = challenge.start_time + timedelta(hours=challenge.duration_hours)
            self.challenges[challenge.challenge_id] = challenge
            
    async def track_user_progress(self, 
                                user_id: str, 
                                challenge_id: str, 
                                progress_data: Dict[str, Any]) -> ChallengeProgress:
        """Track and update user progress on a challenge"""
        
        challenge = self.challenges.get(challenge_id)
        if not challenge:
            raise ValueError(f"Challenge {challenge_id} not found")
            
        # Find existing progress or create new
        user_progress_list = self.user_progress[user_id]
        progress = next(
            (p for p in user_progress_list if p.challenge_id == challenge_id), 
            None
        )
        
        if not progress:
            progress = ChallengeProgress(
                user_id=user_id,
                challenge_id=challenge_id,
                target_value=float(challenge.target_value),
                started_at=datetime.now()
            )
            progress.status = ChallengeStatus.IN_PROGRESS
            user_progress_list.append(progress)
            
        # Update progress
        progress.current_value = progress_data.get("current_value", progress.current_value)
        progress.progress_percentage = (progress.current_value / progress.target_value) * 100
        progress.attempts_count += 1
        progress.last_updated = datetime.now()
        
        # Calculate time spent
        if progress.started_at:
            progress.time_spent_minutes = (datetime.now() - progress.started_at).total_seconds() / 60
            
        # Check for completion
        if progress.current_value >= progress.target_value:
            progress.status = ChallengeStatus.COMPLETED
            progress.completed_at = datetime.now()
            progress.progress_percentage = 100.0
            
            # Award rewards
            await self._award_challenge_rewards(user_id, challenge, progress)
            
        # Check for expiration
        elif challenge.end_time and datetime.now() > challenge.end_time:
            if progress.status == ChallengeStatus.IN_PROGRESS:
                progress.status = ChallengeStatus.EXPIRED
                
        # Update challenge statistics
        await self._update_challenge_statistics(challenge_id)
        
        logger.info(f"Updated progress for user {user_id} on challenge {challenge_id}: {progress.progress_percentage:.1f}%")
        return progress
        
    async def _award_challenge_rewards(self, 
                                     user_id: str, 
                                     challenge: Challenge, 
                                     progress: ChallengeProgress):
        """Award rewards for challenge completion"""
        
        rewards_awarded = []
        
        # Points reward
        if challenge.points_reward > 0:
            # In a real implementation, this would update user's points
            rewards_awarded.append(f"{challenge.points_reward} points")
            
        # Badge reward
        if challenge.badge_reward:
            # In a real implementation, this would award the badge
            rewards_awarded.append(f"Badge: {challenge.badge_reward}")
            
        # Monetary reward
        if challenge.monetary_reward > 0:
            # In a real implementation, this would add to user's earnings
            rewards_awarded.append(f"${challenge.monetary_reward:.2f}")
            
        # Special privileges
        for privilege in challenge.special_privileges:
            rewards_awarded.append(f"Privilege: {privilege}")
            
        logger.info(f"Awarded rewards to user {user_id}: {', '.join(rewards_awarded)}")
        
    async def _update_challenge_statistics(self, challenge_id: str):
        """Update challenge-level statistics"""
        
        challenge = self.challenges.get(challenge_id)
        if not challenge:
            return
            
        # Get all progress records for this challenge
        all_progress = []
        for user_progress_list in self.user_progress.values():
            for progress in user_progress_list:
                if progress.challenge_id == challenge_id:
                    all_progress.append(progress)
                    
        if not all_progress:
            return
            
        # Update statistics
        challenge.participants_count = len(all_progress)
        completed_count = len([p for p in all_progress if p.status == ChallengeStatus.COMPLETED])
        challenge.completion_rate = (completed_count / len(all_progress)) * 100
        
        # Calculate average completion time for completed challenges
        completed_times = [
            p.time_spent_minutes for p in all_progress 
            if p.status == ChallengeStatus.COMPLETED and p.time_spent_minutes > 0
        ]
        
        if completed_times:
            challenge.average_completion_time = statistics.mean(completed_times)
            
    async def analyze_challenge_completion(self, 
                                         challenge_id: str, 
                                         analysis_period_days: int = 30) -> CompletionAnalytics:
        """Perform comprehensive completion analysis for a challenge"""
        
        challenge = self.challenges.get(challenge_id)
        if not challenge:
            raise ValueError(f"Challenge {challenge_id} not found")
            
        # Define analysis period
        end_time = datetime.now()
        start_time = end_time - timedelta(days=analysis_period_days)
        
        # Get relevant progress records
        relevant_progress = []
        for user_progress_list in self.user_progress.values():
            for progress in user_progress_list:
                if (progress.challenge_id == challenge_id and 
                    progress.started_at and 
                    start_time <= progress.started_at <= end_time):
                    relevant_progress.append(progress)
                    
        if not relevant_progress:
            return CompletionAnalytics(
                challenge_id=challenge_id,
                analysis_period_start=start_time,
                analysis_period_end=end_time
            )
            
        # Calculate completion statistics
        total_participants = len(relevant_progress)
        completed = [p for p in relevant_progress if p.status == ChallengeStatus.COMPLETED]
        failed = [p for p in relevant_progress if p.status == ChallengeStatus.FAILED]
        abandoned = [p for p in relevant_progress if p.status == ChallengeStatus.ABANDONED]
        
        completion_rate = (len(completed) / total_participants) * 100
        
        # Time analysis
        completion_times = [p.time_spent_minutes for p in completed if p.time_spent_minutes > 0]
        
        avg_completion_time = statistics.mean(completion_times) if completion_times else 0
        median_completion_time = statistics.median(completion_times) if completion_times else 0
        fastest_time = min(completion_times) if completion_times else 0
        slowest_time = max(completion_times) if completion_times else 0
        
        # Difficulty analysis
        actual_difficulty = await self._calculate_actual_difficulty(completion_rate, avg_completion_time)
        perceived_difficulty = await self._estimate_perceived_difficulty(relevant_progress)
        
        # Activity pattern analysis
        peak_hours = await self._analyze_peak_activity_hours(relevant_progress)
        drop_off_points = await self._identify_drop_off_points(relevant_progress)
        failure_reasons = await self._analyze_failure_reasons(failed + abandoned)
        
        # Generate optimization recommendations
        optimization_recommendations = await self._generate_optimization_recommendations(
            challenge, completion_rate, actual_difficulty, drop_off_points
        )
        
        # Difficulty adjustment suggestions
        suggested_difficulty = await self._suggest_difficulty_adjustment(
            challenge.difficulty, actual_difficulty, completion_rate
        )
        
        # Reward adjustment suggestions
        reward_adjustment = await self._suggest_reward_adjustment(
            challenge, completion_rate, avg_completion_time
        )
        
        analytics = CompletionAnalytics(
            challenge_id=challenge_id,
            analysis_period_start=start_time,
            analysis_period_end=end_time,
            total_participants=total_participants,
            completed_count=len(completed),
            failed_count=len(failed),
            abandoned_count=len(abandoned),
            completion_rate=completion_rate,
            average_completion_time=avg_completion_time,
            median_completion_time=median_completion_time,
            fastest_completion_time=fastest_time,
            slowest_completion_time=slowest_time,
            perceived_difficulty=perceived_difficulty,
            actual_difficulty=actual_difficulty,
            peak_activity_hours=peak_hours,
            drop_off_points=drop_off_points,
            common_failure_reasons=failure_reasons,
            optimization_recommendations=optimization_recommendations,
            suggested_difficulty_adjustment=suggested_difficulty,
            suggested_reward_adjustment=reward_adjustment
        )
        
        self.completion_analytics.append(analytics)
        logger.info(f"Completed analysis for challenge {challenge_id}: {completion_rate:.1f}% completion rate")
        
        return analytics
        
    async def _calculate_actual_difficulty(self, completion_rate: float, avg_completion_time: float) -> float:
        """Calculate actual difficulty based on completion data"""
        
        # Difficulty scoring based on completion rate and time
        # Lower completion rate = higher difficulty
        # Longer completion time = higher difficulty
        
        completion_difficulty = 1.0 - (completion_rate / 100)
        
        # Time-based difficulty (normalized to expected completion time)
        expected_time_by_difficulty = {
            DifficultyLevel.BEGINNER: 30,      # 30 minutes
            DifficultyLevel.INTERMEDIATE: 60,  # 1 hour
            DifficultyLevel.ADVANCED: 120,     # 2 hours
            DifficultyLevel.EXPERT: 240,       # 4 hours
            DifficultyLevel.MASTER: 480        # 8 hours
        }
        
        # Use intermediate as baseline
        expected_time = expected_time_by_difficulty[DifficultyLevel.INTERMEDIATE]
        time_difficulty = min(1.0, avg_completion_time / expected_time) if avg_completion_time > 0 else 0.5
        
        # Combined difficulty score (0-1 scale)
        actual_difficulty = (completion_difficulty * 0.7 + time_difficulty * 0.3)
        
        return actual_difficulty
        
    async def _estimate_perceived_difficulty(self, progress_records: List[ChallengeProgress]) -> float:
        """Estimate perceived difficulty from user behavior"""
        
        if not progress_records:
            return 0.5
            
        # Indicators of perceived difficulty
        total_attempts = sum(p.attempts_count for p in progress_records)
        total_help_requests = sum(p.help_requests for p in progress_records)
        total_hints_used = sum(p.hints_used for p in progress_records)
        
        participants = len(progress_records)
        
        # Calculate difficulty indicators
        avg_attempts = total_attempts / participants if participants > 0 else 1
        avg_help_requests = total_help_requests / participants if participants > 0 else 0
        avg_hints = total_hints_used / participants if participants > 0 else 0
        
        # Normalize to 0-1 scale
        attempts_score = min(1.0, (avg_attempts - 1) / 4)  # 1-5 attempts range
        help_score = min(1.0, avg_help_requests / 3)       # 0-3 help requests range
        hints_score = min(1.0, avg_hints / 5)              # 0-5 hints range
        
        perceived_difficulty = (attempts_score * 0.4 + help_score * 0.3 + hints_score * 0.3)
        
        return perceived_difficulty
        
    async def _analyze_peak_activity_hours(self, progress_records: List[ChallengeProgress]) -> List[int]:
        """Analyze peak activity hours for challenge participation"""
        
        hour_activity = defaultdict(int)
        
        for progress in progress_records:
            if progress.started_at:
                hour = progress.started_at.hour
                hour_activity[hour] += 1
                
        if not hour_activity:
            return []
            
        # Find hours with above-average activity
        avg_activity = statistics.mean(hour_activity.values())
        peak_hours = [hour for hour, activity in hour_activity.items() if activity > avg_activity * 1.2]
        
        return sorted(peak_hours)
        
    async def _identify_drop_off_points(self, progress_records: List[ChallengeProgress]) -> List[str]:
        """Identify common drop-off points in challenges"""
        
        drop_off_points = []
        
        # Analyze progress percentages where users commonly abandon
        abandoned_or_failed = [
            p for p in progress_records 
            if p.status in [ChallengeStatus.ABANDONED, ChallengeStatus.FAILED]
        ]
        
        if not abandoned_or_failed:
            return drop_off_points
            
        # Group by progress percentage ranges
        drop_off_ranges = defaultdict(int)
        for progress in abandoned_or_failed:
            progress_range = int(progress.progress_percentage // 10) * 10  # Group by 10% ranges
            drop_off_ranges[progress_range] += 1
            
        # Find ranges with high drop-off rates
        total_drop_offs = sum(drop_off_ranges.values())
        for progress_range, count in drop_off_ranges.items():
            if count / total_drop_offs > 0.2:  # More than 20% of drop-offs
                drop_off_points.append(f"{progress_range}-{progress_range + 10}% completion")
                
        return drop_off_points
        
    async def _analyze_failure_reasons(self, failed_progress: List[ChallengeProgress]) -> List[str]:
        """Analyze common failure reasons (simulated)"""
        
        # In a real implementation, this would analyze actual failure data
        # For now, return common simulated failure reasons
        
        if not failed_progress:
            return []
            
        failure_reasons = [
            "Time constraints",
            "Difficulty too high", 
            "Unclear instructions",
            "Technical issues",
            "Lack of motivation",
            "Competing priorities"
        ]
        
        # Simulate distribution based on challenge characteristics
        import random
        return random.sample(failure_reasons, min(3, len(failure_reasons)))
        
    async def _generate_optimization_recommendations(self, 
                                                   challenge: Challenge,
                                                   completion_rate: float,
                                                   actual_difficulty: float,
                                                   drop_off_points: List[str]) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        
        recommendations = []
        
        # Completion rate recommendations
        if completion_rate < 30:
            recommendations.append("Consider reducing challenge difficulty or extending time limit")
            recommendations.append("Review challenge instructions for clarity")
        elif completion_rate > 80:
            recommendations.append("Challenge may be too easy - consider increasing difficulty")
            recommendations.append("Add bonus objectives for additional engagement")
            
        # Difficulty recommendations
        if actual_difficulty > 0.8:
            recommendations.append("Challenge is perceived as very difficult - consider breaking into smaller steps")
        elif actual_difficulty < 0.3:
            recommendations.append("Challenge may be too simple - add complexity or additional requirements")
            
        # Drop-off point recommendations
        if drop_off_points:
            recommendations.append(f"High drop-off at {drop_off_points[0]} - add intermediate milestones")
            recommendations.append("Consider providing additional guidance at critical points")
            
        # Engagement recommendations
        if challenge.participants_count < 10:
            recommendations.append("Low participation - improve challenge visibility and marketing")
            recommendations.append("Consider adding social elements to increase appeal")
            
        # Reward optimization
        if completion_rate < 50 and challenge.points_reward < 500:
            recommendations.append("Consider increasing rewards to improve completion motivation")
            
        return recommendations
        
    async def _suggest_difficulty_adjustment(self, 
                                           current_difficulty: DifficultyLevel,
                                           actual_difficulty: float,
                                           completion_rate: float) -> Optional[DifficultyLevel]:
        """Suggest difficulty level adjustment"""
        
        difficulty_levels = list(DifficultyLevel)
        current_index = difficulty_levels.index(current_difficulty)
        
        # Adjust based on completion rate and actual difficulty
        if completion_rate < 30 or actual_difficulty > 0.8:
            # Too difficult - suggest easier level
            if current_index > 0:
                return difficulty_levels[current_index - 1]
        elif completion_rate > 80 and actual_difficulty < 0.3:
            # Too easy - suggest harder level
            if current_index < len(difficulty_levels) - 1:
                return difficulty_levels[current_index + 1]
                
        return None  # No adjustment needed
        
    async def _suggest_reward_adjustment(self, 
                                       challenge: Challenge,
                                       completion_rate: float,
                                       avg_completion_time: float) -> float:
        """Suggest reward adjustment multiplier"""
        
        # Base adjustment on completion rate and time investment
        base_adjustment = 1.0
        
        # If completion rate is low, suggest increasing rewards
        if completion_rate < 30:
            base_adjustment = 1.5
        elif completion_rate < 50:
            base_adjustment = 1.2
        elif completion_rate > 80:
            base_adjustment = 0.9
            
        # Adjust for time investment
        if avg_completion_time > 120:  # More than 2 hours
            base_adjustment *= 1.1
        elif avg_completion_time < 30:  # Less than 30 minutes
            base_adjustment *= 0.9
            
        return base_adjustment
        
    def get_challenge_performance_report(self, challenge_id: str = None) -> Dict[str, Any]:
        """Generate comprehensive challenge performance report"""
        
        if challenge_id:
            return self._get_single_challenge_report(challenge_id)
        else:
            return self._get_overall_performance_report()
            
    def _get_single_challenge_report(self, challenge_id: str) -> Dict[str, Any]:
        """Generate report for a specific challenge"""
        
        challenge = self.challenges.get(challenge_id)
        if not challenge:
            return {"error": f"Challenge {challenge_id} not found"}
            
        # Get all progress for this challenge
        all_progress = []
        for user_progress_list in self.user_progress.values():
            for progress in user_progress_list:
                if progress.challenge_id == challenge_id:
                    all_progress.append(progress)
                    
        # Calculate metrics
        total_participants = len(all_progress)
        completed = len([p for p in all_progress if p.status == ChallengeStatus.COMPLETED])
        in_progress = len([p for p in all_progress if p.status == ChallengeStatus.IN_PROGRESS])
        failed = len([p for p in all_progress if p.status in [ChallengeStatus.FAILED, ChallengeStatus.ABANDONED]])
        
        completion_rate = (completed / total_participants * 100) if total_participants > 0 else 0
        
        # Get latest analytics
        latest_analytics = next(
            (a for a in self.completion_analytics if a.challenge_id == challenge_id),
            None
        )
        
        return {
            "challenge": {
                "id": challenge_id,
                "title": challenge.title,
                "type": challenge.challenge_type.value,
                "difficulty": challenge.difficulty.value,
                "target_metric": challenge.target_metric,
                "target_value": challenge.target_value
            },
            "participation": {
                "total_participants": total_participants,
                "completed": completed,
                "in_progress": in_progress,
                "failed": failed,
                "completion_rate": completion_rate
            },
            "performance": {
                "average_completion_time": challenge.average_completion_time,
                "points_awarded": completed * challenge.points_reward,
                "monetary_rewards": completed * challenge.monetary_reward
            },
            "analytics": {
                "actual_difficulty": latest_analytics.actual_difficulty if latest_analytics else 0,
                "perceived_difficulty": latest_analytics.perceived_difficulty if latest_analytics else 0,
                "optimization_recommendations": latest_analytics.optimization_recommendations if latest_analytics else []
            }
        }
        
    def _get_overall_performance_report(self) -> Dict[str, Any]:
        """Generate overall challenge performance report"""
        
        # Calculate overall statistics
        total_challenges = len(self.challenges)
        active_challenges = len([c for c in self.challenges.values() if c.is_active])
        
        # Participation statistics
        total_participants = 0
        total_completions = 0
        
        for user_progress_list in self.user_progress.values():
            for progress in user_progress_list:
                total_participants += 1
                if progress.status == ChallengeStatus.COMPLETED:
                    total_completions += 1
                    
        overall_completion_rate = (total_completions / total_participants * 100) if total_participants > 0 else 0
        
        # Challenge type performance
        type_performance = defaultdict(lambda: {"participants": 0, "completions": 0})
        
        for challenge in self.challenges.values():
            challenge_type = challenge.challenge_type.value
            
            # Count participants and completions for this challenge
            challenge_progress = []
            for user_progress_list in self.user_progress.values():
                for progress in user_progress_list:
                    if progress.challenge_id == challenge.challenge_id:
                        challenge_progress.append(progress)
                        
            type_performance[challenge_type]["participants"] += len(challenge_progress)
            type_performance[challenge_type]["completions"] += len([
                p for p in challenge_progress if p.status == ChallengeStatus.COMPLETED
            ])
            
        # Calculate completion rates by type
        for type_data in type_performance.values():
            if type_data["participants"] > 0:
                type_data["completion_rate"] = (type_data["completions"] / type_data["participants"]) * 100
            else:
                type_data["completion_rate"] = 0
                
        # Top performing challenges
        challenge_performance = []
        for challenge in self.challenges.values():
            challenge_performance.append({
                "title": challenge.title,
                "type": challenge.challenge_type.value,
                "completion_rate": challenge.completion_rate,
                "participants": challenge.participants_count
            })
            
        top_challenges = sorted(challenge_performance, key=lambda x: x["completion_rate"], reverse=True)[:5]
        
        return {
            "overview": {
                "total_challenges": total_challenges,
                "active_challenges": active_challenges,
                "total_participants": total_participants,
                "total_completions": total_completions,
                "overall_completion_rate": overall_completion_rate
            },
            "challenge_type_performance": dict(type_performance),
            "top_performing_challenges": top_challenges,
            "insights": self._generate_performance_insights(overall_completion_rate, type_performance)
        }
        
    def _generate_performance_insights(self, 
                                     overall_completion_rate: float,
                                     type_performance: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate insights from performance data"""
        
        insights = []
        
        # Overall performance insights
        if overall_completion_rate < 40:
            insights.append("Overall completion rate is low - review challenge difficulty and rewards")
        elif overall_completion_rate > 70:
            insights.append("Strong challenge completion performance across the platform")
            
        # Type-specific insights
        best_type = max(type_performance.items(), key=lambda x: x[1]["completion_rate"])
        worst_type = min(type_performance.items(), key=lambda x: x[1]["completion_rate"])
        
        if best_type[1]["completion_rate"] > 60:
            insights.append(f"{best_type[0].title()} challenges perform best - consider creating more")
            
        if worst_type[1]["completion_rate"] < 30:
            insights.append(f"{worst_type[0].title()} challenges need optimization")
            
        # Participation insights
        total_participants = sum([data["participants"] for data in type_performance.values()])
        if total_participants < 100:
            insights.append("Low overall participation - improve challenge discovery and onboarding")
            
        return insights

# Export main classes
__all__ = [
    'ChallengeCompletionAnalyzer',
    'Challenge',
    'ChallengeProgress',
    'CompletionAnalytics',
    'ChallengeType',
    'ChallengeStatus',
    'DifficultyLevel'
]