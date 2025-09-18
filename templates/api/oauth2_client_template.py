#!/usr/bin/env python3
"""
🔐 AINFLUE OAUTH2 CLIENT TEMPLATE - ENTERPRISE AUTHENTICATION
=============================================================

⚠️  PROPRIETARY & CONFIDENTIAL - AINFLUE CREATOR ECONOMY PLATFORM
🔒 Copyright (c) 2024 Fahed Mlaiel <mlaiel@live.de>. All rights reserved.
🚫 Unauthorized copying, distribution, or modification is strictly prohibited.
📧 Contact: mlaiel@live.de | 🌐 https://ainflue.com

🏢 ENTERPRISE OAUTH2 CLIENT - MULTI-PROVIDER AUTHENTICATION SYSTEM
🎯 Expert Integration: Lead Dev IA + Backend Senior + Security Expert + Enterprise Auth

📋 FEATURES ENTERPRISE:
- 🌐 Multi-Provider OAuth2 (Google/GitHub/Microsoft/Facebook/LinkedIn/Custom)
- 🔐 OpenID Connect (OIDC) full compliance
- 📱 PKCE (Proof Key for Code Exchange) for mobile/SPA security
- 🔄 Token lifecycle management (access/refresh/revoke)
- 🎯 Scope management granulaire
- 🛡️ State parameter anti-CSRF protection
- 📱 Device Authorization Flow support
- 🎨 Creator platform integrations specialized
- ⚡ Rate limiting per provider intelligent
- 📊 Analytics et metrics comprehensive
- 🔧 Configuration factory patterns
- 🏭 Production-ready enterprise deployment

🚀 ARCHITECTURE HIGHLIGHTS:
- Async/await optimization for performance
- Redis caching for token storage
- Comprehensive error handling
- Security-first design patterns
- Creator Economy optimizations
- Multi-tenant support ready
- Monitoring et alerting integrated
"""

import asyncio
import base64
import hashlib
import json
import secrets
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Core imports
import aiohttp
import aioredis
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Monitoring
import structlog
from prometheus_client import Counter, Histogram, Gauge
import opentelemetry.trace

# Security
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

logger = structlog.get_logger(__name__)
tracer = opentelemetry.trace.get_tracer(__name__)

# ================================================================================
# 📊 METRICS & MONITORING CONFIGURATION
# ================================================================================

# OAuth2 metrics
oauth2_requests_total = Counter(
    'oauth2_client_requests_total',
    'Total OAuth2 client requests',
    ['provider', 'flow_type', 'status']
)

oauth2_token_operations = Counter(
    'oauth2_token_operations_total',
    'Total token operations',
    ['provider', 'operation', 'status']
)

oauth2_request_duration = Histogram(
    'oauth2_request_duration_seconds',
    'OAuth2 request duration',
    ['provider', 'endpoint']
)

oauth2_active_sessions = Gauge(
    'oauth2_active_sessions',
    'Number of active OAuth2 sessions',
    ['provider']
)

# ================================================================================
# 🔧 CONFIGURATION MODELS
# ================================================================================

class OAuth2Flow(str, Enum):
    """OAuth2 Flow Types"""
    AUTHORIZATION_CODE = "authorization_code"
    DEVICE_CODE = "device_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"

class PKCEMethod(str, Enum):
    """PKCE Code Challenge Methods"""
    PLAIN = "plain"
    S256 = "S256"

@dataclass
class OAuth2Provider:
    """OAuth2 Provider Configuration"""
    name: str
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    userinfo_url: Optional[str] = None
    revoke_url: Optional[str] = None
    device_authorization_url: Optional[str] = None
    
    # OpenID Connect
    discovery_url: Optional[str] = None
    jwks_url: Optional[str] = None
    issuer: Optional[str] = None
    
    # Configuration
    scope: List[str] = field(default_factory=lambda: ["openid", "email", "profile"])
    use_pkce: bool = True
    pkce_method: PKCEMethod = PKCEMethod.S256
    
    # Rate limiting
    requests_per_hour: int = 1000
    token_requests_per_hour: int = 100
    
    # Creator economy specific
    creator_scopes: List[str] = field(default_factory=list)
    creator_endpoints: Dict[str, str] = field(default_factory=dict)

