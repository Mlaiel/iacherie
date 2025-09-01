"""Audio Collaboration Events - Industrial Grade Collaboration & Social Features
============================================================================

This module handles all events related to audio collaboration, remixing,
versioning, and social interaction features for creators and artists.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from ...core.events.base_event import BaseEvent, EventPriority, EventCategory


class CollaborationType(Enum):
    """
Types of collaboration"""

    REMIX = "remix"
    COVER = "cover"
    COLLABORATION = "collaboration"
    SAMPLE_USAGE = "sample_usage"
    MASHUP = "mashup"
    FEATURED_ARTIST = "featured_artist"
    PRODUCER_COLLABORATION = "producer_collaboration"
    SONGWRITER_COLLABORATION = "songwriter_collaboration"
    VOCAL_FEATURE = "vocal_feature"
    INSTRUMENTAL_FEATURE = "instrumental_feature"


class CollaborationStatus(Enum):
    """Status of collaboration requests"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEGOTIATING = "negotiating"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class RemixType(Enum):
    """Types of remixes"""

    OFFICIAL_REMIX = "official_remix"
    BOOTLEG_REMIX = "bootleg_remix"
    RADIO_EDIT = "radio_edit"
    EXTENDED_MIX = "extended_mix"
    INSTRUMENTAL = "instrumental"
    ACAPELLA = "acapella"
    DUB_MIX = "dub_mix"
    VIP_MIX = "vip_mix"
    FESTIVAL_MIX = "festival_mix"
    CLUB_MIX = "club_mix"


@dataclass
class AudioCollaborationRequestEvent(BaseEvent):
    """
    Event triggered when a collaboration request is initiated.
    
    Handles collaboration invitations between artists and creators.
    """
    requester_id: UUID
    target_artist_id: UUID
    original_file_id: UUID
    collaboration_id: UUID
    collaboration_type: CollaborationType
    request_message: str
    collaboration_terms: Dict[str, Any]
    revenue_split_proposal: Dict[UUID, float]  # artist_id -> percentage
    usage_rights: List[str]
    collaboration_scope: str
    deadline: Optional[datetime] = None
    reference_tracks: List[UUID] = field(default_factory=list)
    preferred_style: Optional[str] = None
    technical_requirements: Dict[str, Any] = field(default_factory=dict)
    collaboration_budget: Optional[float] = None
    exclusive_collaboration: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.request",
            event_category=EventCategory.COLLABORATION,
            priority=EventPriority.HIGH,
            user_id=self.requester_id,
            metadata={
                "collaboration_id": str(self.collaboration_id),
                "target_artist_id": str(self.target_artist_id),
                "original_file_id": str(self.original_file_id),
                "collaboration_type": self.collaboration_type.value,
                "revenue_split_count": len(self.revenue_split_proposal),
                "has_deadline": self.deadline is not None,
                "exclusive": self.exclusive_collaboration
            }
        )


@dataclass
class AudioCollaborationAcceptedEvent(BaseEvent):
    """
    Event triggered when a collaboration request is accepted.
    
    Initiates the collaborative workflow and resource allocation.
    """
    target_artist_id: UUID
    requester_id: UUID
    collaboration_id: UUID
    original_file_id: UUID
    collaboration_type: CollaborationType
    accepted_terms: Dict[str, Any]
    final_revenue_split: Dict[UUID, float]
    collaboration_workspace_id: UUID
    shared_resources: List[str]
    collaboration_timeline: Dict[str, datetime]
    communication_channel_id: str
    file_sharing_permissions: Dict[str, List[str]]
    version_control_enabled: bool = True
    real_time_collaboration: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.accepted",
            event_category=EventCategory.COLLABORATION,
            priority=EventPriority.HIGH,
            user_id=self.target_artist_id,
            metadata={
                "collaboration_id": str(self.collaboration_id),
                "requester_id": str(self.requester_id),
                "workspace_id": str(self.collaboration_workspace_id),
                "collaboration_type": self.collaboration_type.value,
                "participants_count": len(self.final_revenue_split),
                "real_time_enabled": self.real_time_collaboration
            }
        )


