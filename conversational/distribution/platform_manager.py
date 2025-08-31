"""Platform Distribution Manager

Enterprise-grade multi-platform content distribution system with AI-powered optimization.
Handles platform-specific requirements, authentication, and content deployment at scale.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and protected. Unauthorized use, reproduction, 
or distribution is strictly prohibited and will result in legal action.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import hmac
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field, validator
import aiohttp
import aioredis
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import backoff
from tenacity import retry, stop_after_attempt, wait_exponential
import jwt

from ....core.database import get_db
from ....core.config import settings
from ....core.exceptions import DistributionError, PlatformError, AuthenticationError
from ....core.logging import get_logger
from ....utils.encryption import encrypt_data, decrypt_data, generate_secure_token
from ....utils.rate_limiter import RateLimiter, TokenBucket
from ....utils.monitoring import MetricsCollector, track_performance
from ....models.content import ContentModel, DistributionStatus, ContentType
from ....models.user import UserModel, PlatformCredentialsModel
from ....models.analytics import DistributionMetricsModel, PlatformPerformanceModel
from ....security.auth import verify_user_permissions, get_user_security_context
from ....ml.content_analysis import ContentAnalyzer, ViralityPredictor
from ....business.monetization import RevenueCalculator, MonetizationOptimizer


logger = get_logger(__name__)
metrics = MetricsCollector("distribution.platform_manager")


class PlatformType(str, Enum):
    """Supported distribution platforms with advanced integrations"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    REDDIT = "reddit"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    CLUBHOUSE = "clubhouse"


class DistributionPriority(str, Enum):
    """Content distribution priority levels with SLA definitions"""    CRITICAL = "critical"      # <5 seconds
    URGENT = "urgent"         # <30 seconds
    HIGH = "high"             # <2 minutes
    MEDIUM = "medium"         # <10 minutes
    LOW = "low"              # <1 hour
    SCHEDULED = "scheduled"   # At specified time
    BULK = "bulk"            # Background processing


class ContentOptimizationLevel(str, Enum):
    """Content optimization levels for platform-specific adaptation"""    MINIMAL = "minimal"       # Basic format conversion only
    STANDARD = "standard"     # Format + quality optimization
    ADVANCED = "advanced"     # Full AI optimization
    MAXIMUM = "maximum"       # AI + A/B testing + performance prediction


