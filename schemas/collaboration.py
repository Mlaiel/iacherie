"""
Collaboration & Partnership Schemas for IA Influencer Agent Platform
Professional collaboration matching, partnership management, and revenue sharing schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pydantic import Field, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class CollaborationRequest(BaseSchema):
    """Collaboration request schema."""
    
    requester_id: UUID = Field(description="ID of the creator requesting collaboration")
    target_creator_id: UUID = Field(description="ID of the target creator")
    collaboration_type: str = Field(description="Type of collaboration requested")
    
    # Project details
    project_title: str = Field(min_length=3, max_length=200, description="Project title")
    project_description: str = Field(max_length=2000, description="Detailed project description")
    project_genre: str = Field(description="Project genre/category")
    estimated_duration: Optional[str] = Field(None, description="Estimated project duration")
    
    # Collaboration specifics
    role_requirements: Dict[str, str] = Field(default_factory=dict, description="Required roles and skills")
    contribution_expectations: Dict[str, str] = Field(default_factory=dict)
    deliverables: List[str] = Field(default_factory=list, description="Expected deliverables")
    timeline_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Financial terms
    revenue_sharing_model: str = Field(description="Revenue sharing model")
    revenue_split_percentage: Dict[str, float] = Field(default_factory=dict)
    upfront_payment: Optional[Decimal] = Field(None, ge=0, description="Upfront payment if any")
    budget_range: Optional[Dict[str, Decimal]] = Field(None, description="Project budget range")
    
    # Legal and rights
    copyright_split: Dict[str, float] = Field(default_factory=dict)
    licensing_terms: Dict[str, str] = Field(default_factory=dict)
    exclusive_collaboration: bool = Field(default=False)
    territory_restrictions: List[str] = Field(default_factory=list)
    
    # Communication preferences
    preferred_communication_method: str = Field(default="platform_messaging")
    meeting_availability: Dict[str, Any] = Field(default_factory=dict)
    timezone: str = Field(default="UTC")
    language_preferences: List[str] = Field(default_factory=list)
    
    # Additional information
    portfolio_samples: List[HttpUrl] = Field(default_factory=list)
    reference_links: List[HttpUrl] = Field(default_factory=list)
    special_requirements: Optional[str] = Field(None, max_length=500)
    
    @validator('collaboration_type')
    def validate_collaboration_type(cls, v):
        """Validate collaboration type."""
        allowed_types = {
            "music_production", "songwriting", "vocal_performance", "mixing_mastering",
            "video_production", "photography", "content_creation", "marketing_campaign",
            "brand_partnership", "cross_promotion", "remix_collaboration", "cover_collaboration",
            "podcast_guest", "interview", "live_performance", "tour_collaboration"
        }
        if v not in allowed_types:
            raise ValueError(f'Collaboration type must be one of: {", ".join(allowed_types)}')
        return v


class CollaborationOut(UUIDSchema, TimestampSchema):
    """Active collaboration information schema."""
    
    requester_id: UUID
    collaborator_id: UUID
    collaboration_type: str
    project_title: str
    project_description: str
    
    # Status and timeline
    status: str = Field(description="Current collaboration status")
    start_date: Optional[datetime] = None
    expected_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    progress_percentage: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Financial information (public summary)
    revenue_sharing_model: str
    has_upfront_payment: bool = Field(default=False)
    estimated_project_value: Optional[Decimal] = None
    
    # Project deliverables status
    total_deliverables: int = Field(default=0, ge=0)
    completed_deliverables: int = Field(default=0, ge=0)
    pending_deliverables: List[str] = Field(default_factory=list)
    
    # Communication and updates
    last_activity_date: Optional[datetime] = None
    unread_messages: int = Field(default=0, ge=0)
    next_milestone_date: Optional[datetime] = None
    
    # Performance metrics
    collaboration_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    communication_quality: Optional[float] = Field(None, ge=1.0, le=5.0)
    timeline_adherence: Optional[float] = Field(None, ge=1.0, le=5.0)
    
    # Public visibility
    is_public: bool = Field(default=False, description="Whether collaboration is publicly visible")
    showcase_enabled: bool = Field(default=False, description="Display in portfolio")
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate."""
        if self.total_deliverables == 0:
            return 0.0
        return self.completed_deliverables / self.total_deliverables


