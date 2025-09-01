"""Collaboration and Community Schemas

Comprehensive Pydantic schemas for artist collaboration, community features,
and professional networking in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl
from pydantic.types import PositiveInt, PositiveFloat


class CollaborationTypeEnum(str, Enum):
    """Types of collaborations"""
    MUSICAL_COLLABORATION = "musical_collaboration"
    REMIX_PROJECT = "remix_project"
    FEATURED_ARTIST = "featured_artist"
    PRODUCER_COLLABORATION = "producer_collaboration"
    SONGWRITER_COLLABORATION = "songwriter_collaboration"
    VOCAL_COLLABORATION = "vocal_collaboration"
    INSTRUMENTAL_COLLABORATION = "instrumental_collaboration"
    VIDEO_COLLABORATION = "video_collaboration"
    PODCAST_COLLABORATION = "podcast_collaboration"
    LIVE_PERFORMANCE = "live_performance"
    TOUR_COLLABORATION = "tour_collaboration"
    BRAND_PARTNERSHIP = "brand_partnership"
    CROSS_PROMOTION = "cross_promotion"
    MENTORSHIP = "mentorship"
    SKILL_EXCHANGE = "skill_exchange"
    JOINT_VENTURE = "joint_venture"


class CollaborationStatusEnum(str, Enum):
    """Collaboration request status"""
    DRAFT = "draft"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COUNTER_PROPOSED = "counter_proposed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"


class SkillLevelEnum(str, Enum):
    """Skill level classifications"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    EXPERT = "expert"
    MASTER = "master"


class AvailabilityEnum(str, Enum):
    """Availability status"""
    IMMEDIATELY = "immediately"
    WITHIN_WEEK = "within_week"
    WITHIN_MONTH = "within_month"
    FLEXIBLE = "flexible"
    BUSY = "busy"
    NOT_AVAILABLE = "not_available"


class CommunicationMethodEnum(str, Enum):
    """Preferred communication methods"""
    EMAIL = "email"
    PHONE = "phone"
    VIDEO_CALL = "video_call"
    INSTANT_MESSAGE = "instant_message"
    IN_PERSON = "in_person"
    PLATFORM_MESSAGE = "platform_message"
    DISCORD = "discord"
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class RevenueShareTypeEnum(str, Enum):
    """Revenue sharing types"""
    EQUAL_SPLIT = "equal_split"
    PERCENTAGE_BASED = "percentage_based"
    CREDIT_BASED = "credit_based"
    FIXED_PAYMENT = "fixed_payment"
    NO_REVENUE_SHARE = "no_revenue_share"
    NEGOTIABLE = "negotiable"
    PERFORMANCE_BASED = "performance_based"


