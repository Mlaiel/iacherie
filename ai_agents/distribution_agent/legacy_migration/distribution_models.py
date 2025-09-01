"""Distribution Models for IA Influencer Agent - Professional Content Distribution Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚖️ LEGAL WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted to the full extent of the law.

🚀 Professional Team Expertise:
- Lead IA Developer: Advanced AI/ML Architecture
- Senior Backend Engineer: Enterprise-grade Infrastructure  
- ML Engineer: Deep Learning & Data Processing
- Database Architect: High-performance Data Management
- Security Engineer: Advanced Cybersecurity & Protection
- Microservices Architect: Scalable Distributed Systems
- Audio Engineer: Professional Audio Processing
- DevOps Engineer: Cloud Infrastructure & CI/CD
- IA Prompt Engineer: Advanced Prompt Engineering & LLM Integration
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel, Field, validator


class ContentType(str, Enum):
    """
Professional content type enumeration"""

    MUSIC = "music"
    VIDEO = "video" 
    PHOTO = "photo"
    BLOG = "blog"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    ARTICLE = "article"
    PORTFOLIO = "portfolio"


class PlatformType(str, Enum):
    """Professional platform type enumeration"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    TWITCH = "twitch"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    DAILYMOTION = "dailymotion"
    VIMEO = "vimeo"
    REDDIT = "reddit"
    MEDIUM = "medium"
    BEHANCE = "behance"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"


class DistributionStatus(str, Enum):
    """Professional distribution status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRAFT = "draft"
    REVIEWING = "reviewing"


class PlatformCapabilities(BaseModel):
    """Professional platform capabilities model"""
    max_file_size: int = Field(description="Maximum file size in bytes")
    supported_formats: List[str] = Field(description="Supported file formats")
    max_duration: Optional[int] = Field(None, description="Maximum duration in seconds")
    supports_scheduling: bool = Field(True, description="Supports scheduled publishing")
    supports_monetization: bool = Field(False, description="Supports monetization")
    supports_analytics: bool = Field(True, description="Provides analytics")
    supports_collaboration: bool = Field(False, description="Supports collaboration")
    requires_approval: bool = Field(False, description="Requires content approval")
    api_rate_limit: int = Field(100, description="API requests per minute")


class ContentMetadata(BaseModel):
    """Professional content metadata model"""
    title: str = Field(description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    language: str = Field("en", description="Content language")
    duration: Optional[int] = Field(None, description="Content duration in seconds")
    file_size: int = Field(description="File size in bytes")
    resolution: Optional[str] = Field(None, description="Video resolution")
    bitrate: Optional[int] = Field(None, description="Audio/video bitrate")
    format: str = Field(description="File format")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DistributionConfig(BaseModel):
    """Professional distribution configuration model"""
    platform: PlatformType = Field(description="Target platform")
    content_type: ContentType = Field(description="Content type")
    publish_immediately: bool = Field(True, description="Publish immediately")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled publish time")
    visibility: str = Field("public", description="Content visibility")
    enable_comments: bool = Field(True, description="Enable comments")
    enable_monetization: bool = Field(False, description="Enable monetization")
    notification_settings: Dict[str, bool] = Field(default_factory=dict)
    custom_thumbnail: Optional[str] = Field(None, description="Custom thumbnail path")
    custom_settings: Dict[str, Any] = Field(default_factory=dict)

    @validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        if v and v <= datetime.now():
            raise ValueError("Scheduled time must be in the future")
        return v


class DistributionRequest(BaseModel):
    """Professional distribution request model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(description="User identifier")
    content_path: str = Field(description="Path to content file")
    content_metadata: ContentMetadata = Field(description="Content metadata")
    distribution_configs: List[DistributionConfig] = Field(description="Distribution configurations")
    priority: int = Field(1, ge=1, le=10, description="Distribution priority (1-10)")
    max_retries: int = Field(3, description="Maximum retry attempts")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DistributionResult(BaseModel):
    """Professional distribution result model"""
    id: str = Field(description="Distribution result identifier")
    request_id: str = Field(description="Original request identifier")
    platform: PlatformType = Field(description="Target platform")
    status: DistributionStatus = Field(description="Distribution status")
    platform_id: Optional[str] = Field(None, description="Platform-specific content ID")
    platform_url: Optional[str] = Field(None, description="Platform content URL")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(0, description="Number of retry attempts")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DistributionAnalytics(BaseModel):
    """Professional distribution analytics model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    distribution_result_id: str = Field(description="Distribution result identifier")
    platform: PlatformType = Field(description="Platform")
    views: int = Field(0, description="Number of views")
    likes: int = Field(0, description="Number of likes")
    comments: int = Field(0, description="Number of comments")
    shares: int = Field(0, description="Number of shares")
    reach: int = Field(0, description="Content reach")
    engagement_rate: float = Field(0.0, description="Engagement rate percentage")
    click_through_rate: float = Field(0.0, description="Click-through rate percentage")
    conversion_rate: float = Field(0.0, description="Conversion rate percentage")
    revenue: float = Field(0.0, description="Generated revenue")
    collected_at: datetime = Field(default_factory=datetime.now)
    period_start: datetime = Field(description="Analytics period start")
    period_end: datetime = Field(description="Analytics period end")
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class PlatformCredentials(BaseModel):
    """Professional platform credentials model"""
    platform: PlatformType = Field(description="Platform identifier")
    user_id: str = Field(description="User identifier")
    access_token: str = Field(description="Access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration")
    client_id: str = Field(description="Client ID")
    client_secret: str = Field(description="Client secret")
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class CollaborationRequest(BaseModel):
    """Professional collaboration request model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = Field(description="Content creator identifier")
    collaborator_id: str = Field(description="Collaborator identifier")
    content_id: str = Field(description="Content identifier")
    collaboration_type: str = Field(description="Type of collaboration")
    platforms: List[PlatformType] = Field(description="Target platforms")
    revenue_split: Dict[str, float] = Field(description="Revenue sharing agreement")
    status: str = Field("pending", description="Collaboration status")
    terms: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(None, description="Request expiration")


