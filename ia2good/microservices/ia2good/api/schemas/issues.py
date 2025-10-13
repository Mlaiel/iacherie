"""Pydantic schemas for Issues API"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Enums
class IssueType(str):
    ENVIRONMENTAL = "environmental"
    INFRASTRUCTURE = "infrastructure"
    SAFETY = "safety"
    HERITAGE = "heritage"
    ACCESSIBILITY = "accessibility"
    OTHER = "other"


class IssueStatus(str):
    REPORTED = "reported"
    VERIFIED = "verified"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class IssueSeverity(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Issue schemas
class IssueBase(BaseModel):
    type: str
    title: str = Field(..., max_length=200)
    description: str
    severity: str = "medium"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class IssueCreate(IssueBase):
    media_urls: List[str] = Field(default_factory=list)
    media_types: List[str] = Field(default_factory=list)
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['environmental', 'infrastructure', 'safety', 'heritage', 'accessibility', 'other']
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v not in valid_severities:
            raise ValueError(f'Severity must be one of: {", ".join(valid_severities)}')
        return v


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    
    @validator('severity')
    def validate_severity(cls, v):
        if v is not None:
            valid_severities = ['low', 'medium', 'high', 'critical']
            if v not in valid_severities:
                raise ValueError(f'Severity must be one of: {", ".join(valid_severities)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['reported', 'verified', 'in_progress', 'resolved', 'rejected']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class IssueResponse(IssueBase):
    id: UUID
    status: str
    reported_by: UUID
    volunteer_id: Optional[UUID] = None
    media_urls: List[str] = []
    media_types: List[str] = []
    views_count: int = 0
    followers_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    recommended_to: List[str] = []
    notified_organizations: List[str] = []
    notified_authorities: List[str] = []
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    resolution_media: List[str] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Issue Comment schemas
class IssueCommentCreate(BaseModel):
    content: str
    media_urls: List[str] = Field(default_factory=list)


class IssueCommentResponse(BaseModel):
    id: UUID
    issue_id: UUID
    user_id: UUID
    content: str
    media_urls: List[str] = []
    is_official: bool = False
    likes_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


# Issue Follow schemas
class IssueFollowCreate(BaseModel):
    notify_on_update: bool = True
    notify_on_comment: bool = True
    notify_on_resolution: bool = True


class IssueFollowResponse(BaseModel):
    id: UUID
    issue_id: UUID
    user_id: UUID
    notify_on_update: bool
    notify_on_comment: bool
    notify_on_resolution: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Issue Resolution schemas
class IssueResolveCreate(BaseModel):
    resolution_notes: str
    resolution_media: List[str] = Field(default_factory=list)


# Issue List filters
class IssueFilters(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    tags: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = 10.0
    skip: int = 0
    limit: int = 20
