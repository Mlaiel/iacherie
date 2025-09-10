"""
OnlyFans Platform Connector
=========================

Enterprise-grade OnlyFans API connector for Ainflue Distribution Platform.
Supports content publishing, subscriber management, and monetization analytics.

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
import hashlib
import mimetypes
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OnlyFansContentType(Enum):
    """OnlyFans content type options"""
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    LIVE = "live"
    STORY = "story"

class OnlyFansPrivacyLevel(Enum):
    """OnlyFans privacy level options"""
    PUBLIC = "public"
    SUBSCRIBERS = "subscribers"
    VIP = "vip"
    PRIVATE = "private"

class OnlyFansMessageType(Enum):
    """OnlyFans message type options"""
    REGULAR = "regular"
    MASS = "mass"
    VIP = "vip"
    PROMOTIONAL = "promotional"

@dataclass
class OnlyFansCredentials:
    """OnlyFans API credentials"""
    session_token: str
    csrf_token: str
    user_agent: str
    user_id: str
    
    def __post_init__(self):
        if not all([self.session_token, self.csrf_token, self.user_agent, self.user_id]):
            raise ValueError("All OnlyFans credentials are required")

@dataclass
class OnlyFansPost:
    """OnlyFans post data model"""
    content: str
    content_type: OnlyFansContentType = OnlyFansContentType.TEXT
    privacy_level: OnlyFansPrivacyLevel = OnlyFansPrivacyLevel.SUBSCRIBERS
    media_files: List[str] = field(default_factory=list)
    price: Optional[float] = None
    schedule_time: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    location: Optional[str] = None
    is_promotional: bool = False
    allow_comments: bool = True
    expire_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format"""
        data = {
            "text": self.content,
            "type": self.content_type.value,
            "privacy": self.privacy_level.value,
            "isPromo": self.is_promotional,
            "allowComments": self.allow_comments
        }
        
        if self.price is not None:
            data["price"] = self.price
        if self.schedule_time:
            data["scheduledDate"] = self.schedule_time.isoformat()
        if self.tags:
            data["tags"] = self.tags
        if self.location:
            data["location"] = self.location
        if self.expire_date:
            data["expireDate"] = self.expire_date.isoformat()
            
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class OnlyFansAnalytics:
    """OnlyFans analytics data"""
    post_id: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    tips: float = 0.0
    revenue: float = 0.0
    reach: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    click_through_rate: float = 0.0
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'OnlyFansAnalytics':
        """Create from API response"""
        return cls(
            post_id=data.get("id", ""),
            views=data.get("viewsCount", 0),
            likes=data.get("likesCount", 0),
            comments=data.get("commentsCount", 0),
            tips=data.get("tipsAmount", 0.0),
            revenue=data.get("revenue", 0.0),
            reach=data.get("reach", 0),
            engagement_rate=data.get("engagementRate", 0.0),
            conversion_rate=data.get("conversionRate", 0.0),
            click_through_rate=data.get("clickThroughRate", 0.0)
        )

