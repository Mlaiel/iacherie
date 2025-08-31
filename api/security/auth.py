"""
Advanced Authentication Management System
Enterprise-grade authentication with multi-factor support

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Security Expert + Backend Senior
"""

import jwt
import bcrypt
import secrets
import hashlib
import pyotp
import qrcode
import face_recognition
import cv2
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Tuple, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import asyncio
import aioredis
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256
import logging
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time
import hmac
import io

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom authentication exception"""
    pass


class AuthenticationStatus(Enum):
    """Authentication status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    EXPIRED = "expired"
    LOCKED = "locked"
    SUSPENDED = "suspended"


class AuthenticationMethod(Enum):
    """Supported authentication methods"""
    PASSWORD = "password"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    TWO_FACTOR = "two_factor"
    BIOMETRIC = "biometric"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    SAML = "saml"
    FIDO2 = "fido2"


@dataclass
class AuthenticationResult:
    """Authentication result data structure"""
    status: AuthenticationStatus
    user_id: Optional[str] = None
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    attempt_count: int = 0
    last_attempt: Optional[datetime] = None


@dataclass
class UserCredentials:
    """User credentials data structure"""
    username: str
    password: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    biometric_hash: Optional[str] = None
    oauth_tokens: Dict[str, str] = field(default_factory=dict)
    api_keys: List[str] = field(default_factory=list)
    security_questions: Dict[str, str] = field(default_factory=dict)


class BaseAuthenticator(ABC):
    """Base authenticator interface"""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """Authenticate user with provided credentials"""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> AuthenticationResult:
        """Validate authentication token"""
        pass
    
    @abstractmethod
    async def revoke_authentication(self, token: str) -> bool:
        """Revoke authentication token"""
        pass


class JWTManager:
    """Advanced JWT token management with security features"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_blacklist = set()
        self.refresh_tokens = {}
        
    def generate_token(self, user_id: str, permissions: List[str], 
                      expires_hours: int = 24, custom_claims: Dict = None) -> Tuple[str, str]:
        """Generate access and refresh tokens"""
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(hours=expires_hours)
        refresh_exp = now + timedelta(days=30)  # Refresh token valid for 30 days
        
        # Access token payload
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'iat': now,
            'exp': exp_time,
            'type': 'access',
            'jti': secrets.token_urlsafe(32)  # JWT ID for tracking
        }
        
        if custom_claims:
            payload.update(custom_claims)
        
        access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'iat': now,
            'exp': refresh_exp,
            'type': 'refresh',
            'jti': secrets.token_urlsafe(32)
        }
        
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token
        self.refresh_tokens[refresh_token] = {
            'user_id': user_id,
            'created_at': now,
            'expires_at': refresh_exp
        }
        
        return access_token, refresh_token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            if token in self.token_blacklist:
                raise AuthenticationError("Token has been revoked")
            
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token expiration
            if datetime.fromtimestamp(decoded['exp'], timezone.utc) < datetime.now(timezone.utc):
                raise AuthenticationError("Token has expired")
            
            return decoded
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Generate new access token using refresh token"""
        try:
            decoded_refresh = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            if decoded_refresh.get('type') != 'refresh':
                raise AuthenticationError("Invalid refresh token")
            
            if refresh_token not in self.refresh_tokens:
                raise AuthenticationError("Refresh token not found")
            
            user_id = decoded_refresh['user_id']
            
            # Generate new access token (get user permissions from database)
            permissions = self._get_user_permissions(user_id)
            new_access_token, _ = self.generate_token(user_id, permissions)
            
            return new_access_token
            
        except jwt.ExpiredSignatureError:
            # Clean up expired refresh token
            self.refresh_tokens.pop(refresh_token, None)
            raise AuthenticationError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid refresh token: {str(e)}")
    
    def revoke_token(self, token: str) -> bool:
        """Add token to blacklist"""
        self.token_blacklist.add(token)
        return True
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke refresh token"""
        return self.refresh_tokens.pop(refresh_token, None) is not None
    
    def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions (to be implemented with database)"""
        # Placeholder - should query database for user permissions
        return ['read', 'write', 'content_create']


