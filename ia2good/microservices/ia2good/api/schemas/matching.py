"""Pydantic schemas for Matching and Assignments"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field


class AssignmentStatus(str, Enum):
    """Assignment status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MatchRecommendation(BaseModel):
    """Match recommendation for a volunteer"""
    volunteer_id: UUID
    volunteer_name: str
    match_score: float = Field(..., ge=0, le=100)
    distance_km: float
    skills_match: List[str] = Field(default_factory=list)
    availability: bool
    estimated_arrival_minutes: Optional[int] = None
    match_reasons: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "volunteer_id": "123e4567-e89b-12d3-a456-426614174002",
                "volunteer_name": "Jean Dupont",
                "match_score": 92.5,
                "distance_km": 2.5,
                "skills_match": ["medical", "transport"],
                "availability": True,
                "estimated_arrival_minutes": 15,
                "match_reasons": {
                    "skills_score": 40,
                    "distance_score": 25,
                    "availability_score": 15,
                    "reliability_score": 12.5
                }
            }
        }


class AssignmentCreate(BaseModel):
    """Schema for creating an assignment"""
    case_id: UUID
    volunteer_id: UUID
    match_score: Optional[float] = Field(None, ge=0, le=100)


class AssignmentUpdate(BaseModel):
    """Schema for updating assignment status"""
    status: AssignmentStatus


class AssignmentCompletion(BaseModel):
    """Schema for completing an assignment"""
    completion_notes: str = Field(..., min_length=10)
    photos: List[str] = Field(default_factory=list, max_length=5)
    next_steps: Optional[str] = None


class RatingData(BaseModel):
    """Schema for rating an assignment"""
    rating: int = Field(..., ge=1, le=5)
    feedback: str = Field(..., min_length=10)
    recommend: bool = True


class AssignmentResponse(BaseModel):
    """Schema for assignment response"""
    id: UUID
    case_id: UUID
    volunteer_id: UUID
    status: AssignmentStatus
    match_score: Optional[float] = None
    match_reasons: dict = Field(default_factory=dict)
    assigned_at: datetime
    accepted_at: Optional[datetime] = None
    declined_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    response_time_minutes: Optional[int] = None
    completion_time_minutes: Optional[int] = None
    volunteer_rating: Optional[int] = None
    volunteer_feedback: Optional[str] = None
    reporter_rating: Optional[int] = None
    reporter_feedback: Optional[str] = None
    completion_notes: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "case_id": "123e4567-e89b-12d3-a456-426614174000",
                "volunteer_id": "123e4567-e89b-12d3-a456-426614174002",
                "status": "completed",
                "match_score": 92.5,
                "match_reasons": {
                    "skills_score": 40,
                    "distance_score": 25
                },
                "assigned_at": "2025-01-15T10:30:00Z",
                "accepted_at": "2025-01-15T10:35:00Z",
                "started_at": "2025-01-15T10:45:00Z",
                "completed_at": "2025-01-15T12:00:00Z",
                "response_time_minutes": 5,
                "completion_time_minutes": 75,
                "volunteer_rating": 5,
                "volunteer_feedback": "Intervention rapide et efficace",
                "reporter_rating": 5,
                "reporter_feedback": "Excellent volontaire"
            }
        }


class TeamAssignmentRequest(BaseModel):
    """Schema for requesting team assignment"""
    required_skills: List[str] = Field(..., min_length=1)
    team_size: int = Field(default=3, ge=2, le=10)


class ActivityResponse(BaseModel):
    """Schema for activity log response"""
    id: UUID
    case_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    volunteer_id: Optional[UUID] = None
    activity_type: str
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        from_attributes = True