class CollaborationAgreement(UUIDSchema, TimestampSchema, AuditSchema):
    """Legal collaboration agreement schema."""
    
    collaboration_id: UUID = Field(description="Associated collaboration ID")
    agreement_type: str = Field(description="Type of legal agreement")
    legal_status: str = Field(description="Legal validation status")
    
    # Parties involved
    primary_party_id: UUID = Field(description="Primary party (project initiator)")
    secondary_party_id: UUID = Field(description="Secondary party (collaborator)")
    additional_parties: List[UUID] = Field(default_factory=list, description="Additional parties if any")
    
    # Agreement terms
    scope_of_work: str = Field(description="Detailed scope of work")
    deliverables_specification: Dict[str, Any] = Field(default_factory=dict)
    quality_standards: Dict[str, str] = Field(default_factory=dict)
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    # Timeline and milestones
    project_start_date: datetime
    project_end_date: datetime
    milestone_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    deadline_penalties: Dict[str, str] = Field(default_factory=dict)
    
    # Financial terms
    total_project_value: Decimal = Field(ge=0)
    payment_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    revenue_sharing_details: Dict[str, Any] = Field(default_factory=dict)
    expense_allocation: Dict[str, str] = Field(default_factory=dict)
    
    # Intellectual property rights
    copyright_ownership: Dict[str, float] = Field(default_factory=dict)
    licensing_rights: Dict[str, Any] = Field(default_factory=dict)
    moral_rights_waiver: bool = Field(default=False)
    attribution_requirements: List[str] = Field(default_factory=list)
    
    # Legal clauses
    termination_clauses: List[str] = Field(default_factory=list)
    dispute_resolution_method: str = Field(default="mediation")
    governing_law: str = Field(description="Governing law jurisdiction")
    confidentiality_terms: Dict[str, str] = Field(default_factory=dict)
    
    # Agreement lifecycle
    draft_version: int = Field(default=1, ge=1)
    is_finalized: bool = Field(default=False)
    signed_by_primary: bool = Field(default=False)
    signed_by_secondary: bool = Field(default=False)
    witness_signatures: List[Dict[str, str]] = Field(default_factory=list)
    
    # Document management
    agreement_document_url: Optional[HttpUrl] = None
    digital_signatures: Dict[str, str] = Field(default_factory=dict)
    blockchain_hash: Optional[str] = Field(None, description="Blockchain verification hash")
    
    @validator('agreement_type')
    def validate_agreement_type(cls, v):
        """Validate agreement type."""
        allowed_types = {
            "collaboration_contract", "work_for_hire", "joint_venture", "partnership_agreement",
            "licensing_agreement", "revenue_sharing_agreement", "non_disclosure_agreement"
        }
        if v not in allowed_types:
            raise ValueError(f'Agreement type must be one of: {", ".join(allowed_types)}')
        return v


class CollaborationRevenue(UUIDSchema, TimestampSchema):
    """Collaboration revenue tracking schema."""
    
    collaboration_id: UUID
    revenue_period_start: datetime
    revenue_period_end: datetime
    
    # Revenue sources
    total_revenue: Decimal = Field(ge=0, description="Total revenue for period")
    revenue_by_source: Dict[str, Decimal] = Field(default_factory=dict)
    revenue_by_platform: Dict[str, Decimal] = Field(default_factory=dict)
    revenue_by_territory: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Revenue distribution
    revenue_shares: Dict[str, Decimal] = Field(default_factory=dict, description="Revenue per collaborator")
    platform_fees: Decimal = Field(default=Decimal('0.00'), ge=0)
    transaction_fees: Decimal = Field(default=Decimal('0.00'), ge=0)
    tax_withholdings: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Performance metrics
    revenue_growth: Optional[Decimal] = Field(None, description="Revenue growth from previous period")
    performance_vs_estimate: Optional[float] = Field(None, description="Performance vs initial estimates")
    top_performing_assets: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Payment status
    payment_status: str = Field(default="pending", description="Payment processing status")
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    
    # Analytics
    audience_demographics: Dict[str, Any] = Field(default_factory=dict)
    engagement_metrics: Dict[str, float] = Field(default_factory=dict)
    conversion_rates: Dict[str, float] = Field(default_factory=dict)


