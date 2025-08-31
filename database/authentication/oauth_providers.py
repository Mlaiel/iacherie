"""🔐 OAuth Providers Database - Enterprise External Authentication System
=======================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Type: Production-Ready OAuth Provider Management
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING: Unauthorized use strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Business Logic: OAuth Provider Registration → Authorization Flow → Token Exchange → 
Account Linking → Profile Sync → Platform Integration
"""
import asyncio
import secrets
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from uuid import UUID, uuid4
import hashlib

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, Index, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet
import httpx

logger = logging.getLogger(__name__)

Base = declarative_base()

class OAuthProvider(Enum):
    """OAuth provider types"""    GOOGLE = "google"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    GITHUB = "github"
    DISCORD = "discord"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    APPLE = "apple"
    MICROSOFT = "microsoft"

class ConnectionStatus(Enum):
    """OAuth connection status"""    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    ERROR = "error"

class PermissionScope(Enum):
    """OAuth permission scopes"""    PROFILE_READ = "profile:read"
    PROFILE_WRITE = "profile:write"
    EMAIL_READ = "email:read"
    CONTENT_READ = "content:read"
    CONTENT_WRITE = "content:write"
    ANALYTICS_READ = "analytics:read"
    FRIENDS_READ = "friends:read"
    POSTS_READ = "posts:read"
    POSTS_WRITE = "posts:write"
    MEDIA_READ = "media:read"
    MEDIA_WRITE = "media:write"

@dataclass
class OAuthConfig:
    """OAuth provider configuration"""    provider: OAuthProvider
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    user_info_url: str
    scopes: List[str]
    redirect_uri: str

@dataclass
class UserProfile:
    """External user profile data"""    provider_user_id: str
    email: str = ""
    name: str = ""
    username: str = ""
    avatar_url: str = ""
    profile_url: str = ""
    verified: bool = False
    follower_count: int = 0
    additional_data: Dict[str, Any] = field(default_factory=dict)

