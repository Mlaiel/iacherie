"""Universal OAuth 2.0 Management System
========================================

Centralized OAuth 2.0 authentication and token management for all platform integrations.
Supports multiple providers, token refresh, and secure credential storage.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import base64
import hashlib
import secrets
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import aiohttp
import jwt
from cryptography.fernet import Fernet
from enum import Enum


class OAuthFlow(Enum):
    """OAuth flow types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"
    REFRESH_TOKEN = "refresh_token"


class TokenStatus(Enum):
    """Token status enumeration"""
    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"


@dataclass
class OAuthProvider:
    """OAuth provider configuration"""
    name: str
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    refresh_url: Optional[str] = None
    revoke_url: Optional[str] = None
    scope: Optional[str] = None
    redirect_uri: Optional[str] = None
    flow_type: OAuthFlow = OAuthFlow.AUTHORIZATION_CODE
    token_endpoint_auth_method: str = "client_secret_post"
    extra_params: Optional[Dict[str, str]] = None


@dataclass 
class AccessToken:
    """Access token data structure"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    provider: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def expires_at(self) -> Optional[datetime]:
        """Calculate token expiration time"""
        if self.expires_in and self.created_at:
            return self.created_at + timedelta(seconds=self.expires_in)
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if self.expires_at:
            return datetime.utcnow() >= self.expires_at
        return False
    
    @property
    def expires_soon(self, buffer_seconds: int = 300) -> bool:
        """Check if token expires soon"""
        if self.expires_at:
            return datetime.utcnow() >= (self.expires_at - timedelta(seconds=buffer_seconds))
        return False


class OAuthManager:
    """Universal OAuth 2.0 management system"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """Initialize OAuth manager
        
        Args:
            encryption_key: Key for token encryption (auto-generated if None)
        """
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[str, OAuthProvider] = {}
        self.tokens: Dict[str, AccessToken] = {}  # user_id:provider -> token
        
        # Setup encryption
        if encryption_key:
            self.fernet = Fernet(encryption_key)
        else:
            key = Fernet.generate_key()
            self.fernet = Fernet(key)
            self.logger.warning("Generated temporary encryption key. Use persistent key in production.")
        
        # Token storage
        self._token_storage = {}
        self._state_storage = {}  # OAuth state tracking
        
        # Setup default providers
        self._setup_default_providers()
    
    def register_provider(self, provider: OAuthProvider):
        """Register OAuth provider
        
        Args:
            provider: OAuth provider configuration
        """
        self.providers[provider.name] = provider
        self.logger.info(f"Registered OAuth provider: {provider.name}")
    
    def _setup_default_providers(self):
        """Setup common OAuth providers"""
        
        # Google OAuth
        google_provider = OAuthProvider(
            name="google",
            client_id="",  # To be configured
            client_secret="",
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            refresh_url="https://oauth2.googleapis.com/token",
            revoke_url="https://oauth2.googleapis.com/revoke",
            scope="openid email profile"
        )
        
        # Facebook OAuth
        facebook_provider = OAuthProvider(
            name="facebook",
            client_id="",  # To be configured
            client_secret="",
            authorization_url="https://www.facebook.com/v18.0/dialog/oauth",
            token_url="https://graph.facebook.com/v18.0/oauth/access_token",
            scope="email,public_profile,pages_read_engagement"
        )
        
        # Twitter OAuth 2.0
        twitter_provider = OAuthProvider(
            name="twitter",
            client_id="",  # To be configured
            client_secret="",
            authorization_url="https://twitter.com/i/oauth2/authorize",
            token_url="https://api.twitter.com/2/oauth2/token",
            revoke_url="https://api.twitter.com/2/oauth2/revoke",
            scope="tweet.read tweet.write users.read follows.read",
            flow_type=OAuthFlow.AUTHORIZATION_CODE,
            token_endpoint_auth_method="client_secret_basic"
        )
        
        # LinkedIn OAuth
        linkedin_provider = OAuthProvider(
            name="linkedin",
            client_id="",  # To be configured
            client_secret="",
            authorization_url="https://www.linkedin.com/oauth/v2/authorization",
            token_url="https://www.linkedin.com/oauth/v2/accessToken",
            scope="r_liteprofile r_emailaddress w_member_social"
        )
        
        # Instagram Basic Display
        instagram_provider = OAuthProvider(
            name="instagram",
            client_id="",  # To be configured
            client_secret="",
            authorization_url="https://api.instagram.com/oauth/authorize",
            token_url="https://api.instagram.com/oauth/access_token",
            refresh_url="https://graph.instagram.com/refresh_access_token",
            scope="user_profile,user_media"
        )
        
        # Spotify OAuth
        spotify_provider = OAuthProvider(
            name="spotify",
            client_id="",  # To be configured
            client_secret="",
            authorization_url="https://accounts.spotify.com/authorize",
            token_url="https://accounts.spotify.com/api/token",
            scope="user-read-private user-read-email playlist-modify-public playlist-modify-private"
        )
        
        # TikTok OAuth
        tiktok_provider = OAuthProvider(
            name="tiktok",
            client_id="",  # To be configured
            client_secret="",
            authorization_url="https://www.tiktok.com/auth/authorize/",
            token_url="https://open-api.tiktok.com/oauth/access_token/",
            refresh_url="https://open-api.tiktok.com/oauth/refresh_token/",
            scope="user.info.basic,video.list,video.upload"
        )
        
        # YouTube OAuth (Google)
        youtube_provider = OAuthProvider(
            name="youtube",
            client_id="",  # To be configured
            client_secret="",
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            refresh_url="https://oauth2.googleapis.com/token",
            scope="https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.upload"
        )
        
        # Store providers (without credentials - to be configured)
        providers = [
            google_provider, facebook_provider, twitter_provider, 
            linkedin_provider, instagram_provider, spotify_provider,
            tiktok_provider, youtube_provider
        ]
        
        for provider in providers:
            if provider.client_id and provider.client_secret:  # Only register if configured
                self.register_provider(provider)
    
    def generate_authorization_url(self, provider_name: str, user_id: str, 
                                 state: Optional[str] = None, **extra_params) -> str:
        """Generate OAuth authorization URL
        
        Args:
            provider_name: OAuth provider name
            user_id: User identifier
            state: OAuth state parameter
            **extra_params: Additional parameters
            
        Returns:
            str: Authorization URL
        """
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        # Generate state if not provided
        if not state:
            state = self._generate_state()
        
        # Store state for verification
        self._state_storage[state] = {
            "provider": provider_name,
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        
        # Build authorization parameters
        params = {
            "response_type": "code",
            "client_id": provider.client_id,
            "state": state,
            "scope": provider.scope or ""
        }
        
        if provider.redirect_uri:
            params["redirect_uri"] = provider.redirect_uri
        
        # Add provider-specific parameters
        if provider.extra_params:
            params.update(provider.extra_params)
        
        # Add extra parameters
        params.update(extra_params)
        
        # Build URL
        url = f"{provider.authorization_url}?{urlencode(params)}"
        
        self.logger.info(f"Generated authorization URL for {provider_name}")
        return url
    
    async def exchange_code_for_token(self, provider_name: str, code: str, 
                                    state: str, redirect_uri: Optional[str] = None) -> AccessToken:
        """Exchange authorization code for access token
        
        Args:
            provider_name: OAuth provider name
            code: Authorization code
            state: OAuth state parameter
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            AccessToken: Access token data
        """
        # Verify state
        if state not in self._state_storage:
            raise ValueError("Invalid or expired OAuth state")
        
        state_data = self._state_storage[state]
        if state_data["provider"] != provider_name:
            raise ValueError("State provider mismatch")
        
        user_id = state_data["user_id"]
        provider = self.providers[provider_name]
        
        # Prepare token request
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": provider.client_id,
            "client_secret": provider.client_secret
        }
        
        if redirect_uri or provider.redirect_uri:
            data["redirect_uri"] = redirect_uri or provider.redirect_uri
        
        # Make token request
        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            # Handle different authentication methods
            if provider.token_endpoint_auth_method == "client_secret_basic":
                auth_string = f"{provider.client_id}:{provider.client_secret}"
                auth_bytes = auth_string.encode('ascii')
                auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                headers["Authorization"] = f"Basic {auth_b64}"
                # Remove client credentials from data
                data.pop("client_id", None)
                data.pop("client_secret", None)
            
            async with session.post(provider.token_url, data=data, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    # Create access token
                    access_token = AccessToken(
                        access_token=token_data["access_token"],
                        token_type=token_data.get("token_type", "Bearer"),
                        expires_in=token_data.get("expires_in"),
                        refresh_token=token_data.get("refresh_token"),
                        scope=token_data.get("scope"),
                        provider=provider_name,
                        user_id=user_id
                    )
                    
                    # Store token
                    token_key = f"{user_id}:{provider_name}"
                    self.tokens[token_key] = access_token
                    await self._store_token_securely(token_key, access_token)
                    
                    # Cleanup state
                    del self._state_storage[state]
                    
                    self.logger.info(f"Successfully exchanged code for token: {provider_name}")
                    return access_token
                
                else:
                    error_data = await response.text()
                    self.logger.error(f"Token exchange failed: {response.status} - {error_data}")
                    raise Exception(f"Token exchange failed: {response.status}")
    
    async def refresh_token(self, provider_name: str, user_id: str) -> Optional[AccessToken]:
        """Refresh access token
        
        Args:
            provider_name: OAuth provider name
            user_id: User identifier
            
        Returns:
            Optional[AccessToken]: Refreshed token or None
        """
        token_key = f"{user_id}:{provider_name}"
        
        if token_key not in self.tokens:
            self.logger.warning(f"No token found for {token_key}")
            return None
        
        current_token = self.tokens[token_key]
        if not current_token.refresh_token:
            self.logger.warning(f"No refresh token available for {token_key}")
            return None
        
        provider = self.providers[provider_name]
        refresh_url = provider.refresh_url or provider.token_url
        
        # Prepare refresh request
        data = {
            "grant_type": "refresh_token",
            "refresh_token": current_token.refresh_token,
            "client_id": provider.client_id,
            "client_secret": provider.client_secret
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                
                async with session.post(refresh_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        
                        # Create new access token
                        new_token = AccessToken(
                            access_token=token_data["access_token"],
                            token_type=token_data.get("token_type", "Bearer"),
                            expires_in=token_data.get("expires_in"),
                            refresh_token=token_data.get("refresh_token", current_token.refresh_token),
                            scope=token_data.get("scope", current_token.scope),
                            provider=provider_name,
                            user_id=user_id
                        )
                        
                        # Update stored token
                        self.tokens[token_key] = new_token
                        await self._store_token_securely(token_key, new_token)
                        
                        self.logger.info(f"Successfully refreshed token: {token_key}")
                        return new_token
                    
                    else:
                        error_data = await response.text()
                        self.logger.error(f"Token refresh failed: {response.status} - {error_data}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Token refresh error for {token_key}: {e}")
            return None
    
    async def get_valid_token(self, provider_name: str, user_id: str) -> Optional[AccessToken]:
        """Get valid access token, refreshing if necessary
        
        Args:
            provider_name: OAuth provider name
            user_id: User identifier
            
        Returns:
            Optional[AccessToken]: Valid token or None
        """
        token_key = f"{user_id}:{provider_name}"
        
        if token_key not in self.tokens:
            # Try to load from storage
            await self._load_token_from_storage(token_key)
        
        if token_key not in self.tokens:
            return None
        
        token = self.tokens[token_key]
        
        # Check if token needs refresh
        if token.expires_soon:
            refreshed_token = await self.refresh_token(provider_name, user_id)
            if refreshed_token:
                return refreshed_token
            else:
                # Remove invalid token
                del self.tokens[token_key]
                return None
        
        return token
    
    async def revoke_token(self, provider_name: str, user_id: str) -> bool:
        """Revoke access token
        
        Args:
            provider_name: OAuth provider name
            user_id: User identifier
            
        Returns:
            bool: Success status
        """
        token_key = f"{user_id}:{provider_name}"
        
        if token_key not in self.tokens:
            return True  # Already revoked
        
        token = self.tokens[token_key]
        provider = self.providers[provider_name]
        
        if provider.revoke_url:
            try:
                data = {"token": token.access_token}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(provider.revoke_url, data=data) as response:
                        success = response.status == 200
                        
                        if success:
                            self.logger.info(f"Successfully revoked token: {token_key}")
                        else:
                            self.logger.warning(f"Token revocation failed: {response.status}")
                            
            except Exception as e:
                self.logger.error(f"Token revocation error for {token_key}: {e}")
        
        # Remove token locally
        del self.tokens[token_key]
        await self._remove_token_from_storage(token_key)
        
        return True
    
    def get_token_status(self, provider_name: str, user_id: str) -> TokenStatus:
        """Get token status
        
        Args:
            provider_name: OAuth provider name
            user_id: User identifier
            
        Returns:
            TokenStatus: Current token status
        """
        token_key = f"{user_id}:{provider_name}"
        
        if token_key not in self.tokens:
            return TokenStatus.INVALID
        
        token = self.tokens[token_key]
        
        if token.is_expired:
            return TokenStatus.EXPIRED
        
        return TokenStatus.VALID
    
    def _generate_state(self) -> str:
        """Generate secure OAuth state parameter
        
        Returns:
            str: Random state string
        """
        return secrets.token_urlsafe(32)
    
    async def _store_token_securely(self, token_key: str, token: AccessToken):
        """Store token securely (encrypted)
        
        Args:
            token_key: Token storage key
            token: Access token data
        """
        try:
            # Serialize token data
            token_data = json.dumps(asdict(token), default=str)
            
            # Encrypt token data
            encrypted_data = self.fernet.encrypt(token_data.encode())
            
            # Store encrypted data
            self._token_storage[token_key] = encrypted_data
            
        except Exception as e:
            self.logger.error(f"Failed to store token securely: {e}")
    
    async def _load_token_from_storage(self, token_key: str):
        """Load token from secure storage
        
        Args:
            token_key: Token storage key
        """
        try:
            if token_key in self._token_storage:
                # Decrypt token data
                encrypted_data = self._token_storage[token_key]
                decrypted_data = self.fernet.decrypt(encrypted_data)
                
                # Deserialize token
                token_dict = json.loads(decrypted_data.decode())
                
                # Convert created_at back to datetime
                if token_dict.get('created_at'):
                    token_dict['created_at'] = datetime.fromisoformat(token_dict['created_at'])
                
                # Create AccessToken object
                token = AccessToken(**token_dict)
                self.tokens[token_key] = token
                
        except Exception as e:
            self.logger.error(f"Failed to load token from storage: {e}")
    
    async def _remove_token_from_storage(self, token_key: str):
        """Remove token from storage
        
        Args:
            token_key: Token storage key
        """
        try:
            if token_key in self._token_storage:
                del self._token_storage[token_key]
        except Exception as e:
            self.logger.error(f"Failed to remove token from storage: {e}")
    
    async def cleanup_expired_tokens(self):
        """Clean up expired tokens"""
        expired_keys = []
        
        for token_key, token in self.tokens.items():
            if token.is_expired and not token.refresh_token:
                expired_keys.append(token_key)
        
        for key in expired_keys:
            del self.tokens[key]
            await self._remove_token_from_storage(key)
        
        self.logger.info(f"Cleaned up {len(expired_keys)} expired tokens")
    
    async def get_all_user_tokens(self, user_id: str) -> Dict[str, AccessToken]:
        """Get all tokens for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict[str, AccessToken]: Provider name to token mapping
        """
        user_tokens = {}
        
        for token_key, token in self.tokens.items():
            if token_key.startswith(f"{user_id}:"):
                provider_name = token_key.split(":", 1)[1]
                user_tokens[provider_name] = token
        
        return user_tokens
    
    async def revoke_all_user_tokens(self, user_id: str) -> Dict[str, bool]:
        """Revoke all tokens for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict[str, bool]: Provider name to success status mapping
        """
        results = {}
        user_tokens = await self.get_all_user_tokens(user_id)
        
        for provider_name in user_tokens:
            results[provider_name] = await self.revoke_token(provider_name, user_id)
        
        return results