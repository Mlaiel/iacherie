"""IA Influencer Agent Platform - Copyright Models
Comprehensive copyright and intellectual property management

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


class Copyright(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin, MetadataMixin):
    """
Core copyright registration and management"""
    
    __tablename__ = 'copyrights'
    
    content_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('contents.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    owner_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Copyright Information
    copyright_title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True
    )
    
    copyright_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )  # Official registration number
    
    # Ownership Details
    ownership_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # sole, joint, work_for_hire, derivative, collective
    
    ownership_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal('100.00'),
        nullable=False
    )  # 0-100 percentage ownership
    
    # Legal Information
    jurisdiction: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # Country/region where copyright is registered
    
    registration_status: Mapped[str] = mapped_column(
        String(50),
        default='pending',
        nullable=False,
        index=True
    )  # pending, registered, rejected, expired
    
    registered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    registration_authority: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )  # Copyright office, registrar
    
    # Duration and Expiry
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )  # Date of creation
    
    publication_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Work Details
    work_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # literary, musical, dramatic, artistic, sound_recording, audiovisual
    
    work_category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Creator Information
    authors: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False
    )  # List of authors/creators with their details
    
    contributors: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Additional contributors
    
    # Rights and Permissions
    exclusive_rights: Mapped[Dict[str, bool]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )  # reproduction, distribution, public_performance, etc.
    
    moral_rights: Mapped[Dict[str, bool]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )  # attribution, integrity, disclosure
    
    # Financial Information
    registration_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    estimated_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        default='USD',
        nullable=False
    )
    
    # Relationships
    claims: Mapped[List["CopyrightClaim"]] = relationship(
        "CopyrightClaim",
        back_populates="copyright",
        cascade="all, delete-orphan"
    )
    
    transfers: Mapped[List["CopyrightTransfer"]] = relationship(
        "CopyrightTransfer",
        back_populates="copyright",
        cascade="all, delete-orphan"
    )
    
    licenses: Mapped[List["CopyrightLicense"]] = relationship(
        "CopyrightLicense",
        back_populates="copyright",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_copyrights_owner_type', 'owner_id', 'ownership_type'),
        Index('idx_copyrights_status_jurisdiction', 'registration_status', 'jurisdiction'),
        Index('idx_copyrights_creation_expiry', 'creation_date', 'expiry_date'),
        CheckConstraint('ownership_percentage >= 0 AND ownership_percentage <= 100', name='valid_ownership_percentage'),
    )


class CopyrightClaim(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Copyright infringement claims and disputes"""
    
    __tablename__ = 'copyright_claims'
    
    copyright_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('copyrights.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Claim Information
    claim_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # infringement, fair_use_dispute, ownership_dispute
    
    claim_title: Mapped[str] = mapped_column(
        String(300),
        nullable=False
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Parties Involved
    claimant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id'),
        nullable=False,
        index=True
    )
    
    respondent_info: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )  # Information about the alleged infringer
    
    # Evidence and Documentation
    evidence_urls: Mapped[List[str]] = mapped_column(
        ARRAY(String(500)),
        nullable=False
    )
    
    supporting_documents: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    # Legal Basis
    legal_grounds: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    applicable_laws: Mapped[List[str]] = mapped_column(
        ARRAY(String(200)),
        nullable=False
    )
    
    # Claim Details
    infringing_content_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )
    
    date_of_infringement: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Damages and Relief
    damages_claimed: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    relief_sought: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Resolution
    resolution_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )  # settlement, court_decision, withdrawal, dismissal
    
    resolution_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    settlement_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    # Relationships
    copyright: Mapped["Copyright"] = relationship(
        "Copyright",
        back_populates="claims"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_claims_type_status', 'claim_type', 'status'),
        Index('idx_claims_claimant', 'claimant_id'),
        Index('idx_claims_resolution', 'resolution_date'),
    )


class CopyrightTransfer(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Copyright ownership transfers and assignments"""
    
    __tablename__ = 'copyright_transfers'
    
    copyright_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('copyrights.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Transfer Information
    transfer_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # assignment, exclusive_license, non_exclusive_license, work_for_hire
    
    # Parties
    transferor_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id'),
        nullable=False,
        index=True
    )
    
    transferee_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id'),
        nullable=False,
        index=True
    )
    
    # Rights Transferred
    rights_transferred: Mapped[Dict[str, bool]] = mapped_column(
        JSONB,
        nullable=False
    )  # Which specific rights are being transferred
    
    percentage_transferred: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )  # 0-100 percentage of rights transferred
    
    # Terms and Conditions
    transfer_terms: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    consideration: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )  # Payment/consideration for transfer
    
    # Duration
    effective_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Legal Documentation
    contract_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    witnessed_by: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    notarized: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Relationships
    copyright: Mapped["Copyright"] = relationship(
        "Copyright",
        back_populates="transfers"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_transfers_transferor_transferee', 'transferor_id', 'transferee_id'),
        Index('idx_transfers_effective_expiry', 'effective_date', 'expiry_date'),
        Index('idx_transfers_type', 'transfer_type'),
        CheckConstraint('percentage_transferred >= 0 AND percentage_transferred <= 100', name='valid_transfer_percentage'),
    )


class CopyrightLicense(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin):
    """Copyright licensing agreements and permissions"""
    
    __tablename__ = 'copyright_licenses'
    
    copyright_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('copyrights.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # License Information
    license_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # exclusive, non_exclusive, creative_commons, royalty_free, sync_license
    
    license_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    # Licensee
    licensee_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id'),
        nullable=True,
        index=True
    )
    
    licensee_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # For external licensees
    
    # Rights Granted
    granted_rights: Mapped[Dict[str, bool]] = mapped_column(
        JSONB,
        nullable=False
    )  # reproduction, distribution, public_performance, etc.
    
    usage_restrictions: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Geographic, temporal, medium restrictions
    
    # Financial Terms
    license_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    royalty_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )  # 0-1 decimal rate
    
    minimum_guarantee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    # Duration
    effective_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    auto_renew: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Terms and Conditions
    terms_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    special_conditions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    copyright: Mapped["Copyright"] = relationship(
        "Copyright",
        back_populates="licenses"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_licenses_type_status', 'license_type', 'status'),
        Index('idx_licenses_licensee', 'licensee_id'),
        Index('idx_licenses_effective_expiry', 'effective_date', 'expiry_date'),
        CheckConstraint('royalty_rate >= 0 AND royalty_rate <= 1 OR royalty_rate IS NULL', name='valid_royalty_rate'),
    )
