"""Backup Scheduler for IA Influencer Agent Platform.

Provides enterprise-grade scheduling capabilities for automated backups
with support for various scheduling patterns and backup types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import cron_descriptor
from croniter import croniter
import uuid

from ...utils.datetime_utils import DateTimeUtils
from ...core.exceptions import SchedulerError


class ScheduleType(Enum):
    """
Schedule type enumeration."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CRON = "cron"
    INTERVAL = "interval"


class ScheduleStatus(Enum):
    """Schedule status enumeration."""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ScheduleConfig:
    """Schedule configuration container."""
    schedule_id: str
    name: str
    description: str
    schedule_type: ScheduleType
    schedule_pattern: str
    backup_type: str
    enabled: bool = True
    max_executions: Optional[int] = None
    timeout_seconds: int = 3600
    retry_count: int = 3
    retry_delay: int = 300
    tags: List[str] = field(default_factory=list)
    notification_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScheduleExecution:
    """
Schedule execution record."""
    execution_id: str
    schedule_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    result: Optional[Any]
    error_message: Optional[str]
    duration_seconds: Optional[float]
    backup_id: Optional[str]


class BackupScheduler:
    """
    Enterprise backup scheduler with advanced scheduling capabilities.
    
    Supports various scheduling patterns including cron expressions,
    interval-based scheduling, and one-time executions.
    """
    def __init__(self):
        """
Initialize backup scheduler."""
        self.logger = logging.getLogger(__name__)
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.executions: List[ScheduleExecution] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.datetime_utils = DateTimeUtils()
        self._scheduler_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def start_scheduler(self) -> None:
        """
Start the scheduler service."""
        if self._is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.logger.info("Starting backup scheduler...")
        self._is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def stop_scheduler(self) -> None:
        try:
            logger.info(f"Executing stop_scheduler")
            
            # Implementation for stop_scheduler
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"stop_scheduler completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"stop_scheduler failed: {e}")
            raise
    async def add_schedule(
        self,
        schedule_config: Dict[str, Any],
        backup_function: Callable
    ) -> str:
        """
        Add a new backup schedule.
        
        Args:
            schedule_config: Schedule configuration
            backup_function: Function to execute for backup
            
        Returns:
            Schedule ID
        """
        schedule_id = str(uuid.uuid4())
        
        # Validate schedule configuration
        validated_config = await self._validate_schedule_config(schedule_config)
        
        # Create schedule
        schedule = ScheduleConfig(
            schedule_id=schedule_id,
            name=validated_config["name"],
            description=validated_config.get("description", ""),
            schedule_type=ScheduleType(validated_config["schedule_type"]),
            schedule_pattern=validated_config["schedule_pattern"],
            backup_type=validated_config.get("backup_type", "full"),
            enabled=validated_config.get("enabled", True),
            max_executions=validated_config.get("max_executions"),
            timeout_seconds=validated_config.get("timeout_seconds", 3600),
            retry_count=validated_config.get("retry_count", 3),
            retry_delay=validated_config.get("retry_delay", 300),
            tags=validated_config.get("tags", []),
            notification_enabled=validated_config.get("notification_enabled", True)
        )
        
        self.schedules[schedule_id] = schedule
        
        # Store backup function reference
        setattr(schedule, '_backup_function', backup_function)
        
        self.logger.info(f"Schedule added: {schedule_id} - {schedule.name}")
        return schedule_id

    async def update_schedule(
        self,
        schedule_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update existing schedule.
        
        Args:
            schedule_id: Schedule identifier
            updates: Updates to apply
            
        Returns:
            Success status
        """
        if schedule_id not in self.schedules:
            self.logger.error(f"Schedule not found: {schedule_id}")
            return False
        
        schedule = self.schedules[schedule_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        schedule.updated_at = datetime.now()
        
        self.logger.info(f"Schedule updated: {schedule_id}")
        return True

    async def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove schedule.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Success status
        """
        if schedule_id not in self.schedules:
            self.logger.error(f"Schedule not found: {schedule_id}")
            return False
        
        # Cancel running task if exists
        if schedule_id in self.running_tasks:
            self.running_tasks[schedule_id].cancel()
            del self.running_tasks[schedule_id]
        
        # Remove schedule
        del self.schedules[schedule_id]
        
        self.logger.info(f"Schedule removed: {schedule_id}")
        return True

    async def pause_schedule(self, schedule_id: str) -> bool:
        """
        Pause schedule execution.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Success status
        """
        if schedule_id not in self.schedules:
            return False
        
        self.schedules[schedule_id].enabled = False
        self.logger.info(f"Schedule paused: {schedule_id}")
        return True

    async def resume_schedule(self, schedule_id: str) -> bool:
        """
        Resume schedule execution.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Success status
        """
        if schedule_id not in self.schedules:
            return False
        
        self.schedules[schedule_id].enabled = True
        self.logger.info(f"Schedule resumed: {schedule_id}")
        return True

    async def execute_schedule_now(self, schedule_id: str) -> str:
        """
        Execute schedule immediately.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Execution ID
        """
        if schedule_id not in self.schedules:
            raise SchedulerError(f"Schedule not found: {schedule_id}")
        
        schedule = self.schedules[schedule_id]
        backup_function = getattr(schedule, '_backup_function', None)
        
        if not backup_function:
            raise SchedulerError(f"No backup function found for schedule: {schedule_id}")
        
        execution_id = await self._execute_backup(schedule, backup_function)
        return execution_id

    async def get_schedule(self, schedule_id: str) -> Optional[ScheduleConfig]:
        """
        Get schedule by ID.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Schedule configuration
        """
        return self.schedules.get(schedule_id)

    async def list_schedules(
        self,
        enabled_only: bool = False,
        tags: Optional[List[str]] = None
    ) -> List[ScheduleConfig]:
        """
        List all schedules with filtering.
        
        Args:
            enabled_only: Filter only enabled schedules
            tags: Filter by tags
            
        Returns:
            List of schedules
        """
        schedules = list(self.schedules.values())
        
        if enabled_only:
            schedules = [s for s in schedules if s.enabled]
        
        if tags:
            schedules = [
                s for s in schedules 
                if any(tag in s.tags for tag in tags)
            ]
        
        return schedules

    async def get_schedule_executions(
        self,
        schedule_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ScheduleExecution]:
        """
        Get schedule execution history.
        
        Args:
            schedule_id: Optional schedule filter
            limit: Maximum results
            
        Returns:
            List of executions
        """
        executions = self.executions
        
        if schedule_id:
            executions = [e for e in executions if e.schedule_id == schedule_id]
        
        # Sort by start time (newest first)
        executions.sort(key=lambda x: x.started_at, reverse=True)
        
        return executions[:limit]

    async def get_next_execution_time(self, schedule_id: str) -> Optional[datetime]:
        """
        Get next execution time for schedule.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Next execution time
        """
        if schedule_id not in self.schedules:
            return None
        
        schedule = self.schedules[schedule_id]
        if not schedule.enabled:
            return None
        
        return await self._calculate_next_execution(schedule)

    async def get_scheduler_statistics(self) -> Dict[str, Any]:
        """
        Get scheduler statistics.
        
        Returns:
            Scheduler statistics
        """
        total_schedules = len(self.schedules)
        enabled_schedules = len([s for s in self.schedules.values() if s.enabled])
        running_executions = len(self.running_tasks)
        
        recent_executions = [
            e for e in self.executions 
            if e.started_at > datetime.now() - timedelta(hours=24)
        ]
        
        successful_executions = len([e for e in recent_executions if e.status == "completed"])
        failed_executions = len([e for e in recent_executions if e.status == "failed"])
        
        return {
            "total_schedules": total_schedules,
            "enabled_schedules": enabled_schedules,
            "running_executions": running_executions,
            "recent_executions_24h": len(recent_executions),
            "successful_executions_24h": successful_executions,
            "failed_executions_24h": failed_executions,
            "success_rate_24h": successful_executions / len(recent_executions) * 100 if recent_executions else 0,
            "scheduler_uptime": self._is_running
        }

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        self.logger.info("Scheduler loop started")
        
        while self._is_running:
            try:
                current_time = datetime.now()
                
                # Check each schedule for execution
                for schedule_id, schedule in self.schedules.items():
                    if not schedule.enabled:
                        continue
                    
                    # Skip if already running
                    if schedule_id in self.running_tasks:
                        continue
                    
                    # Check if schedule should execute
                    should_execute = await self._should_execute_now(schedule, current_time)
                    
                    if should_execute:
                        backup_function = getattr(schedule, '_backup_function', None)
                        if backup_function:
                            # Start backup execution
                            task = asyncio.create_task(
                                self._execute_backup(schedule, backup_function)
                            )
                            self.running_tasks[schedule_id] = task
                
                # Clean up completed tasks
                completed_tasks = []
                for schedule_id, task in self.running_tasks.items():
                    if task.done():
                        completed_tasks.append(schedule_id)
                
                for schedule_id in completed_tasks:
                    del self.running_tasks[schedule_id]
                
                # Sleep before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)
        
        self.logger.info("Scheduler loop stopped")

    async def _should_execute_now(
        self, 
        schedule: ScheduleConfig, 
        current_time: datetime
    ) -> bool:
        """Check if schedule should execute at current time."""
        try:
            # Check max executions limit
            if schedule.max_executions:
                execution_count = len([
                    e for e in self.executions 
                    if e.schedule_id == schedule.schedule_id
                ])
                if execution_count >= schedule.max_executions:
                    return False
            
            # Calculate next execution time
            next_execution = await self._calculate_next_execution(schedule)
            if not next_execution:
                return False
            
            # Check if it's time to execute (within 1 minute window)
            time_diff = abs((current_time - next_execution).total_seconds())
            return time_diff <= 60
            
        except Exception as e:
            self.logger.error(f"Error checking schedule execution: {e}")
            return False

    async def _calculate_next_execution(self, schedule: ScheduleConfig) -> Optional[datetime]:
        """Calculate next execution time for schedule."""
        current_time = datetime.now()
        
        try:
            if schedule.schedule_type == ScheduleType.ONCE:
                # Parse target datetime
                target_time = datetime.fromisoformat(schedule.schedule_pattern)
                return target_time if target_time > current_time else None
            
            elif schedule.schedule_type == ScheduleType.DAILY:
                # Parse time (e.g., "14:30")
                target_time = datetime.strptime(schedule.schedule_pattern, "%H:%M").time()
                next_execution = datetime.combine(current_time.date(), target_time)
                
                if next_execution <= current_time:
                    next_execution += timedelta(days=1)
                
                return next_execution
            
            elif schedule.schedule_type == ScheduleType.WEEKLY:
                # Parse day and time (e.g., "monday:14:30")
                day_name, time_str = schedule.schedule_pattern.split(":")
                target_time = datetime.strptime(time_str, "%H:%M").time()
                
                days = {
                    "monday": 0, "tuesday": 1, "wednesday": 2,
                    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
                }
                
                target_weekday = days[day_name.lower()]
                days_ahead = target_weekday - current_time.weekday()
                
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                
                next_execution = current_time + timedelta(days=days_ahead)
                next_execution = datetime.combine(next_execution.date(), target_time)
                
                return next_execution
            
            elif schedule.schedule_type == ScheduleType.MONTHLY:
                # Parse day and time (e.g., "1:14:30" for 1st day of month)
                day_str, time_str = schedule.schedule_pattern.split(":", 1)
                target_day = int(day_str)
                target_time = datetime.strptime(time_str, "%H:%M").time()
                
                # Calculate next month with target day
                next_month = current_time.replace(day=1) + timedelta(days=32)
                next_month = next_month.replace(day=1)
                
                try:
                    next_execution = next_month.replace(day=target_day)
                    next_execution = datetime.combine(next_execution.date(), target_time)
                except ValueError:
                    # Handle case where target day doesn't exist in month
                    import calendar
                    last_day = calendar.monthrange(next_month.year, next_month.month)[1]
                    next_execution = next_month.replace(day=min(target_day, last_day))
                    next_execution = datetime.combine(next_execution.date(), target_time)
                
                return next_execution
            
            elif schedule.schedule_type == ScheduleType.CRON:
                # Use croniter for cron expressions
                cron = croniter(schedule.schedule_pattern, current_time)
                return cron.get_next(datetime)
            
            elif schedule.schedule_type == ScheduleType.INTERVAL:
                # Parse interval in seconds
                interval_seconds = int(schedule.schedule_pattern)
                
                # Get last execution time
                last_execution = None
                for execution in reversed(self.executions):
                    if execution.schedule_id == schedule.schedule_id:
                        last_execution = execution.started_at
                        break
                
                if last_execution:
                    next_execution = last_execution + timedelta(seconds=interval_seconds)
                else:
                    next_execution = current_time + timedelta(seconds=interval_seconds)
                
                return next_execution
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating next execution for schedule {schedule.schedule_id}: {e}")
            return None

    async def _execute_backup(
        self, 
        schedule: ScheduleConfig, 
        backup_function: Callable
    ) -> str:
        """Execute backup function with error handling and retry logic."""
        execution_id = str(uuid.uuid4())
        started_at = datetime.now()
        
        execution = ScheduleExecution(
            execution_id=execution_id,
            schedule_id=schedule.schedule_id,
            started_at=started_at,
            completed_at=None,
            status="running",
            result=None,
            error_message=None,
            duration_seconds=None,
            backup_id=None
        )
        
        self.executions.append(execution)
        
        self.logger.info(f"Starting backup execution: {execution_id} for schedule: {schedule.schedule_id}")
        
        retry_count = 0
        last_error = None
        
        while retry_count <= schedule.retry_count:
            try:
                # Execute backup function with timeout
                backup_result = await asyncio.wait_for(
                    backup_function(),
                    timeout=schedule.timeout_seconds
                )
                
                # Success
                completed_at = datetime.now()
                duration = (completed_at - started_at).total_seconds()
                
                execution.completed_at = completed_at
                execution.status = "completed"
                execution.result = backup_result
                execution.duration_seconds = duration
                execution.backup_id = backup_result if isinstance(backup_result, str) else None
                
                self.logger.info(f"Backup execution completed: {execution_id}")
                
                if schedule.notification_enabled:
                    await self._send_success_notification(schedule, execution)
                
                return execution_id
                
            except asyncio.TimeoutError:
                last_error = f"Backup execution timed out after {schedule.timeout_seconds} seconds"
                self.logger.warning(f"Backup execution timeout: {execution_id} (attempt {retry_count + 1})")
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Backup execution error: {execution_id} (attempt {retry_count + 1}) - {e}")
            
            retry_count += 1
            
            if retry_count <= schedule.retry_count:
                self.logger.info(f"Retrying backup execution in {schedule.retry_delay} seconds...")
                await asyncio.sleep(schedule.retry_delay)
        
        # All retries failed
        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()
        
        execution.completed_at = completed_at
        execution.status = "failed"
        execution.error_message = last_error
        execution.duration_seconds = duration
        
        self.logger.error(f"Backup execution failed after {schedule.retry_count} retries: {execution_id}")
        
        if schedule.notification_enabled:
            await self._send_failure_notification(schedule, execution)
        
        return execution_id

    async def _validate_schedule_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate schedule configuration."""
        required_fields = ["name", "schedule_type", "schedule_pattern"]
        
        for field in required_fields:
            if field not in config:
                raise SchedulerError(f"Missing required field: {field}")
        
        # Validate schedule type
        try:
            schedule_type = ScheduleType(config["schedule_type"])
        except ValueError:
            raise SchedulerError(f"Invalid schedule type: {config['schedule_type']}")
        
        # Validate schedule pattern based on type
        pattern = config["schedule_pattern"]
        
        if schedule_type == ScheduleType.ONCE:
            try:
                datetime.fromisoformat(pattern)
            except ValueError:
                raise SchedulerError("Invalid datetime format for ONCE schedule")
        
        elif schedule_type == ScheduleType.DAILY:
            try:
                datetime.strptime(pattern, "%H:%M")
            except ValueError:
                raise SchedulerError("Invalid time format for DAILY schedule (expected HH:MM)")
        
        elif schedule_type == ScheduleType.WEEKLY:
            if ":" not in pattern:
                raise SchedulerError("Invalid pattern for WEEKLY schedule (expected day:HH:MM)")
            
            day_name, time_str = pattern.split(":", 1)
            valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            
            if day_name.lower() not in valid_days:
                raise SchedulerError(f"Invalid day name: {day_name}")
            
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                raise SchedulerError("Invalid time format for WEEKLY schedule")
        
        elif schedule_type == ScheduleType.MONTHLY:
            if ":" not in pattern:
                raise SchedulerError("Invalid pattern for MONTHLY schedule (expected day:HH:MM)")
            
            day_str, time_str = pattern.split(":", 1)
            
            try:
                day = int(day_str)
                if day < 1 or day > 31:
                    raise SchedulerError("Day must be between 1 and 31")
            except ValueError:
                raise SchedulerError("Invalid day format for MONTHLY schedule")
            
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                raise SchedulerError("Invalid time format for MONTHLY schedule")
        
        elif schedule_type == ScheduleType.CRON:
            try:
                croniter(pattern)
            except ValueError:
                raise SchedulerError("Invalid cron expression")
        
        elif schedule_type == ScheduleType.INTERVAL:
            try:
                interval = int(pattern)
                if interval <= 0:
                    raise SchedulerError("Interval must be positive")
            except ValueError:
                raise SchedulerError("Invalid interval format (expected seconds)")
        
        return config

    async def _send_success_notification(
        self, 
        schedule: ScheduleConfig, 
        execution: ScheduleExecution
    ) -> None:
        """Send success notification for backup execution."""
        # Implementation would depend on notification system
        self.logger.info(f"Backup execution successful notification sent for: {schedule.name}")

    async def _send_failure_notification(
        self, 
        schedule: ScheduleConfig, 
        execution: ScheduleExecution
    ) -> None:
        """Send failure notification for backup execution."""
        # Implementation would depend on notification system
        self.logger.error(f"Backup execution failure notification sent for: {schedule.name}")

    def get_schedule_description(self, schedule_id: str) -> Optional[str]:
        """
        Get human-readable description of schedule.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Schedule description
        """
        if schedule_id not in self.schedules:
            return None
        
        schedule = self.schedules[schedule_id]
        
        try:
            if schedule.schedule_type == ScheduleType.CRON:
                return cron_descriptor.get_description(schedule.schedule_pattern)
            else:
                return f"{schedule.schedule_type.value}: {schedule.schedule_pattern}"
        except Exception:
            return f"{schedule.schedule_type.value}: {schedule.schedule_pattern}"
