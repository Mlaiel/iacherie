"""Platform Coordinator - Advanced Orchestration
=============================================

Enhanced central coordinator for managing all platform API integrations.
Orchestrates authentication, data synchronization, cross-platform operations,
and advanced business logic integration for the Ainflue creator economy.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import hashlib
import secrets

# Enhanced imports for advanced functionality
from .platform_oauth_manager import PlatformOAuthManager, OAuthTokens
from .api_rate_limiter import APIRateLimiter
from .youtube_content_id_api import YouTubeContentIDAPI, YouTubeVideo, YouTubeAnalytics
from .instagram_business_api import InstagramBusinessAPI, InstagramMedia, InstagramInsights
from .tiktok_creator_api import TikTokCreatorAPI, TikTokVideo, TikTokAnalytics
from .spotify_artists_api import SpotifyArtistsAPI, SpotifyTrack, SpotifyAnalytics
from .facebook_rights_api import FacebookRightsAPI, FacebookRightsClaim
from .twitter_api_v2 import TwitterAPIv2, Tweet, TwitterAnalytics
from .dmca_services_api import DMCAServicesAPI, DMCARequest

logger = logging.getLogger(__name__)


class PlatformPriority(Enum):
    """Platform priority levels for creator economy workflow."""
    CRITICAL = "critical"      # YouTube, Instagram, TikTok
    HIGH = "high"             # Spotify, Twitter, Facebook
    MEDIUM = "medium"         # LinkedIn, Pinterest
    LOW = "low"              # Experimental platforms


class ContentSyncStrategy(Enum):
    """Content synchronization strategies."""
    IMMEDIATE = "immediate"    # Sync immediately across all platforms
    STAGED = "staged"         # Sync in priority order with delays
    SELECTIVE = "selective"   # Only sync to specified platforms
    AI_OPTIMIZED = "ai_optimized"  # AI determines optimal sync strategy


class CollaborationStatus(Enum):
    """Collaboration request status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class PlatformMetrics:
    """Enhanced platform performance metrics."""
    platform: str
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue_per_impression: float = 0.0
    audience_growth_rate: float = 0.0
    best_posting_times: List[str] = field(default_factory=list)
    top_hashtags: List[str] = field(default_factory=list)
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentOptimization:
    """AI-powered content optimization recommendations."""
    platform: str
    recommended_title: str
    recommended_description: str
    optimal_hashtags: List[str]
    best_posting_time: str
    expected_reach: int
    confidence_score: float
    seo_keywords: List[str]
    thumbnail_suggestions: List[str] = field(default_factory=list)


@dataclass
class CollaborationRequest:
    """Creator collaboration request."""
    id: str
    requester_id: str
    target_creator_id: str
    collaboration_type: str  # "video", "music", "photo", "live_stream"
    proposed_revenue_split: Dict[str, float]
    content_theme: str
    target_platforms: List[str]
    deadline: datetime
    status: CollaborationStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdvancedAnalytics:
    """Advanced cross-platform analytics with AI insights."""
    date_range: Dict[str, str]
    total_content: int = 0
    total_views: int = 0
    total_engagement: int = 0
    total_followers: int = 0
    total_revenue: float = 0.0
    platform_breakdown: Dict[str, PlatformMetrics] = field(default_factory=dict)
    top_performing_content: List[Dict[str, Any]] = field(default_factory=list)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    growth_predictions: Dict[str, float] = field(default_factory=dict)
    optimization_recommendations: List[ContentOptimization] = field(default_factory=list)
    collaboration_opportunities: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PlatformStatus:
    """Enhanced platform connection and health status."""
    platform: str
    is_connected: bool
    is_authenticated: bool
    last_sync: Optional[datetime] = None
    token_expires: Optional[datetime] = None
    error_message: Optional[str] = None
    rate_limit_status: Dict[str, Any] = None
    health_score: float = 1.0  # 0.0 to 1.0
    api_response_time: float = 0.0
    success_rate: float = 1.0
    priority: PlatformPriority = PlatformPriority.MEDIUM
    features_enabled: List[str] = field(default_factory=list)
    quota_usage: Dict[str, Any] = field(default_factory=dict)


