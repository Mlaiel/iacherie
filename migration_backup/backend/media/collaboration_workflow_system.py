"""Collaboration Workflow System - Enterprise Creative Collaboration Platform
========================================================================

Consolidated collaboration system providing comprehensive workflow management,
real-time collaboration tools, team workspaces, and approval workflows.

Consolidates:
- Real-time collaboration tools and live editing (collaboration_tools.py)
- Workflow management and coordination engine (collaboration_workflow_engine.py)  
- Team media workspace and project coordination (team_media_workspace.py)
- Approval workflow management and review processes (approval_workflow_manager.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary collaboration system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or workflow appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
from collections import defaultdict
from pathlib import Path

# External dependencies with graceful fallbacks
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    logging.warning("Websockets not available - using polling for real-time features")

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("Redis not available - using in-memory state management")

try:
    from celery import Celery
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False
    logging.warning("Celery not available - using basic task management")

try:
    from socketio import AsyncServer
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False
    logging.warning("Socket.IO not available - using basic WebSocket implementation")

logger = logging.getLogger(__name__)


class CollaborationEventType(Enum):
    """Collaboration event types"""
    JOIN_SESSION = "join_session"
    LEAVE_SESSION = "leave_session"
    CONTENT_UPDATE = "content_update"
    COMMENT_ADD = "comment_add"
    ANNOTATION_ADD = "annotation_add"
    CURSOR_MOVE = "cursor_move"
    SELECTION_CHANGE = "selection_change"
    VERSION_SAVE = "version_save"
    PERMISSION_CHANGE = "permission_change"
    NOTIFICATION = "notification"


class WorkflowStatus(Enum):
    """Workflow status types"""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PAUSED = "paused"


class WorkflowType(Enum):
    """Workflow types"""
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    REVIEW_APPROVAL = "review_approval"
    PUBLISHING = "publishing"
    CAMPAIGN = "campaign"
    PROJECT_MANAGEMENT = "project_management"


class PermissionLevel(Enum):
    """Permission levels for collaboration"""
    VIEWER = "viewer"
    COMMENTER = "commenter"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"


class ApprovalStatus(Enum):
    """Approval status types"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    EXPIRED = "expired"


@dataclass
class CollaborationConfig:
    """Collaboration system configuration"""
    real_time_sync: bool = True
    auto_save_interval: int = 30  # seconds
    max_concurrent_users: int = 50
    version_history_limit: int = 100
    notification_enabled: bool = True
    approval_timeout_hours: int = 72
    workspace_retention_days: int = 365


@dataclass
class User:
    """User representation"""
    user_id: str
    username: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    permission_level: PermissionLevel = PermissionLevel.VIEWER
    is_online: bool = False
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CollaborationSession:
    """Real-time collaboration session"""
    session_id: str
    project_id: str
    active_users: List[User] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Comment:
    """Comment on content"""
    comment_id: str
    content_id: str
    user_id: str
    text: str
    position: Optional[Dict[str, Any]] = None  # Position in content
    thread_id: Optional[str] = None
    parent_comment_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    resolved: bool = False


@dataclass
class Annotation:
    """Content annotation"""
    annotation_id: str
    content_id: str
    user_id: str
    annotation_type: str  # highlight, note, suggestion
    content: str
    position: Dict[str, Any]  # Position/selection data
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False