class PartnerMatching(UUIDSchema, TimestampSchema):
    """AI-powered partner matching results schema."""
    
    creator_id: UUID = Field(description="Creator seeking collaboration")
    matching_algorithm_version: str = Field(description="Matching algorithm version")
    
    # Matching criteria
    desired_collaboration_types: List[str] = Field(default_factory=list)
    desired_skills: List[str] = Field(default_factory=list)
    genre_preferences: List[str] = Field(default_factory=list)
    experience_level: str = Field(description="Desired experience level")
    budget_range: Optional[Dict[str, Decimal]] = None
    geographic_preferences: List[str] = Field(default_factory=list)
    
    # Matching results
    potential_partners: List[Dict[str, Any]] = Field(default_factory=list)
    total_matches: int = Field(default=0, ge=0)
    high_compatibility_matches: int = Field(default=0, ge=0)
    
    # Matching scores and reasons
    compatibility_scores: Dict[str, float] = Field(default_factory=dict)
    matching_reasons: Dict[str, List[str]] = Field(default_factory=dict)
    potential_synergies: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Recommendations
    recommended_approaches: Dict[str, str] = Field(default_factory=dict)
    collaboration_suggestions: Dict[str, List[str]] = Field(default_factory=dict)
    success_probability: Dict[str, float] = Field(default_factory=dict)
    
    # Matching performance
    matching_confidence: float = Field(ge=0.0, le=1.0, description="Overall matching confidence")
    processing_time_ms: float = Field(ge=0.0, description="Matching processing time")
    data_freshness_score: float = Field(ge=0.0, le=1.0, description="Data freshness score")


