"""
Team Coordination Database Module

Real-time team coordination system for collaborative content creation.
Handles communication, synchronization, and workflow orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices
"""

from typing import List, Dict, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import logging
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, DECIMAL, ARRAY, JSON, Index, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
import asyncio
import aioredis
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

Base = declarative_base()

class TeamRole(Enum):
    """Team role enumeration"""
    PROJECT_LEAD = "project_lead"
    CREATIVE_DIRECTOR = "creative_director"
    CONTENT_CREATOR = "content_creator"
    DESIGNER = "designer"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    COLLABORATOR = "collaborator"
    OBSERVER = "observer"

class CommunicationChannel(Enum):
    """Communication channel enumeration"""
    PROJECT_CHAT = "project_chat"
    TASK_DISCUSSION = "task_discussion"
    DESIGN_REVIEW = "design_review"
    GENERAL_UPDATE = "general_update"
    URGENT_NOTIFICATION = "urgent_notification"
    MILESTONE_ALERT = "milestone_alert"

class SynchronizationEvent(Enum):
    """Synchronization event types"""
    CONTENT_UPDATE = "content_update"
    TASK_STATUS_CHANGE = "task_status_change"
    MILESTONE_REACHED = "milestone_reached"
    TEAM_MEMBER_JOIN = "team_member_join"
    TEAM_MEMBER_LEAVE = "team_member_leave"
    DEADLINE_APPROACHING = "deadline_approaching"
    APPROVAL_REQUESTED = "approval_requested"

class TeamMember(Base):
    """
    Team member model with roles, permissions, and activity tracking.
    Manages individual team member participation in projects.
    """
    __tablename__ = 'team_members'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(String(100), unique=True, nullable=False)
    
    # Member details
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    invited_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Role and permissions
    team_role = Column(ENUM(TeamRole), nullable=False)
    role_permissions = Column(JSONB)
    access_level = Column(String(20), default='member')
    can_invite_others = Column(Boolean, default=False)
    can_manage_tasks = Column(Boolean, default=False)
    can_approve_content = Column(Boolean, default=False)
    
    # Participation status
    status = Column(String(20), default='active')  # active, inactive, on_leave, removed
    join_date = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    total_hours_contributed = Column(Float, default=0.0)
    
    # Specialization and skills
    specializations = Column(ARRAY(String))
    assigned_tasks = Column(ARRAY(UUID(as_uuid=True)))
    responsibility_areas = Column(JSONB)
    
    # Communication preferences
    notification_preferences = Column(JSONB)
    communication_channels = Column(ARRAY(String))
    preferred_contact_methods = Column(ARRAY(String))
    timezone = Column(String(50))
    
    # Performance tracking
    tasks_completed = Column(Integer, default=0)
    average_task_rating = Column(Float, default=0.0)
    collaboration_score = Column(Float, default=0.0)
    reliability_rating = Column(Float, default=0.0)
    
    # Availability and scheduling
    availability_schedule = Column(JSONB)
    current_capacity = Column(Float, default=100.0)  # Percentage
    workload_status = Column(String(20), default='available')
    
    # Metadata
    custom_fields = Column(JSONB)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_member_project_user', 'project_id', 'user_id'),
        Index('idx_member_role_status', 'team_role', 'status'),
        Index('idx_member_last_active', 'last_active'),
    )

