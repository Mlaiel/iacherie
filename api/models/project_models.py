"""IA Influencer Agent Platform - Project Models
Comprehensive project management for content creation workflows

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, Numeric,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .base import (
    BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin,
    AuditMixin, MetadataMixin, StatusMixin
)


class Project(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin, MetadataMixin):
    """Core project management for content creation initiatives"""    
    __tablename__ = 'projects'
    
    creator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Project Identity
    project_name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True
    )
    
    project_slug: Mapped[str] = mapped_column(
        String(350),
        unique=True,
        nullable=False,
        index=True
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Project Classification
    project_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # album, single, video_series, podcast_season, blog_series, campaign
    
    project_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # music, video, photography, writing, social_media, mixed_media
    
    genre: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Timeline and Planning
    planned_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    planned_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Budget and Resources
    estimated_budget: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    actual_budget: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        default='USD',
        nullable=False
    )
    
    # Project Scope
    expected_deliverables: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    success_criteria: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(300)),
        nullable=True
    )
    
    target_platforms: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )
    
    # Progress Tracking
    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True
    )
    
    completed_tasks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    total_tasks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Priority and Visibility
    priority: Mapped[str] = mapped_column(
        String(20),
        default='medium',
        nullable=False,
        index=True
    )  # low, medium, high, critical
    
    visibility: Mapped[str] = mapped_column(
        String(20),
        default='private',
        nullable=False
    )  # private, team, public
    
    # Collaboration
    is_collaborative: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    max_collaborators: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Quality and Requirements
    quality_standards: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    technical_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Relationships
    members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    tasks: Mapped[List["ProjectTask"]] = relationship(
        "ProjectTask",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    milestones: Mapped[List["ProjectMilestone"]] = relationship(
        "ProjectMilestone",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_projects_creator_type', 'creator_id', 'project_type'),
        Index('idx_projects_status_priority', 'status', 'priority'),
        Index('idx_projects_dates', 'planned_start_date', 'planned_end_date'),
        Index('idx_projects_progress', 'progress_percentage'),
        CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='valid_progress_percentage'),
        CheckConstraint('estimated_budget >= 0 OR estimated_budget IS NULL', name='positive_estimated_budget'),
        CheckConstraint('actual_budget >= 0 OR actual_budget IS NULL', name='positive_actual_budget'),
    )


class ProjectMember(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Project team member management and roles"""    
    __tablename__ = 'project_members'
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    member_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Role and Permissions
    role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # owner, manager, collaborator, contributor, reviewer, viewer
    
    role_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    permissions: Mapped[Dict[str, bool]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )  # create_tasks, edit_tasks, manage_members, etc.
    
    # Involvement Details
    involvement_type: Mapped[str] = mapped_column(
        String(50),
        default='full_time',
        nullable=False
    )  # full_time, part_time, consultant, guest
    
    expected_contribution: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Timeline
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Performance and Contribution
    tasks_assigned: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    tasks_completed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    contribution_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )  # 0-1 score based on performance
    
    # Revenue Sharing
    revenue_share_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )  # 0-100 percentage
    
    # Communication Preferences
    notification_preferences: Mapped[Dict[str, bool]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="members"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_members_project_member', 'project_id', 'member_id'),
        Index('idx_members_role_status', 'role', 'is_active'),
        Index('idx_members_joined_at', 'joined_at'),
        UniqueConstraint('project_id', 'member_id', name='unique_project_member'),
        CheckConstraint('revenue_share_percentage >= 0 AND revenue_share_percentage <= 100 OR revenue_share_percentage IS NULL', name='valid_revenue_share'),
    )


class ProjectTask(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin):
    """Individual tasks within project workflows"""    
    __tablename__ = 'project_tasks'
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Task Identity
    task_name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Task Classification
    task_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # content_creation, review, editing, marketing, administration
    
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Assignment
    assigned_to: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('project_members.id'),
        nullable=True,
        index=True
    )
    
    # Timeline
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True
    )
    
    actual_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True
    )
    
    # Progress
    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Priority and Dependencies
    priority: Mapped[str] = mapped_column(
        String(20),
        default='medium',
        nullable=False,
        index=True
    )  # low, medium, high, critical
    
    depends_on_tasks: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(255)),
        nullable=True
    )  # Task IDs this task depends on
    
    # Requirements and Deliverables
    requirements: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    deliverables: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    acceptance_criteria: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    # Files and Resources
    attached_files: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    reference_materials: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    # Quality and Review
    requires_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    reviewed_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    review_comments: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    is_approved: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_tasks_project_assigned', 'project_id', 'assigned_to'),
        Index('idx_tasks_status_priority', 'status', 'priority'),
        Index('idx_tasks_due_date', 'due_date'),
        Index('idx_tasks_completed', 'completed_at'),
        CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='valid_task_progress'),
        CheckConstraint('estimated_hours >= 0 OR estimated_hours IS NULL', name='positive_estimated_hours'),
        CheckConstraint('actual_hours >= 0 OR actual_hours IS NULL', name='positive_actual_hours'),
    )


class ProjectMilestone(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Project milestones and key deliverable tracking"""    
    __tablename__ = 'project_milestones'
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Milestone Identity
    milestone_name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Milestone Classification
    milestone_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # planning, development, review, release, marketing, completion
    
    importance: Mapped[str] = mapped_column(
        String(20),
        default='medium',
        nullable=False
    )  # low, medium, high, critical
    
    # Timeline
    target_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    actual_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Progress and Completion
    completion_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    is_achieved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Success Criteria
    success_criteria: Mapped[List[str]] = mapped_column(
        ARRAY(String(500)),
        nullable=False
    )
    
    deliverables: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    # Dependencies
    dependent_tasks: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(255)),
        nullable=True
    )  # Task IDs that must be completed
    
    prerequisite_milestones: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(255)),
        nullable=True
    )  # Milestone IDs that must be achieved first
    
    # Quality Metrics
    quality_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )  # 0-1 quality score
    
    performance_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Review and Approval
    reviewed_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    review_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    review_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Impact Assessment
    business_impact: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    risk_assessment: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="milestones"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_milestones_project_type', 'project_id', 'milestone_type'),
        Index('idx_milestones_target_date', 'target_date'),
        Index('idx_milestones_achieved', 'is_achieved', 'actual_date'),
        Index('idx_milestones_importance', 'importance'),
        CheckConstraint('completion_percentage >= 0 AND completion_percentage <= 100', name='valid_milestone_completion'),
        CheckConstraint('quality_score >= 0 AND quality_score <= 1 OR quality_score IS NULL', name='valid_milestone_quality'),
    )
