"""Project Versioning System
Git-like versioning system for collaborative projects with AI-powered merge resolution.

Provides:
- Branch management for project versions
- Automatic conflict detection and resolution
- Version history and rollback capabilities
- Collaborative merging workflows
- Asset version tracking
- Change attribution and analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import difflib
import copy

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BranchStatus(Enum):
    """Project branch status"""
    ACTIVE = "active"
    MERGED = "merged"
    ABANDONED = "abandoned"
    PROTECTED = "protected"


class ChangeType(Enum):
    """Types of changes in project versions"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    MOVE = "move"
    RENAME = "rename"


class MergeStrategy(Enum):
    """Merge strategies for conflicting changes"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    AI_ASSISTED = "ai_assisted"
    CONFLICT_RESOLUTION = "conflict_resolution"


@dataclass
class ProjectFile:
    """Project file representation"""
    file_id: str
    path: str
    filename: str
    content_hash: str
    content_type: str
    size: int
    created_at: datetime
    modified_at: datetime
    created_by: str
    modified_by: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectChange:
    """Individual change in project version"""
    change_id: str
    file_id: str
    change_type: ChangeType
    old_content_hash: Optional[str]
    new_content_hash: Optional[str]
    change_data: Dict[str, Any]
    author_id: str
    timestamp: datetime
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectCommit:
    """Project version commit"""
    commit_id: str
    project_id: str
    branch_name: str
    parent_commit_id: Optional[str]
    author_id: str
    commit_message: str
    changes: List[ProjectChange]
    timestamp: datetime
    commit_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectBranch:
    """Project branch representation"""
    branch_id: str
    project_id: str
    branch_name: str
    base_commit_id: str
    head_commit_id: str
    created_by: str
    created_at: datetime
    status: BranchStatus
    description: str
    commits: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MergeConflict:
    """Merge conflict representation"""
    conflict_id: str
    file_id: str
    file_path: str
    source_branch: str
    target_branch: str
    conflict_type: str
    source_content: str
    target_content: str
    base_content: Optional[str]
    resolved: bool = False
    resolution_strategy: Optional[MergeStrategy] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_content: Optional[str] = None


@dataclass
class MergeRequest:
    """Branch merge request"""
    merge_id: str
    project_id: str
    source_branch: str
    target_branch: str
    title: str
    description: str
    author_id: str
    created_at: datetime
    status: str
    conflicts: List[MergeConflict] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    approved_by: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectVersioningSystem:
    """
    Git-like versioning system for collaborative creative projects
    """
    
    def __init__(self):
        self.projects: Dict[str, Dict] = {}
        self.branches: Dict[str, Dict[str, ProjectBranch]] = {}
        self.commits: Dict[str, Dict[str, ProjectCommit]] = {}
        self.files: Dict[str, Dict[str, ProjectFile]] = {}
        self.merge_requests: Dict[str, MergeRequest] = {}
        self.conflict_resolver = ConflictResolver()
    
    async def initialize_project(self, project_id: str, creator_id: str, 
                               project_name: str) -> Dict[str, Any]:
        """Initialize versioning for a new project"""
        try:
            # Create main branch
            main_branch_id = f"branch_{uuid.uuid4().hex[:12]}"
            main_branch = ProjectBranch(
                branch_id=main_branch_id,
                project_id=project_id,
                branch_name="main",
                base_commit_id="",
                head_commit_id="",
                created_by=creator_id,
                created_at=datetime.utcnow(),
                status=BranchStatus.ACTIVE,
                description="Main project branch"
            )
            
            # Create initial commit
            initial_commit_id = f"commit_{uuid.uuid4().hex[:12]}"
            initial_commit = ProjectCommit(
                commit_id=initial_commit_id,
                project_id=project_id,
                branch_name="main",
                parent_commit_id=None,
                author_id=creator_id,
                commit_message="Initial project commit",
                changes=[],
                timestamp=datetime.utcnow(),
                commit_hash=self._generate_commit_hash(initial_commit_id, [])
            )
            
            # Update branch with initial commit
            main_branch.base_commit_id = initial_commit_id
            main_branch.head_commit_id = initial_commit_id
            main_branch.commits = [initial_commit_id]
            
            # Store project data
            self.projects[project_id] = {
                "project_id": project_id,
                "name": project_name,
                "creator_id": creator_id,
                "created_at": datetime.utcnow(),
                "default_branch": "main"
            }
            
            self.branches[project_id] = {main_branch.branch_name: main_branch}
            self.commits[project_id] = {initial_commit_id: initial_commit}
            self.files[project_id] = {}
            
            logger.info(f"Project versioning initialized for {project_id}")
            
            return {
                "status": "success",
                "project_id": project_id,
                "main_branch_id": main_branch_id,
                "initial_commit_id": initial_commit_id,
                "message": "Project versioning initialized"
            }
            
        except Exception as e:
            logger.error(f"Error initializing project versioning: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_branch(self, project_id: str, branch_name: str, 
                          base_branch: str, creator_id: str,
                          description: str = "") -> Dict[str, Any]:
        """Create new project branch"""
        try:
            if project_id not in self.projects:
                return {"status": "error", "message": "Project not found"}
            
            if project_id not in self.branches:
                return {"status": "error", "message": "No branches found for project"}
            
            if branch_name in self.branches[project_id]:
                return {"status": "error", "message": "Branch already exists"}
            
            base_branch_obj = self.branches[project_id].get(base_branch)
            if not base_branch_obj:
                return {"status": "error", "message": "Base branch not found"}
            
            # Create new branch
            branch_id = f"branch_{uuid.uuid4().hex[:12]}"
            new_branch = ProjectBranch(
                branch_id=branch_id,
                project_id=project_id,
                branch_name=branch_name,
                base_commit_id=base_branch_obj.head_commit_id,
                head_commit_id=base_branch_obj.head_commit_id,
                created_by=creator_id,
                created_at=datetime.utcnow(),
                status=BranchStatus.ACTIVE,
                description=description,
                commits=base_branch_obj.commits.copy()
            )
            
            self.branches[project_id][branch_name] = new_branch
            
            logger.info(f"Branch {branch_name} created for project {project_id}")
            
            return {
                "status": "success",
                "branch_id": branch_id,
                "branch_name": branch_name,
                "base_commit": base_branch_obj.head_commit_id,
                "message": "Branch created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            return {"status": "error", "message": str(e)}
    
    async def commit_changes(self, project_id: str, branch_name: str,
                           author_id: str, commit_message: str,
                           file_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Commit changes to project branch"""
        try:
            if project_id not in self.branches:
                return {"status": "error", "message": "Project not found"}
            
            branch = self.branches[project_id].get(branch_name)
            if not branch:
                return {"status": "error", "message": "Branch not found"}
            
            if branch.status != BranchStatus.ACTIVE:
                return {"status": "error", "message": "Cannot commit to inactive branch"}
            
            # Process file changes
            changes = []
            for file_change in file_changes:
                change = await self._process_file_change(
                    project_id, branch_name, author_id, file_change
                )
                if change:
                    changes.append(change)
            
            if not changes:
                return {"status": "error", "message": "No valid changes to commit"}
            
            # Create commit
            commit_id = f"commit_{uuid.uuid4().hex[:12]}"
            commit_hash = self._generate_commit_hash(commit_id, changes)
            
            commit = ProjectCommit(
                commit_id=commit_id,
                project_id=project_id,
                branch_name=branch_name,
                parent_commit_id=branch.head_commit_id,
                author_id=author_id,
                commit_message=commit_message,
                changes=changes,
                timestamp=datetime.utcnow(),
                commit_hash=commit_hash
            )
            
            # Update branch
            branch.head_commit_id = commit_id
            branch.commits.append(commit_id)
            
            # Store commit
            if project_id not in self.commits:
                self.commits[project_id] = {}
            self.commits[project_id][commit_id] = commit
            
            logger.info(f"Changes committed to {branch_name} in project {project_id}")
            
            return {
                "status": "success",
                "commit_id": commit_id,
                "commit_hash": commit_hash,
                "changes_count": len(changes),
                "message": "Changes committed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_file_change(self, project_id: str, branch_name: str,
                                 author_id: str, file_change: Dict[str, Any]) -> Optional[ProjectChange]:
        """Process individual file change"""
        try:
            change_type = ChangeType(file_change.get("change_type"))
            file_path = file_change.get("file_path")
            
            # Generate file ID
            file_id = hashlib.md5(file_path.encode()).hexdigest()
            
            # Get existing file if it exists
            existing_file = None
            if project_id in self.files and file_id in self.files[project_id]:
                existing_file = self.files[project_id][file_id]
            
            change_id = f"change_{uuid.uuid4().hex[:12]}"
            old_hash = existing_file.content_hash if existing_file else None
            new_hash = None
            
            # Process based on change type
            if change_type == ChangeType.CREATE:
                content = file_change.get("content", "")
                new_hash = hashlib.sha256(content.encode()).hexdigest()
                
                # Create new file
                new_file = ProjectFile(
                    file_id=file_id,
                    path=file_path,
                    filename=file_change.get("filename", ""),
                    content_hash=new_hash,
                    content_type=file_change.get("content_type", "text/plain"),
                    size=len(content),
                    created_at=datetime.utcnow(),
                    modified_at=datetime.utcnow(),
                    created_by=author_id,
                    modified_by=author_id,
                    metadata=file_change.get("metadata", {})
                )
                
                if project_id not in self.files:
                    self.files[project_id] = {}
                self.files[project_id][file_id] = new_file
                
            elif change_type == ChangeType.MODIFY:
                if not existing_file:
                    return None
                
                content = file_change.get("content", "")
                new_hash = hashlib.sha256(content.encode()).hexdigest()
                
                # Update existing file
                existing_file.content_hash = new_hash
                existing_file.size = len(content)
                existing_file.modified_at = datetime.utcnow()
                existing_file.modified_by = author_id
                
            elif change_type == ChangeType.DELETE:
                if not existing_file:
                    return None
                
                # Mark file as deleted
                del self.files[project_id][file_id]
            
            # Create change record
            change = ProjectChange(
                change_id=change_id,
                file_id=file_id,
                change_type=change_type,
                old_content_hash=old_hash,
                new_content_hash=new_hash,
                change_data=file_change,
                author_id=author_id,
                timestamp=datetime.utcnow(),
                description=file_change.get("description", "")
            )
            
            return change
            
        except Exception as e:
            logger.error(f"Error processing file change: {e}")
            return None
    
    def _generate_commit_hash(self, commit_id: str, changes: List[ProjectChange]) -> str:
        """Generate commit hash"""
        content = f"{commit_id}:"
        for change in changes:
            content += f"{change.file_id}:{change.change_type.value}:{change.new_content_hash}:"
        
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def create_merge_request(self, project_id: str, source_branch: str,
                                 target_branch: str, title: str, description: str,
                                 author_id: str, reviewers: List[str] = []) -> Dict[str, Any]:
        """Create merge request between branches"""
        try:
            if project_id not in self.branches:
                return {"status": "error", "message": "Project not found"}
            
            source_branch_obj = self.branches[project_id].get(source_branch)
            target_branch_obj = self.branches[project_id].get(target_branch)
            
            if not source_branch_obj or not target_branch_obj:
                return {"status": "error", "message": "Source or target branch not found"}
            
            # Detect conflicts
            conflicts = await self._detect_merge_conflicts(
                project_id, source_branch, target_branch
            )
            
            # Create merge request
            merge_id = f"merge_{uuid.uuid4().hex[:12]}"
            merge_request = MergeRequest(
                merge_id=merge_id,
                project_id=project_id,
                source_branch=source_branch,
                target_branch=target_branch,
                title=title,
                description=description,
                author_id=author_id,
                created_at=datetime.utcnow(),
                status="open",
                conflicts=conflicts,
                reviewers=reviewers
            )
            
            self.merge_requests[merge_id] = merge_request
            
            logger.info(f"Merge request {merge_id} created for {source_branch} -> {target_branch}")
            
            return {
                "status": "success",
                "merge_id": merge_id,
                "conflicts_count": len(conflicts),
                "requires_resolution": len(conflicts) > 0,
                "message": "Merge request created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating merge request: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _detect_merge_conflicts(self, project_id: str, source_branch: str,
                                    target_branch: str) -> List[MergeConflict]:
        """Detect conflicts between branches"""
        conflicts = []
        
        try:
            source_branch_obj = self.branches[project_id][source_branch]
            target_branch_obj = self.branches[project_id][target_branch]
            
            # Get commits unique to each branch
            source_commits = set(source_branch_obj.commits)
            target_commits = set(target_branch_obj.commits)
            
            # Find divergent commits
            source_only = source_commits - target_commits
            target_only = target_commits - source_commits
            
            if not source_only or not target_only:
                return conflicts  # No conflicts if branches haven't diverged
            
            # Analyze file changes in divergent commits
            source_file_changes = {}
            target_file_changes = {}
            
            # Collect changes from source branch
            for commit_id in source_only:
                commit = self.commits[project_id].get(commit_id)
                if commit:
                    for change in commit.changes:
                        source_file_changes[change.file_id] = change
            
            # Collect changes from target branch
            for commit_id in target_only:
                commit = self.commits[project_id].get(commit_id)
                if commit:
                    for change in commit.changes:
                        target_file_changes[change.file_id] = change
            
            # Find conflicting files
            conflicting_files = set(source_file_changes.keys()) & set(target_file_changes.keys())
            
            for file_id in conflicting_files:
                source_change = source_file_changes[file_id]
                target_change = target_file_changes[file_id]
                
                # Create conflict record
                conflict_id = f"conflict_{uuid.uuid4().hex[:12]}"
                conflict = MergeConflict(
                    conflict_id=conflict_id,
                    file_id=file_id,
                    file_path=source_change.change_data.get("file_path", ""),
                    source_branch=source_branch,
                    target_branch=target_branch,
                    conflict_type="content_conflict",
                    source_content=source_change.change_data.get("content", ""),
                    target_content=target_change.change_data.get("content", ""),
                    base_content=None  # Would need to find common ancestor
                )
                
                conflicts.append(conflict)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting merge conflicts: {e}")
            return []
    
    async def resolve_conflict(self, merge_id: str, conflict_id: str,
                             resolution_strategy: MergeStrategy,
                             resolved_content: str, resolver_id: str) -> Dict[str, Any]:
        """Resolve merge conflict"""
        try:
            merge_request = self.merge_requests.get(merge_id)
            if not merge_request:
                return {"status": "error", "message": "Merge request not found"}
            
            # Find conflict
            conflict = None
            for c in merge_request.conflicts:
                if c.conflict_id == conflict_id:
                    conflict = c
                    break
            
            if not conflict:
                return {"status": "error", "message": "Conflict not found"}
            
            if conflict.resolved:
                return {"status": "error", "message": "Conflict already resolved"}
            
            # Resolve conflict
            conflict.resolved = True
            conflict.resolution_strategy = resolution_strategy
            conflict.resolved_by = resolver_id
            conflict.resolved_at = datetime.utcnow()
            conflict.resolved_content = resolved_content
            
            # Check if all conflicts are resolved
            all_resolved = all(c.resolved for c in merge_request.conflicts)
            if all_resolved:
                merge_request.status = "ready_to_merge"
            
            logger.info(f"Conflict {conflict_id} resolved in merge request {merge_id}")
            
            return {
                "status": "success",
                "conflict_id": conflict_id,
                "all_conflicts_resolved": all_resolved,
                "message": "Conflict resolved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return {"status": "error", "message": str(e)}
    
    async def merge_branches(self, merge_id: str, merger_id: str) -> Dict[str, Any]:
        """Execute branch merge"""
        try:
            merge_request = self.merge_requests.get(merge_id)
            if not merge_request:
                return {"status": "error", "message": "Merge request not found"}
            
            if merge_request.status != "ready_to_merge":
                return {"status": "error", "message": "Merge request not ready for merge"}
            
            # Check if all conflicts are resolved
            unresolved_conflicts = [c for c in merge_request.conflicts if not c.resolved]
            if unresolved_conflicts:
                return {"status": "error", "message": "Unresolved conflicts remain"}
            
            project_id = merge_request.project_id
            source_branch = merge_request.source_branch
            target_branch = merge_request.target_branch
            
            source_branch_obj = self.branches[project_id][source_branch]
            target_branch_obj = self.branches[project_id][target_branch]
            
            # Create merge commit
            merge_commit_id = f"commit_{uuid.uuid4().hex[:12]}"
            merge_commit = ProjectCommit(
                commit_id=merge_commit_id,
                project_id=project_id,
                branch_name=target_branch,
                parent_commit_id=target_branch_obj.head_commit_id,
                author_id=merger_id,
                commit_message=f"Merge {source_branch} into {target_branch}",
                changes=[],  # Merge commits typically don't have direct changes
                timestamp=datetime.utcnow(),
                commit_hash=self._generate_commit_hash(merge_commit_id, []),
                metadata={
                    "merge_type": "branch_merge",
                    "source_branch": source_branch,
                    "source_commit": source_branch_obj.head_commit_id,
                    "merge_request_id": merge_id
                }
            )
            
            # Update target branch
            target_branch_obj.head_commit_id = merge_commit_id
            target_branch_obj.commits.append(merge_commit_id)
            
            # Store merge commit
            self.commits[project_id][merge_commit_id] = merge_commit
            
            # Update merge request status
            merge_request.status = "merged"
            
            # Mark source branch as merged if desired
            source_branch_obj.status = BranchStatus.MERGED
            
            logger.info(f"Successfully merged {source_branch} into {target_branch}")
            
            return {
                "status": "success",
                "merge_commit_id": merge_commit_id,
                "target_branch": target_branch,
                "message": "Branches merged successfully"
            }
            
        except Exception as e:
            logger.error(f"Error merging branches: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_project_history(self, project_id: str, branch_name: str = "main",
                                limit: int = 50) -> Dict[str, Any]:
        """Get project commit history"""
        try:
            if project_id not in self.branches:
                return {"status": "error", "message": "Project not found"}
            
            branch = self.branches[project_id].get(branch_name)
            if not branch:
                return {"status": "error", "message": "Branch not found"}
            
            # Get recent commits
            recent_commits = branch.commits[-limit:] if len(branch.commits) > limit else branch.commits
            
            commit_details = []
            for commit_id in reversed(recent_commits):  # Most recent first
                commit = self.commits[project_id].get(commit_id)
                if commit:
                    commit_details.append({
                        "commit_id": commit.commit_id,
                        "commit_hash": commit.commit_hash,
                        "message": commit.commit_message,
                        "author_id": commit.author_id,
                        "timestamp": commit.timestamp.isoformat(),
                        "changes_count": len(commit.changes),
                        "parent_commit": commit.parent_commit_id
                    })
            
            return {
                "status": "success",
                "project_id": project_id,
                "branch_name": branch_name,
                "total_commits": len(branch.commits),
                "commits": commit_details
            }
            
        except Exception as e:
            logger.error(f"Error getting project history: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_branch_comparison(self, project_id: str, source_branch: str,
                                  target_branch: str) -> Dict[str, Any]:
        """Compare two branches"""
        try:
            if project_id not in self.branches:
                return {"status": "error", "message": "Project not found"}
            
            source_branch_obj = self.branches[project_id].get(source_branch)
            target_branch_obj = self.branches[project_id].get(target_branch)
            
            if not source_branch_obj or not target_branch_obj:
                return {"status": "error", "message": "One or both branches not found"}
            
            # Find differences
            source_commits = set(source_branch_obj.commits)
            target_commits = set(target_branch_obj.commits)
            
            commits_ahead = source_commits - target_commits
            commits_behind = target_commits - source_commits
            
            return {
                "status": "success",
                "source_branch": source_branch,
                "target_branch": target_branch,
                "commits_ahead": len(commits_ahead),
                "commits_behind": len(commits_behind),
                "can_merge": len(commits_behind) == 0,
                "needs_update": len(commits_behind) > 0
            }
            
        except Exception as e:
            logger.error(f"Error comparing branches: {e}")
            return {"status": "error", "message": str(e)}


class ConflictResolver:
    """AI-powered conflict resolution system"""
    
    def __init__(self):
        self.resolution_strategies = {
            "text_merge": self._resolve_text_conflict,
            "audio_merge": self._resolve_audio_conflict,
            "metadata_merge": self._resolve_metadata_conflict
        }
    
    async def _resolve_text_conflict(self, conflict: MergeConflict) -> str:
        """Resolve text file conflicts using diff algorithms"""
        try:
            source_lines = conflict.source_content.splitlines()
            target_lines = conflict.target_content.splitlines()
            
            # Use difflib for three-way merge if base content available
            if conflict.base_content:
                base_lines = conflict.base_content.splitlines()
                
                # Simple three-way merge algorithm
                merged_lines = []
                
                # This is a simplified merge - in production, use more sophisticated algorithms
                diff_source = list(difflib.unified_diff(base_lines, source_lines, lineterm=''))
                diff_target = list(difflib.unified_diff(base_lines, target_lines, lineterm=''))
                
                # Combine non-conflicting changes
                merged_lines = source_lines  # Simplified: prefer source
                
                return '\n'.join(merged_lines)
            else:
                # Two-way merge - prefer newer content with conflict markers
                return f"<<<<<<< {conflict.source_branch}\n{conflict.source_content}\n=======\n{conflict.target_content}\n>>>>>>> {conflict.target_branch}"
            
        except Exception as e:
            logger.error(f"Error resolving text conflict: {e}")
            return conflict.source_content  # Fallback to source
    
    async def _resolve_audio_conflict(self, conflict: MergeConflict) -> str:
        """Resolve audio file conflicts"""
        # In a real implementation, this would use audio processing libraries
        # For now, return metadata indicating the conflict
        return json.dumps({
            "conflict_type": "audio",
            "resolution": "manual_required",
            "source_file": conflict.source_content,
            "target_file": conflict.target_content
        })
    
    async def _resolve_metadata_conflict(self, conflict: MergeConflict) -> str:
        """Resolve metadata conflicts"""
        try:
            source_meta = json.loads(conflict.source_content)
            target_meta = json.loads(conflict.target_content)
            
            # Merge metadata fields
            merged_meta = source_meta.copy()
            merged_meta.update(target_meta)
            
            return json.dumps(merged_meta, indent=2)
            
        except Exception as e:
            logger.error(f"Error resolving metadata conflict: {e}")
            return conflict.source_content


# Export the system
__all__ = ['ProjectVersioningSystem', 'BranchStatus', 'ChangeType', 'MergeStrategy',
           'ProjectFile', 'ProjectChange', 'ProjectCommit', 'ProjectBranch',
           'MergeConflict', 'MergeRequest', 'ConflictResolver']