class CollaboratorProfileSchema(BaseModel):
    """Schema for collaborator profile information"""
    user_id: PositiveInt = Field(..., description="User ID")
    display_name: str = Field(..., description="Display name")
    professional_name: Optional[str] = Field(None, description="Professional/stage name")
    bio: Optional[str] = Field(None, max_length=1000, description="Biography")
    
    # Contact information
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    website: Optional[HttpUrl] = Field(None, description="Personal/professional website")
    location: Optional[str] = Field(None, description="Geographic location")
    timezone: Optional[str] = Field(None, description="Timezone")
    
    # Professional information
    primary_role: str = Field(..., description="Primary role (musician, producer, etc.)")
    secondary_roles: Optional[List[str]] = Field(None, description="Secondary roles")
    genres: List[str] = Field(..., description="Musical genres")
    instruments: Optional[List[str]] = Field(None, description="Instruments played")
    software_skills: Optional[List[str]] = Field(None, description="Software/DAW skills")
    
    # Experience and credentials
    years_experience: Optional[int] = Field(None, ge=0, description="Years of experience")
    skill_level: SkillLevelEnum = Field(..., description="Overall skill level")
    education: Optional[List[str]] = Field(None, description="Educational background")
    certifications: Optional[List[str]] = Field(None, description="Professional certifications")
    awards: Optional[List[str]] = Field(None, description="Awards and recognition")
    
    # Portfolio and samples
    portfolio_urls: Optional[List[HttpUrl]] = Field(None, description="Portfolio URLs")
    sample_tracks: Optional[List[str]] = Field(None, description="Sample track URLs")
    video_samples: Optional[List[str]] = Field(None, description="Video sample URLs")
    
    # Social media and platforms
    social_media_links: Optional[Dict[str, HttpUrl]] = Field(None, description="Social media profiles")
    streaming_profiles: Optional[Dict[str, HttpUrl]] = Field(None, description="Streaming platform profiles")
    
    # Collaboration preferences
    collaboration_types: List[CollaborationTypeEnum] = Field(..., description="Preferred collaboration types")
    availability: AvailabilityEnum = Field(..., description="Current availability")
    preferred_communication: List[CommunicationMethodEnum] = Field(..., description="Preferred communication methods")
    remote_collaboration: bool = Field(True, description="Open to remote collaboration")
    in_person_collaboration: bool = Field(False, description="Open to in-person collaboration")
    
    # Rates and payment
    hourly_rate: Optional[Decimal] = Field(None, description="Hourly rate")
    project_rate_range: Optional[str] = Field(None, description="Project rate range")
    revenue_share_preference: RevenueShareTypeEnum = Field(..., description="Revenue share preference")
    currency: str = Field("EUR", description="Preferred currency")
    
    # Verification and reputation
    verified_profile: bool = Field(False, description="Profile verification status")
    reputation_score: float = Field(0.0, ge=0.0, le=5.0, description="Reputation score")
    completed_collaborations: int = Field(0, description="Number of completed collaborations")
    positive_reviews: int = Field(0, description="Number of positive reviews")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "display_name": "Alex Producer",
                "primary_role": "music_producer",
                "genres": ["electronic", "hip-hop", "pop"],
                "years_experience": 8,
                "skill_level": "professional",
                "availability": "within_week",
                "hourly_rate": "75.00",
                "reputation_score": 4.8
            }
        }


class CollaborationProjectSchema(BaseModel):
    """Schema for collaboration project details"""
    project_title: str = Field(..., description="Project title")
    project_description: str = Field(..., max_length=2000, description="Detailed project description")
    collaboration_type: CollaborationTypeEnum = Field(..., description="Type of collaboration")
    
    # Project specifications
    genre: str = Field(..., description="Musical genre")
    style: Optional[str] = Field(None, description="Musical style")
    mood: Optional[str] = Field(None, description="Desired mood/vibe")
    tempo_bpm: Optional[int] = Field(None, ge=60, le=200, description="Tempo in BPM")
    key_signature: Optional[str] = Field(None, description="Key signature")
    
    # Technical requirements
    duration_minutes: Optional[float] = Field(None, description="Expected duration in minutes")
    audio_quality: Optional[str] = Field(None, description="Required audio quality")
    file_formats: Optional[List[str]] = Field(None, description="Required file formats")
    sample_rate: Optional[int] = Field(None, description="Required sample rate")
    
    # Content requirements
    vocal_requirements: Optional[str] = Field(None, description="Vocal requirements")
    instrumental_requirements: Optional[str] = Field(None, description="Instrumental requirements")
    lyrical_themes: Optional[List[str]] = Field(None, description="Lyrical themes")
    reference_tracks: Optional[List[str]] = Field(None, description="Reference track URLs")
    
    # Timeline and deadlines
    estimated_duration: Optional[str] = Field(None, description="Estimated project duration")
    deadline: Optional[date] = Field(None, description="Project deadline")
    milestones: Optional[List[Dict]] = Field(None, description="Project milestones")
    
    # Resources and assets
    provided_assets: Optional[List[str]] = Field(None, description="Assets provided by requester")
    required_assets: Optional[List[str]] = Field(None, description="Assets required from collaborator")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_title": "Electronic Pop Track Production",
                "project_description": "Looking for a producer to create an upbeat electronic pop track...",
                "collaboration_type": "producer_collaboration",
                "genre": "electronic_pop",
                "tempo_bpm": 128,
                "duration_minutes": 3.5,
                "deadline": "2024-10-15"
            }
        }


