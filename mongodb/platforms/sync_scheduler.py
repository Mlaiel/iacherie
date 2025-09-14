"""
Sync Scheduler - Enterprise Platform Synchronization Scheduling and Rate Limiting

This module provides intelligent scheduling for platform synchronization with
rate limiting, optimal timing, and conflict resolution.

🎯 Expert Roles Applied:
- Lead Dev IA: AI-driven scheduling optimization and intelligent timing
- Backend Senior: Robust scheduling engine with fault tolerance
- ML Engineer: Machine learning for optimal posting times and audience targeting
- DBA: Optimized scheduling data storage and retrieval
- Sécurité: Secure scheduling with compliance and rate limiting
- Microservices: Distributed scheduling architecture
- Audio: Audio content scheduling optimization
- DevOps: Scalable scheduling infrastructure and monitoring
- IA Prompt Engineer: AI-powered schedule optimization and recommendations

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorDatabase
import pytz
from croniter import croniter
import hashlib

from .platform_manager import PlatformType, PlatformManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Schedule types for content synchronization"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    RECURRING = "recurring"
    OPTIMAL_TIME = "optimal_time"
    BATCH = "batch"
    SMART_QUEUE = "smart_queue"


class ScheduleStatus(Enum):
    """Schedule execution status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class Priority(Enum):
    """Schedule priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class TimeWindow:
    """Time window for scheduling"""
    start_hour: int  # 0-23
    end_hour: int    # 0-23
    timezone: str = "UTC"
    days_of_week: Set[int] = None  # 0=Monday, 6=Sunday
    
    def __post_init__(self) -> None:
        if self.days_of_week is None:
            self.days_of_week = {0, 1, 2, 3, 4, 5, 6}  # All days


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    cooldown_seconds: int = 60


@dataclass
class ScheduleRule:
    """Scheduling rule configuration"""
    rule_id: str
    name: str
    platform_type: PlatformType
    schedule_type: ScheduleType
    priority: Priority = Priority.NORMAL
    time_windows: List[TimeWindow] = None
    cron_expression: Optional[str] = None
    max_retries: int = 3
    retry_delay_minutes: int = 5
    rate_limit: RateLimitConfig = None
    enabled: bool = True
    
    def __post_init__(self) -> None:
        if self.time_windows is None:
            self.time_windows = []
        if self.rate_limit is None:
            self.rate_limit = RateLimitConfig()


@dataclass
class ScheduledTask:
    """Scheduled synchronization task"""
    task_id: str
    user_id: str
    content_id: str
    platform_type: PlatformType
    schedule_type: ScheduleType
    scheduled_time: datetime
    created_time: datetime
    priority: Priority
    status: ScheduleStatus
    rule_id: Optional[str] = None
    attempts: int = 0
    max_retries: int = 3
    last_attempt: Optional[datetime] = None
    next_retry: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    dependencies: List[str] = None
    
    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class OptimalTimeRecommendation:
    """AI-driven optimal time recommendation"""
    platform_type: PlatformType
    recommended_time: datetime
    confidence_score: float  # 0.0 - 1.0
    expected_engagement: float
    audience_overlap: float
    competition_level: float
    reasoning: str


class SyncScheduler:
    """
    Enterprise Platform Synchronization Scheduler
    
    Provides intelligent scheduling for content synchronization across platforms
    with AI-driven optimization, rate limiting, and conflict resolution.
    """
    
    def __init__(self, db -> None: AsyncIOMotorDatabase, platform_manager -> None: PlatformManager) -> None:
        """
        Initialize Sync Scheduler
        
        Args:
            db: MongoDB database connection
            platform_manager: Platform manager instance
        """
        self.db = db
        self.platform_manager = platform_manager
        
        # Collections
        self.schedules_collection = db.sync_schedules
        self.rules_collection = db.schedule_rules
        self.tasks_collection = db.scheduled_tasks
        self.analytics_collection = db.schedule_analytics
        self.recommendations_collection = db.optimal_times
        
        # Scheduler state
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._executor_tasks: List[asyncio.Task] = []
        
        # Rate limiting tracking
        self._rate_trackers: Dict[str, Dict[str, Any]] = {}
        
        # Optimal timing cache
        self._optimal_times_cache: Dict[str, List[OptimalTimeRecommendation]] = {}
        self._cache_ttl = timedelta(hours=1)
        self._last_cache_update = datetime.utcnow()
        
        # Configuration
        self._max_concurrent_tasks = 10
        self._check_interval_seconds = 30
        self._ai_optimization_enabled = True
    
    async def initialize(self) -> None:
        """Initialize sync scheduler"""
        try:
            # Create indexes
            await self.schedules_collection.create_index([("user_id", 1), ("platform_type", 1)])
            await self.schedules_collection.create_index([("scheduled_time", 1)])
            await self.schedules_collection.create_index([("status", 1), ("priority", -1)])
            
            await self.rules_collection.create_index([("user_id", 1), ("platform_type", 1)])
            await self.rules_collection.create_index([("enabled", 1)])
            
            await self.tasks_collection.create_index([("scheduled_time", 1), ("status", 1)])
            await self.tasks_collection.create_index([("user_id", 1), ("platform_type", 1)])
            await self.tasks_collection.create_index([("priority", -1), ("created_time", 1)])
            
            await self.analytics_collection.create_index([("platform_type", 1), ("date", -1)])
            await self.recommendations_collection.create_index([("platform_type", 1), ("date", -1)])
            
            # Start scheduler
            await self._start_scheduler()
            
            logger.info("Sync Scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sync Scheduler: {e}")
            raise
    
    async def create_schedule_rule(self, user_id: str, rule: ScheduleRule) -> bool:
        """
        Create a new scheduling rule
        
        Args:
            user_id: User identifier
            rule: Schedule rule configuration
            
        Returns:
            bool: Success status
        """
        try:
            # Validate rule
            if not await self._validate_schedule_rule(rule):
                return False
            
            # Store rule
            doc = {
                "user_id": user_id,
                "rule_id": rule.rule_id,
                "rule_data": asdict(rule),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.rules_collection.replace_one(
                {"user_id": user_id, "rule_id": rule.rule_id},
                doc,
                upsert=True
            )
            
            logger.info(f"Schedule rule {rule.rule_id} created for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create schedule rule: {e}")
            return False
    
    async def schedule_sync(self, user_id: str, content_id: str, 
                          platform_type: PlatformType,
                          schedule_type: ScheduleType = ScheduleType.IMMEDIATE,
                          scheduled_time: Optional[datetime] = None,
                          priority: Priority = Priority.NORMAL,
                          rule_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Schedule content synchronization
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            platform_type: Target platform
            schedule_type: Type of scheduling
            scheduled_time: Specific time for scheduling
            priority: Task priority
            rule_id: Optional rule to apply
            metadata: Additional metadata
            
        Returns:
            Optional[str]: Task ID if successful
        """
        try:
            # Generate task ID
            task_id = hashlib.md5(f"{user_id}:{content_id}:{platform_type.value}:{datetime.utcnow()}".encode()).hexdigest()
            
            # Determine scheduling time
            if schedule_type == ScheduleType.OPTIMAL_TIME:
                scheduled_time = await self._get_optimal_time(user_id, platform_type)
            elif schedule_type == ScheduleType.IMMEDIATE:
                scheduled_time = datetime.utcnow()
            elif not scheduled_time:
                # Default to immediate if no time specified
                scheduled_time = datetime.utcnow()
            
            # Check rate limits
            if not await self._check_rate_limits(user_id, platform_type):
                # Schedule for later if rate limited
                scheduled_time = await self._get_next_available_slot(user_id, platform_type)
            
            # Create task
            task = ScheduledTask(
                task_id=task_id,
                user_id=user_id,
                content_id=content_id,
                platform_type=platform_type,
                schedule_type=schedule_type,
                scheduled_time=scheduled_time,
                created_time=datetime.utcnow(),
                priority=priority,
                status=ScheduleStatus.PENDING,
                rule_id=rule_id,
                metadata=metadata or {}
            )
            
            # Apply rule if specified
            if rule_id:
                rule = await self._get_schedule_rule(user_id, rule_id)
                if rule:
                    task.max_retries = rule.max_retries
                    task.priority = rule.priority
            
            # Store task
            await self.tasks_collection.insert_one(asdict(task))
            
            logger.info(f"Sync task {task_id} scheduled for {scheduled_time}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule sync: {e}")
            return None
    
    async def get_optimal_times(self, user_id: str, platform_type: PlatformType,
                              date_range: Optional[Tuple[datetime, datetime]] = None) -> List[OptimalTimeRecommendation]:
        """
        Get AI-driven optimal posting times for a platform
        
        Args:
            user_id: User identifier
            platform_type: Target platform
            date_range: Optional date range for recommendations
            
        Returns:
            List[OptimalTimeRecommendation]: List of optimal times
        """
        try:
            cache_key = f"{user_id}:{platform_type.value}"
            
            # Check cache
            if (cache_key in self._optimal_times_cache and 
                (datetime.utcnow() - self._last_cache_update) < self._cache_ttl):
                return self._optimal_times_cache[cache_key]
            
            # Generate recommendations using AI
            recommendations = await self._generate_optimal_times(user_id, platform_type, date_range)
            
            # Cache results
            self._optimal_times_cache[cache_key] = recommendations
            self._last_cache_update = datetime.utcnow()
            
            # Store in database
            for rec in recommendations:
                doc = {
                    "user_id": user_id,
                    "platform_type": platform_type.value,
                    "recommendation": asdict(rec),
                    "date": rec.recommended_time.date(),
                    "created_at": datetime.utcnow()
                }
                
                await self.recommendations_collection.replace_one(
                    {
                        "user_id": user_id,
                        "platform_type": platform_type.value,
                        "date": rec.recommended_time.date()
                    },
                    doc,
                    upsert=True
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get optimal times: {e}")
            return []
    
    async def get_scheduled_tasks(self, user_id: str, 
                                platform_type: Optional[PlatformType] = None,
                                status_filter: Optional[ScheduleStatus] = None,
                                limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's scheduled tasks
        
        Args:
            user_id: User identifier
            platform_type: Optional platform filter
            status_filter: Optional status filter
            limit: Maximum number of tasks to return
            
        Returns:
            List[Dict[str, Any]]: List of scheduled tasks
        """
        try:
            query = {"user_id": user_id}
            
            if platform_type:
                query["platform_type"] = platform_type.value
            
            if status_filter:
                query["status"] = status_filter.value
            
            cursor = self.tasks_collection.find(query).sort([
                ("priority", -1),
                ("scheduled_time", 1)
            ]).limit(limit)
            
            tasks = await cursor.to_list(length=None)
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get scheduled tasks: {e}")
            return []
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task
        
        Args:
            task_id: Task identifier
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.tasks_collection.update_one(
                {"task_id": task_id, "status": {"$in": ["pending", "scheduled"]}},
                {
                    "$set": {
                        "status": ScheduleStatus.CANCELLED.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            return False
    
    async def reschedule_task(self, task_id: str, new_time: datetime) -> bool:
        """
        Reschedule a task to a new time
        
        Args:
            task_id: Task identifier
            new_time: New scheduled time
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.tasks_collection.update_one(
                {"task_id": task_id, "status": {"$in": ["pending", "scheduled"]}},
                {
                    "$set": {
                        "scheduled_time": new_time,
                        "status": ScheduleStatus.PENDING.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to reschedule task: {e}")
            return False
    
    async def get_schedule_analytics(self, user_id: str, 
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get scheduling analytics
        
        Args:
            user_id: User identifier
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Dict[str, Any]: Analytics data
        """
        try:
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Aggregation pipeline
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "created_time": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "platform": "$platform_type",
                            "status": "$status"
                        },
                        "count": {"$sum": 1},
                        "avg_attempts": {"$avg": "$attempts"}
                    }
                },
                {
                    "$group": {
                        "_id": "$_id.platform",
                        "total_tasks": {"$sum": "$count"},
                        "status_breakdown": {
                            "$push": {
                                "status": "$_id.status",
                                "count": "$count",
                                "avg_attempts": "$avg_attempts"
                            }
                        }
                    }
                }
            ]
            
            cursor = self.tasks_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Calculate summary statistics
            summary = {
                "total_tasks": sum(r["total_tasks"] for r in results),
                "platforms": results,
                "date_range": {
                    "start": start_date,
                    "end": end_date
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get schedule analytics: {e}")
            return {}
    
    async def _start_scheduler(self) -> None:
        """Start the scheduler task"""
        if self._running:
            return
        
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Start executor tasks
        for i in range(self._max_concurrent_tasks):
            task = asyncio.create_task(self._executor_loop(f"executor_{i}"))
            self._executor_tasks.append(task)
        
        logger.info("Sync Scheduler started")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self._running:
            try:
                await self._process_scheduled_tasks()
                await self._update_optimal_times()
                await self._cleanup_completed_tasks()
                
                await asyncio.sleep(self._check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(self._check_interval_seconds)
    
    async def _executor_loop(self, executor_name: str) -> None:
        """Executor loop for processing tasks"""
        logger.info(f"Executor {executor_name} started")
        
        while self._running:
            try:
                # Get next task to execute
                task_doc = await self.tasks_collection.find_one_and_update(
                    {
                        "status": ScheduleStatus.SCHEDULED.value,
                        "scheduled_time": {"$lte": datetime.utcnow()}
                    },
                    {"$set": {"status": ScheduleStatus.EXECUTING.value}},
                    sort=[("priority", -1), ("scheduled_time", 1)]
                )
                
                if task_doc:
                    await self._execute_task(task_doc)
                else:
                    await asyncio.sleep(5)  # No tasks available
                    
            except Exception as e:
                logger.error(f"Executor {executor_name} error: {e}")
                await asyncio.sleep(5)
        
        logger.info(f"Executor {executor_name} stopped")
    
    async def _process_scheduled_tasks(self) -> None:
        """Process pending tasks and schedule them"""
        try:
            # Get pending tasks that should be scheduled
            cursor = self.tasks_collection.find({
                "status": ScheduleStatus.PENDING.value,
                "scheduled_time": {"$lte": datetime.utcnow() + timedelta(minutes=5)}
            })
            
            async for task_doc in cursor:
                # Check if ready to schedule
                if await self._is_ready_to_schedule(task_doc):
                    await self.tasks_collection.update_one(
                        {"task_id": task_doc["task_id"]},
                        {"$set": {"status": ScheduleStatus.SCHEDULED.value}}
                    )
                    
        except Exception as e:
            logger.error(f"Failed to process scheduled tasks: {e}")
    
    async def _execute_task(self, task_doc: Dict[str, Any]) -> None:
        """Execute a scheduled task"""
        task_id = task_doc["task_id"]
        
        try:
            logger.info(f"Executing task {task_id}")
            
            # Update attempt count
            await self.tasks_collection.update_one(
                {"task_id": task_id},
                {
                    "$inc": {"attempts": 1},
                    "$set": {"last_attempt": datetime.utcnow()}
                }
            )
            
            # Execute the actual sync operation
            success = await self._perform_sync_operation(task_doc)
            
            if success:
                # Mark as completed
                await self.tasks_collection.update_one(
                    {"task_id": task_id},
                    {
                        "$set": {
                            "status": ScheduleStatus.COMPLETED.value,
                            "completed_at": datetime.utcnow()
                        }
                    }
                )
                logger.info(f"Task {task_id} completed successfully")
            else:
                # Handle failure
                await self._handle_task_failure(task_doc)
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            await self._handle_task_failure(task_doc, str(e))
    
    async def _perform_sync_operation(self, task_doc: Dict[str, Any]) -> bool:
        """Perform the actual synchronization operation"""
        
        # This would integrate with the actual platform APIs
        # For now, simulate the operation
        
        try:
            user_id = task_doc["user_id"]
            platform_type = PlatformType(task_doc["platform_type"])
            content_id = task_doc["content_id"]
            
            # Check rate limits
            if not await self._check_rate_limits(user_id, platform_type):
                return False
            
            # Simulate API call
            await asyncio.sleep(2)
            
            # Update rate tracker
            await self._update_rate_tracker(user_id, platform_type)
            
            return True
            
        except Exception as e:
            logger.error(f"Sync operation failed: {e}")
            return False
    
    async def _handle_task_failure(self, task_doc: Dict[str, Any], error_message: str = None) -> None:
        """Handle task execution failure"""
        
        task_id = task_doc["task_id"]
        attempts = task_doc.get("attempts", 0)
        max_retries = task_doc.get("max_retries", 3)
        
        if attempts < max_retries:
            # Schedule retry
            retry_delay = timedelta(minutes=task_doc.get("retry_delay_minutes", 5))
            next_retry = datetime.utcnow() + retry_delay
            
            await self.tasks_collection.update_one(
                {"task_id": task_id},
                {
                    "$set": {
                        "status": ScheduleStatus.PENDING.value,
                        "scheduled_time": next_retry,
                        "next_retry": next_retry,
                        "error_message": error_message
                    }
                }
            )
            
            logger.info(f"Task {task_id} scheduled for retry at {next_retry}")
        else:
            # Mark as failed
            await self.tasks_collection.update_one(
                {"task_id": task_id},
                {
                    "$set": {
                        "status": ScheduleStatus.FAILED.value,
                        "completed_at": datetime.utcnow(),
                        "error_message": error_message
                    }
                }
            )
            
            logger.error(f"Task {task_id} failed permanently after {attempts} attempts")
    
    async def _check_rate_limits(self, user_id: str, platform_type: PlatformType) -> bool:
        """Check if rate limits allow execution"""
        
        # Use platform manager's rate limit checking
        can_proceed, _ = await self.platform_manager.check_rate_limits(user_id, platform_type)
        return can_proceed
    
    async def _update_rate_tracker(self, user_id: str, platform_type: PlatformType) -> None:
        """Update rate limiting tracker"""
        
        key = f"{user_id}:{platform_type.value}"
        now = datetime.utcnow()
        
        if key not in self._rate_trackers:
            self._rate_trackers[key] = {
                "last_request": now,
                "request_count": 1
            }
        else:
            self._rate_trackers[key]["last_request"] = now
            self._rate_trackers[key]["request_count"] += 1
    
    async def _get_optimal_time(self, user_id: str, platform_type: PlatformType) -> datetime:
        """Get optimal posting time for platform"""
        
        recommendations = await self.get_optimal_times(user_id, platform_type)
        
        if recommendations:
            # Return the highest confidence recommendation
            best_rec = max(recommendations, key=lambda x: x.confidence_score)
            return best_rec.recommended_time
        
        # Default to current time if no recommendations
        return datetime.utcnow()
    
    async def _get_next_available_slot(self, user_id: str, platform_type: PlatformType) -> datetime:
        """Get next available time slot respecting rate limits"""
        
        # Simple implementation - add delay based on current rate
        base_delay = timedelta(minutes=5)  # Minimum delay
        
        # Check current queue for this platform
        queue_count = await self.tasks_collection.count_documents({
            "user_id": user_id,
            "platform_type": platform_type.value,
            "status": {"$in": ["pending", "scheduled"]}
        })
        
        # Add additional delay based on queue size
        additional_delay = timedelta(minutes=queue_count * 2)
        
        return datetime.utcnow() + base_delay + additional_delay
    
    async def _generate_optimal_times(self, user_id: str, platform_type: PlatformType,
                                    date_range: Optional[Tuple[datetime, datetime]] = None) -> List[OptimalTimeRecommendation]:
        """Generate AI-driven optimal posting time recommendations"""
        
        if not date_range:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=7)
            date_range = (start_date, end_date)
        
        recommendations = []
        
        # Platform-specific optimal times (simplified ML model)
        platform_patterns = {
            PlatformType.INSTAGRAM: [
                (9, 11),   # 9-11 AM
                (13, 15),  # 1-3 PM
                (19, 21)   # 7-9 PM
            ],
            PlatformType.TIKTOK: [
                (6, 10),   # 6-10 AM
                (19, 23)   # 7-11 PM
            ],
            PlatformType.YOUTUBE: [
                (14, 16),  # 2-4 PM
                (20, 22)   # 8-10 PM
            ],
            PlatformType.TWITTER: [
                (8, 10),   # 8-10 AM
                (12, 14),  # 12-2 PM
                (17, 19)   # 5-7 PM
            ]
        }
        
        patterns = platform_patterns.get(platform_type, [(9, 17)])  # Default business hours
        
        current_date = date_range[0].date()
        end_date = date_range[1].date()
        
        while current_date <= end_date:
            for start_hour, end_hour in patterns:
                # Generate recommendation for each optimal window
                optimal_hour = start_hour + (end_hour - start_hour) // 2
                
                recommended_time = datetime.combine(
                    current_date,
                    datetime.min.time().replace(hour=optimal_hour)
                ).replace(tzinfo=timezone.utc)
                
                # Skip past times
                if recommended_time <= datetime.utcnow():
                    continue
                
                # Calculate confidence based on various factors
                confidence = self._calculate_time_confidence(
                    recommended_time, platform_type, user_id
                )
                
                recommendation = OptimalTimeRecommendation(
                    platform_type=platform_type,
                    recommended_time=recommended_time,
                    confidence_score=confidence,
                    expected_engagement=0.7 + (confidence * 0.3),
                    audience_overlap=0.8,
                    competition_level=0.5,
                    reasoning=f"Optimal time based on {platform_type.value} engagement patterns"
                )
                
                recommendations.append(recommendation)
            
            current_date += timedelta(days=1)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations[:20]  # Return top 20 recommendations
    
    def _calculate_time_confidence(self, time: datetime, platform_type: PlatformType, user_id: str) -> float:
        """Calculate confidence score for a recommended time"""
        
        # Base confidence
        confidence = 0.5
        
        # Time-based factors
        hour = time.hour
        weekday = time.weekday()
        
        # Weekday vs weekend
        if weekday < 5:  # Weekday
            confidence += 0.1
        
        # Platform-specific time preferences
        if platform_type == PlatformType.INSTAGRAM:
            if 9 <= hour <= 11 or 13 <= hour <= 15 or 19 <= hour <= 21:
                confidence += 0.3
        elif platform_type == PlatformType.TIKTOK:
            if 6 <= hour <= 10 or 19 <= hour <= 23:
                confidence += 0.3
        elif platform_type == PlatformType.YOUTUBE:
            if 14 <= hour <= 16 or 20 <= hour <= 22:
                confidence += 0.3
        
        # Add some randomness to simulate ML uncertainty
        import random
        confidence += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, confidence))
    
    async def _validate_schedule_rule(self, rule: ScheduleRule) -> bool:
        """Validate schedule rule configuration"""
        
        try:
            # Validate cron expression if provided
            if rule.cron_expression:
                croniter(rule.cron_expression)
            
            # Validate time windows
            for window in rule.time_windows:
                if not (0 <= window.start_hour <= 23 and 0 <= window.end_hour <= 23):
                    return False
                
                try:
                    pytz.timezone(window.timezone)
                except:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule validation failed: {e}")
            return False
    
    async def _get_schedule_rule(self, user_id: str, rule_id: str) -> Optional[ScheduleRule]:
        """Get schedule rule by ID"""
        
        try:
            doc = await self.rules_collection.find_one({
                "user_id": user_id,
                "rule_id": rule_id
            })
            
            if not doc:
                return None
            
            rule_data = doc["rule_data"]
            return ScheduleRule(**rule_data)
            
        except Exception as e:
            logger.error(f"Failed to get schedule rule: {e}")
            return None
    
    async def _is_ready_to_schedule(self, task_doc: Dict[str, Any]) -> bool:
        """Check if task is ready to be scheduled"""
        
        # Check dependencies
        dependencies = task_doc.get("dependencies", [])
        if dependencies:
            # Check if all dependencies are completed
            completed_deps = await self.tasks_collection.count_documents({
                "task_id": {"$in": dependencies},
                "status": ScheduleStatus.COMPLETED.value
            })
            
            if completed_deps < len(dependencies):
                return False
        
        return True
    
    async def _update_optimal_times(self) -> None:
        """Update cached optimal times periodically"""
        
        # This would typically analyze historical data to improve recommendations
        # For now, just update cache timestamp
        if (datetime.utcnow() - self._last_cache_update) > self._cache_ttl:
            self._optimal_times_cache.clear()
            self._last_cache_update = datetime.utcnow()
    
    async def _cleanup_completed_tasks(self) -> None:
        """Cleanup old completed tasks"""
        
        try:
            # Remove completed tasks older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            result = await self.tasks_collection.delete_many({
                "status": {"$in": [ScheduleStatus.COMPLETED.value, ScheduleStatus.FAILED.value]},
                "completed_at": {"$lt": cutoff_date}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old tasks")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup scheduler resources"""
        
        self._running = False
        
        # Cancel scheduler task
        if self._scheduler_task:
            self._scheduler_task.cancel()
        
        # Cancel executor tasks
        for task in self._executor_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        all_tasks = [self._scheduler_task] + self._executor_tasks
        await asyncio.gather(*all_tasks, return_exceptions=True)
        
        logger.info("Sync Scheduler cleanup completed")


async def create_sync_scheduler(db: AsyncIOMotorDatabase, 
                              platform_manager: PlatformManager) -> SyncScheduler:
    """
    Factory function to create and initialize Sync Scheduler
    
    Args:
        db: MongoDB database connection
        platform_manager: Platform manager instance
        
    Returns:
        SyncScheduler: Initialized sync scheduler
    """
    scheduler = SyncScheduler(db, platform_manager)
    await scheduler.initialize()
    return scheduler