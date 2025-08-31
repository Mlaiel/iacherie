"""Collaboration Requests Database Model

Enterprise-grade SQLAlchemy model for managing content collaboration requests,
partnerships, and multi-creator projects with advanced workflow management.

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
"""from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class CollaborationType(Enum):
    """Collaboration type enumeration"""    REMIX = "remix"
    COVER = "cover"
    FEATURE = "feature"
    DUET = "duet"
    MASHUP = "mashup"
    SAMPLE = "sample"
    CO_CREATION = "co_creation"
    PRODUCTION = "production"
    SONGWRITING = "songwriting"
    VOCAL_FEATURE = "vocal_feature"
    INSTRUMENTAL = "instrumental"
    MIXING = "mixing"
    MASTERING = "mastering"
    VIDEO_COLLABORATION = "video_collaboration"
    PODCAST_GUEST = "podcast_guest"
    LIVESTREAM = "livestream"
    BRAND_PARTNERSHIP = "brand_partnership"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_TOUR = "joint_tour"
    COMPILATION = "compilation"


class RequestStatus(Enum):
    """Request status enumeration"""    PENDING = "pending"
    SENT = "sent"
    RECEIVED = "received"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ON_HOLD = "on_hold"
    REQUIRES_REVISION = "requires_revision"
    NEGOTIATING = "negotiating"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Priority(Enum):
    """Request priority levels"""    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CollaborationScope(Enum):
    """Scope of collaboration"""    SINGLE_TRACK = "single_track"
    EP = "ep"
    ALBUM = "album"
    SERIES = "series"
    ONGOING = "ongoing"
    PROJECT_BASED = "project_based"
    SEASONAL = "seasonal"
    ONE_TIME = "one_time"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"


class RevenueShareType(Enum):
    """Revenue sharing types"""    EQUAL_SPLIT = "equal_split"
    PROPORTIONAL = "proportional"
    WEIGHTED = "weighted"
    FLAT_FEE = "flat_fee"
    PERCENTAGE = "percentage"
    PERFORMANCE_BASED = "performance_based"
    NEGOTIATED = "negotiated"
    NO_REVENUE = "no_revenue"


