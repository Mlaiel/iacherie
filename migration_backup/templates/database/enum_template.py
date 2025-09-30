"""{{enum_name}} Enumeration Template for Ainflue Platform
{{enum_description}}

Enterprise-grade enumeration definitions with validation, serialization,
internationalization, and database integration.

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Role: DBA + Data Architecture Expert
"""

import logging
from typing import Dict, Any, Optional, List, Union, Set, Type, Tuple
from enum import Enum, IntEnum, Flag, IntFlag, auto
import json
from functools import total_ordering

logger = logging.getLogger(__name__)


# Base enum classes with additional functionality
class ExtendedEnum(Enum):
    """
    Extended Enum base class with additional functionality
    
    Provides:
    - Description and metadata support
    - Serialization helpers
    - Validation methods
    - Database integration
    - Internationalization support
    """
    
    def __new__(cls, value, description=None, metadata=None):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description or value
        obj.metadata = metadata or {}
        return obj
    
    @property
    def label(self) -> str:
        """Human-readable label"""
        return self.description
    
    @property
    def display_name(self) -> str:
        """Display name for UI"""
        return self.label.replace('_', ' ').title()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'value': self.value,
            'name': self.name,
            'description': self.description,
            'display_name': self.display_name,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON representation"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_value(cls, value):
        """Get enum member from value with validation"""
        if isinstance(value, cls):
            return value
        
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid {cls.__name__} value: {value}")
    
    @classmethod
    def choices(cls) -> List[Tuple[Any, str]]:
        """Get choices for form fields"""
        return [(member.value, member.description) for member in cls]
    
    @classmethod
    def values(cls) -> List[Any]:
        """Get all enum values"""
        return [member.value for member in cls]
    
    @classmethod
    def names(cls) -> List[str]:
        """Get all enum names"""
        return [member.name for member in cls]
    
    @classmethod
    def descriptions(cls) -> List[str]:
        """Get all descriptions"""
        return [member.description for member in cls]
    
    @classmethod
    def to_dict_all(cls) -> Dict[str, Dict[str, Any]]:
        """Get all enum members as dictionary"""
        return {member.name: member.to_dict() for member in cls}
    
    @classmethod
    def validate(cls, value) -> bool:
        """Validate if value is valid for this enum"""
        try:
            cls.from_value(value)
            return True
        except ValueError:
            return False
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.name}: {self.value}>"


@total_ordering
class OrderedEnum(ExtendedEnum):
    """
    Ordered enum that supports comparison operations
    """
    
    def __new__(cls, value, description=None, metadata=None, order=None):
        obj = super().__new__(cls, value, description, metadata)
        obj.order = order if order is not None else len(cls.__members__)
        return obj
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.order < other.order
        return NotImplemented
    
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return self.value == other


class StatusEnum(OrderedEnum):
    """
    Base class for status enumerations with state transition support
    """
    
    def __new__(cls, value, description=None, metadata=None, order=None, 
                transitions=None, is_final=False, is_error=False):
        obj = super().__new__(cls, value, description, metadata, order)
        obj.transitions = transitions or []
        obj.is_final = is_final
        obj.is_error = is_error
        return obj
    
    def can_transition_to(self, target_status) -> bool:
        """Check if transition to target status is allowed"""
        if isinstance(target_status, str):
            target_status = self.__class__.from_value(target_status)
        
        return target_status in self.transitions or target_status == self
    
    def get_valid_transitions(self) -> List['StatusEnum']:
        """Get list of valid transitions from current status"""
        return self.transitions
    
    @classmethod
    def get_initial_statuses(cls) -> List['StatusEnum']:
        """Get statuses that can be used as initial states"""
        return [member for member in cls if not any(
            member in other.transitions for other in cls
        )]
    
    @classmethod
    def get_final_statuses(cls) -> List['StatusEnum']:
        """Get final statuses that cannot transition further"""
        return [member for member in cls if member.is_final]
    
    @classmethod
    def get_error_statuses(cls) -> List['StatusEnum']:
        """Get error statuses"""
        return [member for member in cls if member.is_error]