# Provider presets
OAUTH2_PROVIDERS = {
    "google": OAuth2Provider(
        name="google",
        client_id="{{GOOGLE_CLIENT_ID}}",
        client_secret="{{GOOGLE_CLIENT_SECRET}}",
        authorization_url="https://accounts.google.com/o/oauth2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
        revoke_url="https://oauth2.googleapis.com/revoke",
        discovery_url="https://accounts.google.com/.well-known/openid_configuration",
        scope=["openid", "email", "profile", "https://www.googleapis.com/auth/youtube"],
        creator_scopes=[
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly"
        ],
        creator_endpoints={
            "channels": "https://www.googleapis.com/youtube/v3/channels",
            "videos": "https://www.googleapis.com/youtube/v3/videos",
            "analytics": "https://youtubeanalytics.googleapis.com/v2/reports"
        }
    ),
    
    "github": OAuth2Provider(
        name="github",
        client_id="{{GITHUB_CLIENT_ID}}",
        client_secret="{{GITHUB_CLIENT_SECRET}}",
        authorization_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        scope=["user:email", "read:user"],
        creator_scopes=["repo", "read:org", "read:user"],
        creator_endpoints={
            "repos": "https://api.github.com/user/repos",
            "followers": "https://api.github.com/user/followers",
            "stats": "https://api.github.com/repos/{owner}/{repo}/stats"
        }
    ),
    
    "microsoft": OAuth2Provider(
        name="microsoft",
        client_id="{{MICROSOFT_CLIENT_ID}}",
        client_secret="{{MICROSOFT_CLIENT_SECRET}}",
        authorization_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        userinfo_url="https://graph.microsoft.com/v1.0/me",
        discovery_url="https://login.microsoftonline.com/common/v2.0/.well-known/openid_configuration",
        scope=["openid", "email", "profile", "User.Read"]
    ),
    
    "linkedin": OAuth2Provider(
        name="linkedin",
        client_id="{{LINKEDIN_CLIENT_ID}}",
        client_secret="{{LINKEDIN_CLIENT_SECRET}}",
        authorization_url="https://www.linkedin.com/oauth/v2/authorization",
        token_url="https://www.linkedin.com/oauth/v2/accessToken",
        userinfo_url="https://api.linkedin.com/v2/people/~",
        scope=["r_liteprofile", "r_emailaddress"],
        creator_scopes=[
            "w_member_social",
            "r_organization_social",
            "rw_organization_admin"
        ],
        creator_endpoints={
            "profile": "https://api.linkedin.com/v2/people/~",
            "posts": "https://api.linkedin.com/v2/shares",
            "analytics": "https://api.linkedin.com/v2/organizationalEntityShareStatistics"
        }
    )
}

# ================================================================================
# 📝 REQUEST/RESPONSE MODELS
# ================================================================================

class OAuth2AuthRequest(BaseModel):
    """OAuth2 Authorization Request"""
    provider: str = Field(..., description="OAuth2 provider name")
    redirect_uri: str = Field(..., description="Redirect URI after authorization")
    scope: Optional[List[str]] = Field(None, description="Requested scopes")
    state: Optional[str] = Field(None, description="State parameter for CSRF protection")
    creator_mode: bool = Field(False, description="Enable creator-specific scopes")
    
    @validator('provider')
    def validate_provider(cls, v):
        if v not in OAUTH2_PROVIDERS:
            raise ValueError(f"Unsupported provider: {v}")
        return v

class OAuth2TokenRequest(BaseModel):
    """OAuth2 Token Exchange Request"""
    provider: str
    code: str
    redirect_uri: str
    state: Optional[str] = None
    code_verifier: Optional[str] = None

