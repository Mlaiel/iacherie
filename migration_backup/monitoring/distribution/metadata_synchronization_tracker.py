"""
Metadata Synchronization Tracker - Distribution Module
=====================================================

Advanced metadata synchronization tracking system for maintaining consistent
content metadata across all platforms with real-time updates and conflict resolution.

Features:
- Real-time metadata synchronization tracking
- Cross-platform metadata consistency validation
- Conflict detection and resolution
- Version control and change tracking
- Platform-specific metadata adaptation
- Automated metadata enrichment

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Metadata synchronization status"""
    SYNCHRONIZED = "synchronized"
    PENDING = "pending"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    FAILED = "failed"
    OUTDATED = "outdated"

class MetadataField(Enum):
    """Standard metadata fields"""
    TITLE = "title"
    DESCRIPTION = "description"
    TAGS = "tags"
    CATEGORY = "category"
    DURATION = "duration"
    THUMBNAIL = "thumbnail"
    LANGUAGE = "language"
    COPYRIGHT = "copyright"
    CREATION_DATE = "creation_date"
    VISIBILITY = "visibility"
    MONETIZATION = "monetization"
    CUSTOM_FIELDS = "custom_fields"

class ConflictType(Enum):
    """Types of metadata conflicts"""
    VALUE_MISMATCH = "value_mismatch"
    FORMAT_INCOMPATIBLE = "format_incompatible"
    FIELD_MISSING = "field_missing"
    PLATFORM_RESTRICTION = "platform_restriction"
    ENCODING_ISSUE = "encoding_issue"
    SIZE_LIMIT_EXCEEDED = "size_limit_exceeded"

class PlatformType(Enum):
    """Supported platforms"""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    TWITCH = "twitch"

@dataclass
class MetadataEntry:
    """Individual metadata entry"""
    field: MetadataField
    value: Any
    platform: PlatformType
    last_updated: datetime = field(default_factory=datetime.now)
    version: int = 1
    checksum: str = ""
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
            
    def _calculate_checksum(self) -> str:
        """Calculate checksum for metadata value"""
        content = f"{self.field.value}:{self.value}:{self.platform.value}"
        return hashlib.md5(content.encode()).hexdigest()

@dataclass
class MetadataConflict:
    """Metadata synchronization conflict"""
    conflict_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    field: MetadataField = MetadataField.TITLE
    conflict_type: ConflictType = ConflictType.VALUE_MISMATCH
    source_platform: PlatformType = PlatformType.YOUTUBE
    target_platform: PlatformType = PlatformType.SPOTIFY
    source_value: Any = None
    target_value: Any = None
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_strategy: Optional[str] = None
    resolved_at: Optional[datetime] = None

@dataclass
class SyncJob:
    """Metadata synchronization job"""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    source_platform: PlatformType = PlatformType.YOUTUBE
    target_platforms: List[PlatformType] = field(default_factory=list)
    metadata_fields: List[MetadataField] = field(default_factory=list)
    status: SyncStatus = SyncStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    errors: List[str] = field(default_factory=list)
    conflicts_detected: List[str] = field(default_factory=list)

@dataclass
class SyncHistory:
    """Synchronization history record"""
    sync_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    field: MetadataField = MetadataField.TITLE
    platform: PlatformType = PlatformType.YOUTUBE
    old_value: Any = None
    new_value: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    sync_job_id: Optional[str] = None
    change_source: str = "manual"  # manual, automatic, conflict_resolution

