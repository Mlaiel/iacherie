"""
Timezone-Aware Scheduler
======================

Advanced timezone-aware publication scheduler for Ainflue Distribution Platform.
Handles multi-timezone content scheduling with intelligent optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import pytz
from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class TimezoneStrategy(Enum):
    """Timezone scheduling strategies"""
    AUDIENCE_OPTIMAL = "audience_optimal"  # Schedule based on audience timezone
    GLOBAL_PEAK = "global_peak"  # Schedule at global peak times
    ROLLING_WAVE = "rolling_wave"  # Schedule in waves across timezones
    CUSTOM_TIMES = "custom_times"  # Custom scheduling per timezone
    UNIFIED = "unified"  # Single time for all timezones

class ContentType(Enum):
    """Content type for timezone optimization"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LIVE = "live"
    STORY = "story"

@dataclass
class TimezoneAudience:
    """Audience data for a specific timezone"""
    timezone: str
    active_hours: List[int] = field(default_factory=lambda: list(range(8, 22)))  # 8 AM to 10 PM
    peak_hours: List[int] = field(default_factory=lambda: [12, 18, 20])  # Noon, 6 PM, 8 PM
    audience_size: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    preferred_content_types: List[ContentType] = field(default_factory=list)
    cultural_considerations: Dict[str, Any] = field(default_factory=dict)
    
    def get_optimal_times(self, content_type: ContentType) -> List[int]:
        """Get optimal posting times for content type"""
        if content_type in self.preferred_content_types:
            return self.peak_hours
        return self.active_hours

