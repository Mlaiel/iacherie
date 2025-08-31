"""State Manager - Enterprise State Management & Transition Control System

Advanced state management system providing centralized state coordination,
transition control, and state persistence for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This state management system is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization.

🎯 BUSINESS LOGIC:
State Definition → Transition Rules → State Changes → Validation → Persistence → Notification
"""import asyncio
import uuid
import threading
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set, Union, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import weakref

logger = logging.getLogger(__name__)


class StateType(Enum):
    """Types of states managed by the system"""    WORKFLOW_STATE = "workflow_state"
    PROCESS_STATE = "process_state"
    TASK_STATE = "task_state"
    RESOURCE_STATE = "resource_state"
    USER_SESSION_STATE = "user_session_state"
    CONTENT_STATE = "content_state"
    PROTECTION_STATE = "protection_state"
    MONETIZATION_STATE = "monetization_state"
    SYSTEM_STATE = "system_state"


class TransitionType(Enum):
    """Types of state transitions"""    AUTOMATIC = "automatic"
    MANUAL = "manual"
    CONDITIONAL = "conditional"
    TIMED = "timed"
    EVENT_DRIVEN = "event_driven"
    ROLLBACK = "rollback"


class TransitionRule(Enum):
    """State transition validation rules"""    STRICT = "strict"
    LENIENT = "lenient"
    CONDITIONAL = "conditional"
    CUSTOM = "custom"


class StateStatus(Enum):
    """State status indicators"""    ACTIVE = "active"
    INACTIVE = "inactive"
    TRANSITIONING = "transitioning"
    LOCKED = "locked"
    ERROR = "error"
    SUSPENDED = "suspended"


