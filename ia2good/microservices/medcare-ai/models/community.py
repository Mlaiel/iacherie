"""
Community forum models for MedCare-AI
Anonymous case discussions, second opinions, medical advice
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class AuthorType(str, Enum):
    """Type of forum participant"""
    PATIENT = "patient"
    DOCTOR = "doctor"
    SPECIALIST = "specialist"
    PHARMACIST = "pharmacist"

class PostType(str, Enum):
    """Type of community post"""
    CASE_DISCUSSION = "case_discussion"
    SECOND_OPINION = "second_opinion"
    MEDICAL_ADVICE = "medical_advice"
    DOCUMENT_REVIEW = "document_review"

class PostStatus(str, Enum):
    """Status of community post"""
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"
    FLAGGED = "flagged"

class CommunityPostCreate(BaseModel):
    """Create a community post"""
    author_id: UUID
    author_type: AuthorType
    post_type: PostType
    title: str = Field(min_length=10, max_length=255)
    content: str = Field(min_length=50)
    language: str = "en"
    related_document_id: Optional[UUID] = None
    is_anonymous: bool = True
    tags: List[str] = Field(default_factory=list)

class CommunityPost(BaseModel):
    """Complete community post"""
    id: UUID
    author_id: UUID
    author_type: AuthorType
    post_type: PostType
    title: str
    content: str
    language: str
    related_document_id: Optional[UUID]
    is_anonymous: bool
    anonymous_display_name: str
    tags: List[str]
    status: PostStatus
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CommunityResponseCreate(BaseModel):
    """Create a response to community post"""
    author_id: UUID
    author_type: AuthorType
    content: str = Field(min_length=20)
    language: str = "en"
    is_anonymous: bool = True

class CommunityResponse(BaseModel):
    """Complete community response"""
    id: UUID
    post_id: UUID
    author_id: UUID
    author_type: AuthorType
    content: str
    language: str
    is_anonymous: bool
    anonymous_display_name: str
    helpful_votes: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PostWithResponses(BaseModel):
    """Post with all responses"""
    post: CommunityPost
    responses: List[CommunityResponse]
    response_count: int
    
class VoteResponse(BaseModel):
    """Vote on a helpful response"""
    voter_id: UUID
    is_helpful: bool = True
