"""
Team Management Database Model

Enterprise-grade SQLAlchemy model for comprehensive team management,
organization hierarchy, workspace management, and collaboration coordination.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Set

Base = declarative_base()


class TeamType(Enum):
    """Team type enumeration"""
    ORGANIZATION = "organization"
    DEPARTMENT = "department"
    PROJECT_TEAM = "project_team"
    WORKING_GROUP = "working_group"
    CREATIVE_TEAM = "creative_team"
    COLLABORATION_TEAM = "collaboration_team"
    CROSS_FUNCTIONAL = "cross_functional"
    REMOTE_TEAM = "remote_team"
    TEMPORARY_TEAM = "temporary_team"
    STARTUP_TEAM = "startup_team"
    ENTERPRISE_DIVISION = "enterprise_division"
    STRATEGIC_UNIT = "strategic_unit"


class TeamStatus(Enum):
    """Team status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    FORMATION = "formation"
    DISSOLUTION = "dissolution"
    RESTRUCTURING = "restructuring"
    ON_HOLD = "on_hold"
    MIGRATING = "migrating"


class MemberRole(Enum):
    """Member role enumeration"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"
    SENIOR_MEMBER = "senior_member"
    MEMBER = "member"
    CONTRIBUTOR = "contributor"
    OBSERVER = "observer"
    GUEST = "guest"
    CONSULTANT = "consultant"
    INTERN = "intern"
    EXTERNAL_COLLABORATOR = "external_collaborator"


class MemberStatus(Enum):
    """Member status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_INVITATION = "pending_invitation"
    INVITATION_EXPIRED = "invitation_expired"
    SUSPENDED = "suspended"
    REMOVED = "removed"
    LEFT = "left"
    ON_LEAVE = "on_leave"
    TRANSFERRED = "transferred"


class InvitationStatus(Enum):
    """Invitation status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    RESENT = "resent"


class PermissionLevel(Enum):
    """Permission level enumeration"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_ACCESS = "full_access"
    ADMIN_ACCESS = "admin_access"
    OWNER_ACCESS = "owner_access"


