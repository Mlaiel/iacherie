"""Creator Management Schemas for IA Influencer Agent Platform
Professional creator profiles, verification, statistics and subscription management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Set
from uuid import UUID

from pydantic import Field, validator, HttpUrl

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class CreatorCreate(BaseSchema):
    """Schema for creator profile creation."""    
    user_id: UUID = Field(description="Associated user account ID")
    creator_name: str = Field(min_length=2, max_length=100, description="Creator display name")
    creator_type: str = Field(description="Type of creator (musician, blogger, photographer, etc.)")
    genres: List[str] = Field(default_factory=list, description="Content genres/categories")
    bio: str = Field(max_length=1000, description="Creator biography")
    location: Optional[str] = Field(None, description="Creator location")
    website: Optional[HttpUrl] = Field(None, description="Creator website")
    
    # Platform connections
    spotify_artist_id: Optional[str] = Field(None, description="Spotify artist ID")
    youtube_channel_id: Optional[str] = Field(None, description="YouTube channel ID")
    instagram_handle: Optional[str] = Field(None, description="Instagram handle")
    tiktok_handle: Optional[str] = Field(None, description="TikTok handle")
    soundcloud_profile: Optional[str] = Field(None, description="SoundCloud profile")
    
    # Business information
    business_email: Optional[str] = Field(None, description="Business contact email")
    manager_contact: Optional[str] = Field(None, description="Manager contact information")
    label_affiliation: Optional[str] = Field(None, description="Record label or agency")
    
    @validator('creator_type')
    def validate_creator_type(cls, v):
        """Validate creator type."""        allowed_types = {
            'musician', 'singer', 'songwriter', 'producer', 'dj',
            'blogger', 'vlogger', 'podcaster', 'influencer',
            'photographer', 'designer', 'artist', 'comedian',
            'dancer', 'actor', 'writer', 'journalist'
        }
        if v.lower() not in allowed_types:
            raise ValueError(f'Creator type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class CreatorUpdate(BaseSchema):
    """Schema for updating creator profiles."""    
    creator_name: Optional[str] = Field(None, min_length=2, max_length=100)
    creator_type: Optional[str] = None
    genres: Optional[List[str]] = None
    bio: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = None
    website: Optional[HttpUrl] = None
    business_email: Optional[str] = None
    manager_contact: Optional[str] = None
    label_affiliation: Optional[str] = None


class CreatorOut(UUIDSchema, TimestampSchema):
    """Public creator profile schema."""    
    user_id: UUID
    creator_name: str
    creator_type: str
    genres: List[str]
    bio: str
    location: Optional[str]
    website: Optional[str]
    profile_image_url: Optional[str]
    banner_image_url: Optional[str]
    
    # Verification status
    is_verified: bool = Field(default=False)
    verification_tier: str = Field(default="none")  # none, basic, premium, enterprise
    verification_badges: List[str] = Field(default_factory=list)
    
    # Statistics
    follower_count: int = Field(default=0, ge=0)
    total_content: int = Field(default=0, ge=0)
    total_views: int = Field(default=0, ge=0)
    total_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Platform connections (public info only)
    connected_platforms: List[str] = Field(default_factory=list)
    
    # Status
    is_active: bool = Field(default=True)
    subscription_tier: str = Field(default="free")
    
    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate."""        if self.follower_count == 0:
            return 0.0
        return min(1.0, self.total_views / (self.follower_count * 100))


class CreatorProfile(UUIDSchema, TimestampSchema, AuditSchema):
    """Extended creator profile with private information."""    
    user_id: UUID
    creator_name: str
    creator_type: str
    genres: List[str]
    bio: str
    location: Optional[str]
    website: Optional[str]
    
    # Private business information
    business_email: Optional[str]
    manager_contact: Optional[str]
    label_affiliation: Optional[str]
    tax_id: Optional[str] = Field(None, description="Tax identification number")
    business_address: Optional[str] = Field(None, description="Business address")
    
    # Platform integrations (private)
    platform_integrations: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Platform API keys and tokens"
    )
    
    # Creator preferences
    content_preferences: Dict[str, any] = Field(default_factory=dict)
    collaboration_preferences: Dict[str, any] = Field(default_factory=dict)
    monetization_preferences: Dict[str, any] = Field(default_factory=dict)
    
    # AI and automation settings
    ai_assistance_enabled: bool = Field(default=True)
    auto_content_optimization: bool = Field(default=True)
    auto_rights_protection: bool = Field(default=True)
    auto_collaboration_matching: bool = Field(default=False)


class CreatorStatistics(UUIDSchema, TimestampSchema):
    """Comprehensive creator performance statistics."""    
    creator_id: UUID
    reporting_period: str = Field(description="Statistics period (daily, weekly, monthly, yearly)")
    period_start: datetime
    period_end: datetime
    
    # Content metrics
    total_content: int = Field(default=0, ge=0)
    new_content: int = Field(default=0, ge=0)
    protected_content: int = Field(default=0, ge=0)
    distributed_content: int = Field(default=0, ge=0)
    
    # Engagement metrics
    total_views: int = Field(default=0, ge=0)
    total_likes: int = Field(default=0, ge=0)
    total_comments: int = Field(default=0, ge=0)
    total_shares: int = Field(default=0, ge=0)
    engagement_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Audience metrics
    follower_count: int = Field(default=0, ge=0)
    follower_growth: int = Field(default=0)
    unique_viewers: int = Field(default=0, ge=0)
    returning_viewers: int = Field(default=0, ge=0)
    
    # Revenue metrics
    total_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    revenue_growth: Decimal = Field(default=Decimal('0.00'))
    revenue_by_platform: Dict[str, Decimal] = Field(default_factory=dict)
    revenue_by_content_type: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Protection metrics
    violations_detected: int = Field(default=0, ge=0)
    takedowns_successful: int = Field(default=0, ge=0)
    recovered_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Collaboration metrics
    active_collaborations: int = Field(default=0, ge=0)
    collaboration_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    partnership_requests: int = Field(default=0, ge=0)
    
    # Geographic data
    top_countries: List[Dict[str, any]] = Field(default_factory=list)
    top_cities: List[Dict[str, any]] = Field(default_factory=list)