# User and Account Related Enums
class UserRole(ExtendedEnum):
    """User role enumeration with permissions"""
    
    ADMIN = ("admin", "Administrator", {
        "permissions": ["all"],
        "level": 100,
        "can_moderate": True,
        "can_access_admin": True
    })
    
    MODERATOR = ("moderator", "Moderator", {
        "permissions": ["moderate", "view_reports", "manage_content"],
        "level": 80,
        "can_moderate": True,
        "can_access_admin": False
    })
    
    CREATOR = ("creator", "Content Creator", {
        "permissions": ["create_content", "monetize", "analytics"],
        "level": 60,
        "can_moderate": False,
        "can_access_admin": False
    })
    
    PREMIUM_USER = ("premium_user", "Premium User", {
        "permissions": ["premium_features", "advanced_analytics"],
        "level": 40,
        "can_moderate": False,
        "can_access_admin": False
    })
    
    USER = ("user", "Regular User", {
        "permissions": ["basic_features"],
        "level": 20,
        "can_moderate": False,
        "can_access_admin": False
    })
    
    GUEST = ("guest", "Guest User", {
        "permissions": ["view_public"],
        "level": 10,
        "can_moderate": False,
        "can_access_admin": False
    })
    
    @property
    def permissions(self) -> List[str]:
        """Get permissions for this role"""
        return self.metadata.get("permissions", [])
    
    @property
    def level(self) -> int:
        """Get role level (higher = more permissions)"""
        return self.metadata.get("level", 0)
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in self.permissions or "all" in self.permissions
    
    def can_moderate(self) -> bool:
        """Check if role can moderate content"""
        return self.metadata.get("can_moderate", False)
    
    def can_access_admin(self) -> bool:
        """Check if role can access admin panel"""
        return self.metadata.get("can_access_admin", False)
    
    def is_higher_than(self, other_role: 'UserRole') -> bool:
        """Check if this role has higher privileges than another"""
        return self.level > other_role.level


class AccountStatus(StatusEnum):
    """Account status with state transitions"""
    
    PENDING = ("pending", "Pending Verification", {}, 1, [], False, False)
    ACTIVE = ("active", "Active", {}, 2, [], False, False)
    INACTIVE = ("inactive", "Inactive", {}, 3, [], False, False)
    SUSPENDED = ("suspended", "Suspended", {}, 4, [], False, False)
    BANNED = ("banned", "Banned", {}, 5, [], True, True)
    DELETED = ("deleted", "Deleted", {}, 6, [], True, False)
    
    # Define transitions after class creation
    def __init_subclass__(cls):
        super().__init_subclass__()
        # Set up state transitions
        cls.PENDING.transitions = [cls.ACTIVE, cls.DELETED]
        cls.ACTIVE.transitions = [cls.INACTIVE, cls.SUSPENDED, cls.BANNED, cls.DELETED]
        cls.INACTIVE.transitions = [cls.ACTIVE, cls.DELETED]
        cls.SUSPENDED.transitions = [cls.ACTIVE, cls.BANNED, cls.DELETED]
        cls.BANNED.transitions = [cls.DELETED]
        cls.DELETED.transitions = []