class TeamVisibility(Enum):
    """Team visibility enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"
    ORGANIZATION_VISIBLE = "organization_visible"
    INVITE_ONLY = "invite_only"
    SECRET = "secret"


class TeamManagement(Base):
    """
    Enterprise Team Management Model
    
    Comprehensive team management with hierarchical organization,
    role-based access control, and collaboration features.
    """
    __tablename__ = 'team_management'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Team basic information
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    team_type = Column(SQLEnum(TeamType), nullable=False, index=True)
    status = Column(SQLEnum(TeamStatus), nullable=False, default=TeamStatus.ACTIVE, index=True)
    visibility = Column(SQLEnum(TeamVisibility), nullable=False, default=TeamVisibility.PRIVATE, index=True)
    
    # Organization hierarchy
    parent_team_id = Column(UUID(as_uuid=True), ForeignKey('team_management.id'), nullable=True, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    department_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    hierarchy_level = Column(Integer, nullable=False, default=1)
    hierarchy_path = Column(Text, nullable=True)  # e.g., "/org/dept/team"
    
    # Team leadership
    owner_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    primary_admin_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    secondary_admins = Column(ARRAY(String), nullable=True)
    
    # Team composition
    member_count = Column(Integer, nullable=False, default=0)
    active_member_count = Column(Integer, nullable=False, default=0)
    max_members = Column(Integer, nullable=True)
    invitation_count = Column(Integer, nullable=False, default=0)
    pending_invitations = Column(Integer, nullable=False, default=0)
    
    # Temporal information
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    activated_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True, index=True)
    archive_at = Column(DateTime(timezone=True), nullable=True)
    
    # Team settings and preferences
    settings = Column(JSONB, nullable=True)
    collaboration_preferences = Column(JSONB, nullable=True)
    communication_channels = Column(JSONB, nullable=True)
    default_permissions = Column(SQLEnum(PermissionLevel), nullable=False, default=PermissionLevel.READ_WRITE)
    
    # Project and workspace management
    associated_projects = Column(ARRAY(String), nullable=True)
    workspace_ids = Column(ARRAY(String), nullable=True)
    shared_resources = Column(JSONB, nullable=True)
    team_tools = Column(JSONB, nullable=True)
    
    # Access control and security
    security_settings = Column(JSONB, nullable=True)
    access_restrictions = Column(JSONB, nullable=True)
    ip_whitelist = Column(ARRAY(String), nullable=True)
    require_2fa = Column(Boolean, nullable=False, default=False)
    sso_enabled = Column(Boolean, nullable=False, default=False)
    
    # Billing and subscription
    subscription_plan = Column(String(100), nullable=True)
    billing_responsible_id = Column(UUID(as_uuid=True), nullable=True)
    usage_limits = Column(JSONB, nullable=True)
    current_usage = Column(JSONB, nullable=True)
    billing_cycle = Column(String(20), nullable=True)
    
    # Team performance and metrics
    performance_metrics = Column(JSONB, nullable=True)
    productivity_scores = Column(JSONB, nullable=True)
    collaboration_stats = Column(JSONB, nullable=True)
    engagement_metrics = Column(JSONB, nullable=True)
    
    # AI and automation features
    ai_assistance_enabled = Column(Boolean, nullable=False, default=True)
    automated_workflows = Column(JSONB, nullable=True)
    smart_recommendations = Column(Boolean, nullable=False, default=True)
    content_protection_enabled = Column(Boolean, nullable=False, default=True)
    
    # Integration and external services
    external_integrations = Column(JSONB, nullable=True)
    connected_platforms = Column(ARRAY(String), nullable=True)
    webhook_endpoints = Column(JSONB, nullable=True)
    api_access_tokens = Column(JSONB, nullable=True)
    
    # Geographic and timezone information
    primary_timezone = Column(String(50), nullable=True)
    geographic_regions = Column(ARRAY(String), nullable=True)
    working_hours = Column(JSONB, nullable=True)
    holiday_calendar = Column(String(50), nullable=True)
    
    # Compliance and governance
    compliance_requirements = Column(ARRAY(String), nullable=True)
    data_retention_policy = Column(JSONB, nullable=True)
    audit_settings = Column(JSONB, nullable=True)
    privacy_settings = Column(JSONB, nullable=True)
    
    # Communication and notifications
    notification_preferences = Column(JSONB, nullable=True)
    announcement_channels = Column(ARRAY(String), nullable=True)
    meeting_preferences = Column(JSONB, nullable=True)
    escalation_procedures = Column(JSONB, nullable=True)
    
    # Team culture and branding
    team_avatar = Column(String(500), nullable=True)
    team_banner = Column(String(500), nullable=True)
    brand_colors = Column(JSONB, nullable=True)
    team_values = Column(ARRAY(String), nullable=True)
    mission_statement = Column(Text, nullable=True)
    
    # Metadata and tags
    tags = Column(ARRAY(String), nullable=True)
    labels = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    custom_fields = Column(JSONB, nullable=True)
    
    # Administrative fields
    is_system_team = Column(Boolean, nullable=False, default=False)
    is_template_team = Column(Boolean, nullable=False, default=False)
    template_source_id = Column(UUID(as_uuid=True), nullable=True)
    migration_data = Column(JSONB, nullable=True)
    
    # Relationships
    parent_team = relationship("TeamManagement", remote_side=[id], backref="child_teams")
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_team_management_type_status', 'team_type', 'status'),
        Index('idx_team_management_owner_created', 'owner_user_id', 'created_by'),
        Index('idx_team_management_parent_hierarchy', 'parent_team_id', 'hierarchy_level'),
        Index('idx_team_management_org_dept', 'organization_id', 'department_id'),
        Index('idx_team_management_activity', 'last_activity_at'),
        Index('idx_team_management_member_count', 'member_count', 'active_member_count'),
        Index('idx_team_management_visibility', 'visibility', 'status'),
        Index('idx_team_management_subscription', 'subscription_plan', 'billing_responsible_id'),
        Index('idx_team_management_ai_features', 'ai_assistance_enabled', 'content_protection_enabled'),
        Index('idx_team_management_created_updated', 'created_at', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<TeamManagement(id={self.id}, name={self.name}, type={self.team_type.value}, status={self.status.value})>"
    
    @classmethod
    def create_team(
        cls,
        name: str,
        team_type: TeamType,
        owner_user_id: str,
        created_by: str,
        **kwargs
    ) -> 'TeamManagement':
        """Create a new team"""
        team_id = f"team_{uuid.uuid4().hex[:12]}"
        
        return cls(
            team_id=team_id,
            name=name,
            team_type=team_type,
            owner_user_id=owner_user_id,
            created_by=created_by,
            **kwargs
        )
    
    @classmethod
    def create_organization(
        cls,
        name: str,
        owner_user_id: str,
        created_by: str,
        **kwargs
    ) -> 'TeamManagement':
        """Create a new organization"""



        return cls.create_team(
            name=name,
            team_type=TeamType.ORGANIZATION,
            owner_user_id=owner_user_id,
            created_by=created_by,
            hierarchy_level=0,
            visibility=TeamVisibility.ORGANIZATION_VISIBLE,
            **kwargs
        )
    
    def add_member(self, user_id: str, role: MemberRole, added_by: str) -> 'TeamMember':
        """Add a member to the team"""
        member = TeamMember(
            team_id=self.id,
            user_id=user_id,
            role=role,
            status=MemberStatus.ACTIVE,
            added_by=added_by,
            joined_at=datetime.now(timezone.utc)
        )
        
        self.member_count += 1
        self.active_member_count += 1
        self.last_activity_at = datetime.now(timezone.utc)
        
        return member
    
    def invite_member(self, email: str, role: MemberRole, invited_by: str, message: str = None) -> 'TeamInvitation':
        """Invite a new member to the team"""
        invitation = TeamInvitation(
            team_id=self.id,
            email=email,
            role=role,
            invited_by=invited_by,
            message=message,
            invitation_token=uuid.uuid4().hex,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        
        self.invitation_count += 1
        self.pending_invitations += 1
        
        return invitation
    
    def update_member_role(self, user_id: str, new_role: MemberRole, updated_by: str) -> bool:
        """Update a member's role"""
        # This would update the associated TeamMember record
        self.last_activity_at = datetime.now(timezone.utc)
        return True
    
    def remove_member(self, user_id: str, removed_by: str, reason: str = None) -> bool:
        """Remove a member from the team"""
        # This would update the associated TeamMember record
        self.member_count -= 1
        self.active_member_count -= 1
        self.last_activity_at = datetime.now(timezone.utc)
        return True
    
    def get_hierarchy_path(self) -> str:
        """Get the full hierarchy path"""
        if self.hierarchy_path:
            return self.hierarchy_path
        
        path_parts = [self.name]
        current_team = self.parent_team
        
        while current_team:
            path_parts.insert(0, current_team.name)
            current_team = current_team.parent_team
        
        return "/" + "/".join(path_parts)
    
    def can_user_access(self, user_id: str, required_permission: PermissionLevel = None) -> bool:
        """Check if user can access this team"""
        if self.owner_user_id == user_id:
            return True
        
        if self.visibility == TeamVisibility.PUBLIC:
            return True
        
        # Check if user is a member (would query TeamMember table)
        return False
    
    def get_team_statistics(self) -> Dict[str, Any]:
        """Get comprehensive team statistics"""



        return {
            'basic_info': {
                'team_id': self.team_id,
                'name': self.name,
                'type': self.team_type.value,
                'status': self.status.value,
                'visibility': self.visibility.value
            },
            'membership': {
                'total_members': self.member_count,
                'active_members': self.active_member_count,
                'pending_invitations': self.pending_invitations,
                'max_members': self.max_members
            },
            'hierarchy': {
                'level': self.hierarchy_level,
                'path': self.get_hierarchy_path(),
                'has_parent': bool(self.parent_team_id),
                'organization_id': str(self.organization_id) if self.organization_id else None
            },
            'activity': {
                'created_at': self.created_at.isoformat(),
                'last_activity': self.last_activity_at.isoformat() if self.last_activity_at else None,
                'days_since_creation': (datetime.now(timezone.utc) - self.created_at).days
            },
            'features': {
                'ai_assistance': self.ai_assistance_enabled,
                'content_protection': self.content_protection_enabled,
                'smart_recommendations': self.smart_recommendations,
                'requires_2fa': self.require_2fa
            }
        }
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def archive_team(self, archived_by: str, reason: str = None) -> None:
        """Archive the team"""
        self.status = TeamStatus.ARCHIVED
        self.archive_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        
        if not self.metadata:
            self.metadata = {}
        
        self.metadata['archive_info'] = {
            'archived_by': archived_by,
            'archived_at': datetime.now(timezone.utc).isoformat(),
            'reason': reason
        }
    
    def restore_team(self, restored_by: str) -> None:
        """Restore archived team"""
        self.status = TeamStatus.ACTIVE
        self.archive_at = None
        self.updated_at = datetime.now(timezone.utc)
        
        if not self.metadata:
            self.metadata = {}
        
        self.metadata['restore_info'] = {
            'restored_by': restored_by,
            'restored_at': datetime.now(timezone.utc).isoformat()
        }


