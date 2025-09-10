"""Ainflue Core Security - OAuth Core
===================================

Enterprise-grade OAuth 2.0/OIDC implementation providing secure authentication,
authorization server, token management, scope-based access control, 
and federated identity support for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import urllib.parse
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Setup logger
logger = logging.getLogger(__name__)

class GrantType(str, Enum):
    """OAuth 2.0 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    RESOURCE_OWNER_PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"
    IMPLICIT = "implicit"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"
    JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"

class TokenType(str, Enum):
    """Token types"""
    BEARER = "Bearer"
    MAC = "MAC"
    BASIC = "Basic"

class ResponseType(str, Enum):
    """OAuth response types"""
    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"
    CODE_TOKEN = "code token"
    CODE_ID_TOKEN = "code id_token"
    TOKEN_ID_TOKEN = "token id_token"
    CODE_TOKEN_ID_TOKEN = "code token id_token"

class ClientType(str, Enum):
    """OAuth client types"""
    CONFIDENTIAL = "confidential"
    PUBLIC = "public"

class TokenStatus(str, Enum):
    """Token status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

@dataclass
class OAuthScope:
    """OAuth scope definition"""
    name: str
    description: str
    resource: str
    permissions: List[str]
    required_claims: List[str] = field(default_factory=list)
    sensitive: bool = False

@dataclass
class OAuthClient:
    """OAuth client registration"""
    client_id: str
    client_secret: str
    client_type: ClientType
    redirect_uris: List[str]
    scopes: List[str]
    grant_types: List[GrantType]
    response_types: List[ResponseType]
    name: str
    description: str = ""
    logo_uri: Optional[str] = None
    policy_uri: Optional[str] = None
    tos_uri: Optional[str] = None
    jwks_uri: Optional[str] = None
    sector_identifier_uri: Optional[str] = None
    subject_type: str = "public"
    id_token_signed_response_alg: str = "RS256"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True
    trusted: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessToken:
    """Access token data"""
    token: str
    token_type: TokenType = TokenType.BEARER
    client_id: str = ""
    user_id: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    issued_at: datetime = field(default_factory=datetime.utcnow)
    issuer: str = ""
    audience: List[str] = field(default_factory=list)
    subject: Optional[str] = None
    jti: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TokenStatus = TokenStatus.ACTIVE
    refresh_token: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RefreshToken:
    """Refresh token data"""
    token: str
    client_id: str
    user_id: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    issued_at: datetime = field(default_factory=datetime.utcnow)
    access_token: Optional[str] = None
    status: TokenStatus = TokenStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuthorizationCode:
    """Authorization code data"""
    code: str
    client_id: str
    user_id: str
    redirect_uri: str
    scopes: List[str]
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10))
    issued_at: datetime = field(default_factory=datetime.utcnow)
    used: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IDToken:
    """OpenID Connect ID Token"""
    token: str
    issuer: str
    subject: str
    audience: List[str]
    expires_at: datetime
    issued_at: datetime
    auth_time: Optional[datetime] = None
    nonce: Optional[str] = None
    acr: Optional[str] = None
    amr: List[str] = field(default_factory=list)
    azp: Optional[str] = None
    claims: Dict[str, Any] = field(default_factory=dict)

class TokenStore(ABC):
    """Abstract token store interface"""
    
    @abstractmethod
    async def store_access_token(self, token: AccessToken) -> bool:
        pass
    
    @abstractmethod
    async def get_access_token(self, token: str) -> Optional[AccessToken]:
        pass
    
    @abstractmethod
    async def revoke_access_token(self, token: str) -> bool:
        pass
    
    @abstractmethod
    async def store_refresh_token(self, token: RefreshToken) -> bool:
        pass
    
    @abstractmethod
    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        pass
    
    @abstractmethod
    async def revoke_refresh_token(self, token: str) -> bool:
        pass
    
    @abstractmethod
    async def store_authorization_code(self, code: AuthorizationCode) -> bool:
        pass
    
    @abstractmethod
    async def get_authorization_code(self, code: str) -> Optional[AuthorizationCode]:
        pass
    
    @abstractmethod
    async def use_authorization_code(self, code: str) -> bool:
        pass

class InMemoryTokenStore(TokenStore):
    """In-memory token store implementation"""
    
    def __init__(self):
        self.access_tokens: Dict[str, AccessToken] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        
    async def store_access_token(self, token: AccessToken) -> bool:
        self.access_tokens[token.token] = token
        return True
    
    async def get_access_token(self, token: str) -> Optional[AccessToken]:
        access_token = self.access_tokens.get(token)
        if access_token and access_token.expires_at > datetime.utcnow():
            return access_token
        elif access_token:
            access_token.status = TokenStatus.EXPIRED
        return None
    
    async def revoke_access_token(self, token: str) -> bool:
        if token in self.access_tokens:
            self.access_tokens[token].status = TokenStatus.REVOKED
            return True
        return False
    
    async def store_refresh_token(self, token: RefreshToken) -> bool:
        self.refresh_tokens[token.token] = token
        return True
    
    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        refresh_token = self.refresh_tokens.get(token)
        if refresh_token and refresh_token.expires_at > datetime.utcnow():
            return refresh_token
        elif refresh_token:
            refresh_token.status = TokenStatus.EXPIRED
        return None
    
    async def revoke_refresh_token(self, token: str) -> bool:
        if token in self.refresh_tokens:
            self.refresh_tokens[token].status = TokenStatus.REVOKED
            return True
        return False
    
    async def store_authorization_code(self, code: AuthorizationCode) -> bool:
        self.authorization_codes[code.code] = code
        return True
    
    async def get_authorization_code(self, code: str) -> Optional[AuthorizationCode]:
        auth_code = self.authorization_codes.get(code)
        if auth_code and not auth_code.used and auth_code.expires_at > datetime.utcnow():
            return auth_code
        return None
    
    async def use_authorization_code(self, code: str) -> bool:
        if code in self.authorization_codes:
            self.authorization_codes[code].used = True
            return True
        return False

class ClientStore(ABC):
    """Abstract client store interface"""
    
    @abstractmethod
    async def get_client(self, client_id: str) -> Optional[OAuthClient]:
        pass
    
    @abstractmethod
    async def register_client(self, client: OAuthClient) -> bool:
        pass
    
    @abstractmethod
    async def update_client(self, client: OAuthClient) -> bool:
        pass
    
    @abstractmethod
    async def delete_client(self, client_id: str) -> bool:
        pass

class InMemoryClientStore(ClientStore):
    """In-memory client store implementation"""
    
    def __init__(self):
        self.clients: Dict[str, OAuthClient] = {}
    
    async def get_client(self, client_id: str) -> Optional[OAuthClient]:
        return self.clients.get(client_id)
    
    async def register_client(self, client: OAuthClient) -> bool:
        self.clients[client.client_id] = client
        return True
    
    async def update_client(self, client: OAuthClient) -> bool:
        if client.client_id in self.clients:
            client.updated_at = datetime.utcnow()
            self.clients[client.client_id] = client
            return True
        return False
    
    async def delete_client(self, client_id: str) -> bool:
        if client_id in self.clients:
            del self.clients[client_id]
            return True
        return False

class JWTHandler:
    """JWT token handler"""
    
    def __init__(self, private_key: str, public_key: str, algorithm: str = "RS256"):
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm
    
    def create_access_token(self, payload: Dict[str, Any]) -> str:
        """Create JWT access token"""
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)
    
    def create_id_token(self, payload: Dict[str, Any]) -> str:
        """Create OpenID Connect ID token"""
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and verify JWT token"""
        return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
    
    def verify_token(self, token: str) -> bool:
        """Verify JWT token signature"""
        try:
            jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return True
        except jwt.InvalidTokenError:
            return False

