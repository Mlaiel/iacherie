"""{{model_name}} Pydantic Model Template for Ainflue Platform
{{model_description}}

Enterprise-grade Pydantic models with comprehensive validation, serialization,
nested schemas, custom validators, and API integration.

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Role: DBA + Data Validation Expert
"""

import logging
from typing import Dict, Any, Optional, List, Union, Set, Tuple, ForwardRef
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from uuid import UUID
import re
import json
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse

from pydantic import (
    BaseModel, Field, validator, root_validator, ValidationError,
    EmailStr, HttpUrl, AnyHttpUrl, IPvAnyAddress, constr, conint, 
    confloat, condecimal, conlist, conset, Json, SecretStr
)
from pydantic.color import Color
from pydantic.types import PositiveInt, PositiveFloat, NonNegativeInt, StrictStr
from pydantic.validators import str_validator
from pydantic.fields import ModelField

logger = logging.getLogger(__name__)


# Custom field types and validators
class PhoneNumberStr(str):
    """Custom phone number validation"""
    
    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate
    
    @classmethod
    def validate(cls, v) -> None:
        if not isinstance(v, str):
            raise TypeError('Phone number must be a string')
        
        # Remove all non-digits
        digits_only = re.sub(r'\D', '', v)
        
        # Validate phone number format
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        
        # Additional format validation
        phone_patterns = [
            r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$',  # US format
            r'^\+?[1-9]\d{1,14}$',                  # International format
        ]
        
        if not any(re.match(pattern, digits_only) for pattern in phone_patterns):
            raise ValueError('Invalid phone number format')
        
        return f"+{digits_only}"


class UsernameStr(str):
    """Custom username validation"""
    
    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate
    
    @classmethod
    def validate(cls, v) -> None:
        if not isinstance(v, str):
            raise TypeError('Username must be a string')
        
        v = v.strip().lower()
        
        # Username validation rules
        if len(v) < 3 or len(v) > 30:
            raise ValueError('Username must be between 3 and 30 characters')
        
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError('Username can only contain lowercase letters, numbers, and underscores')
        
        if v.startswith('_') or v.endswith('_'):
            raise ValueError('Username cannot start or end with underscore')
        
        if '__' in v:
            raise ValueError('Username cannot contain consecutive underscores')
        
        # Reserved usernames
        reserved = [
            'admin', 'administrator', 'root', 'system', 'api', 'www', 'mail',
            'support', 'help', 'info', 'contact', 'about', 'terms', 'privacy',
            'security', 'login', 'register', 'signup', 'signin', 'logout',
            'profile', 'account', 'settings', 'dashboard', 'upload', 'download'
        ]
        
        if v in reserved:
            raise ValueError(f'Username "{v}" is reserved')
        
        return v


class PasswordStr(SecretStr):
    """Custom password validation"""
    
    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate
    
    @classmethod
    def validate(cls, v) -> None:
        if not isinstance(v, str):
            raise TypeError('Password must be a string')
        
        # Password strength validation
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        
        # Check for required character types
        has_lower = bool(re.search(r'[a-z]', v))
        has_upper = bool(re.search(r'[A-Z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', v))
        
        if not (has_lower and has_upper and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one lowercase letter, '
                'one uppercase letter, one digit, and one special character'
            )
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '12345678', 'qwerty123', 'admin123', 'letmein',
            'welcome123', 'password123', 'administrator'
        ]
        
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common')
        
        return cls(v)


class ColorCodeStr(str):
    """Custom color code validation"""
    
    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate
    
    @classmethod
    def validate(cls, v) -> None:
        if not isinstance(v, str):
            raise TypeError('Color code must be a string')
        
        # Validate hex color code
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', v):
            raise ValueError('Invalid hex color code format')
        
        return v.upper()


