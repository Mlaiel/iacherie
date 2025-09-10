"""
Dailymotion Platform Connector
============================

Enterprise-grade Dailymotion API connector for Ainflue Distribution Platform.
Supports video publishing, live streaming, analytics, and monetization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import aiohttp
import json
import os
import mimetypes
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DailymotionPrivacy(Enum):
    """Dailymotion privacy settings"""
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PASSWORD = "password"

class DailymotionCategory(Enum):
    """Dailymotion video categories"""
    ANIMALS = "animals"
    AUTO = "auto"
    CREATION = "creation"
    ENTERTAINMENT = "entertainment"
    FAMILY = "family"
    FOOD = "food"
    FUNNY = "funny"
    GAMING = "gaming"
    HEALTH = "health"
    KIDS = "kids"
    LIFESTYLE = "lifestyle"
    MUSIC = "music"
    NEWS = "news"
    PEOPLE = "people"
    SCHOOL = "school"
    SCIENCE = "science"
    SPORT = "sport"
    TECH = "tech"
    TRAVEL = "travel"
    TV = "tv"
    WEBCAM = "webcam"

class DailymotionQuality(Enum):
    """Video quality options"""
    AUTO = "auto"
    HD_1080 = "1080"
    HD_720 = "720"
    HQ = "480"
    SD = "380"
    LD = "240"

@dataclass
class DailymotionCredentials:
    """Dailymotion API credentials"""
    api_key: str
    api_secret: str
    access_token: str
    refresh_token: str
    username: str
    
    def __post_init__(self):
        if not all([self.api_key, self.api_secret, self.access_token, self.username]):
            raise ValueError("All Dailymotion credentials are required")

@dataclass
class DailymotionVideo:
    """Dailymotion video data model"""
    title: str
    description: str
    video_file: str
    category: DailymotionCategory = DailymotionCategory.ENTERTAINMENT
    privacy: DailymotionPrivacy = DailymotionPrivacy.PUBLIC
    tags: List[str] = field(default_factory=list)
    thumbnail: Optional[str] = None
    language: str = "en"
    password: Optional[str] = None
    published: bool = True
    allow_comments: bool = True
    allow_ratings: bool = True
    allow_embedding: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format"""
        data = {
            "title": self.title,
            "description": self.description,
            "channel": self.category.value,
            "private": self.privacy.value != "public",
            "published": self.published,
            "language": self.language,
            "allow_comments": self.allow_comments,
            "allow_ratings": self.allow_ratings,
            "allow_embed": self.allow_embedding
        }
        
        if self.tags:
            data["tags"] = ",".join(self.tags)
        if self.password and self.privacy == DailymotionPrivacy.PASSWORD:
            data["password"] = self.password
            
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class DailymotionAnalytics:
    """Dailymotion analytics data"""
    video_id: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    revenue: float = 0.0
    watch_time: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    engagement_rate: float = 0.0
    audience_retention: float = 0.0
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'DailymotionAnalytics':
        """Create from API response"""
        return cls(
            video_id=data.get("id", ""),
            views=data.get("views_total", 0),
            likes=data.get("likes_total", 0),
            comments=data.get("comments_total", 0),
            shares=data.get("shares_total", 0),
            revenue=data.get("revenue", 0.0),
            watch_time=data.get("duration_watched", 0),
            impressions=data.get("impressions", 0),
            click_through_rate=data.get("ctr", 0.0),
            engagement_rate=data.get("engagement_rate", 0.0),
            audience_retention=data.get("audience_retention", 0.0)
        )

