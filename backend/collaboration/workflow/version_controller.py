"""Version Controller - Advanced Creative Content Version Management System
=========================================================================

Comprehensive version control system providing:
- Creative content versioning and branching
- Conflict resolution for multimedia assets
- Merge strategies for collaborative editing
- Version history and comparison
- Asset dependency tracking
- Rollback and restore capabilities

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import os
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of creative content"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DESIGN = "design"
    CODE = "code"
    DOCUMENT = "document"
    COMPOSITE = "composite"


class VersionStatus(Enum):
    """Version status"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class MergeStrategy(Enum):
    """Merge strategies for content"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    LAST_WRITER_WINS = "last_writer_wins"
    FIRST_WRITER_WINS = "first_writer_wins"
    SMART_MERGE = "smart_merge"
    USER_CHOICE = "user_choice"


class ConflictType(Enum):
    """Types of merge conflicts"""
    CONTENT_CONFLICT = "content_conflict"
    METADATA_CONFLICT = "metadata_conflict"
    TIMING_CONFLICT = "timing_conflict"
    ASSET_CONFLICT = "asset_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"


@dataclass
class ContentVersion:
    """Content version definition"""
    version_id: str
    content_id: str
    version_number: str
    content_type: ContentType
    title: str
    description: str = ""
    creator_id: str = ""
    parent_version_id: Optional[str] = None
    branch_name: str = "main"
    status: VersionStatus = VersionStatus.DRAFT
    content_hash: str = ""
    file_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.version_id:
            self.version_id = str(uuid.uuid4())


@dataclass
class VersionHistory:
    """Version history for content"""
    content_id: str
    versions: List[ContentVersion] = field(default_factory=list)
    branches: Dict[str, List[str]] = field(default_factory=dict)
    merge_history: List[Dict[str, Any]] = field(default_factory=list)
    latest_version: Optional[str] = None
    
    def __post_init__(self):
        if not self.content_id:
            self.content_id = str(uuid.uuid4())


@dataclass
class MergeConflict:
    """Merge conflict definition"""
    conflict_id: str
    content_id: str
    source_version_id: str
    target_version_id: str
    conflict_type: ConflictType
    description: str
    conflicting_sections: List[Dict[str, Any]] = field(default_factory=list)
    suggested_resolution: Dict[str, Any] = field(default_factory=dict)
    resolution_options: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.conflict_id:
            self.conflict_id = str(uuid.uuid4())


@dataclass
class ConflictResolution:
    """Conflict resolution result"""
    resolution_id: str
    conflict_id: str
    resolver_id: str
    resolution_strategy: str
    resolved_content: Dict[str, Any]
    resolution_notes: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.resolution_id:
            self.resolution_id = str(uuid.uuid4())


@dataclass
class BranchOperation:
    """Branch operation record"""
    operation_id: str
    content_id: str
    operation_type: str  # create, merge, delete
    source_branch: str
    target_branch: Optional[str] = None
    operator_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.operation_id:
            self.operation_id = str(uuid.uuid4())


@dataclass
class BranchManagement:
    """Branch management system"""
    content_id: str
    active_branches: Dict[str, str] = field(default_factory=dict)  # branch_name -> latest_version_id
    branch_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    merge_policies: Dict[str, Any] = field(default_factory=dict)
    access_control: Dict[str, List[str]] = field(default_factory=dict)


class VersionController:
    """
    Advanced Creative Content Version Management System
    
    Provides sophisticated version control for multimedia content,
    branching strategies, and intelligent conflict resolution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the version controller"""
        self.config = config or {}
        
        # Storage settings
        self.storage_path = self.config.get('storage_path', './content_versions')
        self.max_versions_per_content = self.config.get('max_versions', 100)
        self.auto_cleanup_days = self.config.get('auto_cleanup_days', 365)
        
        # Merge settings
        self.default_merge_strategy = self.config.get(
            'default_merge_strategy', MergeStrategy.SMART_MERGE
        )
        self.conflict_resolution_timeout = self.config.get(
            'conflict_timeout_hours', 24
        )
        
        # Data storage
        self.content_versions = {}
        self.version_histories = {}
        self.branch_management = {}
        self.merge_conflicts = {}
        self.conflict_resolutions = {}
        
        # Analytics
        self.version_metrics = defaultdict(dict)
        self.usage_stats = defaultdict(list)
        
        # Ensure storage directory exists
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        
        logger.info("VersionController initialized with creative content management")
    
    async def create_version(
        self,
        content_id: str,
        title: str,
        content_type: ContentType,
        creator_id: str,
        content_data: Dict[str, Any],
        parent_version_id: Optional[str] = None,
        branch_name: str = "main",
        description: str = ""
    ) -> ContentVersion:
        """
        Create a new content version
        
        Args:
            content_id: Content identifier
            title: Version title
            content_type: Type of content
            creator_id: Creator identifier
            content_data: Content data and metadata
            parent_version_id: Parent version for lineage
            branch_name: Branch name
            description: Version description
            
        Returns:
            Created content version
        """
        try:
            # Generate version number
            version_number = await self._generate_version_number(
                content_id, branch_name
            )
            
            # Calculate content hash
            content_hash = await self._calculate_content_hash(content_data)
            
            # Store content data
            file_path = await self._store_content_data(
                content_id, version_number, content_data
            )
            
            # Create version
            version = ContentVersion(
                version_id=str(uuid.uuid4()),
                content_id=content_id,
                version_number=version_number,
                content_type=content_type,
                title=title,
                description=description,
                creator_id=creator_id,
                parent_version_id=parent_version_id,
                branch_name=branch_name,
                content_hash=content_hash,
                file_path=file_path,
                metadata=content_data.get('metadata', {}),
                dependencies=content_data.get('dependencies', []),
                tags=content_data.get('tags', [])
            )
            
            # Store version
            self.content_versions[version.version_id] = version
            
            # Update version history
            await self._update_version_history(version)
            
            # Update branch management
            await self._update_branch_tracking(version)
            
            logger.info(f"Version {version_number} created for content {content_id}")
            return version
            
        except Exception as e:
            logger.error(f"Failed to create version: {str(e)}")
            raise
    
    async def create_branch(
        self,
        content_id: str,
        branch_name: str,
        source_version_id: str,
        creator_id: str,
        description: str = ""
    ) -> BranchOperation:
        """
        Create a new branch from existing version
        
        Args:
            content_id: Content identifier
            branch_name: New branch name
            source_version_id: Source version to branch from
            creator_id: Branch creator
            description: Branch description
            
        Returns:
            Branch operation record
        """
        try:
            if source_version_id not in self.content_versions:
                raise ValueError(f"Source version {source_version_id} not found")
            
            source_version = self.content_versions[source_version_id]
            
            # Initialize branch management if needed
            if content_id not in self.branch_management:
                self.branch_management[content_id] = BranchManagement(
                    content_id=content_id
                )
            
            branch_mgmt = self.branch_management[content_id]
            
            # Check if branch already exists
            if branch_name in branch_mgmt.active_branches:
                raise ValueError(f"Branch {branch_name} already exists")
            
            # Create branch
            branch_mgmt.active_branches[branch_name] = source_version_id
            branch_mgmt.branch_metadata[branch_name] = {
                'created_by': creator_id,
                'created_at': datetime.now().isoformat(),
                'description': description,
                'source_version': source_version_id,
                'total_versions': 1
            }
            
            # Record operation
            operation = BranchOperation(
                operation_id=str(uuid.uuid4()),
                content_id=content_id,
                operation_type='create',
                source_branch=source_version.branch_name,
                target_branch=branch_name,
                operator_id=creator_id,
                metadata={
                    'source_version_id': source_version_id,
                    'description': description
                }
            )
            
            logger.info(f"Branch '{branch_name}' created for content {content_id}")
            return operation
            
        except Exception as e:
            logger.error(f"Failed to create branch: {str(e)}")
            raise
    
    async def merge_branches(
        self,
        content_id: str,
        source_branch: str,
        target_branch: str,
        merger_id: str,
        strategy: Optional[MergeStrategy] = None
    ) -> Union[ContentVersion, List[MergeConflict]]:
        """
        Merge branches with conflict detection
        
        Args:
            content_id: Content identifier
            source_branch: Source branch to merge from
            target_branch: Target branch to merge into
            merger_id: User performing merge
            strategy: Merge strategy to use
            
        Returns:
            Merged version or list of conflicts to resolve
        """
        try:
            strategy = strategy or self.default_merge_strategy
            
            if content_id not in self.branch_management:
                raise ValueError(f"No branch management found for content {content_id}")
            
            branch_mgmt = self.branch_management[content_id]
            
            # Get latest versions from both branches
            if source_branch not in branch_mgmt.active_branches:
                raise ValueError(f"Source branch {source_branch} not found")
            if target_branch not in branch_mgmt.active_branches:
                raise ValueError(f"Target branch {target_branch} not found")
            
            source_version_id = branch_mgmt.active_branches[source_branch]
            target_version_id = branch_mgmt.active_branches[target_branch]
            
            source_version = self.content_versions[source_version_id]
            target_version = self.content_versions[target_version_id]
            
            # Detect conflicts
            conflicts = await self._detect_merge_conflicts(
                source_version, target_version
            )
            
            if conflicts and strategy not in [MergeStrategy.AUTOMATIC, MergeStrategy.SMART_MERGE]:
                # Return conflicts for manual resolution
                for conflict in conflicts:
                    self.merge_conflicts[conflict.conflict_id] = conflict
                return conflicts
            
            # Attempt automatic merge
            merged_version = await self._perform_merge(
                source_version, target_version, strategy, merger_id, conflicts
            )
            
            if merged_version:
                # Update branch tracking
                branch_mgmt.active_branches[target_branch] = merged_version.version_id
                
                # Record merge in history
                if content_id in self.version_histories:
                    self.version_histories[content_id].merge_history.append({
                        'source_branch': source_branch,
                        'target_branch': target_branch,
                        'source_version': source_version_id,
                        'target_version': target_version_id,
                        'merged_version': merged_version.version_id,
                        'merger_id': merger_id,
                        'timestamp': datetime.now().isoformat(),
                        'strategy': strategy.value,
                        'conflicts_resolved': len(conflicts)
                    })
                
                logger.info(f"Branches merged: {source_branch} -> {target_branch}")
                return merged_version
            else:
                # Return conflicts that couldn't be auto-resolved
                return conflicts
                
        except Exception as e:
            logger.error(f"Failed to merge branches: {str(e)}")
            raise
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        resolver_id: str,
        resolution_strategy: str,
        resolution_data: Dict[str, Any]
    ) -> ConflictResolution:
        """
        Resolve a merge conflict
        
        Args:
            conflict_id: Conflict identifier
            resolver_id: User resolving conflict
            resolution_strategy: How to resolve
            resolution_data: Resolution data
            
        Returns:
            Conflict resolution record
        """
        try:
            if conflict_id not in self.merge_conflicts:
                raise ValueError(f"Conflict {conflict_id} not found")
            
            conflict = self.merge_conflicts[conflict_id]
            
            # Create resolution
            resolution = ConflictResolution(
                resolution_id=str(uuid.uuid4()),
                conflict_id=conflict_id,
                resolver_id=resolver_id,
                resolution_strategy=resolution_strategy,
                resolved_content=resolution_data,
                resolution_notes=resolution_data.get('notes', '')
            )
            
            self.conflict_resolutions[resolution.resolution_id] = resolution
            
            # Apply resolution to create merged version
            await self._apply_conflict_resolution(conflict, resolution)
            
            logger.info(f"Conflict {conflict_id} resolved by {resolver_id}")
            return resolution
            
        except Exception as e:
            logger.error(f"Failed to resolve conflict: {str(e)}")
            raise
    
    async def get_version_history(self, content_id: str) -> VersionHistory:
        """Get complete version history for content"""
        if content_id in self.version_histories:
            return self.version_histories[content_id]
        else:
            # Create empty history
            history = VersionHistory(content_id=content_id)
            self.version_histories[content_id] = history
            return history
    
    async def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two versions and show differences
        
        Args:
            version_id_1: First version ID
            version_id_2: Second version ID
            
        Returns:
            Comparison results
        """
        try:
            if version_id_1 not in self.content_versions:
                raise ValueError(f"Version {version_id_1} not found")
            if version_id_2 not in self.content_versions:
                raise ValueError(f"Version {version_id_2} not found")
            
            version_1 = self.content_versions[version_id_1]
            version_2 = self.content_versions[version_id_2]
            
            # Load content data
            content_1 = await self._load_content_data(version_1.file_path)
            content_2 = await self._load_content_data(version_2.file_path)
            
            # Perform comparison based on content type
            comparison = await self._compare_content(
                content_1, content_2, version_1.content_type
            )
            
            return {
                'version_1': {
                    'id': version_1.version_id,
                    'number': version_1.version_number,
                    'title': version_1.title,
                    'creator': version_1.creator_id,
                    'created_at': version_1.created_at.isoformat()
                },
                'version_2': {
                    'id': version_2.version_id,
                    'number': version_2.version_number,
                    'title': version_2.title,
                    'creator': version_2.creator_id,
                    'created_at': version_2.created_at.isoformat()
                },
                'differences': comparison,
                'similarity_score': comparison.get('similarity_score', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Failed to compare versions: {str(e)}")
            raise
    
    async def rollback_to_version(
        self,
        content_id: str,
        version_id: str,
        rollback_user_id: str,
        reason: str = ""
    ) -> ContentVersion:
        """
        Rollback content to a specific version
        
        Args:
            content_id: Content identifier
            version_id: Version to rollback to
            rollback_user_id: User performing rollback
            reason: Reason for rollback
            
        Returns:
            New version created from rollback
        """
        try:
            if version_id not in self.content_versions:
                raise ValueError(f"Version {version_id} not found")
            
            rollback_version = self.content_versions[version_id]
            
            # Load content data from rollback version
            content_data = await self._load_content_data(rollback_version.file_path)
            
            # Create new version from rollback
            new_version = await self.create_version(
                content_id=content_id,
                title=f"Rollback to {rollback_version.version_number}",
                content_type=rollback_version.content_type,
                creator_id=rollback_user_id,
                content_data=content_data,
                parent_version_id=rollback_version.version_id,
                branch_name=rollback_version.branch_name,
                description=f"Rollback to version {rollback_version.version_number}. Reason: {reason}"
            )
            
            # Add rollback metadata
            new_version.metadata['rollback_info'] = {
                'original_version_id': version_id,
                'rollback_reason': reason,
                'rollback_timestamp': datetime.now().isoformat(),
                'rollback_user': rollback_user_id
            }
            
            logger.info(f"Content {content_id} rolled back to version {rollback_version.version_number}")
            return new_version
            
        except Exception as e:
            logger.error(f"Failed to rollback version: {str(e)}")
            raise
    
    async def _generate_version_number(
        self, 
        content_id: str, 
        branch_name: str
    ) -> str:
        """Generate version number for content"""
        # Get existing versions for this content and branch
        existing_versions = [
            v for v in self.content_versions.values()
            if v.content_id == content_id and v.branch_name == branch_name
        ]
        
        if not existing_versions:
            return "1.0.0" if branch_name == "main" else f"{branch_name}-1.0.0"
        
        # Find highest version number
        version_numbers = []
        for version in existing_versions:
            try:
                # Extract numeric part from version
                if branch_name == "main":
                    parts = version.version_number.split('.')
                else:
                    parts = version.version_number.replace(f"{branch_name}-", "").split('.')
                
                if len(parts) >= 3:
                    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                    version_numbers.append((major, minor, patch))
            except ValueError:
                continue
        
        if not version_numbers:
            return "1.0.0" if branch_name == "main" else f"{branch_name}-1.0.0"
        
        # Increment patch version
        latest = max(version_numbers)
        new_version = f"{latest[0]}.{latest[1]}.{latest[2] + 1}"
        
        return new_version if branch_name == "main" else f"{branch_name}-{new_version}"
    
    async def _calculate_content_hash(self, content_data: Dict[str, Any]) -> str:
        """Calculate hash for content data"""
        # Create stable string representation
        content_str = json.dumps(content_data, sort_keys=True, default=str)
        
        # Calculate SHA-256 hash
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    async def _store_content_data(
        self, 
        content_id: str, 
        version_number: str, 
        content_data: Dict[str, Any]
    ) -> str:
        """Store content data to filesystem"""
        # Create content directory
        content_dir = Path(self.storage_path) / content_id
        content_dir.mkdir(parents=True, exist_ok=True)
        
        # Create version file
        file_name = f"{version_number}.json"
        file_path = content_dir / file_name
        
        # Store content data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, default=str)
        
        return str(file_path)
    
    async def _load_content_data(self, file_path: str) -> Dict[str, Any]:
        """Load content data from filesystem"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Content file not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in content file: {file_path}")
            return {}
    
    async def _update_version_history(self, version: ContentVersion):
        """Update version history with new version"""
        content_id = version.content_id
        
        if content_id not in self.version_histories:
            self.version_histories[content_id] = VersionHistory(content_id=content_id)
        
        history = self.version_histories[content_id]
        history.versions.append(version)
        history.latest_version = version.version_id
        
        # Update branch tracking in history
        if version.branch_name not in history.branches:
            history.branches[version.branch_name] = []
        history.branches[version.branch_name].append(version.version_id)
    
    async def _update_branch_tracking(self, version: ContentVersion):
        """Update branch tracking with new version"""
        content_id = version.content_id
        
        if content_id not in self.branch_management:
            self.branch_management[content_id] = BranchManagement(
                content_id=content_id
            )
        
        branch_mgmt = self.branch_management[content_id]
        
        # Update active branch pointer
        branch_mgmt.active_branches[version.branch_name] = version.version_id
        
        # Update branch metadata
        if version.branch_name not in branch_mgmt.branch_metadata:
            branch_mgmt.branch_metadata[version.branch_name] = {
                'created_by': version.creator_id,
                'created_at': version.created_at.isoformat(),
                'total_versions': 1
            }
        else:
            branch_mgmt.branch_metadata[version.branch_name]['total_versions'] += 1
    
    async def _detect_merge_conflicts(
        self,
        source_version: ContentVersion,
        target_version: ContentVersion
    ) -> List[MergeConflict]:
        """Detect conflicts between two versions"""
        conflicts = []
        
        # Load content data
        source_content = await self._load_content_data(source_version.file_path)
        target_content = await self._load_content_data(target_version.file_path)
        
        # Check for content conflicts
        if source_version.content_hash != target_version.content_hash:
            # Detailed conflict analysis based on content type
            content_conflicts = await self._analyze_content_conflicts(
                source_content, target_content, source_version.content_type
            )
            
            for conflict_data in content_conflicts:
                conflict = MergeConflict(
                    conflict_id=str(uuid.uuid4()),
                    content_id=source_version.content_id,
                    source_version_id=source_version.version_id,
                    target_version_id=target_version.version_id,
                    conflict_type=ConflictType.CONTENT_CONFLICT,
                    description=conflict_data['description'],
                    conflicting_sections=conflict_data['sections'],
                    suggested_resolution=conflict_data.get('suggestion', {}),
                    resolution_options=conflict_data.get('options', [])
                )
                conflicts.append(conflict)
        
        # Check metadata conflicts
        metadata_conflicts = await self._check_metadata_conflicts(
            source_version, target_version
        )
        conflicts.extend(metadata_conflicts)
        
        # Check dependency conflicts
        dependency_conflicts = await self._check_dependency_conflicts(
            source_version, target_version
        )
        conflicts.extend(dependency_conflicts)
        
        return conflicts
    
    async def _analyze_content_conflicts(
        self,
        source_content: Dict[str, Any],
        target_content: Dict[str, Any],
        content_type: ContentType
    ) -> List[Dict[str, Any]]:
        """Analyze content-specific conflicts"""
        conflicts = []
        
        if content_type == ContentType.TEXT:
            # Text content conflicts
            source_text = source_content.get('text', '')
            target_text = target_content.get('text', '')
            
            if source_text != target_text:
                conflicts.append({
                    'description': 'Text content differs between versions',
                    'sections': [
                        {'type': 'text', 'source': source_text, 'target': target_text}
                    ],
                    'suggestion': {'strategy': 'manual_merge'},
                    'options': [
                        {'name': 'Use source', 'action': 'use_source'},
                        {'name': 'Use target', 'action': 'use_target'},
                        {'name': 'Manual merge', 'action': 'manual_merge'}
                    ]
                })
        
        elif content_type == ContentType.AUDIO:
            # Audio content conflicts
            source_audio = source_content.get('audio_data', {})
            target_audio = target_content.get('audio_data', {})
            
            # Check timing differences
            if source_audio.get('duration') != target_audio.get('duration'):
                conflicts.append({
                    'description': 'Audio duration differs',
                    'sections': [
                        {
                            'type': 'duration',
                            'source': source_audio.get('duration'),
                            'target': target_audio.get('duration')
                        }
                    ],
                    'suggestion': {'strategy': 'use_longer_duration'},
                    'options': [
                        {'name': 'Use source duration', 'action': 'use_source'},
                        {'name': 'Use target duration', 'action': 'use_target'}
                    ]
                })
            
            # Check track differences
            source_tracks = source_audio.get('tracks', [])
            target_tracks = target_audio.get('tracks', [])
            
            if len(source_tracks) != len(target_tracks):
                conflicts.append({
                    'description': 'Different number of audio tracks',
                    'sections': [
                        {
                            'type': 'track_count',
                            'source': len(source_tracks),
                            'target': len(target_tracks)
                        }
                    ],
                    'suggestion': {'strategy': 'merge_tracks'},
                    'options': [
                        {'name': 'Use source tracks', 'action': 'use_source'},
                        {'name': 'Use target tracks', 'action': 'use_target'},
                        {'name': 'Merge all tracks', 'action': 'merge_tracks'}
                    ]
                })
        
        elif content_type == ContentType.VIDEO:
            # Video content conflicts
            source_video = source_content.get('video_data', {})
            target_video = target_content.get('video_data', {})
            
            # Check resolution differences
            if source_video.get('resolution') != target_video.get('resolution'):
                conflicts.append({
                    'description': 'Video resolution differs',
                    'sections': [
                        {
                            'type': 'resolution',
                            'source': source_video.get('resolution'),
                            'target': target_video.get('resolution')
                        }
                    ],
                    'suggestion': {'strategy': 'use_higher_resolution'},
                    'options': [
                        {'name': 'Use source resolution', 'action': 'use_source'},
                        {'name': 'Use target resolution', 'action': 'use_target'}
                    ]
                })
        
        return conflicts
    
    async def _check_metadata_conflicts(
        self,
        source_version: ContentVersion,
        target_version: ContentVersion
    ) -> List[MergeConflict]:
        """Check for metadata conflicts"""
        conflicts = []
        
        # Compare metadata
        source_meta = source_version.metadata
        target_meta = target_version.metadata
        
        # Find conflicting keys
        conflicting_keys = []
        for key in set(source_meta.keys()) & set(target_meta.keys()):
            if source_meta[key] != target_meta[key]:
                conflicting_keys.append(key)
        
        if conflicting_keys:
            conflict = MergeConflict(
                conflict_id=str(uuid.uuid4()),
                content_id=source_version.content_id,
                source_version_id=source_version.version_id,
                target_version_id=target_version.version_id,
                conflict_type=ConflictType.METADATA_CONFLICT,
                description=f"Metadata conflicts in keys: {', '.join(conflicting_keys)}",
                conflicting_sections=[
                    {
                        'key': key,
                        'source_value': source_meta[key],
                        'target_value': target_meta[key]
                    }
                    for key in conflicting_keys
                ],
                resolution_options=[
                    {'name': 'Use source metadata', 'action': 'use_source'},
                    {'name': 'Use target metadata', 'action': 'use_target'},
                    {'name': 'Manual merge', 'action': 'manual_merge'}
                ]
            )
            conflicts.append(conflict)
        
        return conflicts
    
    async def _check_dependency_conflicts(
        self,
        source_version: ContentVersion,
        target_version: ContentVersion
    ) -> List[MergeConflict]:
        """Check for dependency conflicts"""
        conflicts = []
        
        source_deps = set(source_version.dependencies)
        target_deps = set(target_version.dependencies)
        
        # Find conflicting dependencies
        if source_deps != target_deps:
            conflict = MergeConflict(
                conflict_id=str(uuid.uuid4()),
                content_id=source_version.content_id,
                source_version_id=source_version.version_id,
                target_version_id=target_version.version_id,
                conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                description="Dependency lists differ between versions",
                conflicting_sections=[
                    {
                        'type': 'dependencies',
                        'source_only': list(source_deps - target_deps),
                        'target_only': list(target_deps - source_deps),
                        'common': list(source_deps & target_deps)
                    }
                ],
                resolution_options=[
                    {'name': 'Use source dependencies', 'action': 'use_source'},
                    {'name': 'Use target dependencies', 'action': 'use_target'},
                    {'name': 'Merge dependencies', 'action': 'merge_deps'}
                ]
            )
            conflicts.append(conflict)
        
        return conflicts
    
    async def _perform_merge(
        self,
        source_version: ContentVersion,
        target_version: ContentVersion,
        strategy: MergeStrategy,
        merger_id: str,
        conflicts: List[MergeConflict]
    ) -> Optional[ContentVersion]:
        """Perform automatic merge based on strategy"""
        try:
            # Load content data
            source_content = await self._load_content_data(source_version.file_path)
            target_content = await self._load_content_data(target_version.file_path)
            
            merged_content = {}
            
            if strategy == MergeStrategy.SMART_MERGE:
                merged_content = await self._smart_merge_content(
                    source_content, target_content, source_version.content_type, conflicts
                )
            elif strategy == MergeStrategy.LAST_WRITER_WINS:
                merged_content = target_content  # Target is newer
            elif strategy == MergeStrategy.FIRST_WRITER_WINS:
                merged_content = source_content  # Source is older
            else:
                # Cannot auto-merge with this strategy
                return None
            
            if not merged_content:
                return None
            
            # Create merged version
            merged_version = await self.create_version(
                content_id=source_version.content_id,
                title=f"Merge {source_version.branch_name} -> {target_version.branch_name}",
                content_type=source_version.content_type,
                creator_id=merger_id,
                content_data=merged_content,
                parent_version_id=target_version.version_id,
                branch_name=target_version.branch_name,
                description=f"Automatic merge using {strategy.value} strategy"
            )
            
            # Add merge metadata
            merged_version.metadata['merge_info'] = {
                'source_version': source_version.version_id,
                'target_version': target_version.version_id,
                'merge_strategy': strategy.value,
                'conflicts_resolved': len(conflicts),
                'merge_timestamp': datetime.now().isoformat()
            }
            
            return merged_version
            
        except Exception as e:
            logger.error(f"Merge failed: {str(e)}")
            return None
    
    async def _smart_merge_content(
        self,
        source_content: Dict[str, Any],
        target_content: Dict[str, Any],
        content_type: ContentType,
        conflicts: List[MergeConflict]
    ) -> Dict[str, Any]:
        """Perform smart merge based on content type"""
        merged_content = target_content.copy()  # Start with target
        
        if content_type == ContentType.TEXT:
            # For text, try to merge non-conflicting parts
            source_text = source_content.get('text', '')
            target_text = target_content.get('text', '')
            
            # Simple line-based merge (in reality, would use more sophisticated algorithms)
            if source_text != target_text:
                merged_content['text'] = target_text  # Default to target
                merged_content['merge_notes'] = 'Text merged with target version'
        
        elif content_type == ContentType.AUDIO:
            # For audio, merge tracks intelligently
            source_audio = source_content.get('audio_data', {})
            target_audio = target_content.get('audio_data', {})
            
            # Merge track lists
            source_tracks = source_audio.get('tracks', [])
            target_tracks = target_audio.get('tracks', [])
            
            # Combine unique tracks
            all_tracks = target_tracks.copy()
            for track in source_tracks:
                if track not in all_tracks:
                    all_tracks.append(track)
            
            merged_content['audio_data'] = target_audio.copy()
            merged_content['audio_data']['tracks'] = all_tracks
        
        # Merge metadata intelligently
        source_meta = source_content.get('metadata', {})
        target_meta = target_content.get('metadata', {})
        
        merged_meta = target_meta.copy()
        for key, value in source_meta.items():
            if key not in merged_meta:
                merged_meta[key] = value
        
        merged_content['metadata'] = merged_meta
        
        return merged_content
    
    async def _apply_conflict_resolution(
        self,
        conflict: MergeConflict,
        resolution: ConflictResolution
    ):
        """Apply conflict resolution to create final merged version"""
        # Load the conflicting versions
        source_version = self.content_versions[conflict.source_version_id]
        target_version = self.content_versions[conflict.target_version_id]
        
        # Apply resolution strategy
        # This would create a new merged version with the resolution applied
        # Implementation depends on specific resolution strategy
        
        logger.info(f"Applied resolution {resolution.resolution_id} for conflict {conflict.conflict_id}")
    
    async def _compare_content(
        self,
        content_1: Dict[str, Any],
        content_2: Dict[str, Any],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Compare content and return differences"""
        differences = {}
        
        if content_type == ContentType.TEXT:
            text_1 = content_1.get('text', '')
            text_2 = content_2.get('text', '')
            
            # Simple text comparison
            if text_1 == text_2:
                differences['text_identical'] = True
                differences['similarity_score'] = 1.0
            else:
                differences['text_identical'] = False
                
                # Calculate simple similarity (character-based)
                max_len = max(len(text_1), len(text_2))
                if max_len > 0:
                    # Simple Levenshtein-like similarity
                    common_chars = sum(1 for a, b in zip(text_1, text_2) if a == b)
                    differences['similarity_score'] = common_chars / max_len
                else:
                    differences['similarity_score'] = 0.0
                
                differences['length_diff'] = len(text_2) - len(text_1)
        
        elif content_type == ContentType.AUDIO:
            audio_1 = content_1.get('audio_data', {})
            audio_2 = content_2.get('audio_data', {})
            
            differences['duration_diff'] = (
                audio_2.get('duration', 0) - audio_1.get('duration', 0)
            )
            differences['track_count_diff'] = (
                len(audio_2.get('tracks', [])) - len(audio_1.get('tracks', []))
            )
            
            # Calculate audio similarity based on properties
            properties_same = 0
            total_properties = 0
            
            for prop in ['sample_rate', 'bit_rate', 'channels']:
                total_properties += 1
                if audio_1.get(prop) == audio_2.get(prop):
                    properties_same += 1
            
            differences['similarity_score'] = (
                properties_same / total_properties if total_properties > 0 else 0
            )
        
        # Compare metadata
        meta_1 = content_1.get('metadata', {})
        meta_2 = content_2.get('metadata', {})
        
        common_keys = set(meta_1.keys()) & set(meta_2.keys())
        all_keys = set(meta_1.keys()) | set(meta_2.keys())
        
        if all_keys:
            metadata_similarity = len(common_keys) / len(all_keys)
            differences['metadata_similarity'] = metadata_similarity
        
        return differences
    
    async def get_version_metrics(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive version metrics for content"""
        if content_id not in self.version_histories:
            return {}
        
        history = self.version_histories[content_id]
        versions = history.versions
        
        if not versions:
            return {}
        
        # Calculate metrics
        total_versions = len(versions)
        total_branches = len(history.branches)
        total_merges = len(history.merge_history)
        
        # Version frequency
        creation_times = [v.created_at for v in versions]
        creation_times.sort()
        
        if len(creation_times) > 1:
            time_diffs = [
                (creation_times[i] - creation_times[i-1]).total_seconds() / 3600
                for i in range(1, len(creation_times))
            ]
            avg_version_interval = sum(time_diffs) / len(time_diffs)
        else:
            avg_version_interval = 0
        
        # Creator statistics
        creators = defaultdict(int)
        for version in versions:
            creators[version.creator_id] += 1
        
        # Content type distribution
        content_types = defaultdict(int)
        for version in versions:
            content_types[version.content_type.value] += 1
        
        return {
            'content_id': content_id,
            'total_versions': total_versions,
            'total_branches': total_branches,
            'total_merges': total_merges,
            'avg_version_interval_hours': avg_version_interval,
            'creator_distribution': dict(creators),
            'content_type_distribution': dict(content_types),
            'latest_version': history.latest_version,
            'first_version_date': creation_times[0].isoformat() if creation_times else None,
            'last_version_date': creation_times[-1].isoformat() if creation_times else None
        }


# Export main classes
__all__ = [
    'VersionController',
    'ContentVersion',
    'VersionHistory',
    'MergeConflict',
    'ConflictResolution',
    'BranchManagement',
    'BranchOperation',
    'ContentType',
    'VersionStatus',
    'MergeStrategy',
    'ConflictType'
]