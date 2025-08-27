"""
IA Influencer Agent Platform - Collaboration Models
Advanced collaboration and partnership management system

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, Numeric,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .base import (
    BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin,
    AuditMixin, MetadataMixin, StatusMixin
)


class Collaboration(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin):
    """Core collaboration management between creators"""
    
    __tablename__ = 'collaborations'
    
    # Primary Collaborators
    initiator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    collaborator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Collaboration Details
    collaboration_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # music_collab, content_creation, brand_partnership, cross_promotion
    
    collaboration_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Content and Scope
    content_types: Mapped[List[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=False
    )  # music, video, photography, blog, social
    
    collaboration_scope: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # single_project, ongoing, campaign, tour
    
    expected_deliverables: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Timeline and Scheduling
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Revenue and Rights
    revenue_split_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )  # Percentage for collaborator (0-100)
    
    rights_distribution: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Detailed rights split
    
    # Collaboration Preferences
    communication_frequency: Mapped[str] = mapped_column(
        String(20),
        default='weekly',
        nullable=False
    )  # daily, weekly, biweekly, monthly
    
    preferred_platforms: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )
    
    # Quality and Requirements
    quality_standards: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    technical_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Performance Metrics
    total_content_created: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    total_revenue_generated: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    average_performance_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Relationships
    requests: Mapped[List["CollaborationRequest"]] = relationship(
        "CollaborationRequest",
        back_populates="collaboration",
        cascade="all, delete-orphan"
    )
    
    agreement: Mapped[Optional["CollaborationAgreement"]] = relationship(
        "CollaborationAgreement",
        back_populates="collaboration",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    revenue_records: Mapped[List["CollaborationRevenue"]] = relationship(
        "CollaborationRevenue",
        back_populates="collaboration",
        cascade="all, delete-orphan"
    )
    
    messages: Mapped[List["CollaborationMessage"]] = relationship(
        "CollaborationMessage",
        back_populates="collaboration",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_collaborations_initiator_collaborator', 'initiator_id', 'collaborator_id'),
        Index('idx_collaborations_type_status', 'collaboration_type', 'status'),
        Index('idx_collaborations_dates', 'start_date', 'end_date'),
        UniqueConstraint('initiator_id', 'collaborator_id', 'collaboration_name', name='unique_collaboration'),
        CheckConstraint('revenue_split_percentage >= 0 AND revenue_split_percentage <= 100 OR revenue_split_percentage IS NULL', name='valid_revenue_split'),
    )


class CollaborationRequest(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Collaboration invitation and request management"""
    
    __tablename__ = 'collaboration_requests'
    
    collaboration_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('collaborations.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    
    # Request Details
    sender_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    recipient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    request_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # invitation, application, proposal, counter_offer
    
    # Request Content
    subject: Mapped[str] = mapped_column(
        String(300),
        nullable=False
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    proposed_terms: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Attachments and Portfolio
    portfolio_items: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )  # URLs to showcase work
    
    attached_files: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    # Response Tracking
    response_required_by: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    response_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Decision
    is_accepted: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        index=True
    )
    
    rejection_reason: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    # Follow-up
    requires_negotiation: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    negotiation_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    collaboration: Mapped[Optional["Collaboration"]] = relationship(
        "Collaboration",
        back_populates="requests"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_requests_sender_recipient', 'sender_id', 'recipient_id'),
        Index('idx_requests_type_status', 'request_type', 'status'),
        Index('idx_requests_response_date', 'response_required_by'),
        Index('idx_requests_accepted', 'is_accepted'),
    )


