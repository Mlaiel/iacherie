"""API Connectors - External Services Integration Hub
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in 
legal action.

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

This module provides comprehensive API integration capabilities for external services
including streaming platforms, payment processors, analytics services, and content
distribution networks.
"""import logging
import asyncio
import aiohttp
import jwt
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse
import json
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
import ssl
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')

class APIProvider(Enum):
    """Supported API providers"""    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    YOUTUBE_MUSIC = "youtube_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    BANDCAMP = "bandcamp"
    BEATPORT = "beatport"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    GOOGLE_ANALYTICS = "google_analytics"
    FACEBOOK_ANALYTICS = "facebook_analytics"
    MIXPANEL = "mixpanel"
    AMPLITUDE = "amplitude"
    SENDGRID = "sendgrid"
    MAILCHIMP = "mailchimp"
    TWILIO = "twilio"
    AWS_S3 = "aws_s3"
    CLOUDFLARE = "cloudflare"
    FASTLY = "fastly"

class APIConnectionStatus(Enum):
    """API connection status"""    CONNECTED = auto()
    DISCONNECTED = auto()
    AUTHENTICATING = auto()
    ERROR = auto()
    RATE_LIMITED = auto()
    MAINTENANCE = auto()
    TIMEOUT = auto()
    INVALID_CREDENTIALS = auto()

class APIAuthType(Enum):
    """Authentication types"""    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    HMAC_SIGNATURE = "hmac_signature"
    CUSTOM = "custom"

@dataclass
class APICredentials:
    """API authentication credentials"""    provider: APIProvider
    auth_type: APIAuthType
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    scopes: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    base_url: Optional[str] = None
    webhook_url: Optional[str] = None
    encryption_key: Optional[str] = None

@dataclass 
class APIRequestConfig:
    """API request configuration"""    method: str = "GET"
    endpoint: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    files: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 30
    retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    stream: bool = False

@dataclass
class APIResponse(Generic[T]):
    """API response wrapper"""    success: bool
    status_code: Optional[int] = None
    data: Optional[T] = None
    error_message: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    request_id: Optional[str] = None
    rate_limit: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    provider: Optional[APIProvider] = None

class APIConnectorError(Exception):
    """Custom exception for API connector errors"""    def __init__(self, message: str, error_code: Optional[str] = None, 
                 provider: Optional[APIProvider] = None):
        super().__init__(message)
        self.error_code = error_code
        self.provider = provider
        self.timestamp = datetime.utcnow()