class TeamCommunication(Base):
    """
    Team communication and messaging system.
    Handles real-time messaging, announcements, and notifications.
    """
    __tablename__ = 'team_communications'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(100), unique=True, nullable=False)
    
    # Communication context
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    channel = Column(ENUM(CommunicationChannel), nullable=False)
    thread_id = Column(UUID(as_uuid=True))
    parent_message_id = Column(UUID(as_uuid=True), ForeignKey('team_communications.id'))
    
    # Message details
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    message_type = Column(String(20), default='text')  # text, file, image, announcement, system
    message_content = Column(Text, nullable=False)
    message_format = Column(String(10), default='plain')  # plain, markdown, html
    
    # Recipients and targeting
    recipients = Column(ARRAY(UUID(as_uuid=True)))  # Specific recipients, null for all
    mention_users = Column(ARRAY(UUID(as_uuid=True)))
    target_roles = Column(ARRAY(String))  # Target specific roles
    
    # Message metadata
    priority = Column(String(10), default='normal')  # low, normal, high, urgent
    is_announcement = Column(Boolean, default=False)
    is_system_message = Column(Boolean, default=False)
    requires_acknowledgment = Column(Boolean, default=False)
    
    # Attachments and rich content
    attachments = Column(JSONB)
    embedded_content = Column(JSONB)
    related_tasks = Column(ARRAY(UUID(as_uuid=True)))
    related_content = Column(ARRAY(UUID(as_uuid=True)))
    
    # Interaction tracking
    read_by = Column(JSONB)  # User IDs and read timestamps
    acknowledged_by = Column(ARRAY(UUID(as_uuid=True)))
    reactions = Column(JSONB)  # Emoji reactions
    reply_count = Column(Integer, default=0)
    
    # Scheduling and expiration
    scheduled_send_time = Column(DateTime)
    expires_at = Column(DateTime)
    auto_delete_after_read = Column(Boolean, default=False)
    
    # Search and categorization
    tags = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    search_vector = Column(Text)  # For full-text search
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_comm_project_channel', 'project_id', 'channel'),
        Index('idx_comm_sender_date', 'sender_id', 'created_at'),
        Index('idx_comm_thread', 'thread_id'),
        Index('idx_comm_recipients', 'recipients'),
    )

class WorkflowState(Base):
    """
    Workflow state management for team coordination.
    Tracks project and task states across the team.
    """
    __tablename__ = 'workflow_states'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_id = Column(String(100), unique=True, nullable=False)
    
    # Workflow context
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    entity_type = Column(String(20), nullable=False)  # project, task, content, milestone
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    # State information
    current_state = Column(String(50), nullable=False)
    previous_state = Column(String(50))
    state_data = Column(JSONB)
    
    # Workflow rules
    allowed_transitions = Column(JSONB)
    required_approvals = Column(ARRAY(UUID(as_uuid=True)))
    auto_transition_rules = Column(JSONB)
    
    # Change tracking
    changed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    change_reason = Column(Text)
    approval_status = Column(String(20), default='pending')
    
    # Synchronization
    sync_version = Column(Integer, default=1)
    last_sync_time = Column(DateTime, default=datetime.utcnow)
    conflict_resolution = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_workflow_entity', 'entity_type', 'entity_id'),
        Index('idx_workflow_project_state', 'project_id', 'current_state'),
        Index('idx_workflow_sync_version', 'sync_version'),
    )

class RealTimeSession(Base):
    """
    Real-time collaboration session tracking.
    Manages active collaboration sessions and presence.
    """
    __tablename__ = 'realtime_sessions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, nullable=False)
    
    # Session context
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    session_type = Column(String(20), default='collaboration')  # collaboration, review, meeting
    
    # Session details
    status = Column(String(20), default='active')  # active, idle, disconnected
    connection_info = Column(JSONB)
    device_info = Column(JSONB)
    location_info = Column(JSONB)
    
    # Activity tracking
    current_activity = Column(String(50))  # editing, reviewing, viewing, discussing
    focused_content = Column(UUID(as_uuid=True))  # Currently focused content/task
    cursor_position = Column(JSONB)  # For collaborative editing
    
    # Presence information
    presence_status = Column(String(20), default='online')  # online, away, busy, offline
    status_message = Column(String(255))
    last_seen = Column(DateTime, default=datetime.utcnow)
    heartbeat_interval = Column(Integer, default=30)  # Seconds
    
    # Collaboration features
    shared_screen = Column(Boolean, default=False)
    screen_sharing_url = Column(String(500))
    voice_channel_id = Column(String(100))
    video_call_active = Column(Boolean, default=False)
    
    # Performance tracking
    connection_quality = Column(String(20), default='good')
    latency_ms = Column(Integer)
    bandwidth_kbps = Column(Integer)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_session_project_user', 'project_id', 'user_id'),
        Index('idx_session_status', 'status'),
        Index('idx_session_last_activity', 'last_activity'),
    )