class RevenueShareAgreementSchema(BaseModel):
    """Schema for revenue sharing agreements"""
    revenue_share_type: RevenueShareTypeEnum = Field(..., description="Type of revenue sharing")
    
    # Percentage-based sharing
    requester_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Requester's percentage")
    collaborator_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Collaborator's percentage")
    
    # Fixed payment
    fixed_amount: Optional[Decimal] = Field(None, description="Fixed payment amount")
    currency: str = Field("EUR", description="Currency")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    
    # Credit and attribution
    requester_credit: str = Field(..., description="Credit for requester")
    collaborator_credit: str = Field(..., description="Credit for collaborator")
    credit_order: Optional[str] = Field(None, description="Order of credits")
    
    # Rights and ownership
    master_recording_ownership: Optional[str] = Field(None, description="Master recording ownership split")
    publishing_ownership: Optional[str] = Field(None, description="Publishing ownership split")
    sync_rights: Optional[str] = Field(None, description="Sync rights distribution")
    
    # Performance and streaming
    streaming_revenue_split: Optional[str] = Field(None, description="Streaming revenue split")
    performance_royalty_split: Optional[str] = Field(None, description="Performance royalty split")
    mechanical_royalty_split: Optional[str] = Field(None, description="Mechanical royalty split")
    
    # Additional terms
    advance_payment: Optional[Decimal] = Field(None, description="Advance payment amount")
    recoupment_terms: Optional[str] = Field(None, description="Recoupment terms")
    minimum_guarantee: Optional[Decimal] = Field(None, description="Minimum guaranteed payment")
    
    @field_validator('collaborator_percentage')
    @classmethod
    def validate_percentage_total(cls, v, values):
        """Validate that percentages add up to 100"""
        requester_pct = values.get('requester_percentage', 0)
        if v and requester_pct and (v + requester_pct) != 100:
            raise ValueError("Percentages must add up to 100")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "revenue_share_type": "percentage_based",
                "requester_percentage": "60.00",
                "collaborator_percentage": "40.00",
                "requester_credit": "Artist Name",
                "collaborator_credit": "Producer Name",
                "streaming_revenue_split": "60/40",
                "currency": "EUR"
            }
        }


class CollaborationRequestBaseSchema(BaseModel):
    """Base schema for collaboration requests"""
    requester_id: PositiveInt = Field(..., description="User ID of requester")
    collaboration_project: CollaborationProjectSchema = Field(..., description="Project details")
    
    # Target collaborator criteria
    target_collaborator_id: Optional[PositiveInt] = Field(None, description="Specific collaborator ID")
    required_skills: List[str] = Field(..., description="Required skills")
    preferred_experience_level: SkillLevelEnum = Field(..., description="Preferred experience level")
    preferred_genres: Optional[List[str]] = Field(None, description="Preferred musical genres")
    location_preference: Optional[str] = Field(None, description="Location preference")
    budget_range: Optional[str] = Field(None, description="Budget range")
    
    # Revenue and payment
    revenue_agreement: RevenueShareAgreementSchema = Field(..., description="Revenue sharing agreement")
    
    # Communication and workflow
    preferred_communication: List[CommunicationMethodEnum] = Field(..., description="Preferred communication methods")
    remote_collaboration_ok: bool = Field(True, description="Remote collaboration acceptable")
    in_person_required: bool = Field(False, description="In-person collaboration required")
    
    # Additional requirements
    portfolio_required: bool = Field(False, description="Portfolio review required")
    audition_required: bool = Field(False, description="Audition required")
    nda_required: bool = Field(False, description="NDA required")
    exclusive_collaboration: bool = Field(False, description="Exclusive collaboration period")
    
    # Timeline
    response_deadline: Optional[datetime] = Field(None, description="Response deadline")
    project_start_date: Optional[date] = Field(None, description="Preferred project start date")


class CollaborationRequestCreateSchema(CollaborationRequestBaseSchema):
    """Schema for creating collaboration requests"""
    # Visibility and promotion
    public_listing: bool = Field(True, description="Make request publicly visible")
    featured_request: bool = Field(False, description="Request featured placement")
    auto_matching: bool = Field(True, description="Enable automatic matching")
    
    # Notification preferences
    email_notifications: bool = Field(True, description="Enable email notifications")
    push_notifications: bool = Field(True, description="Enable push notifications")
    
    # Additional options
    save_as_template: bool = Field(False, description="Save as template for future use")
    template_name: Optional[str] = Field(None, description="Template name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "requester_id": 123,
                "required_skills": ["music_production", "mixing", "mastering"],
                "preferred_experience_level": "professional",
                "budget_range": "500-1500 EUR",
                "remote_collaboration_ok": True,
                "public_listing": True,
                "auto_matching": True
            }
        }


