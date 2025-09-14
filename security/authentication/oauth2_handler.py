#!/usr/bin/env python3
"""
🔐 OAuth2 Handler - Enterprise Security Module
==============================================

Ultra-secure OAuth2.0 implementation with PKCE, state validation,
and enterprise-grade security features.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Backend + API + DevOps
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import base64
import hashlib
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from urllib.parse import urlencode, parse_qs, urlparse

import aiohttp
import redis
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class OAuth2Provider(Enum):
    """Supported OAuth2 providers"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    APPLE = "apple"
    CUSTOM = "custom"

class OAuth2GrantType(Enum):
    """OAuth2 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"

@dataclass
class OAuth2SecurityConfig:
    """OAuth2 security configuration"""
    provider: OAuth2Provider
    client_id: str
    client_secret: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    redirect_uri: str
    scopes: List[str] = field(default_factory=list)
    use_pkce: bool = True
    use_state: bool = True
    token_endpoint_auth_method: str = "client_secret_basic"
    jwks_uri: Optional[str] = None
    issuer: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OAuth2Token:
    """OAuth2 token data"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    provider: Optional[OAuth2Provider] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OAuth2AuthorizationRequest:
    """OAuth2 authorization request data"""
    state: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    code_verifier: str = field(default_factory=lambda: secrets.token_urlsafe(128))
    code_challenge: str = ""
    redirect_uri: str = ""
    scopes: List[str] = field(default_factory=list)
    provider: Optional[OAuth2Provider] = None
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=10))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OAuth2UserInfo:
    """OAuth2 user information"""
    provider_user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    verified_email: bool = False
    provider: Optional[OAuth2Provider] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

