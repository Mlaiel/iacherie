"""Facebook Rights Manager API Integration
=======================================

Facebook Rights Manager API integration for content protection and rights management.
Handles copyright claims, content monitoring, and rights administration.

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

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class FacebookRightsClaim:
    """Facebook rights claim information"""
    claim_id: str
    content_id: str
    asset_id: str
    claim_type: str  # "copyright", "trademark", "other"
    status: str  # "active", "disputed", "released"
    policy: str  # "block", "track", "monetize"
    created_time: datetime
    match_details: Dict[str, Any] = None
    claimant_name: str = None


@dataclass
class FacebookAsset:
    """Facebook asset information"""
    asset_id: str
    title: str
    asset_type: str  # "sound_recording", "musical_work", "video", "image"
    description: str = None
    metadata: Dict[str, Any] = None
    ownership_countries: List[str] = None
    rights_type: str = None


@dataclass
class FacebookPage:
    """Facebook page information"""
    page_id: str
    name: str
    category: str
    about: str = None
    fan_count: int = 0
    talking_about_count: int = 0
    website: str = None
    instagram_business_account: Dict[str, Any] = None


class FacebookRightsAPI:
    """Facebook Rights Manager API integration"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://graph.facebook.com/v18.0"
        
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
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("facebook", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("facebook", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{self.base_url}/{endpoint}"
        
        # Add access token to params
        if not params:
            params = {}
        params["access_token"] = tokens.access_token
        
        headers = {"Accept": "application/json"}
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    await self.rate_limiter.record_request("facebook", endpoint, None, response.status)
                    
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
                    await self.rate_limiter.record_request("facebook", endpoint, None, response.status)
                    
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Facebook API request failed: {e}")
            raise
            
    async def get_pages(self, tokens: OAuthTokens) -> List[FacebookPage]:
        """Get user's Facebook pages"""
        fields = [
            "id", "name", "category", "about", "fan_count", 
            "talking_about_count", "website", "instagram_business_account"
        ]
        
        params = {"fields": ",".join(fields)}
        
        response = await self._make_request("GET", "me/accounts", tokens, params=params)
        
        pages = []
        for item in response.get("data", []):
            page = FacebookPage(
                page_id=item["id"],
                name=item["name"],
                category=item.get("category", ""),
                about=item.get("about"),
                fan_count=item.get("fan_count", 0),
                talking_about_count=item.get("talking_about_count", 0),
                website=item.get("website"),
                instagram_business_account=item.get("instagram_business_account")
            )
            pages.append(page)
            
        return pages
        
    async def create_asset(
        self,
        tokens: OAuthTokens,
        title: str,
        asset_type: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ownership_countries: Optional[List[str]] = None
    ) -> str:
        """Create a rights asset"""
        
        data = {
            "title": title,
            "type": asset_type
        }
        
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        if ownership_countries:
            data["ownership_countries"] = ownership_countries
            
        response = await self._make_request("POST", "me/assets", tokens, data=data)
        
        asset_id = response.get("id")
        if asset_id:
            logger.info(f"Created asset: {asset_id}")
            
        return asset_id or ""
        
    async def get_assets(
        self,
        tokens: OAuthTokens,
        limit: int = 25,
        after: Optional[str] = None
    ) -> List[FacebookAsset]:
        """Get user's assets"""
        
        fields = [
            "id", "title", "type", "description", "metadata", 
            "ownership_countries", "rights_type"
        ]
        
        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 100)
        }
        
        if after:
            params["after"] = after
            
        response = await self._make_request("GET", "me/assets", tokens, params=params)
        
        assets = []
        for item in response.get("data", []):
            asset = FacebookAsset(
                asset_id=item["id"],
                title=item["title"],
                asset_type=item["type"],
                description=item.get("description"),
                metadata=item.get("metadata"),
                ownership_countries=item.get("ownership_countries", []),
                rights_type=item.get("rights_type")
            )
            assets.append(asset)
            
        return assets
        
    async def create_claim(
        self,
        tokens: OAuthTokens,
        asset_id: str,
        content_id: str,
        claim_type: str = "copyright",
        policy: str = "track"
    ) -> str:
        """Create a rights claim"""
        
        data = {
            "asset_id": asset_id,
            "content_id": content_id,
            "claim_type": claim_type,
            "policy": policy
        }
        
        response = await self._make_request("POST", "me/claims", tokens, data=data)
        
        claim_id = response.get("id")
        if claim_id:
            logger.info(f"Created claim: {claim_id}")
            
        return claim_id or ""
        
    async def get_claims(
        self,
        tokens: OAuthTokens,
        status: Optional[str] = None,
        limit: int = 25,
        after: Optional[str] = None
    ) -> List[FacebookRightsClaim]:
        """Get rights claims"""
        
        fields = [
            "id", "content_id", "asset_id", "claim_type", "status",
            "policy", "created_time", "match_details", "claimant_name"
        ]
        
        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 100)
        }
        
        if status:
            params["status"] = status
        if after:
            params["after"] = after
            
        response = await self._make_request("GET", "me/claims", tokens, params=params)
        
        claims = []
        for item in response.get("data", []):
            claim = FacebookRightsClaim(
                claim_id=item["id"],
                content_id=item.get("content_id", ""),
                asset_id=item.get("asset_id", ""),
                claim_type=item.get("claim_type", ""),
                status=item.get("status", ""),
                policy=item.get("policy", ""),
                created_time=datetime.fromisoformat(
                    item.get("created_time", datetime.now().isoformat())
                ),
                match_details=item.get("match_details"),
                claimant_name=item.get("claimant_name")
            )
            claims.append(claim)
            
        return claims
        
    async def update_claim_policy(
        self,
        tokens: OAuthTokens,
        claim_id: str,
        policy: str
    ) -> bool:
        """Update claim policy"""
        
        data = {"policy": policy}
        
        try:
            await self._make_request("POST", f"{claim_id}", tokens, data=data)
            logger.info(f"Updated claim policy: {claim_id} -> {policy}")
            return True
        except Exception as e:
            logger.error(f"Failed to update claim policy: {e}")
            return False
            
    async def release_claim(self, tokens: OAuthTokens, claim_id: str) -> bool:
        """Release a claim"""
        
        data = {"status": "released"}
        
        try:
            await self._make_request("POST", f"{claim_id}", tokens, data=data)
            logger.info(f"Released claim: {claim_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to release claim: {e}")
            return False
            
    async def get_page_insights(
        self,
        tokens: OAuthTokens,
        page_id: str,
        metrics: Optional[List[str]] = None,
        period: str = "day",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get Facebook page insights"""
        
        default_metrics = [
            "page_impressions", "page_reach", "page_engaged_users",
            "page_post_engagements", "page_fans", "page_fan_adds"
        ]
        
        params = {
            "metric": ",".join(metrics or default_metrics),
            "period": period
        }
        
        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())
            
        return await self._make_request("GET", f"{page_id}/insights", tokens, params=params)
        
    async def get_post_insights(
        self,
        tokens: OAuthTokens,
        post_id: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get insights for a specific post"""
        
        default_metrics = [
            "post_impressions", "post_reach", "post_engaged_users",
            "post_reactions_like_total", "post_reactions_love_total",
            "post_reactions_wow_total", "post_clicks", "post_video_views"
        ]
        
        params = {"metric": ",".join(metrics or default_metrics)}
        
        return await self._make_request("GET", f"{post_id}/insights", tokens, params=params)
        
    async def monitor_content(
        self,
        tokens: OAuthTokens,
        asset_id: str,
        monitoring_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up content monitoring"""
        
        data = {
            "asset_id": asset_id,
            "monitoring_rules": monitoring_rules
        }
        
        return await self._make_request("POST", "me/content_monitoring", tokens, data=data)
        
    async def get_copyright_matches(
        self,
        tokens: OAuthTokens,
        asset_id: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Get copyright matches"""
        
        params = {"limit": min(limit, 100)}
        
        if asset_id:
            params["asset_id"] = asset_id
            
        response = await self._make_request("GET", "me/copyright_matches", tokens, params=params)
        
        return response.get("data", [])
        
    async def submit_takedown_request(
        self,
        tokens: OAuthTokens,
        content_url: str,
        copyright_reason: str,
        asset_id: Optional[str] = None
    ) -> str:
        """Submit a takedown request"""
        
        data = {
            "content_url": content_url,
            "copyright_reason": copyright_reason
        }
        
        if asset_id:
            data["asset_id"] = asset_id
            
        response = await self._make_request("POST", "me/takedown_requests", tokens, data=data)
        
        request_id = response.get("id")
        if request_id:
            logger.info(f"Submitted takedown request: {request_id}")
            
        return request_id or ""