class TeamMember(Base):
    """
    Team Member Model
    
    Manages individual team memberships with roles and permissions.
    """
    __tablename__ = 'team_members'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relationship keys
    team_id = Column(UUID(as_uuid=True), ForeignKey('team_management.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Member information
    role = Column(SQLEnum(MemberRole), nullable=False, index=True)
    status = Column(SQLEnum(MemberStatus), nullable=False, default=MemberStatus.ACTIVE, index=True)
    permission_level = Column(SQLEnum(PermissionLevel), nullable=False, default=PermissionLevel.READ_WRITE)
    
    # Membership timeline
    joined_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    last_active_at = Column(DateTime(timezone=True), nullable=True, index=True)
    left_at = Column(DateTime(timezone=True), nullable=True)
    
    # Administrative information
    added_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    removed_by = Column(UUID(as_uuid=True), nullable=True)
    removal_reason = Column(Text, nullable=True)
    
    # Member settings
    notification_preferences = Column(JSONB, nullable=True)
    custom_permissions = Column(JSONB, nullable=True)
    member_settings = Column(JSONB, nullable=True)
    
    # Performance and contribution
    contribution_score = Column(Float, nullable=True)
    performance_metrics = Column(JSONB, nullable=True)
    achievements = Column(JSONB, nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Relationships
    team = relationship("TeamManagement", backref="members")
    
    # Unique constraint
    __table_args__ = (
        Index('idx_team_members_team_user', 'team_id', 'user_id', unique=True),
        Index('idx_team_members_role_status', 'role', 'status'),
        Index('idx_team_members_joined_active', 'joined_at', 'last_active_at'),
        Index('idx_team_members_added_by', 'added_by'),
    )
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role.value})>"


class TeamInvitation(Base):
    """
    Team Invitation Model
    
    Manages team invitations with expiration and tracking.
    """
    __tablename__ = 'team_invitations'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invitation_token = Column(String(64), unique=True, nullable=False, index=True)
    
    # Invitation details
    team_id = Column(UUID(as_uuid=True), ForeignKey('team_management.id'), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role = Column(SQLEnum(MemberRole), nullable=False)
    status = Column(SQLEnum(InvitationStatus), nullable=False, default=InvitationStatus.PENDING, index=True)
    
    # Timeline
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Administrative
    invited_by = Column(UUID(as_uuid=True), nullable=False)
    accepted_by = Column(UUID(as_uuid=True), nullable=True)
    message = Column(Text, nullable=True)
    
    # Tracking
    send_count = Column(Integer, nullable=False, default=1)
    last_sent_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    click_count = Column(Integer, nullable=False, default=0)
    last_clicked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    team = relationship("TeamManagement", backref="invitations")
    
    __table_args__ = (
        Index('idx_team_invitations_team_email', 'team_id', 'email'),
        Index('idx_team_invitations_status_expires', 'status', 'expires_at'),
        Index('idx_team_invitations_invited_by', 'invited_by'),
    )
    
    def __repr__(self):
        return f"<TeamInvitation(email={self.email}, team_id={self.team_id}, status={self.status.value})>"
    
    def is_expired(self) -> bool:
        """Check if invitation is expired"""



        return datetime.now(timezone.utc) >= self.expires_at
    
    def accept_invitation(self, user_id: str) -> None:
        """Accept the invitation"""
        self.status = InvitationStatus.ACCEPTED
        self.accepted_by = user_id
        self.accepted_at = datetime.now(timezone.utc)
    
    def decline_invitation(self) -> None:
        """Decline the invitation"""
        self.status = InvitationStatus.DECLINED
    
    def resend_invitation(self, expires_in_days: int = 7) -> None:
        """Resend the invitation"""
        self.status = InvitationStatus.RESENT
        self.send_count += 1
        self.last_sent_at = datetime.now(timezone.utc)
        self.expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
