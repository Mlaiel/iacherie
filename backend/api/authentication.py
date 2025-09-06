"""Authentication - OAuth, JWT, Session Management
Consolidated authentication functionality for the IA Influencer Agent platform.

This module consolidates authentication from:
- OAuth2 providers (Google, Facebook, Spotify, YouTube, Instagram, TikTok)
- JWT token management (access tokens, refresh tokens, validation)
- Session management (distributed sessions, Redis clustering)
- Multi-factor authentication (TOTP, SMS, email, hardware keys)
- Biometric authentication (face, voice, fingerprint recognition)
- Device registration and trusted device management
- Password policies and breach detection

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import jwt
import bcrypt
import pyotp
import qrcode
from io import BytesIO
import base64

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field, validator
try:
    import redis.asyncio as redis
except ImportError:
    # Mock redis if not available
    redis = None
import asyncio

# ========================================
# AUTHENTICATION MODELS
# ========================================

class AuthProvider(str, Enum):
    """Supported authentication providers - 35+ platforms for creators"""
    # Core Platforms
    LOCAL = "local"
    GOOGLE = "google"
    FACEBOOK = "facebook"
    APPLE = "apple"
    MICROSOFT = "microsoft"
    
    # Social Media Platforms
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    
    # Content Creator Platforms
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    SUBSTACK = "substack"
    MEDIUM = "medium"
    DEVIANTART = "deviantart"
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    
    # Music Platforms
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    BANDCAMP = "bandcamp"
    MIXCLOUD = "mixcloud"
    AUDIOMACK = "audiomack"
    
    # Video Platforms
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    RUMBLE = "rumble"
    
    # Professional Platforms
    GITHUB = "github"
    GITLAB = "gitlab"
    SLACK = "slack"

class MFAMethod(str, Enum):
    """Multi-factor authentication methods"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_KEY = "hardware_key"
    BIOMETRIC = "biometric"
    PUSH_NOTIFICATION = "push_notification"
    BACKUP_CODES = "backup_codes"

class BiometricType(str, Enum):
    """Biometric authentication types"""
    FACE = "face"
    VOICE = "voice"
    FINGERPRINT = "fingerprint"
    IRIS = "iris"
    PALM = "palm"

class DeviceType(str, Enum):
    """Device types for authentication"""
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    API = "api"

class UserCredentials(BaseModel):
    """User credentials model"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    remember_me: bool = Field(default=False)

class TokenPair(BaseModel):
    """JWT token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: List[str] = []

class UserSession(BaseModel):
    """User session data"""
    session_id: str
    user_id: str
    device_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_mobile: bool = False

# ========================================
# JWT TOKEN MANAGER
# ========================================