class CollaborationRequestUpdateSchema(BaseModel):
    """Schema for updating collaboration requests"""
    collaboration_project: Optional[CollaborationProjectSchema] = Field(None, description="Updated project details")
    required_skills: Optional[List[str]] = Field(None, description="Updated required skills")
    budget_range: Optional[str] = Field(None, description="Updated budget range")
    revenue_agreement: Optional[RevenueShareAgreementSchema] = Field(None, description="Updated revenue agreement")
    status: Optional[CollaborationStatusEnum] = Field(None, description="Updated status")
    public_listing: Optional[bool] = Field(None, description="Updated visibility")
    response_deadline: Optional[datetime] = Field(None, description="Updated response deadline")
    
    class Config:
        json_schema_extra = {
            "example": {
                "budget_range": "750-2000 EUR",
                "status": "pending",
                "response_deadline": "2024-09-15T23:59:59Z"
            }
        }


class CollaborationResponseSchema(BaseModel):
    """Schema for collaboration responses"""
    response_id: str = Field(..., description="Unique response identifier")
    request_id: PositiveInt = Field(..., description="Collaboration request ID")
    responder_id: PositiveInt = Field(..., description="Responder user ID")
    
    # Response details
    interest_level: int = Field(..., ge=1, le=10, description="Interest level (1-10)")
    proposed_rate: Optional[Decimal] = Field(None, description="Proposed rate/fee")
    availability_start: Optional[date] = Field(None, description="Available start date")
    estimated_completion: Optional[date] = Field(None, description="Estimated completion date")
    
    # Counter-proposal
    counter_proposal: Optional[RevenueShareAgreementSchema] = Field(None, description="Counter-proposal terms")
    additional_requirements: Optional[str] = Field(None, description="Additional requirements")
    questions: Optional[str] = Field(None, description="Questions for requester")
    
    # Portfolio and samples
    relevant_portfolio: Optional[List[str]] = Field(None, description="Relevant portfolio items")
    sample_work: Optional[List[str]] = Field(None, description="Sample work URLs")
    references: Optional[List[str]] = Field(None, description="Professional references")
    
    # Communication preferences
    preferred_next_step: str = Field(..., description="Preferred next step")
    availability_for_discussion: Optional[str] = Field(None, description="Availability for discussion")
    
    # Response metadata
    response_timestamp: datetime = Field(..., description="Response timestamp")
    auto_generated: bool = Field(False, description="Whether response was auto-generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response_id": "RESP-2024-001234",
                "request_id": 12345,
                "responder_id": 456,
                "interest_level": 9,
                "proposed_rate": "1200.00",
                "availability_start": "2024-09-01",
                "preferred_next_step": "video_call_discussion"
            }
        }


