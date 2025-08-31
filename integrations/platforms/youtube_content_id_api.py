"""YouTube Content ID API Integration
==================================

Complete YouTube Content ID API integration for content protection and monetization.
Handles content uploads, claims, analytics, and rights management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from urllib.parse import urlencode
import mimetypes
import os

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class YouTubeVideo:
    """YouTube video information"""    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration: str
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    tags: List[str] = None
    category_id: str = None
    privacy_status: str = "private"
    thumbnail_url: str = None


@dataclass
class ContentClaim:
    """YouTube Content ID claim information"""    claim_id: str
    video_id: str
    claimant: str
    claim_type: str  # "audiovisual", "audio", "visual"
    policy: str  # "monetize", "track", "block"
    status: str  # "active", "disputed", "released"
    created_at: datetime
    time_ranges: List[Dict[str, float]] = None  # [{"start": 0.0, "end": 30.0}]
    asset_id: str = None
    dispute_reason: str = None


@dataclass
class YouTubeAnalytics:
    """YouTube analytics data"""    video_id: str
    channel_id: str
    date_range: Dict[str, str]  # {"start": "2024-01-01", "end": "2024-01-31"}
    views: int = 0
    watch_time_minutes: int = 0
    estimated_revenue: float = 0.0
    impressions: int = 0
    click_through_rate: float = 0.0
    average_view_duration: float = 0.0
    subscriber_gain: int = 0
    likes: int = 0
    dislikes: int = 0
    comments: int = 0
    shares: int = 0


class YouTubeContentIDAPI:
    """YouTube Content ID API integration"""    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3"
        self.analytics_url = "https://youtubeanalytics.googleapis.com/v2"
        
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
        files: Optional[Dict[str, Any]] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("youtube", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("youtube", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{base_url or self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"{tokens.token_type} {tokens.access_token}",
            "Accept": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    await self.rate_limiter.record_request("youtube", endpoint, None, response.status)
                    
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
                    
                    async with self.session.post(url, data=form_data, headers=headers, params=params) as response:
                        await self.rate_limiter.record_request("youtube", endpoint, None, response.status)
                        
                        if response.status in [200, 201]:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"Upload failed: {response.status} - {error_text}")
                else:
                    # JSON request
                    headers["Content-Type"] = "application/json"
                    async with self.session.post(url, json=data, headers=headers, params=params) as response:
                        await self.rate_limiter.record_request("youtube", endpoint, None, response.status)
                        
                        if response.status in [200, 201]:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"API request failed: {response.status} - {error_text}")
                            
            elif method.upper() in ["PUT", "PATCH", "DELETE"]:
                async with self.session.request(
                    method, url, json=data, headers=headers, params=params
                ) as response:
                    await self.rate_limiter.record_request("youtube", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"YouTube API request failed: {e}")
            raise
            
    async def get_channel_info(self, tokens: OAuthTokens, channel_id: str = "mine") -> Dict[str, Any]:
        """Get channel information"""        params = {
            "part": "snippet,statistics,brandingSettings,status",
            "id": channel_id if channel_id != "mine" else None
        }
        
        if channel_id == "mine":
            params["mine"] = "true"
            del params["id"]
            
        return await self._make_request("GET", "channels", tokens, params=params)
        
    async def search_videos(
        self,
        tokens: OAuthTokens,
        query: str,
        max_results: int = 50,
        order: str = "relevance",
        published_after: Optional[datetime] = None,
        published_before: Optional[datetime] = None
    ) -> List[YouTubeVideo]:
        """Search for videos"""        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results, 50),
            "order": order
        }
        
        if published_after:
            params["publishedAfter"] = published_after.isoformat() + "Z"
        if published_before:
            params["publishedBefore"] = published_before.isoformat() + "Z"
            
        response = await self._make_request("GET", "search", tokens, params=params)
        
        videos = []
        for item in response.get("items", []):
            video = YouTubeVideo(
                video_id=item["id"]["videoId"],
                title=item["snippet"]["title"],
                description=item["snippet"]["description"],
                channel_id=item["snippet"]["channelId"],
                channel_title=item["snippet"]["channelTitle"],
                published_at=datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00")),
                duration="",  # Need separate API call for duration
                tags=item["snippet"].get("tags", []),
                thumbnail_url=item["snippet"]["thumbnails"]["default"]["url"]
            )
            videos.append(video)
            
        return videos
        
    async def get_video_details(self, tokens: OAuthTokens, video_ids: Union[str, List[str]]) -> List[YouTubeVideo]:
        """Get detailed video information"""        if isinstance(video_ids, str):
            video_ids = [video_ids]
            
        params = {
            "part": "snippet,statistics,contentDetails,status",
            "id": ",".join(video_ids)
        }
        
        response = await self._make_request("GET", "videos", tokens, params=params)
        
        videos = []
        for item in response.get("items", []):
            video = YouTubeVideo(
                video_id=item["id"],
                title=item["snippet"]["title"],
                description=item["snippet"]["description"],
                channel_id=item["snippet"]["channelId"],
                channel_title=item["snippet"]["channelTitle"],
                published_at=datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00")),
                duration=item["contentDetails"]["duration"],
                view_count=int(item["statistics"].get("viewCount", 0)),
                like_count=int(item["statistics"].get("likeCount", 0)),
                comment_count=int(item["statistics"].get("commentCount", 0)),
                tags=item["snippet"].get("tags", []),
                category_id=item["snippet"].get("categoryId"),
                privacy_status=item["status"]["privacyStatus"],
                thumbnail_url=item["snippet"]["thumbnails"]["default"]["url"]
            )
            videos.append(video)
            
        return videos
        
    async def upload_video(
        self,
        tokens: OAuthTokens,
        video_file_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "private"
    ) -> YouTubeVideo:
        """Upload a video to YouTube"""        
        # Prepare video metadata
        snippet = {
            "title": title,
            "description": description,
            "categoryId": category_id
        }
        
        if tags:
            snippet["tags"] = tags
            
        video_metadata = {
            "snippet": snippet,
            "status": {
                "privacyStatus": privacy_status
            }
        }
        
        # Read video file
        if not os.path.exists(video_file_path):
            raise FileNotFoundError(f"Video file not found: {video_file_path}")
            
        file_size = os.path.getsize(video_file_path)
        if file_size > 137438953472:  # 128GB limit
            raise ValueError("Video file too large (max 128GB)")
            
        with open(video_file_path, "rb") as video_file:
            video_content = video_file.read()
            
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(video_file_path)
        if not mime_type or not mime_type.startswith("video/"):
            mime_type = "video/mp4"  # Default fallback
            
        files = {
            "media": {
                "content": video_content,
                "filename": os.path.basename(video_file_path)
            }
        }
        
        params = {
            "part": "snippet,status",
            "uploadType": "multipart"
        }
        
        response = await self._make_request(
            "POST", "videos", tokens,
            params=params,
            data={"resource": video_metadata},
            files=files,
            base_url=self.upload_url
        )
        
        item = response
        video = YouTubeVideo(
            video_id=item["id"],
            title=item["snippet"]["title"],
            description=item["snippet"]["description"],
            channel_id=item["snippet"]["channelId"],
            channel_title=item["snippet"]["channelTitle"],
            published_at=datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00")),
            duration="",
            privacy_status=item["status"]["privacyStatus"],
            tags=item["snippet"].get("tags", []),
            category_id=item["snippet"].get("categoryId")
        )
        
        logger.info(f"Successfully uploaded video: {video.video_id}")
        return video
        
    async def get_analytics(
        self,
        tokens: OAuthTokens,
        channel_id: str,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        filters: Optional[str] = None
    ) -> YouTubeAnalytics:
        """Get YouTube Analytics data"""        
        default_metrics = [
            "views", "estimatedMinutesWatched", "estimatedRevenue",
            "impressions", "impressionCtrPercent", "averageViewDuration",
            "subscribersGained", "likes", "dislikes", "comments", "shares"
        ]
        
        params = {
            "ids": f"channel=={channel_id}",
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "metrics": ",".join(metrics or default_metrics)
        }
        
        if dimensions:
            params["dimensions"] = ",".join(dimensions)
        if filters:
            params["filters"] = filters
            
        response = await self._make_request(
            "GET", "reports", tokens, params=params, base_url=self.analytics_url
        )
        
        # Process analytics data
        rows = response.get("rows", [])
        if not rows:
            return YouTubeAnalytics(
                video_id="",
                channel_id=channel_id,
                date_range={"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")}
            )
            
        # Sum up all metrics across the date range
        totals = [0] * len(response.get("columnHeaders", []))
        for row in rows:
            for i, value in enumerate(row):
                if isinstance(value, (int, float)):
                    totals[i] += value
                    
        # Map to analytics object
        analytics = YouTubeAnalytics(
            video_id="",
            channel_id=channel_id,
            date_range={"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")},
            views=int(totals[0]) if len(totals) > 0 else 0,
            watch_time_minutes=int(totals[1]) if len(totals) > 1 else 0,
            estimated_revenue=float(totals[2]) if len(totals) > 2 else 0.0,
            impressions=int(totals[3]) if len(totals) > 3 else 0,
            click_through_rate=float(totals[4]) if len(totals) > 4 else 0.0,
            average_view_duration=float(totals[5]) if len(totals) > 5 else 0.0,
            subscriber_gain=int(totals[6]) if len(totals) > 6 else 0,
            likes=int(totals[7]) if len(totals) > 7 else 0,
            dislikes=int(totals[8]) if len(totals) > 8 else 0,
            comments=int(totals[9]) if len(totals) > 9 else 0,
            shares=int(totals[10]) if len(totals) > 10 else 0
        )
        
        return analytics
        
    async def create_content_claim(
        self,
        tokens: OAuthTokens,
        video_id: str,
        asset_id: str,
        claim_type: str = "audiovisual",
        policy: str = "monetize",
        time_ranges: Optional[List[Dict[str, float]]] = None
    ) -> ContentClaim:
        """Create a Content ID claim (requires Content ID access)"""        
        claim_data = {
            "videoId": video_id,
            "assetId": asset_id,
            "contentType": claim_type,
            "policy": policy
        }
        
        if time_ranges:
            claim_data["timeRanges"] = time_ranges
            
        # Note: This endpoint requires special Content ID API access
        # This is a placeholder implementation
        response = await self._make_request(
            "POST", "claims", tokens, data=claim_data
        )
        
        claim = ContentClaim(
            claim_id=response.get("id", ""),
            video_id=video_id,
            claimant=response.get("claimant", ""),
            claim_type=claim_type,
            policy=policy,
            status=response.get("status", "active"),
            created_at=datetime.now(),
            time_ranges=time_ranges,
            asset_id=asset_id
        )
        
        logger.info(f"Created Content ID claim: {claim.claim_id}")
        return claim
        
    async def get_content_claims(
        self,
        tokens: OAuthTokens,
        video_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ContentClaim]:
        """Get Content ID claims"""        
        params = {}
        if video_id:
            params["videoId"] = video_id
        if status:
            params["status"] = status
            
        # Note: This endpoint requires special Content ID API access
        response = await self._make_request("GET", "claims", tokens, params=params)
        
        claims = []
        for item in response.get("items", []):
            claim = ContentClaim(
                claim_id=item.get("id", ""),
                video_id=item.get("videoId", ""),
                claimant=item.get("claimant", ""),
                claim_type=item.get("contentType", ""),
                policy=item.get("policy", ""),
                status=item.get("status", ""),
                created_at=datetime.fromisoformat(item.get("timeCreated", datetime.now().isoformat())),
                asset_id=item.get("assetId", "")
            )
            claims.append(claim)
            
        return claims
        
    async def update_video(
        self,
        tokens: OAuthTokens,
        video_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        privacy_status: Optional[str] = None
    ) -> YouTubeVideo:
        """Update video metadata"""        
        # First get current video data
        current_videos = await self.get_video_details(tokens, video_id)
        if not current_videos:
            raise ValueError(f"Video not found: {video_id}")
            
        current_video = current_videos[0]
        
        # Build update data
        snippet = {
            "title": title or current_video.title,
            "description": description or current_video.description,
            "categoryId": current_video.category_id
        }
        
        if tags is not None:
            snippet["tags"] = tags
        elif current_video.tags:
            snippet["tags"] = current_video.tags
            
        update_data = {
            "id": video_id,
            "snippet": snippet
        }
        
        if privacy_status:
            update_data["status"] = {"privacyStatus": privacy_status}
            
        params = {"part": "snippet,status"}
        
        response = await self._make_request("PUT", "videos", tokens, params=params, data=update_data)
        
        # Return updated video info
        return await self.get_video_details(tokens, video_id)
        
    async def delete_video(self, tokens: OAuthTokens, video_id: str) -> bool:
        """Delete a video"""        params = {"id": video_id}
        
        try:
            await self._make_request("DELETE", "videos", tokens, params=params)
            logger.info(f"Successfully deleted video: {video_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete video {video_id}: {e}")
            return False