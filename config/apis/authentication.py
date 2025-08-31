"""API Authentication Manager - OAuth2, API Key & JWT Authentication System
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive authentication management for external APIs
including OAuth2 flows, API key management, JWT tokens, and refresh mechanisms.
"""
import asyncio
import aiohttp
import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlencode, parse_qs, urlparse
import jwt as jwt_lib

logger = logging.getLogger(__name__)

class AuthenticationType(Enum):
    """Authentication types"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    SIGNATURE = "signature"
    CUSTOM = "custom"

class OAuth2GrantType(Enum):
    """OAuth2 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    IMPLICIT = "implicit"
    DEVICE_CODE = "device_code"

@dataclass
class AuthToken:
    """Authentication token data"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def expires_at(self) -> Optional[datetime]:
        """Calculate expiration time"""
        if self.expires_in:
            return self.created_at + timedelta(seconds=self.expires_in)
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if self.expires_at:
            return datetime.utcnow() >= self.expires_at - timedelta(minutes=5)  # 5 min buffer
        return False
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid"""
        return bool(self.access_token) and not self.is_expired

@dataclass
class AuthConfig:
    """Authentication configuration"""
    auth_type: AuthenticationType
    api_name: str
    
    # OAuth2 Configuration
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    redirect_uri: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    
    # API Key Configuration
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    
    # JWT Configuration
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # Basic Auth
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Signature Authentication
    signature_method: str = "HMAC-SHA256"
    signature_header: str = "X-Signature"
    
    # Token storage
    token_cache_key_prefix: str = "auth_token"
    auto_refresh: bool = True
    
    def get_cache_key(self, user_id: Optional[str] = None) -> str:
        """Generate cache key for token storage"""
        key_parts = [self.token_cache_key_prefix, self.api_name]
        if user_id:
            key_parts.append(user_id)
        return ":".join(key_parts)