# Content Related Enums
class ContentType(ExtendedEnum):
    """Content type enumeration with metadata"""
    
    VIDEO = ("video", "Video Content", {
        "mime_types": ["video/mp4", "video/avi", "video/mov", "video/wmv"],
        "max_size_mb": 5000,
        "supports_streaming": True,
        "requires_encoding": True,
        "thumbnail_required": True
    })
    
    IMAGE = ("image", "Image Content", {
        "mime_types": ["image/jpeg", "image/png", "image/gif", "image/webp"],
        "max_size_mb": 50,
        "supports_streaming": False,
        "requires_encoding": False,
        "thumbnail_required": False
    })
    
    AUDIO = ("audio", "Audio Content", {
        "mime_types": ["audio/mp3", "audio/wav", "audio/flac", "audio/aac"],
        "max_size_mb": 500,
        "supports_streaming": True,
        "requires_encoding": True,
        "thumbnail_required": False
    })
    
    TEXT = ("text", "Text Content", {
        "mime_types": ["text/plain", "text/markdown", "text/html"],
        "max_size_mb": 10,
        "supports_streaming": False,
        "requires_encoding": False,
        "thumbnail_required": False
    })
    
    DOCUMENT = ("document", "Document", {
        "mime_types": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
        "max_size_mb": 100,
        "supports_streaming": False,
        "requires_encoding": False,
        "thumbnail_required": True
    })
    
    LIVE_STREAM = ("live_stream", "Live Stream", {
        "mime_types": ["application/x-mpegURL", "video/mp2t"],
        "max_size_mb": None,
        "supports_streaming": True,
        "requires_encoding": True,
        "thumbnail_required": True
    })
    
    def get_supported_mime_types(self) -> List[str]:
        """Get supported MIME types for this content type"""
        return self.metadata.get("mime_types", [])
    
    def get_max_size_mb(self) -> Optional[int]:
        """Get maximum file size in MB"""
        return self.metadata.get("max_size_mb")
    
    def supports_streaming(self) -> bool:
        """Check if content type supports streaming"""
        return self.metadata.get("supports_streaming", False)
    
    def requires_encoding(self) -> bool:
        """Check if content type requires encoding"""
        return self.metadata.get("requires_encoding", False)
    
    def requires_thumbnail(self) -> bool:
        """Check if content type requires thumbnail"""
        return self.metadata.get("thumbnail_required", False)


class ContentStatus(StatusEnum):
    """Content status with workflow transitions"""
    
    DRAFT = ("draft", "Draft", {}, 1, [], False, False)
    PENDING_REVIEW = ("pending_review", "Pending Review", {}, 2, [], False, False)
    APPROVED = ("approved", "Approved", {}, 3, [], False, False)
    PUBLISHED = ("published", "Published", {}, 4, [], False, False)
    REJECTED = ("rejected", "Rejected", {}, 5, [], False, True)
    ARCHIVED = ("archived", "Archived", {}, 6, [], True, False)
    DELETED = ("deleted", "Deleted", {}, 7, [], True, False)
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        # Set up content workflow transitions
        cls.DRAFT.transitions = [cls.PENDING_REVIEW, cls.DELETED]
        cls.PENDING_REVIEW.transitions = [cls.APPROVED, cls.REJECTED, cls.DRAFT]
        cls.APPROVED.transitions = [cls.PUBLISHED, cls.ARCHIVED, cls.DELETED]
        cls.PUBLISHED.transitions = [cls.ARCHIVED, cls.DELETED]
        cls.REJECTED.transitions = [cls.DRAFT, cls.DELETED]
        cls.ARCHIVED.transitions = [cls.PUBLISHED, cls.DELETED]
        cls.DELETED.transitions = []


class PrivacyLevel(OrderedEnum):
    """Privacy level enumeration with access control"""
    
    PUBLIC = ("public", "Public", {
        "description": "Visible to everyone",
        "requires_auth": False,
        "searchable": True,
        "can_share": True
    }, 1)
    
    UNLISTED = ("unlisted", "Unlisted", {
        "description": "Accessible with direct link",
        "requires_auth": False,
        "searchable": False,
        "can_share": True
    }, 2)
    
    FOLLOWERS_ONLY = ("followers_only", "Followers Only", {
        "description": "Visible to followers only",
        "requires_auth": True,
        "searchable": False,
        "can_share": True
    }, 3)
    
    SUBSCRIBERS_ONLY = ("subscribers_only", "Subscribers Only", {
        "description": "Visible to paid subscribers only",
        "requires_auth": True,
        "searchable": False,
        "can_share": False
    }, 4)
    
    PRIVATE = ("private", "Private", {
        "description": "Visible to owner only",
        "requires_auth": True,
        "searchable": False,
        "can_share": False
    }, 5)
    
    def requires_authentication(self) -> bool:
        """Check if privacy level requires authentication"""
        return self.metadata.get("requires_auth", False)
    
    def is_searchable(self) -> bool:
        """Check if content is searchable"""
        return self.metadata.get("searchable", False)
    
    def allows_sharing(self) -> bool:
        """Check if content can be shared"""
        return self.metadata.get("can_share", False)


