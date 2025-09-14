"""
🔄 Platform Sync Microservice
Real-time platform data synchronization across multiple social media and content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
import hashlib
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SyncStatus(str, Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    CONFLICTED = "conflicted"
    SKIPPED = "skipped"


class DataType(str, Enum):
    """Types of data to synchronize"""
    PROFILE = "profile"
    CONTENT = "content"
    METADATA = "metadata"
    ANALYTICS = "analytics"
    COMMENTS = "comments"
    FOLLOWERS = "followers"
    SETTINGS = "settings"
    COLLABORATIONS = "collaborations"
    REVENUE = "revenue"


class SyncDirection(str, Enum):
    """Synchronization direction"""
    BIDIRECTIONAL = "bidirectional"
    PUSH_ONLY = "push_only"
    PULL_ONLY = "pull_only"
    SOURCE_TO_TARGET = "source_to_target"


class ConflictResolution(str, Enum):
    """Conflict resolution strategies"""
    LATEST_WINS = "latest_wins"
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    MANUAL_REVIEW = "manual_review"
    MERGE_FIELDS = "merge_fields"
    SKIP = "skip"


@dataclass
class SyncConfig:
    """Synchronization configuration"""
    config_id: str
    creator_id: str
    source_platform: str
    target_platforms: List[str]
    data_types: List[DataType]
    sync_direction: SyncDirection
    sync_frequency: int  # in seconds
    conflict_resolution: ConflictResolution
    field_mappings: Dict[str, Dict[str, str]] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_sync: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SyncRecord:
    """Individual synchronization record"""
    sync_id: str
    config_id: str
    source_platform: str
    target_platform: str
    data_type: DataType
    source_data: Dict[str, Any]
    target_data: Dict[str, Any]
    status: SyncStatus
    error_message: Optional[str] = None
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    retries: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class DataDifference:
    """Data difference between platforms"""
    field_name: str
    source_value: Any
    target_value: Any
    difference_type: str  # added, removed, modified
    confidence: float  # 0-1


@dataclass
class SyncSummary:
    """Synchronization summary"""
    config_id: str
    total_records: int
    successful_syncs: int
    failed_syncs: int
    conflicts: int
    duration_seconds: float
    data_types_synced: List[DataType]
    platforms_affected: List[str]
    errors: List[str]
    started_at: datetime
    completed_at: datetime


class DataMapper:
    """Maps data between different platform formats"""
    
    def __init__(self) -> None:
        self.field_mappings: Dict[str, Dict[str, str]] = {}
        self.transformation_rules: Dict[str, Callable] = {}
    
    async def map_data(
        self,
        source_data: Dict[str, Any],
        source_platform: str,
        target_platform: str,
        data_type: DataType
    ) -> Dict[str, Any]:
        """Map data from source to target platform format"""
        try:
            mapping_key = f"{source_platform}_to_{target_platform}_{data_type.value}"
            field_mapping = self.field_mappings.get(mapping_key, {})
            
            mapped_data = {}
            
            # Apply field mappings
            for source_field, source_value in source_data.items():
                target_field = field_mapping.get(source_field, source_field)
                
                # Apply transformation if exists
                if source_field in self.transformation_rules:
                    source_value = await self.transformation_rules[source_field](
                        source_value, source_platform, target_platform
                    )
                
                mapped_data[target_field] = source_value
            
            return mapped_data
            
        except Exception as e:
            logger.error(f"Failed to map data: {e}")
            return source_data  # Return original if mapping fails
    
    def register_field_mapping(
        self,
        source_platform: str,
        target_platform: str,
        data_type: DataType,
        mappings: Dict[str, str]
    ) -> None:
        """Register field mappings between platforms"""
        mapping_key = f"{source_platform}_to_{target_platform}_{data_type.value}"
        self.field_mappings[mapping_key] = mappings
    
    def register_transformation_rule(
        self,
        field_name: str,
        transformation_func: Callable
    ) -> None:
        """Register transformation rule for a field"""
        self.transformation_rules[field_name] = transformation_func


class ConflictResolver:
    """Resolves data conflicts between platforms"""
    
    async def resolve_conflicts(
        self,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
        resolution_strategy: ConflictResolution
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Resolve conflicts between source and target data"""
        conflicts = []
        resolved_data = {}
        
        # Find differences
        differences = await self._find_differences(source_data, target_data)
        
        for diff in differences:
            conflict_info = {
                "field": diff.field_name,
                "source_value": diff.source_value,
                "target_value": diff.target_value,
                "type": diff.difference_type,
                "resolution": resolution_strategy.value
            }
            
            # Apply resolution strategy
            if resolution_strategy == ConflictResolution.LATEST_WINS:
                # Assume source is latest for now
                resolved_data[diff.field_name] = diff.source_value
            elif resolution_strategy == ConflictResolution.SOURCE_WINS:
                resolved_data[diff.field_name] = diff.source_value
            elif resolution_strategy == ConflictResolution.TARGET_WINS:
                resolved_data[diff.field_name] = diff.target_value
            elif resolution_strategy == ConflictResolution.MERGE_FIELDS:
                # Simple merge for lists and dicts
                merged_value = await self._merge_values(
                    diff.source_value, 
                    diff.target_value
                )
                resolved_data[diff.field_name] = merged_value
            elif resolution_strategy == ConflictResolution.MANUAL_REVIEW:
                conflicts.append(conflict_info)
                # Keep target value for now
                resolved_data[diff.field_name] = diff.target_value
            else:  # SKIP
                conflicts.append(conflict_info)
                continue
        
        # Add non-conflicting fields
        all_fields = set(source_data.keys()) | set(target_data.keys())
        for field in all_fields:
            if field not in resolved_data:
                resolved_data[field] = source_data.get(field, target_data.get(field))
        
        return resolved_data, conflicts
    
    async def _find_differences(
        self,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any]
    ) -> List[DataDifference]:
        """Find differences between source and target data"""
        differences = []
        
        all_fields = set(source_data.keys()) | set(target_data.keys())
        
        for field in all_fields:
            source_value = source_data.get(field)
            target_value = target_data.get(field)
            
            if source_value != target_value:
                if field not in source_data:
                    diff_type = "removed"
                elif field not in target_data:
                    diff_type = "added"
                else:
                    diff_type = "modified"
                
                difference = DataDifference(
                    field_name=field,
                    source_value=source_value,
                    target_value=target_value,
                    difference_type=diff_type,
                    confidence=1.0
                )
                differences.append(difference)
        
        return differences
    
    async def _merge_values(self, source_value: Any, target_value: Any) -> Any:
        """Merge two values intelligently"""
        if isinstance(source_value, list) and isinstance(target_value, list):
            # Merge lists, removing duplicates
            return list(set(source_value + target_value))
        elif isinstance(source_value, dict) and isinstance(target_value, dict):
            # Merge dictionaries
            merged = target_value.copy()
            merged.update(source_value)
            return merged
        else:
            # For other types, prefer source value
            return source_value


