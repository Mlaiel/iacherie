"""Collaboration Conflict Resolver
AI-powered conflict resolution system for simultaneous collaborative edits.

Provides:
- Real-time conflict detection
- Automatic conflict resolution strategies  
- Manual conflict resolution workflows
- Operational transformation algorithms
- Version reconciliation
- Change attribution and tracking
- Rollback and undo mechanisms

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import difflib
from collections import defaultdict

from fastapi import WebSocket
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of collaboration conflicts"""
    SIMULTANEOUS_EDIT = "simultaneous_edit"
    RESOURCE_LOCK = "resource_lock"
    VERSION_DIVERGENCE = "version_divergence"
    PERMISSION_CONFLICT = "permission_conflict"
    DATA_INTEGRITY = "data_integrity"
    OPERATIONAL_TRANSFORM = "operational_transform"


class ConflictSeverity(Enum):
    """Conflict severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    AUTOMATIC_MERGE = "automatic_merge"
    LAST_WRITER_WINS = "last_writer_wins"
    FIRST_WRITER_WINS = "first_writer_wins"
    MANUAL_RESOLUTION = "manual_resolution"
    AI_ASSISTED = "ai_assisted"
    OPERATIONAL_TRANSFORM = "operational_transform"
    THREE_WAY_MERGE = "three_way_merge"


class OperationType(Enum):
    """Types of operations"""
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    MOVE = "move"
    FORMAT = "format"
    METADATA = "metadata"


@dataclass
class Operation:
    """Individual operation in collaborative editing"""
    operation_id: str
    user_id: str
    operation_type: OperationType
    target_resource: str
    position: int
    length: int
    content: Any
    timestamp: datetime
    vector_clock: Dict[str, int]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictEvent:
    """Conflict event representation"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    resource_id: str
    conflicting_operations: List[Operation]
    conflicting_users: List[str]
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolved_by: Optional[str] = None
    resolution_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorClock:
    """Vector clock for distributed operations ordering"""
    clocks: Dict[str, int] = field(default_factory=dict)
    
    def increment(self, user_id: str):
        """Increment clock for user"""
        self.clocks[user_id] = self.clocks.get(user_id, 0) + 1
    
    def update(self, other_clock: 'VectorClock'):
        """Update with another vector clock"""
        for user_id, clock in other_clock.clocks.items():
            self.clocks[user_id] = max(self.clocks.get(user_id, 0), clock)
    
    def compare(self, other_clock: 'VectorClock') -> str:
        """Compare with another vector clock"""
        self_greater = False
        other_greater = False
        
        all_users = set(self.clocks.keys()) | set(other_clock.clocks.keys())
        
        for user_id in all_users:
            self_time = self.clocks.get(user_id, 0)
            other_time = other_clock.clocks.get(user_id, 0)
            
            if self_time > other_time:
                self_greater = True
            elif self_time < other_time:
                other_greater = True
        
        if self_greater and not other_greater:
            return "after"
        elif other_greater and not self_greater:
            return "before"
        elif not self_greater and not other_greater:
            return "equal"
        else:
            return "concurrent"


@dataclass
class ResourceState:
    """State of a collaborative resource"""
    resource_id: str
    content: Any
    version: int
    last_modified: datetime
    last_modified_by: str
    vector_clock: VectorClock
    pending_operations: List[Operation] = field(default_factory=list)
    active_locks: Dict[str, str] = field(default_factory=dict)  # user_id -> lock_type
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationSession:
    """Collaboration session state"""
    session_id: str
    project_id: str
    participants: Set[str]
    resources: Dict[str, ResourceState]
    vector_clocks: Dict[str, VectorClock]  # user_id -> vector_clock
    conflict_history: List[ConflictEvent]
    operation_log: List[Operation]
    created_at: datetime
    last_activity: datetime
    settings: Dict[str, Any] = field(default_factory=dict)