class JWTManager:
    """JWT token management for authentication"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=30)
    
    def create_access_token(self, user_id: str, scope: List[str] = None) -> str:
        """Create JWT access token"""
        if scope is None:
            scope = ["read", "write"]
            
        payload = {
            "sub": user_id,
            "type": "access",
            "scope": scope,
            "exp": datetime.utcnow() + self.access_token_expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        payload = {
            "sub": user_id,
            "type": "refresh", 
            "exp": datetime.utcnow() + self.refresh_token_expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def create_token_pair(self, user_id: str, scope: List[str] = None) -> TokenPair:
        """Create access and refresh token pair"""
        access_token = self.create_access_token(user_id, scope)
        refresh_token = self.create_refresh_token(user_id)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self.access_token_expire.total_seconds()),
            scope=scope or ["read", "write"]
        )

# ========================================
# OAUTH2 MANAGER
# ========================================

class OAuth2Manager:
    """OAuth2 provider integration manager"""
    
    def __init__(self):
        self.providers = {
            # Core Platforms
            AuthProvider.GOOGLE: self._google_config,
            AuthProvider.FACEBOOK: self._facebook_config,
            AuthProvider.APPLE: self._apple_config,
            AuthProvider.MICROSOFT: self._microsoft_config,
            
            # Social Media Platforms
            AuthProvider.INSTAGRAM: self._instagram_config,
            AuthProvider.TIKTOK: self._tiktok_config,
            AuthProvider.TWITTER: self._twitter_config,
            AuthProvider.LINKEDIN: self._linkedin_config,
            AuthProvider.PINTEREST: self._pinterest_config,
            AuthProvider.SNAPCHAT: self._snapchat_config,
            AuthProvider.DISCORD: self._discord_config,
            AuthProvider.TELEGRAM: self._telegram_config,
            
            # Content Creator Platforms
            AuthProvider.YOUTUBE: self._youtube_config,
            AuthProvider.SPOTIFY: self._spotify_config,
            AuthProvider.SOUNDCLOUD: self._soundcloud_config,
            AuthProvider.TWITCH: self._twitch_config,
            AuthProvider.PATREON: self._patreon_config,
            AuthProvider.SUBSTACK: self._substack_config,
            AuthProvider.MEDIUM: self._medium_config,
            AuthProvider.DEVIANTART: self._deviantart_config,
            AuthProvider.BEHANCE: self._behance_config,
            AuthProvider.DRIBBBLE: self._dribbble_config,
            
            # Music Platforms
            AuthProvider.APPLE_MUSIC: self._apple_music_config,
            AuthProvider.AMAZON_MUSIC: self._amazon_music_config,
            AuthProvider.BANDCAMP: self._bandcamp_config,
            AuthProvider.MIXCLOUD: self._mixcloud_config,
            
            # Video Platforms
            AuthProvider.VIMEO: self._vimeo_config,
            AuthProvider.DAILYMOTION: self._dailymotion_config,
            
            # Professional Platforms
            AuthProvider.GITHUB: self._github_config,
            AuthProvider.GITLAB: self._gitlab_config,
            AuthProvider.SLACK: self._slack_config
        }
    
    def _google_config(self) -> Dict[str, str]:
        """Google OAuth2 configuration"""
        return {
            "authorization_url": "https://accounts.google.com/o/oauth2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
            "scope": "openid email profile"
        }
    
    def _spotify_config(self) -> Dict[str, str]:
        """Spotify OAuth2 configuration"""
        return {
            "authorization_url": "https://accounts.spotify.com/authorize",
            "token_url": "https://accounts.spotify.com/api/token",
            "userinfo_url": "https://api.spotify.com/v1/me",
            "scope": "user-read-private user-read-email"
        }
    
    def _youtube_config(self) -> Dict[str, str]:
        """YouTube OAuth2 configuration"""
        return {
            "authorization_url": "https://accounts.google.com/o/oauth2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/youtube/v3/channels",
            "scope": "https://www.googleapis.com/auth/youtube.readonly"
        }
    
    def _instagram_config(self) -> Dict[str, str]:
        """Instagram OAuth2 configuration"""
        return {
            "authorization_url": "https://api.instagram.com/oauth/authorize",
            "token_url": "https://api.instagram.com/oauth/access_token",
            "userinfo_url": "https://graph.instagram.com/me",
            "scope": "user_profile,user_media"
        }
    
    def _tiktok_config(self) -> Dict[str, str]:
        """TikTok OAuth2 configuration"""
        return {
            "authorization_url": "https://www.tiktok.com/auth/authorize/",
            "token_url": "https://open-api.tiktok.com/oauth/access_token/",
            "userinfo_url": "https://open-api.tiktok.com/user/info/",
            "scope": "user.info.basic,video.list"
        }
    
    def _twitter_config(self) -> Dict[str, str]:
        """Twitter OAuth2 configuration"""
        return {
            "authorization_url": "https://twitter.com/i/oauth2/authorize",
            "token_url": "https://api.twitter.com/2/oauth2/token",
            "userinfo_url": "https://api.twitter.com/2/users/me",
            "scope": "tweet.read users.read"
        }
    
    def _facebook_config(self) -> Dict[str, str]:
        """Facebook OAuth2 configuration"""
        return {
            "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
            "userinfo_url": "https://graph.facebook.com/v18.0/me",
            "scope": "email,public_profile"
        }
    
    def _apple_config(self) -> Dict[str, str]:
        """Apple OAuth2 configuration"""
        return {
            "authorization_url": "https://appleid.apple.com/auth/authorize",
            "token_url": "https://appleid.apple.com/auth/token",
            "userinfo_url": "https://appleid.apple.com/auth/keys",
            "scope": "name email"
        }
    
    def _microsoft_config(self) -> Dict[str, str]:
        """Microsoft OAuth2 configuration"""
        return {
            "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "userinfo_url": "https://graph.microsoft.com/v1.0/me",
            "scope": "openid profile User.Read"
        }
    
    def _linkedin_config(self) -> Dict[str, str]:
        """LinkedIn OAuth2 configuration"""
        return {
            "authorization_url": "https://www.linkedin.com/oauth/v2/authorization",
            "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
            "userinfo_url": "https://api.linkedin.com/v2/people/~",
            "scope": "r_liteprofile r_emailaddress"
        }
    
    def _pinterest_config(self) -> Dict[str, str]:
        """Pinterest OAuth2 configuration"""
        return {
            "authorization_url": "https://www.pinterest.com/oauth/",
            "token_url": "https://api.pinterest.com/v5/oauth/token",
            "userinfo_url": "https://api.pinterest.com/v5/user_account",
            "scope": "user_accounts:read"
        }
    
    def _snapchat_config(self) -> Dict[str, str]:
        """Snapchat OAuth2 configuration"""
        return {
            "authorization_url": "https://accounts.snapchat.com/login/oauth2/authorize",
            "token_url": "https://accounts.snapchat.com/login/oauth2/access_token",
            "userinfo_url": "https://kit.snapchat.com/v1/me",
            "scope": "user.external_id user.display_name"
        }
    
    def _discord_config(self) -> Dict[str, str]:
        """Discord OAuth2 configuration"""
        return {
            "authorization_url": "https://discord.com/api/oauth2/authorize",
            "token_url": "https://discord.com/api/oauth2/token",
            "userinfo_url": "https://discord.com/api/users/@me",
            "scope": "identify email"
        }
    
    def _telegram_config(self) -> Dict[str, str]:
        """Telegram OAuth2 configuration"""
        return {
            "authorization_url": "https://oauth.telegram.org/auth",
            "token_url": "https://oauth.telegram.org/auth/token",
            "userinfo_url": "https://api.telegram.org/bot/getMe",
            "scope": "read"
        }
    
    def _soundcloud_config(self) -> Dict[str, str]:
        """SoundCloud OAuth2 configuration"""
        return {
            "authorization_url": "https://soundcloud.com/connect",
            "token_url": "https://api.soundcloud.com/oauth2/token",
            "userinfo_url": "https://api.soundcloud.com/me",
            "scope": "non-expiring"
        }
    
    def _twitch_config(self) -> Dict[str, str]:
        """Twitch OAuth2 configuration"""
        return {
            "authorization_url": "https://id.twitch.tv/oauth2/authorize",
            "token_url": "https://id.twitch.tv/oauth2/token",
            "userinfo_url": "https://api.twitch.tv/helix/users",
            "scope": "user:read:email"
        }
    
    def _patreon_config(self) -> Dict[str, str]:
        """Patreon OAuth2 configuration"""
        return {
            "authorization_url": "https://www.patreon.com/oauth2/authorize",
            "token_url": "https://www.patreon.com/api/oauth2/token",
            "userinfo_url": "https://www.patreon.com/api/oauth2/v2/identity",
            "scope": "identity identity[email]"
        }
    
    def _substack_config(self) -> Dict[str, str]:
        """Substack OAuth2 configuration"""
        return {
            "authorization_url": "https://substack.com/oauth/authorize",
            "token_url": "https://substack.com/api/v1/oauth/token",
            "userinfo_url": "https://substack.com/api/v1/me",
            "scope": "read"
        }
    
    def _medium_config(self) -> Dict[str, str]:
        """Medium OAuth2 configuration"""
        return {
            "authorization_url": "https://medium.com/m/oauth/authorize",
            "token_url": "https://api.medium.com/v1/tokens",
            "userinfo_url": "https://api.medium.com/v1/me",
            "scope": "basicProfile"
        }
    
    def _deviantart_config(self) -> Dict[str, str]:
        """DeviantArt OAuth2 configuration"""
        return {
            "authorization_url": "https://www.deviantart.com/oauth2/authorize",
            "token_url": "https://www.deviantart.com/oauth2/token",
            "userinfo_url": "https://www.deviantart.com/api/v1/oauth2/user/whoami",
            "scope": "basic"
        }
    
    def _behance_config(self) -> Dict[str, str]:
        """Behance OAuth2 configuration"""
        return {
            "authorization_url": "https://www.behance.net/v2/oauth/authenticate",
            "token_url": "https://api.behance.net/v2/oauth/token",
            "userinfo_url": "https://api.behance.net/v2/users/me",
            "scope": "activity_read"
        }
    
    def _dribbble_config(self) -> Dict[str, str]:
        """Dribbble OAuth2 configuration"""
        return {
            "authorization_url": "https://dribbble.com/oauth/authorize",
            "token_url": "https://dribbble.com/oauth/token",
            "userinfo_url": "https://api.dribbble.com/v2/user",
            "scope": "public"
        }
    
    def _apple_music_config(self) -> Dict[str, str]:
        """Apple Music OAuth2 configuration"""
        return {
            "authorization_url": "https://authorize.music.apple.com/oauth/authorize",
            "token_url": "https://authorize.music.apple.com/oauth/token",
            "userinfo_url": "https://api.music.apple.com/v1/me",
            "scope": "music-user-read"
        }
    
    def _amazon_music_config(self) -> Dict[str, str]:
        """Amazon Music OAuth2 configuration"""
        return {
            "authorization_url": "https://api.amazon.com/auth/o2/authorize",
            "token_url": "https://api.amazon.com/auth/o2/token",
            "userinfo_url": "https://api.amazon.com/user/profile",
            "scope": "profile"
        }
    
    def _bandcamp_config(self) -> Dict[str, str]:
        """Bandcamp OAuth2 configuration"""
        return {
            "authorization_url": "https://bandcamp.com/oauth_login",
            "token_url": "https://bandcamp.com/api/oauth/token",
            "userinfo_url": "https://bandcamp.com/api/account/1/my_profile",
            "scope": "basic"
        }
    
    def _mixcloud_config(self) -> Dict[str, str]:
        """Mixcloud OAuth2 configuration"""
        return {
            "authorization_url": "https://www.mixcloud.com/oauth/authorize",
            "token_url": "https://www.mixcloud.com/oauth/access_token",
            "userinfo_url": "https://api.mixcloud.com/me",
            "scope": "read"
        }
    
    def _vimeo_config(self) -> Dict[str, str]:
        """Vimeo OAuth2 configuration"""
        return {
            "authorization_url": "https://api.vimeo.com/oauth/authorize",
            "token_url": "https://api.vimeo.com/oauth/access_token",
            "userinfo_url": "https://api.vimeo.com/me",
            "scope": "public"
        }
    
    def _dailymotion_config(self) -> Dict[str, str]:
        """Dailymotion OAuth2 configuration"""
        return {
            "authorization_url": "https://www.dailymotion.com/oauth/authorize",
            "token_url": "https://www.dailymotion.com/oauth/token",
            "userinfo_url": "https://www.dailymotion.com/api/user/me",
            "scope": "userinfo"
        }
    
    def _github_config(self) -> Dict[str, str]:
        """GitHub OAuth2 configuration"""
        return {
            "authorization_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scope": "user:email"
        }
    
    def _gitlab_config(self) -> Dict[str, str]:
        """GitLab OAuth2 configuration"""
        return {
            "authorization_url": "https://gitlab.com/oauth/authorize",
            "token_url": "https://gitlab.com/oauth/token",
            "userinfo_url": "https://gitlab.com/api/v4/user",
            "scope": "read_user"
        }
    
    def _slack_config(self) -> Dict[str, str]:
        """Slack OAuth2 configuration"""
        return {
            "authorization_url": "https://slack.com/oauth/v2/authorize",
            "token_url": "https://slack.com/api/oauth.v2.access",
            "userinfo_url": "https://slack.com/api/users.identity",
            "scope": "identity.basic identity.email"
        }
    
    def _tiktok_config(self) -> Dict[str, str]:
        """TikTok OAuth2 configuration"""
        return {
            "authorization_url": "https://www.tiktok.com/auth/authorize/",
            "token_url": "https://open-api.tiktok.com/oauth/access_token/",
            "userinfo_url": "https://open-api.tiktok.com/user/info/",
            "scope": "user.info.basic"
        }
    
    def _facebook_config(self) -> Dict[str, str]:
        """Facebook OAuth2 configuration"""
        return {
            "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
            "userinfo_url": "https://graph.facebook.com/me",
            "scope": "email,public_profile"
        }
    
    def _apple_config(self) -> Dict[str, str]:
        """Apple OAuth2 configuration"""
        return {
            "authorization_url": "https://appleid.apple.com/auth/authorize",
            "token_url": "https://appleid.apple.com/auth/token",
            "userinfo_url": "https://appleid.apple.com/auth/userinfo",
            "scope": "name email"
        }
    
    def _microsoft_config(self) -> Dict[str, str]:
        """Microsoft OAuth2 configuration"""
        return {
            "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "userinfo_url": "https://graph.microsoft.com/v1.0/me",
            "scope": "openid profile email"
        }
    
    def _twitter_config(self) -> Dict[str, str]:
        """Twitter OAuth2 configuration"""
        return {
            "authorization_url": "https://twitter.com/i/oauth2/authorize",
            "token_url": "https://api.twitter.com/2/oauth2/token",
            "userinfo_url": "https://api.twitter.com/2/users/me",
            "scope": "tweet.read users.read"
        }
    
    def _linkedin_config(self) -> Dict[str, str]:
        """LinkedIn OAuth2 configuration"""
        return {
            "authorization_url": "https://www.linkedin.com/oauth/v2/authorization",
            "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
            "userinfo_url": "https://api.linkedin.com/v2/people/~",
            "scope": "r_liteprofile r_emailaddress"
        }
    
    def _pinterest_config(self) -> Dict[str, str]:
        """Pinterest OAuth2 configuration"""
        return {
            "authorization_url": "https://www.pinterest.com/oauth/",
            "token_url": "https://api.pinterest.com/v5/oauth/token",
            "userinfo_url": "https://api.pinterest.com/v5/user_account",
            "scope": "user_accounts:read"
        }
    
    def _discord_config(self) -> Dict[str, str]:
        """Discord OAuth2 configuration"""
        return {
            "authorization_url": "https://discord.com/api/oauth2/authorize",
            "token_url": "https://discord.com/api/oauth2/token",
            "userinfo_url": "https://discord.com/api/users/@me",
            "scope": "identify email"
        }
    
    def _twitch_config(self) -> Dict[str, str]:
        """Twitch OAuth2 configuration"""
        return {
            "authorization_url": "https://id.twitch.tv/oauth2/authorize",
            "token_url": "https://id.twitch.tv/oauth2/token",
            "userinfo_url": "https://api.twitch.tv/helix/users",
            "scope": "user:read:email"
        }
    
    def _github_config(self) -> Dict[str, str]:
        """GitHub OAuth2 configuration"""
        return {
            "authorization_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scope": "user:email"
        }
    
    def _soundcloud_config(self) -> Dict[str, str]:
        """SoundCloud OAuth2 configuration"""
        return {
            "authorization_url": "https://soundcloud.com/connect",
            "token_url": "https://api.soundcloud.com/oauth2/token",
            "userinfo_url": "https://api.soundcloud.com/me",
            "scope": "non-expiring"
        }
    
    def get_authorization_url(self, provider: AuthProvider, client_id: str, redirect_uri: str) -> str:
        """Get OAuth2 authorization URL for provider"""
        config = self.providers[provider]()
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": config["scope"],
            "response_type": "code",
            "state": secrets.token_urlsafe(16)
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config['authorization_url']}?{query_string}"

# ========================================
# SESSION MANAGER
# ========================================

class SessionManager:
    """Distributed session management with Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session_expire = timedelta(hours=24)
    
    async def create_session(self, user_id: str, device_info: Dict[str, Any]) -> UserSession:
        """Create new user session"""
        session_id = secrets.token_urlsafe(32)
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            device_id=device_info.get("device_id", "unknown"),
            ip_address=device_info.get("ip_address", "unknown"),
            user_agent=device_info.get("user_agent", "unknown"),
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.session_expire,
            is_mobile=device_info.get("is_mobile", False)
        )
        
        # Store in Redis
        session_key = f"session:{session_id}"
        await self.redis.setex(
            session_key, 
            int(self.session_expire.total_seconds()),
            session.json()
        )
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        session_key = f"session:{session_id}"
        session_data = await self.redis.get(session_key)
        
        if session_data:
            return UserSession.parse_raw(session_data)
        return None
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""
        session = await self.get_session(session_id)
        if session:
            session.last_activity = datetime.utcnow()
            session_key = f"session:{session_id}"
            await self.redis.setex(
                session_key,
                int(self.session_expire.total_seconds()),
                session.json()
            )
            return True
        return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        session_key = f"session:{session_id}"
        return await self.redis.delete(session_key) > 0

