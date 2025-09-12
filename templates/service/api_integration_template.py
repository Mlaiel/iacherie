"""{{service_name}} API Integration Service for Ainflue Platform
{{service_description}}

Enterprise-grade API integration service with comprehensive external API management,
rate limiting, circuit breaker patterns, retry logic, and monitoring.

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Role: Backend Senior + Integration Architect
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Set, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import time
from urllib.parse import urljoin, urlparse

import aiohttp
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from pydantic import BaseModel, Field, validator, HttpUrl, AnyHttpUrl
from fastapi import HTTPException
import jwt
from cryptography.fernet import Fernet
import backoff

from core.base_service import BaseService
from core.config import get_settings
from core.database import get_async_session
from core.exceptions import ServiceException, ValidationError, RateLimitError
from models.integration import (
    ApiIntegration, ApiEndpoint, ApiKey, ApiRequest, ApiResponse,
    WebhookSubscription, ApiQuota, RateLimitRule
)
from services.analytics_service import AnalyticsService
from utils.validation import validate_api_data
from utils.encryption import encrypt_sensitive_data, decrypt_sensitive_data
from monitoring.api_metrics import ApiMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class HttpMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(Enum):
    """API authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    SIGNATURE = "signature"
    CUSTOM = "custom"


class IntegrationStatus(Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class PlatformType(Enum):
    """Supported platform types"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CUSTOM = "custom"


# Pydantic Models for Request/Response
class CreateIntegrationRequest(BaseModel):
    """Request model for creating API integration"""
    name: str = Field(..., description="Integration name")
    platform_type: PlatformType = Field(..., description="Platform type")
    base_url: AnyHttpUrl = Field(..., description="Base API URL")
    auth_type: AuthType = Field(..., description="Authentication type")
    auth_config: Dict[str, Any] = Field(..., description="Authentication configuration")
    rate_limit: Optional[int] = Field(None, description="Requests per minute")
    timeout: int = Field(30, description="Request timeout in seconds")
    retry_config: Optional[Dict[str, Any]] = Field(None, description="Retry configuration")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Integration name must be at least 3 characters')
        return v.strip()

    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 5 or v > 300:
            raise ValueError('Timeout must be between 5 and 300 seconds')
        return v


class ApiRequestModel(BaseModel):
    """Request model for API calls"""
    integration_id: str = Field(..., description="Integration ID")
    endpoint: str = Field(..., description="API endpoint path")
    method: HttpMethod = Field(HttpMethod.GET, description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    data: Optional[Dict[str, Any]] = Field(None, description="Request body data")
    files: Optional[Dict[str, Any]] = Field(None, description="File uploads")
    auth_override: Optional[Dict[str, Any]] = Field(None, description="Override auth config")
    timeout_override: Optional[int] = Field(None, description="Override timeout")
    retries: Optional[int] = Field(None, description="Override retry count")


class WebhookRequest(BaseModel):
    """Request model for webhook subscriptions"""
    integration_id: str = Field(..., description="Integration ID")
    event_types: List[str] = Field(..., description="Event types to subscribe to")
    callback_url: AnyHttpUrl = Field(..., description="Webhook callback URL")
    secret: Optional[str] = Field(None, description="Webhook secret for verification")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration"""
    failure_threshold: int = Field(5, description="Failure threshold")
    recovery_timeout: int = Field(60, description="Recovery timeout in seconds")
    expected_exception: Optional[str] = Field(None, description="Expected exception type")


class {{service_class_name}}(BaseService):
    """
    Enterprise API Integration Service for Ainflue Platform
    
    Handles comprehensive API integration management including:
    - Multi-platform API connections (YouTube, Instagram, TikTok, etc.)
    - Authentication management (OAuth2, API keys, JWT, etc.)
    - Rate limiting and quota management
    - Circuit breaker patterns for resilience
    - Retry logic with exponential backoff
    - Request/response logging and analytics
    - Webhook management and processing
    - Real-time monitoring and alerting
    - Caching and optimization
    - Error handling and recovery
    """

    def __init__(self):
        super().__init__()
        self.name = "{{service_name}}"
        self.version = "{{service_version}}"
        self.redis_client = None
        self.metrics_collector = ApiMetricsCollector()
        self.http_session = None
        
        # Circuit breaker tracking
        self.circuit_breakers = {}
        
        # Rate limiting tracking
        self.rate_limiters = {}
        
        # Default configurations
        self.default_timeout = 30
        self.default_retries = 3
        self.default_backoff_factor = 2
        
        # Platform-specific configurations
        self.platform_configs = {
            PlatformType.YOUTUBE: {
                'base_url': 'https://www.googleapis.com/youtube/v3',
                'auth_type': AuthType.API_KEY,
                'rate_limit': 10000,  # per day
                'quota_reset': 'daily'
            },
            PlatformType.INSTAGRAM: {
                'base_url': 'https://graph.instagram.com',
                'auth_type': AuthType.OAUTH2,
                'rate_limit': 200,  # per hour
                'quota_reset': 'hourly'
            },
            PlatformType.STRIPE: {
                'base_url': 'https://api.stripe.com/v1',
                'auth_type': AuthType.BEARER_TOKEN,
                'rate_limit': 100,  # per second
                'quota_reset': 'rolling'
            }
        }

    async def initialize(self):
        """Initialize service with dependencies"""
        try:
            await super().initialize()
            
            # Initialize Redis for caching and rate limiting
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                retry_on_timeout=True
            )
            
            # Initialize HTTP session with optimizations
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=10,  # Per-host connection limit
                keepalive_timeout=60,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.default_timeout)
            
            self.http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': f'Ainflue-Platform/{self.version}',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )
            
            # Initialize metrics collection
            await self.metrics_collector.initialize()
            
            # Start background workers
            asyncio.create_task(self._circuit_breaker_monitor())
            asyncio.create_task(self._rate_limit_cleanup_worker())
            
            logger.info(f"{self.name} service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} service: {e}")
            raise ServiceException(f"Service initialization failed: {e}")

    async def create_integration(
        self,
        request: CreateIntegrationRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Create a new API integration
        
        Args:
            request: Integration creation request
            session: Database session
            
        Returns:
            Integration details
        """
        async with self.get_session(session) as db_session:
            try:
                # Validate platform configuration
                platform_config = self.platform_configs.get(request.platform_type, {})
                
                # Encrypt sensitive auth data
                encrypted_auth = await self._encrypt_auth_config(request.auth_config)
                
                # Create integration
                integration = ApiIntegration(
                    id=str(uuid.uuid4()),
                    name=request.name,
                    platform_type=request.platform_type.value,
                    base_url=str(request.base_url),
                    auth_type=request.auth_type.value,
                    auth_config=encrypted_auth,
                    rate_limit=request.rate_limit or platform_config.get('rate_limit', 1000),
                    timeout=request.timeout,
                    retry_config=request.retry_config or {
                        'max_retries': self.default_retries,
                        'backoff_factor': self.default_backoff_factor
                    },
                    status=IntegrationStatus.ACTIVE.value,
                    metadata=request.metadata,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db_session.add(integration)
                await db_session.commit()
                
                # Initialize circuit breaker for this integration
                await self._initialize_circuit_breaker(integration.id)
                
                # Test connection
                connection_test = await self._test_integration_connection(integration)
                
                # Record metrics
                await self.metrics_collector.record_integration_created(
                    integration_id=integration.id,
                    platform_type=request.platform_type.value,
                    connection_success=connection_test['success']
                )
                
                logger.info(f"API integration created: {integration.id}")
                
                return {
                    "integration_id": integration.id,
                    "name": integration.name,
                    "platform_type": integration.platform_type,
                    "status": integration.status,
                    "connection_test": connection_test,
                    "created_at": integration.created_at.isoformat()
                }
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to create integration: {e}")
                await self.metrics_collector.record_error("integration_creation", str(e))
                raise ServiceException(f"Integration creation failed: {e}")

    async def make_api_request(
        self,
        request: ApiRequestModel,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Make an API request through an integration
        
        Args:
            request: API request details
            session: Database session
            
        Returns:
            API response data
        """
        async with self.get_session(session) as db_session:
            try:
                # Get integration details
                integration = await self._get_integration(request.integration_id, db_session)
                if not integration:
                    raise ValidationError(f"Integration {request.integration_id} not found")
                
                if integration.status != IntegrationStatus.ACTIVE.value:
                    raise ValidationError(f"Integration {request.integration_id} is not active")
                
                # Check circuit breaker
                if not await self._check_circuit_breaker(integration.id):
                    raise ServiceException("Circuit breaker is open for this integration")
                
                # Check rate limits
                if not await self._check_rate_limit(integration):
                    raise RateLimitError("Rate limit exceeded for this integration")
                
                # Prepare request
                api_request = await self._prepare_api_request(integration, request)
                
                # Execute request with retries
                response_data = await self._execute_request_with_retries(
                    integration, api_request
                )
                
                # Log successful request
                await self._log_api_request(
                    integration.id, request, response_data, success=True, db_session=db_session
                )
                
                # Update circuit breaker on success
                await self._record_circuit_breaker_success(integration.id)
                
                # Record metrics
                await self.metrics_collector.record_api_request(
                    integration_id=integration.id,
                    method=request.method.value,
                    endpoint=request.endpoint,
                    status_code=response_data.get('status_code', 200),
                    response_time=response_data.get('response_time', 0),
                    success=True
                )
                
                return response_data
                
            except Exception as e:
                # Log failed request
                try:
                    await self._log_api_request(
                        request.integration_id, request, None, 
                        success=False, error=str(e), db_session=db_session
                    )
                except:
                    pass
                
                # Update circuit breaker on failure
                await self._record_circuit_breaker_failure(request.integration_id)
                
                # Record metrics
                await self.metrics_collector.record_api_request(
                    integration_id=request.integration_id,
                    method=request.method.value,
                    endpoint=request.endpoint,
                    status_code=0,
                    response_time=0,
                    success=False,
                    error=str(e)
                )
                
                logger.error(f"API request failed: {e}")
                raise ServiceException(f"API request failed: {e}")

    async def _prepare_api_request(
        self,
        integration: ApiIntegration,
        request: ApiRequestModel
    ) -> Dict[str, Any]:
        """Prepare API request with authentication and headers"""
        try:
            # Build full URL
            base_url = integration.base_url.rstrip('/')
            endpoint = request.endpoint.lstrip('/')
            full_url = f"{base_url}/{endpoint}"
            
            # Prepare headers
            headers = dict(request.headers) if request.headers else {}
            
            # Add authentication
            auth_config = await self._decrypt_auth_config(integration.auth_config)
            headers.update(await self._prepare_auth_headers(integration.auth_type, auth_config))
            
            # Prepare request data
            api_request = {
                'method': request.method.value,
                'url': full_url,
                'headers': headers,
                'params': request.params,
                'timeout': request.timeout_override or integration.timeout
            }
            
            # Add body data for non-GET requests
            if request.method != HttpMethod.GET:
                if request.data:
                    if 'application/json' in headers.get('Content-Type', ''):
                        api_request['json'] = request.data
                    else:
                        api_request['data'] = request.data
                
                if request.files:
                    api_request['data'] = aiohttp.FormData()
                    for key, file_data in request.files.items():
                        api_request['data'].add_field(key, file_data)
            
            return api_request
            
        except Exception as e:
            logger.error(f"Failed to prepare API request: {e}")
            raise ServiceException(f"Request preparation failed: {e}")

    async def _execute_request_with_retries(
        self,
        integration: ApiIntegration,
        api_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute API request with retry logic"""
        retry_config = integration.retry_config or {}
        max_retries = retry_config.get('max_retries', self.default_retries)
        backoff_factor = retry_config.get('backoff_factor', self.default_backoff_factor)
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                # Execute request
                async with self.http_session.request(**api_request) as response:
                    response_time = (time.time() - start_time) * 1000  # milliseconds
                    
                    # Read response
                    response_text = await response.text()
                    
                    # Parse JSON if possible
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"content": response_text}
                    
                    # Check for successful response
                    if 200 <= response.status < 300:
                        return {
                            'status_code': response.status,
                            'headers': dict(response.headers),
                            'data': response_data,
                            'response_time': response_time,
                            'attempt': attempt + 1
                        }
                    
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = response.headers.get('Retry-After')
                        if retry_after:
                            await asyncio.sleep(int(retry_after))
                        else:
                            await asyncio.sleep(backoff_factor ** attempt)
                        continue
                    
                    # Handle server errors (retry)
                    if response.status >= 500:
                        if attempt < max_retries:
                            await asyncio.sleep(backoff_factor ** attempt)
                            continue
                    
                    # Client errors (don't retry)
                    return {
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'data': response_data,
                        'response_time': response_time,
                        'attempt': attempt + 1,
                        'error': f"HTTP {response.status}: {response_text}"
                    }
                    
            except asyncio.TimeoutError as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(backoff_factor ** attempt)
                    continue
                    
            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(backoff_factor ** attempt)
                    continue
                    
            except Exception as e:
                last_exception = e
                break  # Don't retry on unexpected errors
        
        # All retries exhausted
        raise ServiceException(f"Request failed after {max_retries + 1} attempts: {last_exception}")

    async def _prepare_auth_headers(
        self,
        auth_type: str,
        auth_config: Dict[str, Any]
    ) -> Dict[str, str]:
        """Prepare authentication headers"""
        headers = {}
        
        try:
            if auth_type == AuthType.API_KEY.value:
                key_name = auth_config.get('key_name', 'X-API-Key')
                api_key = auth_config.get('api_key')
                if api_key:
                    headers[key_name] = api_key
                    
            elif auth_type == AuthType.BEARER_TOKEN.value:
                token = auth_config.get('token')
                if token:
                    headers['Authorization'] = f'Bearer {token}'
                    
            elif auth_type == AuthType.BASIC_AUTH.value:
                username = auth_config.get('username')
                password = auth_config.get('password')
                if username and password:
                    import base64
                    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                    headers['Authorization'] = f'Basic {credentials}'
                    
            elif auth_type == AuthType.OAUTH2.value:
                access_token = auth_config.get('access_token')
                if access_token:
                    headers['Authorization'] = f'Bearer {access_token}'
                    
            elif auth_type == AuthType.JWT.value:
                jwt_token = auth_config.get('jwt_token')
                if jwt_token:
                    headers['Authorization'] = f'Bearer {jwt_token}'
                    
            elif auth_type == AuthType.SIGNATURE.value:
                # Custom signature-based authentication
                signature = await self._generate_signature(auth_config)
                if signature:
                    headers.update(signature)
                    
            elif auth_type == AuthType.CUSTOM.value:
                # Custom authentication headers
                custom_headers = auth_config.get('headers', {})
                headers.update(custom_headers)
            
            return headers
            
        except Exception as e:
            logger.error(f"Failed to prepare auth headers: {e}")
            return headers

    async def _generate_signature(self, auth_config: Dict[str, Any]) -> Dict[str, str]:
        """Generate signature-based authentication headers"""
        try:
            # This is a placeholder for signature-based auth
            # Implementation depends on the specific API requirements
            secret_key = auth_config.get('secret_key')
            algorithm = auth_config.get('algorithm', 'HS256')
            
            if not secret_key:
                return {}
            
            # Generate timestamp
            timestamp = str(int(time.time()))
            
            # Create signature payload
            payload = {
                'timestamp': timestamp,
                'nonce': str(uuid.uuid4())
            }
            
            # Generate signature
            signature = jwt.encode(payload, secret_key, algorithm=algorithm)
            
            return {
                'X-Timestamp': timestamp,
                'X-Signature': signature
            }
            
        except Exception as e:
            logger.error(f"Failed to generate signature: {e}")
            return {}

    async def _check_circuit_breaker(self, integration_id: str) -> bool:
        """Check circuit breaker state"""
        try:
            circuit_key = f"circuit_breaker:{integration_id}"
            circuit_data = await self.redis_client.hgetall(circuit_key)
            
            if not circuit_data:
                return True  # No circuit breaker data, allow request
            
            state = circuit_data.get('state', CircuitBreakerState.CLOSED.value)
            
            if state == CircuitBreakerState.CLOSED.value:
                return True
                
            elif state == CircuitBreakerState.OPEN.value:
                # Check if recovery timeout has passed
                last_failure = float(circuit_data.get('last_failure_time', 0))
                recovery_timeout = int(circuit_data.get('recovery_timeout', 60))
                
                if time.time() - last_failure >= recovery_timeout:
                    # Move to half-open state
                    await self.redis_client.hset(
                        circuit_key,
                        'state',
                        CircuitBreakerState.HALF_OPEN.value
                    )
                    return True
                    
                return False
                
            elif state == CircuitBreakerState.HALF_OPEN.value:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check circuit breaker: {e}")
            return True  # Allow request on error

    async def _initialize_circuit_breaker(self, integration_id: str):
        """Initialize circuit breaker for integration"""
        try:
            circuit_key = f"circuit_breaker:{integration_id}"
            circuit_data = {
                'state': CircuitBreakerState.CLOSED.value,
                'failure_count': '0',
                'failure_threshold': '5',
                'recovery_timeout': '60',
                'last_failure_time': '0'
            }
            
            await self.redis_client.hset(circuit_key, mapping=circuit_data)
            await self.redis_client.expire(circuit_key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Failed to initialize circuit breaker: {e}")

    async def _record_circuit_breaker_success(self, integration_id: str):
        """Record successful request for circuit breaker"""
        try:
            circuit_key = f"circuit_breaker:{integration_id}"
            
            # Reset failure count and close circuit
            await self.redis_client.hset(
                circuit_key,
                mapping={
                    'state': CircuitBreakerState.CLOSED.value,
                    'failure_count': '0'
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to record circuit breaker success: {e}")

    async def _record_circuit_breaker_failure(self, integration_id: str):
        """Record failed request for circuit breaker"""
        try:
            circuit_key = f"circuit_breaker:{integration_id}"
            circuit_data = await self.redis_client.hgetall(circuit_key)
            
            if not circuit_data:
                await self._initialize_circuit_breaker(integration_id)
                circuit_data = await self.redis_client.hgetall(circuit_key)
            
            failure_count = int(circuit_data.get('failure_count', 0)) + 1
            failure_threshold = int(circuit_data.get('failure_threshold', 5))
            
            updates = {
                'failure_count': str(failure_count),
                'last_failure_time': str(time.time())
            }
            
            # Open circuit if threshold exceeded
            if failure_count >= failure_threshold:
                updates['state'] = CircuitBreakerState.OPEN.value
            
            await self.redis_client.hset(circuit_key, mapping=updates)
            
        except Exception as e:
            logger.error(f"Failed to record circuit breaker failure: {e}")

    async def _check_rate_limit(self, integration: ApiIntegration) -> bool:
        """Check rate limit for integration"""
        try:
            if not integration.rate_limit:
                return True
            
            # Use sliding window rate limiting
            rate_key = f"rate_limit:{integration.id}"
            current_time = time.time()
            window_size = 60  # 1 minute window
            
            # Clean old entries
            await self.redis_client.zremrangebyscore(
                rate_key,
                '-inf',
                current_time - window_size
            )
            
            # Count current requests
            request_count = await self.redis_client.zcard(rate_key)
            
            if request_count >= integration.rate_limit:
                return False
            
            # Add current request
            await self.redis_client.zadd(
                rate_key,
                {str(uuid.uuid4()): current_time}
            )
            
            # Set expiration
            await self.redis_client.expire(rate_key, window_size)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True  # Allow request on error

    async def _test_integration_connection(
        self,
        integration: ApiIntegration
    ) -> Dict[str, Any]:
        """Test integration connection"""
        try:
            # Prepare test request
            test_request = ApiRequestModel(
                integration_id=integration.id,
                endpoint="/",  # Root endpoint
                method=HttpMethod.GET,
                timeout_override=10  # Short timeout for test
            )
            
            # Make test request
            response = await self.make_api_request(test_request)
            
            return {
                "success": True,
                "status_code": response.get('status_code', 200),
                "response_time": response.get('response_time', 0),
                "message": "Connection successful"
            }
            
        except Exception as e:
            logger.warning(f"Integration connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Connection failed"
            }

    async def subscribe_webhook(
        self,
        request: WebhookRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Subscribe to webhook events
        
        Args:
            request: Webhook subscription request
            session: Database session
            
        Returns:
            Webhook subscription details
        """
        async with self.get_session(session) as db_session:
            try:
                # Validate integration
                integration = await self._get_integration(request.integration_id, db_session)
                if not integration:
                    raise ValidationError(f"Integration {request.integration_id} not found")
                
                # Create webhook subscription
                webhook = WebhookSubscription(
                    id=str(uuid.uuid4()),
                    integration_id=request.integration_id,
                    event_types=json.dumps(request.event_types),
                    callback_url=str(request.callback_url),
                    secret=request.secret,
                    status="active",
                    metadata=request.metadata,
                    created_at=datetime.utcnow()
                )
                
                db_session.add(webhook)
                await db_session.commit()
                
                logger.info(f"Webhook subscription created: {webhook.id}")
                
                return {
                    "webhook_id": webhook.id,
                    "integration_id": webhook.integration_id,
                    "event_types": json.loads(webhook.event_types),
                    "callback_url": webhook.callback_url,
                    "status": webhook.status,
                    "created_at": webhook.created_at.isoformat()
                }
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to create webhook subscription: {e}")
                raise ServiceException(f"Webhook subscription failed: {e}")

    async def process_webhook(
        self,
        integration_id: str,
        event_type: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process incoming webhook
        
        Args:
            integration_id: Integration ID
            event_type: Event type
            payload: Webhook payload
            headers: Request headers
            
        Returns:
            Processing result
        """
        try:
            # Get active webhook subscriptions
            async with self.get_session() as session:
                result = await session.execute(
                    select(WebhookSubscription).where(
                        and_(
                            WebhookSubscription.integration_id == integration_id,
                            WebhookSubscription.status == "active"
                        )
                    )
                )
                webhooks = result.scalars().all()
            
            if not webhooks:
                logger.warning(f"No active webhooks for integration {integration_id}")
                return {"processed": 0, "message": "No active webhooks"}
            
            processed_count = 0
            
            for webhook in webhooks:
                try:
                    event_types = json.loads(webhook.event_types)
                    
                    # Check if webhook is subscribed to this event type
                    if event_type not in event_types:
                        continue
                    
                    # Verify webhook signature if secret is provided
                    if webhook.secret and headers:
                        if not await self._verify_webhook_signature(
                            webhook.secret, payload, headers
                        ):
                            logger.warning(f"Invalid webhook signature for {webhook.id}")
                            continue
                    
                    # Process webhook
                    await self._deliver_webhook(webhook, event_type, payload)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process webhook {webhook.id}: {e}")
                    continue
            
            return {
                "processed": processed_count,
                "total_webhooks": len(webhooks),
                "message": f"Processed {processed_count} webhooks"
            }
            
        except Exception as e:
            logger.error(f"Failed to process webhook: {e}")
            raise ServiceException(f"Webhook processing failed: {e}")

    async def _deliver_webhook(
        self,
        webhook: WebhookSubscription,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Deliver webhook to callback URL"""
        try:
            webhook_payload = {
                "event_type": event_type,
                "webhook_id": webhook.id,
                "integration_id": webhook.integration_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": payload
            }
            
            # Add signature if secret is provided
            headers = {"Content-Type": "application/json"}
            if webhook.secret:
                signature = await self._generate_webhook_signature(
                    webhook.secret, webhook_payload
                )
                headers["X-Webhook-Signature"] = signature
            
            # Send webhook
            async with self.http_session.post(
                webhook.callback_url,
                json=webhook_payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    logger.info(f"Webhook delivered successfully: {webhook.id}")
                else:
                    logger.warning(f"Webhook delivery failed with status {response.status}")
                    
        except Exception as e:
            logger.error(f"Failed to deliver webhook {webhook.id}: {e}")

    async def _verify_webhook_signature(
        self,
        secret: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> bool:
        """Verify webhook signature"""
        try:
            signature_header = headers.get('X-Webhook-Signature')
            if not signature_header:
                return False
            
            expected_signature = await self._generate_webhook_signature(secret, payload)
            return signature_header == expected_signature
            
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {e}")
            return False

    async def _generate_webhook_signature(
        self,
        secret: str,
        payload: Dict[str, Any]
    ) -> str:
        """Generate webhook signature"""
        try:
            import hmac
            import hashlib
            
            payload_string = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                secret.encode(),
                payload_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return f"sha256={signature}"
            
        except Exception as e:
            logger.error(f"Failed to generate webhook signature: {e}")
            return ""

    # Helper methods
    async def _get_integration(
        self,
        integration_id: str,
        session: AsyncSession
    ) -> Optional[ApiIntegration]:
        """Get integration by ID"""
        try:
            result = await session.execute(
                select(ApiIntegration).where(ApiIntegration.id == integration_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get integration {integration_id}: {e}")
            return None

    async def _encrypt_auth_config(self, auth_config: Dict[str, Any]) -> str:
        """Encrypt authentication configuration"""
        try:
            if not auth_config:
                return ""
            
            # Use Fernet encryption for sensitive data
            key = settings.ENCRYPTION_KEY.encode() if hasattr(settings, 'ENCRYPTION_KEY') else Fernet.generate_key()
            fernet = Fernet(key)
            
            config_json = json.dumps(auth_config)
            encrypted_config = fernet.encrypt(config_json.encode())
            
            return encrypted_config.decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt auth config: {e}")
            return json.dumps(auth_config)  # Fallback to plain text

    async def _decrypt_auth_config(self, encrypted_config: str) -> Dict[str, Any]:
        """Decrypt authentication configuration"""
        try:
            if not encrypted_config:
                return {}
            
            # Try to decrypt
            try:
                key = settings.ENCRYPTION_KEY.encode() if hasattr(settings, 'ENCRYPTION_KEY') else Fernet.generate_key()
                fernet = Fernet(key)
                
                decrypted_config = fernet.decrypt(encrypted_config.encode())
                return json.loads(decrypted_config.decode())
                
            except:
                # Fallback to plain text
                return json.loads(encrypted_config)
                
        except Exception as e:
            logger.error(f"Failed to decrypt auth config: {e}")
            return {}

    async def _log_api_request(
        self,
        integration_id: str,
        request: ApiRequestModel,
        response: Optional[Dict[str, Any]],
        success: bool,
        error: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ):
        """Log API request"""
        if session:
            try:
                api_request_log = ApiRequest(
                    id=str(uuid.uuid4()),
                    integration_id=integration_id,
                    method=request.method.value,
                    endpoint=request.endpoint,
                    headers=json.dumps(dict(request.headers)) if request.headers else None,
                    params=json.dumps(request.params) if request.params else None,
                    data=json.dumps(request.data) if request.data else None,
                    response_status=response.get('status_code') if response else None,
                    response_data=json.dumps(response.get('data')) if response else None,
                    response_time=response.get('response_time') if response else None,
                    success=success,
                    error_message=error,
                    created_at=datetime.utcnow()
                )
                
                session.add(api_request_log)
                await session.commit()
                
            except Exception as e:
                logger.error(f"Failed to log API request: {e}")

    async def _circuit_breaker_monitor(self):
        """Background task to monitor circuit breakers"""
        while True:
            try:
                # Check all circuit breakers and send alerts for open circuits
                circuit_pattern = "circuit_breaker:*"
                circuit_keys = await self.redis_client.keys(circuit_pattern)
                
                for circuit_key in circuit_keys:
                    circuit_data = await self.redis_client.hgetall(circuit_key)
                    if circuit_data.get('state') == CircuitBreakerState.OPEN.value:
                        integration_id = circuit_key.split(':')[1]
                        logger.warning(f"Circuit breaker OPEN for integration {integration_id}")
                        
                        # Send alert (implement notification logic)
                        await self._send_circuit_breaker_alert(integration_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Circuit breaker monitor error: {e}")
                await asyncio.sleep(60)

    async def _rate_limit_cleanup_worker(self):
        """Background task to clean up rate limit data"""
        while True:
            try:
                # Clean up expired rate limit entries
                rate_limit_pattern = "rate_limit:*"
                rate_limit_keys = await self.redis_client.keys(rate_limit_pattern)
                
                current_time = time.time()
                
                for rate_key in rate_limit_keys:
                    # Remove entries older than 1 hour
                    await self.redis_client.zremrangebyscore(
                        rate_key,
                        '-inf',
                        current_time - 3600
                    )
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Rate limit cleanup error: {e}")
                await asyncio.sleep(300)

    async def _send_circuit_breaker_alert(self, integration_id: str):
        """Send alert when circuit breaker opens"""
        try:
            # This would integrate with your notification service
            alert_data = {
                "type": "circuit_breaker_open",
                "integration_id": integration_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Circuit breaker opened for integration {integration_id}"
            }
            
            # Log alert for now
            logger.error(f"ALERT: {alert_data}")
            
        except Exception as e:
            logger.error(f"Failed to send circuit breaker alert: {e}")

    async def get_integration_status(
        self,
        integration_id: str,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get integration status and health metrics
        
        Args:
            integration_id: Integration ID
            session: Database session
            
        Returns:
            Integration status and metrics
        """
        async with self.get_session(session) as db_session:
            try:
                integration = await self._get_integration(integration_id, db_session)
                if not integration:
                    raise ValidationError(f"Integration {integration_id} not found")
                
                # Get circuit breaker status
                circuit_key = f"circuit_breaker:{integration_id}"
                circuit_data = await self.redis_client.hgetall(circuit_key)
                
                # Get rate limit status
                rate_key = f"rate_limit:{integration_id}"
                current_requests = await self.redis_client.zcard(rate_key)
                
                # Get recent request metrics
                metrics = await self.metrics_collector.get_integration_metrics(integration_id)
                
                return {
                    "integration_id": integration_id,
                    "name": integration.name,
                    "platform_type": integration.platform_type,
                    "status": integration.status,
                    "circuit_breaker": {
                        "state": circuit_data.get('state', 'closed'),
                        "failure_count": int(circuit_data.get('failure_count', 0)),
                        "failure_threshold": int(circuit_data.get('failure_threshold', 5))
                    },
                    "rate_limit": {
                        "current_requests": current_requests,
                        "limit": integration.rate_limit,
                        "percentage": (current_requests / integration.rate_limit * 100) if integration.rate_limit else 0
                    },
                    "metrics": metrics,
                    "last_updated": integration.updated_at.isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to get integration status: {e}")
                raise ServiceException(f"Failed to get integration status: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = await super().health_check()
            
            # Check Redis connectivity
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis"] = "healthy"
            
            # Check HTTP session
            if self.http_session and not self.http_session.closed:
                health_status["http_session"] = "healthy"
            
            # Check active integrations
            async with self.get_session() as session:
                result = await session.execute(
                    select(func.count(ApiIntegration.id)).where(
                        ApiIntegration.status == IntegrationStatus.ACTIVE.value
                    )
                )
                active_integrations = result.scalar() or 0
                health_status["active_integrations"] = active_integrations
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def cleanup(self):
        """Cleanup service resources"""
        try:
            if self.http_session and not self.http_session.closed:
                await self.http_session.close()
            
            if self.redis_client:
                await self.redis_client.close()
            
            if self.metrics_collector:
                await self.metrics_collector.cleanup()
                
            await super().cleanup()
            logger.info(f"{self.name} service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup {self.name} service: {e}")


# Example usage and testing
if __name__ == "__main__":
    async def main():
        service = {{service_class_name}}()
        await service.initialize()
        
        # Example integration creation
        integration_request = CreateIntegrationRequest(
            name="YouTube API Integration",
            platform_type=PlatformType.YOUTUBE,
            base_url="https://www.googleapis.com/youtube/v3",
            auth_type=AuthType.API_KEY,
            auth_config={
                "api_key": "your_youtube_api_key",
                "key_name": "key"
            },
            rate_limit=10000
        )
        
        try:
            integration = await service.create_integration(integration_request)
            print(f"Integration created: {integration}")
            
            # Example API request
            api_request = ApiRequestModel(
                integration_id=integration["integration_id"],
                endpoint="/channels",
                method=HttpMethod.GET,
                params={"part": "snippet", "mine": "true"}
            )
            
            response = await service.make_api_request(api_request)
            print(f"API response: {response}")
            
            # Get integration status
            status = await service.get_integration_status(integration["integration_id"])
            print(f"Integration status: {status}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await service.cleanup()

    asyncio.run(main())