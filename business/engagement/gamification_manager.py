"""
Enterprise Gamification Manager - Advanced gamification system for IA Influencer platform.

This module provides a comprehensive gamification management system that drives user 
engagement through challenges, achievements, rewards, and competitive elements.
Designed for multi-format content creators (musicians, bloggers, photographers, influencers, comedians).

Architecture: Enterprise Production-Ready (Backend Level 2)
Module: backend/business/engagement/gamification_manager.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
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
Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class GamificationEventType(str, Enum):
    """Types of gamification events that trigger rewards."""
    CONTENT_UPLOAD = "content_upload"
    FIRST_UPLOAD = "first_upload"
    DAILY_UPLOAD = "daily_upload"
    WEEKLY_STREAK = "weekly_streak"
    MONTHLY_STREAK = "monthly_streak"
    VIRAL_CONTENT = "viral_content"
    QUALITY_MILESTONE = "quality_milestone"
    COLLABORATION_SUCCESS = "collaboration_success"
    FIRST_COLLABORATION = "first_collaboration"
    MENTOR_ACHIEVEMENT = "mentor_achievement"
    REVENUE_MILESTONE = "revenue_milestone"
    FIRST_REVENUE = "first_revenue"
    PLATFORM_EXPANSION = "platform_expansion"
    GLOBAL_REACH = "global_reach"
    CHALLENGE_COMPLETION = "challenge_completion"
    LEADERBOARD_RANKING = "leaderboard_ranking"
    COMMUNITY_CONTRIBUTION = "community_contribution"
    INNOVATION_USAGE = "innovation_usage"
    SEO_OPTIMIZATION = "seo_optimization"
    ENGAGEMENT_MILESTONE = "engagement_milestone"


class GamificationMetricType(str, Enum):
    """Types of metrics tracked for gamification."""
    EXPERIENCE_POINTS = "experience_points"
    CONTENT_COUNT = "content_count"
    COLLABORATION_COUNT = "collaboration_count"
    REVENUE_TOTAL = "revenue_total"
    ENGAGEMENT_RATE = "engagement_rate"
    QUALITY_SCORE = "quality_score"
    STREAK_DAYS = "streak_days"
    PLATFORM_COUNT = "platform_count"
    GLOBAL_REACH_COUNTRIES = "global_reach_countries"
    COMMUNITY_IMPACT = "community_impact"
    INNOVATION_ADOPTION = "innovation_adoption"


class GamificationLevel(str, Enum):
    """User progression levels in the gamification system."""
    NEWCOMER = "newcomer"           # Level 1-5
    RISING_STAR = "rising_star"     # Level 6-15
    ESTABLISHED = "established"     # Level 16-30
    INFLUENCER = "influencer"       # Level 31-50
    MASTER = "master"               # Level 51-75
    LEGENDARY = "legendary"         # Level 76-100
    ICON = "icon"                   # Level 100+


@dataclass
class GamificationProfile:
    """Complete gamification profile for a user."""
    user_id: str
    level: int = 1
    experience_points: int = 0
    total_points_earned: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    achievements: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    challenge_completions: Dict[str, int] = field(default_factory=dict)
    leaderboard_positions: Dict[str, int] = field(default_factory=dict)
    virtual_currency: Decimal = field(default_factory=lambda: Decimal('0'))
    last_activity: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Detailed metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Customization and preferences
    profile_customizations: Dict[str, Any] = field(default_factory=dict)
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    
    def get_level_category(self) -> GamificationLevel:
        """Get the level category based on current level."""
        if self.level <= 5:
            return GamificationLevel.NEWCOMER
        elif self.level <= 15:
            return GamificationLevel.RISING_STAR
        elif self.level <= 30:
            return GamificationLevel.ESTABLISHED
        elif self.level <= 50:
            return GamificationLevel.INFLUENCER
        elif self.level <= 75:
            return GamificationLevel.MASTER
        elif self.level <= 100:
            return GamificationLevel.LEGENDARY
        else:
            return GamificationLevel.ICON
    
    def calculate_next_level_progress(self) -> Tuple[int, int, float]:
        """Calculate progress to next level.
        
        Returns:
            Tuple of (current_level_threshold, next_level_threshold, progress_percentage)
        """
        level_thresholds = {
            1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
            6: 1500, 7: 2500, 8: 4000, 9: 6000, 10: 10000,
            11: 15000, 12: 22000, 13: 31000, 14: 42000, 15: 55000,
            16: 70000, 17: 87000, 18: 106000, 19: 127000, 20: 150000,
            21: 175000, 22: 202000, 23: 231000, 24: 262000, 25: 295000,
            26: 330000, 27: 367000, 28: 406000, 29: 447000, 30: 490000
        }
        
        # For levels above 30, use exponential growth
        if self.level > 30:
            current_threshold = 490000 + (self.level - 30) * 50000
            next_threshold = 490000 + (self.level - 29) * 50000
        else:
            current_threshold = level_thresholds.get(self.level, 0)
            next_threshold = level_thresholds.get(self.level + 1, current_threshold + 50000)
        
        if next_threshold == current_threshold:
            return current_threshold, next_threshold, 100.0
        
        progress = ((self.experience_points - current_threshold) / 
                   (next_threshold - current_threshold)) * 100
        progress = max(0, min(100, progress))
        
        return current_threshold, next_threshold, progress


@dataclass
class GamificationEvent:
    """Represents a gamification event that occurred."""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    event_type: GamificationEventType = GamificationEventType.CONTENT_UPLOAD
    metadata: Dict[str, Any] = field(default_factory=dict)
    points_awarded: int = 0
    achievements_unlocked: List[str] = field(default_factory=list)
    badges_earned: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processed: bool = False


class GamificationManager:
    """
    Enterprise-grade gamification management system.
    
    Manages user progression, achievements, rewards, and engagement mechanics
    across the entire IA Influencer platform ecosystem.
    """
    
    def __init__(self):
        """Initialize the gamification manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._event_queue: List[GamificationEvent] = []
        self._processing_lock = asyncio.Lock()
        self._user_profiles: Dict[str, GamificationProfile] = {}
        
        # Initialize point values for different actions
        self._point_values = {
            GamificationEventType.CONTENT_UPLOAD: 50,
            GamificationEventType.FIRST_UPLOAD: 200,
            GamificationEventType.DAILY_UPLOAD: 25,
            GamificationEventType.WEEKLY_STREAK: 100,
            GamificationEventType.MONTHLY_STREAK: 500,
            GamificationEventType.VIRAL_CONTENT: 1000,
            GamificationEventType.QUALITY_MILESTONE: 300,
            GamificationEventType.COLLABORATION_SUCCESS: 150,
            GamificationEventType.FIRST_COLLABORATION: 300,
            GamificationEventType.MENTOR_ACHIEVEMENT: 400,
            GamificationEventType.REVENUE_MILESTONE: 500,
            GamificationEventType.FIRST_REVENUE: 1000,
            GamificationEventType.PLATFORM_EXPANSION: 200,
            GamificationEventType.GLOBAL_REACH: 800,
            GamificationEventType.CHALLENGE_COMPLETION: 250,
            GamificationEventType.LEADERBOARD_RANKING: 300,
            GamificationEventType.COMMUNITY_CONTRIBUTION: 100,
            GamificationEventType.INNOVATION_USAGE: 150,
            GamificationEventType.SEO_OPTIMIZATION: 75,
            GamificationEventType.ENGAGEMENT_MILESTONE: 200,
        }
        
        self.logger.info("GamificationManager initialized successfully")
    
    async def get_user_profile(self, user_id: str) -> GamificationProfile:
        """Get or create a gamification profile for a user."""
        if user_id not in self._user_profiles:
            profile = GamificationProfile(user_id=user_id)
            self._user_profiles[user_id] = profile
            self.logger.info(f"Created new gamification profile for user {user_id}")
        
        return self._user_profiles[user_id]
    
    async def record_event(
        self,
        user_id: str,
        event_type: GamificationEventType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GamificationEvent:
        """Record a gamification event for processing."""
        metadata = metadata or {}
        
        event = GamificationEvent(
            user_id=user_id,
            event_type=event_type,
            metadata=metadata
        )
        
        self._event_queue.append(event)
        self.logger.debug(f"Recorded event {event_type} for user {user_id}")
        
        # Process event immediately for real-time feedback
        await self._process_event(event)
        
        return event
    
    async def _process_event(self, event: GamificationEvent) -> None:
        """Process a single gamification event."""
        async with self._processing_lock:
            try:
                profile = await self.get_user_profile(event.user_id)
                
                # Calculate points for this event
                base_points = self._point_values.get(event.event_type, 0)
                multiplier = await self._calculate_point_multiplier(profile, event)
                points_awarded = int(base_points * multiplier)
                
                # Update profile
                profile.experience_points += points_awarded
                profile.total_points_earned += points_awarded
                profile.last_activity = datetime.utcnow()
                profile.updated_at = datetime.utcnow()
                
                # Update metrics
                await self._update_profile_metrics(profile, event)
                
                # Check for level progression
                new_level = await self._calculate_level(profile.experience_points)
                if new_level > profile.level:
                    old_level = profile.level
                    profile.level = new_level
                    self.logger.info(f"User {event.user_id} leveled up from {old_level} to {new_level}")
                    
                    # Award level-up bonuses
                    level_bonus = new_level * 50
                    profile.experience_points += level_bonus
                    profile.total_points_earned += level_bonus
                
                # Check for achievements and badges
                new_achievements = await self._check_achievements(profile, event)
                new_badges = await self._check_badges(profile, event)
                
                # Update streak tracking
                await self._update_streaks(profile, event)
                
                # Update event with results
                event.points_awarded = points_awarded
                event.achievements_unlocked = new_achievements
                event.badges_earned = new_badges
                event.processed = True
                
                self.logger.info(
                    f"Processed event {event.event_type} for user {event.user_id}: "
                    f"{points_awarded} points, {len(new_achievements)} achievements, "
                    f"{len(new_badges)} badges"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to process event {event.event_id}: {e}")
                raise
    
    async def _calculate_point_multiplier(
        self,
        profile: GamificationProfile,
        event: GamificationEvent
    ) -> float:
        """Calculate point multiplier based on user context and event metadata."""
        multiplier = 1.0
        
        # Streak bonus
        if profile.current_streak >= 7:
            multiplier += 0.2  # 20% bonus for 7+ day streak
        if profile.current_streak >= 30:
            multiplier += 0.3  # Additional 30% bonus for 30+ day streak
        
        # Quality bonus from metadata
        if 'quality_score' in event.metadata:
            quality_score = event.metadata['quality_score']
            if quality_score >= 95:
                multiplier += 0.5  # 50% bonus for exceptional quality
            elif quality_score >= 85:
                multiplier += 0.25  # 25% bonus for high quality
        
        # Collaboration bonus
        if 'collaboration_participants' in event.metadata:
            participant_count = event.metadata['collaboration_participants']
            if participant_count >= 5:
                multiplier += 0.3  # 30% bonus for large collaborations
            elif participant_count >= 3:
                multiplier += 0.15  # 15% bonus for medium collaborations
        
        # Platform diversity bonus
        if 'platform_count' in event.metadata:
            platform_count = event.metadata['platform_count']
            if platform_count >= 5:
                multiplier += 0.25  # 25% bonus for cross-platform presence
        
        # Global reach bonus
        if 'countries_reached' in event.metadata:
            countries = event.metadata['countries_reached']
            if countries >= 10:
                multiplier += 0.4  # 40% bonus for global reach
            elif countries >= 5:
                multiplier += 0.2  # 20% bonus for international reach
        
        return multiplier
    
    async def _calculate_level(self, experience_points: int) -> int:
        """Calculate user level based on experience points."""
        # Level progression follows exponential curve
        level_thresholds = {
            1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
            6: 1500, 7: 2500, 8: 4000, 9: 6000, 10: 10000,
            11: 15000, 12: 22000, 13: 31000, 14: 42000, 15: 55000,
            16: 70000, 17: 87000, 18: 106000, 19: 127000, 20: 150000,
            21: 175000, 22: 202000, 23: 231000, 24: 262000, 25: 295000,
            26: 330000, 27: 367000, 28: 406000, 29: 447000, 30: 490000
        }
        
        for level in range(100, 0, -1):
            if level <= 30:
                threshold = level_thresholds.get(level, 0)
            else:
                # For levels above 30, use exponential growth
                threshold = 490000 + (level - 30) * 50000
            
            if experience_points >= threshold:
                return level
        
        return 1
    
    async def _update_profile_metrics(
        self,
        profile: GamificationProfile,
        event: GamificationEvent
    ) -> None:
        """Update profile metrics based on the event."""
        if not profile.metrics:
            profile.metrics = {}
        
        # Update event-specific metrics
        if event.event_type == GamificationEventType.CONTENT_UPLOAD:
            profile.metrics['content_count'] = profile.metrics.get('content_count', 0) + 1
        
        elif event.event_type == GamificationEventType.COLLABORATION_SUCCESS:
            profile.metrics['collaboration_count'] = profile.metrics.get('collaboration_count', 0) + 1
        
        elif event.event_type == GamificationEventType.REVENUE_MILESTONE:
            if 'revenue_amount' in event.metadata:
                profile.metrics['revenue_total'] = profile.metrics.get('revenue_total', 0) + event.metadata['revenue_amount']
        
        # Update from metadata
        for metric_key, metric_value in event.metadata.items():
            if metric_key in ['quality_score', 'engagement_rate', 'platform_count', 'countries_reached']:
                # For these metrics, we store the latest value
                profile.metrics[metric_key] = metric_value
            elif metric_key == 'innovation_features_used':
                # Accumulate innovation usage
                current = profile.metrics.get('innovation_adoption', 0)
                profile.metrics['innovation_adoption'] = current + len(metric_value)
    
    async def _update_streaks(
        self,
        profile: GamificationProfile,
        event: GamificationEvent
    ) -> None:
        """Update user activity streaks."""
        now = datetime.utcnow()
        
        # Only certain events count towards streaks
        streak_events = {
            GamificationEventType.CONTENT_UPLOAD,
            GamificationEventType.DAILY_UPLOAD,
            GamificationEventType.COLLABORATION_SUCCESS,
            GamificationEventType.COMMUNITY_CONTRIBUTION
        }
        
        if event.event_type not in streak_events:
            return
        
        if profile.last_activity:
            # Check if this extends the current streak
            time_since_last = now - profile.last_activity
            
            if time_since_last.days == 1:
                # Consecutive day - extend streak
                profile.current_streak += 1
                profile.longest_streak = max(profile.longest_streak, profile.current_streak)
            elif time_since_last.days > 1:
                # Gap in activity - reset streak
                profile.current_streak = 1
            # Same day activity doesn't change streak count
        else:
            # First activity
            profile.current_streak = 1
            profile.longest_streak = 1
    
    async def _check_achievements(
        self,
        profile: GamificationProfile,
        event: GamificationEvent
    ) -> List[str]:
        """Check for new achievements based on the event and profile state."""
        new_achievements = []
        
        # Define achievement conditions
        achievement_conditions = {
            "first_upload": lambda: (
                event.event_type == GamificationEventType.FIRST_UPLOAD
            ),
            "viral_hit": lambda: (
                event.event_type == GamificationEventType.VIRAL_CONTENT
            ),
            "consistency_king": lambda: (
                profile.current_streak >= 30
            ),
            "quality_master": lambda: (
                event.metadata.get('quality_score', 0) >= 95
            ),
            "multi_format": lambda: (
                event.metadata.get('content_formats_used', 0) >= 5
            ),
            "team_player": lambda: (
                profile.metrics.get('collaboration_count', 0) >= 10
            ),
            "mentor": lambda: (
                event.metadata.get('creators_helped', 0) >= 5
            ),
            "connector": lambda: (
                event.metadata.get('successful_matches', 0) >= 50
            ),
            "global": lambda: (
                profile.metrics.get('countries_reached', 0) >= 5
            ),
            "cross_genre": lambda: (
                event.metadata.get('genres_collaborated', 0) >= 3
            ),
            "first_dollar": lambda: (
                event.event_type == GamificationEventType.FIRST_REVENUE
            ),
            "revenue_milestone_100": lambda: (
                profile.metrics.get('revenue_total', 0) >= 100
            ),
            "revenue_milestone_1k": lambda: (
                profile.metrics.get('revenue_total', 0) >= 1000
            ),
            "revenue_milestone_10k": lambda: (
                profile.metrics.get('revenue_total', 0) >= 10000
            ),
            "passive_income": lambda: (
                event.metadata.get('passive_income_days', 0) >= 30
            ),
            "diversified": lambda: (
                event.metadata.get('revenue_streams', 0) >= 5
            ),
            "optimization_pro": lambda: (
                event.metadata.get('roi_improvement', 0) >= 50
            )
        }
        
        # Check each achievement condition
        for achievement_id, condition in achievement_conditions.items():
            if achievement_id not in profile.achievements:
                try:
                    if condition():
                        profile.achievements.append(achievement_id)
                        new_achievements.append(achievement_id)
                        self.logger.info(f"User {profile.user_id} unlocked achievement: {achievement_id}")
                except Exception as e:
                    self.logger.warning(f"Error checking achievement {achievement_id}: {e}")
        
        return new_achievements
    
    async def _check_badges(
        self,
        profile: GamificationProfile,
        event: GamificationEvent
    ) -> List[str]:
        """Check for new badges based on the event and profile state."""
        new_badges = []
        
        # Define badge conditions
        badge_conditions = {
            "content_creator": lambda: profile.metrics.get('content_count', 0) >= 1,
            "prolific_creator": lambda: profile.metrics.get('content_count', 0) >= 100,
            "viral_sensation": lambda: event.event_type == GamificationEventType.VIRAL_CONTENT,
            "quality_pioneer": lambda: event.metadata.get('quality_score', 0) >= 98,
            "collaboration_champion": lambda: profile.metrics.get('collaboration_count', 0) >= 50,
            "revenue_generator": lambda: profile.metrics.get('revenue_total', 0) >= 1000,
            "global_influencer": lambda: profile.metrics.get('countries_reached', 0) >= 20,
            "innovation_adopter": lambda: profile.metrics.get('innovation_adoption', 0) >= 10,
            "community_leader": lambda: event.metadata.get('community_impact_score', 0) >= 80,
            "platform_master": lambda: profile.metrics.get('platform_count', 0) >= 10,
            "streak_warrior": lambda: profile.longest_streak >= 100,
            "engagement_expert": lambda: profile.metrics.get('engagement_rate', 0) >= 25,
            "seo_specialist": lambda: event.metadata.get('seo_score', 0) >= 95,
            "monetization_guru": lambda: event.metadata.get('revenue_streams', 0) >= 10
        }
        
        # Check each badge condition
        for badge_id, condition in badge_conditions.items():
            if badge_id not in profile.badges:
                try:
                    if condition():
                        profile.badges.append(badge_id)
                        new_badges.append(badge_id)
                        self.logger.info(f"User {profile.user_id} earned badge: {badge_id}")
                except Exception as e:
                    self.logger.warning(f"Error checking badge {badge_id}: {e}")
        
        return new_badges
    
    async def process_queue(self) -> int:
        """Process all pending events in the queue."""
        processed_count = 0
        
        async with self._processing_lock:
            events_to_process = [e for e in self._event_queue if not e.processed]
            
            for event in events_to_process:
                try:
                    await self._process_event(event)
                    processed_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to process event {event.event_id}: {e}")
            
            # Clean up processed events (keep last 1000 for history)
            self._event_queue = [e for e in self._event_queue if not e.processed][-1000:]
        
        return processed_count
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive gamification statistics for a user."""
        profile = await self.get_user_profile(user_id)
        
        current_threshold, next_threshold, progress = profile.calculate_next_level_progress()
        
        return {
            "user_id": user_id,
            "level": profile.level,
            "level_category": profile.get_level_category().value,
            "experience_points": profile.experience_points,
            "total_points_earned": profile.total_points_earned,
            "level_progress": {
                "current_threshold": current_threshold,
                "next_threshold": next_threshold,
                "progress_percentage": progress
            },
            "achievements": {
                "unlocked": profile.achievements,
                "count": len(profile.achievements)
            },
            "badges": {
                "earned": profile.badges,
                "count": len(profile.badges)
            },
            "streaks": {
                "current": profile.current_streak,
                "longest": profile.longest_streak
            },
            "metrics": profile.metrics,
            "virtual_currency": float(profile.virtual_currency),
            "last_activity": profile.last_activity.isoformat() if profile.last_activity else None,
            "profile_age_days": (datetime.utcnow() - profile.created_at).days
        }
    
    async def get_leaderboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get leaderboard-relevant data for a user."""
        profile = await self.get_user_profile(user_id)
        
        return {
            "user_id": user_id,
            "level": profile.level,
            "experience_points": profile.experience_points,
            "achievements_count": len(profile.achievements),
            "badges_count": len(profile.badges),
            "current_streak": profile.current_streak,
            "content_count": profile.metrics.get('content_count', 0),
            "collaboration_count": profile.metrics.get('collaboration_count', 0),
            "revenue_total": profile.metrics.get('revenue_total', 0),
            "quality_score": profile.metrics.get('quality_score', 0),
            "engagement_rate": profile.metrics.get('engagement_rate', 0),
            "global_reach": profile.metrics.get('countries_reached', 0)
        }
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user gamification preferences."""



        try:
            profile = await self.get_user_profile(user_id)
            
            # Update notification preferences
            if 'notifications' in preferences:
                profile.notification_preferences.update(preferences['notifications'])
            
            # Update profile customizations
            if 'customizations' in preferences:
                profile.profile_customizations.update(preferences['customizations'])
            
            profile.updated_at = datetime.utcnow()
            
            self.logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update preferences for user {user_id}: {e}")
            return False
    
    async def simulate_user_journey(
        self,
        user_id: str,
        journey_events: List[Tuple[GamificationEventType, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Simulate a user journey for testing and preview purposes."""
        initial_profile = await self.get_user_profile(user_id)
        initial_stats = await self.get_user_statistics(user_id)
        
        # Record all events in the journey
        for event_type, metadata in journey_events:
            await self.record_event(user_id, event_type, metadata)
        
        final_stats = await self.get_user_statistics(user_id)
        
        return {
            "user_id": user_id,
            "journey_events_count": len(journey_events),
            "initial_stats": initial_stats,
            "final_stats": final_stats,
            "progression": {
                "level_gained": final_stats["level"] - initial_stats["level"],
                "points_earned": final_stats["experience_points"] - initial_stats["experience_points"],
                "achievements_unlocked": len(final_stats["achievements"]["unlocked"]) - len(initial_stats["achievements"]["unlocked"]),
                "badges_earned": len(final_stats["badges"]["earned"]) - len(initial_stats["badges"]["earned"])
            }
        }


# Global gamification manager instance
_gamification_manager: Optional[GamificationManager] = None


async def get_gamification_manager() -> GamificationManager:
    """Get the global gamification manager instance."""
    global _gamification_manager
    
    if _gamification_manager is None:
        _gamification_manager = GamificationManager()
    
    return _gamification_manager


# Convenience functions for common operations
async def record_gamification_event(
    user_id: str,
    event_type: GamificationEventType,
    metadata: Optional[Dict[str, Any]] = None
) -> GamificationEvent:
    """Record a gamification event (convenience function)."""
    manager = await get_gamification_manager()
    return await manager.record_event(user_id, event_type, metadata)


async def get_user_gamification_stats(user_id: str) -> Dict[str, Any]:
    """Get user gamification statistics (convenience function)."""
    manager = await get_gamification_manager()
    return await manager.get_user_statistics(user_id)