# Payment and Monetization Enums
class PaymentStatus(StatusEnum):
    """Payment status with transaction flow"""
    
    PENDING = ("pending", "Pending", {}, 1, [], False, False)
    PROCESSING = ("processing", "Processing", {}, 2, [], False, False)
    COMPLETED = ("completed", "Completed", {}, 3, [], True, False)
    FAILED = ("failed", "Failed", {}, 4, [], False, True)
    CANCELLED = ("cancelled", "Cancelled", {}, 5, [], True, False)
    REFUNDED = ("refunded", "Refunded", {}, 6, [], True, False)
    PARTIALLY_REFUNDED = ("partially_refunded", "Partially Refunded", {}, 7, [], False, False)
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        # Set up payment status transitions
        cls.PENDING.transitions = [cls.PROCESSING, cls.CANCELLED, cls.FAILED]
        cls.PROCESSING.transitions = [cls.COMPLETED, cls.FAILED, cls.CANCELLED]
        cls.COMPLETED.transitions = [cls.REFUNDED, cls.PARTIALLY_REFUNDED]
        cls.FAILED.transitions = [cls.PENDING]
        cls.CANCELLED.transitions = []
        cls.REFUNDED.transitions = []
        cls.PARTIALLY_REFUNDED.transitions = [cls.REFUNDED]


class PaymentMethod(ExtendedEnum):
    """Payment method enumeration with provider details"""
    
    CREDIT_CARD = ("credit_card", "Credit Card", {
        "providers": ["stripe", "paypal", "square"],
        "supports_recurring": True,
        "processing_time": "instant",
        "fees": {"percentage": 2.9, "fixed": 0.30}
    })
    
    DEBIT_CARD = ("debit_card", "Debit Card", {
        "providers": ["stripe", "paypal"],
        "supports_recurring": True,
        "processing_time": "instant",
        "fees": {"percentage": 2.9, "fixed": 0.30}
    })
    
    PAYPAL = ("paypal", "PayPal", {
        "providers": ["paypal"],
        "supports_recurring": True,
        "processing_time": "instant",
        "fees": {"percentage": 3.5, "fixed": 0.35}
    })
    
    BANK_TRANSFER = ("bank_transfer", "Bank Transfer", {
        "providers": ["wise", "stripe"],
        "supports_recurring": False,
        "processing_time": "1-3 days",
        "fees": {"percentage": 0.8, "fixed": 0.00}
    })
    
    CRYPTOCURRENCY = ("cryptocurrency", "Cryptocurrency", {
        "providers": ["coinbase", "bitpay"],
        "supports_recurring": False,
        "processing_time": "10-60 minutes",
        "fees": {"percentage": 1.0, "fixed": 0.00}
    })
    
    APPLE_PAY = ("apple_pay", "Apple Pay", {
        "providers": ["stripe"],
        "supports_recurring": True,
        "processing_time": "instant",
        "fees": {"percentage": 2.9, "fixed": 0.30}
    })
    
    GOOGLE_PAY = ("google_pay", "Google Pay", {
        "providers": ["stripe"],
        "supports_recurring": True,
        "processing_time": "instant",
        "fees": {"percentage": 2.9, "fixed": 0.30}
    })
    
    def get_supported_providers(self) -> List[str]:
        """Get supported payment providers"""
        return self.metadata.get("providers", [])
    
    def supports_recurring_payments(self) -> bool:
        """Check if payment method supports recurring payments"""
        return self.metadata.get("supports_recurring", False)
    
    def get_processing_time(self) -> str:
        """Get typical processing time"""
        return self.metadata.get("processing_time", "unknown")
    
    def get_fees(self) -> Dict[str, float]:
        """Get fee structure"""
        return self.metadata.get("fees", {"percentage": 0, "fixed": 0})


