#!/usr/bin/env python3
"""Distributed State Machine - Advanced Saga State Management
============================================================

Distributed state machine implementation for complex saga workflows.
Supports parallel branches, state synchronization, and distributed
state transitions across microservices.

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
from typing import Dict, List, Optional, Any, Set, Callable, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class StateTransitionResult(Enum):
    """Result of state transition attempt"""
    SUCCESS = "success"
    INVALID = "invalid"
    BLOCKED = "blocked"
    ERROR = "error"


class SynchronizationResult(Enum):
    """Result of branch synchronization"""
    SUCCESS = "success"
    WAITING = "waiting"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class StateTransition:
    """Represents a state transition"""
    from_state: str
    to_state: str
    trigger_event: str
    condition: Optional[Callable] = None
    action: Optional[Callable] = None


@dataclass
class ParallelBranch:
    """Represents a parallel execution branch"""
    branch_id: str
    branch_name: str
    current_state: str
    started_at: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    
    def is_ready_for_sync(self) -> bool:
        """Check if branch is ready for synchronization"""
        return self.completed_at is not None


@dataclass
class StateHistory:
    """State transition history entry"""
    from_state: str
    to_state: str
    trigger_event: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


class DistributedStateMachine:
    """Distributed state machine for saga coordination"""
    
    def __init__(self, saga_id: str, initial_state: str):
        self.saga_id = saga_id
        self.current_states: Set[str] = {initial_state}
        self.state_history: List[StateHistory] = []
        self.state_data: Dict[str, Any] = {}
        self.parallel_branches: Dict[str, ParallelBranch] = {}
        self.transition_handlers: Dict[str, List[Callable]] = {}
        self.state_locks: Dict[str, asyncio.Lock] = {}
        self.created_at = datetime.now(timezone.utc)
    
    async def transition_to_state(
        self,
        target_state: str,
        trigger_event: str,
        context: Dict[str, Any] = None
    ) -> StateTransitionResult:
        """Transition to new state with validation"""
        context = context or {}
        
        # Validate transition
        if not await self._is_valid_transition(target_state, trigger_event):
            logger.warning(f"Invalid transition to {target_state} from {self.current_states}")
            return StateTransitionResult.INVALID
        
        # Acquire state lock
        async with self._get_state_lock(target_state):
            try:
                # Execute pre-transition hooks
                await self._execute_pre_transition_hooks(target_state, context)
                
                # Record current states for history
                previous_states = self.current_states.copy()
                
                # Update state
                await self._update_state(target_state, trigger_event, context)
                
                # Execute post-transition hooks
                await self._execute_post_transition_hooks(previous_states, target_state, context)
                
                # Check for saga completion
                if await self._is_saga_completed():
                    await self._handle_saga_completion()
                
                logger.info(f"State transition successful: {previous_states} -> {target_state}")
                return StateTransitionResult.SUCCESS
                
            except Exception as e:
                logger.error(f"State transition failed: {e}")
                return StateTransitionResult.ERROR
    
    async def start_parallel_branch(
        self,
        branch_name: str,
        initial_state: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Start parallel execution branch"""
        branch_id = f"{self.saga_id}_{branch_name}_{uuid.uuid4().hex[:8]}"
        
        branch = ParallelBranch(
            branch_id=branch_id,
            branch_name=branch_name,
            current_state=initial_state,
            started_at=datetime.now(timezone.utc),
            context=context or {}
        )
        
        self.parallel_branches[branch_id] = branch
        
        # Add parallel state to current states
        parallel_state = f"parallel_{branch_name}_{initial_state}"
        self.current_states.add(parallel_state)
        
        logger.info(f"Started parallel branch {branch_name} with ID {branch_id}")
        return branch_id
    
    async def complete_parallel_branch(
        self,
        branch_id: str,
        final_state: str,
        result: Dict[str, Any] = None
    ):
        """Mark parallel branch as completed"""
        if branch_id in self.parallel_branches:
            branch = self.parallel_branches[branch_id]
            branch.current_state = final_state
            branch.completed_at = datetime.now(timezone.utc)
            branch.result = result or {}
            
            logger.info(f"Completed parallel branch {branch_id} with state {final_state}")
    
    async def synchronize_parallel_branches(
        self,
        branch_names: List[str],
        target_state: str,
        timeout_seconds: float = 300.0
    ) -> tuple[SynchronizationResult, Optional[Dict[str, Any]]]:
        """Synchronize parallel branches to common state"""
        start_time = datetime.now(timezone.utc)
        timeout_time = start_time + timedelta(seconds=timeout_seconds)
        
        while datetime.now(timezone.utc) < timeout_time:
            # Find branches for synchronization
            target_branches = []
            for branch_id, branch in self.parallel_branches.items():
                if any(name in branch.branch_name for name in branch_names):
                    target_branches.append(branch)
            
            # Check if all branches are ready
            ready_branches = [b for b in target_branches if b.is_ready_for_sync()]
            
            if len(ready_branches) == len(branch_names):
                # All branches ready - merge and synchronize
                merged_context = await self._merge_branch_contexts(ready_branches)
                
                # Transition to synchronized state
                await self.transition_to_state(target_state, "branches_synchronized", merged_context)
                
                # Cleanup completed branches
                for branch in ready_branches:
                    if branch.branch_id in self.parallel_branches:
                        del self.parallel_branches[branch.branch_id]
                
                logger.info(f"Successfully synchronized {len(ready_branches)} branches to {target_state}")
                return SynchronizationResult.SUCCESS, merged_context
            
            # Wait before checking again
            await asyncio.sleep(1.0)
        
        # Timeout reached
        logger.warning(f"Synchronization timeout for branches {branch_names}")
        return SynchronizationResult.TIMEOUT, None
    
    async def _is_valid_transition(self, target_state: str, trigger_event: str) -> bool:
        """Validate if transition is allowed"""
        # For demo purposes, allow most transitions
        # In real implementation, this would check transition rules
        
        # Block transitions to same state
        if target_state in self.current_states:
            return False
        
        # Check for conflicting states
        if target_state == "saga_failed" and "saga_completed" in self.current_states:
            return False
        
        if target_state == "saga_completed" and "saga_failed" in self.current_states:
            return False
        
        return True
    
    async def _update_state(
        self,
        target_state: str,
        trigger_event: str,
        context: Dict[str, Any]
    ):
        """Update state machine state"""
        # Record history
        for current_state in self.current_states:
            self.state_history.append(StateHistory(
                from_state=current_state,
                to_state=target_state,
                trigger_event=trigger_event,
                timestamp=datetime.now(timezone.utc),
                context=context.copy()
            ))
        
        # Update current states
        if target_state.startswith("parallel_"):
            # Parallel state - add to current states
            self.current_states.add(target_state)
        else:
            # Regular state - replace current states
            self.current_states = {target_state}
        
        # Update state data
        self.state_data.update(context)
    
    async def _execute_pre_transition_hooks(
        self,
        target_state: str,
        context: Dict[str, Any]
    ):
        """Execute pre-transition hooks"""
        hooks = self.transition_handlers.get(f"pre_{target_state}", [])
        for hook in hooks:
            try:
                await hook(self, target_state, context)
            except Exception as e:
                logger.error(f"Pre-transition hook failed: {e}")
    
    async def _execute_post_transition_hooks(
        self,
        previous_states: Set[str],
        target_state: str,
        context: Dict[str, Any]
    ):
        """Execute post-transition hooks"""
        hooks = self.transition_handlers.get(f"post_{target_state}", [])
        for hook in hooks:
            try:
                await hook(self, previous_states, target_state, context)
            except Exception as e:
                logger.error(f"Post-transition hook failed: {e}")
    
    async def _is_saga_completed(self) -> bool:
        """Check if saga is completed"""
        completion_states = {"saga_completed", "saga_failed", "compensation_completed"}
        return bool(self.current_states.intersection(completion_states))
    
    async def _handle_saga_completion(self):
        """Handle saga completion"""
        logger.info(f"Saga {self.saga_id} completed with states: {self.current_states}")
        
        # Cleanup parallel branches
        self.parallel_branches.clear()
    
    async def _merge_branch_contexts(
        self,
        branches: List[ParallelBranch]
    ) -> Dict[str, Any]:
        """Merge contexts from parallel branches"""
        merged_context = {}
        
        for branch in branches:
            branch_key = f"branch_{branch.branch_name}"
            merged_context[branch_key] = {
                "state": branch.current_state,
                "result": branch.result,
                "execution_time": (
                    (branch.completed_at - branch.started_at).total_seconds()
                    if branch.completed_at else 0
                ),
                "context": branch.context
            }
        
        return merged_context
    
    def _get_state_lock(self, state: str) -> asyncio.Lock:
        """Get lock for state to prevent race conditions"""
        if state not in self.state_locks:
            self.state_locks[state] = asyncio.Lock()
        return self.state_locks[state]
    
    def register_transition_handler(
        self,
        event_type: str,
        handler: Callable
    ):
        """Register transition handler"""
        if event_type not in self.transition_handlers:
            self.transition_handlers[event_type] = []
        self.transition_handlers[event_type].append(handler)
    
    def get_current_state(self) -> Set[str]:
        """Get current state(s)"""
        return self.current_states.copy()
    
    def get_state_history(self) -> List[StateHistory]:
        """Get state transition history"""
        return self.state_history.copy()
    
    def get_parallel_branches(self) -> List[Dict[str, Any]]:
        """Get information about parallel branches"""
        return [
            {
                "branch_id": branch.branch_id,
                "branch_name": branch.branch_name,
                "current_state": branch.current_state,
                "started_at": branch.started_at,
                "completed_at": branch.completed_at,
                "is_ready": branch.is_ready_for_sync()
            }
            for branch in self.parallel_branches.values()
        ]


