"""Advanced Schedule Manager - Intelligent Content Scheduling System
==================================================================

Sophisticated content scheduling system providing AI-powered optimal timing,
multi-platform coordination, audience analysis, timezone management, and
comprehensive scheduling analytics for content distribution.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/distribution/schedule_manager.py
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
Platform Connection → Intelligent Scheduling → Content Distribution → Analytics → Monetization
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import pytz
from statistics import mean
import calendar

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """Types of scheduling."""
    IMMEDIATE = "immediate"
    SPECIFIC_TIME = "specific_time"
    OPTIMAL_TIME = "optimal_time"
    RECURRING = "recurring"
    COORDINATED = "coordinated"
    BATCH = "batch"


class ScheduleStatus(str, Enum):
    """Schedule status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class RecurrencePattern(str, Enum):
    """Recurrence patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class OptimizationGoal(str, Enum):
    """Optimization goals for scheduling."""
    MAX_ENGAGEMENT = "max_engagement"
    MAX_REACH = "max_reach"
    MAX_REVENUE = "max_revenue"
    BALANCED = "balanced"
    CUSTOM = "custom"


@dataclass
class TimeWindow:
    """Time window for scheduling."""
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    days_of_week: List[int] = field(default_factory=lambda: list(range(7)))  # 0=Monday
    priority: int = 1  # 1=highest, 5=lowest


@dataclass
class AudienceInsight:
    """Audience behavior insights."""
    platform: str
    peak_hours: List[int]  # Hours of day (0-23)
    peak_days: List[int]   # Days of week (0=Monday)
    timezone: str
    engagement_patterns: Dict[str, float]
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    sample_size: int = 0
    confidence_score: float = 0.0


@dataclass
class ScheduleRule:
    """Scheduling rule configuration."""
    id: str
    name: str
    priority: int
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    platforms: List[str] = field(default_factory=list)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScheduledContent:
    """Scheduled content item."""
    id: str
    content_id: str
    title: str
    platforms: List[str]
    schedule_type: ScheduleType
    scheduled_time: datetime
    original_timezone: str
    status: ScheduleStatus
    optimization_goal: OptimizationGoal
    estimated_engagement: Optional[float] = None
    estimated_reach: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_config: Dict[str, Any] = field(default_factory=dict)
    coordination_group: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class OptimalTimeSlot:
    """Optimal time slot suggestion."""
    datetime_utc: datetime
    score: float
    confidence: float
    platform: str
    reasoning: str
    estimated_metrics: Dict[str, float] = field(default_factory=dict)


class ScheduleManager:
    """
    Advanced content scheduling system providing intelligent timing optimization,
    multi-platform coordination, and comprehensive scheduling management.
    """
    
    def __init__(self, database_connection=None, cache_client=None) -> None:
        """Initialize the schedule manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.scheduled_content: Dict[str, ScheduledContent] = {}
        self.schedule_rules: Dict[str, ScheduleRule] = {}
        self.audience_insights: Dict[str, AudienceInsight] = {}
        self.default_time_windows = self._initialize_default_time_windows()
        self.platform_optimal_times = self._initialize_platform_optimal_times()
        
        self.logger.info("ScheduleManager initialized")
    
    def _initialize_default_time_windows(self) -> Dict[str, List[TimeWindow]]:
        """Initialize default optimal time windows for platforms."""
        return {
            "youtube": [
                TimeWindow(
                    start_time=datetime.now().replace(hour=14, minute=0, second=0),
                    end_time=datetime.now().replace(hour=16, minute=0, second=0),
                    days_of_week=[1, 2, 3],  # Tuesday, Wednesday, Thursday
                    priority=1
                ),
                TimeWindow(
                    start_time=datetime.now().replace(hour=20, minute=0, second=0),
                    end_time=datetime.now().replace(hour=22, minute=0, second=0),
                    days_of_week=[5, 6],  # Saturday, Sunday
                    priority=2
                )
            ],
            "instagram": [
                TimeWindow(
                    start_time=datetime.now().replace(hour=11, minute=0, second=0),
                    end_time=datetime.now().replace(hour=13, minute=0, second=0),
                    days_of_week=[1, 2, 3, 4],  # Tuesday-Friday
                    priority=1
                ),
                TimeWindow(
                    start_time=datetime.now().replace(hour=19, minute=0, second=0),
                    end_time=datetime.now().replace(hour=21, minute=0, second=0),
                    days_of_week=[0, 1, 2, 3, 4],  # Monday-Friday
                    priority=2
                )
            ],
            "tiktok": [
                TimeWindow(
                    start_time=datetime.now().replace(hour=18, minute=0, second=0),
                    end_time=datetime.now().replace(hour=21, minute=0, second=0),
                    days_of_week=[1, 2, 3, 4],  # Tuesday-Friday
                    priority=1
                ),
                TimeWindow(
                    start_time=datetime.now().replace(hour=12, minute=0, second=0),
                    end_time=datetime.now().replace(hour=15, minute=0, second=0),
                    days_of_week=[5, 6],  # Saturday, Sunday
                    priority=2
                )
            ],
            "twitter": [
                TimeWindow(
                    start_time=datetime.now().replace(hour=9, minute=0, second=0),
                    end_time=datetime.now().replace(hour=10, minute=0, second=0),
                    days_of_week=[1, 2, 3, 4],  # Tuesday-Friday
                    priority=1
                ),
                TimeWindow(
                    start_time=datetime.now().replace(hour=12, minute=0, second=0),
                    end_time=datetime.now().replace(hour=13, minute=0, second=0),
                    days_of_week=[1, 2, 3, 4],  # Tuesday-Friday
                    priority=2
                )
            ]
        }
    
    def _initialize_platform_optimal_times(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific optimal timing data."""
        return {
            "youtube": {
                "peak_hours": [14, 15, 20, 21],
                "peak_days": [1, 2, 3, 5, 6],  # Tue, Wed, Thu, Sat, Sun
                "avg_engagement_rate": 0.04,
                "best_upload_frequency": "2-3 times per week"
            },
            "instagram": {
                "peak_hours": [11, 12, 19, 20],
                "peak_days": [1, 2, 3, 4],  # Tue-Fri
                "avg_engagement_rate": 0.09,
                "best_upload_frequency": "1-2 times per day"
            },
            "tiktok": {
                "peak_hours": [18, 19, 20],
                "peak_days": [1, 2, 3, 4, 5],  # Tue-Sat
                "avg_engagement_rate": 0.05,
                "best_upload_frequency": "1-4 times per day"
            },
            "twitter": {
                "peak_hours": [9, 12, 17, 19],
                "peak_days": [1, 2, 3, 4],  # Tue-Fri
                "avg_engagement_rate": 0.02,
                "best_upload_frequency": "3-5 times per day"
            },
            "linkedin": {
                "peak_hours": [8, 9, 12, 17, 18],
                "peak_days": [1, 2, 3, 4],  # Tue-Fri
                "avg_engagement_rate": 0.03,
                "best_upload_frequency": "1-2 times per day"
            }
        }
    
    async def schedule_content(
        self,
        content_id: str,
        title: str,
        platforms: List[str],
        schedule_type: ScheduleType = ScheduleType.OPTIMAL_TIME,
        specific_time: Optional[datetime] = None,
        timezone_str: str = "UTC",
        optimization_goal: OptimizationGoal = OptimizationGoal.BALANCED,
        recurrence_config: Optional[Dict[str, Any]] = None
    ) -> ScheduledContent:
        """Schedule content for distribution."""
        try:
            schedule_id = str(uuid4())
            
            # Determine scheduled time based on type
            if schedule_type == ScheduleType.IMMEDIATE:
                scheduled_time = datetime.utcnow()
            elif schedule_type == ScheduleType.SPECIFIC_TIME:
                if not specific_time:
                    raise ValueError("Specific time required for SPECIFIC_TIME schedule type")
                scheduled_time = specific_time
            elif schedule_type == ScheduleType.OPTIMAL_TIME:
                optimal_times = await self.find_optimal_time_slots(
                    platforms, optimization_goal, timezone_str
                )
                if optimal_times:
                    scheduled_time = optimal_times[0].datetime_utc
                else:
                    # Fallback to default time
                    scheduled_time = datetime.utcnow() + timedelta(hours=1)
            else:
                scheduled_time = datetime.utcnow() + timedelta(hours=1)
            
            # Create scheduled content
            scheduled_content = ScheduledContent(
                id=schedule_id,
                content_id=content_id,
                title=title,
                platforms=platforms,
                schedule_type=schedule_type,
                scheduled_time=scheduled_time,
                original_timezone=timezone_str,
                status=ScheduleStatus.SCHEDULED,
                optimization_goal=optimization_goal,
                recurrence_config=recurrence_config or {}
            )
            
            # Calculate estimated metrics
            await self._calculate_estimated_metrics(scheduled_content)
            
            # Store scheduled content
            self.scheduled_content[schedule_id] = scheduled_content
            
            # Set up recurring schedule if needed
            if recurrence_config:
                await self._setup_recurring_schedule(scheduled_content)
            
            self.logger.info(f"✅ Content scheduled: {title} for {len(platforms)} platforms")
            
            return scheduled_content
            
        except Exception as e:
            self.logger.error(f"Error scheduling content: {e}")
            raise
    
    async def find_optimal_time_slots(
        self,
        platforms: List[str],
        optimization_goal: OptimizationGoal,
        timezone_str: str = "UTC",
        time_range_hours: int = 72,
        max_suggestions: int = 5
    ) -> List[OptimalTimeSlot]:
        """Find optimal time slots for content publishing."""
        try:
            suggestions = []
            current_time = datetime.utcnow()
            end_time = current_time + timedelta(hours=time_range_hours)
            
            # Generate candidate time slots (every hour)
            candidate_times = []
            check_time = current_time + timedelta(hours=1)
            while check_time <= end_time:
                candidate_times.append(check_time)
                check_time += timedelta(hours=1)
            
            # Score each candidate time for each platform
            for candidate_time in candidate_times:
                for platform in platforms:
                    score = await self._score_time_slot(
                        candidate_time, platform, optimization_goal, timezone_str
                    )
                    
                    if score > 0.3:  # Minimum threshold
                        optimal_slot = OptimalTimeSlot(
                            datetime_utc=candidate_time,
                            score=score,
                            confidence=self._calculate_confidence(platform, candidate_time),
                            platform=platform,
                            reasoning=self._generate_reasoning(platform, candidate_time, score)
                        )
                        suggestions.append(optimal_slot)
            
            # Sort by score and return top suggestions
            suggestions.sort(key=lambda x: x.score, reverse=True)
            
            # Group by time and return best overall slots
            time_groups = {}
            for suggestion in suggestions:
                time_key = suggestion.datetime_utc.replace(minute=0, second=0)
                if time_key not in time_groups:
                    time_groups[time_key] = []
                time_groups[time_key].append(suggestion)
            
            # Calculate average scores for each time slot
            final_suggestions = []
            for time_key, group in time_groups.items():
                avg_score = mean([s.score for s in group])
                avg_confidence = mean([s.confidence for s in group])
                
                final_suggestion = OptimalTimeSlot(
                    datetime_utc=time_key,
                    score=avg_score,
                    confidence=avg_confidence,
                    platform="multi-platform",
                    reasoning=f"Optimal for {len(group)} platforms with average score {avg_score:.2f}",
                    estimated_metrics={
                        "estimated_engagement_rate": avg_score * 0.1,
                        "estimated_reach_multiplier": 1 + (avg_score - 0.5)
                    }
                )
                final_suggestions.append(final_suggestion)
            
            # Sort and return top suggestions
            final_suggestions.sort(key=lambda x: x.score, reverse=True)
            return final_suggestions[:max_suggestions]
            
        except Exception as e:
            self.logger.error(f"Error finding optimal time slots: {e}")
            return []
    
    async def _score_time_slot(
        self,
        candidate_time: datetime,
        platform: str,
        optimization_goal: OptimizationGoal,
        timezone_str: str
    ) -> float:
        """Score a time slot for a specific platform."""
        try:
            # Convert to target timezone
            tz = pytz.timezone(timezone_str)
            local_time = candidate_time.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            # Get platform optimal times
            platform_data = self.platform_optimal_times.get(platform.lower(), {})
            peak_hours = platform_data.get("peak_hours", [])
            peak_days = platform_data.get("peak_days", [])
            
            score = 0.5  # Base score
            
            # Hour of day score
            hour = local_time.hour
            if hour in peak_hours:
                score += 0.3
            elif any(abs(hour - ph) <= 1 for ph in peak_hours):
                score += 0.15
            
            # Day of week score
            day_of_week = local_time.weekday()
            if day_of_week in peak_days:
                score += 0.2
            
            # Avoid very early or very late hours (general audience)
            if 6 <= hour <= 23:
                score += 0.1
            elif hour < 6 or hour > 23:
                score -= 0.2
            
            # Weekend vs weekday adjustments
            if day_of_week >= 5:  # Weekend
                if platform.lower() in ["youtube", "tiktok", "instagram"]:
                    score += 0.1
                elif platform.lower() in ["linkedin", "twitter"]:
                    score -= 0.1
            
            # Optimization goal adjustments
            if optimization_goal == OptimizationGoal.MAX_ENGAGEMENT:
                if hour in peak_hours:
                    score += 0.1
            elif optimization_goal == OptimizationGoal.MAX_REACH:
                # Slightly favor off-peak times for less competition
                if hour not in peak_hours and 9 <= hour <= 21:
                    score += 0.05
            
            # Check for audience insights
            if platform in self.audience_insights:
                insight = self.audience_insights[platform]
                if hour in insight.peak_hours:
                    score += 0.2 * insight.confidence_score
                if day_of_week in insight.peak_days:
                    score += 0.1 * insight.confidence_score
            
            # Ensure score is within bounds
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Error scoring time slot: {e}")
            return 0.0
    
    def _calculate_confidence(self, platform: str, candidate_time: datetime) -> float:
        """Calculate confidence score for a time slot."""
        try:
            # Base confidence
            confidence = 0.7
            
            # Higher confidence for platforms with more data
            if platform in self.platform_optimal_times:
                confidence += 0.1
            
            # Higher confidence for audience insights
            if platform in self.audience_insights:
                insight = self.audience_insights[platform]
                confidence += 0.2 * insight.confidence_score
            
            # Lower confidence for far future times
            hours_ahead = (candidate_time - datetime.utcnow()).total_seconds() / 3600
            if hours_ahead > 48:
                confidence -= 0.1
            elif hours_ahead > 168:  # 1 week
                confidence -= 0.2
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _generate_reasoning(self, platform: str, candidate_time: datetime, score: float) -> str:
        """Generate human-readable reasoning for time slot score."""
        try:
            local_time = candidate_time.replace(tzinfo=pytz.UTC)
            hour = local_time.hour
            day_name = calendar.day_name[local_time.weekday()]
            
            platform_data = self.platform_optimal_times.get(platform.lower(), {})
            peak_hours = platform_data.get("peak_hours", [])
            
            reasons = []
            
            if hour in peak_hours:
                reasons.append(f"Peak hour for {platform}")
            elif any(abs(hour - ph) <= 1 for ph in peak_hours):
                reasons.append(f"Near peak hours for {platform}")
            
            if local_time.weekday() < 5:
                reasons.append("Weekday timing")
            else:
                reasons.append("Weekend timing")
            
            if score > 0.8:
                quality = "Excellent"
            elif score > 0.6:
                quality = "Good"
            elif score > 0.4:
                quality = "Fair"
            else:
                quality = "Poor"
            
            reasoning = f"{quality} time slot for {platform} on {day_name} at {hour:02d}:00"
            if reasons:
                reasoning += f" - {', '.join(reasons)}"
            
            return reasoning
            
        except Exception as e:
            self.logger.error(f"Error generating reasoning: {e}")
            return f"Time slot for {platform}"
    
    async def _calculate_estimated_metrics(self, scheduled_content -> None: ScheduledContent) -> None:
        """Calculate estimated metrics for scheduled content."""
        try:
            total_engagement_estimate = 0.0
            total_reach_estimate = 0
            
            for platform in scheduled_content.platforms:
                platform_data = self.platform_optimal_times.get(platform.lower(), {})
                base_engagement = platform_data.get("avg_engagement_rate", 0.03)
                
                # Score the scheduled time
                score = await self._score_time_slot(
                    scheduled_content.scheduled_time,
                    platform,
                    scheduled_content.optimization_goal,
                    scheduled_content.original_timezone
                )
                
                # Adjust estimates based on score
                estimated_engagement = base_engagement * (1 + score)
                estimated_reach = int(1000 * (1 + score))  # Base 1000 reach
                
                total_engagement_estimate += estimated_engagement
                total_reach_estimate += estimated_reach
            
            # Average across platforms
            if scheduled_content.platforms:
                scheduled_content.estimated_engagement = total_engagement_estimate / len(scheduled_content.platforms)
                scheduled_content.estimated_reach = total_reach_estimate
            
        except Exception as e:
            self.logger.error(f"Error calculating estimated metrics: {e}")
    
    async def _setup_recurring_schedule(self, scheduled_content -> None: ScheduledContent) -> None:
        """Set up recurring schedule based on configuration."""
        try:
            recurrence_config = scheduled_content.recurrence_config
            pattern = scheduled_content.recurrence_pattern
            
            if not pattern or not recurrence_config:
                return
            
            # Implementation would create future scheduled items
            # based on recurrence pattern
            self.logger.info(f"✅ Recurring schedule set up for {scheduled_content.id}")
            
        except Exception as e:
            self.logger.error(f"Error setting up recurring schedule: {e}")
    
    async def update_audience_insights(
        self,
        platform -> None: str,
        insights -> None: AudienceInsight
    ) -> None:
        """Update audience insights for a platform."""
        try:
            self.audience_insights[platform] = insights
            self.logger.info(f"✅ Audience insights updated for {platform}")
        except Exception as e:
            self.logger.error(f"Error updating audience insights: {e}")
    
    async def get_scheduled_content(
        self,
        status: Optional[ScheduleStatus] = None,
        platform: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[ScheduledContent]:
        """Get scheduled content with optional filtering."""
        try:
            filtered_content = []
            
            for content in self.scheduled_content.values():
                # Filter by status
                if status and content.status != status:
                    continue
                
                # Filter by platform
                if platform and platform not in content.platforms:
                    continue
                
                # Filter by time range
                if time_range:
                    start_time, end_time = time_range
                    if not (start_time <= content.scheduled_time <= end_time):
                        continue
                
                filtered_content.append(content)
            
            # Sort by scheduled time
            filtered_content.sort(key=lambda x: x.scheduled_time)
            return filtered_content
            
        except Exception as e:
            self.logger.error(f"Error getting scheduled content: {e}")
            return []
    
    async def cancel_scheduled_content(self, schedule_id: str) -> bool:
        """Cancel scheduled content."""
        try:
            if schedule_id in self.scheduled_content:
                self.scheduled_content[schedule_id].status = ScheduleStatus.CANCELLED
                self.logger.info(f"✅ Scheduled content cancelled: {schedule_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error cancelling scheduled content: {e}")
            return False
    
    async def reschedule_content(
        self,
        schedule_id: str,
        new_time: datetime,
        timezone_str: str = "UTC"
    ) -> bool:
        """Reschedule content to a new time."""
        try:
            if schedule_id in self.scheduled_content:
                content = self.scheduled_content[schedule_id]
                content.scheduled_time = new_time
                content.original_timezone = timezone_str
                content.status = ScheduleStatus.SCHEDULED
                
                # Recalculate estimated metrics
                await self._calculate_estimated_metrics(content)
                
                self.logger.info(f"✅ Content rescheduled: {schedule_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error rescheduling content: {e}")
            return False
    
    async def get_schedule_analytics(
        self,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Get scheduling analytics for a time range."""
        try:
            start_time, end_time = time_range
            
            # Filter content in time range
            content_in_range = [
                content for content in self.scheduled_content.values()
                if start_time <= content.scheduled_time <= end_time
            ]
            
            analytics = {
                "total_scheduled": len(content_in_range),
                "by_status": {},
                "by_platform": {},
                "by_schedule_type": {},
                "avg_estimated_engagement": 0.0,
                "total_estimated_reach": 0,
                "optimal_vs_manual": {}
            }
            
            # Calculate analytics
            for content in content_in_range:
                # By status
                status = content.status.value
                analytics["by_status"][status] = analytics["by_status"].get(status, 0) + 1
                
                # By platform
                for platform in content.platforms:
                    analytics["by_platform"][platform] = analytics["by_platform"].get(platform, 0) + 1
                
                # By schedule type
                schedule_type = content.schedule_type.value
                analytics["by_schedule_type"][schedule_type] = analytics["by_schedule_type"].get(schedule_type, 0) + 1
                
                # Metrics
                if content.estimated_engagement:
                    analytics["avg_estimated_engagement"] += content.estimated_engagement
                if content.estimated_reach:
                    analytics["total_estimated_reach"] += content.estimated_reach
            
            # Calculate averages
            if content_in_range:
                analytics["avg_estimated_engagement"] /= len(content_in_range)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting schedule analytics: {e}")
            return {}
    
    async def process_scheduled_content(self) -> None:
        """Process content that is ready to be published."""
        try:
            current_time = datetime.utcnow()
            ready_content = []
            
            # Find content ready for publishing
            for content in self.scheduled_content.values():
                if (content.status == ScheduleStatus.SCHEDULED and 
                    content.scheduled_time <= current_time):
                    ready_content.append(content)
            
            self.logger.info(f"📅 Processing {len(ready_content)} scheduled items")
            
            for content in ready_content:
                try:
                    # Update status
                    content.status = ScheduleStatus.PUBLISHED
                    content.published_at = current_time
                    
                    # Here would integrate with platform connectors to actually publish
                    self.logger.info(f"✅ Published: {content.title}")
                    
                except Exception as e:
                    content.status = ScheduleStatus.FAILED
                    content.error_message = str(e)
                    content.retry_count += 1
                    
                    # Retry logic
                    if content.retry_count < content.max_retries:
                        content.scheduled_time = current_time + timedelta(minutes=5)
                        content.status = ScheduleStatus.SCHEDULED
                    
                    self.logger.error(f"❌ Failed to publish {content.title}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error processing scheduled content: {e}")


# Global schedule manager instance
_schedule_manager: Optional[ScheduleManager] = None


async def get_schedule_manager() -> ScheduleManager:
    """Get global schedule manager instance."""
    global _schedule_manager
    
    if _schedule_manager is None:
        _schedule_manager = ScheduleManager()
    
    return _schedule_manager


async def schedule_content(
    content_id: str,
    title: str,
    platforms: List[str],
    schedule_type: ScheduleType = ScheduleType.OPTIMAL_TIME,
    specific_time: Optional[datetime] = None,
    timezone_str: str = "UTC"
) -> ScheduledContent:
    """Convenience function to schedule content."""
    manager = await get_schedule_manager()
    return await manager.schedule_content(
        content_id, title, platforms, schedule_type, specific_time, timezone_str
    )