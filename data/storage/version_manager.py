"""Professional Version Manager - IA Influencer Agent Platform
===========================================================
Module: backend/data/storage/version_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Data Storage Core - Version Control Management
Responsibility: Content versioning, rollback, and change tracking for creators
Technologies: Python, Git-like versioning, Delta compression, Conflict resolution
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior + ML Engineer: Expertise multi-domaines  
- Audio + DevOps + DBA + Sécurité: Compétences industrielles
- Microservices + IA Prompt Engineer: Innovation avancée

LOGIQUE MÉTIER:
Content Creation → Version Tracking → Change Detection → 
Delta Storage → Conflict Resolution → Rollback Support → 
Branch Management → Collaboration History → Audit Trail
"""
import asyncio
import logging
import hashlib
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import aiofiles
import difflib
import gzip
import base64
from collections import defaultdict
import copy

# For binary file diffing
import bsdiff4

logger = logging.getLogger(__name__)


class VersionType(Enum):
    """Version type enumeration"""
    INITIAL = "initial"
    MINOR = "minor"
    MAJOR = "major"
    HOTFIX = "hotfix"
    BRANCH = "branch"
    MERGE = "merge"
    ROLLBACK = "rollback"


class ChangeType(Enum):
    """Change type enumeration"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RENAME = "rename"
    MOVE = "move"
    COPY = "copy"
    METADATA_CHANGE = "metadata_change"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    AUTO_MERGE = "auto_merge"
    PREFER_LOCAL = "prefer_local"
    PREFER_REMOTE = "prefer_remote"
    MANUAL_RESOLUTION = "manual_resolution"
    CREATE_BRANCH = "create_branch"


@dataclass
class VersionInfo:
    """Comprehensive version information"""
    version_id: str
    file_id: str
    version_number: str
    version_type: VersionType
    parent_version: Optional[str]
    
    # Change information
    change_type: ChangeType
    change_description: str
    changed_by: str
    change_timestamp: datetime
    
    # File information
    file_size: int
    file_hash: str
    content_hash: str
    
    # Storage information
    storage_path: str
    delta_path: Optional[str] = None
    compression_ratio: Optional[float] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Collaboration
    branch_name: str = "main"
    merge_base: Optional[str] = None
    conflicts_resolved: List[str] = field(default_factory=list)
    
    # Performance
    creation_time: float = 0.0
    storage_efficiency: float = 0.0


@dataclass
class VersionDelta:
    """Version delta/difference information"""
    from_version: str
    to_version: str
    delta_type: str  # "binary", "text", "metadata"
    delta_size: int
    compression_ratio: float
    delta_data: bytes
    checksum: str


@dataclass
class BranchInfo:
    """Branch information for parallel development"""
    branch_id: str
    branch_name: str
    created_by: str
    created_at: datetime
    parent_branch: str
    head_version: str
    
    # Branch status
    is_active: bool = True
    is_merged: bool = False
    merge_target: Optional[str] = None
    
    # Statistics
    commit_count: int = 0
    last_activity: Optional[datetime] = None
    contributors: List[str] = field(default_factory=list)


@dataclass
class MergeResult:
    """Result of merge operation"""
    success: bool
    merged_version_id: str
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    resolution_strategy: Optional[ConflictResolution] = None
    merge_timestamp: datetime = field(default_factory=datetime.now)
    merged_by: str = ""


@dataclass
class VersionComparison:
    """Comparison between two versions"""
    version_a: str
    version_b: str
    differences: List[Dict[str, Any]]
    similarity_score: float
    total_changes: int
    comparison_timestamp: datetime = field(default_factory=datetime.now)


class VersionManager:
    """
    Industrial-grade version management system for IA Influencer Agent platform.
    
    Provides Git-like versioning capabilities for content files with advanced
    features like delta compression, conflict resolution, and collaboration support.
    """
    
    def __init__(self, storage_path: Union[str, Path]):
        """
        Initialize VersionManager with storage configuration.
        
        Args:
            storage_path: Base path for version storage
        """
        self.storage_path = Path(storage_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize version storage structure
        self._create_version_structure()
        
        # Version tracking
        self.versions: Dict[str, List[VersionInfo]] = defaultdict(list)
        self.branches: Dict[str, BranchInfo] = {}
        self.active_branches: Dict[str, str] = {}  # file_id -> branch_name
        
        # Performance settings
        self.delta_compression = True
        self.max_versions_per_file = 100
        self.cleanup_threshold_days = 90
        
        # Conflict resolution settings
        self.auto_merge_threshold = 0.95  # Similarity threshold for auto-merge
        self.max_merge_attempts = 3
        
        self.logger.info("🔄 VersionManager initialized with industrial capabilities")
    
    def _create_version_structure(self):
        """Create organized version storage directory structure"""
        directories = [
            "versions/data",
            "versions/deltas", 
            "versions/metadata",
            "versions/branches",
            "versions/merges",
            "versions/conflicts",
            "versions/snapshots",
            "versions/archive",
            "temp/comparison",
            "temp/merge",
            "logs"
        ]
        
        for directory in directories:
            (self.storage_path / directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"📁 Version structure created at {self.storage_path}")
    
    async def create_version(self,
                            file_id: str,
                            file_path: Union[str, Path],
                            change_description: str,
                            changed_by: str,
                            version_type: VersionType = VersionType.MINOR,
                            branch_name: str = "main",
                            metadata: Optional[Dict[str, Any]] = None) -> VersionInfo:
        """
        Create new version of a file with comprehensive tracking.
        
        Args:
            file_id: Unique file identifier
            file_path: Path to the file content
            change_description: Description of changes made
            changed_by: User who made the changes
            version_type: Type of version (minor, major, etc.)
            branch_name: Branch name for the version
            metadata: Optional metadata for the version
            
        Returns:
            Created version information
        """
        try:
            start_time = datetime.now()
            
            # Generate version ID and number
            version_id = str(uuid.uuid4())
            
            # Get previous version for this file/branch
            previous_version = await self._get_latest_version(file_id, branch_name)
            version_number = self._generate_version_number(previous_version, version_type)
            
            # Calculate file hashes
            file_hash, content_hash = await self._calculate_hashes(file_path)
            file_size = Path(file_path).stat().st_size
            
            # Check if content actually changed
            if previous_version and previous_version.content_hash == content_hash:
                self.logger.info(f"📄 No content changes detected for {file_id}")
                return previous_version
            
            # Store version data
            storage_path = await self._store_version_data(version_id, file_path)
            
            # Create delta if previous version exists
            delta_path = None
            compression_ratio = None
            
            if previous_version and self.delta_compression:
                delta_info = await self._create_delta(
                    previous_version.storage_path, 
                    storage_path, 
                    version_id
                )
                delta_path = delta_info.get("delta_path")
                compression_ratio = delta_info.get("compression_ratio")
            
            # Determine change type
            change_type = ChangeType.CREATE if not previous_version else ChangeType.UPDATE
            
            # Create version info
            version_info = VersionInfo(
                version_id=version_id,
                file_id=file_id,
                version_number=version_number,
                version_type=version_type,
                parent_version=previous_version.version_id if previous_version else None,
                change_type=change_type,
                change_description=change_description,
                changed_by=changed_by,
                change_timestamp=datetime.now(),
                file_size=file_size,
                file_hash=file_hash,
                content_hash=content_hash,
                storage_path=storage_path,
                delta_path=delta_path,
                compression_ratio=compression_ratio,
                tags=[],
                metadata=metadata or {},
                branch_name=branch_name,
                creation_time=(datetime.now() - start_time).total_seconds()
            )
            
            # Calculate storage efficiency
            if compression_ratio:
                version_info.storage_efficiency = (1 - compression_ratio) * 100
            
            # Save version metadata
            await self._save_version_metadata(version_info)
            
            # Update branch information
            await self._update_branch_info(file_id, branch_name, version_info)
            
            # Add to in-memory tracking
            self.versions[file_id].append(version_info)
            
            # Cleanup old versions if needed
            await self._cleanup_old_versions(file_id)
            
            self.logger.info(f"✅ Version created: {version_number} for {file_id}")
            return version_info
            
        except Exception as e:
            self.logger.error(f"❌ Version creation failed: {str(e)}")
            raise
    
    async def _get_latest_version(self, file_id: str, branch_name: str = "main") -> Optional[VersionInfo]:
        """Get the latest version for a file on a specific branch"""
        try:
            # Load versions from storage if not in memory
            if file_id not in self.versions:
                await self._load_file_versions(file_id)
            
            # Filter by branch and find latest
            branch_versions = [
                v for v in self.versions[file_id] 
                if v.branch_name == branch_name
            ]
            
            if not branch_versions:
                return None
            
            # Sort by timestamp and return latest
            branch_versions.sort(key=lambda x: x.change_timestamp, reverse=True)
            return branch_versions[0]
            
        except Exception as e:
            self.logger.error(f"Failed to get latest version for {file_id}: {e}")
            return None
    
    def _generate_version_number(self, previous_version: Optional[VersionInfo], 
                                version_type: VersionType) -> str:
        """Generate semantic version number"""
        if not previous_version:
            return "1.0.0"
        
        try:
            # Parse previous version number
            parts = previous_version.version_number.split('.')
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            # Increment based on version type
            if version_type == VersionType.MAJOR:
                major += 1
                minor = 0
                patch = 0
            elif version_type == VersionType.MINOR:
                minor += 1
                patch = 0
            elif version_type in [VersionType.HOTFIX, VersionType.ROLLBACK]:
                patch += 1
            else:  # BRANCH, MERGE, INITIAL
                patch += 1
            
            return f"{major}.{minor}.{patch}"
            
        except Exception:
            # Fallback to simple increment
            return f"{previous_version.version_number}.1"
    
    async def _calculate_hashes(self, file_path: Union[str, Path]) -> Tuple[str, str]:
        """Calculate file hash and content hash"""
        file_path = Path(file_path)
        
        # File hash (SHA-256 of entire file)
        file_hash = hashlib.sha256()
        
        # Content hash (SHA-256 of content only, excluding metadata)
        content_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                file_hash.update(chunk)
                content_hash.update(chunk)  # For now, same as file hash
        
        return file_hash.hexdigest(), content_hash.hexdigest()
    
    async def _store_version_data(self, version_id: str, file_path: Union[str, Path]) -> str:
        """Store version data in organized structure"""
        file_path = Path(file_path)
        
        # Create storage path with organized structure
        storage_dir = self.storage_path / "versions" / "data" / version_id[:2] / version_id[2:4]
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        storage_path = storage_dir / f"{version_id}{file_path.suffix}"
        
        # Copy file to storage
        shutil.copy2(file_path, storage_path)
        
        return str(storage_path)
    
    async def _create_delta(self, old_path: str, new_path: str, version_id: str) -> Dict[str, Any]:
        """Create delta/diff between two versions"""
        try:
            old_path = Path(old_path)
            new_path = Path(new_path)
            
            # Read files
            async with aiofiles.open(old_path, 'rb') as f:
                old_data = await f.read()
            
            async with aiofiles.open(new_path, 'rb') as f:
                new_data = await f.read()
            
            # Create binary delta using bsdiff
            delta_data = bsdiff4.diff(old_data, new_data)
            
            # Compress delta
            compressed_delta = gzip.compress(delta_data)
            
            # Calculate compression ratio
            compression_ratio = len(compressed_delta) / len(new_data) if len(new_data) > 0 else 1.0
            
            # Store delta
            delta_dir = self.storage_path / "versions" / "deltas" / version_id[:2]
            delta_dir.mkdir(parents=True, exist_ok=True)
            
            delta_path = delta_dir / f"{version_id}.delta"
            
            async with aiofiles.open(delta_path, 'wb') as f:
                await f.write(compressed_delta)
            
            return {
                "delta_path": str(delta_path),
                "compression_ratio": compression_ratio,
                "delta_size": len(compressed_delta),
                "original_size": len(new_data)
            }
            
        except Exception as e:
            self.logger.warning(f"Delta creation failed: {e}")
            return {"delta_path": None, "compression_ratio": None}
    
    async def _save_version_metadata(self, version_info: VersionInfo):
        """Save version metadata to storage"""
        try:
            metadata_dir = self.storage_path / "versions" / "metadata" / version_info.file_id
            metadata_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_path = metadata_dir / f"{version_info.version_id}.json"
            
            # Convert to dictionary
            metadata_dict = {
                "version_id": version_info.version_id,
                "file_id": version_info.file_id,
                "version_number": version_info.version_number,
                "version_type": version_info.version_type.value,
                "parent_version": version_info.parent_version,
                "change_type": version_info.change_type.value,
                "change_description": version_info.change_description,
                "changed_by": version_info.changed_by,
                "change_timestamp": version_info.change_timestamp.isoformat(),
                "file_size": version_info.file_size,
                "file_hash": version_info.file_hash,
                "content_hash": version_info.content_hash,
                "storage_path": version_info.storage_path,
                "delta_path": version_info.delta_path,
                "compression_ratio": version_info.compression_ratio,
                "tags": version_info.tags,
                "metadata": version_info.metadata,
                "branch_name": version_info.branch_name,
                "merge_base": version_info.merge_base,
                "conflicts_resolved": version_info.conflicts_resolved,
                "creation_time": version_info.creation_time,
                "storage_efficiency": version_info.storage_efficiency
            }
            
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata_dict, indent=2))
            
        except Exception as e:
            self.logger.error(f"Failed to save version metadata: {e}")
            raise
    
    async def _update_branch_info(self, file_id: str, branch_name: str, version_info: VersionInfo):
        """Update branch information with new version"""
        try:
            branch_key = f"{file_id}_{branch_name}"
            
            if branch_key not in self.branches:
                # Create new branch
                branch_info = BranchInfo(
                    branch_id=str(uuid.uuid4()),
                    branch_name=branch_name,
                    created_by=version_info.changed_by,
                    created_at=datetime.now(),
                    parent_branch="main" if branch_name != "main" else "",
                    head_version=version_info.version_id,
                    commit_count=1,
                    last_activity=datetime.now(),
                    contributors=[version_info.changed_by]
                )
                self.branches[branch_key] = branch_info
            else:
                # Update existing branch
                branch_info = self.branches[branch_key]
                branch_info.head_version = version_info.version_id
                branch_info.commit_count += 1
                branch_info.last_activity = datetime.now()
                
                if version_info.changed_by not in branch_info.contributors:
                    branch_info.contributors.append(version_info.changed_by)
            
            # Save branch metadata
            await self._save_branch_metadata(branch_key, self.branches[branch_key])
            
        except Exception as e:
            self.logger.error(f"Failed to update branch info: {e}")
    
    async def _save_branch_metadata(self, branch_key: str, branch_info: BranchInfo):
        """Save branch metadata to storage"""
        try:
            branch_dir = self.storage_path / "versions" / "branches"
            branch_path = branch_dir / f"{branch_key}.json"
            
            branch_dict = {
                "branch_id": branch_info.branch_id,
                "branch_name": branch_info.branch_name,
                "created_by": branch_info.created_by,
                "created_at": branch_info.created_at.isoformat(),
                "parent_branch": branch_info.parent_branch,
                "head_version": branch_info.head_version,
                "is_active": branch_info.is_active,
                "is_merged": branch_info.is_merged,
                "merge_target": branch_info.merge_target,
                "commit_count": branch_info.commit_count,
                "last_activity": branch_info.last_activity.isoformat() if branch_info.last_activity else None,
                "contributors": branch_info.contributors
            }
            
            async with aiofiles.open(branch_path, 'w') as f:
                await f.write(json.dumps(branch_dict, indent=2))
            
        except Exception as e:
            self.logger.error(f"Failed to save branch metadata: {e}")
    
    async def _load_file_versions(self, file_id: str):
        """Load all versions for a file from storage"""
        try:
            metadata_dir = self.storage_path / "versions" / "metadata" / file_id
            
            if not metadata_dir.exists():
                return
            
            versions = []
            for metadata_file in metadata_dir.glob("*.json"):
                try:
                    async with aiofiles.open(metadata_file, 'r') as f:
                        metadata_dict = json.loads(await f.read())
                    
                    # Convert back to VersionInfo
                    version_info = VersionInfo(
                        version_id=metadata_dict["version_id"],
                        file_id=metadata_dict["file_id"],
                        version_number=metadata_dict["version_number"],
                        version_type=VersionType(metadata_dict["version_type"]),
                        parent_version=metadata_dict.get("parent_version"),
                        change_type=ChangeType(metadata_dict["change_type"]),
                        change_description=metadata_dict["change_description"],
                        changed_by=metadata_dict["changed_by"],
                        change_timestamp=datetime.fromisoformat(metadata_dict["change_timestamp"]),
                        file_size=metadata_dict["file_size"],
                        file_hash=metadata_dict["file_hash"],
                        content_hash=metadata_dict["content_hash"],
                        storage_path=metadata_dict["storage_path"],
                        delta_path=metadata_dict.get("delta_path"),
                        compression_ratio=metadata_dict.get("compression_ratio"),
                        tags=metadata_dict.get("tags", []),
                        metadata=metadata_dict.get("metadata", {}),
                        branch_name=metadata_dict.get("branch_name", "main"),
                        merge_base=metadata_dict.get("merge_base"),
                        conflicts_resolved=metadata_dict.get("conflicts_resolved", []),
                        creation_time=metadata_dict.get("creation_time", 0.0),
                        storage_efficiency=metadata_dict.get("storage_efficiency", 0.0)
                    )
                    
                    versions.append(version_info)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load version metadata from {metadata_file}: {e}")
                    continue
            
            # Sort by timestamp
            versions.sort(key=lambda x: x.change_timestamp)
            self.versions[file_id] = versions
            
        except Exception as e:
            self.logger.error(f"Failed to load versions for {file_id}: {e}")
    
    async def get_version(self, file_id: str, version_id: str) -> Optional[VersionInfo]:
        """Get specific version by ID"""
        try:
            if file_id not in self.versions:
                await self._load_file_versions(file_id)
            
            for version in self.versions[file_id]:
                if version.version_id == version_id:
                    return version
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get version {version_id}: {e}")
            return None
    
    async def get_version_content(self, version_info: VersionInfo) -> bytes:
        """Get content for a specific version"""
        try:
            # If direct storage exists, return it
            if Path(version_info.storage_path).exists():
                async with aiofiles.open(version_info.storage_path, 'rb') as f:
                    return await f.read()
            
            # If only delta exists, reconstruct from parent
            if version_info.delta_path and version_info.parent_version:
                parent_version = await self.get_version(version_info.file_id, version_info.parent_version)
                if parent_version:
                    parent_content = await self.get_version_content(parent_version)
                    return await self._apply_delta(parent_content, version_info.delta_path)
            
            raise FileNotFoundError(f"Content not found for version {version_info.version_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to get version content: {e}")
            raise
    
    async def _apply_delta(self, base_content: bytes, delta_path: str) -> bytes:
        """Apply delta to base content to reconstruct version"""
        try:
            # Read compressed delta
            async with aiofiles.open(delta_path, 'rb') as f:
                compressed_delta = await f.read()
            
            # Decompress delta
            delta_data = gzip.decompress(compressed_delta)
            
            # Apply binary patch
            reconstructed_content = bsdiff4.patch(base_content, delta_data)
            
            return reconstructed_content
            
        except Exception as e:
            self.logger.error(f"Failed to apply delta: {e}")
            raise
    
    async def list_versions(self, file_id: str, branch_name: Optional[str] = None, 
                           limit: int = 50) -> List[VersionInfo]:
        """List versions for a file with optional filtering"""
        try:
            if file_id not in self.versions:
                await self._load_file_versions(file_id)
            
            versions = self.versions[file_id]
            
            # Filter by branch if specified
            if branch_name:
                versions = [v for v in versions if v.branch_name == branch_name]
            
            # Sort by timestamp (newest first) and limit
            versions.sort(key=lambda x: x.change_timestamp, reverse=True)
            
            return versions[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to list versions for {file_id}: {e}")
            return []
    
    async def compare_versions(self, file_id: str, version_a: str, version_b: str) -> VersionComparison:
        """Compare two versions and return differences"""
        try:
            version_info_a = await self.get_version(file_id, version_a)
            version_info_b = await self.get_version(file_id, version_b)
            
            if not version_info_a or not version_info_b:
                raise ValueError("One or both versions not found")
            
            # Get content for both versions
            content_a = await self.get_version_content(version_info_a)
            content_b = await self.get_version_content(version_info_b)
            
            # Perform comparison
            differences = []
            
            # Basic metadata differences
            if version_info_a.file_size != version_info_b.file_size:
                differences.append({
                    "type": "size_change",
                    "from": version_info_a.file_size,
                    "to": version_info_b.file_size,
                    "change": version_info_b.file_size - version_info_a.file_size
                })
            
            # Content comparison
            if content_a != content_b:
                # Try text comparison first
                try:
                    text_a = content_a.decode('utf-8')
                    text_b = content_b.decode('utf-8')
                    
                    # Line-by-line diff
                    diff_lines = list(difflib.unified_diff(
                        text_a.splitlines(keepends=True),
                        text_b.splitlines(keepends=True),
                        fromfile=f"version_{version_a}",
                        tofile=f"version_{version_b}",
                        n=3
                    ))
                    
                    if diff_lines:
                        differences.append({
                            "type": "text_change",
                            "diff": diff_lines,
                            "lines_added": len([line for line in diff_lines if line.startswith('+')]),
                            "lines_removed": len([line for line in diff_lines if line.startswith('-')])
                        })
                    
                except UnicodeDecodeError:
                    # Binary file comparison
                    differences.append({
                        "type": "binary_change",
                        "size_a": len(content_a),
                        "size_b": len(content_b),
                        "similarity": self._calculate_binary_similarity(content_a, content_b)
                    })
            
            # Calculate overall similarity
            similarity_score = self._calculate_overall_similarity(differences, content_a, content_b)
            
            return VersionComparison(
                version_a=version_a,
                version_b=version_b,
                differences=differences,
                similarity_score=similarity_score,
                total_changes=len(differences)
            )
            
        except Exception as e:
            self.logger.error(f"Version comparison failed: {e}")
            raise
    
    def _calculate_binary_similarity(self, content_a: bytes, content_b: bytes) -> float:
        """Calculate similarity between binary content"""
        if len(content_a) == 0 and len(content_b) == 0:
            return 1.0
        
        if len(content_a) == 0 or len(content_b) == 0:
            return 0.0
        
        # Simple byte-by-byte comparison for similarity
        min_len = min(len(content_a), len(content_b))
        max_len = max(len(content_a), len(content_b))
        
        matching_bytes = sum(1 for i in range(min_len) if content_a[i] == content_b[i])
        
        # Account for size difference
        similarity = (matching_bytes / max_len) if max_len > 0 else 0.0
        
        return similarity
    
    def _calculate_overall_similarity(self, differences: List[Dict], content_a: bytes, content_b: bytes) -> float:
        """Calculate overall similarity score between versions"""
        if not differences:
            return 1.0
        
        # Base similarity on content similarity
        content_similarity = self._calculate_binary_similarity(content_a, content_b)
        
        # Adjust based on number and type of differences
        difference_penalty = len(differences) * 0.1
        
        # Type-based penalties
        for diff in differences:
            if diff["type"] == "binary_change":
                difference_penalty += 0.2
            elif diff["type"] == "text_change":
                difference_penalty += 0.1
            elif diff["type"] == "size_change":
                difference_penalty += 0.05
        
        final_similarity = max(0.0, content_similarity - difference_penalty)
        return min(1.0, final_similarity)
    
    async def rollback_to_version(self, file_id: str, target_version_id: str, 
                                 rolled_back_by: str, reason: str = "") -> VersionInfo:
        """Rollback file to a specific version"""
        try:
            target_version = await self.get_version(file_id, target_version_id)
            if not target_version:
                raise ValueError(f"Target version {target_version_id} not found")
            
            # Get current latest version
            current_version = await self._get_latest_version(file_id, target_version.branch_name)
            
            # Get content of target version
            target_content = await self.get_version_content(target_version)
            
            # Create temporary file with target content
            temp_dir = self.storage_path / "temp"
            temp_path = temp_dir / f"rollback_{file_id}_{uuid.uuid4()}"
            
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(target_content)
            
            # Create new version as rollback
            rollback_description = f"Rollback to version {target_version.version_number}"
            if reason:
                rollback_description += f" - Reason: {reason}"
            
            rollback_version = await self.create_version(
                file_id=file_id,
                file_path=temp_path,
                change_description=rollback_description,
                changed_by=rolled_back_by,
                version_type=VersionType.ROLLBACK,
                branch_name=target_version.branch_name,
                metadata={
                    "rollback_target": target_version_id,
                    "rollback_from": current_version.version_id if current_version else None,
                    "rollback_reason": reason
                }
            )
            
            # Cleanup temp file
            temp_path.unlink(missing_ok=True)
            
            self.logger.info(f"🔄 Rolled back {file_id} to version {target_version.version_number}")
            return rollback_version
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            raise
    
    async def create_branch(self, file_id: str, branch_name: str, 
                           created_by: str, from_version: Optional[str] = None) -> BranchInfo:
        """Create new branch for parallel development"""
        try:
            # Determine source version
            if from_version:
                source_version = await self.get_version(file_id, from_version)
                if not source_version:
                    raise ValueError(f"Source version {from_version} not found")
            else:
                source_version = await self._get_latest_version(file_id, "main")
                if not source_version:
                    raise ValueError(f"No versions found for file {file_id}")
            
            # Check if branch already exists
            branch_key = f"{file_id}_{branch_name}"
            if branch_key in self.branches:
                raise ValueError(f"Branch {branch_name} already exists for file {file_id}")
            
            # Create branch info
            branch_info = BranchInfo(
                branch_id=str(uuid.uuid4()),
                branch_name=branch_name,
                created_by=created_by,
                created_at=datetime.now(),
                parent_branch=source_version.branch_name,
                head_version=source_version.version_id,
                commit_count=0,
                contributors=[created_by]
            )
            
            # Save branch
            self.branches[branch_key] = branch_info
            await self._save_branch_metadata(branch_key, branch_info)
            
            self.logger.info(f"🌿 Created branch {branch_name} for {file_id}")
            return branch_info
            
        except Exception as e:
            self.logger.error(f"Branch creation failed: {e}")
            raise
    
    async def merge_branches(self, file_id: str, source_branch: str, target_branch: str,
                            merged_by: str, resolution_strategy: ConflictResolution = ConflictResolution.AUTO_MERGE) -> MergeResult:
        """Merge one branch into another"""
        try:
            # Get latest versions from both branches
            source_version = await self._get_latest_version(file_id, source_branch)
            target_version = await self._get_latest_version(file_id, target_branch)
            
            if not source_version or not target_version:
                raise ValueError("Source or target branch not found")
            
            # Compare versions to detect conflicts
            comparison = await self.compare_versions(file_id, target_version.version_id, source_version.version_id)
            
            conflicts = []
            merged_version_id = None
            
            # Determine if auto-merge is possible
            can_auto_merge = (
                comparison.similarity_score >= self.auto_merge_threshold and
                resolution_strategy == ConflictResolution.AUTO_MERGE
            )
            
            if can_auto_merge:
                # Perform auto-merge
                merged_content = await self._auto_merge_content(source_version, target_version)
                
                # Create temporary file with merged content
                temp_dir = self.storage_path / "temp" / "merge"
                temp_path = temp_dir / f"merge_{file_id}_{uuid.uuid4()}"
                
                async with aiofiles.open(temp_path, 'wb') as f:
                    await f.write(merged_content)
                
                # Create merge version
                merge_description = f"Merge {source_branch} into {target_branch}"
                
                merged_version = await self.create_version(
                    file_id=file_id,
                    file_path=temp_path,
                    change_description=merge_description,
                    changed_by=merged_by,
                    version_type=VersionType.MERGE,
                    branch_name=target_branch,
                    metadata={
                        "merge_source": source_branch,
                        "merge_target": target_branch,
                        "source_version": source_version.version_id,
                        "target_version": target_version.version_id,
                        "resolution_strategy": resolution_strategy.value
                    }
                )
                
                merged_version_id = merged_version.version_id
                
                # Mark source branch as merged
                source_branch_key = f"{file_id}_{source_branch}"
                if source_branch_key in self.branches:
                    self.branches[source_branch_key].is_merged = True
                    self.branches[source_branch_key].merge_target = target_branch
                    await self._save_branch_metadata(source_branch_key, self.branches[source_branch_key])
                
                # Cleanup temp file
                temp_path.unlink(missing_ok=True)
                
            else:
                # Manual resolution required
                conflicts = await self._identify_conflicts(comparison, source_version, target_version)
                
                if resolution_strategy == ConflictResolution.CREATE_BRANCH:
                    # Create conflict resolution branch
                    conflict_branch = f"{target_branch}_conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    await self.create_branch(file_id, conflict_branch, merged_by, source_version.version_id)
            
            result = MergeResult(
                success=can_auto_merge,
                merged_version_id=merged_version_id or "",
                conflicts=conflicts,
                resolution_strategy=resolution_strategy,
                merged_by=merged_by
            )
            
            # Save merge result
            await self._save_merge_result(file_id, result)
            
            self.logger.info(f"🔀 Merge {'completed' if can_auto_merge else 'failed'}: {source_branch} → {target_branch}")
            return result
            
        except Exception as e:
            self.logger.error(f"Merge failed: {e}")
            raise
    
    async def _auto_merge_content(self, source_version: VersionInfo, target_version: VersionInfo) -> bytes:
        """Automatically merge content from two versions"""
        try:
            # Get content from both versions
            source_content = await self.get_version_content(source_version)
            target_content = await self.get_version_content(target_version)
            
            # For now, simple strategy: prefer source if different
            # In production, implement intelligent merge based on content type
            if source_content != target_content:
                # Try text-based merge for text files
                try:
                    source_text = source_content.decode('utf-8')
                    target_text = target_content.decode('utf-8')
                    
                    # Simple line-based merge (prefer source changes)
                    return source_content
                    
                except UnicodeDecodeError:
                    # Binary file - prefer source
                    return source_content
            
            return target_content
            
        except Exception as e:
            self.logger.error(f"Auto-merge failed: {e}")
            raise
    
    async def _identify_conflicts(self, comparison: VersionComparison, 
                                 source_version: VersionInfo, target_version: VersionInfo) -> List[Dict[str, Any]]:
        """Identify conflicts between versions"""
        conflicts = []
        
        for diff in comparison.differences:
            if diff["type"] == "text_change":
                # Analyze text changes for conflicts
                conflicts.append({
                    "type": "text_conflict",
                    "description": "Conflicting text changes detected",
                    "source_version": source_version.version_id,
                    "target_version": target_version.version_id,
                    "details": diff
                })
            elif diff["type"] == "binary_change":
                conflicts.append({
                    "type": "binary_conflict",
                    "description": "Binary file changed in both branches",
                    "source_version": source_version.version_id,
                    "target_version": target_version.version_id,
                    "details": diff
                })
            elif diff["type"] == "size_change" and abs(diff["change"]) > 1024:  # Significant size change
                conflicts.append({
                    "type": "size_conflict",
                    "description": "Significant size change detected",
                    "source_version": source_version.version_id,
                    "target_version": target_version.version_id,
                    "details": diff
                })
        
        return conflicts
    
    async def _save_merge_result(self, file_id: str, merge_result: MergeResult):
        """Save merge result for auditing"""
        try:
            merge_dir = self.storage_path / "versions" / "merges" / file_id
            merge_dir.mkdir(parents=True, exist_ok=True)
            
            merge_id = str(uuid.uuid4())
            merge_path = merge_dir / f"{merge_id}.json"
            
            merge_dict = {
                "merge_id": merge_id,
                "file_id": file_id,
                "success": merge_result.success,
                "merged_version_id": merge_result.merged_version_id,
                "conflicts": merge_result.conflicts,
                "resolution_strategy": merge_result.resolution_strategy.value if merge_result.resolution_strategy else None,
                "merge_timestamp": merge_result.merge_timestamp.isoformat(),
                "merged_by": merge_result.merged_by
            }
            
            async with aiofiles.open(merge_path, 'w') as f:
                await f.write(json.dumps(merge_dict, indent=2))
            
        except Exception as e:
            self.logger.error(f"Failed to save merge result: {e}")
    
    async def _cleanup_old_versions(self, file_id: str):
        """Clean up old versions based on retention policy"""
        try:
            if file_id not in self.versions:
                return
            
            versions = self.versions[file_id]
            
            # Keep versions within threshold
            cutoff_date = datetime.now() - timedelta(days=self.cleanup_threshold_days)
            
            # Always keep certain types of versions
            protected_types = {VersionType.MAJOR, VersionType.MERGE, VersionType.ROLLBACK}
            
            versions_to_remove = []
            
            # Sort by timestamp
            sorted_versions = sorted(versions, key=lambda x: x.change_timestamp)
            
            # Keep last N versions
            if len(sorted_versions) > self.max_versions_per_file:
                for version in sorted_versions[:-self.max_versions_per_file]:
                    if (version.change_timestamp < cutoff_date and 
                        version.version_type not in protected_types):
                        versions_to_remove.append(version)
            
            # Remove old versions
            for version in versions_to_remove:
                await self._remove_version(version)
                self.versions[file_id].remove(version)
            
            if versions_to_remove:
                self.logger.info(f"🧹 Cleaned up {len(versions_to_remove)} old versions for {file_id}")
            
        except Exception as e:
            self.logger.error(f"Version cleanup failed: {e}")
    
    async def _remove_version(self, version: VersionInfo):
        """Remove version data and metadata"""
        try:
            # Remove version data file
            if Path(version.storage_path).exists():
                Path(version.storage_path).unlink()
            
            # Remove delta file
            if version.delta_path and Path(version.delta_path).exists():
                Path(version.delta_path).unlink()
            
            # Remove metadata file
            metadata_path = (
                self.storage_path / "versions" / "metadata" / 
                version.file_id / f"{version.version_id}.json"
            )
            if metadata_path.exists():
                metadata_path.unlink()
            
        except Exception as e:
            self.logger.warning(f"Failed to remove version {version.version_id}: {e}")
    
    async def get_version_history(self, file_id: str, branch_name: str = "main") -> List[Dict[str, Any]]:
        """Get complete version history for a file"""
        try:
            versions = await self.list_versions(file_id, branch_name)
            
            history = []
            for version in versions:
                history_entry = {
                    "version_id": version.version_id,
                    "version_number": version.version_number,
                    "version_type": version.version_type.value,
                    "change_description": version.change_description,
                    "changed_by": version.changed_by,
                    "change_timestamp": version.change_timestamp.isoformat(),
                    "file_size": version.file_size,
                    "branch_name": version.branch_name,
                    "tags": version.tags,
                    "creation_time": version.creation_time,
                    "storage_efficiency": version.storage_efficiency
                }
                history.append(history_entry)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get version history: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive version management statistics"""
        try:
            stats = {
                "total_files": len(self.versions),
                "total_versions": sum(len(versions) for versions in self.versions.values()),
                "total_branches": len(self.branches),
                "active_branches": len([b for b in self.branches.values() if b.is_active]),
                "storage_efficiency": 0.0,
                "space_saved": 0,
                "version_types": defaultdict(int),
                "recent_activity": []
            }
            
            total_original_size = 0
            total_stored_size = 0
            
            # Calculate statistics from all versions
            for file_id, versions in self.versions.items():
                for version in versions:
                    stats["version_types"][version.version_type.value] += 1
                    
                    total_original_size += version.file_size
                    
                    # Estimate stored size (original + delta if exists)
                    stored_size = version.file_size
                    if version.delta_path and version.compression_ratio:
                        stored_size = int(version.file_size * version.compression_ratio)
                    
                    total_stored_size += stored_size
            
            # Calculate efficiency
            if total_original_size > 0:
                stats["storage_efficiency"] = ((total_original_size - total_stored_size) / total_original_size) * 100
                stats["space_saved"] = total_original_size - total_stored_size
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
