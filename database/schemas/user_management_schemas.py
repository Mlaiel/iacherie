"""
User Management and Profile Schemas

Comprehensive Pydantic schemas for user management, profile data,
and user preferences in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr, HttpUrl
from pydantic.types import PositiveInt, PositiveFloat


class UserRoleEnum(str, Enum):
    """User roles in the platform"""
    ARTIST = "artist"
    PRODUCER = "producer"
    SONGWRITER = "songwriter"
    VOCALIST = "vocalist"
    INSTRUMENTALIST = "instrumentalist"
    DJ = "dj"
    PODCASTER = "podcaster"
    CONTENT_CREATOR = "content_creator"
    INFLUENCER = "influencer"
    MUSIC_LABEL = "music_label"
    MUSIC_PUBLISHER = "music_publisher"
    BOOKING_AGENT = "booking_agent"
    MUSIC_MANAGER = "music_manager"
    SOUND_ENGINEER = "sound_engineer"
    MUSIC_JOURNALIST = "music_journalist"
    RADIO_DJ = "radio_dj"
    PLAYLIST_CURATOR = "playlist_curator"
    MUSIC_EDUCATOR = "music_educator"
    FAN = "fan"
    ADMINISTRATOR = "administrator"


class AccountStatusEnum(str, Enum):
    """Account status"""
    ACTIVE = "active"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    BANNED = "banned"
    DELETED = "deleted"
    UNDER_REVIEW = "under_review"


class SubscriptionTierEnum(str, Enum):
    """Subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class VerificationStatusEnum(str, Enum):
    """Verification status types"""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class NotificationTypeEnum(str, Enum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class PrivacyLevelEnum(str, Enum):
    """Privacy levels"""
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"
    CUSTOM = "custom"


class ContactInformationSchema(BaseModel):
    """Schema for contact information"""
    primary_email: EmailStr = Field(..., description="Primary email address")
    secondary_email: Optional[EmailStr] = Field(None, description="Secondary email address")
    phone_primary: Optional[str] = Field(None, description="Primary phone number")
    phone_secondary: Optional[str] = Field(None, description="Secondary phone number")
    website: Optional[HttpUrl] = Field(None, description="Personal/professional website")
    
    # Address information
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state_province: Optional[str] = Field(None, description="State or province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    
    # Emergency contact
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    emergency_contact_relationship: Optional[str] = Field(None, description="Relationship to emergency contact")
    
    class Config:
        json_schema_extra = {
            "example": {
                "primary_email": "artist@example.com",
                "phone_primary": "+49123456789",
                "website": "https://artistname.com",
                "city": "Berlin",
                "country": "Germany"
            }
        }


class ProfessionalInformationSchema(BaseModel):
    """Schema for professional information"""
    # Basic professional details
    stage_name: Optional[str] = Field(None, description="Stage/professional name")
    legal_name: Optional[str] = Field(None, description="Legal name")
    biography: Optional[str] = Field(None, max_length=2000, description="Professional biography")
    genres: List[str] = Field([], description="Musical genres")
    instruments: List[str] = Field([], description="Instruments played")
    
    # Career information
    career_start_year: Optional[int] = Field(None, ge=1950, le=2030, description="Career start year")
    years_experience: Optional[int] = Field(None, ge=0, description="Years of experience")
    record_label: Optional[str] = Field(None, description="Current record label")
    management_company: Optional[str] = Field(None, description="Management company")
    booking_agency: Optional[str] = Field(None, description="Booking agency")
    publisher: Optional[str] = Field(None, description="Music publisher")
    
    # Professional credentials
    education: Optional[List[str]] = Field(None, description="Educational background")
    certifications: Optional[List[str]] = Field(None, description="Professional certifications")
    awards: Optional[List[str]] = Field(None, description="Awards and recognition")
    notable_collaborations: Optional[List[str]] = Field(None, description="Notable collaborations")
    
    # Business information
    business_name: Optional[str] = Field(None, description="Business name")
    tax_id: Optional[str] = Field(None, description="Tax identification number")
    vat_number: Optional[str] = Field(None, description="VAT number")
    business_type: Optional[str] = Field(None, description="Type of business entity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stage_name": "Electronic Producer",
                "genres": ["electronic", "techno", "house"],
                "instruments": ["synthesizer", "drum_machine"],
                "career_start_year": 2018,
                "years_experience": 6,
                "education": ["Music Production Certification"]
            }
        }


class SocialMediaProfilesSchema(BaseModel):
    """Schema for social media profiles"""
    spotify_artist_id: Optional[str] = Field(None, description="Spotify artist ID")
    apple_music_id: Optional[str] = Field(None, description="Apple Music artist ID")
    youtube_channel_id: Optional[str] = Field(None, description="YouTube channel ID")
    soundcloud_username: Optional[str] = Field(None, description="SoundCloud username")
    bandcamp_username: Optional[str] = Field(None, description="Bandcamp username")
    
    # Social platforms
    instagram_username: Optional[str] = Field(None, description="Instagram username")
    twitter_username: Optional[str] = Field(None, description="Twitter/X username")
    facebook_page: Optional[str] = Field(None, description="Facebook page")
    tiktok_username: Optional[str] = Field(None, description="TikTok username")
    linkedin_profile: Optional[str] = Field(None, description="LinkedIn profile")
    
    # Professional platforms
    discogs_artist_id: Optional[str] = Field(None, description="Discogs artist ID")
    beatport_artist_id: Optional[str] = Field(None, description="Beatport artist ID")
    mixcloud_username: Optional[str] = Field(None, description="Mixcloud username")
    
    # Custom profiles
    custom_profiles: Optional[Dict[str, str]] = Field(None, description="Other platform profiles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "spotify_artist_id": "1ABC23DEF456",
                "instagram_username": "electronic_producer",
                "youtube_channel_id": "UCAbC123dEf456",
                "soundcloud_username": "electronicproducer"
            }
        }


