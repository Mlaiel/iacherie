"""Advanced Team Collaboration Database Model

Enterprise-grade SQLAlchemy model for creator collaboration, team management,
and intelligent matching systems for multi-format content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class CollaborationType(Enum):
    """Types of collaboration"""    MUSIC_PRODUCTION = "music_production"
    VIDEO_CREATION = "video_creation"
    PODCAST_COLLABORATION = "podcast_collaboration"
    CONTENT_SERIES = "content_series"
    CROSS_PROMOTION = "cross_promotion"
    BRAND_PARTNERSHIP = "brand_partnership"
    EDUCATIONAL_CONTENT = "educational_content"
    LIVE_PERFORMANCE = "live_performance"
    REMIX_PROJECT = "remix_project"
    CHARITY_CAMPAIGN = "charity_campaign"


class CollaborationStatus(Enum):
    """Collaboration request status"""    DRAFT = "draft"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TeamRole(Enum):
    """Team member roles"""    LEAD_CREATOR = "lead_creator"
    CO_CREATOR = "co_creator"
    PRODUCER = "producer"
    SONGWRITER = "songwriter"
    VOCALIST = "vocalist"
    INSTRUMENTALIST = "instrumentalist"
    VIDEO_EDITOR = "video_editor"
    GRAPHIC_DESIGNER = "graphic_designer"
    MARKETING_SPECIALIST = "marketing_specialist"
    SOCIAL_MEDIA_MANAGER = "social_media_manager"
    BRAND_MANAGER = "brand_manager"
    TECHNICAL_SUPPORT = "technical_support"


class SkillLevel(Enum):
    """Skill proficiency levels"""    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class MatchingCriteria(Enum):
    """AI matching criteria"""    GENRE_COMPATIBILITY = "genre_compatibility"
    AUDIENCE_OVERLAP = "audience_overlap"
    ENGAGEMENT_SIMILARITY = "engagement_similarity"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    COLLABORATION_HISTORY = "collaboration_history"
    SKILL_COMPLEMENTARITY = "skill_complementarity"
    BRAND_ALIGNMENT = "brand_alignment"
    SCHEDULING_COMPATIBILITY = "scheduling_compatibility"


class CreatorCollaboration(Base):
    """    Creator Collaboration Model
    
    Manages collaboration requests, team formation, and project coordination
    between content creators with AI-powered matching and optimization.
    """    __tablename__ = "creator_collaborations"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiator_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    collaboration_type = Column(SQLEnum(CollaborationType), nullable=False, index=True)
    
    # Basic information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(CollaborationStatus), default=CollaborationStatus.DRAFT, index=True)
    
    # Project details
    expected_duration_days = Column(Integer, nullable=True)
    budget_range_min = Column(Numeric(18, 8), nullable=True)
    budget_range_max = Column(Numeric(18, 8), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Requirements and preferences
    required_skills = Column(ARRAY(String), nullable=True)
    preferred_genres = Column(ARRAY(String), nullable=True)
    target_audience_demographics = Column(JSON, nullable=True)
    content_format_requirements = Column(JSON, nullable=True)
    
    # Matching criteria
    ai_matching_enabled = Column(Boolean, default=True)
    matching_criteria_weights = Column(JSON, nullable=True)
    minimum_match_score = Column(Float, default=0.7)
    geographic_restrictions = Column(ARRAY(String), nullable=True)
    
    # Team composition
    maximum_team_size = Column(Integer, default=5)
    current_team_size = Column(Integer, default=1)
    open_positions = Column(JSON, nullable=True)  # Available roles
    skills_gap_analysis = Column(JSON, nullable=True)
    
    # Revenue and rights sharing
    revenue_sharing_model = Column(String(100), default="equal_split")
    revenue_distribution = Column(JSON, nullable=True)
    intellectual_property_terms = Column(JSON, nullable=True)
    licensing_agreement_template = Column(Text, nullable=True)
    
    # Timeline and milestones
    project_start_date = Column(DateTime(timezone=True), nullable=True)
    project_end_date = Column(DateTime(timezone=True), nullable=True)
    milestones = Column(JSON, nullable=True)
    deliverables = Column(JSON, nullable=True)
    
    # Communication and coordination
    primary_communication_platform = Column(String(100), nullable=True)
    meeting_schedule = Column(JSON, nullable=True)
    file_sharing_workspace = Column(String(255), nullable=True)
    project_management_tool = Column(String(100), nullable=True)
    
    # Quality and compliance
    content_quality_standards = Column(JSON, nullable=True)
    brand_guidelines = Column(JSON, nullable=True)
    legal_requirements = Column(JSON, nullable=True)
    platform_compliance_rules = Column(JSON, nullable=True)
    
    # Performance tracking
    collaboration_success_score = Column(Float, nullable=True)
    team_synergy_rating = Column(Float, nullable=True)
    project_completion_rate = Column(Float, nullable=True)
    audience_engagement_impact = Column(JSON, nullable=True)
    
    # AI insights and recommendations
    ai_compatibility_analysis = Column(JSON, nullable=True)
    success_probability_prediction = Column(Float, nullable=True)
    optimization_suggestions = Column(JSON, nullable=True)
    risk_assessment = Column(JSON, nullable=True)
    
    # Marketing and promotion
    cross_promotion_strategy = Column(JSON, nullable=True)
    social_media_plan = Column(JSON, nullable=True)
    press_release_template = Column(Text, nullable=True)
    promotional_timeline = Column(JSON, nullable=True)
    
    # Financial tracking
    total_budget_allocated = Column(Numeric(18, 8), default=Decimal('0.0'))
    expenses_incurred = Column(Numeric(18, 8), default=Decimal('0.0'))
    revenue_generated = Column(Numeric(18, 8), default=Decimal('0.0'))
    roi_calculation = Column(Float, nullable=True)
    
    # Contract and legal
    contract_template_id = Column(UUID(as_uuid=True), nullable=True)
    legal_review_required = Column(Boolean, default=False)
    nda_required = Column(Boolean, default=False)
    contract_signed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_public = Column(Boolean, default=True)
    is_urgent = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    team_members = relationship("CollaborationTeamMember", back_populates="collaboration", cascade="all, delete-orphan")
    applications = relationship("CollaborationApplication", back_populates="collaboration", cascade="all, delete-orphan")
    ai_matches = relationship("AICollaborationMatch", back_populates="collaboration", cascade="all, delete-orphan")
    project_updates = relationship("ProjectUpdate", back_populates="collaboration", cascade="all, delete-orphan")
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_collaborations_initiator_type', 'initiator_user_id', 'collaboration_type'),
        Index('idx_collaborations_status_public', 'status', 'is_public'),
        Index('idx_collaborations_budget_range', 'budget_range_min', 'budget_range_max'),
        Index('idx_collaborations_timeline', 'project_start_date', 'project_end_date'),
        Index('idx_collaborations_matching', 'ai_matching_enabled', 'minimum_match_score'),
        Index('idx_collaborations_success', 'collaboration_success_score', 'team_synergy_rating'),
    )
    
    def __repr__(self):
        return f"<CreatorCollaboration(id={self.id}, title={self.title}, status={self.status.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""        return {
            "id": str(self.id),
            "initiator_user_id": str(self.initiator_user_id),
            "collaboration_type": self.collaboration_type.value,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "expected_duration_days": self.expected_duration_days,
            "budget_range_min": float(self.budget_range_min) if self.budget_range_min else None,
            "budget_range_max": float(self.budget_range_max) if self.budget_range_max else None,
            "currency": self.currency,
            "required_skills": self.required_skills,
            "preferred_genres": self.preferred_genres,
            "target_audience_demographics": self.target_audience_demographics,
            "content_format_requirements": self.content_format_requirements,
            "ai_matching_enabled": self.ai_matching_enabled,
            "matching_criteria_weights": self.matching_criteria_weights,
            "minimum_match_score": self.minimum_match_score,
            "geographic_restrictions": self.geographic_restrictions,
            "maximum_team_size": self.maximum_team_size,
            "current_team_size": self.current_team_size,
            "open_positions": self.open_positions,
            "skills_gap_analysis": self.skills_gap_analysis,
            "revenue_sharing_model": self.revenue_sharing_model,
            "revenue_distribution": self.revenue_distribution,
            "intellectual_property_terms": self.intellectual_property_terms,
            "project_start_date": self.project_start_date.isoformat() if self.project_start_date else None,
            "project_end_date": self.project_end_date.isoformat() if self.project_end_date else None,
            "milestones": self.milestones,
            "deliverables": self.deliverables,
            "primary_communication_platform": self.primary_communication_platform,
            "meeting_schedule": self.meeting_schedule,
            "file_sharing_workspace": self.file_sharing_workspace,
            "project_management_tool": self.project_management_tool,
            "content_quality_standards": self.content_quality_standards,
            "brand_guidelines": self.brand_guidelines,
            "legal_requirements": self.legal_requirements,
            "platform_compliance_rules": self.platform_compliance_rules,
            "collaboration_success_score": self.collaboration_success_score,
            "team_synergy_rating": self.team_synergy_rating,
            "project_completion_rate": self.project_completion_rate,
            "audience_engagement_impact": self.audience_engagement_impact,
            "ai_compatibility_analysis": self.ai_compatibility_analysis,
            "success_probability_prediction": self.success_probability_prediction,
            "optimization_suggestions": self.optimization_suggestions,
            "risk_assessment": self.risk_assessment,
            "cross_promotion_strategy": self.cross_promotion_strategy,
            "social_media_plan": self.social_media_plan,
            "promotional_timeline": self.promotional_timeline,
            "total_budget_allocated": float(self.total_budget_allocated) if self.total_budget_allocated else None,
            "expenses_incurred": float(self.expenses_incurred) if self.expenses_incurred else None,
            "revenue_generated": float(self.revenue_generated) if self.revenue_generated else None,
            "roi_calculation": self.roi_calculation,
            "legal_review_required": self.legal_review_required,
            "nda_required": self.nda_required,
            "contract_signed_date": self.contract_signed_date.isoformat() if self.contract_signed_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_public": self.is_public,
            "is_urgent": self.is_urgent,
            "is_featured": self.is_featured,
            "is_verified": self.is_verified
        }


class CollaborationTeamMember(Base):
    """    Collaboration Team Member Model
    
    Manages team members within collaboration projects.
    """    __tablename__ = "collaboration_team_members"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('creator_collaborations.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Role and responsibilities
    team_role = Column(SQLEnum(TeamRole), nullable=False)
    role_description = Column(Text, nullable=True)
    responsibilities = Column(ARRAY(String), nullable=True)
    skill_contributions = Column(JSON, nullable=True)
    
    # Participation details
    join_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expected_time_commitment_hours = Column(Integer, nullable=True)
    actual_time_contributed_hours = Column(Integer, default=0)
    
    # Performance tracking
    contribution_quality_score = Column(Float, nullable=True)
    collaboration_rating = Column(Float, nullable=True)
    milestone_completion_rate = Column(Float, default=0.0)
    
    # Revenue sharing
    revenue_share_percentage = Column(Float, nullable=False)
    earnings_to_date = Column(Numeric(18, 8), default=Decimal('0.0'))
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_lead = Column(Boolean, default=False)
    can_invite_others = Column(Boolean, default=False)
    
    # Relationships
    collaboration = relationship("CreatorCollaboration", back_populates="team_members")
    
    def __repr__(self):
        return f"<CollaborationTeamMember(id={self.id}, role={self.team_role.value}, share={self.revenue_share_percentage}%)>"


class CollaborationApplication(Base):
    """    Collaboration Application Model
    
    Manages applications to join collaboration projects.
    """    __tablename__ = "collaboration_applications"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('creator_collaborations.id'), nullable=False, index=True)
    applicant_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Application details
    applied_role = Column(SQLEnum(TeamRole), nullable=False)
    motivation_statement = Column(Text, nullable=False)
    relevant_experience = Column(Text, nullable=True)
    portfolio_links = Column(ARRAY(String), nullable=True)
    
    # Qualifications
    skills_offered = Column(JSON, nullable=True)
    skill_levels = Column(JSON, nullable=True)
    availability_hours_per_week = Column(Integer, nullable=True)
    preferred_revenue_share = Column(Float, nullable=True)
    
    # Application status
    application_status = Column(String(50), default="pending")  # pending, reviewing, accepted, rejected
    reviewed_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # AI scoring
    ai_compatibility_score = Column(Float, nullable=True)
    skill_match_score = Column(Float, nullable=True)
    experience_relevance_score = Column(Float, nullable=True)
    
    # Timestamps
    applied_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    collaboration = relationship("CreatorCollaboration", back_populates="applications")
    
    def __repr__(self):
        return f"<CollaborationApplication(id={self.id}, role={self.applied_role.value}, status={self.application_status})>"


class AICollaborationMatch(Base):
    """    AI Collaboration Match Model
    
    Stores AI-generated matches between creators and collaboration opportunities.
    """    __tablename__ = "ai_collaboration_matches"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('creator_collaborations.id'), nullable=False, index=True)
    matched_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Matching scores
    overall_match_score = Column(Float, nullable=False, index=True)
    genre_compatibility_score = Column(Float, nullable=True)
    audience_overlap_score = Column(Float, nullable=True)
    skill_complementarity_score = Column(Float, nullable=True)
    collaboration_history_score = Column(Float, nullable=True)
    
    # Match analysis
    matching_algorithm_version = Column(String(50), nullable=False)
    match_reasoning = Column(JSON, nullable=True)
    potential_synergies = Column(JSON, nullable=True)
    predicted_success_probability = Column(Float, nullable=True)
    
    # User interaction
    viewed_by_user = Column(Boolean, default=False)
    user_interest_level = Column(String(20), nullable=True)  # high, medium, low, none
    contacted_user = Column(Boolean, default=False)
    
    # Timestamps
    matched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    contacted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    collaboration = relationship("CreatorCollaboration", back_populates="ai_matches")
    
    def __repr__(self):
        return f"<AICollaborationMatch(id={self.id}, score={self.overall_match_score}, viewed={self.viewed_by_user})>"


class ProjectUpdate(Base):
    """    Project Update Model
    
    Tracks progress updates and communications within collaboration projects.
    """    __tablename__ = "project_updates"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('creator_collaborations.id'), nullable=False, index=True)
    author_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Update content
    update_type = Column(String(50), nullable=False)  # progress, milestone, announcement, issue
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    attachments = Column(ARRAY(String), nullable=True)
    
    # Progress tracking
    milestone_completed = Column(String(255), nullable=True)
    progress_percentage = Column(Float, nullable=True)
    next_steps = Column(Text, nullable=True)
    blockers_identified = Column(JSON, nullable=True)
    
    # Visibility and notifications
    is_public = Column(Boolean, default=True)
    notify_team_members = Column(Boolean, default=True)
    requires_feedback = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    collaboration = relationship("CreatorCollaboration", back_populates="project_updates")
    
    def __repr__(self):
        return f"<ProjectUpdate(id={self.id}, type={self.update_type}, title={self.title})>"
