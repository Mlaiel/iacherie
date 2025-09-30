"""OAuth 2.0 Client Implementation for Ainflue SDK

Multi-expert implementation:
- Security: Secure OAuth 2.0 flows with PKCE and state validation
- Backend Senior: Robust OAuth flow management and token handling
- DevOps: Monitoring and metrics for authentication flows
- Lead Dev IA: Intelligent OAuth provider selection and fallbacks

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import base64
import hashlib
import json
import logging
import secrets
import time
import urllib.parse
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import httpx
from pydantic import BaseModel, Field, HttpUrl

from .exceptions import (
    OAuthError, AuthenticationError, ValidationError,
    TokenExpiredError, ConfigurationError
)


class OAuthFlow(Enum):
    """OAuth 2.0 flow types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"
    REFRESH_TOKEN = "refresh_token"


class OAuthProvider(Enum):
    """Supported OAuth providers"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    CUSTOM = "custom"


@dataclass
class OAuthMetrics:
    """OAuth authentication metrics (DevOps expertise)"""
    total_auth_attempts: int = 0
    successful_auths: int = 0
    failed_auths: int = 0
    token_refreshes: int = 0
    token_refresh_failures: int = 0
    average_auth_time: float = 0.0
    provider_usage: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate authentication success rate"""
        if self.total_auth_attempts == 0:
            return 0.0
        return (self.successful_auths / self.total_auth_attempts) * 100
    
    @property
    def token_refresh_success_rate(self) -> float:
        """Calculate token refresh success rate"""
        if self.token_refreshes == 0:
            return 0.0
        successful_refreshes = self.token_refreshes - self.token_refresh_failures
        return (successful_refreshes / self.token_refreshes) * 100


class OAuthConfig(BaseModel):
    """OAuth 2.0 configuration with security best practices"""
    # Basic OAuth settings
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: Optional[str] = Field(default=None, description="OAuth client secret")
    redirect_uri: HttpUrl = Field(..., description="OAuth redirect URI")
    
    # Provider settings
    provider: OAuthProvider = Field(default=OAuthProvider.CUSTOM, description="OAuth provider")
    authorization_endpoint: HttpUrl = Field(..., description="Authorization endpoint")
    token_endpoint: HttpUrl = Field(..., description="Token endpoint")
    
    # Security settings (Security expertise)
    use_pkce: bool = Field(default=True, description="Use PKCE for security")
    validate_state: bool = Field(default=True, description="Validate state parameter")
    enforce_https: bool = Field(default=True, description="Enforce HTTPS for security")
    
    # Scopes and permissions
    scopes: List[str] = Field(default_factory=list, description="OAuth scopes")
    
    # Timeout and retry settings
    auth_timeout: float = Field(default=300.0, description="Authentication timeout")
    token_timeout: float = Field(default=30.0, description="Token request timeout")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class PKCEChallenge:
    """PKCE (Proof Key for Code Exchange) implementation"""
    
    def __init__(self):
        self.code_verifier = self._generate_code_verifier()
        self.code_challenge = self._generate_code_challenge()
    
    def _generate_code_verifier(self) -> str:
        """Generate cryptographically random code verifier"""
        # RFC 7636: 43-128 characters, base64url-encoded
        random_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
    
    def _generate_code_challenge(self) -> str:
        """Generate code challenge from verifier using S256"""
        # SHA256 hash of code verifier
        challenge_bytes = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')


