"""{{model_name}} Database Model Template for Ainflue Platform
import asyncio

{{model_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime, timezone
from enum import Enum
import uuid

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, validator, ConfigDict

from core.database import Base, get_session
from core.config import get_settings
from utils.exceptions import ValidationError

logger = logging.getLogger(__name__)
settings = get_settings()


class RecordStatus(Enum):
    """Record status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DELETED = "deleted"
    ARCHIVED = "archived"


class AuditMixin:
    """Mixin for audit fields"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)


class VersionMixin:
    """Mixin for record versioning"""
    version = Column(Integer, default=1, nullable=False)
    
    def increment_version(self) -> None:
        """Increment version number"""
        self.version = (self.version or 0) + 1


class {{model_name}}Model(Base, AuditMixin, SoftDeleteMixin, VersionMixin):
    """{{model_description}}
    
    Comprehensive database model providing:
    - Primary key with UUID support
    - Audit fields (created/updated timestamps and users)
    - Soft delete functionality
    - Record versioning and optimistic locking
    - JSON/JSONB field support for flexible data
    - Proper indexing for performance
    - Relationship management
    - Data validation and constraints
    - Full-text search capabilities
    - Metadata and tagging support
    """
    
    __tablename__ = '{{table_name}}'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Core fields
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=RecordStatus.ACTIVE.value, nullable=False, index=True)
    
    # Business-specific fields
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    config = Column(JSONB, nullable=True)
    
    # Relationships (examples)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('{{table_name}}.id'), nullable=True, index=True)
    
    # Performance and search fields
    search_vector = Column(Text, nullable=True)  # For full-text search
    priority = Column(Integer, default=0, nullable=False, index=True)
    weight = Column(Integer, default=1, nullable=False)
    
    # Boolean flags
    is_public = Column(Boolean, default=False, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False, index=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="{{table_name}}_records", foreign_keys=[owner_id])
    parent = relationship("{{model_name}}Model", remote_side=[id], back_populates="children")
    children = relationship("{{model_name}}Model", back_populates="parent")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_{{table_name}}_name_status', 'name', 'status'),
        Index('idx_{{table_name}}_created_status', 'created_at', 'status'),
        Index('idx_{{table_name}}_owner_status', 'owner_id', 'status'),
        Index('idx_{{table_name}}_category_status', 'category', 'status'),
        Index('idx_{{table_name}}_search', 'search_vector'),
        UniqueConstraint('name', 'owner_id', name='uq_{{table_name}}_name_owner'),
    )
    
    @validates('status')
    def validate_status(self, key, status) -> None:
        """Validate status field"""
        valid_statuses = [s.value for s in RecordStatus]
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}. Must be one of: {valid_statuses}")
        return status
    
    @validates('name')
    def validate_name(self, key, name) -> None:
        """Validate name field"""
        if not name or not name.strip():
            raise ValidationError("Name cannot be empty")
        if len(name.strip()) > 255:
            raise ValidationError("Name cannot exceed 255 characters")
        return name.strip()
    
    @validates('priority')
    def validate_priority(self, key, priority) -> None:
        """Validate priority field"""
        if priority is not None and (priority < 0 or priority > 10):
            raise ValidationError("Priority must be between 0 and 10")
        return priority
    
    def soft_delete(self, deleted_by -> None: Optional[uuid.UUID] = None) -> None:
        """Perform soft delete"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = deleted_by
        self.status = RecordStatus.DELETED.value
    
    def restore(self) -> None:
        """Restore soft deleted record"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.status = RecordStatus.ACTIVE.value
    
    def add_tag(self, tag -> None: str) -> None:
        """Add a tag to the record"""
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            # Mark as modified for SQLAlchemy
            self.tags = self.tags.copy()
    
    def remove_tag(self, tag -> None: str) -> None:
        """Remove a tag from the record"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            # Mark as modified for SQLAlchemy
            self.tags = self.tags.copy()
    
    def set_metadata(self, key -> None: str, value -> None: Any) -> None:
        """Set metadata key-value pair"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
        # Mark as modified for SQLAlchemy
        self.metadata = self.metadata.copy()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key"""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def update_search_vector(self) -> None:
        """Update search vector for full-text search"""
        searchable_text = []
        
        if self.name:
            searchable_text.append(self.name)
        if self.description:
            searchable_text.append(self.description)
        if self.category:
            searchable_text.append(self.category)
        if self.tags:
            searchable_text.extend(self.tags)
        
        self.search_vector = ' '.join(searchable_text).lower()
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'category': self.category,
            'tags': self.tags,
            'metadata': self.metadata,
            'config': self.config,
            'priority': self.priority,
            'weight': self.weight,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'is_locked': self.is_locked,
            'is_deleted': self.is_deleted,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'owner_id': str(self.owner_id) if self.owner_id else None,
            'parent_id': str(self.parent_id) if self.parent_id else None,
        }
        
        if include_relations:
            result.update({
                'owner': self.owner.to_dict() if self.owner else None,
                'parent': self.parent.to_dict() if self.parent else None,
                'children': [child.to_dict() for child in self.children] if self.children else []
            })
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '{{model_name}}Model':
        """Create model instance from dictionary"""
        # Remove fields that shouldn't be set directly
        excluded_fields = {'id', 'created_at', 'updated_at', 'deleted_at', 'version'}
        filtered_data = {k: v for k, v in data.items() if k not in excluded_fields}
        
        return cls(**filtered_data)
    
    def __repr__(self) -> str:
        return f"<{{model_name}}Model(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def __str__(self) -> str:
        return self.name or f"{{model_name}} {self.id}"