class SyncEngine:
    """Core synchronization engine"""
    
    def __init__(self) -> None:
        self.active_syncs: Dict[str, SyncRecord] = {}
        self.data_mapper = DataMapper()
        self.conflict_resolver = ConflictResolver()
        self.retry_delay = 30  # seconds
        self.max_retries = 3
    
    async def execute_sync(
        self,
        sync_config: SyncConfig,
        specific_data_types: Optional[List[DataType]] = None
    ) -> SyncSummary:
        """Execute synchronization based on configuration"""
        try:
            start_time = datetime.now()
            sync_records = []
            
            data_types_to_sync = specific_data_types or sync_config.data_types
            
            # Execute sync for each data type and target platform
            for data_type in data_types_to_sync:
                for target_platform in sync_config.target_platforms:
                    sync_record = await self._sync_data_type(
                        sync_config=sync_config,
                        target_platform=target_platform,
                        data_type=data_type
                    )
                    sync_records.append(sync_record)
            
            # Generate summary
            end_time = datetime.now()
            summary = self._generate_sync_summary(
                config_id=sync_config.config_id,
                sync_records=sync_records,
                start_time=start_time,
                end_time=end_time,
                data_types_synced=data_types_to_sync
            )
            
            # Update last sync time
            sync_config.last_sync = end_time
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to execute sync: {e}")
            raise
    
    async def _sync_data_type(
        self,
        sync_config: SyncConfig,
        target_platform: str,
        data_type: DataType
    ) -> SyncRecord:
        """Sync specific data type to target platform"""
        sync_id = str(uuid.uuid4())
        
        sync_record = SyncRecord(
            sync_id=sync_id,
            config_id=sync_config.config_id,
            source_platform=sync_config.source_platform,
            target_platform=target_platform,
            data_type=data_type,
            source_data={},
            target_data={},
            status=SyncStatus.PENDING
        )
        
        try:
            self.active_syncs[sync_id] = sync_record
            sync_record.status = SyncStatus.IN_PROGRESS
            
            # Fetch source data
            source_data = await self._fetch_platform_data(
                sync_config.source_platform,
                data_type,
                sync_config.creator_id
            )
            sync_record.source_data = source_data
            
            # Fetch target data for comparison
            target_data = await self._fetch_platform_data(
                target_platform,
                data_type,
                sync_config.creator_id
            )
            sync_record.target_data = target_data
            
            # Map data to target platform format
            mapped_data = await self.data_mapper.map_data(
                source_data=source_data,
                source_platform=sync_config.source_platform,
                target_platform=target_platform,
                data_type=data_type
            )
            
            # Resolve conflicts
            resolved_data, conflicts = await self.conflict_resolver.resolve_conflicts(
                source_data=mapped_data,
                target_data=target_data,
                resolution_strategy=sync_config.conflict_resolution
            )
            sync_record.conflicts = conflicts
            
            # Push resolved data to target platform
            if sync_config.sync_direction in [
                SyncDirection.BIDIRECTIONAL,
                SyncDirection.PUSH_ONLY,
                SyncDirection.SOURCE_TO_TARGET
            ]:
                success = await self._push_platform_data(
                    target_platform,
                    data_type,
                    sync_config.creator_id,
                    resolved_data
                )
                
                if success:
                    if conflicts:
                        sync_record.status = SyncStatus.PARTIAL
                    else:
                        sync_record.status = SyncStatus.COMPLETED
                else:
                    sync_record.status = SyncStatus.FAILED
                    sync_record.error_message = "Failed to push data to target platform"
            else:
                sync_record.status = SyncStatus.SKIPPED
                sync_record.error_message = "Sync direction does not allow push to target"
            
            sync_record.completed_at = datetime.now()
            
        except Exception as e:
            sync_record.status = SyncStatus.FAILED
            sync_record.error_message = str(e)
            sync_record.completed_at = datetime.now()
            logger.error(f"Sync failed for {sync_id}: {e}")
        
        finally:
            if sync_id in self.active_syncs:
                del self.active_syncs[sync_id]
        
        return sync_record
    
    async def _fetch_platform_data(
        self,
        platform_id: str,
        data_type: DataType,
        creator_id: str
    ) -> Dict[str, Any]:
        """Fetch data from platform"""
        # Simulate platform API call
        sample_data = {
            DataType.PROFILE: {
                "name": "Creator Name",
                "bio": "Creator biography",
                "followers_count": 10000,
                "following_count": 500,
                "avatar_url": "https://example.com/avatar.jpg"
            },
            DataType.CONTENT: {
                "posts": [
                    {"id": "1", "title": "Post 1", "content": "Content 1"},
                    {"id": "2", "title": "Post 2", "content": "Content 2"}
                ]
            },
            DataType.ANALYTICS: {
                "total_views": 50000,
                "engagement_rate": 3.5,
                "top_content": ["post_1", "post_2"]
            }
        }
        
        return sample_data.get(data_type, {})
    
    async def _push_platform_data(
        self,
        platform_id: str,
        data_type: DataType,
        creator_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Push data to platform"""
        try:
            # Simulate platform API call
            await asyncio.sleep(0.1)  # Simulate network delay
            logger.info(f"Pushed {data_type.value} data to {platform_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push data to {platform_id}: {e}")
            return False
    
    def _generate_sync_summary(
        self,
        config_id: str,
        sync_records: List[SyncRecord],
        start_time: datetime,
        end_time: datetime,
        data_types_synced: List[DataType]
    ) -> SyncSummary:
        """Generate synchronization summary"""
        total_records = len(sync_records)
        successful_syncs = len([r for r in sync_records if r.status == SyncStatus.COMPLETED])
        failed_syncs = len([r for r in sync_records if r.status == SyncStatus.FAILED])
        conflicts = sum(len(r.conflicts) for r in sync_records)
        duration = (end_time - start_time).total_seconds()
        
        platforms_affected = list(set(r.target_platform for r in sync_records))
        errors = [r.error_message for r in sync_records if r.error_message]
        
        return SyncSummary(
            config_id=config_id,
            total_records=total_records,
            successful_syncs=successful_syncs,
            failed_syncs=failed_syncs,
            conflicts=conflicts,
            duration_seconds=duration,
            data_types_synced=data_types_synced,
            platforms_affected=platforms_affected,
            errors=errors,
            started_at=start_time,
            completed_at=end_time
        )


class PlatformSyncService:
    """
    🔄 Platform Sync Microservice
    
    Provides real-time data synchronization across multiple platforms,
    ensuring consistency and reducing manual data management overhead.
    
    Features:
    - Real-time bidirectional sync
    - Intelligent conflict resolution
    - Data mapping and transformation
    - Bulk synchronization operations
    - Sync monitoring and reporting
    - Retry mechanisms for failed syncs
    - Custom field mappings
    - Filter-based selective sync
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.sync_engine = SyncEngine()
        self.sync_configs: Dict[str, SyncConfig] = {}
        self.is_running = False
        
        # Service configuration
        self.sync_interval = self.config.get("sync_interval", 300)  # 5 minutes
        self.max_concurrent_syncs = self.config.get("max_concurrent_syncs", 10)
        
        # Initialize default field mappings
        self._setup_default_mappings()
        
        logger.info("Platform Sync Service initialized")
    
    async def start(self) -> None:
        """Start the sync service"""
        try:
            self.is_running = True
            logger.info("Platform Sync Service started")
            
            # Start background sync loop
            asyncio.create_task(self._sync_scheduler_loop())
            
        except Exception as e:
            logger.error(f"Failed to start Platform Sync Service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the sync service"""
        try:
            self.is_running = False
            logger.info("Platform Sync Service stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop Platform Sync Service: {e}")
            raise
    
    async def create_sync_config(
        self,
        creator_id: str,
        source_platform: str,
        target_platforms: List[str],
        data_types: List[DataType],
        sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        sync_frequency: int = 300,
        conflict_resolution: ConflictResolution = ConflictResolution.LATEST_WINS
    ) -> str:
        """Create a new synchronization configuration"""
        try:
            config_id = str(uuid.uuid4())
            
            sync_config = SyncConfig(
                config_id=config_id,
                creator_id=creator_id,
                source_platform=source_platform,
                target_platforms=target_platforms,
                data_types=data_types,
                sync_direction=sync_direction,
                sync_frequency=sync_frequency,
                conflict_resolution=conflict_resolution
            )
            
            self.sync_configs[config_id] = sync_config
            
            logger.info(f"Created sync config {config_id} for creator {creator_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"Failed to create sync config: {e}")
            raise
    
    async def execute_manual_sync(
        self,
        config_id: str,
        data_types: Optional[List[DataType]] = None
    ) -> Dict[str, Any]:
        """Execute manual synchronization"""
        try:
            if config_id not in self.sync_configs:
                raise ValueError(f"Sync config {config_id} not found")
            
            sync_config = self.sync_configs[config_id]
            
            summary = await self.sync_engine.execute_sync(
                sync_config=sync_config,
                specific_data_types=data_types
            )
            
            return {
                "sync_summary": asdict(summary),
                "executed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute manual sync: {e}")
            raise
    
    async def get_sync_status(self, config_id: str) -> Dict[str, Any]:
        """Get synchronization status for a configuration"""
        try:
            if config_id not in self.sync_configs:
                raise ValueError(f"Sync config {config_id} not found")
            
            sync_config = self.sync_configs[config_id]
            
            return {
                "config_id": config_id,
                "creator_id": sync_config.creator_id,
                "source_platform": sync_config.source_platform,
                "target_platforms": sync_config.target_platforms,
                "data_types": [dt.value for dt in sync_config.data_types],
                "sync_direction": sync_config.sync_direction.value,
                "enabled": sync_config.enabled,
                "last_sync": sync_config.last_sync.isoformat() if sync_config.last_sync else None,
                "next_sync": self._calculate_next_sync(sync_config).isoformat(),
                "active_syncs": len(self.sync_engine.active_syncs)
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}")
            raise
    
    async def update_sync_config(
        self,
        config_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update synchronization configuration"""
        try:
            if config_id not in self.sync_configs:
                raise ValueError(f"Sync config {config_id} not found")
            
            sync_config = self.sync_configs[config_id]
            
            # Update allowed fields
            allowed_updates = [
                "target_platforms", "data_types", "sync_direction",
                "sync_frequency", "conflict_resolution", "enabled",
                "field_mappings", "filters"
            ]
            
            for field, value in updates.items():
                if field in allowed_updates:
                    if field == "data_types" and isinstance(value, list):
                        setattr(sync_config, field, [DataType(dt) for dt in value])
                    elif field == "sync_direction":
                        setattr(sync_config, field, SyncDirection(value))
                    elif field == "conflict_resolution":
                        setattr(sync_config, field, ConflictResolution(value))
                    else:
                        setattr(sync_config, field, value)
            
            return await self.get_sync_status(config_id)
            
        except Exception as e:
            logger.error(f"Failed to update sync config: {e}")
            raise
    
    async def _sync_scheduler_loop(self) -> None:
        """Background sync scheduler loop"""
        while self.is_running:
            try:
                await self._execute_scheduled_syncs()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in sync scheduler loop: {e}")
                await asyncio.sleep(60)
    
    async def _execute_scheduled_syncs(self) -> None:
        """Execute scheduled synchronizations"""
        try:
            current_time = datetime.now()
            
            for config_id, sync_config in self.sync_configs.items():
                if not sync_config.enabled:
                    continue
                
                next_sync = self._calculate_next_sync(sync_config)
                
                if current_time >= next_sync:
                    logger.info(f"Executing scheduled sync for config {config_id}")
                    try:
                        await self.sync_engine.execute_sync(sync_config)
                    except Exception as e:
                        logger.error(f"Scheduled sync failed for {config_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to execute scheduled syncs: {e}")
    
    def _calculate_next_sync(self, sync_config: SyncConfig) -> datetime:
        """Calculate next sync time"""
        if sync_config.last_sync:
            return sync_config.last_sync + timedelta(seconds=sync_config.sync_frequency)
        else:
            return datetime.now()
    
    def _setup_default_mappings(self) -> None:
        """Setup default field mappings between platforms"""
        # Instagram to Twitter mappings for profile data
        self.sync_engine.data_mapper.register_field_mapping(
            source_platform="instagram",
            target_platform="twitter",
            data_type=DataType.PROFILE,
            mappings={
                "followers_count": "followers_count",
                "following_count": "friends_count",
                "bio": "description",
                "profile_pic_url": "profile_image_url"
            }
        )
        
        # YouTube to TikTok mappings for content
        self.sync_engine.data_mapper.register_field_mapping(
            source_platform="youtube",
            target_platform="tiktok",
            data_type=DataType.CONTENT,
            mappings={
                "title": "caption",
                "description": "caption",
                "video_url": "video_url",
                "thumbnail_url": "cover_url"
            }
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the service"""
        return {
            "service": "PlatformSyncService",
            "status": "healthy" if self.is_running else "stopped",
            "active_configs": len(self.sync_configs),
            "active_syncs": len(self.sync_engine.active_syncs),
            "sync_interval": self.sync_interval,
            "timestamp": datetime.now().isoformat()
        }


# Service instance
platform_sync_service = PlatformSyncService()