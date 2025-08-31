"""
LinkedIn API Integration
========================

Complete LinkedIn API integration for company pages, posts, and professional networking.
Handles posts, analytics, company page management, and networking features.

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
class LinkedInPost:
    """LinkedIn post information"""
    post_id: str
    author_urn: str
    content: str
    created_at: datetime
    updated_at: datetime
    visibility: str  # "PUBLIC", "CONNECTIONS", "LOGGED_IN_MEMBERS"
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    impression_count: int = 0
    media_urls: List[str] = None
    post_type: str = "ARTICLE"  # "ARTICLE", "IMAGE", "VIDEO", "DOCUMENT"


@dataclass
class LinkedInCompany:
    """LinkedIn company page information"""
    company_id: str
    name: str
    description: str
    industry: str
    company_size: str
    headquarters: str
    website_url: str
    logo_url: str = None
    cover_image_url: str = None
    follower_count: int = 0
    employee_count: int = 0
    specialties: List[str] = None


@dataclass
class LinkedInAnalytics:
    """LinkedIn analytics data"""
    entity_id: str  # Post or company ID
    entity_type: str  # "POST", "COMPANY"
    date_range: Dict[str, str]
    impressions: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    video_views: int = 0


@dataclass
class LinkedInProfile:
    """LinkedIn user profile information"""
    profile_id: str
    first_name: str
    last_name: str
    headline: str
    location: str
    industry: str
    summary: str = None
    profile_picture_url: str = None
    connections_count: int = 0
    current_position: str = None
    experience: List[Dict[str, Any]] = None


class LinkedInAPI:
    """LinkedIn API integration"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://api.linkedin.com/v2"
        self.api_version = "202408"  # LinkedIn API version
        
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
        rate_status = await self.rate_limiter.check_rate_limit("linkedin", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("linkedin", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{self.base_url}/{endpoint}"
        
        # Default headers
        request_headers = {
            "Authorization": f"{tokens.token_type} {tokens.access_token}",
            "Accept": "application/json",
            "LinkedIn-Version": self.api_version,
            "X-RestLi-Protocol-Version": "2.0.0"
        }
        
        if headers:
            request_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=request_headers) as response:
                    await self.rate_limiter.record_request("linkedin", endpoint, None, response.status)
                    
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
                    await self.rate_limiter.record_request("linkedin", endpoint, None, response.status)
                    
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() in ["PUT", "PATCH", "DELETE"]:
                request_headers["Content-Type"] = "application/json"
                async with self.session.request(
                    method, url, json=data, headers=request_headers, params=params
                ) as response:
                    await self.rate_limiter.record_request("linkedin", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"LinkedIn API request failed: {e}")
            raise
            
    async def get_profile(self, tokens: OAuthTokens) -> LinkedInProfile:
        """Get current user profile information"""
        
        # Get basic profile info
        fields = [
            "id", "firstName", "lastName", "headline", "location",
            "industry", "summary", "profilePicture(displayImage~:playableStreams)"
        ]
        
        params = {"projection": f"({','.join(fields)})"}
        
        response = await self._make_request("GET", "people/~", tokens, params=params)
        
        # Extract profile picture URL
        profile_picture_url = None
        if "profilePicture" in response and "displayImage~" in response["profilePicture"]:
            elements = response["profilePicture"]["displayImage~"].get("elements", [])
            if elements:
                # Get the largest image
                largest_image = max(elements, key=lambda x: x.get("data", {}).get("com.linkedin.digitalmedia.mediaartifact.StillImage", {}).get("storageSize", {}).get("width", 0))
                identifiers = largest_image.get("identifiers", [])
                if identifiers:
                    profile_picture_url = identifiers[0].get("identifier")
        
        profile = LinkedInProfile(
            profile_id=response["id"],
            first_name=response.get("firstName", {}).get("localized", {}).get("en_US", ""),
            last_name=response.get("lastName", {}).get("localized", {}).get("en_US", ""),
            headline=response.get("headline", {}).get("localized", {}).get("en_US", ""),
            location=response.get("location", {}).get("name", ""),
            industry=response.get("industry", ""),
            summary=response.get("summary", {}).get("localized", {}).get("en_US", ""),
            profile_picture_url=profile_picture_url
        )
        
        return profile
        
    async def get_company_info(self, tokens: OAuthTokens, company_id: str) -> LinkedInCompany:
        """Get company page information"""
        
        fields = [
            "id", "name", "description", "industry", "companySize",
            "headquarter", "websiteUrl", "logo(originalImage~:playableStreams)",
            "coverPhoto(originalImage~:playableStreams)", "specialties"
        ]
        
        params = {"projection": f"({','.join(fields)})"}
        
        response = await self._make_request("GET", f"companies/{company_id}", tokens, params=params)
        
        # Extract logo URL
        logo_url = None
        if "logo" in response and "originalImage~" in response["logo"]:
            elements = response["logo"]["originalImage~"].get("elements", [])
            if elements:
                identifiers = elements[0].get("identifiers", [])
                if identifiers:
                    logo_url = identifiers[0].get("identifier")
        
        # Extract cover image URL
        cover_image_url = None
        if "coverPhoto" in response and "originalImage~" in response["coverPhoto"]:
            elements = response["coverPhoto"]["originalImage~"].get("elements", [])
            if elements:
                identifiers = elements[0].get("identifiers", [])
                if identifiers:
                    cover_image_url = identifiers[0].get("identifier")
        
        company = LinkedInCompany(
            company_id=response["id"],
            name=response.get("name", {}).get("localized", {}).get("en_US", ""),
            description=response.get("description", {}).get("localized", {}).get("en_US", ""),
            industry=response.get("industry", ""),
            company_size=response.get("companySize", ""),
            headquarters=response.get("headquarter", {}).get("geographicArea", ""),
            website_url=response.get("websiteUrl", ""),
            logo_url=logo_url,
            cover_image_url=cover_image_url,
            specialties=response.get("specialties", [])
        )
        
        return company
        
    async def create_post(
        self,
        tokens: OAuthTokens,
        content: str,
        visibility: str = "PUBLIC",
        media_urls: Optional[List[str]] = None
    ) -> LinkedInPost:
        """Create a new LinkedIn post"""
        
        # Get user ID for post creation
        profile = await self.get_profile(tokens)
        author_urn = f"urn:li:person:{profile.profile_id}"
        
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        # Add media if provided
        if media_urls:
            media_list = []
            for media_url in media_urls:
                media_list.append({
                    "status": "READY",
                    "description": {
                        "text": ""
                    },
                    "media": media_url,
                    "title": {
                        "text": ""
                    }
                })
            
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = media_list
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE" if len(media_urls) == 1 else "CAROUSEL"
        
        response = await self._make_request("POST", "ugcPosts", tokens, data=post_data)
        
        post_id = response.get("id", "")
        
        post = LinkedInPost(
            post_id=post_id,
            author_urn=author_urn,
            content=content,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            visibility=visibility,
            media_urls=media_urls or []
        )
        
        logger.info(f"Created LinkedIn post: {post_id}")
        return post
        
    async def get_company_posts(
        self,
        tokens: OAuthTokens,
        company_id: str,
        count: int = 20
    ) -> List[LinkedInPost]:
        """Get posts from a company page"""
        
        params = {
            "authors": f"urn:li:organization:{company_id}",
            "count": min(count, 100),
            "sortBy": "LAST_MODIFIED"
        }
        
        response = await self._make_request("GET", "ugcPosts", tokens, params=params)
        
        posts = []
        for element in response.get("elements", []):
            post = LinkedInPost(
                post_id=element["id"],
                author_urn=element["author"],
                content=element.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("shareCommentary", {}).get("text", ""),
                created_at=datetime.fromtimestamp(element.get("created", {}).get("time", 0) / 1000),
                updated_at=datetime.fromtimestamp(element.get("lastModified", {}).get("time", 0) / 1000),
                visibility=element.get("visibility", {}).get("com.linkedin.ugc.MemberNetworkVisibility", "PUBLIC")
            )
            posts.append(post)
            
        return posts
        
    async def get_post_analytics(
        self,
        tokens: OAuthTokens,
        post_id: str
    ) -> LinkedInAnalytics:
        """Get analytics for a specific post"""
        
        # LinkedIn analytics require different endpoints and permissions
        # This is a simplified implementation
        params = {
            "q": "ugcPost",
            "ugcPost": post_id,
            "fields": "totalShareStatistics"
        }
        
        try:
            response = await self._make_request("GET", "networkSizes", tokens, params=params)
            
            stats = response.get("elements", [{}])[0].get("totalShareStatistics", {})
            
            analytics = LinkedInAnalytics(
                entity_id=post_id,
                entity_type="POST",
                date_range={"start": "", "end": ""},
                likes=stats.get("likeCount", 0),
                comments=stats.get("commentCount", 0),
                shares=stats.get("shareCount", 0),
                impressions=stats.get("impressionCount", 0)
            )
            
            return analytics
            
        except Exception as e:
            logger.warning(f"Could not get analytics for post {post_id}: {e}")
            return LinkedInAnalytics(
                entity_id=post_id,
                entity_type="POST",
                date_range={"start": "", "end": ""}
            )
            
    async def get_company_analytics(
        self,
        tokens: OAuthTokens,
        company_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> LinkedInAnalytics:
        """Get analytics for company page"""
        
        # Company analytics require special permissions
        # This is a placeholder implementation
        try:
            params = {
                "q": "organizationalEntity",
                "organizationalEntity": f"urn:li:organization:{company_id}",
                "timeGranularity": "DAY",
                "timeRange.start": int(start_date.timestamp() * 1000),
                "timeRange.end": int(end_date.timestamp() * 1000)
            }
            
            response = await self._make_request("GET", "organizationalEntityFollowerStatistics", tokens, params=params)
            
            elements = response.get("elements", [])
            total_followers = sum(elem.get("followerCountsByRegion", [{}])[0].get("followerCounts", {}).get("organicFollowerCount", 0) for elem in elements)
            
            analytics = LinkedInAnalytics(
                entity_id=company_id,
                entity_type="COMPANY",
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                },
                reach=total_followers
            )
            
            return analytics
            
        except Exception as e:
            logger.warning(f"Could not get company analytics for {company_id}: {e}")
            return LinkedInAnalytics(
                entity_id=company_id,
                entity_type="COMPANY",
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                }
            )
            
    async def search_companies(
        self,
        tokens: OAuthTokens,
        keywords: str,
        limit: int = 10
    ) -> List[LinkedInCompany]:
        """Search for companies by keywords"""
        
        params = {
            "q": "universalName",
            "keywords": keywords,
            "start": 0,
            "count": min(limit, 50)
        }
        
        try:
            response = await self._make_request("GET", "companies", tokens, params=params)
            
            companies = []
            for element in response.get("elements", []):
                company = LinkedInCompany(
                    company_id=str(element.get("id", "")),
                    name=element.get("name", {}).get("localized", {}).get("en_US", ""),
                    description=element.get("description", {}).get("localized", {}).get("en_US", ""),
                    industry=element.get("industry", ""),
                    company_size=element.get("companySize", ""),
                    headquarters=element.get("headquarter", {}).get("geographicArea", ""),
                    website_url=element.get("websiteUrl", "")
                )
                companies.append(company)
                
            return companies
            
        except Exception as e:
            logger.error(f"Company search failed: {e}")
            return []
            
    async def follow_company(self, tokens: OAuthTokens, company_id: str) -> bool:
        """Follow a company page"""
        
        profile = await self.get_profile(tokens)
        
        follow_data = {
            "followee": f"urn:li:organization:{company_id}",
            "follower": f"urn:li:person:{profile.profile_id}"
        }
        
        try:
            await self._make_request("POST", "organizationalEntityFollows", tokens, data=follow_data)
            logger.info(f"Successfully followed company: {company_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to follow company {company_id}: {e}")
            return False
            
    async def unfollow_company(self, tokens: OAuthTokens, company_id: str) -> bool:
        """Unfollow a company page"""
        
        profile = await self.get_profile(tokens)
        follow_id = f"follower={profile.profile_id}&followee=urn:li:organization:{company_id}"
        
        try:
            await self._make_request("DELETE", f"organizationalEntityFollows/{follow_id}", tokens)
            logger.info(f"Successfully unfollowed company: {company_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unfollow company {company_id}: {e}")
            return False
            
    async def get_connections(
        self,
        tokens: OAuthTokens,
        start: int = 0,
        count: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user connections"""
        
        params = {
            "q": "viewer",
            "start": start,
            "count": min(count, 100)
        }
        
        try:
            response = await self._make_request("GET", "connections", tokens, params=params)
            return response.get("elements", [])
        except Exception as e:
            logger.error(f"Failed to get connections: {e}")
            return []
            
    async def send_message(
        self,
        tokens: OAuthTokens,
        recipient_id: str,
        message_text: str
    ) -> str:
        """Send a direct message to a connection"""
        
        profile = await self.get_profile(tokens)
        
        message_data = {
            "recipients": [f"urn:li:person:{recipient_id}"],
            "subject": "Message from LinkedIn API",
            "body": message_text,
            "sender": f"urn:li:person:{profile.profile_id}"
        }
        
        try:
            response = await self._make_request("POST", "messages", tokens, data=message_data)
            message_id = response.get("id", "")
            logger.info(f"Sent message: {message_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return ""