class OAuth2Manager:
    """OAuth2 authentication manager"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.state_storage: Dict[str, Dict[str, Any]] = {}
    
    def generate_auth_url(self, user_id: str, state_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate OAuth2 authorization URL
        
        Args:
            user_id: User identifier
            state_data: Additional state data to include
            
        Returns:
            Authorization URL
        """
        state = self._generate_state(user_id, state_data)
        
        params = {
            'response_type': 'code',
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'scope': ' '.join(self.config.scopes),
            'state': state,
            'access_type': 'offline',  # For refresh tokens
            'prompt': 'consent'
        }
        
        return f"{self.config.auth_url}?{urlencode(params)}"
    
    def _generate_state(self, user_id: str, state_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate secure state parameter"""
        state_id = secrets.token_urlsafe(32)
        
        self.state_storage[state_id] = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'data': state_data or {}
        }
        
        return state_id
    
    def verify_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Verify and retrieve state data"""
        if state not in self.state_storage:
            return None
        
        state_data = self.state_storage[state]
        
        # Check if state is too old (15 minutes max)
        if datetime.utcnow() - state_data['created_at'] > timedelta(minutes=15):
            del self.state_storage[state]
            return None
        
        # Clean up used state
        del self.state_storage[state]
        return state_data
    
    async def exchange_code_for_token(self, code: str, state: str) -> Optional[AuthToken]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code
            state: State parameter
            
        Returns:
            AuthToken or None if failed
        """
        try:
            # Verify state
            state_data = self.verify_state(state)
            if not state_data:
                logger.error("Invalid or expired state parameter")
                return None
            
            # Prepare token request
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.config.redirect_uri,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.token_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        return AuthToken(
                            access_token=token_data['access_token'],
                            token_type=token_data.get('token_type', 'Bearer'),
                            expires_in=token_data.get('expires_in'),
                            refresh_token=token_data.get('refresh_token'),
                            scope=token_data.get('scope')
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Token exchange failed: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            return None
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[AuthToken]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New AuthToken or None if failed
        """
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.token_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        return AuthToken(
                            access_token=token_data['access_token'],
                            token_type=token_data.get('token_type', 'Bearer'),
                            expires_in=token_data.get('expires_in'),
                            refresh_token=token_data.get('refresh_token', refresh_token),
                            scope=token_data.get('scope')
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Token refresh failed: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    async def get_client_credentials_token(self) -> Optional[AuthToken]:
        """
        Get access token using client credentials flow
        
        Returns:
            AuthToken or None if failed
        """
        try:
            data = {
                'grant_type': 'client_credentials',
                'scope': ' '.join(self.config.scopes)
            }
            
            # Basic auth with client credentials
            auth_string = f"{self.config.client_id}:{self.config.client_secret}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth_bytes}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.token_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        return AuthToken(
                            access_token=token_data['access_token'],
                            token_type=token_data.get('token_type', 'Bearer'),
                            expires_in=token_data.get('expires_in'),
                            scope=token_data.get('scope')
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Client credentials failed: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Client credentials error: {e}")
            return None

class APIKeyManager:
    """API Key authentication manager"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get headers with API key authentication"""
        return {
            self.config.api_key_header: self.config.api_key
        }
    
    def validate_api_key(self) -> bool:
        """Validate API key is present"""
        return bool(self.config.api_key)

class JWTManager:
    """JWT token manager"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
    
    def generate_jwt(self, payload: Dict[str, Any]) -> str:
        """Generate JWT token"""
        payload.update({
            'iat': int(time.time()),
            'exp': int(time.time()) + (self.config.jwt_expiry_hours * 3600),
            'iss': self.config.api_name
        })
        
        return jwt_lib.encode(payload, self.config.jwt_secret, algorithm=self.config.jwt_algorithm)
    
    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt_lib.decode(
                token, 
                self.config.jwt_secret, 
                algorithms=[self.config.jwt_algorithm]
            )
            return payload
        except jwt_lib.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt_lib.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            return None

class SignatureManager:
    """API signature authentication manager"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
    
    def generate_signature(self, method: str, url: str, body: str = "", timestamp: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate API signature
        
        Args:
            method: HTTP method
            url: Request URL
            body: Request body
            timestamp: Unix timestamp (generated if not provided)
            
        Returns:
            Tuple of (signature, timestamp)
        """
        if not timestamp:
            timestamp = str(int(time.time()))
        
        # Create string to sign
        string_to_sign = f"{method}\n{url}\n{body}\n{timestamp}"
        
        # Generate signature
        signature = hmac.new(
            self.config.client_secret.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    def get_auth_headers(self, method: str, url: str, body: str = "") -> Dict[str, str]:
        """Get headers with signature authentication"""
        signature, timestamp = self.generate_signature(method, url, body)
        
        return {
            self.config.signature_header: signature,
            'X-Timestamp': timestamp,
            'X-Client-ID': self.config.client_id or ""
        }

class APIAuthenticationManager:
    """Main API authentication manager"""
    
    def __init__(self):
        self.token_cache: Dict[str, AuthToken] = {}
        self.oauth2_managers: Dict[str, OAuth2Manager] = {}
        self.api_key_managers: Dict[str, APIKeyManager] = {}
        self.jwt_managers: Dict[str, JWTManager] = {}
        self.signature_managers: Dict[str, SignatureManager] = {}
    
    def register_auth_config(self, api_name: str, config: AuthConfig):
        """Register authentication configuration for an API"""
        if config.auth_type == AuthenticationType.OAUTH2:
            self.oauth2_managers[api_name] = OAuth2Manager(config)
        elif config.auth_type == AuthenticationType.API_KEY:
            self.api_key_managers[api_name] = APIKeyManager(config)
        elif config.auth_type == AuthenticationType.JWT:
            self.jwt_managers[api_name] = JWTManager(config)
        elif config.auth_type == AuthenticationType.SIGNATURE:
            self.signature_managers[api_name] = SignatureManager(config)
        
        logger.info(f"Registered {config.auth_type.value} authentication for {api_name}")
    
    async def get_authenticated_client(self, platform: str, config: Dict[str, Any], 
                                    user_id: Optional[str] = None) -> Optional[aiohttp.ClientSession]:
        """
        Get authenticated HTTP client for platform
        
        Args:
            platform: Platform name
            config: Platform configuration
            user_id: Optional user ID for user-specific auth
            
        Returns:
            Authenticated ClientSession or None
        """
        try:
            headers = {}
            
            # Determine authentication type and get headers
            auth_type = config.get('authentication_type', 'api_key')
            
            if auth_type == 'oauth2':
                token = await self._get_oauth2_token(platform, user_id)
                if token and token.is_valid:
                    headers['Authorization'] = f"{token.token_type} {token.access_token}"
                else:
                    logger.error(f"No valid OAuth2 token for {platform}")
                    return None
            
            elif auth_type == 'api_key':
                api_key = config.get('api_key')
                if api_key:
                    headers['X-API-Key'] = api_key
                else:
                    logger.error(f"No API key configured for {platform}")
                    return None
            
            elif auth_type == 'bearer_token':
                token = config.get('access_token') or config.get('api_key')
                if token:
                    headers['Authorization'] = f"Bearer {token}"
                else:
                    logger.error(f"No bearer token configured for {platform}")
                    return None
            
            # Create session with authentication headers
            session = aiohttp.ClientSession(headers=headers)
            return session
            
        except Exception as e:
            logger.error(f"Failed to create authenticated client for {platform}: {e}")
            return None
    
    async def _get_oauth2_token(self, api_name: str, user_id: Optional[str] = None) -> Optional[AuthToken]:
        """Get OAuth2 token for API and user"""
        cache_key = f"{api_name}:{user_id or 'default'}"
        
        # Check cache first
        if cache_key in self.token_cache:
            token = self.token_cache[cache_key]
            if token.is_valid:
                return token
            elif token.refresh_token and api_name in self.oauth2_managers:
                # Try to refresh token
                manager = self.oauth2_managers[api_name]
                new_token = await manager.refresh_access_token(token.refresh_token)
                if new_token:
                    self.token_cache[cache_key] = new_token
                    return new_token
        
        # Try client credentials flow if no user-specific token
        if not user_id and api_name in self.oauth2_managers:
            manager = self.oauth2_managers[api_name]
            token = await manager.get_client_credentials_token()
            if token:
                self.token_cache[cache_key] = token
                return token
        
        return None
    
    def store_user_token(self, api_name: str, user_id: str, token: AuthToken):
        """Store user-specific OAuth2 token"""
        cache_key = f"{api_name}:{user_id}"
        self.token_cache[cache_key] = token
        logger.info(f"Stored token for {api_name} user {user_id}")
    
    def get_auth_headers(self, api_name: str, method: str = "GET", 
                        url: str = "", body: str = "") -> Dict[str, str]:
        """Get authentication headers for API request"""
        headers = {}
        
        if api_name in self.api_key_managers:
            headers.update(self.api_key_managers[api_name].get_auth_headers())
        elif api_name in self.signature_managers:
            headers.update(self.signature_managers[api_name].get_auth_headers(method, url, body))
        
        return headers
    
    def generate_oauth2_auth_url(self, api_name: str, user_id: str, 
                                state_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate OAuth2 authorization URL"""
        if api_name in self.oauth2_managers:
            return self.oauth2_managers[api_name].generate_auth_url(user_id, state_data)
        return None
    
    async def handle_oauth2_callback(self, api_name: str, code: str, state: str) -> Optional[AuthToken]:
        """Handle OAuth2 callback and exchange code for token"""
        if api_name in self.oauth2_managers:
            manager = self.oauth2_managers[api_name]
            token = await manager.exchange_code_for_token(code, state)
            
            if token:
                # Verify state to get user_id
                state_data = manager.verify_state(state)
                if state_data:
                    user_id = state_data['user_id']
                    self.store_user_token(api_name, user_id, token)
            
            return token
        return None
    
    def revoke_user_token(self, api_name: str, user_id: str):
        """Revoke user-specific token"""
        cache_key = f"{api_name}:{user_id}"
        if cache_key in self.token_cache:
            del self.token_cache[cache_key]
            logger.info(f"Revoked token for {api_name} user {user_id}")
    
    def get_token_status(self, api_name: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get token status for API and user"""
        cache_key = f"{api_name}:{user_id or 'default'}"
        
        if cache_key in self.token_cache:
            token = self.token_cache[cache_key]
            return {
                'exists': True,
                'valid': token.is_valid,
                'expires_at': token.expires_at,
                'has_refresh_token': bool(token.refresh_token),
                'scopes': token.scope
            }
        
        return {
            'exists': False,
            'valid': False,
            'expires_at': None,
            'has_refresh_token': False,
            'scopes': None
        }
