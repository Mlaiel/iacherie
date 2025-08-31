"""OAuth Configuration Module for IA-Influencer Agent Platform
===========================================================

Professional OAuth2 configuration for external service integrations.
Supports multi-platform authentication for content creators and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission
is strictly prohibited and will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field, validator
from enum import Enum


class OAuthProvider(str, Enum):
    """Supported OAuth providers for content platforms."""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SOUNDCLOUD = "soundcloud"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    GITHUB = "github"


class OAuthScope(str, Enum):
    """OAuth scopes for different platform integrations."""    # Spotify scopes
    SPOTIFY_READ = "user-read-private user-read-email user-library-read"
    SPOTIFY_WRITE = "user-library-modify playlist-modify-public playlist-modify-private"
    SPOTIFY_ADVANCED = "user-read-recently-played user-top-read user-follow-read"
    
    # YouTube scopes
    YOUTUBE_READ = "https://www.googleapis.com/auth/youtube.readonly"
    YOUTUBE_UPLOAD = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_MANAGE = "https://www.googleapis.com/auth/youtube"
    
    # Social media scopes
    INSTAGRAM_READ = "user_profile,user_media"
    TIKTOK_READ = "user.info.basic,video.list"
    TWITTER_READ = "tweet.read users.read"
    
    # Business scopes
    LINKEDIN_READ = "r_liteprofile r_emailaddress"
    FACEBOOK_READ = "email public_profile pages_show_list"


class OAuthConfig(BaseSettings):
    """OAuth configuration for external service integrations."""    
    # Spotify OAuth
    spotify_client_id: str = Field(..., env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(..., env="SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri: str = Field(..., env="SPOTIFY_REDIRECT_URI")
    spotify_scopes: List[str] = Field(default_factory=lambda: [
        OAuthScope.SPOTIFY_READ,
        OAuthScope.SPOTIFY_WRITE,
        OAuthScope.SPOTIFY_ADVANCED
    ])
    
    # YouTube OAuth
    youtube_client_id: str = Field(..., env="YOUTUBE_CLIENT_ID")
    youtube_client_secret: str = Field(..., env="YOUTUBE_CLIENT_SECRET")
    youtube_redirect_uri: str = Field(..., env="YOUTUBE_REDIRECT_URI")
    youtube_scopes: List[str] = Field(default_factory=lambda: [
        OAuthScope.YOUTUBE_READ,
        OAuthScope.YOUTUBE_UPLOAD,
        OAuthScope.YOUTUBE_MANAGE
    ])
    
    # Instagram OAuth
    instagram_client_id: str = Field(..., env="INSTAGRAM_CLIENT_ID")
    instagram_client_secret: str = Field(..., env="INSTAGRAM_CLIENT_SECRET")
    instagram_redirect_uri: str = Field(..., env="INSTAGRAM_REDIRECT_URI")
    instagram_scopes: List[str] = Field(default_factory=lambda: [OAuthScope.INSTAGRAM_READ])
    
    # TikTok OAuth
    tiktok_client_id: str = Field(..., env="TIKTOK_CLIENT_ID")
    tiktok_client_secret: str = Field(..., env="TIKTOK_CLIENT_SECRET")
    tiktok_redirect_uri: str = Field(..., env="TIKTOK_REDIRECT_URI")
    tiktok_scopes: List[str] = Field(default_factory=lambda: [OAuthScope.TIKTOK_READ])
    
    # SoundCloud OAuth
    soundcloud_client_id: str = Field(..., env="SOUNDCLOUD_CLIENT_ID")
    soundcloud_client_secret: str = Field(..., env="SOUNDCLOUD_CLIENT_SECRET")
    soundcloud_redirect_uri: str = Field(..., env="SOUNDCLOUD_REDIRECT_URI")
    
    # Twitter OAuth
    twitter_client_id: str = Field(..., env="TWITTER_CLIENT_ID")
    twitter_client_secret: str = Field(..., env="TWITTER_CLIENT_SECRET")
    twitter_redirect_uri: str = Field(..., env="TWITTER_REDIRECT_URI")
    twitter_scopes: List[str] = Field(default_factory=lambda: [OAuthScope.TWITTER_READ])
    
    # Facebook OAuth
    facebook_app_id: str = Field(..., env="FACEBOOK_APP_ID")
    facebook_app_secret: str = Field(..., env="FACEBOOK_APP_SECRET")
    facebook_redirect_uri: str = Field(..., env="FACEBOOK_REDIRECT_URI")
    facebook_scopes: List[str] = Field(default_factory=lambda: [OAuthScope.FACEBOOK_READ])
    
    # LinkedIn OAuth
    linkedin_client_id: str = Field(..., env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: str = Field(..., env="LINKEDIN_CLIENT_SECRET")
    linkedin_redirect_uri: str = Field(..., env="LINKEDIN_REDIRECT_URI")
    linkedin_scopes: List[str] = Field(default_factory=lambda: [OAuthScope.LINKEDIN_READ])
    
    # GitHub OAuth (for developer integrations)
    github_client_id: str = Field(..., env="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(..., env="GITHUB_CLIENT_SECRET")
    github_redirect_uri: str = Field(..., env="GITHUB_REDIRECT_URI")
    
    # General OAuth settings
    oauth_state_secret: str = Field(..., env="OAUTH_STATE_SECRET")
    oauth_token_expiry_seconds: int = Field(default=3600, env="OAUTH_TOKEN_EXPIRY")
    oauth_refresh_buffer_seconds: int = Field(default=300, env="OAUTH_REFRESH_BUFFER")
    
    # Security settings
    oauth_enforce_https: bool = Field(default=True, env="OAUTH_ENFORCE_HTTPS")
    oauth_csrf_protection: bool = Field(default=True, env="OAUTH_CSRF_PROTECTION")
    oauth_rate_limit_per_hour: int = Field(default=100, env="OAUTH_RATE_LIMIT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class OAuthEndpoints:
    """OAuth endpoints configuration for supported platforms."""    
    ENDPOINTS = {
        OAuthProvider.SPOTIFY: {
            "authorize": "https://accounts.spotify.com/authorize",
            "token": "https://accounts.spotify.com/api/token",
            "userinfo": "https://api.spotify.com/v1/me"
        },
        OAuthProvider.YOUTUBE: {
            "authorize": "https://accounts.google.com/o/oauth2/v2/auth",
            "token": "https://oauth2.googleapis.com/token",
            "userinfo": "https://www.googleapis.com/oauth2/v1/userinfo"
        },
        OAuthProvider.INSTAGRAM: {
            "authorize": "https://api.instagram.com/oauth/authorize",
            "token": "https://api.instagram.com/oauth/access_token",
            "userinfo": "https://graph.instagram.com/me"
        },
        OAuthProvider.TIKTOK: {
            "authorize": "https://www.tiktok.com/auth/authorize/",
            "token": "https://open-api.tiktok.com/oauth/access_token/",
            "userinfo": "https://open-api.tiktok.com/user/info/"
        },
        OAuthProvider.SOUNDCLOUD: {
            "authorize": "https://soundcloud.com/connect",
            "token": "https://api.soundcloud.com/oauth2/token",
            "userinfo": "https://api.soundcloud.com/me"
        },
        OAuthProvider.TWITTER: {
            "authorize": "https://twitter.com/i/oauth2/authorize",
            "token": "https://api.twitter.com/2/oauth2/token",
            "userinfo": "https://api.twitter.com/2/users/me"
        },
        OAuthProvider.FACEBOOK: {
            "authorize": "https://www.facebook.com/v18.0/dialog/oauth",
            "token": "https://graph.facebook.com/v18.0/oauth/access_token",
            "userinfo": "https://graph.facebook.com/me"
        },
        OAuthProvider.LINKEDIN: {
            "authorize": "https://www.linkedin.com/oauth/v2/authorization",
            "token": "https://www.linkedin.com/oauth/v2/accessToken",
            "userinfo": "https://api.linkedin.com/v2/me"
        },
        OAuthProvider.GITHUB: {
            "authorize": "https://github.com/login/oauth/authorize",
            "token": "https://github.com/login/oauth/access_token",
            "userinfo": "https://api.github.com/user"
        }
    }
    
    @classmethod
    def get_endpoints(cls, provider: OAuthProvider) -> Dict[str, str]:
        """Get OAuth endpoints for a specific provider."""        return cls.ENDPOINTS.get(provider, {})


class OAuthManager:
    """OAuth manager for handling multi-platform authentication."""    
    def __init__(self, config: OAuthConfig):
        self.config = config
        
    def get_authorization_url(
        self, 
        provider: OAuthProvider, 
        state: str,
        scopes: Optional[List[str]] = None
    ) -> str:
        """Generate authorization URL for OAuth flow."""        endpoints = OAuthEndpoints.get_endpoints(provider)
        if not endpoints:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
            
        client_id = getattr(self.config, f"{provider}_client_id")
        redirect_uri = getattr(self.config, f"{provider}_redirect_uri")
        
        if scopes is None:
            scopes = getattr(self.config, f"{provider}_scopes", [])
            
        scope_string = " ".join(scopes) if isinstance(scopes, list) else scopes
        
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scope_string,
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{endpoints['authorize']}?{query_string}"
    
    def get_provider_config(self, provider: OAuthProvider) -> Dict[str, Any]:
        """Get complete configuration for a specific provider."""        return {
            "client_id": getattr(self.config, f"{provider}_client_id"),
            "client_secret": getattr(self.config, f"{provider}_client_secret"),
            "redirect_uri": getattr(self.config, f"{provider}_redirect_uri"),
            "scopes": getattr(self.config, f"{provider}_scopes", []),
            "endpoints": OAuthEndpoints.get_endpoints(provider)
        }
    
    def validate_provider_config(self, provider: OAuthProvider) -> bool:
        """Validate that all required configuration is present for a provider."""        try:
            config = self.get_provider_config(provider)
            required_fields = ["client_id", "client_secret", "redirect_uri"]
            return all(config.get(field) for field in required_fields)
        except AttributeError:
            return False


# Global OAuth configuration instance
oauth_config = OAuthConfig()
oauth_manager = OAuthManager(oauth_config)
