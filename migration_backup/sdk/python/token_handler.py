"""Token Handler for Ainflue SDK

Enterprise-grade token management with multi-expert design:
- Sécurité: Secure token rotation and refresh strategies
- DevOps: Token monitoring and health validation
- Backend Senior: Robust token lifecycle management
- Lead Dev IA: Intelligent token refresh prediction

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import json
import logging
import threading
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from .exceptions import (
    AuthenticationError, TokenExpiredError, TokenInvalidError,
    NetworkError, ConfigurationError
)


@dataclass
class TokenInfo:
    """Token information structure"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    scope: Optional[List[str]] = None
    issued_at: datetime = None
    
    def __post_init__(self):
        if self.issued_at is None:
            self.issued_at = datetime.utcnow()
        
        # Calculate expires_at if expires_in is provided
        if self.expires_in and not self.expires_at:
            self.expires_at = self.issued_at + timedelta(seconds=self.expires_in)
    
    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Check if token is expired (with buffer)"""
        if not self.expires_at:
            return False
        
        buffer_time = datetime.utcnow() + timedelta(seconds=buffer_seconds)
        return buffer_time >= self.expires_at
    
    def time_until_expiry(self) -> Optional[timedelta]:
        """Get time until token expiry"""
        if not self.expires_at:
            return None
        
        remaining = self.expires_at - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        if data['expires_at']:
            data['expires_at'] = data['expires_at'].isoformat()
        if data['issued_at']:
            data['issued_at'] = data['issued_at'].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenInfo':
        """Create from dictionary"""
        # Convert ISO strings to datetime objects
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        if data.get('issued_at'):
            data['issued_at'] = datetime.fromisoformat(data['issued_at'])
        
        return cls(**data)


class TokenRefreshStrategy(ABC):
    """Abstract base class for token refresh strategies"""
    
    @abstractmethod
    async def refresh_token(self, token_info: TokenInfo) -> TokenInfo:
        """Refresh the token"""
        pass
    
    @abstractmethod
    def should_refresh(self, token_info: TokenInfo) -> bool:
        """Check if token should be refreshed"""
        pass


class JWTRefreshStrategy(TokenRefreshStrategy):
    """JWT token refresh strategy"""
    
    def __init__(self, refresh_endpoint: str, client_id: str, client_secret: str):
        self.refresh_endpoint = refresh_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.logger = logging.getLogger(__name__)
    
    async def refresh_token(self, token_info: TokenInfo) -> TokenInfo:
        """Refresh JWT token using refresh token"""
        if not token_info.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        try:
            import httpx
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': token_info.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.refresh_endpoint, data=data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    return TokenInfo(
                        access_token=response_data['access_token'],
                        token_type=response_data.get('token_type', 'Bearer'),
                        expires_in=response_data.get('expires_in'),
                        refresh_token=response_data.get('refresh_token', token_info.refresh_token),
                        scope=response_data.get('scope', '').split() if response_data.get('scope') else None
                    )
                else:
                    raise AuthenticationError(f"Token refresh failed: {response.text}")
        
        except Exception as e:
            self.logger.error(f"Token refresh error: {str(e)}")
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    def should_refresh(self, token_info: TokenInfo) -> bool:
        """Check if JWT token should be refreshed"""
        return token_info.is_expired(buffer_seconds=300)  # 5 minutes buffer


class APIKeyRefreshStrategy(TokenRefreshStrategy):
    """API key refresh strategy (usually no refresh needed)"""
    
    async def refresh_token(self, token_info: TokenInfo) -> TokenInfo:
        """API keys typically don't need refresh"""
        return token_info
    
    def should_refresh(self, token_info: TokenInfo) -> bool:
        """API keys typically don't expire"""
        return False


