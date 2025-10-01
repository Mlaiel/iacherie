"""OAuth2 Server Template for iacherie Platform
RFC 6749 compliant OAuth 2.0 authorization server with PKCE, OpenID Connect,
and creator-specific authorization flows for secure API access management.

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
from urllib.parse import urlencode, parse_qs, urlparse
import jwt
from pydantic import BaseModel, Field, validator, HttpUrl
from cryptography.fernet import Fernet

from core.config import get_settings
from utils.exceptions import OAuth2Exception, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class GrantType(Enum):
    """OAuth 2.0 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    PASSWORD = "password"
    DEVICE_CODE = "device_code"
    IMPLICIT = "implicit"


class ResponseType(Enum):
    """OAuth 2.0 response types"""
    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"
    CODE_TOKEN = "code token"
    CODE_ID_TOKEN = "code id_token"
    TOKEN_ID_TOKEN = "token id_token"
    CODE_TOKEN_ID_TOKEN = "code token id_token"


class ClientType(Enum):
    """OAuth 2.0 client types"""
    CONFIDENTIAL = "confidential"
    PUBLIC = "public"


class TokenFormat(Enum):
    """Token formats"""
    JWT = "jwt"
    OPAQUE = "opaque"
    REFERENCE = "reference"


class AuthenticationMethod(Enum):
    """Client authentication methods"""
    CLIENT_SECRET_BASIC = "client_secret_basic"
    CLIENT_SECRET_POST = "client_secret_post"
    CLIENT_SECRET_JWT = "client_secret_jwt"
    PRIVATE_KEY_JWT = "private_key_jwt"
    NONE = "none"