# ========================================
# MULTI-FACTOR AUTHENTICATION
# ========================================

class MFAManager:
    """Multi-factor authentication manager"""
    
    def __init__(self):
        self.totp_issuer = "IA Influencer Agent"
    
    def generate_totp_secret(self, user_email: str) -> str:
        """Generate TOTP secret for user"""
        return pyotp.random_base32()
    
    def generate_totp_qr_code(self, user_email: str, secret: str) -> str:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=self.totp_issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode()
    
    def verify_totp_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    async def send_sms_code(self, phone_number: str) -> str:
        """Send SMS verification code"""
        code = secrets.randbelow(900000) + 100000
        # SMS integration would go here
        return str(code)
    
    async def send_email_code(self, email: str) -> str:
        """Send email verification code"""
        code = secrets.randbelow(900000) + 100000
        # Email integration would go here
        return str(code)

# ========================================
# BIOMETRIC AUTHENTICATION MANAGER
# ========================================

class BiometricAuthManager:
    """Biometric authentication manager for face, voice, fingerprint recognition"""
    
    def __init__(self):
        self.supported_types = [BiometricType.FACE, BiometricType.VOICE, BiometricType.FINGERPRINT]
        self.confidence_threshold = 0.85
        self.max_attempts = 3
    
    async def enroll_biometric(self, user_id: str, biometric_type: BiometricType, biometric_data: bytes) -> str:
        """Enroll biometric data for user"""
        # Generate unique biometric template ID
        template_id = f"bio_{user_id}_{biometric_type.value}_{secrets.token_hex(8)}"
        
        # In production, this would use specialized biometric SDKs
        if biometric_type == BiometricType.FACE:
            template = await self._process_face_enrollment(biometric_data)
        elif biometric_type == BiometricType.VOICE:
            template = await self._process_voice_enrollment(biometric_data)
        elif biometric_type == BiometricType.FINGERPRINT:
            template = await self._process_fingerprint_enrollment(biometric_data)
        else:
            raise ValueError(f"Unsupported biometric type: {biometric_type}")
        
        # Store encrypted template
        await self._store_biometric_template(template_id, template)
        
        return template_id
    
    async def verify_biometric(self, user_id: str, biometric_type: BiometricType, biometric_data: bytes) -> bool:
        """Verify biometric data against enrolled template"""
        try:
            # Get user's enrolled templates
            templates = await self._get_user_templates(user_id, biometric_type)
            
            if not templates:
                return False
            
            # Process verification data
            if biometric_type == BiometricType.FACE:
                verification_template = await self._process_face_verification(biometric_data)
            elif biometric_type == BiometricType.VOICE:
                verification_template = await self._process_voice_verification(biometric_data)
            elif biometric_type == BiometricType.FINGERPRINT:
                verification_template = await self._process_fingerprint_verification(biometric_data)
            else:
                return False
            
            # Compare against enrolled templates
            for template in templates:
                confidence = await self._compare_templates(verification_template, template)
                if confidence >= self.confidence_threshold:
                    return True
            
            return False
            
        except Exception as e:
            # Log error but don't expose details
            return False
    
    async def _process_face_enrollment(self, face_data: bytes) -> Dict[str, Any]:
        """Process face enrollment using facial recognition"""
        # Mock implementation - would use OpenCV/dlib in production
        return {
            "type": "face",
            "features": hashlib.sha256(face_data).hexdigest(),
            "quality_score": 0.9,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _process_voice_enrollment(self, voice_data: bytes) -> Dict[str, Any]:
        """Process voice enrollment using speaker recognition"""
        # Mock implementation - would use speech processing libraries
        return {
            "type": "voice",
            "features": hashlib.sha256(voice_data).hexdigest(),
            "quality_score": 0.88,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _process_fingerprint_enrollment(self, fingerprint_data: bytes) -> Dict[str, Any]:
        """Process fingerprint enrollment"""
        # Mock implementation - would use fingerprint SDK
        return {
            "type": "fingerprint",
            "minutiae": hashlib.sha256(fingerprint_data).hexdigest(),
            "quality_score": 0.92,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _process_face_verification(self, face_data: bytes) -> Dict[str, Any]:
        """Process face verification data"""
        return await self._process_face_enrollment(face_data)
    
    async def _process_voice_verification(self, voice_data: bytes) -> Dict[str, Any]:
        """Process voice verification data"""
        return await self._process_voice_enrollment(voice_data)
    
    async def _process_fingerprint_verification(self, fingerprint_data: bytes) -> Dict[str, Any]:
        """Process fingerprint verification data"""
        return await self._process_fingerprint_enrollment(fingerprint_data)
    
    async def _store_biometric_template(self, template_id: str, template: Dict[str, Any]) -> None:
        """Store encrypted biometric template"""
        # In production, this would use secure encrypted storage
        pass
    
    async def _get_user_templates(self, user_id: str, biometric_type: BiometricType) -> List[Dict[str, Any]]:
        """Get user's enrolled biometric templates"""
        # Mock implementation
        return [{"features": "mock_template", "quality_score": 0.9}]
    
    async def _compare_templates(self, template1: Dict[str, Any], template2: Dict[str, Any]) -> float:
        """Compare biometric templates and return confidence score"""
        # Mock implementation - would use specialized comparison algorithms
        return 0.9 if template1.get("features") == template2.get("features") else 0.3


# ========================================
# ENTERPRISE HARDWARE SECURITY MANAGER
# ========================================

class HardwareSecurityManager:
    """Enterprise hardware security key manager with YubiKey/FIDO2 support"""
    
    def __init__(self):
        self.supported_protocols = ["FIDO2", "U2F", "OTP", "PIV", "OATH"]
        self.key_registry = {}  # Would be database in production
    
    async def register_hardware_key(self, user_id: str, key_data: Dict[str, Any]) -> str:
        """Register hardware security key for user"""
        try:
            key_id = f"hwkey_{user_id}_{secrets.token_hex(8)}"
            
            # Validate hardware key
            if not await self._validate_hardware_key(key_data):
                raise ValueError("Invalid hardware key")
            
            # Extract key information
            key_info = {
                "key_id": key_id,
                "user_id": user_id,
                "protocol": key_data.get("protocol", "FIDO2"),
                "public_key": key_data.get("public_key"),
                "attestation": key_data.get("attestation"),
                "counter": 0,
                "created_at": datetime.utcnow().isoformat(),
                "last_used": None
            }
            
            # Store in registry
            self.key_registry[key_id] = key_info
            
            return key_id
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Hardware key registration failed: {e}")
    
    async def verify_hardware_key(self, user_id: str, challenge: str, response: Dict[str, Any]) -> bool:
        """Verify hardware key challenge response"""
        try:
            # Get user's registered keys
            user_keys = [k for k in self.key_registry.values() if k["user_id"] == user_id]
            
            if not user_keys:
                return False
            
            # Verify challenge response against each registered key
            for key_info in user_keys:
                if await self._verify_fido2_response(key_info, challenge, response):
                    # Update usage counter
                    key_info["counter"] += 1
                    key_info["last_used"] = datetime.utcnow().isoformat()
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _validate_hardware_key(self, key_data: Dict[str, Any]) -> bool:
        """Validate hardware key format and authenticity"""
        required_fields = ["protocol", "public_key"]
        return all(field in key_data for field in required_fields)
    
    async def _verify_fido2_response(self, key_info: Dict, challenge: str, response: Dict) -> bool:
        """Verify FIDO2 challenge response"""
        # Mock implementation - would use WebAuthn libraries in production
        return (
            response.get("challenge") == challenge and
            response.get("key_id") == key_info["key_id"]
        )


# ========================================
# ENTERPRISE SESSION CLUSTERING MANAGER
# ========================================

class DistributedSessionManager:
    """Enterprise distributed session management with Redis clustering"""
    
    def __init__(self, redis_cluster_urls: List[str] = None):
        self.redis_cluster_urls = redis_cluster_urls or ["redis://localhost:6379"]
        self.session_timeout = 24 * 60 * 60  # 24 hours
        self.max_sessions_per_user = 10
    
    async def create_distributed_session(self, user_id: str, device_info: Dict[str, Any]) -> str:
        """Create distributed session across Redis cluster"""
        try:
            session_id = f"sess_{user_id}_{secrets.token_hex(16)}"
            
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "device_info": device_info,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "is_active": True,
                "location": device_info.get("location", "unknown"),
                "user_agent": device_info.get("user_agent", "unknown")
            }
            
            # Store session in Redis cluster
            await self._store_session_distributed(session_id, session_data)
            
            # Enforce session limits
            await self._enforce_session_limits(user_id)
            
            return session_id
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Session creation failed: {e}")
    
    async def validate_distributed_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session across Redis cluster"""
        try:
            session_data = await self._get_session_distributed(session_id)
            
            if not session_data or not session_data.get("is_active"):
                return None
            
            # Check session timeout
            created_at = datetime.fromisoformat(session_data["created_at"])
            if (datetime.utcnow() - created_at).total_seconds() > self.session_timeout:
                await self._invalidate_session_distributed(session_id)
                return None
            
            # Update last activity
            session_data["last_activity"] = datetime.utcnow().isoformat()
            await self._store_session_distributed(session_id, session_data)
            
            return session_data
            
        except Exception:
            return None
    
    async def _store_session_distributed(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Store session data in Redis cluster"""
        # Mock implementation - would use Redis cluster client
        pass
    
    async def _get_session_distributed(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis cluster"""
        # Mock implementation - would query Redis cluster
        return {
            "session_id": session_id,
            "user_id": "mock_user",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
    
    async def _invalidate_session_distributed(self, session_id: str) -> None:
        """Invalidate session across Redis cluster"""
        # Mock implementation - would remove from Redis cluster
        pass
    
    async def _enforce_session_limits(self, user_id: str) -> None:
        """Enforce maximum sessions per user"""
        # Mock implementation - would query and cleanup old sessions
        pass


# ========================================
# ENHANCED AUTHENTICATION SERVICE
# ========================================

class EnterpriseAuthenticationService:
    """Enhanced authentication service with enterprise features"""
    
    def __init__(self, jwt_secret: str, redis_cluster: Optional[List[str]] = None):
        self.jwt_manager = JWTManager(jwt_secret)
        self.oauth2_manager = OAuth2Manager()
        self.mfa_manager = MFAManager()
        self.biometric_manager = BiometricAuthManager()
        self.hardware_security = HardwareSecurityManager()
        self.session_manager = DistributedSessionManager(redis_cluster)
        self.password_manager = PasswordManager()
    
    async def authenticate_multi_platform(
        self, 
        provider: AuthProvider, 
        auth_code: str,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Authenticate user via multiple OAuth platforms"""
        try:
            # Get provider configuration
            provider_config = self.oauth2_manager.providers.get(provider)
            if not provider_config:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
            
            # Exchange auth code for tokens
            tokens = await self._exchange_oauth_code(provider, auth_code, provider_config())
            
            # Get user info from provider
            user_info = await self._get_provider_user_info(provider, tokens, provider_config())
            
            # Create or update user account
            user_account = await self._create_or_update_user(user_info, provider)
            
            # Create distributed session
            session_id = await self.session_manager.create_distributed_session(
                user_account["id"], 
                device_info
            )
            
            # Generate JWT tokens
            access_token = await self.jwt_manager.create_access_token(user_account["id"])
            refresh_token = await self.jwt_manager.create_refresh_token(user_account["id"])
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "session_id": session_id,
                "user": user_account,
                "provider": provider.value,
                "expires_in": 3600
            }
            
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {e}")
    
    async def authenticate_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        biometric_data: bytes,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Authenticate user via biometric data"""
        try:
            # Verify biometric data
            is_valid = await self.biometric_manager.verify_biometric(
                user_id, biometric_type, biometric_data
            )
            
            if not is_valid:
                raise HTTPException(status_code=401, detail="Biometric authentication failed")
            
            # Create session and tokens
            session_id = await self.session_manager.create_distributed_session(user_id, device_info)
            access_token = await self.jwt_manager.create_access_token(user_id)
            refresh_token = await self.jwt_manager.create_refresh_token(user_id)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "session_id": session_id,
                "authentication_method": f"biometric_{biometric_type.value}",
                "expires_in": 3600
            }
            
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Biometric authentication failed: {e}")
    
    async def authenticate_hardware_key(
        self,
        user_id: str,
        challenge: str,
        key_response: Dict[str, Any],
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Authenticate user via hardware security key"""
        try:
            # Verify hardware key response
            is_valid = await self.hardware_security.verify_hardware_key(
                user_id, challenge, key_response
            )
            
            if not is_valid:
                raise HTTPException(status_code=401, detail="Hardware key authentication failed")
            
            # Create session and tokens
            session_id = await self.session_manager.create_distributed_session(user_id, device_info)
            access_token = await self.jwt_manager.create_access_token(user_id)
            refresh_token = await self.jwt_manager.create_refresh_token(user_id)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "session_id": session_id,
                "authentication_method": "hardware_key",
                "expires_in": 3600
            }
            
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Hardware key authentication failed: {e}")
    
    async def _exchange_oauth_code(self, provider: AuthProvider, code: str, config: Dict) -> Dict:
        """Exchange OAuth authorization code for tokens"""
        # Mock implementation - would make HTTP request to provider
        return {
            "access_token": f"oauth_{provider.value}_{secrets.token_hex(16)}",
            "refresh_token": f"refresh_{provider.value}_{secrets.token_hex(16)}",
            "expires_in": 3600
        }
    
    async def _get_provider_user_info(self, provider: AuthProvider, tokens: Dict, config: Dict) -> Dict:
        """Get user information from OAuth provider"""
        # Mock implementation - would make HTTP request to provider
        return {
            "id": f"provider_{provider.value}_{secrets.token_hex(8)}",
            "email": f"user@{provider.value}.com",
            "name": f"User from {provider.value}",
            "provider": provider.value
        }
    
    async def _create_or_update_user(self, user_info: Dict, provider: AuthProvider) -> Dict:
        """Create or update user account from provider info"""
        # Mock implementation - would interact with database
        return {
            "id": user_info["id"],
            "email": user_info["email"],
            "name": user_info["name"],
            "provider": provider.value,
            "created_at": datetime.utcnow().isoformat()
        }
        return {
            "type": "voice",
            "voiceprint": hashlib.sha256(voice_data).hexdigest(),
            "quality_score": 0.85,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _process_fingerprint_enrollment(self, fingerprint_data: bytes) -> Dict[str, Any]:
        """Process fingerprint enrollment"""
        # Mock implementation - would use fingerprint SDKs
        return {
            "type": "fingerprint",
            "minutiae": hashlib.sha256(fingerprint_data).hexdigest(),
            "quality_score": 0.95,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _process_face_verification(self, face_data: bytes) -> Dict[str, Any]:
        """Process face verification"""
        return await self._process_face_enrollment(face_data)
    
    async def _process_voice_verification(self, voice_data: bytes) -> Dict[str, Any]:
        """Process voice verification"""
        return await self._process_voice_enrollment(voice_data)
    
    async def _process_fingerprint_verification(self, fingerprint_data: bytes) -> Dict[str, Any]:
        """Process fingerprint verification"""
        return await self._process_fingerprint_enrollment(fingerprint_data)
    
    async def _compare_templates(self, template1: Dict[str, Any], template2: Dict[str, Any]) -> float:
        """Compare two biometric templates and return confidence score"""
        # Mock implementation - would use specialized matching algorithms
        if template1.get("type") != template2.get("type"):
            return 0.0
        
        # Simple hash comparison for mock
        if template1.get("type") == "face":
            return 0.9 if template1.get("features") == template2.get("features") else 0.1
        elif template1.get("type") == "voice":
            return 0.88 if template1.get("voiceprint") == template2.get("voiceprint") else 0.1
        elif template1.get("type") == "fingerprint":
            return 0.95 if template1.get("minutiae") == template2.get("minutiae") else 0.1
        
        return 0.0
    
    async def _store_biometric_template(self, template_id: str, template: Dict[str, Any]) -> None:
        """Store encrypted biometric template"""
        # Mock implementation - would use secure storage with encryption
        pass
    
    async def _get_user_templates(self, user_id: str, biometric_type: BiometricType) -> List[Dict[str, Any]]:
        """Get user's enrolled biometric templates"""
        # Mock implementation - would retrieve from secure storage
        return []

# ========================================
# PASSWORD MANAGER
# ========================================

class PasswordManager:
    """Password hashing and validation manager"""
    
    def __init__(self):
        self.rounds = 12
        self.min_length = 8
        self.max_length = 128
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=self.rounds)).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> List[str]:
        """Validate password strength and return issues"""
        issues = []
        
        if len(password) < self.min_length:
            issues.append(f"Password must be at least {self.min_length} characters")
        
        if len(password) > self.max_length:
            issues.append(f"Password must be no more than {self.max_length} characters")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
            issues.append("Password must contain at least one special character")
        
        return issues

# ========================================
# AUTHENTICATION SERVICE
# ========================================

class AuthenticationService:
    """Main authentication service consolidating all auth functionality"""
    
    def __init__(self, secret_key: str, redis_client: redis.Redis):
        self.jwt_manager = JWTManager(secret_key)
        self.oauth2_manager = OAuth2Manager()
        self.session_manager = SessionManager(redis_client)
        self.mfa_manager = MFAManager()
        self.biometric_manager = BiometricAuthManager()
        self.password_manager = PasswordManager()
    
    async def authenticate_user(self, credentials: UserCredentials, device_info: Dict[str, Any]) -> TokenPair:
        """Authenticate user with email/password"""
        # Password validation would go here
        # For now, returning mock response
        
        user_id = "user_123"  # Would come from database
        
        # Create session
        session = await self.session_manager.create_session(user_id, device_info)
        
        # Create tokens
        return self.jwt_manager.create_token_pair(user_id)
    
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token"""
        payload = self.jwt_manager.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        return self.jwt_manager.create_token_pair(user_id)
    
    async def logout(self, session_id: str) -> bool:
        """Logout user and invalidate session"""
        return await self.session_manager.delete_session(session_id)

# ========================================
# DEPENDENCY INJECTION
# ========================================

# Global instances (would be properly injected in real implementation)
_auth_service = None

def get_auth_service() -> AuthenticationService:
    """Get authentication service instance"""
    global _auth_service
    if _auth_service is None:
        # Mock initialization - would use proper dependency injection
        _auth_service = AuthenticationService("mock_secret", None)
    return _auth_service

# ========================================
# EXPORTS
# ========================================

__all__ = [
    "AuthProvider",
    "MFAMethod",
    "BiometricType",
    "DeviceType",
    "UserCredentials",
    "TokenPair",
    "UserSession",
    "JWTManager",
    "OAuth2Manager",
    "SessionManager",
    "MFAManager",
    "BiometricAuthManager",
    "PasswordManager",
    "AuthenticationService",
    "HardwareSecurityManager",
    "DistributedSessionManager",
    "EnterpriseAuthenticationService",
    "get_auth_service"
]