"""
Platform Integration Schemas

Comprehensive Pydantic schemas for platform integrations, API management,
and multi-platform content distribution in the IA Influencer Agent platform.

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


class PlatformTypeEnum(str, Enum):
    """Types of supported platforms"""
    SOCIAL_MEDIA = "social_media"
    STREAMING_MUSIC = "streaming_music"
    STREAMING_VIDEO = "streaming_video"
    PODCAST = "podcast"
    IMAGE_SHARING = "image_sharing"
    BLOG = "blog"
    MARKETPLACE = "marketplace"
    GAMING = "gaming"
    PROFESSIONAL = "professional"
    NEWS = "news"
    COMMUNITY = "community"
    LIVE_STREAMING = "live_streaming"
    NFT_MARKETPLACE = "nft_marketplace"
    OTHER = "other"


class IntegrationStatusEnum(str, Enum):
    """Platform integration status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    SYNCING = "syncing"
    ACTIVE = "active"
    ERROR = "error"
    SUSPENDED = "suspended"
    RATE_LIMITED = "rate_limited"
    EXPIRED = "expired"
    REVOKED = "revoked"


class AuthMethodEnum(str, Enum):
    """Authentication methods"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    WEBHOOK = "webhook"
    CUSTOM = "custom"


class SyncFrequencyEnum(str, Enum):
    """Data synchronization frequencies"""
    REAL_TIME = "real_time"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    EVERY_30_MINUTES = "every_30_minutes"
    HOURLY = "hourly"
    EVERY_6_HOURS = "every_6_hours"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"


class ContentFormatEnum(str, Enum):
    """Content formats supported by platforms"""
    AUDIO_MP3 = "audio_mp3"
    AUDIO_WAV = "audio_wav"
    AUDIO_FLAC = "audio_flac"
    VIDEO_MP4 = "video_mp4"
    VIDEO_MOV = "video_mov"
    VIDEO_AVI = "video_avi"
    IMAGE_JPG = "image_jpg"
    IMAGE_PNG = "image_png"
    IMAGE_GIF = "image_gif"
    TEXT_PLAIN = "text_plain"
    TEXT_HTML = "text_html"
    TEXT_MARKDOWN = "text_markdown"
    DOCUMENT_PDF = "document_pdf"
    LIVESTREAM = "livestream"


class APICapabilitySchema(BaseModel):
    """Schema for platform API capabilities"""
    capability_name: str = Field(..., description="Name of the capability")
    enabled: bool = Field(..., description="Whether capability is enabled")
    rate_limit: Optional[int] = Field(None, description="Rate limit per hour")
    quota_remaining: Optional[int] = Field(None, description="Remaining quota")
    quota_reset: Optional[datetime] = Field(None, description="Quota reset time")
    supported_operations: List[str] = Field(..., description="Supported CRUD operations")
    required_permissions: List[str] = Field(..., description="Required permissions")
    data_formats: List[str] = Field(..., description="Supported data formats")
    
    class Config:
        json_schema_extra = {
            "example": {
                "capability_name": "upload_video",
                "enabled": True,
                "rate_limit": 100,
                "supported_operations": ["create", "read", "update", "delete"],
                "required_permissions": ["content_upload", "content_manage"]
            }
        }


class PlatformMetricsSchema(BaseModel):
    """Schema for platform-specific metrics"""
    followers_count: Optional[int] = Field(None, description="Number of followers")
    following_count: Optional[int] = Field(None, description="Number of following")
    posts_count: Optional[int] = Field(None, description="Number of posts")
    engagement_rate: Optional[float] = Field(None, description="Engagement rate")
    reach: Optional[int] = Field(None, description="Content reach")
    impressions: Optional[int] = Field(None, description="Content impressions")
    clicks: Optional[int] = Field(None, description="Content clicks")
    shares: Optional[int] = Field(None, description="Content shares")
    comments: Optional[int] = Field(None, description="Number of comments")
    likes: Optional[int] = Field(None, description="Number of likes")
    views: Optional[int] = Field(None, description="Number of views")
    streams: Optional[int] = Field(None, description="Number of streams")
    downloads: Optional[int] = Field(None, description="Number of downloads")
    revenue: Optional[Decimal] = Field(None, description="Revenue generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "followers_count": 15000,
                "posts_count": 250,
                "engagement_rate": 4.8,
                "reach": 50000,
                "impressions": 125000,
                "likes": 8500,
                "streams": 75000
            }
        }


class ContentDistributionSchema(BaseModel):
    """Schema for content distribution settings"""
    auto_publish: bool = Field(False, description="Enable automatic publishing")
    publish_delay: Optional[int] = Field(None, description="Delay in minutes before publishing")
    custom_caption: Optional[str] = Field(None, description="Custom caption for platform")
    custom_hashtags: Optional[List[str]] = Field(None, description="Platform-specific hashtags")
    content_format: ContentFormatEnum = Field(..., description="Content format for platform")
    quality_settings: Optional[Dict[str, Any]] = Field(None, description="Quality/encoding settings")
    privacy_settings: Optional[Dict[str, Any]] = Field(None, description="Privacy settings")
    monetization_enabled: bool = Field(False, description="Enable monetization")
    copyright_check: bool = Field(True, description="Enable copyright checking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "auto_publish": True,
                "publish_delay": 30,
                "custom_caption": "Check out my latest track!",
                "custom_hashtags": ["#music", "#electronic", "#newrelease"],
                "content_format": "audio_mp3",
                "monetization_enabled": True
            }
        }


class PlatformIntegrationBaseSchema(BaseModel):
    """Base schema for platform integrations"""
    platform_name: str = Field(..., description="Platform name")
    platform_type: PlatformTypeEnum = Field(..., description="Type of platform")
    platform_url: HttpUrl = Field(..., description="Platform base URL")
    platform_version: Optional[str] = Field(None, description="Platform API version")
    
    # Authentication details
    auth_method: AuthMethodEnum = Field(..., description="Authentication method")
    client_id: Optional[str] = Field(None, description="OAuth client ID")
    client_secret: Optional[str] = Field(None, description="OAuth client secret (encrypted)")
    api_key: Optional[str] = Field(None, description="API key (encrypted)")
    access_token: Optional[str] = Field(None, description="Access token (encrypted)")
    refresh_token: Optional[str] = Field(None, description="Refresh token (encrypted)")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    
    # Platform configuration
    webhook_url: Optional[HttpUrl] = Field(None, description="Webhook URL for notifications")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret")
    scopes: List[str] = Field(..., description="Granted permissions/scopes")
    
    # Sync settings
    sync_frequency: SyncFrequencyEnum = Field(..., description="Data sync frequency")
    last_sync: Optional[datetime] = Field(None, description="Last successful sync")
    next_sync: Optional[datetime] = Field(None, description="Next scheduled sync")
    
    # Content distribution settings
    distribution_settings: Optional[ContentDistributionSchema] = Field(None, description="Content distribution settings")
    
    @field_validator('platform_name')
    @classmethod
    def validate_platform_name(cls, v):
        """Validate platform name"""
        if not v or len(v.strip()) < 2:
            raise ValueError("Platform name must be at least 2 characters long")
        return v.lower().strip()


class PlatformIntegrationCreateSchema(PlatformIntegrationBaseSchema):
    """Schema for creating platform integrations"""
    user_id: PositiveInt = Field(..., description="User ID")
    
    # Initial setup
    auto_configure: bool = Field(True, description="Enable automatic configuration")
    test_connection: bool = Field(True, description="Test connection on creation")
    enable_notifications: bool = Field(True, description="Enable notifications")
    
    # Default settings
    default_privacy: str = Field("public", description="Default privacy setting")
    default_monetization: bool = Field(False, description="Default monetization setting")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "platform_name": "youtube",
                "platform_type": "streaming_video",
                "platform_url": "https://www.youtube.com",
                "auth_method": "oauth2",
                "scopes": ["upload", "analytics", "monetization"],
                "sync_frequency": "daily",
                "auto_configure": True
            }
        }


class PlatformIntegrationUpdateSchema(BaseModel):
    """Schema for updating platform integrations"""
    scopes: Optional[List[str]] = Field(None, description="Updated scopes")
    sync_frequency: Optional[SyncFrequencyEnum] = Field(None, description="Updated sync frequency")
    webhook_url: Optional[HttpUrl] = Field(None, description="Updated webhook URL")
    distribution_settings: Optional[ContentDistributionSchema] = Field(None, description="Updated distribution settings")
    enable_notifications: Optional[bool] = Field(None, description="Enable/disable notifications")
    active: Optional[bool] = Field(None, description="Enable/disable integration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sync_frequency": "every_30_minutes",
                "enable_notifications": True,
                "active": True
            }
        }


class PlatformIntegrationResponseSchema(PlatformIntegrationBaseSchema):
    """Schema for platform integration responses"""
    id: PositiveInt = Field(..., description="Unique integration ID")
    user_id: PositiveInt = Field(..., description="Owner user ID")
    
    # Status information
    status: IntegrationStatusEnum = Field(..., description="Integration status")
    health_score: float = Field(0.0, ge=0.0, le=1.0, description="Integration health score")
    error_message: Optional[str] = Field(None, description="Last error message")
    error_count: int = Field(0, description="Number of errors")
    
    # API capabilities
    capabilities: List[APICapabilitySchema] = Field(..., description="Platform API capabilities")
    supported_formats: List[ContentFormatEnum] = Field(..., description="Supported content formats")
    
    # Performance metrics
    api_calls_today: int = Field(0, description="API calls made today")
    rate_limit_remaining: Optional[int] = Field(None, description="Remaining rate limit")
    average_response_time: Optional[float] = Field(None, description="Average API response time")
    success_rate: float = Field(1.0, description="API success rate")
    
    # Platform metrics
    platform_metrics: Optional[PlatformMetricsSchema] = Field(None, description="Platform-specific metrics")
    
    # Content statistics
    content_published: int = Field(0, description="Number of content items published")
    content_synced: int = Field(0, description="Number of content items synced")
    total_reach: Optional[int] = Field(None, description="Total content reach")
    total_engagement: Optional[int] = Field(None, description="Total engagement")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    connected_at: Optional[datetime] = Field(None, description="Connection timestamp")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    # Configuration
    active: bool = Field(True, description="Whether integration is active")
    verified: bool = Field(False, description="Whether integration is verified")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "user_id": 123,
                "platform_name": "youtube",
                "status": "active",
                "health_score": 0.95,
                "api_calls_today": 150,
                "content_published": 25,
                "total_reach": 100000,
                "created_at": "2024-08-24T10:30:00Z",
                "verified": True
            }
        }


class PlatformSyncLogSchema(BaseModel):
    """Schema for platform synchronization logs"""
    sync_id: str = Field(..., description="Unique sync identifier")
    integration_id: PositiveInt = Field(..., description="Platform integration ID")
    sync_type: str = Field(..., description="Type of sync operation")
    
    # Sync details
    started_at: datetime = Field(..., description="Sync start time")
    completed_at: Optional[datetime] = Field(None, description="Sync completion time")
    duration_seconds: Optional[float] = Field(None, description="Sync duration in seconds")
    
    # Results
    status: str = Field(..., description="Sync status")
    items_processed: int = Field(0, description="Number of items processed")
    items_created: int = Field(0, description="Number of items created")
    items_updated: int = Field(0, description="Number of items updated")
    items_deleted: int = Field(0, description="Number of items deleted")
    items_failed: int = Field(0, description="Number of items failed")
    
    # Error handling
    errors: Optional[List[Dict]] = Field(None, description="List of errors encountered")
    warnings: Optional[List[Dict]] = Field(None, description="List of warnings")
    
    # Performance metrics
    api_calls_made: int = Field(0, description="Number of API calls made")
    data_transferred: Optional[int] = Field(None, description="Data transferred in bytes")
    rate_limit_hit: bool = Field(False, description="Whether rate limit was hit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sync_id": "SYNC-2024-001234",
                "integration_id": 12345,
                "sync_type": "content_metrics",
                "status": "completed",
                "items_processed": 50,
                "items_updated": 45,
                "api_calls_made": 15,
                "duration_seconds": 125.5
            }
        }


class PlatformAnalyticsSchema(BaseModel):
    """Schema for platform analytics and insights"""
    integration_id: PositiveInt = Field(..., description="Platform integration ID")
    analytics_period: str = Field(..., description="Analytics time period")
    
    # Performance metrics
    total_reach: int = Field(0, description="Total content reach")
    total_impressions: int = Field(0, description="Total impressions")
    total_engagement: int = Field(0, description="Total engagement")
    engagement_rate: float = Field(0.0, description="Average engagement rate")
    click_through_rate: float = Field(0.0, description="Click-through rate")
    
    # Audience insights
    audience_demographics: Optional[Dict[str, Any]] = Field(None, description="Audience demographics")
    top_countries: Optional[List[Dict]] = Field(None, description="Top countries by reach")
    peak_activity_hours: Optional[List[int]] = Field(None, description="Peak activity hours")
    
    # Content performance
    top_performing_content: Optional[List[Dict]] = Field(None, description="Top performing content")
    content_type_performance: Optional[Dict[str, float]] = Field(None, description="Performance by content type")
    hashtag_performance: Optional[Dict[str, int]] = Field(None, description="Hashtag performance")
    
    # Growth metrics
    follower_growth: Optional[List[Dict]] = Field(None, description="Follower growth over time")
    reach_growth: Optional[List[Dict]] = Field(None, description="Reach growth over time")
    engagement_trends: Optional[List[Dict]] = Field(None, description="Engagement trends")
    
    # Revenue metrics
    revenue_generated: Optional[Decimal] = Field(None, description="Revenue generated")
    monetized_views: Optional[int] = Field(None, description="Monetized views")
    cpm: Optional[Decimal] = Field(None, description="Cost per mille")
    
    class Config:
        json_schema_extra = {
            "example": {
                "integration_id": 12345,
                "analytics_period": "last_30_days",
                "total_reach": 250000,
                "total_engagement": 15000,
                "engagement_rate": 6.0,
                "revenue_generated": "450.75"
            }
        }


class CrossPlatformDistributionSchema(BaseModel):
    """Schema for cross-platform content distribution"""
    distribution_id: str = Field(..., description="Unique distribution identifier")
    user_id: PositiveInt = Field(..., description="User ID")
    content_id: PositiveInt = Field(..., description="Content ID")
    
    # Target platforms
    target_platforms: List[PositiveInt] = Field(..., description="Target platform integration IDs")
    distribution_strategy: str = Field(..., description="Distribution strategy")
    
    # Scheduling
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled distribution time")
    published_at: Optional[datetime] = Field(None, description="Actual publication time")
    
    # Status tracking
    overall_status: str = Field(..., description="Overall distribution status")
    platform_statuses: Dict[str, str] = Field(..., description="Status per platform")
    
    # Performance
    total_reach: Optional[int] = Field(None, description="Total reach across platforms")
    total_engagement: Optional[int] = Field(None, description="Total engagement across platforms")
    performance_by_platform: Optional[Dict[str, Dict]] = Field(None, description="Performance metrics by platform")
    
    class Config:
        json_schema_extra = {
            "example": {
                "distribution_id": "DIST-2024-001234",
                "user_id": 123,
                "content_id": 456,
                "target_platforms": [1, 2, 3],
                "distribution_strategy": "simultaneous",
                "overall_status": "completed",
                "total_reach": 75000
            }
        }


class PlatformComplianceSchema(BaseModel):
    """Schema for platform compliance and content policies"""
    platform_name: str = Field(..., description="Platform name")
    content_policies: List[Dict] = Field(..., description="Platform content policies")
    monetization_policies: List[Dict] = Field(..., description="Monetization policies")
    copyright_policies: List[Dict] = Field(..., description="Copyright policies")
    community_guidelines: List[Dict] = Field(..., description="Community guidelines")
    
    # Compliance checking
    auto_compliance_check: bool = Field(True, description="Enable automatic compliance checking")
    blocked_content_types: List[str] = Field([], description="Blocked content types")
    required_age_verification: bool = Field(False, description="Age verification required")
    geographic_restrictions: Optional[List[str]] = Field(None, description="Geographic restrictions")
    
    # Violation handling
    violation_thresholds: Dict[str, int] = Field(..., description="Violation thresholds")
    auto_removal_enabled: bool = Field(False, description="Enable automatic content removal")
    appeal_process: Optional[Dict] = Field(None, description="Appeal process information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform_name": "youtube",
                "auto_compliance_check": True,
                "blocked_content_types": ["explicit", "violent"],
                "required_age_verification": False,
                "auto_removal_enabled": False
            }
        }


# Export schemas
__all__ = [
    # Enums
    "PlatformTypeEnum",
    "IntegrationStatusEnum",
    "AuthMethodEnum",
    "SyncFrequencyEnum",
    "ContentFormatEnum",
    
    # Complex schemas
    "APICapabilitySchema",
    "PlatformMetricsSchema",
    "ContentDistributionSchema",
    "PlatformSyncLogSchema",
    "PlatformAnalyticsSchema",
    "CrossPlatformDistributionSchema",
    "PlatformComplianceSchema",
    
    # Main schemas
    "PlatformIntegrationBaseSchema",
    "PlatformIntegrationCreateSchema",
    "PlatformIntegrationUpdateSchema",
    "PlatformIntegrationResponseSchema"
]
