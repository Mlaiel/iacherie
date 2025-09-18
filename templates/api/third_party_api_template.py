"""Third Party API Template for Ainflue Platform
Enterprise-grade integration framework for external API services

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, Union, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from abc import ABC, abstractmethod

from pydantic import BaseModel, validator, Field
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.config import get_settings
from core.database import get_db_session, Base
from core.auth import APIKeyManager, OAuth2Manager
from core.rate_limiting import RateLimiter
from core.circuit_breaker import CircuitBreaker
from utils.exceptions import APIException, RateLimitException, AuthenticationException
from monitoring.api_metrics import ThirdPartyAPIMetrics

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar('T')


class APIProvider(str, Enum):
    """Supported third party API providers"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_CLOUD = "google_cloud"
    AWS = "aws"
    AZURE = "azure"
    SLACK = "slack"
    DISCORD = "discord"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    MAILCHIMP = "mailchimp"
    SENDGRID = "sendgrid"
    TWILIO = "twilio"


class AuthType(str, Enum):
    """Authentication types for APIs"""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    HMAC = "hmac"
    JWT = "jwt"
    CUSTOM = "custom"


class RequestMethod(str, Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    method: RequestMethod = RequestMethod.GET
    auth_required: bool = True
    rate_limit: Optional[int] = None
    timeout_seconds: int = 30
    retry_count: int = 3
    cache_ttl: Optional[int] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class APIProviderConfig:
    """Configuration for third party API provider"""
    provider: APIProvider
    base_url: str
    auth_type: AuthType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    default_headers: Dict[str, str] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    timeout_seconds: int = 30
    max_retries: int = 3
    circuit_breaker_enabled: bool = True
    cache_enabled: bool = True


class APIRequest(BaseModel):
    """Model for API request"""
    endpoint: str = Field(..., description="API endpoint path")
    method: RequestMethod = Field(default=RequestMethod.GET, description="HTTP method")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Request parameters")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Additional headers")
    body: Optional[Union[Dict[str, Any], str]] = Field(default=None, description="Request body")
    timeout: Optional[int] = Field(default=None, description="Request timeout in seconds")
    cache_key: Optional[str] = Field(default=None, description="Custom cache key")


