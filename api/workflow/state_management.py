"""Workflow state management and persistence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set, Union
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
import json
import uuid
import logging
from contextlib import asynccontextmanager

from ..core.exceptions import StateManagementException
from ..models.workflow import WorkflowState, WorkflowCheckpoint
from ..database.connection import DatabaseManager
from ..utils.serialization import JsonEncoder, JsonDecoder
from ..utils.locking import DistributedLock
from ..utils.metrics import MetricsCollector


class StateTransitionType(Enum):
    """
Types of state transitions."""

    INITIALIZATION = "initialization"
    STAGE_COMPLETION = "stage_completion"
    ERROR_HANDLING = "error_handling"
    COMPENSATION = "compensation"
    TIMEOUT = "timeout"
    CANCELLATION = "cancellation"
    RETRY = "retry"
    RECOVERY = "recovery"


class PersistenceLevel(Enum):
    """Levels of state persistence."""

    NONE = "none"  # In-memory only
    CHECKPOINT = "checkpoint"  # Save at checkpoints
    STAGE = "stage"  # Save after each stage
    CONTINUOUS = "continuous"  # Save all changes


@dataclass
class StateSnapshot:
    """Immutable snapshot of workflow state."""
    workflow_id: str
    timestamp: datetime
    stage_index: int
    stage_results: Dict[str, Any]
    variables: Dict[str, Any]
    error_log: List[Dict[str, Any]]
    execution_path: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    checksum: str = field(init=False)
    
    def __post_init__(self):
        # Calculate checksum for integrity verification
        content = {
            "workflow_id": self.workflow_id,
            "stage_index": self.stage_index,
            "stage_results": self.stage_results,
            "variables": self.variables,
            "error_log": self.error_log,
            "execution_path": self.execution_path,
            "metadata": self.metadata
        }
        self.checksum = hash(json.dumps(content, sort_keys=True, cls=JsonEncoder))
    
    def verify_integrity(self) -> bool:
        """Verify snapshot integrity."""
        expected_checksum = self.checksum
        # Recalculate checksum
        self.__post_init__()
        return self.checksum == expected_checksum
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateSnapshot':
        """
