"""Content Collaboration Module - Advanced Multi-Creator Collaboration System

Module gérant la collaboration entre créateurs, les projets partagés et 
la distribution des revenus pour les contenus collaboratifs.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Collaboration Expert, Project Management Specialist, Revenue Distribution Expert
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json
import asyncio
import logging
from decimal import Decimal

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Float, JSON, Text,
    ForeignKey, Table, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

logger = logging.getLogger(__name__)
Base = declarative_base()

class CollaborationType(Enum):
    """
Types of collaboration between creators"""

    REMIX = "remix"
    FEATURE = "feature"
    DUET = "duet"
    COVER = "cover"
    MASHUP = "mashup"
    SPLIT_TRACK = "split_track"
    JOINT_PROJECT = "joint_project"
    SAMPLE_USE = "sample_use"
    PRODUCER_ARTIST = "producer_artist"
    GUEST_APPEARANCE = "guest_appearance"
    CO_WRITING = "co_writing"
    REMIX_COMPETITION = "remix_competition"

class CollaborationStatus(Enum):
    """Status of collaboration projects"""

    PROPOSED = "proposed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    DISPUTE = "dispute"

class RoleType(Enum):
    """Roles in collaborative projects"""

    INITIATOR = "initiator"
    COLLABORATOR = "collaborator"
    PRODUCER = "producer"
    ARTIST = "artist"
    SONGWRITER = "songwriter"
    VOCALIST = "vocalist"
    INSTRUMENTALIST = "instrumentalist"
    MIXER = "mixer"
    MASTERING_ENGINEER = "mastering_engineer"
    CONTRIBUTOR = "contributor"
    GUEST = "guest"
    REVIEWER = "reviewer"

class RevenueShareType(Enum):
    """Types of revenue sharing models"""

    EQUAL_SPLIT = "equal_split"
    PERCENTAGE_BASED = "percentage_based"
    PERFORMANCE_BASED = "performance_based"
    CONTRIBUTION_WEIGHTED = "contribution_weighted"
    CUSTOM = "custom"
    BUYOUT = "buyout"
    ROYALTY_FREE = "royalty_free"

class ContributionType(Enum):
    """Types of contributions to collaborative content"""

    COMPOSITION = "composition"
    LYRICS = "lyrics"
    VOCAL_PERFORMANCE = "vocal_performance"
    INSTRUMENTAL = "instrumental"
    PRODUCTION = "production"
    MIXING = "mixing"
    MASTERING = "mastering"
    CONCEPT = "concept"
    ARTWORK = "artwork"
    PROMOTION = "promotion"
    FUNDING = "funding"

# Association table for collaboration participants
collaboration_participants = Table(
    'collaboration_participants',
    Base.metadata,
    Column('collaboration_id', UUID(as_uuid=True), ForeignKey('collaborations.id')),
    Column('user_id', UUID(as_uuid=True), nullable=False),
    Column('role', String(50), nullable=False),
    Column('revenue_share_percentage', Float, default=0.0),
    Column('contribution_weight', Float, default=1.0),
    Column('joined_at', DateTime(timezone=True), default=datetime.utcnow),
    Column('status', String(20), default='active')
)

class Collaboration(Base):
    """Collaboration project database model"""
    __tablename__ = "collaborations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Project information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    collaboration_type = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False, default=CollaborationStatus.PROPOSED.value)
    
    # Content references
    source_content_id = Column(UUID(as_uuid=True), nullable=True)  # Original content if remix/cover
    result_content_id = Column(UUID(as_uuid=True), nullable=True)  # Final collaborative content
    
    # Initiator and management
    initiator_id = Column(UUID(as_uuid=True), nullable=False)
    project_manager_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timeline
    proposed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    deadline = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Revenue and rights
    revenue_share_model = Column(String(30), nullable=False, default=RevenueShareType.EQUAL_SPLIT.value)
    revenue_shares = Column(JSONB, default={})  # Detailed revenue distribution
    copyright_split = Column(JSONB, default={})  # Copyright ownership split
    publishing_split = Column(JSONB, default={})  # Publishing rights split
    
    # Contract and legal
    contract_terms = Column(JSONB, default={})
    requires_approval = Column(Boolean, default=True)
    is_exclusive = Column(Boolean, default=False)
    geographic_restrictions = Column(ARRAY(String), default=[])
    
    # Collaboration settings
    allows_public_preview = Column(Boolean, default=False)
    allows_feedback = Column(Boolean, default=True)
    max_participants = Column(Integer, default=10)
    
    # Metadata
    tags = Column(ARRAY(String), default=[])
    genre = Column(String(100), nullable=True)
    language = Column(String(10), nullable=True)
    target_platforms = Column(ARRAY(String), default=[])
    
    # Quality and moderation
    quality_requirements = Column(JSONB, default={})
    moderation_status = Column(String(20), default='pending')
    is_featured = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("CollaborationVersion", back_populates="collaboration")
    comments = relationship("CollaborationComment", back_populates="collaboration")
    files = relationship("CollaborationFile", back_populates="collaboration")

class CollaborationVersion(Base):
    """Versioning system for collaborative content"""
    __tablename__ = "collaboration_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('collaborations.id'), nullable=False)
    
    version_number = Column(String(20), nullable=False)  # e.g., "1.0", "1.1", "2.0"
    version_name = Column(String(100), nullable=True)  # e.g., "Final Mix", "Demo Version"
    
    # Version content
    content_file_id = Column(UUID(as_uuid=True), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    # Version metadata
    created_by = Column(UUID(as_uuid=True), nullable=False)
    changes_description = Column(Text)
    is_current = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    approval_count = Column(Integer, default=0)
    required_approvals = Column(Integer, default=1)
    
    # Quality metrics
    audio_quality_score = Column(Float, nullable=True)
    mix_quality_score = Column(Float, nullable=True)
    mastering_quality_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    collaboration = relationship("Collaboration", back_populates="versions")
    approvals = relationship("VersionApproval", back_populates="version")

class VersionApproval(Base):
    """Approval tracking for collaboration versions"""
    __tablename__ = "version_approvals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_versions.id'), nullable=False)
    
    approved_by = Column(UUID(as_uuid=True), nullable=False)
    approval_status = Column(String(20), nullable=False)  # approved, rejected, pending
    feedback = Column(Text, nullable=True)
    
    approved_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    version = relationship("CollaborationVersion", back_populates="approvals")

class CollaborationComment(Base):
    """Comments and feedback system for collaborations"""
    __tablename__ = "collaboration_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('collaborations.id'), nullable=False)
    
    # Comment content
    author_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)
    comment_type = Column(String(30), default='general')  # general, feedback, suggestion, approval
    
    # Threading
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_comments.id'), nullable=True)
    thread_depth = Column(Integer, default=0)
    
    # Timing and context
    timestamp_reference = Column(Float, nullable=True)  # For audio/video timestamp comments
    version_reference = Column(String(20), nullable=True)
    
    # Moderation
    is_resolved = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    priority = Column(String(10), default='normal')  # low, normal, high, critical
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    collaboration = relationship("Collaboration", back_populates="comments")
    replies = relationship("CollaborationComment", backref=backref('parent', remote_side=[id]))

class CollaborationFile(Base):
    """File management for collaborative projects"""
    __tablename__ = "collaboration_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('collaborations.id'), nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(100), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=False)
    
    # File metadata
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)
    file_category = Column(String(50), nullable=False)  # source, working, final, reference
    description = Column(Text, nullable=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(30), default='pending')
    
    # Access control
    is_public = Column(Boolean, default=False)
    access_level = Column(String(20), default='collaborators')  # all, collaborators, specific
    allowed_users = Column(ARRAY(String), default=[])
    
    # Version tracking
    version = Column(String(20), default='1.0')
    replaces_file_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_files.id'), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    collaboration = relationship("Collaboration", back_populates="files")

@dataclass 
class ContributionRecord:
    """Record of individual contributor contributions"""
    contributor_id: str
    contribution_type: ContributionType
    contribution_weight: float
    timestamp: datetime
    description: Optional[str] = None
    file_references: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    peer_ratings: List[float] = field(default_factory=list)

class CollaborationManager:
    """