class Currency(ExtendedEnum):
    """Currency enumeration with exchange rate support"""
    
    USD = ("USD", "US Dollar", {
        "symbol": "$",
        "decimal_places": 2,
        "is_crypto": False,
        "countries": ["US"]
    })
    
    EUR = ("EUR", "Euro", {
        "symbol": "€",
        "decimal_places": 2,
        "is_crypto": False,
        "countries": ["DE", "FR", "IT", "ES", "NL"]
    })
    
    GBP = ("GBP", "British Pound", {
        "symbol": "£",
        "decimal_places": 2,
        "is_crypto": False,
        "countries": ["GB"]
    })
    
    JPY = ("JPY", "Japanese Yen", {
        "symbol": "¥",
        "decimal_places": 0,
        "is_crypto": False,
        "countries": ["JP"]
    })
    
    CAD = ("CAD", "Canadian Dollar", {
        "symbol": "C$",
        "decimal_places": 2,
        "is_crypto": False,
        "countries": ["CA"]
    })
    
    BTC = ("BTC", "Bitcoin", {
        "symbol": "₿",
        "decimal_places": 8,
        "is_crypto": True,
        "countries": []
    })
    
    ETH = ("ETH", "Ethereum", {
        "symbol": "Ξ",
        "decimal_places": 18,
        "is_crypto": True,
        "countries": []
    })
    
    def get_symbol(self) -> str:
        """Get currency symbol"""
        return self.metadata.get("symbol", self.value)
    
    def get_decimal_places(self) -> int:
        """Get number of decimal places"""
        return self.metadata.get("decimal_places", 2)
    
    def is_cryptocurrency(self) -> bool:
        """Check if currency is cryptocurrency"""
        return self.metadata.get("is_crypto", False)
    
    def get_countries(self) -> List[str]:
        """Get countries using this currency"""
        return self.metadata.get("countries", [])


# Platform and Integration Enums
class Platform(ExtendedEnum):
    """Social media platform enumeration"""
    
    YOUTUBE = ("youtube", "YouTube", {
        "api_base": "https://www.googleapis.com/youtube/v3",
        "oauth_required": True,
        "rate_limit": 10000,
        "content_types": ["video", "live_stream"],
        "max_video_size_gb": 256
    })
    
    INSTAGRAM = ("instagram", "Instagram", {
        "api_base": "https://graph.instagram.com",
        "oauth_required": True,
        "rate_limit": 200,
        "content_types": ["image", "video"],
        "max_video_size_gb": 4
    })
    
    TIKTOK = ("tiktok", "TikTok", {
        "api_base": "https://open-api.tiktok.com",
        "oauth_required": True,
        "rate_limit": 1000,
        "content_types": ["video"],
        "max_video_size_gb": 4
    })
    
    TWITTER = ("twitter", "Twitter/X", {
        "api_base": "https://api.twitter.com/2",
        "oauth_required": True,
        "rate_limit": 300,
        "content_types": ["text", "image", "video"],
        "max_video_size_gb": 0.5
    })
    
    FACEBOOK = ("facebook", "Facebook", {
        "api_base": "https://graph.facebook.com",
        "oauth_required": True,
        "rate_limit": 600,
        "content_types": ["text", "image", "video"],
        "max_video_size_gb": 10
    })
    
    LINKEDIN = ("linkedin", "LinkedIn", {
        "api_base": "https://api.linkedin.com/v2",
        "oauth_required": True,
        "rate_limit": 500,
        "content_types": ["text", "image", "video", "document"],
        "max_video_size_gb": 5
    })
    
    TWITCH = ("twitch", "Twitch", {
        "api_base": "https://api.twitch.tv/helix",
        "oauth_required": True,
        "rate_limit": 800,
        "content_types": ["live_stream", "video"],
        "max_video_size_gb": None
    })
    
    def get_api_base_url(self) -> str:
        """Get API base URL"""
        return self.metadata.get("api_base", "")
    
    def requires_oauth(self) -> bool:
        """Check if platform requires OAuth"""
        return self.metadata.get("oauth_required", False)
    
    def get_rate_limit(self) -> int:
        """Get API rate limit per hour"""
        return self.metadata.get("rate_limit", 100)
    
    def get_supported_content_types(self) -> List[str]:
        """Get supported content types"""
        return self.metadata.get("content_types", [])
    
    def get_max_video_size_gb(self) -> Optional[float]:
        """Get maximum video size in GB"""
        return self.metadata.get("max_video_size_gb")