class CollaborationMessage(UUIDSchema, TimestampSchema):
    """Collaboration messaging schema."""
    
    collaboration_id: UUID
    sender_id: UUID
    recipient_id: UUID
    message_type: str = Field(description="Type of message")
    
    # Message content
    subject: Optional[str] = Field(None, max_length=200, description="Message subject")
    content: str = Field(max_length=5000, description="Message content")
    message_priority: str = Field(default="normal", description="Message priority")
    
    # Attachments and media
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    embedded_media: List[HttpUrl] = Field(default_factory=list)
    file_references: List[UUID] = Field(default_factory=list)
    
    # Message status
    is_read: bool = Field(default=False)
    read_at: Optional[datetime] = None
    is_archived: bool = Field(default=False)
    is_starred: bool = Field(default=False)
    
    # Threading and replies
    parent_message_id: Optional[UUID] = Field(None, description="Parent message for replies")
    thread_id: Optional[UUID] = Field(None, description="Message thread ID")
    reply_count: int = Field(default=0, ge=0)
    
    # Metadata
    delivery_status: str = Field(default="delivered")
    encryption_enabled: bool = Field(default=True)
    message_hash: Optional[str] = Field(None, description="Message integrity hash")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Validate message type."""
        allowed_types = {
            "text_message", "file_share", "milestone_update", "feedback_request",
            "revision_request", "approval_notification", "payment_update", 
            "contract_discussion", "meeting_request", "project_update"
        }
        if v not in allowed_types:
            raise ValueError(f'Message type must be one of: {", ".join(allowed_types)}')
        return v


class ProjectCollaboration(UUIDSchema, TimestampSchema, AuditSchema):
    """Extended project collaboration management schema."""
    
    collaboration_id: UUID
    project_name: str = Field(min_length=3, max_length=200)
    project_type: str = Field(description="Type of collaborative project")
    
    # Project structure
    work_packages: List[Dict[str, Any]] = Field(default_factory=list)
    task_assignments: Dict[str, UUID] = Field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)
    critical_path: List[str] = Field(default_factory=list)
    
    # Progress tracking
    overall_progress: float = Field(default=0.0, ge=0.0, le=1.0)
    milestone_progress: Dict[str, float] = Field(default_factory=dict)
    task_completion_status: Dict[str, str] = Field(default_factory=dict)
    blocked_tasks: List[str] = Field(default_factory=list)
    
    # Quality management
    quality_checkpoints: List[Dict[str, Any]] = Field(default_factory=list)
    review_requirements: Dict[str, List[str]] = Field(default_factory=dict)
    approval_workflow: List[Dict[str, str]] = Field(default_factory=list)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Resource management
    resource_allocation: Dict[str, Any] = Field(default_factory=dict)
    budget_tracking: Dict[str, Decimal] = Field(default_factory=dict)
    time_tracking: Dict[str, float] = Field(default_factory=dict)
    tool_requirements: List[str] = Field(default_factory=list)
    
    # Risk management
    identified_risks: List[Dict[str, str]] = Field(default_factory=list)
    risk_mitigation_plans: Dict[str, str] = Field(default_factory=dict)
    contingency_plans: List[str] = Field(default_factory=list)
    
    # Communication and collaboration
    communication_plan: Dict[str, Any] = Field(default_factory=dict)
    meeting_schedule: List[Dict[str, datetime]] = Field(default_factory=list)
    decision_log: List[Dict[str, Any]] = Field(default_factory=list)
    change_requests: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('project_type')
    def validate_project_type(cls, v):
        """Validate project type."""
        allowed_types = {
            "album_production", "single_release", "music_video", "podcast_series",
            "content_campaign", "brand_collaboration", "live_event", "tour_planning",
            "merchandise_development", "app_development", "platform_integration"
        }
        if v not in allowed_types:
            raise ValueError(f'Project type must be one of: {", ".join(allowed_types)}')
        return v


class CollaborationFeedback(UUIDSchema, TimestampSchema):
    """Collaboration feedback and rating schema."""
    
    collaboration_id: UUID
    reviewer_id: UUID = Field(description="ID of the person providing feedback")
    reviewee_id: UUID = Field(description="ID of the person being reviewed")
    
    # Rating categories
    overall_rating: float = Field(ge=1.0, le=5.0, description="Overall collaboration rating")
    communication_rating: float = Field(ge=1.0, le=5.0)
    professionalism_rating: float = Field(ge=1.0, le=5.0)
    creativity_rating: float = Field(ge=1.0, le=5.0)
    reliability_rating: float = Field(ge=1.0, le=5.0)
    technical_skills_rating: float = Field(ge=1.0, le=5.0)
    
    # Detailed feedback
    positive_aspects: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    detailed_comments: Optional[str] = Field(None, max_length=1000)
    
    # Recommendation
    would_collaborate_again: bool = Field(description="Would collaborate again")
    recommend_to_others: bool = Field(description="Would recommend to others")
    collaboration_highlight: Optional[str] = Field(None, description="Best aspect of collaboration")
    
    # Visibility and privacy
    is_public_review: bool = Field(default=False)
    is_anonymous: bool = Field(default=False)
    allow_response: bool = Field(default=True)
    
    # Response from reviewee
    response_provided: bool = Field(default=False)
    response_content: Optional[str] = Field(None, max_length=500)
    response_date: Optional[datetime] = None


class CollaborationAnalytics(UUIDSchema, TimestampSchema):
    """Collaboration analytics and insights schema."""
    
    collaboration_id: UUID
    analytics_period_start: datetime
    analytics_period_end: datetime
    
    # Performance metrics
    project_efficiency_score: float = Field(ge=0.0, le=1.0)
    timeline_adherence_score: float = Field(ge=0.0, le=1.0)
    quality_score: float = Field(ge=0.0, le=1.0)
    collaboration_satisfaction_score: float = Field(ge=0.0, le=1.0)
    
    # Productivity analytics
    tasks_completed_on_time: int = Field(default=0, ge=0)
    average_task_completion_time: float = Field(default=0.0, ge=0.0)
    communication_frequency: float = Field(default=0.0, ge=0.0)
    decision_making_speed: float = Field(default=0.0, ge=0.0)
    
    # Financial performance
    revenue_per_collaborator: Dict[str, Decimal] = Field(default_factory=dict)
    cost_efficiency_ratio: Optional[float] = None
    roi_per_collaborator: Dict[str, float] = Field(default_factory=dict)
    
    # Success indicators
    goal_achievement_rate: float = Field(ge=0.0, le=1.0)
    stakeholder_satisfaction: Dict[str, float] = Field(default_factory=dict)
    market_performance: Dict[str, Any] = Field(default_factory=dict)
    
    # Insights and recommendations
    success_factors: List[str] = Field(default_factory=list)
    improvement_opportunities: List[str] = Field(default_factory=list)
    best_practices_identified: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)
