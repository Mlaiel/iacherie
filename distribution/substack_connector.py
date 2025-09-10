"""
Substack Platform Connector
==========================

Enterprise-grade Substack API connector for Ainflue Distribution Platform.
Supports newsletter publishing, subscriber management, and analytics integration.

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
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import markdown

logger = logging.getLogger(__name__)

class SubstackPostType(Enum):
    """Substack post type options"""
    NEWSLETTER = "newsletter"
    PODCAST = "podcast" 
    THREAD = "thread"
    ARTICLE = "article"

class SubstackPublishStatus(Enum):
    """Substack publish status options"""
    PUBLISHED = "published"
    DRAFT = "draft"
    SCHEDULED = "scheduled"

class SubstackAudience(Enum):
    """Substack audience options"""
    EVERYONE = "everyone"
    ONLY_PAID = "only_paid"
    FOUNDING_MEMBERS = "founding_members"

@dataclass
class SubstackCredentials:
    """Substack API credentials"""
    api_key: str
    publication_slug: str
    username: str
    
    def __post_init__(self):
        if not all([self.api_key, self.publication_slug, self.username]):
            raise ValueError("All Substack credentials are required")

@dataclass
class SubstackPost:
    """Substack post data model"""
    title: str
    content: str
    subtitle: Optional[str] = None
    post_type: SubstackPostType = SubstackPostType.NEWSLETTER
    status: SubstackPublishStatus = SubstackPublishStatus.DRAFT
    audience: SubstackAudience = SubstackAudience.EVERYONE
    publish_at: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    podcast_url: Optional[str] = None
    podcast_duration: Optional[int] = None
    send_email: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format"""
        data = {
            "title": self.title,
            "body": self.content,
            "type": self.post_type.value,
            "post_date": self.publish_at.isoformat() if self.publish_at else None,
            "audience": self.audience.value,
            "send_email": self.send_email
        }
        
        if self.subtitle:
            data["subtitle"] = self.subtitle
        if self.cover_image_url:
            data["cover_image_url"] = self.cover_image_url
        if self.tags:
            data["tags"] = self.tags
        if self.podcast_url:
            data["podcast_url"] = self.podcast_url
        if self.podcast_duration:
            data["podcast_duration"] = self.podcast_duration
            
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class SubstackAnalytics:
    """Substack analytics data"""
    post_id: str
    views: int = 0
    opens: int = 0
    clicks: int = 0
    subscribers: int = 0
    unsubscribes: int = 0
    revenue: float = 0.0
    comments: int = 0
    likes: int = 0
    shares: int = 0
    conversion_rate: float = 0.0
    engagement_rate: float = 0.0
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SubstackAnalytics':
        """Create from API response"""
        return cls(
            post_id=data.get("id", ""),
            views=data.get("views", 0),
            opens=data.get("opens", 0),
            clicks=data.get("clicks", 0),
            subscribers=data.get("new_subscribers", 0),
            unsubscribes=data.get("unsubscribes", 0),
            revenue=data.get("revenue", 0.0),
            comments=data.get("comments", 0),
            likes=data.get("likes", 0),
            shares=data.get("shares", 0),
            conversion_rate=data.get("conversion_rate", 0.0),
            engagement_rate=data.get("engagement_rate", 0.0)
        )