class ContentProtection(BaseModel):
    """Professional content protection model"""
    content_id: str = Field(description="Content identifier")
    protection_level: str = Field("standard", description="Protection level")
    watermark_enabled: bool = Field(True, description="Watermark protection")
    drm_enabled: bool = Field(False, description="DRM protection")
    geographic_restrictions: List[str] = Field(default_factory=list)
    access_restrictions: Dict[str, Any] = Field(default_factory=dict)
    copyright_metadata: Dict[str, str] = Field(default_factory=dict)
    monitoring_enabled: bool = Field(True, description="Content monitoring")
    takedown_requests: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class DistributionBatch(BaseModel):
    """Professional distribution batch model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(description="User identifier")
    name: str = Field(description="Batch name")
    description: Optional[str] = Field(None, description="Batch description")
    requests: List[DistributionRequest] = Field(description="Distribution requests")
    status: str = Field("pending", description="Batch status")
    total_requests: int = Field(description="Total number of requests")
    completed_requests: int = Field(0, description="Completed requests count")
    failed_requests: int = Field(0, description="Failed requests count")
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = Field(None, description="Batch start time")
    completed_at: Optional[datetime] = Field(None, description="Batch completion time")


@dataclass
class PlatformRegistry:
    """Professional platform registry for managing all supported platforms"""
    
    def __post_init__(self):
        self._platforms = {
            PlatformType.YOUTUBE: PlatformCapabilities(
                max_file_size=256 * 1024 * 1024 * 1024,  # 256GB
                supported_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
                max_duration=12 * 60 * 60,  # 12 hours
                supports_monetization=True,
                supports_collaboration=True,
                api_rate_limit=10000
            ),
            PlatformType.INSTAGRAM: PlatformCapabilities(
                max_file_size=4 * 1024 * 1024 * 1024,  # 4GB
                supported_formats=["mp4", "mov", "jpg", "jpeg", "png"],
                max_duration=60 * 60,  # 1 hour
                supports_monetization=True,
                supports_collaboration=True,
                api_rate_limit=200
            ),
            PlatformType.TIKTOK: PlatformCapabilities(
                max_file_size=287 * 1024 * 1024,  # 287MB
                supported_formats=["mp4", "mov"],
                max_duration=10 * 60,  # 10 minutes
                supports_monetization=True,
                supports_collaboration=True,
                api_rate_limit=100
            ),
            PlatformType.SPOTIFY: PlatformCapabilities(
                max_file_size=650 * 1024 * 1024,  # 650MB
                supported_formats=["mp3", "wav", "flac", "ogg"],
                supports_monetization=True,
                requires_approval=True,
                api_rate_limit=1000
            ),
            PlatformType.TWITTER: PlatformCapabilities(
                max_file_size=512 * 1024 * 1024,  # 512MB
                supported_formats=["mp4", "mov", "gif", "jpg", "jpeg", "png"],
                max_duration=2 * 60 + 20,  # 2:20
                api_rate_limit=300
            ),
            # Additional platforms with their specific capabilities...
        }
    
    def get_platform_capabilities(self, platform: PlatformType) -> PlatformCapabilities:
        """Get capabilities for a specific platform"""
        return self._platforms.get(platform, PlatformCapabilities(
            max_file_size=100 * 1024 * 1024,  # Default 100MB
            supported_formats=["mp4", "jpg", "png"],
            api_rate_limit=100
        ))
    
    def is_content_supported(self, platform: PlatformType, content_metadata: ContentMetadata) -> bool:
        """Check if content is supported by platform"""
        capabilities = self.get_platform_capabilities(platform)
        
        # Check file size
        if content_metadata.file_size > capabilities.max_file_size:
            return False
            
        # Check format
        if content_metadata.format.lower() not in [f.lower() for f in capabilities.supported_formats]:
            return False
            
        # Check duration
        if capabilities.max_duration and content_metadata.duration:
            if content_metadata.duration > capabilities.max_duration:
                return False
                
        return True


# Export all models for external use
__all__ = [
    'ContentType',
    'PlatformType', 
    'DistributionStatus',
    'PlatformCapabilities',
    'ContentMetadata',
    'DistributionConfig',
    'DistributionRequest',
    'DistributionResult',
    'DistributionAnalytics',
    'PlatformCredentials',
    'CollaborationRequest',
    'ContentProtection',
    'DistributionBatch',
    'PlatformRegistry'
]
