"""Core Adapters Module for IA Influencer Agent

This module provides a comprehensive adapter system for integrating with various
external platforms and services. The architecture follows enterprise patterns
with support for multi-tenancy, rate limiting, health monitoring, and failover.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Components:
- Base adapter framework with standard interfaces
- Social media platform adapters (YouTube, Instagram, TikTok, etc.)
- AI platform adapters (OpenAI, Anthropic, HuggingFace, etc.)
- Content protection adapters (YouTube Content ID, Facebook Rights Manager, etc.)
- Email marketing platform adapters (Mailchimp, SendGrid, etc.)
- SEO platform adapters (Google Search Console, SEMrush, etc.)
- Payment processing adapters (Stripe, PayPal, etc.)
- Storage platform adapters (AWS S3, Google Cloud, etc.)
- Adapter registry for centralized management
- Configuration management and validation
- Auto-discovery and health monitoring systems

Architecture:
- Factory pattern for adapter creation
- Registry pattern for adapter management
- Observer pattern for event handling
- Strategy pattern for platform-specific implementations
- Configuration management with encryption
- Auto-discovery and initialization system
"""
from .base_adapter import (
    BasePlatformAdapter, 
    AdapterStatus, 
    PlatformType,
    RateLimiter,
    AdapterConfig,
    AdapterMetrics
)

from .adapter_registry import (
    AdapterRegistry,
    AdapterRegistration,
    get_adapter_registry,
    register_adapter,
    get_adapter,
    list_adapters
)

from .social_media_adapters import (
    YouTubeAdapter,
    InstagramAdapter,
    TikTokAdapter,
    TwitterAdapter,
    FacebookAdapter,
    LinkedInAdapter,
    PinterestAdapter,
    SnapchatAdapter,
    RedditAdapter,
    SocialMediaAdapterFactory
)

from .ai_platform_adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    HuggingFaceAdapter,
    AIAdapterManager
)

from .content_protection_adapters import (
    YouTubeContentIDAdapter,
    FacebookRightsManagerAdapter,
    DMCAProtectionAdapter,
    ProtectionAdapterManager
)

from .email_marketing_adapters import (
    MailchimpAdapter,
    SendGridAdapter,
    ConvertKitAdapter,
    EmailMarketingAdapterFactory
)

from .seo_platform_adapters import (
    GoogleSearchConsoleAdapter,
    SEMrushAdapter,
    SEOAdapterManager
)

from .payment_adapters import (
    StripeAdapter,
    PayPalAdapter,
    SquareAdapter,
    PaymentAdapterFactory
)

from .storage_adapters import (
    S3StorageAdapter,
    GoogleCloudStorageAdapter,
    AzureBlobStorageAdapter,
    StorageAdapterFactory
)

from .config import (
    ConfigurationManager,
    get_configuration_manager,
    get_adapter_config,
    validate_adapter_config,
    Environment,
    AdapterBaseConfig,
    SocialMediaAdapterConfig,
    AIAdapterConfig,
    ContentProtectionConfig,
    EmailMarketingConfig,
    SEOPlatformConfig
)

from .index import (
    AdapterIndexManager,
    get_adapter_index_manager,
    initialize_adapter_index,
    get_adapter_system_status,
    AdapterDiscoveryResult,
    AdapterModuleInfo
)

# Platform support matrix
SUPPORTED_PLATFORMS = {
    PlatformType.SOCIAL_MEDIA: [
        "youtube", "instagram", "tiktok", "twitter", "facebook", 
        "linkedin", "pinterest", "snapchat", "reddit"
    ],
    PlatformType.AI_PLATFORM: [
        "openai", "anthropic", "huggingface"
    ],
    PlatformType.CONTENT_PROTECTION: [
        "youtube_content_id", "facebook_rights_manager", "dmca_protection"
    ],
    PlatformType.EMAIL_MARKETING: [
        "mailchimp", "sendgrid", "convertkit"
    ],
    PlatformType.SEO_PLATFORM: [
        "google_search_console", "semrush"
    ],
    PlatformType.PAYMENT: [
        "stripe", "paypal", "square"
    ],
    PlatformType.STORAGE: [
        "s3", "google_cloud", "azure_blob"
    ]
}

