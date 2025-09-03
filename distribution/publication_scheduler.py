"""Publication Scheduler

Advanced cross-platform content scheduling system with optimal timing analysis,
audience engagement optimization, and automated publication management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from collections import defaultdict
try:
    import pytz
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.date import DateTrigger
except ImportError:
    pytz = AsyncIOScheduler = CronTrigger = DateTrigger = None

from .platform_connectors import SocialPlatform, ContentPayload, PublicationResult, PlatformConnectorManager

logger = logging.getLogger(__name__)


class ScheduleStrategy(Enum):
    """Content scheduling strategies"""
    OPTIMAL_TIMING = "optimal_timing"
    CUSTOM_TIME = "custom_time"
    AUDIENCE_BASED = "audience_based"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    EVENT_TRIGGERED = "event_triggered"
    MULTI_WAVE = "multi_wave"
    AB_TESTING = "ab_testing"


class PublicationStatus(Enum):
    """Publication status states"""
    SCHEDULED = "scheduled"
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class TimeZonePreference(Enum):
    """Timezone optimization preferences"""
    USER_TIMEZONE = "user_timezone"
    AUDIENCE_TIMEZONE = "audience_timezone"
    PLATFORM_OPTIMAL = "platform_optimal"
    GLOBAL_OPTIMAL = "global_optimal"


@dataclass
class AudienceInsight:
    """Audience engagement insights"""
    platform: SocialPlatform
    timezone: str
    peak_hours: List[int]  # Hours of day (0-23)
    peak_days: List[int]   # Days of week (0-6, Monday=0)
    engagement_rate: float
    active_users_count: int
    demographic_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduledPublication:
    """Scheduled publication data"""
    id: str
    user_id: str
    content: ContentPayload
    platforms: List[SocialPlatform]
    scheduled_time: datetime
    strategy: ScheduleStrategy
    status: PublicationStatus
    timezone: str = "UTC"
    retry_count: int = 0
    max_retries: int = 3
    audience_insights: List[AudienceInsight] = field(default_factory=list)
    optimization_settings: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    published_results: Dict[SocialPlatform, PublicationResult] = field(default_factory=dict)


@dataclass
class OptimalTimeSlot:
    """Optimal publication time slot"""
    platform: SocialPlatform
    datetime_slot: datetime
    engagement_score: float
    audience_size: int
    competition_level: float
    confidence: float


class PublicationScheduler:
    """Advanced publication scheduler with optimal timing analysis"""
    
    # Platform-specific optimal times (based on research data)
    PLATFORM_OPTIMAL_TIMES = {
        SocialPlatform.YOUTUBE: {
            "weekdays": [14, 15, 16, 17, 18],  # 2-6 PM
            "weekends": [10, 11, 12, 13, 14],  # 10 AM-2 PM
            "peak_days": [1, 2, 3, 4]  # Tuesday-Friday
        },
        SocialPlatform.TIKTOK: {
            "weekdays": [18, 19, 20, 21],  # 6-9 PM
            "weekends": [12, 13, 14, 15],  # 12-3 PM
            "peak_days": [0, 1, 2, 3]  # Monday-Thursday
        },
        SocialPlatform.INSTAGRAM: {
            "weekdays": [11, 12, 17, 18, 19],  # 11 AM-12 PM, 5-7 PM
            "weekends": [10, 11, 12, 13],  # 10 AM-1 PM
            "peak_days": [2, 3, 4]  # Wednesday-Friday
        },
        SocialPlatform.TWITTER: {
            "weekdays": [8, 9, 12, 13, 17, 18],  # 8-9 AM, 12-1 PM, 5-6 PM
            "weekends": [10, 11, 12],  # 10 AM-12 PM
            "peak_days": [1, 2, 3, 4]  # Tuesday-Friday
        },
        SocialPlatform.FACEBOOK: {
            "weekdays": [13, 14, 15],  # 1-3 PM
            "weekends": [14, 15, 16],  # 2-4 PM
            "peak_days": [2, 3, 4]  # Wednesday-Friday
        },
        SocialPlatform.LINKEDIN: {
            "weekdays": [8, 9, 10, 17, 18],  # 8-10 AM, 5-6 PM
            "weekends": [],  # Not optimal for LinkedIn
            "peak_days": [1, 2, 3, 4]  # Tuesday-Friday
        }
    }
    
    def __init__(self, connector_manager: PlatformConnectorManager):
        self.connector_manager = connector_manager
        self.scheduler = AsyncIOScheduler()
        self.scheduled_publications: Dict[str, ScheduledPublication] = {}
        self.audience_insights: Dict[str, List[AudienceInsight]] = {}
        self.publication_history: List[ScheduledPublication] = []
        
        # Start the scheduler
        self.scheduler.start()
    
    async def schedule_publication(
        self,
        user_id: str,
        content: ContentPayload,
        platforms: List[SocialPlatform],
        strategy: ScheduleStrategy = ScheduleStrategy.OPTIMAL_TIMING,
        custom_time: Optional[datetime] = None,
        timezone_preference: TimeZonePreference = TimeZonePreference.AUDIENCE_TIMEZONE,
        optimization_settings: Optional[Dict] = None
    ) -> ScheduledPublication:
        """Schedule content publication across multiple platforms"""
        try:
            publication_id = str(uuid.uuid4())
            
            # Determine optimal timing based on strategy
            if strategy == ScheduleStrategy.CUSTOM_TIME and custom_time:
                scheduled_time = custom_time
            else:
                scheduled_time = await self._calculate_optimal_time(
                    user_id, platforms, strategy, timezone_preference
                )
            
            # Get audience insights for optimization
            insights = await self._get_audience_insights(user_id, platforms)
            
            publication = ScheduledPublication(
                id=publication_id,
                user_id=user_id,
                content=content,
                platforms=platforms,
                scheduled_time=scheduled_time,
                strategy=strategy,
                status=PublicationStatus.SCHEDULED,
                audience_insights=insights,
                optimization_settings=optimization_settings or {}
            )
            
            # Store the scheduled publication
            self.scheduled_publications[publication_id] = publication
            
            # Schedule the job
            self.scheduler.add_job(
                self._execute_publication,
                trigger=DateTrigger(run_date=scheduled_time),
                args=[publication_id],
                id=publication_id,
                misfire_grace_time=300  # 5 minutes grace period
            )
            
            logger.info(f"Publication scheduled for {scheduled_time} across {len(platforms)} platforms")
            return publication
        
        except Exception as e:
            logger.error(f"Failed to schedule publication: {str(e)}")
            raise
    
    async def _calculate_optimal_time(
        self,
        user_id: str,
        platforms: List[SocialPlatform],
        strategy: ScheduleStrategy,
        timezone_preference: TimeZonePreference
    ) -> datetime:
        """Calculate optimal publication time based on strategy"""
        try:
            # Get user's timezone
            user_timezone = await self._get_user_timezone(user_id)
            
            # Get audience insights
            insights = await self._get_audience_insights(user_id, platforms)
            
            # Calculate optimal times for each platform
            optimal_slots = []
            
            for platform in platforms:
                platform_slots = await self._get_platform_optimal_slots(
                    platform, insights, user_timezone, strategy
                )
                optimal_slots.extend(platform_slots)
            
            if not optimal_slots:
                # Fallback to general optimal time
                return datetime.now() + timedelta(hours=2)
            
            # Find the best overall time slot
            best_slot = max(optimal_slots, key=lambda x: x.engagement_score)
            
            # Adjust for timezone preference
            if timezone_preference == TimeZonePreference.USER_TIMEZONE:
                user_tz = pytz.timezone(user_timezone)
                return user_tz.localize(best_slot.datetime_slot.replace(tzinfo=None))
            elif timezone_preference == TimeZonePreference.AUDIENCE_TIMEZONE:
                # Use the timezone with highest engagement
                if insights:
                    best_insight = max(insights, key=lambda x: x.engagement_rate)
                    audience_tz = pytz.timezone(best_insight.timezone)
                    return audience_tz.localize(best_slot.datetime_slot.replace(tzinfo=None))
            
            return best_slot.datetime_slot
        
        except Exception as e:
            logger.error(f"Optimal time calculation failed: {str(e)}")
            # Fallback to 2 hours from now
            return datetime.now() + timedelta(hours=2)
    
    async def _get_platform_optimal_slots(
        self,
        platform: SocialPlatform,
        insights: List[AudienceInsight],
        user_timezone: str,
        strategy: ScheduleStrategy
    ) -> List[OptimalTimeSlot]:
        """Get optimal time slots for a specific platform"""
        try:
            slots = []
            
            # Get platform-specific insights
            platform_insights = [i for i in insights if i.platform == platform]
            
            # Get platform optimal times configuration
            platform_config = self.PLATFORM_OPTIMAL_TIMES.get(platform, {})
            
            # Generate time slots for next 7 days
            now = datetime.now()
            
            for day_offset in range(7):
                target_date = now + timedelta(days=day_offset)
                day_of_week = target_date.weekday()
                
                # Check if day is optimal for platform
                peak_days = platform_config.get("peak_days", [])
                day_score = 1.0 if day_of_week in peak_days else 0.5
                
                # Get optimal hours for the day
                is_weekend = day_of_week >= 5
                optimal_hours = platform_config.get(
                    "weekends" if is_weekend else "weekdays", 
                    [12, 13, 14, 15, 16]
                )
                
                for hour in optimal_hours:
                    slot_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    # Skip past times
                    if slot_time <= now:
                        continue
                    
                    # Calculate engagement score
                    engagement_score = day_score
                    audience_size = 1000  # Default
                    
                    # Enhance with audience insights
                    if platform_insights:
                        for insight in platform_insights:
                            if hour in insight.peak_hours and day_of_week in insight.peak_days:
                                engagement_score *= (1 + insight.engagement_rate)
                                audience_size = max(audience_size, insight.active_users_count)
                    
                    # Calculate competition level (simplified)
                    competition_level = await self._estimate_competition_level(
                        platform, slot_time
                    )
                    
                    # Adjust score based on competition
                    engagement_score *= (1 - competition_level * 0.3)
                    
                    slot = OptimalTimeSlot(
                        platform=platform,
                        datetime_slot=slot_time,
                        engagement_score=engagement_score,
                        audience_size=audience_size,
                        competition_level=competition_level,
                        confidence=0.8  # Base confidence
                    )
                    
                    slots.append(slot)
            
            # Sort by engagement score
            slots.sort(key=lambda x: x.engagement_score, reverse=True)
            
            # Return top 10 slots
            return slots[:10]
        
        except Exception as e:
            logger.error(f"Platform optimal slots calculation failed: {str(e)}")
            return []
    
    async def _execute_publication(self, publication_id: str):
        """Execute a scheduled publication"""
        try:
            publication = self.scheduled_publications.get(publication_id)
            if not publication:
                logger.error(f"Publication {publication_id} not found")
                return
            
            # Update status
            publication.status = PublicationStatus.PUBLISHING
            publication.updated_at = datetime.now()
            
            logger.info(f"Executing publication {publication_id} to {len(publication.platforms)} platforms")
            
            # Execute publication through connector manager
            results = await self.connector_manager.publish_content(
                platforms=publication.platforms,
                content=publication.content,
                optimization_settings=publication.optimization_settings
            )
            
            # Store results
            publication.published_results = results
            
            # Check if all publications succeeded
            successful_platforms = [
                platform for platform, result in results.items() 
                if result.status == PublicationStatus.PUBLISHED
            ]
            
            failed_platforms = [
                platform for platform, result in results.items()
                if result.status == PublicationStatus.FAILED
            ]
            
            if successful_platforms and not failed_platforms:
                publication.status = PublicationStatus.PUBLISHED
                logger.info(f"Publication {publication_id} completed successfully")
            elif failed_platforms and not successful_platforms:
                publication.status = PublicationStatus.FAILED
                logger.error(f"Publication {publication_id} failed completely")
                
                # Retry if under retry limit
                if publication.retry_count < publication.max_retries:
                    await self._schedule_retry(publication)
            else:
                # Partial success
                publication.status = PublicationStatus.PUBLISHED
                logger.warning(f"Publication {publication_id} partially successful: {len(successful_platforms)}/{len(publication.platforms)}")
            
            # Move to history
            self.publication_history.append(publication)
            
            # Clean up scheduled job
            if publication_id in self.scheduled_publications:
                del self.scheduled_publications[publication_id]
        
        except Exception as e:
            logger.error(f"Publication execution failed: {str(e)}")
            
            # Update publication status
            if publication_id in self.scheduled_publications:
                publication = self.scheduled_publications[publication_id]
                publication.status = PublicationStatus.FAILED
                publication.updated_at = datetime.now()
                
                # Try to retry
                if publication.retry_count < publication.max_retries:
                    await self._schedule_retry(publication)
    
    async def _schedule_retry(self, publication: ScheduledPublication):
        """Schedule a retry for failed publication"""
        try:
            publication.retry_count += 1
            publication.status = PublicationStatus.SCHEDULED
            
            # Calculate retry delay (exponential backoff)
            delay_minutes = 5 * (2 ** (publication.retry_count - 1))  # 5, 10, 20 minutes
            retry_time = datetime.now() + timedelta(minutes=delay_minutes)
            
            publication.scheduled_time = retry_time
            
            # Schedule retry
            self.scheduler.add_job(
                self._execute_publication,
                trigger=DateTrigger(run_date=retry_time),
                args=[publication.id],
                id=f"{publication.id}_retry_{publication.retry_count}",
                misfire_grace_time=300
            )
            
            logger.info(f"Retry {publication.retry_count} scheduled for publication {publication.id} at {retry_time}")
        
        except Exception as e:
            logger.error(f"Retry scheduling failed: {str(e)}")
    
    async def cancel_publication(self, publication_id: str) -> bool:
        """Cancel a scheduled publication"""
        try:
            publication = self.scheduled_publications.get(publication_id)
            if not publication:
                return False
            
            # Remove from scheduler
            try:
                self.scheduler.remove_job(publication_id)
            except:
                pass  # Job might not exist or already executed
            
            # Update status
            publication.status = PublicationStatus.CANCELLED
            publication.updated_at = datetime.now()
            
            # Move to history
            self.publication_history.append(publication)
            del self.scheduled_publications[publication_id]
            
            logger.info(f"Publication {publication_id} cancelled")
            return True
        
        except Exception as e:
            logger.error(f"Publication cancellation failed: {str(e)}")
            return False
    
    async def reschedule_publication(
        self,
        publication_id: str,
        new_time: datetime,
        new_strategy: Optional[ScheduleStrategy] = None
    ) -> bool:
        """Reschedule an existing publication"""
        try:
            publication = self.scheduled_publications.get(publication_id)
            if not publication:
                return False
            
            # Remove existing job
            try:
                self.scheduler.remove_job(publication_id)
            except:
                pass
            
            # Update publication
            publication.scheduled_time = new_time
            if new_strategy:
                publication.strategy = new_strategy
            publication.status = PublicationStatus.RESCHEDULED
            publication.updated_at = datetime.now()
            
            # Schedule new job
            self.scheduler.add_job(
                self._execute_publication,
                trigger=DateTrigger(run_date=new_time),
                args=[publication_id],
                id=publication_id,
                misfire_grace_time=300
            )
            
            logger.info(f"Publication {publication_id} rescheduled to {new_time}")
            return True
        
        except Exception as e:
            logger.error(f"Publication rescheduling failed: {str(e)}")
            return False
    
    async def get_publication_status(self, publication_id: str) -> Optional[ScheduledPublication]:
        """Get status of a scheduled publication"""
        # Check active publications
        if publication_id in self.scheduled_publications:
            return self.scheduled_publications[publication_id]
        
        # Check history
        for pub in self.publication_history:
            if pub.id == publication_id:
                return pub
        
        return None
    
    async def get_user_publications(
        self,
        user_id: str,
        status_filter: Optional[PublicationStatus] = None
    ) -> List[ScheduledPublication]:
        """Get all publications for a user"""
        publications = []
        
        # Active publications
        for pub in self.scheduled_publications.values():
            if pub.user_id == user_id:
                if not status_filter or pub.status == status_filter:
                    publications.append(pub)
        
        # Historical publications
        for pub in self.publication_history:
            if pub.user_id == user_id:
                if not status_filter or pub.status == status_filter:
                    publications.append(pub)
        
        # Sort by creation time
        publications.sort(key=lambda x: x.created_at, reverse=True)
        return publications
    
    async def _get_audience_insights(
        self,
        user_id: str,
        platforms: List[SocialPlatform]
    ) -> List[AudienceInsight]:
        """Get audience insights for platforms"""
        try:
            insights = []
            
            # Get cached insights
            cached_insights = self.audience_insights.get(user_id, [])
            
            for platform in platforms:
                # Look for existing insights
                platform_insights = [
                    i for i in cached_insights 
                    if i.platform == platform
                ]
                
                if platform_insights:
                    insights.extend(platform_insights)
                else:
                    # Generate default insights based on platform
                    default_insight = await self._generate_default_insight(platform)
                    insights.append(default_insight)
            
            return insights
        
        except Exception as e:
            logger.error(f"Audience insights retrieval failed: {str(e)}")
            return []
    
    async def _generate_default_insight(self, platform: SocialPlatform) -> AudienceInsight:
        """Generate default audience insight for platform"""
        # Use platform-specific defaults
        config = self.PLATFORM_OPTIMAL_TIMES.get(platform, {})
        
        return AudienceInsight(
            platform=platform,
            timezone="UTC",
            peak_hours=config.get("weekdays", [12, 13, 14, 15, 16]),
            peak_days=config.get("peak_days", [1, 2, 3, 4]),
            engagement_rate=0.1,  # 10% default
            active_users_count=1000
        )
    
    async def _get_user_timezone(self, user_id: str) -> str:
        """Get user's preferred timezone"""
        # In a real implementation, this would query user preferences
        return "UTC"
    
    async def _estimate_competition_level(
        self,
        platform: SocialPlatform,
        time_slot: datetime
    ) -> float:
        """Estimate competition level at given time slot"""
        try:
            # Simplified competition estimation
            hour = time_slot.hour
            day_of_week = time_slot.weekday()
            
            # Higher competition during peak hours
            if platform in [SocialPlatform.INSTAGRAM, SocialPlatform.TIKTOK]:
                if 18 <= hour <= 21:  # Evening peak
                    return 0.8
                elif 12 <= hour <= 14:  # Lunch peak
                    return 0.6
            
            # Business platforms have different patterns
            if platform == SocialPlatform.LINKEDIN:
                if 8 <= hour <= 10 or 17 <= hour <= 18:  # Business hours
                    return 0.7
                if day_of_week >= 5:  # Weekends
                    return 0.2
            
            # Default moderate competition
            return 0.4
        
        except Exception as e:
            logger.error(f"Competition level estimation failed: {str(e)}")
            return 0.5  # Medium competition as fallback
    
    async def get_scheduler_statistics(self) -> Dict[str, Any]:
        """Get scheduler performance statistics"""
        try:
            active_count = len(self.scheduled_publications)
            completed_count = len([p for p in self.publication_history if p.status == PublicationStatus.PUBLISHED])
            failed_count = len([p for p in self.publication_history if p.status == PublicationStatus.FAILED])
            
            # Platform distribution
            platform_stats = defaultdict(int)
            for pub in list(self.scheduled_publications.values()) + self.publication_history:
                for platform in pub.platforms:
                    platform_stats[platform.value] += 1
            
            # Success rate calculation
            total_attempts = completed_count + failed_count
            success_rate = (completed_count / total_attempts) if total_attempts > 0 else 0
            
            return {
                "active_publications": active_count,
                "completed_publications": completed_count,
                "failed_publications": failed_count,
                "success_rate": success_rate,
                "platform_distribution": dict(platform_stats),
                "scheduler_running": self.scheduler.running,
                "next_job_time": self._get_next_job_time()
            }
        
        except Exception as e:
            logger.error(f"Statistics generation failed: {str(e)}")
            return {}
    
    def _get_next_job_time(self) -> Optional[str]:
        """Get next scheduled job time"""
        try:
            jobs = self.scheduler.get_jobs()
            if jobs:
                next_job = min(jobs, key=lambda x: x.next_run_time)
                return next_job.next_run_time.isoformat() if next_job.next_run_time else None
            return None
        except Exception:
            return None
    
    async def shutdown(self):
        """Shutdown the scheduler gracefully"""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("Publication scheduler shutdown completed")
        except Exception as e:
            logger.error(f"Scheduler shutdown failed: {str(e)}")