@dataclass
class AudioCollaborationRejectedEvent(BaseEvent):
    """
    Event triggered when a collaboration request is rejected.
    
    Handles rejection feedback and alternative suggestions.
    """
    target_artist_id: UUID
    requester_id: UUID
    collaboration_id: UUID
    original_file_id: UUID
    rejection_reason: str
    rejection_details: Dict[str, Any]
    alternative_suggestions: List[str]
    counter_proposal: Optional[Dict[str, Any]] = None
    feedback_to_requester: Optional[str] = None
    rejection_category: str = "not_interested"  # not_interested, terms_disagreement, rights_issues, etc.
    auto_rejection: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.rejected",
            event_category=EventCategory.COLLABORATION,
            priority=EventPriority.MEDIUM,
            user_id=self.target_artist_id,
            metadata={
                "collaboration_id": str(self.collaboration_id),
                "requester_id": str(self.requester_id),
                "rejection_category": self.rejection_category,
                "has_counter_proposal": self.counter_proposal is not None,
                "auto_rejection": self.auto_rejection,
                "suggestions_count": len(self.alternative_suggestions)
            }
        )


@dataclass
class AudioRemixCreatedEvent(BaseEvent):
    """
    Event triggered when a remix is created and completed.
    
    Contains comprehensive remix metadata and analysis.
    """
    creator_id: UUID
    original_file_id: UUID
    remix_file_id: UUID
    remix_id: UUID
    remix_type: RemixType
    original_artist_id: UUID
    remix_title: str
    remix_duration: float
    original_duration: float
    tempo_change: float
    key_change: str
    genre_fusion: List[str]
    elements_preserved: List[str]
    elements_modified: List[str]
    new_elements_added: List[str]
    remix_techniques: List[str]
    remix_quality_score: float
    originality_score: float
    commercial_viability: float
    collaboration_authorized: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.remix_created",
            event_category=EventCategory.CREATION,
            priority=EventPriority.HIGH,
            user_id=self.creator_id,
            metadata={
                "remix_id": str(self.remix_id),
                "original_file_id": str(self.original_file_id),
                "remix_file_id": str(self.remix_file_id),
                "remix_type": self.remix_type.value,
                "tempo_change": self.tempo_change,
                "originality_score": self.originality_score,
                "authorized": self.collaboration_authorized
            }
        )


@dataclass
class AudioVersionCreatedEvent(BaseEvent):
    """
    Event triggered when a new version of a collaborative work is created.
    
    Handles version control and collaborative editing workflows.
    """
    creator_id: UUID
    collaboration_id: UUID
    original_file_id: UUID
    version_file_id: UUID
    version_id: UUID
    version_number: str
    version_type: str  # draft, revision, final, alternative
    changes_made: List[str]
    version_notes: str
    collaboration_stage: str
    contributors: List[UUID]
    approval_required: bool
    approval_status: str = "pending"
    merge_conflicts: List[str] = field(default_factory=list)
    diff_summary: Dict[str, Any] = field(default_factory=dict)
    rollback_available: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.version_created",
            event_category=EventCategory.VERSION_CONTROL,
            priority=EventPriority.MEDIUM,
            user_id=self.creator_id,
            metadata={
                "collaboration_id": str(self.collaboration_id),
                "version_id": str(self.version_id),
                "version_number": self.version_number,
                "version_type": self.version_type,
                "contributors_count": len(self.contributors),
                "has_conflicts": len(self.merge_conflicts) > 0,
                "approval_required": self.approval_required
            }
        )


@dataclass
class AudioCollaborationFeedbackEvent(BaseEvent):
    """
    Event triggered when feedback is provided on collaborative work.
    
    Handles peer review and feedback workflows.
    """
    reviewer_id: UUID
    collaboration_id: UUID
    version_id: UUID
    feedback_id: UUID
    feedback_type: str  # review, suggestion, approval, rejection
    feedback_content: str
    feedback_timestamp_markers: List[Tuple[float, str]]  # (time, comment)
    rating: Optional[float] = None
    suggested_changes: List[Dict[str, Any]] = field(default_factory=list)
    technical_feedback: Dict[str, Any] = field(default_factory=dict)
    creative_feedback: Dict[str, Any] = field(default_factory=dict)
    approval_status: Optional[str] = None
    priority_level: int = 1
    actionable_items: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.feedback",
            event_category=EventCategory.REVIEW,
            priority=EventPriority.MEDIUM,
            user_id=self.reviewer_id,
            metadata={
                "collaboration_id": str(self.collaboration_id),
                "version_id": str(self.version_id),
                "feedback_id": str(self.feedback_id),
                "feedback_type": self.feedback_type,
                "has_rating": self.rating is not None,
                "suggestions_count": len(self.suggested_changes),
                "actionable_items_count": len(self.actionable_items)
            }
        )


