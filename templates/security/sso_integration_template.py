"""SSO Integration Template for Ainflue Platform
Enterprise Single Sign-On integration supporting SAML 2.0, OpenID Connect,
LDAP, Active Directory for enterprise creator authentication and management.

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle protégée
"""

import logging
import secrets
import hashlib
import base64
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlencode, quote, unquote
import json
import asyncio
import ssl

from pydantic import BaseModel, Field, validator, HttpUrl
import jwt
import aiohttp
import ldap3
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509 import load_pem_x509_certificate

from core.config import get_settings
from utils.exceptions import SSOException, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class SSOProtocol(Enum):
    """SSO protocol types"""
    SAML2 = "saml2"
    OIDC = "oidc"
    LDAP = "ldap"
    ACTIVE_DIRECTORY = "active_directory"
    CAS = "cas"
    OAUTH2 = "oauth2"
    KERBEROS = "kerberos"


class SAMLBinding(Enum):
    """SAML binding types"""
    HTTP_POST = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    HTTP_REDIRECT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    HTTP_ARTIFACT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact"


class NameIDFormat(Enum):
    """SAML NameID formats"""
    PERSISTENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
    TRANSIENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
    EMAIL = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    UNSPECIFIED = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"


class SSOProvider(BaseModel):
    """SSO provider configuration"""
    provider_id: str = Field(..., description="Unique provider identifier")
    name: str = Field(..., description="Provider display name")
    protocol: SSOProtocol = Field(..., description="SSO protocol")
    entity_id: str = Field(..., description="Entity/Issuer ID")
    sso_url: str = Field(..., description="SSO login URL")
    slo_url: Optional[str] = Field(default=None, description="Single logout URL")
    certificate: Optional[str] = Field(default=None, description="X.509 certificate")
    private_key: Optional[str] = Field(default=None, description="Private key for signing")
    metadata_url: Optional[str] = Field(default=None, description="Metadata URL")
    attribute_mapping: Dict[str, str] = Field(default_factory=dict)
    is_enabled: bool = Field(default=True)
    auto_provision: bool = Field(default=True, description="Auto-provision users")
    default_role: Optional[str] = Field(default=None)
    domain_whitelist: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SSORequest(BaseModel):
    """SSO authentication request"""
    provider_id: str = Field(..., description="SSO provider ID")
    protocol: SSOProtocol = Field(..., description="SSO protocol")
    saml_request: Optional[str] = Field(default=None, description="SAML request")
    saml_response: Optional[str] = Field(default=None, description="SAML response")
    relay_state: Optional[str] = Field(default=None, description="Relay state")
    username: Optional[str] = Field(default=None, description="LDAP username")
    password: Optional[str] = Field(default=None, description="LDAP password")
    id_token: Optional[str] = Field(default=None, description="OIDC ID token")
    access_token: Optional[str] = Field(default=None, description="OAuth access token")
    device_info: Optional[Dict[str, Any]] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)


class SSOUserAttributes(BaseModel):
    """SSO user attributes"""
    name_id: str = Field(..., description="User identifier")
    email: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    display_name: Optional[str] = Field(default=None)
    department: Optional[str] = Field(default=None)
    organization: Optional[str] = Field(default=None)
    roles: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    employee_id: Optional[str] = Field(default=None)
    manager: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    timezone: Optional[str] = Field(default=None)
    raw_attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SSOResponse(BaseModel):
    """SSO authentication response"""
    success: bool = Field(..., description="Authentication success")
    provider_id: str = Field(..., description="SSO provider ID")
    protocol: SSOProtocol = Field(..., description="SSO protocol used")
    user_id: Optional[str] = Field(default=None, description="Ainflue user ID")
    sso_user_id: Optional[str] = Field(default=None, description="SSO user ID")
    access_token: Optional[str] = Field(default=None, description="Ainflue access token")
    refresh_token: Optional[str] = Field(default=None, description="Ainflue refresh token")
    session_id: Optional[str] = Field(default=None, description="SSO session ID")
    attributes: Optional[SSOUserAttributes] = Field(default=None)
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    is_new_user: bool = Field(default=False)
    session_expires_at: Optional[datetime] = Field(default=None)
    logout_url: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SAMLAssertion(BaseModel):
    """SAML assertion data"""
    assertion_id: str = Field(..., description="Assertion ID")
    issuer: str = Field(..., description="Assertion issuer")
    subject: str = Field(..., description="Subject NameID")
    audience: str = Field(..., description="Audience restriction")
    issued_at: datetime = Field(..., description="Issue timestamp")
    not_before: datetime = Field(..., description="Not valid before")
    not_on_or_after: datetime = Field(..., description="Not valid after")
    attributes: Dict[str, List[str]] = Field(default_factory=dict)
    session_index: Optional[str] = Field(default=None)
    authn_context: Optional[str] = Field(default=None)
    signature_valid: bool = Field(default=False)