# Common enumerations
class AccountStatus(str, Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"
    DELETED = "deleted"


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    CREATOR = "creator"
    USER = "user"
    GUEST = "guest"


class ContentType(str, Enum):
    """Content type enumeration"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"


class PrivacyLevel(str, Enum):
    """Privacy level enumeration"""
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    FRIENDS_ONLY = "friends_only"
    SUBSCRIBERS_ONLY = "subscribers_only"


# Base model with common functionality
class {{base_model_class}}(BaseModel):
    """
    Base Pydantic model with common functionality
    
    Provides:
    - Automatic timestamps
    - UUID generation
    - Common validation
    - Serialization helpers
    - Metadata support
    """
    
    class Config:
    """Config: class implementation"""
        # Enable field validation on assignment
        validate_assignment = True
        
        # Use enum values instead of names
        use_enum_values = True
        
        # Allow population by field name or alias
        allow_population_by_field_name = True
        
        # Validate default values
        validate_all = True
        
        # Enable arbitrary types
        arbitrary_types_allowed = True
        
        # JSON encoding
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            time: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: str(v) if v else None,
            UUID: lambda v: str(v) if v else None,
            set: list,
        }
        
        # Field aliases for API compatibility
        alias_generator = None
        
        # Schema extras
        schema_extra = {
            "example": {}
        }
    
    # Common fields
    id: Optional[str] = Field(
        None, 
        description="Unique identifier",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    
    created_at: Optional[datetime] = Field(
        None,
        description="Creation timestamp",
        example="2023-01-01T00:00:00Z"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp", 
        example="2023-01-01T00:00:00Z"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata",
        example={"source": "api", "version": "1.0"}
    )
    
    @validator('id', pre=True, always=True)
    def validate_id(cls, v) -> None:
        """Validate and generate ID if not provided"""
        if v is None:
            import uuid
            return str(uuid.uuid4())
        
        # Validate UUID format
        try:
            UUID(v)
            return str(v)
        except ValueError:
            # Allow other ID formats but validate length
            if not isinstance(v, str) or len(v) < 1 or len(v) > 100:
                raise ValueError('ID must be a valid UUID or string between 1 and 100 characters')
            return v
    
    @validator('created_at', pre=True, always=True)
    def validate_created_at(cls, v) -> None:
        """Set creation timestamp if not provided"""
        if v is None:
            return datetime.utcnow()
        return v
    
    @validator('updated_at', pre=True, always=True)
    def validate_updated_at(cls, v) -> None:
        """Set update timestamp if not provided"""
        if v is None:
            return datetime.utcnow()
        return v
    
    @validator('metadata')
    def validate_metadata(cls, v) -> None:
        """Validate metadata size and content"""
        if v and len(json.dumps(v)) > 10000:  # 10KB limit
            raise ValueError('Metadata size cannot exceed 10KB')
        return v or {}
    
    def dict_for_api(self, **kwargs) -> Dict[str, Any]:
        """
        Export model as dictionary suitable for API responses
        """
        return self.dict(
            exclude_unset=True,
            exclude_none=True,
            by_alias=True,
            **kwargs
        )
    
    def dict_for_db(self, **kwargs) -> Dict[str, Any]:
        """
        Export model as dictionary suitable for database storage
        """
        return self.dict(
            exclude_unset=False,
            exclude_none=False,
            by_alias=False,
            **kwargs
        )
    
    def json_for_api(self, **kwargs) -> str:
        """
        Export model as JSON suitable for API responses
        """
        return self.json(
            exclude_unset=True,
            exclude_none=True,
            by_alias=True,
            **kwargs
        )


# User-related models
class UserProfile({{base_model_class}}):
    """User profile model with comprehensive validation"""
    
    # Basic information
    username: UsernameStr = Field(
        ...,
        description="Unique username",
        example="john_doe"
    )
    
    email: EmailStr = Field(
        ...,
        description="Email address",
        example="john.doe@example.com"
    )
    
    first_name: constr(min_length=1, max_length=50, strip_whitespace=True) = Field(
        ...,
        description="First name",
        example="John"
    )
    
    last_name: constr(min_length=1, max_length=50, strip_whitespace=True) = Field(
        ...,
        description="Last name", 
        example="Doe"
    )
    
    display_name: Optional[constr(min_length=1, max_length=100, strip_whitespace=True)] = Field(
        None,
        description="Display name",
        example="John Doe"
    )
    
    bio: Optional[constr(max_length=1000, strip_whitespace=True)] = Field(
        None,
        description="User biography",
        example="Content creator and digital artist"
    )
    
    # Contact information
    phone: Optional[PhoneNumberStr] = Field(
        None,
        description="Phone number",
        example="+1234567890"
    )
    
    website: Optional[AnyHttpUrl] = Field(
        None,
        description="Personal website",
        example="https://johndoe.com"
    )
    
    # Location
    country: Optional[constr(min_length=2, max_length=2)] = Field(
        None,
        description="Country code (ISO 3166-1 alpha-2)",
        example="US"
    )
    
    city: Optional[constr(max_length=100, strip_whitespace=True)] = Field(
        None,
        description="City name",
        example="New York"
    )
    
    timezone: Optional[constr(max_length=50)] = Field(
        None,
        description="Timezone",
        example="America/New_York"
    )
    
    # Account settings
    role: UserRole = Field(
        UserRole.USER,
        description="User role"
    )
    
    status: AccountStatus = Field(
        AccountStatus.ACTIVE,
        description="Account status"
    )
    
    is_verified: bool = Field(
        False,
        description="Email verification status"
    )
    
    is_premium: bool = Field(
        False,
        description="Premium account status"
    )
    
    # Privacy settings
    privacy_level: PrivacyLevel = Field(
        PrivacyLevel.PUBLIC,
        description="Profile privacy level"
    )
    
    # Profile customization
    avatar_url: Optional[AnyHttpUrl] = Field(
        None,
        description="Avatar image URL",
        example="https://cdn.example.com/avatars/john_doe.jpg"
    )
    
    banner_url: Optional[AnyHttpUrl] = Field(
        None,
        description="Profile banner URL",
        example="https://cdn.example.com/banners/john_doe.jpg"
    )
    
    theme_color: Optional[ColorCodeStr] = Field(
        None,
        description="Profile theme color",
        example="#FF5733"
    )
    
    # Social links
    social_links: Optional[List[Dict[str, Union[str, AnyHttpUrl]]]] = Field(
        default_factory=list,
        description="Social media links",
        example=[
            {"platform": "twitter", "url": "https://twitter.com/johndoe"},
            {"platform": "instagram", "url": "https://instagram.com/johndoe"}
        ]
    )
    
    # Preferences
    language: Optional[constr(min_length=2, max_length=5)] = Field(
        "en",
        description="Preferred language code",
        example="en"
    )
    
    notification_preferences: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {
            "email_notifications": True,
            "push_notifications": True,
            "sms_notifications": False,
            "marketing_emails": False
        },
        description="Notification preferences"
    )
    
    # Statistics (read-only)
    follower_count: NonNegativeInt = Field(
        0,
        description="Number of followers"
    )
    
    following_count: NonNegativeInt = Field(
        0,
        description="Number of users being followed"
    )
    
    content_count: NonNegativeInt = Field(
        0,
        description="Number of content items"
    )
    
    # Timestamps
    last_login_at: Optional[datetime] = Field(
        None,
        description="Last login timestamp"
    )
    
    email_verified_at: Optional[datetime] = Field(
        None,
        description="Email verification timestamp"
    )
    
    class Config({{base_model_class}}.Config):
    """Config class implementation"""
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "display_name": "John Doe",
                "bio": "Content creator and digital artist",
                "phone": "+1234567890",
                "website": "https://johndoe.com",
                "country": "US",
                "city": "New York",
                "timezone": "America/New_York",
                "role": "creator",
                "status": "active",
                "is_verified": True,
                "is_premium": False,
                "privacy_level": "public",
                "avatar_url": "https://cdn.example.com/avatars/john_doe.jpg",
                "theme_color": "#FF5733",
                "social_links": [
                    {"platform": "twitter", "url": "https://twitter.com/johndoe"}
                ],
                "language": "en",
                "follower_count": 1250,
                "following_count": 345,
                "content_count": 67
            }
        }
    
    @validator('display_name', always=True)
    def validate_display_name(cls, v, values) -> None:
        """Generate display name if not provided"""
        if v is None and 'first_name' in values and 'last_name' in values:
            return f"{values['first_name']} {values['last_name']}"
        return v
    
    @validator('social_links')
    def validate_social_links(cls, v) -> None:
        """Validate social media links"""
        if not v:
            return []
        
        allowed_platforms = {
            'twitter', 'instagram', 'facebook', 'youtube', 'tiktok',
            'linkedin', 'github', 'discord', 'twitch', 'spotify'
        }
        
        for link in v:
            if not isinstance(link, dict):
                raise ValueError('Social link must be a dictionary')
            
            if 'platform' not in link or 'url' not in link:
                raise ValueError('Social link must have platform and url fields')
            
            if link['platform'] not in allowed_platforms:
                raise ValueError(f'Platform must be one of: {", ".join(allowed_platforms)}')
            
            # Validate URL format
            try:
                parsed = urlparse(str(link['url']))
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError('Invalid URL format')
            except Exception:
                raise ValueError('Invalid URL format')
        
        return v
    
    @validator('notification_preferences')
    def validate_notification_preferences(cls, v) -> None:
        """Validate notification preferences"""
        if not v:
            return {
                "email_notifications": True,
                "push_notifications": True,
                "sms_notifications": False,
                "marketing_emails": False
            }
        
        required_keys = {
            'email_notifications', 'push_notifications', 
            'sms_notifications', 'marketing_emails'
        }
        
        for key in required_keys:
            if key not in v:
                v[key] = False
            if not isinstance(v[key], bool):
                raise ValueError(f'{key} must be a boolean')
        
        return v
    
    @root_validator
    def validate_user_profile(cls, values) -> None:
        """Root validator for cross-field validation"""
        # Ensure premium users have verified email
        if values.get('is_premium') and not values.get('is_verified'):
            raise ValueError('Premium accounts must have verified email')
        
        # Validate role permissions
        if values.get('role') == UserRole.ADMIN and values.get('status') != AccountStatus.ACTIVE:
            raise ValueError('Admin accounts must be active')
        
        return values


class UserRegistration(BaseModel):
    """User registration model"""
    
    username: UsernameStr = Field(..., description="Desired username")
    email: EmailStr = Field(..., description="Email address")
    password: PasswordStr = Field(..., description="Password")
    first_name: constr(min_length=1, max_length=50, strip_whitespace=True) = Field(..., description="First name")
    last_name: constr(min_length=1, max_length=50, strip_whitespace=True) = Field(..., description="Last name")
    terms_accepted: bool = Field(..., description="Terms of service acceptance")
    marketing_consent: bool = Field(False, description="Marketing email consent")
    referral_code: Optional[constr(max_length=20)] = Field(None, description="Referral code")
    
    @validator('terms_accepted')
    def validate_terms_accepted(cls, v) -> None:
        if not v:
            raise ValueError('Terms of service must be accepted')
        return v
    
    class Config:
    """Config: class implementation"""
        schema_extra = {
            "example": {
                "username": "new_user",
                "email": "new.user@example.com",
                "password": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "terms_accepted": True,
                "marketing_consent": False,
                "referral_code": "FRIEND2023"
            }
        }


class UserLogin(BaseModel):
    """User login model"""
    
    identifier: constr(min_length=1, max_length=100) = Field(
        ..., 
        description="Username or email"
    )
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember login")
    device_info: Optional[Dict[str, str]] = Field(
        None, 
        description="Device information for security"
    )
    
    @validator('device_info')
    def validate_device_info(cls, v) -> None:
        if v:
            allowed_keys = {'user_agent', 'ip_address', 'device_type', 'os', 'browser'}
            for key in v.keys():
                if key not in allowed_keys:
                    raise ValueError(f'Invalid device info key: {key}')
        return v
    
    class Config:
    """Config: class implementation"""
        schema_extra = {
            "example": {
                "identifier": "john_doe",
                "password": "SecurePass123!",
                "remember_me": True,
                "device_info": {
                    "user_agent": "Mozilla/5.0...",
                    "device_type": "desktop",
                    "os": "Windows 10",
                    "browser": "Chrome"
                }
            }
        }


# Content-related models
class ContentMetadata({{base_model_class}}):
    """Content metadata model"""
    
    title: constr(min_length=1, max_length=200, strip_whitespace=True) = Field(
        ...,
        description="Content title"
    )
    
    description: Optional[constr(max_length=5000, strip_whitespace=True)] = Field(
        None,
        description="Content description"
    )
    
    content_type: ContentType = Field(..., description="Type of content")
    
    tags: conlist(str, max_items=20) = Field(
        default_factory=list,
        description="Content tags"
    )
    
    category: Optional[constr(max_length=50)] = Field(
        None,
        description="Content category"
    )
    
    language: constr(min_length=2, max_length=5) = Field(
        "en",
        description="Content language"
    )
    
    privacy_level: PrivacyLevel = Field(
        PrivacyLevel.PUBLIC,
        description="Content privacy level"
    )
    
    # File information
    file_size: Optional[PositiveInt] = Field(
        None,
        description="File size in bytes"
    )
    
    file_format: Optional[constr(max_length=10)] = Field(
        None,
        description="File format/extension"
    )
    
    mime_type: Optional[constr(max_length=100)] = Field(
        None,
        description="MIME type"
    )
    
    # Media-specific fields
    duration: Optional[PositiveFloat] = Field(
        None,
        description="Duration in seconds (for audio/video)"
    )
    
    dimensions: Optional[Dict[str, PositiveInt]] = Field(
        None,
        description="Content dimensions",
        example={"width": 1920, "height": 1080}
    )
    
    thumbnail_url: Optional[AnyHttpUrl] = Field(
        None,
        description="Thumbnail image URL"
    )
    
    # Engagement metrics
    view_count: NonNegativeInt = Field(0, description="View count")
    like_count: NonNegativeInt = Field(0, description="Like count")
    share_count: NonNegativeInt = Field(0, description="Share count")
    comment_count: NonNegativeInt = Field(0, description="Comment count")
    
    # Content quality
    quality_score: Optional[confloat(ge=0.0, le=10.0)] = Field(
        None,
        description="AI-generated quality score (0-10)"
    )
    
    # Monetization
    is_monetized: bool = Field(False, description="Monetization status")
    price: Optional[condecimal(ge=0, decimal_places=2)] = Field(
        None,
        description="Content price"
    )
    
    # Publishing
    published_at: Optional[datetime] = Field(
        None,
        description="Publication timestamp"
    )
    
    scheduled_at: Optional[datetime] = Field(
        None,
        description="Scheduled publication time"
    )
    
    expires_at: Optional[datetime] = Field(
        None,
        description="Content expiration time"
    )
    
    @validator('tags')
    def validate_tags(cls, v) -> None:
        """Validate content tags"""
        if not v:
            return []
        
        validated_tags = []
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError('Tags must be strings')
            
            # Clean and validate tag
            clean_tag = tag.strip().lower()
            if len(clean_tag) < 2 or len(clean_tag) > 30:
                raise ValueError('Tags must be between 2 and 30 characters')
            
            if not re.match(r'^[a-z0-9_]+$', clean_tag):
                raise ValueError('Tags can only contain lowercase letters, numbers, and underscores')
            
            if clean_tag not in validated_tags:
                validated_tags.append(clean_tag)
        
        return validated_tags[:20]  # Limit to 20 tags
    
    @validator('dimensions')
    def validate_dimensions(cls, v) -> None:
        """Validate content dimensions"""
        if v:
            required_keys = {'width', 'height'}
            if not all(key in v for key in required_keys):
                raise ValueError('Dimensions must include width and height')
            
            if v['width'] <= 0 or v['height'] <= 0:
                raise ValueError('Dimensions must be positive')
            
            if v['width'] > 10000 or v['height'] > 10000:
                raise ValueError('Dimensions too large (max 10000x10000)')
        
        return v
    
    @root_validator
    def validate_content_metadata(cls, values) -> None:
        """Root validator for content metadata"""
        content_type = values.get('content_type')
        
        # Type-specific validations
        if content_type in [ContentType.VIDEO, ContentType.AUDIO]:
            if values.get('duration') is None:
                raise ValueError(f'{content_type} content must have duration')
        
        if content_type in [ContentType.VIDEO, ContentType.IMAGE]:
            if values.get('dimensions') is None:
                raise ValueError(f'{content_type} content must have dimensions')
        
        # Monetization validation
        if values.get('is_monetized') and values.get('price') is None:
            raise ValueError('Monetized content must have a price')
        
        # Publishing validation
        published_at = values.get('published_at')
        scheduled_at = values.get('scheduled_at')
        
        if published_at and scheduled_at:
            raise ValueError('Content cannot be both published and scheduled')
        
        return values
    
    class Config({{base_model_class}}.Config):
    """Config class implementation"""
        schema_extra = {
            "example": {
                "title": "Amazing Nature Documentary",
                "description": "A breathtaking journey through pristine wilderness",
                "content_type": "video",
                "tags": ["nature", "documentary", "wildlife", "4k"],
                "category": "documentary",
                "language": "en",
                "privacy_level": "public",
                "file_size": 2147483648,
                "file_format": "mp4",
                "mime_type": "video/mp4",
                "duration": 3600.0,
                "dimensions": {"width": 3840, "height": 2160},
                "thumbnail_url": "https://cdn.example.com/thumbnails/nature_doc.jpg",
                "view_count": 15420,
                "like_count": 892,
                "share_count": 156,
                "comment_count": 234,
                "quality_score": 9.2,
                "is_monetized": True,
                "price": "4.99",
                "published_at": "2023-01-01T00:00:00Z"
            }
        }


# Financial models
class PaymentInformation({{base_model_class}}):
    """Payment information model"""
    
    # Basic payment info
    amount: condecimal(gt=0, decimal_places=2) = Field(
        ...,
        description="Payment amount"
    )
    
    currency: constr(min_length=3, max_length=3) = Field(
        "USD",
        description="Currency code (ISO 4217)"
    )
    
    payment_method: constr(min_length=1, max_length=50) = Field(
        ...,
        description="Payment method type"
    )
    
    # Transaction details
    transaction_id: Optional[str] = Field(
        None,
        description="External transaction ID"
    )
    
    reference_id: Optional[str] = Field(
        None,
        description="Internal reference ID"
    )
    
    description: Optional[constr(max_length=500)] = Field(
        None,
        description="Payment description"
    )
    
    # Status and timing
    status: constr(min_length=1, max_length=20) = Field(
        "pending",
        description="Payment status"
    )
    
    processed_at: Optional[datetime] = Field(
        None,
        description="Processing timestamp"
    )
    
    # Fee information
    fee_amount: Optional[condecimal(ge=0, decimal_places=2)] = Field(
        None,
        description="Processing fee"
    )
    
    net_amount: Optional[condecimal(ge=0, decimal_places=2)] = Field(
        None,
        description="Net amount after fees"
    )
    
    # Customer information
    customer_email: Optional[EmailStr] = Field(
        None,
        description="Customer email"
    )
    
    billing_address: Optional[Dict[str, str]] = Field(
        None,
        description="Billing address"
    )
    
    @validator('currency')
    def validate_currency(cls, v) -> None:
        """Validate currency code"""
        v = v.upper()
        # Common currency codes
        valid_currencies = {
            'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY',
            'SEK', 'NZD', 'MXN', 'SGD', 'HKD', 'NOK', 'TRY', 'INR'
        }
        
        if v not in valid_currencies:
            raise ValueError(f'Unsupported currency: {v}')
        
        return v
    
    @validator('net_amount', always=True)
    def calculate_net_amount(cls, v, values) -> None:
        """Calculate net amount if not provided"""
        if v is None and 'amount' in values and 'fee_amount' in values:
            amount = values['amount']
            fee = values.get('fee_amount', Decimal('0'))
            return amount - fee
        return v
    
    @validator('billing_address')
    def validate_billing_address(cls, v) -> None:
        """Validate billing address"""
        if v:
            required_fields = {'street', 'city', 'country'}
            optional_fields = {'state', 'postal_code', 'apartment'}
            
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Billing address missing required field: {field}')
            
            # Validate field lengths
            for field, value in v.items():
                if field not in required_fields.union(optional_fields):
                    raise ValueError(f'Invalid billing address field: {field}')
                
                if not isinstance(value, str) or len(value.strip()) == 0:
                    raise ValueError(f'Billing address {field} cannot be empty')
                
                if len(value) > 100:
                    raise ValueError(f'Billing address {field} too long (max 100 chars)')
        
        return v
    
    class Config({{base_model_class}}.Config):
    """Config class implementation"""
        schema_extra = {
            "example": {
                "amount": "29.99",
                "currency": "USD",
                "payment_method": "credit_card",
                "transaction_id": "txn_1234567890",
                "reference_id": "ref_abcdef123456",
                "description": "Premium subscription payment",
                "status": "completed",
                "processed_at": "2023-01-01T00:00:00Z",
                "fee_amount": "1.20",
                "net_amount": "28.79",
                "customer_email": "customer@example.com",
                "billing_address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "postal_code": "10001",
                    "country": "US"
                }
            }
        }


# API Response models
class ApiResponse(BaseModel):
    """Standard API response model"""
    
    success: bool = Field(..., description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
    """Config: class implementation"""
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": "123", "name": "Example"},
                "errors": None,
                "metadata": {"page": 1, "total": 100},
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    
    items: List[Any] = Field(..., description="List of items")
    total: NonNegativeInt = Field(..., description="Total number of items")
    page: PositiveInt = Field(..., description="Current page number")
    per_page: PositiveInt = Field(..., description="Items per page")
    pages: PositiveInt = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")
    
    @validator('pages', always=True)
    def calculate_pages(cls, v, values) -> None:
        """Calculate total pages"""
        if 'total' in values and 'per_page' in values:
            import math
            return math.ceil(values['total'] / values['per_page'])
        return v
    
    @validator('has_next', always=True)
    def calculate_has_next(cls, v, values) -> None:
        """Calculate has next page"""
        if 'page' in values and 'pages' in values:
            return values['page'] < values['pages']
        return v
    
    @validator('has_prev', always=True)
    def calculate_has_prev(cls, v, values) -> None:
        """Calculate has previous page"""
        if 'page' in values:
            return values['page'] > 1
        return v
    
    class Config:
    """Config: class implementation"""
        schema_extra = {
            "example": {
                "items": [{"id": "1", "name": "Item 1"}, {"id": "2", "name": "Item 2"}],
                "total": 150,
                "page": 1,
                "per_page": 20,
                "pages": 8,
                "has_next": True,
                "has_prev": False
            }
        }


# Factory functions for model creation
def create_model_with_custom_validation(
    model_name: str,
    fields: Dict[str, Any],
    validators: Optional[Dict[str, Callable]] = None,
    config: Optional[type] = None
) -> type:
    """
    Factory function to create Pydantic models with custom validation
    
    Args:
        model_name: Name of the model class
        fields: Dictionary of field definitions
        validators: Optional custom validators
        config: Optional model configuration
        
    Returns:
        Dynamically created Pydantic model class
    """
    
    # Base model attributes
    model_attrs = fields.copy()
    
    # Add custom validators
    if validators:
        for validator_name, validator_func in validators.items():
            model_attrs[validator_name] = validator_func
    
    # Add configuration
    if config:
        model_attrs['Config'] = config
    else:
        model_attrs['Config'] = {{base_model_class}}.Config
    
    # Create the model class
    model_class = type(model_name, ({{base_model_class}},), model_attrs)
    
    return model_class


def validate_model_data(model_class: type, data: Dict[str, Any]) -> Tuple[bool, Optional[Any], Optional[List[str]]]:
    """
    Validate data against a Pydantic model
    
    Args:
        model_class: Pydantic model class
        data: Data to validate
        
    Returns:
        Tuple of (is_valid, model_instance, errors)
    """
    try:
        model_instance = model_class(**data)
        return True, model_instance, None
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ' -> '.join(str(x) for x in error['loc'])
            message = error['msg']
            errors.append(f"{field}: {message}")
        
        return False, None, errors
    except Exception as e:
        return False, None, [str(e)]


# Example usage and testing
if __name__ == "__main__":
    # Test user profile validation
    user_data = {
        "username": "test_user",
        "email": "test@example.com", 
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "website": "https://testuser.com",
        "bio": "Test user biography",
        "country": "US",
        "city": "Test City",
        "role": "creator",
        "social_links": [
            {"platform": "twitter", "url": "https://twitter.com/testuser"}
        ]
    }
    
    try:
        user = UserProfile(**user_data)
        print(f"User profile created: {user.username}")
        print(f"API JSON: {user.json_for_api()}")
        
        # Test validation errors
        invalid_data = {
            "username": "a",  # Too short
            "email": "invalid-email",  # Invalid format
            "first_name": "",  # Empty
            "phone": "123"  # Invalid format
        }
        
        is_valid, model, errors = validate_model_data(UserProfile, invalid_data)
        if not is_valid:
            print(f"Validation errors: {errors}")
            
    except Exception as e:
        print(f"Error: {e}")

# File has syntax issues - needs manual review