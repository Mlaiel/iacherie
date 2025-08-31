"""
Pinterest API Integration
=========================

Complete Pinterest API integration for board management, pin creation, and analytics.
Handles pins, boards, tracking, and audience insights.

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
class PinterestPin:
    """Pinterest pin information"""
    pin_id: str
    board_id: str
    title: str
    description: str
    link: str
    media_url: str
    created_at: datetime
    updated_at: datetime
    creator_id: str
    save_count: int = 0
    comment_count: int = 0
    impression_count: int = 0
    click_count: int = 0
    pin_metrics: Dict[str, Any] = None


@dataclass
class PinterestBoard:
    """Pinterest board information"""
    board_id: str
    name: str
    description: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    pin_count: int = 0
    follower_count: int = 0
    privacy: str = "PUBLIC"  # "PUBLIC", "PROTECTED", "SECRET"
    board_url: str = None
    cover_pin_id: str = None


@dataclass
class PinterestUser:
    """Pinterest user/business account information"""
    user_id: str
    username: str
    first_name: str
    last_name: str
    bio: str
    profile_image_url: str
    website_url: str
    verified: bool = False
    monthly_views: int = 0
    follower_count: int = 0
    following_count: int = 0
    board_count: int = 0
    pin_count: int = 0
    account_type: str = "PERSONAL"  # "PERSONAL", "BUSINESS"


@dataclass
class PinterestAnalytics:
    """Pinterest analytics data"""
    entity_id: str  # Pin, Board, or User ID
    entity_type: str  # "PIN", "BOARD", "USER"
    date_range: Dict[str, str]
    impressions: int = 0
    saves: int = 0
    clicks: int = 0
    comments: int = 0
    video_views: int = 0
    video_avg_watch_time: float = 0.0
    engagement_rate: float = 0.0
    reach: int = 0
    profile_visits: int = 0


class PinterestAPI:
    """Pinterest API integration"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://api.pinterest.com/v5"
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
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
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("pinterest", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("pinterest", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{self.base_url}/{endpoint}"
        
        # Default headers
        request_headers = {
            "Authorization": f"{tokens.token_type} {tokens.access_token}",
            "Accept": "application/json",
            "User-Agent": "Ainflue/1.0"
        }
        
        if headers:
            request_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=request_headers) as response:
                    await self.rate_limiter.record_request("pinterest", endpoint, None, response.status)
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        raise Exception("Rate limit exceeded")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                request_headers["Content-Type"] = "application/json"
                async with self.session.post(url, json=data, headers=request_headers, params=params) as response:
                    await self.rate_limiter.record_request("pinterest", endpoint, None, response.status)
                    
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() in ["PUT", "PATCH", "DELETE"]:
                if data:
                    request_headers["Content-Type"] = "application/json"
                    
                async with self.session.request(
                    method, url, json=data, headers=request_headers, params=params
                ) as response:
                    await self.rate_limiter.record_request("pinterest", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Pinterest API request failed: {e}")
            raise
            
    async def get_user_profile(self, tokens: OAuthTokens) -> PinterestUser:
        """Get current user profile information"""
        
        response = await self._make_request("GET", "user_account", tokens)
        
        user = PinterestUser(
            user_id=response.get("id", ""),
            username=response.get("username", ""),
            first_name=response.get("first_name", ""),
            last_name=response.get("last_name", ""),
            bio=response.get("bio", ""),
            profile_image_url=response.get("profile_image", ""),
            website_url=response.get("website_url", ""),
            verified=response.get("verified", False),
            monthly_views=response.get("monthly_views", 0),
            follower_count=response.get("follower_count", 0),
            following_count=response.get("following_count", 0),
            board_count=response.get("board_count", 0),
            pin_count=response.get("pin_count", 0),
            account_type=response.get("account_type", "PERSONAL")
        )
        
        return user
        
    async def get_user_boards(
        self,
        tokens: OAuthTokens,
        page_size: int = 25,
        bookmark: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's boards"""
        
        params = {"page_size": min(page_size, 100)}
        if bookmark:
            params["bookmark"] = bookmark
            
        response = await self._make_request("GET", "boards", tokens, params=params)
        
        boards = []
        for item in response.get("items", []):
            board = PinterestBoard(
                board_id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                owner_id=item["owner"]["id"],
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")),
                pin_count=item.get("pin_count", 0),
                follower_count=item.get("follower_count", 0),
                privacy=item.get("privacy", "PUBLIC"),
                board_url=item.get("board_url", ""),
                cover_pin_id=item.get("cover_pin", {}).get("id", "") if item.get("cover_pin") else ""
            )
            boards.append(board)
            
        return {
            "items": boards,
            "bookmark": response.get("bookmark", "")
        }
        
    async def create_board(
        self,
        tokens: OAuthTokens,
        name: str,
        description: str = "",
        privacy: str = "PUBLIC"
    ) -> PinterestBoard:
        """Create a new board"""
        
        board_data = {
            "name": name,
            "description": description,
            "privacy": privacy
        }
        
        response = await self._make_request("POST", "boards", tokens, data=board_data)
        
        board = PinterestBoard(
            board_id=response["id"],
            name=response["name"],
            description=response.get("description", ""),
            owner_id=response["owner"]["id"],
            created_at=datetime.fromisoformat(response["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(response["updated_at"].replace("Z", "+00:00")),
            privacy=response.get("privacy", "PUBLIC"),
            board_url=response.get("board_url", "")
        )
        
        logger.info(f"Created Pinterest board: {board.board_id}")
        return board
        
    async def get_board_details(self, tokens: OAuthTokens, board_id: str) -> PinterestBoard:
        """Get detailed information about a board"""
        
        response = await self._make_request("GET", f"boards/{board_id}", tokens)
        
        board = PinterestBoard(
            board_id=response["id"],
            name=response["name"],
            description=response.get("description", ""),
            owner_id=response["owner"]["id"],
            created_at=datetime.fromisoformat(response["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(response["updated_at"].replace("Z", "+00:00")),
            pin_count=response.get("pin_count", 0),
            follower_count=response.get("follower_count", 0),
            privacy=response.get("privacy", "PUBLIC"),
            board_url=response.get("board_url", ""),
            cover_pin_id=response.get("cover_pin", {}).get("id", "") if response.get("cover_pin") else ""
        )
        
        return board
        
    async def get_board_pins(
        self,
        tokens: OAuthTokens,
        board_id: str,
        page_size: int = 25,
        bookmark: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get pins from a board"""
        
        params = {"page_size": min(page_size, 100)}
        if bookmark:
            params["bookmark"] = bookmark
            
        response = await self._make_request("GET", f"boards/{board_id}/pins", tokens, params=params)
        
        pins = []
        for item in response.get("items", []):
            pin = PinterestPin(
                pin_id=item["id"],
                board_id=board_id,
                title=item.get("title", ""),
                description=item.get("description", ""),
                link=item.get("link", ""),
                media_url=item.get("media", {}).get("images", {}).get("originals", {}).get("url", ""),
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")),
                creator_id=item.get("creator", {}).get("id", ""),
                save_count=item.get("save_count", 0),
                comment_count=item.get("comment_count", 0)
            )
            pins.append(pin)
            
        return {
            "items": pins,
            "bookmark": response.get("bookmark", "")
        }
        
    async def create_pin(
        self,
        tokens: OAuthTokens,
        board_id: str,
        title: str,
        description: str,
        media_url: str,
        link: Optional[str] = None,
        alt_text: Optional[str] = None
    ) -> PinterestPin:
        """Create a new pin"""
        
        pin_data = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "media_source": {
                "source_type": "image_url",
                "url": media_url
            }
        }
        
        if link:
            pin_data["link"] = link
        if alt_text:
            pin_data["alt_text"] = alt_text
            
        response = await self._make_request("POST", "pins", tokens, data=pin_data)
        
        pin = PinterestPin(
            pin_id=response["id"],
            board_id=board_id,
            title=response.get("title", ""),
            description=response.get("description", ""),
            link=response.get("link", ""),
            media_url=response.get("media", {}).get("images", {}).get("originals", {}).get("url", ""),
            created_at=datetime.fromisoformat(response["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(response["updated_at"].replace("Z", "+00:00")),
            creator_id=response.get("creator", {}).get("id", "")
        )
        
        logger.info(f"Created Pinterest pin: {pin.pin_id}")
        return pin
        
    async def get_pin_details(self, tokens: OAuthTokens, pin_id: str) -> PinterestPin:
        """Get detailed information about a pin"""
        
        response = await self._make_request("GET", f"pins/{pin_id}", tokens)
        
        pin = PinterestPin(
            pin_id=response["id"],
            board_id=response.get("board_id", ""),
            title=response.get("title", ""),
            description=response.get("description", ""),
            link=response.get("link", ""),
            media_url=response.get("media", {}).get("images", {}).get("originals", {}).get("url", ""),
            created_at=datetime.fromisoformat(response["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(response["updated_at"].replace("Z", "+00:00")),
            creator_id=response.get("creator", {}).get("id", ""),
            save_count=response.get("save_count", 0),
            comment_count=response.get("comment_count", 0)
        )
        
        return pin
        
    async def update_pin(
        self,
        tokens: OAuthTokens,
        pin_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        link: Optional[str] = None,
        board_id: Optional[str] = None
    ) -> PinterestPin:
        """Update pin information"""
        
        update_data = {}
        if title:
            update_data["title"] = title
        if description:
            update_data["description"] = description
        if link:
            update_data["link"] = link
        if board_id:
            update_data["board_id"] = board_id
            
        response = await self._make_request("PATCH", f"pins/{pin_id}", tokens, data=update_data)
        
        pin = PinterestPin(
            pin_id=response["id"],
            board_id=response.get("board_id", ""),
            title=response.get("title", ""),
            description=response.get("description", ""),
            link=response.get("link", ""),
            media_url=response.get("media", {}).get("images", {}).get("originals", {}).get("url", ""),
            created_at=datetime.fromisoformat(response["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(response["updated_at"].replace("Z", "+00:00")),
            creator_id=response.get("creator", {}).get("id", "")
        )
        
        logger.info(f"Updated Pinterest pin: {pin_id}")
        return pin
        
    async def delete_pin(self, tokens: OAuthTokens, pin_id: str) -> bool:
        """Delete a pin"""
        
        try:
            await self._make_request("DELETE", f"pins/{pin_id}", tokens)
            logger.info(f"Deleted Pinterest pin: {pin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete pin {pin_id}: {e}")
            return False
            
    async def get_pin_analytics(
        self,
        tokens: OAuthTokens,
        pin_id: str,
        start_date: datetime,
        end_date: datetime,
        metric_types: Optional[List[str]] = None
    ) -> PinterestAnalytics:
        """Get analytics for a specific pin"""
        
        default_metrics = ["IMPRESSION", "SAVE", "PIN_CLICK", "OUTBOUND_CLICK"]
        metrics = metric_types or default_metrics
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "metric_types": ",".join(metrics),
            "granularity": "TOTAL"
        }
        
        try:
            response = await self._make_request("GET", f"pins/{pin_id}/analytics", tokens, params=params)
            
            daily_metrics = response.get("daily_metrics", [])
            summary_metrics = response.get("summary_metrics", {})
            
            analytics = PinterestAnalytics(
                entity_id=pin_id,
                entity_type="PIN",
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                },
                impressions=summary_metrics.get("IMPRESSION", 0),
                saves=summary_metrics.get("SAVE", 0),
                clicks=summary_metrics.get("PIN_CLICK", 0) + summary_metrics.get("OUTBOUND_CLICK", 0)
            )
            
            return analytics
            
        except Exception as e:
            logger.warning(f"Could not get analytics for pin {pin_id}: {e}")
            return PinterestAnalytics(
                entity_id=pin_id,
                entity_type="PIN",
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                }
            )
            
    async def get_user_analytics(
        self,
        tokens: OAuthTokens,
        start_date: datetime,
        end_date: datetime,
        metric_types: Optional[List[str]] = None
    ) -> PinterestAnalytics:
        """Get analytics for user account"""
        
        default_metrics = ["IMPRESSION", "SAVE", "PIN_CLICK", "OUTBOUND_CLICK", "QUARTILE_95_PERCENT_VIEW"]
        metrics = metric_types or default_metrics
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "metric_types": ",".join(metrics),
            "granularity": "TOTAL"
        }
        
        try:
            response = await self._make_request("GET", "user_account/analytics", tokens, params=params)
            
            summary_metrics = response.get("summary_metrics", {})
            
            analytics = PinterestAnalytics(
                entity_id="user_account",
                entity_type="USER",
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                },
                impressions=summary_metrics.get("IMPRESSION", 0),
                saves=summary_metrics.get("SAVE", 0),
                clicks=summary_metrics.get("PIN_CLICK", 0) + summary_metrics.get("OUTBOUND_CLICK", 0),
                video_views=summary_metrics.get("QUARTILE_95_PERCENT_VIEW", 0)
            )
            
            return analytics
            
        except Exception as e:
            logger.warning(f"Could not get user analytics: {e}")
            return PinterestAnalytics(
                entity_id="user_account",
                entity_type="USER",
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                }
            )
            
    async def search_pins(
        self,
        tokens: OAuthTokens,
        query: str,
        page_size: int = 25,
        bookmark: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for pins by keywords"""
        
        params = {
            "query": query,
            "page_size": min(page_size, 100)
        }
        if bookmark:
            params["bookmark"] = bookmark
            
        response = await self._make_request("GET", "search/pins", tokens, params=params)
        
        pins = []
        for item in response.get("items", []):
            pin = PinterestPin(
                pin_id=item["id"],
                board_id=item.get("board_id", ""),
                title=item.get("title", ""),
                description=item.get("description", ""),
                link=item.get("link", ""),
                media_url=item.get("media", {}).get("images", {}).get("originals", {}).get("url", ""),
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")),
                creator_id=item.get("creator", {}).get("id", ""),
                save_count=item.get("save_count", 0),
                comment_count=item.get("comment_count", 0)
            )
            pins.append(pin)
            
        return {
            "items": pins,
            "bookmark": response.get("bookmark", "")
        }
        
    async def search_boards(
        self,
        tokens: OAuthTokens,
        query: str,
        page_size: int = 25,
        bookmark: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for boards by keywords"""
        
        params = {
            "query": query,
            "page_size": min(page_size, 100)
        }
        if bookmark:
            params["bookmark"] = bookmark
            
        response = await self._make_request("GET", "search/boards", tokens, params=params)
        
        boards = []
        for item in response.get("items", []):
            board = PinterestBoard(
                board_id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                owner_id=item["owner"]["id"],
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")),
                pin_count=item.get("pin_count", 0),
                follower_count=item.get("follower_count", 0),
                privacy=item.get("privacy", "PUBLIC"),
                board_url=item.get("board_url", "")
            )
            boards.append(board)
            
        return {
            "items": boards,
            "bookmark": response.get("bookmark", "")
        }
        
    async def follow_board(self, tokens: OAuthTokens, board_id: str) -> bool:
        """Follow a board"""
        
        try:
            await self._make_request("POST", f"boards/{board_id}/follow", tokens)
            logger.info(f"Successfully followed board: {board_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to follow board {board_id}: {e}")
            return False
            
    async def unfollow_board(self, tokens: OAuthTokens, board_id: str) -> bool:
        """Unfollow a board"""
        
        try:
            await self._make_request("DELETE", f"boards/{board_id}/follow", tokens)
            logger.info(f"Successfully unfollowed board: {board_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unfollow board {board_id}: {e}")
            return False
            
    async def follow_user(self, tokens: OAuthTokens, user_id: str) -> bool:
        """Follow a user"""
        
        try:
            await self._make_request("POST", f"users/{user_id}/follow", tokens)
            logger.info(f"Successfully followed user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to follow user {user_id}: {e}")
            return False
            
    async def unfollow_user(self, tokens: OAuthTokens, user_id: str) -> bool:
        """Unfollow a user"""
        
        try:
            await self._make_request("DELETE", f"users/{user_id}/follow", tokens)
            logger.info(f"Successfully unfollowed user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unfollow user {user_id}: {e}")
            return False
            
    async def get_trending_keywords(self, tokens: OAuthTokens, region: str = "US") -> List[str]:
        """Get trending keywords for the specified region"""
        
        params = {"region": region}
        
        try:
            response = await self._make_request("GET", "trends", tokens, params=params)
            trends = response.get("trends", [])
            keywords = [trend.get("keyword", "") for trend in trends if trend.get("keyword")]
            return keywords
        except Exception as e:
            logger.error(f"Failed to get trending keywords: {e}")
            return []