Create from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class StateTransition:
    """Record of state transition."""
    transition_id: str
    workflow_id: str
    transition_type: StateTransitionType
    from_stage: Optional[str]
    to_stage: Optional[str]
    timestamp: datetime
    duration_ms: int
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary."""
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat(),
            "transition_type": self.transition_type.value
        }


class WorkflowStateManager:
    """Manages workflow state with persistence and recovery."""
    
    def __init__(
        self,
        persistence_level: PersistenceLevel = PersistenceLevel.STAGE,
        checkpoint_interval: int = 300,  # 5 minutes
        state_retention_days: int = 30
    ):
        self.logger = logging.getLogger("workflow.state_manager")
        self.db_manager = DatabaseManager()
        self.metrics = MetricsCollector()
        
        # Configuration
        self.persistence_level = persistence_level
        self.checkpoint_interval = checkpoint_interval
        self.state_retention_days = state_retention_days
        
        # In-memory state cache
        self.workflow_states = {}
        self.state_snapshots = {}
        self.state_transitions = {}
        
        # Background tasks
        self.checkpoint_task = None
        self.cleanup_task = None
        
        # Distributed locking for state consistency
        self.locks = {}
    
    async def initialize(self):
        """Initialize state manager."""
        self.logger.info("Initializing workflow state manager")
        
        # Start background tasks
        if self.persistence_level in [PersistenceLevel.CHECKPOINT, PersistenceLevel.CONTINUOUS]:
            self.checkpoint_task = asyncio.create_task(self._checkpoint_loop())
        
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Load active workflow states from persistence
        await self._load_active_states()
    
    async def shutdown(self):
        """Shutdown state manager."""
        self.logger.info("Shutting down workflow state manager")
        
        # Cancel background tasks
        if self.checkpoint_task:
            self.checkpoint_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Save all pending states
        await self._save_all_states()
    
    @asynccontextmanager
    async def workflow_state_lock(self, workflow_id: str):
        """Get distributed lock for workflow state."""
        lock_key = f"workflow_state:{workflow_id}"
        
        if lock_key not in self.locks:
            self.locks[lock_key] = DistributedLock(lock_key)
        
        async with self.locks[lock_key]:
            yield
    
    async def create_workflow_state(
        self,
        workflow_id: str,
        template_id: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowState:
        """Create new workflow state."""
        async with self.workflow_state_lock(workflow_id):
            if workflow_id in self.workflow_states:
                raise StateManagementException(f"Workflow state {workflow_id} already exists")
            
            # Create initial state
            state = WorkflowState(
                workflow_id=workflow_id,
                template_id=template_id,
                input_data=input_data,
                stage_index=0,
                stage_results={},
                variables={},
                error_log=[],
                execution_path=[],
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.workflow_states[workflow_id] = state
            
            # Record state transition
            await self._record_state_transition(
                workflow_id=workflow_id,
                transition_type=StateTransitionType.INITIALIZATION,
                from_stage=None,
                to_stage="initialized",
                success=True,
                metadata={"template_id": template_id}
            )
            
            # Save if needed
            if self.persistence_level in [PersistenceLevel.STAGE, PersistenceLevel.CONTINUOUS]:
                await self._save_state(workflow_id)
            
            self.logger.info(f"Created workflow state for {workflow_id}")
            return state
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state."""
        # Try memory cache first
        if workflow_id in self.workflow_states:
            return self.workflow_states[workflow_id]
        
        # Try loading from persistence
        state = await self._load_state(workflow_id)
        if state:
            self.workflow_states[workflow_id] = state
        
        return state
    
    async def update_workflow_state(
        self,
        workflow_id: str,
        updates: Dict[str, Any]
    ) -> WorkflowState:
        """
Update workflow state."""
        async with self.workflow_state_lock(workflow_id):
            state = await self.get_workflow_state(workflow_id)
            if not state:
                raise StateManagementException(f"Workflow state {workflow_id} not found")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            
            state.updated_at = datetime.utcnow()
            
            # Save if needed
            if self.persistence_level in [PersistenceLevel.STAGE, PersistenceLevel.CONTINUOUS]:
                await self._save_state(workflow_id)
            
            return state
    
    async def advance_workflow_stage(
        self,
        workflow_id: str,
        new_stage_index: int,
        stage_result: Dict[str, Any],
        stage_name: Optional[str] = None
    ) -> WorkflowState:
        """Advance workflow to next stage."""
        async with self.workflow_state_lock(workflow_id):
            state = await self.get_workflow_state(workflow_id)
            if not state:
                raise StateManagementException(f"Workflow state {workflow_id} not found")
            
            # Record previous stage
            previous_stage = f"stage_{state.stage_index}"
            current_stage = f"stage_{new_stage_index}"
            
            # Update state
            state.stage_index = new_stage_index
            state.stage_results[previous_stage] = {
                "result": stage_result,
                "completed_at": datetime.utcnow().isoformat(),
                "duration": stage_result.get("duration", 0)
            }
            
            # Add to execution path
            state.execution_path.append({
                "stage": previous_stage,
                "stage_name": stage_name,
                "completed_at": datetime.utcnow().isoformat(),
                "success": stage_result.get("success", True),
                "duration": stage_result.get("duration", 0)
            })
            
            state.updated_at = datetime.utcnow()
            
            # Record state transition
            await self._record_state_transition(
                workflow_id=workflow_id,
                transition_type=StateTransitionType.STAGE_COMPLETION,
                from_stage=previous_stage,
                to_stage=current_stage,
                success=stage_result.get("success", True),
                metadata={"stage_result": stage_result}
            )
            
            # Create snapshot for important stages
            if new_stage_index % 3 == 0:  # Every 3rd stage
                await self.create_state_snapshot(workflow_id)
            
            # Save state
            if self.persistence_level in [PersistenceLevel.STAGE, PersistenceLevel.CONTINUOUS]:
                await self._save_state(workflow_id)
            
            self.logger.info(f"Advanced workflow {workflow_id} from {previous_stage} to {current_stage}")
            return state
    
    async def handle_workflow_error(
        self,
        workflow_id: str,
        error: str,
        stage_name: Optional[str] = None,
        error_type: str = "execution",
        recoverable: bool = True
    ) -> WorkflowState:
        """Handle workflow error."""
        async with self.workflow_state_lock(workflow_id):
            state = await self.get_workflow_state(workflow_id)
            if not state:
                raise StateManagementException(f"Workflow state {workflow_id} not found")
            
            # Add error to log
            error_entry = {
                "error": error,
                "error_type": error_type,
                "stage": stage_name or f"stage_{state.stage_index}",
                "timestamp": datetime.utcnow().isoformat(),
                "recoverable": recoverable
            }
            state.error_log.append(error_entry)
            state.updated_at = datetime.utcnow()
            
            # Record state transition
            await self._record_state_transition(
                workflow_id=workflow_id,
                transition_type=StateTransitionType.ERROR_HANDLING,
                from_stage=f"stage_{state.stage_index}",
                to_stage=f"error_stage_{state.stage_index}",
                success=False,
                error=error,
                metadata={"error_type": error_type, "recoverable": recoverable}
            )
            
            # Create error snapshot
            await self.create_state_snapshot(workflow_id, snapshot_type="error")
            
            # Save state
            if self.persistence_level in [PersistenceLevel.STAGE, PersistenceLevel.CONTINUOUS]:
                await self._save_state(workflow_id)
            
            self.logger.error(f"Recorded error for workflow {workflow_id}: {error}")
            return state
    
    async def set_workflow_variable(
        self,
        workflow_id: str,
        key: str,
        value: Any
    ) -> WorkflowState:
        """Set workflow variable."""
        async with self.workflow_state_lock(workflow_id):
            state = await self.get_workflow_state(workflow_id)
            if not state:
                raise StateManagementException(f"Workflow state {workflow_id} not found")
            
            state.variables[key] = value
            state.updated_at = datetime.utcnow()
            
            # Save if continuous persistence
            if self.persistence_level == PersistenceLevel.CONTINUOUS:
                await self._save_state(workflow_id)
            
            return state
    
    async def get_workflow_variable(
        self,
        workflow_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Get workflow variable."""
        state = await self.get_workflow_state(workflow_id)
        if not state:
            return default
        
        return state.variables.get(key, default)
    
    async def create_state_snapshot(
        self,
        workflow_id: str,
        snapshot_type: str = "checkpoint"
    ) -> StateSnapshot:
        """Create state snapshot."""
        state = await self.get_workflow_state(workflow_id)
        if not state:
            raise StateManagementException(f"Workflow state {workflow_id} not found")
        
        snapshot = StateSnapshot(
            workflow_id=workflow_id,
            timestamp=datetime.utcnow(),
            stage_index=state.stage_index,
            stage_results=state.stage_results.copy(),
            variables=state.variables.copy(),
            error_log=state.error_log.copy(),
            execution_path=state.execution_path.copy(),
            metadata={
                **state.metadata,
                "snapshot_type": snapshot_type
            }
        )
        
        # Store snapshot
        snapshot_key = f"{workflow_id}:{snapshot.timestamp.isoformat()}"
        self.state_snapshots[snapshot_key] = snapshot
        
        # Save snapshot to persistence
        if self.persistence_level != PersistenceLevel.NONE:
            await self._save_snapshot(snapshot)
        
        self.logger.info(f"Created {snapshot_type} snapshot for workflow {workflow_id}")
        return snapshot
    
    async def restore_from_snapshot(
        self,
        workflow_id: str,
        snapshot_timestamp: Optional[datetime] = None
    ) -> WorkflowState:
        """Restore workflow state from snapshot."""
        async with self.workflow_state_lock(workflow_id):
            # Find appropriate snapshot
            snapshot = await self._find_snapshot(workflow_id, snapshot_timestamp)
            if not snapshot:
                raise StateManagementException(
                    f"No snapshot found for workflow {workflow_id}"
                )
            
            # Verify snapshot integrity
            if not snapshot.verify_integrity():
                raise StateManagementException(
                    f"Snapshot integrity check failed for workflow {workflow_id}"
                )
            
            # Restore state
            state = WorkflowState(
                workflow_id=workflow_id,
                template_id=snapshot.metadata.get("template_id", "unknown"),
                input_data=snapshot.metadata.get("input_data", {}),
                stage_index=snapshot.stage_index,
                stage_results=snapshot.stage_results,
                variables=snapshot.variables,
                error_log=snapshot.error_log,
                execution_path=snapshot.execution_path,
                metadata=snapshot.metadata,
                created_at=snapshot.metadata.get("created_at", snapshot.timestamp),
                updated_at=datetime.utcnow()
            )
            
            self.workflow_states[workflow_id] = state
            
            # Record recovery transition
            await self._record_state_transition(
                workflow_id=workflow_id,
                transition_type=StateTransitionType.RECOVERY,
                from_stage="error",
                to_stage=f"stage_{snapshot.stage_index}",
                success=True,
                metadata={
                    "snapshot_timestamp": snapshot.timestamp.isoformat(),
                    "recovered_from": snapshot.metadata.get("snapshot_type", "unknown")
                }
            )
            
            # Save restored state
            if self.persistence_level in [PersistenceLevel.STAGE, PersistenceLevel.CONTINUOUS]:
                await self._save_state(workflow_id)
            
            self.logger.info(f"Restored workflow {workflow_id} from snapshot at {snapshot.timestamp}")
            return state
    
    async def get_workflow_history(
        self,
        workflow_id: str,
        include_transitions: bool = True,
        include_snapshots: bool = False
    ) -> Dict[str, Any]:
        """Get comprehensive workflow history."""
        state = await self.get_workflow_state(workflow_id)
        if not state:
            return {}
        
        history = {
            "workflow_id": workflow_id,
            "current_state": {
                "stage_index": state.stage_index,
                "variables": state.variables,
                "error_count": len(state.error_log),
                "stage_count": len(state.stage_results),
                "created_at": state.created_at.isoformat(),
                "updated_at": state.updated_at.isoformat()
            },
            "execution_path": state.execution_path,
            "error_log": state.error_log
        }
        
        if include_transitions:
            transitions = [
                transition.to_dict() 
                for transition in self.state_transitions.values()
                if transition.workflow_id == workflow_id
            ]
            transitions.sort(key=lambda x: x["timestamp"])
            history["state_transitions"] = transitions
        
        if include_snapshots:
            snapshots = [
                snapshot.to_dict()
                for snapshot in self.state_snapshots.values()
                if snapshot.workflow_id == workflow_id
            ]
            snapshots.sort(key=lambda x: x["timestamp"])
            history["snapshots"] = snapshots
        
        return history
    
    async def cleanup_workflow_state(self, workflow_id: str) -> bool:
        """Clean up workflow state and related data."""
        async with self.workflow_state_lock(workflow_id):
            # Remove from memory
            if workflow_id in self.workflow_states:
                del self.workflow_states[workflow_id]
            
            # Remove snapshots
            snapshots_to_remove = [
                key for key in self.state_snapshots.keys()
                if key.startswith(workflow_id)
            ]
            for key in snapshots_to_remove:
                del self.state_snapshots[key]
            
            # Remove transitions
            transitions_to_remove = [
                key for key, transition in self.state_transitions.items()
                if transition.workflow_id == workflow_id
            ]
            for key in transitions_to_remove:
                del self.state_transitions[key]
            
            # Remove from persistence
            if self.persistence_level != PersistenceLevel.NONE:
                await self._delete_persisted_state(workflow_id)
            
            self.logger.info(f"Cleaned up state for workflow {workflow_id}")
            return True
    
    async def get_state_metrics(self) -> Dict[str, Any]:
        """Get state management metrics."""
        active_states = len(self.workflow_states)
        total_snapshots = len(self.state_snapshots)
        total_transitions = len(self.state_transitions)
        
        # Calculate error rates
        recent_transitions = [
            t for t in self.state_transitions.values()
            if t.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        error_rate = (
            sum(1 for t in recent_transitions if not t.success) / len(recent_transitions) * 100
            if recent_transitions else 0
        )
        
        return {
            "active_workflow_states": active_states,
            "total_snapshots": total_snapshots,
            "total_state_transitions": total_transitions,
            "error_rate_24h": error_rate,
            "persistence_level": self.persistence_level.value,
            "checkpoint_interval": self.checkpoint_interval,
            "memory_usage_mb": self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage of state data."""
        total_size = 0
        
        # Estimate state sizes
        for state in self.workflow_states.values():
            state_json = json.dumps(state.__dict__, cls=JsonEncoder)
            total_size += len(state_json.encode('utf-8'))
        
        # Estimate snapshot sizes
        for snapshot in self.state_snapshots.values():
            snapshot_json = json.dumps(snapshot.to_dict(), cls=JsonEncoder)
            total_size += len(snapshot_json.encode('utf-8'))
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    async def _record_state_transition(
        self,
        workflow_id: str,
        transition_type: StateTransitionType,
        from_stage: Optional[str],
        to_stage: Optional[str],
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: int = 0
    ):
        """
Record state transition."""
        transition_id = f"{workflow_id}_{uuid.uuid4().hex[:8]}"
        
        transition = StateTransition(
            transition_id=transition_id,
            workflow_id=workflow_id,
            transition_type=transition_type,
            from_stage=from_stage,
            to_stage=to_stage,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms,
            success=success,
            metadata=metadata or {},
            error=error
        )
        
        self.state_transitions[transition_id] = transition
        
        # Save transition if persistent
        if self.persistence_level != PersistenceLevel.NONE:
            await self._save_transition(transition)
    
    async def _checkpoint_loop(self):
        """Background checkpoint loop."""
        while True:
            try:
                await asyncio.sleep(self.checkpoint_interval)
                
                # Create checkpoints for active workflows
                for workflow_id in list(self.workflow_states.keys()):
                    try:
                        await self.create_state_snapshot(workflow_id, "checkpoint")
                    except Exception as e:
                        self.logger.error(f"Error creating checkpoint for {workflow_id}: {e}")
                
            except Exception as e:
                self.logger.error(f"Error in checkpoint loop: {e}")
                await asyncio.sleep(60)  # Back off on error
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff_date = datetime.utcnow() - timedelta(days=self.state_retention_days)
                
                # Clean up old snapshots
                snapshots_to_remove = []
                for key, snapshot in self.state_snapshots.items():
                    if snapshot.timestamp < cutoff_date:
                        snapshots_to_remove.append(key)
                
                for key in snapshots_to_remove:
                    del self.state_snapshots[key]
                
                # Clean up old transitions
                transitions_to_remove = []
                for key, transition in self.state_transitions.items():
                    if transition.timestamp < cutoff_date:
                        transitions_to_remove.append(key)
                
                for key in transitions_to_remove:
                    del self.state_transitions[key]
                
                if snapshots_to_remove or transitions_to_remove:
                    self.logger.info(
                        f"Cleaned up {len(snapshots_to_remove)} snapshots "
                        f"and {len(transitions_to_remove)} transitions"
                    )
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _load_active_states(self):
        """Load active workflow states from persistence."""
        if self.persistence_level == PersistenceLevel.NONE:
            return
        
        try:
            # Implementation would load states from database
            # Placeholder for actual database loading
            self.logger.info("Loaded active workflow states from persistence")
        except Exception as e:
            self.logger.error(f"Error loading active states: {e}")
    
    async def _save_state(self, workflow_id: str):
        """Save workflow state to persistence."""
        if self.persistence_level == PersistenceLevel.NONE:
            return
        
        state = self.workflow_states.get(workflow_id)
        if not state:
            return
        
        try:
            # Implementation would save state to database
            # Placeholder for actual database saving
            pass
        except Exception as e:
            self.logger.error(f"Error saving state for {workflow_id}: {e}")
    
    async def _load_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow state from persistence."""
        if self.persistence_level == PersistenceLevel.NONE:
            return None
        
        try:
            # Implementation would load state from database
            # Placeholder for actual database loading
            return None
        except Exception as e:
            self.logger.error(f"Error loading state for {workflow_id}: {e}")
            return None
    
    async def _save_all_states(self):
        """Save all workflow states to persistence."""
        for workflow_id in self.workflow_states.keys():
            await self._save_state(workflow_id)
    
    async def _save_snapshot(self, snapshot: StateSnapshot):
        """
Save snapshot to persistence."""
        try:
            # Implementation would save snapshot to database
            # Placeholder for actual database saving
            pass
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
    
    async def _save_transition(self, transition: StateTransition):
        """Save state transition to persistence."""
        try:
            # Implementation would save transition to database
            # Placeholder for actual database saving
            pass
        except Exception as e:
            self.logger.error(f"Error saving transition: {e}")
    
    async def _find_snapshot(
        self, 
        workflow_id: str, 
        timestamp: Optional[datetime] = None
    ) -> Optional[StateSnapshot]:
        """Find appropriate snapshot for workflow."""
        workflow_snapshots = [
            snapshot for snapshot in self.state_snapshots.values()
            if snapshot.workflow_id == workflow_id
        ]
        
        if not workflow_snapshots:
            return None
        
        if timestamp:
            # Find snapshot closest to timestamp
            closest_snapshot = min(
                workflow_snapshots,
                key=lambda s: abs((s.timestamp - timestamp).total_seconds())
            )
            return closest_snapshot
        else:
            # Return most recent snapshot
            return max(workflow_snapshots, key=lambda s: s.timestamp)
    
    async def _delete_persisted_state(self, workflow_id: str):
        """
Delete persisted state data."""
        try:
            # Implementation would delete from database
            # Placeholder for actual database deletion
            pass
        except Exception as e:
            self.logger.error(f"Error deleting persisted state for {workflow_id}: {e}")
