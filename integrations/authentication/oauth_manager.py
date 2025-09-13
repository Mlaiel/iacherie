"""OAuth Manager - Universal OAuth 2.0 Management
==============================================

Universal OAuth 2.0 authentication system for all third-party integrations.
Supports multiple providers with secure token management and refresh logic.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import secrets
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import base64
from urllib.parse import urlencode, parse_qs

import httpx
from cryptography.fernet import Fernet
import jwt


class OAuthProvider(Enum):
    """Supported OAuth providers."""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    DISCORD = "discord"
    TWITCH = "twitch"
    TIKTOK = "tiktok"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    CUSTOM = "custom"


class OAuthFlow(Enum):
    """OAuth flow types."""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"
    REFRESH_TOKEN = "refresh_token"


@dataclass
class OAuthConfig:
    """OAuth provider configuration."""
    provider: OAuthProvider
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    refresh_url: Optional[str] = None
    scope: List[str] = field(default_factory=list)
    redirect_uri: str = ""
    revoke_url: Optional[str] = None
    user_info_url: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OAuthToken:
    """OAuth token data."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    expires_at: Optional[datetime] = None
    scope: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OAuthSession:
    """OAuth session management."""
    user_id: str
    provider: OAuthProvider
    integration_name: str
    token: OAuthToken
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


