"""Facebook Marketing API Integration
==================================

Complete Facebook Marketing API integration for advertising and business management.
Handles campaigns, audiences, insights, and page management.

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
import os

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class FacebookCampaign:
    """Facebook campaign information"""
    campaign_id: str
    name: str
    objective: str
    status: str  # "ACTIVE", "PAUSED", "DELETED"
    daily_budget: float = 0
    lifetime_budget: float = 0
    created_time: datetime = None
    start_time: datetime = None
    stop_time: datetime = None


@dataclass
class FacebookAdSet:
    """Facebook ad set information"""
    adset_id: str
    campaign_id: str
    name: str
    status: str
    targeting: Dict[str, Any] = None
    daily_budget: float = 0
    bid_amount: int = 0
    billing_event: str = None
    optimization_goal: str = None


@dataclass
class FacebookAd:
    """Facebook ad information"""
    ad_id: str
    adset_id: str
    name: str
    status: str
    creative: Dict[str, Any] = None
    tracking_specs: List[Dict[str, Any]] = None


@dataclass
class FacebookInsights:
    """Facebook insights data"""
    date_start: str
    date_stop: str
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    reach: int = 0
    frequency: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    cpm: float = 0.0
    cpp: float = 0.0


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
    phone: str = None
    emails: List[str] = None


class FacebookMarketingAPI:
    """Facebook Marketing API integration"""
    
    def __init__(self, access_token: str = None, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.access_token = access_token or os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.api_version = os.getenv('FACEBOOK_API_VERSION', 'v18.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
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
        params["access_token"] = self.access_token
        
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
                        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {e}")
            raise Exception(f"Network error: {e}")
            
    # =================== PAGE MANAGEMENT ===================
    
    async def get_page_info(self, page_id: str) -> FacebookPage:
        """Get Facebook page information"""
        
        fields = [
            "id", "name", "category", "about", "fan_count", 
            "talking_about_count", "website", "phone", "emails"
        ]
        
        params = {"fields": ",".join(fields)}
        response = await self._make_request("GET", page_id, params)
        
        return FacebookPage(
            page_id=response.get("id"),
            name=response.get("name"),
            category=response.get("category"),
            about=response.get("about"),
            fan_count=response.get("fan_count", 0),
            talking_about_count=response.get("talking_about_count", 0),
            website=response.get("website"),
            phone=response.get("phone"),
            emails=response.get("emails", [])
        )
    
    async def get_page_posts(self, page_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get page posts"""
        
        fields = [
            "id", "message", "story", "created_time", "updated_time",
            "likes.summary(true)", "comments.summary(true)", "shares"
        ]
        
        params = {
            "fields": ",".join(fields),
            "limit": limit
        }
        
        response = await self._make_request("GET", f"{page_id}/posts", params)
        return response.get("data", [])
    
    # =================== INSIGHTS & ANALYTICS ===================
    
    async def get_page_insights(
        self,
        page_id: str,
        metrics: List[str],
        period: str = "day",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get page insights"""
        
        params = {
            "metric": ",".join(metrics),
            "period": period
        }
        
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
            
        response = await self._make_request("GET", f"{page_id}/insights", params)
        return response.get("data", [])
    
    async def get_post_insights(
        self,
        post_id: str,
        metrics: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get post insights"""
        
        if not metrics:
            metrics = [
                "post_impressions", "post_reach", "post_clicks",
                "post_reactions_by_type_total", "post_video_views"
            ]
        
        params = {"metric": ",".join(metrics)}
        response = await self._make_request("GET", f"{post_id}/insights", params)
        return response.get("data", [])
    
    # =================== CAMPAIGN MANAGEMENT ===================
    
    async def get_campaigns(self, account_id: str) -> List[FacebookCampaign]:
        """Get advertising campaigns"""
        
        fields = [
            "id", "name", "objective", "status", "daily_budget",
            "lifetime_budget", "created_time", "start_time", "stop_time"
        ]
        
        params = {"fields": ",".join(fields)}
        response = await self._make_request("GET", f"act_{account_id}/campaigns", params)
        
        campaigns = []
        for campaign_data in response.get("data", []):
            campaigns.append(FacebookCampaign(
                campaign_id=campaign_data.get("id"),
                name=campaign_data.get("name"),
                objective=campaign_data.get("objective"),
                status=campaign_data.get("status"),
                daily_budget=float(campaign_data.get("daily_budget", 0)),
                lifetime_budget=float(campaign_data.get("lifetime_budget", 0)),
                created_time=datetime.fromisoformat(campaign_data.get("created_time", "").replace("Z", "+00:00")) if campaign_data.get("created_time") else None
            ))
        
        return campaigns
    
    async def get_campaign_insights(
        self,
        campaign_id: str,
        date_preset: str = "last_7_days"
    ) -> FacebookInsights:
        """Get campaign insights"""
        
        fields = [
            "impressions", "clicks", "spend", "reach", "frequency",
            "ctr", "cpc", "cpm", "cpp"
        ]
        
        params = {
            "fields": ",".join(fields),
            "date_preset": date_preset
        }
        
        response = await self._make_request("GET", f"{campaign_id}/insights", params)
        
        if response.get("data"):
            data = response["data"][0]
            return FacebookInsights(
                date_start=data.get("date_start"),
                date_stop=data.get("date_stop"),
                impressions=int(data.get("impressions", 0)),
                clicks=int(data.get("clicks", 0)),
                spend=float(data.get("spend", 0.0)),
                reach=int(data.get("reach", 0)),
                frequency=float(data.get("frequency", 0.0)),
                ctr=float(data.get("ctr", 0.0)),
                cpc=float(data.get("cpc", 0.0)),
                cpm=float(data.get("cpm", 0.0)),
                cpp=float(data.get("cpp", 0.0))
            )
        
        return FacebookInsights(date_start="", date_stop="")
    
    # =================== AD MANAGEMENT ===================
    
    async def create_campaign(
        self,
        account_id: str,
        name: str,
        objective: str,
        status: str = "PAUSED"
    ) -> str:
        """Create a new campaign"""
        
        data = {
            "name": name,
            "objective": objective,
            "status": status
        }
        
        response = await self._make_request("POST", f"act_{account_id}/campaigns", data=data)
        return response.get("id")
    
    async def create_adset(
        self,
        account_id: str,
        campaign_id: str,
        name: str,
        daily_budget: int,
        targeting: Dict[str, Any],
        billing_event: str = "IMPRESSIONS",
        optimization_goal: str = "REACH"
    ) -> str:
        """Create a new ad set"""
        
        data = {
            "name": name,
            "campaign_id": campaign_id,
            "daily_budget": daily_budget,
            "targeting": targeting,
            "billing_event": billing_event,
            "optimization_goal": optimization_goal,
            "status": "PAUSED"
        }
        
        response = await self._make_request("POST", f"act_{account_id}/adsets", data=data)
        return response.get("id")
    
    # =================== AUDIENCE MANAGEMENT ===================
    
    async def get_custom_audiences(self, account_id: str) -> List[Dict[str, Any]]:
        """Get custom audiences"""
        
        fields = ["id", "name", "description", "approximate_count", "time_created"]
        params = {"fields": ",".join(fields)}
        
        response = await self._make_request("GET", f"act_{account_id}/customaudiences", params)
        return response.get("data", [])
    
    async def create_custom_audience(
        self,
        account_id: str,
        name: str,
        description: str,
        subtype: str = "CUSTOM"
    ) -> str:
        """Create a custom audience"""
        
        data = {
            "name": name,
            "description": description,
            "subtype": subtype
        }
        
        response = await self._make_request("POST", f"act_{account_id}/customaudiences", data=data)
        return response.get("id")
    
    # =================== UTILITY METHODS ===================
    
    async def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = await self._make_request("GET", "me", {"fields": "id,name"})
            return "id" in response
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def get_user_accounts(self) -> List[Dict[str, Any]]:
        """Get user's ad accounts"""
        
        fields = ["id", "name", "account_status", "currency", "timezone_name"]
        params = {"fields": ",".join(fields)}
        
        response = await self._make_request("GET", "me/adaccounts", params)
        return response.get("data", [])