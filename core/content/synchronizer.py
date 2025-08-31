"""Content Synchronizer - Real-Time Content Synchronization Engine
==============================================================

The ContentSynchronizer ensures data consistency across platforms,
manages real-time updates, and handles conflict resolution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from ..data.models.content import Content
from ..data.models.sync_log import SyncLog
from ..events.event_publisher import EventPublisher


class SyncStatus(Enum):
    """Synchronization status enumeration"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"
    SKIPPED = "skipped"


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategy enumeration"""    LATEST_WINS = "latest_wins"
    SOURCE_PRIORITY = "source_priority"
    MANUAL_REVIEW = "manual_review"
    MERGE_CHANGES = "merge_changes"
    PRESERVE_LOCAL = "preserve_local"
    PRESERVE_REMOTE = "preserve_remote"


@dataclass
class SyncTask:
    """Content synchronization task container"""    task_id: str
    content_id: str
    source_platform: str
    target_platforms: List[str]
    sync_type: str  # create, update, delete, metadata
    priority: int = 1
    scheduled_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    status: SyncStatus = SyncStatus.PENDING


@dataclass
class SyncConflict:
    """Content synchronization conflict container"""    conflict_id: str
    content_id: str
    platform_a: str
    platform_b: str
    conflict_type: str
    conflicting_fields: List[str]
    resolution_strategy: ConflictResolutionStrategy
    resolved: bool = False
    created_at: datetime = None


@dataclass
class SyncResult:
    """Content synchronization result container"""    task_id: str
    content_id: str
    success: bool
    platforms_synced: List[str]
    platforms_failed: List[str]
    conflicts_detected: List[SyncConflict]
    sync_time: float
    error_message: Optional[str] = None


class ContentSynchronizer:
    """    Real-Time Content Synchronization Engine
    
    Provides comprehensive content synchronization including:
    - Real-time content sync across multiple platforms
    - Conflict detection and resolution
    - Bidirectional synchronization with platform APIs
    - Metadata consistency maintenance
    - Change tracking and audit logging
    - Batch synchronization operations
    - Platform-specific sync rules and mappings
    """    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = logging.getLogger(__name__)
        
        # Event publisher for sync notifications
        self.event_publisher = EventPublisher()
        
        # Sync state management
        self.active_sync_tasks = {}
        self.sync_queue = asyncio.Queue()
        self.conflict_resolution_queue = asyncio.Queue()
        
        # Platform sync configurations
        self.platform_sync_configs = self._load_platform_sync_configs()
        
        # Conflict resolution strategies
        self.conflict_resolvers = {
            ConflictResolutionStrategy.LATEST_WINS: self._resolve_conflict_latest_wins,
            ConflictResolutionStrategy.SOURCE_PRIORITY: self._resolve_conflict_source_priority,
            ConflictResolutionStrategy.MERGE_CHANGES: self._resolve_conflict_merge_changes,
            ConflictResolutionStrategy.PRESERVE_LOCAL: self._resolve_conflict_preserve_local,
            ConflictResolutionStrategy.PRESERVE_REMOTE: self._resolve_conflict_preserve_remote,
        }
        
        # Start background sync processor
        asyncio.create_task(self._start_sync_processor())

    async def sync_content(
        self,
        content_id: str,
        target_platforms: List[str] = None,
        sync_type: str = "update",
        priority: int = 1,
        force_sync: bool = False
    ) -> Dict[str, Any]:
        """        Synchronize content across platforms
        
        Args:
            content_id: Content identifier
            target_platforms: List of target platforms (None = all configured)
            sync_type: Type of synchronization (create, update, delete, metadata)
            priority: Sync priority (higher = more urgent)
            force_sync: Force sync even if no changes detected
            
        Returns:
            Synchronization result with status and conflicts
        """        sync_start = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting content synchronization for {content_id}")
            
            # Get content data
            content_data = await self._get_content_data(content_id)
            if not content_data:
                return {
                    "success": False,
                    "error": "Content not found",
                    "content_id": content_id
                }
            
            # Determine target platforms
            if not target_platforms:
                target_platforms = await self._get_configured_platforms(content_id)
            
            if not target_platforms:
                return {
                    "success": False,
                    "error": "No target platforms configured",
                    "content_id": content_id
                }
            
            # Check if sync is needed
            if not force_sync and not await self._sync_needed(content_id, target_platforms):
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "No changes detected",
                    "content_id": content_id
                }
            
            # Create sync task
            sync_task = SyncTask(
                task_id=str(uuid.uuid4()),
                content_id=content_id,
                source_platform="local",
                target_platforms=target_platforms,
                sync_type=sync_type,
                priority=priority
            )
            
            # Execute synchronization
            sync_result = await self._execute_sync_task(sync_task)
            
            # Calculate sync time
            sync_time = (datetime.utcnow() - sync_start).total_seconds()
            sync_result.sync_time = sync_time
            
            # Log sync operation
            await self._log_sync_operation(sync_task, sync_result)
            
            # Publish sync event
            await self.event_publisher.publish_event("content.synchronized", {
                "content_id": content_id,
                "platforms": target_platforms,
                "success": sync_result.success,
                "conflicts": len(sync_result.conflicts_detected)
            })
            
            self.logger.info(f"Content synchronization completed for {content_id} in {sync_time:.2f}s")
            
            return {
                "success": sync_result.success,
                "content_id": content_id,
                "sync_result": self._serialize_sync_result(sync_result),
                "sync_time": sync_time
            }
            
        except Exception as e:
            sync_time = (datetime.utcnow() - sync_start).total_seconds()
            error_msg = f"Content synchronization failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id,
                "sync_time": sync_time
            }

    async def sync_from_platform(
        self,
        platform_name: str,
        content_filter: Dict[str, Any] = None,
        conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LATEST_WINS
    ) -> Dict[str, Any]:
        """        Synchronize content from a platform to local storage
        
        Args:
            platform_name: Source platform name
            content_filter: Filter criteria for content selection
            conflict_strategy: Strategy for resolving conflicts
            
        Returns:
            Platform sync result with statistics
        """        try:
            self.logger.info(f"Starting platform synchronization from {platform_name}")
            
            # Get platform sync configuration
            platform_config = self.platform_sync_configs.get(platform_name)
            if not platform_config:
                return {
                    "success": False,
                    "error": f"Platform {platform_name} not configured for sync",
                    "platform": platform_name
                }
            
            # Get content from platform
            platform_content = await self._fetch_platform_content(platform_name, content_filter)
            
            if not platform_content:
                return {
                    "success": True,
                    "platform": platform_name,
                    "items_processed": 0,
                    "message": "No content found on platform"
                }
            
            # Process each content item
            sync_results = []
            conflicts_detected = []
            
            for platform_item in platform_content:
                try:
                    # Check for local content
                    local_content = await self._find_local_content_by_platform_id(
                        platform_name, platform_item.get("platform_id", "")
                    )
                    
                    if local_content:
                        # Check for conflicts
                        conflict = await self._detect_sync_conflict(
                            local_content, platform_item, platform_name
                        )
                        
                        if conflict:
                            conflicts_detected.append(conflict)
                            
                            if conflict_strategy != ConflictResolutionStrategy.MANUAL_REVIEW:
                                # Auto-resolve conflict
                                resolved_content = await self._resolve_sync_conflict(
                                    conflict, conflict_strategy
                                )
                                
                                if resolved_content:
                                    await self._update_local_content(local_content, resolved_content)
                                    sync_results.append({
                                        "content_id": local_content.id,
                                        "action": "updated",
                                        "conflicts_resolved": 1
                                    })
                            else:
                                # Queue for manual review
                                await self.conflict_resolution_queue.put(conflict)
                                sync_results.append({
                                    "content_id": local_content.id,
                                    "action": "queued_for_review",
                                    "conflicts_detected": 1
                                })
                        else:
                            # No conflict, update local content
                            await self._update_local_content_from_platform(
                                local_content, platform_item, platform_name
                            )
                            sync_results.append({
                                "content_id": local_content.id,
                                "action": "updated",
                                "conflicts_resolved": 0
                            })
                    else:
                        # Create new local content
                        new_content = await self._create_local_content_from_platform(
                            platform_item, platform_name
                        )
                        
                        if new_content:
                            sync_results.append({
                                "content_id": new_content.id,
                                "action": "created",
                                "conflicts_resolved": 0
                            })
                
                except Exception as e:
                    self.logger.error(f"Failed to sync platform item: {str(e)}")
                    sync_results.append({
                        "error": str(e),
                        "action": "failed"
                    })
            
            # Calculate statistics
            items_processed = len(platform_content)
            items_created = sum(1 for r in sync_results if r.get("action") == "created")
            items_updated = sum(1 for r in sync_results if r.get("action") == "updated")
            items_failed = sum(1 for r in sync_results if r.get("action") == "failed")
            total_conflicts = len(conflicts_detected)
            
            return {
                "success": True,
                "platform": platform_name,
                "items_processed": items_processed,
                "items_created": items_created,
                "items_updated": items_updated,
                "items_failed": items_failed,
                "conflicts_detected": total_conflicts,
                "sync_results": sync_results
            }
            
        except Exception as e:
            error_msg = f"Platform synchronization failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "platform": platform_name
            }

    async def _execute_sync_task(self, sync_task: SyncTask) -> SyncResult:
        """        Execute a synchronization task
        
        Args:
            sync_task: Synchronization task to execute
            
        Returns:
            Synchronization result
        """        try:
            sync_task.status = SyncStatus.IN_PROGRESS
            self.active_sync_tasks[sync_task.task_id] = sync_task
            
            platforms_synced = []
            platforms_failed = []
            conflicts_detected = []
            
            # Get content data
            content_data = await self._get_content_data(sync_task.content_id)
            
            # Sync to each target platform
            for platform in sync_task.target_platforms:
                try:
                    platform_result = await self._sync_to_platform(
                        content_data, platform, sync_task.sync_type
                    )
                    
                    if platform_result.get("success"):
                        platforms_synced.append(platform)
                        
                        # Check for conflicts
                        if platform_result.get("conflicts"):
                            conflicts_detected.extend(platform_result["conflicts"])
                    else:
                        platforms_failed.append(platform)
                        
                except Exception as e:
                    self.logger.error(f"Failed to sync to platform {platform}: {str(e)}")
                    platforms_failed.append(platform)
            
            # Update sync task status
            if platforms_failed:
                sync_task.status = SyncStatus.FAILED if not platforms_synced else SyncStatus.COMPLETED
            else:
                sync_task.status = SyncStatus.COMPLETED
            
            return SyncResult(
                task_id=sync_task.task_id,
                content_id=sync_task.content_id,
                success=len(platforms_synced) > 0,
                platforms_synced=platforms_synced,
                platforms_failed=platforms_failed,
                conflicts_detected=conflicts_detected,
                sync_time=0.0,
                error_message=f"Failed platforms: {platforms_failed}" if platforms_failed else None
            )
            
        except Exception as e:
            sync_task.status = SyncStatus.FAILED
            raise Exception(f"Sync task execution failed: {str(e)}")
        finally:
            # Remove from active tasks
            self.active_sync_tasks.pop(sync_task.task_id, None)

    async def _sync_to_platform(
        self,
        content_data: Dict[str, Any],
        platform: str,
        sync_type: str
    ) -> Dict[str, Any]:
        """        Synchronize content to a specific platform
        
        Args:
            content_data: Content data to sync
            platform: Target platform
            sync_type: Type of synchronization
            
        Returns:
            Platform sync result
        """        try:
            # Get platform-specific sync configuration
            platform_config = self.platform_sync_configs.get(platform, {})
            
            # Transform content for platform
            platform_content = await self._transform_content_for_platform(
                content_data, platform, platform_config
            )
            
            # Get platform API client
            api_client = await self._get_platform_api_client(platform)
            
            if not api_client:
                return {
                    "success": False,
                    "error": f"Platform API client not available for {platform}"
                }
            
            # Execute platform-specific sync
            if sync_type == "create":
                result = await api_client.create_content(platform_content)
            elif sync_type == "update":
                result = await api_client.update_content(
                    content_data.get("platform_ids", {}).get(platform, ""),
                    platform_content
                )
            elif sync_type == "delete":
                result = await api_client.delete_content(
                    content_data.get("platform_ids", {}).get(platform, "")
                )
            elif sync_type == "metadata":
                result = await api_client.update_metadata(
                    content_data.get("platform_ids", {}).get(platform, ""),
                    platform_content.get("metadata", {})
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported sync type: {sync_type}"
                }
            
            # Update local content with platform response
            if result.get("success") and result.get("platform_id"):
                await self._update_content_platform_id(
                    content_data["id"], platform, result["platform_id"]
                )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Platform sync failed: {str(e)}"
            }

    async def _detect_sync_conflict(
        self,
        local_content: Any,
        platform_content: Dict[str, Any],
        platform: str
    ) -> Optional[SyncConflict]:
        """        Detect synchronization conflicts between local and platform content
        
        Args:
            local_content: Local content record
            platform_content: Platform content data
            platform: Platform name
            
        Returns:
            Conflict object if conflict detected, None otherwise
        """        try:
            conflicting_fields = []
            
            # Check for conflicts in key fields
            conflict_fields = ["title", "description", "tags", "metadata"]
            
            for field in conflict_fields:
                local_value = getattr(local_content, field, None)
                platform_value = platform_content.get(field)
                
                # Normalize values for comparison
                local_normalized = self._normalize_field_value(local_value)
                platform_normalized = self._normalize_field_value(platform_value)
                
                if local_normalized != platform_normalized:
                    conflicting_fields.append(field)
            
            # Check modification timestamps
            local_modified = getattr(local_content, "updated_at", None)
            platform_modified = platform_content.get("updated_at")
            
            if platform_modified:
                platform_modified = datetime.fromisoformat(platform_modified.replace("Z", "+00:00"))
                
                # Only consider it a conflict if both have been modified recently
                # and the modifications are not from sync operations
                if (local_modified and platform_modified and 
                    abs((local_modified - platform_modified).total_seconds()) > 60):  # 1 minute threshold
                    conflicting_fields.append("updated_at")
            
            if not conflicting_fields:
                return None
            
            return SyncConflict(
                conflict_id=str(uuid.uuid4()),
                content_id=local_content.id,
                platform_a="local",
                platform_b=platform,
                conflict_type="field_mismatch",
                conflicting_fields=conflicting_fields,
                resolution_strategy=ConflictResolutionStrategy.LATEST_WINS,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Conflict detection failed: {str(e)}")
            return None

    # Conflict resolution methods

    async def _resolve_conflict_latest_wins(
        self,
        conflict: SyncConflict,
        local_content: Any,
        platform_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by using the latest modification time"""        local_modified = getattr(local_content, "updated_at", datetime.min)
        platform_modified = platform_content.get("updated_at")
        
        if platform_modified:
            platform_modified = datetime.fromisoformat(platform_modified.replace("Z", "+00:00"))
        else:
            platform_modified = datetime.min
        
        # Use the more recently modified version
        if platform_modified > local_modified:
            return platform_content
        else:
            return self._content_to_dict(local_content)

    async def _resolve_conflict_source_priority(
        self,
        conflict: SyncConflict,
        local_content: Any,
        platform_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict based on configured source priority"""        # Local storage has higher priority by default
        return self._content_to_dict(local_content)

    async def _resolve_conflict_merge_changes(
        self,
        conflict: SyncConflict,
        local_content: Any,
        platform_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by merging non-conflicting changes"""        merged_content = self._content_to_dict(local_content)
        
        # Merge fields that don't conflict
        for field, platform_value in platform_content.items():
            if field not in conflict.conflicting_fields:
                merged_content[field] = platform_value
        
        return merged_content

    async def _resolve_conflict_preserve_local(
        self,
        conflict: SyncConflict,
        local_content: Any,
        platform_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by preserving local content"""        return self._content_to_dict(local_content)

    async def _resolve_conflict_preserve_remote(
        self,
        conflict: SyncConflict,
        local_content: Any,
        platform_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by preserving remote/platform content"""        return platform_content

    # Helper methods

    def _load_platform_sync_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific synchronization configurations"""        return {
            "youtube": {
                "field_mappings": {
                    "title": "snippet.title",
                    "description": "snippet.description",
                    "tags": "snippet.tags"
                },
                "sync_frequency": 30,  # minutes
                "conflict_strategy": "latest_wins"
            },
            "instagram": {
                "field_mappings": {
                    "title": "caption",
                    "description": "caption"
                },
                "sync_frequency": 15,
                "conflict_strategy": "source_priority"
            },
            "tiktok": {
                "field_mappings": {
                    "title": "desc",
                    "description": "desc"
                },
                "sync_frequency": 10,
                "conflict_strategy": "latest_wins"
            }
        }

    def _normalize_field_value(self, value: Any) -> str:
        """Normalize field value for comparison"""        if value is None:
            return ""
        elif isinstance(value, (list, dict)):
            return json.dumps(value, sort_keys=True)
        else:
            return str(value).strip().lower()

    def _content_to_dict(self, content: Any) -> Dict[str, Any]:
        """Convert content object to dictionary"""        return {
            "id": content.id,
            "title": content.title,
            "description": content.description,
            "content_type": content.content_type,
            "tags": content.tags,
            "metadata": content.metadata,
            "updated_at": content.updated_at.isoformat() if content.updated_at else None
        }

    async def _start_sync_processor(self):
        """Start background sync task processor"""        while True:
            try:
                # Process sync queue
                if not self.sync_queue.empty():
                    sync_task = await self.sync_queue.get()
                    await self._execute_sync_task(sync_task)
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Sync processor error: {str(e)}")
                await asyncio.sleep(5)

    # Placeholder methods for actual implementations
    async def _get_content_data(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content data from database"""        return None

    async def _get_configured_platforms(self, content_id: str) -> List[str]:
        """Get configured platforms for content"""        return ["youtube", "instagram"]

    async def _sync_needed(self, content_id: str, platforms: List[str]) -> bool:
        """Check if synchronization is needed"""        return True

    async def _log_sync_operation(self, sync_task: SyncTask, sync_result: SyncResult) -> None:
        """Log synchronization operation"""        pass

    def _serialize_sync_result(self, result: SyncResult) -> Dict[str, Any]:
        """Convert sync result to serializable format"""        return {
            "task_id": result.task_id,
            "content_id": result.content_id,
            "success": result.success,
            "platforms_synced": result.platforms_synced,
            "platforms_failed": result.platforms_failed,
            "conflicts_detected": len(result.conflicts_detected),
            "sync_time": result.sync_time,
            "error_message": result.error_message
        }
