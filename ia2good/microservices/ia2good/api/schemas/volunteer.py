"""Pydantic schemas for Volunteers"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field

from .case import GeoPoint


class VerificationStatus(str, Enum):
    """Verification status enumeration"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class VolunteerSkill(str, Enum):
    """Available volunteer skills"""
    MEDICAL = "medical"
    TRANSPORT = "transport"
    SHELTER = "shelter"
    FOOD = "food"
    LEGAL = "legal"
    PSYCHOLOGICAL = "psychological"
    TRANSLATION = "translation"
    TECHNICAL = "technical"


class VolunteerProfileBase(BaseModel):
    """Base volunteer profile schema"""
    location: GeoPoint
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "France"
    skills: List[str] = Field(default_factory=list, min_length=1, max_length=10)
    languages: List[str] = Field(default=["fr"])
    certifications: dict = Field(default_factory=dict)
    max_distance_km: int = Field(default=10, ge=1, le=100)
    availability_schedule: dict = Field(default_factory=dict)
    preferred_case_types: List[str] = Field(default_factory=list)


class VolunteerProfileCreate(VolunteerProfileBase):
    """Schema for creating a volunteer profile"""
    pass


class VolunteerProfileUpdate(BaseModel):
    """Schema for updating volunteer profile"""
    location: Optional[GeoPoint] = None
    address: Optional[str] = None
    city: Optional[str] = None
    skills: Optional[List[str]] = Field(None, min_length=1, max_length=10)
    languages: Optional[List[str]] = None
    certifications: Optional[dict] = None
    availability_status: Optional[bool] = None
    max_distance_km: Optional[int] = Field(None, ge=1, le=100)
    availability_schedule: Optional[dict] = None
    notification_radius_km: Optional[int] = Field(None, ge=1, le=50)
    preferred_case_types: Optional[List[str]] = None


class UserSummary(BaseModel):
    """Summary of user information"""
    id: UUID
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class VolunteerProfileResponse(VolunteerProfileBase):
    """Schema for volunteer profile response"""
    id: UUID
    user_id: UUID
    availability_status: bool
    verification_status: VerificationStatus
    identity_verified: bool
    background_check: bool
    reliability_score: float
    total_cases_completed: int
    total_hours_volunteered: int
    average_rating: Optional[float] = None
    total_ratings: int = 0
    notification_radius_km: int
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "location": {
                    "latitude": 48.8566,
                    "longitude": 2.3522
                },
                "city": "Paris",
                "country": "France",
                "skills": ["medical", "transport"],
                "languages": ["fr", "en"],
                "certifications": {
                    "first_aid": True,
                    "driver_license": True
                },
                "availability_status": True,
                "verification_status": "verified",
                "identity_verified": True,
                "background_check": True,
                "reliability_score": 95.5,
                "total_cases_completed": 15,
                "total_hours_volunteered": 45,
                "average_rating": 4.8,
                "total_ratings": 12,
                "max_distance_km": 10,
                "notification_radius_km": 5,
                "created_at": "2025-01-10T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z"
            }
        }


class VolunteerDetailResponse(VolunteerProfileResponse):
    """Detailed volunteer profile with user info"""
    user: Optional[UserSummary] = None
    recent_cases: List[dict] = Field(default_factory=list)
    achievements: List[dict] = Field(default_factory=list)


class VolunteerStatsResponse(BaseModel):
    """Volunteer statistics response"""
    total_cases_completed: int
    total_hours_volunteered: int
    reliability_score: float
    average_rating: Optional[float]
    total_ratings: int
    response_time_avg_minutes: Optional[int] = None
    achievements_count: int
    points_total: int
    rank: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_cases_completed": 15,
                "total_hours_volunteered": 45,
                "reliability_score": 95.5,
                "average_rating": 4.8,
                "total_ratings": 12,
                "response_time_avg_minutes": 15,
                "achievements_count": 5,
                "points_total": 350,
                "rank": 42
            }
        }


class VolunteerFilters(BaseModel):
    """Schema for volunteer filters"""
    skills: Optional[List[str]] = None
    city: Optional[str] = None
    available: Optional[bool] = None
    verified_only: bool = True
    sort_by: str = Field(default="reliability_score")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class VerificationData(BaseModel):
    """Schema for volunteer verification"""
    identity_verified: bool = False
    background_check: bool = False
    verification_notes: Optional[str] = None
