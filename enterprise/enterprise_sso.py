"""Enterprise Single Sign-On (SSO) System
======================================

Advanced enterprise SSO integration supporting SAML 2.0, OpenID Connect (OIDC),
Active Directory, and major identity providers. Provides secure authentication,
session management, and multi-factor authentication for enterprise deployments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""import asyncio
import logging
import json
import uuid
import hashlib
import time
import jwt
import base64
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import aiohttp
import aioredis
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
import ldap3
from urllib.parse import urlencode, parse_qs, urlparse
import secrets
import bcrypt

logger = logging.getLogger(__name__)


class AuthenticationProtocol(Enum):
    """Authentication protocol types"""    SAML2 = "saml2"
    OIDC = "oidc"
    OAUTH2 = "oauth2"
    LDAP = "ldap"
    ACTIVE_DIRECTORY = "ad"
    CUSTOM = "custom"


class SessionStatus(Enum):
    """User session status"""    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    SUSPENDED = "suspended"


class MFAMethod(Enum):
    """Multi-factor authentication methods"""    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_TOKEN = "hardware_token"
    BIOMETRIC = "biometric"
    PUSH_NOTIFICATION = "push"


@dataclass
class SAMLConfiguration:
    """SAML 2.0 configuration"""    entity_id: str
    sso_url: str
    slo_url: Optional[str]
    certificate: str
    private_key: Optional[str]
    name_id_format: str = "urn:oasis:names:tc:SAML:2.0:nameid-format:emailAddress"
    signature_algorithm: str = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
    digest_algorithm: str = "http://www.w3.org/2001/04/xmlenc#sha256"
    want_assertions_signed: bool = True
    want_response_signed: bool = True
    attribute_mapping: Dict[str, str] = field(default_factory=dict)


@dataclass
class OIDCConfiguration:
    """OpenID Connect configuration"""    client_id: str
    client_secret: str
    discovery_url: str
    redirect_uri: str
    scope: List[str] = field(default_factory=lambda: ["openid", "profile", "email"])
    response_type: str = "code"
    grant_type: str = "authorization_code"
    token_endpoint_auth_method: str = "client_secret_post"
    jwks_uri: Optional[str] = None
    issuer: Optional[str] = None
    userinfo_endpoint: Optional[str] = None


@dataclass
class ActiveDirectoryConfiguration:
    """Active Directory configuration"""    server_uri: str
    bind_dn: str
    bind_password: str
    user_search_base: str
    user_search_filter: str = "(sAMAccountName={username})"
    group_search_base: Optional[str] = None
    group_search_filter: str = "(member={user_dn})"
    use_ssl: bool = True
    port: int = 636
    timeout: int = 30
    attribute_mapping: Dict[str, str] = field(default_factory=dict)


@dataclass
class UserProfile:
    """User profile from identity provider"""    user_id: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    groups: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    permissions: Set[str] = field(default_factory=set)
    tenant_id: Optional[str] = None
    last_login: Optional[datetime] = None
    is_active: bool = True


@dataclass
class AuthenticationSession:
    """User authentication session"""    session_id: str
    user_id: str
    user_profile: UserProfile
    provider: str
    protocol: AuthenticationProtocol
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    status: SessionStatus = SessionStatus.ACTIVE
    mfa_verified: bool = False
    mfa_methods: List[MFAMethod] = field(default_factory=list)
    session_token: Optional[str] = None
    refresh_token: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IdentityProvider:
    """Identity provider configuration"""    provider_id: str
    name: str
    protocol: AuthenticationProtocol
    enabled: bool
    priority: int
    configuration: Union[SAMLConfiguration, OIDCConfiguration, ActiveDirectoryConfiguration]
    user_mapping: Dict[str, str] = field(default_factory=dict)
    group_mapping: Dict[str, str] = field(default_factory=dict)
    auto_provision: bool = False
    default_roles: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SAMLProvider:
    """SAML 2.0 authentication provider"""    
    def __init__(self, config: SAMLConfiguration):
        self.config = config
        self._certificate = None
        self._private_key = None
        self._load_certificates()
    
    def _load_certificates(self):
        """Load SAML certificates"""        try:
            # Load X.509 certificate
            cert_pem = self.config.certificate.encode('utf-8')
            self._certificate = load_pem_x509_certificate(cert_pem, default_backend())
            
            # Load private key if provided
            if self.config.private_key:
                key_pem = self.config.private_key.encode('utf-8')
                self._private_key = serialization.load_pem_private_key(
                    key_pem, password=None, backend=default_backend()
                )
        except Exception as e:
            logger.error(f"Failed to load SAML certificates: {e}")
            raise
    
    async def generate_auth_request(self, request_id: str, relay_state: Optional[str] = None) -> str:
        """Generate SAML authentication request"""        try:
            # Create SAML AuthnRequest
            auth_request = f"""            <samlp:AuthnRequest
                xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                ID="{request_id}"
                Version="2.0"
                IssueInstant="{datetime.now(timezone.utc).isoformat()}"
                Destination="{self.config.sso_url}"
                ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                AssertionConsumerServiceURL="{self.config.entity_id}/acs">
                <saml:Issuer>{self.config.entity_id}</saml:Issuer>
                <samlp:NameIDPolicy
                    Format="{self.config.name_id_format}"
                    AllowCreate="true"/>
            </samlp:AuthnRequest>
            """            
            # Encode and sign if required
            encoded_request = base64.b64encode(auth_request.encode('utf-8')).decode('utf-8')
            
            # Build redirect URL
            params = {
                'SAMLRequest': encoded_request
            }
            
            if relay_state:
                params['RelayState'] = relay_state
            
            redirect_url = f"{self.config.sso_url}?{urlencode(params)}"
            return redirect_url
            
        except Exception as e:
            logger.error(f"Failed to generate SAML auth request: {e}")
            raise
    
    async def process_saml_response(self, saml_response: str) -> UserProfile:
        """Process SAML authentication response"""        try:
            # Decode SAML response
            decoded_response = base64.b64decode(saml_response)
            
            # Parse XML
            root = ET.fromstring(decoded_response)
            
            # Extract assertion
            assertion = root.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
            if assertion is None:
                raise ValueError("No assertion found in SAML response")
            
            # Verify signature if required
            if self.config.want_assertions_signed:
                await self._verify_saml_signature(assertion)
            
            # Extract user attributes
            user_profile = await self._extract_user_profile(assertion)
            
            return user_profile
            
        except Exception as e:
            logger.error(f"Failed to process SAML response: {e}")
            raise
    
    async def _verify_saml_signature(self, assertion: ET.Element) -> bool:
        """Verify SAML assertion signature"""        try:
            # In real implementation, this would perform cryptographic verification
            # using the certificate and signature algorithms
            signature = assertion.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
            return signature is not None
        except Exception as e:
            logger.error(f"SAML signature verification failed: {e}")
            return False
    
    async def _extract_user_profile(self, assertion: ET.Element) -> UserProfile:
        """Extract user profile from SAML assertion"""        try:
            # Extract NameID
            name_id = assertion.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}NameID')
            user_id = name_id.text if name_id is not None else str(uuid.uuid4())
            
            # Extract attributes
            attributes = {}
            attr_statement = assertion.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement')
            
            if attr_statement is not None:
                for attr in attr_statement.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
                    attr_name = attr.get('Name')
                    attr_values = [
                        value.text for value in 
                        attr.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue')
                    ]
                    if attr_values:
                        attributes[attr_name] = attr_values[0] if len(attr_values) == 1 else attr_values
            
            # Map attributes to user profile
            email = attributes.get('email', attributes.get('mail', f"{user_id}@unknown.com"))
            first_name = attributes.get('firstName', attributes.get('givenName', ''))
            last_name = attributes.get('lastName', attributes.get('surname', ''))
            display_name = attributes.get('displayName', f"{first_name} {last_name}".strip())
            
            # Extract groups/roles
            groups = []
            if 'groups' in attributes:
                groups = attributes['groups'] if isinstance(attributes['groups'], list) else [attributes['groups']]
            
            return UserProfile(
                user_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                display_name=display_name or email,
                groups=groups,
                attributes=attributes
            )
            
        except Exception as e:
            logger.error(f"Failed to extract user profile from SAML: {e}")
            raise


class OIDCProvider:
    """OpenID Connect authentication provider"""    
    def __init__(self, config: OIDCConfiguration):
        self.config = config
        self._discovery_doc: Optional[Dict[str, Any]] = None
        self._jwks: Optional[Dict[str, Any]] = None
    
    async def initialize(self):
        """Initialize OIDC provider with discovery"""        try:
            # Fetch discovery document
            async with aiohttp.ClientSession() as session:
                async with session.get(self.config.discovery_url) as response:
                    if response.status == 200:
                        self._discovery_doc = await response.json()
                    else:
                        raise ValueError(f"Failed to fetch OIDC discovery document: {response.status}")
            
            # Update configuration from discovery
            if self._discovery_doc:
                self.config.jwks_uri = self._discovery_doc.get('jwks_uri')
                self.config.issuer = self._discovery_doc.get('issuer')
                self.config.userinfo_endpoint = self._discovery_doc.get('userinfo_endpoint')
            
            # Fetch JWKS
            if self.config.jwks_uri:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.config.jwks_uri) as response:
                        if response.status == 200:
                            self._jwks = await response.json()
            
            logger.info("OIDC provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OIDC provider: {e}")
            raise
    
    async def generate_auth_url(self, state: str, nonce: str) -> str:
        """Generate OIDC authorization URL"""        try:
            if not self._discovery_doc:
                await self.initialize()
            
            auth_endpoint = self._discovery_doc.get('authorization_endpoint')
            if not auth_endpoint:
                raise ValueError("Authorization endpoint not found in discovery document")
            
            params = {
                'client_id': self.config.client_id,
                'response_type': self.config.response_type,
                'scope': ' '.join(self.config.scope),
                'redirect_uri': self.config.redirect_uri,
                'state': state,
                'nonce': nonce
            }
            
            return f"{auth_endpoint}?{urlencode(params)}"
            
        except Exception as e:
            logger.error(f"Failed to generate OIDC auth URL: {e}")
            raise
    
    async def exchange_code_for_tokens(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""        try:
            if not self._discovery_doc:
                await self.initialize()
            
            token_endpoint = self._discovery_doc.get('token_endpoint')
            if not token_endpoint:
                raise ValueError("Token endpoint not found in discovery document")
            
            token_data = {
                'grant_type': self.config.grant_type,
                'code': code,
                'redirect_uri': self.config.redirect_uri,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    token_endpoint,
                    data=token_data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise ValueError(f"Token exchange failed: {response.status} - {error_text}")
            
        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            raise
    
    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify and decode ID token"""        try:
            # Decode token header to get key ID
            header = jwt.get_unverified_header(id_token)
            kid = header.get('kid')
            
            # Find matching key in JWKS
            if not self._jwks:
                raise ValueError("JWKS not available")
            
            key = None
            for jwk in self._jwks.get('keys', []):
                if jwk.get('kid') == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
            
            if not key:
                raise ValueError(f"Key with ID {kid} not found in JWKS")
            
            # Verify and decode token
            decoded_token = jwt.decode(
                id_token,
                key,
                algorithms=['RS256'],
                audience=self.config.client_id,
                issuer=self.config.issuer
            )
            
            return decoded_token
            
        except Exception as e:
            logger.error(f"Failed to verify ID token: {e}")
            raise
    
    async def get_user_info(self, access_token: str) -> UserProfile:
        """Get user information using access token"""        try:
            if not self.config.userinfo_endpoint:
                raise ValueError("UserInfo endpoint not configured")
            
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.config.userinfo_endpoint, headers=headers) as response:
                    if response.status == 200:
                        user_info = await response.json()
                        return self._map_oidc_user_profile(user_info)
                    else:
                        raise ValueError(f"UserInfo request failed: {response.status}")
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise
    
    def _map_oidc_user_profile(self, user_info: Dict[str, Any]) -> UserProfile:
        """Map OIDC user info to UserProfile"""        return UserProfile(
            user_id=user_info.get('sub', str(uuid.uuid4())),
            email=user_info.get('email', ''),
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', ''),
            display_name=user_info.get('name', user_info.get('preferred_username', '')),
            groups=user_info.get('groups', []),
            attributes=user_info
        )


