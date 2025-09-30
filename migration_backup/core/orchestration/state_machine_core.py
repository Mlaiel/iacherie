"""Ainflue Core Orchestration - State Machine Core
===============================================

Enterprise-grade state machine implementation providing workflow orchestration,
state transitions, event-driven processing, and complex business process
management for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Type, Union, Set
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import threading
import copy

# Setup logger
logger = logging.getLogger(__name__)

class TransitionType(str, Enum):
    """State transition types"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    CONDITIONAL = "conditional"
    TIMED = "timed"
    EVENT_DRIVEN = "event_driven"

class ExecutionStatus(str, Enum):
    """State execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    PAUSED = "paused"

class StateMachineStatus(str, Enum):
    """State machine status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class StateContext:
    """State execution context"""
    state_machine_id: str
    current_state: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_info: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get data value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set data value"""
        self.data[key] = value
        self.updated_at = datetime.utcnow()
    
    def update(self, data: Dict[str, Any]):
        """Update multiple data values"""
        self.data.update(data)
        self.updated_at = datetime.utcnow()

@dataclass
class Transition:
    """State transition definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_state: str = ""
    to_state: str = ""
    condition: Optional[Callable[[StateContext], bool]] = None
    action: Optional[Callable[[StateContext], Any]] = None
    trigger_event: Optional[str] = None
    timeout_seconds: Optional[int] = None
    transition_type: TransitionType = TransitionType.MANUAL
    priority: int = 5  # 1-10, 10 being highest
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StateDefinition:
    """State definition"""
    name: str
    description: str = ""
    entry_action: Optional[Callable[[StateContext], Any]] = None
    exit_action: Optional[Callable[[StateContext], Any]] = None
    timeout_seconds: Optional[int] = None
    max_retries: int = 3
    is_initial: bool = False
    is_final: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StateMachineDefinition:
    """State machine definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    states: Dict[str, StateDefinition] = field(default_factory=dict)
    transitions: List[Transition] = field(default_factory=list)
    initial_state: str = ""
    final_states: Set[str] = field(default_factory=set)
    global_timeout_seconds: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StateExecution:
    """State execution record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state_machine_id: str = ""
    state_name: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: float = 0.0
    retry_count: int = 0
    error_message: Optional[str] = None
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateAction(ABC):
    """Abstract state action"""
    
    @abstractmethod
    async def execute(self, context: StateContext) -> Any:
        """Execute state action"""
        pass
    
    async def on_entry(self, context: StateContext) -> Any:
        """Called when entering state"""
        pass
    
    async def on_exit(self, context: StateContext) -> Any:
        """Called when exiting state"""
        pass

