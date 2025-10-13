"""Pydantic schemas for Cases"""
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from geoalchemy2.shape import to_shape


class CaseType(str, Enum):
    """Case type enumeration"""
    MEDICAL = "medical"
    FOOD = "food"
    SHELTER = "shelter"
    HOMELESS = "homeless"
    ANIMAL = "animal"
    EMERGENCY = "emergency"
    LEGAL = "legal"
    EDUCATION = "education"
    OTHER = "other"


class CaseStatus(str, Enum):
    """Case status enumeration"""
    OPEN = "open"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GeoPoint(BaseModel):
    """Geographic point (latitude, longitude)"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 48.8566,
                "longitude": 2.3522
            }
        }


class CaseBase(BaseModel):
    """Base case schema"""
    type: CaseType
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    location: GeoPoint
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "France"
    urgency_level: Optional[int] = Field(None, ge=1, le=10)
    tags: List[str] = Field(default_factory=list)
    volunteers_needed: int = Field(default=1, ge=1, le=10)


class CaseCreate(CaseBase):
    """Schema for creating a case"""
    photos: List[str] = Field(default_factory=list, max_length=5)
    
    @field_validator('photos')
    @classmethod
    def validate_photos(cls, v):
        """Validate photos list"""
        if len(v) > 5:
            raise ValueError("Maximum 5 photos allowed")
        return v


class CaseUpdate(BaseModel):
    """Schema for updating a case"""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=20)
    status: Optional[CaseStatus] = None
    urgency_level: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None


class CaseResponse(CaseBase):
    """Schema for case response"""
    id: UUID
    user_id: UUID
    status: CaseStatus
    location: Any  # Override to allow WKBElement from database
    ai_classification: dict = Field(default_factory=dict)
    photos: List[str] = Field(default_factory=list)
    main_photo: Optional[str] = None
    volunteers_assigned: int = 0
    views_count: int = 0
    shares_count: int = 0
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    @field_validator('location', mode='before')
    @classmethod
    def convert_location(cls, v: Any) -> dict:
        """Convert PostGIS WKBElement to GeoPoint dict"""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        # Convert WKBElement from PostGIS to GeoPoint
        try:
            shape = to_shape(v)
            return {"latitude": shape.y, "longitude": shape.x}
        except:
            return v
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "type": "homeless",
                "status": "open",
                "title": "Personne sans-abri dans le froid",
                "description": "Homme seul, environ 50 ans, besoin d'aide urgente",
                "location": {
                    "latitude": 48.8566,
                    "longitude": 2.3522
                },
                "address": "Rue de Rivoli, Paris",
                "city": "Paris",
                "country": "France",
                "urgency_level": 8,
                "ai_classification": {
                    "confidence": 0.95,
                    "keywords": ["homeless", "urgent", "cold"]
                },
                "tags": ["urgent", "winter"],
                "photos": [],
                "volunteers_needed": 1,
                "volunteers_assigned": 0,
                "views_count": 5,
                "shares_count": 0,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            }
        }


class CaseDetailResponse(CaseResponse):
    """Schema for detailed case response with relations"""
    activity_log: List[dict] = Field(default_factory=list)
    assignments: List[dict] = Field(default_factory=list)


class CaseFilters(BaseModel):
    """Schema for case filters"""
    type: Optional[CaseType] = None
    status: Optional[CaseStatus] = None
    urgency_min: Optional[int] = Field(None, ge=1, le=10)
    city: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
