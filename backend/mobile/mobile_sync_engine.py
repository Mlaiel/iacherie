"""Offline Synchronization Manager
=================================

Professional offline data synchronization for mobile applications
with conflict resolution, incremental sync, and robust error handling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import json
import hashlib
import uuid
import time
import sqlite3
import aiosqlite

logger = logging.getLogger(__name__)


class SyncStrategy(str, Enum):
    """Data synchronization strategies."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE_FIELDS = "merge_fields"
    USER_RESOLUTION = "user_resolution"
    TIMESTAMP_BASED = "timestamp_based"


class ConflictResolution(str, Enum):
    """Conflict resolution options."""
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    MANUAL = "manual"
    MERGE = "merge"
    KEEP_BOTH = "keep_both"


class SyncDirection(str, Enum):
    """Sync direction options."""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    BIDIRECTIONAL = "bidirectional"


class OperationType(str, Enum):
    """Data operation types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    PATCH = "patch"


class SyncStatus(str, Enum):
    """Synchronization status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"
    CANCELLED = "cancelled"


@dataclass
class OfflineOperation:
    """Offline operation record."""
    operation_id: str
    entity_type: str
    entity_id: str
    operation_type: OperationType
    data: Dict[str, Any]
    local_timestamp: datetime
    retry_count: int
    max_retries: int
    status: SyncStatus
    conflict_data: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class SyncConflict:
    """Data synchronization conflict."""
    conflict_id: str
    entity_type: str
    entity_id: str
    local_data: Dict[str, Any]
    remote_data: Dict[str, Any]
    local_timestamp: datetime
    remote_timestamp: datetime
    conflict_fields: List[str]
    resolution: Optional[ConflictResolution]
    resolved_data: Optional[Dict[str, Any]]
    created_at: datetime
    resolved_at: Optional[datetime]


@dataclass
class SyncSession:
    """Synchronization session."""
    session_id: str
    user_id: str
    device_id: str
    direction: SyncDirection
    entity_types: List[str]
    started_at: datetime
    completed_at: Optional[datetime]
    operations_total: int
    operations_completed: int
    operations_failed: int
    conflicts_detected: int
    conflicts_resolved: int
    status: SyncStatus
    metadata: Dict[str, Any]


@dataclass
class SyncConfiguration:
    """Sync configuration settings."""
    sync_interval_seconds: int = 300  # 5 minutes
    batch_size: int = 100
    max_retries: int = 3
    conflict_resolution: ConflictResolution = ConflictResolution.REMOTE_WINS
    sync_strategy: SyncStrategy = SyncStrategy.LAST_WRITE_WINS
    auto_resolve_conflicts: bool = True
    compress_data: bool = True
    encrypt_data: bool = True
    offline_retention_days: int = 30
    sync_on_connection: bool = True
    priority_entities: List[str] = None
    excluded_fields: List[str] = None