@dataclass
class AudioCollaborationMilestoneEvent(BaseEvent):
    """
    Event triggered when a collaboration milestone is reached.
    
    Tracks progress and completion of collaborative projects.
    """
    collaboration_id: UUID
    milestone_id: UUID
    milestone_name: str
    milestone_type: str  # checkpoint, deadline, completion, approval
    achieved_by: UUID
    achievement_date: datetime
    milestone_criteria: Dict[str, Any]
    completion_percentage: float
    next_milestone: Optional[str] = None
    deliverables_completed: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    collaboration_health: float = 1.0
    timeline_status: str = "on_track"  # ahead, on_track, delayed, critical
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.milestone",
            event_category=EventCategory.PROJECT_MANAGEMENT,
            priority=EventPriority.MEDIUM,
            user_id=self.achieved_by,
            metadata={
                "collaboration_id": str(self.collaboration_id),
                "milestone_id": str(self.milestone_id),
                "milestone_type": self.milestone_type,
                "completion_percentage": self.completion_percentage,
                "timeline_status": self.timeline_status,
                "deliverables_count": len(self.deliverables_completed)
            }
        )


@dataclass
class AudioCollaborationCompletedEvent(BaseEvent):
    """
    Event triggered when a collaboration is fully completed.
    
    Finalizes collaborative work and initiates distribution/monetization.
    """
    collaboration_id: UUID
    final_file_id: UUID
    final_version_id: UUID
    participants: List[UUID]
    completion_date: datetime
    project_duration: float  # days
    final_revenue_split: Dict[UUID, float]
    final_credits: Dict[UUID, List[str]]  # user_id -> roles
    quality_score: float
    commercial_readiness: float
    distribution_approved: bool
    copyright_cleared: bool
    master_recording_owner: UUID
    publishing_rights: Dict[UUID, float]
    collaboration_success_score: float
    lessons_learned: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.completed",
            event_category=EventCategory.COMPLETION,
            priority=EventPriority.HIGH,
            metadata={
                "collaboration_id": str(self.collaboration_id),
                "final_file_id": str(self.final_file_id),
                "participants_count": len(self.participants),
                "project_duration_days": self.project_duration,
                "quality_score": self.quality_score,
                "success_score": self.collaboration_success_score,
                "distribution_ready": self.distribution_approved and self.copyright_cleared
            }
        )


@dataclass
class AudioSampleUsageEvent(BaseEvent):
    """
    Event triggered when an audio sample is used in a new creation.
    
    Handles sample clearance and usage tracking.
    """
    user_id: UUID
    original_file_id: UUID
    new_file_id: UUID
    sample_id: UUID
    sample_start_time: float
    sample_end_time: float
    sample_duration: float
    sample_usage_type: str  # loop, one_shot, chop, stretch, pitch_shift
    original_owner_id: UUID
    clearance_status: str  # cleared, pending, rejected, not_required
    usage_fee: Optional[float] = None
    royalty_percentage: Optional[float] = None
    sample_transformation: Dict[str, Any] = field(default_factory=dict)
    recognition_probability: float = 1.0
    fair_use_assessment: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.sample_usage",
            event_category=EventCategory.SAMPLING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "sample_id": str(self.sample_id),
                "original_file_id": str(self.original_file_id),
                "new_file_id": str(self.new_file_id),
                "sample_duration": self.sample_duration,
                "clearance_status": self.clearance_status,
                "recognition_probability": self.recognition_probability,
                "usage_type": self.sample_usage_type
            }
        )