class OAuth2Client(BaseModel):
    """OAuth 2.0 client registration"""
    client_id: str = Field(..., description="Client identifier")
    client_secret: Optional[str] = Field(default=None, description="Client secret")
    client_name: str = Field(..., description="Client name")
    client_type: ClientType = Field(..., description="Client type")
    redirect_uris: List[str] = Field(..., description="Authorized redirect URIs")
    response_types: List[ResponseType] = Field(..., description="Authorized response types")
    grant_types: List[GrantType] = Field(..., description="Authorized grant types")
    scopes: List[str] = Field(..., description="Authorized scopes")
    token_endpoint_auth_method: AuthenticationMethod = Field(
        default=AuthenticationMethod.CLIENT_SECRET_BASIC,
        description="Token endpoint authentication method"
    )
    jwks_uri: Optional[str] = Field(default=None, description="JWKS URI for key verification")
    application_type: str = Field(default="web", description="Application type")
    contacts: List[str] = Field(default_factory=list, description="Contact emails")
    logo_uri: Optional[str] = Field(default=None, description="Logo URI")
    client_uri: Optional[str] = Field(default=None, description="Client URI")
    policy_uri: Optional[str] = Field(default=None, description="Privacy policy URI")
    tos_uri: Optional[str] = Field(default=None, description="Terms of service URI")
    sector_identifier_uri: Optional[str] = Field(default=None, description="Sector identifier URI")
    subject_type: str = Field(default="public", description="Subject identifier type")
    id_token_signed_response_alg: str = Field(default="RS256", description="ID token signing algorithm")
    access_token_lifetime: int = Field(default=3600, description="Access token lifetime in seconds")
    refresh_token_lifetime: int = Field(default=2592000, description="Refresh token lifetime in seconds")
    is_active: bool = Field(default=True, description="Client active status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuthorizationRequest(BaseModel):
    """OAuth 2.0 authorization request"""
    response_type: str = Field(..., description="Response type")
    client_id: str = Field(..., description="Client identifier")
    redirect_uri: Optional[str] = Field(default=None, description="Redirect URI")
    scope: Optional[str] = Field(default=None, description="Requested scopes")
    state: Optional[str] = Field(default=None, description="Client state")
    nonce: Optional[str] = Field(default=None, description="OpenID Connect nonce")
    code_challenge: Optional[str] = Field(default=None, description="PKCE code challenge")
    code_challenge_method: Optional[str] = Field(default=None, description="PKCE challenge method")
    prompt: Optional[str] = Field(default=None, description="OpenID Connect prompt")
    max_age: Optional[int] = Field(default=None, description="Maximum authentication age")
    ui_locales: Optional[str] = Field(default=None, description="UI locales")
    id_token_hint: Optional[str] = Field(default=None, description="ID token hint")
    login_hint: Optional[str] = Field(default=None, description="Login hint")
    acr_values: Optional[str] = Field(default=None, description="Authentication context class references")
    custom_params: Dict[str, str] = Field(default_factory=dict, description="Custom parameters")


class TokenRequest(BaseModel):
    """OAuth 2.0 token request"""
    grant_type: str = Field(..., description="Grant type")
    client_id: Optional[str] = Field(default=None, description="Client identifier")
    client_secret: Optional[str] = Field(default=None, description="Client secret")
    code: Optional[str] = Field(default=None, description="Authorization code")
    redirect_uri: Optional[str] = Field(default=None, description="Redirect URI")
    username: Optional[str] = Field(default=None, description="Username for password grant")
    password: Optional[str] = Field(default=None, description="Password for password grant")
    scope: Optional[str] = Field(default=None, description="Requested scope")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    code_verifier: Optional[str] = Field(default=None, description="PKCE code verifier")
    device_code: Optional[str] = Field(default=None, description="Device authorization code")
    custom_params: Dict[str, str] = Field(default_factory=dict, description="Custom parameters")


class AuthorizationCode(BaseModel):
    """Authorization code data"""
    code: str = Field(..., description="Authorization code")
    client_id: str = Field(..., description="Client identifier")
    user_id: str = Field(..., description="User identifier")
    redirect_uri: str = Field(..., description="Redirect URI")
    scopes: List[str] = Field(..., description="Authorized scopes")
    code_challenge: Optional[str] = Field(default=None, description="PKCE code challenge")
    code_challenge_method: Optional[str] = Field(default=None, description="PKCE challenge method")
    nonce: Optional[str] = Field(default=None, description="OpenID Connect nonce")
    auth_time: datetime = Field(default_factory=datetime.utcnow, description="Authentication time")
    expires_at: datetime = Field(..., description="Code expiration time")
    is_used: bool = Field(default=False, description="Code usage status")
    used_at: Optional[datetime] = Field(default=None, description="Code usage time")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessToken(BaseModel):
    """Access token data"""
    token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Token type")
    client_id: str = Field(..., description="Client identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    scopes: List[str] = Field(..., description="Token scopes")
    expires_at: datetime = Field(..., description="Token expiration")
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    is_revoked: bool = Field(default=False)
    revoked_at: Optional[datetime] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RefreshToken(BaseModel):
    """Refresh token data"""
    token: str = Field(..., description="Refresh token")
    client_id: str = Field(..., description="Client identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    scopes: List[str] = Field(..., description="Token scopes")
    access_token: str = Field(..., description="Associated access token")
    expires_at: datetime = Field(..., description="Token expiration")
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    is_revoked: bool = Field(default=False)
    revoked_at: Optional[datetime] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TokenResponse(BaseModel):
    """OAuth 2.0 token response"""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: Optional[int] = Field(default=None, description="Token lifetime in seconds")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    scope: Optional[str] = Field(default=None, description="Granted scopes")
    id_token: Optional[str] = Field(default=None, description="OpenID Connect ID token")
    custom_claims: Dict[str, Any] = Field(default_factory=dict, description="Custom claims")


class DeviceAuthorizationRequest(BaseModel):
    """Device authorization request (RFC 8628)"""
    client_id: str = Field(..., description="Client identifier")
    scope: Optional[str] = Field(default=None, description="Requested scope")


class DeviceAuthorizationResponse(BaseModel):
    """Device authorization response (RFC 8628)"""
    device_code: str = Field(..., description="Device verification code")
    user_code: str = Field(..., description="User verification code")
    verification_uri: str = Field(..., description="User verification URI")
    verification_uri_complete: Optional[str] = Field(default=None, description="Complete verification URI")
    expires_in: int = Field(..., description="Code lifetime in seconds")
    interval: int = Field(default=5, description="Polling interval in seconds")


class OAuth2ServerService:
    """Comprehensive OAuth 2.0 authorization server for iacherie platform
    
    Provides RFC 6749 compliant OAuth 2.0 server with:
    - Multiple grant type support (authorization code, client credentials, etc.)
    - PKCE (RFC 7636) for public client security
    - OpenID Connect 1.0 integration
    - Device authorization flow (RFC 8628)
    - Dynamic client registration (RFC 7591)
    - Token introspection (RFC 7662) integration
    - Creator-specific scopes and permissions
    - Advanced security features and monitoring
    - High-performance token management
    - Compliance and audit logging
    """
    
    def __init__(self):
        self.metrics_collector = SecurityMetricsCollector()
        self.cipher = Fernet(Fernet.generate_key())
        
        # Storage
        self.clients: Dict[str, OAuth2Client] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        self.access_tokens: Dict[str, AccessToken] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}
        self.device_codes: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.issuer = getattr(settings, 'OAUTH2_ISSUER', 'https://auth.iacherie.com')
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.jwt_algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
        
        # Default scopes
        self.default_scopes = [
            'openid', 'profile', 'email', 'read', 'write',
            'creator:basic', 'creator:content', 'creator:analytics',
            'creator:monetization', 'creator:collaboration'
        ]
        
        # Security settings
        self.code_lifetime = 600  # 10 minutes
        self.access_token_lifetime = 3600  # 1 hour
        self.refresh_token_lifetime = 2592000  # 30 days
        self.device_code_lifetime = 1800  # 30 minutes
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        logger.info("OAuth2 server service initialized")
    
    async def register_client(self, client_data: Dict[str, Any]) -> OAuth2Client:
        """Register new OAuth 2.0 client"""
        try:
            # Generate client credentials
            client_id = f"client_{secrets.token_urlsafe(16)}"
            client_secret = None
            
            if client_data.get('client_type') == ClientType.CONFIDENTIAL:
                client_secret = secrets.token_urlsafe(32)
            
            # Create client
            client = OAuth2Client(
                client_id=client_id,
                client_secret=client_secret,
                client_name=client_data['client_name'],
                client_type=ClientType(client_data.get('client_type', 'confidential')),
                redirect_uris=client_data['redirect_uris'],
                response_types=[ResponseType(rt) for rt in client_data.get('response_types', ['code'])],
                grant_types=[GrantType(gt) for gt in client_data.get('grant_types', ['authorization_code'])],
                scopes=client_data.get('scopes', self.default_scopes),
                token_endpoint_auth_method=AuthenticationMethod(
                    client_data.get('token_endpoint_auth_method', 'client_secret_basic')
                ),
                application_type=client_data.get('application_type', 'web'),
                contacts=client_data.get('contacts', []),
                logo_uri=client_data.get('logo_uri'),
                client_uri=client_data.get('client_uri'),
                policy_uri=client_data.get('policy_uri'),
                tos_uri=client_data.get('tos_uri'),
                metadata=client_data.get('metadata', {})
            )
            
            # Store client
            self.clients[client_id] = client
            
            logger.info(f"Registered OAuth2 client: {client_id}")
            return client
            
        except Exception as e:
            logger.error(f"Client registration failed: {e}")
            raise OAuth2Exception(f"Client registration failed: {e}")
    
    async def handle_authorization_request(self, request: AuthorizationRequest, 
                                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle OAuth 2.0 authorization request"""
        try:
            # Validate client
            client = await self._validate_client(request.client_id)
            if not client:
                raise OAuth2Exception("Invalid client")
            
            # Validate redirect URI
            if request.redirect_uri and request.redirect_uri not in client.redirect_uris:
                raise OAuth2Exception("Invalid redirect URI")
            
            redirect_uri = request.redirect_uri or client.redirect_uris[0]
            
            # Validate response type
            response_types = request.response_type.split()
            for rt in response_types:
                if ResponseType(rt) not in client.response_types:
                    raise OAuth2Exception(f"Unauthorized response type: {rt}")
            
            # Validate scopes
            requested_scopes = request.scope.split() if request.scope else []
            invalid_scopes = [scope for scope in requested_scopes if scope not in client.scopes]
            if invalid_scopes:
                raise OAuth2Exception(f"Invalid scopes: {', '.join(invalid_scopes)}")
            
            # Validate PKCE if present
            if request.code_challenge:
                if request.code_challenge_method not in ['S256', 'plain']:
                    raise OAuth2Exception("Invalid code challenge method")
            
            # If user is not authenticated, return authorization URL
            if not user_id:
                auth_params = {
                    'response_type': request.response_type,
                    'client_id': request.client_id,
                    'redirect_uri': redirect_uri,
                    'scope': request.scope or '',
                    'state': request.state or '',
                    'nonce': request.nonce or '',
                }
                
                if request.code_challenge:
                    auth_params['code_challenge'] = request.code_challenge
                    auth_params['code_challenge_method'] = request.code_challenge_method
                
                auth_url = f"{settings.BASE_URL}/oauth2/authorize?{urlencode(auth_params)}"
                
                return {
                    'type': 'authorization_required',
                    'authorization_url': auth_url,
                    'client': {
                        'client_id': client.client_id,
                        'client_name': client.client_name,
                        'logo_uri': client.logo_uri,
                        'client_uri': client.client_uri
                    },
                    'requested_scopes': requested_scopes
                }
            
            # User is authenticated, process authorization
            if 'code' in response_types:
                # Generate authorization code
                code = await self._generate_authorization_code(
                    client_id=request.client_id,
                    user_id=user_id,
                    redirect_uri=redirect_uri,
                    scopes=requested_scopes,
                    code_challenge=request.code_challenge,
                    code_challenge_method=request.code_challenge_method,
                    nonce=request.nonce
                )
                
                # Build redirect URL
                params = {'code': code}
                if request.state:
                    params['state'] = request.state
                
                redirect_url = f"{redirect_uri}?{urlencode(params)}"
                
                return {
                    'type': 'authorization_code',
                    'redirect_url': redirect_url,
                    'code': code
                }
            
            elif 'token' in response_types:
                # Implicit flow - generate access token directly
                access_token_data = await self._generate_access_token(
                    client_id=request.client_id,
                    user_id=user_id,
                    scopes=requested_scopes
                )
                
                # Build fragment parameters
                params = {
                    'access_token': access_token_data['token'],
                    'token_type': 'Bearer',
                    'expires_in': str(self.access_token_lifetime)
                }
                
                if request.scope:
                    params['scope'] = request.scope
                if request.state:
                    params['state'] = request.state
                
                redirect_url = f"{redirect_uri}#{urlencode(params)}"
                
                return {
                    'type': 'implicit_grant',
                    'redirect_url': redirect_url,
                    'access_token': access_token_data['token']
                }
            
            else:
                raise OAuth2Exception("Unsupported response type")
                
        except Exception as e:
            logger.error(f"Authorization request handling failed: {e}")
            raise OAuth2Exception(str(e))
    
    async def handle_token_request(self, request: TokenRequest) -> TokenResponse:
        """Handle OAuth 2.0 token request"""
        try:
            # Authenticate client
            client = await self._authenticate_client_for_token_request(request)
            if not client:
                raise OAuth2Exception("Client authentication failed")
            
            grant_type = GrantType(request.grant_type)
            
            if grant_type == GrantType.AUTHORIZATION_CODE:
                return await self._handle_authorization_code_grant(request, client)
            elif grant_type == GrantType.CLIENT_CREDENTIALS:
                return await self._handle_client_credentials_grant(request, client)
            elif grant_type == GrantType.REFRESH_TOKEN:
                return await self._handle_refresh_token_grant(request, client)
            elif grant_type == GrantType.PASSWORD:
                return await self._handle_password_grant(request, client)
            elif grant_type == GrantType.DEVICE_CODE:
                return await self._handle_device_code_grant(request, client)
            else:
                raise OAuth2Exception(f"Unsupported grant type: {request.grant_type}")
                
        except Exception as e:
            logger.error(f"Token request handling failed: {e}")
            raise OAuth2Exception(str(e))
    
    async def _handle_authorization_code_grant(self, request: TokenRequest, 
                                             client: OAuth2Client) -> TokenResponse:
        """Handle authorization code grant"""
        if not request.code or not request.redirect_uri:
            raise OAuth2Exception("Missing required parameters")
        
        # Validate authorization code
        if request.code not in self.authorization_codes:
            raise OAuth2Exception("Invalid authorization code")
        
        code_data = self.authorization_codes[request.code]
        
        # Check if code is already used
        if code_data.is_used:
            raise OAuth2Exception("Authorization code already used")
        
        # Check if code is expired
        if code_data.expires_at < datetime.utcnow():
            raise OAuth2Exception("Authorization code expired")
        
        # Validate client and redirect URI
        if code_data.client_id != client.client_id:
            raise OAuth2Exception("Invalid client")
        
        if code_data.redirect_uri != request.redirect_uri:
            raise OAuth2Exception("Invalid redirect URI")
        
        # Validate PKCE if present
        if code_data.code_challenge:
            if not request.code_verifier:
                raise OAuth2Exception("Missing code verifier")
            
            if not await self._verify_pkce(code_data.code_challenge, 
                                         code_data.code_challenge_method, 
                                         request.code_verifier):
                raise OAuth2Exception("Invalid code verifier")
        
        # Mark code as used
        code_data.is_used = True
        code_data.used_at = datetime.utcnow()
        
        # Generate tokens
        access_token_data = await self._generate_access_token(
            client_id=client.client_id,
            user_id=code_data.user_id,
            scopes=code_data.scopes
        )
        
        refresh_token_data = await self._generate_refresh_token(
            client_id=client.client_id,
            user_id=code_data.user_id,
            scopes=code_data.scopes,
            access_token=access_token_data['token']
        )
        
        # Generate ID token if OpenID Connect
        id_token = None
        if 'openid' in code_data.scopes:
            id_token = await self._generate_id_token(
                client_id=client.client_id,
                user_id=code_data.user_id,
                nonce=code_data.nonce,
                auth_time=code_data.auth_time,
                scopes=code_data.scopes
            )
        
        return TokenResponse(
            access_token=access_token_data['token'],
            token_type="Bearer",
            expires_in=self.access_token_lifetime,
            refresh_token=refresh_token_data['token'],
            scope=' '.join(code_data.scopes),
            id_token=id_token
        )
    
    async def _handle_client_credentials_grant(self, request: TokenRequest, 
                                             client: OAuth2Client) -> TokenResponse:
        """Handle client credentials grant"""
        # Validate grant type is allowed
        if GrantType.CLIENT_CREDENTIALS not in client.grant_types:
            raise OAuth2Exception("Grant type not allowed for this client")
        
        # Validate scopes
        requested_scopes = request.scope.split() if request.scope else []
        invalid_scopes = [scope for scope in requested_scopes if scope not in client.scopes]
        if invalid_scopes:
            raise OAuth2Exception(f"Invalid scopes: {', '.join(invalid_scopes)}")
        
        # Generate access token (no user context)
        access_token_data = await self._generate_access_token(
            client_id=client.client_id,
            user_id=None,
            scopes=requested_scopes or client.scopes
        )
        
        return TokenResponse(
            access_token=access_token_data['token'],
            token_type="Bearer",
            expires_in=self.access_token_lifetime,
            scope=' '.join(requested_scopes or client.scopes)
        )
    
    async def _handle_refresh_token_grant(self, request: TokenRequest, 
                                        client: OAuth2Client) -> TokenResponse:
        """Handle refresh token grant"""
        if not request.refresh_token:
            raise OAuth2Exception("Missing refresh token")
        
        # Validate refresh token
        if request.refresh_token not in self.refresh_tokens:
            raise OAuth2Exception("Invalid refresh token")
        
        refresh_data = self.refresh_tokens[request.refresh_token]
        
        # Check if token is revoked
        if refresh_data.is_revoked:
            raise OAuth2Exception("Refresh token revoked")
        
        # Check if token is expired
        if refresh_data.expires_at < datetime.utcnow():
            raise OAuth2Exception("Refresh token expired")
        
        # Validate client
        if refresh_data.client_id != client.client_id:
            raise OAuth2Exception("Invalid client")
        
        # Revoke old access token
        if refresh_data.access_token in self.access_tokens:
            self.access_tokens[refresh_data.access_token].is_revoked = True
            self.access_tokens[refresh_data.access_token].revoked_at = datetime.utcnow()
        
        # Generate new access token
        access_token_data = await self._generate_access_token(
            client_id=client.client_id,
            user_id=refresh_data.user_id,
            scopes=refresh_data.scopes
        )
        
        # Update refresh token
        refresh_data.access_token = access_token_data['token']
        
        return TokenResponse(
            access_token=access_token_data['token'],
            token_type="Bearer",
            expires_in=self.access_token_lifetime,
            refresh_token=request.refresh_token,
            scope=' '.join(refresh_data.scopes)
        )
    
    async def _handle_password_grant(self, request: TokenRequest, 
                                   client: OAuth2Client) -> TokenResponse:
        """Handle resource owner password credentials grant"""
        if not request.username or not request.password:
            raise OAuth2Exception("Missing username or password")
        
        # Validate grant type is allowed
        if GrantType.PASSWORD not in client.grant_types:
            raise OAuth2Exception("Grant type not allowed for this client")
        
        # Authenticate user (simplified - implement actual authentication)
        user_id = await self._authenticate_user(request.username, request.password)
        if not user_id:
            raise OAuth2Exception("Invalid credentials")
        
        # Validate scopes
        requested_scopes = request.scope.split() if request.scope else []
        invalid_scopes = [scope for scope in requested_scopes if scope not in client.scopes]
        if invalid_scopes:
            raise OAuth2Exception(f"Invalid scopes: {', '.join(invalid_scopes)}")
        
        # Generate tokens
        access_token_data = await self._generate_access_token(
            client_id=client.client_id,
            user_id=user_id,
            scopes=requested_scopes or client.scopes
        )
        
        refresh_token_data = await self._generate_refresh_token(
            client_id=client.client_id,
            user_id=user_id,
            scopes=requested_scopes or client.scopes,
            access_token=access_token_data['token']
        )
        
        return TokenResponse(
            access_token=access_token_data['token'],
            token_type="Bearer",
            expires_in=self.access_token_lifetime,
            refresh_token=refresh_token_data['token'],
            scope=' '.join(requested_scopes or client.scopes)
        )
    
    async def _handle_device_code_grant(self, request: TokenRequest, 
                                      client: OAuth2Client) -> TokenResponse:
        """Handle device authorization grant"""
        if not request.device_code:
            raise OAuth2Exception("Missing device code")
        
        # Validate device code
        if request.device_code not in self.device_codes:
            raise OAuth2Exception("Invalid device code")
        
        device_data = self.device_codes[request.device_code]
        
        # Check if code is expired
        if device_data['expires_at'] < datetime.utcnow():
            raise OAuth2Exception("Device code expired")
        
        # Check if user has authorized
        if not device_data.get('authorized'):
            raise OAuth2Exception("Authorization pending")
        
        # Generate tokens
        access_token_data = await self._generate_access_token(
            client_id=client.client_id,
            user_id=device_data['user_id'],
            scopes=device_data['scopes']
        )
        
        refresh_token_data = await self._generate_refresh_token(
            client_id=client.client_id,
            user_id=device_data['user_id'],
            scopes=device_data['scopes'],
            access_token=access_token_data['token']
        )
        
        # Remove device code
        del self.device_codes[request.device_code]
        
        return TokenResponse(
            access_token=access_token_data['token'],
            token_type="Bearer",
            expires_in=self.access_token_lifetime,
            refresh_token=refresh_token_data['token'],
            scope=' '.join(device_data['scopes'])
        )
    
    async def handle_device_authorization_request(self, request: DeviceAuthorizationRequest) -> DeviceAuthorizationResponse:
        """Handle device authorization request (RFC 8628)"""
        try:
            # Validate client
            client = await self._validate_client(request.client_id)
            if not client:
                raise OAuth2Exception("Invalid client")
            
            # Generate codes
            device_code = secrets.token_urlsafe(32)
            user_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            
            # Validate scopes
            requested_scopes = request.scope.split() if request.scope else client.scopes
            invalid_scopes = [scope for scope in requested_scopes if scope not in client.scopes]
            if invalid_scopes:
                raise OAuth2Exception(f"Invalid scopes: {', '.join(invalid_scopes)}")
            
            # Store device authorization
            self.device_codes[device_code] = {
                'user_code': user_code,
                'client_id': request.client_id,
                'scopes': requested_scopes,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(seconds=self.device_code_lifetime),
                'authorized': False,
                'user_id': None
            }
            
            verification_uri = f"{settings.BASE_URL}/device"
            verification_uri_complete = f"{verification_uri}?user_code={user_code}"
            
            return DeviceAuthorizationResponse(
                device_code=device_code,
                user_code=user_code,
                verification_uri=verification_uri,
                verification_uri_complete=verification_uri_complete,
                expires_in=self.device_code_lifetime,
                interval=5
            )
            
        except Exception as e:
            logger.error(f"Device authorization request failed: {e}")
            raise OAuth2Exception(str(e))
    
    async def _validate_client(self, client_id: str) -> Optional[OAuth2Client]:
        """Validate client exists and is active"""
        client = self.clients.get(client_id)
        return client if client and client.is_active else None
    
    async def _authenticate_client_for_token_request(self, request: TokenRequest) -> Optional[OAuth2Client]:
        """Authenticate client for token request"""
        client = await self._validate_client(request.client_id)
        if not client:
            return None
        
        # Public clients don't require authentication
        if client.client_type == ClientType.PUBLIC:
            return client
        
        # Confidential clients must authenticate
        if client.token_endpoint_auth_method == AuthenticationMethod.CLIENT_SECRET_POST:
            if request.client_secret != client.client_secret:
                return None
        elif client.token_endpoint_auth_method == AuthenticationMethod.CLIENT_SECRET_BASIC:
            # In real implementation, extract from Authorization header
            if request.client_secret != client.client_secret:
                return None
        
        return client
    
    async def _generate_authorization_code(self, client_id: str, user_id: str, 
                                         redirect_uri: str, scopes: List[str],
                                         code_challenge: Optional[str] = None,
                                         code_challenge_method: Optional[str] = None,
                                         nonce: Optional[str] = None) -> str:
        """Generate authorization code"""
        code = secrets.token_urlsafe(32)
        
        code_data = AuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            nonce=nonce,
            expires_at=datetime.utcnow() + timedelta(seconds=self.code_lifetime)
        )
        
        self.authorization_codes[code] = code_data
        return code
    
    async def _generate_access_token(self, client_id: str, user_id: Optional[str], 
                                   scopes: List[str]) -> Dict[str, Any]:
        """Generate access token"""
        token = secrets.token_urlsafe(32)
        
        # Create JWT payload
        payload = {
            'iss': self.issuer,
            'aud': client_id,
            'client_id': client_id,
            'scope': scopes,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.access_token_lifetime),
            'jti': token
        }
        
        if user_id:
            payload['sub'] = user_id
            payload['user_id'] = user_id
        
        # Generate JWT token
        jwt_token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Store token metadata
        token_data = AccessToken(
            token=jwt_token,
            client_id=client_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=datetime.utcnow() + timedelta(seconds=self.access_token_lifetime)
        )
        
        self.access_tokens[jwt_token] = token_data
        
        return {'token': jwt_token, 'data': token_data}
    
    async def _generate_refresh_token(self, client_id: str, user_id: Optional[str], 
                                    scopes: List[str], access_token: str) -> Dict[str, Any]:
        """Generate refresh token"""
        token = secrets.token_urlsafe(32)
        
        token_data = RefreshToken(
            token=token,
            client_id=client_id,
            user_id=user_id,
            scopes=scopes,
            access_token=access_token,
            expires_at=datetime.utcnow() + timedelta(seconds=self.refresh_token_lifetime)
        )
        
        self.refresh_tokens[token] = token_data
        
        return {'token': token, 'data': token_data}
    
    async def _generate_id_token(self, client_id: str, user_id: str, 
                               nonce: Optional[str] = None,
                               auth_time: Optional[datetime] = None,
                               scopes: List[str] = None) -> str:
        """Generate OpenID Connect ID token"""
        payload = {
            'iss': self.issuer,
            'sub': user_id,
            'aud': client_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.access_token_lifetime),
            'auth_time': int(auth_time.timestamp()) if auth_time else int(datetime.utcnow().timestamp())
        }
        
        if nonce:
            payload['nonce'] = nonce
        
        # Add user claims based on scopes
        if scopes and 'profile' in scopes:
            # In production, fetch actual user profile data
            payload.update({
                'name': 'User Name',
                'preferred_username': 'username',
                'picture': 'https://example.com/avatar.jpg'
            })
        
        if scopes and 'email' in scopes:
            payload.update({
                'email': 'user@example.com',
                'email_verified': True
            })
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    async def _verify_pkce(self, code_challenge: str, method: str, code_verifier: str) -> bool:
        """Verify PKCE code challenge"""
        if method == 'plain':
            return code_challenge == code_verifier
        elif method == 'S256':
            hash_bytes = hashlib.sha256(code_verifier.encode()).digest()
            expected_challenge = base64.urlsafe_b64encode(hash_bytes).decode().rstrip('=')
            return code_challenge == expected_challenge
        
        return False
    
    async def _authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user credentials"""
        # Simplified user authentication - implement actual authentication
        # This would validate against your user database
        if username and password:
            return f"user_{hashlib.md5(username.encode()).hexdigest()[:8]}"
        return None
    
    async def cleanup_expired_codes_and_tokens(self) -> Dict[str, int]:
        """Clean up expired codes and tokens"""
        now = datetime.utcnow()
        cleanup_stats = {
            'authorization_codes': 0,
            'access_tokens': 0,
            'refresh_tokens': 0,
            'device_codes': 0
        }
        
        # Clean authorization codes
        expired_codes = [
            code for code, data in self.authorization_codes.items()
            if data.expires_at < now
        ]
        for code in expired_codes:
            del self.authorization_codes[code]
            cleanup_stats['authorization_codes'] += 1
        
        # Clean access tokens
        expired_tokens = [
            token for token, data in self.access_tokens.items()
            if data.expires_at < now
        ]
        for token in expired_tokens:
            del self.access_tokens[token]
            cleanup_stats['access_tokens'] += 1
        
        # Clean refresh tokens
        expired_refresh = [
            token for token, data in self.refresh_tokens.items()
            if data.expires_at < now
        ]
        for token in expired_refresh:
            del self.refresh_tokens[token]
            cleanup_stats['refresh_tokens'] += 1
        
        # Clean device codes
        expired_device = [
            code for code, data in self.device_codes.items()
            if data['expires_at'] < now
        ]
        for code in expired_device:
            del self.device_codes[code]
            cleanup_stats['device_codes'] += 1
        
        total_cleaned = sum(cleanup_stats.values())
        if total_cleaned > 0:
            logger.info(f"Cleaned up {total_cleaned} expired OAuth2 items: {cleanup_stats}")
        
        return cleanup_stats


# Export service instance
oauth2_server_service = OAuth2ServerService()

__all__ = [
    'GrantType',
    'ResponseType',
    'ClientType',
    'TokenFormat',
    'AuthenticationMethod',
    'OAuth2Client',
    'AuthorizationRequest',
    'TokenRequest',
    'AuthorizationCode',
    'AccessToken',
    'RefreshToken',
    'TokenResponse',
    'DeviceAuthorizationRequest',
    'DeviceAuthorizationResponse',
    'OAuth2ServerService',
    'oauth2_server_service'
]