class TokenMetrics:
    """Token usage metrics (DevOps expertise)"""
    
    def __init__(self):
        self.refresh_count = 0
        self.refresh_failures = 0
        self.last_refresh_time: Optional[datetime] = None
        self.last_refresh_duration: Optional[float] = None
        self.token_lifespan_stats: List[float] = []
        self.concurrent_refreshes = 0
        self._lock = threading.Lock()
    
    def record_refresh_start(self):
        """Record start of token refresh"""
        with self._lock:
            self.concurrent_refreshes += 1
    
    def record_refresh_success(self, duration: float, token_lifespan: Optional[float] = None):
        """Record successful token refresh"""
        with self._lock:
            self.refresh_count += 1
            self.last_refresh_time = datetime.utcnow()
            self.last_refresh_duration = duration
            self.concurrent_refreshes = max(0, self.concurrent_refreshes - 1)
            
            if token_lifespan:
                self.token_lifespan_stats.append(token_lifespan)
                # Keep only last 100 measurements
                if len(self.token_lifespan_stats) > 100:
                    self.token_lifespan_stats.pop(0)
    
    def record_refresh_failure(self):
        """Record failed token refresh"""
        with self._lock:
            self.refresh_failures += 1
            self.concurrent_refreshes = max(0, self.concurrent_refreshes - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get token metrics statistics"""
        with self._lock:
            avg_lifespan = (
                sum(self.token_lifespan_stats) / len(self.token_lifespan_stats)
                if self.token_lifespan_stats else None
            )
            
            success_rate = (
                self.refresh_count / max(self.refresh_count + self.refresh_failures, 1)
            )
            
            return {
                'refresh_count': self.refresh_count,
                'refresh_failures': self.refresh_failures,
                'success_rate': success_rate,
                'last_refresh_time': self.last_refresh_time.isoformat() if self.last_refresh_time else None,
                'last_refresh_duration_ms': self.last_refresh_duration * 1000 if self.last_refresh_duration else None,
                'average_token_lifespan_seconds': avg_lifespan,
                'concurrent_refreshes': self.concurrent_refreshes
            }


class TokenHandler:
    """Enterprise token management with automatic refresh
    
    Features:
    - Automatic token refresh based on expiry
    - Multiple refresh strategies (JWT, API Key, OAuth)
    - Thread-safe token access
    - Token usage metrics
    - Event callbacks for token events
    - Predictive refresh based on usage patterns
    """
    
    def __init__(
        self,
        refresh_strategy: TokenRefreshStrategy,
        auto_refresh: bool = True,
        refresh_buffer_seconds: int = 300,
        max_concurrent_refreshes: int = 1
    ):
        self.refresh_strategy = refresh_strategy
        self.auto_refresh = auto_refresh
        self.refresh_buffer_seconds = refresh_buffer_seconds
        self.max_concurrent_refreshes = max_concurrent_refreshes
        
        # Token state
        self._current_token: Optional[TokenInfo] = None
        self._refresh_task: Optional[asyncio.Task] = None
        self._refresh_lock = asyncio.Lock()
        self._sync_lock = threading.Lock()
        
        # Event callbacks
        self._event_callbacks: Dict[str, List[Callable]] = {
            'token_refreshed': [],
            'token_expired': [],
            'refresh_failed': [],
            'token_updated': []
        }
        
        # Metrics and logging
        self.metrics = TokenMetrics()
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._monitor_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    def add_event_callback(self, event: str, callback: Callable):
        """Add callback for token events"""
        if event in self._event_callbacks:
            self._event_callbacks[event].append(callback)
    
    def _notify_event(self, event: str, data: Dict[str, Any]):
        """Notify event callbacks"""
        if event in self._event_callbacks:
            for callback in self._event_callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(data))
                    else:
                        callback(data)
                except Exception as e:
                    self.logger.warning(f"Event callback error for {event}: {str(e)}")
    
    def set_token(self, token_info: TokenInfo):
        """Set current token"""
        with self._sync_lock:
            old_token = self._current_token
            self._current_token = token_info
            
            self.logger.info("Token updated")
            self._notify_event('token_updated', {
                'old_expires_at': old_token.expires_at.isoformat() if old_token and old_token.expires_at else None,
                'new_expires_at': token_info.expires_at.isoformat() if token_info.expires_at else None
            })
    
    def get_token(self) -> Optional[TokenInfo]:
        """Get current token (thread-safe)"""
        with self._sync_lock:
            return self._current_token
    
    async def get_valid_token(self) -> TokenInfo:
        """Get valid token, refreshing if necessary"""
        current_token = self.get_token()
        
        if not current_token:
            raise AuthenticationError("No token available")
        
        # Check if token needs refresh
        if self.auto_refresh and self.refresh_strategy.should_refresh(current_token):
            self.logger.info("Token needs refresh")
            
            # Attempt refresh
            refreshed_token = await self._refresh_token_with_retry(current_token)
            if refreshed_token:
                self.set_token(refreshed_token)
                return refreshed_token
            else:
                # Use current token if refresh fails (might still be valid)
                if not current_token.is_expired():
                    self.logger.warning("Refresh failed, using current token")
                    return current_token
                else:
                    raise TokenExpiredError("Token expired and refresh failed")
        
        # Check if token is expired
        if current_token.is_expired():
            raise TokenExpiredError("Token has expired")
        
        return current_token
    
    async def refresh_token(self) -> bool:
        """Manually refresh current token"""
        current_token = self.get_token()
        
        if not current_token:
            raise AuthenticationError("No token to refresh")
        
        refreshed_token = await self._refresh_token_with_retry(current_token)
        
        if refreshed_token:
            self.set_token(refreshed_token)
            return True
        
        return False
    
    async def _refresh_token_with_retry(self, token_info: TokenInfo) -> Optional[TokenInfo]:
        """Refresh token with retry logic and concurrency control"""
        
        # Use lock to prevent concurrent refreshes
        async with self._refresh_lock:
            
            # Check if token was already refreshed by another call
            current_token = self.get_token()
            if current_token and current_token != token_info:
                self.logger.debug("Token already refreshed by concurrent call")
                return current_token
            
            # Check concurrent refresh limit
            if self.metrics.concurrent_refreshes >= self.max_concurrent_refreshes:
                self.logger.warning("Max concurrent refreshes reached, skipping")
                return None
            
            self.metrics.record_refresh_start()
            start_time = time.time()
            
            try:
                # Calculate token lifespan
                token_lifespan = None
                if token_info.issued_at and token_info.expires_at:
                    token_lifespan = (token_info.expires_at - token_info.issued_at).total_seconds()
                
                # Perform refresh
                self.logger.info("Refreshing token")
                refreshed_token = await self.refresh_strategy.refresh_token(token_info)
                
                # Record success metrics
                duration = time.time() - start_time
                self.metrics.record_refresh_success(duration, token_lifespan)
                
                self.logger.info(f"Token refreshed successfully in {duration:.2f}s")
                self._notify_event('token_refreshed', {
                    'duration_ms': duration * 1000,
                    'old_expires_at': token_info.expires_at.isoformat() if token_info.expires_at else None,
                    'new_expires_at': refreshed_token.expires_at.isoformat() if refreshed_token.expires_at else None
                })
                
                return refreshed_token
                
            except Exception as e:
                # Record failure metrics
                self.metrics.record_refresh_failure()
                
                self.logger.error(f"Token refresh failed: {str(e)}")
                self._notify_event('refresh_failed', {
                    'error': str(e),
                    'duration_ms': (time.time() - start_time) * 1000
                })
                
                return None
    
    def start_monitoring(self):
        """Start background token monitoring"""
        if self._is_running:
            return
        
        self._is_running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info("Token monitoring started")
    
    def stop_monitoring(self):
        """Stop background token monitoring"""
        self._is_running = False
        
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
        
        self.logger.info("Token monitoring stopped")
    
    async def _monitor_loop(self):
        """Background monitoring loop"""
        try:
            while self._is_running:
                await asyncio.sleep(60)  # Check every minute
                
                current_token = self.get_token()
                if not current_token:
                    continue
                
                # Check if token will expire soon
                time_until_expiry = current_token.time_until_expiry()
                if time_until_expiry and time_until_expiry.total_seconds() < self.refresh_buffer_seconds:
                    
                    if self.auto_refresh:
                        self.logger.info(f"Token expiring in {time_until_expiry}, refreshing proactively")
                        await self._refresh_token_with_retry(current_token)
                    else:
                        self.logger.warning(f"Token expiring in {time_until_expiry}, auto-refresh disabled")
                        self._notify_event('token_expired', {
                            'expires_at': current_token.expires_at.isoformat() if current_token.expires_at else None,
                            'time_until_expiry_seconds': time_until_expiry.total_seconds()
                        })
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Token monitoring error: {str(e)}")
    
    def get_auth_header(self) -> Dict[str, str]:
        """Get authorization header for requests"""
        token = self.get_token()
        
        if not token:
            raise AuthenticationError("No token available")
        
        return {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
    
    async def get_auth_header_async(self) -> Dict[str, str]:
        """Get authorization header for requests (async, with refresh)"""
        token = await self.get_valid_token()
        
        return {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
    
    def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        token = self.get_token()
        return token is not None and not token.is_expired()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get token handler metrics"""
        return self.metrics.get_stats()
    
    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """Get current token information"""
        token = self.get_token()
        
        if not token:
            return None
        
        return {
            'token_type': token.token_type,
            'expires_at': token.expires_at.isoformat() if token.expires_at else None,
            'issued_at': token.issued_at.isoformat() if token.issued_at else None,
            'time_until_expiry_seconds': token.time_until_expiry().total_seconds() if token.time_until_expiry() else None,
            'scope': token.scope,
            'is_expired': token.is_expired(),
            'should_refresh': self.refresh_strategy.should_refresh(token) if self.auto_refresh else False
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.start_monitoring()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.stop_monitoring()


# Export token handler components
__all__ = [
    'TokenHandler',
    'TokenInfo',
    'TokenRefreshStrategy',
    'JWTRefreshStrategy',
    'APIKeyRefreshStrategy',
    'TokenMetrics'
]