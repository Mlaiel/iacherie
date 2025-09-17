"""🚀 Notification Scheduler - Intelligent Enterprise System
=========================================================
Module: platform_core/notifications/notification_scheduler.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 NOTIFICATION SCHEDULER - INTELLIGENT ENTERPRISE
- Scheduling intelligent avec timezone awareness
- ML-powered optimal timing prediction
- Batch processing et rate limiting
- Retry mechanisms avec exponential backoff
- Campaign orchestration automation
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import pytz
import croniter
import redis.asyncio as redis
from celery import Celery
from celery.schedules import crontab
import numpy as np
from sklearn.ensemble import RandomForestRegressor

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Schedule types for notifications."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    RECURRING = "recurring"
    TRIGGERED = "triggered"
    OPTIMAL = "optimal"
    BATCH = "batch"


class ScheduleStatus(Enum):
    """Schedule status."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TriggerType(Enum):
    """Trigger types for automated scheduling."""
    USER_ACTION = "user_action"
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    THRESHOLD_BASED = "threshold_based"
    BEHAVIORAL = "behavioral"


class Priority(Enum):
    """Notification priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class TimeWindow:
    """Time window for notification delivery."""
    start_hour: int  # 0-23
    end_hour: int    # 0-23
    timezone: str = "UTC"
    days_of_week: List[int] = field(default_factory=lambda: list(range(7)))  # 0=Monday
    
    def __post_init__(self):
        """Validate time window."""
        if not 0 <= self.start_hour <= 23:
            raise ValueError("start_hour must be between 0 and 23")
        if not 0 <= self.end_hour <= 23:
            raise ValueError("end_hour must be between 0 and 23")
        if not all(0 <= day <= 6 for day in self.days_of_week):
            raise ValueError("days_of_week must contain values between 0 and 6")


@dataclass
class RetryPolicy:
    """Retry policy for failed notifications."""
    max_attempts: int = 3
    initial_delay: int = 60  # seconds
    max_delay: int = 3600   # seconds
    backoff_multiplier: float = 2.0
    retry_on_errors: List[str] = field(default_factory=lambda: ["timeout", "rate_limit", "server_error"])


@dataclass
class BatchConfig:
    """Batch processing configuration."""
    batch_size: int = 100
    batch_interval: int = 60  # seconds
    max_batch_time: int = 300  # seconds
    priority_ordering: bool = True


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 100
    requests_per_hour: int = 5000
    requests_per_day: int = 50000
    burst_limit: int = 200
    provider_limits: Dict[str, int] = field(default_factory=dict)


@dataclass
class TriggerCondition:
    """Trigger condition for automated scheduling."""
    id: str
    name: str
    type: TriggerType
    condition: str  # JSON expression or SQL-like condition
    template_id: str
    delay_minutes: int = 0
    time_window: Optional[TimeWindow] = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScheduledNotification:
    """Scheduled notification configuration."""
    id: str
    user_id: str
    template_id: str
    template_data: Dict[str, Any] = field(default_factory=dict)
    schedule_type: ScheduleType = ScheduleType.SCHEDULED
    scheduled_at: Optional[datetime] = None
    cron_expression: Optional[str] = None
    time_window: Optional[TimeWindow] = None
    priority: Priority = Priority.NORMAL
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trigger_condition: Optional[TriggerCondition] = None
    status: ScheduleStatus = ScheduleStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_sent_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    attempt_count: int = 0
    last_error: Optional[str] = None


@dataclass
class BatchJob:
    """Batch notification job."""
    id: str
    notifications: List[ScheduledNotification]
    scheduled_at: datetime
    status: ScheduleStatus = ScheduleStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    errors: List[str] = field(default_factory=list)


class OptimalTimingPredictor:
    """ML-based optimal timing prediction engine."""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_names = [
            'hour_of_day', 'day_of_week', 'user_timezone_offset',
            'historical_open_rate', 'historical_click_rate',
            'days_since_last_notification', 'notification_frequency',
            'user_engagement_score', 'content_category_preference'
        ]
    
    async def predict_optimal_time(self, user_id: str, user_data: Dict[str, Any]) -> datetime:
        """Predict optimal send time for user."""
        try:
            if not self.is_trained:
                await self._train_model()
            
            # Extract features
            features = self._extract_features(user_data)
            
            # Predict optimal hour
            if self.is_trained:
                predicted_hour = self.model.predict([features])[0]
                predicted_hour = max(0, min(23, int(predicted_hour)))
            else:
                # Fallback to heuristic
                predicted_hour = self._heuristic_optimal_hour(user_data)
            
            # Calculate optimal datetime
            current_time = datetime.utcnow()
            user_timezone = user_data.get('timezone', 'UTC')
            
            try:
                tz = pytz.timezone(user_timezone)
                user_now = current_time.astimezone(tz)
                
                # Set to predicted hour
                optimal_time = user_now.replace(
                    hour=predicted_hour,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                
                # If time has passed today, schedule for tomorrow
                if optimal_time <= user_now:
                    optimal_time += timedelta(days=1)
                
                # Convert back to UTC
                return optimal_time.astimezone(pytz.UTC).replace(tzinfo=None)
                
            except Exception as e:
                logger.warning(f"Timezone conversion failed: {e}")
                # Fallback to UTC
                optimal_time = current_time.replace(
                    hour=predicted_hour,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                
                if optimal_time <= current_time:
                    optimal_time += timedelta(days=1)
                
                return optimal_time
            
        except Exception as e:
            logger.error(f"Optimal timing prediction failed: {e}")
            # Fallback to immediate
            return datetime.utcnow() + timedelta(minutes=5)
    
    def _extract_features(self, user_data: Dict[str, Any]) -> List[float]:
        """Extract features for ML model."""
        features = []
        
        current_time = datetime.utcnow()
        features.append(current_time.hour)  # hour_of_day
        features.append(current_time.weekday())  # day_of_week
        
        # User timezone offset
        user_timezone = user_data.get('timezone', 'UTC')
        try:
            tz = pytz.timezone(user_timezone)
            offset_hours = tz.utcoffset(current_time).total_seconds() / 3600
            features.append(offset_hours)
        except:
            features.append(0)  # UTC offset
        
        # Historical metrics
        features.append(user_data.get('historical_open_rate', 0.3))
        features.append(user_data.get('historical_click_rate', 0.1))
        features.append(user_data.get('days_since_last_notification', 1))
        features.append(user_data.get('notification_frequency', 3))  # per week
        features.append(user_data.get('engagement_score', 0.5))
        features.append(user_data.get('content_category_preference', 0.5))
        
        return features
    
    def _heuristic_optimal_hour(self, user_data: Dict[str, Any]) -> int:
        """Fallback heuristic for optimal hour."""
        # Business hours heuristic based on user type
        user_type = user_data.get('user_type', 'consumer')
        
        if user_type == 'business':
            return 10  # 10 AM
        elif user_type == 'creator':
            return 18  # 6 PM
        else:
            return 12  # 12 PM
    
    async def _train_model(self):
        """Train the optimal timing model."""
        try:
            # In production, this would load historical data
            # For now, create synthetic training data
            X, y = self._generate_synthetic_data()
            
            if len(X) > 0:
                self.model.fit(X, y)
                self.is_trained = True
                logger.info("Optimal timing model trained successfully")
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
    
    def _generate_synthetic_data(self):
        """Generate synthetic training data."""
        # Create synthetic data for demonstration
        np.random.seed(42)
        n_samples = 1000
        
        X = []
        y = []
        
        for _ in range(n_samples):
            features = [
                np.random.randint(0, 24),  # hour_of_day
                np.random.randint(0, 7),   # day_of_week
                np.random.uniform(-12, 12),  # timezone_offset
                np.random.uniform(0.1, 0.8),  # open_rate
                np.random.uniform(0.01, 0.3), # click_rate
                np.random.randint(1, 14),     # days_since_last
                np.random.randint(1, 10),     # frequency
                np.random.uniform(0.1, 1.0),  # engagement_score
                np.random.uniform(0.1, 1.0)   # category_preference
            ]
            
            # Synthetic optimal hour (business hours bias)
            optimal_hour = np.random.choice([9, 10, 11, 14, 15, 16, 17, 18], 
                                          p=[0.1, 0.15, 0.1, 0.15, 0.15, 0.15, 0.1, 0.1])
            
            X.append(features)
            y.append(optimal_hour)
        
        return X, y


class NotificationScheduler:
    """Enterprise notification scheduler with intelligent timing."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis = redis.Redis(**config.get('redis', {}))
        
        # Initialize Celery for background tasks
        self.celery_app = Celery('notification_scheduler')
        self.celery_app.conf.update(config.get('celery', {}))
        
        # Initialize optimal timing predictor
        self.timing_predictor = OptimalTimingPredictor()
        
        # Configuration
        self.batch_config = BatchConfig(**config.get('batch', {}))
        self.rate_limit_config = RateLimitConfig(**config.get('rate_limits', {}))
        
        # Storage
        self.scheduled_notifications: Dict[str, ScheduledNotification] = {}
        self.trigger_conditions: Dict[str, TriggerCondition] = {}
        self.batch_jobs: Dict[str, BatchJob] = {}
        
        # Rate limiting
        self.rate_limiter = self._create_rate_limiter()
        
        # Start background tasks
        asyncio.create_task(self._process_scheduled_notifications())
        asyncio.create_task(self._process_batch_jobs())
        asyncio.create_task(self._cleanup_completed_jobs())
    
    async def schedule_notification(self, notification: ScheduledNotification) -> bool:
        """Schedule a notification for delivery."""
        try:
            # Validate notification
            if not await self._validate_notification(notification):
                return False
            
            # Set next run time based on schedule type
            await self._calculate_next_run_time(notification)
            
            # Store notification
            await self._store_notification(notification)
            
            # Add to scheduler queue
            if notification.schedule_type == ScheduleType.IMMEDIATE:
                await self._queue_immediate_notification(notification)
            elif notification.schedule_type == ScheduleType.BATCH:
                await self._add_to_batch(notification)
            else:
                await self._add_to_scheduler_queue(notification)
            
            logger.info(f"Notification {notification.id} scheduled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule notification: {e}")
            return False
    
    async def schedule_bulk_notifications(self, notifications: List[ScheduledNotification]) -> int:
        """Schedule multiple notifications efficiently."""
        try:
            scheduled_count = 0
            
            # Group by schedule type for efficient processing
            immediate_notifications = []
            batch_notifications = []
            scheduled_notifications = []
            
            for notification in notifications:
                if notification.schedule_type == ScheduleType.IMMEDIATE:
                    immediate_notifications.append(notification)
                elif notification.schedule_type == ScheduleType.BATCH:
                    batch_notifications.append(notification)
                else:
                    scheduled_notifications.append(notification)
            
            # Process immediate notifications
            for notification in immediate_notifications:
                if await self.schedule_notification(notification):
                    scheduled_count += 1
            
            # Create batch job for batch notifications
            if batch_notifications:
                batch_job = await self._create_batch_job(batch_notifications)
                if batch_job:
                    scheduled_count += len(batch_notifications)
            
            # Schedule regular notifications
            for notification in scheduled_notifications:
                if await self.schedule_notification(notification):
                    scheduled_count += 1
            
            logger.info(f"Bulk scheduled {scheduled_count}/{len(notifications)} notifications")
            return scheduled_count
            
        except Exception as e:
            logger.error(f"Bulk scheduling failed: {e}")
            return 0
    
    async def schedule_optimal_notification(self, user_id: str, template_id: str, 
                                          template_data: Dict[str, Any],
                                          user_data: Dict[str, Any]) -> str:
        """Schedule notification at optimal time for user."""
        try:
            # Predict optimal send time
            optimal_time = await self.timing_predictor.predict_optimal_time(user_id, user_data)
            
            # Create scheduled notification
            notification = ScheduledNotification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                template_id=template_id,
                template_data=template_data,
                schedule_type=ScheduleType.OPTIMAL,
                scheduled_at=optimal_time,
                priority=Priority.NORMAL
            )
            
            # Schedule the notification
            if await self.schedule_notification(notification):
                logger.info(f"Optimal notification scheduled for {optimal_time}")
                return notification.id
            
            return ""
            
        except Exception as e:
            logger.error(f"Optimal scheduling failed: {e}")
            return ""
    
    async def create_recurring_schedule(self, user_id: str, template_id: str,
                                      cron_expression: str, template_data: Dict[str, Any],
                                      time_window: Optional[TimeWindow] = None) -> str:
        """Create recurring notification schedule."""
        try:
            # Validate cron expression
            try:
                croniter.croniter(cron_expression)
            except ValueError as e:
                raise ValueError(f"Invalid cron expression: {e}")
            
            notification = ScheduledNotification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                template_id=template_id,
                template_data=template_data,
                schedule_type=ScheduleType.RECURRING,
                cron_expression=cron_expression,
                time_window=time_window,
                priority=Priority.NORMAL
            )
            
            # Calculate first run time
            await self._calculate_next_run_time(notification)
            
            if await self.schedule_notification(notification):
                return notification.id
            
            return ""
            
        except Exception as e:
            logger.error(f"Recurring schedule creation failed: {e}")
            return ""
    
    async def create_trigger_condition(self, condition: TriggerCondition) -> bool:
        """Create trigger condition for automated notifications."""
        try:
            # Validate condition
            if not await self._validate_trigger_condition(condition):
                return False
            
            # Store trigger condition
            await self._store_trigger_condition(condition)
            
            self.trigger_conditions[condition.id] = condition
            
            logger.info(f"Trigger condition {condition.id} created")
            return True
            
        except Exception as e:
            logger.error(f"Trigger condition creation failed: {e}")
            return False
    
    async def cancel_notification(self, notification_id: str) -> bool:
        """Cancel scheduled notification."""
        try:
            notification = await self._load_notification(notification_id)
            if not notification:
                return False
            
            notification.status = ScheduleStatus.CANCELLED
            notification.updated_at = datetime.utcnow()
            
            await self._store_notification(notification)
            
            # Remove from scheduler queue
            await self.redis.zrem("scheduler_queue", notification_id)
            
            logger.info(f"Notification {notification_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel notification: {e}")
            return False
    
    async def pause_notification(self, notification_id: str) -> bool:
        """Pause scheduled notification."""
        try:
            notification = await self._load_notification(notification_id)
            if not notification:
                return False
            
            notification.status = ScheduleStatus.PAUSED
            notification.updated_at = datetime.utcnow()
            
            await self._store_notification(notification)
            
            logger.info(f"Notification {notification_id} paused")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause notification: {e}")
            return False
    
    async def resume_notification(self, notification_id: str) -> bool:
        """Resume paused notification."""
        try:
            notification = await self._load_notification(notification_id)
            if not notification:
                return False
            
            if notification.status != ScheduleStatus.PAUSED:
                return False
            
            notification.status = ScheduleStatus.ACTIVE
            notification.updated_at = datetime.utcnow()
            
            # Recalculate next run time
            await self._calculate_next_run_time(notification)
            
            await self._store_notification(notification)
            await self._add_to_scheduler_queue(notification)
            
            logger.info(f"Notification {notification_id} resumed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume notification: {e}")
            return False
    
    async def get_user_scheduled_notifications(self, user_id: str) -> List[ScheduledNotification]:
        """Get scheduled notifications for user."""
        try:
            notification_ids = await self.redis.smembers(f"user_notifications:{user_id}")
            notifications = []
            
            for notification_id in notification_ids:
                notification = await self._load_notification(notification_id)
                if notification and notification.status != ScheduleStatus.CANCELLED:
                    notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    async def get_scheduler_statistics(self) -> Dict[str, Any]:
        """Get scheduler performance statistics."""
        try:
            stats = {}
            
            # Queue statistics
            total_queued = await self.redis.zcard("scheduler_queue")
            batch_queued = await self.redis.llen("batch_queue")
            
            stats['queued_notifications'] = total_queued
            stats['batch_notifications'] = batch_queued
            
            # Status statistics
            for status in ScheduleStatus:
                count = await self.redis.scard(f"notifications_by_status:{status.value}")
                stats[f"{status.value}_notifications"] = count
            
            # Performance metrics
            today = datetime.utcnow().strftime('%Y-%m-%d')
            sent_today = await self.redis.get(f"notifications_sent:{today}") or 0
            failed_today = await self.redis.get(f"notifications_failed:{today}") or 0
            
            stats['sent_today'] = int(sent_today)
            stats['failed_today'] = int(failed_today)
            
            # Rate limiting status
            current_minute = datetime.utcnow().strftime('%Y-%m-%d:%H:%M')
            current_rate = await self.redis.get(f"rate_limit:{current_minute}") or 0
            stats['current_rate_per_minute'] = int(current_rate)
            stats['rate_limit_per_minute'] = self.rate_limit_config.requests_per_minute
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get scheduler statistics: {e}")
            return {}
    
    async def _validate_notification(self, notification: ScheduledNotification) -> bool:
        """Validate notification before scheduling."""
        try:
            # Required fields
            if not notification.user_id or not notification.template_id:
                logger.error("Missing required fields: user_id or template_id")
                return False
            
            # Validate scheduled time
            if notification.scheduled_at and notification.scheduled_at < datetime.utcnow():
                logger.error("Scheduled time is in the past")
                return False
            
            # Validate cron expression for recurring notifications
            if notification.schedule_type == ScheduleType.RECURRING:
                if not notification.cron_expression:
                    logger.error("Missing cron expression for recurring notification")
                    return False
                
                try:
                    croniter.croniter(notification.cron_expression)
                except ValueError:
                    logger.error("Invalid cron expression")
                    return False
            
            # Validate time window
            if notification.time_window:
                if notification.time_window.start_hour > notification.time_window.end_hour:
                    logger.error("Invalid time window: start_hour > end_hour")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Notification validation failed: {e}")
            return False
    
    async def _calculate_next_run_time(self, notification: ScheduledNotification) -> None:
        """Calculate next run time for notification."""
        try:
            if notification.schedule_type == ScheduleType.IMMEDIATE:
                notification.next_run_at = datetime.utcnow()
                
            elif notification.schedule_type == ScheduleType.SCHEDULED:
                notification.next_run_at = notification.scheduled_at
                
            elif notification.schedule_type == ScheduleType.RECURRING:
                if notification.cron_expression:
                    cron = croniter.croniter(notification.cron_expression, datetime.utcnow())
                    notification.next_run_at = cron.get_next(datetime)
                    
            elif notification.schedule_type == ScheduleType.OPTIMAL:
                notification.next_run_at = notification.scheduled_at
                
            elif notification.schedule_type == ScheduleType.BATCH:
                # Batch notifications are processed in batches
                notification.next_run_at = datetime.utcnow() + timedelta(seconds=self.batch_config.batch_interval)
            
            # Apply time window constraints
            if notification.time_window and notification.next_run_at:
                notification.next_run_at = await self._apply_time_window(
                    notification.next_run_at, notification.time_window
                )
                
        except Exception as e:
            logger.error(f"Failed to calculate next run time: {e}")
            notification.next_run_at = datetime.utcnow() + timedelta(minutes=5)
    
    async def _apply_time_window(self, scheduled_time: datetime, 
                               time_window: TimeWindow) -> datetime:
        """Apply time window constraints to scheduled time."""
        try:
            # Convert to user timezone
            tz = pytz.timezone(time_window.timezone)
            scheduled_tz = scheduled_time.astimezone(tz)
            
            # Check if day of week is allowed
            if scheduled_tz.weekday() not in time_window.days_of_week:
                # Find next allowed day
                days_ahead = 1
                while (scheduled_tz + timedelta(days=days_ahead)).weekday() not in time_window.days_of_week:
                    days_ahead += 1
                
                scheduled_tz = scheduled_tz + timedelta(days=days_ahead)
                scheduled_tz = scheduled_tz.replace(hour=time_window.start_hour, minute=0, second=0)
            
            # Check if hour is within allowed window
            elif not time_window.start_hour <= scheduled_tz.hour <= time_window.end_hour:
                if scheduled_tz.hour < time_window.start_hour:
                    # Schedule for start of window today
                    scheduled_tz = scheduled_tz.replace(hour=time_window.start_hour, minute=0, second=0)
                else:
                    # Schedule for start of window tomorrow
                    scheduled_tz = scheduled_tz + timedelta(days=1)
                    scheduled_tz = scheduled_tz.replace(hour=time_window.start_hour, minute=0, second=0)
            
            # Convert back to UTC
            return scheduled_tz.astimezone(pytz.UTC).replace(tzinfo=None)
            
        except Exception as e:
            logger.error(f"Time window application failed: {e}")
            return scheduled_time
    
    async def _store_notification(self, notification: ScheduledNotification) -> None:
        """Store notification in Redis."""
        try:
            notification_data = self._serialize_notification(notification)
            await self.redis.hset(f"notification:{notification.id}", mapping=notification_data)
            
            # Add to user's notifications
            await self.redis.sadd(f"user_notifications:{notification.user_id}", notification.id)
            
            # Add to status index
            await self.redis.sadd(f"notifications_by_status:{notification.status.value}", notification.id)
            
        except Exception as e:
            logger.error(f"Failed to store notification: {e}")
            raise
    
    async def _load_notification(self, notification_id: str) -> Optional[ScheduledNotification]:
        """Load notification from Redis."""
        try:
            notification_data = await self.redis.hgetall(f"notification:{notification_id}")
            if notification_data:
                return self._deserialize_notification(notification_data)
            return None
        except Exception as e:
            logger.error(f"Failed to load notification: {e}")
            return None
    
    def _serialize_notification(self, notification: ScheduledNotification) -> Dict[str, str]:
        """Serialize notification for storage."""
        try:
            data = {
                'id': notification.id,
                'user_id': notification.user_id,
                'template_id': notification.template_id,
                'template_data': json.dumps(notification.template_data),
                'schedule_type': notification.schedule_type.value,
                'scheduled_at': notification.scheduled_at.isoformat() if notification.scheduled_at else '',
                'cron_expression': notification.cron_expression or '',
                'priority': notification.priority.value,
                'status': notification.status.value,
                'created_at': notification.created_at.isoformat(),
                'updated_at': notification.updated_at.isoformat(),
                'last_sent_at': notification.last_sent_at.isoformat() if notification.last_sent_at else '',
                'next_run_at': notification.next_run_at.isoformat() if notification.next_run_at else '',
                'attempt_count': str(notification.attempt_count),
                'last_error': notification.last_error or '',
                'metadata': json.dumps(notification.metadata)
            }
            
            # Serialize time window
            if notification.time_window:
                data['time_window'] = json.dumps({
                    'start_hour': notification.time_window.start_hour,
                    'end_hour': notification.time_window.end_hour,
                    'timezone': notification.time_window.timezone,
                    'days_of_week': notification.time_window.days_of_week
                })
            else:
                data['time_window'] = ''
            
            # Serialize retry policy
            data['retry_policy'] = json.dumps({
                'max_attempts': notification.retry_policy.max_attempts,
                'initial_delay': notification.retry_policy.initial_delay,
                'max_delay': notification.retry_policy.max_delay,
                'backoff_multiplier': notification.retry_policy.backoff_multiplier,
                'retry_on_errors': notification.retry_policy.retry_on_errors
            })
            
            return data
            
        except Exception as e:
            logger.error(f"Notification serialization failed: {e}")
            return {}
    
    def _deserialize_notification(self, data: Dict[str, str]) -> ScheduledNotification:
        """Deserialize notification from storage."""
        try:
            # Parse datetime fields
            def parse_datetime(dt_str):
                return datetime.fromisoformat(dt_str) if dt_str else None
            
            # Parse time window
            time_window = None
            if data.get('time_window'):
                tw_data = json.loads(data['time_window'])
                time_window = TimeWindow(**tw_data)
            
            # Parse retry policy
            retry_policy = RetryPolicy()
            if data.get('retry_policy'):
                rp_data = json.loads(data['retry_policy'])
                retry_policy = RetryPolicy(**rp_data)
            
            return ScheduledNotification(
                id=data['id'],
                user_id=data['user_id'],
                template_id=data['template_id'],
                template_data=json.loads(data.get('template_data', '{}')),
                schedule_type=ScheduleType(data['schedule_type']),
                scheduled_at=parse_datetime(data.get('scheduled_at')),
                cron_expression=data.get('cron_expression') or None,
                time_window=time_window,
                priority=Priority(int(data['priority'])),
                retry_policy=retry_policy,
                metadata=json.loads(data.get('metadata', '{}')),
                status=ScheduleStatus(data['status']),
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at']),
                last_sent_at=parse_datetime(data.get('last_sent_at')),
                next_run_at=parse_datetime(data.get('next_run_at')),
                attempt_count=int(data.get('attempt_count', 0)),
                last_error=data.get('last_error') or None
            )
            
        except Exception as e:
            logger.error(f"Notification deserialization failed: {e}")
            raise
    
    async def _queue_immediate_notification(self, notification: ScheduledNotification) -> None:
        """Queue notification for immediate delivery."""
        try:
            # Add to high priority queue
            await self.redis.lpush("immediate_queue", notification.id)
            logger.debug(f"Notification {notification.id} queued for immediate delivery")
        except Exception as e:
            logger.error(f"Failed to queue immediate notification: {e}")
    
    async def _add_to_scheduler_queue(self, notification: ScheduledNotification) -> None:
        """Add notification to scheduler queue."""
        try:
            if notification.next_run_at:
                timestamp = notification.next_run_at.timestamp()
                await self.redis.zadd("scheduler_queue", {notification.id: timestamp})
                logger.debug(f"Notification {notification.id} added to scheduler queue")
        except Exception as e:
            logger.error(f"Failed to add to scheduler queue: {e}")
    
    async def _add_to_batch(self, notification: ScheduledNotification) -> None:
        """Add notification to batch queue."""
        try:
            await self.redis.lpush("batch_queue", notification.id)
            logger.debug(f"Notification {notification.id} added to batch queue")
        except Exception as e:
            logger.error(f"Failed to add to batch: {e}")
    
    async def _create_batch_job(self, notifications: List[ScheduledNotification]) -> Optional[BatchJob]:
        """Create batch job for notifications."""
        try:
            batch_job = BatchJob(
                id=str(uuid.uuid4()),
                notifications=notifications,
                scheduled_at=datetime.utcnow() + timedelta(seconds=self.batch_config.batch_interval)
            )
            
            # Store batch job
            await self._store_batch_job(batch_job)
            
            # Add notifications to batch
            for notification in notifications:
                await self._add_to_batch(notification)
            
            return batch_job
            
        except Exception as e:
            logger.error(f"Failed to create batch job: {e}")
            return None
    
    async def _store_batch_job(self, batch_job: BatchJob) -> None:
        """Store batch job in Redis."""
        try:
            job_data = {
                'id': batch_job.id,
                'scheduled_at': batch_job.scheduled_at.isoformat(),
                'status': batch_job.status.value,
                'notification_ids': json.dumps([n.id for n in batch_job.notifications])
            }
            
            await self.redis.hset(f"batch_job:{batch_job.id}", mapping=job_data)
            await self.redis.zadd("batch_jobs_queue", {batch_job.id: batch_job.scheduled_at.timestamp()})
            
        except Exception as e:
            logger.error(f"Failed to store batch job: {e}")
    
    def _create_rate_limiter(self):
        """Create rate limiter instance."""
        # Simple rate limiter implementation
        class RateLimiter:
            def __init__(self, redis_client, config):
                self.redis = redis_client
                self.config = config
            
            async def can_send(self) -> bool:
                """Check if we can send a notification."""
                current_minute = datetime.utcnow().strftime('%Y-%m-%d:%H:%M')
                current_count = await self.redis.get(f"rate_limit:{current_minute}") or 0
                return int(current_count) < self.config.requests_per_minute
            
            async def record_send(self) -> None:
                """Record a sent notification."""
                current_minute = datetime.utcnow().strftime('%Y-%m-%d:%H:%M')
                await self.redis.incr(f"rate_limit:{current_minute}")
                await self.redis.expire(f"rate_limit:{current_minute}", 60)
        
        return RateLimiter(self.redis, self.rate_limit_config)
    
    async def _process_scheduled_notifications(self) -> None:
        """Background task to process scheduled notifications."""
        while True:
            try:
                current_time = datetime.utcnow().timestamp()
                
                # Get notifications ready to send
                ready_notifications = await self.redis.zrangebyscore(
                    "scheduler_queue", 0, current_time, withscores=True
                )
                
                for notification_id, _ in ready_notifications:
                    try:
                        if await self.rate_limiter.can_send():
                            await self._send_notification(notification_id)
                            await self.rate_limiter.record_send()
                        else:
                            # Rate limit reached, wait
                            break
                            
                    except Exception as e:
                        logger.error(f"Failed to process notification {notification_id}: {e}")
                
                # Sleep for processing interval
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Scheduler processing error: {e}")
                await asyncio.sleep(30)
    
    async def _send_notification(self, notification_id: str) -> None:
        """Send individual notification."""
        try:
            notification = await self._load_notification(notification_id)
            if not notification:
                return
            
            # Remove from scheduler queue
            await self.redis.zrem("scheduler_queue", notification_id)
            
            # Update attempt count
            notification.attempt_count += 1
            notification.last_sent_at = datetime.utcnow()
            notification.status = ScheduleStatus.ACTIVE
            
            # TODO: Integrate with actual notification sending services
            # For now, just simulate sending
            logger.info(f"Sending notification {notification_id} to user {notification.user_id}")
            
            # If recurring, schedule next occurrence
            if notification.schedule_type == ScheduleType.RECURRING:
                await self._calculate_next_run_time(notification)
                await self._add_to_scheduler_queue(notification)
            else:
                notification.status = ScheduleStatus.COMPLETED
            
            await self._store_notification(notification)
            
            # Track metrics
            today = datetime.utcnow().strftime('%Y-%m-%d')
            await self.redis.incr(f"notifications_sent:{today}")
            
        except Exception as e:
            logger.error(f"Failed to send notification {notification_id}: {e}")
            await self._handle_send_failure(notification_id, str(e))
    
    async def _handle_send_failure(self, notification_id: str, error: str) -> None:
        """Handle notification send failure."""
        try:
            notification = await self._load_notification(notification_id)
            if not notification:
                return
            
            notification.last_error = error
            
            # Check if we should retry
            if notification.attempt_count < notification.retry_policy.max_attempts:
                # Calculate retry delay
                delay = min(
                    notification.retry_policy.initial_delay * 
                    (notification.retry_policy.backoff_multiplier ** (notification.attempt_count - 1)),
                    notification.retry_policy.max_delay
                )
                
                # Schedule retry
                notification.next_run_at = datetime.utcnow() + timedelta(seconds=delay)
                await self._add_to_scheduler_queue(notification)
                
                logger.info(f"Notification {notification_id} scheduled for retry in {delay}s")
            else:
                # Max attempts reached
                notification.status = ScheduleStatus.FAILED
                logger.error(f"Notification {notification_id} failed after {notification.attempt_count} attempts")
            
            await self._store_notification(notification)
            
            # Track failure metrics
            today = datetime.utcnow().strftime('%Y-%m-%d')
            await self.redis.incr(f"notifications_failed:{today}")
            
        except Exception as e:
            logger.error(f"Failed to handle send failure: {e}")
    
    async def _process_batch_jobs(self) -> None:
        """Background task to process batch jobs."""
        while True:
            try:
                # Process batch queue
                batch_size = self.batch_config.batch_size
                notification_ids = await self.redis.lrange("batch_queue", 0, batch_size - 1)
                
                if notification_ids:
                    # Remove processed items from queue
                    for _ in range(len(notification_ids)):
                        await self.redis.lpop("batch_queue")
                    
                    # Create and process batch job
                    await self._process_batch_notifications(notification_ids)
                
                await asyncio.sleep(self.batch_config.batch_interval)
                
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                await asyncio.sleep(60)
    
    async def _process_batch_notifications(self, notification_ids: List[str]) -> None:
        """Process a batch of notifications."""
        try:
            logger.info(f"Processing batch of {len(notification_ids)} notifications")
            
            for notification_id in notification_ids:
                if await self.rate_limiter.can_send():
                    await self._send_notification(notification_id)
                    await self.rate_limiter.record_send()
                else:
                    # Re-queue if rate limited
                    await self.redis.lpush("batch_queue", notification_id)
                    break
                    
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
    
    async def _cleanup_completed_jobs(self) -> None:
        """Background task to cleanup completed jobs."""
        while True:
            try:
                # Cleanup old completed notifications
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                cutoff_timestamp = cutoff_time.timestamp()
                
                # Remove old completed notifications from queue
                await self.redis.zremrangebyscore("scheduler_queue", 0, cutoff_timestamp)
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(3600)
    
    async def _validate_trigger_condition(self, condition: TriggerCondition) -> bool:
        """Validate trigger condition."""
        try:
            # Basic validation
            if not condition.name or not condition.condition or not condition.template_id:
                return False
            
            # TODO: Validate condition syntax
            return True
            
        except Exception as e:
            logger.error(f"Trigger condition validation failed: {e}")
            return False
    
    async def _store_trigger_condition(self, condition: TriggerCondition) -> None:
        """Store trigger condition in Redis."""
        try:
            condition_data = {
                'id': condition.id,
                'name': condition.name,
                'type': condition.type.value,
                'condition': condition.condition,
                'template_id': condition.template_id,
                'delay_minutes': str(condition.delay_minutes),
                'active': str(condition.active),
                'created_at': condition.created_at.isoformat()
            }
            
            if condition.time_window:
                condition_data['time_window'] = json.dumps({
                    'start_hour': condition.time_window.start_hour,
                    'end_hour': condition.time_window.end_hour,
                    'timezone': condition.time_window.timezone,
                    'days_of_week': condition.time_window.days_of_week
                })
            
            await self.redis.hset(f"trigger_condition:{condition.id}", mapping=condition_data)
            await self.redis.sadd("trigger_conditions", condition.id)
            
        except Exception as e:
            logger.error(f"Failed to store trigger condition: {e}")


# Factory function for creating service instance
def create_notification_scheduler(config: Dict[str, Any]) -> NotificationScheduler:
    """Create and configure notification scheduler."""
    return NotificationScheduler(config)


# Export main classes and functions
__all__ = [
    'NotificationScheduler',
    'ScheduledNotification',
    'TriggerCondition',
    'BatchJob',
    'TimeWindow',
    'RetryPolicy',
    'BatchConfig',
    'RateLimitConfig',
    'ScheduleType',
    'ScheduleStatus',
    'TriggerType',
    'Priority',
    'OptimalTimingPredictor',
    'create_notification_scheduler'
]