# Notification and Communication Enums
class NotificationType(ExtendedEnum):
    """Notification type enumeration"""
    
    INFO = ("info", "Information", {
        "icon": "info",
        "color": "#17a2b8",
        "priority": "normal",
        "auto_dismiss": True,
        "sound": False
    })
    
    SUCCESS = ("success", "Success", {
        "icon": "check",
        "color": "#28a745",
        "priority": "normal",
        "auto_dismiss": True,
        "sound": False
    })
    
    WARNING = ("warning", "Warning", {
        "icon": "warning",
        "color": "#ffc107",
        "priority": "high",
        "auto_dismiss": False,
        "sound": True
    })
    
    ERROR = ("error", "Error", {
        "icon": "error",
        "color": "#dc3545",
        "priority": "urgent",
        "auto_dismiss": False,
        "sound": True
    })
    
    SECURITY = ("security", "Security Alert", {
        "icon": "shield",
        "color": "#6f42c1",
        "priority": "critical",
        "auto_dismiss": False,
        "sound": True
    })
    
    MARKETING = ("marketing", "Marketing", {
        "icon": "bullhorn",
        "color": "#fd7e14",
        "priority": "low",
        "auto_dismiss": True,
        "sound": False
    })
    
    def get_icon(self) -> str:
        """Get notification icon"""
        return self.metadata.get("icon", "info")
    
    def get_color(self) -> str:
        """Get notification color"""
        return self.metadata.get("color", "#000000")
    
    def get_priority(self) -> str:
        """Get notification priority"""
        return self.metadata.get("priority", "normal")
    
    def should_auto_dismiss(self) -> bool:
        """Check if notification should auto-dismiss"""
        return self.metadata.get("auto_dismiss", True)
    
    def has_sound(self) -> bool:
        """Check if notification has sound"""
        return self.metadata.get("sound", False)


class NotificationChannel(ExtendedEnum):
    """Notification delivery channel enumeration"""
    
    EMAIL = ("email", "Email", {
        "rate_limit": 100,
        "batch_size": 50,
        "retry_attempts": 3,
        "delivery_time": "immediate"
    })
    
    SMS = ("sms", "SMS", {
        "rate_limit": 50,
        "batch_size": 10,
        "retry_attempts": 2,
        "delivery_time": "immediate"
    })
    
    PUSH = ("push", "Push Notification", {
        "rate_limit": 1000,
        "batch_size": 100,
        "retry_attempts": 3,
        "delivery_time": "immediate"
    })
    
    IN_APP = ("in_app", "In-App Notification", {
        "rate_limit": 10000,
        "batch_size": 500,
        "retry_attempts": 1,
        "delivery_time": "immediate"
    })
    
    WEBHOOK = ("webhook", "Webhook", {
        "rate_limit": 500,
        "batch_size": 1,
        "retry_attempts": 5,
        "delivery_time": "immediate"
    })
    
    def get_rate_limit(self) -> int:
        """Get rate limit per hour"""
        return self.metadata.get("rate_limit", 100)
    
    def get_batch_size(self) -> int:
        """Get maximum batch size"""
        return self.metadata.get("batch_size", 1)
    
    def get_retry_attempts(self) -> int:
        """Get number of retry attempts"""
        return self.metadata.get("retry_attempts", 3)


