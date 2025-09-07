"""Version Control System - Advanced Media Asset Version Management

Enterprise-grade version control system for managing media assets, tracking changes,
handling collaborative editing, and maintaining comprehensive audit trails.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

LEGAL WARNING: This code is the exclusive property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import json
import logging
import hashlib
import mimetypes
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from pathlib import Path
import uuid
import shutil
import os
from collections import defaultdict

# External dependencies with graceful fallbacks
try:
    import git
    HAS_GIT = True
except ImportError:
    HAS_GIT = False
    logging.warning("GitPython not available - using basic version control")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL not available - image comparison limited")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logging.warning("Librosa not available - audio analysis limited")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VersionOperation(Enum):
    """Version operation types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RENAME = "rename"
    MOVE = "move"
    MERGE = "merge"
    BRANCH = "branch"
    TAG = "tag"


class AssetType(Enum):
    """Media asset types"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    PROJECT = "project"
    TEMPLATE = "template"
    PRESET = "preset"
    SCRIPT = "script"


class VersionStatus(Enum):
    """Version status types"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    MANUAL = "manual"
    AUTO_MERGE = "auto_merge"
    LATEST_WINS = "latest_wins"
    CREATOR_PRIORITY = "creator_priority"
    QUALITY_BASED = "quality_based"


@dataclass
class AssetMetadata:
    """Asset metadata information"""
    file_size: int
    mime_type: str
    checksum: str
    dimensions: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    color_profile: Optional[str] = None
    sample_rate: Optional[int] = None
    created_with: Optional[str] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VersionDiff:
    """Version difference information"""
    added_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    deleted_files: List[str] = field(default_factory=list)
    renamed_files: List[Tuple[str, str]] = field(default_factory=list)
    metadata_changes: Dict[str, Any] = field(default_factory=dict)
    size_delta: int = 0
    quality_delta: Optional[float] = None


@dataclass
class AssetVersion:
    """Individual asset version"""
    id: str
    asset_id: str
    version_number: str
    file_path: str
    created_by: str
    created_at: datetime
    
    # Version information
    operation: VersionOperation
    message: str
    tags: List[str] = field(default_factory=list)
    status: VersionStatus = VersionStatus.DRAFT
    
    # Asset information
    metadata: Optional[AssetMetadata] = None
    parent_version: Optional[str] = None
    merge_parents: List[str] = field(default_factory=list)
    
    # Collaboration
    reviewed_by: List[str] = field(default_factory=list)
    approved_by: Optional[str] = None
    comments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Storage
    storage_path: Optional[str] = None
    backup_paths: List[str] = field(default_factory=list)
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AssetBranch:
    """Asset branch for parallel development"""
    id: str
    name: str
    asset_id: str
    created_by: str
    created_at: datetime
    
    # Branch information
    base_version: str
    head_version: str
    description: str
    purpose: str
    
    # Collaboration
    collaborators: List[str] = field(default_factory=list)
    protected: bool = False
    merge_strategy: ConflictResolution = ConflictResolution.MANUAL
    
    # Status
    active: bool = True
    merged_at: Optional[datetime] = None
    merged_by: Optional[str] = None
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MergeConflict:
    """Merge conflict information"""
    id: str
    asset_id: str
    source_branch: str
    target_branch: str
    conflicting_files: List[str]
    conflict_type: str
    detected_at: datetime
    
    # Resolution
    resolution_strategy: Optional[ConflictResolution] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
    
    # Metadata
    severity: str = "medium"
    auto_resolvable: bool = False