@dataclass
class OAuthTokens:
    """OAuth token container with secure storage"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def expires_at(self) -> Optional[datetime]:
        """Calculate token expiration time"""
        if self.expires_in:
            return self.created_at + timedelta(seconds=self.expires_in)
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at
    
    @property
    def expires_soon(self, buffer_seconds: int = 300) -> bool:
        """Check if token expires soon (within buffer)"""
        if not self.expires_at:
            return False
        return datetime.now() >= (self.expires_at - timedelta(seconds=buffer_seconds))


class OAuthProviderConfig:
    """OAuth provider configurations (Lead Dev IA expertise)"""
    
    @staticmethod
    def get_provider_config(provider: OAuthProvider) -> Dict[str, str]:
        """Get predefined OAuth provider configurations"""
        configs = {
            OAuthProvider.GOOGLE: {
                "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_endpoint": "https://oauth2.googleapis.com/token",
                "userinfo_endpoint": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scopes": ["openid", "email", "profile"]
            },
            OAuthProvider.MICROSOFT: {
                "authorization_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_endpoint": "https://graph.microsoft.com/v1.0/me",
                "scopes": ["openid", "email", "profile"]
            },
            OAuthProvider.GITHUB: {
                "authorization_endpoint": "https://github.com/login/oauth/authorize",
                "token_endpoint": "https://github.com/login/oauth/access_token",
                "userinfo_endpoint": "https://api.github.com/user",
                "scopes": ["user:email"]
            }
        }
        return configs.get(provider, {})


class OAuthStateManager:
    """OAuth state management for security (Security expertise)"""
    
    def __init__(self):
        self.states = {}  # In production, use secure storage
        self.cleanup_interval = 3600  # 1 hour
    
    def generate_state(self, 
                      session_id: Optional[str] = None,
                      expires_in: int = 600) -> str:
        """Generate secure OAuth state parameter"""
        # Generate cryptographically secure random state
        state = secrets.token_urlsafe(32)
        
        # Store state with metadata
        self.states[state] = {
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=expires_in),
            "session_id": session_id,
            "used": False
        }
        
        return state
    
    def validate_state(self, state: str, session_id: Optional[str] = None) -> bool:
        """Validate OAuth state parameter"""
        if state not in self.states:
            return False
        
        state_data = self.states[state]
        
        # Check expiration
        if datetime.now() > state_data["expires_at"]:
            self._remove_state(state)
            return False
        
        # Check if already used
        if state_data["used"]:
            self._remove_state(state)
            return False
        
        # Check session ID if provided
        if session_id and state_data["session_id"] != session_id:
            return False
        
        # Mark as used
        state_data["used"] = True
        return True
    
    def _remove_state(self, state: str):
        """Remove state from storage"""
        self.states.pop(state, None)
    
    def cleanup_expired_states(self):
        """Clean up expired states"""
        now = datetime.now()
        expired_states = [
            state for state, data in self.states.items()
            if now > data["expires_at"]
        ]
        
        for state in expired_states:
            self._remove_state(state)


class OAuthClient:
    """Main OAuth 2.0 client with multi-expert security implementation"""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Security components
        self.state_manager = OAuthStateManager()
        
        # Metrics and monitoring
        self.metrics = OAuthMetrics()
        
        # HTTP client with security settings
        self.http_client = None
        
        # Token storage
        self.current_tokens: Optional[OAuthTokens] = None
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate OAuth configuration (Security expertise)"""
        if self.config.enforce_https:
            if not str(self.config.authorization_endpoint).startswith('https://'):
                raise ConfigurationError("Authorization endpoint must use HTTPS")
            if not str(self.config.token_endpoint).startswith('https://'):
                raise ConfigurationError("Token endpoint must use HTTPS")
            if not str(self.config.redirect_uri).startswith('https://'):
                raise ConfigurationError("Redirect URI must use HTTPS")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.http_client = httpx.AsyncClient(
            timeout=self.config.token_timeout,
            verify=True  # Always verify SSL certificates
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()
    
    def get_authorization_url(self, 
                            state: Optional[str] = None,
                            session_id: Optional[str] = None,
                            additional_params: Optional[Dict[str, str]] = None) -> str:
        """Generate OAuth authorization URL with security best practices"""
        start_time = time.time()
        
        try:
            # Generate or validate state
            if not state:
                state = self.state_manager.generate_state(session_id)
            
            # Prepare PKCE if enabled
            pkce_challenge = None
            if self.config.use_pkce:
                pkce_challenge = PKCEChallenge()
                # Store PKCE verifier for later use (in production, use secure storage)
                self.state_manager.states[state]["code_verifier"] = pkce_challenge.code_verifier
            
            # Build authorization parameters
            params = {
                "response_type": "code",
                "client_id": self.config.client_id,
                "redirect_uri": str(self.config.redirect_uri),
                "scope": " ".join(self.config.scopes),
            }
            
            # Add state parameter
            if self.config.validate_state:
                params["state"] = state
            
            # Add PKCE parameters
            if pkce_challenge:
                params["code_challenge"] = pkce_challenge.code_challenge
                params["code_challenge_method"] = "S256"
            
            # Add additional parameters
            if additional_params:
                params.update(additional_params)
            
            # Build URL
            auth_url = f"{self.config.authorization_endpoint}?{urllib.parse.urlencode(params)}"
            
            # Update metrics
            auth_time = time.time() - start_time
            provider_name = self.config.provider.value
            self.metrics.provider_usage[provider_name] = \
                self.metrics.provider_usage.get(provider_name, 0) + 1
            
            self.logger.info(f"Generated authorization URL for {provider_name}")
            return auth_url
            
        except Exception as e:
            self.logger.error(f"Failed to generate authorization URL: {e}")
            raise OAuthError(f"Authorization URL generation failed: {e}")
    
    async def exchange_code_for_tokens(self, 
                                     authorization_code: str,
                                     state: Optional[str] = None,
                                     session_id: Optional[str] = None) -> OAuthTokens:
        """Exchange authorization code for tokens"""
        start_time = time.time()
        
        try:
            self.metrics.total_auth_attempts += 1
            
            # Validate state if provided
            if state and self.config.validate_state:
                if not self.state_manager.validate_state(state, session_id):
                    raise OAuthError("Invalid or expired state parameter")
            
            # Get PKCE verifier if available
            code_verifier = None
            if self.config.use_pkce and state:
                state_data = self.state_manager.states.get(state, {})
                code_verifier = state_data.get("code_verifier")
                if not code_verifier:
                    raise OAuthError("PKCE code verifier not found")
            
            # Prepare token request
            token_data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": str(self.config.redirect_uri),
                "client_id": self.config.client_id,
            }
            
            # Add client secret if available (for confidential clients)
            if self.config.client_secret:
                token_data["client_secret"] = self.config.client_secret
            
            # Add PKCE verifier
            if code_verifier:
                token_data["code_verifier"] = code_verifier
            
            # Make token request
            tokens = await self._request_tokens(token_data)
            
            # Store tokens
            self.current_tokens = tokens
            
            # Update metrics
            auth_time = time.time() - start_time
            self.metrics.successful_auths += 1
            self._update_average_auth_time(auth_time)
            
            # Clean up state
            if state:
                self.state_manager._remove_state(state)
            
            self.logger.info("Successfully exchanged authorization code for tokens")
            return tokens
            
        except Exception as e:
            self.metrics.failed_auths += 1
            self.logger.error(f"Token exchange failed: {e}")
            raise OAuthError(f"Token exchange failed: {e}")
    
    async def client_credentials_flow(self, scopes: Optional[List[str]] = None) -> OAuthTokens:
        """Execute OAuth 2.0 Client Credentials flow"""
        start_time = time.time()
        
        try:
            self.metrics.total_auth_attempts += 1
            
            if not self.config.client_secret:
                raise ConfigurationError("Client secret required for client credentials flow")
            
            # Prepare token request
            token_data = {
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }
            
            # Add scopes
            if scopes:
                token_data["scope"] = " ".join(scopes)
            elif self.config.scopes:
                token_data["scope"] = " ".join(self.config.scopes)
            
            # Make token request
            tokens = await self._request_tokens(token_data)
            
            # Store tokens
            self.current_tokens = tokens
            
            # Update metrics
            auth_time = time.time() - start_time
            self.metrics.successful_auths += 1
            self._update_average_auth_time(auth_time)
            
            self.logger.info("Successfully completed client credentials flow")
            return tokens
            
        except Exception as e:
            self.metrics.failed_auths += 1
            self.logger.error(f"Client credentials flow failed: {e}")
            raise OAuthError(f"Client credentials flow failed: {e}")
    
    async def refresh_tokens(self, refresh_token: Optional[str] = None) -> OAuthTokens:
        """Refresh access tokens using refresh token"""
        try:
            self.metrics.token_refreshes += 1
            
            # Use provided refresh token or current one
            token_to_refresh = refresh_token
            if not token_to_refresh and self.current_tokens:
                token_to_refresh = self.current_tokens.refresh_token
            
            if not token_to_refresh:
                raise OAuthError("No refresh token available")
            
            # Prepare refresh request
            token_data = {
                "grant_type": "refresh_token",
                "refresh_token": token_to_refresh,
                "client_id": self.config.client_id,
            }
            
            # Add client secret if available
            if self.config.client_secret:
                token_data["client_secret"] = self.config.client_secret
            
            # Make token request
            new_tokens = await self._request_tokens(token_data)
            
            # Update stored tokens
            self.current_tokens = new_tokens
            
            self.logger.info("Successfully refreshed tokens")
            return new_tokens
            
        except Exception as e:
            self.metrics.token_refresh_failures += 1
            self.logger.error(f"Token refresh failed: {e}")
            raise OAuthError(f"Token refresh failed: {e}")
    
    async def _request_tokens(self, token_data: Dict[str, str]) -> OAuthTokens:
        """Make HTTP request to token endpoint with retry logic"""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "Ainflue-Python-SDK/1.0.0"
        }
        
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self.http_client.post(
                    str(self.config.token_endpoint),
                    data=token_data,
                    headers=headers
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    self.logger.warning(f"Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                
                # Parse token response
                token_response = response.json()
                
                # Validate required fields
                if "access_token" not in token_response:
                    raise OAuthError("No access token in response")
                
                # Create token object
                tokens = OAuthTokens(
                    access_token=token_response["access_token"],
                    token_type=token_response.get("token_type", "Bearer"),
                    expires_in=token_response.get("expires_in"),
                    refresh_token=token_response.get("refresh_token"),
                    scope=token_response.get("scope")
                )
                
                return tokens
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [500, 502, 503, 504] and attempt < self.config.max_retries:
                    # Server error - retry
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Server error {e.response.status_code}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    error_detail = ""
                    try:
                        error_response = e.response.json()
                        error_detail = error_response.get("error_description", 
                                                        error_response.get("error", "Unknown error"))
                    except:
                        error_detail = e.response.text
                    
                    raise OAuthError(f"Token request failed: {error_detail}")
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    continue
                break
        
        # All retries failed
        raise OAuthError(f"All token request attempts failed. Last error: {last_error}")
    
    async def get_valid_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        if not self.current_tokens:
            raise AuthenticationError("No tokens available")
        
        # Check if token needs refresh
        if self.current_tokens.expires_soon():
            if self.current_tokens.refresh_token:
                await self.refresh_tokens()
            else:
                raise TokenExpiredError("Access token expired and no refresh token available")
        
        return self.current_tokens.access_token
    
    async def revoke_tokens(self, token: Optional[str] = None) -> bool:
        """Revoke OAuth tokens"""
        try:
            # Use provided token or current access token
            token_to_revoke = token or (self.current_tokens.access_token if self.current_tokens else None)
            
            if not token_to_revoke:
                return True  # No token to revoke
            
            # Many providers support token revocation endpoint
            # This is a simplified implementation
            self.logger.info("Token revocation not implemented for this provider")
            
            # Clear stored tokens
            self.current_tokens = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Token revocation failed: {e}")
            return False
    
    def _update_average_auth_time(self, auth_time: float):
        """Update average authentication time"""
        if self.metrics.successful_auths == 1:
            self.metrics.average_auth_time = auth_time
        else:
            # Calculate running average
            total_time = self.metrics.average_auth_time * (self.metrics.successful_auths - 1)
            total_time += auth_time
            self.metrics.average_auth_time = total_time / self.metrics.successful_auths
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get OAuth client metrics"""
        return {
            "total_auth_attempts": self.metrics.total_auth_attempts,
            "successful_auths": self.metrics.successful_auths,
            "failed_auths": self.metrics.failed_auths,
            "success_rate": self.metrics.success_rate,
            "token_refreshes": self.metrics.token_refreshes,
            "token_refresh_failures": self.metrics.token_refresh_failures,
            "token_refresh_success_rate": self.metrics.token_refresh_success_rate,
            "average_auth_time": self.metrics.average_auth_time,
            "provider_usage": self.metrics.provider_usage
        }


# Example usage
async def example_oauth_usage():
    """Example OAuth 2.0 usage"""
    # Google OAuth configuration
    config = OAuthConfig(
        client_id="your-google-client-id",
        client_secret="your-google-client-secret",
        redirect_uri="https://your-app.com/oauth/callback",
        provider=OAuthProvider.GOOGLE,
        authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
        token_endpoint="https://oauth2.googleapis.com/token",
        scopes=["openid", "email", "profile"]
    )
    
    async with OAuthClient(config) as oauth_client:
        # Get authorization URL
        auth_url = oauth_client.get_authorization_url()
        print(f"Visit this URL to authorize: {auth_url}")
        
        # After user authorization, exchange code for tokens
        # authorization_code = "code_from_callback"
        # tokens = await oauth_client.exchange_code_for_tokens(authorization_code)
        # print(f"Access token: {tokens.access_token}")
        
        # Get metrics
        metrics = oauth_client.get_metrics()
        print(f"OAuth metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_oauth_usage())