"""Copyright & Licensing Schemas for IA Influencer Agent Platform
Professional intellectual property, copyright management, and licensing schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pydantic import Field, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class CopyrightCreate(BaseSchema):
    """Copyright registration request schema."""    
    content_id: UUID = Field(description="Content to register for copyright")
    copyright_holder_id: UUID = Field(description="Primary copyright holder")
    work_title: str = Field(min_length=1, max_length=300, description="Official work title")
    work_type: str = Field(description="Type of copyrighted work")
    
    # Work details
    creation_date: datetime = Field(description="Date of work creation")
    publication_date: Optional[datetime] = Field(None, description="Date of first publication")
    work_description: str = Field(max_length=2000, description="Detailed work description")
    genre_category: str = Field(description="Genre or category of work")
    
    # Authorship information
    authors: List[Dict[str, Any]] = Field(description="List of authors/creators")
    contributors: List[Dict[str, Any]] = Field(default_factory=list, description="Additional contributors")
    work_for_hire: bool = Field(default=False, description="Work created for hire")
    
    # Registration details
    registration_jurisdiction: str = Field(description="Jurisdiction for registration")
    registration_type: str = Field(description="Type of copyright registration")
    existing_registrations: List[Dict[str, str]] = Field(default_factory=list)
    
    # Supporting materials
    deposit_materials: List[Dict[str, str]] = Field(default_factory=list)
    supporting_documents: List[HttpUrl] = Field(default_factory=list)
    related_works: List[UUID] = Field(default_factory=list, description="Related copyrighted works")
    
    @validator('work_type')
    def validate_work_type(cls, v):
        """Validate work type."""        allowed_types = {
            "literary_work", "musical_work", "dramatic_work", "choreographic_work",
            "pictorial_graphic_sculptural", "motion_picture", "sound_recording",
            "architectural_work", "computer_program", "compilation", "derivative_work"
        }
        if v not in allowed_types:
            raise ValueError(f'Work type must be one of: {", ".join(allowed_types)}')
        return v


class CopyrightOut(UUIDSchema, TimestampSchema):
    """Copyright information schema."""    
    content_id: UUID
    copyright_holder_id: UUID
    work_title: str
    work_type: str
    registration_status: str = Field(description="Current registration status")
    
    # Registration information
    registration_number: Optional[str] = Field(None, description="Official registration number")
    registration_date: Optional[datetime] = Field(None)
    registration_jurisdiction: str
    registration_certificate_url: Optional[HttpUrl] = None
    
    # Copyright term information
    copyright_term_start: datetime
    copyright_term_end: Optional[datetime] = None
    renewal_required: bool = Field(default=False)
    renewal_date: Optional[datetime] = None
    
    # Ownership information
    ownership_percentage: Dict[str, float] = Field(default_factory=dict)
    moral_rights_retained: bool = Field(default=True)
    transfer_restrictions: List[str] = Field(default_factory=list)
    
    # Protection status
    protection_level: str = Field(default="full_copyright")
    fair_use_guidelines: List[str] = Field(default_factory=list)
    licensing_restrictions: List[str] = Field(default_factory=list)
    
    # Legal standing
    enforcement_rights: List[str] = Field(default_factory=list)
    litigation_history: List[Dict[str, Any]] = Field(default_factory=list)
    infringement_cases: int = Field(default=0, ge=0)
    successful_enforcements: int = Field(default=0, ge=0)
    
    # Commercial information
    is_commercially_exploited: bool = Field(default=False)
    licensing_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    estimated_value: Optional[Decimal] = None


class CopyrightClaim(UUIDSchema, TimestampSchema, AuditSchema):
    """Copyright claim schema."""    
    copyright_id: UUID = Field(description="Associated copyright registration")
    claimant_id: UUID = Field(description="Person or entity making the claim")
    claim_type: str = Field(description="Type of copyright claim")
    claim_basis: str = Field(description="Legal basis for the claim")
    
    # Infringement details
    infringing_content_url: HttpUrl = Field(description="URL of infringing content")
    infringing_platform: str = Field(description="Platform hosting infringing content")
    infringer_information: Dict[str, str] = Field(default_factory=dict)
    infringement_description: str = Field(description="Detailed infringement description")
    
    # Evidence and documentation
    evidence_of_ownership: List[HttpUrl] = Field(default_factory=list)
    evidence_of_infringement: List[HttpUrl] = Field(default_factory=list)
    expert_analysis: Optional[str] = Field(None, description="Expert analysis report")
    forensic_evidence: Dict[str, Any] = Field(default_factory=dict)
    
    # Legal actions
    notice_sent: bool = Field(default=False)
    notice_sent_date: Optional[datetime] = None
    response_received: bool = Field(default=False)
    response_content: Optional[str] = None
    legal_action_taken: bool = Field(default=False)
    
    # Financial impact
    estimated_damages: Optional[Decimal] = Field(None, ge=0)
    lost_revenue: Optional[Decimal] = Field(None, ge=0)
    legal_costs: Optional[Decimal] = Field(None, ge=0)
    settlement_amount: Optional[Decimal] = None
    
    # Claim status and resolution
    claim_status: str = Field(default="submitted")
    resolution_type: Optional[str] = None
    resolution_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    @validator('claim_type')
    def validate_claim_type(cls, v):
        """Validate claim type."""        allowed_types = {
            "direct_infringement", "contributory_infringement", "vicarious_infringement",
            "digital_piracy", "unauthorized_distribution", "derivative_work_violation",
            "public_performance_violation", "synchronization_violation"
        }
        if v not in allowed_types:
            raise ValueError(f'Claim type must be one of: {", ".join(allowed_types)}')
        return v


class CopyrightTransfer(UUIDSchema, TimestampSchema, AuditSchema):
    """Copyright transfer/assignment schema."""    
    copyright_id: UUID
    transferor_id: UUID = Field(description="Current copyright holder transferring rights")
    transferee_id: UUID = Field(description="New copyright holder receiving rights")
    transfer_type: str = Field(description="Type of transfer")
    
    # Transfer details
    rights_transferred: List[str] = Field(description="Specific rights being transferred")
    transfer_percentage: float = Field(ge=0.0, le=100.0, description="Percentage of rights transferred")
    territorial_scope: List[str] = Field(default_factory=list, description="Geographic scope")
    duration_of_transfer: Optional[str] = Field(None, description="Duration of transfer")
    
    # Financial terms
    transfer_consideration: Optional[Decimal] = Field(None, ge=0, description="Payment for transfer")
    royalty_arrangements: Dict[str, Any] = Field(default_factory=dict)
    revenue_sharing: Dict[str, float] = Field(default_factory=dict)
    
    # Legal documentation
    transfer_agreement_url: Optional[HttpUrl] = None
    legal_representation: Dict[str, str] = Field(default_factory=dict)
    notarization_required: bool = Field(default=False)
    registration_required: bool = Field(default=True)
    
    # Transfer conditions
    conditions_precedent: List[str] = Field(default_factory=list)
    warranties_and_representations: List[str] = Field(default_factory=list)
    indemnification_clauses: List[str] = Field(default_factory=list)
    
    # Status tracking
    transfer_status: str = Field(default="pending")
    execution_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    registration_date: Optional[datetime] = None
    
    @validator('transfer_type')
    def validate_transfer_type(cls, v):
        """Validate transfer type."""        allowed_types = {
            "assignment", "exclusive_license", "non_exclusive_license",
            "work_for_hire_assignment", "testamentary_transfer", "involuntary_transfer"
        }
        if v not in allowed_types:
            raise ValueError(f'Transfer type must be one of: {", ".join(allowed_types)}')
        return v


class LicenseAgreement(UUIDSchema, TimestampSchema, AuditSchema):
    """License agreement schema."""    
    copyright_id: UUID = Field(description="Licensed copyrighted work")
    licensor_id: UUID = Field(description="License grantor")
    licensee_id: UUID = Field(description="License recipient")
    license_type: str = Field(description="Type of license")
    
    # License scope
    licensed_rights: List[str] = Field(description="Specific rights being licensed")
    permitted_uses: List[str] = Field(description="Permitted uses of the work")
    prohibited_uses: List[str] = Field(default_factory=list, description="Prohibited uses")
    territorial_limits: List[str] = Field(default_factory=list, description="Geographic limitations")
    
    # License terms
    license_duration: str = Field(description="Duration of license")
    start_date: datetime = Field(description="License start date")
    end_date: Optional[datetime] = Field(None, description="License end date")
    renewal_options: Dict[str, Any] = Field(default_factory=dict)
    
    # Financial terms
    license_fee_structure: str = Field(description="Fee structure type")
    upfront_fee: Optional[Decimal] = Field(None, ge=0, description="Initial payment")
    royalty_rate: Optional[float] = Field(None, ge=0.0, le=100.0, description="Royalty percentage")
    minimum_guarantee: Optional[Decimal] = Field(None, ge=0)
    payment_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Quality and standards
    quality_standards: List[str] = Field(default_factory=list)
    attribution_requirements: List[str] = Field(default_factory=list)
    modification_rights: Dict[str, bool] = Field(default_factory=dict)
    approval_requirements: List[str] = Field(default_factory=list)
    
    # Legal provisions
    termination_clauses: List[str] = Field(default_factory=list)
    breach_remedies: List[str] = Field(default_factory=list)
    indemnification_terms: Dict[str, str] = Field(default_factory=dict)
    governing_law: str = Field(description="Governing law jurisdiction")
    
    # License management
    sublicensing_allowed: bool = Field(default=False)
    exclusivity: str = Field(description="Exclusivity level")
    reporting_requirements: List[str] = Field(default_factory=list)
    audit_rights: Dict[str, bool] = Field(default_factory=dict)
    
    # Status and compliance
    license_status: str = Field(default="draft")
    compliance_status: str = Field(default="pending")
    last_compliance_check: Optional[datetime] = None
    violations_reported: int = Field(default=0, ge=0)
    
    @validator('license_type')
    def validate_license_type(cls, v):
        """Validate license type."""        allowed_types = {
            "exclusive", "non_exclusive", "sole", "compulsory", "statutory",
            "creative_commons", "royalty_free", "rights_managed", "microstock",
            "synchronization", "mechanical", "performance", "broadcast"
        }
        if v not in allowed_types:
            raise ValueError(f'License type must be one of: {", ".join(allowed_types)}')
        return v


class LicenseUsage(UUIDSchema, TimestampSchema):
    """License usage tracking schema."""    
    license_agreement_id: UUID
    licensee_id: UUID
    usage_period_start: datetime
    usage_period_end: datetime
    
    # Usage metrics
    total_usage_instances: int = Field(default=0, ge=0)
    usage_by_type: Dict[str, int] = Field(default_factory=dict)
    usage_by_platform: Dict[str, int] = Field(default_factory=dict)
    usage_by_territory: Dict[str, int] = Field(default_factory=dict)
    
    # Performance data
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    engagement_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Revenue tracking
    gross_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    net_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    royalties_due: Decimal = Field(default=Decimal('0.00'), ge=0)
    royalties_paid: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Compliance monitoring
    terms_compliance: bool = Field(default=True)
    usage_violations: List[str] = Field(default_factory=list)
    attribution_compliance: bool = Field(default=True)
    quality_compliance: bool = Field(default=True)
    
    # Reporting
    usage_report_url: Optional[HttpUrl] = None
    detailed_analytics: Dict[str, Any] = Field(default_factory=dict)
    performance_benchmarks: Dict[str, float] = Field(default_factory=dict)


class RightsManagement(UUIDSchema, TimestampSchema):
    """Comprehensive rights management schema."""    
    content_id: UUID
    rights_holder_id: UUID
    rights_portfolio_name: str = Field(description="Name of rights portfolio")
    
    # Rights inventory
    owned_rights: Dict[str, float] = Field(default_factory=dict, description="Owned rights percentages")
    licensed_rights: Dict[str, Any] = Field(default_factory=dict, description="Licensed rights details")
    administered_rights: Dict[str, Any] = Field(default_factory=dict, description="Rights under administration")
    
    # Geographic rights
    territorial_rights: Dict[str, List[str]] = Field(default_factory=dict)
    international_registrations: List[Dict[str, str]] = Field(default_factory=list)
    reciprocal_agreements: List[str] = Field(default_factory=list)
    
    # Digital rights management
    drm_settings: Dict[str, Any] = Field(default_factory=dict)
    digital_distribution_rights: List[str] = Field(default_factory=list)
    streaming_rights: Dict[str, Any] = Field(default_factory=dict)
    download_rights: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance rights
    public_performance_rights: Dict[str, bool] = Field(default_factory=dict)
    broadcast_rights: Dict[str, Any] = Field(default_factory=dict)
    synchronization_rights: Dict[str, Any] = Field(default_factory=dict)
    live_performance_rights: Dict[str, bool] = Field(default_factory=dict)
    
    # Commercial exploitation
    merchandising_rights: Dict[str, bool] = Field(default_factory=dict)
    adaptation_rights: Dict[str, bool] = Field(default_factory=dict)
    translation_rights: Dict[str, bool] = Field(default_factory=dict)
    derivative_work_rights: Dict[str, bool] = Field(default_factory=dict)
    
    # Rights valuation
    estimated_value: Optional[Decimal] = None
    revenue_history: List[Dict[str, Any]] = Field(default_factory=list)
    licensing_income: Decimal = Field(default=Decimal('0.00'), ge=0)
    market_comparables: List[Dict[str, Any]] = Field(default_factory=list)


class IntellectualProperty(UUIDSchema, TimestampSchema, AuditSchema):
    """Comprehensive intellectual property portfolio schema."""    
    owner_id: UUID = Field(description="IP portfolio owner")
    portfolio_name: str = Field(description="IP portfolio name")
    portfolio_type: str = Field(description="Type of IP portfolio")
    
    # Copyright assets
    copyrighted_works: List[UUID] = Field(default_factory=list)
    copyright_applications: List[UUID] = Field(default_factory=list)
    copyright_registrations: List[UUID] = Field(default_factory=list)
    
    # Trademark assets
    trademarks: List[Dict[str, Any]] = Field(default_factory=list)
    trademark_applications: List[Dict[str, Any]] = Field(default_factory=list)
    service_marks: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Patent assets (if applicable)
    patents: List[Dict[str, Any]] = Field(default_factory=list)
    patent_applications: List[Dict[str, Any]] = Field(default_factory=list)
    utility_models: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Trade secrets and know-how
    trade_secrets: List[Dict[str, str]] = Field(default_factory=list)
    confidential_information: List[Dict[str, str]] = Field(default_factory=list)
    proprietary_processes: List[Dict[str, str]] = Field(default_factory=list)
    
    # Portfolio management
    management_strategy: Dict[str, str] = Field(default_factory=dict)
    protection_priorities: List[str] = Field(default_factory=list)
    enforcement_policies: List[str] = Field(default_factory=list)
    licensing_strategy: Dict[str, Any] = Field(default_factory=dict)
    
    # Financial metrics
    portfolio_value: Optional[Decimal] = None
    annual_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    licensing_income: Decimal = Field(default=Decimal('0.00'), ge=0)
    enforcement_costs: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Risk management
    infringement_risks: List[Dict[str, Any]] = Field(default_factory=list)
    competitive_threats: List[str] = Field(default_factory=list)
    expiration_schedule: List[Dict[str, datetime]] = Field(default_factory=list)
    renewal_calendar: List[Dict[str, datetime]] = Field(default_factory=list)
    
    @validator('portfolio_type')
    def validate_portfolio_type(cls, v):
        """Validate portfolio type."""        allowed_types = {
            "creative_works", "brand_assets", "technology_patents", "mixed_portfolio",
            "entertainment_rights", "digital_assets", "content_library"
        }
        if v not in allowed_types:
            raise ValueError(f'Portfolio type must be one of: {", ".join(allowed_types)}')
        return v