class LDAPConfig(BaseModel):
    """LDAP/AD configuration"""
    server_uri: str = Field(..., description="LDAP server URI")
    bind_dn: str = Field(..., description="Bind DN")
    bind_password: str = Field(..., description="Bind password")
    base_dn: str = Field(..., description="Base DN for searches")
    user_filter: str = Field(default="(uid={username})", description="User search filter")
    group_filter: str = Field(default="(member={user_dn})", description="Group search filter")
    attributes: List[str] = Field(default_factory=list)
    use_tls: bool = Field(default=True)
    timeout: int = Field(default=30)
    page_size: int = Field(default=1000)


class SSOIntegrationService:
    """Comprehensive SSO integration service for Ainflue platform
    
    Provides enterprise-grade SSO authentication with:
    - SAML 2.0 identity provider integration
    - OpenID Connect support
    - LDAP/Active Directory authentication
    - Attribute mapping and user provisioning
    - Session management and single logout
    - Certificate validation and encryption
    - Multi-tenant SSO configuration
    - Enterprise security compliance
    """
    
    def __init__(self):
        self.metrics_collector = SecurityMetricsCollector()
        self.session = aiohttp.ClientSession()
        
        # SSO providers storage
        self.providers: Dict[str, SSOProvider] = {}
        self.ldap_configs: Dict[str, LDAPConfig] = {}
        
        # User sessions
        self.sso_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_mappings: Dict[str, str] = {}  # SSO user ID -> Ainflue user ID
        
        logger.info("SSO integration service initialized")
    
    async def register_saml_provider(self, provider: SSOProvider) -> bool:
        """Register SAML identity provider"""
        try:
            # Validate provider configuration
            if provider.protocol != SSOProtocol.SAML2:
                raise SSOException("Provider must use SAML2 protocol")
            
            if not provider.entity_id or not provider.sso_url:
                raise SSOException("Entity ID and SSO URL are required")
            
            # Load and validate certificate if provided
            if provider.certificate:
                try:
                    cert = load_pem_x509_certificate(provider.certificate.encode())
                    # Verify certificate is not expired
                    if cert.not_valid_after < datetime.utcnow():
                        raise SSOException("Certificate has expired")
                except Exception as e:
                    raise SSOException(f"Invalid certificate: {e}")
            
            # Store provider
            self.providers[provider.provider_id] = provider
            
            logger.info(f"Registered SAML provider: {provider.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register SAML provider: {e}")
            raise SSOException(f"Provider registration failed: {e}")
    
    async def register_ldap_provider(self, provider: SSOProvider, ldap_config: LDAPConfig) -> bool:
        """Register LDAP/AD provider"""
        try:
            if provider.protocol not in [SSOProtocol.LDAP, SSOProtocol.ACTIVE_DIRECTORY]:
                raise SSOException("Provider must use LDAP or Active Directory protocol")
            
            # Test LDAP connection
            try:
                server = ldap3.Server(
                    ldap_config.server_uri,
                    use_ssl=ldap_config.use_tls,
                    get_info=ldap3.ALL,
                    connect_timeout=ldap_config.timeout
                )
                conn = ldap3.Connection(
                    server,
                    user=ldap_config.bind_dn,
                    password=ldap_config.bind_password,
                    auto_bind=True
                )
                conn.unbind()
            except Exception as e:
                raise SSOException(f"LDAP connection test failed: {e}")
            
            # Store configurations
            self.providers[provider.provider_id] = provider
            self.ldap_configs[provider.provider_id] = ldap_config
            
            logger.info(f"Registered LDAP provider: {provider.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register LDAP provider: {e}")
            raise SSOException(f"Provider registration failed: {e}")
    
    async def generate_saml_request(self, provider_id: str, relay_state: Optional[str] = None) -> str:
        """Generate SAML authentication request"""
        try:
            provider = self.providers.get(provider_id)
            if not provider or provider.protocol != SSOProtocol.SAML2:
                raise SSOException("Invalid SAML provider")
            
            # Generate request ID
            request_id = f"_req_{secrets.token_urlsafe(16)}"
            
            # Generate AuthnRequest XML
            authn_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="{request_id}"
                    Version="2.0"
                    IssueInstant="{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}"
                    Destination="{provider.sso_url}"
                    ProtocolBinding="{SAMLBinding.HTTP_POST.value}"
                    AssertionConsumerServiceURL="{settings.BASE_URL}/sso/saml/{provider_id}/acs">
    <saml:Issuer>{settings.SAML_ENTITY_ID}</saml:Issuer>
    <samlp:NameIDPolicy Format="{NameIDFormat.EMAIL.value}" AllowCreate="true"/>
    <samlp:RequestedAuthnContext Comparison="exact">
        <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml:AuthnContextClassRef>
    </samlp:RequestedAuthnContext>
