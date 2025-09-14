"""
Cross Platform Sync module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Cross Platform Sync Engine

Advanced synchronization system for content metadata, versions, and updates
across multiple distribution platforms. Handles conflict resolution, version
control, and automated propagation of changes with intelligent sync strategies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Synchronization status"""
    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"
    PENDING = "pending"


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    MANUAL = "manual"
    LATEST_WINS = "latest_wins"
    PLATFORM_PRIORITY = "platform_priority"
    MERGE_CHANGES = "merge_changes"
    BACKUP_AND_OVERWRITE = "backup_and_overwrite"


class SyncDirection(Enum):
    """Synchronization direction"""
    BIDIRECTIONAL = "bidirectional"
    SOURCE_TO_TARGETS = "source_to_targets"
    TARGETS_TO_SOURCE = "targets_to_source"
    PEER_TO_PEER = "peer_to_peer"


class ChangeType(Enum):
    """Types of content changes"""
    METADATA_UPDATE = "metadata_update"
    CONTENT_MODIFICATION = "content_modification"
    TITLE_CHANGE = "title_change"
    DESCRIPTION_CHANGE = "description_change"
    TAGS_UPDATE = "tags_update"
    THUMBNAIL_CHANGE = "thumbnail_change"
    PRIVACY_CHANGE = "privacy_change"
    MONETIZATION_CHANGE = "monetization_change"


@dataclass
class ContentVersion:
    """Content version tracking"""
    version_id: str
    content_id: str
    platform: str
    version_number: int
    timestamp: datetime
    checksum: str
    metadata: Dict[str, Any]
    changes: List[str]
    author: str
    commit_message: str


@dataclass
class SyncConflict:
    """Synchronization conflict data"""
    conflict_id: str
    content_id: str
    platforms_involved: List[str]
    conflict_type: str
    detected_at: datetime
    local_version: ContentVersion
    remote_versions: List[ContentVersion]
    resolution_strategy: Optional[ConflictResolutionStrategy]
    resolved: bool
    resolution_timestamp: Optional[datetime]
    resolution_metadata: Dict[str, Any]


@dataclass
class SyncRule:
    """Synchronization rule definition"""
    rule_id: str
    name: str
    source_platform: str
    target_platforms: List[str]
    content_types: List[str]
    sync_fields: List[str]
    sync_direction: SyncDirection
    conflict_resolution: ConflictResolutionStrategy
    sync_frequency: int
    enabled: bool
    conditions: Dict[str, Any]
    transformations: Dict[str, Any]


@dataclass
class SyncSession:
    """Synchronization session tracking"""
    session_id: str
    content_id: str
    platforms: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    status: SyncStatus
    changes_applied: List[Dict[str, Any]]
    conflicts_detected: List[str]
    errors: List[str]
    performance_metrics: Dict[str, Any]


@dataclass
class PlatformState:
    """Platform-specific content state"""
    platform: str
    content_id: str
    last_sync: datetime
    current_version: ContentVersion
    metadata_hash: str
    sync_status: SyncStatus
    pending_changes: List[Dict[str, Any]]
    platform_specific_data: Dict[str, Any]