class PlatformCoordinator:
    """
    Enhanced central coordinator for all platform integrations.
    
    Provides advanced orchestration for the Ainflue creator economy including:
    - Multi-platform content synchronization with AI optimization
    - Cross-platform analytics and insights
    - Creator collaboration matching and management
    - Advanced monetization tracking
    - SEO optimization across platforms
    - Real-time performance monitoring
    """
    
    def __init__(
        self,
        oauth_manager: Optional[PlatformOAuthManager] = None,
        rate_limiter: Optional[APIRateLimiter] = None,
        redis_url: Optional[str] = None
    ):
        self.oauth_manager = oauth_manager or PlatformOAuthManager()
        self.rate_limiter = rate_limiter or APIRateLimiter(redis_url)
        
        # Platform API instances
        self.youtube_api = YouTubeContentIDAPI(self.rate_limiter)
        self.instagram_api = InstagramBusinessAPI(self.rate_limiter)
        self.tiktok_api = TikTokCreatorAPI(self.rate_limiter)
        self.spotify_api = SpotifyArtistsAPI(self.rate_limiter)
        self.facebook_api = FacebookRightsAPI(self.rate_limiter)
        self.twitter_api = TwitterAPIv2(self.rate_limiter)
        self.dmca_api = DMCAServicesAPI(self.rate_limiter)
        
        # Token storage (in production, this should be a secure database)
        self.tokens_storage: Dict[str, Dict[str, OAuthTokens]] = {}
        
        # Platform health status
        self.platform_status: Dict[str, PlatformStatus] = {}
        
    async def __aenter__(self):
        """
Async context manager entry"""
        await self.oauth_manager.__aenter__()
        await self.rate_limiter.__aenter__()
        await self.youtube_api.__aenter__()
        await self.instagram_api.__aenter__()
        await self.tiktok_api.__aenter__()
        await self.spotify_api.__aenter__()
        await self.facebook_api.__aenter__()
        await self.twitter_api.__aenter__()
        await self.dmca_api.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit"""
        await self.oauth_manager.__aexit__(exc_type, exc_val, exc_tb)
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        await self.youtube_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.instagram_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.tiktok_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.spotify_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.facebook_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.twitter_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.dmca_api.__aexit__(exc_type, exc_val, exc_tb)
        
    def configure_platform_oauth(
        self,
        platform: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: Optional[List[str]] = None
    ):
        """
