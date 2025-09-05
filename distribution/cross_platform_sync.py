#!/usr/bin/env python3
"""Cross-Platform Synchronization Engine

Advanced synchronization system for maintaining content consistency and metadata
alignment across multiple platforms. Handles version control, conflict resolution,
and automated updates for distributed content.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Synchronization status"""
    SYNCHRONIZED = "synchronized"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CONFLICT = "conflict"
    FAILED = "failed"
    PARTIAL = "partial"


class ConflictType(Enum):
    """Types of synchronization conflicts"""
    METADATA_MISMATCH = "metadata_mismatch"
    VERSION_CONFLICT = "version_conflict"
    CONTENT_DIVERGED = "content_diverged"
    PERMISSION_DENIED = "permission_denied"
    PLATFORM_LIMITATION = "platform_limitation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class SyncAction(Enum):
    """Synchronization actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
    MERGE = "merge"
    SKIP = "skip"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    MANUAL = "manual"
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    MERGE_AUTOMATIC = "merge_automatic"
    LATEST_TIMESTAMP = "latest_timestamp"
    HIGHEST_PRIORITY = "highest_priority"


@dataclass
class PlatformContent:
    """Content representation on a specific platform"""
    platform: str
    content_id: str
    platform_specific_id: str
    title: str
    description: str
    metadata: Dict[str, Any]
    tags: List[str]
    url: str
    last_updated: datetime
    version_hash: str
    sync_status: SyncStatus = SyncStatus.SYNCHRONIZED


@dataclass
class SyncRule:
    """Synchronization rule configuration"""
    rule_id: str
    name: str
    source_platform: str
    target_platforms: List[str]
    field_mappings: Dict[str, str]
    sync_frequency: str  # realtime, hourly, daily, manual
    conflict_resolution: ConflictResolution
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    transformations: Dict[str, str] = field(default_factory=dict)


@dataclass
class SyncConflict:
    """Synchronization conflict details"""
    conflict_id: str
    content_id: str
    conflict_type: ConflictType
    source_platform: str
    target_platform: str
    source_value: Any
    target_value: Any
    field_name: str
    detected_at: datetime
    resolved: bool = False
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None


@dataclass
class SyncOperation:
    """Individual synchronization operation"""
    operation_id: str
    content_id: str
    source_platform: str
    target_platform: str
    action: SyncAction
    field_changes: Dict[str, Tuple[Any, Any]]  # field: (old_value, new_value)
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: SyncStatus = SyncStatus.PENDING
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class SyncSession:
    """Synchronization session details"""
    session_id: str
    content_id: str
    initiated_by: str
    platforms_involved: List[str]
    operations: List[SyncOperation]
    conflicts: List[SyncConflict]
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: SyncStatus = SyncStatus.PENDING
    summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VersionInfo:
    """Content version information"""
    version_id: str
    content_id: str
    platform: str
    version_number: int
    changes: Dict[str, Any]
    created_at: datetime
    created_by: str
    checksum: str


class CrossPlatformSync:
    """
    Advanced cross-platform synchronization engine.
    
    Maintains content consistency across multiple platforms with intelligent
    conflict resolution, version control, and automated update propagation.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize cross-platform synchronization engine"""
        self.config = config or {}
        self.sync_rules = {}
        self.content_registry = {}
        self.version_history = {}
        self.active_sessions = {}
        self.conflict_queue = []
        self.sync_schedules = {}
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default synchronization rules"""
        # Universal metadata sync rule
        self.sync_rules["universal_metadata"] = SyncRule(
            rule_id="universal_metadata",
            name="Universal Metadata Synchronization",
            source_platform="master",
            target_platforms=["all"],
            field_mappings={
                "title": "title",
                "description": "description", 
                "tags": "hashtags",
                "category": "genre",
                "creator": "artist"
            },
            sync_frequency="realtime",
            conflict_resolution=ConflictResolution.LATEST_TIMESTAMP
        )

        # Platform-specific rules
        self.sync_rules["social_media_sync"] = SyncRule(
            rule_id="social_media_sync",
            name="Social Media Platforms Sync",
            source_platform="instagram",
            target_platforms=["facebook", "twitter", "tiktok"],
            field_mappings={
                "caption": "description",
                "hashtags": "tags",
                "location": "geo_tag"
            },
            sync_frequency="hourly",
            conflict_resolution=ConflictResolution.SOURCE_WINS
        )

        self.sync_rules["music_platform_sync"] = SyncRule(
            rule_id="music_platform_sync",
            name="Music Platforms Sync",
            source_platform="spotify",
            target_platforms=["soundcloud", "youtube", "bandcamp"],
            field_mappings={
                "track_name": "title",
                "artist": "creator",
                "album": "collection",
                "genre": "category"
            },
            sync_frequency="daily",
            conflict_resolution=ConflictResolution.MERGE_AUTOMATIC
        )

    async def register_content(
        self,
        content_id: str,
        platform_contents: List[PlatformContent]
    ) -> bool:
        """
        Register content across multiple platforms for synchronization
        
        Args:
            content_id: Unique content identifier
            platform_contents: List of platform-specific content representations
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Validate platform contents
            for platform_content in platform_contents:
                if not self._validate_platform_content(platform_content):
                    raise ValueError(f"Invalid platform content for {platform_content.platform}")
            
            # Create content registry entry
            self.content_registry[content_id] = {
                "content_id": content_id,
                "platforms": {pc.platform: pc for pc in platform_contents},
                "master_version": None,
                "last_sync": None,
                "sync_status": SyncStatus.SYNCHRONIZED,
                "registered_at": datetime.now()
            }
            
            # Initialize version history
            self.version_history[content_id] = {}
            for platform_content in platform_contents:
                await self._create_version_entry(platform_content)
            
            # Determine master version
            await self._determine_master_version(content_id)
            
            logger.info(f"Registered content {content_id} across {len(platform_contents)} platforms")
            return True
            
        except Exception as e:
            logger.error(f"Error registering content: {str(e)}")
            return False

    def _validate_platform_content(self, content: PlatformContent) -> bool:
        """Validate platform content structure"""
        required_fields = ["platform", "content_id", "title", "last_updated"]
        return all(hasattr(content, field) and getattr(content, field) is not None for field in required_fields)

    async def _create_version_entry(self, platform_content: PlatformContent):
        """Create version history entry for platform content"""
        content_id = platform_content.content_id
        platform = platform_content.platform
        
        if content_id not in self.version_history:
            self.version_history[content_id] = {}
        
        if platform not in self.version_history[content_id]:
            self.version_history[content_id][platform] = []
        
        version_info = VersionInfo(
            version_id=f"{content_id}_{platform}_{uuid.uuid4().hex[:8]}",
            content_id=content_id,
            platform=platform,
            version_number=len(self.version_history[content_id][platform]) + 1,
            changes={"initial_creation": True},
            created_at=platform_content.last_updated,
            created_by="system",
            checksum=self._calculate_content_checksum(platform_content)
        )
        
        self.version_history[content_id][platform].append(version_info)

    def _calculate_content_checksum(self, content: PlatformContent) -> str:
        """Calculate checksum for content version"""
        content_str = json.dumps({
            "title": content.title,
            "description": content.description,
            "metadata": content.metadata,
            "tags": sorted(content.tags)
        }, sort_keys=True)
        
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def _determine_master_version(self, content_id: str):
        """Determine master version based on platform priority and recency"""
        if content_id not in self.content_registry:
            return
        
        platforms_data = self.content_registry[content_id]["platforms"]
        
        # Platform priority (higher number = higher priority)
        platform_priorities = {
            "spotify": 10,
            "youtube": 9,
            "instagram": 8,
            "soundcloud": 7,
            "facebook": 6,
            "twitter": 5,
            "tiktok": 4,
            "pinterest": 3
        }
        
        # Find master based on priority and recency
        master_platform = None
        master_priority = -1
        master_timestamp = datetime.min
        
        for platform, content in platforms_data.items():
            priority = platform_priorities.get(platform, 1)
            timestamp = content.last_updated
            
            if priority > master_priority or (priority == master_priority and timestamp > master_timestamp):
                master_platform = platform
                master_priority = priority
                master_timestamp = timestamp
        
        if master_platform:
            self.content_registry[content_id]["master_version"] = master_platform
            logger.info(f"Set {master_platform} as master for content {content_id}")

    async def synchronize_content(
        self,
        content_id: str,
        source_platform: Optional[str] = None,
        target_platforms: Optional[List[str]] = None,
        sync_rule_id: Optional[str] = None
    ) -> SyncSession:
        """
        Synchronize content across platforms
        
        Args:
            content_id: Content to synchronize
            source_platform: Source platform (defaults to master)
            target_platforms: Target platforms (defaults to all others)
            sync_rule_id: Specific sync rule to apply
            
        Returns:
            SyncSession: Synchronization session details
        """
        try:
            if content_id not in self.content_registry:
                raise ValueError(f"Content {content_id} not registered")
            
            # Initialize sync session
            session_id = f"sync_{uuid.uuid4().hex[:8]}"
            session = SyncSession(
                session_id=session_id,
                content_id=content_id,
                initiated_by="system",
                platforms_involved=[],
                operations=[],
                conflicts=[],
                started_at=datetime.now()
            )
            
            self.active_sessions[session_id] = session
            
            # Determine source and targets
            content_data = self.content_registry[content_id]
            available_platforms = list(content_data["platforms"].keys())
            
            if not source_platform:
                source_platform = content_data["master_version"]
            
            if not target_platforms:
                target_platforms = [p for p in available_platforms if p != source_platform]
            
            session.platforms_involved = [source_platform] + target_platforms
            
            # Select sync rule
            sync_rule = self._select_sync_rule(source_platform, target_platforms, sync_rule_id)
            
            # Perform synchronization
            source_content = content_data["platforms"][source_platform]
            
            for target_platform in target_platforms:
                if target_platform in content_data["platforms"]:
                    target_content = content_data["platforms"][target_platform]
                    
                    # Detect changes and conflicts
                    operation = await self._create_sync_operation(
                        session_id, source_content, target_content, sync_rule
                    )
                    session.operations.append(operation)
                    
                    # Execute operation
                    await self._execute_sync_operation(operation, sync_rule)
            
            # Process conflicts
            session.conflicts = await self._detect_conflicts(session)
            if session.conflicts:
                await self._resolve_conflicts(session, sync_rule.conflict_resolution)
            
            # Complete session
            session.completed_at = datetime.now()
            session.status = self._determine_session_status(session)
            session.summary = self._generate_session_summary(session)
            
            # Update content registry
            await self._update_content_registry(content_id, session)
            
            logger.info(f"Synchronization session {session_id} completed with status {session.status.value}")
            return session
            
        except Exception as e:
            logger.error(f"Error synchronizing content: {str(e)}")
            if 'session' in locals():
                session.status = SyncStatus.FAILED
                session.completed_at = datetime.now()
            raise

    def _select_sync_rule(
        self,
        source_platform: str,
        target_platforms: List[str],
        rule_id: Optional[str]
    ) -> SyncRule:
        """Select appropriate sync rule"""
        if rule_id and rule_id in self.sync_rules:
            return self.sync_rules[rule_id]
        
        # Find matching rule based on platforms
        for rule in self.sync_rules.values():
            if (rule.source_platform == source_platform or rule.source_platform == "master") and \
               (set(target_platforms).issubset(set(rule.target_platforms)) or "all" in rule.target_platforms):
                return rule
        
        # Return default rule
        return self.sync_rules["universal_metadata"]

    async def _create_sync_operation(
        self,
        session_id: str,
        source_content: PlatformContent,
        target_content: PlatformContent,
        sync_rule: SyncRule
    ) -> SyncOperation:
        """Create synchronization operation for content pair"""
        operation_id = f"op_{uuid.uuid4().hex[:8]}"
        
        # Detect changes
        field_changes = {}
        action = SyncAction.SKIP
        
        for source_field, target_field in sync_rule.field_mappings.items():
            source_value = getattr(source_content, source_field, None)
            target_value = getattr(target_content, target_field, None)
            
            # Apply transformations if configured
            if source_field in sync_rule.transformations:
                source_value = self._apply_transformation(
                    source_value, sync_rule.transformations[source_field]
                )
            
            if source_value != target_value:
                field_changes[target_field] = (target_value, source_value)
                action = SyncAction.UPDATE
        
        operation = SyncOperation(
            operation_id=operation_id,
            content_id=source_content.content_id,
            source_platform=source_content.platform,
            target_platform=target_content.platform,
            action=action,
            field_changes=field_changes,
            started_at=datetime.now()
        )
        
        return operation

    def _apply_transformation(self, value: Any, transformation: str) -> Any:
        """Apply value transformation based on transformation rule"""
        if transformation == "uppercase":
            return str(value).upper() if value else value
        elif transformation == "lowercase":
            return str(value).lower() if value else value
        elif transformation == "truncate_100":
            return str(value)[:100] if value else value
        elif transformation == "hashtag_format":
            if isinstance(value, list):
                return [f"#{tag.lstrip('#')}" for tag in value]
            return value
        else:
            return value

    async def _execute_sync_operation(self, operation: SyncOperation, sync_rule: SyncRule):
        """Execute synchronization operation"""
        try:
            operation.status = SyncStatus.IN_PROGRESS
            
            if operation.action == SyncAction.SKIP:
                operation.status = SyncStatus.SYNCHRONIZED
                operation.completed_at = datetime.now()
                return
            
            # Check conditions
            if not self._check_sync_conditions(operation, sync_rule):
                operation.status = SyncStatus.SYNCHRONIZED
                operation.completed_at = datetime.now()
                return
            
            # Simulate platform API update
            await self._update_platform_content(operation)
            
            # Update local content representation
            await self._update_local_content(operation)
            
            # Create version entry
            await self._create_operation_version(operation)
            
            operation.status = SyncStatus.SYNCHRONIZED
            operation.completed_at = datetime.now()
            
        except Exception as e:
            operation.status = SyncStatus.FAILED
            operation.error_message = str(e)
            operation.completed_at = datetime.now()
            logger.error(f"Operation {operation.operation_id} failed: {str(e)}")

    def _check_sync_conditions(self, operation: SyncOperation, sync_rule: SyncRule) -> bool:
        """Check if sync conditions are met"""
        # Check rule conditions
        for condition_key, condition_value in sync_rule.conditions.items():
            # Implement condition checking logic
            pass
        
        # Check rate limits
        if not self._check_rate_limits(operation.target_platform):
            return False
        
        return True

    def _check_rate_limits(self, platform: str) -> bool:
        """Check if platform rate limits allow synchronization"""
        # Platform-specific rate limits
        rate_limits = {
            "twitter": {"requests_per_hour": 300},
            "instagram": {"requests_per_hour": 200},
            "facebook": {"requests_per_hour": 500},
            "tiktok": {"requests_per_hour": 100}
        }
        
        # Simplified rate limiting check
        return True  # In production, implement proper rate limiting

    async def _update_platform_content(self, operation: SyncOperation):
        """Update content on target platform via API"""
        # Placeholder for platform API calls
        # In production, this would make actual API calls to update content
        
        platform = operation.target_platform
        updates = operation.field_changes
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        logger.info(f"Updated {platform} content with {len(updates)} changes")

    async def _update_local_content(self, operation: SyncOperation):
        """Update local content representation"""
        content_id = operation.content_id
        platform = operation.target_platform
        
        if content_id in self.content_registry and platform in self.content_registry[content_id]["platforms"]:
            content = self.content_registry[content_id]["platforms"][platform]
            
            # Apply changes
            for field, (old_value, new_value) in operation.field_changes.items():
                if hasattr(content, field):
                    setattr(content, field, new_value)
            
            # Update metadata
            content.last_updated = datetime.now()
            content.version_hash = self._calculate_content_checksum(content)

    async def _create_operation_version(self, operation: SyncOperation):
        """Create version entry for sync operation"""
        content_id = operation.content_id
        platform = operation.target_platform
        
        if content_id not in self.version_history:
            self.version_history[content_id] = {}
        
        if platform not in self.version_history[content_id]:
            self.version_history[content_id][platform] = []
        
        version_info = VersionInfo(
            version_id=f"sync_{operation.operation_id}",
            content_id=content_id,
            platform=platform,
            version_number=len(self.version_history[content_id][platform]) + 1,
            changes=operation.field_changes,
            created_at=datetime.now(),
            created_by=f"sync_from_{operation.source_platform}",
            checksum=f"sync_{operation.operation_id}"
        )
        
        self.version_history[content_id][platform].append(version_info)

    async def _detect_conflicts(self, session: SyncSession) -> List[SyncConflict]:
        """Detect synchronization conflicts"""
        conflicts = []
        
        for operation in session.operations:
            if operation.status == SyncStatus.FAILED:
                # Create conflict for failed operations
                conflict = SyncConflict(
                    conflict_id=f"conflict_{uuid.uuid4().hex[:8]}",
                    content_id=operation.content_id,
                    conflict_type=ConflictType.VERSION_CONFLICT,
                    source_platform=operation.source_platform,
                    target_platform=operation.target_platform,
                    source_value=None,
                    target_value=None,
                    field_name="operation_failure",
                    detected_at=datetime.now()
                )
                conflicts.append(conflict)
            
            # Check for concurrent modifications
            conflicts.extend(await self._detect_concurrent_modifications(operation))
        
        return conflicts

    async def _detect_concurrent_modifications(self, operation: SyncOperation) -> List[SyncConflict]:
        """Detect concurrent modifications that could cause conflicts"""
        conflicts = []
        
        # Check if target content was modified during sync
        content_id = operation.content_id
        platform = operation.target_platform
        
        if content_id in self.content_registry and platform in self.content_registry[content_id]["platforms"]:
            content = self.content_registry[content_id]["platforms"][platform]
            
            # If content was modified after operation started, it's a potential conflict
            if content.last_updated > operation.started_at:
                conflict = SyncConflict(
                    conflict_id=f"conflict_{uuid.uuid4().hex[:8]}",
                    content_id=content_id,
                    conflict_type=ConflictType.CONTENT_DIVERGED,
                    source_platform=operation.source_platform,
                    target_platform=platform,
                    source_value="sync_operation",
                    target_value="concurrent_modification",
                    field_name="last_updated",
                    detected_at=datetime.now()
                )
                conflicts.append(conflict)
        
        return conflicts

    async def _resolve_conflicts(self, session: SyncSession, resolution_strategy: ConflictResolution):
        """Resolve synchronization conflicts"""
        for conflict in session.conflicts:
            try:
                if resolution_strategy == ConflictResolution.MANUAL:
                    # Queue for manual resolution
                    self.conflict_queue.append(conflict)
                    continue
                
                elif resolution_strategy == ConflictResolution.SOURCE_WINS:
                    conflict.resolution = "source_platform_values_applied"
                
                elif resolution_strategy == ConflictResolution.TARGET_WINS:
                    conflict.resolution = "target_platform_values_preserved"
                
                elif resolution_strategy == ConflictResolution.LATEST_TIMESTAMP:
                    conflict.resolution = "latest_modification_wins"
                
                elif resolution_strategy == ConflictResolution.MERGE_AUTOMATIC:
                    conflict.resolution = await self._attempt_automatic_merge(conflict)
                
                conflict.resolved = True
                conflict.resolved_at = datetime.now()
                
            except Exception as e:
                logger.error(f"Error resolving conflict {conflict.conflict_id}: {str(e)}")

    async def _attempt_automatic_merge(self, conflict: SyncConflict) -> str:
        """Attempt automatic merge of conflicting values"""
        # Simple merge strategy - concatenate string values, sum numeric values
        source_val = conflict.source_value
        target_val = conflict.target_value
        
        if isinstance(source_val, str) and isinstance(target_val, str):
            return f"merged_strings_{len(source_val + target_val)}_chars"
        elif isinstance(source_val, (int, float)) and isinstance(target_val, (int, float)):
            return f"averaged_values_{(source_val + target_val) / 2}"
        else:
            return "merge_not_possible_manual_review_required"

    def _determine_session_status(self, session: SyncSession) -> SyncStatus:
        """Determine overall status of sync session"""
        if not session.operations:
            return SyncStatus.SYNCHRONIZED
        
        statuses = [op.status for op in session.operations]
        
        if all(s == SyncStatus.SYNCHRONIZED for s in statuses):
            return SyncStatus.SYNCHRONIZED
        elif any(s == SyncStatus.FAILED for s in statuses):
            return SyncStatus.FAILED if session.conflicts else SyncStatus.PARTIAL
        elif any(s == SyncStatus.IN_PROGRESS for s in statuses):
            return SyncStatus.IN_PROGRESS
        else:
            return SyncStatus.PARTIAL

    def _generate_session_summary(self, session: SyncSession) -> Dict[str, Any]:
        """Generate summary of sync session"""
        return {
            "total_operations": len(session.operations),
            "successful_operations": len([op for op in session.operations if op.status == SyncStatus.SYNCHRONIZED]),
            "failed_operations": len([op for op in session.operations if op.status == SyncStatus.FAILED]),
            "conflicts_detected": len(session.conflicts),
            "conflicts_resolved": len([c for c in session.conflicts if c.resolved]),
            "duration_seconds": (session.completed_at - session.started_at).total_seconds() if session.completed_at else 0,
            "platforms_synchronized": len(set(op.target_platform for op in session.operations))
        }

    async def _update_content_registry(self, content_id: str, session: SyncSession):
        """Update content registry after synchronization"""
        if content_id in self.content_registry:
            self.content_registry[content_id]["last_sync"] = session.completed_at
            self.content_registry[content_id]["sync_status"] = session.status

    async def schedule_automatic_sync(
        self,
        content_id: str,
        sync_rule_id: str,
        frequency: str
    ) -> bool:
        """
        Schedule automatic synchronization for content
        
        Args:
            content_id: Content to schedule sync for
            sync_rule_id: Sync rule to apply
            frequency: Sync frequency (hourly, daily, weekly)
            
        Returns:
            bool: True if scheduling successful
        """
        try:
            schedule_id = f"schedule_{content_id}_{uuid.uuid4().hex[:8]}"
            
            self.sync_schedules[schedule_id] = {
                "schedule_id": schedule_id,
                "content_id": content_id,
                "sync_rule_id": sync_rule_id,
                "frequency": frequency,
                "next_sync": self._calculate_next_sync_time(frequency),
                "enabled": True,
                "created_at": datetime.now()
            }
            
            logger.info(f"Scheduled automatic sync for content {content_id} with frequency {frequency}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling automatic sync: {str(e)}")
            return False

    def _calculate_next_sync_time(self, frequency: str) -> datetime:
        """Calculate next synchronization time based on frequency"""
        now = datetime.now()
        
        if frequency == "hourly":
            return now + timedelta(hours=1)
        elif frequency == "daily":
            return now + timedelta(days=1)
        elif frequency == "weekly":
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(hours=1)  # Default to hourly

    async def get_sync_status(self, content_id: str) -> Dict[str, Any]:
        """Get synchronization status for content"""
        if content_id not in self.content_registry:
            return {"error": "Content not registered"}
        
        content_data = self.content_registry[content_id]
        
        platform_statuses = {}
        for platform, content in content_data["platforms"].items():
            platform_statuses[platform] = {
                "status": content.sync_status.value,
                "last_updated": content.last_updated.isoformat(),
                "version_hash": content.version_hash
            }
        
        return {
            "content_id": content_id,
            "overall_status": content_data["sync_status"].value,
            "master_platform": content_data["master_version"],
            "last_sync": content_data["last_sync"].isoformat() if content_data["last_sync"] else None,
            "platform_statuses": platform_statuses,
            "registered_at": content_data["registered_at"].isoformat()
        }

    async def get_version_history(self, content_id: str, platform: Optional[str] = None) -> Dict[str, Any]:
        """Get version history for content"""
        if content_id not in self.version_history:
            return {"error": "No version history found"}
        
        history = self.version_history[content_id]
        
        if platform:
            if platform in history:
                versions = [
                    {
                        "version_id": v.version_id,
                        "version_number": v.version_number,
                        "changes": v.changes,
                        "created_at": v.created_at.isoformat(),
                        "created_by": v.created_by
                    }
                    for v in history[platform]
                ]
                return {"platform": platform, "versions": versions}
            else:
                return {"error": f"No history for platform {platform}"}
        else:
            all_versions = {}
            for plt, versions in history.items():
                all_versions[plt] = [
                    {
                        "version_id": v.version_id,
                        "version_number": v.version_number,
                        "changes": v.changes,
                        "created_at": v.created_at.isoformat(),
                        "created_by": v.created_by
                    }
                    for v in versions
                ]
            return {"content_id": content_id, "version_history": all_versions}

    async def get_pending_conflicts(self) -> List[Dict[str, Any]]:
        """Get list of pending conflicts requiring manual resolution"""
        pending = []
        
        for conflict in self.conflict_queue:
            if not conflict.resolved:
                pending.append({
                    "conflict_id": conflict.conflict_id,
                    "content_id": conflict.content_id,
                    "conflict_type": conflict.conflict_type.value,
                    "source_platform": conflict.source_platform,
                    "target_platform": conflict.target_platform,
                    "field_name": conflict.field_name,
                    "detected_at": conflict.detected_at.isoformat()
                })
        
        return pending

    async def resolve_manual_conflict(
        self,
        conflict_id: str,
        resolution: str,
        chosen_value: Any
    ) -> bool:
        """Manually resolve a pending conflict"""
        try:
            conflict = next((c for c in self.conflict_queue if c.conflict_id == conflict_id), None)
            
            if not conflict:
                return False
            
            conflict.resolution = resolution
            conflict.resolved = True
            conflict.resolved_at = datetime.now()
            
            # Apply resolution to content
            await self._apply_conflict_resolution(conflict, chosen_value)
            
            logger.info(f"Manually resolved conflict {conflict_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving conflict {conflict_id}: {str(e)}")
            return False

    async def _apply_conflict_resolution(self, conflict: SyncConflict, chosen_value: Any):
        """Apply manual conflict resolution to content"""
        content_id = conflict.content_id
        platform = conflict.target_platform
        field = conflict.field_name
        
        if content_id in self.content_registry and platform in self.content_registry[content_id]["platforms"]:
            content = self.content_registry[content_id]["platforms"][platform]
            
            if hasattr(content, field):
                setattr(content, field, chosen_value)
                content.last_updated = datetime.now()
                content.version_hash = self._calculate_content_checksum(content)

    async def create_sync_rule(
        self,
        name: str,
        source_platform: str,
        target_platforms: List[str],
        field_mappings: Dict[str, str],
        sync_frequency: str = "manual",
        conflict_resolution: ConflictResolution = ConflictResolution.MANUAL
    ) -> str:
        """Create custom synchronization rule"""
        rule_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        sync_rule = SyncRule(
            rule_id=rule_id,
            name=name,
            source_platform=source_platform,
            target_platforms=target_platforms,
            field_mappings=field_mappings,
            sync_frequency=sync_frequency,
            conflict_resolution=conflict_resolution
        )
        
        self.sync_rules[rule_id] = sync_rule
        
        logger.info(f"Created custom sync rule {rule_id}: {name}")
        return rule_id

    async def run_scheduled_syncs(self):
        """Run all scheduled synchronizations that are due"""
        now = datetime.now()
        
        for schedule_id, schedule in self.sync_schedules.items():
            if schedule["enabled"] and schedule["next_sync"] <= now:
                try:
                    # Execute sync
                    await self.synchronize_content(
                        schedule["content_id"],
                        sync_rule_id=schedule["sync_rule_id"]
                    )
                    
                    # Update next sync time
                    schedule["next_sync"] = self._calculate_next_sync_time(schedule["frequency"])
                    
                except Exception as e:
                    logger.error(f"Error in scheduled sync {schedule_id}: {str(e)}")

    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get overall synchronization statistics"""
        total_content = len(self.content_registry)
        synchronized_content = len([
            c for c in self.content_registry.values()
            if c["sync_status"] == SyncStatus.SYNCHRONIZED
        ])
        
        active_sessions = len([
            s for s in self.active_sessions.values()
            if s.status == SyncStatus.IN_PROGRESS
        ])
        
        pending_conflicts = len([c for c in self.conflict_queue if not c.resolved])
        
        return {
            "total_registered_content": total_content,
            "synchronized_content": synchronized_content,
            "synchronization_rate": (synchronized_content / total_content * 100) if total_content > 0 else 0,
            "active_sync_sessions": active_sessions,
            "pending_conflicts": pending_conflicts,
            "total_sync_rules": len(self.sync_rules),
            "scheduled_syncs": len(self.sync_schedules)
        }