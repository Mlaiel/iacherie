"""
DMCA Services API Integration
============================

Integration with DMCA protection services for automated takedown requests.
Handles copyright protection, violation detection, and takedown management.

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

from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class DMCARequest:
    """DMCA takedown request information"""
    request_id: str
    content_url: str
    infringing_url: str
    copyright_holder: str
    description: str
    status: str  # "pending", "submitted", "processed", "completed", "failed"
    created_at: datetime
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    platform: str = None
    evidence_urls: List[str] = None


@dataclass
class ContentMonitor:
    """Content monitoring configuration"""
    monitor_id: str
    content_title: str
    content_type: str  # "video", "audio", "image", "text"
    keywords: List[str]
    platforms: List[str]
    created_at: datetime
    is_active: bool = True
    detection_count: int = 0


@dataclass
class InfringementAlert:
    """Copyright infringement alert"""
    alert_id: str
    monitor_id: str
    infringing_url: str
    platform: str
    detected_at: datetime
    similarity_score: float
    status: str  # "new", "reviewing", "confirmed", "false_positive", "taken_down"
    metadata: Dict[str, Any] = None


class DMCAServicesAPI:
    """DMCA Services API integration"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None, api_key: Optional[str] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.api_key = api_key
        
        # Multiple DMCA service endpoints
        self.services = {
            "dmca_com": {
                "base_url": "https://api.dmca.com/v1",
                "auth_header": "X-API-Key"
            },
            "copyright_bot": {
                "base_url": "https://api.copyrightbot.com/v1", 
                "auth_header": "Authorization"
            },
            "brand_shield": {
                "base_url": "https://api.brandshield.com/v1",
                "auth_header": "X-API-Key"
            }
        }
        
        self.default_service = "dmca_com"
        
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
        data: Optional[Dict[str, Any]] = None,
        service: str = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        
        service = service or self.default_service
        service_config = self.services.get(service)
        
        if not service_config:
            raise ValueError(f"Unknown DMCA service: {service}")
            
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("dmca", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("dmca", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{service_config['base_url']}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add authentication
        if self.api_key:
            auth_header = service_config["auth_header"]
            if auth_header == "Authorization":
                headers[auth_header] = f"Bearer {self.api_key}"
            else:
                headers[auth_header] = self.api_key
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    await self.rate_limiter.record_request("dmca", endpoint, None, response.status)
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        raise Exception("Rate limit exceeded")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers, params=params) as response:
                    await self.rate_limiter.record_request("dmca", endpoint, None, response.status)
                    
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() in ["PUT", "PATCH", "DELETE"]:
                async with self.session.request(
                    method, url, json=data, headers=headers, params=params
                ) as response:
                    await self.rate_limiter.record_request("dmca", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"DMCA API request failed: {e}")
            raise
            
    async def submit_takedown_request(
        self,
        content_url: str,
        infringing_url: str,
        copyright_holder: str,
        description: str,
        evidence_urls: Optional[List[str]] = None,
        platform: Optional[str] = None,
        service: str = None
    ) -> DMCARequest:
        """Submit a DMCA takedown request"""
        
        data = {
            "content_url": content_url,
            "infringing_url": infringing_url,
            "copyright_holder": copyright_holder,
            "description": description,
            "platform": platform,
            "evidence_urls": evidence_urls or []
        }
        
        response = await self._make_request("POST", "takedown-requests", data=data, service=service)
        
        request = DMCARequest(
            request_id=response.get("id", ""),
            content_url=content_url,
            infringing_url=infringing_url,
            copyright_holder=copyright_holder,
            description=description,
            status=response.get("status", "pending"),
            created_at=datetime.now(),
            platform=platform,
            evidence_urls=evidence_urls
        )
        
        logger.info(f"Submitted DMCA takedown request: {request.request_id}")
        return request
        
    async def get_takedown_status(
        self,
        request_id: str,
        service: str = None
    ) -> DMCARequest:
        """Get status of a takedown request"""
        
        response = await self._make_request("GET", f"takedown-requests/{request_id}", service=service)
        
        request = DMCARequest(
            request_id=response["id"],
            content_url=response["content_url"],
            infringing_url=response["infringing_url"],
            copyright_holder=response["copyright_holder"],
            description=response["description"],
            status=response["status"],
            created_at=datetime.fromisoformat(response["created_at"]),
            submitted_at=datetime.fromisoformat(response["submitted_at"]) if response.get("submitted_at") else None,
            completed_at=datetime.fromisoformat(response["completed_at"]) if response.get("completed_at") else None,
            platform=response.get("platform"),
            evidence_urls=response.get("evidence_urls", [])
        )
        
        return request
        
    async def list_takedown_requests(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        service: str = None
    ) -> List[DMCARequest]:
        """List takedown requests"""
        
        params = {
            "limit": min(limit, 100),
            "offset": offset
        }
        
        if status:
            params["status"] = status
        if platform:
            params["platform"] = platform
            
        response = await self._make_request("GET", "takedown-requests", params=params, service=service)
        
        requests = []
        for item in response.get("data", []):
            request = DMCARequest(
                request_id=item["id"],
                content_url=item["content_url"],
                infringing_url=item["infringing_url"],
                copyright_holder=item["copyright_holder"],
                description=item["description"],
                status=item["status"],
                created_at=datetime.fromisoformat(item["created_at"]),
                submitted_at=datetime.fromisoformat(item["submitted_at"]) if item.get("submitted_at") else None,
                completed_at=datetime.fromisoformat(item["completed_at"]) if item.get("completed_at") else None,
                platform=item.get("platform"),
                evidence_urls=item.get("evidence_urls", [])
            )
            requests.append(request)
            
        return requests
        
    async def create_content_monitor(
        self,
        content_title: str,
        content_type: str,
        keywords: List[str],
        platforms: List[str],
        service: str = None
    ) -> ContentMonitor:
        """Create a content monitoring job"""
        
        data = {
            "content_title": content_title,
            "content_type": content_type,
            "keywords": keywords,
            "platforms": platforms
        }
        
        response = await self._make_request("POST", "monitors", data=data, service=service)
        
        monitor = ContentMonitor(
            monitor_id=response.get("id", ""),
            content_title=content_title,
            content_type=content_type,
            keywords=keywords,
            platforms=platforms,
            created_at=datetime.now(),
            is_active=response.get("is_active", True)
        )
        
        logger.info(f"Created content monitor: {monitor.monitor_id}")
        return monitor
        
    async def get_content_monitors(
        self,
        is_active: Optional[bool] = None,
        service: str = None
    ) -> List[ContentMonitor]:
        """Get content monitors"""
        
        params = {}
        if is_active is not None:
            params["is_active"] = is_active
            
        response = await self._make_request("GET", "monitors", params=params, service=service)
        
        monitors = []
        for item in response.get("data", []):
            monitor = ContentMonitor(
                monitor_id=item["id"],
                content_title=item["content_title"],
                content_type=item["content_type"],
                keywords=item["keywords"],
                platforms=item["platforms"],
                created_at=datetime.fromisoformat(item["created_at"]),
                is_active=item.get("is_active", True),
                detection_count=item.get("detection_count", 0)
            )
            monitors.append(monitor)
            
        return monitors
        
    async def get_infringement_alerts(
        self,
        monitor_id: Optional[str] = None,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50,
        service: str = None
    ) -> List[InfringementAlert]:
        """Get infringement alerts"""
        
        params = {"limit": min(limit, 100)}
        
        if monitor_id:
            params["monitor_id"] = monitor_id
        if status:
            params["status"] = status
        if platform:
            params["platform"] = platform
            
        response = await self._make_request("GET", "alerts", params=params, service=service)
        
        alerts = []
        for item in response.get("data", []):
            alert = InfringementAlert(
                alert_id=item["id"],
                monitor_id=item["monitor_id"],
                infringing_url=item["infringing_url"],
                platform=item["platform"],
                detected_at=datetime.fromisoformat(item["detected_at"]),
                similarity_score=item.get("similarity_score", 0.0),
                status=item.get("status", "new"),
                metadata=item.get("metadata", {})
            )
            alerts.append(alert)
            
        return alerts
        
    async def update_alert_status(
        self,
        alert_id: str,
        status: str,
        service: str = None
    ) -> bool:
        """Update infringement alert status"""
        
        data = {"status": status}
        
        try:
            await self._make_request("PATCH", f"alerts/{alert_id}", data=data, service=service)
            logger.info(f"Updated alert status: {alert_id} -> {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update alert status: {e}")
            return False
            
    async def create_takedown_from_alert(
        self,
        alert_id: str,
        copyright_holder: str,
        description: str,
        service: str = None
    ) -> DMCARequest:
        """Create a takedown request from an infringement alert"""
        
        # First get alert details
        alert_response = await self._make_request("GET", f"alerts/{alert_id}", service=service)
        
        # Create takedown request
        data = {
            "alert_id": alert_id,
            "copyright_holder": copyright_holder,
            "description": description
        }
        
        response = await self._make_request("POST", "alerts/takedown", data=data, service=service)
        
        request = DMCARequest(
            request_id=response.get("id", ""),
            content_url=alert_response.get("original_url", ""),
            infringing_url=alert_response.get("infringing_url", ""),
            copyright_holder=copyright_holder,
            description=description,
            status=response.get("status", "pending"),
            created_at=datetime.now(),
            platform=alert_response.get("platform")
        )
        
        logger.info(f"Created takedown from alert: {request.request_id}")
        return request
        
    async def bulk_takedown_request(
        self,
        requests: List[Dict[str, Any]],
        service: str = None
    ) -> List[DMCARequest]:
        """Submit multiple takedown requests in bulk"""
        
        data = {"requests": requests}
        
        response = await self._make_request("POST", "takedown-requests/bulk", data=data, service=service)
        
        dmca_requests = []
        for item in response.get("data", []):
            request = DMCARequest(
                request_id=item.get("id", ""),
                content_url=item.get("content_url", ""),
                infringing_url=item.get("infringing_url", ""),
                copyright_holder=item.get("copyright_holder", ""),
                description=item.get("description", ""),
                status=item.get("status", "pending"),
                created_at=datetime.now(),
                platform=item.get("platform")
            )
            dmca_requests.append(request)
            
        logger.info(f"Submitted {len(dmca_requests)} bulk takedown requests")
        return dmca_requests
        
    async def get_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        service: str = None
    ) -> Dict[str, Any]:
        """Get DMCA service analytics"""
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        return await self._make_request("GET", "analytics", params=params, service=service)
        
    async def pause_monitor(self, monitor_id: str, service: str = None) -> bool:
        """Pause a content monitor"""
        
        data = {"is_active": False}
        
        try:
            await self._make_request("PATCH", f"monitors/{monitor_id}", data=data, service=service)
            logger.info(f"Paused monitor: {monitor_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause monitor: {e}")
            return False
            
    async def resume_monitor(self, monitor_id: str, service: str = None) -> bool:
        """Resume a content monitor"""
        
        data = {"is_active": True}
        
        try:
            await self._make_request("PATCH", f"monitors/{monitor_id}", data=data, service=service)
            logger.info(f"Resumed monitor: {monitor_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume monitor: {e}")
            return False