class MetadataSynchronizationTracker:
    """Main metadata synchronization tracking system"""
    
    def __init__(self):
        self.metadata_store: Dict[str, Dict[PlatformType, Dict[MetadataField, MetadataEntry]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        self.active_sync_jobs: Dict[str, SyncJob] = {}
        self.sync_history: List[SyncHistory] = []
        self.conflicts: List[MetadataConflict] = []
        self.platform_requirements = self._initialize_platform_requirements()
        self.sync_rules = self._initialize_sync_rules()
        
    def _initialize_platform_requirements(self) -> Dict[PlatformType, Dict[MetadataField, Dict[str, Any]]]:
        """Initialize platform-specific metadata requirements"""
        return {
            PlatformType.YOUTUBE: {
                MetadataField.TITLE: {
                    'max_length': 100,
                    'required': True,
                    'allowed_chars': 'all'
                },
                MetadataField.DESCRIPTION: {
                    'max_length': 5000,
                    'required': False,
                    'supports_html': True
                },
                MetadataField.TAGS: {
                    'max_count': 500,
                    'max_length_per_tag': 100,
                    'required': False
                }
            },
            PlatformType.INSTAGRAM: {
                MetadataField.TITLE: {
                    'max_length': 65,
                    'required': True
                },
                MetadataField.DESCRIPTION: {
                    'max_length': 2200,
                    'required': False,
                    'hashtag_support': True
                }
            },
            PlatformType.TIKTOK: {
                MetadataField.TITLE: {
                    'max_length': 150,
                    'required': True
                },
                MetadataField.DESCRIPTION: {
                    'max_length': 2200,
                    'required': False
                }
            },
            PlatformType.SPOTIFY: {
                MetadataField.TITLE: {
                    'max_length': 100,
                    'required': True
                },
                MetadataField.DESCRIPTION: {
                    'max_length': 1000,
                    'required': False
                }
            }
        }
        
    def _initialize_sync_rules(self) -> Dict[str, Any]:
        """Initialize metadata synchronization rules"""
        return {
            'conflict_resolution': {
                'strategy': 'newest_wins',  # newest_wins, manual_review, platform_priority
                'auto_resolve_types': [ConflictType.ENCODING_ISSUE],
                'manual_review_types': [ConflictType.VALUE_MISMATCH, ConflictType.PLATFORM_RESTRICTION]
            },
            'sync_frequency': {
                'real_time': True,
                'batch_interval_minutes': 15,
                'full_sync_interval_hours': 24
            },
            'field_priorities': {
                MetadataField.TITLE: 1,
                MetadataField.DESCRIPTION: 2,
                MetadataField.TAGS: 3,
                MetadataField.THUMBNAIL: 4
            }
        }
        
    async def update_metadata(self, 
                            content_id: str, 
                            platform: PlatformType,
                            field: MetadataField, 
                            value: Any) -> bool:
        """Update metadata for specific content and platform"""
        try:
            # Create or update metadata entry
            entry = MetadataEntry(
                field=field,
                value=value,
                platform=platform
            )
            
            # Check if this is an update
            existing_entry = self.metadata_store[content_id][platform].get(field)
            if existing_entry:
                entry.version = existing_entry.version + 1
                
                # Record change in history
                history = SyncHistory(
                    content_id=content_id,
                    field=field,
                    platform=platform,
                    old_value=existing_entry.value,
                    new_value=value,
                    change_source="api_update"
                )
                self.sync_history.append(history)
                
            # Store updated metadata
            self.metadata_store[content_id][platform][field] = entry
            
            # Check for conflicts with other platforms
            await self._detect_conflicts(content_id, field)
            
            # Trigger synchronization if enabled
            if self.sync_rules['sync_frequency']['real_time']:
                await self._trigger_sync(content_id, platform, field)
                
            logger.info(f"Metadata updated: {content_id}/{platform.value}/{field.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False
            
    async def _detect_conflicts(self, content_id: str, field: MetadataField):
        """Detect metadata conflicts across platforms"""
        if content_id not in self.metadata_store:
            return
            
        # Get all platform entries for this field
        platform_entries = {}
        for platform, platform_metadata in self.metadata_store[content_id].items():
            if field in platform_metadata:
                platform_entries[platform] = platform_metadata[field]
                
        # Compare entries between platforms
        platforms = list(platform_entries.keys())
        for i in range(len(platforms)):
            for j in range(i + 1, len(platforms)):
                platform1, platform2 = platforms[i], platforms[j]
                entry1, entry2 = platform_entries[platform1], platform_entries[platform2]
                
                # Check for conflicts
                conflict_type = self._identify_conflict_type(entry1, entry2, platform1, platform2)
                if conflict_type:
                    conflict = MetadataConflict(
                        content_id=content_id,
                        field=field,
                        conflict_type=conflict_type,
                        source_platform=platform1,
                        target_platform=platform2,
                        source_value=entry1.value,
                        target_value=entry2.value
                    )
                    self.conflicts.append(conflict)
                    logger.warning(f"Metadata conflict detected: {conflict.conflict_id}")
                    
    def _identify_conflict_type(self, 
                              entry1: MetadataEntry, 
                              entry2: MetadataEntry,
                              platform1: PlatformType, 
                              platform2: PlatformType) -> Optional[ConflictType]:
        """Identify the type of conflict between two metadata entries"""
        # Check if values are different
        if entry1.value != entry2.value:
            # Check if it's a platform restriction issue
            if not self._validate_metadata_for_platform(entry1.value, entry1.field, platform2):
                return ConflictType.PLATFORM_RESTRICTION
            if not self._validate_metadata_for_platform(entry2.value, entry2.field, platform1):
                return ConflictType.PLATFORM_RESTRICTION
                
            # Check for encoding issues
            if isinstance(entry1.value, str) and isinstance(entry2.value, str):
                try:
                    entry1.value.encode('utf-8')
                    entry2.value.encode('utf-8')
                except UnicodeEncodeError:
                    return ConflictType.ENCODING_ISSUE
                    
            # General value mismatch
            return ConflictType.VALUE_MISMATCH
            
        return None
        
    def _validate_metadata_for_platform(self, 
                                       value: Any, 
                                       field: MetadataField, 
                                       platform: PlatformType) -> bool:
        """Validate metadata value against platform requirements"""
        requirements = self.platform_requirements.get(platform, {}).get(field, {})
        
        if not requirements:
            return True  # No specific requirements
            
        # Check string length
        if isinstance(value, str) and 'max_length' in requirements:
            if len(value) > requirements['max_length']:
                return False
                
        # Check list count (for tags)
        if isinstance(value, list) and 'max_count' in requirements:
            if len(value) > requirements['max_count']:
                return False
                
        # Check required fields
        if requirements.get('required', False) and not value:
            return False
            
        return True
        
    async def _trigger_sync(self, content_id: str, source_platform: PlatformType, field: MetadataField):
        """Trigger metadata synchronization"""
        # Get target platforms (all platforms except source)
        all_platforms = list(PlatformType)
        target_platforms = [p for p in all_platforms if p != source_platform]
        
        # Create sync job
        sync_job = SyncJob(
            content_id=content_id,
            source_platform=source_platform,
            target_platforms=target_platforms,
            metadata_fields=[field],
            status=SyncStatus.PENDING
        )
        
        self.active_sync_jobs[sync_job.job_id] = sync_job
        
        # Execute synchronization
        await self._execute_sync_job(sync_job)
        
    async def _execute_sync_job(self, job: SyncJob):
        """Execute metadata synchronization job"""
        job.status = SyncStatus.SYNCING
        job.started_at = datetime.now()
        
        try:
            total_operations = len(job.target_platforms) * len(job.metadata_fields)
            completed_operations = 0
            
            # Get source metadata
            source_metadata = self.metadata_store[job.content_id].get(job.source_platform, {})
            
            for target_platform in job.target_platforms:
                for field in job.metadata_fields:
                    if field not in source_metadata:
                        continue
                        
                    source_entry = source_metadata[field]
                    
                    # Adapt metadata for target platform
                    adapted_value = await self._adapt_metadata_for_platform(
                        source_entry.value, field, target_platform
                    )
                    
                    if adapted_value is not None:
                        # Update target platform metadata
                        await self.update_metadata(job.content_id, target_platform, field, adapted_value)
                        
                    completed_operations += 1
                    job.progress_percentage = (completed_operations / total_operations) * 100
                    
            job.status = SyncStatus.SYNCHRONIZED
            job.completed_at = datetime.now()
            
            logger.info(f"Sync job completed: {job.job_id}")
            
        except Exception as e:
            job.status = SyncStatus.FAILED
            job.errors.append(str(e))
            logger.error(f"Sync job failed: {job.job_id} - {e}")
            
    async def _adapt_metadata_for_platform(self, 
                                         value: Any, 
                                         field: MetadataField, 
                                         platform: PlatformType) -> Optional[Any]:
        """Adapt metadata value for specific platform requirements"""
        requirements = self.platform_requirements.get(platform, {}).get(field, {})
        
        if not requirements:
            return value
            
        adapted_value = value
        
        # Truncate strings if too long
        if isinstance(value, str) and 'max_length' in requirements:
            max_length = requirements['max_length']
            if len(value) > max_length:
                adapted_value = value[:max_length-3] + "..."
                
        # Truncate lists if too many items
        if isinstance(value, list) and 'max_count' in requirements:
            max_count = requirements['max_count']
            if len(value) > max_count:
                adapted_value = value[:max_count]
                
        # Handle encoding issues
        if isinstance(adapted_value, str):
            try:
                adapted_value.encode('utf-8')
            except UnicodeEncodeError:
                # Remove problematic characters
                adapted_value = adapted_value.encode('utf-8', errors='ignore').decode('utf-8')
                
        return adapted_value
        
    async def resolve_conflict(self, conflict_id: str, resolution_strategy: str, resolved_value: Any = None) -> bool:
        """Resolve metadata conflict"""
        conflict = None
        for c in self.conflicts:
            if c.conflict_id == conflict_id:
                conflict = c
                break
                
        if not conflict or conflict.resolved:
            return False
            
        try:
            if resolution_strategy == "use_source":
                final_value = conflict.source_value
            elif resolution_strategy == "use_target":
                final_value = conflict.target_value
            elif resolution_strategy == "use_custom":
                final_value = resolved_value
            elif resolution_strategy == "newest_wins":
                # Compare timestamps and use newest
                source_entry = self.metadata_store[conflict.content_id][conflict.source_platform].get(conflict.field)
                target_entry = self.metadata_store[conflict.content_id][conflict.target_platform].get(conflict.field)
                
                if source_entry and target_entry:
                    final_value = source_entry.value if source_entry.last_updated > target_entry.last_updated else target_entry.value
                else:
                    final_value = conflict.source_value
            else:
                return False
                
            # Apply resolution to both platforms
            await self.update_metadata(conflict.content_id, conflict.source_platform, conflict.field, final_value)
            await self.update_metadata(conflict.content_id, conflict.target_platform, conflict.field, final_value)
            
            # Mark conflict as resolved
            conflict.resolved = True
            conflict.resolution_strategy = resolution_strategy
            conflict.resolved_at = datetime.now()
            
            logger.info(f"Conflict resolved: {conflict_id} using {resolution_strategy}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict_id}: {e}")
            return False
            
    def get_metadata_status(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive metadata status for content"""
        if content_id not in self.metadata_store:
            return {'error': 'Content not found'}
            
        content_metadata = self.metadata_store[content_id]
        
        # Calculate sync status for each field
        field_status = {}
        all_fields = set()
        
        # Collect all fields across platforms
        for platform_metadata in content_metadata.values():
            all_fields.update(platform_metadata.keys())
            
        for field in all_fields:
            field_platforms = []
            field_values = []
            
            for platform, platform_metadata in content_metadata.items():
                if field in platform_metadata:
                    field_platforms.append(platform.value)
                    field_values.append(platform_metadata[field].value)
                    
            # Check if all values are the same
            unique_values = set(str(v) for v in field_values)
            sync_status = SyncStatus.SYNCHRONIZED if len(unique_values) <= 1 else SyncStatus.CONFLICT
            
            field_status[field.value] = {
                'sync_status': sync_status.value,
                'platforms': field_platforms,
                'unique_values': len(unique_values),
                'last_updated': max(
                    entry.last_updated for platform_metadata in content_metadata.values()
                    for entry in platform_metadata.values() if entry.field == field
                ).isoformat() if field_platforms else None
            }
            
        # Count conflicts
        content_conflicts = [c for c in self.conflicts if c.content_id == content_id and not c.resolved]
        
        return {
            'content_id': content_id,
            'platforms_count': len(content_metadata),
            'fields_count': len(all_fields),
            'field_status': field_status,
            'active_conflicts': len(content_conflicts),
            'overall_sync_status': SyncStatus.SYNCHRONIZED.value if not content_conflicts else SyncStatus.CONFLICT.value
        }
        
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get comprehensive synchronization statistics"""
        total_content = len(self.metadata_store)
        total_conflicts = len(self.conflicts)
        resolved_conflicts = len([c for c in self.conflicts if c.resolved])
        active_jobs = len(self.active_sync_jobs)
        
        # Calculate platform coverage
        platform_coverage = defaultdict(int)
        for content_metadata in self.metadata_store.values():
            for platform in content_metadata.keys():
                platform_coverage[platform.value] += 1
                
        # Field usage statistics
        field_usage = defaultdict(int)
        for content_metadata in self.metadata_store.values():
            for platform_metadata in content_metadata.values():
                for field in platform_metadata.keys():
                    field_usage[field.value] += 1
                    
        # Recent sync activity
        recent_syncs = len([h for h in self.sync_history 
                          if h.timestamp > datetime.now() - timedelta(hours=24)])
        
        return {
            'total_content': total_content,
            'total_conflicts': total_conflicts,
            'resolved_conflicts': resolved_conflicts,
            'conflict_resolution_rate': resolved_conflicts / total_conflicts if total_conflicts > 0 else 1.0,
            'active_sync_jobs': active_jobs,
            'platform_coverage': dict(platform_coverage),
            'field_usage': dict(field_usage),
            'recent_sync_activity_24h': recent_syncs,
            'sync_history_count': len(self.sync_history)
        }
        
    async def perform_full_sync(self, content_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform full metadata synchronization"""
        content_ids = [content_id] if content_id else list(self.metadata_store.keys())
        
        sync_results = {
            'total_content': len(content_ids),
            'successful_syncs': 0,
            'failed_syncs': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0
        }
        
        for cid in content_ids:
            try:
                # Sync all fields for all platforms
                content_metadata = self.metadata_store[cid]
                
                for source_platform in content_metadata.keys():
                    for field in content_metadata[source_platform].keys():
                        await self._trigger_sync(cid, source_platform, field)
                        
                sync_results['successful_syncs'] += 1
                
            except Exception as e:
                sync_results['failed_syncs'] += 1
                logger.error(f"Full sync failed for {cid}: {e}")
                
        # Auto-resolve conflicts where possible
        auto_resolved = 0
        for conflict in self.conflicts:
            if not conflict.resolved and conflict.conflict_type in self.sync_rules['conflict_resolution']['auto_resolve_types']:
                if await self.resolve_conflict(conflict.conflict_id, "newest_wins"):
                    auto_resolved += 1
                    
        sync_results['conflicts_resolved'] = auto_resolved
        
        logger.info(f"Full sync completed: {sync_results}")
        return sync_results

# Export main classes
__all__ = [
    'MetadataSynchronizationTracker',
    'MetadataEntry',
    'MetadataConflict', 
    'SyncJob',
    'SyncHistory',
    'SyncStatus',
    'MetadataField',
    'ConflictType',
    'PlatformType'
]