class CollaborationAgreement(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Legal agreements for collaboration partnerships"""
    
    __tablename__ = 'collaboration_agreements'
    
    collaboration_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('collaborations.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Agreement Details
    agreement_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # standard_collaboration, revenue_share, licensing, work_for_hire
    
    agreement_title: Mapped[str] = mapped_column(
        String(300),
        nullable=False
    )
    
    agreement_version: Mapped[str] = mapped_column(
        String(20),
        default='1.0',
        nullable=False
    )
    
    # Legal Terms
    terms_and_conditions: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    intellectual_property_terms: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    revenue_sharing_terms: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Financial Details
    revenue_split_initiator: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )  # Percentage for initiator
    
    revenue_split_collaborator: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )  # Percentage for collaborator
    
    minimum_payout_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    payment_frequency: Mapped[str] = mapped_column(
        String(20),
        default='monthly',
        nullable=False
    )  # weekly, monthly, quarterly, project_end
    
    # Rights and Responsibilities
    content_ownership: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    usage_rights: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    exclusivity_terms: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Timeline and Deadlines
    project_milestones: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    delivery_schedule: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Quality Standards
    quality_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    approval_process: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Termination and Disputes
    termination_conditions: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    dispute_resolution: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    governing_law: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    # Signatures and Execution
    is_signed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    signed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    digital_signatures: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Digital signature data
    
    # Relationships
    collaboration: Mapped["Collaboration"] = relationship(
        "Collaboration",
        back_populates="agreement"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_agreements_type_signed', 'agreement_type', 'is_signed'),
        Index('idx_agreements_signed_at', 'signed_at'),
        CheckConstraint('revenue_split_initiator + revenue_split_collaborator = 100', name='valid_revenue_split_total'),
    )


class CollaborationRevenue(BaseModel, UUIDMixin, TimestampMixin, AuditMixin):
    """Revenue tracking and distribution for collaborations"""
    
    __tablename__ = 'collaboration_revenues'
    
    collaboration_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('collaborations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Revenue Information
    revenue_period: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )  # daily, weekly, monthly, quarterly, yearly
    
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Revenue Sources
    revenue_sources: Mapped[Dict[str, Decimal]] = mapped_column(
        JSONB,
        nullable=False
    )  # Platform-wise revenue breakdown
    
    total_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        index=True
    )
    
    # Distribution
    initiator_share: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    
    collaborator_share: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    
    platform_fees: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    transaction_fees: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    # Payment Status
    is_paid_out: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    payout_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    payment_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Analytics
    performance_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Views, engagement, conversion rates
    
    # Currency
    currency: Mapped[str] = mapped_column(
        String(3),
        default='USD',
        nullable=False
    )
    
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6),
        nullable=True
    )
    
    # Relationships
    collaboration: Mapped["Collaboration"] = relationship(
        "Collaboration",
        back_populates="revenue_records"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_revenues_period', 'period_start', 'period_end'),
        Index('idx_revenues_total', 'total_revenue'),
        Index('idx_revenues_payout', 'is_paid_out', 'payout_date'),
        CheckConstraint('total_revenue >= 0', name='positive_total_revenue'),
        CheckConstraint('initiator_share >= 0', name='positive_initiator_share'),
        CheckConstraint('collaborator_share >= 0', name='positive_collaborator_share'),
    )


class CollaborationMessage(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Communication system for collaboration management"""
    
    __tablename__ = 'collaboration_messages'
    
    collaboration_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('collaborations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Message Details
    sender_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    message_type: Mapped[str] = mapped_column(
        String(50),
        default='text',
        nullable=False
    )  # text, file, link, milestone_update, revenue_report
    
    subject: Mapped[Optional[str]] = mapped_column(
        String(300),
        nullable=True
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Attachments
    attachments: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    # Message Status
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    is_important: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Threading
    reply_to_message_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('collaboration_messages.id'),
        nullable=True,
        index=True
    )
    
    thread_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    # Metadata
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Relationships
    collaboration: Mapped["Collaboration"] = relationship(
        "Collaboration",
        back_populates="messages"
    )
    
    replies: Mapped[List["CollaborationMessage"]] = relationship(
        "CollaborationMessage",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_messages_collaboration_sender', 'collaboration_id', 'sender_id'),
        Index('idx_messages_created_at', 'created_at'),
        Index('idx_messages_read_status', 'is_read'),
        Index('idx_messages_thread', 'thread_id'),
    )
