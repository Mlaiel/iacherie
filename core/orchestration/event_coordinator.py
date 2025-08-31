"""
Event Coordinator - Advanced Event Management & Coordination System

Intelligent event orchestration engine for managing complex event flows,
choreography, and sagas across distributed microservices and workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from concurrent.futures import ThreadPoolExecutor

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class EventType(Enum):
    """Event type classification."""
    SYSTEM = "system"
    BUSINESS = "business"
    TECHNICAL = "technical"
    MONITORING = "monitoring"
    SECURITY = "security"
    USER = "user"


class EventPriority(Enum):
    """Event priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEBUG = "debug"


class EventStatus(Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class CoordinationPattern(Enum):
    """Event coordination patterns."""
    CHOREOGRAPHY = "choreography"
    ORCHESTRATION = "orchestration"
    SAGA = "saga"
    WORKFLOW = "workflow"
    PIPELINE = "pipeline"
    FANOUT = "fanout"
    SCATTER_GATHER = "scatter_gather"


@dataclass
class EventDefinition:
    """Event definition and metadata."""
    event_id: str
    name: str
    event_type: EventType
    priority: EventPriority
    schema: Dict[str, Any] = field(default_factory=dict)
    routing_rules: List[str] = field(default_factory=list)
    retention_policy: Dict[str, Any] = field(default_factory=dict)
    security_policy: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventInstance:
    """Individual event instance."""
    instance_id: str
    event_id: str
    payload: Dict[str, Any]
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    priority: EventPriority = EventPriority.MEDIUM
    status: EventStatus = EventStatus.PENDING
    retry_count: int = 0
    error_details: Optional[str] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventHandler:
    """Event handler configuration."""
    handler_id: str
    name: str
    event_types: List[str]
    handler_function: Callable
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    circuit_breaker: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventFlow:
    """Event flow coordination definition."""
    flow_id: str
    name: str
    pattern: CoordinationPattern
    trigger_events: List[str]
    steps: List[Dict[str, Any]]
    compensation_steps: List[Dict[str, Any]] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowExecution:
    """Event flow execution instance."""
    execution_id: str
    flow_id: str
    trigger_event: EventInstance
    current_step: int = 0
    status: str = "running"
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    compensation_executed: bool = False
    context: Dict[str, Any] = field(default_factory=dict)
    events_produced: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventCorrelation:
    """Event correlation tracking."""
    correlation_id: str
    events: List[str] = field(default_factory=list)
    flows: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventCoordinator:
    """
    Advanced event coordination engine for complex event-driven architectures.
    
    Provides comprehensive event management capabilities including:
    - Multi-pattern event coordination (choreography, orchestration, sagas)
    - Intelligent event routing and correlation
    - Distributed event flow execution
    - Circuit breaker and retry mechanisms
    - Event replay and compensation patterns
    - Real-time monitoring and observability
    """
    
    def __init__(self, max_workers: int = 10, correlation_timeout: int = 3600):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.max_workers = max_workers
        self.correlation_timeout = correlation_timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Event management
        self.event_definitions: Dict[str, EventDefinition] = {}
        self.event_handlers: Dict[str, EventHandler] = {}
        self.event_flows: Dict[str, EventFlow] = {}
        
        # Runtime tracking
        self.pending_events: Dict[str, EventInstance] = {}
        self.processing_events: Dict[str, EventInstance] = {}
        self.event_history: List[EventInstance] = []
        self.active_flows: Dict[str, FlowExecution] = {}
        self.flow_history: List[FlowExecution] = []
        self.correlations: Dict[str, EventCorrelation] = {}
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.coordinator_stats = {
            'total_events_processed': 0,
            'successful_events': 0,
            'failed_events': 0,
            'average_processing_time': 0.0,
            'active_flows': 0,
            'completed_flows': 0,
            'failed_flows': 0,
            'circuit_breaker_trips': 0,
            'correlation_efficiency': 0.0
        }
        
        # Start background tasks
        self._start_background_tasks()
        
        self.logger.info(f"EventCoordinator initialized with {max_workers} workers")
    
    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        asyncio.create_task(self._correlation_cleanup_task())
        asyncio.create_task(self._flow_timeout_monitor())
        asyncio.create_task(self._circuit_breaker_monitor())
    
    async def register_event_definition(self, definition: EventDefinition) -> bool:
        """
        Register event definition.
        
        Args:
            definition: Event definition to register
            
        Returns:
            bool: Success status
        """



        try:
            # Validate definition
            if not await self._validate_event_definition(definition):
                return False
            
            self.event_definitions[definition.event_id] = definition
            
            await self.event_dispatcher.emit('event_definition_registered', {
                'event_id': definition.event_id,
                'event_type': definition.event_type.value,
                'priority': definition.priority.value
            })
            
            await self.metrics_collector.increment('event_definitions.registered')
            
            self.logger.info(f"Event definition registered: {definition.event_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register event definition: {e}")
            return False
    
    async def register_event_handler(self, handler: EventHandler) -> bool:
        """
        Register event handler.
        
        Args:
            handler: Event handler to register
            
        Returns:
            bool: Success status
        """



        try:
            # Validate handler
            if not await self._validate_event_handler(handler):
                return False
            
            self.event_handlers[handler.handler_id] = handler
            
            # Initialize circuit breaker
            self.circuit_breakers[handler.handler_id] = {
                'state': 'closed',
                'failure_count': 0,
                'last_failure_time': None,
                'timeout': handler.circuit_breaker.get('timeout', 60),
                'failure_threshold': handler.circuit_breaker.get('failure_threshold', 5)
            }
            
            await self.event_dispatcher.emit('event_handler_registered', {
                'handler_id': handler.handler_id,
                'event_types': handler.event_types
            })
            
            await self.metrics_collector.increment('event_handlers.registered')
            
            self.logger.info(f"Event handler registered: {handler.handler_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register event handler: {e}")
            return False
    
    async def register_event_flow(self, flow: EventFlow) -> bool:
        """
        Register event flow definition.
        
        Args:
            flow: Event flow to register
            
        Returns:
            bool: Success status
        """



        try:
            # Validate flow
            if not await self._validate_event_flow(flow):
                return False
            
            self.event_flows[flow.flow_id] = flow
            
            await self.event_dispatcher.emit('event_flow_registered', {
                'flow_id': flow.flow_id,
                'pattern': flow.pattern.value,
                'trigger_events': flow.trigger_events,
                'step_count': len(flow.steps)
            })
            
            await self.metrics_collector.increment('event_flows.registered')
            
            self.logger.info(f"Event flow registered: {flow.flow_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register event flow: {e}")
            return False
    
    async def publish_event(self, event: EventInstance) -> str:
        """
        Publish event for processing.
        
        Args:
            event: Event instance to publish
            
        Returns:
            str: Event processing ID
        """



        try:
            # Validate event
            if not await self._validate_event_instance(event):
                raise ValueError("Invalid event instance")
            
            # Assign correlation ID if not present
            if not event.correlation_id:
                event.correlation_id = str(uuid.uuid4())
            
            # Store event
            self.pending_events[event.instance_id] = event
            
            # Process event asynchronously
            asyncio.create_task(self._process_event_async(event))
            
            await self.event_dispatcher.emit('event_published', {
                'instance_id': event.instance_id,
                'event_id': event.event_id,
                'source': event.source,
                'priority': event.priority.value,
                'correlation_id': event.correlation_id
            })
            
            await self.metrics_collector.increment('events.published')
            
            self.logger.debug(f"Event published: {event.instance_id}")
            return event.instance_id
            
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
            raise
    
    async def _process_event_async(self, event: EventInstance) -> None:
        """Internal asynchronous event processing."""



        try:
            # Move to processing
            if event.instance_id in self.pending_events:
                del self.pending_events[event.instance_id]
            self.processing_events[event.instance_id] = event
            
            event.status = EventStatus.PROCESSING
            start_time = datetime.now()
            
            # Update correlation
            await self._update_correlation(event)
            
            # Find matching handlers
            handlers = await self._find_matching_handlers(event)
            
            # Process with handlers
            handler_results = []
            for handler in handlers:
                result = await self._execute_handler(handler, event)
                handler_results.append(result)
            
            # Check for flow triggers
            await self._check_flow_triggers(event)
            
            # Update event status
            event.processing_time = (datetime.now() - start_time).total_seconds()
            
            if all(handler_results):
                event.status = EventStatus.COMPLETED
                self.coordinator_stats['successful_events'] += 1
            else:
                event.status = EventStatus.FAILED
                self.coordinator_stats['failed_events'] += 1
            
            # Update statistics
            self._update_processing_stats(event)
            
            await self.event_dispatcher.emit('event_processed', {
                'instance_id': event.instance_id,
                'status': event.status.value,
                'processing_time': event.processing_time,
                'handlers_executed': len(handlers)
            })
            
            await self.metrics_collector.record('event.processing_time', event.processing_time)
            await self.metrics_collector.increment(f'events.{event.status.value}')
            
        except Exception as e:
            event.status = EventStatus.FAILED
            event.error_details = str(e)
            self.coordinator_stats['failed_events'] += 1
            
            self.logger.error(f"Event processing failed: {e}")
            
            await self.event_dispatcher.emit('event_failed', {
                'instance_id': event.instance_id,
                'error': str(e)
            })
        
        finally:
            # Move to history
            if event.instance_id in self.processing_events:
                del self.processing_events[event.instance_id]
            self.event_history.append(event)
            
            self.coordinator_stats['total_events_processed'] += 1
    
    async def _execute_handler(self, handler: EventHandler, event: EventInstance) -> bool:
        """Execute event handler with circuit breaker protection."""
        handler_id = handler.handler_id
        
        try:
            # Check circuit breaker
            if not await self._check_circuit_breaker(handler_id):
                self.logger.warning(f"Circuit breaker open for handler: {handler_id}")
                return False
            
            # Check conditions
            if not await self._check_handler_conditions(handler, event):
                return True  # Conditions not met, but not a failure
            
            # Execute with timeout
            timeout = handler.timeout or 30
            
            try:
                result = await asyncio.wait_for(
                    handler.handler_function(event),
                    timeout=timeout
                )
                
                # Reset circuit breaker on success
                await self._reset_circuit_breaker(handler_id)
                
                return bool(result)
                
            except asyncio.TimeoutError:
                await self._record_circuit_breaker_failure(handler_id)
                event.error_details = f"Handler timeout: {handler_id}"
                return False
            
        except Exception as e:
            await self._record_circuit_breaker_failure(handler_id)
            event.error_details = f"Handler error: {handler_id} - {str(e)}"
            self.logger.error(f"Handler execution failed: {handler_id} - {e}")
            return False
    
    async def _find_matching_handlers(self, event: EventInstance) -> List[EventHandler]:
        """Find handlers that match the event."""
        matching_handlers = []
        
        for handler in self.event_handlers.values():
            if event.event_id in handler.event_types or '*' in handler.event_types:
                matching_handlers.append(handler)
        
        # Sort by priority if needed
        return matching_handlers
    
    async def _check_flow_triggers(self, event: EventInstance) -> None:
        """Check if event triggers any flows."""
        for flow in self.event_flows.values():
            if event.event_id in flow.trigger_events:
                await self._start_flow_execution(flow, event)
    
    async def _start_flow_execution(self, flow: EventFlow, trigger_event: EventInstance) -> str:
        """Start flow execution."""
        execution_id = str(uuid.uuid4())
        
        execution = FlowExecution(
            execution_id=execution_id,
            flow_id=flow.flow_id,
            trigger_event=trigger_event,
            context={'trigger_payload': trigger_event.payload}
        )
        
        self.active_flows[execution_id] = execution
        self.coordinator_stats['active_flows'] += 1
        
        # Execute flow asynchronously
        asyncio.create_task(self._execute_flow_async(execution, flow))
        
        await self.event_dispatcher.emit('flow_started', {
            'execution_id': execution_id,
            'flow_id': flow.flow_id,
            'trigger_event': trigger_event.instance_id,
            'pattern': flow.pattern.value
        })
        
        await self.metrics_collector.increment('flows.started')
        
        return execution_id
    
    async def _execute_flow_async(self, execution: FlowExecution, flow: EventFlow) -> None:
        """Execute flow steps asynchronously."""



        try:
            for step_index, step in enumerate(flow.steps):
                execution.current_step = step_index
                
                success = await self._execute_flow_step(execution, step, flow)
                
                if success:
                    execution.completed_steps.append(step.get('name', f'step_{step_index}'))
                else:
                    execution.failed_steps.append(step.get('name', f'step_{step_index}'))
                    
                    # Execute compensation if configured
                    if flow.compensation_steps:
                        await self._execute_compensation(execution, flow)
                    
                    execution.status = "failed"
                    break
            
            if execution.status != "failed":
                execution.status = "completed"
                self.coordinator_stats['completed_flows'] += 1
            else:
                self.coordinator_stats['failed_flows'] += 1
            
            execution.end_time = datetime.now()
            
            await self.event_dispatcher.emit('flow_completed', {
                'execution_id': execution.execution_id,
                'status': execution.status,
                'completed_steps': len(execution.completed_steps),
                'failed_steps': len(execution.failed_steps)
            })
            
        except Exception as e:
            execution.status = "error"
            execution.end_time = datetime.now()
            self.logger.error(f"Flow execution failed: {e}")
        
        finally:
            # Move to history
            if execution.execution_id in self.active_flows:
                del self.active_flows[execution.execution_id]
                self.coordinator_stats['active_flows'] -= 1
            
            self.flow_history.append(execution)
    
    async def _execute_flow_step(
        self,
        execution: FlowExecution,
        step: Dict[str, Any],
        flow: EventFlow
    ) -> bool:
        """Execute individual flow step."""



        try:
            step_type = step.get('type', 'event')
            
            if step_type == 'event':
                # Publish event
                event_data = step.get('event', {})
                event = EventInstance(
                    instance_id=str(uuid.uuid4()),
                    event_id=event_data.get('event_id'),
                    payload=event_data.get('payload', {}),
                    source=f"flow_{flow.flow_id}",
                    correlation_id=execution.trigger_event.correlation_id
                )
                
                await self.publish_event(event)
                execution.events_produced.append(event.instance_id)
                
            elif step_type == 'condition':
                # Evaluate condition
                condition = step.get('condition', {})
                return await self._evaluate_condition(condition, execution.context)
            
            elif step_type == 'parallel':
                # Execute parallel steps
                parallel_steps = step.get('steps', [])
                tasks = []
                
                for parallel_step in parallel_steps:
                    tasks.append(self._execute_flow_step(execution, parallel_step, flow))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return all(isinstance(r, bool) and r for r in results)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Flow step execution failed: {e}")
            return False
    
    async def _execute_compensation(self, execution: FlowExecution, flow: EventFlow) -> None:
        """Execute compensation steps."""
        execution.compensation_executed = True
        
        for step in reversed(flow.compensation_steps):
            try:
                await self._execute_flow_step(execution, step, flow)
            except Exception as e:
                self.logger.error(f"Compensation step failed: {e}")
    
    async def _update_correlation(self, event: EventInstance) -> None:
        """Update event correlation tracking."""
        if not event.correlation_id:
            return
        
        correlation_id = event.correlation_id
        
        if correlation_id not in self.correlations:
            self.correlations[correlation_id] = EventCorrelation(
                correlation_id=correlation_id
            )
        
        correlation = self.correlations[correlation_id]
        correlation.events.append(event.instance_id)
    
    async def _check_circuit_breaker(self, handler_id: str) -> bool:
        """Check circuit breaker state."""
        cb = self.circuit_breakers.get(handler_id, {})
        
        if cb.get('state') == 'open':
            # Check if timeout period has passed
            last_failure = cb.get('last_failure_time')
            timeout = cb.get('timeout', 60)
            
            if last_failure and (datetime.now() - last_failure).seconds > timeout:
                cb['state'] = 'half_open'
                return True
            
            return False
        
        return True
    
    async def _record_circuit_breaker_failure(self, handler_id: str) -> None:
        """Record circuit breaker failure."""
        cb = self.circuit_breakers.get(handler_id, {})
        
        cb['failure_count'] = cb.get('failure_count', 0) + 1
        cb['last_failure_time'] = datetime.now()
        
        threshold = cb.get('failure_threshold', 5)
        
        if cb['failure_count'] >= threshold:
            cb['state'] = 'open'
            self.coordinator_stats['circuit_breaker_trips'] += 1
            
            await self.event_dispatcher.emit('circuit_breaker_opened', {
                'handler_id': handler_id,
                'failure_count': cb['failure_count']
            })
    
    async def _reset_circuit_breaker(self, handler_id: str) -> None:
        """Reset circuit breaker after successful execution."""
        cb = self.circuit_breakers.get(handler_id, {})
        cb['state'] = 'closed'
        cb['failure_count'] = 0
        cb['last_failure_time'] = None
    
    async def _check_handler_conditions(self, handler: EventHandler, event: EventInstance) -> bool:
        """Check if handler conditions are met."""
        conditions = handler.conditions
        
        if not conditions:
            return True
        
        # Simple condition evaluation (can be enhanced)
        for key, expected_value in conditions.items():
            actual_value = event.payload.get(key)
            if actual_value != expected_value:
                return False
        
        return True
    
    async def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate flow condition."""
        # Simple condition evaluation
        condition_type = condition.get('type', 'equals')
        field = condition.get('field')
        value = condition.get('value')
        
        if not field:
            return True
        
        actual_value = context.get(field)
        
        if condition_type == 'equals':
            return actual_value == value
        elif condition_type == 'not_equals':
            return actual_value != value
        elif condition_type == 'exists':
            return field in context
        
        return True
    
    async def _correlation_cleanup_task(self) -> None:
        """Background task to clean up old correlations."""
        while True:
            try:
                current_time = datetime.now()
                expired_correlations = []
                
                for correlation_id, correlation in self.correlations.items():
                    age = (current_time - correlation.start_time).seconds
                    if age > self.correlation_timeout:
                        expired_correlations.append(correlation_id)
                
                for correlation_id in expired_correlations:
                    del self.correlations[correlation_id]
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Correlation cleanup failed: {e}")
                await asyncio.sleep(60)
    
    async def _flow_timeout_monitor(self) -> None:
        """Monitor flow timeouts."""
        while True:
            try:
                current_time = datetime.now()
                timed_out_flows = []
                
                for execution_id, execution in self.active_flows.items():
                    flow = self.event_flows.get(execution.flow_id)
                    if flow and flow.timeout:
                        age = (current_time - execution.start_time).seconds
                        if age > flow.timeout:
                            timed_out_flows.append(execution_id)
                
                for execution_id in timed_out_flows:
                    execution = self.active_flows[execution_id]
                    execution.status = "timeout"
                    execution.end_time = current_time
                    
                    await self.event_dispatcher.emit('flow_timeout', {
                        'execution_id': execution_id,
                        'flow_id': execution.flow_id
                    })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Flow timeout monitor failed: {e}")
                await asyncio.sleep(60)
    
    async def _circuit_breaker_monitor(self) -> None:
        """Monitor circuit breaker states."""
        while True:
            try:
                # Log circuit breaker states periodically
                for handler_id, cb in self.circuit_breakers.items():
                    if cb.get('state') != 'closed':
                        self.logger.info(f"Circuit breaker {handler_id}: {cb}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Circuit breaker monitor failed: {e}")
                await asyncio.sleep(60)
    
    def _update_processing_stats(self, event: EventInstance) -> None:
        """Update processing statistics."""
        if event.processing_time:
            # Update average processing time
            current_avg = self.coordinator_stats['average_processing_time']
            total_events = self.coordinator_stats['total_events_processed']
            
            if total_events > 0:
                self.coordinator_stats['average_processing_time'] = (
                    (current_avg * total_events + event.processing_time) / (total_events + 1)
                )
            else:
                self.coordinator_stats['average_processing_time'] = event.processing_time
    
    async def _validate_event_definition(self, definition: EventDefinition) -> bool:
        """Validate event definition."""



        return bool(definition.event_id and definition.name)
    
    async def _validate_event_handler(self, handler: EventHandler) -> bool:
        """Validate event handler."""



        return bool(handler.handler_id and handler.name and handler.event_types and handler.handler_function)
    
    async def _validate_event_flow(self, flow: EventFlow) -> bool:
        """Validate event flow."""



        return bool(flow.flow_id and flow.name and flow.trigger_events and flow.steps)
    
    async def _validate_event_instance(self, event: EventInstance) -> bool:
        """Validate event instance."""



        return bool(event.instance_id and event.event_id and event.source)
    
    async def get_event_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get event processing status."""
        # Check pending events
        if instance_id in self.pending_events:
            event = self.pending_events[instance_id]
            return self._event_to_status_dict(event)
        
        # Check processing events
        if instance_id in self.processing_events:
            event = self.processing_events[instance_id]
            return self._event_to_status_dict(event)
        
        # Check history
        for event in self.event_history:
            if event.instance_id == instance_id:
                return self._event_to_status_dict(event)
        
        return None
    
    async def get_flow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get flow execution status."""
        # Check active flows
        if execution_id in self.active_flows:
            execution = self.active_flows[execution_id]
            return self._execution_to_status_dict(execution)
        
        # Check history
        for execution in self.flow_history:
            if execution.execution_id == execution_id:
                return self._execution_to_status_dict(execution)
        
        return None
    
    async def get_correlation_info(self, correlation_id: str) -> Optional[Dict[str, Any]]:
        """Get correlation information."""
        correlation = self.correlations.get(correlation_id)
        if not correlation:
            return None
        
        return {
            'correlation_id': correlation.correlation_id,
            'event_count': len(correlation.events),
            'flow_count': len(correlation.flows),
            'start_time': correlation.start_time.isoformat(),
            'end_time': correlation.end_time.isoformat() if correlation.end_time else None,
            'status': correlation.status,
            'events': correlation.events,
            'flows': correlation.flows
        }
    
    def _event_to_status_dict(self, event: EventInstance) -> Dict[str, Any]:
        """Convert event to status dictionary."""



        return {
            'instance_id': event.instance_id,
            'event_id': event.event_id,
            'status': event.status.value,
            'source': event.source,
            'timestamp': event.timestamp.isoformat(),
            'correlation_id': event.correlation_id,
            'priority': event.priority.value,
            'retry_count': event.retry_count,
            'processing_time': event.processing_time,
            'error_details': event.error_details
        }
    
    def _execution_to_status_dict(self, execution: FlowExecution) -> Dict[str, Any]:
        """Convert execution to status dictionary."""



        return {
            'execution_id': execution.execution_id,
            'flow_id': execution.flow_id,
            'status': execution.status,
            'current_step': execution.current_step,
            'start_time': execution.start_time.isoformat(),
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'completed_steps': len(execution.completed_steps),
            'failed_steps': len(execution.failed_steps),
            'compensation_executed': execution.compensation_executed,
            'events_produced': len(execution.events_produced)
        }
    
    async def get_coordinator_stats(self) -> Dict[str, Any]:
        """Get event coordinator statistics."""



        return {
            **self.coordinator_stats,
            'pending_events': len(self.pending_events),
            'processing_events': len(self.processing_events),
            'event_history_size': len(self.event_history),
            'active_correlations': len(self.correlations),
            'registered_definitions': len(self.event_definitions),
            'registered_handlers': len(self.event_handlers),
            'registered_flows': len(self.event_flows),
            'circuit_breakers': {
                handler_id: cb.get('state', 'unknown') 
                for handler_id, cb in self.circuit_breakers.items()
            }
        }
