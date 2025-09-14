"""
Bulk Scheduler
=============

Advanced bulk content scheduling engine for Ainflue Distribution Platform.
Handles mass content scheduling with intelligent distribution and optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import csv
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import random

logger = logging.getLogger(__name__)

class BulkSchedulingStrategy(Enum):
    """Bulk scheduling strategies"""
    EVEN_DISTRIBUTION = "even_distribution"
    OPTIMAL_TIMES = "optimal_times"
    ENGAGEMENT_BASED = "engagement_based"
    SEASONAL_ADJUSTED = "seasonal_adjusted"
    CUSTOM_PATTERN = "custom_pattern"

class ContentPriority(Enum):
    """Content priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class SchedulingStatus(Enum):
    """Scheduling status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BulkContent:
    """Individual content item for bulk scheduling"""
    content_id: str
    title: str
    content: str
    platforms: List[str]
    priority: int = 2
    preferred_time: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    media_files: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchedulingSlot:
    """Time slot for content scheduling"""
    datetime: datetime
    platform: str
    content_id: Optional[str] = None
    is_optimal: bool = False
    engagement_score: float = 1.0
    competition_score: float = 1.0

@dataclass
class BulkSchedulingResult:
    """Result of bulk scheduling operation"""
    total_content: int
    successfully_scheduled: int
    failed_to_schedule: int
    scheduling_conflicts: int
    optimization_applied: bool
    schedule_summary: Dict[str, Any]
    failed_items: List[Dict[str, Any]]
    recommendations: List[str]

class BulkScheduler:
    """
    Advanced Bulk Content Scheduler
    
    Provides intelligent bulk scheduling with:
    - Multiple scheduling strategies
    - Platform-specific optimization
    - Conflict resolution
    - Load balancing across time periods
    - Analytics and reporting
    """
    
    def __init__(self, default_timezone -> None: str = "UTC") -> None:
        """
        Initialize bulk scheduler
        
        Args:
            default_timezone: Default timezone for scheduling
        """
        self.default_timezone = default_timezone
        self.scheduled_content: Dict[str, List[SchedulingSlot]] = {}
        self.optimal_times: Dict[str, List[str]] = self._load_optimal_times()
        self.platform_limits: Dict[str, Dict] = self._load_platform_limits()
        self.scheduling_rules: Dict[str, Any] = self._load_scheduling_rules()
        
    def _load_optimal_times(self) -> Dict[str, List[str]]:
        """Load optimal posting times by platform"""
        return {
            "instagram": ["09:00", "11:00", "14:00", "17:00", "19:00"],
            "facebook": ["09:00", "13:00", "15:00", "18:00", "20:00"],
            "twitter": ["08:00", "12:00", "17:00", "19:00", "21:00"],
            "linkedin": ["07:30", "08:00", "12:00", "17:00", "18:00"],
            "tiktok": ["06:00", "10:00", "14:00", "19:00", "22:00"],
            "youtube": ["14:00", "15:00", "16:00", "17:00", "18:00"],
            "pinterest": ["08:00", "11:00", "14:00", "20:00", "22:00"],
            "reddit": ["07:00", "09:00", "12:00", "18:00", "20:00"]
        }
    
    def _load_platform_limits(self) -> Dict[str, Dict]:
        """Load platform posting limits and constraints"""
        return {
            "instagram": {
                "max_posts_per_day": 10,
                "min_interval_minutes": 30,
                "optimal_frequency": "3-5 posts/day",
                "peak_days": ["tue", "wed", "thu", "fri"]
            },
            "facebook": {
                "max_posts_per_day": 15,
                "min_interval_minutes": 15,
                "optimal_frequency": "1-2 posts/day",
                "peak_days": ["tue", "wed", "thu", "sun"]
            },
            "twitter": {
                "max_posts_per_day": 50,
                "min_interval_minutes": 5,
                "optimal_frequency": "5-15 tweets/day",
                "peak_days": ["mon", "tue", "wed", "thu", "fri"]
            },
            "linkedin": {
                "max_posts_per_day": 5,
                "min_interval_minutes": 60,
                "optimal_frequency": "1 post/day",
                "peak_days": ["tue", "wed", "thu"]
            },
            "tiktok": {
                "max_posts_per_day": 8,
                "min_interval_minutes": 60,
                "optimal_frequency": "1-3 posts/day",
                "peak_days": ["tue", "wed", "thu", "fri", "sat"]
            },
            "youtube": {
                "max_posts_per_day": 3,
                "min_interval_minutes": 120,
                "optimal_frequency": "3-7 posts/week",
                "peak_days": ["wed", "thu", "fri", "sat", "sun"]
            }
        }
    
    def _load_scheduling_rules(self) -> Dict[str, Any]:
        """Load scheduling rules and constraints"""
        return {
            "global_rules": {
                "no_posting_hours": ["02:00", "03:00", "04:00", "05:00"],
                "peak_engagement_hours": ["09:00", "12:00", "17:00", "19:00"],
                "weekend_adjustment": 0.8,
                "holiday_adjustment": 1.2
            },
            "priority_rules": {
                "critical": {"max_delay_hours": 1, "override_optimal_times": True},
                "urgent": {"max_delay_hours": 6, "override_optimal_times": False},
                "high": {"max_delay_hours": 24, "override_optimal_times": False},
                "normal": {"max_delay_hours": 72, "override_optimal_times": False},
                "low": {"max_delay_hours": 168, "override_optimal_times": False}
            }
        }
    
    async def schedule_bulk_content(self, content_list: List[BulkContent], 
                                   strategy: str = "optimal_times",
                                   start_date: datetime = None,
                                   end_date: datetime = None,
                                   dry_run: bool = False) -> BulkSchedulingResult:
        """
        Schedule bulk content using specified strategy
        
        Args:
            content_list: List of content to schedule
            strategy: Scheduling strategy to use
            start_date: Earliest scheduling date
            end_date: Latest scheduling date
            dry_run: If True, don't actually schedule, just simulate
            
        Returns:
            BulkSchedulingResult: Scheduling results
        """
        try:
            if start_date is None:
                start_date = datetime.now() + timedelta(hours=1)
            
            if end_date is None:
                end_date = start_date + timedelta(days=30)
            
            logger.info(f"Starting bulk scheduling of {len(content_list)} items using {strategy}")
            
            # Validate content
            validated_content = await self._validate_content_list(content_list)
            
            # Generate time slots
            available_slots = await self._generate_time_slots(start_date, end_date, strategy)
            
            # Schedule content to slots
            scheduling_result = await self._assign_content_to_slots(
                validated_content, available_slots, strategy
            )
            
            # Apply optimizations
            optimized_result = await self._optimize_schedule(scheduling_result, strategy)
            
            # Execute scheduling if not dry run
            if not dry_run:
                execution_result = await self._execute_bulk_schedule(optimized_result)
            else:
                execution_result = optimized_result
                logger.info("Dry run completed - no content actually scheduled")
            
            # Generate result summary
            result = self._generate_scheduling_result(
                content_list, execution_result, strategy
            )
            
            logger.info(f"Bulk scheduling completed: {result.successfully_scheduled}/{result.total_content} scheduled")
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk scheduling: {str(e)}")
            raise
    
    async def _validate_content_list(self, content_list: List[BulkContent]) -> List[BulkContent]:
        """Validate and clean content list"""
        validated = []
        
        for content in content_list:
            # Check required fields
            if not content.content_id or not content.title or not content.platforms:
                logger.warning(f"Skipping invalid content: {content.content_id}")
                continue
            
            # Validate platforms
            valid_platforms = [p for p in content.platforms if p in self.platform_limits]
            if not valid_platforms:
                logger.warning(f"No valid platforms for content: {content.content_id}")
                continue
            
            content.platforms = valid_platforms
            validated.append(content)
        
        logger.info(f"Validated {len(validated)}/{len(content_list)} content items")
        return validated
    
    async def _generate_time_slots(self, start_date: datetime, end_date: datetime, 
                                 strategy: str) -> Dict[str, List[SchedulingSlot]]:
        """Generate available time slots for each platform"""
        slots = {}
        
        for platform in self.platform_limits.keys():
            platform_slots = []
            current_date = start_date
            
            while current_date <= end_date:
                daily_slots = await self._generate_daily_slots(platform, current_date, strategy)
                platform_slots.extend(daily_slots)
                current_date += timedelta(days=1)
            
            slots[platform] = platform_slots
        
        return slots
    
    async def _generate_daily_slots(self, platform: str, date: datetime, 
                                  strategy: str) -> List[SchedulingSlot]:
        """Generate time slots for a specific platform and date"""
        slots = []
        platform_config = self.platform_limits[platform]
        max_posts = platform_config["max_posts_per_day"]
        min_interval = platform_config["min_interval_minutes"]
        
        if strategy == "even_distribution":
            # Distribute evenly throughout the day
            hours_range = 16  # 6 AM to 10 PM
            interval_hours = hours_range / max_posts
            
            for i in range(max_posts):
                hour = 6 + (i * interval_hours)
                slot_time = date.replace(hour=int(hour), minute=int((hour % 1) * 60), 
                                       second=0, microsecond=0)
                
                slot = SchedulingSlot(
                    datetime=slot_time,
                    platform=platform,
                    engagement_score=self._calculate_engagement_score(slot_time, platform)
                )
                slots.append(slot)
        
        elif strategy == "optimal_times":
            # Use predefined optimal times
            optimal_times = self.optimal_times.get(platform, ["09:00", "14:00", "19:00"])
            
            for time_str in optimal_times[:max_posts]:
                hour, minute = map(int, time_str.split(':'))
                slot_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                slot = SchedulingSlot(
                    datetime=slot_time,
                    platform=platform,
                    is_optimal=True,
                    engagement_score=self._calculate_engagement_score(slot_time, platform) * 1.2
                )
                slots.append(slot)
        
        elif strategy == "engagement_based":
            # Generate slots based on historical engagement data
            slots = await self._generate_engagement_based_slots(platform, date, max_posts)
        
        # Ensure minimum intervals
        slots = self._enforce_minimum_intervals(slots, min_interval)
        
        return slots
    
    def _calculate_engagement_score(self, slot_time: datetime, platform: str) -> float:
        """Calculate engagement score for a time slot"""
        base_score = 1.0
        
        # Time of day adjustment
        hour = slot_time.hour
        if 9 <= hour <= 11 or 14 <= hour <= 16 or 19 <= hour <= 21:
            base_score *= 1.2
        elif 6 <= hour <= 8 or 12 <= hour <= 13 or 17 <= hour <= 18:
            base_score *= 1.1
        elif hour < 6 or hour > 23:
            base_score *= 0.5
        
        # Day of week adjustment
        day_of_week = slot_time.strftime('%a').lower()
        platform_config = self.platform_limits.get(platform, {})
        peak_days = platform_config.get("peak_days", [])
        
        if day_of_week in peak_days:
            base_score *= 1.15
        elif day_of_week in ["sat", "sun"]:
            base_score *= self.scheduling_rules["global_rules"]["weekend_adjustment"]
        
        return base_score
    
    async def _generate_engagement_based_slots(self, platform: str, date: datetime, 
                                             max_posts: int) -> List[SchedulingSlot]:
        """Generate slots based on engagement patterns"""
        slots = []
        
        # Simulate engagement-based timing (in real implementation, use historical data)
        high_engagement_hours = [9, 12, 17, 19, 21]
        medium_engagement_hours = [8, 11, 14, 16, 20]
        
        # Prioritize high engagement hours
        selected_hours = high_engagement_hours[:max_posts]
        if len(selected_hours) < max_posts:
            selected_hours.extend(medium_engagement_hours[:max_posts - len(selected_hours)])
        
        for hour in selected_hours:
            # Add some randomness to minutes
            minute = random.choice([0, 15, 30, 45])
            slot_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            slot = SchedulingSlot(
                datetime=slot_time,
                platform=platform,
                engagement_score=self._calculate_engagement_score(slot_time, platform)
            )
            slots.append(slot)
        
        return sorted(slots, key=lambda s: s.datetime)
    
    def _enforce_minimum_intervals(self, slots: List[SchedulingSlot], 
                                 min_interval_minutes: int) -> List[SchedulingSlot]:
        """Ensure minimum intervals between posts"""
        if not slots:
            return slots
        
        sorted_slots = sorted(slots, key=lambda s: s.datetime)
        filtered_slots = [sorted_slots[0]]
        
        for slot in sorted_slots[1:]:
            last_slot_time = filtered_slots[-1].datetime
            time_diff = (slot.datetime - last_slot_time).total_seconds() / 60
            
            if time_diff >= min_interval_minutes:
                filtered_slots.append(slot)
            else:
                # Adjust time to meet minimum interval
                adjusted_time = last_slot_time + timedelta(minutes=min_interval_minutes)
                slot.datetime = adjusted_time
                filtered_slots.append(slot)
        
        return filtered_slots
    
    async def _assign_content_to_slots(self, content_list: List[BulkContent], 
                                     available_slots: Dict[str, List[SchedulingSlot]], 
                                     strategy: str) -> Dict[str, List[SchedulingSlot]]:
        """Assign content to available time slots"""
        scheduled_slots = {platform: [] for platform in available_slots.keys()}
        
        # Sort content by priority
        sorted_content = sorted(content_list, key=lambda c: c.priority, reverse=True)
        
        for content in sorted_content:
            for platform in content.platforms:
                if platform not in available_slots:
                    continue
                
                # Find best slot for this content on this platform
                best_slot = await self._find_best_slot(
                    content, platform, available_slots[platform], strategy
                )
                
                if best_slot:
                    best_slot.content_id = content.content_id
                    scheduled_slots[platform].append(best_slot)
                    available_slots[platform].remove(best_slot)
        
        return scheduled_slots
    
    async def _find_best_slot(self, content: BulkContent, platform: str, 
                            available_slots: List[SchedulingSlot], 
                            strategy: str) -> Optional[SchedulingSlot]:
        """Find the best available slot for content"""
        if not available_slots:
            return None
        
        # Filter slots based on content preferences
        suitable_slots = []
        
        for slot in available_slots:
            # Check preferred time if specified
            if content.preferred_time:
                time_diff = abs((slot.datetime - content.preferred_time).total_seconds())
                if time_diff > 86400:  # More than 24 hours difference
                    continue
            
            # Check constraints
            if content.constraints:
                if not self._check_slot_constraints(slot, content.constraints):
                    continue
            
            suitable_slots.append(slot)
        
        if not suitable_slots:
            return available_slots[0] if available_slots else None
        
        # Select best slot based on strategy
        if strategy == "optimal_times":
            # Prefer optimal time slots
            optimal_slots = [s for s in suitable_slots if s.is_optimal]
            if optimal_slots:
                return max(optimal_slots, key=lambda s: s.engagement_score)
        
        elif strategy == "engagement_based":
            # Choose highest engagement score
            return max(suitable_slots, key=lambda s: s.engagement_score)
        
        # Default: return first suitable slot
        return suitable_slots[0]
    
    def _check_slot_constraints(self, slot: SchedulingSlot, constraints: Dict[str, Any]) -> bool:
        """Check if slot meets content constraints"""
        # Time range constraints
        if "earliest_time" in constraints:
            earliest = datetime.fromisoformat(constraints["earliest_time"])
            if slot.datetime < earliest:
                return False
        
        if "latest_time" in constraints:
            latest = datetime.fromisoformat(constraints["latest_time"])
            if slot.datetime > latest:
                return False
        
        # Day of week constraints
        if "allowed_days" in constraints:
            day_name = slot.datetime.strftime('%A').lower()
            if day_name not in constraints["allowed_days"]:
                return False
        
        # Hour constraints
        if "allowed_hours" in constraints:
            if slot.datetime.hour not in constraints["allowed_hours"]:
                return False
        
        return True
    
    async def _optimize_schedule(self, scheduled_slots: Dict[str, List[SchedulingSlot]], 
                               strategy: str) -> Dict[str, List[SchedulingSlot]]:
        """Optimize the scheduled content"""
        optimized_slots = {}
        
        for platform, slots in scheduled_slots.items():
            if not slots:
                optimized_slots[platform] = []
                continue
            
            # Sort by datetime
            sorted_slots = sorted(slots, key=lambda s: s.datetime)
            
            # Apply platform-specific optimizations
            platform_optimized = await self._apply_platform_optimizations(
                platform, sorted_slots
            )
            
            optimized_slots[platform] = platform_optimized
        
        return optimized_slots
    
    async def _apply_platform_optimizations(self, platform: str, 
                                          slots: List[SchedulingSlot]) -> List[SchedulingSlot]:
        """Apply platform-specific optimizations"""
        platform_config = self.platform_limits.get(platform, {})
        min_interval = platform_config.get("min_interval_minutes", 60)
        
        # Ensure minimum intervals
        optimized_slots = []
        last_slot_time = None
        
        for slot in slots:
            if last_slot_time:
                time_diff = (slot.datetime - last_slot_time).total_seconds() / 60
                if time_diff < min_interval:
                    # Adjust time
                    adjusted_time = last_slot_time + timedelta(minutes=min_interval)
                    slot.datetime = adjusted_time
            
            optimized_slots.append(slot)
            last_slot_time = slot.datetime
        
        return optimized_slots
    
    async def _execute_bulk_schedule(self, scheduled_slots: Dict[str, List[SchedulingSlot]]) -> Dict[str, List[SchedulingSlot]]:
        """Execute the bulk scheduling (placeholder for actual implementation)"""
        # In real implementation, this would interface with the actual scheduling system
        logger.info("Executing bulk schedule...")
        
        # Simulate execution with some failures
        executed_slots = {}
        
        for platform, slots in scheduled_slots.items():
            executed_platform_slots = []
            
            for slot in slots:
                # Simulate 95% success rate
                if random.random() < 0.95:
                    executed_platform_slots.append(slot)
                else:
                    logger.warning(f"Failed to schedule content {slot.content_id} on {platform}")
            
            executed_slots[platform] = executed_platform_slots
        
        return executed_slots
    
    def _generate_scheduling_result(self, original_content: List[BulkContent], 
                                  executed_slots: Dict[str, List[SchedulingSlot]], 
                                  strategy: str) -> BulkSchedulingResult:
        """Generate comprehensive scheduling result"""
        total_content = len(original_content)
        total_scheduled_slots = sum(len(slots) for slots in executed_slots.values())
        
        # Calculate success metrics
        content_ids_scheduled = set()
        for slots in executed_slots.values():
            content_ids_scheduled.update(slot.content_id for slot in slots if slot.content_id)
        
        successfully_scheduled = len(content_ids_scheduled)
        failed_to_schedule = total_content - successfully_scheduled
        
        # Generate summary
        schedule_summary = {
            "platforms": list(executed_slots.keys()),
            "total_slots": total_scheduled_slots,
            "earliest_post": min(
                (slot.datetime for slots in executed_slots.values() for slot in slots),
                default=None
            ),
            "latest_post": max(
                (slot.datetime for slots in executed_slots.values() for slot in slots),
                default=None
            ),
            "strategy_used": strategy,
            "platform_distribution": {
                platform: len(slots) for platform, slots in executed_slots.items()
            }
        }
        
        # Find failed items
        scheduled_content_ids = content_ids_scheduled
        failed_items = [
            {
                "content_id": content.content_id,
                "title": content.title,
                "reason": "No suitable time slots available"
            }
            for content in original_content
            if content.content_id not in scheduled_content_ids
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(executed_slots, failed_items)
        
        return BulkSchedulingResult(
            total_content=total_content,
            successfully_scheduled=successfully_scheduled,
            failed_to_schedule=failed_to_schedule,
            scheduling_conflicts=0,  # Would be calculated based on actual conflicts
            optimization_applied=True,
            schedule_summary=schedule_summary,
            failed_items=failed_items,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, executed_slots: Dict[str, List[SchedulingSlot]], 
                                failed_items: List[Dict]) -> List[str]:
        """Generate recommendations based on scheduling results"""
        recommendations = []
        
        if failed_items:
            recommendations.append(f"Consider expanding time range for {len(failed_items)} failed items")
        
        # Platform distribution analysis
        platform_counts = {p: len(slots) for p, slots in executed_slots.items()}
        if platform_counts:
            max_platform = max(platform_counts, key=platform_counts.get)
            min_platform = min(platform_counts, key=platform_counts.get)
            
            if platform_counts[max_platform] > platform_counts[min_platform] * 2:
                recommendations.append(
                    f"Consider redistributing content - {max_platform} has significantly more posts"
                )
        
        recommendations.extend([
            "Monitor scheduled content performance for optimization",
            "Consider A/B testing different time slots",
            "Review platform-specific engagement patterns regularly"
        ])
        
        return recommendations
    
    async def import_from_csv(self, csv_file_path: str) -> List[BulkContent]:
        """Import content from CSV file"""
        content_list = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    content = BulkContent(
                        content_id=row.get('content_id', f"auto_{len(content_list)}"),
                        title=row.get('title', ''),
                        content=row.get('content', ''),
                        platforms=row.get('platforms', '').split(','),
                        priority=int(row.get('priority', 2)),
                        preferred_time=datetime.fromisoformat(row['preferred_time']) 
                                     if row.get('preferred_time') else None,
                        tags=row.get('tags', '').split(',') if row.get('tags') else [],
                        media_files=row.get('media_files', '').split(',') if row.get('media_files') else []
                    )
                    content_list.append(content)
            
            logger.info(f"Imported {len(content_list)} content items from CSV")
            return content_list
            
        except Exception as e:
            logger.error(f"Error importing from CSV: {str(e)}")
            raise
    
    async def export_schedule_to_csv(self, scheduled_slots -> None: Dict[str, List[SchedulingSlot]], 
                                   output_path -> None: str) -> None:
        """Export scheduled content to CSV"""
        try:
            rows = []
            
            for platform, slots in scheduled_slots.items():
                for slot in slots:
                    rows.append({
                        'platform': platform,
                        'content_id': slot.content_id,
                        'scheduled_time': slot.datetime.isoformat(),
                        'is_optimal': slot.is_optimal,
                        'engagement_score': slot.engagement_score
                    })
            
            with open(output_path, 'w', newline='', encoding='utf-8') as file:
                if rows:
                    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
            
            logger.info(f"Exported schedule to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise

# Usage example
async def main() -> None:
    """Example usage of BulkScheduler"""
    scheduler = BulkScheduler()
    
    # Create sample content
    content_list = [
        BulkContent(
            content_id="post_001",
            title="Sample Post 1",
            content="This is a sample post content",
            platforms=["instagram", "facebook", "twitter"],
            priority=3,
            tags=["sample", "test"]
        ),
        BulkContent(
            content_id="post_002",
            title="Sample Post 2",
            content="Another sample post",
            platforms=["linkedin", "twitter"],
            priority=2,
            preferred_time=datetime.now() + timedelta(days=1)
        )
    ]
    
    # Schedule content
    result = await scheduler.schedule_bulk_content(
        content_list=content_list,
        strategy="optimal_times",
        start_date=datetime.now() + timedelta(hours=1),
        end_date=datetime.now() + timedelta(days=7),
        dry_run=True
    )
    
    print(f"Scheduling completed:")
    print(f"Total content: {result.total_content}")
    print(f"Successfully scheduled: {result.successfully_scheduled}")
    print(f"Failed to schedule: {result.failed_to_schedule}")
    print(f"Recommendations: {result.recommendations}")

if __name__ == "__main__":
    asyncio.run(main())