class CreatorSubscription(UUIDSchema, TimestampSchema):
    """Creator subscription and billing schema."""    
    creator_id: UUID
    subscription_tier: str = Field(description="Subscription tier")
    billing_period: str = Field(description="Billing period (monthly, yearly)")
    price: Decimal = Field(ge=0, description="Subscription price")
    currency: str = Field(default="EUR", max_length=3)
    
    # Subscription status
    status: str = Field(description="Subscription status")
    is_active: bool = Field(default=True)
    auto_renew: bool = Field(default=True)
    
    # Billing information
    current_period_start: datetime
    current_period_end: datetime
    next_billing_date: Optional[datetime]
    last_payment_date: Optional[datetime]
    
    # Features and limits
    features_included: List[str] = Field(default_factory=list)
    upload_limit_gb: Optional[int] = Field(None, ge=0)
    content_limit: Optional[int] = Field(None, ge=0)
    collaborator_limit: Optional[int] = Field(None, ge=0)
    api_requests_limit: Optional[int] = Field(None, ge=0)
    
    # Payment information
    payment_method_id: Optional[str] = Field(None, description="Payment method identifier")
    payment_provider: Optional[str] = Field(None, description="Payment provider")
    
    # Discounts and promotions
    discount_code: Optional[str] = Field(None, description="Applied discount code")
    discount_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    @validator('subscription_tier')
    def validate_subscription_tier(cls, v):
        """Validate subscription tier."""        allowed_tiers = {'free', 'creator', 'professional', 'enterprise', 'custom'}
        if v not in allowed_tiers:
            raise ValueError(f'Subscription tier must be one of: {", ".join(allowed_tiers)}')
        return v
    
    @property
    def days_until_renewal(self) -> int:
        """Days until next billing."""        if not self.next_billing_date:
            return 0
        return max(0, (self.next_billing_date - datetime.utcnow()).days)


class CreatorVerification(UUIDSchema, TimestampSchema):
    """Creator verification and identity confirmation."""    
    creator_id: UUID
    verification_type: str = Field(description="Type of verification requested")
    verification_status: str = Field(description="Current verification status")
    verification_tier: str = Field(description="Target verification tier")
    
    # Identity verification
    identity_documents: List[Dict[str, str]] = Field(default_factory=list)
    identity_verified: bool = Field(default=False)
    identity_verified_at: Optional[datetime] = None
    
    # Platform verification
    platform_verifications: Dict[str, Dict[str, any]] = Field(default_factory=dict)
    
    # Content authenticity verification
    content_samples: List[str] = Field(default_factory=list, description="Sample content for verification")
    content_verified: bool = Field(default=False)
    content_verified_at: Optional[datetime] = None
    
    # Business verification (for professional tiers)
    business_documents: List[Dict[str, str]] = Field(default_factory=list)
    business_verified: bool = Field(default=False)
    business_verified_at: Optional[datetime] = None
    
    # Verification notes and communication
    verification_notes: List[Dict[str, str]] = Field(default_factory=list)
    reviewer_id: Optional[UUID] = Field(None, description="ID of verification reviewer")
    review_completed_at: Optional[datetime] = None
    
    # Badge and credential information
    earned_badges: List[str] = Field(default_factory=list)
    credentials: Dict[str, any] = Field(default_factory=dict)
    
    @validator('verification_status')
    def validate_verification_status(cls, v):
        """Validate verification status."""        allowed_statuses = {
            'pending', 'under_review', 'approved', 'rejected', 
            'expired', 'suspended', 'revoked'
        }
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class CollaborationPreferences(BaseSchema):
    """Creator collaboration preferences schema."""    
    open_to_collaborations: bool = Field(default=True)
    collaboration_types: List[str] = Field(default_factory=list)
    preferred_genres: List[str] = Field(default_factory=list)
    geographic_preferences: List[str] = Field(default_factory=list)
    experience_level_preferences: List[str] = Field(default_factory=list)
    revenue_sharing_preferences: Dict[str, float] = Field(default_factory=dict)
    communication_preferences: Dict[str, bool] = Field(default_factory=dict)


class MonetizationPreferences(BaseSchema):
    """Creator monetization preferences schema."""    
    auto_monetization_enabled: bool = Field(default=False)
    preferred_revenue_models: List[str] = Field(default_factory=list)
    minimum_payout_threshold: Decimal = Field(default=Decimal('10.00'), ge=0)
    preferred_payment_methods: List[str] = Field(default_factory=list)
    tax_withholding_preferences: Dict[str, any] = Field(default_factory=dict)
    licensing_preferences: Dict[str, any] = Field(default_factory=dict)