# Version information
__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export all public interfaces
__all__ = [
    # Base components
    "BasePlatformAdapter", "AdapterStatus", "PlatformType", 
    "RateLimiter", "AdapterConfig", "AdapterMetrics",
    
    # Registry system
    "AdapterRegistry", "AdapterRegistration", "get_adapter_registry",
    "register_adapter", "get_adapter", "list_adapters",
    
    # Social media adapters
    "YouTubeAdapter", "InstagramAdapter", "TikTokAdapter", "TwitterAdapter",
    "FacebookAdapter", "LinkedInAdapter", "PinterestAdapter", "SnapchatAdapter",
    "RedditAdapter", "SocialMediaAdapterFactory",
    
    # AI platform adapters
    "OpenAIAdapter", "AnthropicAdapter", "HuggingFaceAdapter", "AIAdapterManager",
    
    # Content protection adapters
    "YouTubeContentIDAdapter", "FacebookRightsManagerAdapter", "DMCAProtectionAdapter",
    "ProtectionAdapterManager",
    
    # Email marketing adapters
    "MailchimpAdapter", "SendGridAdapter", "ConvertKitAdapter",
    "EmailMarketingAdapterFactory",
    
    # SEO platform adapters
    "GoogleSearchConsoleAdapter", "SEMrushAdapter", "SEOAdapterManager",
    
    # Payment adapters
    "StripeAdapter", "PayPalAdapter", "SquareAdapter", "PaymentAdapterFactory",
    
    # Storage adapters
    "S3StorageAdapter", "GoogleCloudStorageAdapter", "AzureBlobStorageAdapter",
    "StorageAdapterFactory",
    
    # Configuration management
    "ConfigurationManager", "get_configuration_manager", "get_adapter_config",
    "validate_adapter_config", "Environment", "AdapterBaseConfig",
    "SocialMediaAdapterConfig", "AIAdapterConfig", "ContentProtectionConfig",
    "EmailMarketingConfig", "SEOPlatformConfig",
    
    # Index and discovery
    "AdapterIndexManager", "get_adapter_index_manager", "initialize_adapter_index",
    "get_adapter_system_status", "AdapterDiscoveryResult", "AdapterModuleInfo",
    
    # Platform support
    "SUPPORTED_PLATFORMS"
]

import logging
from typing import Dict, List, Optional, Any, Union, Type

# Base adapter framework
from .base_adapter import (
    BasePlatformAdapter,
    PlatformType,
    AdapterStatus,
    AuthenticationType,
    AdapterCredentials,
    RateLimitConfig,
    AdapterError,
    AuthenticationError,
    RateLimitError,
    PlatformError,
    ConfigurationError
)

# AI platform adapters
from .ai_platform_adapters import (
    AIProvider,
    AIModelType,
    AIModelConfig,
    AIRequest,
    AIResponse,
    BaseAIAdapter,
    OpenAIAdapter,
    AnthropicAdapter,
    HuggingFaceAdapter,
    AIAdapterFactory,
    AIAdapterManager
)

# Content protection adapters
from .content_protection_adapters import (
    ProtectionPlatform,
    ContentType,
    ViolationType,
    ActionType,
    ProtectedContent,
    ContentViolation,
    TakedownRequest,
    BaseProtectionAdapter,
    YouTubeContentIDAdapter,
    FacebookRightsManagerAdapter,
    DMCATakedownAdapter,
    ProtectionAdapterFactory,
    ProtectionAdapterManager
)

# Email marketing adapters
from .email_marketing_adapters import (
    EmailPlatform,
    CampaignType,
    SegmentCriteria,
    EmailContact,
    EmailTemplate,
    EmailCampaign,
    CampaignStats,
    BaseEmailAdapter,
    MailchimpAdapter,
    SendGridAdapter,
    EmailAdapterFactory,
    EmailAdapterManager
)

# SEO platform adapters
from .seo_platform_adapters import (
    SEOPlatform,
    SEOMetricType,
    KeywordDifficulty,
    SEOKeyword,
    BacklinkProfile,
    TechnicalSEOIssue,
    ContentOptimization,
    CompetitorAnalysis,
    BaseSEOAdapter,
    GoogleSearchConsoleAdapter,
    SEMrushAdapter,
    SEOAdapterFactory,
    SEOAdapterManager
)

