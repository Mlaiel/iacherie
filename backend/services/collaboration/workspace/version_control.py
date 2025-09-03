"""Version Control - Collaborative Content Versioning System

Advanced version control system for collaborative content creation with 
conflict resolution, branching, and change tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import hashlib
import difflib

logger = logging.getLogger(__name__)


class VersionStatus(Enum):
    """Version status options"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ChangeType(Enum):
    """Types of changes"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    RENAME = "rename"
    MERGE = "merge"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    MANUAL = "manual"
    AUTO_MERGE = "auto_merge"
    ACCEPT_MINE = "accept_mine"
    ACCEPT_THEIRS = "accept_theirs"
    REJECT_ALL = "reject_all"


@dataclass
class VersionChange:
    """Individual version change"""
    change_id: str
    change_type: ChangeType
    author_id: str
    timestamp: datetime
    file_path: str
    content_before: Optional[str] = None
    content_after: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Version:
    """Content version"""
    version_id: str
    version_number: str
    parent_version_id: Optional[str]
    branch_name: str
    author_id: str
    created_at: datetime
    status: VersionStatus
    changes: List[VersionChange]
    content_snapshot: Dict[str, Any]
    commit_message: str
    tags: List[str] = field(default_factory=list)
    approval_required: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


@dataclass
class Branch:
    """Version control branch"""
    branch_id: str
    branch_name: str
    parent_branch: Optional[str]
    created_by: str
    created_at: datetime
    is_protected: bool = False
    merge_strategy: str = "auto"
    access_permissions: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class MergeRequest:
    """Merge request between branches"""
    merge_id: str
    source_branch: str
    target_branch: str
    source_version: str
    target_version: str
    author_id: str
    title: str
    description: str
    created_at: datetime
    status: str = "pending"  # pending, approved, rejected, merged
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    approved_by: List[str] = field(default_factory=list)
    rejected_by: List[str] = field(default_factory=list)


@dataclass
class Conflict:
    """Version control conflict"""
    conflict_id: str
    file_path: str
    conflict_type: str
    local_content: str
    remote_content: str
    base_content: Optional[str] = None
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None


@dataclass
class Repository:
    """Version control repository"""
    repo_id: str
    name: str
    project_id: str
    branches: Dict[str, Branch]
    versions: Dict[str, Version]
    current_branch: str = "main"
    default_branch: str = "main"
    created_at: datetime = field(default_factory=datetime.now)
    settings: Dict[str, Any] = field(default_factory=dict)


class VersionControl:
    """Advanced collaborative version control system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Repository storage
        self.repositories: Dict[str, Repository] = {}
        
        # Merge requests and conflicts
        self.merge_requests: Dict[str, MergeRequest] = {}
        self.active_conflicts: Dict[str, List[Conflict]] = {}
        
        # Configuration
        self.auto_merge_enabled = self.config.get('auto_merge', True)
        self.require_approval = self.config.get('require_approval', False)
        self.max_versions = self.config.get('max_versions', 1000)
        self.conflict_timeout = self.config.get('conflict_timeout', 3600)  # 1 hour
        
        # Content hashing for integrity
        self.hash_algorithm = self.config.get('hash_algorithm', 'sha256')
        
        logger.info("VersionControl system initialized")
    
    async def initialize(self):
        """Initialize the version control system"""
        logger.info("Initializing Version Control...")
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_versions())
        asyncio.create_task(self._resolve_stale_conflicts())
        
        logger.info("Version Control initialized successfully")
    
    async def shutdown(self):
        """Shutdown the version control system"""
        logger.info("Shutting down Version Control...")
        
        # Save repository states
        for repo in self.repositories.values():
            await self._save_repository_state(repo)
        
        logger.info("Version Control shutdown complete")
    
    async def create_repository(
        self,
        name: str,
        project_id: str,
        created_by: str,
        initial_content: Dict[str, Any] = None
    ) -> Repository:
        """Create a new version control repository"""
        try:
            repo_id = str(uuid.uuid4())
            
            # Create main branch
            main_branch = Branch(
                branch_id=str(uuid.uuid4()),
                branch_name="main",
                parent_branch=None,
                created_by=created_by,
                created_at=datetime.now(),
                is_protected=True,
                description="Main branch"
            )
            
            # Create initial version
            initial_version = None
            if initial_content:
                initial_version = await self._create_initial_version(
                    repo_id, created_by, initial_content
                )
            
            # Create repository
            repository = Repository(
                repo_id=repo_id,
                name=name,
                project_id=project_id,
                branches={"main": main_branch},
                versions={initial_version.version_id: initial_version} if initial_version else {},
                current_branch="main",
                default_branch="main"
            )
            
            self.repositories[repo_id] = repository
            
            logger.info(f"Created repository: {repo_id}")
            return repository
            
        except Exception as e:
            logger.error(f"Error creating repository: {str(e)}")
            raise
    
    async def create_branch(
        self,
        repo_id: str,
        branch_name: str,
        parent_branch: str,
        created_by: str,
        description: str = ""
    ) -> Branch:
        """Create a new branch"""
        try:
            repository = self.repositories.get(repo_id)
            if not repository:
                raise ValueError(f"Repository {repo_id} not found")
            
            if branch_name in repository.branches:
                raise ValueError(f"Branch {branch_name} already exists")
            
            if parent_branch not in repository.branches:
                raise ValueError(f"Parent branch {parent_branch} not found")
            
            branch_id = str(uuid.uuid4())
            
            branch = Branch(
                branch_id=branch_id,
                branch_name=branch_name,
                parent_branch=parent_branch,
                created_by=created_by,
                created_at=datetime.now(),
                description=description
            )
            
            repository.branches[branch_name] = branch
            
            logger.info(f"Created branch {branch_name} in repository {repo_id}")
            return branch
            
        except Exception as e:
            logger.error(f"Error creating branch: {str(e)}")
            raise
    
    async def commit_changes(
        self,
        repo_id: str,
        branch_name: str,
        author_id: str,
        changes: List[VersionChange],
        commit_message: str,
        content_snapshot: Dict[str, Any]
    ) -> Version:
        """Commit changes to a branch"""
        try:
            repository = self.repositories.get(repo_id)
            if not repository:
                raise ValueError(f"Repository {repo_id} not found")
            
            if branch_name not in repository.branches:
                raise ValueError(f"Branch {branch_name} not found")
            
            # Get parent version
            parent_version_id = await self._get_latest_version_id(repository, branch_name)
            
            # Generate version number
            version_number = await self._generate_version_number(repository, branch_name)
            
            # Create version
            version_id = str(uuid.uuid4())
            
            version = Version(
                version_id=version_id,
                version_number=version_number,
                parent_version_id=parent_version_id,
                branch_name=branch_name,
                author_id=author_id,
                created_at=datetime.now(),
                status=VersionStatus.DRAFT,
                changes=changes,
                content_snapshot=content_snapshot,
                commit_message=commit_message,
                approval_required=self.require_approval
            )
            
            # Validate changes
            await self._validate_changes(repository, version)
            
            # Store version
            repository.versions[version_id] = version
            
            # Check for conflicts if merging
            if parent_version_id:
                conflicts = await self._detect_conflicts(repository, version)
                if conflicts:
                    self.active_conflicts[version_id] = conflicts
                    logger.warning(f"Conflicts detected in version {version_id}")
            
            # Auto-approve if not required
            if not self.require_approval:
                version.status = VersionStatus.APPROVED
                version.approved_by = author_id
                version.approved_at = datetime.now()
            
            logger.info(f"Committed version {version_id} to branch {branch_name}")
            return version
            
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            raise
    
    async def create_merge_request(
        self,
        repo_id: str,
        source_branch: str,
        target_branch: str,
        author_id: str,
        title: str,
        description: str,
        reviewers: List[str] = None
    ) -> MergeRequest:
        """Create a merge request"""
        try:
            repository = self.repositories.get(repo_id)
            if not repository:
                raise ValueError(f"Repository {repo_id} not found")
            
            if source_branch not in repository.branches:
                raise ValueError(f"Source branch {source_branch} not found")
            
            if target_branch not in repository.branches:
                raise ValueError(f"Target branch {target_branch} not found")
            
            # Get latest versions from both branches
            source_version = await self._get_latest_version_id(repository, source_branch)
            target_version = await self._get_latest_version_id(repository, target_branch)
            
            merge_id = str(uuid.uuid4())
            
            # Detect conflicts
            conflicts = await self._detect_merge_conflicts(
                repository, source_version, target_version
            )
            
            merge_request = MergeRequest(
                merge_id=merge_id,
                source_branch=source_branch,
                target_branch=target_branch,
                source_version=source_version,
                target_version=target_version,
                author_id=author_id,
                title=title,
                description=description,
                created_at=datetime.now(),
                conflicts=conflicts,
                reviewers=reviewers or []
            )
            
            self.merge_requests[merge_id] = merge_request
            
            logger.info(f"Created merge request {merge_id}")
            return merge_request
            
        except Exception as e:
            logger.error(f"Error creating merge request: {str(e)}")
            raise
    
    async def approve_merge_request(
        self,
        merge_id: str,
        approver_id: str
    ) -> bool:
        """Approve a merge request"""
        try:
            merge_request = self.merge_requests.get(merge_id)
            if not merge_request:
                raise ValueError(f"Merge request {merge_id} not found")
            
            if merge_request.status != "pending":
                raise ValueError(f"Merge request is not pending")
            
            if approver_id not in merge_request.reviewers:
                raise ValueError(f"User {approver_id} is not a reviewer")
            
            if approver_id not in merge_request.approved_by:
                merge_request.approved_by.append(approver_id)
            
            # Check if all reviewers have approved
            if len(merge_request.approved_by) >= len(merge_request.reviewers):
                merge_request.status = "approved"
                
                # Auto-merge if no conflicts
                if not merge_request.conflicts and self.auto_merge_enabled:
                    await self._execute_merge(merge_request)
            
            logger.info(f"Merge request {merge_id} approved by {approver_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving merge request: {str(e)}")
            raise
    
    async def merge_branches(
        self,
        repo_id: str,
        source_branch: str,
        target_branch: str,
        merge_strategy: str = "auto",
        merged_by: str = None
    ) -> Version:
        """Merge branches"""
        try:
            repository = self.repositories.get(repo_id)
            if not repository:
                raise ValueError(f"Repository {repo_id} not found")
            
            # Get latest versions
            source_version_id = await self._get_latest_version_id(repository, source_branch)
            target_version_id = await self._get_latest_version_id(repository, target_branch)
            
            source_version = repository.versions[source_version_id]
            target_version = repository.versions[target_version_id]
            
            # Detect and resolve conflicts
            conflicts = await self._detect_merge_conflicts(
                repository, source_version_id, target_version_id
            )
            
            if conflicts and merge_strategy == "auto":
                raise ValueError("Conflicts detected - manual resolution required")
            
            # Create merged content
            merged_content = await self._merge_content(
                source_version.content_snapshot,
                target_version.content_snapshot,
                merge_strategy
            )
            
            # Create merge changes
            merge_changes = await self._create_merge_changes(
                source_version, target_version, merged_by
            )
            
            # Create merge version
            version_number = await self._generate_version_number(repository, target_branch)
            merge_version_id = str(uuid.uuid4())
            
            merge_version = Version(
                version_id=merge_version_id,
                version_number=version_number,
                parent_version_id=target_version_id,
                branch_name=target_branch,
                author_id=merged_by,
                created_at=datetime.now(),
                status=VersionStatus.APPROVED,
                changes=merge_changes,
                content_snapshot=merged_content,
                commit_message=f"Merge {source_branch} into {target_branch}",
                tags=["merge"]
            )
            
            repository.versions[merge_version_id] = merge_version
            
            logger.info(f"Merged {source_branch} into {target_branch}")
            return merge_version
            
        except Exception as e:
            logger.error(f"Error merging branches: {str(e)}")
            raise
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution: str,
        resolved_by: str,
        resolution_strategy: ConflictResolution = ConflictResolution.MANUAL
    ):
        """Resolve a version control conflict"""
        try:
            # Find conflict
            conflict = None
            version_id = None
            
            for vid, conflicts in self.active_conflicts.items():
                for c in conflicts:
                    if c.conflict_id == conflict_id:
                        conflict = c
                        version_id = vid
                        break
                if conflict:
                    break
            
            if not conflict:
                raise ValueError(f"Conflict {conflict_id} not found")
            
            # Apply resolution
            conflict.resolution = resolution
            conflict.resolved_by = resolved_by
            conflict.resolved_at = datetime.now()
            
            # Remove from active conflicts if all resolved
            version_conflicts = self.active_conflicts.get(version_id, [])
            remaining_conflicts = [c for c in version_conflicts if not c.resolution]
            
            if not remaining_conflicts:
                del self.active_conflicts[version_id]
                logger.info(f"All conflicts resolved for version {version_id}")
            
            logger.info(f"Conflict {conflict_id} resolved by {resolved_by}")
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            raise
    
    async def get_version_history(
        self,
        repo_id: str,
        branch_name: str = None,
        limit: int = 50
    ) -> List[Version]:
        """Get version history for a branch or entire repository"""
        try:
            repository = self.repositories.get(repo_id)
            if not repository:
                raise ValueError(f"Repository {repo_id} not found")
            
            versions = list(repository.versions.values())
            
            # Filter by branch if specified
            if branch_name:
                versions = [v for v in versions if v.branch_name == branch_name]
            
            # Sort by creation date (newest first)
            versions.sort(key=lambda x: x.created_at, reverse=True)
            
            return versions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting version history: {str(e)}")
            raise
    
    async def get_file_diff(
        self,
        repo_id: str,
        file_path: str,
        version_a: str,
        version_b: str
    ) -> Dict[str, Any]:
        """Get diff between two versions of a file"""
        try:
            repository = self.repositories.get(repo_id)
            if not repository:
                raise ValueError(f"Repository {repo_id} not found")
            
            version_a_obj = repository.versions.get(version_a)
            version_b_obj = repository.versions.get(version_b)
            
            if not version_a_obj or not version_b_obj:
                raise ValueError("One or both versions not found")
            
            content_a = version_a_obj.content_snapshot.get(file_path, "")
            content_b = version_b_obj.content_snapshot.get(file_path, "")
            
            # Generate diff
            diff = list(difflib.unified_diff(
                content_a.splitlines(keepends=True),
                content_b.splitlines(keepends=True),
                fromfile=f"{file_path}@{version_a}",
                tofile=f"{file_path}@{version_b}"
            ))
            
            return {
                'file_path': file_path,
                'version_a': version_a,
                'version_b': version_b,
                'diff': ''.join(diff),
                'lines_added': len([line for line in diff if line.startswith('+')]),
                'lines_removed': len([line for line in diff if line.startswith('-')])
            }
            
        except Exception as e:
            logger.error(f"Error getting file diff: {str(e)}")
            raise
    
    async def revert_version(
        self,
        repo_id: str,
        version_id: str,
        reverted_by: str,
        branch_name: str = None
    ) -> Version:
        """Revert to a previous version"""
        try:
            repository = self.repositories.get(repo_id)
            if not repository:
                raise ValueError(f"Repository {repo_id} not found")
            
            version_to_revert = repository.versions.get(version_id)
            if not version_to_revert:
                raise ValueError(f"Version {version_id} not found")
            
            target_branch = branch_name or version_to_revert.branch_name
            
            # Create revert changes
            revert_changes = [
                VersionChange(
                    change_id=str(uuid.uuid4()),
                    change_type=ChangeType.UPDATE,
                    author_id=reverted_by,
                    timestamp=datetime.now(),
                    file_path="*",
                    description=f"Revert to version {version_id}"
                )
            ]
            
            # Create revert version
            revert_version_id = str(uuid.uuid4())
            version_number = await self._generate_version_number(repository, target_branch)
            
            revert_version = Version(
                version_id=revert_version_id,
                version_number=version_number,
                parent_version_id=await self._get_latest_version_id(repository, target_branch),
                branch_name=target_branch,
                author_id=reverted_by,
                created_at=datetime.now(),
                status=VersionStatus.APPROVED,
                changes=revert_changes,
                content_snapshot=version_to_revert.content_snapshot.copy(),
                commit_message=f"Revert to version {version_to_revert.version_number}",
                tags=["revert"]
            )
            
            repository.versions[revert_version_id] = revert_version
            
            logger.info(f"Reverted to version {version_id}")
            return revert_version
            
        except Exception as e:
            logger.error(f"Error reverting version: {str(e)}")
            raise
    
    def get_repository_info(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get repository information"""
        repository = self.repositories.get(repo_id)
        if not repository:
            return None
        
        # Get latest version synchronously
        latest_version_id = None
        branch_versions = [
            v for v in repository.versions.values() 
            if v.branch_name == repository.current_branch
        ]
        if branch_versions:
            latest_version = max(branch_versions, key=lambda x: x.created_at)
            latest_version_id = latest_version.version_id
        
        return {
            'repo_id': repository.repo_id,
            'name': repository.name,
            'project_id': repository.project_id,
            'current_branch': repository.current_branch,
            'default_branch': repository.default_branch,
            'branches': list(repository.branches.keys()),
            'version_count': len(repository.versions),
            'created_at': repository.created_at.isoformat(),
            'latest_version': latest_version_id
        }
    
    def get_branch_info(self, repo_id: str, branch_name: str) -> Optional[Dict[str, Any]]:
        """Get branch information"""
        repository = self.repositories.get(repo_id)
        if not repository:
            return None
        
        branch = repository.branches.get(branch_name)
        if not branch:
            return None
        
        # Count versions in this branch
        branch_versions = [v for v in repository.versions.values() if v.branch_name == branch_name]
        
        return {
            'branch_id': branch.branch_id,
            'branch_name': branch.branch_name,
            'parent_branch': branch.parent_branch,
            'created_by': branch.created_by,
            'created_at': branch.created_at.isoformat(),
            'is_protected': branch.is_protected,
            'merge_strategy': branch.merge_strategy,
            'version_count': len(branch_versions),
            'description': branch.description
        }
    
    # Private helper methods
    
    async def _create_initial_version(
        self,
        repo_id: str,
        author_id: str,
        content: Dict[str, Any]
    ) -> Version:
        """Create the initial version for a repository"""
        version_id = str(uuid.uuid4())
        
        initial_changes = [
            VersionChange(
                change_id=str(uuid.uuid4()),
                change_type=ChangeType.CREATE,
                author_id=author_id,
                timestamp=datetime.now(),
                file_path="*",
                content_after=json.dumps(content),
                description="Initial commit"
            )
        ]
        
        return Version(
            version_id=version_id,
            version_number="1.0.0",
            parent_version_id=None,
            branch_name="main",
            author_id=author_id,
            created_at=datetime.now(),
            status=VersionStatus.APPROVED,
            changes=initial_changes,
            content_snapshot=content,
            commit_message="Initial commit",
            tags=["initial"]
        )
    
    async def _get_latest_version_id(self, repository: Repository, branch_name: str) -> Optional[str]:
        """Get the latest version ID for a branch"""
        branch_versions = [
            v for v in repository.versions.values() 
            if v.branch_name == branch_name
        ]
        
        if not branch_versions:
            return None
        
        latest_version = max(branch_versions, key=lambda x: x.created_at)
        return latest_version.version_id
    
    async def _generate_version_number(self, repository: Repository, branch_name: str) -> str:
        """Generate the next version number for a branch"""
        branch_versions = [
            v for v in repository.versions.values() 
            if v.branch_name == branch_name
        ]
        
        if not branch_versions:
            return "1.0.0"
        
        # Simple versioning: increment patch number
        latest_version = max(branch_versions, key=lambda x: x.created_at)
        version_parts = latest_version.version_number.split('.')
        
        try:
            major, minor, patch = int(version_parts[0]), int(version_parts[1]), int(version_parts[2])
            return f"{major}.{minor}.{patch + 1}"
        except (ValueError, IndexError):
            return f"{len(branch_versions) + 1}.0.0"
    
    async def _validate_changes(self, repository: Repository, version: Version):
        """Validate version changes"""
        # Check for empty changes
        if not version.changes:
            raise ValueError("Version must contain at least one change")
        
        # Validate content snapshot
        if not version.content_snapshot:
            logger.warning(f"Version {version.version_id} has empty content snapshot")
        
        # Check for duplicate changes
        change_ids = [c.change_id for c in version.changes]
        if len(change_ids) != len(set(change_ids)):
            raise ValueError("Duplicate change IDs detected")
    
    async def _detect_conflicts(self, repository: Repository, version: Version) -> List[Conflict]:
        """Detect conflicts in a version"""
        conflicts = []
        
        # Simple conflict detection - in real implementation, this would be more sophisticated
        if version.parent_version_id:
            parent_version = repository.versions.get(version.parent_version_id)
            if parent_version:
                # Check for concurrent modifications
                for change in version.changes:
                    if change.change_type == ChangeType.UPDATE:
                        # Check if file was modified in parallel
                        concurrent_changes = self._find_concurrent_changes(
                            repository, version.parent_version_id, change.file_path
                        )
                        
                        if concurrent_changes:
                            conflict = Conflict(
                                conflict_id=str(uuid.uuid4()),
                                file_path=change.file_path,
                                conflict_type="concurrent_modification",
                                local_content=change.content_after or "",
                                remote_content=concurrent_changes[0].content_after or "",
                                base_content=change.content_before
                            )
                            conflicts.append(conflict)
        
        return conflicts
    
    def _find_concurrent_changes(
        self,
        repository: Repository,
        base_version_id: str,
        file_path: str
    ) -> List[VersionChange]:
        """Find concurrent changes to a file"""
        # Find all versions that modified the same file after the base version
        base_version = repository.versions.get(base_version_id)
        if not base_version:
            return []
        
        concurrent_changes = []
        for version in repository.versions.values():
            if (version.created_at > base_version.created_at and 
                version.version_id != base_version_id):
                
                for change in version.changes:
                    if change.file_path == file_path and change.change_type == ChangeType.UPDATE:
                        concurrent_changes.append(change)
        
        return concurrent_changes
    
    async def _detect_merge_conflicts(
        self,
        repository: Repository,
        source_version_id: str,
        target_version_id: str
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between two versions for merging"""
        conflicts = []
        
        source_version = repository.versions.get(source_version_id)
        target_version = repository.versions.get(target_version_id)
        
        if not source_version or not target_version:
            return conflicts
        
        # Compare content snapshots
        source_files = set(source_version.content_snapshot.keys())
        target_files = set(target_version.content_snapshot.keys())
        
        # Check for conflicting modifications
        common_files = source_files.intersection(target_files)
        for file_path in common_files:
            source_content = source_version.content_snapshot[file_path]
            target_content = target_version.content_snapshot[file_path]
            
            if source_content != target_content:
                # Find common ancestor content
                base_content = await self._find_common_ancestor_content(
                    repository, source_version_id, target_version_id, file_path
                )
                
                conflicts.append({
                    'file_path': file_path,
                    'conflict_type': 'content_modification',
                    'source_content': source_content,
                    'target_content': target_content,
                    'base_content': base_content
                })
        
        return conflicts
    
    async def _find_common_ancestor_content(
        self,
        repository: Repository,
        version_a_id: str,
        version_b_id: str,
        file_path: str
    ) -> Optional[str]:
        """Find common ancestor content for a file"""
        # Simplified implementation - find the most recent common version
        # In a real implementation, this would use a proper merge-base algorithm
        
        version_a = repository.versions.get(version_a_id)
        version_b = repository.versions.get(version_b_id)
        
        if not version_a or not version_b:
            return None
        
        # Find earliest version that contains the file
        versions_with_file = [
            v for v in repository.versions.values()
            if file_path in v.content_snapshot and v.created_at < min(version_a.created_at, version_b.created_at)
        ]
        
        if versions_with_file:
            latest_common = max(versions_with_file, key=lambda x: x.created_at)
            return latest_common.content_snapshot.get(file_path)
        
        return None
    
    async def _merge_content(
        self,
        source_content: Dict[str, Any],
        target_content: Dict[str, Any],
        strategy: str = "auto"
    ) -> Dict[str, Any]:
        """Merge content from two versions"""
        merged_content = target_content.copy()
        
        if strategy == "auto":
            # Simple auto-merge: add new files, keep target for conflicts
            for file_path, content in source_content.items():
                if file_path not in merged_content:
                    merged_content[file_path] = content
        elif strategy == "source_wins":
            merged_content.update(source_content)
        elif strategy == "target_wins":
            # Already using target content as base
            pass
        
        return merged_content
    
    async def _create_merge_changes(
        self,
        source_version: Version,
        target_version: Version,
        merged_by: str
    ) -> List[VersionChange]:
        """Create changes for a merge commit"""
        merge_changes = [
            VersionChange(
                change_id=str(uuid.uuid4()),
                change_type=ChangeType.MERGE,
                author_id=merged_by,
                timestamp=datetime.now(),
                file_path="*",
                description=f"Merge {source_version.branch_name} into {target_version.branch_name}",
                metadata={
                    'source_version': source_version.version_id,
                    'target_version': target_version.version_id,
                    'source_branch': source_version.branch_name,
                    'target_branch': target_version.branch_name
                }
            )
        ]
        
        return merge_changes
    
    async def _execute_merge(self, merge_request: MergeRequest):
        """Execute an approved merge request"""
        try:
            # Find repository
            repo = None
            for repository in self.repositories.values():
                if (merge_request.source_branch in repository.branches and
                    merge_request.target_branch in repository.branches):
                    repo = repository
                    break
            
            if not repo:
                raise ValueError("Repository not found for merge request")
            
            # Execute merge
            await self.merge_branches(
                repo.repo_id,
                merge_request.source_branch,
                merge_request.target_branch,
                "auto",
                merge_request.author_id
            )
            
            merge_request.status = "merged"
            
            logger.info(f"Executed merge for request {merge_request.merge_id}")
            
        except Exception as e:
            logger.error(f"Error executing merge: {str(e)}")
            merge_request.status = "failed"
    
    async def _cleanup_old_versions(self):
        """Cleanup old versions to stay within limits"""
        while True:
            try:
                for repository in self.repositories.values():
                    if len(repository.versions) > self.max_versions:
                        # Keep the most recent versions
                        versions_by_date = sorted(
                            repository.versions.values(),
                            key=lambda x: x.created_at,
                            reverse=True
                        )
                        
                        versions_to_keep = versions_by_date[:self.max_versions]
                        versions_to_remove = versions_by_date[self.max_versions:]
                        
                        for version in versions_to_remove:
                            if version.status != VersionStatus.PUBLISHED:  # Keep published versions
                                del repository.versions[version.version_id]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in version cleanup: {str(e)}")
                await asyncio.sleep(300)
    
    async def _resolve_stale_conflicts(self):
        """Resolve conflicts that have been open too long"""
        while True:
            try:
                current_time = datetime.now()
                stale_conflicts = []
                
                for version_id, conflicts in self.active_conflicts.items():
                    for conflict in conflicts:
                        if not conflict.resolution:
                            # Check if conflict is stale
                            if hasattr(conflict, 'created_at'):
                                age = (current_time - conflict.created_at).seconds
                                if age > self.conflict_timeout:
                                    stale_conflicts.append((version_id, conflict))
                
                # Auto-resolve stale conflicts (accept target)
                for version_id, conflict in stale_conflicts:
                    await self.resolve_conflict(
                        conflict.conflict_id,
                        conflict.remote_content,
                        "system",
                        ConflictResolution.ACCEPT_THEIRS
                    )
                
                await asyncio.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                logger.error(f"Error resolving stale conflicts: {str(e)}")
                await asyncio.sleep(300)
    
    async def _save_repository_state(self, repository: Repository):
        """Save repository state to persistent storage"""
        # In real implementation, save to database
        logger.debug(f"Saving state for repository {repository.repo_id}")


# Export main classes
__all__ = [
    'VersionControl', 'Repository', 'Version', 'Branch', 'VersionChange', 'MergeRequest', 'Conflict',
    'VersionStatus', 'ChangeType', 'ConflictResolution'
]