class UserPreferencesSchema(BaseModel):
    """Schema for user preferences and settings"""
    # Notification preferences
    email_notifications: bool = Field(True, description="Enable email notifications")
    sms_notifications: bool = Field(False, description="Enable SMS notifications")
    push_notifications: bool = Field(True, description="Enable push notifications")
    marketing_emails: bool = Field(False, description="Enable marketing emails")
    
    # Notification types
    content_upload_notifications: bool = Field(True, description="Content upload notifications")
    collaboration_notifications: bool = Field(True, description="Collaboration notifications")
    protection_alert_notifications: bool = Field(True, description="Protection alert notifications")
    revenue_notifications: bool = Field(True, description="Revenue notifications")
    platform_news: bool = Field(False, description="Platform news and updates")
    
    # Privacy preferences
    profile_visibility: PrivacyLevelEnum = Field(PrivacyLevelEnum.PUBLIC, description="Profile visibility")
    contact_visibility: PrivacyLevelEnum = Field(PrivacyLevelEnum.FRIENDS, description="Contact info visibility")
    activity_visibility: PrivacyLevelEnum = Field(PrivacyLevelEnum.PUBLIC, description="Activity visibility")
    collaboration_visibility: bool = Field(True, description="Show collaboration history")
    
    # Content preferences
    auto_fingerprinting: bool = Field(True, description="Automatic content fingerprinting")
    auto_protection: bool = Field(True, description="Automatic protection monitoring")
    auto_monetization: bool = Field(False, description="Automatic monetization")
    content_backup: bool = Field(True, description="Automatic content backup")
    
    # Platform preferences
    preferred_language: str = Field("en", description="Preferred language")
    preferred_timezone: str = Field("UTC", description="Preferred timezone")
    preferred_currency: str = Field("EUR", description="Preferred currency")
    date_format: str = Field("YYYY-MM-DD", description="Preferred date format")
    
    # AI and analytics preferences
    ai_recommendations: bool = Field(True, description="Enable AI recommendations")
    analytics_tracking: bool = Field(True, description="Enable analytics tracking")
    market_insights: bool = Field(True, description="Enable market insights")
    trend_notifications: bool = Field(False, description="Trend notifications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email_notifications": True,
                "push_notifications": True,
                "profile_visibility": "public",
                "auto_protection": True,
                "preferred_language": "en",
                "preferred_currency": "EUR"
            }
        }


class VerificationDocumentSchema(BaseModel):
    """Schema for verification documents"""
    document_id: str = Field(..., description="Unique document identifier")
    document_type: str = Field(..., description="Type of document")
    document_url: str = Field(..., description="Document file URL")
    file_hash: str = Field(..., description="Document file hash for integrity")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    verified_by: Optional[str] = Field(None, description="Verified by (user/system)")
    verification_status: VerificationStatusEnum = Field(..., description="Verification status")
    expiry_date: Optional[date] = Field(None, description="Document expiry date")
    notes: Optional[str] = Field(None, description="Verification notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "DOC-2024-001234",
                "document_type": "government_id",
                "verification_status": "verified",
                "uploaded_at": "2024-08-24T10:30:00Z",
                "verified_at": "2024-08-24T15:45:00Z"
            }
        }