class OAuth2Manager:
    """OAuth2 authentication management"""
    
    def __init__(self):
        self.providers = {
            'google': {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'scope': 'openid email profile'
            },
            'facebook': {
                'client_id': os.getenv('FACEBOOK_CLIENT_ID'),
                'client_secret': os.getenv('FACEBOOK_CLIENT_SECRET'),
                'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'scope': 'email,public_profile'
            },
            'apple': {
                'client_id': os.getenv('APPLE_CLIENT_ID'),
                'client_secret': os.getenv('APPLE_CLIENT_SECRET'),
                'auth_url': 'https://appleid.apple.com/auth/authorize',
                'token_url': 'https://appleid.apple.com/auth/token',
                'scope': 'email name'
            },
            'twitter': {
                'client_id': os.getenv('TWITTER_CLIENT_ID'),
                'client_secret': os.getenv('TWITTER_CLIENT_SECRET'),
                'auth_url': 'https://twitter.com/i/oauth2/authorize',
                'token_url': 'https://api.twitter.com/2/oauth2/token',
                'scope': 'tweet.read users.read'
            },
            'spotify': {
                'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
                'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
                'auth_url': 'https://accounts.spotify.com/authorize',
                'token_url': 'https://accounts.spotify.com/api/token',
                'scope': 'user-read-private user-read-email streaming user-library-read'
            },
            'github': {
                'client_id': os.getenv('GITHUB_CLIENT_ID'),
                'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
                'auth_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'scope': 'user:email'
            }
        }
        self.state_tokens = {}  # For CSRF protection
    
    def generate_auth_url(self, provider: str, redirect_uri: str, state: str = None) -> str:
        """Generate OAuth2 authorization URL"""
        if provider not in self.providers:
            raise ValueError(f"Unsupported OAuth2 provider: {provider}")
        
        config = self.providers[provider]
        
        if not state:
            state = secrets.token_urlsafe(32)
        
        self.state_tokens[state] = {
            'provider': provider,
            'created_at': datetime.now(timezone.utc),
            'redirect_uri': redirect_uri
        }
        
        params = {
            'client_id': config['client_id'],
            'redirect_uri': redirect_uri,
            'scope': config['scope'],
            'response_type': 'code',
            'state': state
        }
        
        param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f"{config['auth_url']}?{param_string}"
    
    async def exchange_code_for_token(self, provider: str, code: str, 
                                    redirect_uri: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if state not in self.state_tokens:
            raise AuthenticationError("Invalid or expired state token")
        
        state_info = self.state_tokens.pop(state)
        if state_info['provider'] != provider:
            raise AuthenticationError("Provider mismatch")
        
        config = self.providers[provider]
        
        # Exchange code for token (implementation would use HTTP client)
        # This is a simplified version - real implementation would make HTTP request
        token_data = {
            'access_token': 'mock_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'mock_refresh_token',
            'scope': config['scope']
        }
        
        return token_data
    
    async def get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth2 provider"""
        # Provider-specific user info endpoints
        endpoints = {
            'google': 'https://www.googleapis.com/oauth2/v2/userinfo',
            'facebook': 'https://graph.facebook.com/me?fields=id,email,name,picture',
            'apple': 'https://appleid.apple.com/auth/userinfo',
            'twitter': 'https://api.twitter.com/2/users/me',
            'spotify': 'https://api.spotify.com/v1/me',
            'github': 'https://api.github.com/user'
        }
        
        if provider not in endpoints:
            raise ValueError(f"No user info endpoint for provider: {provider}")
        
        # Mock user data - real implementation would make HTTP request
        mock_user_data = {
            'id': f'mock_{provider}_user_id',
            'email': f'user@{provider}.com',
            'name': f'Mock {provider.title()} User',
            'picture': f'https://{provider}.com/avatar.jpg'
        }
        
        return mock_user_data


class SAMLManager:
    """SAML SSO authentication management for enterprise clients"""
    
    def __init__(self):
        self.saml_settings = {
            'sp': {
                'entityId': os.getenv('SAML_SP_ENTITY_ID', 'https://ainflue.ai/saml/metadata'),
                'assertionConsumerService': {
                    'url': os.getenv('SAML_ACS_URL', 'https://ainflue.ai/saml/acs'),
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
                },
                'singleLogoutService': {
                    'url': os.getenv('SAML_SLS_URL', 'https://ainflue.ai/saml/sls'),
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                },
                'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
                'x509cert': '',
                'privateKey': ''
            },
            'idp': {}  # Will be configured per enterprise client
        }
        self.enterprise_configs = {}
    
    def configure_enterprise_idp(self, enterprise_id: str, idp_config: Dict[str, Any]):
        """Configure SAML IdP settings for an enterprise client"""
        required_fields = ['entityId', 'singleSignOnService', 'x509cert']
        
        for field in required_fields:
            if field not in idp_config:
                raise ValueError(f"Missing required SAML IdP field: {field}")
        
        self.enterprise_configs[enterprise_id] = {
            'entityId': idp_config['entityId'],
            'singleSignOnService': {
                'url': idp_config['singleSignOnService'],
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'singleLogoutService': {
                'url': idp_config.get('singleLogoutService', ''),
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'x509cert': idp_config['x509cert'],
            'attributeMapping': idp_config.get('attributeMapping', {
                'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
                'name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
                'groups': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/groups'
            })
        }
        
        logger.info(f"Configured SAML IdP for enterprise: {enterprise_id}")
    
    def generate_auth_request(self, enterprise_id: str, relay_state: str = None) -> str:
        """Generate SAML authentication request"""
        if enterprise_id not in self.enterprise_configs:
            raise ValueError(f"No SAML configuration found for enterprise: {enterprise_id}")
        
        idp_config = self.enterprise_configs[enterprise_id]
        
        # Generate SAML AuthnRequest (simplified version)
        auth_request_id = f"_{secrets.token_hex(20)}"
        issue_instant = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        auth_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest 
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{auth_request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{idp_config['singleSignOnService']['url']}"
    AssertionConsumerServiceURL="{self.saml_settings['sp']['assertionConsumerService']['url']}"
    ProtocolBinding="{self.saml_settings['sp']['assertionConsumerService']['binding']}">
    <saml:Issuer>{self.saml_settings['sp']['entityId']}</saml:Issuer>
</samlp:AuthnRequest>"""
        
        # In production: properly encode and sign the request
        encoded_request = base64.b64encode(auth_request.encode()).decode()
        
        # Build redirect URL
        params = {
            'SAMLRequest': encoded_request
        }
        if relay_state:
            params['RelayState'] = relay_state
        
        param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f"{idp_config['singleSignOnService']['url']}?{param_string}"
    
    async def process_saml_response(self, enterprise_id: str, saml_response: str, 
                                  relay_state: str = None) -> Dict[str, Any]:
        """Process SAML response and extract user information"""
        if enterprise_id not in self.enterprise_configs:
            raise ValueError(f"No SAML configuration found for enterprise: {enterprise_id}")
        
        try:
            # Decode SAML response
            decoded_response = base64.b64decode(saml_response).decode()
            
            # In production: validate signature, parse XML, extract assertions
            # For now, return mock user data
            user_data = {
                'enterprise_id': enterprise_id,
                'user_id': f'saml_user_{secrets.token_hex(8)}',
                'email': 'saml.user@enterprise.com',
                'name': 'SAML Enterprise User',
                'groups': ['employees', 'users'],
                'attributes': {
                    'department': 'IT',
                    'title': 'Software Engineer'
                }
            }
            
            return user_data
            
        except Exception as e:
            logger.error(f"SAML response processing error: {e}")
            raise AuthenticationError(f"Invalid SAML response: {str(e)}")
    
    def generate_metadata(self) -> str:
        """Generate SAML SP metadata"""
        metadata = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    entityID="{self.saml_settings['sp']['entityId']}">
    <md:SPSSODescriptor
        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:AssertionConsumerService
            Binding="{self.saml_settings['sp']['assertionConsumerService']['binding']}"
            Location="{self.saml_settings['sp']['assertionConsumerService']['url']}"
            index="0" isDefault="true"/>
        <md:SingleLogoutService
            Binding="{self.saml_settings['sp']['singleLogoutService']['binding']}"
            Location="{self.saml_settings['sp']['singleLogoutService']['url']}"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""
        
        return metadata


class FIDO2Manager:
    """FIDO2/WebAuthn hardware key authentication management"""
    
    def __init__(self):
        self.rp_id = os.getenv('WEBAUTHN_RP_ID', 'ainflue.ai')
        self.rp_name = os.getenv('WEBAUTHN_RP_NAME', 'Ainflue AI Platform')
        self.origin = os.getenv('WEBAUTHN_ORIGIN', 'https://ainflue.ai')
        self.registered_credentials = {}  # In production: use secure database
        self.pending_challenges = {}
    
    def generate_registration_options(self, user_id: str, username: str, 
                                    display_name: str = None) -> Dict[str, Any]:
        """Generate WebAuthn registration options for new credential"""
        challenge = secrets.token_bytes(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip('=')
        
        # Store challenge for verification
        self.pending_challenges[challenge_b64] = {
            'user_id': user_id,
            'username': username,
            'created_at': datetime.now(timezone.utc),
            'type': 'registration'
        }
        
        registration_options = {
            'challenge': challenge_b64,
            'rp': {
                'name': self.rp_name,
                'id': self.rp_id
            },
            'user': {
                'id': base64.urlsafe_b64encode(user_id.encode()).decode().rstrip('='),
                'name': username,
                'displayName': display_name or username
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},   # ES256
                {'type': 'public-key', 'alg': -257}  # RS256
            ],
            'timeout': 60000,
            'attestation': 'direct',
            'authenticatorSelection': {
                'authenticatorAttachment': 'cross-platform',
                'userVerification': 'preferred',
                'requireResidentKey': False
            }
        }
        
        return registration_options
    
    def verify_registration(self, user_id: str, credential_data: Dict[str, Any]) -> bool:
        """Verify and store new FIDO2 credential"""
        try:
            challenge = credential_data.get('challenge')
            if not challenge or challenge not in self.pending_challenges:
                return False
            
            challenge_info = self.pending_challenges.pop(challenge)
            if challenge_info['user_id'] != user_id:
                return False
            
            # In production: verify attestation, signature, etc.
            credential_id = credential_data.get('id')
            public_key = credential_data.get('publicKey')
            
            if not credential_id or not public_key:
                return False
            
            # Store credential
            if user_id not in self.registered_credentials:
                self.registered_credentials[user_id] = []
            
            self.registered_credentials[user_id].append({
                'id': credential_id,
                'public_key': public_key,
                'counter': credential_data.get('counter', 0),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_used': None
            })
            
            logger.info(f"FIDO2 credential registered for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"FIDO2 registration error: {e}")
            return False
    
    def generate_authentication_options(self, user_id: str = None) -> Dict[str, Any]:
        """Generate WebAuthn authentication options"""
        challenge = secrets.token_bytes(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip('=')
        
        # Store challenge for verification
        self.pending_challenges[challenge_b64] = {
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc),
            'type': 'authentication'
        }
        
        auth_options = {
            'challenge': challenge_b64,
            'timeout': 60000,
            'userVerification': 'preferred',
            'rpId': self.rp_id
        }
        
        # Add allowed credentials if user specified
        if user_id and user_id in self.registered_credentials:
            auth_options['allowCredentials'] = [
                {
                    'type': 'public-key',
                    'id': cred['id'],
                    'transports': ['usb', 'nfc', 'ble', 'internal']
                }
                for cred in self.registered_credentials[user_id]
            ]
        
        return auth_options
    
    def verify_authentication(self, credential_data: Dict[str, Any]) -> Optional[str]:
        """Verify FIDO2 authentication and return user ID if successful"""
        try:
            challenge = credential_data.get('challenge')
            credential_id = credential_data.get('id')
            
            if not challenge or challenge not in self.pending_challenges:
                return None
            
            challenge_info = self.pending_challenges.pop(challenge)
            
            # Find credential owner
            user_id = None
            credential = None
            
            for uid, creds in self.registered_credentials.items():
                for cred in creds:
                    if cred['id'] == credential_id:
                        user_id = uid
                        credential = cred
                        break
                if user_id:
                    break
            
            if not user_id or not credential:
                return None
            
            # In production: verify signature, counter, etc.
            
            # Update last used
            credential['last_used'] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"FIDO2 authentication successful for user: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"FIDO2 authentication error: {e}")
            return None
    
    def get_user_credentials(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of registered credentials for user"""
        return self.registered_credentials.get(user_id, [])
    
    def revoke_credential(self, user_id: str, credential_id: str) -> bool:
        """Revoke a specific credential"""
        if user_id not in self.registered_credentials:
            return False
        
        credentials = self.registered_credentials[user_id]
        for i, cred in enumerate(credentials):
            if cred['id'] == credential_id:
                credentials.pop(i)
                logger.info(f"FIDO2 credential revoked: {credential_id} for user: {user_id}")
                return True
        
        return False


class SessionManager:
    """Advanced session management with security features"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.session_timeout = 3600  # 1 hour default
        self.max_sessions_per_user = 5
        self.session_encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.session_encryption_key)
    
    async def create_session(self, user_id: str, user_agent: str = None, 
                           ip_address: str = None, metadata: Dict = None) -> str:
        """Create new session with security metadata"""
        redis_client = await aioredis.from_url(self.redis_url)
        
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_accessed': datetime.now(timezone.utc).isoformat(),
            'user_agent': user_agent,
            'ip_address': ip_address,
            'metadata': metadata or {},
            'is_active': True
        }
        
        # Check session limit
        await self._enforce_session_limit(redis_client, user_id)
        
        # Encrypt session data
        encrypted_data = self.cipher.encrypt(str(session_data).encode())
        
        # Store in Redis with expiration
        await redis_client.setex(
            f"session:{session_id}",
            self.session_timeout,
            encrypted_data
        )
        
        # Add to user's session list
        await redis_client.sadd(f"user_sessions:{user_id}", session_id)
        
        await redis_client.close()
        return session_id
    
    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate and update session"""
        redis_client = await aioredis.from_url(self.redis_url)
        
        encrypted_data = await redis_client.get(f"session:{session_id}")
        if not encrypted_data:
            await redis_client.close()
            return None
        
        try:
            # Decrypt session data
            decrypted_data = self.cipher.decrypt(encrypted_data)
            session_data = eval(decrypted_data.decode())  # In production, use JSON
            
            # Update last accessed time
            session_data['last_accessed'] = datetime.now(timezone.utc).isoformat()
            
            # Re-encrypt and store
            encrypted_data = self.cipher.encrypt(str(session_data).encode())
            await redis_client.setex(
                f"session:{session_id}",
                self.session_timeout,
                encrypted_data
            )
            
            await redis_client.close()
            return session_data
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            await redis_client.close()
            return None
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke specific session"""
        redis_client = await aioredis.from_url(self.redis_url)
        
        # Get session data to find user
        session_data = await self.validate_session(session_id)
        if session_data:
            user_id = session_data['user_id']
            await redis_client.srem(f"user_sessions:{user_id}", session_id)
        
        # Delete session
        result = await redis_client.delete(f"session:{session_id}")
        await redis_client.close()
        
        return result > 0
    
    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user"""
        redis_client = await aioredis.from_url(self.redis_url)
        
        # Get all user sessions
        session_ids = await redis_client.smembers(f"user_sessions:{user_id}")
        
        count = 0
        for session_id in session_ids:
            if await redis_client.delete(f"session:{session_id.decode()}"):
                count += 1
        
        # Clear user session set
        await redis_client.delete(f"user_sessions:{user_id}")
        await redis_client.close()
        
        return count
    
    async def _enforce_session_limit(self, redis_client, user_id: str):
        """Enforce maximum sessions per user"""
        session_ids = await redis_client.smembers(f"user_sessions:{user_id}")
        
        if len(session_ids) >= self.max_sessions_per_user:
            # Remove oldest session
            oldest_session = session_ids.pop()
            await redis_client.delete(f"session:{oldest_session.decode()}")
            await redis_client.srem(f"user_sessions:{user_id}", oldest_session)


class TwoFactorAuthManager:
    """Two-Factor Authentication management"""
    
    def __init__(self):
        self.totp_window = 30  # 30-second window
        self.backup_codes_count = 10
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def generate_secret_key(self, user_id: str, app_name: str = "IA Influencer Agent") -> str:
        """Generate TOTP secret key for user"""
        secret = pyotp.random_base32()
        
        # Store secret securely (in production, encrypt and store in database)
        self._store_user_secret(user_id, secret)
        
        return secret
    
    def generate_qr_code(self, user_id: str, user_email: str, secret: str, 
                        app_name: str = "IA Influencer Agent") -> bytes:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=app_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
    
    def verify_totp_token(self, user_id: str, token: str) -> bool:
        """Verify TOTP token"""
        secret = self._get_user_secret(user_id)
        if not secret:
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 1 window before/after
    
    def generate_backup_codes(self, user_id: str) -> List[str]:
        """Generate backup recovery codes"""
        backup_codes = []
        
        for _ in range(self.backup_codes_count):
            code = secrets.token_hex(4).upper()  # 8-character hex codes
            backup_codes.append(code)
        
        # Hash and store codes
        hashed_codes = [self.pwd_context.hash(code) for code in backup_codes]
        self._store_backup_codes(user_id, hashed_codes)
        
        return backup_codes
    
    def verify_backup_code(self, user_id: str, backup_code: str) -> bool:
        """Verify backup recovery code"""
        stored_codes = self._get_backup_codes(user_id)
        
        for i, hashed_code in enumerate(stored_codes):
            if self.pwd_context.verify(backup_code, hashed_code):
                # Remove used backup code
                stored_codes.pop(i)
                self._store_backup_codes(user_id, stored_codes)
                return True
        
        return False
    
    def _store_user_secret(self, user_id: str, secret: str):
        """Store user's TOTP secret (placeholder - implement with secure database)"""
        # In production: encrypt and store in database
        pass
    
    def _get_user_secret(self, user_id: str) -> Optional[str]:
        """Get user's TOTP secret (placeholder)"""
        # In production: decrypt from database
        return "JBSWY3DPEHPK3PXP"  # Mock secret for testing
    
    def _store_backup_codes(self, user_id: str, codes: List[str]):
        """Store backup codes (placeholder)"""
        pass
    
    def _get_backup_codes(self, user_id: str) -> List[str]:
        """Get backup codes (placeholder)"""
        return []


class BiometricAuthManager:
    """Biometric authentication management"""
    
    def __init__(self):
        self.face_encodings = {}  # In production: use secure database
        self.fingerprint_templates = {}
        self.voice_prints = {}
    
    def register_face(self, user_id: str, face_image: np.ndarray) -> bool:
        """Register user's face for biometric authentication"""
        try:
            # Detect faces in the image
            face_locations = face_recognition.face_locations(face_image)
            
            if len(face_locations) != 1:
                raise ValueError("Image must contain exactly one face")
            
            # Generate face encoding
            face_encodings = face_recognition.face_encodings(face_image, face_locations)
            
            if len(face_encodings) > 0:
                # Store face encoding (in production: encrypt and store securely)
                self.face_encodings[user_id] = face_encodings[0]
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Face registration error: {e}")
            return False
    
    def authenticate_face(self, user_id: str, face_image: np.ndarray, 
                         tolerance: float = 0.6) -> bool:
        """Authenticate user using face recognition"""
        try:
            if user_id not in self.face_encodings:
                return False
            
            # Get face encoding from image
            face_locations = face_recognition.face_locations(face_image)
            face_encodings = face_recognition.face_encodings(face_image, face_locations)
            
            if len(face_encodings) == 0:
                return False
            
            # Compare with stored encoding
            stored_encoding = self.face_encodings[user_id]
            matches = face_recognition.compare_faces([stored_encoding], 
                                                   face_encodings[0], 
                                                   tolerance=tolerance)
            
            return matches[0] if matches else False
            
        except Exception as e:
            logger.error(f"Face authentication error: {e}")
            return False
    
    def register_fingerprint(self, user_id: str, fingerprint_template: bytes) -> bool:
        """Register fingerprint template"""
        try:
            # In production: process and validate fingerprint template
            # For now, store as-is
            self.fingerprint_templates[user_id] = fingerprint_template
            return True
            
        except Exception as e:
            logger.error(f"Fingerprint registration error: {e}")
            return False
    
    def authenticate_fingerprint(self, user_id: str, fingerprint_template: bytes) -> bool:
        """Authenticate using fingerprint"""
        try:
            if user_id not in self.fingerprint_templates:
                return False
            
            stored_template = self.fingerprint_templates[user_id]
            
            # In production: use proper fingerprint matching algorithm
            # For now, simple comparison
            return stored_template == fingerprint_template
            
        except Exception as e:
            logger.error(f"Fingerprint authentication error: {e}")
            return False
    
    def register_voice_print(self, user_id: str, voice_sample: np.ndarray) -> bool:
        """Register voice print for authentication"""
        try:
            # In production: extract voice features using ML models
            # For now, store voice sample hash
            voice_hash = hashlib.sha256(voice_sample.tobytes()).hexdigest()
            self.voice_prints[user_id] = voice_hash
            return True
            
        except Exception as e:
            logger.error(f"Voice print registration error: {e}")
            return False
    
    def authenticate_voice(self, user_id: str, voice_sample: np.ndarray, 
                          threshold: float = 0.8) -> bool:
        """Authenticate using voice recognition"""
        try:
            if user_id not in self.voice_prints:
                return False
            
            # In production: use proper voice recognition ML model
            # For now, simple hash comparison
            voice_hash = hashlib.sha256(voice_sample.tobytes()).hexdigest()
            return self.voice_prints[user_id] == voice_hash
            
        except Exception as e:
            logger.error(f"Voice authentication error: {e}")
            return False


class AuthenticationManager:
    """Main authentication manager coordinating all authentication methods"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.jwt_manager = JWTManager(
            secret_key=self.config.get('jwt_secret', secrets.token_urlsafe(32))
        )
        self.oauth2_manager = OAuth2Manager()
        self.saml_manager = SAMLManager()
        self.fido2_manager = FIDO2Manager()
        self.session_manager = SessionManager(
            redis_url=self.config.get('redis_url', 'redis://localhost:6379')
        )
        self.two_factor_manager = TwoFactorAuthManager()
        self.biometric_manager = BiometricAuthManager()
        
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.failed_attempts = {}  # Track failed login attempts
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 minutes
    
    async def authenticate_user(self, credentials: UserCredentials, 
                              authentication_methods: List[AuthenticationMethod],
                              metadata: Dict[str, Any] = None) -> AuthenticationResult:
        """Authenticate user with multiple methods"""
        try:
            # Check if user is locked out
            if await self._is_user_locked(credentials.username):
                return AuthenticationResult(
                    status=AuthenticationStatus.LOCKED,
                    error_message="Account temporarily locked due to multiple failed attempts"
                )
            
            auth_results = []
            
            # Primary authentication (password/OAuth2)
            if AuthenticationMethod.PASSWORD in authentication_methods:
                result = await self._authenticate_password(credentials)
                auth_results.append(result)
            
            if AuthenticationMethod.OAUTH2 in authentication_methods:
                result = await self._authenticate_oauth2(credentials)
                auth_results.append(result)
            
            # Check if primary authentication succeeded
            primary_success = any(r.status == AuthenticationStatus.SUCCESS for r in auth_results)
            
            if not primary_success:
                await self._record_failed_attempt(credentials.username)
                return AuthenticationResult(
                    status=AuthenticationStatus.FAILED,
                    error_message="Primary authentication failed"
                )
            
            # Two-factor authentication if required
            if AuthenticationMethod.TWO_FACTOR in authentication_methods:
                if not await self._authenticate_two_factor(credentials):
                    return AuthenticationResult(
                        status=AuthenticationStatus.FAILED,
                        error_message="Two-factor authentication failed"
                    )
            
            # SAML authentication if required
            if AuthenticationMethod.SAML in authentication_methods:
                if not await self._authenticate_saml(credentials):
                    return AuthenticationResult(
                        status=AuthenticationStatus.FAILED,
                        error_message="SAML authentication failed"
                    )
            
            # FIDO2 authentication if required
            if AuthenticationMethod.FIDO2 in authentication_methods:
                if not await self._authenticate_fido2(credentials):
                    return AuthenticationResult(
                        status=AuthenticationStatus.FAILED,
                        error_message="FIDO2 authentication failed"
                    )
            
            # Biometric authentication if required
            if AuthenticationMethod.BIOMETRIC in authentication_methods:
                if not await self._authenticate_biometric(credentials):
                    return AuthenticationResult(
                        status=AuthenticationStatus.FAILED,
                        error_message="Biometric authentication failed"
                    )
            
            # Create session
            user_id = credentials.username  # In production: get from database
            session_id = await self.session_manager.create_session(
                user_id=user_id,
                user_agent=metadata.get('user_agent') if metadata else None,
                ip_address=metadata.get('ip_address') if metadata else None,
                metadata=metadata
            )
            
            # Generate JWT tokens
            permissions = self._get_user_permissions(user_id)
            access_token, refresh_token = self.jwt_manager.generate_token(
                user_id=user_id,
                permissions=permissions
            )
            
            # Clear failed attempts
            self.failed_attempts.pop(credentials.username, None)
            
            return AuthenticationResult(
                status=AuthenticationStatus.SUCCESS,
                user_id=user_id,
                session_token=session_id,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
                permissions=permissions,
                metadata={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'session_id': session_id
                }
            )
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthenticationResult(
                status=AuthenticationStatus.FAILED,
                error_message="Authentication system error"
            )
    
    async def validate_token(self, token: str, token_type: str = 'access') -> AuthenticationResult:
        """Validate JWT token"""
        try:
            decoded_token = self.jwt_manager.verify_token(token)
            
            if decoded_token.get('type') != token_type:
                raise AuthenticationError(f"Invalid token type, expected {token_type}")
            
            return AuthenticationResult(
                status=AuthenticationStatus.SUCCESS,
                user_id=decoded_token['user_id'],
                permissions=decoded_token.get('permissions', []),
                metadata={'token_data': decoded_token}
            )
            
        except AuthenticationError as e:
            return AuthenticationResult(
                status=AuthenticationStatus.FAILED,
                error_message=str(e)
            )
    
    async def refresh_authentication(self, refresh_token: str) -> AuthenticationResult:
        """Refresh access token using refresh token"""
        try:
            new_access_token = self.jwt_manager.refresh_access_token(refresh_token)
            
            # Validate new token to get user info
            validation_result = await self.validate_token(new_access_token)
            
            if validation_result.status == AuthenticationStatus.SUCCESS:
                validation_result.metadata['new_access_token'] = new_access_token
            
            return validation_result
            
        except AuthenticationError as e:
            return AuthenticationResult(
                status=AuthenticationStatus.FAILED,
                error_message=str(e)
            )
    
    async def logout_user(self, session_id: str = None, access_token: str = None, 
                         refresh_token: str = None) -> bool:
        """Logout user and revoke tokens/sessions"""
        success_count = 0
        
        if session_id:
            if await self.session_manager.revoke_session(session_id):
                success_count += 1
        
        if access_token:
            if self.jwt_manager.revoke_token(access_token):
                success_count += 1
        
        if refresh_token:
            if self.jwt_manager.revoke_refresh_token(refresh_token):
                success_count += 1
        
        return success_count > 0
    
    async def _authenticate_password(self, credentials: UserCredentials) -> AuthenticationResult:
        """Authenticate using password"""
        if not credentials.password:
            return AuthenticationResult(
                status=AuthenticationStatus.FAILED,
                error_message="Password required"
            )
        
        # In production: get hashed password from database
        stored_password_hash = self._get_stored_password_hash(credentials.username)
        
        if stored_password_hash and self.pwd_context.verify(credentials.password, stored_password_hash):
            return AuthenticationResult(status=AuthenticationStatus.SUCCESS)
        
        return AuthenticationResult(
            status=AuthenticationStatus.FAILED,
            error_message="Invalid password"
        )
    
    async def _authenticate_oauth2(self, credentials: UserCredentials) -> AuthenticationResult:
        """Authenticate using OAuth2 tokens"""
        # Implementation depends on specific OAuth2 flow
        # This is a simplified version
        return AuthenticationResult(status=AuthenticationStatus.SUCCESS)
    
    async def _authenticate_two_factor(self, credentials: UserCredentials) -> bool:
        """Authenticate using two-factor authentication"""
        # Implementation would check TOTP token or backup codes
        return True  # Placeholder
    
    async def _authenticate_saml(self, credentials: UserCredentials) -> bool:
        """Authenticate using SAML response"""
        # Implementation would verify SAML assertion
        return True  # Placeholder
    
    async def _authenticate_fido2(self, credentials: UserCredentials) -> bool:
        """Authenticate using FIDO2/WebAuthn"""
        # Implementation would verify FIDO2 assertion
        return True  # Placeholder
    
    async def _authenticate_biometric(self, credentials: UserCredentials) -> bool:
        """Authenticate using biometric data"""
        # Implementation would verify biometric hash
        return True  # Placeholder
    
    async def _is_user_locked(self, username: str) -> bool:
        """Check if user account is locked due to failed attempts"""
        if username not in self.failed_attempts:
            return False
        
        attempts_info = self.failed_attempts[username]
        
        if attempts_info['count'] >= self.max_attempts:
            time_since_last = time.time() - attempts_info['last_attempt']
            return time_since_last < self.lockout_duration
        
        return False
    
    async def _record_failed_attempt(self, username: str):
        """Record failed authentication attempt"""
        current_time = time.time()
        
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {'count': 0, 'last_attempt': current_time}
        
        self.failed_attempts[username]['count'] += 1
        self.failed_attempts[username]['last_attempt'] = current_time
    
    def _get_stored_password_hash(self, username: str) -> Optional[str]:
        """Get stored password hash (placeholder - implement with database)"""
        # Placeholder - in production, query database
        return self.pwd_context.hash("default_password")
    
    def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions (placeholder - implement with database)"""
        # Placeholder - in production, query database for user roles/permissions
        return ['read', 'write', 'content_create', 'content_protect']


__all__ = [
    'AuthenticationManager',
    'JWTManager',
    'OAuth2Manager',
    'SAMLManager',
    'FIDO2Manager',
    'SessionManager',
    'TwoFactorAuthManager',
    'BiometricAuthManager',
    'AuthenticationError',
    'AuthenticationStatus',
    'AuthenticationMethod',
    'AuthenticationResult',
    'UserCredentials'
]