# System and Configuration Enums
class LogLevel(OrderedEnum):
    """Logging level enumeration"""
    
    TRACE = ("trace", "Trace", {}, 1)
    DEBUG = ("debug", "Debug", {}, 2)
    INFO = ("info", "Information", {}, 3)
    WARNING = ("warning", "Warning", {}, 4)
    ERROR = ("error", "Error", {}, 5)
    CRITICAL = ("critical", "Critical", {}, 6)


class Environment(ExtendedEnum):
    """Environment enumeration"""
    
    DEVELOPMENT = ("development", "Development", {
        "debug": True,
        "ssl_required": False,
        "log_level": "debug",
        "cache_ttl": 60
    })
    
    TESTING = ("testing", "Testing", {
        "debug": True,
        "ssl_required": False,
        "log_level": "info",
        "cache_ttl": 30
    })
    
    STAGING = ("staging", "Staging", {
        "debug": False,
        "ssl_required": True,
        "log_level": "warning",
        "cache_ttl": 300
    })
    
    PRODUCTION = ("production", "Production", {
        "debug": False,
        "ssl_required": True,
        "log_level": "error",
        "cache_ttl": 3600
    })
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled"""
        return self.metadata.get("debug", False)
    
    def requires_ssl(self) -> bool:
        """Check if SSL is required"""
        return self.metadata.get("ssl_required", False)
    
    def get_log_level(self) -> str:
        """Get default log level"""
        return self.metadata.get("log_level", "info")
    
    def get_cache_ttl(self) -> int:
        """Get default cache TTL"""
        return self.metadata.get("cache_ttl", 3600)


# Utility functions for enum management
class EnumRegistry:
    """Registry for managing enumerations"""
    
    _registry: Dict[str, Type[Enum]] = {}
    
    @classmethod
    def register(cls, enum_class: Type[Enum]) -> None:
        """Register an enum class"""
        cls._registry[enum_class.__name__] = enum_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[Enum]]:
        """Get enum class by name"""
        return cls._registry.get(name)
    
    @classmethod
    def list_all(cls) -> List[str]:
        """List all registered enum names"""
        return list(cls._registry.keys())
    
    @classmethod
    def validate_value(cls, enum_name: str, value: Any) -> bool:
        """Validate value against enum"""
        enum_class = cls.get(enum_name)
        if enum_class and hasattr(enum_class, 'validate'):
            return enum_class.validate(value)
        return False


def create_enum_from_config(name: str, config: Dict[str, Any]) -> Type[ExtendedEnum]:
    """
    Create enum from configuration dictionary
    
    Args:
        name: Enum class name
        config: Configuration with enum values and metadata
        
    Returns:
        Dynamically created enum class
    """
    
    enum_members = {}
    
    for key, value_config in config.items():
        if isinstance(value_config, dict):
            value = value_config.get('value', key.lower())
            description = value_config.get('description', key.replace('_', ' ').title())
            metadata = value_config.get('metadata', {})
        else:
            value = value_config
            description = key.replace('_', ' ').title()
            metadata = {}
        
        enum_members[key] = (value, description, metadata)
    
    # Create the enum class
    enum_class = ExtendedEnum(name, enum_members)
    
    # Register the enum
    EnumRegistry.register(enum_class)
    
    return enum_class


def enum_to_choices(enum_class: Type[Enum]) -> List[Tuple[Any, str]]:
    """Convert enum to choices format for forms"""
    if hasattr(enum_class, 'choices'):
        return enum_class.choices()
    else:
        return [(member.value, member.name.replace('_', ' ').title()) for member in enum_class]


def validate_enum_transition(current_status: StatusEnum, target_status: StatusEnum) -> Tuple[bool, Optional[str]]:
    """
    Validate status transition
    
    Args:
        current_status: Current status
        target_status: Target status
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(current_status, StatusEnum) or not isinstance(target_status, StatusEnum):
        return False, "Invalid status type"
    
    if current_status.__class__ != target_status.__class__:
        return False, "Status types do not match"
    
    if current_status.can_transition_to(target_status):
        return True, None
    else:
        valid_transitions = [status.value for status in current_status.get_valid_transitions()]
        return False, f"Cannot transition from {current_status.value} to {target_status.value}. Valid transitions: {valid_transitions}"


