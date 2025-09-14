"""Instagram Business API Integration
=================================

Complete Instagram Business API integration for content management and analytics.
Handles posts, stories, insights, and business account management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
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
class InstagramMedia:
    """
Instagram media information"""
    media_id: str
    media_type: str  # "IMAGE", "VIDEO", "CAROUSEL_ALBUM"
    caption: str
    permalink: str
    timestamp: datetime
    username: str
    like_count: int = 0
    comments_count: int = 0
    media_url: str = None
    thumbnail_url: str = None
    children: List[str] = None  # For carousel posts


@dataclass
class InstagramInsights:
    """Instagram insights data"""
    media_id: str
    period: str  # "day", "week", "days_28", "lifetime"
    impressions: int = 0
    reach: int = 0
    engagement: int = 0
    saves: int = 0
    video_views: int = 0
    profile_visits: int = 0
    website_clicks: int = 0
    email_contacts: int = 0
    phone_call_clicks: int = 0
    text_message_clicks: int = 0
    get_directions_clicks: int = 0


@dataclass
class InstagramUser:
    """Instagram user/business account information"""
    user_id: str
    username: str
    account_type: str  # "BUSINESS", "CREATOR", "PERSONAL"
    media_count: int = 0
    followers_count: int = 0
    follows_count: int = 0
    name: str = None
    biography: str = None
    website: str = None
    profile_picture_url: str = None


class InstagramBusinessAPI:
    """Instagram Business API integration"""
    
    def __init__(self, rate_limiter -> None: Optional[APIRateLimiter] = None) -> None:
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://graph.instagram.com"
        self.graph_url = "https://graph.facebook.com/v18.0"
        
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
Async context manager exit"""
        if self.session:
            await self.session.close()
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        tokens: OAuthTokens,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
Make authenticated API request with rate limiting"""
        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("instagram", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("instagram", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{base_url or self.base_url}/{endpoint}"
        
        # Add access token to params
        if not params:
            params = {}
        params["access_token"] = tokens.access_token
        
        headers = {"Accept": "application/json"}
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    await self.rate_limiter.record_request("instagram", endpoint, None, response.status)
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        raise Exception("Rate limit exceeded")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                headers["Content-Type"] = "application/json"
                async with self.session.post(url, json=data, headers=headers, params=params) as response:
                    await self.rate_limiter.record_request("instagram", endpoint, None, response.status)
                    
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() in ["PUT", "PATCH", "DELETE"]:
                async with self.session.request(
                    method, url, json=data, headers=headers, params=params
                ) as response:
                    await self.rate_limiter.record_request("instagram", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Instagram API request failed: {e}")
            raise
            
    async def get_user_info(self, tokens: OAuthTokens, user_id: str = "me") -> InstagramUser:
        """Get Instagram user/business account information"""
        fields = [
            "id", "username", "account_type", "media_count",
            "followers_count", "follows_count", "name", "biography",
            "website", "profile_picture_url"
        ]
        
        params = {"fields": ",".join(fields)}
        
        response = await self._make_request("GET", user_id, tokens, params=params)
        
        user = InstagramUser(
            user_id=response["id"],
            username=response["username"],
            account_type=response.get("account_type", "PERSONAL"),
            media_count=response.get("media_count", 0),
            followers_count=response.get("followers_count", 0),
            follows_count=response.get("follows_count", 0),
            name=response.get("name"),
            biography=response.get("biography"),
            website=response.get("website"),
            profile_picture_url=response.get("profile_picture_url")
        )
        
        return user
        
    async def get_media_list(
        self,
        tokens: OAuthTokens,
        user_id: str = "me",
        limit: int = 25,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[InstagramMedia]:
        """Get list of media posts"""
        fields = [
            "id", "media_type", "caption", "permalink", "timestamp",
            "username", "like_count", "comments_count", "media_url",
            "thumbnail_url", "children"
        ]
        
        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 100)
        }
        
        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())
            
        response = await self._make_request("GET", f"{user_id}/media", tokens, params=params)
        
        media_list = []
        for item in response.get("data", []):
            media = InstagramMedia(
                media_id=item["id"],
                media_type=item["media_type"],
                caption=item.get("caption", ""),
                permalink=item["permalink"],
                timestamp=datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")),
                username=item["username"],
                like_count=item.get("like_count", 0),
                comments_count=item.get("comments_count", 0),
                media_url=item.get("media_url"),
                thumbnail_url=item.get("thumbnail_url"),
                children=item.get("children", {}).get("data", []) if item.get("children") else None
            )
            media_list.append(media)
            
        return media_list
        
    async def get_media_details(self, tokens: OAuthTokens, media_id: str) -> InstagramMedia:
        """Get detailed information about specific media"""
        fields = [
            "id", "media_type", "caption", "permalink", "timestamp",
            "username", "like_count", "comments_count", "media_url",
            "thumbnail_url", "children"
        ]
        
        params = {"fields": ",".join(fields)}
        
        response = await self._make_request("GET", media_id, tokens, params=params)
        
        media = InstagramMedia(
            media_id=response["id"],
            media_type=response["media_type"],
            caption=response.get("caption", ""),
            permalink=response["permalink"],
            timestamp=datetime.fromisoformat(response["timestamp"].replace("Z", "+00:00")),
            username=response["username"],
            like_count=response.get("like_count", 0),
            comments_count=response.get("comments_count", 0),
            media_url=response.get("media_url"),
            thumbnail_url=response.get("thumbnail_url"),
            children=response.get("children", {}).get("data", []) if response.get("children") else None
        )
        
        return media
        
    async def get_media_insights(
        self,
        tokens: OAuthTokens,
        media_id: str,
        metric_names: Optional[List[str]] = None
    ) -> InstagramInsights:
        """Get insights for specific media"""
        
        # Default metrics based on media type
        default_metrics = [
            "impressions", "reach", "engagement", "saves"
        ]
        
        metrics = metric_names or default_metrics
        params = {"metric": ",".join(metrics)}
        
        response = await self._make_request("GET", f"{media_id}/insights", tokens, params=params)
        
        insights_data = {}
        for item in response.get("data", []):
            metric_name = item["name"]
            values = item.get("values", [])
            if values and len(values) > 0:
                insights_data[metric_name] = values[0].get("value", 0)
                
        insights = InstagramInsights(
            media_id=media_id,
            period="lifetime",
            impressions=insights_data.get("impressions", 0),
            reach=insights_data.get("reach", 0),
            engagement=insights_data.get("engagement", 0),
            saves=insights_data.get("saves", 0),
            video_views=insights_data.get("video_views", 0)
        )
        
        return insights
        
    async def get_account_insights(
        self,
        tokens: OAuthTokens,
        user_id: str = "me",
        period: str = "day",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        metric_names: Optional[List[str]] = None
    ) -> InstagramInsights:
        """Get account-level insights"""
        
        # Default account metrics
        default_metrics = [
            "impressions", "reach", "profile_views", "website_clicks",
            "email_contacts", "phone_call_clicks", "text_message_clicks",
            "get_directions_clicks"
        ]
        
        metrics = metric_names or default_metrics
        params = {
            "metric": ",".join(metrics),
            "period": period
        }
        
        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())
            
        response = await self._make_request("GET", f"{user_id}/insights", tokens, params=params)
        
        insights_data = {}
        for item in response.get("data", []):
            metric_name = item["name"]
            values = item.get("values", [])
            if values and len(values) > 0:
                # Sum up values if multiple periods
                total_value = sum(v.get("value", 0) for v in values if isinstance(v.get("value"), (int, float)))
                insights_data[metric_name] = total_value
                
        insights = InstagramInsights(
            media_id="",  # Account-level insights
            period=period,
            impressions=insights_data.get("impressions", 0),
            reach=insights_data.get("reach", 0),
            profile_visits=insights_data.get("profile_views", 0),
            website_clicks=insights_data.get("website_clicks", 0),
            email_contacts=insights_data.get("email_contacts", 0),
            phone_call_clicks=insights_data.get("phone_call_clicks", 0),
            text_message_clicks=insights_data.get("text_message_clicks", 0),
            get_directions_clicks=insights_data.get("get_directions_clicks", 0)
        )
        
        return insights
        
    async def create_media_container(
        self,
        tokens: OAuthTokens,
        user_id: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None,
        location_id: Optional[str] = None,
        user_tags: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Create a media container for publishing"""
        
        data = {
            "media_type": media_type.upper(),
            "media_url": media_url
        }
        
        if caption:
            data["caption"] = caption
        if location_id:
            data["location_id"] = location_id
        if user_tags:
            data["user_tags"] = json.dumps(user_tags)
            
        response = await self._make_request("POST", f"{user_id}/media", tokens, data=data)
        
        container_id = response.get("id")
        if not container_id:
            raise Exception("Failed to create media container")
            
        logger.info(f"Created media container: {container_id}")
        return container_id
        
    async def publish_media(self, tokens: OAuthTokens, user_id: str, creation_id: str) -> str:
        """Publish a media container"""
        
        data = {"creation_id": creation_id}
        
        response = await self._make_request("POST", f"{user_id}/media_publish", tokens, data=data)
        
        media_id = response.get("id")
        if not media_id:
            raise Exception("Failed to publish media")
            
        logger.info(f"Published media: {media_id}")
        return media_id
        
    async def create_carousel_container(
        self,
        tokens: OAuthTokens,
        user_id: str,
        children_containers: List[str],
        caption: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> str:
        """Create a carousel media container"""
        
        data = {
            "media_type": "CAROUSEL",
            "children": ",".join(children_containers)
        }
        
        if caption:
            data["caption"] = caption
        if location_id:
            data["location_id"] = location_id
            
        response = await self._make_request("POST", f"{user_id}/media", tokens, data=data)
        
        container_id = response.get("id")
        if not container_id:
            raise Exception("Failed to create carousel container")
            
        logger.info(f"Created carousel container: {container_id}")
        return container_id
        
    async def get_comments(
        self,
        tokens: OAuthTokens,
        media_id: str,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Get comments for specific media"""
        
        fields = ["id", "text", "timestamp", "username", "like_count"]
        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 100)
        }
        
        response = await self._make_request("GET", f"{media_id}/comments", tokens, params=params)
        
        return response.get("data", [])
        
    async def reply_to_comment(
        self,
        tokens: OAuthTokens,
        media_id: str,
        comment_text: str
    ) -> str:
        """Reply to a comment on media"""
        
        data = {"message": comment_text}
        
        response = await self._make_request("POST", f"{media_id}/comments", tokens, data=data)
        
        comment_id = response.get("id")
        if not comment_id:
            raise Exception("Failed to post comment")
            
        logger.info(f"Posted comment: {comment_id}")
        return comment_id
        
    async def hide_comment(self, tokens: OAuthTokens, comment_id: str) -> bool:
        """Hide a comment"""
        
        data = {"hide": True}
        
        try:
            await self._make_request("POST", comment_id, tokens, data=data)
            logger.info(f"Hidden comment: {comment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to hide comment {comment_id}: {e}")
            return False
            
    async def get_hashtag_info(self, tokens: OAuthTokens, hashtag_name: str) -> Dict[str, Any]:
        """Get information about a hashtag"""
        
        # First, search for the hashtag ID
        params = {"q": hashtag_name}
        
        response = await self._make_request("GET", "ig_hashtag_search", tokens, params=params)
        
        hashtag_data = response.get("data", [])
        if not hashtag_data:
            raise Exception(f"Hashtag not found: {hashtag_name}")
            
        hashtag_id = hashtag_data[0]["id"]
        
        # Get hashtag details
        fields = ["id", "name"]
        params = {"fields": ",".join(fields)}
        
        hashtag_info = await self._make_request("GET", hashtag_id, tokens, params=params)
        
        return hashtag_info
        
    async def get_hashtag_top_media(
        self,
        tokens: OAuthTokens,
        hashtag_id: str,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Get top media for a hashtag"""
        
        fields = ["id", "media_type", "caption", "permalink", "timestamp"]
        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 50)
        }
        
        response = await self._make_request("GET", f"{hashtag_id}/top_media", tokens, params=params)
        
        return response.get("data", [])
        
    async def get_business_discovery(
        self,
        tokens: OAuthTokens,
        business_account_id: str,
        target_username: str
    ) -> Dict[str, Any]:
        """Get public information about another business account"""
        
        fields = [
            "biography", "id", "ig_id", "followers_count", "follows_count",
            "media_count", "name", "profile_picture_url", "username", "website"
        ]
        
        params = {
            "fields": f"business_discovery.username({target_username}){{{','.join(fields)}}}"
        }
        
        response = await self._make_request("GET", business_account_id, tokens, params=params)
        
        return response.get("business_discovery", {})
        
    async def get_mentioned_media(
        self,
        tokens: OAuthTokens,
        user_id: str = "me",
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Get media where the account is mentioned"""
        
        fields = ["id", "media_type", "caption", "permalink", "timestamp"]
        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 100)
        }
        
        response = await self._make_request("GET", f"{user_id}/tags", tokens, params=params)
        
        return response.get("data", [])
        
    async def get_story_insights(
        self,
        tokens: OAuthTokens,
        story_id: str
    ) -> InstagramInsights:
        """Get insights for Instagram story"""
        
        metrics = ["impressions", "reach", "replies", "exits", "taps_forward", "taps_back"]
        params = {"metric": ",".join(metrics)}
        
        response = await self._make_request("GET", f"{story_id}/insights", tokens, params=params)
        
        insights_data = {}
        for item in response.get("data", []):
            metric_name = item["name"]
            values = item.get("values", [])
            if values and len(values) > 0:
                insights_data[metric_name] = values[0].get("value", 0)
                
        insights = InstagramInsights(
            media_id=story_id,
            period="lifetime",
            impressions=insights_data.get("impressions", 0),
            reach=insights_data.get("reach", 0)
        )
        
        return insights