"""Authentication Manager for Ainflue SDK

Enterprise-grade authentication with multi-expert design:
- Sécurité: Secure token storage and rotation
- Backend Senior: Robust authentication flows
- DevOps: Token monitoring and health checks
- Lead Dev IA: Intelligent authentication strategies

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import json
import logging
import hashlib
import secrets
import base64
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
import threading
import os
from pathlib import Path

from .exceptions import (
    AuthenticationError, AuthorizationError, TokenExpiredError,
    TokenInvalidError, ConfigurationError, ValidationError
)


class SecureTokenStorage:
    """Secure token storage with encryption (Sécurité expertise)"""
    
    def __init__(self, storage_path -> None: Optional[str] = None) -> None:
        self.storage_path = storage_path or os.path.join(
            Path.home(), '.ainflue', 'tokens.dat'
        )
        self._ensure_storage_dir()
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def _ensure_storage_dir(self) -> None:
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Set restrictive permissions on directory (Unix only)
        if os.name != 'nt':
            os.chmod(os.path.dirname(self.storage_path), 0o700)
    
    def _encrypt_data(self, data: str, key: str) -> str:
        """Simple XOR encryption (for basic obfuscation)"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        data_bytes = data.encode()
        
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_data(self, encrypted_data: str, key: str) -> str:
        """Simple XOR decryption"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return decrypted.decode()
    
    def store_token(self, token_id: str, token_data: Dict[str, Any]) -> bool:
        """Store token securely"""
        try:
            with self._lock:
                # Load existing tokens
                tokens = self._load_tokens()
                
                # Add new token
                tokens[token_id] = {
                    **token_data,
                    'stored_at': datetime.utcnow().isoformat()
                }
                
                # Save tokens
                return self._save_tokens(tokens)
        
        except Exception as e:
            self.logger.error(f"Failed to store token: {str(e)}")
            return False
    
    def get_token(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve token securely"""
        try:
            with self._lock:
                tokens = self._load_tokens()
                return tokens.get(token_id)
        
        except Exception as e:
            self.logger.error(f"Failed to retrieve token: {str(e)}")
            return None
    
    def delete_token(self, token_id: str) -> bool:
        """Delete token securely"""
        try:
            with self._lock:
                tokens = self._load_tokens()
                
                if token_id in tokens:
                    del tokens[token_id]
                    return self._save_tokens(tokens)
                
                return True
        
        except Exception as e:
            self.logger.error(f"Failed to delete token: {str(e)}")
            return False
    
    def list_tokens(self) -> List[str]:
        """List stored token IDs"""
        try:
            with self._lock:
                tokens = self._load_tokens()
                return list(tokens.keys())
        
        except Exception as e:
            self.logger.error(f"Failed to list tokens: {str(e)}")
            return []
    
    def _load_tokens(self) -> Dict[str, Any]:
        """Load tokens from storage"""
        if not os.path.exists(self.storage_path):
            return {}
        
        try:
            with open(self.storage_path, 'r') as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return {}
            
            # Use machine-specific key for decryption
            key = self._get_machine_key()
            decrypted_data = self._decrypt_data(encrypted_data, key)
            
            return json.loads(decrypted_data)
        
        except Exception as e:
            self.logger.warning(f"Failed to load tokens, starting fresh: {str(e)}")
            return {}
    
    def _save_tokens(self, tokens: Dict[str, Any]) -> bool:
        """Save tokens to storage"""
        try:
            # Use machine-specific key for encryption
            key = self._get_machine_key()
            data = json.dumps(tokens, indent=2)
            encrypted_data = self._encrypt_data(data, key)
            
            # Write to temporary file first, then move (atomic operation)
            temp_path = f"{self.storage_path}.tmp"
            
            with open(temp_path, 'w') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions (Unix only)
            if os.name != 'nt':
                os.chmod(temp_path, 0o600)
            
            # Atomic move
            os.replace(temp_path, self.storage_path)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save tokens: {str(e)}")
            return False
    
    def _get_machine_key(self) -> str:
        """Generate machine-specific encryption key"""
        # Use hostname and user as base for key
        import socket
        import getpass
        
        machine_info = f"{socket.gethostname()}-{getpass.getuser()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()


class TokenValidator:
    """JWT and token validation utilities"""
    
    @staticmethod
    def is_jwt_expired(token: str) -> bool:
        """Check if JWT token is expired"""
        try:
            # Parse JWT without verification (just to check expiry)
            parts = token.split('.')
            if len(parts) != 3:
                return True
            
            # Decode payload
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            
            decoded = json.loads(base64.b64decode(payload))
            
            # Check expiry
            exp = decoded.get('exp')
            if exp:
                return datetime.utcnow().timestamp() > exp
            
            return False
        
        except Exception:
            return True
    
    @staticmethod
    def extract_token_claims(token: str) -> Dict[str, Any]:
        """Extract claims from JWT token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise TokenInvalidError("Invalid JWT format")
            
            # Decode payload
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            
            return json.loads(base64.b64decode(payload))
        
        except Exception as e:
            raise TokenInvalidError(f"Failed to extract token claims: {str(e)}")
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate API key format"""
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Basic validation - should be at least 32 characters
        if len(api_key) < 32:
            return False
        
        # Should contain only alphanumeric characters and some symbols
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', api_key):
            return False
        
        return True


