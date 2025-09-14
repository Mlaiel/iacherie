"""Ainflue Platform Python SDK
Official Python SDK for the Ainflue AI-powered content protection platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import httpx
from pydantic import BaseModel, Field


__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"


# Configuration
class AinflueSdkConfig(BaseModel):
    """SDK configuration settings"""
    base_url: str = Field(default="https://api.ainflue.com", description="API base URL")
    api_key: str = Field(..., description="API key for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")


# Exceptions
class AinflueSdkException(Exception):
    """Base exception for Ainflue SDK"""
    pass


class AuthenticationError(AinflueSdkException):
    """Authentication failed"""
    pass


class APIError(AinflueSdkException):
    """API request failed"""
    def __init__(self, message -> None: str, status_code -> None: int = None, response -> None: Dict = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ValidationError(AinflueSdkException):
    """Request validation failed"""
    pass


# Response Models
class AinflueSdkResponse(BaseModel):
    """Base response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentAnalysisResult(BaseModel):
    """Content analysis result"""
    content_id: str
    analysis_type: str
    confidence: float
    fingerprint: str
    metadata: Dict[str, Any]
    timestamp: datetime


class ContentProtectionResult(BaseModel):
    """Content protection result"""
    protection_id: str
    status: str
    platforms: List[str]
    matches_found: int
    actions_taken: List[str]
    timestamp: datetime