class PKCEHandler:
    """PKCE (Proof Key for Code Exchange) handler"""
    
    @staticmethod
    def generate_code_verifier() -> str:
        """Generate code verifier"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    @staticmethod
    def generate_code_challenge(code_verifier: str, method: str = "S256") -> str:
        """Generate code challenge"""
        if method == "S256":
            digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
            return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
        elif method == "plain":
            return code_verifier
        else:
            raise ValueError(f"Unsupported code challenge method: {method}")
    
    @staticmethod
    def verify_code_challenge(code_verifier: str, code_challenge: str, method: str = "S256") -> bool:
        """Verify code challenge"""
        expected_challenge = PKCEHandler.generate_code_challenge(code_verifier, method)
        return hmac.compare_digest(expected_challenge, code_challenge)

class OAuthCore:
    """Core OAuth 2.0/OIDC authorization server"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.token_store = InMemoryTokenStore()
        self.client_store = InMemoryClientStore()
        self.jwt_handler: Optional[JWTHandler] = None
        self.scopes: Dict[str, OAuthScope] = {}
        self.issuer = "https://auth.ainflue.com"
        self.default_scope = ["read"]
        self.token_endpoint = "/oauth/token"
        self.authorization_endpoint = "/oauth/authorize"
        self.jwks_endpoint = "/oauth/jwks"
        self.userinfo_endpoint = "/oauth/userinfo"
        self.introspection_endpoint = "/oauth/introspect"
        self.revocation_endpoint = "/oauth/revoke"
        self.metrics = {
            'tokens_issued': 0,
            'tokens_revoked': 0,
            'authorization_codes_issued': 0,
            'client_registrations': 0
        }
        
        # Initialize default scopes
        self._initialize_default_scopes()
        
        logger.info(f"OAuth Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize OAuth system"""
        try:
            # Generate RSA key pair for JWT signing
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            self.jwt_handler = JWTHandler(
                private_pem.decode('utf-8'),
                public_pem.decode('utf-8')
            )
            
            # Register default client for testing
            await self._register_default_client()
            
            logger.info("OAuth Core initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OAuth Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start OAuth system"""
        try:
            logger.info("OAuth Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start OAuth Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop OAuth system"""
        try:
            logger.info("OAuth Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop OAuth Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Verify JWT handler is working
            if not self.jwt_handler:
                return False
            
            # Test token creation and verification
            test_payload = {"sub": "test", "exp": int(time.time()) + 3600}
            test_token = self.jwt_handler.create_access_token(test_payload)
            is_valid = self.jwt_handler.verify_token(test_token)
            
            return is_valid
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def _initialize_default_scopes(self):
        """Initialize default OAuth scopes"""
        self.scopes = {
            "read": OAuthScope("read", "Read access to basic resources", "api", ["read"]),
            "write": OAuthScope("write", "Write access to resources", "api", ["write"]),
            "admin": OAuthScope("admin", "Administrative access", "api", ["read", "write", "admin"], sensitive=True),
            "profile": OAuthScope("profile", "Access to user profile", "user", ["read"]),
            "email": OAuthScope("email", "Access to user email", "user", ["read"]),
            "openid": OAuthScope("openid", "OpenID Connect authentication", "identity", ["auth"]),
            "offline_access": OAuthScope("offline_access", "Refresh token access", "token", ["refresh"])
        }
    
    async def _register_default_client(self):
        """Register default OAuth client"""
        client = OAuthClient(
            client_id="ainflue_web_app",
            client_secret=secrets.token_urlsafe(32),
            client_type=ClientType.CONFIDENTIAL,
            redirect_uris=["https://app.ainflue.com/auth/callback"],
            scopes=list(self.scopes.keys()),
            grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
            response_types=[ResponseType.CODE],
            name="Ainflue Web Application",
            description="Main web application for Ainflue platform",
            trusted=True
        )
        await self.client_store.register_client(client)
        self.metrics['client_registrations'] += 1
    
    async def register_client(self, client_data: Dict[str, Any]) -> OAuthClient:
        """Register new OAuth client"""
        try:
            client = OAuthClient(
                client_id=client_data.get('client_id', f"client_{uuid.uuid4().hex[:16]}"),
                client_secret=secrets.token_urlsafe(32),
                client_type=ClientType(client_data.get('client_type', ClientType.CONFIDENTIAL.value)),
                redirect_uris=client_data.get('redirect_uris', []),
                scopes=client_data.get('scopes', self.default_scope),
                grant_types=[GrantType(gt) for gt in client_data.get('grant_types', [GrantType.AUTHORIZATION_CODE.value])],
                response_types=[ResponseType(rt) for rt in client_data.get('response_types', [ResponseType.CODE.value])],
                name=client_data.get('name', ''),
                description=client_data.get('description', ''),
                logo_uri=client_data.get('logo_uri'),
                policy_uri=client_data.get('policy_uri'),
                tos_uri=client_data.get('tos_uri')
            )
            
            success = await self.client_store.register_client(client)
            if success:
                self.metrics['client_registrations'] += 1
                logger.info(f"Registered OAuth client: {client.client_id}")
                return client
            else:
                raise Exception("Failed to store client")
                
        except Exception as e:
            logger.error(f"Client registration failed: {str(e)}")
            raise
    
    async def authorize(self, client_id: str, redirect_uri: str, response_type: str,
                       scope: str, state: Optional[str] = None, 
                       code_challenge: Optional[str] = None,
                       code_challenge_method: Optional[str] = None,
                       user_id: Optional[str] = None) -> str:
        """Handle authorization request"""
        try:
            # Validate client
            client = await self.client_store.get_client(client_id)
            if not client or not client.active:
                raise Exception("Invalid client")
            
            # Validate redirect URI
            if redirect_uri not in client.redirect_uris:
                raise Exception("Invalid redirect URI")
            
            # Validate response type
            if ResponseType(response_type) not in client.response_types:
                raise Exception("Invalid response type")
            
            # Validate scopes
            requested_scopes = scope.split() if scope else self.default_scope
            for scope_name in requested_scopes:
                if scope_name not in self.scopes:
                    raise Exception(f"Invalid scope: {scope_name}")
                if scope_name not in client.scopes:
                    raise Exception(f"Scope not allowed for client: {scope_name}")
            
            # Generate authorization code
            auth_code = AuthorizationCode(
                code=secrets.token_urlsafe(32),
                client_id=client_id,
                user_id=user_id or "anonymous",
                redirect_uri=redirect_uri,
                scopes=requested_scopes,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method
            )
            
            await self.token_store.store_authorization_code(auth_code)
            self.metrics['authorization_codes_issued'] += 1
            
            # Build redirect URL
            params = {
                'code': auth_code.code,
                'state': state
            }
            
            query_string = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            redirect_url = f"{redirect_uri}?{query_string}"
            
            logger.info(f"Authorization granted for client {client_id}")
            return redirect_url
            
        except Exception as e:
            logger.error(f"Authorization failed: {str(e)}")
            raise
    
    async def token(self, grant_type: str, **kwargs) -> Dict[str, Any]:
        """Handle token request"""
        try:
            if grant_type == GrantType.AUTHORIZATION_CODE.value:
                return await self._handle_authorization_code_grant(**kwargs)
            elif grant_type == GrantType.REFRESH_TOKEN.value:
                return await self._handle_refresh_token_grant(**kwargs)
            elif grant_type == GrantType.CLIENT_CREDENTIALS.value:
                return await self._handle_client_credentials_grant(**kwargs)
            else:
                raise Exception(f"Unsupported grant type: {grant_type}")
                
        except Exception as e:
            logger.error(f"Token request failed: {str(e)}")
            raise
    
    async def _handle_authorization_code_grant(self, client_id: str, client_secret: str,
                                             code: str, redirect_uri: str,
                                             code_verifier: Optional[str] = None) -> Dict[str, Any]:
        """Handle authorization code grant"""
        # Validate client
        client = await self.client_store.get_client(client_id)
        if not client or client.client_secret != client_secret:
            raise Exception("Invalid client credentials")
        
        # Get authorization code
        auth_code = await self.token_store.get_authorization_code(code)
        if not auth_code or auth_code.client_id != client_id:
            raise Exception("Invalid authorization code")
        
        # Validate redirect URI
        if auth_code.redirect_uri != redirect_uri:
            raise Exception("Invalid redirect URI")
        
        # Validate PKCE if used
        if auth_code.code_challenge and code_verifier:
            if not PKCEHandler.verify_code_challenge(
                code_verifier, auth_code.code_challenge, auth_code.code_challenge_method or "S256"
            ):
                raise Exception("Invalid code verifier")
        
        # Mark code as used
        await self.token_store.use_authorization_code(code)
        
        # Generate tokens
        access_token_data = await self._create_access_token(
            client_id, auth_code.user_id, auth_code.scopes
        )
        
        refresh_token_data = await self._create_refresh_token(
            client_id, auth_code.user_id, auth_code.scopes
        )
        
        response = {
            "access_token": access_token_data.token,
            "token_type": access_token_data.token_type.value,
            "expires_in": int((access_token_data.expires_at - datetime.utcnow()).total_seconds()),
            "refresh_token": refresh_token_data.token,
            "scope": " ".join(access_token_data.scopes)
        }
        
        # Add ID token for OpenID Connect
        if "openid" in auth_code.scopes:
            id_token = await self._create_id_token(client_id, auth_code.user_id, auth_code.scopes)
            response["id_token"] = id_token.token
        
        self.metrics['tokens_issued'] += 1
        return response
    
    async def _handle_refresh_token_grant(self, client_id: str, client_secret: str,
                                        refresh_token: str) -> Dict[str, Any]:
        """Handle refresh token grant"""
        # Validate client
        client = await self.client_store.get_client(client_id)
        if not client or client.client_secret != client_secret:
            raise Exception("Invalid client credentials")
        
        # Get refresh token
        refresh_token_data = await self.token_store.get_refresh_token(refresh_token)
        if not refresh_token_data or refresh_token_data.client_id != client_id:
            raise Exception("Invalid refresh token")
        
        # Generate new access token
        access_token_data = await self._create_access_token(
            client_id, refresh_token_data.user_id, refresh_token_data.scopes
        )
        
        response = {
            "access_token": access_token_data.token,
            "token_type": access_token_data.token_type.value,
            "expires_in": int((access_token_data.expires_at - datetime.utcnow()).total_seconds()),
            "scope": " ".join(access_token_data.scopes)
        }
        
        self.metrics['tokens_issued'] += 1
        return response
    
    async def _handle_client_credentials_grant(self, client_id: str, client_secret: str,
                                             scope: Optional[str] = None) -> Dict[str, Any]:
        """Handle client credentials grant"""
        # Validate client
        client = await self.client_store.get_client(client_id)
        if not client or client.client_secret != client_secret:
            raise Exception("Invalid client credentials")
        
        # Validate grant type allowed
        if GrantType.CLIENT_CREDENTIALS not in client.grant_types:
            raise Exception("Grant type not allowed for client")
        
        # Parse scopes
        requested_scopes = scope.split() if scope else self.default_scope
        for scope_name in requested_scopes:
            if scope_name not in client.scopes:
                raise Exception(f"Scope not allowed for client: {scope_name}")
        
        # Generate access token
        access_token_data = await self._create_access_token(client_id, None, requested_scopes)
        
        response = {
            "access_token": access_token_data.token,
            "token_type": access_token_data.token_type.value,
            "expires_in": int((access_token_data.expires_at - datetime.utcnow()).total_seconds()),
            "scope": " ".join(access_token_data.scopes)
        }
        
        self.metrics['tokens_issued'] += 1
        return response
    
    async def _create_access_token(self, client_id: str, user_id: Optional[str], 
                                 scopes: List[str]) -> AccessToken:
        """Create access token"""
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=1)
        
        payload = {
            "iss": self.issuer,
            "sub": user_id or client_id,
            "aud": [client_id],
            "exp": int(expires_at.timestamp()),
            "iat": int(now.timestamp()),
            "scope": " ".join(scopes),
            "client_id": client_id
        }
        
        if user_id:
            payload["user_id"] = user_id
        
        token = self.jwt_handler.create_access_token(payload)
        
        access_token = AccessToken(
            token=token,
            client_id=client_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=expires_at,
            issuer=self.issuer,
            audience=[client_id],
            subject=user_id or client_id
        )
        
        await self.token_store.store_access_token(access_token)
        return access_token
    
    async def _create_refresh_token(self, client_id: str, user_id: Optional[str],
                                  scopes: List[str]) -> RefreshToken:
        """Create refresh token"""
        token = secrets.token_urlsafe(32)
        
        refresh_token = RefreshToken(
            token=token,
            client_id=client_id,
            user_id=user_id,
            scopes=scopes
        )
        
        await self.token_store.store_refresh_token(refresh_token)
        return refresh_token
    
    async def _create_id_token(self, client_id: str, user_id: str, scopes: List[str]) -> IDToken:
        """Create OpenID Connect ID token"""
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=1)
        
        payload = {
            "iss": self.issuer,
            "sub": user_id,
            "aud": [client_id],
            "exp": int(expires_at.timestamp()),
            "iat": int(now.timestamp()),
            "auth_time": int(now.timestamp())
        }
        
        # Add claims based on scopes
        if "profile" in scopes:
            payload.update({
                "name": f"User {user_id}",
                "preferred_username": user_id
            })
        
        if "email" in scopes:
            payload.update({
                "email": f"{user_id}@example.com",
                "email_verified": True
            })
        
        token = self.jwt_handler.create_id_token(payload)
        
        return IDToken(
            token=token,
            issuer=self.issuer,
            subject=user_id,
            audience=[client_id],
            expires_at=expires_at,
            issued_at=now,
            claims=payload
        )
    
    async def introspect_token(self, token: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Introspect access token"""
        try:
            # Validate client
            client = await self.client_store.get_client(client_id)
            if not client or client.client_secret != client_secret:
                return {"active": False}
            
            # Get token
            access_token = await self.token_store.get_access_token(token)
            if not access_token or access_token.status != TokenStatus.ACTIVE:
                return {"active": False}
            
            return {
                "active": True,
                "client_id": access_token.client_id,
                "user_id": access_token.user_id,
                "scope": " ".join(access_token.scopes),
                "exp": int(access_token.expires_at.timestamp()),
                "iat": int(access_token.issued_at.timestamp()),
                "sub": access_token.subject,
                "aud": access_token.audience,
                "iss": access_token.issuer,
                "token_type": access_token.token_type.value
            }
            
        except Exception as e:
            logger.error(f"Token introspection failed: {str(e)}")
            return {"active": False}
    
    async def revoke_token(self, token: str, client_id: str, client_secret: str) -> bool:
        """Revoke access or refresh token"""
        try:
            # Validate client
            client = await self.client_store.get_client(client_id)
            if not client or client.client_secret != client_secret:
                return False
            
            # Try to revoke as access token
            success = await self.token_store.revoke_access_token(token)
            if not success:
                # Try to revoke as refresh token
                success = await self.token_store.revoke_refresh_token(token)
            
            if success:
                self.metrics['tokens_revoked'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Token revocation failed: {str(e)}")
            return False
    
    def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set"""
        # In a real implementation, this would return the public keys
        # For now, return a placeholder
        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "alg": "RS256",
                    "kid": "oauth-key-1"
                }
            ]
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            'level': self.level,
            'issuer': self.issuer,
            'tokens_issued': self.metrics['tokens_issued'],
            'tokens_revoked': self.metrics['tokens_revoked'],
            'authorization_codes_issued': self.metrics['authorization_codes_issued'],
            'client_registrations': self.metrics['client_registrations'],
            'supported_grant_types': [gt.value for gt in GrantType],
            'supported_response_types': [rt.value for rt in ResponseType],
            'supported_scopes': list(self.scopes.keys()),
            'endpoints': {
                'authorization': self.authorization_endpoint,
                'token': self.token_endpoint,
                'jwks': self.jwks_endpoint,
                'userinfo': self.userinfo_endpoint,
                'introspection': self.introspection_endpoint,
                'revocation': self.revocation_endpoint
            }
        }

# Global instance
oauth_core = OAuthCore()

# Convenience functions
async def register_oauth_client(client_data: Dict[str, Any]) -> OAuthClient:
    """Register OAuth client"""
    return await oauth_core.register_client(client_data)

async def authorize_request(client_id: str, redirect_uri: str, response_type: str,
                          scope: str, user_id: str, state: Optional[str] = None) -> str:
    """Handle authorization request"""
    return await oauth_core.authorize(client_id, redirect_uri, response_type, scope, state, user_id=user_id)

async def token_request(grant_type: str, **kwargs) -> Dict[str, Any]:
    """Handle token request"""
    return await oauth_core.token(grant_type, **kwargs)

# Module exports
__all__ = [
    "OAuthCore", "OAuthClient", "AccessToken", "RefreshToken", "AuthorizationCode",
    "IDToken", "OAuthScope", "TokenStore", "ClientStore", "JWTHandler", "PKCEHandler",
    "GrantType", "TokenType", "ResponseType", "ClientType", "TokenStatus",
    "oauth_core", "register_oauth_client", "authorize_request", "token_request"
]

logger.info("OAuth Core module loaded")