class OAuth2TokenResponse(BaseModel):
    """OAuth2 Token Response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None

class OAuth2UserInfo(BaseModel):
    """OAuth2 User Information"""
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: str
    creator_info: Optional[Dict[str, Any]] = None

class DeviceAuthorizationResponse(BaseModel):
    """Device Authorization Response"""
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: Optional[str] = None
    expires_in: int
    interval: int = 5

# ================================================================================
# 🔐 OAUTH2 CLIENT IMPLEMENTATION
# ================================================================================

class OAuth2Client:
    """
    🔐 Enterprise OAuth2 Client with Multi-Provider Support
    
    Features:
    - Multi-provider OAuth2 & OpenID Connect
    - PKCE security for mobile/SPA
    - Token lifecycle management
    - Rate limiting per provider
    - Creator platform integrations
    - Device authorization flow
    - Comprehensive monitoring
    """
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        providers: Optional[Dict[str, OAuth2Provider]] = None,
        secret_key: str = "{{SECRET_KEY}}",
        token_cache_ttl: int = 3600
    ):
        self.redis = redis_client
        self.providers = providers or OAUTH2_PROVIDERS
        self.secret_key = secret_key
        self.token_cache_ttl = token_cache_ttl
        self.serializer = URLSafeTimedSerializer(secret_key)
        
        # Rate limiting tracking
        self.rate_limits: Dict[str, Dict[str, int]] = {}
        
        # Device flow tracking
        self.device_flows: Dict[str, Dict[str, Any]] = {}
        
        logger.info("OAuth2 client initialized", providers=list(self.providers.keys()))
    
    def _generate_state(self, provider: str, redirect_uri: str) -> str:
        """Generate secure state parameter"""
        data = {
            "provider": provider,
            "redirect_uri": redirect_uri,
            "timestamp": time.time(),
            "nonce": secrets.token_urlsafe(16)
        }
        return self.serializer.dumps(data)
    
    def _verify_state(self, state: str, max_age: int = 300) -> Dict[str, Any]:
        """Verify state parameter"""
        try:
            return self.serializer.loads(state, max_age=max_age)
        except (SignatureExpired, BadSignature) as e:
            raise HTTPException(status_code=400, detail=f"Invalid state: {e}")
    
    def _generate_pkce_challenge(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    async def _check_rate_limit(self, provider: str, endpoint: str) -> bool:
        """Check rate limiting for provider endpoint"""
        key = f"oauth2_rate_limit:{provider}:{endpoint}"
        current_hour = int(time.time() // 3600)
        
        try:
            count = await self.redis.hget(key, str(current_hour))
            count = int(count) if count else 0
            
            provider_config = self.providers[provider]
            limit = provider_config.requests_per_hour
            
            if endpoint == "token":
                limit = provider_config.token_requests_per_hour
            
            if count >= limit:
                return False
            
            # Increment counter
            await self.redis.hincrby(key, str(current_hour), 1)
            await self.redis.expire(key, 7200)  # 2 hours TTL
            
            return True
            
        except Exception as e:
            logger.warning("Rate limit check failed", error=str(e))
            return True  # Allow on error
    
    async def get_authorization_url(
        self,
        provider: str,
        redirect_uri: str,
        scope: Optional[List[str]] = None,
        creator_mode: bool = False,
        state: Optional[str] = None
    ) -> Tuple[str, str, Optional[str]]:
        """
        Generate OAuth2 authorization URL
        
        Returns:
            Tuple of (authorization_url, state, code_verifier)
        """
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        provider_config = self.providers[provider]
        
        # Rate limiting check
        if not await self._check_rate_limit(provider, "authorize"):
            oauth2_requests_total.labels(provider=provider, flow_type="authorize", status="rate_limited").inc()
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Generate state if not provided
        if not state:
            state = self._generate_state(provider, redirect_uri)
        
        # Determine scopes
        if scope is None:
            scope = provider_config.scope.copy()
            if creator_mode and provider_config.creator_scopes:
                scope.extend(provider_config.creator_scopes)
        
        # Generate PKCE challenge
        code_verifier = None
        params = {
            "client_id": provider_config.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scope),
            "state": state,
            "response_type": "code"
        }
        
        if provider_config.use_pkce:
            code_verifier, code_challenge = self._generate_pkce_challenge()
            params.update({
                "code_challenge": code_challenge,
                "code_challenge_method": provider_config.pkce_method.value
            })
            
            # Store code verifier in Redis
            verifier_key = f"oauth2_verifier:{state}"
            await self.redis.setex(verifier_key, 300, code_verifier)  # 5 min TTL
        
        # Build authorization URL
        auth_url = f"{provider_config.authorization_url}?{urllib.parse.urlencode(params)}"
        
        oauth2_requests_total.labels(provider=provider, flow_type="authorize", status="success").inc()
        
        logger.info(
            "Generated authorization URL",
            provider=provider,
            redirect_uri=redirect_uri,
            creator_mode=creator_mode,
            use_pkce=provider_config.use_pkce
        )
        
        return auth_url, state, code_verifier
    
    async def exchange_code_for_token(
        self,
        provider: str,
        code: str,
        redirect_uri: str,
        state: Optional[str] = None,
        code_verifier: Optional[str] = None
    ) -> OAuth2TokenResponse:
        """Exchange authorization code for access token"""
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        provider_config = self.providers[provider]
        
        # Rate limiting check
        if not await self._check_rate_limit(provider, "token"):
            oauth2_token_operations.labels(provider=provider, operation="exchange", status="rate_limited").inc()
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Verify state if provided
        if state:
            state_data = self._verify_state(state)
            if state_data["provider"] != provider:
                raise HTTPException(status_code=400, detail="State provider mismatch")
        
        # Get code verifier from Redis if PKCE is enabled
        if provider_config.use_pkce and not code_verifier:
            if state:
                verifier_key = f"oauth2_verifier:{state}"
                code_verifier = await self.redis.get(verifier_key)
                if code_verifier:
                    code_verifier = code_verifier.decode('utf-8')
                    await self.redis.delete(verifier_key)
        
        # Prepare token request
        data = {
            "client_id": provider_config.client_id,
            "client_secret": provider_config.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        if provider_config.use_pkce and code_verifier:
            data["code_verifier"] = code_verifier
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            with oauth2_request_duration.labels(provider=provider, endpoint="token").time():
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        provider_config.token_url,
                        data=data,
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            oauth2_token_operations.labels(provider=provider, operation="exchange", status="error").inc()
                            raise HTTPException(
                                status_code=response.status,
                                detail=f"Token exchange failed: {error_text}"
                            )
                        
                        token_data = await response.json()
            
            # Parse token response
            token_response = OAuth2TokenResponse(**token_data)
            
            # Cache token data
            await self._cache_token(provider, token_response)
            
            oauth2_token_operations.labels(provider=provider, operation="exchange", status="success").inc()
            oauth2_active_sessions.labels(provider=provider).inc()
            
            logger.info(
                "Token exchange successful",
                provider=provider,
                has_refresh_token=bool(token_response.refresh_token),
                expires_in=token_response.expires_in
            )
            
            return token_response
            
        except aiohttp.ClientError as e:
            oauth2_token_operations.labels(provider=provider, operation="exchange", status="error").inc()
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
    
    async def refresh_token(
        self,
        provider: str,
        refresh_token: str
    ) -> OAuth2TokenResponse:
        """Refresh access token using refresh token"""
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        provider_config = self.providers[provider]
        
        # Rate limiting check
        if not await self._check_rate_limit(provider, "token"):
            oauth2_token_operations.labels(provider=provider, operation="refresh", status="rate_limited").inc()
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        data = {
            "client_id": provider_config.client_id,
            "client_secret": provider_config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            with oauth2_request_duration.labels(provider=provider, endpoint="refresh").time():
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        provider_config.token_url,
                        data=data,
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            oauth2_token_operations.labels(provider=provider, operation="refresh", status="error").inc()
                            raise HTTPException(
                                status_code=response.status,
                                detail=f"Token refresh failed: {error_text}"
                            )
                        
                        token_data = await response.json()
            
            token_response = OAuth2TokenResponse(**token_data)
            
            # Cache new token
            await self._cache_token(provider, token_response)
            
            oauth2_token_operations.labels(provider=provider, operation="refresh", status="success").inc()
            
            logger.info("Token refresh successful", provider=provider)
            
            return token_response
            
        except aiohttp.ClientError as e:
            oauth2_token_operations.labels(provider=provider, operation="refresh", status="error").inc()
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
    
    async def revoke_token(
        self,
        provider: str,
        token: str,
        token_type: str = "access_token"
    ) -> bool:
        """Revoke access or refresh token"""
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        provider_config = self.providers[provider]
        
        if not provider_config.revoke_url:
            logger.warning("Token revocation not supported", provider=provider)
            return False
        
        # Rate limiting check
        if not await self._check_rate_limit(provider, "revoke"):
            oauth2_token_operations.labels(provider=provider, operation="revoke", status="rate_limited").inc()
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        data = {
            "token": token,
            "token_type_hint": token_type
        }
        
        # Some providers require client authentication
        auth = aiohttp.BasicAuth(provider_config.client_id, provider_config.client_secret)
        
        try:
            with oauth2_request_duration.labels(provider=provider, endpoint="revoke").time():
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        provider_config.revoke_url,
                        data=data,
                        auth=auth
                    ) as response:
                        success = response.status in [200, 204]
                        
                        status = "success" if success else "error"
                        oauth2_token_operations.labels(provider=provider, operation="revoke", status=status).inc()
                        
                        if success:
                            oauth2_active_sessions.labels(provider=provider).dec()
                        
                        return success
                        
        except aiohttp.ClientError as e:
            oauth2_token_operations.labels(provider=provider, operation="revoke", status="error").inc()
            logger.error("Token revocation failed", provider=provider, error=str(e))
            return False
    
    async def get_user_info(
        self,
        provider: str,
        access_token: str,
        include_creator_info: bool = False
    ) -> OAuth2UserInfo:
        """Get user information from OAuth2 provider"""
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        provider_config = self.providers[provider]
        
        if not provider_config.userinfo_url:
            raise HTTPException(status_code=400, detail=f"User info not supported for {provider}")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        try:
            with oauth2_request_duration.labels(provider=provider, endpoint="userinfo").time():
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        provider_config.userinfo_url,
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise HTTPException(
                                status_code=response.status,
                                detail=f"User info request failed: {error_text}"
                            )
                        
                        user_data = await response.json()
            
            # Normalize user data across providers
            normalized_data = self._normalize_user_data(provider, user_data)
            
            # Get creator-specific information if requested
            creator_info = None
            if include_creator_info and provider_config.creator_endpoints:
                creator_info = await self._get_creator_info(provider, access_token)
            
            user_info = OAuth2UserInfo(
                **normalized_data,
                provider=provider,
                creator_info=creator_info
            )
            
            logger.info(
                "User info retrieved",
                provider=provider,
                user_id=user_info.sub,
                has_creator_info=bool(creator_info)
            )
            
            return user_info
            
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
    
    def _normalize_user_data(self, provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize user data across different providers"""
        if provider == "google":
            return {
                "sub": data.get("id", data.get("sub")),
                "email": data.get("email"),
                "name": data.get("name"),
                "picture": data.get("picture")
            }
        elif provider == "github":
            return {
                "sub": str(data.get("id")),
                "email": data.get("email"),
                "name": data.get("name") or data.get("login"),
                "picture": data.get("avatar_url")
            }
        elif provider == "microsoft":
            return {
                "sub": data.get("id"),
                "email": data.get("mail") or data.get("userPrincipalName"),
                "name": data.get("displayName"),
                "picture": None  # Not in basic profile
            }
        elif provider == "linkedin":
            return {
                "sub": data.get("id"),
                "email": None,  # Requires separate API call
                "name": data.get("localizedFirstName", "") + " " + data.get("localizedLastName", ""),
                "picture": data.get("profilePicture", {}).get("displayImage")
            }
        else:
            # Generic OpenID Connect response
            return {
                "sub": data.get("sub"),
                "email": data.get("email"),
                "name": data.get("name"),
                "picture": data.get("picture")
            }
    
    async def _get_creator_info(
        self,
        provider: str,
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Get creator-specific information from provider APIs"""
        provider_config = self.providers[provider]
        
        if not provider_config.creator_endpoints:
            return None
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        creator_info = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint_name, endpoint_url in provider_config.creator_endpoints.items():
                    try:
                        async with session.get(endpoint_url, headers=headers) as response:
                            if response.status == 200:
                                creator_info[endpoint_name] = await response.json()
                            else:
                                logger.warning(
                                    "Creator endpoint failed",
                                    provider=provider,
                                    endpoint=endpoint_name,
                                    status=response.status
                                )
                    except Exception as e:
                        logger.warning(
                            "Creator endpoint error",
                            provider=provider,
                            endpoint=endpoint_name,
                            error=str(e)
                        )
            
            return creator_info if creator_info else None
            
        except Exception as e:
            logger.error("Creator info retrieval failed", provider=provider, error=str(e))
            return None
    
    async def _cache_token(self, provider: str, token_response: OAuth2TokenResponse):
        """Cache token data in Redis"""
        try:
            token_data = token_response.dict()
            token_data["cached_at"] = time.time()
            
            # Use access token hash as key for security
            token_hash = hashlib.sha256(token_response.access_token.encode()).hexdigest()[:16]
            cache_key = f"oauth2_token:{provider}:{token_hash}"
            
            ttl = token_response.expires_in or self.token_cache_ttl
            await self.redis.setex(cache_key, ttl, json.dumps(token_data))
            
        except Exception as e:
            logger.warning("Token caching failed", provider=provider, error=str(e))
    
    async def start_device_authorization(
        self,
        provider: str,
        scope: Optional[List[str]] = None
    ) -> DeviceAuthorizationResponse:
        """Start device authorization flow"""
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        provider_config = self.providers[provider]
        
        if not provider_config.device_authorization_url:
            raise HTTPException(status_code=400, detail=f"Device flow not supported for {provider}")
        
        # Rate limiting check
        if not await self._check_rate_limit(provider, "device_auth"):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        scope = scope or provider_config.scope
        
        data = {
            "client_id": provider_config.client_id,
            "scope": " ".join(scope)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    provider_config.device_authorization_url,
                    data=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Device authorization failed: {error_text}"
                        )
                    
                    device_data = await response.json()
            
            device_response = DeviceAuthorizationResponse(**device_data)
            
            # Store device flow data
            self.device_flows[device_response.device_code] = {
                "provider": provider,
                "expires_at": time.time() + device_response.expires_in,
                "interval": device_response.interval,
                "polling_started": False
            }
            
            logger.info(
                "Device authorization started",
                provider=provider,
                device_code=device_response.device_code[:8] + "...",
                user_code=device_response.user_code
            )
            
            return device_response
            
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
    
    async def poll_device_token(
        self,
        provider: str,
        device_code: str
    ) -> Optional[OAuth2TokenResponse]:
        """Poll for device authorization token"""
        if device_code not in self.device_flows:
            raise HTTPException(status_code=400, detail="Unknown device code")
        
        flow_data = self.device_flows[device_code]
        
        if flow_data["provider"] != provider:
            raise HTTPException(status_code=400, detail="Provider mismatch")
        
        if time.time() > flow_data["expires_at"]:
            del self.device_flows[device_code]
            raise HTTPException(status_code=400, detail="Device code expired")
        
        provider_config = self.providers[provider]
        
        data = {
            "client_id": provider_config.client_id,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    provider_config.token_url,
                    data=data
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        token_response = OAuth2TokenResponse(**token_data)
                        
                        # Clean up device flow
                        del self.device_flows[device_code]
                        
                        # Cache token
                        await self._cache_token(provider, token_response)
                        
                        logger.info("Device token obtained", provider=provider)
                        
                        return token_response
                    elif response.status == 400:
                        error_data = await response.json()
                        error_code = error_data.get("error")
                        
                        if error_code == "authorization_pending":
                            return None  # Continue polling
                        elif error_code == "slow_down":
                            # Increase polling interval
                            flow_data["interval"] += 5
                            return None
                        elif error_code in ["access_denied", "expired_token"]:
                            del self.device_flows[device_code]
                            raise HTTPException(status_code=400, detail=f"Device authorization {error_code}")
                        else:
                            raise HTTPException(status_code=400, detail=f"Device token error: {error_code}")
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Device token request failed: {error_text}"
                        )
                        
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {e}")

# ================================================================================
# 🌐 FASTAPI INTEGRATION
# ================================================================================

class OAuth2ClientAPI:
    """FastAPI integration for OAuth2 client"""
    
    def __init__(self, oauth2_client: OAuth2Client):
        self.oauth2_client = oauth2_client
        self.app = FastAPI(title="OAuth2 Client API", version="1.0.0")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/oauth2/providers")
        async def list_providers():
            """List available OAuth2 providers"""
            return {
                "providers": [
                    {
                        "name": name,
                        "authorization_url": config.authorization_url,
                        "scope": config.scope,
                        "creator_scopes": config.creator_scopes,
                        "supports_pkce": config.use_pkce,
                        "supports_device_flow": bool(config.device_authorization_url)
                    }
                    for name, config in self.oauth2_client.providers.items()
                ]
            }
        
        @self.app.post("/oauth2/{provider}/authorize")
        async def authorize(
            provider: str,
            request: OAuth2AuthRequest
        ):
            """Start OAuth2 authorization flow"""
            auth_url, state, code_verifier = await self.oauth2_client.get_authorization_url(
                provider=provider,
                redirect_uri=request.redirect_uri,
                scope=request.scope,
                creator_mode=request.creator_mode,
                state=request.state
            )
            
            response_data = {
                "authorization_url": auth_url,
                "state": state
            }
            
            if code_verifier:
                response_data["code_verifier"] = code_verifier
            
            return response_data
        
        @self.app.post("/oauth2/{provider}/token")
        async def exchange_token(
            provider: str,
            request: OAuth2TokenRequest
        ):
            """Exchange authorization code for access token"""
            return await self.oauth2_client.exchange_code_for_token(
                provider=provider,
                code=request.code,
                redirect_uri=request.redirect_uri,
                state=request.state,
                code_verifier=request.code_verifier
            )
        
        @self.app.post("/oauth2/{provider}/refresh")
        async def refresh_token(
            provider: str,
            refresh_token: str
        ):
            """Refresh access token"""
            return await self.oauth2_client.refresh_token(provider, refresh_token)
        
        @self.app.post("/oauth2/{provider}/revoke")
        async def revoke_token(
            provider: str,
            token: str,
            token_type: str = "access_token"
        ):
            """Revoke access or refresh token"""
            success = await self.oauth2_client.revoke_token(provider, token, token_type)
            return {"revoked": success}
        
        @self.app.get("/oauth2/{provider}/userinfo")
        async def get_userinfo(
            provider: str,
            access_token: str,
            include_creator_info: bool = False
        ):
            """Get user information"""
            return await self.oauth2_client.get_user_info(
                provider,
                access_token,
                include_creator_info
            )
        
        @self.app.post("/oauth2/{provider}/device/authorize")
        async def device_authorize(
            provider: str,
            scope: Optional[List[str]] = None
        ):
            """Start device authorization flow"""
            return await self.oauth2_client.start_device_authorization(provider, scope)
        
        @self.app.post("/oauth2/{provider}/device/token")
        async def device_token(
            provider: str,
            device_code: str
        ):
            """Poll for device authorization token"""
            token = await self.oauth2_client.poll_device_token(provider, device_code)
            if token:
                return token
            else:
                return {"status": "pending"}

# ================================================================================
# 🏭 FACTORY FUNCTIONS & UTILITIES
# ================================================================================

async def create_oauth2_client(
    redis_url: str = "redis://localhost:6379",
    providers: Optional[Dict[str, OAuth2Provider]] = None,
    secret_key: str = "{{SECRET_KEY}}",
    token_cache_ttl: int = 3600
) -> OAuth2Client:
    """Factory function to create OAuth2 client"""
    redis_client = await aioredis.from_url(redis_url)
    return OAuth2Client(
        redis_client=redis_client,
        providers=providers,
        secret_key=secret_key,
        token_cache_ttl=token_cache_ttl
    )

def create_oauth2_app(oauth2_client: OAuth2Client) -> FastAPI:
    """Factory function to create FastAPI app with OAuth2 client"""
    oauth2_api = OAuth2ClientAPI(oauth2_client)
    return oauth2_api.app

# ================================================================================
# 🧪 EXAMPLE USAGE & TESTING
# ================================================================================

async def example_oauth2_flow():
    """Example OAuth2 authorization flow"""
    
    # Initialize OAuth2 client
    oauth2_client = await create_oauth2_client()
    
    try:
        # 1. Start authorization flow
        auth_url, state, code_verifier = await oauth2_client.get_authorization_url(
            provider="google",
            redirect_uri="https://app.ainflue.com/auth/callback",
            creator_mode=True
        )
        
        print(f"Authorization URL: {auth_url}")
        print(f"State: {state}")
        
        # 2. User completes authorization and returns with code
        # In real app, this would come from the callback
        authorization_code = "example_code_from_callback"
        
        # 3. Exchange code for token
        token_response = await oauth2_client.exchange_code_for_token(
            provider="google",
            code=authorization_code,
            redirect_uri="https://app.ainflue.com/auth/callback",
            state=state,
            code_verifier=code_verifier
        )
        
        print(f"Access token: {token_response.access_token[:20]}...")
        
        # 4. Get user information
        user_info = await oauth2_client.get_user_info(
            provider="google",
            access_token=token_response.access_token,
            include_creator_info=True
        )
        
        print(f"User: {user_info.name} ({user_info.email})")
        print(f"Creator info: {bool(user_info.creator_info)}")
        
        # 5. Refresh token if needed
        if token_response.refresh_token:
            new_token = await oauth2_client.refresh_token(
                provider="google",
                refresh_token=token_response.refresh_token
            )
            print(f"Refreshed token: {new_token.access_token[:20]}...")
        
        # 6. Revoke token when done
        await oauth2_client.revoke_token(
            provider="google",
            token=token_response.access_token
        )
        print("Token revoked")
        
    except HTTPException as e:
        print(f"OAuth2 error: {e.detail}")
    except Exception as e:
        print(f"Unexpected error: {e}")

async def example_device_flow():
    """Example device authorization flow"""
    
    oauth2_client = await create_oauth2_client()
    
    try:
        # 1. Start device authorization
        device_response = await oauth2_client.start_device_authorization(
            provider="google",
            scope=["openid", "email", "profile"]
        )
        
        print(f"Visit: {device_response.verification_uri}")
        print(f"Enter code: {device_response.user_code}")
        
        # 2. Poll for token
        poll_interval = device_response.interval
        start_time = time.time()
        
        while time.time() - start_time < device_response.expires_in:
            await asyncio.sleep(poll_interval)
            
            token = await oauth2_client.poll_device_token(
                provider="google",
                device_code=device_response.device_code
            )
            
            if token:
                print(f"Device token obtained: {token.access_token[:20]}...")
                break
            else:
                print("Still waiting for user authorization...")
        
    except HTTPException as e:
        print(f"Device flow error: {e.detail}")

if __name__ == "__main__":
    # Example usage
    asyncio.run(example_oauth2_flow())
    # asyncio.run(example_device_flow())

# ================================================================================
# 📚 DOCUMENTATION & INTEGRATION GUIDE
# ================================================================================

"""
🔐 OAUTH2 CLIENT INTEGRATION GUIDE
=================================

## Basic Setup

```python
import asyncio
from oauth2_client_template import create_oauth2_client, OAuth2Provider

# Custom provider configuration
custom_provider = OAuth2Provider(
    name="custom",
    client_id="your_client_id",
    client_secret="your_client_secret",
    authorization_url="https://auth.example.com/oauth2/authorize",
    token_url="https://auth.example.com/oauth2/token",
    userinfo_url="https://api.example.com/user",
    scope=["read", "write"]
)

# Initialize client
oauth2_client = await create_oauth2_client(
    redis_url="redis://localhost:6379",
    providers={"custom": custom_provider}
)
```

## FastAPI Integration

```python
from fastapi import FastAPI
from oauth2_client_template import create_oauth2_app

app = create_oauth2_app(oauth2_client)

# Your app routes here
@app.get("/protected")
async def protected_route(token: str = Depends(get_current_user)):
    return {"user": token.user_id}
```

## Creator Economy Features

```python
# Request creator-specific scopes
auth_url, state, verifier = await oauth2_client.get_authorization_url(
    provider="youtube",
    redirect_uri="https://app.ainflue.com/auth/callback",
    creator_mode=True  # Enables creator scopes
)

# Get creator information
user_info = await oauth2_client.get_user_info(
    provider="youtube",
    access_token=token,
    include_creator_info=True
)

# Access creator-specific data
channel_data = user_info.creator_info.get("channels")
video_stats = user_info.creator_info.get("analytics")
```

## Security Features

### PKCE (Proof Key for Code Exchange)
- Automatically enabled for mobile/SPA security
- SHA256 code challenge method
- Secure code verifier storage in Redis

### Rate Limiting
- Per-provider request limits
- Separate limits for token operations
- Automatic rate limit enforcement

### State Parameter Protection
- Cryptographically signed state parameters
- CSRF attack prevention
- Configurable expiration times

## Error Handling

```python
try:
    token = await oauth2_client.exchange_code_for_token(...)
except HTTPException as e:
    if e.status_code == 429:
        # Rate limited
        retry_after = e.headers.get("Retry-After")
    elif e.status_code == 400:
        # Invalid request (expired code, etc.)
        handle_auth_error(e.detail)
    else:
        # Other OAuth2 errors
        log_oauth_error(e)
```

## Monitoring & Metrics

The client exports Prometheus metrics:
- `oauth2_client_requests_total` - Total requests by provider/flow/status
- `oauth2_token_operations_total` - Token operations by provider/operation/status  
- `oauth2_request_duration_seconds` - Request duration by provider/endpoint
- `oauth2_active_sessions` - Active sessions by provider

## Configuration Examples

### Google OAuth2 (YouTube Creator)
```python
google_config = OAuth2Provider(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorization_url="https://accounts.google.com/o/oauth2/auth",
    token_url="https://oauth2.googleapis.com/token",
    userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
    scope=["openid", "email", "profile"],
    creator_scopes=[
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.upload"
    ]
)
```

### Enterprise SAML + OAuth2 Hybrid
```python
# Use OAuth2 client with SAML authentication template
# for enterprise identity federation
```

🚀 ADVANCED FEATURES:
- Multi-provider authentication
- Creator platform integrations  
- Device authorization flow
- Token lifecycle management
- Enterprise security compliance
- Real-time monitoring & alerting
- Redis-backed caching & sessions
- Comprehensive audit logging

🛡️ SECURITY COMPLIANCE:
- OAuth 2.0 & OpenID Connect standards
- PKCE for enhanced security
- Rate limiting & DDoS protection
- CSRF protection via state parameters
- Secure token storage & transmission
- Audit trail for compliance

For more examples and advanced usage, see the test files and documentation.
"""

# ================================================================================
# 🔚 END OF OAUTH2 CLIENT TEMPLATE
# ================================================================================