@dataclass
class TeamInviteRequest:
    """Data class for team invitation requests"""
    project_id: str
    invited_user_id: str
    invited_by: str
    team_role: TeamRole
    message: str = None
    permissions: Dict[str, Any] = None
    access_level: str = 'member'

@dataclass
class CommunicationMessage:
    """Data class for team communication messages"""
    project_id: str
    sender_id: str
    channel: CommunicationChannel
    content: str
    message_type: str = 'text'
    recipients: List[str] = None
    priority: str = 'normal'
    attachments: List[Dict[str, Any]] = None

class TeamCoordinationEngine:
    """
    Enterprise team coordination engine with real-time features.
    Handles team management, communication, and workflow synchronization.
    """
    
    def __init__(self, db_session, redis_client: aioredis.Redis = None, websocket_manager = None):
        self.db_session = db_session
        self.redis_client = redis_client
        self.websocket_manager = websocket_manager
        self.cache_ttl = 1800  # 30 minutes cache
        
        # Real-time channels
        self.presence_channel = "team_presence"
        self.communication_channel = "team_communication"
        self.workflow_channel = "workflow_updates"
    
    async def invite_team_member(self, request: TeamInviteRequest) -> Optional[TeamMember]:
        """
        Invite a new team member to the project.
        
        Args:
            request: Team invitation request
            
        Returns:
            Created team member instance
        """
        try:
            # Check if user is already a team member
            existing_member = await self.db_session.query(TeamMember)\
                .filter(
                    TeamMember.project_id == uuid.UUID(request.project_id),
                    TeamMember.user_id == uuid.UUID(request.invited_user_id)
                )\
                .first()
            
            if existing_member:
                logger.warning(f"User {request.invited_user_id} already a member of project {request.project_id}")
                return existing_member
            
            # Generate member ID
            member_id = self._generate_member_id(request.project_id)
            
            # Create team member
            team_member = TeamMember(
                member_id=member_id,
                project_id=uuid.UUID(request.project_id),
                user_id=uuid.UUID(request.invited_user_id),
                invited_by=uuid.UUID(request.invited_by),
                team_role=request.team_role,
                role_permissions=request.permissions or self._default_role_permissions(request.team_role),
                access_level=request.access_level,
                notification_preferences=self._default_notification_preferences(),
                availability_schedule=self._default_availability_schedule(),
                responsibility_areas=self._default_responsibility_areas(request.team_role)
            )
            
            # Save team member
            self.db_session.add(team_member)
            await self.db_session.commit()
            await self.db_session.refresh(team_member)
            
            # Send invitation notification
            await self._send_invitation_notification(team_member, request.message)
            
            # Broadcast team update
            await self._broadcast_team_update(request.project_id, 'member_added', {
                'member_id': member_id,
                'user_id': request.invited_user_id,
                'role': request.team_role.value,
                'invited_by': request.invited_by
            })
            
            logger.info(f"Team member invited: {member_id}")
            
            return team_member
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to invite team member: {str(e)}")
            raise
    
    async def send_team_message(self, message: CommunicationMessage) -> Optional[TeamCommunication]:
        """
        Send message to team with real-time delivery.
        
        Args:
            message: Communication message data
            
        Returns:
            Created communication instance
        """
        try:
            # Generate message ID
            message_id = self._generate_message_id(message.project_id)
            
            # Create communication record
            communication = TeamCommunication(
                message_id=message_id,
                project_id=uuid.UUID(message.project_id),
                channel=message.channel,
                sender_id=uuid.UUID(message.sender_id),
                message_type=message.message_type,
                message_content=message.content,
                recipients=[uuid.UUID(uid) for uid in (message.recipients or [])],
                priority=message.priority,
                attachments=message.attachments or [],
                thread_id=uuid.uuid4(),
                sent_at=datetime.utcnow(),
                search_vector=self._generate_search_vector(message.content)
            )
            
            # Save communication
            self.db_session.add(communication)
            await self.db_session.commit()
            await self.db_session.refresh(communication)
            
            # Real-time delivery
            await self._deliver_message_realtime(communication)
            
            # Update team activity
            await self._update_team_activity(message.project_id, message.sender_id, 'sent_message')
            
            logger.info(f"Team message sent: {message_id}")
            
            return communication
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to send team message: {str(e)}")
            raise
    
    async def start_realtime_session(
        self,
        project_id: str,
        user_id: str,
        session_type: str = 'collaboration',
        activity: str = 'general'
    ) -> Optional[RealTimeSession]:
        """
        Start a real-time collaboration session.
        
        Args:
            project_id: Project identifier
            user_id: User starting session
            session_type: Type of session
            activity: Current activity
            
        Returns:
            Created session instance
        """
        try:
            # End any existing active sessions for this user/project
            await self._end_user_sessions(project_id, user_id)
            
            # Generate session ID
            session_id = self._generate_session_id(project_id, user_id)
            
            # Create session
            session = RealTimeSession(
                session_id=session_id,
                project_id=uuid.UUID(project_id),
                user_id=uuid.UUID(user_id),
                session_type=session_type,
                current_activity=activity,
                connection_info=await self._get_connection_info(user_id),
                device_info=await self._get_device_info(user_id),
                presence_status='online'
            )
            
            # Save session
            self.db_session.add(session)
            await self.db_session.commit()
            await self.db_session.refresh(session)
            
            # Update presence in Redis
            await self._update_user_presence(project_id, user_id, 'online', session_id)
            
            # Broadcast presence update
            await self._broadcast_presence_update(project_id, user_id, 'joined', {
                'session_id': session_id,
                'activity': activity,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Real-time session started: {session_id}")
            
            return session
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to start real-time session: {str(e)}")
            raise
    
    async def update_workflow_state(
        self,
        project_id: str,
        entity_type: str,
        entity_id: str,
        new_state: str,
        changed_by: str,
        change_reason: str = None
    ) -> Optional[WorkflowState]:
        """
        Update workflow state with team synchronization.
        
        Args:
            project_id: Project identifier
            entity_type: Type of entity (project, task, content, milestone)
            entity_id: Entity identifier
            new_state: New workflow state
            changed_by: User making the change
            change_reason: Reason for state change
            
        Returns:
            Updated workflow state instance
        """
        try:
            # Get current workflow state
            workflow_state = await self.db_session.query(WorkflowState)\
                .filter(
                    WorkflowState.project_id == uuid.UUID(project_id),
                    WorkflowState.entity_type == entity_type,
                    WorkflowState.entity_id == uuid.UUID(entity_id)
                )\
                .first()
            
            if not workflow_state:
                # Create new workflow state
                state_id = self._generate_workflow_state_id(project_id, entity_type)
                workflow_state = WorkflowState(
                    state_id=state_id,
                    project_id=uuid.UUID(project_id),
                    entity_type=entity_type,
                    entity_id=uuid.UUID(entity_id),
                    current_state=new_state,
                    changed_by=uuid.UUID(changed_by),
                    change_reason=change_reason,
                    sync_version=1,
                    allowed_transitions=self._get_allowed_transitions(entity_type, new_state)
                )
                self.db_session.add(workflow_state)
            else:
                # Update existing state
                workflow_state.previous_state = workflow_state.current_state
                workflow_state.current_state = new_state
                workflow_state.changed_by = uuid.UUID(changed_by)
                workflow_state.change_reason = change_reason
                workflow_state.sync_version += 1
                workflow_state.last_sync_time = datetime.utcnow()
                workflow_state.updated_at = datetime.utcnow()
            
            # Save changes
            await self.db_session.commit()
            await self.db_session.refresh(workflow_state)
            
            # Broadcast workflow update
            await self._broadcast_workflow_update(project_id, {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'new_state': new_state,
                'previous_state': workflow_state.previous_state,
                'changed_by': changed_by,
                'sync_version': workflow_state.sync_version,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Update team activity
            await self._update_team_activity(project_id, changed_by, f'updated_{entity_type}_state')
            
            logger.info(f"Workflow state updated: {entity_type}:{entity_id} -> {new_state}")
            
            return workflow_state
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update workflow state: {str(e)}")
            raise
    
    async def get_team_presence(self, project_id: str) -> Dict[str, Any]:
        """
        Get real-time team presence information.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Team presence data
        """
        try:
            # Get active sessions
            active_sessions = await self.db_session.query(RealTimeSession)\
                .filter(
                    RealTimeSession.project_id == uuid.UUID(project_id),
                    RealTimeSession.status == 'active'
                )\
                .all()
            
            # Get team members
            team_members = await self.db_session.query(TeamMember)\
                .filter(
                    TeamMember.project_id == uuid.UUID(project_id),
                    TeamMember.status == 'active'
                )\
                .all()
            
            # Build presence data
            presence_data = {
                'project_id': project_id,
                'timestamp': datetime.utcnow().isoformat(),
                'online_count': len(active_sessions),
                'total_members': len(team_members),
                'members': []
            }
            
            # Add member presence info
            for member in team_members:
                # Find active session for this member
                active_session = next(
                    (s for s in active_sessions if s.user_id == member.user_id), None
                )
                
                member_presence = {
                    'user_id': str(member.user_id),
                    'member_id': member.member_id,
                    'role': member.team_role.value,
                    'status': 'online' if active_session else 'offline',
                    'last_active': member.last_active.isoformat() if member.last_active else None,
                    'current_activity': active_session.current_activity if active_session else None,
                    'session_id': active_session.session_id if active_session else None
                }
                
                presence_data['members'].append(member_presence)
            
            return presence_data
            
        except Exception as e:
            logger.error(f"Failed to get team presence for {project_id}: {str(e)}")
            return {}
    
    async def get_team_activity_feed(
        self,
        project_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get team activity feed for project dashboard.
        
        Args:
            project_id: Project identifier
            limit: Number of activities to return
            offset: Activity offset for pagination
            
        Returns:
            List of activity items
        """
        try:
            # Get recent communications
            communications = await self.db_session.query(TeamCommunication)\
                .filter(TeamCommunication.project_id == uuid.UUID(project_id))\
                .order_by(TeamCommunication.created_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            # Get recent workflow updates
            workflow_updates = await self.db_session.query(WorkflowState)\
                .filter(WorkflowState.project_id == uuid.UUID(project_id))\
                .order_by(WorkflowState.updated_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            # Combine and format activities
            activities = []
            
            # Add communication activities
            for comm in communications:
                activity = {
                    'type': 'communication',
                    'id': str(comm.id),
                    'timestamp': comm.created_at.isoformat(),
                    'user_id': str(comm.sender_id),
                    'channel': comm.channel.value,
                    'content': comm.message_content[:200] + '...' if len(comm.message_content) > 200 else comm.message_content,
                    'priority': comm.priority,
                    'reply_count': comm.reply_count
                }
                activities.append(activity)
            
            # Add workflow activities
            for workflow in workflow_updates:
                activity = {
                    'type': 'workflow',
                    'id': str(workflow.id),
                    'timestamp': workflow.updated_at.isoformat(),
                    'user_id': str(workflow.changed_by),
                    'entity_type': workflow.entity_type,
                    'entity_id': str(workflow.entity_id),
                    'state_change': f"{workflow.previous_state} → {workflow.current_state}",
                    'reason': workflow.change_reason
                }
                activities.append(activity)
            
            # Sort by timestamp and limit
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get team activity feed for {project_id}: {str(e)}")
            return []
    
    async def get_team_performance_metrics(self, project_id: str) -> Dict[str, Any]:
        """
        Get comprehensive team performance metrics.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Team performance metrics
        """
        try:
            # Get team members
            team_members = await self.db_session.query(TeamMember)\
                .filter(
                    TeamMember.project_id == uuid.UUID(project_id),
                    TeamMember.status == 'active'
                )\
                .all()
            
            # Calculate team metrics
            total_members = len(team_members)
            total_hours = sum(member.total_hours_contributed for member in team_members)
            avg_collaboration_score = sum(member.collaboration_score for member in team_members) / total_members if total_members > 0 else 0
            avg_reliability = sum(member.reliability_rating for member in team_members) / total_members if total_members > 0 else 0
            
            # Get communication metrics
            comm_count = await self.db_session.query(TeamCommunication)\
                .filter(TeamCommunication.project_id == uuid.UUID(project_id))\
                .count()
            
            # Get recent activity metrics
            recent_activity = await self.db_session.query(RealTimeSession)\
                .filter(
                    RealTimeSession.project_id == uuid.UUID(project_id),
                    RealTimeSession.started_at >= datetime.utcnow() - timedelta(days=7)
                )\
                .count()
            
            metrics = {
                'project_id': project_id,
                'generated_at': datetime.utcnow().isoformat(),
                'team_size': total_members,
                'total_hours_contributed': total_hours,
                'average_collaboration_score': round(avg_collaboration_score, 2),
                'average_reliability_rating': round(avg_reliability, 2),
                'communication_volume': comm_count,
                'recent_activity_sessions': recent_activity,
                'member_metrics': [
                    {
                        'user_id': str(member.user_id),
                        'role': member.team_role.value,
                        'hours_contributed': member.total_hours_contributed,
                        'tasks_completed': member.tasks_completed,
                        'collaboration_score': member.collaboration_score,
                        'reliability_rating': member.reliability_rating,
                        'current_capacity': member.current_capacity,
                        'last_active': member.last_active.isoformat() if member.last_active else None
                    }
                    for member in team_members
                ]
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get team performance metrics for {project_id}: {str(e)}")
            return {}
    
    # Private helper methods
    
    def _generate_member_id(self, project_id: str) -> str:
        """Generate unique team member identifier"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"MEMBER-{timestamp}-{random_suffix}"
    
    def _generate_message_id(self, project_id: str) -> str:
        """Generate unique message identifier"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"MSG-{timestamp}-{random_suffix}"
    
    def _generate_session_id(self, project_id: str, user_id: str) -> str:
        """Generate unique session identifier"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        user_short = str(user_id)[:8]
        return f"SESSION-{timestamp}-{user_short}"
    
    def _generate_workflow_state_id(self, project_id: str, entity_type: str) -> str:
        """Generate unique workflow state identifier"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        type_code = entity_type.upper()[:4]
        return f"WORKFLOW-{type_code}-{timestamp}-{str(uuid.uuid4())[:8]}"
    
    def _default_role_permissions(self, role: TeamRole) -> Dict[str, Any]:
        """Get default permissions for team role"""
        permissions = {
            TeamRole.PROJECT_LEAD: {
                'can_manage_team': True,
                'can_manage_tasks': True,
                'can_approve_content': True,
                'can_manage_budget': True,
                'can_delete_project': True
            },
            TeamRole.CREATIVE_DIRECTOR: {
                'can_manage_team': False,
                'can_manage_tasks': True,
                'can_approve_content': True,
                'can_manage_budget': False,
                'can_delete_project': False
            },
            TeamRole.CONTENT_CREATOR: {
                'can_manage_team': False,
                'can_manage_tasks': False,
                'can_approve_content': False,
                'can_manage_budget': False,
                'can_delete_project': False
            }
        }
        
        return permissions.get(role, permissions[TeamRole.COLLABORATOR])
    
    def _default_notification_preferences(self) -> Dict[str, Any]:
        """Default notification preferences"""
        return {
            'email_notifications': True,
            'push_notifications': True,
            'in_app_notifications': True,
            'digest_frequency': 'daily',
            'urgent_only': False,
            'quiet_hours': {
                'enabled': True,
                'start': '22:00',
                'end': '08:00'
            }
        }
    
    def _default_availability_schedule(self) -> Dict[str, Any]:
        """Default availability schedule"""
        return {
            'monday': ['09:00', '17:00'],
            'tuesday': ['09:00', '17:00'],
            'wednesday': ['09:00', '17:00'],
            'thursday': ['09:00', '17:00'],
            'friday': ['09:00', '17:00'],
            'saturday': [],
            'sunday': []
        }
    
    def _default_responsibility_areas(self, role: TeamRole) -> Dict[str, Any]:
        """Default responsibility areas for role"""
        areas = {
            TeamRole.PROJECT_LEAD: ['project_oversight', 'team_management', 'stakeholder_communication'],
            TeamRole.CREATIVE_DIRECTOR: ['creative_direction', 'quality_assurance', 'design_approval'],
            TeamRole.CONTENT_CREATOR: ['content_creation', 'content_editing', 'asset_management'],
            TeamRole.DESIGNER: ['visual_design', 'branding', 'user_interface'],
            TeamRole.DEVELOPER: ['technical_implementation', 'system_integration', 'testing'],
            TeamRole.REVIEWER: ['content_review', 'quality_control', 'feedback_provision']
        }
        
        return {
            'primary_areas': areas.get(role, ['general_collaboration']),
            'secondary_areas': [],
            'expertise_level': 'intermediate'
        }
    
    def _generate_search_vector(self, content: str) -> str:
        """Generate search vector for full-text search"""
        # This would typically use PostgreSQL's full-text search
        # For now, return a simplified version
        words = content.lower().split()
        return ' '.join(set(words))
    
    async def _deliver_message_realtime(self, communication: TeamCommunication):
        """Deliver message via WebSocket to online team members"""
        if not self.websocket_manager:
            return
        
        message_data = {
            'type': 'team_message',
            'message_id': communication.message_id,
            'channel': communication.channel.value,
            'sender_id': str(communication.sender_id),
            'content': communication.message_content,
            'timestamp': communication.created_at.isoformat(),
            'priority': communication.priority
        }
        
        # Send to project channel
        await self.websocket_manager.broadcast_to_project(
            str(communication.project_id),
            message_data
        )
    
    async def _broadcast_team_update(self, project_id: str, update_type: str, data: Dict[str, Any]):
        """Broadcast team updates to project members"""
        if not self.websocket_manager:
            return
        
        update_data = {
            'type': 'team_update',
            'update_type': update_type,
            'project_id': project_id,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.websocket_manager.broadcast_to_project(project_id, update_data)
    
    async def _broadcast_presence_update(self, project_id: str, user_id: str, action: str, data: Dict[str, Any]):
        """Broadcast presence updates"""
        if not self.websocket_manager:
            return
        
        presence_data = {
            'type': 'presence_update',
            'user_id': user_id,
            'action': action,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.websocket_manager.broadcast_to_project(project_id, presence_data)
    
    async def _broadcast_workflow_update(self, project_id: str, workflow_data: Dict[str, Any]):
        """Broadcast workflow state changes"""
        if not self.websocket_manager:
            return
        
        update_data = {
            'type': 'workflow_update',
            'project_id': project_id,
            'workflow': workflow_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.websocket_manager.broadcast_to_project(project_id, update_data)

# Export main classes
__all__ = [
    'TeamMember',
    'TeamCommunication',
    'WorkflowState',
    'RealTimeSession',
    'TeamRole',
    'CommunicationChannel',
    'SynchronizationEvent',
    'TeamInviteRequest',
    'CommunicationMessage',
    'TeamCoordinationEngine'
]