class CollaborationRequest(Base):
    """    Enterprise Collaboration Request Model
    
    Comprehensive collaboration management system for content creators supporting
    complex workflows, revenue sharing, and multi-party agreements.
    """    __tablename__ = "collaboration_requests"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    target_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('user_content.id'), nullable=True, index=True)
    
    # Request identification
    request_number = Column(String(100), unique=True, nullable=False, index=True)
    request_title = Column(String(500), nullable=False)
    request_description = Column(Text, nullable=True)
    external_reference = Column(String(255), nullable=True)
    
    # Collaboration details
    collaboration_type = Column(SQLEnum(CollaborationType), nullable=False, index=True)
    collaboration_scope = Column(SQLEnum(CollaborationScope), nullable=False)
    request_status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, index=True)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM, index=True)
    
    # Participant information
    requester_name = Column(String(255), nullable=False)
    requester_email = Column(String(255), nullable=True)
    requester_profile = Column(JSON, nullable=True)
    requester_portfolio = Column(JSON, nullable=True)
    
    target_name = Column(String(255), nullable=False)
    target_email = Column(String(255), nullable=True)
    target_profile = Column(JSON, nullable=True)
    target_skills = Column(ARRAY(String), nullable=True)
    
    # Additional collaborators
    additional_collaborators = Column(JSON, nullable=True)
    collaborator_roles = Column(JSON, nullable=True)
    team_structure = Column(JSON, nullable=True)
    
    # Content and project details
    content_title = Column(String(500), nullable=True)
    content_genre = Column(String(100), nullable=True)
    content_style = Column(String(100), nullable=True)
    content_mood = Column(String(100), nullable=True)
    content_duration = Column(Float, nullable=True)
    content_requirements = Column(JSON, nullable=True)
    
    # Project specifications
    project_goals = Column(JSON, nullable=True)
    creative_direction = Column(Text, nullable=True)
    technical_requirements = Column(JSON, nullable=True)
    quality_standards = Column(JSON, nullable=True)
    deliverables = Column(JSON, nullable=True)
    
    # Timeline and scheduling
    proposed_start_date = Column(DateTime(timezone=True), nullable=True)
    proposed_end_date = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    milestone_dates = Column(JSON, nullable=True)
    time_zone = Column(String(50), default="UTC")
    
    # Availability and constraints
    availability_windows = Column(JSON, nullable=True)
    time_constraints = Column(JSON, nullable=True)
    geographic_constraints = Column(JSON, nullable=True)
    equipment_requirements = Column(JSON, nullable=True)
    location_preferences = Column(JSON, nullable=True)
    
    # Financial terms
    revenue_share_type = Column(SQLEnum(RevenueShareType), default=RevenueShareType.EQUAL_SPLIT)
    revenue_splits = Column(JSON, nullable=True)
    budget_range = Column(JSON, nullable=True)
    payment_terms = Column(JSON, nullable=True)
    expense_sharing = Column(JSON, nullable=True)
    currency = Column(String(3), default="EUR")
    
    # Rights and ownership
    copyright_split = Column(JSON, nullable=True)
    publishing_rights = Column(JSON, nullable=True)
    master_rights = Column(JSON, nullable=True)
    performance_rights = Column(JSON, nullable=True)
    sync_rights = Column(JSON, nullable=True)
    merchandise_rights = Column(JSON, nullable=True)
    
    # Legal and contractual
    contract_terms = Column(JSON, nullable=True)
    exclusivity_terms = Column(JSON, nullable=True)
    territorial_rights = Column(JSON, nullable=True)
    duration_terms = Column(JSON, nullable=True)
    termination_clauses = Column(JSON, nullable=True)
    dispute_resolution = Column(JSON, nullable=True)
    
    # Platform and distribution
    target_platforms = Column(ARRAY(String), nullable=True)
    distribution_strategy = Column(JSON, nullable=True)
    marketing_plan = Column(JSON, nullable=True)
    promotion_responsibilities = Column(JSON, nullable=True)
    cross_promotion_terms = Column(JSON, nullable=True)
    
    # Communication and workflow
    communication_preferences = Column(JSON, nullable=True)
    preferred_tools = Column(ARRAY(String), nullable=True)
    file_sharing_setup = Column(JSON, nullable=True)
    review_process = Column(JSON, nullable=True)
    approval_workflow = Column(JSON, nullable=True)
    
    # Requirements and preferences
    skill_requirements = Column(JSON, nullable=True)
    experience_level = Column(String(50), nullable=True)
    portfolio_requirements = Column(JSON, nullable=True)
    reference_tracks = Column(JSON, nullable=True)
    style_references = Column(JSON, nullable=True)
    
    # AI matching and recommendations
    ai_compatibility_score = Column(Float, nullable=True)
    ai_match_reasons = Column(JSON, nullable=True)
    ai_success_prediction = Column(Float, nullable=True)
    recommendation_factors = Column(JSON, nullable=True)
    similarity_metrics = Column(JSON, nullable=True)
    
    # Response and negotiation
    response_message = Column(Text, nullable=True)
    counter_proposals = Column(JSON, nullable=True)
    negotiation_history = Column(JSON, nullable=True)
    terms_modifications = Column(JSON, nullable=True)
    final_agreement = Column(JSON, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    milestones_completed = Column(JSON, nullable=True)
    current_phase = Column(String(100), nullable=True)
    deliverable_status = Column(JSON, nullable=True)
    quality_checkpoints = Column(JSON, nullable=True)
    
    # File and asset management
    shared_files = Column(JSON, nullable=True)
    file_permissions = Column(JSON, nullable=True)
    version_control = Column(JSON, nullable=True)
    backup_locations = Column(JSON, nullable=True)
    asset_inventory = Column(JSON, nullable=True)
    
    # Performance metrics
    collaboration_rating = Column(Float, nullable=True)
    completion_time = Column(Float, nullable=True)  # Hours
    quality_score = Column(Float, nullable=True)
    satisfaction_scores = Column(JSON, nullable=True)
    feedback_ratings = Column(JSON, nullable=True)
    
    # Analytics and insights
    engagement_metrics = Column(JSON, nullable=True)
    performance_analytics = Column(JSON, nullable=True)
    success_indicators = Column(JSON, nullable=True)
    learning_outcomes = Column(JSON, nullable=True)
    improvement_suggestions = Column(JSON, nullable=True)
    
    # Risk assessment
    risk_level = Column(String(50), default="low")
    risk_factors = Column(JSON, nullable=True)
    mitigation_strategies = Column(JSON, nullable=True)
    contingency_plans = Column(JSON, nullable=True)
    insurance_requirements = Column(JSON, nullable=True)
    
    # Compliance and verification
    identity_verified = Column(Boolean, default=False)
    portfolio_verified = Column(Boolean, default=False)
    references_checked = Column(Boolean, default=False)
    background_check = Column(JSON, nullable=True)
    compliance_status = Column(String(50), default="pending")
    
    # Notification and alerts
    notification_settings = Column(JSON, nullable=True)
    reminder_schedule = Column(JSON, nullable=True)
    escalation_rules = Column(JSON, nullable=True)
    alert_thresholds = Column(JSON, nullable=True)
    stakeholder_updates = Column(JSON, nullable=True)
    
    # Integration and automation
    external_integrations = Column(JSON, nullable=True)
    automation_rules = Column(JSON, nullable=True)
    webhook_endpoints = Column(JSON, nullable=True)
    api_integrations = Column(JSON, nullable=True)
    sync_status = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_urgent = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    is_exclusive = Column(Boolean, default=False)
    requires_nda = Column(Boolean, default=False)
    allows_counter_offers = Column(Boolean, default=True)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_user_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    content = relationship("UserContent", foreign_keys=[content_id])
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_collaboration_requests_requester_status', 'requester_user_id', 'request_status'),
        Index('idx_collaboration_requests_target_type', 'target_user_id', 'collaboration_type'),
        Index('idx_collaboration_requests_content_collaboration', 'content_id', 'collaboration_type'),
        Index('idx_collaboration_requests_status_priority', 'request_status', 'priority'),
        Index('idx_collaboration_requests_created_deadline', 'created_at', 'deadline'),
        Index('idx_collaboration_requests_timeline', 'proposed_start_date', 'proposed_end_date'),
        Index('idx_collaboration_requests_genre_scope', 'content_genre', 'collaboration_scope'),
        Index('idx_collaboration_requests_ai_compatibility', 'ai_compatibility_score', 'ai_success_prediction'),
        Index('idx_collaboration_requests_revenue_type', 'revenue_share_type', 'currency'),
        Index('idx_collaboration_requests_verification', 'identity_verified', 'portfolio_verified'),
        Index('idx_collaboration_requests_public_featured', 'is_public', 'is_featured'),
        Index('idx_collaboration_requests_urgent_active', 'is_urgent', 'is_active'),
        Index('idx_collaboration_requests_expires', 'expires_at', 'request_status'),
    )
    
    def __repr__(self):
        return f"<CollaborationRequest(id={self.id}, request_number='{self.request_number}', type={self.collaboration_type.value}, status={self.request_status.value})>"
    
    def to_dict(self, include_sensitive: bool = False, include_analytics: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""        base_dict = {
            "id": str(self.id),
            "requester_user_id": str(self.requester_user_id),
            "target_user_id": str(self.target_user_id),
            "content_id": str(self.content_id) if self.content_id else None,
            "request_number": self.request_number,
            "request_title": self.request_title,
            "request_description": self.request_description,
            "external_reference": self.external_reference,
            "collaboration_type": self.collaboration_type.value if self.collaboration_type else None,
            "collaboration_scope": self.collaboration_scope.value if self.collaboration_scope else None,
            "request_status": self.request_status.value if self.request_status else None,
            "priority": self.priority.value if self.priority else None,
            "requester_name": self.requester_name,
            "target_name": self.target_name,
            "requester_profile": self.requester_profile,
            "target_skills": self.target_skills,
            "additional_collaborators": self.additional_collaborators,
            "collaborator_roles": self.collaborator_roles,
            "content_title": self.content_title,
            "content_genre": self.content_genre,
            "content_style": self.content_style,
            "content_mood": self.content_mood,
            "content_duration": self.content_duration,
            "content_requirements": self.content_requirements,
            "project_goals": self.project_goals,
            "creative_direction": self.creative_direction,
            "technical_requirements": self.technical_requirements,
            "quality_standards": self.quality_standards,
            "deliverables": self.deliverables,
            "proposed_start_date": self.proposed_start_date.isoformat() if self.proposed_start_date else None,
            "proposed_end_date": self.proposed_end_date.isoformat() if self.proposed_end_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "milestone_dates": self.milestone_dates,
            "time_zone": self.time_zone,
            "availability_windows": self.availability_windows,
            "time_constraints": self.time_constraints,
            "equipment_requirements": self.equipment_requirements,
            "location_preferences": self.location_preferences,
            "revenue_share_type": self.revenue_share_type.value if self.revenue_share_type else None,
            "revenue_splits": self.revenue_splits,
            "budget_range": self.budget_range,
            "payment_terms": self.payment_terms,
            "currency": self.currency,
            "copyright_split": self.copyright_split,
            "publishing_rights": self.publishing_rights,
            "target_platforms": self.target_platforms,
            "distribution_strategy": self.distribution_strategy,
            "marketing_plan": self.marketing_plan,
            "communication_preferences": self.communication_preferences,
            "preferred_tools": self.preferred_tools,
            "skill_requirements": self.skill_requirements,
            "experience_level": self.experience_level,
            "reference_tracks": self.reference_tracks,
            "style_references": self.style_references,
            "ai_compatibility_score": self.ai_compatibility_score,
            "ai_match_reasons": self.ai_match_reasons,
            "ai_success_prediction": self.ai_success_prediction,
            "response_message": self.response_message,
            "counter_proposals": self.counter_proposals,
            "progress_percentage": self.progress_percentage,
            "current_phase": self.current_phase,
            "deliverable_status": self.deliverable_status,
            "risk_level": self.risk_level,
            "identity_verified": self.identity_verified,
            "portfolio_verified": self.portfolio_verified,
            "references_checked": self.references_checked,
            "compliance_status": self.compliance_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "is_urgent": self.is_urgent,
            "is_featured": self.is_featured,
            "is_public": self.is_public,
            "is_exclusive": self.is_exclusive,
            "requires_nda": self.requires_nda,
            "allows_counter_offers": self.allows_counter_offers
        }
        
        if include_analytics:
            base_dict.update({
                "collaboration_rating": self.collaboration_rating,
                "completion_time": self.completion_time,
                "quality_score": self.quality_score,
                "satisfaction_scores": self.satisfaction_scores,
                "feedback_ratings": self.feedback_ratings,
                "engagement_metrics": self.engagement_metrics,
                "performance_analytics": self.performance_analytics,
                "success_indicators": self.success_indicators,
                "improvement_suggestions": self.improvement_suggestions
            })
        
        if include_sensitive:
            base_dict.update({
                "requester_email": self.requester_email,
                "target_email": self.target_email,
                "contract_terms": self.contract_terms,
                "final_agreement": self.final_agreement,
                "negotiation_history": self.negotiation_history,
                "background_check": self.background_check,
                "file_permissions": self.file_permissions,
                "shared_files": self.shared_files
            })
        
        return base_dict
    
    def is_expired(self) -> bool:
        """Check if request is expired"""        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) >= self.expires_at
    
    def is_pending_response(self) -> bool:
        """Check if request is waiting for response"""        return (
            self.request_status in [RequestStatus.SENT, RequestStatus.RECEIVED] and
            not self.is_expired() and
            self.is_active
        )
    
    def days_until_deadline(self) -> Optional[int]:
        """Calculate days until deadline"""        if not self.deadline:
            return None
        
        delta = self.deadline - datetime.now(timezone.utc)
        return max(delta.days, 0)
    
    def is_overdue(self) -> bool:
        """Check if request is overdue"""        if not self.deadline:
            return False
        return datetime.now(timezone.utc) > self.deadline
    
    def calculate_compatibility_score(self, target_user_data: Dict[str, Any]) -> float:
        """Calculate compatibility score with target user"""        score = 0.0
        factors = 0
        
        # Genre compatibility
        if self.content_genre and target_user_data.get('preferred_genres'):
            if self.content_genre in target_user_data['preferred_genres']:
                score += 20.0
            factors += 1
        
        # Skill matching
        if self.skill_requirements and target_user_data.get('skills'):
            required_skills = set(self.skill_requirements.get('required', []))
            user_skills = set(target_user_data['skills'])
            match_ratio = len(required_skills.intersection(user_skills)) / len(required_skills) if required_skills else 1.0
            score += match_ratio * 25.0
            factors += 1
        
        # Experience level
        if self.experience_level and target_user_data.get('experience_level'):
            experience_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            req_level = experience_levels.index(self.experience_level) if self.experience_level in experience_levels else 1
            user_level = experience_levels.index(target_user_data['experience_level']) if target_user_data['experience_level'] in experience_levels else 1
            level_diff = abs(req_level - user_level)
            score += max(0, 15.0 - (level_diff * 5.0))
            factors += 1
        
        # Availability overlap
        if self.availability_windows and target_user_data.get('availability'):
            # Simplified availability check
            score += 15.0  # Placeholder
            factors += 1
        
        # Portfolio quality
        if target_user_data.get('portfolio_score'):
            score += min(target_user_data['portfolio_score'] * 25.0, 25.0)
            factors += 1
        
        return score / max(factors, 1) if factors > 0 else 0.0
    
    def get_next_milestone(self) -> Optional[Dict[str, Any]]:
        """Get the next upcoming milestone"""        if not self.milestone_dates:
            return None
        
        now = datetime.now(timezone.utc)
        upcoming_milestones = [
            milestone for milestone in self.milestone_dates
            if datetime.fromisoformat(milestone.get('date', '')) > now
        ]
        
        if not upcoming_milestones:
            return None
        
        return min(upcoming_milestones, key=lambda m: datetime.fromisoformat(m.get('date', '')))
    
    def can_accept(self, user_id: str) -> bool:
        """Check if user can accept this request"""        return (
            str(self.target_user_id) == user_id and
            self.request_status in [RequestStatus.SENT, RequestStatus.RECEIVED] and
            not self.is_expired() and
            self.is_active
        )
    
    def can_modify(self, user_id: str) -> bool:
        """Check if user can modify this request"""        return (
            str(self.requester_user_id) == user_id and
            self.request_status in [RequestStatus.DRAFT, RequestStatus.PENDING, RequestStatus.NEGOTIATING] and
            self.is_active
        )
    
    @classmethod
    def create_request(cls, request_data: Dict[str, Any], requester_user_id: str) -> 'CollaborationRequest':
        """Create CollaborationRequest from request data"""        # Generate unique request number
        request_number = f"COLLAB-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        return cls(
            requester_user_id=requester_user_id,
            target_user_id=request_data.get('target_user_id'),
            content_id=request_data.get('content_id'),
            request_number=request_number,
            request_title=request_data.get('request_title'),
            request_description=request_data.get('request_description'),
            collaboration_type=CollaborationType(request_data.get('collaboration_type', 'co_creation')),
            collaboration_scope=CollaborationScope(request_data.get('collaboration_scope', 'single_track')),
            priority=Priority(request_data.get('priority', 'medium')),
            requester_name=request_data.get('requester_name'),
            target_name=request_data.get('target_name'),
            content_title=request_data.get('content_title'),
            content_genre=request_data.get('content_genre'),
            content_requirements=request_data.get('content_requirements', {}),
            project_goals=request_data.get('project_goals', {}),
            proposed_start_date=request_data.get('proposed_start_date'),
            proposed_end_date=request_data.get('proposed_end_date'),
            deadline=request_data.get('deadline'),
            revenue_share_type=RevenueShareType(request_data.get('revenue_share_type', 'equal_split')),
            revenue_splits=request_data.get('revenue_splits', {}),
            skill_requirements=request_data.get('skill_requirements', {}),
            experience_level=request_data.get('experience_level'),
            target_platforms=request_data.get('target_platforms', []),
            communication_preferences=request_data.get('communication_preferences', {}),
            is_urgent=request_data.get('is_urgent', False),
            is_public=request_data.get('is_public', False),
            allows_counter_offers=request_data.get('allows_counter_offers', True),
            expires_at=request_data.get('expires_at', datetime.now(timezone.utc) + timedelta(days=30))
        )
