"""Pydantic schemas for Campaigns API"""
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, validator


# Enums
class CampaignType(str):
    PETITION = "petition"
    FUNDRAISING = "fundraising"


class CampaignStatus(str):
    DRAFT = "draft"
    ACTIVE = "active"
    SUCCESSFUL = "successful"
    CLOSED = "closed"
    CANCELLED = "cancelled"


# Campaign schemas
class CampaignBase(BaseModel):
    type: str
    title: str = Field(..., max_length=200)
    description: str
    story: Optional[str] = None
    objectives: Optional[str] = None
    goal: float = Field(..., gt=0)
    tags: List[str] = Field(default_factory=list)


class CampaignCreate(CampaignBase):
    creator_type: str = "individual"  # individual, organization, volunteer
    organization_name: Optional[str] = None
    end_date: Optional[datetime] = None
    cover_image: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    
    # Pour FUNDRAISING
    beneficiary_name: Optional[str] = None
    beneficiary_details: Optional[str] = None
    funds_usage_plan: Optional[str] = None
    
    # Pour PETITION
    target_authority: Optional[str] = None
    target_email: Optional[EmailStr] = None
    petition_text: Optional[str] = None
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['petition', 'fundraising']:
            raise ValueError('Type must be either "petition" or "fundraising"')
        return v
    
    @validator('creator_type')
    def validate_creator_type(cls, v):
        valid_types = ['individual', 'organization', 'volunteer']
        if v not in valid_types:
            raise ValueError(f'Creator type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('beneficiary_name')
    def validate_fundraising_fields(cls, v, values):
        if values.get('type') == 'fundraising' and not v:
            raise ValueError('Beneficiary name is required for fundraising campaigns')
        return v
    
    @validator('target_authority')
    def validate_petition_fields(cls, v, values):
        if values.get('type') == 'petition' and not v:
            raise ValueError('Target authority is required for petition campaigns')
        return v


class CampaignUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    story: Optional[str] = None
    objectives: Optional[str] = None
    status: Optional[str] = None
    end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    success_story: Optional[str] = None
    impact_achieved: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['draft', 'active', 'successful', 'closed', 'cancelled']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class CampaignResponse(CampaignBase):
    id: UUID
    status: str
    creator_id: UUID
    creator_type: str
    organization_name: Optional[str] = None
    current_amount: float = 0
    start_date: datetime
    end_date: Optional[datetime] = None
    cover_image: Optional[str] = None
    images: List[str] = []
    videos: List[str] = []
    
    # Pour FUNDRAISING
    beneficiary_name: Optional[str] = None
    beneficiary_details: Optional[str] = None
    funds_usage_plan: Optional[str] = None
    transparency_reports: List[Dict] = []
    
    # Pour PETITION
    target_authority: Optional[str] = None
    target_email: Optional[str] = None
    petition_text: Optional[str] = None
    
    # Engagement
    supporters_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    
    # Résultats
    success_story: Optional[str] = None
    impact_achieved: Optional[str] = None
    
    is_public: bool = True
    is_featured: bool = False
    is_verified: bool = False
    
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Signature schemas
class SignatureCreate(BaseModel):
    full_name: str = Field(..., max_length=200)
    email: EmailStr
    city: Optional[str] = None
    country: Optional[str] = None
    message: Optional[str] = None
    is_public: bool = True
    is_anonymous: bool = False


class SignatureResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    user_id: Optional[UUID] = None
    full_name: str
    email: str
    city: Optional[str] = None
    country: Optional[str] = None
    message: Optional[str] = None
    is_public: bool
    is_anonymous: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Donation schemas
class DonationCreate(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = "EUR"
    donor_name: Optional[str] = None
    donor_email: Optional[EmailStr] = None
    message: Optional[str] = None
    is_public: bool = True
    is_anonymous: bool = False
    tax_receipt_requested: bool = False
    
    @validator('currency')
    def validate_currency(cls, v):
        if v not in ['EUR', 'USD', 'GBP']:
            raise ValueError('Currency must be EUR, USD, or GBP')
        return v


class DonationResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    user_id: Optional[UUID] = None
    amount: float
    currency: str
    donor_name: Optional[str] = None
    donor_email: Optional[str] = None
    message: Optional[str] = None
    is_public: bool
    is_anonymous: bool
    payment_status: str
    tax_receipt_requested: bool
    tax_receipt_sent: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Campaign Update schemas
class CampaignUpdateCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: str
    media_urls: List[str] = Field(default_factory=list)
    update_type: str = "general"  # general, milestone, transparency, thank_you
    
    # Pour rapports de transparence
    funds_used: Optional[float] = Field(None, ge=0)
    funds_usage_details: Optional[str] = None
    receipts: List[str] = Field(default_factory=list)
    
    notify_supporters: bool = True
    
    @validator('update_type')
    def validate_update_type(cls, v):
        valid_types = ['general', 'milestone', 'transparency', 'thank_you']
        if v not in valid_types:
            raise ValueError(f'Update type must be one of: {", ".join(valid_types)}')
        return v


class CampaignUpdateResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    author_id: UUID
    title: Optional[str] = None
    content: str
    media_urls: List[str] = []
    update_type: str
    funds_used: Optional[float] = None
    funds_usage_details: Optional[str] = None
    receipts: List[str] = []
    notify_supporters: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Campaign Stats
class CampaignStats(BaseModel):
    total_supporters: int
    current_amount: float
    goal: float
    percentage: float
    days_remaining: Optional[int] = None
    average_contribution: Optional[float] = None


# Campaign Filters
class CampaignFilters(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    creator_type: Optional[str] = None
    skip: int = 0
    limit: int = 20
