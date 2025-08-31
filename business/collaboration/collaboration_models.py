"""
Advanced Collaboration Models for IA Influencer Agent
Professional collaboration business logic models

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import uuid


class CollaborationType(Enum):
    """Types of collaboration available in the platform"""
    MUSIC_COLLABORATION = "music_collaboration"
    CONTENT_CREATION = "content_creation"
    BRAND_PARTNERSHIP = "brand_partnership"
    CROSS_PROMOTION = "cross_promotion"
    SKILL_EXCHANGE = "skill_exchange"
    JOINT_PRODUCTION = "joint_production"
    MENTORSHIP = "mentorship"
    EVENT_COLLABORATION = "event_collaboration"


class CollaborationStatus(Enum):
    """Status tracking for collaboration requests"""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SkillLevel(Enum):
    """Skill proficiency levels for matching"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class CollaborationSkill:
    """Represents a skill for collaboration matching"""
    name: str
    level: SkillLevel
    category: str
    experience_years: int = 0
    certifications: List[str] = field(default_factory=list)
    portfolio_items: List[str] = field(default_factory=list)
    
    def compatibility_score(self, other: 'CollaborationSkill') -> float:
        """Calculate compatibility score with another skill"""
        if self.name != other.name:
            return 0.0
            
        level_scores = {
            SkillLevel.BEGINNER: 1,
            SkillLevel.INTERMEDIATE: 2,
            SkillLevel.ADVANCED: 3,
            SkillLevel.EXPERT: 4,
            SkillLevel.MASTER: 5
        }
        
        self_score = level_scores[self.level]
        other_score = level_scores[other.level]
        
        # Perfect complement: beginner with expert, etc.
        if abs(self_score - other_score) >= 2:
            return 0.9
        elif abs(self_score - other_score) == 1:
            return 0.7
        else:
            return 0.5


class CollaborationRequest(BaseModel):
    """Professional collaboration request model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    collaboration_type: CollaborationType
    status: CollaborationStatus = CollaborationStatus.DRAFT
    
    # Creator information
    creator_id: str
    creator_profile: Dict[str, Any] = Field(default_factory=dict)
    
    # Requirements
    required_skills: List[CollaborationSkill] = Field(default_factory=list)
    offered_skills: List[CollaborationSkill] = Field(default_factory=list)
    budget_range: Optional[Dict[str, float]] = None
    timeline: Optional[Dict[str, datetime]] = None
    
    # Preferences
    preferred_locations: List[str] = Field(default_factory=list)
    remote_work_allowed: bool = True
    language_requirements: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    
    # Matching data
    match_score_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    max_participants: int = Field(default=2, ge=2, le=10)
    current_participants: List[str] = Field(default_factory=list)
    
    @validator('budget_range')
    def validate_budget(cls, v):
        if v and ('min' in v and 'max' in v):
            if v['min'] > v['max']:
                raise ValueError("Minimum budget cannot exceed maximum")
        return v
    
    @validator('timeline')
    def validate_timeline(cls, v):
        if v and ('start' in v and 'end' in v):
            if v['start'] >= v['end']:
                raise ValueError("Start date must be before end date")
        return v
    
    def is_expired(self) -> bool:
        """Check if collaboration request has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def can_accept_participant(self) -> bool:
        """Check if more participants can be accepted"""



        return len(self.current_participants) < self.max_participants
    
    def calculate_compatibility_score(self, other_profile: Dict[str, Any]) -> float:
        """Calculate compatibility score with another creator profile"""
        if not other_profile.get('skills'):
            return 0.0
            
        total_score = 0.0
        skill_matches = 0
        
        other_skills = [CollaborationSkill(**skill) for skill in other_profile['skills']]
        
        for required_skill in self.required_skills:
            for other_skill in other_skills:
                score = required_skill.compatibility_score(other_skill)
                if score > 0:
                    total_score += score
                    skill_matches += 1
        
        if skill_matches == 0:
            return 0.0
            
        return min(total_score / skill_matches, 1.0)


@dataclass
class CollaborationMatch:
    """Represents a potential collaboration match"""
    request_id: str
    matched_creator_id: str
    compatibility_score: float
    skill_matches: List[Dict[str, Any]]
    location_match: bool
    language_match: bool
    budget_compatible: bool
    timeline_compatible: bool
    
    # Enhanced matching factors
    reputation_score: float = 0.0
    portfolio_relevance: float = 0.0
    communication_style_match: float = 0.0
    work_availability_match: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority_score: float = field(init=False)
    
    def __post_init__(self):
        """Calculate overall priority score"""
        base_score = self.compatibility_score * 0.4
        reputation_weight = self.reputation_score * 0.2
        portfolio_weight = self.portfolio_relevance * 0.2
        communication_weight = self.communication_style_match * 0.1
        availability_weight = self.work_availability_match * 0.1
        
        self.priority_score = (
            base_score + reputation_weight + portfolio_weight + 
            communication_weight + availability_weight
        )
        
        # Bonus for perfect matches
        if (self.location_match and self.language_match and 
            self.budget_compatible and self.timeline_compatible):
            self.priority_score *= 1.1
            
        self.priority_score = min(self.priority_score, 1.0)
    
    def is_high_quality_match(self) -> bool:
        """Determine if this is a high-quality match"""



        return (
            self.compatibility_score >= 0.7 and
            self.reputation_score >= 0.6 and
            self.priority_score >= 0.75
        )


