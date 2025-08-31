"""Client Module Index - Performance optimization and quick access.

This index file provides optimized imports and configuration for the
Client Business Module of the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Advanced Content Protection
"""
# Core client management imports
from .manager import ClientManager, ClientRegistrationData, ClientUpdateData, ClientType
from .content import ContentManager, ContentUploadData, ContentProcessingOptions, SupportedFormat
from .profile import ProfileManager, ProfileUpdateData, PortfolioItemData, CreatorTier
from .subscription import SubscriptionManager, SubscriptionCreateData, SubscriptionPlan, BillingCycle
from .verification import VerificationManager, DocumentSubmissionData, SocialMediaVerificationData, VerificationLevel
from .activity import ActivityManager, ActivityFilter, SessionData, InteractionType
from .preference import PreferenceManager, NotificationPreferenceData, PrivacyPreferenceData, ContentPreferenceData

# Module configuration
MODULE_VERSION = "2.1.0"
MODULE_AUTHOR = "Fahed Mlaiel"
MODULE_EMAIL = "mlaiel@live.de"
MODULE_NAME = "IA Influencer Agent - Client Business Module"

# Supported creator types
SUPPORTED_CREATOR_TYPES = [
    "musician",
    "blogger", 
    "photographer",
    "influencer",
    "comedian",
    "podcaster",
    "video_creator",
    "artist"
]

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    "free": {
        "price": 0.00,
        "uploads_per_month": 5,
        "storage_gb": 1,
        "features": ["basic_protection", "manual_fingerprinting"]
    },
    "creator": {
        "price": 29.99,
        "uploads_per_month": 100,
        "storage_gb": 50,
        "features": ["advanced_protection", "automated_fingerprinting", "social_integration"]
    },
    "professional": {
        "price": 99.99,
        "uploads_per_month": 500,
        "storage_gb": 250,
        "features": ["premium_protection", "real_time_monitoring", "api_access"]
    },
    "enterprise": {
        "price": 299.99,
        "uploads_per_month": -1,  # Unlimited
        "storage_gb": 1000,
        "features": ["enterprise_protection", "dedicated_monitoring", "white_label"]
    }
}

# Content format support
SUPPORTED_CONTENT_FORMATS = {
    "audio": ["mp3", "wav", "flac", "m4a", "ogg"],
    "video": ["mp4", "avi", "mov", "mkv", "webm"],
    "image": ["jpg", "jpeg", "png", "gif", "webp", "tiff"],
    "text": ["txt", "md", "html", "pdf"]
}

# Verification levels hierarchy
VERIFICATION_HIERARCHY = [
    "unverified",
    "email_verified", 
    "phone_verified",
    "identity_verified",
    "creator_verified",
    "business_verified",
    "premium_verified"
]

# Module health check
def get_module_status():
    """Get current module status and configuration."""    return {
        "module": MODULE_NAME,
        "version": MODULE_VERSION,
        "author": MODULE_AUTHOR,
        "email": MODULE_EMAIL,
        "status": "active",
        "supported_creators": len(SUPPORTED_CREATOR_TYPES),
        "subscription_tiers": len(SUBSCRIPTION_PLANS),
        "content_formats": sum(len(formats) for formats in SUPPORTED_CONTENT_FORMATS.values()),
        "verification_levels": len(VERIFICATION_HIERARCHY)
    }

# Performance optimization hints
PERFORMANCE_CONFIG = {
    "cache_timeout_seconds": 3600,
    "max_concurrent_uploads": 10,
    "batch_processing_size": 100,
    "session_cleanup_interval": 86400,  # 24 hours
    "activity_retention_days": 90,
    "analytics_aggregation_interval": 300  # 5 minutes
}

# Export all main classes for easy import
__all__ = [
    # Core managers
    "ClientManager",
    "ContentManager", 
    "ProfileManager",
    "SubscriptionManager",
    "VerificationManager",
    "ActivityManager",
    "PreferenceManager",
    
    # Data models
    "ClientRegistrationData",
    "ClientUpdateData",
    "ContentUploadData",
    "ContentProcessingOptions",
    "ProfileUpdateData",
    "PortfolioItemData",
    "SubscriptionCreateData",
    "DocumentSubmissionData",
    "SocialMediaVerificationData",
    "ActivityFilter",
    "SessionData",
    "NotificationPreferenceData",
    "PrivacyPreferenceData",
    "ContentPreferenceData",
    
    # Enums
    "ClientType",
    "SupportedFormat",
    "CreatorTier",
    "SubscriptionPlan",
    "BillingCycle",
    "VerificationLevel",
    "InteractionType",
    
    # Configuration
    "MODULE_VERSION",
    "MODULE_AUTHOR",
    "MODULE_EMAIL",
    "SUPPORTED_CREATOR_TYPES",
    "SUBSCRIPTION_PLANS",
    "SUPPORTED_CONTENT_FORMATS",
    "VERIFICATION_HIERARCHY",
    "PERFORMANCE_CONFIG",
    
    # Utilities
    "get_module_status"
]