@dataclass
class WorkflowTask:
    """Individual workflow task"""
    task_id: str
    workflow_id: str
    name: str
    description: str
    assigned_to: List[str]  # User IDs
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: int = 1  # 1-5 scale
    due_date: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class Workflow:
    """Collaboration workflow definition"""
    workflow_id: str
    name: str
    description: str
    workflow_type: WorkflowType
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_by: str
    tasks: List[WorkflowTask] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)  # User IDs
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ApprovalRequest:
    """Approval request for content or workflow"""
    request_id: str
    content_id: str
    workflow_id: Optional[str] = None
    requester_id: str
    approvers: List[str] = field(default_factory=list)  # User IDs
    status: ApprovalStatus = ApprovalStatus.PENDING
    message: Optional[str] = None
    deadline: Optional[datetime] = None
    approvals: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # approver_id -> decision
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class TeamWorkspace:
    """Team collaboration workspace"""
    workspace_id: str
    name: str
    description: str
    owner_id: str
    members: List[User] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)  # Project IDs
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RealTimeCollaborationManager:
    """Manages real-time collaboration features"""
    
    def __init__(self, config: CollaborationConfig):
        self.config = config
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)  # user_id -> session_ids
        self.websocket_connections: Dict[str, Any] = {}
        
        if HAS_REDIS:
            self.redis_client = redis.Redis(decode_responses=True)
        else:
            self.redis_client = None
        
        logger.info("🔄 Real-time Collaboration Manager initialized")
    
    async def create_session(self, project_id: str, creator_user: User) -> CollaborationSession:
        """Create new collaboration session"""
        try:
            session_id = str(uuid.uuid4())
            
            session = CollaborationSession(
                session_id=session_id,
                project_id=project_id,
                active_users=[creator_user]
            )
            
            self.active_sessions[session_id] = session
            self.user_sessions[creator_user.user_id].add(session_id)
            
            await self._notify_session_event(session_id, CollaborationEventType.JOIN_SESSION, {
                'user': self._serialize_user(creator_user),
                'session_id': session_id
            })
            
            logger.info(f"Created collaboration session {session_id} for project {project_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create collaboration session: {e}")
            raise
    
    async def join_session(self, session_id: str, user: User) -> bool:
        """User joins collaboration session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            # Check if user already in session
            if any(u.user_id == user.user_id for u in session.active_users):
                return True
            
            # Check concurrent user limit
            if len(session.active_users) >= self.config.max_concurrent_users:
                return False
            
            session.active_users.append(user)
            session.last_activity = datetime.now(timezone.utc)
            self.user_sessions[user.user_id].add(session_id)
            
            await self._notify_session_event(session_id, CollaborationEventType.JOIN_SESSION, {
                'user': self._serialize_user(user),
                'active_users_count': len(session.active_users)
            })
            
            logger.info(f"User {user.user_id} joined session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join session: {e}")
            return False
    
    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """User leaves collaboration session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            # Remove user from session
            session.active_users = [u for u in session.active_users if u.user_id != user_id]
            session.last_activity = datetime.now(timezone.utc)
            
            if session_id in self.user_sessions[user_id]:
                self.user_sessions[user_id].remove(session_id)
            
            await self._notify_session_event(session_id, CollaborationEventType.LEAVE_SESSION, {
                'user_id': user_id,
                'active_users_count': len(session.active_users)
            })
            
            # Clean up empty sessions
            if not session.active_users:
                del self.active_sessions[session_id]
            
            logger.info(f"User {user_id} left session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to leave session: {e}")
            return False
    
    async def broadcast_content_update(
        self, 
        session_id: str, 
        user_id: str, 
        update_data: Dict[str, Any]
    ) -> bool:
        """Broadcast content update to all session participants"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            event_data = {
                'user_id': user_id,
                'update_data': update_data,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            await self._notify_session_event(
                session_id, 
                CollaborationEventType.CONTENT_UPDATE, 
                event_data
            )
            
            # Auto-save if interval reached
            if self.config.real_time_sync:
                await self._trigger_auto_save(session_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to broadcast content update: {e}")
            return False
    
    async def add_comment(
        self, 
        session_id: str, 
        comment: Comment
    ) -> bool:
        """Add comment and notify session participants"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            # Store comment (would use database in production)
            comment_data = self._serialize_comment(comment)
            
            await self._notify_session_event(
                session_id, 
                CollaborationEventType.COMMENT_ADD, 
                comment_data
            )
            
            logger.info(f"Comment added to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            return False
    
    async def add_annotation(
        self, 
        session_id: str, 
        annotation: Annotation
    ) -> bool:
        """Add annotation and notify session participants"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            annotation_data = self._serialize_annotation(annotation)
            
            await self._notify_session_event(
                session_id, 
                CollaborationEventType.ANNOTATION_ADD, 
                annotation_data
            )
            
            logger.info(f"Annotation added to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add annotation: {e}")
            return False
    
    async def _notify_session_event(
        self, 
        session_id: str, 
        event_type: CollaborationEventType, 
        data: Dict[str, Any]
    ):
        """Notify all session participants of event"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        event_payload = {
            'type': event_type.value,
            'session_id': session_id,
            'data': data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Send to all active users (would use WebSocket/Socket.IO in production)
        for user in session.active_users:
            await self._send_to_user(user.user_id, event_payload)
    
    async def _send_to_user(self, user_id: str, payload: Dict[str, Any]):
        """Send payload to specific user"""
        # Placeholder for WebSocket implementation
        logger.debug(f"Sending to user {user_id}: {payload['type']}")
    
    async def _trigger_auto_save(self, session_id: str):
        """Trigger auto-save for session"""
        # Placeholder for auto-save implementation
        logger.debug(f"Auto-save triggered for session {session_id}")
    
    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user for transmission"""
        return {
            'user_id': user.user_id,
            'username': user.username,
            'display_name': user.display_name,
            'avatar_url': user.avatar_url,
            'permission_level': user.permission_level.value,
            'is_online': user.is_online
        }
    
    def _serialize_comment(self, comment: Comment) -> Dict[str, Any]:
        """Serialize comment for transmission"""
        return {
            'comment_id': comment.comment_id,
            'content_id': comment.content_id,
            'user_id': comment.user_id,
            'text': comment.text,
            'position': comment.position,
            'thread_id': comment.thread_id,
            'parent_comment_id': comment.parent_comment_id,
            'created_at': comment.created_at.isoformat(),
            'resolved': comment.resolved
        }
    
    def _serialize_annotation(self, annotation: Annotation) -> Dict[str, Any]:
        """Serialize annotation for transmission"""
        return {
            'annotation_id': annotation.annotation_id,
            'content_id': annotation.content_id,
            'user_id': annotation.user_id,
            'annotation_type': annotation.annotation_type,
            'content': annotation.content,
            'position': annotation.position,
            'created_at': annotation.created_at.isoformat(),
            'resolved': annotation.resolved
        }


class WorkflowEngine:
    """Manages collaboration workflows and task coordination"""
    
    def __init__(self, config: CollaborationConfig):
        self.config = config
        self.workflows: Dict[str, Workflow] = {}
        self.task_queue = []
        
        if HAS_CELERY:
            self.celery_app = Celery('workflow_engine')
        else:
            self.celery_app = None
        
        logger.info("⚙️ Workflow Engine initialized")
    
    async def create_workflow(
        self, 
        name: str,
        description: str,
        workflow_type: WorkflowType,
        created_by: str,
        participants: List[str],
        deadline: Optional[datetime] = None
    ) -> Workflow:
        """Create new collaboration workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            workflow = Workflow(
                workflow_id=workflow_id,
                name=name,
                description=description,
                workflow_type=workflow_type,
                created_by=created_by,
                participants=participants,
                deadline=deadline
            )
            
            self.workflows[workflow_id] = workflow
            
            # Notify participants
            await self._notify_workflow_created(workflow)
            
            logger.info(f"Created workflow {workflow_id}: {name}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def add_task(
        self, 
        workflow_id: str,
        name: str,
        description: str,
        assigned_to: List[str],
        priority: int = 1,
        due_date: Optional[datetime] = None,
        dependencies: Optional[List[str]] = None
    ) -> WorkflowTask:
        """Add task to workflow"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            task_id = str(uuid.uuid4())
            
            task = WorkflowTask(
                task_id=task_id,
                workflow_id=workflow_id,
                name=name,
                description=description,
                assigned_to=assigned_to,
                priority=priority,
                due_date=due_date,
                dependencies=dependencies or []
            )
            
            workflow.tasks.append(task)
            workflow.updated_at = datetime.now(timezone.utc)
            
            # Notify assigned users
            await self._notify_task_assigned(task)
            
            logger.info(f"Added task {task_id} to workflow {workflow_id}")
            return task
            
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            raise
    
    async def update_task_status(
        self, 
        task_id: str, 
        new_status: WorkflowStatus,
        updated_by: str
    ) -> bool:
        """Update task status"""
        try:
            task = self._find_task(task_id)
            if not task:
                return False
            
            old_status = task.status
            task.status = new_status
            
            if new_status == WorkflowStatus.COMPLETED:
                task.completed_at = datetime.now(timezone.utc)
            
            # Update workflow status if needed
            workflow = self.workflows.get(task.workflow_id)
            if workflow:
                await self._update_workflow_status(workflow)
            
            await self._notify_task_status_changed(task, old_status, updated_by)
            
            logger.info(f"Task {task_id} status changed: {old_status.value} -> {new_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            return False
    
    async def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow progress statistics"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return {}
            
            total_tasks = len(workflow.tasks)
            if total_tasks == 0:
                return {'progress': 0, 'total_tasks': 0, 'completed_tasks': 0}
            
            completed_tasks = sum(1 for task in workflow.tasks if task.status == WorkflowStatus.COMPLETED)
            in_progress_tasks = sum(1 for task in workflow.tasks if task.status == WorkflowStatus.IN_PROGRESS)
            pending_tasks = sum(1 for task in workflow.tasks if task.status == WorkflowStatus.PENDING)
            
            progress = (completed_tasks / total_tasks) * 100
            
            return {
                'workflow_id': workflow_id,
                'progress': progress,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_tasks': pending_tasks,
                'status': workflow.status.value,
                'deadline': workflow.deadline.isoformat() if workflow.deadline else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow progress: {e}")
            return {}
    
    async def _update_workflow_status(self, workflow: Workflow):
        """Update workflow status based on task statuses"""
        if not workflow.tasks:
            return
        
        completed_tasks = sum(1 for task in workflow.tasks if task.status == WorkflowStatus.COMPLETED)
        total_tasks = len(workflow.tasks)
        
        if completed_tasks == total_tasks:
            workflow.status = WorkflowStatus.COMPLETED
        elif completed_tasks > 0:
            workflow.status = WorkflowStatus.IN_PROGRESS
        else:
            workflow.status = WorkflowStatus.PENDING
        
        workflow.updated_at = datetime.now(timezone.utc)
    
    def _find_task(self, task_id: str) -> Optional[WorkflowTask]:
        """Find task by ID across all workflows"""
        for workflow in self.workflows.values():
            for task in workflow.tasks:
                if task.task_id == task_id:
                    return task
        return None
    
    async def _notify_workflow_created(self, workflow: Workflow):
        """Notify participants about new workflow"""
        # Placeholder for notification implementation
        logger.info(f"Notifying participants about workflow {workflow.workflow_id}")
    
    async def _notify_task_assigned(self, task: WorkflowTask):
        """Notify users about task assignment"""
        # Placeholder for notification implementation
        logger.info(f"Notifying users about task assignment {task.task_id}")
    
    async def _notify_task_status_changed(
        self, 
        task: WorkflowTask, 
        old_status: WorkflowStatus, 
        updated_by: str
    ):
        """Notify about task status change"""
        # Placeholder for notification implementation
        logger.info(f"Task {task.task_id} status changed by {updated_by}")


class ApprovalWorkflowManager:
    """Manages approval workflows and review processes"""
    
    def __init__(self, config: CollaborationConfig):
        self.config = config
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        
        logger.info("✅ Approval Workflow Manager initialized")
    
    async def create_approval_request(
        self, 
        content_id: str,
        requester_id: str,
        approvers: List[str],
        message: Optional[str] = None,
        workflow_id: Optional[str] = None,
        deadline_hours: Optional[int] = None
    ) -> ApprovalRequest:
        """Create new approval request"""
        try:
            request_id = str(uuid.uuid4())
            
            deadline = None
            if deadline_hours:
                deadline = datetime.now(timezone.utc) + timedelta(hours=deadline_hours)
            elif self.config.approval_timeout_hours > 0:
                deadline = datetime.now(timezone.utc) + timedelta(hours=self.config.approval_timeout_hours)
            
            request = ApprovalRequest(
                request_id=request_id,
                content_id=content_id,
                workflow_id=workflow_id,
                requester_id=requester_id,
                approvers=approvers,
                message=message,
                deadline=deadline
            )
            
            self.approval_requests[request_id] = request
            
            # Notify approvers
            await self._notify_approval_requested(request)
            
            logger.info(f"Created approval request {request_id} for content {content_id}")
            return request
            
        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")
            raise
    
    async def submit_approval(
        self, 
        request_id: str,
        approver_id: str,
        decision: ApprovalStatus,
        comments: Optional[str] = None
    ) -> bool:
        """Submit approval decision"""
        try:
            request = self.approval_requests.get(request_id)
            if not request:
                return False
            
            if approver_id not in request.approvers:
                return False
            
            if request.status != ApprovalStatus.PENDING:
                return False
            
            # Check if deadline passed
            if request.deadline and datetime.now(timezone.utc) > request.deadline:
                request.status = ApprovalStatus.EXPIRED
                return False
            
            # Record approval decision
            request.approvals[approver_id] = {
                'decision': decision.value,
                'comments': comments,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Check if all approvals received
            if len(request.approvals) == len(request.approvers):
                await self._finalize_approval_request(request)
            
            await self._notify_approval_submitted(request, approver_id, decision)
            
            logger.info(f"Approval submitted for request {request_id} by {approver_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit approval: {e}")
            return False
    
    async def get_approval_status(self, request_id: str) -> Dict[str, Any]:
        """Get approval request status"""
        try:
            request = self.approval_requests.get(request_id)
            if not request:
                return {}
            
            pending_approvers = [
                approver for approver in request.approvers
                if approver not in request.approvals
            ]
            
            return {
                'request_id': request_id,
                'content_id': request.content_id,
                'status': request.status.value,
                'approvals_received': len(request.approvals),
                'total_approvers': len(request.approvers),
                'pending_approvers': pending_approvers,
                'deadline': request.deadline.isoformat() if request.deadline else None,
                'created_at': request.created_at.isoformat(),
                'completed_at': request.completed_at.isoformat() if request.completed_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get approval status: {e}")
            return {}
    
    async def _finalize_approval_request(self, request: ApprovalRequest):
        """Finalize approval request based on all decisions"""
        decisions = [approval['decision'] for approval in request.approvals.values()]
        
        if all(decision == ApprovalStatus.APPROVED.value for decision in decisions):
            request.status = ApprovalStatus.APPROVED
        elif any(decision == ApprovalStatus.REJECTED.value for decision in decisions):
            request.status = ApprovalStatus.REJECTED
        elif any(decision == ApprovalStatus.CHANGES_REQUESTED.value for decision in decisions):
            request.status = ApprovalStatus.CHANGES_REQUESTED
        else:
            request.status = ApprovalStatus.APPROVED  # Default to approved
        
        request.completed_at = datetime.now(timezone.utc)
        
        await self._notify_approval_completed(request)
    
    async def _notify_approval_requested(self, request: ApprovalRequest):
        """Notify approvers about new approval request"""
        # Placeholder for notification implementation
        logger.info(f"Notifying approvers about request {request.request_id}")
    
    async def _notify_approval_submitted(
        self, 
        request: ApprovalRequest, 
        approver_id: str, 
        decision: ApprovalStatus
    ):
        """Notify about submitted approval"""
        # Placeholder for notification implementation
        logger.info(f"Approval {decision.value} submitted for request {request.request_id}")
    
    async def _notify_approval_completed(self, request: ApprovalRequest):
        """Notify about completed approval process"""
        # Placeholder for notification implementation
        logger.info(f"Approval process completed for request {request.request_id}: {request.status.value}")


class TeamWorkspaceManager:
    """Manages team workspaces and project coordination"""
    
    def __init__(self, config: CollaborationConfig):
        self.config = config
        self.workspaces: Dict[str, TeamWorkspace] = {}
        
        logger.info("🏢 Team Workspace Manager initialized")
    
    async def create_workspace(
        self, 
        name: str,
        description: str,
        owner_id: str,
        initial_members: Optional[List[User]] = None
    ) -> TeamWorkspace:
        """Create new team workspace"""
        try:
            workspace_id = str(uuid.uuid4())
            
            workspace = TeamWorkspace(
                workspace_id=workspace_id,
                name=name,
                description=description,
                owner_id=owner_id,
                members=initial_members or []
            )
            
            self.workspaces[workspace_id] = workspace
            
            # Notify members
            await self._notify_workspace_created(workspace)
            
            logger.info(f"Created workspace {workspace_id}: {name}")
            return workspace
            
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            raise
    
    async def add_member(
        self, 
        workspace_id: str, 
        user: User, 
        added_by: str
    ) -> bool:
        """Add member to workspace"""
        try:
            workspace = self.workspaces.get(workspace_id)
            if not workspace:
                return False
            
            # Check if user already member
            if any(member.user_id == user.user_id for member in workspace.members):
                return True
            
            workspace.members.append(user)
            workspace.updated_at = datetime.now(timezone.utc)
            
            await self._notify_member_added(workspace, user, added_by)
            
            logger.info(f"Added member {user.user_id} to workspace {workspace_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add member: {e}")
            return False
    
    async def remove_member(
        self, 
        workspace_id: str, 
        user_id: str, 
        removed_by: str
    ) -> bool:
        """Remove member from workspace"""
        try:
            workspace = self.workspaces.get(workspace_id)
            if not workspace:
                return False
            
            # Cannot remove owner
            if user_id == workspace.owner_id:
                return False
            
            workspace.members = [m for m in workspace.members if m.user_id != user_id]
            workspace.updated_at = datetime.now(timezone.utc)
            
            await self._notify_member_removed(workspace, user_id, removed_by)
            
            logger.info(f"Removed member {user_id} from workspace {workspace_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove member: {e}")
            return False
    
    async def add_project(
        self, 
        workspace_id: str, 
        project_id: str
    ) -> bool:
        """Add project to workspace"""
        try:
            workspace = self.workspaces.get(workspace_id)
            if not workspace:
                return False
            
            if project_id not in workspace.projects:
                workspace.projects.append(project_id)
                workspace.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Added project {project_id} to workspace {workspace_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add project: {e}")
            return False
    
    async def get_workspace_activity(
        self, 
        workspace_id: str, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Get workspace activity summary"""
        try:
            workspace = self.workspaces.get(workspace_id)
            if not workspace:
                return {}
            
            # Calculate activity metrics (placeholder)
            return {
                'workspace_id': workspace_id,
                'name': workspace.name,
                'member_count': len(workspace.members),
                'project_count': len(workspace.projects),
                'recent_activity': {
                    'collaborations': 0,  # Would calculate from real data
                    'comments': 0,
                    'approvals': 0,
                    'workflow_updates': 0
                },
                'updated_at': workspace.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get workspace activity: {e}")
            return {}
    
    async def _notify_workspace_created(self, workspace: TeamWorkspace):
        """Notify about workspace creation"""
        # Placeholder for notification implementation
        logger.info(f"Workspace created: {workspace.workspace_id}")
    
    async def _notify_member_added(self, workspace: TeamWorkspace, user: User, added_by: str):
        """Notify about member addition"""
        # Placeholder for notification implementation
        logger.info(f"Member {user.user_id} added to workspace {workspace.workspace_id}")
    
    async def _notify_member_removed(self, workspace: TeamWorkspace, user_id: str, removed_by: str):
        """Notify about member removal"""
        # Placeholder for notification implementation
        logger.info(f"Member {user_id} removed from workspace {workspace.workspace_id}")


class CollaborationWorkflowSystem:
    """Main collaboration workflow system orchestrating all components"""
    
    def __init__(self, config: Optional[CollaborationConfig] = None):
        """Initialize collaboration workflow system"""
        self.config = config or CollaborationConfig()
        
        # Initialize component managers
        self.realtime_manager = RealTimeCollaborationManager(self.config)
        self.workflow_engine = WorkflowEngine(self.config)
        self.approval_manager = ApprovalWorkflowManager(self.config)
        self.workspace_manager = TeamWorkspaceManager(self.config)
        
        # System-wide state
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        
        logger.info("🤝 Collaboration Workflow System initialized")
    
    async def create_collaborative_project(
        self, 
        project_name: str,
        project_description: str,
        creator_user: User,
        workspace_id: Optional[str] = None,
        initial_collaborators: Optional[List[User]] = None
    ) -> Dict[str, Any]:
        """Create new collaborative project with full workflow setup"""
        try:
            project_id = str(uuid.uuid4())
            
            # Create collaboration session
            session = await self.realtime_manager.create_session(project_id, creator_user)
            
            # Create project workflow
            workflow = await self.workflow_engine.create_workflow(
                name=f"{project_name} - Main Workflow",
                description=f"Main workflow for {project_name}",
                workflow_type=WorkflowType.CONTENT_CREATION,
                created_by=creator_user.user_id,
                participants=[creator_user.user_id] + [u.user_id for u in (initial_collaborators or [])]
            )
            
            # Add to workspace if specified
            if workspace_id:
                await self.workspace_manager.add_project(workspace_id, project_id)
            
            # Add initial collaborators to session
            if initial_collaborators:
                for collaborator in initial_collaborators:
                    await self.realtime_manager.join_session(session.session_id, collaborator)
            
            project_data = {
                'project_id': project_id,
                'name': project_name,
                'description': project_description,
                'creator_id': creator_user.user_id,
                'session_id': session.session_id,
                'workflow_id': workflow.workflow_id,
                'workspace_id': workspace_id,
                'collaborators': [u.user_id for u in (initial_collaborators or [])],
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            self.active_projects[project_id] = project_data
            
            logger.info(f"Created collaborative project {project_id}: {project_name}")
            return project_data
            
        except Exception as e:
            logger.error(f"Failed to create collaborative project: {e}")
            raise
    
    async def request_content_approval(
        self, 
        project_id: str,
        content_id: str,
        requester_id: str,
        approvers: List[str],
        message: Optional[str] = None
    ) -> ApprovalRequest:
        """Request approval for project content"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Create approval request
            approval_request = await self.approval_manager.create_approval_request(
                content_id=content_id,
                requester_id=requester_id,
                approvers=approvers,
                message=message,
                workflow_id=project.get('workflow_id')
            )
            
            # Create workflow task for approval
            await self.workflow_engine.add_task(
                workflow_id=project['workflow_id'],
                name=f"Approve Content - {content_id}",
                description=f"Review and approve content: {message or 'No description'}",
                assigned_to=approvers,
                priority=2
            )
            
            logger.info(f"Content approval requested for project {project_id}")
            return approval_request
            
        except Exception as e:
            logger.error(f"Failed to request content approval: {e}")
            raise
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project status"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                return {}
            
            # Get workflow progress
            workflow_progress = await self.workflow_engine.get_workflow_progress(
                project['workflow_id']
            )
            
            # Get active session info
            session = self.realtime_manager.active_sessions.get(project['session_id'])
            session_info = {
                'active_users': len(session.active_users) if session else 0,
                'last_activity': session.last_activity.isoformat() if session else None
            }
            
            return {
                'project_id': project_id,
                'project_data': project,
                'workflow_progress': workflow_progress,
                'session_info': session_info,
                'status_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get project status: {e}")
            return {}
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get user collaboration dashboard"""
        try:
            # Find user's active sessions
            active_sessions = [
                session_id for session_id in self.realtime_manager.user_sessions.get(user_id, set())
                if session_id in self.realtime_manager.active_sessions
            ]
            
            # Find user's workflows
            user_workflows = [
                workflow for workflow in self.workflow_engine.workflows.values()
                if user_id in workflow.participants
            ]
            
            # Find pending approvals
            pending_approvals = [
                request for request in self.approval_manager.approval_requests.values()
                if user_id in request.approvers and user_id not in request.approvals
                and request.status == ApprovalStatus.PENDING
            ]
            
            # Find user's workspaces
            user_workspaces = [
                workspace for workspace in self.workspace_manager.workspaces.values()
                if workspace.owner_id == user_id or 
                any(member.user_id == user_id for member in workspace.members)
            ]
            
            return {
                'user_id': user_id,
                'active_sessions': len(active_sessions),
                'active_workflows': len(user_workflows),
                'pending_approvals': len(pending_approvals),
                'workspaces': len(user_workspaces),
                'recent_activity': {
                    'last_collaboration': None,  # Would track actual activity
                    'recent_comments': 0,
                    'recent_approvals': 0
                },
                'dashboard_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user dashboard: {e}")
            return {}


# Backward compatibility classes for existing imports
class CollaborationTools_Legacy:
    """Legacy wrapper for collaboration tools"""
    def __init__(self, *args, **kwargs):
        self.system = CollaborationWorkflowSystem(*args, **kwargs)
        self.realtime_manager = self.system.realtime_manager


class CollaborationWorkflowEngine_Legacy:
    """Legacy wrapper for workflow engine"""
    def __init__(self, *args, **kwargs):
        config = CollaborationConfig()
        self.engine = WorkflowEngine(config)


class TeamMediaWorkspace_Legacy:
    """Legacy wrapper for team workspace"""
    def __init__(self, *args, **kwargs):
        config = CollaborationConfig()
        self.manager = TeamWorkspaceManager(config)


class ApprovalWorkflowManager_Legacy:
    """Legacy wrapper for approval manager"""
    def __init__(self, *args, **kwargs):
        config = CollaborationConfig()
        self.manager = ApprovalWorkflowManager(config)


# Export all classes for consolidated import
__all__ = [
    'CollaborationWorkflowSystem',
    'RealTimeCollaborationManager',
    'WorkflowEngine',
    'ApprovalWorkflowManager',
    'TeamWorkspaceManager',
    'CollaborationConfig',
    'User',
    'CollaborationSession',
    'Comment',
    'Annotation',
    'WorkflowTask',
    'Workflow',
    'ApprovalRequest',
    'TeamWorkspace',
    'CollaborationEventType',
    'WorkflowStatus',
    'WorkflowType',
    'PermissionLevel',
    'ApprovalStatus',
    # Legacy compatibility
    'CollaborationTools_Legacy',
    'CollaborationWorkflowEngine_Legacy',
    'TeamMediaWorkspace_Legacy',
    'ApprovalWorkflowManager_Legacy'
]