@dataclass
class ScheduleRequest:
    """Request for timezone-aware scheduling"""
    content_id: str
    content_type: ContentType
    platforms: List[str]
    strategy: TimezoneStrategy = TimezoneStrategy.AUDIENCE_OPTIMAL
    preferred_time: Optional[datetime] = None
    target_timezones: Optional[List[str]] = None
    priority: int = 1  # 1-10, higher is more priority
    flexibility_hours: int = 2  # How many hours flexibility for optimization
    exclude_weekends: bool = False
    exclude_holidays: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScheduledItem:
    """Scheduled publication item"""
    schedule_id: str
    content_id: str
    platform: str
    timezone: str
    scheduled_time: datetime
    local_time: str
    optimal_score: float
    audience_size: int
    expected_engagement: float
    status: str = "scheduled"  # scheduled, published, failed, cancelled
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class TimezoneAwareScheduler:
    """
    Advanced timezone-aware scheduler with intelligent optimization
    
    Features:
    - Multi-timezone audience analysis
    - Optimal timing predictions
    - Cultural consideration integration
    - Rolling wave scheduling
    - Peak time optimization
    - Holiday and weekend handling
    """
    
    # Global peak times by content type (UTC hours)
    GLOBAL_PEAK_TIMES = {
        ContentType.TEXT: [12, 15, 18, 21],  # Text content peaks
        ContentType.IMAGE: [11, 14, 17, 20],  # Image content peaks
        ContentType.VIDEO: [19, 20, 21, 22],  # Video content peaks
        ContentType.AUDIO: [7, 12, 17, 22],  # Audio content peaks
        ContentType.LIVE: [19, 20, 21],  # Live content peaks
        ContentType.STORY: [9, 12, 18, 21]  # Story content peaks
    }
    
    # Major timezone groups for rolling wave strategy
    TIMEZONE_WAVES = [
        ["Pacific/Auckland", "Australia/Sydney"],  # Wave 1: Oceania
        ["Asia/Tokyo", "Asia/Shanghai", "Asia/Singapore"],  # Wave 2: East Asia
        ["Asia/Kolkata", "Asia/Dubai"],  # Wave 3: South/West Asia
        ["Europe/London", "Europe/Paris", "Europe/Berlin"],  # Wave 4: Europe
        ["America/New_York", "America/Toronto"],  # Wave 5: East America
        ["America/Chicago", "America/Mexico_City"],  # Wave 6: Central America
        ["America/Los_Angeles", "America/Vancouver"]  # Wave 7: West America
    ]
    
    def __init__(self) -> None:
        self.audience_data: Dict[str, TimezoneAudience] = {}
        self.scheduled_items: List[ScheduledItem] = []
        self.platform_constraints: Dict[str, Dict[str, Any]] = {}
        self._schedule_lock = asyncio.Lock()
        
    async def add_audience_data(self, timezone_data -> None: List[TimezoneAudience]) -> None:
        """Add audience data for multiple timezones"""
        for audience in timezone_data:
            self.audience_data[audience.timezone] = audience
            
        logger.info(f"Added audience data for {len(timezone_data)} timezones")
        
    async def set_platform_constraints(self, platform -> None: str, constraints -> None: Dict[str, Any]) -> None:
        """Set scheduling constraints for a platform"""
        self.platform_constraints[platform] = constraints
        logger.info(f"Set constraints for platform: {platform}")
        
    async def schedule_content(self, request: ScheduleRequest) -> List[ScheduledItem]:
        """
        Schedule content across timezones using specified strategy
        
        Args:
            request: ScheduleRequest with content and scheduling preferences
            
        Returns:
            List of ScheduledItem objects with optimal scheduling times
        """
        async with self._schedule_lock:
            try:
                logger.info(f"Scheduling content {request.content_id} with strategy {request.strategy.value}")
                
                scheduled_items = []
                
                if request.strategy == TimezoneStrategy.AUDIENCE_OPTIMAL:
                    scheduled_items = await self._schedule_audience_optimal(request)
                elif request.strategy == TimezoneStrategy.GLOBAL_PEAK:
                    scheduled_items = await self._schedule_global_peak(request)
                elif request.strategy == TimezoneStrategy.ROLLING_WAVE:
                    scheduled_items = await self._schedule_rolling_wave(request)
                elif request.strategy == TimezoneStrategy.CUSTOM_TIMES:
                    scheduled_items = await self._schedule_custom_times(request)
                elif request.strategy == TimezoneStrategy.UNIFIED:
                    scheduled_items = await self._schedule_unified(request)
                    
                # Apply platform constraints and validate
                validated_items = await self._validate_and_adjust_schedule(scheduled_items)
                
                # Store scheduled items
                self.scheduled_items.extend(validated_items)
                
                logger.info(f"Scheduled {len(validated_items)} items for content {request.content_id}")
                return validated_items
                
            except Exception as e:
                logger.error(f"Failed to schedule content {request.content_id}: {e}")
                return []
                
    async def _schedule_audience_optimal(self, request: ScheduleRequest) -> List[ScheduledItem]:
        """Schedule based on optimal times for each timezone audience"""
        scheduled_items = []
        
        target_timezones = request.target_timezones or list(self.audience_data.keys())
        
        for tz_name in target_timezones:
            if tz_name not in self.audience_data:
                continue
                
            audience = self.audience_data[tz_name]
            optimal_hours = audience.get_optimal_times(request.content_type)
            
            for platform in request.platforms:
                # Find best time within optimal hours
                best_time = await self._find_best_time_in_timezone(
                    tz_name, optimal_hours, request
                )
                
                if best_time:
                    item = ScheduledItem(
                        schedule_id=f"{request.content_id}_{platform}_{tz_name}",
                        content_id=request.content_id,
                        platform=platform,
                        timezone=tz_name,
                        scheduled_time=best_time,
                        local_time=self._format_local_time(best_time, tz_name),
                        optimal_score=await self._calculate_optimal_score(best_time, tz_name, request),
                        audience_size=audience.audience_size,
                        expected_engagement=audience.engagement_rate
                    )
                    scheduled_items.append(item)
                    
        return scheduled_items
        
    async def _schedule_global_peak(self, request: ScheduleRequest) -> List[ScheduledItem]:
        """Schedule at global peak times for content type"""
        scheduled_items = []
        
        peak_hours = self.GLOBAL_PEAK_TIMES.get(request.content_type, [12, 18, 21])
        
        # Use preferred time if provided, otherwise use first peak hour
        if request.preferred_time:
            target_hour = request.preferred_time.hour
        else:
            target_hour = peak_hours[0]
            
        # Create UTC datetime for the target hour
        base_time = datetime.now(timezone.utc).replace(
            hour=target_hour, minute=0, second=0, microsecond=0
        )
        
        # Adjust to next occurrence if time has passed
        if base_time <= datetime.now(timezone.utc):
            base_time += timedelta(days=1)
            
        for platform in request.platforms:
            # Get all relevant timezones or use major ones
            target_timezones = request.target_timezones or list(self.audience_data.keys())
            
            for tz_name in target_timezones[:5]:  # Limit to top 5 timezones
                if tz_name in self.audience_data:
                    audience = self.audience_data[tz_name]
                    
                    item = ScheduledItem(
                        schedule_id=f"{request.content_id}_{platform}_{tz_name}_global",
                        content_id=request.content_id,
                        platform=platform,
                        timezone=tz_name,
                        scheduled_time=base_time,
                        local_time=self._format_local_time(base_time, tz_name),
                        optimal_score=0.8,  # Global peak assumed good
                        audience_size=audience.audience_size,
                        expected_engagement=audience.engagement_rate * 0.9
                    )
                    scheduled_items.append(item)
                    
        return scheduled_items
        
    async def _schedule_rolling_wave(self, request: ScheduleRequest) -> List[ScheduledItem]:
        """Schedule in rolling waves across timezone groups"""
        scheduled_items = []
        
        base_time = request.preferred_time or datetime.now(timezone.utc) + timedelta(hours=1)
        wave_interval = timedelta(hours=3)  # 3 hours between waves
        
        for wave_index, wave_timezones in enumerate(self.TIMEZONE_WAVES):
            wave_time = base_time + (wave_interval * wave_index)
            
            for tz_name in wave_timezones:
                if tz_name in self.audience_data:
                    audience = self.audience_data[tz_name]
                    
                    # Adjust time to be optimal for this timezone
                    tz = pytz.timezone(tz_name)
                    local_time = wave_time.astimezone(tz)
                    
                    # Find nearest optimal hour
                    optimal_hours = audience.get_optimal_times(request.content_type)
                    nearest_hour = min(optimal_hours, key=lambda h: abs(h - local_time.hour))
                    
                    adjusted_time = local_time.replace(hour=nearest_hour, minute=0)
                    final_time = adjusted_time.astimezone(timezone.utc)
                    
                    for platform in request.platforms:
                        item = ScheduledItem(
                            schedule_id=f"{request.content_id}_{platform}_{tz_name}_wave{wave_index}",
                            content_id=request.content_id,
                            platform=platform,
                            timezone=tz_name,
                            scheduled_time=final_time,
                            local_time=self._format_local_time(final_time, tz_name),
                            optimal_score=0.85,  # Rolling wave is well-optimized
                            audience_size=audience.audience_size,
                            expected_engagement=audience.engagement_rate
                        )
                        scheduled_items.append(item)
                        
        return scheduled_items
        
    async def _schedule_custom_times(self, request: ScheduleRequest) -> List[ScheduledItem]:
        """Schedule at custom specified times per timezone"""
        scheduled_items = []
        
        # Custom times should be provided in metadata
        custom_times = request.metadata.get("custom_times", {})
        
        if not custom_times:
            logger.warning("No custom times provided, falling back to audience optimal")
            return await self._schedule_audience_optimal(request)
            
        for tz_name, time_spec in custom_times.items():
            if tz_name not in self.audience_data:
                continue
                
            # Parse time specification
            if isinstance(time_spec, str):
                # Parse "HH:MM" format
                hour, minute = map(int, time_spec.split(":"))
            elif isinstance(time_spec, dict):
                hour = time_spec.get("hour", 12)
                minute = time_spec.get("minute", 0)
            else:
                continue
                
            # Create scheduled time
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            scheduled_local = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Move to next day if time has passed
            if scheduled_local <= now:
                scheduled_local += timedelta(days=1)
                
            scheduled_utc = scheduled_local.astimezone(timezone.utc)
            audience = self.audience_data[tz_name]
            
            for platform in request.platforms:
                item = ScheduledItem(
                    schedule_id=f"{request.content_id}_{platform}_{tz_name}_custom",
                    content_id=request.content_id,
                    platform=platform,
                    timezone=tz_name,
                    scheduled_time=scheduled_utc,
                    local_time=self._format_local_time(scheduled_utc, tz_name),
                    optimal_score=0.7,  # Custom time may not be optimal
                    audience_size=audience.audience_size,
                    expected_engagement=audience.engagement_rate * 0.8
                )
                scheduled_items.append(item)
                
        return scheduled_items
        
    async def _schedule_unified(self, request: ScheduleRequest) -> List[ScheduledItem]:
        """Schedule at the same time across all timezones"""
        scheduled_items = []
        
        # Use preferred time or default to next hour
        unified_time = request.preferred_time or (
            datetime.now(timezone.utc) + timedelta(hours=1)
        ).replace(minute=0, second=0, microsecond=0)
        
        target_timezones = request.target_timezones or list(self.audience_data.keys())
        
        for tz_name in target_timezones:
            if tz_name in self.audience_data:
                audience = self.audience_data[tz_name]
                
                for platform in request.platforms:
                    item = ScheduledItem(
                        schedule_id=f"{request.content_id}_{platform}_{tz_name}_unified",
                        content_id=request.content_id,
                        platform=platform,
                        timezone=tz_name,
                        scheduled_time=unified_time,
                        local_time=self._format_local_time(unified_time, tz_name),
                        optimal_score=0.6,  # Unified may not be optimal for all
                        audience_size=audience.audience_size,
                        expected_engagement=audience.engagement_rate * 0.7
                    )
                    scheduled_items.append(item)
                    
        return scheduled_items
        
    async def _find_best_time_in_timezone(
        self, 
        tz_name: str, 
        optimal_hours: List[int], 
        request: ScheduleRequest
    ) -> Optional[datetime]:
        """Find the best scheduling time within optimal hours for a timezone"""
        try:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            
            # Find next available optimal hour
            for hour in optimal_hours:
                candidate_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                # Move to next day if time has passed
                if candidate_time <= now:
                    candidate_time += timedelta(days=1)
                    
                # Skip weekends if requested
                if request.exclude_weekends and candidate_time.weekday() >= 5:
                    continue
                    
                # Check flexibility window
                if request.preferred_time:
                    time_diff = abs((candidate_time.astimezone(timezone.utc) - request.preferred_time).total_seconds())
                    if time_diff > request.flexibility_hours * 3600:
                        continue
                        
                return candidate_time.astimezone(timezone.utc)
                
            return None
            
        except Exception as e:
            logger.error(f"Error finding best time for timezone {tz_name}: {e}")
            return None
            
    async def _calculate_optimal_score(
        self, 
        scheduled_time: datetime, 
        tz_name: str, 
        request: ScheduleRequest
    ) -> float:
        """Calculate optimization score for a scheduled time"""
        try:
            if tz_name not in self.audience_data:
                return 0.5
                
            audience = self.audience_data[tz_name]
            tz = pytz.timezone(tz_name)
            local_time = scheduled_time.astimezone(tz)
            
            score = 0.0
            
            # Hour optimization (30% weight)
            if local_time.hour in audience.peak_hours:
                score += 0.3
            elif local_time.hour in audience.active_hours:
                score += 0.2
            else:
                score += 0.1
                
            # Content type match (25% weight)
            if request.content_type in audience.preferred_content_types:
                score += 0.25
            else:
                score += 0.15
                
            # Audience size factor (20% weight)
            max_audience = max([a.audience_size for a in self.audience_data.values()], default=1)
            audience_factor = audience.audience_size / max_audience
            score += 0.2 * audience_factor
            
            # Engagement rate (15% weight)
            score += 0.15 * audience.engagement_rate
            
            # Day of week (10% weight)
            weekday = local_time.weekday()
            if weekday < 5:  # Weekday
                score += 0.1
            else:  # Weekend
                score += 0.05
                
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating optimal score: {e}")
            return 0.5
            
    def _format_local_time(self, utc_time: datetime, tz_name: str) -> str:
        """Format UTC time as local time string"""
        try:
            tz = pytz.timezone(tz_name)
            local_time = utc_time.astimezone(tz)
            return local_time.strftime("%Y-%m-%d %H:%M %Z")
        except:
            return utc_time.strftime("%Y-%m-%d %H:%M UTC")
            
    async def _validate_and_adjust_schedule(self, items: List[ScheduledItem]) -> List[ScheduledItem]:
        """Validate scheduled items against platform constraints"""
        validated_items = []
        
        for item in items:
            # Apply platform constraints
            constraints = self.platform_constraints.get(item.platform, {})
            
            # Check minimum interval between posts
            min_interval = constraints.get("min_interval_minutes", 0)
            if min_interval > 0:
                conflicts = [
                    existing for existing in self.scheduled_items
                    if existing.platform == item.platform and
                    abs((existing.scheduled_time - item.scheduled_time).total_seconds()) < min_interval * 60
                ]
                
                if conflicts:
                    # Adjust time to avoid conflict
                    adjustment = timedelta(minutes=min_interval)
                    item.scheduled_time += adjustment
                    item.local_time = self._format_local_time(item.scheduled_time, item.timezone)
                    
            # Check daily post limits
            daily_limit = constraints.get("daily_post_limit")
            if daily_limit:
                same_day_posts = [
                    existing for existing in self.scheduled_items
                    if existing.platform == item.platform and
                    existing.scheduled_time.date() == item.scheduled_time.date()
                ]
                
                if len(same_day_posts) >= daily_limit:
                    # Move to next day
                    item.scheduled_time += timedelta(days=1)
                    item.local_time = self._format_local_time(item.scheduled_time, item.timezone)
                    
            validated_items.append(item)
            
        return validated_items
        
    async def get_scheduled_items(
        self, 
        content_id: Optional[str] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ScheduledItem]:
        """Get scheduled items with optional filtering"""
        items = self.scheduled_items
        
        if content_id:
            items = [item for item in items if item.content_id == content_id]
        if platform:
            items = [item for item in items if item.platform == platform]
        if status:
            items = [item for item in items if item.status == status]
            
        return items
        
    async def update_schedule_status(self, schedule_id: str, status: str) -> bool:
        """Update the status of a scheduled item"""
        for item in self.scheduled_items:
            if item.schedule_id == schedule_id:
                item.status = status
                logger.info(f"Updated schedule {schedule_id} status to {status}")
                return True
                
        return False
        
    async def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancel a scheduled item"""
        return await self.update_schedule_status(schedule_id, "cancelled")
        
    async def get_timezone_coverage_report(self) -> Dict[str, Any]:
        """Generate a report on timezone coverage and optimization"""
        report = {
            "total_timezones": len(self.audience_data),
            "total_audience": sum(a.audience_size for a in self.audience_data.values()),
            "scheduled_items": len(self.scheduled_items),
            "timezone_breakdown": {},
            "platform_breakdown": {},
            "optimization_stats": {
                "average_optimal_score": 0.0,
                "high_score_items": 0,
                "coverage_percentage": 0.0
            }
        }
        
        # Timezone breakdown
        for tz_name, audience in self.audience_data.items():
            tz_items = [item for item in self.scheduled_items if item.timezone == tz_name]
            report["timezone_breakdown"][tz_name] = {
                "audience_size": audience.audience_size,
                "scheduled_items": len(tz_items),
                "average_score": sum(item.optimal_score for item in tz_items) / len(tz_items) if tz_items else 0
            }
            
        # Platform breakdown
        platforms = set(item.platform for item in self.scheduled_items)
        for platform in platforms:
            platform_items = [item for item in self.scheduled_items if item.platform == platform]
            report["platform_breakdown"][platform] = {
                "scheduled_items": len(platform_items),
                "timezones_covered": len(set(item.timezone for item in platform_items)),
                "average_score": sum(item.optimal_score for item in platform_items) / len(platform_items)
            }
            
        # Optimization stats
        if self.scheduled_items:
            scores = [item.optimal_score for item in self.scheduled_items]
            report["optimization_stats"]["average_optimal_score"] = sum(scores) / len(scores)
            report["optimization_stats"]["high_score_items"] = len([s for s in scores if s >= 0.8])
            report["optimization_stats"]["coverage_percentage"] = len(set(item.timezone for item in self.scheduled_items)) / len(self.audience_data) * 100
            
        return report

# Usage example
async def example_usage() -> None:
    """Example usage of TimezoneAwareScheduler"""
    scheduler = TimezoneAwareScheduler()
    
    # Add audience data
    audiences = [
        TimezoneAudience(
            timezone="America/New_York",
            active_hours=list(range(7, 23)),
            peak_hours=[9, 12, 17, 20],
            audience_size=50000,
            engagement_rate=0.08,
            preferred_content_types=[ContentType.TEXT, ContentType.IMAGE]
        ),
        TimezoneAudience(
            timezone="Europe/London",
            active_hours=list(range(8, 24)),
            peak_hours=[11, 15, 19, 21],
            audience_size=35000,
            engagement_rate=0.06,
            preferred_content_types=[ContentType.VIDEO, ContentType.IMAGE]
        ),
        TimezoneAudience(
            timezone="Asia/Tokyo",
            active_hours=list(range(6, 22)),
            peak_hours=[8, 12, 18, 21],
            audience_size=25000,
            engagement_rate=0.10,
            preferred_content_types=[ContentType.IMAGE, ContentType.STORY]
        )
    ]
    
    await scheduler.add_audience_data(audiences)
    
    # Set platform constraints
    await scheduler.set_platform_constraints("instagram", {
        "min_interval_minutes": 30,
        "daily_post_limit": 5
    })
    
    # Schedule content with rolling wave strategy
    request = ScheduleRequest(
        content_id="content_123",
        content_type=ContentType.IMAGE,
        platforms=["instagram", "twitter", "facebook"],
        strategy=TimezoneStrategy.ROLLING_WAVE,
        priority=8,
        flexibility_hours=3
    )
    
    scheduled_items = await scheduler.schedule_content(request)
    
    print(f"Scheduled {len(scheduled_items)} items:")
    for item in scheduled_items:
        print(f"  {item.platform} in {item.timezone}: {item.local_time} (score: {item.optimal_score:.2f})")
        
    # Generate coverage report
    report = await scheduler.get_timezone_coverage_report()
    print(f"\nCoverage Report: {json.dumps(report, indent=2)}")

if __name__ == "__main__":
    asyncio.run(example_usage())