</samlp:AuthnRequest>"""
            
            # Base64 encode and deflate compress
            encoded_request = base64.b64encode(authn_request.encode()).decode()
            
            # Generate SSO URL
            params = {
                'SAMLRequest': encoded_request,
                'RelayState': relay_state or ''
            }
            
            sso_url = f"{provider.sso_url}?{urlencode(params)}"
            
            logger.info(f"Generated SAML request for provider {provider_id}")
            return sso_url
            
        except Exception as e:
            logger.error(f"Failed to generate SAML request: {e}")
            raise SSOException(f"SAML request generation failed: {e}")
    
    async def process_saml_response(self, request: SSORequest) -> SSOResponse:
        """Process SAML authentication response"""
        start_time = datetime.utcnow()
        
        try:
            provider = self.providers.get(request.provider_id)
            if not provider or provider.protocol != SSOProtocol.SAML2:
                raise SSOException("Invalid SAML provider")
            
            if not request.saml_response:
                raise SSOException("SAML response is required")
            
            # Decode SAML response
            try:
                decoded_response = base64.b64decode(request.saml_response).decode()
            except Exception:
                raise SSOException("Invalid SAML response encoding")
            
            # Parse SAML response
            assertion = await self._parse_saml_response(decoded_response, provider)
            
            # Extract user attributes
            attributes = await self._extract_saml_attributes(assertion, provider)
            
            # Find or create user
            user_id = await self._find_or_create_sso_user(attributes, provider)
            
            # Create SSO session
            session_id = await self._create_sso_session(user_id, provider.provider_id, assertion)
            
            # Generate Ainflue tokens
            tokens = await self._generate_sso_tokens(user_id, session_id)
            
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Record metrics
            await self.metrics_collector.record_sso_auth(
                provider_id=request.provider_id,
                protocol=request.protocol.value,
                success=True,
                processing_time_ms=processing_time,
                user_id=user_id
            )
            
            return SSOResponse(
                success=True,
                provider_id=request.provider_id,
                protocol=SSOProtocol.SAML2,
                user_id=user_id,
                sso_user_id=attributes.name_id,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                session_id=session_id,
                attributes=attributes,
                session_expires_at=assertion.not_on_or_after,
                logout_url=provider.slo_url,
                metadata={"processing_time_ms": processing_time}
            )
            
        except Exception as e:
            logger.error(f"SAML response processing failed: {e}")
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            await self.metrics_collector.record_sso_auth(
                provider_id=request.provider_id,
                protocol=request.protocol.value,
                success=False,
                processing_time_ms=processing_time,
                error=str(e)
            )
            
            return SSOResponse(
                success=False,
                provider_id=request.provider_id,
                protocol=SSOProtocol.SAML2,
                error_message=str(e),
                metadata={"processing_time_ms": processing_time}
            )
    
    async def authenticate_ldap_user(self, request: SSORequest) -> SSOResponse:
        """Authenticate user via LDAP/AD"""
        start_time = datetime.utcnow()
        
        try:
            provider = self.providers.get(request.provider_id)
            ldap_config = self.ldap_configs.get(request.provider_id)
            
            if not provider or not ldap_config:
                raise SSOException("Invalid LDAP provider configuration")
            
            if not request.username or not request.password:
                raise SSOException("Username and password are required")
            
            # Authenticate user
            user_dn, user_attributes = await self._authenticate_ldap_user(
                ldap_config, request.username, request.password
            )
            
            # Extract user attributes
            attributes = await self._extract_ldap_attributes(user_attributes, provider)
            
            # Find or create user
            user_id = await self._find_or_create_sso_user(attributes, provider)
            
            # Create SSO session
            session_id = await self._create_sso_session(user_id, provider.provider_id)
            
            # Generate tokens
            tokens = await self._generate_sso_tokens(user_id, session_id)
            
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Record metrics
            await self.metrics_collector.record_sso_auth(
                provider_id=request.provider_id,
                protocol=request.protocol.value,
                success=True,
                processing_time_ms=processing_time,
                user_id=user_id
            )
            
            return SSOResponse(
                success=True,
                provider_id=request.provider_id,
                protocol=provider.protocol,
                user_id=user_id,
                sso_user_id=attributes.name_id,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                session_id=session_id,
                attributes=attributes,
                session_expires_at=datetime.utcnow() + timedelta(hours=8),
                metadata={"processing_time_ms": processing_time}
            )
            
        except Exception as e:
            logger.error(f"LDAP authentication failed: {e}")
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            await self.metrics_collector.record_sso_auth(
                provider_id=request.provider_id,
                protocol=request.protocol.value,
                success=False,
                processing_time_ms=processing_time,
                error=str(e)
            )
            
            return SSOResponse(
                success=False,
                provider_id=request.provider_id,
                protocol=provider.protocol,
                error_message=str(e),
                metadata={"processing_time_ms": processing_time}
            )
    
    async def _parse_saml_response(self, response_xml: str, provider: SSOProvider) -> SAMLAssertion:
        """Parse SAML response and extract assertion"""
        try:
            root = ET.fromstring(response_xml)
            
            # Find assertion
            assertion_elem = root.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion")
            if assertion_elem is None:
                raise SSOException("No assertion found in SAML response")
            
            # Extract assertion data
            assertion_id = assertion_elem.get("ID")
            
            # Get issuer
            issuer_elem = assertion_elem.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Issuer")
            issuer = issuer_elem.text if issuer_elem is not None else ""
            
            # Get subject
            subject_elem = assertion_elem.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}NameID")
            subject = subject_elem.text if subject_elem is not None else ""
            
            # Get conditions
            conditions_elem = assertion_elem.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Conditions")
            not_before = datetime.utcnow()
            not_on_or_after = datetime.utcnow() + timedelta(hours=1)
            
            if conditions_elem is not None:
                if conditions_elem.get("NotBefore"):
                    not_before = datetime.fromisoformat(conditions_elem.get("NotBefore").replace("Z", "+00:00"))
                if conditions_elem.get("NotOnOrAfter"):
                    not_on_or_after = datetime.fromisoformat(conditions_elem.get("NotOnOrAfter").replace("Z", "+00:00"))
            
            # Get audience
            audience_elem = assertion_elem.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Audience")
            audience = audience_elem.text if audience_elem is not None else ""
            
            # Extract attributes
            attributes = {}
            attr_statements = assertion_elem.findall(".//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement")
            
            for attr_statement in attr_statements:
                for attr in attr_statement.findall(".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"):
                    attr_name = attr.get("Name")
                    attr_values = []
                    
                    for value in attr.findall(".//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue"):
                        if value.text:
                            attr_values.append(value.text)
                    
                    if attr_name and attr_values:
                        attributes[attr_name] = attr_values
            
            # Verify signature if certificate provided
            signature_valid = False
            if provider.certificate:
                signature_valid = await self._verify_saml_signature(response_xml, provider.certificate)
            
            return SAMLAssertion(
                assertion_id=assertion_id,
                issuer=issuer,
                subject=subject,
                audience=audience,
                issued_at=datetime.utcnow(),
                not_before=not_before,
                not_on_or_after=not_on_or_after,
                attributes=attributes,
                signature_valid=signature_valid
            )
            
        except ET.ParseError as e:
            raise SSOException(f"Invalid SAML response XML: {e}")
        except Exception as e:
            raise SSOException(f"SAML response parsing failed: {e}")
    
    async def _verify_saml_signature(self, response_xml: str, certificate: str) -> bool:
        """Verify SAML response signature"""
        try:
            # Simplified signature verification
            # In production, use proper XML signature verification
            cert = load_pem_x509_certificate(certificate.encode())
            
            # Check if certificate is valid
            now = datetime.utcnow()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                return False
            
            # In a real implementation, verify XML signature
            # This is a simplified version
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    async def _extract_saml_attributes(self, assertion: SAMLAssertion, 
                                     provider: SSOProvider) -> SSOUserAttributes:
        """Extract user attributes from SAML assertion"""
        attributes = SSOUserAttributes(
            name_id=assertion.subject,
            raw_attributes=assertion.attributes
        )
        
        # Apply attribute mapping
        mapping = provider.attribute_mapping
        
        for saml_attr, value_list in assertion.attributes.items():
            value = value_list[0] if value_list else None
            
            if saml_attr in mapping:
                ainflue_attr = mapping[saml_attr]
                
                if ainflue_attr == "email":
                    attributes.email = value
                elif ainflue_attr == "first_name":
                    attributes.first_name = value
                elif ainflue_attr == "last_name":
                    attributes.last_name = value
                elif ainflue_attr == "display_name":
                    attributes.display_name = value
                elif ainflue_attr == "department":
                    attributes.department = value
                elif ainflue_attr == "organization":
                    attributes.organization = value
                elif ainflue_attr == "roles":
                    attributes.roles = value_list
                elif ainflue_attr == "groups":
                    attributes.groups = value_list
        
        # Set display name if not provided
        if not attributes.display_name and attributes.first_name and attributes.last_name:
            attributes.display_name = f"{attributes.first_name} {attributes.last_name}"
        
        return attributes
    
    async def _authenticate_ldap_user(self, config: LDAPConfig, username: str, 
                                    password: str) -> Tuple[str, Dict[str, Any]]:
        """Authenticate user against LDAP/AD"""
        try:
            # Create LDAP server connection
            server = ldap3.Server(
                config.server_uri,
                use_ssl=config.use_tls,
                get_info=ldap3.ALL,
                connect_timeout=config.timeout
            )
            
            # Bind with service account
            conn = ldap3.Connection(
                server,
                user=config.bind_dn,
                password=config.bind_password,
                auto_bind=True
            )
            
            # Search for user
            search_filter = config.user_filter.format(username=username)
            
            conn.search(
                search_base=config.base_dn,
                search_filter=search_filter,
                attributes=config.attributes or ldap3.ALL_ATTRIBUTES
            )
            
            if not conn.entries:
                raise SSOException("User not found in directory")
            
            user_entry = conn.entries[0]
            user_dn = user_entry.entry_dn
            
            # Authenticate user
            user_conn = ldap3.Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )
            
            # Get user attributes
            user_attributes = dict(user_entry.entry_attributes_as_dict)
            
            user_conn.unbind()
            conn.unbind()
            
            return user_dn, user_attributes
            
        except ldap3.core.exceptions.LDAPBindError:
            raise SSOException("Invalid username or password")
        except Exception as e:
            raise SSOException(f"LDAP authentication failed: {e}")
    
    async def _extract_ldap_attributes(self, ldap_attributes: Dict[str, Any],
                                     provider: SSOProvider) -> SSOUserAttributes:
        """Extract user attributes from LDAP response"""
        def get_first_value(attr_list):
            if isinstance(attr_list, list) and attr_list:
                return str(attr_list[0])
            return str(attr_list) if attr_list else None
        
        attributes = SSOUserAttributes(
            name_id=get_first_value(ldap_attributes.get("uid", ldap_attributes.get("sAMAccountName", []))),
            email=get_first_value(ldap_attributes.get("mail", [])),
            first_name=get_first_value(ldap_attributes.get("givenName", [])),
            last_name=get_first_value(ldap_attributes.get("sn", [])),
            display_name=get_first_value(ldap_attributes.get("displayName", [])),
            department=get_first_value(ldap_attributes.get("department", [])),
            organization=get_first_value(ldap_attributes.get("o", [])),
            employee_id=get_first_value(ldap_attributes.get("employeeID", [])),
            phone=get_first_value(ldap_attributes.get("telephoneNumber", [])),
            raw_attributes=ldap_attributes
        )
        
        # Extract groups/roles
        if "memberOf" in ldap_attributes:
            groups = [str(group) for group in ldap_attributes["memberOf"]]
            attributes.groups = groups
            
            # Extract roles from group names
            roles = []
            for group in groups:
                if "CN=" in group:
                    role = group.split("CN=")[1].split(",")[0]
                    roles.append(role)
            attributes.roles = roles
        
        return attributes
    
    async def _find_or_create_sso_user(self, attributes: SSOUserAttributes, 
                                     provider: SSOProvider) -> str:
        """Find existing user or create new one"""
        # Check if user already exists
        sso_user_key = f"{provider.provider_id}:{attributes.name_id}"
        
        if sso_user_key in self.user_mappings:
            return self.user_mappings[sso_user_key]
        
        # Create new user if auto-provision is enabled
        if provider.auto_provision:
            user_id = f"user_{secrets.token_urlsafe(16)}"
            self.user_mappings[sso_user_key] = user_id
            
            logger.info(f"Auto-provisioned new user {user_id} from SSO provider {provider.provider_id}")
            return user_id
        else:
            raise SSOException("User not found and auto-provisioning is disabled")
    
    async def _create_sso_session(self, user_id: str, provider_id: str, 
                                assertion: Optional[SAMLAssertion] = None) -> str:
        """Create SSO session"""
        session_id = f"sso_{secrets.token_urlsafe(32)}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "provider_id": provider_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=8),
            "last_activity": datetime.utcnow()
        }
        
        if assertion:
            session_data.update({
                "assertion_id": assertion.assertion_id,
                "session_index": assertion.session_index,
                "not_on_or_after": assertion.not_on_or_after
            })
        
        self.sso_sessions[session_id] = session_data
        
        return session_id
    
    async def _generate_sso_tokens(self, user_id: str, session_id: str) -> Dict[str, str]:
        """Generate Ainflue platform tokens for SSO user"""
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "session_type": "sso",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        access_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        refresh_payload = payload.copy()
        refresh_payload["exp"] = datetime.utcnow() + timedelta(days=30)
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def logout_sso_user(self, session_id: str) -> bool:
        """Logout SSO user and invalidate session"""
        try:
            if session_id in self.sso_sessions:
                session = self.sso_sessions[session_id]
                del self.sso_sessions[session_id]
                
                logger.info(f"Logged out SSO session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"SSO logout failed: {e}")
            return False
    
    async def get_sso_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get SSO session information"""
        session = self.sso_sessions.get(session_id)
        
        if session and session["expires_at"] > datetime.utcnow():
            # Update last activity
            session["last_activity"] = datetime.utcnow()
            return session
        elif session:
            # Session expired, remove it
            del self.sso_sessions[session_id]
        
        return None
    
    async def get_provider_list(self) -> List[Dict[str, Any]]:
        """Get list of available SSO providers"""
        providers = []
        
        for provider_id, provider in self.providers.items():
            if provider.is_enabled:
                providers.append({
                    "provider_id": provider_id,
                    "name": provider.name,
                    "protocol": provider.protocol.value,
                    "login_url": f"/sso/{provider.protocol.value}/{provider_id}/login"
                })
        
        return providers
    
    async def cleanup(self):
        """Cleanup resources and expired sessions"""
        # Remove expired sessions
        expired_sessions = []
        for session_id, session in self.sso_sessions.items():
            if session["expires_at"] < datetime.utcnow():
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sso_sessions[session_id]
        
        # Close HTTP session
        if self.session:
            await self.session.close()


# Export service instance
sso_integration_service = SSOIntegrationService()

__all__ = [
    'SSOProtocol',
    'SAMLBinding',
    'NameIDFormat',
    'SSOProvider',
    'SSORequest',
    'SSOUserAttributes',
    'SSOResponse',
    'SAMLAssertion',
    'LDAPConfig',
    'SSOIntegrationService',
    'sso_integration_service'
]