class UserSubscriptionSchema(BaseModel):
    """Schema for user subscription information"""
    subscription_id: str = Field(..., description="Unique subscription identifier")
    tier: SubscriptionTierEnum = Field(..., description="Subscription tier")
    status: str = Field(..., description="Subscription status")
    
    # Billing information
    monthly_price: Decimal = Field(..., description="Monthly price")
    annual_price: Optional[Decimal] = Field(None, description="Annual price")
    currency: str = Field(..., description="Billing currency")
    billing_cycle: str = Field(..., description="Billing cycle")
    
    # Dates
    start_date: date = Field(..., description="Subscription start date")
    end_date: Optional[date] = Field(None, description="Subscription end date")
    next_billing_date: Optional[date] = Field(None, description="Next billing date")
    trial_end_date: Optional[date] = Field(None, description="Trial end date")
    
    # Features and limits
    features_included: List[str] = Field(..., description="Included features")
    usage_limits: Dict[str, int] = Field(..., description="Usage limits")
    current_usage: Dict[str, int] = Field(..., description="Current usage")
    
    # Payment information
    payment_method: Optional[str] = Field(None, description="Payment method")
    last_payment_date: Optional[date] = Field(None, description="Last payment date")
    next_payment_amount: Optional[Decimal] = Field(None, description="Next payment amount")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subscription_id": "SUB-2024-001234",
                "tier": "professional",
                "status": "active",
                "monthly_price": "29.99",
                "currency": "EUR",
                "billing_cycle": "monthly",
                "start_date": "2024-08-01"
            }
        }


class UserBaseSchema(BaseModel):
    """Base schema for user information"""
    # Basic information
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Primary email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    
    # Profile information
    avatar_url: Optional[str] = Field(None, description="Profile avatar URL")
    cover_image_url: Optional[str] = Field(None, description="Profile cover image URL")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, description="Gender")
    
    # Platform information
    user_roles: List[UserRoleEnum] = Field(..., description="User roles on platform")
    primary_role: UserRoleEnum = Field(..., description="Primary user role")
    
    # Contact and professional info
    contact_info: ContactInformationSchema = Field(..., description="Contact information")
    professional_info: Optional[ProfessionalInformationSchema] = Field(None, description="Professional information")
    social_media: Optional[SocialMediaProfilesSchema] = Field(None, description="Social media profiles")
    
    # Preferences and settings
    preferences: UserPreferencesSchema = Field(..., description="User preferences")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.lower()


class UserCreateSchema(UserBaseSchema):
    """Schema for creating users"""
    password: str = Field(..., min_length=8, description="User password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    # Registration options
    terms_accepted: bool = Field(..., description="Terms and conditions accepted")
    privacy_policy_accepted: bool = Field(..., description="Privacy policy accepted")
    marketing_consent: bool = Field(False, description="Marketing communications consent")
    
    # Initial setup
    skip_onboarding: bool = Field(False, description="Skip onboarding process")
    referral_code: Optional[str] = Field(None, description="Referral code")
    utm_source: Optional[str] = Field(None, description="UTM source for tracking")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, values):
        """Validate password confirmation"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "electronic_artist",
                "email": "artist@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePassword123!",
                "confirm_password": "SecurePassword123!",
                "user_roles": ["artist", "producer"],
                "primary_role": "artist",
                "terms_accepted": True,
                "privacy_policy_accepted": True
            }
        }


class UserUpdateSchema(BaseModel):
    """Schema for updating user information"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated last name")
    avatar_url: Optional[str] = Field(None, description="Updated avatar URL")
    cover_image_url: Optional[str] = Field(None, description="Updated cover image URL")
    
    # Contact and professional updates
    contact_info: Optional[ContactInformationSchema] = Field(None, description="Updated contact information")
    professional_info: Optional[ProfessionalInformationSchema] = Field(None, description="Updated professional information")
    social_media: Optional[SocialMediaProfilesSchema] = Field(None, description="Updated social media profiles")
    preferences: Optional[UserPreferencesSchema] = Field(None, description="Updated preferences")
    
    # Role updates
    user_roles: Optional[List[UserRoleEnum]] = Field(None, description="Updated user roles")
    primary_role: Optional[UserRoleEnum] = Field(None, description="Updated primary role")
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "user_roles": ["artist", "producer", "dj"],
                "primary_role": "producer"
            }
        }