Manager class for collaboration operations"""
    
    def __init__(self):
        self.active_collaborations = {}
        self.pending_invitations = {}
    
    async def create_collaboration(
        self,
        initiator_id: str,
        collaboration_data: Dict[str, Any]
    ) -> str:
        """
Create a new collaboration project"""
        try:
            collaboration_id = str(uuid.uuid4())
            
            # Validate collaboration data
            self._validate_collaboration_data(collaboration_data)
            
            # Create collaboration record
            collaboration = Collaboration(
                id=collaboration_id,
                initiator_id=initiator_id,
                **collaboration_data
            )
            
            # Initialize revenue sharing
            if collaboration_data.get('participants'):
                revenue_shares = self._calculate_initial_revenue_shares(
                    collaboration_data['participants'],
                    collaboration_data.get('revenue_share_model', RevenueShareType.EQUAL_SPLIT)
                )
                collaboration.revenue_shares = revenue_shares
            
            logger.info(f"Created collaboration {collaboration_id}")
            return collaboration_id
            
        except Exception as e:
            logger.error(f"Error creating collaboration: {e}")
            raise
    
    async def invite_collaborator(
        self,
        collaboration_id: str,
        inviter_id: str,
        invitee_id: str,
        role: RoleType,
        message: Optional[str] = None
    ) -> bool:
        """Invite a user to join a collaboration"""
        try:
            invitation_data = {
                'collaboration_id': collaboration_id,
                'inviter_id': inviter_id,
                'invitee_id': invitee_id,
                'role': role.value,
                'message': message,
                'invited_at': datetime.utcnow(),
                'status': 'pending'
            }
            
            invitation_key = f"{collaboration_id}_{invitee_id}"
            self.pending_invitations[invitation_key] = invitation_data
            
            # Send notification (implementation would integrate with notification system)
            await self._send_invitation_notification(invitation_data)
            
            logger.info(f"Sent collaboration invitation: {invitation_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending collaboration invitation: {e}")
            return False
    
    async def accept_invitation(
        self,
        collaboration_id: str,
        invitee_id: str,
        acceptance_terms: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Accept a collaboration invitation"""
        try:
            invitation_key = f"{collaboration_id}_{invitee_id}"
            
            if invitation_key not in self.pending_invitations:
                raise ValueError("Invitation not found or expired")
            
            invitation = self.pending_invitations[invitation_key]
            
            # Add user to collaboration
            await self._add_participant_to_collaboration(
                collaboration_id,
                invitee_id,
                invitation['role'],
                acceptance_terms
            )
            
            # Update invitation status
            invitation['status'] = 'accepted'
            invitation['accepted_at'] = datetime.utcnow()
            
            # Remove from pending
            del self.pending_invitations[invitation_key]
            
            logger.info(f"Collaboration invitation accepted: {invitation_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error accepting collaboration invitation: {e}")
            return False
    
    async def submit_contribution(
        self,
        collaboration_id: str,
        contributor_id: str,
        contribution: ContributionRecord
    ) -> str:
        """Submit a contribution to a collaboration"""
        try:
            contribution_id = str(uuid.uuid4())
            
            # Validate contribution
            self._validate_contribution(contribution)
            
            # Process contribution files if any
            if contribution.file_references:
                processed_files = await self._process_contribution_files(
                    collaboration_id,
                    contribution.file_references
                )
                contribution.file_references = processed_files
            
            # Calculate contribution weight based on type and quality
            contribution.contribution_weight = await self._calculate_contribution_weight(
                contribution
            )
            
            # Store contribution record
            # Implementation would store in database
            
            # Update collaboration status if needed
            await self._update_collaboration_progress(collaboration_id)
            
            logger.info(f"Contribution submitted: {contribution_id}")
            return contribution_id
            
        except Exception as e:
            logger.error(f"Error submitting contribution: {e}")
            raise
    
    async def calculate_revenue_distribution(
        self,
        collaboration_id: str,
        total_revenue: Decimal,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Decimal]:
        """Calculate revenue distribution among collaborators"""
        try:
            # Get collaboration details
            collaboration = await self._get_collaboration(collaboration_id)
            
            # Get contribution records for the period
            contributions = await self._get_contributions_for_period(
                collaboration_id, period_start, period_end
            )
            
            # Calculate distribution based on revenue share model
            distribution = {}
            
            if collaboration.revenue_share_model == RevenueShareType.EQUAL_SPLIT.value:
                participant_count = len(collaboration.revenue_shares)
                per_participant = total_revenue / participant_count
                distribution = {
                    user_id: per_participant 
                    for user_id in collaboration.revenue_shares.keys()
                }
            
            elif collaboration.revenue_share_model == RevenueShareType.PERCENTAGE_BASED.value:
                for user_id, percentage in collaboration.revenue_shares.items():
                    distribution[user_id] = total_revenue * (Decimal(percentage) / 100)
            
            elif collaboration.revenue_share_model == RevenueShareType.CONTRIBUTION_WEIGHTED.value:
                total_weight = sum(
                    contrib.contribution_weight 
                    for contrib in contributions
                )
                
                for user_id in collaboration.revenue_shares.keys():
                    user_contributions = [
                        c for c in contributions 
                        if c.contributor_id == user_id
                    ]
                    user_weight = sum(c.contribution_weight for c in user_contributions)
                    distribution[user_id] = total_revenue * (user_weight / total_weight)
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating revenue distribution: {e}")
            raise
    
    def _validate_collaboration_data(self, data: Dict[str, Any]):
        """Validate collaboration creation data"""
        required_fields = ['title', 'collaboration_type']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if data['collaboration_type'] not in [ct.value for ct in CollaborationType]:
            raise ValueError("Invalid collaboration type")
    
    def _validate_contribution(self, contribution: ContributionRecord):
        """Validate contribution data"""
        if not contribution.contributor_id:
            raise ValueError("Contributor ID is required")
        
        if contribution.contribution_weight < 0 or contribution.contribution_weight > 1:
            raise ValueError("Contribution weight must be between 0 and 1")
    
    def _calculate_initial_revenue_shares(
        self,
        participants: List[Dict[str, Any]],
        share_model: RevenueShareType
    ) -> Dict[str, float]:
        """Calculate initial revenue sharing percentages"""
        if share_model == RevenueShareType.EQUAL_SPLIT:
            share_per_participant = 100.0 / len(participants)
            return {
                participant['user_id']: share_per_participant
                for participant in participants
            }
        else:
            # For other models, use provided percentages or defaults
            return {
                participant['user_id']: participant.get('revenue_share', 0.0)
                for participant in participants
            }
    
    async def _calculate_contribution_weight(
        self,
        contribution: ContributionRecord
    ) -> float:
        """
Calculate weighted contribution value"""
        base_weights = {
            ContributionType.COMPOSITION: 0.3,
            ContributionType.LYRICS: 0.2,
            ContributionType.VOCAL_PERFORMANCE: 0.25,
            ContributionType.PRODUCTION: 0.2,
            ContributionType.MIXING: 0.15,
            ContributionType.MASTERING: 0.1,
            ContributionType.INSTRUMENTAL: 0.2,
            ContributionType.CONCEPT: 0.1,
            ContributionType.ARTWORK: 0.05,
            ContributionType.PROMOTION: 0.05
        }
        
        base_weight = base_weights.get(contribution.contribution_type, 0.1)
        
        # Adjust based on quality score
        quality_multiplier = 1.0
        if contribution.quality_score:
            quality_multiplier = 0.5 + (contribution.quality_score / 10.0)
        
        # Adjust based on peer ratings
        peer_multiplier = 1.0
        if contribution.peer_ratings:
            avg_rating = sum(contribution.peer_ratings) / len(contribution.peer_ratings)
            peer_multiplier = 0.5 + (avg_rating / 10.0)
        
        return base_weight * quality_multiplier * peer_multiplier
    
    async def _send_invitation_notification(self, invitation_data: Dict[str, Any]):
        """
Send invitation notification to invitee"""
        # Implementation would integrate with notification system
        pass
    
    async def _add_participant_to_collaboration(
        self,
        collaboration_id: str,
        user_id: str,
        role: str,
        terms: Optional[Dict[str, Any]]
    ):
        """
Add participant to collaboration"""
        # Implementation would update database
        pass
    
    async def _process_contribution_files(
        self,
        collaboration_id: str,
        file_references: List[str]
    ) -> List[str]:
        """
Process and validate contribution files"""
        # Implementation would handle file processing
        return file_references
    
    async def _update_collaboration_progress(self, collaboration_id: str):
        """
Update collaboration progress based on contributions"""
        # Implementation would update collaboration status
        pass
    
    async def _get_collaboration(self, collaboration_id: str):
        """
Get collaboration details from database"""
        # Implementation would query database
        pass
    
    async def _get_contributions_for_period(
        self,
        collaboration_id: str,
        start: datetime,
        end: datetime
    ) -> List[ContributionRecord]:
        """
Get contributions for a specific period"""
        # Implementation would query contribution records
        return []

# Export classes and functions
__all__ = [
    'CollaborationType',
    'CollaborationStatus', 
    'RoleType',
    'RevenueShareType',
    'ContributionType',
    'Collaboration',
    'CollaborationVersion',
    'VersionApproval',
    'CollaborationComment',
    'CollaborationFile',
    'ContributionRecord',
    'CollaborationManager'
]