class OnlyFansConnector:
    """
    Enterprise-grade OnlyFans API connector
    
    Features:
    - Content publishing and management
    - Subscriber engagement and analytics
    - Revenue tracking and optimization
    - Privacy and content protection
    - Advanced monetization tools
    
    Note: This connector requires proper authentication and compliance
    with OnlyFans terms of service and content policies.
    """
    
    BASE_URL = "https://onlyfans.com/api2/v2"
    
    def __init__(self, credentials: OnlyFansCredentials):
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_remaining = 60
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
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Cookie": f"sess={self.credentials.session_token}",
                    "X-BC": self.credentials.csrf_token,
                    "User-Agent": self.credentials.user_agent,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            logger.info("OnlyFans connector initialized")
            
    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("OnlyFans connector disconnected")
            
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        if not self.session:
            await self.connect()
            
        # Check rate limiting
        if self._rate_limit_remaining <= 1:
            if datetime.now(timezone.utc) < self._rate_limit_reset:
                wait_time = (self._rate_limit_reset - datetime.now(timezone.utc)).total_seconds()
                logger.warning(f"Rate limit reached, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
                
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            # Handle file uploads differently
            if files:
                form_data = aiohttp.FormData()
                if data:
                    for key, value in data.items():
                        form_data.add_field(key, json.dumps(value) if isinstance(value, (dict, list)) else str(value))
                
                for key, file_path in files.items():
                    with open(file_path, 'rb') as f:
                        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                        form_data.add_field(key, f, filename=Path(file_path).name, content_type=content_type)
                
                async with self.session.request(method, url, data=form_data, params=params) as response:
                    return await self._handle_response(response)
            else:
                async with self.session.request(
                    method, url, json=data, params=params
                ) as response:
                    return await self._handle_response(response)
                    
        except aiohttp.ClientError as e:
            logger.error(f"OnlyFans API request failed: {e}")
            raise Exception(f"OnlyFans API error: {e}")
            
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response with rate limiting"""
        # Update rate limiting info
        self._rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 60))
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
        return await response.json()
        
    async def publish_post(self, post: OnlyFansPost) -> Dict[str, Any]:
        """
        Publish content on OnlyFans
        
        Args:
            post: OnlyFansPost object with content and settings
            
        Returns:
            Dict with post ID and publication details
        """
        try:
            endpoint = "posts"
            post_data = post.to_dict()
            
            # Handle media uploads if present
            files = {}
            if post.media_files:
                # First upload media files
                media_ids = []
                for i, media_file in enumerate(post.media_files):
                    media_id = await self._upload_media(media_file)
                    if media_id:
                        media_ids.append(media_id)
                
                if media_ids:
                    post_data["mediaIds"] = media_ids
            
            logger.info(f"Publishing OnlyFans post: {post.content[:50]}...")
            
            response = await self._make_request("POST", endpoint, post_data)
            
            result = {
                "success": True,
                "platform": "onlyfans",
                "post_id": response.get("id"),
                "url": f"https://onlyfans.com/{self.credentials.user_id}/post/{response.get('id')}",
                "status": "published" if not post.schedule_time else "scheduled",
                "published_at": response.get("postedAt"),
                "privacy_level": post.privacy_level.value,
                "metadata": {
                    "content_type": post.content_type.value,
                    "price": post.price,
                    "is_promotional": post.is_promotional,
                    "media_count": len(post.media_files)
                }
            }
            
            logger.info(f"OnlyFans post published successfully: {result['post_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to publish OnlyFans post: {e}")
            return {
                "success": False,
                "platform": "onlyfans",
                "error": str(e),
                "error_type": "publication_failed"
            }
            
    async def _upload_media(self, file_path: str) -> Optional[str]:
        """Upload media file and return media ID"""
        try:
            endpoint = "upload"
            
            files = {"file": file_path}
            response = await self._make_request("POST", endpoint, files=files)
            
            return response.get("id")
            
        except Exception as e:
            logger.error(f"Failed to upload media file {file_path}: {e}")
            return None
            
    async def update_post(self, post_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing post"""
        try:
            endpoint = f"posts/{post_id}"
            
            response = await self._make_request("PUT", endpoint, updates)
            
            return {
                "success": True,
                "platform": "onlyfans",
                "post_id": post_id,
                "updated_at": response.get("updatedAt"),
                "changes": list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to update OnlyFans post {post_id}: {e}")
            return {
                "success": False,
                "platform": "onlyfans",
                "error": str(e),
                "post_id": post_id
            }
            
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a post"""
        try:
            endpoint = f"posts/{post_id}"
            
            await self._make_request("DELETE", endpoint)
            
            return {
                "success": True,
                "platform": "onlyfans",
                "post_id": post_id,
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete OnlyFans post {post_id}: {e}")
            return {
                "success": False,
                "platform": "onlyfans",
                "error": str(e),
                "post_id": post_id
            }
            
    async def get_post_analytics(self, post_id: str) -> OnlyFansAnalytics:
        """Get comprehensive analytics for a specific post"""
        try:
            endpoint = f"posts/{post_id}/stats"
            
            response = await self._make_request("GET", endpoint)
            
            return OnlyFansAnalytics.from_api_response(response)
            
        except Exception as e:
            logger.error(f"Failed to get OnlyFans analytics for post {post_id}: {e}")
            return OnlyFansAnalytics(post_id=post_id)
            
    async def get_subscriber_analytics(self) -> Dict[str, Any]:
        """Get subscriber analytics and revenue metrics"""
        try:
            endpoint = f"users/{self.credentials.user_id}/stats"
            
            response = await self._make_request("GET", endpoint)
            
            return {
                "total_subscribers": response.get("subscribersCount", 0),
                "active_subscribers": response.get("activeSubscribers", 0),
                "new_subscribers": response.get("newSubscribers", 0),
                "total_revenue": response.get("totalRevenue", 0.0),
                "monthly_revenue": response.get("monthlyRevenue", 0.0),
                "tips_received": response.get("tipsReceived", 0.0),
                "messages_sent": response.get("messagesSent", 0),
                "average_tip": response.get("averageTip", 0.0),
                "subscription_price": response.get("subscriptionPrice", 0.0),
                "retention_rate": response.get("retentionRate", 0.0),
                "engagement_rate": response.get("engagementRate", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get OnlyFans subscriber analytics: {e}")
            return {}
            
    async def send_message(
        self,
        recipient_id: str,
        message: str,
        message_type: OnlyFansMessageType = OnlyFansMessageType.REGULAR,
        media_files: Optional[List[str]] = None,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Send direct message to subscriber"""
        try:
            endpoint = "chats/messages"
            
            message_data = {
                "text": message,
                "userId": recipient_id,
                "type": message_type.value
            }
            
            if price is not None:
                message_data["price"] = price
                
            # Handle media attachments
            if media_files:
                media_ids = []
                for media_file in media_files:
                    media_id = await self._upload_media(media_file)
                    if media_id:
                        media_ids.append(media_id)
                
                if media_ids:
                    message_data["mediaIds"] = media_ids
            
            response = await self._make_request("POST", endpoint, message_data)
            
            return {
                "success": True,
                "platform": "onlyfans",
                "message_id": response.get("id"),
                "sent_at": response.get("createdAt"),
                "recipient_id": recipient_id,
                "type": message_type.value
            }
            
        except Exception as e:
            logger.error(f"Failed to send OnlyFans message: {e}")
            return {
                "success": False,
                "platform": "onlyfans",
                "error": str(e)
            }
            
    async def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts with basic metrics"""
        try:
            endpoint = f"users/{self.credentials.user_id}/posts"
            params = {"limit": limit, "offset": 0}
            
            response = await self._make_request("GET", endpoint, params=params)
            
            posts = []
            for post_data in response.get("list", []):
                posts.append({
                    "id": post_data.get("id"),
                    "text": post_data.get("text", ""),
                    "url": f"https://onlyfans.com/{self.credentials.user_id}/post/{post_data.get('id')}",
                    "posted_at": post_data.get("postedAt"),
                    "media_count": len(post_data.get("media", [])),
                    "likes_count": post_data.get("likesCount", 0),
                    "comments_count": post_data.get("commentsCount", 0),
                    "views_count": post_data.get("viewsCount", 0),
                    "price": post_data.get("price"),
                    "is_promotional": post_data.get("isPromo", False)
                })
                
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get recent OnlyFans posts: {e}")
            return []
            
    async def validate_credentials(self) -> bool:
        """Validate API credentials"""
        try:
            endpoint = f"users/{self.credentials.user_id}"
            await self._make_request("GET", endpoint)
            return True
            
        except Exception as e:
            logger.error(f"OnlyFans credentials validation failed: {e}")
            return False
            
    async def get_profile_stats(self) -> Dict[str, Any]:
        """Get overall profile statistics"""
        try:
            endpoint = f"users/{self.credentials.user_id}/profile"
            
            response = await self._make_request("GET", endpoint)
            
            return {
                "username": response.get("username"),
                "display_name": response.get("name"),
                "bio": response.get("rawAbout"),
                "total_posts": response.get("postsCount", 0),
                "total_subscribers": response.get("subscribersCount", 0),
                "total_photos": response.get("photosCount", 0),
                "total_videos": response.get("videosCount", 0),
                "subscription_price": response.get("subscribePrice", 0.0),
                "is_verified": response.get("isVerified", False),
                "join_date": response.get("joinDate"),
                "last_seen": response.get("lastSeen")
            }
            
        except Exception as e:
            logger.error(f"Failed to get OnlyFans profile stats: {e}")
            return {}
            
    async def get_earnings_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get detailed earnings report for date range"""
        try:
            endpoint = "earnings"
            params = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat()
            }
            
            response = await self._make_request("GET", endpoint, params=params)
            
            return {
                "total_earnings": response.get("total", 0.0),
                "subscription_earnings": response.get("subscriptions", 0.0),
                "tips_earnings": response.get("tips", 0.0),
                "messages_earnings": response.get("messages", 0.0),
                "posts_earnings": response.get("posts", 0.0),
                "referrals_earnings": response.get("referrals", 0.0),
                "daily_breakdown": response.get("dailyBreakdown", []),
                "top_earning_posts": response.get("topPosts", []),
                "payment_methods": response.get("paymentMethods", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get OnlyFans earnings report: {e}")
            return {}

# Usage example
async def example_usage():
    """Example usage of OnlyFansConnector"""
    credentials = OnlyFansCredentials(
        session_token="your_session_token",
        csrf_token="your_csrf_token", 
        user_agent="your_user_agent",
        user_id="your_user_id"
    )
    
    async with OnlyFansConnector(credentials) as connector:
        # Create a post
        post = OnlyFansPost(
            content="Check out my latest content! 🔥",
            content_type=OnlyFansContentType.PHOTO,
            privacy_level=OnlyFansPrivacyLevel.SUBSCRIBERS,
            media_files=["path/to/photo.jpg"],
            price=5.00,
            tags=["premium", "exclusive"],
            allow_comments=True
        )
        
        # Publish the post
        result = await connector.publish_post(post)
        print(f"Published: {result}")
        
        if result["success"]:
            # Get analytics
            analytics = await connector.get_post_analytics(result["post_id"])
            print(f"Analytics: {analytics}")
            
            # Get subscriber stats
            subscriber_stats = await connector.get_subscriber_analytics()
            print(f"Subscribers: {subscriber_stats}")

if __name__ == "__main__":
    asyncio.run(example_usage())