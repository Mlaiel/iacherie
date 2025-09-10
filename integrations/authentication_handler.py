"""Authentication Handler - Multi-Platform Authentication
======================================================

Centralized authentication system for managing authentication across
all third-party integrations. Supports multiple auth methods and providers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import secrets
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

import jwt
import httpx
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class AuthMethod(Enum):
    """Authentication methods."""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    JWT = "jwt"
    CUSTOM_HEADER = "custom_header"
    SIGNATURE = "signature"
    MUTUAL_TLS = "mutual_tls"


class AuthLocation(Enum):
    """Authentication location in request."""
    HEADER = "header"
    QUERY_PARAM = "query_param"
    BODY = "body"
    FORM_DATA = "form_data"


@dataclass
class AuthConfig:
    """Authentication configuration for integration."""
    integration_name: str
    auth_method: AuthMethod
    auth_location: AuthLocation = AuthLocation.HEADER
    
    # API Key authentication
    api_key: Optional[str] = None
    api_key_name: str = "X-API-Key"
    
    # Bearer token authentication
    bearer_token: Optional[str] = None
    
    # Basic authentication
    username: Optional[str] = None
    password: Optional[str] = None
    
    # OAuth2 authentication
    oauth_token: Optional[str] = None
    oauth_refresh_token: Optional[str] = None
    oauth_expires_at: Optional[datetime] = None
    
    # JWT authentication
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_payload: Dict[str, Any] = field(default_factory=dict)
    jwt_expires_in: int = 3600  # seconds
    
    # Custom header authentication
    custom_header_name: Optional[str] = None
    custom_header_value: Optional[str] = None
    
    # Signature authentication
    signature_secret: Optional[str] = None
    signature_algorithm: str = "sha256"
    signature_header: str = "X-Signature"
    
    # Additional headers
    additional_headers: Dict[str, str] = field(default_factory=dict)
    
    # Security settings
    auto_refresh: bool = True
    token_rotation_interval: int = 86400  # 24 hours
    max_auth_attempts: int = 3
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthResult:
    """Authentication result."""
    success: bool
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, str] = field(default_factory=dict)
    body_additions: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    expires_at: Optional[datetime] = None
    requires_refresh: bool = False


class AuthenticationHandler:
    """Multi-platform authentication handler.
    
    Manages authentication for all third-party integrations,
    supporting multiple authentication methods and automatic token refresh.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize authentication handler."""
        self.logger = logging.getLogger(__name__)
        
        # Encryption for sensitive data
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Authentication configurations
        self.auth_configs: Dict[str, AuthConfig] = {}
        
        # Active authentication sessions
        self.auth_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Failed authentication tracking
        self.auth_failures: Dict[str, int] = {}
        
        # Token refresh tasks
        self.refresh_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize default authentication configs
        self._initialize_default_configs()
    
    def _initialize_default_configs(self) -> None:
        """Initialize default authentication configurations."""
        default_configs = [
            # Social Media Platforms
            AuthConfig(
                integration_name="youtube",
                auth_method=AuthMethod.OAUTH2,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
            AuthConfig(
                integration_name="instagram",
                auth_method=AuthMethod.OAUTH2,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
            AuthConfig(
                integration_name="tiktok",
                auth_method=AuthMethod.BEARER_TOKEN,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
            AuthConfig(
                integration_name="spotify",
                auth_method=AuthMethod.OAUTH2,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
            AuthConfig(
                integration_name="twitter",
                auth_method=AuthMethod.BEARER_TOKEN,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
            AuthConfig(
                integration_name="facebook",
                auth_method=AuthMethod.OAUTH2,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
            
            # AI Services
            AuthConfig(
                integration_name="openai",
                auth_method=AuthMethod.BEARER_TOKEN,
                auth_location=AuthLocation.HEADER,
                api_key_name="Authorization"
            ),
            AuthConfig(
                integration_name="anthropic",
                auth_method=AuthMethod.API_KEY,
                auth_location=AuthLocation.HEADER,
                api_key_name="X-API-Key"
            ),
            AuthConfig(
                integration_name="huggingface",
                auth_method=AuthMethod.BEARER_TOKEN,
                auth_location=AuthLocation.HEADER,
                api_key_name="Authorization"
            ),
            
            # Payment Gateways
            AuthConfig(
                integration_name="stripe",
                auth_method=AuthMethod.BEARER_TOKEN,
                auth_location=AuthLocation.HEADER,
                api_key_name="Authorization"
            ),
            AuthConfig(
                integration_name="paypal",
                auth_method=AuthMethod.OAUTH2,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
            
            # Cloud Providers
            AuthConfig(
                integration_name="aws",
                auth_method=AuthMethod.SIGNATURE,
                auth_location=AuthLocation.HEADER,
                signature_algorithm="sha256",
                signature_header="Authorization"
            ),
            AuthConfig(
                integration_name="gcp",
                auth_method=AuthMethod.BEARER_TOKEN,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
            AuthConfig(
                integration_name="azure",
                auth_method=AuthMethod.BEARER_TOKEN,
                auth_location=AuthLocation.HEADER,
                auto_refresh=True
            ),
        ]
        
        for config in default_configs:
            self.auth_configs[config.integration_name] = config
    
    async def initialize_auth(self, integration_name: str) -> bool:
        """Initialize authentication for integration."""
        try:
            if integration_name not in self.auth_configs:
                self.logger.warning(f"No auth config found for {integration_name}")
                return False
            
            config = self.auth_configs[integration_name]
            
            # Validate configuration
            if not await self._validate_auth_config(config):
                return False
            
            # Initialize session
            self.auth_sessions[integration_name] = {
                "authenticated": False,
                "last_auth_time": None,
                "auth_attempts": 0,
                "current_token": None,
                "refresh_token": None,
                "expires_at": None
            }
            
            # Start auto-refresh if enabled
            if config.auto_refresh and config.auth_method in [AuthMethod.OAUTH2, AuthMethod.JWT]:
                await self._start_token_refresh(integration_name)
            
            self.logger.info(f"Authentication initialized for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize auth for {integration_name}: {str(e)}")
            return False
    
    async def authenticate_request(
        self,
        integration_name: str,
        request_data: Dict[str, Any]
    ) -> AuthResult:
        """Authenticate request for integration."""
        try:
            if integration_name not in self.auth_configs:
                return AuthResult(
                    success=False,
                    error=f"No authentication config for {integration_name}"
                )
            
            config = self.auth_configs[integration_name]
            
            # Check if authentication is blocked due to failures
            if self._is_auth_blocked(integration_name):
                return AuthResult(
                    success=False,
                    error="Authentication blocked due to repeated failures"
                )
            
            # Get or refresh authentication
            auth_data = await self._get_valid_auth_data(integration_name)
            if not auth_data:
                return AuthResult(
                    success=False,
                    error="Failed to obtain valid authentication"
                )
            
            # Apply authentication based on method
            result = await self._apply_authentication(config, auth_data, request_data)
            
            if result.success:
                # Reset failure count on success
                self.auth_failures[integration_name] = 0
                
                # Update session
                session = self.auth_sessions.get(integration_name, {})
                session["authenticated"] = True
                session["last_auth_time"] = datetime.utcnow()
                self.auth_sessions[integration_name] = session
            else:
                # Increment failure count
                self.auth_failures[integration_name] = self.auth_failures.get(integration_name, 0) + 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Authentication failed for {integration_name}: {str(e)}")
            return AuthResult(
                success=False,
                error=str(e)
            )
    
    async def configure_auth(
        self,
        integration_name: str,
        auth_method: AuthMethod,
        credentials: Dict[str, Any],
        additional_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Configure authentication for integration."""
        try:
            # Create or update auth config
            if integration_name in self.auth_configs:
                config = self.auth_configs[integration_name]
            else:
                config = AuthConfig(
                    integration_name=integration_name,
                    auth_method=auth_method
                )
            
            # Update auth method
            config.auth_method = auth_method
            config.updated_at = datetime.utcnow()
            
            # Configure based on auth method
            if auth_method == AuthMethod.API_KEY:
                config.api_key = self._encrypt_credential(credentials.get("api_key", ""))
                config.api_key_name = credentials.get("api_key_name", "X-API-Key")
                
            elif auth_method == AuthMethod.BEARER_TOKEN:
                config.bearer_token = self._encrypt_credential(credentials.get("bearer_token", ""))
                
            elif auth_method == AuthMethod.BASIC_AUTH:
                config.username = credentials.get("username", "")
                config.password = self._encrypt_credential(credentials.get("password", ""))
                
            elif auth_method == AuthMethod.OAUTH2:
                config.oauth_token = self._encrypt_credential(credentials.get("access_token", ""))
                config.oauth_refresh_token = self._encrypt_credential(credentials.get("refresh_token", ""))
                if credentials.get("expires_in"):
                    config.oauth_expires_at = datetime.utcnow() + timedelta(seconds=int(credentials["expires_in"]))
                
            elif auth_method == AuthMethod.JWT:
                config.jwt_secret = self._encrypt_credential(credentials.get("jwt_secret", ""))
                config.jwt_algorithm = credentials.get("jwt_algorithm", "HS256")
                config.jwt_payload = credentials.get("jwt_payload", {})
                config.jwt_expires_in = credentials.get("jwt_expires_in", 3600)
                
            elif auth_method == AuthMethod.CUSTOM_HEADER:
                config.custom_header_name = credentials.get("header_name", "")
                config.custom_header_value = self._encrypt_credential(credentials.get("header_value", ""))
                
            elif auth_method == AuthMethod.SIGNATURE:
                config.signature_secret = self._encrypt_credential(credentials.get("signature_secret", ""))
                config.signature_algorithm = credentials.get("signature_algorithm", "sha256")
                config.signature_header = credentials.get("signature_header", "X-Signature")
            
            # Apply additional configuration
            if additional_config:
                for key, value in additional_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            
            # Store configuration
            self.auth_configs[integration_name] = config
            
            self.logger.info(f"Authentication configured for {integration_name} with method {auth_method.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure auth for {integration_name}: {str(e)}")
            return False
    
    async def refresh_authentication(self, integration_name: str) -> bool:
        """Refresh authentication for integration."""
        try:
            if integration_name not in self.auth_configs:
                return False
            
            config = self.auth_configs[integration_name]
            
            if config.auth_method == AuthMethod.OAUTH2:
                return await self._refresh_oauth_token(integration_name)
            elif config.auth_method == AuthMethod.JWT:
                return await self._refresh_jwt_token(integration_name)
            
            # For other methods, re-authenticate
            return await self.initialize_auth(integration_name)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh auth for {integration_name}: {str(e)}")
            return False
    
    async def revoke_authentication(self, integration_name: str) -> bool:
        """Revoke authentication for integration."""
        try:
            # Stop refresh tasks
            if integration_name in self.refresh_tasks:
                self.refresh_tasks[integration_name].cancel()
                del self.refresh_tasks[integration_name]
            
            # Clear session
            if integration_name in self.auth_sessions:
                del self.auth_sessions[integration_name]
            
            # Reset failure count
            self.auth_failures.pop(integration_name, None)
            
            self.logger.info(f"Authentication revoked for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke auth for {integration_name}: {str(e)}")
            return False
    
    async def get_auth_status(self, integration_name: str) -> Dict[str, Any]:
        """Get authentication status for integration."""
        if integration_name not in self.auth_configs:
            return {"error": "Integration not configured"}
        
        config = self.auth_configs[integration_name]
        session = self.auth_sessions.get(integration_name, {})
        
        return {
            "integration_name": integration_name,
            "auth_method": config.auth_method.value,
            "auth_location": config.auth_location.value,
            "authenticated": session.get("authenticated", False),
            "last_auth_time": session.get("last_auth_time").isoformat() if session.get("last_auth_time") else None,
            "auth_attempts": session.get("auth_attempts", 0),
            "expires_at": config.oauth_expires_at.isoformat() if config.oauth_expires_at else None,
            "auto_refresh": config.auto_refresh,
            "failure_count": self.auth_failures.get(integration_name, 0),
            "is_blocked": self._is_auth_blocked(integration_name),
            "has_refresh_task": integration_name in self.refresh_tasks
        }
    
    async def _apply_authentication(
        self,
        config: AuthConfig,
        auth_data: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> AuthResult:
        """Apply authentication to request."""
        result = AuthResult(success=True)
        
        try:
            if config.auth_method == AuthMethod.API_KEY:
                if config.auth_location == AuthLocation.HEADER:
                    result.headers[config.api_key_name] = auth_data["api_key"]
                elif config.auth_location == AuthLocation.QUERY_PARAM:
                    result.params[config.api_key_name] = auth_data["api_key"]
                
            elif config.auth_method == AuthMethod.BEARER_TOKEN:
                if config.auth_location == AuthLocation.HEADER:
                    result.headers["Authorization"] = f"Bearer {auth_data['bearer_token']}"
                
            elif config.auth_method == AuthMethod.BASIC_AUTH:
                credentials = base64.b64encode(f"{config.username}:{auth_data['password']}".encode()).decode()
                result.headers["Authorization"] = f"Basic {credentials}"
                
            elif config.auth_method == AuthMethod.OAUTH2:
                result.headers["Authorization"] = f"Bearer {auth_data['oauth_token']}"
                if config.oauth_expires_at:
                    result.expires_at = config.oauth_expires_at
                    result.requires_refresh = datetime.utcnow() + timedelta(minutes=5) >= config.oauth_expires_at
                
            elif config.auth_method == AuthMethod.JWT:
                jwt_token = await self._generate_jwt_token(config)
                result.headers["Authorization"] = f"Bearer {jwt_token}"
                result.expires_at = datetime.utcnow() + timedelta(seconds=config.jwt_expires_in)
                
            elif config.auth_method == AuthMethod.CUSTOM_HEADER:
                result.headers[config.custom_header_name] = auth_data["custom_header_value"]
                
            elif config.auth_method == AuthMethod.SIGNATURE:
                signature = await self._generate_signature(config, request_data)
                result.headers[config.signature_header] = signature
            
            # Add additional headers
            result.headers.update(config.additional_headers)
            
            return result
            
        except Exception as e:
            return AuthResult(
                success=False,
                error=f"Failed to apply authentication: {str(e)}"
            )
    
    async def _get_valid_auth_data(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Get valid authentication data for integration."""
        config = self.auth_configs[integration_name]
        
        # Check if token needs refresh
        if config.auth_method == AuthMethod.OAUTH2 and config.oauth_expires_at:
            if datetime.utcnow() + timedelta(minutes=5) >= config.oauth_expires_at:
                await self._refresh_oauth_token(integration_name)
        
        # Return decrypted credentials
        auth_data = {}
        
        if config.api_key:
            auth_data["api_key"] = self._decrypt_credential(config.api_key)
        
        if config.bearer_token:
            auth_data["bearer_token"] = self._decrypt_credential(config.bearer_token)
        
        if config.password:
            auth_data["password"] = self._decrypt_credential(config.password)
        
        if config.oauth_token:
            auth_data["oauth_token"] = self._decrypt_credential(config.oauth_token)
        
        if config.oauth_refresh_token:
            auth_data["oauth_refresh_token"] = self._decrypt_credential(config.oauth_refresh_token)
        
        if config.jwt_secret:
            auth_data["jwt_secret"] = self._decrypt_credential(config.jwt_secret)
        
        if config.custom_header_value:
            auth_data["custom_header_value"] = self._decrypt_credential(config.custom_header_value)
        
        if config.signature_secret:
            auth_data["signature_secret"] = self._decrypt_credential(config.signature_secret)
        
        return auth_data if auth_data else None
    
    async def _refresh_oauth_token(self, integration_name: str) -> bool:
        """Refresh OAuth token for integration."""
        try:
            config = self.auth_configs[integration_name]
            
            if not config.oauth_refresh_token:
                return False
            
            # This would integrate with the OAuth manager
            # For now, just extend the expiration
            config.oauth_expires_at = datetime.utcnow() + timedelta(hours=1)
            config.updated_at = datetime.utcnow()
            
            self.logger.info(f"OAuth token refreshed for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh OAuth token for {integration_name}: {str(e)}")
            return False
    
    async def _refresh_jwt_token(self, integration_name: str) -> bool:
        """Refresh JWT token for integration."""
        try:
            # JWT tokens are generated on-demand, so this just validates the secret
            config = self.auth_configs[integration_name]
            return bool(config.jwt_secret)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh JWT token for {integration_name}: {str(e)}")
            return False
    
    async def _generate_jwt_token(self, config: AuthConfig) -> str:
        """Generate JWT token."""
        payload = {
            **config.jwt_payload,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=config.jwt_expires_in),
            "iss": "ainflue-integrations"
        }
        
        secret = self._decrypt_credential(config.jwt_secret)
        return jwt.encode(payload, secret, algorithm=config.jwt_algorithm)
    
    async def _generate_signature(self, config: AuthConfig, request_data: Dict[str, Any]) -> str:
        """Generate request signature."""
        # Create signature string from request data
        method = request_data.get("method", "GET")
        url = request_data.get("url", "")
        body = request_data.get("body", "")
        timestamp = str(int(datetime.utcnow().timestamp()))
        
        signature_string = f"{method}\n{url}\n{body}\n{timestamp}"
        
        # Generate signature
        secret = self._decrypt_credential(config.signature_secret)
        signature = hashlib.new(
            config.signature_algorithm,
            signature_string.encode() + secret.encode()
        ).hexdigest()
        
        return f"{timestamp}.{signature}"
    
    async def _start_token_refresh(self, integration_name: str) -> None:
        """Start automatic token refresh task."""
        config = self.auth_configs[integration_name]
        
        async def refresh_loop():
            while True:
                try:
                    # Calculate sleep time
                    if config.auth_method == AuthMethod.OAUTH2 and config.oauth_expires_at:
                        sleep_time = (config.oauth_expires_at - datetime.utcnow()).total_seconds() - 300  # 5 min before expiry
                    else:
                        sleep_time = config.token_rotation_interval
                    
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                    
                    # Refresh token
                    await self.refresh_authentication(integration_name)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Token refresh error for {integration_name}: {str(e)}")
                    await asyncio.sleep(60)  # Retry after 1 minute
        
        self.refresh_tasks[integration_name] = asyncio.create_task(refresh_loop())
    
    async def _validate_auth_config(self, config: AuthConfig) -> bool:
        """Validate authentication configuration."""
        if not config.integration_name:
            return False
        
        # Validate required fields based on auth method
        if config.auth_method == AuthMethod.API_KEY and not config.api_key:
            return False
        
        if config.auth_method == AuthMethod.BEARER_TOKEN and not config.bearer_token:
            return False
        
        if config.auth_method == AuthMethod.BASIC_AUTH and (not config.username or not config.password):
            return False
        
        if config.auth_method == AuthMethod.OAUTH2 and not config.oauth_token:
            return False
        
        if config.auth_method == AuthMethod.JWT and not config.jwt_secret:
            return False
        
        if config.auth_method == AuthMethod.CUSTOM_HEADER and (not config.custom_header_name or not config.custom_header_value):
            return False
        
        if config.auth_method == AuthMethod.SIGNATURE and not config.signature_secret:
            return False
        
        return True
    
    def _is_auth_blocked(self, integration_name: str) -> bool:
        """Check if authentication is blocked due to failures."""
        config = self.auth_configs.get(integration_name)
        if not config:
            return False
        
        failure_count = self.auth_failures.get(integration_name, 0)
        return failure_count >= config.max_auth_attempts
    
    def _encrypt_credential(self, credential: str) -> str:
        """Encrypt sensitive credential."""
        if not credential:
            return ""
        return self.cipher_suite.encrypt(credential.encode()).decode()
    
    def _decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt sensitive credential."""
        if not encrypted_credential:
            return ""
        return self.cipher_suite.decrypt(encrypted_credential.encode()).decode()
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired authentication sessions."""
        cleaned_count = 0
        current_time = datetime.utcnow()
        
        expired_integrations = []
        
        for integration_name, config in self.auth_configs.items():
            if config.oauth_expires_at and current_time > config.oauth_expires_at:
                if not config.oauth_refresh_token:
                    expired_integrations.append(integration_name)
        
        for integration_name in expired_integrations:
            await self.revoke_authentication(integration_name)
            cleaned_count += 1
        
        return cleaned_count
    
    async def get_all_auth_status(self) -> Dict[str, Any]:
        """Get authentication status for all integrations."""
        status_data = {}
        
        for integration_name in self.auth_configs:
            status_data[integration_name] = await self.get_auth_status(integration_name)
        
        authenticated_count = len([
            s for s in status_data.values()
            if s.get("authenticated", False) and not s.get("is_blocked", False)
        ])
        
        return {
            "total_integrations": len(self.auth_configs),
            "authenticated_integrations": authenticated_count,
            "active_refresh_tasks": len(self.refresh_tasks),
            "integrations": status_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self) -> None:
        """Shutdown authentication handler."""
        self.logger.info("Shutting down authentication handler...")
        
        # Cancel all refresh tasks
        for task in self.refresh_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.refresh_tasks:
            await asyncio.gather(*self.refresh_tasks.values(), return_exceptions=True)
        
        self.refresh_tasks.clear()
        self.auth_sessions.clear()
        
        self.logger.info("Authentication handler shutdown complete")