# Pydantic schemas for API serialization/deserialization

class {{model_name}}Base(BaseModel):
    """Base {{model_name}} schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Record name")
    description: Optional[str] = Field(default=None, description="Record description")
    category: Optional[str] = Field(default=None, max_length=100, description="Record category")
    tags: Optional[List[str]] = Field(default=None, description="Record tags")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration data")
    priority: Optional[int] = Field(default=0, ge=0, le=10, description="Priority level")
    weight: Optional[int] = Field(default=1, ge=1, description="Weight value")
    is_public: Optional[bool] = Field(default=False, description="Public visibility")
    is_featured: Optional[bool] = Field(default=False, description="Featured status")
    
    @validator('name')
    def validate_name(cls, v) -> None:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v) -> None:
        if v is not None:
            # Remove duplicates and empty tags
            v = list(set(tag.strip() for tag in v if tag and tag.strip()))
        return v


class {{model_name}}Create({{model_name}}Base):
    """Schema for creating {{model_name}}"""
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    parent_id: Optional[str] = Field(default=None, description="Parent record ID")


class {{model_name}}Update(BaseModel):
    """Schema for updating {{model_name}}"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Record name")
    description: Optional[str] = Field(default=None, description="Record description")
    category: Optional[str] = Field(default=None, max_length=100, description="Record category")
    tags: Optional[List[str]] = Field(default=None, description="Record tags")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration data")
    status: Optional[str] = Field(default=None, description="Record status")
    priority: Optional[int] = Field(default=None, ge=0, le=10, description="Priority level")
    weight: Optional[int] = Field(default=None, ge=1, description="Weight value")
    is_public: Optional[bool] = Field(default=None, description="Public visibility")
    is_featured: Optional[bool] = Field(default=None, description="Featured status")
    is_locked: Optional[bool] = Field(default=None, description="Lock status")
    
    @validator('name')
    def validate_name(cls, v) -> None:
        if v is not None and (not v or not v.strip()):
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v
    
    @validator('status')
    def validate_status(cls, v) -> None:
        if v is not None:
            valid_statuses = [s.value for s in RecordStatus]
            if v not in valid_statuses:
                raise ValueError(f'Invalid status: {v}. Must be one of: {valid_statuses}')
        return v