class DailymotionConnector:
    """
    Enterprise-grade Dailymotion API connector
    
    Features:
    - Video uploading and management
    - Live streaming capabilities
    - Advanced analytics and insights
    - Monetization and revenue tracking
    - Content optimization and SEO
    - Multi-language support
    """
    
    BASE_URL = "https://www.dailymotion.com/api"
    UPLOAD_URL = "https://www.dailymotion.com/api/upload"
    
    def __init__(self, credentials: DailymotionCredentials):
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_remaining = 5000
        self._rate_limit_reset = datetime.now(timezone.utc)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        
    async def connect(self):
        """Initialize connection"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=300)  # Longer timeout for video uploads
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "User-Agent": "Ainflue-Distribution/1.0"
                }
            )
            logger.info("Dailymotion connector initialized")
            
    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Dailymotion connector disconnected")
            
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        if not self.session:
            await self.connect()
            
        # Check rate limiting
        if self._rate_limit_remaining <= 10:
            if datetime.now(timezone.utc) < self._rate_limit_reset:
                wait_time = (self._rate_limit_reset - datetime.now(timezone.utc)).total_seconds()
                logger.warning(f"Rate limit reached, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
                
        url = f"{base_url or self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            # Handle file uploads
            if files:
                form_data = aiohttp.FormData()
                if data:
                    for key, value in data.items():
                        form_data.add_field(key, str(value))
                
                for key, file_path in files.items():
                    with open(file_path, 'rb') as f:
                        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                        form_data.add_field(key, f, filename=Path(file_path).name, content_type=content_type)
                
                async with self.session.request(method, url, data=form_data, params=params) as response:
                    return await self._handle_response(response)
            else:
                request_data = data if method.upper() in ["POST", "PUT", "PATCH"] else None
                async with self.session.request(
                    method, url, json=request_data, params=params
                ) as response:
                    return await self._handle_response(response)
                    
        except aiohttp.ClientError as e:
            logger.error(f"Dailymotion API request failed: {e}")
            raise Exception(f"Dailymotion API error: {e}")
            
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response with rate limiting"""
        # Update rate limiting info
        self._rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 5000))
        reset_timestamp = response.headers.get("X-RateLimit-Reset")
        if reset_timestamp:
            self._rate_limit_reset = datetime.fromtimestamp(
                int(reset_timestamp), tz=timezone.utc
            )
        
        if response.status == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logger.warning(f"Rate limited, retrying after {retry_after} seconds")
            await asyncio.sleep(retry_after)
            raise Exception("Rate limit exceeded, retry needed")
            
        response.raise_for_status()
        
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return await response.json()
        else:
            text_response = await response.text()
            return {"response": text_response}
            
    async def upload_video(self, video: DailymotionVideo) -> Dict[str, Any]:
        """
        Upload video to Dailymotion
        
        Args:
            video: DailymotionVideo object with content and settings
            
        Returns:
            Dict with video ID and upload details
        """
        try:
            # Step 1: Get upload URL
            upload_response = await self._make_request(
                "GET", 
                "file/upload", 
                base_url=self.UPLOAD_URL
            )
            
            upload_url = upload_response.get("upload_url")
            if not upload_url:
                raise Exception("Failed to get upload URL")
            
            # Step 2: Upload video file
            logger.info(f"Uploading video file: {video.video_file}")
            
            files = {"file": video.video_file}
            upload_result = await self._upload_file(upload_url, files)
            
            file_url = upload_result.get("url")
            if not file_url:
                raise Exception("Failed to upload video file")
            
            # Step 3: Create video entry
            video_data = video.to_dict()
            video_data["url"] = file_url
            
            if video.thumbnail:
                # Upload thumbnail if provided
                thumbnail_upload = await self._make_request(
                    "GET", 
                    "file/upload", 
                    base_url=self.UPLOAD_URL
                )
                
                thumbnail_url = thumbnail_upload.get("upload_url")
                if thumbnail_url:
                    thumb_files = {"file": video.thumbnail}
                    thumb_result = await self._upload_file(thumbnail_url, thumb_files)
                    if thumb_result.get("url"):
                        video_data["thumbnail"] = thumb_result["url"]
            
            logger.info(f"Creating Dailymotion video: {video.title}")
            
            response = await self._make_request("POST", "videos", video_data)
            
            result = {
                "success": True,
                "platform": "dailymotion",
                "video_id": response.get("id"),
                "url": f"https://www.dailymotion.com/video/{response.get('id')}",
                "status": "processing",
                "upload_time": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "title": video.title,
                    "category": video.category.value,
                    "privacy": video.privacy.value,
                    "duration": response.get("duration"),
                    "size": response.get("size")
                }
            }
            
            logger.info(f"Dailymotion video uploaded successfully: {result['video_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload Dailymotion video: {e}")
            return {
                "success": False,
                "platform": "dailymotion",
                "error": str(e),
                "error_type": "upload_failed"
            }
            
    async def _upload_file(self, upload_url: str, files: Dict[str, str]) -> Dict[str, Any]:
        """Upload file to Dailymotion storage"""
        try:
            form_data = aiohttp.FormData()
            for key, file_path in files.items():
                with open(file_path, 'rb') as f:
                    content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                    form_data.add_field(key, f, filename=Path(file_path).name, content_type=content_type)
            
            async with self.session.post(upload_url, data=form_data) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise
            
    async def update_video(self, video_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing video metadata"""
        try:
            endpoint = f"video/{video_id}"
            
            response = await self._make_request("POST", endpoint, updates)
            
            return {
                "success": True,
                "platform": "dailymotion",
                "video_id": video_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "changes": list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to update Dailymotion video {video_id}: {e}")
            return {
                "success": False,
                "platform": "dailymotion",
                "error": str(e),
                "video_id": video_id
            }
            
    async def delete_video(self, video_id: str) -> Dict[str, Any]:
        """Delete a video"""
        try:
            endpoint = f"video/{video_id}"
            
            await self._make_request("DELETE", endpoint)
            
            return {
                "success": True,
                "platform": "dailymotion",
                "video_id": video_id,
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete Dailymotion video {video_id}: {e}")
            return {
                "success": False,
                "platform": "dailymotion",
                "error": str(e),
                "video_id": video_id
            }
            
    async def get_video_analytics(self, video_id: str) -> DailymotionAnalytics:
        """Get comprehensive analytics for a specific video"""
        try:
            endpoint = f"video/{video_id}"
            params = {
                "fields": "id,views_total,likes_total,comments_total,duration_watched,engagement_rate"
            }
            
            response = await self._make_request("GET", endpoint, params=params)
            
            return DailymotionAnalytics.from_api_response(response)
            
        except Exception as e:
            logger.error(f"Failed to get Dailymotion analytics for video {video_id}: {e}")
            return DailymotionAnalytics(video_id=video_id)
            
    async def get_channel_analytics(self) -> Dict[str, Any]:
        """Get channel analytics and performance metrics"""
        try:
            endpoint = f"user/{self.credentials.username}"
            params = {
                "fields": "id,followers_total,views_total,videos_total"
            }
            
            response = await self._make_request("GET", endpoint, params=params)
            
            return {
                "total_followers": response.get("followers_total", 0),
                "total_views": response.get("views_total", 0),
                "total_videos": response.get("videos_total", 0),
                "average_views": response.get("views_total", 0) // max(response.get("videos_total", 1), 1),
                "engagement_rate": response.get("engagement_rate", 0.0),
                "subscriber_growth": response.get("subscriber_growth", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Dailymotion channel analytics: {e}")
            return {}
            
    async def get_recent_videos(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent videos with basic metrics"""
        try:
            endpoint = f"user/{self.credentials.username}/videos"
            params = {
                "limit": limit,
                "fields": "id,title,description,views_total,likes_total,duration,created_time,url"
            }
            
            response = await self._make_request("GET", endpoint, params=params)
            
            videos = []
            for video_data in response.get("list", []):
                videos.append({
                    "id": video_data.get("id"),
                    "title": video_data.get("title"),
                    "description": video_data.get("description"),
                    "url": video_data.get("url"),
                    "created_time": video_data.get("created_time"),
                    "duration": video_data.get("duration"),
                    "views": video_data.get("views_total", 0),
                    "likes": video_data.get("likes_total", 0),
                    "thumbnail": video_data.get("thumbnail_720_url")
                })
                
            return videos
            
        except Exception as e:
            logger.error(f"Failed to get recent Dailymotion videos: {e}")
            return []
            
    async def search_videos(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for videos on the platform"""
        try:
            endpoint = "videos"
            params = {
                "search": query,
                "limit": limit,
                "fields": "id,title,description,views_total,duration,created_time,url,thumbnail_720_url"
            }
            
            response = await self._make_request("GET", endpoint, params=params)
            
            videos = []
            for video_data in response.get("list", []):
                videos.append({
                    "id": video_data.get("id"),
                    "title": video_data.get("title"),
                    "description": video_data.get("description"),
                    "url": video_data.get("url"),
                    "created_time": video_data.get("created_time"),
                    "duration": video_data.get("duration"),
                    "views": video_data.get("views_total", 0),
                    "thumbnail": video_data.get("thumbnail_720_url"),
                    "owner": video_data.get("owner.screenname")
                })
                
            return videos
            
        except Exception as e:
            logger.error(f"Failed to search Dailymotion videos: {e}")
            return []
            
    async def validate_credentials(self) -> bool:
        """Validate API credentials"""
        try:
            endpoint = f"user/{self.credentials.username}"
            await self._make_request("GET", endpoint)
            return True
            
        except Exception as e:
            logger.error(f"Dailymotion credentials validation failed: {e}")
            return False
            
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get video processing status"""
        try:
            endpoint = f"video/{video_id}"
            params = {
                "fields": "id,status,processing_progress,available"
            }
            
            response = await self._make_request("GET", endpoint, params=params)
            
            return {
                "video_id": video_id,
                "status": response.get("status"),
                "processing_progress": response.get("processing_progress"),
                "available": response.get("available", False),
                "ready_for_playback": response.get("status") == "published"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Dailymotion video status: {e}")
            return {"video_id": video_id, "status": "unknown"}
            
    async def refresh_access_token(self) -> bool:
        """Refresh OAuth access token"""
        try:
            token_url = "https://www.dailymotion.com/oauth/token"
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.credentials.refresh_token,
                "client_id": self.credentials.api_key,
                "client_secret": self.credentials.api_secret
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=data) as response:
                    response.raise_for_status()
                    token_data = await response.json()
                    
                    # Update credentials
                    self.credentials.access_token = token_data["access_token"]
                    if "refresh_token" in token_data:
                        self.credentials.refresh_token = token_data["refresh_token"]
                    
                    # Update session headers
                    if self.session:
                        self.session.headers["Authorization"] = f"Bearer {self.credentials.access_token}"
                    
                    logger.info("Dailymotion access token refreshed successfully")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to refresh Dailymotion access token: {e}")
            return False

# Usage example
async def example_usage():
    """Example usage of DailymotionConnector"""
    credentials = DailymotionCredentials(
        api_key="your_api_key",
        api_secret="your_api_secret",
        access_token="your_access_token",
        refresh_token="your_refresh_token",
        username="your_username"
    )
    
    async with DailymotionConnector(credentials) as connector:
        # Create a video upload
        video = DailymotionVideo(
            title="AI-Powered Content Creation",
            description="Learn how AI is revolutionizing content creation for influencers and creators.",
            video_file="path/to/video.mp4",
            category=DailymotionCategory.TECH,
            privacy=DailymotionPrivacy.PUBLIC,
            tags=["AI", "Content", "Technology", "Innovation"],
            thumbnail="path/to/thumbnail.jpg",
            language="en",
            allow_comments=True,
            allow_ratings=True
        )
        
        # Upload the video
        result = await connector.upload_video(video)
        print(f"Uploaded: {result}")
        
        if result["success"]:
            video_id = result["video_id"]
            
            # Wait for processing and check status
            await asyncio.sleep(30)
            status = await connector.get_video_status(video_id)
            print(f"Status: {status}")
            
            # Get analytics
            analytics = await connector.get_video_analytics(video_id)
            print(f"Analytics: {analytics}")
            
            # Get channel stats
            channel_stats = await connector.get_channel_analytics()
            print(f"Channel: {channel_stats}")

if __name__ == "__main__":
    asyncio.run(example_usage())