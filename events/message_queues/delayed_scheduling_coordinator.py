"""Delayed Scheduling Coordinator Module

Advanced delayed message scheduling with precision timing and business calendar awareness
for the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Delayed Scheduling Coordinator architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import heapq
from collections import defaultdict
import calendar

from ..core.exceptions import MessageQueueError
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Types of message scheduling"""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    CRON_BASED = "cron_based"
    BUSINESS_CALENDAR = "business_calendar"
    CONDITIONAL = "conditional"


class RecurrencePattern(Enum):
    """Recurrence patterns for scheduled messages"""
    MINUTELY = "minutely"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BusinessCalendarEvent(Enum):
    """Business calendar events for Ainflue"""
    CONTENT_DEADLINE = "content_deadline"
    PAYMENT_CYCLE = "payment_cycle"
    ANALYTICS_REPORT = "analytics_report"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION_FOLLOWUP = "collaboration_followup"
    CREATOR_PAYOUT = "creator_payout"
    PLATFORM_MAINTENANCE = "platform_maintenance"


@dataclass
class ScheduledMessage:
    """Scheduled message with timing metadata"""
    id: str = field(default_factory=lambda: str(uuid4()))
    schedule_type: ScheduleType = ScheduleType.ONE_TIME
    scheduled_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = field(default_factory=dict)
    queue_name: str = ""
    priority: int = 5
    
    # Recurrence settings
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: int = 1
    recurrence_end: Optional[datetime] = None
    max_executions: Optional[int] = None
    execution_count: int = 0
    
    # Cron settings
    cron_expression: Optional[str] = None
    
    # Business calendar settings
    business_event: Optional[BusinessCalendarEvent] = None
    business_context: Dict[str, Any] = field(default_factory=dict)
    
    # Conditional settings
    condition_callback: Optional[str] = None
    condition_data: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_executed: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    is_active: bool = True
    
    def __lt__(self, other) -> None:
        """Comparison for heap operations"""
        return self.scheduled_time < other.scheduled_time


@dataclass
class SchedulingMetrics:
    """Scheduling system metrics"""
    total_scheduled: int = 0
    executed_messages: int = 0
    failed_executions: int = 0
    cancelled_schedules: int = 0
    avg_execution_delay: float = 0.0
    precision_accuracy: float = 100.0
    schedule_type_distribution: Dict[str, int] = field(default_factory=dict)
    business_event_distribution: Dict[str, int] = field(default_factory=dict)


class AinflueBusiness:
    """Ainflue Business Scheduling Rules"""
    
    # Business calendar schedules
    BUSINESS_SCHEDULES = {
        # Content management schedules
        BusinessCalendarEvent.CONTENT_DEADLINE: {
            "default_advance_warning": timedelta(hours=24),
            "reminder_intervals": [timedelta(hours=24), timedelta(hours=6), timedelta(hours=1)],
            "priority": 7,
            "queue": "content_management"
        },
        
        # Payment and revenue schedules
        BusinessCalendarEvent.PAYMENT_CYCLE: {
            "recurrence": RecurrencePattern.MONTHLY,
            "execution_day": 1,  # 1st of each month
            "execution_time": "09:00",
            "priority": 9,
            "queue": "payment_processing"
        },
        BusinessCalendarEvent.CREATOR_PAYOUT: {
            "recurrence": RecurrencePattern.MONTHLY,
            "execution_day": 15,  # 15th of each month
            "execution_time": "10:00",
            "priority": 9,
            "queue": "payment_processing"
        },
        
        # Analytics and reporting schedules
        BusinessCalendarEvent.ANALYTICS_REPORT: {
            "recurrence": RecurrencePattern.DAILY,
            "execution_time": "06:00",
            "priority": 4,
            "queue": "analytics_processing"
        },
        
        # SEO optimization schedules
        BusinessCalendarEvent.SEO_OPTIMIZATION: {
            "recurrence": RecurrencePattern.WEEKLY,
            "execution_day": 1,  # Monday
            "execution_time": "08:00",
            "priority": 5,
            "queue": "seo_processing"
        },
        
        # Collaboration management
        BusinessCalendarEvent.COLLABORATION_FOLLOWUP: {
            "default_delay": timedelta(days=7),
            "reminder_intervals": [timedelta(days=7), timedelta(days=3), timedelta(days=1)],
            "priority": 6,
            "queue": "collaboration_management"
        },
        
        # System maintenance
        BusinessCalendarEvent.PLATFORM_MAINTENANCE: {
            "recurrence": RecurrencePattern.WEEKLY,
            "execution_day": 7,  # Sunday
            "execution_time": "02:00",
            "priority": 3,
            "queue": "system_maintenance"
        }
    }
    
    # Timezone settings for global operations
    BUSINESS_TIMEZONES = {
        "default": "UTC",
        "payment_processing": "America/New_York",
        "content_management": "UTC",
        "analytics_processing": "UTC",
        "creator_payouts": "America/Los_Angeles"
    }
    
    # Business hours for scheduling
    BUSINESS_HOURS = {
        "start": "09:00",
        "end": "17:00",
        "timezone": "UTC"
    }