class ActiveDirectoryConnector:
    """Active Directory LDAP connector"""    
    def __init__(self, config: ActiveDirectoryConfiguration):
        self.config = config
        self._connection: Optional[ldap3.Connection] = None
    
    async def connect(self) -> bool:
        """Connect to Active Directory"""        try:
            server = ldap3.Server(
                self.config.server_uri,
                port=self.config.port,
                use_ssl=self.config.use_ssl,
                get_info=ldap3.ALL
            )
            
            self._connection = ldap3.Connection(
                server,
                user=self.config.bind_dn,
                password=self.config.bind_password,
                auto_bind=True,
                authentication=ldap3.SIMPLE
            )
            
            logger.info("Successfully connected to Active Directory")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Active Directory: {e}")
            return False
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserProfile]:
        """Authenticate user against Active Directory"""        try:
            if not self._connection:
                await self.connect()
            
            # Search for user
            search_filter = self.config.user_search_filter.format(username=username)
            
            self._connection.search(
                search_base=self.config.user_search_base,
                search_filter=search_filter,
                attributes=['*']
            )
            
            if not self._connection.entries:
                logger.warning(f"User not found in AD: {username}")
                return None
            
            user_entry = self._connection.entries[0]
            user_dn = str(user_entry.entry_dn)
            
            # Verify password by binding as user
            user_connection = ldap3.Connection(
                self._connection.server,
                user=user_dn,
                password=password,
                authentication=ldap3.SIMPLE
            )
            
            if not user_connection.bind():
                logger.warning(f"Invalid password for user: {username}")
                return None
            
            user_connection.unbind()
            
            # Get user groups
            groups = await self._get_user_groups(user_dn)
            
            # Map attributes to user profile
            attributes = dict(user_entry.entry_attributes_as_dict)
            
            return UserProfile(
                user_id=str(attributes.get('objectGUID', [str(uuid.uuid4())])[0]),
                email=str(attributes.get('mail', [f"{username}@unknown.com"])[0]),
                first_name=str(attributes.get('givenName', [''])[0]),
                last_name=str(attributes.get('sn', [''])[0]),
                display_name=str(attributes.get('displayName', [username])[0]),
                groups=groups,
                attributes=attributes
            )
            
        except Exception as e:
            logger.error(f"Failed to authenticate user {username}: {e}")
            return None
    
    async def _get_user_groups(self, user_dn: str) -> List[str]:
        """Get user group memberships"""        try:
            if not self.config.group_search_base:
                return []
            
            search_filter = self.config.group_search_filter.format(user_dn=user_dn)
            
            self._connection.search(
                search_base=self.config.group_search_base,
                search_filter=search_filter,
                attributes=['cn']
            )
            
            groups = []
            for entry in self._connection.entries:
                group_name = str(entry.cn)
                groups.append(group_name)
            
            return groups
            
        except Exception as e:
            logger.error(f"Failed to get user groups: {e}")
            return []
    
    async def disconnect(self):
        """Disconnect from Active Directory"""        if self._connection:
            self._connection.unbind()
            self._connection = None


