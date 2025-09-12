"""Streak Tracking Workflow

AI-powered streak tracking and maintenance workflow for gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class StreakType(Enum):
    """Types of streaks"""
    LOGIN_STREAK = "login_streak"
    CONTENT_CREATION_STREAK = "content_creation_streak"  
    ENGAGEMENT_STREAK = "engagement_streak"
    LEARNING_STREAK = "learning_streak"
    SOCIAL_STREAK = "social_streak"
    CUSTOM_STREAK = "custom_streak"


@dataclass
class Streak:
    """Streak tracking data"""
    streak_id: str
    user_id: str
    streak_type: StreakType
    current_count: int = 0
    longest_count: int = 0
    last_activity_date: Optional[date] = None
    is_active: bool = True
    streak_start_date: Optional[date] = None
    freeze_count: int = 0  # Streak freezes available
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StreakActivity:
    """Streak activity record"""
    activity_id: str
    streak_id: str
    user_id: str
    activity_date: date
    activity_type: str
    activity_data: Dict[str, Any] = field(default_factory=dict)


class StreakTrackingWorkflow:
    """AI-powered streak tracking workflow"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.user_streaks: Dict[str, List[Streak]] = {}
        self.streak_activities: Dict[str, List[StreakActivity]] = {}
        
    async def track_activity(
        self,
        user_id: str,
        activity_type: str,
        streak_types: List[StreakType],
        activity_data: Dict[str, Any] = None
    ) -> List[Streak]:
        """
        Track user activity for streak maintenance
        
        Args:
            user_id: User identifier
            activity_type: Type of activity performed
            streak_types: Types of streaks this activity affects
            activity_data: Additional activity data
            
        Returns:
            List of updated streaks
        """
        try:
            today = date.today()
            updated_streaks = []
            
            for streak_type in streak_types:
                # Get or create streak
                streak = await self._get_or_create_streak(user_id, streak_type)
                
                # Check if activity already recorded today
                if streak.last_activity_date == today:
                    continue  # Already tracked today
                
                # Update streak based on activity
                updated_streak = await self._update_streak(streak, today, activity_type, activity_data)
                updated_streaks.append(updated_streak)
                
                # Record activity
                await self._record_streak_activity(streak, activity_type, today, activity_data)
            
            # Record metrics
            await self.metrics_collector.record_metric("streak_activities_tracked", len(updated_streaks))
            
            return updated_streaks
            
        except Exception as e:
            logger.error(f"Streak tracking failed: {e}")
            raise WorkflowError(f"Streak tracking failed: {e}")
    
    async def check_streak_status(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Check current status of all user streaks
        
        Args:
            user_id: User identifier
            
        Returns:
            List of streak status information
        """
        try:
            user_streaks = self.user_streaks.get(user_id, [])
            streak_statuses = []
            
            today = date.today()
            
            for streak in user_streaks:
                status = await self._calculate_streak_status(streak, today)
                streak_statuses.append(status)
            
            return streak_statuses
            
        except Exception as e:
            logger.error(f"Streak status check failed: {e}")
            return []
    
    async def use_streak_freeze(self, user_id: str, streak_type: StreakType) -> bool:
        """
        Use a streak freeze to maintain streak
        
        Args:
            user_id: User identifier
            streak_type: Type of streak to freeze
            
        Returns:
            True if freeze was successful
        """
        try:
            streak = await self._find_user_streak(user_id, streak_type)
            if not streak:
                return False
            
            if streak.freeze_count <= 0:
                return False  # No freezes available
            
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # Check if freeze is needed (missed yesterday)
            if streak.last_activity_date and streak.last_activity_date < yesterday:
                streak.freeze_count -= 1
                streak.last_activity_date = yesterday  # Extend streak
                logger.info(f"Streak freeze used for user {user_id}, streak {streak_type.value}")
                return True
            
            return False  # Freeze not needed
            
        except Exception as e:
            logger.error(f"Streak freeze failed: {e}")
            return False
    
    async def get_streak_leaderboard(self, streak_type: StreakType, limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard for specific streak type"""
        
        all_streaks = []
        
        # Collect all streaks of specified type
        for user_streaks in self.user_streaks.values():
            for streak in user_streaks:
                if streak.streak_type == streak_type and streak.is_active:
                    all_streaks.append(streak)
        
        # Sort by current count (descending)
        all_streaks.sort(key=lambda x: x.current_count, reverse=True)
        
        # Create leaderboard
        leaderboard = []
        for i, streak in enumerate(all_streaks[:limit]):
            leaderboard.append({
                "rank": i + 1,
                "user_id": streak.user_id,
                "current_streak": streak.current_count,
                "longest_streak": streak.longest_count,
                "streak_start_date": streak.streak_start_date,
                "last_activity": streak.last_activity_date
            })
        
        return leaderboard
    
    async def get_streak_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user's streak patterns"""
        
        user_streaks = self.user_streaks.get(user_id, [])
        
        if not user_streaks:
            return {"message": "No streak data available"}
        
        # Calculate insights
        total_streaks = len(user_streaks)
        active_streaks = len([s for s in user_streaks if s.is_active and s.current_count > 0])
        longest_overall = max([s.longest_count for s in user_streaks], default=0)
        current_total = sum([s.current_count for s in user_streaks if s.is_active])
        
        # Find best performing streak type
        best_streak = max(user_streaks, key=lambda x: x.longest_count, default=None)
        
        # Calculate consistency score
        consistency_score = await self._calculate_consistency_score(user_id)
        
        insights = {
            "total_streak_types": total_streaks,
            "active_streaks": active_streaks,
            "longest_streak_ever": longest_overall,
            "current_total_days": current_total,
            "best_streak_type": best_streak.streak_type.value if best_streak else None,
            "best_streak_count": best_streak.longest_count if best_streak else 0,
            "consistency_score": consistency_score,
            "freeze_count_total": sum([s.freeze_count for s in user_streaks]),
            "recommendations": await self._generate_streak_recommendations(user_streaks)
        }
        
        return insights
    
    async def _get_or_create_streak(self, user_id: str, streak_type: StreakType) -> Streak:
        """Get existing streak or create new one"""
        
        # Check if streak already exists
        existing_streak = await self._find_user_streak(user_id, streak_type)
        if existing_streak:
            return existing_streak
        
        # Create new streak
        streak_id = f"streak_{int(datetime.utcnow().timestamp())}_{user_id}"
        new_streak = Streak(
            streak_id=streak_id,
            user_id=user_id,
            streak_type=streak_type,
            freeze_count=3  # Start with 3 streak freezes
        )
        
        # Store streak
        if user_id not in self.user_streaks:
            self.user_streaks[user_id] = []
        self.user_streaks[user_id].append(new_streak)
        
        return new_streak
    
    async def _find_user_streak(self, user_id: str, streak_type: StreakType) -> Optional[Streak]:
        """Find specific streak for user"""
        
        user_streaks = self.user_streaks.get(user_id, [])
        for streak in user_streaks:
            if streak.streak_type == streak_type:
                return streak
        
        return None
    
    async def _update_streak(
        self, 
        streak: Streak, 
        activity_date: date, 
        activity_type: str, 
        activity_data: Dict[str, Any]
    ) -> Streak:
        """Update streak based on activity"""
        
        if not streak.last_activity_date:
            # First activity
            streak.current_count = 1
            streak.longest_count = 1
            streak.streak_start_date = activity_date
        else:
            days_since_last = (activity_date - streak.last_activity_date).days
            
            if days_since_last == 1:
                # Consecutive day - extend streak
                streak.current_count += 1
                if streak.current_count > streak.longest_count:
                    streak.longest_count = streak.current_count
            elif days_since_last == 0:
                # Same day - no change to count
                pass
            else:
                # Streak broken - reset
                streak.current_count = 1
                streak.streak_start_date = activity_date
                streak.is_active = True  # Reactivate if needed
        
        streak.last_activity_date = activity_date
        
        return streak
    
    async def _record_streak_activity(
        self, 
        streak: Streak, 
        activity_type: str, 
        activity_date: date, 
        activity_data: Dict[str, Any]
    ):
        """Record streak activity for history"""
        
        activity_id = f"activity_{int(datetime.utcnow().timestamp())}_{streak.user_id}"
        
        activity = StreakActivity(
            activity_id=activity_id,
            streak_id=streak.streak_id,
            user_id=streak.user_id,
            activity_date=activity_date,
            activity_type=activity_type,
            activity_data=activity_data or {}
        )
        
        # Store activity
        if streak.streak_id not in self.streak_activities:
            self.streak_activities[streak.streak_id] = []
        self.streak_activities[streak.streak_id].append(activity)
    
    async def _calculate_streak_status(self, streak: Streak, current_date: date) -> Dict[str, Any]:
        """Calculate current status of a streak"""
        
        status = {
            "streak_type": streak.streak_type.value,
            "current_count": streak.current_count,
            "longest_count": streak.longest_count,
            "is_active": streak.is_active,
            "freeze_count": streak.freeze_count,
            "last_activity_date": streak.last_activity_date,
            "streak_start_date": streak.streak_start_date
        }
        
        if streak.last_activity_date:
            days_since_last = (current_date - streak.last_activity_date).days
            
            if days_since_last == 0:
                status["status"] = "completed_today"
            elif days_since_last == 1:
                status["status"] = "at_risk"  # Need to act today
            else:
                status["status"] = "broken" if streak.freeze_count == 0 else "can_freeze"
        else:
            status["status"] = "new"
        
        return status
    
    async def _calculate_consistency_score(self, user_id: str) -> float:
        """Calculate user's overall streak consistency score"""
        
        user_streaks = self.user_streaks.get(user_id, [])
        
        if not user_streaks:
            return 0.0
        
        # Calculate average streak performance
        total_score = 0
        for streak in user_streaks:
            if streak.longest_count > 0:
                current_ratio = streak.current_count / streak.longest_count
                total_score += current_ratio
        
        consistency_score = total_score / len(user_streaks) if user_streaks else 0
        
        return round(consistency_score, 3)
    
    async def _generate_streak_recommendations(self, user_streaks: List[Streak]) -> List[str]:
        """Generate personalized streak recommendations"""
        
        recommendations = []
        today = date.today()
        
        # Check for at-risk streaks
        at_risk_streaks = []
        for streak in user_streaks:
            if streak.last_activity_date:
                days_since = (today - streak.last_activity_date).days
                if days_since == 1 and streak.current_count > 0:
                    at_risk_streaks.append(streak)
        
        if at_risk_streaks:
            recommendations.append(f"🚨 {len(at_risk_streaks)} streak(s) at risk! Complete activities today to maintain.")
        
        # Check for potential new streaks
        active_types = {s.streak_type for s in user_streaks if s.is_active}
        all_types = set(StreakType)
        missing_types = all_types - active_types
        
        if missing_types:
            recommendations.append(f"💡 Start new streaks: {', '.join([t.value.replace('_', ' ') for t in list(missing_types)[:2]])}")
        
        # Encourage consistency
        if user_streaks:
            avg_current = sum(s.current_count for s in user_streaks) / len(user_streaks)
            if avg_current < 7:
                recommendations.append("🎯 Focus on building 7-day streaks for better momentum!")
        
        return recommendations[:3]  # Limit to 3 recommendations