class UserResponseSchema(UserBaseSchema):
    """Schema for user responses"""
    id: PositiveInt = Field(..., description="Unique user ID")
    user_reference: str = Field(..., description="Human-readable user reference")
    
    # Account status
    account_status: AccountStatusEnum = Field(..., description="Account status")
    is_verified: bool = Field(False, description="Overall verification status")
    verification_level: str = Field("basic", description="Verification level")
    
    # Verification details
    email_verified: bool = Field(False, description="Email verification status")
    phone_verified: bool = Field(False, description="Phone verification status")
    identity_verified: bool = Field(False, description="Identity verification status")
    verification_documents: List[VerificationDocumentSchema] = Field([], description="Verification documents")
    
    # Subscription information
    subscription: Optional[UserSubscriptionSchema] = Field(None, description="Subscription information")
    
    # Activity and engagement
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(0, description="Total login count")
    content_uploads: int = Field(0, description="Number of content uploads")
    collaborations_count: int = Field(0, description="Number of collaborations")
    
    # Reputation and social proof
    reputation_score: float = Field(0.0, ge=0.0, le=5.0, description="Reputation score")
    follower_count: int = Field(0, description="Number of followers")
    following_count: int = Field(0, description="Number of following")
    verified_badge: bool = Field(False, description="Verified badge status")
    
    # Financial information
    total_revenue: Decimal = Field(Decimal('0.00'), description="Total revenue earned")
    pending_revenue: Decimal = Field(Decimal('0.00'), description="Pending revenue")
    total_licensing_deals: int = Field(0, description="Total licensing deals")
    
    # Platform metrics
    profile_views: int = Field(0, description="Profile view count")
    content_views: int = Field(0, description="Total content views")
    engagement_rate: float = Field(0.0, description="Average engagement rate")
    
    # Timestamps
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    email_verified_at: Optional[datetime] = Field(None, description="Email verification timestamp")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    # Privacy note: Sensitive fields like password are excluded from response
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "user_reference": "USER-2024-001234",
                "username": "electronic_artist",
                "email": "artist@example.com",
                "account_status": "active",
                "is_verified": True,
                "verification_level": "professional",
                "reputation_score": 4.8,
                "follower_count": 15000,
                "total_revenue": "5750.00",
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class UserListSchema(BaseModel):
    """Schema for listing users"""
    users: List[UserResponseSchema] = Field(..., description="List of users")
    total_count: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_previous: bool = Field(..., description="Whether there's a previous page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "users": [],
                "total_count": 15000,
                "page": 1,
                "per_page": 20,
                "total_pages": 750,
                "has_next": True,
                "has_previous": False
            }
        }


class UserSearchSchema(BaseModel):
    """Schema for user search requests"""
    query: Optional[str] = Field(None, description="Search query")
    user_roles: Optional[List[UserRoleEnum]] = Field(None, description="Filter by user roles")
    verification_status: Optional[List[VerificationStatusEnum]] = Field(None, description="Filter by verification")
    account_status: Optional[List[AccountStatusEnum]] = Field(None, description="Filter by account status")
    subscription_tiers: Optional[List[SubscriptionTierEnum]] = Field(None, description="Filter by subscription")
    genres: Optional[List[str]] = Field(None, description="Filter by musical genres")
    location: Optional[str] = Field(None, description="Filter by location")
    registration_date_from: Optional[date] = Field(None, description="Registration date from")
    registration_date_to: Optional[date] = Field(None, description="Registration date to")
    min_reputation: Optional[float] = Field(None, description="Minimum reputation score")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "electronic producer",
                "user_roles": ["artist", "producer"],
                "verification_status": ["verified"],
                "genres": ["electronic", "techno"],
                "min_reputation": 4.0,
                "sort_by": "reputation_score",
                "sort_order": "desc"
            }
        }


# Export schemas
__all__ = [
    # Enums
    "UserRoleEnum",
    "AccountStatusEnum",
    "SubscriptionTierEnum",
    "VerificationStatusEnum",
    "NotificationTypeEnum",
    "PrivacyLevelEnum",
    
    # Complex schemas
    "ContactInformationSchema",
    "ProfessionalInformationSchema",
    "SocialMediaProfilesSchema",
    "UserPreferencesSchema",
    "VerificationDocumentSchema",
    "UserSubscriptionSchema",
    
    # Main schemas
    "UserBaseSchema",
    "UserCreateSchema",
    "UserUpdateSchema",
    "UserResponseSchema",
    "UserListSchema",
    "UserSearchSchema"
]
