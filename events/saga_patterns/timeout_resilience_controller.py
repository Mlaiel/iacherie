#!/usr/bin/env python3
"""Timeout Resilience Controller - Adaptive Timeout Management
=============================================================

Advanced timeout management and resilience controller for saga patterns.
Provides adaptive timeouts, escalation policies, and intelligent
recovery strategies for distributed saga workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import uuid
import time
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TimeoutAction(Enum):
    """Actions to take on timeout"""
    RETRY = "retry"
    ESCALATE = "escalate"
    COMPENSATE = "compensate"
    ABORT = "abort"
    EXTEND = "extend"


class EscalationLevel(Enum):
    """Escalation levels for timeout handling"""
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class TimeoutConfiguration:
    """Configuration for timeout management"""
    base_timeout_seconds: int = 300  # 5 minutes default
    max_timeout_seconds: int = 3600  # 1 hour maximum
    retry_count: int = 3
    escalation_threshold: int = 2
    adaptive_scaling: bool = True
    business_hours_multiplier: float = 1.0
    off_hours_multiplier: float = 1.5


@dataclass
class TimeoutContext:
    """Context information for timeout decisions"""
    saga_id: str
    saga_type: str
    step_name: str
    attempt_count: int
    business_context: Dict[str, Any]
    historical_performance: Optional[Dict[str, float]] = None
    current_system_load: float = 1.0
    is_business_hours: bool = True


@dataclass
class TimeoutEvent:
    """Represents a timeout event"""
    timer_id: str
    saga_id: str
    step_name: str
    timeout_duration: float
    started_at: datetime
    context: TimeoutContext
    action_taken: Optional[TimeoutAction] = None
    escalation_level: Optional[EscalationLevel] = None


@dataclass
class EscalationPolicy:
    """Policy for timeout escalation"""
    escalation_levels: List[EscalationLevel]
    actions_per_level: Dict[EscalationLevel, List[TimeoutAction]]
    notification_channels: Dict[EscalationLevel, List[str]]
    auto_recovery_enabled: bool = True


class TimeoutStrategy(ABC):
    """Abstract base class for timeout strategies"""
    
    @abstractmethod
    async def calculate_timeout(self, context: TimeoutContext) -> float:
        """Calculate timeout duration for given context"""
        pass
    
    @abstractmethod
    async def handle_timeout(
        self, 
        timeout_event: TimeoutEvent
    ) -> TimeoutAction:
        """Handle timeout event and return action to take"""
        pass


class AdaptiveTimeoutStrategy(TimeoutStrategy):
    """Adaptive timeout strategy based on historical performance"""
    
    def __init__(self, config: TimeoutConfiguration):
        self.config = config
        self.performance_history: Dict[str, List[float]] = {}
    
    async def calculate_timeout(self, context: TimeoutContext) -> float:
        """Calculate adaptive timeout based on context"""
        base_timeout = self.config.base_timeout_seconds
        
        # Get step-specific base timeout
        step_timeouts = {
            "content_upload": 300,      # 5 minutes
            "ai_analysis": 1800,        # 30 minutes
            "content_protection": 120,  # 2 minutes
            "seo_optimization": 600,    # 10 minutes
            "distribution": 900,        # 15 minutes
            "payment_processing": 180,  # 3 minutes
            "collaboration_matching": 60,  # 1 minute
            "notification_delivery": 30   # 30 seconds
        }
        
        base_timeout = step_timeouts.get(context.step_name, base_timeout)
        
        # Apply historical performance adjustment
        if context.historical_performance:
            avg_duration = context.historical_performance.get("average_duration", base_timeout)
            p95_duration = context.historical_performance.get("p95_duration", base_timeout * 1.5)
            
            # Use P95 as basis for timeout with buffer
            base_timeout = max(base_timeout, p95_duration * 1.2)
        
        # Apply business context adjustments
        timeout = base_timeout
        
        # Content size adjustment
        content_size = context.business_context.get("content_size_mb", 0)
        if content_size > 100:  # Large content
            timeout *= 1.5
        elif content_size > 500:  # Very large content
            timeout *= 2.0
        
        # Content type adjustment
        content_type = context.business_context.get("content_type", "")
        if content_type == "video":
            timeout *= 1.3
        elif content_type == "audio":
            timeout *= 1.1
        
        # Creator tier adjustment
        creator_tier = context.business_context.get("creator_tier", "standard")
        if creator_tier == "premium":
            timeout *= 1.2
        elif creator_tier == "enterprise":
            timeout *= 1.5
        
        # System load adjustment
        if context.current_system_load > 0.8:
            timeout *= 1.3
        elif context.current_system_load > 0.9:
            timeout *= 1.6
        
        # Business hours adjustment
        if not context.is_business_hours:
            timeout *= self.config.off_hours_multiplier
        else:
            timeout *= self.config.business_hours_multiplier
        
        # Attempt count adjustment (progressive timeout)
        if context.attempt_count > 1:
            timeout *= (1.5 ** (context.attempt_count - 1))
        
        # Ensure within bounds
        timeout = min(timeout, self.config.max_timeout_seconds)
        timeout = max(timeout, 30)  # Minimum 30 seconds
        
        return timeout
    
    async def handle_timeout(self, timeout_event: TimeoutEvent) -> TimeoutAction:
        """Handle timeout with adaptive strategy"""
        context = timeout_event.context
        
        # Record timeout for learning
        self._record_timeout(timeout_event)
        
        # Determine action based on context
        if context.attempt_count < self.config.retry_count:
            # Check if retry is worth it based on historical data
            if await self._should_retry(context):
                return TimeoutAction.RETRY
        
        # Check if we should escalate
        if context.attempt_count >= self.config.escalation_threshold:
            return TimeoutAction.ESCALATE
        
        # For critical business operations, try extending timeout
        priority = context.business_context.get("priority", "normal")
        if priority in ["high", "critical"]:
            return TimeoutAction.EXTEND
        
        # Default to compensation
        return TimeoutAction.COMPENSATE
    
    async def _should_retry(self, context: TimeoutContext) -> bool:
        """Determine if retry is worthwhile"""
        step_key = f"{context.saga_type}_{context.step_name}"
        
        if step_key not in self.performance_history:
            return True  # No history, give it a chance
        
        recent_timeouts = self.performance_history[step_key][-10:]  # Last 10
        timeout_rate = len([t for t in recent_timeouts if t < 0]) / len(recent_timeouts)
        
        # If timeout rate is very high, skip retry
        return timeout_rate < 0.7
    
    def _record_timeout(self, timeout_event: TimeoutEvent):
        """Record timeout for learning"""
        step_key = f"{timeout_event.context.saga_type}_{timeout_event.step_name}"
        
        if step_key not in self.performance_history:
            self.performance_history[step_key] = []
        
        # Record as negative value to indicate timeout
        self.performance_history[step_key].append(-timeout_event.timeout_duration)
        
        # Keep only recent history
        if len(self.performance_history[step_key]) > 100:
            self.performance_history[step_key] = self.performance_history[step_key][-100:]


class TimeoutResilienceController:
    """Main controller for timeout management and resilience"""
    
    def __init__(self, config: TimeoutConfiguration = None):
        self.config = config or TimeoutConfiguration()
        self.active_timers: Dict[str, asyncio.Task] = {}
        self.timeout_strategy = AdaptiveTimeoutStrategy(self.config)
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.timeout_events: List[TimeoutEvent] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        # Setup default escalation policies
        self._setup_default_escalation_policies()
    
    def _setup_default_escalation_policies(self):
        """Setup default escalation policies"""
        self.escalation_policies["content_processing"] = EscalationPolicy(
            escalation_levels=[EscalationLevel.WARNING, EscalationLevel.CRITICAL, EscalationLevel.EMERGENCY],
            actions_per_level={
                EscalationLevel.WARNING: [TimeoutAction.RETRY, TimeoutAction.EXTEND],
                EscalationLevel.CRITICAL: [TimeoutAction.ESCALATE, TimeoutAction.COMPENSATE],
                EscalationLevel.EMERGENCY: [TimeoutAction.ABORT]
            },
            notification_channels={
                EscalationLevel.WARNING: ["ops_team"],
                EscalationLevel.CRITICAL: ["ops_team", "engineering_lead"],
                EscalationLevel.EMERGENCY: ["ops_team", "engineering_lead", "management"]
            }
        )
        
        self.escalation_policies["collaboration_workflow"] = EscalationPolicy(
            escalation_levels=[EscalationLevel.WARNING, EscalationLevel.CRITICAL],
            actions_per_level={
                EscalationLevel.WARNING: [TimeoutAction.RETRY],
                EscalationLevel.CRITICAL: [TimeoutAction.COMPENSATE]
            },
            notification_channels={
                EscalationLevel.WARNING: ["ops_team"],
                EscalationLevel.CRITICAL: ["ops_team", "product_team"]
            }
        )
    
    async def set_saga_timeout(
        self,
        saga_id: str,
        saga_type: str,
        step_name: str,
        business_context: Dict[str, Any],
        attempt_count: int = 1
    ) -> str:
        """Set adaptive timeout for saga step"""
        
        # Create timeout context
        context = TimeoutContext(
            saga_id=saga_id,
            saga_type=saga_type,
            step_name=step_name,
            attempt_count=attempt_count,
            business_context=business_context,
            historical_performance=await self._get_historical_performance(saga_type, step_name),
            current_system_load=await self._get_current_system_load(),
            is_business_hours=self._is_business_hours()
        )
        
        # Calculate timeout duration
        timeout_duration = await self.timeout_strategy.calculate_timeout(context)
        
        # Create timer
        timer_id = f"{saga_id}_{step_name}_{uuid.uuid4().hex[:8]}"
        
        # Start timeout task
        timeout_task = asyncio.create_task(
            self._timeout_with_escalation(timer_id, timeout_duration, context)
        )
        
        self.active_timers[timer_id] = timeout_task
        
        logger.info(f"Set timeout {timeout_duration}s for saga {saga_id} step {step_name}")
        return timer_id
    
    async def cancel_timeout(self, timer_id: str) -> bool:
        """Cancel active timeout"""
        if timer_id in self.active_timers:
            task = self.active_timers[timer_id]
            task.cancel()
            del self.active_timers[timer_id]
            logger.info(f"Cancelled timeout {timer_id}")
            return True
        return False
    
    async def extend_timeout(
        self,
        timer_id: str,
        additional_seconds: float
    ) -> bool:
        """Extend active timeout"""
        if timer_id in self.active_timers:
            # Cancel current timer
            await self.cancel_timeout(timer_id)
            
            # Find the original timeout event
            original_event = next(
                (event for event in self.timeout_events if event.timer_id == timer_id),
                None
            )
            
            if original_event:
                # Create new timeout with extended duration
                new_duration = original_event.timeout_duration + additional_seconds
                new_timer_id = await self.set_saga_timeout(
                    original_event.saga_id,
                    original_event.context.saga_type,
                    original_event.step_name,
                    original_event.context.business_context,
                    original_event.context.attempt_count
                )
                
                logger.info(f"Extended timeout {timer_id} by {additional_seconds}s -> {new_timer_id}")
                return True
        
        return False
    
    async def _timeout_with_escalation(
        self,
        timer_id: str,
        timeout_duration: float,
        context: TimeoutContext
    ):
        """Execute timeout with escalation logic"""
        timeout_event = TimeoutEvent(
            timer_id=timer_id,
            saga_id=context.saga_id,
            step_name=context.step_name,
            timeout_duration=timeout_duration,
            started_at=datetime.now(timezone.utc),
            context=context
        )
        
        self.timeout_events.append(timeout_event)
        
        try:
            # Wait for timeout
            await asyncio.sleep(timeout_duration)
            
            # Timeout occurred - handle it
            logger.warning(f"Timeout occurred for saga {context.saga_id} step {context.step_name}")
            
            # Determine action to take
            action = await self.timeout_strategy.handle_timeout(timeout_event)
            timeout_event.action_taken = action
            
            # Execute action
            await self._execute_timeout_action(timeout_event, action)
            
            # Update metrics
            self._update_timeout_metrics(timeout_event)
            
        except asyncio.CancelledError:
            # Timeout was cancelled (step completed in time)
            logger.debug(f"Timeout cancelled for {timer_id} - step completed")
            self._record_successful_completion(timeout_event)
        except Exception as e:
            logger.error(f"Error in timeout handling for {timer_id}: {e}")
        finally:
            # Cleanup
            if timer_id in self.active_timers:
                del self.active_timers[timer_id]
    
    async def _execute_timeout_action(
        self,
        timeout_event: TimeoutEvent,
        action: TimeoutAction
    ):
        """Execute the determined timeout action"""
        saga_id = timeout_event.saga_id
        step_name = timeout_event.step_name
        
        if action == TimeoutAction.RETRY:
            logger.info(f"Retrying step {step_name} for saga {saga_id}")
            # In real implementation, would trigger step retry
            
        elif action == TimeoutAction.ESCALATE:
            escalation_level = self._determine_escalation_level(timeout_event)
            timeout_event.escalation_level = escalation_level
            await self._escalate_timeout(timeout_event, escalation_level)
            
        elif action == TimeoutAction.COMPENSATE:
            logger.info(f"Starting compensation for saga {saga_id}")
            # In real implementation, would trigger compensation workflow
            
        elif action == TimeoutAction.ABORT:
            logger.error(f"Aborting saga {saga_id} due to timeout")
            # In real implementation, would abort saga
            
        elif action == TimeoutAction.EXTEND:
            extension_time = timeout_event.timeout_duration * 0.5  # 50% extension
            await self.extend_timeout(timeout_event.timer_id, extension_time)
    
    def _determine_escalation_level(self, timeout_event: TimeoutEvent) -> EscalationLevel:
        """Determine escalation level based on context"""
        context = timeout_event.context
        
        # Check business priority
        priority = context.business_context.get("priority", "normal")
        if priority == "critical":
            return EscalationLevel.EMERGENCY
        elif priority == "high":
            return EscalationLevel.CRITICAL
        
        # Check attempt count
        if context.attempt_count >= 3:
            return EscalationLevel.CRITICAL
        elif context.attempt_count >= 2:
            return EscalationLevel.WARNING
        
        return EscalationLevel.WARNING
    
    async def _escalate_timeout(
        self,
        timeout_event: TimeoutEvent,
        escalation_level: EscalationLevel
    ):
        """Escalate timeout to appropriate channels"""
        saga_type = timeout_event.context.saga_type
        policy = self.escalation_policies.get(saga_type)
        
        if not policy:
            logger.warning(f"No escalation policy found for saga type {saga_type}")
            return
        
        channels = policy.notification_channels.get(escalation_level, [])
        
        for channel in channels:
            await self._send_escalation_notification(timeout_event, escalation_level, channel)
    
    async def _send_escalation_notification(
        self,
        timeout_event: TimeoutEvent,
        escalation_level: EscalationLevel,
        channel: str
    ):
        """Send escalation notification"""
        message = {
            "event": "saga_timeout_escalation",
            "saga_id": timeout_event.saga_id,
            "step_name": timeout_event.step_name,
            "escalation_level": escalation_level.value,
            "timeout_duration": timeout_event.timeout_duration,
            "attempt_count": timeout_event.context.attempt_count,
            "channel": channel
        }
        
        logger.critical(f"ESCALATION {escalation_level.value}: {message}")
        # In real implementation, would send to actual notification systems
    
    async def _get_historical_performance(
        self,
        saga_type: str,
        step_name: str
    ) -> Optional[Dict[str, float]]:
        """Get historical performance data for step"""
        # In real implementation, would query from metrics database
        return None
    
    async def _get_current_system_load(self) -> float:
        """Get current system load"""
        # In real implementation, would get from monitoring system
        return 0.5  # Mock 50% load
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        
        # Business hours: 9 AM - 6 PM, Monday-Friday
        return 0 <= weekday <= 4 and 9 <= hour < 18
    
    def _record_successful_completion(self, timeout_event: TimeoutEvent):
        """Record successful step completion"""
        elapsed = (datetime.now(timezone.utc) - timeout_event.started_at).total_seconds()
        
        step_key = f"{timeout_event.context.saga_type}_{timeout_event.step_name}"
        if step_key not in self.performance_metrics:
            self.performance_metrics[step_key] = {
                "total_executions": 0,
                "successful_executions": 0,
                "total_duration": 0.0,
                "timeouts": 0
            }
        
        metrics = self.performance_metrics[step_key]
        metrics["total_executions"] += 1
        metrics["successful_executions"] += 1
        metrics["total_duration"] += elapsed
    
    def _update_timeout_metrics(self, timeout_event: TimeoutEvent):
        """Update timeout metrics"""
        step_key = f"{timeout_event.context.saga_type}_{timeout_event.step_name}"
        if step_key not in self.performance_metrics:
            self.performance_metrics[step_key] = {
                "total_executions": 0,
                "successful_executions": 0,
                "total_duration": 0.0,
                "timeouts": 0
            }
        
        metrics = self.performance_metrics[step_key]
        metrics["total_executions"] += 1
        metrics["timeouts"] += 1
    
    async def get_timeout_status(self) -> Dict[str, Any]:
        """Get current timeout status"""
        return {
            "active_timers": len(self.active_timers),
            "total_timeout_events": len(self.timeout_events),
            "recent_timeouts": len([
                event for event in self.timeout_events[-100:]
                if event.started_at > datetime.now(timezone.utc) - timedelta(hours=1)
            ]),
            "performance_metrics": self.performance_metrics.copy()
        }
    
    async def get_saga_timeouts(self, saga_id: str) -> List[Dict[str, Any]]:
        """Get timeout information for specific saga"""
        saga_events = [event for event in self.timeout_events if event.saga_id == saga_id]
        
        return [
            {
                "timer_id": event.timer_id,
                "step_name": event.step_name,
                "timeout_duration": event.timeout_duration,
                "started_at": event.started_at,
                "action_taken": event.action_taken.value if event.action_taken else None,
                "escalation_level": event.escalation_level.value if event.escalation_level else None
            }
            for event in saga_events
        ]


# Global timeout controller
_timeout_controller: Optional[TimeoutResilienceController] = None


def get_timeout_resilience_controller() -> TimeoutResilienceController:
    """Get global timeout resilience controller"""
    global _timeout_controller
    if _timeout_controller is None:
        _timeout_controller = TimeoutResilienceController()
    
    return _timeout_controller


async def set_adaptive_timeout(
    saga_id: str,
    saga_type: str,
    step_name: str,
    business_context: Dict[str, Any] = None
) -> str:
    """Convenience function to set adaptive timeout"""
    controller = get_timeout_resilience_controller()
    return await controller.set_saga_timeout(
        saga_id, saga_type, step_name, business_context or {}
    )


async def cancel_saga_timeout(timer_id: str) -> bool:
    """Convenience function to cancel timeout"""
    controller = get_timeout_resilience_controller()
    return await controller.cancel_timeout(timer_id)


__all__ = [
    "TimeoutResilienceController",
    "TimeoutConfiguration",
    "TimeoutContext",
    "TimeoutEvent",
    "EscalationPolicy",
    "TimeoutAction",
    "EscalationLevel",
    "TimeoutStrategy",
    "AdaptiveTimeoutStrategy",
    "get_timeout_resilience_controller",
    "set_adaptive_timeout",
    "cancel_saga_timeout"
]