# Social media adapters
from .social_media_adapters import (
    SocialMediaAdapterFactory,
    SocialMediaPlatform,
    InstagramAdapter,
    YouTubeAdapter,
    TikTokAdapter,
    TwitterAdapter,
    FacebookAdapter,
    LinkedInAdapter
)

# Music streaming adapters  
from .music_streaming_adapters import (
    MusicAdapterFactory,
    MusicPlatform,
    SpotifyAdapter,
    SoundCloudAdapter,
    AppleMusicAdapter,
    YouTubeMusicAdapter,
    DeezerAdapter,
    TidalAdapter
)

# Payment gateway adapters
from .payment_gateway_adapters import (
    PaymentAdapterFactory,
    PaymentGateway,
    StripeAdapter,
    PayPalAdapter,
    WiseAdapter,
    SquareAdapter,
    RazorpayAdapter,
    AdyenAdapter
)

# Cloud storage adapters
from .cloud_storage_adapters import (
    CloudStorageAdapterFactory,
    CloudProvider,
    AWSS3Adapter,
    GoogleCloudStorageAdapter,
    MinIOAdapter,
    AzureBlobAdapter,
    DropboxAdapter,
    BackblazeAdapter
)

# Analytics service adapters
from .analytics_service_adapters import (
    AnalyticsAdapterFactory,
    AnalyticsPlatform,
    GoogleAnalyticsAdapter,
    MixpanelAdapter,
    SegmentAdapter,
    AmplitudeAdapter,
    HotjarAdapter,
    FullStoryAdapter
)

# Registry and management
from .adapter_registry import (
    AdapterRegistry,
    AdapterCategory,
    AdapterPriority,
    AdapterConfig,
    AdapterInstance,
    get_adapter_registry,
    adapter_context,
    get_social_media_adapter,
    get_music_adapter,
    get_payment_adapter,
    get_storage_adapter,
    get_analytics_adapter
)

# Module-level logger
logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Module metadata
MODULE_NAME = "adapters"
MODULE_DESCRIPTION = "Enterprise platform integration adapters"
SUPPORTED_PLATFORMS = {
    "ai_platform": ["openai", "anthropic", "hugging_face", "azure_openai", "cohere", "replicate", "google_palm"],
    "content_protection": ["youtube_content_id", "facebook_rights_manager", "dmca_takedown", "tiktok_copyright", "instagram_creator_studio"],
    "email_marketing": ["mailchimp", "sendgrid", "klaviyo", "constant_contact", "convertkit", "mailgun", "brevo", "hubspot"],
    "seo_platform": ["google_search_console", "semrush", "ahrefs", "moz", "brightedge", "conductor", "screaming_frog"],
    "social_media": ["instagram", "youtube", "tiktok", "twitter", "facebook", "linkedin"],
    "music_streaming": ["spotify", "soundcloud", "apple_music", "youtube_music", "deezer", "tidal"],
    "payment_gateway": ["stripe", "paypal", "wise", "square", "razorpay", "adyen"],
    "cloud_storage": ["aws_s3", "google_cloud", "minio", "azure_blob", "dropbox", "backblaze"],
    "analytics": ["google_analytics", "mixpanel", "segment", "amplitude", "hotjar", "fullstory"]
}

def get_supported_platforms(category: Optional[str] = None) -> Union[Dict[str, List[str]], List[str]]:
    """Get list of supported platforms by category or all categories."""    if category:
        return SUPPORTED_PLATFORMS.get(category, [])
    return SUPPORTED_PLATFORMS

def get_adapter_factory(category: AdapterCategory) -> Optional[Type]:
    """Get adapter factory class for a specific category."""    factories = {
        AdapterCategory.SOCIAL_MEDIA: SocialMediaAdapterFactory,
        AdapterCategory.MUSIC_STREAMING: MusicAdapterFactory,
        AdapterCategory.PAYMENT_GATEWAY: PaymentAdapterFactory,
        AdapterCategory.CLOUD_STORAGE: CloudStorageAdapterFactory,
        AdapterCategory.ANALYTICS_SERVICE: AnalyticsAdapterFactory
    }
    return factories.get(category)

