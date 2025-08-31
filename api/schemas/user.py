"""User Management Schemas for IA Influencer Agent Platform
Professional user authentication, profile, and session management schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class UserAuthentication(BaseSchema):
    """User authentication credentials schema."""    
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password")
    remember_me: bool = Field(default=False, description="Remember user session")
    

class UserCreate(BaseSchema):
    """Schema for creating new user accounts."""    
    email: EmailStr = Field(description="Unique user email address")
    password: str = Field(min_length=8, description="User password")
    first_name: str = Field(min_length=2, max_length=50, description="User first name")
    last_name: str = Field(min_length=2, max_length=50, description="User last name")
    username: str = Field(min_length=3, max_length=30, description="Unique username")
    phone_number: Optional[str] = Field(None, description="Phone number with country code")
    country_code: str = Field(default="DE", max_length=2, description="ISO country code")
    language: str = Field(default="en", max_length=5, description="Preferred language")
    timezone: str = Field(default="UTC", description="User timezone")
    terms_accepted: bool = Field(description="User accepted terms and conditions")
    privacy_accepted: bool = Field(description="User accepted privacy policy")
    marketing_consent: bool = Field(default=False, description="Marketing communications consent")
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower()
    
    @validator('terms_accepted', 'privacy_accepted')
    def validate_required_consents(cls, v):
        """Validate required legal consents."""        if not v:
            raise ValueError('Terms and privacy policy must be accepted')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating user information."""    
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone_number: Optional[str] = None
    country_code: Optional[str] = Field(None, max_length=2)
    language: Optional[str] = Field(None, max_length=5)
    timezone: Optional[str] = None
    marketing_consent: Optional[bool] = None


class UserOut(UUIDSchema, TimestampSchema):
    """Public user information schema."""    
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_creator: bool
    country_code: str
    language: str
    timezone: str
    last_login: Optional[datetime]
    profile_image_url: Optional[str]
    
    @property
    def display_name(self) -> str:
        """Get user display name."""        return f"{self.first_name} {self.last_name}"


class UserProfile(UUIDSchema, TimestampSchema):
    """Extended user profile schema."""    
    user_id: UUID
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    website: Optional[str] = Field(None, description="Personal website URL")
    social_links: Dict[str, str] = Field(default_factory=dict, description="Social media links")
    interests: List[str] = Field(default_factory=list, description="User interests and tags")
    skills: List[str] = Field(default_factory=list, description="Professional skills")
    location: Optional[str] = Field(None, description="User location")
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, description="Gender identity")
    profession: Optional[str] = Field(None, description="Professional title")
    company: Optional[str] = Field(None, description="Company or organization")
    
    # Privacy settings
    profile_visibility: str = Field(default="public", description="Profile visibility setting")
    show_email: bool = Field(default=False, description="Show email publicly")
    show_location: bool = Field(default=True, description="Show location publicly")
    
    # Statistics
    follower_count: int = Field(default=0, ge=0)
    following_count: int = Field(default=0, ge=0)
    content_count: int = Field(default=0, ge=0)
    
    @validator('social_links')
    def validate_social_links(cls, v):
        """Validate social media links format."""        allowed_platforms = {
            'twitter', 'instagram', 'facebook', 'linkedin', 
            'youtube', 'tiktok', 'spotify', 'soundcloud'
        }
        for platform in v.keys():
            if platform not in allowed_platforms:
                raise ValueError(f'Unsupported social platform: {platform}')
        return v


class UserSettings(UUIDSchema, TimestampSchema):
    """User application settings schema."""    
    user_id: UUID
    
    # Notification preferences
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=True)
    marketing_emails: bool = Field(default=False)
    collaboration_requests: bool = Field(default=True)
    content_violations: bool = Field(default=True)
    revenue_updates: bool = Field(default=True)
    
    # Privacy settings
    profile_searchable: bool = Field(default=True)
    content_indexable: bool = Field(default=True)
    analytics_tracking: bool = Field(default=True)
    data_sharing: bool = Field(default=False)
    
    # Platform preferences
    default_upload_privacy: str = Field(default="private")
    auto_protection_enabled: bool = Field(default=True)
    auto_seo_optimization: bool = Field(default=True)
    auto_distribution: bool = Field(default=False)
    
    # Advanced features
    ai_recommendations: bool = Field(default=True)
    collaboration_matching: bool = Field(default=True)
    automatic_monetization: bool = Field(default=False)
    blockchain_verification: bool = Field(default=False)


class UserVerification(UUIDSchema, TimestampSchema):
    """User verification status schema."""    
    user_id: UUID
    verification_type: str = Field(description="Type of verification")
    verification_status: str = Field(description="Current verification status")
    verification_code: Optional[str] = Field(None, description="Verification code")
    verification_token: Optional[str] = Field(None, description="Verification token")
    verified_at: Optional[datetime] = Field(None, description="Verification completion timestamp")
    expires_at: Optional[datetime] = Field(None, description="Verification expiration")
    attempts_count: int = Field(default=0, ge=0, description="Number of verification attempts")
    max_attempts: int = Field(default=5, ge=1, description="Maximum allowed attempts")
    verification_data: Dict[str, any] = Field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if verification is expired."""        return self.expires_at and datetime.utcnow() > self.expires_at
    
    @property
    def attempts_remaining(self) -> int:
        """Get remaining verification attempts."""        return max(0, self.max_attempts - self.attempts_count)


class UserSession(UUIDSchema, TimestampSchema):
    """User session management schema."""    
    user_id: UUID
    session_id: str = Field(description="Unique session identifier")
    device_type: str = Field(description="Device type (web, mobile, api)")
    device_id: Optional[str] = Field(None, description="Unique device identifier")
    ip_address: str = Field(description="Client IP address")
    user_agent: str = Field(description="Client user agent")
    location: Optional[str] = Field(None, description="Approximate location")
    
    # Session status
    is_active: bool = Field(default=True, description="Session active status")
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(description="Session expiration timestamp")
    
    # Security features
    requires_2fa: bool = Field(default=False, description="Requires two-factor authentication")
    is_trusted_device: bool = Field(default=False, description="Trusted device status")
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Session risk score")
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""        return datetime.utcnow() > self.expires_at
    
    @property
    def time_since_last_activity(self) -> int:
        """Get seconds since last activity."""        return int((datetime.utcnow() - self.last_activity).total_seconds())


class PasswordChange(BaseSchema):
    """Password change request schema."""    
    current_password: str = Field(description="Current password")
    new_password: str = Field(min_length=8, description="New password")
    confirm_password: str = Field(description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate password confirmation matches."""        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordReset(BaseSchema):
    """Password reset request schema."""    
    email: EmailStr = Field(description="User email for password reset")
    

class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""    
    token: str = Field(description="Password reset token")
    new_password: str = Field(min_length=8, description="New password")
    confirm_password: str = Field(description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate password confirmation matches."""        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class TwoFactorSetup(BaseSchema):
    """Two-factor authentication setup schema."""    
    method: str = Field(description="2FA method (totp, sms, email)")
    phone_number: Optional[str] = Field(None, description="Phone number for SMS")
    backup_codes: List[str] = Field(default_factory=list, description="Backup codes")


class TwoFactorVerify(BaseSchema):
    """Two-factor authentication verification schema."""    
    code: str = Field(min_length=6, max_length=8, description="2FA verification code")
    backup_code: Optional[str] = Field(None, description="Backup code if primary fails")
    remember_device: bool = Field(default=False, description="Remember this device")