@dataclass
class StateTransition:
    """State transition definition"""    from_state: str
    to_state: str
    transition_type: TransitionType
    conditions: Dict[str, Any] = field(default_factory=dict)
    validators: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    timeout_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateDefinition:
    """Complete state definition"""    state_id: str
    name: str
    state_type: StateType
    properties: Dict[str, Any] = field(default_factory=dict)
    allowed_transitions: List[StateTransition] = field(default_factory=list)
    entry_actions: List[str] = field(default_factory=list)
    exit_actions: List[str] = field(default_factory=list)
    validators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateInstance:
    """Active state instance"""    instance_id: str
    state_id: str
    entity_id: str
    current_data: Dict[str, Any]
    status: StateStatus
    created_at: datetime
    updated_at: datetime
    version: int = 1
    locked_by: Optional[str] = None
    lock_expires_at: Optional[datetime] = None
    transition_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TransitionRequest:
    """State transition request"""    request_id: str
    instance_id: str
    target_state: str
    initiator: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    force: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class StateManager:
    """Enterprise state management and transition control system"""    
    def __init__(self, persistence_enabled: bool = True):
        self.persistence_enabled = persistence_enabled
        
        # State registry
        self.state_definitions: Dict[str, StateDefinition] = {}
        self.state_instances: Dict[str, StateInstance] = {}
        self.pending_transitions: Dict[str, TransitionRequest] = {}
        
        # Transition management
        self.transition_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        self.transition_validators: Dict[str, Callable] = {}
        self.transition_actions: Dict[str, Callable] = {}
        
        # Event handling
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.state_listeners: Dict[str, List[Callable]] = defaultdict(list)
        self.entity_listeners: Dict[str, List[Callable]] = defaultdict(list)
        
        # Performance tracking
        self.transition_metrics: Dict[str, List[float]] = defaultdict(list)
        self.state_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Persistence and recovery
        self.state_snapshots: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.recovery_points: Dict[str, Dict[str, Any]] = {}
        
        # Initialize standard states
        self._initialize_standard_states()
        
        logger.info("StateManager initialized successfully")
    
    def _initialize_standard_states(self):
        """Initialize standard business state definitions"""        # Content Processing States
        content_states = [
            StateDefinition(
                state_id="content_uploaded",
                name="Content Uploaded",
                state_type=StateType.CONTENT_STATE,
                properties={"stage": "initial", "processing_required": True},
                allowed_transitions=[
                    StateTransition(
                        from_state="content_uploaded",
                        to_state="content_analyzing",
                        transition_type=TransitionType.AUTOMATIC,
                        validators=["validate_content_format"]
                    )
                ],
                entry_actions=["log_content_upload", "validate_file_integrity"]
            ),
            
            StateDefinition(
                state_id="content_analyzing",
                name="Content Analyzing",
                state_type=StateType.CONTENT_STATE,
                properties={"stage": "processing", "ai_processing": True},
                allowed_transitions=[
                    StateTransition(
                        from_state="content_analyzing",
                        to_state="content_analyzed",
                        transition_type=TransitionType.AUTOMATIC,
                        conditions={"analysis_complete": True}
                    ),
                    StateTransition(
                        from_state="content_analyzing",
                        to_state="content_analysis_failed",
                        transition_type=TransitionType.CONDITIONAL,
                        conditions={"analysis_error": True}
                    )
                ]
            ),
            
            StateDefinition(
                state_id="content_analyzed",
                name="Content Analyzed",
                state_type=StateType.CONTENT_STATE,
                properties={"stage": "analyzed", "ready_for_protection": True},
                allowed_transitions=[
                    StateTransition(
                        from_state="content_analyzed",
                        to_state="fingerprinting",
                        transition_type=TransitionType.AUTOMATIC
                    )
                ]
            )
        ]
        
        # Protection States
        protection_states = [
            StateDefinition(
                state_id="fingerprinting",
                name="Generating Fingerprints",
                state_type=StateType.PROTECTION_STATE,
                properties={"protection_level": "active", "fingerprint_types": ["audio", "video", "image"]},
                allowed_transitions=[
                    StateTransition(
                        from_state="fingerprinting",
                        to_state="fingerprinted",
                        transition_type=TransitionType.AUTOMATIC,
                        conditions={"fingerprints_generated": True}
                    )
                ]
            ),
            
            StateDefinition(
                state_id="fingerprinted",
                name="Content Fingerprinted",
                state_type=StateType.PROTECTION_STATE,
                properties={"protection_level": "protected", "monitoring_active": True},
                allowed_transitions=[
                    StateTransition(
                        from_state="fingerprinted",
                        to_state="monitoring_active",
                        transition_type=TransitionType.AUTOMATIC
                    )
                ]
            ),
            
            StateDefinition(
                state_id="monitoring_active",
                name="Active Monitoring",
                state_type=StateType.PROTECTION_STATE,
                properties={"protection_level": "monitoring", "alerts_enabled": True},
                allowed_transitions=[
                    StateTransition(
                        from_state="monitoring_active",
                        to_state="violation_detected",
                        transition_type=TransitionType.EVENT_DRIVEN,
                        conditions={"violation_found": True}
                    )
                ]
            )
        ]
        
        # Monetization States
        monetization_states = [
            StateDefinition(
                state_id="revenue_tracking_setup",
                name="Revenue Tracking Setup",
                state_type=StateType.MONETIZATION_STATE,
                properties={"tracking_enabled": False, "platforms_connected": False},
                allowed_transitions=[
                    StateTransition(
                        from_state="revenue_tracking_setup",
                        to_state="revenue_tracking_active",
                        transition_type=TransitionType.MANUAL,
                        conditions={"platforms_configured": True}
                    )
                ]
            ),
            
            StateDefinition(
                state_id="revenue_tracking_active",
                name="Revenue Tracking Active",
                state_type=StateType.MONETIZATION_STATE,
                properties={"tracking_enabled": True, "sync_frequency": "daily"},
                allowed_transitions=[
                    StateTransition(
                        from_state="revenue_tracking_active",
                        to_state="revenue_calculated",
                        transition_type=TransitionType.TIMED,
                        timeout_seconds=86400  # Daily
                    )
                ]
            )
        ]
        
        # Register all standard states
        all_states = content_states + protection_states + monetization_states
        for state_def in all_states:
            self.register_state(state_def)
    
    def register_state(self, state_definition: StateDefinition) -> bool:
        """Register a new state definition"""        try:
            # Validate state definition
            if not self._validate_state_definition(state_definition):
                return False
            
            self.state_definitions[state_definition.state_id] = state_definition
            logger.info(f"State registered: {state_definition.state_id}")
            return True
            
        except Exception as e:
            logger.error(f"State registration failed: {e}")
            return False
    
    def _validate_state_definition(self, state_def: StateDefinition) -> bool:
        """Validate state definition integrity"""        try:
            # Required fields validation
            if not all([state_def.state_id, state_def.name, state_def.state_type]):
                logger.error("Missing required state definition fields")
                return False
            
            # Validate transitions
            for transition in state_def.allowed_transitions:
                if transition.from_state != state_def.state_id:
                    logger.error(f"Invalid transition from_state: {transition.from_state}")
                    return False
            
            # Validate validators exist
            for validator_name in state_def.validators:
                if validator_name not in self.transition_validators:
                    logger.warning(f"Validator not found: {validator_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"State definition validation error: {e}")
            return False
    
    async def create_state_instance(
        self,
        state_id: str,
        entity_id: str,
        initial_data: Dict[str, Any] = None
    ) -> str:
        """Create a new state instance for an entity"""        try:
            if state_id not in self.state_definitions:
                raise ValueError(f"State definition '{state_id}' not found")
            
            state_def = self.state_definitions[state_id]
            instance_id = str(uuid.uuid4())
            
            # Create state instance
            instance = StateInstance(
                instance_id=instance_id,
                state_id=state_id,
                entity_id=entity_id,
                current_data=initial_data or {},
                status=StateStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Execute entry actions
            await self._execute_actions(state_def.entry_actions, instance)
            
            # Store instance
            self.state_instances[instance_id] = instance
            
            # Create recovery point
            await self._create_recovery_point(instance_id)
            
            # Emit state created event
            await self._emit_state_event("state_created", instance)
            
            logger.info(f"State instance created: {instance_id} for entity {entity_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"State instance creation failed: {e}")
            raise
    
    async def transition_state(
        self,
        instance_id: str,
        target_state: str,
        initiator: str,
        parameters: Dict[str, Any] = None,
        force: bool = False
    ) -> bool:
        """Transition state instance to target state"""        try:
            if instance_id not in self.state_instances:
                raise ValueError(f"State instance '{instance_id}' not found")
            
            instance = self.state_instances[instance_id]
            
            # Check if instance is locked
            if not force and self._is_instance_locked(instance):
                logger.warning(f"State instance {instance_id} is locked")
                return False
            
            # Lock instance for transition
            await self._lock_instance(instance_id, initiator)
            
            try:
                # Validate transition
                if not await self._validate_transition(instance, target_state, parameters or {}):
                    logger.error(f"Transition validation failed: {instance.state_id} -> {target_state}")
                    return False
                
                # Create transition request
                request = TransitionRequest(
                    request_id=str(uuid.uuid4()),
                    instance_id=instance_id,
                    target_state=target_state,
                    initiator=initiator,
                    parameters=parameters or {},
                    force=force
                )
                
                # Execute transition
                success = await self._execute_transition(request)
                
                if success:
                    logger.info(f"State transition successful: {instance.state_id} -> {target_state}")
                else:
                    logger.error(f"State transition failed: {instance.state_id} -> {target_state}")
                
                return success
                
            finally:
                # Always unlock instance
                await self._unlock_instance(instance_id)
                
        except Exception as e:
            logger.error(f"State transition failed: {e}")
            return False
    
    async def _validate_transition(
        self,
        instance: StateInstance,
        target_state: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """Validate if transition is allowed"""        try:
            state_def = self.state_definitions.get(instance.state_id)
            if not state_def:
                return False
            
            # Find matching transition
            valid_transition = None
            for transition in state_def.allowed_transitions:
                if transition.to_state == target_state:
                    valid_transition = transition
                    break
            
            if not valid_transition:
                logger.error(f"No valid transition found: {instance.state_id} -> {target_state}")
                return False
            
            # Check conditions
            if not await self._check_transition_conditions(
                valid_transition.conditions, instance, parameters
            ):
                logger.error(f"Transition conditions not met: {instance.state_id} -> {target_state}")
                return False
            
            # Run validators
            for validator_name in valid_transition.validators:
                if validator_name in self.transition_validators:
                    validator_func = self.transition_validators[validator_name]
                    if not await self._run_validator(validator_func, instance, parameters):
                        logger.error(f"Validator failed: {validator_name}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Transition validation error: {e}")
            return False
    
    async def _check_transition_conditions(
        self,
        conditions: Dict[str, Any],
        instance: StateInstance,
        parameters: Dict[str, Any]
    ) -> bool:
        """Check if transition conditions are satisfied"""        try:
            for condition_key, condition_value in conditions.items():
                # Check in instance data
                if condition_key in instance.current_data:
                    if instance.current_data[condition_key] != condition_value:
                        return False
                
                # Check in parameters
                elif condition_key in parameters:
                    if parameters[condition_key] != condition_value:
                        return False
                
                # Check predefined conditions
                elif condition_key == "analysis_complete":
                    if not instance.current_data.get("analysis_results"):
                        return False
                
                elif condition_key == "fingerprints_generated":
                    if not instance.current_data.get("fingerprints"):
                        return False
                
                else:
                    # Unknown condition
                    logger.warning(f"Unknown condition: {condition_key}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition checking failed: {e}")
            return False
    
    async def _run_validator(
        self,
        validator_func: Callable,
        instance: StateInstance,
        parameters: Dict[str, Any]
    ) -> bool:
        """Run transition validator function"""        try:
            if asyncio.iscoroutinefunction(validator_func):
                return await validator_func(instance, parameters)
            else:
                return validator_func(instance, parameters)
        except Exception as e:
            logger.error(f"Validator execution failed: {e}")
            return False
    
    async def _execute_transition(self, request: TransitionRequest) -> bool:
        """Execute state transition"""        try:
            instance = self.state_instances[request.instance_id]
            old_state_id = instance.state_id
            
            # Get state definitions
            old_state_def = self.state_definitions.get(old_state_id)
            new_state_def = self.state_definitions.get(request.target_state)
            
            if not new_state_def:
                logger.error(f"Target state definition not found: {request.target_state}")
                return False
            
            # Execute exit actions for old state
            if old_state_def:
                await self._execute_actions(old_state_def.exit_actions, instance)
            
            # Create snapshot before transition
            await self._create_state_snapshot(instance)
            
            # Update instance state
            instance.state_id = request.target_state
            instance.updated_at = datetime.now(timezone.utc)
            instance.version += 1
            
            # Merge parameters into instance data
            instance.current_data.update(request.parameters)
            
            # Record transition in history
            transition_record = {
                "from_state": old_state_id,
                "to_state": request.target_state,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "initiator": request.initiator,
                "request_id": request.request_id,
                "parameters": request.parameters
            }
            instance.transition_history.append(transition_record)
            
            # Execute entry actions for new state
            await self._execute_actions(new_state_def.entry_actions, instance)
            
            # Emit transition event
            await self._emit_state_event("state_transitioned", instance, {
                "from_state": old_state_id,
                "to_state": request.target_state,
                "initiator": request.initiator
            })
            
            # Create new recovery point
            await self._create_recovery_point(request.instance_id)
            
            # Track performance
            transition_key = f"{old_state_id}->{request.target_state}"
            self.transition_metrics[transition_key].append(
                (datetime.now(timezone.utc) - request.created_at).total_seconds()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Transition execution failed: {e}")
            return False
    
    async def _execute_actions(self, actions: List[str], instance: StateInstance):
        """Execute state entry/exit actions"""        try:
            for action_name in actions:
                if action_name in self.transition_actions:
                    action_func = self.transition_actions[action_name]
                    try:
                        if asyncio.iscoroutinefunction(action_func):
                            await action_func(instance)
                        else:
                            action_func(instance)
                    except Exception as e:
                        logger.error(f"Action execution failed: {action_name} - {e}")
                else:
                    logger.warning(f"Action not found: {action_name}")
                    
        except Exception as e:
            logger.error(f"Actions execution failed: {e}")
    
    def _is_instance_locked(self, instance: StateInstance) -> bool:
        """Check if state instance is locked"""        if not instance.locked_by:
            return False
        
        if instance.lock_expires_at and instance.lock_expires_at <= datetime.now(timezone.utc):
            # Lock expired
            instance.locked_by = None
            instance.lock_expires_at = None
            return False
        
        return True
    
    async def _lock_instance(self, instance_id: str, locker: str, timeout_seconds: int = 300):
        """Lock state instance for transition"""        instance = self.state_instances[instance_id]
        instance.locked_by = locker
        instance.lock_expires_at = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)
        logger.debug(f"State instance locked: {instance_id} by {locker}")
    
    async def _unlock_instance(self, instance_id: str):
        """Unlock state instance"""        instance = self.state_instances[instance_id]
        instance.locked_by = None
        instance.lock_expires_at = None
        logger.debug(f"State instance unlocked: {instance_id}")
    
    async def _create_state_snapshot(self, instance: StateInstance):
        """Create state snapshot for recovery"""        try:
            snapshot = {
                "instance_id": instance.instance_id,
                "state_id": instance.state_id,
                "entity_id": instance.entity_id,
                "current_data": instance.current_data.copy(),
                "status": instance.status.value,
                "version": instance.version,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.state_snapshots[instance.instance_id].append(snapshot)
            
            # Keep only last 10 snapshots
            if len(self.state_snapshots[instance.instance_id]) > 10:
                self.state_snapshots[instance.instance_id].pop(0)
                
        except Exception as e:
            logger.error(f"Snapshot creation failed: {e}")
    
    async def _create_recovery_point(self, instance_id: str):
        """Create recovery point for state instance"""        try:
            instance = self.state_instances[instance_id]
            
            recovery_point = {
                "instance_id": instance_id,
                "state_id": instance.state_id,
                "entity_id": instance.entity_id,
                "current_data": instance.current_data.copy(),
                "version": instance.version,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            self.recovery_points[instance_id] = recovery_point
            
        except Exception as e:
            logger.error(f"Recovery point creation failed: {e}")
    
    async def rollback_state(self, instance_id: str, target_version: Optional[int] = None) -> bool:
        """Rollback state to previous version or snapshot"""        try:
            if instance_id not in self.state_instances:
                logger.error(f"State instance not found: {instance_id}")
                return False
            
            snapshots = self.state_snapshots.get(instance_id, [])
            if not snapshots:
                logger.error(f"No snapshots available for rollback: {instance_id}")
                return False
            
            # Find target snapshot
            target_snapshot = None
            if target_version:
                for snapshot in reversed(snapshots):
                    if snapshot["version"] == target_version:
                        target_snapshot = snapshot
                        break
            else:
                # Use latest snapshot
                target_snapshot = snapshots[-1]
            
            if not target_snapshot:
                logger.error(f"Target snapshot not found: {instance_id}")
                return False
            
            # Restore state from snapshot
            instance = self.state_instances[instance_id]
            instance.state_id = target_snapshot["state_id"]
            instance.current_data = target_snapshot["current_data"].copy()
            instance.version = target_snapshot["version"]
            instance.updated_at = datetime.now(timezone.utc)
            instance.status = StateStatus.ACTIVE
            
            # Record rollback in history
            rollback_record = {
                "action": "rollback",
                "target_version": target_snapshot["version"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": "manual_rollback"
            }
            instance.transition_history.append(rollback_record)
            
            # Emit rollback event
            await self._emit_state_event("state_rolled_back", instance, {
                "target_version": target_snapshot["version"]
            })
            
            logger.info(f"State rolled back: {instance_id} to version {target_snapshot['version']}")
            return True
            
        except Exception as e:
            logger.error(f"State rollback failed: {e}")
            return False
    
    async def _emit_state_event(
        self,
        event_type: str,
        instance: StateInstance,
        additional_data: Dict[str, Any] = None
    ):
        """Emit state events to registered handlers"""        try:
            event_data = {
                "event_type": event_type,
                "instance_id": instance.instance_id,
                "state_id": instance.state_id,
                "entity_id": instance.entity_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if additional_data:
                event_data.update(additional_data)
            
            # Call registered event handlers
            for handler in self.event_handlers.get(event_type, []):
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")
            
            # Call state-specific listeners
            for listener in self.state_listeners.get(instance.state_id, []):
                try:
                    await listener(event_data)
                except Exception as e:
                    logger.error(f"State listener failed: {e}")
            
            # Call entity-specific listeners
            for listener in self.entity_listeners.get(instance.entity_id, []):
                try:
                    await listener(event_data)
                except Exception as e:
                    logger.error(f"Entity listener failed: {e}")
                    
        except Exception as e:
            logger.error(f"Event emission failed: {e}")
    
    def get_state_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get state instance information"""        instance = self.state_instances.get(instance_id)
        if not instance:
            return None
        
        return {
            "instance_id": instance.instance_id,
            "state_id": instance.state_id,
            "entity_id": instance.entity_id,
            "current_data": instance.current_data,
            "status": instance.status.value,
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat(),
            "version": instance.version,
            "locked_by": instance.locked_by,
            "lock_expires_at": instance.lock_expires_at.isoformat() if instance.lock_expires_at else None,
            "transition_count": len(instance.transition_history)
        }
    
    def get_entity_states(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all state instances for an entity"""        entity_instances = []
        
        for instance in self.state_instances.values():
            if instance.entity_id == entity_id:
                entity_instances.append(self.get_state_instance(instance.instance_id))
        
        return entity_instances
    
    def get_state_metrics(self) -> Dict[str, Any]:
        """Get state management metrics"""        total_instances = len(self.state_instances)
        active_instances = len([i for i in self.state_instances.values() if i.status == StateStatus.ACTIVE])
        locked_instances = len([i for i in self.state_instances.values() if self._is_instance_locked(i)])
        
        # Calculate transition statistics
        transition_stats = {}
        for transition_key, times in self.transition_metrics.items():
            if times:
                transition_stats[transition_key] = {
                    "count": len(times),
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times)
                }
        
        return {
            "total_instances": total_instances,
            "active_instances": active_instances,
            "locked_instances": locked_instances,
            "registered_states": len(self.state_definitions),
            "transition_statistics": transition_stats,
            "snapshots_count": sum(len(snapshots) for snapshots in self.state_snapshots.values()),
            "recovery_points": len(self.recovery_points)
        }
    
    def register_validator(self, name: str, validator_func: Callable):
        """Register state transition validator"""        self.transition_validators[name] = validator_func
        logger.info(f"Validator registered: {name}")
    
    def register_action(self, name: str, action_func: Callable):
        """Register state entry/exit action"""        self.transition_actions[name] = action_func
        logger.info(f"Action registered: {name}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for state events"""        self.event_handlers[event_type].append(handler)
    
    def register_state_listener(self, state_id: str, listener: Callable):
        """Register listener for specific state"""        self.state_listeners[state_id].append(listener)
    
    def register_entity_listener(self, entity_id: str, listener: Callable):
        """Register listener for specific entity"""        self.entity_listeners[entity_id].append(listener)
    
    async def cleanup_expired_instances(self) -> int:
        """Cleanup expired and inactive state instances"""        try:
            cleanup_count = 0
            current_time = datetime.now(timezone.utc)
            expired_instances = []
            
            for instance_id, instance in self.state_instances.items():
                # Remove expired locks
                if (instance.lock_expires_at and 
                    instance.lock_expires_at <= current_time):
                    instance.locked_by = None
                    instance.lock_expires_at = None
                
                # Mark inactive instances for cleanup (older than 30 days)
                if (instance.status == StateStatus.INACTIVE and
                    (current_time - instance.updated_at).days > 30):
                    expired_instances.append(instance_id)
            
            # Remove expired instances
            for instance_id in expired_instances:
                del self.state_instances[instance_id]
                if instance_id in self.recovery_points:
                    del self.recovery_points[instance_id]
                if instance_id in self.state_snapshots:
                    del self.state_snapshots[instance_id]
                cleanup_count += 1
            
            if cleanup_count > 0:
                logger.info(f"Cleaned up {cleanup_count} expired state instances")
            
            return cleanup_count
            
        except Exception as e:
            logger.error(f"State cleanup failed: {e}")
            return 0
    
    def shutdown(self):
        """Shutdown state manager and cleanup"""        try:
            # Unlock all locked instances
            for instance in self.state_instances.values():
                instance.locked_by = None
                instance.lock_expires_at = None
            
            logger.info("StateManager shutdown completed")
            
        except Exception as e:
            logger.error(f"StateManager shutdown failed: {e}")