class OAuthConnections(Base):
    """Database model for OAuth provider connections"""    __tablename__ = 'oauth_connections'
    
    connection_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    provider = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False)
    provider_username = Column(String, nullable=True)
    provider_email = Column(String, nullable=True)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    scopes = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default=ConnectionStatus.CONNECTED.value)
    connected_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    profile_data = Column(JSON, nullable=True)
    connection_metadata = Column(JSON, nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    auto_sync_enabled = Column(Boolean, nullable=False, default=True)
    
    __table_args__ = (
        Index('idx_oauth_user_provider', 'user_id', 'provider'),
        Index('idx_oauth_provider_user_id', 'provider', 'provider_user_id'),
        Index('idx_oauth_status', 'status'),
    )

class OAuthProviderConfigs(Base):
    """Database model for OAuth provider configurations"""    __tablename__ = 'oauth_provider_configs'
    
    config_id = Column(String, primary_key=True)
    provider = Column(String, nullable=False, unique=True)
    client_id = Column(String, nullable=False)
    encrypted_client_secret = Column(Text, nullable=False)
    authorization_url = Column(String, nullable=False)
    token_url = Column(String, nullable=False)
    user_info_url = Column(String, nullable=False)
    default_scopes = Column(JSON, nullable=True)
    redirect_uri = Column(String, nullable=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    rate_limit_per_hour = Column(Integer, nullable=False, default=3600)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    configuration_metadata = Column(JSON, nullable=True)

class OAuthTokens(Base):
    """Database model for OAuth token management"""    __tablename__ = 'oauth_tokens'
    
    token_id = Column(String, primary_key=True)
    connection_id = Column(String, nullable=False, index=True)
    token_type = Column(String, nullable=False)  # access, refresh, id
    encrypted_token_value = Column(Text, nullable=False)
    token_hash = Column(String, nullable=False)
    scopes = Column(JSON, nullable=True)
    issued_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    __table_args__ = (
        Index('idx_oauth_tokens_connection', 'connection_id', 'token_type'),
        Index('idx_oauth_tokens_hash', 'token_hash'),
        Index('idx_oauth_tokens_expires', 'expires_at'),
    )

class OAuthAuditLog(Base):
    """Database model for OAuth audit logging"""    __tablename__ = 'oauth_audit_log'
    
    audit_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    connection_id = Column(String, nullable=True)
    provider = Column(String, nullable=False)
    action = Column(String, nullable=False)  # connect, disconnect, refresh, sync, etc.
    status = Column(String, nullable=False)  # success, failure, error
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_oauth_audit_user_date', 'user_id', 'created_at'),
        Index('idx_oauth_audit_provider_action', 'provider', 'action'),
    )

class OAuthProvidersRepository:
    """    Enterprise-grade OAuth providers management repository.
    
    Features:
    - Multi-provider OAuth integration
    - Secure token storage and refresh
    - Profile synchronization
    - Connection management
    - Comprehensive audit logging
    - Rate limiting and error handling
    """    
    def __init__(
        self,
        session: AsyncSession,
        encryption_key: str,
        base_redirect_uri: str = "https://app.iainfluenceragent.com/auth/callback"
    ):
        self.session = session
        self.fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        self.base_redirect_uri = base_redirect_uri
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Provider-specific configurations
        self.provider_configs = {
            OAuthProvider.GOOGLE: {
                'authorization_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'default_scopes': ['openid', 'email', 'profile']
            },
            OAuthProvider.SPOTIFY: {
                'authorization_url': 'https://accounts.spotify.com/authorize',
                'token_url': 'https://accounts.spotify.com/api/token',
                'user_info_url': 'https://api.spotify.com/v1/me',
                'default_scopes': ['user-read-email', 'user-read-private', 'playlist-read-private']
            },
            OAuthProvider.GITHUB: {
                'authorization_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'user_info_url': 'https://api.github.com/user',
                'default_scopes': ['read:user', 'user:email']
            },
            OAuthProvider.FACEBOOK: {
                'authorization_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'user_info_url': 'https://graph.facebook.com/v18.0/me',
                'default_scopes': ['email', 'public_profile']
            },
            OAuthProvider.INSTAGRAM: {
                'authorization_url': 'https://api.instagram.com/oauth/authorize',
                'token_url': 'https://api.instagram.com/oauth/access_token',
                'user_info_url': 'https://graph.instagram.com/me',
                'default_scopes': ['user_profile', 'user_media']
            }
        }
    
    async def setup_provider_config(
        self,
        provider: OAuthProvider,
        client_id: str,
        client_secret: str,
        custom_scopes: Optional[List[str]] = None
    ) -> str:
        """Setup OAuth provider configuration"""        try:
            config = self.provider_configs.get(provider)
            if not config:
                raise ValueError(f"Provider {provider.value} is not supported")
            
            # Encrypt client secret
            encrypted_secret = self.fernet.encrypt(client_secret.encode()).decode()
            
            config_id = str(uuid4())
            redirect_uri = f"{self.base_redirect_uri}/{provider.value}"
            
            provider_config = OAuthProviderConfigs(
                config_id=config_id,
                provider=provider.value,
                client_id=client_id,
                encrypted_client_secret=encrypted_secret,
                authorization_url=config['authorization_url'],
                token_url=config['token_url'],
                user_info_url=config['user_info_url'],
                default_scopes=custom_scopes or config['default_scopes'],
                redirect_uri=redirect_uri
            )
            
            self.session.add(provider_config)
            await self.session.commit()
            
            logger.info(f"OAuth provider {provider.value} configured successfully")
            return config_id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to setup provider config for {provider.value}: {e}")
            raise
    
    async def generate_authorization_url(
        self,
        provider: OAuthProvider,
        user_id: str,
        custom_scopes: Optional[List[str]] = None,
        state_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate OAuth authorization URL"""        try:
            # Get provider configuration
            config = await self._get_provider_config(provider)
            if not config:
                raise ValueError(f"Provider {provider.value} is not configured")
            
            # Generate state parameter for security
            state_data = state_data or {}
            state_data.update({
                'user_id': user_id,
                'provider': provider.value,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            state = self.fernet.encrypt(json.dumps(state_data).encode()).decode()
            
            # Prepare authorization URL parameters
            scopes = custom_scopes or config.default_scopes
            scope_string = ' '.join(scopes) if isinstance(scopes, list) else scopes
            
            auth_params = {
                'response_type': 'code',
                'client_id': config.client_id,
                'redirect_uri': config.redirect_uri,
                'scope': scope_string,
                'state': state,
                'access_type': 'offline',  # For refresh token (Google)
                'prompt': 'consent'  # Force consent screen
            }
            
            # Provider-specific parameters
            if provider == OAuthProvider.SPOTIFY:
                auth_params['show_dialog'] = 'true'
            elif provider == OAuthProvider.FACEBOOK:
                auth_params['response_type'] = 'code'
                auth_params['display'] = 'popup'
            
            # Build authorization URL
            params_str = '&'.join([f"{k}={v}" for k, v in auth_params.items()])
            authorization_url = f"{config.authorization_url}?{params_str}"
            
            logger.info(f"Authorization URL generated for {provider.value} and user {user_id}")
            
            return {
                'authorization_url': authorization_url,
                'state': state,
                'provider': provider.value
            }
            
        except Exception as e:
            logger.error(f"Failed to generate authorization URL for {provider.value}: {e}")
            raise
    
    async def exchange_authorization_code(
        self,
        provider: OAuthProvider,
        authorization_code: str,
        state: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token"""        try:
            # Verify and decode state
            state_data = json.loads(self.fernet.decrypt(state.encode()).decode())
            user_id = state_data.get('user_id')
            
            if not user_id:
                raise ValueError("Invalid state parameter")
            
            # Get provider configuration
            config = await self._get_provider_config(provider)
            if not config:
                raise ValueError(f"Provider {provider.value} is not configured")
            
            # Decrypt client secret
            client_secret = self.fernet.decrypt(config.encrypted_client_secret.encode()).decode()
            
            # Prepare token request
            token_data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': config.redirect_uri,
                'client_id': config.client_id,
                'client_secret': client_secret
            }
            
            # Exchange code for tokens
            async with self.http_client as client:
                response = await client.post(
                    config.token_url,
                    data=token_data,
                    headers={'Accept': 'application/json'}
                )
                response.raise_for_status()
                token_response = response.json()
            
            # Get user profile from provider
            user_profile = await self._fetch_user_profile(
                provider,
                token_response['access_token'],
                config.user_info_url
            )
            
            # Store OAuth connection
            connection_id = await self._store_oauth_connection(
                user_id=user_id,
                provider=provider,
                token_response=token_response,
                user_profile=user_profile,
                scopes=state_data.get('scopes', config.default_scopes)
            )
            
            # Log successful connection
            await self._log_oauth_action(
                user_id=user_id,
                provider=provider,
                action="connect",
                status="success",
                connection_id=connection_id
            )
            
            logger.info(f"OAuth connection established for {provider.value} and user {user_id}")
            
            return {
                'connection_id': connection_id,
                'user_profile': user_profile,
                'provider': provider.value,
                'connected_at': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            # Log failed connection attempt
            if 'user_id' in locals():
                await self._log_oauth_action(
                    user_id=user_id,
                    provider=provider,
                    action="connect",
                    status="failure",
                    error_message=str(e)
                )
            
            logger.error(f"OAuth code exchange failed for {provider.value}: {e}")
            raise
    
    async def refresh_access_token(self, connection_id: str) -> bool:
        """Refresh OAuth access token"""        try:
            # Get connection
            stmt = select(OAuthConnections).where(OAuthConnections.connection_id == connection_id)
            result = await self.session.execute(stmt)
            connection = result.scalar_one_or_none()
            
            if not connection or not connection.encrypted_refresh_token:
                raise ValueError("Connection not found or no refresh token available")
            
            # Get provider configuration
            provider = OAuthProvider(connection.provider)
            config = await self._get_provider_config(provider)
            
            # Decrypt tokens
            refresh_token = self.fernet.decrypt(connection.encrypted_refresh_token.encode()).decode()
            client_secret = self.fernet.decrypt(config.encrypted_client_secret.encode()).decode()
            
            # Prepare refresh request
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': config.client_id,
                'client_secret': client_secret
            }
            
            # Request new tokens
            async with self.http_client as client:
                response = await client.post(
                    config.token_url,
                    data=refresh_data,
                    headers={'Accept': 'application/json'}
                )
                response.raise_for_status()
                token_response = response.json()
            
            # Update stored tokens
            connection.encrypted_access_token = self.fernet.encrypt(
                token_response['access_token'].encode()
            ).decode()
            
            if 'refresh_token' in token_response:
                connection.encrypted_refresh_token = self.fernet.encrypt(
                    token_response['refresh_token'].encode()
                ).decode()
            
            if 'expires_in' in token_response:
                connection.token_expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=token_response['expires_in']
                )
            
            connection.last_used_at = datetime.now(timezone.utc)
            connection.status = ConnectionStatus.CONNECTED.value
            
            await self.session.commit()
            
            # Log successful refresh
            await self._log_oauth_action(
                user_id=connection.user_id,
                provider=provider,
                action="refresh_token",
                status="success",
                connection_id=connection_id
            )
            
            logger.info(f"Access token refreshed for connection {connection_id}")
            return True
            
        except Exception as e:
            # Mark connection as expired if refresh fails
            if 'connection' in locals():
                connection.status = ConnectionStatus.EXPIRED.value
                await self.session.commit()
                
                await self._log_oauth_action(
                    user_id=connection.user_id,
                    provider=OAuthProvider(connection.provider),
                    action="refresh_token",
                    status="failure",
                    connection_id=connection_id,
                    error_message=str(e)
                )
            
            logger.error(f"Token refresh failed for connection {connection_id}: {e}")
            return False
    
    async def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all OAuth connections for a user"""        try:
            stmt = select(OAuthConnections).where(
                OAuthConnections.user_id == user_id
            ).order_by(OAuthConnections.connected_at.desc())
            
            result = await self.session.execute(stmt)
            connections = result.scalars().all()
            
            connection_list = []
            for conn in connections:
                profile_data = conn.profile_data or {}
                connection_info = {
                    'connection_id': conn.connection_id,
                    'provider': conn.provider,
                    'provider_username': conn.provider_username,
                    'provider_email': conn.provider_email,
                    'status': conn.status,
                    'connected_at': conn.connected_at,
                    'last_used_at': conn.last_used_at,
                    'last_sync_at': conn.last_sync_at,
                    'is_primary': conn.is_primary,
                    'auto_sync_enabled': conn.auto_sync_enabled,
                    'profile_data': {
                        'name': profile_data.get('name'),
                        'avatar_url': profile_data.get('avatar_url'),
                        'verified': profile_data.get('verified', False),
                        'follower_count': profile_data.get('follower_count', 0)
                    },
                    'token_expires_at': conn.token_expires_at,
                    'needs_refresh': (
                        conn.token_expires_at and 
                        conn.token_expires_at < datetime.now(timezone.utc) + timedelta(minutes=5)
                    ) if conn.token_expires_at else False
                }
                connection_list.append(connection_info)
            
            return connection_list
            
        except Exception as e:
            logger.error(f"Failed to get user connections for {user_id}: {e}")
            raise
    
    async def disconnect_provider(self, user_id: str, connection_id: str, reason: str = "User requested") -> bool:
        """Disconnect OAuth provider"""        try:
            stmt = select(OAuthConnections).where(
                OAuthConnections.connection_id == connection_id,
                OAuthConnections.user_id == user_id
            )
            result = await self.session.execute(stmt)
            connection = result.scalar_one_or_none()
            
            if not connection:
                raise ValueError("Connection not found")
            
            # Revoke tokens at provider if possible
            try:
                await self._revoke_provider_tokens(connection)
            except Exception as e:
                logger.warning(f"Failed to revoke tokens at provider: {e}")
            
            # Update connection status
            connection.status = ConnectionStatus.DISCONNECTED.value
            connection.last_used_at = datetime.now(timezone.utc)
            
            # Clear sensitive data
            connection.encrypted_access_token = ""
            connection.encrypted_refresh_token = ""
            
            await self.session.commit()
            
            # Log disconnection
            await self._log_oauth_action(
                user_id=user_id,
                provider=OAuthProvider(connection.provider),
                action="disconnect",
                status="success",
                connection_id=connection_id
            )
            
            logger.info(f"OAuth connection {connection_id} disconnected: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect OAuth connection {connection_id}: {e}")
            raise
    
    async def sync_user_profile(self, connection_id: str) -> Dict[str, Any]:
        """Sync user profile from OAuth provider"""        try:
            # Get connection
            stmt = select(OAuthConnections).where(OAuthConnections.connection_id == connection_id)
            result = await self.session.execute(stmt)
            connection = result.scalar_one_or_none()
            
            if not connection:
                raise ValueError("Connection not found")
            
            if connection.status != ConnectionStatus.CONNECTED.value:
                raise ValueError("Connection is not active")
            
            # Check if token needs refresh
            if (connection.token_expires_at and 
                connection.token_expires_at < datetime.now(timezone.utc) + timedelta(minutes=5)):
                await self.refresh_access_token(connection_id)
                # Reload connection after refresh
                await self.session.refresh(connection)
            
            # Get provider config
            provider = OAuthProvider(connection.provider)
            config = await self._get_provider_config(provider)
            
            # Decrypt access token
            access_token = self.fernet.decrypt(connection.encrypted_access_token.encode()).decode()
            
            # Fetch updated profile
            user_profile = await self._fetch_user_profile(
                provider,
                access_token,
                config.user_info_url
            )
            
            # Update stored profile data
            connection.profile_data = user_profile.__dict__
            connection.provider_username = user_profile.username
            connection.provider_email = user_profile.email
            connection.last_sync_at = datetime.now(timezone.utc)
            
            await self.session.commit()
            
            # Log successful sync
            await self._log_oauth_action(
                user_id=connection.user_id,
                provider=provider,
                action="sync_profile",
                status="success",
                connection_id=connection_id
            )
            
            logger.info(f"Profile synced for connection {connection_id}")
            return user_profile.__dict__
            
        except Exception as e:
            # Log failed sync
            if 'connection' in locals():
                await self._log_oauth_action(
                    user_id=connection.user_id,
                    provider=OAuthProvider(connection.provider),
                    action="sync_profile",
                    status="failure",
                    connection_id=connection_id,
                    error_message=str(e)
                )
            
            logger.error(f"Profile sync failed for connection {connection_id}: {e}")
            raise
    
    # Private helper methods
    
    async def _get_provider_config(self, provider: OAuthProvider) -> Optional[OAuthProviderConfigs]:
        """Get OAuth provider configuration"""        stmt = select(OAuthProviderConfigs).where(
            OAuthProviderConfigs.provider == provider.value,
            OAuthProviderConfigs.is_enabled == True
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _fetch_user_profile(
        self,
        provider: OAuthProvider,
        access_token: str,
        user_info_url: str
    ) -> UserProfile:
        """Fetch user profile from OAuth provider"""        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Provider-specific API calls
        if provider == OAuthProvider.FACEBOOK:
            user_info_url += '?fields=id,name,email,picture'
        elif provider == OAuthProvider.INSTAGRAM:
            user_info_url += '?fields=id,username,media_count,account_type'
        
        async with self.http_client as client:
            response = await client.get(user_info_url, headers=headers)
            response.raise_for_status()
            profile_data = response.json()
        
        # Parse profile data based on provider
        if provider == OAuthProvider.GOOGLE:
            return UserProfile(
                provider_user_id=profile_data.get('id', ''),
                email=profile_data.get('email', ''),
                name=profile_data.get('name', ''),
                avatar_url=profile_data.get('picture', ''),
                verified=profile_data.get('verified_email', False)
            )
        elif provider == OAuthProvider.SPOTIFY:
            return UserProfile(
                provider_user_id=profile_data.get('id', ''),
                email=profile_data.get('email', ''),
                name=profile_data.get('display_name', ''),
                avatar_url=profile_data.get('images', [{}])[0].get('url', '') if profile_data.get('images') else '',
                follower_count=profile_data.get('followers', {}).get('total', 0)
            )
        elif provider == OAuthProvider.GITHUB:
            return UserProfile(
                provider_user_id=str(profile_data.get('id', '')),
                email=profile_data.get('email', ''),
                name=profile_data.get('name', ''),
                username=profile_data.get('login', ''),
                avatar_url=profile_data.get('avatar_url', ''),
                profile_url=profile_data.get('html_url', ''),
                follower_count=profile_data.get('followers', 0)
            )
        else:
            # Generic profile parsing
            return UserProfile(
                provider_user_id=str(profile_data.get('id', profile_data.get('user_id', ''))),
                email=profile_data.get('email', ''),
                name=profile_data.get('name', profile_data.get('display_name', '')),
                username=profile_data.get('username', profile_data.get('login', '')),
                avatar_url=profile_data.get('avatar_url', profile_data.get('picture', ''))
            )
    
    async def _store_oauth_connection(
        self,
        user_id: str,
        provider: OAuthProvider,
        token_response: Dict[str, Any],
        user_profile: UserProfile,
        scopes: List[str]
    ) -> str:
        """Store OAuth connection in database"""        connection_id = str(uuid4())
        
        # Encrypt tokens
        encrypted_access_token = self.fernet.encrypt(token_response['access_token'].encode()).decode()
        encrypted_refresh_token = None
        
        if 'refresh_token' in token_response:
            encrypted_refresh_token = self.fernet.encrypt(token_response['refresh_token'].encode()).decode()
        
        # Calculate token expiration
        token_expires_at = None
        if 'expires_in' in token_response:
            token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_response['expires_in'])
        
        # Check if this should be the primary connection for this provider
        is_primary = not await self._has_primary_connection(user_id, provider)
        
        connection = OAuthConnections(
            connection_id=connection_id,
            user_id=user_id,
            provider=provider.value,
            provider_user_id=user_profile.provider_user_id,
            provider_username=user_profile.username,
            provider_email=user_profile.email,
            encrypted_access_token=encrypted_access_token,
            encrypted_refresh_token=encrypted_refresh_token,
            token_expires_at=token_expires_at,
            scopes=scopes,
            status=ConnectionStatus.CONNECTED.value,
            profile_data=user_profile.__dict__,
            is_primary=is_primary,
            connection_metadata={
                'token_type': token_response.get('token_type', 'Bearer'),
                'scope': token_response.get('scope', ' '.join(scopes))
            }
        )
        
        self.session.add(connection)
        await self.session.commit()
        
        return connection_id
    
    async def _has_primary_connection(self, user_id: str, provider: OAuthProvider) -> bool:
        """Check if user has a primary connection for provider"""        stmt = select(OAuthConnections).where(
            OAuthConnections.user_id == user_id,
            OAuthConnections.provider == provider.value,
            OAuthConnections.is_primary == True,
            OAuthConnections.status == ConnectionStatus.CONNECTED.value
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def _revoke_provider_tokens(self, connection: OAuthConnections):
        """Revoke tokens at OAuth provider"""        try:
            provider = OAuthProvider(connection.provider)
            config = await self._get_provider_config(provider)
            
            if not config:
                return
            
            # Decrypt tokens
            access_token = self.fernet.decrypt(connection.encrypted_access_token.encode()).decode()
            
            # Provider-specific revocation
            if provider == OAuthProvider.GOOGLE:
                revoke_url = f"https://oauth2.googleapis.com/revoke?token={access_token}"
                async with self.http_client as client:
                    await client.post(revoke_url)
            elif provider == OAuthProvider.GITHUB:
                # GitHub requires different approach
                pass
            
        except Exception as e:
            logger.warning(f"Token revocation failed at provider: {e}")
    
    async def _log_oauth_action(
        self,
        user_id: str,
        provider: OAuthProvider,
        action: str,
        status: str,
        connection_id: Optional[str] = None,
        error_message: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log OAuth action for audit purposes"""        try:
            audit_log = OAuthAuditLog(
                audit_id=str(uuid4()),
                user_id=user_id,
                connection_id=connection_id,
                provider=provider.value,
                action=action,
                status=status,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=error_message,
                request_data=request_data,
                response_data=response_data
            )
            
            self.session.add(audit_log)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log OAuth action: {e}")

# Export the main classes
__all__ = [
    'OAuthProvidersRepository',
    'OAuthConnections',
    'OAuthProviderConfigs',
    'OAuthTokens',
    'OAuthAuditLog',
    'OAuthProvider',
    'ConnectionStatus',
    'PermissionScope',
    'OAuthConfig',
    'UserProfile'
]