def validate_platform_support(category: str, platform: str) -> bool:
    """Validate if a platform is supported in a category."""    supported = SUPPORTED_PLATFORMS.get(category, [])
    return platform.lower() in supported

def get_adapter_classes_by_category(category: AdapterCategory) -> List[Type[BasePlatformAdapter]]:
    """Get all adapter classes for a specific category."""    adapter_classes = {
        AdapterCategory.SOCIAL_MEDIA: [
            InstagramAdapter, YouTubeAdapter, TikTokAdapter,
            TwitterAdapter, FacebookAdapter, LinkedInAdapter
        ],
        AdapterCategory.MUSIC_STREAMING: [
            SpotifyAdapter, SoundCloudAdapter, AppleMusicAdapter,
            YouTubeMusicAdapter, DeezerAdapter, TidalAdapter
        ],
        AdapterCategory.PAYMENT_GATEWAY: [
            StripeAdapter, PayPalAdapter, WiseAdapter,
            SquareAdapter, RazorpayAdapter, AdyenAdapter
        ],
        AdapterCategory.CLOUD_STORAGE: [
            AWSS3Adapter, GoogleCloudStorageAdapter, MinIOAdapter,
            AzureBlobAdapter, DropboxAdapter, BackblazeAdapter
        ],
        AdapterCategory.ANALYTICS_SERVICE: [
            GoogleAnalyticsAdapter, MixpanelAdapter, SegmentAdapter,
            AmplitudeAdapter, HotjarAdapter, FullStoryAdapter
        ]
    }
    return adapter_classes.get(category, [])

def create_adapter_config(
    adapter_id: str,
    category: str,
    platform: str,
    credentials: Dict[str, Any],
    priority: str = "medium",
    enabled: bool = True,
    tenant_id: Optional[str] = None,
    custom_config: Optional[Dict[str, Any]] = None
) -> AdapterConfig:
    """Create adapter configuration from parameters."""    
    # Convert string parameters to enums
    category_enum = AdapterCategory(category.lower())
    priority_enum = AdapterPriority(priority.lower())
    
    # Create credentials object
    adapter_credentials = AdapterCredentials(
        api_key=credentials.get('api_key'),
        secret_key=credentials.get('secret_key'),
        access_token=credentials.get('access_token'),
        refresh_token=credentials.get('refresh_token'),
        additional_params=credentials.get('additional_params', {})
    )
    
    return AdapterConfig(
        adapter_id=adapter_id,
        category=category_enum,
        platform=platform,
        credentials=adapter_credentials,
        priority=priority_enum,
        enabled=enabled,
        tenant_id=tenant_id,
        custom_config=custom_config or {}
    )

async def initialize_adapter_system(redis_client=None) -> AdapterRegistry:
    """Initialize the adapter system with default configuration."""    registry = get_adapter_registry(redis_client)
    
    logger.info(f"Adapter system initialized")
    logger.info(f"Supported platforms: {len(sum(SUPPORTED_PLATFORMS.values(), []))}")
    logger.info(f"Categories: {list(SUPPORTED_PLATFORMS.keys())}")
    
    return registry

async def shutdown_adapter_system():
    """Shutdown the adapter system and cleanup resources."""    global _registry_instance
    
    if _registry_instance:
        # Unregister all adapters
        adapter_ids = list(_registry_instance.adapters.keys())
        for adapter_id in adapter_ids:
            await _registry_instance.unregister_adapter(adapter_id)
        
        # Cancel health monitoring
        if _registry_instance.health_check_task:
            _registry_instance.health_check_task.cancel()
        
        _registry_instance = None
        logger.info("Adapter system shutdown completed")