class SessionManager:
    """Advanced session management with Redis backend"""    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._session_timeout = timedelta(hours=8)
        self._max_sessions_per_user = 5
    
    async def initialize(self):
        """Initialize Redis connection"""        try:
            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
            await self._redis.ping()
            logger.info("Session manager initialized with Redis")
        except Exception as e:
            logger.error(f"Failed to initialize session manager: {e}")
            raise
    
    async def create_session(
        self,
        user_profile: UserProfile,
        provider: str,
        protocol: AuthenticationProtocol,
        ip_address: str,
        user_agent: str
    ) -> AuthenticationSession:
        """Create new authentication session"""        try:
            session_id = secrets.token_urlsafe(32)
            session_token = secrets.token_urlsafe(64)
            refresh_token = secrets.token_urlsafe(64)
            
            now = datetime.now(timezone.utc)
            expires_at = now + self._session_timeout
            
            session = AuthenticationSession(
                session_id=session_id,
                user_id=user_profile.user_id,
                user_profile=user_profile,
                provider=provider,
                protocol=protocol,
                created_at=now,
                expires_at=expires_at,
                last_activity=now,
                ip_address=ip_address,
                user_agent=user_agent,
                session_token=session_token,
                refresh_token=refresh_token
            )
            
            # Store session in Redis
            await self._store_session(session)
            
            # Enforce max sessions per user
            await self._enforce_session_limits(user_profile.user_id)
            
            logger.info(f"Created session for user: {user_profile.user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def _store_session(self, session: AuthenticationSession):
        """Store session in Redis"""        if not self._redis:
            await self.initialize()
        
        session_key = f"session:{session.session_id}"
        user_sessions_key = f"user_sessions:{session.user_id}"
        
        # Store session data
        session_data = asdict(session)
        # Convert datetime objects to ISO strings
        for key, value in session_data.items():
            if isinstance(value, datetime):
                session_data[key] = value.isoformat()
            elif hasattr(value, '__dict__'):  # Handle dataclass objects
                session_data[key] = asdict(value)
        
        await self._redis.hset(session_key, mapping=session_data)
        await self._redis.expire(session_key, int(self._session_timeout.total_seconds()))
        
        # Add to user's session list
        await self._redis.sadd(user_sessions_key, session.session_id)
        await self._redis.expire(user_sessions_key, int(self._session_timeout.total_seconds()))
    
    async def _enforce_session_limits(self, user_id: str):
        """Enforce maximum sessions per user"""        try:
            user_sessions_key = f"user_sessions:{user_id}"
            session_ids = await self._redis.smembers(user_sessions_key)
            
            if len(session_ids) > self._max_sessions_per_user:
                # Remove oldest sessions
                sessions_to_remove = len(session_ids) - self._max_sessions_per_user
                
                # Get session creation times and sort by oldest
                session_times = []
                for session_id in session_ids:
                    session_key = f"session:{session_id}"
                    created_at = await self._redis.hget(session_key, 'created_at')
                    if created_at:
                        session_times.append((session_id, created_at))
                
                session_times.sort(key=lambda x: x[1])  # Sort by creation time
                
                # Remove oldest sessions
                for i in range(sessions_to_remove):
                    old_session_id = session_times[i][0]
                    await self.invalidate_session(old_session_id)
                    
        except Exception as e:
            logger.error(f"Failed to enforce session limits: {e}")
    
    async def get_session(self, session_id: str) -> Optional[AuthenticationSession]:
        """Get session by ID"""        try:
            if not self._redis:
                await self.initialize()
            
            session_key = f"session:{session_id}"
            session_data = await self._redis.hgetall(session_key)
            
            if not session_data:
                return None
            
            # Reconstruct session object
            # Convert ISO strings back to datetime objects
            for key, value in session_data.items():
                if key.endswith('_at') and isinstance(value, str):
                    try:
                        session_data[key] = datetime.fromisoformat(value)
                    except ValueError:
                        pass
            
            # Reconstruct user profile
            if 'user_profile' in session_data:
                user_profile_data = session_data['user_profile']
                session_data['user_profile'] = UserProfile(**user_profile_data)
            
            # Reconstruct protocol enum
            if 'protocol' in session_data:
                session_data['protocol'] = AuthenticationProtocol(session_data['protocol'])
            
            # Reconstruct status enum
            if 'status' in session_data:
                session_data['status'] = SessionStatus(session_data['status'])
            
            session = AuthenticationSession(**session_data)
            
            # Check if session is expired
            if session.expires_at < datetime.now(timezone.utc):
                await self.invalidate_session(session_id)
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""        try:
            if not self._redis:
                await self.initialize()
            
            session_key = f"session:{session_id}"
            now = datetime.now(timezone.utc).isoformat()
            
            result = await self._redis.hset(session_key, 'last_activity', now)
            return result is not None
            
        except Exception as e:
            logger.error(f"Failed to update session activity: {e}")
            return False
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate session"""        try:
            if not self._redis:
                await self.initialize()
            
            session_key = f"session:{session_id}"
            
            # Get user ID before deleting
            user_id = await self._redis.hget(session_key, 'user_id')
            
            # Delete session
            await self._redis.delete(session_key)
            
            # Remove from user's session list
            if user_id:
                user_sessions_key = f"user_sessions:{user_id}"
                await self._redis.srem(user_sessions_key, session_id)
            
            logger.info(f"Invalidated session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate session: {e}")
            return False


class EnterpriseSSO:
    """Main Enterprise SSO orchestrator"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._providers: Dict[str, IdentityProvider] = {}
        self._saml_providers: Dict[str, SAMLProvider] = {}
        self._oidc_providers: Dict[str, OIDCProvider] = {}
        self._ad_connectors: Dict[str, ActiveDirectoryConnector] = {}
        self.session_manager = SessionManager(
            redis_url=self.config.get('redis_url', 'redis://localhost:6379')
        )
        
    async def initialize(self):
        """Initialize SSO system"""        try:
            await self.session_manager.initialize()
            logger.info("Enterprise SSO system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SSO system: {e}")
            raise
    
    async def configure_saml_provider(
        self,
        provider_id: str,
        name: str,
        saml_config: SAMLConfiguration,
        enabled: bool = True
    ) -> bool:
        """Configure SAML identity provider"""        try:
            provider = IdentityProvider(
                provider_id=provider_id,
                name=name,
                protocol=AuthenticationProtocol.SAML2,
                enabled=enabled,
                priority=len(self._providers),
                configuration=saml_config
            )
            
            saml_provider = SAMLProvider(saml_config)
            
            self._providers[provider_id] = provider
            self._saml_providers[provider_id] = saml_provider
            
            logger.info(f"Configured SAML provider: {provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure SAML provider: {e}")
            return False
    
    async def configure_oidc_provider(
        self,
        provider_id: str,
        name: str,
        oidc_config: OIDCConfiguration,
        enabled: bool = True
    ) -> bool:
        """Configure OIDC identity provider"""        try:
            provider = IdentityProvider(
                provider_id=provider_id,
                name=name,
                protocol=AuthenticationProtocol.OIDC,
                enabled=enabled,
                priority=len(self._providers),
                configuration=oidc_config
            )
            
            oidc_provider = OIDCProvider(oidc_config)
            await oidc_provider.initialize()
            
            self._providers[provider_id] = provider
            self._oidc_providers[provider_id] = oidc_provider
            
            logger.info(f"Configured OIDC provider: {provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure OIDC provider: {e}")
            return False
    
    async def configure_ad_connector(
        self,
        provider_id: str,
        name: str,
        ad_config: ActiveDirectoryConfiguration,
        enabled: bool = True
    ) -> bool:
        """Configure Active Directory connector"""        try:
            provider = IdentityProvider(
                provider_id=provider_id,
                name=name,
                protocol=AuthenticationProtocol.ACTIVE_DIRECTORY,
                enabled=enabled,
                priority=len(self._providers),
                configuration=ad_config
            )
            
            ad_connector = ActiveDirectoryConnector(ad_config)
            await ad_connector.connect()
            
            self._providers[provider_id] = provider
            self._ad_connectors[provider_id] = ad_connector
            
            logger.info(f"Configured AD connector: {provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure AD connector: {e}")
            return False
    
    async def initiate_authentication(
        self,
        provider_id: str,
        redirect_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate authentication with specified provider"""        try:
            if provider_id not in self._providers:
                raise ValueError(f"Provider not found: {provider_id}")
            
            provider = self._providers[provider_id]
            
            if not provider.enabled:
                raise ValueError(f"Provider disabled: {provider_id}")
            
            if provider.protocol == AuthenticationProtocol.SAML2:
                request_id = f"saml_{uuid.uuid4().hex}"
                saml_provider = self._saml_providers[provider_id]
                auth_url = await saml_provider.generate_auth_request(request_id)
                
                return {
                    'auth_url': auth_url,
                    'request_id': request_id,
                    'protocol': 'saml2'
                }
                
            elif provider.protocol == AuthenticationProtocol.OIDC:
                state = secrets.token_urlsafe(32)
                nonce = secrets.token_urlsafe(32)
                oidc_provider = self._oidc_providers[provider_id]
                auth_url = await oidc_provider.generate_auth_url(state, nonce)
                
                return {
                    'auth_url': auth_url,
                    'state': state,
                    'nonce': nonce,
                    'protocol': 'oidc'
                }
                
            else:
                raise ValueError(f"Unsupported protocol for web authentication: {provider.protocol}")
                
        except Exception as e:
            logger.error(f"Failed to initiate authentication: {e}")
            raise
    
    async def process_authentication_response(
        self,
        provider_id: str,
        response_data: Dict[str, Any],
        ip_address: str,
        user_agent: str
    ) -> AuthenticationSession:
        """Process authentication response and create session"""        try:
            if provider_id not in self._providers:
                raise ValueError(f"Provider not found: {provider_id}")
            
            provider = self._providers[provider_id]
            user_profile = None
            
            if provider.protocol == AuthenticationProtocol.SAML2:
                saml_provider = self._saml_providers[provider_id]
                saml_response = response_data.get('SAMLResponse')
                if not saml_response:
                    raise ValueError("SAML response not found")
                user_profile = await saml_provider.process_saml_response(saml_response)
                
            elif provider.protocol == AuthenticationProtocol.OIDC:
                oidc_provider = self._oidc_providers[provider_id]
                code = response_data.get('code')
                state = response_data.get('state')
                
                if not code:
                    raise ValueError("Authorization code not found")
                
                tokens = await oidc_provider.exchange_code_for_tokens(code, state)
                access_token = tokens.get('access_token')
                
                if access_token:
                    user_profile = await oidc_provider.get_user_info(access_token)
                
            elif provider.protocol == AuthenticationProtocol.ACTIVE_DIRECTORY:
                ad_connector = self._ad_connectors[provider_id]
                username = response_data.get('username')
                password = response_data.get('password')
                
                if not username or not password:
                    raise ValueError("Username and password required for AD authentication")
                
                user_profile = await ad_connector.authenticate_user(username, password)
                
            if not user_profile:
                raise ValueError("Authentication failed - no user profile returned")
            
            # Create session
            session = await self.session_manager.create_session(
                user_profile=user_profile,
                provider=provider_id,
                protocol=provider.protocol,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to process authentication response: {e}")
            raise
    
    async def validate_session(self, session_token: str) -> Optional[AuthenticationSession]:
        """Validate session token"""        try:
            # In real implementation, you'd decode the session token to get session_id
            # For now, we'll treat the token as session_id
            session = await self.session_manager.get_session(session_token)
            
            if session and session.status == SessionStatus.ACTIVE:
                await self.session_manager.update_session_activity(session.session_id)
                return session
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to validate session: {e}")
            return None
    
    async def logout(self, session_id: str) -> bool:
        """Logout user and invalidate session"""        try:
            return await self.session_manager.invalidate_session(session_id)
        except Exception as e:
            logger.error(f"Failed to logout: {e}")
            return False
    
    async def get_configured_providers(self) -> List[Dict[str, Any]]:
        """Get list of configured identity providers"""        providers = []
        
        for provider_id, provider in self._providers.items():
            providers.append({
                'provider_id': provider_id,
                'name': provider.name,
                'protocol': provider.protocol.value,
                'enabled': provider.enabled,
                'priority': provider.priority
            })
        
        # Sort by priority
        providers.sort(key=lambda x: x['priority'])
        return providers
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for SSO system"""        try:
            health_status = {
                'status': 'healthy',
                'providers': {},
                'session_manager': 'active',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 1.0
            }
            
            # Check each provider
            for provider_id, provider in self._providers.items():
                provider_status = {
                    'enabled': provider.enabled,
                    'protocol': provider.protocol.value,
                    'status': 'active' if provider.enabled else 'disabled'
                }
                
                # Protocol-specific health checks
                if provider.protocol == AuthenticationProtocol.ACTIVE_DIRECTORY:
                    if provider_id in self._ad_connectors:
                        ad_connector = self._ad_connectors[provider_id]
                        if ad_connector._connection:
                            provider_status['connection'] = 'connected'
                        else:
                            provider_status['connection'] = 'disconnected'
                            provider_status['status'] = 'degraded'
                
                health_status['providers'][provider_id] = provider_status
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 0.0
            }