class {{model_name}}Response({{model_name}}Base):
    """Schema for {{model_name}} response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Record ID")
    status: str = Field(..., description="Record status")
    is_deleted: bool = Field(..., description="Soft delete status")
    is_locked: bool = Field(..., description="Lock status")
    version: int = Field(..., description="Record version")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Deletion timestamp")
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    parent_id: Optional[str] = Field(default=None, description="Parent record ID")
    created_by: Optional[str] = Field(default=None, description="Created by user ID")
    updated_by: Optional[str] = Field(default=None, description="Updated by user ID")
    deleted_by: Optional[str] = Field(default=None, description="Deleted by user ID")


class {{model_name}}DetailResponse({{model_name}}Response):
    """Schema for detailed {{model_name}} response with relationships"""
    owner: Optional[Dict[str, Any]] = Field(default=None, description="Owner details")
    parent: Optional[Dict[str, Any]] = Field(default=None, description="Parent record details")
    children: Optional[List[Dict[str, Any]]] = Field(default=None, description="Child records")


class {{model_name}}ListResponse(BaseModel):
    """Schema for {{model_name}} list response"""
    items: List[{{model_name}}Response] = Field(..., description="List of records")
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


# Repository pattern for database operations

class {{model_name}}Repository:
    """Repository for {{model_name}} database operations"""
    
    def __init__(self, session -> None: Session) -> None:
        self.session = session
    
    async def create(self, data: {{model_name}}Create, created_by: Optional[str] = None) -> {{model_name}}Model:
        """Create new record"""
        db_obj = {{model_name}}Model(**data.dict())
        if created_by:
            db_obj.created_by = uuid.UUID(created_by)
        
        db_obj.update_search_vector()
        
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        
        return db_obj
    
    async def get(self, id: Union[str, uuid.UUID], include_deleted: bool = False) -> Optional[{{model_name}}Model]:
        """Get record by ID"""
        query = self.session.query({{model_name}}Model).filter({{model_name}}Model.id == id)
        
        if not include_deleted:
            query = query.filter({{model_name}}Model.is_deleted == False)
        
        return query.first()
    
    async def get_by_name(self, name: str, owner_id: Optional[str] = None, include_deleted: bool = False) -> Optional[{{model_name}}Model]:
        """Get record by name"""
        query = self.session.query({{model_name}}Model).filter({{model_name}}Model.name == name)
        
        if owner_id:
            query = query.filter({{model_name}}Model.owner_id == owner_id)
        
        if not include_deleted:
            query = query.filter({{model_name}}Model.is_deleted == False)
        
        return query.first()
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        include_deleted: bool = False,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[{{model_name}}Model]:
        """List records with filtering and pagination"""
        query = self.session.query({{model_name}}Model)
        
        # Apply filters
        if owner_id:
            query = query.filter({{model_name}}Model.owner_id == owner_id)
        
        if category:
            query = query.filter({{model_name}}Model.category == category)
        
        if status:
            query = query.filter({{model_name}}Model.status == status)
        
        if not include_deleted:
            query = query.filter({{model_name}}Model.is_deleted == False)
        
        # Apply ordering
        if hasattr({{model_name}}Model, order_by):
            column = getattr({{model_name}}Model, order_by)
            if order_direction.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        
        # Apply pagination
        return query.offset(skip).limit(limit).all()
    
    async def update(self, id: Union[str, uuid.UUID], data: {{model_name}}Update, updated_by: Optional[str] = None) -> Optional[{{model_name}}Model]:
        """Update record"""
        db_obj = await self.get(id)
        if not db_obj:
            return None
        
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        if updated_by:
            db_obj.updated_by = uuid.UUID(updated_by)
        
        db_obj.increment_version()
        db_obj.update_search_vector()
        
        self.session.commit()
        self.session.refresh(db_obj)
        
        return db_obj
    
    async def delete(self, id: Union[str, uuid.UUID], deleted_by: Optional[str] = None, hard_delete: bool = False) -> bool:
        """Delete record (soft or hard)"""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        if hard_delete:
            self.session.delete(db_obj)
        else:
            db_obj.soft_delete(uuid.UUID(deleted_by) if deleted_by else None)
        
        self.session.commit()
        return True
    
    async def search(self, query: str, limit: int = 50) -> List[{{model_name}}Model]:
        """Search records by text"""
        search_query = self.session.query({{model_name}}Model).filter(
            {{model_name}}Model.search_vector.contains(query.lower()),
            {{model_name}}Model.is_deleted == False
        ).order_by({{model_name}}Model.priority.desc(), {{model_name}}Model.created_at.desc()).limit(limit)
        
        return search_query.all()
    
    async def count(self, owner_id: Optional[str] = None, include_deleted: bool = False) -> int:
        """Count records"""
        query = self.session.query({{model_name}}Model)
        
        if owner_id:
            query = query.filter({{model_name}}Model.owner_id == owner_id)
        
        if not include_deleted:
            query = query.filter({{model_name}}Model.is_deleted == False)
        
        return query.count()
    
    async def get_by_tags(self, tags: List[str], include_deleted: bool = False) -> List[{{model_name}}Model]:
        """Get records by tags"""
        query = self.session.query({{model_name}}Model)
        
        for tag in tags:
            query = query.filter({{model_name}}Model.tags.contains([tag]))
        
        if not include_deleted:
            query = query.filter({{model_name}}Model.is_deleted == False)
        
        return query.all()
    
    async def get_featured(self, limit: int = 10) -> List[{{model_name}}Model]:
        """Get featured records"""
        return self.session.query({{model_name}}Model).filter(
            {{model_name}}Model.is_featured == True,
            {{model_name}}Model.is_deleted == False,
            {{model_name}}Model.status == RecordStatus.ACTIVE.value
        ).order_by({{model_name}}Model.priority.desc()).limit(limit).all()
    
    async def bulk_update_status(self, ids: List[Union[str, uuid.UUID]], status: str, updated_by: Optional[str] = None) -> int:
        """Bulk update status for multiple records"""
        query = self.session.query({{model_name}}Model).filter({{model_name}}Model.id.in_(ids))
        
        update_data = {"status": status}
        if updated_by:
            update_data["updated_by"] = uuid.UUID(updated_by)
        
        updated_count = query.update(update_data, synchronize_session=False)
        self.session.commit()
        
        return updated_count

# File has syntax issues - needs manual review