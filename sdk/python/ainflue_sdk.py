"""
Ainflue Platform Python SDK
Official Python client library for the Ainflue AI Platform API.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

# SDK version
__version__ = "1.0.0"

class AinflueSdkException(Exception):
    """Base exception for Ainflue SDK."""
    pass

class AuthenticationError(AinflueSdkException):
    """Authentication failed."""
    pass

class RateLimitError(AinflueSdkException):
    """Rate limit exceeded."""
    pass

class ApiError(AinflueSdkException):
    """API error response."""
    pass

class Environment(Enum):
    """API environment."""
    PRODUCTION = "https://api.ainflue.com/v1"
    STAGING = "https://staging-api.ainflue.com/v1"
    DEVELOPMENT = "http://localhost:8000/api/v1"

@dataclass
class SdkConfig:
    """SDK configuration."""
    api_key: str
    base_url: str = Environment.PRODUCTION.value
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = f"Ainflue-Python-SDK/{__version__}"
    debug: bool = False

class AinflueSdk:
    """Official Ainflue Platform Python SDK.
    
    Provides easy access to all Ainflue AI Platform APIs including:
    - Content protection and fingerprinting
    - AI-powered content analysis
    - Monetization and payment processing
    - Analytics and reporting
    - Multi-language support
    
    Example:
        ```python
        from ainflue_sdk import AinflueSdk
        
        # Initialize SDK
        sdk = AinflueSdk(api_key="your-api-key")
        
        # Analyze content
        result = await sdk.content.analyze("path/to/content.mp4")
        print(result)
        ```
    """
    
    def __init__(self, api_key: str, config: Optional[SdkConfig] = None):
        """Initialize the Ainflue SDK.
        
        Args:
            api_key: Your Ainflue API key
            config: Optional SDK configuration
        """
        self.config = config or SdkConfig(api_key=api_key)
        self.config.api_key = api_key
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # Initialize API clients
        self.content = ContentApi(self)
        self.ai_agents = AIAgentsApi(self)
        self.monetization = MonetizationApi(self)
        self.analytics = AnalyticsApi(self)
        self.auth = AuthApi(self)
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._auth_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is initialized."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers={
                    "User-Agent": self.config.user_agent,
                    "Content-Type": "application/json"
                }
            )
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        auth_required: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            files: Files to upload
            auth_required: Whether authentication is required
            
        Returns:
            Dict containing API response
            
        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            ApiError: For other API errors
        """
        await self._ensure_session()
        
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {}
        
        # Add authentication
        if auth_required:
            await self._ensure_auth()
            if self._auth_token:
                headers["Authorization"] = f"Bearer {self._auth_token}"
            else:
                headers["X-API-Key"] = self.config.api_key
        
        # Prepare request data
        request_kwargs = {
            "headers": headers,
            "params": params
        }
        
        if files:
            # For file uploads, use FormData
            form_data = aiohttp.FormData()
            for key, value in (data or {}).items():
                form_data.add_field(key, value)
            for key, file_data in files.items():
                form_data.add_field(key, file_data["content"], filename=file_data["filename"])
            request_kwargs["data"] = form_data
        elif data:
            request_kwargs["json"] = data
        
        # Make request with retries
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                async with self._session.request(method, url, **request_kwargs) as response:
                    response_data = await self._handle_response(response)
                    return response_data
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.debug(f"Request failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"Request failed after {self.config.max_retries} retries: {e}")
        
        raise AinflueSdkException(f"Request failed: {last_exception}")
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle HTTP response and errors."""
        try:
            response_data = await response.json()
        except json.JSONDecodeError:
            response_data = {"message": await response.text()}
        
        if response.status == 200:
            return response_data
        elif response.status == 401:
            raise AuthenticationError(response_data.get("message", "Authentication failed"))
        elif response.status == 429:
            raise RateLimitError(response_data.get("message", "Rate limit exceeded"))
        elif response.status >= 400:
            raise ApiError(f"API error {response.status}: {response_data.get('message', 'Unknown error')}")
        else:
            return response_data
    
    async def _ensure_auth(self):
        """Ensure valid authentication token."""
        if self._auth_token and self._token_expires and datetime.now() < self._token_expires:
            return  # Token is still valid
        
        # Token expired or doesn't exist, refresh it
        try:
            auth_response = await self._make_request(
                "POST",
                "/auth/token",
                data={"api_key": self.config.api_key},
                auth_required=False
            )
            
            self._auth_token = auth_response["access_token"]
            expires_in = auth_response.get("expires_in", 3600)
            self._token_expires = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 minute early
            
        except Exception as e:
            self.logger.warning(f"Failed to refresh token: {e}")
            # Fall back to API key authentication

class BaseApi:
    """Base class for API clients."""
    
    def __init__(self, sdk: AinflueSdk):
        self.sdk = sdk

class ContentApi(BaseApi):
    """Content protection and analysis API."""
    
    async def analyze(
        self,
        content_path: str,
        analysis_type: str = "comprehensive",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze content for protection and insights.
        
        Args:
            content_path: Path to content file
            analysis_type: Type of analysis (basic, comprehensive, deep)
            options: Additional analysis options
            
        Returns:
            Dict containing analysis results
        """
        with open(content_path, 'rb') as f:
            content_data = f.read()
        
        files = {
            "content": {
                "content": content_data,
                "filename": content_path.split('/')[-1]
            }
        }
        
        data = {
            "analysis_type": analysis_type,
            **(options or {})
        }
        
        return await self.sdk._make_request("POST", "/content/analyze", data=data, files=files)
    
    async def fingerprint(self, content_path: str) -> Dict[str, Any]:
        """Generate content fingerprint.
        
        Args:
            content_path: Path to content file
            
        Returns:
            Dict containing fingerprint data
        """
        return await self.analyze(content_path, analysis_type="fingerprint")
    
    async def check_copyright(self, content_path: str) -> Dict[str, Any]:
        """Check content for copyright violations.
        
        Args:
            content_path: Path to content file
            
        Returns:
            Dict containing copyright check results
        """
        return await self.analyze(content_path, analysis_type="copyright")

class AIAgentsApi(BaseApi):
    """AI Agents API for intelligent processing."""
    
    async def chat(
        self,
        agent_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Chat with an AI agent.
        
        Args:
            agent_name: Name of the agent to chat with
            message: Your message to the agent
            context: Optional context information
            parameters: Optional parameters for the agent
            
        Returns:
            Dict containing agent response
        """
        data = {
            "message": message,
            "context": context or {},
            "parameters": parameters or {}
        }
        
        return await self.sdk._make_request("POST", f"/agents/{agent_name}/chat", data=data)
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List available AI agents.
        
        Returns:
            List of available agents and their capabilities
        """
        response = await self.sdk._make_request("GET", "/agents")
        return response.get("agents", [])
    
    async def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get information about a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dict containing agent information and capabilities
        """
        return await self.sdk._make_request("GET", f"/agents/{agent_name}")

class MonetizationApi(BaseApi):
    """Monetization and payment processing API."""
    
    async def create_payment(
        self,
        amount: float,
        currency: str = "USD",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payment transaction.
        
        Args:
            amount: Payment amount
            currency: Currency code (USD, EUR, etc.)
            description: Payment description
            metadata: Additional metadata
            
        Returns:
            Dict containing payment information
        """
        data = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "metadata": metadata or {}
        }
        
        return await self.sdk._make_request("POST", "/monetization/payments", data=data)
    
    async def get_revenue_analytics(
        self,
        start_date: str,
        end_date: str,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """Get revenue analytics for a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            granularity: Data granularity (daily, weekly, monthly)
            
        Returns:
            Dict containing revenue analytics
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "granularity": granularity
        }
        
        return await self.sdk._make_request("GET", "/monetization/analytics", params=params)

class AnalyticsApi(BaseApi):
    """Analytics and reporting API."""
    
    async def get_performance_metrics(
        self,
        metric_type: str = "all",
        time_period: str = "7d"
    ) -> Dict[str, Any]:
        """Get performance metrics.
        
        Args:
            metric_type: Type of metrics (all, content, revenue, users)
            time_period: Time period (1h, 1d, 7d, 30d)
            
        Returns:
            Dict containing performance metrics
        """
        params = {
            "metric_type": metric_type,
            "time_period": time_period
        }
        
        return await self.sdk._make_request("GET", "/analytics/metrics", params=params)
    
    async def generate_report(
        self,
        report_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a custom report.
        
        Args:
            report_type: Type of report to generate
            parameters: Report parameters
            
        Returns:
            Dict containing report data or generation status
        """
        data = {
            "report_type": report_type,
            "parameters": parameters or {}
        }
        
        return await self.sdk._make_request("POST", "/analytics/reports", data=data)

class AuthApi(BaseApi):
    """Authentication API."""
    
    async def validate_api_key(self) -> Dict[str, Any]:
        """Validate the current API key.
        
        Returns:
            Dict containing validation results and user info
        """
        return await self.sdk._make_request("GET", "/auth/validate")
    
    async def get_usage_limits(self) -> Dict[str, Any]:
        """Get current usage limits and remaining quota.
        
        Returns:
            Dict containing usage limits and current usage
        """
        return await self.sdk._make_request("GET", "/auth/limits")

# Convenience functions for quick access
async def analyze_content(api_key: str, content_path: str, **kwargs) -> Dict[str, Any]:
    """Quick content analysis function.
    
    Args:
        api_key: Your Ainflue API key
        content_path: Path to content file
        **kwargs: Additional options
        
    Returns:
        Dict containing analysis results
    """
    async with AinflueSdk(api_key) as sdk:
        return await sdk.content.analyze(content_path, **kwargs)

async def chat_with_agent(
    api_key: str,
    agent_name: str,
    message: str,
    **kwargs
) -> Dict[str, Any]:
    """Quick agent chat function.
    
    Args:
        api_key: Your Ainflue API key
        agent_name: Name of the agent
        message: Your message
        **kwargs: Additional options
        
    Returns:
        Dict containing agent response
    """
    async with AinflueSdk(api_key) as sdk:
        return await sdk.ai_agents.chat(agent_name, message, **kwargs)

# Export public API
__all__ = [
    "AinflueSdk",
    "SdkConfig",
    "Environment",
    "AinflueSdkException",
    "AuthenticationError",
    "RateLimitError",
    "ApiError",
    "analyze_content",
    "chat_with_agent"
]