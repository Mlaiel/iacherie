"""Collaboration Projects Database Module

Enterprise-grade project lifecycle management for multi-format content creators.
Handles project creation, management, versioning, and collaboration workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import logging
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, DECIMAL, ARRAY, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
import asyncio
import aioredis
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

Base = declarative_base()

class ProjectStatus(Enum):
    """
Project status enumeration"""

    DRAFT = "draft"
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class ProjectType(Enum):
    """Project type enumeration for multi-format content"""

    MUSIC_COLLABORATION = "music_collaboration"
    VIDEO_PRODUCTION = "video_production"
    PHOTOGRAPHY_SERIES = "photography_series"
    BLOG_SERIES = "blog_series"
    COMEDY_SKETCH = "comedy_sketch"
    MULTI_FORMAT_CAMPAIGN = "multi_format_campaign"
    CROSS_PLATFORM_CONTENT = "cross_platform_content"

class ProjectPriority(Enum):
    """Project priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class CollaborationProject(Base):
    """
    Core collaboration project model for enterprise project management.
    Supports multi-format content creation with advanced features.
    """
    __tablename__ = 'collaboration_projects'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Project categorization
    project_type = Column(ENUM(ProjectType), nullable=False)
    priority = Column(ENUM(ProjectPriority), default=ProjectPriority.MEDIUM)
    status = Column(ENUM(ProjectStatus), default=ProjectStatus.DRAFT)
    
    # Creator and team management
    creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    team_lead_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    team_members = Column(ARRAY(UUID(as_uuid=True)))
    invited_members = Column(ARRAY(UUID(as_uuid=True)))
    
    # Timeline and scheduling
    start_date = Column(DateTime)
    target_end_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    
    # Financial planning
    budget_allocated = Column(DECIMAL(15, 2))
    budget_spent = Column(DECIMAL(15, 2), default=0)
    revenue_target = Column(DECIMAL(15, 2))
    revenue_sharing_model = Column(JSONB)
    
    # Content and deliverables
    content_formats = Column(ARRAY(String))  # audio, video, image, text
    deliverables = Column(JSONB)
    assets_bucket = Column(String(255))  # S3 bucket for project assets
    
    # Collaboration features
    collaboration_settings = Column(JSONB)
    communication_channels = Column(JSONB)
    approval_workflow = Column(JSONB)
    version_control = Column(JSONB)
    
    # Analytics and tracking
    performance_metrics = Column(JSONB)
    ai_insights = Column(JSONB)
    engagement_stats = Column(JSONB)
    quality_scores = Column(JSONB)
    
    # Security and compliance
    access_permissions = Column(JSONB)
    confidentiality_level = Column(String(20), default='standard')
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'))
    legal_requirements = Column(JSONB)
    
    # Platform distribution
    target_platforms = Column(ARRAY(String))
    platform_configs = Column(JSONB)
    seo_keywords = Column(ARRAY(String))
    hashtags = Column(ARRAY(String))
    
    # Metadata and versioning
    version = Column(String(20), default='1.0.0')
    tags = Column(ARRAY(String))
    custom_fields = Column(JSONB)
    metadata = Column(JSONB)
    
    # Timestamps and audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    last_modified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_project_status_type', 'status', 'project_type'),
        Index('idx_project_creator_date', 'creator_id', 'created_at'),
        Index('idx_project_team_members', 'team_members'),
        Index('idx_project_timeline', 'start_date', 'target_end_date'),
    )

@dataclass
class ProjectCreationRequest:
    """
Data class for project creation requests"""
    title: str
    description: str
    project_type: ProjectType
    creator_id: str
    priority: ProjectPriority = ProjectPriority.MEDIUM
    content_formats: List[str] = None
    target_platforms: List[str] = None
    estimated_hours: int = None
    budget_allocated: float = None
    start_date: datetime = None
    target_end_date: datetime = None
    team_members: List[str] = None
    tags: List[str] = None
    custom_fields: Dict[str, Any] = None