class CollaborationContract(BaseModel):
    """Professional collaboration contract model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collaboration_request_id: str
    participants: List[str] = Field(min_items=2, max_items=10)
    
    # Contract terms
    title: str
    description: str
    deliverables: List[Dict[str, Any]] = Field(default_factory=list)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Financial terms
    total_budget: Optional[float] = None
    payment_terms: Dict[str, Any] = Field(default_factory=dict)
    revenue_sharing: Dict[str, float] = Field(default_factory=dict)
    
    # Timeline
    start_date: datetime
    end_date: datetime
    deadline_extensions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Legal and rights
    intellectual_property_terms: Dict[str, Any] = Field(default_factory=dict)
    usage_rights: Dict[str, Any] = Field(default_factory=dict)
    confidentiality_terms: Dict[str, Any] = Field(default_factory=dict)
    
    # Status tracking
    status: CollaborationStatus = CollaborationStatus.ACTIVE
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Signatures and approvals
    signatures: Dict[str, datetime] = Field(default_factory=dict)
    approved_by_all: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_fully_signed(self) -> bool:
        """Check if all participants have signed"""



        return len(self.signatures) == len(self.participants)
    
    def get_participant_share(self, participant_id: str) -> float:
        """Get revenue share percentage for participant"""



        return self.revenue_sharing.get(participant_id, 0.0)
    
    def calculate_estimated_completion_date(self) -> datetime:
        """Calculate estimated completion based on current progress"""
        if self.completion_percentage == 0:
            return self.end_date
            
        elapsed_time = datetime.utcnow() - self.start_date
        total_estimated_time = elapsed_time / (self.completion_percentage / 100)
        
        return self.start_date + total_estimated_time


@dataclass
class CollaborationAnalytics:
    """Analytics data for collaboration performance"""
    collaboration_id: str
    
    # Performance metrics
    response_rate: float = 0.0
    completion_rate: float = 0.0
    satisfaction_score: float = 0.0
    quality_score: float = 0.0
    
    # Engagement metrics
    messages_exchanged: int = 0
    meetings_held: int = 0
    files_shared: int = 0
    revisions_count: int = 0
    
    # Time metrics
    average_response_time: float = 0.0  # hours
    project_duration: float = 0.0  # days
    time_to_completion: float = 0.0  # days
    
    # Financial metrics
    budget_utilization: float = 0.0
    cost_per_deliverable: float = 0.0
    roi_percentage: float = 0.0
    
    # Quality indicators
    revision_ratio: float = 0.0
    client_feedback_score: float = 0.0
    repeat_collaboration_rate: float = 0.0
    
    # Timestamps
    measured_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_overall_success_score(self) -> float:
        """Calculate overall collaboration success score"""
        weights = {
            'completion_rate': 0.25,
            'satisfaction_score': 0.20,
            'quality_score': 0.20,
            'budget_utilization': 0.15,
            'client_feedback_score': 0.10,
            'roi_percentage': 0.10
        }
        
        score = 0.0
        for metric, weight in weights.items():
            value = getattr(self, metric, 0.0)
            # Normalize ROI to 0-1 scale (assume 100% ROI = 1.0)
            if metric == 'roi_percentage':
                value = min(value / 100, 1.0)
            score += value * weight
            
        return min(score, 1.0)


class CollaborationNotification(BaseModel):
    """Notification system for collaboration events"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_id: str
    collaboration_id: str
    
    # Notification content
    title: str
    message: str
    notification_type: str
    priority: str = Field(default="normal")  # low, normal, high, urgent
    
    # Delivery options
    channels: List[str] = Field(default=["in_app"])  # in_app, email, sms, push
    
    # Status
    sent: bool = False
    delivered: bool = False
    read: bool = False
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.sent = True
        self.sent_at = datetime.utcnow()
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read = True
        self.read_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if notification has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


# Export all models
__all__ = [
    'CollaborationType',
    'CollaborationStatus', 
    'SkillLevel',
    'CollaborationSkill',
    'CollaborationRequest',
    'CollaborationMatch',
    'CollaborationContract',
    'CollaborationAnalytics',
    'CollaborationNotification'
]