class OfflineSyncManager:
    """Professional offline synchronization manager."""
    
    def __init__(
        self,
        db_path -> None: str = " -> None:memory -> None:",
        config -> None: Optional[SyncConfiguration] = None,
        api_client -> None: Optional[Any] = None
    ) -> None:
        self.db_path = db_path
        self.config = config or SyncConfiguration()
        self.api_client = api_client
        
        # Database connection
        self.db_connection: Optional[aiosqlite.Connection] = None
        
        # Operation tracking
        self.pending_operations: Dict[str, OfflineOperation] = {}
        self.sync_conflicts: Dict[str, SyncConflict] = {}
        self.active_sessions: Dict[str, SyncSession] = {}
        
        # Statistics
        self.total_operations = 0
        self.successful_syncs = 0
        self.failed_syncs = 0
        self.conflicts_resolved = 0
        
        # Event handlers
        self.conflict_handlers: Dict[str, Callable] = {}
        self.sync_progress_handlers: List[Callable] = []
        
        logger.info("Offline sync manager initialized")
    
    async def initialize(self) -> None:
        """Initialize the sync manager."""
        await self._setup_database()
        await self._load_pending_operations()
        await self._load_conflicts()
        logger.info("Offline sync manager ready")
    
    async def close(self) -> None:
        """Close the sync manager."""
        if self.db_connection:
            await self.db_connection.close()
    
    async def _setup_database(self) -> None:
        """Setup SQLite database for offline storage."""
        self.db_connection = await aiosqlite.connect(self.db_path)
        
        # Create tables
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS offline_operations (
                operation_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                data TEXT NOT NULL,
                local_timestamp TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                status TEXT DEFAULT 'pending',
                conflict_data TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS sync_conflicts (
                conflict_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                local_data TEXT NOT NULL,
                remote_data TEXT NOT NULL,
                local_timestamp TEXT NOT NULL,
                remote_timestamp TEXT NOT NULL,
                conflict_fields TEXT NOT NULL,
                resolution TEXT,
                resolved_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                resolved_at TEXT
            )
        """)
        
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS sync_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                direction TEXT NOT NULL,
                entity_types TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                operations_total INTEGER DEFAULT 0,
                operations_completed INTEGER DEFAULT 0,
                operations_failed INTEGER DEFAULT 0,
                conflicts_detected INTEGER DEFAULT 0,
                conflicts_resolved INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                metadata TEXT
            )
        """)
        
        await self.db_connection.commit()
    
    async def _load_pending_operations(self) -> None:
        """Load pending operations from database."""
        cursor = await self.db_connection.execute(
            "SELECT * FROM offline_operations WHERE status IN ('pending', 'failed')"
        )
        rows = await cursor.fetchall()
        
        for row in rows:
            operation = OfflineOperation(
                operation_id=row[0],
                entity_type=row[1],
                entity_id=row[2],
                operation_type=OperationType(row[3]),
                data=json.loads(row[4]),
                local_timestamp=datetime.fromisoformat(row[5]),
                retry_count=row[6],
                max_retries=row[7],
                status=SyncStatus(row[8]),
                conflict_data=json.loads(row[9]) if row[9] else None,
                metadata=json.loads(row[10]) if row[10] else {}
            )
            self.pending_operations[operation.operation_id] = operation
        
        logger.info(f"Loaded {len(self.pending_operations)} pending operations")
    
    async def _load_conflicts(self) -> None:
        """Load unresolved conflicts from database."""
        cursor = await self.db_connection.execute(
            "SELECT * FROM sync_conflicts WHERE resolution IS NULL"
        )
        rows = await cursor.fetchall()
        
        for row in rows:
            conflict = SyncConflict(
                conflict_id=row[0],
                entity_type=row[1],
                entity_id=row[2],
                local_data=json.loads(row[3]),
                remote_data=json.loads(row[4]),
                local_timestamp=datetime.fromisoformat(row[5]),
                remote_timestamp=datetime.fromisoformat(row[6]),
                conflict_fields=json.loads(row[7]),
                resolution=ConflictResolution(row[8]) if row[8] else None,
                resolved_data=json.loads(row[9]) if row[9] else None,
                created_at=datetime.fromisoformat(row[10]),
                resolved_at=datetime.fromisoformat(row[11]) if row[11] else None
            )
            self.sync_conflicts[conflict.conflict_id] = conflict
        
        logger.info(f"Loaded {len(self.sync_conflicts)} unresolved conflicts")
    
    async def queue_operation(
        self,
        entity_type: str,
        entity_id: str,
        operation_type: OperationType,
        data: Dict[str, Any],
        priority: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Queue an offline operation."""
        operation_id = str(uuid.uuid4())
        
        operation = OfflineOperation(
            operation_id=operation_id,
            entity_type=entity_type,
            entity_id=entity_id,
            operation_type=operation_type,
            data=data,
            local_timestamp=datetime.now(),
            retry_count=0,
            max_retries=self.config.max_retries,
            status=SyncStatus.PENDING,
            conflict_data=None,
            metadata=metadata or {}
        )
        
        # Store in database
        await self.db_connection.execute("""
            INSERT INTO offline_operations 
            (operation_id, entity_type, entity_id, operation_type, data, 
             local_timestamp, max_retries, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            operation.operation_id,
            operation.entity_type,
            operation.entity_id,
            operation.operation_type.value,
            json.dumps(operation.data),
            operation.local_timestamp.isoformat(),
            operation.max_retries,
            json.dumps(operation.metadata)
        ))
        await self.db_connection.commit()
        
        # Add to pending operations
        self.pending_operations[operation_id] = operation
        self.total_operations += 1
        
        logger.info(f"Operation queued: {operation_type.value} {entity_type}:{entity_id}")
        return operation_id
    
    async def start_sync_session(
        self,
        user_id: str,
        device_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        entity_types: Optional[List[str]] = None
    ) -> str:
        """Start a synchronization session."""
        session_id = str(uuid.uuid4())
        
        session = SyncSession(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            direction=direction,
            entity_types=entity_types or [],
            started_at=datetime.now(),
            completed_at=None,
            operations_total=0,
            operations_completed=0,
            operations_failed=0,
            conflicts_detected=0,
            conflicts_resolved=0,
            status=SyncStatus.IN_PROGRESS,
            metadata={}
        )
        
        # Store in database
        await self.db_connection.execute("""
            INSERT INTO sync_sessions 
            (session_id, user_id, device_id, direction, entity_types, started_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.user_id,
            session.device_id,
            session.direction.value,
            json.dumps(session.entity_types),
            session.started_at.isoformat(),
            session.status.value
        ))
        await self.db_connection.commit()
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Sync session started: {session_id}")
        return session_id
    
    async def sync_pending_operations(
        self,
        session_id: str,
        batch_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Synchronize pending operations."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        batch_size = batch_size or self.config.batch_size
        
        # Get pending operations for this session
        operations_to_sync = []
        for operation in self.pending_operations.values():
            if (not session.entity_types or 
                operation.entity_type in session.entity_types):
                operations_to_sync.append(operation)
                
                if len(operations_to_sync) >= batch_size:
                    break
        
        session.operations_total = len(operations_to_sync)
        
        sync_results = []
        
        for operation in operations_to_sync:
            try:
                result = await self._sync_operation(operation)
                sync_results.append(result)
                
                if result["success"]:
                    session.operations_completed += 1
                    await self._remove_operation(operation.operation_id)
                else:
                    session.operations_failed += 1
                    await self._update_operation_status(
                        operation.operation_id, 
                        SyncStatus.FAILED
                    )
                
                # Notify progress
                await self._notify_sync_progress(session, operation, result)
                
            except Exception as e:
                logger.error(f"Operation sync failed: {operation.operation_id} - {e}")
                session.operations_failed += 1
                sync_results.append({
                    "operation_id": operation.operation_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Update session
        await self._update_session(session)
        
        return {
            "session_id": session_id,
            "operations_processed": len(sync_results),
            "operations_completed": session.operations_completed,
            "operations_failed": session.operations_failed,
            "conflicts_detected": session.conflicts_detected,
            "results": sync_results
        }
    
    async def _sync_operation(self, operation: OfflineOperation) -> Dict[str, Any]:
        """Sync a single operation."""
        if not self.api_client:
            return {
                "operation_id": operation.operation_id,
                "success": False,
                "error": "No API client configured"
            }
        
        try:
            # Attempt to sync operation
            if operation.operation_type == OperationType.CREATE:
                result = await self._sync_create_operation(operation)
            elif operation.operation_type == OperationType.UPDATE:
                result = await self._sync_update_operation(operation)
            elif operation.operation_type == OperationType.DELETE:
                result = await self._sync_delete_operation(operation)
            elif operation.operation_type == OperationType.PATCH:
                result = await self._sync_patch_operation(operation)
            else:
                return {
                    "operation_id": operation.operation_id,
                    "success": False,
                    "error": f"Unknown operation type: {operation.operation_type}"
                }
            
            return result
            
        except Exception as e:
            # Handle retry logic
            operation.retry_count += 1
            
            if operation.retry_count >= operation.max_retries:
                operation.status = SyncStatus.FAILED
            else:
                operation.status = SyncStatus.PENDING
            
            await self._update_operation(operation)
            
            return {
                "operation_id": operation.operation_id,
                "success": False,
                "error": str(e),
                "retry_count": operation.retry_count
            }
    
    async def _sync_create_operation(self, operation: OfflineOperation) -> Dict[str, Any]:
        """Sync create operation."""
        # Simulate API call
        await asyncio.sleep(0.1)  # Network delay simulation
        
        # Check for conflicts (entity already exists remotely)
        if await self._check_remote_exists(operation.entity_type, operation.entity_id):
            # Create conflict
            conflict_id = await self._create_conflict(
                operation, 
                {"message": "Entity already exists remotely"}
            )
            return {
                "operation_id": operation.operation_id,
                "success": False,
                "conflict_id": conflict_id,
                "error": "Conflict detected"
            }
        
        # Successful creation
        return {
            "operation_id": operation.operation_id,
            "success": True,
            "action": "created",
            "entity_id": operation.entity_id
        }
    
    async def _sync_update_operation(self, operation: OfflineOperation) -> Dict[str, Any]:
        """Sync update operation."""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        # Get remote version for conflict detection
        remote_data = await self._get_remote_data(operation.entity_type, operation.entity_id)
        
        if remote_data:
            # Check for conflicts
            conflicts = await self._detect_conflicts(operation.data, remote_data)
            
            if conflicts:
                conflict_id = await self._create_conflict(operation, remote_data)
                return {
                    "operation_id": operation.operation_id,
                    "success": False,
                    "conflict_id": conflict_id,
                    "error": "Data conflicts detected"
                }
        
        # Successful update
        return {
            "operation_id": operation.operation_id,
            "success": True,
            "action": "updated",
            "entity_id": operation.entity_id
        }
    
    async def _sync_delete_operation(self, operation: OfflineOperation) -> Dict[str, Any]:
        """Sync delete operation."""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        # Check if entity still exists remotely
        if not await self._check_remote_exists(operation.entity_type, operation.entity_id):
            # Already deleted, consider success
            return {
                "operation_id": operation.operation_id,
                "success": True,
                "action": "already_deleted",
                "entity_id": operation.entity_id
            }
        
        # Successful deletion
        return {
            "operation_id": operation.operation_id,
            "success": True,
            "action": "deleted",
            "entity_id": operation.entity_id
        }
    
    async def _sync_patch_operation(self, operation: OfflineOperation) -> Dict[str, Any]:
        """Sync patch operation."""
        # Similar to update but only patches specific fields
        return await self._sync_update_operation(operation)
    
    async def _check_remote_exists(self, entity_type: str, entity_id: str) -> bool:
        """Check if entity exists remotely."""
        # Simulate API call
        await asyncio.sleep(0.05)
        # For demo purposes, randomly return True/False
        import random
        return random.choice([True, False])
    
    async def _get_remote_data(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get remote data for entity."""
        # Simulate API call
        await asyncio.sleep(0.05)
        # Return mock remote data
        return {
            "id": entity_id,
            "updated_at": datetime.now().isoformat(),
            "version": 2
        }
    
    async def _detect_conflicts(self, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> List[str]:
        """Detect conflicts between local and remote data."""
        conflicts = []
        
        for key, local_value in local_data.items():
            if key in remote_data and remote_data[key] != local_value:
                # Check if this is a timestamp-based conflict
                if key in ["updated_at", "modified_at"]:
                    try:
                        local_time = datetime.fromisoformat(str(local_value))
                        remote_time = datetime.fromisoformat(str(remote_data[key]))
                        
                        # Consider conflict if times are significantly different
                        if abs((local_time - remote_time).total_seconds()) > 60:
                            conflicts.append(key)
                    except:
                        conflicts.append(key)
                else:
                    conflicts.append(key)
        
        return conflicts
    
    async def _create_conflict(
        self, 
        operation: OfflineOperation, 
        remote_data: Dict[str, Any]
    ) -> str:
        """Create a sync conflict record."""
        conflict_id = str(uuid.uuid4())
        
        conflict = SyncConflict(
            conflict_id=conflict_id,
            entity_type=operation.entity_type,
            entity_id=operation.entity_id,
            local_data=operation.data,
            remote_data=remote_data,
            local_timestamp=operation.local_timestamp,
            remote_timestamp=datetime.now(),  # Assume remote timestamp is now
            conflict_fields=await self._detect_conflicts(operation.data, remote_data),
            resolution=None,
            resolved_data=None,
            created_at=datetime.now(),
            resolved_at=None
        )
        
        # Store in database
        await self.db_connection.execute("""
            INSERT INTO sync_conflicts 
            (conflict_id, entity_type, entity_id, local_data, remote_data,
             local_timestamp, remote_timestamp, conflict_fields, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conflict.conflict_id,
            conflict.entity_type,
            conflict.entity_id,
            json.dumps(conflict.local_data),
            json.dumps(conflict.remote_data),
            conflict.local_timestamp.isoformat(),
            conflict.remote_timestamp.isoformat(),
            json.dumps(conflict.conflict_fields),
            conflict.created_at.isoformat()
        ))
        await self.db_connection.commit()
        
        self.sync_conflicts[conflict_id] = conflict
        
        # Auto-resolve if configured
        if self.config.auto_resolve_conflicts:
            await self._auto_resolve_conflict(conflict_id)
        
        logger.info(f"Conflict created: {conflict_id}")
        return conflict_id
    
    async def _auto_resolve_conflict(self, conflict_id: str) -> bool:
        """Automatically resolve conflict based on configuration."""
        if conflict_id not in self.sync_conflicts:
            return False
        
        conflict = self.sync_conflicts[conflict_id]
        
        if self.config.conflict_resolution == ConflictResolution.LOCAL_WINS:
            resolved_data = conflict.local_data
        elif self.config.conflict_resolution == ConflictResolution.REMOTE_WINS:
            resolved_data = conflict.remote_data
        elif self.config.conflict_resolution == ConflictResolution.MERGE:
            resolved_data = await self._merge_conflict_data(conflict)
        else:
            return False  # Cannot auto-resolve
        
        return await self.resolve_conflict(conflict_id, ConflictResolution.MERGE, resolved_data)
    
    async def _merge_conflict_data(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Merge conflicted data using strategy."""
        merged_data = conflict.remote_data.copy()
        
        if self.config.sync_strategy == SyncStrategy.LAST_WRITE_WINS:
            # Use data from the most recent timestamp
            if conflict.local_timestamp > conflict.remote_timestamp:
                merged_data.update(conflict.local_data)
        elif self.config.sync_strategy == SyncStrategy.MERGE_FIELDS:
            # Merge non-conflicting fields
            for key, value in conflict.local_data.items():
                if key not in conflict.conflict_fields:
                    merged_data[key] = value
        
        return merged_data
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution: ConflictResolution,
        resolved_data: Dict[str, Any]
    ) -> bool:
        """Manually resolve a conflict."""
        if conflict_id not in self.sync_conflicts:
            return False
        
        conflict = self.sync_conflicts[conflict_id]
        conflict.resolution = resolution
        conflict.resolved_data = resolved_data
        conflict.resolved_at = datetime.now()
        
        # Update database
        await self.db_connection.execute("""
            UPDATE sync_conflicts 
            SET resolution = ?, resolved_data = ?, resolved_at = ?
            WHERE conflict_id = ?
        """, (
            resolution.value,
            json.dumps(resolved_data),
            conflict.resolved_at.isoformat(),
            conflict_id
        ))
        await self.db_connection.commit()
        
        # Remove from active conflicts
        del self.sync_conflicts[conflict_id]
        self.conflicts_resolved += 1
        
        logger.info(f"Conflict resolved: {conflict_id}")
        return True
    
    async def _remove_operation(self, operation_id -> None: str) -> None:
        """Remove completed operation."""
        await self.db_connection.execute(
            "DELETE FROM offline_operations WHERE operation_id = ?",
            (operation_id,)
        )
        await self.db_connection.commit()
        
        if operation_id in self.pending_operations:
            del self.pending_operations[operation_id]
    
    async def _update_operation_status(self, operation_id -> None: str, status -> None: SyncStatus) -> None:
        """Update operation status."""
        await self.db_connection.execute(
            "UPDATE offline_operations SET status = ? WHERE operation_id = ?",
            (status.value, operation_id)
        )
        await self.db_connection.commit()
        
        if operation_id in self.pending_operations:
            self.pending_operations[operation_id].status = status
    
    async def _update_operation(self, operation -> None: OfflineOperation) -> None:
        """Update operation in database."""
        await self.db_connection.execute("""
            UPDATE offline_operations 
            SET retry_count = ?, status = ? 
            WHERE operation_id = ?
        """, (
            operation.retry_count,
            operation.status.value,
            operation.operation_id
        ))
        await self.db_connection.commit()
    
    async def _update_session(self, session -> None: SyncSession) -> None:
        """Update session in database."""
        await self.db_connection.execute("""
            UPDATE sync_sessions 
            SET operations_completed = ?, operations_failed = ?, 
                conflicts_detected = ?, conflicts_resolved = ?
            WHERE session_id = ?
        """, (
            session.operations_completed,
            session.operations_failed,
            session.conflicts_detected,
            session.conflicts_resolved,
            session.session_id
        ))
        await self.db_connection.commit()
    
    async def _notify_sync_progress(
        self, 
        session -> None: SyncSession, 
        operation -> None: OfflineOperation, 
        result -> None: Dict[str, Any]
    ) -> None:
        """Notify sync progress to handlers."""
        for handler in self.sync_progress_handlers:
            try:
                await handler(session, operation, result)
            except Exception as e:
                logger.error(f"Progress handler error: {e}")
    
    def add_conflict_handler(self, entity_type -> None: str, handler -> None: Callable) -> None:
        """Add conflict resolution handler for entity type."""
        self.conflict_handlers[entity_type] = handler
    
    def add_progress_handler(self, handler -> None: Callable) -> None:
        """Add sync progress handler."""
        self.sync_progress_handlers.append(handler)
    
    async def complete_sync_session(self, session_id: str) -> SyncSession:
        """Complete a sync session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.completed_at = datetime.now()
        session.status = SyncStatus.COMPLETED
        
        # Update database
        await self.db_connection.execute("""
            UPDATE sync_sessions 
            SET completed_at = ?, status = ?
            WHERE session_id = ?
        """, (
            session.completed_at.isoformat(),
            session.status.value,
            session_id
        ))
        await self.db_connection.commit()
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Sync session completed: {session_id}")
        return session
    
    def get_pending_operations(self, entity_type: Optional[str] = None) -> List[OfflineOperation]:
        """Get pending operations."""
        operations = list(self.pending_operations.values())
        
        if entity_type:
            operations = [op for op in operations if op.entity_type == entity_type]
        
        return operations
    
    def get_unresolved_conflicts(self, entity_type: Optional[str] = None) -> List[SyncConflict]:
        """Get unresolved conflicts."""
        conflicts = list(self.sync_conflicts.values())
        
        if entity_type:
            conflicts = [c for c in conflicts if c.entity_type == entity_type]
        
        return conflicts
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics."""
        return {
            "total_operations": self.total_operations,
            "pending_operations": len(self.pending_operations),
            "successful_syncs": self.successful_syncs,
            "failed_syncs": self.failed_syncs,
            "unresolved_conflicts": len(self.sync_conflicts),
            "conflicts_resolved": self.conflicts_resolved,
            "active_sessions": len(self.active_sessions)
        }


# Utility functions
async def create_offline_sync_manager(
    db_path: str = ":memory:",
    config: Optional[SyncConfiguration] = None
) -> OfflineSyncManager:
    """Create and initialize offline sync manager."""
    manager = OfflineSyncManager(db_path=db_path, config=config)
    await manager.initialize()
    return manager


async def quick_sync_operation(
    manager: OfflineSyncManager,
    entity_type: str,
    entity_id: str,
    operation_type: OperationType,
    data: Dict[str, Any],
    user_id: str,
    device_id: str
) -> Dict[str, Any]:
    """Quick sync operation utility."""
    # Queue operation
    operation_id = await manager.queue_operation(
        entity_type=entity_type,
        entity_id=entity_id,
        operation_type=operation_type,
        data=data
    )
    
    # Start sync session
    session_id = await manager.start_sync_session(
        user_id=user_id,
        device_id=device_id,
        entity_types=[entity_type]
    )
    
    # Sync operations
    result = await manager.sync_pending_operations(session_id, batch_size=1)
    
    # Complete session
    await manager.complete_sync_session(session_id)
    
    return {
        "operation_id": operation_id,
        "session_id": session_id,
        "sync_result": result
    }


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        config = SyncConfiguration(
            sync_interval_seconds=60,
            auto_resolve_conflicts=True,
            conflict_resolution=ConflictResolution.MERGE
        )
        
        manager = await create_offline_sync_manager(config=config)
        
        try:
            # Queue some operations
            op1 = await manager.queue_operation(
                entity_type="content",
                entity_id="post_123",
                operation_type=OperationType.CREATE,
                data={"title": "My Post", "content": "Hello World"}
            )
            
            op2 = await manager.queue_operation(
                entity_type="content",
                entity_id="post_124",
                operation_type=OperationType.UPDATE,
                data={"title": "Updated Post", "updated_at": datetime.now().isoformat()}
            )
            
            print(f"Queued operations: {op1}, {op2}")
            
            # Start sync session
            session_id = await manager.start_sync_session(
                user_id="user123",
                device_id="device456",
                entity_types=["content"]
            )
            
            # Sync operations
            result = await manager.sync_pending_operations(session_id)
            print(f"Sync result: {result}")
            
            # Complete session
            session = await manager.complete_sync_session(session_id)
            print(f"Session completed: {session.session_id}")
            
            # Get statistics
            stats = manager.get_sync_statistics()
            print(f"Sync stats: {stats}")
            
        finally:
            await manager.close()
    
    asyncio.run(main())