@dataclass
class ProjectUpdateRequest:
    """
Data class for project update requests"""
    project_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    team_members: Optional[List[str]] = None
    budget_allocated: Optional[float] = None
    target_end_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ProjectDatabaseManager:
    """
    Enterprise project database manager with advanced features.
    Handles CRUD operations, caching, and business logic.
    """
    
    def __init__(self, db_session, redis_client: aioredis.Redis = None):
        self.db_session = db_session
        self.redis_client = redis_client
        self.cache_ttl = 3600  # 1 hour cache
        
    async def create_project(self, request: ProjectCreationRequest) -> CollaborationProject:
        """
        Create a new collaboration project with enterprise features.
        
        Args:
            request: Project creation request data
            
        Returns:
            Created project instance
            
        Raises:
            ValueError: Invalid project data
            DatabaseError: Database operation failed
        """
        try:
            # Generate unique project code
            project_code = await self._generate_project_code(request.project_type)
            
            # Create project instance
            project = CollaborationProject(
                project_code=project_code,
                title=request.title,
                description=request.description,
                project_type=request.project_type,
                creator_id=uuid.UUID(request.creator_id),
                priority=request.priority,
                content_formats=request.content_formats or [],
                target_platforms=request.target_platforms or [],
                estimated_hours=request.estimated_hours,
                budget_allocated=request.budget_allocated,
                start_date=request.start_date,
                target_end_date=request.target_end_date,
                team_members=[uuid.UUID(id) for id in (request.team_members or [])],
                tags=request.tags or [],
                custom_fields=request.custom_fields or {},
                created_by=uuid.UUID(request.creator_id),
                collaboration_settings=self._default_collaboration_settings(),
                version_control=self._initialize_version_control(),
                access_permissions=self._default_access_permissions(),
                metadata=self._initialize_project_metadata(request)
            )
            
            # Save to database
            self.db_session.add(project)
            await self.db_session.commit()
            await self.db_session.refresh(project)
            
            # Cache project data
            if self.redis_client:
                await self._cache_project(project)
            
            # Log project creation
            logger.info(f"Project created: {project_code} by user {request.creator_id}")
            
            return project
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create project: {str(e)}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[CollaborationProject]:
        """
        Retrieve project by ID with caching support.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Project instance or None
        """
        try:
            # Check cache first
            if self.redis_client:
                cached_data = await self.redis_client.get(f"project:{project_id}")
                if cached_data:
                    return self._deserialize_project(json.loads(cached_data))
            
            # Query database
            project = await self.db_session.query(CollaborationProject)\
                .filter(CollaborationProject.id == uuid.UUID(project_id))\
                .first()
            
            # Cache result
            if project and self.redis_client:
                await self._cache_project(project)
            
            return project
            
        except Exception as e:
            logger.error(f"Failed to retrieve project {project_id}: {str(e)}")
            return None
    
    async def update_project(self, request: ProjectUpdateRequest) -> Optional[CollaborationProject]:
        """
        Update project with enterprise audit trail.
        
        Args:
            request: Project update request
            
        Returns:
            Updated project instance
        """
        try:
            project = await self.get_project(request.project_id)
            if not project:
                return None
            
            # Track changes for audit
            changes = {}
            
            if request.title and request.title != project.title:
                changes['title'] = {'old': project.title, 'new': request.title}
                project.title = request.title
            
            if request.description and request.description != project.description:
                changes['description'] = {'old': project.description, 'new': request.description}
                project.description = request.description
            
            if request.status and request.status != project.status:
                changes['status'] = {'old': project.status.value, 'new': request.status.value}
                project.status = request.status
            
            if request.priority and request.priority != project.priority:
                changes['priority'] = {'old': project.priority.value, 'new': request.priority.value}
                project.priority = request.priority
            
            if request.team_members is not None:
                old_members = [str(id) for id in project.team_members or []]
                new_members = request.team_members
                if old_members != new_members:
                    changes['team_members'] = {'old': old_members, 'new': new_members}
                    project.team_members = [uuid.UUID(id) for id in new_members]
            
            if request.budget_allocated is not None:
                changes['budget_allocated'] = {'old': float(project.budget_allocated or 0), 'new': request.budget_allocated}
                project.budget_allocated = request.budget_allocated
            
            if request.target_end_date:
                changes['target_end_date'] = {'old': project.target_end_date.isoformat() if project.target_end_date else None, 'new': request.target_end_date.isoformat()}
                project.target_end_date = request.target_end_date
            
            if request.metadata:
                project.metadata = {**(project.metadata or {}), **request.metadata}
            
            # Update modification tracking
            project.updated_at = datetime.utcnow()
            project.last_modified_by = project.creator_id  # Should be current user ID
            
            # Store audit trail
            if changes:
                audit_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'changes': changes,
                    'modified_by': str(project.last_modified_by)
                }
                
                audit_trail = project.metadata.get('audit_trail', [])
                audit_trail.append(audit_entry)
                project.metadata['audit_trail'] = audit_trail
            
            # Save changes
            await self.db_session.commit()
            
            # Update cache
            if self.redis_client:
                await self._cache_project(project)
            
            logger.info(f"Project updated: {project.project_code} - {len(changes)} changes")
            
            return project
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update project {request.project_id}: {str(e)}")
            raise
    
    async def list_projects(
        self, 
        creator_id: str = None,
        status: ProjectStatus = None,
        project_type: ProjectType = None,
        team_member_id: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[CollaborationProject], int]:
        """
        List projects with advanced filtering and pagination.
        
        Args:
            creator_id: Filter by creator
            status: Filter by status
            project_type: Filter by type
            team_member_id: Filter by team member
            limit: Results limit
            offset: Results offset
            
        Returns:
            Tuple of (projects list, total count)
        """
        try:
            query = self.db_session.query(CollaborationProject)
            
            # Apply filters
            if creator_id:
                query = query.filter(CollaborationProject.creator_id == uuid.UUID(creator_id))
            
            if status:
                query = query.filter(CollaborationProject.status == status)
            
            if project_type:
                query = query.filter(CollaborationProject.project_type == project_type)
            
            if team_member_id:
                query = query.filter(CollaborationProject.team_members.any(uuid.UUID(team_member_id)))
            
            # Get total count
            total_count = await query.count()
            
            # Apply pagination and ordering
            projects = await query\
                .order_by(CollaborationProject.updated_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            return projects, total_count
            
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}")
            return [], 0
    
    async def delete_project(self, project_id: str, soft_delete: bool = True) -> bool:
        """
        Delete project with optional soft delete.
        
        Args:
            project_id: Project UUID
            soft_delete: Use soft delete (archive)
            
        Returns:
            Success status
        """
        try:
            project = await self.get_project(project_id)
            if not project:
                return False
            
            if soft_delete:
                # Soft delete - archive project
                project.status = ProjectStatus.ARCHIVED
                project.updated_at = datetime.utcnow()
                await self.db_session.commit()
            else:
                # Hard delete
                await self.db_session.delete(project)
                await self.db_session.commit()
            
            # Remove from cache
            if self.redis_client:
                await self.redis_client.delete(f"project:{project_id}")
            
            logger.info(f"Project {'archived' if soft_delete else 'deleted'}: {project.project_code}")
            
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to delete project {project_id}: {str(e)}")
            return False
    
    async def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """
        Get comprehensive project analytics and insights.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Analytics data dictionary
        """
        try:
            project = await self.get_project(project_id)
            if not project:
                return {}
            
            # Calculate project metrics
            analytics = {
                'basic_info': {
                    'project_code': project.project_code,
                    'title': project.title,
                    'status': project.status.value,
                    'type': project.project_type.value,
                    'priority': project.priority.value
                },
                'timeline': {
                    'created_at': project.created_at.isoformat(),
                    'start_date': project.start_date.isoformat() if project.start_date else None,
                    'target_end_date': project.target_end_date.isoformat() if project.target_end_date else None,
                    'actual_end_date': project.actual_end_date.isoformat() if project.actual_end_date else None,
                    'duration_days': self._calculate_project_duration(project),
                    'completion_percentage': self._calculate_completion_percentage(project)
                },
                'team': {
                    'team_size': len(project.team_members or []),
                    'creator_id': str(project.creator_id),
                    'team_lead_id': str(project.team_lead_id) if project.team_lead_id else None,
                    'invited_count': len(project.invited_members or [])
                },
                'financial': {
                    'budget_allocated': float(project.budget_allocated or 0),
                    'budget_spent': float(project.budget_spent or 0),
                    'budget_remaining': float((project.budget_allocated or 0) - (project.budget_spent or 0)),
                    'budget_utilization': self._calculate_budget_utilization(project),
                    'revenue_target': float(project.revenue_target or 0)
                },
                'content': {
                    'formats': project.content_formats or [],
                    'platforms': project.target_platforms or [],
                    'deliverables_count': len(project.deliverables or {}),
                    'assets_bucket': project.assets_bucket
                },
                'performance': project.performance_metrics or {},
                'ai_insights': project.ai_insights or {},
                'engagement': project.engagement_stats or {}
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get analytics for project {project_id}: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _generate_project_code(self, project_type: ProjectType) -> str:
        """Generate unique project code based on type and timestamp"""
        type_prefix = {
            ProjectType.MUSIC_COLLABORATION: 'MUS',
            ProjectType.VIDEO_PRODUCTION: 'VID',
            ProjectType.PHOTOGRAPHY_SERIES: 'PHO',
            ProjectType.BLOG_SERIES: 'BLG',
            ProjectType.COMEDY_SKETCH: 'COM',
            ProjectType.MULTI_FORMAT_CAMPAIGN: 'MFC',
            ProjectType.CROSS_PLATFORM_CONTENT: 'CPC'
        }
        
        prefix = type_prefix.get(project_type, 'GEN')
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        random_suffix = str(uuid.uuid4())[:8].upper()
        
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    def _default_collaboration_settings(self) -> Dict[str, Any]:
        """Default collaboration settings for new projects"""
        return {
            'real_time_editing': True,
            'version_control': True,
            'comment_system': True,
            'task_assignment': True,
            'file_sharing': True,
            'video_calls': True,
            'screen_sharing': True,
            'notification_preferences': {
                'email': True,
                'push': True,
                'in_app': True
            }
        }
    
    def _initialize_version_control(self) -> Dict[str, Any]:
        """
Initialize version control structure"""
        return {
            'current_version': '1.0.0',
            'branches': ['main'],
            'commits': [],
            'tags': [],
            'merge_requests': []
        }
    
    def _default_access_permissions(self) -> Dict[str, Any]:
        """
Default access permissions structure"""
        return {
            'read': ['team_member', 'viewer'],
            'write': ['team_member', 'editor'],
            'admin': ['creator', 'team_lead'],
            'delete': ['creator'],
            'invite': ['creator', 'team_lead']
        }
    
    def _initialize_project_metadata(self, request: ProjectCreationRequest) -> Dict[str, Any]:
        """
Initialize comprehensive project metadata"""
        return {
            'creation_context': {
                'source': 'api',
                'timestamp': datetime.utcnow().isoformat(),
                'initial_request': asdict(request)
            },
            'audit_trail': [],
            'performance_tracking': {
                'creation_time': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat()
            },
            'ai_recommendations': [],
            'quality_metrics': {},
            'collaboration_stats': {
                'messages_count': 0,
                'files_shared': 0,
                'edits_count': 0,
                'reviews_count': 0
            }
        }
    
    async def _cache_project(self, project: CollaborationProject):
        """
Cache project data in Redis"""
        try:
            project_data = {
                'id': str(project.id),
                'project_code': project.project_code,
                'title': project.title,
                'status': project.status.value,
                'type': project.project_type.value,
                'creator_id': str(project.creator_id),
                'updated_at': project.updated_at.isoformat()
            }
            
            await self.redis_client.setex(
                f"project:{project.id}",
                self.cache_ttl,
                json.dumps(project_data)
            )
            
        except Exception as e:
            logger.warning(f"Failed to cache project {project.id}: {str(e)}")
    
    def _calculate_project_duration(self, project: CollaborationProject) -> Optional[int]:
        """Calculate project duration in days"""
        if not project.start_date:
            return None
        
        end_date = project.actual_end_date or project.target_end_date or datetime.utcnow()
        return (end_date - project.start_date).days
    
    def _calculate_completion_percentage(self, project: CollaborationProject) -> float:
        """
Calculate project completion percentage"""
        if project.status == ProjectStatus.COMPLETED:
            return 100.0
        elif project.status in [ProjectStatus.DRAFT, ProjectStatus.PLANNING]:
            return 0.0
        
        # Calculate based on deliverables and milestones
        deliverables = project.deliverables or {}
        if not deliverables:
            return 25.0 if project.status == ProjectStatus.ACTIVE else 0.0
        
        completed_items = sum(1 for item in deliverables.values() if item.get('status') == 'completed')
        total_items = len(deliverables)
        
        return (completed_items / total_items) * 100 if total_items > 0 else 0.0
    
    def _calculate_budget_utilization(self, project: CollaborationProject) -> float:
        """
Calculate budget utilization percentage"""
        if not project.budget_allocated or project.budget_allocated == 0:
            return 0.0
        
        spent = project.budget_spent or 0
        return (spent / project.budget_allocated) * 100
    
    def _deserialize_project(self, data: Dict[str, Any]) -> CollaborationProject:
        """
Deserialize project data from cache"""
        # Simplified deserialization for cache data
        project = CollaborationProject()
        project.id = uuid.UUID(data['id'])
        project.project_code = data['project_code']
        project.title = data['title']
        project.status = ProjectStatus(data['status'])
        project.project_type = ProjectType(data['type'])
        project.creator_id = uuid.UUID(data['creator_id'])
        project.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return project

# Export main classes
__all__ = [
    'CollaborationProject',
    'ProjectStatus',
    'ProjectType',
    'ProjectPriority',
    'ProjectCreationRequest',
    'ProjectUpdateRequest',
    'ProjectDatabaseManager'
]