class ContentProcessingStateMachine(DistributedStateMachine):
    """Specialized state machine for content processing saga"""
    
    # State definitions
    STATES = {
        "content_uploaded": "Content uploaded successfully",
        "ai_analysis_started": "AI analysis in progress",
        "ai_analysis_completed": "AI analysis completed",
        "protection_started": "Content protection in progress",
        "protection_applied": "Content protection applied",
        "seo_optimization_started": "SEO optimization in progress",
        "seo_optimized": "SEO optimization completed",
        "distribution_started": "Distribution in progress",
        "distribution_completed": "Distribution completed",
        "saga_completed": "Saga completed successfully",
        "saga_failed": "Saga failed",
        "compensation_started": "Compensation in progress",
        "compensation_completed": "Compensation completed"
    }
    
    def __init__(self, saga_id: str):
        super().__init__(saga_id, "content_uploaded")
        self._setup_content_processing_transitions()
    
    def _setup_content_processing_transitions(self):
        """Setup content processing specific transitions"""
        # Register transition handlers
        self.register_transition_handler(
            "post_ai_analysis_completed",
            self._handle_ai_analysis_completed
        )
        
        self.register_transition_handler(
            "post_protection_applied",
            self._check_distribution_ready
        )
        
        self.register_transition_handler(
            "post_seo_optimized",
            self._check_distribution_ready
        )
    
    async def _handle_ai_analysis_completed(
        self,
        state_machine: 'DistributedStateMachine',
        previous_states: Set[str],
        target_state: str,
        context: Dict[str, Any]
    ):
        """Handle AI analysis completion - start parallel branches"""
        if target_state == "ai_analysis_completed":
            # Start parallel branches for protection and SEO
            protection_branch = await self.start_parallel_branch(
                "protection", "protection_started", {"ai_result": context.get("ai_result")}
            )
            
            seo_branch = await self.start_parallel_branch(
                "seo", "seo_optimization_started", {"ai_result": context.get("ai_result")}
            )
            
            logger.info(f"Started parallel branches: protection={protection_branch}, seo={seo_branch}")
    
    async def _check_distribution_ready(
        self,
        state_machine: 'DistributedStateMachine',
        previous_states: Set[str],
        target_state: str,
        context: Dict[str, Any]
    ):
        """Check if ready for distribution after protection or SEO"""
        # Check if both protection and SEO parallel branches are completed
        protection_ready = any("protection" in branch.branch_name and branch.is_ready_for_sync() 
                             for branch in self.parallel_branches.values())
        
        seo_ready = any("seo" in branch.branch_name and branch.is_ready_for_sync() 
                       for branch in self.parallel_branches.values())
        
        if protection_ready and seo_ready:
            # Synchronize branches and proceed to distribution
            sync_result, merged_context = await self.synchronize_parallel_branches(
                ["protection", "seo"], "distribution_started"
            )
            
            if sync_result == SynchronizationResult.SUCCESS:
                logger.info("Ready for distribution - branches synchronized")


