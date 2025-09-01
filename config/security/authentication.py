"""Authentication Configuration Module
===================================

Advanced authentication configuration for IA Influencer Agent platform.
Supports JWT, OAuth2, multi-factor authentication, social logins,
and enterprise-grade authentication flows.

Business Logic Integration:
- Creator authentication before content upload
- Secure session management for content processing
- Multi-platform authentication for distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum


class AuthenticationMethod(Enum):
    """
Supported authentication methods."""

    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    API_KEY = "api_key"
    MULTI_FACTOR = "mfa"
    BIOMETRIC = "biometric"


class SocialProvider(Enum):
    """Supported social authentication providers."""

    GOOGLE = "google"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


@dataclass
class JwtConfig:
    """JWT authentication configuration."""
    secret_key: str = field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: str = "ia-influencer-agent"
    audience: str = "ia-influencer-users"
    
    # Advanced JWT features
    auto_refresh_threshold: int = 5  # minutes before expiry
    max_refresh_attempts: int = 3
    blacklist_enabled: bool = True
    csrf_protection: bool = True
    
    # Content creator specific claims
    creator_claims: List[str] = field(default_factory=lambda: [
        "creator_id",
        "creator_type",  # musician, blogger, photographer, etc.
        "verification_level",
        "subscription_tier",
        "content_permissions"
    ])


@dataclass
class OAuth2Config:
    """OAuth2 authentication configuration."""
    authorization_server: str = ""
    token_endpoint: str = ""
    userinfo_endpoint: str = ""
    client_id: str = field(default_factory=lambda: os.getenv("OAUTH2_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os.getenv("OAUTH2_CLIENT_SECRET", ""))
    
    # OAuth2 flows
    supported_flows: List[str] = field(default_factory=lambda: [
        "authorization_code",
        "refresh_token",
        "client_credentials"
    ])
    
    # Scopes for content creators
    creator_scopes: List[str] = field(default_factory=lambda: [
        "profile",
        "email",
        "content:upload",
        "content:protect",
        "analytics:read",
        "revenue:read"
    ])
    
    # Platform-specific scopes
    platform_scopes: Dict[str, List[str]] = field(default_factory=lambda: {
        "spotify": ["user-read-private", "user-read-email", "playlist-read-private"],
        "youtube": ["youtube.readonly", "youtube.upload"],
        "instagram": ["instagram_basic", "instagram_content_publish"],
        "tiktok": ["user.info.basic", "video.list"]
    })


@dataclass
class MultiFactorConfig:
    """Multi-factor authentication configuration."""
    enabled: bool = True
    required_for_creators: bool = True
    methods: List[str] = field(default_factory=lambda: [
        "totp",  # Time-based OTP
        "sms",   # SMS verification
        "email", # Email verification
        "push"   # Push notification
    ])
    
    # TOTP configuration
    totp_issuer: str = "IA Influencer Agent"
    totp_digits: int = 6
    totp_window: int = 1
    
    # SMS configuration
    sms_provider: str = "twilio"
    sms_template: str = "Your IA Influencer Agent verification code: {code}"
    
    # Backup codes
    backup_codes_count: int = 10
    backup_codes_length: int = 8


@dataclass
class SocialAuthConfig:
    """Social authentication providers configuration."""
    enabled_providers: List[SocialProvider] = field(default_factory=lambda: [
        SocialProvider.GOOGLE,
        SocialProvider.SPOTIFY,
        SocialProvider.INSTAGRAM,
        SocialProvider.YOUTUBE
    ])
    
    # Provider configurations
    google: Dict[str, str] = field(default_factory=lambda: {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": "/auth/google/callback"
    })
    
    spotify: Dict[str, str] = field(default_factory=lambda: {
        "client_id": os.getenv("SPOTIFY_CLIENT_ID", ""),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET", ""),
        "redirect_uri": "/auth/spotify/callback"
    })
    
    instagram: Dict[str, str] = field(default_factory=lambda: {
        "client_id": os.getenv("INSTAGRAM_CLIENT_ID", ""),
        "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET", ""),
        "redirect_uri": "/auth/instagram/callback"
    })
    
    youtube: Dict[str, str] = field(default_factory=lambda: {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID", ""),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
        "redirect_uri": "/auth/youtube/callback"
    })


@dataclass
class SessionConfig:
    """Session management configuration."""
    session_timeout: timedelta = timedelta(hours=24)
    idle_timeout: timedelta = timedelta(hours=2)
    concurrent_sessions_limit: int = 5
    
    # Session security
    secure_cookies: bool = True
    httponly_cookies: bool = True
    samesite_cookies: str = "Strict"
    
    # Content creator sessions
    creator_extended_session: bool = True
    creator_session_timeout: timedelta = timedelta(days=7)
    
    # Session storage
    storage_backend: str = "redis"
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))


@dataclass
class PasswordConfig:
    """Password policy configuration."""
    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_symbols: bool = True
    
    # Password history
    history_count: int = 12
    
    # Password strength
    min_strength_score: int = 3  # 0-4 scale
    forbidden_passwords: List[str] = field(default_factory=lambda: [
        "password", "123456", "admin", "creator"
    ])
    
    # Reset configuration
    reset_token_expire_hours: int = 1
    max_reset_attempts: int = 3


@dataclass
class ApiKeyConfig:
    """API key authentication configuration."""
    enabled: bool = True
    key_length: int = 64
    key_prefix: str = "ia_"
    
    # Key types for different creator operations
    key_types: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "upload": {
            "permissions": ["content:upload", "content:process"],
            "rate_limit": "1000/hour",
            "expires_days": 90
        },
        "protection": {
            "permissions": ["content:protect", "fingerprint:create"],
            "rate_limit": "500/hour", 
            "expires_days": 365
        },
        "analytics": {
            "permissions": ["analytics:read", "reports:generate"],
            "rate_limit": "2000/hour",
            "expires_days": 180
        },
        "revenue": {
            "permissions": ["revenue:read", "payments:process"],
            "rate_limit": "100/hour",
            "expires_days": 365
        }
    })


@dataclass
class AuthenticationConfig:
    """Main authentication configuration container."""
    jwt: JwtConfig = field(default_factory=JwtConfig)
    oauth2: OAuth2Config = field(default_factory=OAuth2Config)
    mfa: MultiFactorConfig = field(default_factory=MultiFactorConfig)
    social: SocialAuthConfig = field(default_factory=SocialAuthConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    password: PasswordConfig = field(default_factory=PasswordConfig)
    api_key: ApiKeyConfig = field(default_factory=ApiKeyConfig)
    
    # Global authentication settings
    default_method: AuthenticationMethod = AuthenticationMethod.JWT
    fallback_methods: List[AuthenticationMethod] = field(default_factory=lambda: [
        AuthenticationMethod.OAUTH2,
        AuthenticationMethod.API_KEY
    ])
    
    # Creator-specific settings
    creator_verification_required: bool = True
    creator_identity_verification: bool = True
    creator_document_verification: bool = False  # For premium tiers
    
    # Security features
    brute_force_protection: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    
    # Audit and monitoring
    log_authentication_events: bool = True
    monitor_suspicious_activity: bool = True
    alert_on_security_events: bool = True


# Default configuration instance
authentication_config = AuthenticationConfig()


def get_authentication_config() -> AuthenticationConfig:
    """
Get the authentication configuration instance."""
    return authentication_config


def validate_authentication_config(config: AuthenticationConfig) -> bool:
    """
Validate authentication configuration settings."""
    if not config.jwt.secret_key:
        raise ValueError("JWT secret key is required")
    
    if config.oauth2.client_id and not config.oauth2.client_secret:
        raise ValueError("OAuth2 client secret is required when client ID is provided")
    
    if config.password.min_length < 8:
        raise ValueError("Minimum password length must be at least 8 characters")
    
    return True