@dataclass
class PlatformCredentials:
    """Secure platform authentication credentials with advanced security"""    platform: PlatformType
    access_token: str
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"
    scope: List[str] = field(default_factory=list)
    rate_limit_remaining: int = 1000
    rate_limit_reset: Optional[datetime] = None
    webhook_secret: Optional[str] = None
    encryption_key: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if credentials are expired with buffer time"""        if not self.expires_at:
            return False
        # Add 5 minute buffer before expiration
        buffer_time = timedelta(minutes=5)
        return datetime.utcnow() >= (self.expires_at - buffer_time)
    
    def is_rate_limited(self) -> bool:
        """Check if platform is currently rate limited"""        if self.rate_limit_reset and datetime.utcnow() < self.rate_limit_reset:
            return self.rate_limit_remaining <= 0
        return False
    
    def get_authorization_header(self) -> Dict[str, str]:
        """Generate secure authorization header"""        return {
            "Authorization": f"{self.token_type} {self.access_token}",
            "User-Agent": f"IA-Influencer-Agent/1.0 (+{settings.BASE_URL})"
        }


class PlatformCapabilities(BaseModel):
    """Platform-specific capabilities and limitations"""    max_file_size: int  # bytes
    supported_formats: List[str]
    max_duration: Optional[int] = None  # seconds
    supports_scheduling: bool = True
    supports_live_streaming: bool = False
    supports_analytics: bool = True
    supports_monetization: bool = False
    api_rate_limit: int = 100  # requests per minute
    requires_approval: bool = False
    content_restrictions: List[str] = Field(default_factory=list)
    optimal_posting_times: List[int] = Field(default_factory=list)  # hours of day
    audience_demographics: Dict[str, Any] = Field(default_factory=dict)


class DistributionRequest(BaseModel):
    """Advanced distribution request with comprehensive targeting"""    user_id: int
    content_id: int
    platforms: List[PlatformType]
    priority: DistributionPriority = DistributionPriority.MEDIUM
    optimization_level: ContentOptimizationLevel = ContentOptimizationLevel.STANDARD
    schedule_time: Optional[datetime] = None
    custom_message: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    geo_targeting: Optional[Dict[str, Any]] = None
    audience_targeting: Optional[Dict[str, Any]] = None
    budget_allocation: Optional[Dict[PlatformType, float]] = None
    a_b_testing: bool = False
    track_conversions: bool = True
    enable_analytics: bool = True
    auto_crosspost: bool = False
    content_variations: Dict[PlatformType, Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('schedule_time')
    def validate_schedule_time(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Schedule time must be in the future")
        return v
    
    @validator('platforms')
    def validate_platforms(cls, v):
        if not v:
            raise ValueError("At least one platform must be specified")
        return v


class DistributionResult(BaseModel):
    """Comprehensive distribution operation result with metrics"""    platform: PlatformType
    success: bool
    post_id: Optional[str] = None
    url: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    retry_count: int = 0
    optimization_applied: bool = False
    predicted_performance: Optional[Dict[str, float]] = None
    content_warnings: List[str] = Field(default_factory=list)
    platform_feedback: Optional[Dict[str, Any]] = None


class PlatformDistributionManager:
class PlatformDistributionManager:
    """    Enterprise-grade platform distribution manager with AI optimization and advanced security.
    
    Features:
    - Multi-platform content distribution (15+ platforms)
    - AI-powered content optimization and adaptation
    - Advanced rate limiting and retry mechanisms
    - Real-time analytics and performance tracking
    - Secure credential management with encryption
    - Automated monetization and revenue optimization
    """    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = None
        self.platform_configs = self._load_platform_configs()
        self.platform_capabilities = self._load_platform_capabilities()
        self.active_sessions: Dict[str, aiohttp.ClientSession] = {}
        self.credentials_cache: Dict[int, Dict[PlatformType, PlatformCredentials]] = {}
        self.rate_limiters: Dict[PlatformType, RateLimiter] = {}
        self.content_analyzer = ContentAnalyzer()
        self.virality_predictor = ViralityPredictor()
        self.revenue_calculator = RevenueCalculator()
        self.monetization_optimizer = MonetizationOptimizer()
        
        # Initialize rate limiters for each platform
        self._initialize_rate_limiters()
        
    async def __aenter__(self):
        """Async context manager entry"""        self.redis_client = await aioredis.from_url(settings.REDIS_URL)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""        await self._cleanup_sessions()
        if self.redis_client:
            await self.redis_client.close()
    
    def _load_platform_configs(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Load comprehensive platform-specific configuration"""        return {
            PlatformType.YOUTUBE: {
                "api_base": "https://www.googleapis.com/youtube/v3",
                "upload_endpoint": "/videos",
                "analytics_endpoint": "/analytics",
                "max_file_size": 128 * 1024 * 1024 * 1024,  # 128GB
                "supported_formats": ["mp4", "mov", "avi", "wmv", "flv", "webm", "mkv"],
                "max_title_length": 100,
                "max_description_length": 5000,
                "max_tags": 500,
                "optimal_aspect_ratios": ["16:9", "9:16", "1:1"],
                "rate_limit": {"requests": 10000, "period": "day", "quota_cost": True},
                "monetization": {"requires_approval": True, "min_subscribers": 1000}
            },
            PlatformType.INSTAGRAM: {
                "api_base": "https://graph.instagram.com",
                "upload_endpoint": "/media",
                "stories_endpoint": "/media",
                "reels_endpoint": "/media",
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "supported_formats": ["jpg", "jpeg", "png", "mp4", "mov", "gif"],
                "max_caption_length": 2200,
                "max_hashtags": 30,
                "optimal_aspect_ratios": ["1:1", "4:5", "9:16"],
                "rate_limit": {"requests": 4800, "period": "hour"},
                "stories_duration": 24,  # hours
                "reels_max_duration": 90  # seconds
            },
            PlatformType.TIKTOK: {
                "api_base": "https://open-api.tiktok.com",
                "upload_endpoint": "/share/video/upload",
                "max_file_size": 500 * 1024 * 1024,  # 500MB
                "supported_formats": ["mp4", "mov", "webm"],
                "max_caption_length": 150,
                "max_hashtags": 20,
                "optimal_aspect_ratio": "9:16",
                "rate_limit": {"requests": 1000, "period": "day"},
                "min_duration": 3,  # seconds
                "max_duration": 180,  # seconds
                "viral_factors": ["trending_sounds", "hashtag_challenges", "effects"]
            },
            PlatformType.TWITTER: {
                "api_base": "https://api.twitter.com/2",
                "upload_endpoint": "/tweets",
                "media_endpoint": "/media/upload",
                "max_file_size": 512 * 1024 * 1024,  # 512MB
                "supported_formats": ["jpg", "jpeg", "png", "gif", "mp4", "mov"],
                "max_text_length": 280,
                "max_hashtags": 10,
                "thread_support": True,
                "rate_limit": {"requests": 300, "period": "15min"},
                "premium_features": ["longer_videos", "edit_tweets", "spaces"]
            },
            PlatformType.SPOTIFY: {
                "api_base": "https://api.spotify.com/v1",
                "upload_endpoint": "/podcasts/episodes",
                "max_file_size": 200 * 1024 * 1024,  # 200MB
                "supported_formats": ["mp3", "wav", "flac", "m4a", "ogg"],
                "max_title_length": 200,
                "max_description_length": 1000,
                "rate_limit": {"requests": 1000, "period": "hour"},
                "monetization": {"spotify_ad_studio": True, "premium_streaming": True}
            },
            PlatformType.LINKEDIN: {
                "api_base": "https://api.linkedin.com/v2",
                "upload_endpoint": "/ugcPosts",
                "company_endpoint": "/organizationAcls",
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "supported_formats": ["jpg", "jpeg", "png", "gif", "mp4", "pdf"],
                "max_text_length": 3000,
                "max_hashtags": 15,
                "rate_limit": {"requests": 500, "period": "day"},
                "professional_features": ["company_pages", "showcase_pages", "events"]
            },
            PlatformType.FACEBOOK: {
                "api_base": "https://graph.facebook.com/v18.0",
                "upload_endpoint": "/photos",
                "video_endpoint": "/videos",
                "max_file_size": 4 * 1024 * 1024 * 1024,  # 4GB
                "supported_formats": ["jpg", "jpeg", "png", "gif", "mp4", "mov", "avi"],
                "max_text_length": 63206,
                "max_hashtags": 30,
                "rate_limit": {"requests": 4800, "period": "hour"},
                "advertising_api": True
            },
            PlatformType.PINTEREST: {
                "api_base": "https://api.pinterest.com/v5",
                "upload_endpoint": "/pins",
                "max_file_size": 32 * 1024 * 1024,  # 32MB
                "supported_formats": ["jpg", "jpeg", "png", "gif", "mp4", "mov"],
                "max_description_length": 500,
                "max_hashtags": 20,
                "optimal_aspect_ratio": "2:3",
                "rate_limit": {"requests": 1000, "period": "hour"},
                "business_features": ["shopping_ads", "catalogs", "audience_insights"]
            },
            PlatformType.SNAPCHAT: {
                "api_base": "https://adsapi.snapchat.com/v1",
                "upload_endpoint": "/media",
                "max_file_size": 32 * 1024 * 1024,  # 32MB
                "supported_formats": ["jpg", "jpeg", "png", "mp4", "mov"],
                "optimal_aspect_ratio": "9:16",
                "rate_limit": {"requests": 1000, "period": "hour"},
                "story_duration": 24,  # hours
                "spotlight_eligible": True
            },
            PlatformType.TWITCH: {
                "api_base": "https://api.twitch.tv/helix",
                "upload_endpoint": "/videos",
                "clips_endpoint": "/clips",
                "max_file_size": 10 * 1024 * 1024 * 1024,  # 10GB
                "supported_formats": ["mp4", "mov", "avi", "flv"],
                "rate_limit": {"requests": 800, "period": "minute"},
                "streaming_features": ["live_streaming", "clips", "highlights"],
                "monetization": {"subscriptions": True, "bits": True, "ads": True}
            },
            PlatformType.REDDIT: {
                "api_base": "https://oauth.reddit.com",
                "upload_endpoint": "/api/submit",
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "supported_formats": ["jpg", "jpeg", "png", "gif", "mp4"],
                "max_title_length": 300,
                "max_text_length": 40000,
                "rate_limit": {"requests": 60, "period": "minute"},
                "community_rules": True
            },
            PlatformType.DISCORD: {
                "api_base": "https://discord.com/api/v10",
                "upload_endpoint": "/channels/{channel_id}/messages",
                "max_file_size": 25 * 1024 * 1024,  # 25MB (50MB for Nitro)
                "supported_formats": ["jpg", "jpeg", "png", "gif", "mp4", "mov", "webm"],
                "max_message_length": 2000,
                "rate_limit": {"requests": 50, "period": "second"},
                "bot_features": ["slash_commands", "embeds", "reactions"]
            },
            PlatformType.TELEGRAM: {
                "api_base": "https://api.telegram.org/bot",
                "upload_endpoint": "/sendDocument",
                "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB
                "supported_formats": ["jpg", "jpeg", "png", "gif", "mp4", "mov", "pdf"],
                "max_caption_length": 1024,
                "rate_limit": {"requests": 30, "period": "second"},
                "channel_features": ["channels", "groups", "supergroups"]
            }
        }
    
    def _load_platform_capabilities(self) -> Dict[PlatformType, PlatformCapabilities]:
        """Load platform capabilities and limitations"""        capabilities = {}
        for platform, config in self.platform_configs.items():
            capabilities[platform] = PlatformCapabilities(
                max_file_size=config["max_file_size"],
                supported_formats=config["supported_formats"],
                max_duration=config.get("max_duration"),
                supports_scheduling=config.get("supports_scheduling", True),
                supports_live_streaming=config.get("supports_live_streaming", False),
                supports_analytics=config.get("supports_analytics", True),
                supports_monetization=config.get("supports_monetization", False),
                api_rate_limit=config["rate_limit"]["requests"],
                requires_approval=config.get("requires_approval", False),
                content_restrictions=config.get("content_restrictions", []),
                optimal_posting_times=config.get("optimal_posting_times", [9, 12, 15, 18, 21])
            )
        return capabilities
    
    def _initialize_rate_limiters(self):
        """Initialize rate limiters for each platform"""        for platform, config in self.platform_configs.items():
            rate_config = config["rate_limit"]
            if rate_config["period"] == "minute":
                window_size = 60
            elif rate_config["period"] == "hour":
                window_size = 3600
            elif rate_config["period"] == "day":
                window_size = 86400
            elif rate_config["period"] == "15min":
                window_size = 900
            else:
                window_size = 3600  # default to hour
                
            self.rate_limiters[platform] = RateLimiter(
                max_requests=rate_config["requests"],
                window_size=window_size
            )
    
    @track_performance("distribution.distribute_content")
    async def distribute_content(
        self,
        request: DistributionRequest
    ) -> List[DistributionResult]:
        """        Distribute content to multiple platforms with AI optimization and advanced features.
        
        This method handles:
        - User authentication and authorization
        - Content analysis and optimization
        - Platform-specific adaptation
        - Rate limiting and retry logic
        - Real-time analytics tracking
        - Revenue optimization
        
        Args:
            request: Comprehensive distribution request
            
        Returns:
            List of detailed distribution results for each platform
        """        start_time = datetime.utcnow()
        results: List[DistributionResult] = []
        
        try:
            with metrics.timer("distribution.total_time"):
                # Step 1: Validate user and permissions
                user = await self._validate_user_and_permissions(request.user_id)
                
                # Step 2: Get and analyze content
                content = await self._get_and_analyze_content(request.content_id, request.user_id)
                
                # Step 3: Load and validate platform credentials
                credentials = await self._load_platform_credentials(request.user_id, request.platforms)
                
                # Step 4: AI-powered content optimization
                if request.optimization_level != ContentOptimizationLevel.MINIMAL:
                    content = await self._optimize_content_with_ai(content, request)
                
                # Step 5: Generate platform-specific adaptations
                adaptations = await self._generate_platform_adaptations(content, request)
                
                # Step 6: Execute distribution with concurrent processing
                distribution_tasks = []
                for platform in request.platforms:
                    if platform in credentials:
                        task = self._distribute_to_platform(
                            platform=platform,
                            content=content,
                            adaptations=adaptations.get(platform, {}),
                            credentials=credentials[platform],
                            request=request
                        )
                        distribution_tasks.append(task)
                
                # Execute all distributions concurrently with proper error handling
                platform_results = await asyncio.gather(*distribution_tasks, return_exceptions=True)
                
                # Process results and handle exceptions
                for i, result in enumerate(platform_results):
                    if isinstance(result, Exception):
                        platform = request.platforms[i]
                        error_result = DistributionResult(
                            platform=platform,
                            success=False,
                            error_message=str(result),
                            error_code="EXECUTION_ERROR",
                            processing_time=(datetime.utcnow() - start_time).total_seconds()
                        )
                        results.append(error_result)
                        logger.error(f"Distribution failed for {platform}: {result}")
                    else:
                        results.append(result)
                
                # Step 7: Update analytics and tracking
                await self._update_distribution_analytics(request, results)
                
                # Step 8: Calculate and update revenue projections
                if request.track_conversions:
                    await self._calculate_revenue_projections(request, results)
                
                # Step 9: Trigger follow-up actions (crossposting, scheduling, etc.)
                if request.auto_crosspost:
                    await self._handle_auto_crosspost(request, results)
                
                metrics.increment("distribution.requests.completed")
                logger.info(f"Distribution completed for content {request.content_id} across {len(request.platforms)} platforms")
                
                return results
                
        except Exception as e:
            metrics.increment("distribution.requests.failed")
            logger.error(f"Distribution failed for content {request.content_id}: {e}")
            
            # Return error results for all platforms
            for platform in request.platforms:
                error_result = DistributionResult(
                    platform=platform,
                    success=False,
                    error_message=str(e),
                    error_code="SYSTEM_ERROR",
                    processing_time=(datetime.utcnow() - start_time).total_seconds()
                )
                results.append(error_result)
            
            return results
                raise DistributionError("Content not found or access denied")
            
            # Validate platforms and credentials
            valid_platforms = await self._validate_platform_credentials(
                request.user_id, request.platforms
            )
            
            if not valid_platforms:
                raise DistributionError("No valid platform credentials found")
            
            # Optimize content for each platform
            optimized_content = await self._optimize_content_for_platforms(
                content, valid_platforms
            )
            
            # Execute distribution tasks
            distribution_tasks = []
            for platform in valid_platforms:
                task = self._distribute_to_platform(
                    platform, content, optimized_content[platform], request
                )
                distribution_tasks.append(task)
            
            # Execute distributions concurrently
            results = await asyncio.gather(
                *distribution_tasks, return_exceptions=True
            )
            
            # Process results and handle exceptions
            distribution_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Distribution failed for {valid_platforms[i]}: {result}")
                    distribution_results.append(DistributionResult(
                        platform=valid_platforms[i],
                        success=False,
                        error_message=str(result)
                    ))
                else:
                    distribution_results.append(result)
            
            # Update content distribution status
            await self._update_content_status(content, distribution_results)
            
            # Log distribution analytics
            await self._log_distribution_analytics(request, distribution_results)
            
            return distribution_results
            
        except Exception as e:
            logger.error(f"Content distribution failed: {e}")
            raise DistributionError(f"Distribution failed: {str(e)}")
    
    async def _validate_platform_credentials(
        self,
        user_id: int,
        platforms: List[PlatformType]
    ) -> List[PlatformType]:
        """Validate and refresh platform credentials"""        valid_platforms = []
        
        for platform in platforms:
            try:
                credentials = await self._get_platform_credentials(user_id, platform)
                
                if credentials and not credentials.is_expired():
                    valid_platforms.append(platform)
                elif credentials and credentials.is_expired():
                    # Attempt to refresh credentials
                    refreshed = await self._refresh_platform_credentials(
                        user_id, platform, credentials
                    )
                    if refreshed:
                        valid_platforms.append(platform)
                        
            except Exception as e:
                logger.warning(f"Failed to validate credentials for {platform}: {e}")
                continue
        
        return valid_platforms
    
    async def _get_platform_credentials(
        self,
        user_id: int,
        platform: PlatformType
    ) -> Optional[PlatformCredentials]:
        """Retrieve and decrypt platform credentials"""        # Check cache first
        if user_id in self.credentials_cache:
            if platform in self.credentials_cache[user_id]:
                return self.credentials_cache[user_id][platform]
        
        # Query database for encrypted credentials
        from ....models.platform_credentials import PlatformCredentialsModel
        
        cred_record = self.db.query(PlatformCredentialsModel).filter(
            PlatformCredentialsModel.user_id == user_id,
            PlatformCredentialsModel.platform == platform.value,
            PlatformCredentialsModel.is_active == True
        ).first()
        
        if not cred_record:
            return None
        
        # Decrypt credentials
        try:
            decrypted_data = decrypt_data(cred_record.encrypted_credentials)
            credentials = PlatformCredentials(
                platform=platform,
                access_token=decrypted_data.get("access_token"),
                refresh_token=decrypted_data.get("refresh_token"),
                api_key=decrypted_data.get("api_key"),
                secret_key=decrypted_data.get("secret_key"),
                expires_at=cred_record.expires_at
            )
            
            # Cache credentials
            if user_id not in self.credentials_cache:
                self.credentials_cache[user_id] = {}
            self.credentials_cache[user_id][platform] = credentials
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to decrypt credentials for {platform}: {e}")
            return None
    
    async def _refresh_platform_credentials(
        self,
        user_id: int,
        platform: PlatformType,
        credentials: PlatformCredentials
    ) -> bool:
        """Refresh expired platform credentials"""        try:
            if not credentials.refresh_token:
                return False
            
            config = self.platform_configs[platform]
            refresh_url = f"{config['api_base']}/oauth/token"
            
            refresh_data = {
                "grant_type": "refresh_token",
                "refresh_token": credentials.refresh_token,
                "client_id": settings.get(f"{platform.value}_client_id"),
                "client_secret": settings.get(f"{platform.value}_client_secret")
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(refresh_url, data=refresh_data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        
                        # Update credentials
                        credentials.access_token = token_data["access_token"]
                        if "refresh_token" in token_data:
                            credentials.refresh_token = token_data["refresh_token"]
                        
                        expires_in = token_data.get("expires_in", 3600)
                        credentials.expires_at = datetime.utcnow() + timedelta(
                            seconds=expires_in
                        )
                        
                        # Update database
                        await self._save_platform_credentials(user_id, credentials)
                        
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to refresh credentials for {platform}: {e}")
            return False
    
    async def _optimize_content_for_platforms(
        self,
        content: ContentModel,
        platforms: List[PlatformType]
    ) -> Dict[PlatformType, Dict[str, Any]]:
        """Optimize content for each platform's requirements"""        optimized_content = {}
        
        for platform in platforms:
            config = self.platform_configs[platform]
            
            optimized_content[platform] = {
                "title": self._optimize_title(content.title, config),
                "description": self._optimize_description(
                    content.description, config
                ),
                "hashtags": self._optimize_hashtags(content.hashtags, config),
                "file_url": content.file_url,
                "thumbnail_url": content.thumbnail_url,
                "metadata": content.metadata or {}
            }
        
        return optimized_content
    
    def _optimize_title(self, title: str, config: Dict[str, Any]) -> str:
        """Optimize title for platform constraints"""        max_length = config.get("max_title_length", 100)
        if len(title) <= max_length:
            return title
        
        # Truncate and add ellipsis
        return title[:max_length-3] + "..."
    
    def _optimize_description(self, description: str, config: Dict[str, Any]) -> str:
        """Optimize description for platform constraints"""        max_length = config.get("max_description_length", 1000)
        if len(description) <= max_length:
            return description
        
        # Truncate intelligently at sentence boundary
        truncated = description[:max_length]
        last_sentence = truncated.rfind(". ")
        if last_sentence > max_length * 0.7:  # If we can keep 70% and end at sentence
            return truncated[:last_sentence + 1]
        
        return truncated + "..."
    
    def _optimize_hashtags(
        self, hashtags: List[str], config: Dict[str, Any]
    ) -> List[str]:
        """Optimize hashtags for platform constraints"""        max_hashtags = config.get("max_hashtags", 30)
        return hashtags[:max_hashtags]
    
    async def _distribute_to_platform(
        self,
        platform: PlatformType,
        content: ContentModel,
        optimized_content: Dict[str, Any],
        request: DistributionRequest
    ) -> DistributionResult:
        """Distribute content to a specific platform"""        try:
            credentials = await self._get_platform_credentials(
                request.user_id, platform
            )
            
            if not credentials:
                raise PlatformError(f"No valid credentials for {platform}")
            
            # Get platform-specific manager
            manager = await self._get_platform_manager(platform)
            
            # Execute platform-specific distribution
            result = await manager.distribute_content(
                credentials, optimized_content, request
            )
            
            return DistributionResult(
                platform=platform,
                success=True,
                post_id=result.get("post_id"),
                url=result.get("url"),
                metrics=result.get("metrics", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to distribute to {platform}: {e}")
            return DistributionResult(
                platform=platform,
                success=False,
                error_message=str(e)
            )
    
    async def _get_platform_manager(self, platform: PlatformType):
        """Get platform-specific distribution manager"""        from .channel_managers import (
            YouTubeChannelManager,
            InstagramChannelManager,
            TikTokChannelManager,
            TwitterChannelManager,
            SpotifyChannelManager,
            LinkedInChannelManager
        )
        
        managers = {
            PlatformType.YOUTUBE: YouTubeChannelManager,
            PlatformType.INSTAGRAM: InstagramChannelManager,
            PlatformType.TIKTOK: TikTokChannelManager,
            PlatformType.TWITTER: TwitterChannelManager,
            PlatformType.SPOTIFY: SpotifyChannelManager,
            PlatformType.LINKEDIN: LinkedInChannelManager
        }
        
        manager_class = managers.get(platform)
        if not manager_class:
            raise PlatformError(f"No manager available for {platform}")
        
        return manager_class(self.db)
    
    async def _update_content_status(
        self,
        content: ContentModel,
        results: List[DistributionResult]
    ) -> None:
        """Update content distribution status"""        successful_platforms = [
            result.platform for result in results if result.success
        ]
        failed_platforms = [
            result.platform for result in results if not result.success
        ]
        
        if successful_platforms and not failed_platforms:
            content.distribution_status = DistributionStatus.COMPLETED
        elif successful_platforms and failed_platforms:
            content.distribution_status = DistributionStatus.PARTIAL
        else:
            content.distribution_status = DistributionStatus.FAILED
        
        content.distributed_platforms = [p.value for p in successful_platforms]
        content.last_distribution_attempt = datetime.utcnow()
        
        self.db.commit()
    
    async def _log_distribution_analytics(
        self,
        request: DistributionRequest,
        results: List[DistributionResult]
    ) -> None:
        """Log distribution analytics for reporting"""        from ....models.distribution_analytics import DistributionAnalyticsModel
        
        for result in results:
            analytics = DistributionAnalyticsModel(
                user_id=request.user_id,
                content_id=request.content_id,
                platform=result.platform.value,
                success=result.success,
                post_id=result.post_id,
                url=result.url,
                error_message=result.error_message,
                metrics=result.metrics,
                created_at=result.timestamp
            )
            
            self.db.add(analytics)
        
        self.db.commit()
    
    async def _save_platform_credentials(
        self,
        user_id: int,
        credentials: PlatformCredentials
    ) -> None:
        """Save encrypted platform credentials"""        from ....models.platform_credentials import PlatformCredentialsModel
        
        # Encrypt credentials
        cred_data = {
            "access_token": credentials.access_token,
            "refresh_token": credentials.refresh_token,
            "api_key": credentials.api_key,
            "secret_key": credentials.secret_key
        }
        
        encrypted_data = encrypt_data(cred_data)
        
        # Update existing record or create new one
        existing = self.db.query(PlatformCredentialsModel).filter(
            PlatformCredentialsModel.user_id == user_id,
            PlatformCredentialsModel.platform == credentials.platform.value
        ).first()
        
        if existing:
            existing.encrypted_credentials = encrypted_data
            existing.expires_at = credentials.expires_at
            existing.updated_at = datetime.utcnow()
        else:
            new_cred = PlatformCredentialsModel(
                user_id=user_id,
                platform=credentials.platform.value,
                encrypted_credentials=encrypted_data,
                expires_at=credentials.expires_at
            )
            self.db.add(new_cred)
        
        self.db.commit()
        
        # Update cache
        if user_id not in self.credentials_cache:
            self.credentials_cache[user_id] = {}
        self.credentials_cache[user_id][credentials.platform] = credentials
    
    async def get_distribution_status(
        self, user_id: int, content_id: int
    ) -> Dict[str, Any]:
        """Get content distribution status across platforms"""        content = self.db.query(ContentModel).filter(
            ContentModel.id == content_id,
            ContentModel.user_id == user_id
        ).first()
        
        if not content:
            raise DistributionError("Content not found")
        
        # Get distribution analytics
        from ....models.distribution_analytics import DistributionAnalyticsModel
        
        analytics = self.db.query(DistributionAnalyticsModel).filter(
            DistributionAnalyticsModel.content_id == content_id
        ).all()
        
        platform_status = {}
        for record in analytics:
            platform_status[record.platform] = {
                "success": record.success,
                "post_id": record.post_id,
                "url": record.url,
                "error_message": record.error_message,
                "metrics": record.metrics,
                "timestamp": record.created_at
            }
        
        return {
            "content_id": content_id,
            "distribution_status": content.distribution_status.value,
            "distributed_platforms": content.distributed_platforms,
            "last_attempt": content.last_distribution_attempt,
            "platform_details": platform_status
        }
    
    async def schedule_distribution(
        self,
        request: DistributionRequest
    ) -> str:
        """Schedule content distribution for future execution"""        from ....tasks.distribution import schedule_content_distribution
        
        # Validate schedule time
        if not request.schedule_time:
            raise DistributionError("Schedule time is required")
        
        if request.schedule_time <= datetime.utcnow():
            raise DistributionError("Schedule time must be in the future")
        
        # Create scheduled task
        task_id = await schedule_content_distribution.apply_async(
            args=[request.dict()],
            eta=request.schedule_time
        )
        
        return str(task_id)
    
    async def cancel_scheduled_distribution(
        self, user_id: int, task_id: str
    ) -> bool:
        """Cancel a scheduled distribution task"""        try:
            from celery import current_app
            
            # Verify task belongs to user
            task = current_app.control.inspect().scheduled()
            if task_id not in task:
                return False
            
            # Cancel the task
            current_app.control.revoke(task_id, terminate=True)
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel scheduled distribution {task_id}: {e}")
            return False
    
    async def cleanup_expired_credentials(self) -> None:
        """Cleanup expired credentials from cache and database"""        from ....models.platform_credentials import PlatformCredentialsModel
        
        # Remove expired credentials from database
        expired_credentials = self.db.query(PlatformCredentialsModel).filter(
            PlatformCredentialsModel.expires_at < datetime.utcnow(),
            PlatformCredentialsModel.is_active == True
        ).all()
        
        for cred in expired_credentials:
            cred.is_active = False
        
        self.db.commit()
        
        # Clear cache for expired credentials
        current_time = datetime.utcnow()
        for user_id in list(self.credentials_cache.keys()):
            for platform in list(self.credentials_cache[user_id].keys()):
                if self.credentials_cache[user_id][platform].is_expired():
                    del self.credentials_cache[user_id][platform]
            
            # Remove empty user entries
            if not self.credentials_cache[user_id]:
                del self.credentials_cache[user_id]
    
    # Platform-specific distribution methods
    
    async def _distribute_to_youtube(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Distribute content to YouTube with advanced features"""        config = self.platform_configs[PlatformType.YOUTUBE]
        
        # Prepare video metadata
        video_metadata = {
            "snippet": {
                "title": adaptations["title"],
                "description": adaptations["description"],
                "tags": adaptations["hashtags"],
                "categoryId": adaptations.get("category", "22"),
                "defaultLanguage": adaptations.get("language", "en"),
                "defaultAudioLanguage": adaptations.get("language", "en")
            },
            "status": {
                "privacyStatus": adaptations.get("privacy", "public"),
                "embeddable": True,
                "license": "youtube",
                "publicStatsViewable": True,
                "madeForKids": adaptations.get("made_for_kids", False)
            },
            "recordingDetails": {
                "recordingDate": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Add monetization if enabled
        if adaptations.get("monetization", {}).get("enabled"):
            video_metadata["monetizationDetails"] = {
                "access": {
                    "allowed": True,
                    "exception": []
                }
            }
        
        # Upload video file
        upload_url = f"{config['api_base']}/videos?uploadType=resumable&part=snippet,status,recordingDetails"
        
        # First, initiate the upload
        headers = {"Content-Type": "application/json"}
        async with session.post(upload_url, json=video_metadata, headers=headers) as response:
            if response.status != 200:
                raise PlatformError(f"YouTube upload initiation failed: {response.status}")
            
            location = response.headers.get("Location")
            if not location:
                raise PlatformError("YouTube upload location not received")
        
        # Upload the actual video file (simplified - in reality, you'd stream the file)
        upload_response = await self._upload_file_to_youtube(session, location, content.file_url)
        
        if upload_response["success"]:
            video_id = upload_response["video_id"]
            
            # Add to playlist if specified
            if request.content_variations.get(PlatformType.YOUTUBE, {}).get("playlist_id"):
                await self._add_to_youtube_playlist(
                    session, 
                    video_id, 
                    request.content_variations[PlatformType.YOUTUBE]["playlist_id"]
                )
            
            return {
                "post_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "metrics": {"upload_size": content.file_size or 0},
                "predicted_performance": await self._predict_youtube_performance(content, adaptations),
                "platform_feedback": upload_response.get("processing_details")
            }
        else:
            raise PlatformError(f"YouTube video upload failed: {upload_response['error']}")
    
    async def _distribute_to_instagram(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Distribute content to Instagram with advanced features"""        config = self.platform_configs[PlatformType.INSTAGRAM]
        
        # Determine content type and endpoint
        content_type = adaptations.get("content_type", "photo")
        
        if content_type == "reel":
            return await self._create_instagram_reel(session, content, adaptations, request)
        elif content_type == "story":
            return await self._create_instagram_story(session, content, adaptations, request)
        else:
            return await self._create_instagram_post(session, content, adaptations, request)
    
    async def _create_instagram_post(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Create Instagram feed post"""        config = self.platform_configs[PlatformType.INSTAGRAM]
        
        # Step 1: Create media object
        media_data = {
            "image_url": content.file_url if content.content_type != ContentType.VIDEO else content.thumbnail_url,
            "video_url": content.file_url if content.content_type == ContentType.VIDEO else None,
            "caption": f"{adaptations['description']}\n\n{' '.join(['#' + tag for tag in adaptations['hashtags']])}",
            "location_id": adaptations.get("location"),
            "user_tags": adaptations.get("tagged_users", [])
        }
        
        # Remove None values
        media_data = {k: v for k, v in media_data.items() if v is not None}
        
        # Create media container
        create_url = f"{config['api_base']}/me/media"
        async with session.post(create_url, data=media_data) as response:
            if response.status != 200:
                response_text = await response.text()
                raise PlatformError(f"Instagram media creation failed: {response.status} - {response_text}")
            
            media_response = await response.json()
            creation_id = media_response["id"]
        
        # Step 2: Publish media
        publish_url = f"{config['api_base']}/me/media_publish"
        publish_data = {"creation_id": creation_id}
        
        async with session.post(publish_url, data=publish_data) as response:
            if response.status != 200:
                response_text = await response.text()
                raise PlatformError(f"Instagram media publish failed: {response.status} - {response_text}")
            
            publish_response = await response.json()
            media_id = publish_response["id"]
        
        return {
            "post_id": media_id,
            "url": f"https://www.instagram.com/p/{media_id}/",
            "metrics": {"caption_length": len(media_data.get("caption", ""))},
            "predicted_performance": await self._predict_instagram_performance(content, adaptations)
        }
    
    async def _distribute_to_tiktok(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Distribute content to TikTok with viral optimization"""        config = self.platform_configs[PlatformType.TIKTOK]
        
        # Prepare video data
        video_data = {
            "video": {
                "video_url": content.file_url,
                "thumbnail_url": content.thumbnail_url or content.file_url,
                "video_cover_timestamp_ms": 1000  # Cover frame at 1 second
            },
            "post_info": {
                "title": adaptations["description"],
                "privacy_level": adaptations.get("privacy", "SELF_ONLY"),  # PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIEND, FOLLOWER_OF_CREATOR, SELF_ONLY
                "disable_duet": not adaptations.get("allow_duets", True),
                "disable_comment": not adaptations.get("allow_comments", True),
                "disable_stitch": not adaptations.get("allow_reactions", True),
                "video_cover_timestamp_ms": 1000
            }
        }
        
        # Add trending hashtags and effects if available
        if adaptations.get("hashtags"):
            # TikTok uses hashtags in the title
            hashtag_string = " ".join([f"#{tag}" for tag in adaptations["hashtags"]])
            video_data["post_info"]["title"] = f"{adaptations['description']} {hashtag_string}"
        
        # Upload video
        upload_url = f"{config['api_base']}/share/video/upload/"
        
        async with session.post(upload_url, json=video_data) as response:
            if response.status != 200:
                response_text = await response.text()
                raise PlatformError(f"TikTok upload failed: {response.status} - {response_text}")
            
            upload_response = await response.json()
            
            if upload_response.get("error"):
                raise PlatformError(f"TikTok upload error: {upload_response['error']['message']}")
            
            share_id = upload_response["data"]["share_id"]
            
            return {
                "post_id": share_id,
                "url": f"https://www.tiktok.com/@user/video/{share_id}",
                "metrics": {"video_duration": content.duration or 0},
                "predicted_performance": await self._predict_tiktok_performance(content, adaptations),
                "platform_feedback": {
                    "processing_status": upload_response["data"].get("status"),
                    "viral_factors": adaptations.get("viral_factors", [])
                }
            }
    
    async def _distribute_to_twitter(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Distribute content to Twitter with advanced features"""        config = self.platform_configs[PlatformType.TWITTER]
        
        # Prepare tweet data
        tweet_text = adaptations["description"]
        if adaptations.get("hashtags"):
            hashtag_string = " ".join([f"#{tag}" for tag in adaptations["hashtags"][:3]])  # Limit hashtags for Twitter
            tweet_text = f"{tweet_text} {hashtag_string}"
        
        tweet_data = {
            "text": tweet_text[:280],  # Ensure character limit
            "reply": {
                "exclude_reply_user_ids": []
            }
        }
        
        # Add media if present
        if content.file_url:
            # First upload media
            media_id = await self._upload_twitter_media(session, content)
            if media_id:
                tweet_data["media"] = {"media_ids": [media_id]}
        
        # Add geo data if available
        if adaptations.get("geo"):
            tweet_data["geo"] = adaptations["geo"]
        
        # Add poll if specified
        if request.content_variations.get(PlatformType.TWITTER, {}).get("poll"):
            poll_data = request.content_variations[PlatformType.TWITTER]["poll"]
            tweet_data["poll"] = {
                "options": poll_data["options"],
                "duration_minutes": poll_data.get("duration", 1440)  # 24 hours default
            }
        
        # Create tweet
        create_url = f"{config['api_base']}/tweets"
        
        async with session.post(create_url, json=tweet_data) as response:
            if response.status != 201:
                response_text = await response.text()
                raise PlatformError(f"Twitter tweet creation failed: {response.status} - {response_text}")
            
            tweet_response = await response.json()
            tweet_id = tweet_response["data"]["id"]
            
            return {
                "post_id": tweet_id,
                "url": f"https://twitter.com/user/status/{tweet_id}",
                "metrics": {"character_count": len(tweet_text)},
                "predicted_performance": await self._predict_twitter_performance(content, adaptations)
            }
    
    async def _distribute_to_spotify(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Distribute audio content to Spotify"""        config = self.platform_configs[PlatformType.SPOTIFY]
        
        # Spotify is primarily for podcasts via Anchor or direct artist uploads
        # This is a simplified implementation for podcast episodes
        
        episode_data = {
            "name": adaptations["title"],
            "description": adaptations["description"],
            "audio_url": content.file_url,
            "language": adaptations.get("language", "en"),
            "explicit": content.metadata.get("explicit", False),
            "type": "full"  # full, trailer, bonus
        }
        
        # Note: Actual Spotify podcast upload requires pre-existing show
        # This is a simplified representation
        upload_url = f"{config['api_base']}/shows/episodes"
        
        async with session.post(upload_url, json=episode_data) as response:
            if response.status != 201:
                response_text = await response.text()
                raise PlatformError(f"Spotify episode upload failed: {response.status} - {response_text}")
            
            episode_response = await response.json()
            episode_id = episode_response["id"]
            
            return {
                "post_id": episode_id,
                "url": f"https://open.spotify.com/episode/{episode_id}",
                "metrics": {"duration": content.duration or 0},
                "predicted_performance": await self._predict_spotify_performance(content, adaptations)
            }
    
    async def _distribute_to_linkedin(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Distribute content to LinkedIn with professional optimization"""        config = self.platform_configs[PlatformType.LINKEDIN]
        
        # Prepare post data
        post_data = {
            "author": f"urn:li:person:{request.user_id}",  # Simplified - should be LinkedIn person URN
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": adaptations["description"]
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": adaptations.get("visibility", "PUBLIC")
            }
        }
        
        # Add media if present
        if content.file_url:
            if content.content_type == ContentType.VIDEO:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "VIDEO"
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "description": {
                        "text": adaptations.get("title", "")
                    },
                    "media": content.file_url,
                    "title": {
                        "text": adaptations["title"]
                    }
                }]
            else:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "description": {
                        "text": adaptations.get("title", "")
                    },
                    "media": content.file_url,
                    "title": {
                        "text": adaptations["title"]
                    }
                }]
        
        # Create LinkedIn post
        create_url = f"{config['api_base']}/ugcPosts"
        
        async with session.post(create_url, json=post_data) as response:
            if response.status != 201:
                response_text = await response.text()
                raise PlatformError(f"LinkedIn post creation failed: {response.status} - {response_text}")
            
            post_response = await response.json()
            post_id = post_response["id"]
            
            return {
                "post_id": post_id,
                "url": f"https://www.linkedin.com/feed/update/{post_id}/",
                "metrics": {"text_length": len(adaptations["description"])},
                "predicted_performance": await self._predict_linkedin_performance(content, adaptations)
            }
    
    async def _distribute_to_generic_platform(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest,
        platform: PlatformType
    ) -> Dict[str, Any]:
        """Generic distribution method for other platforms"""        config = self.platform_configs[platform]
        
        # Generic post data structure
        post_data = {
            "title": adaptations.get("title", ""),
            "content": adaptations.get("description", ""),
            "media_url": content.file_url,
            "tags": adaptations.get("hashtags", []),
            "metadata": adaptations.get("metadata", {})
        }
        
        # Generic upload endpoint
        upload_url = f"{config['api_base']}{config['upload_endpoint']}"
        
        async with session.post(upload_url, json=post_data) as response:
            if response.status not in [200, 201]:
                response_text = await response.text()
                raise PlatformError(f"{platform} upload failed: {response.status} - {response_text}")
            
            response_data = await response.json()
            post_id = response_data.get("id") or response_data.get("post_id") or "unknown"
            
            return {
                "post_id": post_id,
                "url": response_data.get("url", f"https://{platform.value}.com/post/{post_id}"),
                "metrics": {"content_length": len(adaptations.get("description", ""))},
                "predicted_performance": {}
            }
    
    # Performance prediction methods
    
    async def _predict_youtube_performance(self, content: ContentModel, adaptations: Dict[str, Any]) -> Dict[str, float]:
        """Predict YouTube video performance using AI"""        if not hasattr(self, 'virality_predictor'):
            return {}
        
        features = {
            "title_length": len(adaptations["title"]),
            "description_length": len(adaptations["description"]),
            "tag_count": len(adaptations.get("hashtags", [])),
            "video_duration": content.duration or 0,
            "upload_time": datetime.utcnow().hour,
            "content_type": content.content_type.value if content.content_type else "unknown"
        }
        
        prediction = await self.virality_predictor.predict_platform_performance(
            platform=PlatformType.YOUTUBE,
            features=features,
            content=content
        )
        
        return prediction
    
    async def _predict_instagram_performance(self, content: ContentModel, adaptations: Dict[str, Any]) -> Dict[str, float]:
        """Predict Instagram post performance"""        if not hasattr(self, 'virality_predictor'):
            return {}
        
        features = {
            "caption_length": len(adaptations["description"]),
            "hashtag_count": len(adaptations.get("hashtags", [])),
            "content_type": adaptations.get("content_type", "photo"),
            "posting_time": datetime.utcnow().hour,
            "has_location": bool(adaptations.get("location"))
        }
        
        prediction = await self.virality_predictor.predict_platform_performance(
            platform=PlatformType.INSTAGRAM,
            features=features,
            content=content
        )
        
        return prediction
    
    async def _predict_tiktok_performance(self, content: ContentModel, adaptations: Dict[str, Any]) -> Dict[str, float]:
        """Predict TikTok video performance"""        if not hasattr(self, 'virality_predictor'):
            return {}
        
        features = {
            "video_duration": content.duration or 0,
            "hashtag_count": len(adaptations.get("hashtags", [])),
            "trending_sounds": len(adaptations.get("sounds", [])),
            "effects_used": len(adaptations.get("effects", [])),
            "posting_time": datetime.utcnow().hour
        }
        
        prediction = await self.virality_predictor.predict_platform_performance(
            platform=PlatformType.TIKTOK,
            features=features,
            content=content
        )
        
        return prediction
    
    async def _predict_twitter_performance(self, content: ContentModel, adaptations: Dict[str, Any]) -> Dict[str, float]:
        """Predict Twitter tweet performance"""        if not hasattr(self, 'virality_predictor'):
            return {}
        
        features = {
            "text_length": len(adaptations["description"]),
            "hashtag_count": len(adaptations.get("hashtags", [])),
            "has_media": bool(content.file_url),
            "posting_time": datetime.utcnow().hour,
            "mentions_count": len(adaptations.get("mentions", []))
        }
        
        prediction = await self.virality_predictor.predict_platform_performance(
            platform=PlatformType.TWITTER,
            features=features,
            content=content
        )
        
        return prediction
    
    async def _predict_spotify_performance(self, content: ContentModel, adaptations: Dict[str, Any]) -> Dict[str, float]:
        """Predict Spotify episode performance"""        if not hasattr(self, 'virality_predictor'):
            return {}
        
        features = {
            "title_length": len(adaptations["title"]),
            "description_length": len(adaptations["description"]),
            "duration": content.duration or 0,
            "language": adaptations.get("language", "en"),
            "explicit": content.metadata.get("explicit", False)
        }
        
        prediction = await self.virality_predictor.predict_platform_performance(
            platform=PlatformType.SPOTIFY,
            features=features,
            content=content
        )
        
        return prediction
    
    async def _predict_linkedin_performance(self, content: ContentModel, adaptations: Dict[str, Any]) -> Dict[str, float]:
        """Predict LinkedIn post performance"""        if not hasattr(self, 'virality_predictor'):
            return {}
        
        features = {
            "text_length": len(adaptations["description"]),
            "has_media": bool(content.file_url),
            "professional_tone": adaptations.get("professional_tone", True),
            "posting_time": datetime.utcnow().hour,
            "has_cta": adaptations.get("include_cta", False)
        }
        
        prediction = await self.virality_predictor.predict_platform_performance(
            platform=PlatformType.LINKEDIN,
            features=features,
            content=content
        )
        
        return prediction
    
    # Helper methods for specific platforms
    
    async def _upload_file_to_youtube(self, session: aiohttp.ClientSession, upload_url: str, file_url: str) -> Dict[str, Any]:
        """Upload file to YouTube (simplified implementation)"""        # In reality, this would handle resumable uploads for large files
        try:
            # This is a simplified version - actual implementation would stream the file
            upload_data = {"file_url": file_url}  # Placeholder
            
            async with session.put(upload_url, json=upload_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "video_id": result.get("id"),
                        "processing_details": result.get("processingDetails")
                    }
                else:
                    return {"success": False, "error": f"Upload failed with status {response.status}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _add_to_youtube_playlist(self, session: aiohttp.ClientSession, video_id: str, playlist_id: str):
        """Add video to YouTube playlist"""        config = self.platform_configs[PlatformType.YOUTUBE]
        
        playlist_item_data = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        
        playlist_url = f"{config['api_base']}/playlistItems?part=snippet"
        
        async with session.post(playlist_url, json=playlist_item_data) as response:
            if response.status != 200:
                logger.warning(f"Failed to add video {video_id} to playlist {playlist_id}")
    
    async def _create_instagram_reel(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Create Instagram Reel"""        config = self.platform_configs[PlatformType.INSTAGRAM]
        
        reel_data = {
            "video_url": content.file_url,
            "caption": f"{adaptations['description']}\n\n{' '.join(['#' + tag for tag in adaptations['hashtags']])}",
            "cover_url": content.thumbnail_url,
            "media_type": "REELS"
        }
        
        create_url = f"{config['api_base']}/me/media"
        
        async with session.post(create_url, data=reel_data) as response:
            if response.status != 200:
                response_text = await response.text()
                raise PlatformError(f"Instagram Reel creation failed: {response.status} - {response_text}")
            
            media_response = await response.json()
            creation_id = media_response["id"]
        
        # Publish the reel
        publish_url = f"{config['api_base']}/me/media_publish"
        publish_data = {"creation_id": creation_id}
        
        async with session.post(publish_url, data=publish_data) as response:
            if response.status != 200:
                response_text = await response.text()
                raise PlatformError(f"Instagram Reel publish failed: {response.status} - {response_text}")
            
            publish_response = await response.json()
            media_id = publish_response["id"]
        
        return {
            "post_id": media_id,
            "url": f"https://www.instagram.com/reel/{media_id}/",
            "metrics": {"reel_duration": content.duration or 0},
            "predicted_performance": await self._predict_instagram_performance(content, adaptations)
        }
    
    async def _create_instagram_story(
        self,
        session: aiohttp.ClientSession,
        content: ContentModel,
        adaptations: Dict[str, Any],
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Create Instagram Story"""        config = self.platform_configs[PlatformType.INSTAGRAM]
        
        story_data = {
            "image_url": content.file_url if content.content_type != ContentType.VIDEO else content.thumbnail_url,
            "video_url": content.file_url if content.content_type == ContentType.VIDEO else None,
            "media_type": "STORIES"
        }
        
        # Remove None values
        story_data = {k: v for k, v in story_data.items() if v is not None}
        
        create_url = f"{config['api_base']}/me/media"
        
        async with session.post(create_url, data=story_data) as response:
            if response.status != 200:
                response_text = await response.text()
                raise PlatformError(f"Instagram Story creation failed: {response.status} - {response_text}")
            
            media_response = await response.json()
            creation_id = media_response["id"]
        
        # Publish the story
        publish_url = f"{config['api_base']}/me/media_publish"
        publish_data = {"creation_id": creation_id}
        
        async with session.post(publish_url, data=publish_data) as response:
            if response.status != 200:
                response_text = await response.text()
                raise PlatformError(f"Instagram Story publish failed: {response.status} - {response_text}")
            
            publish_response = await response.json()
            media_id = publish_response["id"]
        
        return {
            "post_id": media_id,
            "url": f"https://www.instagram.com/stories/user/{media_id}/",
            "metrics": {"story_type": adaptations.get("story_type", "photo")},
            "predicted_performance": await self._predict_instagram_performance(content, adaptations)
        }
    
    async def _upload_twitter_media(self, session: aiohttp.ClientSession, content: ContentModel) -> Optional[str]:
        """Upload media to Twitter"""        config = self.platform_configs[PlatformType.TWITTER]
        
        try:
            # Simplified media upload - actual implementation would handle chunked uploads
            media_data = {
                "media_url": content.file_url,
                "media_type": content.content_type.value if content.content_type else "photo"
            }
            
            upload_url = f"{config['api_base']}/media/upload"
            
            async with session.post(upload_url, data=media_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("media_id_string")
                else:
                    logger.warning(f"Twitter media upload failed: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Twitter media upload error: {e}")
            return None
    
    async def __aenter__(self):
        """Async context manager entry"""        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""        # Close all active sessions
        for session in self.active_sessions.values():
            await session.close()
        self.active_sessions.clear()