class RateLimiter:
    """Advanced rate limiter with multiple strategies"""    
    def __init__(self, requests_per_minute: int = 60, 
                 requests_per_hour: int = 3600, 
                 burst_limit: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        self.minute_window = []
        self.hour_window = []
        self.burst_window = []
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire rate limit permission"""        async with self.lock:
            now = datetime.utcnow()
            
            # Clean old entries
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            burst_window_ago = now - timedelta(seconds=10)
            
            self.minute_window = [t for t in self.minute_window if t > minute_ago]
            self.hour_window = [t for t in self.hour_window if t > hour_ago]
            self.burst_window = [t for t in self.burst_window if t > burst_window_ago]
            
            # Check limits
            if (len(self.minute_window) >= self.requests_per_minute or
                len(self.hour_window) >= self.requests_per_hour or
                len(self.burst_window) >= self.burst_limit):
                return False
            
            # Add current request
            self.minute_window.append(now)
            self.hour_window.append(now)
            self.burst_window.append(now)
            
            return True
    
    def get_wait_time(self) -> float:
        """Get time to wait before next request"""        now = datetime.utcnow()
        
        if self.minute_window and len(self.minute_window) >= self.requests_per_minute:
            oldest = min(self.minute_window)
            return (oldest + timedelta(minutes=1) - now).total_seconds()
        
        if self.burst_window and len(self.burst_window) >= self.burst_limit:
            oldest = min(self.burst_window)
            return (oldest + timedelta(seconds=10) - now).total_seconds()
        
        return 0.0

class BaseAPIConnector(ABC, Generic[T]):
    """Base class for all API connectors"""    
    def __init__(self, credentials: APICredentials, provider: APIProvider):
        self.credentials = credentials
        self.provider = provider
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.status = APIConnectionStatus.DISCONNECTED
        self.rate_limiter = RateLimiter()
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = None
        self.error_count = 0
        self.max_errors = 5
        
        # Encryption for sensitive data
        if credentials.encryption_key:
            self.cipher = Fernet(credentials.encryption_key.encode()[:44].ljust(44, b'='))
        else:
            self.cipher = None
    
    async def __aenter__(self):
        """Async context manager entry"""        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""        await self._close_session()
    
    async def _create_session(self):
        """Create HTTP session"""        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                ssl=ssl.create_default_context() if self.credentials.base_url and 
                    self.credentials.base_url.startswith('https') else False,
                limit=100,
                limit_per_host=10
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._get_default_headers()
            )
    
    async def _close_session(self):
        """Close HTTP session"""        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests"""        headers = {
            'User-Agent': 'IA-Influencer-Agent/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        headers.update(self.credentials.custom_headers)
        return headers
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""        if self.cipher:
            return self.cipher.encrypt(data.encode()).decode()
        return data
    
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""        if self.cipher:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        return encrypted_data
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the API"""        pass
    
    @abstractmethod
    async def refresh_credentials(self) -> bool:
        """Refresh authentication credentials"""        pass
    
    @abstractmethod
    def _prepare_auth_headers(self) -> Dict[str, str]:
        """Prepare authentication headers"""        pass
    
    async def _make_request(self, config: APIRequestConfig) -> APIResponse[T]:
        """Make HTTP request with comprehensive error handling"""        if not self.session:
            await self._create_session()
        
        # Rate limiting
        if not await self.rate_limiter.acquire():
            wait_time = self.rate_limiter.get_wait_time()
            self.logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            return await self._make_request(config)  # Retry after waiting
        
        # Build full URL
        base_url = self.credentials.base_url or ""
        url = f"{base_url.rstrip('/')}/{config.endpoint.lstrip('/')}"
        
        # Prepare headers
        headers = self._get_default_headers()
        headers.update(self._prepare_auth_headers())
        headers.update(config.headers)
        
        start_time = datetime.utcnow()
        
        for attempt in range(config.retries + 1):
            try:
                async with self.session.request(
                    method=config.method.upper(),
                    url=url,
                    params=config.params,
                    headers=headers,
                    json=config.json_data,
                    data=config.data,
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                    ssl=config.verify_ssl
                ) as response:
                    
                    execution_time = (datetime.utcnow() - start_time).total_seconds()
                    self.last_request_time = datetime.utcnow()
                    
                    # Parse rate limit headers
                    rate_limit = self._parse_rate_limit_headers(response.headers)
                    
                    # Get request ID from headers
                    request_id = response.headers.get('X-Request-ID') or response.headers.get('Request-ID')
                    
                    if response.status == 200:
                        try:
                            if config.stream:
                                data = await response.read()
                            else:
                                data = await response.json()
                            
                            self.error_count = 0  # Reset error count on success
                            
                            return APIResponse(
                                success=True,
                                status_code=response.status,
                                data=data,
                                headers=dict(response.headers),
                                request_id=request_id,
                                rate_limit=rate_limit,
                                execution_time=execution_time,
                                provider=self.provider
                            )
                            
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON decode error: {e}")
                            return APIResponse(
                                success=False,
                                status_code=response.status,
                                error_message=f"Invalid JSON response: {e}",
                                provider=self.provider
                            )
                    
                    elif response.status == 401:
                        # Try to refresh credentials
                        if await self.refresh_credentials():
                            headers.update(self._prepare_auth_headers())
                            continue
                        else:
                            self.status = APIConnectionStatus.INVALID_CREDENTIALS
                            return APIResponse(
                                success=False,
                                status_code=response.status,
                                error_message="Authentication failed",
                                provider=self.provider
                            )
                    
                    elif response.status == 429:
                        # Rate limited
                        retry_after = response.headers.get('Retry-After', '60')
                        wait_time = int(retry_after)
                        self.logger.warning(f"Rate limited, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        error_text = await response.text()
                        return APIResponse(
                            success=False,
                            status_code=response.status,
                            error_message=f"HTTP {response.status}: {error_text}",
                            headers=dict(response.headers),
                            provider=self.provider
                        )
            
            except asyncio.TimeoutError:
                if attempt < config.retries:
                    await asyncio.sleep(config.retry_delay * (attempt + 1))
                    continue
                    
                return APIResponse(
                    success=False,
                    error_message="Request timeout",
                    provider=self.provider
                )
            
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Request error (attempt {attempt + 1}): {e}")
                
                if self.error_count >= self.max_errors:
                    self.status = APIConnectionStatus.ERROR
                
                if attempt < config.retries:
                    await asyncio.sleep(config.retry_delay * (attempt + 1))
                    continue
                
                return APIResponse(
                    success=False,
                    error_message=str(e),
                    provider=self.provider
                )
        
        return APIResponse(
            success=False,
            error_message="All retry attempts failed",
            provider=self.provider
        )
    
    def _parse_rate_limit_headers(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Parse rate limit information from response headers"""        rate_limit = {}
        
        # Common rate limit header patterns
        patterns = [
            ('limit', ['X-Rate-Limit-Limit', 'X-RateLimit-Limit', 'Rate-Limit-Limit']),
            ('remaining', ['X-Rate-Limit-Remaining', 'X-RateLimit-Remaining', 'Rate-Limit-Remaining']),
            ('reset', ['X-Rate-Limit-Reset', 'X-RateLimit-Reset', 'Rate-Limit-Reset']),
            ('retry_after', ['Retry-After'])
        ]
        
        for key, header_names in patterns:
            for header_name in header_names:
                if header_name in headers:
                    try:
                        rate_limit[key] = int(headers[header_name])
                        break
                    except ValueError:
                        continue
        
        return rate_limit if rate_limit else None
    
    async def test_connection(self) -> APIResponse[Dict[str, Any]]:
        """Test API connection"""        test_config = APIRequestConfig(
            method="GET",
            endpoint="/health" if hasattr(self, '_health_endpoint') else "/",
            timeout=10
        )
        
        response = await self._make_request(test_config)
        
        if response.success:
            self.status = APIConnectionStatus.CONNECTED
        else:
            self.status = APIConnectionStatus.ERROR
        
        return response
    
    def get_status(self) -> APIConnectionStatus:
        """Get current connection status"""        return self.status
    
    def get_error_count(self) -> int:
        """Get current error count"""        return self.error_count
    
    def reset_error_count(self):
        """Reset error count"""        self.error_count = 0
        if self.error_count == 0:
            self.status = APIConnectionStatus.DISCONNECTED

class StreamingPlatformConnector(BaseAPIConnector[Dict[str, Any]]):
    """Specialized connector for streaming platforms"""    
    def __init__(self, credentials: APICredentials, provider: APIProvider):
        super().__init__(credentials, provider)
        self.track_cache = {}
        self.artist_cache = {}
        self.playlist_cache = {}
    
    async def authenticate(self) -> bool:
        """Authenticate with streaming platform"""        try:
            if self.credentials.auth_type == APIAuthType.OAUTH2:
                return await self._oauth2_authenticate()
            elif self.credentials.auth_type == APIAuthType.API_KEY:
                return await self._api_key_authenticate()
            else:
                self.logger.error(f"Unsupported auth type: {self.credentials.auth_type}")
                return False
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            self.status = APIConnectionStatus.ERROR
            return False
    
    async def _oauth2_authenticate(self) -> bool:
        """OAuth2 authentication flow"""        auth_config = APIRequestConfig(
            method="POST",
            endpoint="/api/token",
            data={
                'grant_type': 'client_credentials',
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret
            }
        )
        
        response = await self._make_request(auth_config)
        
        if response.success and response.data:
            self.credentials.access_token = response.data.get('access_token')
            if 'expires_in' in response.data:
                expires_in = response.data['expires_in']
                self.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            self.status = APIConnectionStatus.CONNECTED
            return True
        
        return False
    
    async def _api_key_authenticate(self) -> bool:
        """API key authentication"""        # Simple test request to verify API key
        test_response = await self.test_connection()
        return test_response.success
    
    async def refresh_credentials(self) -> bool:
        """Refresh OAuth2 credentials"""        if not self.credentials.refresh_token:
            return await self.authenticate()
        
        refresh_config = APIRequestConfig(
            method="POST",
            endpoint="/api/token",
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.credentials.refresh_token,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret
            }
        )
        
        response = await self._make_request(refresh_config)
        
        if response.success and response.data:
            self.credentials.access_token = response.data.get('access_token')
            new_refresh_token = response.data.get('refresh_token')
            if new_refresh_token:
                self.credentials.refresh_token = new_refresh_token
            
            if 'expires_in' in response.data:
                expires_in = response.data['expires_in']
                self.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return True
        
        return False
    
    def _prepare_auth_headers(self) -> Dict[str, str]:
        """Prepare authentication headers"""        if self.credentials.auth_type == APIAuthType.OAUTH2 and self.credentials.access_token:
            return {'Authorization': f'Bearer {self.credentials.access_token}'}
        elif self.credentials.auth_type == APIAuthType.API_KEY and self.credentials.api_key:
            return {'X-API-Key': self.credentials.api_key}
        return {}
    
    async def search_tracks(self, query: str, limit: int = 50) -> APIResponse[List[Dict[str, Any]]]:
        """Search for tracks"""        search_config = APIRequestConfig(
            method="GET",
            endpoint="/search",
            params={
                'q': query,
                'type': 'track',
                'limit': limit
            }
        )
        
        return await self._make_request(search_config)
    
    async def get_track(self, track_id: str, use_cache: bool = True) -> APIResponse[Dict[str, Any]]:
        """Get track details"""        if use_cache and track_id in self.track_cache:
            return APIResponse(
                success=True,
                data=self.track_cache[track_id],
                provider=self.provider
            )
        
        track_config = APIRequestConfig(
            method="GET",
            endpoint=f"/tracks/{track_id}"
        )
        
        response = await self._make_request(track_config)
        
        if response.success and response.data:
            self.track_cache[track_id] = response.data
        
        return response
    
    async def get_artist(self, artist_id: str, use_cache: bool = True) -> APIResponse[Dict[str, Any]]:
        """Get artist details"""        if use_cache and artist_id in self.artist_cache:
            return APIResponse(
                success=True,
                data=self.artist_cache[artist_id],
                provider=self.provider
            )
        
        artist_config = APIRequestConfig(
            method="GET",
            endpoint=f"/artists/{artist_id}"
        )
        
        response = await self._make_request(artist_config)
        
        if response.success and response.data:
            self.artist_cache[artist_id] = response.data
        
        return response
    
    async def get_playlist(self, playlist_id: str, use_cache: bool = True) -> APIResponse[Dict[str, Any]]:
        """Get playlist details"""        if use_cache and playlist_id in self.playlist_cache:
            return APIResponse(
                success=True,
                data=self.playlist_cache[playlist_id],
                provider=self.provider
            )
        
        playlist_config = APIRequestConfig(
            method="GET",
            endpoint=f"/playlists/{playlist_id}"
        )
        
        response = await self._make_request(playlist_config)
        
        if response.success and response.data:
            self.playlist_cache[playlist_id] = response.data
        
        return response
    
    def clear_cache(self):
        """Clear all cached data"""        self.track_cache.clear()
        self.artist_cache.clear()
        self.playlist_cache.clear()

class PaymentGatewayConnector(BaseAPIConnector[Dict[str, Any]]):
    """Specialized connector for payment gateways"""    
    def __init__(self, credentials: APICredentials, provider: APIProvider):
        super().__init__(credentials, provider)
        self.webhook_validators = {}
    
    async def authenticate(self) -> bool:
        """Authenticate with payment gateway"""        try:
            test_response = await self.test_connection()
            if test_response.success:
                self.status = APIConnectionStatus.CONNECTED
                return True
            return False
        except Exception as e:
            self.logger.error(f"Payment gateway authentication error: {e}")
            self.status = APIConnectionStatus.ERROR
            return False
    
    async def refresh_credentials(self) -> bool:
        """Refresh credentials (mostly not needed for payment gateways)"""        return await self.authenticate()
    
    def _prepare_auth_headers(self) -> Dict[str, str]:
        """Prepare authentication headers"""        if self.provider == APIProvider.STRIPE and self.credentials.secret_key:
            return {'Authorization': f'Bearer {self.credentials.secret_key}'}
        elif self.credentials.api_key:
            return {'Authorization': f'Bearer {self.credentials.api_key}'}
        return {}
    
    async def create_payment_intent(self, amount: int, currency: str = 'usd', 
                                  metadata: Optional[Dict[str, str]] = None) -> APIResponse[Dict[str, Any]]:
        """Create payment intent"""        payment_config = APIRequestConfig(
            method="POST",
            endpoint="/payment_intents",
            json_data={
                'amount': amount,
                'currency': currency,
                'metadata': metadata or {}
            }
        )
        
        return await self._make_request(payment_config)
    
    async def process_payment(self, payment_method: str, amount: int, 
                            currency: str = 'usd') -> APIResponse[Dict[str, Any]]:
        """Process payment"""        process_config = APIRequestConfig(
            method="POST",
            endpoint="/charges",
            json_data={
                'amount': amount,
                'currency': currency,
                'source': payment_method
            }
        )
        
        return await self._make_request(process_config)
    
    async def refund_payment(self, charge_id: str, amount: Optional[int] = None) -> APIResponse[Dict[str, Any]]:
        """Refund payment"""        refund_data = {'charge': charge_id}
        if amount:
            refund_data['amount'] = amount
        
        refund_config = APIRequestConfig(
            method="POST",
            endpoint="/refunds",
            json_data=refund_data
        )
        
        return await self._make_request(refund_config)
    
    def validate_webhook(self, payload: str, signature: str, endpoint_secret: str) -> bool:
        """Validate webhook signature"""        try:
            if self.provider == APIProvider.STRIPE:
                # Stripe webhook validation
                expected_sig = hmac.new(
                    endpoint_secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                return hmac.compare_digest(signature, f"sha256={expected_sig}")
            
            # Generic HMAC validation
            expected_sig = hmac.new(
                endpoint_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected_sig)
            
        except Exception as e:
            self.logger.error(f"Webhook validation error: {e}")
            return False

class APIConnectorManager:
    """Central manager for all API connections"""    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connectors: Dict[APIProvider, BaseAPIConnector] = {}
        self.connection_pool_size = 50
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = {}
        
        # Connector class mapping
        self.connector_classes = {
            APIProvider.SPOTIFY: StreamingPlatformConnector,
            APIProvider.APPLE_MUSIC: StreamingPlatformConnector,
            APIProvider.SOUNDCLOUD: StreamingPlatformConnector,
            APIProvider.YOUTUBE_MUSIC: StreamingPlatformConnector,
            APIProvider.STRIPE: PaymentGatewayConnector,
            APIProvider.PAYPAL: PaymentGatewayConnector,
        }
    
    async def add_connector(self, credentials: APICredentials) -> bool:
        """Add new API connector"""        try:
            provider = credentials.provider
            
            # Get appropriate connector class
            if provider in self.connector_classes:
                connector_class = self.connector_classes[provider]
            else:
                connector_class = BaseAPIConnector
            
            connector = connector_class(credentials, provider)
            
            # Test connection
            async with connector:
                if await connector.authenticate():
                    self.connectors[provider] = connector
                    self.logger.info(f"Successfully added connector for {provider.value}")
                    return True
                else:
                    self.logger.error(f"Failed to authenticate {provider.value}")
                    return False
        
        except Exception as e:
            self.logger.error(f"Failed to add connector for {credentials.provider}: {e}")
            return False
    
    def get_connector(self, provider: APIProvider) -> Optional[BaseAPIConnector]:
        """Get connector for specific provider"""        return self.connectors.get(provider)
    
    async def remove_connector(self, provider: APIProvider) -> bool:
        """Remove connector"""        if provider in self.connectors:
            connector = self.connectors[provider]
            if hasattr(connector, '_close_session'):
                await connector._close_session()
            
            del self.connectors[provider]
            self.logger.info(f"Removed connector for {provider.value}")
            return True
        
        return False
    
    async def health_check_all(self) -> Dict[APIProvider, bool]:
        """Health check for all connectors"""        results = {}
        
        for provider, connector in self.connectors.items():
            try:
                async with connector:
                    response = await connector.test_connection()
                    results[provider] = response.success
                    self.last_health_check[provider] = datetime.utcnow()
            except Exception as e:
                self.logger.error(f"Health check failed for {provider}: {e}")
                results[provider] = False
        
        return results
    
    async def refresh_all_credentials(self) -> Dict[APIProvider, bool]:
        """Refresh credentials for all connectors"""        results = {}
        
        for provider, connector in self.connectors.items():
            try:
                results[provider] = await connector.refresh_credentials()
            except Exception as e:
                self.logger.error(f"Credential refresh failed for {provider}: {e}")
                results[provider] = False
        
        return results
    
    def get_all_statuses(self) -> Dict[APIProvider, APIConnectionStatus]:
        """Get status of all connectors"""        return {provider: connector.get_status() 
                for provider, connector in self.connectors.items()}
    
    async def cleanup(self):
        """Cleanup all connections"""        for provider, connector in list(self.connectors.items()):
            await self.remove_connector(provider)
        
        self.logger.info("All API connections cleaned up")

# Export main classes
__all__ = [
    'APIConnectorManager',
    'BaseAPIConnector',
    'StreamingPlatformConnector',
    'PaymentGatewayConnector',
    'APICredentials',
    'APIRequestConfig',
    'APIResponse',
    'APIProvider',
    'APIConnectionStatus',
    'APIAuthType',
    'APIConnectorError',
    'RateLimiter'
]

logger.info("API connectors module loaded successfully")
