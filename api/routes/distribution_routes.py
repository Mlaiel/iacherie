"""
Distribution Routes - Multi-Platform Distribution & Publishing API
Enterprise distribution system supporting 35+ platforms with automated publishing and analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import asyncio

# Enterprise Security
security = HTTPBearer()

router = APIRouter(
    prefix="/distribution",
    tags=["distribution"],
    responses={404: {"description": "Not found"}}
)

# ========================================
# ENUMS & CONSTANTS
# ========================================

class PlatformType(str, Enum):
    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORM = "video_platform"
    AUDIO_PLATFORM = "audio_platform"
    STREAMING_SERVICE = "streaming_service"
    BLOG_PLATFORM = "blog_platform"
    MARKETPLACE = "marketplace"
    PROFESSIONAL_NETWORK = "professional_network"

class ContentFormat(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"

class DistributionStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"
    PROCESSING = "processing"
    DRAFT = "draft"

class PlatformStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"

class OptimizationType(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"
    AI_ENHANCED = "ai_enhanced"
    PLATFORM_SPECIFIC = "platform_specific"

# ========================================
# SUPPORTED PLATFORMS
# ========================================

SUPPORTED_PLATFORMS = {
    # Social Media Platforms
    "youtube": {
        "name": "YouTube",
        "type": PlatformType.VIDEO_PLATFORM,
        "formats": [ContentFormat.VIDEO, ContentFormat.SHORT],
        "max_video_size_gb": 256,
        "max_duration_hours": 12,
        "supports_scheduling": True,
        "supports_analytics": True,
        "api_available": True
    },
    "instagram": {
        "name": "Instagram",
        "type": PlatformType.SOCIAL_MEDIA,
        "formats": [ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.REEL, ContentFormat.STORY],
        "max_video_size_gb": 4,
        "max_duration_minutes": 60,
        "supports_scheduling": True,
        "supports_analytics": True,
        "api_available": True
    },
    "tiktok": {
        "name": "TikTok",
        "type": PlatformType.SOCIAL_MEDIA,
        "formats": [ContentFormat.VIDEO, ContentFormat.SHORT],
        "max_video_size_gb": 4,
        "max_duration_minutes": 10,
        "supports_scheduling": True,
        "supports_analytics": True,
        "api_available": True
    },
    "facebook": {
        "name": "Facebook",
        "type": PlatformType.SOCIAL_MEDIA,
        "formats": [ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.TEXT, ContentFormat.LIVESTREAM],
        "max_video_size_gb": 10,
        "max_duration_hours": 4,
        "supports_scheduling": True,
        "supports_analytics": True,
        "api_available": True
    },
    "twitter": {
        "name": "Twitter/X",
        "type": PlatformType.SOCIAL_MEDIA,
        "formats": [ContentFormat.TEXT, ContentFormat.IMAGE, ContentFormat.VIDEO],
        "max_video_size_gb": 0.5,
        "max_duration_minutes": 2.2,
        "supports_scheduling": True,
        "supports_analytics": True,
        "api_available": True
    },
    "linkedin": {
        "name": "LinkedIn",
        "type": PlatformType.PROFESSIONAL_NETWORK,
        "formats": [ContentFormat.TEXT, ContentFormat.IMAGE, ContentFormat.VIDEO],
        "max_video_size_gb": 5,
        "max_duration_minutes": 10,
        "supports_scheduling": True,
        "supports_analytics": True,
        "api_available": True
    },
    
    # Audio Platforms
    "spotify": {
        "name": "Spotify",
        "type": PlatformType.AUDIO_PLATFORM,
        "formats": [ContentFormat.AUDIO, ContentFormat.PODCAST],
        "max_file_size_gb": 1,
        "supports_scheduling": False,
        "supports_analytics": True,
        "api_available": True
    },
    "apple_music": {
        "name": "Apple Music",
        "type": PlatformType.AUDIO_PLATFORM,
        "formats": [ContentFormat.AUDIO, ContentFormat.PODCAST],
        "max_file_size_gb": 1,
        "supports_scheduling": False,
        "supports_analytics": True,
        "api_available": True
    },
    "soundcloud": {
        "name": "SoundCloud",
        "type": PlatformType.AUDIO_PLATFORM,
        "formats": [ContentFormat.AUDIO],
        "max_file_size_gb": 1,
        "supports_scheduling": True,
        "supports_analytics": True,
        "api_available": True
    },
    
    # Additional platforms (35+ total)
    "pinterest": {"name": "Pinterest", "type": PlatformType.SOCIAL_MEDIA},
    "snapchat": {"name": "Snapchat", "type": PlatformType.SOCIAL_MEDIA},
    "discord": {"name": "Discord", "type": PlatformType.SOCIAL_MEDIA},
    "reddit": {"name": "Reddit", "type": PlatformType.SOCIAL_MEDIA},
    "tumblr": {"name": "Tumblr", "type": PlatformType.BLOG_PLATFORM},
    "medium": {"name": "Medium", "type": PlatformType.BLOG_PLATFORM},
    "twitch": {"name": "Twitch", "type": PlatformType.STREAMING_SERVICE},
    "vimeo": {"name": "Vimeo", "type": PlatformType.VIDEO_PLATFORM},
    "dailymotion": {"name": "Dailymotion", "type": PlatformType.VIDEO_PLATFORM},
    "behance": {"name": "Behance", "type": PlatformType.PROFESSIONAL_NETWORK},
    "dribbble": {"name": "Dribbble", "type": PlatformType.PROFESSIONAL_NETWORK},
    "flickr": {"name": "Flickr", "type": PlatformType.SOCIAL_MEDIA},
    "deviantart": {"name": "DeviantArt", "type": PlatformType.SOCIAL_MEDIA},
    "patreon": {"name": "Patreon", "type": PlatformType.MARKETPLACE},
    "onlyfans": {"name": "OnlyFans", "type": PlatformType.MARKETPLACE},
    "substack": {"name": "Substack", "type": PlatformType.BLOG_PLATFORM},
    "wordpress": {"name": "WordPress", "type": PlatformType.BLOG_PLATFORM},
    "ghost": {"name": "Ghost", "type": PlatformType.BLOG_PLATFORM},
    "anchor": {"name": "Anchor", "type": PlatformType.AUDIO_PLATFORM},
    "castbox": {"name": "Castbox", "type": PlatformType.AUDIO_PLATFORM},
    "overcast": {"name": "Overcast", "type": PlatformType.AUDIO_PLATFORM},
    "pocket_casts": {"name": "Pocket Casts", "type": PlatformType.AUDIO_PLATFORM},
    "google_podcasts": {"name": "Google Podcasts", "type": PlatformType.AUDIO_PLATFORM},
    "amazon_music": {"name": "Amazon Music", "type": PlatformType.AUDIO_PLATFORM},
    "deezer": {"name": "Deezer", "type": PlatformType.AUDIO_PLATFORM},
    "bandcamp": {"name": "Bandcamp", "type": PlatformType.AUDIO_PLATFORM},
    "clubhouse": {"name": "Clubhouse", "type": PlatformType.AUDIO_PLATFORM},
    "spaces": {"name": "Twitter Spaces", "type": PlatformType.AUDIO_PLATFORM},
    "telegram": {"name": "Telegram", "type": PlatformType.SOCIAL_MEDIA},
    "whatsapp": {"name": "WhatsApp Business", "type": PlatformType.SOCIAL_MEDIA},
    "wechat": {"name": "WeChat", "type": PlatformType.SOCIAL_MEDIA},
    "weibo": {"name": "Weibo", "type": PlatformType.SOCIAL_MEDIA},
    "line": {"name": "LINE", "type": PlatformType.SOCIAL_MEDIA},
    "viber": {"name": "Viber", "type": PlatformType.SOCIAL_MEDIA},
    "mastodon": {"name": "Mastodon", "type": PlatformType.SOCIAL_MEDIA}
}

# ========================================
# PYDANTIC MODELS
# ========================================

class PlatformConnection(BaseModel):
    platform_id: str = Field(..., description="Platform identifier")
    account_id: str = Field(..., description="User account ID on platform")
    account_name: str = Field(..., description="Display name on platform")
    access_token: str = Field(..., description="OAuth access token")
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)
    status: PlatformStatus = Field(default=PlatformStatus.ACTIVE)
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    api_quota: Dict[str, int] = Field(default_factory=dict)

class ContentFormatting(BaseModel):
    platform_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    tags: List[str] = Field(default_factory=list, max_items=30)
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    privacy_level: str = Field(default="public", pattern="^(public|unlisted|private)$")
    monetization_enabled: bool = Field(default=True)
    comments_enabled: bool = Field(default=True)
    age_restriction: Optional[str] = None

class DistributionRequest(BaseModel):
    content_id: str = Field(..., description="Content ID to distribute")
    platforms: List[str] = Field(..., min_items=1, description="Target platforms")
    schedule_time: Optional[datetime] = None
    auto_optimize: bool = Field(default=True)
    platform_formatting: Dict[str, ContentFormatting] = Field(default_factory=dict)
    cross_post: bool = Field(default=False)
    notify_on_completion: bool = Field(default=True)
    retry_on_failure: bool = Field(default=True)
    max_retries: int = Field(default=3, ge=0, le=10)

class DistributionJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    platform_id: str
    status: DistributionStatus = Field(default=DistributionStatus.PENDING)
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    optimization_applied: OptimizationType = Field(default=OptimizationType.AUTO)
    formatting_used: Optional[ContentFormatting] = None
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DistributionBatch(BaseModel):
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    total_platforms: int = Field(..., ge=1)
    completed_platforms: int = Field(default=0, ge=0)
    failed_platforms: int = Field(default=0, ge=0)
    jobs: List[DistributionJob] = Field(default_factory=list)
    overall_status: str = Field(default="in_progress")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None

class PlatformAnalytics(BaseModel):
    platform_id: str
    content_id: str
    platform_post_id: str
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    click_through_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    engagement_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    reach: int = Field(default=0, ge=0)
    impressions: int = Field(default=0, ge=0)
    revenue_generated: Decimal = Field(default=Decimal("0.00"), ge=0)
    demographics: Dict[str, Any] = Field(default_factory=dict)
    geographic_data: Dict[str, int] = Field(default_factory=dict)
    time_series_data: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class CrossPlatformAnalytics(BaseModel):
    content_id: str
    total_platforms: int
    total_views: int
    total_engagement: int
    total_revenue: Decimal
    best_performing_platform: Dict[str, Any]
    worst_performing_platform: Dict[str, Any]
    platform_breakdown: List[PlatformAnalytics]
    audience_overlap: Dict[str, float] = Field(default_factory=dict)
    optimal_posting_times: Dict[str, str] = Field(default_factory=dict)
    content_performance_score: float = Field(..., ge=0.0, le=100.0)
    recommendations: List[str] = Field(default_factory=list)

class AutoOptimization(BaseModel):
    content_id: str
    platform_id: str
    optimization_type: OptimizationType
    original_formatting: ContentFormatting
    optimized_formatting: ContentFormatting
    improvements_made: List[str] = Field(default_factory=list)
    expected_performance_gain: float = Field(default=0.0, ge=0.0, le=100.0)
    ai_confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    a_b_test_enabled: bool = Field(default=False)

# ========================================
# DEPENDENCY FUNCTIONS
# ========================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Extract user information from JWT token"""
    return {
        "id": "user_123",
        "email": "creator@example.com",
        "name": "Demo Creator",
        "subscription_tier": "enterprise"
    }

