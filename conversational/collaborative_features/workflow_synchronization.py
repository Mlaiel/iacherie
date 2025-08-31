"""
Workflow Synchronization Module - Advanced Collaboration Synchronization

Enterprise-grade workflow synchronization for multi-format content creators
enabling version control, conflict resolution, synchronous editing, and workflow state management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import hashlib
import difflib
from sqlalchemy.ext.asyncio import AsyncSession
import websockets

from ...core.database import get_db_session
from ...core.exceptions import BusinessLogicError, ValidationError
from ...utils.cache_manager import CacheManager
from ...utils.file_manager import FileManager
from ...utils.diff_engine import DiffEngine
from ...utils.operational_transform import OperationalTransform

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Synchronization status for workflow items"""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    MERGING = "merging"
    FAILED = "failed"
    LOCKED = "locked"


class ConflictType(Enum):
    """Types of synchronization conflicts"""
    CONTENT_CONFLICT = "content_conflict"
    METADATA_CONFLICT = "metadata_conflict"
    PERMISSION_CONFLICT = "permission_conflict"
    VERSION_CONFLICT = "version_conflict"
    TIMESTAMP_CONFLICT = "timestamp_conflict"
    STRUCTURE_CONFLICT = "structure_conflict"


class VersionType(Enum):
    """Types of version changes"""
    MAJOR = "major"      # Breaking changes
    MINOR = "minor"      # Feature additions
    PATCH = "patch"      # Bug fixes
    DRAFT = "draft"      # Work in progress
    SNAPSHOT = "snapshot" # Automatic saves


class EditOperation(Enum):
    """Types of editing operations for collaborative editing"""
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    FORMAT = "format"
    MOVE = "move"
    COMMENT = "comment"


@dataclass
class WorkflowVersion:
    """Workflow version with comprehensive metadata"""
    version_id: str
    workflow_id: str
    version_number: str
    version_type: VersionType
    content_hash: str
    content_data: Dict[str, Any]
    metadata: Dict[str, Any]
    author_id: str
    commit_message: str
    parent_version_id: Optional[str]
    branch_name: str
    tags: List[str]
    file_changes: List[Dict[str, Any]]
    collaborators: List[str]
    approval_status: str
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary representation"""



        return {
            "version_id": self.version_id,
            "workflow_id": self.workflow_id,
            "version_number": self.version_number,
            "version_type": self.version_type.value,
            "content_hash": self.content_hash,
            "content_data": self.content_data,
            "metadata": self.metadata,
            "author_id": self.author_id,
            "commit_message": self.commit_message,
            "parent_version_id": self.parent_version_id,
            "branch_name": self.branch_name,
            "tags": self.tags,
            "file_changes": self.file_changes,
            "collaborators": self.collaborators,
            "approval_status": self.approval_status,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class SyncConflict:
    """Synchronization conflict representation"""
    conflict_id: str
    workflow_id: str
    conflict_type: ConflictType
    affected_users: List[str]
    local_version: Dict[str, Any]
    remote_version: Dict[str, Any]
    conflict_data: Dict[str, Any]
    suggested_resolution: Dict[str, Any]
    priority_level: int
    auto_resolvable: bool
    resolution_strategies: List[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dictionary representation"""



        return {
            "conflict_id": self.conflict_id,
            "workflow_id": self.workflow_id,
            "conflict_type": self.conflict_type.value,
            "affected_users": self.affected_users,
            "local_version": self.local_version,
            "remote_version": self.remote_version,
            "conflict_data": self.conflict_data,
            "suggested_resolution": self.suggested_resolution,
            "priority_level": self.priority_level,
            "auto_resolvable": self.auto_resolvable,
            "resolution_strategies": self.resolution_strategies,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by
        }


