"""Licensing and Rights Management Schemas

Comprehensive Pydantic schemas for licensing agreements, rights management,
and intellectual property protection in the IA Influencer Agent platform.

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


class LicenseTypeEnum(str, Enum):
    """
Types of content licenses"""

    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    EDITORIAL = "editorial"
    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    EDUCATIONAL = "educational"
    SYNC_LICENSE = "sync_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    MASTER_USE_LICENSE = "master_use_license"
    SAMPLING_LICENSE = "sampling_license"
    CUSTOM = "custom"


class UsageRightsEnum(str, Enum):
    """Types of usage rights"""

    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    PUBLIC_PERFORMANCE = "public_performance"
    PUBLIC_DISPLAY = "public_display"
    SYNCHRONIZATION = "synchronization"
    MECHANICAL = "mechanical"
    DIGITAL_STREAMING = "digital_streaming"
    BROADCAST = "broadcast"
    ADAPTATION = "adaptation"
    TRANSLATION = "translation"
    REMIX = "remix"
    SAMPLING = "sampling"
    COMMERCIAL_USE = "commercial_use"
    ADVERTISING = "advertising"
    RESALE = "resale"
    SUBLICENSING = "sublicensing"


class LicenseStatusEnum(str, Enum):
    """License agreement status"""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    BREACHED = "breached"
    RENEWED = "renewed"
    TRANSFERRED = "transferred"


class TerritoryEnum(str, Enum):
    """Geographic territories for licensing"""

    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    MIDDLE_EAST = "middle_east"
    UNITED_STATES = "united_states"
    CANADA = "canada"
    UNITED_KINGDOM = "united_kingdom"
    GERMANY = "germany"
    FRANCE = "france"
    JAPAN = "japan"
    AUSTRALIA = "australia"
    CUSTOM = "custom"


class PaymentTermsEnum(str, Enum):
    """Payment terms for licensing"""

    UPFRONT = "upfront"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    REVENUE_SHARE = "revenue_share"
    PER_USE = "per_use"
    MILESTONE_BASED = "milestone_based"
    NET_30 = "net_30"
    NET_60 = "net_60"
    NET_90 = "net_90"


class RoyaltyStructureSchema(BaseModel):
    """Schema for royalty payment structure"""
    royalty_type: str = Field(..., description="Type of royalty (percentage, fixed, tiered)")
    base_rate: Decimal = Field(..., description="Base royalty rate")
    currency: str = Field(..., description="Currency for payments")
    minimum_guarantee: Optional[Decimal] = Field(None, description="Minimum guaranteed payment")
    maximum_cap: Optional[Decimal] = Field(None, description="Maximum payment cap")
    
    # Tiered structure
    tiers: Optional[List[Dict[str, Any]]] = Field(None, description="Tiered royalty structure")
    threshold_amounts: Optional[List[Decimal]] = Field(None, description="Revenue thresholds")
    
    # Payment timing
    payment_frequency: PaymentTermsEnum = Field(..., description="Payment frequency")
    payment_delay_days: int = Field(0, description="Days delay after period end")
    accounting_period: str = Field("monthly", description="Accounting period")
    
    # Deductions
    allowable_deductions: Optional[List[str]] = Field(None, description="Allowable deductions")
    deduction_percentage: Optional[Decimal] = Field(None, description="Maximum deduction percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "royalty_type": "percentage",
                "base_rate": "15.00",
                "currency": "EUR",
                "minimum_guarantee": "1000.00",
                "payment_frequency": "quarterly",
                "accounting_period": "monthly"
            }
        }


class UsageRestrictionsSchema(BaseModel):
    """Schema for usage restrictions and limitations"""
    # Content restrictions
    adult_content_allowed: bool = Field(False, description="Adult content allowed")
    violence_content_allowed: bool = Field(False, description="Violence content allowed")
    political_content_allowed: bool = Field(True, description="Political content allowed")
    religious_content_allowed: bool = Field(True, description="Religious content allowed")
    
    # Usage limitations
    max_usage_duration: Optional[int] = Field(None, description="Maximum usage duration in seconds")
    max_broadcast_audience: Optional[int] = Field(None, description="Maximum broadcast audience size")
    max_copies: Optional[int] = Field(None, description="Maximum number of copies")
    max_downloads: Optional[int] = Field(None, description="Maximum number of downloads")
    
    # Platform restrictions
    excluded_platforms: Optional[List[str]] = Field(None, description="Platforms where use is prohibited")
    required_platforms: Optional[List[str]] = Field(None, description="Platforms where use is required")
    streaming_only: bool = Field(False, description="Streaming only, no downloads")
    
    # Attribution requirements
    attribution_required: bool = Field(True, description="Attribution required")
    attribution_format: Optional[str] = Field(None, description="Required attribution format")
    credit_placement: Optional[str] = Field(None, description="Where credit must be placed")
    
    # Modification restrictions
    modifications_allowed: bool = Field(False, description="Modifications allowed")
    remix_allowed: bool = Field(False, description="Remixing allowed")
    sampling_allowed: bool = Field(False, description="Sampling allowed")
    translation_allowed: bool = Field(True, description="Translation allowed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "adult_content_allowed": False,
                "max_usage_duration": 300,
                "attribution_required": True,
                "modifications_allowed": False,
                "streaming_only": True
            }
        }


class LicenseeInformationSchema(BaseModel):
    """Schema for licensee information"""
    # Basic information
    name: str = Field(..., description="Licensee name")
    company: Optional[str] = Field(None, description="Company name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    
    # Address information
    address_line1: str = Field(..., description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    state_province: Optional[str] = Field(None, description="State or province")
    postal_code: str = Field(..., description="Postal code")
    country: str = Field(..., description="Country")
    
    # Business information
    business_type: Optional[str] = Field(None, description="Type of business")
    tax_id: Optional[str] = Field(None, description="Tax identification number")
    vat_number: Optional[str] = Field(None, description="VAT number")
    website: Optional[HttpUrl] = Field(None, description="Website URL")
    
    # Verification
    identity_verified: bool = Field(False, description="Identity verification status")
    business_verified: bool = Field(False, description="Business verification status")
    verification_documents: Optional[List[str]] = Field(None, description="Verification document URLs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "company": "Creative Media Ltd",
                "email": "john@creativemedia.com",
                "address_line1": "123 Creative Street",
                "city": "Berlin",
                "country": "Germany",
                "business_type": "media_production"
            }
        }


class LicensingAgreementBaseSchema(BaseModel):
    """Base schema for licensing agreements"""
    # Agreement identification
    agreement_title: str = Field(..., description="Title of the licensing agreement")
    license_type: LicenseTypeEnum = Field(..., description="Type of license")
    content_id: PositiveInt = Field(..., description="Licensed content ID")
    fingerprint_id: Optional[PositiveInt] = Field(None, description="Content fingerprint ID")
    
    # Parties
    licensor_id: PositiveInt = Field(..., description="Licensor user ID")
    licensee_info: LicenseeInformationSchema = Field(..., description="Licensee information")
    
    # Rights and permissions
    granted_rights: List[UsageRightsEnum] = Field(..., description="Rights granted to licensee")
    territory: TerritoryEnum = Field(..., description="Geographic territory")
    custom_territories: Optional[List[str]] = Field(None, description="Custom territory definitions")
    
    # Duration and timing
    effective_date: date = Field(..., description="Agreement effective date")
    expiration_date: Optional[date] = Field(None, description="Agreement expiration date")
    term_duration_months: Optional[int] = Field(None, description="Term duration in months")
    auto_renewal: bool = Field(False, description="Automatic renewal enabled")
    renewal_notice_days: int = Field(30, description="Notice period for renewal in days")
    
    # Financial terms
    royalty_structure: RoyaltyStructureSchema = Field(..., description="Royalty payment structure")
    advance_payment: Optional[Decimal] = Field(None, description="Advance payment amount")
    signing_bonus: Optional[Decimal] = Field(None, description="Signing bonus")
    
    # Usage restrictions and obligations
    usage_restrictions: UsageRestrictionsSchema = Field(..., description="Usage restrictions")
    reporting_obligations: List[str] = Field(..., description="Reporting obligations")
    quality_standards: Optional[Dict[str, Any]] = Field(None, description="Quality standards")
    
    # Legal and compliance
    governing_law: str = Field(..., description="Governing law jurisdiction")
    dispute_resolution: str = Field(..., description="Dispute resolution method")
    force_majeure_clause: bool = Field(True, description="Force majeure clause included")
    
    @field_validator('expiration_date')
    @classmethod
    def validate_expiration_date(cls, v, values):
        """Validate expiration date is after effective date"""
        effective_date = values.get('effective_date')
        if v and effective_date and v <= effective_date:
            raise ValueError("Expiration date must be after effective date")
        return v


class LicensingAgreementCreateSchema(LicensingAgreementBaseSchema):
    """Schema for creating licensing agreements"""
    # Additional creation options
    template_id: Optional[PositiveInt] = Field(None, description="License template ID")
    auto_approve: bool = Field(False, description="Auto-approve if conditions met")
    notification_enabled: bool = Field(True, description="Enable notifications")
    
    # Draft settings
    save_as_draft: bool = Field(False, description="Save as draft")
    draft_notes: Optional[str] = Field(None, description="Draft notes")
    
    # Verification requirements
    require_identity_verification: bool = Field(True, description="Require identity verification")
    require_business_verification: bool = Field(False, description="Require business verification")
    require_reference_check: bool = Field(False, description="Require reference check")
    
    # Integration settings
    integrate_with_platforms: bool = Field(True, description="Integrate with content platforms")
    auto_content_id: bool = Field(True, description="Automatic content ID registration")
    monitoring_enabled: bool = Field(True, description="Enable usage monitoring")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agreement_title": "Music Sync License for Commercial Use",
                "license_type": "sync_license",
                "content_id": 12345,
                "licensor_id": 123,
                "granted_rights": ["synchronization", "commercial_use"],
                "territory": "worldwide",
                "effective_date": "2024-09-01",
                "term_duration_months": 24,
                "governing_law": "German Law"
            }
        }


class LicensingAgreementUpdateSchema(BaseModel):
    """Schema for updating licensing agreements"""
    agreement_title: Optional[str] = Field(None, description="Updated agreement title")
    expiration_date: Optional[date] = Field(None, description="Updated expiration date")
    auto_renewal: Optional[bool] = Field(None, description="Updated auto-renewal setting")
    royalty_structure: Optional[RoyaltyStructureSchema] = Field(None, description="Updated royalty structure")
    usage_restrictions: Optional[UsageRestrictionsSchema] = Field(None, description="Updated usage restrictions")
    status: Optional[LicenseStatusEnum] = Field(None, description="Updated license status")
    notes: Optional[str] = Field(None, description="Update notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expiration_date": "2026-08-31",
                "auto_renewal": True,
                "status": "active",
                "notes": "Extended term and enabled auto-renewal"
            }
        }


class LicenseComplianceSchema(BaseModel):
    """Schema for license compliance monitoring"""
    agreement_id: PositiveInt = Field(..., description="License agreement ID")
    compliance_check_date: datetime = Field(..., description="Compliance check date")
    overall_compliance: bool = Field(..., description="Overall compliance status")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Compliance score")
    
    # Compliance details
    usage_within_terms: bool = Field(..., description="Usage within agreed terms")
    territory_compliance: bool = Field(..., description="Territory restrictions complied")
    attribution_compliance: bool = Field(..., description="Attribution requirements met")
    payment_compliance: bool = Field(..., description="Payment obligations met")
    reporting_compliance: bool = Field(..., description="Reporting obligations met")
    
    # Violations
    violations_detected: List[Dict[str, Any]] = Field([], description="Detected violations")
    violation_severity: Optional[str] = Field(None, description="Highest violation severity")
    
    # Actions taken
    warnings_issued: int = Field(0, description="Number of warnings issued")
    notices_sent: int = Field(0, description="Number of notices sent")
    automatic_actions: List[str] = Field([], description="Automatic actions taken")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agreement_id": 12345,
                "overall_compliance": True,
                "compliance_score": 0.95,
                "usage_within_terms": True,
                "payment_compliance": True,
                "violations_detected": [],
                "warnings_issued": 0
            }
        }


class LicensingAgreementResponseSchema(LicensingAgreementBaseSchema):
    """Schema for licensing agreement responses"""
    id: PositiveInt = Field(..., description="Unique agreement ID")
    agreement_reference: str = Field(..., description="Human-readable agreement reference")
    
    # Status and tracking
    status: LicenseStatusEnum = Field(..., description="Current agreement status")
    version: int = Field(1, description="Agreement version number")
    approval_status: str = Field(..., description="Approval status")
    
    # Compliance and monitoring
    compliance_status: Optional[LicenseComplianceSchema] = Field(None, description="Latest compliance status")
    usage_monitoring_enabled: bool = Field(..., description="Usage monitoring enabled")
    violation_count: int = Field(0, description="Number of violations detected")
    
    # Financial tracking
    total_revenue_generated: Decimal = Field(Decimal('0.00'), description="Total revenue generated")
    total_royalties_paid: Decimal = Field(Decimal('0.00'), description="Total royalties paid")
    outstanding_balance: Decimal = Field(Decimal('0.00'), description="Outstanding balance")
    next_payment_due: Optional[date] = Field(None, description="Next payment due date")
    
    # Performance metrics
    usage_statistics: Optional[Dict[str, Any]] = Field(None, description="Usage statistics")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    
    # Document management
    contract_document_url: Optional[str] = Field(None, description="Contract document URL")
    signed_document_url: Optional[str] = Field(None, description="Signed contract URL")
    amendment_documents: Optional[List[str]] = Field(None, description="Amendment document URLs")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    signed_at: Optional[datetime] = Field(None, description="Contract signing timestamp")
    activated_at: Optional[datetime] = Field(None, description="Activation timestamp")
    
    # Workflow tracking
    approval_workflow: Optional[List[Dict]] = Field(None, description="Approval workflow history")
    modification_history: Optional[List[Dict]] = Field(None, description="Modification history")
    communication_log: Optional[List[Dict]] = Field(None, description="Communication log")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "agreement_reference": "LIC-2024-001234",
                "status": "active",
                "version": 1,
                "approval_status": "approved",
                "total_revenue_generated": "5750.00",
                "total_royalties_paid": "862.50",
                "usage_monitoring_enabled": True,
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class RightsManagementSchema(BaseModel):
    """Schema for intellectual property rights management"""
    content_id: PositiveInt = Field(..., description="Content ID")
    copyright_owner: str = Field(..., description="Copyright owner name")
    copyright_year: int = Field(..., description="Copyright year")
    copyright_registration: Optional[str] = Field(None, description="Copyright registration number")
    
    # Rights information
    composition_rights: Optional[Dict[str, Any]] = Field(None, description="Composition rights details")
    sound_recording_rights: Optional[Dict[str, Any]] = Field(None, description="Sound recording rights")
    publishing_rights: Optional[Dict[str, Any]] = Field(None, description="Publishing rights")
    neighboring_rights: Optional[Dict[str, Any]] = Field(None, description="Neighboring rights")
    
    # Societies and organizations
    performing_rights_society: Optional[str] = Field(None, description="Performing rights society")
    mechanical_rights_society: Optional[str] = Field(None, description="Mechanical rights society")
    collection_societies: Optional[List[str]] = Field(None, description="Collection societies")
    
    # Clearances and permissions
    sample_clearances: Optional[List[Dict]] = Field(None, description="Sample clearances")
    interpolation_clearances: Optional[List[Dict]] = Field(None, description="Interpolation clearances")
    cover_version_permissions: Optional[List[Dict]] = Field(None, description="Cover version permissions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_id": 12345,
                "copyright_owner": "John Doe Music",
                "copyright_year": 2024,
                "performing_rights_society": "GEMA",
                "mechanical_rights_society": "GEMA",
                "collection_societies": ["GEMA", "GVL"]
            }
        }


class LicensingDashboardSchema(BaseModel):
    """Schema for licensing dashboard metrics"""
    # Agreement summary
    total_agreements: int = Field(..., description="Total number of agreements")
    active_agreements: int = Field(..., description="Number of active agreements")
    pending_agreements: int = Field(..., description="Number of pending agreements")
    expired_agreements: int = Field(..., description="Number of expired agreements")
    
    # Revenue summary
    total_licensing_revenue: Decimal = Field(..., description="Total licensing revenue")
    revenue_this_month: Decimal = Field(..., description="Revenue this month")
    pending_royalties: Decimal = Field(..., description="Pending royalty payments")
    overdue_payments: Decimal = Field(..., description="Overdue payments")
    
    # Performance metrics
    average_deal_value: Decimal = Field(..., description="Average deal value")
    conversion_rate: float = Field(..., description="License conversion rate")
    renewal_rate: float = Field(..., description="License renewal rate")
    compliance_rate: float = Field(..., description="Overall compliance rate")
    
    # Breakdown by type
    agreements_by_type: Dict[str, int] = Field(..., description="Agreements by license type")
    revenue_by_type: Dict[str, Decimal] = Field(..., description="Revenue by license type")
    territory_distribution: Dict[str, int] = Field(..., description="Agreements by territory")
    
    # Trends and forecasts
    revenue_trends: List[Dict] = Field(..., description="Revenue trends over time")
    agreement_trends: List[Dict] = Field(..., description="Agreement trends over time")
    forecasted_revenue: Dict[str, Decimal] = Field(..., description="Revenue forecasts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_agreements": 150,
                "active_agreements": 125,
                "pending_agreements": 15,
                "total_licensing_revenue": "125000.00",
                "revenue_this_month": "8500.00",
                "average_deal_value": "833.33",
                "compliance_rate": 0.96
            }
        }


# Export schemas
__all__ = [
    # Enums
    "LicenseTypeEnum",
    "UsageRightsEnum",
    "LicenseStatusEnum",
    "TerritoryEnum",
    "PaymentTermsEnum",
    
    # Complex schemas
    "RoyaltyStructureSchema",
    "UsageRestrictionsSchema",
    "LicenseeInformationSchema",
    "LicenseComplianceSchema",
    "RightsManagementSchema",
    
    # Main schemas
    "LicensingAgreementBaseSchema",
    "LicensingAgreementCreateSchema",
    "LicensingAgreementUpdateSchema",
    "LicensingAgreementResponseSchema",
    
    # Dashboard and utilities
    "LicensingDashboardSchema"
]
