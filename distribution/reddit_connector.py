"""
Reddit Platform Connector
=========================

Enterprise-grade Reddit API connector for Ainflue Distribution Platform.
Supports Reddit posting, commenting, subreddit management, and community analytics.

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
import base64
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import logging
import urllib.parse

logger = logging.getLogger(__name__)

class RedditPostType(Enum):
    """Reddit post types"""
    TEXT = "self"
    LINK = "link"
    IMAGE = "image"
    VIDEO = "video"
    GALLERY = "gallery"
    POLL = "poll"
    CROSSPOST = "crosspost"

class RedditSort(Enum):
    """Reddit sorting options"""
    HOT = "hot"
    NEW = "new"
    TOP = "top"
    RISING = "rising"
    CONTROVERSIAL = "controversial"
    BEST = "best"

class RedditTimeframe(Enum):
    """Reddit timeframe options for top/controversial"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"

class RedditFlairType(Enum):
    """Reddit flair types"""
    TEXT = "text"
    RICHTEXT = "richtext"

@dataclass
class RedditCredentials:
    """Reddit API credentials"""
    client_id: str
    client_secret: str
    username: str
    password: str
    user_agent: str
    redirect_uri: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

@dataclass
class RedditPost:
    """Reddit post structure"""
    title: str
    subreddit: str
    kind: RedditPostType = RedditPostType.TEXT
    text: Optional[str] = None
    url: Optional[str] = None
    flair_id: Optional[str] = None
    flair_text: Optional[str] = None
    nsfw: bool = False
    spoiler: bool = False
    send_replies: bool = True
    resubmit: bool = True
    collection_id: Optional[str] = None
    event_end: Optional[datetime] = None
    event_start: Optional[datetime] = None
    event_tz: Optional[str] = None

@dataclass
class RedditComment:
    """Reddit comment structure"""
    body: str
    parent_id: str  # Thing ID of parent (post or comment)
    return_rtjson: bool = False

@dataclass
class RedditSubmission:
    """Reddit submission data"""
    id: str
    title: str
    selftext: str
    url: str
    subreddit: str
    author: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: datetime
    permalink: str
    thumbnail: Optional[str] = None
    preview: Optional[Dict] = None
    is_video: bool = False
    is_self: bool = False
    over_18: bool = False
    spoiler: bool = False
    stickied: bool = False
    locked: bool = False
    distinguished: Optional[str] = None