class OAuthManager:
    """Universal OAuth 2.0 authentication manager.
    
    Provides secure, centralized OAuth management for all platform integrations.
    Supports multiple providers, token refresh, and session management.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize OAuth manager with encryption."""
        # Generate or use provided encryption key
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Provider configurations
        self.providers: Dict[OAuthProvider, OAuthConfig] = {}
        
        # Active sessions
        self.sessions: Dict[str, OAuthSession] = {}
        
        # State management for security
        self.pending_states: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default provider configurations
        self._initialize_default_providers()
    
    def _initialize_default_providers(self) -> None:
        """Initialize default OAuth provider configurations."""
        default_providers = {
            OAuthProvider.GOOGLE: OAuthConfig(
                provider=OAuthProvider.GOOGLE,
                client_id="",  # To be configured
                client_secret="",  # To be configured
                authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token",
                refresh_url="https://oauth2.googleapis.com/token",
                user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
                scope=["openid", "email", "profile"]
            ),
            OAuthProvider.FACEBOOK: OAuthConfig(
                provider=OAuthProvider.FACEBOOK,
                client_id="",
                client_secret="",
                authorization_url="https://www.facebook.com/v18.0/dialog/oauth",
                token_url="https://graph.facebook.com/v18.0/oauth/access_token",
                user_info_url="https://graph.facebook.com/v18.0/me",
                scope=["email", "public_profile", "pages_manage_posts"]
            ),
            OAuthProvider.TWITTER: OAuthConfig(
                provider=OAuthProvider.TWITTER,
                client_id="",
                client_secret="",
                authorization_url="https://twitter.com/i/oauth2/authorize",
                token_url="https://api.twitter.com/2/oauth2/token",
                refresh_url="https://api.twitter.com/2/oauth2/token",
                revoke_url="https://api.twitter.com/2/oauth2/revoke",
                scope=["tweet.read", "tweet.write", "users.read"]
            ),
            OAuthProvider.SPOTIFY: OAuthConfig(
                provider=OAuthProvider.SPOTIFY,
                client_id="",
                client_secret="",
                authorization_url="https://accounts.spotify.com/authorize",
                token_url="https://accounts.spotify.com/api/token",
                refresh_url="https://accounts.spotify.com/api/token",
                scope=["user-read-private", "user-read-email", "playlist-modify-public"]
            ),
            OAuthProvider.LINKEDIN: OAuthConfig(
                provider=OAuthProvider.LINKEDIN,
                client_id="",
                client_secret="",
                authorization_url="https://www.linkedin.com/oauth/v2/authorization",
                token_url="https://www.linkedin.com/oauth/v2/accessToken",
                user_info_url="https://api.linkedin.com/v2/people/~",
                scope=["r_liteprofile", "r_emailaddress", "w_member_social"]
            ),
            OAuthProvider.GITHUB: OAuthConfig(
                provider=OAuthProvider.GITHUB,
                client_id="",
                client_secret="",
                authorization_url="https://github.com/login/oauth/authorize",
                token_url="https://github.com/login/oauth/access_token",
                user_info_url="https://api.github.com/user",
                scope=["user", "repo"]
            ),
            OAuthProvider.DISCORD: OAuthConfig(
                provider=OAuthProvider.DISCORD,
                client_id="",
                client_secret="",
                authorization_url="https://discord.com/api/oauth2/authorize",
                token_url="https://discord.com/api/oauth2/token",
                refresh_url="https://discord.com/api/oauth2/token",
                revoke_url="https://discord.com/api/oauth2/token/revoke",
                scope=["identify", "email", "guilds"]
            ),
            OAuthProvider.TWITCH: OAuthConfig(
                provider=OAuthProvider.TWITCH,
                client_id="",
                client_secret="",
                authorization_url="https://id.twitch.tv/oauth2/authorize",
                token_url="https://id.twitch.tv/oauth2/token",
                refresh_url="https://id.twitch.tv/oauth2/token",
                revoke_url="https://id.twitch.tv/oauth2/revoke",
                scope=["user:read:email", "channel:read:subscriptions"]
            ),
            OAuthProvider.TIKTOK: OAuthConfig(
                provider=OAuthProvider.TIKTOK,
                client_id="",
                client_secret="",
                authorization_url="https://www.tiktok.com/auth/authorize/",
                token_url="https://open-api.tiktok.com/oauth/access_token/",
                refresh_url="https://open-api.tiktok.com/oauth/refresh_token/",
                scope=["user.info.basic", "video.list"]
            ),
        }
        
        self.providers.update(default_providers)
    
    async def register_provider(self, config: OAuthConfig) -> bool:
        """Register a new OAuth provider."""
        try:
            if not self._validate_provider_config(config):
                return False
            
            self.providers[config.provider] = config
            return True
            
        except Exception:
            return False
    
    async def configure_provider(
        self,
        provider: OAuthProvider,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        additional_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Configure OAuth provider credentials."""
        try:
            if provider not in self.providers:
                return False
            
            config = self.providers[provider]
            config.client_id = client_id
            config.client_secret = self._encrypt_secret(client_secret)
            config.redirect_uri = redirect_uri
            
            if additional_config:
                config.additional_params.update(additional_config)
            
            return True
            
        except Exception:
            return False
    
    async def get_authorization_url(
        self,
        provider: OAuthProvider,
        integration_name: str,
        user_id: str,
        custom_scope: Optional[List[str]] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """Generate OAuth authorization URL with state parameter."""
        if provider not in self.providers:
            raise ValueError(f"Provider not configured: {provider}")
        
        config = self.providers[provider]
        
        # Generate secure state parameter
        state = self._generate_state()
        
        # Store state information
        self.pending_states[state] = {
            "provider": provider,
            "integration_name": integration_name,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Prepare authorization parameters
        scope = custom_scope or config.scope
        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(scope),
            "state": state,
            "response_type": "code"
        }
        
        # Add provider-specific parameters
        params.update(config.additional_params)
        
        if additional_params:
            params.update(additional_params)
        
        # Construct authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return auth_url, state
    
    async def exchange_code_for_token(
        self,
        code: str,
        state: str,
        flow: OAuthFlow = OAuthFlow.AUTHORIZATION_CODE
    ) -> Optional[OAuthSession]:
        """Exchange authorization code for access token."""
        try:
            # Validate state
            state_info = self._validate_and_consume_state(state)
            if not state_info:
                return None
            
            provider = state_info["provider"]
            config = self.providers[provider]
            
            # Prepare token request
            token_data = {
                "client_id": config.client_id,
                "client_secret": self._decrypt_secret(config.client_secret),
                "code": code,
                "redirect_uri": config.redirect_uri,
                "grant_type": flow.value
            }
            
            # Exchange code for token
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config.token_url,
                    data=token_data,
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code != 200:
                    return None
                
                token_response = response.json()
            
            # Parse token response
            oauth_token = self._parse_token_response(token_response)
            
            # Create session
            session = OAuthSession(
                user_id=state_info["user_id"],
                provider=provider,
                integration_name=state_info["integration_name"],
                token=oauth_token,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store session
            session_key = self._generate_session_key(
                state_info["user_id"], provider, state_info["integration_name"]
            )
            self.sessions[session_key] = session
            
            return session
            
        except Exception:
            return None
    
    async def refresh_token(self, session_key: str) -> Optional[OAuthToken]:
        """Refresh OAuth access token."""
        try:
            if session_key not in self.sessions:
                return None
            
            session = self.sessions[session_key]
            
            if not session.token.refresh_token:
                return None
            
            config = self.providers[session.provider]
            
            if not config.refresh_url:
                return None
            
            # Prepare refresh request
            refresh_data = {
                "client_id": config.client_id,
                "client_secret": self._decrypt_secret(config.client_secret),
                "refresh_token": session.token.refresh_token,
                "grant_type": OAuthFlow.REFRESH_TOKEN.value
            }
            
            # Refresh token
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config.refresh_url,
                    data=refresh_data,
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code != 200:
                    return None
                
                token_response = response.json()
            
            # Parse new token
            new_token = self._parse_token_response(token_response)
            
            # Update session
            session.token = new_token
            session.updated_at = datetime.utcnow()
            
            return new_token
            
        except Exception:
            return None
    
    async def get_valid_token(self, session_key: str) -> Optional[str]:
        """Get valid access token, refreshing if necessary."""
        if session_key not in self.sessions:
            return None
        
        session = self.sessions[session_key]
        
        # Check if token is expired
        if self._is_token_expired(session.token):
            # Try to refresh
            new_token = await self.refresh_token(session_key)
            if not new_token:
                # Remove invalid session
                del self.sessions[session_key]
                return None
        
        return session.token.access_token
    
    async def revoke_token(self, session_key: str) -> bool:
        """Revoke OAuth token and invalidate session."""
        try:
            if session_key not in self.sessions:
                return False
            
            session = self.sessions[session_key]
            config = self.providers[session.provider]
            
            if config.revoke_url:
                # Revoke token with provider
                revoke_data = {
                    "client_id": config.client_id,
                    "client_secret": self._decrypt_secret(config.client_secret),
                    "token": session.token.access_token
                }
                
                async with httpx.AsyncClient() as client:
                    await client.post(config.revoke_url, data=revoke_data)
            
            # Remove session
            del self.sessions[session_key]
            
            return True
            
        except Exception:
            return False
    
    async def get_user_info(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get user information using OAuth token."""
        try:
            if session_key not in self.sessions:
                return None
            
            session = self.sessions[session_key]
            config = self.providers[session.provider]
            
            if not config.user_info_url:
                return None
            
            # Get valid token
            access_token = await self.get_valid_token(session_key)
            if not access_token:
                return None
            
            # Fetch user info
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    config.user_info_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    return None
                
                return response.json()
                
        except Exception:
            return None
    
    async def validate_session(self, session_key: str) -> bool:
        """Validate OAuth session."""
        if session_key not in self.sessions:
            return False
        
        session = self.sessions[session_key]
        
        if not session.is_active:
            return False
        
        # Check token expiration
        if self._is_token_expired(session.token):
            # Try to refresh
            new_token = await self.refresh_token(session_key)
            return new_token is not None
        
        return True
    
    async def get_session_info(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get OAuth session information."""
        if session_key not in self.sessions:
            return None
        
        session = self.sessions[session_key]
        
        return {
            "user_id": session.user_id,
            "provider": session.provider.value,
            "integration_name": session.integration_name,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "is_active": session.is_active,
            "has_refresh_token": session.token.refresh_token is not None,
            "expires_at": session.token.expires_at.isoformat() if session.token.expires_at else None,
            "scope": session.token.scope
        }
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and states."""
        cleaned_count = 0
        current_time = datetime.utcnow()
        
        # Clean expired sessions
        expired_sessions = [
            key for key, session in self.sessions.items()
            if self._is_token_expired(session.token) and not session.token.refresh_token
        ]
        
        for session_key in expired_sessions:
            del self.sessions[session_key]
            cleaned_count += 1
        
        # Clean expired states
        expired_states = [
            state for state, info in self.pending_states.items()
            if current_time > info["expires_at"]
        ]
        
        for state in expired_states:
            del self.pending_states[state]
            cleaned_count += 1
        
        return cleaned_count
    
    def _generate_state(self) -> str:
        """Generate secure state parameter."""
        return secrets.token_urlsafe(32)
    
    def _generate_session_key(self, user_id: str, provider: OAuthProvider, integration_name: str) -> str:
        """Generate session key."""
        key_data = f"{user_id}:{provider.value}:{integration_name}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _encrypt_secret(self, secret: str) -> str:
        """Encrypt OAuth secret."""
        return self.cipher_suite.encrypt(secret.encode()).decode()
    
    def _decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt OAuth secret."""
        return self.cipher_suite.decrypt(encrypted_secret.encode()).decode()
    
    def _validate_provider_config(self, config: OAuthConfig) -> bool:
        """Validate OAuth provider configuration."""
        required_fields = ["client_id", "authorization_url", "token_url"]
        
        for field in required_fields:
            if not getattr(config, field):
                return False
        
        return True
    
    def _validate_and_consume_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Validate and consume OAuth state parameter."""
        if state not in self.pending_states:
            return None
        
        state_info = self.pending_states[state]
        
        # Check expiration
        if datetime.utcnow() > state_info["expires_at"]:
            del self.pending_states[state]
            return None
        
        # Consume state (remove it)
        del self.pending_states[state]
        
        return state_info
    
    def _parse_token_response(self, response: Dict[str, Any]) -> OAuthToken:
        """Parse token response from OAuth provider."""
        expires_in = response.get("expires_in")
        expires_at = None
        
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
        
        scope = response.get("scope", "")
        if isinstance(scope, str):
            scope = scope.split() if scope else []
        
        return OAuthToken(
            access_token=response["access_token"],
            refresh_token=response.get("refresh_token"),
            token_type=response.get("token_type", "Bearer"),
            expires_in=expires_in,
            expires_at=expires_at,
            scope=scope,
            metadata={k: v for k, v in response.items() if k not in [
                "access_token", "refresh_token", "token_type", "expires_in", "scope"
            ]}
        )
    
    def _is_token_expired(self, token: OAuthToken) -> bool:
        """Check if token is expired."""
        if not token.expires_at:
            return False
        
        # Add 5-minute buffer for token refresh
        buffer_time = timedelta(minutes=5)
        return datetime.utcnow() + buffer_time >= token.expires_at