class CollaborationRequestResponseSchema(CollaborationRequestBaseSchema):
    """Schema for collaboration request responses"""
    id: PositiveInt = Field(..., description="Unique request ID")
    request_reference: str = Field(..., description="Human-readable request reference")
    
    # Status and tracking
    status: CollaborationStatusEnum = Field(..., description="Current request status")
    priority: int = Field(5, ge=1, le=10, description="Request priority")
    
    # Matching and responses
    matched_collaborators: List[CollaboratorProfileSchema] = Field([], description="Matched collaborator profiles")
    received_responses: List[CollaborationResponseSchema] = Field([], description="Received responses")
    response_count: int = Field(0, description="Number of responses received")
    
    # Analytics and performance
    view_count: int = Field(0, description="Number of views")
    interest_score: float = Field(0.0, description="Calculated interest score")
    matching_accuracy: Optional[float] = Field(None, description="Matching algorithm accuracy")
    
    # Timeline tracking
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Request expiration")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    # Visibility and promotion
    public_listing: bool = Field(..., description="Publicly visible")
    featured: bool = Field(False, description="Featured request")
    boosted: bool = Field(False, description="Boosted for better visibility")
    
    # Communication
    message_thread_id: Optional[str] = Field(None, description="Message thread ID")
    unread_messages: int = Field(0, description="Number of unread messages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "request_reference": "COL-2024-001234",
                "status": "pending",
                "response_count": 8,
                "view_count": 156,
                "interest_score": 7.8,
                "public_listing": True,
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class CollaborationMatchingSchema(BaseModel):
    """Schema for collaboration matching algorithm"""
    request_id: PositiveInt = Field(..., description="Collaboration request ID")
    potential_matches: List[Dict[str, Any]] = Field(..., description="Potential matches with scores")
    matching_criteria: Dict[str, float] = Field(..., description="Matching criteria weights")
    algorithm_version: str = Field(..., description="Matching algorithm version")
    
    # Matching scores
    skill_match_scores: Dict[str, float] = Field(..., description="Skill matching scores")
    experience_match_scores: Dict[str, float] = Field(..., description="Experience matching scores")
    genre_match_scores: Dict[str, float] = Field(..., description="Genre matching scores")
    availability_scores: Dict[str, float] = Field(..., description="Availability scores")
    location_scores: Dict[str, float] = Field(..., description="Location proximity scores")
    
    # Overall metrics
    average_match_score: float = Field(..., description="Average match score")
    top_match_score: float = Field(..., description="Highest match score")
    recommendation_confidence: float = Field(..., description="Recommendation confidence")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": 12345,
                "algorithm_version": "v2.1",
                "average_match_score": 0.78,
                "top_match_score": 0.92,
                "recommendation_confidence": 0.85
            }
        }


class CommunityEventSchema(BaseModel):
    """Schema for community events and activities"""
    event_id: str = Field(..., description="Unique event identifier")
    event_title: str = Field(..., description="Event title")
    event_type: str = Field(..., description="Type of event")
    description: str = Field(..., description="Event description")
    
    # Event details
    start_datetime: datetime = Field(..., description="Event start time")
    end_datetime: datetime = Field(..., description="Event end time")
    timezone: str = Field(..., description="Event timezone")
    location: Optional[str] = Field(None, description="Physical location")
    virtual_location: Optional[HttpUrl] = Field(None, description="Virtual meeting URL")
    
    # Participation
    organizer_id: PositiveInt = Field(..., description="Event organizer user ID")
    max_participants: Optional[int] = Field(None, description="Maximum participants")
    current_participants: int = Field(0, description="Current participant count")
    registration_required: bool = Field(False, description="Registration required")
    registration_fee: Optional[Decimal] = Field(None, description="Registration fee")
    
    # Content and format
    agenda: Optional[List[Dict]] = Field(None, description="Event agenda")
    speakers: Optional[List[str]] = Field(None, description="Event speakers")
    topics: List[str] = Field(..., description="Event topics")
    skill_level: Optional[SkillLevelEnum] = Field(None, description="Target skill level")
    
    # Visibility and access
    public_event: bool = Field(True, description="Publicly visible event")
    member_only: bool = Field(False, description="Members only")
    invite_only: bool = Field(False, description="Invite only")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "EVT-2024-001234",
                "event_title": "Electronic Music Production Workshop",
                "event_type": "workshop",
                "start_datetime": "2024-09-15T18:00:00Z",
                "end_datetime": "2024-09-15T21:00:00Z",
                "organizer_id": 123,
                "max_participants": 50,
                "public_event": True
            }
        }


# Export schemas
__all__ = [
    # Enums
    "CollaborationTypeEnum",
    "CollaborationStatusEnum",
    "SkillLevelEnum",
    "AvailabilityEnum",
    "CommunicationMethodEnum",
    "RevenueShareTypeEnum",
    
    # Complex schemas
    "CollaboratorProfileSchema",
    "CollaborationProjectSchema",
    "RevenueShareAgreementSchema",
    "CollaborationResponseSchema",
    "CollaborationMatchingSchema",
    "CommunityEventSchema",
    
    # Main schemas
    "CollaborationRequestBaseSchema",
    "CollaborationRequestCreateSchema",
    "CollaborationRequestUpdateSchema",
    "CollaborationRequestResponseSchema"
]