# Register all enums
EnumRegistry.register(UserRole)
EnumRegistry.register(AccountStatus)
EnumRegistry.register(ContentType)
EnumRegistry.register(ContentStatus)
EnumRegistry.register(PrivacyLevel)
EnumRegistry.register(PaymentStatus)
EnumRegistry.register(PaymentMethod)
EnumRegistry.register(Currency)
EnumRegistry.register(Platform)
EnumRegistry.register(NotificationType)
EnumRegistry.register(NotificationChannel)
EnumRegistry.register(LogLevel)
EnumRegistry.register(Environment)


# Example usage and testing
if __name__ == "__main__":
    # Test user role functionality
    admin_role = UserRole.ADMIN
    print(f"Admin role: {admin_role.value}")
    print(f"Admin permissions: {admin_role.permissions}")
    print(f"Admin level: {admin_role.level}")
    print(f"Can moderate: {admin_role.can_moderate()}")
    print(f"Can access admin: {admin_role.can_access_admin()}")
    
    # Test role comparison
    user_role = UserRole.USER
    print(f"Admin is higher than user: {admin_role.is_higher_than(user_role)}")
    
    # Test content status transitions
    draft_status = ContentStatus.DRAFT
    published_status = ContentStatus.PUBLISHED
    
    print(f"Can transition from draft to published: {draft_status.can_transition_to(published_status)}")
    print(f"Valid transitions from draft: {[s.value for s in draft_status.get_valid_transitions()]}")
    
    # Test currency functionality
    usd = Currency.USD
    print(f"USD symbol: {usd.get_symbol()}")
    print(f"USD decimal places: {usd.get_decimal_places()}")
    print(f"USD is crypto: {usd.is_cryptocurrency()}")
    
    # Test platform functionality
    youtube = Platform.YOUTUBE
    print(f"YouTube API: {youtube.get_api_base_url()}")
    print(f"YouTube content types: {youtube.get_supported_content_types()}")
    print(f"YouTube rate limit: {youtube.get_rate_limit()}")
    
    # Test enum registry
    print(f"Registered enums: {EnumRegistry.list_all()}")
    
    # Test dynamic enum creation
    color_config = {
        'RED': {'value': '#FF0000', 'description': 'Red Color', 'metadata': {'hex': '#FF0000'}},
        'GREEN': {'value': '#00FF00', 'description': 'Green Color', 'metadata': {'hex': '#00FF00'}},
        'BLUE': {'value': '#0000FF', 'description': 'Blue Color', 'metadata': {'hex': '#0000FF'}}
    }
    
    ColorEnum = create_enum_from_config('ColorEnum', color_config)
    print(f"Dynamic enum created: {ColorEnum.RED.value}")
    print(f"Color choices: {enum_to_choices(ColorEnum)}")
    
    # Test status transition validation
    pending_payment = PaymentStatus.PENDING
    completed_payment = PaymentStatus.COMPLETED
    
    is_valid, error = validate_enum_transition(pending_payment, completed_payment)
    print(f"Payment transition valid: {is_valid}, error: {error}")
    
    # Test enum serialization
    print(f"User role as dict: {admin_role.to_dict()}")
    print(f"All user roles: {UserRole.to_dict_all()}")