class DelayedSchedulingCoordinator:
    """
    Advanced delayed message scheduling with precision timing
    Supports one-time, recurring, cron-based, and business calendar scheduling
    """
    
    def __init__(self,
                 metrics_collector -> None: Optional[MetricsCollector] = None,
                 encryption_manager -> None: Optional[EncryptionManager] = None) -> None:
        self.metrics = metrics_collector
        self.encryption = encryption_manager
        
        # Scheduling storage
        self.scheduled_messages = []  # Priority queue (heap)
        self.message_registry = {}    # Fast lookup by ID
        self.recurring_schedules = {} # Recurring schedule templates
        
        # Execution tracking
        self.execution_history = {}
        self.failed_executions = {}
        
        # Business calendar
        self.business_calendar = {}
        self.calendar_events = defaultdict(list)
        
        # Condition handlers
        self.condition_handlers = {}
        
        # Metrics
        self.scheduling_metrics = SchedulingMetrics()
        
        # Scheduler state
        self.is_running = False
        self.scheduler_task = None
        self.precision_threshold = 1.0  # 1 second precision
        
        logger.info("Initialized Delayed Scheduling Coordinator")
    
    async def start(self) -> bool:
        """Start the scheduling coordinator"""
        try:
            if self.is_running:
                return True
            
            self.is_running = True
            
            # Initialize business calendar
            await self._initialize_business_calendar()
            
            # Start scheduler loop
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            logger.info("Delayed Scheduling Coordinator started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise MessageQueueError(f"Scheduler startup failed: {str(e)}")
    
    async def stop(self) -> None:
        """Stop the scheduling coordinator"""
        try:
            self.is_running = False
            
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Delayed Scheduling Coordinator stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
    
    async def schedule_one_time_message(self,
                                      scheduled_time: datetime,
                                      payload: Dict[str, Any],
                                      queue_name: str,
                                      priority: int = 5) -> str:
        """Schedule a one-time message"""
        try:
            message = ScheduledMessage(
                schedule_type=ScheduleType.ONE_TIME,
                scheduled_time=scheduled_time,
                payload=payload,
                queue_name=queue_name,
                priority=priority
            )
            
            return await self._add_scheduled_message(message)
            
        except Exception as e:
            logger.error(f"Error scheduling one-time message: {str(e)}")
            raise MessageQueueError(f"One-time scheduling failed: {str(e)}")
    
    async def schedule_recurring_message(self,
                                       start_time: datetime,
                                       pattern: RecurrencePattern,
                                       interval: int,
                                       payload: Dict[str, Any],
                                       queue_name: str,
                                       end_time: Optional[datetime] = None,
                                       max_executions: Optional[int] = None,
                                       priority: int = 5) -> str:
        """Schedule a recurring message"""
        try:
            message = ScheduledMessage(
                schedule_type=ScheduleType.RECURRING,
                scheduled_time=start_time,
                payload=payload,
                queue_name=queue_name,
                priority=priority,
                recurrence_pattern=pattern,
                recurrence_interval=interval,
                recurrence_end=end_time,
                max_executions=max_executions
            )
            
            # Calculate next execution
            message.next_execution = await self._calculate_next_execution(message)
            
            return await self._add_scheduled_message(message)
            
        except Exception as e:
            logger.error(f"Error scheduling recurring message: {str(e)}")
            raise MessageQueueError(f"Recurring scheduling failed: {str(e)}")
    
    async def schedule_cron_message(self,
                                  cron_expression: str,
                                  payload: Dict[str, Any],
                                  queue_name: str,
                                  priority: int = 5) -> str:
        """Schedule a message using cron expression"""
        try:
            # Parse cron expression and calculate next execution
            next_execution = await self._parse_cron_expression(cron_expression)
            
            message = ScheduledMessage(
                schedule_type=ScheduleType.CRON_BASED,
                scheduled_time=next_execution,
                payload=payload,
                queue_name=queue_name,
                priority=priority,
                cron_expression=cron_expression,
                next_execution=next_execution
            )
            
            return await self._add_scheduled_message(message)
            
        except Exception as e:
            logger.error(f"Error scheduling cron message: {str(e)}")
            raise MessageQueueError(f"Cron scheduling failed: {str(e)}")
    
    async def schedule_business_calendar_event(self,
                                             event_type: BusinessCalendarEvent,
                                             target_date: datetime,
                                             payload: Dict[str, Any],
                                             business_context: Dict[str, Any] = None) -> str:
        """Schedule a business calendar event"""
        try:
            # Get business schedule settings
            settings = AinflueBusiness.BUSINESS_SCHEDULES.get(event_type, {})
            
            message = ScheduledMessage(
                schedule_type=ScheduleType.BUSINESS_CALENDAR,
                scheduled_time=target_date,
                payload=payload,
                queue_name=settings.get("queue", "default"),
                priority=settings.get("priority", 5),
                business_event=event_type,
                business_context=business_context or {}
            )
            
            # Set up recurrence if specified
            if "recurrence" in settings:
                message.recurrence_pattern = settings["recurrence"]
                message.next_execution = await self._calculate_business_next_execution(message)
            
            return await self._add_scheduled_message(message)
            
        except Exception as e:
            logger.error(f"Error scheduling business calendar event: {str(e)}")
            raise MessageQueueError(f"Business calendar scheduling failed: {str(e)}")
    
    async def schedule_conditional_message(self,
                                         condition_callback: str,
                                         condition_data: Dict[str, Any],
                                         payload: Dict[str, Any],
                                         queue_name: str,
                                         max_wait_time: timedelta = timedelta(hours=24),
                                         priority: int = 5) -> str:
        """Schedule a message based on conditional logic"""
        try:
            scheduled_time = datetime.now(timezone.utc) + max_wait_time
            
            message = ScheduledMessage(
                schedule_type=ScheduleType.CONDITIONAL,
                scheduled_time=scheduled_time,  # Max wait time
                payload=payload,
                queue_name=queue_name,
                priority=priority,
                condition_callback=condition_callback,
                condition_data=condition_data
            )
            
            return await self._add_scheduled_message(message)
            
        except Exception as e:
            logger.error(f"Error scheduling conditional message: {str(e)}")
            raise MessageQueueError(f"Conditional scheduling failed: {str(e)}")
    
    async def schedule_content_deadline_reminder(self,
                                               content_id: str,
                                               creator_id: str,
                                               deadline: datetime,
                                               collaboration_id: Optional[str] = None) -> List[str]:
        """Schedule content deadline reminders"""
        try:
            settings = AinflueBusiness.BUSINESS_SCHEDULES[BusinessCalendarEvent.CONTENT_DEADLINE]
            reminder_intervals = settings["reminder_intervals"]
            
            scheduled_ids = []
            
            for interval in reminder_intervals:
                reminder_time = deadline - interval
                
                # Only schedule future reminders
                if reminder_time > datetime.now(timezone.utc):
                    payload = {
                        "event_type": "content_deadline_reminder",
                        "content_id": content_id,
                        "creator_id": creator_id,
                        "deadline": deadline.isoformat(),
                        "collaboration_id": collaboration_id,
                        "reminder_interval": str(interval)
                    }
                    
                    message_id = await self.schedule_business_calendar_event(
                        BusinessCalendarEvent.CONTENT_DEADLINE,
                        reminder_time,
                        payload,
                        {"content_id": content_id, "creator_id": creator_id}
                    )
                    
                    scheduled_ids.append(message_id)
            
            logger.info(f"Scheduled {len(scheduled_ids)} deadline reminders for content {content_id}")
            return scheduled_ids
            
        except Exception as e:
            logger.error(f"Error scheduling content deadline reminders: {str(e)}")
            return []
    
    async def schedule_payment_cycle(self,
                                   cycle_type: str = "monthly",
                                   creator_ids: List[str] = None) -> str:
        """Schedule payment cycle processing"""
        try:
            # Calculate next payment date
            now = datetime.now(timezone.utc)
            if cycle_type == "monthly":
                # First day of next month
                next_month = now.replace(day=1) + timedelta(days=32)
                payment_date = next_month.replace(day=1, hour=9, minute=0, second=0, microsecond=0)
            else:
                # Weekly payments (every Monday)
                days_ahead = 0 - now.weekday()  # Monday is 0
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                payment_date = now + timedelta(days=days_ahead)
                payment_date = payment_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
            payload = {
                "event_type": "payment_cycle",
                "cycle_type": cycle_type,
                "creator_ids": creator_ids or [],
                "processing_date": payment_date.isoformat()
            }
            
            return await self.schedule_business_calendar_event(
                BusinessCalendarEvent.PAYMENT_CYCLE,
                payment_date,
                payload,
                {"cycle_type": cycle_type, "creator_count": len(creator_ids or [])}
            )
            
        except Exception as e:
            logger.error(f"Error scheduling payment cycle: {str(e)}")
            raise MessageQueueError(f"Payment cycle scheduling failed: {str(e)}")
    
    async def cancel_scheduled_message(self, message_id: str) -> bool:
        """Cancel a scheduled message"""
        try:
            if message_id in self.message_registry:
                message = self.message_registry[message_id]
                message.is_active = False
                
                # Update metrics
                self.scheduling_metrics.cancelled_schedules += 1
                
                logger.info(f"Cancelled scheduled message: {message_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling scheduled message: {str(e)}")
            return False
    
    async def get_scheduled_messages(self,
                                   queue_name: Optional[str] = None,
                                   schedule_type: Optional[ScheduleType] = None) -> List[Dict[str, Any]]:
        """Get list of scheduled messages"""
        try:
            messages = []
            
            for message in self.message_registry.values():
                if not message.is_active:
                    continue
                
                if queue_name and message.queue_name != queue_name:
                    continue
                
                if schedule_type and message.schedule_type != schedule_type:
                    continue
                
                messages.append({
                    "id": message.id,
                    "schedule_type": message.schedule_type.value,
                    "scheduled_time": message.scheduled_time.isoformat(),
                    "queue_name": message.queue_name,
                    "priority": message.priority,
                    "execution_count": message.execution_count,
                    "next_execution": message.next_execution.isoformat() if message.next_execution else None,
                    "business_event": message.business_event.value if message.business_event else None,
                    "created_at": message.created_at.isoformat()
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting scheduled messages: {str(e)}")
            return []
    
    async def get_scheduling_metrics(self) -> Dict[str, Any]:
        """Get scheduling system metrics"""
        try:
            # Calculate additional metrics
            total_scheduled = len(self.message_registry)
            active_scheduled = sum(1 for msg in self.message_registry.values() if msg.is_active)
            
            # Schedule type distribution
            type_distribution = defaultdict(int)
            for message in self.message_registry.values():
                type_distribution[message.schedule_type.value] += 1
            
            # Business event distribution
            event_distribution = defaultdict(int)
            for message in self.message_registry.values():
                if message.business_event:
                    event_distribution[message.business_event.value] += 1
            
            return {
                "total_scheduled": total_scheduled,
                "active_scheduled": active_scheduled,
                "executed_messages": self.scheduling_metrics.executed_messages,
                "failed_executions": self.scheduling_metrics.failed_executions,
                "cancelled_schedules": self.scheduling_metrics.cancelled_schedules,
                "avg_execution_delay": round(self.scheduling_metrics.avg_execution_delay, 2),
                "precision_accuracy": round(self.scheduling_metrics.precision_accuracy, 2),
                "schedule_type_distribution": dict(type_distribution),
                "business_event_distribution": dict(event_distribution),
                "next_execution_time": await self._get_next_execution_time(),
                "scheduler_running": self.is_running
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduling metrics: {str(e)}")
            return {"error": str(e)}
    
    # Core scheduling logic
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Check for messages ready to execute
                await self._process_ready_messages()
                
                # Check conditional messages
                await self._process_conditional_messages()
                
                # Update business calendar
                await self._update_business_calendar()
                
                # Sleep until next check
                await asyncio.sleep(1.0)  # 1 second precision
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                await asyncio.sleep(5.0)  # Back off on error
    
    async def _process_ready_messages(self) -> None:
        """Process messages that are ready for execution"""
        current_time = datetime.now(timezone.utc)
        
        # Get messages ready for execution
        ready_messages = []
        while (self.scheduled_messages and 
               self.scheduled_messages[0].scheduled_time <= current_time and
               self.scheduled_messages[0].is_active):
            ready_messages.append(heapq.heappop(self.scheduled_messages))
        
        # Execute ready messages
        for message in ready_messages:
            await self._execute_scheduled_message(message)
    
    async def _execute_scheduled_message(self, message -> None: ScheduledMessage) -> None:
        """Execute a scheduled message"""
        try:
            execution_time = datetime.now(timezone.utc)
            
            # Calculate execution delay
            delay = (execution_time - message.scheduled_time).total_seconds()
            
            # Encrypt payload if needed
            payload = message.payload
            if self.encryption:
                payload = await self._encrypt_payload(payload)
            
            # Create execution record
            execution_record = {
                "message_id": message.id,
                "scheduled_time": message.scheduled_time,
                "execution_time": execution_time,
                "delay_seconds": delay,
                "queue_name": message.queue_name,
                "priority": message.priority,
                "payload": payload
            }
            
            # Store execution history
            self.execution_history[f"{message.id}_{execution_time.timestamp()}"] = execution_record
            
            # Update message execution tracking
            message.execution_count += 1
            message.last_executed = execution_time
            
            # Update metrics
            await self._update_execution_metrics(message, delay)
            
            # Handle recurring messages
            if message.schedule_type in [ScheduleType.RECURRING, ScheduleType.CRON_BASED, ScheduleType.BUSINESS_CALENDAR]:
                await self._handle_recurring_execution(message)
            
            # TODO: Send message to actual queue
            logger.info(f"Executed scheduled message {message.id} with {delay:.2f}s delay")
            
        except Exception as e:
            logger.error(f"Error executing scheduled message {message.id}: {str(e)}")
            await self._handle_execution_failure(message, str(e))
    
    async def _handle_recurring_execution(self, message -> None: ScheduledMessage) -> None:
        """Handle recurring message execution"""
        try:
            # Check if we should continue recurring
            should_continue = True
            
            if message.max_executions and message.execution_count >= message.max_executions:
                should_continue = False
            
            if message.recurrence_end and datetime.now(timezone.utc) >= message.recurrence_end:
                should_continue = False
            
            if should_continue:
                # Calculate next execution time
                if message.schedule_type == ScheduleType.RECURRING:
                    message.next_execution = await self._calculate_next_execution(message)
                elif message.schedule_type == ScheduleType.CRON_BASED:
                    message.next_execution = await self._parse_cron_expression(message.cron_expression)
                elif message.schedule_type == ScheduleType.BUSINESS_CALENDAR:
                    message.next_execution = await self._calculate_business_next_execution(message)
                
                if message.next_execution:
                    message.scheduled_time = message.next_execution
                    heapq.heappush(self.scheduled_messages, message)
            else:
                # Mark as inactive
                message.is_active = False
                logger.info(f"Recurring message {message.id} completed all executions")
                
        except Exception as e:
            logger.error(f"Error handling recurring execution: {str(e)}")
            message.is_active = False
    
    async def _process_conditional_messages(self) -> None:
        """Process messages with conditional execution"""
        current_time = datetime.now(timezone.utc)
        
        conditional_messages = [
            msg for msg in self.message_registry.values()
            if msg.is_active and msg.schedule_type == ScheduleType.CONDITIONAL
        ]
        
        for message in conditional_messages:
            try:
                # Check if condition is met
                if await self._check_condition(message):
                    # Execute immediately
                    message.scheduled_time = current_time
                    heapq.heappush(self.scheduled_messages, message)
                elif current_time >= message.scheduled_time:
                    # Max wait time exceeded - execute anyway or cancel
                    logger.warning(f"Conditional message {message.id} timed out")
                    message.is_active = False
                    
            except Exception as e:
                logger.error(f"Error processing conditional message {message.id}: {str(e)}")
    
    # Helper methods
    
    async def _add_scheduled_message(self, message: ScheduledMessage) -> str:
        """Add a message to the scheduling system"""
        # Add to registry
        self.message_registry[message.id] = message
        
        # Add to priority queue
        heapq.heappush(self.scheduled_messages, message)
        
        # Update metrics
        self.scheduling_metrics.total_scheduled += 1
        
        logger.debug(f"Added scheduled message {message.id} for {message.scheduled_time}")
        return message.id
    
    async def _calculate_next_execution(self, message: ScheduledMessage) -> Optional[datetime]:
        """Calculate next execution time for recurring message"""
        if not message.recurrence_pattern:
            return None
        
        last_execution = message.last_executed or message.created_at
        interval = message.recurrence_interval
        
        if message.recurrence_pattern == RecurrencePattern.MINUTELY:
            return last_execution + timedelta(minutes=interval)
        elif message.recurrence_pattern == RecurrencePattern.HOURLY:
            return last_execution + timedelta(hours=interval)
        elif message.recurrence_pattern == RecurrencePattern.DAILY:
            return last_execution + timedelta(days=interval)
        elif message.recurrence_pattern == RecurrencePattern.WEEKLY:
            return last_execution + timedelta(weeks=interval)
        elif message.recurrence_pattern == RecurrencePattern.MONTHLY:
            # Add months (approximate)
            next_month = last_execution.month + interval
            next_year = last_execution.year + (next_month - 1) // 12
            next_month = ((next_month - 1) % 12) + 1
            
            # Handle day overflow
            try:
                return last_execution.replace(year=next_year, month=next_month)
            except ValueError:
                # Day doesn't exist in next month (e.g., Jan 31 -> Feb 31)
                last_day = calendar.monthrange(next_year, next_month)[1]
                return last_execution.replace(year=next_year, month=next_month, day=last_day)
        
        return None
    
    async def _calculate_business_next_execution(self, message: ScheduledMessage) -> Optional[datetime]:
        """Calculate next execution for business calendar events"""
        if not message.business_event:
            return None
        
        settings = AinflueBusiness.BUSINESS_SCHEDULES.get(message.business_event, {})
        
        if "recurrence" not in settings:
            return None
        
        pattern = settings["recurrence"]
        execution_day = settings.get("execution_day", 1)
        execution_time = settings.get("execution_time", "09:00")
        
        current_time = datetime.now(timezone.utc)
        
        if pattern == RecurrencePattern.DAILY:
            next_date = current_time + timedelta(days=1)
            hour, minute = map(int, execution_time.split(":"))
            return next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        elif pattern == RecurrencePattern.WEEKLY:
            days_ahead = execution_day - current_time.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_date = current_time + timedelta(days=days_ahead)
            hour, minute = map(int, execution_time.split(":"))
            return next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        elif pattern == RecurrencePattern.MONTHLY:
            # Next month, specific day
            next_month = current_time.month + 1
            next_year = current_time.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            
            hour, minute = map(int, execution_time.split(":"))
            return datetime(next_year, next_month, execution_day, hour, minute, tzinfo=timezone.utc)
        
        return None
    
    async def _parse_cron_expression(self, cron_expr: str) -> Optional[datetime]:
        """Parse cron expression and calculate next execution (simplified)"""
        # This is a simplified cron parser
        # In production, would use a proper cron library like croniter
        
        try:
            parts = cron_expr.split()
            if len(parts) != 5:
                raise ValueError("Invalid cron expression format")
            
            minute, hour, day, month, weekday = parts
            
            current_time = datetime.now(timezone.utc)
            next_time = current_time + timedelta(minutes=1)
            
            # For simplicity, just calculate next hour if hour is specified
            if hour != "*" and hour.isdigit():
                target_hour = int(hour)
                if current_time.hour >= target_hour:
                    next_time = next_time + timedelta(days=1)
                next_time = next_time.replace(hour=target_hour, minute=0, second=0, microsecond=0)
            
            return next_time
            
        except Exception as e:
            logger.error(f"Error parsing cron expression '{cron_expr}': {str(e)}")
            return None
    
    async def _check_condition(self, message: ScheduledMessage) -> bool:
        """Check if conditional message condition is met"""
        if not message.condition_callback:
            return False
        
        try:
            # Get condition handler
            handler = self.condition_handlers.get(message.condition_callback)
            if not handler:
                logger.warning(f"No condition handler for {message.condition_callback}")
                return False
            
            # Execute condition check
            return await handler(message.condition_data)
            
        except Exception as e:
            logger.error(f"Error checking condition: {str(e)}")
            return False
    
    async def _initialize_business_calendar(self) -> None:
        """Initialize business calendar with recurring events"""
        try:
            # Set up recurring business events
            for event_type, settings in AinflueBusiness.BUSINESS_SCHEDULES.items():
                if "recurrence" in settings:
                    # Calculate first execution time
                    first_execution = await self._calculate_first_business_execution(event_type, settings)
                    
                    if first_execution:
                        payload = {
                            "event_type": f"business_calendar_{event_type.value}",
                            "business_event": event_type.value,
                            "settings": settings
                        }
                        
                        await self.schedule_business_calendar_event(
                            event_type,
                            first_execution,
                            payload
                        )
            
            logger.info("Business calendar initialized")
            
        except Exception as e:
            logger.error(f"Error initializing business calendar: {str(e)}")
    
    async def _calculate_first_business_execution(self, event_type: BusinessCalendarEvent, settings: Dict[str, Any]) -> Optional[datetime]:
        """Calculate first execution time for business event"""
        current_time = datetime.now(timezone.utc)
        pattern = settings.get("recurrence")
        
        if pattern == RecurrencePattern.DAILY:
            execution_time = settings.get("execution_time", "09:00")
            hour, minute = map(int, execution_time.split(":"))
            next_execution = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if next_execution <= current_time:
                next_execution += timedelta(days=1)
            
            return next_execution
        
        elif pattern == RecurrencePattern.MONTHLY:
            execution_day = settings.get("execution_day", 1)
            execution_time = settings.get("execution_time", "09:00")
            hour, minute = map(int, execution_time.split(":"))
            
            try:
                next_execution = current_time.replace(
                    day=execution_day, hour=hour, minute=minute, second=0, microsecond=0
                )
                
                if next_execution <= current_time:
                    # Next month
                    if current_time.month == 12:
                        next_execution = next_execution.replace(year=current_time.year + 1, month=1)
                    else:
                        next_execution = next_execution.replace(month=current_time.month + 1)
                
                return next_execution
                
            except ValueError:
                # Invalid day for month
                return None
        
        return None
    
    async def _update_business_calendar(self) -> None:
        """Update business calendar events"""
        # Placeholder for business calendar updates
        pass
    
    async def _encrypt_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt message payload"""
        # Placeholder for encryption
        return payload
    
    async def _update_execution_metrics(self, message -> None: ScheduledMessage, delay -> None: float) -> None:
        """Update execution metrics"""
        self.scheduling_metrics.executed_messages += 1
        
        # Update average delay
        total_delay = self.scheduling_metrics.avg_execution_delay * (self.scheduling_metrics.executed_messages - 1)
        total_delay += delay
        self.scheduling_metrics.avg_execution_delay = total_delay / self.scheduling_metrics.executed_messages
        
        # Update precision accuracy
        if abs(delay) <= self.precision_threshold:
            # Good precision
            pass
        else:
            # Update precision accuracy (simplified)
            if delay > self.precision_threshold:
                self.scheduling_metrics.precision_accuracy *= 0.99  # Slight decrease
    
    async def _handle_execution_failure(self, message -> None: ScheduledMessage, error -> None: str) -> None:
        """Handle execution failure"""
        self.scheduling_metrics.failed_executions += 1
        
        self.failed_executions[message.id] = {
            "message_id": message.id,
            "error": error,
            "failure_time": datetime.now(timezone.utc),
            "scheduled_time": message.scheduled_time
        }
        
        # Mark as inactive for now (could implement retry logic)
        message.is_active = False
    
    async def _get_next_execution_time(self) -> Optional[str]:
        """Get next scheduled execution time"""
        if self.scheduled_messages:
            return self.scheduled_messages[0].scheduled_time.isoformat()
        return None
    
    def register_condition_handler(self, name -> None: str, handler -> None: Callable) -> None:
        """Register a condition handler for conditional scheduling"""
        self.condition_handlers[name] = handler
        logger.info(f"Registered condition handler: {name}")


# Export for public API
__all__ = [
    "DelayedSchedulingCoordinator",
    "ScheduledMessage",
    "SchedulingMetrics",
    "ScheduleType",
    "RecurrencePattern",
    "BusinessCalendarEvent",
    "AinflueBusiness"
]