class OAuth2Handler:
    """
    Enterprise-grade OAuth2.0 handler with advanced security features.
    
    Features:
    - PKCE (Proof Key for Code Exchange) support
    - State parameter validation
    - Multiple provider support
    - Token lifecycle management
    - Security event logging
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        encryption_key: Optional[bytes] = None
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.providers: Dict[OAuth2Provider, OAuth2SecurityConfig] = {}
        
        # Security configuration
        self.config = {
            "state_expiry": 600,  # 10 minutes
            "token_cache_expiry": 3600,  # 1 hour
            "max_authorization_attempts": 5,
            "enable_token_encryption": True,
            "require_https": True,
            "validate_redirect_uri": True,
            "log_all_events": True,
        }

    async def initialize(self) -> None:
        """Initialize the OAuth2 handler"""
        try:
            # Initialize Redis connection
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            
            logger.info("OAuth2 handler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OAuth2 handler: {e}")
            raise

    def register_provider(
        self,
        provider: OAuth2Provider,
        config: OAuth2SecurityConfig
    ) -> None:
        """Register OAuth2 provider configuration"""
        try:
            # Validate configuration
            self._validate_provider_config(config)
            
            # Store provider configuration
            self.providers[provider] = config
            
            logger.info(f"Registered OAuth2 provider: {provider.value}")
            
        except Exception as e:
            logger.error(f"Failed to register provider {provider.value}: {e}")
            raise

    async def create_authorization_url(
        self,
        provider: OAuth2Provider,
        user_id: Optional[str] = None,
        additional_scopes: List[str] = None,
        custom_state: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Create OAuth2 authorization URL.
        
        Args:
            provider: OAuth2 provider
            user_id: User identifier (optional)
            additional_scopes: Additional scopes to request
            custom_state: Custom state parameter
            
        Returns:
            Tuple[str, str]: (authorization_url, state)
        """
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider {provider.value} not registered")
                
            config = self.providers[provider]
            
            # Create authorization request
            auth_request = OAuth2AuthorizationRequest(
                provider=provider,
                user_id=user_id,
                redirect_uri=config.redirect_uri,
                scopes=config.scopes + (additional_scopes or [])
            )
            
            # Use custom state if provided
            if custom_state:
                auth_request.state = custom_state
            
            # Generate PKCE challenge if enabled
            if config.use_pkce:
                auth_request.code_challenge = self._generate_code_challenge(auth_request.code_verifier)
            
            # Store authorization request
            await self._store_authorization_request(auth_request)
            
            # Build authorization URL
            params = {
                "response_type": "code",
                "client_id": config.client_id,
                "redirect_uri": config.redirect_uri,
                "scope": " ".join(auth_request.scopes),
            }
            
            if config.use_state:
                params["state"] = auth_request.state
                
            if config.use_pkce:
                params["code_challenge"] = auth_request.code_challenge
                params["code_challenge_method"] = "S256"
            
            # Add additional parameters
            params.update(config.additional_params)
            
            authorization_url = f"{config.authorization_endpoint}?{urlencode(params)}"
            
            await self._log_oauth2_event(
                "authorization_request_created",
                provider,
                user_id,
                {"state": auth_request.state}
            )
            
            return authorization_url, auth_request.state
            
        except Exception as e:
            logger.error(f"Failed to create authorization URL for {provider.value}: {e}")
            raise

    async def handle_authorization_callback(
        self,
        provider: OAuth2Provider,
        authorization_code: str,
        state: str,
        redirect_uri: Optional[str] = None
    ) -> Tuple[OAuth2Token, OAuth2UserInfo]:
        """
        Handle OAuth2 authorization callback.
        
        Args:
            provider: OAuth2 provider
            authorization_code: Authorization code from callback
            state: State parameter from callback
            redirect_uri: Redirect URI (if different from registered)
            
        Returns:
            Tuple[OAuth2Token, OAuth2UserInfo]: Token and user information
        """
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider {provider.value} not registered")
                
            config = self.providers[provider]
            
            # Validate and retrieve authorization request
            auth_request = await self._get_authorization_request(state)
            if not auth_request:
                raise ValueError("Invalid or expired state parameter")
            
            # Validate redirect URI if required
            if self.config["validate_redirect_uri"]:
                expected_uri = redirect_uri or config.redirect_uri
                if auth_request.redirect_uri != expected_uri:
                    raise ValueError("Redirect URI mismatch")
            
            # Exchange authorization code for token
            token = await self._exchange_code_for_token(
                config, authorization_code, auth_request
            )
            
            # Get user information
            user_info = await self._get_user_info(config, token)
            
            # Store token
            await self._store_token(token)
            
            # Clean up authorization request
            await self._cleanup_authorization_request(state)
            
            await self._log_oauth2_event(
                "authorization_callback_success",
                provider,
                auth_request.user_id,
                {
                    "state": state,
                    "user_id": user_info.provider_user_id
                }
            )
            
            return token, user_info
            
        except Exception as e:
            logger.error(f"OAuth2 callback failed for {provider.value}: {e}")
            await self._log_oauth2_event(
                "authorization_callback_error",
                provider,
                None,
                {"state": state, "error": str(e)}
            )
            raise

    async def refresh_access_token(
        self,
        provider: OAuth2Provider,
        refresh_token: str
    ) -> OAuth2Token:
        """
        Refresh OAuth2 access token.
        
        Args:
            provider: OAuth2 provider
            refresh_token: Refresh token
            
        Returns:
            OAuth2Token: New access token
        """
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider {provider.value} not registered")
                
            config = self.providers[provider]
            
            # Prepare token refresh request
            token_data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": config.client_id,
            }
            
            # Add client authentication
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            if config.token_endpoint_auth_method == "client_secret_basic":
                auth_string = f"{config.client_id}:{config.client_secret}"
                auth_bytes = base64.b64encode(auth_string.encode()).decode()
                headers["Authorization"] = f"Basic {auth_bytes}"
            elif config.token_endpoint_auth_method == "client_secret_post":
                token_data["client_secret"] = config.client_secret
            
            # Make token refresh request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.token_endpoint,
                    data=token_data,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Token refresh failed: {error_text}")
                    
                    token_response = await response.json()
            
            # Create new token object
            new_token = OAuth2Token(
                access_token=token_response["access_token"],
                token_type=token_response.get("token_type", "Bearer"),
                expires_in=token_response.get("expires_in"),
                refresh_token=token_response.get("refresh_token", refresh_token),
                scope=token_response.get("scope"),
                id_token=token_response.get("id_token"),
                provider=provider
            )
            
            # Calculate expiration
            if new_token.expires_in:
                new_token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=new_token.expires_in)
            
            # Store refreshed token
            await self._store_token(new_token)
            
            await self._log_oauth2_event(
                "token_refresh_success",
                provider,
                None,
                {"expires_in": new_token.expires_in}
            )
            
            return new_token
            
        except Exception as e:
            logger.error(f"Token refresh failed for {provider.value}: {e}")
            await self._log_oauth2_event(
                "token_refresh_error",
                provider,
                None,
                {"error": str(e)}
            )
            raise

    async def revoke_token(
        self,
        provider: OAuth2Provider,
        token: str,
        token_type_hint: str = "access_token"
    ) -> bool:
        """
        Revoke OAuth2 token.
        
        Args:
            provider: OAuth2 provider
            token: Token to revoke
            token_type_hint: Hint about token type
            
        Returns:
            bool: True if revoked successfully
        """
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider {provider.value} not registered")
                
            config = self.providers[provider]
            
            # Not all providers support token revocation
            if not hasattr(config, 'revocation_endpoint'):
                logger.warning(f"Provider {provider.value} does not support token revocation")
                return False
            
            # Prepare revocation request
            revoke_data = {
                "token": token,
                "token_type_hint": token_type_hint
            }
            
            # Add client authentication
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            if config.token_endpoint_auth_method == "client_secret_basic":
                auth_string = f"{config.client_id}:{config.client_secret}"
                auth_bytes = base64.b64encode(auth_string.encode()).decode()
                headers["Authorization"] = f"Basic {auth_bytes}"
            elif config.token_endpoint_auth_method == "client_secret_post":
                revoke_data["client_id"] = config.client_id
                revoke_data["client_secret"] = config.client_secret
            
            # Make revocation request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.revocation_endpoint,
                    data=revoke_data,
                    headers=headers
                ) as response:
                    # RFC 7009: successful revocation returns 200
                    success = response.status == 200
                    
                    if success:
                        await self._log_oauth2_event(
                            "token_revocation_success",
                            provider,
                            None,
                            {"token_type_hint": token_type_hint}
                        )
                    else:
                        error_text = await response.text()
                        logger.warning(f"Token revocation failed: {error_text}")
                    
                    return success
                    
        except Exception as e:
            logger.error(f"Token revocation failed for {provider.value}: {e}")
            return False

    def _validate_provider_config(self, config: OAuth2SecurityConfig) -> None:
        """Validate provider configuration"""
        required_fields = [
            "client_id", "client_secret", "authorization_endpoint",
            "token_endpoint", "redirect_uri"
        ]
        
        for field in required_fields:
            if not getattr(config, field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validate HTTPS requirement
        if self.config["require_https"]:
            for endpoint in [config.authorization_endpoint, config.token_endpoint, config.redirect_uri]:
                if not endpoint.startswith("https://"):
                    raise ValueError(f"HTTPS required for endpoint: {endpoint}")

    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge"""
        try:
            # SHA256 hash of code verifier
            code_challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
            # Base64 URL encode without padding
            code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode().rstrip("=")
            return code_challenge
        except Exception as e:
            logger.error(f"Failed to generate code challenge: {e}")
            raise

    async def _store_authorization_request(self, auth_request: OAuth2AuthorizationRequest) -> None:
        """Store authorization request in Redis"""
        try:
            request_key = f"oauth2_auth_request:{auth_request.state}"
            request_data = {
                "state": auth_request.state,
                "code_verifier": auth_request.code_verifier,
                "code_challenge": auth_request.code_challenge,
                "redirect_uri": auth_request.redirect_uri,
                "scopes": auth_request.scopes,
                "provider": auth_request.provider.value if auth_request.provider else None,
                "user_id": auth_request.user_id,
                "created_at": auth_request.created_at.isoformat(),
                "expires_at": auth_request.expires_at.isoformat(),
                "metadata": auth_request.metadata
            }
            
            request_json = json.dumps(request_data, default=str)
            
            # Encrypt if enabled
            if self.config["enable_token_encryption"]:
                request_json = self.cipher_suite.encrypt(request_json.encode())
            else:
                request_json = request_json.encode()
            
            await self.redis.setex(
                request_key,
                self.config["state_expiry"],
                request_json
            )
            
        except Exception as e:
            logger.error(f"Failed to store authorization request: {e}")
            raise

    async def _get_authorization_request(self, state: str) -> Optional[OAuth2AuthorizationRequest]:
        """Retrieve authorization request from Redis"""
        try:
            request_key = f"oauth2_auth_request:{state}"
            request_data = await self.redis.get(request_key)
            
            if not request_data:
                return None
            
            # Decrypt if needed
            if self.config["enable_token_encryption"]:
                request_data = self.cipher_suite.decrypt(request_data)
            
            request_dict = json.loads(request_data)
            
            auth_request = OAuth2AuthorizationRequest(
                state=request_dict["state"],
                code_verifier=request_dict["code_verifier"],
                code_challenge=request_dict["code_challenge"],
                redirect_uri=request_dict["redirect_uri"],
                scopes=request_dict["scopes"],
                provider=OAuth2Provider(request_dict["provider"]) if request_dict["provider"] else None,
                user_id=request_dict["user_id"],
                created_at=datetime.fromisoformat(request_dict["created_at"]),
                expires_at=datetime.fromisoformat(request_dict["expires_at"]),
                metadata=request_dict["metadata"]
            )
            
            # Check expiration
            if datetime.now(timezone.utc) > auth_request.expires_at:
                await self._cleanup_authorization_request(state)
                return None
            
            return auth_request
            
        except Exception as e:
            logger.error(f"Failed to get authorization request: {e}")
            return None

    async def _cleanup_authorization_request(self, state: str) -> None:
        """Clean up authorization request"""
        try:
            request_key = f"oauth2_auth_request:{state}"
            await self.redis.delete(request_key)
        except Exception as e:
            logger.error(f"Failed to cleanup authorization request: {e}")

    async def _exchange_code_for_token(
        self,
        config: OAuth2SecurityConfig,
        authorization_code: str,
        auth_request: OAuth2AuthorizationRequest
    ) -> OAuth2Token:
        """Exchange authorization code for access token"""
        try:
            # Prepare token request
            token_data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": auth_request.redirect_uri,
                "client_id": config.client_id,
            }
            
            # Add PKCE verifier if used
            if config.use_pkce:
                token_data["code_verifier"] = auth_request.code_verifier
            
            # Add client authentication
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            if config.token_endpoint_auth_method == "client_secret_basic":
                auth_string = f"{config.client_id}:{config.client_secret}"
                auth_bytes = base64.b64encode(auth_string.encode()).decode()
                headers["Authorization"] = f"Basic {auth_bytes}"
            elif config.token_endpoint_auth_method == "client_secret_post":
                token_data["client_secret"] = config.client_secret
            
            # Make token request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.token_endpoint,
                    data=token_data,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Token exchange failed: {error_text}")
                    
                    token_response = await response.json()
            
            # Create token object
            token = OAuth2Token(
                access_token=token_response["access_token"],
                token_type=token_response.get("token_type", "Bearer"),
                expires_in=token_response.get("expires_in"),
                refresh_token=token_response.get("refresh_token"),
                scope=token_response.get("scope"),
                id_token=token_response.get("id_token"),
                provider=config.provider,
                user_id=auth_request.user_id
            )
            
            # Calculate expiration
            if token.expires_in:
                token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=token.expires_in)
            
            return token
            
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            raise

    async def _get_user_info(
        self,
        config: OAuth2SecurityConfig,
        token: OAuth2Token
    ) -> OAuth2UserInfo:
        """Get user information from provider"""
        try:
            headers = {
                "Authorization": f"{token.token_type} {token.access_token}",
                "Accept": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    config.userinfo_endpoint,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"User info request failed: {error_text}")
                    
                    user_data = await response.json()
            
            # Parse user information based on provider
            user_info = self._parse_user_info(config.provider, user_data)
            user_info.provider = config.provider
            user_info.raw_data = user_data
            
            return user_info
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise

    def _parse_user_info(self, provider: OAuth2Provider, user_data: Dict[str, Any]) -> OAuth2UserInfo:
        """Parse user information based on provider format"""
        try:
            if provider == OAuth2Provider.GOOGLE:
                return OAuth2UserInfo(
                    provider_user_id=user_data["sub"],
                    email=user_data.get("email"),
                    name=user_data.get("name"),
                    given_name=user_data.get("given_name"),
                    family_name=user_data.get("family_name"),
                    picture=user_data.get("picture"),
                    locale=user_data.get("locale"),
                    verified_email=user_data.get("email_verified", False)
                )
            elif provider == OAuth2Provider.MICROSOFT:
                return OAuth2UserInfo(
                    provider_user_id=user_data["id"],
                    email=user_data.get("mail") or user_data.get("userPrincipalName"),
                    name=user_data.get("displayName"),
                    given_name=user_data.get("givenName"),
                    family_name=user_data.get("surname"),
                    verified_email=True  # Microsoft emails are verified
                )
            elif provider == OAuth2Provider.GITHUB:
                return OAuth2UserInfo(
                    provider_user_id=str(user_data["id"]),
                    email=user_data.get("email"),
                    name=user_data.get("name"),
                    picture=user_data.get("avatar_url"),
                    verified_email=user_data.get("verified", False)
                )
            else:
                # Generic parsing for other providers
                return OAuth2UserInfo(
                    provider_user_id=str(user_data.get("id", user_data.get("sub", "unknown"))),
                    email=user_data.get("email"),
                    name=user_data.get("name"),
                    given_name=user_data.get("given_name"),
                    family_name=user_data.get("family_name"),
                    picture=user_data.get("picture"),
                    locale=user_data.get("locale"),
                    verified_email=user_data.get("email_verified", False)
                )
                
        except Exception as e:
            logger.error(f"Failed to parse user info for {provider.value}: {e}")
            # Return minimal user info
            return OAuth2UserInfo(
                provider_user_id=str(user_data.get("id", "unknown"))
            )

    async def _store_token(self, token: OAuth2Token) -> None:
        """Store OAuth2 token in Redis"""
        try:
            token_key = f"oauth2_token:{token.access_token[:16]}"  # Use first 16 chars as key
            token_data = {
                "access_token": token.access_token,
                "token_type": token.token_type,
                "expires_in": token.expires_in,
                "refresh_token": token.refresh_token,
                "scope": token.scope,
                "id_token": token.id_token,
                "issued_at": token.issued_at.isoformat(),
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "provider": token.provider.value if token.provider else None,
                "user_id": token.user_id,
                "metadata": token.metadata
            }
            
            token_json = json.dumps(token_data, default=str)
            
            # Encrypt if enabled
            if self.config["enable_token_encryption"]:
                token_json = self.cipher_suite.encrypt(token_json.encode())
            else:
                token_json = token_json.encode()
            
            # Set expiry
            expiry = self.config["token_cache_expiry"]
            if token.expires_at:
                calculated_expiry = int((token.expires_at - datetime.now(timezone.utc)).total_seconds())
                expiry = min(expiry, max(60, calculated_expiry))
            
            await self.redis.setex(token_key, expiry, token_json)
            
        except Exception as e:
            logger.error(f"Failed to store token: {e}")

    async def _log_oauth2_event(
        self,
        event_type: str,
        provider: OAuth2Provider,
        user_id: Optional[str],
        details: Dict[str, Any]
    ) -> None:
        """Log OAuth2 security event"""
        try:
            if not self.config["log_all_events"]:
                return
                
            event_data = {
                "event_type": event_type,
                "provider": provider.value,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": details
            }
            
            event_key = f"oauth2_event:{int(time.time())}:{secrets.token_hex(8)}"
            await self.redis.setex(
                event_key,
                86400 * 7,  # Keep for 7 days
                json.dumps(event_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to log OAuth2 event: {e}")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()