@dataclass
class RedditPublishResult:
    """Result of Reddit publish operation"""
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    permalink: Optional[str] = None
    subreddit: Optional[str] = None
    status: str = "published"
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class RedditConnector:
    """Reddit platform connector with posting and community management"""
    
    BASE_URL = "https://www.reddit.com/api/v1"
    OAUTH_URL = "https://oauth.reddit.com"
    
    def __init__(self, credentials: RedditCredentials):
        """Initialize Reddit connector"""
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_info: Optional[Dict[str, Any]] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self._authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _authenticate(self):
        """Authenticate with Reddit API using OAuth2"""
        try:
            # Prepare authentication data
            auth_data = {
                "grant_type": "password",
                "username": self.credentials.username,
                "password": self.credentials.password
            }
            
            # Create basic auth header
            credentials = f"{self.credentials.client_id}:{self.credentials.client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {credentials_b64}",
                "User-Agent": self.credentials.user_agent,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with self.session.post(
                f"{self.BASE_URL}/access_token",
                data=auth_data,
                headers=headers
            ) as response:
                response.raise_for_status()
                token_data = await response.json()
                
                self.credentials.access_token = token_data["access_token"]
                self.credentials.refresh_token = token_data.get("refresh_token")
                
                logger.info("Reddit OAuth2 authentication successful")
                
                # Get user info
                await self._get_user_info()
                
        except Exception as e:
            logger.error(f"Reddit authentication failed: {e}")
            raise
    
    async def _get_user_info(self):
        """Get authenticated user information"""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "User-Agent": self.credentials.user_agent
            }
            
            async with self.session.get(
                f"{self.OAUTH_URL}/api/v1/me",
                headers=headers
            ) as response:
                response.raise_for_status()
                self.user_info = await response.json()
                
        except Exception as e:
            logger.error(f"Failed to get Reddit user info: {e}")
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        use_oauth: bool = True
    ) -> Dict[str, Any]:
        """Make authenticated request to Reddit API"""
        base_url = self.OAUTH_URL if use_oauth else "https://www.reddit.com"
        url = f"{base_url}/{endpoint.lstrip('/')}"
        
        headers = {
            "User-Agent": self.credentials.user_agent
        }
        
        if use_oauth and self.credentials.access_token:
            headers["Authorization"] = f"Bearer {self.credentials.access_token}"
        
        # Reddit API expects form data for POST requests
        if method.upper() == "POST" and data:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            form_data = urllib.parse.urlencode(data)
        else:
            headers["Content-Type"] = "application/json"
            form_data = None
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=form_data if form_data else None,
                json=data if not form_data else None,
                params=params
            ) as response:
                
                # Handle rate limiting
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Reddit rate limit hit, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, data, params, use_oauth)
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Reddit API request failed: {e}")
            raise
    
    async def submit_post(self, post: RedditPost) -> RedditPublishResult:
        """Submit a post to Reddit"""
        try:
            # Prepare submission data
            submission_data = {
                "api_type": "json",
                "kind": post.kind.value,
                "title": post.title,
                "sr": post.subreddit,
                "nsfw": post.nsfw,
                "spoiler": post.spoiler,
                "sendreplies": post.send_replies,
                "resubmit": post.resubmit
            }
            
            # Add content based on post type
            if post.kind == RedditPostType.TEXT:
                submission_data["text"] = post.text or ""
            elif post.kind == RedditPostType.LINK:
                submission_data["url"] = post.url
            
            # Add optional fields
            if post.flair_id:
                submission_data["flair_id"] = post.flair_id
            if post.flair_text:
                submission_data["flair_text"] = post.flair_text
            if post.collection_id:
                submission_data["collection_id"] = post.collection_id
            
            # Submit the post
            response = await self._make_request(
                "POST", 
                "/api/submit",
                data=submission_data
            )
            
            # Parse response
            if response.get("json", {}).get("errors"):
                errors = response["json"]["errors"]
                error_message = "; ".join([error[1] for error in errors])
                return RedditPublishResult(
                    success=False,
                    message=f"Reddit submission errors: {error_message}",
                    metadata=response
                )
            
            # Extract post information
            post_data = response.get("json", {}).get("data", {})
            post_id = post_data.get("id")
            post_url = post_data.get("url")
            
            if post_id:
                permalink = f"https://www.reddit.com/r/{post.subreddit}/comments/{post_id}/"
                return RedditPublishResult(
                    success=True,
                    post_id=post_id,
                    post_url=post_url,
                    permalink=permalink,
                    subreddit=post.subreddit,
                    message="Post submitted successfully to Reddit",
                    metadata=post_data
                )
            else:
                return RedditPublishResult(
                    success=False,
                    message="Unknown error during Reddit submission",
                    metadata=response
                )
                
        except Exception as e:
            logger.error(f"Failed to submit Reddit post: {e}")
            return RedditPublishResult(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    async def submit_comment(self, comment: RedditComment) -> RedditPublishResult:
        """Submit a comment to Reddit"""
        try:
            comment_data = {
                "api_type": "json",
                "text": comment.body,
                "thing_id": comment.parent_id,
                "return_rtjson": comment.return_rtjson
            }
            
            response = await self._make_request(
                "POST",
                "/api/comment",
                data=comment_data
            )
            
            # Parse response
            if response.get("json", {}).get("errors"):
                errors = response["json"]["errors"]
                error_message = "; ".join([error[1] for error in errors])
                return RedditPublishResult(
                    success=False,
                    message=f"Reddit comment errors: {error_message}",
                    metadata=response
                )
            
            comment_data = response.get("json", {}).get("data", {}).get("things", [])
            if comment_data:
                comment_info = comment_data[0].get("data", {})
                return RedditPublishResult(
                    success=True,
                    post_id=comment_info.get("id"),
                    permalink=f"https://www.reddit.com{comment_info.get('permalink', '')}",
                    message="Comment submitted successfully",
                    metadata=comment_info
                )
            else:
                return RedditPublishResult(
                    success=False,
                    message="Unknown error during comment submission",
                    metadata=response
                )
                
        except Exception as e:
            logger.error(f"Failed to submit Reddit comment: {e}")
            return RedditPublishResult(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    async def get_subreddit_info(self, subreddit: str) -> Dict[str, Any]:
        """Get subreddit information"""
        return await self._make_request("GET", f"/r/{subreddit}/about")
    
    async def get_subreddit_posts(
        self, 
        subreddit: str,
        sort: RedditSort = RedditSort.HOT,
        timeframe: RedditTimeframe = RedditTimeframe.DAY,
        limit: int = 25,
        after: Optional[str] = None
    ) -> List[RedditSubmission]:
        """Get posts from a subreddit"""
        params = {
            "limit": limit,
            "raw_json": 1
        }
        
        if after:
            params["after"] = after
        
        if sort in [RedditSort.TOP, RedditSort.CONTROVERSIAL]:
            params["t"] = timeframe.value
        
        endpoint = f"/r/{subreddit}/{sort.value}"
        response = await self._make_request("GET", endpoint, params=params)
        
        posts = []
        for post_data in response.get("data", {}).get("children", []):
            data = post_data.get("data", {})
            
            posts.append(RedditSubmission(
                id=data.get("id", ""),
                title=data.get("title", ""),
                selftext=data.get("selftext", ""),
                url=data.get("url", ""),
                subreddit=data.get("subreddit", ""),
                author=data.get("author", ""),
                score=data.get("score", 0),
                upvote_ratio=data.get("upvote_ratio", 0.0),
                num_comments=data.get("num_comments", 0),
                created_utc=datetime.fromtimestamp(data.get("created_utc", 0), tz=timezone.utc),
                permalink=data.get("permalink", ""),
                thumbnail=data.get("thumbnail"),
                preview=data.get("preview"),
                is_video=data.get("is_video", False),
                is_self=data.get("is_self", False),
                over_18=data.get("over_18", False),
                spoiler=data.get("spoiler", False),
                stickied=data.get("stickied", False),
                locked=data.get("locked", False),
                distinguished=data.get("distinguished")
            ))
        
        return posts
    
    async def get_post_comments(
        self, 
        subreddit: str, 
        post_id: str,
        sort: str = "best",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get comments for a specific post"""
        params = {
            "sort": sort,
            "limit": limit,
            "raw_json": 1
        }
        
        endpoint = f"/r/{subreddit}/comments/{post_id}"
        return await self._make_request("GET", endpoint, params=params)
    
    async def vote(self, thing_id: str, direction: int) -> bool:
        """Vote on a post or comment (1 = upvote, -1 = downvote, 0 = no vote)"""
        try:
            vote_data = {
                "id": thing_id,
                "dir": direction
            }
            
            await self._make_request("POST", "/api/vote", data=vote_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to vote on Reddit: {e}")
            return False
    
    async def save_post(self, thing_id: str) -> bool:
        """Save a post or comment"""
        try:
            save_data = {"id": thing_id}
            await self._make_request("POST", "/api/save", data=save_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to save Reddit post: {e}")
            return False
    
    async def unsave_post(self, thing_id: str) -> bool:
        """Unsave a post or comment"""
        try:
            unsave_data = {"id": thing_id}
            await self._make_request("POST", "/api/unsave", data=unsave_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsave Reddit post: {e}")
            return False
    
    async def get_user_posts(
        self, 
        username: str,
        sort: str = "new",
        timeframe: str = "all",
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Get posts by a specific user"""
        params = {
            "sort": sort,
            "t": timeframe,
            "limit": limit,
            "raw_json": 1
        }
        
        response = await self._make_request("GET", f"/user/{username}/submitted", params=params)
        return response.get("data", {}).get("children", [])
    
    async def get_subreddit_rules(self, subreddit: str) -> Dict[str, Any]:
        """Get subreddit rules"""
        return await self._make_request("GET", f"/r/{subreddit}/about/rules")
    
    async def get_subreddit_flairs(self, subreddit: str) -> List[Dict[str, Any]]:
        """Get available post flairs for a subreddit"""
        response = await self._make_request("GET", f"/r/{subreddit}/api/link_flair_v2")
        return response
    
    async def search_subreddits(
        self, 
        query: str,
        limit: int = 25,
        sort: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """Search for subreddits"""
        params = {
            "q": query,
            "type": "sr",
            "limit": limit,
            "sort": sort,
            "raw_json": 1
        }
        
        response = await self._make_request("GET", "/subreddits/search", params=params)
        return response.get("data", {}).get("children", [])
    
    async def get_trending_subreddits(self) -> List[str]:
        """Get trending subreddits"""
        try:
            response = await self._make_request("GET", "/api/trending_subreddits", use_oauth=False)
            return response.get("subreddit_names", [])
        except Exception as e:
            logger.error(f"Failed to get trending subreddits: {e}")
            return []
    
    async def get_user_analytics(self, username: Optional[str] = None) -> Dict[str, Any]:
        """Get user analytics and karma breakdown"""
        try:
            target_user = username or self.user_info.get("name", "")
            
            # Get user overview
            user_response = await self._make_request("GET", f"/user/{target_user}/about")
            user_data = user_response.get("data", {})
            
            # Get user posts and comments
            posts = await self.get_user_posts(target_user, limit=100)
            
            # Calculate analytics
            total_post_karma = sum(
                post.get("data", {}).get("score", 0) 
                for post in posts
            )
            
            return {
                "username": target_user,
                "total_karma": user_data.get("total_karma", 0),
                "link_karma": user_data.get("link_karma", 0),
                "comment_karma": user_data.get("comment_karma", 0),
                "account_created": datetime.fromtimestamp(
                    user_data.get("created_utc", 0), tz=timezone.utc
                ).isoformat(),
                "is_verified": user_data.get("verified", False),
                "has_verified_email": user_data.get("has_verified_email", False),
                "post_count": len(posts),
                "calculated_post_karma": total_post_karma,
                "avg_post_score": total_post_karma / len(posts) if posts else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {"error": str(e)}
    
    async def validate_connection(self) -> bool:
        """Validate Reddit connection"""
        try:
            if not self.user_info:
                await self._get_user_info()
            
            return self.user_info is not None and self.credentials.access_token is not None
            
        except Exception as e:
            logger.error(f"Reddit connection validation failed: {e}")
            return False
    
    async def get_platform_limits(self) -> Dict[str, Any]:
        """Get Reddit platform limits and guidelines"""
        return {
            "max_title_length": 300,
            "max_selftext_length": 40000,
            "max_comment_length": 10000,
            "rate_limits": {
                "posts_per_hour": 5,
                "comments_per_minute": 10,
                "api_requests_per_minute": 60
            },
            "karma_requirements": {
                "posting_threshold": 10,  # Varies by subreddit
                "commenting_threshold": 1
            },
            "account_age_requirements": {
                "posting_minimum_days": 1,  # Varies by subreddit
                "commenting_minimum_days": 0
            },
            "content_guidelines": {
                "spam_prevention": True,
                "self_promotion_limit": "10% rule",
                "vote_manipulation_forbidden": True,
                "brigading_forbidden": True
            },
            "supported_media": {
                "images": ["jpg", "jpeg", "png", "gif"],
                "videos": ["mp4", "mov"],
                "max_image_size_mb": 20,
                "max_video_size_mb": 1000,
                "galleries_max_items": 20
            }
        }


# Export main components
__all__ = [
    "RedditConnector",
    "RedditCredentials",
    "RedditPost",
    "RedditComment",
    "RedditSubmission",
    "RedditPublishResult",
    "RedditPostType",
    "RedditSort",
    "RedditTimeframe",
    "RedditFlairType"
]