"""TikTok Creator API Integration
=============================

Complete TikTok for Developers API integration for content management and analytics.
Handles video uploads, user data, analytics, and creator tools.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlencode
import mimetypes
import os

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class TikTokVideo:
    """TikTok video information"""    video_id: str
    title: str
    description: str
    create_time: datetime
    duration: int  # in seconds
    cover_image_url: str
    share_url: str
    embed_html: str = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    download_count: int = 0
    hashtags: List[str] = None
    music_id: str = None
    effect_ids: List[str] = None


@dataclass
class TikTokUser:
    """TikTok user information"""    open_id: str
    union_id: str
    username: str
    display_name: str
    avatar_url: str
    avatar_large_url: str
    bio_description: str = None
    profile_deep_link: str = None
    is_verified: bool = False
    follower_count: int = 0
    following_count: int = 0
    likes_count: int = 0
    video_count: int = 0


@dataclass
class TikTokAnalytics:
    """TikTok analytics data"""    date_range: Dict[str, str]  # {"start": "20240101", "end": "20240131"}
    profile_views: int = 0
    video_views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    followers_count: int = 0
    video_count: int = 0


class TikTokCreatorAPI:
    """TikTok for Developers API integration"""    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://open-api.tiktok.com"
        
    async def __aenter__(self):
        """Async context manager entry"""        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""        if self.session:
            await self.session.close()
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        tokens: OAuthTokens,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("tiktok", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("tiktok", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{self.base_url}/{endpoint}/"
        headers = {
            "Authorization": f"Bearer {tokens.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    await self.rate_limiter.record_request("tiktok", endpoint, None, response.status)
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        raise Exception("Rate limit exceeded")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                if files:
                    # Multipart upload
                    form_data = aiohttp.FormData()
                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, json.dumps(value) if isinstance(value, dict) else str(value))
                    for key, file_info in files.items():
                        form_data.add_field(key, file_info["content"], filename=file_info["filename"])
                    
                    # Remove Content-Type header for multipart uploads
                    upload_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
                    
                    async with self.session.post(url, data=form_data, headers=upload_headers, params=params) as response:
                        await self.rate_limiter.record_request("tiktok", endpoint, None, response.status)
                        
                        if response.status in [200, 201]:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"Upload failed: {response.status} - {error_text}")
                else:
                    # JSON request
                    async with self.session.post(url, json=data, headers=headers, params=params) as response:
                        await self.rate_limiter.record_request("tiktok", endpoint, None, response.status)
                        
                        if response.status in [200, 201]:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"API request failed: {response.status} - {error_text}")
                            
        except Exception as e:
            logger.error(f"TikTok API request failed: {e}")
            raise
            
    async def get_user_info(self, tokens: OAuthTokens, fields: Optional[List[str]] = None) -> TikTokUser:
        """Get TikTok user information"""        
        default_fields = [
            "open_id", "union_id", "username", "display_name", "avatar_url",
            "avatar_large_url", "bio_description", "profile_deep_link", "is_verified",
            "follower_count", "following_count", "likes_count", "video_count"
        ]
        
        params = {
            "fields": ",".join(fields or default_fields)
        }
        
        response = await self._make_request("GET", "user/info", tokens, params=params)
        
        if response.get("error"):
            raise Exception(f"TikTok API error: {response['error']}")
            
        user_data = response.get("data", {}).get("user", {})
        
        user = TikTokUser(
            open_id=user_data.get("open_id", ""),
            union_id=user_data.get("union_id", ""),
            username=user_data.get("username", ""),
            display_name=user_data.get("display_name", ""),
            avatar_url=user_data.get("avatar_url", ""),
            avatar_large_url=user_data.get("avatar_large_url", ""),
            bio_description=user_data.get("bio_description", ""),
            profile_deep_link=user_data.get("profile_deep_link", ""),
            is_verified=user_data.get("is_verified", False),
            follower_count=user_data.get("follower_count", 0),
            following_count=user_data.get("following_count", 0),
            likes_count=user_data.get("likes_count", 0),
            video_count=user_data.get("video_count", 0)
        )
        
        return user
        
    async def get_video_list(
        self,
        tokens: OAuthTokens,
        cursor: Optional[str] = None,
        max_count: int = 20,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get list of user's videos"""        
        default_fields = [
            "id", "title", "video_description", "create_time", "duration",
            "cover_image_url", "share_url", "view_count", "like_count",
            "comment_count", "share_count", "download_count"
        ]
        
        params = {
            "max_count": min(max_count, 20),
            "fields": ",".join(fields or default_fields)
        }
        
        if cursor:
            params["cursor"] = cursor
            
        response = await self._make_request("GET", "video/list", tokens, params=params)
        
        if response.get("error"):
            raise Exception(f"TikTok API error: {response['error']}")
            
        return response.get("data", {})
        
    async def get_video_info(
        self,
        tokens: OAuthTokens,
        video_ids: Union[str, List[str]],
        fields: Optional[List[str]] = None
    ) -> List[TikTokVideo]:
        """Get information about specific videos"""        
        if isinstance(video_ids, str):
            video_ids = [video_ids]
            
        default_fields = [
            "id", "title", "video_description", "create_time", "duration",
            "cover_image_url", "share_url", "embed_html", "view_count",
            "like_count", "comment_count", "share_count", "download_count"
        ]
        
        data = {
            "video_ids": video_ids,
            "fields": ",".join(fields or default_fields)
        }
        
        response = await self._make_request("POST", "video/query", tokens, data=data)
        
        if response.get("error"):
            raise Exception(f"TikTok API error: {response['error']}")
            
        videos = []
        for video_data in response.get("data", {}).get("videos", []):
            video = TikTokVideo(
                video_id=video_data.get("id", ""),
                title=video_data.get("title", ""),
                description=video_data.get("video_description", ""),
                create_time=datetime.fromtimestamp(video_data.get("create_time", 0)),
                duration=video_data.get("duration", 0),
                cover_image_url=video_data.get("cover_image_url", ""),
                share_url=video_data.get("share_url", ""),
                embed_html=video_data.get("embed_html", ""),
                view_count=video_data.get("view_count", 0),
                like_count=video_data.get("like_count", 0),
                comment_count=video_data.get("comment_count", 0),
                share_count=video_data.get("share_count", 0),
                download_count=video_data.get("download_count", 0)
            )
            videos.append(video)
            
        return videos
        
    async def upload_video(
        self,
        tokens: OAuthTokens,
        video_file_path: str,
        title: str,
        description: Optional[str] = None,
        privacy_level: str = "SELF_ONLY",  # "PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"
        disable_duet: bool = False,
        disable_comment: bool = False,
        disable_stitch: bool = False,
        video_cover_timestamp_ms: Optional[int] = None
    ) -> str:
        """Upload a video to TikTok"""        
        # Step 1: Initialize upload
        init_data = {
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": os.path.getsize(video_file_path)
            }
        }
        
        if description:
            init_data["post_info"]["description"] = description
        if video_cover_timestamp_ms:
            init_data["post_info"]["video_cover_timestamp_ms"] = video_cover_timestamp_ms
            
        init_response = await self._make_request("POST", "video/init", tokens, data=init_data)
        
        if init_response.get("error"):
            raise Exception(f"Upload initialization failed: {init_response['error']}")
            
        upload_url = init_response.get("data", {}).get("upload_url")
        publish_id = init_response.get("data", {}).get("publish_id")
        
        if not upload_url or not publish_id:
            raise Exception("Failed to get upload URL or publish ID")
            
        # Step 2: Upload video file
        if not os.path.exists(video_file_path):
            raise FileNotFoundError(f"Video file not found: {video_file_path}")
            
        with open(video_file_path, "rb") as video_file:
            video_content = video_file.read()
            
        files = {
            "video": {
                "content": video_content,
                "filename": os.path.basename(video_file_path)
            }
        }
        
        upload_response = await self._make_request("POST", "video/upload", tokens, files=files)
        
        if upload_response.get("error"):
            raise Exception(f"Video upload failed: {upload_response['error']}")
            
        # Step 3: Publish video
        publish_data = {"publish_id": publish_id}
        
        publish_response = await self._make_request("POST", "video/publish", tokens, data=publish_data)
        
        if publish_response.get("error"):
            raise Exception(f"Video publish failed: {publish_response['error']}")
            
        video_id = publish_response.get("data", {}).get("video_id")
        
        if not video_id:
            raise Exception("Failed to get video ID after publishing")
            
        logger.info(f"Successfully uploaded TikTok video: {video_id}")
        return video_id
        
    async def get_video_comments(
        self,
        tokens: OAuthTokens,
        video_id: str,
        cursor: Optional[str] = None,
        count: int = 20
    ) -> Dict[str, Any]:
        """Get comments for a specific video"""        
        params = {
            "video_id": video_id,
            "count": min(count, 50)
        }
        
        if cursor:
            params["cursor"] = cursor
            
        response = await self._make_request("GET", "video/comment/list", tokens, params=params)
        
        if response.get("error"):
            raise Exception(f"TikTok API error: {response['error']}")
            
        return response.get("data", {})
        
    async def reply_to_comment(
        self,
        tokens: OAuthTokens,
        video_id: str,
        comment_id: str,
        text: str
    ) -> str:
        """Reply to a comment on a video"""        
        data = {
            "video_id": video_id,
            "comment_id": comment_id,
            "text": text
        }
        
        response = await self._make_request("POST", "video/comment/reply", tokens, data=data)
        
        if response.get("error"):
            raise Exception(f"Comment reply failed: {response['error']}")
            
        reply_id = response.get("data", {}).get("comment_id")
        
        if reply_id:
            logger.info(f"Successfully replied to comment: {reply_id}")
            
        return reply_id or ""
        
    async def research_hashtag(self, tokens: OAuthTokens, hashtag_name: str) -> Dict[str, Any]:
        """Research hashtag performance and trends"""        
        params = {"hashtag_name": hashtag_name}
        
        response = await self._make_request("GET", "research/hashtag/info", tokens, params=params)
        
        if response.get("error"):
            raise Exception(f"Hashtag research failed: {response['error']}")
            
        return response.get("data", {})
        
    async def get_trending_hashtags(
        self,
        tokens: OAuthTokens,
        region: str = "US",
        count: int = 20
    ) -> List[Dict[str, Any]]:
        """Get trending hashtags for a region"""        
        params = {
            "region": region,
            "count": min(count, 50)
        }
        
        response = await self._make_request("GET", "research/hashtag/trending", tokens, params=params)
        
        if response.get("error"):
            raise Exception(f"Trending hashtags request failed: {response['error']}")
            
        return response.get("data", {}).get("hashtags", [])
        
    async def get_creator_insights(
        self,
        tokens: OAuthTokens,
        date_range: int = 7  # Last N days
    ) -> TikTokAnalytics:
        """Get creator insights and analytics"""        
        params = {"date_range": date_range}
        
        response = await self._make_request("GET", "creator/insights", tokens, params=params)
        
        if response.get("error"):
            raise Exception(f"Creator insights request failed: {response['error']}")
            
        insights_data = response.get("data", {})
        
        analytics = TikTokAnalytics(
            date_range={
                "start": (datetime.now() - timedelta(days=date_range)).strftime("%Y%m%d"),
                "end": datetime.now().strftime("%Y%m%d")
            },
            profile_views=insights_data.get("profile_views", 0),
            video_views=insights_data.get("video_views", 0),
            likes=insights_data.get("likes", 0),
            comments=insights_data.get("comments", 0),
            shares=insights_data.get("shares", 0),
            followers_count=insights_data.get("followers_count", 0),
            video_count=insights_data.get("video_count", 0)
        )
        
        return analytics
        
    async def search_videos(
        self,
        tokens: OAuthTokens,
        query: str,
        cursor: Optional[str] = None,
        search_id: Optional[str] = None,
        count: int = 20
    ) -> Dict[str, Any]:
        """Search for videos by keyword"""        
        params = {
            "query": query,
            "count": min(count, 20)
        }
        
        if cursor:
            params["cursor"] = cursor
        if search_id:
            params["search_id"] = search_id
            
        response = await self._make_request("GET", "research/video/query", tokens, params=params)
        
        if response.get("error"):
            raise Exception(f"Video search failed: {response['error']}")
            
        return response.get("data", {})
        
    async def get_video_analytics(
        self,
        tokens: OAuthTokens,
        video_ids: Union[str, List[str]],
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get analytics for specific videos"""        
        if isinstance(video_ids, str):
            video_ids = [video_ids]
            
        default_fields = [
            "id", "view_count", "like_count", "comment_count", "share_count",
            "download_count", "play_count", "profile_view_count"
        ]
        
        data = {
            "video_ids": video_ids,
            "fields": ",".join(fields or default_fields)
        }
        
        response = await self._make_request("POST", "video/analytics", tokens, data=data)
        
        if response.get("error"):
            raise Exception(f"Video analytics request failed: {response['error']}")
            
        return response.get("data", {}).get("videos", [])
        
    async def delete_video(self, tokens: OAuthTokens, video_id: str) -> bool:
        """Delete a video"""        
        data = {"video_id": video_id}
        
        try:
            response = await self._make_request("POST", "video/delete", tokens, data=data)
            
            if response.get("error"):
                logger.error(f"Failed to delete video {video_id}: {response['error']}")
                return False
                
            logger.info(f"Successfully deleted video: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete video {video_id}: {e}")
            return False
            
    async def get_share_insights(
        self,
        tokens: OAuthTokens,
        video_id: str
    ) -> Dict[str, Any]:
        """Get detailed sharing insights for a video"""        
        params = {"video_id": video_id}
        
        response = await self._make_request("GET", "video/share/insights", tokens, params=params)
        
        if response.get("error"):
            raise Exception(f"Share insights request failed: {response['error']}")
            
        return response.get("data", {})