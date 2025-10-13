"""Pydantic schemas for Events API"""
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Enums
class EventType(str):
    CLEANUP = "cleanup"
    PROTEST = "protest"
    WORKSHOP = "workshop"
    FUNDRAISER = "fundraiser"
    AWARENESS = "awareness"
    TREE_PLANTING = "tree_planting"
    FOOD_DISTRIBUTION = "food_distribution"
    COMMUNITY_GATHERING = "community_gathering"
    OTHER = "other"


class EventStatus(str):
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Event schemas
class EventBase(BaseModel):
    type: str
    title: str = Field(..., max_length=200)
    description: str
    objectives: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    venue_name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    registration_deadline: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)


class EventCreate(EventBase):
    co_organizers: List[UUID] = Field(default_factory=list)
    capacity: Optional[int] = None
    min_participants: Optional[int] = None
    cover_image: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    age_minimum: Optional[int] = None
    equipment_needed: List[str] = Field(default_factory=list)
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['cleanup', 'protest', 'workshop', 'fundraiser', 'awareness', 
                      'tree_planting', 'food_distribution', 'community_gathering', 'other']
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    objectives: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    capacity: Optional[int] = None
    tags: Optional[List[str]] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['draft', 'published', 'ongoing', 'completed', 'cancelled']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class EventResponse(EventBase):
    id: UUID
    status: str
    organizer_id: UUID
    co_organizers: List[UUID] = []
    capacity: Optional[int] = None
    participants_count: int = 0
    checked_in_count: int = 0
    min_participants: Optional[int] = None
    cover_image: Optional[str] = None
    images: List[str] = []
    videos: List[str] = []
    photos_after: List[str] = []
    required_skills: List[str] = []
    age_minimum: Optional[int] = None
    equipment_needed: List[str] = []
    attendance_count: int = 0
    impact_summary: Optional[str] = None
    impact_metrics: Dict = {}
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Event Participant schemas
class EventParticipantCreate(BaseModel):
    role: str = "participant"  # participant, helper, coordinator
    tasks_assigned: List[str] = Field(default_factory=list)


class EventParticipantUpdate(BaseModel):
    status: Optional[str] = None  # registered, approved, declined, attended, absent
    tasks_assigned: Optional[List[str]] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None


class EventParticipantResponse(BaseModel):
    id: UUID
    event_id: UUID
    user_id: UUID
    status: str
    role: str
    tasks_assigned: List[str] = []
    checked_in: bool = False
    checked_in_at: Optional[datetime] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None
    registered_at: datetime
    
    class Config:
        from_attributes = True


# Event Update (announcement) schemas
class EventUpdateCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: str
    media_urls: List[str] = Field(default_factory=list)
    update_type: str = "general"  # general, important, reminder, cancellation
    notify_participants: bool = True
    
    @validator('update_type')
    def validate_update_type(cls, v):
        valid_types = ['general', 'important', 'reminder', 'cancellation']
        if v not in valid_types:
            raise ValueError(f'Update type must be one of: {", ".join(valid_types)}')
        return v


class EventUpdateResponse(BaseModel):
    id: UUID
    event_id: UUID
    author_id: UUID
    title: Optional[str] = None
    content: str
    media_urls: List[str] = []
    update_type: str
    notify_participants: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Event Check-in
class EventCheckInCreate(BaseModel):
    user_id: Optional[UUID] = None  # Si organizer check-in quelqu'un d'autre


# Event Impact
class EventImpactUpdate(BaseModel):
    impact_summary: str
    impact_metrics: Dict
    photos_after: List[str] = Field(default_factory=list)


# Event Filters
class EventFilters(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    start_date_after: Optional[datetime] = None
    start_date_before: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = 10.0
    skip: int = 0
    limit: int = 20
