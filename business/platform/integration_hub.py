"""Integration Hub - Universal Platform Integration Manager

Central hub for managing all platform integrations, API connections,
authentication flows, and data synchronization across multiple platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

import aiohttp
import httpx
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from ...core.config import settings
from ...core.logging import get_logger
from ...core.security import verify_oauth_token
from ...models.integration import PlatformIntegration, IntegrationStatus, APICredentials
from ...services.oauth.oauth_manager import OAuthManager
from ...services.webhook.webhook_handler import WebhookHandler
from ...utils.encryption_utils import encrypt_sensitive_data, decrypt_sensitive_data

logger = get_logger(__name__)

class IntegrationType(Enum):
    """Integration types"""    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    WEBHOOK = "webhook"
    RSS_FEED = "rss_feed"
    CUSTOM = "custom"

class PlatformCategory(Enum):
    """Platform categories"""    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    BLOG_PLATFORM = "blog_platform"
    ECOMMERCE = "ecommerce"
    ANALYTICS = "analytics"
    PAYMENT = "payment"

@dataclass
class PlatformInfo:
    """Platform information structure"""    platform_id: str
    name: str
    category: PlatformCategory
    integration_type: IntegrationType
    api_version: str
    base_url: str
    oauth_config: Optional[Dict[str, str]] = None
    rate_limits: Optional[Dict[str, int]] = None
    features: List[str] = field(default_factory=list)
    webhook_support: bool = False

@dataclass
class IntegrationResult:
    """Integration operation result"""    success: bool
    platform_id: str
    integration_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntegrationHub:
    """    Universal platform integration manager
    
    Features:
    - Multi-platform OAuth2 authentication
    - API key management and rotation
    - Webhook endpoint management
    - Rate limit handling and queuing
    - Token refresh automation
    - Integration health monitoring
    - Cross-platform data synchronization
    """    
    def __init__(self):
        self.oauth_manager = OAuthManager()
        self.webhook_handler = WebhookHandler()
        
        # Platform configurations
        self.platform_configs = self._initialize_platform_configs()
        
        # Active integrations cache
        self.active_integrations = {}
        
        # Rate limit tracking
        self.rate_limits = {}
        
        # HTTP clients for different platforms
        self.http_clients = {}
        
    async def initialize(self) -> bool:
        """        Initialize integration hub
        
        Returns:
            bool: Initialization success status
        """        try:
            logger.info("Initializing Integration Hub...")
            
            # Initialize OAuth manager
            await self.oauth_manager.initialize()
            
            # Initialize webhook handler
            await self.webhook_handler.initialize()
            
            # Initialize HTTP clients
            await self._initialize_http_clients()
            
            # Start background tasks
            asyncio.create_task(self._monitor_integrations())
            asyncio.create_task(self._refresh_tokens_periodically())
            
            logger.info("Integration Hub initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Integration Hub initialization failed: {e}")
            return False
    
    async def initiate_platform_integration(
        self,
        user_id: int,
        platform_id: str,
        integration_config: Dict[str, Any],
        session: AsyncSession
    ) -> IntegrationResult:
        """        Initiate integration with a platform
        
        Args:
            user_id: User ID
            platform_id: Platform identifier
            integration_config: Integration configuration
            session: Database session
            
        Returns:
            IntegrationResult with integration status
        """        try:
            platform_info = self.platform_configs.get(platform_id)
            if not platform_info:
                raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform_id}")
            
            logger.info(f"Initiating {platform_id} integration for user {user_id}")
            
            # Check if integration already exists
            existing_integration = await self._get_existing_integration(
                user_id, platform_id, session
            )
            
            if existing_integration and existing_integration.status == IntegrationStatus.ACTIVE:
                return IntegrationResult(
                    success=True,
                    platform_id=platform_id,
                    integration_id=existing_integration.integration_id,
                    error_message="Integration already exists and is active"
                )
            
            # Handle different integration types
            if platform_info.integration_type == IntegrationType.OAUTH2:
                result = await self._initiate_oauth_integration(
                    user_id, platform_info, integration_config
                )
            elif platform_info.integration_type == IntegrationType.API_KEY:
                result = await self._initiate_api_key_integration(
                    user_id, platform_info, integration_config
                )
            elif platform_info.integration_type == IntegrationType.WEBHOOK:
                result = await self._initiate_webhook_integration(
                    user_id, platform_info, integration_config
                )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported integration type: {platform_info.integration_type.value}"
                )
            
            # Store integration in database
            if result.success:
                await self._store_integration(user_id, platform_id, result, session)
            
            logger.info(f"Integration initiated: {platform_id} - Success: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Platform integration failed: {e}")
            return IntegrationResult(
                success=False,
                platform_id=platform_id,
                error_message=str(e)
            )
    
    async def complete_oauth_integration(
        self,
        user_id: int,
        platform_id: str,
        authorization_code: str,
        state: Optional[str] = None,
        session: AsyncSession = None
    ) -> IntegrationResult:
        """        Complete OAuth2 integration flow
        
        Args:
            user_id: User ID
            platform_id: Platform identifier
            authorization_code: OAuth authorization code
            state: OAuth state parameter
            session: Database session
            
        Returns:
            IntegrationResult with final integration status
        """        try:
            platform_info = self.platform_configs.get(platform_id)
            if not platform_info:
                raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform_id}")
            
            # Exchange authorization code for access token
            token_result = await self.oauth_manager.exchange_code_for_token(
                platform_id=platform_id,
                authorization_code=authorization_code,
                user_id=user_id
            )
            
            if not token_result.get('success'):
                return IntegrationResult(
                    success=False,
                    platform_id=platform_id,
                    error_message=token_result.get('error', 'Token exchange failed')
                )
            
            # Verify token and get user info
            user_info = await self._verify_platform_token(
                platform_id, token_result['access_token']
            )
            
            # Create integration result
            result = IntegrationResult(
                success=True,
                platform_id=platform_id,
                access_token=token_result['access_token'],
                refresh_token=token_result.get('refresh_token'),
                expires_at=datetime.utcnow() + timedelta(seconds=token_result.get('expires_in', 3600)),
                metadata={
                    'user_info': user_info,
                    'scope': token_result.get('scope', []),
                    'token_type': token_result.get('token_type', 'Bearer')
                }
            )
            
            # Update integration in database
            await self._update_integration_status(user_id, platform_id, result, session)
            
            # Setup webhook if supported
            if platform_info.webhook_support:
                await self._setup_platform_webhook(user_id, platform_id, result.access_token)
            
            logger.info(f"OAuth integration completed: {platform_id}")
            return result
            
        except Exception as e:
            logger.error(f"OAuth integration completion failed: {e}")
            return IntegrationResult(
                success=False,
                platform_id=platform_id,
                error_message=str(e)
            )
    
    async def revoke_platform_integration(
        self,
        user_id: int,
        platform_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """        Revoke platform integration
        
        Args:
            user_id: User ID
            platform_id: Platform identifier
            session: Database session
            
        Returns:
            Dict containing revocation status
        """        try:
            # Get existing integration
            integration = await self._get_existing_integration(user_id, platform_id, session)
            
            if not integration:
                raise HTTPException(status_code=404, detail="Integration not found")
            
            # Revoke tokens on platform
            if integration.access_token:
                await self._revoke_platform_tokens(platform_id, integration.access_token)
            
            # Remove webhook if exists
            if integration.webhook_url:
                await self._remove_platform_webhook(platform_id, integration.webhook_url)
            
            # Update integration status
            integration.status = IntegrationStatus.REVOKED
            integration.access_token = None
            integration.refresh_token = None
            integration.revoked_at = datetime.utcnow()
            
            await session.commit()
            
            # Remove from active integrations cache
            cache_key = f"{user_id}_{platform_id}"
            if cache_key in self.active_integrations:
                del self.active_integrations[cache_key]
            
            logger.info(f"Integration revoked: {platform_id} for user {user_id}")
            
            return {
                'success': True,
                'platform_id': platform_id,
                'message': 'Integration revoked successfully',
                'revoked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Integration revocation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Revocation failed: {str(e)}")
    
    async def get_integration_status(
        self,
        user_id: int,
        platform_id: Optional[str] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """        Get integration status for user
        
        Args:
            user_id: User ID
            platform_id: Specific platform (None for all)
            session: Database session
            
        Returns:
            Dict containing integration status information
        """        try:
            if platform_id:
                # Get specific platform integration
                integration = await self._get_existing_integration(user_id, platform_id, session)
                
                if not integration:
                    return {
                        'platform_id': platform_id,
                        'status': 'not_connected',
                        'connected_at': None,
                        'last_sync': None
                    }
                
                return {
                    'platform_id': platform_id,
                    'status': integration.status.value,
                    'connected_at': integration.created_at.isoformat(),
                    'last_sync': integration.last_sync.isoformat() if integration.last_sync else None,
                    'features_enabled': integration.features_enabled or [],
                    'webhook_active': bool(integration.webhook_url)
                }
            
            else:
                # Get all platform integrations
                result = await session.execute(
                    select(PlatformIntegration).where(PlatformIntegration.user_id == user_id)
                )
                integrations = result.scalars().all()
                
                status_data = {}
                for integration in integrations:
                    status_data[integration.platform_id] = {
                        'status': integration.status.value,
                        'connected_at': integration.created_at.isoformat(),
                        'last_sync': integration.last_sync.isoformat() if integration.last_sync else None,
                        'features_enabled': integration.features_enabled or [],
                        'webhook_active': bool(integration.webhook_url)
                    }
                
                return {
                    'user_id': user_id,
                    'integrations': status_data,
                    'total_connected': len([i for i in integrations if i.status == IntegrationStatus.ACTIVE])
                }
                
        except Exception as e:
            logger.error(f"Failed to get integration status: {e}")
            raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
    
    async def refresh_platform_token(
        self,
        user_id: int,
        platform_id: str,
        session: AsyncSession
    ) -> IntegrationResult:
        """        Refresh platform access token
        
        Args:
            user_id: User ID
            platform_id: Platform identifier
            session: Database session
            
        Returns:
            IntegrationResult with updated token information
        """        try:
            # Get existing integration
            integration = await self._get_existing_integration(user_id, platform_id, session)
            
            if not integration or not integration.refresh_token:
                raise HTTPException(
                    status_code=404, 
                    detail="Integration or refresh token not found"
                )
            
            # Refresh token using OAuth manager
            refresh_result = await self.oauth_manager.refresh_access_token(
                platform_id=platform_id,
                refresh_token=integration.refresh_token,
                user_id=user_id
            )
            
            if not refresh_result.get('success'):
                return IntegrationResult(
                    success=False,
                    platform_id=platform_id,
                    error_message=refresh_result.get('error', 'Token refresh failed')
                )
            
            # Update integration with new tokens
            integration.access_token = encrypt_sensitive_data(refresh_result['access_token'])
            if refresh_result.get('refresh_token'):
                integration.refresh_token = encrypt_sensitive_data(refresh_result['refresh_token'])
            integration.expires_at = datetime.utcnow() + timedelta(
                seconds=refresh_result.get('expires_in', 3600)
            )
            integration.last_token_refresh = datetime.utcnow()
            
            await session.commit()
            
            logger.info(f"Token refreshed for {platform_id} - user {user_id}")
            
            return IntegrationResult(
                success=True,
                platform_id=platform_id,
                access_token=refresh_result['access_token'],
                refresh_token=refresh_result.get('refresh_token'),
                expires_at=integration.expires_at
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return IntegrationResult(
                success=False,
                platform_id=platform_id,
                error_message=str(e)
            )
    
    async def sync_platform_data(
        self,
        user_id: int,
        platform_id: str,
        data_types: List[str],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """        Synchronize data from platform
        
        Args:
            user_id: User ID
            platform_id: Platform identifier
            data_types: Types of data to sync (profile, content, analytics, etc.)
            session: Database session
            
        Returns:
            Dict containing sync results
        """        try:
            # Get active integration
            integration = await self._get_active_integration(user_id, platform_id, session)
            
            if not integration:
                raise HTTPException(status_code=404, detail="Active integration not found")
            
            # Check if token is still valid
            if integration.expires_at and integration.expires_at < datetime.utcnow():
                # Try to refresh token
                refresh_result = await self.refresh_platform_token(user_id, platform_id, session)
                if not refresh_result.success:
                    raise HTTPException(status_code=401, detail="Token expired and refresh failed")
            
            # Perform data synchronization
            sync_results = {}
            
            for data_type in data_types:
                try:
                    sync_result = await self._sync_data_type(
                        integration, data_type, platform_id
                    )
                    sync_results[data_type] = sync_result
                except Exception as e:
                    logger.error(f"Failed to sync {data_type} from {platform_id}: {e}")
                    sync_results[data_type] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Update last sync time
            integration.last_sync = datetime.utcnow()
            await session.commit()
            
            return {
                'user_id': user_id,
                'platform_id': platform_id,
                'sync_results': sync_results,
                'synced_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data synchronization failed: {e}")
            raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
    
    def _initialize_platform_configs(self) -> Dict[str, PlatformInfo]:
        """Initialize platform configurations"""        return {
            'youtube': PlatformInfo(
                platform_id='youtube',
                name='YouTube',
                category=PlatformCategory.VIDEO_PLATFORM,
                integration_type=IntegrationType.OAUTH2,
                api_version='v3',
                base_url='https://www.googleapis.com/youtube/v3',
                oauth_config={
                    'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                    'token_url': 'https://oauth2.googleapis.com/token',
                    'scope': 'https://www.googleapis.com/auth/youtube.upload'
                },
                features=['upload', 'analytics', 'live_streaming'],
                webhook_support=True
            ),
            'instagram': PlatformInfo(
                platform_id='instagram',
                name='Instagram',
                category=PlatformCategory.SOCIAL_MEDIA,
                integration_type=IntegrationType.OAUTH2,
                api_version='v18.0',
                base_url='https://graph.facebook.com/v18.0',
                oauth_config={
                    'auth_url': 'https://api.instagram.com/oauth/authorize',
                    'token_url': 'https://api.instagram.com/oauth/access_token',
                    'scope': 'user_profile,user_media'
                },
                features=['upload', 'stories', 'analytics'],
                webhook_support=True
            ),
            'tiktok': PlatformInfo(
                platform_id='tiktok',
                name='TikTok',
                category=PlatformCategory.SOCIAL_MEDIA,
                integration_type=IntegrationType.OAUTH2,
                api_version='v1',
                base_url='https://open-api.tiktok.com',
                oauth_config={
                    'auth_url': 'https://www.tiktok.com/auth/authorize',
                    'token_url': 'https://open-api.tiktok.com/oauth/access_token',
                    'scope': 'user.info.basic,video.upload'
                },
                features=['upload', 'analytics'],
                webhook_support=False
            ),
            'spotify': PlatformInfo(
                platform_id='spotify',
                name='Spotify',
                category=PlatformCategory.MUSIC_STREAMING,
                integration_type=IntegrationType.OAUTH2,
                api_version='v1',
                base_url='https://api.spotify.com/v1',
                oauth_config={
                    'auth_url': 'https://accounts.spotify.com/authorize',
                    'token_url': 'https://accounts.spotify.com/api/token',
                    'scope': 'user-read-private user-read-email playlist-modify-public'
                },
                features=['playlist_management', 'analytics', 'artist_profile'],
                webhook_support=True
            )
        }
    
    async def _initialize_http_clients(self):
        """Initialize HTTP clients for different platforms"""        for platform_id, config in self.platform_configs.items():
            self.http_clients[platform_id] = httpx.AsyncClient(
                base_url=config.base_url,
                timeout=30.0,
                headers={'User-Agent': f'IA-Influencer-Agent/{settings.VERSION}'}
            )
    
    async def _initiate_oauth_integration(
        self,
        user_id: int,
        platform_info: PlatformInfo,
        config: Dict[str, Any]
    ) -> IntegrationResult:
        """Initiate OAuth2 integration"""        oauth_url = await self.oauth_manager.generate_oauth_url(
            platform_id=platform_info.platform_id,
            user_id=user_id,
            scopes=config.get('scopes', platform_info.oauth_config.get('scope', '').split(' '))
        )
        
        return IntegrationResult(
            success=True,
            platform_id=platform_info.platform_id,
            metadata={
                'oauth_url': oauth_url,
                'integration_type': 'oauth2',
                'next_step': 'redirect_user_to_oauth_url'
            }
        )
    
    async def _initiate_api_key_integration(
        self,
        user_id: int,
        platform_info: PlatformInfo,
        config: Dict[str, Any]
    ) -> IntegrationResult:
        """Initiate API key integration"""        api_key = config.get('api_key')
        if not api_key:
            return IntegrationResult(
                success=False,
                platform_id=platform_info.platform_id,
                error_message='API key is required'
            )
        
        # Verify API key
        is_valid = await self._verify_api_key(platform_info.platform_id, api_key)
        
        if not is_valid:
            return IntegrationResult(
                success=False,
                platform_id=platform_info.platform_id,
                error_message='Invalid API key'
            )
        
        return IntegrationResult(
            success=True,
            platform_id=platform_info.platform_id,
            access_token=api_key,
            metadata={'integration_type': 'api_key'}
        )
    
    async def _initiate_webhook_integration(
        self,
        user_id: int,
        platform_info: PlatformInfo,
        config: Dict[str, Any]
    ) -> IntegrationResult:
        """Initiate webhook integration"""        webhook_url = config.get('webhook_url')
        if not webhook_url:
            return IntegrationResult(
                success=False,
                platform_id=platform_info.platform_id,
                error_message='Webhook URL is required'
            )
        
        # Setup webhook endpoint
        webhook_result = await self.webhook_handler.setup_webhook(
            platform_id=platform_info.platform_id,
            user_id=user_id,
            webhook_url=webhook_url
        )
        
        return IntegrationResult(
            success=webhook_result.get('success', False),
            platform_id=platform_info.platform_id,
            error_message=webhook_result.get('error'),
            metadata={
                'webhook_id': webhook_result.get('webhook_id'),
                'integration_type': 'webhook'
            }
        )
    
    async def _get_existing_integration(
        self, 
        user_id: int, 
        platform_id: str, 
        session: AsyncSession
    ) -> Optional[PlatformIntegration]:
        """Get existing integration from database"""        result = await session.execute(
            select(PlatformIntegration).where(
                and_(
                    PlatformIntegration.user_id == user_id,
                    PlatformIntegration.platform_id == platform_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def _get_active_integration(
        self, 
        user_id: int, 
        platform_id: str, 
        session: AsyncSession
    ) -> Optional[PlatformIntegration]:
        """Get active integration from database"""        result = await session.execute(
            select(PlatformIntegration).where(
                and_(
                    PlatformIntegration.user_id == user_id,
                    PlatformIntegration.platform_id == platform_id,
                    PlatformIntegration.status == IntegrationStatus.ACTIVE
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def _store_integration(
        self,
        user_id: int,
        platform_id: str,
        result: IntegrationResult,
        session: AsyncSession
    ):
        """Store integration in database"""        integration = PlatformIntegration(
            user_id=user_id,
            platform_id=platform_id,
            integration_type=self.platform_configs[platform_id].integration_type.value,
            status=IntegrationStatus.PENDING,
            access_token=encrypt_sensitive_data(result.access_token) if result.access_token else None,
            refresh_token=encrypt_sensitive_data(result.refresh_token) if result.refresh_token else None,
            expires_at=result.expires_at,
            metadata=json.dumps(result.metadata),
            created_at=datetime.utcnow()
        )
        
        session.add(integration)
        await session.commit()
        await session.refresh(integration)
    
    async def _monitor_integrations(self):
        """Monitor integration health"""        while True:
            try:
                logger.info("Running integration health check")
                # Implementation for integration monitoring
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Integration monitoring error: {e}")
                await asyncio.sleep(3600)
    
    async def _refresh_tokens_periodically(self):
        """Periodically refresh expiring tokens"""        while True:
            try:
                # Implementation for automatic token refresh
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Token refresh error: {e}")
                await asyncio.sleep(1800)