# Quick access adapters for common use cases
class QuickAdapters:
    """Quick access utility for common adapter operations."""    
    @staticmethod
    async def get_instagram_adapter(credentials: Dict[str, Any]) -> Optional[InstagramAdapter]:
        """Get Instagram adapter with credentials."""        adapter_creds = AdapterCredentials(**credentials)
        return await get_social_media_adapter("instagram", adapter_creds)
    
    @staticmethod
    async def get_youtube_adapter(credentials: Dict[str, Any]) -> Optional[YouTubeAdapter]:
        """Get YouTube adapter with credentials."""        adapter_creds = AdapterCredentials(**credentials)
        return await get_social_media_adapter("youtube", adapter_creds)
    
    @staticmethod
    async def get_spotify_adapter(credentials: Dict[str, Any]) -> Optional[SpotifyAdapter]:
        """Get Spotify adapter with credentials."""        adapter_creds = AdapterCredentials(**credentials)
        return await get_music_adapter("spotify", adapter_creds)
    
    @staticmethod
    async def get_stripe_adapter(credentials: Dict[str, Any]) -> Optional[StripeAdapter]:
        """Get Stripe adapter with credentials."""        adapter_creds = AdapterCredentials(**credentials)
        return await get_payment_adapter("stripe", adapter_creds)
    
    @staticmethod
    async def get_aws_s3_adapter(credentials: Dict[str, Any]) -> Optional[AWSS3Adapter]:
        """Get AWS S3 adapter with credentials."""        adapter_creds = AdapterCredentials(**credentials)
        return await get_storage_adapter("aws_s3", adapter_creds)
    
    @staticmethod
    async def get_google_analytics_adapter(credentials: Dict[str, Any]) -> Optional[GoogleAnalyticsAdapter]:
        """Get Google Analytics adapter with credentials."""        adapter_creds = AdapterCredentials(**credentials)
        return await get_analytics_adapter("google_analytics", adapter_creds)

# Export all public classes and functions
__all__ = [
    # Base classes
    'BasePlatformAdapter',
    'PlatformType',
    'AdapterStatus',
    'AuthenticationType',
    'AdapterCredentials',
    'RateLimitConfig',
    
    # Exceptions
    'AdapterError',
    'AuthenticationError',
    'RateLimitError',
    'PlatformError',
    'ConfigurationError',
    
    # Social media
    'SocialMediaAdapterFactory',
    'SocialMediaPlatform',
    'InstagramAdapter',
    'YouTubeAdapter',
    'TikTokAdapter',
    'TwitterAdapter',
    'FacebookAdapter',
    'LinkedInAdapter',
    
    # Music streaming
    'MusicAdapterFactory',
    'MusicPlatform',
    'SpotifyAdapter',
    'SoundCloudAdapter',
    'AppleMusicAdapter',
    'YouTubeMusicAdapter',
    'DeezerAdapter',
    'TidalAdapter',
    
    # Payment gateways
    'PaymentAdapterFactory',
    'PaymentGateway',
    'StripeAdapter',
    'PayPalAdapter',
    'WiseAdapter',
    'SquareAdapter',
    'RazorpayAdapter',
    'AdyenAdapter',
    
    # Cloud storage
    'CloudStorageAdapterFactory',
    'CloudProvider',
    'AWSS3Adapter',
    'GoogleCloudStorageAdapter',
    'MinIOAdapter',
    'AzureBlobAdapter',
    'DropboxAdapter',
    'BackblazeAdapter',
    
    # Analytics
    'AnalyticsAdapterFactory',
    'AnalyticsPlatform',
    'GoogleAnalyticsAdapter',
    'MixpanelAdapter',
    'SegmentAdapter',
    'AmplitudeAdapter',
    'HotjarAdapter',
    'FullStoryAdapter',
    
    # Registry and management
    'AdapterRegistry',
    'AdapterCategory',
    'AdapterPriority',
    'AdapterConfig',
    'AdapterInstance',
    'get_adapter_registry',
    'adapter_context',
    'get_social_media_adapter',
    'get_music_adapter',
    'get_payment_adapter',
    'get_storage_adapter',
    'get_analytics_adapter',
    
    # Utility functions
    'get_supported_platforms',
    'get_adapter_factory',
    'validate_platform_support',
    'get_adapter_classes_by_category',
    'create_adapter_config',
    'initialize_adapter_system',
    'shutdown_adapter_system',
    'QuickAdapters'
]

# Module initialization
logger.info(f"Adapters module loaded - Version {__version__}")
logger.info(f"Total supported platforms: {len(sum(SUPPORTED_PLATFORMS.values(), []))}")
logger.info(f"Available categories: {list(SUPPORTED_PLATFORMS.keys())}")
