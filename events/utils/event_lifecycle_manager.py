"""Event Lifecycle Manager - Complete Management for Ainflue Events

Comprehensive event lifecycle management with state tracking,
automated workflows, and business process orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import asyncio

logger = logging.getLogger(__name__)


class EventState(Enum):
    """Event lifecycle states"""
    CREATED = "created"
    VALIDATED = "validated"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class LifecycleAction(Enum):
    """Lifecycle management actions"""
    VALIDATE = "validate"
    PROCESS = "process"
    RETRY = "retry"
    ESCALATE = "escalate"
    ARCHIVE = "archive"
    EXPIRE = "expire"
    NOTIFY = "notify"


@dataclass
class EventLifecycle:
    """Event lifecycle tracking"""
    event_id: str
    current_state: EventState
    state_history: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LifecycleRule:
    """Lifecycle management rule"""
    name: str
    event_patterns: List[str]
    state_transitions: Dict[EventState, List[EventState]]
    actions: Dict[EventState, List[LifecycleAction]]
    timeouts: Dict[EventState, int] = field(default_factory=dict)
    business_rules: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class EventLifecycleManager:
    """
    Comprehensive event lifecycle manager for Ainflue platform
    Manages state transitions, automated workflows, and business processes
    """
    
    def __init__(self):
        self.managed_events: Dict[str, EventLifecycle] = {}
        self.lifecycle_rules: List[LifecycleRule] = []
        self.state_handlers: Dict[EventState, List[Callable]] = defaultdict(list)
        self.action_handlers: Dict[LifecycleAction, Callable] = {}
        
        self._initialize_default_rules()
        self._initialize_default_handlers()
        
        logger.info("EventLifecycleManager initialized for Ainflue platform")
    
    def _initialize_default_rules(self):
        """Initialize default lifecycle rules for Ainflue events"""
        
        # Content lifecycle rule
        content_rule = LifecycleRule(
            name="content_lifecycle",
            event_patterns=["content.*"],
            state_transitions={
                EventState.CREATED: [EventState.VALIDATED, EventState.FAILED],
                EventState.VALIDATED: [EventState.PROCESSING, EventState.FAILED],
                EventState.PROCESSING: [EventState.PROCESSED, EventState.FAILED],
                EventState.PROCESSED: [EventState.COMPLETED, EventState.FAILED],
                EventState.FAILED: [EventState.PROCESSING, EventState.ARCHIVED],  # Retry or give up
                EventState.COMPLETED: [EventState.ARCHIVED]
            },
            actions={
                EventState.CREATED: [LifecycleAction.VALIDATE],
                EventState.VALIDATED: [LifecycleAction.PROCESS],
                EventState.PROCESSING: [],  # External processing
                EventState.PROCESSED: [LifecycleAction.NOTIFY],
                EventState.FAILED: [LifecycleAction.RETRY, LifecycleAction.ESCALATE],
                EventState.COMPLETED: [LifecycleAction.ARCHIVE]
            },
            timeouts={
                EventState.PROCESSING: 3600,  # 1 hour max processing
                EventState.VALIDATED: 300,    # 5 minutes to start processing
                EventState.CREATED: 600       # 10 minutes to validate
            }
        )
        
        # Monetization lifecycle rule
        monetization_rule = LifecycleRule(
            name="monetization_lifecycle",
            event_patterns=["monetization.*", "payment.*", "revenue.*"],
            state_transitions={
                EventState.CREATED: [EventState.VALIDATED, EventState.FAILED],
                EventState.VALIDATED: [EventState.PROCESSING, EventState.FAILED],
                EventState.PROCESSING: [EventState.PROCESSED, EventState.FAILED],
                EventState.PROCESSED: [EventState.COMPLETED],
                EventState.FAILED: [EventState.PROCESSING, EventState.ARCHIVED],
                EventState.COMPLETED: [EventState.ARCHIVED]
            },
            actions={
                EventState.CREATED: [LifecycleAction.VALIDATE],
                EventState.VALIDATED: [LifecycleAction.PROCESS],
                EventState.FAILED: [LifecycleAction.ESCALATE, LifecycleAction.NOTIFY],
                EventState.COMPLETED: [LifecycleAction.NOTIFY, LifecycleAction.ARCHIVE]
            },
            timeouts={
                EventState.PROCESSING: 300,   # 5 minutes max for payments
                EventState.VALIDATED: 60,     # 1 minute to start processing
                EventState.CREATED: 120       # 2 minutes to validate
            },
            business_rules={
                "critical_priority": True,
                "max_retries": 5,
                "escalation_required": True
            }
        )
        
        # Collaboration lifecycle rule
        collaboration_rule = LifecycleRule(
            name="collaboration_lifecycle",
            event_patterns=["collaboration.*"],
            state_transitions={
                EventState.CREATED: [EventState.VALIDATED, EventState.FAILED],
                EventState.VALIDATED: [EventState.PROCESSING, EventState.FAILED],
                EventState.PROCESSING: [EventState.PROCESSED, EventState.FAILED],
                EventState.PROCESSED: [EventState.COMPLETED, EventState.FAILED],
                EventState.FAILED: [EventState.PROCESSING, EventState.ARCHIVED],
                EventState.COMPLETED: [EventState.ARCHIVED]
            },
            actions={
                EventState.CREATED: [LifecycleAction.VALIDATE],
                EventState.VALIDATED: [LifecycleAction.PROCESS],
                EventState.COMPLETED: [LifecycleAction.NOTIFY, LifecycleAction.ARCHIVE],
                EventState.FAILED: [LifecycleAction.RETRY]
            },
            timeouts={
                EventState.PROCESSING: 1800,  # 30 minutes for matching
                EventState.VALIDATED: 180,    # 3 minutes to start
                EventState.CREATED: 300       # 5 minutes to validate
            }
        )
        
        self.lifecycle_rules = [content_rule, monetization_rule, collaboration_rule]
    
    def _initialize_default_handlers(self):
        """Initialize default action handlers"""
        
        self.action_handlers = {
            LifecycleAction.VALIDATE: self._handle_validate,
            LifecycleAction.PROCESS: self._handle_process,
            LifecycleAction.RETRY: self._handle_retry,
            LifecycleAction.ESCALATE: self._handle_escalate,
            LifecycleAction.ARCHIVE: self._handle_archive,
            LifecycleAction.EXPIRE: self._handle_expire,
            LifecycleAction.NOTIFY: self._handle_notify
        }
    
    async def register_event(self, event_data: Dict[str, Any]) -> str:
        """Register new event for lifecycle management"""
        
        event_id = event_data.get("event_id")
        if not event_id:
            raise ValueError("Event must have an event_id")
        
        # Find applicable lifecycle rule
        rule = self._find_applicable_rule(event_data)
        
        # Create lifecycle tracking
        lifecycle = EventLifecycle(
            event_id=event_id,
            current_state=EventState.CREATED,
            max_retries=rule.business_rules.get("max_retries", 3) if rule else 3
        )
        
        # Set expiration if specified
        if rule and "ttl_seconds" in rule.business_rules:
            lifecycle.expires_at = datetime.utcnow() + timedelta(seconds=rule.business_rules["ttl_seconds"])
        
        # Add initial state to history
        lifecycle.state_history.append({
            "state": EventState.CREATED.value,
            "timestamp": lifecycle.created_at.isoformat(),
            "reason": "event_registered",
            "metadata": {"rule": rule.name if rule else "default"}
        })
        
        self.managed_events[event_id] = lifecycle
        
        # Trigger initial actions
        if rule:
            await self._execute_state_actions(event_id, rule, event_data)
        
        logger.debug(f"Registered event {event_id} for lifecycle management")
        return event_id
    
    def _find_applicable_rule(self, event_data: Dict[str, Any]) -> Optional[LifecycleRule]:
        """Find lifecycle rule applicable to event"""
        
        event_type = event_data.get("event_type", "")
        
        for rule in self.lifecycle_rules:
            if not rule.enabled:
                continue
            
            for pattern in rule.event_patterns:
                if self._matches_pattern(event_type, pattern):
                    return rule
        
        return None
    
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches pattern"""
        
        if pattern.endswith("*"):
            return event_type.startswith(pattern[:-1])
        return event_type == pattern
    
    async def transition_state(self, event_id: str, new_state: EventState, 
                             reason: str = "", metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Transition event to new state"""
        
        if event_id not in self.managed_events:
            logger.warning(f"Event {event_id} not found for state transition")
            return False
        
        lifecycle = self.managed_events[event_id]
        rule = self._find_rule_for_event(event_id)
        
        # Validate state transition
        if rule and not self._is_valid_transition(lifecycle.current_state, new_state, rule):
            logger.warning(f"Invalid state transition for {event_id}: {lifecycle.current_state} -> {new_state}")
            return False
        
        # Update state
        old_state = lifecycle.current_state
        lifecycle.current_state = new_state
        lifecycle.updated_at = datetime.utcnow()
        
        # Add to history
        lifecycle.state_history.append({
            "state": new_state.value,
            "timestamp": lifecycle.updated_at.isoformat(),
            "reason": reason,
            "metadata": metadata or {},
            "previous_state": old_state.value
        })
        
        # Execute state change handlers
        await self._notify_state_handlers(event_id, old_state, new_state)
        
        # Execute state actions
        if rule:
            await self._execute_state_actions(event_id, rule, {})
        
        logger.debug(f"Event {event_id} transitioned from {old_state} to {new_state}")
        return True
    
    def _find_rule_for_event(self, event_id: str) -> Optional[LifecycleRule]:
        """Find rule for managed event"""
        
        if event_id not in self.managed_events:
            return None
        
        lifecycle = self.managed_events[event_id]
        
        # Get rule from state history
        for state_entry in lifecycle.state_history:
            if "metadata" in state_entry and "rule" in state_entry["metadata"]:
                rule_name = state_entry["metadata"]["rule"]
                for rule in self.lifecycle_rules:
                    if rule.name == rule_name:
                        return rule
        
        return None
    
    def _is_valid_transition(self, current_state: EventState, new_state: EventState, 
                           rule: LifecycleRule) -> bool:
        """Check if state transition is valid"""
        
        allowed_transitions = rule.state_transitions.get(current_state, [])
        return new_state in allowed_transitions
    
    async def _execute_state_actions(self, event_id: str, rule: LifecycleRule, event_data: Dict[str, Any]):
        """Execute actions for current state"""
        
        lifecycle = self.managed_events[event_id]
        actions = rule.actions.get(lifecycle.current_state, [])
        
        for action in actions:
            try:
                handler = self.action_handlers.get(action)
                if handler:
                    await handler(event_id, event_data, rule)
                else:
                    logger.warning(f"No handler found for action: {action}")
            except Exception as e:
                logger.error(f"Failed to execute action {action} for event {event_id}: {e}")
                
                # Transition to failed state if action fails
                if lifecycle.current_state != EventState.FAILED:
                    await self.transition_state(event_id, EventState.FAILED, 
                                              f"Action {action.value} failed: {e}")
    
    async def _notify_state_handlers(self, event_id: str, old_state: EventState, new_state: EventState):
        """Notify registered state change handlers"""
        
        handlers = self.state_handlers.get(new_state, [])
        
        for handler in handlers:
            try:
                await handler(event_id, old_state, new_state)
            except Exception as e:
                logger.error(f"State handler failed for event {event_id}: {e}")
    
    # Default action handlers
    async def _handle_validate(self, event_id: str, event_data: Dict[str, Any], rule: LifecycleRule):
        """Handle validation action"""
        logger.debug(f"Validating event {event_id}")
        
        # Simulate validation - in real implementation would call validation service
        await asyncio.sleep(0.1)
        
        # Assume validation succeeds for demo
        await self.transition_state(event_id, EventState.VALIDATED, "validation_completed")
    
    async def _handle_process(self, event_id: str, event_data: Dict[str, Any], rule: LifecycleRule):
        """Handle processing action"""
        logger.debug(f"Starting processing for event {event_id}")
        
        await self.transition_state(event_id, EventState.PROCESSING, "processing_started")
        
        # Note: Actual processing would be handled by external services
        # This just transitions to processing state
    
    async def _handle_retry(self, event_id: str, event_data: Dict[str, Any], rule: LifecycleRule):
        """Handle retry action"""
        lifecycle = self.managed_events[event_id]
        
        if lifecycle.retry_count >= lifecycle.max_retries:
            logger.warning(f"Max retries exceeded for event {event_id}")
            await self.transition_state(event_id, EventState.ARCHIVED, "max_retries_exceeded")
            return
        
        lifecycle.retry_count += 1
        logger.debug(f"Retrying event {event_id} (attempt {lifecycle.retry_count})")
        
        # Reset to validated state for retry
        await self.transition_state(event_id, EventState.VALIDATED, 
                                   f"retry_attempt_{lifecycle.retry_count}")
    
    async def _handle_escalate(self, event_id: str, event_data: Dict[str, Any], rule: LifecycleRule):
        """Handle escalation action"""
        logger.warning(f"Escalating event {event_id}")
        
        # In real implementation, would notify support team or trigger alerts
        lifecycle = self.managed_events[event_id]
        lifecycle.metadata["escalated"] = True
        lifecycle.metadata["escalation_time"] = datetime.utcnow().isoformat()
    
    async def _handle_archive(self, event_id: str, event_data: Dict[str, Any], rule: LifecycleRule):
        """Handle archive action"""
        logger.debug(f"Archiving event {event_id}")
        
        await self.transition_state(event_id, EventState.ARCHIVED, "lifecycle_completed")
        
        # In real implementation, would move to long-term storage
        lifecycle = self.managed_events[event_id]
        lifecycle.metadata["archived"] = True
        lifecycle.metadata["archive_time"] = datetime.utcnow().isoformat()
    
    async def _handle_expire(self, event_id: str, event_data: Dict[str, Any], rule: LifecycleRule):
        """Handle expiration action"""
        logger.debug(f"Expiring event {event_id}")
        
        await self.transition_state(event_id, EventState.EXPIRED, "event_expired")
    
    async def _handle_notify(self, event_id: str, event_data: Dict[str, Any], rule: LifecycleRule):
        """Handle notification action"""
        logger.debug(f"Sending notifications for event {event_id}")
        
        # In real implementation, would send notifications to relevant parties
        lifecycle = self.managed_events[event_id]
        lifecycle.metadata["notifications_sent"] = True
        lifecycle.metadata["notification_time"] = datetime.utcnow().isoformat()
    
    async def check_timeouts(self):
        """Check for timed out events and take action"""
        
        current_time = datetime.utcnow()
        
        for event_id, lifecycle in self.managed_events.items():
            rule = self._find_rule_for_event(event_id)
            
            if not rule:
                continue
            
            # Check state timeout
            state_timeout = rule.timeouts.get(lifecycle.current_state)
            if state_timeout:
                time_in_state = (current_time - lifecycle.updated_at).total_seconds()
                
                if time_in_state > state_timeout:
                    logger.warning(f"Event {event_id} timed out in state {lifecycle.current_state}")
                    await self.transition_state(event_id, EventState.FAILED, 
                                               f"timeout_in_state_{lifecycle.current_state.value}")
            
            # Check expiration
            if lifecycle.expires_at and current_time > lifecycle.expires_at:
                logger.warning(f"Event {event_id} expired")
                await self._handle_expire(event_id, {}, rule)
    
    def register_state_handler(self, state: EventState, handler: Callable):
        """Register handler for state changes"""
        self.state_handlers[state].append(handler)
    
    def register_action_handler(self, action: LifecycleAction, handler: Callable):
        """Register custom action handler"""
        self.action_handlers[action] = handler
    
    def get_event_lifecycle(self, event_id: str) -> Optional[EventLifecycle]:
        """Get lifecycle information for event"""
        return self.managed_events.get(event_id)
    
    def get_events_by_state(self, state: EventState) -> List[str]:
        """Get all events in a specific state"""
        return [
            event_id for event_id, lifecycle in self.managed_events.items()
            if lifecycle.current_state == state
        ]
    
    def get_lifecycle_statistics(self) -> Dict[str, Any]:
        """Get lifecycle management statistics"""
        
        state_counts = defaultdict(int)
        total_events = len(self.managed_events)
        
        for lifecycle in self.managed_events.values():
            state_counts[lifecycle.current_state.value] += 1
        
        retry_stats = {
            "events_with_retries": len([l for l in self.managed_events.values() if l.retry_count > 0]),
            "total_retries": sum(l.retry_count for l in self.managed_events.values()),
            "max_retries_hit": len([l for l in self.managed_events.values() if l.retry_count >= l.max_retries])
        }
        
        return {
            "total_managed_events": total_events,
            "events_by_state": dict(state_counts),
            "active_rules": len([r for r in self.lifecycle_rules if r.enabled]),
            "retry_statistics": retry_stats,
            "expired_events": len([l for l in self.managed_events.values() if l.current_state == EventState.EXPIRED]),
            "archived_events": len([l for l in self.managed_events.values() if l.current_state == EventState.ARCHIVED])
        }


# Export main classes
__all__ = [
    'EventLifecycleManager',
    'EventState',
    'LifecycleAction',
    'EventLifecycle',
    'LifecycleRule'
]