class SubstackConnector:
    """
    Enterprise-grade Substack API connector
    
    Features:
    - Newsletter publishing and management
    - Subscriber analytics and insights
    - Content scheduling and automation
    - Revenue tracking and optimization
    - Cross-platform content adaptation
    """
    
    BASE_URL = "https://substack.com/api/v1"
    
    def __init__(self, credentials: SubstackCredentials):
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_remaining = 100
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
                    "Authorization": f"Bearer {self.credentials.api_key}",
                    "User-Agent": "Ainflue-Distribution/1.0",
                    "Content-Type": "application/json"
                }
            )
            logger.info("Substack connector initialized")
            
    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Substack connector disconnected")
            
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
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
            async with self.session.request(
                method, url, json=data, params=params
            ) as response:
                # Update rate limiting info
                self._rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
                reset_timestamp = response.headers.get("X-RateLimit-Reset")
                if reset_timestamp:
                    self._rate_limit_reset = datetime.fromtimestamp(
                        int(reset_timestamp), tz=timezone.utc
                    )
                
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, data, params)
                    
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Substack API request failed: {e}")
            raise Exception(f"Substack API error: {e}")
            
    async def publish_post(self, post: SubstackPost) -> Dict[str, Any]:
        """
        Publish or schedule a post on Substack
        
        Args:
            post: SubstackPost object with content and settings
            
        Returns:
            Dict with post ID and publication details
        """
        try:
            endpoint = f"publications/{self.credentials.publication_slug}/posts"
            post_data = post.to_dict()
            
            logger.info(f"Publishing Substack post: {post.title}")
            
            response = await self._make_request("POST", endpoint, post_data)
            
            result = {
                "success": True,
                "platform": "substack",
                "post_id": response.get("id"),
                "url": response.get("canonical_url"),
                "status": post.status.value,
                "published_at": response.get("post_date"),
                "subscriber_count": response.get("subscriber_count"),
                "metadata": {
                    "audience": post.audience.value,
                    "email_sent": post.send_email,
                    "type": post.post_type.value
                }
            }
            
            logger.info(f"Substack post published successfully: {result['post_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to publish Substack post: {e}")
            return {
                "success": False,
                "platform": "substack",
                "error": str(e),
                "error_type": "publication_failed"
            }
            
    async def update_post(self, post_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing post"""
        try:
            endpoint = f"publications/{self.credentials.publication_slug}/posts/{post_id}"
            
            response = await self._make_request("PUT", endpoint, updates)
            
            return {
                "success": True,
                "platform": "substack",
                "post_id": post_id,
                "updated_at": response.get("updated_at"),
                "changes": list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to update Substack post {post_id}: {e}")
            return {
                "success": False,
                "platform": "substack",
                "error": str(e),
                "post_id": post_id
            }
            
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a post"""
        try:
            endpoint = f"publications/{self.credentials.publication_slug}/posts/{post_id}"
            
            await self._make_request("DELETE", endpoint)
            
            return {
                "success": True,
                "platform": "substack",
                "post_id": post_id,
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete Substack post {post_id}: {e}")
            return {
                "success": False,
                "platform": "substack",
                "error": str(e),
                "post_id": post_id
            }
            
    async def get_post_analytics(self, post_id: str) -> SubstackAnalytics:
        """Get comprehensive analytics for a specific post"""
        try:
            endpoint = f"publications/{self.credentials.publication_slug}/posts/{post_id}/stats"
            
            response = await self._make_request("GET", endpoint)
            
            return SubstackAnalytics.from_api_response(response)
            
        except Exception as e:
            logger.error(f"Failed to get Substack analytics for post {post_id}: {e}")
            return SubstackAnalytics(post_id=post_id)
            
    async def get_subscriber_analytics(self) -> Dict[str, Any]:
        """Get subscriber analytics and growth metrics"""
        try:
            endpoint = f"publications/{self.credentials.publication_slug}/analytics/subscribers"
            
            response = await self._make_request("GET", endpoint)
            
            return {
                "total_subscribers": response.get("total_count", 0),
                "free_subscribers": response.get("free_count", 0),
                "paid_subscribers": response.get("paid_count", 0),
                "growth_rate": response.get("growth_rate", 0.0),
                "monthly_revenue": response.get("monthly_revenue", 0.0),
                "churn_rate": response.get("churn_rate", 0.0),
                "conversion_rate": response.get("conversion_rate", 0.0),
                "average_open_rate": response.get("average_open_rate", 0.0),
                "average_click_rate": response.get("average_click_rate", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Substack subscriber analytics: {e}")
            return {}
            
    async def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts with basic metrics"""
        try:
            endpoint = f"publications/{self.credentials.publication_slug}/posts"
            params = {"limit": limit, "offset": 0}
            
            response = await self._make_request("GET", endpoint, params=params)
            
            posts = []
            for post_data in response.get("posts", []):
                posts.append({
                    "id": post_data.get("id"),
                    "title": post_data.get("title"),
                    "subtitle": post_data.get("subtitle"),
                    "url": post_data.get("canonical_url"),
                    "published_at": post_data.get("post_date"),
                    "type": post_data.get("type"),
                    "audience": post_data.get("audience"),
                    "views": post_data.get("views", 0),
                    "likes": post_data.get("reactions", 0),
                    "comments": post_data.get("comment_count", 0)
                })
                
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get recent Substack posts: {e}")
            return []
            
    async def validate_credentials(self) -> bool:
        """Validate API credentials"""
        try:
            endpoint = f"publications/{self.credentials.publication_slug}"
            await self._make_request("GET", endpoint)
            return True
            
        except Exception as e:
            logger.error(f"Substack credentials validation failed: {e}")
            return False
            
    async def get_publication_stats(self) -> Dict[str, Any]:
        """Get overall publication statistics"""
        try:
            endpoint = f"publications/{self.credentials.publication_slug}/stats"
            
            response = await self._make_request("GET", endpoint)
            
            return {
                "name": response.get("name"),
                "description": response.get("description"),
                "total_posts": response.get("post_count", 0),
                "total_subscribers": response.get("subscriber_count", 0),
                "monthly_revenue": response.get("monthly_revenue", 0.0),
                "average_open_rate": response.get("average_open_rate", 0.0),
                "average_click_rate": response.get("average_click_rate", 0.0),
                "growth_rate": response.get("growth_rate", 0.0),
                "top_posts": response.get("top_posts", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get Substack publication stats: {e}")
            return {}

# Usage example
async def example_usage():
    """Example usage of SubstackConnector"""
    credentials = SubstackCredentials(
        api_key="your_substack_api_key",
        publication_slug="your-publication",
        username="your_username"
    )
    
    async with SubstackConnector(credentials) as connector:
        # Create a newsletter post
        post = SubstackPost(
            title="AI-Powered Content Distribution",
            content="This is the content of your newsletter...",
            subtitle="Revolutionary platform for creators",
            post_type=SubstackPostType.NEWSLETTER,
            status=SubstackPublishStatus.PUBLISHED,
            audience=SubstackAudience.EVERYONE,
            tags=["AI", "Content", "Distribution"],
            send_email=True
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