class StateMachineManager:
    """Manager for multiple distributed state machines"""
    
    def __init__(self):
        self.state_machines: Dict[str, DistributedStateMachine] = {}
    
    def create_state_machine(
        self,
        saga_id: str,
        machine_type: str = "generic",
        initial_state: str = "initialized"
    ) -> DistributedStateMachine:
        """Create new state machine"""
        if machine_type == "content_processing":
            state_machine = ContentProcessingStateMachine(saga_id)
        else:
            state_machine = DistributedStateMachine(saga_id, initial_state)
        
        self.state_machines[saga_id] = state_machine
        logger.info(f"Created {machine_type} state machine for saga {saga_id}")
        
        return state_machine
    
    def get_state_machine(self, saga_id: str) -> Optional[DistributedStateMachine]:
        """Get state machine by saga ID"""
        return self.state_machines.get(saga_id)
    
    def remove_state_machine(self, saga_id: str):
        """Remove state machine"""
        if saga_id in self.state_machines:
            del self.state_machines[saga_id]
            logger.info(f"Removed state machine for saga {saga_id}")
    
    def list_active_state_machines(self) -> List[Dict[str, Any]]:
        """List all active state machines"""
        return [
            {
                "saga_id": saga_id,
                "current_states": list(sm.current_states),
                "created_at": sm.created_at,
                "parallel_branches": len(sm.parallel_branches)
            }
            for saga_id, sm in self.state_machines.items()
        ]
    
    async def get_aggregate_status(self) -> Dict[str, Any]:
        """Get aggregate status of all state machines"""
        total_machines = len(self.state_machines)
        completed_machines = 0
        failed_machines = 0
        active_machines = 0
        
        for sm in self.state_machines.values():
            if "saga_completed" in sm.current_states:
                completed_machines += 1
            elif "saga_failed" in sm.current_states:
                failed_machines += 1
            else:
                active_machines += 1
        
        return {
            "total_machines": total_machines,
            "active_machines": active_machines,
            "completed_machines": completed_machines,
            "failed_machines": failed_machines,
            "success_rate": completed_machines / total_machines if total_machines > 0 else 0
        }


# Global state machine manager
_state_machine_manager: Optional[StateMachineManager] = None


def get_state_machine_manager() -> StateMachineManager:
    """Get global state machine manager"""
    global _state_machine_manager
    if _state_machine_manager is None:
        _state_machine_manager = StateMachineManager()
    
    return _state_machine_manager


def create_content_processing_state_machine(saga_id: str) -> ContentProcessingStateMachine:
    """Convenience function to create content processing state machine"""
    manager = get_state_machine_manager()
    return manager.create_state_machine(saga_id, "content_processing")


__all__ = [
    "DistributedStateMachine",
    "ContentProcessingStateMachine",
    "StateMachineManager",
    "StateTransitionResult",
    "SynchronizationResult",
    "StateTransition",
    "ParallelBranch",
    "StateHistory",
    "get_state_machine_manager",
    "create_content_processing_state_machine"
]