class APIResponse(BaseModel):
    """Model for API response"""
    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(..., description="Response headers")
    data: Optional[Union[Dict[str, Any], List[Any], str]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")
    cached: bool = Field(default=False, description="Whether response was cached")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    retry_count: int = Field(default=0, description="Number of retries performed")


class APIUsageLog(Base):
    """Database model for API usage tracking"""
    __tablename__ = "third_party_api_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    cached = Column(Boolean, default=False, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class BaseAPIClient(ABC, Generic[T]):
    """Abstract base class for third party API clients"""

    def __init__(self, config: APIProviderConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.redis: Optional[aioredis.Redis] = None
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=APIException
        ) if config.circuit_breaker_enabled else None
        self.metrics = ThirdPartyAPIMetrics()

    async def initialize(self):
        """Initialize the API client"""
        try:
            # Create HTTP session
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.config.default_headers,
                raise_for_status=False
            )

            # Initialize Redis for caching
            if self.config.cache_enabled:
                self.redis = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )

            logger.info(f"Initialized {self.config.provider} API client")

        except Exception as e:
            logger.error(f"Failed to initialize {self.config.provider} client: {e}")
            raise APIException(f"Client initialization failed: {e}")

    async def close(self):
        """Close the API client and cleanup resources"""
        if self.session:
            await self.session.close()
        if self.redis:
            await self.redis.close()

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the API provider"""
        pass

    async def _prepare_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare request headers with authentication"""
        headers = self.config.default_headers.copy()
        
        if additional_headers:
            headers.update(additional_headers)

        # Add authentication headers based on auth type
        if self.config.auth_type == AuthType.API_KEY:
            if self.config.api_key:
                headers['Authorization'] = f'Bearer {self.config.api_key}'
        
        elif self.config.auth_type == AuthType.BEARER_TOKEN:
            if self.config.access_token:
                headers['Authorization'] = f'Bearer {self.config.access_token}'
        
        elif self.config.auth_type == AuthType.BASIC_AUTH:
            if self.config.api_key and self.config.api_secret:
                import base64
                credentials = base64.b64encode(
                    f"{self.config.api_key}:{self.config.api_secret}".encode()
                ).decode()
                headers['Authorization'] = f'Basic {credentials}'

        return headers

    async def _get_cache_key(self, request: APIRequest) -> str:
        """Generate cache key for request"""
        if request.cache_key:
            return f"api_cache:{self.config.provider}:{request.cache_key}"
        
        # Generate key from request parameters
        import hashlib
        key_data = f"{request.method}:{request.endpoint}:{json.dumps(request.parameters or {}, sort_keys=True)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"api_cache:{self.config.provider}:{key_hash}"

    async def _get_cached_response(self, cache_key: str) -> Optional[APIResponse]:
        """Get cached response if available"""
        if not self.redis or not self.config.cache_enabled:
            return None

        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                response_data = json.loads(cached_data)
                response = APIResponse(**response_data)
                response.cached = True
                return response
        except Exception as e:
            logger.warning(f"Failed to get cached response: {e}")
        
        return None

    async def _cache_response(self, cache_key: str, response: APIResponse, ttl: int):
        """Cache API response"""
        if not self.redis or not self.config.cache_enabled:
            return

        try:
            response_copy = response.copy()
            response_copy.cached = False  # Don't cache the cached flag
            await self.redis.setex(
                cache_key,
                ttl,
                json.dumps(response_copy.dict(), default=str)
            )
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")

    async def _check_rate_limit(self, endpoint: str) -> bool:
        """Check rate limits for endpoint"""
        if not self.config.rate_limits:
            return True

        rate_limit_key = f"rate_limit:{self.config.provider}:{endpoint}"
        
        # Get rate limit for this endpoint
        rate_limit = self.config.rate_limits.get(endpoint)
        if not rate_limit:
            rate_limit = self.config.rate_limits.get('default', 100)

        return await self.rate_limiter.check_rate_limit(
            rate_limit_key,
            rate_limit,
            3600  # 1 hour window
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _make_request(
        self,
        request: APIRequest,
        session: AsyncSession
    ) -> APIResponse:
        """Make HTTP request with retry logic"""
        start_time = datetime.utcnow()
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(request.endpoint):
                raise RateLimitException(f"Rate limit exceeded for {request.endpoint}")

            # Check circuit breaker
            if self.circuit_breaker and not self.circuit_breaker.can_execute():
                raise APIException("Circuit breaker is open")

            # Prepare request
            url = f"{self.config.base_url.rstrip('/')}/{request.endpoint.lstrip('/')}"
            headers = await self._prepare_headers(request.headers)
            
            # Prepare request parameters
            params = request.parameters or {}
            data = None
            json_data = None
            
            if request.body:
                if isinstance(request.body, dict):
                    json_data = request.body
                else:
                    data = request.body

            # Make request
            async with self.session.request(
                method=request.method.value,
                url=url,
                params=params,
                headers=headers,
                data=data,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=request.timeout or self.config.timeout_seconds)
            ) as response:
                
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                response_text = await response.text()
                
                # Try to parse JSON response
                response_data = None
                try:
                    response_data = await response.json()
                except:
                    if response_text:
                        response_data = response_text

                # Create API response
                api_response = APIResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    data=response_data,
                    response_time_ms=response_time,
                    error=response_text if response.status >= 400 else None
                )

                # Log usage
                await self._log_api_usage(request, api_response, session)

                # Update metrics
                await self.metrics.record_api_call(
                    self.config.provider.value,
                    request.endpoint,
                    response.status,
                    response_time
                )

                # Update circuit breaker
                if self.circuit_breaker:
                    if response.status >= 500:
                        self.circuit_breaker.record_failure()
                    else:
                        self.circuit_breaker.record_success()

                return api_response

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create error response
            api_response = APIResponse(
                status_code=500,
                headers={},
                error=str(e),
                response_time_ms=response_time
            )

            # Log usage
            await self._log_api_usage(request, api_response, session)

            # Update circuit breaker
            if self.circuit_breaker:
                self.circuit_breaker.record_failure()

            raise APIException(f"API request failed: {e}")

    async def _log_api_usage(
        self,
        request: APIRequest,
        response: APIResponse,
        session: AsyncSession
    ):
        """Log API usage for monitoring and analytics"""
        try:
            usage_log = APIUsageLog(
                provider=self.config.provider.value,
                endpoint=request.endpoint,
                method=request.method.value,
                status_code=response.status_code,
                response_time_ms=response.response_time_ms,
                cached=response.cached,
                retry_count=response.retry_count,
                error_message=response.error,
                metadata={
                    'headers': dict(response.headers),
                    'parameters': request.parameters
                }
            )
            
            session.add(usage_log)
            await session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log API usage: {e}")

    async def request(
        self,
        request: APIRequest,
        cache_ttl: Optional[int] = None
    ) -> APIResponse:
        """Make API request with caching and error handling"""
        # Check cache first
        cache_key = await self._get_cache_key(request)
        cached_response = await self._get_cached_response(cache_key)
        
        if cached_response:
            return cached_response

        # Make request
        async with get_db_session() as session:
            response = await self._make_request(request, session)
            
            # Cache successful responses
            if cache_ttl and response.status_code < 400:
                await self._cache_response(cache_key, response, cache_ttl)
            
            return response

    # Convenience methods for common HTTP operations
    async def get(
        self,
        endpoint: str,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> APIResponse:
        """Make GET request"""
        request = APIRequest(
            endpoint=endpoint,
            method=RequestMethod.GET,
            parameters=parameters,
            **kwargs
        )
        return await self.request(request)

    async def post(
        self,
        endpoint: str,
        body: Optional[Union[Dict[str, Any], str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> APIResponse:
        """Make POST request"""
        request = APIRequest(
            endpoint=endpoint,
            method=RequestMethod.POST,
            body=body,
            parameters=parameters,
            **kwargs
        )
        return await self.request(request)

    async def put(
        self,
        endpoint: str,
        body: Optional[Union[Dict[str, Any], str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> APIResponse:
        """Make PUT request"""
        request = APIRequest(
            endpoint=endpoint,
            method=RequestMethod.PUT,
            body=body,
            parameters=parameters,
            **kwargs
        )
        return await self.request(request)

    async def delete(
        self,
        endpoint: str,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> APIResponse:
        """Make DELETE request"""
        request = APIRequest(
            endpoint=endpoint,
            method=RequestMethod.DELETE,
            parameters=parameters,
            **kwargs
        )
        return await self.request(request)


class YouTubeAPIClient(BaseAPIClient):
    """YouTube Data API client"""

    def __init__(self, api_key: str):
        config = APIProviderConfig(
            provider=APIProvider.YOUTUBE,
            base_url="https://www.googleapis.com/youtube/v3",
            auth_type=AuthType.API_KEY,
            api_key=api_key,
            default_headers={
                "Accept": "application/json"
            },
            rate_limits={
                "default": 10000,  # 10,000 units per day
                "search": 100      # 100 requests per minute
            }
        )
        super().__init__(config)

    async def authenticate(self) -> bool:
        """YouTube API uses API key authentication"""
        return bool(self.config.api_key)

    async def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = "relevance"
    ) -> APIResponse:
        """Search for videos"""
        return await self.get(
            "search",
            parameters={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": max_results,
                "order": order,
                "key": self.config.api_key
            },
            cache_key=f"search:{query}:{max_results}:{order}"
        )

    async def get_video_details(self, video_id: str) -> APIResponse:
        """Get video details"""
        return await self.get(
            "videos",
            parameters={
                "part": "snippet,contentDetails,statistics",
                "id": video_id,
                "key": self.config.api_key
            },
            cache_key=f"video:{video_id}"
        )


class StripeAPIClient(BaseAPIClient):
    """Stripe API client"""

    def __init__(self, api_key: str):
        config = APIProviderConfig(
            provider=APIProvider.STRIPE,
            base_url="https://api.stripe.com/v1",
            auth_type=AuthType.BEARER_TOKEN,
            access_token=api_key,
            default_headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Stripe-Version": "2022-11-15"
            },
            rate_limits={
                "default": 100  # 100 requests per second
            }
        )
        super().__init__(config)

    async def authenticate(self) -> bool:
        """Stripe uses API key authentication"""
        return bool(self.config.access_token)

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Create a payment intent"""
        data = {
            "amount": amount,
            "currency": currency
        }
        if metadata:
            for key, value in metadata.items():
                data[f"metadata[{key}]"] = value

        return await self.post(
            "payment_intents",
            body=data
        )

    async def get_payment_intent(self, payment_intent_id: str) -> APIResponse:
        """Get payment intent details"""
        return await self.get(f"payment_intents/{payment_intent_id}")


class OpenAIAPIClient(BaseAPIClient):
    """OpenAI API client"""

    def __init__(self, api_key: str):
        config = APIProviderConfig(
            provider=APIProvider.OPENAI,
            base_url="https://api.openai.com/v1",
            auth_type=AuthType.BEARER_TOKEN,
            access_token=api_key,
            default_headers={
                "Content-Type": "application/json"
            },
            rate_limits={
                "default": 3500,  # 3500 RPM for GPT-3.5
                "completions": 200  # 200 RPM for GPT-4
            }
        )
        super().__init__(config)

    async def authenticate(self) -> bool:
        """OpenAI uses API key authentication"""
        return bool(self.config.access_token)

    async def create_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> APIResponse:
        """Create chat completion"""
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        if max_tokens:
            data["max_tokens"] = max_tokens

        return await self.post("chat/completions", body=data)


class ThirdPartyAPIManager:
    """Manager for all third party API clients"""

    def __init__(self):
        self.clients: Dict[APIProvider, BaseAPIClient] = {}
        self.redis: Optional[aioredis.Redis] = None

    async def initialize(self):
        """Initialize the API manager"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Third party API manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize API manager: {e}")
            raise

    def register_client(self, provider: APIProvider, client: BaseAPIClient):
        """Register an API client"""
        self.clients[provider] = client
        logger.info(f"Registered {provider} API client")

    async def get_client(self, provider: APIProvider) -> Optional[BaseAPIClient]:
        """Get API client for provider"""
        return self.clients.get(provider)

    async def initialize_all_clients(self):
        """Initialize all registered clients"""
        for provider, client in self.clients.items():
            try:
                await client.initialize()
                await client.authenticate()
                logger.info(f"Initialized {provider} client")
            except Exception as e:
                logger.error(f"Failed to initialize {provider} client: {e}")

    async def close_all_clients(self):
        """Close all registered clients"""
        for client in self.clients.values():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing client: {e}")


# Global API manager instance
api_manager = ThirdPartyAPIManager()

async def get_api_manager() -> ThirdPartyAPIManager:
    """Dependency to get API manager instance"""
    return api_manager


# Example usage and configuration
async def setup_api_clients():
    """Setup and configure API clients"""
    # YouTube API
    if settings.YOUTUBE_API_KEY:
        youtube_client = YouTubeAPIClient(settings.YOUTUBE_API_KEY)
        api_manager.register_client(APIProvider.YOUTUBE, youtube_client)

    # Stripe API
    if settings.STRIPE_API_KEY:
        stripe_client = StripeAPIClient(settings.STRIPE_API_KEY)
        api_manager.register_client(APIProvider.STRIPE, stripe_client)

    # OpenAI API
    if settings.OPENAI_API_KEY:
        openai_client = OpenAIAPIClient(settings.OPENAI_API_KEY)
        api_manager.register_client(APIProvider.OPENAI, openai_client)

    # Initialize all clients
    await api_manager.initialize()
    await api_manager.initialize_all_clients()


if __name__ == "__main__":
    async def main():
        await setup_api_clients()
        
        # Example usage
        youtube_client = await api_manager.get_client(APIProvider.YOUTUBE)
        if youtube_client:
            response = await youtube_client.search_videos("AI tutorial", max_results=5)
            print(f"YouTube search response: {response.status_code}")
            
        await api_manager.close_all_clients()

    asyncio.run(main())