class CrossPlatformSync:
    """
    Advanced cross-platform synchronization engine for content and metadata.
    
    Features:
    - Real-time bidirectional synchronization
    - Intelligent conflict detection and resolution
    - Version control and change tracking
    - Platform-specific transformation handling
    - Automated conflict resolution strategies
    - Comprehensive audit trails
    - Performance optimization for large-scale sync
    - Rollback and recovery capabilities
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the cross-platform sync engine"""
        self.config = config or {}
        self.sync_rules: Dict[str, SyncRule] = {}
        self.platform_states: Dict[str, Dict[str, PlatformState]] = {}
        self.content_versions: Dict[str, List[ContentVersion]] = {}
        self.sync_conflicts: List[SyncConflict] = []
        self.sync_sessions: Dict[str, SyncSession] = {}
        self.active_syncs: Dict[str, asyncio.Task] = {}
        
        # Configuration
        self.max_concurrent_syncs = self.config.get('max_concurrent_syncs', 5)
        self.sync_timeout_seconds = self.config.get('sync_timeout_seconds', 300)
        self.enable_real_time_sync = self.config.get('enable_real_time_sync', True)
        self.conflict_resolution_timeout = self.config.get('conflict_resolution_timeout', 3600)
        
        # Initialize platform adapters
        self.platform_adapters: Dict[str, Any] = {}
        self._initialize_platform_adapters()
        
        logger.info("Cross Platform Sync Engine initialized")
    
    async def create_sync_rule(self, rule_config: Dict[str, Any]) -> SyncRule:
        """
        Create a new synchronization rule
        
        Args:
            rule_config: Rule configuration
            
        Returns:
            Created sync rule
        """
        try:
            # Validate rule configuration
            validated_config = await self._validate_rule_config(rule_config)
            
            # Create sync rule
            rule = SyncRule(
                rule_id=validated_config.get('rule_id', str(uuid.uuid4())),
                name=validated_config['name'],
                source_platform=validated_config['source_platform'],
                target_platforms=validated_config['target_platforms'],
                content_types=validated_config.get('content_types', ['all']),
                sync_fields=validated_config.get('sync_fields', ['title', 'description', 'tags']),
                sync_direction=SyncDirection(validated_config.get('sync_direction', 'bidirectional')),
                conflict_resolution=ConflictResolutionStrategy(validated_config.get('conflict_resolution', 'latest_wins')),
                sync_frequency=validated_config.get('sync_frequency', 3600),  # 1 hour default
                enabled=validated_config.get('enabled', True),
                conditions=validated_config.get('conditions', {}),
                transformations=validated_config.get('transformations', {})
            )
            
            # Store rule
            self.sync_rules[rule.rule_id] = rule
            
            # Set up sync schedule if enabled
            if rule.enabled and self.enable_real_time_sync:
                await self._schedule_sync_rule(rule)
            
            logger.info(f"Sync rule created: {rule.rule_id} - {rule.name}")
            return rule
            
        except Exception as e:
            logger.error(f"Error creating sync rule: {e}")
            raise
    
    async def sync_content(self, content_id: str, 
                         platforms: List[str],
                         sync_options: Optional[Dict[str, Any]] = None) -> str:
        """
        Synchronize content across specified platforms
        
        Args:
            content_id: Content to synchronize
            platforms: Platforms to sync
            sync_options: Optional sync configuration
            
        Returns:
            Sync session ID
        """
        try:
            sync_options = sync_options or {}
            
            # Check concurrent sync limit
            if len(self.active_syncs) >= self.max_concurrent_syncs:
                raise RuntimeError("Maximum concurrent sync limit reached")
            
            # Create sync session
            session_id = str(uuid.uuid4())
            session = SyncSession(
                session_id=session_id,
                content_id=content_id,
                platforms=platforms,
                start_time=datetime.now(),
                end_time=None,
                status=SyncStatus.SYNCING,
                changes_applied=[],
                conflicts_detected=[],
                errors=[],
                performance_metrics={}
            )
            
            self.sync_sessions[session_id] = session
            
            # Start sync process
            sync_task = asyncio.create_task(
                self._sync_content_internal(session_id, sync_options)
            )
            self.active_syncs[session_id] = sync_task
            
            logger.info(f"Content sync started: {session_id} for content {content_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting content sync: {e}")
            raise
    
    async def detect_changes(self, content_id: str, platforms: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect changes across platforms for content
        
        Args:
            content_id: Content to check
            platforms: Platforms to check
            
        Returns:
            Detected changes per platform
        """
        try:
            changes_by_platform = {}
            
            # Get current state for each platform
            current_states = {}
            for platform in platforms:
                current_state = await self._get_platform_content_state(content_id, platform)
                current_states[platform] = current_state
            
            # Compare with stored states
            for platform in platforms:
                changes = []
                
                if content_id in self.platform_states and platform in self.platform_states[content_id]:
                    stored_state = self.platform_states[content_id][platform]
                    current_state = current_states[platform]
                    
                    # Detect changes
                    detected_changes = await self._compare_platform_states(stored_state, current_state)
                    changes.extend(detected_changes)
                else:
                    # First time seeing this content on this platform
                    changes.append({
                        'type': 'new_content',
                        'description': 'Content newly detected on platform',
                        'timestamp': datetime.now().isoformat()
                    })
                
                changes_by_platform[platform] = changes
            
            logger.info(f"Change detection completed for {content_id} across {len(platforms)} platforms")
            return changes_by_platform
            
        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            raise
    
    async def resolve_conflict(self, conflict_id: str, 
                             resolution_strategy: ConflictResolutionStrategy,
                             resolution_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Resolve a synchronization conflict
        
        Args:
            conflict_id: Conflict to resolve
            resolution_strategy: Resolution strategy to use
            resolution_data: Additional resolution data
            
        Returns:
            Resolution success status
        """
        try:
            conflict = next((c for c in self.sync_conflicts if c.conflict_id == conflict_id), None)
            if not conflict:
                raise ValueError(f"Conflict not found: {conflict_id}")
            
            if conflict.resolved:
                logger.warning(f"Conflict {conflict_id} already resolved")
                return True
            
            resolution_data = resolution_data or {}
            
            # Apply resolution strategy
            success = False
            if resolution_strategy == ConflictResolutionStrategy.LATEST_WINS:
                success = await self._resolve_latest_wins(conflict)
            elif resolution_strategy == ConflictResolutionStrategy.PLATFORM_PRIORITY:
                success = await self._resolve_platform_priority(conflict, resolution_data)
            elif resolution_strategy == ConflictResolutionStrategy.MERGE_CHANGES:
                success = await self._resolve_merge_changes(conflict)
            elif resolution_strategy == ConflictResolutionStrategy.BACKUP_AND_OVERWRITE:
                success = await self._resolve_backup_and_overwrite(conflict, resolution_data)
            else:  # MANUAL
                success = await self._resolve_manual(conflict, resolution_data)
            
            if success:
                conflict.resolved = True
                conflict.resolution_timestamp = datetime.now()
                conflict.resolution_strategy = resolution_strategy
                conflict.resolution_metadata = resolution_data
                
                logger.info(f"Conflict resolved: {conflict_id} using {resolution_strategy.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return False
    
    async def create_content_version(self, content_id: str, platform: str,
                                   metadata: Dict[str, Any],
                                   changes: List[str],
                                   author: str = "system") -> ContentVersion:
        """
        Create a new content version
        
        Args:
            content_id: Content identifier
            platform: Platform where version exists
            metadata: Content metadata
            changes: List of changes made
            author: Version author
            
        Returns:
            Created content version
        """
        try:
            # Get existing versions to determine version number
            existing_versions = self.content_versions.get(content_id, [])
            platform_versions = [v for v in existing_versions if v.platform == platform]
            
            version_number = max([v.version_number for v in platform_versions], default=0) + 1
            
            # Calculate content checksum
            metadata_json = json.dumps(metadata, sort_keys=True)
            checksum = hashlib.sha256(metadata_json.encode()).hexdigest()
            
            # Create version
            version = ContentVersion(
                version_id=str(uuid.uuid4()),
                content_id=content_id,
                platform=platform,
                version_number=version_number,
                timestamp=datetime.now(),
                checksum=checksum,
                metadata=metadata,
                changes=changes,
                author=author,
                commit_message=f"Version {version_number}: {', '.join(changes[:3])}{'...' if len(changes) > 3 else ''}"
            )
            
            # Store version
            if content_id not in self.content_versions:
                self.content_versions[content_id] = []
            self.content_versions[content_id].append(version)
            
            # Update platform state
            await self._update_platform_state(content_id, platform, version)
            
            logger.info(f"Content version created: {version.version_id} for {content_id} on {platform}")
            return version
            
        except Exception as e:
            logger.error(f"Error creating content version: {e}")
            raise
    
    async def get_sync_status(self, content_id: str, platforms: List[str]) -> Dict[str, Any]:
        """
        Get synchronization status for content across platforms
        
        Args:
            content_id: Content to check
            platforms: Platforms to check
            
        Returns:
            Sync status information
        """
        try:
            status_info = {
                'content_id': content_id,
                'overall_status': SyncStatus.IN_SYNC.value,
                'last_sync': None,
                'platform_statuses': {},
                'pending_conflicts': [],
                'recent_changes': [],
                'sync_health_score': 1.0
            }
            
            # Check platform statuses
            out_of_sync_count = 0
            last_sync_times = []
            
            for platform in platforms:
                platform_status = {
                    'status': SyncStatus.IN_SYNC.value,
                    'last_sync': None,
                    'pending_changes': 0,
                    'version_info': None
                }
                
                if content_id in self.platform_states and platform in self.platform_states[content_id]:
                    state = self.platform_states[content_id][platform]
                    platform_status['status'] = state.sync_status.value
                    platform_status['last_sync'] = state.last_sync.isoformat()
                    platform_status['pending_changes'] = len(state.pending_changes)
                    platform_status['version_info'] = {
                        'version_number': state.current_version.version_number,
                        'timestamp': state.current_version.timestamp.isoformat()
                    }
                    
                    last_sync_times.append(state.last_sync)
                    
                    if state.sync_status != SyncStatus.IN_SYNC:
                        out_of_sync_count += 1
                else:
                    platform_status['status'] = SyncStatus.PENDING.value
                    out_of_sync_count += 1
                
                status_info['platform_statuses'][platform] = platform_status
            
            # Determine overall status
            if out_of_sync_count == 0:
                status_info['overall_status'] = SyncStatus.IN_SYNC.value
            elif out_of_sync_count == len(platforms):
                status_info['overall_status'] = SyncStatus.OUT_OF_SYNC.value
            else:
                status_info['overall_status'] = SyncStatus.CONFLICT.value
            
            # Get last sync time
            if last_sync_times:
                status_info['last_sync'] = max(last_sync_times).isoformat()
            
            # Get pending conflicts
            content_conflicts = [
                {
                    'conflict_id': c.conflict_id,
                    'type': c.conflict_type,
                    'platforms': c.platforms_involved,
                    'detected_at': c.detected_at.isoformat()
                }
                for c in self.sync_conflicts
                if c.content_id == content_id and not c.resolved
            ]
            status_info['pending_conflicts'] = content_conflicts
            
            # Calculate sync health score
            status_info['sync_health_score'] = await self._calculate_sync_health_score(
                content_id, platforms, out_of_sync_count, len(content_conflicts)
            )
            
            logger.info(f"Sync status retrieved for {content_id}")
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            raise
    
    async def force_sync(self, content_id: str, source_platform: str, 
                        target_platforms: List[str]) -> str:
        """
        Force synchronization from source to target platforms
        
        Args:
            content_id: Content to sync
            source_platform: Source platform (master)
            target_platforms: Target platforms to update
            
        Returns:
            Sync session ID
        """
        try:
            # Get source content state
            source_state = await self._get_platform_content_state(content_id, source_platform)
            
            # Create sync session
            session_id = str(uuid.uuid4())
            session = SyncSession(
                session_id=session_id,
                content_id=content_id,
                platforms=[source_platform] + target_platforms,
                start_time=datetime.now(),
                end_time=None,
                status=SyncStatus.SYNCING,
                changes_applied=[],
                conflicts_detected=[],
                errors=[],
                performance_metrics={}
            )
            
            self.sync_sessions[session_id] = session
            
            # Force sync to each target platform
            for target_platform in target_platforms:
                try:
                    await self._force_sync_to_platform(
                        content_id, source_state, target_platform, session_id
                    )
                except Exception as e:
                    session.errors.append(f"Failed to sync to {target_platform}: {e}")
            
            # Complete session
            session.status = SyncStatus.IN_SYNC if not session.errors else SyncStatus.ERROR
            session.end_time = datetime.now()
            
            logger.info(f"Force sync completed: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error in force sync: {e}")
            raise
    
    async def get_sync_history(self, content_id: str, 
                             limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get synchronization history for content
        
        Args:
            content_id: Content to get history for
            limit: Maximum number of records to return
            
        Returns:
            Sync history records
        """
        try:
            history = []
            
            # Get version history
            versions = self.content_versions.get(content_id, [])
            for version in sorted(versions, key=lambda v: v.timestamp, reverse=True)[:limit]:
                history.append({
                    'type': 'version_created',
                    'timestamp': version.timestamp.isoformat(),
                    'platform': version.platform,
                    'version_number': version.version_number,
                    'changes': version.changes,
                    'author': version.author,
                    'commit_message': version.commit_message
                })
            
            # Get sync session history
            content_sessions = [
                s for s in self.sync_sessions.values()
                if s.content_id == content_id
            ]
            
            for session in sorted(content_sessions, key=lambda s: s.start_time, reverse=True)[:limit]:
                history.append({
                    'type': 'sync_session',
                    'timestamp': session.start_time.isoformat(),
                    'session_id': session.session_id,
                    'platforms': session.platforms,
                    'status': session.status.value,
                    'changes_applied': len(session.changes_applied),
                    'conflicts': len(session.conflicts_detected),
                    'errors': len(session.errors)
                })
            
            # Get conflict history
            content_conflicts = [
                c for c in self.sync_conflicts
                if c.content_id == content_id
            ]
            
            for conflict in sorted(content_conflicts, key=lambda c: c.detected_at, reverse=True)[:limit]:
                history.append({
                    'type': 'conflict',
                    'timestamp': conflict.detected_at.isoformat(),
                    'conflict_id': conflict.conflict_id,
                    'conflict_type': conflict.conflict_type,
                    'platforms': conflict.platforms_involved,
                    'resolved': conflict.resolved,
                    'resolution_strategy': conflict.resolution_strategy.value if conflict.resolution_strategy else None
                })
            
            # Sort combined history by timestamp
            history.sort(key=lambda h: h['timestamp'], reverse=True)
            
            logger.info(f"Sync history retrieved for {content_id}: {len(history)} records")
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Error getting sync history: {e}")
            raise
    
    # Private helper methods
    def _initialize_platform_adapters(self) -> None:
        """Initialize platform-specific adapters"""
        # Mock platform adapters - in production would have real API integrations
        self.platform_adapters = {
            'youtube': {'api_client': 'youtube_api', 'rate_limit': 10000},
            'instagram': {'api_client': 'instagram_api', 'rate_limit': 5000},
            'tiktok': {'api_client': 'tiktok_api', 'rate_limit': 3000},
            'twitter': {'api_client': 'twitter_api', 'rate_limit': 15000},
            'facebook': {'api_client': 'facebook_api', 'rate_limit': 5000},
            'linkedin': {'api_client': 'linkedin_api', 'rate_limit': 2000}
        }
    
    async def _validate_rule_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sync rule configuration"""
        required_fields = ['name', 'source_platform', 'target_platforms']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Required field '{field}' missing from rule config")
        
        # Validate platforms
        all_platforms = [config['source_platform']] + config['target_platforms']
        for platform in all_platforms:
            if platform not in self.platform_adapters:
                raise ValueError(f"Unsupported platform: {platform}")
        
        return config
    
    async def _schedule_sync_rule(self, rule: SyncRule) -> None:
        """Schedule automatic sync rule execution"""
        # In production, would integrate with task scheduler
        logger.info(f"Sync rule scheduled: {rule.rule_id} every {rule.sync_frequency} seconds")
    
    async def _sync_content_internal(self, session_id: str, sync_options: Dict[str, Any]) -> None:
        """Internal content synchronization logic"""
        try:
            session = self.sync_sessions[session_id]
            content_id = session.content_id
            platforms = session.platforms
            
            # Phase 1: Detect changes
            changes_by_platform = await self.detect_changes(content_id, platforms)
            
            # Phase 2: Identify conflicts
            conflicts = await self._identify_conflicts(content_id, changes_by_platform)
            
            if conflicts:
                session.conflicts_detected.extend([c.conflict_id for c in conflicts])
                self.sync_conflicts.extend(conflicts)
                
                # Auto-resolve conflicts based on strategy
                for conflict in conflicts:
                    if sync_options.get('auto_resolve_conflicts', True):
                        strategy = ConflictResolutionStrategy(
                            sync_options.get('conflict_resolution', 'latest_wins')
                        )
                        await self.resolve_conflict(conflict.conflict_id, strategy)
            
            # Phase 3: Apply changes
            for platform, changes in changes_by_platform.items():
                for change in changes:
                    try:
                        await self._apply_change_to_platform(content_id, platform, change, session_id)
                        session.changes_applied.append({
                            'platform': platform,
                            'change': change,
                            'applied_at': datetime.now().isoformat()
                        })
                    except Exception as e:
                        session.errors.append(f"Failed to apply change to {platform}: {e}")
            
            # Phase 4: Verify sync
            final_status = await self._verify_sync_completion(content_id, platforms)
            session.status = final_status
            
        except Exception as e:
            session.status = SyncStatus.ERROR
            session.errors.append(f"Sync failed: {e}")
            logger.error(f"Error in sync session {session_id}: {e}")
        
        finally:
            session.end_time = datetime.now()
            if session_id in self.active_syncs:
                del self.active_syncs[session_id]
    
    async def _get_platform_content_state(self, content_id: str, platform: str) -> PlatformState:
        """Get current content state from platform"""
        # Mock platform state retrieval - in production would use real APIs
        current_time = datetime.now()
        
        # Create mock metadata
        mock_metadata = {
            'title': f'Content {content_id} on {platform}',
            'description': f'Description for content {content_id}',
            'tags': ['tag1', 'tag2', 'tag3'],
            'privacy': 'public',
            'monetization': 'enabled',
            'thumbnail_url': f'https://{platform}.com/thumb/{content_id}',
            'last_modified': current_time.isoformat()
        }
        
        # Create version
        version = ContentVersion(
            version_id=str(uuid.uuid4()),
            content_id=content_id,
            platform=platform,
            version_number=1,
            timestamp=current_time,
            checksum=hashlib.sha256(json.dumps(mock_metadata, sort_keys=True).encode()).hexdigest(),
            metadata=mock_metadata,
            changes=[],
            author='system',
            commit_message='Current platform state'
        )
        
        # Create platform state
        state = PlatformState(
            platform=platform,
            content_id=content_id,
            last_sync=current_time,
            current_version=version,
            metadata_hash=version.checksum,
            sync_status=SyncStatus.IN_SYNC,
            pending_changes=[],
            platform_specific_data={
                'platform_url': f'https://{platform}.com/content/{content_id}',
                'platform_id': f'{platform}_{content_id}',
                'api_version': '1.0'
            }
        )
        
        return state
    
    async def _compare_platform_states(self, stored_state: PlatformState, 
                                     current_state: PlatformState) -> List[Dict[str, Any]]:
        """Compare stored and current platform states to detect changes"""
        changes = []
        
        # Compare metadata hashes
        if stored_state.metadata_hash != current_state.metadata_hash:
            # Detailed field comparison
            stored_metadata = stored_state.current_version.metadata
            current_metadata = current_state.current_version.metadata
            
            for field in ['title', 'description', 'tags', 'privacy', 'monetization']:
                if stored_metadata.get(field) != current_metadata.get(field):
                    changes.append({
                        'type': f'{field}_change',
                        'field': field,
                        'old_value': stored_metadata.get(field),
                        'new_value': current_metadata.get(field),
                        'timestamp': current_state.current_version.timestamp.isoformat()
                    })
        
        # Check for pending changes
        if current_state.pending_changes:
            for pending_change in current_state.pending_changes:
                changes.append({
                    'type': 'pending_change',
                    'change_data': pending_change,
                    'timestamp': datetime.now().isoformat()
                })
        
        return changes
    
    async def _identify_conflicts(self, content_id: str, 
                                changes_by_platform: Dict[str, List[Dict[str, Any]]]) -> List[SyncConflict]:
        """Identify conflicts between platform changes"""
        conflicts = []
        
        # Find platforms with conflicting changes
        platforms_with_changes = {
            platform: changes for platform, changes in changes_by_platform.items()
            if changes
        }
        
        if len(platforms_with_changes) > 1:
            # Check for conflicting field changes
            field_changes = {}
            
            for platform, changes in platforms_with_changes.items():
                for change in changes:
                    if change.get('field'):
                        field = change['field']
                        if field not in field_changes:
                            field_changes[field] = []
                        field_changes[field].append((platform, change))
            
            # Create conflicts for fields changed on multiple platforms
            for field, platform_changes in field_changes.items():
                if len(platform_changes) > 1:
                    platforms_involved = [pc[0] for pc in platform_changes]
                    
                    # Get versions for conflict
                    local_version = None
                    remote_versions = []
                    
                    for platform, change in platform_changes:
                        version = await self._get_platform_version(content_id, platform)
                        if not local_version:
                            local_version = version
                        else:
                            remote_versions.append(version)
                    
                    conflict = SyncConflict(
                        conflict_id=str(uuid.uuid4()),
                        content_id=content_id,
                        platforms_involved=platforms_involved,
                        conflict_type=f'{field}_conflict',
                        detected_at=datetime.now(),
                        local_version=local_version,
                        remote_versions=remote_versions,
                        resolution_strategy=None,
                        resolved=False,
                        resolution_timestamp=None,
                        resolution_metadata={}
                    )
                    
                    conflicts.append(conflict)
        
        return conflicts
    
    async def _get_platform_version(self, content_id: str, platform: str) -> ContentVersion:
        """Get latest version for content on platform"""
        versions = self.content_versions.get(content_id, [])
        platform_versions = [v for v in versions if v.platform == platform]
        
        if platform_versions:
            return max(platform_versions, key=lambda v: v.version_number)
        
        # Create default version if none exists
        return ContentVersion(
            version_id=str(uuid.uuid4()),
            content_id=content_id,
            platform=platform,
            version_number=1,
            timestamp=datetime.now(),
            checksum='default_checksum',
            metadata={},
            changes=[],
            author='system',
            commit_message='Default version'
        )
    
    # Conflict resolution methods
    async def _resolve_latest_wins(self, conflict: SyncConflict) -> bool:
        """Resolve conflict using latest timestamp wins strategy"""
        try:
            # Find the version with the latest timestamp
            all_versions = [conflict.local_version] + conflict.remote_versions
            latest_version = max(all_versions, key=lambda v: v.timestamp)
            
            # Apply latest version to all platforms
            for platform in conflict.platforms_involved:
                if platform != latest_version.platform:
                    await self._apply_version_to_platform(
                        conflict.content_id, platform, latest_version
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error in latest_wins resolution: {e}")
            return False
    
    async def _resolve_platform_priority(self, conflict: SyncConflict, 
                                       resolution_data: Dict[str, Any]) -> bool:
        """Resolve conflict using platform priority strategy"""
        try:
            platform_priorities = resolution_data.get('platform_priorities', {})
            
            # Find highest priority platform
            highest_priority = -1
            winning_platform = None
            
            for platform in conflict.platforms_involved:
                priority = platform_priorities.get(platform, 0)
                if priority > highest_priority:
                    highest_priority = priority
                    winning_platform = platform
            
            if winning_platform:
                winning_version = next(
                    (v for v in [conflict.local_version] + conflict.remote_versions 
                     if v.platform == winning_platform), 
                    conflict.local_version
                )
                
                # Apply winning version to all platforms
                for platform in conflict.platforms_involved:
                    if platform != winning_platform:
                        await self._apply_version_to_platform(
                            conflict.content_id, platform, winning_version
                        )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in platform_priority resolution: {e}")
            return False
    
    async def _resolve_merge_changes(self, conflict: SyncConflict) -> bool:
        """Resolve conflict by merging changes from all platforms"""
        try:
            # Merge metadata from all versions
            merged_metadata = {}
            all_versions = [conflict.local_version] + conflict.remote_versions
            
            # Start with the earliest version as base
            base_version = min(all_versions, key=lambda v: v.timestamp)
            merged_metadata.update(base_version.metadata)
            
            # Apply changes from each version
            for version in sorted(all_versions, key=lambda v: v.timestamp):
                for field, value in version.metadata.items():
                    # For lists (like tags), merge them
                    if isinstance(value, list) and field in merged_metadata:
                        if isinstance(merged_metadata[field], list):
                            merged_metadata[field] = list(set(merged_metadata[field] + value))
                        else:
                            merged_metadata[field] = value
                    else:
                        merged_metadata[field] = value
            
            # Create merged version
            merged_version = ContentVersion(
                version_id=str(uuid.uuid4()),
                content_id=conflict.content_id,
                platform='merged',
                version_number=max(v.version_number for v in all_versions) + 1,
                timestamp=datetime.now(),
                checksum=hashlib.sha256(json.dumps(merged_metadata, sort_keys=True).encode()).hexdigest(),
                metadata=merged_metadata,
                changes=['merged_conflict_resolution'],
                author='system',
                commit_message='Merged conflict resolution'
            )
            
            # Apply merged version to all platforms
            for platform in conflict.platforms_involved:
                await self._apply_version_to_platform(
                    conflict.content_id, platform, merged_version
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error in merge_changes resolution: {e}")
            return False
    
    async def _resolve_backup_and_overwrite(self, conflict: SyncConflict,
                                          resolution_data: Dict[str, Any]) -> bool:
        """Resolve conflict by backing up and overwriting with preferred version"""
        try:
            preferred_platform = resolution_data.get('preferred_platform')
            if not preferred_platform:
                return False
            
            # Find preferred version
            preferred_version = next(
                (v for v in [conflict.local_version] + conflict.remote_versions 
                 if v.platform == preferred_platform),
                None
            )
            
            if not preferred_version:
                return False
            
            # Backup other versions
            for version in [conflict.local_version] + conflict.remote_versions:
                if version.platform != preferred_platform:
                    backup_version = ContentVersion(
                        version_id=str(uuid.uuid4()),
                        content_id=version.content_id,
                        platform=f"{version.platform}_backup",
                        version_number=version.version_number,
                        timestamp=version.timestamp,
                        checksum=version.checksum,
                        metadata=version.metadata,
                        changes=version.changes + ['backed_up_before_overwrite'],
                        author=version.author,
                        commit_message=f"Backup before overwrite: {version.commit_message}"
                    )
                    
                    # Store backup
                    if version.content_id not in self.content_versions:
                        self.content_versions[version.content_id] = []
                    self.content_versions[version.content_id].append(backup_version)
            
            # Apply preferred version to all platforms
            for platform in conflict.platforms_involved:
                if platform != preferred_platform:
                    await self._apply_version_to_platform(
                        conflict.content_id, platform, preferred_version
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error in backup_and_overwrite resolution: {e}")
            return False
    
    async def _resolve_manual(self, conflict: SyncConflict, 
                            resolution_data: Dict[str, Any]) -> bool:
        """Resolve conflict using manual resolution data"""
        try:
            manual_metadata = resolution_data.get('manual_metadata')
            if not manual_metadata:
                return False
            
            # Create manual resolution version
            manual_version = ContentVersion(
                version_id=str(uuid.uuid4()),
                content_id=conflict.content_id,
                platform='manual_resolution',
                version_number=max(
                    v.version_number for v in [conflict.local_version] + conflict.remote_versions
                ) + 1,
                timestamp=datetime.now(),
                checksum=hashlib.sha256(json.dumps(manual_metadata, sort_keys=True).encode()).hexdigest(),
                metadata=manual_metadata,
                changes=['manual_conflict_resolution'],
                author=resolution_data.get('resolver', 'admin'),
                commit_message='Manual conflict resolution'
            )
            
            # Apply manual version to all platforms
            for platform in conflict.platforms_involved:
                await self._apply_version_to_platform(
                    conflict.content_id, platform, manual_version
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error in manual resolution: {e}")
            return False
    
    async def _apply_version_to_platform(self, content_id: str, platform: str, 
                                       version: ContentVersion) -> None:
        """Apply version to specific platform"""
        try:
            # Mock platform API call to update content
            logger.info(f"Applying version {version.version_id} to {platform} for content {content_id}")
            
            # Update platform state
            await self._update_platform_state(content_id, platform, version)
            
        except Exception as e:
            logger.error(f"Error applying version to platform {platform}: {e}")
            raise
    
    async def _apply_change_to_platform(self, content_id: str, platform: str,
                                      change: Dict[str, Any], session_id: str) -> None:
        """Apply specific change to platform"""
        try:
            # Mock change application
            logger.info(f"Applying change {change['type']} to {platform} for content {content_id}")
            
            # Update platform state based on change
            if content_id not in self.platform_states:
                self.platform_states[content_id] = {}
            
            if platform not in self.platform_states[content_id]:
                # Create initial state
                initial_state = await self._get_platform_content_state(content_id, platform)
                self.platform_states[content_id][platform] = initial_state
            
            state = self.platform_states[content_id][platform]
            
            # Apply change to metadata
            if change.get('field') and 'new_value' in change:
                state.current_version.metadata[change['field']] = change['new_value']
                
                # Update checksum
                metadata_json = json.dumps(state.current_version.metadata, sort_keys=True)
                state.metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
                state.current_version.checksum = state.metadata_hash
                
                # Update sync time
                state.last_sync = datetime.now()
            
        except Exception as e:
            logger.error(f"Error applying change to platform {platform}: {e}")
            raise
    
    async def _verify_sync_completion(self, content_id: str, platforms: List[str]) -> SyncStatus:
        """Verify that sync completed successfully across all platforms"""
        try:
            # Check if all platforms have consistent state
            platform_checksums = {}
            
            for platform in platforms:
                if content_id in self.platform_states and platform in self.platform_states[content_id]:
                    state = self.platform_states[content_id][platform]
                    platform_checksums[platform] = state.metadata_hash
                else:
                    return SyncStatus.ERROR
            
            # Check if all checksums are the same
            unique_checksums = set(platform_checksums.values())
            
            if len(unique_checksums) == 1:
                return SyncStatus.IN_SYNC
            elif len(unique_checksums) <= len(platforms) // 2:
                return SyncStatus.CONFLICT
            else:
                return SyncStatus.OUT_OF_SYNC
            
        except Exception as e:
            logger.error(f"Error verifying sync completion: {e}")
            return SyncStatus.ERROR
    
    async def _update_platform_state(self, content_id: str, platform: str, 
                                   version: ContentVersion) -> None:
        """Update stored platform state"""
        if content_id not in self.platform_states:
            self.platform_states[content_id] = {}
        
        state = PlatformState(
            platform=platform,
            content_id=content_id,
            last_sync=datetime.now(),
            current_version=version,
            metadata_hash=version.checksum,
            sync_status=SyncStatus.IN_SYNC,
            pending_changes=[],
            platform_specific_data={}
        )
        
        self.platform_states[content_id][platform] = state
    
    async def _force_sync_to_platform(self, content_id: str, source_state: PlatformState,
                                     target_platform: str, session_id: str) -> None:
        """Force sync content from source to target platform"""
        try:
            # Apply source version to target platform
            await self._apply_version_to_platform(content_id, target_platform, source_state.current_version)
            
            # Log the sync
            logger.info(f"Force synced {content_id} from {source_state.platform} to {target_platform}")
            
        except Exception as e:
            logger.error(f"Error force syncing to {target_platform}: {e}")
            raise
    
    async def _calculate_sync_health_score(self, content_id: str, platforms: List[str],
                                         out_of_sync_count: int, conflict_count: int) -> float:
        """Calculate sync health score (0.0 to 1.0)"""
        base_score = 1.0
        
        # Reduce score for out-of-sync platforms
        if out_of_sync_count > 0:
            base_score -= (out_of_sync_count / len(platforms)) * 0.5
        
        # Reduce score for unresolved conflicts
        if conflict_count > 0:
            base_score -= min(conflict_count * 0.1, 0.3)
        
        # Check sync freshness
        if content_id in self.platform_states:
            last_sync_times = []
            for platform in platforms:
                if platform in self.platform_states[content_id]:
                    last_sync_times.append(self.platform_states[content_id][platform].last_sync)
            
            if last_sync_times:
                oldest_sync = min(last_sync_times)
                hours_since_sync = (datetime.now() - oldest_sync).total_seconds() / 3600
                
                # Reduce score for stale syncs
                if hours_since_sync > 24:
                    base_score -= 0.2
                elif hours_since_sync > 6:
                    base_score -= 0.1
        
        return max(0.0, base_score)