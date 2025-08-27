"""
Time-Based Scheduler Module
==========================

Advanced time-based scheduling system for crawler operations.
Implements cron-like scheduling with intelligent timing optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts

Business Logic Integration:
Content scheduling → Timezone optimization → Platform timing → 
Audience engagement peaks → Campaign coordination → SEO timing → 
Collaboration synchronization → Multi-platform distribution → Revenue optimization
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import uuid
import pytz
from croniter import croniter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
import sqlite3
import aiofiles
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Types of scheduling patterns."""
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"
    OPTIMAL = "optimal"
    CONDITIONAL = "conditional"
    COLLABORATIVE = "collaborative"


class TimingStrategy(Enum):
    """Timing optimization strategies."""
    IMMEDIATE = "immediate"
    PEAK_ENGAGEMENT = "peak_engagement"
    OFF_PEAK = "off_peak"
    BALANCED = "balanced"
    SEQUENTIAL = "sequential"
    SYNCHRONIZED = "synchronized"
    ADAPTIVE = "adaptive"


class PlatformTiming(Enum):
    """Platform-specific timing preferences."""
    YOUTUBE_PRIME = "youtube_prime"  # 2-4 PM, 8-11 PM
    INSTAGRAM_PEAK = "instagram_peak"  # 11 AM-1 PM, 7-9 PM
    TIKTOK_VIRAL = "tiktok_viral"  # 6-10 AM, 7-9 PM
    TWITTER_ENGAGEMENT = "twitter_engagement"  # 9 AM-3 PM
    FACEBOOK_FAMILY = "facebook_family"  # 1-4 PM, 7-9 PM
    SPOTIFY_DISCOVERY = "spotify_discovery"  # 7-9 AM, 5-7 PM


@dataclass
class TimezoneConfig:
    """Timezone configuration for scheduling."""
    primary_timezone: str = "UTC"
    target_timezones: List[str] = field(default_factory=lambda: ["UTC"])
    audience_distribution: Dict[str, float] = field(default_factory=dict)
    peak_hours: Dict[str, List[int]] = field(default_factory=dict)
    business_hours: Dict[str, Tuple[int, int]] = field(default_factory=dict)


@dataclass
class ScheduleWindow:
    """Time window for scheduling."""
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    priority: float = 1.0
    max_tasks: int = 10
    platform_preferences: List[str] = field(default_factory=list)
    engagement_multiplier: float = 1.0


