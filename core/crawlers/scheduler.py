"""
Crawling Scheduler System
========================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
Unauthorized use, copying or distribution prohibited.

Professional scheduling system for automated content monitoring.
Manages periodic crawling tasks, priority scheduling, load balancing,
and intelligent resource allocation across multiple platforms.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import cron_descriptor
from croniter import croniter
import json
import redis

logger = logging.getLogger(__name__)

class ScheduleType(Enum):
    """Types of scheduling supported."""
    IMMEDIATE = "immediate"
    PERIODIC = "periodic"
    CRON = "cron"
    TRIGGERED = "triggered"

class Priority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

@dataclass
class ScheduledTask:
    """Represents a scheduled crawling task."""
    
    schedule_id: str
    name: str
    platform: str
    target_urls: List[str]
    fingerprints: List[str]
    
    # Scheduling configuration
    schedule_type: ScheduleType
    priority: Priority = Priority.MEDIUM
    cron_expression: Optional[str] = None
    interval_minutes: Optional[int] = None
    
    # Execution tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    execution_count: int = 0
    failure_count: int = 0
    
    # Configuration
    enabled: bool = True
    max_failures: int = 3
    timeout_minutes: int = 30
    retry_delay_minutes: int = 5
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def is_due(self) -> bool:
        """Check if task is due for execution."""
        if not self.enabled:
            return False
        
        if not self.next_execution:
            return True
        
        return datetime.utcnow() >= self.next_execution
    
    def calculate_next_execution(self) -> Optional[datetime]:
        """Calculate next execution time based on schedule type."""
        
        now = datetime.utcnow()
        
        if self.schedule_type == ScheduleType.IMMEDIATE:
            return now
        
        elif self.schedule_type == ScheduleType.PERIODIC and self.interval_minutes:
            return now + timedelta(minutes=self.interval_minutes)
        
        elif self.schedule_type == ScheduleType.CRON and self.cron_expression:
            cron = croniter(self.cron_expression, now)
            return cron.get_next(datetime)
        
        elif self.schedule_type == ScheduleType.TRIGGERED:
            # Triggered tasks don't have automatic next execution
            return None
        
        return None
    
    def mark_executed(self, success: bool = True):
        """Mark task as executed and update counters."""
        
        self.last_execution = datetime.utcnow()
        self.execution_count += 1
        
        if not success:
            self.failure_count += 1
        else:
            # Reset failure count on success
            self.failure_count = 0
        
        # Calculate next execution
        self.next_execution = self.calculate_next_execution()
        
        # Disable if too many failures
        if self.failure_count >= self.max_failures:
            self.enabled = False
            logger.warning("Task %s disabled due to %d failures", self.schedule_id, self.failure_count)

class CrawlingScheduler:
    """
    Advanced scheduling system for automated content monitoring.
    
    Manages periodic crawling tasks, resource allocation, and intelligent
    scheduling based on priority, platform load, and historical performance.
    """
    
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.redis_client = coordinator.redis_client
        
        # Scheduled tasks storage
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.task_execution_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Scheduler state
        self.is_running = False
        self.scheduler_loop_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.scheduler_interval_seconds = 30
        self.max_concurrent_scheduled_tasks = 10
        self.load_balancing_enabled = True
        
        # Platform load tracking
        self.platform_load: Dict[str, int] = {}
        self.platform_performance: Dict[str, Dict[str, float]] = {}
        
        logger.info("CrawlingScheduler initialized")
    
    async def start(self):
        """Start the scheduling system."""
        
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        
        # Load persisted schedules
        await self._load_persisted_schedules()
        
        # Start scheduler loop
        self.scheduler_loop_task = asyncio.create_task(self._scheduler_loop())
        
        logger.info("CrawlingScheduler started with %d scheduled tasks", len(self.scheduled_tasks))
    
    async def stop(self):
        """Stop the scheduling system."""
        
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel scheduler loop
        if self.scheduler_loop_task:
            self.scheduler_loop_task.cancel()
            try:
                await self.scheduler_loop_task
            except asyncio.CancelledError:
                pass
        
        # Persist current schedules
        await self._persist_schedules()
        
        logger.info("CrawlingScheduler stopped")
    
    async def add_scheduled_task(
        self,
        name: str,
        platform: str,
        target_urls: List[str],
        fingerprints: List[str],
        schedule_type: ScheduleType,
        priority: Priority = Priority.MEDIUM,
        cron_expression: Optional[str] = None,
        interval_minutes: Optional[int] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a new scheduled crawling task.
        
        Args:
            name: Human-readable task name
            platform: Target platform
            target_urls: URLs to monitor
            fingerprints: Protected content fingerprints
            schedule_type: Type of scheduling
            priority: Task priority
            cron_expression: Cron expression for CRON schedule type
            interval_minutes: Interval for PERIODIC schedule type
            conditions: Additional execution conditions
            
        Returns:
            Schedule ID for the created task
        """
        
        # Validate parameters
        if schedule_type == ScheduleType.CRON and not cron_expression:
            raise ValueError("Cron expression required for CRON schedule type")
        
        if schedule_type == ScheduleType.PERIODIC and not interval_minutes:
            raise ValueError("Interval required for PERIODIC schedule type")
        
        if cron_expression:
            try:
                # Validate cron expression
                croniter(cron_expression)
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {e}")
        
        # Generate schedule ID
        schedule_id = f"sched_{platform}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(self.scheduled_tasks)}"
        
        # Create scheduled task
        task = ScheduledTask(
            schedule_id=schedule_id,
            name=name,
            platform=platform,
            target_urls=target_urls,
            fingerprints=fingerprints,
            schedule_type=schedule_type,
            priority=priority,
            cron_expression=cron_expression,
            interval_minutes=interval_minutes,
            conditions=conditions or {}
        )
        
        # Set initial next execution
        task.next_execution = task.calculate_next_execution()
        
        # Store task
        self.scheduled_tasks[schedule_id] = task
        self.task_execution_history[schedule_id] = []
        
        # Persist to Redis
        await self._persist_task(task)
        
        logger.info("Added scheduled task %s: %s (%s)", schedule_id, name, schedule_type.value)
        
        return schedule_id
    
    async def remove_scheduled_task(self, schedule_id: str) -> bool:
        """Remove a scheduled task."""
        
        if schedule_id not in self.scheduled_tasks:
            return False
        
        # Remove from memory
        del self.scheduled_tasks[schedule_id]
        if schedule_id in self.task_execution_history:
            del self.task_execution_history[schedule_id]
        
        # Remove from Redis
        try:
            self.redis_client.delete(f"scheduled_task:{schedule_id}")
        except Exception as e:
            logger.error("Error removing task from Redis: %s", str(e))
        
        logger.info("Removed scheduled task: %s", schedule_id)
        return True
    
    async def update_scheduled_task(
        self,
        schedule_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update an existing scheduled task."""
        
        if schedule_id not in self.scheduled_tasks:
            return False
        
        task = self.scheduled_tasks[schedule_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Recalculate next execution if schedule changed
        if any(key in updates for key in ['cron_expression', 'interval_minutes', 'schedule_type']):
            task.next_execution = task.calculate_next_execution()
        
        # Persist changes
        await self._persist_task(task)
        
        logger.info("Updated scheduled task: %s", schedule_id)
        return True
    
    async def trigger_task_execution(self, schedule_id: str) -> Optional[str]:
        """Manually trigger execution of a scheduled task."""
        
        if schedule_id not in self.scheduled_tasks:
            return None
        
        task = self.scheduled_tasks[schedule_id]
        
        # Submit task for immediate execution
        crawler_task_id = await self._execute_scheduled_task(task, manual_trigger=True)
        
        logger.info("Manually triggered execution of task %s", schedule_id)
        
        return crawler_task_id
    
    async def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get list of all scheduled tasks with their status."""
        
        tasks = []
        
        for task in self.scheduled_tasks.values():
            task_info = {
                'schedule_id': task.schedule_id,
                'name': task.name,
                'platform': task.platform,
                'schedule_type': task.schedule_type.value,
                'priority': task.priority.value,
                'enabled': task.enabled,
                'created_at': task.created_at.isoformat(),
                'last_execution': task.last_execution.isoformat() if task.last_execution else None,
                'next_execution': task.next_execution.isoformat() if task.next_execution else None,
                'execution_count': task.execution_count,
                'failure_count': task.failure_count,
                'target_urls_count': len(task.target_urls),
                'fingerprints_count': len(task.fingerprints)
            }
            
            # Add schedule description
            if task.cron_expression:
                try:
                    task_info['schedule_description'] = cron_descriptor.get_description(task.cron_expression)
                except:
                    task_info['schedule_description'] = task.cron_expression
            elif task.interval_minutes:
                task_info['schedule_description'] = f"Every {task.interval_minutes} minutes"
            else:
                task_info['schedule_description'] = task.schedule_type.value
            
            tasks.append(task_info)
        
        return tasks
    
    async def get_scheduler_statistics(self) -> Dict[str, Any]:
        """Get scheduler performance statistics."""
        
        total_tasks = len(self.scheduled_tasks)
        enabled_tasks = sum(1 for task in self.scheduled_tasks.values() if task.enabled)
        failed_tasks = sum(1 for task in self.scheduled_tasks.values() if task.failure_count >= task.max_failures)
        
        # Platform distribution
        platform_distribution = {}
        for task in self.scheduled_tasks.values():
            platform_distribution[task.platform] = platform_distribution.get(task.platform, 0) + 1
        
        # Execution statistics
        total_executions = sum(task.execution_count for task in self.scheduled_tasks.values())
        total_failures = sum(task.failure_count for task in self.scheduled_tasks.values())
        
        return {
            'total_scheduled_tasks': total_tasks,
            'enabled_tasks': enabled_tasks,
            'disabled_tasks': total_tasks - enabled_tasks,
            'failed_tasks': failed_tasks,
            'platform_distribution': platform_distribution,
            'total_executions': total_executions,
            'total_failures': total_failures,
            'success_rate': (total_executions - total_failures) / total_executions if total_executions > 0 else 0,
            'platform_load': self.platform_load.copy(),
            'is_running': self.is_running
        }
    
    async def _scheduler_loop(self):
        """Main scheduler loop that processes due tasks."""
        
        while self.is_running:
            try:
                # Find due tasks
                due_tasks = [
                    task for task in self.scheduled_tasks.values()
                    if task.enabled and task.is_due()
                ]
                
                if due_tasks:
                    # Sort by priority and last execution time
                    due_tasks.sort(key=lambda t: (t.priority.value, t.last_execution or datetime.min))
                    
                    # Limit concurrent executions
                    current_running = len(self.coordinator.running_tasks)
                    available_slots = min(
                        self.max_concurrent_scheduled_tasks,
                        self.coordinator.config.concurrent_crawlers - current_running
                    )
                    
                    # Execute tasks up to available capacity
                    for task in due_tasks[:available_slots]:
                        if self._check_execution_conditions(task):
                            asyncio.create_task(self._execute_scheduled_task(task))
                
                # Update platform load tracking
                await self._update_platform_load()
                
                # Cleanup old execution history
                await self._cleanup_execution_history()
                
                # Wait before next iteration
                await asyncio.sleep(self.scheduler_interval_seconds)
                
            except Exception as e:
                logger.error("Error in scheduler loop: %s", str(e))
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _execute_scheduled_task(self, task: ScheduledTask, manual_trigger: bool = False) -> Optional[str]:
        """Execute a scheduled task."""
        
        try:
            # Check platform load balancing
            if self.load_balancing_enabled and not manual_trigger:
                if self._is_platform_overloaded(task.platform):
                    logger.info("Delaying task %s due to platform load", task.schedule_id)
                    return None
            
            # Submit crawler task
            from .config import CrawlerType
            platform_type = CrawlerType(task.platform.lower())
            
            crawler_task_id = await self.coordinator.submit_crawling_task(
                platform=platform_type,
                target_urls=task.target_urls,
                content_fingerprints=task.fingerprints,
                priority=task.priority.value
            )
            
            # Record execution
            execution_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'crawler_task_id': crawler_task_id,
                'manual_trigger': manual_trigger,
                'platform_load': self.platform_load.get(task.platform, 0)
            }
            
            # Update task
            task.mark_executed(success=True)
            
            # Store execution history
            if task.schedule_id not in self.task_execution_history:
                self.task_execution_history[task.schedule_id] = []
            
            self.task_execution_history[task.schedule_id].append(execution_record)
            
            # Keep only last 100 execution records
            if len(self.task_execution_history[task.schedule_id]) > 100:
                self.task_execution_history[task.schedule_id] = self.task_execution_history[task.schedule_id][-100:]
            
            # Update platform load
            self.platform_load[task.platform] = self.platform_load.get(task.platform, 0) + 1
            
            # Persist updated task
            await self._persist_task(task)
            
            logger.info("Executed scheduled task %s (crawler task: %s)", task.schedule_id, crawler_task_id)
            
            return crawler_task_id
            
        except Exception as e:
            logger.error("Error executing scheduled task %s: %s", task.schedule_id, str(e))
            
            # Mark as failed
            task.mark_executed(success=False)
            await self._persist_task(task)
            
            return None
    
    def _check_execution_conditions(self, task: ScheduledTask) -> bool:
        """Check if task execution conditions are met."""
        
        conditions = task.conditions
        
        # Check time-based conditions
        if 'time_window' in conditions:
            time_window = conditions['time_window']
            current_hour = datetime.utcnow().hour
            
            start_hour = time_window.get('start_hour', 0)
            end_hour = time_window.get('end_hour', 23)
            
            if not (start_hour <= current_hour <= end_hour):
                return False
        
        # Check platform load conditions
        if 'max_platform_load' in conditions:
            max_load = conditions['max_platform_load']
            current_load = self.platform_load.get(task.platform, 0)
            
            if current_load >= max_load:
                return False
        
        # Check minimum interval since last execution
        if 'min_interval_minutes' in conditions and task.last_execution:
            min_interval = timedelta(minutes=conditions['min_interval_minutes'])
            if datetime.utcnow() - task.last_execution < min_interval:
                return False
        
        return True
    
    def _is_platform_overloaded(self, platform: str) -> bool:
        """Check if platform is currently overloaded."""
        
        current_load = self.platform_load.get(platform, 0)
        
        # Define load thresholds per platform
        load_thresholds = {
            'youtube': 5,
            'tiktok': 3,
            'instagram': 4,
            'twitter': 6,
            'generic_web': 2
        }
        
        threshold = load_thresholds.get(platform, 3)
        return current_load >= threshold
    
    async def _update_platform_load(self):
        """Update platform load tracking based on running tasks."""
        
        # Reset load counters
        self.platform_load = {}
        
        # Count running tasks per platform
        for task in self.coordinator.running_tasks.values():
            platform = task.platform.value
            self.platform_load[platform] = self.platform_load.get(platform, 0) + 1
    
    async def _cleanup_execution_history(self):
        """Clean up old execution history records."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        for schedule_id, history in self.task_execution_history.items():
            # Remove records older than 30 days
            self.task_execution_history[schedule_id] = [
                record for record in history
                if datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')) > cutoff_date
            ]
    
    async def _persist_task(self, task: ScheduledTask):
        """Persist scheduled task to Redis."""
        
        try:
            task_data = {
                'schedule_id': task.schedule_id,
                'name': task.name,
                'platform': task.platform,
                'target_urls': task.target_urls,
                'fingerprints': task.fingerprints,
                'schedule_type': task.schedule_type.value,
                'priority': task.priority.value,
                'cron_expression': task.cron_expression,
                'interval_minutes': task.interval_minutes,
                'created_at': task.created_at.isoformat(),
                'last_execution': task.last_execution.isoformat() if task.last_execution else None,
                'next_execution': task.next_execution.isoformat() if task.next_execution else None,
                'execution_count': task.execution_count,
                'failure_count': task.failure_count,
                'enabled': task.enabled,
                'max_failures': task.max_failures,
                'timeout_minutes': task.timeout_minutes,
                'retry_delay_minutes': task.retry_delay_minutes,
                'conditions': task.conditions
            }
            
            self.redis_client.setex(
                f"scheduled_task:{task.schedule_id}",
                86400 * 30,  # 30 days
                json.dumps(task_data)
            )
            
        except Exception as e:
            logger.error("Error persisting task to Redis: %s", str(e))
    
    async def _persist_schedules(self):
        """Persist all scheduled tasks."""
        
        for task in self.scheduled_tasks.values():
            await self._persist_task(task)
    
    async def _load_persisted_schedules(self):
        """Load scheduled tasks from Redis."""
        
        try:
            # Find all scheduled task keys
            keys = self.redis_client.keys("scheduled_task:*")
            
            for key in keys:
                try:
                    task_data = json.loads(self.redis_client.get(key))
                    
                    # Reconstruct ScheduledTask object
                    task = ScheduledTask(
                        schedule_id=task_data['schedule_id'],
                        name=task_data['name'],
                        platform=task_data['platform'],
                        target_urls=task_data['target_urls'],
                        fingerprints=task_data['fingerprints'],
                        schedule_type=ScheduleType(task_data['schedule_type']),
                        priority=Priority(task_data['priority']),
                        cron_expression=task_data.get('cron_expression'),
                        interval_minutes=task_data.get('interval_minutes'),
                        created_at=datetime.fromisoformat(task_data['created_at']),
                        last_execution=datetime.fromisoformat(task_data['last_execution']) if task_data.get('last_execution') else None,
                        next_execution=datetime.fromisoformat(task_data['next_execution']) if task_data.get('next_execution') else None,
                        execution_count=task_data.get('execution_count', 0),
                        failure_count=task_data.get('failure_count', 0),
                        enabled=task_data.get('enabled', True),
                        max_failures=task_data.get('max_failures', 3),
                        timeout_minutes=task_data.get('timeout_minutes', 30),
                        retry_delay_minutes=task_data.get('retry_delay_minutes', 5),
                        conditions=task_data.get('conditions', {})
                    )
                    
                    self.scheduled_tasks[task.schedule_id] = task
                    self.task_execution_history[task.schedule_id] = []
                    
                except Exception as e:
                    logger.error("Error loading scheduled task from %s: %s", key, str(e))
            
            logger.info("Loaded %d scheduled tasks from Redis", len(self.scheduled_tasks))
            
        except Exception as e:
            logger.error("Error loading persisted schedules: %s", str(e))
