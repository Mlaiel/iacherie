"""Social Login Authentication Template for iacherie Platform
Comprehensive social login integration supporting OAuth 2.0, OpenID Connect,
and major social platforms for creator authentication and audience growth.

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle protégée
"""

import logging
import secrets
import hashlib
import base64
import json
import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlencode, parse_qs
import aiohttp
from pydantic import BaseModel, Field, validator, HttpUrl
import jwt

from core.config import get_settings
from utils.exceptions import SocialAuthException, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class SocialProvider(Enum):
    """Supported social login providers"""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    APPLE = "apple"
    MICROSOFT = "microsoft"
    DISCORD = "discord"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    TWITCH = "twitch"


class GrantType(Enum):
    """OAuth 2.0 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"


class ScopeType(Enum):
    """OAuth 2.0 scope types"""
    PROFILE = "profile"
    EMAIL = "email"
    OPENID = "openid"
    READ_USER = "read:user"
    READ_FOLLOWERS = "read:followers"
    PUBLISH = "publish"
    ANALYTICS = "analytics"


class SocialProviderConfig(BaseModel):
    """Social provider configuration"""
    provider: SocialProvider = Field(..., description="Social provider name")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    authorization_url: str = Field(..., description="Authorization endpoint")
    token_url: str = Field(..., description="Token endpoint")
    userinfo_url: str = Field(..., description="User info endpoint")
    scopes: List[str] = Field(..., description="Required scopes")
    additional_params: Dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = Field(default=True)
    rate_limit: int = Field(default=100, description="Requests per hour")
    timeout_seconds: int = Field(default=30)


class SocialAuthRequest(BaseModel):
    """Social authentication request"""
    provider: SocialProvider = Field(..., description="Social provider")
    code: Optional[str] = Field(default=None, description="Authorization code")
    state: Optional[str] = Field(default=None, description="CSRF state parameter")
    redirect_uri: Optional[str] = Field(default=None, description="Redirect URI")
    scopes: Optional[List[str]] = Field(default=None, description="Requested scopes")
    device_info: Optional[Dict[str, Any]] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    link_existing_account: bool = Field(default=False)
    existing_user_id: Optional[str] = Field(default=None)


class SocialUserProfile(BaseModel):
    """Social user profile data"""
    provider_id: str = Field(..., description="Provider user ID")
    provider: SocialProvider = Field(..., description="Social provider")
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    display_name: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    profile_url: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None)
    timezone: Optional[str] = Field(default=None)
    verified: Optional[bool] = Field(default=None)
    followers_count: Optional[int] = Field(default=None)
    following_count: Optional[int] = Field(default=None)
    posts_count: Optional[int] = Field(default=None)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SocialAuthResponse(BaseModel):
    """Social authentication response"""
    success: bool = Field(..., description="Authentication success")
    provider: SocialProvider = Field(..., description="Social provider")
    user_id: Optional[str] = Field(default=None, description="iacherie user ID")
    social_user_id: Optional[str] = Field(default=None, description="Provider user ID")
    access_token: Optional[str] = Field(default=None, description="iacherie access token")
    refresh_token: Optional[str] = Field(default=None, description="iacherie refresh token")
    social_access_token: Optional[str] = Field(default=None, description="Provider access token")
    social_refresh_token: Optional[str] = Field(default=None, description="Provider refresh token")
    token_expires_in: Optional[int] = Field(default=None, description="Token expiration seconds")
    profile: Optional[SocialUserProfile] = Field(default=None)
    granted_scopes: List[str] = Field(default_factory=list)
    is_new_user: bool = Field(default=False)
    account_linked: bool = Field(default=False)
    error_message: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OAuthToken(BaseModel):
    """OAuth token data"""
    access_token: str = Field(..., description="Access token")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: Optional[int] = Field(default=None, description="Expiration seconds")
    scope: Optional[str] = Field(default=None, description="Granted scopes")
    id_token: Optional[str] = Field(default=None, description="OpenID Connect ID token")
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SocialAccount(BaseModel):
    """Social account link model"""
    account_id: str = Field(..., description="Unique account link ID")
    user_id: str = Field(..., description="iacherie user ID")
    provider: SocialProvider = Field(..., description="Social provider")
    provider_user_id: str = Field(..., description="Provider user ID")
    username: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    display_name: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    access_token: Optional[str] = Field(default=None, description="Encrypted access token")
    refresh_token: Optional[str] = Field(default=None, description="Encrypted refresh token")
    token_expires_at: Optional[datetime] = Field(default=None)
    granted_scopes: List[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    is_primary: bool = Field(default=False, description="Primary auth method")
    last_login: Optional[datetime] = Field(default=None)
    login_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class SocialLoginService:
    """Comprehensive social login authentication service for iacherie platform
    
    Provides enterprise-grade social authentication with:
    - OAuth 2.0 and OpenID Connect support
    - Multiple social provider integration
    - Account linking and unlinking
    - Token refresh and management
    - Creator audience connection features
    - Security and abuse protection
    - Analytics and metrics collection
    """
    
    def __init__(self):
        self.metrics_collector = SecurityMetricsCollector()
        self.session = aiohttp.ClientSession()
        
        # Provider configurations
        self.providers: Dict[SocialProvider, SocialProviderConfig] = {
            SocialProvider.GOOGLE: SocialProviderConfig(
                provider=SocialProvider.GOOGLE,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                redirect_uri=f"{settings.BASE_URL}/auth/google/callback",
                authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token",
                userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
                scopes=["openid", "email", "profile"]
            ),
            SocialProvider.FACEBOOK: SocialProviderConfig(
                provider=SocialProvider.FACEBOOK,
                client_id=settings.FACEBOOK_CLIENT_ID,
                client_secret=settings.FACEBOOK_CLIENT_SECRET,
                redirect_uri=f"{settings.BASE_URL}/auth/facebook/callback",
                authorization_url="https://www.facebook.com/v18.0/dialog/oauth",
                token_url="https://graph.facebook.com/v18.0/oauth/access_token",
                userinfo_url="https://graph.facebook.com/v18.0/me",
                scopes=["email", "public_profile"]
            ),
            SocialProvider.TWITTER: SocialProviderConfig(
                provider=SocialProvider.TWITTER,
                client_id=settings.TWITTER_CLIENT_ID,
                client_secret=settings.TWITTER_CLIENT_SECRET,
                redirect_uri=f"{settings.BASE_URL}/auth/twitter/callback",
                authorization_url="https://twitter.com/i/oauth2/authorize",
                token_url="https://api.twitter.com/2/oauth2/token",
                userinfo_url="https://api.twitter.com/2/users/me",
                scopes=["users.read", "tweet.read"]
            ),
            SocialProvider.LINKEDIN: SocialProviderConfig(
                provider=SocialProvider.LINKEDIN,
                client_id=settings.LINKEDIN_CLIENT_ID,
                client_secret=settings.LINKEDIN_CLIENT_SECRET,
                redirect_uri=f"{settings.BASE_URL}/auth/linkedin/callback",
                authorization_url="https://www.linkedin.com/oauth/v2/authorization",
                token_url="https://www.linkedin.com/oauth/v2/accessToken",
                userinfo_url="https://api.linkedin.com/v2/people/~",
                scopes=["r_liteprofile", "r_emailaddress"]
            ),
            SocialProvider.GITHUB: SocialProviderConfig(
                provider=SocialProvider.GITHUB,
                client_id=settings.GITHUB_CLIENT_ID,
                client_secret=settings.GITHUB_CLIENT_SECRET,
                redirect_uri=f"{settings.BASE_URL}/auth/github/callback",
                authorization_url="https://github.com/login/oauth/authorize",
                token_url="https://github.com/login/oauth/access_token",
                userinfo_url="https://api.github.com/user",
                scopes=["user:email"]
            )
        }
        
        # Social account storage (in production, use secure database)
        self.social_accounts: Dict[str, List[SocialAccount]] = {}
        self.provider_users: Dict[SocialProvider, Dict[str, str]] = {}
        
        logger.info("Social login service initialized")
    
    async def get_authorization_url(self, provider: SocialProvider, state: Optional[str] = None) -> str:
        """Generate OAuth authorization URL"""
        try:
            provider_config = self.providers.get(provider)
            if not provider_config or not provider_config.is_enabled:
                raise SocialAuthException(f"Provider {provider.value} not supported or disabled")
            
            # Generate state parameter for CSRF protection
            if not state:
                state = secrets.token_urlsafe(32)
            
            # Build authorization parameters
            params = {
                "client_id": provider_config.client_id,
                "redirect_uri": provider_config.redirect_uri,
                "scope": " ".join(provider_config.scopes),
                "response_type": "code",
                "state": state,
                **provider_config.additional_params
            }
            
            # Provider-specific parameters
            if provider == SocialProvider.GOOGLE:
                params["access_type"] = "offline"
                params["prompt"] = "consent"
            elif provider == SocialProvider.FACEBOOK:
                params["display"] = "popup"
            elif provider == SocialProvider.TWITTER:
                params["code_challenge"] = self._generate_pkce_challenge()
                params["code_challenge_method"] = "S256"
            
            auth_url = f"{provider_config.authorization_url}?{urlencode(params)}"
            
            logger.info(f"Generated authorization URL for {provider.value}")
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate authorization URL for {provider.value}: {e}")
            raise SocialAuthException(f"Authorization URL generation failed: {e}")
    
    async def exchange_code_for_token(self, provider: SocialProvider, code: str, 
                                     redirect_uri: Optional[str] = None) -> OAuthToken:
        """Exchange authorization code for access token"""
        try:
            provider_config = self.providers.get(provider)
            if not provider_config:
                raise SocialAuthException(f"Provider {provider.value} not configured")
            
            # Prepare token request
            data = {
                "client_id": provider_config.client_id,
                "client_secret": provider_config.client_secret,
                "code": code,
                "grant_type": GrantType.AUTHORIZATION_CODE.value,
                "redirect_uri": redirect_uri or provider_config.redirect_uri
            }
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Make token request
            async with self.session.post(
                provider_config.token_url, 
                data=data, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=provider_config.timeout_seconds)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise SocialAuthException(f"Token exchange failed: {error_text}")
                
                token_data = await response.json()
            
            # Parse token response
            expires_at = None
            if "expires_in" in token_data:
                expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
            
            token = OAuthToken(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_type=token_data.get("token_type", "Bearer"),
                expires_in=token_data.get("expires_in"),
                scope=token_data.get("scope"),
                id_token=token_data.get("id_token"),
                expires_at=expires_at
            )
            
            logger.info(f"Successfully exchanged code for token with {provider.value}")
            return token
            
        except Exception as e:
            logger.error(f"Token exchange failed for {provider.value}: {e}")
            raise SocialAuthException(f"Token exchange failed: {e}")
    
    async def fetch_user_profile(self, provider: SocialProvider, access_token: str) -> SocialUserProfile:
        """Fetch user profile from social provider"""
        try:
            provider_config = self.providers.get(provider)
            if not provider_config:
                raise SocialAuthException(f"Provider {provider.value} not configured")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            # Provider-specific profile requests
            if provider == SocialProvider.FACEBOOK:
                userinfo_url = f"{provider_config.userinfo_url}?fields=id,name,email,first_name,last_name,picture"
            elif provider == SocialProvider.LINKEDIN:
                userinfo_url = f"{provider_config.userinfo_url}:(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"
            else:
                userinfo_url = provider_config.userinfo_url
            
            async with self.session.get(
                userinfo_url, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=provider_config.timeout_seconds)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise SocialAuthException(f"Profile fetch failed: {error_text}")
                
                profile_data = await response.json()
            
            # Parse profile data based on provider
            profile = self._parse_profile_data(provider, profile_data)
            
            logger.info(f"Successfully fetched profile for {provider.value} user {profile.provider_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Profile fetch failed for {provider.value}: {e}")
            raise SocialAuthException(f"Profile fetch failed: {e}")
    
    def _parse_profile_data(self, provider: SocialProvider, data: Dict[str, Any]) -> SocialUserProfile:
        """Parse provider-specific profile data"""
        profile = SocialUserProfile(
            provider=provider,
            provider_id=str(data.get("id", "")),
            raw_data=data
        )
        
        if provider == SocialProvider.GOOGLE:
            profile.email = data.get("email")
            profile.display_name = data.get("name")
            profile.first_name = data.get("given_name")
            profile.last_name = data.get("family_name")
            profile.avatar_url = data.get("picture")
            profile.locale = data.get("locale")
            profile.verified = data.get("email_verified", False)
            
        elif provider == SocialProvider.FACEBOOK:
            profile.email = data.get("email")
            profile.display_name = data.get("name")
            profile.first_name = data.get("first_name")
            profile.last_name = data.get("last_name")
            if "picture" in data and "data" in data["picture"]:
                profile.avatar_url = data["picture"]["data"].get("url")
                
        elif provider == SocialProvider.TWITTER:
            profile.username = data.get("username")
            profile.display_name = data.get("name")
            profile.avatar_url = data.get("profile_image_url")
            profile.verified = data.get("verified", False)
            if "public_metrics" in data:
                metrics = data["public_metrics"]
                profile.followers_count = metrics.get("followers_count")
                profile.following_count = metrics.get("following_count")
                profile.posts_count = metrics.get("tweet_count")
                
        elif provider == SocialProvider.LINKEDIN:
            if "firstName" in data:
                profile.first_name = data["firstName"].get("localized", {}).get("en_US")
            if "lastName" in data:
                profile.last_name = data["lastName"].get("localized", {}).get("en_US")
            profile.display_name = f"{profile.first_name or ''} {profile.last_name or ''}".strip()
            
        elif provider == SocialProvider.GITHUB:
            profile.username = data.get("login")
            profile.display_name = data.get("name")
            profile.email = data.get("email")
            profile.avatar_url = data.get("avatar_url")
            profile.profile_url = data.get("html_url")
            profile.followers_count = data.get("followers")
            profile.following_count = data.get("following")
            profile.posts_count = data.get("public_repos")
        
        return profile
    
    async def authenticate_user(self, request: SocialAuthRequest) -> SocialAuthResponse:
        """Complete social authentication flow"""
        start_time = datetime.utcnow()
        
        try:
            if not request.code:
                raise SocialAuthException("Authorization code is required")
            
            provider_config = self.providers.get(request.provider)
            if not provider_config or not provider_config.is_enabled:
                raise SocialAuthException(f"Provider {request.provider.value} not available")
            
            # Exchange code for token
            token = await self.exchange_code_for_token(
                request.provider, 
                request.code, 
                request.redirect_uri
            )
            
            # Fetch user profile
            profile = await self.fetch_user_profile(request.provider, token.access_token)
            
            # Find or create user account
            user_id = await self._find_or_create_user(profile, request)
            
            # Link social account
            social_account = await self._link_social_account(
                user_id, 
                profile, 
                token, 
                request
            )
            
            # Generate iacherie access token
            iacherie_token = await self._generate_iacherie_token(user_id, social_account)
            
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Record metrics
            await self.metrics_collector.record_social_auth(
                provider=request.provider.value,
                success=True,
                processing_time_ms=processing_time,
                user_id=user_id
            )
            
            return SocialAuthResponse(
                success=True,
                provider=request.provider,
                user_id=user_id,
                social_user_id=profile.provider_id,
                access_token=iacherie_token["access_token"],
                refresh_token=iacherie_token["refresh_token"],
                social_access_token=token.access_token,
                social_refresh_token=token.refresh_token,
                token_expires_in=token.expires_in,
                profile=profile,
                granted_scopes=token.scope.split(" ") if token.scope else [],
                is_new_user=social_account.login_count == 1,
                account_linked=True,
                metadata={
                    "processing_time_ms": processing_time,
                    "provider_config": provider_config.provider.value
                }
            )
            
        except Exception as e:
            logger.error(f"Social authentication failed for {request.provider.value}: {e}")
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            await self.metrics_collector.record_social_auth(
                provider=request.provider.value,
                success=False,
                processing_time_ms=processing_time,
                error=str(e)
            )
            
            return SocialAuthResponse(
                success=False,
                provider=request.provider,
                error_message=str(e),
                metadata={"processing_time_ms": processing_time}
            )
    
    async def _find_or_create_user(self, profile: SocialUserProfile, 
                                  request: SocialAuthRequest) -> str:
        """Find existing user or create new one"""
        # Check if social account already exists
        if request.provider not in self.provider_users:
            self.provider_users[request.provider] = {}
        
        provider_users = self.provider_users[request.provider]
        
        if profile.provider_id in provider_users:
            return provider_users[profile.provider_id]
        
        # Check if linking to existing account
        if request.link_existing_account and request.existing_user_id:
            user_id = request.existing_user_id
        else:
            # Create new user
            user_id = f"user_{secrets.token_urlsafe(16)}"
        
        # Register mapping
        provider_users[profile.provider_id] = user_id
        
        return user_id
    
    async def _link_social_account(self, user_id: str, profile: SocialUserProfile,
                                  token: OAuthToken, request: SocialAuthRequest) -> SocialAccount:
        """Link social account to user"""
        account_id = f"social_{secrets.token_urlsafe(16)}"
        
        # Encrypt tokens (simplified - use proper encryption in production)
        encrypted_access_token = base64.b64encode(token.access_token.encode()).decode()
        encrypted_refresh_token = None
        if token.refresh_token:
            encrypted_refresh_token = base64.b64encode(token.refresh_token.encode()).decode()
        
        social_account = SocialAccount(
            account_id=account_id,
            user_id=user_id,
            provider=request.provider,
            provider_user_id=profile.provider_id,
            username=profile.username,
            email=profile.email,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            access_token=encrypted_access_token,
            refresh_token=encrypted_refresh_token,
            token_expires_at=token.expires_at,
            granted_scopes=token.scope.split(" ") if token.scope else [],
            last_login=datetime.utcnow(),
            login_count=1
        )
        
        # Store social account
        if user_id not in self.social_accounts:
            self.social_accounts[user_id] = []
        
        # Check if account already exists
        existing_account = None
        for account in self.social_accounts[user_id]:
            if (account.provider == request.provider and 
                account.provider_user_id == profile.provider_id):
                existing_account = account
                break
        
        if existing_account:
            # Update existing account
            existing_account.access_token = encrypted_access_token
            existing_account.refresh_token = encrypted_refresh_token
            existing_account.token_expires_at = token.expires_at
            existing_account.last_login = datetime.utcnow()
            existing_account.login_count += 1
            existing_account.updated_at = datetime.utcnow()
            return existing_account
        else:
            # Add new account
            self.social_accounts[user_id].append(social_account)
            return social_account
    
    async def _generate_iacherie_token(self, user_id: str, social_account: SocialAccount) -> Dict[str, str]:
        """Generate iacherie platform tokens"""
        # JWT payload
        payload = {
            "user_id": user_id,
            "social_provider": social_account.provider.value,
            "social_account_id": social_account.account_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        # Generate tokens (simplified - use proper JWT in production)
        access_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        refresh_payload = payload.copy()
        refresh_payload["exp"] = datetime.utcnow() + timedelta(days=30)
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def _generate_pkce_challenge(self) -> str:
        """Generate PKCE code challenge for OAuth 2.1"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        return code_challenge
    
    async def refresh_social_token(self, user_id: str, provider: SocialProvider) -> Optional[OAuthToken]:
        """Refresh social provider access token"""
        try:
            user_accounts = self.social_accounts.get(user_id, [])
            social_account = None
            
            for account in user_accounts:
                if account.provider == provider and account.is_active:
                    social_account = account
                    break
            
            if not social_account or not social_account.refresh_token:
                return None
            
            provider_config = self.providers.get(provider)
            if not provider_config:
                return None
            
            # Decrypt refresh token
            refresh_token = base64.b64decode(social_account.refresh_token).decode()
            
            # Refresh token request
            data = {
                "client_id": provider_config.client_id,
                "client_secret": provider_config.client_secret,
                "refresh_token": refresh_token,
                "grant_type": GrantType.REFRESH_TOKEN.value
            }
            
            async with self.session.post(provider_config.token_url, data=data) as response:
                if response.status != 200:
                    logger.error(f"Token refresh failed for {provider.value}")
                    return None
                
                token_data = await response.json()
            
            # Update stored tokens
            new_access_token = base64.b64encode(token_data["access_token"].encode()).decode()
            social_account.access_token = new_access_token
            
            if "refresh_token" in token_data:
                new_refresh_token = base64.b64encode(token_data["refresh_token"].encode()).decode()
                social_account.refresh_token = new_refresh_token
            
            if "expires_in" in token_data:
                social_account.token_expires_at = datetime.utcnow() + timedelta(
                    seconds=token_data["expires_in"]
                )
            
            social_account.updated_at = datetime.utcnow()
            
            return OAuthToken(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_in=token_data.get("expires_in")
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    async def unlink_social_account(self, user_id: str, provider: SocialProvider) -> bool:
        """Unlink social account from user"""
        try:
            user_accounts = self.social_accounts.get(user_id, [])
            
            for i, account in enumerate(user_accounts):
                if account.provider == provider:
                    del user_accounts[i]
                    
                    # Remove from provider mapping
                    if provider in self.provider_users:
                        provider_users = self.provider_users[provider]
                        if account.provider_user_id in provider_users:
                            del provider_users[account.provider_user_id]
                    
                    logger.info(f"Unlinked {provider.value} account for user {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unlink social account: {e}")
            return False
    
    async def get_user_social_accounts(self, user_id: str) -> List[SocialAccount]:
        """Get all social accounts for a user"""
        return self.social_accounts.get(user_id, [])
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()


# Export service instance
social_login_service = SocialLoginService()

__all__ = [
    'SocialProvider',
    'GrantType',
    'ScopeType',
    'SocialProviderConfig',
    'SocialAuthRequest',
    'SocialUserProfile',
    'SocialAuthResponse',
    'OAuthToken',
    'SocialAccount',
    'SocialLoginService',
    'social_login_service'
]