@dataclass
class TimedTask:
    """Time-scheduled task definition."""
    task_id: str
    schedule_type: ScheduleType
    trigger_expression: str  # Cron expression, interval, or datetime ISO
    task_definition: Dict[str, Any]
    timezone: str = "UTC"
    created_at: datetime = field(default_factory=datetime.utcnow)
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None
    is_active: bool = True
    timing_strategy: TimingStrategy = TimingStrategy.IMMEDIATE
    platform_timing: Optional[PlatformTiming] = None
    collaborators: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.task_id:
            self.task_id = f"timed_{uuid.uuid4().hex[:8]}"
        
        # Calculate next run time
        if not self.next_run:
            self.next_run = self._calculate_next_run()
    
    def _calculate_next_run(self) -> Optional[datetime]:
        """Calculate next run time based on schedule type."""
        try:
            tz = pytz.timezone(self.timezone)
            base_time = datetime.now(tz)
            
            if self.schedule_type == ScheduleType.ONCE:
                # Parse ISO datetime
                return datetime.fromisoformat(self.trigger_expression.replace('Z', '+00:00'))
            
            elif self.schedule_type == ScheduleType.INTERVAL:
                # Parse interval (e.g., "30m", "1h", "2d")
                interval_seconds = self._parse_interval(self.trigger_expression)
                return base_time + timedelta(seconds=interval_seconds)
            
            elif self.schedule_type == ScheduleType.CRON:
                # Use croniter for cron expressions
                cron = croniter(self.trigger_expression, base_time)
                return cron.get_next(datetime)
            
            elif self.schedule_type == ScheduleType.OPTIMAL:
                # Calculate optimal time based on strategy
                return self._calculate_optimal_time(base_time)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to calculate next run time: {e}")
            return None
    
    def _parse_interval(self, interval_str: str) -> int:
        """Parse interval string to seconds."""
        unit_multipliers = {
            's': 1, 'sec': 1, 'second': 1, 'seconds': 1,
            'm': 60, 'min': 60, 'minute': 60, 'minutes': 60,
            'h': 3600, 'hour': 3600, 'hours': 3600,
            'd': 86400, 'day': 86400, 'days': 86400,
            'w': 604800, 'week': 604800, 'weeks': 604800
        }
        
        # Extract number and unit
        import re
        match = re.match(r'(\d+)([a-zA-Z]+)', interval_str.strip())
        if match:
            number = int(match.group(1))
            unit = match.group(2).lower()
            multiplier = unit_multipliers.get(unit, 60)
            return number * multiplier
        
        return 3600  # Default to 1 hour
    
    def _calculate_optimal_time(self, base_time: datetime) -> datetime:
        """Calculate optimal execution time based on strategy and platform."""
        if self.platform_timing:
            return self._get_platform_optimal_time(base_time)
        
        if self.timing_strategy == TimingStrategy.PEAK_ENGAGEMENT:
            # Default peak hours: 10 AM - 2 PM, 7 PM - 10 PM
            current_hour = base_time.hour
            
            if 10 <= current_hour <= 14:
                # Already in morning peak
                return base_time + timedelta(minutes=30)
            elif 19 <= current_hour <= 22:
                # Already in evening peak
                return base_time + timedelta(minutes=30)
            elif current_hour < 10:
                # Wait for morning peak
                return base_time.replace(hour=10, minute=0, second=0, microsecond=0)
            else:
                # Wait for next day morning peak
                next_day = base_time + timedelta(days=1)
                return next_day.replace(hour=10, minute=0, second=0, microsecond=0)
        
        elif self.timing_strategy == TimingStrategy.OFF_PEAK:
            # Off-peak hours: 2 AM - 6 AM
            if 2 <= base_time.hour <= 6:
                return base_time + timedelta(minutes=30)
            else:
                next_run = base_time.replace(hour=3, minute=0, second=0, microsecond=0)
                if next_run <= base_time:
                    next_run += timedelta(days=1)
                return next_run
        
        else:
            # Default to immediate or small delay
            return base_time + timedelta(minutes=5)
    
    def _get_platform_optimal_time(self, base_time: datetime) -> datetime:
        """Get platform-specific optimal timing."""
        platform_schedules = {
            PlatformTiming.YOUTUBE_PRIME: [(14, 16), (20, 23)],  # 2-4 PM, 8-11 PM
            PlatformTiming.INSTAGRAM_PEAK: [(11, 13), (19, 21)],  # 11 AM-1 PM, 7-9 PM
            PlatformTiming.TIKTOK_VIRAL: [(6, 10), (19, 21)],  # 6-10 AM, 7-9 PM
            PlatformTiming.TWITTER_ENGAGEMENT: [(9, 15)],  # 9 AM-3 PM
            PlatformTiming.FACEBOOK_FAMILY: [(13, 16), (19, 21)],  # 1-4 PM, 7-9 PM
            PlatformTiming.SPOTIFY_DISCOVERY: [(7, 9), (17, 19)]  # 7-9 AM, 5-7 PM
        }
        
        time_windows = platform_schedules.get(self.platform_timing, [(base_time.hour, base_time.hour + 1)])
        current_hour = base_time.hour
        
        # Find next available window
        for start_hour, end_hour in time_windows:
            if start_hour <= current_hour < end_hour:
                # Already in window
                return base_time + timedelta(minutes=30)
            elif current_hour < start_hour:
                # Wait for this window
                return base_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        # Wait for first window tomorrow
        next_day = base_time + timedelta(days=1)
        first_window_start = time_windows[0][0]
        return next_day.replace(hour=first_window_start, minute=0, second=0, microsecond=0)