@dataclass
class EditEvent:
    """Real-time editing event for collaborative editing"""
    event_id: str
    workflow_id: str
    user_id: str
    operation: EditOperation
    position: int
    content: str
    length: int
    metadata: Dict[str, Any]
    timestamp: datetime
    applied: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edit event to dictionary"""



        return {
            "event_id": self.event_id,
            "workflow_id": self.workflow_id,
            "user_id": self.user_id,
            "operation": self.operation.value,
            "position": self.position,
            "content": self.content,
            "length": self.length,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "applied": self.applied
        }


class WorkflowSynchronizer:
    """Advanced workflow synchronization manager"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
        self.file_manager = FileManager()
        self.diff_engine = DiffEngine()
        self.operational_transform = OperationalTransform()
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.sync_locks: Dict[str, str] = {}  # workflow_id -> user_id
        
    async def initialize_workflow_sync(
        self,
        workflow_id: str,
        initial_content: Dict[str, Any],
        created_by: str,
        sync_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize workflow synchronization system"""



        try:
            # Create initial version
            initial_version = await self._create_initial_version(
                workflow_id, initial_content, created_by
            )
            
            # Set up sync metadata
            sync_metadata = {
                "workflow_id": workflow_id,
                "current_version": initial_version["version_id"],
                "sync_enabled": True,
                "conflict_resolution_mode": sync_settings.get("conflict_resolution", "manual"),
                "auto_save_interval": sync_settings.get("auto_save_interval", 30),
                "max_versions": sync_settings.get("max_versions", 100),
                "collaborators": [created_by],
                "active_editors": [],
                "sync_locks": {},
                "pending_operations": [],
                "last_sync": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.cache.set(f"workflow_sync:{workflow_id}", sync_metadata, ttl=86400)
            
            # Initialize active workflow tracking
            self.active_workflows[workflow_id] = {
                "metadata": sync_metadata,
                "active_users": set([created_by]),
                "edit_queue": [],
                "last_activity": datetime.utcnow()
            }
            
            logger.info(f"Workflow sync initialized: {workflow_id}")
            return {
                "workflow_id": workflow_id,
                "initial_version": initial_version,
                "sync_status": SyncStatus.SYNCED.value,
                "initialized_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error initializing workflow sync: {str(e)}")
            raise BusinessLogicError(f"Failed to initialize sync: {str(e)}")
    
    async def join_workflow_session(
        self,
        workflow_id: str,
        user_id: str,
        client_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Join collaborative workflow session"""



        try:
            sync_metadata = await self.cache.get(f"workflow_sync:{workflow_id}")
            if not sync_metadata:
                raise ValidationError("Workflow sync not found")
            
            # Check if user has permission
            if user_id not in sync_metadata["collaborators"]:
                raise ValidationError("User not authorized for this workflow")
            
            # Get current version
            current_version = await self._get_version(
                workflow_id, sync_metadata["current_version"]
            )
            
            # Check if client needs sync
            needs_sync = False
            sync_operations = []
            
            if client_version and client_version != current_version["version_id"]:
                needs_sync = True
                sync_operations = await self._get_sync_operations(
                    workflow_id, client_version, current_version["version_id"]
                )
            
            # Add user to active editors
            sync_metadata["active_editors"].append(user_id)
            sync_metadata["active_editors"] = list(set(sync_metadata["active_editors"]))
            
            await self.cache.set(f"workflow_sync:{workflow_id}", sync_metadata, ttl=86400)
            
            # Update active workflow tracking
            if workflow_id not in self.active_workflows:
                self.active_workflows[workflow_id] = {
                    "metadata": sync_metadata,
                    "active_users": set(),
                    "edit_queue": [],
                    "last_activity": datetime.utcnow()
                }
            
            self.active_workflows[workflow_id]["active_users"].add(user_id)
            self.active_workflows[workflow_id]["last_activity"] = datetime.utcnow()
            
            return {
                "workflow_id": workflow_id,
                "current_version": current_version,
                "needs_sync": needs_sync,
                "sync_operations": sync_operations,
                "active_editors": sync_metadata["active_editors"],
                "session_joined": True
            }
            
        except Exception as e:
            logger.error(f"Error joining workflow session: {str(e)}")
            raise BusinessLogicError(f"Failed to join session: {str(e)}")
    
    async def leave_workflow_session(
        self,
        workflow_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Leave collaborative workflow session"""



        try:
            sync_metadata = await self.cache.get(f"workflow_sync:{workflow_id}")
            if sync_metadata:
                # Remove from active editors
                if user_id in sync_metadata["active_editors"]:
                    sync_metadata["active_editors"].remove(user_id)
                
                await self.cache.set(f"workflow_sync:{workflow_id}", sync_metadata, ttl=86400)
            
            # Update active workflow tracking
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["active_users"].discard(user_id)
                
                # Clean up if no active users
                if not self.active_workflows[workflow_id]["active_users"]:
                    del self.active_workflows[workflow_id]
            
            # Release any locks held by user
            if workflow_id in self.sync_locks and self.sync_locks[workflow_id] == user_id:
                del self.sync_locks[workflow_id]
            
            return {
                "workflow_id": workflow_id,
                "user_id": user_id,
                "session_left": True
            }
            
        except Exception as e:
            logger.error(f"Error leaving workflow session: {str(e)}")
            return {"error": str(e)}
    
    async def synchronize_changes(
        self,
        workflow_id: str,
        user_id: str,
        changes: List[Dict[str, Any]],
        client_version: str
    ) -> Dict[str, Any]:
        """Synchronize workflow changes across collaborators"""



        try:
            # Acquire sync lock
            if not await self._acquire_sync_lock(workflow_id, user_id):
                return {
                    "status": "locked",
                    "message": "Workflow is locked by another user",
                    "retry_after": 5
                }
            
            try:
                sync_metadata = await self.cache.get(f"workflow_sync:{workflow_id}")
                if not sync_metadata:
                    raise ValidationError("Workflow sync not found")
                
                current_version_id = sync_metadata["current_version"]
                
                # Check for conflicts
                conflicts = await self._detect_conflicts(
                    workflow_id, client_version, current_version_id, changes
                )
                
                if conflicts:
                    return {
                        "status": "conflicts_detected",
                        "conflicts": [conflict.to_dict() for conflict in conflicts],
                        "requires_resolution": True
                    }
                
                # Apply changes
                new_version = await self._apply_changes(
                    workflow_id, current_version_id, changes, user_id
                )
                
                # Update sync metadata
                sync_metadata["current_version"] = new_version["version_id"]
                sync_metadata["last_sync"] = datetime.utcnow().isoformat()
                
                await self.cache.set(f"workflow_sync:{workflow_id}", sync_metadata, ttl=86400)
                
                # Broadcast changes to other collaborators
                await self._broadcast_changes(workflow_id, new_version, user_id)
                
                return {
                    "status": "synchronized",
                    "new_version": new_version,
                    "changes_applied": len(changes),
                    "synced_at": datetime.utcnow().isoformat()
                }
                
            finally:
                # Release sync lock
                await self._release_sync_lock(workflow_id, user_id)
                
        except Exception as e:
            logger.error(f"Error synchronizing changes: {str(e)}")
            raise BusinessLogicError(f"Failed to synchronize: {str(e)}")
    
    async def _create_initial_version(
        self,
        workflow_id: str,
        content: Dict[str, Any],
        author_id: str
    ) -> Dict[str, Any]:
        """Create initial version for workflow"""
        version_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
        
        version = WorkflowVersion(
            version_id=version_id,
            workflow_id=workflow_id,
            version_number="1.0.0",
            version_type=VersionType.MAJOR,
            content_hash=content_hash,
            content_data=content,
            metadata={
                "creation_type": "initial",
                "workflow_type": content.get("type", "unknown"),
                "file_count": len(content.get("files", [])),
                "total_size": sum(f.get("size", 0) for f in content.get("files", []))
            },
            author_id=author_id,
            commit_message="Initial version",
            parent_version_id=None,
            branch_name="main",
            tags=["initial"],
            file_changes=[],
            collaborators=[author_id],
            approval_status="approved",
            created_at=datetime.utcnow()
        )
        
        version_data = version.to_dict()
        await self.cache.set(f"version:{version_id}", version_data, ttl=2592000)  # 30 days
        
        return version_data
    
    async def _get_version(self, workflow_id: str, version_id: str) -> Dict[str, Any]:
        """Get workflow version data"""
        version_data = await self.cache.get(f"version:{version_id}")
        if not version_data:
            raise ValidationError(f"Version {version_id} not found")
        return version_data
    
    async def _get_sync_operations(
        self,
        workflow_id: str,
        from_version: str,
        to_version: str
    ) -> List[Dict[str, Any]]:
        """Get operations needed to sync from one version to another"""



        try:
            from_version_data = await self._get_version(workflow_id, from_version)
            to_version_data = await self._get_version(workflow_id, to_version)
            
            # Calculate differences
            operations = await self.diff_engine.calculate_sync_operations(
                from_version_data["content_data"],
                to_version_data["content_data"]
            )
            
            return operations
            
        except Exception as e:
            logger.error(f"Error getting sync operations: {str(e)}")
            return []
    
    async def _detect_conflicts(
        self,
        workflow_id: str,
        client_version: str,
        server_version: str,
        changes: List[Dict[str, Any]]
    ) -> List[SyncConflict]:
        """Detect synchronization conflicts"""
        conflicts = []
        
        try:
            if client_version == server_version:
                return conflicts  # No conflicts if versions match
            
            client_data = await self._get_version(workflow_id, client_version)
            server_data = await self._get_version(workflow_id, server_version)
            
            # Detect content conflicts
            content_conflicts = await self._detect_content_conflicts(
                workflow_id, client_data, server_data, changes
            )
            conflicts.extend(content_conflicts)
            
            # Detect metadata conflicts
            metadata_conflicts = await self._detect_metadata_conflicts(
                workflow_id, client_data, server_data, changes
            )
            conflicts.extend(metadata_conflicts)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting conflicts: {str(e)}")
            return []
    
    async def _detect_content_conflicts(
        self,
        workflow_id: str,
        client_data: Dict[str, Any],
        server_data: Dict[str, Any],
        changes: List[Dict[str, Any]]
    ) -> List[SyncConflict]:
        """Detect content-based conflicts"""
        conflicts = []
        
        # Implementation would analyze content differences
        # and detect overlapping changes
        
        return conflicts
    
    async def _detect_metadata_conflicts(
        self,
        workflow_id: str,
        client_data: Dict[str, Any],
        server_data: Dict[str, Any],
        changes: List[Dict[str, Any]]
    ) -> List[SyncConflict]:
        """Detect metadata-based conflicts"""
        conflicts = []
        
        # Implementation would analyze metadata differences
        # such as permissions, timestamps, etc.
        
        return conflicts
    
    async def _apply_changes(
        self,
        workflow_id: str,
        current_version_id: str,
        changes: List[Dict[str, Any]],
        author_id: str
    ) -> Dict[str, Any]:
        """Apply changes and create new version"""



        try:
            current_version = await self._get_version(workflow_id, current_version_id)
            
            # Apply changes to content
            new_content = await self._merge_changes(
                current_version["content_data"], changes
            )
            
            # Calculate new version number
            new_version_number = await self._calculate_next_version(
                current_version["version_number"], changes
            )
            
            # Create new version
            new_version_id = str(uuid.uuid4())
            content_hash = hashlib.sha256(
                json.dumps(new_content, sort_keys=True).encode()
            ).hexdigest()
            
            new_version = WorkflowVersion(
                version_id=new_version_id,
                workflow_id=workflow_id,
                version_number=new_version_number,
                version_type=VersionType.MINOR,
                content_hash=content_hash,
                content_data=new_content,
                metadata={
                    "sync_changes": len(changes),
                    "parent_version": current_version_id,
                    "change_summary": await self._summarize_changes(changes)
                },
                author_id=author_id,
                commit_message=f"Synchronized changes ({len(changes)} operations)",
                parent_version_id=current_version_id,
                branch_name="main",
                tags=[],
                file_changes=changes,
                collaborators=current_version["collaborators"],
                approval_status="pending",
                created_at=datetime.utcnow()
            )
            
            new_version_data = new_version.to_dict()
            await self.cache.set(f"version:{new_version_id}", new_version_data, ttl=2592000)
            
            return new_version_data
            
        except Exception as e:
            logger.error(f"Error applying changes: {str(e)}")
            raise BusinessLogicError(f"Failed to apply changes: {str(e)}")
    
    async def _merge_changes(
        self,
        content: Dict[str, Any],
        changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge changes into content"""
        merged_content = content.copy()
        
        for change in changes:
            change_type = change.get("type")
            path = change.get("path", [])
            value = change.get("value")
            
            if change_type == "update":
                await self._apply_update_change(merged_content, path, value)
            elif change_type == "add":
                await self._apply_add_change(merged_content, path, value)
            elif change_type == "delete":
                await self._apply_delete_change(merged_content, path)
        
        return merged_content
    
    async def _apply_update_change(
        self,
        content: Dict[str, Any],
        path: List[str],
        value: Any
    ):
        """Apply update change to content"""
        current = content
        for key in path[:-1]:
            current = current[key]
        current[path[-1]] = value
    
    async def _apply_add_change(
        self,
        content: Dict[str, Any],
        path: List[str],
        value: Any
    ):
        """Apply add change to content"""
        current = content
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    async def _apply_delete_change(
        self,
        content: Dict[str, Any],
        path: List[str]
    ):
        """Apply delete change to content"""
        current = content
        for key in path[:-1]:
            current = current[key]
        if path[-1] in current:
            del current[path[-1]]
    
    async def _calculate_next_version(
        self,
        current_version: str,
        changes: List[Dict[str, Any]]
    ) -> str:
        """Calculate next version number based on changes"""
        # Simple semantic versioning
        parts = current_version.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        # Check for breaking changes
        has_breaking_changes = any(
            change.get("breaking", False) for change in changes
        )
        
        if has_breaking_changes:
            major += 1
            minor = 0
            patch = 0
        else:
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    async def _summarize_changes(self, changes: List[Dict[str, Any]]) -> str:
        """Create summary of changes"""
        if not changes:
            return "No changes"
        
        change_types = {}
        for change in changes:
            change_type = change.get("type", "unknown")
            change_types[change_type] = change_types.get(change_type, 0) + 1
        
        summary_parts = []
        for change_type, count in change_types.items():
            summary_parts.append(f"{count} {change_type}")
        
        return ", ".join(summary_parts)
    
    async def _broadcast_changes(
        self,
        workflow_id: str,
        new_version: Dict[str, Any],
        author_id: str
    ):
        """Broadcast changes to other collaborators"""
        if workflow_id not in self.active_workflows:
            return
        
        active_users = self.active_workflows[workflow_id]["active_users"]
        
        # Create broadcast message
        broadcast_data = {
            "type": "workflow_updated",
            "workflow_id": workflow_id,
            "new_version": new_version,
            "author_id": author_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to active users (except author)
        for user_id in active_users:
            if user_id != author_id:
                await self._send_sync_notification(user_id, broadcast_data)
    
    async def _send_sync_notification(self, user_id: str, data: Dict[str, Any]):
        """Send sync notification to user"""
        # Implementation would send via WebSocket or notification service
        logger.info(f"Sending sync notification to user {user_id}")
    
    async def _acquire_sync_lock(self, workflow_id: str, user_id: str) -> bool:
        """Acquire sync lock for workflow"""
        if workflow_id in self.sync_locks:
            return self.sync_locks[workflow_id] == user_id
        
        self.sync_locks[workflow_id] = user_id
        return True
    
    async def _release_sync_lock(self, workflow_id: str, user_id: str):
        """Release sync lock for workflow"""
        if workflow_id in self.sync_locks and self.sync_locks[workflow_id] == user_id:
            del self.sync_locks[workflow_id]


class ContentVersionController:
    """Advanced content version control system"""
    
    def __init__(self, cache_manager: CacheManager, file_manager: FileManager):
        self.cache = cache_manager
        self.file_manager = file_manager
        self.version_trees: Dict[str, Dict[str, Any]] = {}
    
    async def create_branch(
        self,
        workflow_id: str,
        branch_name: str,
        source_version_id: str,
        created_by: str,
        description: str
    ) -> Dict[str, Any]:
        """Create new branch from existing version"""



        try:
            # Validate source version
            source_version = await self.cache.get(f"version:{source_version_id}")
            if not source_version:
                raise ValidationError("Source version not found")
            
            # Create branch metadata
            branch_id = str(uuid.uuid4())
            branch_data = {
                "branch_id": branch_id,
                "workflow_id": workflow_id,
                "branch_name": branch_name,
                "description": description,
                "source_version_id": source_version_id,
                "head_version_id": source_version_id,
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "merge_conflicts": [],
                "collaborators": [created_by]
            }
            
            await self.cache.set(f"branch:{branch_id}", branch_data, ttl=2592000)
            
            # Update workflow branches list
            await self._add_branch_to_workflow(workflow_id, branch_id)
            
            return {
                "branch_id": branch_id,
                "branch_name": branch_name,
                "head_version": source_version_id,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Error creating branch: {str(e)}")
            raise BusinessLogicError(f"Failed to create branch: {str(e)}")
    
    async def merge_branches(
        self,
        workflow_id: str,
        source_branch_id: str,
        target_branch_id: str,
        merge_strategy: str,
        merged_by: str
    ) -> Dict[str, Any]:
        """Merge one branch into another"""



        try:
            source_branch = await self.cache.get(f"branch:{source_branch_id}")
            target_branch = await self.cache.get(f"branch:{target_branch_id}")
            
            if not source_branch or not target_branch:
                raise ValidationError("Branch not found")
            
            # Get versions to merge
            source_version = await self.cache.get(f"version:{source_branch['head_version_id']}")
            target_version = await self.cache.get(f"version:{target_branch['head_version_id']}")
            
            # Detect conflicts
            conflicts = await self._detect_merge_conflicts(source_version, target_version)
            
            if conflicts and merge_strategy != "force":
                return {
                    "status": "conflicts_detected",
                    "conflicts": conflicts,
                    "requires_resolution": True
                }
            
            # Perform merge
            merged_content = await self._perform_merge(
                source_version, target_version, merge_strategy
            )
            
            # Create merged version
            merged_version = await self._create_merged_version(
                workflow_id, source_version, target_version, merged_content, merged_by
            )
            
            # Update target branch head
            target_branch["head_version_id"] = merged_version["version_id"]
            target_branch["last_merge"] = datetime.utcnow().isoformat()
            
            await self.cache.set(f"branch:{target_branch_id}", target_branch, ttl=2592000)
            
            return {
                "status": "merged",
                "merged_version": merged_version,
                "conflicts_resolved": len(conflicts) if conflicts else 0
            }
            
        except Exception as e:
            logger.error(f"Error merging branches: {str(e)}")
            raise BusinessLogicError(f"Failed to merge branches: {str(e)}")
    
    async def compare_versions(
        self,
        version_a_id: str,
        version_b_id: str
    ) -> Dict[str, Any]:
        """Compare two versions and show differences"""



        try:
            version_a = await self.cache.get(f"version:{version_a_id}")
            version_b = await self.cache.get(f"version:{version_b_id}")
            
            if not version_a or not version_b:
                raise ValidationError("Version not found")
            
            # Calculate differences
            diff_result = await self.diff_engine.compare_versions(
                version_a["content_data"], version_b["content_data"]
            )
            
            return {
                "version_a": version_a_id,
                "version_b": version_b_id,
                "differences": diff_result,
                "similarity_score": await self._calculate_similarity_score(
                    version_a["content_data"], version_b["content_data"]
                ),
                "compared_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error comparing versions: {str(e)}")
            raise BusinessLogicError(f"Failed to compare versions: {str(e)}")
    
    async def _add_branch_to_workflow(self, workflow_id: str, branch_id: str):
        """Add branch to workflow branches list"""
        branches_key = f"workflow_branches:{workflow_id}"
        branches_data = await self.cache.get(branches_key)
        
        if not branches_data:
            branches_data = {"workflow_id": workflow_id, "branches": []}
        
        branches_data["branches"].append(branch_id)
        await self.cache.set(branches_key, branches_data, ttl=2592000)
    
    async def _detect_merge_conflicts(
        self,
        source_version: Dict[str, Any],
        target_version: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between two versions"""
        conflicts = []
        
        # Implementation would analyze content differences
        # and detect conflicting changes
        
        return conflicts
    
    async def _perform_merge(
        self,
        source_version: Dict[str, Any],
        target_version: Dict[str, Any],
        strategy: str
    ) -> Dict[str, Any]:
        """Perform merge operation"""
        if strategy == "theirs":
            return source_version["content_data"]
        elif strategy == "ours":
            return target_version["content_data"]
        else:
            # Three-way merge
            return await self._three_way_merge(source_version, target_version)
    
    async def _three_way_merge(
        self,
        source_version: Dict[str, Any],
        target_version: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform three-way merge"""
        # Implementation would find common ancestor and merge changes
        merged_content = target_version["content_data"].copy()
        
        # Merge source changes that don't conflict
        source_content = source_version["content_data"]
        
        for key, value in source_content.items():
            if key not in merged_content:
                merged_content[key] = value
        
        return merged_content
    
    async def _create_merged_version(
        self,
        workflow_id: str,
        source_version: Dict[str, Any],
        target_version: Dict[str, Any],
        merged_content: Dict[str, Any],
        merged_by: str
    ) -> Dict[str, Any]:
        """Create version from merge result"""
        version_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(
            json.dumps(merged_content, sort_keys=True).encode()
        ).hexdigest()
        
        # Calculate next version number
        target_version_num = target_version["version_number"]
        next_version = await self._increment_version(target_version_num, "minor")
        
        merged_version = WorkflowVersion(
            version_id=version_id,
            workflow_id=workflow_id,
            version_number=next_version,
            version_type=VersionType.MINOR,
            content_hash=content_hash,
            content_data=merged_content,
            metadata={
                "merge_type": "branch_merge",
                "source_version": source_version["version_id"],
                "target_version": target_version["version_id"],
                "merge_timestamp": datetime.utcnow().isoformat()
            },
            author_id=merged_by,
            commit_message=f"Merge branch into {target_version['branch_name']}",
            parent_version_id=target_version["version_id"],
            branch_name=target_version["branch_name"],
            tags=["merge"],
            file_changes=[],
            collaborators=list(set(
                source_version["collaborators"] + target_version["collaborators"]
            )),
            approval_status="pending",
            created_at=datetime.utcnow()
        )
        
        version_data = merged_version.to_dict()
        await self.cache.set(f"version:{version_id}", version_data, ttl=2592000)
        
        return version_data
    
    async def _increment_version(self, version_string: str, increment_type: str) -> str:
        """Increment version number"""
        parts = version_string.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    async def _calculate_similarity_score(
        self,
        content_a: Dict[str, Any],
        content_b: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between two content versions"""
        # Simple similarity calculation based on shared keys
        keys_a = set(content_a.keys())
        keys_b = set(content_b.keys())
        
        if not keys_a and not keys_b:
            return 1.0
        
        intersection = keys_a & keys_b
        union = keys_a | keys_b
        
        return len(intersection) / len(union) if union else 0.0


class ConflictResolutionManager:
    """Advanced conflict resolution for collaborative workflows"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.resolution_strategies = {
            "auto_merge": self._auto_merge_strategy,
            "manual_review": self._manual_review_strategy,
            "timestamp_priority": self._timestamp_priority_strategy,
            "user_priority": self._user_priority_strategy
        }
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution_strategy: str,
        resolved_by: str,
        resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve synchronization conflict"""



        try:
            conflict_data = await self.cache.get(f"conflict:{conflict_id}")
            if not conflict_data:
                raise ValidationError("Conflict not found")
            
            if conflict_data.get("resolved_at"):
                raise ValidationError("Conflict already resolved")
            
            # Apply resolution strategy
            if resolution_strategy in self.resolution_strategies:
                resolution_result = await self.resolution_strategies[resolution_strategy](
                    conflict_data, resolution_data
                )
            else:
                raise ValidationError(f"Unknown resolution strategy: {resolution_strategy}")
            
            # Update conflict record
            conflict_data["resolved_at"] = datetime.utcnow().isoformat()
            conflict_data["resolved_by"] = resolved_by
            conflict_data["resolution_strategy"] = resolution_strategy
            conflict_data["resolution_result"] = resolution_result
            
            await self.cache.set(f"conflict:{conflict_id}", conflict_data, ttl=2592000)
            
            return {
                "conflict_id": conflict_id,
                "status": "resolved",
                "resolution_strategy": resolution_strategy,
                "resolution_result": resolution_result
            }
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            raise BusinessLogicError(f"Failed to resolve conflict: {str(e)}")
    
    async def _auto_merge_strategy(
        self,
        conflict_data: Dict[str, Any],
        resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Automatic merge conflict resolution"""
        # Implementation would automatically merge non-conflicting parts
        return {
            "strategy": "auto_merge",
            "merged_content": {},
            "conflicts_remaining": 0
        }
    
    async def _manual_review_strategy(
        self,
        conflict_data: Dict[str, Any],
        resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manual review conflict resolution"""



        return {
            "strategy": "manual_review",
            "reviewer_decision": resolution_data.get("decision"),
            "final_content": resolution_data.get("resolved_content")
        }
    
    async def _timestamp_priority_strategy(
        self,
        conflict_data: Dict[str, Any],
        resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Timestamp-based priority resolution"""
        # Use most recent changes
        local_time = conflict_data["local_version"].get("timestamp")
        remote_time = conflict_data["remote_version"].get("timestamp")
        
        if local_time > remote_time:
            winner = "local"
            final_content = conflict_data["local_version"]["content"]
        else:
            winner = "remote"
            final_content = conflict_data["remote_version"]["content"]
        
        return {
            "strategy": "timestamp_priority",
            "winner": winner,
            "final_content": final_content
        }
    
    async def _user_priority_strategy(
        self,
        conflict_data: Dict[str, Any],
        resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """User priority-based resolution"""
        priority_user = resolution_data.get("priority_user")
        
        if priority_user == conflict_data["local_version"]["author"]:
            final_content = conflict_data["local_version"]["content"]
        else:
            final_content = conflict_data["remote_version"]["content"]
        
        return {
            "strategy": "user_priority",
            "priority_user": priority_user,
            "final_content": final_content
        }


class SynchronousEditingEngine:
    """Real-time collaborative editing engine"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.operational_transform = OperationalTransform()
        self.active_editors: Dict[str, Set[str]] = {}  # workflow_id -> user_ids
        self.edit_cursors: Dict[str, Dict[str, Dict[str, Any]]] = {}  # workflow_id -> user_id -> cursor
    
    async def start_editing_session(
        self,
        workflow_id: str,
        user_id: str,
        document_id: str
    ) -> Dict[str, Any]:
        """Start real-time editing session"""



        try:
            # Initialize editor tracking
            if workflow_id not in self.active_editors:
                self.active_editors[workflow_id] = set()
                self.edit_cursors[workflow_id] = {}
            
            self.active_editors[workflow_id].add(user_id)
            self.edit_cursors[workflow_id][user_id] = {
                "position": 0,
                "selection": {"start": 0, "end": 0},
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # Get current document state
            document_state = await self._get_document_state(workflow_id, document_id)
            
            # Get other active editors
            other_editors = [
                {
                    "user_id": editor_id,
                    "cursor": self.edit_cursors[workflow_id].get(editor_id, {})
                }
                for editor_id in self.active_editors[workflow_id]
                if editor_id != user_id
            ]
            
            return {
                "session_id": f"{workflow_id}_{user_id}",
                "document_state": document_state,
                "other_editors": other_editors,
                "started_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error starting editing session: {str(e)}")
            raise BusinessLogicError(f"Failed to start editing session: {str(e)}")
    
    async def apply_edit_operation(
        self,
        workflow_id: str,
        user_id: str,
        operation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply real-time edit operation"""



        try:
            # Validate operation
            if not await self._validate_edit_operation(operation):
                raise ValidationError("Invalid edit operation")
            
            # Transform operation against concurrent operations
            transformed_operation = await self.operational_transform.transform_operation(
                workflow_id, operation
            )
            
            # Apply operation to document
            result = await self._apply_operation_to_document(
                workflow_id, transformed_operation
            )
            
            # Broadcast to other editors
            await self._broadcast_operation(workflow_id, user_id, transformed_operation)
            
            # Update cursor position
            await self._update_cursor_position(workflow_id, user_id, transformed_operation)
            
            return {
                "operation_id": transformed_operation.get("id"),
                "applied": True,
                "document_version": result.get("version"),
                "cursor_position": self.edit_cursors[workflow_id][user_id]["position"]
            }
            
        except Exception as e:
            logger.error(f"Error applying edit operation: {str(e)}")
            raise BusinessLogicError(f"Failed to apply operation: {str(e)}")
    
    async def update_cursor_position(
        self,
        workflow_id: str,
        user_id: str,
        position: int,
        selection: Dict[str, int]
    ) -> Dict[str, Any]:
        """Update user cursor position"""



        try:
            if workflow_id in self.edit_cursors and user_id in self.edit_cursors[workflow_id]:
                self.edit_cursors[workflow_id][user_id].update({
                    "position": position,
                    "selection": selection,
                    "last_activity": datetime.utcnow().isoformat()
                })
                
                # Broadcast cursor update to other editors
                await self._broadcast_cursor_update(workflow_id, user_id, position, selection)
            
            return {
                "cursor_updated": True,
                "position": position,
                "selection": selection
            }
            
        except Exception as e:
            logger.error(f"Error updating cursor position: {str(e)}")
            return {"error": str(e)}
    
    async def end_editing_session(
        self,
        workflow_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """End real-time editing session"""



        try:
            if workflow_id in self.active_editors:
                self.active_editors[workflow_id].discard(user_id)
                
                if workflow_id in self.edit_cursors and user_id in self.edit_cursors[workflow_id]:
                    del self.edit_cursors[workflow_id][user_id]
                
                # Clean up if no active editors
                if not self.active_editors[workflow_id]:
                    del self.active_editors[workflow_id]
                    if workflow_id in self.edit_cursors:
                        del self.edit_cursors[workflow_id]
                
                # Notify other editors
                await self._broadcast_editor_left(workflow_id, user_id)
            
            return {
                "session_ended": True,
                "ended_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error ending editing session: {str(e)}")
            return {"error": str(e)}
    
    async def _get_document_state(
        self,
        workflow_id: str,
        document_id: str
    ) -> Dict[str, Any]:
        """Get current document state"""
        document_data = await self.cache.get(f"document:{workflow_id}:{document_id}")
        if not document_data:
            # Initialize empty document
            document_data = {
                "document_id": document_id,
                "workflow_id": workflow_id,
                "content": "",
                "version": 1,
                "last_modified": datetime.utcnow().isoformat()
            }
            await self.cache.set(f"document:{workflow_id}:{document_id}", document_data, ttl=86400)
        
        return document_data
    
    async def _validate_edit_operation(self, operation: Dict[str, Any]) -> bool:
        """Validate edit operation"""
        required_fields = ["type", "position"]
        return all(field in operation for field in required_fields)
    
    async def _apply_operation_to_document(
        self,
        workflow_id: str,
        operation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply operation to document"""
        # Implementation would apply the operation to the document content
        # and return the updated document state
        return {"version": 1, "applied": True}
    
    async def _broadcast_operation(
        self,
        workflow_id: str,
        sender_id: str,
        operation: Dict[str, Any]
    ):
        """Broadcast operation to other editors"""
        if workflow_id not in self.active_editors:
            return
        
        for editor_id in self.active_editors[workflow_id]:
            if editor_id != sender_id:
                # Send operation to editor
                await self._send_operation_to_editor(editor_id, operation)
    
    async def _broadcast_cursor_update(
        self,
        workflow_id: str,
        user_id: str,
        position: int,
        selection: Dict[str, int]
    ):
        """Broadcast cursor update to other editors"""
        if workflow_id not in self.active_editors:
            return
        
        cursor_data = {
            "type": "cursor_update",
            "user_id": user_id,
            "position": position,
            "selection": selection
        }
        
        for editor_id in self.active_editors[workflow_id]:
            if editor_id != user_id:
                await self._send_cursor_update_to_editor(editor_id, cursor_data)
    
    async def _broadcast_editor_left(self, workflow_id: str, user_id: str):
        """Broadcast that editor left session"""
        if workflow_id not in self.active_editors:
            return
        
        leave_data = {
            "type": "editor_left",
            "user_id": user_id
        }
        
        for editor_id in self.active_editors[workflow_id]:
            await self._send_editor_update_to_editor(editor_id, leave_data)
    
    async def _update_cursor_position(
        self,
        workflow_id: str,
        user_id: str,
        operation: Dict[str, Any]
    ):
        """Update cursor position based on operation"""
        if workflow_id in self.edit_cursors and user_id in self.edit_cursors[workflow_id]:
            # Adjust cursor position based on operation type
            operation_type = operation.get("type")
            operation_position = operation.get("position", 0)
            operation_length = operation.get("length", 0)
            
            current_position = self.edit_cursors[workflow_id][user_id]["position"]
            
            if operation_type == "insert" and operation_position <= current_position:
                new_position = current_position + operation_length
            elif operation_type == "delete" and operation_position < current_position:
                new_position = max(operation_position, current_position - operation_length)
            else:
                new_position = current_position
            
            self.edit_cursors[workflow_id][user_id]["position"] = new_position
    
    async def _send_operation_to_editor(self, editor_id: str, operation: Dict[str, Any]):
        """Send operation to specific editor"""
        # Implementation would send via WebSocket or message queue
        logger.info(f"Sending operation to editor {editor_id}")
    
    async def _send_cursor_update_to_editor(self, editor_id: str, cursor_data: Dict[str, Any]):
        """Send cursor update to specific editor"""
        # Implementation would send via WebSocket
        logger.info(f"Sending cursor update to editor {editor_id}")
    
    async def _send_editor_update_to_editor(self, editor_id: str, update_data: Dict[str, Any]):
        """Send editor update to specific editor"""
        # Implementation would send via WebSocket
        logger.info(f"Sending editor update to editor {editor_id}")


class WorkflowStateManager:
    """Workflow state management for collaborative processes"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.state_transitions = {
            "draft": ["review", "published", "archived"],
            "review": ["draft", "approved", "rejected"],
            "approved": ["published", "draft"],
            "rejected": ["draft"],
            "published": ["archived", "draft"],
            "archived": ["draft"]
        }
    
    async def get_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow state"""



        try:
            state_data = await self.cache.get(f"workflow_state:{workflow_id}")
            if not state_data:
                # Initialize default state
                state_data = {
                    "workflow_id": workflow_id,
                    "current_state": "draft",
                    "state_history": [],
                    "permissions": {},
                    "metadata": {},
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                await self.cache.set(f"workflow_state:{workflow_id}", state_data, ttl=86400)
            
            return state_data
            
        except Exception as e:
            logger.error(f"Error getting workflow state: {str(e)}")
            raise BusinessLogicError(f"Failed to get workflow state: {str(e)}")
    
    async def transition_state(
        self,
        workflow_id: str,
        new_state: str,
        user_id: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transition workflow to new state"""



        try:
            state_data = await self.get_workflow_state(workflow_id)
            current_state = state_data["current_state"]
            
            # Validate transition
            if new_state not in self.state_transitions.get(current_state, []):
                raise ValidationError(
                    f"Invalid transition from {current_state} to {new_state}"
                )
            
            # Record state change
            state_change = {
                "from_state": current_state,
                "to_state": new_state,
                "changed_by": user_id,
                "changed_at": datetime.utcnow().isoformat(),
                "comment": comment
            }
            
            state_data["state_history"].append(state_change)
            state_data["current_state"] = new_state
            state_data["updated_at"] = datetime.utcnow().isoformat()
            
            await self.cache.set(f"workflow_state:{workflow_id}", state_data, ttl=86400)
            
            # Trigger state-specific actions
            await self._handle_state_transition(workflow_id, new_state, user_id)
            
            return {
                "workflow_id": workflow_id,
                "previous_state": current_state,
                "new_state": new_state,
                "transitioned_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error transitioning workflow state: {str(e)}")
            raise BusinessLogicError(f"Failed to transition state: {str(e)}")
    
    async def _handle_state_transition(
        self,
        workflow_id: str,
        new_state: str,
        user_id: str
    ):
        """Handle state-specific transition actions"""
        state_handlers = {
            "review": self._handle_review_state,
            "approved": self._handle_approved_state,
            "published": self._handle_published_state,
            "archived": self._handle_archived_state
        }
        
        handler = state_handlers.get(new_state)
        if handler:
            await handler(workflow_id, user_id)
    
    async def _handle_review_state(self, workflow_id: str, user_id: str):
        """Handle transition to review state"""
        # Notify reviewers, create review tasks, etc.
        logger.info(f"Workflow {workflow_id} moved to review state by {user_id}")
    
    async def _handle_approved_state(self, workflow_id: str, user_id: str):
        """Handle transition to approved state"""
        # Notify team, prepare for publication, etc.
        logger.info(f"Workflow {workflow_id} approved by {user_id}")
    
    async def _handle_published_state(self, workflow_id: str, user_id: str):
        """Handle transition to published state"""
        # Publish content, notify stakeholders, etc.
        logger.info(f"Workflow {workflow_id} published by {user_id}")
    
    async def _handle_archived_state(self, workflow_id: str, user_id: str):
        """Handle transition to archived state"""
        # Archive data, clean up resources, etc.
        logger.info(f"Workflow {workflow_id} archived by {user_id}")