async def validate_distribution_access(user: Dict = Depends(get_current_user)) -> bool:
    """Validate user has access to distribution features"""
    return user["subscription_tier"] in ["pro", "enterprise", "unlimited"]

# ========================================
# PLATFORM MANAGEMENT
# ========================================

@router.get("/platforms")
async def get_supported_platforms(
    platform_type: Optional[PlatformType] = Query(None),
    content_format: Optional[ContentFormat] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """Get list of supported platforms with capabilities"""
    
    platforms = []
    for platform_id, platform_info in SUPPORTED_PLATFORMS.items():
        if platform_type and platform_info.get("type") != platform_type:
            continue
        if content_format and platform_info.get("formats") and content_format not in platform_info.get("formats", []):
            continue
        
        platforms.append({
            "platform_id": platform_id,
            "name": platform_info["name"],
            "type": platform_info.get("type", PlatformType.SOCIAL_MEDIA),
            "supported_formats": platform_info.get("formats", []),
            "capabilities": {
                "scheduling": platform_info.get("supports_scheduling", False),
                "analytics": platform_info.get("supports_analytics", False),
                "api_available": platform_info.get("api_available", False),
                "max_file_size_gb": platform_info.get("max_video_size_gb", platform_info.get("max_file_size_gb", 1)),
                "max_duration": platform_info.get("max_duration_hours", platform_info.get("max_duration_minutes", 60))
            }
        })
    
    return {
        "total_platforms": len(platforms),
        "platforms": platforms,
        "platform_types": list(PlatformType),
        "content_formats": list(ContentFormat)
    }

@router.get("/platforms/connected", response_model=List[PlatformConnection])
async def get_connected_platforms(
    status: Optional[PlatformStatus] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """Get user's connected platforms"""
    
    # Mock connected platforms
    connections = [
        PlatformConnection(
            platform_id="youtube",
            account_id="UC_demo_channel_123",
            account_name="Demo Creator Channel",
            access_token="ya29.a0Ae4lvC123...",
            refresh_token="1//0ABC123...",
            token_expires_at=datetime.utcnow() + timedelta(hours=1),
            permissions=["upload", "analytics", "manage"],
            status=PlatformStatus.ACTIVE,
            connected_at=datetime.utcnow() - timedelta(days=30),
            last_used=datetime.utcnow() - timedelta(hours=2),
            api_quota={"uploads_per_day": 100, "requests_per_minute": 1000}
        ),
        PlatformConnection(
            platform_id="instagram",
            account_id="demo_creator_ig",
            account_name="Demo Creator",
            access_token="IGQVJXabc123...",
            permissions=["publish", "insights"],
            status=PlatformStatus.ACTIVE,
            connected_at=datetime.utcnow() - timedelta(days=15),
            last_used=datetime.utcnow() - timedelta(minutes=30),
            api_quota={"posts_per_day": 25, "requests_per_hour": 200}
        ),
        PlatformConnection(
            platform_id="spotify",
            account_id="demo_artist_spotify",
            account_name="Demo Artist",
            access_token="BQC123abc...",
            permissions=["upload", "analytics"],
            status=PlatformStatus.ACTIVE,
            connected_at=datetime.utcnow() - timedelta(days=45),
            last_used=datetime.utcnow() - timedelta(days=1),
            api_quota={"uploads_per_month": 50}
        )
    ]
    
    if status:
        connections = [c for c in connections if c.status == status]
    
    return connections

@router.post("/platforms/{platform_id}/connect")
async def connect_platform(
    platform_id: str,
    authorization_code: str = Query(..., description="OAuth authorization code"),
    redirect_uri: str = Query(..., description="OAuth redirect URI"),
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Connect to a new platform"""
    
    if platform_id not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {platform_id} is not supported"
        )
    
    # Schedule background OAuth flow completion
    background_tasks.add_task(complete_platform_connection, platform_id, authorization_code, current_user["id"])
    
    return {
        "message": f"Platform {platform_id} connection initiated",
        "platform_id": platform_id,
        "platform_name": SUPPORTED_PLATFORMS[platform_id]["name"],
        "status": "connecting",
        "estimated_completion": datetime.utcnow() + timedelta(minutes=2)
    }

@router.delete("/platforms/{platform_id}/disconnect")
async def disconnect_platform(
    platform_id: str,
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Disconnect from a platform"""
    
    # Schedule background disconnection
    background_tasks.add_task(handle_platform_disconnection, platform_id, current_user["id"])
    
    return {
        "message": f"Platform {platform_id} disconnected",
        "platform_id": platform_id,
        "disconnected_at": datetime.utcnow()
    }

# ========================================
# CONTENT DISTRIBUTION
# ========================================

@router.post("/publish", response_model=DistributionBatch)
async def distribute_content(
    distribution_request: DistributionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    has_access: bool = Depends(validate_distribution_access)
):
    """Distribute content to multiple platforms"""
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Distribution features require Pro subscription or higher"
        )
    
    # Validate platforms
    invalid_platforms = [p for p in distribution_request.platforms if p not in SUPPORTED_PLATFORMS]
    if invalid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platforms: {invalid_platforms}"
        )
    
    # Create distribution jobs
    jobs = []
    for platform_id in distribution_request.platforms:
        job = DistributionJob(
            content_id=distribution_request.content_id,
            platform_id=platform_id,
            scheduled_for=distribution_request.schedule_time,
            optimization_applied=OptimizationType.AI_ENHANCED if distribution_request.auto_optimize else OptimizationType.MANUAL,
            formatting_used=distribution_request.platform_formatting.get(platform_id)
        )
        jobs.append(job)
    
    # Create batch
    batch = DistributionBatch(
        content_id=distribution_request.content_id,
        total_platforms=len(distribution_request.platforms),
        jobs=jobs,
        estimated_completion=datetime.utcnow() + timedelta(minutes=len(distribution_request.platforms) * 2)
    )
    
    # Schedule background distribution
    background_tasks.add_task(process_distribution_batch, batch, distribution_request, current_user["id"])
    
    return batch

@router.get("/jobs/{batch_id}", response_model=DistributionBatch)
async def get_distribution_batch(
    batch_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get distribution batch status"""
    
    # Mock batch data
    return DistributionBatch(
        batch_id=batch_id,
        content_id="content_demo_123",
        total_platforms=3,
        completed_platforms=2,
        failed_platforms=0,
        jobs=[
            DistributionJob(
                job_id="job_001",
                content_id="content_demo_123",
                platform_id="youtube",
                status=DistributionStatus.PUBLISHED,
                platform_post_id="abc123xyz",
                platform_url="https://youtube.com/watch?v=abc123xyz",
                started_at=datetime.utcnow() - timedelta(minutes=10),
                completed_at=datetime.utcnow() - timedelta(minutes=5),
                optimization_applied=OptimizationType.AI_ENHANCED
            ),
            DistributionJob(
                job_id="job_002",
                content_id="content_demo_123",
                platform_id="instagram",
                status=DistributionStatus.PUBLISHED,
                platform_post_id="ig_post_456",
                platform_url="https://instagram.com/p/ig_post_456",
                started_at=datetime.utcnow() - timedelta(minutes=8),
                completed_at=datetime.utcnow() - timedelta(minutes=3),
                optimization_applied=OptimizationType.AI_ENHANCED
            ),
            DistributionJob(
                job_id="job_003",
                content_id="content_demo_123",
                platform_id="tiktok",
                status=DistributionStatus.PUBLISHING,
                started_at=datetime.utcnow() - timedelta(minutes=2),
                optimization_applied=OptimizationType.AI_ENHANCED
            )
        ],
        overall_status="in_progress",
        estimated_completion=datetime.utcnow() + timedelta(minutes=3)
    )

@router.get("/jobs")
async def get_distribution_jobs(
    content_id: Optional[str] = Query(None),
    platform_id: Optional[str] = Query(None),
    status: Optional[DistributionStatus] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """Get distribution jobs with filtering"""
    
    # Mock jobs data
    jobs = [
        {
            "job_id": "job_001",
            "content_id": "content_demo_123",
            "platform_id": "youtube",
            "status": DistributionStatus.PUBLISHED,
            "platform_url": "https://youtube.com/watch?v=abc123xyz",
            "completed_at": datetime.utcnow() - timedelta(hours=2),
            "performance_metrics": {"views": 1250, "likes": 89, "comments": 23}
        },
        {
            "job_id": "job_002",
            "content_id": "content_demo_456",
            "platform_id": "instagram",
            "status": DistributionStatus.SCHEDULED,
            "scheduled_for": datetime.utcnow() + timedelta(hours=2)
        },
        {
            "job_id": "job_003",
            "content_id": "content_demo_789",
            "platform_id": "tiktok",
            "status": DistributionStatus.FAILED,
            "error_message": "Content format not supported",
            "retry_count": 2
        }
    ]
    
    # Apply filters
    if content_id:
        jobs = [j for j in jobs if j["content_id"] == content_id]
    if platform_id:
        jobs = [j for j in jobs if j["platform_id"] == platform_id]
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    return {
        "jobs": jobs[:limit],
        "total_jobs": len(jobs),
        "filters_applied": {
            "content_id": content_id,
            "platform_id": platform_id,
            "status": status
        }
    }

@router.post("/jobs/{job_id}/retry")
async def retry_distribution_job(
    job_id: str,
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Retry a failed distribution job"""
    
    # Schedule background retry
    background_tasks.add_task(retry_distribution, job_id, current_user["id"])
    
    return {
        "message": f"Distribution job {job_id} retry initiated",
        "job_id": job_id,
        "retry_started_at": datetime.utcnow()
    }

# ========================================
# CONTENT OPTIMIZATION
# ========================================

@router.post("/optimize", response_model=List[AutoOptimization])
async def optimize_content_for_platforms(
    content_id: str = Query(..., description="Content ID to optimize"),
    platforms: List[str] = Query(..., min_items=1, description="Target platforms"),
    current_user: Dict = Depends(get_current_user),
    has_access: bool = Depends(validate_distribution_access),
    background_tasks: BackgroundTasks
):
    """AI-powered content optimization for multiple platforms"""
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content optimization requires premium access"
        )
    
    # Schedule background optimization
    background_tasks.add_task(perform_ai_optimization, content_id, platforms, current_user["id"])
    
    # Return immediate optimizations
    optimizations = []
    for platform_id in platforms:
        original_formatting = ContentFormatting(
            platform_id=platform_id,
            title="Original Content Title",
            description="Original content description without optimization.",
            tags=["general", "content"]
        )
        
        optimized_formatting = ContentFormatting(
            platform_id=platform_id,
            title=f"Optimized: Original Content Title - {SUPPORTED_PLATFORMS.get(platform_id, {}).get('name', platform_id)}",
            description="AI-optimized content description with platform-specific keywords and engagement triggers.",
            tags=["optimized", "ai-enhanced", "trending", platform_id],
            custom_fields={"optimized_for": platform_id, "ai_score": 0.92}
        )
        
        optimization = AutoOptimization(
            content_id=content_id,
            platform_id=platform_id,
            optimization_type=OptimizationType.AI_ENHANCED,
            original_formatting=original_formatting,
            optimized_formatting=optimized_formatting,
            improvements_made=[
                "Enhanced title with platform-specific keywords",
                "Optimized description for engagement",
                "Added trending tags",
                "Improved metadata structure"
            ],
            expected_performance_gain=25.5,
            ai_confidence_score=0.92
        )
        optimizations.append(optimization)
    
    return optimizations

@router.get("/analytics/{content_id}", response_model=CrossPlatformAnalytics)
async def get_cross_platform_analytics(
    content_id: str,
    time_period: str = Query("7d", pattern="^(24h|7d|30d|90d)$"),
    current_user: Dict = Depends(get_current_user),
    has_access: bool = Depends(validate_distribution_access)
):
    """Get cross-platform analytics for distributed content"""
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-platform analytics require premium access"
        )
    
    # Mock analytics data
    platform_breakdown = [
        PlatformAnalytics(
            platform_id="youtube",
            content_id=content_id,
            platform_post_id="abc123xyz",
            views=25000,
            likes=1250,
            shares=89,
            comments=156,
            saves=234,
            click_through_rate=8.5,
            engagement_rate=6.2,
            reach=28000,
            impressions=45000,
            revenue_generated=Decimal("125.75"),
            demographics={"age_18_24": 35, "age_25_34": 42, "age_35_44": 23},
            geographic_data={"US": 12000, "UK": 5000, "DE": 3500, "FR": 2800, "CA": 1700}
        ),
        PlatformAnalytics(
            platform_id="instagram",
            content_id=content_id,
            platform_post_id="ig_post_456",
            views=18000,
            likes=1890,
            shares=234,
            comments=89,
            saves=456,
            click_through_rate=12.3,
            engagement_rate=14.8,
            reach=22000,
            impressions=35000,
            revenue_generated=Decimal("89.50"),
            demographics={"age_18_24": 58, "age_25_34": 28, "age_35_44": 14},
            geographic_data={"US": 8000, "UK": 3500, "DE": 2200, "FR": 2000, "CA": 1300, "AU": 1000}
        ),
        PlatformAnalytics(
            platform_id="tiktok",
            content_id=content_id,
            platform_post_id="tiktok_789",
            views=45000,
            likes=3200,
            shares=567,
            comments=234,
            saves=890,
            click_through_rate=15.7,
            engagement_rate=10.9,
            reach=52000,
            impressions=78000,
            revenue_generated=Decimal("67.25"),
            demographics={"age_16_24": 67, "age_25_34": 23, "age_35_44": 10},
            geographic_data={"US": 18000, "UK": 8000, "DE": 5500, "FR": 4200, "CA": 3800, "AU": 2500, "MX": 3000}
        )
    ]
    
    total_views = sum(p.views for p in platform_breakdown)
    total_engagement = sum(p.likes + p.shares + p.comments + p.saves for p in platform_breakdown)
    total_revenue = sum(p.revenue_generated for p in platform_breakdown)
    
    best_platform = max(platform_breakdown, key=lambda p: p.engagement_rate)
    worst_platform = min(platform_breakdown, key=lambda p: p.engagement_rate)
    
    return CrossPlatformAnalytics(
        content_id=content_id,
        total_platforms=len(platform_breakdown),
        total_views=total_views,
        total_engagement=total_engagement,
        total_revenue=total_revenue,
        best_performing_platform={
            "platform_id": best_platform.platform_id,
            "engagement_rate": best_platform.engagement_rate,
            "views": best_platform.views
        },
        worst_performing_platform={
            "platform_id": worst_platform.platform_id,
            "engagement_rate": worst_platform.engagement_rate,
            "views": worst_platform.views
        },
        platform_breakdown=platform_breakdown,
        audience_overlap={
            "youtube_instagram": 45.2,
            "youtube_tiktok": 32.8,
            "instagram_tiktok": 38.7
        },
        optimal_posting_times={
            "youtube": "Tuesday 2:00 PM",
            "instagram": "Thursday 11:00 AM",
            "tiktok": "Friday 7:00 PM"
        },
        content_performance_score=87.3,
        recommendations=[
            "Focus more on TikTok for this content type",
            "Optimize posting times for better reach",
            "Cross-promote between platforms to increase overlap",
            "Consider platform-specific content variations"
        ]
    )

