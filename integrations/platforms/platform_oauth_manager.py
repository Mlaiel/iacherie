"""Platform OAuth Manager
======================

Multi-platform OAuth authentication and token management system.
Handles OAuth 2.0 flows for all supported platforms with secure token storage.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
import logging
import secrets
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from urllib.parse import urlencode, parse_qs, urlparse
import hashlib
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


@dataclass
class OAuthConfig:
    """
OAuth configuration for a platform"""
    platform: str
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    redirect_uri: str
    scopes: List[str]
    additional_params: Dict[str, str] = None


@dataclass
class OAuthTokens:
    """
OAuth tokens for a platform"""
    platform: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    scopes: List[str] = None
    raw_data: Dict[str, Any] = None


class PlatformOAuthManager:
    """Multi-platform OAuth authentication manager"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.session = None
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.oauth_states = {}  # Store CSRF state tokens
        
        # Platform OAuth configurations
        self.platform_configs = {
            "youtube": OAuthConfig(
                platform="youtube",
                client_id="",  # To be set by user
                client_secret="",  # To be set by user
                authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token",
                redirect_uri="",  # To be set by user
                scopes=[
                    "https://www.googleapis.com/auth/youtube.readonly",
                    "https://www.googleapis.com/auth/yt-analytics.readonly",
                    "https://www.googleapis.com/auth/youtube.force-ssl"
                ]
            ),
            "instagram": OAuthConfig(
                platform="instagram",
                client_id="",
                client_secret="",
                authorize_url="https://api.instagram.com/oauth/authorize",
                token_url="https://api.instagram.com/oauth/access_token",
                redirect_uri="",
                scopes=[
                    "user_profile",
                    "user_media",
                    "instagram_business_basic",
                    "instagram_business_manage_messages",
                    "instagram_business_manage_comments",
                    "instagram_business_content_publish"
                ]
            ),
            "tiktok": OAuthConfig(
                platform="tiktok",
                client_id="",
                client_secret="",
                authorize_url="https://www.tiktok.com/auth/authorize/",
                token_url="https://open-api.tiktok.com/oauth/access_token/",
                redirect_uri="",
                scopes=[
                    "user.info.basic",
                    "user.info.profile",
                    "user.info.stats",
                    "video.list",
                    "video.upload"
                ]
            ),
            "spotify": OAuthConfig(
                platform="spotify",
                client_id="",
                client_secret="",
                authorize_url="https://accounts.spotify.com/authorize",
                token_url="https://accounts.spotify.com/api/token",
                redirect_uri="",
                scopes=[
                    "user-read-private",
                    "user-read-email", 
                    "user-top-read",
                    "user-read-recently-played",
                    "playlist-read-private",
                    "playlist-read-collaborative"
                ]
            ),
            "facebook": OAuthConfig(
                platform="facebook",
                client_id="",
                client_secret="",
                authorize_url="https://www.facebook.com/v18.0/dialog/oauth",
                token_url="https://graph.facebook.com/v18.0/oauth/access_token",
                redirect_uri="",
                scopes=[
                    "pages_read_engagement",
                    "pages_read_user_content",
                    "pages_manage_posts",
                    "business_management",
                    "instagram_basic",
                    "instagram_content_publish"
                ]
            ),
            "twitter": OAuthConfig(
                platform="twitter",
                client_id="",
                client_secret="",
                authorize_url="https://twitter.com/i/oauth2/authorize",
                token_url="https://api.twitter.com/2/oauth2/token",
                redirect_uri="",
                scopes=[
                    "tweet.read",
                    "tweet.write",
                    "users.read",
                    "follows.read",
                    "follows.write",
                    "offline.access"
                ],
                additional_params={"code_challenge_method": "S256"}
            )
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def configure_platform(
        self,
        platform: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: Optional[List[str]] = None
    ):
        """
Configure OAuth settings for a platform"""
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
            
        config = self.platform_configs[platform]
        config.client_id = client_id
        config.client_secret = client_secret
        config.redirect_uri = redirect_uri
        
        if scopes:
            config.scopes = scopes
            
        logger.info(f"Configured OAuth for platform: {platform}")
        
    def generate_authorization_url(
        self,
        platform: str,
        user_id: str,
        state: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL
        
        Args:
            platform: Platform name
            user_id: User identifier
            state: Optional state parameter (generated if not provided)
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
            
        config = self.platform_configs[platform]
        
        if not config.client_id:
            raise ValueError(f"OAuth not configured for platform: {platform}")
            
        # Generate state for CSRF protection
        if not state:
            state = secrets.token_urlsafe(32)
            
        # Store state for validation
        self.oauth_states[state] = {
            "platform": platform,
            "user_id": user_id,
            "created_at": datetime.now()
        }
        
        # Build authorization parameters
        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(config.scopes),
            "state": state,
            "response_type": "code"
        }
        
        # Platform-specific parameters
        if platform == "twitter":
            # Twitter requires PKCE
            code_verifier = secrets.token_urlsafe(32)
            code_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).decode().rstrip("=")
            
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
            
            # Store code verifier for token exchange
            self.oauth_states[state]["code_verifier"] = code_verifier
            
        elif platform == "instagram":
            params["response_type"] = "code"
            
        elif platform == "tiktok":
            params["response_type"] = "code"
            
        # Add additional platform-specific parameters
        if config.additional_params:
            params.update(config.additional_params)
            
        authorization_url = f"{config.authorize_url}?{urlencode(params)}"
        
        logger.info(f"Generated OAuth URL for {platform}: {authorization_url[:100]}...")
        
        return authorization_url, state
        
    async def exchange_code_for_tokens(
        self,
        platform: str,
        authorization_code: str,
        state: str
    ) -> OAuthTokens:
        """
        Exchange authorization code for access tokens
        
        Args:
            platform: Platform name
            authorization_code: Authorization code from callback
            state: State parameter for CSRF validation
            
        Returns:
            OAuthTokens object with access tokens
        """
        # Validate state
        if state not in self.oauth_states:
            raise ValueError("Invalid or expired OAuth state")
            
        state_data = self.oauth_states[state]
        if state_data["platform"] != platform:
            raise ValueError("Platform mismatch in OAuth state")
            
        # Clean up state
        del self.oauth_states[state]
        
        config = self.platform_configs[platform]
        
        # Prepare token request
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": authorization_code,
            "redirect_uri": config.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        # Platform-specific parameters
        if platform == "twitter" and "code_verifier" in state_data:
            data["code_verifier"] = state_data["code_verifier"]
            
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        # Some platforms require different authentication methods
        if platform == "spotify":
            # Spotify uses Basic auth for client credentials
            auth_string = f"{config.client_id}:{config.client_secret}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            headers["Authorization"] = f"Basic {auth_bytes}"
            # Remove client_secret from data for Spotify
            del data["client_secret"]
            
        try:
            async with self.session.post(
                config.token_url,
                data=data,
                headers=headers
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Token exchange failed for {platform}: {error_text}")
                    raise ValueError(f"Token exchange failed: {response.status}")
                    
                token_data = await response.json()
                
                # Parse response based on platform
                access_token = token_data.get("access_token")
                if not access_token:
                    raise ValueError("No access token in response")
                    
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in")
                token_type = token_data.get("token_type", "Bearer")
                
                # Calculate expiration time
                expires_at = None
                if expires_in:
                    expires_at = datetime.now() + timedelta(seconds=int(expires_in))
                    
                # Extract granted scopes
                granted_scopes = []
                if "scope" in token_data:
                    scope_string = token_data["scope"]
                    if isinstance(scope_string, str):
                        granted_scopes = scope_string.split()
                    elif isinstance(scope_string, list):
                        granted_scopes = scope_string
                        
                tokens = OAuthTokens(
                    platform=platform,
                    user_id=state_data["user_id"],
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type=token_type,
                    expires_at=expires_at,
                    scopes=granted_scopes,
                    raw_data=token_data
                )
                
                logger.info(f"Successfully obtained tokens for {platform}")
                return tokens
                
        except Exception as e:
            logger.error(f"Error exchanging code for tokens ({platform}): {e}")
            raise
            
    async def refresh_access_token(
        self,
        platform: str,
        refresh_token: str
    ) -> OAuthTokens:
        """
        Refresh access token using refresh token
        
        Args:
            platform: Platform name
            refresh_token: Refresh token
            
        Returns:
            New OAuthTokens with refreshed access token
        """
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
            
        config = self.platform_configs[platform]
        
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        # Platform-specific authentication
        if platform == "spotify":
            auth_string = f"{config.client_id}:{config.client_secret}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            headers["Authorization"] = f"Basic {auth_bytes}"
            del data["client_secret"]
            
        try:
            async with self.session.post(
                config.token_url,
                data=data,
                headers=headers
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Token refresh failed for {platform}: {error_text}")
                    raise ValueError(f"Token refresh failed: {response.status}")
                    
                token_data = await response.json()
                
                access_token = token_data.get("access_token")
                if not access_token:
                    raise ValueError("No access token in refresh response")
                    
                # Use new refresh token if provided, otherwise keep the old one
                new_refresh_token = token_data.get("refresh_token", refresh_token)
                expires_in = token_data.get("expires_in")
                token_type = token_data.get("token_type", "Bearer")
                
                expires_at = None
                if expires_in:
                    expires_at = datetime.now() + timedelta(seconds=int(expires_in))
                    
                tokens = OAuthTokens(
                    platform=platform,
                    user_id="",  # Will be set by caller
                    access_token=access_token,
                    refresh_token=new_refresh_token,
                    token_type=token_type,
                    expires_at=expires_at,
                    raw_data=token_data
                )
                
                logger.info(f"Successfully refreshed tokens for {platform}")
                return tokens
                
        except Exception as e:
            logger.error(f"Error refreshing tokens ({platform}): {e}")
            raise
            
    def encrypt_tokens(self, tokens: OAuthTokens) -> str:
        """Encrypt tokens for secure storage"""
        tokens_dict = asdict(tokens)
        
        # Convert datetime to ISO format for JSON serialization
        if tokens_dict["expires_at"]:
            tokens_dict["expires_at"] = tokens_dict["expires_at"].isoformat()
            
        tokens_json = json.dumps(tokens_dict)
        encrypted_data = self.cipher_suite.encrypt(tokens_json.encode())
        return base64.b64encode(encrypted_data).decode()
        
    def decrypt_tokens(self, encrypted_tokens: str) -> OAuthTokens:
        """Decrypt tokens from secure storage"""
        try:
            encrypted_data = base64.b64decode(encrypted_tokens.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            tokens_dict = json.loads(decrypted_data.decode())
            
            # Convert ISO format back to datetime
            if tokens_dict["expires_at"]:
                tokens_dict["expires_at"] = datetime.fromisoformat(tokens_dict["expires_at"])
                
            return OAuthTokens(**tokens_dict)
            
        except Exception as e:
            logger.error(f"Error decrypting tokens: {e}")
            raise ValueError("Invalid or corrupted token data")
            
    async def validate_tokens(self, tokens: OAuthTokens) -> bool:
        """
        Validate if tokens are still valid
        
        Args:
            tokens: OAuthTokens to validate
            
        Returns:
            True if tokens are valid, False otherwise
        """
        # Check expiration
        if tokens.expires_at and datetime.now() >= tokens.expires_at:
            logger.info(f"Tokens expired for {tokens.platform}")
            return False
            
        # Make a test API call to validate tokens
        try:
            headers = {
                "Authorization": f"{tokens.token_type} {tokens.access_token}"
            }
            
            # Platform-specific validation endpoints
            validation_urls = {
                "youtube": "https://www.googleapis.com/oauth2/v1/tokeninfo",
                "instagram": "https://graph.instagram.com/me",
                "spotify": "https://api.spotify.com/v1/me",
                "facebook": "https://graph.facebook.com/me",
                "twitter": "https://api.twitter.com/2/users/me",
                "tiktok": "https://open-api.tiktok.com/oauth/userinfo/"
            }
            
            validation_url = validation_urls.get(tokens.platform)
            if not validation_url:
                logger.warning(f"No validation URL for platform: {tokens.platform}")
                return True  # Assume valid if we can't validate
                
            async with self.session.get(validation_url, headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error validating tokens for {tokens.platform}: {e}")
            return False
            
    def cleanup_expired_states(self, max_age_minutes: int = 30):
        """Clean up expired OAuth states"""
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        
        expired_states = [
            state for state, data in self.oauth_states.items()
            if data["created_at"] < cutoff_time
        ]
        
        for state in expired_states:
            del self.oauth_states[state]
            
        if expired_states:
            logger.info(f"Cleaned up {len(expired_states)} expired OAuth states")
            
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return list(self.platform_configs.keys())
        
    def get_platform_scopes(self, platform: str) -> List[str]:
        """
Get default scopes for a platform"""
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
            
        return self.platform_configs[platform].scopes.copy()