# Main SDK Client
class AinflueSdk:
    """Main Ainflue SDK client"""
    
    def __init__(self, config -> None: AinflueSdkConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._client = None
        
        # Initialize HTTP client
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize HTTP client"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"ainflue-python-sdk/{__version__}",
            "X-SDK-Version": __version__
        }
        
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=headers,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl
        )
    
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.close()
    
    async def close(self) -> None:
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        
        for attempt in range(self.config.max_retries):
            try:
                if method.upper() == "GET":
                    response = await self._client.get(endpoint, params=params)
                elif method.upper() == "POST":
                    response = await self._client.post(endpoint, json=data, params=params)
                elif method.upper() == "PUT":
                    response = await self._client.put(endpoint, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = await self._client.delete(endpoint, params=params)
                else:
                    raise ValidationError(f"Unsupported HTTP method: {method}")
                
                # Handle HTTP errors
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key or authentication failed")
                elif response.status_code == 422:
                    raise ValidationError(f"Request validation failed: {response.text}")
                elif response.status_code >= 400:
                    raise APIError(
                        f"API request failed: {response.text}",
                        status_code=response.status_code,
                        response=response.json() if response.content else None
                    )
                
                # Parse response
                return response.json()
                
            except httpx.RequestError as e:
                if attempt == self.config.max_retries - 1:
                    raise APIError(f"Request failed after {self.config.max_retries} attempts: {str(e)}")
                
                # Wait before retry
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
    
    # Content Analysis Methods
    async def analyze_content(
        self,
        content_data: Union[str, bytes],
        content_type: str = "text",
        analysis_options: Optional[Dict] = None
    ) -> ContentAnalysisResult:
        """Analyze content for fingerprinting and protection"""
        
        payload = {
            "content_data": content_data if isinstance(content_data, str) else content_data.hex(),
            "content_type": content_type,
            "options": analysis_options or {}
        }
        
        response = await self._make_request("POST", "/api/v1/content/analyze", data=payload)
        
        return ContentAnalysisResult(**response["data"])
    
    async def upload_content(
        self,
        file_path: str,
        title: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Upload content file for analysis"""
        
        # This would typically use multipart form data
        # Simplified for this example
        payload = {
            "file_path": file_path,
            "title": title,
            "description": description,
            "tags": tags or []
        }
        
        response = await self._make_request("POST", "/api/v1/content/upload", data=payload)
        return response["data"]
    
    # Content Protection Methods
    async def protect_content(
        self,
        content_id: str,
        platforms: List[str],
        protection_options: Optional[Dict] = None
    ) -> ContentProtectionResult:
        """Enable content protection across platforms"""
        
        payload = {
            "content_id": content_id,
            "platforms": platforms,
            "options": protection_options or {}
        }
        
        response = await self._make_request("POST", "/api/v1/protection/enable", data=payload)
        
        return ContentProtectionResult(**response["data"])
    
    async def check_protection_status(self, protection_id: str) -> Dict[str, Any]:
        """Check protection status"""
        
        response = await self._make_request("GET", f"/api/v1/protection/{protection_id}")
        return response["data"]
    
    async def get_protection_matches(self, protection_id: str) -> List[Dict[str, Any]]:
        """Get detected matches for protected content"""
        
        response = await self._make_request("GET", f"/api/v1/protection/{protection_id}/matches")
        return response["data"]["matches"]
    
    # Monetization Methods
    async def create_license(
        self,
        content_id: str,
        license_type: str,
        terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create content license"""
        
        payload = {
            "content_id": content_id,
            "license_type": license_type,
            "terms": terms
        }
        
        response = await self._make_request("POST", "/api/v1/monetization/license", data=payload)
        return response["data"]
    
    async def get_revenue_stats(
        self,
        content_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get revenue statistics"""
        
        params = {}
        if content_id:
            params["content_id"] = content_id
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        
        response = await self._make_request("GET", "/api/v1/monetization/revenue", params=params)
        return response["data"]
    
    # User Management Methods
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        
        response = await self._make_request("GET", "/api/v1/user/profile")
        return response["data"]
    
    async def update_user_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        
        response = await self._make_request("PUT", "/api/v1/user/profile", data=profile_data)
        return response["data"]
    
    # Analytics Methods
    async def get_analytics(
        self,
        metric_type: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get analytics data"""
        
        params = {
            "metric_type": metric_type
        }
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if filters:
            params.update(filters)
        
        response = await self._make_request("GET", "/api/v1/analytics", params=params)
        return response["data"]
    
    # Utility Methods
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        
        response = await self._make_request("GET", "/health")
        return response


# Synchronous wrapper
class AinflueSdkSync:
    """Synchronous wrapper for Ainflue SDK"""
    
    def __init__(self, config -> None: AinflueSdkConfig) -> None:
        self.config = config
        self._async_sdk = None
    
    def _get_async_sdk(self) -> AinflueSdk:
        """Get or create async SDK instance"""
        if self._async_sdk is None:
            self._async_sdk = AinflueSdk(self.config)
        return self._async_sdk
    
    def _run_async(self, coro) -> None:
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def analyze_content(self, content_data: Union[str, bytes], content_type: str = "text", analysis_options: Optional[Dict] = None) -> ContentAnalysisResult:
        """Synchronous content analysis"""
        sdk = self._get_async_sdk()
        return self._run_async(sdk.analyze_content(content_data, content_type, analysis_options))
    
    def protect_content(self, content_id: str, platforms: List[str], protection_options: Optional[Dict] = None) -> ContentProtectionResult:
        """Synchronous content protection"""
        sdk = self._get_async_sdk()
        return self._run_async(sdk.protect_content(content_id, platforms, protection_options))
    
    def get_revenue_stats(self, content_id: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Synchronous revenue statistics"""
        sdk = self._get_async_sdk()
        return self._run_async(sdk.get_revenue_stats(content_id, date_from, date_to))
    
    def health_check(self) -> Dict[str, Any]:
        """Synchronous health check"""
        sdk = self._get_async_sdk()
        return self._run_async(sdk.health_check())
    
    def close(self) -> None:
        """Close connections"""
        if self._async_sdk:
            self._run_async(self._async_sdk.close())


# Factory functions
def create_sdk(api_key: str, base_url: str = "https://api.ainflue.com", **kwargs) -> AinflueSdk:
    """Create async SDK instance"""
    config = AinflueSdkConfig(api_key=api_key, base_url=base_url, **kwargs)
    return AinflueSdk(config)


def create_sync_sdk(api_key: str, base_url: str = "https://api.ainflue.com", **kwargs) -> AinflueSdkSync:
    """Create sync SDK instance"""
    config = AinflueSdkConfig(api_key=api_key, base_url=base_url, **kwargs)
    return AinflueSdkSync(config)


# Convenience exports
__all__ = [
    "AinflueSdk",
    "AinflueSdkSync",
    "AinflueSdkConfig",
    "AinflueSdkException",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "ContentAnalysisResult",
    "ContentProtectionResult",
    "create_sdk",
    "create_sync_sdk"
]