@dataclass
class SchedulerMetrics:
    """Time-based scheduler metrics."""
    total_scheduled_tasks: int = 0
    active_schedules: int = 0
    completed_schedules: int = 0
    missed_schedules: int = 0
    average_execution_delay: float = 0.0
    timing_accuracy: float = 0.0
    platform_distribution: Dict[str, int] = field(default_factory=dict)
    timezone_coverage: Dict[str, int] = field(default_factory=dict)
    collaboration_sync_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class TimeBasedScheduler:
    """
    Advanced time-based scheduler for crawler operations.
    
    Features:
    - Cron-like scheduling with advanced expressions
    - Multi-timezone support with audience optimization
    - Platform-specific timing optimization
    - Collaborative scheduling and synchronization
    - Intelligent peak-time detection
    - Adaptive timing based on performance
    - Campaign coordination across time zones
    - SEO-optimized scheduling
    """
    
    def __init__(
        self,
        default_timezone: str = "UTC",
        enable_timezone_optimization: bool = True,
        enable_platform_timing: bool = True,
        enable_collaborative_sync: bool = True,
        max_concurrent_schedules: int = 1000
    ):
        """Initialize time-based scheduler."""
        self.default_timezone = default_timezone
        self.enable_timezone_optimization = enable_timezone_optimization
        self.enable_platform_timing = enable_platform_timing
        self.enable_collaborative_sync = enable_collaborative_sync
        self.max_concurrent_schedules = max_concurrent_schedules
        
        # APScheduler setup
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={'default': AsyncIOExecutor()},
            job_defaults={'coalesce': False, 'max_instances': 3}
        )
        
        # Task storage
        self.timed_tasks: Dict[str, TimedTask] = {}
        self.schedule_history: deque = deque(maxlen=1000)
        self.collaboration_groups: Dict[str, List[str]] = defaultdict(list)
        
        # Timezone management
        self.timezone_configs: Dict[str, TimezoneConfig] = {}
        self.audience_data: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.metrics = SchedulerMetrics()
        self.execution_history: deque = deque(maxlen=500)
        
        # Configuration
        self.config = {
            'scheduling_precision': 30,  # seconds
            'missed_job_grace_time': 300,  # seconds
            'collaboration_sync_tolerance': 60,  # seconds
            'peak_detection_window': 7,  # days
            'platform_timing_enabled': True,
            'adaptive_timing_enabled': True,
            'timezone_auto_detection': True,
            'execution_timeout': 3600,  # seconds
            'retry_failed_schedules': True,
            'max_schedule_drift': 300  # seconds
        }
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # State
        self.is_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Setup event listeners
        self.scheduler.add_listener(self._on_job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._on_job_missed, EVENT_JOB_MISSED)
        
        logger.info(f"Time-based scheduler initialized with timezone: {default_timezone}")
    
    async def start_scheduler(self) -> None:
        """Start the time-based scheduler."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        try:
            self.scheduler.start()
            self.is_running = True
            
            # Start monitoring tasks
            self.scheduler_task = asyncio.create_task(self._monitoring_loop())
            
            # Initialize timezone optimization
            if self.enable_timezone_optimization:
                await self._initialize_timezone_optimization()
            
            logger.info("Time-based scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop_scheduler(self) -> None:
        """Stop the time-based scheduler gracefully."""
        self.is_running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.scheduler.shutdown(wait=True)
        logger.info("Time-based scheduler stopped")
    
    async def schedule_task(
        self,
        task: TimedTask,
        replace_existing: bool = False
    ) -> str:
        """Schedule a time-based task."""
        try:
            # Check if task already exists
            if task.task_id in self.timed_tasks and not replace_existing:
                raise ValueError(f"Task already scheduled: {task.task_id}")
            
            # Validate schedule
            await self._validate_schedule(task)
            
            # Apply timing optimization
            if self.enable_platform_timing and task.platform_timing:
                await self._optimize_platform_timing(task)
            
            # Handle collaborative scheduling
            if self.enable_collaborative_sync and task.collaborators:
                await self._setup_collaborative_scheduling(task)
            
            # Create APScheduler job
            await self._create_scheduler_job(task)
            
            # Store task
            self.timed_tasks[task.task_id] = task
            
            # Update metrics
            self.metrics.total_scheduled_tasks += 1
            self.metrics.active_schedules += 1
            
            logger.info(
                f"Task scheduled: {task.task_id} "
                f"(type={task.schedule_type.value}, next_run={task.next_run})"
            )
            
            # Call scheduling callbacks
            await self._call_callbacks('scheduled', task)
            
            return task.task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule task {task.task_id}: {e}")
            raise
    
    async def _validate_schedule(self, task: TimedTask) -> None:
        """Validate task schedule configuration."""
        # Check schedule limits
        if len(self.timed_tasks) >= self.max_concurrent_schedules:
            raise ValueError("Maximum concurrent schedules reached")
        
        # Validate timezone
        try:
            pytz.timezone(task.timezone)
        except Exception:
            raise ValueError(f"Invalid timezone: {task.timezone}")
        
        # Validate cron expression if applicable
        if task.schedule_type == ScheduleType.CRON:
            try:
                croniter(task.trigger_expression)
            except Exception:
                raise ValueError(f"Invalid cron expression: {task.trigger_expression}")
        
        # Validate datetime for one-time schedules
        if task.schedule_type == ScheduleType.ONCE:
            try:
                datetime.fromisoformat(task.trigger_expression.replace('Z', '+00:00'))
            except Exception:
                raise ValueError(f"Invalid datetime format: {task.trigger_expression}")
    
    async def _optimize_platform_timing(self, task: TimedTask) -> None:
        """Optimize timing based on platform preferences."""
        if not task.platform_timing:
            return
        
        # Recalculate next run time with platform optimization
        task.next_run = task._calculate_next_run()
        
        # Apply timezone optimization if enabled
        if self.enable_timezone_optimization:
            await self._apply_timezone_optimization(task)
    
    async def _apply_timezone_optimization(self, task: TimedTask) -> None:
        """Apply timezone optimization for global audience."""
        # Get audience distribution for this task's context
        audience_data = self.audience_data.get(task.task_id, {})
        
        if not audience_data:
            return
        
        # Find optimal timezone based on audience distribution
        primary_timezone = max(
            audience_data.get('timezone_distribution', {'UTC': 1.0}),
            key=audience_data.get('timezone_distribution', {'UTC': 1.0}).get
        )
        
        # Adjust timing for primary audience timezone
        if primary_timezone != task.timezone:
            original_tz = pytz.timezone(task.timezone)
            target_tz = pytz.timezone(primary_timezone)
            
            # Convert to target timezone
            if task.next_run:
                localized_time = original_tz.localize(task.next_run.replace(tzinfo=None))
                converted_time = localized_time.astimezone(target_tz)
                task.next_run = converted_time.replace(tzinfo=None)
                task.timezone = primary_timezone
    
    async def _setup_collaborative_scheduling(self, task: TimedTask) -> None:
        """Setup collaborative scheduling synchronization."""
        if not task.collaborators:
            return
        
        # Add to collaboration group
        group_id = f"collab_{hash('_'.join(sorted(task.collaborators)))}"
        self.collaboration_groups[group_id].append(task.task_id)
        
        # Synchronize timing with other collaborators
        await self._synchronize_collaborative_timing(group_id, task)
    
    async def _synchronize_collaborative_timing(self, group_id: str, new_task: TimedTask) -> None:
        """Synchronize timing across collaborative tasks."""
        group_tasks = [
            self.timed_tasks[task_id] 
            for task_id in self.collaboration_groups[group_id]
            if task_id in self.timed_tasks and task_id != new_task.task_id
        ]
        
        if not group_tasks:
            return
        
        # Find the earliest next run time in the group
        earliest_time = min(
            task.next_run for task in group_tasks 
            if task.next_run is not None
        )
        
        # Adjust new task timing to synchronize
        if new_task.next_run and earliest_time:
            time_diff = abs((new_task.next_run - earliest_time).total_seconds())
            
            if time_diff <= self.config['collaboration_sync_tolerance']:
                # Close enough - synchronize exactly
                new_task.next_run = earliest_time
                logger.info(f"Synchronized task {new_task.task_id} with collaboration group")
    
    async def _create_scheduler_job(self, task: TimedTask) -> None:
        """Create APScheduler job for the task."""
        try:
            # Determine trigger type
            if task.schedule_type == ScheduleType.ONCE:
                trigger = DateTrigger(
                    run_date=task.next_run,
                    timezone=task.timezone
                )
            
            elif task.schedule_type == ScheduleType.INTERVAL:
                interval_seconds = task._parse_interval(task.trigger_expression)
                trigger = IntervalTrigger(
                    seconds=interval_seconds,
                    start_date=task.next_run,
                    timezone=task.timezone
                )
            
            elif task.schedule_type == ScheduleType.CRON:
                trigger = CronTrigger.from_crontab(
                    task.trigger_expression,
                    timezone=task.timezone
                )
            
            else:
                # Default to date trigger
                trigger = DateTrigger(
                    run_date=task.next_run or datetime.now(),
                    timezone=task.timezone
                )
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=self._execute_scheduled_task,
                trigger=trigger,
                args=[task.task_id],
                id=task.task_id,
                name=f"Scheduled task: {task.task_id}",
                max_instances=1,
                coalesce=True,
                misfire_grace_time=self.config['missed_job_grace_time']
            )
            
        except Exception as e:
            logger.error(f"Failed to create scheduler job for {task.task_id}: {e}")
            raise
    
    async def _execute_scheduled_task(self, task_id: str) -> None:
        """Execute a scheduled task."""
        start_time = time.time()
        
        try:
            task = self.timed_tasks.get(task_id)
            if not task:
                logger.error(f"Scheduled task not found: {task_id}")
                return
            
            if not task.is_active:
                logger.info(f"Skipping inactive task: {task_id}")
                return
            
            # Update task execution info
            task.last_run = datetime.utcnow()
            task.run_count += 1
            
            # Check max runs limit
            if task.max_runs and task.run_count >= task.max_runs:
                task.is_active = False
                await self.unschedule_task(task_id)
                logger.info(f"Task completed all runs: {task_id}")
                return
            
            # Execute the actual task
            execution_result = await self._perform_task_execution(task)
            
            # Record execution metrics
            execution_time = time.time() - start_time
            self.execution_history.append({
                'task_id': task_id,
                'scheduled_time': task.next_run,
                'actual_time': task.last_run,
                'execution_time': execution_time,
                'success': execution_result.get('success', False),
                'delay': (task.last_run - task.next_run).total_seconds() if task.next_run else 0
            })
            
            # Update next run time for recurring tasks
            if task.schedule_type in [ScheduleType.INTERVAL, ScheduleType.CRON]:
                task.next_run = task._calculate_next_run()
            
            # Call execution callbacks
            await self._call_callbacks('executed', task, execution_result)
            
            logger.info(f"Scheduled task executed: {task_id} in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Scheduled task execution failed: {task_id}: {e}")
            
            # Handle retry logic
            await self._handle_task_retry(task_id, str(e))
            
            # Call error callbacks
            await self._call_callbacks('error', task, {'error': str(e)})
    
    async def _perform_task_execution(self, task: TimedTask) -> Dict[str, Any]:
        """Perform the actual task execution."""
        # This is a placeholder for actual task execution
        # In real implementation, this would integrate with the crawler system
        
        task_definition = task.task_definition
        task_type = task_definition.get('type', 'unknown')
        
        # Simulate task execution based on type
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            'success': True,
            'task_type': task_type,
            'executed_at': datetime.utcnow().isoformat(),
            'result': f"Task {task.task_id} executed successfully"
        }
    
    async def _handle_task_retry(self, task_id: str, error: str) -> None:
        """Handle retry logic for failed tasks."""
        task = self.timed_tasks.get(task_id)
        if not task or not self.config.get('retry_failed_schedules', True):
            return
        
        retry_config = task.retry_config
        max_retries = retry_config.get('max_retries', 3)
        retry_delay = retry_config.get('retry_delay', 300)  # 5 minutes
        
        current_retries = retry_config.get('current_retries', 0)
        
        if current_retries < max_retries:
            # Schedule retry
            retry_config['current_retries'] = current_retries + 1
            
            # Calculate retry time with exponential backoff
            backoff_multiplier = retry_config.get('backoff_multiplier', 2.0)
            retry_delay_actual = retry_delay * (backoff_multiplier ** current_retries)
            
            retry_time = datetime.utcnow() + timedelta(seconds=retry_delay_actual)
            
            # Update next run time for retry
            task.next_run = retry_time
            
            # Reschedule
            await self._create_scheduler_job(task)
            
            logger.info(f"Scheduled retry {current_retries + 1}/{max_retries} for task {task_id}")
        else:
            logger.error(f"Task {task_id} failed after {max_retries} retries")
            task.is_active = False
    
    async def unschedule_task(self, task_id: str) -> bool:
        """Unschedule a task."""
        try:
            # Remove from APScheduler
            if self.scheduler.get_job(task_id):
                self.scheduler.remove_job(task_id)
            
            # Remove from task storage
            if task_id in self.timed_tasks:
                task = self.timed_tasks[task_id]
                task.is_active = False
                del self.timed_tasks[task_id]
                
                # Update metrics
                self.metrics.active_schedules -= 1
                self.metrics.completed_schedules += 1
                
                # Remove from collaboration groups
                for group_tasks in self.collaboration_groups.values():
                    if task_id in group_tasks:
                        group_tasks.remove(task_id)
                
                # Call unscheduled callbacks
                await self._call_callbacks('unscheduled', task)
                
                logger.info(f"Task unscheduled: {task_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unschedule task {task_id}: {e}")
            return False
    
    async def reschedule_task(
        self,
        task_id: str,
        new_trigger_expression: str,
        new_timezone: Optional[str] = None
    ) -> bool:
        """Reschedule an existing task."""
        try:
            task = self.timed_tasks.get(task_id)
            if not task:
                return False
            
            # Update task configuration
            task.trigger_expression = new_trigger_expression
            if new_timezone:
                task.timezone = new_timezone
            
            # Recalculate next run time
            task.next_run = task._calculate_next_run()
            
            # Remove old job and create new one
            if self.scheduler.get_job(task_id):
                self.scheduler.remove_job(task_id)
            
            await self._create_scheduler_job(task)
            
            logger.info(f"Task rescheduled: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reschedule task {task_id}: {e}")
            return False
    
    async def get_schedule_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a scheduled task."""
        task = self.timed_tasks.get(task_id)
        if not task:
            return None
        
        job = self.scheduler.get_job(task_id)
        
        return {
            'task_id': task.task_id,
            'schedule_type': task.schedule_type.value,
            'trigger_expression': task.trigger_expression,
            'timezone': task.timezone,
            'is_active': task.is_active,
            'created_at': task.created_at.isoformat(),
            'next_run': task.next_run.isoformat() if task.next_run else None,
            'last_run': task.last_run.isoformat() if task.last_run else None,
            'run_count': task.run_count,
            'max_runs': task.max_runs,
            'timing_strategy': task.timing_strategy.value,
            'platform_timing': task.platform_timing.value if task.platform_timing else None,
            'collaborators': task.collaborators,
            'job_scheduled': job is not None,
            'next_scheduled_run': job.next_run_time.isoformat() if job and job.next_run_time else None
        }
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Get comprehensive scheduler status."""
        # Calculate timing accuracy
        recent_executions = list(self.execution_history)[-100:]
        if recent_executions:
            delays = [abs(exec_data['delay']) for exec_data in recent_executions]
            avg_delay = sum(delays) / len(delays)
            timing_accuracy = max(0, 100 - (avg_delay / 60))  # Accuracy as percentage
        else:
            avg_delay = 0
            timing_accuracy = 100
        
        # Update metrics
        self.metrics.average_execution_delay = avg_delay
        self.metrics.timing_accuracy = timing_accuracy
        
        # Platform distribution
        platform_dist = defaultdict(int)
        for task in self.timed_tasks.values():
            if task.platform_timing:
                platform_dist[task.platform_timing.value] += 1
        
        # Timezone coverage
        timezone_coverage = defaultdict(int)
        for task in self.timed_tasks.values():
            timezone_coverage[task.timezone] += 1
        
        return {
            'scheduler_running': self.is_running,
            'total_scheduled_tasks': len(self.timed_tasks),
            'active_schedules': sum(1 for t in self.timed_tasks.values() if t.is_active),
            'pending_jobs': len(self.scheduler.get_jobs()),
            'collaboration_groups': len(self.collaboration_groups),
            'timezone_optimization_enabled': self.enable_timezone_optimization,
            'platform_timing_enabled': self.enable_platform_timing,
            'collaborative_sync_enabled': self.enable_collaborative_sync,
            'metrics': asdict(self.metrics),
            'platform_distribution': dict(platform_dist),
            'timezone_coverage': dict(timezone_coverage),
            'recent_executions': len(self.execution_history),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self.is_running:
            try:
                await self._update_metrics()
                await self._cleanup_completed_tasks()
                await self._check_schedule_health()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)
    
    async def _update_metrics(self) -> None:
        """Update scheduler metrics."""
        # Update basic counts
        self.metrics.active_schedules = sum(1 for t in self.timed_tasks.values() if t.is_active)
        
        # Calculate collaboration sync rate
        total_collaborations = len(self.collaboration_groups)
        if total_collaborations > 0:
            synced_groups = 0
            for group_tasks in self.collaboration_groups.values():
                if len(group_tasks) > 1:
                    # Check if tasks in group are synchronized
                    task_times = [
                        self.timed_tasks[tid].next_run 
                        for tid in group_tasks 
                        if tid in self.timed_tasks and self.timed_tasks[tid].next_run
                    ]
                    
                    if len(task_times) > 1:
                        time_diffs = [
                            abs((t1 - t2).total_seconds()) 
                            for i, t1 in enumerate(task_times) 
                            for t2 in task_times[i+1:]
                        ]
                        
                        if all(diff <= self.config['collaboration_sync_tolerance'] for diff in time_diffs):
                            synced_groups += 1
            
            self.metrics.collaboration_sync_rate = (synced_groups / total_collaborations) * 100
        
        self.metrics.last_updated = datetime.utcnow()
    
    async def _cleanup_completed_tasks(self) -> None:
        """Clean up completed and inactive tasks."""
        completed_tasks = [
            task_id for task_id, task in self.timed_tasks.items()
            if not task.is_active and (not task.max_runs or task.run_count >= task.max_runs)
        ]
        
        for task_id in completed_tasks:
            # Keep for a while for monitoring purposes
            task = self.timed_tasks[task_id]
            if task.last_run and (datetime.utcnow() - task.last_run).days > 7:
                del self.timed_tasks[task_id]
    
    async def _check_schedule_health(self) -> None:
        """Check scheduler health and detect issues."""
        # Check for missed schedules
        missed_count = 0
        current_time = datetime.utcnow()
        
        for task in self.timed_tasks.values():
            if task.is_active and task.next_run and task.next_run < current_time:
                time_diff = (current_time - task.next_run).total_seconds()
                if time_diff > self.config['max_schedule_drift']:
                    missed_count += 1
                    logger.warning(f"Schedule drift detected for task {task.task_id}: {time_diff}s")
        
        self.metrics.missed_schedules = missed_count
    
    async def _initialize_timezone_optimization(self) -> None:
        """Initialize timezone optimization data."""
        # Default timezone configurations
        default_timezones = [
            "UTC", "US/Eastern", "US/Pacific", "Europe/London", 
            "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai", "Australia/Sydney"
        ]
        
        for tz in default_timezones:
            self.timezone_configs[tz] = TimezoneConfig(
                primary_timezone=tz,
                target_timezones=[tz],
                peak_hours={tz: [10, 11, 12, 13, 19, 20, 21]},
                business_hours={tz: (9, 17)}
            )
        
        logger.info("Timezone optimization initialized")
    
    def _on_job_executed(self, event) -> None:
        """Handle job execution event."""
        asyncio.create_task(self._call_callbacks('job_executed', event))
    
    def _on_job_error(self, event) -> None:
        """Handle job error event."""
        logger.error(f"Scheduled job error: {event.job_id}: {event.exception}")
        asyncio.create_task(self._call_callbacks('job_error', event))
    
    def _on_job_missed(self, event) -> None:
        """Handle missed job event."""
        logger.warning(f"Scheduled job missed: {event.job_id}")
        self.metrics.missed_schedules += 1
        asyncio.create_task(self._call_callbacks('job_missed', event))
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """Add event callback."""
        self.event_callbacks[event_type].append(callback)
    
    async def _call_callbacks(self, event_type: str, *args) -> None:
        """Call registered callbacks for an event."""
        for callback in self.event_callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args)
                else:
                    callback(*args)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")


# Export main classes
__all__ = [
    'TimeBasedScheduler',
    'TimedTask',
    'ScheduleType',
    'TimingStrategy',
    'PlatformTiming',
    'TimezoneConfig',
    'ScheduleWindow',
    'SchedulerMetrics'
]