class CollaborationConflictResolver:
    """
    AI-powered conflict resolution system for collaborative editing
    """
    
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.message_handlers: Dict[str, callable] = {}
        self.conflict_detectors: Dict[str, callable] = {}
        self.resolution_strategies: Dict[str, callable] = {}
        self.operational_transformer = OperationalTransformer()
        
        self._setup_handlers()
        self._setup_conflict_detectors()
        self._setup_resolution_strategies()
    
    def _setup_handlers(self):
        """Setup message handlers"""
        self.message_handlers = {
            "submit_operation": self._handle_submit_operation,
            "request_lock": self._handle_request_lock,
            "release_lock": self._handle_release_lock,
            "resolve_conflict": self._handle_resolve_conflict,
            "request_sync": self._handle_request_sync,
            "undo_operation": self._handle_undo_operation,
            "redo_operation": self._handle_redo_operation,
            "get_conflict_history": self._handle_get_conflict_history
        }
    
    def _setup_conflict_detectors(self):
        """Setup conflict detection methods"""
        self.conflict_detectors = {
            ConflictType.SIMULTANEOUS_EDIT: self._detect_simultaneous_edit,
            ConflictType.RESOURCE_LOCK: self._detect_resource_lock,
            ConflictType.VERSION_DIVERGENCE: self._detect_version_divergence,
            ConflictType.PERMISSION_CONFLICT: self._detect_permission_conflict,
            ConflictType.DATA_INTEGRITY: self._detect_data_integrity,
            ConflictType.OPERATIONAL_TRANSFORM: self._detect_operational_transform
        }
    
    def _setup_resolution_strategies(self):
        """Setup resolution strategies"""
        self.resolution_strategies = {
            ResolutionStrategy.AUTOMATIC_MERGE: self._resolve_automatic_merge,
            ResolutionStrategy.LAST_WRITER_WINS: self._resolve_last_writer_wins,
            ResolutionStrategy.FIRST_WRITER_WINS: self._resolve_first_writer_wins,
            ResolutionStrategy.MANUAL_RESOLUTION: self._resolve_manual,
            ResolutionStrategy.AI_ASSISTED: self._resolve_ai_assisted,
            ResolutionStrategy.OPERATIONAL_TRANSFORM: self._resolve_operational_transform,
            ResolutionStrategy.THREE_WAY_MERGE: self._resolve_three_way_merge
        }
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket connection for conflict resolution"""
        try:
            await websocket.accept()
            self.websocket_connections[user_id] = websocket
            
            logger.info(f"Conflict resolution connection established for user {user_id}")
            
            # Send connection confirmation
            await self._send_to_user(user_id, {
                "type": "connection_established",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_message(user_id, message)
                    
                except Exception as e:
                    logger.error(f"Error handling message from {user_id}: {e}")
                    await self._send_error(user_id, str(e))
        
        except Exception as e:
            logger.error(f"WebSocket connection error for {user_id}: {e}")
        
        finally:
            await self._cleanup_user_connection(user_id)
    
    async def _handle_message(self, user_id: str, message: Dict[str, Any]):
        """Route messages to appropriate handlers"""
        message_type = message.get("type")
        handler = self.message_handlers.get(message_type)
        
        if handler:
            await handler(user_id, message)
        else:
            await self._send_error(user_id, f"Unknown message type: {message_type}")
    
    async def create_collaboration_session(self, session_id: str, project_id: str,
                                         participants: List[str]) -> Dict[str, Any]:
        """Create new collaboration session"""
        try:
            session = CollaborationSession(
                session_id=session_id,
                project_id=project_id,
                participants=set(participants),
                resources={},
                vector_clocks={user_id: VectorClock() for user_id in participants},
                conflict_history=[],
                operation_log=[],
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            self.sessions[session_id] = session
            
            logger.info(f"Collaboration session {session_id} created for project {project_id}")
            
            return {
                "status": "success",
                "session_id": session_id,
                "project_id": project_id,
                "participants": participants,
                "message": "Collaboration session created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating collaboration session: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_submit_operation(self, user_id: str, message: Dict[str, Any]):
        """Handle operation submission"""
        try:
            session_id = message.get("session_id")
            operation_data = message.get("operation")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            if user_id not in session.participants:
                await self._send_error(user_id, "Not a participant in this session")
                return
            
            # Create operation
            operation = Operation(
                operation_id=f"op_{uuid.uuid4().hex[:12]}",
                user_id=user_id,
                operation_type=OperationType(operation_data.get("type")),
                target_resource=operation_data.get("resource_id"),
                position=operation_data.get("position", 0),
                length=operation_data.get("length", 0),
                content=operation_data.get("content"),
                timestamp=datetime.utcnow(),
                vector_clock=session.vector_clocks[user_id].clocks.copy(),
                metadata=operation_data.get("metadata", {})
            )
            
            # Update vector clock
            session.vector_clocks[user_id].increment(user_id)
            operation.vector_clock = session.vector_clocks[user_id].clocks.copy()
            
            # Detect conflicts
            conflicts = await self._detect_conflicts(session, operation)
            
            if conflicts:
                # Handle conflicts
                for conflict in conflicts:
                    await self._handle_conflict(session, conflict)
            else:
                # Apply operation
                await self._apply_operation(session, operation)
            
            # Log operation
            session.operation_log.append(operation)
            session.last_activity = datetime.utcnow()
            
            # Broadcast operation to other participants
            await self._broadcast_operation(session_id, operation, exclude_user=user_id)
            
            logger.info(f"Operation {operation.operation_id} submitted by {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling operation submission: {e}")
            await self._send_error(user_id, str(e))
    
    async def _detect_conflicts(self, session: CollaborationSession, 
                              operation: Operation) -> List[ConflictEvent]:
        """Detect conflicts for an operation"""
        conflicts = []
        
        # Check all conflict types
        for conflict_type, detector in self.conflict_detectors.items():
            detected_conflicts = await detector(session, operation)
            conflicts.extend(detected_conflicts)
        
        return conflicts
    
    async def _detect_simultaneous_edit(self, session: CollaborationSession,
                                      operation: Operation) -> List[ConflictEvent]:
        """Detect simultaneous edit conflicts"""
        conflicts = []
        
        resource_id = operation.target_resource
        if resource_id not in session.resources:
            return conflicts
        
        resource = session.resources[resource_id]
        
        # Check for overlapping operations in pending queue
        for pending_op in resource.pending_operations:
            if (pending_op.user_id != operation.user_id and
                self._operations_overlap(operation, pending_op)):
                
                conflict = ConflictEvent(
                    conflict_id=f"conflict_{uuid.uuid4().hex[:12]}",
                    conflict_type=ConflictType.SIMULTANEOUS_EDIT,
                    severity=ConflictSeverity.MEDIUM,
                    resource_id=resource_id,
                    conflicting_operations=[operation, pending_op],
                    conflicting_users=[operation.user_id, pending_op.user_id],
                    detected_at=datetime.utcnow()
                )
                conflicts.append(conflict)
        
        return conflicts
    
    async def _detect_resource_lock(self, session: CollaborationSession,
                                  operation: Operation) -> List[ConflictEvent]:
        """Detect resource lock conflicts"""
        conflicts = []
        
        resource_id = operation.target_resource
        if resource_id not in session.resources:
            return conflicts
        
        resource = session.resources[resource_id]
        
        # Check if resource is locked by another user
        for lock_user, lock_type in resource.active_locks.items():
            if lock_user != operation.user_id:
                conflict = ConflictEvent(
                    conflict_id=f"conflict_{uuid.uuid4().hex[:12]}",
                    conflict_type=ConflictType.RESOURCE_LOCK,
                    severity=ConflictSeverity.HIGH,
                    resource_id=resource_id,
                    conflicting_operations=[operation],
                    conflicting_users=[operation.user_id, lock_user],
                    detected_at=datetime.utcnow(),
                    metadata={"lock_type": lock_type, "lock_holder": lock_user}
                )
                conflicts.append(conflict)
        
        return conflicts
    
    async def _detect_version_divergence(self, session: CollaborationSession,
                                       operation: Operation) -> List[ConflictEvent]:
        """Detect version divergence conflicts"""
        conflicts = []
        
        # Compare vector clocks to detect divergence
        for user_id, user_clock in session.vector_clocks.items():
            if user_id != operation.user_id:
                op_clock = VectorClock()
                op_clock.clocks = operation.vector_clock
                
                comparison = user_clock.compare(op_clock)
                if comparison == "concurrent":
                    conflict = ConflictEvent(
                        conflict_id=f"conflict_{uuid.uuid4().hex[:12]}",
                        conflict_type=ConflictType.VERSION_DIVERGENCE,
                        severity=ConflictSeverity.HIGH,
                        resource_id=operation.target_resource,
                        conflicting_operations=[operation],
                        conflicting_users=[operation.user_id, user_id],
                        detected_at=datetime.utcnow(),
                        metadata={"vector_clocks": {
                            operation.user_id: operation.vector_clock,
                            user_id: user_clock.clocks
                        }}
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    async def _detect_permission_conflict(self, session: CollaborationSession,
                                        operation: Operation) -> List[ConflictEvent]:
        """Detect permission conflicts"""
        # Simplified implementation - in production would check actual permissions
        return []
    
    async def _detect_data_integrity(self, session: CollaborationSession,
                                   operation: Operation) -> List[ConflictEvent]:
        """Detect data integrity conflicts"""
        # Simplified implementation - would validate data consistency
        return []
    
    async def _detect_operational_transform(self, session: CollaborationSession,
                                          operation: Operation) -> List[ConflictEvent]:
        """Detect operational transform conflicts"""
        conflicts = []
        
        resource_id = operation.target_resource
        if resource_id not in session.resources:
            return conflicts
        
        resource = session.resources[resource_id]
        
        # Check for operations that need transformation
        for pending_op in resource.pending_operations:
            if (pending_op.user_id != operation.user_id and
                self._needs_transformation(operation, pending_op)):
                
                conflict = ConflictEvent(
                    conflict_id=f"conflict_{uuid.uuid4().hex[:12]}",
                    conflict_type=ConflictType.OPERATIONAL_TRANSFORM,
                    severity=ConflictSeverity.LOW,
                    resource_id=resource_id,
                    conflicting_operations=[operation, pending_op],
                    conflicting_users=[operation.user_id, pending_op.user_id],
                    detected_at=datetime.utcnow()
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _operations_overlap(self, op1: Operation, op2: Operation) -> bool:
        """Check if two operations overlap"""
        if op1.target_resource != op2.target_resource:
            return False
        
        # Check position overlap
        op1_end = op1.position + op1.length
        op2_end = op2.position + op2.length
        
        return not (op1_end <= op2.position or op2_end <= op1.position)
    
    def _needs_transformation(self, op1: Operation, op2: Operation) -> bool:
        """Check if operations need operational transformation"""
        return (op1.target_resource == op2.target_resource and
                op1.operation_type in [OperationType.INSERT, OperationType.DELETE] and
                op2.operation_type in [OperationType.INSERT, OperationType.DELETE])
    
    async def _handle_conflict(self, session: CollaborationSession, conflict: ConflictEvent):
        """Handle detected conflict"""
        try:
            # Add to conflict history
            session.conflict_history.append(conflict)
            
            # Determine resolution strategy based on conflict type and severity
            strategy = self._select_resolution_strategy(conflict)
            
            # Apply resolution strategy
            resolver = self.resolution_strategies.get(strategy)
            if resolver:
                resolution_result = await resolver(session, conflict)
                
                # Update conflict with resolution
                conflict.resolved_at = datetime.utcnow()
                conflict.resolution_strategy = strategy
                conflict.resolution_data = resolution_result
                
                # Notify participants
                await self._notify_conflict_resolution(session.session_id, conflict)
            
            logger.info(f"Conflict {conflict.conflict_id} resolved using {strategy.value}")
            
        except Exception as e:
            logger.error(f"Error handling conflict: {e}")
    
    def _select_resolution_strategy(self, conflict: ConflictEvent) -> ResolutionStrategy:
        """Select appropriate resolution strategy"""
        if conflict.conflict_type == ConflictType.OPERATIONAL_TRANSFORM:
            return ResolutionStrategy.OPERATIONAL_TRANSFORM
        elif conflict.conflict_type == ConflictType.SIMULTANEOUS_EDIT:
            if conflict.severity in [ConflictSeverity.LOW, ConflictSeverity.MEDIUM]:
                return ResolutionStrategy.AUTOMATIC_MERGE
            else:
                return ResolutionStrategy.MANUAL_RESOLUTION
        elif conflict.conflict_type == ConflictType.RESOURCE_LOCK:
            return ResolutionStrategy.FIRST_WRITER_WINS
        elif conflict.conflict_type == ConflictType.VERSION_DIVERGENCE:
            return ResolutionStrategy.THREE_WAY_MERGE
        else:
            return ResolutionStrategy.MANUAL_RESOLUTION
    
    async def _resolve_automatic_merge(self, session: CollaborationSession,
                                     conflict: ConflictEvent) -> Dict[str, Any]:
        """Automatic merge resolution"""
        try:
            operations = conflict.conflicting_operations
            if len(operations) != 2:
                return {"status": "error", "message": "Automatic merge requires exactly 2 operations"}
            
            op1, op2 = operations[0], operations[1]
            
            # Simple merge strategy: apply both operations in timestamp order
            if op1.timestamp <= op2.timestamp:
                first_op, second_op = op1, op2
            else:
                first_op, second_op = op2, op1
            
            # Apply operations in order
            await self._apply_operation(session, first_op)
            
            # Transform second operation if needed
            if self._needs_transformation(first_op, second_op):
                transformed_op = self.operational_transformer.transform(second_op, first_op)
                await self._apply_operation(session, transformed_op)
            else:
                await self._apply_operation(session, second_op)
            
            return {
                "status": "success",
                "strategy": "automatic_merge",
                "applied_operations": [first_op.operation_id, second_op.operation_id]
            }
            
        except Exception as e:
            logger.error(f"Error in automatic merge resolution: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _resolve_last_writer_wins(self, session: CollaborationSession,
                                      conflict: ConflictEvent) -> Dict[str, Any]:
        """Last writer wins resolution"""
        operations = conflict.conflicting_operations
        latest_op = max(operations, key=lambda op: op.timestamp)
        
        await self._apply_operation(session, latest_op)
        
        return {
            "status": "success",
            "strategy": "last_writer_wins",
            "winning_operation": latest_op.operation_id,
            "winning_user": latest_op.user_id
        }
    
    async def _resolve_first_writer_wins(self, session: CollaborationSession,
                                       conflict: ConflictEvent) -> Dict[str, Any]:
        """First writer wins resolution"""
        operations = conflict.conflicting_operations
        earliest_op = min(operations, key=lambda op: op.timestamp)
        
        await self._apply_operation(session, earliest_op)
        
        return {
            "status": "success",
            "strategy": "first_writer_wins",
            "winning_operation": earliest_op.operation_id,
            "winning_user": earliest_op.user_id
        }
    
    async def _resolve_manual(self, session: CollaborationSession,
                            conflict: ConflictEvent) -> Dict[str, Any]:
        """Manual resolution - notify users"""
        # Notify all conflicting users for manual resolution
        for user_id in conflict.conflicting_users:
            await self._send_to_user(user_id, {
                "type": "manual_resolution_required",
                "conflict": {
                    "conflict_id": conflict.conflict_id,
                    "conflict_type": conflict.conflict_type.value,
                    "severity": conflict.severity.value,
                    "resource_id": conflict.resource_id,
                    "operations": [
                        {
                            "operation_id": op.operation_id,
                            "user_id": op.user_id,
                            "type": op.operation_type.value,
                            "content": op.content
                        }
                        for op in conflict.conflicting_operations
                    ]
                }
            })
        
        return {
            "status": "pending",
            "strategy": "manual_resolution",
            "message": "Manual resolution required"
        }
    
    async def _resolve_ai_assisted(self, session: CollaborationSession,
                                 conflict: ConflictEvent) -> Dict[str, Any]:
        """AI-assisted resolution"""
        # Simplified AI resolution - in production would use ML models
        operations = conflict.conflicting_operations
        
        # Analyze operations and suggest resolution
        if len(operations) == 2:
            op1, op2 = operations[0], operations[1]
            
            # Simple heuristic: prefer larger changes
            if len(str(op1.content)) >= len(str(op2.content)):
                preferred_op = op1
            else:
                preferred_op = op2
            
            await self._apply_operation(session, preferred_op)
            
            return {
                "status": "success",
                "strategy": "ai_assisted",
                "preferred_operation": preferred_op.operation_id,
                "confidence": 0.7
            }
        
        return {"status": "error", "message": "AI resolution not applicable"}
    
    async def _resolve_operational_transform(self, session: CollaborationSession,
                                           conflict: ConflictEvent) -> Dict[str, Any]:
        """Operational transformation resolution"""
        operations = conflict.conflicting_operations
        if len(operations) != 2:
            return {"status": "error", "message": "OT requires exactly 2 operations"}
        
        op1, op2 = operations[0], operations[1]
        
        # Apply operational transformation
        transformed_op1, transformed_op2 = self.operational_transformer.transform_pair(op1, op2)
        
        # Apply transformed operations
        await self._apply_operation(session, transformed_op1)
        await self._apply_operation(session, transformed_op2)
        
        return {
            "status": "success",
            "strategy": "operational_transform",
            "transformed_operations": [transformed_op1.operation_id, transformed_op2.operation_id]
        }
    
    async def _resolve_three_way_merge(self, session: CollaborationSession,
                                     conflict: ConflictEvent) -> Dict[str, Any]:
        """Three-way merge resolution"""
        # Simplified three-way merge
        operations = conflict.conflicting_operations
        
        # Find common ancestor and merge
        merged_content = self._perform_three_way_merge(operations)
        
        # Create merged operation
        merged_op = Operation(
            operation_id=f"merged_{uuid.uuid4().hex[:8]}",
            user_id="system",
            operation_type=OperationType.REPLACE,
            target_resource=conflict.resource_id,
            position=0,
            length=0,
            content=merged_content,
            timestamp=datetime.utcnow(),
            vector_clock={},
            metadata={"merge_source": [op.operation_id for op in operations]}
        )
        
        await self._apply_operation(session, merged_op)
        
        return {
            "status": "success",
            "strategy": "three_way_merge",
            "merged_operation": merged_op.operation_id
        }
    
    def _perform_three_way_merge(self, operations: List[Operation]) -> Any:
        """Perform three-way merge algorithm"""
        # Simplified merge - in production would use proper merge algorithms
        if not operations:
            return ""
        
        # For text content, use difflib
        contents = [str(op.content) for op in operations]
        
        if len(contents) == 2:
            # Simple two-way merge
            return contents[0] + "\n" + contents[1]
        else:
            # Multi-way merge
            return "\n".join(contents)
    
    async def _apply_operation(self, session: CollaborationSession, operation: Operation):
        """Apply operation to resource"""
        resource_id = operation.target_resource
        
        # Ensure resource exists
        if resource_id not in session.resources:
            session.resources[resource_id] = ResourceState(
                resource_id=resource_id,
                content="",
                version=0,
                last_modified=datetime.utcnow(),
                last_modified_by=operation.user_id,
                vector_clock=VectorClock()
            )
        
        resource = session.resources[resource_id]
        
        # Apply operation based on type
        if operation.operation_type == OperationType.INSERT:
            if isinstance(resource.content, str):
                content = str(resource.content)
                resource.content = (content[:operation.position] + 
                                  str(operation.content) + 
                                  content[operation.position:])
        
        elif operation.operation_type == OperationType.DELETE:
            if isinstance(resource.content, str):
                content = str(resource.content)
                end_pos = operation.position + operation.length
                resource.content = content[:operation.position] + content[end_pos:]
        
        elif operation.operation_type == OperationType.REPLACE:
            resource.content = operation.content
        
        # Update resource metadata
        resource.version += 1
        resource.last_modified = operation.timestamp
        resource.last_modified_by = operation.user_id
        resource.vector_clock.update(VectorClock(operation.vector_clock))
    
    async def _broadcast_operation(self, session_id: str, operation: Operation,
                                 exclude_user: Optional[str] = None):
        """Broadcast operation to session participants"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        message = {
            "type": "operation_applied",
            "operation": {
                "operation_id": operation.operation_id,
                "user_id": operation.user_id,
                "operation_type": operation.operation_type.value,
                "target_resource": operation.target_resource,
                "position": operation.position,
                "length": operation.length,
                "content": operation.content,
                "timestamp": operation.timestamp.isoformat(),
                "vector_clock": operation.vector_clock
            }
        }
        
        for user_id in session.participants:
            if user_id != exclude_user:
                await self._send_to_user(user_id, message)
    
    async def _notify_conflict_resolution(self, session_id: str, conflict: ConflictEvent):
        """Notify participants about conflict resolution"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        message = {
            "type": "conflict_resolved",
            "conflict": {
                "conflict_id": conflict.conflict_id,
                "conflict_type": conflict.conflict_type.value,
                "resource_id": conflict.resource_id,
                "resolution_strategy": conflict.resolution_strategy.value if conflict.resolution_strategy else None,
                "resolved_at": conflict.resolved_at.isoformat() if conflict.resolved_at else None,
                "resolution_data": conflict.resolution_data
            }
        }
        
        for user_id in session.participants:
            await self._send_to_user(user_id, message)
    
    async def _handle_request_lock(self, user_id: str, message: Dict[str, Any]):
        """Handle resource lock request"""
        try:
            session_id = message.get("session_id")
            resource_id = message.get("resource_id")
            lock_type = message.get("lock_type", "exclusive")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Ensure resource exists
            if resource_id not in session.resources:
                session.resources[resource_id] = ResourceState(
                    resource_id=resource_id,
                    content="",
                    version=0,
                    last_modified=datetime.utcnow(),
                    last_modified_by=user_id,
                    vector_clock=VectorClock()
                )
            
            resource = session.resources[resource_id]
            
            # Check if resource is already locked
            if resource.active_locks and lock_type == "exclusive":
                await self._send_error(user_id, "Resource is already locked")
                return
            
            # Grant lock
            resource.active_locks[user_id] = lock_type
            
            await self._send_to_user(user_id, {
                "type": "lock_granted",
                "resource_id": resource_id,
                "lock_type": lock_type
            })
            
            # Notify other participants
            await self._broadcast_to_session(session_id, {
                "type": "resource_locked",
                "resource_id": resource_id,
                "locked_by": user_id,
                "lock_type": lock_type
            }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling lock request: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_release_lock(self, user_id: str, message: Dict[str, Any]):
        """Handle resource lock release"""
        try:
            session_id = message.get("session_id")
            resource_id = message.get("resource_id")
            
            session = self.sessions.get(session_id)
            if not session or resource_id not in session.resources:
                return
            
            resource = session.resources[resource_id]
            
            # Release lock
            if user_id in resource.active_locks:
                del resource.active_locks[user_id]
                
                await self._send_to_user(user_id, {
                    "type": "lock_released",
                    "resource_id": resource_id
                })
                
                # Notify other participants
                await self._broadcast_to_session(session_id, {
                    "type": "resource_unlocked",
                    "resource_id": resource_id,
                    "unlocked_by": user_id
                }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling lock release: {e}")
    
    async def _handle_resolve_conflict(self, user_id: str, message: Dict[str, Any]):
        """Handle manual conflict resolution"""
        try:
            session_id = message.get("session_id")
            conflict_id = message.get("conflict_id")
            resolution_choice = message.get("resolution_choice")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Find conflict
            conflict = None
            for c in session.conflict_history:
                if c.conflict_id == conflict_id:
                    conflict = c
                    break
            
            if not conflict:
                await self._send_error(user_id, "Conflict not found")
                return
            
            if conflict.resolved_at:
                await self._send_error(user_id, "Conflict already resolved")
                return
            
            # Apply user's resolution choice
            if resolution_choice == "accept_all":
                for op in conflict.conflicting_operations:
                    await self._apply_operation(session, op)
            elif resolution_choice == "accept_mine":
                user_ops = [op for op in conflict.conflicting_operations if op.user_id == user_id]
                for op in user_ops:
                    await self._apply_operation(session, op)
            elif resolution_choice == "accept_theirs":
                other_ops = [op for op in conflict.conflicting_operations if op.user_id != user_id]
                for op in other_ops:
                    await self._apply_operation(session, op)
            
            # Mark conflict as resolved
            conflict.resolved_at = datetime.utcnow()
            conflict.resolved_by = user_id
            conflict.resolution_strategy = ResolutionStrategy.MANUAL_RESOLUTION
            conflict.resolution_data = {"choice": resolution_choice}
            
            # Notify participants
            await self._notify_conflict_resolution(session_id, conflict)
            
        except Exception as e:
            logger.error(f"Error handling conflict resolution: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_request_sync(self, user_id: str, message: Dict[str, Any]):
        """Handle synchronization request"""
        try:
            session_id = message.get("session_id")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Send full session state
            await self._send_to_user(user_id, {
                "type": "full_sync",
                "session": await self._serialize_session(session),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling sync request: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_undo_operation(self, user_id: str, message: Dict[str, Any]):
        """Handle operation undo"""
        try:
            session_id = message.get("session_id")
            operation_id = message.get("operation_id")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Find operation to undo
            operation = None
            for op in reversed(session.operation_log):
                if op.operation_id == operation_id and op.user_id == user_id:
                    operation = op
                    break
            
            if not operation:
                await self._send_error(user_id, "Operation not found or not yours")
                return
            
            # Create inverse operation
            inverse_op = self._create_inverse_operation(operation)
            
            # Apply inverse operation
            await self._apply_operation(session, inverse_op)
            session.operation_log.append(inverse_op)
            
            # Broadcast undo
            await self._broadcast_operation(session_id, inverse_op, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling undo: {e}")
            await self._send_error(user_id, str(e))
    
    def _create_inverse_operation(self, operation: Operation) -> Operation:
        """Create inverse operation for undo"""
        if operation.operation_type == OperationType.INSERT:
            return Operation(
                operation_id=f"undo_{operation.operation_id}",
                user_id=operation.user_id,
                operation_type=OperationType.DELETE,
                target_resource=operation.target_resource,
                position=operation.position,
                length=len(str(operation.content)),
                content="",
                timestamp=datetime.utcnow(),
                vector_clock={},
                metadata={"undo_of": operation.operation_id}
            )
        elif operation.operation_type == OperationType.DELETE:
            return Operation(
                operation_id=f"undo_{operation.operation_id}",
                user_id=operation.user_id,
                operation_type=OperationType.INSERT,
                target_resource=operation.target_resource,
                position=operation.position,
                length=0,
                content=operation.content,
                timestamp=datetime.utcnow(),
                vector_clock={},
                metadata={"undo_of": operation.operation_id}
            )
        else:
            # For other operations, create a replace operation
            return Operation(
                operation_id=f"undo_{operation.operation_id}",
                user_id=operation.user_id,
                operation_type=OperationType.REPLACE,
                target_resource=operation.target_resource,
                position=0,
                length=0,
                content="",  # Would need to store previous content
                timestamp=datetime.utcnow(),
                vector_clock={},
                metadata={"undo_of": operation.operation_id}
            )
    
    async def _handle_redo_operation(self, user_id: str, message: Dict[str, Any]):
        """Handle operation redo"""
        # Implementation would track undone operations and reapply them
        pass
    
    async def _handle_get_conflict_history(self, user_id: str, message: Dict[str, Any]):
        """Handle conflict history request"""
        try:
            session_id = message.get("session_id")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Send conflict history
            conflicts = [
                {
                    "conflict_id": c.conflict_id,
                    "conflict_type": c.conflict_type.value,
                    "severity": c.severity.value,
                    "resource_id": c.resource_id,
                    "conflicting_users": c.conflicting_users,
                    "detected_at": c.detected_at.isoformat(),
                    "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
                    "resolution_strategy": c.resolution_strategy.value if c.resolution_strategy else None,
                    "resolved_by": c.resolved_by
                }
                for c in session.conflict_history
            ]
            
            await self._send_to_user(user_id, {
                "type": "conflict_history",
                "conflicts": conflicts,
                "total_count": len(conflicts)
            })
            
        except Exception as e:
            logger.error(f"Error getting conflict history: {e}")
            await self._send_error(user_id, str(e))
    
    async def _serialize_session(self, session: CollaborationSession) -> Dict[str, Any]:
        """Serialize session for transmission"""
        return {
            "session_id": session.session_id,
            "project_id": session.project_id,
            "participants": list(session.participants),
            "resources": {
                resource_id: {
                    "resource_id": resource.resource_id,
                    "content": resource.content,
                    "version": resource.version,
                    "last_modified": resource.last_modified.isoformat(),
                    "last_modified_by": resource.last_modified_by,
                    "active_locks": resource.active_locks
                }
                for resource_id, resource in session.resources.items()
            },
            "vector_clocks": {
                user_id: clock.clocks for user_id, clock in session.vector_clocks.items()
            },
            "conflict_count": len(session.conflict_history),
            "operation_count": len(session.operation_log),
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
    
    async def _broadcast_to_session(self, session_id: str, message: Dict[str, Any],
                                   exclude_user: Optional[str] = None):
        """Broadcast message to session participants"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        for user_id in session.participants:
            if user_id != exclude_user:
                await self._send_to_user(user_id, message)
    
    async def _send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        websocket = self.websocket_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
                await self._cleanup_user_connection(user_id)
    
    async def _send_error(self, user_id: str, error_message: str):
        """Send error message to user"""
        await self._send_to_user(user_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _cleanup_user_connection(self, user_id: str):
        """Cleanup user connection"""
        try:
            # Remove WebSocket connection
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
            
            # Release all locks held by user
            for session in self.sessions.values():
                if user_id in session.participants:
                    for resource in session.resources.values():
                        if user_id in resource.active_locks:
                            del resource.active_locks[user_id]
            
        except Exception as e:
            logger.error(f"Error cleaning up user connection: {e}")


class OperationalTransformer:
    """Operational transformation algorithms"""
    
    def transform(self, operation: Operation, against_operation: Operation) -> Operation:
        """Transform operation against another operation"""
        if operation.operation_type == OperationType.INSERT and against_operation.operation_type == OperationType.INSERT:
            return self._transform_insert_insert(operation, against_operation)
        elif operation.operation_type == OperationType.INSERT and against_operation.operation_type == OperationType.DELETE:
            return self._transform_insert_delete(operation, against_operation)
        elif operation.operation_type == OperationType.DELETE and against_operation.operation_type == OperationType.INSERT:
            return self._transform_delete_insert(operation, against_operation)
        elif operation.operation_type == OperationType.DELETE and against_operation.operation_type == OperationType.DELETE:
            return self._transform_delete_delete(operation, against_operation)
        else:
            return operation  # No transformation needed
    
    def transform_pair(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """Transform a pair of operations"""
        transformed_op1 = self.transform(op1, op2)
        transformed_op2 = self.transform(op2, op1)
        return transformed_op1, transformed_op2
    
    def _transform_insert_insert(self, op1: Operation, op2: Operation) -> Operation:
        """Transform insert against insert"""
        if op1.position <= op2.position:
            return op1  # No change needed
        else:
            # Adjust position
            new_op = Operation(
                operation_id=op1.operation_id,
                user_id=op1.user_id,
                operation_type=op1.operation_type,
                target_resource=op1.target_resource,
                position=op1.position + len(str(op2.content)),
                length=op1.length,
                content=op1.content,
                timestamp=op1.timestamp,
                vector_clock=op1.vector_clock,
                metadata=op1.metadata
            )
            return new_op
    
    def _transform_insert_delete(self, op1: Operation, op2: Operation) -> Operation:
        """Transform insert against delete"""
        if op1.position <= op2.position:
            return op1  # No change needed
        elif op1.position >= op2.position + op2.length:
            # Adjust position
            new_op = Operation(
                operation_id=op1.operation_id,
                user_id=op1.user_id,
                operation_type=op1.operation_type,
                target_resource=op1.target_resource,
                position=op1.position - op2.length,
                length=op1.length,
                content=op1.content,
                timestamp=op1.timestamp,
                vector_clock=op1.vector_clock,
                metadata=op1.metadata
            )
            return new_op
        else:
            # Insert position is within deleted range - adjust to deletion start
            new_op = Operation(
                operation_id=op1.operation_id,
                user_id=op1.user_id,
                operation_type=op1.operation_type,
                target_resource=op1.target_resource,
                position=op2.position,
                length=op1.length,
                content=op1.content,
                timestamp=op1.timestamp,
                vector_clock=op1.vector_clock,
                metadata=op1.metadata
            )
            return new_op
    
    def _transform_delete_insert(self, op1: Operation, op2: Operation) -> Operation:
        """Transform delete against insert"""
        if op2.position <= op1.position:
            # Adjust position
            new_op = Operation(
                operation_id=op1.operation_id,
                user_id=op1.user_id,
                operation_type=op1.operation_type,
                target_resource=op1.target_resource,
                position=op1.position + len(str(op2.content)),
                length=op1.length,
                content=op1.content,
                timestamp=op1.timestamp,
                vector_clock=op1.vector_clock,
                metadata=op1.metadata
            )
            return new_op
        else:
            return op1  # No change needed
    
    def _transform_delete_delete(self, op1: Operation, op2: Operation) -> Operation:
        """Transform delete against delete"""
        if op1.position >= op2.position + op2.length:
            # Adjust position
            new_op = Operation(
                operation_id=op1.operation_id,
                user_id=op1.user_id,
                operation_type=op1.operation_type,
                target_resource=op1.target_resource,
                position=op1.position - op2.length,
                length=op1.length,
                content=op1.content,
                timestamp=op1.timestamp,
                vector_clock=op1.vector_clock,
                metadata=op1.metadata
            )
            return new_op
        elif op2.position >= op1.position + op1.length:
            return op1  # No overlap
        else:
            # Overlapping deletes - need complex resolution
            # Simplified: adjust length
            overlap_start = max(op1.position, op2.position)
            overlap_end = min(op1.position + op1.length, op2.position + op2.length)
            overlap_length = max(0, overlap_end - overlap_start)
            
            new_op = Operation(
                operation_id=op1.operation_id,
                user_id=op1.user_id,
                operation_type=op1.operation_type,
                target_resource=op1.target_resource,
                position=min(op1.position, op2.position),
                length=op1.length - overlap_length,
                content=op1.content,
                timestamp=op1.timestamp,
                vector_clock=op1.vector_clock,
                metadata=op1.metadata
            )
            return new_op


# Export the resolver
__all__ = ['CollaborationConflictResolver', 'ConflictType', 'ConflictSeverity',
           'ResolutionStrategy', 'OperationType', 'Operation', 'ConflictEvent',
           'VectorClock', 'ResourceState', 'CollaborationSession', 'OperationalTransformer']