class StateMachineInstance:
    """State machine instance"""
    
    def __init__(self, definition: StateMachineDefinition, instance_id: Optional[str] = None):
        self.id = instance_id or str(uuid.uuid4())
        self.definition = definition
        self.context = StateContext(
            state_machine_id=self.id,
            current_state=definition.initial_state
        )
        self.status = StateMachineStatus.CREATED
        self.executions: List[StateExecution] = []
        self.event_queue: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.lock = threading.Lock()
        
    async def start(self, initial_data: Optional[Dict[str, Any]] = None) -> bool:
        """Start state machine execution"""
        try:
            with self.lock:
                if self.status != StateMachineStatus.CREATED:
                    raise Exception(f"State machine is already {self.status.value}")
                
                self.status = StateMachineStatus.RUNNING
                self.start_time = datetime.utcnow()
                
                if initial_data:
                    self.context.update(initial_data)
            
            # Execute initial state
            await self._execute_state(self.context.current_state)
            
            logger.info(f"State machine {self.id} started in state {self.context.current_state}")
            return True
            
        except Exception as e:
            self.status = StateMachineStatus.FAILED
            self.context.error_info = {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
            logger.error(f"Failed to start state machine {self.id}: {str(e)}")
            return False
    
    async def trigger_event(self, event_name: str, event_data: Optional[Dict[str, Any]] = None) -> bool:
        """Trigger event for state transitions"""
        try:
            event = {
                'name': event_name,
                'data': event_data or {},
                'timestamp': datetime.utcnow()
            }
            
            with self.lock:
                self.event_queue.append(event)
            
            # Process event-driven transitions
            await self._process_event(event)
            
            logger.debug(f"Event {event_name} triggered for state machine {self.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger event {event_name}: {str(e)}")
            return False
    
    async def transition_to(self, target_state: str, force: bool = False) -> bool:
        """Transition to target state"""
        try:
            current_state = self.context.current_state
            
            # Find valid transition
            transition = None
            if not force:
                transition = self._find_transition(current_state, target_state)
                if not transition:
                    raise Exception(f"No valid transition from {current_state} to {target_state}")
                
                # Check transition condition
                if transition.condition and not await self._evaluate_condition(transition.condition):
                    raise Exception(f"Transition condition not met for {current_state} -> {target_state}")
            
            # Execute transition
            await self._execute_transition(current_state, target_state, transition)
            
            logger.info(f"State machine {self.id} transitioned from {current_state} to {target_state}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to transition to {target_state}: {str(e)}")
            return False
    
    async def pause(self) -> bool:
        """Pause state machine execution"""
        try:
            with self.lock:
                if self.status == StateMachineStatus.RUNNING:
                    self.status = StateMachineStatus.PAUSED
                    logger.info(f"State machine {self.id} paused")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to pause state machine {self.id}: {str(e)}")
            return False
    
    async def resume(self) -> bool:
        """Resume state machine execution"""
        try:
            with self.lock:
                if self.status == StateMachineStatus.PAUSED:
                    self.status = StateMachineStatus.RUNNING
                    logger.info(f"State machine {self.id} resumed")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to resume state machine {self.id}: {str(e)}")
            return False
    
    async def cancel(self) -> bool:
        """Cancel state machine execution"""
        try:
            with self.lock:
                if self.status in [StateMachineStatus.RUNNING, StateMachineStatus.PAUSED]:
                    self.status = StateMachineStatus.CANCELLED
                    self.end_time = datetime.utcnow()
                    logger.info(f"State machine {self.id} cancelled")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to cancel state machine {self.id}: {str(e)}")
            return False
    
    async def _execute_state(self, state_name: str) -> StateExecution:
        """Execute state"""
        execution = StateExecution(
            state_machine_id=self.id,
            state_name=state_name,
            started_at=datetime.utcnow()
        )
        
        try:
            execution.status = ExecutionStatus.RUNNING
            state_def = self.definition.states.get(state_name)
            
            if not state_def:
                raise Exception(f"State {state_name} not found in definition")
            
            # Execute entry action
            if state_def.entry_action:
                await self._execute_action(state_def.entry_action, execution)
            
            # Check if final state
            if state_def.is_final or state_name in self.definition.final_states:
                self.status = StateMachineStatus.COMPLETED
                self.end_time = datetime.utcnow()
                logger.info(f"State machine {self.id} completed at final state {state_name}")
            
            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.execution_time_ms = (
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            # Handle retry logic
            if execution.retry_count < state_def.max_retries:
                execution.retry_count += 1
                execution.status = ExecutionStatus.PENDING
                logger.warning(f"State {state_name} failed, retrying ({execution.retry_count}/{state_def.max_retries})")
                # Reschedule execution
                await asyncio.sleep(1)  # Brief delay before retry
                return await self._execute_state(state_name)
            else:
                self.status = StateMachineStatus.FAILED
                self.context.error_info = {'error': str(e), 'state': state_name}
                logger.error(f"State {state_name} failed after {state_def.max_retries} retries: {str(e)}")
        
        finally:
            self.executions.append(execution)
        
        return execution
    
    async def _execute_transition(self, from_state: str, to_state: str, 
                                 transition: Optional[Transition] = None):
        """Execute state transition"""
        try:
            # Execute exit action for current state
            current_state_def = self.definition.states.get(from_state)
            if current_state_def and current_state_def.exit_action:
                await self._execute_action(current_state_def.exit_action)
            
            # Execute transition action
            if transition and transition.action:
                await self._execute_action(transition.action)
            
            # Update current state
            self.context.current_state = to_state
            self.context.updated_at = datetime.utcnow()
            
            # Execute new state
            await self._execute_state(to_state)
            
        except Exception as e:
            logger.error(f"Transition execution failed: {str(e)}")
            raise
    
    async def _execute_action(self, action: Callable[[StateContext], Any], 
                             execution: Optional[StateExecution] = None):
        """Execute action with context"""
        try:
            if asyncio.iscoroutinefunction(action):
                result = await action(self.context)
            else:
                result = action(self.context)
            
            if execution:
                execution.result = result
            
            return result
        except Exception as e:
            if execution:
                execution.error_message = str(e)
            raise
    
    async def _evaluate_condition(self, condition: Callable[[StateContext], bool]) -> bool:
        """Evaluate transition condition"""
        try:
            if asyncio.iscoroutinefunction(condition):
                return await condition(self.context)
            else:
                return condition(self.context)
        except Exception as e:
            logger.error(f"Condition evaluation failed: {str(e)}")
            return False
    
    def _find_transition(self, from_state: str, to_state: str) -> Optional[Transition]:
        """Find transition between states"""
        for transition in self.definition.transitions:
            if transition.from_state == from_state and transition.to_state == to_state:
                return transition
        return None
    
    async def _process_event(self, event: Dict[str, Any]):
        """Process event for transitions"""
        try:
            current_state = self.context.current_state
            
            # Find event-driven transitions
            for transition in self.definition.transitions:
                if (transition.from_state == current_state and 
                    transition.transition_type == TransitionType.EVENT_DRIVEN and
                    transition.trigger_event == event['name']):
                    
                    # Check condition if present
                    if transition.condition:
                        if not await self._evaluate_condition(transition.condition):
                            continue
                    
                    # Execute transition
                    await self._execute_transition(current_state, transition.to_state, transition)
                    break
        except Exception as e:
            logger.error(f"Event processing failed: {str(e)}")
    
    def get_current_state(self) -> str:
        """Get current state"""
        return self.context.current_state
    
    def get_available_transitions(self) -> List[Transition]:
        """Get available transitions from current state"""
        current_state = self.context.current_state
        return [
            t for t in self.definition.transitions 
            if t.from_state == current_state
        ]
    
    def get_execution_history(self) -> List[StateExecution]:
        """Get execution history"""
        return self.executions.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'definition_id': self.definition.id,
            'status': self.status.value,
            'current_state': self.context.current_state,
            'context_data': self.context.data,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'executions': [asdict(exec) for exec in self.executions],
            'error_info': self.context.error_info
        }

class StateMachineCore:
    """Core state machine management system"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.definitions: Dict[str, StateMachineDefinition] = {}
        self.instances: Dict[str, StateMachineInstance] = {}
        self.running_instances: Set[str] = set()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.metrics = {
            'total_instances_created': 0,
            'total_instances_completed': 0,
            'total_instances_failed': 0,
            'total_state_executions': 0,
            'total_transitions': 0,
            'avg_execution_time': 0.0
        }
        
        # Initialize default state machine definitions
        self._initialize_default_definitions()
        
        logger.info(f"State Machine Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize state machine system"""
        try:
            logger.info("State Machine Core initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize State Machine Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start state machine system"""
        try:
            self.is_running = True
            
            # Start monitoring task
            self.monitoring_task = asyncio.create_task(self._monitor_instances())
            
            logger.info("State Machine Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start State Machine Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop state machine system"""
        try:
            self.is_running = False
            
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("State Machine Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop State Machine Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check if monitoring is running
            if self.is_running and (not self.monitoring_task or self.monitoring_task.done()):
                logger.warning("State machine monitoring is not running")
                return False
            
            # Check for stuck instances
            stuck_instances = 0
            for instance in self.instances.values():
                if (instance.status == StateMachineStatus.RUNNING and
                    instance.start_time and
                    (datetime.utcnow() - instance.start_time).total_seconds() > 3600):  # 1 hour
                    stuck_instances += 1
            
            if stuck_instances > len(self.instances) * 0.1:  # More than 10% stuck
                logger.warning(f"Too many stuck instances: {stuck_instances}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def _monitor_instances(self):
        """Monitor state machine instances"""
        while self.is_running:
            try:
                await self._check_timeouts()
                await self._update_metrics()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Instance monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_timeouts(self):
        """Check for timed out instances"""
        now = datetime.utcnow()
        
        for instance in list(self.instances.values()):
            if instance.status != StateMachineStatus.RUNNING:
                continue
            
            # Check global timeout
            if (instance.definition.global_timeout_seconds and
                instance.start_time and
                (now - instance.start_time).total_seconds() > instance.definition.global_timeout_seconds):
                
                instance.status = StateMachineStatus.FAILED
                instance.end_time = now
                instance.context.error_info = {
                    'error': 'Global timeout exceeded',
                    'timeout_seconds': instance.definition.global_timeout_seconds
                }
                logger.warning(f"State machine {instance.id} timed out")
    
    async def _update_metrics(self):
        """Update system metrics"""
        total_exec_time = 0.0
        total_executions = 0
        
        for instance in self.instances.values():
            for execution in instance.executions:
                if execution.status == ExecutionStatus.COMPLETED:
                    total_exec_time += execution.execution_time_ms
                    total_executions += 1
        
        if total_executions > 0:
            self.metrics['avg_execution_time'] = total_exec_time / total_executions
        
        self.metrics['total_state_executions'] = total_executions
    
    def _initialize_default_definitions(self):
        """Initialize default state machine definitions"""
        # Content approval workflow
        content_approval = StateMachineDefinition(
            id="content_approval_workflow",
            name="Content Approval Workflow",
            description="Workflow for content approval process",
            initial_state="submitted",
            final_states={"approved", "rejected"}
        )
        
        # Define states
        content_approval.states = {
            "submitted": StateDefinition(
                name="submitted",
                description="Content submitted for review",
                is_initial=True
            ),
            "under_review": StateDefinition(
                name="under_review",
                description="Content under review"
            ),
            "approved": StateDefinition(
                name="approved",
                description="Content approved",
                is_final=True
            ),
            "rejected": StateDefinition(
                name="rejected",
                description="Content rejected",
                is_final=True
            ),
            "revision_required": StateDefinition(
                name="revision_required",
                description="Content requires revision"
            )
        }
        
        # Define transitions
        content_approval.transitions = [
            Transition(
                from_state="submitted",
                to_state="under_review",
                transition_type=TransitionType.AUTOMATIC
            ),
            Transition(
                from_state="under_review",
                to_state="approved",
                transition_type=TransitionType.MANUAL
            ),
            Transition(
                from_state="under_review",
                to_state="rejected",
                transition_type=TransitionType.MANUAL
            ),
            Transition(
                from_state="under_review",
                to_state="revision_required",
                transition_type=TransitionType.MANUAL
            ),
            Transition(
                from_state="revision_required",
                to_state="under_review",
                transition_type=TransitionType.EVENT_DRIVEN,
                trigger_event="revision_submitted"
            )
        ]
        
        self.definitions[content_approval.id] = content_approval
    
    def register_definition(self, definition: StateMachineDefinition) -> bool:
        """Register state machine definition"""
        try:
            self.definitions[definition.id] = definition
            logger.info(f"Registered state machine definition: {definition.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register definition: {str(e)}")
            return False
    
    def get_definition(self, definition_id: str) -> Optional[StateMachineDefinition]:
        """Get state machine definition"""
        return self.definitions.get(definition_id)
    
    async def create_instance(self, definition_id: str, 
                             initial_data: Optional[Dict[str, Any]] = None,
                             instance_id: Optional[str] = None) -> Optional[str]:
        """Create state machine instance"""
        try:
            definition = self.definitions.get(definition_id)
            if not definition:
                raise Exception(f"Definition {definition_id} not found")
            
            instance = StateMachineInstance(definition, instance_id)
            self.instances[instance.id] = instance
            self.metrics['total_instances_created'] += 1
            
            logger.info(f"Created state machine instance {instance.id} from definition {definition_id}")
            return instance.id
            
        except Exception as e:
            logger.error(f"Failed to create instance: {str(e)}")
            return None
    
    async def start_instance(self, instance_id: str, 
                           initial_data: Optional[Dict[str, Any]] = None) -> bool:
        """Start state machine instance"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                raise Exception(f"Instance {instance_id} not found")
            
            success = await instance.start(initial_data)
            if success:
                self.running_instances.add(instance_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to start instance {instance_id}: {str(e)}")
            return False
    
    async def trigger_event(self, instance_id: str, event_name: str, 
                          event_data: Optional[Dict[str, Any]] = None) -> bool:
        """Trigger event on instance"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                raise Exception(f"Instance {instance_id} not found")
            
            return await instance.trigger_event(event_name, event_data)
            
        except Exception as e:
            logger.error(f"Failed to trigger event: {str(e)}")
            return False
    
    async def transition_instance(self, instance_id: str, target_state: str) -> bool:
        """Transition instance to target state"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                raise Exception(f"Instance {instance_id} not found")
            
            return await instance.transition_to(target_state)
            
        except Exception as e:
            logger.error(f"Failed to transition instance: {str(e)}")
            return False
    
    def get_instance(self, instance_id: str) -> Optional[StateMachineInstance]:
        """Get state machine instance"""
        return self.instances.get(instance_id)
    
    def get_instance_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get instance status"""
        instance = self.instances.get(instance_id)
        if not instance:
            return None
        
        return {
            'id': instance.id,
            'definition_id': instance.definition.id,
            'status': instance.status.value,
            'current_state': instance.context.current_state,
            'start_time': instance.start_time.isoformat() if instance.start_time else None,
            'end_time': instance.end_time.isoformat() if instance.end_time else None,
            'execution_count': len(instance.executions),
            'available_transitions': [
                {
                    'from_state': t.from_state,
                    'to_state': t.to_state,
                    'type': t.transition_type.value,
                    'trigger_event': t.trigger_event
                }
                for t in instance.get_available_transitions()
            ],
            'context_data': instance.context.data,
            'error_info': instance.context.error_info
        }
    
    def list_instances(self, definition_id: Optional[str] = None, 
                      status: Optional[StateMachineStatus] = None) -> List[Dict[str, Any]]:
        """List state machine instances"""
        instances = []
        
        for instance in self.instances.values():
            if definition_id and instance.definition.id != definition_id:
                continue
            if status and instance.status != status:
                continue
            
            instances.append({
                'id': instance.id,
                'definition_id': instance.definition.id,
                'definition_name': instance.definition.name,
                'status': instance.status.value,
                'current_state': instance.context.current_state,
                'start_time': instance.start_time.isoformat() if instance.start_time else None,
                'end_time': instance.end_time.isoformat() if instance.end_time else None
            })
        
        return instances
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        running_instances = len([i for i in self.instances.values() 
                               if i.status == StateMachineStatus.RUNNING])
        completed_instances = len([i for i in self.instances.values() 
                                 if i.status == StateMachineStatus.COMPLETED])
        failed_instances = len([i for i in self.instances.values() 
                              if i.status == StateMachineStatus.FAILED])
        
        return {
            'level': self.level,
            'total_definitions': len(self.definitions),
            'total_instances': len(self.instances),
            'running_instances': running_instances,
            'completed_instances': completed_instances,
            'failed_instances': failed_instances,
            'total_instances_created': self.metrics['total_instances_created'],
            'total_state_executions': self.metrics['total_state_executions'],
            'avg_execution_time_ms': self.metrics['avg_execution_time'],
            'success_rate': (
                completed_instances / len(self.instances) 
                if len(self.instances) > 0 else 0
            ),
            'failure_rate': (
                failed_instances / len(self.instances) 
                if len(self.instances) > 0 else 0
            ),
            'available_definitions': [
                {
                    'id': d.id,
                    'name': d.name,
                    'version': d.version,
                    'states_count': len(d.states),
                    'transitions_count': len(d.transitions)
                }
                for d in self.definitions.values()
            ],
            'is_running': self.is_running
        }

# Global instance
state_machine_core = StateMachineCore()

# Convenience functions
async def create_state_machine(definition_id: str, 
                              initial_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Create and start state machine instance"""
    instance_id = await state_machine_core.create_instance(definition_id)
    if instance_id:
        await state_machine_core.start_instance(instance_id, initial_data)
    return instance_id

async def trigger_state_machine_event(instance_id: str, event_name: str, 
                                     event_data: Optional[Dict[str, Any]] = None) -> bool:
    """Trigger event on state machine"""
    return await state_machine_core.trigger_event(instance_id, event_name, event_data)

def get_state_machine_status(instance_id: str) -> Optional[Dict[str, Any]]:
    """Get state machine status"""
    return state_machine_core.get_instance_status(instance_id)

# Module exports
__all__ = [
    "StateMachineCore", "StateMachineDefinition", "StateDefinition", "Transition",
    "StateMachineInstance", "StateContext", "StateExecution", "StateAction",
    "TransitionType", "ExecutionStatus", "StateMachineStatus",
    "state_machine_core", "create_state_machine", "trigger_state_machine_event",
    "get_state_machine_status"
]

logger.info("State Machine Core module loaded")