Configure OAuth settings for a platform"""
        self.oauth_manager.configure_platform(
            platform, client_id, client_secret, redirect_uri, scopes
        )
        logger.info(f"Configured OAuth for platform: {platform}")
        
    async def initiate_platform_auth(
        self,
        platform: str,
        user_id: str
    ) -> str:
        """Initiate OAuth authentication for a platform"""
        auth_url, state = self.oauth_manager.generate_authorization_url(platform, user_id)
        logger.info(f"Generated auth URL for {platform}: {auth_url[:100]}...")
        return auth_url
        
    async def complete_platform_auth(
        self,
        platform: str,
        user_id: str,
        authorization_code: str,
        state: str
    ) -> bool:
        """Complete OAuth authentication and store tokens"""
        try:
            tokens = await self.oauth_manager.exchange_code_for_tokens(
                platform, authorization_code, state
            )
            
            # Store tokens
            if user_id not in self.tokens_storage:
                self.tokens_storage[user_id] = {}
            self.tokens_storage[user_id][platform] = tokens
            
            # Update platform status
            self.platform_status[f"{user_id}:{platform}"] = PlatformStatus(
                platform=platform,
                is_connected=True,
                is_authenticated=True,
                last_sync=datetime.now(),
                token_expires=tokens.expires_at
            )
            
            logger.info(f"Completed authentication for {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete authentication for {platform}: {e}")
            self.platform_status[f"{user_id}:{platform}"] = PlatformStatus(
                platform=platform,
                is_connected=False,
                is_authenticated=False,
                error_message=str(e)
            )
            return False
            
    async def get_user_tokens(self, user_id: str, platform: str) -> Optional[OAuthTokens]:
        """Get stored tokens for a user and platform"""
        user_tokens = self.tokens_storage.get(user_id, {})
        tokens = user_tokens.get(platform)
        
        if tokens and tokens.expires_at and datetime.now() >= tokens.expires_at:
            # Token expired, try to refresh
            try:
                if tokens.refresh_token:
                    new_tokens = await self.oauth_manager.refresh_access_token(
                        platform, tokens.refresh_token
                    )
                    new_tokens.user_id = user_id
                    self.tokens_storage[user_id][platform] = new_tokens
                    return new_tokens
                else:
                    logger.warning(f"No refresh token available for {platform}")
                    return True
            except Exception as e:
                logger.error(f"Failed to refresh token for {platform}: {e}")
                return True
                
        return tokens
        
    async def check_platform_health(self, user_id: str, platform: str) -> PlatformStatus:
        """Check health status of a platform connection"""
        tokens = await self.get_user_tokens(user_id, platform)
        
        if not tokens:
            status = PlatformStatus(
                platform=platform,
                is_connected=False,
                is_authenticated=False,
                error_message="No valid tokens"
            )
        else:
            try:
                # Validate tokens by making a test API call
                is_valid = await self.oauth_manager.validate_tokens(tokens)
                
                status = PlatformStatus(
                    platform=platform,
                    is_connected=is_valid,
                    is_authenticated=is_valid,
                    last_sync=datetime.now(),
                    token_expires=tokens.expires_at,
                    rate_limit_status=await self.rate_limiter.get_platform_status(platform)
                )
                
                if not is_valid:
                    status.error_message = "Token validation failed"
                    
            except Exception as e:
                status = PlatformStatus(
                    platform=platform,
                    is_connected=False,
                    is_authenticated=False,
                    error_message=str(e)
                )
                
        self.platform_status[f"{user_id}:{platform}"] = status
        return status
        
    async def get_all_platform_status(self, user_id: str) -> Dict[str, PlatformStatus]:
        """Get health status for all platforms for a user"""
        supported_platforms = self.oauth_manager.get_supported_platforms()
        status_dict = {}
        
        tasks = []
        for platform in supported_platforms:
            tasks.append(self.check_platform_health(user_id, platform))
            
        statuses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, platform in enumerate(supported_platforms):
            if isinstance(statuses[i], Exception):
                status_dict[platform] = PlatformStatus(
                    platform=platform,
                    is_connected=False,
                    is_authenticated=False,
                    error_message=str(statuses[i])
                )
            else:
                status_dict[platform] = statuses[i]
                
        return status_dict
        
    async def sync_content_across_platforms(
        self,
        user_id: str,
        content_title: str,
        content_description: str,
        content_file_path: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        platform_specific_data: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
Sync content across multiple platforms"""
        
        platforms = platforms or ["youtube", "instagram", "tiktok", "twitter"]
        platform_specific_data = platform_specific_data or {}
        results = {}
        
        for platform in platforms:
            tokens = await self.get_user_tokens(user_id, platform)
            if not tokens:
                results[platform] = {"success": False, "error": "No valid tokens"}
                continue
                
            try:
                platform_data = platform_specific_data.get(platform, {})
                
                if platform == "youtube" and content_file_path:
                    video = await self.youtube_api.upload_video(
                        tokens, content_file_path, content_title, content_description,
                        **platform_data
                    )
                    results[platform] = {"success": True, "content_id": video.video_id}
                    
                elif platform == "instagram":
                    # Instagram requires media URL, not file upload
                    if "media_url" in platform_data:
                        container_id = await self.instagram_api.create_media_container(
                            tokens, "me", platform_data.get("media_type", "IMAGE"),
                            platform_data["media_url"], content_description
                        )
                        media_id = await self.instagram_api.publish_media(
                            tokens, "me", container_id
                        )
                        results[platform] = {"success": True, "content_id": media_id}
                    else:
                        results[platform] = {"success": False, "error": "Media URL required"}
                        
                elif platform == "tiktok" and content_file_path:
                    video_id = await self.tiktok_api.upload_video(
                        tokens, content_file_path, content_title, content_description,
                        **platform_data
                    )
                    results[platform] = {"success": True, "content_id": video_id}
                    
                elif platform == "twitter":
                    # Twitter text post
                    tweet_text = f"{content_title}\n\n{content_description}"
                    if len(tweet_text) > 280:
                        tweet_text = tweet_text[:277] + "..."
                        
                    tweet = await self.twitter_api.create_tweet(
                        tokens, tweet_text, **platform_data
                    )
                    results[platform] = {"success": True, "content_id": tweet.tweet_id}
                    
                else:
                    results[platform] = {"success": False, "error": "Platform not supported for this content type"}
                    
            except Exception as e:
                logger.error(f"Failed to sync content to {platform}: {e}")
                results[platform] = {"success": False, "error": str(e)}
                
        return results
        
    async def get_aggregated_analytics(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        platforms: Optional[List[str]] = None
    ) -> CrossPlatformAnalytics:
        """Get aggregated analytics across all platforms"""
        
        platforms = platforms or ["youtube", "instagram", "tiktok", "spotify", "twitter"]
        platform_breakdown = {}
        
        total_content = 0
        total_views = 0
        total_engagement = 0
        total_followers = 0
        total_revenue = 0.0
        
        for platform in platforms:
            tokens = await self.get_user_tokens(user_id, platform)
            if not tokens:
                continue
                
            try:
                platform_data = {"views": 0, "engagement": 0, "followers": 0, "revenue": 0.0, "content_count": 0}
                
                if platform == "youtube":
                    # Get channel info and analytics
                    channel_info = await self.youtube_api.get_channel_info(tokens)
                    if channel_info.get("items"):
                        channel_id = channel_info["items"][0]["id"]
                        analytics = await self.youtube_api.get_analytics(
                            tokens, channel_id, start_date, end_date
                        )
                        
                        platform_data["views"] = analytics.views
                        platform_data["engagement"] = analytics.likes + analytics.comments + analytics.shares
                        platform_data["followers"] = channel_info["items"][0]["statistics"].get("subscriberCount", 0)
                        platform_data["revenue"] = analytics.estimated_revenue
                        
                elif platform == "instagram":
                    user_info = await self.instagram_api.get_user_info(tokens)
                    insights = await self.instagram_api.get_account_insights(
                        tokens, "me", "day", start_date, end_date
                    )
                    
                    platform_data["views"] = insights.impressions
                    platform_data["engagement"] = insights.engagement
                    platform_data["followers"] = user_info.followers_count
                    
                elif platform == "tiktok":
                    user_info = await self.tiktok_api.get_user_info(tokens)
                    analytics = await self.tiktok_api.get_creator_insights(
                        tokens, (end_date - start_date).days
                    )
                    
                    platform_data["views"] = analytics.video_views
                    platform_data["engagement"] = analytics.likes + analytics.comments + analytics.shares
                    platform_data["followers"] = user_info.follower_count
                    
                elif platform == "spotify":
                    profile = await self.spotify_api.get_current_user_profile(tokens)
                    # Note: Spotify for Artists analytics would require special access
                    platform_data["followers"] = profile.get("followers", {}).get("total", 0)
                    
                elif platform == "twitter":
                    user_info = await self.twitter_api.get_me(tokens)
                    platform_data["followers"] = user_info.public_metrics.get("followers_count", 0)
                    platform_data["engagement"] = user_info.public_metrics.get("like_count", 0)
                    
                # Aggregate totals
                total_views += int(platform_data["views"])
                total_engagement += int(platform_data["engagement"])
                total_followers += int(platform_data["followers"])
                total_revenue += float(platform_data["revenue"])
                total_content += int(platform_data["content_count"])
                
                platform_breakdown[platform] = platform_data
                
            except Exception as e:
                logger.error(f"Failed to get analytics for {platform}: {e}")
                platform_breakdown[platform] = {"error": str(e)}
                
        analytics = CrossPlatformAnalytics(
            date_range={
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            total_content=total_content,
            total_views=total_views,
            total_engagement=total_engagement,
            total_followers=total_followers,
            total_revenue=total_revenue,
            platform_breakdown=platform_breakdown
        )
        
        return analytics
        
    async def monitor_content_protection(
        self,
        user_id: str,
        content_title: str,
        content_type: str,
        keywords: List[str]
    ) -> str:
        """Set up content protection monitoring across platforms"""
        
        platforms = ["youtube", "facebook", "instagram", "tiktok"]
        
        monitor_id = await self.dmca_api.create_content_monitor(
            content_title, content_type, keywords, platforms
        )
        
        logger.info(f"Created content protection monitor: {monitor_id.monitor_id}")
        return monitor_id.monitor_id
        
    async def handle_copyright_infringement(
        self,
        user_id: str,
        infringing_url: str,
        original_content_url: str,
        description: str
    ) -> str:
        """Handle copyright infringement with automated takedown"""
        
        copyright_holder = f"User {user_id}"  # In production, get from user profile
        
        takedown_request = await self.dmca_api.submit_takedown_request(
            original_content_url, infringing_url, copyright_holder, description
        )
        
        logger.info(f"Submitted copyright takedown: {takedown_request.request_id}")
        return takedown_request.request_id
        
    async def get_platform_insights(
        self,
        user_id: str,
        platform: str,
        insight_type: str = "overview"
    ) -> Dict[str, Any]:
        """Get detailed insights for a specific platform"""
        
        tokens = await self.get_user_tokens(user_id, platform)
        if not tokens:
            return {"error": "No valid tokens for platform"}
            
        try:
            if platform == "youtube":
                channel_info = await self.youtube_api.get_channel_info(tokens)
                return {"channel_info": channel_info}
                
            elif platform == "instagram":
                user_info = await self.instagram_api.get_user_info(tokens)
                return {"user_info": asdict(user_info)}
                
            elif platform == "tiktok":
                user_info = await self.tiktok_api.get_user_info(tokens)
                return {"user_info": asdict(user_info)}
                
            elif platform == "spotify":
                profile = await self.spotify_api.get_current_user_profile(tokens)
                return {"profile": profile}
                
            elif platform == "twitter":
                user_info = await self.twitter_api.get_me(tokens)
                return {"user_info": asdict(user_info)}
                
            else:
                return {"error": f"Insights not available for platform: {platform}"}
                
        except Exception as e:
            logger.error(f"Failed to get insights for {platform}: {e}")
            return {"error": str(e)}
            
    async def cleanup_expired_tokens(self):
        """Clean up expired tokens and OAuth states"""
        current_time = datetime.now()
        
        for user_id, user_tokens in self.tokens_storage.items():
            expired_platforms = []
            for platform, tokens in user_tokens.items():
                if tokens.expires_at and current_time >= tokens.expires_at:
                    if not tokens.refresh_token:
                        expired_platforms.append(platform)
                        
            for platform in expired_platforms:
                del user_tokens[platform]
                logger.info(f"Removed expired token for {user_id}:{platform}")
                
        # Clean up OAuth states
        self.oauth_manager.cleanup_expired_states()
        
    async def disconnect_platform(self, user_id: str, platform: str) -> bool:
        """Disconnect a platform for a user"""
        try:
            # Remove stored tokens
            if user_id in self.tokens_storage and platform in self.tokens_storage[user_id]:
                del self.tokens_storage[user_id][platform]
                
            # Update status
            self.platform_status[f"{user_id}:{platform}"] = PlatformStatus(
                platform=platform,
                is_connected=False,
                is_authenticated=False
            )
            
            logger.info(f"Disconnected platform: {user_id}:{platform}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect platform {platform}: {e}")
            return False