# ========================================
# SCHEDULING & AUTOMATION
# ========================================

@router.post("/schedule")
async def schedule_distribution(
    content_id: str = Query(..., description="Content ID to schedule"),
    platforms: List[str] = Query(..., min_items=1),
    schedule_times: Dict[str, datetime] = Query(..., description="Platform-specific schedule times"),
    current_user: Dict = Depends(get_current_user),
    has_access: bool = Depends(validate_distribution_access),
    background_tasks: BackgroundTasks
):
    """Schedule content distribution across platforms"""
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content scheduling requires premium access"
        )
    
    # Validate platforms support scheduling
    non_scheduling_platforms = [
        p for p in platforms 
        if not SUPPORTED_PLATFORMS.get(p, {}).get("supports_scheduling", False)
    ]
    
    if non_scheduling_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platforms {non_scheduling_platforms} do not support scheduling"
        )
    
    # Schedule background job
    background_tasks.add_task(setup_scheduled_distribution, content_id, platforms, schedule_times, current_user["id"])
    
    return {
        "message": f"Scheduled distribution for {len(platforms)} platforms",
        "content_id": content_id,
        "platforms": platforms,
        "schedule_times": schedule_times,
        "scheduled_at": datetime.utcnow()
    }

@router.get("/schedule")
async def get_scheduled_distributions(
    upcoming_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """Get scheduled distributions"""
    
    # Mock scheduled distributions
    schedules = [
        {
            "schedule_id": "sched_001",
            "content_id": "content_upcoming_1",
            "platform_id": "youtube",
            "scheduled_for": datetime.utcnow() + timedelta(hours=6),
            "status": "scheduled",
            "title": "Upcoming YouTube Video"
        },
        {
            "schedule_id": "sched_002",
            "content_id": "content_upcoming_2",
            "platform_id": "instagram",
            "scheduled_for": datetime.utcnow() + timedelta(days=1),
            "status": "scheduled",
            "title": "Tomorrow's Instagram Post"
        },
        {
            "schedule_id": "sched_003",
            "content_id": "content_past_1",
            "platform_id": "tiktok",
            "scheduled_for": datetime.utcnow() - timedelta(hours=2),
            "status": "completed",
            "title": "Published TikTok Video"
        }
    ]
    
    if upcoming_only:
        schedules = [s for s in schedules if s["scheduled_for"] > datetime.utcnow()]
    
    return {
        "scheduled_distributions": schedules[:limit],
        "total_scheduled": len(schedules),
        "upcoming_count": len([s for s in schedules if s["scheduled_for"] > datetime.utcnow()])
    }

# ========================================
# BACKGROUND TASKS
# ========================================

async def complete_platform_connection(platform_id: str, auth_code: str, user_id: str):
    """Complete OAuth platform connection"""
    await asyncio.sleep(30)  # Simulate OAuth flow
    print(f"Connected {platform_id} for user {user_id}")

async def handle_platform_disconnection(platform_id: str, user_id: str):
    """Handle platform disconnection"""
    await asyncio.sleep(5)
    print(f"Disconnected {platform_id} for user {user_id}")

async def process_distribution_batch(batch: DistributionBatch, request: DistributionRequest, user_id: str):
    """Process distribution batch in background"""
    for job in batch.jobs:
        await asyncio.sleep(30)  # Simulate platform API calls
        print(f"Published content {job.content_id} to {job.platform_id}")

async def retry_distribution(job_id: str, user_id: str):
    """Retry failed distribution"""
    await asyncio.sleep(20)
    print(f"Retried distribution job {job_id} for user {user_id}")

async def perform_ai_optimization(content_id: str, platforms: List[str], user_id: str):
    """Perform AI content optimization"""
    await asyncio.sleep(45)
    print(f"AI optimization completed for content {content_id} on {len(platforms)} platforms")

async def setup_scheduled_distribution(content_id: str, platforms: List[str], schedule_times: Dict[str, datetime], user_id: str):
    """Setup scheduled distribution"""
    await asyncio.sleep(10)
    print(f"Scheduled distribution setup for content {content_id}")

__all__ = ["router"]