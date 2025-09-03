"""Post Scheduler - Planification des posts
==========================================

Intelligent post scheduling system for optimal timing and audience engagement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import pytz

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """Types of post scheduling."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    OPTIMAL = "optimal"
    RECURRING = "recurring"


class PostStatus(str, Enum):
    """Post scheduling status."""
    PENDING = "pending"
    SCHEDULED = "scheduled" 
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledPost:
    """Scheduled post data structure."""
    post_id: str
    content_id: str
    platform: str
    title: str
    content: str
    media_urls: List[str]
    scheduled_time: datetime
    timezone_str: str
    status: PostStatus
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


@dataclass
class OptimalTimeSlot:
    """Optimal time slot for posting."""
    datetime_utc: datetime
    local_time: datetime
    timezone_str: str
    confidence_score: float
    audience_activity: float
    engagement_prediction: float
    platform: str


class PostScheduler:
    """Advanced post scheduler with AI-powered optimal timing."""
    
    def __init__(self):
        """Initialize post scheduler."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.timezone_cache: Dict[str, pytz.BaseTzInfo] = {}
    
    async def schedule_post(
        self,
        content_id: str,
        platform: str,
        title: str,
        content: str,
        media_urls: Optional[List[str]] = None,
        schedule_type: ScheduleType = ScheduleType.OPTIMAL,
        scheduled_time: Optional[datetime] = None,
        timezone_str: str = "UTC",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ScheduledPost:
        """Schedule a post for publication.
        
        Args:
            content_id: Unique content identifier
            platform: Target platform name
            title: Post title
            content: Post content
            media_urls: List of media URLs
            schedule_type: Type of scheduling
            scheduled_time: Specific time to schedule (if SCHEDULED type)
            timezone_str: Timezone for scheduling
            metadata: Additional metadata
            
        Returns:
            ScheduledPost object
        """
        try:
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{platform}"
            
            # Determine scheduling time based on type
            if schedule_type == ScheduleType.IMMEDIATE:
                target_time = datetime.now(timezone.utc)
            elif schedule_type == ScheduleType.SCHEDULED and scheduled_time:
                target_time = self._normalize_datetime(scheduled_time, timezone_str)
            elif schedule_type == ScheduleType.OPTIMAL:
                optimal_slot = await self._find_optimal_time_slot(platform, timezone_str)
                target_time = optimal_slot.datetime_utc
            else:
                # Default to next hour
                target_time = datetime.now(timezone.utc) + timedelta(hours=1)
            
            scheduled_post = ScheduledPost(
                post_id=post_id,
                content_id=content_id,
                platform=platform,
                title=title,
                content=content,
                media_urls=media_urls or [],
                scheduled_time=target_time,
                timezone_str=timezone_str,
                status=PostStatus.SCHEDULED,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                metadata=metadata or {}
            )
            
            self.scheduled_posts[post_id] = scheduled_post
            
            self.logger.info(f"Post scheduled: {post_id} for {platform} at {target_time}")
            return scheduled_post
            
        except Exception as e:
            self.logger.error(f"Failed to schedule post: {str(e)}")
            raise
    
    async def _find_optimal_time_slot(
        self,
        platform: str,
        timezone_str: str,
        days_ahead: int = 7
    ) -> OptimalTimeSlot:
        """Find optimal time slot for posting based on audience data.
        
        Args:
            platform: Target platform
            timezone_str: User timezone
            days_ahead: Days to look ahead for optimal slot
            
        Returns:
            OptimalTimeSlot with best timing
        """
        try:
            # Simulate audience analysis and optimal time calculation
            await asyncio.sleep(0.1)
            
            # Get timezone
            tz = self._get_timezone(timezone_str)
            
            # Platform-specific optimal times (simulated)
            platform_optimal_hours = {
                "instagram": [9, 11, 14, 17, 19],
                "youtube": [14, 16, 18, 20],
                "tiktok": [12, 15, 18, 21],
                "spotify": [8, 12, 16, 20],
                "soundcloud": [10, 14, 17, 21]
            }
            
            optimal_hours = platform_optimal_hours.get(platform.lower(), [12, 15, 18])
            
            # Find next optimal slot
            now = datetime.now(tz)
            for day_offset in range(days_ahead):
                for hour in optimal_hours:
                    candidate_time = now.replace(
                        hour=hour, 
                        minute=0, 
                        second=0, 
                        microsecond=0
                    ) + timedelta(days=day_offset)
                    
                    if candidate_time > now:
                        # Convert to UTC
                        utc_time = candidate_time.astimezone(timezone.utc)
                        
                        return OptimalTimeSlot(
                            datetime_utc=utc_time,
                            local_time=candidate_time,
                            timezone_str=timezone_str,
                            confidence_score=0.85,
                            audience_activity=0.75,
                            engagement_prediction=0.68,
                            platform=platform
                        )
            
            # Fallback to next hour
            fallback_time = now + timedelta(hours=1)
            return OptimalTimeSlot(
                datetime_utc=fallback_time.astimezone(timezone.utc),
                local_time=fallback_time,
                timezone_str=timezone_str,
                confidence_score=0.5,
                audience_activity=0.5,
                engagement_prediction=0.5,
                platform=platform
            )
            
        except Exception as e:
            self.logger.error(f"Failed to find optimal time slot: {str(e)}")
            # Return immediate time as fallback
            now_utc = datetime.now(timezone.utc)
            return OptimalTimeSlot(
                datetime_utc=now_utc,
                local_time=now_utc,
                timezone_str="UTC",
                confidence_score=0.3,
                audience_activity=0.3,
                engagement_prediction=0.3,
                platform=platform
            )
    
    def _get_timezone(self, timezone_str: str) -> pytz.BaseTzInfo:
        """Get timezone object with caching."""
        if timezone_str not in self.timezone_cache:
            try:
                self.timezone_cache[timezone_str] = pytz.timezone(timezone_str)
            except Exception:
                self.logger.warning(f"Invalid timezone {timezone_str}, using UTC")
                self.timezone_cache[timezone_str] = pytz.UTC
        
        return self.timezone_cache[timezone_str]
    
    def _normalize_datetime(self, dt: datetime, timezone_str: str) -> datetime:
        """Normalize datetime to UTC."""
        tz = self._get_timezone(timezone_str)
        
        if dt.tzinfo is None:
            # Assume local timezone
            localized_dt = tz.localize(dt)
        else:
            localized_dt = dt.astimezone(tz)
        
        return localized_dt.astimezone(timezone.utc)
    
    async def get_scheduled_posts(
        self,
        platform: Optional[str] = None,
        status: Optional[PostStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ScheduledPost]:
        """Get scheduled posts with filtering.
        
        Args:
            platform: Filter by platform
            status: Filter by status
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of matching scheduled posts
        """
        posts = list(self.scheduled_posts.values())
        
        if platform:
            posts = [p for p in posts if p.platform.lower() == platform.lower()]
        
        if status:
            posts = [p for p in posts if p.status == status]
        
        if start_time:
            posts = [p for p in posts if p.scheduled_time >= start_time]
        
        if end_time:
            posts = [p for p in posts if p.scheduled_time <= end_time]
        
        return sorted(posts, key=lambda p: p.scheduled_time)
    
    async def update_post_status(self, post_id: str, status: PostStatus) -> bool:
        """Update post status.
        
        Args:
            post_id: Post identifier
            status: New status
            
        Returns:
            True if successful
        """
        if post_id in self.scheduled_posts:
            self.scheduled_posts[post_id].status = status
            self.scheduled_posts[post_id].updated_at = datetime.now(timezone.utc)
            
            self.logger.info(f"Post {post_id} status updated to {status.value}")
            return True
        
        return False
    
    async def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post.
        
        Args:
            post_id: Post identifier
            
        Returns:
            True if successful
        """
        return await self.update_post_status(post_id, PostStatus.CANCELLED)
    
    async def get_optimal_times_analysis(
        self,
        platform: str,
        timezone_str: str = "UTC",
        days: int = 7
    ) -> Dict[str, Any]:
        """Get optimal posting times analysis.
        
        Args:
            platform: Platform to analyze
            timezone_str: Timezone for analysis
            days: Number of days to analyze
            
        Returns:
            Analysis data
        """
        try:
            # Simulate analysis
            await asyncio.sleep(0.1)
            
            return {
                "platform": platform,
                "timezone": timezone_str,
                "analysis_period_days": days,
                "optimal_hours": [9, 12, 15, 18, 21],
                "peak_days": ["tuesday", "wednesday", "thursday"],
                "engagement_by_hour": {
                    str(hour): 0.3 + (hour % 12) * 0.05 
                    for hour in range(24)
                },
                "audience_activity": {
                    "morning": 0.6,
                    "afternoon": 0.8,
                    "evening": 0.9,
                    "night": 0.3
                },
                "recommendations": [
                    f"Best time to post on {platform} is between 6-8 PM in your timezone",
                    "Avoid posting late at night or very early morning",
                    "Tuesday through Thursday show highest engagement"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate analysis: {str(e)}")
            return {}


# Global scheduler instance
_post_scheduler: Optional[PostScheduler] = None


def get_post_scheduler() -> PostScheduler:
    """Get global post scheduler instance."""
    global _post_scheduler
    
    if _post_scheduler is None:
        _post_scheduler = PostScheduler()
    
    return _post_scheduler


# Convenience functions
async def schedule_post(
    content_id: str,
    platform: str,
    title: str,
    content: str,
    schedule_type: ScheduleType = ScheduleType.OPTIMAL,
    **kwargs
) -> ScheduledPost:
    """Convenience function to schedule a post."""
    scheduler = get_post_scheduler()
    return await scheduler.schedule_post(
        content_id=content_id,
        platform=platform,
        title=title,
        content=content,
        schedule_type=schedule_type,
        **kwargs
    )


async def get_optimal_time(platform: str, timezone_str: str = "UTC") -> OptimalTimeSlot:
    """Convenience function to get optimal posting time."""
    scheduler = get_post_scheduler()
    return await scheduler._find_optimal_time_slot(platform, timezone_str)