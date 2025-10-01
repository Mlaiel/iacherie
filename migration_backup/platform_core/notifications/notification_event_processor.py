#!/usr/bin/env python3
"""
⚡ Enterprise Notification Event Processor - IA Chéries Platform Core
Real-time triggered notifications and event-driven processing

© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class EventType(Enum):
    """Types of events that can trigger notifications"""
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_LIKED = "content_liked"
    CONTENT_SHARED = "content_shared"
    FOLLOWER_GAINED = "follower_gained"
    COMMENT_RECEIVED = "comment_received"
    PAYMENT_RECEIVED = "payment_received"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    MILESTONE_REACHED = "milestone_reached"
    SYSTEM_ALERT = "system_alert"
    SECURITY_EVENT = "security_event"
    COLLABORATION_INVITE = "collaboration_invite"
    CAMPAIGN_STARTED = "campaign_started"
    REVENUE_TARGET_MET = "revenue_target_met"

class EventPriority(Enum):
    """Event processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class ProcessingStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class TriggerCondition(Enum):
    """Conditions for triggering notifications"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    SCHEDULED = "scheduled"
    AGGREGATED = "aggregated"
    CONDITIONAL = "conditional"

@dataclass
class NotificationEvent:
    """Event that can trigger notifications"""
    id: str
    event_type: EventType
    user_id: str
    priority: EventPriority
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    source: str
    correlation_id: Optional[str] = None

@dataclass
class EventTrigger:
    """Configuration for event-triggered notifications"""
    id: str
    name: str
    event_type: EventType
    condition: TriggerCondition
    notification_template: str
    target_users: List[str]  # Can be specific users or patterns like "followers", "subscribers"
    filters: Dict[str, Any]
    delay_seconds: int = 0
    max_frequency: Optional[int] = None  # Max notifications per hour
    aggregation_window: Optional[int] = None  # Seconds to aggregate events
    is_active: bool = True
    created_by: str = "system"
    created_at: datetime = None

@dataclass
class ProcessedEvent:
    """Record of processed event"""
    event_id: str
    trigger_id: str
    notifications_sent: int
    processing_time: float
    status: ProcessingStatus
    error_message: Optional[str]
    processed_at: datetime

class NotificationEventProcessor:
    """Enterprise notification event processor with real-time processing"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_workers: int = 10,
        batch_size: int = 100
    ):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)
        
        # Processing configuration
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Event processing
        self.event_triggers: Dict[str, EventTrigger] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        
        # Rate limiting and frequency control
        self.frequency_counters: Dict[str, Dict[str, int]] = {}  # user_id -> trigger_id -> count
        self.last_notifications: Dict[str, datetime] = {}  # user_id:trigger_id -> timestamp
        
        # Event aggregation
        self.aggregation_buffers: Dict[str, List[NotificationEvent]] = {}  # trigger_id -> events
        self.aggregation_timers: Dict[str, asyncio.Task] = {}
        
        # Processing state
        self.is_processing = False
        self.worker_tasks: List[asyncio.Task] = []
        
        # Performance metrics
        self.metrics = {
            'events_received': 0,
            'events_processed': 0,
            'events_failed': 0,
            'notifications_triggered': 0,
            'triggers_active': 0,
            'processing_time_avg': 0.0,
            'queue_size': 0,
            'aggregated_events': 0,
            'filtered_events': 0
        }

    async def initialize(self):
        """Initialize event processor"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("✅ Event processor initialized with Redis connection")
            
            # Load existing triggers
            await self._load_event_triggers()
            
            # Start processing workers
            await self._start_processing_workers()
            
            # Set up default event handlers
            self._setup_default_handlers()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize event processor: {e}")
            raise

    async def create_event_trigger(
        self,
        name: str,
        event_type: EventType,
        notification_template: str,
        target_users: List[str],
        condition: TriggerCondition = TriggerCondition.IMMEDIATE,
        filters: Optional[Dict[str, Any]] = None,
        delay_seconds: int = 0,
        max_frequency: Optional[int] = None,
        aggregation_window: Optional[int] = None,
        created_by: str = "system"
    ) -> EventTrigger:
        """
        Create new event trigger
        
        Args:
            name: Trigger name
            event_type: Type of event to listen for
            notification_template: Template for notifications
            target_users: List of target users or patterns
            condition: When to trigger notifications
            filters: Additional filtering criteria
            delay_seconds: Delay before sending notification
            max_frequency: Maximum notifications per hour
            aggregation_window: Window for aggregating events
            created_by: Who created the trigger
            
        Returns:
            EventTrigger configuration
        """
        
        trigger_id = str(uuid.uuid4())
        
        trigger = EventTrigger(
            id=trigger_id,
            name=name,
            event_type=event_type,
            condition=condition,
            notification_template=notification_template,
            target_users=target_users,
            filters=filters or {},
            delay_seconds=delay_seconds,
            max_frequency=max_frequency,
            aggregation_window=aggregation_window,
            is_active=True,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        
        # Store trigger
        self.event_triggers[trigger_id] = trigger
        await self._save_event_trigger(trigger)
        
        # Set up aggregation if needed
        if aggregation_window and aggregation_window > 0:
            self.aggregation_buffers[trigger_id] = []
        
        self.metrics['triggers_active'] += 1
        
        self.logger.info(f"✅ Event trigger created: {name} ({trigger_id})")
        
        return trigger

    async def process_event(self, event: NotificationEvent) -> bool:
        """
        Process incoming notification event
        
        Args:
            event: Notification event to process
            
        Returns:
            True if event was accepted for processing
        """
        
        self.metrics['events_received'] += 1
        
        try:
            # Add to processing queue
            await self.processing_queue.put(event)
            self.metrics['queue_size'] = self.processing_queue.qsize()
            
            self.logger.debug(f"Event queued for processing: {event.id} - {event.event_type.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to queue event: {e}")
            self.metrics['events_failed'] += 1
            return False

    async def _start_processing_workers(self):
        """Start background processing workers"""
        
        self.is_processing = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            task = asyncio.create_task(self._event_processing_worker(f"worker_{i}"))
            self.worker_tasks.append(task)
        
        self.logger.info(f"✅ Started {self.max_workers} event processing workers")

    async def _event_processing_worker(self, worker_id: str):
        """Background worker for processing events"""
        
        self.logger.info(f"Event processing worker started: {worker_id}")
        
        while self.is_processing:
            try:
                # Get event from queue with timeout
                try:
                    event = await asyncio.wait_for(
                        self.processing_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process the event
                await self._process_single_event(event)
                
                # Update queue size metric
                self.metrics['queue_size'] = self.processing_queue.qsize()
                
            except Exception as e:
                self.logger.error(f"❌ Error in processing worker {worker_id}: {e}")
                await asyncio.sleep(1)  # Brief pause on error

    async def _process_single_event(self, event: NotificationEvent):
        """Process a single event"""
        
        start_time = time.time()
        
        try:
            # Find matching triggers
            matching_triggers = self._find_matching_triggers(event)
            
            if not matching_triggers:
                self.logger.debug(f"No matching triggers for event: {event.id}")
                return
            
            notifications_sent = 0
            
            for trigger in matching_triggers:
                try:
                    # Apply filters
                    if not self._event_matches_filters(event, trigger.filters):
                        self.metrics['filtered_events'] += 1
                        continue
                    
                    # Check frequency limits
                    if not self._check_frequency_limit(event.user_id, trigger):
                        continue
                    
                    # Process based on condition
                    if trigger.condition == TriggerCondition.IMMEDIATE:
                        sent = await self._send_immediate_notification(event, trigger)
                        notifications_sent += sent
                        
                    elif trigger.condition == TriggerCondition.DELAYED:
                        await self._schedule_delayed_notification(event, trigger)
                        
                    elif trigger.condition == TriggerCondition.AGGREGATED:
                        await self._add_to_aggregation_buffer(event, trigger)
                        
                    elif trigger.condition == TriggerCondition.CONDITIONAL:
                        if await self._evaluate_conditional_trigger(event, trigger):
                            sent = await self._send_immediate_notification(event, trigger)
                            notifications_sent += sent
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to process trigger {trigger.id}: {e}")
                    continue
            
            # Record processed event
            processing_time = time.time() - start_time
            
            processed_event = ProcessedEvent(
                event_id=event.id,
                trigger_id="multiple" if len(matching_triggers) > 1 else matching_triggers[0].id,
                notifications_sent=notifications_sent,
                processing_time=processing_time,
                status=ProcessingStatus.COMPLETED,
                error_message=None,
                processed_at=datetime.utcnow()
            )
            
            await self._store_processed_event(processed_event)
            
            # Update metrics
            self.metrics['events_processed'] += 1
            self.metrics['notifications_triggered'] += notifications_sent
            
            # Update average processing time
            current_avg = self.metrics['processing_time_avg']
            self.metrics['processing_time_avg'] = (current_avg * 0.9) + (processing_time * 0.1)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process event {event.id}: {e}")
            self.metrics['events_failed'] += 1

    def _find_matching_triggers(self, event: NotificationEvent) -> List[EventTrigger]:
        """Find triggers that match the event"""
        
        matching_triggers = []
        
        for trigger in self.event_triggers.values():
            if not trigger.is_active:
                continue
            
            if trigger.event_type != event.event_type:
                continue
            
            # Check if user is in target users
            if self._user_matches_target(event.user_id, trigger.target_users, event):
                matching_triggers.append(trigger)
        
        return matching_triggers

    def _user_matches_target(
        self,
        user_id: str,
        target_users: List[str],
        event: NotificationEvent
    ) -> bool:
        """Check if user matches target criteria"""
        
        # Direct user ID match
        if user_id in target_users:
            return True
        
        # Pattern matching
        for target in target_users:
            if target == "all_users":
                return True
            elif target == "followers" and event.payload.get('has_followers'):
                return True
            elif target == "creators" and event.payload.get('is_creator'):
                return True
            elif target == "subscribers" and event.payload.get('has_subscription'):
                return True
            elif target.startswith("segment:"):
                segment = target.split(":", 1)[1]
                if event.payload.get('user_segment') == segment:
                    return True
        
        return False

    def _event_matches_filters(
        self,
        event: NotificationEvent,
        filters: Dict[str, Any]
    ) -> bool:
        """Check if event matches filter criteria"""
        
        if not filters:
            return True
        
        for filter_key, filter_value in filters.items():
            event_value = event.payload.get(filter_key)
            
            if isinstance(filter_value, dict):
                # Range filter
                if 'min' in filter_value or 'max' in filter_value:
                    min_val = filter_value.get('min', float('-inf'))
                    max_val = filter_value.get('max', float('inf'))
                    if not (min_val <= event_value <= max_val):
                        return False
                
                # List filter
                elif 'in' in filter_value:
                    if event_value not in filter_value['in']:
                        return False
            
            elif isinstance(filter_value, list):
                # Value must be in list
                if event_value not in filter_value:
                    return False
            
            else:
                # Exact match
                if event_value != filter_value:
                    return False
        
        return True

    def _check_frequency_limit(self, user_id: str, trigger: EventTrigger) -> bool:
        """Check if user hasn't exceeded frequency limit"""
        
        if not trigger.max_frequency:
            return True
        
        # Initialize counters if needed
        if user_id not in self.frequency_counters:
            self.frequency_counters[user_id] = {}
        
        if trigger.id not in self.frequency_counters[user_id]:
            self.frequency_counters[user_id][trigger.id] = 0
        
        # Check current hour count
        current_hour = datetime.utcnow().hour
        counter_key = f"{user_id}:{trigger.id}:{current_hour}"
        
        # This would typically use Redis for distributed frequency limiting
        # For now, using in-memory counters
        
        current_count = self.frequency_counters[user_id][trigger.id]
        
        if current_count >= trigger.max_frequency:
            return False
        
        # Increment counter
        self.frequency_counters[user_id][trigger.id] += 1
        
        return True

    async def _send_immediate_notification(
        self,
        event: NotificationEvent,
        trigger: EventTrigger
    ) -> int:
        """Send immediate notification"""
        
        try:
            # Render notification content
            notification_content = await self._render_notification_template(
                trigger.notification_template,
                event
            )
            
            # Determine recipients
            recipients = await self._resolve_target_users(trigger.target_users, event)
            
            notifications_sent = 0
            
            for recipient_id in recipients:
                # Create notification payload
                notification_payload = {
                    'recipient_id': recipient_id,
                    'content': notification_content,
                    'event_id': event.id,
                    'trigger_id': trigger.id,
                    'priority': event.priority.value,
                    'metadata': {
                        'event_type': event.event_type.value,
                        'source': event.source,
                        'correlation_id': event.correlation_id
                    }
                }
                
                # Send notification (this would integrate with notification manager)
                success = await self._send_notification(notification_payload)
                
                if success:
                    notifications_sent += 1
            
            return notifications_sent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send immediate notification: {e}")
            return 0

    async def _schedule_delayed_notification(
        self,
        event: NotificationEvent,
        trigger: EventTrigger
    ):
        """Schedule delayed notification"""
        
        try:
            # Calculate send time
            send_time = datetime.utcnow() + timedelta(seconds=trigger.delay_seconds)
            
            # Store scheduled notification
            scheduled_notification = {
                'event_id': event.id,
                'trigger_id': trigger.id,
                'send_time': send_time.isoformat(),
                'event_data': asdict(event),
                'trigger_data': asdict(trigger)
            }
            
            # Add to scheduled notifications queue
            await self.redis_client.zadd(
                "scheduled_notifications",
                {json.dumps(scheduled_notification): send_time.timestamp()}
            )
            
            self.logger.debug(f"Notification scheduled for {send_time}: {event.id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to schedule delayed notification: {e}")

    async def _add_to_aggregation_buffer(
        self,
        event: NotificationEvent,
        trigger: EventTrigger
    ):
        """Add event to aggregation buffer"""
        
        try:
            if trigger.id not in self.aggregation_buffers:
                self.aggregation_buffers[trigger.id] = []
            
            # Add event to buffer
            self.aggregation_buffers[trigger.id].append(event)
            self.metrics['aggregated_events'] += 1
            
            # Start aggregation timer if not already running
            if trigger.id not in self.aggregation_timers:
                timer_task = asyncio.create_task(
                    self._aggregation_timer(trigger)
                )
                self.aggregation_timers[trigger.id] = timer_task
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add event to aggregation buffer: {e}")

    async def _aggregation_timer(self, trigger: EventTrigger):
        """Timer for processing aggregated events"""
        
        try:
            # Wait for aggregation window
            await asyncio.sleep(trigger.aggregation_window)
            
            # Get events from buffer
            events = self.aggregation_buffers.get(trigger.id, [])
            
            if events:
                # Create aggregated notification
                await self._send_aggregated_notification(events, trigger)
                
                # Clear buffer
                self.aggregation_buffers[trigger.id] = []
            
            # Remove timer reference
            if trigger.id in self.aggregation_timers:
                del self.aggregation_timers[trigger.id]
            
        except Exception as e:
            self.logger.error(f"❌ Aggregation timer failed: {e}")

    async def _send_aggregated_notification(
        self,
        events: List[NotificationEvent],
        trigger: EventTrigger
    ):
        """Send notification for aggregated events"""
        
        try:
            # Create aggregated event data
            aggregated_data = {
                'event_count': len(events),
                'event_types': list(set(e.event_type.value for e in events)),
                'users_involved': list(set(e.user_id for e in events)),
                'time_span': {
                    'start': min(e.created_at for e in events).isoformat(),
                    'end': max(e.created_at for e in events).isoformat()
                },
                'events': [asdict(e) for e in events[:10]]  # Include first 10 events
            }
            
            # Render aggregated notification
            notification_content = await self._render_aggregated_template(
                trigger.notification_template,
                aggregated_data
            )
            
            # Send to target users
            recipients = await self._resolve_target_users(trigger.target_users, events[0])
            
            for recipient_id in recipients:
                notification_payload = {
                    'recipient_id': recipient_id,
                    'content': notification_content,
                    'trigger_id': trigger.id,
                    'priority': 'normal',
                    'metadata': {
                        'type': 'aggregated',
                        'event_count': len(events),
                        'aggregation_window': trigger.aggregation_window
                    }
                }
                
                await self._send_notification(notification_payload)
            
            self.logger.info(f"Aggregated notification sent: {len(events)} events")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send aggregated notification: {e}")

    async def _evaluate_conditional_trigger(
        self,
        event: NotificationEvent,
        trigger: EventTrigger
    ) -> bool:
        """Evaluate conditional trigger logic"""
        
        # This would implement complex conditional logic
        # For now, simple example conditions
        
        conditions = trigger.filters.get('conditions', {})
        
        # Time-based conditions
        if 'time_range' in conditions:
            current_hour = datetime.utcnow().hour
            time_range = conditions['time_range']
            if not (time_range['start'] <= current_hour <= time_range['end']):
                return False
        
        # Event count conditions
        if 'min_events' in conditions:
            # Check if user has had minimum number of events in time window
            min_events = conditions['min_events']
            # This would query event history
            # For now, return True
        
        # User segment conditions
        if 'user_segments' in conditions:
            user_segment = event.payload.get('user_segment')
            if user_segment not in conditions['user_segments']:
                return False
        
        return True

    async def _render_notification_template(
        self,
        template: str,
        event: NotificationEvent
    ) -> str:
        """Render notification template with event data"""
        
        try:
            # Simple template rendering - in production would use Jinja2 or similar
            content = template
            
            # Replace event placeholders
            replacements = {
                '{user_id}': event.user_id,
                '{event_type}': event.event_type.value,
                '{source}': event.source,
                '{created_at}': event.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add payload values
            for key, value in event.payload.items():
                replacements[f'{{{key}}}'] = str(value)
            
            # Perform replacements
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            
            return content
            
        except Exception as e:
            self.logger.error(f"❌ Failed to render notification template: {e}")
            return template

    async def _render_aggregated_template(
        self,
        template: str,
        aggregated_data: Dict[str, Any]
    ) -> str:
        """Render template for aggregated notification"""
        
        try:
            content = template
            
            # Replace aggregated placeholders
            replacements = {
                '{event_count}': str(aggregated_data['event_count']),
                '{users_count}': str(len(aggregated_data['users_involved'])),
                '{time_span}': f"{aggregated_data['time_span']['start']} to {aggregated_data['time_span']['end']}"
            }
            
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            
            return content
            
        except Exception as e:
            self.logger.error(f"❌ Failed to render aggregated template: {e}")
            return template

    async def _resolve_target_users(
        self,
        target_users: List[str],
        event: NotificationEvent
    ) -> List[str]:
        """Resolve target user patterns to actual user IDs"""
        
        resolved_users = set()
        
        for target in target_users:
            if target == "all_users":
                # Would typically query user database
                resolved_users.add(event.user_id)  # For demo
                
            elif target == "followers":
                # Get followers of the event user
                followers = await self._get_user_followers(event.user_id)
                resolved_users.update(followers)
                
            elif target == "subscribers":
                # Get subscribers
                subscribers = await self._get_user_subscribers(event.user_id)
                resolved_users.update(subscribers)
                
            elif target.startswith("segment:"):
                # Get users in segment
                segment = target.split(":", 1)[1]
                segment_users = await self._get_segment_users(segment)
                resolved_users.update(segment_users)
                
            else:
                # Direct user ID
                resolved_users.add(target)
        
        return list(resolved_users)

    async def _get_user_followers(self, user_id: str) -> List[str]:
        """Get followers of a user"""
        # This would integrate with user service
        return [f"follower_{i}" for i in range(3)]  # Demo data

    async def _get_user_subscribers(self, user_id: str) -> List[str]:
        """Get subscribers of a user"""
        # This would integrate with subscription service
        return [f"subscriber_{i}" for i in range(2)]  # Demo data

    async def _get_segment_users(self, segment: str) -> List[str]:
        """Get users in a segment"""
        # This would integrate with analytics service
        return [f"segment_user_{i}" for i in range(5)]  # Demo data

    async def _send_notification(self, payload: Dict[str, Any]) -> bool:
        """Send notification via notification manager"""
        
        try:
            # This would integrate with the notification manager
            # For now, just log and return success
            self.logger.info(f"📧 Notification sent to {payload['recipient_id']}: {payload['content'][:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send notification: {e}")
            return False

    async def _store_processed_event(self, processed_event: ProcessedEvent):
        """Store processed event record"""
        try:
            event_dict = asdict(processed_event)
            event_dict['processed_at'] = processed_event.processed_at.isoformat()
            event_dict['status'] = processed_event.status.value
            
            await self.redis_client.lpush(
                "processed_events",
                json.dumps(event_dict)
            )
            await self.redis_client.ltrim("processed_events", 0, 9999)  # Keep last 10k
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store processed event: {e}")

    def _setup_default_handlers(self):
        """Set up default event handlers"""
        
        # User signup handler
        async def handle_user_signup(event: NotificationEvent):
            self.logger.info(f"New user signup: {event.user_id}")
        
        # Content published handler
        async def handle_content_published(event: NotificationEvent):
            self.logger.info(f"Content published by {event.user_id}: {event.payload.get('content_title', 'Unknown')}")
        
        # Payment received handler
        async def handle_payment_received(event: NotificationEvent):
            amount = event.payload.get('amount', 0)
            self.logger.info(f"Payment received: ${amount} for user {event.user_id}")
        
        # Register handlers
        self.event_handlers[EventType.USER_SIGNUP] = [handle_user_signup]
        self.event_handlers[EventType.CONTENT_PUBLISHED] = [handle_content_published]
        self.event_handlers[EventType.PAYMENT_RECEIVED] = [handle_payment_received]

    async def process_scheduled_notifications(self):
        """Process scheduled notifications that are due"""
        
        try:
            current_time = time.time()
            
            # Get notifications due for sending
            due_notifications = await self.redis_client.zrangebyscore(
                "scheduled_notifications",
                0,
                current_time,
                withscores=True
            )
            
            for notification_data, score in due_notifications:
                try:
                    notification = json.loads(notification_data)
                    
                    # Recreate event and trigger objects
                    event_data = notification['event_data']
                    event = NotificationEvent(**event_data)
                    
                    trigger_data = notification['trigger_data']
                    trigger = EventTrigger(**trigger_data)
                    
                    # Send the notification
                    await self._send_immediate_notification(event, trigger)
                    
                    # Remove from scheduled queue
                    await self.redis_client.zrem("scheduled_notifications", notification_data)
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to process scheduled notification: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process scheduled notifications: {e}")

    async def get_event_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get event processing statistics"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        stats = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'metrics': self.metrics,
            'triggers': {
                'total': len(self.event_triggers),
                'active': len([t for t in self.event_triggers.values() if t.is_active]),
                'by_type': {}
            },
            'processing': {
                'queue_size': self.metrics['queue_size'],
                'workers_active': len(self.worker_tasks),
                'success_rate': 0.0
            }
        }
        
        # Calculate success rate
        total_events = self.metrics['events_processed'] + self.metrics['events_failed']
        if total_events > 0:
            stats['processing']['success_rate'] = (self.metrics['events_processed'] / total_events) * 100
        
        # Trigger statistics by type
        for trigger in self.event_triggers.values():
            event_type = trigger.event_type.value
            stats['triggers']['by_type'][event_type] = stats['triggers']['by_type'].get(event_type, 0) + 1
        
        return stats

    async def _save_event_trigger(self, trigger: EventTrigger):
        """Save event trigger to Redis"""
        try:
            trigger_dict = asdict(trigger)
            trigger_dict['event_type'] = trigger.event_type.value
            trigger_dict['condition'] = trigger.condition.value
            trigger_dict['created_at'] = trigger.created_at.isoformat()
            
            await self.redis_client.setex(
                f"event_trigger:{trigger.id}",
                86400 * 90,  # 90 days
                json.dumps(trigger_dict)
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to save event trigger: {e}")

    async def _load_event_triggers(self):
        """Load event triggers from Redis"""
        try:
            # This would typically scan for trigger keys
            # For now, we'll start with empty triggers
            pass
        except Exception as e:
            self.logger.error(f"❌ Failed to load event triggers: {e}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get event processor metrics"""
        
        return {
            **self.metrics,
            'active_triggers': len(self.event_triggers),
            'aggregation_buffers': len(self.aggregation_buffers),
            'frequency_counters': len(self.frequency_counters),
            'worker_tasks': len(self.worker_tasks),
            'is_processing': self.is_processing
        }

    async def stop_processing(self):
        """Stop event processing"""
        
        self.is_processing = False
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        self.worker_tasks.clear()
        
        self.logger.info("✅ Event processing stopped")

    async def cleanup(self):
        """Cleanup resources"""
        
        await self.stop_processing()
        
        if self.redis_client:
            await self.redis_client.close()
        
        if self.executor:
            self.executor.shutdown(wait=True)
        
        self.logger.info("✅ Event processor cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    async def test_event_processor():
        """Test event processor functionality"""
        
        # Initialize processor
        processor = NotificationEventProcessor()
        await processor.initialize()
        
        # Create event trigger
        trigger = await processor.create_event_trigger(
            name="Welcome New Users",
            event_type=EventType.USER_SIGNUP,
            notification_template="Welcome to IA Chéries, {user_id}! 🎉",
            target_users=["{user_id}"],  # Send to the user who signed up
            condition=TriggerCondition.IMMEDIATE
        )
        
        print(f"Event trigger created: {trigger.name} ({trigger.id})")
        
        # Create and process test event
        test_event = NotificationEvent(
            id=str(uuid.uuid4()),
            event_type=EventType.USER_SIGNUP,
            user_id="new_user_123",
            priority=EventPriority.NORMAL,
            payload={
                'email': 'newuser@example.com',
                'signup_source': 'website',
                'user_segment': 'creator'
            },
            metadata={
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0...'
            },
            created_at=datetime.utcnow(),
            source="user_service"
        )
        
        # Process event
        success = await processor.process_event(test_event)
        print(f"Event processed: {success}")
        
        # Wait a moment for processing
        await asyncio.sleep(2)
        
        # Get statistics
        stats = await processor.get_event_statistics()
        print(f"\nEvent Statistics: {json.dumps(stats, indent=2)}")
        
        # Get metrics
        metrics = await processor.get_metrics()
        print(f"\nProcessor Metrics: {json.dumps(metrics, indent=2)}")
        
        await processor.cleanup()
    
    # Run test
    asyncio.run(test_event_processor())