@dataclass
class MediaAsset:
    """Media asset with version control"""
    id: str
    name: str
    type: AssetType
    project_id: Optional[str]
    created_by: str
    created_at: datetime
    
    # Version control
    current_version: Optional[str] = None
    versions: List[AssetVersion] = field(default_factory=list)
    branches: List[AssetBranch] = field(default_factory=list)
    
    # Collaboration
    collaborators: List[str] = field(default_factory=list)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    
    # Storage and organization
    storage_location: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    license: Optional[str] = None
    copyright_holder: Optional[str] = None
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MediaVersionControl:
    """Advanced media version control system"""
    
    def __init__(self, storage_root: str, enable_git: bool = True):
        """Initialize version control system
        
        Args:
            storage_root: Root directory for asset storage
            enable_git: Whether to use Git for version control
        """
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        self.assets: Dict[str, MediaAsset] = {}
        self.active_branches: Dict[str, Dict[str, str]] = defaultdict(dict)
        self.conflict_queue: List[MergeConflict] = []
        
        # Git integration
        self.git_repo = None
        if enable_git and HAS_GIT:
            try:
                self.git_repo = git.Repo.init(self.storage_root)
                logger.info("Initialized Git repository for version control")
            except Exception as e:
                logger.warning(f"Failed to initialize Git repo: {e}")
        
        logger.info(f"MediaVersionControl initialized at {self.storage_root}")
    
    async def create_asset(self, asset_data: Dict[str, Any], file_path: Optional[str] = None) -> str:
        """Create a new media asset
        
        Args:
            asset_data: Asset information
            file_path: Optional file to import
            
        Returns:
            Asset ID
        """
        try:
            asset_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # Create asset
            asset = MediaAsset(
                id=asset_id,
                name=asset_data["name"],
                type=AssetType(asset_data["type"]),
                project_id=asset_data.get("project_id"),
                created_by=asset_data["created_by"],
                created_at=now,
                description=asset_data.get("description", ""),
                tags=asset_data.get("tags", []),
                categories=asset_data.get("categories", [])
            )
            
            # Set up storage location
            asset_dir = self.storage_root / asset_id
            asset_dir.mkdir(parents=True, exist_ok=True)
            asset.storage_location = str(asset_dir)
            
            # Create initial version if file provided
            if file_path and Path(file_path).exists():
                version_id = await self._create_initial_version(asset, file_path)
                asset.current_version = version_id
            
            # Set up permissions
            asset.permissions[asset.created_by] = ["read", "write", "admin"]
            
            # Store asset
            self.assets[asset_id] = asset
            
            # Git commit
            if self.git_repo:
                try:
                    self.git_repo.index.add([str(asset_dir)])
                    self.git_repo.index.commit(f"Created asset: {asset.name}")
                except Exception as e:
                    logger.warning(f"Git commit failed: {e}")
            
            logger.info(f"Created asset {asset_id}: {asset.name}")
            return asset_id
            
        except Exception as e:
            logger.error(f"Error creating asset: {e}")
            raise
    
    async def create_version(self, asset_id: str, file_path: str, message: str, 
                           created_by: str, operation: VersionOperation = VersionOperation.UPDATE) -> str:
        """Create a new version of an asset
        
        Args:
            asset_id: Asset identifier
            file_path: Path to new file
            message: Version message
            created_by: Creator identifier
            operation: Version operation type
            
        Returns:
            Version ID
        """
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self._check_permission(asset, created_by, "write"):
                raise PermissionError(f"User {created_by} lacks write permission")
            
            version_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # Determine version number
            version_number = self._generate_version_number(asset)
            
            # Copy file to asset storage
            storage_dir = Path(asset.storage_location) / "versions"
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            file_extension = Path(file_path).suffix
            version_file = storage_dir / f"{version_number}{file_extension}"
            shutil.copy2(file_path, version_file)
            
            # Extract metadata
            metadata = await self._extract_metadata(version_file)
            
            # Create version
            version = AssetVersion(
                id=version_id,
                asset_id=asset_id,
                version_number=version_number,
                file_path=str(version_file),
                created_by=created_by,
                created_at=now,
                operation=operation,
                message=message,
                metadata=metadata,
                parent_version=asset.current_version,
                storage_path=str(version_file)
            )
            
            # Add to asset
            asset.versions.append(version)
            asset.current_version = version_id
            asset.updated_at = now
            
            # Git commit
            if self.git_repo:
                try:
                    self.git_repo.index.add([str(version_file)])
                    self.git_repo.index.commit(f"{operation.value}: {message}")
                except Exception as e:
                    logger.warning(f"Git commit failed: {e}")
            
            logger.info(f"Created version {version_number} for asset {asset_id}")
            return version_id
            
        except Exception as e:
            logger.error(f"Error creating version: {e}")
            raise
    
    async def create_branch(self, asset_id: str, branch_name: str, description: str, 
                          created_by: str, base_version: Optional[str] = None) -> str:
        """Create a new branch for parallel development
        
        Args:
            asset_id: Asset identifier
            branch_name: Branch name
            description: Branch description
            created_by: Creator identifier
            base_version: Base version ID (defaults to current)
            
        Returns:
            Branch ID
        """
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self._check_permission(asset, created_by, "write"):
                raise PermissionError(f"User {created_by} lacks write permission")
            
            # Use current version as base if not specified
            if not base_version:
                base_version = asset.current_version
            
            if not base_version:
                raise ValueError("No base version available")
            
            branch_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # Create branch
            branch = AssetBranch(
                id=branch_id,
                name=branch_name,
                asset_id=asset_id,
                created_by=created_by,
                created_at=now,
                base_version=base_version,
                head_version=base_version,
                description=description,
                purpose=description
            )
            
            # Add to asset
            asset.branches.append(branch)
            asset.updated_at = now
            
            # Track active branch
            self.active_branches[asset_id][created_by] = branch_id
            
            logger.info(f"Created branch {branch_name} for asset {asset_id}")
            return branch_id
            
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            raise
    
    async def merge_branch(self, asset_id: str, source_branch_id: str, target_branch: str = "main",
                         merged_by: str, resolution_strategy: ConflictResolution = ConflictResolution.MANUAL) -> bool:
        """Merge a branch into target branch
        
        Args:
            asset_id: Asset identifier
            source_branch_id: Source branch ID
            target_branch: Target branch name
            merged_by: User performing merge
            resolution_strategy: Conflict resolution strategy
            
        Returns:
            Success status
        """
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self._check_permission(asset, merged_by, "write"):
                raise PermissionError(f"User {merged_by} lacks write permission")
            
            # Find source branch
            source_branch = next((b for b in asset.branches if b.id == source_branch_id), None)
            if not source_branch:
                raise ValueError(f"Source branch {source_branch_id} not found")
            
            # Check for conflicts
            conflicts = await self._detect_conflicts(asset, source_branch, target_branch)
            
            if conflicts and resolution_strategy == ConflictResolution.MANUAL:
                # Add to conflict queue
                conflict = MergeConflict(
                    id=str(uuid.uuid4()),
                    asset_id=asset_id,
                    source_branch=source_branch.name,
                    target_branch=target_branch,
                    conflicting_files=[],  # Simplified for this implementation
                    conflict_type="version_conflict",
                    detected_at=datetime.now(timezone.utc),
                    resolution_strategy=resolution_strategy
                )
                self.conflict_queue.append(conflict)
                logger.warning(f"Merge conflicts detected - added to resolution queue")
                return False
            
            # Perform merge
            await self._perform_merge(asset, source_branch, target_branch, resolution_strategy)
            
            # Mark branch as merged
            source_branch.merged_at = datetime.now(timezone.utc)
            source_branch.merged_by = merged_by
            source_branch.active = False
            
            # Git merge (simplified)
            if self.git_repo:
                try:
                    self.git_repo.index.commit(f"Merged branch {source_branch.name} into {target_branch}")
                except Exception as e:
                    logger.warning(f"Git merge commit failed: {e}")
            
            logger.info(f"Successfully merged branch {source_branch.name} into {target_branch}")
            return True
            
        except Exception as e:
            logger.error(f"Error merging branch: {e}")
            return False
    
    async def get_version_history(self, asset_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get version history for an asset
        
        Args:
            asset_id: Asset identifier
            limit: Maximum number of versions to return
            
        Returns:
            Version history
        """
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                return []
            
            # Sort versions by creation date (newest first)
            sorted_versions = sorted(asset.versions, key=lambda v: v.created_at, reverse=True)
            
            history = []
            for version in sorted_versions[:limit]:
                history.append({
                    "id": version.id,
                    "version_number": version.version_number,
                    "operation": version.operation.value,
                    "message": version.message,
                    "created_by": version.created_by,
                    "created_at": version.created_at.isoformat(),
                    "status": version.status.value,
                    "tags": version.tags,
                    "file_size": version.metadata.file_size if version.metadata else 0,
                    "parent_version": version.parent_version
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting version history: {e}")
            return []
    
    async def compare_versions(self, asset_id: str, version1_id: str, version2_id: str) -> VersionDiff:
        """Compare two versions of an asset
        
        Args:
            asset_id: Asset identifier
            version1_id: First version ID
            version2_id: Second version ID
            
        Returns:
            Version difference information
        """
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Find versions
            version1 = next((v for v in asset.versions if v.id == version1_id), None)
            version2 = next((v for v in asset.versions if v.id == version2_id), None)
            
            if not version1 or not version2:
                raise ValueError("One or both versions not found")
            
            # Calculate differences
            diff = VersionDiff()
            
            if version1.metadata and version2.metadata:
                diff.size_delta = version2.metadata.file_size - version1.metadata.file_size
                
                # Metadata changes
                if version1.metadata.dimensions != version2.metadata.dimensions:
                    diff.metadata_changes["dimensions"] = {
                        "old": version1.metadata.dimensions,
                        "new": version2.metadata.dimensions
                    }
                
                if version1.metadata.duration != version2.metadata.duration:
                    diff.metadata_changes["duration"] = {
                        "old": version1.metadata.duration,
                        "new": version2.metadata.duration
                    }
            
            # File changes (simplified)
            if version1.file_path != version2.file_path:
                diff.modified_files.append(Path(version2.file_path).name)
            
            return diff
            
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return VersionDiff()
    
    async def restore_version(self, asset_id: str, version_id: str, restored_by: str) -> bool:
        """Restore an asset to a previous version
        
        Args:
            asset_id: Asset identifier
            version_id: Version to restore
            restored_by: User performing restoration
            
        Returns:
            Success status
        """
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                return False
            
            # Check permissions
            if not self._check_permission(asset, restored_by, "write"):
                raise PermissionError(f"User {restored_by} lacks write permission")
            
            # Find version to restore
            restore_version = next((v for v in asset.versions if v.id == version_id), None)
            if not restore_version:
                return False
            
            # Create new version from restored file
            new_version_id = await self.create_version(
                asset_id,
                restore_version.file_path,
                f"Restored to version {restore_version.version_number}",
                restored_by,
                VersionOperation.UPDATE
            )
            
            logger.info(f"Restored asset {asset_id} to version {restore_version.version_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring version: {e}")
            return False
    
    async def get_asset_status(self, asset_id: str) -> Dict[str, Any]:
        """Get comprehensive asset status
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Asset status information
        """
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                return {}
            
            current_version = None
            if asset.current_version:
                current_version = next((v for v in asset.versions if v.id == asset.current_version), None)
            
            status = {
                "asset": {
                    "id": asset.id,
                    "name": asset.name,
                    "type": asset.type.value,
                    "created_by": asset.created_by,
                    "created_at": asset.created_at.isoformat(),
                    "description": asset.description,
                    "tags": asset.tags,
                    "categories": asset.categories
                },
                "version_control": {
                    "total_versions": len(asset.versions),
                    "current_version": current_version.version_number if current_version else None,
                    "active_branches": len([b for b in asset.branches if b.active]),
                    "total_branches": len(asset.branches)
                },
                "collaboration": {
                    "collaborators": asset.collaborators,
                    "permissions": asset.permissions
                },
                "storage": {
                    "location": asset.storage_location,
                    "total_size": sum(v.metadata.file_size for v in asset.versions if v.metadata)
                }
            }
            
            # Add current version details
            if current_version:
                status["current_version"] = {
                    "id": current_version.id,
                    "number": current_version.version_number,
                    "created_by": current_version.created_by,
                    "created_at": current_version.created_at.isoformat(),
                    "message": current_version.message,
                    "status": current_version.status.value,
                    "file_size": current_version.metadata.file_size if current_version.metadata else 0
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting asset status: {e}")
            return {}
    
    async def _create_initial_version(self, asset: MediaAsset, file_path: str) -> str:
        """Create initial version from file"""
        version_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Copy file to asset storage
        storage_dir = Path(asset.storage_location) / "versions"
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = Path(file_path).suffix
        version_file = storage_dir / f"1.0{file_extension}"
        shutil.copy2(file_path, version_file)
        
        # Extract metadata
        metadata = await self._extract_metadata(version_file)
        
        # Create version
        version = AssetVersion(
            id=version_id,
            asset_id=asset.id,
            version_number="1.0",
            file_path=str(version_file),
            created_by=asset.created_by,
            created_at=now,
            operation=VersionOperation.CREATE,
            message="Initial version",
            metadata=metadata,
            storage_path=str(version_file)
        )
        
        asset.versions.append(version)
        return version_id
    
    async def _extract_metadata(self, file_path: Path) -> AssetMetadata:
        """Extract metadata from file"""
        file_stat = file_path.stat()
        file_size = file_stat.st_size
        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        
        # Calculate checksum
        with open(file_path, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        
        metadata = AssetMetadata(
            file_size=file_size,
            mime_type=mime_type,
            checksum=checksum
        )
        
        # Extract media-specific metadata
        if mime_type.startswith('image/') and HAS_PIL:
            try:
                with Image.open(file_path) as img:
                    metadata.dimensions = img.size
                    metadata.color_profile = img.mode
            except Exception as e:
                logger.warning(f"Failed to extract image metadata: {e}")
        
        elif mime_type.startswith('audio/') and HAS_LIBROSA:
            try:
                y, sr = librosa.load(str(file_path))
                metadata.duration = len(y) / sr
                metadata.sample_rate = sr
            except Exception as e:
                logger.warning(f"Failed to extract audio metadata: {e}")
        
        return metadata
    
    def _generate_version_number(self, asset: MediaAsset) -> str:
        """Generate next version number"""
        if not asset.versions:
            return "1.0"
        
        # Find highest version number
        versions = [v.version_number for v in asset.versions]
        versions.sort(key=lambda x: [int(i) for i in x.split('.')])
        
        latest = versions[-1].split('.')
        major, minor = int(latest[0]), int(latest[1])
        
        # Increment minor version
        return f"{major}.{minor + 1}"
    
    def _check_permission(self, asset: MediaAsset, user: str, permission: str) -> bool:
        """Check user permissions on asset"""
        user_permissions = asset.permissions.get(user, [])
        return permission in user_permissions or "admin" in user_permissions
    
    async def _detect_conflicts(self, asset: MediaAsset, source_branch: AssetBranch, target_branch: str) -> List[str]:
        """Detect merge conflicts"""
        # Simplified conflict detection
        conflicts = []
        
        # Check if both branches have been modified since divergence
        source_head = next((v for v in asset.versions if v.id == source_branch.head_version), None)
        base_version = next((v for v in asset.versions if v.id == source_branch.base_version), None)
        
        if source_head and base_version:
            # Check if target has been modified since base
            target_versions = [v for v in asset.versions if v.created_at > base_version.created_at]
            if target_versions:
                conflicts.append("concurrent_modifications")
        
        return conflicts
    
    async def _perform_merge(self, asset: MediaAsset, source_branch: AssetBranch, 
                           target_branch: str, resolution_strategy: ConflictResolution):
        """Perform branch merge"""
        # Simplified merge implementation
        # In a real implementation, this would handle actual file merging
        
        source_head = next((v for v in asset.versions if v.id == source_branch.head_version), None)
        if source_head:
            # Update current version to source head
            asset.current_version = source_head.id
            asset.updated_at = datetime.now(timezone.utc)


# Convenience functions for easy usage
async def create_version_controlled_asset(name: str, asset_type: str, file_path: str, 
                                        created_by: str, storage_root: str = "./media_storage") -> str:
    """Create a new version-controlled media asset
    
    Args:
        name: Asset name
        asset_type: Asset type
        file_path: Initial file path
        created_by: Creator identifier
        storage_root: Storage root directory
        
    Returns:
        Asset ID
    """
    vc = MediaVersionControl(storage_root)
    
    asset_data = {
        "name": name,
        "type": asset_type,
        "created_by": created_by,
        "description": f"Version-controlled {asset_type} asset"
    }
    
    return await vc.create_asset(asset_data, file_path)


async def update_asset_version(asset_id: str, new_file_path: str, message: str, 
                             updated_by: str, storage_root: str = "./media_storage") -> str:
    """Update asset with new version
    
    Args:
        asset_id: Asset identifier
        new_file_path: Path to new file
        message: Update message
        updated_by: User making update
        storage_root: Storage root directory
        
    Returns:
        Version ID
    """
    vc = MediaVersionControl(storage_root)
    vc.assets = {}  # In real implementation, load from storage
    
    return await vc.create_version(asset_id, new_file_path, message, updated_by)


async def get_asset_history(asset_id: str, storage_root: str = "./media_storage") -> List[Dict[str, Any]]:
    """Get asset version history
    
    Args:
        asset_id: Asset identifier
        storage_root: Storage root directory
        
    Returns:
        Version history
    """
    vc = MediaVersionControl(storage_root)
    vc.assets = {}  # In real implementation, load from storage
    
    return await vc.get_version_history(asset_id)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create version control system
        vc = MediaVersionControl("./test_media_storage")
        
        # Create a new asset
        asset_data = {
            "name": "Project Logo",
            "type": "image",
            "created_by": "designer_1",
            "description": "Company logo for marketing materials",
            "tags": ["logo", "branding", "marketing"]
        }
        
        # For demo purposes, create a dummy file
        dummy_file = Path("./test_logo.png")
        dummy_file.write_text("dummy image content")
        
        asset_id = await vc.create_asset(asset_data, str(dummy_file))
        print(f"Created asset: {asset_id}")
        
        # Create a new version
        version_id = await vc.create_version(
            asset_id,
            str(dummy_file),
            "Updated logo with new colors",
            "designer_1"
        )
        print(f"Created version: {version_id}")
        
        # Create a branch
        branch_id = await vc.create_branch(
            asset_id,
            "experimental",
            "Experimental design variations",
            "designer_2"
        )
        print(f"Created branch: {branch_id}")
        
        # Get asset status
        status = await vc.get_asset_status(asset_id)
        print(f"Asset status: {json.dumps(status, indent=2, default=str)}")
        
        # Cleanup
        dummy_file.unlink(missing_ok=True)
    
    asyncio.run(main())