class AuthenticationManager:
    """Comprehensive authentication management
    
    Handles multiple authentication methods:
    - API Keys
    - JWT tokens
    - OAuth 2.0 flows
    - Service-to-service authentication
    """
    
    def __init__(
        self,
        storage_path -> None: Optional[str] = None,
        auto_refresh -> None: bool = True,
        refresh_threshold -> None: int = 300  # 5 minutes before expiry
    ) -> None:
        self.storage = SecureTokenStorage(storage_path)
        self.auto_refresh = auto_refresh
        self.refresh_threshold = refresh_threshold
        self.logger = logging.getLogger(__name__)
        
        # Authentication state
        self._current_token: Optional[Dict[str, Any]] = None
        self._auth_callbacks: List[Callable] = []
        self._lock = threading.Lock()
        
        # Authentication methods
        self._auth_methods = {
            'api_key': self._authenticate_api_key,
            'jwt': self._authenticate_jwt,
            'oauth': self._authenticate_oauth,
            'service': self._authenticate_service
        }
    
    def add_auth_callback(self, callback -> None: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add callback for authentication events"""
        self._auth_callbacks.append(callback)
    
    def _notify_auth_event(self, event_type -> None: str, data -> None: Dict[str, Any]) -> None:
        """Notify authentication event callbacks"""
        for callback in self._auth_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                self.logger.warning(f"Auth callback failed: {str(e)}")
    
    def authenticate_with_api_key(self, api_key: str) -> Dict[str, Any]:
        """Authenticate using API key"""
        if not TokenValidator.validate_api_key_format(api_key):
            raise AuthenticationError("Invalid API key format")
        
        return self._authenticate_api_key(api_key)
    
    def authenticate_with_jwt(self, jwt_token: str) -> Dict[str, Any]:
        """Authenticate using JWT token"""
        if TokenValidator.is_jwt_expired(jwt_token):
            raise TokenExpiredError("JWT token has expired")
        
        return self._authenticate_jwt(jwt_token)
    
    def authenticate_with_oauth(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start OAuth 2.0 authentication flow"""
        return self._authenticate_oauth(client_id, client_secret, redirect_uri, scope)
    
    def authenticate_with_service_account(
        self,
        service_key: str,
        service_id: str
    ) -> Dict[str, Any]:
        """Authenticate using service account"""
        return self._authenticate_service(service_key, service_id)
    
    def get_current_token(self) -> Optional[Dict[str, Any]]:
        """Get current authentication token"""
        with self._lock:
            if self._current_token and self._should_refresh_token():
                self._refresh_current_token()
            
            return self._current_token
    
    def get_auth_header(self) -> Dict[str, str]:
        """Get authentication header for requests"""
        token = self.get_current_token()
        
        if not token:
            raise AuthenticationError("No valid authentication token available")
        
        auth_type = token.get('type', 'Bearer')
        auth_value = token.get('access_token') or token.get('api_key')
        
        if not auth_value:
            raise AuthenticationError("No authentication value in token")
        
        return {'Authorization': f'{auth_type} {auth_value}'}
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        try:
            token = self.get_current_token()
            return token is not None and not self._is_token_expired(token)
        except:
            return False
    
    def logout(self) -> bool:
        """Logout and clear authentication"""
        with self._lock:
            if self._current_token:
                token_id = self._current_token.get('id')
                if token_id:
                    self.storage.delete_token(token_id)
                
                self._notify_auth_event('logout', {'token_id': token_id})
                self._current_token = None
                
                return True
            
            return False
    
    def refresh_token(self) -> Dict[str, Any]:
        """Refresh current authentication token"""
        with self._lock:
            return self._refresh_current_token()
    
    def _authenticate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Internal API key authentication"""
        # Validate API key format
        if not TokenValidator.validate_api_key_format(api_key):
            raise AuthenticationError("Invalid API key format")
        
        # Create token data
        token_id = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        token_data = {
            'id': token_id,
            'type': 'Bearer',
            'api_key': api_key,
            'method': 'api_key',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': None  # API keys don't expire
        }
        
        # Store token
        self.storage.store_token(token_id, token_data)
        
        with self._lock:
            self._current_token = token_data
        
        self._notify_auth_event('authenticated', {'method': 'api_key', 'token_id': token_id})
        
        return token_data
    
    def _authenticate_jwt(self, jwt_token: str) -> Dict[str, Any]:
        """Internal JWT authentication"""
        try:
            claims = TokenValidator.extract_token_claims(jwt_token)
        except Exception as e:
            raise TokenInvalidError(f"Invalid JWT token: {str(e)}")
        
        # Create token data
        token_id = hashlib.sha256(jwt_token.encode()).hexdigest()[:16]
        token_data = {
            'id': token_id,
            'type': 'Bearer',
            'access_token': jwt_token,
            'method': 'jwt',
            'claims': claims,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': datetime.fromtimestamp(claims.get('exp', 0)).isoformat() if claims.get('exp') else None
        }
        
        # Store token
        self.storage.store_token(token_id, token_data)
        
        with self._lock:
            self._current_token = token_data
        
        self._notify_auth_event('authenticated', {'method': 'jwt', 'token_id': token_id})
        
        return token_data
    
    def _authenticate_oauth(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """Internal OAuth 2.0 authentication"""
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        # OAuth flow would typically redirect to authorization server
        # For this implementation, we'll return the authorization URL
        
        auth_url = f"https://auth.ainflue.com/oauth/authorize"
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': scope or 'read write'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        authorization_url = f"{auth_url}?{query_string}"
        
        # Store OAuth state for validation
        oauth_data = {
            'id': f"oauth_{state}",
            'type': 'OAuth',
            'method': 'oauth',
            'client_id': client_id,
            'state': state,
            'redirect_uri': redirect_uri,
            'authorization_url': authorization_url,
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.storage.store_token(f"oauth_{state}", oauth_data)
        
        self._notify_auth_event('oauth_started', {'state': state})
        
        return oauth_data
    
    def _authenticate_service(self, service_key: str, service_id: str) -> Dict[str, Any]:
        """Internal service account authentication"""
        # Validate service credentials
        if not service_key or not service_id:
            raise AuthenticationError("Service key and ID are required")
        
        # Create service token
        token_id = f"service_{service_id}"
        token_data = {
            'id': token_id,
            'type': 'Bearer',
            'service_key': service_key,
            'service_id': service_id,
            'method': 'service',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        # Store token
        self.storage.store_token(token_id, token_data)
        
        with self._lock:
            self._current_token = token_data
        
        self._notify_auth_event('authenticated', {'method': 'service', 'service_id': service_id})
        
        return token_data
    
    def _should_refresh_token(self) -> bool:
        """Check if token should be refreshed"""
        if not self.auto_refresh or not self._current_token:
            return False
        
        expires_at = self._current_token.get('expires_at')
        if not expires_at:
            return False
        
        try:
            expiry = datetime.fromisoformat(expires_at)
            now = datetime.utcnow()
            
            # Refresh if within threshold of expiry
            return (expiry - now).total_seconds() < self.refresh_threshold
        except:
            return False
    
    def _is_token_expired(self, token: Dict[str, Any]) -> bool:
        """Check if token is expired"""
        expires_at = token.get('expires_at')
        if not expires_at:
            return False
        
        try:
            expiry = datetime.fromisoformat(expires_at)
            return datetime.utcnow() > expiry
        except:
            return True
    
    def _refresh_current_token(self) -> Dict[str, Any]:
        """Refresh the current token"""
        if not self._current_token:
            raise AuthenticationError("No token to refresh")
        
        method = self._current_token.get('method')
        
        if method == 'jwt':
            # For JWT, would typically call refresh endpoint
            # For now, just validate current token
            access_token = self._current_token.get('access_token')
            if access_token and not TokenValidator.is_jwt_expired(access_token):
                return self._current_token
            else:
                raise TokenExpiredError("JWT token expired and cannot be refreshed")
        
        elif method == 'service':
            # Refresh service token
            service_key = self._current_token.get('service_key')
            service_id = self._current_token.get('service_id')
            
            if service_key and service_id:
                return self._authenticate_service(service_key, service_id)
        
        # For other methods, return current token
        return self._current_token
    
    def get_stored_tokens(self) -> List[str]:
        """Get list of stored token IDs"""
        return self.storage.list_tokens()
    
    def load_stored_token(self, token_id: str) -> bool:
        """Load a stored token as current"""
        token_data = self.storage.get_token(token_id)
        
        if not token_data:
            return False
        
        # Check if token is expired
        if self._is_token_expired(token_data):
            self.storage.delete_token(token_id)
            return False
        
        with self._lock:
            self._current_token = token_data
        
        self._notify_auth_event('token_loaded', {'token_id': token_id})
        
        return True


# Export authentication components
__all__ = [
    'AuthenticationManager',
    'SecureTokenStorage', 
    'TokenValidator'
]