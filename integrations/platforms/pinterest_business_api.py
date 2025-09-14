"""
Pinterest Business API Integration for Ainflue Platform
Enterprise-grade Pinterest creator and visual content management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
import logging
from dataclasses import dataclass, field
from enum import Enum
import base64
import uuid
import urllib.parse

import aiohttp
import structlog

from ..core.base_integration import BaseIntegration
from ..core.exceptions import (
    APIError, InvalidConfigurationError, 
    SecurityError, ValidationError
)
from ..core.security import SecurityManager
from ..core.monitoring import MetricsCollector
from ..core.cache import CacheManager

logger = structlog.get_logger(__name__)

class PinterestScope(Enum):
    """Pinterest API OAuth scopes"""
    READ_PUBLIC = "read_public"
    WRITE_PUBLIC = "write_public"
    READ_RELATIONSHIPS = "read_relationships"
    WRITE_RELATIONSHIPS = "write_relationships"
    ADS_READ = "ads:read"
    ADS_WRITE = "ads:write"
    CATALOGS_READ = "catalogs:read"
    CATALOGS_WRITE = "catalogs:write"

class PinFormat(Enum):
    """Pinterest pin formats"""
    PRODUCT = "product"
    RECIPE = "recipe"
    ARTICLE = "article"
    APP = "app"
    VIDEO = "video"
    CAROUSEL = "carousel"
    IDEA = "idea"

class BoardPrivacy(Enum):
    """Pinterest board privacy settings"""
    PUBLIC = "public"
    PROTECTED = "protected"
    SECRET = "secret"

class VideoStatus(Enum):
    """Pinterest video processing status"""
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class AdStatus(Enum):
    """Pinterest ad status"""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"
    DRAFT = "DRAFT"

@dataclass
class PinterestConfig:
    """Pinterest API configuration"""
    app_id: str
    app_secret: str
    redirect_uri: str
    scopes: List[PinterestScope]
    api_version: str = "v5"
    environment: str = "production"  # production or sandbox
    rate_limit_requests: int = 1000  # requests per hour
    rate_limit_window: int = 3600  # 1 hour
    webhook_secret: Optional[str] = None
    
    def __post_init__(self) -> None:
        if not self.scopes:
            self.scopes = [
                PinterestScope.READ_PUBLIC,
                PinterestScope.WRITE_PUBLIC
            ]

@dataclass
class PinterestUser:
    """Pinterest user profile data"""
    id: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    bio: Optional[str]
    profile_image: Optional[str]
    website_url: Optional[str]
    verified: bool = False
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    pin_count: Optional[int] = None
    board_count: Optional[int] = None
    monthly_views: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PinterestBoard:
    """Pinterest board data"""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    privacy: BoardPrivacy
    category: Optional[str] = None
    pin_count: Optional[int] = None
    follower_count: Optional[int] = None
    cover_pin: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PinterestPin:
    """Pinterest pin data"""
    id: str
    title: str
    description: Optional[str]
    link: Optional[str]
    board_id: str
    creator_id: str
    image_url: str
    pin_format: PinFormat = PinFormat.IDEA
    alt_text: Optional[str] = None
    color: Optional[str] = None
    note: Optional[str] = None
    dominant_color: Optional[str] = None
    is_standard: bool = True
    has_been_promoted: bool = False
    save_count: Optional[int] = None
    comment_count: Optional[int] = None
    reaction_count: Optional[int] = None
    click_count: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PinterestAnalytics:
    """Pinterest analytics data"""
    pin_id: Optional[str] = None
    board_id: Optional[str] = None
    user_id: Optional[str] = None
    impressions: int = 0
    saves: int = 0
    pin_clicks: int = 0
    outbound_clicks: int = 0
    video_views: int = 0
    video_starts: int = 0
    video_avg_watch_time: float = 0.0
    carousel_card_swipes: int = 0
    collected_at: datetime = field(default_factory=datetime.utcnow)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None

@dataclass
class PinterestAd:
    """Pinterest advertising data"""
    id: str
    name: str
    status: AdStatus
    campaign_id: str
    ad_group_id: str
    creative_type: str
    pin_id: str
    destination_url: Optional[str] = None
    tracking_urls: Dict[str, str] = field(default_factory=dict)
    is_pin_deleted: bool = False
    is_removable: bool = True
    created_time: datetime = field(default_factory=datetime.utcnow)
    updated_time: datetime = field(default_factory=datetime.utcnow)

class PinterestBusinessAPI(BaseIntegration):
    """
    Enterprise Pinterest Business API integration for Ainflue platform
    
    Features:
    - Complete Pinterest OAuth 2.0 authentication
    - Visual content creation and publishing
    - Board management and organization
    - Advanced analytics and performance tracking
    - Pinterest Ads management and optimization
    - Rich Pin implementation
    - Video content support
    - Carousel pin creation
    - Shopping integration
    - Trend analysis and insights
    """

    def __init__(self, config -> None: PinterestConfig) -> None:
        super().__init__("pinterest_business")
        self.config = config
        self.security_manager = SecurityManager()
        self.metrics = MetricsCollector()
        self.cache = CacheManager()
        
        # API endpoints
        self.base_url = "https://api.pinterest.com"
        self.auth_url = "https://www.pinterest.com/oauth"
        
        # Headers template
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Ainflue/1.0.0"
        }
        
        # Rate limiting
        self.rate_limiter = {}
        
        # Storage
        self._users: Dict[str, PinterestUser] = {}
        self._boards: Dict[str, PinterestBoard] = {}
        self._pins: Dict[str, PinterestPin] = {}
        self._analytics: Dict[str, List[PinterestAnalytics]] = {}
        
        logger.info("Pinterest Business API integration initialized",
                   app_id=config.app_id[:8] + "...",
                   scopes=len(config.scopes),
                   api_version=config.api_version)

    async def get_authorization_url(self, 
                                  state: Optional[str] = None) -> str:
        """
        Generate Pinterest OAuth authorization URL
        
        Args:
            state: Optional state parameter for security
            
        Returns:
            Authorization URL for user redirect
        """
        try:
            # Prepare scopes
            scope_string = ",".join([scope.value for scope in self.config.scopes])
            
            # Prepare parameters
            params = {
                "response_type": "code",
                "client_id": self.config.app_id,
                "redirect_uri": self.config.redirect_uri,
                "scope": scope_string
            }
            
            if state:
                params["state"] = state
            
            # Build URL
            auth_url = f"{self.auth_url}/?" + urllib.parse.urlencode(params)
            
            self.metrics.increment("pinterest.auth_urls.generated")
            
            logger.info("Pinterest authorization URL generated",
                       scopes=len(self.config.scopes),
                       has_state=bool(state))
            
            return auth_url
            
        except Exception as e:
            self.metrics.increment("pinterest.auth_urls.failed")
            logger.error("Failed to generate authorization URL", error=str(e))
            raise ValidationError(f"Authorization URL generation failed: {e}")

    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_code: Authorization code from callback
            
        Returns:
            Token response with access_token and metadata
        """
        try:
            token_data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": self.config.redirect_uri,
                "client_id": self.config.app_id,
                "client_secret": self.config.app_secret
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.auth_url}/token",
                    data=token_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise APIError(f"Token exchange failed: {error_text}")
                    
                    token_response = await response.json()
                    
                    # Store token with expiration
                    expires_in = token_response.get("expires_in", 3600)
                    token_response["expires_at"] = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    # Cache token
                    await self.cache.set(
                        f"pinterest_token:{authorization_code[:10]}",
                        token_response,
                        ttl=expires_in - 300  # Refresh 5 minutes before expiry
                    )
                    
                    self.metrics.increment("pinterest.tokens.exchanged")
                    
                    logger.info("Pinterest token exchange successful",
                               expires_in=expires_in)
                    
                    return token_response
                    
        except Exception as e:
            self.metrics.increment("pinterest.tokens.exchange_failed")
            logger.error("Token exchange failed", error=str(e))
            raise APIError(f"Token exchange failed: {e}")

    async def _make_authenticated_request(self,
                                        method: str,
                                        endpoint: str,
                                        access_token: str,
                                        data: Optional[Dict[str, Any]] = None,
                                        params: Optional[Dict[str, Any]] = None,
                                        files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make authenticated request to Pinterest API"""
        url = f"{self.base_url}/{self.config.api_version}{endpoint}"
        
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}"
        }
        
        # Handle file uploads
        if files:
            headers.pop("Content-Type", None)  # Let aiohttp set multipart content-type
        
        try:
            async with aiohttp.ClientSession() as session:
                if files:
                    # Multipart form data for file uploads
                    form_data = aiohttp.FormData()
                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, str(value))
                    for key, file_data in files.items():
                        form_data.add_field(key, file_data)
                    request_data = form_data
                else:
                    request_data = data
                
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=request_data if not files else None,
                    data=request_data if files else None,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning("Pinterest API rate limited",
                                     retry_after=retry_after)
                        raise APIError(f"Rate limited. Retry after {retry_after} seconds")
                    
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error("Pinterest API error",
                                   status=response.status,
                                   error=error_msg,
                                   endpoint=endpoint)
                        raise APIError(f"Pinterest API error: {error_msg}")
                    
                    return response_data
                    
        except aiohttp.ClientError as e:
            logger.error("Pinterest API request failed",
                        endpoint=endpoint,
                        error=str(e))
            raise APIError(f"API request failed: {e}")

    async def get_user_profile(self, access_token: str) -> PinterestUser:
        """
        Get authenticated user's Pinterest profile
        
        Args:
            access_token: Pinterest access token
            
        Returns:
            Pinterest user profile data
        """
        try:
            # Get user profile
            profile_data = await self._make_authenticated_request(
                "GET",
                "/user_account",
                access_token
            )
            
            user_id = profile_data["id"]
            
            # Get additional profile stats
            stats_data = await self._make_authenticated_request(
                "GET",
                f"/user_account/analytics",
                access_token,
                params={"start_date": "2024-01-01", "end_date": "2024-12-31"}
            )
            
            # Create user object
            pinterest_user = PinterestUser(
                id=user_id,
                username=profile_data.get("username", ""),
                first_name=profile_data.get("first_name"),
                last_name=profile_data.get("last_name"),
                display_name=profile_data.get("display_name"),
                bio=profile_data.get("bio"),
                profile_image=profile_data.get("profile_image"),
                website_url=profile_data.get("website_url"),
                verified=profile_data.get("verified", False),
                follower_count=profile_data.get("follower_count"),
                following_count=profile_data.get("following_count"),
                pin_count=profile_data.get("pin_count"),
                board_count=profile_data.get("board_count"),
                monthly_views=stats_data.get("monthly_views", 0) if stats_data else None
            )
            
            # Store user
            self._users[user_id] = pinterest_user
            
            # Cache user data
            await self.cache.set(
                f"pinterest_user:{user_id}",
                pinterest_user,
                ttl=3600  # 1 hour
            )
            
            self.metrics.increment("pinterest.profiles.retrieved")
            
            logger.info("Pinterest user profile retrieved",
                       user_id=user_id,
                       username=pinterest_user.username)
            
            return pinterest_user
            
        except Exception as e:
            self.metrics.increment("pinterest.profiles.failed")
            logger.error("Failed to get user profile", error=str(e))
            raise APIError(f"Failed to get user profile: {e}")

    async def create_board(self,
                         access_token: str,
                         name: str,
                         description: Optional[str] = None,
                         privacy: BoardPrivacy = BoardPrivacy.PUBLIC) -> PinterestBoard:
        """
        Create a new Pinterest board
        
        Args:
            access_token: Pinterest access token
            name: Board name
            description: Board description
            privacy: Board privacy setting
            
        Returns:
            Created Pinterest board
        """
        try:
            board_data = {
                "name": name,
                "privacy": privacy.value
            }
            
            if description:
                board_data["description"] = description
            
            response = await self._make_authenticated_request(
                "POST",
                "/boards",
                access_token,
                data=board_data
            )
            
            board_id = response["id"]
            
            board = PinterestBoard(
                id=board_id,
                name=response["name"],
                description=response.get("description"),
                owner_id=response.get("owner", {}).get("id", ""),
                privacy=BoardPrivacy(response.get("privacy", "public")),
                category=response.get("category"),
                pin_count=response.get("pin_count", 0),
                follower_count=response.get("follower_count", 0)
            )
            
            # Store board
            self._boards[board_id] = board
            
            # Cache board data
            await self.cache.set(
                f"pinterest_board:{board_id}",
                board,
                ttl=7200  # 2 hours
            )
            
            self.metrics.increment("pinterest.boards.created")
            
            logger.info("Pinterest board created",
                       board_id=board_id,
                       name=board.name,
                       privacy=privacy.value)
            
            return board
            
        except Exception as e:
            self.metrics.increment("pinterest.boards.creation_failed")
            logger.error("Failed to create board", error=str(e))
            raise APIError(f"Failed to create board: {e}")

    async def upload_media(self,
                         access_token: str,
                         media_data: bytes,
                         media_type: str) -> str:
        """
        Upload media to Pinterest
        
        Args:
            access_token: Pinterest access token
            media_data: Media file bytes
            media_type: MIME type of media
            
        Returns:
            Media URL for pin creation
        """
        try:
            # Pinterest media upload process
            # Step 1: Register upload
            upload_request = {
                "media_type": "image" if "image" in media_type else "video"
            }
            
            upload_response = await self._make_authenticated_request(
                "POST",
                "/media",
                access_token,
                data=upload_request
            )
            
            media_id = upload_response["media_id"]
            upload_url = upload_response["upload_url"]
            upload_parameters = upload_response.get("upload_parameters", {})
            
            # Step 2: Upload to provided URL
            upload_data = aiohttp.FormData()
            
            # Add upload parameters
            for key, value in upload_parameters.items():
                upload_data.add_field(key, value)
            
            # Add file
            upload_data.add_field("file", media_data, content_type=media_type)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(upload_url, data=upload_data) as upload_resp:
                    if upload_resp.status not in [200, 201, 204]:
                        error_text = await upload_resp.text()
                        raise APIError(f"Media upload failed: {error_text}")
            
            # Step 3: Get media status
            media_status = await self._make_authenticated_request(
                "GET",
                f"/media/{media_id}",
                access_token
            )
            
            media_url = media_status.get("url")
            if not media_url:
                raise APIError("Media upload completed but URL not available")
            
            self.metrics.increment("pinterest.media.uploaded")
            self.metrics.observe("pinterest.media.size", len(media_data))
            
            logger.info("Pinterest media uploaded",
                       media_id=media_id,
                       media_type=media_type,
                       size=len(media_data))
            
            return media_url
            
        except Exception as e:
            self.metrics.increment("pinterest.media.upload_failed")
            logger.error("Failed to upload media", error=str(e))
            raise APIError(f"Failed to upload media: {e}")

    async def create_pin(self,
                       access_token: str,
                       board_id: str,
                       title: str,
                       media_url: str,
                       description: Optional[str] = None,
                       link: Optional[str] = None,
                       alt_text: Optional[str] = None) -> PinterestPin:
        """
        Create a new Pinterest pin
        
        Args:
            access_token: Pinterest access token
            board_id: Board ID to add pin to
            title: Pin title
            media_url: URL of uploaded media
            description: Pin description
            link: Destination URL for pin
            alt_text: Alt text for accessibility
            
        Returns:
            Created Pinterest pin
        """
        try:
            pin_data = {
                "board_id": board_id,
                "title": title,
                "media_source": {
                    "source_type": "image_url",
                    "url": media_url
                }
            }
            
            if description:
                pin_data["description"] = description
            
            if link:
                pin_data["link"] = link
            
            if alt_text:
                pin_data["alt_text"] = alt_text
            
            response = await self._make_authenticated_request(
                "POST",
                "/pins",
                access_token,
                data=pin_data
            )
            
            pin_id = response["id"]
            
            pin = PinterestPin(
                id=pin_id,
                title=response["title"],
                description=response.get("description"),
                link=response.get("link"),
                board_id=response.get("board_id", board_id),
                creator_id=response.get("creator", {}).get("id", ""),
                image_url=response.get("media", {}).get("url", media_url),
                alt_text=response.get("alt_text"),
                color=response.get("color"),
                dominant_color=response.get("dominant_color")
            )
            
            # Store pin
            self._pins[pin_id] = pin
            
            # Cache pin data
            await self.cache.set(
                f"pinterest_pin:{pin_id}",
                pin,
                ttl=86400  # 24 hours
            )
            
            self.metrics.increment("pinterest.pins.created")
            
            logger.info("Pinterest pin created",
                       pin_id=pin_id,
                       board_id=board_id,
                       title=title)
            
            return pin
            
        except Exception as e:
            self.metrics.increment("pinterest.pins.creation_failed")
            logger.error("Failed to create pin", error=str(e))
            raise APIError(f"Failed to create pin: {e}")

    async def create_idea_pin(self,
                            access_token: str,
                            title: str,
                            pages: List[Dict[str, Any]],
                            description: Optional[str] = None) -> PinterestPin:
        """
        Create a Pinterest Idea Pin (Story Pin)
        
        Args:
            access_token: Pinterest access token
            title: Idea Pin title
            pages: List of pages with media and text
            description: Pin description
            
        Returns:
            Created Pinterest Idea Pin
        """
        try:
            pin_data = {
                "title": title,
                "media_source": {
                    "source_type": "multiple_image_urls",
                    "items": pages
                },
                "pin_format": "story"
            }
            
            if description:
                pin_data["description"] = description
            
            response = await self._make_authenticated_request(
                "POST",
                "/pins",
                access_token,
                data=pin_data
            )
            
            pin_id = response["id"]
            
            pin = PinterestPin(
                id=pin_id,
                title=response["title"],
                description=response.get("description"),
                board_id="",  # Idea pins don't require boards
                creator_id=response.get("creator", {}).get("id", ""),
                image_url=response.get("media", {}).get("url", ""),
                pin_format=PinFormat.IDEA
            )
            
            # Store pin
            self._pins[pin_id] = pin
            
            # Cache pin data
            await self.cache.set(
                f"pinterest_pin:{pin_id}",
                pin,
                ttl=86400  # 24 hours
            )
            
            self.metrics.increment("pinterest.idea_pins.created")
            
            logger.info("Pinterest Idea Pin created",
                       pin_id=pin_id,
                       title=title,
                       pages=len(pages))
            
            return pin
            
        except Exception as e:
            self.metrics.increment("pinterest.idea_pins.creation_failed")
            logger.error("Failed to create Idea Pin", error=str(e))
            raise APIError(f"Failed to create Idea Pin: {e}")

    async def get_pin_analytics(self,
                              access_token: str,
                              pin_id: str,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> PinterestAnalytics:
        """
        Get analytics for a Pinterest pin
        
        Args:
            access_token: Pinterest access token
            pin_id: Pin ID to analyze
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Pin analytics data
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "metric_types": "IMPRESSION,SAVE,PIN_CLICK,OUTBOUND_CLICK,VIDEO_MRC_VIEW,VIDEO_START"
            }
            
            response = await self._make_authenticated_request(
                "GET",
                f"/pins/{pin_id}/analytics",
                access_token,
                params=params
            )
            
            # Process analytics data
            all_time_metrics = response.get("all_time", {})
            daily_metrics = response.get("daily_metrics", [])
            
            analytics = PinterestAnalytics(
                pin_id=pin_id,
                impressions=all_time_metrics.get("IMPRESSION", 0),
                saves=all_time_metrics.get("SAVE", 0),
                pin_clicks=all_time_metrics.get("PIN_CLICK", 0),
                outbound_clicks=all_time_metrics.get("OUTBOUND_CLICK", 0),
                video_views=all_time_metrics.get("VIDEO_MRC_VIEW", 0),
                video_starts=all_time_metrics.get("VIDEO_START", 0),
                date_range_start=start_date,
                date_range_end=end_date
            )
            
            # Store analytics
            if pin_id not in self._analytics:
                self._analytics[pin_id] = []
            self._analytics[pin_id].append(analytics)
            
            # Cache analytics
            await self.cache.set(
                f"pinterest_analytics:{pin_id}",
                analytics,
                ttl=3600  # 1 hour
            )
            
            self.metrics.increment("pinterest.analytics.retrieved")
            
            logger.info("Pinterest pin analytics retrieved",
                       pin_id=pin_id,
                       impressions=analytics.impressions,
                       saves=analytics.saves)
            
            return analytics
            
        except Exception as e:
            self.metrics.increment("pinterest.analytics.failed")
            logger.error("Failed to get pin analytics",
                        pin_id=pin_id,
                        error=str(e))
            raise APIError(f"Failed to get pin analytics: {e}")

    async def get_user_boards(self,
                            access_token: str,
                            page_size: int = 25,
                            bookmark: Optional[str] = None) -> List[PinterestBoard]:
        """
        Get user's Pinterest boards
        
        Args:
            access_token: Pinterest access token
            page_size: Number of boards per page
            bookmark: Pagination bookmark
            
        Returns:
            List of user's Pinterest boards
        """
        try:
            params = {"page_size": page_size}
            if bookmark:
                params["bookmark"] = bookmark
            
            response = await self._make_authenticated_request(
                "GET",
                "/boards",
                access_token,
                params=params
            )
            
            boards = []
            for item in response.get("items", []):
                board = PinterestBoard(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description"),
                    owner_id=item.get("owner", {}).get("id", ""),
                    privacy=BoardPrivacy(item.get("privacy", "public")),
                    category=item.get("category"),
                    pin_count=item.get("pin_count", 0),
                    follower_count=item.get("follower_count", 0)
                )
                
                boards.append(board)
                self._boards[board.id] = board
            
            self.metrics.increment("pinterest.boards.retrieved")
            
            logger.info("Pinterest user boards retrieved",
                       count=len(boards))
            
            return boards
            
        except Exception as e:
            self.metrics.increment("pinterest.boards.retrieval_failed")
            logger.error("Failed to get user boards", error=str(e))
            raise APIError(f"Failed to get user boards: {e}")

    async def search_pins(self,
                        access_token: str,
                        query: str,
                        limit: int = 20) -> List[PinterestPin]:
        """
        Search for Pinterest pins
        
        Args:
            access_token: Pinterest access token
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching pins
        """
        try:
            params = {
                "query": query,
                "limit": limit
            }
            
            response = await self._make_authenticated_request(
                "GET",
                "/search/pins",
                access_token,
                params=params
            )
            
            pins = []
            for item in response.get("items", []):
                pin = PinterestPin(
                    id=item["id"],
                    title=item.get("title", ""),
                    description=item.get("description"),
                    link=item.get("link"),
                    board_id=item.get("board_id", ""),
                    creator_id=item.get("creator", {}).get("id", ""),
                    image_url=item.get("media", {}).get("url", ""),
                    color=item.get("color"),
                    dominant_color=item.get("dominant_color")
                )
                
                pins.append(pin)
                self._pins[pin.id] = pin
            
            self.metrics.increment("pinterest.pins.searched")
            
            logger.info("Pinterest pins searched",
                       query=query,
                       results=len(pins))
            
            return pins
            
        except Exception as e:
            self.metrics.increment("pinterest.pins.search_failed")
            logger.error("Failed to search pins", error=str(e))
            raise APIError(f"Failed to search pins: {e}")

    async def get_trending_searches(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get trending search terms on Pinterest
        
        Args:
            access_token: Pinterest access token
            
        Returns:
            List of trending search terms
        """
        try:
            response = await self._make_authenticated_request(
                "GET",
                "/search/partner/pins",
                access_token,
                params={"terms": "trending"}
            )
            
            trending = response.get("trending_searches", [])
            
            self.metrics.increment("pinterest.trends.retrieved")
            
            logger.info("Pinterest trending searches retrieved",
                       count=len(trending))
            
            return trending
            
        except Exception as e:
            self.metrics.increment("pinterest.trends.failed")
            logger.error("Failed to get trending searches", error=str(e))
            raise APIError(f"Failed to get trending searches: {e}")

    async def create_shopping_pin(self,
                                access_token: str,
                                board_id: str,
                                title: str,
                                media_url: str,
                                product_data: Dict[str, Any],
                                description: Optional[str] = None) -> PinterestPin:
        """
        Create a shopping pin with product information
        
        Args:
            access_token: Pinterest access token
            board_id: Board ID to add pin to
            title: Pin title
            media_url: Product image URL
            product_data: Product information (price, availability, etc.)
            description: Pin description
            
        Returns:
            Created shopping pin
        """
        try:
            pin_data = {
                "board_id": board_id,
                "title": title,
                "media_source": {
                    "source_type": "image_url",
                    "url": media_url
                },
                "pin_format": "product"
            }
            
            if description:
                pin_data["description"] = description
            
            # Add product-specific data
            if "price" in product_data:
                pin_data["product_rich_pin_data"] = {
                    "price": product_data["price"],
                    "currency": product_data.get("currency", "USD"),
                    "availability": product_data.get("availability", "in_stock")
                }
            
            response = await self._make_authenticated_request(
                "POST",
                "/pins",
                access_token,
                data=pin_data
            )
            
            pin_id = response["id"]
            
            pin = PinterestPin(
                id=pin_id,
                title=response["title"],
                description=response.get("description"),
                board_id=response.get("board_id", board_id),
                creator_id=response.get("creator", {}).get("id", ""),
                image_url=response.get("media", {}).get("url", media_url),
                pin_format=PinFormat.PRODUCT
            )
            
            # Store pin
            self._pins[pin_id] = pin
            
            self.metrics.increment("pinterest.shopping_pins.created")
            
            logger.info("Pinterest shopping pin created",
                       pin_id=pin_id,
                       title=title,
                       price=product_data.get("price"))
            
            return pin
            
        except Exception as e:
            self.metrics.increment("pinterest.shopping_pins.creation_failed")
            logger.error("Failed to create shopping pin", error=str(e))
            raise APIError(f"Failed to create shopping pin: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check Pinterest Business API integration health
        
        Returns:
            Health status information
        """
        try:
            health_status = {
                "service": "pinterest_business",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "config": {
                    "app_id": self.config.app_id[:8] + "...",
                    "api_version": self.config.api_version,
                    "scopes": len(self.config.scopes)
                },
                "metrics": {
                    "total_users": len(self._users),
                    "total_boards": len(self._boards),
                    "total_pins": len(self._pins)
                }
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "pinterest_business",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Factory function for easy integration setup
def create_pinterest_business_integration(
    app_id: str,
    app_secret: str,
    redirect_uri: str,
    **kwargs
) -> PinterestBusinessAPI:
    """
    Factory function to create Pinterest Business API integration
    
    Args:
        app_id: Pinterest application ID
        app_secret: Pinterest application secret
        redirect_uri: OAuth redirect URI
        **kwargs: Additional configuration options
        
    Returns:
        Configured Pinterest Business API integration instance
    """
    config = PinterestConfig(
        app_id=app_id,
        app_secret=app_secret,
        redirect_uri=redirect_uri,
        **kwargs
    )
    
    return PinterestBusinessAPI(config)

# Example usage for Ainflue platform
async def example_pinterest_business_flow() -> None:
    """Example Pinterest Business API integration usage"""
    
    # Initialize Pinterest Business API integration
    pinterest = create_pinterest_business_integration(
        app_id="your_pinterest_app_id",
        app_secret="your_pinterest_app_secret",
        redirect_uri="https://ainflue.com/auth/pinterest/callback",
        scopes=[
            PinterestScope.READ_PUBLIC,
            PinterestScope.WRITE_PUBLIC,
            PinterestScope.ADS_READ
        ]
    )
    
    try:
        # Generate authorization URL
        auth_url = await pinterest.get_authorization_url(
            state="creator_onboarding_123"
        )
        print(f"Authorization URL: {auth_url}")
        
        # After user authorization, exchange code for token
        # access_token_data = await pinterest.exchange_code_for_token("authorization_code")
        # access_token = access_token_data["access_token"]
        
        # For demo purposes, use placeholder token
        access_token = "demo_access_token"
        
        # Get user profile
        # user_profile = await pinterest.get_user_profile(access_token)
        # print(f"User: {user_profile.username}")
        
        # Create board
        # board = await pinterest.create_board(
        #     access_token=access_token,
        #     name="Ainflue Creations",
        #     description="Creative content from Ainflue platform",
        #     privacy=BoardPrivacy.PUBLIC
        # )
        # print(f"Board created: {board.name}")
        
        # Upload and create pin
        # with open("creative_content.jpg", "rb") as f:
        #     media_data = f.read()
        # 
        # media_url = await pinterest.upload_media(
        #     access_token=access_token,
        #     media_data=media_data,
        #     media_type="image/jpeg"
        # )
        # 
        # pin = await pinterest.create_pin(
        #     access_token=access_token,
        #     board_id=board.id,
        #     title="Amazing Content Created with Ainflue",
        #     media_url=media_url,
        #     description="Check out this stunning visual content created using Ainflue's AI tools!",
        #     link="https://ainflue.com",
        #     alt_text="Beautiful AI-generated visual content"
        # )
        # print(f"Pin created: {pin.title}")
        
        # Get pin analytics
        # analytics = await pinterest.get_pin_analytics(
        #     access_token=access_token,
        #     pin_id=pin.id
        # )
        # print(f"Pin analytics: {analytics.impressions} impressions, {analytics.saves} saves")
        
        # Search for trending content
        # trending = await pinterest.get_trending_searches(access_token)
        # print(f"Trending searches: {len(trending)} trends")
        
        # Health check
        health = await pinterest.health_check()
        print(f"Pinterest Business API health: {health['status']}")
        
    except Exception as e:
        print(f"Pinterest Business API integration error: {e}")

if __name__ == "__main__":
    asyncio.run(example_pinterest_business_flow())